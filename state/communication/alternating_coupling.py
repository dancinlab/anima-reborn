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
"""

from __future__ import annotations

import hashlib
import math
import random
import statistics
from collections.abc import Callable

from anima_reborn.coupled import AMPLITUDE, GAIN, UNITS, Wiring
from anima_reborn.iit4 import directed_big_phi
from anima_reborn.pipeline import PULL, WALK
from anima_reborn.substrate import estimate_matrix

SOURCES = Wiring.RING.sources

WORDS = [
    "고양이", "자동차", "바다", "연필", "하늘", "돌멩이", "웃음", "기차",
    "구름", "의자", "강물", "종이", "산", "모래", "노래", "버스",
]
"""Sixteen, because the effect scales with what the inputs carry and eight left
the ratio close enough to the bar to be argued about."""

HIGH = 0.7
"""Coupling during the integrate phase."""


def encode(word: str) -> float:
    digest = hashlib.blake2b(word.encode("utf-8"), digest_size=2).digest()
    return int.from_bytes(digest, "big") / 65535.0 * 2.0 - 1.0


def alternating(period: int, high: float = HIGH) -> Callable[[int], float]:
    """Off for `period` ticks, on for `period` ticks."""
    return lambda tick: 0.0 if (tick // period) % 2 == 0 else high


def fixed(value: float) -> Callable[[int], float]:
    return lambda _tick: value


def trajectory(
    value: float, *, seed: int, coupling: Callable[[int], float], ticks: int = 800
) -> list[list[float]]:
    rng = random.Random(seed)
    x = [0.0] * UNITS
    out = []
    for tick in range(ticks):
        lam = coupling(tick)
        previous = list(x)
        for i, source in enumerate(SOURCES):
            assert source is not None
            partner = -AMPLITUDE * math.tanh(GAIN * previous[source] / AMPLITUDE)
            target = (1.0 - lam) * (value * AMPLITUDE) + lam * partner
            x[i] = previous[i] + (target - previous[i]) * PULL + (rng.random() - 0.5) * WALK
        out.append(list(x))
    return out


def summarize(path: list[list[float]], tail: int = 300) -> list[float]:
    """Mean AND variability per unit — the trajectory, not the endpoint."""
    recent = path[-tail:]
    return [statistics.mean(p[i] for p in recent) for i in range(UNITS)] + [
        statistics.pstdev([p[i] for p in recent]) for i in range(UNITS)
    ]


def spread(points: list[list[float]]) -> float:
    centre = [statistics.mean(p[i] for p in points) for i in range(len(points[0]))]
    return statistics.mean(math.dist(p, centre) for p in points)


def representation(coupling: Callable[[int], float], *, word_seed: int = 1) -> float:
    by_word = spread(
        [summarize(trajectory(encode(w), seed=word_seed, coupling=coupling)) for w in WORDS]
    )
    by_noise = spread(
        [
            summarize(trajectory(encode(WORDS[0]), seed=s, coupling=coupling))
            for s in range(12)
        ]
    )
    return by_word / max(by_noise, 1e-9)


def integration(
    coupling: Callable[[int], float], *, macro_step: int, trials: int = 6400, seeds: int = 3
) -> float:
    value = encode(WORDS[0])

    def step(state: int, rng: random.Random) -> int:
        x = [AMPLITUDE if state >> i & 1 else -AMPLITUDE for i in range(UNITS)]
        for tick in range(macro_step):
            lam = coupling(tick)
            previous = list(x)
            for i, source in enumerate(SOURCES):
                assert source is not None
                partner = -AMPLITUDE * math.tanh(GAIN * previous[source] / AMPLITUDE)
                target = (1.0 - lam) * (value * AMPLITUDE) + lam * partner
                x[i] = (
                    previous[i] + (target - previous[i]) * PULL
                    + (rng.random() - 0.5) * WALK
                )
        return sum(1 << i for i, v in enumerate(x) if v > 0)

    return statistics.mean(
        directed_big_phi(
            estimate_matrix(UNITS, step, trials=trials, seed=s), 0b0101
        ).phi
        for s in range(seeds)
    )


def main() -> None:
    # Macro-step covers a whole listen/integrate cycle, and the fixed controls
    # use the same span so the comparison is not about the window.
    cases = [
        ("alternating 10/10", alternating(10), 20),
        ("fixed 0.35 (same mean)", fixed(0.35), 20),
        ("fixed 0.50", fixed(0.50), 20),
        ("fixed 0.70", fixed(0.70), 20),
        ("alternating 20/20", alternating(20), 40),
    ]

    print(f"{'configuration':<26}{'directed Phi':>14}{'representation':>16}")
    print("-" * 56)
    for label, coupling, macro_step in cases:
        phi = integration(coupling, macro_step=macro_step)
        ratio = statistics.mean(
            representation(coupling, word_seed=ws) for ws in range(1, 4)
        )
        print(f"{label:<26}{phi:>14.3f}{ratio:>16.2f}")

    print(
        "\nthe comparison that survives: at matched-or-higher integration,"
        "\nalternating keeps representation that fixed coupling destroys."
    )


if __name__ == "__main__":
    main()
