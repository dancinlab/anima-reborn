"""Two engines establishing a convention neither was given.

The last piece of the communication line: reward-gated plasticity closes the
learning loop `handshake.py` showed was open. The engines stay pure 1-bit
channels; the plasticity is in the harness, and its updates are factored so that
neither agent's update reads the other's private state — the static audit that
defeats the experimenter-owned-codec trap. Full game and controls in
`state/communication/signaling.py`; these run a short version.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "state" / "communication"))

import signaling  # noqa: E402


def _trained(seed: int):
    return signaling.play(seed, episodes=400)


class TestAConventionForms:
    def test_recovery_beats_chance_on_every_pair(self) -> None:
        """A convention neither agent was given: recovery over 0.5, per pair."""
        recoveries = [_trained(s)[0] for s in range(3)]
        assert statistics.mean(recoveries) > 0.7, recoveries
        assert all(r > 0.5 for r in recoveries), recoveries

    def test_the_consequence_is_what_establishes_it(self) -> None:
        """Yoked feedback — the success bit decoupled from the outcome — learns
        nothing, so exposure alone does not form the code."""
        yoked = [signaling.play(s, episodes=400, yoked=True)[0] for s in range(3)]
        assert statistics.mean(yoked) < 0.6, yoked

    def test_the_convention_is_private_to_the_pair(self) -> None:
        """The row handshake.py could not pass: a stranger reads the code only at
        chance, aggregated over independent pairs (two conventions exist, so any
        single swapped pair agrees by luck half the time)."""
        pairs = [_trained(s) for s in range(3)]
        within = statistics.mean(
            signaling._recover(s, r, seed=i) for i, (_, s, r) in enumerate(pairs)
        )
        cross = statistics.mean(
            signaling._recover(pairs[i][1], pairs[j][2], seed=i * 100 + j)
            for i in range(3)
            for j in range(3)
            if i != j
        )
        assert within > 0.7, within
        assert cross < 0.65, cross
        assert within - cross > 0.15, (within, cross)


class TestTheStaticAudit:
    """The trap both delegated designs named: a code installed at training time
    passes every runtime control. The guarantee is structural — the update
    functions cannot see across the gap."""

    def test_sender_update_takes_only_the_senders_locals(self) -> None:
        import inspect

        params = list(inspect.signature(signaling._update_sender).parameters)
        assert params == ["policy", "referent", "signal", "reward"], params

    def test_receiver_update_takes_only_the_receivers_locals(self) -> None:
        import inspect

        params = list(inspect.signature(signaling._update_receiver).parameters)
        assert params == ["policy", "word", "act", "reward"], params
