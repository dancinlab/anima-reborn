"""The full chain — engine repulsion drives two streams, and emergence is read
off the pair.

This is the other two engines joined end to end. A and G drift apart exactly as
in `repulsion`, but here their leading dimensions are *sampled*: one noisy
observation per tick from each. Those two observation streams are then measured
the way `emergence` measures its own.

    A, G drift apart  ->  sample A[0], G[0]  ->  MI(L, R)

The claim is that separation is what produces shared information. Collapse A
onto G and the streams have no common structure left to carry; hold them apart
and mutual information appears in the pair without anything being injected into
either stream.

Ported from the pipeline engine in `dancinlab/anima-experience` `index.html`.
See `repulsion` on the float32-versus-float64 difference from the original.
"""

from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass

from .info import Binning, Emergence, entropy, joint_entropy
from .repulsion import DAMPING, PHASE_RATE, PULL

__all__ = ["Pipeline", "PipelineState"]

DIM = 8
"""Latent dimension of each engine — smaller than the standalone field."""

HISTORY = 200
"""Rolling window of stream observations."""

MIN_SAMPLES_FOR_METRICS = 50

SEPARATION = 0.60

WALK = 0.04
"""Per-dimension random walk on the engine vectors. Fixed here, unlike the
standalone field where it scales with a noise control."""

OBSERVATION_NOISE = 0.4
"""Width of the noise on each sampled observation."""


@dataclass(frozen=True, slots=True)
class PipelineState:
    """One reading of the whole chain."""

    tension: float
    """Mean squared repulsion between the engines."""
    h_left: float
    h_right: float
    h_joint: float
    mutual_information: float
    verdict: Emergence

    def __str__(self) -> str:
        return (
            f"tension={self.tension:.2f} H(L)={self.h_left:.2f} "
            f"H(R)={self.h_right:.2f} MI={self.mutual_information:.3f} "
            f"[{self.verdict.value}]"
        )


class Pipeline:
    """Engine separation in, emergence out.

    Args:
        separation: How hard the rotating target drives A and G apart.
        dim: Latent dimension of each engine. Must be at least 2.
        history: Rolling window of observations behind the entropies.
        seed: Fixes the engine vectors, the drift and the observation noise.
        binning: Histogram used for the entropies.
    """

    def __init__(
        self,
        *,
        separation: float = SEPARATION,
        dim: int = DIM,
        history: int = HISTORY,
        seed: int | None = None,
        binning: Binning | None = None,
    ) -> None:
        if dim < 2:
            raise ValueError(f"dim must be >= 2, got {dim}")
        if history < 1:
            raise ValueError(f"history must be >= 1, got {history}")
        self.separation = separation
        self.binning = binning or Binning(bins=12, vrange=1.6)
        self._dim = dim
        self._rng = random.Random(seed)
        self._a = self._random_vector()
        self._g = self._random_vector()
        self._left: deque[float] = deque(maxlen=history)
        self._right: deque[float] = deque(maxlen=history)
        self._tick = 0

    def _random_vector(self) -> list[float]:
        return [(self._rng.random() - 0.5) * 0.3 for _ in range(self._dim)]

    @property
    def a(self) -> tuple[float, ...]:
        return tuple(self._a)

    @property
    def g(self) -> tuple[float, ...]:
        return tuple(self._g)

    @property
    def left(self) -> tuple[float, ...]:
        """Observations sampled from engine A, oldest first."""
        return tuple(self._left)

    @property
    def right(self) -> tuple[float, ...]:
        """Observations sampled from engine G, oldest first."""
        return tuple(self._right)

    @property
    def ticks(self) -> int:
        return self._tick

    @property
    def tension(self) -> float:
        """Mean squared repulsion between the engines."""
        return sum((self._a[i] - self._g[i]) ** 2 for i in range(self._dim)) / self._dim

    def _drift(self) -> None:
        """Advance both engines. Only dims 0 and 1 are driven; the rest decay,
        which keeps the observable structure in the leading dimension the
        streams are sampled from."""
        phase = self._tick * PHASE_RATE
        a, g = self._a, self._g
        random_ = self._rng.random

        for i in range(self._dim):
            a[i] += (random_() - 0.5) * WALK
            g[i] += (random_() - 0.5) * WALK

            if i == 0:
                target = self.separation * 1.3 * math.sin(phase)
            elif i == 1:
                target = self.separation * 1.0 * math.cos(phase)
            else:
                a[i] *= DAMPING
                g[i] *= DAMPING
                continue

            a[i] += (target - a[i]) * PULL
            g[i] += (-target - g[i]) * PULL

    def step(self) -> PipelineState:
        """Advance one tick: drift the engines, sample one observation from
        each, then re-measure the pair."""
        self._drift()

        self._left.append(self._a[0] + (self._rng.random() - 0.5) * OBSERVATION_NOISE)
        self._right.append(self._g[0] + (self._rng.random() - 0.5) * OBSERVATION_NOISE)

        self._tick += 1
        return self.state

    def run(self, ticks: int) -> PipelineState:
        """Advance `ticks` times and return the final state."""
        if ticks < 1:
            raise ValueError(f"ticks must be >= 1, got {ticks}")
        for _ in range(ticks - 1):
            self.step()
        return self.step()

    @property
    def state(self) -> PipelineState:
        """The current reading. Entropies stay at zero until the window holds
        enough observations to estimate them."""
        if len(self._left) < MIN_SAMPLES_FOR_METRICS:
            return PipelineState(
                tension=self.tension,
                h_left=0.0,
                h_right=0.0,
                h_joint=0.0,
                mutual_information=0.0,
                verdict=Emergence.INDEPENDENT,
            )

        h_left = entropy(self._left, self.binning)
        h_right = entropy(self._right, self.binning)
        h_joint = joint_entropy(self._left, self._right, self.binning)
        mi = max(0.0, h_left + h_right - h_joint)
        return PipelineState(
            tension=self.tension,
            h_left=h_left,
            h_right=h_right,
            h_joint=h_joint,
            mutual_information=mi,
            verdict=Emergence.classify(mi),
        )

    def reset(self) -> None:
        """Re-randomize the engines and drop the observation window."""
        self._a = self._random_vector()
        self._g = self._random_vector()
        self._left.clear()
        self._right.clear()
        self._tick = 0
