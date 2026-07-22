"""M10 and M13 — the exclusion postulate: which subsystem is the entity.

`big_phi` measures the system you hand it. IIT 4.0 says that is the wrong
question to stop on: the conscious entity is the *maximal complex* — whichever
subset of units has the highest big-Phi. Overlapping candidates with less are
excluded; they do not get to be a second, lesser experience inside the first.

Each candidate subset is re-measured **as its own system**: the units outside it
are pinned to their current values and become fixed background, which is IIT
4.0's convention for asking what a part would be on its own. That conditioning
is a modeling choice, and naming it is part of the measurement.

`complex_spectrum` goes further. One substrate can host several *disjoint*
complexes — think two clusters that are each integrated but not with each other.
Sorting candidates by Phi and greedily taking any that shares no unit with an
accepted one gives the ranked list, since a unit may belong to at most one
complex.

Ties are decided the same way in both: higher Phi wins; on a tie the larger
subset wins, because more units is a bigger entity; on equal size the lower mask
wins, which the ascending scan gives for free.

Cost is brutal — 2^n - 1 subsets, each a full big-Phi measurement.

Ported from `dancinlab/selfhost-work` `stdlib/consciousness/iit4_complex.hexa`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .bigphi import big_phi
from .tpm import TransitionMatrix, expand, units_of

__all__ = ["Complex", "subsystem", "find_complex", "complex_spectrum"]

TIE_EPSILON = 1.0e-9
"""Phi values within this of each other count as tied. Origin: `eps`."""


@dataclass(frozen=True, slots=True)
class Complex:
    """A subsystem measured on its own, with the background held fixed."""

    units: int
    """Bitmask of the units in the complex. Zero means there is no complex."""
    phi: float
    size: int

    @property
    def exists(self) -> bool:
        return self.units != 0 and self.phi > TIE_EPSILON

    def __str__(self) -> str:
        if not self.exists:
            return "no complex"
        return f"units={self.units:b} (size {self.size}) phi={self.phi:.6f}"


NO_COMPLEX = Complex(units=0, phi=0.0, size=0)
"""Every candidate was reducible — nothing here is one thing."""


def subsystem(
    matrix: TransitionMatrix, subset: int, system_state: int
) -> TransitionMatrix:
    """The subset's own transition matrix, external units held at their values.

    The result is indexed compactly: unit `b` of the new matrix is the `b`-th
    unit of `subset` in ascending order. Origin: `subsystem_tpm`.
    """
    inside = units_of(subset, matrix.n)
    if not inside:
        raise ValueError("a subsystem needs at least one unit")

    all_units = (1 << matrix.n) - 1
    external = all_units & ~subset
    background = system_state & external

    values = []
    for compact in range(1 << len(inside)):
        # Everything is pinned: the subset to the state being asked about, the
        # outside to where it actually is.
        fixed = expand(compact, inside) | background
        for unit in inside:
            values.append(matrix.marginal_on(all_units, fixed, unit))
    return TransitionMatrix(values, len(inside))


def _project(system_state: int, units: tuple[int, ...]) -> int:
    """A system state seen from inside the subset. Origin: `iit4_project_state`."""
    projected = 0
    for bit, unit in enumerate(units):
        if system_state >> unit & 1:
            projected |= 1 << bit
    return projected


def _candidates(
    matrix: TransitionMatrix, system_state: int
) -> list[Complex]:
    """Score every non-empty subset as its own system, ascending by mask."""
    scored = []
    for subset in range(1, 1 << matrix.n):
        inside = units_of(subset, matrix.n)
        measured = big_phi(
            subsystem(matrix, subset, system_state),
            _project(system_state, inside),
        )
        scored.append(Complex(units=subset, phi=measured.phi, size=len(inside)))
    return scored


def find_complex(matrix: TransitionMatrix, system_state: int) -> Complex:
    """The single maximal complex, or `NO_COMPLEX`. Origin: `find_complex`."""
    best = NO_COMPLEX
    for candidate in _candidates(matrix, system_state):
        if candidate.phi > best.phi + TIE_EPSILON:
            best = candidate
        elif abs(candidate.phi - best.phi) <= TIE_EPSILON and candidate.size > best.size:
            best = candidate
    return best if best.phi > TIE_EPSILON else NO_COMPLEX


def complex_spectrum(
    matrix: TransitionMatrix, system_state: int
) -> tuple[Complex, ...]:
    """Every non-overlapping complex, strongest first.

    Empty when the substrate hosts no complex at all.
    Origin: `complex_spectrum`.
    """
    scored = [c for c in _candidates(matrix, system_state) if c.phi > TIE_EPSILON]
    # Phi descending, then size descending, then mask ascending.
    #
    # Phi is quantized onto the epsilon grid first, because the tie-break only
    # means anything if "within TIE_EPSILON" counts as tied — the origin
    # compares pairwise with that tolerance. Sorting on the raw float instead
    # would let a 1e-15 difference outrank a whole extra unit. Quantizing keeps
    # the tolerance while still giving a genuine total order, which a
    # tolerant pairwise comparator is not.
    scored.sort(key=lambda c: (-round(c.phi / TIE_EPSILON), -c.size, c.units))

    accepted: list[Complex] = []
    taken = 0
    for candidate in scored:
        if candidate.units & taken:
            continue  # a unit belongs to at most one complex
        accepted.append(candidate)
        taken |= candidate.units
    return tuple(accepted)
