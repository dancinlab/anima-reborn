"""A x G — the repulsion field between two engines.

Two latent vectors, A and G, are pushed apart by a slowly rotating target: A is
pulled toward it, G toward its negative. What the substrate reads off is never
either vector on its own, only the gap between them.

    repulsion = A - G
    tension   = |A - G|^2 / dim      how hard the engines are pushing apart
    concept   = repulsion / |repulsion|   the direction of the disagreement
    meaning   = A * G                elementwise, where they overlap despite it

Tension near zero is not calm — it is the engines having collapsed onto each
other, with no gap left to think in. The mood readout calls that `quiet`.

Ported from the A x G engine in `dancinlab/anima-experience` `index.html`; the
mood thresholds are `tension_link.py`'s, carried over verbatim.

The original holds A and G in `Float32Array`s while this port uses Python
floats (double precision). The trajectories are noise-driven, so the difference
is not observable in any statistic here, but the two will not agree digit for
digit.
"""

from __future__ import annotations

import math
import random
import time
from collections import deque
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum

__all__ = ["Mood", "RepulsionField", "RepulsionState"]

DIM = 16
"""Latent dimension of each engine."""

SEPARATION = 0.60
"""How far apart the rotating target drives the two engines."""

NOISE = 0.20
"""Scale of the per-dimension random walk."""

AUTHENTICITY_WINDOW = 30
"""Tension samples behind the authenticity estimate."""

PHASE_RATE = 0.025
"""Radians per tick of the target's rotation."""

PULL = 0.06
"""How fast dims 0-1 chase their target."""

MID_PULL = 0.04
"""How fast dims 2-3 chase theirs."""

DAMPING = 0.985
"""Per-tick decay of the dims that have no target — a slow drift home."""

SECONDS_PER_DAY = 86400


class Mood(Enum):
    """A coarse read on what the tension field is doing.

    Thresholds are `tension_link.py`'s. Order matters: a curiosity spike wins
    over any tension level, because a sudden change in tension says more about
    the moment than its absolute size does.
    """

    SURPRISED = "surprised"
    """Tension jumped this tick."""
    EXCITED = "excited"
    """Sustained high tension."""
    THOUGHTFUL = "thoughtful"
    CALM = "calm"
    QUIET = "quiet"
    """Tension near zero — the engines have collapsed together and there is no
    gap left to think in."""

    @classmethod
    def classify(cls, tension: float, curiosity: float) -> Mood:
        if curiosity > 0.5:
            return cls.SURPRISED
        if tension > 1.0:
            return cls.EXCITED
        if tension > 0.3:
            return cls.THOUGHTFUL
        if tension > 0.05:
            return cls.CALM
        return cls.QUIET


@dataclass(frozen=True, slots=True)
class RepulsionState:
    """Everything one tick of the field says."""

    tension: float
    """Mean squared repulsion, >= 0."""
    concept: tuple[float, ...]
    """Unit vector along the disagreement — what the engines differ *about*."""
    meaning: tuple[float, ...]
    """Elementwise A * G — where they overlap in spite of the repulsion."""
    topic: int
    """Index of the concept's dominant axis."""
    curiosity: float
    """Absolute change in tension since the previous tick."""
    mood: Mood
    authenticity: float
    """1 minus recent tension volatility, clamped to [0, 1]. High means the
    field is holding a steady stance rather than thrashing."""
    context: tuple[float, ...]
    """Eight-channel context vector; see `RepulsionField.step`."""
    sender: tuple[float, ...]
    """Four-channel engine signature — a fingerprint of the current A/G pair,
    carried so downstream consumers can tell one field from another."""

    def __str__(self) -> str:
        return (
            f"tension={self.tension:.3f} topic=#{self.topic} "
            f"auth={self.authenticity:.3f} mood={self.mood.value}"
        )


class RepulsionField:
    """Two latent engines held apart, and the channels read off the gap.

    Args:
        dim: Latent dimension. Must be at least 4 — dims 0-3 have distinct
            roles in the drive.
        separation: Strength of the target that pushes A and G apart.
        noise: Scale of the random walk on every dimension.
        seed: Fixes the initial vectors and the walk.
        clock: Source of wall-clock seconds for the circadian context channel.
            Injectable so a run can be made deterministic.
        initial: Starting (A, G) vectors. Defaults to a random pair. Pass an
            explicit one to resume a known configuration; `reset` re-randomizes
            regardless.
    """

    def __init__(
        self,
        *,
        dim: int = DIM,
        separation: float = SEPARATION,
        noise: float = NOISE,
        seed: int | None = None,
        clock: Callable[[], float] = time.time,
        initial: tuple[Sequence[float], Sequence[float]] | None = None,
    ) -> None:
        if dim < 4:
            raise ValueError(f"dim must be >= 4, got {dim}")
        self.separation = separation
        self.noise = noise
        self._dim = dim
        self._rng = random.Random(seed)
        self._clock = clock
        if initial is None:
            self._a = self._random_vector()
            self._g = self._random_vector()
        else:
            self._a, self._g = (self._checked(v, name) for v, name in
                                zip(initial, ("initial A", "initial G")))
        self._tension_history: deque[float] = deque(maxlen=AUTHENTICITY_WINDOW)
        self._previous_tension = 0.0
        self._tick = 0
        self._state: RepulsionState | None = None

    def _random_vector(self) -> list[float]:
        return [(self._rng.random() - 0.5) * 0.4 for _ in range(self._dim)]

    def _checked(self, vector: Sequence[float], name: str) -> list[float]:
        if len(vector) != self._dim:
            raise ValueError(
                f"{name} must have {self._dim} entries, got {len(vector)}"
            )
        return [float(v) for v in vector]

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def a(self) -> tuple[float, ...]:
        """Engine A's latent vector."""
        return tuple(self._a)

    @property
    def g(self) -> tuple[float, ...]:
        """Engine G's latent vector."""
        return tuple(self._g)

    @property
    def ticks(self) -> int:
        return self._tick

    def _drift(self) -> None:
        """Advance both engines one tick.

        Dims 0 and 1 track a rotating target in antiphase — this is the drive
        that keeps the engines apart. Dims 2 and 3 track a slower, weaker one.
        Everything above that is left to decay, so the field's structure stays
        in its low dimensions.
        """
        phase = self._tick * PHASE_RATE
        a, g = self._a, self._g
        walk = self.noise * 0.06
        random_ = self._rng.random

        for i in range(self._dim):
            a[i] += (random_() - 0.5) * walk
            g[i] += (random_() - 0.5) * walk

            if i == 0:
                target = self.separation * 1.3 * math.sin(phase)
                rate = PULL
            elif i == 1:
                target = self.separation * 1.0 * math.cos(phase)
                rate = PULL
            elif i in (2, 3):
                target = self.separation * 0.6 * math.sin(phase * 1.7 + i)
                rate = MID_PULL
            else:
                a[i] *= DAMPING
                g[i] *= DAMPING
                continue

            a[i] += (target - a[i]) * rate
            g[i] += (-target - g[i]) * rate

    def _authenticity(self, tension: float) -> tuple[float, float]:
        """Update the tension window and return (authenticity, window mean).

        Authenticity is one minus the window's standard deviation, doubled and
        clamped — a field whose tension swings wildly reads as inauthentic.
        """
        self._tension_history.append(tension)
        window = self._tension_history
        mean = sum(window) / len(window)
        variance = sum((v - mean) ** 2 for v in window) / len(window)
        authenticity = max(0.0, min(1.0, 1.0 - math.sqrt(variance) * 2.0))
        return authenticity, mean

    def step(self) -> RepulsionState:
        """Advance one tick and read every channel off the new gap.

        The eight context channels are, in order: circadian position, curiosity,
        tension, mean recent tension, curiosity relative to tension, how full
        the authenticity window is, and two channels left at zero — the
        original reserves them without feeding them.
        """
        self._drift()

        repulsion = [self._a[i] - self._g[i] for i in range(self._dim)]
        squared = sum(r * r for r in repulsion)
        tension = squared / self._dim

        # A collapsed field has no direction; fall back to 1.0 so `concept`
        # stays all-zero instead of dividing by nothing.
        norm = math.sqrt(squared) or 1.0
        concept = tuple(r / norm for r in repulsion)
        meaning = tuple(self._a[i] * self._g[i] for i in range(self._dim))

        topic = max(range(self._dim), key=lambda i: abs(concept[i]))

        curiosity = abs(tension - self._previous_tension)
        self._previous_tension = tension

        authenticity, mean_tension = self._authenticity(tension)

        now = self._clock()
        context = (
            math.sin(2.0 * math.pi * (now % SECONDS_PER_DAY) / SECONDS_PER_DAY),
            curiosity,
            tension,
            mean_tension,
            curiosity / max(tension, 0.01),
            min(1.0, len(self._tension_history) / AUTHENTICITY_WINDOW),
            0.0,
            0.0,
        )

        sender = (
            abs(self._a[0]) * 7 % 1,
            abs(self._g[0]) * 11 % 1,
            abs(self._a[0] * self._g[0]) * 13 % 1,
            abs(tension) * 17 % 1,
        )

        self._tick += 1

        self._state = RepulsionState(
            tension=tension,
            concept=concept,
            meaning=meaning,
            topic=topic,
            curiosity=curiosity,
            mood=Mood.classify(tension, curiosity),
            authenticity=authenticity,
            context=context,
            sender=sender,
        )
        return self._state

    @property
    def state(self) -> RepulsionState | None:
        """The most recent reading, or None before the first tick.

        Reading is free — unlike `step`, this does not advance the field. The
        channels are derived per tick rather than from standing state, so there
        is nothing to report until the field has moved at least once.
        """
        return self._state

    def run(self, ticks: int) -> RepulsionState:
        """Advance `ticks` times and return the final state."""
        if ticks < 1:
            raise ValueError(f"ticks must be >= 1, got {ticks}")
        for _ in range(ticks - 1):
            self.step()
        return self.step()

    def reset(self) -> None:
        """Re-randomize both engines and drop all history."""
        self._a = self._random_vector()
        self._g = self._random_vector()
        self._tension_history.clear()
        self._previous_tension = 0.0
        self._tick = 0
        self._state = None
