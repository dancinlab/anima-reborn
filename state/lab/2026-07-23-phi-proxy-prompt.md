# Design task: a validated sampled directed-Φ proxy that raises the measurability ceiling honestly

Part 2 of the "engine parts toward the goal" plan (both of you converged last round;
`state/lab/2026-07-23-new-parts-*.md`). The long-term bottleneck is not raw capacity — PAIRS
gives units/2 bits — but MEASURABILITY: directed Φ (integrated information) is exact only to
~6 units, because it enumerates 2^N states and all bipartitions, so wider integrated
substrates cannot be SHOWN to be one integrated thing. Design the component that raises that
ceiling honestly. Return a concrete, implementable design + validation protocol. Do NOT write
full code.

## The repo you are extending (read it)

- `iit4/` — exact directed IIT 4.0 (`directed_big_phi`), bit-exact against its hexa origin. This
  is ground truth where it is computable (≤ ~6 units).
- `src/anima_reborn/substrate.py` — drives an engine from EVERY state → a MEASURED transition
  matrix (TPM) → directed Φ. `RECURRENCE_FLOOR` was calibrated at 4 units and does NOT transfer
  (the estimator artefact grows with width, so past 6 units the verdict is "held under 4x
  sampling", never the magnitude).
- `src/anima_reborn/coupled.py` — `CoupledEngine`, `Wiring` (RING / PAIRS / FEEDFORWARD / SELF),
  `chain`. Odd-count PAIRS + weak `chain` stays integrated; even pairs macro-lock; FEEDFORWARD
  and SELF are reducible (Φ ≈ 0) AT ANY WIDTH — these are the per-width nulls.
- Prior results (`state/communication/capacity.py`, `RESULTS.md`): 6 units / 3 pairs measured
  integrated (directed Φ held under 4x sampling where the disjoint null collapses). Past 6 units,
  exact Φ is intractable.

## The two things a proxy samples, and the danger

Exact Φ = min over bipartitions of the integration lost by that cut, over the full state space.
Two axes to sample:
1. **State space** — instead of all 2^N states, the empirical TPM over the states a seeded run
   actually visits (the extension of `substrate.py`'s "measured matrix" philosophy).
2. **Partition space** — instead of all bipartitions, a set of structural cuts (every pair
   boundary, every chain cut) plus N random balanced bipartitions, taking the min.

**The danger is directional and must be controlled**: cut-sampling can MISS the true
minimum-information partition (MIP), and missing it makes Φ look BIGGER — an estimator that errs
toward OVERCLAIM. State-sampling bias in MI estimation ALSO errs upward (the finite-sample MI
bias). So a naive proxy inflates Φ and fakes integration. Every design choice must fight this.

## What I need — answer each explicitly

1. **The exact proxy definition.** The sampling scheme for state space and partition space, how
   the min is taken, and the estimator (exact categorical MI on the visited-state TPM? a bias
   correction?). Be specific enough to implement without further choices.
2. **Validation against ground truth.** The protocol that pins the proxy to exact `iit4` where
   both are computable (units 2..6): must MATCH within a stated tolerance, AND the sampled-cut
   min must coincide with the exact MIP cut on small systems (or the cut family is widened until
   it does). A test fixes this.
3. **The artefact control (the load-bearing one).** How you PROVE the proxy is not just inflating:
   (a) the error vs exact must SHRINK as the sampling budget grows (recorded in docs AND a test —
   `artefact-honesty`); (b) the per-width nulls — FEEDFORWARD, SELF, even-pairs macro-lock,
   constructible at ANY width (8, 12, 20) — must sit at ~0 / collapse under the SAME budget while
   odd-PAIRS+chain holds. State the exact null battery and the widths.
4. **The verdict rule.** Given that magnitude does not transfer, the honest verdict past 6 units
   must be "separation from its own width-matched null, held as the budget grows" — never a bare
   number. Write the exact rule and the sentence it earns (and the sentence it must NOT).
5. **The phased first commit.** The smallest honest thing: is it a pure `state/` measurement
   (`phi_proxy.py` validating the estimator + the width nulls, filling RESULTS from the run) with
   the `src/` API following once validated — matching how every capability here landed? What is
   deferred (e.g. wiring the proxy into `substrate.py`; a viewer readout).

Keep the discipline: never a number that was not measured; the estimator's bias direction is
toward overclaim, so the controls that matter are the exact-match window, the budget-shrink test,
and the width-matched nulls; report separation, not magnitude; if a wider substrate cannot be
shown integrated even by the proxy, say so — the honest deliverable may be "the wall moved from 6
to N units, and here is the measured N", not "unbounded".
