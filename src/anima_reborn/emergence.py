"""Emergence — two byte streams bound by a shared oscillator.

Each tick draws one sample per stream. Both are a blend of private noise and a
single sine wave they have in common, mixed by `coupling`:

    L = (1 - c) * noise_L + c * sin(0.1 * t)
    R = (1 - c) * noise_R + c * sin(0.1 * t)

At c = 0 the streams are independent and their mutual information is zero. Turn
c up and the shared term dominates: the scatter of L against R collapses onto
the diagonal and MI climbs past the emergence bar. Nothing was added to either
stream — the information lives in the pair.

Ported from the emergence engine in `dancinlab/anima-experience` `index.html`.
"""

from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass

from .info import Binning, Emergence, entropy, joint_entropy

__all__ = ["EmergenceEngine", "EmergenceMetrics"]

HISTORY = 250
"""Rolling window, about four seconds at the original's 60 fps."""

MIN_SAMPLES_FOR_METRICS = 50
"""Below this the histogram is too sparse for the entropy estimate to mean
anything, so no metrics are reported at all."""

COMMON_FREQUENCY = 0.1
"""Radians per tick of the shared oscillator."""


@dataclass(frozen=True, slots=True)
class EmergenceMetrics:
    """One reading of the pair. All entropies are in bits."""

    h_left: float
    h_right: float
    h_joint: float
    mutual_information: float
    verdict: Emergence

    def __str__(self) -> str:
        return (
            f"H(L)={self.h_left:.2f} H(R)={self.h_right:.2f} "
            f"H(L,R)={self.h_joint:.2f} MI={self.mutual_information:.3f} "
            f"[{self.verdict.value}]"
        )


class EmergenceEngine:
    """Two coupled streams and the mutual information between them.

    Args:
        coupling: How much of the shared oscillator each stream carries, in
            [0, 1]. 0 is fully independent, 1 makes the streams identical.
        seed: Fixes the noise so a run is reproducible. None draws from the
            system source.
        history: Rolling window length in samples.
        binning: Histogram used for every entropy on this engine.
    """

    def __init__(
        self,
        coupling: float = 0.5,
        *,
        seed: int | None = None,
        history: int = HISTORY,
        binning: Binning | None = None,
    ) -> None:
        if history < 1:
            raise ValueError(f"history must be >= 1, got {history}")
        self.coupling = coupling
        self.binning = binning or Binning(bins=12, vrange=1.5)
        self._rng = random.Random(seed)
        self._left: deque[float] = deque(maxlen=history)
        self._right: deque[float] = deque(maxlen=history)
        self._tick = 0

    @property
    def coupling(self) -> float:
        return self._coupling

    @coupling.setter
    def coupling(self, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"coupling must be in [0, 1], got {value}")
        self._coupling = value

    @property
    def left(self) -> tuple[float, ...]:
        """The left stream's rolling window, oldest first."""
        return tuple(self._left)

    @property
    def right(self) -> tuple[float, ...]:
        return tuple(self._right)

    @property
    def ticks(self) -> int:
        return self._tick

    def sample(self) -> tuple[float, float]:
        """Draw the next pair without recording it."""
        common = math.sin(self._tick * COMMON_FREQUENCY)
        c = self._coupling
        noise_l = (self._rng.random() - 0.5) * 2.0
        noise_r = (self._rng.random() - 0.5) * 2.0
        return (
            (1.0 - c) * noise_l + c * common,
            (1.0 - c) * noise_r + c * common,
        )

    def step(self) -> tuple[float, float]:
        """Advance one tick and push the new pair into the window."""
        left, right = self.sample()
        self._left.append(left)
        self._right.append(right)
        self._tick += 1
        return left, right

    def run(self, ticks: int) -> EmergenceMetrics | None:
        """Advance `ticks` times and read the metrics out at the end."""
        if ticks < 0:
            raise ValueError(f"ticks must be >= 0, got {ticks}")
        for _ in range(ticks):
            self.step()
        return self.metrics

    @property
    def metrics(self) -> EmergenceMetrics | None:
        """The current reading, or None while the window is still filling."""
        if len(self._left) < MIN_SAMPLES_FOR_METRICS:
            return None
        h_left = entropy(self._left, self.binning)
        h_right = entropy(self._right, self.binning)
        h_joint = joint_entropy(self._left, self._right, self.binning)
        mi = max(0.0, h_left + h_right - h_joint)
        return EmergenceMetrics(
            h_left=h_left,
            h_right=h_right,
            h_joint=h_joint,
            mutual_information=mi,
            verdict=Emergence.classify(mi),
        )

    def reset(self) -> None:
        """Clear the window and the tick counter. The noise source carries on
        where it left off — resetting is not rewinding."""
        self._left.clear()
        self._right.clear()
        self._tick = 0
