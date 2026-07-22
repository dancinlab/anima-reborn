"""M1 — the transition matrix, the repertoires, and intrinsic difference.

Everything above this module is built from three ideas defined here.

**The transition matrix.** A system of `n` binary units is described by
`P(unit is ON next | the whole system is in state s)`. IIT 4.0 assumes the units
update conditionally independently given the current state, so one probability
per (state, unit) pair is enough — a state-by-node matrix rather than a full
2^n x 2^n joint.

**The repertoires.** Fix a *mechanism* (a subset of units, in its current state)
and ask what it says about a *purview* (another subset).

    effect repertoire  p(purview next  | mechanism now)  — what it predicts
    cause  repertoire  p(purview before | mechanism now)  — what it remembers

Units outside the constraint are averaged over uniformly, which is IIT's way of
saying "assume nothing about them". The cause direction is Bayes with a uniform
prior over the past.

**Intrinsic difference.** IIT 4.0's break from 3.0. Instead of summing a
divergence over all states, take the single largest pointwise term:

    ID(p || q) = max_x  p(x) * log2( p(x) / q(x) )

The maximizing `x` is the state the mechanism *specifies* — a distinction is
about one particular state, not a spread over all of them. Ties go to the lowest
index, which is what makes a run reproducible.

Ported from `dancinlab/selfhost-work` `stdlib/consciousness/iit4_tpm.hexa`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from collections.abc import Sequence

__all__ = [
    "TransitionMatrix",
    "IntrinsicDifference",
    "intrinsic_difference",
    "units_of",
    "expand",
    "compact_index",
]

_LN2 = math.log(2.0)
"""log2 is computed as `(log p - log q) / log 2` rather than with `math.log2`.
The two differ in the last bits, and the origin used this form — since intrinsic
difference is an argmax, a changed last bit can move the specified state."""

Q_SMOOTHING = 1.0e-10
"""Added to the reference distribution so a zero there is a large finite ratio
rather than an infinity. Origin: iit4_tpm.hexa:232."""

P_FLOOR = 1.0e-12
"""Below this a probability contributes nothing: p*log(p) -> 0 as p -> 0."""


def units_of(mask: int, n: int) -> tuple[int, ...]:
    """The unit indices set in `mask`, ascending. Origin: `iit4_units`."""
    return tuple(i for i in range(n) if mask >> i & 1)


def expand(compact: int, units: Sequence[int]) -> int:
    """Lift a purview-local state onto absolute unit positions.

    Bit `b` of `compact` is the state of `units[b]`. Origin: `iit4_expand`.
    """
    absolute = 0
    for bit, unit in enumerate(units):
        if compact >> bit & 1:
            absolute |= 1 << unit
    return absolute


def compact_index(absolute: int, units: Sequence[int]) -> int:
    """The inverse of `expand`. Origin: `iit4_compact_index`."""
    index = 0
    for bit, unit in enumerate(units):
        if absolute >> unit & 1:
            index |= 1 << bit
    return index


@dataclass(frozen=True, slots=True)
class IntrinsicDifference:
    """The largest pointwise divergence term, and where it occurred."""

    value: float
    """In bits. Zero or negative means the mechanism says nothing beyond the
    reference."""
    state: int
    """The purview state the mechanism specifies — the argmax, ties to the
    lowest index."""


def intrinsic_difference(
    p: Sequence[float], q: Sequence[float]
) -> IntrinsicDifference:
    """max_x p(x) log2(p(x)/q(x)). Origin: `intrinsic_difference`."""
    best_value = -1.0e308
    best_state = 0
    for state, px in enumerate(p):
        term = 0.0
        if px > P_FLOOR:
            term = px * (math.log(px) - math.log(q[state] + Q_SMOOTHING)) / _LN2
        if term > best_value:  # strict: the first maximizer keeps the slot
            best_value = term
            best_state = state
    return IntrinsicDifference(value=best_value, state=best_state)


class TransitionMatrix:
    """A state-by-node transition matrix over `n` binary units.

    `probability(state, unit)` is P(unit is ON at t+1 | system state is `state`
    at t). A state encodes unit `i` in bit `i`, 0 for OFF and 1 for ON.

    Marginals are memoized. Every measurement above this module asks for the
    same marginals over and over — the same purview under the same constraint
    recurs across partitions, mechanisms and subsystems — and the cache is what
    makes anything past n = 3 finish. It changes no result: `marginal_on` is a
    pure function of the matrix, which never changes after construction.
    """

    __slots__ = ("n", "_values", "_states", "_cache")

    def __init__(self, values: Sequence[float], n: int) -> None:
        """Build from a flat row-major sequence, `values[state * n + unit]`."""
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n}")
        states = 1 << n
        if len(values) != states * n:
            raise ValueError(
                f"a {n}-unit matrix needs {states * n} entries, got {len(values)}"
            )
        for i, v in enumerate(values):
            if not 0.0 <= v <= 1.0:
                raise ValueError(
                    f"entry {i} is {v}; every entry is a probability in [0, 1]"
                )
        self.n = n
        self._states = states
        self._values = tuple(float(v) for v in values)
        self._cache: dict[tuple[int, int, int], float] = {}

    @classmethod
    def from_rows(cls, rows: Sequence[Sequence[float]]) -> TransitionMatrix:
        """Build from one row per state: `rows[state][unit]`."""
        if not rows:
            raise ValueError("need at least one row")
        n = len(rows[0])
        if any(len(row) != n for row in rows):
            raise ValueError("every row must name the same units")
        if len(rows) != 1 << n:
            raise ValueError(
                f"{n} units need {1 << n} rows, got {len(rows)}"
            )
        return cls([v for row in rows for v in row], n)

    @property
    def states(self) -> int:
        """How many system states there are — 2^n."""
        return self._states

    @property
    def values(self) -> tuple[float, ...]:
        return self._values

    def probability(self, state: int, unit: int) -> float:
        """P(unit ON at t+1 | system in `state`). Origin: `tpm_on`."""
        return self._values[state * self.n + unit]

    def marginal_on(self, fix_mask: int, fix_state: int, target: int) -> float:
        """P(target ON next), averaging over every unit not in `fix_mask`.

        The units named by `fix_mask` are pinned to their values in `fix_state`;
        the rest are averaged with equal weight, which is IIT's maximum-entropy
        way of declining to assume anything about them. `fix_mask = 0` gives the
        unconstrained marginal. Origin: `iit4_marginal_on`.
        """
        # Only the low n bits name real units, and only the pinned bits of
        # `fix_state` matter — normalizing both keeps the cache from splitting
        # one marginal across several keys, and matches the origin, which
        # compares bit by bit over [0, n) alone.
        fix_mask &= self._states - 1
        pinned = fix_state & fix_mask
        key = (fix_mask, pinned, target)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        total = 0.0
        count = 0
        for state in range(self._states):
            if state & fix_mask == pinned:
                total += self._values[state * self.n + target]
                count += 1
        result = total / count if count else 0.0
        self._cache[key] = result
        return result

    def effect_repertoire(
        self, mechanism: int, mechanism_state: int, purview: int
    ) -> tuple[float, ...]:
        """What the mechanism says the purview will be. Origin:
        `effect_repertoire`."""
        units = units_of(purview, self.n)
        on = [
            self.marginal_on(mechanism, mechanism_state, unit) for unit in units
        ]
        return _product_distribution(on)

    def cause_repertoire(
        self, mechanism: int, mechanism_state: int, purview: int
    ) -> tuple[float, ...]:
        """What the mechanism says the purview was.

        Bayes with a uniform prior: for each candidate past purview state, how
        likely was it to leave the mechanism in the state it is now.
        Origin: `cause_repertoire`.
        """
        purview_units = units_of(purview, self.n)
        mechanism_units = units_of(mechanism, self.n)
        count = 1 << len(purview_units)

        likelihood = []
        total = 0.0
        for compact in range(count):
            past = expand(compact, purview_units)
            weight = 1.0
            for unit in mechanism_units:
                on = self.marginal_on(purview, past, unit)
                weight *= on if mechanism_state >> unit & 1 else 1.0 - on
            likelihood.append(weight)
            total += weight

        if total <= 0.0:
            # Nothing could have produced this state. Uniform is the honest
            # answer: the mechanism singles out no past at all.
            return (1.0 / count,) * count
        return tuple(w / total for w in likelihood)

    def unconstrained_effect(self, purview: int) -> tuple[float, ...]:
        """The purview's own marginal, with no mechanism constraining it."""
        return self.effect_repertoire(0, 0, purview)

    def unconstrained_cause(self, purview: int) -> tuple[float, ...]:
        """Uniform — the prior over the past, before any mechanism speaks."""
        count = 1 << len(units_of(purview, self.n))
        return (1.0 / count,) * count

    def __repr__(self) -> str:
        return f"TransitionMatrix(n={self.n}, states={self._states})"


def _product_distribution(on: Sequence[float]) -> tuple[float, ...]:
    """Joint over independent binary units from their ON probabilities."""
    count = 1 << len(on)
    out = []
    for compact in range(count):
        probability = 1.0
        for bit, p in enumerate(on):
            probability *= p if compact >> bit & 1 else 1.0 - p
        out.append(probability)
    return tuple(out)
