"""Reproduce the coupling measurement behind the stage-1 roadmap.

Run from the repo root:

    PYTHONPATH=src python state/coupling/verify_coupling.py

This is the independent check of the delegated design's headline claim: that a
ring of four units, each reading another, has integration bought entirely by its
own wiring — and that rewiring each unit to itself collapses it to the pinned
sampling-artefact floor.

Nothing here is imported by the package. It exists so the numbers in
`state/coupling/RESULTS.md` can be re-derived rather than trusted.
"""

from __future__ import annotations

import math
import random
import statistics

from anima_reborn.iit4 import big_phi, find_complex
from anima_reborn.pipeline import PULL, WALK
from anima_reborn.substrate import estimate_matrix

AMPLITUDE = 0.78
"""`separation * 1.3` — the repulsion field's own dim-0 target amplitude."""

GAIN = 3.0
"""Steepness of the tanh each unit applies to whatever it reads."""

MACRO_STEP = 17
"""Engine ticks per measured transition — the substrate's time constant
`1 / PULL`. This sits INSIDE the resulting Phi and must be quoted with it: at
tau = 1 a unit moves 6% toward its target, every unit merely copies itself, the
transition matrix factorizes and Phi is 0.0000 exactly."""

STATE = 0b0101
"""The alternating pattern a negative four-cycle settles into. Phi is a property
of a system *in a state*; this is the ring's own attractor."""

WIRINGS = {
    # index i reads WIRINGS[w][i]; None means an exogenous constant target.
    "ring": [3, 0, 1, 2],  # closed cycle: a0<-g1, g0<-a0, a1<-g0, g1<-a1
    "feedforward": [None, 0, 1, 2],  # no path back to unit 0
    "self": [0, 1, 2, 3],  # each unit reads itself — the null
}


def make_step(sources: list[int | None], macro_step: int = MACRO_STEP):
    """One measured transition: reconstruct to +/-AMPLITUDE, run `macro_step`
    engine ticks of the repulsion law, threshold at zero."""

    def step(state: int, rng: random.Random) -> int:
        x = [AMPLITUDE if state >> i & 1 else -AMPLITUDE for i in range(4)]
        for _ in range(macro_step):
            nxt = list(x)
            for i, source in enumerate(sources):
                target = (
                    -AMPLITUDE
                    if source is None
                    else -AMPLITUDE * math.tanh(GAIN * x[source] / AMPLITUDE)
                )
                nxt[i] = x[i] + (target - x[i]) * PULL + (rng.random() - 0.5) * WALK
            x = nxt
        return sum(1 << i for i, v in enumerate(x) if v > 0)

    return step


def phi(sources, *, trials: int, seeds: int = 4, macro_step: int = MACRO_STEP) -> float:
    return statistics.mean(
        big_phi(
            estimate_matrix(4, make_step(sources, macro_step), trials=trials, seed=s),
            STATE,
        ).phi
        for s in range(seeds)
    )


def main() -> None:
    print(f"4 units · state {STATE:04b} · threshold 0 · tau={MACRO_STEP} · seeds 0-3\n")

    print(f"{'wiring':<14}{'400':>9}{'1600':>9}{'6400':>9}   verdict")
    print("-" * 60)
    for name, sources in WIRINGS.items():
        row = [phi(sources, trials=t) for t in (400, 1600, 6400)]
        artefact = row[-1] < row[0] / 2
        print(
            f"{name:<14}{row[0]:>9.2f}{row[1]:>9.2f}{row[2]:>9.2f}   "
            f"{'artefact — halves with trials' if artefact else 'holds across trials'}"
        )

    print("\ntimescale dependence (ring, 6400 trials, seeds 0-2)")
    for macro_step in (1, 5, 17, 34):
        value = phi(WIRINGS["ring"], trials=6400, seeds=3, macro_step=macro_step)
        print(f"  tau={macro_step:<4} Phi={value:.4f}")

    matrix = estimate_matrix(4, make_step(WIRINGS["ring"]), trials=6400, seed=0)
    print(f"\nmaximal complex of the ring: {find_complex(matrix, STATE)}")


if __name__ == "__main__":
    main()
