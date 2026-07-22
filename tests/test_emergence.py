"""The emergence engine — does coupling actually produce shared information?"""

from __future__ import annotations

import pytest

from anima_reborn import Emergence, EmergenceEngine


def mean_mi(coupling: float, *, window: int = 250, seeds: int = 24) -> float:
    """Average MI over independent runs, each measured on a full window — one
    run is far too noisy to compare."""
    total = 0.0
    for seed in range(seeds):
        engine = EmergenceEngine(coupling=coupling, seed=seed, history=window)
        metrics = engine.run(window)
        assert metrics is not None
        total += metrics.mutual_information
    return total / seeds


def test_uncoupled_streams_never_reach_emergence() -> None:
    """Independent streams never clear the emergence bar, on any seed."""
    for seed in range(24):
        metrics = EmergenceEngine(coupling=0.0, seed=seed).run(250)
        assert metrics is not None
        assert metrics.verdict is not Emergence.EMERGENT


def test_uncoupled_streams_sit_on_the_estimator_bias_floor() -> None:
    """Uncoupled does NOT read as zero MI on the default window: 144 joint bins
    filled from 250 samples are sparse enough to look like structure. This
    pins that floor so a future change to the estimator or the window shows up
    here rather than being mistaken for real emergence."""
    assert 0.10 < mean_mi(0.0) < 0.25


def test_the_bias_floor_collapses_on_a_long_window() -> None:
    """Proof that the floor above is a small-sample artefact and not a coupling
    the engine is leaking: give the estimator enough samples and independent
    streams read as independent."""
    long_window = mean_mi(0.0, window=5000, seeds=6)
    assert long_window < 0.05
    assert long_window < mean_mi(0.0, window=250, seeds=6)


def test_strong_coupling_produces_emergence() -> None:
    """The claim the whole visualizer exists to make."""
    metrics = EmergenceEngine(coupling=0.95, seed=1).run(250)
    assert metrics is not None
    assert metrics.mutual_information > 0.30
    assert metrics.verdict is Emergence.EMERGENT


def test_mutual_information_rises_with_coupling() -> None:
    """Monotone in the mean. A single run is not — at low coupling the spread
    between seeds swamps the difference between settings."""
    readings = [mean_mi(c) for c in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert readings == sorted(readings), readings
    assert readings[-1] - readings[0] > 2.0


def test_full_coupling_makes_the_streams_identical() -> None:
    engine = EmergenceEngine(coupling=1.0, seed=9)
    engine.run(250)
    assert engine.left == engine.right


def test_no_metrics_until_the_window_has_filled() -> None:
    engine = EmergenceEngine(coupling=0.9, seed=2)
    assert engine.metrics is None
    engine.run(49)
    assert engine.metrics is None
    engine.step()
    assert engine.metrics is not None


def test_the_window_rolls_rather_than_grows() -> None:
    engine = EmergenceEngine(coupling=0.5, seed=3, history=100)
    engine.run(500)
    assert len(engine.left) == 100
    assert len(engine.right) == 100
    assert engine.ticks == 500


def test_a_seed_makes_a_run_reproducible() -> None:
    first = EmergenceEngine(coupling=0.6, seed=123).run(250)
    second = EmergenceEngine(coupling=0.6, seed=123).run(250)
    assert first == second


def test_different_seeds_give_different_runs() -> None:
    first = EmergenceEngine(coupling=0.6, seed=1).run(250)
    second = EmergenceEngine(coupling=0.6, seed=2).run(250)
    assert first != second


def test_entropies_are_bounded_by_the_binning() -> None:
    """Twelve bins cap each stream at log2(12) bits and the pair at log2(144)."""
    import math

    metrics = EmergenceEngine(coupling=0.4, seed=8).run(250)
    assert metrics is not None
    assert 0.0 <= metrics.h_left <= math.log2(12)
    assert 0.0 <= metrics.h_right <= math.log2(12)
    assert 0.0 <= metrics.h_joint <= math.log2(144)
    assert metrics.h_joint >= max(metrics.h_left, metrics.h_right) - 1e-12


def test_samples_stay_within_the_binning_range() -> None:
    """Noise spans [-1, 1] and the shared sine spans [-1, 1], so any blend of
    them fits inside the +/-1.5 window without clamping."""
    engine = EmergenceEngine(coupling=0.5, seed=4)
    for _ in range(1000):
        left, right = engine.step()
        assert -1.5 <= left <= 1.5
        assert -1.5 <= right <= 1.5


def test_reset_clears_the_window() -> None:
    engine = EmergenceEngine(coupling=0.9, seed=5)
    engine.run(250)
    engine.reset()
    assert engine.left == ()
    assert engine.ticks == 0
    assert engine.metrics is None


def test_coupling_is_validated() -> None:
    with pytest.raises(ValueError, match=r"coupling must be in \[0, 1\]"):
        EmergenceEngine(coupling=1.5)
    with pytest.raises(ValueError, match=r"coupling must be in \[0, 1\]"):
        EmergenceEngine(coupling=-0.1)


def test_coupling_can_be_changed_mid_run() -> None:
    """The original drives this from a live slider."""
    engine = EmergenceEngine(coupling=0.0, seed=6)
    engine.run(250)
    engine.coupling = 1.0
    metrics = engine.run(250)
    assert metrics is not None
    assert metrics.verdict is Emergence.EMERGENT


def test_run_rejects_negative_ticks() -> None:
    with pytest.raises(ValueError, match="ticks must be >= 0"):
        EmergenceEngine().run(-1)
