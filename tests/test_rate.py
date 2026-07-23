"""RateCell — the population rate cell packages the measured hold-and-consume into an engine.

Pins the two things a single latch cannot do at once (the whole point of the state/communication
line): the population HOLDS a past symbol's analog depth as a stable count (rate rises with depth),
and a fixed current symbol reads DIFFERENTLY by the held past while keeping its own sign. The full
MI battery + nulls live in state/communication/{rate_code,context_modulation,context_synergy}.py;
these guard that the shipped engine still exhibits the effect. Reproducible under seed=.
"""

from __future__ import annotations

import statistics

from anima_reborn.rate import PAST_DEPTHS, RateCell


class TestRateCell:
    def test_held_rate_rises_with_past_depth(self) -> None:
        """The population holds the past symbol's analog depth as a count — deeper past, higher rate."""
        rates = [statistics.mean(RateCell(seed=s).tell(d, 1) for s in range(8)) for d in PAST_DEPTHS]
        assert rates == sorted(rates), rates
        assert rates[-1] - rates[0] > 0.15, rates

    def test_current_read_tracks_the_held_past(self) -> None:
        """A FIXED current symbol reads differently by the held past — context, the held past acting."""
        counts = []
        for d in PAST_DEPTHS:
            cs = []
            for s in range(8):
                cell = RateCell(seed=s)
                cell.tell(d, 1)
                cs.append(cell.consume(0.5, 1))
            counts.append(statistics.mean(cs))
        assert counts[-1] - counts[0] > 1.5, counts   # the read moves with the held past

    def test_both_current_signs_survive(self) -> None:
        """The positive gain never flips the current sign — the symbol survives while modulated."""
        cell = RateCell(seed=1)
        cell.tell(0.8, 1)
        assert cell.consume(0.5, +1) > cell.n_pairs // 2   # + reads up
        cell.tell(0.8, 1)
        assert cell.consume(0.5, -1) < cell.n_pairs // 2   # - reads down

    def test_consume_before_tell_is_an_error(self) -> None:
        import pytest
        with pytest.raises(ValueError):
            RateCell(seed=0).consume(0.5, 1)

    def test_step_cycles_phases_and_describe_reads(self) -> None:
        """The passive viewer contract: step() advances the phase cycle; describe() only reads."""
        cell = RateCell(seed=3)
        seen = set()
        before = cell.describe()
        for _ in range(200):
            cell.step()
            seen.add(cell.describe()["phase"])
        after = cell.describe()
        assert seen == {"tell", "hold", "consume"}, seen
        assert after == cell.describe()          # describe does not advance
        assert before["phase"] == "tell"

    def test_reproducible(self) -> None:
        assert RateCell(seed=7).tell(0.5, 1) == RateCell(seed=7).tell(0.5, 1)
