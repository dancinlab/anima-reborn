"""The door reaches context: multiplicative modulation delivers the held past into the current write.

`context_rate_gate.py` measured that an ADDITIVE gate cannot deliver the held past's depth into the
current read without erasing the current symbol (no window). This pins the escape: a MULTIPLICATIVE
gate (the past scales the current with a positive gain, so it cannot flip the sign) opens a window —
the current read carries the past depth above floor WHILE both current signs survive, a shuffled
past kills it, and — the decisive control — with no current symbol (a_cur=0) the past collapses to
floor, proving it reaches the read only by MODULATING the current, not as an independent input. Full
sweep + nulls live in `state/communication/context_modulation.py` and RESULTS.
"""

from __future__ import annotations

import importlib.util
import random
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "context_modulation.py"
_spec = importlib.util.spec_from_file_location("context_modulation", _PATH)
cm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cm)

WINDOW = 0.04   # the base current strength where the window opens (RESULTS)


class TestDoorReachesContext:
    def test_the_past_depth_reaches_the_read(self) -> None:
        """At the window base strength, the read carries the held past's depth above floor."""
        obs, floor = cm._mi_depth(cm._trials(WINDOW), shuffle_seed=5)
        assert obs > floor + 0.1, (obs, floor)

    def test_both_current_signs_survive(self) -> None:
        """The multiplicative gain never flips the sign — the current symbol survives for both."""
        assert cm._fidelity(WINDOW) >= 0.95

    def test_additive_gating_had_no_such_window(self) -> None:
        """Contrast the sibling additive gate: a graded current (readable past) has fidelity ~coin,
        so no additive base strength gives both. Here the SAME readable regime keeps fidelity 1."""
        obs, floor = cm._mi_depth(cm._trials(WINDOW), shuffle_seed=6)
        assert obs > floor + 0.1 and cm._fidelity(WINDOW) >= 0.95

    def test_past_reaches_the_read_only_through_the_current(self) -> None:
        """The decisive modulation control: with NO current symbol (a_cur=0) the past has nothing to
        scale, so its influence collapses to floor — it is not an independent additive input."""
        none, floor0 = cm._mi_depth(cm._trials(WINDOW, a_cur=0.0), shuffle_seed=7)
        some, _ = cm._mi_depth(cm._trials(WINDOW, a_cur=cm.A_CUR), shuffle_seed=7)
        assert none <= floor0 + 0.05, (none, floor0)   # no current -> past collapses
        assert some > none + 0.1, (some, none)          # current present -> past reaches the read

    def test_the_read_past_is_history_not_leak(self) -> None:
        """The past-depth signal vanishes when the history is shuffled."""
        rows = cm._trials(WINDOW)
        obs, _ = cm._mi_depth(rows, shuffle_seed=9)
        rng = random.Random(2)
        labels = [ai for ai, _ in rows]
        reads = [r for _, r in rows]
        rng.shuffle(labels)
        shuffled, _ = cm._mi_depth(list(zip(labels, reads)), shuffle_seed=9)
        assert shuffled < obs - 0.1, (obs, shuffled)

    def test_reproducible(self) -> None:
        pm = cm._past_mean(0.5, +1, seed=11)
        a = cm._mod_read(0.5, +1, pm, cur_base=WINDOW, seed=13)
        b = cm._mod_read(0.5, +1, pm, cur_base=WINDOW, seed=13)
        assert a == b
