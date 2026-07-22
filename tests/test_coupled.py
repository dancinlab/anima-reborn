"""The coupled field — integration bought by wiring and nothing else.

Every other engine in this package measures zero integration, because in every
one of them each unit updates from itself and something exogenous. This one
changes exactly one thing: the source a unit flees is a live partner. The claim
is that the change is what produces the integration, and the falsifier ships
with it — the same engine wired feedforward, and wired to itself.

The claim is deliberately narrow. Integration is not experience and Phi is not a
score for anything; the sentence this engine earns is *integration is now
created, and created is all this measures*.
"""

from __future__ import annotations

import math
import statistics

import pytest

from anima_reborn.coupled import (
    AMPLITUDE,
    GAIN,
    MACRO_STEP,
    NAMES,
    UNITS,
    CoupledEngine,
    Wiring,
)
from anima_reborn.pipeline import PULL
from anima_reborn.substrate import (
    RECURRENCE_FLOOR,
    coupled_phi,
    recurrence_evidence,
)

TRIALS = 1600
"""Enough to separate signal from floor without making the suite crawl. The
self-wired null still reads ~0.27 here, which is why recurrence is claimed from
trial scaling and never from one measurement."""


class TestTheClaim:
    def test_the_ring_integrates(self) -> None:
        evidence = recurrence_evidence(Wiring.RING, trials=TRIALS, seed=0)
        assert evidence.is_recurrent, evidence
        assert evidence.fine.directed_phi > 5.0

    def test_the_same_engine_wired_feedforward_does_not(self) -> None:
        """The falsifier. Identical law, identical constants, identical
        measurement — only the wiring differs."""
        for seed in range(3):
            reading = coupled_phi(
                Wiring.FEEDFORWARD, trials=TRIALS, seed=seed, with_complex=False
            )
            assert reading.is_reducible, reading
            assert reading.directed_phi == 0.0

    def test_the_same_engine_wired_to_itself_does_not(self) -> None:
        evidence = recurrence_evidence(Wiring.SELF, trials=TRIALS, seed=0)
        assert not evidence.is_recurrent, evidence
        assert not evidence.held, "the null must collapse with more sampling"

    def test_the_ring_is_one_complex_of_all_four_units(self) -> None:
        reading = coupled_phi(Wiring.RING, trials=TRIALS, seed=0)
        assert reading.complex_units == 0b1111


class TestRecurrenceNeedsEvidence:
    def test_a_single_reading_offers_no_recurrence_verdict(self) -> None:
        """Deliberately absent. A sampled matrix invents structure, so a
        positive Phi from one measurement cannot establish recurrence — the
        self-wired null reads well above zero at any finite trial count."""
        reading = coupled_phi(Wiring.SELF, trials=400, seed=0, with_complex=False)
        assert reading.directed_phi > 0.0
        assert not hasattr(reading, "is_recurrent")

    def test_but_a_zero_is_readable_from_one(self) -> None:
        """The asymmetry that makes `is_reducible` safe: sampling noise can
        manufacture structure, but it cannot manufacture its absence."""
        reading = coupled_phi(
            Wiring.FEEDFORWARD, trials=400, seed=0, with_complex=False
        )
        assert reading.is_reducible

    def test_the_null_floor_decays_with_sampling(self) -> None:
        """Averaged over seeds, because a single run does not show it. Three
        seeds once read 0.173 / 0.250 / 0.062 / 0.062 and looked like a
        systematic floor; eight give 0.251 / 0.155 / 0.081 / 0.037 — a clean
        halving per fourfold increase. Seed noise, not a plateau."""
        def floor(trials: int) -> float:
            return statistics.mean(
                coupled_phi(
                    Wiring.SELF, trials=trials, seed=s, with_complex=False
                ).directed_phi
                for s in range(8)
            )

        coarse, fine = floor(400), floor(6400)
        assert fine < coarse / 2, (coarse, fine)
        assert fine < RECURRENCE_FLOOR / 5

    def test_the_ring_does_not_decay(self) -> None:
        ring = recurrence_evidence(Wiring.RING, trials=400, seed=1)
        assert ring.held
        assert ring.is_recurrent

    def test_the_floor_is_measured_against_the_null(self) -> None:
        """The bar exists to sit above what no-coupling produces, so it has to
        be checked against it rather than asserted."""
        worst = max(
            coupled_phi(Wiring.SELF, trials=400, seed=s, with_complex=False).directed_phi
            for s in range(8)
        )
        assert worst < RECURRENCE_FLOOR

    def test_the_evidence_rejects_a_meaningless_factor(self) -> None:
        with pytest.raises(ValueError, match="factor must be >= 2"):
            recurrence_evidence(trials=400, factor=1)


class TestTheNumberCarriesItsConditions:
    def test_at_one_tick_the_ring_does_not_integrate(self) -> None:
        """The condition most easily dropped. One engine tick moves a unit 6%
        toward its target, so every unit is dominated by its own previous value,
        the matrix factorizes, and Phi is exactly zero — ring included."""
        reading = coupled_phi(
            Wiring.RING, macro_step=1, trials=TRIALS, seed=0, with_complex=False
        )
        assert reading.phi == 0.0
        assert reading.directed_phi == 0.0

    def test_the_reading_reports_every_condition(self) -> None:
        reading = coupled_phi(
            Wiring.RING, state=0b0101, trials=800, seed=0, with_complex=False
        )
        assert reading.state == 0b0101
        assert reading.macro_step == MACRO_STEP
        assert reading.trials == 800
        assert reading.wiring is Wiring.RING
        assert str(reading.trials) in str(reading)
        assert "tau" in str(reading)

    def test_the_macro_step_is_the_substrate_time_constant(self) -> None:
        assert MACRO_STEP == pytest.approx(1 / PULL, abs=1.0)

    def test_phi_is_a_property_of_a_state(self) -> None:
        """Not of a system. Different patterns measure differently."""
        readings = {
            state: coupled_phi(
                Wiring.RING, state=state, trials=TRIALS, seed=0, with_complex=False
            ).directed_phi
            for state in (0b0101, 0b0000, 0b1100)
        }
        assert len(set(readings.values())) > 1, readings


class TestTheDynamics:
    def test_the_ring_settles_into_an_alternating_pattern(self) -> None:
        """A negative four-cycle has two fixed points, and they are each other's
        inverse. This is why 0b0101 is the state Phi is measured at."""
        for seed in range(5):
            settled = CoupledEngine(wiring=Wiring.RING, seed=seed).run(400)
            assert settled.pattern in (0b0101, 0b1010), (seed, settled)

    def test_a_unit_flees_its_source(self) -> None:
        """The repulsion identity is what stayed the same. Drive one unit hard
        positive and whoever reads it must go negative."""
        engine = CoupledEngine(
            wiring=Wiring.RING, seed=1, initial=(AMPLITUDE,) * UNITS
        )
        engine.run(200)
        source_index = Wiring.RING.sources[1]
        assert source_index is not None
        assert engine.values[1] * engine.values[source_index] < 0

    def test_the_update_is_simultaneous(self) -> None:
        """Every unit reads the previous positions, so no unit has a privileged
        place in the cycle. A sequential update would make the ring's behaviour
        depend on which index happened to be first."""
        forward = CoupledEngine(
            wiring=Wiring.RING, seed=3, initial=(0.5, -0.5, 0.25, -0.25)
        )
        first = forward.step().values

        # Recomputed by hand from the same starting values, all at once.
        start = (0.5, -0.5, 0.25, -0.25)
        expected = []
        for i, source in enumerate(Wiring.RING.sources):
            assert source is not None
            target = -AMPLITUDE * math.tanh(GAIN * start[source] / AMPLITUDE)
            expected.append(start[i] + (target - start[i]) * PULL)
        # The walk adds noise, so compare the direction of travel rather than
        # the exact value.
        for got, want, began in zip(first, expected, start):
            assert (got - began) * (want - began) > 0 or abs(want - began) < 0.02

    def test_tension_stays_finite_and_positive(self) -> None:
        engine = CoupledEngine(wiring=Wiring.RING, seed=2)
        for _ in range(500):
            state = engine.step()
            assert 0.0 <= state.tension < 100.0

    def test_reset_rerandomizes_but_keeps_the_wiring(self) -> None:
        engine = CoupledEngine(wiring=Wiring.FEEDFORWARD, seed=4)
        engine.run(200)
        engine.reset()
        assert engine.ticks == 0
        assert engine.wiring is Wiring.FEEDFORWARD

    def test_a_seed_makes_a_run_reproducible(self) -> None:
        assert (
            CoupledEngine(seed=9).run(300) == CoupledEngine(seed=9).run(300)
        )

    def test_different_seeds_differ(self) -> None:
        assert CoupledEngine(seed=1).run(300) != CoupledEngine(seed=2).run(300)


class TestWiring:
    def test_only_the_ring_is_cyclic(self) -> None:
        assert Wiring.RING.is_cyclic
        assert not Wiring.FEEDFORWARD.is_cyclic
        assert not Wiring.SELF.is_cyclic

    def test_the_ring_sources_form_one_cycle(self) -> None:
        """Following the sources from any unit visits all four and returns."""
        sources = Wiring.RING.sources
        seen, unit = [], 0
        for _ in range(UNITS):
            seen.append(unit)
            following = sources[unit]
            assert following is not None
            unit = following
        assert sorted(seen) == list(range(UNITS))
        assert unit == 0, "the walk must return to where it started"

    def test_feedforward_has_a_unit_nothing_reaches(self) -> None:
        assert Wiring.FEEDFORWARD.sources[0] is None

    def test_every_wiring_names_one_source_per_unit(self) -> None:
        for wiring in Wiring:
            assert len(wiring.sources) == UNITS


class TestValidation:
    def test_it_rejects_a_useless_gain(self) -> None:
        with pytest.raises(ValueError, match="gain must be > 0"):
            CoupledEngine(gain=0.0)

    def test_it_rejects_a_useless_amplitude(self) -> None:
        with pytest.raises(ValueError, match="amplitude must be > 0"):
            CoupledEngine(amplitude=-1.0)

    def test_it_rejects_the_wrong_number_of_starting_values(self) -> None:
        with pytest.raises(ValueError, match=f"initial must have {UNITS} values"):
            CoupledEngine(initial=(0.1, 0.2))

    def test_it_rejects_a_meaningless_run(self) -> None:
        with pytest.raises(ValueError, match="ticks must be >= 1"):
            CoupledEngine().run(0)

    def test_the_matrix_rejects_a_zero_macro_step(self) -> None:
        from anima_reborn.substrate import coupled_matrix

        with pytest.raises(ValueError, match="macro_step must be >= 1"):
            coupled_matrix(macro_step=0)

    def test_the_units_are_named(self) -> None:
        assert NAMES == ("a0", "a1", "g0", "g1")
        assert len(NAMES) == UNITS
