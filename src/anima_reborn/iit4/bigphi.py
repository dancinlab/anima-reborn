"""M4 — system big-Phi: what the kindest cut still destroys.

Cut the system in two. A distinction survives only if everything it involves —
its mechanism and both purviews — lands on one side; a distinction that reaches
across the cut depended on a connection that is now gone. A relation survives
only if both its distinctions survive *on the same side*.

    loss(cut) = total - (what survived it)
    big-Phi   = min over cuts of loss(cut)

So big-Phi is what the *least damaging* cut still costs. Above zero means no
cut is free: the system is irreducible, a whole rather than parts that happen to
sit together. Exactly zero means some partition splits it losslessly, and the
system was never one thing.

Only the cuts with unit 0 on the left are enumerated, since a cut and its mirror
are the same cut.

Carve-out, stated plainly: irreducibility is measured as structure destroyed by
the cut. IIT 4.0 proper rebuilds the cause-effect structure on the partitioned
matrix and applies a normalization; the origin flags that gap as unfinished
calibration work, and this port carries the gap over rather than papering it.
By construction big-Phi lands in [0, total].

Ported from `dancinlab/selfhost-work` `stdlib/consciousness/iit4_bigphi.hexa`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .distinction import Distinction
from .relation import PhiStructure, phi_structure
from .tpm import TransitionMatrix

__all__ = ["SystemPhi", "big_phi", "side_of"]

SPANS = 0
"""The distinction reaches across the cut and does not survive it."""


def side_of(distinction: Distinction, left_mask: int, n: int) -> int:
    """Which side of a cut a distinction lies on: 1 left, 2 right, 0 spanning.

    Origin: `iit4_distinction_side`.
    """
    in_left = False
    in_right = False
    for unit in range(n):
        if distinction.involves(unit):
            if left_mask >> unit & 1:
                in_left = True
            else:
                in_right = True
    if in_left and in_right:
        return SPANS
    return 1 if in_left else 2


@dataclass(frozen=True, slots=True)
class SystemPhi:
    """The verdict on one system in one state."""

    phi: float
    """big-Phi, in bits. Zero means reducible — some cut costs nothing."""
    structure: PhiStructure
    cut: int
    """Left side of the minimum-information partition, as a unit bitmask. Zero
    when no cut was evaluated (a system of one unit)."""

    @property
    def is_irreducible(self) -> bool:
        """Whether the system holds together as one thing."""
        return self.phi > 0.0

    @property
    def total(self) -> float:
        return self.structure.total

    def __str__(self) -> str:
        verdict = "irreducible" if self.is_irreducible else "reducible"
        return (
            f"big-phi={self.phi:.6f} of total={self.total:.6f} "
            f"[{verdict}] cut={self.cut:b}"
        )


def big_phi(matrix: TransitionMatrix, system_state: int) -> SystemPhi:
    """Measure a system's irreducibility in a given state.

    Cost grows steeply: every mechanism searches every purview over every
    partition, so this is exponential in `n` several times over. n <= 5 is the
    practical ceiling.
    """
    structure = phi_structure(matrix, system_state)
    found = structure.distinctions
    total = structure.total

    if matrix.n < 2:
        # There is nothing to cut, so nothing can be lost.
        return SystemPhi(phi=0.0, structure=structure, cut=0)

    all_units = (1 << matrix.n) - 1
    best_loss = float("inf")
    best_cut = 0

    for left in range(1, all_units):
        if not left & 1:
            # Unit 0 pinned left, so each unordered cut is visited once.
            continue

        sides = [side_of(d, left, matrix.n) for d in found]
        survived = sum(d.phi for d, side in zip(found, sides) if side != SPANS)

        by_mechanism = {d.mechanism: side for d, side in zip(found, sides)}
        for relation in structure.relations:
            left_side = by_mechanism[relation.left]
            right_side = by_mechanism[relation.right]
            if left_side != SPANS and left_side == right_side:
                survived += relation.phi

        loss = total - survived
        if loss < best_loss:
            best_loss, best_cut = loss, left

    if best_loss == float("inf"):
        best_loss = 0.0
    return SystemPhi(phi=max(0.0, best_loss), structure=structure, cut=best_cut)
