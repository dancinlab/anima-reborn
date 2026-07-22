"""The viewer — that it drives the real engines, and does so exactly once.

These exercise `Viewer` directly rather than over a socket: the HTTP layer is
stdlib, the part worth testing is the wiring between the page's controls and
the engines.
"""

from __future__ import annotations

import importlib
import inspect
import json
import re
import time
from pathlib import Path

import pytest

import anima_reborn
from anima_reborn.viewer.server import (
    MAX_STEPS_PER_REQUEST,
    PAGE,
    TICK_RATES,
    Viewer,
    local_address,
)


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


class TestTicker:
    def test_a_ticker_runs_only_while_watched(self) -> None:
        viewer = Viewer(seed=20)
        ticker = viewer.ticker("emergence")
        assert ticker.watchers == 0

        ticker.subscribe()
        assert ticker.watchers == 1
        sequence, _ = ticker.wait(0, timeout=2.0)
        assert sequence > 0, "a subscribed ticker must produce frames"

        ticker.unsubscribe()
        assert ticker.watchers == 0
        settled = viewer.engine("emergence").ticks
        time.sleep(0.2)
        assert viewer.engine("emergence").ticks == settled, "an unwatched ticker must stop"

    def test_rapid_resubscribe_leaves_one_thread(self) -> None:
        """Switching tabs quickly must not leave the previous ticker thread
        alive alongside the new one — two threads would step a single engine at
        twice its rate."""
        viewer = Viewer(seed=21)
        ticker = viewer.ticker("emergence")
        for _ in range(8):
            ticker.subscribe()
            ticker.unsubscribe()

        ticker.subscribe()
        try:
            ticker.wait(0, timeout=2.0)
            before = viewer.engine("emergence").ticks
            time.sleep(0.5)
            elapsed = viewer.engine("emergence").ticks - before
        finally:
            ticker.unsubscribe()

        # 60 Hz for half a second is ~30 ticks. Two threads would roughly
        # double it, so the ceiling is what this test is really asserting.
        assert 10 < elapsed < 55, elapsed

    def test_controls_reach_a_running_ticker(self) -> None:
        viewer = Viewer(seed=22)
        viewer.control("emergence", params(coupling=1.0))
        ticker = viewer.ticker("emergence")
        ticker.subscribe()
        try:
            ticker.wait(0, timeout=2.0)
        finally:
            ticker.unsubscribe()
        assert viewer.engine("emergence").coupling == 1.0

    def test_every_engine_ticks_at_the_origins_rate(self) -> None:
        rates = {"emergence": 60.0, "crystal": 20.0, "repulsion": 30.0, "pipeline": 30.0}
        viewer = Viewer(seed=23)
        for name, expected in rates.items():
            assert viewer.ticker(name).rate == expected


class TestEngineViewerLockstep:
    """Every engine must be visible in the viewer, and vice versa.

    An engine nobody can watch tends to rot — the crystal sat unwired to
    anything for a while and it took a question to notice. So the rule is not a
    note in a guide, it is these tests: add an engine without a tab, or leave a
    tab pointing at an engine that no longer exists, and the suite fails.

    "Engine" is decided structurally rather than from a hand-written list, so a
    new one is caught the day it lands: a class defined in a top-level module of
    the package that has both `step` and `reset`.
    """

    @staticmethod
    def engine_modules() -> set[str]:
        found = set()
        package = Path(anima_reborn.__file__).parent
        for path in sorted(package.glob("*.py")):
            if path.stem.startswith("_"):
                continue
            module = importlib.import_module(f"anima_reborn.{path.stem}")
            for value in vars(module).values():
                if (
                    inspect.isclass(value)
                    and value.__module__ == module.__name__
                    and callable(getattr(value, "step", None))
                    and callable(getattr(value, "reset", None))
                ):
                    found.add(path.stem)
                    break
        return found

    @staticmethod
    def page() -> str:
        return PAGE.read_text(encoding="utf-8")

    def test_every_engine_has_a_route(self) -> None:
        missing = self.engine_modules() - set(Viewer().names())
        assert not missing, (
            f"engine(s) with no viewer route: {sorted(missing)} — "
            "add a handler to _HANDLERS and an instance to Viewer.__init__"
        )

    def test_no_route_points_at_a_missing_engine(self) -> None:
        orphans = set(Viewer().names()) - self.engine_modules()
        assert not orphans, f"viewer route(s) with no engine: {sorted(orphans)}"

    def test_every_route_has_a_tick_rate(self) -> None:
        assert set(Viewer().names()) == set(TICK_RATES)

    def test_every_route_has_a_tab_and_a_panel(self) -> None:
        page = self.page()
        for name in Viewer().names():
            assert f'data-tab="{name}"' in page, f"{name} has no tab button"
            assert f'id="p-{name}"' in page, f"{name} has no panel"

    def test_exactly_one_tab_is_active(self) -> None:
        page = self.page()
        assert page.count('class="tab active"') == 1
        assert page.count('class="panel active"') == 1

    def test_the_default_tab_and_panel_agree(self) -> None:
        page = self.page()
        tab = re.search(r'class="tab active" data-tab="(\w+)"', page)
        panel = re.search(r'class="panel active" id="p-(\w+)"', page)
        active = re.search(r'let active = "(\w+)";', page)
        assert tab and panel and active
        assert tab.group(1) == panel.group(1) == active.group(1)

    def test_every_route_is_drawable(self) -> None:
        """A tab that streams frames nothing knows how to draw is a blank
        panel, which looks like a broken engine."""
        page = self.page()
        prefix_line = page.split("const PREFIX =")[1].split("\n")[0]
        for name in Viewer().names():
            assert f"{name}:" in prefix_line, f"{name} is missing from the PREFIX map"
            # The dispatch runs one branch per engine and falls through to the
            # last, so the render function is the thing to check for — a name
            # in the `if` chain would miss whichever engine is the `else`.
            renderer = f"function render{name[0].upper()}{name[1:]}("
            assert renderer in page, f"{name} has no {renderer.strip('(')} function"

    def test_every_route_answers_with_a_drawable_frame(self) -> None:
        viewer = Viewer(seed=1)
        for name in viewer.names():
            payload = viewer.advance(name, params(steps=60))
            assert payload, name
            assert json.loads(json.dumps(payload)) == payload, name


def test_local_address_is_an_address() -> None:
    """Never raises and never returns empty, even with no route out."""
    address = local_address()
    assert address.count(".") == 3
    assert all(part.isdigit() for part in address.split("."))
