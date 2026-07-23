"""The transient window: a read before the basin claims the state carries both bit and depth.

Pins that the held |delta| still separates by input amplitude at a transient hold (depth present)
while the sign is already settled, and that the endpoint has erased the depth — so context is
available in the transient window that Part 4's endpoint gate could not reach. The MI decay curve
lives in `state/communication/transient_context.py` and RESULTS.
"""

from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "transient_context.py"
_spec = importlib.util.spec_from_file_location("transient_context", _PATH)
tc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tc)


def _spread(hold: int, seeds: int = 40) -> float:
    means = [
        statistics.mean(abs(tc._held_delta(a, hold=hold, seed=s)) for s in range(seeds))
        for a in tc.AMPS
    ]
    return max(means) - min(means)


def _retention(hold: int, seeds: int = 40) -> float:
    hits = sum((tc._held_delta(a, hold=hold, seed=s) > 0) == (a > 0)
               for a in tc.AMPS for s in range(seeds))
    return hits / (len(tc.AMPS) * seeds)


class TestTheTransientWindow:
    def test_depth_and_sign_both_present_in_the_window(self) -> None:
        """At a transient hold (10) the |delta| still separates by input amplitude (depth) AND
        the sign is fully settled (bit) — a read here carries both."""
        assert _spread(10) > 0.2, _spread(10)
        assert _retention(10) > 0.95

    def test_the_endpoint_has_erased_the_depth(self) -> None:
        """By the endpoint the basin has collapsed |delta| to one value — depth gone, bit kept."""
        assert _spread(160) < 0.02, _spread(160)
        assert _retention(160) > 0.95

    def test_depth_decays_monotonically_into_the_hold(self) -> None:
        assert _spread(0) > _spread(20) > _spread(80)

    def test_reproducible(self) -> None:
        assert tc._held_delta(0.5, hold=10, seed=3) == tc._held_delta(0.5, hold=10, seed=3)
