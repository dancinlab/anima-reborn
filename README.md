<h1 align="center">🌱 anima-reborn</h1>

<p align="center"><strong>The <a href="https://github.com/dancinlab/anima-experience">anima-experience</a> engines, reborn as headless Python</strong> — same maths, no canvas, seedable and testable</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue">
  <img alt="Dependencies" src="https://img.shields.io/badge/dependencies-none-success">
  <img alt="Tests" src="https://img.shields.io/badge/tests-96%20passing-success">
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
  ctrl-c to stop
```

Four tabs, live sliders, and the same visuals as the origin — but every number and every
plotted point comes from the Python engines over `/api/<engine>`. The page draws; it
never simulates. That is what makes it evidence about the port rather than a second
implementation.

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
└─ viewer/        the browser view — the only I/O in the package
tests/            96 tests, no network, no fixtures
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
