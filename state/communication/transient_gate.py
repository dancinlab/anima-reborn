"""Re-auditing context in the transient window: the wall is recursive — a latch re-erases depth.

Run from the repo root:

    PYTHONPATH=src python state/communication/transient_gate.py

`transient_context.py` found that a read in the window (hold 0..~40) carries the input's analog
DEPTH (1.14 bits at hold 10) that the endpoint erases — reopening the context Part 4 pruned. This
re-audits it at the level of a USED gate: if a downstream response cell reads the past state
transiently, does its output R depend on the past's analog DEPTH beyond its sign — the control a
sign-only lookup fails? If yes, context is genuinely used; if no, the window is only a readout, not
a usable gate.

The past is written with a sign AND an analog magnitude a_past (its depth). The context response is
a bistable pair driven near its barrier by the past's held differential (whose magnitude carries
a_past when read in the window). We measure, per past-sign, I(R ; a_past) — does the response follow
the depth — against its shuffled floor, at several drive scales and read times.

The measured answer is a WALL, and a recursive one: I(R ; a_past | sign) sits at 0 at every scale
and every read time. To USE the depth the response must drive a latch; to be a stable bit the latch
must saturate; saturating re-erases the depth — exactly the retention<->depth wall, one level down.
So the transient window is a continuous-READOUT finding (depth is measurable there), not a usable
context gate: a latching consumer flattens it again. The honest verdict is that context stays
readable but unlatched — and the substrate has no non-latching consumer to turn depth into a used
bit. Still not language; the frontier this reopened is a readout, and it closes again at the next
latch.
"""

from __future__ import annotations

import math
import random
from collections import Counter

from anima_reborn.coupled import ALTERNATING, AMPLITUDE, GAIN, CoupledEngine, Rhythm, Wiring
from anima_reborn.dialogue import TELL

AMPS = (0.2, 0.35, 0.5, 0.65, 0.8)   # the past's analog depth
SEEDS = 120


def _past_delta(a_past: float, sign: int, *, read_hold: int, seed: int) -> float:
    """Write a past symbol with magnitude a_past and given sign; hold `read_hold` ticks; read the
    differential. Small read_hold is the transient window (depth present)."""
    drive = (a_past, -a_past) if sign > 0 else (-a_past, a_past)
    engine = CoupledEngine(
        units=2, wiring=Wiring.PAIRS, chain=0.0, rhythm=ALTERNATING, drive=drive,
        seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    if read_hold > 0:
        engine.rhythm = Rhythm(coupling=1.0)
        engine.drive = 0.0
        engine.run(read_hold)
    v = engine.values
    return v[0] - v[1]


def _response(delta_past: float, *, scale: float, seed: int) -> int:
    """A bistable response driven near its barrier by the past differential (its magnitude carries
    the past depth). It then holds to become a readable bit — which is where the depth dies."""
    h = math.tanh(GAIN * delta_past / (2 * AMPLITUDE))
    engine = CoupledEngine(
        units=2, wiring=Wiring.PAIRS, chain=0.0, rhythm=ALTERNATING,
        drive=(scale * h, -scale * h), seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    engine.rhythm = Rhythm(coupling=1.0)
    engine.drive = 0.0
    v = engine.run(120).values
    return 0 if (v[0] - v[1]) > 0 else 1


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


def _readout_depth(read_hold: int) -> tuple[float, float]:
    """I(a_past ; |past delta|-bucket) — the CONTINUOUS readout: is the depth there to be read?"""
    samples = []
    for ai, a in enumerate(AMPS):
        for sg in (1, -1):
            for s in range(SEEDS):
                samples.append((ai, abs(_past_delta(a, sg, read_hold=read_hold, seed=s * 3 + 1))))
    order = sorted(x for _, x in samples)
    edges = [order[int(len(order) * q / 5)] for q in range(1, 5)]

    def bucket(x: float) -> int:
        return sum(1 for e in edges if x > e)

    rows = [(ai, bucket(x)) for ai, x in samples]
    obs = _mi(rows)
    a_vals = [a for a, _ in rows]
    b_vals = [b for _, b in rows]
    rng = random.Random(3)
    floors = []
    for _ in range(30):
        rng.shuffle(b_vals)
        floors.append(_mi(list(zip(a_vals, b_vals))))
    return obs, max(floors)


def _gate_depth(read_hold: int, scale: float) -> tuple[float, float]:
    """I(R ; a_past | past-sign) — does the LATCHED response follow the past depth beyond its sign?"""
    by_sign: dict[int, list[tuple[int, int]]] = {}
    for ai, a in enumerate(AMPS):
        for sg in (1, -1):
            for s in range(SEEDS):
                dp = _past_delta(a, sg, read_hold=read_hold, seed=s * 3 + 1)
                r = _response(dp, scale=scale, seed=s * 7 + 2)
                by_sign.setdefault(sg, []).append((ai, r))
    total = sum(len(v) for v in by_sign.values())
    cond = sum((len(v) / total) * _mi(v) for v in by_sign.values())
    rng = random.Random(9)
    floors = []
    for _ in range(30):
        f = 0.0
        for v in by_sign.values():
            ais = [a for a, _ in v]
            rs = [r for _, r in v]
            rng.shuffle(ais)
            f += (len(v) / total) * _mi(list(zip(ais, rs)))
        floors.append(f)
    return cond, max(floors)


def main() -> None:
    print("transient context, re-audited as a USED gate — does a latched response carry depth?\n")
    for hold in (10, 240):
        d, f = _readout_depth(hold)
        where = "transient window" if hold == 10 else "endpoint"
        print(f"  readout at hold {hold:>3} ({where}): I(a_past; |delta|) = {d:.3f}  floor {f:.3f}"
              f"   {'depth readable ✓' if d > f + 0.05 else 'depth gone'}")

    print("\n  now drive a bistable RESPONSE from that past state and read its bit:")
    print(f"  {'read hold':>10}{'scale':>7}{'I(R;a_past|sign)':>18}{'floor':>8}   gate carries depth?")
    print("  " + "-" * 56)
    any_pass = False
    for hold in (10, 240):
        for scale in (0.30, 0.15, 0.08):
            c, fl = _gate_depth(hold, scale)
            ok = c > fl + 0.01
            any_pass = any_pass or ok
            print(f"  {hold:>10}{scale:>7.2f}{c:>18.4f}{fl:>8.4f}   {'YES ✓' if ok else 'no'}")

    print("\n  VERDICT:")
    if any_pass:
        print("  a latched response carries the past depth — context is genuinely used in the window.")
    else:
        print("  RECURSIVE WALL. The depth is READABLE in the transient window (continuous readout,")
        print("  ~1.1 bits), but a bistable response driven from it carries NONE of it: I(R;a_past|sign)")
        print("  = 0 at every scale and read time. To USE the depth the response must drive a latch; to")
        print("  be a stable bit the latch must saturate; saturating re-erases the depth — the")
        print("  retention<->depth wall, one level down. So the transient window reopened a READOUT,")
        print("  not a usable gate: this substrate has no non-latching consumer to turn depth into a")
        print("  used bit. Context stays readable but unlatched. Still memory and order, not language.")


if __name__ == "__main__":
    main()
