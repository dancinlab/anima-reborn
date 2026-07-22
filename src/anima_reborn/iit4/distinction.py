"""M2 — small-phi, the maximally irreducible purview, and distinctions.

A mechanism earns a *distinction* when it says something about the system that
it could not say if it were cut apart. Measuring that takes three steps, in one
direction (cause or effect) at a time:

1. Take the mechanism's repertoire over a purview, and the unconstrained
   reference. Their intrinsic difference gives how much the mechanism informs,
   and which purview state it specifies — call it `z*`.
2. Cut the mechanism and the purview into two parts, each part constraining only
   its own half. That severed version is a partitioned repertoire.
3. small-phi is the *smallest* loss any such cut produces, measured at `z*` and
   nowhere else. The cut that costs least is the mechanism's minimum-information
   partition — its weakest link, and therefore what its integration is worth.

If step 1 says the mechanism informs nothing, small-phi is zero and there is no
distinction to find.

The **maximally irreducible cause/effect** is then the purview that maximizes
small-phi, and the distinction's `phi_d` is the *smaller* of the cause and
effect sides — a mechanism is only as integrated as its weaker direction.

Partition scheme, stated plainly because it is a real carve-out: this takes all
bipartitions of mechanism-and-purview, the standard tractable scheme, not IIT
4.0's own partition set. The origin flags the same gap.

Ported from `dancinlab/selfhost-work` `stdlib/consciousness/iit4_distinction.hexa`.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from .tpm import (
    P_FLOOR,
    Q_SMOOTHING,
    TransitionMatrix,
    compact_index,
    expand,
    intrinsic_difference,
    units_of,
)

__all__ = ["Direction", "Mice", "Distinction", "small_phi", "mice", "distinction", "distinctions"]

_LN2 = math.log(2.0)

PHI_EPSILON = 1.0e-9
"""Below this a phi counts as zero. Origin uses 1e-9 for existence tests."""


class Direction(Enum):
    """Which way in time a repertoire looks."""

    CAUSE = "cause"
    EFFECT = "effect"


@dataclass(frozen=True, slots=True)
class Mice:
    """A mechanism's maximally irreducible cause or effect.

    Origin: `mice_cause` / `mice_effect`.
    """

    phi: float
    """small-phi over the winning purview, in bits. Never negative."""
    purview: int
    """Bitmask of the units the mechanism speaks about most irreducibly."""
    state: int
    """The purview state it specifies, as a compact index over that purview."""
    direction: Direction


@dataclass(frozen=True, slots=True)
class Distinction:
    """One mechanism's irreducible contribution to the system.

    It exists — it is a distinction at all — only when `phi > 0`.
    Origin: `distinction`.
    """

    mechanism: int
    """Bitmask of the units forming the mechanism."""
    phi: float
    """min(cause phi, effect phi), in bits. A mechanism is only as integrated as
    its weaker direction."""
    cause: Mice
    effect: Mice

    @property
    def exists(self) -> bool:
        return self.phi > PHI_EPSILON

    def involves(self, unit: int) -> bool:
        """Whether a unit appears anywhere in the distinction — in the
        mechanism or in either purview. This is what a system cut has to keep
        on one side for the distinction to survive it."""
        bit = 1 << unit
        return bool(
            self.mechanism & bit or self.cause.purview & bit or self.effect.purview & bit
        )

    def __str__(self) -> str:
        return (
            f"mechanism={self.mechanism:b} phi={self.phi:.6f} "
            f"cause={self.cause.purview:b}@{self.cause.state} "
            f"effect={self.effect.purview:b}@{self.effect.state}"
        )


def _phi_at(p: Sequence[float], q: Sequence[float], state: int) -> float:
    """The divergence at one fixed state, floored at zero.

    small-phi is evaluated only at the state the unpartitioned repertoire
    specified — a partition is judged on what it does to *that* claim, not on
    how it rearranges the rest. Origin: `iit4_phi_at`.
    """
    px = p[state]
    if px <= P_FLOOR:
        return 0.0
    phi = px * (math.log(px) - math.log(q[state] + Q_SMOOTHING)) / _LN2
    return max(0.0, phi)


def _partitioned_effect(
    matrix: TransitionMatrix,
    mechanism_state: int,
    part_a: tuple[int, int],
    part_b: tuple[int, int],
    purview: int,
) -> tuple[float, ...]:
    """Effect repertoire with the two halves constraining only their own.

    Each part is `(mechanism_part, purview_part)`. A purview unit takes its
    marginal under whichever mechanism part it was paired with, so the crossing
    connections are gone. An empty mechanism part leaves its purview part
    unconstrained. Origin: `iit4_partitioned_effect`.
    """
    mech_a, purview_a = part_a
    mech_b, _ = part_b
    on = []
    for unit in units_of(purview, matrix.n):
        owner = mech_a if purview_a >> unit & 1 else mech_b
        on.append(matrix.marginal_on(owner, mechanism_state, unit))

    count = 1 << len(on)
    out = []
    for compact in range(count):
        probability = 1.0
        for bit, p in enumerate(on):
            probability *= p if compact >> bit & 1 else 1.0 - p
        out.append(probability)
    return tuple(out)


def _partitioned_cause(
    matrix: TransitionMatrix,
    mechanism_state: int,
    part_a: tuple[int, int],
    part_b: tuple[int, int],
    purview: int,
) -> tuple[float, ...]:
    """Cause repertoire as the product of the two parts', reindexed onto the
    whole purview. Origin: `iit4_partitioned_cause`."""

    def part(mechanism: int, purview_part: int) -> tuple[float, ...]:
        if mechanism == 0:
            return matrix.unconstrained_cause(purview_part)
        return matrix.cause_repertoire(mechanism, mechanism_state, purview_part)

    left = part(*part_a)
    right = part(*part_b)
    purview_units = units_of(purview, matrix.n)
    left_units = units_of(part_a[1], matrix.n)
    right_units = units_of(part_b[1], matrix.n)

    out = []
    for compact in range(1 << len(purview_units)):
        absolute = expand(compact, purview_units)
        out.append(
            left[compact_index(absolute, left_units)]
            * right[compact_index(absolute, right_units)]
        )
    return tuple(out)


def small_phi(
    matrix: TransitionMatrix,
    mechanism: int,
    mechanism_state: int,
    purview: int,
    direction: Direction,
) -> tuple[float, int]:
    """Integrated information of one mechanism over one purview, in bits.

    Returns `(phi, specified_state)`. Origin: `small_phi_cause` /
    `small_phi_effect`.
    """
    if direction is Direction.EFFECT:
        p = matrix.effect_repertoire(mechanism, mechanism_state, purview)
        reference = matrix.unconstrained_effect(purview)
        partitioned = _partitioned_effect
    else:
        p = matrix.cause_repertoire(mechanism, mechanism_state, purview)
        reference = matrix.unconstrained_cause(purview)
        partitioned = _partitioned_cause

    informativeness = intrinsic_difference(p, reference)
    if informativeness.value <= P_FLOOR:
        # The mechanism adds nothing over the reference, so there is no claim
        # for a partition to damage.
        return 0.0, informativeness.state

    specified = informativeness.state
    mechanism_units = units_of(mechanism, matrix.n)
    purview_units = units_of(purview, matrix.n)

    minimum = math.inf
    for mech_choice in range(1 << len(mechanism_units)):
        mech_a = expand(mech_choice, mechanism_units)
        mech_b = mechanism - mech_a
        for purview_choice in range(1 << len(purview_units)):
            purview_a = expand(purview_choice, purview_units)
            purview_b = purview - purview_a
            # The two identities cut nothing, so they would trivially win.
            if (mech_a == mechanism and purview_a == purview) or (
                mech_a == 0 and purview_a == 0
            ):
                continue
            q = partitioned(
                matrix,
                mechanism_state,
                (mech_a, purview_a),
                (mech_b, purview_b),
                purview,
            )
            minimum = min(minimum, _phi_at(p, q, specified))

    return (0.0 if minimum is math.inf else minimum), specified


def mice(
    matrix: TransitionMatrix,
    mechanism: int,
    mechanism_state: int,
    direction: Direction,
) -> Mice:
    """The purview over which the mechanism is most irreducible.

    Every non-empty purview is tried; ties keep the lowest mask, since the scan
    ascends and the comparison is strict. Origin: `mice_cause` / `mice_effect`.
    """
    best_phi = -1.0
    best_purview = 0
    best_state = 0
    for purview in range(1, 1 << matrix.n):
        phi, state = small_phi(matrix, mechanism, mechanism_state, purview, direction)
        if phi > best_phi:
            best_phi, best_purview, best_state = phi, purview, state
    return Mice(
        phi=best_phi, purview=best_purview, state=best_state, direction=direction
    )


def distinction(
    matrix: TransitionMatrix, mechanism: int, system_state: int
) -> Distinction:
    """One mechanism's distinction. Origin: `distinction`."""
    cause = mice(matrix, mechanism, system_state, Direction.CAUSE)
    effect = mice(matrix, mechanism, system_state, Direction.EFFECT)
    return Distinction(
        mechanism=mechanism,
        phi=min(cause.phi, effect.phi),
        cause=cause,
        effect=effect,
    )


def distinctions(
    matrix: TransitionMatrix, system_state: int
) -> tuple[Distinction, ...]:
    """Every mechanism that exists as a distinction, by ascending mask.

    Origin: the collection loop shared by `count_distinctions`, `phi_structure`
    and `big_phi`.
    """
    return tuple(
        found
        for mask in range(1, 1 << matrix.n)
        if (found := distinction(matrix, mask, system_state)).exists
    )
