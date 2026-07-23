"""The non-latching consumer: a population RATE code holds analog depth AND a response consumes it.

Run from the repo root:

    PYTHONPATH=src python state/communication/rate_code.py

`transient_gate.py` closed the context line with a recursive wall: every single bistable latch
flattens analog depth. The retaining basin drives |delta| to one attractor value independent of
the input amplitude (`depth_hold.py`), and a response latch driven from the transient window
re-erases the depth it read (I(R; a_past | sign) = 0 at every scale and read time). The missing
piece was named there: a NON-LATCHING consumer — an element that HOLDS an analog value stably
(memory) and can be CONSUMED into a context-dependent output without saturating it away.

This measures the candidate that escapes the recursion by refusing to fight it: a POPULATION RATE
code. N independent near-barrier PAIRS latches are all told the same signed depth (sign * a) at a
write scale s, each from its OWN random initial state (the per-latch threshold spread) with its
own walk noise. Each latch saturates completely — that is exactly what makes the hold stable — but
WHICH basin each latch falls into is stochastic with a probability graded in a, so the input's
analog depth is transduced, at write time, from a magnitude (the dimension the basin erases) into
a COUNT of up-latches (sign statistics — the dimension the basin preserves, flat through silence
per `retention.py`). Saturation then protects the code instead of erasing it.

The mechanism, stated honestly: this is NOT a non-attractor store — the recursive wall stands for
any single attractor, because retention IS discretization. The escape is MANY attractors: depth is
held quantized across the population's basins, the effective analog width is bounded by
log2(N + 1), and the downstream reads the population MEAN differential — a plain average, analog
in the count, obtained without any latch having to carry magnitude. Each consuming response latch
still flattens its own input to one bit — but that bit is now a bit OF DEPTH (which side of a
bias theta the rate sits), not a copy of the input's sign.

Measured, each against its shuffled floor (`claims-need-controls`), with the write scale and the
consumer bias chosen on CALIBRATION seeds and every claim scored on fresh EVALUATION seeds:

- **the trade-off curve** (write-scale sweep): majority-sign retention vs held depth
  I(a ; count | sign) — the single latch's strict exclusion should become a curve with a middle.
- **HOLD**: I(a ; count | sign) at hold 0 / 240 / 480 deaf ticks (FIXED coupling 1.0, drive
  bit-unreachable), plus count drift — the analog value must survive silence at the ENDPOINT,
  where the single latch's depth is 0.000 (`depth_hold.py`).
- **CONSUME**: two bistable response latches (bias +theta / -theta) driven by
  tanh(GAIN * mean_delta / 2A) — the same response form `transient_gate.py` used — read after
  their own full 120-tick latch. The exact control that failed there: I(R ; a_past | sign) > floor.
  The read is non-destructive by construction: the responses hear a copy of the mean, the
  population is untouched.
- **the rank** (`report-the-rank`): effective width beside stability — count spread per amplitude,
  2^I distinguishable levels against the log2(5) ceiling, and the width sweep N = 1..32, where
  N = 1 IS the wall row.
- **channel-before-carrier**: the depth ENTERING the response stage (I(a ; h | sign)) is scored
  before the depth leaving it, and the surviving fraction reported.

The honest ceiling, fixed in advance: if this works, the claim is only "an element on this
substrate holds analog depth stably AND a downstream's output depends on that depth beyond the
sign" — context becomes USABLE, quantized at the measured width, at most log2(N+1) bits per
moment, at most ~1 bit extracted per response latch per read. The population is deliberately
DISintegrated (chain 0 — Phi across independent pairs factorizes), so this element buys held
depth, not integration; an integrated (odd-chained) population is a separate measurement. Not
language.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter

from anima_reborn.coupled import ALTERNATING, AMPLITUDE, FIXED, GAIN, CoupledEngine, Wiring
from anima_reborn.dialogue import TELL

AMPS = (0.2, 0.35, 0.5, 0.65, 0.8)   # the input's analog depth
SIGNS = (1, -1)                      # the input's sign — the latch dimension, conditioned out
PAIRS_N = 32                         # latches in the population; count in 0..32
SCALES = (0.03, 0.05, 0.08, 0.15, 0.30)   # write drive scale sweep — the graded regime is low
SWEEP_TRIALS = 30                    # calibration trials per (a, sign) per sweep row
TRIALS = 60                          # evaluation trials per (a, sign)
SWEEP_HOLD = 240
HOLDS = (0, 240, 480)
BINS = 5
RETENTION_BAR = 0.95                 # same bar `depth_hold.py` used for "retains"
RESPONSE_SCALE = 0.5
RESPONSE_SETTLE = 120                # same settle `transient_gate.py` used
WIDTHS = (1, 4, 8, 16, 32)           # population width sweep; 1 is the single-latch wall

CAL_BASE = 100_000                   # calibration seeds (scale choice, theta)
EVAL_BASE = 500_000                  # evaluation seeds (every claimed number)
WIDTH_BASE = 700_000
RESP_BASE = 900_000


def _write_and_hold(
    a: float, sign: int, *, scale: float, seed: int, n_pairs: int, holds: tuple[int, ...],
) -> dict[int, tuple[int, float]]:
    """Tell N near-barrier latches the signed depth, hold them deaf, and read (count, mean delta)
    at each hold. One engine of 2N units, PAIRS at chain 0 = N independent latches sharing one
    seeded rng; the default RANDOM initial spread is the per-latch threshold diversity."""
    d = scale * a * sign
    engine = CoupledEngine(
        units=2 * n_pairs, wiring=Wiring.PAIRS, chain=0.0, rhythm=ALTERNATING,
        drive=(d, -d) * n_pairs, seed=seed,
    )
    engine.run(TELL)
    engine.rhythm = FIXED          # deaf: coupling 1.0, drive bit-unreachable
    engine.drive = 0.0
    out: dict[int, tuple[int, float]] = {}
    elapsed = 0
    for hold in holds:
        if hold > elapsed:
            engine.run(hold - elapsed)
            elapsed = hold
        v = engine.values
        deltas = [v[2 * i] - v[2 * i + 1] for i in range(n_pairs)]
        count = sum(1 for x in deltas if x > 0)
        out[hold] = (count, sum(deltas) / n_pairs)
    return out


Row = tuple[int, int, dict[int, tuple[int, float]]]   # (amp index, sign, {hold: (count, mean_d)})


def _collect(
    *, scale: float, n_pairs: int, trials: int, holds: tuple[int, ...], base: int,
) -> list[Row]:
    rows: list[Row] = []
    k = 0
    for ai, a in enumerate(AMPS):
        for sign in SIGNS:
            for _ in range(trials):
                rows.append((ai, sign, _write_and_hold(
                    a, sign, scale=scale, seed=base + k, n_pairs=n_pairs, holds=holds)))
                k += 1
    return rows


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


def _bucket_rows(samples: list[tuple[int, float]]) -> list[tuple[int, int]]:
    """Quantile-bucket the analog column into BINS shared bins (the siblings' scheme)."""
    order = sorted(x for _, x in samples)
    edges = [order[int(len(order) * q / BINS)] for q in range(1, BINS)]
    return [(ai, sum(1 for e in edges if x > e)) for ai, x in samples]


def _cond_depth(by_sign: dict[int, list[tuple[int, float]]], *, shuffle_seed: int) -> tuple[float, float]:
    """I(a ; x-bucket | sign) and its floor: a-labels shuffled WITHIN each sign arm, max of 30 —
    a sign-only lookup scores exactly the floor here, which is what makes this the control."""
    total = sum(len(v) for v in by_sign.values())
    arms = {sg: _bucket_rows(v) for sg, v in by_sign.items()}
    obs = sum((len(rows) / total) * _mi(rows) for rows in arms.values())
    rng = random.Random(shuffle_seed)
    floors = []
    for _ in range(30):
        f = 0.0
        for rows in arms.values():
            ais = [a for a, _ in rows]
            bs = [b for _, b in rows]
            rng.shuffle(ais)
            f += (len(rows) / total) * _mi(list(zip(ais, bs)))
        floors.append(f)
    return obs, max(floors)


def _depth(rows: list[Row], hold: int, *, shuffle_seed: int = 7) -> tuple[float, float]:
    by_sign: dict[int, list[tuple[int, float]]] = {}
    for ai, sign, out in rows:
        by_sign.setdefault(sign, []).append((ai, float(out[hold][0])))
    return _cond_depth(by_sign, shuffle_seed=shuffle_seed)


def _retention(rows: list[Row], hold: int, n_pairs: int) -> tuple[float, float]:
    """Majority-vote sign retention: pooled, and the worst per-amplitude level. A tie counts
    wrong — the majority must actually carry the sign."""
    hits: dict[int, int] = {ai: 0 for ai in range(len(AMPS))}
    totals: dict[int, int] = {ai: 0 for ai in range(len(AMPS))}
    for ai, sign, out in rows:
        maj = 2 * out[hold][0] - n_pairs
        hits[ai] += int((maj > 0) if sign > 0 else (maj < 0))
        totals[ai] += 1
    per_a = [hits[ai] / totals[ai] for ai in range(len(AMPS))]
    pooled = sum(hits.values()) / sum(totals.values())
    return pooled, min(per_a)


def _h_tanh(mean_delta: float) -> float:
    """What `transient_gate.py`'s response heard — the reader's own tanh, kept for comparability.
    Saturates near full count, which costs separability against the response noise, not
    information (quantile-bucket MI is invariant under a monotone map)."""
    return math.tanh(GAIN * mean_delta / (2 * AMPLITUDE))


def _h_lin(mean_delta: float) -> float:
    """The linear average read — a unit hearing the population mean as a drive does, linearly
    (`heard = value * amplitude`), the same way `observe()` reports raw positions."""
    return mean_delta / (2 * AMPLITUDE)


def _response(x: float, *, seed: int) -> int:
    """A bistable response latch driven near its barrier by x, then fully latched — the consumer
    stage that erased depth in `transient_gate.py`, unchanged."""
    engine = CoupledEngine(
        units=2, wiring=Wiring.PAIRS, chain=0.0, rhythm=ALTERNATING,
        drive=(RESPONSE_SCALE * x, -RESPONSE_SCALE * x), seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    v = engine.run(RESPONSE_SETTLE).values
    return 0 if (v[0] - v[1]) > 0 else 1


def main() -> None:
    print("the non-latching consumer — a population rate code: hold analog depth, then consume it\n")
    print(f"input depth = drive amplitude a in {AMPS}, sign in {SIGNS}; population = {PAIRS_N}")
    print(f"near-barrier PAIRS latches (random initials = threshold spread); tell {TELL}, deaf hold\n")

    # [1] the trade-off curve — write scale vs (retention, depth), on calibration seeds.
    print(f"[1] write-scale trade-off (hold {SWEEP_HOLD}, {SWEEP_TRIALS} calibration trials/class)")
    print(f"{'scale':>7}{'retention':>11}{'min/a':>8}{'depth I(a;count|sign)':>23}{'floor':>8}")
    print("  " + "-" * 55)
    sweep: dict[float, tuple[list[Row], float, float, float, float]] = {}
    for si, scale in enumerate(SCALES):
        rows = _collect(scale=scale, n_pairs=PAIRS_N, trials=SWEEP_TRIALS,
                        holds=(SWEEP_HOLD,), base=CAL_BASE + si * 10_000)
        ret, ret_min = _retention(rows, SWEEP_HOLD, PAIRS_N)
        depth, floor = _depth(rows, SWEEP_HOLD, shuffle_seed=11 + si)
        sweep[scale] = (rows, ret, ret_min, depth, floor)
        print(f"{scale:>7.2f}{ret:>11.3f}{ret_min:>8.3f}{depth:>23.3f}{floor:>8.3f}")

    retaining = [s for s in SCALES if sweep[s][1] >= RETENTION_BAR]
    if retaining:
        main_scale = max(retaining, key=lambda s: sweep[s][3])
        print(f"\n  chosen scale s = {main_scale:.2f} — max depth among rows with retention >= {RETENTION_BAR}")
    else:
        main_scale = max(SCALES, key=lambda s: sweep[s][1])
        print(f"\n  NO scale retains at >= {RETENTION_BAR}; best-retention row s = {main_scale:.2f} — "
              "the trade-off did not open")
    cal_rows = sweep[main_scale][0]

    # Psychometric curve at the chosen scale: the write-time transduction magnitude -> count.
    up_frac = {ai: [] for ai in range(len(AMPS))}
    for ai, sign, out in cal_rows:
        if sign > 0:
            up_frac[ai].append(out[SWEEP_HOLD][0] / PAIRS_N)
    curve = "  ".join(f"a={AMPS[ai]:.2f}:{statistics.mean(v):.2f}" for ai, v in up_frac.items())
    print(f"  psychometric P(latch up | a, sign=+): {curve}")

    # Consumer biases, from calibration only: the median of what each read form hears, + arm.
    thetas = {}
    for name, fn in (("tanh", _h_tanh), ("linear", _h_lin)):
        hs_pos = sorted(fn(out[SWEEP_HOLD][1]) for _, sign, out in cal_rows if sign > 0)
        thetas[name] = hs_pos[len(hs_pos) // 2]
    print("  consumer bias theta (median heard-rate, + arm, calibration): "
          + "  ".join(f"{k}={v:.3f}" for k, v in thetas.items()) + "\n")

    # [2] HOLD — evaluation seeds, the endpoint where the single latch reads 0.000.
    print(f"[2] HOLD — depth through deaf silence ({TRIALS} evaluation trials/class)")
    rows = _collect(scale=main_scale, n_pairs=PAIRS_N, trials=TRIALS, holds=HOLDS, base=EVAL_BASE)
    print(f"{'hold':>7}{'depth I(a;count|sign)':>23}{'floor':>8}{'retention':>11}{'min/a':>8}")
    print("  " + "-" * 55)
    held: dict[int, tuple[float, float]] = {}
    for hold in HOLDS:
        depth, floor = _depth(rows, hold, shuffle_seed=29 + hold)
        ret, ret_min = _retention(rows, hold, PAIRS_N)
        held[hold] = (depth, floor)
        print(f"{hold:>7}{depth:>23.3f}{floor:>8.3f}{ret:>11.3f}{ret_min:>8.3f}")
    drift_a = statistics.mean(abs(out[240][0] - out[0][0]) for *_, out in rows)
    drift_b = statistics.mean(abs(out[480][0] - out[240][0]) for *_, out in rows)
    frozen = statistics.mean(out[480][0] == out[240][0] for *_, out in rows)
    print(f"  count drift |dcount|: write->240 = {drift_a:.2f}, 240->480 = {drift_b:.2f}; "
          f"P(count frozen 240->480) = {frozen:.3f}")

    # [3] the rank — effective width beside the stability just shown.
    print("\n[3] rank — what the held readout actually spans (+ arm, hold 480)")
    for ai, a in enumerate(AMPS):
        cs = [out[480][0] for aj, sign, out in rows if aj == ai and sign > 0]
        print(f"    a={a:.2f}: count {statistics.mean(cs):5.1f} +/- {statistics.stdev(cs):4.1f}")
    d480 = held[480][0]
    print(f"    held depth {d480:.3f} bits ~= {2 ** d480:.1f} distinguishable levels "
          f"(ceiling log2({len(AMPS)}) = {math.log2(len(AMPS)):.2f} bits; count lattice log2({PAIRS_N + 1}) = "
          f"{math.log2(PAIRS_N + 1):.2f})")

    # [4] CONSUME — the exact control transient_gate.py failed, on the hold-480 endpoint.
    print("\n[4] CONSUME — biased response latches read the held rate (hold 480)")
    enter_by_sign: dict[int, list[tuple[int, float]]] = {}
    for ai, sign, out in rows:
        enter_by_sign.setdefault(sign, []).append((ai, _h_lin(out[480][1])))
    enter, enter_floor = _cond_depth(enter_by_sign, shuffle_seed=41)
    print(f"    entering the stage:  I(a ; heard rate | sign) = {enter:.3f}  floor {enter_floor:.3f}")
    gates = {}
    for fi, (name, fn) in enumerate((("tanh", _h_tanh), ("linear", _h_lin))):
        theta = thetas[name]
        gate_by_sign: dict[int, list[tuple[int, float]]] = {}
        for idx, (ai, sign, out) in enumerate(rows):
            h = fn(out[480][1])
            rp = _response(h - theta, seed=RESP_BASE + fi * 10_000 + idx * 2)
            rm = _response(h + theta, seed=RESP_BASE + fi * 10_000 + idx * 2 + 1)
            gate_by_sign.setdefault(sign, []).append((ai, float(2 * rp + rm)))
        gate, gate_floor = _cond_depth(gate_by_sign, shuffle_seed=43 + fi)
        gates[name] = (gate, gate_floor)
        note = "  [transient_gate.py's read form: 0.0000 there]" if name == "tanh" else ""
        print(f"    leaving, {name:>6} read: I(R ; a_past | sign) = {gate:.3f}  floor {gate_floor:.3f}"
              f"  surviving {gate / enter:.2f}{note}")
    gate, gate_floor = max(gates.values(), key=lambda t: t[0] - t[1])

    # [5] width sweep — N = 1 is the wall row; width is what buys the coexistence.
    print(f"\n[5] width sweep (s = {main_scale:.2f}, hold {SWEEP_HOLD}, {SWEEP_TRIALS} trials/class)")
    print(f"{'N':>5}{'retention':>11}{'depth I(a;count|sign)':>23}{'floor':>8}")
    print("  " + "-" * 48)
    for ni, n in enumerate(WIDTHS):
        wrows = _collect(scale=main_scale, n_pairs=n, trials=SWEEP_TRIALS,
                         holds=(SWEEP_HOLD,), base=WIDTH_BASE + ni * 10_000)
        wret, _ = _retention(wrows, SWEEP_HOLD, n)
        wdepth, wfloor = _depth(wrows, SWEEP_HOLD, shuffle_seed=53 + ni)
        tag = "   <- the single-latch wall" if n == 1 else ""
        print(f"{n:>5}{wret:>11.3f}{wdepth:>23.3f}{wfloor:>8.3f}{tag}")

    # The verdict, from the evaluation numbers alone.
    ret480, _ = _retention(rows, 480, PAIRS_N)
    holds_ok = d480 > held[480][1] + 0.05 and ret480 >= RETENTION_BAR and frozen >= 0.95
    consumes_ok = gate > gate_floor + 0.05
    print("\n  VERDICT:")
    if holds_ok and consumes_ok:
        print(f"  the wall has a door, and it is WIDTH. A {PAIRS_N}-latch rate code HOLDS analog depth")
        print(f"  through {HOLDS[-1]} deaf ticks ({d480:.2f} bits, floor {held[480][1]:.2f}, sign retention "
              f"{ret480:.2f}, count frozen)")
        print(f"  AND a latched response driven from its mean carries that depth beyond the sign")
        print(f"  (I(R;a_past|sign) = {gate:.2f} vs floor {gate_floor:.2f}, where every single-latch consumer")
        print(f"  measured 0.0000). No latch fights the basin: depth is transduced at write time into")
        print(f"  the COUNT — sign statistics, which the basins preserve — so saturation protects the")
        print(f"  code instead of erasing it. The element is not a continuous store: depth is held")
        print(f"  QUANTIZED, {d480:.2f} bits effective of a log2({PAIRS_N + 1}) lattice, ~1 bit per response")
        print(f"  latch per read. Context is now USABLE (holdable AND consumable) at that width.")
        print(f"  The population is disintegrated (chain 0) — this buys held depth, not Phi. Not language.")
    elif holds_ok:
        print(f"  HALF a door: the rate holds depth ({d480:.2f} bits at hold {HOLDS[-1]}) but the biased")
        print(f"  response does not carry it (I = {gate:.3f} vs floor {gate_floor:.3f}) — the consumer stage")
        print(f"  is still a wall; the held rate is readable but, again, unlatched.")
    else:
        print(f"  ANOTHER WALL: no write scale gives majority retention >= {RETENTION_BAR} together with")
        print(f"  depth above floor (best: retention {ret480:.2f}, depth {d480:.3f} vs floor {held[480][1]:.3f}).")
        print(f"  The population trade-off closes just as the single latch's did — 'no non-latching")
        print(f"  consumer exists on this substrate' would survive one more design.")


if __name__ == "__main__":
    main()
