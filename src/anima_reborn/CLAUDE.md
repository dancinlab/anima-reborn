# src/anima_reborn/ — the engines

Headless Python ports of the four browser engines in
[`dancinlab/anima-experience`](https://github.com/dancinlab/anima-experience) `index.html`.
Rendering, timers and DOM wiring stay in the origin; only the maths lives here.

## Files

| file | engine | origin |
| --- | --- | --- |
| `info.py` | entropy · joint entropy · mutual information · `Binning` | `bin` / `entropy` / `jointEntropy` |
| `emergence.py` | two streams sharing one oscillator | emergence tab |
| `crystal.py` | driven Ising ring, period-2 lock | DTC tab (`dtc_demo.py`) |
| `repulsion.py` | A × G latent field | A × G tab (moods from `tension_link.py`) |
| `pipeline.py` | repulsion → sampled streams → emergence | pipeline tab |
| `base.py` | all four under the crystal's clock — rotation only while LOCKED | (new — not in the origin) |
| `coupled.py` | A and G reading each other — the only engine here with nonzero integration, and `Rhythm`, which is when they do | (new — not in the origin) |
| `align.py` | the only module that LEARNS — co-occurrence teaches two modalities to meet | (new — not in the origin) |
| `substrate.py` | drive an engine from every state → measured TPM → Phi | (new — not in the origin) |
| `words.py` | words as a continuing drive, always paired with a null control | (new — not in the origin) |

`pipeline.py` imports `PHASE_RATE` / `PULL` / `DAMPING` from `repulsion.py` — the two
engines share one drift law, and it is defined once.

`coupled.py` is where the repo stops being a set of driven simulations. Everywhere else a
unit reads itself and something exogenous, which is why Phi is zero by architecture; there
the source is a live partner. Its falsifiers ship as part of its API (`Wiring.FEEDFORWARD`,
`Wiring.SELF`) rather than living only in tests — the claim is that the wiring is what
produces the integration, and that is only checkable if the other wirings are reachable.

`Rhythm` is the same module's second claim and its harder one. Add a `drive` and a wall
appears: on a fixed coupling, integration and representation trade off monotonically and
no value holds both — at full coupling the drive is not weak but *unreachable*, bit for
bit. A rhythm meets the two demands at different times instead of the same one, and beats
the control that matters (a fixed coupling at the rhythm's own time average). Two rules
follow. Measure a rhythm over a WHOLE listen/integrate cycle — `Rhythm.macro_step`, which
`substrate` defaults to — since half a cycle reports one phase's transition matrix and
labels it the engine's. And keep `Rhythm()` bit-exact with the pre-rhythm engine, because
every Phi already published was measured on it.

`align.py` is the only module that changes with experience, and it earns that by
measurement rather than ambition: dynamics alone cannot canonicalize, because the evidence
that two signals are one concept must be IN the signals and co-occurrence is what puts it
there. Its falsifier (`shuffled=True`) is public API for the same reason the wirings are.
Two rules it must keep — score only on held-out concepts, and report the gain over the
learner's OWN untrained baseline, which is not zero. A third arrived with `contrast`:
report how many effective dimensions the learned space uses, because pulling toward a
midpoint narrows it (1.21 of four, below the raw signals' 1.93) and a narrow space scores
well while carrying little. The push that fixes it must be by the unit direction and must
stop at a distance; by the raw displacement it runs away to rank 1.00, which is worse
than the contraction. `observe(..., sample=n)` draws a
fresh noise realization of the same concept; a consumer that repeats a noisy process on
one fixed observation is measuring that process's noise and scoring an exemplar.

The two are connected: `CoupledEngine(drive=...)` takes a per-unit vector, so an aligned
representation arrives as itself rather than as its average, and
`state/communication/aligned_drive.py` measures whether concept identity survives the
engine — 81% of it does with the midpoint rule alone, 86% with the push on. Measure the
drive BEFORE the engine every time: the engine can only lose information, so a trajectory
score alone cannot be attributed to it, and the deaf arm (coupling 1.0, drive
bit-unreachable) is what proves the engine was in the path at all.

Made deaf AFTER being told, the ring keeps its state forever while every acyclic wiring
falls to a fixed point — the first capability in this repo that recurrence buys rather
than merely exhibits (`state/communication/silence.py`). It is exactly one bit: four sign
inversions round the cycle make the loop's net sign positive, so the autonomous ring is
bistable, and that is a derivation the measurement then confirmed.

"Uses" is now earned too, and only just: loaded then probed, the ring's own response
depends on whether the probe agrees with what it holds — 0.729 against a ceiling of
0.758 that one bit allows, on 8/8 seeds, while every arm holding nothing is pinned at
0.500 by construction (`state/communication/match.py`). A score near 1.0 there would be
a bug, not a better result. The bound is topological, not a matter of size: a single ring of ANY even width holds
exactly one bit (a theorem — the response is odd, decreasing, bounded, so no orbit longer
than two), so widening it buys nothing. Capacity lives in the wiring's cycle structure, so
`Wiring.PAIRS` (units/2 latches) with a weak inter-pair `chain` holds units/2 bits AND
measures as integrated — 6 units, 3 bits, directed Phi held under 4x sampling where the
disjoint null collapses. Two rules it forces: `RECURRENCE_FLOOR` was calibrated at four
units and does NOT transfer (the artefact grows with width, so the decay test is the
verdict past six, never the magnitude), and the chain only integrates for an ODD number of
pairs — an even number forms a macro-ring that locks. `state/communication/capacity.py`.

`base.py` is the one module here that is **not** a port: it composes the four under a
single mortal clock. Its thesis, its measured constant `EPSILON`, and the line between
what it designs in and what it discovers are all stated in its docstring — keep them
there and keep them honest. `iit4/` has its own guide.

`viewer/` is the browser view of all five, and the one place in this package that does
I/O. The rules below apply to the engine files here, not to it — see its own guide.

## Adding or changing an engine — the viewer moves with it

An engine nobody can watch rots: the crystal sat wired to nothing for a while and it took
a question to notice. So a viewer change ships in the **same commit** as the engine change,
and it is enforced rather than remembered.

New engine:

1. `viewer/server.py` — a handler class with `configure` / `describe`, an entry in
   `_HANDLERS`, an instance in `Viewer.__init__`, a `TICK_RATES` rate.
2. `viewer/page.html` — a tab button, a panel, a `PREFIX` entry, and a `render<Name>()`
   function. Korean UI text (`ui-language` in the repo root guide).
3. Restart the viewer. `page.html` is re-read per request; `server.py` is not.

Changed readout: update `describe()` **and** the panel that draws it, together.

`tests/test_viewer.py::TestEngineViewerLockstep` fails on any of: an engine with no route,
a route with no engine, a missing tick rate, a missing tab or panel, a missing render
function, or a default tab that disagrees with `let active`. "Engine" is detected
structurally — any class in a top-level module with both `step` and `reset` — so a new one
is caught the day it lands, without anyone updating a list.

## Rules for changes here

- **Standard library only.** No numpy, no torch. If a change seems to need one, it
  belongs in a consumer, not in an engine.
- **No I/O, no clock, no threads.** Everything an engine needs arrives as an argument.
  Wall-clock time enters exactly once, through `RepulsionField`'s injectable `clock`.
- **Seedable.** Every stochastic engine takes `seed=` and owns a private
  `random.Random`. Never call the module-level `random` functions.
- **Immutable readings.** State objects are frozen slotted dataclasses, so a reading can
  be compared and stored. Engines are mutable; what they return is not.
- **Constants carry their origin.** A numeric literal that came from the origin is named,
  module-level, and documented with where it came from. Do not inline it.
- **Do not invent.** If the origin's behaviour is unclear, say so in the docstring rather
  than guessing. Deliberate departures from the origin are listed in the README.

## The estimator caveat

`info.py` is the plain plug-in estimator, matching the origin — no bias correction. On
the default 250-sample window it reports ~0.155 bits for genuinely independent streams.
That floor is pinned by `tests/test_emergence.py`; if you touch the estimator or the
default window, expect those tests to fail and update them deliberately, never by
loosening the bound.
