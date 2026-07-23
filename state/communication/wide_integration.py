"""How far can the integration verdict be trusted? — the floor's growth and the false-positive width.

Run from the repo root:

    PYTHONPATH=src python state/communication/wide_integration.py

`integrated_rate.py` had to write "16 units is past where the proxy floor is trustworthy — depth
trend only", and `phi_proxy.py`/`coupled.py` say the exact directed-Phi MAGNITUDE is already useless
at 6 units. Neither pinned WHERE the verdict stops being trustworthy. This does, by measurement.

The method under test is `phi_proxy.reading(...).separated` — the ABSOLUTE-floor separation test:
an arm reads "integrated" iff its sampled directed-cut proxy `phi_hat` exceeds its own time-shuffle
floor. The task is to bound its trust region with the load-bearing controls: the KNOWN-REDUCIBLE
wirings, which CANNOT integrate and so MUST read "not integrated" at every width the verdict is
trusted at — `Wiring.SELF`, `Wiring.FEEDFORWARD`, and `Wiring.PAIRS` at `chain=0` (disjoint pairs).
The width at which one of them first reads "integrated" (a false positive) is the honest ceiling.

What this establishes, all measured here:

1. FLOOR GROWTH. The shuffle floor of `Wiring.PAIRS` grows fast with width — a few thousandths at
   6 units, a few tenths at 10, and it swallows even the integrated arm past ~12. So the ABSOLUTE
   magnitude of the proxy is width-bound exactly as the exact Phi is; only the separation is a verdict.

2. THE EXACT-MAGNITUDE ARTEFACT, shown not told. At 6 units `Wiring.SELF` — each unit reads only
   itself, the purest reducible null — reads exact directed Phi ~5.7, LARGER than the disjoint pairs
   (~5.0) and comparable to a real chained ring, while at 4 units the same null reads ~0.26. The
   magnitude tracks WIDTH, not integration. And the 4-unit reducible magnitude is a SAMPLING artefact
   that shrinks toward zero as trials rise (SELF 0.71 -> 0.09 from 100 -> 6400 trials) while the
   integrated arm's stays put (~0.44) — `default-stays-exact`/`artefact-honesty`: never quote the
   magnitude as integration. Only `Wiring.FEEDFORWARD` is structurally zeroed (acyclic cut), at every
   width, by exact IIT and by the proxy.

3. THE FALSE-POSITIVE WIDTH (the honest ceiling of the ABSOLUTE test). Measured below.

4. A CHEAP, VALIDATED IMPROVEMENT — the WIDTH-MATCHED reducible ceiling. Instead of each arm's own
   time-shuffle floor, use the largest proxy over the width-matched REDUCIBLE wirings {SELF, FF,
   disjoint PAIRS} as the bar (plus their measured seed spread). That bar IS the width artefact,
   measured directly at that width by systems that provably cannot integrate. A reducible arm sits
   inside the set that defines the bar, so it cannot clear it (no false positive by construction); the
   integrated arm must rise above the artefact cloud. It is validated the same way — every reducible
   null stays negative AND the integrated arm stays positive, up to the width where IT too breaks
   (the integrated arm sinks into the reducible cloud), which is reported, not hidden.

Not language, not "unbounded", never an exact-Phi magnitude as a verdict. The deliverable is the
numbers and the two ceilings (absolute test, matched test), each with the width where it fails.

Measured verdict (budget 4000, seeds 7/11/13; full table in RESULTS): the ABSOLUTE test is clean
only to 4 units — a reducible null false-positives from 6 (sporadic) and solidly at 8 — while the
MATCHED test keeps every reducible null negative at every width and certifies the integrated ring
through ~12 before the ring itself sinks into the width-artefact cloud (14+). Neither reaches 16.

Runtime: a full `main()` is minutes — the widths 14/16 proxy readings are tens of seconds each even
memoized. The exact cross-check touches only units <= 6.
"""

from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

from anima_reborn.coupled import FIXED, Wiring
from anima_reborn.iit4 import directed_big_phi
from anima_reborn.substrate import coupled_matrix

_PP = Path(__file__).resolve().parent / "phi_proxy.py"
_spec = importlib.util.spec_from_file_location("phi_proxy", _PP)
pp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pp)

# ── the grid ──────────────────────────────────────────────────────────────────────────
WIDTHS = (4, 6, 8, 10, 12, 14, 16)
SEEDS = (7, 11, 13)
BUDGET = 4000
INT_CHAIN = 0.2   # the chained-PAIRS arm that DOES integrate (validated to 6 by exact IIT)

# The three width-matched REDUCIBLE nulls — each CANNOT integrate, so each MUST read "not
# integrated" wherever the verdict is trusted. FEEDFORWARD is also the exact structural zero.
REDUCIBLE = (
    ("SELF", Wiring.SELF, 0.0),
    ("FEEDFORWARD", Wiring.FEEDFORWARD, 0.0),
    ("PAIRS chain=0", Wiring.PAIRS, 0.0),
)
INTEGRATED = ("PAIRS chain=0.2", Wiring.PAIRS, INT_CHAIN)


_CACHE: dict[tuple, dict] = {}


def _reading(wiring: Wiring, chain: float, units: int, budget: int, seed: int) -> dict:
    """Memoized `phi_proxy.reading` — the reports re-request the same reducible arms many times
    (as nulls, as the matched ceiling, as false-positive candidates); the reading is deterministic
    in the seed, so cache it. A wide reading at budget 4000 costs tens of seconds; without this the
    full sweep would recompute each one several-fold."""
    key = (wiring, chain, units, budget, seed)
    if key not in _CACHE:
        _CACHE[key] = pp.reading(wiring, units=units, chain=chain, budget=budget, seed=seed)
    return _CACHE[key]


def arm_readings(wiring: Wiring, chain: float, *, units: int, budget: int, seeds=SEEDS) -> list[dict]:
    """`phi_proxy.reading` for one arm across seeds (deterministic given the seed)."""
    return [_reading(wiring, chain, units, budget, s) for s in seeds]


def arm_summary(wiring: Wiring, chain: float, *, units: int, budget: int, seeds=SEEDS) -> dict:
    """Mean phi_hat, mean floor, mean margin, and how many seeds the ABSOLUTE test called separated."""
    rs = arm_readings(wiring, chain, units=units, budget=budget, seeds=seeds)
    phis = [r["phi_hat"] for r in rs]
    floors = [r["floor"] for r in rs]
    margins = [r["phi_hat"] - r["floor"] for r in rs]
    return {
        "phi_hat": statistics.fmean(phis),
        "phi_sd": statistics.pstdev(phis),
        "floor": statistics.fmean(floors),
        "margin": statistics.fmean(margins),
        "n_separated": sum(1 for r in rs if r["separated"]),
        "n": len(rs),
    }


# ── the width-matched reducible ceiling (the improvement) ───────────────────────────────

def matched_ceiling(*, units: int, budget: int, seeds=SEEDS) -> tuple[float, float]:
    """The width-matched reducible bar: (max mean phi_hat over {SELF, FF, disjoint PAIRS}, spread).

    The bar is the width artefact measured directly by systems that provably cannot integrate at this
    exact width. `spread` is the max seed-to-seed sd across those reducible arms — a MEASURED margin,
    not a picked threshold (`claims-need-controls`)."""
    means, sds = [], []
    for _, wiring, chain in REDUCIBLE:
        s = arm_summary(wiring, chain, units=units, budget=budget, seeds=seeds)
        means.append(s["phi_hat"])
        sds.append(s["phi_sd"])
    return max(means), max(sds)


def matched_integrated(phi_hat_mean: float, *, units: int, budget: int, seeds=SEEDS,
                       k: float = 3.0) -> bool:
    """Matched-test verdict: mean phi_hat clears the width-matched reducible ceiling by k spreads."""
    bar, spread = matched_ceiling(units=units, budget=budget, seeds=seeds)
    return phi_hat_mean > bar + k * spread


# ── exact cross-check (units <= substrate.MAX_UNITS = 6) ────────────────────────────────

def exact_phi(wiring: Wiring, *, units: int, chain: float, seed: int = 1, trials: int | None = None) -> float:
    """Exact directed Phi via substrate.coupled_matrix + iit4.directed_big_phi (legal to 6 units)."""
    kw = {} if trials is None else {"trials": trials}
    matrix = coupled_matrix(wiring, units=units, chain=chain, rhythm=FIXED, seed=seed, **kw)
    state = int("01" * (units // 2), 2)
    return directed_big_phi(matrix, state).phi


# ── reports ─────────────────────────────────────────────────────────────────────────────

def report_floor_growth(budget: int = BUDGET) -> None:
    print(f"[1] Floor growth with width — PAIRS, budget {budget}, seeds {SEEDS}\n")
    print(f"{'W':>4}  {'chain0 phi':>11}{'chain0 flr':>11}{'sep?':>6}   "
          f"{'chainC phi':>11}{'chainC flr':>11}{'margin':>9}{'sep?':>6}")
    print("-" * 78)
    for w in WIDTHS:
        r0 = arm_summary(Wiring.PAIRS, 0.0, units=w, budget=budget)
        rc = arm_summary(Wiring.PAIRS, INT_CHAIN, units=w, budget=budget)
        print(f"{w:>4}  {r0['phi_hat']:>11.3f}{r0['floor']:>11.3f}{r0['n_separated']:>4}/3   "
              f"{rc['phi_hat']:>11.3f}{rc['floor']:>11.3f}{rc['margin']:>9.3f}{rc['n_separated']:>4}/3")


def report_reducible_nulls(budget: int = BUDGET) -> int | None:
    print(f"\n[2] Known-reducible nulls under the ABSOLUTE test — first false positive is the ceiling\n")
    print(f"{'W':>4}  " + "".join(f"{name:>16}" for name, _, _ in REDUCIBLE) + f"{'ceiling':>9}")
    print("-" * 70)
    first_fp = None
    for w in WIDTHS:
        cells = []
        fp_here = False
        for name, wiring, chain in REDUCIBLE:
            s = arm_summary(wiring, chain, units=w, budget=budget)
            sep = s["n_separated"]
            if sep > 0:
                fp_here = True
            cells.append(f"{s['phi_hat']:.3f}({sep}/3)")
        if fp_here and first_fp is None:
            first_fp = w
        mark = " <- false positive" if fp_here else ""
        print(f"{w:>4}  " + "".join(f"{c:>16}" for c in cells) + f"{mark}")
    print(f"\n  Absolute-test ceiling (last width with NO reducible false positive): "
          f"{'>' + str(WIDTHS[-1]) if first_fp is None else first_fp - 2}")
    print(f"  First reducible false positive at width: {first_fp}")
    return first_fp


def report_matched(budget: int = BUDGET) -> int | None:
    print(f"\n[3] The MATCHED test — width-matched reducible ceiling (k=3 spreads)\n")
    print(f"{'W':>4}  {'bar':>8}{'spread':>8}   "
          + "".join(f"{name.split()[0][:4]:>7}" for name, _, _ in REDUCIBLE)
          + f"{'chainC':>8}   verdicts (R=reducible, I=integrated)")
    print("-" * 88)
    int_ceiling = None
    for w in WIDTHS:
        bar, spread = matched_ceiling(units=w, budget=budget)
        red_cells, red_ok = [], True
        for _, wiring, chain in REDUCIBLE:
            m = arm_summary(wiring, chain, units=w, budget=budget)["phi_hat"]
            red_cells.append(m)
            if matched_integrated(m, units=w, budget=budget):
                red_ok = False
        ci = arm_summary(Wiring.PAIRS, INT_CHAIN, units=w, budget=budget)["phi_hat"]
        int_ok = matched_integrated(ci, units=w, budget=budget)
        if int_ok:
            int_ceiling = w
        verdict = ("R:all-negative" if red_ok else "R:FALSE-POSITIVE") + \
                  ("  I:positive" if int_ok else "  I:sunk-into-cloud")
        print(f"{w:>4}  {bar:>8.3f}{spread:>8.3f}   "
              + "".join(f"{c:>7.3f}" for c in red_cells) + f"{ci:>8.3f}   {verdict}")
    print(f"\n  Matched-test trust ceiling (integrated still clears the reducible cloud AND no")
    print(f"  reducible false positive): {int_ceiling}")
    return int_ceiling


def report_exact_artefact() -> None:
    print(f"\n[4] Exact directed Phi (units <= MAX_UNITS=6) — the magnitude is a WIDTH artefact\n")
    print(f"{'W':>4}  {'SELF':>8}{'FF':>8}{'PAIRS0':>8}{'PAIRS.2':>9}   note")
    print("-" * 62)
    for w in (4, 6):
        vals = {}
        for name, wiring, chain in [("SELF", Wiring.SELF, 0.0), ("FF", Wiring.FEEDFORWARD, 0.0),
                                    ("PAIRS0", Wiring.PAIRS, 0.0), ("PAIRS.2", Wiring.PAIRS, INT_CHAIN)]:
            vals[name] = exact_phi(wiring, units=w, chain=chain)
        note = ("SELF~PAIRS0, FF=0" if w == 4 else "SELF>PAIRS0, both huge; FF=0 (only structural zero)")
        print(f"{w:>4}  {vals['SELF']:>8.3f}{vals['FF']:>8.3f}{vals['PAIRS0']:>8.3f}"
              f"{vals['PAIRS.2']:>9.3f}   {note}")
    print("\n  A REDUCIBLE null (SELF) reads a LARGER exact Phi at 6 units than a chained ring reads")
    print("  at 4 — the magnitude tracks width, not integration. Only FEEDFORWARD is structurally 0.")


def report_trials_shrink() -> None:
    print(f"\n[5] The 4-unit reducible magnitude is a SAMPLING artefact (shrinks with trials)\n")
    print(f"{'trials':>7}  {'SELF':>8}{'PAIRS0':>8}{'PAIRS.2 (integrated)':>22}")
    print("-" * 48)
    for trials in (100, 400, 1600, 6400):
        row = {}
        for name, wiring, chain in [("SELF", Wiring.SELF, 0.0), ("PAIRS0", Wiring.PAIRS, 0.0),
                                    ("PAIRS.2", Wiring.PAIRS, INT_CHAIN)]:
            row[name] = statistics.fmean(
                exact_phi(wiring, units=4, chain=chain, seed=s, trials=trials) for s in (1, 2, 3))
        print(f"{trials:>7}  {row['SELF']:>8.3f}{row['PAIRS0']:>8.3f}{row['PAIRS.2']:>22.3f}")
    print("\n  Reducible arms decay toward 0 (their Phi was estimator bias); the integrated arm is flat.")


def main() -> None:
    report_floor_growth()
    report_reducible_nulls()
    report_matched()
    report_exact_artefact()
    report_trials_shrink()


if __name__ == "__main__":
    main()
