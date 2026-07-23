"""The recursive wall: the transient past carries depth, but a latched response re-erases it.

Pins that the past differential read in the window separates by the input's analog magnitude
(depth is readable) while a bistable response driven from it follows only the SIGN — so context
stays a continuous readout, not a usable latched gate. The full MI table lives in
`state/communication/transient_gate.py` and RESULTS.
"""

from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "transient_gate.py"
_spec = importlib.util.spec_from_file_location("transient_gate", _PATH)
tg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tg)


class TestTheRecursiveWall:
    def test_the_transient_past_carries_depth(self) -> None:
        """Read in the window (hold 10), the past |delta| separates by its input magnitude."""
        means = [
            statistics.mean(abs(tg._past_delta(a, +1, read_hold=10, seed=s)) for s in range(30))
            for a in tg.AMPS
        ]
        assert means[-1] - means[0] > 0.2, means

    def test_the_latched_response_follows_only_the_sign(self) -> None:
        """For a fixed past sign, the response bit is the same across every past magnitude — the
        latch flattened the depth away, so it carries none of it."""
        for sign in (+1, -1):
            outs = {
                a: statistics.mode(
                    tg._response(tg._past_delta(a, sign, read_hold=10, seed=s), scale=0.15,
                                 seed=s * 7 + 2)
                    for s in range(30)
                )
                for a in tg.AMPS
            }
            assert len(set(outs.values())) == 1, (sign, outs)  # one response for all depths

    def test_reproducible(self) -> None:
        d = tg._past_delta(0.5, +1, read_hold=10, seed=3)
        assert tg._response(d, scale=0.15, seed=5) == tg._response(d, scale=0.15, seed=5)
