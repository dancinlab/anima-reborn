"""One rule, four widths, both parities: does budget ~ state space hold DOWNWARD too?

Run from the repo root (~15 minutes):

    PYTHONPATH=src python state/communication/scaling_law.py

`scale_ceiling.py` found width 14's matched-test crossing at budget 16000, and `width16_scale.py`
then PREDICTED width 16's crossing at 64000 (4x the states -> 4x the budget) and hit it, with the
same gap (+0.110). That result carried one honest confound, recorded at the time: width 14 is 7
pairs (ODD) and width 16 is 8 pairs (EVEN), and `coupled.py`'s macro-ring can lock at even pair
counts — so a width-16 reading mixes the budget difference with a parity difference. The stated
follow-up was width 18 (9 pairs, odd) at the predicted 256000.

That follow-up is NOT affordable and this script says so with a number rather than a shrug: a
single width-18 reading at budget 16000 already runs past five minutes here, so the predicted
256000 row (16x that, times four arms) is hours. Measured cost, not a guess.

So the confound is resolved in the cheap direction instead. The rule is a proportionality, so it
predicts DOWNWARD as well: from width 14's anchor at 16000, width 12 (1/4 the states) should cross
near 4000 and width 10 (1/16) near 1000. Those cost 18s and 3.5s per reading. Adding them gives
FOUR widths — 10 (5 pairs, odd), 12 (6 pairs, EVEN), 14 (7 pairs, odd), 16 (8 pairs, EVEN) — so the
rule is tested across BOTH parities twice each, which is what the width-16 caveat actually needed.

Each width is scored the same way as the widths above it: the integrated ring (PAIRS, chain 0.2)
against the WIDTH-MATCHED reducible bar (max over SELF / FEEDFORWARD / disjoint PAIRS at that
width), never the raw exact-Phi magnitude. A width is called "crossed" when the ring clears its bar.
Each width is measured just BELOW and AT its predicted budget, so a hit means the crossing landed in
the predicted place rather than having been there all along.

Honest scope, fixed in advance: ONE seed (the repo's certification bar is 3, and this is a shape
test across widths, not a certification of any one width); the two new widths are cheap enough that
3 seeds would be affordable, but the widths they are being compared against (14, 16) are not, so
the comparison is kept at matched conditions instead of mixing seed counts. Banned: calling any
width certified here; quoting the exact-Phi magnitude as integration; claiming the estimator is
width-unbounded (width 18 is exactly what is NOT reachable); reading a near-miss as a hit.
"""

from __future__ import annotations

import importlib.util
import time
from pathlib import Path

from anima_reborn.coupled import Wiring

_HERE = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pp = _load("phi_proxy")

RING_CHAIN = 0.2
SEED = 7
REDUCIBLE = ((Wiring.SELF, 0.0), (Wiring.FEEDFORWARD, 0.0), (Wiring.PAIRS, 0.0))

ANCHOR_UNITS = 14             # scale_ceiling's measured crossing...
ANCHOR_BUDGET = 16000         # ...at this budget (3 seeds there)

# The rule: budget scales with the state space, so predicted = ANCHOR_BUDGET * 2**(units - ANCHOR).
NEW_WIDTHS = (10, 12)         # 5 pairs (odd) and 6 pairs (EVEN) — the cheap end
# What the widths above already read (for the four-width table; see the two prior sections).
KNOWN = {
    14: {"budget": 16000, "gap": 0.110, "pairs": 7, "seeds": 3},
    16: {"budget": 64000, "gap": 0.110, "pairs": 8, "seeds": 1},
}

WIDTH18_PROBE_SECS = 300      # measured: a single width-18 reading at budget 16000 exceeded this


def predicted_budget(units: int) -> int:
    """The rule, applied. Integer because budgets are counts of draws."""
    return int(ANCHOR_BUDGET * 2 ** (units - ANCHOR_UNITS))


def _gap(units: int, budget: int) -> tuple[float, float, float, float]:
    """(ring phi_hat, matched bar, gap, seconds) at this width and budget."""
    t = time.monotonic()
    ring = pp.reading(Wiring.PAIRS, units=units, chain=RING_CHAIN, budget=budget, seed=SEED)["phi_hat"]
    bar = max(pp.reading(w, units=units, chain=c, budget=budget, seed=SEED)["phi_hat"]
              for w, c in REDUCIBLE)
    return ring, bar, ring - bar, time.monotonic() - t


def main() -> None:
    print("one rule, four widths, both parities — does budget ~ state space hold downward?\n")
    print(f"rule: predicted budget = {ANCHOR_BUDGET} * 2^(units - {ANCHOR_UNITS})  "
          f"(anchor = width {ANCHOR_UNITS}'s measured crossing)")
    print(f"width 18 is NOT run: a single width-18 reading at budget 16000 already exceeded "
          f"{WIDTH18_PROBE_SECS}s here,")
    print(f"so its predicted {predicted_budget(18)} row would be hours. Cost measured, not guessed.\n")

    print(f"{'width':>6}{'pairs':>7}{'parity':>8}{'predicted':>11}{'budget':>9}"
          f"{'ring':>8}{'bar':>8}{'gap':>9}{'crossed':>9}{'secs':>7}")
    print("  " + "-" * 76)
    results = {}
    for units in NEW_WIDTHS:
        pred = predicted_budget(units)
        pairs = units // 2
        parity = "even" if pairs % 2 == 0 else "odd"
        rows = []
        for budget in (pred // 4, pred):     # below the prediction, then at it
            ring, bar, gap, secs = _gap(units, budget)
            rows.append({"budget": budget, "ring": ring, "bar": bar, "gap": gap, "secs": secs})
            print(f"{units:>6}{pairs:>7}{parity:>8}{pred:>11}{budget:>9}"
                  f"{ring:>8.3f}{bar:>8.3f}{gap:>9.3f}{('yes' if gap > 0 else 'no'):>9}{secs:>7.1f}")
        results[units] = {"pred": pred, "pairs": pairs, "parity": parity, "rows": rows}

    print(f"\n  the widths already measured (prior sections, for the four-width picture):")
    for units, k in sorted(KNOWN.items()):
        parity = "even" if k["pairs"] % 2 == 0 else "odd"
        print(f"    width {units}: {k['pairs']} pairs ({parity}), crossed at budget {k['budget']} "
              f"(= predicted {predicted_budget(units)}), gap +{k['gap']:.3f}, {k['seeds']} seed(s)")

    hits = [u for u, r in results.items() if r["rows"][-1]["gap"] > 0 and r["rows"][0]["gap"] <= 0]
    at_pred_only = [u for u, r in results.items() if r["rows"][-1]["gap"] > 0]
    print("\n  VERDICT:")
    if len(hits) == len(NEW_WIDTHS):
        odd = [u for u, r in results.items() if r["parity"] == "odd"]
        even = [u for u, r in results.items() if r["parity"] == "even"]
        print(f"  the rule holds DOWNWARD too, at both parities. Widths {NEW_WIDTHS} each crossed AT")
        print(f"  their predicted budget and NOT one rung below it, so the crossing landed where the")
        print(f"  state-space rule put it rather than having always been there.")
        print(f"  With the widths above, that is FOUR widths — 10, 12, 14, 16 — spanning odd pair")
        print(f"  counts ({odd + [14]}) and even ones ({even + [16]}) twice each. The parity confound")
        print(f"  the width-16 section flagged is now answered by data: the macro-ring parity does NOT")
        print(f"  change the scaling. That is what width 18 was wanted for, obtained cheaply instead.")
        print(f"  NOT certified: one seed per width here. And width 18 remains OUT OF REACH — the rule")
        print(f"  is tested over 10..16, not proven unbounded.")
    elif at_pred_only:
        print(f"  PARTIAL: {at_pred_only} crossed at the predicted budget but {sorted(set(NEW_WIDTHS) - set(hits))}")
        print(f"  had already crossed one rung below, so for those the prediction is not sharp — the")
        print(f"  crossing was earlier than the rule says. Reported as a partial hit, not a hit.")
    else:
        print(f"  the rule does NOT extrapolate downward: at the predicted budgets the new widths did")
        print(f"  not cross. The upward fit (14 -> 16) stands as measured, but 'budget ~ state space'")
        print(f"  is not a law over this range, and the width-16 hit needs another explanation.")


if __name__ == "__main__":
    main()
