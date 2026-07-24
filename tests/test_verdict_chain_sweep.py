"""The joint operating point at the verdict width — a window closed at BOTH ends.

integrated_context.py compared only two chains (0 and 0.05). The sweep across 0.02..0.15 at the
verdict width (5 pairs = 10 units) found that integration margin rises monotonically with the chain
while the CONTEXT window closes at both ends: too weak and the read sits at floor, too strong and the
coupling takes the gate over. The joint maximum is chain 0.11. These pin the shape (a bounded
window), not just the existence of one point — the full table lives in
`state/communication/verdict_chain_sweep.py` and RESULTS.

Each check drives the shipped measurement's own helpers, so a change in the underlying battery or in
the matched-ceiling verdict is caught here rather than silently re-shaping the window.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from anima_reborn.coupled import Wiring

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "verdict_chain_sweep.py"
_spec = importlib.util.spec_from_file_location("verdict_chain_sweep", _PATH)
vs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vs)

UNITS = vs.UNITS          # 10
PAIRS_N = vs.PAIRS_N      # 5


class TestJointWindow:
    def test_integration_margin_rises_with_the_chain(self) -> None:
        """More coupling buys more integration margin over the width-matched reducible bar."""
        bar, _ = vs.wi.matched_ceiling(units=UNITS, budget=vs.BUDGET)
        lo = vs.wi.arm_summary(Wiring.PAIRS, 0.02, units=UNITS, budget=vs.BUDGET)["phi_hat"] - bar
        hi = vs.wi.arm_summary(Wiring.PAIRS, 0.15, units=UNITS, budget=vs.BUDGET)["phi_hat"] - bar
        assert hi > lo + 0.1, (lo, hi)

    def test_the_context_window_is_closed_at_the_weak_end(self) -> None:
        """At chain 0.02 the read sits at its floor — integrated, but no usable context."""
        b = vs.ic._battery(PAIRS_N, 0.02, tag="test")
        assert not b["window"], (b["obs"], b["floor"], b["fid"])

    def test_the_context_window_is_closed_at_the_strong_end(self) -> None:
        """At chain 0.15 the coupling takes the gate over — a takeover, not a joint point."""
        b = vs.ic._battery(PAIRS_N, 0.15, tag="test")
        assert not b["window"], (b["obs"], b["floor"], b["fid"])

    def test_the_joint_point_holds_both(self) -> None:
        """At chain 0.11 the population is integrated (matched verdict) AND the gate is alive."""
        arm = vs.wi.arm_summary(Wiring.PAIRS, 0.11, units=UNITS, budget=vs.BUDGET)
        assert vs.wi.matched_integrated(arm["phi_hat"], units=UNITS, budget=vs.BUDGET)
        b = vs.ic._battery(PAIRS_N, 0.11, tag="test")
        assert b["window"] and b["obs"] > b["floor"] + 0.05 and b["fid"] >= 0.95, b

    def test_the_read_width_stays_tiny_here(self) -> None:
        """report-the-rank guard: 10 units means count 0..5, so the read carries ~1 level. If this
        ever reads much wider, the narrow-width caveat in RESULTS must be revisited, not deleted."""
        b = vs.ic._battery(PAIRS_N, 0.11, tag="test")
        assert 2 ** b["obs"] < 1.5, b["obs"]
