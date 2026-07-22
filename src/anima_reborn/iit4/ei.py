"""Effective information — a cheap, conservative floor under Phi.

Full big-Phi searches every mechanism, purview and partition, which is why it
stops being computable somewhere around six units. Effective information is the
consolation prize: one pass over the transition matrix, and the answer is a
*lower bound*. True Phi is never smaller than EI, so a positive EI is real
evidence of integration even when Phi itself is out of reach.

For each state, compare where the system goes from there against where it goes
on average:

    EI(s) = sum_t  P(t|s) * log( P(t|s) / Q(t) ),   Q(t) = mean over s of P(t|s)

Q is the "no causal structure" reference — the column mean of the matrix. A
state whose future is sharply different from that average is doing causal work.

Note the shape of the input: this takes a **state-to-state** matrix, one row per
state summing to one, not the state-by-node matrix the rest of this package
uses. It is a different lane, not another view of the same object.

If a state could reach a target the average never reaches, the ratio would
divide by zero and EI would be infinite. That is reported as `math.inf` rather
than smoothed away — the origin used a `"+inf"` sentinel for the same reason,
and averaging skips those states rather than letting one infinity swallow the
result.

That branch is very nearly unreachable, which is worth stating rather than
implying otherwise: Q is the column mean of the same matrix, so `Q(t) = 0`
means no state reaches `t`, which means `P(t|s) = 0` in every row too — and the
infinite term needs `P(t|s) > 0`. The one way through is arithmetic rather than
causal: a probability small enough that dividing by the state count underflows
to zero (subnormals, around 5e-324). The guard is kept for that case and
because the origin has it, not because ordinary matrices reach it.

Ported from `dancinlab/selfhost-work` `stdlib/iit_ei.hexa`.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

__all__ = ["column_mean", "effective_information", "average_effective_information"]

BITS_PER_NAT = 1.4426950408889634
"""1 / ln 2. Origin: `LN2_INV`."""


def _validate(matrix: Sequence[Sequence[float]]) -> int:
    n = len(matrix)
    if n == 0:
        raise ValueError("need at least one state")
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError(
                f"row {i} has {len(row)} entries; a state-to-state matrix must "
                f"be square, expected {n}"
            )
        if any(p < 0.0 for p in row):
            raise ValueError(f"row {i} holds a negative probability")
    return n


def column_mean(matrix: Sequence[Sequence[float]]) -> tuple[float, ...]:
    """Q(t) — where the system goes averaged over every starting state.

    Origin: `_ei_column_mean`.
    """
    n = _validate(matrix)
    return tuple(sum(matrix[s][t] for s in range(n)) / n for t in range(n))


def effective_information(
    matrix: Sequence[Sequence[float]], *, bits: bool = False
) -> tuple[float, ...]:
    """EI per state, in nats by default or bits on request.

    A state that can reach somewhere the average never reaches gets
    `math.inf`. Origin: `ei_per_state_nats` / `ei_per_state_bits`.
    """
    n = _validate(matrix)
    reference = column_mean(matrix)

    out = []
    for row in matrix:
        total = 0.0
        for target in range(n):
            p = row[target]
            if p <= 0.0:
                continue
            q = reference[target]
            if q <= 0.0:
                total = math.inf
                break
            total += p * math.log(p / q)
        out.append(total * BITS_PER_NAT if bits and total != math.inf else total)
    return tuple(out)


def average_effective_information(
    matrix: Sequence[Sequence[float]], *, bits: bool = False
) -> float:
    """Unweighted mean EI across states, skipping infinite ones.

    Skipping is deliberate: one unreachable target would otherwise make the
    whole average infinite and tell you nothing about the rest. Callers who care
    about singular states should look at `effective_information` directly.
    Returns 0.0 when every state is singular. Origin: `ei_average_nats`.
    """
    finite = [v for v in effective_information(matrix, bits=bits) if v != math.inf]
    return sum(finite) / len(finite) if finite else 0.0
