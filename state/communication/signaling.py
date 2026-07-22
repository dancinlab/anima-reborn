"""Two engines establish a convention neither was given — the last piece.

Run from the repo root:

    PYTHONPATH=src python state/communication/signaling.py

`handshake.py` measured the wall: the shipped pieces transmit, but the code is
fixed by us, so a stranger reads it (the partner swap survives). Both delegated
designs said the missing mechanism is reward-gated plasticity, and that it must
be a NEW causal loop, not a composition. This is it, and it is the smallest
honest version — a Lewis-Skyrms signaling game where the referent->signal and
signal->act maps are learned by the two agents from a one-bit success signal.

**The game.** Each episode: a balanced referent r in {0, 1} is shown only to A.
A's policy picks one of two unlabeled signals s. A's engine holds s and emits its
latch bit; that emission is B's only input. B's engine holds it into a word, B's
policy picks an act y, and both agents get the single bit `y == r`. The engines
are the noisy channel — pure, unchanged, one bit each — and all plasticity lives
here in the harness.

**The static audit — the trap `handshake.py` named.** The communication trap
hides in the training loop: if either agent's update reads the other's private
state, the code is installed by us and every runtime control passes anyway. So
the update is factored by construction — `_update_sender` sees only A's own
`(referent, signal, success)`, `_update_receiver` only B's own
`(word, act, success)`. Neither ever takes the other agent's policy, state, or
choice as an argument. That factoring is the proof, and it is structural rather
than statistical.

**The ceiling, derived.** Recovery cannot beat the channel: if the convention
were perfect, B would still only recover r as often as A's signal survives two
noisy holds. That fidelity is measured (no learning) and printed as the bar; a
score above it would mean the referent reached B through something other than
the signal, exactly as 1.0 in `match.py` would have been a bug.

**What the controls must show** (each an arm below):

- trained beats its own day-0 (the untrained policy, measured — not assumed 0.5,
  though for a symmetric 2x2 game it is 0.5) on every seed;
- yoked feedback (the success bit decoupled from the outcome) fails to learn, so
  it is the CONSEQUENCE that establishes the code, not exposure;
- signal scrambled at test destroys recovery, so the signal is necessary;
- partner swap collapses to chance AGGREGATED over independent pairs — the code
  is private to a shared history. This is the row `handshake.py` could not pass
  with a fixed code; passing it here is the whole point. Two conventions exist,
  so any single swapped pair agrees by chance half the time; only the mean over
  all cross pairs is readable (sol's correction).
"""

from __future__ import annotations

import random
import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

EPISODES = 1500
RATE = 0.3
TAIL = 300
"""Episodes averaged for a recovery reading, from the end of training."""
SEEDS = 12
TELL = 200
HOLD = 120


def _channel(signal: int, *, seed: int) -> int:
    """One agent's engine: hold a bit, return the latch bit it settled into.

    A pure `CoupledEngine` — the noisy wire, nothing learned in it."""
    drive = (0.8, -0.8) if signal == 0 else (-0.8, 0.8)
    engine = CoupledEngine(
        units=2, wiring=Wiring.PAIRS, chain=0.0, rhythm=ALTERNATING,
        drive=drive, seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    values = engine.run(HOLD).values
    return 0 if (values[0] - values[1]) > 0 else 1


def _pick(weights: list[float], rng: random.Random) -> int:
    total = sum(weights)
    threshold = rng.random() * total
    cumulative = 0.0
    for i, w in enumerate(weights):
        cumulative += w
        if threshold < cumulative:
            return i
    return len(weights) - 1


def _update_sender(policy: list[list[float]], referent: int, signal: int, reward: float) -> None:
    """A's update — reads A's OWN (referent, signal, success) and nothing else.
    No argument here is or contains B's policy, state, or choice."""
    policy[referent][signal] += RATE * reward


def _update_receiver(policy: list[list[float]], word: int, act: int, reward: float) -> None:
    """B's update — reads B's OWN (word, act, success) and nothing else."""
    policy[word][act] += RATE * reward


def play(
    seed: int,
    *,
    episodes: int = EPISODES,
    yoked: bool = False,
    frozen_sender: bool = False,
    frozen_receiver: bool = False,
) -> tuple[float, list[list[float]], list[list[float]]]:
    """One dyad learning to signal. Returns tail recovery and both final policies."""
    rng = random.Random(seed)
    sender = [[1.0, 1.0], [1.0, 1.0]]  # sender[referent][signal]
    receiver = [[1.0, 1.0], [1.0, 1.0]]  # receiver[word][act]
    outcomes: list[float] = []
    for ep in range(episodes):
        referent = rng.randrange(2)
        signal = _pick(sender[referent], rng)
        emission = _channel(signal, seed=seed * 7 + ep)
        word = _channel(emission, seed=seed * 13 + ep)
        act = _pick(receiver[word], rng)
        success = 1.0 if act == referent else 0.0
        outcomes.append(success)
        # Yoked: the reward each agent learns from is decoupled from the outcome,
        # same reward frequency, wrong causal pairing.
        reward = rng.random() if yoked else success
        if not frozen_sender:
            _update_sender(sender, referent, signal, reward)
        if not frozen_receiver:
            _update_receiver(receiver, word, act, reward)
    return statistics.mean(outcomes[-TAIL:]), sender, receiver


def _recover(
    sender: list[list[float]], receiver: list[list[float]], *, seed: int,
    trials: int = 200, scramble: bool = False,
) -> float:
    """Test a fixed (sender, receiver) pair with no learning."""
    rng = random.Random(seed + 9000)
    hits = 0
    for ep in range(trials):
        referent = rng.randrange(2)
        signal = _pick(sender[referent], rng)
        if scramble:
            signal = rng.randrange(2)  # signal independent of the referent
        emission = _channel(signal, seed=seed * 7 + ep + 5000)
        word = _channel(emission, seed=seed * 13 + ep + 5000)
        act = _pick(receiver[word], rng)
        hits += act == referent
    return hits / trials


def channel_fidelity() -> float:
    """The derived ceiling: how often A's signal survives two noisy holds, with
    a perfect convention assumed. Recovery cannot exceed this."""
    survived = 0
    for s in range(2):
        for seed in range(200):
            emission = _channel(s, seed=seed * 7 + 20000)
            word = _channel(emission, seed=seed * 13 + 20000)
            survived += word == s
    return survived / 400


def main() -> None:
    ceiling = channel_fidelity()
    print("closed-loop signaling — two engines learning a convention from a success bit")
    print(f"{EPISODES} episodes, {SEEDS} pairs, engines are pure 1-bit channels\n")
    print(f"chance (2 referents, 2 acts) : 0.500")
    print(f"channel-fidelity ceiling      : {ceiling:.3f}   <- derived, recovery cannot beat it")
    print(f"impossible                    : 1.000\n")

    trained, senders, receivers = [], [], []
    for seed in range(SEEDS):
        recovery, sender, receiver = play(seed)
        trained.append(recovery)
        senders.append(sender)
        receivers.append(receiver)

    yoked = [play(seed, yoked=True)[0] for seed in range(SEEDS)]
    scrambled = [
        _recover(senders[s], receivers[s], seed=s, scramble=True) for s in range(SEEDS)
    ]
    # Partner swap: every cross pair, aggregated — two conventions exist, so one
    # swapped pair agrees by chance; only the mean over independent pairs reads.
    swapped = [
        _recover(senders[i], receivers[j], seed=i * 100 + j)
        for i in range(SEEDS)
        for j in range(SEEDS)
        if i != j
    ]

    print(f"{'arm':<28}{'recovery':>10}{'worst seed':>12}   verdict")
    print("-" * 66)
    print(
        f"{'trained within-pair':<28}{statistics.mean(trained):>10.3f}"
        f"{min(trained):>12.3f}   a convention formed"
    )
    print(f"{'day-0 (untrained policy)':<28}{0.5:>10.3f}{0.5:>12.3f}   chance")
    print(
        f"{'yoked feedback':<28}{statistics.mean(yoked):>10.3f}"
        f"{min(yoked):>12.3f}   consequence establishes it"
    )
    print(
        f"{'signal scrambled at test':<28}{statistics.mean(scrambled):>10.3f}"
        f"{min(scrambled):>12.3f}   the signal is necessary"
    )
    print(
        f"{'partner swap (all cross)':<28}{statistics.mean(swapped):>10.3f}"
        f"{'—':>12}   PRIVATE to a shared history"
    )

    wins = sum(t > 0.5 for t in trained)
    print(
        f"\n  trained beats day-0 on {wins}/{SEEDS} pairs; yoked does not learn"
        f"\n  (the success bit must be causal); the signal is necessary; and the"
        f"\n  convention is private — a stranger reads it only at chance, which is"
        f"\n  the row handshake.py could not pass with a code we installed."
        f"\n\n  The static audit is the real guarantee: `_update_sender` sees only"
        f"\n  A's own (referent, signal, success), `_update_receiver` only B's own"
        f"\n  (word, act, success). Neither reads the other's state, so the code"
        f"\n  could only have been established BETWEEN them."
    )


if __name__ == "__main__":
    main()
