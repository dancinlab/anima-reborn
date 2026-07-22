"""The full chain — does engine separation actually produce emergence?"""

from __future__ import annotations

import math

import pytest

from anima_reborn import Emergence, Pipeline


def test_separation_produces_shared_information() -> None:
    """The pipeline's whole claim: hold the engines apart and the two sampled
    streams start carrying information in common."""
    apart = Pipeline(separation=1.0, seed=1).run(400)
    together = Pipeline(separation=0.0, seed=1).run(400)
    assert apart.mutual_information > together.mutual_information


def test_collapsed_engines_produce_no_emergence() -> None:
    state = Pipeline(separation=0.0, seed=2).run(400)
    assert state.verdict is Emergence.INDEPENDENT


def test_wide_separation_reaches_emergence() -> None:
    state = Pipeline(separation=1.0, seed=2).run(400)
    assert state.verdict is Emergence.EMERGENT


def test_tension_rises_with_separation() -> None:
    readings = [
        Pipeline(separation=s, seed=3).run(400).tension for s in (0.0, 0.5, 1.0)
    ]
    assert readings == sorted(readings), readings


def test_metrics_stay_silent_until_the_window_fills() -> None:
    pipeline = Pipeline(seed=4)
    state = pipeline.run(49)
    assert state.h_left == 0.0
    assert state.mutual_information == 0.0
    # Tension is a property of the engines, not the window, so it is live from
    # the first tick.
    assert state.tension > 0.0

    assert pipeline.step().h_left > 0.0


def test_the_window_rolls_rather_than_grows() -> None:
    pipeline = Pipeline(seed=5, history=100)
    pipeline.run(500)
    assert len(pipeline.left) == 100
    assert len(pipeline.right) == 100
    assert pipeline.ticks == 500


def test_a_seed_makes_a_run_reproducible() -> None:
    assert Pipeline(seed=55).run(300) == Pipeline(seed=55).run(300)


def test_different_seeds_give_different_runs() -> None:
    assert Pipeline(seed=1).run(300) != Pipeline(seed=2).run(300)


def test_entropies_are_bounded_by_the_binning() -> None:
    state = Pipeline(separation=0.8, seed=6).run(400)
    assert 0.0 <= state.h_left <= math.log2(12)
    assert 0.0 <= state.h_right <= math.log2(12)
    assert state.h_joint >= max(state.h_left, state.h_right) - 1e-12


def test_only_the_leading_dimensions_are_driven() -> None:
    """Dims 2 and up decay, which is what keeps the observable structure in the
    dimension the streams are sampled from."""
    pipeline = Pipeline(separation=1.0, seed=7)
    pipeline.run(500)
    leading = max(abs(pipeline.a[0]), abs(pipeline.a[1]))
    trailing = max(abs(v) for v in pipeline.a[2:])
    assert leading > trailing


def test_separation_can_be_changed_mid_run() -> None:
    """The original drives this from a live slider."""
    pipeline = Pipeline(separation=0.0, seed=8)
    assert pipeline.run(400).verdict is Emergence.INDEPENDENT
    pipeline.separation = 1.0
    assert pipeline.run(600).verdict is Emergence.EMERGENT


def test_reset_clears_the_streams() -> None:
    pipeline = Pipeline(seed=9)
    pipeline.run(300)
    pipeline.reset()
    assert pipeline.left == ()
    assert pipeline.ticks == 0


def test_configuration_is_validated() -> None:
    with pytest.raises(ValueError, match="dim must be >= 2"):
        Pipeline(dim=1)
    with pytest.raises(ValueError, match="history must be >= 1"):
        Pipeline(history=0)
    with pytest.raises(ValueError, match="ticks must be >= 1"):
        Pipeline().run(0)
