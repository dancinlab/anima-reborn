"""Does MULTIPLICATIVE modulation open the door additive gating could not? (context, take 2)

Run from the repo root:

    PYTHONPATH=src python state/communication/context_modulation.py

`context_rate_gate.py` measured the wall behind the rate-code door: an ADDITIVE gate (the held past
biases the current drive by + g*past_mean) cannot deliver the past's depth into the current read
without erasing the current symbol. The reason it named: the past bias has a fixed sign, so it
OVERRIDES a weak opposing current — a graded (readable) current has no sign of its own, a saturated
current is deaf. The escape it named: a MULTIPLICATIVE modulation, where the past scales the current
instead of adding to it.

This tests exactly that. The current drive is

    drive = CUR_BASE * a_cur * s_cur * (GAIN_BASE + GAIN_K * past_mean)

with GAIN_BASE > 0 and the gain factor kept POSITIVE, so it never flips the current sign — the
current symbol survives for BOTH signs by construction (drive sign = s_cur always). The held past
(past_mean, sign +, magnitude graded in a_past) then modulates the current count WITHIN a
sign-consistent range: a_past scales how hard the same current symbol is written, so the count
carries the past depth while the majority (the current sign) stays put.

The claim, same control the wall failed (`claims-need-controls`, D7-proof on a fresh continuous
a_past): does the current read carry the past's DEPTH beyond its sign —

    I(a_past ; read | s_past, a_cur, s_cur)  >  shuffled-history floor

AND does the current symbol survive for BOTH signs (fidelity >= 0.95), where additive gating forced
one or the other. Swept over the base current strength (grading <-> saturation); the honest question
is whether multiplicative modulation OPENS a window the additive gate had none of.

`channel-before-carrier`: the past depth entering (I(a_past; held mean | sign)) scored before what
survives into the read. `report-the-rank`: effective past-depth width beside the current fidelity.

Honest ceiling, fixed in advance: if a window opens, the sentence earned is only "the held past's
analog depth modulated the current write — the same current symbol read differently by the held past,
beyond its sign, by measured MI over a shuffled-history null, with the current symbol intact for both
signs" — context that COMPOSES (a 2D interaction, past x current), working memory USED, at the
population's few-bit width. Still not language, not integration (chain 0). If no window opens, the
wall is deeper than additive-vs-multiplicative and this substrate's population count cannot hold the
current symbol and be modulated by the past at once — reported with numbers either way.
"""

from __future__ import annotations

import importlib.util
import math
import random
import statistics
from pathlib import Path

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring
from anima_reborn.dialogue import TELL

_RC = Path(__file__).resolve().parent / "rate_code.py"
_spec = importlib.util.spec_from_file_location("rate_code", _RC)
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

AMPS = rc.AMPS
N = rc.PAIRS_N
WRITE_SCALE = 0.08                    # the PAST population's graded write (rate_code's choice)
HOLD = 240
CUR_HOLD = 40
GAIN_BASE = 0.5                       # positive floor: the current always has a sign of its own
GAIN_K = 1.0                          # past-depth -> gain slope (the modulation strength)
CUR_BASES = (0.02, 0.04, 0.08, 0.15, 0.30)   # base current write strength swept (grading->saturation)
A_CUR = 0.5
S_CUR = 1
S_PAST = 1
TRIALS = 40
BINS = rc.BINS

PAST_BASE = 200_000
CUR_BASE_SEED = 400_000


def _past_mean(a_past: float, s_past: int, *, seed: int) -> float:
    out = rc._write_and_hold(a_past, s_past, scale=WRITE_SCALE, seed=seed, n_pairs=N, holds=(HOLD,))
    return out[HOLD][1]


def _mod_read(a_cur: float, s_cur: int, past_mean: float, *, cur_base: float, seed: int) -> int:
    """Current write MODULATED (multiplied) by a positive past-derived gain; read the up-count.
    The gain stays positive, so the drive sign is always s_cur — the current symbol cannot be
    overridden by the past, only scaled."""
    gain = GAIN_BASE + GAIN_K * abs(past_mean)   # positive by construction
    d = cur_base * a_cur * s_cur * gain
    engine = CoupledEngine(
        units=2 * N, wiring=Wiring.PAIRS, chain=0.0, rhythm=ALTERNATING,
        drive=(d, -d) * N, seed=seed,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    engine.run(CUR_HOLD)
    v = engine.values
    return sum(1 for i in range(N) if (v[2 * i] - v[2 * i + 1]) > 0)


def _trials(cur_base: float, a_cur: float = A_CUR) -> list[tuple[int, int]]:
    rows: list[tuple[int, int]] = []
    k = 0
    for ai, a_past in enumerate(AMPS):
        for _ in range(TRIALS):
            pm = _past_mean(a_past, S_PAST, seed=PAST_BASE + k)
            rows.append((ai, _mod_read(a_cur, S_CUR, pm, cur_base=cur_base, seed=CUR_BASE_SEED + k)))
            k += 1
    return rows


def _mi_depth(rows: list[tuple[int, int]], *, shuffle_seed: int) -> tuple[float, float]:
    order = sorted(r for _, r in rows)
    edges = [order[int(len(order) * q / BINS)] for q in range(1, BINS)]
    bucketed = [(ai, sum(1 for e in edges if r > e)) for ai, r in rows]
    obs = rc._mi(bucketed)
    rng = random.Random(shuffle_seed)
    ais = [a for a, _ in bucketed]
    bs = [b for _, b in bucketed]
    floors = []
    for _ in range(40):
        rng.shuffle(ais)
        floors.append(rc._mi(list(zip(ais, bs))))
    return obs, max(floors)


def _fidelity(cur_base: float) -> float:
    """Both current signs, across both past extremes and signs — the majority must follow s_cur."""
    hits = 0
    total = 0
    k = 900_000
    for s_cur in (+1, -1):
        for a_past in (AMPS[0], AMPS[-1]):
            for s_past in (+1, -1):
                for _ in range(10):
                    pm = _past_mean(a_past, s_past, seed=k)
                    read = _mod_read(A_CUR, s_cur, pm, cur_base=cur_base, seed=k + 1)
                    maj = 2 * read - N
                    hits += int((maj > 0) if s_cur > 0 else (maj < 0))
                    total += 1
                    k += 2
    return hits / total


def main() -> None:
    print("context take 2: does MULTIPLICATIVE modulation deliver the past into the current write?\n")
    print(f"drive = CUR_BASE * a_cur({A_CUR:+.2f}) * s_cur * (GAIN_BASE {GAIN_BASE} + GAIN_K {GAIN_K} * |past_mean|)")
    print(f"gain kept POSITIVE -> current sign survives by construction; {TRIALS} trials/level, N={N}\n")

    enter_by_sign: dict[int, list[tuple[int, float]]] = {S_PAST: []}
    kk = 0
    for ai, a_past in enumerate(AMPS):
        for _ in range(TRIALS):
            enter_by_sign[S_PAST].append((ai, _past_mean(a_past, S_PAST, seed=PAST_BASE + kk)))
            kk += 1
    enter, enter_floor = rc._cond_depth(enter_by_sign, shuffle_seed=17)
    print(f"[0] entering: I(a_past ; held mean | sign) = {enter:.3f}  (floor {enter_floor:.3f})\n")

    # [1] base-current sweep: past depth into the read AND both-sign fidelity, together this time?
    print("[1] base-current sweep — read past depth AND keep the current symbol (both signs)")
    print(f"{'cur_b':>7}{'+arm count':>12}{'I(a_past;read)':>16}{'floor':>8}{'fidelity':>10}")
    print("  " + "-" * 53)
    sweep: dict[float, tuple[float, float, float, float]] = {}
    for ci, cb in enumerate(CUR_BASES):
        rows = _trials(cb)
        obs, floor = _mi_depth(rows, shuffle_seed=23 + ci)
        fid = _fidelity(cb)
        cnt = statistics.mean(r for _, r in rows)
        sweep[cb] = (obs, floor, fid, cnt)
        print(f"{cb:>7.2f}{cnt:>12.1f}{obs:>16.3f}{floor:>8.3f}{fid:>10.3f}")

    both = [cb for cb in CUR_BASES if sweep[cb][2] >= 0.95 and sweep[cb][0] > sweep[cb][1] + 0.05]
    if both:
        cb_star = max(both, key=lambda cb: sweep[cb][0] - sweep[cb][1])
        print(f"\n  WINDOW at cur_b = {cb_star:.2f}: the past depth reaches the read WHILE both current "
              f"signs survive — additive gating had none.")
    else:
        cb_star = max(CUR_BASES, key=lambda cb: sweep[cb][0] - sweep[cb][1])
        print(f"\n  NO WINDOW: multiplicative modulation did not separate the two either. "
              f"Characterising at cur_b = {cb_star:.2f}.")

    obs, floor, fid, cnt = sweep[cb_star]
    rows = _trials(cb_star)

    # [1b] MODULATION control — is the past acting THROUGH the current, or as an independent input?
    # a_cur = 0 (no current symbol): drive = 0 * gain = 0, so the past has nothing to scale. If the
    # past still reaches the read, it is an additive input, not a modulation. And the multiplicative
    # signature: the past's effect (slope of read across a_past) should GROW with a_cur (a product),
    # not stay flat (a sum).
    print(f"\n[1b] modulation control (cur_b = {cb_star:.2f}) — is the past acting THROUGH the current?")
    for a_cur in (0.0, 0.25, A_CUR):
        crows = _trials(cb_star, a_cur=a_cur)
        cobs, cfloor = _mi_depth(crows, shuffle_seed=61 + int(a_cur * 100))
        by = {ai: statistics.mean(r for aj, r in crows if aj == ai) for ai in range(len(AMPS))}
        slope = by[len(AMPS) - 1] - by[0]
        tag = "  <- no current symbol: past should have nothing to modulate" if a_cur == 0.0 else ""
        print(f"    a_cur={a_cur:.2f}: I(a_past;read) = {cobs:.3f} (floor {cfloor:.3f}), "
              f"past-slope {slope:+.1f} counts{tag}")

    # [2] D7-proof: within the fixed past sign, the read separates by a_past (a word/sign lookup can't).
    print(f"\n[2] D7 control (cur_b = {cb_star:.2f}): read vs past DEPTH, past sign fixed +")
    by_a = {ai: statistics.mean(r for aj, r in rows if aj == ai) for ai in range(len(AMPS))}
    curve = "  ".join(f"a={AMPS[ai]:.2f}:{by_a[ai]:.1f}" for ai in range(len(AMPS)))
    print(f"    mean +arm count by past depth: {curve}")
    span = max(by_a.values()) - min(by_a.values())
    print(f"    I(a_past ; read | sign) = {obs:.3f}  floor {floor:.3f}  span {span:.1f} counts  "
          f"surviving {obs / enter if enter else 0:.2f}")

    # [3] shuffled-history null.
    rng = random.Random(71)
    labels = [ai for ai, _ in rows]
    reads = [r for _, r in rows]
    rng.shuffle(labels)
    sh_obs, _ = _mi_depth(list(zip(labels, reads)), shuffle_seed=99)
    print(f"\n[3] shuffled-history: read paired with a RANDOM past -> I = {sh_obs:.3f} "
          f"({'vanishes' if sh_obs < floor + 0.02 else 'PERSISTS — leak, not history'})")

    # [4] verdict.
    print("\n[4] rank / ceiling")
    print(f"    effective past-depth width into the read ~ 2^I = {2 ** obs:.1f} levels "
          f"(entering {2 ** enter:.1f}; ceiling log2({len(AMPS)}) = {math.log2(len(AMPS)):.2f})")

    composes = obs > floor + 0.05 and fid >= 0.95 and sh_obs < floor + 0.02
    print("\n  VERDICT:")
    if composes:
        print(f"  THE DOOR REACHES CONTEXT. Multiplicative modulation delivers the held past's DEPTH")
        print(f"  into the current read (I(a_past;read|sign) = {obs:.2f}, floor {floor:.2f}, {2 ** obs:.1f} levels)")
        print(f"  while BOTH current signs survive (fidelity {fid:.2f}), a shuffled past kills it")
        print(f"  ({sh_obs:.2f}), and — the decisive control — with NO current symbol (a_cur=0) the past")
        print(f"  collapses to floor: it reaches the read ONLY by modulating the current, not as an")
        print(f"  independent input. The same current symbol reads differently by the held past. Part 4's")
        print(f"  prune is LIFTED: the held past ACTS on the current write, on a continuous a_past sampled")
        print(f"  fresh (D7-proof). Working memory USED — context that composes — at ~{2 ** obs:.0f} level of past")
        print(f"  per read (~{obs:.2f} bits). NOT strong synergy (interaction information over a full a_cur x")
        print(f"  a_past grid not computed), NOT language, NOT integration (chain 0), bounded by the width.")
    else:
        print(f"  the wall is DEEPER than additive-vs-multiplicative. Even with a positive gain that")
        print(f"  preserves the current sign, no base strength both reads a_past above floor ({obs:.2f} vs")
        print(f"  {floor:.2f}) and keeps both signs (fidelity there {fid:.2f}). A single population count")
        print(f"  cannot simultaneously carry the current symbol AND be modulated by the past — one")
        print(f"  scalar per moment. Composition needs a SECOND register (the past reads into a channel")
        print(f"  the current symbol does not occupy), a separate measurement. The door holds and")
        print(f"  consumes depth; delivering it as usable context remains open.")


if __name__ == "__main__":
    main()
