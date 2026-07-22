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

import math
import random
import statistics
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .coupled import (
    AMPLITUDE,
    FIXED,
    GAIN,
    MACRO_STEP,
    UNITS,
    CoupledEngine,
    Rhythm,
    Wiring,
)
from .crystal import COUPLING, EPSILON, INVERSE_TEMPERATURE, CrystalVerdict, TimeCrystal
from .iit4 import (
    Complex,
    DirectedPhi,
    SystemPhi,
    TransitionMatrix,
    big_phi,
    directed_big_phi,
    find_complex,
)

__all__ = [
    "CoupledReading",
    "RECURRENCE_FLOOR",
    "RecurrenceEvidence",
    "Representation",
    "SubstrateReading",
    "coupled_matrix",
    "coupled_phi",
    "representation",
    "signature",
    "recurrence_evidence",
    "binarize",
    "crystal_matrix",
    "crystal_phi",
    "estimate_matrix",
    "estimate_state_matrix",
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


@dataclass(frozen=True, slots=True)
class CoupledReading:
    """What IIT 4.0 says about the coupled engine, with its conditions attached.

    Both measures are reported because they disagree, and the disagreement is
    the finding: `phi` cuts undirected and cannot see that a feedforward system
    is reducible, `directed_phi` cuts one way at a time and can. A claim about
    recurrence uses the directed number.

    The conditions are fields rather than documentation because they are part of
    the result. The same engine reads 12.07 at `macro_step = 17` and exactly
    0.0000 at 1.
    """

    wiring: Wiring
    phi: float
    """Undirected big-Phi — comparable with the rest of the repo."""
    directed_phi: float
    """Directed big-Phi. Zero means some direction of influence can be severed
    for free, which is what reducible means."""
    complex_units: int
    """Bitmask of the maximal complex, or 0 when there is none."""
    state: int
    macro_step: int
    trials: int

    @property
    def is_reducible(self) -> bool:
        """Exactly zero directed Phi — some direction severs for free.

        This direction is safe to read off one measurement: a sampled matrix can
        invent structure but cannot invent its absence, so a zero here is a zero.
        The opposite claim is not symmetric, which is why there is no
        `is_recurrent` — see `recurrence_evidence`.
        """
        return self.directed_phi == 0.0

    def __str__(self) -> str:
        entity = f"{self.complex_units:04b}" if self.complex_units else "none"
        return (
            f"{self.wiring.value:<12} phi={self.phi:6.3f} "
            f"directed={self.directed_phi:6.3f} "
            f"{'[reducible]' if self.is_reducible else '           '} "
            f"complex={entity} (state {self.state:04b}, tau={self.macro_step}, "
            f"{self.trials} trials)"
        )


def coupled_matrix(
    wiring: Wiring = Wiring.RING,
    *,
    units: int = UNITS,
    chain: float = 0.0,
    rhythm: Rhythm = FIXED,
    drive: float = 0.0,
    macro_step: int | None = None,
    gain: float = GAIN,
    amplitude: float = AMPLITUDE,
    trials: int = TRIALS,
    seed: int | None = None,
) -> TransitionMatrix:
    """Measure the coupled engine's transition matrix.

    One transition is `macro_step` engine ticks: reconstruct the units to
    +/-`amplitude` from the state, run, threshold at zero. Reconstruction
    amplitude and macro-step both sit inside the result.

    A rhythm must be measured over a whole listen/integrate cycle, so the
    default macro-step follows the rhythm rather than the module constant. Half
    a cycle would report one phase's matrix and label it the engine's.
    """
    if macro_step is None:
        macro_step = rhythm.macro_step
    if macro_step < 1:
        raise ValueError(f"macro_step must be >= 1, got {macro_step}")
    if units > MAX_UNITS:
        raise ValueError(
            f"units must be <= {MAX_UNITS} to stay measurable, got {units}"
        )

    def step(state: int, rng: random.Random) -> int:
        engine = CoupledEngine(
            wiring=wiring,
            units=units,
            chain=chain,
            rhythm=rhythm,
            drive=drive,
            gain=gain,
            amplitude=amplitude,
            seed=rng.getrandbits(63),
            initial=tuple(
                amplitude if state >> i & 1 else -amplitude for i in range(units)
            ),
        )
        return engine.run(macro_step).pattern

    return estimate_matrix(units, step, trials=trials, seed=seed)


def coupled_phi(
    wiring: Wiring = Wiring.RING,
    *,
    units: int = UNITS,
    chain: float = 0.0,
    rhythm: Rhythm = FIXED,
    drive: float = 0.0,
    state: int = 0b0101,
    macro_step: int | None = None,
    gain: float = GAIN,
    amplitude: float = AMPLITUDE,
    trials: int = TRIALS,
    seed: int | None = None,
    with_complex: bool = True,
) -> CoupledReading:
    """Measure the coupled engine's integration.

    Args:
        wiring: Which engine to measure. Pass `Wiring.SELF` or
            `Wiring.FEEDFORWARD` for the falsifiers.
        rhythm: When the units read each other. Integration is a property of the
            engine *including its rhythm*, so this sits in the reading.
        drive: What the engine is being told while measured.
        state: Which pattern to measure at — Phi belongs to a system *in a
            state*. The default is the ring's own attractor.
        macro_step: Engine ticks per measured transition. Defaults to the
            rhythm's own cycle. At 1 every wiring reads exactly zero; see
            `coupled.MACRO_STEP`.
        trials: Samples per state. The artefact floor falls with this.
    """
    if macro_step is None:
        macro_step = rhythm.macro_step
    matrix = coupled_matrix(
        wiring,
        units=units,
        chain=chain,
        rhythm=rhythm,
        drive=drive,
        macro_step=macro_step,
        gain=gain,
        amplitude=amplitude,
        trials=trials,
        seed=seed,
    )
    undirected: SystemPhi = big_phi(matrix, state)
    directed: DirectedPhi = directed_big_phi(matrix, state)
    entity: Complex | None = find_complex(matrix, state) if with_complex else None

    return CoupledReading(
        wiring=wiring,
        phi=undirected.phi,
        directed_phi=directed.phi,
        complex_units=entity.units if entity else 0,
        state=state,
        macro_step=macro_step,
        trials=trials,
    )


REPRESENTATION_TICKS = 800
"""Ticks per trajectory. Long enough that the ring has settled into whatever it
settles into, so the reading is not about the transient."""

REPRESENTATION_TAIL = 300
"""Ticks summarized, taken from the end. Mean AND variability per unit, because
an alternating engine never stops moving and its position alone throws away what
its motion keeps."""

NOISE_SEEDS = 12
"""Repeats of ONE drive under different walks — the within-drive spread that the
between-drive spread has to beat. This is the null, and it is structural rather
than chosen: at a ratio of 1.0 the drives separate exactly as much as the same
drive separates from itself."""


@dataclass(frozen=True, slots=True)
class Representation:
    """How much of what an engine was told survives in what it does.

    Two spreads, in the same units. `by_drive` is how far apart different drives
    put the engine; `by_noise` is how far apart ONE drive puts it across
    different walks. Their ratio is the reading, and 1.0 is the floor by
    construction rather than by choice.
    """

    by_drive: float
    by_noise: float
    drives: int
    ticks: int

    @property
    def ratio(self) -> float:
        return self.by_drive / max(self.by_noise, 1e-9)

    @property
    def represents(self) -> bool:
        """Whether the drive is recoverable from the trajectory at all."""
        return self.ratio > 1.0

    def __str__(self) -> str:
        return (
            f"representation={self.ratio:6.2f} "
            f"(between {self.by_drive:.4f} / within {self.by_noise:.4f}, "
            f"{self.drives} drives, {self.ticks} ticks)"
            f"{'' if self.represents else ' [at the noise floor]'}"
        )


def signature(
    drive: float | Sequence[float],
    *,
    wiring: Wiring = Wiring.RING,
    rhythm: Rhythm = FIXED,
    seed: int = 0,
    ticks: int = REPRESENTATION_TICKS,
    tail: int = REPRESENTATION_TAIL,
    gain: float = GAIN,
    amplitude: float = AMPLITUDE,
) -> list[float]:
    """What an engine told `drive` does, as `UNITS` means then `UNITS` spreads.

    The tail of the trajectory rather than its endpoint, and its variability
    alongside its position — an engine running a rhythm never stops moving, and
    where it is throws away what its motion keeps. Public because a caller
    asking "does what I told it survive" needs the same summary `representation`
    scores, and a second copy of it would drift.
    """
    engine = CoupledEngine(
        wiring=wiring,
        rhythm=rhythm,
        drive=drive,
        gain=gain,
        amplitude=amplitude,
        seed=seed,
        initial=(0.0,) * UNITS,
    )
    recent: list[tuple[float, ...]] = []
    for tick in range(ticks):
        values = engine.step().values
        if tick >= ticks - tail:
            recent.append(values)
    return [
        statistics.mean(point[i] for point in recent) for i in range(UNITS)
    ] + [statistics.pstdev([point[i] for point in recent]) for i in range(UNITS)]


def _spread(points: Sequence[Sequence[float]]) -> float:
    centre = [statistics.mean(p[i] for p in points) for i in range(len(points[0]))]
    return statistics.mean(math.dist(p, centre) for p in points)


def representation(
    drives: Sequence[float | Sequence[float]],
    *,
    wiring: Wiring = Wiring.RING,
    rhythm: Rhythm = FIXED,
    seed: int = 1,
    noise_seeds: int = NOISE_SEEDS,
    ticks: int = REPRESENTATION_TICKS,
    tail: int = REPRESENTATION_TAIL,
    gain: float = GAIN,
    amplitude: float = AMPLITUDE,
) -> Representation:
    """Measure how much of its drive an engine's trajectory still carries.

    The other half of the wall. `coupled_phi` says whether the engine is
    irreducible; this says whether anything it was told is still in it. On a
    fixed coupling the two trade off monotonically and there is no setting where
    both hold — which is why `Rhythm` exists.

    Args:
        drives: What to tell the engine, one value per trial, in [-1, 1].
        rhythm: When the units read each other. This is the argument the
            measurement is about.
        seed: Fixes the walk for the between-drive comparison, so different
            drives differ by their drive and not by their noise.
        noise_seeds: Repeats of `drives[0]` that form the within-drive null.
    """
    if len(drives) < 2:
        raise ValueError(f"drives must have at least 2 values, got {len(drives)}")
    if noise_seeds < 2:
        raise ValueError(f"noise_seeds must be >= 2, got {noise_seeds}")
    if tail < 2 or tail > ticks:
        raise ValueError(f"tail must be in [2, {ticks}], got {tail}")

    def measure(drive: float | Sequence[float], walk: int) -> list[float]:
        return signature(
            drive,
            wiring=wiring,
            rhythm=rhythm,
            seed=walk,
            ticks=ticks,
            tail=tail,
            gain=gain,
            amplitude=amplitude,
        )

    return Representation(
        by_drive=_spread([measure(d, seed) for d in drives]),
        by_noise=_spread([measure(drives[0], w) for w in range(noise_seeds)]),
        drives=len(drives),
        ticks=ticks,
    )


RECURRENCE_FLOOR = 1.0
"""Directed Phi a wiring must clear before recurrence is entertained.

Measured against the null rather than picked: four units reading only
themselves, where the true value is exactly zero, produce 0.251 mean and 0.547
worst over eight seeds at 400 trials, decaying to 0.037 at 25600. This bar is
above every one of those, and the ring measures ~9.9 — a factor of sixty.

Verified separately that the measure itself is not the source: on an exactly
factorized transition matrix, built analytically with no sampling at all, both
`big_phi` and `directed_big_phi` return 0.000000. The residue is sampling, and
sampling alone.
"""


@dataclass(frozen=True, slots=True)
class RecurrenceEvidence:
    """Whether integration survives being looked at harder.

    A single positive Phi means nothing on its own: at 6400 trials the
    self-wired null — four units reading only themselves, no coupling anywhere —
    still measures 0.031 directed. Sampling noise manufactures structure, and a
    bare threshold would call that recurrence.

    What separates signal from floor is the same discipline the rest of the repo
    uses: measure twice and see whether it shrinks. Artefacts halve as trials
    grow; a real coupling does not.
    """

    coarse: CoupledReading
    fine: CoupledReading

    @property
    def held(self) -> bool:
        """The directed value survived a fourfold increase in sampling."""
        return self.fine.directed_phi > self.coarse.directed_phi / 2

    @property
    def is_recurrent(self) -> bool:
        """Integration that is substantial AND did not shrink.

        Both conditions, because either alone is fooled. The magnitude bar of
        `RECURRENCE_FLOOR` is measured, not chosen: the self-wired null — no
        coupling anywhere, true Phi exactly zero — reads 0.251 / 0.155 / 0.081 /
        0.037 mean over eight seeds at 400 / 1600 / 6400 / 25600 trials, with a
        worst seed of 0.547. The bar sits nearly twice that worst case.
        """
        return self.fine.directed_phi > RECURRENCE_FLOOR and self.held

    def __str__(self) -> str:
        trend = "held" if self.held else "collapsed"
        return (
            f"{self.coarse.wiring.value:<12} "
            f"{self.coarse.trials}->{self.fine.trials} trials: "
            f"{self.coarse.directed_phi:.3f} -> {self.fine.directed_phi:.3f} "
            f"({trend}) "
            f"{'RECURRENT' if self.is_recurrent else 'not established'}"
        )


def recurrence_evidence(
    wiring: Wiring = Wiring.RING,
    *,
    trials: int = TRIALS,
    factor: int = 4,
    **kwargs: Any,
) -> RecurrenceEvidence:
    """Measure a wiring twice and report whether its integration held.

    Recurrence is not readable from one number, so this refuses to return one.
    Any keyword `coupled_phi` accepts is forwarded to both measurements.
    """
    if factor < 2:
        raise ValueError(f"factor must be >= 2, got {factor}")
    return RecurrenceEvidence(
        coarse=coupled_phi(wiring, trials=trials, with_complex=False, **kwargs),
        fine=coupled_phi(wiring, trials=trials * factor, with_complex=False, **kwargs),
    )


def estimate_state_matrix(
    n: int,
    step: Callable[[int, random.Random], int],
    *,
    trials: int = TRIALS,
    seed: int | None = None,
) -> list[list[float]]:
    """Measure a process's state-to-state transition matrix.

    A different object from `estimate_matrix`, which records each unit's ON
    frequency and assumes the units are conditionally independent. This counts
    whole successor states, which is what `iit4.ei` needs — the two lanes take
    different inputs and are not views of one thing.

    Rows sum to one by construction.
    """
    if not 1 <= n <= MAX_UNITS:
        raise ValueError(f"n must be in [1, {MAX_UNITS}], got {n}")
    if trials < 1:
        raise ValueError(f"trials must be >= 1, got {trials}")

    rng = random.Random(seed)
    states = 1 << n
    matrix = []
    for state in range(states):
        counts = [0] * states
        for _ in range(trials):
            counts[step(state, rng)] += 1
        matrix.append([count / trials for count in counts])
    return matrix
