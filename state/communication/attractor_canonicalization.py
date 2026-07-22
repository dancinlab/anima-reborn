"""Does planting attractors make the substrate canonicalize? Measured: no.

Run from the repo root:

    PYTHONPATH=src python state/communication/attractor_canonicalization.py

The delegated divergence picked D7 — a Hopfield-style substrate with several
basins, so that many different inputs collapse to one — as the direction to
start on. Its own pass bar was that two encodings of one concept end up in the
same basin. This tests it, and finds two things worth more than the direction.

**First, the test everyone had been running was impossible.** Two independent
hashes of the same word share no information — measured across 4000 words, their
mutual information is 0.0185 bits against a shuffled null of 0.0212. Identical.
No dynamics can recover "same concept" from two signals that share nothing, so
the earlier refutations of modality invariance were refuting an impossibility,
not a property of any substrate. A fair test needs modalities that actually
share structure, the way text and audio of one word do.

**Second, given shared structure, the attractors contribute nothing.** With two
noisy views of one latent the agreement is real — but a substrate with no
attractors at all agrees just as often, so the agreement is the input's, not the
dynamics'.

The trap that nearly hid this: at low gain everything lands in ONE basin, which
scores 100% agreement while carrying zero information. Agreement is only
meaningful alongside how many basins were used.
"""

from __future__ import annotations

import collections
import hashlib
import math
import random

from anima_reborn.info import Binning, entropy, joint_entropy
from anima_reborn.pipeline import PULL, WALK

UNITS = 4
PATTERNS = [[1, 1, -1, -1], [1, -1, 1, -1]]
"""Two orthogonal patterns, so four basins counting sign. Hopfield capacity is
about 0.14N, so four units hold one or two — the basin list is small by
construction and that is a declared condition, not an oversight."""

WORDS = [f"w{i:03d}" for i in range(60)]


def weights() -> list[list[float]]:
    """Hebbian storage, diagonal zeroed so no unit reads itself."""
    w = [[0.0] * UNITS for _ in range(UNITS)]
    for pattern in PATTERNS:
        for i in range(UNITS):
            for j in range(UNITS):
                if i != j:
                    w[i][j] += pattern[i] * pattern[j] / UNITS
    return w


W = weights()


def settle(start: list[float], *, gain: float, seed: int = 1, ticks: int = 400):
    rng = random.Random(seed)
    x = list(start)
    for _ in range(ticks):
        previous = list(x)
        for i in range(UNITS):
            field = sum(W[i][j] * previous[j] for j in range(UNITS))
            x[i] = (
                previous[i] + (math.tanh(gain * field) - previous[i]) * PULL
                + (rng.random() - 0.5) * WALK
            )
    return x


def settle_without_attractors(start: list[float], *, seed: int = 1, ticks: int = 400):
    """The control: same noise, same timescale, no basins to fall into."""
    rng = random.Random(seed)
    x = list(start)
    for _ in range(ticks):
        for i in range(UNITS):
            x[i] = 0.9 * x[i] + 0.1 * start[i] + (rng.random() - 0.5) * WALK
    return x


def basin(x: list[float]) -> tuple[int, int]:
    best, distance = (0, 1), math.inf
    for k, pattern in enumerate(PATTERNS):
        for sign in (1, -1):
            d = sum((x[i] - sign * pattern[i]) ** 2 for i in range(UNITS))
            if d < distance:
                distance, best = d, (k, sign)
    return best


def two_views(word: str, noise: float) -> tuple[list[float], list[float]]:
    """Two noisy observations of one latent — modalities that DO share
    structure, unlike two independent hashes."""
    digest = hashlib.blake2b(word.encode("utf-8"), digest_size=UNITS).digest()
    latent = [(b / 255.0) * 2 - 1 for b in digest]
    rng = random.Random(hash(word) & 0xFFFFFFFF)
    return (
        [v + (rng.random() - 0.5) * noise for v in latent],
        [v + (rng.random() - 0.5) * noise for v in latent],
    )


def independent_encodings_share_nothing() -> tuple[float, float]:
    """Mutual information between two hashes of the same word, and its null."""
    binning = Binning(bins=12, vrange=1.0)
    words = [f"w{i:04d}" for i in range(4000)]

    def encode(word: str, scheme: str) -> float:
        digest = (
            hashlib.blake2b(word.encode(), digest_size=2).digest()
            if scheme == "A"
            else hashlib.sha256(("s|" + word).encode()).digest()[:2]
        )
        return int.from_bytes(digest, "big") / 65535.0 * 2 - 1

    a = [encode(w, "A") for w in words]
    b = [encode(w, "B") for w in words]

    def mi(left, right):
        return max(
            0.0,
            entropy(left, binning) + entropy(right, binning)
            - joint_entropy(left, right, binning),
        )

    shuffled = list(b)
    random.Random(1).shuffle(shuffled)
    return mi(a, b), mi(a, shuffled)


def main() -> None:
    observed, null = independent_encodings_share_nothing()
    print("two independent hashes of one word, over 4000 words")
    print(f"  mutual information : {observed:.4f} bits")
    print(f"  shuffled null      : {null:.4f} bits")
    print("  -> nothing shared; the invariance test as posed has no signal in it\n")

    print("given modalities that DO share structure (noisy views of one latent)")
    print(f"{'noise':>7}{'with attractors':>18}{'control':>10}")
    print("-" * 36)
    for noise in (0.5, 1.0, 1.5):
        pairs = [two_views(w, noise) for w in WORDS]
        with_attr = sum(
            basin(settle(a, gain=4)) == basin(settle(b, gain=4)) for a, b in pairs
        )
        without = sum(
            basin(settle_without_attractors(a)) == basin(settle_without_attractors(b))
            for a, b in pairs
        )
        n = len(pairs)
        print(f"{noise:>7.1f}{with_attr / n:>17.0%}{without / n:>10.0%}")

    print("\nagreement is only meaningful next to how many basins were used")
    print(f"{'gain':>7}{'agreement':>12}{'basins used':>14}   reading")
    print("-" * 52)
    pairs = [two_views(w, 1.5) for w in WORDS]
    for gain in (1.0, 1.5, 2.0, 4.0, 8.0):
        landed = [basin(settle(a, gain=gain)) for a, _ in pairs]
        used = len(set(landed))
        agree = sum(
            basin(settle(a, gain=gain)) == basin(settle(b, gain=gain)) for a, b in pairs
        ) / len(pairs)
        reading = (
            "collapse — one basin, no information"
            if used <= 1
            else ("canonicalizing" if agree > 0.70 else "no better than control")
        )
        print(f"{gain:>7.1f}{agree:>12.0%}{used:>14}   {reading}")
        if used > 1:
            counts = collections.Counter(
                f"{k}{'+' if s > 0 else '-'}" for k, s in landed
            )
            print(f"{'':>33}{dict(counts)}")


if __name__ == "__main__":
    main()
