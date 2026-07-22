"""M3 — relations, and the Phi-structure they assemble.

Distinctions are not a heap. Two of them *relate* when their purviews overlap
and they say the *same thing* about the units they share — congruence. A
relation is worth the weaker of the two distinctions, because the binding
cannot be stronger than what it binds.

The Phi-structure is the whole of it: every distinction the system has, plus
every relation among them, and the total those add up to. That total is the
thing M4 tries to break.

Carve-out, stated plainly: only second-order relations — pairs. Three-way and
higher congruent overlaps are the combinatorial frontier, and `min(phi_d)` is a
proxy for the relation's own irreducibility rather than IIT 4.0's relation
measure. The origin declares the same limits; this port neither widens nor
hides them.

Ported from `dancinlab/selfhost-work` `stdlib/consciousness/iit4_relation.hexa`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .distinction import PHI_EPSILON, Distinction, distinctions
from .tpm import TransitionMatrix, expand, units_of

__all__ = [
    "Relation",
    "PhiStructure",
    "congruent_overlap",
    "relation_between",
    "phi_structure",
]


def congruent_overlap(
    purview_a: int, state_a: int, purview_b: int, state_b: int, n: int
) -> bool:
    """Do two purviews share units and agree on every one they share?

    Sharing nothing is not congruence — there has to be something to agree
    about. Origin: `iit4_overlap_congruent`.
    """
    absolute_a = expand(state_a, units_of(purview_a, n))
    absolute_b = expand(state_b, units_of(purview_b, n))
    shared = purview_a & purview_b & ((1 << n) - 1)
    if not shared:
        return False
    return absolute_a & shared == absolute_b & shared


@dataclass(frozen=True, slots=True)
class Relation:
    """Two distinctions bound by a congruent overlap."""

    left: int
    """Mechanism mask of one distinction."""
    right: int
    """Mechanism mask of the other."""
    phi: float
    """min of the two distinctions' phi — a binding is worth no more than the
    weaker thing it binds."""

    def __str__(self) -> str:
        return f"{self.left:b} ~ {self.right:b} phi={self.phi:.6f}"


def relation_between(a: Distinction, b: Distinction, n: int) -> float:
    """The relation's phi, or 0.0 when the two do not relate.

    Congruence on *either* the cause or the effect side is enough.
    Origin: `relation_2nd`.
    """
    on_cause = congruent_overlap(
        a.cause.purview, a.cause.state, b.cause.purview, b.cause.state, n
    )
    on_effect = congruent_overlap(
        a.effect.purview, a.effect.state, b.effect.purview, b.effect.state, n
    )
    if on_cause or on_effect:
        return min(a.phi, b.phi)
    return 0.0


@dataclass(frozen=True, slots=True)
class PhiStructure:
    """Everything the system specifies about itself, in one state.

    Origin: `phi_structure`.
    """

    distinctions: tuple[Distinction, ...]
    relations: tuple[Relation, ...]

    @property
    def distinction_phi(self) -> float:
        return sum(d.phi for d in self.distinctions)

    @property
    def relation_phi(self) -> float:
        return sum(r.phi for r in self.relations)

    @property
    def total(self) -> float:
        """The unpartitioned value of the structure — what a system cut is
        measured against."""
        return self.distinction_phi + self.relation_phi

    def __len__(self) -> int:
        return len(self.distinctions)

    def __str__(self) -> str:
        return (
            f"{len(self.distinctions)} distinctions (sum phi="
            f"{self.distinction_phi:.6f}) · {len(self.relations)} relations "
            f"(sum phi={self.relation_phi:.6f}) · total={self.total:.6f}"
        )


def relations_among(
    found: tuple[Distinction, ...], n: int
) -> tuple[Relation, ...]:
    """Every congruent pair, in ascending index order."""
    out = []
    for i, a in enumerate(found):
        for b in found[i + 1:]:
            phi = relation_between(a, b, n)
            if phi > PHI_EPSILON:
                out.append(Relation(left=a.mechanism, right=b.mechanism, phi=phi))
    return tuple(out)


def phi_structure(matrix: TransitionMatrix, system_state: int) -> PhiStructure:
    """Assemble the system's Phi-structure. Origin: `phi_structure`."""
    found = distinctions(matrix, system_state)
    return PhiStructure(distinctions=found, relations=relations_among(found, matrix.n))
