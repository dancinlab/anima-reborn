"""The viewer — that it drives the real engines, and does so exactly once.

These exercise `Viewer` directly rather than over a socket: the HTTP layer is
stdlib, the part worth testing is the wiring between the page's controls and
the engines.
"""

from __future__ import annotations

import json

import pytest

from anima_reborn.viewer.server import MAX_STEPS_PER_REQUEST, Viewer, local_address


def params(**kwargs: object) -> dict[str, list[str]]:
    """Query parameters as the handler receives them — every value a string."""
    return {key: [str(value)] for key, value in kwargs.items()}


class TestAdvance:
    def test_every_engine_answers(self) -> None:
        viewer = Viewer(seed=1)
        for name in viewer.names():
            payload = viewer.advance(name, params(steps=60))
            assert payload, name
            # The page receives this over the wire, so it has to survive JSON.
            assert json.loads(json.dumps(payload)) == payload

    def test_steps_advance_the_engine_exactly_once_each(self) -> None:
        """A reading must never cost an extra tick — that would make the engine
        run faster than the page asked for."""
        viewer = Viewer(seed=2)
        viewer.advance("emergence", params(steps=10))
        assert viewer.engine("emergence").ticks == 10

        viewer.advance("emergence", params(steps=5))
        assert viewer.engine("emergence").ticks == 15

    def test_the_repulsion_field_is_not_double_stepped(self) -> None:
        viewer = Viewer(seed=3)
        viewer.advance("repulsion", params(steps=7))
        assert viewer.engine("repulsion").ticks == 7

    def test_the_pipeline_is_not_double_stepped(self) -> None:
        viewer = Viewer(seed=4)
        viewer.advance("pipeline", params(steps=7))
        assert viewer.engine("pipeline").ticks == 7


class TestControls:
    def test_coupling_reaches_the_engine(self) -> None:
        viewer = Viewer(seed=5)
        payload = viewer.advance("emergence", params(steps=250, coupling=1.0))
        assert payload["metrics"]["verdict"] == "emergent"

    def test_epsilon_reaches_the_engine(self) -> None:
        viewer = Viewer(seed=6)
        assert viewer.advance("crystal", params(steps=400, epsilon=0.02))["verdict"] == "locked"
        assert viewer.advance("crystal", params(steps=400, epsilon=0.6))["verdict"] == "chaos"

    def test_separation_reaches_the_pipeline(self) -> None:
        viewer = Viewer(seed=7)
        apart = viewer.advance("pipeline", params(steps=400, separation=1.0))["mi"]
        viewer.reset("pipeline")
        together = viewer.advance("pipeline", params(steps=400, separation=0.0))["mi"]
        assert apart > together

    def test_out_of_range_controls_are_clamped_not_rejected(self) -> None:
        """A stale or hand-edited query string must not take an engine outside
        the range it validates."""
        viewer = Viewer(seed=8)
        viewer.advance("emergence", params(steps=1, coupling=99))
        assert viewer.engine("emergence").coupling == 1.0

        viewer.advance("crystal", params(steps=1, epsilon=-5))
        assert viewer.engine("crystal").epsilon == 0.0

    def test_unparseable_controls_fall_back_to_the_current_value(self) -> None:
        viewer = Viewer(seed=9)
        viewer.advance("emergence", params(steps=1, coupling="banana"))
        assert viewer.engine("emergence").coupling == 0.5

    def test_missing_controls_leave_the_engine_alone(self) -> None:
        viewer = Viewer(seed=10)
        viewer.advance("emergence", params(steps=1, coupling=0.8))
        viewer.advance("emergence", params(steps=1))
        assert viewer.engine("emergence").coupling == pytest.approx(0.8)

    def test_a_huge_step_request_is_capped(self) -> None:
        """A page that stopped polling for a minute must not be able to demand
        an unbounded amount of work when it comes back."""
        viewer = Viewer(seed=11)
        viewer.advance("emergence", params(steps=10_000_000))
        assert viewer.engine("emergence").ticks == MAX_STEPS_PER_REQUEST

    def test_steps_below_one_still_advance(self) -> None:
        viewer = Viewer(seed=12)
        viewer.advance("emergence", params(steps=0))
        assert viewer.engine("emergence").ticks == 1


class TestPayloads:
    def test_emergence_withholds_metrics_until_the_window_fills(self) -> None:
        viewer = Viewer(seed=13)
        assert viewer.advance("emergence", params(steps=10))["metrics"] is None
        assert viewer.advance("emergence", params(steps=100))["metrics"] is not None

    def test_crystal_payload_is_drawable(self) -> None:
        payload = Viewer(seed=14).advance("crystal", params(steps=100))
        assert len(payload["spins"]) == 64
        assert set(payload["spins"]) <= {1, -1}
        assert payload["verdict"] in {"locked", "building", "chaos"}

    def test_repulsion_payload_carries_every_channel(self) -> None:
        payload = Viewer(seed=15).advance("repulsion", params(steps=50))
        assert len(payload["a"]) == 16
        assert len(payload["concept"]) == 16
        assert len(payload["context"]) == 8
        assert len(payload["sender"]) == 4
        assert payload["mood"] in {
            "surprised", "excited", "thoughtful", "calm", "quiet",
        }


class TestReset:
    def test_reset_rewinds_the_engine(self) -> None:
        viewer = Viewer(seed=16)
        viewer.advance("emergence", params(steps=100))
        viewer.reset("emergence")
        assert viewer.engine("emergence").ticks == 0

    def test_reset_rejects_an_unknown_engine(self) -> None:
        with pytest.raises(KeyError):
            Viewer().reset("nope")


class TestSeeding:
    def test_a_seed_makes_the_whole_viewer_reproducible(self) -> None:
        first = Viewer(seed=99).advance("emergence", params(steps=250))
        second = Viewer(seed=99).advance("emergence", params(steps=250))
        assert first == second


def test_local_address_is_an_address() -> None:
    """Never raises and never returns empty, even with no route out."""
    address = local_address()
    assert address.count(".") == 3
    assert all(part.isdigit() for part in address.split("."))
