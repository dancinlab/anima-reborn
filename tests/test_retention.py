"""The 3-bit cell's retention through silence — the measure-first gate for time accumulation.

Pins that the 6-unit PAIRS cell holds all three latch bits indefinitely under a deaf hold,
while pure leak and an acyclic wiring die to chance — so the sequence engine (the first new
part) can rely on a measured, flat hold rather than a guessed one.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "retention.py"
_spec = importlib.util.spec_from_file_location("retention", _PATH)
ret = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ret)


class TestRetention:
    def test_the_deaf_hold_keeps_all_three_bits_flat(self) -> None:
        near, _ = ret._joint("deaf", 0)
        far, per_bit = ret._joint("deaf", 480)
        assert near > 0.99
        assert far > 0.99, far
        assert all(b > 0.99 for b in per_bit), per_bit  # every latch, not just one

    def test_pure_leak_dies(self) -> None:
        """Coupling 0 with no drive is a time-constant decay, so the held word is lost —
        the hold is active recurrence, not slow relaxation."""
        joint, _ = ret._joint("leak", 120)
        assert joint <= 0.2, joint

    def test_an_acyclic_wiring_cannot_hold(self) -> None:
        """Feedforward has no cycle to hold a state, so it falls to chance — recurrence is
        what buys the hold (`silence.py`'s result, at 3-bit width)."""
        joint, _ = ret._joint("feedforward", 120)
        assert joint <= 0.2, joint

    def test_the_word_reads_are_reproducible(self) -> None:
        a = ret.hold_word(5, seed=3, silence=240, mode="deaf")
        b = ret.hold_word(5, seed=3, silence=240, mode="deaf")
        assert a == b == 5
