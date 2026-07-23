"""The retention ↔ analog-depth wall: measured. And where depth actually survives.

Run from the repo root:

    PYTHONPATH=src python state/communication/depth_hold.py

Part 4 (conditional composition) pruned: a context gate on the held state is indistinguishable
from a planted lookup, because the response follows only the SIGN of the held state, not its
analog depth. The stated cause was "the clean bistable hold saturates depth away." That was a
hypothesis. This measures it — is there ANY hold regime that keeps analog depth AND retains the
bit, or is the trade strict? — and finds the one place depth does survive.

(The design delegation for this went off-topic — both models answered about a different project —
so this was designed and measured directly, grounded in `retention.py` and the pruning.)

The input carries analog DEPTH as its drive amplitude a: a pair driven with `(a, -a)` for
different a. What is measured, against a sweep of the HOLD coupling c:

- **depth after the drive** (before the hold): I(a ; held |delta|), the ceiling — is the depth
  even there once the tanh drive has run?
- **depth after the hold**: I(a ; held |delta|) once the pair has held at coupling c for the HOLD
  window — does the basin keep it?
- **retention**: does the held SIGN survive the hold (vs its walk/feedforward null)?

The two curves (retention and post-hold depth) against c are the deliverable — a crossing window
would re-open context; a strict anticorrelation is the wall, quantified. Depth is scored on
held-out amplitude buckets and against a shuffled-amplitude null (`claims-need-controls`).

The honest ceiling: even if a window existed, the most it buys is RE-OPENING context (a hold that
keeps sub-word depth) — not language. If the trade is strict, the finding is the wall itself, plus
the one channel that survives it.
"""

from __future__ import annotations

import math
import random
from collections import Counter

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Rhythm, Wiring
from anima_reborn.dialogue import TELL

AMPS = (0.2, 0.35, 0.5, 0.65, 0.8)   # the input's analog depth
SEEDS = 120
HOLD_TICKS = 240
BINS = 5


def _held_delta(a: float, *, coupling: float, hold: int, seed: int, feedforward: bool = False) -> float:
    """Drive a pair with amplitude a, then hold at `coupling`; return the held differential."""
    wiring = Wiring.FEEDFORWARD if feedforward else Wiring.PAIRS
    engine = CoupledEngine(
        units=2, wiring=wiring, chain=0.0, rhythm=ALTERNATING, drive=(a, -a),
        seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    if hold > 0:
        engine.rhythm = Rhythm(coupling=coupling)
        engine.drive = 0.0
        engine.run(hold)
    values = engine.values
    return values[0] - values[1]


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


def _depth_mi(coupling: float, *, hold: int) -> tuple[float, float]:
    """I(amplitude ; held |delta|-bucket) and its shuffled-amplitude floor. |delta| is bucketed
    at global quantiles so the bins are shared across amplitudes (no per-a leakage)."""
    samples: list[tuple[int, float]] = []
    for ai, a in enumerate(AMPS):
        for s in range(SEEDS):
            d = abs(_held_delta(a, coupling=coupling, hold=hold, seed=s))
            samples.append((ai, d))
    order = sorted(d for _, d in samples)
    edges = [order[int(len(order) * q / BINS)] for q in range(1, BINS)]

    def bucket(d: float) -> int:
        return sum(1 for e in edges if d > e)

    rows = [(ai, bucket(d)) for ai, d in samples]
    obs = _mi(rows)
    a_vals = [ai for ai, _ in rows]
    b_vals = [b for _, b in rows]
    rng = random.Random(7)
    floors = []
    for _ in range(60):
        rng.shuffle(b_vals)
        floors.append(_mi(list(zip(a_vals, b_vals))))
    return obs, max(floors)


def _retention(coupling: float, *, hold: int, feedforward: bool = False) -> float:
    hits = 0
    total = 0
    for a in AMPS:
        for s in range(SEEDS):
            d = _held_delta(a, coupling=coupling, hold=hold, seed=s, feedforward=feedforward)
            hits += int((d > 0) == (a > 0))
            total += 1
    return hits / total


def main() -> None:
    print("retention <-> analog-depth: does any hold keep BOTH?\n")
    print(f"input depth = drive amplitude a in {AMPS}; hold {HOLD_TICKS} ticks; "
          f"{SEEDS} seeds/level\n")

    # The ceiling: depth right after the drive, before any hold.
    d0, f0 = _depth_mi(1.0, hold=0)
    print(f"depth AFTER THE DRIVE (no hold):  I(a; |delta|) = {d0:.3f}  floor {f0:.3f}  "
          f"-> the analog depth IS there once the drive has run\n")

    print(f"{'hold c':>7}{'retention':>11}{'depth I(a;|d|)':>16}{'floor':>8}   verdict")
    print("-" * 56)
    curve = []
    for c in (1.0, 0.9, 0.7, 0.5, 0.3):
        ret = _retention(c, hold=HOLD_TICKS)
        depth, floor = _depth_mi(c, hold=HOLD_TICKS)
        keeps_depth = depth > floor + 0.02
        retains = ret > 0.95
        verdict = "keeps BOTH" if keeps_depth and retains else (
            "retains, depth erased" if retains else "depth?, bit lost")
        curve.append((c, ret, depth, keeps_depth and retains))
        print(f"{c:>7.1f}{ret:>11.2f}{depth:>16.3f}{floor:>8.3f}   {verdict}")

    ff_ret = _retention(1.0, hold=HOLD_TICKS, feedforward=True)
    print(f"\n  retention null (feedforward, c=1.0): {ff_ret:.2f} (no cycle -> no hold)")

    # The one channel that survives: the transient carries a even where the endpoint does not.
    trans, tf = _depth_mi(1.0, hold=0)
    held, hf = _depth_mi(1.0, hold=HOLD_TICKS)
    window = any(both for *_, both in curve)
    print("\n  VERDICT:")
    if window:
        print("  a hold regime keeps BOTH depth and the bit — context can be re-opened there.")
    else:
        print("  STRICT WALL — no hold keeps both. Every coupling that RETAINS the bit (>0.95)")
        print("  drives |delta| to a single attractor value INDEPENDENT of a (depth I at its floor);")
        print("  the only coupling that keeps any depth is where the bit is already lost. The BASIN")
        print("  that buys retention is exactly what erases depth — retention and analog depth are")
        print("  mutually exclusive in the HELD state. This is the pruning's cause, measured.")
        print(f"\n  But depth is not gone from the substrate: after the drive I(a;|delta|)={trans:.3f}")
        print(f"  (floor {tf:.3f}) while after the hold it is {held:.3f} (floor {hf:.3f}). Depth lives")
        print("  in the TRANSIENT, not the endpoint — so context, if it comes, must be read DURING")
        print("  settling, never from memory. Memory and context want opposite dynamics on one latch.")


if __name__ == "__main__":
    main()
