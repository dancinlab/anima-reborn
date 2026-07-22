"""Does time-multiplexing the coupling break the integration/representation wall?

Run from the repo root:

    PYTHONPATH=src python state/communication/alternating_coupling.py

`integration_vs_representation.py` established the wall: on a fixed coupling the
ring either integrates or stays about what it was told, never both, because its
own attractor swamps the drive. This tests the cheapest of the three candidate
escapes — stop holding the coupling fixed. Listen with it off, integrate with it
on, alternate.

The control that matters is a **fixed coupling at the alternation's time
average**. If the effect were just "some coupling on average", that control would
reproduce it. It does not.

Representation is read off the trajectory (mean and variability of the last
stretch) rather than the settling point, which is candidate three from
`RESULTS.md` folded in — position alone loses what the trajectory keeps.

**This script no longer simulates anything of its own.** It first ran against a
hand-rolled copy of the ring, which measures a copy rather than the engine; the
rhythm now lives in `coupled.Rhythm` and this drives the shipped engine through
`substrate.representation` and `substrate.coupled_phi`. A re-derivation that
reproduces a claim about a copy is not evidence about what anyone imports.

**Two conditions this script exists to keep visible.** Phi rises with `tau` on
its own, so a 20/20 rhythm (which needs tau 40 for one cycle) may not be read
against a fixed coupling at tau 20 — the first version of this table did exactly
that and produced a "matched-or-higher Phi" claim that does not survive. And a
rhythm's Phi depends on the `drive`, because a rhythm can hear; a fixed engine's
does not, because it cannot. Both are printed per row for that reason.
"""

from __future__ import annotations

import hashlib
import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, HIGH, Rhythm
from anima_reborn.substrate import coupled_phi, representation

WORDS = [
    "고양이", "자동차", "바다", "연필", "하늘", "돌멩이", "웃음", "기차",
    "구름", "의자", "강물", "종이", "산", "모래", "노래", "버스",
]
"""Sixteen, because the effect scales with what the inputs carry and eight left
the ratio close enough to the bar to be argued about."""

TRIALS = 6400
"""Samples per state for Phi. The artefact floor at 400 trials is 0.251 on a
system whose true value is zero, which is the same order as the differences
being compared here."""

SEEDS = 5
"""Enough that the tau-40 comparison separates without seed overlap — every
alternating seed read below every fixed one. Three seeds hid an outlier that
moved the mean by 0.26. The whole table takes about 40 minutes."""


def encode(word: str) -> float:
    digest = hashlib.blake2b(word.encode("utf-8"), digest_size=2).digest()
    return int.from_bytes(digest, "big") / 65535.0 * 2.0 - 1.0


DRIVES = [encode(w) for w in WORDS]


DRIVE = 0.42
"""What the engine is told while its Phi is measured. Fixed and printed because
a rhythm's Phi moves with it: alternating 20/20 at tau 40 reads 14.99 told
nothing, 13.16 told 0.42, and is indistinguishable from a fixed coupling told
-0.27. A fixed engine reads the same whatever this is — it cannot hear."""


def integration(rhythm: Rhythm, *, macro_step: int) -> tuple[float, float]:
    values = [
        coupled_phi(
            rhythm=rhythm,
            drive=DRIVE,
            macro_step=macro_step,
            trials=TRIALS,
            seed=s,
            with_complex=False,
        ).directed_phi
        for s in range(SEEDS)
    ]
    return statistics.mean(values), statistics.pstdev(values)


def represents(rhythm: Rhythm) -> float:
    return statistics.mean(
        representation(DRIVES, rhythm=rhythm, seed=s).ratio for s in range(1, 4)
    )


def main() -> None:
    # Phi rises with the macro-step on its own — 12.07 at tau 17, 14.88 at 34 —
    # so tau is printed per row and a comparison across two of them is not a
    # comparison. The 20/20 rhythm needs tau 40 to cover one cycle, which is why
    # the fixed controls appear at BOTH spans.
    cases = [
        ("alternating 10/10", ALTERNATING, 20),
        ("fixed 0.35 (same mean)", Rhythm(ALTERNATING.mean), 20),
        ("fixed 0.70 (same peak)", Rhythm(HIGH), 20),
        ("fixed 1.00 (the engine)", FIXED, 20),
        ("alternating 20/20", Rhythm(HIGH, period=20), 40),
        ("fixed 0.70 @ tau 40", Rhythm(HIGH), 40),
        ("fixed 1.00 @ tau 40", FIXED, 40),
    ]

    print(f"drive = {DRIVE}, {TRIALS} trials, {SEEDS} seeds\n")
    print(f"{'configuration':<26}{'tau':>5}{'directed Phi':>20}{'representation':>16}")
    print("-" * 67)
    for label, rhythm, macro_step in cases:
        mean, deviation = integration(rhythm, macro_step=macro_step)
        print(
            f"{label:<26}{macro_step:>5}{mean:>13.3f} +/-{deviation:5.3f}"
            f"{represents(rhythm):>16.2f}"
        )

    print(
        "\nRead this at ONE tau at a time. Within tau 20 the honest comparison is"
        "\nagainst the same-mean control, which alternating beats on BOTH axes."
        "\nWhat a rhythm buys is representation a fixed coupling has none of; it"
        "\ndoes NOT buy more integration, and the row-against-row reading that"
        "\nsaid it did was comparing two different taus."
    )


if __name__ == "__main__":
    main()
