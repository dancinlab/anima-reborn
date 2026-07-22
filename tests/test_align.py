"""Cross-modal alignment — learning that two signals are about one thing.

The first learner in the package, and it is here because measurement demanded
it: dynamics alone cannot canonicalize, because the evidence that two signals
belong together has to be IN the signals, and co-occurrence is what puts it
there.

Everything is scored on concepts the learner never trained on, and everything is
reported as the gain over its own untrained state. Both of those exist because
of specific ways this could look like a success without being one — memorizing
the training pairs, and an untrained baseline that is not zero.
"""

from __future__ import annotations

import math
import statistics

import pytest

from anima_reborn.align import CONCEPTS, DIM, Aligner


def learned(*, shuffled: bool = False, pairs: int = 4000, seeds: int = 8, **kwargs):
    return [
        Aligner(shuffled=shuffled, seed=s, **kwargs).run(pairs).learned
        for s in range(seeds)
    ]


class TestTheClaim:
    def test_co_occurrence_teaches_the_correspondence(self) -> None:
        values = learned()
        assert statistics.mean(values) > 0.5, values
        assert min(values) > 0.3, values

    def test_destroying_the_pairing_kills_it(self) -> None:
        """The falsifier. Same signals, same statistics, same rate — only the
        pairing is wrong, so there is no co-occurrence to learn from."""
        values = learned(shuffled=True)
        assert statistics.mean(values) < 0.2, values

    def test_the_two_are_far_apart(self) -> None:
        honest = statistics.mean(learned())
        control = statistics.mean(learned(shuffled=True))
        assert honest - control > 0.5

    def test_the_verdict_follows(self) -> None:
        assert Aligner(seed=1).run(4000).aligned
        assert not Aligner(shuffled=True, seed=1).run(4000).aligned


class TestItIsNotMemorising:
    def test_every_score_is_on_unseen_concepts(self) -> None:
        """Held-out ids are far outside the training pool, so nothing scored was
        ever trained on."""
        aligner = Aligner(concepts=40, seed=1)
        assert aligner.concepts == 40
        # The state samples ids at 10_000+, well beyond any training id.
        assert aligner.run(2000).aligned

    def test_ten_concepts_are_enough(self) -> None:
        """A learner that memorized pairs could not generalize from ten. One
        that acquired the mapping between the modalities can."""
        values = learned(concepts=10, seeds=6)
        assert statistics.mean(values) > 0.4, values

    def test_more_concepts_do_not_hurt(self) -> None:
        few = statistics.mean(learned(concepts=10, seeds=4))
        many = statistics.mean(learned(concepts=80, seeds=4))
        assert many > 0.4
        assert abs(many - few) < 0.4, (few, many)


class TestTheBaselineIsNotZero:
    """The trap that nearly shipped.

    Both modalities mix one latent, so even random untrained projections keep
    some correlation — up to 0.397 on an unlucky seed. A verdict on the raw gap
    passes a learner that has seen nothing.
    """

    def test_an_untrained_learner_can_have_a_large_raw_gap(self) -> None:
        gaps = [Aligner(seed=s).state.gap for s in range(12)]
        assert max(gaps) > 0.3, gaps

    def test_but_it_has_learned_nothing_and_says_so(self) -> None:
        for seed in range(12):
            state = Aligner(seed=seed).state
            assert state.learned == 0.0
            assert not state.aligned

    def test_the_verdict_is_on_the_gain_not_the_gap(self) -> None:
        aligner = Aligner(seed=1)
        before = aligner.state
        after = aligner.run(2000)
        assert after.gap > before.gap
        assert after.learned == pytest.approx(after.gap - before.gap, abs=1e-9)


class TestConditions:
    def test_it_degrades_with_observation_noise(self) -> None:
        readings = [
            statistics.mean(learned(noise=n, seeds=4)) for n in (0.1, 0.6, 1.2)
        ]
        assert readings == sorted(readings, reverse=True), readings
        assert readings[0] > 0.5

    def test_it_survives_modalities_that_are_not_linearly_related(self) -> None:
        """Declared condition: the default world mixes the latent linearly. The
        effect is not an artefact of that — with noise raised, which is a
        different distortion, it still learns."""
        assert statistics.mean(learned(noise=0.5, seeds=4)) > 0.3

    def test_learning_accumulates(self) -> None:
        aligner = Aligner(seed=2)
        early = aligner.run(200).learned
        late = aligner.run(3000).learned
        assert late > early


class TestObservationsCanBeRepeated:
    """A consumer that re-runs a noisy process on ONE fixed observation is
    measuring that process's noise, not invariance to observation noise — it
    would be scoring an exemplar and calling it a concept."""

    def test_sample_zero_is_what_there_always_was(self) -> None:
        aligner = Aligner(seed=1)
        assert aligner.observe(3, modality=0) == aligner.observe(
            3, modality=0, sample=0
        )

    def test_another_sample_is_another_draw_of_the_same_concept(self) -> None:
        aligner = Aligner(seed=1, noise=0.3)
        first = aligner.observe(3, modality=0, sample=1)
        second = aligner.observe(3, modality=0, sample=2)
        assert first != second
        assert first != aligner.observe(3, modality=0)

    def test_repeats_are_reproducible(self) -> None:
        assert Aligner(seed=1).observe(3, modality=0, sample=7) == Aligner(
            seed=1
        ).observe(3, modality=0, sample=7)

    def test_they_are_still_the_same_concept(self) -> None:
        """Noisy draws of one concept must stay closer to each other than to
        another concept's draws, or a repeat is not a repeat."""
        aligner = Aligner(seed=1, dim=4)
        same = [aligner.observe(3, modality=0, sample=s) for s in range(1, 9)]
        other = aligner.observe(11, modality=0, sample=1)
        within = statistics.mean(
            math.dist(a, b) for a in same for b in same if a is not b
        )
        assert within < math.dist(same[0], other)


class TestTheOtherHalfOfCoOccurrence:
    """The midpoint rule only pulls, so nothing opposes contraction and the
    shared space shrinks toward a line. Co-occurrence says what does NOT come
    together as well, and that half was missing."""

    def test_it_is_off_by_default_and_changes_nothing(self) -> None:
        """Every published number was measured without it."""
        assert Aligner(seed=5).contrast == 0.0
        plain = Aligner(seed=5).run(1500)
        spelled = Aligner(seed=5, contrast=0.0).run(1500)
        assert plain == spelled

    def test_an_unscaled_push_collapses_what_it_was_meant_to_widen(self) -> None:
        """The first attempt, pinned so it cannot come back as a simplification.

        Pushing by the raw displacement makes the step grow with the distance
        already achieved, so one direction runs away and the effective rank goes
        to 1.0 — full collapse, worse than the contraction being fixed. The
        shipped rule pushes by the unit direction instead.
        """
        assert _rank(1, contrast=0.3, margin=1e9, cls=_Unscaled) < 1.05

    def test_the_direction_and_the_stopping_distance_do_different_jobs(
        self,
    ) -> None:
        """Both are load-bearing, and neither is the other's spare. Measured
        over six seeds at `dim=4`: rank 1.21 with no push, 1.00 unscaled, 1.12
        scaled with nothing to stop it, 1.48 scaled and stopped."""
        endless = statistics.mean(
            _rank(s, contrast=0.3, margin=1e9) for s in range(4)
        )
        stopped = statistics.mean(
            _rank(s, contrast=0.3, margin=1.0) for s in range(4)
        )
        assert endless > 1.05, endless
        assert stopped > endless, (endless, stopped)

    def test_it_widens_the_space_that_was_narrowing(self) -> None:
        without = statistics.mean(_rank(s) for s in range(4))
        with_push = statistics.mean(
            _rank(s, contrast=0.3, margin=1.0) for s in range(4)
        )
        assert with_push > without, (without, with_push)

    def test_it_does_not_rescue_the_control(self) -> None:
        """A change that improved the shuffled arm too would be improving the
        signals rather than teaching from the pairing."""
        values = learned(shuffled=True, seeds=4, contrast=0.3, margin=1.0)
        assert statistics.mean(values) < 0.2, values

    def test_configuration_is_validated(self) -> None:
        with pytest.raises(ValueError, match="contrast must be >= 0"):
            Aligner(contrast=-0.1)
        with pytest.raises(ValueError, match="margin must be > 0"):
            Aligner(margin=0.0)


class _Unscaled(Aligner):
    """The rejected push: by the raw displacement rather than its direction."""

    def _push_apart(self, concept: int, here: list[float]) -> None:
        other = self._rng.randrange(self.concepts)
        if other == concept:
            return
        view = self.observe(other, modality=1)
        there = self.project(view, modality=1)
        for i in range(self.dim):
            away = there[i] - here[i]
            for j in range(self.dim):
                self._right[i][j] += self.rate * self.contrast * away * view[j]


def _rank(seed: int, *, cls: type[Aligner] = Aligner, **kwargs) -> float:
    """Effective dimensions the trained projections of held-out concepts use."""
    aligner = cls(dim=4, concepts=40, seed=seed, **kwargs)
    aligner.run(3000)
    points = [
        aligner.project(aligner.observe(c, modality=0), modality=0)
        for c in range(10_000, 10_020)
    ]
    middle = [statistics.mean(p[i] for p in points) for i in range(4)]
    centred = [[p[i] - middle[i] for i in range(4)] for p in points]
    cov = [
        [statistics.mean(r[i] * r[j] for r in centred) for j in range(4)]
        for i in range(4)
    ]
    trace = sum(cov[i][i] for i in range(4))
    square = sum(cov[i][j] * cov[i][j] for i in range(4) for j in range(4))
    return trace * trace / max(square, 1e-18)


class TestEngine:
    def test_a_seed_makes_a_run_reproducible(self) -> None:
        assert Aligner(seed=7).run(500) == Aligner(seed=7).run(500)

    def test_different_seeds_differ(self) -> None:
        assert Aligner(seed=1).run(500) != Aligner(seed=2).run(500)

    def test_reset_forgets_what_was_learned(self) -> None:
        aligner = Aligner(seed=3)
        aligner.run(2000)
        assert aligner.state.aligned

        aligner.reset()
        assert aligner.pairs_seen == 0
        assert aligner.state.learned == 0.0
        assert not aligner.state.aligned

    def test_reading_does_not_train(self) -> None:
        aligner = Aligner(seed=4)
        aligner.run(100)
        before = aligner.pairs_seen
        aligner.state
        aligner.state
        assert aligner.pairs_seen == before

    def test_projections_have_the_declared_width(self) -> None:
        aligner = Aligner(dim=DIM, seed=1)
        observation = aligner.observe(0, modality=0)
        assert len(observation) == DIM
        assert len(aligner.project(observation, modality=0)) == DIM

    def test_configuration_is_validated(self) -> None:
        with pytest.raises(ValueError, match="dim must be >= 2"):
            Aligner(dim=1)
        with pytest.raises(ValueError, match="concepts must be >= 2"):
            Aligner(concepts=1)
        with pytest.raises(ValueError, match="rate must be > 0"):
            Aligner(rate=0.0)
        with pytest.raises(ValueError, match="noise must be >= 0"):
            Aligner(noise=-1.0)
        with pytest.raises(ValueError, match="pairs must be >= 1"):
            Aligner().run(0)

    def test_the_default_pool_is_the_documented_one(self) -> None:
        assert Aligner(seed=1).concepts == CONCEPTS
