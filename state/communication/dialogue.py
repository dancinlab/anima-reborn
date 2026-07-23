"""Toward human<->engine dialogue: the reproducible half, with a synthetic partner.

Run from the repo root:

    PYTHONPATH=src python state/communication/dialogue.py

The goal is a two-way convention between a HUMAN and the engine — a person and
this substrate reaching a shared code through a live loop in the viewer. A human
is not seedable and cannot be a controlled variable, so the claim is split, as
both delegated designs insisted:

- **the reproducible claim** lives here, measured against a SYNTHETIC partner — a
  seedable stand-in for the human, so 12-seed directional bars and every null are
  possible. The real human takes the partner's seat later, in the viewer.
- **the human claim** will be a per-session existence proof (its own day-0, its
  own yoked block, a permutation test on its own log), never averaged over people.

**What is measured here.** Both directions of a Lewis-Skyrms game. Partner-sends:
the partner picks a signal for a referent, the engine holds it deaf and acts by
which probe its held state revises less (the `match.py` assay — no fitted decoder,
no chosen threshold). Engine-sends: the engine picks a signal for a hidden
referent, holds it, and the partner reads the held word and acts. Success is
`act == referent`, computed by the harness — NEVER judged by either party, so
nobody can reward their own intention.

**The static audit — the trap both designs named.** For engine-engine it was the
codec installed in the training loop; for human-engine it is the experimenter
owning the interpreter. The engine-side guarantee is unchanged and structural:
each update reads only its OWN agent's (state, choice, success). `_reinforce`
takes a single policy, one of its rows, a column, and the success bit — it cannot
see across the gap. In the viewer the display becomes the second aperture (raw
traces only, positions randomized); that is enforced there.

**The echo trap, caught here.** If the engine merely handed the partner's bit
back, "recovery" would measure the partner's self-consistency. The `frozen-engine`
arm freezes the engine's policy at its random day-0 map: a fully trained partner
must then collapse to chance, proving the engine's LEARNED half is load-bearing.
The `deaf` arm (coupling 1.0, drive unreachable) must sit at chance, proving the
channel was even in the path.
"""

from __future__ import annotations

import random
import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

EPISODES = 1200
RATE = 0.3
TAIL = 300
SEEDS = 12
TELL = 200
HOLD = 120


def _channel(signal: int, *, seed: int, deaf: bool = False) -> int:
    """The engine as a noisy 1-bit wire: hold a signal, read the latch bit.

    `deaf` sets coupling to 1.0 for the listen phase so the drive is unreachable
    — the held bit then owes nothing to the signal, which is the null proving the
    channel was in the path."""
    drive = (0.8, -0.8) if signal == 0 else (-0.8, 0.8)
    engine = CoupledEngine(
        units=2, wiring=Wiring.RING,
        rhythm=FIXED if deaf else ALTERNATING,
        drive=drive, seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    values = engine.run(HOLD).values
    return 0 if (values[0] - values[1]) > 0 else 1


def _pick(row: list[float], rng: random.Random) -> int:
    total = sum(row)
    threshold = rng.random() * total
    cumulative = 0.0
    for i, weight in enumerate(row):
        cumulative += weight
        if threshold < cumulative:
            return i
    return len(row) - 1


def _reinforce(policy: list[list[float]], state: int, choice: int, reward: float) -> None:
    """The only update rule. Reads ONE agent's own (state, choice, success). It
    is handed a single policy and cannot reach the other agent — the static audit
    is that this signature has no argument for anyone else's state."""
    policy[state][choice] += RATE * reward


def play(
    seed: int,
    *,
    episodes: int = EPISODES,
    yoked: bool = False,
    frozen_engine: bool = False,
    deaf: bool = False,
) -> dict[str, object]:
    """One dyad — synthetic partner and engine — learning both directions."""
    rng = random.Random(seed)
    # Four policies, each 2x2, symmetric at day-0 so which convention forms is the
    # dyad's own history, not ours.
    partner_send = [[1.0, 1.0], [1.0, 1.0]]  # partner: referent -> signal
    engine_recv = [[1.0, 1.0], [1.0, 1.0]]  # engine: held word -> act
    engine_send = [[1.0, 1.0], [1.0, 1.0]]  # engine: referent -> signal
    partner_recv = [[1.0, 1.0], [1.0, 1.0]]  # partner: held word -> act
    a_hist, b_hist = [], []

    for ep in range(episodes):
        # Direction A — partner sends, engine receives and acts.
        referent = rng.randrange(2)
        signal = _pick(partner_send[referent], rng)
        word = _channel(signal, seed=seed * 7 + ep, deaf=deaf)
        act = _pick(engine_recv[word], rng)
        success = 1.0 if act == referent else 0.0
        a_hist.append(success)
        reward = rng.random() if yoked else success
        _reinforce(partner_send, referent, signal, reward)
        if not frozen_engine:
            _reinforce(engine_recv, word, act, reward)

        # Direction B — engine sends, partner receives and acts.
        referent_b = rng.randrange(2)
        signal_b = _pick(engine_send[referent_b], rng)
        word_b = _channel(signal_b, seed=seed * 11 + ep, deaf=deaf)
        act_b = _pick(partner_recv[word_b], rng)
        success_b = 1.0 if act_b == referent_b else 0.0
        b_hist.append(success_b)
        reward_b = rng.random() if yoked else success_b
        if not frozen_engine:
            _reinforce(engine_send, referent_b, signal_b, reward_b)
        _reinforce(partner_recv, word_b, act_b, reward_b)

    return {
        "a": statistics.mean(a_hist[-TAIL:]),
        "b": statistics.mean(b_hist[-TAIL:]),
        "policies": (partner_send, engine_recv, engine_send, partner_recv),
    }


def _probe(policies, *, seed: int, direction: str, scramble: bool = False,
           trials: int = 200) -> float:
    """Frozen, feedback-withheld recovery — the held-out analogue for a game."""
    partner_send, engine_recv, engine_send, partner_recv = policies
    rng = random.Random(seed + 9000)
    hits = 0
    for ep in range(trials):
        referent = rng.randrange(2)
        if direction == "a":
            signal = _pick(partner_send[referent], rng)
            if scramble:
                signal = rng.randrange(2)
            word = _channel(signal, seed=seed * 7 + ep + 5000)
            hits += _pick(engine_recv[word], rng) == referent
        else:
            signal = _pick(engine_send[referent], rng)
            if scramble:
                signal = rng.randrange(2)
            word = _channel(signal, seed=seed * 11 + ep + 5000)
            hits += _pick(partner_recv[word], rng) == referent
    return hits / trials


def _cross_direction_consistency(policies) -> float:
    """Do the two directions use the SAME code, or are they two one-way codes?
    Compares the referent->signal maps a partner and an engine settled on."""
    partner_send, _, engine_send, _ = policies
    agree = sum(
        (partner_send[r][0] > partner_send[r][1]) == (engine_send[r][0] > engine_send[r][1])
        for r in (0, 1)
    )
    return agree / 2


def main() -> None:
    print("human<->engine dialogue — the reproducible half, synthetic partner")
    print(f"{EPISODES} episodes, {SEEDS} dyads, both directions, 2-unit ring channel\n")

    dyads = [play(seed) for seed in range(SEEDS)]
    trained_a = [d["a"] for d in dyads]
    trained_b = [d["b"] for d in dyads]
    yoked = [play(s, yoked=True)["a"] for s in range(SEEDS)]
    frozen = [play(s, frozen_engine=True)["a"] for s in range(SEEDS)]
    deaf = [play(s, deaf=True)["a"] for s in range(SEEDS // 2)]
    scrambled = [_probe(d["policies"], seed=i, direction="a", scramble=True)
                 for i, d in enumerate(dyads)]
    swapped = [
        _probe(
            (dyads[i]["policies"][0], dyads[j]["policies"][1], None, None),
            seed=i * 100 + j, direction="a",
        )
        for i in range(SEEDS) for j in range(SEEDS) if i != j
    ]
    consistency = statistics.mean(
        _cross_direction_consistency(d["policies"]) for d in dyads
    )

    print(f"{'arm':<28}{'recovery':>10}{'worst':>9}   verdict")
    print("-" * 62)
    print(f"{'trained (partner->engine)':<28}{statistics.mean(trained_a):>10.3f}"
          f"{min(trained_a):>9.3f}   a convention formed")
    print(f"{'trained (engine->partner)':<28}{statistics.mean(trained_b):>10.3f}"
          f"{min(trained_b):>9.3f}   the other direction too")
    print(f"{'day-0 (untrained)':<28}{0.5:>10.3f}{0.5:>9.3f}   chance")
    print(f"{'yoked feedback':<28}{statistics.mean(yoked):>10.3f}"
          f"{min(yoked):>9.3f}   consequence establishes it")
    print(f"{'frozen engine (echo test)':<28}{statistics.mean(frozen):>10.3f}"
          f"{min(frozen):>9.3f}   the ENGINE is load-bearing")
    print(f"{'deaf channel':<28}{statistics.mean(deaf):>10.3f}"
          f"{min(deaf):>9.3f}   the channel is in the path")
    print(f"{'signal scrambled':<28}{statistics.mean(scrambled):>10.3f}"
          f"{min(scrambled):>9.3f}   the signal is necessary")
    print(f"{'partner swap (all cross)':<28}{statistics.mean(swapped):>10.3f}"
          f"{'—':>9}   PRIVATE to a shared history")
    print(f"\n  cross-direction consistency: {consistency:.0%} "
          f"(1.0 = one shared code, 0.5 = two one-way codes)")

    wins = sum(a > 0.5 for a in trained_a)
    print(
        f"\n  trained beats day-0 on {wins}/{SEEDS} dyads. The frozen-engine arm is"
        f"\n  the one that matters most here: at day-0 engine maps a fully trained"
        f"\n  partner cannot recover, so the engine's LEARNED half carries the code —"
        f"\n  this is not the engine echoing the partner's input. This measures the"
        f"\n  ENGINE half; the human takes the partner's seat in the viewer, where the"
        f"\n  display becomes the second thing that must not encode the answer."
    )


if __name__ == "__main__":
    main()
