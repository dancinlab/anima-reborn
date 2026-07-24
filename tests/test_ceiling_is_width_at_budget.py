"""A ceiling is width@budget, never a width wall — guard the correction, not just the numbers.

`wide_integration.py` reported two trust ceilings and closed with "Neither reaches 16", and its
RESULTS section banned the claim "raising the budget makes the wall disappear". Later work overturned
both: `scale_ceiling.py` measured width 14 crossing at budget 16000, `width16_scale.py` predicted and
hit width 16 at 64000, and `scaling_law.py` confirmed the same rule downward at widths 10 and 12
across both pair parities.

Those sections were corrected in place with the correction MARKED rather than rewritten away
(`artefact-honesty`). The risk now is the opposite of the original error: a future edit tidies the
strikethrough away and the repo silently reads as a width wall again. These tests are cheap text
guards that keep the correction attached to the claim it corrects — no measurement, just the
invariant that the two documents still say the qualified thing.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _ROOT / "state" / "communication" / "wide_integration.py"
_RESULTS = _ROOT / "state" / "communication" / "RESULTS.md"


class TestCeilingIsQualified:
    def test_the_script_docstring_carries_the_correction(self) -> None:
        """The module that produced the ceilings must say they are width@budget, and must name the
        measurements that corrected it — so a reader of the script alone is not misled."""
        text = _SCRIPT.read_text(encoding="utf-8")
        head = text[: text.index('"""', 3)]
        assert "WIDTH@BUDGET" in head, "the width@budget correction left the docstring"
        for cited in ("scale_ceiling.py", "width16_scale.py", "scaling_law.py"):
            assert cited in head, f"the correction no longer cites {cited}"

    def test_the_runtime_output_says_it_too(self) -> None:
        """Someone who runs the script sees only its prints, so the qualifier has to be in them —
        both ceilings, not just the docstring."""
        text = _SCRIPT.read_text(encoding="utf-8")
        assert "Absolute-test ceiling AT BUDGET" in text
        assert "Matched-test trust ceiling AT BUDGET" in text
        assert "never a width wall" in text
        assert "MOVES with the budget" in text

    def test_results_marks_the_overturned_ban_rather_than_deleting_it(self) -> None:
        """The banned claim that later proved TRUE must stay visible as struck-through with the
        correction beside it. If it is simply removed, the ledger loses the fact that the repo once
        banned the right answer — which is the part worth remembering."""
        text = _RESULTS.read_text(encoding="utf-8")
        assert "budget을 올리면 벽이 사라진다" in text, "the overturned ban was deleted, not marked"
        assert "이 금지는 이후 측정으로 뒤집혔다" in text
        assert "폭@budget" in text

    def test_the_correction_keeps_what_did_not_change(self) -> None:
        """A correction that overclaims in the other direction is the same failure. The ledger must
        still say the absolute test is untrustworthy past 4 units and that nothing is unbounded."""
        text = _RESULTS.read_text(encoding="utf-8")
        assert "폭 18은 여전히 도달 불가" in text
        assert "무제한은 아니다" in text
