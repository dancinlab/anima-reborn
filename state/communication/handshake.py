"""Where communication actually begins — and why the shipped pieces stop short.

Run from the repo root:

    PYTHONPATH=src python state/communication/handshake.py

`concepts.py` carried a referent through two engines. The seed question the whole
`state/communication/` line was named for is harder: did they COMMUNICATE, or did
we wire a channel and call it that? Both delegated designs converged on the same
falsifiable definition (a Lewis-Skyrms signaling game) and the same verdict:
communication is reachable in this substrate but NOT by composing what exists —
it needs one mechanism the repo does not have, reward-gated plasticity, so that
the code is established BETWEEN two agents rather than installed by us.

This script does not fake that mechanism. It measures the wall directly, by
running the communication controls against exactly the transmission the shipped
pieces DO support, and showing which controls it passes and which it cannot —
the profile of a wired channel, so the gap to real communication is a measured
thing rather than an assertion.

**The channel (declared infrastructure, not cheating).** A sender engine is told
a referent, holds it deaf, and its held latch signs are tapped as the drive of a
receiver engine, which holds in turn. The pipe is fine — air is a pipe for
speech. What is NOT established between them is the CODE: the referent->signal and
signal->act mapping is fixed by us (identity), never negotiated.

**The measurement is I(referent; B-word) in bits, under three conditions.**

- Intact — referent -> A emits -> B holds. Nonzero mutual information means the
  referent is recoverable from B's held word: transmission works.
- Signal scrambled — give B a signal drawn from a RANDOM referent, independent
  of the true one (destroy the code, not relabel it: a deterministic permutation
  is injective and leaves the information untouched, which is a trap this script
  was rewritten to avoid). If information dies, the signal really carried the
  referent. A genuine channel passes this.
- Partner swapped — read A's emission with a receiver from a different seed, one
  that shares no history with A. If information SURVIVES, the code was installed
  by us, not established between this pair — a real convention would collapse
  when a stranger replaces the partner. A wired channel survives it, because the
  referent->signal->act map lives in our wiring.

Feedback dependence is the fourth control every communication test needs, and it
is not run here because there is nothing to destroy: nothing in the shipped repo
updates on success. That absence IS the wall.
"""

from __future__ import annotations

import collections
import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

REFERENTS = [
    tuple((((i >> k) & 1) * 2 - 1) * 0.8 for k in range(6)) for i in range(8)
]
"""Eight referents on the three-latch engine — three bits of channel."""

TELL = 400
SILENCE = 240
WALKS = 8


def hold(drive: tuple[float, ...], *, seed: int, chain: float = 0.2) -> tuple[float, ...]:
    engine = CoupledEngine(
        wiring=Wiring.PAIRS, units=6, chain=chain, rhythm=ALTERNATING,
        drive=drive, seed=seed, initial=(0.0,) * 6,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    return engine.run(SILENCE).values


def emit(referent: tuple[float, ...], *, seed: int) -> tuple[float, ...]:
    """A's signal: the latch signs it settled into, as a drive for B."""
    held = hold(referent, seed=seed)
    return tuple(0.8 if held[i] > 0 else -0.8 for i in range(6))


def receive(signal: tuple[float, ...], *, seed: int) -> tuple[bool, ...]:
    """B's held word after listening to A's signal."""
    held = hold(signal, seed=seed)
    return tuple((held[2 * j] - held[2 * j + 1]) > 0 for j in range(3))


def _mutual_information(pairs: list[tuple[tuple, tuple]]) -> float:
    """I(referent; B-word) in bits, plug-in estimate. H(R) is 3 for eight equal
    referents, so this is bounded by 3 and by the code's own word count."""
    import math
    n = len(pairs)
    joint = collections.Counter(pairs)
    left = collections.Counter(r for r, _ in pairs)
    right = collections.Counter(w for _, w in pairs)
    total = 0.0
    for (r, w), c in joint.items():
        pj = c / n
        total += pj * math.log2(pj / ((left[r] / n) * (right[w] / n)))
    return max(0.0, total)


def transmit(
    *, emit_seed_shift: int = 0, scramble: bool = False, seed_walks: int = WALKS
) -> tuple[float, int]:
    """Referent -> A emits -> B holds, scored as I(referent; B-word) in bits.

    `emit_seed_shift` reads B on emissions from a DIFFERENT sender seed — a
    partner with no shared history. `scramble` gives B a signal drawn from a
    RANDOM referent independent of the true one (the signal-necessity null:
    destroy the code, not relabel it).
    """
    emissions = {
        r: [emit(r, seed=w + emit_seed_shift) for w in range(seed_walks)]
        for r in REFERENTS
    }
    pairs: list[tuple[tuple, tuple]] = []
    words: set[tuple[bool, ...]] = set()
    # a fixed independent referent per (referent, walk) for the scramble null —
    # no Random(): index arithmetic keeps it deterministic and seed-free.
    for ri, referent in enumerate(REFERENTS):
        for w in range(seed_walks):
            source = REFERENTS[(ri + w + 1) % len(REFERENTS)] if scramble else referent
            signal = emissions[source][w]
            word = receive(signal, seed=w + 100)
            pairs.append((referent, word))
            words.add(word)
    return _mutual_information(pairs), len(words)


def main() -> None:
    print("the shipped substrate as a signaling channel — what it passes, what it cannot")
    print(f"{len(REFERENTS)} referents (H = 3 bits), {WALKS} walks, PAIRS+chain\n")

    intact, words = transmit()
    scrambled, _ = transmit(scramble=True)
    swapped, _ = transmit(emit_seed_shift=1)

    print(f"{'control':<36}{'I(referent; B-word)':>20}   verdict")
    print("-" * 76)
    print(f"{'intact channel':<36}{intact:>18.2f} b   transmits ({words}/8 words)")
    print(
        f"{'signal scrambled (destroy the code)':<36}{scrambled:>18.2f} b   "
        f"{'signal necessary — passes' if scrambled < intact * 0.4 else 'signal not needed'}"
    )
    print(
        f"{'partner swapped (no shared history)':<36}{swapped:>18.2f} b   "
        f"{'SURVIVES — code installed, not established' if swapped > intact * 0.6 else 'collapses — a real convention'}"
    )

    print(
        "\nThe two rows below intact are the whole point. Scrambling the signal"
        "\nkills recovery, so the signal really does carry the referent — the"
        "\nchannel is genuine. But swapping in a partner with no shared history"
        "\ndoes NOT kill it: the referent->signal->act map is fixed by us, so any"
        "\nreceiver reads it. That is the signature of a wired channel — production"
        "\nand reception without an established convention."
        "\n\nClosing the gap needs reward-gated plasticity: each endpoint's map"
        "\nupdated from the dyad's own success bit and nothing else — a new causal"
        "\nmechanism, not a composition. Its one non-negotiable rule: no update may"
        "\nread the other agent's private state. The midpoint rule in align.py"
        "\ndoes exactly that, which is why it cannot be the two-agent learner —"
        "\nsplit across the gap it is a telepathic wire, and every runtime control"
        "\nwould pass while the code was installed at training time."
    )


if __name__ == "__main__":
    main()
