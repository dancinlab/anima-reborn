"""Words as a drive — and why the obvious version of that experiment lies.

The question this module exists for: put words into engine A and engine G, and
see whether emergence happens. It can be asked honestly, but only after two
things that the naive version gets wrong are dealt with. Both were measured
before this file was written.

**1. Words cannot be an initial condition — the substrate erases them.**
`repulsion`'s drift pulls the driven dimensions toward their target at `PULL`
and decays the rest by `DAMPING` every tick, so any starting vector is gone in a
few hundred ticks. Measured: two fields started from different words, under the
same noise, drift apart by 1.31 at the first tick and 0.0001 by tick 600 — and
the decay curve is identical for three unrelated encodings, so it is the
substrate's constants doing it, not the encoding. An emergence verdict needs
~800 ticks. The word is long gone before the verdict exists. So words here are a
*continuing* drive: each one is the target A or G chases while it is current.

**2. The plug-in estimator reports emergence for words that have nothing to do
with each other.** Holding a word for `hold` ticks means a window of `window`
samples contains only `window / hold` independent draws, and the estimator's
bias explodes as that number falls. Measured on two *completely independent*
word sequences, where the true mutual information is exactly zero:

    effective samples     8      80     800    4000   20000
    reported MI       0.835   0.152   0.014   0.003   0.001

At eight effective samples the estimator reports 0.835 bits — nearly three times
the 0.30-bit emergence bar — for words with no relation whatsoever.

So this module refuses to hand out a bare number. Every measurement carries its
own null: the same words, paired at random, measured the same way. What can be
read is the **excess** over that null, and the verdict is classified on the
excess rather than on the raw value. An absolute mutual information from word
data is not evidence of anything, and here it is not available on its own.

The encoding is deliberately the caller's: a word becomes a number by whatever
rule is passed in, because that rule — not the words — decides what any absolute
value would be. What it cannot decide is the excess over a null measured through
the same rule, which is the whole reason the null is mandatory.
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .info import Binning, Emergence, entropy, joint_entropy
from .pipeline import OBSERVATION_NOISE, PULL, WALK

__all__ = [
    "WordReading",
    "blake_scalar",
    "drive",
    "measure",
    "MIN_EFFECTIVE_SAMPLES",
]

HOLD = 17
"""Ticks a word stays current — the substrate's own time constant, `1 / PULL`.

Not a fitted number: it is how long the engine takes to travel most of the way
to a target, and a word the engine cannot reach is a word it cannot carry.
Measured, driving both engines from the SAME word sequence and holding the
effective sample count fixed, the excess over the null tracks reach exactly:

    hold           2      5     10     17     34     68
    reach        12%    27%    46%    65%    88%    99%
    excess     0.060  0.138  0.281  0.418  0.616  0.793

Below the time constant the words change faster than the engine can follow and
the signal is filtered away; at it, the excess clears the 0.30 bar."""

WINDOW = HOLD * 800
"""Observations behind each entropy — sized to keep 800 effective samples.

Far longer than the pipeline's 200, and necessarily so: `window / hold` is what
governs the estimator's bias, and 800 is where truly independent word streams
measure 0.014 bits instead of 0.835."""

MIN_EFFECTIVE_SAMPLES = 400
"""Below this the null is worth more than the signal and `measure` says so.
Chosen from the measurement above: 400 effective samples sits between the 0.036
and 0.014 bias readings, an order of magnitude under the 0.30 bar."""

CONTROL_ROUNDS = 8
"""Null measurements averaged per reading. One shuffle is itself a sample."""


def blake_scalar(word: str) -> float:
    """A word to a number in [-1, 1], by hash.

    Offered as a default, not as a truth. Any encoding produces some absolute
    mutual information; that is precisely why `measure` reports the excess over
    a null computed through the *same* encoding rather than the raw value.
    """
    digest = hashlib.blake2b(word.encode("utf-8"), digest_size=2).digest()
    return int.from_bytes(digest, "big") / 65535.0 * 2.0 - 1.0


def drive(
    words: Sequence[str],
    *,
    hold: int = HOLD,
    ticks: int = WINDOW,
    encode: Callable[[str], float] = blake_scalar,
    rng: random.Random | None = None,
) -> list[float]:
    """Run one engine driven by a word sequence, and return what was observed.

    The engine chases whichever word is current, exactly as the pipeline chases
    its rotating target: a random step of width `WALK`, then a pull of `PULL`
    toward the encoded word. Each observation adds the pipeline's own noise.
    The sequence repeats if it is shorter than `ticks`.
    """
    if not words:
        raise ValueError("need at least one word")
    if hold < 1:
        raise ValueError(f"hold must be >= 1, got {hold}")
    if ticks < 1:
        raise ValueError(f"ticks must be >= 1, got {ticks}")

    rng = rng or random.Random(0)
    position = 0.0
    observations = []
    for tick in range(ticks):
        target = encode(words[(tick // hold) % len(words)])
        position += (rng.random() - 0.5) * WALK
        position += (target - position) * PULL
        observations.append(position + (rng.random() - 0.5) * OBSERVATION_NOISE)
    return observations


@dataclass(frozen=True, slots=True)
class WordReading:
    """One word-pair measurement, and the null it has to beat.

    `mutual_information` is deliberately not the headline. On word data it is
    dominated by how many independent draws the window held, so it means
    nothing without `control` beside it.
    """

    mutual_information: float
    """Bits between the two driven streams."""
    control: float
    """The same words with the pairing destroyed, measured identically. This is
    what the estimator reports for no relationship at all, at this exact
    effective sample size."""
    effective_samples: int
    """`window / hold` — independent draws behind the estimate. The bias that
    fakes emergence is governed by this and nothing else."""
    trustworthy: bool
    """False when `effective_samples` is under `MIN_EFFECTIVE_SAMPLES`, i.e. the
    null is large enough that no excess can be believed."""

    @property
    def excess(self) -> float:
        """Bits beyond what unrelated words score. The only readable number."""
        return self.mutual_information - self.control

    @property
    def verdict(self) -> Emergence:
        """Classified on the excess, never on the raw value — which is what
        stops an estimator artefact from being read as emergence."""
        if not self.trustworthy:
            return Emergence.INDEPENDENT
        return Emergence.classify(self.excess)

    def __str__(self) -> str:
        warning = "" if self.trustworthy else "  ⚠ too few effective samples"
        return (
            f"MI={self.mutual_information:.3f} null={self.control:.3f} "
            f"excess={self.excess:+.3f} [{self.verdict.value}] "
            f"n_eff={self.effective_samples}{warning}"
        )


def measure(
    words_a: Sequence[str],
    words_g: Sequence[str],
    *,
    hold: int = HOLD,
    window: int = WINDOW,
    seed: int | None = None,
    encode: Callable[[str], float] = blake_scalar,
    binning: Binning | None = None,
) -> WordReading:
    """Drive A from one word sequence, G from another, and measure the pair.

    The null is built by permuting G's words: same multiset, same marginal
    distribution, same encoding, same window — only the pairing destroyed. Any
    excess over it is the part that the relationship between the sequences
    accounts for.
    """
    binning = binning or Binning(bins=12, vrange=1.6)
    rng = random.Random(seed)

    def paired(sequence_g: Sequence[str], stream_seed: int) -> float:
        left = drive(
            words_a,
            hold=hold,
            ticks=window,
            encode=encode,
            rng=random.Random(stream_seed),
        )
        right = drive(
            sequence_g,
            hold=hold,
            ticks=window,
            encode=encode,
            rng=random.Random(stream_seed + 1),
        )
        return max(
            0.0,
            entropy(left, binning)
            + entropy(right, binning)
            - joint_entropy(left, right, binning),
        )

    observed = paired(words_g, rng.getrandbits(32))

    shuffled = list(words_g)
    nulls = []
    for _ in range(CONTROL_ROUNDS):
        rng.shuffle(shuffled)
        nulls.append(paired(shuffled, rng.getrandbits(32)))

    effective = window // hold
    return WordReading(
        mutual_information=observed,
        control=sum(nulls) / len(nulls),
        effective_samples=effective,
        trustworthy=effective >= MIN_EFFECTIVE_SAMPLES,
    )
