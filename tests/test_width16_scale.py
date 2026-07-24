"""The budget-scaling rule predicted an unmeasured width — guard the PRE-REGISTRATION.

`scale_ceiling.py` established that the width-14 collapse was undersampling and that the matched
ceiling is a budget statement. `width16_scale.py` turned that into a prediction — width 16 has 4x
the state space, so it should cross at 4x the budget (64000) — wrote the number down BEFORE running,
and it crossed there with the same gap (+0.110) width 14 had at its own crossing.

The value of that result lives entirely in the prediction having been fixed in advance. So what these
tests pin is the DERIVATION, not the expensive crossing: the predicted budget must equal the
state-space ratio times width 14's crossing budget, so nobody can quietly retune it to whatever the
run produced. The crossing itself (~32 minutes for the 64000 row) stays in the script and RESULTS.

They also pin the two honesty limits the script fixed in advance: one seed (so NOT a certification)
and the even/odd pair-count difference from width 14.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "width16_scale.py"
_spec = importlib.util.spec_from_file_location("width16_scale", _PATH)
w16 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w16)


class TestPreRegistration:
    def test_the_predicted_budget_is_derived_not_fitted(self) -> None:
        """PREDICTED_CROSSING must be width 14's crossing budget times the state-space ratio
        (2^16 / 2^14 = 4). If someone edits it to match a run, this fails — which is the whole
        point of having pre-registered it."""
        ratio = 2 ** w16.UNITS / 2 ** 14
        assert ratio == 4
        assert w16.PREDICTED_CROSSING == w16.W14_CROSSING["budget"] * ratio, (
            w16.PREDICTED_CROSSING, w16.W14_CROSSING["budget"], ratio)

    def test_the_grid_actually_contains_the_predicted_budget(self) -> None:
        """The prediction is only tested if the grid runs at that budget, with a lower rung to show
        it had NOT crossed earlier."""
        assert w16.PREDICTED_CROSSING in w16.BUDGETS, w16.BUDGETS
        assert min(w16.BUDGETS) < w16.PREDICTED_CROSSING, w16.BUDGETS

    def test_the_width14_reference_matches_what_scale_ceiling_reported(self) -> None:
        """The comparison row is quoted from the 3-seed scale_ceiling result; if that section is
        ever re-measured, this catches the quote going stale."""
        assert w16.W14_CROSSING == {"budget": 16000, "ring": 0.633, "bar": 0.523, "gap": 0.110}

    def test_the_honesty_limits_are_declared_in_code(self) -> None:
        """One seed means this cannot certify a width, and 16 units is an EVEN pair count where
        width 14 was odd. Both limits are stated in RESULTS; if the code drifts from them (e.g.
        someone adds seeds and calls it certified without re-running), this fails first."""
        assert isinstance(w16.SEED, int), w16.SEED          # a single seed, not a tuple
        assert w16.UNITS % 4 == 0, w16.UNITS                # 16 units = 8 pairs = EVEN pair count
        assert (w16.UNITS // 2) % 2 == 0                    # the parity that differs from width 14
        assert (14 // 2) % 2 == 1                           # width 14 was 7 pairs = odd
