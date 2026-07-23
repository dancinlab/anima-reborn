"""The wall behind the door: the retention<->depth trade reappears at the composition step.

`rate_code.py` showed the population holds AND consumes analog depth. This re-audits whether that
held depth can ACT on a current write (context) via an additive gate — and pins the measured wall:
a GRADED current population reads the held past's depth (above its shuffled floor) but has no
reliable sign of its own; a SATURATED current keeps its sign but goes deaf to the past. No current
strength buys both. The full sweep + nulls live in `state/communication/context_rate_gate.py` and
RESULTS. These are the cheap invariants that guard the wall from quietly becoming a "context works".
"""

from __future__ import annotations

import importlib.util
import random
import statistics
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "context_rate_gate.py"
_spec = importlib.util.spec_from_file_location("context_rate_gate", _PATH)
cg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cg)


def _rows(cur_scale: float):
    return cg._trials(cur_scale)


class TestTradeReappearsAtComposition:
    def test_a_graded_current_reads_the_past_depth(self) -> None:
        """At a small (graded) current write, the read carries the held past's depth above floor."""
        obs, floor = cg._mi_depth(_rows(0.01), shuffle_seed=5)
        assert obs > floor + 0.1, (obs, floor)

    def test_but_the_graded_current_has_no_sign_of_its_own(self) -> None:
        """The same graded current cannot reliably carry its OWN symbol — fidelity is near a coin."""
        assert cg._current_fidelity(0.01) < 0.7

    def test_a_saturated_current_keeps_its_sign_but_goes_deaf(self) -> None:
        """At a strong (saturated) current write, the sign survives but the past nudge is unreadable."""
        obs, floor = cg._mi_depth(_rows(0.08), shuffle_seed=7)
        assert cg._current_fidelity(0.08) >= 0.95
        assert obs <= floor + 0.05, (obs, floor)

    def test_no_window_keeps_both(self) -> None:
        """Across the swept current strengths, none reads the past above floor AND keeps the sign."""
        window = [
            cs for cs in cg.CUR_SCALES
            if cg._current_fidelity(cs) >= 0.95
            and (lambda of: of[0] > of[1] + 0.05)(cg._mi_depth(_rows(cs), shuffle_seed=3))
        ]
        assert window == [], window

    def test_the_read_past_is_history_not_leak(self) -> None:
        """The past-depth signal in the graded current vanishes when the history is shuffled."""
        rows = _rows(0.01)
        obs, floor = cg._mi_depth(rows, shuffle_seed=9)
        rng = random.Random(2)
        labels = [ai for ai, _ in rows]
        reads = [r for _, r in rows]
        rng.shuffle(labels)
        shuffled, _ = cg._mi_depth(list(zip(labels, reads)), shuffle_seed=9)
        assert shuffled < obs - 0.1, (obs, shuffled)

    def test_reproducible(self) -> None:
        pm = cg._past_mean(0.5, +1, seed=11)
        a = cg._gated_read(0.5, +1, pm, cur_scale=0.02, seed=13)
        b = cg._gated_read(0.5, +1, pm, cur_scale=0.02, seed=13)
        assert a == b
