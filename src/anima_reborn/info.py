"""Information theory shared by the emergence and pipeline engines.

Two streams are each histogrammed into a fixed number of bins over a fixed
range, and their mutual information falls out of the entropies:

    MI = H(L) + H(R) - H(L, R)   [bits]

Independent streams share nothing, so MI sits at zero. Bind them to a common
source and MI climbs: the pair now carries information neither stream holds
alone. That number is the whole claim the visualizer makes.

Ported from the `bin` / `entropy` / `jointEntropy` functions in
`dancinlab/anima-experience` `index.html`.

A caveat worth stating plainly, because it changes how the numbers read: this
is the plain plug-in estimator with no bias correction, and on short windows it
overstates MI badly. Filling 144 joint bins from 250 samples leaves most of them
holding 0, 1 or 2 counts, and that sparsity alone looks like structure. Two
genuinely independent streams measure about 0.155 bits over the default window,
not zero. The floor falls off as 1/N — roughly 0.03 bits at 1000 samples and
0.007 at 5000 — so it is a small-sample artefact, not a property of the streams.
The `Emergence` thresholds below are the original's and were chosen against that
floor: `PARTIAL` at the default window means "indistinguishable from
independent", and only `EMERGENT` is a claim about the streams.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from enum import Enum

__all__ = [
    "Binning",
    "Emergence",
    "entropy",
    "joint_entropy",
    "mutual_information",
]


class Binning:
    """Maps a value range onto a fixed number of histogram bins.

    Values outside [-vrange, +vrange] are clamped into the edge bins rather
    than dropped, so a stream that overshoots still contributes.
    """

    __slots__ = ("bins", "vrange", "_scale")

    def __init__(self, bins: int = 12, vrange: float = 1.5) -> None:
        if bins < 1:
            raise ValueError(f"bins must be >= 1, got {bins}")
        if vrange <= 0:
            raise ValueError(f"vrange must be > 0, got {vrange}")
        self.bins = bins
        self.vrange = vrange
        self._scale = bins / (2.0 * vrange)

    def index(self, value: float) -> int:
        """The bin a value falls in, clamped to [0, bins - 1]."""
        i = int((value + self.vrange) * self._scale)
        return max(0, min(self.bins - 1, i))

    def __repr__(self) -> str:
        return f"Binning(bins={self.bins}, vrange={self.vrange})"


DEFAULT_BINNING = Binning()


def entropy(samples: Sequence[float], binning: Binning = DEFAULT_BINNING) -> float:
    """Shannon entropy of one stream, in bits. Empty stream -> 0.0."""
    n = len(samples)
    if n == 0:
        return 0.0
    counts = Counter(binning.index(v) for v in samples)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def joint_entropy(
    left: Sequence[float],
    right: Sequence[float],
    binning: Binning = DEFAULT_BINNING,
) -> float:
    """Shannon entropy of the pair, in bits. The streams are read in lockstep,
    so sample i of one belongs with sample i of the other."""
    if len(left) != len(right):
        raise ValueError(
            f"streams must be the same length, got {len(left)} and {len(right)}"
        )
    n = len(left)
    if n == 0:
        return 0.0
    counts = Counter(
        (binning.index(a), binning.index(b)) for a, b in zip(left, right)
    )
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def mutual_information(
    left: Sequence[float],
    right: Sequence[float],
    binning: Binning = DEFAULT_BINNING,
) -> float:
    """Bits the two streams share. Floored at zero — the plug-in estimator can
    go slightly negative on small samples, which is estimator noise rather than
    negative information."""
    h_left = entropy(left, binning)
    h_right = entropy(right, binning)
    h_joint = joint_entropy(left, right, binning)
    return max(0.0, h_left + h_right - h_joint)


class Emergence(Enum):
    """How much the two streams have bound together.

    Thresholds are the original's: 0.30 bits and 0.05 bits.
    """

    INDEPENDENT = "independent"
    """MI at or below 0.05 bits — the streams carry nothing in common."""
    PARTIAL = "partial"
    """Measurable shared information, but under the emergence bar."""
    EMERGENT = "emergent"
    """Above 0.30 bits — bound tightly enough to call it emergence."""

    @classmethod
    def classify(cls, mi: float) -> Emergence:
        if mi > 0.30:
            return cls.EMERGENT
        if mi > 0.05:
            return cls.PARTIAL
        return cls.INDEPENDENT
