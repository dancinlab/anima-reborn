"""The modulation is synergy — honestly bounded: interaction information over the a_cur x a_past grid.

`context_modulation.py` showed the held past modulates the current write but left one caveat: it did
not compute the interaction information, so it did not call the composition "synergy". This pins the
close: the multiplicative gate's read carries the PAIR (past, current) beyond the sum of each
(II > floor), and it is larger than the additive gate's — but NOT against a clean zero (the count's
saturation makes any two inputs interact a little, so the additive gate has a weaker residual II).
The contrast is quantitative, not qualitative. Full grid + nulls in
`state/communication/context_synergy.py` and RESULTS.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "context_synergy.py"
_spec = importlib.util.spec_from_file_location("context_synergy", _PATH)
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)


class TestModulationIsSynergy:
    def test_multiplicative_gate_is_super_additive(self) -> None:
        """The read carries the (cur, past) pair beyond the sum of the marginals — II above floor."""
        rows = cs._grid_reads("mult")
        ii, ij, ic, ip, fmax, _ = cs._interaction(rows, shuffle_seed=31)
        assert ii > fmax + 0.03, (ii, fmax)
        assert ij > ic + ip, (ij, ic, ip)   # joint tells more than the two marginals summed

    def test_multiplicative_synergy_exceeds_additive(self) -> None:
        """Multiplicative interaction is larger than the additive gate's — the quantitative contrast."""
        ii_m, *_ = cs._interaction(cs._grid_reads("mult"), shuffle_seed=31)
        ii_a, *_ = cs._interaction(cs._grid_reads("add"), shuffle_seed=37)
        assert ii_m > ii_a + 0.03, (ii_m, ii_a)

    def test_additive_is_not_a_clean_null(self) -> None:
        """Honesty guard: the additive gate is NOT zero synergy — the count saturation gives a weak
        residual interaction. If a future change makes it read ~0, this test flags the claim drift."""
        ii_a, _ij, _ic, _ip, fmax, _ = cs._interaction(cs._grid_reads("add"), shuffle_seed=37)
        assert ii_a > 0.0, ii_a           # it interacts a little — not a clean null
        assert ii_a < 0.15, ii_a          # but clearly weaker than the multiplicative ~0.17

    def test_reproducible(self) -> None:
        a = cs._interaction(cs._grid_reads("mult"), shuffle_seed=31)[0]
        b = cs._interaction(cs._grid_reads("mult"), shuffle_seed=31)[0]
        assert a == b
