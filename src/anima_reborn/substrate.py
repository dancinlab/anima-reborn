"""The bridge — measuring one of our own engines with IIT 4.0.

The engines in this package produce behaviour. `iit4` measures whether a system
is one thing. This module joins them: it drives an engine from every state it
could be in, watches where it goes, and hands the resulting transition matrix to
Phi.

    from anima_reborn.substrate import crystal_phi

    print(crystal_phi(size=4, epsilon=0.02, seed=1))

**How the matrix is obtained.** IIT needs `P(unit is ON next | system state)`.
For a stochastic engine that is not something to derive on paper — the Ising
sweep visits spins in order, each decision conditioned on flips already made —
so it is *measured*: pin the system to a state, run one step, record which units
came back ON, and repeat. That is an empirical transition matrix, and its error
falls off as one over the square root of the trial count. Nothing here pretends
otherwise; `trials` is the honest knob and the estimate is a sample.

**Why the crystal.** Of the four engines it is the only one whose state is
natively binary — a spin is up or down, which is exactly what a unit is. The
others live in continuous latent space, and turning that into bits means
choosing a threshold. A threshold is a modeling decision that would end up
inside the Phi it produces, so this module refuses to make one silently:
`binarize` exists and takes the rule from the caller.

**What the crystal has to do with consciousness: nothing, and that is the
point.** It is a substrate with a known, tunable amount of causal structure, so
it can say whether the measurement responds to structure at all. The drive that
flips every spin acts on each one independently and integrates nothing; the
Ising coupling, where each spin answers to its neighbours, is the only thing
that can. So Phi should follow the coupling and collapse when noise drowns it —
a prediction that can fail, and `tests/test_substrate.py` is where it is put at
risk.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .crystal import COUPLING, EPSILON, INVERSE_TEMPERATURE, CrystalVerdict, TimeCrystal
from .iit4 import Complex, SystemPhi, TransitionMatrix, big_phi, find_complex

__all__ = [
    "SubstrateReading",
    "binarize",
    "crystal_matrix",
    "crystal_phi",
    "estimate_matrix",
]

TRIALS = 400
"""Samples per state. The estimate's error falls as 1/sqrt(trials), so this
buys precision, not correctness — and Phi is an argmax, so a noisy matrix can
pick a different partition rather than merely a nearby number."""

MAX_UNITS = 6
"""Above this, measuring Phi stops finishing. Every mechanism searches every
purview over every partition, and `find_complex` repeats all of it per subset."""


def binarize(values: Sequence[float], threshold: float = 0.0) -> int:
    """Pack values into a state, one bit per value, ON when above `threshold`.

    Offered for callers who want to measure a continuous engine, and left as
    the caller's call on purpose: the threshold decides what counts as a unit
    being on, and therefore decides the Phi. It is a choice about the model,
    not a fact about the engine.
    """
    state = 0
    for i, value in enumerate(values):
        if value > threshold:
            state |= 1 << i
    return state


def estimate_matrix(
    n: int,
    step: Callable[[int, random.Random], int],
    *,
    trials: int = TRIALS,
    seed: int | None = None,
) -> TransitionMatrix:
    """Measure a stepping process's transition matrix by driving it.

    Args:
        n: Number of binary units.
        step: Takes a state and a random source, returns the state one step
            later. Called `trials` times per state, so it must not carry
            anything over between calls — the whole point is that each trial is
            an independent draw from the same starting state.
        trials: Samples per state.
        seed: Fixes the sampling.

    Returns:
        A `TransitionMatrix` whose entries are ON-frequencies rather than exact
        probabilities.
    """
    if not 1 <= n <= MAX_UNITS:
        raise ValueError(f"n must be in [1, {MAX_UNITS}], got {n}")
    if trials < 1:
        raise ValueError(f"trials must be >= 1, got {trials}")

    rng = random.Random(seed)
    values: list[float] = []
    for state in range(1 << n):
        counts = [0] * n
        for _ in range(trials):
            following = step(state, rng)
            for unit in range(n):
                if following >> unit & 1:
                    counts[unit] += 1
        values.extend(count / trials for count in counts)
    return TransitionMatrix(values, n)


def crystal_matrix(
    *,
    size: int = 4,
    epsilon: float = EPSILON,
    coupling: float = COUPLING,
    beta: float = INVERSE_TEMPERATURE,
    trials: int = TRIALS,
    seed: int | None = None,
) -> TransitionMatrix:
    """The time crystal's transition matrix, measured over one drive period.

    A spin being up is a unit being ON. One step is what the crystal itself
    calls a step: an Ising sweep, then the imperfect global flip.
    """
    if size > MAX_UNITS:
        raise ValueError(
            f"size must be <= {MAX_UNITS} to stay measurable, got {size}"
        )

    def step(state: int, rng: random.Random) -> int:
        spins = [1 if state >> i & 1 else -1 for i in range(size)]
        ring = TimeCrystal(
            size=size,
            epsilon=epsilon,
            coupling=coupling,
            beta=beta,
            history=1,
            seed=rng.getrandbits(63),
            initial=spins,
        )
        ring.step()
        return sum(1 << i for i, spin in enumerate(ring.spins) if spin > 0)

    return estimate_matrix(size, step, trials=trials, seed=seed)


@dataclass(frozen=True, slots=True)
class SubstrateReading:
    """What IIT 4.0 says about one of our engines.

    `verdict` is the engine's own read on itself — the crystal's period-2 lock —
    kept alongside Phi so the two can be compared rather than conflated. They
    are different claims: one is about rhythm in time, the other about the
    system being one thing.
    """

    phi: float
    """big-Phi of the whole substrate, in bits."""
    complex_units: int
    """Bitmask of the maximal complex — the part that is the entity. Zero when
    there is none."""
    complex_phi: float
    total: float
    """Unpartitioned Phi-structure the cut was measured against."""
    distinctions: int
    verdict: CrystalVerdict | None = None
    """The crystal's own lock verdict, when the substrate is a crystal."""

    @property
    def is_integrated(self) -> bool:
        return self.phi > 0.0

    def __str__(self) -> str:
        entity = f"{self.complex_units:b}" if self.complex_units else "none"
        rhythm = f" rhythm={self.verdict.value}" if self.verdict else ""
        return (
            f"phi={self.phi:.6f} of total={self.total:.6f} "
            f"({self.distinctions} distinctions) complex={entity}"
            f" phi_c={self.complex_phi:.6f}{rhythm}"
        )


def crystal_phi(
    *,
    size: int = 4,
    epsilon: float = EPSILON,
    coupling: float = COUPLING,
    beta: float = INVERSE_TEMPERATURE,
    state: int | None = None,
    trials: int = TRIALS,
    seed: int | None = None,
    with_complex: bool = True,
    with_verdict: bool = True,
) -> SubstrateReading:
    """Measure the time crystal's integrated information.

    Args:
        size: Spins in the ring, at most `MAX_UNITS`.
        epsilon: Per-spin probability the drive misses.
        state: Which ring configuration to measure Phi at. Defaults to the
            all-up state — Phi is a property of a system *in a state*, never of
            the system alone.
        trials: Samples per state when measuring the transition matrix.
        with_complex: Also search for the maximal complex. Roughly doubles the
            work and is what tells you *which part* is the entity.
        with_verdict: Also run the ring long enough to read its own lock
            verdict, for comparison against Phi.
    """
    matrix = crystal_matrix(
        size=size,
        epsilon=epsilon,
        coupling=coupling,
        beta=beta,
        trials=trials,
        seed=seed,
    )
    at = (1 << size) - 1 if state is None else state
    measured: SystemPhi = big_phi(matrix, at)

    entity: Complex | None = find_complex(matrix, at) if with_complex else None

    verdict = None
    if with_verdict:
        ring = TimeCrystal(
            size=size, epsilon=epsilon, coupling=coupling, beta=beta, seed=seed
        )
        verdict = ring.run(400).verdict

    return SubstrateReading(
        phi=measured.phi,
        complex_units=entity.units if entity else 0,
        complex_phi=entity.phi if entity else 0.0,
        total=measured.total,
        distinctions=len(measured.structure.distinctions),
        verdict=verdict,
    )
