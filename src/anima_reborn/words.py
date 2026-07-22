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

**And the answer, stated so it cannot be over-read: binding is transmitted, not
created.** A and G never read each other — no engine in this package couples
them, the gap is a readout rather than a channel — so two independent word
streams produce two independent observation streams *by construction*, and no
measurement could show otherwise. Measured, on eight seeds: -0.002 to +0.004
bits, flat at zero. What the substrate does is *carry* whatever relationship its
inputs already had, through a filter with a measurable passband, losing some of
it on the way. It never invents one. So "emergence happens when words go into A
and G" is true only in the sense that a wire carries a signal.

The same architecture puts Phi at zero. Every dimension updates from itself and
its own exogenous target, so the transition matrix factorizes and there is
nothing for a partition to destroy. Measured through `substrate`/`iit4` on the
four driven units at three binarization thresholds: **Phi = 0.0000 exactly**, at
four distinctions and a structure total of 4.0 — plenty specified, nothing
integrated. Words do not change this and were never going to.

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
from enum import Enum

from .info import Binning, Emergence, entropy, joint_entropy
from .pipeline import OBSERVATION_NOISE, PULL, WALK

__all__ = [
    "Channel",
    "WordReading",
    "measure_channel",
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

SHIFTS = (37, 83, 127)
"""Circular offsets the null is measured at, and their median is taken.

A shift is a stricter null than a shuffle, which is why it replaced one here.
Rotating the second stream keeps everything the encoding produced — marginals,
block structure, autocorrelation, the estimator's whole contribution — and
removes only the alignment. A shuffle rebuilds the stream and loses some of that
autocorrelation with it, so it reads LOW and flatters the result: measured
0.0120 against the shift's 0.0182 on the same unrelated pair.

All three are coprime to `HOLD` and past the substrate's 17-tick memory, so no
offset can accidentally re-align the blocks."""


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
    """The same streams with the second rotated in time — everything the
    encoding produced kept, only the alignment removed. This is what the
    estimator reports for no relationship at all, at this exact window."""
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

    The null is the same pair of streams with the second one rotated in time:
    same encoding, same cadence, same substrate, same estimator bias — only the
    alignment gone. Any excess over it is what the relationship between the
    sequences accounts for, and nothing the encoding can manufacture survives
    a time shift.
    """
    binning = binning or Binning(bins=12, vrange=1.6)
    rng = random.Random(seed)

    stream_seed = rng.getrandbits(32)
    left = drive(
        words_a, hold=hold, ticks=window, encode=encode,
        rng=random.Random(stream_seed),
    )
    right = drive(
        words_g, hold=hold, ticks=window, encode=encode,
        rng=random.Random(stream_seed + 1),
    )

    def against(other: Sequence[float]) -> float:
        return max(
            0.0,
            entropy(left, binning)
            + entropy(other, binning)
            - joint_entropy(left, other, binning),
        )

    observed = against(right)
    nulls = sorted(against(right[shift:] + right[:shift]) for shift in SHIFTS)
    effective = window // hold
    return WordReading(
        mutual_information=observed,
        control=nulls[len(nulls) // 2],
        effective_samples=effective,
        trustworthy=effective >= MIN_EFFECTIVE_SAMPLES,
    )


class Channel(Enum):
    """How the two driven engines are connected, if at all.

    The conditions exist together because the claim needs all of them: a number
    from `LIVE` means nothing without `YOKED` beside it, since partner-shaped
    input could carry the dependence on its own.
    """

    NONE = "none"
    """No connection. Each engine chases only its own words — what `measure`
    does, and where binding is transmitted rather than created."""
    LIVE = "live"
    """Each engine reads the other's live position. A closed loop."""
    ONE_WAY = "one_way"
    """Only A reaches G; A reads a recording instead of the live partner. Half
    the loop, and it produces a fraction of the effect."""
    YOKED = "yoked"
    """**The control.** Both engines read recordings taken from independent
    runs: partner-shaped statistics, identical drive law, no live channel
    anywhere. Whatever survives this was not created by the coupling."""


def _record(
    words: Sequence[str],
    *,
    coupling: float,
    hold: int,
    window: int,
    encode: Callable[[str], float],
    rng: random.Random,
) -> list[float]:
    """A partner trajectory from a run that never touched the other engine."""
    position = 0.0
    out = []
    for tick in range(window):
        target = (1.0 - coupling) * encode(words[(tick // hold) % len(words)])
        position += (target - position) * PULL + (rng.random() - 0.5) * WALK
        out.append(position)
    return out


def _drive_pair(
    words_a: Sequence[str],
    words_g: Sequence[str],
    *,
    coupling: float,
    channel: Channel,
    hold: int,
    window: int,
    encode: Callable[[str], float],
    rng: random.Random,
    replays: tuple[list[float] | None, list[float] | None],
) -> tuple[list[float], list[float]]:
    """Run both engines together and return what each was observed doing.

    A unit's target mixes its own word with the negated partner — the same
    repulsion sign the rest of the package uses — weighted by `coupling`. The
    two are updated from the previous positions, so neither leads.
    """
    replay_a, replay_g = replays
    a = g = 0.0
    left, right = [], []
    for tick in range(window):
        word_a = encode(words_a[(tick // hold) % len(words_a)])
        word_g = encode(words_g[(tick // hold) % len(words_g)])
        partner_of_a = replay_a[tick] if replay_a is not None else g
        partner_of_g = replay_g[tick] if replay_g is not None else a

        next_a = a + (
            ((1.0 - coupling) * word_a + coupling * -partner_of_a) - a
        ) * PULL + (rng.random() - 0.5) * WALK
        next_g = g + (
            ((1.0 - coupling) * word_g + coupling * -partner_of_g) - g
        ) * PULL + (rng.random() - 0.5) * WALK
        a, g = next_a, next_g

        left.append(a + (rng.random() - 0.5) * OBSERVATION_NOISE)
        right.append(g + (rng.random() - 0.5) * OBSERVATION_NOISE)
    return left, right


def measure_channel(
    words_a: Sequence[str],
    words_g: Sequence[str],
    *,
    coupling: float = 0.5,
    channel: Channel = Channel.LIVE,
    hold: int = HOLD,
    window: int = WINDOW,
    seed: int | None = None,
    encode: Callable[[str], float] = blake_scalar,
    binning: Binning | None = None,
) -> WordReading:
    """Drive two engines from independent words and let them read each other.

    `measure` proves that an uncoupled substrate only ever *transmits* what its
    inputs already shared. This asks the opposite question: given inputs that
    share nothing, does a live channel *create* dependence between them?

    Measured at `coupling = 0.5` over eight seeds, excess over the time-shift
    null, on a twenty-word vocabulary:

        live +0.078   one-way +0.008   yoked -0.000   no channel -0.002

    The yoked control dying is what makes the first number mean anything, and
    half a loop producing a tenth of a whole one is the dose-response.

    Two conditions belong with the number. It does **not** depend on the window
    — +0.039 at 400, 800 and 1600 effective samples alike, so it is not the
    estimator — but it **does** depend on how much the inputs carry: a ten-word
    vocabulary gives +0.039 where twenty gives +0.078, at any sequence length.
    A channel can only bind what was there to bind.

    Note the size either way. It is real and consistent — eight seeds out of
    eight — and still well under the 0.30 emergence bar. The honest reading is
    *measurable created dependence*, not emergence.

    Args:
        coupling: How much of each target is the negated partner, in [0, 1]. At
            0 there is no channel whatever `channel` says.
        channel: Which connection to run, including the controls.
    """
    if not 0.0 <= coupling <= 1.0:
        raise ValueError(f"coupling must be in [0, 1], got {coupling}")
    binning = binning or Binning(bins=12, vrange=1.6)
    rng = random.Random(seed)

    def recording() -> list[float]:
        """A partner-shaped trajectory that shares nothing with anything.

        The word order is drawn independently per recording. Deriving both
        recordings from one source — an offset of the same sequence, say —
        correlates them, and two engines fed correlated tapes have a shared
        cause: measured, that alone lifts the yoked control from -0.001 to
        +0.006 on every seed, which would eat a fourteenth of the effect the
        control exists to rule out.
        """
        source = list(words_a) + list(words_g)
        rng.shuffle(source)
        return _record(
            source,
            coupling=coupling,
            hold=hold,
            window=window,
            encode=encode,
            rng=random.Random(rng.getrandbits(32)),
        )

    replays: tuple[list[float] | None, list[float] | None]
    if channel is Channel.LIVE:
        replays = (None, None)
    elif channel is Channel.ONE_WAY:
        replays = (recording(), None)  # A hears a tape; G still hears A
    elif channel is Channel.YOKED:
        replays = (recording(), recording())
    else:  # Channel.NONE
        coupling, replays = 0.0, (None, None)

    left, right = _drive_pair(
        words_a,
        words_g,
        coupling=coupling,
        channel=channel,
        hold=hold,
        window=window,
        encode=encode,
        rng=random.Random(rng.getrandbits(32)),
        replays=replays,
    )

    def against(other: Sequence[float]) -> float:
        return max(
            0.0,
            entropy(left, binning)
            + entropy(other, binning)
            - joint_entropy(left, other, binning),
        )

    observed = against(right)
    nulls = sorted(against(right[shift:] + right[:shift]) for shift in SHIFTS)
    effective = window // hold
    return WordReading(
        mutual_information=observed,
        control=nulls[len(nulls) // 2],
        effective_samples=effective,
        trustworthy=effective >= MIN_EFFECTIVE_SAMPLES,
    )
