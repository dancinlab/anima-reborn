"""The wall between integration and representation, and the rhythm through it.

`coupled.py` bought integration by wiring the units to each other. Adding a
drive — something the engine is *told* — exposes what that cost: on a fixed
coupling the engine either keeps what it was told or integrates, never both.
That is not a tuning failure. It is what a fixed coupling is, and the tests here
put it at risk two ways.

**The wall.** Representation falls monotonically as the coupling rises, and at
full coupling the drive is not merely weak but unreachable — the trajectory is
bit-for-bit identical whatever it is told.

**The way through, and how far it goes.** Alternating splits the two demands
across time instead of asking one coupling to meet both, and it restores
representation that fixed coupling has none of. The control that matters is a
fixed coupling at the alternation's own time average: if the effect were "some
coupling on average", that control would reproduce it, and it does not.

**What was withdrawn.** An earlier reading also claimed the rhythm reached
matched-or-higher Phi, which would have made it a free win rather than a trade.
It had compared a rhythm at tau 40 against fixed couplings at tau 20, and Phi
rises with tau by itself. Re-measured at matched tau the direction is not even
fixed — it depends on the drive — so nothing here asserts one, and the test that
would have is replaced by the exact statement of why: a rhythm's transition
matrix moves with what it is told and a fixed engine's cannot.
"""

from __future__ import annotations

import hashlib
import statistics

import pytest

from anima_reborn.coupled import (
    ALTERNATING,
    FIXED,
    HIGH,
    MACRO_STEP,
    PERIOD,
    CoupledEngine,
    Rhythm,
    Wiring,
)
from anima_reborn.substrate import coupled_matrix, coupled_phi, representation

WORDS = [
    "고양이", "자동차", "바다", "연필", "하늘", "돌멩이", "웃음", "기차",
    "구름", "의자", "강물", "종이", "산", "모래", "노래", "버스",
]
"""Sixteen drives. The reading scales with what the inputs carry, and eight left
the ratio close enough to the floor to be argued about."""


def encode(word: str) -> float:
    digest = hashlib.blake2b(word.encode("utf-8"), digest_size=2).digest()
    return int.from_bytes(digest, "big") / 65535.0 * 2.0 - 1.0


DRIVES = [encode(w) for w in WORDS]


def represents(rhythm: Rhythm, *, seeds: int = 3) -> float:
    return statistics.mean(
        representation(DRIVES, rhythm=rhythm, seed=s).ratio for s in range(1, seeds + 1)
    )


class TestTheSchedule:
    def test_a_fixed_rhythm_never_lets_go(self) -> None:
        rhythm = Rhythm(coupling=0.6)
        assert not rhythm.alternates
        assert [rhythm.at(t) for t in range(5)] == [0.6] * 5

    def test_an_alternating_rhythm_listens_first(self) -> None:
        """A run should begin by taking something in, not by settling into the
        ring's attractor with nothing heard."""
        rhythm = Rhythm(coupling=0.7, period=2)
        assert [rhythm.at(t) for t in range(8)] == [0, 0, 0.7, 0.7, 0, 0, 0.7, 0.7]

    def test_the_mean_is_what_a_fixed_control_must_match(self) -> None:
        assert Rhythm(coupling=0.7, period=10).mean == pytest.approx(0.35)
        assert Rhythm(coupling=0.7).mean == pytest.approx(0.7)

    def test_a_rhythm_is_measured_over_a_whole_cycle(self) -> None:
        """Half a cycle would report one phase's transition matrix and call it
        the engine's."""
        assert Rhythm(coupling=0.7, period=10).macro_step == 20
        assert Rhythm(coupling=0.7).macro_step == MACRO_STEP

    def test_the_shipped_rhythms_are_what_they_say(self) -> None:
        assert FIXED == Rhythm(coupling=1.0, period=None)
        assert ALTERNATING == Rhythm(coupling=HIGH, period=PERIOD)

    def test_configuration_is_validated(self) -> None:
        with pytest.raises(ValueError, match="coupling must be in"):
            Rhythm(coupling=1.4)
        with pytest.raises(ValueError, match="coupling must be in"):
            Rhythm(coupling=-0.1)
        with pytest.raises(ValueError, match="period must be >= 1"):
            Rhythm(period=0)
        with pytest.raises(ValueError, match="drive must be in"):
            CoupledEngine(drive=2.0)


class TestTheDefaultChangedNothing:
    """Rhythms were added to an engine whose measurements were already
    published. If the default moved a single float, those numbers stopped
    referring to this code."""

    def test_the_default_is_the_engine_as_it_was(self) -> None:
        assert CoupledEngine(seed=1).rhythm == FIXED

    def test_at_full_coupling_the_drive_is_unreachable(self) -> None:
        """Bit-identical, not merely close. This is the wall stated exactly:
        a unit whose target is entirely its partner cannot hear anything."""
        deaf = CoupledEngine(seed=5, drive=0.0).run(400)
        shouted = CoupledEngine(seed=5, drive=1.0).run(400)
        assert deaf.values == shouted.values

    def test_and_the_reading_says_so(self) -> None:
        state = CoupledEngine(seed=5).run(10)
        assert state.coupling == 1.0
        assert not state.listening


class TestTheWall:
    def test_representation_falls_as_the_coupling_rises(self) -> None:
        readings = [represents(Rhythm(c)) for c in (0.0, 0.35, 0.7, 1.0)]
        assert readings == sorted(readings, reverse=True), readings

    def test_at_the_top_nothing_of_the_drive_survives(self) -> None:
        """Different drives separate the engine no more than one drive separates
        from itself — the floor is structural, not a chosen bar."""
        assert not representation(DRIVES, rhythm=FIXED).represents

    def test_and_at_the_bottom_it_all_does(self) -> None:
        assert representation(DRIVES, rhythm=Rhythm(0.0)).represents


class TestTheWayThrough:
    def test_alternating_represents_where_the_same_coupling_cannot(self) -> None:
        """`HIGH` held fixed destroys the drive; released half the time it does
        not, at the same coupling value."""
        assert represents(Rhythm(HIGH)) < 1.0
        assert represents(ALTERNATING) > 3.0

    def test_it_integrates_more_than_a_fixed_coupling_at_its_own_mean(self) -> None:
        """The control that matters. Both spend the same coupling on average and
        sit at the same tau, so an advantage here is the rhythm's and not the
        mean's. Measured with nothing being said (`drive` 0), which is a
        condition and not an oversight — see the next test for why.

        Resolvable: 8.08 vs 0.90 at 1600 trials, 8.02 vs 0.85 at 6400, so this
        is not the estimator's bias being read as a difference.
        """
        alternating = statistics.mean(
            coupled_phi(rhythm=ALTERNATING, trials=1600, seed=s, with_complex=False)
            .directed_phi
            for s in range(2)
        )
        same_mean = statistics.mean(
            coupled_phi(
                rhythm=Rhythm(ALTERNATING.mean),
                macro_step=ALTERNATING.macro_step,
                trials=1600,
                seed=s,
                with_complex=False,
            ).directed_phi
            for s in range(2)
        )
        assert alternating > same_mean, (alternating, same_mean)

    def test_a_rhythms_integration_depends_on_what_it_is_told(self) -> None:
        """Why no test here asserts that a rhythm out-integrates a fixed
        coupling, and why the claim that it does was withdrawn.

        A fixed engine cannot hear, so its transition matrix is bit-identical
        whatever the drive — Phi is a property of the engine alone. A rhythm
        hears, so its matrix moves with the drive, and its Phi moves too:
        measured at tau 40, alternating 20/20 reads 14.99 told nothing, 13.16
        told 0.42, and is indistinguishable from fixed coupling told -0.27.
        A direction quoted without the drive is therefore not a finding.

        This is checked on the matrices rather than on Phi because it is then
        exact rather than a threshold on a noisy estimate.
        """
        def grid(rhythm: Rhythm, drive: float) -> list[float]:
            matrix = coupled_matrix(rhythm=rhythm, drive=drive, trials=100, seed=1)
            return [
                matrix.probability(state, unit)
                for state in range(16)
                for unit in range(4)
            ]

        assert grid(FIXED, 0.0) == grid(FIXED, 0.9)
        assert grid(ALTERNATING, 0.0) != grid(ALTERNATING, 0.9)

    def test_what_it_buys_is_representation_the_other_has_none_of(self) -> None:
        assert representation(DRIVES, rhythm=Rhythm(HIGH, period=20)).represents
        assert not representation(DRIVES, rhythm=FIXED).represents


class TestTheEngineCarriesIt:
    def test_the_phase_is_visible_in_the_reading(self) -> None:
        engine = CoupledEngine(rhythm=Rhythm(0.7, period=3), drive=0.5, seed=1)
        phases = [engine.step().listening for _ in range(9)]
        assert phases == [True] * 3 + [False] * 3 + [True] * 3

    def test_a_drive_moves_it_only_while_listening(self) -> None:
        rhythm = Rhythm(0.7, period=3)
        quiet = CoupledEngine(rhythm=rhythm, drive=0.0, seed=6, initial=(0.0,) * 4)
        loud = CoupledEngine(rhythm=rhythm, drive=1.0, seed=6, initial=(0.0,) * 4)
        # First tick is a listen tick, so one step already separates them.
        assert quiet.step().values != loud.step().values

    def test_reset_keeps_the_rhythm_and_rewinds_the_phase(self) -> None:
        engine = CoupledEngine(rhythm=ALTERNATING, seed=1)
        engine.run(PERIOD + 1)
        assert not engine.state.listening
        engine.reset()
        assert engine.rhythm == ALTERNATING
        assert engine.state.listening

    def test_a_seed_makes_a_rhythmic_run_reproducible(self) -> None:
        left = CoupledEngine(rhythm=ALTERNATING, drive=0.4, seed=9).run(120)
        right = CoupledEngine(rhythm=ALTERNATING, drive=0.4, seed=9).run(120)
        assert left == right

    def test_the_wirings_still_falsify_under_a_rhythm(self) -> None:
        """Whatever the rhythm does, it does not make an uncoupled engine
        behave like the ring."""
        engine = CoupledEngine(wiring=Wiring.SELF, rhythm=ALTERNATING, seed=1)
        assert engine.run(200).coupling in (0.0, HIGH)


class TestRepresentationIsValidated:
    def test_it_needs_something_to_compare(self) -> None:
        with pytest.raises(ValueError, match="drives must have at least 2"):
            representation([0.5])
        with pytest.raises(ValueError, match="noise_seeds must be >= 2"):
            representation(DRIVES, noise_seeds=1)
        with pytest.raises(ValueError, match="tail must be in"):
            representation(DRIVES, ticks=50, tail=80)

    def test_the_reading_carries_its_conditions(self) -> None:
        reading = representation(DRIVES[:4], rhythm=ALTERNATING, ticks=200, tail=80)
        assert reading.drives == 4
        assert reading.ticks == 200
        assert "200 ticks" in str(reading)
