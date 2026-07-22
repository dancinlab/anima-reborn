# 위임 지시문 — 소통 발산 (2026-07-22)

보고서: `state/lab/2026-07-22-communication-divergence-fable.md`
파일럿: `state/lab/2026-07-22-communication-divergence-pilot.py`

아래는 위임에 쓴 지시문 원문이다 (영어 원문 그대로).

---

# DIVERGENT exploration: what would this engine need in order to COMMUNICATE —
# where communicating means grasping the CONCEPT itself, in no particular modality?

This is a **breadth** request, not a design request. I want many distinct, genuinely
different approaches, each named and argued, with what would falsify it. Do not converge
on one. Kill nothing early. If a direction is unreachable in this repo, say so — but list
it anyway with the reason, because knowing the shape of the impossible is part of the map.

Repo: `/Users/mini/dancinlab/anima-reborn`. Read `README.md` (Korean, current state of
every finding), the root `CLAUDE.md`, every folder `CLAUDE.md`, all of
`src/anima_reborn/`, and `state/coupling/RESULTS.md`.

## The owner's question, verbatim

> "소통하기 위해선 어떤 게 엔진에 필요할지 발산 위임 . 텍스트, 음성 등 제한없이 개념자체를 이해"
> = *"Diverge on what the engine would need in order to COMMUNICATE. Not limited to text
> or voice — understanding the concept itself."*

Note the two halves. **Communicate** and **understand the concept itself, modality-
unrestricted.** The second is the hard one and the one to take literally.

## Where the repo actually stands (all measured, all in the README)

- `coupled.py` — a four-unit ring where each unit reads a live partner. Directed Phi 9.86
  at tau=17; the same engine wired feedforward reads exactly 0.000 and wired to itself
  0.031 (the sampling floor). Integration is bought by wiring, and that is the only claim.
- `words.py` — words as a continuing drive. On the UNCOUPLED substrate binding is
  transmitted, never created (independent inputs, excess -0.002..+0.004 over a time-shift
  null). Through the COUPLED channel it IS created: +0.078 live, +0.008 one-way, -0.000
  yoked. Real, consistent, and still far under the 0.30 emergence bar.
- `iit4/` — bit-exact port, plus `directed.py` which closes the feedforward carve-out.
- **EI is refuted as a scout**: it is not a lower bound on Phi (feedforward reads EI 1.867
  with Phi 0.000), and a system with NO coupling reads 70% of the fully integrated ring.
  So scaling past six units currently has no measure behind it.

## The wall you must engage, not walk around

The repo already proved, and documented, that **it has no semantics**:

> "이 실험은 단어의 의미에 대해 아무것도 말하지 않습니다. 표준 라이브러리에 의미를 아는
> 인코더는 없고, '관련된 단어 vs 무관한 단어' 같은 대조를 만들면 그건 제 인코더를 재는
> 것이지 기판을 재는 게 아닙니다."
> = *any related-vs-unrelated word contrast measures the ENCODER, not the substrate.*

And these were explicitly refused, with reasons, in an earlier delegated roadmap:

- **An LLM in the loop** — breaks stdlib purity, and epistemically worse: it imports
  meaning the instruments cannot measure, so every output becomes a claim about the LLM.
- **A self-report channel** — "the system says it is integrated" is a readout with a
  sentence template attached. It earns standing only if it is itself a unit inside the
  measured transition matrix.
- **A fused "aliveness"/consciousness scalar** — invented weights, cannot fail a test.
- **Phi as an optimization target** — an optimizer harvests the 0.3-bit sampling artefact.

So the question has teeth: **how could a substrate with no semantics come to grasp a
concept?** Any answer that quietly reintroduces an external meaning-source is the LLM
refusal wearing a hat. Say so when you see it, including in your own proposals.

## What I want (breadth first)

1. **At least eight genuinely distinct directions.** Not eight variations of one idea.
   For each: a name, the mechanism in two or three sentences, what it would predict, and
   the single measurement that could kill it. Rough cost. Span the space — some cheap,
   some expensive, some probably wrong but interesting.

   Seeds to react to (adopt, mutate, or kill with a reason — and go well beyond them):
   - modality-invariance as the operational definition: the same concept arriving through
     two unrelated encodings drives the substrate to the same attractor. This looks
     testable with what already exists — is it, and does it actually mean understanding?
   - grounding by consequence: a "concept" is whatever regularity lets the substrate
     predict its own next input better. Prediction error as the only teacher.
   - two coupled substrates that must coordinate with a narrow channel, where a shared
     code has to emerge because neither can solve the task alone (signalling games)
   - concepts as attractors vs concepts as transformations vs concepts as invariants
   - the substrate acting on its world and seeing what changes — intervention, not
     correlation, as the route to meaning
   - communication as compression: the channel is too narrow for raw state, so whatever
     survives is what mattered
   - time as the carrier — the crystal's lock already showed order can be temporal
   - refusing the question: maybe "understanding" is not measurable here at all, and the
     honest deliverable is a smaller thing done well

2. **The measurement problem, per direction.** This repo's whole discipline is that a
   number means nothing without the null that could fake it. For each direction, name the
   artefact most likely to make it look successful when it is not. Several directions will
   die here and that is useful.

3. **What "understanding the concept itself" could operationally mean** — give three or
   four candidate definitions, each falsifiable, each with what it would NOT establish.
   Be explicit about which are within reach of a stdlib, four-to-six-unit instrument.

4. **The honest partition.** Which directions are reachable now, which need a measure that
   does not exist yet (see the EI refutation), and which are out of reach in principle.

5. **If you had to start Monday**, which single direction and why — but only after the
   breadth above, and stated as your preference rather than the answer.

Constraints for anything you propose building: Python >= 3.11, standard library only, zero
runtime dependencies, deterministic under `seed=`, engines pure, and a new engine needs a
viewer tab in the same commit. Prototype and MEASURE where you can — your last three
designs reproduced to the decimal because they were measured, and that is the standard.
