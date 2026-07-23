"""The SequenceEngine shift chain — the shipped working-memory engine.

Pins order preservation through the clean bridge, the deaf-bridge transport null (default
off, so the engine stays bit-identical), the passive auto-tick, and the describe() shape the
viewer draws. The forgetting curve and its statistical nulls live in
`state/communication/accumulation.py`, which drives THIS engine.
"""

from __future__ import annotations

from anima_reborn.sequence import BITS, CELLS, WRITE_PERIOD, SequenceEngine


class TestTheShiftChain:
    def test_it_holds_the_last_k_symbols_in_order(self) -> None:
        hits = 0
        total = 0
        for s in range(40):
            engine = SequenceEngine(seed=s)
            stream = [(s * 3 + i * 5) % 8 for i in range(CELLS + 3)]
            for sym in stream:
                engine.turn(sym)
            tape = engine.tape()
            for j in range(CELLS):
                total += 1
                if tape[j] == stream[-1 - j]:
                    hits += 1
        assert hits / total > 0.98, hits / total  # the wire is measured-clean (1.000)

    def test_the_deaf_bridge_delivers_nothing_past_cell_zero(self) -> None:
        hits = 0
        total = 0
        for s in range(40):
            engine = SequenceEngine(seed=s, deaf_bridge=True)
            stream = [(s * 7 + i * 3) % 8 for i in range(CELLS + 3)]
            for sym in stream:
                engine.turn(sym)
            tape = engine.tape()
            assert tape[0] == stream[-1]  # cell 0 is always written, never deaf
            for j in range(1, CELLS):
                total += 1
                if tape[j] == stream[-1 - j]:
                    hits += 1
        assert hits / total < 0.3, hits / total  # ~1/8 chance past the deaf bridge

    def test_the_deaf_bridge_defaults_off(self) -> None:
        import inspect

        sig = inspect.signature(SequenceEngine.__init__)
        assert sig.parameters["deaf_bridge"].default is False

    def test_the_tape_is_reproducible(self) -> None:
        def run() -> list:
            e = SequenceEngine(seed=9)
            for sym in (1, 4, 7, 2, 5, 0, 3):
                e.turn(sym)
            return e.tape()

        assert run() == run()


class TestTheViewerContract:
    def test_step_auto_advances_on_the_write_period(self) -> None:
        engine = SequenceEngine(seed=1)
        assert engine.describe()["turns"] == 0
        for _ in range(WRITE_PERIOD):
            engine.step()
        assert engine.describe()["turns"] == 1

    def test_describe_is_drawable(self) -> None:
        engine = SequenceEngine(seed=2)
        for _ in range(WRITE_PERIOD * (CELLS + 1)):
            engine.step()
        frame = engine.describe()
        assert frame["held_bits"] == BITS * CELLS
        assert frame["capacity_bits"] == BITS * CELLS
        assert len(frame["front_values"]) == 2 * BITS
        assert all(0 <= c["word"] <= 7 and 0 <= c["age"] < CELLS for c in frame["cells"])
