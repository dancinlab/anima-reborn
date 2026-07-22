"""Does the ring HOLD what it was told once the telling stops? One bit, and whose?

Run from the repo root:

    PYTHONPATH=src python state/communication/silence.py

`aligned_drive.py` reads the engine while it is still being told, which cannot
tell a substrate that holds a concept from a wire that passes one. Removing the
drive is the first measurement where the engine is the ONLY possible carrier:
afterwards the drive is not in the path at all, so anything recoverable lives in
engine state or nowhere. It is also the first place recurrence could buy
something rather than merely measure as present.

**Three things called silence, and they are not the same experiment.**

- **deaf** — coupling to 1.0. The drive becomes bit-unreachable, so this is the
  autonomous ring seeded by whatever state it was left in. This is silence.
- **erasing** — drive to zero with the rhythm still running. The engine is
  actively told "origin" half the time, which is an erase signal rather than an
  absence. The first version of this script measured only this and called it
  silence.
- **leaking** — coupling to 0.0 AND drive to zero. Every unit's target is zero,
  so this is pure decay at the substrate's own constant, `1 / PULL` = 17 ticks.
  It is the null that says how much retention is merely "not yet cold".

**What is measured.** Sixteen drives at the corners of the 4-unit cube, so a
substrate holding what it heard has four bits to hold. Separation says how far
apart the states still are; effective rank and the count of distinct
sign-patterns say how WIDE that separation is. Reporting the first without the
second is the error that killed the attractor route.

**Predicted before it was run, and confirmed.** The ring's cycle carries four
sign inversions, so the loop's net sign is positive and the autonomous ring is
bistable — two consistent assignments, `0b0101` and its flip. Asymptotic
capacity in deaf silence is therefore ONE BIT by construction, not a concept
vector. That is the canonical thing recurrence buys and no acyclic wiring can
have, and it is still one bit.

**And the last table decides whether even that bit is worth anything:** does the
CONCEPT choose the basin, or does the walk? Same drive under eight different
walks. The floor is not the half it looks like: eight coin flips over two basins
put a majority of 5.09 on average, so noise alone agrees 63.7% of the time.
Unanimity is the sharp column — eight independent walks agree completely on
0.78% of drives by chance, so a drive whose eight walks all land in one basin is
a drive the concept decided.
"""

from __future__ import annotations

import collections
import math
import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Rhythm, Wiring

DRIVES = [
    tuple((((i >> k) & 1) * 2 - 1) * 0.8 for k in range(4)) for i in range(16)
]
"""The corners of the cube — sixteen distinct things to be told."""

TELL = 400
"""Ticks of drive before the silence, twenty full listen/integrate cycles."""

TAIL = 20
"""Ticks summarized, one whole cycle, fixed across every delay. A window that
grew with the delay would make the window the variable."""

SEEDS = 4
WALKS = 8

LEAK = Rhythm(coupling=0.0)
"""Coupling released entirely, so every target is the drive — and with the drive
at zero, every target is zero."""


def after_silence(
    drive: tuple[float, ...], *, wiring: Wiring, seed: int, silence: int, mode: str
) -> list[float]:
    """Where the engine sits `silence` ticks after the telling stops.

    Drive values and coupling never touch the random source, so one seed gives
    the bit-identical walk under every mode — the modes differ by what silence
    means and by nothing else.
    """
    engine = CoupledEngine(
        wiring=wiring, rhythm=ALTERNATING, drive=drive, seed=seed, initial=(0.0,) * 4
    )
    for _ in range(TELL):
        engine.step()

    if mode == "deaf":
        engine.rhythm = FIXED  # coupling 1.0 — the drive cannot be heard at all
    elif mode == "erasing":
        engine.drive = 0.0  # still listening, and told the origin
    elif mode == "leaking":
        engine.rhythm = LEAK
        engine.drive = 0.0  # every target zero
    else:
        raise ValueError(f"unknown silence mode {mode!r}")

    if silence == 0:
        return list(engine.state.values)
    tail = min(TAIL, silence)
    recent = []
    for tick in range(silence):
        values = engine.step().values
        if tick >= silence - tail:
            recent.append(values)
    return [statistics.mean(p[i] for p in recent) for i in range(4)]


def spread(points: list[list[float]]) -> float:
    centre = [statistics.mean(p[i] for p in points) for i in range(len(points[0]))]
    return statistics.mean(math.dist(p, centre) for p in points)


def effective_rank(points: list[list[float]]) -> float:
    """How many directions the retained states use. One is a line — the collapse
    that separates beautifully and carries a single bit."""
    dim = len(points[0])
    centre = [statistics.mean(p[i] for p in points) for i in range(dim)]
    centred = [[p[i] - centre[i] for i in range(dim)] for p in points]
    cov = [
        [statistics.mean(row[i] * row[j] for row in centred) for j in range(dim)]
        for i in range(dim)
    ]
    trace = sum(cov[i][i] for i in range(dim))
    square = sum(cov[i][j] * cov[i][j] for i in range(dim) for j in range(dim))
    return trace * trace / max(square, 1e-18)


def basin(point: list[float]) -> tuple[bool, ...]:
    return tuple(v > 0 for v in point)


def _majority_floor(walks: int) -> float:
    """Expected majority share when the walk, not the concept, picks the basin.
    Eight coin flips over two basins leave a majority of 5.09, not 4 — the
    floor is 63.7%, and reading it as 50% would call noise a memory."""
    total = sum(math.comb(walks, k) for k in range(walks + 1))
    return sum(
        math.comb(walks, k) * max(k, walks - k) for k in range(walks + 1)
    ) / (total * walks)


def _unanimous_floor(walks: int) -> float:
    """Chance that all walks agree with no concept deciding anything."""
    return 2.0 / (1 << walks)


def separation(mode: str, wiring: Wiring, silence: int) -> float:
    return statistics.mean(
        spread(
            [
                after_silence(d, wiring=wiring, seed=s, silence=silence, mode=mode)
                for d in DRIVES
            ]
        )
        for s in range(SEEDS)
    )


def main() -> None:
    rungs = (0, 20, 60, 120, 240, 480)

    print(f"separation surviving silence — {len(DRIVES)} drives, {SEEDS} seeds")
    print("ring under each meaning of silence, then its two falsifiers\n")
    print(
        f"{'silence':>8}{'RING deaf':>12}{'RING erasing':>14}{'RING leaking':>14}"
        f"{'ffwd deaf':>12}{'self deaf':>11}"
    )
    print("-" * 71)
    for silence in rungs:
        print(
            f"{silence:>8}"
            f"{separation('deaf', Wiring.RING, silence):>12.4f}"
            f"{separation('erasing', Wiring.RING, silence):>14.4f}"
            f"{separation('leaking', Wiring.RING, silence):>14.4f}"
            f"{separation('deaf', Wiring.FEEDFORWARD, silence):>12.4f}"
            f"{separation('deaf', Wiring.SELF, silence):>11.4f}",
            flush=True,
        )

    print("\nand the columns that say what that separation IS (ring, deaf)")
    print(f"{'silence':>8}{'eff. rank':>12}{'sign-patterns':>16}{'width kept':>13}")
    print("-" * 49)
    width_at_zero: float | None = None
    for silence in rungs:
        ranks, patterns = [], []
        for seed in range(SEEDS):
            points = [
                after_silence(
                    d, wiring=Wiring.RING, seed=seed, silence=silence, mode="deaf"
                )
                for d in DRIVES
            ]
            ranks.append(effective_rank(points))
            patterns.append(len({basin(p) for p in points}))
        rank = statistics.mean(ranks)
        if width_at_zero is None:
            width_at_zero = rank
        # Against its OWN width at the moment the telling stopped, rather than a
        # bar someone picked. One retained direction is a line whatever the
        # engine started from.
        kept = (rank - 1.0) / max(width_at_zero - 1.0, 1e-9)
        print(
            f"{silence:>8}{rank:>12.2f}"
            f"{statistics.mean(patterns):>13.1f}/16{kept:>13.0%}",
            flush=True,
        )

    print("\nwhose bit is it — the concept's, or the walk's?")
    print(
        f"noise floors for {WALKS} walks over two basins: "
        f"majority {_majority_floor(WALKS):.1%}, unanimous {_unanimous_floor(WALKS):.2%}\n"
    )
    print(f"{'silence':>8}{'majority':>10}{'unanimous':>12}   reading")
    print("-" * 62)
    for silence in (120, 240, 480):
        agreements, unanimous = [], 0
        for drive in DRIVES:
            landed = [
                basin(
                    after_silence(
                        drive, wiring=Wiring.RING, seed=w, silence=silence, mode="deaf"
                    )
                )
                for w in range(WALKS)
            ]
            counts = collections.Counter(landed)
            agreements.append(counts.most_common(1)[0][1] / len(landed))
            unanimous += len(counts) == 1
        share = unanimous / len(DRIVES)
        reading = (
            "the concept decides"
            if share > _unanimous_floor(WALKS) * 10
            else "the walk decides — the bit is noise"
        )
        print(
            f"{silence:>8}{statistics.mean(agreements):>9.0%}{share:>12.0%}"
            f"   {reading}",
            flush=True,
        )

    print(
        "\nRead the first table with the second, or it reads as recurrence buying"
        "\nmemory. The ring's four sign inversions make the collapse predictable"
        "\nrather than surprising — the loop's net sign is positive, the"
        "\nautonomous ring is bistable, and one bit is all it can hold. The third"
        "\ntable says whether that bit is even the concept's."
    )


if __name__ == "__main__":
    main()
