"""Phase-0 for time accumulation: how long does a 3-bit cell HOLD its bits through silence?

Run from the repo root:

    PYTHONPATH=src python state/communication/retention.py

The delegated design for "engine parts to reach the goal" (both models converged,
`state/lab/2026-07-23-new-parts-*.md`) is: the width walls (ring = 1 bit; PAIRS = units/2;
Φ unmeasurable past ~6 units) are real, but the TIME axis has hit no wall yet. So the first
new part is TIME ACCUMULATION — reuse the proven 6-unit / 3-bit PAIRS cell over ordered turns,
holding each turn's bits IN THE ENGINE across a silent gap. Before designing that shift chain,
`measure-first` demands the number it hangs on: the cell's RETENTION curve.

`silence.py` already showed the 1-bit ring holds its single bit through silence indefinitely
(flat to 480 ticks) while every acyclic wiring and pure leak dies. This asks the same of the
3-bit cell — do ALL three differential latches survive silence, and for how long — so the
sequence engine's commit-window can be set to a measured hold time, not a guessed one.

The hold is the DEAF autonomous ring (coupling 1.0, drive bit-unreachable): what survives owes
nothing to ongoing input. Two nulls prove the hold is the recurrence's, not an artefact:
- **leak** (coupling 0, drive 0): pure time-constant decay — must die, proving the cell holds
  ACTIVELY, not by a slow relaxation.
- **feedforward** (acyclic wiring): no cycle to hold a state — must fall to its fixed point,
  proving recurrence is what buys the hold (`silence.py`'s result, at 3-bit width).
"""

from __future__ import annotations

import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Rhythm, Wiring

BITS = 3
UNITS = 2 * BITS
CHAIN = 0.2
TELL = 200
SEEDS = 40
SILENCES = (0, 60, 120, 240, 480)


def _drive_for(symbol: int) -> tuple[float, ...]:
    drive: list[float] = []
    for j in range(BITS):
        bit = (symbol >> j) & 1
        drive += [0.8, -0.8] if bit == 0 else [-0.8, 0.8]
    return tuple(drive)


def hold_word(symbol: int, *, seed: int, silence: int, mode: str = "deaf") -> int:
    """Tell the cell a 3-bit symbol, then hold it deaf (or leak / feedforward) for `silence`
    ticks, and read the 3 differential sign bits."""
    wiring = Wiring.FEEDFORWARD if mode == "feedforward" else Wiring.PAIRS
    engine = CoupledEngine(
        units=UNITS, wiring=wiring, chain=CHAIN if wiring is Wiring.PAIRS else 0.0,
        rhythm=ALTERNATING, drive=_drive_for(symbol), seed=seed, initial=(0.0,) * UNITS,
    )
    engine.run(TELL)
    # The hold phase: deaf = autonomous ring (coupling 1.0); leak = no partner, pure decay.
    engine.rhythm = Rhythm(coupling=0.0) if mode == "leak" else FIXED
    engine.drive = 0.0
    if silence > 0:
        engine.run(silence)
    values = engine.values
    word = 0
    for j in range(BITS):
        bit = 0 if (values[2 * j] - values[2 * j + 1]) > 0 else 1
        word |= bit << j
    return word


def _joint(mode: str, silence: int) -> tuple[float, list[float]]:
    """Joint (all-3-bit) and per-bit retention over 8 symbols x SEEDS."""
    joint = 0
    per_bit = [0, 0, 0]
    total = 0
    for symbol in range(8):
        for seed in range(SEEDS):
            word = hold_word(symbol, seed=seed * 13 + 1, silence=silence, mode=mode)
            total += 1
            if word == symbol:
                joint += 1
            for j in range(BITS):
                if ((word >> j) & 1) == ((symbol >> j) & 1):
                    per_bit[j] += 1
    return joint / total, [b / total for b in per_bit]


def main() -> None:
    print("3-bit cell retention — does a 6-unit PAIRS cell hold its 3 bits through silence?")
    print(f"tell {TELL}, then hold; 8 symbols x {SEEDS} seeds per cell; joint = all 3 bits kept\n")
    print(f"{'silence':>8}{'deaf(hold)':>12}{'leak':>9}{'feedforward':>13}")
    print("-" * 44)
    curves: dict[str, list[float]] = {"deaf": [], "leak": [], "feedforward": []}
    per_bit_deaf: dict[int, list[float]] = {}
    for silence in SILENCES:
        row = {}
        for mode in ("deaf", "leak", "feedforward"):
            j, pb = _joint(mode, silence)
            row[mode] = j
            curves[mode].append(j)
            if mode == "deaf":
                per_bit_deaf[silence] = pb
        print(f"{silence:>8}{row['deaf']:>12.3f}{row['leak']:>9.3f}{row['feedforward']:>13.3f}")

    flat = abs(curves["deaf"][-1] - curves["deaf"][1]) < 0.05 and curves["deaf"][-1] > 0.9
    print(f"\n  per-bit deaf hold at {SILENCES[-1]} ticks: "
          f"{'  '.join(f'{b:.3f}' for b in per_bit_deaf[SILENCES[-1]])} "
          f"(all three latches, not just one)")
    print(f"  deaf curve: {'  '.join(f'{v:.3f}' for v in curves['deaf'])}")
    print(f"  leak dies to {curves['leak'][-1]:.3f}, feedforward to {curves['feedforward'][-1]:.3f} "
          f"(chance 1/8 = 0.125)")
    if flat:
        print(f"\n  VERDICT: the 3-bit cell holds all 3 bits through {SILENCES[-1]} ticks of silence,")
        print(f"  flat, while leak and feedforward die — recurrence buys the hold, at 3-bit width.")
        print(f"  Time accumulation is viable: a cell can carry its bits across a silent gap while")
        print(f"  the next turn is processed. The commit-window may be as short as the tell phase.")
    else:
        print(f"\n  VERDICT: the hold is NOT flat — retention limits the sequence design; "
              f"see the curve.")


if __name__ == "__main__":
    main()
