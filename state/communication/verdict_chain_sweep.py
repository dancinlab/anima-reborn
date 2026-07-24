"""The best joint operating point: sweep the chain at the verdict width, context alive vs integration.

Run from the repo root:

    PYTHONPATH=src python state/communication/verdict_chain_sweep.py

integrated_context.py showed, at the only width where integration is a verdict (5 pairs = 10 units,
odd), that the multiplicative-modulation CONTEXT survives coupling — but it only compared chain 0
(disintegrated) against chain 0.05 (integrated). This sweeps the chain across 0.02..0.15 at that
width to find the JOINT operating point: the chain that maximises the integration margin (over the
width-matched reducible ceiling — wide_integration.py's valid verdict, NOT the raw phi magnitude)
WHILE the context gate is still alive (a base-current window exists: the held past reaches the read
above floor with the current symbol's sign intact).

Two axes, one chain knob, both measured at the same 10-unit population:
- integration: wide_integration.arm_summary(PAIRS, chain).phi_hat, scored against
  wide_integration.matched_ceiling (max proxy over the reducible nulls SELF/FEEDFORWARD/disjoint-PAIRS
  at this width, plus their seed spread). matched_integrated(...) is the verdict; the margin over the
  bar is how far above reducible the ring sits.
- context: integrated_context._battery(5, chain) — does a cur_base window exist (read I(a_past;read|
  sign) above its shuffled-within-sign floor with fidelity >= 0.95), and how big is that read margin.

report-the-rank: at 10 units the count spans only 0..5, so the context read carries ~1 level (2^I);
this finds the best TRADE point at a narrow width, NOT a strong coexistence — the width collision
integrated_rate.py named still binds. The honest deliverable is the shape of the two curves against
the chain and where they are jointly best, with the null on each.

Banned (fixed in advance): calling the raw phi magnitude integration (wide_integration showed a
6-unit SELF null reads ~5); claiming coexistence at a width wider than the verdict holds (10 units
only); "language"; more context width than the ~1 level measured; a "best chain" that is integrated
but has NO context window (that is not a joint point, it is a takeover).
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

from anima_reborn.coupled import Wiring

_HERE = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ic = _load("integrated_context")     # the context battery (_battery, _integrated)
wi = _load("wide_integration")       # the integration margin (arm_summary, matched_ceiling, matched_integrated)

PAIRS_N = 5
UNITS = 2 * PAIRS_N                   # 10 — odd pairs, the width where the verdict is takeable
CHAINS = (0.02, 0.05, 0.08, 0.11, 0.15)
BUDGET = wi.BUDGET


def main() -> None:
    print("best joint operating point — sweep the chain at the verdict width (10 units)\n")
    print(f"integration = matched-ceiling verdict (NOT the raw phi magnitude); context = the")
    print(f"multiplicative-modulation gate's window at {PAIRS_N} pairs; both at the SAME population\n")

    bar, spread = wi.matched_ceiling(units=UNITS, budget=BUDGET)
    print(f"width-matched reducible ceiling at {UNITS} units: bar {bar:.3f}  spread {spread:.3f}"
          f"  (integrated if phi_hat > bar + 3*spread)\n")

    print(f"{'chain':>7}{'phi_hat':>9}{'int.margin':>11}{'integrated':>11}"
          f"{'ctx window':>11}{'read I':>8}{'floor':>8}{'fidelity':>9}")
    print("  " + "-" * 74)
    rows = []
    for chain in CHAINS:
        arm = wi.arm_summary(Wiring.PAIRS, chain, units=UNITS, budget=BUDGET)
        integrated = wi.matched_integrated(arm["phi_hat"], units=UNITS, budget=BUDGET)
        int_margin = arm["phi_hat"] - bar
        b = ic._battery(PAIRS_N, chain, tag="sweep")
        ctx_alive = bool(b["window"])
        read_margin = b["obs"] - b["floor"]
        rows.append({
            "chain": chain, "phi_hat": arm["phi_hat"], "int_margin": int_margin,
            "integrated": integrated, "ctx_alive": ctx_alive, "read": b["obs"],
            "floor": b["floor"], "fid": b["fid"], "read_margin": read_margin,
            "acur": b["acur"], "shuffled": b["shuffled"],
        })
        print(f"{chain:>7.2f}{arm['phi_hat']:>9.3f}{int_margin:>11.3f}"
              f"{('yes' if integrated else 'no'):>11}{('yes' if ctx_alive else 'no'):>11}"
              f"{b['obs']:>8.3f}{b['floor']:>8.3f}{b['fid']:>9.3f}")

    # the joint point: integrated AND context-alive, maximising the integration margin.
    joint = [r for r in rows if r["integrated"] and r["ctx_alive"]]
    print("\n  VERDICT:")
    if joint:
        best = max(joint, key=lambda r: r["int_margin"])
        # is the read still real at that chain — above floor, shuffled kills it, a_cur=0 collapses?
        acur0 = best["acur"].get(0.0, (None, None)) if isinstance(best["acur"], dict) else (None, None)
        print(f"  BEST JOINT POINT at chain {best['chain']:.2f}: integrated (matched verdict) with the")
        print(f"  LARGEST integration margin over the reducible bar ({best['int_margin']:.3f}) among the")
        print(f"  chains whose context gate is still alive (read I {best['read']:.3f} > floor "
              f"{best['floor']:.3f}, fidelity {best['fid']:.3f}).")
        hi = max(rows, key=lambda r: r["int_margin"])
        if not hi["ctx_alive"]:
            print(f"  A HIGHER integration margin exists at chain {hi['chain']:.2f} ({hi['int_margin']:.3f})")
            print(f"  but its context gate has NO window (a takeover, not a joint point) — excluded.")
        else:
            print(f"  Integration margin still rises with chain across the swept range; the joint point is")
            print(f"  the strongest chain measured that keeps the window.")
        print(f"  report-the-rank: the read carries ~{2 ** best['read']:.1f} level(s) at {UNITS} units"
              f" (count 0..{PAIRS_N}) — the narrow-width collision still binds; this is the best TRADE")
        print(f"  point, not a strong coexistence. NOT language, NOT a phi magnitude, {UNITS} units only.")
    else:
        any_int = [r for r in rows if r["integrated"]]
        any_ctx = [r for r in rows if r["ctx_alive"]]
        print(f"  NO joint point in the swept range: integrated chains {[r['chain'] for r in any_int]},")
        print(f"  context-alive chains {[r['chain'] for r in any_ctx]} — they do not overlap here. The")
        print(f"  chain that integrates has already closed the context window (a takeover), or none")
        print(f"  integrates on the matched test at this budget. Reported with numbers, not smoothed over.")


if __name__ == "__main__":
    main()
