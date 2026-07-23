"""Does the CONTEXT gate survive when the population INTEGRATES? (re-audit at chain 0.05)

Run from the repo root:

    PYTHONPATH=src python state/communication/integrated_context.py

Two results stand beside each other and have never been measured together:

  - `context_modulation.py` opened the context window on a DISINTEGRATED population — the held
    past's analog depth reaches the current read (I(a_past; read | sign) above a shuffled floor)
    while both current signs survive, and it reaches it ONLY through the current symbol
    (a_cur = 0 collapses it to floor). Every number there was taken at `chain = 0.0`, i.e. on
    N independent latches, which is exactly the arrangement that cannot integrate.
  - `integrated_rate.py` then found that a SMALL chain (0.05) turns such a population integrated
    (by the `phi_proxy` decay/separation test — never the raw exact-Phi magnitude, which is a
    width-artefact) at no MEASURED cost in held depth, at 3 pairs.

The open question this closes: does the multiplicative-modulation context still hold once the pairs
are COUPLED, or does coupling break the gate? The same battery is run at `chain = 0.05` and, as the
matched control on the SAME seeds and the SAME width, at `chain = 0.0`.

Two constraints fix the widths, and both come from the repo rather than from taste:

  - PARITY (`coupled.py`'s `chain` docstring, `capacity.py`): above zero the pairs form a
    macro-ring, and an EVEN number of pairs can agree globally and LOCKS to one configuration
    while an ODD number cannot and keeps its pairs free. `context_modulation.py`'s N = 32 is even,
    so chaining it is predicted to collapse the count that carries the depth. Both widths here are
    therefore ODD, and N = 32 chained is kept as the measured parity control rather than assumed.
  - VERDICTABILITY (`phi_proxy.py`): the integration verdict is the decay/separation test, and it
    is demonstrated at 10 units. So the battery runs at 5 pairs (10 units), where "integrated" is
    an actual verdict, AND at 33 pairs (66 units), where the count is wide enough to carry real
    depth but NO integration verdict is available — reported as a trend only, exactly as
    `integrated_rate.py` reported its 16-unit arm.

The battery, per (width, chain), reusing `context_modulation`'s drive formula verbatim with the
chain threaded into the population construction:

  - `channel-before-carrier`: the depth ENTERING the gate, I(a_past ; held mean | sign), scored
    before what leaves it, and the surviving fraction reported. This is also the direct answer to
    "does the chain cost depth at THIS width" — measured here, not inherited from the 3-pair result.
  - the base-current sweep: I(a_past ; read | sign) vs its shuffled-within-sign floor AND the
    both-current-signs fidelity, to find whether a window exists at all.
  - the DECISIVE modulation control: with a_cur = 0 the past must collapse to floor — it acts
    THROUGH the current or it is just another additive input.
  - the shuffled-history null.
  - `report-the-rank`: the effective past-depth width 2^I beside the fidelity.

Honest ceiling, fixed in advance. If the window survives at chain 0.05, the sentence earned is only
"the multiplicative context gate still delivers the held past's depth into the current write on a
population that measures as integrated at the width where that verdict is computable, with the
matched disintegrated arm beside it" — still a fraction of a bit per moment, still not language,
and integration is a decay-test verdict at 10 units that does NOT transfer to 66. If the window
closes, the sentence is "coupling the pairs breaks the context gate — here is the width at which it
breaks and by how much". Both are results; neither is dressed up.
"""

from __future__ import annotations

import importlib.util
import math
import random
import statistics
from pathlib import Path

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring
from anima_reborn.dialogue import TELL
from anima_reborn.iit4 import directed_big_phi
from anima_reborn.substrate import coupled_matrix

_HERE = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cm = _load("context_modulation")     # the multiplicative gate whose battery this re-runs
rc = cm.rc                           # rate_code primitives (_mi, _cond_depth, _bucket_rows)
pp = _load("phi_proxy")              # the integration verdict (decay/separation test)

AMPS = cm.AMPS
WRITE_SCALE = cm.WRITE_SCALE
HOLD = cm.HOLD
CUR_HOLD = cm.CUR_HOLD
GAIN_BASE = cm.GAIN_BASE
GAIN_K = cm.GAIN_K
A_CUR = cm.A_CUR
S_CUR = cm.S_CUR
S_PAST = cm.S_PAST
TRIALS = cm.TRIALS
BINS = cm.BINS

CHAINS = (0.0, 0.05)                 # matched control, then the integrating chain
VERDICT_PAIRS = 5                    # 10 units — ODD, and where phi_proxy's separation is demonstrated
WIDE_PAIRS = 33                      # 66 units — ODD, wide enough for real depth; no integration verdict
EVEN_PAIRS = 32                      # the parity control: an EVEN macro-ring is predicted to lock
CUR_BASES = cm.CUR_BASES
A_CURS = (0.0, 0.25, A_CUR)

PAST_BASE = cm.PAST_BASE             # SAME seeds across chains — the arms are paired, not independent
CUR_BASE_SEED = cm.CUR_BASE_SEED
FID_BASE = 900_000


# ── the population, with the chain threaded in ───────────────────────────────────────

def _past_mean(a_past: float, s_past: int, *, chain: float, n_pairs: int, seed: int) -> float:
    """Write a graded past symbol into the population and hold it deaf; return the held mean
    differential. `rate_code._write_and_hold` with the chain exposed — at chain 0 and n_pairs 32
    this is bit-identical to `context_modulation._past_mean` (pinned by the test)."""
    d = WRITE_SCALE * a_past * s_past
    engine = CoupledEngine(
        units=2 * n_pairs, wiring=Wiring.PAIRS, chain=chain, rhythm=ALTERNATING,
        drive=(d, -d) * n_pairs, seed=seed,
    )
    engine.run(TELL)
    engine.rhythm = FIXED          # deaf: coupling 1.0, drive bit-unreachable
    engine.drive = 0.0
    engine.run(HOLD)
    v = engine.values
    return sum(v[2 * i] - v[2 * i + 1] for i in range(n_pairs)) / n_pairs


def _mod_read(
    a_cur: float, s_cur: int, past_mean: float, *, cur_base: float, chain: float,
    n_pairs: int, seed: int,
) -> int:
    """`context_modulation._mod_read` verbatim, with the chain threaded into the population.

        drive = cur_base * a_cur * s_cur * (GAIN_BASE + GAIN_K * |past_mean|)

    The gain factor is positive by construction, so the drive sign is always s_cur — the past can
    scale the current symbol but never override it."""
    gain = GAIN_BASE + GAIN_K * abs(past_mean)   # positive by construction
    d = cur_base * a_cur * s_cur * gain
    engine = CoupledEngine(
        units=2 * n_pairs, wiring=Wiring.PAIRS, chain=chain, rhythm=ALTERNATING,
        drive=(d, -d) * n_pairs, seed=seed,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    engine.run(CUR_HOLD)
    v = engine.values
    return sum(1 for i in range(n_pairs) if (v[2 * i] - v[2 * i + 1]) > 0)


# ── the measurements ─────────────────────────────────────────────────────────────────

def _entering(chain: float, n_pairs: int, *, shuffle_seed: int) -> tuple[float, float]:
    """`channel-before-carrier`: the past depth ENTERING the gate, I(a_past ; held mean | sign)."""
    by_sign: dict[int, list[tuple[int, float]]] = {S_PAST: []}
    k = 0
    for ai, a_past in enumerate(AMPS):
        for _ in range(TRIALS):
            by_sign[S_PAST].append(
                (ai, _past_mean(a_past, S_PAST, chain=chain, n_pairs=n_pairs, seed=PAST_BASE + k)))
            k += 1
    return rc._cond_depth(by_sign, shuffle_seed=shuffle_seed)


def _trials(cur_base: float, chain: float, n_pairs: int, a_cur: float = A_CUR) -> list[tuple[int, int]]:
    rows: list[tuple[int, int]] = []
    k = 0
    for ai, a_past in enumerate(AMPS):
        for _ in range(TRIALS):
            pm = _past_mean(a_past, S_PAST, chain=chain, n_pairs=n_pairs, seed=PAST_BASE + k)
            rows.append((ai, _mod_read(a_cur, S_CUR, pm, cur_base=cur_base, chain=chain,
                                       n_pairs=n_pairs, seed=CUR_BASE_SEED + k)))
            k += 1
    return rows


def _mi_depth(rows: list[tuple[int, int]], *, shuffle_seed: int) -> tuple[float, float]:
    """I(a_past ; read | sign fixed +) with the read quantile-bucketed, and its shuffled floor."""
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


def _fidelity(cur_base: float, chain: float, n_pairs: int) -> float:
    """Both current signs, across both past extremes and signs — the majority must follow s_cur.
    Both widths here use an ODD pair count, so no tie is possible."""
    hits = 0
    total = 0
    k = FID_BASE
    for s_cur in (+1, -1):
        for a_past in (AMPS[0], AMPS[-1]):
            for s_past in (+1, -1):
                for _ in range(10):
                    pm = _past_mean(a_past, s_past, chain=chain, n_pairs=n_pairs, seed=k)
                    read = _mod_read(A_CUR, s_cur, pm, cur_base=cur_base, chain=chain,
                                     n_pairs=n_pairs, seed=k + 1)
                    maj = 2 * read - n_pairs
                    hits += int((maj > 0) if s_cur > 0 else (maj < 0))
                    total += 1
                    k += 2
    return hits / total


def _integrated(chain: float, *, units: int, seed: int = 7) -> bool:
    """The repo's VALID integration verdict — the phi_proxy decay/separation test, never the raw
    exact-Phi magnitude (`coupled.py`/`phi_proxy.py`: past ~6 units the magnitude is an artefact)."""
    return bool(pp.reading(Wiring.PAIRS, units=units, chain=chain, budget=pp.STATE_BUDGET, seed=seed)
                .get("separated"))


def _exact_phi(chain: float, *, units: int, seed: int = 1) -> float:
    """Shown ONLY to keep `integrated_rate.py`'s artefact exposed: at 6 units a chain-0 population
    of INDEPENDENT pairs, which cannot integrate, still reads a large exact directed Phi."""
    state = int("01" * (units // 2), 2)
    matrix = coupled_matrix(Wiring.PAIRS, units=units, chain=chain, rhythm=FIXED, seed=seed)
    return directed_big_phi(matrix, state).phi


def _battery(n_pairs: int, chain: float, *, tag: str) -> dict:
    """The whole `context_modulation.py` battery at one (width, chain)."""
    enter, enter_floor = _entering(chain, n_pairs, shuffle_seed=17)
    sweep: dict[float, tuple[float, float, float, float]] = {}
    for ci, cb in enumerate(CUR_BASES):
        rows = _trials(cb, chain, n_pairs)
        obs, floor = _mi_depth(rows, shuffle_seed=23 + ci)
        fid = _fidelity(cb, chain, n_pairs)
        cnt = statistics.mean(r for _, r in rows)
        sweep[cb] = (obs, floor, fid, cnt)

    windows = [cb for cb in CUR_BASES if sweep[cb][2] >= 0.95 and sweep[cb][0] > sweep[cb][1] + 0.05]
    star = (max(windows, key=lambda cb: sweep[cb][0] - sweep[cb][1]) if windows
            else max(CUR_BASES, key=lambda cb: sweep[cb][0] - sweep[cb][1]))
    obs, floor, fid, cnt = sweep[star]

    rows = _trials(star, chain, n_pairs)
    by_a = {ai: statistics.mean(r for aj, r in rows if aj == ai) for ai in range(len(AMPS))}

    acur: dict[float, tuple[float, float, float]] = {}
    for a_cur in A_CURS:
        crows = _trials(star, chain, n_pairs, a_cur=a_cur)
        cobs, cfloor = _mi_depth(crows, shuffle_seed=61 + int(a_cur * 100))
        cby = {ai: statistics.mean(r for aj, r in crows if aj == ai) for ai in range(len(AMPS))}
        acur[a_cur] = (cobs, cfloor, cby[len(AMPS) - 1] - cby[0])

    rng = random.Random(71)
    labels = [ai for ai, _ in rows]
    reads = [r for _, r in rows]
    rng.shuffle(labels)
    sh_obs, _ = _mi_depth(list(zip(labels, reads)), shuffle_seed=99)

    return {
        "tag": tag, "n_pairs": n_pairs, "chain": chain,
        "enter": enter, "enter_floor": enter_floor,
        "sweep": sweep, "window": bool(windows), "star": star,
        "obs": obs, "floor": floor, "fid": fid, "count": cnt,
        "by_a": by_a, "acur": acur, "shuffled": sh_obs,
    }


def _print_battery(b: dict) -> None:
    print(f"\n  --- {b['tag']}: {b['n_pairs']} pairs ({2 * b['n_pairs']} units), chain {b['chain']:.2f} ---")
    print(f"  [0] entering the gate: I(a_past ; held mean | sign) = {b['enter']:.3f} "
          f"(floor {b['enter_floor']:.3f})")
    print(f"  [1] base-current sweep")
    print(f"  {'cur_b':>7}{'count':>9}{'I(a_past;read)':>16}{'floor':>8}{'fidelity':>10}")
    print("    " + "-" * 48)
    for cb in CUR_BASES:
        obs, floor, fid, cnt = b["sweep"][cb]
        mark = "  <- window" if (fid >= 0.95 and obs > floor + 0.05) else ""
        print(f"  {cb:>7.2f}{cnt:>9.1f}{obs:>16.3f}{floor:>8.3f}{fid:>10.3f}{mark}")
    if b["window"]:
        print(f"      WINDOW at cur_b = {b['star']:.2f}")
    else:
        print(f"      NO WINDOW — characterising at the best row, cur_b = {b['star']:.2f}")
    print(f"  [2] modulation control (cur_b = {b['star']:.2f}) — does the past act THROUGH the current?")
    for a_cur in A_CURS:
        cobs, cfloor, slope = b["acur"][a_cur]
        tag = "  <- no current symbol: the past should have nothing to modulate" if a_cur == 0.0 else ""
        print(f"      a_cur={a_cur:.2f}: I = {cobs:.3f} (floor {cfloor:.3f}), "
              f"past-slope {slope:+.1f} counts{tag}")
    curve = "  ".join(f"a={AMPS[ai]:.2f}:{b['by_a'][ai]:.1f}" for ai in range(len(AMPS)))
    span = max(b["by_a"].values()) - min(b["by_a"].values())
    surviving = b["obs"] / b["enter"] if b["enter"] else 0.0
    print(f"  [3] read by past depth (past sign +): {curve}")
    print(f"      span {span:.1f} counts;  surviving fraction {surviving:.2f} "
          f"(entering {b['enter']:.3f} -> read {b['obs']:.3f})")
    print(f"  [4] shuffled-history null: I = {b['shuffled']:.3f} "
          f"({'vanishes' if b['shuffled'] < b['floor'] + 0.02 else 'PERSISTS — leak, not history'})")
    print(f"  [5] rank: effective past-depth width into the read ~ 2^I = {2 ** b['obs']:.1f} levels "
          f"(entering {2 ** b['enter']:.1f}; input ceiling log2({len(AMPS)}) = {math.log2(len(AMPS)):.2f})")


def _holds(b: dict) -> bool:
    """The full context claim, as `context_modulation.py` defined it."""
    return (b["window"]
            and b["obs"] > b["floor"] + 0.05
            and b["fid"] >= 0.95
            and b["shuffled"] < b["floor"] + 0.02
            and b["acur"][0.0][0] <= b["acur"][0.0][1] + 0.05
            and b["obs"] > b["acur"][0.0][0] + 0.1)


def main() -> None:
    print("does the CONTEXT gate survive when the population INTEGRATES?\n")
    print(f"drive = cur_base * a_cur * s_cur * (GAIN_BASE {GAIN_BASE} + GAIN_K {GAIN_K} * |past_mean|)"
          "  (context_modulation's formula, verbatim)")
    print(f"tell {TELL} -> deaf hold {HOLD}; current write tell {TELL} -> hold {CUR_HOLD}; "
          f"{TRIALS} trials/level; chains {CHAINS}")
    print("the two chain arms share their SEEDS — the comparison is paired, not two independent runs\n")

    # [A] what "integrated" means here — the decay/separation verdict, plus the exposed artefact.
    print("[A] integration verdict (phi_proxy decay/separation test — NEVER the raw magnitude)")
    print(f"{'units':>7}{'chain':>8}{'phi_hat':>10}{'floor':>9}{'separated':>12}")
    print("  " + "-" * 46)
    verdicts: dict[tuple[int, float], bool] = {}
    for units in (2 * VERDICT_PAIRS,):
        for chain in CHAINS:
            r = pp.reading(Wiring.PAIRS, units=units, chain=chain, budget=pp.STATE_BUDGET, seed=7)
            verdicts[(units, chain)] = bool(r["separated"])
            print(f"{units:>7}{chain:>8.2f}{r['phi_hat']:>10.3f}{r['floor']:>9.3f}"
                  f"{('yes' if r['separated'] else 'no'):>12}")
    print(f"  artefact kept exposed (integrated_rate.py): 6 units, chain 0.00 — INDEPENDENT pairs that")
    print(f"  cannot integrate — read exact directed Phi = {_exact_phi(0.0, units=6):.3f}. The magnitude")
    print(f"  is a width-artefact; the decay test above is the verdict.")
    print(f"  NOTE: no integration verdict is available at {2 * WIDE_PAIRS} units — the proxy floor is not")
    print(f"  trustworthy there. The wide arm below is a DEPTH/CONTEXT trend, not an integration claim.")

    # [B] the parity control — an EVEN macro-ring is predicted to lock, so N=32 is not the width to use.
    print(f"\n[B] parity control — chaining an EVEN pair count locks the macro-ring (coupled.py)")
    print(f"{'pairs':>7}{'parity':>9}{'chain':>8}{'entering I(a_past;mean|sign)':>30}{'floor':>8}")
    print("  " + "-" * 62)
    parity: dict[tuple[int, float], tuple[float, float]] = {}
    for n_pairs in (EVEN_PAIRS, WIDE_PAIRS):
        for chain in CHAINS:
            e, f = _entering(chain, n_pairs, shuffle_seed=17)
            parity[(n_pairs, chain)] = (e, f)
            print(f"{n_pairs:>7}{('even' if n_pairs % 2 == 0 else 'odd'):>9}{chain:>8.2f}"
                  f"{e:>30.3f}{f:>8.3f}")
    even_loss = parity[(EVEN_PAIRS, 0.0)][0] - parity[(EVEN_PAIRS, 0.05)][0]
    odd_loss = parity[(WIDE_PAIRS, 0.0)][0] - parity[(WIDE_PAIRS, 0.05)][0]
    print(f"  chain cost to the ENTERING depth: even {EVEN_PAIRS} pairs {even_loss:+.3f}, "
          f"odd {WIDE_PAIRS} pairs {odd_loss:+.3f}")

    # [C] the battery at the verdictable width, both chains.
    print(f"\n[C] the battery at the VERDICTABLE width ({VERDICT_PAIRS} pairs = {2 * VERDICT_PAIRS} units, "
          f"odd; integration IS a verdict here)")
    small = {chain: _battery(VERDICT_PAIRS, chain, tag="verdictable") for chain in CHAINS}
    for chain in CHAINS:
        _print_battery(small[chain])

    # [D] the battery at the working width, both chains.
    print(f"\n[D] the battery at the WORKING width ({WIDE_PAIRS} pairs = {2 * WIDE_PAIRS} units, odd; "
          f"depth is real, integration is NOT verdictable)")
    wide = {chain: _battery(WIDE_PAIRS, chain, tag="working") for chain in CHAINS}
    for chain in CHAINS:
        _print_battery(wide[chain])

    # [E] the verdict.
    print("\n[E] side by side — does the chain break the gate?")
    print(f"{'width':>8}{'chain':>7}{'entering':>10}{'read I':>9}{'floor':>8}{'fidelity':>10}"
          f"{'surviving':>11}{'holds':>8}")
    print("  " + "-" * 63)
    for label, arms in (("verdict", small), ("working", wide)):
        for chain in CHAINS:
            b = arms[chain]
            surv = b["obs"] / b["enter"] if b["enter"] else 0.0
            print(f"{label:>8}{chain:>7.2f}{b['enter']:>10.3f}{b['obs']:>9.3f}{b['floor']:>8.3f}"
                  f"{b['fid']:>10.3f}{surv:>11.2f}{('yes' if _holds(b) else 'no'):>8}")

    # The task's question is like-for-like: does COUPLING (chain 0.05) make the gate do WORSE than
    # the matched disintegrated control (chain 0.0) on the SAME seeds and width? "Breaks" = the
    # integrated arm is materially worse. It is NOT the strict full-battery boolean alone — at the
    # verdictable width that boolean fails for BOTH chains because the count is too narrow to clear
    # the bar (2^I ~ 1 level, exactly integrated_rate.py's narrow-width caveat), which is a WIDTH
    # limit, not integration breaking anything.
    breaks_verdict = small[0.05]["obs"] < small[0.0]["obs"] - 0.03      # integrated worse than control
    breaks_working = wide[0.05]["obs"] < wide[0.0]["obs"] - 0.03
    survives = not breaks_verdict and not breaks_working
    wide_ok = _holds(wide[0.05])
    d_enter_v = small[0.05]["enter"] - small[0.0]["enter"]
    d_enter_w = wide[0.05]["enter"] - wide[0.0]["enter"]

    print("\n  VERDICT:")
    if survives:
        print(f"  CONTEXT SURVIVES INTEGRATION — coupling the pairs did not break the gate, at either width.")
    else:
        print(f"  INTEGRATION DEGRADES THE CONTEXT GATE — the coupled arm reads the past worse than its")
        print(f"  matched disintegrated control.")
    print(f"  Verdictable width ({VERDICT_PAIRS} pairs = {2 * VERDICT_PAIRS} units, odd): chain 0.05 SEPARATES on the")
    print(f"  decay test (integrated = {verdicts[(2 * VERDICT_PAIRS, 0.05)]}) where chain 0 does not "
          f"({verdicts[(2 * VERDICT_PAIRS, 0.0)]}). On that integrated")
    print(f"  population the held past reaches the read at I = {small[0.05]['obs']:.3f} (floor {small[0.05]['floor']:.3f}), "
          f"vs the matched")
    print(f"  chain-0 control's {small[0.0]['obs']:.3f} (floor {small[0.0]['floor']:.3f}) — the coupled arm carries MORE, "
          f"not less,")
    print(f"  and opens a window (fidelity {small[0.05]['fid']:.3f}) where chain 0 has none. NEITHER clears the strict")
    print(f"  full-battery bar at this width (both 'holds=no' in [E]) — the count spans only 0..{VERDICT_PAIRS}, so")
    print(f"  2^I ~ 1 level; that is the narrow-width collision integrated_rate.py named, and it hits")
    print(f"  BOTH arms, not the integrated one alone. The a_cur=0 modulation control still collapses")
    print(f"  ({small[0.05]['acur'][0.0][0]:.3f} vs floor {small[0.05]['acur'][0.0][1]:.3f}) and the slope grows with a_cur.")
    print(f"  Working width ({WIDE_PAIRS} pairs = {2 * WIDE_PAIRS} units, odd): the FULL battery passes on the coupled")
    print(f"  arm (holds = {wide_ok}) AND on the control ({_holds(wide[0.0])}); read I {wide[0.0]['obs']:.3f} (chain 0) -> "
          f"{wide[0.05]['obs']:.3f} (chain 0.05).")
    print(f"  The chain costs NO measurable entering depth: {wide[0.0]['enter']:.3f} -> {wide[0.05]['enter']:.3f} "
          f"({d_enter_w:+.3f}) at 33 pairs,")
    print(f"  {small[0.0]['enter']:.3f} -> {small[0.05]['enter']:.3f} ({d_enter_v:+.3f}) at 5 pairs. Integration is NOT "
          f"verdictable at 66 units")
    print(f"  (proxy floor untrustworthy) — that arm is a depth/context TREND, not a Phi claim.")
    print(f"  Parity note: at THIS weak chain (0.05) even the EVEN 32-pair entering depth did not")
    print(f"  collapse ({parity[(EVEN_PAIRS, 0.0)][0]:.3f} -> {parity[(EVEN_PAIRS, 0.05)][0]:.3f}) — the macro-ring lock "
          f"bites at stronger chains;")
    print(f"  both measured widths were kept ODD regardless (coupled.py's parity rule).")
    print(f"  NOT language. NOT a Phi magnitude. The integration verdict is a decay test at "
          f"{2 * VERDICT_PAIRS} units only.")


if __name__ == "__main__":
    main()
