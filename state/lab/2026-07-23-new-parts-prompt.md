# Design task: the additional engine components needed to advance the goal, past the proven walls

The owner of `anima-reborn` (a Python research repo whose culture is: every capability earned
by measurement with its null, never overclaimed) has walked a line — human<->engine
communication -> conversation -> "real English conversation" -> we PROVED English is impossible
on this substrate (≤3 measurable-integrated bits; data-processing inequality
I(X;Y) ≤ I(C;C') ≤ H(C) ≤ 3). The owner now says: **"목표 달성위한 엔진 추가 부품 설계" — design
the ADDITIONAL engine components needed to achieve the goal.**

The goal is genuine, richer human<->engine communication — as far toward it as the physics
honestly allows. The additional parts must PUSH THE REAL FRONTIER (the walls below), not paper
over them with labels. Return a concrete architecture design + a phased build plan. Do NOT write
full code.

## The proven walls you must respect (theorems + measurements in this repo — do not violate them)

1. **The ring holds exactly 1 bit.** THEOREM: each unit's response is odd, decreasing, bounded
   (a `tanh` of a scaled partner), so no orbit longer than 2; a closed ring of ANY even width
   has exactly two consistent sign assignments. Widening a single ring buys nothing.
2. **Capacity lives in the wiring's CYCLE structure.** `Wiring.PAIRS` = units/2 cross-coupled
   latches holds units/2 bits, addressed only through each pair's DIFFERENTIAL mode d[2j]-d[2j+1]
   (the common mode dies in silence). It stays INTEGRATED only for an ODD number of pairs (even
   pairs form a macro-ring that locks).
3. **The integration measure Φ is UNMEASURABLE past ~6 units.** Directed Φ (`substrate.py`, exact
   IIT in `iit4/`) enumerates bipartitions / state space 2^units, so it becomes intractable past
   ~6 units, AND `RECURRENCE_FLOOR` was calibrated at 4 units and does NOT transfer (the estimator
   artefact grows with width, so past 6 units the verdict is "held under 4x sampling", never the
   magnitude). So the ceiling on CARRYING more bits is not the bottleneck — the ceiling on SHOWING
   they are held as ONE integrated thing is.
4. **What the substrate has earned** (all measured, with nulls): holds 1 bit through silence
   (`silence.py`), USES the held bit (delayed match-to-sample, `match.py`), carries a
   co-occurrence-learned concept across modalities (`align.py`, 86% survives), and — the English
   proof — carries exactly 3 bits of a real sentence's choice, object unrepresentable.

## The existing components (what you are adding TO)

- `coupled.py`: `CoupledEngine` — units, `Wiring` (RING/PAIRS/FEEDFORWARD/SELF), `Rhythm`
  (ALTERNATING vs FIXED — listen vs integrate in time), per-unit `drive`, `chain` (weak inter-pair
  coupling that makes odd pairs integrate). Unit update: tanh-of-partner, simultaneous, seeded WALK
  noise. This is where new dynamics/wirings would live.
- `align.py`: the only LEARNER (co-occurrence pulls two modalities to a midpoint + a unit-direction
  contrast push; scored only on held-out concepts; reports effective rank).
- `substrate.py` + `iit4/`: drive an engine from every state -> measured TPM -> directed Φ.
- `dialogue.py`/`conversation.py`: the human-facing 1-bit and 3-bit games + blind audits.

## The candidate directions to evaluate (address each, then recommend a phased plan)

A. **Time-accumulation / sequence memory.** The substrate holds ~3 bits per moment; a component
   that CHAINS held states across turns (like `silence.py`'s deaf-hold, but writable/readable in
   sequence) could accumulate k bits/turn × T turns of MEANING without wider units — composition
   in TIME, the repo's recurring escape (order carried in time, not space). What new engine part?
   How is capacity-over-time MEASURED (and what is the forgetting null)?

B. **Multistable units (more bits per unit).** The 1-bit theorem hinges on the odd-decreasing
   bounded response giving a 2-cycle. A unit with k>2 stable states (a different nonlinearity —
   e.g. a periodic or multi-well response) would hold log2(k) bits per unit. Is this consistent
   with staying integrated and measurable? What is the new unit dynamics, and does the Φ machinery
   still apply? Danger: a hand-tuned multi-well is the designer planting basins (the D7 death —
   `attractor_canonicalization.py` — where planting basins = the designer choosing the categories).

C. **A scalable integration MEASURE.** The wall is Φ-UNMEASURABILITY past 6 units, not zero
   integration. A new measurement component — a sampled/approximate directed-Φ or a
   partition-information proxy VALIDATED against exact `iit4` Φ on small systems — would let WIDER
   integrated substrates be SHOWN integrated, directly raising the measurable ceiling. What proxy,
   validated how, with what artefact control (it must match exact Φ where both are computable, and
   its bias must shrink with samples)?

D. **Hierarchy / modular composition.** Several 3-bit integrated modules with a measured
   inter-module binding (a slow chain), so the whole holds more while each part is measurable.
   Does the odd-pairs / macro-ring-lock constraint permit a measurable hierarchy? What binds the
   modules, and what is the null that the whole does something the parts cannot (the cross-pair
   response test from `concepts.py`)?

E. Anything else that is the TRUE highest-leverage part — name it.

## What I need — answer each explicitly

1. **Which wall is the true bottleneck to the goal** — raw capacity, integration-MEASURABILITY,
   time-accumulation, or composition — and therefore which component to build FIRST. One-line
   dissent if you'd order it differently.
2. **The concrete new component(s)**: what is added to which module, the new dynamics/wiring/measure,
   how it stays stdlib-pure and seedable, and CRUCIALLY the measurement that proves it works and the
   NULL that could fake it (a new capability with no control is not earned here).
3. **`default-stays-exact`**: any new engine parameter must default to leaving every published
   number BIT-identical, pinned by a test. State how.
4. **The overclaim trap for THIS part** — how a naive version fakes success (e.g. planted basins,
   an estimator artefact that grows with width, capacity that collapses to rank 1) and the control
   that kills it.
5. **The phased plan**: the smallest first component that measurably moves the frontier, what it
   unlocks, and what each later part depends on. What is the honest ceiling even if all of it works
   (is it "more bits", or actually closer to language)?

Keep the discipline: never a number that was not measured; every capability shipped with the null
that could fake it; report effective rank/width beside any capacity; respect the ring and
odd-pairs theorems; the engine is not language. If a direction is a dead end by the existing
theorems, say so and prune it.
