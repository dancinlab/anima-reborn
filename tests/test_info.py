"""The entropy estimators — checked against values that can be worked out by
hand, so the tests do not merely agree with the implementation."""

from __future__ import annotations

import math
import random

import pytest

from anima_reborn import Binning, Emergence, entropy, joint_entropy, mutual_information


def test_a_single_bin_carries_no_information() -> None:
    assert entropy([0.0] * 100) == 0.0


def test_empty_stream_is_zero() -> None:
    assert entropy([]) == 0.0
    assert joint_entropy([], []) == 0.0
    assert mutual_information([], []) == 0.0


def test_two_equally_likely_bins_is_one_bit() -> None:
    binning = Binning(bins=2, vrange=1.0)
    assert entropy([-0.5, 0.5] * 50, binning) == pytest.approx(1.0)


def test_uniform_over_n_bins_is_log2_n() -> None:
    binning = Binning(bins=8, vrange=1.0)
    # One sample at the centre of each of the 8 bins.
    samples = [-1.0 + (i + 0.5) * 0.25 for i in range(8)]
    assert entropy(samples, binning) == pytest.approx(math.log2(8))


def test_entropy_is_maximal_for_the_uniform_distribution() -> None:
    """Nothing can beat log2(bins), whatever the stream."""
    binning = Binning(bins=12, vrange=1.5)
    rng = random.Random(11)
    for _ in range(20):
        samples = [rng.uniform(-1.5, 1.5) for _ in range(500)]
        assert entropy(samples, binning) <= math.log2(12) + 1e-12


def test_identical_streams_share_all_their_information() -> None:
    """MI(X, X) = H(X): a stream tells you everything about itself."""
    rng = random.Random(3)
    stream = [rng.uniform(-1.5, 1.5) for _ in range(500)]
    assert mutual_information(stream, stream) == pytest.approx(entropy(stream))


def test_independent_streams_share_almost_nothing() -> None:
    """The plug-in estimator is biased upward on finite samples, so this is
    'small', not 'zero' — 12 bins over 2000 samples leaves a little slack."""
    rng = random.Random(5)
    left = [rng.uniform(-1.5, 1.5) for _ in range(2000)]
    right = [rng.uniform(-1.5, 1.5) for _ in range(2000)]
    assert mutual_information(left, right) < 0.1


def test_mutual_information_is_symmetric() -> None:
    rng = random.Random(17)
    left = [rng.uniform(-1.5, 1.5) for _ in range(300)]
    right = [x + rng.gauss(0, 0.3) for x in left]
    assert mutual_information(left, right) == pytest.approx(
        mutual_information(right, left)
    )


def test_mutual_information_is_never_negative() -> None:
    rng = random.Random(23)
    for _ in range(20):
        left = [rng.uniform(-1.5, 1.5) for _ in range(60)]
        right = [rng.uniform(-1.5, 1.5) for _ in range(60)]
        assert mutual_information(left, right) >= 0.0


def test_joint_entropy_rejects_mismatched_streams() -> None:
    with pytest.raises(ValueError, match="same length"):
        joint_entropy([0.1, 0.2], [0.1])


class TestBinning:
    def test_values_outside_the_range_are_clamped_not_dropped(self) -> None:
        binning = Binning(bins=12, vrange=1.5)
        assert binning.index(-99.0) == 0
        assert binning.index(99.0) == 11

    def test_the_range_is_partitioned_edge_to_edge(self) -> None:
        binning = Binning(bins=4, vrange=1.0)
        assert binning.index(-1.0) == 0
        assert binning.index(-0.5) == 1
        assert binning.index(0.0) == 2
        assert binning.index(0.5) == 3
        assert binning.index(1.0) == 3  # the top edge belongs to the last bin

    def test_rejects_degenerate_configuration(self) -> None:
        with pytest.raises(ValueError, match="bins must be >= 1"):
            Binning(bins=0)
        with pytest.raises(ValueError, match="vrange must be > 0"):
            Binning(vrange=0.0)


class TestEmergenceVerdict:
    def test_thresholds(self) -> None:
        assert Emergence.classify(0.0) is Emergence.INDEPENDENT
        assert Emergence.classify(0.05) is Emergence.INDEPENDENT
        assert Emergence.classify(0.051) is Emergence.PARTIAL
        assert Emergence.classify(0.30) is Emergence.PARTIAL
        assert Emergence.classify(0.301) is Emergence.EMERGENT
