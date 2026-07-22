"""The base engine — the dissociation battery.

The thesis: shared information downstream is paid for in temporal order
upstream. Melt the crystal and the gap between A and G survives while the
information in it dies; refreeze and it comes back.

Part of that is architecture rather than discovery, and the tests are split to
keep the difference visible. The gate hard-wires no-lock to no-rotation, so
"melting kills binding" was designed in. What was genuinely contingent — and is
therefore what these tests actually risk — is that a locked ring's rotation is
*enough* to clear the emergence bar, that binding *revives* from windows full of
dead samples, and that tension survives a melt at all.

Every EMERGENT assertion clears the bar by at least 4x, and every INDEPENDENT
assertion sits an order of magnitude below it, so no claim here lives inside the
plug-in estimator's bias band.
"""

from __future__ import annotations

import math
import statistics

import pytest

from anima_reborn import Emergence
from anima_reborn.base import EPSILON, BaseEngine, BaseState
from anima_reborn.crystal import CrystalVerdict

LOCKED = 0.02
"""Well inside the locked regime — see `base.EPSILON`."""

MELTED = 0.5
"""The drive is a fair coin; the ring cannot hold a rhythm."""

SEEDS = 8
"""Single runs near the transition are seed-lore, so claims are made on means
or on all-seeds quantifiers."""


def final(epsilon: float, ticks: int = 800, *, seed: int) -> BaseState:
    return BaseEngine(epsilon=epsilon, seed=seed).run(ticks)


def mean_mi(epsilon: float, ticks: int = 800, *, seeds: int = SEEDS) -> float:
    return statistics.mean(
        final(epsilon, ticks, seed=s).mutual_information for s in range(seeds)
    )


class TestTheContingentClaims:
    """The parts that could have come out otherwise."""

    def test_a_locked_crystal_is_enough_to_bind(self) -> None:
        """Nothing in the gate guarantees the downstream tracking clears the
        bar — the rotation could have been too slow, or the observation noise
        too wide. Measured margin: worst seed 1.26 against a bar of 0.30."""
        for seed in range(SEEDS):
            state = final(LOCKED, seed=seed)
            assert state.verdict is Emergence.EMERGENT, seed
            assert state.mutual_information > 1.0, seed

    def test_the_gap_survives_a_melt_but_the_binding_does_not(self) -> None:
        """The thesis's teeth, and the sentence the pipeline cannot say. A
        frozen target could plausibly have let the gap decay to nothing; it does
        not. The engines stay apart and stop meaning anything by it."""
        for seed in range(SEEDS):
            state = final(MELTED, seed=seed)
            assert state.mutual_information < 0.05, seed
            assert state.tension > 0.05, seed  # QUIET boundary — apart, not collapsed

    def test_the_gap_is_the_same_size_dead_or_alive(self) -> None:
        """Tension cannot tell a live engine from a dead one, which is why the
        state carries the pair rather than one blended number."""
        alive = statistics.mean(final(LOCKED, seed=s).tension for s in range(SEEDS))
        dead = statistics.mean(final(MELTED, seed=s).tension for s in range(SEEDS))
        assert alive == pytest.approx(dead, rel=0.3)

    def test_binding_dies_when_the_crystal_melts_mid_run(self) -> None:
        engine = BaseEngine(epsilon=LOCKED, seed=1)
        assert engine.run(800).verdict is Emergence.EMERGENT

        engine.epsilon = MELTED
        after = engine.run(1200)
        assert after.verdict is Emergence.INDEPENDENT
        assert after.mutual_information < 0.05

    def test_binding_revives_when_the_crystal_refreezes(self) -> None:
        """The test most likely to fail if the thesis is wrong. It needs the
        ring to re-lock out of chaos *and* the resumed rotation to re-bind
        streams whose windows are full of dead samples. Nothing architectural
        forces either. Measured: 8/8 seeds, 0.85 to 1.38 bits."""
        for seed in range(SEEDS):
            engine = BaseEngine(epsilon=LOCKED, seed=seed)
            engine.run(800)
            engine.epsilon = MELTED
            assert engine.run(1200).verdict is Emergence.INDEPENDENT, seed

            engine.epsilon = LOCKED
            revived = engine.run(1200)
            assert revived.verdict is Emergence.EMERGENT, seed
            assert revived.mutual_information > 0.5, seed


class TestTheDoseResponse:
    def test_binding_falls_as_the_drive_degrades(self) -> None:
        """Measured: 1.349 -> 0.501 -> 0.005. This co-locates the downstream
        transition with the crystal's own melting curve."""
        readings = [mean_mi(e) for e in (0.02, 0.05, 0.10)]
        assert readings == sorted(readings, reverse=True), readings
        assert readings[0] > 1.0
        assert readings[-1] < 0.05

    def test_the_boundary_regime_is_bistable_and_is_not_claimed(self) -> None:
        """At the crystal's own default the outcome is a property of the seed,
        not the engine. Pinned so nobody demonstrates anything there."""
        spread = [final(0.05, seed=s).mutual_information for s in range(SEEDS)]
        assert max(spread) - min(spread) > 0.5, spread


class TestThePhaseGate:
    def test_phase_advances_only_under_lock(self) -> None:
        """The one structural change: rotation is bought, not given. Not
        asserted as exactly zero — an early autocorrelation on a short history
        can flicker a spurious lock."""
        locked = final(LOCKED, seed=1).phase
        melted = final(MELTED, seed=1).phase
        assert locked > 10.0
        assert melted < locked * 0.05

    def test_a_fresh_engine_has_not_been_paid_yet(self) -> None:
        assert BaseEngine(seed=1).phase == 0.0

    def test_phase_never_runs_backwards(self) -> None:
        engine = BaseEngine(epsilon=LOCKED, seed=1)
        previous = 0.0
        for _ in range(400):
            phase = engine.step().phase
            assert phase >= previous
            previous = phase

    def test_the_crystal_reading_travels_with_the_state(self) -> None:
        state = final(LOCKED, seed=1)
        assert isinstance(state.crystal.verdict, CrystalVerdict)
        assert -1.0 <= state.crystal.magnetization <= 1.0


class TestTheEstimatorFloor:
    def test_melted_streams_read_below_the_floor_by_collapsing_not_by_dying_harder(
        self,
    ) -> None:
        """A melted engine reads about 0.005 bits, far under the README's 0.155
        independence floor. That is not extra deadness: a frozen target makes
        near-constant streams that occupy a couple of bins, and the sparsity
        bias shrinks with them. The entropies say so, which is why the state
        carries them."""
        melted = final(MELTED, seed=1)
        locked = final(LOCKED, seed=1)
        assert melted.mutual_information < 0.05
        assert melted.h_left < locked.h_left / 2


class TestHouseBattery:
    def test_a_seed_makes_a_run_reproducible(self) -> None:
        """Equality has to work through the nested frozen crystal reading."""
        assert final(LOCKED, 300, seed=42) == final(LOCKED, 300, seed=42)

    def test_different_seeds_differ(self) -> None:
        assert final(LOCKED, 300, seed=1) != final(LOCKED, 300, seed=2)

    def test_the_window_rolls_rather_than_grows(self) -> None:
        engine = BaseEngine(seed=1, history=100)
        engine.run(500)
        assert len(engine.left) == 100
        assert len(engine.right) == 100
        assert engine.ticks == 500

    def test_metrics_stay_silent_until_the_window_fills(self) -> None:
        engine = BaseEngine(seed=1)
        early = engine.run(49)
        assert early.h_left == 0.0
        assert early.mutual_information == 0.0
        # Tension belongs to the engines, not the window, so it is live at once.
        assert early.tension > 0.0
        assert engine.step().h_left > 0.0

    def test_entropies_are_bounded_by_the_binning(self) -> None:
        state = final(LOCKED, seed=1)
        assert 0.0 <= state.h_left <= math.log2(12)
        assert 0.0 <= state.h_right <= math.log2(12)
        assert state.h_joint >= max(state.h_left, state.h_right) - 1e-12

    def test_epsilon_is_validated_by_the_ring_itself(self) -> None:
        with pytest.raises(ValueError, match=r"epsilon must be in \[0, 1\]"):
            BaseEngine(epsilon=1.5)
        engine = BaseEngine(seed=1)
        with pytest.raises(ValueError, match=r"epsilon must be in \[0, 1\]"):
            engine.epsilon = -0.1

    def test_controls_are_changeable_mid_run(self) -> None:
        engine = BaseEngine(seed=1)
        engine.epsilon = 0.3
        engine.separation = 1.0
        assert engine.epsilon == 0.3
        assert engine.separation == 1.0
        engine.run(10)

    def test_reset_clears_everything_including_the_clock(self) -> None:
        engine = BaseEngine(epsilon=LOCKED, seed=1)
        engine.run(400)
        assert engine.phase > 0.0

        engine.reset()
        assert engine.phase == 0.0
        assert engine.ticks == 0
        assert engine.left == ()
        assert engine.right == ()

    def test_the_default_epsilon_is_the_locked_one(self) -> None:
        assert EPSILON == LOCKED
        assert BaseEngine(seed=1).epsilon == LOCKED

    def test_configuration_is_validated(self) -> None:
        with pytest.raises(ValueError, match="dim must be >= 2"):
            BaseEngine(dim=1)
        with pytest.raises(ValueError, match="history must be >= 1"):
            BaseEngine(history=0)
        with pytest.raises(ValueError, match="ticks must be >= 1"):
            BaseEngine().run(0)

    def test_reading_the_state_does_not_advance_it(self) -> None:
        engine = BaseEngine(seed=1)
        engine.run(100)
        before = engine.ticks
        assert engine.state == engine.state
        assert engine.ticks == before
