# Design task: conditional composition — the held past ACTS on the current write, measured honestly

Part 4 of the "engine parts toward the goal" plan (both of you converged last round;
`state/lab/2026-07-23-new-parts-*.md`). Parts 1-2 landed: `src/anima_reborn/sequence.py` — a
shift chain of K proven 3-bit cells that holds the last K symbols IN ORDER (memory), measured
in `state/communication/accumulation.py`; and `state/communication/phi_proxy.py` — a validated
sampled directed-Φ proxy that moved the integration-measurability wall 6 → 10 units.

But the shift chain is a RECORDER: it holds, it does not USE the past. Both of you named the
next honest step toward language: **the held past must ACT on the current write** — context.
Design that component + the measurement that proves it is real, not planted. Return a concrete
architecture + validation protocol. Do NOT write full code.

## What exists (read it)

- `src/anima_reborn/sequence.py`: `SequenceEngine`, K=4 cells (6-unit `Wiring.PAIRS`, chain=0.2),
  each holds 3 bits deaf. `turn(symbol)` shifts every held word one cell down (via a clean
  `dialogue.channel(bits=3)` bridge) then writes the new symbol to cell 0. `tape()` reads all K.
- `state/communication/accumulation.py` measured: 12 bits held in order, deaf-bridge / time-shift
  / cross-cell / perturbation nulls all pass; the bridge is a TRANSPORT claim, never integration.
- `state/communication/retention.py`: the deaf-hold is a self-correcting basin (small jolt
  recovers, large jolt crosses a finite barrier), so the state lives in the engine's DYNAMICS,
  not a Python variable.
- `src/anima_reborn/coupled.py`: `CoupledEngine`, per-unit `drive` (a vector), `chain`, `Rhythm`.

## Your own prior sketches (reconcile and sharpen these)

- fable: "the bridge's sign/gate is MODULATED by the previous cell's differential state. Measure
  SYNERGY — the amount I(read; s_t, s_{t-1}) exceeds the sum of the individual MIs — null =
  shuffled history."
- sol: a `ContextGate` — genuine but BOUNDED temporal state; the receiver's transcript may
  accumulate info but the engine must not thereby be credited with sequence memory; free play is
  descriptive only, evidence comes from a blind frozen audit.

## The trap you must both name and kill

History-dependence is trivial to FAKE: if the "context effect" is just the bridge deterministically
copying the previous cell (a rule the designer wired in), that is not the engine composing — it is
the designer's lookup table. The D7 death (`attractor_canonicalization.py`) is the ancestor: a
planted structure that scores. The control must isolate GENUINE synergy (the whole read depends on
the pair (current, past) BEYOND what each contributes alone AND beyond a deterministic copy) from
a planted rule, with a shuffled-history null and a "no-gate" baseline.

## What I need — answer each explicitly

1. **The mechanism.** The smallest honest way the held past acts on the current write, added to
   `sequence.py` (or a sibling), stdlib + seedable + `engine-purity`. Exactly what modulates what:
   does the previous cell's held differential bias the current cell's drive/gate? Keep it a DYNAMICAL
   coupling (measurable), not a Python `if`. `default-stays-exact`: it must default OFF, leaving
   `SequenceEngine` bit-identical, pinned by a test.
2. **The measurement of synergy.** The exact quantity: interaction information / synergy
   I(read ; current, past) − I(read;current) − I(read;past), or a co-information, computed with
   exact categorical MI (not `info.py`'s binning) over sampled reads. What is "read" here — a held
   cell, a probe response? State it so it is unambiguous.
3. **The nulls (the load-bearing part).** At minimum: (a) shuffled-history — pair each read with a
   RANDOM past instead of its true past, synergy must vanish; (b) no-gate baseline — the same engine
   with the gate off, synergy ~0 (context is what the gate buys, `channel-before-carrier`); (c) the
   deterministic-copy control — show the synergy is not reproducible by a fixed lookup (e.g. the
   gate's effect survives when the past is a NEW random symbol the engine could not have memorized a
   rule for). Give the exact null battery and what each kills.
4. **The honest verdict + ceiling.** The sentence it earns and the sentence it must NOT. Even with
   context, I(X;Y) ≤ 3 bits per moment stays bound; the claim is "the current exchange depended on
   the held past, by measured synergy above its shuffled-history null" — working memory that is
   USED, not language. Where exactly is the line?
5. **The phased first commit.** Smallest honest thing: a pure `state/` measurement (a sibling of
   `accumulation.py`) driving `SequenceEngine` with the gate, filling RESULTS from the run — matching
   how every part here landed — with the `src/` gate parameter + a viewer readout following. What is
   deferred (e.g. the multi-turn working-memory conversation game in `conversation.py`)?

Keep the discipline: never a number that was not measured; every capability with the null that could
fake it; report effective rank/width beside any synergy; the engine is not language — the gain is
CONTEXT (current depends on held past), earned by synergy over a shuffled-history null, nothing more.
If the honest result is "the gate adds no measurable synergy beyond the copy," say so and prune it.
