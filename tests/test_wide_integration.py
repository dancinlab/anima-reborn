"""Where the integration verdict stops being trustworthy — pinned invariants + the artefact guards.

The full sweep and both ceilings live in `state/communication/wide_integration.py` and RESULTS. This
pins the load-bearing, cheap-to-recompute facts:

- FEEDFORWARD is the only STRUCTURAL zero: exact directed Phi 0 and proxy at floor, at every width.
- The exact directed-Phi MAGNITUDE is a WIDTH artefact — a reducible null (SELF) reads a LARGER exact
  Phi at 6 units than a chained ring reads at 4, and its 4-unit value shrinks toward 0 with trials
  (a SAMPLING artefact). Guards: if either ever flips, the docs' artefact note must be revisited
  (`artefact-honesty`) — do not just delete the test.
- The ABSOLUTE separation test FALSE-POSITIVES a reducible null at width 8; the MATCHED test does not,
  while still certifying the integrated ring there. That contrast is the improvement, and it is pinned.

Tests use a small seed set / budget and widths <= 8 to stay fast; the wide-width breakdown is the
script's job, not a unit test's.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from anima_reborn.coupled import Wiring

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "wide_integration.py"
_spec = importlib.util.spec_from_file_location("wide_integration", _PATH)
wi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wi)

SEEDS = (7, 11)      # two seeds keep the proxy calls cheap; determinism pins them
BUDGET = 2000


class TestFeedforwardIsTheStructuralZero:
    def test_exact_feedforward_is_zero_at_4_and_6(self) -> None:
        """directed_big_phi zeros an acyclic cut exactly, at both widths — the only arm it can."""
        assert wi.exact_phi(Wiring.FEEDFORWARD, units=4, chain=0.0) == 0.0
        assert wi.exact_phi(Wiring.FEEDFORWARD, units=6, chain=0.0) == 0.0

    def test_proxy_feedforward_never_separates(self) -> None:
        """FEEDFORWARD sits at its floor (proxy == 0) at every width tested — never a false positive."""
        for units in (4, 6, 8):
            s = wi.arm_summary(Wiring.FEEDFORWARD, 0.0, units=units, budget=BUDGET, seeds=SEEDS)
            assert s["n_separated"] == 0, (units, s)
            assert s["phi_hat"] == 0.0, (units, s)


class TestExactMagnitudeIsAWidthArtefact:
    def test_a_reducible_null_reads_a_large_exact_phi_at_6_units(self) -> None:
        """THE ARTEFACT GUARD: SELF — each unit reads only itself, provably reducible — reads a large
        exact directed Phi at 6 units, LARGER than a chained ring reads at 4. The magnitude tracks
        width, not integration, which is exactly why the decay/separation test is the verdict past a
        few units, never the magnitude. If this ever reads ~0 the estimator changed; revisit the docs,
        do not delete the test."""
        self_6 = wi.exact_phi(Wiring.SELF, units=6, chain=0.0)
        ring_4 = wi.exact_phi(Wiring.PAIRS, units=4, chain=wi.INT_CHAIN)
        assert self_6 > 1.0, self_6                 # the reducible null reads huge at 6
        assert self_6 > ring_4, (self_6, ring_4)    # bigger than a real chained ring at 4

    def test_self_exact_phi_is_small_at_4_units(self) -> None:
        """Same null, narrower: the artefact is width-driven — at 4 units SELF's exact Phi is small."""
        assert wi.exact_phi(Wiring.SELF, units=4, chain=0.0) < 1.0

    def test_the_4_unit_reducible_magnitude_shrinks_with_trials(self) -> None:
        """It is a SAMPLING artefact: SELF's 4-unit exact Phi falls sharply as trials rise (the
        integrated arm's would not). Guards `artefact-honesty` — a nonzero that should be zero must
        be shown to shrink with samples."""
        coarse = wi.exact_phi(Wiring.SELF, units=4, chain=0.0, seed=1, trials=100)
        fine = wi.exact_phi(Wiring.SELF, units=4, chain=0.0, seed=1, trials=1600)
        assert coarse > fine, (coarse, fine)
        assert coarse - fine > 0.1, (coarse, fine)


class TestMatchedTestFixesTheFalsePositive:
    def test_absolute_test_false_positives_a_reducible_null_at_width_8(self) -> None:
        """The documented failure of the ABSOLUTE test: SELF (reducible) reads 'separated' at 8 units.
        Pinned so a silent estimator change that hides it is caught (`artefact-honesty`)."""
        s = wi.arm_summary(Wiring.SELF, 0.0, units=8, budget=BUDGET, seeds=SEEDS)
        assert s["n_separated"] > 0, s

    def test_matched_test_keeps_the_reducible_null_negative_at_width_8(self) -> None:
        """The IMPROVEMENT: against the width-matched reducible ceiling, SELF at 8 is NOT integrated —
        the false positive is removed."""
        m = wi.arm_summary(Wiring.SELF, 0.0, units=8, budget=BUDGET, seeds=SEEDS)["phi_hat"]
        assert wi.matched_integrated(m, units=8, budget=BUDGET, seeds=SEEDS) is False

    def test_matched_test_still_certifies_the_integrated_ring_at_width_8(self) -> None:
        """And it keeps its power: the chained ring clears the width-matched reducible cloud at 8."""
        ci = wi.arm_summary(Wiring.PAIRS, wi.INT_CHAIN, units=8, budget=BUDGET, seeds=SEEDS)["phi_hat"]
        assert wi.matched_integrated(ci, units=8, budget=BUDGET, seeds=SEEDS) is True


class TestFloorGrowsWithWidth:
    def test_the_shuffle_floor_grows_fast_with_width(self) -> None:
        """The absolute magnitude is width-bound: PAIRS chain-0 floor is much larger at 8 than at 4,
        which is why the integrated arm's margin over its own floor decays to nothing by ~12."""
        f4 = wi.arm_summary(Wiring.PAIRS, 0.0, units=4, budget=BUDGET, seeds=SEEDS)["floor"]
        f8 = wi.arm_summary(Wiring.PAIRS, 0.0, units=8, budget=BUDGET, seeds=SEEDS)["floor"]
        assert f8 > 3 * f4, (f4, f8)


class TestReproducible:
    def test_reading_is_deterministic_in_the_seed(self) -> None:
        a = wi.arm_summary(Wiring.PAIRS, wi.INT_CHAIN, units=6, budget=BUDGET, seeds=(7,))
        b = wi.arm_summary(Wiring.PAIRS, wi.INT_CHAIN, units=6, budget=BUDGET, seeds=(7,))
        assert a == b
