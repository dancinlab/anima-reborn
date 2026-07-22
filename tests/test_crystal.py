"""The time crystal — does the ring actually keep a beat, and does it melt?"""

from __future__ import annotations

import pytest

from anima_reborn import CrystalVerdict, TimeCrystal, autocorrelation


class TestAutocorrelation:
    def test_a_series_correlates_perfectly_with_itself(self) -> None:
        series = [(-1.0) ** i * (i % 7) for i in range(100)]
        assert autocorrelation(series, 0) == pytest.approx(1.0)

    def test_an_alternating_series_is_antiphase_at_lag_one(self) -> None:
        series = [1.0 if i % 2 == 0 else -1.0 for i in range(100)]
        assert autocorrelation(series, 1) == pytest.approx(-1.0)
        assert autocorrelation(series, 2) == pytest.approx(1.0)

    def test_a_flat_series_has_no_correlation_to_report(self) -> None:
        assert autocorrelation([0.5] * 100, 1) == 0.0

    def test_too_short_a_series_returns_zero_rather_than_noise(self) -> None:
        assert autocorrelation([1.0, -1.0] * 5, 1) == 0.0

    def test_negative_lag_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="lag must be >= 0"):
            autocorrelation([1.0] * 100, -1)


class TestTimeCrystal:
    def test_a_near_perfect_drive_locks_the_crystal(self) -> None:
        """The claim: with a small imperfection the Ising coupling repairs the
        damage and the period-2 rhythm survives."""
        state = TimeCrystal(epsilon=0.02, seed=1).run(400)
        assert state.verdict is CrystalVerdict.LOCKED
        assert state.ac1 < -0.85
        assert state.ac2 > 0.80

    def test_a_broken_drive_melts_the_crystal(self) -> None:
        """Miss half the spins every period and there is no rhythm left."""
        state = TimeCrystal(epsilon=0.5, seed=1).run(400)
        assert state.verdict is CrystalVerdict.CHAOS

    def test_the_lock_degrades_as_the_drive_worsens(self) -> None:
        locked = TimeCrystal(epsilon=0.02, seed=7).run(400)
        melted = TimeCrystal(epsilon=0.6, seed=7).run(400)
        assert locked.ac1 < melted.ac1

    def test_spins_are_always_plus_or_minus_one(self) -> None:
        crystal = TimeCrystal(seed=2)
        for _ in range(200):
            crystal.step()
            assert set(crystal.spins) <= {1, -1}

    def test_magnetization_stays_in_range(self) -> None:
        crystal = TimeCrystal(seed=3)
        for _ in range(300):
            state = crystal.step()
            assert -1.0 <= state.magnetization <= 1.0

    def test_the_history_rolls_rather_than_grows(self) -> None:
        crystal = TimeCrystal(seed=4, history=50)
        crystal.run(300)
        assert len(crystal.history) == 50

    def test_a_seed_makes_a_run_reproducible(self) -> None:
        first = TimeCrystal(epsilon=0.05, seed=99).run(200)
        second = TimeCrystal(epsilon=0.05, seed=99).run(200)
        assert first == second

    def test_epsilon_can_be_changed_mid_run(self) -> None:
        """The original drives this from a live slider: a locked crystal must
        be able to melt without being rebuilt."""
        crystal = TimeCrystal(epsilon=0.02, seed=5)
        assert crystal.run(400).verdict is CrystalVerdict.LOCKED
        crystal.epsilon = 0.6
        assert crystal.run(400).verdict is CrystalVerdict.CHAOS

    def test_reset_drops_the_history(self) -> None:
        crystal = TimeCrystal(seed=6)
        crystal.run(200)
        crystal.reset()
        assert crystal.history == ()
        assert len(crystal.spins) == crystal.size

    def test_configuration_is_validated(self) -> None:
        with pytest.raises(ValueError, match="size must be >= 3"):
            TimeCrystal(size=2)
        with pytest.raises(ValueError, match=r"epsilon must be in \[0, 1\]"):
            TimeCrystal(epsilon=1.5)
        with pytest.raises(ValueError, match="ticks must be >= 1"):
            TimeCrystal().run(0)


class TestVerdictThresholds:
    def test_classification(self) -> None:
        assert CrystalVerdict.classify(-0.9, 0.9) is CrystalVerdict.LOCKED
        # anti-phase at lag 1 but lag 2 has not caught up
        assert CrystalVerdict.classify(-0.9, 0.5) is CrystalVerdict.BUILDING
        assert CrystalVerdict.classify(-0.6, 0.9) is CrystalVerdict.BUILDING
        assert CrystalVerdict.classify(-0.1, 0.0) is CrystalVerdict.CHAOS
