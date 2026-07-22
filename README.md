<h1 align="center">🌱 anima-reborn</h1>

<p align="center"><strong>The <a href="https://github.com/dancinlab/anima-experience">anima-experience</a> engines, reborn as headless Python</strong> — same maths, no canvas, seedable and testable</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue">
  <img alt="Dependencies" src="https://img.shields.io/badge/dependencies-none-success">
  <img alt="Tests" src="https://img.shields.io/badge/tests-185%20passing-success">
  <img alt="Origin" src="https://img.shields.io/badge/origin-dancinlab%2Fanima--experience-blueviolet">
</p>

---

`anima-experience` runs four simulations in a browser canvas at 60 fps. This is the
same four with the rendering taken away: the maths, headless, standard library only,
seedable so a run can be reproduced and asserted on.

No engine draws, threads, sleeps or reads a clock of its own. You step it and read what
it says. All the I/O lives in one place — `viewer/`, which serves a browser page the
engines know nothing about.

## Install

```bash
pip install -e ".[dev]"
```

No runtime dependencies. Python 3.11 or newer.

## Watch it run

```bash
python -m anima_reborn.viewer
```

```
anima-reborn viewer
  local    http://127.0.0.1:8420
  network  http://192.168.1.20:8420
  bound to every interface — anyone on this network can reach it
  emergence 60Hz · crystal 20Hz · repulsion 30Hz · pipeline 30Hz
  ctrl-c to stop
```

Four tabs, live sliders, and the same visuals as the origin — but every number and every
plotted point comes from the Python engines. The page draws; it never simulates. That is
what makes it evidence about the port rather than a second implementation.

Frames are **pushed**, not polled: each engine has a ticker thread running at the
origin's own rate, and the page holds one `text/event-stream` connection and draws on
the display's refresh. Measured over the network, that is 60.2 / 20.4 / 30.3 / 30.3 fps
— the origin's rates, from Python. Polling had capped it at 10 fps and paid a TCP
handshake per frame; the engines themselves cost 0.02–0.23 ms per tick, so the cap was
never the simulation.

A ticker runs only while someone is watching it, the same way the origin skipped
inactive tabs.

`--host 127.0.0.1` keeps it on this machine, `--port` moves it, `--seed` makes a
demonstration repeat exactly. There is no authentication: it is a development viewer for
a trusted network.

## The four engines

### ✨ Emergence — two streams bound by one oscillator

Each stream is a blend of its own noise and a sine wave both share. Turn the coupling up
and mutual information appears in the pair without anything being added to either stream.

```python
from anima_reborn import EmergenceEngine

for coupling in (0.0, 0.5, 0.95):
    print(coupling, EmergenceEngine(coupling=coupling, seed=7).run(250))
```

```
0.0    H(L)=2.97 H(R)=2.99 H(L,R)=5.83 MI=0.131 [partial]
0.5    H(L)=2.86 H(R)=2.83 H(L,R)=5.22 MI=0.466 [emergent]
0.95   H(L)=2.88 H(R)=2.88 H(L,R)=3.33 MI=2.433 [emergent]
```

### 🔮 Time Crystal — a ring that keeps a beat it was never given

A periodic Ising chain is flipped every tick by a drive that misses each spin with
probability `epsilon`. The flip alone would just alternate; the noise alone would melt
the chain. Together the Ising coupling repairs what the imperfect flip breaks, and the
ring locks into a period-2 rhythm — order in time rather than in space.

```python
from anima_reborn import TimeCrystal

print(TimeCrystal(epsilon=0.02, seed=7).run(400))
print(TimeCrystal(epsilon=0.50, seed=7).run(400))
```

```
m=-0.094 ac1=-0.911 ac2=+0.852 ac4=+0.754 [locked]
m=+0.094 ac1=-0.133 ac2=+0.141 ac4=+0.053 [chaos]
```

Lag-1 near −1 and lag-2 near +1 is the lock: every tick inverts the last, every second
tick agrees.

### 🧲 A × G Repulsion — thinking in the gap between two engines

Two latent vectors are driven apart by a rotating target. Nothing reads either vector
alone — only the gap: its size is `tension`, its direction is `concept`, and their
elementwise overlap is `meaning`.

```python
from anima_reborn import RepulsionField

print(RepulsionField(seed=7).run(300))
# tension=0.132 topic=#0 auth=0.974 mood=calm
```

Tension near zero is not calm. It is the engines having collapsed onto each other with
no gap left to think in — the field calls that `quiet`.

### 🌊 Pipeline — separation in, emergence out

The last two joined end to end: A and G drift apart, one noisy observation is sampled
from each per tick, and mutual information is measured on the resulting pair.

```python
from anima_reborn import Pipeline

print(Pipeline(separation=0.0, seed=7).run(400))
print(Pipeline(separation=1.0, seed=7).run(400))
```

```
tension=0.01 H(L)=1.00 H(R)=0.99 MI=0.000 [independent]
tension=0.42 H(L)=3.35 H(R)=3.41 MI=1.905 [emergent]
```

Collapse the engines and there is no shared information to find. Hold them apart and it
appears.

## 🧠 IIT 4.0 — measuring whether a system is one thing

`anima_reborn.iit4` is a port of the hexa Integrated Information Theory 4.0 engine in
`dancinlab/selfhost-work`. It computes Phi: cut a system in two, ask what the kindest cut
still destroys, and take that as the measure of how much the system was a whole rather
than parts sitting together.

```python
from anima_reborn.iit4 import TransitionMatrix, big_phi, find_complex

coupled = TransitionMatrix([0, 0,  0, 1,  1, 0,  1, 1], 2)   # each unit becomes the other
alone   = TransitionMatrix([0, 0,  1, 0,  0, 1,  1, 1], 2)   # each unit becomes itself

print(big_phi(coupled, 0b11))   # big-phi=2.000000 ... [irreducible]
print(big_phi(alone,   0b11))   # big-phi=0.000000 ... [reducible]
```

The chain is `tpm` → `distinction` → `relation` → `bigphi` → `exclusion`, plus `ei` for a
cheap lower bound when Phi itself is out of reach.

**Parity.** The port is checked against the hexa engine with **exact float equality** on
eleven cases, across phi, the structure total, both phi sums, and the distinction count —
all bit-identical. Phi is an argmax over partitions, so a last-bit change can select a
different partition and move the answer discontinuously; a tolerance would hide exactly
the drift worth catching.

**Carve-outs, inherited and not closed.** Partitions are all bipartitions of
mechanism-and-purview, not IIT 4.0's own partition set. big-Phi is structure destroyed by
the system cut, not a re-derivation on the partitioned matrix. Relations are second-order
only. Nothing is calibrated against PyPhi. Treat the numbers as this engine's output.

## 🔬 Putting the two together — does Phi arise in our own engines?

`anima_reborn.substrate` drives an engine from every state it could be in, measures the
transition matrix that results, and hands it to Phi. The time crystal is the natural
subject: its state is already binary, and it has a knob that tunes exactly how much
causal structure it has.

The prediction is sharp, because the crystal's two mechanisms do different things. The
drive flips every spin **independently**, so it can integrate nothing. The Ising coupling,
where each spin answers to its neighbours, is the only thing that can. So Phi should
follow the coupling and die when the drive's noise drowns it — and the noise is maximal
at `epsilon = 0.5`, where each flip is a fair coin.

Measured, four spins, 400 trials per state:

| epsilon | 0.00 | 0.02 | 0.05 | 0.20 | **0.50** | 0.80 | 1.00 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Phi | 2.93 | 3.52 | 3.70 | 2.80 | **0.10** | 2.31 | 2.92 |

Phi collapses at the noise maximum and recovers symmetrically on both sides — what
matters is how *determined* the drive is, not which way it goes. The prediction held.

**The residual at `epsilon = 0.5` is not integration.** True Phi there is zero; a measured
matrix is a sample, and sampling noise alone manufactures apparent structure. It shrinks
with the trial count, which is how you can tell:

| trials | 100 | 400 | 1 600 | 6 400 | 25 600 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| mean Phi at pure noise | 0.58 | 0.30 | 0.15 | 0.10 | 0.03 |
| mean Phi at `epsilon = 0.05` | 3.32 | 3.47 | 2.73 | 2.63 | — |

So a run at the default trial count reports about 0.3 bits of pure artefact. Both the
floor and its decay are pinned in `tests/test_substrate.py`, so the artefact cannot be
mistaken for a finding.

**What cannot be compared.** The crystal's period-2 lock verdict was calibrated on a
64-spin ring; Phi is only computable up to six units. At four spins the verdict disagrees
with the same epsilon at sixty-four, so Phi and the lock have no shared size to be
compared at. This package therefore claims no relationship between them in either
direction — there is a test pinning the disagreement so the limitation stays visible.

## Reading the mutual-information numbers honestly

The estimator is the plain plug-in one, exactly as the original runs it — no bias
correction. On short windows it overstates MI badly: filling 144 joint bins from 250
samples leaves most of them holding 0, 1 or 2 counts, and that sparsity by itself looks
like structure.

Two genuinely independent streams therefore measure about **0.155 bits**, not zero, on
the default window. The floor falls off as 1/N:

| window | mean MI of independent streams |
| ---: | ---: |
| 250 | 0.155 |
| 1 000 | 0.030 |
| 5 000 | 0.007 |
| 20 000 | 0.002 |

So at the default window `partial` means *indistinguishable from independent*, and only
`emergent` is a claim about the streams. `tests/test_emergence.py` pins both the floor
and its collapse, so a change to the estimator shows up as a failure rather than as
apparent emergence.

## Layout

```
src/anima_reborn/
├─ info.py        entropy · joint entropy · mutual information · Binning
├─ emergence.py   coupled sine streams
├─ crystal.py     driven Ising ring
├─ repulsion.py   A × G latent field
├─ pipeline.py    repulsion → streams → emergence
├─ iit4/          Integrated Information Theory 4.0 — Phi, bit-exact vs hexa
├─ substrate.py   the bridge: our engines → measured TPM → Phi
└─ viewer/        the browser view — the only I/O in the package
tests/            185 tests, no network, no fixtures
```

Every engine is a class you step yourself, with `seed=` for reproducibility, `run(n)` to
advance in bulk, and `reset()` to start over. State objects are frozen dataclasses, so a
reading can be compared, stored and asserted on directly.

## What was deliberately left out of the engines

Canvas drawing, DOM wiring, timers, the tab switcher and the Gradio wrapper. None of it
belongs to an engine. The drawing that survives lives in `viewer/page.html`, on the far
side of an HTTP boundary, and it draws only what Python sends it.

## Differences from the origin

- The origin holds the A × G and pipeline vectors in `Float32Array`; this port uses
  Python floats throughout. The trajectories are noise-driven, so no statistic here is
  affected, but the two will not agree digit for digit.
- `Math.random()` becomes a seeded `random.Random`, so runs are reproducible.
- The repulsion field's circadian channel takes an injectable `clock`, so it can be made
  deterministic in a test.
- One dead local in the origin's A × G tick (`senderHash`, computed and never used) was
  not carried over.

## Tests

```bash
pytest
```

## License

MIT
