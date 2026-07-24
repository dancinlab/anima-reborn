"""The scaling rule over four widths and both parities — cheap guards on a cheap measurement.

`width16_scale.py` predicted width 16's crossing budget and hit it, but flagged a confound: width 14
is odd pairs and width 16 is even, and the macro-ring can lock at even pair counts. Its stated
follow-up (width 18, odd) turned out to cost hours per row. `scaling_law.py` closes the confound in
the cheap direction instead — pushing the same rule DOWNWARD to widths 10 (odd) and 12 (even), so
the rule is tested at both parities twice.

Unlike the widths above, these are fast enough to re-derive in the suite: the whole width-10 pair of
rows is seconds. So these tests actually re-measure the width-10 crossing rather than only pinning
the arithmetic — and pin the derivation, the parity coverage, and the recorded cost wall besides.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "scaling_law.py"
_spec = importlib.util.spec_from_file_location("scaling_law", _PATH)
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)


class TestScalingLaw:
    def test_the_predicted_budget_is_derived_from_the_anchor(self) -> None:
        """Predictions must come from the rule, not from the runs. Width 14 is the anchor, so it
        predicts itself; each step of 2 units multiplies the budget by 4."""
        assert sl.predicted_budget(sl.ANCHOR_UNITS) == sl.ANCHOR_BUDGET
        assert sl.predicted_budget(12) == sl.ANCHOR_BUDGET // 4 == 4000
        assert sl.predicted_budget(10) == sl.ANCHOR_BUDGET // 16 == 1000
        assert sl.predicted_budget(16) == sl.ANCHOR_BUDGET * 4 == 64000

    def test_width_10_crosses_at_its_predicted_budget(self) -> None:
        """Re-measured, not just asserted: the cheapest width really does cross where the rule says."""
        _ring, _bar, gap, _secs = sl._gap(10, sl.predicted_budget(10))
        assert gap > 0.0, gap

    def test_width_10_has_not_crossed_one_rung_below(self) -> None:
        """The load-bearing half: if it had already crossed below the prediction, the prediction
        would be describing something that was there anyway."""
        _ring, _bar, gap, _secs = sl._gap(10, sl.predicted_budget(10) // 4)
        assert gap < 0.0, gap

    def test_both_parities_are_covered_by_the_new_widths(self) -> None:
        """The point of choosing 10 and 12: one odd pair count, one even — which, with 14 (odd) and
        16 (even), gives two of each. If someone narrows NEW_WIDTHS, the parity argument breaks."""
        parities = {(u // 2) % 2 for u in sl.NEW_WIDTHS}
        assert parities == {0, 1}, sl.NEW_WIDTHS
        assert {(u // 2) % 2 for u in sl.KNOWN} == {0, 1}, sl.KNOWN

    def test_the_width18_cost_wall_stays_recorded(self) -> None:
        """Width 18 was skipped for a MEASURED reason, and the number is part of the claim. If it is
        ever dropped, the section reads as an unexplained omission instead of a cost wall."""
        assert sl.WIDTH18_PROBE_SECS >= 300, sl.WIDTH18_PROBE_SECS
        assert sl.predicted_budget(18) == 256000
