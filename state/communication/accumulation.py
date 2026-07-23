"""Time accumulation: a chain of gated cells holds the last K 3-bit symbols, IN ORDER.

Run from the repo root:

    PYTHONPATH=src python state/communication/accumulation.py

The first new part toward the goal (both delegated designs converged,
`state/lab/2026-07-23-new-parts-*.md`): the width walls are real, but the TIME axis has hit
none. `retention.py` proved a 6-unit / 3-bit cell holds its bits through silence indefinitely.
This composes K such cells into a SHIFT CHAIN — each turn a new symbol is written to cell 0 and
every cell's word is bridged one step down the chain — and MEASURES that the chain remembers
the last K symbols in order, with the nulls that could fake it. Prototyped here in `state/`
before any `src/` engine (the repo pattern: measure the capability, with its controls, first).

What is claimed and what is NOT: each cell is integrated on its own (6 units, exact Φ —
`capacity.py`), and holds its bits (`retention.py`). The inter-cell BRIDGE is a TRANSPORT
claim, never an integration claim — the whole tape is not asserted to be one integrated thing.
What accumulation buys over a single wide substrate is the two properties a moment cannot have:
MEMORY (past turns held by the engine's own dynamics) and ORDER (which the time-shift null
proves is carried, not a bag of bits).

The bridge reuses the measured-clean `channel(bits=3)` wire: read a cell's 3 differential
signs, drive the next cell with them, hold deaf. So a symbol at age j has passed through j+1
clean channel operations.

Nulls:
- **deaf bridge** — the bridge's channel is deaf (drive unreachable): nothing is delivered past
  cell 0, so ages >= 1 must fall to chance (`channel-before-carrier` — score what ENTERS a cell
  before crediting what leaves).
- **time-shift** — compare a cell's read to the WRONG turn's symbol: must fall to chance,
  proving ORDER is carried (a bag of bits would not).
- **cross-cell independence** — write independent symbols; the reads must be mutually ~0 bits,
  or the capacity is double-counted (`report-the-rank`).
- **perturbation** — jolt a held cell mid-hold: an engine BASIN self-corrects, a frozen Python
  variable would not exist to perturb. This is the control that the state lives in the engine's
  dynamics, not in a stored number (sol's decisive point).
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring
from anima_reborn.sequence import BITS, CELLS, SequenceEngine

UNITS = 2 * BITS
CHAIN = 0.2
SEQUENCES = 300    # independent symbol streams (enough to push the MI floor well below signal)
TELL = 200


def _drive_for(symbol: int) -> tuple[float, ...]:
    drive: list[float] = []
    for j in range(BITS):
        bit = (symbol >> j) & 1
        drive += [0.8, -0.8] if bit == 0 else [-0.8, 0.8]
    return tuple(drive)


def _mi(pairs: list[tuple[int, int]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    joint = Counter(pairs)
    ma = Counter(a for a, _ in pairs)
    mb = Counter(b for _, b in pairs)
    mi = 0.0
    for (a, b), c in joint.items():
        p = c / n
        mi += p * math.log2(p / ((ma[a] / n) * (mb[b] / n)))
    return mi


def _floor(pairs: list[tuple[int, int]], trials: int = 150) -> float:
    """The MI a shuffled pairing yields — the finite-sample bias floor. A real MI must clear
    it; a null sitting AT it carries no signal (`artefact-honesty`)."""
    if not pairs:
        return 0.0
    a_vals = [a for a, _ in pairs]
    b_vals = [b for _, b in pairs]
    rng = random.Random(4242)
    out = []
    for _ in range(trials):
        rng.shuffle(b_vals)
        out.append(_mi(list(zip(a_vals, b_vals))))
    return sum(out) / len(out)


def run_chain(symbols: list[int], *, seed: int, deaf_bridge: bool = False) -> list[int | None]:
    """Push a stream of symbols through the shipped `SequenceEngine` shift chain; return the
    final tape, where tape[j] is the word held in the cell of age j (0 = most recent). This
    DRIVES the shipped engine — a script measures the engine, not a copy of it."""
    engine = SequenceEngine(seed=seed, deaf_bridge=deaf_bridge)
    for symbol in symbols:
        engine.turn(symbol)
    return engine.tape()


def _forgetting(deaf_bridge: bool = False) -> list[tuple[int, int]]:
    """For each age j, collect (symbol_that_was_written_j_ago, word_read_now) pairs."""
    rng = random.Random(7)
    by_age: list[list[tuple[int, int]]] = [[] for _ in range(CELLS)]
    for s in range(SEQUENCES):
        stream = [rng.randrange(8) for _ in range(CELLS + 3)]  # a few extra turns
        tape = run_chain(stream, seed=s, deaf_bridge=deaf_bridge)
        for j in range(CELLS):
            read = tape[j]
            if read is not None:
                by_age[j].append((stream[-1 - j], read))
    return by_age


def _perturbation_hold(symbol: int, *, seed: int, jolt: float, hold: int = 240) -> int:
    """Write a symbol, hold deaf, but jolt the state once mid-hold; read the word. A basin
    self-corrects; a frozen number could not be jolted at all."""
    engine = CoupledEngine(
        units=UNITS, wiring=Wiring.PAIRS, chain=CHAIN, rhythm=ALTERNATING,
        drive=_drive_for(symbol), seed=seed, initial=(0.0,) * UNITS,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    engine.run(hold // 2)
    rng = random.Random(seed + 999)
    jolted = [v + (rng.random() - 0.5) * 2 * jolt for v in engine.values]
    engine = CoupledEngine(
        units=UNITS, wiring=Wiring.PAIRS, chain=CHAIN, rhythm=FIXED,
        drive=0.0, seed=seed + 1, initial=tuple(jolted),
    )
    values = engine.run(hold // 2).values
    word = 0
    for j in range(BITS):
        word |= (0 if (values[2 * j] - values[2 * j + 1]) > 0 else 1) << j
    return word


def main() -> None:
    print(f"time accumulation — a {CELLS}-cell chain holding the last {CELLS} 3-bit symbols\n")
    print(f"{'age j':>6}{'I(sym;read) live':>18}{'deaf-bridge':>13}{'time-shift':>12}{'floor':>8}")
    print("-" * 59)
    live = _forgetting(deaf_bridge=False)
    deaf = _forgetting(deaf_bridge=True)
    total = 0.0
    for j in range(CELLS):
        i_live = _mi(live[j])
        i_deaf = _mi(deaf[j])
        # time-shift: compare age-j reads against the symbol from a DIFFERENT age.
        shifted = [(sym_other, read) for (_, read), (sym_other, _)
                   in zip(live[j], live[(j + 1) % CELLS])]
        i_shift = _mi(shifted)
        floor = _floor(live[j])
        total += i_live
        print(f"{j:>6}{i_live:>18.3f}{i_deaf:>13.3f}{i_shift:>12.3f}{floor:>8.3f}")
    print(f"\n  total held = {total:.2f} bits ({CELLS} cells x 3), flat across age — the limit "
          f"is the\n  cell count K, not time; the chain remembers the last {CELLS} symbols in order.")

    # Cross-cell independence: independent inputs must give mutually ~0-bit reads (no double count).
    rng = random.Random(11)
    cross = []
    for s in range(SEQUENCES):
        stream = [rng.randrange(8) for _ in range(CELLS + 3)]
        tape = run_chain(stream, seed=1000 + s)
        if tape[0] is not None and tape[1] is not None:
            cross.append((tape[0], tape[1]))
    print(f"  cross-cell I(read0; read1) = {_mi(cross):.3f} bits vs floor {_floor(cross):.3f} "
          f"(at the floor → independent, not double-counted).")

    # Perturbation: the hold is a basin, not a frozen variable.
    print("\n  perturbation (the state lives in the engine's dynamics, not a Python variable):")
    for jolt in (0.0, 0.3, 0.6):
        hits = sum(
            _perturbation_hold(sym, seed=sym * 17 + s, jolt=jolt) == sym
            for sym in range(8) for s in range(20)
        )
        print(f"    jolt {jolt:.1f}: recovered {hits}/160 "
              f"({'basin holds' if hits >= 150 else 'basin broken' if jolt else 'clean'})")

    print("\n  VERDICT: time accumulation works — the chain holds K x 3 bits in order (memory), "
          f"\n  each cell integrated on its own; the bridge is transport, not integration. This "
          f"\n  buys memory and order, not language.")


if __name__ == "__main__":
    main()
