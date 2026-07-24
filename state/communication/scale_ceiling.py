"""Is the width-14 collapse a SAMPLING limit or a real wall? Scale the budget and watch the gap.

Run from the repo root (SLOW — tens of minutes; the 16000-budget readings dominate):

    PYTHONPATH=src python state/communication/scale_ceiling.py

`wide_integration.py` measured two ceilings for the integration verdict and left ONE question
explicitly unverified: the width-matched test certifies the integrated ring through width 12 and
COLLAPSES at 14 — and that collapse "may be support/cut undersampling", flagged as not checked.
This checks it, the only way it can be checked: raise the state budget at width 14 and watch whether
the two quantities that decide the verdict move toward each other or stay apart.

Why the budget is the right knob (and the cut count is not): `phi_proxy.phi_hat` is a MINIMUM over
sampled cuts, so sampling MORE cuts can only LOWER it — for the ring and the nulls alike, which does
not obviously help separation. The budget is different: it is the number of independent
(state -> next) draws, and `wide_integration.py` already measured that a reducible arm's phi_hat —
which SHOULD be zero — shrinks toward zero as trials rise (SELF 0.71 -> 0.09 from 100 -> 6400 at 4
units) while a genuinely integrated arm stays flat. So more budget should push the artefact DOWN
without taking the ring's real integration with it.

Measured at width 14 (7 pairs, ODD so the chain can integrate), budgets 4000 / 8000 / 16000:
- the integrated ring (PAIRS, chain 0.2): mean phi_hat over seeds.
- the width-matched REDUCIBLE bar (max mean phi_hat over SELF / FEEDFORWARD / disjoint PAIRS at the
  same width) — `wide_integration.matched_ceiling`'s definition, recomputed at each budget.
- the GAP = ring phi_hat - bar, and the matched verdict (ring clears bar + 3 spreads).
- the ABSOLUTE floor too, since it is what the older test used.

The honest question is the SIGN OF THE TREND, not one row: if the gap closes monotonically with the
budget, the width-14 collapse is a sampling limit and the ceiling is a budget question; if the gap
stalls or widens, 14 is a real wall for this estimator and no budget in reach fixes it.

Conditions (stated because they are weaker than wide_integration's): SEEDS is 2 here, not 3 — a
16000-budget reading at 14 units costs ~2 minutes and the full grid is already ~30 minutes. The
seed spread is therefore an estimate from two points; treat the bar's spread as indicative and the
GAP TREND as the claim.

A caveat found while writing the test, kept rather than smoothed over (`artefact-honesty`): the
absolute floor is NOT monotone in the budget. At width 14 it reads 0.268 at budget 1000 and 0.883 at
4000 — it RISES first, then falls (0.883 -> 0.784 -> 0.629 across this grid). At 1000 draws over
2^14 states the floor estimate is itself starved and comes out artificially LOW, which would read as
"easier to separate" if anyone scored there. So "more budget lowers the floor" holds only ABOVE that
starved regime, and the grid here starts at 4000 for that reason. Never score a width at a budget
where the floor has not yet turned over.

Banned in advance: calling width 14 "certified" off a trend that has not actually crossed; quoting
the raw exact-Phi magnitude (wide_integration showed a 6-unit SELF null reads ~5); claiming any
budget makes the estimator width-unbounded; "language".
"""

from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

from anima_reborn.coupled import Wiring

_HERE = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pp = _load("phi_proxy")

UNITS = 14                    # 7 pairs — ODD, the width where wide_integration's matched test fell
RING_CHAIN = 0.2              # the integrated arm
BUDGETS = (4000, 8000, 16000)
SEEDS = (7, 11)               # 2, not 3 — cost; stated as a condition, not hidden
REDUCIBLE = (                 # the width-matched nulls that define the bar (each CANNOT integrate)
    (Wiring.SELF, 0.0),
    (Wiring.FEEDFORWARD, 0.0),
    (Wiring.PAIRS, 0.0),      # disjoint pairs
)
K_SPREADS = 3                 # wide_integration's matched-test margin


CONFIRM_SEEDS = (7, 11, 13)   # the crossing row re-run at wide_integration's own 3 seeds
CROSSING_BUDGET = 16000


def _arm(wiring: Wiring, chain: float, *, budget: int,
         seeds: tuple[int, ...] = ()) -> tuple[float, float, float]:
    """(mean phi_hat, mean absolute floor, seed spread) for one arm at this budget."""
    use = seeds or SEEDS
    rs = [pp.reading(wiring, units=UNITS, chain=chain, budget=budget, seed=s) for s in use]
    phis = [r["phi_hat"] for r in rs]
    floors = [r["floor"] for r in rs]
    spread = statistics.pstdev(phis) if len(phis) > 1 else 0.0
    return statistics.fmean(phis), statistics.fmean(floors), spread


def confirm_trend() -> list[dict]:
    """Re-run the TREND rows (the pre-crossing budgets) at the same 3 seeds.

    `confirm()` closed the crossing row's seed gap; these are the rows the gap-closes-monotonically
    statement rests on, and they were still 2-seed. Running them at 3 makes EVERY row in this
    section match `wide_integration.py`'s seed count, so the section's conditions no longer differ
    from the work it corrects. The verdict does not depend on these rows crossing (they do not —
    their gaps are negative by construction); what is checked is that the MONOTONE CLOSING survives
    the third seed."""
    rows = []
    for budget in [b for b in BUDGETS if b != CROSSING_BUDGET]:
        ring, ring_floor, _ = _arm(Wiring.PAIRS, RING_CHAIN, budget=budget, seeds=CONFIRM_SEEDS)
        bar = 0.0
        spread = 0.0
        for wiring, chain in REDUCIBLE:
            phi, _f, sp = _arm(wiring, chain, budget=budget, seeds=CONFIRM_SEEDS)
            bar = max(bar, phi)
            spread = max(spread, sp)
        rows.append({"budget": budget, "ring": ring, "floor": ring_floor, "bar": bar,
                     "spread": spread, "gap": ring - bar,
                     "matched": ring > bar + K_SPREADS * spread, "seeds": CONFIRM_SEEDS})
    return rows


def confirm() -> dict:
    """Re-run ONLY the crossing row at 3 seeds — closing this script's own stated weakness.

    The grid above used 2 seeds for cost, which is weaker than the 3 `wide_integration.py` used, and
    the whole claim rests on ONE row crossing. This re-measures that row at the same 3 seeds so the
    crossing is not an artefact of which two seeds were drawn. Only the crossing budget is re-run;
    the trend rows stay 2-seed and are still reported as such."""
    ring, ring_floor, ring_spread = _arm(Wiring.PAIRS, RING_CHAIN,
                                         budget=CROSSING_BUDGET, seeds=CONFIRM_SEEDS)
    bar = 0.0
    spread = 0.0
    for wiring, chain in REDUCIBLE:
        phi, _f, sp = _arm(wiring, chain, budget=CROSSING_BUDGET, seeds=CONFIRM_SEEDS)
        bar = max(bar, phi)
        spread = max(spread, sp)
    gap = ring - bar
    return {"ring": ring, "ring_spread": ring_spread, "bar": bar, "spread": spread,
            "gap": gap, "matched": ring > bar + K_SPREADS * spread,
            "seeds": CONFIRM_SEEDS, "budget": CROSSING_BUDGET}


def main() -> None:
    print(f"does more budget close the width-{UNITS} gap? (the unverified question wide_integration left)\n")
    print(f"width {UNITS} = {UNITS // 2} pairs (odd); ring = PAIRS chain {RING_CHAIN}; seeds {SEEDS}")
    print("bar = max mean phi_hat over the width-matched reducible nulls (SELF / FEEDFORWARD / disjoint PAIRS)\n")

    print(f"{'budget':>8}{'ring phi':>10}{'abs floor':>11}{'bar':>8}{'spread':>8}"
          f"{'GAP(ring-bar)':>15}{'matched':>9}")
    print("  " + "-" * 69)
    rows = []
    for budget in BUDGETS:
        ring_phi, ring_floor, _ = _arm(Wiring.PAIRS, RING_CHAIN, budget=budget)
        bar = 0.0
        spread = 0.0
        for wiring, chain in REDUCIBLE:
            phi, _floor, sp = _arm(wiring, chain, budget=budget)
            if phi > bar:
                bar = phi
            spread = max(spread, sp)
        gap = ring_phi - bar
        matched = ring_phi > bar + K_SPREADS * spread
        rows.append({"budget": budget, "ring": ring_phi, "floor": ring_floor,
                     "bar": bar, "spread": spread, "gap": gap, "matched": matched})
        print(f"{budget:>8}{ring_phi:>10.3f}{ring_floor:>11.3f}{bar:>8.3f}{spread:>8.3f}"
              f"{gap:>15.3f}{('yes' if matched else 'no'):>9}")

    gaps = [r["gap"] for r in rows]
    closing = all(gaps[i + 1] > gaps[i] for i in range(len(gaps) - 1))
    crossed = any(r["matched"] for r in rows)
    print("\n  VERDICT:")
    if crossed:
        first = next(r for r in rows if r["matched"])
        print(f"  the width-{UNITS} collapse was a SAMPLING limit: at budget {first['budget']} the ring clears the")
        print(f"  width-matched reducible bar (ring {first['ring']:.3f} > bar {first['bar']:.3f} + "
              f"{K_SPREADS}*{first['spread']:.3f}).")
        print(f"  wide_integration's matched ceiling of 12 is a BUDGET statement, not a width wall — at this")
        print(f"  budget it reaches {UNITS}. It is still not unbounded: the cost grows with both width and")
        print(f"  budget, and nothing here certifies 16 units.")
    elif closing:
        print(f"  NOT crossed, but the gap CLOSES MONOTONICALLY with the budget "
              f"({' -> '.join(f'{g:+.3f}' for g in gaps)}).")
        print(f"  So the width-{UNITS} collapse behaves like a sampling limit rather than a wall — the ring's")
        print(f"  phi_hat rises while the reducible bar falls, which is exactly the artefact-shrinks-with-")
        print(f"  samples signature wide_integration measured at 4 units. What is NOT shown: an actual")
        print(f"  crossing. The honest statement is a TREND, and width {UNITS} stays uncertified here.")
    else:
        print(f"  the gap does NOT close with the budget ({' -> '.join(f'{g:+.3f}' for g in gaps)}) — width")
        print(f"  {UNITS} looks like a real wall for this estimator, not undersampling. wide_integration's")
        print(f"  matched ceiling of 12 stands as a width statement, and more budget is not the fix.")
    print(f"  Conditions: {len(SEEDS)} seeds (wide_integration used 3), budgets {BUDGETS}, width {UNITS} only.")

    # The claim rests on ONE row crossing, measured at 2 seeds. Re-run that row at 3.
    print(f"\n[confirm] the crossing row at {len(CONFIRM_SEEDS)} seeds {CONFIRM_SEEDS} "
          f"(budget {CROSSING_BUDGET})")
    c = confirm()
    print(f"    ring {c['ring']:.3f} (spread {c['ring_spread']:.3f})   bar {c['bar']:.3f} "
          f"(spread {c['spread']:.3f})   GAP {c['gap']:+.3f}   matched: "
          f"{'yes' if c['matched'] else 'NO'}")
    if c["matched"]:
        print(f"    the crossing HOLDS at 3 seeds — it is not an artefact of which two were drawn,")
        print(f"    and the row now matches wide_integration's own seed count.")
        print(f"\n[confirm-trend] the pre-crossing rows at the same {len(CONFIRM_SEEDS)} seeds")
        trend = confirm_trend()
        for t in trend:
            print(f"    budget {t['budget']:>6}: ring {t['ring']:.3f}  bar {t['bar']:.3f}  "
                  f"GAP {t['gap']:+.3f}  matched: {'yes' if t['matched'] else 'no'}")
        gaps = [t["gap"] for t in trend] + [c["gap"]]
        closes = all(gaps[i + 1] > gaps[i] for i in range(len(gaps) - 1))
        print(f"    3-seed gaps: {' -> '.join(f'{g:+.3f}' for g in gaps)} — "
              f"{'monotone closing, and it crosses' if closes else 'NOT monotone; re-read the rows'}")
        print(f"    every row in this section is now {len(CONFIRM_SEEDS)}-seed: the conditions match")
        print(f"    wide_integration exactly. 3 is the MATCHED seed count, not a confidence interval.")
    else:
        print(f"    the crossing does NOT hold at 3 seeds — the 2-seed result was seed-lucky, and the")
        print(f"    width-{UNITS} claim must be withdrawn to a TREND. Report this, do not re-pick seeds.")


if __name__ == "__main__":
    main()
