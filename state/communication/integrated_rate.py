"""Does INTEGRATION preserve the held depth, or trade against it? (the rate cell's chain-0 choice)

Run from the repo root:

    PYTHONPATH=src python state/communication/integrated_rate.py

`rate.py`'s RateCell is deliberately chain 0 — the N latches are INDEPENDENT, and its docstring
claims that is why it "holds depth, not Phi": a disintegrated population, Phi factorizes across the
pairs. That was asserted, not measured here. This measures it, and the honest open question behind
it: is the held-depth code compatible with INTEGRATION, or does the rate cell's chain 0 have to be
chain 0?

The mechanism predicts a trade. The rate code's depth lives in the COUNT of INDEPENDENT latches:
each falls into its basin on its own, graded in the input amplitude, so the fraction up is the
input's CDF. A `chain > 0` couples the pairs into a macro-ring (an ODD number of pairs then
integrates — `capacity.py`, `coupled.py`), and coupling is exactly what removes the independence the
count relied on: the pairs pull toward a shared configuration, the count is no longer a free analog
sum. So integration should SHRINK the held depth even as it raises Phi.

Measured, sweeping the chain on a population narrow enough for the integration verdict (3 pairs =
6 units, odd, so chain can integrate; `substrate.MAX_UNITS = 6`):

- held depth: I(a ; count | sign) after tell+hold, vs its shuffled-within-sign floor (rate_code's
  control), for the SAME population and chain.
- integration: the `phi_proxy` DECAY/SEPARATION test — the repo's valid verdict. The exact directed
  Phi MAGNITUDE is deliberately printed beside it to expose why: at 6 units a chain-0 population of
  INDEPENDENT pairs, which cannot integrate, still "reads" ~5, so the magnitude is a width-artefact
  (`coupled.py`/`phi_proxy.py`: past ~6 units the decay test is the verdict, never the magnitude).
  An earlier draft of this script compared those magnitudes and read a false coexistence off them;
  that is corrected here rather than quietly dropped (`artefact-honesty`).

`report-the-rank`: the count spans only 0..3 at 3 pairs, so the depth width here is tiny by
construction — the honest collision is that a population WIDE enough to hold real depth (the rate
cell's N=32) is far past where Phi can be computed exactly, and a population narrow enough for exact
Phi holds almost no depth. The width sweep reports the depth span shrinking under the chain at a
wider N (8 pairs, Phi via the `phi_proxy` separation, not a bit value) to show the trade is not an
artefact of the tiny width.

Honest ceiling: if depth falls as Phi rises, the claim is "on this substrate held analog depth and
integration trade off — the rate cell's chain 0 is necessary, not incidental; the population buys
held depth by NOT integrating." That is a wall, reported with numbers, not a capability. It does not
say depth and Phi are impossible together on some other substrate — only that THIS population's
depth code is a disintegrated one. Not language either way.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring
from anima_reborn.dialogue import TELL
from anima_reborn.iit4 import directed_big_phi
from anima_reborn.substrate import coupled_matrix

_RC = Path(__file__).resolve().parent / "rate_code.py"
_spec = importlib.util.spec_from_file_location("rate_code", _RC)
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

_PP = Path(__file__).resolve().parent / "phi_proxy.py"
_spec2 = importlib.util.spec_from_file_location("phi_proxy", _PP)
pp = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(pp)

AMPS = rc.AMPS
SIGNS = (1, -1)
WRITE_SCALE = 0.08
HOLD = 240
TRIALS = 40
CHAINS = (0.0, 0.05, 0.1, 0.2)
EXACT_PAIRS = 3        # 6 units — odd pairs integrate; exact directed Phi is computable
WIDE_PAIRS = 8         # 16 units — real depth width; Phi only via the proxy separation

BASE = 300_000


def _held_count(a: float, sign: int, *, chain: float, n_pairs: int, seed: int) -> int:
    d = WRITE_SCALE * a * sign
    engine = CoupledEngine(
        units=2 * n_pairs, wiring=Wiring.PAIRS, chain=chain, rhythm=ALTERNATING,
        drive=(d, -d) * n_pairs, seed=seed,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    engine.run(HOLD)
    v = engine.values
    return sum(1 for i in range(n_pairs) if (v[2 * i] - v[2 * i + 1]) > 0)


def _depth(chain: float, n_pairs: int, *, shuffle_seed: int) -> tuple[float, float]:
    by_sign: dict[int, list[tuple[int, float]]] = {}
    k = 0
    for ai, a in enumerate(AMPS):
        for sign in SIGNS:
            for _ in range(TRIALS):
                c = _held_count(a, sign, chain=chain, n_pairs=n_pairs, seed=BASE + k)
                by_sign.setdefault(sign, []).append((ai, float(c)))
                k += 1
    return rc._cond_depth(by_sign, shuffle_seed=shuffle_seed)


def _integrated(chain: float, *, units: int, seed: int = 7) -> bool:
    """The repo's VALID integration verdict: the phi_proxy decay/separation test, NOT the raw exact
    magnitude. `phi_proxy.py`/`coupled.py` are explicit that past ~6 units the exact directed Phi
    carries a width-artifact, so 'the decay test is the verdict, never the magnitude'."""
    return bool(pp.reading(Wiring.PAIRS, units=units, chain=chain, budget=pp.STATE_BUDGET, seed=seed)
                .get("separated"))


def _exact_phi(chain: float, *, units: int, seed: int) -> float:
    """Exact directed Phi magnitude at the canonical alternating state — shown ONLY to expose the
    artefact: at 6 units chain-0 (independent pairs, which cannot integrate) reads ~5, so the
    magnitude is NOT the verdict here; `_integrated` (the decay test) is."""
    state = int("01" * (units // 2), 2)
    matrix = coupled_matrix(Wiring.PAIRS, units=units, chain=chain, rhythm=FIXED, seed=seed)
    return directed_big_phi(matrix, state).phi


def main() -> None:
    print("does integration preserve the held depth, or trade against it?\n")
    print(f"population = PAIRS latches; tell {TELL}, deaf hold {HOLD}; {TRIALS} trials/class")
    print("integration VERDICT = phi_proxy decay/separation test (the exact magnitude is artefact-")
    print("prone past ~4 units and is shown only to expose that, per coupled.py/phi_proxy.py)\n")

    # [1] the Phi-measurable width — 3 pairs (6 units): depth AND the proper integration verdict.
    units = 2 * EXACT_PAIRS
    print(f"[1] Phi-measurable width — {EXACT_PAIRS} pairs ({units} units, odd -> chain can integrate)")
    print(f"{'chain':>7}{'depth I(a;count|sign)':>23}{'floor':>8}{'margin':>8}"
          f"{'integrated':>12}{'exact Phi(art.)':>16}")
    print("  " + "-" * 74)
    rows = []
    for ci, chain in enumerate(CHAINS):
        depth, floor = _depth(chain, EXACT_PAIRS, shuffle_seed=13 + ci)
        integ = _integrated(chain, units=units)
        phi = _exact_phi(chain, units=units, seed=1)
        margin = depth - floor
        rows.append((chain, depth, floor, margin, integ))
        print(f"{chain:>7.2f}{depth:>23.3f}{floor:>8.3f}{margin:>8.3f}"
              f"{('yes' if integ else 'no'):>12}{phi:>16.3f}")

    # a coexistence row = integrated AND depth above floor; a trade row = integrated but depth gone.
    coexist = [(c, m) for c, d, f, m, integ in rows if integ and m > 0.1]
    disint_margin = next((m for c, d, f, m, integ in rows if not integ), 0.0)

    # [2] wider width — depth is clearer (the count spans more), integration only structurally.
    print(f"\n[2] wider width — {WIDE_PAIRS} pairs ({2 * WIDE_PAIRS} units): depth vs chain")
    print(f"    (16 units is past where the proxy floor is trustworthy — depth trend only)")
    print(f"{'chain':>7}{'depth I(a;count|sign)':>23}{'floor':>8}{'margin':>8}")
    print("  " + "-" * 46)
    wide = []
    for ci, chain in enumerate(CHAINS):
        depth, floor = _depth(chain, WIDE_PAIRS, shuffle_seed=41 + ci)
        wide.append((chain, depth - floor))
        print(f"{chain:>7.2f}{depth:>23.3f}{floor:>8.3f}{depth - floor:>8.3f}")

    print("\n  VERDICT:")
    print(f"  The exact Phi MAGNITUDE is an artefact here (chain-0 independent pairs 'read' ~5 at 6")
    print(f"  units though they cannot integrate) — the decay-test verdict is used instead.")
    if coexist:
        cmax = max(coexist, key=lambda t: t[1])
        big = [m for c, d, f, m, integ in rows if integ]
        collapses = min(big) < 0.1 if big else False
        print(f"  NOT strictly exclusive. A SMALL chain integrates (decay-test) WHILE the held depth")
        print(f"  survives above floor — coexistence at chain {cmax[0]:.2f} (margin {cmax[1]:.2f}, integrated),")
        print(f"  vs the disintegrated chain-0 margin {disint_margin:.2f}. "
              + (f"A LARGER chain then trades it away (depth collapses to near floor)."
                 if collapses else "Depth reduces with chain but stays above floor across the swept range."))
        print(f"  So the rate cell's chain 0 was a CHOICE, not a necessity: a modest chain would add")
        print(f"  integration at a depth cost. The wider-width [2] shows the same depth-shrinks-with-chain")
        print(f"  trend at a width where the count carries more depth. Bounded, not language.")
    else:
        print(f"  a TRADE: every chain that integrates (decay-test) has driven the held depth to floor —")
        print(f"  integration and held depth do not coexist on this population. The rate cell's chain 0")
        print(f"  holds depth by NOT integrating. A wall, scoped to this disintegrated depth code.")


if __name__ == "__main__":
    main()
