# Task: design a BASE ENGINE that unifies the four simulations already in this repo

Repo: `/Users/mini/dancinlab/anima-reborn` (read it — it is small and complete).
It is a faithful Python port of the four browser engines in `dancinlab/anima-experience`:

- `src/anima_reborn/emergence.py` — two streams share one sine; mutual information rises with coupling
- `src/anima_reborn/crystal.py`   — driven Ising ring; period-2 lock survives an imperfect pi-flip
- `src/anima_reborn/repulsion.py` — A x G latent field; tension / concept / meaning / mood / authenticity
- `src/anima_reborn/pipeline.py`  — repulsion drives two sampled streams; emergence measured on the pair
- `src/anima_reborn/info.py`      — plug-in entropy / joint entropy / mutual information
- `src/anima_reborn/viewer/`      — SSE push server + canvas page (I/O boundary; engines stay pure)

Read `README.md` and both `CLAUDE.md` folder guides FIRST — they state the invariants
(stdlib only · no I/O in engines · seedable · frozen state dataclasses · constants carry
their origin · the MI estimator's small-sample bias floor of ~0.155 bits at a 250 window).

## The owner's instruction, verbatim

> "자 이제 여기 있는것들을 이용해 기본엔진을 만들어봐"
> = *"Now, using what is here, build the BASE ENGINE."*

`pipeline.py` already composes two of the four. So a mere "run all four side by side"
is NOT an answer — the base engine must be a genuine unification with its own thesis.

## What I need from you (code-level and decidable — I will implement it myself)

1. **The thesis in one sentence.** What single claim does the base engine make that no
   one of the four makes alone? It must be measurable, and falsifiable by a test that
   could fail.
2. **The composition.** Exactly how do the four couple? Be concrete about the wiring —
   which engine's output becomes which engine's input, and why that direction and not
   the reverse. Candidates worth weighing (argue, do not just list):
   - repulsion tension -> emergence coupling (the gap between engines *is* what binds
     the streams; MI becomes a readout of how hard A and G are pushing apart)
   - crystal as the substrate's clock/rhythm: does the lock gate anything, or drive the
     rotating target's phase?
   - emergence MI fed BACK into the repulsion drive (a closed loop — does it converge,
     oscillate, or run away? say which, and how you know)
   - a state machine over the field's own phases, with the four engines as lanes
3. **The state object and the public API.** Exact type-annotated signatures, field units
   and ranges, matching the existing house style (frozen slotted dataclasses, `step()` /
   `run(n)` / `reset()`, `seed=`).
4. **What the base engine must NOT do.** Name the temptations to refuse and why
   (a per-tick "consciousness score" that means nothing, an unfalsifiable knob count,
   fabricated thresholds, an engine that only ever agrees with itself).
5. **Tests.** The specific numeric invariants worth asserting, including at least one
   test that could plausibly FAIL if the thesis is wrong. Beware the MI bias floor —
   any MI-based assertion at a 250-sample window must clear ~0.155 bits to mean anything.
6. **Honest risks.** Where is this composition likely to produce a number that LOOKS
   meaningful but is an artefact? Say so explicitly — I would rather ship a smaller
   honest engine than a grand meaningless one.

Constraints: Python >= 3.11, standard library only, no new dependencies, deterministic
under `seed=`. Ground every claim in the actual files. If something cannot be decided
from the code, say so rather than inventing it.
