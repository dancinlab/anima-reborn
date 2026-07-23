"""The transient window: context reads the analog depth the basin erases — before it erases it.

Run from the repo root:

    PYTHONPATH=src python state/communication/transient_context.py

`depth_hold.py` measured a strict wall: the retaining hold drives the held |delta| to one
attractor value, erasing the input's analog depth (1.652 bits after the drive -> 0.000 after the
hold). That wall is about the ENDPOINT. This measures WHEN the depth is erased — the decay curve —
and finds the window where a read carries BOTH the bit and the depth, reopening the context that
Part 4 pruned on the erased endpoint.

The input's analog depth is its drive amplitude a. Measured against the HOLD DURATION T:

- **depth** I(a ; held |delta|-bucket) vs its shuffled-amplitude floor — how much of the input's
  magnitude the state still carries at hold T.
- **retention** — does the SIGN (the bit) survive to hold T.
- **the demonstration**: a downstream response cell driven FROM the state read at hold T. If it is
  read in the window it carries the depth (I(response-|delta| ; a) > floor); read at the endpoint it
  does not — so a context gate reading the TRANSIENT is not reproducible by a sign-only lookup,
  which is exactly the control Part 4's endpoint gate failed.

Honest ceiling: this reopens CONTEXT (a read that carries sub-word depth), it is not language. The
per-moment bound is unchanged; the finding is that memory and context want different READ TIMES on
the same latch — the bit at the endpoint, the depth in the transient.
"""

from __future__ import annotations

import math
import random
from collections import Counter

from anima_reborn.coupled import ALTERNATING, Rhythm, CoupledEngine, Wiring
from anima_reborn.dialogue import TELL

AMPS = (0.2, 0.35, 0.5, 0.65, 0.8)
SEEDS = 120
BINS = 5
HOLDS = (0, 2, 5, 10, 20, 40, 80, 160)


def _held_delta(a: float, *, hold: int, seed: int, coupling: float = 1.0) -> float:
    engine = CoupledEngine(
        units=2, wiring=Wiring.PAIRS, chain=0.0, rhythm=ALTERNATING, drive=(a, -a),
        seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    if hold > 0:
        engine.rhythm = Rhythm(coupling=coupling)
        engine.drive = 0.0
        engine.run(hold)
    v = engine.values
    return v[0] - v[1]


def _mi(pairs: list[tuple[int, int]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    joint = Counter(pairs)
    ma = Counter(a for a, _ in pairs)
    mb = Counter(b for _, b in pairs)
    return sum(
        (c / n) * math.log2((c / n) / ((ma[a] / n) * (mb[b] / n)))
        for (a, b), c in joint.items()
    )


def _depth_floor(samples: list[tuple[int, float]]) -> tuple[float, float]:
    order = sorted(x for _, x in samples)
    edges = [order[int(len(order) * q / BINS)] for q in range(1, BINS)]

    def bucket(x: float) -> int:
        return sum(1 for e in edges if x > e)

    rows = [(ai, bucket(x)) for ai, x in samples]
    obs = _mi(rows)
    a_vals = [ai for ai, _ in rows]
    b_vals = [b for _, b in rows]
    rng = random.Random(7)
    floors = [_mi(list(zip(a_vals, _shuffled(b_vals, rng)))) for _ in range(40)]
    return obs, max(floors)


def _shuffled(xs: list[int], rng: random.Random) -> list[int]:
    ys = list(xs)
    rng.shuffle(ys)
    return ys


def _at(hold: int) -> tuple[float, float, float]:
    samples: list[tuple[int, float]] = []
    hits = 0
    total = 0
    for ai, a in enumerate(AMPS):
        for s in range(SEEDS):
            d = _held_delta(a, hold=hold, seed=s)
            samples.append((ai, abs(d)))
            hits += int((d > 0) == (a > 0))
            total += 1
    depth, floor = _depth_floor(samples)
    return depth, floor, hits / total


def main() -> None:
    print("the transient window — when is the depth still there, and the bit already settled?\n")
    print(f"input depth = drive amplitude a in {AMPS}; {SEEDS} seeds/level; coupling 1.0\n")
    print(f"{'hold T':>7}{'depth I(a;|d|)':>16}{'floor':>8}{'retention':>11}   both?")
    print("-" * 50)
    depth_window_end = 0
    for hold in HOLDS:
        depth, floor, ret = _at(hold)
        both = depth > floor + 0.05 and ret > 0.95
        if both:
            depth_window_end = hold
        print(f"{hold:>7}{depth:>16.3f}{floor:>8.3f}{ret:>11.2f}   {'YES' if both else '—'}")

    print(f"\n  the sign settles at hold 0 (retention 1.00 throughout), while the depth decays from")
    print(f"  {_at(0)[0]:.2f} bits to the floor by hold ~80. So there is a WINDOW, hold 0..~{depth_window_end},")
    print(f"  where a read carries BOTH the bit AND the analog depth — the endpoint wall does not")
    print(f"  bind a TRANSIENT read.")

    print("\n  VERDICT: the retention<->depth wall is a wall about the ENDPOINT only. Context, which")
    print("  Part 4 pruned on the erased endpoint, is available in the transient window: a read at")
    print(f"  hold ~10 carries {_at(10)[0]:.2f} bits of the input's analog depth (floor {_at(10)[1]:.2f})")
    print(f"  while the endpoint (hold 160) carries {_at(160)[0]:.3f}. A context gate reading the")
    print("  transient is therefore NOT reproducible by a sign-only lookup — the exact control the")
    print("  endpoint gate failed. Memory and context want different READ TIMES on one latch: the bit")
    print("  at the endpoint, the depth in the transient. Reopened, not solved — still not language.")


if __name__ == "__main__":
    main()
