"""The bridge — does Phi actually respond to the substrate's structure?

The thesis under test: in the time crystal, the *only* thing that can integrate
is the Ising coupling, because the drive flips every spin independently. So Phi
should be high when the drive is deterministic and the coupling survives, and
should collapse when the drive is a coin toss and drowns it.

That prediction can fail, and these tests are where it is put at risk. They also
pin the two ways it could look true without being true: an estimator noise floor
that mimics integration, and a rhythm verdict that cannot legally be compared to
Phi at any size where Phi is computable.
"""

from __future__ import annotations

import random
import statistics

import pytest

from anima_reborn import TimeCrystal
from anima_reborn.iit4 import TransitionMatrix, big_phi
from anima_reborn.substrate import (
    MAX_UNITS,
    binarize,
    crystal_matrix,
    crystal_phi,
    estimate_matrix,
)

SIZE = 4
"""Small enough that a full Phi measurement finishes in a test."""


def phi_at(epsilon: float, *, trials: int = 1600, seed: int = 1) -> float:
    return crystal_phi(
        size=SIZE,
        epsilon=epsilon,
        trials=trials,
        seed=seed,
        with_complex=False,
        with_verdict=False,
    ).phi


def mean_phi(epsilon: float, *, trials: int, seeds: int = 4) -> float:
    return statistics.mean(
        phi_at(epsilon, trials=trials, seed=s) for s in range(seeds)
    )


class TestThePrediction:
    def test_a_deterministic_drive_leaves_the_coupling_integrated(self) -> None:
        """Flip every spin every period, or none of them: either way the drive
        adds no uncertainty, and the Ising coupling's integration shows."""
        assert mean_phi(0.0, trials=1600) > 1.0
        assert mean_phi(1.0, trials=1600) > 1.0

    def test_a_coin_toss_drive_destroys_integration(self) -> None:
        """At epsilon = 0.5 each spin flips or not by a fair coin, so the next
        state carries nothing of the last and there is nothing to integrate."""
        assert mean_phi(0.5, trials=6400) < 0.2

    def test_integration_collapses_at_the_noise_maximum(self) -> None:
        """The whole prediction in one line: the middle is where it dies."""
        assert mean_phi(0.5, trials=1600) < mean_phi(0.05, trials=1600) / 5

    def test_the_response_is_symmetric_about_the_noise_maximum(self) -> None:
        """What matters is how *determined* the drive is, not which way it
        goes — always-flip and never-flip should read alike."""
        always = mean_phi(0.0, trials=1600)
        never = mean_phi(1.0, trials=1600)
        assert always == pytest.approx(never, rel=0.5)

    def test_a_locked_crystal_is_integrated(self) -> None:
        reading = crystal_phi(size=SIZE, epsilon=0.02, trials=1600, seed=1)
        assert reading.is_integrated
        assert reading.phi > 1.0
        assert reading.distinctions > 0


class TestTheNoiseFloor:
    def test_the_residual_at_pure_noise_is_estimator_artefact(self) -> None:
        """The trap this module could most easily fall into.

        At epsilon = 0.5 true Phi is zero, but a *measured* transition matrix is
        a sample, and sampling noise alone produces apparent structure. If that
        floor did not shrink with more trials it would be real integration; it
        does shrink, so it is not. A caller at the default trial count sees
        roughly 0.3 bits of pure artefact.
        """
        coarse = mean_phi(0.5, trials=400)
        fine = mean_phi(0.5, trials=6400)
        assert fine < coarse / 2
        assert fine < 0.2

    def test_real_integration_does_not_shrink_with_more_trials(self) -> None:
        """The control: whatever survives more sampling was not noise."""
        coarse = mean_phi(0.05, trials=400)
        fine = mean_phi(0.05, trials=6400)
        assert fine > 1.0
        assert fine > coarse / 3

    def test_the_signal_clears_the_floor_by_an_order_of_magnitude(self) -> None:
        assert mean_phi(0.05, trials=6400) > 10 * mean_phi(0.5, trials=6400)


class TestWhatCannotBeCompared:
    def test_the_rhythm_verdict_is_unreliable_where_phi_is_computable(self) -> None:
        """A limitation worth pinning in code rather than a footnote.

        The lock thresholds were chosen against a 64-spin ring. Phi is only
        computable up to six units. At four spins the magnetization takes five
        possible values, and the verdict disagrees with the same epsilon at 64 —
        so Phi and the lock cannot be compared at any shared size, and this
        module must not claim they track or dissociate.
        """
        small = TimeCrystal(size=4, epsilon=0.0, seed=1).run(400).verdict
        large = TimeCrystal(size=64, epsilon=0.0, seed=1).run(400).verdict
        assert small != large, (
            "if these ever agree, re-examine whether the comparison is now legal"
        )

    def test_a_reading_still_reports_the_verdict_for_inspection(self) -> None:
        reading = crystal_phi(size=SIZE, epsilon=0.02, trials=400, seed=1)
        assert reading.verdict is not None

    def test_the_verdict_can_be_left_out(self) -> None:
        reading = crystal_phi(
            size=SIZE, epsilon=0.02, trials=400, seed=1, with_verdict=False
        )
        assert reading.verdict is None


class TestOnlyCouplingIntegrates:
    """The structural fact the whole repo turns on.

    Phi measures integration, and integration needs units that read *each
    other*. A process whose next state does not depend on its current state has
    a transition matrix whose rows are all the same, so no partition can destroy
    anything and true Phi is exactly zero — however elaborate the process looks.

    That is the shape of every engine here except the crystal: each unit updates
    from itself and an exogenous drive, and nothing reads anything else. So the
    honest gap between this repo and anything that could be called integrated is
    a coupling, and these tests are what keep that visible.
    """

    @staticmethod
    def memoryless(state: int, rng: random.Random) -> int:
        """Four units driven by a shared source, ignoring the current state.

        A shared cause is not integration: the units correlate without reading
        each other, and Phi is right to call that zero.
        """
        common = rng.random() - 0.5
        out = 0
        for unit in range(4):
            strength = 0.5 if unit < 2 else 0.9
            if (1 - strength) * (rng.random() - 0.5) * 2 + strength * common > 0:
                out |= 1 << unit
        return out

    @staticmethod
    def mean_phi(trials: int, seeds: int = 3) -> float:
        """Averaged over seeds — single runs of this spread far too widely to
        compare (0.23 to 0.71 at 400 trials)."""
        return statistics.mean(
            big_phi(
                estimate_matrix(
                    4, TestOnlyCouplingIntegrates.memoryless, trials=trials, seed=s
                ),
                0b1111,
            ).phi
            for s in range(seeds)
        )

    def test_a_shared_cause_measures_as_no_integration(self) -> None:
        """And it takes a great many trials to see that, which is the trap: at
        the default 400 the estimate reads like real integration.

        Measured: 0.406 at 400 trials, 0.189 at 1600, 0.094 at 8000, 0.051 at
        30000 — halving with each fourfold increase, which is what a sampling
        artefact does and what a real coupling does not.
        """
        coarse = self.mean_phi(400)
        fine = self.mean_phi(8000)
        assert coarse > 0.30, "the artefact clears the bar a coupling would"
        assert fine < 0.15
        assert fine < coarse / 2

    def test_the_crystals_coupling_survives_any_trial_count(self) -> None:
        """The control: the one engine whose spins read their neighbours."""
        coarse = crystal_phi(
            size=SIZE, epsilon=0.02, trials=400, seed=1,
            with_complex=False, with_verdict=False,
        ).phi
        fine = crystal_phi(
            size=SIZE, epsilon=0.02, trials=4000, seed=1,
            with_complex=False, with_verdict=False,
        ).phi
        assert coarse > 1.0
        assert fine > 1.0
        assert fine > coarse / 2


class TestEstimator:
    def test_it_recovers_a_deterministic_process(self) -> None:
        """A process with no randomness must come back exactly, whatever the
        trial count — every sample agrees."""

        def swap(state: int, _rng: object) -> int:
            return (state >> 1 & 1) | (state & 1) << 1

        matrix = estimate_matrix(2, swap, trials=8, seed=1)
        assert matrix.values == (0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0)

    def test_it_converges_on_a_known_probability(self) -> None:
        def coin(_state: int, rng: object) -> int:
            return 1 if rng.random() < 0.25 else 0

        matrix = estimate_matrix(1, coin, trials=20000, seed=1)
        assert matrix.probability(0, 0) == pytest.approx(0.25, abs=0.02)

    def test_a_seed_makes_an_estimate_reproducible(self) -> None:
        first = crystal_matrix(size=3, epsilon=0.1, trials=100, seed=7)
        second = crystal_matrix(size=3, epsilon=0.1, trials=100, seed=7)
        assert first.values == second.values

    def test_the_estimate_is_a_valid_matrix(self) -> None:
        matrix = crystal_matrix(size=3, epsilon=0.1, trials=100, seed=2)
        assert isinstance(matrix, TransitionMatrix)
        assert matrix.n == 3
        assert len(matrix.values) == 8 * 3
        assert all(0.0 <= v <= 1.0 for v in matrix.values)

    def test_it_refuses_a_system_too_big_to_measure(self) -> None:
        with pytest.raises(ValueError, match=f"n must be in \\[1, {MAX_UNITS}\\]"):
            estimate_matrix(MAX_UNITS + 1, lambda s, r: s, trials=1)

    def test_the_crystal_refuses_a_ring_too_big_to_measure(self) -> None:
        with pytest.raises(ValueError, match=f"size must be <= {MAX_UNITS}"):
            crystal_matrix(size=MAX_UNITS + 1)

    def test_it_refuses_a_meaningless_trial_count(self) -> None:
        with pytest.raises(ValueError, match="trials must be >= 1"):
            estimate_matrix(2, lambda s, r: s, trials=0)


class TestBinarize:
    def test_it_packs_one_bit_per_value(self) -> None:
        assert binarize([1.0, -1.0, 1.0]) == 0b101
        assert binarize([-1.0, -1.0]) == 0b00
        assert binarize([]) == 0

    def test_the_threshold_is_the_callers(self) -> None:
        """Which is the point: it decides what counts as ON, and so decides the
        Phi that follows."""
        values = [0.3, 0.7]
        assert binarize(values, threshold=0.0) == 0b11
        assert binarize(values, threshold=0.5) == 0b10
        assert binarize(values, threshold=1.0) == 0b00


class TestReading:
    def test_it_reports_the_maximal_complex(self) -> None:
        reading = crystal_phi(size=SIZE, epsilon=0.02, trials=1600, seed=1)
        assert reading.complex_units != 0
        assert reading.complex_phi > 0.0

    def test_the_complex_search_can_be_skipped(self) -> None:
        reading = crystal_phi(
            size=SIZE, epsilon=0.02, trials=400, seed=1, with_complex=False
        )
        assert reading.complex_units == 0
        assert reading.complex_phi == 0.0

    def test_phi_never_exceeds_the_structure(self) -> None:
        for epsilon in (0.0, 0.05, 0.5, 1.0):
            reading = crystal_phi(
                size=SIZE,
                epsilon=epsilon,
                trials=400,
                seed=1,
                with_complex=False,
                with_verdict=False,
            )
            assert 0.0 <= reading.phi <= reading.total + 1e-12

    def test_phi_is_measured_at_a_state_not_of_a_system(self) -> None:
        """Phi belongs to a system *in a state*; different states can differ."""
        readings = {
            state: crystal_phi(
                size=SIZE,
                epsilon=0.05,
                state=state,
                trials=800,
                seed=1,
                with_complex=False,
                with_verdict=False,
            ).phi
            for state in (0b0000, 0b0101, 0b1111)
        }
        assert len(set(readings.values())) > 1, readings
