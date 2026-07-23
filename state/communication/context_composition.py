"""Conditional composition: does the HELD PAST act on the current write? Measured, with the
control that a planted lookup cannot fake.

Run from the repo root:

    PYTHONPATH=src python state/communication/context_composition.py

Part 4 of the "engine parts toward the goal" plan. `sequence.py` holds the last K symbols in
order (memory), but a recorder does not USE its past. The step toward language both delegated
designs named: the held past must ACT on the current write — CONTEXT. This prototypes the gate
on raw `CoupledEngine` cells and measures whether the dependence is real, before any `src/`
change (the repo pattern: measure the capability, with its controls, first).

Design delegated to both frontier models and reconciled (`state/lab/2026-07-23-context-gate-*.md`).
sol caught a flaw in the first sketch — writing the composite back into tape cell 0 would make
the NEXT turn's "past" the previous composite, destroying the recorder — so the tape stays clean
and the gate drives a SEPARATE response cell R. The mechanism is a smooth STATE EQUATION, not a
lookup: for pair j the response drive orientation is

    q_j = x_j * [ (1 - g) + g * tanh(GAIN * delta_j / (2*AMPLITUDE)) ]

where x_j is the current symbol's drive orientation and delta_j is the ACTUAL held differential
of the previous cell's pair j (never the stored word). At g=0 this is the ordinary current
write; at g>0 the orientation depends jointly on current and past.

The trap, named exactly: the synergy score S = I(R;(C,P)) − I(R;C) − I(R;P) is NECESSARY but
NOT SUFFICIENT — a designer-wired XOR lookup `R = C XOR P` scores S maximally (the D7 revival).
So the load-bearing control is CAUSAL: the response must follow the raw physical state (the
analog DEPTH of delta), which a lookup on the symbol log cannot see. If S sits at its floor
beyond the copy arms, OR the response shows no depth sensitivity beyond a sign-only lookup, the
honest result is "no synergy beyond copy — PRUNED", and we stop there.

Even if it passes, the ceiling is unmoved: I(R;C,P) <= 3 bits per response, the synergy is paid
for out of the SAME 3-bit budget (it trades against current fidelity), and the gain is
CONTEXT that is used — not learned composition, not understanding, not language.
"""

from __future__ import annotations

import math
import random
from collections import Counter

from anima_reborn.coupled import ALTERNATING, AMPLITUDE, FIXED, GAIN, CoupledEngine, Wiring
from anima_reborn.dialogue import HOLD, TELL, channel_trace

BITS = 3
UNITS = 2 * BITS
CHAIN = 0.2
SEEDS = 32          # per (current, past) pair
SHUFFLES = 100


def _decode(values: tuple[float, ...]) -> int:
    word = 0
    for j in range(BITS):
        word |= (0 if (values[2 * j] - values[2 * j + 1]) > 0 else 1) << j
    return word


def _held(symbol: int, *, seed: int) -> tuple[list[float], int]:
    """Drive a cell with `symbol`, hold deaf, return its per-pair differentials and word."""
    final = channel_trace(symbol, seed=seed, bits=BITS)[-1]
    diffs = [final[2 * j] - final[2 * j + 1] for j in range(BITS)]
    return diffs, _decode(tuple(final))


def _response(current: int, diffs: list[float], *, gate: float, seed: int) -> int:
    """Drive a fresh response cell whose orientation is the current symbol modulated by the
    held differentials — the multiplicative context gate."""
    drive: list[float] = []
    for j in range(BITS):
        h = math.tanh(GAIN * diffs[j] / (2 * AMPLITUDE))
        x = 1.0 if ((current >> j) & 1) == 0 else -1.0
        q = x * ((1.0 - gate) + gate * h)
        drive += [0.8 * q, -0.8 * q]
    engine = CoupledEngine(
        units=UNITS, wiring=Wiring.PAIRS, chain=CHAIN, rhythm=ALTERNATING,
        drive=tuple(drive), seed=seed, initial=(0.0,) * UNITS,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    return _decode(engine.run(HOLD).values)


# ── information ───────────────────────────────────────────────────────────────────────

def _mi(pairs: list[tuple]) -> float:
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


def _interaction(rows: list[tuple[int, int, int]]) -> float:
    """S = I(R;(C,P)) - I(R;C) - I(R;P). Signed, not clipped."""
    cp_r = [((c, p), r) for c, p, r in rows]
    c_r = [(c, r) for c, p, r in rows]
    p_r = [(p, r) for c, p, r in rows]
    return _mi(cp_r) - _mi(c_r) - _mi(p_r)


def _shuffle_floor(rows: list[tuple[int, int, int]]) -> float:
    """Permute the past P across reads (keeping C, R and margins) — the interaction a random
    pairing yields. True synergy must clear it."""
    cs = [c for c, _, _ in rows]
    ps = [p for _, p, _ in rows]
    rs = [r for _, _, r in rows]
    rng = random.Random(4242)
    out = []
    for _ in range(SHUFFLES):
        rng.shuffle(ps)
        out.append(_interaction(list(zip(cs, ps, rs))))
    return max(out)


# ── the arms ──────────────────────────────────────────────────────────────────────────

def _collect(gate: float, *, arm: str = "gate") -> list[tuple[int, int, int]]:
    """One balanced pass over all 64 (current, past) pairs x SEEDS. `arm` selects the variant."""
    rows = []
    base = 20260723
    for current in range(8):
        for past in range(8):
            for s in range(SEEDS):
                seed = base + (current * 8 + past) * 97 + s
                diffs, p_h = _held(past, seed=seed)
                if arm == "past_copy":
                    r = p_h
                elif arm == "current_copy":
                    r = current
                elif arm == "xor":
                    r = current ^ p_h  # a planted lookup on the symbol log
                else:  # gate (gate=0 is the no-gate arm)
                    r = _response(current, diffs, gate=gate, seed=seed * 13 + 5)
                rows.append((current, p_h, r))
    return rows


def _depth_sensitivity(gate: float, *, scale: float = 0.8) -> tuple[float, float]:
    """Does R follow the analog DEPTH of the held state beyond its sign — the control a
    sign-only lookup cannot pass? I(R; depth-bucket | current, past-word), vs its floor. The
    held |delta| is split at its own MEDIAN (so shallow/deep each get half); `scale` shrinks
    the response drive toward the barrier where depth would matter most."""
    recs: list[tuple[int, int, float, int]] = []
    base = 55550
    for current in range(8):
        for past in range(8):
            for s in range(SEEDS):
                seed = base + (current * 8 + past) * 89 + s
                diffs, p_h = _held(past, seed=seed)
                drive: list[float] = []
                for j in range(BITS):
                    h = math.tanh(GAIN * diffs[j] / (2 * AMPLITUDE))
                    x = 1.0 if ((current >> j) & 1) == 0 else -1.0
                    q = x * ((1.0 - gate) + gate * h)
                    drive += [scale * q, -scale * q]
                engine = CoupledEngine(
                    units=UNITS, wiring=Wiring.PAIRS, chain=CHAIN, rhythm=ALTERNATING,
                    drive=tuple(drive), seed=seed * 13 + 5, initial=(0.0,) * UNITS,
                )
                engine.run(TELL)
                engine.rhythm = FIXED
                engine.drive = 0.0
                r = _decode(engine.run(HOLD).values)
                recs.append((current, p_h, sum(abs(d) for d in diffs) / BITS, r))
    median = sorted(m for _, _, m, _ in recs)[len(recs) // 2]
    by_ctx: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for current, p_h, mag, r in recs:
        by_ctx.setdefault((current, p_h), []).append((1 if mag > median else 0, r))
    total = sum(len(v) for v in by_ctx.values())
    cond = sum((len(v) / total) * _mi(v) for v in by_ctx.values() if len(v) > 4)
    rng = random.Random(99)
    floors = []
    for _ in range(30):
        f = 0.0
        for v in by_ctx.values():
            if len(v) <= 4:
                continue
            depths = [d for d, _ in v]
            rs = [r for _, r in v]
            rng.shuffle(depths)
            f += (len(v) / total) * _mi(list(zip(depths, rs)))
        floors.append(f)
    return cond, max(floors)


def main() -> None:
    print("conditional composition — does the held past act on the current write?\n")
    print(f"64 (current,past) pairs x {SEEDS} seeds; S = I(R;C,P) - I(R;C) - I(R;P)\n")
    print(f"{'arm':<26}{'S':>9}{'floor':>9}{'I(R;C)':>9}{'I(R;P)':>9}   verdict")
    print("-" * 74)

    def show(name: str, rows: list[tuple[int, int, int]]) -> float:
        s = _interaction(rows)
        floor = _shuffle_floor(rows)
        i_c = _mi([(c, r) for c, _, r in rows])
        i_p = _mi([(p, r) for _, p, r in rows])
        verdict = "S clears floor" if s > floor else "at floor"
        print(f"{name:<26}{s:>9.3f}{floor:>9.3f}{i_c:>9.3f}{i_p:>9.3f}   {verdict}")
        return s

    gate_rows = _collect(1.0, arm="gate")
    show("gate (g=1)", gate_rows)
    show("no-gate (g=0)", _collect(0.0, arm="gate"))
    show("past-copy", _collect(0.0, arm="past_copy"))
    show("current-copy", _collect(0.0, arm="current_copy"))
    show("XOR lookup (planted)", _collect(0.0, arm="xor"))

    print("\n  S is NECESSARY but NOT SUFFICIENT: the planted XOR lookup scores S = 3.000 too —")
    print("  the gate's information signature is IDENTICAL to a designer's rule. The control a")
    print("  lookup cannot fake is DEPTH: does R follow the ANALOG held state beyond its sign?")
    print("  (median |delta| split; the drive is scaled toward the barrier where depth matters)")
    passed = False
    for scale in (0.8, 0.3, 0.12):
        depth, floor = _depth_sensitivity(1.0, scale=scale)
        ok = depth > floor + 0.005
        passed = passed or ok
        note = "follows raw depth ✓" if ok else "no depth signal"
        print(f"    drive scale {scale:.2f}: I(R; depth | current, past-word) "
              f"{depth:.4f} vs floor {floor:.4f}   {note}")

    print("\n  VERDICT: PRUNED." if not passed else "\n  VERDICT: context is genuinely dynamical.")
    if not passed:
        print("  The gate's synergy (S=3.0) is real information-theoretically but is INDISTINGUISHABLE")
        print("  from a planted XOR lookup: at every drive strength the response follows only the")
        print("  SIGN of the held state (its word), never the analog depth — exactly what a symbol-log")
        print("  lookup uses. Root cause: the clean bistable hold that makes the memory FLAT (retention.py")
        print("  = 1.000 through silence) saturates away the sub-word analog information a genuinely")
        print("  dynamical context gate would need. This is a real wall, kin to integration<->representation:")
        print("  you cannot have both a clean-holding memory AND a raw-state-mediated context gate on this")
        print("  latch. So we do NOT claim 'the engine composes'; the frontier claim is pruned. The bound")
        print("  is moot but noted: I(R;C,P) <= 3 bits, context (if any) is paid from the same budget.")


if __name__ == "__main__":
    main()
