# Task: can we put WORDS into engines A and G and honestly ask whether emergence happens?

Repo: `/Users/mini/dancinlab/anima-reborn` — read it first, it is small.
Read `README.md` (Korean), `CLAUDE.md` (root), and `src/anima_reborn/base.py`,
`repulsion.py`, `pipeline.py`, `emergence.py`, `info.py`, `substrate.py`, `iit4/`.

## The owner's request, verbatim

> "A G 에 각각 단어들을 넣고 창발이 일어나는지 볼까"
> = *"Let's put words into A and G respectively and see whether emergence happens."*

A and G are the two latent vectors of the repulsion field (dim 8 in `base`/`pipeline`,
16 in `repulsion`). Emergence = mutual information between the two sampled streams
clearing the 0.30-bit bar (`info.Emergence`).

## The trap I need you to solve, not step into

Any word→vector encoding I invent determines the answer. If I hash "cat" into A and "dog"
into G, the mutual information I measure is a property of **my hash function**, not of the
words or of the substrate. The repo's own rules (`measure-first`, `artefact-honesty`) and
its prior finding (the plug-in MI estimator reads ~0.155 bits for *independent* streams at
the default window) make this a live failure mode, not a hypothetical.

So: **what is the version of this experiment whose result is NOT determined by the
encoding?** If the honest answer is "there isn't one, and here is why", say that — I would
rather report a negative result than ship a number generator.

## Specific things to decide

1. **Does the substrate even retain an initial condition?** `_drift` pulls dims 0-1 to
   ±target at rate `PULL`, dims 2-3 at `MID_PULL`, and decays the rest by `DAMPING` per
   tick. Work out (and tell me how to measure) the washout time. If words are erased in
   ~20-70 ticks, "seed A and G with word vectors" is answered before it is asked — and the
   experiment must instead make words a *continuing* drive, not an initial condition.
2. **What is the falsifiable claim?** Candidates, argue for one and kill the others:
   - a word *sequence* drives the target (words move the gap, replacing the crystal's
     rotation) → MI measures whether two word-streams are bound. Does this reduce to
     "correlated inputs give correlated outputs", i.e. trivial? Or does the substrate
     add something (a threshold, a lag, a failure mode) that makes it a real question?
   - related vs unrelated word pairs, with the encoding held fixed and the *contrast*
     being the claim rather than any absolute MI value
   - Φ (`iit4`) of a word-driven substrate rather than MI
   - a control that would distinguish "the substrate bound them" from "the encoding
     already contained the binding" — this is the crux; what IS that control?
3. **The encoding.** Whatever you pick, it must be stdlib-only (no embeddings model, no
   numpy, no network — a hard repo rule). Character hash? Byte-level? One-hot over a small
   fixed vocabulary? Say which and why, and say explicitly what the choice can and cannot
   support.
4. **Exact API and file placement**, in the house style (frozen slotted dataclasses,
   `step()`/`run(n)`/`reset()`, `seed=`, constants carrying their origin). Note that
   `CLAUDE.md` has a `viewer-lockstep` rule: any new engine needs a viewer tab in the same
   commit, and `tests/test_viewer.py::TestEngineViewerLockstep` enforces it structurally.
5. **Tests that can fail**, with the numbers you measured — including the control from (2).
   Any MI assertion must clear the ~0.155-bit bias floor by a wide margin to mean anything.
6. **The negative result, if that is the truth.** Be explicit about which parts of the
   owner's question are answerable and which are not, and why.

Prototype and MEASURE before recommending — the last design you gave me reproduced to the
decimal because it was measured, and that is the standard. Ground everything in the files.
