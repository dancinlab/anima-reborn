"""Discrete time crystal — a ring of spins that keeps a beat it was never given.

Each tick does two things to a periodic Ising chain:

    1. a Metropolis sweep, which lets neighbours pull each other into line
    2. a pi-flip, which tries to invert every spin but misses with probability
       `epsilon`

The flip alone would just alternate the chain forever, and the noise alone
would melt it. Together they do something stranger: the Ising coupling repairs
the flaws the imperfect flip leaves behind, so the chain locks into a period-2
rhythm that survives the imperfection. That is the time crystal — order in
time rather than in space, and it holds only while the repair outruns the
damage.

The lock shows up in the magnetization's autocorrelation: strongly negative at
lag 1 (each tick is the opposite of the last) and strongly positive at lag 2
(every second tick agrees).

Ported from the DTC engine in `dancinlab/anima-experience` `index.html`, itself
a port of `dtc_demo.py`.
"""

from __future__ import annotations

import math
import random
from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

__all__ = ["CrystalState", "CrystalVerdict", "TimeCrystal", "autocorrelation"]

SIZE = 64
"""Spins in the ring."""

COUPLING = 1.0
"""Ising J — how hard neighbours insist on agreeing."""

INVERSE_TEMPERATURE = 2.5
"""Ising beta. Higher means colder, so unfavourable flips are rarer."""

EPSILON = 0.05
"""Per-spin probability the pi-flip *misses* — the imperfection the crystal has
to survive."""

HISTORY = 300
"""Magnetization samples kept for the autocorrelation."""

MIN_LEAD = 20
"""An autocorrelation at lag k needs at least k + 20 samples before it is
reported; below that it returns 0.0 rather than a number built on noise."""


def autocorrelation(series: Sequence[float], lag: int) -> float:
    """Pearson correlation of a series with itself, shifted by `lag`.

    Returns 0.0 when the series is too short to support the lag, or when it is
    flat enough that the correlation would be a division by nothing.
    """
    if lag < 0:
        raise ValueError(f"lag must be >= 0, got {lag}")
    n = len(series)
    if n < lag + MIN_LEAD:
        return 0.0

    mean = sum(series) / n
    dot_aa = dot_bb = dot_ab = 0.0
    for i in range(n - lag):
        a = series[i] - mean
        b = series[i + lag] - mean
        dot_aa += a * a
        dot_bb += b * b
        dot_ab += a * b

    denominator = math.sqrt(dot_aa * dot_bb)
    return dot_ab / denominator if denominator > 1e-10 else 0.0


class CrystalVerdict(Enum):
    """What the autocorrelation says the chain is doing."""

    LOCKED = "locked"
    """Period-2 lock: anti-phase with the drive, and holding."""
    BUILDING = "building"
    """Period doubling under way — lag-1 has gone anti-phase, lag-2 has not yet
    caught up."""
    CHAOS = "chaos"
    """Melted. The imperfection outran the Ising repair."""

    @classmethod
    def classify(cls, ac1: float, ac2: float) -> CrystalVerdict:
        if ac1 < -0.85 and ac2 > 0.80:
            return cls.LOCKED
        if ac1 < -0.5:
            return cls.BUILDING
        return cls.CHAOS


@dataclass(frozen=True, slots=True)
class CrystalState:
    """One reading of the chain."""

    magnetization: float
    """Mean spin, in [-1, +1]."""
    ac1: float
    """Autocorrelation at lag 1 — near -1 when each tick inverts the last."""
    ac2: float
    """Autocorrelation at lag 2 — near +1 when every second tick agrees."""
    ac4: float
    """Autocorrelation at lag 4, reported for contrast with the period-2 pair."""
    verdict: CrystalVerdict

    def __str__(self) -> str:
        return (
            f"m={self.magnetization:+.3f} ac1={self.ac1:+.3f} "
            f"ac2={self.ac2:+.3f} ac4={self.ac4:+.3f} [{self.verdict.value}]"
        )


class TimeCrystal:
    """A driven Ising ring that can lock into a period-2 rhythm.

    Args:
        size: Number of spins in the ring.
        epsilon: Per-spin miss probability of the pi-flip, in [0, 1]. Small
            values keep the crystal; raise it far enough and it melts.
        coupling: Ising J.
        beta: Inverse temperature.
        history: Magnetization samples kept for the autocorrelations.
        seed: Fixes both the initial spins and the dynamics.
        initial: Starting spins, each +1 or -1. Defaults to a random ring. Pass
            an explicit one to start from a known configuration — measuring the
            ring's transition probabilities means driving it from every state in
            turn. `reset` re-randomizes regardless.
    """

    def __init__(
        self,
        *,
        size: int = SIZE,
        epsilon: float = EPSILON,
        coupling: float = COUPLING,
        beta: float = INVERSE_TEMPERATURE,
        history: int = HISTORY,
        seed: int | None = None,
        initial: Sequence[int] | None = None,
    ) -> None:
        if size < 3:
            raise ValueError(f"size must be >= 3 for a ring, got {size}")
        if history < 1:
            raise ValueError(f"history must be >= 1, got {history}")
        self.epsilon = epsilon
        self.coupling = coupling
        self.beta = beta
        self._rng = random.Random(seed)
        if initial is None:
            self._spins = [1 if self._rng.random() < 0.5 else -1 for _ in range(size)]
        else:
            if len(initial) != size:
                raise ValueError(
                    f"initial must have {size} spins, got {len(initial)}"
                )
            if any(s not in (1, -1) for s in initial):
                raise ValueError("every spin must be +1 or -1")
            self._spins = [int(s) for s in initial]
        self._history: deque[float] = deque(maxlen=history)

    @property
    def epsilon(self) -> float:
        return self._epsilon

    @epsilon.setter
    def epsilon(self, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"epsilon must be in [0, 1], got {value}")
        self._epsilon = value

    @property
    def spins(self) -> tuple[int, ...]:
        """The ring, each entry +1 or -1."""
        return tuple(self._spins)

    @property
    def size(self) -> int:
        return len(self._spins)

    @property
    def magnetization(self) -> float:
        """Mean spin, in [-1, +1]."""
        return sum(self._spins) / len(self._spins)

    @property
    def history(self) -> tuple[float, ...]:
        """Recent magnetizations, oldest first."""
        return tuple(self._history)

    def _ising_sweep(self) -> None:
        """One Metropolis pass. Each spin is offered a flip; it takes it if the
        flip lowers the energy, or by chance if it does not. This is the repair
        that keeps the imperfect drive from melting the chain."""
        spins = self._spins
        n = len(spins)
        random_ = self._rng.random
        exp = math.exp
        two_j = 2.0 * self.coupling
        beta = self.beta
        for i in range(n):
            neighbours = spins[i - 1] + spins[(i + 1) % n]
            delta_e = two_j * spins[i] * neighbours
            if delta_e <= 0 or random_() < exp(-beta * delta_e):
                spins[i] = -spins[i]

    def _pi_flip(self) -> None:
        """The external drive: invert every spin, missing each independently
        with probability `epsilon`."""
        spins = self._spins
        random_ = self._rng.random
        epsilon = self._epsilon
        for i in range(len(spins)):
            if random_() > epsilon:
                spins[i] = -spins[i]

    def step(self) -> CrystalState:
        """Advance one drive period: sweep, flip, then measure."""
        self._ising_sweep()
        self._pi_flip()
        self._history.append(self.magnetization)
        return self.state

    def run(self, ticks: int) -> CrystalState:
        """Advance `ticks` periods and read the state at the end."""
        if ticks < 1:
            raise ValueError(f"ticks must be >= 1, got {ticks}")
        for _ in range(ticks - 1):
            self.step()
        return self.step()

    @property
    def state(self) -> CrystalState:
        series = self._history
        ac1 = autocorrelation(series, 1)
        ac2 = autocorrelation(series, 2)
        ac4 = autocorrelation(series, 4)
        return CrystalState(
            magnetization=self.magnetization,
            ac1=ac1,
            ac2=ac2,
            ac4=ac4,
            verdict=CrystalVerdict.classify(ac1, ac2),
        )

    def reset(self) -> None:
        """Re-randomize the ring and drop the history."""
        self._spins = [
            1 if self._rng.random() < 0.5 else -1 for _ in range(len(self._spins))
        ]
        self._history.clear()
