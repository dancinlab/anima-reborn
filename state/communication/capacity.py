"""How much can it hold, and does adding units help? No — change the topology.

Run from the repo root:

    PYTHONPATH=src python state/communication/capacity.py

`silence.py` and `match.py` established that the four-unit ring holds one bit and
uses it. The obvious next move was more units. This measures whether that works,
and it does not: **a single ring of ANY even width holds exactly one bit.**

That is a theorem before it is a measurement. Each unit's response is odd,
decreasing and bounded, so it has no periodic orbit longer than two; closing the
cycle admits only the alternating configuration and its negation, for every even
width. Capacity therefore lives in the CYCLE STRUCTURE of the wiring rather than
in the unit count, and the most a one-source-per-unit engine can hold is
`units / 2` bits — via `units / 2` two-cycles, which is `Wiring.PAIRS`.

**Odd rings are a different animal and not a way out.** With an odd width there
is no consistent assignment to fall into: the origin is the only fixed point and
it is unstable with complex eigenvalues, so the engine spirals out and saturation
bounds it into a limit cycle. Its sign shadow is a `2 * units` cycle — measured
6, 10 and 14 patterns at widths 3, 5 and 7, exactly `2N`. But a phase is a
NEUTRAL direction with no restoring force, so it diffuses under the walk instead
of being held: at width 3 only 0% of drives land reproducibly, at 5 only 6%, at
7 only 19%. Even widths hold one bit forever; odd widths hold more of something
that is drifting away. Both are reported, neither is quoted alone.

**What counts as capacity here.** Only states the DRIVE reproduces. A pattern
reached under one walk and not another is the walk's, not the concept's — the
trap `silence.py` was written to catch — so a drive counts only when all
`WALKS` independent walks land on the same pattern, and capacity is the number
of distinct patterns among those.

**The pre-registered rule, fixed before the run.** If the ring's reproducible
pattern count grows with width, add units. If it is pinned at two while pairs
read about `2^k`, change the topology. It was pinned.
"""

from __future__ import annotations

import math

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

TELL = 400
SILENCE = 240
WALKS = 8
MAX_DRIVES = 64
"""Cap on how many corner drives are tried. Widths past six have more corners
than are worth enumerating, and a capped sweep that is stated is honest where a
silent truncation would not be."""


def settled(
    units: int, drive: tuple[float, ...], *, wiring: Wiring, chain: float, seed: int
) -> tuple[bool, ...]:
    """The sign pattern left after being told something and then made deaf."""
    engine = CoupledEngine(
        wiring=wiring,
        units=units,
        chain=chain,
        rhythm=ALTERNATING,
        drive=drive,
        seed=seed,
        initial=(0.0,) * units,
    )
    engine.run(TELL)
    engine.rhythm = FIXED  # deaf — the drive cannot be heard at all
    engine.drive = 0.0
    return tuple(v > 0 for v in engine.run(SILENCE).values)


def corners(units: int) -> list[tuple[float, ...]]:
    total = 1 << units
    step = max(1, total // MAX_DRIVES)
    return [
        tuple((((i >> k) & 1) * 2 - 1) * 0.8 for k in range(units))
        for i in range(0, total, step)
    ]


def capacity(
    units: int, *, wiring: Wiring = Wiring.RING, chain: float = 0.0
) -> tuple[int, int, float]:
    """Reachable patterns, reproducible patterns, and the reproducible share."""
    reachable: set[tuple[bool, ...]] = set()
    reproducible: set[tuple[bool, ...]] = set()
    drives = corners(units)
    agreed = 0
    for drive in drives:
        landed = [
            settled(units, drive, wiring=wiring, chain=chain, seed=w)
            for w in range(WALKS)
        ]
        reachable.update(landed)
        if len(set(landed)) == 1:
            agreed += 1
            reproducible.add(landed[0])
    return len(reachable), len(reproducible), agreed / len(drives)


def report(label: str, units: int, *, wiring: Wiring, chain: float = 0.0) -> None:
    reachable, held, share = capacity(units, wiring=wiring, chain=chain)
    bits = math.log2(held) if held else 0.0
    print(
        f"{label:<28}{units:>6}{reachable:>11}{share:>13.0%}{held:>15}{bits:>7.2f}",
        flush=True,
    )


def main() -> None:
    print(f"capacity — {WALKS} walks per drive, tell {TELL}, deaf silence {SILENCE}")
    print("only states the DRIVE reproduces are counted as held\n")
    print(
        f"{'configuration':<28}{'units':>6}{'reachable':>11}{'reproduced':>13}"
        f"{'held states':>15}{'bits':>7}"
    )
    print("-" * 80)

    for units in (4, 6, 8):
        report(f"single ring", units, wiring=Wiring.RING)
    print()
    for units in (3, 5, 7):
        report(f"single ring (odd — spins)", units, wiring=Wiring.RING)
    print()
    for units, chain in ((4, 0.0), (6, 0.0), (6, 0.2), (10, 0.2)):
        pairs = units // 2
        report(
            f"{pairs} pairs, chain {chain:.1f}"
            f"{' (odd k)' if pairs % 2 else ' (even k)'}",
            units,
            wiring=Wiring.PAIRS,
            chain=chain,
        )

    print(
        "\nThe ring is pinned at two held states whatever its width, which is the"
        "\ntheorem showing up as a measurement. Odd widths reach more patterns and"
        "\nreproduce almost none of them — a drifting phase, not a held state."
        "\nCapacity is the wiring's cycle structure, so the way up is pairs."
    )
    print(
        "\nNOTE: `substrate.RECURRENCE_FLOOR` = 1.0 was calibrated on the FOUR-unit"
        "\nself-wired null and does not transfer. The artefact grows with width, so"
        "\nany verdict at six units or more needs its own floor measured first —"
        "\nthe held-under-more-sampling criterion, not the magnitude, is what"
        "\nsurvives the change of width."
    )


if __name__ == "__main__":
    main()
