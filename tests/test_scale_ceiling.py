"""The width-14 collapse was undersampling — pin the MECHANISM, cheaply.

`wide_integration.py` left one question explicitly unverified: is its matched-test collapse at width
14 a real wall or undersampling? `scale_ceiling.py` answered it by measurement — raising the budget
lifts the integrated ring's phi_hat and lowers the reducible bar until they cross at budget 16000.

These tests pin the MECHANISM (the direction each curve moves with the budget), not the crossing
itself: one 16000-budget reading at 14 units costs ~2 minutes, so re-deriving the crossing in the
suite would make it unrunnable. The crossing lives in the script + RESULTS; what is guarded here is
that the ring rises and the artefact falls — if either direction ever flips, the RESULTS conclusion
is void and must be re-measured, not patched.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from anima_reborn.coupled import Wiring

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "scale_ceiling.py"
_spec = importlib.util.spec_from_file_location("scale_ceiling", _PATH)
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)

UNITS = sc.UNITS          # 14


class TestBudgetMechanism:
    def test_the_reducible_artefact_shrinks_with_budget(self) -> None:
        """A null that CANNOT integrate must read closer to zero with more samples — the artefact
        signature. Measured on SELF at a cheap width so the suite stays runnable."""
        lo = sc.pp.reading(Wiring.SELF, units=8, chain=0.0, budget=1000, seed=7)["phi_hat"]
        hi = sc.pp.reading(Wiring.SELF, units=8, chain=0.0, budget=8000, seed=7)["phi_hat"]
        assert hi < lo, (lo, hi)

    def test_the_integrated_ring_does_not_shrink_with_budget(self) -> None:
        """The integrated arm's phi_hat must NOT wash out with samples the way the null does —
        that asymmetry is what makes the budget the right knob."""
        lo = sc.pp.reading(Wiring.PAIRS, units=8, chain=sc.RING_CHAIN, budget=1000, seed=7)["phi_hat"]
        hi = sc.pp.reading(Wiring.PAIRS, units=8, chain=sc.RING_CHAIN, budget=8000, seed=7)["phi_hat"]
        assert hi >= lo * 0.9, (lo, hi)   # holds up (it rose at width 14; here: does not collapse)

    def test_the_floor_falls_only_INSIDE_the_measured_range(self) -> None:
        """The shuffle floor comes down with samples across the measured range (4000 -> 8000) — the
        other half of why the gap closes.

        NON-MONOTONIC BELOW IT, and that is recorded rather than hidden: at width 14 the floor reads
        0.268 at budget 1000 and 0.883 at 4000, i.e. it RISES first. At 1000 draws over 2^14 states
        the floor estimate is itself starved and reads artificially low, so 'the floor falls with
        budget' is true only above that starved regime. RESULTS says so; do not widen this claim.
        """
        lo = sc.pp.reading(Wiring.PAIRS, units=UNITS, chain=sc.RING_CHAIN, budget=4000, seed=7)["floor"]
        hi = sc.pp.reading(Wiring.PAIRS, units=UNITS, chain=sc.RING_CHAIN, budget=8000, seed=7)["floor"]
        assert hi < lo, (lo, hi)

    def test_the_starved_regime_is_real_and_stays_documented(self) -> None:
        """Guard the caveat itself: below the measured range the floor is NOT lower-is-better — it
        reads artificially low. If this ever stops holding, the estimator changed and the RESULTS
        caveat must be re-measured, not deleted."""
        starved = sc.pp.reading(Wiring.PAIRS, units=UNITS, chain=sc.RING_CHAIN, budget=1000, seed=7)["floor"]
        measured = sc.pp.reading(Wiring.PAIRS, units=UNITS, chain=sc.RING_CHAIN, budget=4000, seed=7)["floor"]
        assert starved < measured, (starved, measured)

    def test_conditions_are_declared(self) -> None:
        """The run used 2 seeds where wide_integration used 3; RESULTS says so. If someone raises
        SEEDS without re-running, this catches the doc drifting from the script."""
        assert len(sc.SEEDS) == 2, sc.SEEDS
        assert sc.UNITS == 14 and sc.BUDGETS[-1] == 16000, (sc.UNITS, sc.BUDGETS)
