"""Does the alignment survive an integrating engine? And is there anything to carry?

Run from the repo root:

    PYTHONPATH=src python state/communication/aligned_drive.py

`align.py` learns that two dissimilar signals are about one concept. `coupled.py`
can now be told a vector. The obvious next move is to wire them together and ask
whether an integrated substrate's trajectory identifies the concept — but both
delegated designs said the same thing first: **the engine can only lose
information, so if the concept is not already recoverable from the drive, no
downstream dynamics can put it back.** This measures that, with no engine
involved, and it can kill the whole direction in a minute.

So this runs in two stages. **Stage one** scores the drive itself. **Stage two**
scores the engine's trajectory when told that drive, with the identical
procedure, and reports the fraction that survived. Stage two only runs if stage
one found something, because there is nothing to look for otherwise.

The measurement is cross-modal identification on held-out concepts. Build a
prototype for each concept from repeated modality-0 observations, query with
repeated modality-1 observations, and count how often the nearest prototype is
the right one. Both modalities of one concept must land closer than two
different concepts do, using signals that share no encoding.

**What could fake a pass, and what is here to stop it.**

- The world's own structure. Both modalities are mixings of ONE latent, so raw
  observations already carry the concept — `align.py` measured an untrained gap
  of up to 0.397 for exactly this reason. `raw` is therefore the bar that
  matters, not chance.
- Any training at all. Weights growing or drifting toward the data's leading
  directions would improve separation without pairing teaching anything, so
  `shuffled` trains on the same signals with co-occurrence destroyed.
- The architecture. `untrained` is the same projections at zero pairs.
- The matcher. `permuted` re-scores after shuffling which prototype belongs to
  which query, which is what this matcher reports for no correspondence at all —
  the analytic 1/20 misses bias from unequal variances.
- Collapse. Everything mapped onto one direction agrees beautifully and carries
  nothing; that is what killed the attractor route. Effective rank of the
  projected concepts is reported beside every accuracy, never instead of it.
- The engine not being in the path. At coupling 1.0 the drive is bit-for-bit
  unreachable, so `FIXED` must read the permutation floor. If it does not, the
  concept is reaching the score through something other than the engine and
  nothing else in stage two means anything.
- The engine looking like it contributed. It cannot create information, so the
  reportable number is the fraction of the drive's accuracy that SURVIVES the
  trajectory, never the trajectory's accuracy on its own.

**Conditions.** Scoring uses `sample`-distinct observations, so a repeat is a
fresh draw of observation noise rather than the same fixed exemplar seen twice;
without that, this would score exemplars and call them concepts. `dim=4` matches
the engine's unit count, so nothing is compressed on the way in and there is no
adapter that could create or destroy the result. `Aligner(shuffled=True)` draws
its wrong partner independently, so about 1 pair in `concepts` is accidentally
correct — that makes the control slightly harder to beat, which is the safe
direction for it to be wrong in. Drives are scaled into [-1, 1] by one pooled
constant per arm taken from that arm's projections of its TRAINING concepts
only: per-vector normalization would rescue a collapsed projection back to full
range, and a held-out-derived constant would leak.

Walk seeds are crossed with concepts rather than assigned to them, so nothing
can classify the schedule instead of the drive.
"""

from __future__ import annotations

import math
import random
import statistics

from anima_reborn.align import Aligner
from anima_reborn.coupled import ALTERNATING, FIXED, Rhythm
from anima_reborn.substrate import signature

DIM = 4
"""Width of the shared space. Four so it lands on the engine's four units
untouched — an adapter would be a second learner sitting in the causal path."""

CONCEPTS = 40
HELD_OUT = list(range(10_000, 10_020))
"""The twenty `align.py` keeps out of training. Nothing scored here was trained
on, and nothing here is allowed to influence training."""

REPEATS = 12
"""Observations per (concept, modality). Split 6/6: prototypes from one half,
queries from the other, so a query never contributes to its own prototype."""

PAIRS = 4000
SEEDS = 12
PERMUTATIONS = 200


def views(aligner: Aligner, modality: int, samples: range) -> dict[int, list[list[float]]]:
    """Where each held-out concept lands, once per fresh observation."""
    return {
        concept: [
            aligner.project(
                aligner.observe(concept, modality=modality, sample=s), modality=modality
            )
            for s in samples
        ]
        for concept in HELD_OUT
    }


def raw_views(aligner: Aligner, modality: int, samples: range):
    """The same, with no aligner in the path at all."""
    return {
        concept: [
            aligner.observe(concept, modality=modality, sample=s) for s in samples
        ]
        for concept in HELD_OUT
    }


def centre(points: list[list[float]]) -> list[float]:
    return [statistics.mean(p[i] for p in points) for i in range(len(points[0]))]


def identify(
    prototypes: dict[int, list[float]], queries: dict[int, list[list[float]]]
) -> float:
    """Fraction of queries whose nearest prototype is their own concept."""
    concepts = list(prototypes)
    hits = total = 0
    for concept, points in queries.items():
        for point in points:
            nearest = min(concepts, key=lambda c: math.dist(point, prototypes[c]))
            hits += nearest == concept
            total += 1
    return hits / total


def permuted_floor(
    prototypes: dict[int, list[float]],
    queries: dict[int, list[list[float]]],
    rng: random.Random,
) -> float:
    """What this matcher reports when the correspondence is removed and nothing
    else is. The empirical floor, in place of the analytic 1/20."""
    concepts = list(prototypes)
    best = 0.0
    for _ in range(PERMUTATIONS):
        shuffled = list(concepts)
        rng.shuffle(shuffled)
        relabelled = {a: prototypes[b] for a, b in zip(concepts, shuffled)}
        best = max(best, identify(relabelled, queries))
    return best


def effective_rank(points: list[list[float]]) -> float:
    """Participation ratio of the covariance spectrum, without a linear algebra
    dependency: `(sum of variances)^2 / sum of squared covariance entries`. One
    means everything lies on a single direction, which is the collapse that
    scores well and carries nothing."""
    middle = centre(points)
    dim = len(middle)
    centred = [[p[i] - middle[i] for i in range(dim)] for p in points]
    cov = [
        [statistics.mean(row[i] * row[j] for row in centred) for j in range(dim)]
        for i in range(dim)
    ]
    trace = sum(cov[i][i] for i in range(dim))
    square = sum(cov[i][j] * cov[i][j] for i in range(dim) for j in range(dim))
    return trace * trace / max(square, 1e-18)


def score(aligner: Aligner, *, raw: bool = False) -> tuple[float, float, float]:
    """Cross-modal identification, its permutation floor, and effective rank."""
    read = raw_views if raw else views
    gallery = read(aligner, 0, range(1, REPEATS // 2 + 1))
    probes = read(aligner, 1, range(REPEATS // 2 + 1, REPEATS + 1))
    prototypes = {c: centre(points) for c, points in gallery.items()}
    rng = random.Random(17)
    return (
        identify(prototypes, probes),
        permuted_floor(prototypes, probes, rng),
        effective_rank(list(prototypes.values())),
    )


WALKS = 6
"""Engine walks per drive, crossed with concepts. Six matches the six
observations a prototype is built from, so one trajectory per observation."""


def training_scale(aligner: Aligner, *, raw: bool) -> float:
    """One constant that puts this arm's drives inside [-1, 1].

    Taken from the TRAINING concepts, so no held-out concept influences the
    scaling, and pooled over all of them, so a collapsed projection stays
    collapsed instead of being stretched back out one vector at a time.
    """
    biggest = 0.0
    for concept in range(aligner.concepts):
        for modality in (0, 1):
            observation = aligner.observe(concept, modality=modality)
            point = (
                observation
                if raw
                else aligner.project(observation, modality=modality)
            )
            biggest = max(biggest, max(abs(v) for v in point))
    return max(biggest, 1e-9)


def through_engine(
    aligner: Aligner,
    modality: int,
    samples: range,
    *,
    scale: float,
    rhythm: Rhythm,
    raw: bool = False,
) -> dict[int, list[list[float]]]:
    """Where the ENGINE ends up when told each held-out concept's drive."""
    out: dict[int, list[list[float]]] = {}
    for concept in HELD_OUT:
        readings = []
        for walk, s in enumerate(samples):
            observation = aligner.observe(concept, modality=modality, sample=s)
            point = (
                observation
                if raw
                else aligner.project(observation, modality=modality)
            )
            drive = tuple(max(-1.0, min(1.0, v / scale)) for v in point)
            readings.append(signature(drive, rhythm=rhythm, seed=walk))
        out[concept] = readings
    return out


def engine_score(
    aligner: Aligner, *, rhythm: Rhythm, raw: bool = False
) -> tuple[float, float]:
    """The same identification, read off the engine's trajectory."""
    scale = training_scale(aligner, raw=raw)
    gallery = through_engine(
        aligner, 0, range(1, WALKS + 1), scale=scale, rhythm=rhythm, raw=raw
    )
    probes = through_engine(
        aligner, 1, range(WALKS + 1, WALKS * 2 + 1), scale=scale, rhythm=rhythm, raw=raw
    )
    prototypes = {c: centre(points) for c, points in gallery.items()}
    return (
        identify(prototypes, probes),
        permuted_floor(prototypes, probes, random.Random(17)),
    )


def main() -> None:
    print(
        f"cross-modal identification on {len(HELD_OUT)} held-out concepts, "
        f"{REPEATS} fresh observations each"
    )
    print(f"dim={DIM}, {PAIRS} pairs, {SEEDS} seeds, chance = 1/{len(HELD_OUT)}\n")

    arms: dict[str, list[float]] = {}
    ranks: dict[str, list[float]] = {}
    floors: dict[str, list[float]] = {}

    for seed in range(SEEDS):
        def fresh(**kwargs: object) -> Aligner:
            return Aligner(dim=DIM, concepts=CONCEPTS, seed=seed, **kwargs)

        trained = fresh()
        trained.run(PAIRS)
        shuffled = fresh(shuffled=True)
        shuffled.run(PAIRS)

        readings = {
            "trained": score(trained),
            "untrained": score(fresh()),
            "shuffled": score(shuffled),
            "raw": score(trained, raw=True),
        }
        for name, (accuracy, floor, rank) in readings.items():
            arms.setdefault(name, []).append(accuracy)
            ranks.setdefault(name, []).append(rank)
            floors.setdefault(name, []).append(floor)

    print(f"{'arm':<12}{'accuracy':>12}{'worst seed':>13}{'eff. rank':>12}")
    print("-" * 49)
    for name in ("trained", "raw", "untrained", "shuffled"):
        print(
            f"{name:<12}{statistics.mean(arms[name]):>12.3f}"
            f"{min(arms[name]):>13.3f}{statistics.mean(ranks[name]):>12.2f}"
        )
    every = [f for values in floors.values() for f in values]
    print(f"{'permuted':<12}{statistics.mean(every):>12.3f}{max(every):>13.3f}")
    clears = sum(
        arms["trained"][i] > floors["trained"][i] for i in range(SEEDS)
    )
    print(f"\n  trained clears its OWN permutation ceiling on {clears}/{SEEDS} seeds")

    print("\nper-seed margin over the strongest control (all 12 must be positive)")
    margins = [
        arms["trained"][i] - max(arms["raw"][i], arms["untrained"][i], arms["shuffled"][i])
        for i in range(SEEDS)
    ]
    print("  " + " ".join(f"{m:+.3f}" for m in margins))
    wins = sum(m > 0 for m in margins)
    print(f"  {wins}/{SEEDS} positive")

    if wins < SEEDS:
        print(
            "\nNothing for an engine to carry at this bar. The engine can only"
            "\nlose information, so a bridge cannot recreate what is not here."
        )
        return

    print(
        "\nThere is something for an engine to carry: the concept is"
        "\nrecoverable from the drive, and co-occurrence is what put it there."
    )

    print("\n── stage two: does it survive the engine ──")
    print(
        f"RING, {WALKS} crossed walks per drive, 800 ticks, tail 300, "
        "same scoring as above\n"
    )
    engine: dict[str, list[float]] = {}
    engine_floors: dict[str, list[float]] = {}
    for seed in range(SEEDS):
        trained = Aligner(dim=DIM, concepts=CONCEPTS, seed=seed)
        trained.run(PAIRS)
        shuffled = Aligner(dim=DIM, concepts=CONCEPTS, seed=seed, shuffled=True)
        shuffled.run(PAIRS)
        untrained = Aligner(dim=DIM, concepts=CONCEPTS, seed=seed)

        for name, aligner, rhythm, raw in (
            ("trained", trained, ALTERNATING, False),
            ("raw", trained, ALTERNATING, True),
            ("untrained", untrained, ALTERNATING, False),
            ("shuffled", shuffled, ALTERNATING, False),
            ("deaf (FIXED)", trained, FIXED, False),
        ):
            accuracy, floor = engine_score(aligner, rhythm=rhythm, raw=raw)
            engine.setdefault(name, []).append(accuracy)
            engine_floors.setdefault(name, []).append(floor)

    every_floor = [f for values in engine_floors.values() for f in values]
    ceiling = max(every_floor)
    print(f"{'arm':<14}{'trajectory':>12}{'worst':>9}{'drive':>9}{'survived':>11}")
    print("-" * 55)
    for name in ("trained", "raw", "untrained", "shuffled", "deaf (FIXED)"):
        through = statistics.mean(engine[name])
        before = statistics.mean(arms.get(name.split()[0], arms["trained"]))
        # A ratio between two numbers that are both at the floor is noise
        # wearing a percent sign.
        share = f"{through / before:>10.0%}" if before > ceiling else f"{'—':>10}"
        print(
            f"{name:<14}{through:>12.3f}{min(engine[name]):>9.3f}"
            f"{before:>9.3f}{share}"
        )
    print(
        f"{'permuted':<14}{statistics.mean(every_floor):>12.3f}{ceiling:>9.3f}"
    )
    clears = sum(
        engine["trained"][i] > engine_floors["trained"][i] for i in range(SEEDS)
    )
    print(
        f"\n  trained clears its OWN permutation ceiling on {clears}/{SEEDS} seeds"
        "\n  (each seed against its own 200 re-labellings, not the worst of all"
        "\n   seeds' — a max of maxes is a bar nothing should have to clear)"
    )

    survived = [
        engine["trained"][i]
        - max(engine["raw"][i], engine["untrained"][i], engine["shuffled"][i])
        for i in range(SEEDS)
    ]
    print("\nper-seed margin through the engine (all 12 must be positive)")
    print("  " + " ".join(f"{m:+.3f}" for m in survived))
    print(f"  {sum(m > 0 for m in survived)}/{SEEDS} positive")
    print(
        "\nThe deaf row is the instrument check: at coupling 1.0 the drive is"
        "\nbit-for-bit unreachable, so it must sit at the permutation floor."
    )


if __name__ == "__main__":
    main()
