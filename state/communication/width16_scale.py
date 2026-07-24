"""Does the budget-scaling rule PREDICT width 16? A pre-registered test of its own generalisation.

Run from the repo root (SLOW — ~1 hour; the 64000-budget readings dominate):

    PYTHONPATH=src python state/communication/width16_scale.py

`scale_ceiling.py` showed the width-14 collapse was undersampling: raising the budget lifted the
integrated ring and lowered the width-matched reducible bar until they crossed at budget 16000. That
turned "the matched ceiling is 12" into "the ceiling is a budget statement". This asks the obvious
next question — does the rule PREDICT the next width, or was 14 a one-off fit?

THE PREDICTION, FIXED BEFORE THE RUN. A cost probe measured width 16 at budget 16000 and got ring
phi_hat 0.329 with floor 0.885 — which is almost exactly what width 14 read at budget 4000 (0.315,
floor 0.882). Width 16 has 4x the state space of width 14 (2^16 vs 2^14), and 4000 * 4 = 16000. So
if the required budget scales with the STATE SPACE, width 16 should reach at budget 16000 * 4 =
**64000** the place width 14 reached at 16000 — i.e. the ring should clear the width-matched
reducible bar there. That is the prediction this script tests. It was written down before the
64000 grid ran, so it can fail.

HONEST SCOPE, ALSO FIXED IN ADVANCE. This runs ONE seed, not the three `wide_integration.py` and
`scale_ceiling.py` use, because a 64000-budget reading at 16 units costs ~11 minutes and the 3-seed
grid would be hours. A single seed CANNOT certify a width — this is a TREND test of a prediction,
and the verdict is phrased that way whichever direction it goes. If the prediction holds, the honest
sentence is "the scaling rule predicted width 16's crossing budget at one seed; certifying it needs
the 3-seed grid"; nothing here promotes width 16 to certified.

Banned in advance: calling width 16 certified off one seed; quoting the raw exact-Phi magnitude as
integration (a 6-unit SELF null reads ~5); claiming the estimator is width-unbounded (cost grows in
both width and budget — 18 units is untouched); reading a near-miss as a hit.
"""

from __future__ import annotations

import importlib.util
import statistics
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

UNITS = 16                    # 8 pairs — EVEN pair count; see the parity note in the verdict
RING_CHAIN = 0.2
BUDGETS = (16000, 64000)      # the width-14 crossing budget, and the state-space-scaled prediction
SEED = 7                      # ONE seed — a trend test, not a certification (stated above)
REDUCIBLE = (
    (Wiring.SELF, 0.0),
    (Wiring.FEEDFORWARD, 0.0),
    (Wiring.PAIRS, 0.0),
)
K_SPREADS = 3
PREDICTED_CROSSING = 64000

# What width 14 read at its own crossing, for the side-by-side (from scale_ceiling.py, 3 seeds).
W14_CROSSING = {"budget": 16000, "ring": 0.633, "bar": 0.523, "gap": 0.110}


def _row(budget: int) -> dict:
    t = time.monotonic()
    ring = pp.reading(Wiring.PAIRS, units=UNITS, chain=RING_CHAIN, budget=budget, seed=SEED)
    bar = 0.0
    for wiring, chain in REDUCIBLE:
        phi = pp.reading(wiring, units=UNITS, chain=chain, budget=budget, seed=SEED)["phi_hat"]
        bar = max(bar, phi)
    gap = ring["phi_hat"] - bar
    return {"budget": budget, "ring": ring["phi_hat"], "floor": ring["floor"], "bar": bar,
            "gap": gap, "crossed": gap > 0.0, "secs": time.monotonic() - t}


def main() -> None:
    print(f"does the budget-scaling rule predict width {UNITS}? (pre-registered)\n")
    print(f"prediction, written before the run: width 14 crossed at budget "
          f"{W14_CROSSING['budget']}; width {UNITS} has 4x the state space, so it should cross near "
          f"{PREDICTED_CROSSING}.")
    print(f"ONE seed ({SEED}) — a trend test; certifying a width needs the 3-seed grid.\n")

    print(f"{'budget':>8}{'ring phi':>10}{'abs floor':>11}{'bar':>8}{'GAP':>9}{'crossed':>9}{'secs':>7}")
    print("  " + "-" * 54)
    rows = []
    for budget in BUDGETS:
        r = _row(budget)
        rows.append(r)
        print(f"{r['budget']:>8}{r['ring']:>10.3f}{r['floor']:>11.3f}{r['bar']:>8.3f}"
              f"{r['gap']:>9.3f}{('yes' if r['crossed'] else 'no'):>9}{r['secs']:>7.0f}")

    at_pred = next(r for r in rows if r["budget"] == PREDICTED_CROSSING)
    baseline = next(r for r in rows if r["budget"] == 16000)
    print(f"\n  width 14 at ITS crossing (3 seeds, scale_ceiling.py): ring {W14_CROSSING['ring']:.3f}  "
          f"bar {W14_CROSSING['bar']:.3f}  gap +{W14_CROSSING['gap']:.3f}")
    print(f"  width {UNITS} at the predicted budget {PREDICTED_CROSSING}: ring {at_pred['ring']:.3f}  "
          f"bar {at_pred['bar']:.3f}  gap {at_pred['gap']:+.3f}")

    print("\n  VERDICT:")
    if at_pred["crossed"]:
        print(f"  the PREDICTION HELD at one seed. The state-space scaling (4x states -> 4x budget)")
        print(f"  put width {UNITS}'s crossing where it was predicted: gap {baseline['gap']:+.3f} at 16000")
        print(f"  -> {at_pred['gap']:+.3f} at {PREDICTED_CROSSING}. The budget-scaling rule is not a")
        print(f"  one-off fit to width 14; it generalised to a width it was not measured on.")
        print(f"  NOT certified: one seed. Certifying width {UNITS} needs the 3-seed grid, which is")
        print(f"  hours at this budget. Read this as a TREND that matched a pre-registered number.")
    else:
        print(f"  the PREDICTION MISSED at one seed: at the predicted budget {PREDICTED_CROSSING} the gap is")
        print(f"  {at_pred['gap']:+.3f}, still short. Either the required budget grows FASTER than the")
        print(f"  state space, or width {UNITS} has something width 14 did not. Reported as a miss —")
        print(f"  the rule is not withdrawn (it was measured at 14), but it does NOT extrapolate by")
        print(f"  state-space ratio alone, and that is the honest finding here.")
    print(f"  Parity note: {UNITS} units is {UNITS // 2} pairs, an EVEN pair count, where coupled.py's")
    print(f"  macro-ring can lock — width 14 was 7 pairs (odd). Any width-16 reading carries that")
    print(f"  difference as well as the budget one; a same-parity check (18 units = 9 pairs) is the")
    print(f"  clean follow-up and is NOT done here.")


if __name__ == "__main__":
    main()
