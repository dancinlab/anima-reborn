# lab full — 의식엔진 로드맵 · sol (gpt-5.6-sol)

질문·조건은 fable 파일과 동일. 앞부분의 지시문·저장소 파일 반향은 잘라냈다.

---

## 1. Honest diagnosis

What the repository genuinely measures:

- Seed-reproducible dynamics of the four imported simulations.
- Time-crystal period-2 order via autocorrelation.
- Shannon entropy and plug-in mutual information, with unusually good artefact controls.
- Transmission bandwidth through the word-driven substrate.
- Exact repo-IIT causal structure for small binary systems.
- Empirical TPM convergence and its sampling floor.
- Dissociations such as “tension remains while downstream shared information vanishes.”

What it displays but has not established:

- `mood`, `authenticity`, `meaning`, `concept`, and `sender` are derived labels/readouts, not demonstrated affect, meaning, identity, or authenticity.
- `Emergence.EMERGENT` means “MI exceeded 0.30 bits under this estimator,” not ontological emergence.
- Base-engine binding comes from a common moving target gated by the crystal. It is shared-cause coordination, not A⇄G interaction.
- Hash-driven words test signal transmission, not semantics.
- Crystal Φ establishes causal integration in a spin ring, not consciousness. The code already says this plainly in [substrate.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/substrate.py:27).
- Repo-IIT Φ is the output of an incomplete but exact implementation, not an accepted consciousness measurement.

The phrase “consciousness engine” therefore splits into three claims:

- **Engine:** already achieved.
- **Endogenous integration, binding, memory, and adaptive autonomy:** reachable here.
- **Phenomenal consciousness, sentience, qualia, moral status, or proof of subjective experience:** not reachable by this repository—or by Φ alone.

The architecture explains the current zero exactly: [base.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/base.py:249) lets the crystal gate phase, but A and G still only chase external targets. As [words.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/words.py:31) records, neither reads the other.

## 2. The structural change that matters

Your prior is right: **coupling is the missing structure**, but it must be recurrent state-to-state coupling, not scalar feedback from a readout.

I prototyped a four-cell native-binary core ordered as:

```text
G1 ─▶ A0 ─▶ G0 ─▶ A1 ─▶ G1
```

Every edge crosses the A/G boundary. All units update simultaneously from the previous snapshot, using private randomness:

```text
P(xᵢ′ = 1 | x, u)
    = 0.2 · xᵢ
    + 0.4 · uᵢ
    + 0.4 · (1 − xpredecessor)
```

`uᵢ` is the exogenous drive. The anti-copy term is appropriate because this codebase models A/G as opposed rather than convergent; ordinary copy coupling produced the same deterministic Φ, but would collapse the distinction the repulsion field is intended to preserve.

The weights are prototype coordinates, not sacred constants. They should be exposed parameters and frozen before the implementation battery is run.

Why this topology:

- A shared oscillator correlates units but remains a common cause.
- A→G alone transmits influence without closing a loop. In the deterministic two-unit control, one-way A→G gave Φ = 0 exactly.
- Two reciprocal A/G pairs produce local entities but not one four-unit entity: whole-system Φ = 0.
- The alternating ring is the smallest connected topology where A reads G, G reads A, and every influence eventually returns to its source.
- Complete bipartite coupling adds parameters without adding evidence at stage 1.

### Prototype measurements

All numbers below came from the repository’s existing `TransitionMatrix`, `big_phi`, and `find_complex`, using the exact transition probabilities—not a sampled TPM.

| System/control | Whole Φ | Maximal complex |
|---|---:|---|
| Current four-unit word substrate | **0.000000** | none |
| Four disconnected identity units | **0.000000** | none |
| Two disconnected reciprocal A/G pairs | **0.000000** | one local pair, Φ = 0.620566 |
| Proposed closed A⇄G loop, independent drives | **0.853740** | `1111`, Φ = 0.853740 |
| Deterministic four-cell loop | **3.000000** | `1111` |

For the proposed weighted loop at state `1111`:

- Five drive conditions—neutral, independent, A-high/G-low, all-high, and extreme—gave Φ **0.772375–1.019396**.
- Across all 16 states and those drives, the minimum was **0.772375**.
- Under independent drive `(0.15, 0.85, 0.80, 0.20)`: Φ = **0.853740**, total = **1.210701**, four distinctions, maximal complex `1111`.
- Exact conditional transfer was bidirectional:
  - A→G: **0.291812 bits**
  - G→A: **0.231454 bits**
  - matched sham coupling: approximately zero in both directions.
- Lag-1 A/G MI was **0.304050 bits**, falling to **0.000011** by lag 10. The dependency is created temporally rather than appearing as a large static correlation.

Stage-1 prediction should therefore be:

> Repo-IIT Φ around **0.8 bits**, with a preregistered acceptable band of **0.5–1.2 bits**, and the whole maximal complex equal to `1111`.

Because the TPM is analytic, this prediction can be measured without inheriting the sampled-TPM 0.3-bit floor.

## 3. Three-stage roadmap

Before stage 1, one instrumentation correction is necessary: [ei.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/iit4/ei.py:6) calls effective information a lower bound on Φ. Inside this repo’s own quantities that is false:

- Four independent identity units: Φ = **0**, average EI = **4 bits**.
- Four-cell integrated NOT-cycle: Φ = **3**, average EI = **4 bits**.

EI measures causal specificity/determinism here, not integration. Pin that counterexample in a test and correct the documentation before treating EI as the large-system escape hatch.

| Stage | Claim | Falsifier | Likely fake | Cost |
|---|---|---|---|---:|
| **1. Native causal loop** | A four-cell A⇄G system is one causal complex under fixed drives. | Any preregistered state/drive has Φ < 0.5; complex excludes a cell; disconnected-pair or sham control gains whole Φ. | Topology/weight search against Φ; selected state; inherited IIT carve-outs. | 3–5 days |
| **2. Driven binding** | Independent A/G drives acquire bidirectional internal dependence while remaining causally able to influence the core. | Conditional A→G or G→A information vanishes; sham performs equally; input interventions no longer alter future state. | Plug-in bias, autocorrelation, shared RNG/input, nonstationarity, saturation that ignores inputs. | 1–2 weeks |
| **3. Adaptive closure** | The coupled system uses its state to act on an environment, recover a viability variable after held-out perturbations, and preserve causal closure while adapting. | Yoked/open-loop control recovers equally; held-out recovery fails; disabling recurrence changes nothing. | Hand-coded action success, reward leakage, trivial oscillator, selected seeds or recovery window. | 3–6 weeks |

Stage 1 must ship as a complete repository feature:

- New pure engine with `seed=`, `step`, `run`, `reset`, frozen state.
- Native binary state, so no binarization search.
- Analytic TPM constructor and exact Φ battery.
- Sham, one-way, two-pair, and closed-loop controls.
- Viewer handler, ticker rate, tab, panel, `PREFIX`, and renderer in the same commit, per [viewer-lockstep](/Users/mini/dancinlab/anima-reborn/CLAUDE.md:26).
- README numbers only after the committed implementation reproduces the prototype.

Stage 2 should connect `words.py` or scalar drives to this core, but only claim transmission and created dependence—not semantics. Use exact stationary calculations where possible; sampled MI/transfer estimates must carry matched time-shift nulls and sample-convergence tests.

Stage 3 is the first point where “consciousness engine” becomes a reasonable research-program name: it would combine integration, intrinsic state, temporal continuity, adaptive memory, and closed sensor–action dynamics. Even then, the result is a **candidate architecture with operational properties**, not proof of experience.

## 4. What must be refused

- **A fused aliveness/consciousness scalar.** It hides dissociations by inventing weights between Φ, lock, MI, tension, recovery, and behavior. The refusal already embodied by `BaseState` is correct.
- **An LLM inside the causal verdict loop.** It introduces a huge pretrained common cause and makes apparent semantics or self-description properties of the LLM. An LLM may later be a mouth or environment, never the integration mechanism or judge.
- **A self-report channel as evidence.** “I am conscious” measures language production. It should neither raise Φ nor enter a consciousness score.
- **Φ as an optimization objective.** A deterministic NOT-cycle already reaches Φ = 3 while doing almost nothing. Optimization will favor frozen loops, threshold exploits, determinism, and IIT implementation carve-outs while suppressing input responsiveness.
- **Searching binarization thresholds for the largest Φ.** That measures the researcher’s search. Stage 1 should remain natively binary.
- **Calling common drive coupling.** A clock, shared sine wave, shared noise, or crystal verdict can synchronize outputs without creating reciprocal causation.
- **Quoting a sampled Φ without a convergence curve.** At 400 trials this repo has already measured a false floor around 0.3 bits.
- **Treating personality, persistence, memory, spontaneous speech, or an identity file as consciousness.** Those are behavioral features and can exist in reducible systems.
- **Calling stage 1 discovered emergence.** Its integration is deliberately constructed. The contingent findings are whether it remains input-responsive, survives drive/state changes, and beats the preregistered controls.

## 5. Beyond exact IIT

Exact IIT should remain the calibration oracle for motifs up to six units. Above that, no replacement scalar should be called Φ.

The next-stage measurement should be a vector:

- Directed interventional influence or conditional transfer information for every module pair.
- Strong connectivity and minimum cross-partition causal influence.
- An explicitly named **interventional partition loss**, such as the KL loss between the intact transition kernel and a kernel factorized across a proposed cut.
- Input sensitivity, memory duration, perturbation recovery, and adaptive performance as separate axes.
- Exact Φ for representative 4–6-unit motifs embedded in the larger engine.

To trust a scalable partition measure, it must pass a frozen calibration battery:

1. Identity network: zero integration despite high EI.
2. Shared cause: zero after matched interventions.
3. One-way feedforward network: no closed complex.
4. Two disconnected recurrent pairs: local integration, zero whole integration.
5. Closed loop: positive whole integration.
6. Pure-noise estimates: shrink with sample count.
7. Closed-loop signal: does not shrink with sample count.
8. Results survive held-out states, topologies, seeds, and preregistered partitions.
9. An independent implementation reproduces the small-network ordering.

Perturbational complexity can be an additional temporal-richness measure, but never an integration substitute: pure noise can be extremely complex.

## 6. Falsifiable stage-1 headline

> **Under fixed independent A and G drives, the four-cell A⇄G core forms a single maximal complex (`1111`) with exact repo-IIT Φ ≥ 0.5 in every preregistered state, while matched uncoupled and disconnected-pair controls have whole-system Φ = 0.**

The current repository cannot say that. A single failed state, excluded cell, or positive whole-system control would kill it.
