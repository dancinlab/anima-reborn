"""Learning that two very different signals are about the same thing.

Everything before this in the package is fixed: the wiring is given, the
constants are given, and nothing the engines meet ever changes them. This is the
first module that **learns**, and it is here because measurement demanded it
rather than because learning is interesting.

The chain that led here. `words.py` established that the substrate carries the
code and not the concept. The obvious fix — check whether one concept arriving
through two encodings lands in the same place — turned out to be an impossible
test: two independent hashes of one word share 0.0185 bits against a shuffled
null of 0.0212, so there is nothing in them to recover. Planting attractors
(`state/communication/attractor_canonicalization.py`) did not help either; a
substrate with no attractors agreed exactly as often, to the digit.

What that leaves is the shape of the real problem. **Two signals can only be
recognized as one concept if the evidence that they belong together is in the
signals — and what puts it there is co-occurrence, not dynamics.** Using
co-occurrence means changing with experience. Hence this.

**The mechanism.** Two modalities, each with its own projection. A pair arrives
together, and each projection is nudged toward the midpoint of where the two
currently land. Nothing else. There is no global objective — in particular
nothing maximizes Phi or mutual information, which this repo refused for the
good reason that an optimizer harvests the estimator's artefact.

**What makes it more than memorizing.** It is scored on concepts it never
trained on. Ten training concepts are enough to align concepts it has never
seen, so what it acquired is the correspondence between the modalities rather
than a table of pairs.

**The falsifier ships with it.** `shuffled=True` trains on the same signals with
the pairing destroyed — same statistics, same rate, same everything, no
co-occurrence. Over twelve seeds an honest run gains 0.780 and the control gains
-0.067.

**And the baseline is not zero.** Both modalities mix the same latent, so even
untrained random projections retain correlation — up to 0.397 on an unlucky
seed. Everything is therefore reported as the gain over this learner's OWN
untrained gap, because a verdict on the raw number would pass a learner that
never saw anything.

**What this is not.** It is two learned linear maps. Calling that understanding
would be the overclaim this repo keeps refusing; what it earns is that two
dissimilar signals about one thing can be brought to one place, and that the
bringing generalizes. Whether anything downstream *uses* that is a separate
question nothing here answers.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass

__all__ = ["Aligner", "AlignState", "DIM", "CONCEPTS", "NOISE", "RATE"]

DIM = 6
"""Width of a modality vector, and of the shared space they are brought into."""

CONCEPTS = 40
"""Concepts in the training pool. Ten already suffice — measured gap +0.748 at
ten, +0.519 at five — which is the evidence that the correspondence is what is
learned rather than the pairs."""

HELD_OUT = 20
"""Concepts kept out of training entirely. Every reported number is scored on
these; a learner that only memorized reads zero here."""

NOISE = 0.3
"""Per-component observation noise on each modality. The gap degrades gracefully
with it: +0.948 / +0.716 / +0.421 / +0.103 at 0.1 / 0.3 / 0.6 / 1.0."""

RATE = 0.01
"""Learning rate of the nudge toward the midpoint."""

INITIAL_SCALE = 0.3
"""Projections start random, and must. Starting at zero makes both projections
land on the origin, the midpoint is the origin too, and the update is
identically zero forever — the learner never leaves its initial state."""


def _concept_vector(concept: int, dim: int) -> list[float]:
    """A concept's latent value. Hashed so it is deterministic across runs and
    carries no structure anyone designed."""
    digest = hashlib.blake2b(f"c|{concept}".encode(), digest_size=dim).digest()
    return [(b / 255.0) * 2 - 1 for b in digest]


@dataclass(frozen=True, slots=True)
class AlignState:
    """How well the two modalities have been brought together.

    Every field is scored on held-out concepts. Training-set agreement is not
    reported at all, because it cannot distinguish learning from memorizing.
    """

    same_concept: float
    """Mean cosine between the two projections when both come from ONE held-out
    concept. In [-1, 1]."""
    different_concept: float
    """The same, for projections of two DIFFERENT held-out concepts."""
    initial_gap: float
    """What this learner's gap was before it saw anything.

    Not zero, and that matters. Both modalities are mixings of one latent, so
    even random projections of them retain some correlation — measured over
    twelve seeds the untrained gap averages 0.049 but reaches 0.397 on the
    unluckiest. A verdict on the raw gap would let an untrained learner pass.
    """
    pairs_seen: int

    @property
    def gap(self) -> float:
        """How much closer one concept's two views are than two concepts' views.
        Read `learned` instead unless you want the raw number."""
        return self.same_concept - self.different_concept

    @property
    def learned(self) -> float:
        """The gap this learner ADDED. The only number that is about learning."""
        return self.gap - self.initial_gap

    @property
    def aligned(self) -> bool:
        """Measured against the shuffled control rather than chosen: over twelve
        seeds an honest run gains 0.780 (worst 0.566) and the control gains
        -0.067 (worst -0.428). The bar sits between them with room on both."""
        return self.learned > 0.3

    def __str__(self) -> str:
        return (
            f"learned={self.learned:+.3f} (gap {self.gap:+.3f} from "
            f"{self.initial_gap:+.3f}) after {self.pairs_seen} pairs"
            f"{' [aligned]' if self.aligned else ''}"
        )


class Aligner:
    """Two modalities of one world, and the correspondence between them.

    Args:
        dim: Width of each modality and of the shared space.
        concepts: Size of the training pool.
        noise: Observation noise per component.
        rate: How far each projection moves toward the midpoint per pair.
        shuffled: **The falsifier.** Pair each modality-A observation with a
            different concept's modality-B observation — same signals, same
            statistics, co-occurrence destroyed. Public API rather than a test
            fixture, because the claim is that co-occurrence is what teaches,
            and that is only checkable if it can be removed.
        seed: Fixes the modalities, the noise and the initial projections.
    """

    def __init__(
        self,
        *,
        dim: int = DIM,
        concepts: int = CONCEPTS,
        noise: float = NOISE,
        rate: float = RATE,
        shuffled: bool = False,
        seed: int | None = None,
    ) -> None:
        if dim < 2:
            raise ValueError(f"dim must be >= 2, got {dim}")
        if concepts < 2:
            raise ValueError(f"concepts must be >= 2, got {concepts}")
        if rate <= 0.0:
            raise ValueError(f"rate must be > 0, got {rate}")
        if noise < 0.0:
            raise ValueError(f"noise must be >= 0, got {noise}")

        self.dim = dim
        self.concepts = concepts
        self.noise = noise
        self.rate = rate
        self.shuffled = shuffled
        self._seed = seed
        self._rng = random.Random(seed)
        self._world = self._make_world()
        self._left, self._right = self._initial_projections()
        self._pairs = 0
        self._held_out_views: list[tuple[list[float], list[float]]] | None = None
        self._initial_gap = self._measure().gap

    # ── the world ──────────────────────────────────────────────────────────
    def _make_world(self) -> tuple[list[list[float]], list[list[float]]]:
        """Two ways of looking at the same concepts. Each modality is its own
        random mixing of the latent, so neither resembles the other."""
        rng = random.Random(self._rng.getrandbits(32))
        return (
            [[rng.gauss(0, 1) for _ in range(self.dim)] for _ in range(self.dim)],
            [[rng.gauss(0, 1) for _ in range(self.dim)] for _ in range(self.dim)],
        )

    def _initial_projections(self) -> tuple[list[list[float]], list[list[float]]]:
        rng = random.Random(self._rng.getrandbits(32))
        return (
            [
                [rng.gauss(0, INITIAL_SCALE) for _ in range(self.dim)]
                for _ in range(self.dim)
            ],
            [
                [rng.gauss(0, INITIAL_SCALE) for _ in range(self.dim)]
                for _ in range(self.dim)
            ],
        )

    def observe(self, concept: int, *, modality: int) -> list[float]:
        """One noisy observation of a concept through one modality."""
        latent = _concept_vector(concept, self.dim)
        mixing = self._world[modality]
        rng = random.Random((concept * 2 + modality) ^ (self._seed or 0))
        return [
            sum(mixing[i][j] * latent[j] for j in range(self.dim))
            + rng.gauss(0, self.noise)
            for i in range(self.dim)
        ]

    def project(self, observation: list[float], *, modality: int) -> list[float]:
        """Where a modality's observation lands in the shared space."""
        weights = self._left if modality == 0 else self._right
        return [
            sum(weights[i][j] * observation[j] for j in range(self.dim))
            for i in range(self.dim)
        ]

    # ── learning ───────────────────────────────────────────────────────────
    def step(self) -> None:
        """Take one co-occurring pair and nudge both projections together.

        The rule is local: each projection moves toward the midpoint of where
        the two currently land. Nothing computes a global score, which is what
        keeps the refused Phi-optimizer out.

        Returns nothing on purpose, unlike the engines. Learning is cheap and
        scoring is not — `state` re-measures every held-out pair — so returning
        a reading from every step would make a run of a few thousand pairs
        thousands of times more expensive than the learning it is doing.
        """
        concept = self._rng.randrange(self.concepts)
        partner = concept
        if self.shuffled:
            # Same observations, wrong partner — co-occurrence removed.
            partner = self._rng.randrange(self.concepts)

        left_view = self.observe(concept, modality=0)
        right_view = self.observe(partner, modality=1)
        here = self.project(left_view, modality=0)
        there = self.project(right_view, modality=1)
        midpoint = [(here[i] + there[i]) / 2 for i in range(self.dim)]

        for i in range(self.dim):
            left_error = midpoint[i] - here[i]
            right_error = midpoint[i] - there[i]
            for j in range(self.dim):
                self._left[i][j] += self.rate * left_error * left_view[j]
                self._right[i][j] += self.rate * right_error * right_view[j]

        self._pairs += 1

    def run(self, pairs: int) -> AlignState:
        """Learn from `pairs` pairs, then measure once."""
        if pairs < 1:
            raise ValueError(f"pairs must be >= 1, got {pairs}")
        for _ in range(pairs):
            self.step()
        return self.state

    # ── reading ────────────────────────────────────────────────────────────
    @property
    def pairs_seen(self) -> int:
        return self._pairs

    @property
    def state(self) -> AlignState:
        """Scored on held-out concepts only — reading does not train."""
        return self._measure()

    def _measure(self) -> AlignState:
        # The world never changes, so the held-out observations are the same
        # every time; only the projections move. Caching them turns scoring
        # from the dominant cost into a small one.
        if self._held_out_views is None:
            self._held_out_views = [
                (self.observe(c, modality=0), self.observe(c, modality=1))
                for c in range(10_000, 10_000 + HELD_OUT)
            ]
        views = self._held_out_views

        same = [
            _cosine(self.project(a, modality=0), self.project(b, modality=1))
            for a, b in views
        ]
        different = [
            _cosine(
                self.project(views[i][0], modality=0),
                self.project(views[j][1], modality=1),
            )
            for i in range(len(views))
            for j in range(len(views))
            if i != j
        ]
        return AlignState(
            same_concept=sum(same) / len(same),
            different_concept=sum(different) / len(different),
            initial_gap=getattr(self, "_initial_gap", 0.0),
            pairs_seen=self._pairs,
        )

    def reset(self) -> None:
        """Forget everything learned. The world stays — a different world would
        be a different experiment."""
        self._left, self._right = self._initial_projections()
        self._pairs = 0
        self._initial_gap = self._measure().gap


def _cosine(u: list[float], v: list[float]) -> float:
    left = math.sqrt(sum(x * x for x in u))
    right = math.sqrt(sum(x * x for x in v))
    return sum(x * y for x, y in zip(u, v)) / max(left * right, 1e-9)
