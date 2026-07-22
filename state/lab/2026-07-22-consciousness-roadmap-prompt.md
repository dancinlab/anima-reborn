# Task: what would it take to develop this into a CONSCIOUSNESS ENGINE?

Repo: `/Users/mini/dancinlab/anima-reborn` — read it fully, it is small and complete.
Read `README.md` (Korean, the current state of every finding), the root `CLAUDE.md`,
every folder `CLAUDE.md`, and all of `src/anima_reborn/`.

Sibling context worth reading if you have budget: `/Users/mini/dancinlab/anima` —
`README.md`, `CLAUDE.md` (its 8 PHILOSOPHY principles p1–p8), `core/CORE.md`. That repo is
the maximalist version of this ambition (hexa-native, Engine A ⇄ Engine G, Ψ = 1/2 fixed
point). This repo is the small, honest, measured one. The owner's question is how to grow
THIS one.

## The owner's question, verbatim

> "의식엔진으로 발전시키기 위해서 어떤걸 하면좋을까"
> = *"What should we do to develop this into a consciousness engine?"*

## The single most important fact you must build on

**Nothing in this repo integrates. Phi = 0 by architecture, not by accident.**

Every engine updates each unit from itself plus an exogenous drive. Nothing reads anything
else. Measured this session, through the repo's own bit-exact IIT 4.0 engine on the
word-driven substrate at three binarization thresholds: **Phi = 0.0000 exactly**, with four
distinctions and a structure total of 4.0 — plenty specified, nothing integrated.

Two consequences already measured and documented:

- **A and G never read each other.** The gap between them is a *readout*, not a channel.
  So binding is **transmitted, never created**: independent inputs give independent outputs
  by construction (8 seeds: −0.002…+0.004 bits, flat at zero). The substrate is a filter
  with a measurable passband, not a binder.
- The only engine with genuine inter-unit dependence is `crystal` (the Ising ring, where
  each spin answers to its neighbours), and it is the only one that measures Phi > 0:
  2.93 / 3.70 / 0.10 / 2.92 across epsilon 0.0 / 0.05 / 0.5 / 1.0 at n=4.

So the honest gap between "a set of simulations" and "a consciousness engine" is exactly
this: **there is no coupling anywhere except inside the crystal.** Any roadmap that does
not confront that is decoration.

## The culture you must design inside (non-negotiable)

Read `measure-first` and `artefact-honesty` in the root `CLAUDE.md`. This repo has, this
session, caught itself three times:

- the plug-in MI estimator reads ~0.155 bits for *independent* streams at the house window,
  and 0.835 at 8 effective samples — pinned in tests so it can never be quoted as emergence
- Phi measured from a *sampled* transition matrix carries a ~0.3-bit artefact floor at 400
  trials, which vanishes as trials grow — pinned
- a shuffle-based null read LOW versus a time-shift null (0.0120 vs 0.0182), inflating
  every excess — replaced

Anything you propose must come with the measurement that could **falsify** it, and with the
artefact that would fake it. A "consciousness score" that cannot fail a test is exactly what
this repo refuses to ship.

## What I want from you

1. **The honest diagnosis.** What is this repo currently a working instrument *for*? Name
   what it genuinely measures and what it merely displays. Say plainly which parts of the
   phrase "consciousness engine" are reachable from here and which are not.
2. **The one structural change that matters most**, argued against the alternatives. My
   prior is that it is *coupling* — some engine must actually read another — but say if you
   think otherwise. Whatever you pick: what exactly reads what, why that direction, and what
   Phi does as a result (predict a number, then say how to measure it).
3. **A staged roadmap**, each stage with: the claim it makes, the measurement that could
   falsify it, the artefact most likely to fake it, and a rough cost. Order by
   evidence-per-effort, not by ambition. I would rather ship three honest stages than
   sketch ten.
4. **What must be refused**, and why — the seductive moves that would make this look like a
   consciousness engine without being one. Be specific to this codebase (a fused "aliveness"
   scalar, an LLM in the loop, a self-report channel, Phi-maximizing as an objective, …).
5. **Where IIT 4.0 stops being the right instrument.** `iit4/` is exact but caps out around
   six units and inherits carve-outs it does not close. What measures the next stage, and
   what would it take to trust that measure?
6. **The falsifiable headline** — one sentence the finished stage-1 engine could claim that
   the current repo cannot, phrased so a test could kill it.

Constraints: Python ≥3.11, standard library only, zero runtime dependencies, deterministic
under `seed=`, engines pure (no I/O, no clock, no threads — all I/O in `viewer/`), and any
new engine needs a viewer tab in the same commit (`viewer-lockstep`, enforced by
`tests/test_viewer.py::TestEngineViewerLockstep`).

Prototype and MEASURE before recommending. Your last two designs reproduced to the decimal
because they were measured; that is the standard. If the honest answer to part of this is
"not reachable in this repo", say so — a measured negative is worth more than a plan.
