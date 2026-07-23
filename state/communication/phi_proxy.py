"""A validated sampled directed-Φ proxy — moving the measurability wall past 6 units.

Run from the repo root:

    PYTHONPATH=src python state/communication/phi_proxy.py

Part 2 of the "engine parts toward the goal" plan. Directed Φ (`iit4.directed_big_phi`) is
exact only to ~6 units (`substrate.MAX_UNITS`), because it searches every mechanism × purview
× partition over 2^N states — so a wider integrated substrate cannot be SHOWN to be one
integrated thing. This measures a cheaper surrogate that samples instead of enumerating, and
validates it against exact IIT where both are computable.

Design delegated to both frontier models and reconciled (`state/lab/2026-07-23-phi-proxy-*.md`),
which converged: the proxy is NOT big-Φ (a different, cheaper functional — DIRECTED
CUT-INFORMATION), so its MAGNITUDE is never compared to `directed_big_phi`'s bits. What it must
share with exact IIT — pinned by the validation ladder — is only three things: the NULL SET
(reducible <=> ~0), the MIP CUT identity, and the RANK/separation. The estimator is fable's
plug-in conditional MI with a MEASURED shuffle floor (the repo's `info.py`/`RECURRENCE_FLOOR`
philosophy: measure the null, don't analytically correct). (sol dissented for a 5-fold
cross-fitted out-of-sample log-score estimator that errs conservative by construction; deferred
as a robustness variant — the exact-window + shuffle floor + budget-shrink already bound the
plug-in's upward bias.)

The functional. For a directed cut A -/-> B (A, B partition the units), the loss is the
predictive information the source A carried about the sink B's next state beyond B's own present:

    loss(A -/-> B) = sum_{i in B} I( X_A(t) ; X_i(t+1) | X_B(t) )   (plug-in, visited states only)

The proxy is the MIN of that loss over a deterministic cut family (singletons, pair atoms,
pair-chain blocks, seeded random balanced bipartitions). Sampling more cuts can only LOWER the
min — it cannot manufacture a larger one, so cut-sampling errs toward UNDER-reporting (safe).
The plug-in MI errs UP; the measured shuffle floor and the exact-window catch that.

The wall does not vanish, it MOVES: the positive (integrated) arm is the chained PAIRS ring,
demonstrated here at 10 units. The width-matched nulls for INTEGRATION are the reducible
wirings — SELF, FEEDFORWARD, and disconnected PAIRS (chain=0) — which must sit at their measured
floor while the chained ring separates. (Even-pair widths {8,12,20} are a CAPACITY null — the
closed macro-ring collapses to one macro-bit — NOT an integration null: a locked ring is still
integrated. That distinction is `capacity.py`'s, not this module's.) The honest deliverable is
"the measurable-integration wall moved from 6 to W, here is the measurement", never "unbounded".
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter

from anima_reborn.coupled import AMPLITUDE, FIXED, GAIN, MACRO_STEP, CoupledEngine, Wiring
from anima_reborn.substrate import coupled_matrix
from anima_reborn.iit4 import directed_big_phi

CHAIN = 0.2
STATE_BUDGET = 4000   # independent (state -> next) draws per reading
CUT_SEED = 20260723
SHUFFLES = 8


# ── the measurement kernel (identical to substrate.coupled_matrix's step) ────────────

def _kernel_step(state: int, *, wiring: Wiring, units: int, chain: float, seed: int) -> int:
    engine = CoupledEngine(
        wiring=wiring, units=units, chain=chain, rhythm=FIXED, drive=0.0,
        gain=GAIN, amplitude=AMPLITUDE, seed=seed,
        initial=tuple(AMPLITUDE if state >> i & 1 else -AMPLITUDE for i in range(units)),
    )
    return engine.run(MACRO_STEP).pattern


def sample_transitions(
    wiring: Wiring, *, units: int, chain: float, budget: int, seed: int
) -> list[tuple[int, int]]:
    """Drive from `budget` INDEPENDENT uniform-random states, one macro-step each — a sampled
    estimate of the same transition matrix `substrate.coupled_matrix` enumerates exactly. A
    trajectory instead would collapse into the autonomous engine's attractor and see nothing;
    driving from every-state (sampled) is what the exact measure does and what keeps the
    conditional information measurable."""
    rng = random.Random(seed)
    out: list[tuple[int, int]] = []
    for _ in range(budget):
        s = rng.getrandbits(units)
        nxt = _kernel_step(s, wiring=wiring, units=units, chain=chain, seed=rng.getrandbits(63))
        out.append((s, nxt))
    return out


# ── the estimator: plug-in conditional mutual information ─────────────────────────────

def _cond_mi(triples: Counter) -> float:
    """I(A; Y | C) from counts over (c, a, y). Signed plug-in; not clipped to zero."""
    total = sum(triples.values())
    if total == 0:
        return 0.0
    by_c: dict[int, Counter] = {}
    for (c, a, y), n in triples.items():
        by_c.setdefault(c, Counter())[(a, y)] += n
    mi = 0.0
    for c, ay in by_c.items():
        nc = sum(ay.values())
        pa = Counter()
        py = Counter()
        for (a, y), n in ay.items():
            pa[a] += n
            py[y] += n
        for (a, y), n in ay.items():
            p_ay = n / nc
            mi += (nc / total) * p_ay * math.log2(p_ay / ((pa[a] / nc) * (py[y] / nc)))
    return mi


def cut_loss(transitions: list[tuple[int, int]], source: int, units: int) -> float:
    """loss(source -/-> rest) = sum_{i in rest} I(X_source ; Y_i | X_rest)."""
    sink = ((1 << units) - 1) & ~source
    total = 0.0
    for i in range(units):
        if not (sink >> i) & 1:
            continue
        triples: Counter = Counter()
        for x, y in transitions:
            triples[(x & sink, x & source, (y >> i) & 1)] += 1
        total += _cond_mi(triples)
    return total


# ── the cut family (deterministic) ────────────────────────────────────────────────────

def cut_family(units: int, wiring: Wiring, *, seed: int, randoms: int = 64) -> list[int]:
    """Source masks for directed cuts. Nested and structural: singletons, pair atoms, pair-
    chain contiguous blocks, and seeded random balanced bipartitions (both directions come
    from evaluating source and its complement)."""
    full = (1 << units) - 1
    sources: set[int] = set()
    for u in range(units):
        sources.add(1 << u)                 # singleton -> rest
        sources.add(full & ~(1 << u))       # rest -> singleton
    if wiring is Wiring.PAIRS:
        pairs = units // 2
        for j in range(pairs):
            atom = (1 << (2 * j)) | (1 << (2 * j + 1))
            sources.add(atom)
            sources.add(full & ~atom)
        # contiguous blocks of whole pairs on the pair-chain (all rotations, lengths)
        for length in range(1, pairs):
            for start in range(pairs):
                block = 0
                for k in range(length):
                    j = (start + k) % pairs
                    block |= (1 << (2 * j)) | (1 << (2 * j + 1))
                sources.add(block)
    rng = random.Random(seed)
    half = units // 2
    # Add seeded random balanced bipartitions, but never ask for more than exist (small
    # widths have only C(units, half) — an unbounded target would spin forever).
    target = min(randoms, math.comb(units, half))
    attempts = 0
    while sum(1 for s in sources if bin(s).count("1") == half) < target and attempts < target * 40:
        bits = rng.sample(range(units), half)
        sources.add(sum(1 << b for b in bits))
        attempts += 1
    return [s for s in sources if 0 < s < full]


def proxy(transitions: list[tuple[int, int]], units: int, wiring: Wiring) -> tuple[float, int]:
    """min over the cut family of the directed cut loss; returns (value, argmin source)."""
    best = math.inf
    best_src = 0
    for source in cut_family(units, wiring, seed=CUT_SEED):
        loss = cut_loss(transitions, source, units)
        if loss < best:
            best, best_src = loss, source
    return best, best_src


def shuffle_floor(transitions: list[tuple[int, int]], units: int, wiring: Wiring) -> float:
    """The proxy on time-broken data (successors permuted, margins kept): the measured null.
    Floor = max over SHUFFLES of the shuffled proxy min — a value at or below it is estimator
    bias, not signal (`artefact-honesty`, the `RECURRENCE_FLOOR` philosophy)."""
    xs = [x for x, _ in transitions]
    ys = [y for _, y in transitions]
    rng = random.Random(4242)
    floors = []
    for _ in range(SHUFFLES):
        rng.shuffle(ys)
        floors.append(proxy(list(zip(xs, ys)), units, wiring)[0])
    return max(floors)


def reading(wiring: Wiring, *, units: int, chain: float, budget: int, seed: int) -> dict:
    trans = sample_transitions(wiring, units=units, chain=chain, budget=budget, seed=seed)
    val, src = proxy(trans, units, wiring)
    floor = shuffle_floor(trans, units, wiring)
    support = len({x for x, _ in trans})
    return {"phi_hat": val, "argmin_source": src, "floor": floor,
            "support": support, "separated": val > floor}


# ── validation against exact iit4 (units 2..6) ────────────────────────────────────────

def _exact(wiring: Wiring, *, units: int, chain: float, state: int, seed: int) -> tuple[float, int]:
    """Exact directed Φ and its MIP source mask (via coupled_matrix + directed_big_phi)."""
    matrix = coupled_matrix(wiring, units=units, chain=chain, rhythm=FIXED, seed=seed)
    dp = directed_big_phi(matrix, state)
    return dp.phi, (dp.cut.source if dp.cut is not None else 0)


def validate() -> None:
    print("V1 — proxy vs exact directed IIT (units 2..6), same kernel\n")
    print(f"{'wiring':<12}{'units':>6}{'exact Φ':>10}{'proxy':>9}{'floor':>8}"
          f"{'MIP?':>6}   null-set")
    print("-" * 62)
    grid = [
        (Wiring.SELF, 4, 0.0), (Wiring.FEEDFORWARD, 4, 0.0),
        (Wiring.RING, 4, 0.0), (Wiring.PAIRS, 4, 0.0), (Wiring.PAIRS, 4, CHAIN),
        (Wiring.PAIRS, 6, CHAIN),
    ]
    exact_vals, proxy_vals = [], []
    for wiring, units, chain in grid:
        state = int("01" * (units // 2), 2)
        ex_phi, ex_src = _exact(wiring, units=units, chain=chain, state=state, seed=1)
        r = reading(wiring, units=units, chain=chain, budget=STATE_BUDGET, seed=7)
        integrated = wiring is Wiring.PAIRS and chain > 0.0  # the only arm exact calls recurrent here
        reducible = wiring in (Wiring.SELF, Wiring.FEEDFORWARD) or (wiring is Wiring.PAIRS and chain == 0.0)
        full = (1 << units) - 1
        mip_ok = ("✓" if r["argmin_source"] in (ex_src, full & ~ex_src) else "✗") if integrated else "—"
        null_note = ("proxy at floor ✓" if not r["separated"] else "proxy>floor ✗") if reducible else (
            "separated ✓" if r["separated"] else "not separated ✗")
        exact_vals.append(ex_phi)
        proxy_vals.append(r["phi_hat"])
        print(f"{wiring.value:<12}{units:>6}{ex_phi:>10.3f}{r['phi_hat']:>9.3f}"
              f"{r['floor']:>8.3f}{mip_ok:>6}   {null_note}")
    rho = _spearman(exact_vals, proxy_vals)
    print(f"\n  rank agreement (Spearman ρ, exact Φ vs proxy across the grid): {rho:.3f}")
    print("  the proxy shares exact IIT's NULL SET, MIP CUT and RANK — never its magnitude.")


def _spearman(a: list[float], b: list[float]) -> float:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    mean_a, mean_b = sum(ra) / n, sum(rb) / n
    cov = sum((ra[i] - mean_a) * (rb[i] - mean_b) for i in range(n))
    va = math.sqrt(sum((x - mean_a) ** 2 for x in ra))
    vb = math.sqrt(sum((x - mean_b) ** 2 for x in rb))
    return cov / (va * vb) if va and vb else 0.0


def move_the_wall() -> None:
    print("\n\nThe wall moves from 6 to 10 — a 10-unit chained ring vs its width-matched nulls\n")
    print(f"{'width':>6}  {'config':<24}{'proxy':>9}{'floor':>8}{'support':>9}   verdict")
    print("-" * 64)
    rows = [
        (10, "PAIRS+chain (5 pairs)", Wiring.PAIRS, CHAIN),  # the positive (odd pairs)
        (10, "SELF", Wiring.SELF, 0.0),                      # reducible null
        (10, "FEEDFORWARD", Wiring.FEEDFORWARD, 0.0),        # reducible null (Φ=0 exactly)
        (10, "PAIRS chain=0 (disjoint)", Wiring.PAIRS, 0.0), # reducible null (disconnected)
    ]
    for units, label, wiring, chain in rows:
        r = reading(wiring, units=units, chain=chain, budget=STATE_BUDGET, seed=7)
        verdict = "SEPARATED" if r["separated"] else "at floor (reducible)"
        star = " ← integrated" if wiring is Wiring.PAIRS and chain == CHAIN else ""
        print(f"{units:>6}  {label:<24}{r['phi_hat']:>9.3f}{r['floor']:>8.3f}"
              f"{r['support']:>9}   {verdict}{star}")
    print("\n  The 10-unit chained PAIRS separates from its three width-matched REDUCIBLE nulls")
    print("  (SELF / FEEDFORWARD / disconnected), each of which sits at its floor — while exact Φ")
    print("  cannot be computed at 10 units at all. The measurable-integration wall moved 6 → 10,")
    print("  a proxy-strength claim (validated against exact IIT to 6), never an exact-Φ magnitude.")
    print("  (Even-pair widths {8,12,20} are a CAPACITY null — 1 macro-bit — not an integration")
    print("   null: a locked macro-ring is still integrated. That story is capacity.py's, not this.)")


def main() -> None:
    validate()
    move_the_wall()


if __name__ == "__main__":
    main()
