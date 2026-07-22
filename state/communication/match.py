"""Does the engine USE what it holds? Delayed match-to-sample.

Run from the repo root:

    PYTHONPATH=src python state/communication/match.py

`silence.py` established that the ring holds one bit across silence and that the
drive writes it. Both delegated designs then said the same thing: holding is not
using, and the test that earns the stronger word is delayed match-to-sample.
Load the engine with something, make it deaf, then present a probe — and ask
whether the engine's RESPONSE differs according to whether the probe matches
what it is holding.

**Why this can earn "uses" when nothing before it could.** Every previous
measurement is a readout we perform on the engine. Here the quantity is the
engine's own reaction to a new input: how far it has to move. Nothing is
trained, no decoder is fitted, and no threshold is chosen — the two candidates
are compared against each other on the same loaded state and the same walk.

**The response.** Mean squared displacement from the pre-probe state over one
probe cycle. Pre-registered direction: a probe compatible with what is held
should require LESS revision than an incompatible one. That direction is fixed
before the run and is not reversed afterwards.

**The ceiling, derived before measuring.** What is held is ONE BIT — which of
the ring's two consistent sign assignments it settled into. A foil that happens
to load the same basin as the target is therefore indistinguishable in
principle, not merely in practice. With the sixteen corner drives splitting k /
16-k across the two basins, perfect use of the held bit scores
`(0.5*(k-1) + (16-k)) / 15` — 0.767 at an even 8/8 split. So:

    0.500  holds it but does not use it
    0.767  uses the held bit perfectly (at an 8/8 split)
    1.000  impossible — would mean more than one bit is held

Reporting anything near 1.0 as success would mean the measurement is reading
something other than the held state, and the script prints the split so the
ceiling is recomputed from what actually happened rather than assumed.

**Controls, and why they read exactly 0.500.** `SELF` and `FEEDFORWARD` hold
nothing across silence (measured: they fall to their fixed points by 20 and 120
ticks), and a never-loaded arm holds nothing by definition. For any such arm the
held state is the SAME whatever the target was, so the comparison of target `t`
against foil `f` and the mirrored comparison of `f` against `t` use one identical
held state and disagree — exactly one of the two is a hit. The score is therefore
pinned at 0.500 by construction, not by luck. That is what makes these controls
airtight rather than merely reassuring: an arm holding nothing CANNOT score above
chance here, so the ring's margin cannot be a property of the scoring.

The probe phase restores listening, since a deaf engine cannot receive a probe at
all, and every probe starts at the same rhythm phase because the fork restarts
the tick count — phase cannot be the thing that differs.
"""

from __future__ import annotations

import collections
import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

DRIVES = [
    tuple((((i >> k) & 1) * 2 - 1) * 0.8 for k in range(4)) for i in range(16)
]

TELL = 400
"""Ticks of drive before the silence."""

SILENCE = 240
"""Ticks of deaf silence. Past 60 the ring is fully settled into one basin and
every acyclic control has decayed to zero, so this is where holding is real and
the controls are honestly empty."""

PROBE = 20
"""Ticks of probe — one full listen/integrate cycle."""

SEEDS = 8


def hold(drive: tuple[float, ...], *, wiring: Wiring, seed: int) -> tuple[float, ...]:
    """Tell the engine something, then make it deaf and let it keep whatever it
    keeps."""
    engine = CoupledEngine(
        wiring=wiring, rhythm=ALTERNATING, drive=drive, seed=seed, initial=(0.0,) * 4
    )
    engine.run(TELL)
    engine.rhythm = FIXED  # deaf — nothing can be heard during the silence
    engine.drive = 0.0
    engine.run(SILENCE)
    return engine.state.values


def revision(
    held: tuple[float, ...], probe: tuple[float, ...], *, wiring: Wiring, seed: int
) -> float:
    """How far the engine has to move to accommodate a probe.

    Listening is restored for the probe, because a deaf engine cannot receive
    one. The fork restarts the tick count, so every probe arrives at the same
    rhythm phase and phase cannot be the thing that differs.
    """
    engine = CoupledEngine(
        wiring=wiring, rhythm=ALTERNATING, drive=probe, seed=seed, initial=held
    )
    moved = []
    for _ in range(PROBE):
        values = engine.step().values
        moved.append(sum((values[i] - held[i]) ** 2 for i in range(4)))
    return statistics.mean(moved)


def basin(point: tuple[float, ...]) -> tuple[bool, ...]:
    return tuple(v > 0 for v in point)


def two_alternative(wiring: Wiring, *, loaded: bool = True) -> list[float]:
    """For each target, is the match revised less than each foil?

    Every one of the other fifteen drives is used as a foil, so no easy negative
    is chosen. Ties score half, which is what a state carrying nothing produces.
    """
    per_seed = []
    for seed in range(SEEDS):
        hits = total = 0.0
        for target in DRIVES:
            held = (
                hold(target, wiring=wiring, seed=seed)
                if loaded
                else hold(tuple([0.0] * 4), wiring=wiring, seed=seed)
            )
            match = revision(held, target, wiring=wiring, seed=seed)
            for foil in DRIVES:
                if foil == target:
                    continue
                against = revision(held, foil, wiring=wiring, seed=seed)
                hits += 1.0 if match < against else 0.5 if match == against else 0.0
                total += 1
        per_seed.append(hits / total)
    return per_seed


def ceiling() -> tuple[float, str]:
    """What perfect use of ONE bit would score, from the split that occurred."""
    counts = collections.Counter(
        basin(hold(d, wiring=Wiring.RING, seed=s))
        for d in DRIVES
        for s in range(SEEDS)
    )
    shares = sorted((c / SEEDS for c in counts.values()), reverse=True)
    k = shares[0] if shares else 0.0
    other = len(DRIVES) - k
    return (0.5 * (k - 1) + other) / (len(DRIVES) - 1), " / ".join(
        f"{s:.1f}" for s in shares
    )


def main() -> None:
    bar, split = ceiling()
    print(f"delayed match-to-sample — {len(DRIVES)} drives, {SEEDS} seeds")
    print(f"tell {TELL}, deaf silence {SILENCE}, probe {PROBE}\n")
    print(f"basin split across drives : {split}")
    print(f"holds but does not use    : 0.500")
    print(f"uses the held bit fully   : {bar:.3f}   <- derived, not chosen")
    print(f"impossible                : 1.000   (would need more than one bit)\n")

    print(f"{'arm':<26}{'2AFC':>8}{'worst seed':>12}   reading")
    print("-" * 72)
    for label, wiring, loaded in (
        ("ring", Wiring.RING, True),
        ("ring, never loaded", Wiring.RING, False),
        ("feedforward", Wiring.FEEDFORWARD, True),
        ("self", Wiring.SELF, True),
    ):
        per_seed = two_alternative(wiring, loaded=loaded)
        score = statistics.mean(per_seed)
        if score <= 0.55:
            reading = "at chance — the state is not used"
        elif score > bar + 0.02:
            reading = "ABOVE the one-bit ceiling — something else is being read"
        else:
            reading = f"{(score - 0.5) / max(bar - 0.5, 1e-9):.0%} of the held bit used"
        print(
            f"{label:<26}{score:>8.3f}{min(per_seed):>12.3f}   {reading}",
            flush=True,
        )
        if loaded and wiring is Wiring.RING:
            above = sum(v > 0.5 for v in per_seed)
            print(f"{'':<26}{'':>8}{'':>12}   above chance on {above}/{SEEDS} seeds")

    print(
        "\nThe ceiling is what makes this readable. A score near 1.0 would not be"
        "\na better result — it would mean the probe is being compared against"
        "\nsomething other than the one bit the silence leaves behind. And the"
        "\ncontrols are at 0.500 by construction, not by luck: an arm whose held"
        "\nstate does not depend on what it was told scores each comparison and"
        "\nits mirror oppositely, so it cannot beat chance here at all."
    )


if __name__ == "__main__":
    main()
