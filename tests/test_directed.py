"""Directed cuts — closing the carve-out that could not tell a loop from a chain.

The undirected measure reads a strictly feedforward system at 1.27 bits and does
not shrink with more trials, where IIT 4.0 says zero. Cutting one direction at a
time fixes that. These tests exist to make sure it fixes it *for the right
reason*, because a directed search tries twice as many cuts and so cannot help
returning a smaller number — a lower value proves nothing on its own.

What proves it: the ring stays high through the same code (so the search was
directed, not weakened), and the winning cut on the chain is identifiably the
one pointing at the exogenous unit (so the zero is structural, not numerical).

The battery at the end is the calibration set both delegated reviews converged
on: systems whose integration is known by construction, each of which the
measure must get right before it is trusted anywhere else.
"""

from __future__ import annotations

import math
import random
import statistics

import pytest

from anima_reborn.iit4 import TransitionMatrix, big_phi, directed_big_phi
from anima_reborn.pipeline import PULL, WALK
from anima_reborn.substrate import estimate_matrix

AMPLITUDE = 0.78
GAIN = 3.0
MACRO_STEP = 17
"""The substrate's time constant. Phi is zero at tau = 1 whatever the wiring —
see `state/coupling/RESULTS.md`."""

STATE = 0b0101
TRIALS = 6400

RING = [3, 0, 1, 2]
"""Closed cycle: every unit reads another, influence returns."""
FEEDFORWARD = [None, 0, 1, 2]
"""Unit 0 is exogenous; nothing flows back into it."""
SELF = [0, 1, 2, 3]
"""Each unit reads itself — no coupling at all, the null."""


def wired(sources: list[int | None]):
    def step(state: int, rng: random.Random) -> int:
        x = [AMPLITUDE if state >> i & 1 else -AMPLITUDE for i in range(4)]
        for _ in range(MACRO_STEP):
            nxt = list(x)
            for i, source in enumerate(sources):
                target = (
                    -AMPLITUDE
                    if source is None
                    else -AMPLITUDE * math.tanh(GAIN * x[source] / AMPLITUDE)
                )
                nxt[i] = x[i] + (target - x[i]) * PULL + (rng.random() - 0.5) * WALK
            x = nxt
        return sum(1 << i for i, v in enumerate(x) if v > 0)

    return step


def matrix_for(sources: list[int | None], *, trials: int = TRIALS, seed: int = 0):
    return estimate_matrix(4, wired(sources), trials=trials, seed=seed)


class TestTheCarveOutCloses:
    def test_the_undirected_measure_cannot_see_a_chain_is_reducible(self) -> None:
        """The defect, stated as a test so it stays visible after the fix."""
        readings = [big_phi(matrix_for(FEEDFORWARD, seed=s), STATE).phi for s in range(3)]
        assert min(readings) > 0.5, readings

    def test_the_directed_measure_can(self) -> None:
        for seed in range(3):
            assert directed_big_phi(matrix_for(FEEDFORWARD, seed=seed), STATE).phi == 0.0

    def test_the_zero_points_at_the_exogenous_unit(self) -> None:
        """Not a smaller number — the *right* cut. Unit 0 takes no input from
        the system, so severing everything aimed at it costs nothing, which is
        exactly why the theory calls a feedforward system reducible."""
        measured = directed_big_phi(matrix_for(FEEDFORWARD), STATE)
        assert measured.cut is not None
        assert measured.cut.sink == 0b0001
        assert measured.cut.source == 0b1110

    def test_a_ring_has_no_free_direction(self) -> None:
        """The positive control, and the whole reason the zero above means
        something: the same code, searching the same doubled space, still finds
        no cheap cut when influence returns."""
        for seed in range(3):
            measured = directed_big_phi(matrix_for(RING, seed=seed), STATE)
            assert measured.is_recurrent
            assert measured.phi > 5.0, measured

    def test_directing_the_cut_did_not_weaken_the_search(self) -> None:
        """A directed search tries both directions of every split, so its
        minimum can only fall. What must not happen is the ring falling with
        it."""
        undirected = big_phi(matrix_for(RING), STATE).phi
        directed = directed_big_phi(matrix_for(RING), STATE).phi
        assert directed <= undirected + 1e-12
        assert directed > undirected * 0.5


class TestCalibrationBattery:
    """Systems whose integration is known by construction.

    Both delegated reviews converged on wanting exactly this before the measure
    is trusted anywhere new, and the reasoning is the repo's own: a measure that
    cannot fail on a system with a known answer is not a measure.
    """

    def test_an_identity_network_has_no_integration(self) -> None:
        """Each unit copies itself. Whatever else it does, nothing is shared."""
        readings = [
            directed_big_phi(matrix_for(SELF, seed=s), STATE).phi for s in range(3)
        ]
        assert statistics.mean(readings) < 0.2, readings

    def test_a_shared_cause_is_not_integration(self) -> None:
        """Four units driven by one common source, reading nothing of each
        other. They correlate; they do not integrate."""

        def step(state: int, rng: random.Random) -> int:
            common = rng.random() - 0.5
            return sum(
                1 << i
                for i in range(4)
                if 0.2 * (rng.random() - 0.5) + 0.8 * common > 0
            )

        measured = directed_big_phi(estimate_matrix(4, step, trials=8000, seed=1), STATE)
        assert measured.phi < 0.2

    def test_two_disconnected_pairs_do_not_integrate_as_a_whole(self) -> None:
        """Each pair reads itself into a loop; the pairs never meet. Both halves
        are integrated, the whole is not — and the free cut is the one between
        them."""
        measured = directed_big_phi(matrix_for([1, 0, 3, 2]), 0b0101)
        assert measured.phi < 0.5, measured

    def test_a_closed_loop_does_integrate(self) -> None:
        assert directed_big_phi(matrix_for(RING), STATE).phi > 5.0

    def test_noise_estimates_shrink_with_samples(self) -> None:
        """The artefact discipline, applied to the new measure. A system with
        no coupling must read lower the harder you look."""
        coarse = statistics.mean(
            directed_big_phi(matrix_for(SELF, trials=400, seed=s), STATE).phi
            for s in range(3)
        )
        fine = statistics.mean(
            directed_big_phi(matrix_for(SELF, trials=6400, seed=s), STATE).phi
            for s in range(3)
        )
        assert fine < coarse / 2

    def test_a_real_signal_does_not(self) -> None:
        coarse = directed_big_phi(matrix_for(RING, trials=400), STATE).phi
        fine = directed_big_phi(matrix_for(RING, trials=6400), STATE).phi
        assert fine > coarse * 0.5
        assert fine > 5.0


class TestTheNumberCarriesItsConditions:
    def test_at_one_tick_nothing_integrates_whatever_the_wiring(self) -> None:
        """The timescale sits inside the result. One engine tick moves a unit 6%
        toward its target, so every unit merely copies itself, the matrix
        factorizes, and Phi is exactly zero — for the ring too. Quoting the
        ring's value without its tau is not shorthand, it is a false statement.
        """
        global MACRO_STEP
        original = MACRO_STEP
        try:
            MACRO_STEP = 1
            assert directed_big_phi(matrix_for(RING), STATE).phi == 0.0
            assert big_phi(matrix_for(RING), STATE).phi == 0.0
        finally:
            MACRO_STEP = original

    def test_the_ring_is_back_at_the_measured_value(self) -> None:
        """Guards the restore above, and pins the headline number."""
        assert directed_big_phi(matrix_for(RING), STATE).phi > 5.0


class TestSmallSystems:
    def test_a_single_unit_has_nothing_to_cut(self) -> None:
        measured = directed_big_phi(TransitionMatrix([0.0, 1.0], 1), 0b1)
        assert measured.phi == 0.0
        assert measured.cut is None

    def test_a_coupled_pair_is_recurrent(self) -> None:
        """Each unit becomes the other — influence returns in one step."""
        pair = TransitionMatrix([0, 0, 0, 1, 1, 0, 1, 1], 2)
        assert directed_big_phi(pair, 0b11).is_recurrent

    def test_independent_units_are_not(self) -> None:
        """Each unit becomes itself: two systems sharing a name."""
        pair = TransitionMatrix([0, 0, 1, 0, 0, 1, 1, 1], 2)
        assert directed_big_phi(pair, 0b11).phi == 0.0


def test_the_undirected_goldens_are_untouched() -> None:
    """The hexa parity contract is not what changed here. Closing a carve-out
    means adding a measure beside the old one, never redefining it."""
    coupled = TransitionMatrix([0, 0, 0, 1, 1, 0, 1, 1], 2)
    assert big_phi(coupled, 0b11).phi == 1.9999999994229218
