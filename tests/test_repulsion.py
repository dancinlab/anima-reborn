"""The A x G repulsion field — the channels read off the gap between engines."""

from __future__ import annotations

import math

import pytest

from anima_reborn import Mood, RepulsionField


def fixed_clock() -> float:
    """A stopped clock, so the circadian channel is deterministic."""
    return 0.0


class TestMood:
    def test_a_curiosity_spike_outranks_any_tension(self) -> None:
        assert Mood.classify(tension=0.0, curiosity=0.9) is Mood.SURPRISED
        assert Mood.classify(tension=5.0, curiosity=0.9) is Mood.SURPRISED

    def test_tension_bands(self) -> None:
        assert Mood.classify(tension=2.0, curiosity=0.0) is Mood.EXCITED
        assert Mood.classify(tension=0.5, curiosity=0.0) is Mood.THOUGHTFUL
        assert Mood.classify(tension=0.1, curiosity=0.0) is Mood.CALM
        assert Mood.classify(tension=0.01, curiosity=0.0) is Mood.QUIET

    def test_the_boundaries_are_strict(self) -> None:
        assert Mood.classify(tension=1.0, curiosity=0.0) is Mood.THOUGHTFUL
        assert Mood.classify(tension=0.3, curiosity=0.0) is Mood.CALM
        assert Mood.classify(tension=0.05, curiosity=0.0) is Mood.QUIET
        assert Mood.classify(tension=0.0, curiosity=0.5) is Mood.QUIET


def circadian_at(seconds: float) -> float:
    """Context channel 0 for a field whose clock reads `seconds`."""
    field = RepulsionField(seed=11, clock=lambda: seconds)
    return field.step().context[0]


class TestRepulsionField:
    def test_separation_drives_tension_up(self) -> None:
        """The core relation: push the engines further apart and the field
        reports more tension."""
        readings = []
        for separation in (0.0, 0.5, 1.0):
            field = RepulsionField(separation=separation, seed=1, clock=fixed_clock)
            tensions = [field.step().tension for _ in range(300)]
            readings.append(sum(tensions[100:]) / len(tensions[100:]))

        assert readings == sorted(readings), readings
        assert readings[-1] > readings[0]

    def test_collapsed_engines_go_quiet(self) -> None:
        """With no separation driving them apart, tension decays to nothing and
        the field reports `quiet` — not calm, but no gap left to think in."""
        field = RepulsionField(separation=0.0, noise=0.0, seed=2, clock=fixed_clock)
        state = field.run(500)
        assert state.tension < 0.05
        assert state.mood is Mood.QUIET

    def test_the_concept_vector_is_a_unit_vector(self) -> None:
        field = RepulsionField(seed=3, clock=fixed_clock)
        for _ in range(200):
            state = field.step()
            norm = math.sqrt(sum(c * c for c in state.concept))
            assert norm == pytest.approx(1.0)

    def test_identical_engines_have_no_direction_rather_than_a_crash(self) -> None:
        """Zero repulsion would divide by zero. Started from one shared vector
        with nothing to separate them, A and G stay identical forever, so the
        field must report a zero concept instead of failing."""
        vector = [0.3] * 16
        field = RepulsionField(
            separation=0.0,
            noise=0.0,
            seed=4,
            clock=fixed_clock,
            initial=(vector, list(vector)),
        )
        for _ in range(50):
            state = field.step()
            assert state.tension == pytest.approx(0.0)
            assert all(c == 0.0 for c in state.concept)
            assert state.mood is Mood.QUIET

    def test_topic_names_the_dominant_axis(self) -> None:
        field = RepulsionField(seed=5, clock=fixed_clock)
        for _ in range(200):
            state = field.step()
            dominant = max(range(field.dim), key=lambda i: abs(state.concept[i]))
            assert state.topic == dominant

    def test_curiosity_is_the_change_in_tension(self) -> None:
        field = RepulsionField(seed=6, clock=fixed_clock)
        previous = field.step().tension
        for _ in range(100):
            state = field.step()
            assert state.curiosity == pytest.approx(abs(state.tension - previous))
            previous = state.tension

    def test_authenticity_stays_in_unit_range(self) -> None:
        field = RepulsionField(seed=7, clock=fixed_clock)
        for _ in range(300):
            assert 0.0 <= field.step().authenticity <= 1.0

    def test_a_steady_field_reads_as_authentic(self) -> None:
        """Authenticity is one minus tension volatility, so a field left alone
        to settle should score high."""
        field = RepulsionField(separation=0.0, noise=0.0, seed=8, clock=fixed_clock)
        assert field.run(400).authenticity > 0.9

    def test_channel_widths_are_fixed(self) -> None:
        field = RepulsionField(seed=9, clock=fixed_clock)
        state = field.step()
        assert len(state.concept) == field.dim
        assert len(state.meaning) == field.dim
        assert len(state.context) == 8
        assert len(state.sender) == 4

    def test_the_sender_signature_is_a_fraction(self) -> None:
        field = RepulsionField(seed=10, clock=fixed_clock)
        for _ in range(100):
            assert all(0.0 <= v < 1.0 for v in field.step().sender)

    def test_the_circadian_channel_tracks_the_clock(self) -> None:
        """Channel 0 is a sine over the day: zero at midnight and noon, peaking
        at 06:00 and troughing at 18:00."""
        assert circadian_at(0.0) == pytest.approx(0.0, abs=1e-9)
        assert circadian_at(21600.0) == pytest.approx(1.0)
        assert circadian_at(43200.0) == pytest.approx(0.0, abs=1e-9)
        assert circadian_at(64800.0) == pytest.approx(-1.0)

    def test_the_window_fill_channel_saturates(self) -> None:
        field = RepulsionField(seed=12, clock=fixed_clock)
        assert field.step().context[5] == pytest.approx(1 / 30)
        assert field.run(29).context[5] == pytest.approx(1.0)
        assert field.run(100).context[5] == pytest.approx(1.0)

    def test_a_seed_makes_a_run_reproducible(self) -> None:
        first = RepulsionField(seed=77, clock=fixed_clock).run(200)
        second = RepulsionField(seed=77, clock=fixed_clock).run(200)
        assert first == second

    def test_reset_returns_the_field_to_a_fresh_start(self) -> None:
        field = RepulsionField(seed=13, clock=fixed_clock)
        field.run(200)
        field.reset()
        assert field.ticks == 0
        assert field.step().context[5] == pytest.approx(1 / 30)

    def test_configuration_is_validated(self) -> None:
        with pytest.raises(ValueError, match="dim must be >= 4"):
            RepulsionField(dim=3)
        with pytest.raises(ValueError, match="ticks must be >= 1"):
            RepulsionField().run(0)
        with pytest.raises(ValueError, match="initial A must have 16 entries"):
            RepulsionField(initial=([0.0] * 4, [0.0] * 16))
