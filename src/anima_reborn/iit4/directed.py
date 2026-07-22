"""Directed system cuts — telling a loop apart from a chain.

`bigphi.big_phi` cuts a system in two and removes everything crossing the
divide, in both directions at once. That is the scheme inherited from the hexa
origin, and it has a consequence worth stating plainly: **it cannot see that a
feedforward system is reducible.** Measured on a four-unit chain where unit 0 is
exogenous and each later unit reads only the one before it, the undirected
measure reports 1.27 bits and does not shrink with more trials — where IIT 4.0
says zero, because nothing flows back.

A directed cut severs influence one way and leaves the other intact. Under a cut
that stops A from reaching B:

    a distinction survives unless its mechanism sits in A and its effect
    purview reaches into B (its prediction crossed the cut), or its cause
    purview sits in A and its mechanism in B (its memory crossed it)

and Phi is again the least damage any cut does. For the chain that minimum is
exactly zero, and for the right reason: cutting *into* the exogenous unit costs
nothing, because nothing was flowing that way. For a ring no direction is free —
measured, the cheapest directed cut still destroys 10.02 of 13.61 bits.

This lives beside `big_phi` rather than replacing it. The undirected measure is
bit-exact against the hexa engine and eleven golden cases depend on that; a
carve-out gets closed in the open, with both numbers available, not by quietly
changing what the old name means.

    from anima_reborn.iit4 import big_phi, directed_big_phi

    big_phi(chain, state).phi           # 1.27 — cannot see the reducibility
    directed_big_phi(chain, state).phi  # 0.00 — can

**The trap this could have fallen into.** A directed measure searches twice as
many cuts, so its minimum is always at most the undirected one — a lower number
is guaranteed by construction and proves nothing. What makes the zero real is
that the ring stays high through the same code, and that the winning cut on the
chain is identifiably the one pointing at the exogenous unit. Both are tests.

What this does not do: close the other inherited carve-outs. Partitions are
still all bipartitions of mechanism-and-purview, relations are still
second-order, and nothing is calibrated against PyPhi. See `iit4/CLAUDE.md`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .relation import PhiStructure, phi_structure
from .tpm import TransitionMatrix

__all__ = ["DirectedCut", "DirectedPhi", "directed_big_phi"]


@dataclass(frozen=True, slots=True)
class DirectedCut:
    """One direction of one bipartition: `source` stops reaching `sink`."""

    source: int
    """Units whose outgoing influence is severed."""
    sink: int
    """Units that stop hearing from `source`. The reverse direction survives."""

    def severs(self, mechanism: int, cause: int, effect: int) -> bool:
        """Whether this cut breaks a distinction.

        Two ways it can: the mechanism predicts across the cut, or it remembers
        across it. Either is a dependence the cut has removed.
        """
        predicts_across = bool(mechanism & self.source and effect & self.sink)
        remembers_across = bool(cause & self.source and mechanism & self.sink)
        return predicts_across or remembers_across

    def __str__(self) -> str:
        return f"{self.source:b} -/-> {self.sink:b}"


@dataclass(frozen=True, slots=True)
class DirectedPhi:
    """What the least damaging *directed* cut still destroys."""

    phi: float
    """Bits. Zero means some direction can be severed for free — the system is
    reducible in the sense IIT 4.0 means."""
    structure: PhiStructure
    cut: DirectedCut | None
    """The minimum-information directed partition, or None for a system too
    small to cut."""

    @property
    def is_recurrent(self) -> bool:
        """No direction is free, so influence must return. This is the claim the
        undirected measure could not make."""
        return self.phi > 0.0

    @property
    def total(self) -> float:
        return self.structure.total

    def __str__(self) -> str:
        verdict = "recurrent" if self.is_recurrent else "reducible"
        return (
            f"directed-phi={self.phi:.6f} of total={self.total:.6f} "
            f"[{verdict}] cut={self.cut}"
        )


def directed_big_phi(matrix: TransitionMatrix, state: int) -> DirectedPhi:
    """Measure irreducibility against directed cuts.

    Every bipartition is tried in both directions; unit 0 is pinned to one side
    so each directed cut is visited exactly once. Cost is twice `big_phi`'s cut
    loop, which is not where the expense lives — the distinction search above it
    dominates.
    """
    structure = phi_structure(matrix, state)
    found = structure.distinctions

    if matrix.n < 2:
        return DirectedPhi(phi=0.0, structure=structure, cut=None)

    all_units = (1 << matrix.n) - 1
    best_loss = float("inf")
    best_cut: DirectedCut | None = None

    for left in range(1, all_units):
        if not left & 1:
            # Unit 0 pinned left, so each unordered split is enumerated once
            # and both of its directions are tried below.
            continue
        right = all_units & ~left

        for cut in (DirectedCut(left, right), DirectedCut(right, left)):
            # Accumulate what the cut DESTROYS rather than what survives, and
            # subtract nothing. A cut that severs nothing then costs exactly
            # 0.0, where `total - survived` would leave float residue on the
            # order of 1e-16 and turn "reducible" into "almost reducible".
            lost = 0.0
            alive: dict[int, bool] = {}
            for distinction in found:
                intact = not cut.severs(
                    distinction.mechanism,
                    distinction.cause.purview,
                    distinction.effect.purview,
                )
                alive[distinction.mechanism] = intact
                if not intact:
                    lost += distinction.phi

            for relation in structure.relations:
                if not (alive[relation.left] and alive[relation.right]):
                    lost += relation.phi

            if lost < best_loss:
                best_loss, best_cut = lost, cut

    if best_loss == float("inf"):
        best_loss = 0.0
    return DirectedPhi(phi=max(0.0, best_loss), structure=structure, cut=best_cut)
