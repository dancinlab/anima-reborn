"""The reproducible half of human<->engine dialogue, with a synthetic partner.

A human is not seedable, so the reproducible claim is measured against a scripted
stand-in; the real human takes the partner's seat in the viewer later. These pin
that the engine's reward-gated policy forms a convention, that the engine's
learned half is load-bearing (not an echo), and that the update rule cannot see
across the gap. Full game in `state/communication/dialogue.py`.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "state" / "communication"))

import dialogue  # noqa: E402


class TestAConventionForms:
    def test_both_directions_beat_chance(self) -> None:
        dyads = [dialogue.play(s, episodes=400) for s in range(3)]
        assert statistics.mean(d["a"] for d in dyads) > 0.7
        assert statistics.mean(d["b"] for d in dyads) > 0.7

    def test_the_engines_learned_half_is_load_bearing_not_an_echo(self) -> None:
        """Frozen at its random day-0 map, the engine cannot recover with a fully
        trained partner — so the code is not the engine handing the bit back."""
        frozen = [dialogue.play(s, episodes=400, frozen_engine=True)["a"] for s in range(3)]
        assert statistics.mean(frozen) < 0.6, frozen

    def test_the_consequence_establishes_it(self) -> None:
        yoked = [dialogue.play(s, episodes=400, yoked=True)["a"] for s in range(3)]
        assert statistics.mean(yoked) < 0.6, yoked

    def test_the_convention_is_private_to_the_pair(self) -> None:
        dyads = [dialogue.play(s, episodes=400) for s in range(3)]
        within = statistics.mean(
            dialogue._probe(d["policies"], seed=i, direction="a")
            for i, d in enumerate(dyads)
        )
        cross = statistics.mean(
            dialogue._probe(
                (dyads[i]["policies"][0], dyads[j]["policies"][1], None, None),
                seed=i * 100 + j, direction="a",
            )
            for i in range(3) for j in range(3) if i != j
        )
        assert within > 0.7, within
        assert cross < 0.65, cross


class TestTheStaticAudit:
    def test_the_update_rule_reads_only_one_agents_locals(self) -> None:
        import inspect

        params = list(inspect.signature(dialogue._reinforce).parameters)
        assert params == ["policy", "state", "choice", "reward"], params
