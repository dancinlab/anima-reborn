"""Calibrate the 3-bit PAIRS channel before its constants are frozen.

Run from the repo root:

    PYTHONPATH=src python state/communication/conversation_channel.py

The free-conversation tab (`대화`, its own commit) wants a richer channel than the 1-bit
ring: `Wiring.PAIRS` (6 units, 3 odd pairs, `chain=0.2`), proven in `capacity.py` to hold
3 bits AND measure as integrated. But `channel-before-carrier`/`measure-first` forbid
freezing TELL/HOLD constants for it by analogy with the 1-bit ring — the wire's own
fidelity is the human's accuracy ceiling and must be MEASURED here first, so a human's
0.85 is never read against an imaginary 1.0.

What this measures, for a sweep of TELL/HOLD candidates:

- **per-bit fidelity** = P(decoded latch bit == driven bit), each of the 3 pairs, over all
  8 symbols and many seeds. Each pair is addressed only through its differential
  `v[2j] - v[2j+1]` (the common mode dies in silence), so the bit is `sign` of that.
- **joint fidelity** = P(all 3 bits correct) = the exact-symbol reproducibility, the number
  `capacity.py` reported as ~88%.
- **the deaf null**: coupling 1.0 for the whole run makes the drive bit-unreachable, so the
  decoded word must carry ~0 information about the symbol — the arm proving the channel was
  in the path. Reported as the deaf joint fidelity (should sit at 1/8 chance).

Nothing is frozen here; this prints the numbers the `대화` commit will pin its constants to.
"""

from __future__ import annotations

import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

BITS = 3
UNITS = 2 * BITS
CHAIN = 0.2
SEEDS = 200


def _drive_for(symbol: int) -> tuple[float, ...]:
    """Per-unit drive: pair j is pushed to sign +/- by bit j of the symbol."""
    drive: list[float] = []
    for j in range(BITS):
        bit = (symbol >> j) & 1
        drive += [0.8, -0.8] if bit == 0 else [-0.8, 0.8]
    return tuple(drive)


def pairs_word(symbol: int, *, seed: int, tell: int, hold: int, deaf: bool = False) -> int:
    """Drive the 3 pairs for `symbol`, hold, and read the 3 differential sign bits."""
    engine = CoupledEngine(
        units=UNITS, wiring=Wiring.PAIRS, chain=CHAIN,
        rhythm=FIXED if deaf else ALTERNATING,
        drive=_drive_for(symbol), seed=seed, initial=(0.0,) * UNITS,
    )
    engine.run(tell)
    engine.rhythm = FIXED
    engine.drive = 0.0
    values = engine.run(hold).values
    word = 0
    for j in range(BITS):
        bit = 0 if (values[2 * j] - values[2 * j + 1]) > 0 else 1
        word |= bit << j
    return word


def _fidelity(*, tell: int, hold: int, deaf: bool = False) -> tuple[list[float], float]:
    """Per-bit and joint fidelity over all 8 symbols x SEEDS."""
    per_bit = [0, 0, 0]
    joint = 0
    total = 0
    for symbol in range(8):
        for seed in range(SEEDS):
            word = pairs_word(symbol, seed=seed * 13 + 1, tell=tell, hold=hold, deaf=deaf)
            total += 1
            if word == symbol:
                joint += 1
            for j in range(BITS):
                if ((word >> j) & 1) == ((symbol >> j) & 1):
                    per_bit[j] += 1
    return [b / total for b in per_bit], joint / total


def main() -> None:
    print("3-bit PAIRS channel calibration — 6 units, 3 odd pairs, chain=0.2")
    print(f"{8 * SEEDS} runs per cell (8 symbols x {SEEDS} seeds), ALTERNATING tell / FIXED hold\n")
    print(f"{'tell':>5}{'hold':>6}{'  bit0':>8}{'bit1':>8}{'bit2':>8}{'  joint':>9}   verdict")
    print("-" * 60)

    best = None
    for tell in (200, 300, 400, 600):
        for hold in (120, 240):
            per_bit, joint = _fidelity(tell=tell, hold=hold)
            worst_bit = min(per_bit)
            note = "3-bit usable" if worst_bit >= 0.95 else "a bit is lossy"
            print(f"{tell:>5}{hold:>6}"
                  f"{per_bit[0]:>8.3f}{per_bit[1]:>8.3f}{per_bit[2]:>8.3f}"
                  f"{joint:>9.3f}   {note}")
            if worst_bit >= 0.95 and (best is None or (tell, hold) < best[:2]):
                best = (tell, hold, per_bit, joint)

    # The deaf null at a representative setting — the channel must be in the path.
    _, deaf_joint = _fidelity(tell=400, hold=240, deaf=True)
    print(f"\n  deaf (coupling 1.0, tell=400 hold=240): joint {deaf_joint:.3f} "
          f"(1/8 = {1/8:.3f} chance — drive bit-unreachable)")

    if best is None:
        print("\n  NO setting reached 0.95 on every bit — the 3-bit channel is not clean")
        print("  enough at these envelopes; the 대화 commit must widen TELL or reconsider.")
    else:
        tell, hold, per_bit, joint = best
        print(f"\n  cheapest usable envelope: TELL={tell} HOLD={hold} — "
              f"per-bit {min(per_bit):.3f}..{max(per_bit):.3f}, joint {joint:.3f}")
        print(f"  this joint fidelity is the human's accuracy CEILING and must be printed "
              f"beside\n  any 대화 recovery number — a human cannot beat the wire.")


if __name__ == "__main__":
    main()
