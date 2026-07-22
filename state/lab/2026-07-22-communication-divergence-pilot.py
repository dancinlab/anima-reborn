"""Pilot measurement for the communication divergence report.

Question: is "modality invariance" — the same concept arriving through two
unrelated encodings driving the substrate to the same place — testable with the
existing words machinery, and would a positive mean understanding?

Two measurements, both against the seeds in
`state/lab/2026-07-22-communication-divergence-fable.md` section 1 direction D1.

A. Stream level. Drive A with blake2b(word) and G with sha256(word) of the SAME
   word sequence, no channel, and measure excess over the time-shift null. If
   this is positive it cannot mean understanding: the two streams share a cause
   (the word sequence) and MI cannot tell a shared cause from a grasped concept.
   `substrate.py` already proved shared cause is not integration; this checks
   the same confound exists for the invariance reading.

B. State level. Per word, the substrate's settled response under each encoding.
   A substrate that canonicalizes — maps the concept, not the code, to its
   response — would give correlated responses across encodings. A substrate
   that is a filter on the encoder's scalar will show (i) response ~ encoded
   value within an encoding and (ii) cross-encoding response correlation equal
   to the encodings' own (hash ~ 0).

Run from the repo root:  PYTHONPATH=src python state/lab/2026-07-22-communication-divergence-pilot.py
Conditions: hold=17, window=13600 (800 effective samples), Binning(12, 1.6),
time-shift null at SHIFTS median, seeds 0-7, vocabulary 20 words.
"""

from __future__ import annotations

import hashlib
import random
import statistics

from anima_reborn.info import Binning, entropy, joint_entropy
from anima_reborn.words import HOLD, SHIFTS, WINDOW, blake_scalar, drive

VOCAB = [
    "river", "stone", "ember", "cloud", "anchor", "meadow", "signal", "mirror",
    "harbor", "thread", "silence", "orbit", "lantern", "cinder", "valley",
    "compass", "willow", "static", "granite", "tide",
]

SEEDS = range(8)
BINNING = Binning(bins=12, vrange=1.6)


def sha_scalar(word: str) -> float:
    """Second encoding, unrelated to blake_scalar by construction."""
    digest = hashlib.sha256(word.encode("utf-8")).digest()[:2]
    return int.from_bytes(digest, "big") / 65535.0 * 2.0 - 1.0


def mutual_information(a: list[float], b: list[float]) -> float:
    return max(
        0.0, entropy(a, BINNING) + entropy(b, BINNING) - joint_entropy(a, b, BINNING)
    )


def excess(left: list[float], right: list[float]) -> float:
    observed = mutual_information(left, right)
    nulls = sorted(
        mutual_information(left, right[s:] + right[:s]) for s in SHIFTS
    )
    return observed - nulls[len(nulls) // 2]


def word_sequence(seed: int) -> list[str]:
    rng = random.Random(seed)
    return [rng.choice(VOCAB) for _ in range(WINDOW // HOLD)]


def settled_response(words: list[str], observations: list[float]) -> dict[str, float]:
    """Mean observed position over the settled back half of each hold."""
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for block, word in enumerate(words):
        start = block * HOLD + HOLD // 2
        segment = observations[start : block * HOLD + HOLD]
        if not segment:
            continue
        sums[word] = sums.get(word, 0.0) + sum(segment) / len(segment)
        counts[word] = counts.get(word, 0) + 1
    return {w: sums[w] / counts[w] for w in sums}


def main() -> None:
    # A — same words, two unrelated encodings, no channel of any kind.
    excesses = []
    for seed in SEEDS:
        words = word_sequence(seed)
        left = drive(words, encode=blake_scalar, rng=random.Random(seed * 2 + 1))
        right = drive(words, encode=sha_scalar, rng=random.Random(seed * 2 + 2))
        excesses.append(excess(left, right))
    print("A. cross-encoding excess, same words, no channel (true coupling = none)")
    print(f"   per seed: {' '.join(f'{e:+.3f}' for e in excesses)}")
    print(f"   mean {statistics.mean(excesses):+.3f}   all positive: "
          f"{all(e > 0 for e in excesses)}")

    # B — does the substrate's response track the concept or the code?
    within, across, encodings_own = [], [], None
    for seed in SEEDS:
        words = word_sequence(seed)
        obs_blake = drive(words, encode=blake_scalar, rng=random.Random(seed * 2 + 1))
        obs_sha = drive(words, encode=sha_scalar, rng=random.Random(seed * 2 + 2))
        r_blake = settled_response(words, obs_blake)
        r_sha = settled_response(words, obs_sha)
        shared = sorted(set(r_blake) & set(r_sha))
        e_blake = [blake_scalar(w) for w in shared]
        e_sha = [sha_scalar(w) for w in shared]
        within.append(
            statistics.correlation([r_blake[w] for w in shared], e_blake)
        )
        across.append(
            statistics.correlation(
                [r_blake[w] for w in shared], [r_sha[w] for w in shared]
            )
        )
        if encodings_own is None:
            encodings_own = statistics.correlation(e_blake, e_sha)
    print("\nB. is the settled response the concept or the code?")
    print(f"   corr(response, own encoder)  mean {statistics.mean(within):+.3f}"
          f"  (1.0 = the response IS the encoder, rescaled)")
    print(f"   corr(response A-enc, response B-enc) mean {statistics.mean(across):+.3f}")
    print(f"   corr(encoder A, encoder B) itself     {encodings_own:+.3f}"
          f"  (what zero canonicalization predicts the line above equals)")


if __name__ == "__main__":
    main()
