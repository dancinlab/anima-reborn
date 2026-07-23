"""The 3-bit PAIRS channel added for the free-conversation tab, and its 1-bit exactness.

`channel`/`channel_trace` gained a `bits=` parameter. `bits=1` (default) MUST stay
byte-for-byte the published 1-bit ring — the reproducible half's numbers were measured on
it (`default-stays-exact`). `bits=3` is the proven `Wiring.PAIRS` substrate, calibrated in
`state/communication/conversation_channel.py`; these pin its driven-decode fidelity and its
deaf null so the channel's own fidelity (the human's accuracy ceiling) cannot silently rot.
"""

from __future__ import annotations

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring
from anima_reborn.dialogue import HOLD, TELL, channel, channel_trace


def _old_one_bit_channel(signal: int, *, seed: int, deaf: bool = False) -> int:
    """The 1-bit ring exactly as it was before `bits=` existed — the golden reference."""
    drive = (0.8, -0.8) if signal == 0 else (-0.8, 0.8)
    engine = CoupledEngine(
        units=2, wiring=Wiring.RING,
        rhythm=FIXED if deaf else ALTERNATING,
        drive=drive, seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    values = engine.run(HOLD).values
    return 0 if (values[0] - values[1]) > 0 else 1


class TestDefaultStaysExact:
    def test_one_bit_default_is_byte_for_byte_the_published_channel(self) -> None:
        for seed in range(300):
            for signal in (0, 1):
                for deaf in (False, True):
                    assert channel(signal, seed=seed, deaf=deaf) == _old_one_bit_channel(
                        signal, seed=seed, deaf=deaf
                    ), (seed, signal, deaf)

    def test_one_bit_is_the_default(self) -> None:
        # A single latch: two possible words, and the trace is 2 units wide.
        assert channel(1, seed=1) in (0, 1)
        assert len(channel_trace(0, seed=1)[-1]) == 2


class TestThreeBitChannel:
    def test_driven_decode_is_clean(self) -> None:
        """Calibrated at joint 1.000 — a strongly driven bistable latch from origin settles
        deterministically, so the wire is not what limits a human's recovery."""
        hits = 0
        total = 0
        for symbol in range(8):
            for seed in range(40):
                total += 1
                if channel(symbol, seed=seed * 13 + 1, bits=3) == symbol:
                    hits += 1
        assert hits / total >= 0.99, hits / total

    def test_the_trace_is_six_units_wide(self) -> None:
        trace = channel_trace(5, seed=3, bits=3)
        assert len(trace) == HOLD
        assert all(len(row) == 6 for row in trace)

    def test_deaf_carries_no_symbol(self) -> None:
        """Coupling 1.0 makes the drive bit-unreachable, so the decoded word cannot track
        the symbol — the null proving the channel was in the path (calibrated at 1/8)."""
        hits = 0
        total = 0
        for symbol in range(8):
            for seed in range(40):
                total += 1
                if channel(symbol, seed=seed * 13 + 1, bits=3, deaf=True) == symbol:
                    hits += 1
        assert hits / total <= 0.30, hits / total

    def test_a_bad_bit_count_is_rejected(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            channel(0, seed=1, bits=2)
