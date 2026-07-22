"""The base engine — the four engines under one clock, and the clock is mortal.

Every other engine here rotates on a free tick counter: `phase = tick *
PHASE_RATE`, a gift that never stops arriving. The base engine takes that away.
Phase becomes a state variable that only the crystal's period-2 lock can
advance, and the tick counter disappears from the drive entirely.

    TimeCrystal.step() ── verdict ──▶ phase += PHASE_RATE only while LOCKED
                                            │
                          A and G drift toward +/-(sin phase, cos phase)
                                            │
                          one noisy observation sampled from each
                                            │
                          H(L), H(R), H(L,R) -> mutual information

**The claim.** Shared information downstream is paid for in temporal order
upstream. The two streams hold emergent mutual information exactly while the
crystal's lock animates the gap between A and G. Melt the crystal and the gap
*survives* — tension stays around 0.18, the engines are still apart — but the
information in it dies. Refreeze it and the information comes back.

That corrects the pipeline's own summary. `pipeline.py` says separation is what
produces shared information; under a melted crystal separation persists at
pipeline-typical levels while mutual information reads INDEPENDENT. It is not
the gap that binds the streams, it is the *motion* of the gap — and the motion
is bought entirely by the lock.

**What is designed in, and what is not.** The gate hard-wires no-lock to
no-rotation, so "melting kills binding" is architecture, not discovery, and
should never be quoted as an emergent finding. What is genuinely contingent:
that a locked ring's rotation is *enough* to clear the emergence bar, that
binding *revives* after a melt from windows full of dead samples, and that
tension survives a melt at all — a frozen target could just as easily have let
the gap decay.

**What this engine cannot see.** Gating on the verdict quantizes temporal order
at the crystal's own pinned thresholds. Measurement showed that *sub-verdict*
order binds streams too — a ring in nominal chaos still carries enough residual
anti-correlation to rotate the target and hold mutual information above the bar
at epsilon 0.10-0.20. That continuum is real, and the gate trades it away for a
transition sharp enough to write a test against. The trade is deliberate; a
smoother coupling is not an improvement waiting to be made.

Nothing here is a new constant. Every threshold is imported from the engine it
belongs to, except `EPSILON`, which is measured and shows its work.
"""

from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass

from .crystal import CrystalState, CrystalVerdict, TimeCrystal
from .info import Binning, Emergence, entropy, joint_entropy
from .pipeline import MIN_SAMPLES_FOR_METRICS, OBSERVATION_NOISE, WALK
from .repulsion import DAMPING, PHASE_RATE, PULL

__all__ = ["BaseEngine", "BaseState"]

DIM = 8
"""Latent dimension, as `pipeline.py` — structure lives in the leading dims."""

HISTORY = 200
"""Rolling observation window, as `pipeline.py`."""

SEPARATION = 0.60
"""As `repulsion.py` and `pipeline.py`."""

EPSILON = 0.02
"""Default drive imperfection — deliberately not the crystal's own 0.05.

Measured over eight seeds at 800 ticks: 0.05 sits on the verdict's flicker
boundary, locked for about 29% of ticks with end-of-run mutual information
ranging 0.01 to 1.39 by seed alone. That regime is bistable, and any claim made
there is a claim about a seed. At 0.02 the ring locks for about 94% of ticks and
binds every time. It is also the value `tests/test_crystal.py` pins as LOCKED.
"""


@dataclass(frozen=True, slots=True)
class BaseState:
    """One tick of the whole engine.

    The crystal's reading is carried verbatim rather than summarized. There is
    deliberately no single "aliveness" number: any `f(lock, mutual_information)`
    would need invented weights and could not fail a test. The novel readout is
    the *pair* — the gap persists, the binding stopped — and that is two
    measured numbers, not one fabricated one.
    """

    crystal: CrystalState
    """The substrate's clock, exactly as the ring reported it."""
    tension: float
    """Mean squared A-G gap, >= 0. Survives a melt, which is the point."""
    phase: float
    """Accumulated target rotation in radians, >= 0. Advances only on locked
    ticks — this is the one structural change from every other engine here."""
    h_left: float
    h_right: float
    h_joint: float
    mutual_information: float
    """Bits, >= 0. Plug-in estimator, so read `info.py`'s caveat before treating
    a small value as meaningful."""
    verdict: Emergence

    def __str__(self) -> str:
        return (
            f"[{self.crystal.verdict.value}] phase={self.phase:.2f} "
            f"tension={self.tension:.3f} MI={self.mutual_information:.3f} "
            f"[{self.verdict.value}]"
        )


class BaseEngine:
    """The four engines composed under the crystal's clock.

    Args:
        epsilon: Per-spin probability the crystal's drive misses. Validated by
            the ring itself.
        separation: How hard the rotating target drives A and G apart.
        dim: Latent dimension of each engine.
        history: Rolling observation window.
        seed: Fixes the whole engine.
        binning: Histogram for the entropies. Defaults to the pipeline's.

    The embedded crystal is not exposed. Handing out the live ring would let a
    caller step it out of band and desynchronize the one clock the engine has;
    its reading arrives frozen inside `BaseState.crystal` instead.
    """

    def __init__(
        self,
        *,
        epsilon: float = EPSILON,
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

        # Two derived streams rather than one shared source: if the crystal's
        # internal draw count ever changes — a different ring size, say — the
        # field's noise must not silently reshuffle with it.
        master = random.Random(seed)
        self._crystal = TimeCrystal(
            epsilon=epsilon, seed=master.getrandbits(64)
        )
        self._rng = random.Random(master.getrandbits(64))

        self.separation = separation
        self.binning = binning or Binning(bins=12, vrange=1.6)
        self._dim = dim
        self._a = self._random_vector()
        self._g = self._random_vector()
        self._left: deque[float] = deque(maxlen=history)
        self._right: deque[float] = deque(maxlen=history)
        self._phase = 0.0
        self._tick = 0

    def _random_vector(self) -> list[float]:
        return [(self._rng.random() - 0.5) * 0.3 for _ in range(self._dim)]

    # ── controls ───────────────────────────────────────────────────────────
    @property
    def epsilon(self) -> float:
        """Delegates to the ring, so its validation is the only validation."""
        return self._crystal.epsilon

    @epsilon.setter
    def epsilon(self, value: float) -> None:
        self._crystal.epsilon = value

    # ── readouts ───────────────────────────────────────────────────────────
    @property
    def a(self) -> tuple[float, ...]:
        return tuple(self._a)

    @property
    def g(self) -> tuple[float, ...]:
        return tuple(self._g)

    @property
    def left(self) -> tuple[float, ...]:
        """Observations sampled from A, oldest first."""
        return tuple(self._left)

    @property
    def right(self) -> tuple[float, ...]:
        return tuple(self._right)

    @property
    def ticks(self) -> int:
        return self._tick

    @property
    def phase(self) -> float:
        """Radians of rotation the crystal has paid for so far."""
        return self._phase

    @property
    def magnetization(self) -> tuple[float, ...]:
        """The ring's recent magnetization, for anything that wants to draw the
        clock rather than only its effect."""
        return self._crystal.history

    @property
    def tension(self) -> float:
        """Mean squared repulsion between the engines."""
        return sum((self._a[i] - self._g[i]) ** 2 for i in range(self._dim)) / self._dim

    def _drift(self) -> None:
        """The pipeline's drift law, with accumulated phase in place of the
        tick counter. Dims 0 and 1 chase the rotating target in antiphase; the
        rest decay, keeping the observable structure where the streams read."""
        a, g = self._a, self._g
        random_ = self._rng.random

        for i in range(self._dim):
            a[i] += (random_() - 0.5) * WALK
            g[i] += (random_() - 0.5) * WALK

            if i == 0:
                target = self.separation * 1.3 * math.sin(self._phase)
            elif i == 1:
                target = self.separation * 1.0 * math.cos(self._phase)
            else:
                a[i] *= DAMPING
                g[i] *= DAMPING
                continue

            a[i] += (target - a[i]) * PULL
            g[i] += (-target - g[i]) * PULL

    def step(self) -> BaseState:
        """Advance one tick.

        Order matters: the ring moves first, its fresh verdict decides whether
        the phase advances at all, and only then do A and G chase a target at
        the new phase.
        """
        crystal = self._crystal.step()
        if crystal.verdict is CrystalVerdict.LOCKED:
            self._phase += PHASE_RATE

        self._drift()

        self._left.append(self._a[0] + (self._rng.random() - 0.5) * OBSERVATION_NOISE)
        self._right.append(self._g[0] + (self._rng.random() - 0.5) * OBSERVATION_NOISE)

        self._tick += 1
        return self._read(crystal)

    def run(self, ticks: int) -> BaseState:
        """Advance `ticks` times and return the final state."""
        if ticks < 1:
            raise ValueError(f"ticks must be >= 1, got {ticks}")
        for _ in range(ticks - 1):
            self.step()
        return self.step()

    @property
    def state(self) -> BaseState:
        """The current reading, without advancing anything."""
        return self._read(self._crystal.state)

    def _read(self, crystal: CrystalState) -> BaseState:
        if len(self._left) < MIN_SAMPLES_FOR_METRICS:
            # Tension is a property of the engines and is live from tick one;
            # the entropies need a window before they mean anything.
            return BaseState(
                crystal=crystal,
                tension=self.tension,
                phase=self._phase,
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
        return BaseState(
            crystal=crystal,
            tension=self.tension,
            phase=self._phase,
            h_left=h_left,
            h_right=h_right,
            h_joint=h_joint,
            mutual_information=mi,
            verdict=Emergence.classify(mi),
        )

    def reset(self) -> None:
        """Return everything to a fresh start, the clock included."""
        self._crystal.reset()
        self._a = self._random_vector()
        self._g = self._random_vector()
        self._left.clear()
        self._right.clear()
        self._phase = 0.0
        self._tick = 0
