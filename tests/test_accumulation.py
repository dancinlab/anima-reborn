"""Time accumulation: the K-cell chain holds the last K symbols in order.

Pins the shift chain's core (order preserved through clean bridges), the deaf-bridge null
(nothing delivered past cell 0), the reproducibility, and that the hold is a self-correcting
basin — not a frozen Python variable (sol's control that the state lives in the engine).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "accumulation.py"
_spec = importlib.util.spec_from_file_location("accumulation", _PATH)
acc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(acc)


class TestTheShiftChain:
    def test_it_holds_the_last_k_symbols_in_order(self) -> None:
        """The clean bridge preserves each word, so the tape is exactly the last K symbols,
        newest first — memory AND order, not a bag of bits."""
        hits = 0
        total = 0
        for s in range(40):
            stream = [(s * 3 + i * 5) % 8 for i in range(acc.CELLS + 3)]
            tape = acc.run_chain(stream, seed=s)
            for j in range(acc.CELLS):
                total += 1
                if tape[j] == stream[-1 - j]:
                    hits += 1
        assert hits / total > 0.98, hits / total  # the wire is measured-clean (1.000)

    def test_the_deaf_bridge_delivers_nothing_past_cell_zero(self) -> None:
        """With the bridge deaf, ages >= 1 cannot track the symbol — the bridge is what
        carries the word, scored before crediting what a later cell holds."""
        hits = 0
        total = 0
        for s in range(40):
            stream = [(s * 7 + i * 3) % 8 for i in range(acc.CELLS + 3)]
            tape = acc.run_chain(stream, seed=s, deaf_bridge=True)
            for j in range(1, acc.CELLS):
                total += 1
                if tape[j] == stream[-1 - j]:
                    hits += 1
        assert hits / total < 0.3, hits / total  # ~1/8 chance, not the live ~1.0

    def test_it_is_reproducible(self) -> None:
        stream = [1, 4, 7, 2, 5, 0, 3]
        assert acc.run_chain(stream, seed=9) == acc.run_chain(stream, seed=9)


class TestTheHoldIsABasin:
    def test_a_small_jolt_self_corrects(self) -> None:
        """The state lives in the engine's dynamics: a small perturbation is pulled back to
        the latch, which a frozen stored number could not do."""
        hits = sum(
            acc._perturbation_hold(sym, seed=sym * 17 + s, jolt=0.3) == sym
            for sym in range(8) for s in range(10)
        )
        assert hits >= 75, hits  # out of 80

    def test_a_large_jolt_can_cross_the_barrier(self) -> None:
        """The basin has a finite barrier — a big enough jolt flips it. That it CAN be
        flipped is the proof it is a dynamical basin, not an infinitely rigid variable."""
        clean = sum(
            acc._perturbation_hold(sym, seed=sym * 17 + s, jolt=0.0) == sym
            for sym in range(8) for s in range(10)
        )
        big = sum(
            acc._perturbation_hold(sym, seed=sym * 17 + s, jolt=0.9) == sym
            for sym in range(8) for s in range(10)
        )
        assert clean >= 78
        assert big < clean
