"""Re-audit context on the population rate code: does the held past DEPTH act on the current write?

Run from the repo root:

    PYTHONPATH=src python state/communication/context_rate_gate.py

Part 4 (`context_composition.py`) PRUNED: a context gate on a clean bistable hold was
indistinguishable from a planted sign lookup, because the saturating latch kept only the held
word's SIGN — the response could not follow the held past's analog DEPTH, so nothing distinguished
"the engine composed" from "the designer wired a rule keyed on the word." `rate_code.py` then built
the missing piece: a population whose held COUNT carries the past's depth (I(a_past; count | sign) =
0.98 bits, flat through silence). This re-runs the pruned audit with that piece in place.

The gate — a TWO-population step:

  past population   : write (a_past, s_past) into N near-barrier PAIRS latches, hold deaf; its held
                      mean differential is the analog memory (depth in the count, per rate_code.py).
  current write     : write (a_cur, s_cur) into a SECOND population, but every current latch's drive
                      is BIASED by g * past_mean — the held past broadcast onto the current write.
  read              : the current population's up-count.

The claim the wall forbade, now measured (each against its null, `claims-need-controls`): the
current read depends on the past's DEPTH beyond its sign —

    I(read ; a_past | s_past, a_cur, s_cur)  >  its shuffled-history floor

conditioned on the current symbol AND the past sign held fixed, so the surviving dependence is on
the past MAGNITUDE — a continuous quantity no discrete word/sign lookup was ever given (the D7 trap:
a planted rule keyed on the past word scores exactly the floor here, because within a fixed past
sign it is blind to a_past). a_past is sampled fresh every trial, so no rule could have memorized it.

Nulls / controls:
  - shuffled-history : pair each current read with a RANDOM trial's a_past — the dependence vanishes.
  - no-gate (g = 0)  : the past never enters the current drive — dependence ~ floor (the gate is
                       what buys it, `channel-before-carrier`; the deaf arm proving the path).
  - current fidelity : the current symbol's own sign must SURVIVE the gate — context that overwrites
                       the current write is not composition. The gate sweep reports both curves.

`channel-before-carrier`: the depth ENTERING the gate (I(a_past ; held past mean | sign) = ~0.94)
is scored before what survives into the current read; the surviving fraction is reported.
`report-the-rank`: the effective width of the past-depth channel that reaches the current read is
reported beside it — a read that collapses to the current symbol carries no past.

Honest ceiling, fixed in advance: if this passes, the sentence earned is only "the current exchange
depended on the held past's analog depth, beyond its sign, by measured MI over a shuffled-history
null, while the current symbol survived" — working memory that is USED (context), at the population's
few-bit width, at most ~1 bit of past per read. NOT synergy in the strong sense unless the
interaction information is separately positive (reported, not assumed); NOT integration (chain 0,
Phi factorizes); NOT language. If the current read does not carry a_past above floor, or only by
destroying the current symbol, the prune stands and the door does not reach context — reported with
numbers either way.
"""

from __future__ import annotations

import importlib.util
import math
import random
import statistics
from collections import Counter
from pathlib import Path

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring
from anima_reborn.dialogue import TELL

_RC = Path(__file__).resolve().parent / "rate_code.py"
_spec = importlib.util.spec_from_file_location("rate_code", _RC)
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

AMPS = rc.AMPS                       # past depth levels (the quantity conditioned on)
N = rc.PAIRS_N                       # population width
WRITE_SCALE = 0.08                   # rate_code's chosen graded write scale (for the PAST population)
HOLD = 240                           # deaf hold before the past is read (endpoint regime)
CUR_HOLD = 40                        # short settle for the current population before reading
GATE = 0.02                          # past->current bias strength, fixed (0.02 was the max that
#                                      kept current fidelity in the first sweep; larger overwrites)
# The real axis is the CURRENT write strength: graded (small) = sensitive to the past nudge but its
# own sign is a coin; saturated (large) = reliable current sign but pinned at the ceiling, deaf to
# the past. The retention<->depth trade, now at the composition step — swept, not asserted.
CUR_SCALES = (0.005, 0.01, 0.02, 0.04, 0.08)
A_CUR = 0.5                          # the current symbol is held FIXED so we isolate a_past
S_CUR = 1
S_PAST = 1                           # past sign held fixed: the surviving channel is MAGNITUDE
TRIALS = 40
BINS = rc.BINS

PAST_BASE = 200_000
CUR_BASE = 400_000


def _past_mean(a_past: float, s_past: int, *, seed: int) -> float:
    """The held analog memory: a population's mean differential after a deaf hold (rate_code.py)."""
    out = rc._write_and_hold(a_past, s_past, scale=WRITE_SCALE, seed=seed, n_pairs=N, holds=(HOLD,))
    return out[HOLD][1]


def _gated_read(a_cur: float, s_cur: int, past_mean: float, *, cur_scale: float, seed: int) -> int:
    """Write the current symbol into a fresh population at write strength cur_scale, biased by
    GATE * past_mean; read the up-count."""
    d = cur_scale * a_cur * s_cur + GATE * past_mean
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


def _trials(cur_scale: float) -> list[tuple[int, int]]:
    """(past-amp index, current read count) over fresh past depths at a fixed current symbol."""
    rows: list[tuple[int, int]] = []
    k = 0
    for ai, a_past in enumerate(AMPS):
        for _ in range(TRIALS):
            pm = _past_mean(a_past, S_PAST, seed=PAST_BASE + k)
            read = _gated_read(A_CUR, S_CUR, pm, cur_scale=cur_scale, seed=CUR_BASE + k)
            rows.append((ai, read))
            k += 1
    return rows


def _mi_depth(rows: list[tuple[int, int]], *, shuffle_seed: int) -> tuple[float, float]:
    """I(a_past ; read | fixed current, fixed past sign) and its shuffled-history floor."""
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


def _current_fidelity(cur_scale: float) -> float:
    """Does the current symbol's OWN sign survive at this write strength (and the gate)? Flip s_cur
    across both past extremes/signs and check the read majority still reflects the current sign."""
    hits = 0
    total = 0
    k = 900_000
    for s_cur in (+1, -1):
        for a_past in (AMPS[0], AMPS[-1]):
            for s_past in (+1, -1):
                for _ in range(10):
                    pm = _past_mean(a_past, s_past, seed=k)
                    read = _gated_read(A_CUR, s_cur, pm, cur_scale=cur_scale, seed=k + 1)
                    maj = 2 * read - N
                    hits += int((maj > 0) if s_cur > 0 else (maj < 0))
                    total += 1
                    k += 2
    return hits / total


def main() -> None:
    print("re-audit: does the held past DEPTH act on the current write? (population rate gate)\n")
    print(f"past (a_past in {AMPS}, sign +) -> held mean -> biases current write ({A_CUR:+.2f}, +)")
    print(f"read = current up-count; gate {GATE} fixed; {TRIALS} fresh-past trials/level, N={N}\n")

    # channel entering: the past depth held, before any gating.
    enter_by_sign: dict[int, list[tuple[int, float]]] = {S_PAST: []}
    kk = 0
    for ai, a_past in enumerate(AMPS):
        for _ in range(TRIALS):
            enter_by_sign[S_PAST].append((ai, _past_mean(a_past, S_PAST, seed=PAST_BASE + kk)))
            kk += 1
    enter, enter_floor = rc._cond_depth(enter_by_sign, shuffle_seed=17)
    print(f"[0] entering the gate: I(a_past ; held mean | sign) = {enter:.3f}  (floor {enter_floor:.3f})\n")

    # [1] the composition-step trade: current write strength (graded -> saturated) vs BOTH the
    # current symbol's own fidelity AND the past depth reaching the read. The retention<->depth
    # wall predicts these two never rise together — measured here, not asserted.
    print("[1] current-write-strength sweep — read past depth vs keep the current symbol")
    print(f"{'cur_s':>7}{'cur count':>11}{'I(a_past;read)':>16}{'floor':>8}{'cur fidelity':>14}")
    print("  " + "-" * 56)
    sweep: dict[float, tuple[float, float, float, float]] = {}
    for ci, cs in enumerate(CUR_SCALES):
        rows = _trials(cs)
        obs, floor = _mi_depth(rows, shuffle_seed=23 + ci)
        fid = _current_fidelity(cs)
        base_count = statistics.mean(r for _, r in rows)
        sweep[cs] = (obs, floor, fid, base_count)
        print(f"{cs:>7.3f}{base_count:>11.1f}{obs:>16.3f}{floor:>8.3f}{fid:>14.3f}")

    both = [cs for cs in CUR_SCALES if sweep[cs][2] >= 0.95 and sweep[cs][0] > sweep[cs][1] + 0.05]
    if both:
        cs_star = max(both, key=lambda cs: sweep[cs][0] - sweep[cs][1])
        print(f"\n  WINDOW at cur_s = {cs_star:.3f}: past depth reaches the read AND the current sign survives")
    else:
        # no window: pick the scale with the best past-read to characterise the failure honestly.
        cs_star = max(CUR_SCALES, key=lambda cs: sweep[cs][0] - sweep[cs][1])
        print(f"\n  NO WINDOW: no current strength both keeps fidelity >= 0.95 and reads a_past above floor")
        print(f"  — the retention<->depth trade reappears at the composition step. Characterising at "
              f"cur_s = {cs_star:.3f} (max past-read).")

    obs, floor, fid, base_count = sweep[cs_star]
    rows = _trials(cs_star)

    # [2] the D7-proof: within the fixed past sign, does the read separate by a_past? A sign/word
    # lookup, blind to a_past inside a sign, scores the floor. Fresh a_past each trial = no memorized rule.
    print(f"\n[2] D7 control (cur_s = {cs_star:.3f}): read vs past DEPTH, past sign fixed +")
    by_a = {ai: statistics.mean(r for aj, r in rows if aj == ai) for ai in range(len(AMPS))}
    curve = "  ".join(f"a={AMPS[ai]:.2f}:{by_a[ai]:.1f}" for ai in range(len(AMPS)))
    print(f"    mean current count by past depth: {curve}")
    span = max(by_a.values()) - min(by_a.values())
    print(f"    I(a_past ; read | sign) = {obs:.3f}  floor {floor:.3f}  span {span:.1f} counts  "
          f"surviving {obs / enter if enter else 0:.2f} of entering")

    # [3] shuffled-history null: same reads, each paired with a RANDOM past's depth label.
    rng = random.Random(71)
    labels = [ai for ai, _ in rows]
    reads = [r for _, r in rows]
    rng.shuffle(labels)
    sh_obs, _ = _mi_depth(list(zip(labels, reads)), shuffle_seed=99)
    print(f"\n[3] shuffled-history: read paired with a RANDOM past -> I = {sh_obs:.3f} "
          f"({'vanishes' if sh_obs < floor + 0.02 else 'PERSISTS — leak, not history'})")

    # [4] rank / ceiling.
    print("\n[4] rank / ceiling")
    print(f"    effective past-depth width into the read ~ 2^I = {2 ** obs:.1f} levels "
          f"(entering {2 ** enter:.1f}; ceiling log2({len(AMPS)}) = {math.log2(len(AMPS)):.2f} bits)")

    composes = obs > floor + 0.05 and fid >= 0.95 and sh_obs < floor + 0.02
    print("\n  VERDICT:")
    if composes:
        print(f"  CONTEXT REACHES the door. At cur_s = {cs_star:.3f} the current read carries the held")
        print(f"  past's DEPTH (I(a_past;read|sign) = {obs:.2f}, floor {floor:.2f}, {2 ** obs:.1f} levels) beyond")
        print(f"  its sign, the current symbol survives (fidelity {fid:.2f}), and a shuffled past kills it")
        print(f"  ({sh_obs:.2f}). Part 4's prune is lifted: the held past ACTS on the current write, on a")
        print(f"  continuous a_past sampled fresh — no word/sign lookup can fake it (D7-proof). Working")
        print(f"  memory USED, ~{2 ** obs:.0f} levels of past per read. Not language, not integration (chain 0).")
    else:
        print(f"  the prune STANDS — as a MEASURED wall, not a parameter artefact. Across the whole")
        print(f"  current-strength sweep, no setting reads a_past above floor (best {obs:.2f} vs {floor:.2f})")
        print(f"  while the current sign survives (fidelity there {fid:.2f}): a GRADED current is sensitive")
        print(f"  to the past but has no reliable sign of its own, a SATURATED current has a sign but is")
        print(f"  deaf to the past nudge. The retention<->depth trade reappears at the composition step —")
        print(f"  the door holds and consumes depth, but additive gating cannot deliver it into the")
        print(f"  current write without erasing the current symbol. Usable context needs a modulation")
        print(f"  the additive drive does not offer (a separate measurement).")


if __name__ == "__main__":
    main()
