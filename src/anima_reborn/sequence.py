"""A shift chain of gated cells — the engine's working memory of the last K symbols.

The first new part toward the goal (both delegated designs converged,
`state/lab/2026-07-23-new-parts-*.md`; prototyped and measured in
`state/communication/accumulation.py`). The width walls are real (ring = 1 bit; PAIRS =
units/2; Φ unmeasurable past ~6 units), but the TIME axis has hit none, so this composes K
proven 6-unit / 3-bit PAIRS cells into a shift register: each turn a new symbol is written to
cell 0 and every held word is bridged one step down the chain, oldest off the end. The chain
then remembers the last K symbols IN ORDER.

Each cell is integrated on its own (6 units, exact Φ — `capacity.py`) and holds its bits
through the inter-turn gap (`retention.py`, flat to 480 ticks). The inter-cell BRIDGE reuses
the measured-clean `channel(bits=3)` wire and is a TRANSPORT claim, never an integration claim
— the whole tape is not asserted to be one integrated thing. What this buys over a single wide
substrate is the two properties a moment cannot have: MEMORY (past turns held by the engine's
own dynamics) and ORDER (a bag of bits would fail the time-shift null). It is not language;
`I(X;Y) <= 3 bits` stays bound every moment.

`state/communication/accumulation.py` drives THIS engine to re-derive the forgetting curve and
its nulls (a script measures the shipped engine, not a copy of it).
"""

from __future__ import annotations

import random
from typing import Any

from .dialogue import channel_trace

__all__ = ["BITS", "CELLS", "SequenceEngine"]

BITS = 3
UNITS = 2 * BITS
CELLS = 4          # tape length K — the chain remembers the last 4 symbols
WRITE_PERIOD = 12  # viewer ticks between turns, so a new symbol lands ~1.5 s apart at 8 Hz


def _decode(values: tuple[float, ...]) -> int:
    word = 0
    for j in range(BITS):
        word |= (0 if (values[2 * j] - values[2 * j + 1]) > 0 else 1) << j
    return word


class SequenceEngine:
    """K gated cells in a shift register. A passive viewer engine: `step()` auto-advances
    (writing a new symbol every WRITE_PERIOD ticks and shifting), `reset()` starts fresh.
    `turn()` is the unit the accumulation measurement drives directly."""

    def __init__(self, *, seed: int | None = None, deaf_bridge: bool = False) -> None:
        self._seed = 0 if seed is None else int(seed)
        # `deaf_bridge` is the transport null: the inter-cell bridge's drive is made
        # bit-unreachable (coupling 1.0), so nothing is delivered past cell 0. Default False
        # leaves the engine bit-identical (`default-stays-exact`); the write to cell 0 is never
        # deaf, so cell 0 always carries the newest symbol.
        self._deaf_bridge = bool(deaf_bridge)
        self.reset()

    def reset(self) -> None:
        self._rng = random.Random(self._seed)
        self._op = 0
        self._ticks = 0
        self._turns = 0
        self._last_symbol: int | None = None
        # Each cell: {"values": tuple[6] , "word": int} or None (empty).
        self._cells: list[dict[str, Any] | None] = [None] * CELLS

    # -- the mechanism the measurement drives ------------------------------------------

    def _hold(self, word: int, *, deaf: bool = False) -> dict[str, Any]:
        """Drive a fresh cell with `word` over the clean wire and hold it; return its held
        state and decoded word. A fresh engine (origin start) matches the calibration. `deaf`
        makes the drive bit-unreachable — the transport null."""
        self._op += 1
        trace = channel_trace(word, seed=self._seed * 100_003 + self._op, deaf=deaf, bits=BITS)
        values = tuple(trace[-1])
        return {"values": values, "word": _decode(values)}

    def turn(self, symbol: int) -> None:
        """One turn: shift every held word one cell down (oldest off the end), then write the
        new symbol into cell 0. This is exactly what the accumulation prototype measured."""
        for k in range(CELLS - 1, 0, -1):
            src = self._cells[k - 1]
            self._cells[k] = None if src is None else self._hold(src["word"], deaf=self._deaf_bridge)
        self._cells[0] = self._hold(symbol)  # the write is never deaf
        self._last_symbol = symbol
        self._turns += 1

    def tape(self) -> list[int | None]:
        """The K decoded words, newest first — what the chain currently remembers."""
        return [None if c is None else c["word"] for c in self._cells]

    # -- viewer engine contract --------------------------------------------------------

    def step(self) -> "SequenceEngine":
        self._ticks += 1
        if self._ticks % WRITE_PERIOD == 0:
            self.turn(self._rng.randrange(8))
        return self

    def describe(self) -> dict[str, Any]:
        cells = []
        for age, cell in enumerate(self._cells):
            if cell is not None:
                cells.append({"age": age, "word": cell["word"]})
        held_bits = BITS * sum(1 for c in self._cells if c is not None)
        first = next((c for c in self._cells if c is not None), None)
        return {
            "cells": cells,
            "held_bits": held_bits,
            "capacity_bits": BITS * CELLS,
            "turns": self._turns,
            "last_symbol": self._last_symbol,
            "front_values": [round(v, 4) for v in first["values"]] if first else [],
            "ticks_to_next": WRITE_PERIOD - (self._ticks % WRITE_PERIOD),
        }
