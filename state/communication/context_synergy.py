"""Is the modulation genuine SYNERGY? Interaction information over the a_cur x a_past grid.

Run from the repo root:

    PYTHONPATH=src python state/communication/context_synergy.py

`context_modulation.py` landed the honest claim that the held past MODULATES the current write (the
past reaches the read only through the current: a_cur=0 collapses it to floor), but it explicitly
left ONE caveat open — it did NOT compute the interaction information over a full a_cur x a_past
grid, so it stopped short of calling the composition "synergy" in the strict sense. This closes that
caveat, the only one the shipped result named.

Interaction information (co-information) of the read R with the two inputs:

    II = I(R ; A_cur, A_past) - I(R ; A_cur) - I(R ; A_past)

II > 0 is SYNERGY: the read tells you more about the pair jointly than about the two separately —
the signature of a genuine interaction (a product), the composition being MORE than the sum. II ~ 0
(or < 0, redundant) is what a purely additive channel gives: the read is a sum a_cur + a_past, so
the joint adds nothing over the marginals. Measured for BOTH gates as the decisive contrast:

  - MULTIPLICATIVE gate (`context_modulation._mod_read`, the window cur_base=0.04): expected II > 0.
  - ADDITIVE gate (`context_rate_gate._gated_read`, its readable regime): expected II ~ 0 / < 0.

Grid: a_cur in a few magnitudes (sign +), a_past in the usual levels (sign +); the read is the
current up-count, quantile-bucketed. II is scored against a shuffled-label floor
(`claims-need-controls`); the marginals are reported beside it (`report-the-rank`: the joint width
vs the marginal widths).

Honest ceiling: if II_mult > 0 above floor while II_add is not, the shipped claim upgrades from
"the past modulates the current" to "the composition is synergistic — the read carries the pair
(past, current) beyond the sum of each" — still bounded by the population width (a fraction of a bit),
still not language, still not integration (chain 0). If II_mult is not above floor, the claim STAYS
"modulation, not synergy" exactly as `context_modulation.py` already conservatively stated — no
retraction, the caveat simply holds.
"""

from __future__ import annotations

import importlib.util
import math
import random
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cm = _load("context_modulation")     # multiplicative gate + rate_code primitives (cm.rc)
cg = _load("context_rate_gate")      # additive gate

A_CURS = (0.2, 0.4, 0.6)             # current symbol magnitudes (sign +)
A_PASTS = cm.AMPS                    # past depths (sign +)
TRIALS = 40
BINS = 6
MULT_BASE = 0.04                     # the multiplicative window (RESULTS)
ADD_SCALE = 0.02                     # the additive gate's most-readable retaining regime

PAST_SEED = 300_000
READ_SEED = 600_000


def _grid_reads(kind: str) -> list[tuple[int, int, int]]:
    """(a_cur index, a_past index, read count) over the full grid, for one gate kind."""
    rows: list[tuple[int, int, int]] = []
    k = 0
    for ci, a_cur in enumerate(A_CURS):
        for pj, a_past in enumerate(A_PASTS):
            for _ in range(TRIALS):
                pm = cm._past_mean(a_past, +1, seed=PAST_SEED + k)
                if kind == "mult":
                    r = cm._mod_read(a_cur, +1, pm, cur_base=MULT_BASE, seed=READ_SEED + k)
                else:
                    r = cg._gated_read(a_cur, +1, pm, cur_scale=ADD_SCALE, seed=READ_SEED + k)
                rows.append((ci, pj, r))
                k += 1
    return rows


def _mi(pairs: list[tuple]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    joint = Counter(pairs)
    ma = Counter(a for a, _ in pairs)
    mb = Counter(b for _, b in pairs)
    return sum((c / n) * math.log2((c / n) / ((ma[a] / n) * (mb[b] / n)))
               for (a, b), c in joint.items())


def _bucket(reads: list[int]) -> list[int]:
    order = sorted(reads)
    edges = [order[int(len(order) * q / BINS)] for q in range(1, BINS)]
    return [sum(1 for e in edges if r > e) for r in reads]


def _interaction(rows: list[tuple[int, int, int]], *, shuffle_seed: int):
    """II = I(R;cur,past) - I(R;cur) - I(R;past), and a shuffled-label floor for II."""
    buckets = _bucket([r for *_, r in rows])
    cur = [c for c, _, _ in rows]
    past = [p for _, p, _ in rows]
    i_joint = _mi(list(zip(zip(cur, past), buckets)))
    i_cur = _mi(list(zip(cur, buckets)))
    i_past = _mi(list(zip(past, buckets)))
    ii = i_joint - i_cur - i_past
    # floor: shuffle the READ buckets against fixed (cur,past) labels -> destroys all structure,
    # the residual II is the estimator's bias at this sample size (should sit near 0).
    rng = random.Random(shuffle_seed)
    floors = []
    b = list(buckets)
    for _ in range(40):
        rng.shuffle(b)
        fj = _mi(list(zip(zip(cur, past), b)))
        fc = _mi(list(zip(cur, b)))
        fp = _mi(list(zip(past, b)))
        floors.append(fj - fc - fp)
    return ii, i_joint, i_cur, i_past, max(floors), sum(floors) / len(floors)


def main() -> None:
    print("is the modulation SYNERGY? interaction information over the a_cur x a_past grid\n")
    print(f"grid: a_cur {A_CURS} x a_past {A_PASTS} (both sign +), {TRIALS} trials/cell, read = up-count\n")
    print(f"{'gate':>14}{'II':>9}{'floor(max)':>12}{'I(R;joint)':>12}{'I(R;cur)':>10}{'I(R;past)':>11}")
    print("  " + "-" * 66)
    results = {}
    for kind, base, label in (("mult", MULT_BASE, f"MULTIPLICATIVE"), ("add", ADD_SCALE, "ADDITIVE")):
        rows = _grid_reads(kind)
        ii, ij, ic, ip, fmax, fmean = _interaction(rows, shuffle_seed=31 if kind == "mult" else 37)
        results[kind] = (ii, fmax)
        print(f"{label:>14}{ii:>9.3f}{fmax:>12.3f}{ij:>12.3f}{ic:>10.3f}{ip:>11.3f}")

    ii_m, f_m = results["mult"]
    ii_a, f_a = results["add"]
    print("\n  VERDICT:")
    synergy = ii_m > f_m + 0.02
    add_synergy = ii_a > f_a + 0.02
    if synergy:
        print(f"  SYNERGY, measured — but honestly bounded. The multiplicative gate's read carries the")
        print(f"  PAIR (past, current) beyond the sum of each: II = {ii_m:.3f} > floor {f_m:.3f} (margin")
        print(f"  {ii_m - f_m:.3f}). So the composition is genuinely super-additive — the held past and the")
        print(f"  current symbol INTERACT in the read, not merely superpose. `context_modulation.py`'s one")
        print(f"  open caveat closes: the modulation IS synergy, at the population's fraction-of-a-bit width.")
        if add_synergy:
            print(f"  HONEST CONTRAST, NOT A CLEAN NULL: the ADDITIVE gate also shows a WEAKER interaction")
            print(f"  (II = {ii_a:.3f} > floor {f_a:.3f}, margin {ii_a - f_a:.3f}) — the count's SATURATING")
            print(f"  nonlinearity makes any two inputs interact a little. The contrast is QUANTITATIVE")
            print(f"  ({ii_m:.3f} vs {ii_a:.3f}, and further above its floor), not 'multiplicative synergy vs")
            print(f"  zero'. Multiplicative synergy is real and ~{ii_m / ii_a:.1f}x larger; that is the claim.")
        else:
            print(f"  The additive gate sits at its floor (II = {ii_a:.3f}, floor {f_a:.3f}) — synergy is the")
            print(f"  multiplicative gate's, as expected. Still not language, not integration (chain 0).")
    else:
        print(f"  NO synergy above floor (II = {ii_m:.3f} vs floor {f_m:.3f}). The claim STAYS exactly as")
        print(f"  context_modulation.py stated it — MODULATION, not synergy. The caveat holds; no")
        print(f"  retraction. The past reaches the read through the current, but the read does not carry")
        print(f"  the pair beyond the sum at this width / sample size.")


if __name__ == "__main__":
    main()
