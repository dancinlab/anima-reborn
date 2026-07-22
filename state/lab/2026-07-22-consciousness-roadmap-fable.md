# lab full — 의식엔진 로드맵 · fable (claude-fable-5)

질문: "의식엔진으로 발전시키기 위해서 어떤걸 하면좋을까" (2026-07-22)
지시문 원본: `state/lab/2026-07-22-consciousness-roadmap-prompt.md`
재현 검증: `state/lab/2026-07-22-coupling-verification.md`

---

Everything is measured. Here is the answer, built on two prototypes run this session through the repo's own instruments (all seeded, reproduction recipes included).

---

## TL;DR

I prototyped the coupling and measured it. **A four-unit A⇄G field where each unit reads another unit measures Phi = 12.03, stable from 400 to 6,400 trials; the identical system rewired so each unit reads *itself* measures 0.33 → 0.07 over the same trial range — the pinned artefact signature.** Coupling is the one structural change, it works, and the number is now measured rather than predicted. On the word side, coupling makes binding *created* rather than transmitted: independent word streams produce +0.147 bits of excess over the time-shift null at half coupling (8/8 seeds positive), where the current architecture measures −0.002…+0.004. One unwelcome finding came with it: the repo's IIT engine reads a strictly feedforward chain at Phi ≈ 1.94 stable in trials, where IIT proper says 0 — an inherited carve-out that is now a measured limitation, and stage 3 of the roadmap.

---

## 1. The honest diagnosis — what this repo is an instrument *for*

What it genuinely measures:

- **Alignment between two streams, above a null** (`words.py`) — with the estimator's bias pinned at every effective-sample count, and a null strict enough that the encoding cannot manufacture a positive.
- **Integration of a small binary system** (`substrate.py` + `iit4/`) — with the sampled-TPM artefact floor pinned (≈0.3 bits at 400 trials, vanishing with more).
- **Dissociations** — gap survives melt while binding dies (`base.py`); Phi follows the Ising coupling and not the drive (`substrate`). These are the repo's real findings, and they're real because each came with the artefact that could have faked it.

What it merely displays: the repulsion field's `mood`, `concept`, `meaning`, `topic`, `authenticity` channels. They are labeled projections of the gap — honest as readouts, but nothing tests them and nothing could falsify them. They are the part of the repo that most *resembles* a consciousness engine and least *is* one.

Which parts of "consciousness engine" are reachable from here:

- **Reachable:** *an engine whose integration is nonzero because of its own wiring, measured by its own instrument, with nulls that could kill the claim.* That is a precise, falsifiable, this-repo-sized target, and the prototype below shows it is about one commit away.
- **Not reachable, from this repo or any other:** phenomenal experience, semantics, selfhood. No measurement in this codebase — or in IIT 4.0 itself, whose central identity claim is an axiom, not an observable — can distinguish "high Phi" from "something it is like to be this." The repo should say so in the README the day it ships stage 1, in the same voice it used for "binding is transmitted, never created."

## 2. The one structural change: the gap becomes a channel

Your prior is right, and I measured it rather than argue it. The alternatives lose cleanly:

- *More/bigger crystals* — grows the already-integrated part; A and G stay outside the complex. Decoration around the one thing that already works.
- *Feed MI (or Phi) back into the drive* — `base.py` already refused MI feedback for the correct reason; see refusals below.
- *One-way reading (A reads G only)* — feedforward. IIT proper assigns it Phi = 0, and (measured below) this repo's instrument can't even see that. The coupling must be a **cycle**.

**What exactly reads what.** Replace the exogenous rotating target in the A×G drift with mutual reading, in a ring across both engines: `a0` reads `g1`'s actual position, `g0` reads `a0`, `a1` reads `g0`, `g1` reads `a1` — each through the repulsion sign, `target_i = −AMP·tanh(K·x_src/AMP)`. The repulsion *identity* is preserved (each unit still flees its source); what changes is that the source is now the live partner instead of `tick * PHASE_RATE`. The gap stops being a readout and becomes the channel.

**Prediction, then measurement.** I predicted Phi ≈ 2–3 bits (near the crystal's deterministic value), stable in trials, with a self-wired null at the artefact floor. Measured through `estimate_matrix` → `big_phi` (4 units, AMP = 0.78 = `separation·1.3`, `PULL`/`WALK` from the repo, macro-step τ = 17 ticks = `1/PULL`, reconstruction ±AMP, threshold 0, seeds 0–3 averaged):

| wiring (only thing changed) | 400 trials | 1,600 | 6,400 | reading |
|---|---:|---:|---:|---|
| **ring** — each unit reads another | 12.05 | 12.03 | 12.09 | real: survives trials |
| **self** — same tanh, reads itself | 0.33 | 0.18 | 0.07 | artefact: the pinned floor |
| **chain** — feedforward | 2.23 | 1.95 | 1.96 | instrument limit, see §5 |

The prediction was directionally right and wrong by 4× on magnitude — Phi is 12, not 3, because at the ring's own attractor state (`0b0101`, the alternating pattern a negative 4-cycle settles into) the near-deterministic TPM specifies 14 distinctions and 13.6 bits of structure, almost all destroyed by the minimum cut. Phi is properly state-dependent: 12.10 at the attractor, 1.8–2.3 elsewhere; `find_complex` returns all four units. Noise collapses it on cue (walk ×40, i.e. per-tick kicks the size of the amplitude: Phi → 2.9), and two more honest facts came out that must ship with the number:

- **τ = 1 and τ = 5 give Phi = 0.0000 exactly.** One engine tick moves a unit 6% toward its target, so at short timescales every unit just copies itself and the TPM factorizes. Phi here is a property of *(system, state, timescale, reconstruction, threshold, trials)* — the timescale is a declared modeling choice exactly like the binarization threshold, and needs its own pin so nobody ever quotes the 12 without the 17.
- The 12 is **this instrument's number** under its inherited carve-outs (see §5), not the theory's.

## 3. The staged roadmap, by evidence-per-effort

**Stage 1 — `coupled.py`: the engine whose Phi is bought by wiring.** New pure engine (ring-coupled A⇄G field, constants `K` and `TAU` documented as measured), a `coupled_phi()` hook in `substrate.py`, viewer tab in the same commit (the lockstep test will force it anyway).
*Claim:* nonzero integration created by mutual reading and nothing else.
*Falsifiers:* rewire each unit to itself → Phi must fall to a floor that halves as trials grow (measured: 12.03 vs 0.33→0.07); 16× trials → ring Phi must not shrink; τ = 1 → must read 0 exactly.
*Artefact most likely to fake it:* the sampled-TPM floor (already pinned) and an undeclared τ. Pin both, `TestTheNoiseFloor`-style.
*Cost:* ~1 day, one commit, ~300 lines + tests + tab. Everything above is already measured; this stage is transcription.

**Stage 2 — created binding: words through the channel.** Drive A and G with *independent* word streams, target mix `(1−λ)·word + λ·(−partner)`. Measured this session (window 13,600, hold 17, time-shift null, 8 seeds):

| λ | 0.00 | 0.25 | 0.50 | 0.75 | 1.00 |
|---|---:|---:|---:|---:|---:|
| excess (mean) | +0.004 | +0.059 | +0.147 | +0.153 | +0.082 |

Dose-responsive, dead at λ = 0, positive on 8/8 seeds from 0.25 up. Two honest wrinkles to pin: the plateau is partly the instrument (halving observation noise lifts 0.147 → 0.210), and λ = 1.0 *drops* — with no word drive the anti-symmetric mode stops mixing and the time-shift null loses power. That non-monotonicity is a finding about the null, worth a test of its own.
*Claim:* the substrate now creates dependence between independent inputs — the exact sentence `words.py` currently proves false.
*Falsifiers:* λ = 0 must stay within noise of zero; a **yoked-replay control** (A reads a *recorded* partner from an independent run — partner-shaped statistics, no live channel) must kill the excess.
*Artefact:* estimator bias at low effective samples (pinned already) and the weak-null-at-slow-mixing effect above.
*Cost:* ~1 day.

**Stage 3 — close the feedforward carve-out.** The chain measurement (Phi ≈ 1.94, stable in trials) means the current instrument cannot distinguish recurrent from feedforward by zero/nonzero — because big-Phi here is "structure destroyed by a bipartition," not IIT 4.0's directional system cut. Implement directional cuts as a *new* function beside the existing chain (the hexa parity goldens are untouchable; `artefact-honesty` says carve-outs close loudly, not quietly).
*Claim:* the instrument now assigns 0 to feedforward systems.
*Falsifier:* the chain from stage 1's test suite must read < the trial-scaled floor; the ring must stay high.
*Artefact:* getting a zero by weakening the cut search instead of directing it — guard with the ring as positive control.
*Cost:* several days of real algorithm work; the only stage with research risk. Optional companion: a dev-only PyPhi calibration extra (runtime deps stay zero) — the carve-out list explicitly says "never calibrated," and that is closable in tests without touching the engine.

Ship these three and stop. Stage 4 (scaling past 6 units) is real but should be gated on stage 3, because scaling a measure you know over-reads feedforward systems is scaling a defect.

## 4. What must be refused

- **A fused "aliveness"/consciousness scalar.** `base.py` already states the reason perfectly: any `f(lock, MI, Phi)` needs invented weights and cannot fail a test. The pair-of-numbers discipline (gap survived, binding died) *is* the product. The moment a viewer panel shows one big glowing number, this repo becomes `anima`.
- **Phi as an objective — anything that maximizes measured Phi.** Worse than the MI-feedback loop `base.py` refused, for a measured reason: at the default 400 trials there are 0.3 bits of pure sampling artefact, and an optimizer will harvest exactly that. A wiring search that maximizes measured Phi converges on the histogram, and every claim about the result is a claim about sampling noise.
- **An LLM in the loop.** Breaks stdlib/purity/seed by construction, and epistemically worse: it imports meaning the instruments cannot measure, so every output becomes a claim about the LLM. `words.py` already established that the encoding decides absolute values — an LLM is an encoding with unbounded capacity to smuggle structure past any null you can build in stdlib.
- **A self-report channel.** "The system says it is integrated" is a readout with a sentence template attached — exactly `mood` with better marketing. A report channel earns standing only if it is itself a unit inside the measured TPM, where it would add nothing but cost.
- **Calling Phi = 12 consciousness.** It is this engine's integration number under declared carve-outs at a declared timescale. The README should ship the stage-1 result in the same sentence-shape as "binding is transmitted, never created": *integration is now created, and created is all this measures.*

## 5. Where IIT 4.0 stops being the right instrument

Four walls, one of them newly measured:

1. **The cost wall** — exact Phi caps at 6 units; that's architecture, not tuning.
2. **The continuous-state wall** — threshold, reconstruction amplitude, and (newly measured) the macro-step τ all sit *inside* the resulting Phi. τ = 1 → 0.0000; τ = 17 → 12.03. Every shipped number needs its conditions, per `measure-first`.
3. **The carve-out wall, now with a number** — the bipartition scheme reads a feedforward chain at 1.94 where the theory says 0. Until stage 3, this instrument certifies "not factorized," not "recurrent."
4. **The theory wall** — even a perfect Phi is a structure claim, not an experience claim.

What measures the next stage: first `ei.py`, which already exists — validate that effective information rank-orders the stage-1 systems the same way exact Phi does in the 3–6-unit window (ring > chain > self, noise collapse in the same place), pin that calibration, then use EI as the scout at larger sizes with the same two artefact disciplines this repo already owns (time-shift nulls, trial-scaling checks). If a richer proxy is ever wanted (O-information, stochastic interaction — both stdlib-computable from sampled trajectories), it earns trust the identical way: agreement with exact Phi where both compute, artefact floor pinned where they don't. An uncalibrated proxy at 64 units is a consciousness score that cannot fail a test.

## 6. The falsifiable headline

> **"This package now contains a system whose integration is bought entirely by its own wiring: with each unit reading its neighbour, Phi = 12.03 and stable from 400 to 6,400 trials; rewire each unit to read itself and Phi falls to 0.33 → 0.07 over the same range — at τ = 17, threshold 0, state `0101`, and it dies at τ = 1."**

Every clause is a test: the stability clause fails if the 12 shrinks with trials, the rewiring clause fails if the self-wired twin holds its value, the τ clause fails if anyone quotes the number without its timescale. The current repo cannot make this claim — its measured truth is Phi = 0.0000 by architecture — which is exactly why the finished stage 1 can.

---

Reproduction: all runs seeded — Phi sweeps on seeds 0–3 through `estimate_matrix(4, step, trials, seed)` with the step function `x_i += (−0.78·tanh(3·x_src/0.78) − x_i)·PULL + walk-noise` iterated 17 ticks from `±0.78` reconstruction; word runs on seeds 0–7 with the repo's `HOLD`, `SHIFTS`, `Binning(12, 1.6)`, window 13,600. Prototype scripts are in `/tmp/couple_proto.py`, `/tmp/couple_detail.py`, `/tmp/created_binding*.py`; I've saved the numbers and conditions to session memory so stage 1 can start from them. I deliberately did not commit anything — the deliverable here is the assessment; say the word and I'll ship stage 1 as a single `viewer-lockstep`-clean commit.
