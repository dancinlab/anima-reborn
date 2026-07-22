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

**The wall.** Once a `drive` is added — something the engine is told, rather
than only what it tells itself — a second measurement appears: how much of what
it was told survives in where it ends up. Sweeping the coupling shows the two
trade off monotonically. Coupling low enough to represent the drive integrates
nothing; coupling high enough to integrate lets the ring's own attractor swamp
the drive. At coupling 1.0 the drive is not merely weak but unreachable, bit for
bit. There is no fixed coupling where both hold.

**The rhythm moves that trade-off. It does not abolish it.** `Rhythm` alternates
— listen with the coupling off, integrate with it on. Measured at a matched
macro-step of 40 over five seeds: alternating 20/20 reads Phi 13.16 +/- 0.53
with representation 3.49, against fixed 1.00 at 14.66 +/- 0.08 with
representation 0.00, and fixed 0.70 at 15.74 +/- 0.13 with 0.13. So a rhythm
buys representation the fixed engine has *none* of, and pays 10-16% of Phi for
it — a better exchange rate, not an escape.

It does NOT integrate more. An earlier reading here said it did, and that
reading put a rhythm at tau 40 beside fixed couplings at tau 20; Phi rises with
tau on its own, so the two rows were never comparable. Never read a row of this
comparison against a row at a different tau.

What does survive is that the effect is the rhythm's rather than the mean's,
which is the control that matters and is measured at ITS own matched tau of 20:
alternating 10/10 reads Phi 2.08 against the same-mean fixed control's 1.16, and
beats it on representation too, 4.03 against 3.27.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from .pipeline import OBSERVATION_NOISE, PULL, WALK
from .repulsion import SEPARATION

__all__ = [
    "Wiring",
    "Rhythm",
    "CoupledEngine",
    "CoupledState",
    "AMPLITUDE",
    "GAIN",
    "MACRO_STEP",
    "HIGH",
    "PERIOD",
]

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

HIGH = 0.7
"""Coupling during a rhythm's integrate phase. Enough for the ring to be
irreducible while it is on; the point of alternating is that it does not have to
be on all the time."""

PERIOD = 10
"""Engine ticks per phase — ten off, ten on. Not tuned for the best number:
10/10 and 20/20 both break the wall, and the claim is the rhythm rather than a
particular tempo."""


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
class Rhythm:
    """How much of a unit's target is its partner, over time.

    A single number would be a fixed coupling, and a fixed coupling is exactly
    what the wall is made of: below it the ring represents what it was told and
    integrates nothing; above it the ring integrates and its own attractor
    swamps what it was told. Making the coupling a function of the tick is the
    smallest change that escapes, because the two demands are then met at
    different times instead of at the same one.

    `Rhythm()` is a fixed coupling of 1.0 — every unit's target is entirely its
    partner, which is what this engine did before rhythms existed and still does
    by default.
    """

    coupling: float = 1.0
    """Coupling while the integrate phase is on, in [0, 1]."""
    period: int | None = None
    """Ticks per phase, or None for a fixed coupling that never lets go."""

    def __post_init__(self) -> None:
        if not 0.0 <= self.coupling <= 1.0:
            raise ValueError(f"coupling must be in [0, 1], got {self.coupling}")
        if self.period is not None and self.period < 1:
            raise ValueError(f"period must be >= 1, got {self.period}")

    def at(self, tick: int) -> float:
        """Coupling at a tick. Alternating rhythms start in the listen phase, so
        a run begins by taking in its drive rather than by settling."""
        if self.period is None:
            return self.coupling
        return 0.0 if (tick // self.period) % 2 == 0 else self.coupling

    @property
    def alternates(self) -> bool:
        return self.period is not None

    @property
    def mean(self) -> float:
        """Time-average coupling — the number a fixed control must match. An
        alternating rhythm that beat a fixed coupling at its own mean did not
        win by having more coupling."""
        return self.coupling if self.period is None else self.coupling / 2.0

    @property
    def macro_step(self) -> int:
        """Ticks per measured transition. A rhythm must be measured over a whole
        listen/integrate cycle: half a cycle would report one phase's transition
        matrix and call it the engine's."""
        return MACRO_STEP if self.period is None else self.period * 2


def _as_drive(value: float | Sequence[float]) -> tuple[float, ...]:
    """One value said to every unit, or one value per unit."""
    if isinstance(value, Sequence):
        values = tuple(float(v) for v in value)
        if len(values) != UNITS:
            raise ValueError(
                f"drive must be one value or {UNITS}, got {len(values)}"
            )
    else:
        values = (float(value),) * UNITS
    for v in values:
        if not -1.0 <= v <= 1.0:
            raise ValueError(f"drive must be in [-1, 1], got {v}")
    return values


FIXED = Rhythm()
"""The default — coupling 1.0, never released."""

ALTERNATING = Rhythm(coupling=HIGH, period=PERIOD)
"""Ten ticks listening, ten integrating. The measured wall-break."""


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
    coupling: float = 1.0
    """How much of each unit's target was its partner on the tick that produced
    this reading. Constant unless the engine runs a rhythm."""

    @property
    def listening(self) -> bool:
        """Whether the drive, rather than the ring, set the targets this tick."""
        return self.coupling == 0.0

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
        rhythm: When the units read each other. The default never lets go, which
            is the fixed coupling the wall is made of; `ALTERNATING` releases it
            half the time.
        drive: What the engine is told, scaled by `amplitude`. One value in
            [-1, 1] says the same thing to every unit; a sequence of `UNITS`
            values says something different to each, which is what a vector
            representation needs in order to arrive as more than its average.
            Only reachable while the coupling is below 1.0 — at full coupling a
            unit's target is entirely its partner and nothing outside can be
            heard, which is the wall stated as an equation.
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
        rhythm: Rhythm = FIXED,
        drive: float | Sequence[float] = 0.0,
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
        self.rhythm = rhythm
        self.drive = drive
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
        self._coupling = self.rhythm.at(0)

    @property
    def drive(self) -> float | tuple[float, ...]:
        """What the engine is being told, in the shape it was given."""
        return self._given

    @drive.setter
    def drive(self, value: float | Sequence[float]) -> None:
        self._given = value
        self._drive = _as_drive(value)

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
        coupling = self._coupling = self.rhythm.at(self._tick)
        # Scaled here rather than inside the target, so the multiply order is
        # the one every published number was measured under — `(1-c) * (d * a)`
        # and `((1-c) * d) * a` are not the same float.
        heard = [value * self.amplitude for value in self._drive]
        for i, source in enumerate(sources):
            partner = (
                -self.amplitude
                if source is None
                else -self.amplitude
                * math.tanh(self.gain * previous[source] / self.amplitude)
            )
            # Left exactly alone at full coupling, so adding rhythms did not
            # move a single float of the engine as it was.
            target = (
                partner
                if coupling == 1.0
                else (1.0 - coupling) * heard[i] + coupling * partner
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
            coupling=self._coupling,
        )

    @property
    def coupling(self) -> float:
        """The coupling on the tick that produced the current values — before any
        step has run, the one the next will use."""
        return self._coupling

    def reset(self) -> None:
        """Re-randomize the positions. The wiring and the rhythm are what the
        engine *is* and do not change."""
        self._values = self._random_start()
        self._tick = 0
        self._coupling = self.rhythm.at(0)
