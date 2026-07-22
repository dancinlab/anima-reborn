"""Does the coupled engine stay about-something once it integrates?

Run from the repo root:

    PYTHONPATH=src python state/communication/integration_vs_representation.py

Asked while diverging on what the engine would need in order to communicate. The
obvious first requirement is that it be *about* what it is told — and the
obvious first test is whether a concept arriving through two unrelated encodings
drives it to the same place. That test fails, and chasing why produced something
more useful than the test itself.

Two quantities, swept over the same knob:

    representation   how far apart the substrate settles for DIFFERENT words,
                     divided by how far apart it settles for the SAME word under
                     different noise. Above ~3 the input is visible in where the
                     system ends up; near 1 it is buried in noise.
    integration      directed Phi, which needs the units to read each other.

Both are measured on the identical engine, changing only `lambda` — how much of
each unit's target is the live partner rather than the word.

See `RESULTS.md` for what came out, which was not what the seed predicted.
"""

from __future__ import annotations

import hashlib
import math
import random
import statistics

from anima_reborn.coupled import AMPLITUDE, GAIN, MACRO_STEP, UNITS, Wiring
from anima_reborn.iit4 import directed_big_phi
from anima_reborn.pipeline import PULL, WALK
from anima_reborn.substrate import estimate_matrix

WORDS = ["고양이", "자동차", "바다", "연필", "하늘", "돌멩이", "웃음", "기차"]
SOURCES = Wiring.RING.sources

REPRESENTATION_BAR = 3.0
"""Word-driven spread must clear noise-driven spread by this much before the
input can be said to be visible in the outcome."""

INTEGRATION_BAR = 1.0
"""`substrate.RECURRENCE_FLOOR` — measured against the uncoupled null."""


def encode(word: str, *, salt: str = "") -> float:
    digest = hashlib.blake2b((salt + word).encode("utf-8"), digest_size=2).digest()
    return int.from_bytes(digest, "big") / 65535.0 * 2.0 - 1.0


def settle(value: float, *, seed: int, coupling: float, ticks: int = 600) -> list[float]:
    """Where the ring ends up while a constant drive pushes on it."""
    rng = random.Random(seed)
    x = [0.0] * UNITS
    for _ in range(ticks):
        previous = list(x)
        for i, source in enumerate(SOURCES):
            assert source is not None
            partner = -AMPLITUDE * math.tanh(GAIN * previous[source] / AMPLITUDE)
            target = (1.0 - coupling) * (value * AMPLITUDE) + coupling * partner
            x[i] = previous[i] + (target - previous[i]) * PULL + (rng.random() - 0.5) * WALK
    return x


def spread(points: list[list[float]]) -> float:
    centre = [statistics.mean(p[i] for p in points) for i in range(UNITS)]
    return statistics.mean(math.dist(p, centre) for p in points)


def representation(coupling: float) -> float:
    """Spread caused by the words, over spread caused by the noise alone."""
    by_word = spread([settle(encode(w), seed=1, coupling=coupling) for w in WORDS])
    by_noise = spread(
        [settle(encode(WORDS[0]), seed=s, coupling=coupling) for s in range(8)]
    )
    return by_word / max(by_noise, 1e-9)


def integration(coupling: float, *, trials: int = 3200, seeds: int = 2) -> float:
    value = encode(WORDS[0])

    def step(state: int, rng: random.Random) -> int:
        x = [AMPLITUDE if state >> i & 1 else -AMPLITUDE for i in range(UNITS)]
        for _ in range(MACRO_STEP):
            previous = list(x)
            for i, source in enumerate(SOURCES):
                assert source is not None
                partner = -AMPLITUDE * math.tanh(GAIN * previous[source] / AMPLITUDE)
                target = (1.0 - coupling) * (value * AMPLITUDE) + coupling * partner
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


def modality_invariance() -> tuple[float, float]:
    """The seed that started this: same word, two unrelated encodings.

    Returns (same word across encodings, different words within one encoding).
    For the substrate to be about the *concept* the first must be far smaller.
    """
    same = statistics.mean(
        math.dist(
            settle(encode(w), seed=1, coupling=0.5),
            settle(encode(w, salt="salt|"), seed=1, coupling=0.5),
        )
        for w in WORDS
    )
    different = statistics.mean(
        math.dist(
            settle(encode(WORDS[i]), seed=1, coupling=0.5),
            settle(encode(WORDS[j]), seed=1, coupling=0.5),
        )
        for i in range(len(WORDS))
        for j in range(i + 1, len(WORDS))
    )
    return same, different


def main() -> None:
    same, different = modality_invariance()
    print("modality invariance (coupling 0.5)")
    print(f"  same word, two encodings : {same:.3f}")
    print(f"  different words, one enc : {different:.3f}")
    print(
        "  -> "
        + (
            "invariant"
            if same < different / 2
            else "NOT invariant — the encoding decides, not the word"
        )
    )

    print(f"\n{'lambda':>7}{'directed Phi':>14}{'representation':>16}   both?")
    print("-" * 52)
    for coupling in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7):
        phi = integration(coupling)
        ratio = representation(coupling)
        both = phi > INTEGRATION_BAR and ratio > REPRESENTATION_BAR
        why = (
            ""
            if both
            else ("no integration" if phi <= INTEGRATION_BAR else "input buried")
        )
        print(f"{coupling:>7.1f}{phi:>14.3f}{ratio:>16.2f}   {'yes' if both else 'no':<4} {why}")


if __name__ == "__main__":
    main()
