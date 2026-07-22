"""The whole chain on the 3-bit integrated substrate — concepts, held and used.

Run from the repo root:

    PYTHONPATH=src python state/communication/concepts.py

Four things were built and measured separately: the ring INTEGRATES, it HOLDS a
bit through silence, it USES what it holds, and `Wiring.PAIRS` with a chain holds
`units/2` bits while still integrating. Each used designed inputs (cube corners)
to isolate the engine from any learner. This joins them: learned concepts on the
six-unit, three-latch, chained engine, asked whether concept identity is held as
more than one bit and whether the engine uses it.

**The confound the composition creates, and how it is handled.** `chain=0` — three
DISJOINT latches — already holds three bits and each latch passes on its own,
while measuring as reducible (the null that collapses 5.2 -> 2.1). So "concepts
on the integrated substrate pass" would earn only *coexistence*, never "integration
carries concepts". `chain=0` therefore ships as a first-class arm, and the only
place integration can be a FUNCTION rather than a coincidence is the cross-pair
probe (Phase C): a probe that differs only within pair 0 can move pairs 1-2 only
through the chain, and at `chain=0` that path is exactly zero by construction.

**What addresses a latch.** With `Wiring.PAIRS` each pair j is units (2j, 2j+1),
an inverting two-cycle whose DIFFERENTIAL `d[2j] - d[2j+1]` is the bistable mode
that writes the bit; the common mode has negative feedback and dies in silence.
So a concept's usable channel is the three differentials, not the full six-vector,
and the aligner's narrowness could collapse them — which is why Phase 0 measures
the aligner's own address rate with no engine in the path before anything else.

**Gates.** Phase 0 kills the whole thing if the aligned code carries no more than
one bit of address (a lossy engine cannot recreate address diversity never fed to
it). Only if it passes do the engine phases run.
"""

from __future__ import annotations

import collections
import math
import statistics

from anima_reborn.align import Aligner
from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

DIM = 6
CONCEPTS = 40
HELD_OUT = list(range(10_000, 10_020))
CONTRAST = 0.3
MARGIN = 1.0
PAIRS = 3
CHAIN = 0.2

TELL = 400
SILENCE = 240
PROBE = 20
WALKS = 8
SAMPLES = 12
SEEDS = 8
PAIRS_ARM = Wiring.PAIRS


def aligned(seed: int, *, shuffled: bool = False, contrast: float = CONTRAST) -> Aligner:
    learner = Aligner(
        dim=DIM, concepts=CONCEPTS, seed=seed, contrast=contrast, margin=MARGIN,
        shuffled=shuffled,
    )
    learner.run(4000)
    return learner


def drive_of(
    learner: Aligner, concept: int, modality: int, sample: int, scale: float
) -> tuple[float, ...]:
    point = learner.project(
        learner.observe(concept, modality=modality, sample=sample), modality=modality
    )
    return tuple(max(-1.0, min(1.0, v / scale)) for v in point)


def training_scale(learner: Aligner, modality: int) -> float:
    biggest = 0.0
    for concept in range(learner.concepts):
        point = learner.project(learner.observe(concept, modality=modality), modality=modality)
        biggest = max(biggest, max(abs(v) for v in point))
    return max(biggest, 1e-9)


def differentials(drive: tuple[float, ...]) -> tuple[float, ...]:
    """The three writable functionals — one per latch."""
    return tuple(drive[2 * j] - drive[2 * j + 1] for j in range(PAIRS))


def address(drive: tuple[float, ...]) -> tuple[bool, ...]:
    return tuple(d > 0 for d in differentials(drive))


# ── Phase 0: can the aligned code even address three latches? (no engine) ──
def phase0() -> bool:
    print("Phase 0 — aligner address rate, no engine in the path")
    print(f"{'arm':<12}{'stable concepts':>16}{'distinct words':>16}{'bits':>7}")
    print("-" * 51)
    verdict = {}
    for name, shuffled in (("trained", False), ("shuffled", True)):
        words, stable, bits = [], [], []
        for seed in range(SEEDS):
            learner = aligned(seed, shuffled=shuffled)
            scale = training_scale(learner, 0)
            seed_words = set()
            seed_stable = 0
            for concept in HELD_OUT:
                addrs = {
                    address(drive_of(learner, concept, 0, s, scale))
                    for s in range(1, SAMPLES + 1)
                }
                if len(addrs) == 1:
                    seed_stable += 1
                    seed_words |= addrs
            words.append(len(seed_words))
            stable.append(seed_stable / len(HELD_OUT))
            bits.append(math.log2(len(seed_words)) if seed_words else 0.0)
        verdict[name] = (statistics.mean(words), statistics.mean(bits))
        print(
            f"{name:<12}{statistics.mean(stable):>15.0%}"
            f"{statistics.mean(words):>16.1f}{statistics.mean(bits):>7.2f}",
            flush=True,
        )
    passed = verdict["trained"][1] > 1.0 and verdict["trained"][0] > verdict["shuffled"][0]
    print(
        f"\n  {'PASS' if passed else 'KILL'}: trained carries "
        f"{verdict['trained'][1]:.2f} bits of address"
        f"{' (> 1, and beats shuffled)' if passed else ' — one bit or less, dead here'}\n"
    )
    return passed


# ── engine helpers ──
def hold(
    learner: Aligner, concept: int, modality: int, *, seed: int, chain: float, scale: float
) -> tuple[bool, ...]:
    """The three latch bits after telling a concept and going deaf."""
    engine = CoupledEngine(
        wiring=PAIRS_ARM, units=DIM, chain=chain, rhythm=ALTERNATING,
        drive=drive_of(learner, concept, modality, 0, scale), seed=seed, initial=(0.0,) * DIM,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    values = engine.run(SILENCE).values
    return tuple((values[2 * j] - values[2 * j + 1]) > 0 for j in range(PAIRS))


def _permuted_floor(held_by_concept, top_by_concept) -> float:
    """Cross-modal agreement with the concept labels shuffled — what this match
    reports for no correspondence. The empirical floor beside the shuffled arm."""
    import random as _random
    concepts = list(top_by_concept)
    rng = _random.Random(17)
    best = 0.0
    for _ in range(200):
        order = list(concepts)
        rng.shuffle(order)
        agree = statistics.mean(
            1.0 if held_by_concept[a] == top_by_concept[b] else 0.0
            for a, b in zip(concepts, order)
        )
        best = max(best, agree)
    return best


# ── Phase B: does the aligned CONCEPT survive silence, across modalities? ──
def phaseB() -> None:
    print("Phase B — the aligned concept surviving silence, read across modalities")
    print(f"tell {TELL}, deaf silence {SILENCE}, {WALKS} walks, {SEEDS} seeds\n")
    print(
        "cross-modal agreement is the headline: a concept told through modality 0"
        "\nand held through silence lands on the same latch word as the same concept"
        "\ntold through modality 1. distinct words is a CONTROL column — shuffled"
        "\nuses just as many, so word count is basin occupancy, not concept memory.\n"
    )
    print(
        f"{'arm':<20}{'cross-modal':>12}{'worst seed':>12}"
        f"{'perm floor':>12}{'words':>7}"
    )
    print("-" * 63)

    for name, shuffled, chain in (
        ("chained (3-bit)", False, CHAIN),
        ("disjoint chain=0", False, 0.0),
        ("shuffled aligner", True, CHAIN),
    ):
        per_seed_agree, per_seed_words, floors = [], [], []
        for seed in range(SEEDS):
            learner = aligned(seed, shuffled=shuffled)
            scale0 = training_scale(learner, 0)
            scale1 = training_scale(learner, 1)
            words = set()
            top_by_concept, held1_by_concept = {}, {}
            for concept in HELD_OUT:
                held0 = [
                    hold(learner, concept, 0, seed=w, chain=chain, scale=scale0)
                    for w in range(WALKS)
                ]
                top, n = collections.Counter(held0).most_common(1)[0]
                if n == WALKS:
                    words.add(top)
                top_by_concept[concept] = top
                held1_by_concept[concept] = hold(
                    learner, concept, 1, seed=0, chain=chain, scale=scale1
                )
            per_seed_agree.append(
                statistics.mean(
                    1.0 if held1_by_concept[c] == top_by_concept[c] else 0.0
                    for c in HELD_OUT
                )
            )
            floors.append(_permuted_floor(held1_by_concept, top_by_concept))
            per_seed_words.append(len(words))
        print(
            f"{name:<20}{statistics.mean(per_seed_agree):>11.0%}"
            f"{min(per_seed_agree):>12.0%}{statistics.mean(floors):>12.0%}"
            f"{statistics.mean(per_seed_words):>7.1f}",
            flush=True,
        )

    print(
        "\n  Storage does NOT require integration: chain=0 (three disjoint latches,"
        "\n  which measure as reducible) holds the concept across modalities just as"
        "\n  well. That is the confound made explicit — passing here is coexistence,"
        "\n  not 'integration carries the concept'. Phase C is where integration is a"
        "\n  function rather than a coincidence.\n"
    )


# ── Phase C: does the integrated whole respond where disjoint parts cannot? ──
def phaseC() -> None:
    """The cross-pair probe. A probe that differs only within pair 0 can move
    pairs 1-2 only through the chain; at chain=0 that response is exactly zero by
    construction, so a nonzero response IS integration acting as function."""
    print("Phase C — cross-pair response: is integration a function, not a coincidence?")
    print("a probe differing only in pair 0; measure how much pairs 1-2 move\n")
    print(f"{'chain':<10}{'pairs 1-2 response':>20}   reading")
    print("-" * 52)

    for chain in (0.0, CHAIN):
        responses = []
        for seed in range(SEEDS):
            learner = aligned(seed)
            scale = training_scale(learner, 0)
            for concept in HELD_OUT[:8]:
                held = list(
                    _hold_state(learner, concept, seed=seed, chain=chain, scale=scale)
                )
                base = _probe_move(held, held, chain=chain, seed=seed)
                flipped = list(held)
                flipped[0], flipped[1] = held[1], held[0]  # flip pair 0 only
                moved = _probe_move(held, flipped, chain=chain, seed=seed)
                # response of pairs 1-2 to a pair-0-only change
                responses.append(abs(moved - base))
        mean = statistics.mean(responses)
        reading = (
            "exactly zero — disjoint parts cannot respond"
            if mean < 1e-9
            else "nonzero — the chain carries the influence"
        )
        print(f"{chain:<10.1f}{mean:>20.6f}   {reading}", flush=True)
    print(
        "\n  chain=0 is zero BY CONSTRUCTION (no causal path between pairs), so a"
        "\n  nonzero chained response is the integrated whole doing what its parts"
        "\n  cannot — the one sentence coexistence cannot fake."
    )


def _hold_state(
    learner: Aligner, concept: int, *, seed: int, chain: float, scale: float
) -> tuple[float, ...]:
    engine = CoupledEngine(
        wiring=PAIRS_ARM, units=DIM, chain=chain, rhythm=ALTERNATING,
        drive=drive_of(learner, concept, 0, 0, scale), seed=seed, initial=(0.0,) * DIM,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    return engine.run(SILENCE).values


def _probe_move(
    held: list[float], start: list[float], *, chain: float, seed: int
) -> float:
    """Total movement of pairs 1-2 over a probe cycle, from a given start."""
    engine = CoupledEngine(
        wiring=PAIRS_ARM, units=DIM, chain=chain, rhythm=ALTERNATING,
        drive=0.0, seed=seed, initial=tuple(start),
    )
    moved = 0.0
    for _ in range(PROBE):
        values = engine.step().values
        moved += sum((values[i] - held[i]) ** 2 for i in range(2, DIM))
    return moved


def main() -> None:
    if not phase0():
        print("Dead at the aligner. The engine cannot recreate address diversity")
        print("that was never fed to it — the fix is upstream, in align.py.")
        return
    phaseB()
    phaseC()


if __name__ == "__main__":
    main()
