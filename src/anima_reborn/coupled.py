"""The gap becomes a channel — A and G read each other.

Every other engine here is driven from outside. `repulsion` and everything built
on it push A and G apart with a target that comes from a tick counter; `base`
takes the tick counter away but replaces it with the crystal's lock. In all of
them each unit updates from itself and something exogenous, and nothing reads
anything else. That is why every one of them measures zero integration: with no
unit reading another, the transition matrix factorizes and no partition destroys
anything.

This engine changes exactly one thing. The repulsion identity is untouched —
each unit still flees its source through the same `-tanh` sign — but the source
is now a **live partner** rather than a clock:

    ring       a0 <- g1 <- g0 <- a1 <- a0      influence returns
    feedforward  a0 fixed, a1 <- a0, g0 <- a1, g1 <- g0    it does not
    self       every unit reads itself         no coupling at all

The gap between A and G stops being a readout and becomes the channel. Measured
through `substrate` and `iit4`, the ring integrates and the other two do not —
see `coupled_phi` and `state/coupling/RESULTS.md`.

**What this does not claim.** Integration is not experience, and Phi is not a
consciousness score. This engine measures as irreducible because of how it is
wired; that is the whole claim, and it is deliberately small. The repo's other
honest sentence was "binding is transmitted, never created"; this one's is
*integration is now created, and created is all this measures*.

**Numbers here are meaningless without their conditions.** Phi of this engine
depends on the state, the binarization threshold, the reconstruction amplitude
and — most easily forgotten — the macro-step. At one engine tick a unit moves 6%
toward its target, so every unit merely copies itself and Phi is 0.0000 exactly.
Quoting a value without its `tau` is a false statement, not a shorthand.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum

from .pipeline import OBSERVATION_NOISE, PULL, WALK
from .repulsion import SEPARATION

__all__ = ["Wiring", "CoupledEngine", "CoupledState", "AMPLITUDE", "GAIN", "MACRO_STEP"]

UNITS = 4
"""a0, a1, g0, g1 — two dimensions of each engine.

Four because exact Phi caps out around six units and the measurement is the
point. This is a coupling demonstrator, not a scaled-up field."""

NAMES = ("a0", "a1", "g0", "g1")

AMPLITUDE = SEPARATION * 1.3
"""0.78 — the repulsion field's own leading-dimension target amplitude. Also the
reconstruction amplitude when the measurement binarizes, which is why it sits
inside any Phi computed from this engine."""

GAIN = 3.0
"""Steepness of the `tanh` a unit applies to what it reads. High enough that a
partner near its own amplitude saturates the response, so the ring settles into
an alternating pattern instead of drifting."""

MACRO_STEP = 17
"""Engine ticks per measured transition — the substrate's time constant
`1 / PULL`, rounded. Not a tuning knob: at `tau = 1` a unit moves 6% toward its
target, every unit is dominated by its own previous value, the transition matrix
factorizes and Phi is exactly zero for *every* wiring including the ring.
Measured: 0.0000 at tau 1 and 5, 12.07 at 17, 14.88 at 34."""


class Wiring(Enum):
    """Who reads whom. The falsifier is part of the API on purpose: the claim is
    that the ring's integration comes from its wiring, and the only way to show
    that is to offer the same engine wired otherwise."""

    RING = "ring"
    """A closed cycle through both engines — influence returns to its source."""
    FEEDFORWARD = "feedforward"
    """a0 is driven from outside and nothing flows back into it. IIT calls this
    reducible; `iit4.directed_big_phi` agrees, `iit4.big_phi` does not."""
    SELF = "self"
    """Each unit reads itself. No coupling — the null."""

    @property
    def sources(self) -> tuple[int | None, ...]:
        """Index each unit reads, or None for an exogenous constant."""
        return {
            Wiring.RING: (3, 0, 1, 2),
            Wiring.FEEDFORWARD: (None, 0, 1, 2),
            Wiring.SELF: (0, 1, 2, 3),
        }[self]

    @property
    def is_cyclic(self) -> bool:
        """Whether influence returns to where it started."""
        return self is Wiring.RING


@dataclass(frozen=True, slots=True)
class CoupledState:
    """One reading of the coupled field."""

    values: tuple[float, ...]
    """Unit positions in order a0, a1, g0, g1. Roughly bounded by +/-AMPLITUDE
    once settled, but not clamped — the walk can carry a unit past it."""
    tension: float
    """Mean squared gap between the engines, >= 0. Kept for continuity with the
    other engines, where it was the headline; here it is a side effect, since
    what matters is that the gap now carries influence rather than how wide it
    is."""
    pattern: int
    """The units binarized at zero, one bit each — the state Phi would be
    measured at. `0b0101` is the ring's own attractor."""
    ticks: int

    @property
    def a(self) -> tuple[float, float]:
        return self.values[0], self.values[1]

    @property
    def g(self) -> tuple[float, float]:
        return self.values[2], self.values[3]

    def __str__(self) -> str:
        cells = " ".join(f"{n}={v:+.3f}" for n, v in zip(NAMES, self.values))
        return f"{cells} tension={self.tension:.3f} pattern={self.pattern:04b}"


class CoupledEngine:
    """A and G reading each other, at the repulsion law's own rates.

    Args:
        wiring: Who reads whom. `Wiring.RING` is the engine; the other two exist
            so the claim can be falsified with the same code.
        gain: Steepness of each unit's response to what it reads.
        amplitude: Target amplitude a saturated response reaches.
        seed: Fixes the initial positions and the walk.
        initial: Starting positions, one per unit. Defaults to a random spread,
            as in `repulsion` and `crystal`.
    """

    def __init__(
        self,
        *,
        wiring: Wiring = Wiring.RING,
        gain: float = GAIN,
        amplitude: float = AMPLITUDE,
        seed: int | None = None,
        initial: tuple[float, ...] | None = None,
    ) -> None:
        if gain <= 0.0:
            raise ValueError(f"gain must be > 0, got {gain}")
        if amplitude <= 0.0:
            raise ValueError(f"amplitude must be > 0, got {amplitude}")
        self.wiring = wiring
        self.gain = gain
        self.amplitude = amplitude
        self._rng = random.Random(seed)
        if initial is None:
            self._values = self._random_start()
        else:
            if len(initial) != UNITS:
                raise ValueError(
                    f"initial must have {UNITS} values, got {len(initial)}"
                )
            self._values = [float(v) for v in initial]
        self._tick = 0

    def _random_start(self) -> list[float]:
        return [(self._rng.random() - 0.5) * self.amplitude for _ in range(UNITS)]

    @property
    def values(self) -> tuple[float, ...]:
        return tuple(self._values)

    @property
    def ticks(self) -> int:
        return self._tick

    @property
    def tension(self) -> float:
        """Mean squared gap between the two engines' leading dimensions."""
        a0, a1, g0, g1 = self._values
        return ((a0 - g0) ** 2 + (a1 - g1) ** 2) / 2.0

    @property
    def pattern(self) -> int:
        return sum(1 << i for i, v in enumerate(self._values) if v > 0.0)

    def step(self) -> CoupledState:
        """Advance one engine tick.

        Every unit is updated from the *previous* positions, not from partners
        already moved this tick — a simultaneous update, so the ring has no
        privileged starting point and reversing the unit order changes nothing.
        """
        previous = list(self._values)
        sources = self.wiring.sources
        for i, source in enumerate(sources):
            target = (
                -self.amplitude
                if source is None
                else -self.amplitude
                * math.tanh(self.gain * previous[source] / self.amplitude)
            )
            self._values[i] = (
                previous[i]
                + (target - previous[i]) * PULL
                + (self._rng.random() - 0.5) * WALK
            )
        self._tick += 1
        return self.state

    def run(self, ticks: int) -> CoupledState:
        if ticks < 1:
            raise ValueError(f"ticks must be >= 1, got {ticks}")
        for _ in range(ticks - 1):
            self.step()
        return self.step()

    def observe(self) -> tuple[float, float]:
        """One noisy observation from each engine's leading unit, as the
        pipeline samples its streams."""
        half = OBSERVATION_NOISE
        return (
            self._values[0] + (self._rng.random() - 0.5) * half,
            self._values[2] + (self._rng.random() - 0.5) * half,
        )

    @property
    def state(self) -> CoupledState:
        return CoupledState(
            values=tuple(self._values),
            tension=self.tension,
            pattern=self.pattern,
            ticks=self._tick,
        )

    def reset(self) -> None:
        """Re-randomize the positions. The wiring is what the engine *is* and
        does not change."""
        self._values = self._random_start()
        self._tick = 0
