"""The retention <-> analog-depth wall: depth survives the drive but the basin erases it.

Pins the measured wall — the held |delta| separates by input amplitude right after the drive
(depth present) but collapses to a single attractor value after a retaining hold (depth erased),
while an acyclic wiring cannot hold at all. The full MI curve + nulls live in
`state/communication/depth_hold.py` and RESULTS.
"""

from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "depth_hold.py"
_spec = importlib.util.spec_from_file_location("depth_hold", _PATH)
dh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dh)


def _by_amp(coupling: float, hold: int, seeds: int = 30) -> dict[float, float]:
    return {
        a: statistics.mean(abs(dh._held_delta(a, coupling=coupling, hold=hold, seed=s))
                           for s in range(seeds))
        for a in dh.AMPS
    }


class TestTheWall:
    def test_depth_survives_the_drive(self) -> None:
        """Right after the drive the held |delta| tracks the input amplitude — the analog depth
        is there, monotone and well separated from the seed noise."""
        m = _by_amp(1.0, hold=0)
        lo, hi = m[dh.AMPS[0]], m[dh.AMPS[-1]]
        assert hi - lo > 0.3, m  # the a=0.2..0.8 gap dwarfs the ~0.05 seed spread
        assert m[0.2] < m[0.5] < m[0.8]  # monotone in the input

    def test_the_retaining_hold_erases_depth(self) -> None:
        """After a hold at coupling 1.0 the |delta| collapses to one attractor value, the same
        for every input amplitude — the basin that retains the bit erases the depth."""
        m = _by_amp(1.0, hold=dh.HOLD_TICKS)
        spread = max(m.values()) - min(m.values())
        assert spread < 0.02, m  # flat across a: depth gone

    def test_the_sign_is_retained_while_depth_is_lost(self) -> None:
        hits = sum(
            (dh._held_delta(a, coupling=1.0, hold=dh.HOLD_TICKS, seed=s) > 0) == (a > 0)
            for a in dh.AMPS for s in range(20)
        )
        assert hits >= 95  # out of 100 — the bit survives even as depth does not

    def test_an_acyclic_wiring_cannot_hold(self) -> None:
        hits = sum(
            (dh._held_delta(a, coupling=1.0, hold=dh.HOLD_TICKS, seed=s, feedforward=True) > 0)
            == (a > 0)
            for a in dh.AMPS for s in range(20)
        )
        assert hits <= 65  # ~chance: no cycle, no hold

    def test_reproducible(self) -> None:
        assert dh._held_delta(0.5, coupling=0.7, hold=120, seed=3) == \
            dh._held_delta(0.5, coupling=0.7, hold=120, seed=3)
