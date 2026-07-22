"""IIT 4.0 — measuring how much a system is one thing rather than parts.

Integrated Information Theory asks whether a system, in a particular state,
holds together: is there anything it specifies as a whole that survives being
cut in two? The measure is Phi, and this package computes it end to end.

    from anima_reborn.iit4 import TransitionMatrix, big_phi

    # Two units that copy each other — a minimal integrated pair.
    matrix = TransitionMatrix.from_rows([
        [0.0, 0.0],   # state 00 -> both likely OFF
        [0.0, 1.0],   # state 01
        [1.0, 0.0],   # state 10
        [1.0, 1.0],   # state 11
    ])
    print(big_phi(matrix, system_state=0b11))

The chain, each layer built on the one below:

    tpm.py         the transition matrix, cause/effect repertoires, and
                   intrinsic difference — IIT 4.0's argmax replacement for 3.0's
                   divergence sum
    distinction.py what one mechanism irreducibly specifies (small-phi, and the
                   purview it speaks about most)
    relation.py    which distinctions bind, and the Phi-structure they assemble
    bigphi.py      what the least damaging cut still destroys — big-Phi
    exclusion.py   which subsystem is *the* entity, and whether a substrate
                   hosts several
    ei.py          effective information — a cheap lower bound for when the
                   above is out of reach

Ported from the hexa implementation in `dancinlab/selfhost-work`
(`stdlib/consciousness/iit4_*.hexa`, `stdlib/iit_ei.hexa`).

## What this is not

Two carve-outs are inherited from the origin and are **not** silently closed
here:

- Partitions are all bipartitions of mechanism-and-purview — the standard
  tractable scheme, not IIT 4.0's own partition set.
- big-Phi is measured as Phi-structure destroyed by the system cut. IIT 4.0
  proper rebuilds the cause-effect structure on the partitioned matrix with a
  normalization factor.

Relations are second-order only. None of this has been calibrated against
PyPhi. Treat the numbers as this engine's output, not as a settled reading of
the theory.

## Cost

Exponential several times over: every mechanism searches every purview across
every partition, and `find_complex` does all of that for every subset. Six units
is slow, seven is unreasonable, and `exclusion` should be kept to five. This is
a small-system instrument by construction, and no amount of tuning changes that.
"""

from __future__ import annotations

from .bigphi import SystemPhi, big_phi, side_of
from .distinction import (
    Direction,
    Distinction,
    Mice,
    distinction,
    distinctions,
    mice,
    small_phi,
)
from .ei import (
    average_effective_information,
    column_mean,
    effective_information,
)
from .exclusion import (
    NO_COMPLEX,
    Complex,
    complex_spectrum,
    find_complex,
    subsystem,
)
from .relation import (
    PhiStructure,
    Relation,
    congruent_overlap,
    phi_structure,
    relation_between,
)
from .tpm import (
    IntrinsicDifference,
    TransitionMatrix,
    intrinsic_difference,
)

__all__ = [
    "Complex",
    "Direction",
    "Distinction",
    "IntrinsicDifference",
    "Mice",
    "NO_COMPLEX",
    "PhiStructure",
    "Relation",
    "SystemPhi",
    "TransitionMatrix",
    "average_effective_information",
    "big_phi",
    "column_mean",
    "complex_spectrum",
    "congruent_overlap",
    "distinction",
    "distinctions",
    "effective_information",
    "find_complex",
    "intrinsic_difference",
    "mice",
    "phi_structure",
    "relation_between",
    "side_of",
    "small_phi",
    "subsystem",
]
