"""Words as a drive — and the two ways this experiment lies if left alone.

The question: put words into A and G, does emergence happen? It does, but only
under conditions that had to be measured rather than assumed, and the naive
version of the experiment reports emergence for words with no relation at all.

These tests pin both the signal and the two traps, so neither can be quietly
lost: the substrate erases words used as initial conditions, and the estimator
manufactures over half a bit when the window holds too few independent draws.
"""

from __future__ import annotations

import math
import random
import statistics

import pytest

from anima_reborn import Emergence, RepulsionField
from anima_reborn.info import Binning, entropy, joint_entropy
from anima_reborn.iit4 import big_phi
from anima_reborn.pipeline import DAMPING, PULL, WALK
from anima_reborn.substrate import estimate_matrix
from anima_reborn.words import (
    HOLD,
    Channel,
    MIN_EFFECTIVE_SAMPLES,
    WINDOW,
    blake_scalar,
    drive,
    measure,
    measure_channel,
)

VOCAB = ["고양이", "자동차", "바다", "연필", "하늘", "돌멩이", "웃음", "기차", "빵", "별"]

WINDOW_FAST = HOLD * MIN_EFFECTIVE_SAMPLES
"""Half the default window — still trustworthy, and the suite stays quick."""


def sequence(length: int = 200, *, seed: int) -> list[str]:
    rng = random.Random(seed)
    return [rng.choice(VOCAB) for _ in range(length)]


def mean_excess(words_a, words_g, *, seeds: int = 4, **kwargs) -> float:
    kwargs.setdefault("window", WINDOW_FAST)
    return statistics.mean(
        measure(words_a, words_g, seed=s, **kwargs).excess for s in range(seeds)
    )


class TestDoesEmergenceHappen:
    """The answer, and how it depends on how much the sequences share."""

    def test_the_same_words_in_both_engines_emerge(self) -> None:
        related = sequence(seed=7)
        assert mean_excess(related, related) > 0.30

    def test_unrelated_words_do_not(self) -> None:
        assert mean_excess(sequence(seed=7), sequence(seed=8)) < 0.05

    def test_the_excess_tracks_how_much_the_sequences_share(self) -> None:
        base = sequence(seed=7)
        rng = random.Random(11)
        half = base[:100] + [rng.choice(VOCAB) for _ in range(100)]

        readings = [
            mean_excess(base, sequence(seed=8)),  # nothing shared
            mean_excess(base, base[1:] + base[:1]),  # shifted by one
            mean_excess(base, half),  # half shared
            mean_excess(base, base),  # identical
        ]
        assert readings == sorted(readings), readings
        assert readings[-1] - readings[0] > 0.30

    def test_the_verdict_follows_the_excess(self) -> None:
        related = sequence(seed=7)
        assert measure(related, related, window=WINDOW_FAST, seed=1).verdict is (
            Emergence.EMERGENT
        )
        assert measure(
            related, sequence(seed=8), window=WINDOW_FAST, seed=1
        ).verdict is Emergence.INDEPENDENT


class TestTransmittedNotCreated:
    """The claim that keeps the headline honest.

    A and G never read each other — the gap between them is a readout, not a
    channel — so independent inputs give independent outputs by construction.
    The substrate carries a relationship; it cannot manufacture one, and if any
    of this ever measured otherwise it would mean a coupling had been
    introduced somewhere it does not belong.
    """

    def test_independent_words_produce_no_binding_on_any_seed(self) -> None:
        readings = [
            measure(sequence(seed=7), sequence(seed=8), window=WINDOW_FAST, seed=s)
            for s in range(8)
        ]
        for reading in readings:
            assert abs(reading.excess) < 0.05, reading
            assert reading.verdict is Emergence.INDEPENDENT

    def test_the_substrate_has_no_phi_to_give(self) -> None:
        """Every dimension updates from itself and its own target, so the
        transition matrix factorizes and no cut destroys anything. Four
        distinctions exist; none of them are integrated."""
        wa, wg = blake_scalar("고양이"), blake_scalar("자동차")

        def step(state: int, rng: random.Random) -> int:
            values = []
            for i, target in enumerate((wa, wa * 0.8, wg, wg * 0.8)):
                x = 0.2 if state >> i & 1 else -0.2
                x += (rng.random() - 0.5) * WALK
                x += (target - x) * PULL
                values.append(x)
            return sum(1 << i for i, v in enumerate(values) if v > 0)

        measured = big_phi(estimate_matrix(4, step, trials=400, seed=1), 0b1111)
        assert measured.phi == 0.0
        assert measured.structure.distinctions, "it does specify things"


class TestTheSubstrateErasesAnInitialCondition:
    """Why words are a continuing drive here and not a starting vector."""

    def test_two_different_starts_converge_to_the_same_trajectory(self) -> None:
        """Same noise, different starting words: the gap between the two
        trajectories collapses long before an emergence verdict could exist."""

        def field(word: str) -> RepulsionField:
            vector = [blake_scalar(word + str(i)) / 2 for i in range(16)]
            anchor = [blake_scalar("anchor" + str(i)) / 2 for i in range(16)]
            return RepulsionField(
                seed=1, clock=lambda: 0.0, initial=(vector, anchor)
            )

        first, second = field("고양이"), field("자동차")
        start = math.dist(first.a, second.a)

        for _ in range(600):
            first.step()
            second.step()

        assert start > 0.5, "the two starts must actually differ"
        assert math.dist(first.a, second.a) < 0.01

    def test_the_washout_is_the_substrate_not_the_encoding(self) -> None:
        """Three unrelated encodings, same decay — so it is `PULL` and
        `DAMPING` doing it, not a property of how words became numbers."""
        decay_times = []
        for scale in (1.0, 0.5, 0.25):

            def field(word: str, scale: float = scale) -> RepulsionField:
                vector = [blake_scalar(word + str(i)) * scale for i in range(16)]
                anchor = [blake_scalar("anchor" + str(i)) * scale for i in range(16)]
                return RepulsionField(
                    seed=1, clock=lambda: 0.0, initial=(vector, anchor)
                )

            first, second = field("고양이"), field("자동차")
            start = math.dist(first.a, second.a)
            ticks = 0
            while math.dist(first.a, second.a) > start * 0.01 and ticks < 2000:
                first.step()
                second.step()
                ticks += 1
            decay_times.append(ticks)

        assert max(decay_times) - min(decay_times) < 60, decay_times

    def test_the_decay_matches_the_constants(self) -> None:
        """`DAMPING` puts 1% survival at ~305 ticks, which is what the sweep
        above lands on — the constant, not a coincidence."""
        assert math.log(0.01) / math.log(DAMPING) == pytest.approx(305, abs=5)


class TestTheEstimatorTrap:
    """Too few independent draws and the estimator invents emergence."""

    def test_independent_words_read_far_above_zero_on_a_short_window(self) -> None:
        """The trap, stated as measured rather than as feared.

        Two unrelated word sequences have a true mutual information of exactly
        zero. At eight effective samples the raw estimate averages 0.222 bits —
        about forty times what the same pair reads once the window is honest —
        and the spread reaches past the 0.30 emergence bar on some seeds. So the
        failure is not "always looks emergent"; it is "inflated by a factor of
        tens, and occasionally over the line", which is worse, because it looks
        like an ordinary noisy measurement.
        """
        raw = [
            measure(
                sequence(seed=7), sequence(seed=8), hold=25, window=200, seed=s
            ).mutual_information
            for s in range(12)
        ]
        honest = [
            measure(
                sequence(seed=7), sequence(seed=8), window=WINDOW_FAST, seed=s
            ).mutual_information
            for s in range(12)
        ]
        assert statistics.mean(raw) > 20 * statistics.mean(honest)
        assert max(raw) > 0.30, "at least one seed crosses the bar on noise alone"
        assert max(honest) < 0.05

    def test_but_the_reading_refuses_to_call_it(self) -> None:
        reading = measure(
            sequence(seed=7), sequence(seed=8), hold=25, window=200, seed=1
        )
        assert not reading.trustworthy
        assert reading.effective_samples < MIN_EFFECTIVE_SAMPLES
        assert reading.verdict is Emergence.INDEPENDENT
        assert "⚠" in str(reading)

    def test_the_bias_shrinks_with_effective_samples(self) -> None:
        """What makes the artefact an artefact. True value is zero throughout."""
        binning = Binning(bins=12, vrange=1.6)

        def bias(hold: int, window: int) -> float:
            def stream(seed: int) -> list[float]:
                rng = random.Random(seed)
                words = [rng.choice(VOCAB) for _ in range(window // hold + 2)]
                flat = [blake_scalar(w) for w in words for _ in range(hold)]
                return flat[:window]

            values = []
            for seed in range(4):
                left, right = stream(seed), stream(seed + 9999)
                values.append(
                    max(
                        0.0,
                        entropy(left, binning)
                        + entropy(right, binning)
                        - joint_entropy(left, right, binning),
                    )
                )
            return statistics.mean(values)

        few = bias(25, 200)  # 8 effective samples
        many = bias(25, 20_000)  # 800
        assert few > 0.30, few
        assert many < 0.05, many

    def test_a_time_shift_is_a_stricter_null_than_a_shuffle(self) -> None:
        """Why the null rotates rather than reshuffles.

        A rotation keeps the stream's own autocorrelation and removes only the
        alignment; rebuilding from shuffled words loses some of that structure
        and so reads LOW, which would flatter every excess by the difference.
        """
        words = sequence(seed=7)
        left = drive(words, ticks=WINDOW_FAST, rng=random.Random(1))
        right = drive(words, ticks=WINDOW_FAST, rng=random.Random(2))
        binning = Binning(bins=12, vrange=1.6)

        def against(other: list[float]) -> float:
            return max(
                0.0,
                entropy(left, binning)
                + entropy(other, binning)
                - joint_entropy(left, other, binning),
            )

        rotated = statistics.median(
            against(right[d:] + right[:d]) for d in (37, 83, 127)
        )
        reshuffled = list(words)
        random.Random(3).shuffle(reshuffled)
        rebuilt = against(drive(reshuffled, ticks=WINDOW_FAST, rng=random.Random(4)))
        assert rotated > rebuilt

    def test_a_time_shift_is_a_stricter_null_than_a_shuffle(self) -> None:
        """Why the null rotates rather than reshuffles.

        A rotation keeps the stream's own autocorrelation and removes only the
        alignment. Rebuilding the stream from shuffled words loses some of that
        structure too, so it reads LOW — and a null that reads low flatters
        every excess measured against it. Measured on the same unrelated pair:
        0.0182 rotated against 0.0120 reshuffled.
        """
        words = sequence(seed=7)
        left = drive(words, ticks=WINDOW_FAST, rng=random.Random(1))
        right = drive(words, ticks=WINDOW_FAST, rng=random.Random(2))
        binning = Binning(bins=12, vrange=1.6)

        def against(other: list[float]) -> float:
            return max(
                0.0,
                entropy(left, binning)
                + entropy(other, binning)
                - joint_entropy(left, other, binning),
            )

        rotated = statistics.median(
            against(right[shift:] + right[:shift]) for shift in (37, 83, 127)
        )
        reshuffled = list(words)
        random.Random(3).shuffle(reshuffled)
        rebuilt = against(drive(reshuffled, ticks=WINDOW_FAST, rng=random.Random(4)))

        assert rotated > rebuilt, (rotated, rebuilt)

    def test_the_null_does_not_care_what_the_words_are(self) -> None:
        """The control measures the estimator, not the relationship — so it
        should read the same whether the sequences are identical or unrelated.
        If it ever tracked the words, it would be subtracting real signal."""
        related = sequence(seed=7)
        same = statistics.mean(
            measure(related, related, window=WINDOW_FAST, seed=s).control
            for s in range(4)
        )
        different = statistics.mean(
            measure(related, sequence(seed=8), window=WINDOW_FAST, seed=s).control
            for s in range(4)
        )
        assert same == pytest.approx(different, abs=0.02)


class TestTheSubstrateHasToKeepUp:
    def test_words_faster_than_the_time_constant_are_filtered_away(self) -> None:
        """A word the engine cannot reach is a word it cannot carry. Effective
        samples are held constant, so this is not the estimator talking."""
        related = sequence(seed=7)
        fast = mean_excess(related, related, hold=2, window=2 * 800, seeds=3)
        matched = mean_excess(related, related, hold=17, window=17 * 800, seeds=3)
        assert fast < 0.15
        assert matched > 0.30
        assert matched > 3 * fast

    def test_the_default_hold_is_the_substrate_time_constant(self) -> None:
        assert HOLD == pytest.approx(1 / PULL, abs=1.0)

    def test_the_default_window_keeps_the_estimate_trustworthy(self) -> None:
        assert WINDOW // HOLD >= MIN_EFFECTIVE_SAMPLES


class TestEncodingIndependence:
    def test_the_contrast_survives_a_different_encoding(self) -> None:
        """Absolute values belong to the encoding; the contrast should not."""

        def reversed_hash(word: str) -> float:
            return blake_scalar(word[::-1] + "salt")

        related = sequence(seed=7)
        for encode in (blake_scalar, reversed_hash):
            same = mean_excess(related, related, encode=encode, seeds=3)
            different = mean_excess(
                related, sequence(seed=8), encode=encode, seeds=3
            )
            assert same > 0.30, encode.__name__
            assert different < 0.05, encode.__name__


class TestDrive:
    def test_it_returns_one_observation_per_tick(self) -> None:
        assert len(drive(["가"], ticks=250)) == 250

    def test_it_follows_the_word(self) -> None:
        """Driven long enough by one word, the engine sits near its value."""
        word = "고양이"
        settled = drive([word], ticks=400, rng=random.Random(1))[-100:]
        assert statistics.mean(settled) == pytest.approx(blake_scalar(word), abs=0.15)

    def test_a_short_sequence_repeats(self) -> None:
        observations = drive(["가", "나"], hold=2, ticks=100, rng=random.Random(1))
        assert len(observations) == 100

    def test_configuration_is_validated(self) -> None:
        with pytest.raises(ValueError, match="at least one word"):
            drive([])
        with pytest.raises(ValueError, match="hold must be >= 1"):
            drive(["가"], hold=0)
        with pytest.raises(ValueError, match="ticks must be >= 1"):
            drive(["가"], ticks=0)


class TestReading:
    def test_a_seed_makes_a_measurement_reproducible(self) -> None:
        words = sequence(seed=7)
        first = measure(words, words, window=WINDOW_FAST, seed=42)
        second = measure(words, words, window=WINDOW_FAST, seed=42)
        assert first == second

    def test_excess_is_the_difference(self) -> None:
        reading = measure(sequence(seed=7), sequence(seed=8), window=WINDOW_FAST, seed=1)
        assert reading.excess == reading.mutual_information - reading.control

    def test_it_reports_its_own_effective_samples(self) -> None:
        reading = measure(
            sequence(seed=7), sequence(seed=7), hold=10, window=5000, seed=1
        )
        assert reading.effective_samples == 500


class TestCreatedBinding:
    """The sentence this module previously proved false.

    `measure` shows an uncoupled substrate only ever transmits what its inputs
    already shared. `measure_channel` asks whether a live loop can *create*
    dependence between inputs that share nothing — and it can, modestly.

    Measured at coupling 0.5 over eight seeds with this file's ten-word
    vocabulary: live +0.039, one-way +0.008, yoked -0.000, no channel -0.002.
    Stable across window sizes (400 / 800 / 1600 effective samples), so it is
    not the estimator; a twenty-word vocabulary doubles it to +0.078, because a
    channel can only bind what the inputs carried.
    """

    @staticmethod
    def excesses(channel: Channel, *, coupling: float = 0.5, seeds: int = 8):
        a, g = sequence(seed=7), sequence(seed=8)
        return [
            measure_channel(
                a, g, channel=channel, coupling=coupling,
                window=WINDOW_FAST, seed=s,
            ).excess
            for s in range(seeds)
        ]

    def test_a_live_loop_creates_dependence_from_independent_words(self) -> None:
        """The claim. Neither word stream knows anything about the other."""
        values = self.excesses(Channel.LIVE)
        assert all(v > 0.02 for v in values), values
        assert statistics.mean(values) > 0.03

    def test_the_yoked_control_kills_it(self) -> None:
        """The decisive control, and the reason the number above means anything.

        Both engines read recordings: same drive law, same partner-shaped
        statistics, no live channel. If the dependence survived this it would
        have been in the input all along.
        """
        values = self.excesses(Channel.YOKED)
        assert statistics.mean(values) < 0.01, values
        assert not all(v > 0 for v in values), "a dead control must not be one-signed"

    def test_the_yoked_recordings_must_not_share_a_source(self) -> None:
        """A control can be contaminated as easily as a measurement.

        Two recordings cut from one word sequence correlate, and two engines
        fed correlated tapes have a shared cause — which reads as binding. That
        version measured +0.006 on every seed. Independent draws give -0.000.
        """
        assert statistics.mean(self.excesses(Channel.YOKED)) < 0.005

    def test_half_a_loop_creates_less_than_a_whole_one(self) -> None:
        one_way = statistics.mean(self.excesses(Channel.ONE_WAY))
        live = statistics.mean(self.excesses(Channel.LIVE))
        assert one_way > 0.004
        assert live > 3 * one_way

    def test_the_effect_is_not_the_window(self) -> None:
        """An estimator artefact would move with the sample count. This does
        not: +0.039 at 400, 800 and 1600 effective samples alike."""
        a, g = sequence(seed=7), sequence(seed=8)
        readings = [
            statistics.mean(
                measure_channel(
                    a, g, channel=Channel.LIVE, window=HOLD * n, seed=s
                ).excess
                for s in range(4)
            )
            for n in (400, 1600)
        ]
        assert readings[1] == pytest.approx(readings[0], abs=0.015), readings

    def test_the_effect_grows_with_what_the_inputs_carry(self) -> None:
        """A channel can only bind what was there to bind. Doubling the
        vocabulary doubles the created dependence."""
        wide = VOCAB + ["구름", "의자", "강물", "종이", "산", "모래", "노래", "버스", "밥", "달"]
        rng = random.Random(3)
        a = [rng.choice(wide) for _ in range(200)]
        g = [rng.choice(wide) for _ in range(200)]
        rich = statistics.mean(
            measure_channel(
                a, g, channel=Channel.LIVE, window=WINDOW_FAST, seed=s
            ).excess
            for s in range(8)
        )
        assert rich > 1.5 * statistics.mean(self.excesses(Channel.LIVE))

    def test_no_channel_is_no_binding(self) -> None:
        values = self.excesses(Channel.NONE)
        assert statistics.mean(values) < 0.01
        assert not all(v > 0 for v in values)

    def test_coupling_zero_disables_the_channel(self) -> None:
        """Whatever the channel says, nothing is read at coupling zero."""
        values = self.excesses(Channel.LIVE, coupling=0.0)
        assert statistics.mean(values) < 0.01

    def test_the_effect_grows_with_coupling(self) -> None:
        readings = [
            statistics.mean(self.excesses(Channel.LIVE, coupling=c, seeds=4))
            for c in (0.0, 0.25, 0.5)
        ]
        assert readings == sorted(readings), readings

    def test_created_binding_is_below_the_emergence_bar(self) -> None:
        """Stated as a test so the size cannot be quietly overclaimed. This is
        measurable created dependence, not emergence."""
        assert statistics.mean(self.excesses(Channel.LIVE)) < 0.30

    def test_coupling_is_validated(self) -> None:
        with pytest.raises(ValueError, match=r"coupling must be in \[0, 1\]"):
            measure_channel(sequence(seed=1), sequence(seed=2), coupling=1.5)
