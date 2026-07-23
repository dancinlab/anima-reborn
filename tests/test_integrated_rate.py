"""Integration and held depth are not exclusive — and the exact-Phi magnitude here is an artefact.

`rate.py`'s RateCell is chain 0 (independent pairs) and its docstring calls that "holds depth, not
Phi" — a structural claim. This pins what the measurement found: a SMALL chain integrates (by the
phi_proxy decay/separation test, the repo's valid verdict) while the held depth stays above floor,
so chain 0 was a choice, not a necessity; a LARGE chain does trade the depth away. It also pins the
artefact that made an earlier draft read a false coexistence: at 6 units a chain-0 population of
INDEPENDENT pairs — which cannot integrate — still reads a large exact directed Phi. If that guard
ever passes silently, someone has started quoting the magnitude as integration again.
Full sweep + nulls in `state/communication/integrated_rate.py` and RESULTS.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "integrated_rate.py"
_spec = importlib.util.spec_from_file_location("integrated_rate", _PATH)
ir = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ir)

UNITS = 2 * ir.EXACT_PAIRS   # 6


class TestIntegrationAndDepth:
    def test_chain_zero_is_not_integrated(self) -> None:
        """Independent pairs (chain 0) do not integrate — the decay-test verdict, not the magnitude."""
        assert ir._integrated(0.0, units=UNITS) is False

    def test_a_small_chain_integrates(self) -> None:
        """A modest chain turns the population integrated by the same decay test."""
        assert ir._integrated(0.05, units=UNITS) is True

    def test_the_exact_phi_magnitude_is_an_artefact_at_this_width(self) -> None:
        """THE GUARD: chain-0 independent pairs cannot integrate, yet the exact directed Phi reads
        large at 6 units. This is the width-artefact `coupled.py`/`phi_proxy.py` warn about — it is
        why the decay test is the verdict. If this ever reads ~0, the estimator changed and the
        docs' artefact note must be revisited (do not just delete this test)."""
        phi0 = ir._exact_phi(0.0, units=UNITS, seed=1)
        assert phi0 > 1.0, phi0                       # the artefact is present, and documented
        assert ir._integrated(0.0, units=UNITS) is False   # while the valid verdict says no

    def test_small_chain_keeps_the_depth_but_large_chain_trades_it(self) -> None:
        """Coexistence at a small chain; the trade only at a large one."""
        d_small, f_small = ir._depth(0.05, ir.EXACT_PAIRS, shuffle_seed=13)
        d_large, f_large = ir._depth(0.20, ir.EXACT_PAIRS, shuffle_seed=16)
        assert d_small - f_small > 0.15, (d_small, f_small)   # depth survives while integrated
        assert d_large - f_large < 0.10, (d_large, f_large)   # a large chain collapses it

    def test_reproducible(self) -> None:
        a = ir._held_count(0.5, 1, chain=0.05, n_pairs=ir.EXACT_PAIRS, seed=5)
        b = ir._held_count(0.5, 1, chain=0.05, n_pairs=ir.EXACT_PAIRS, seed=5)
        assert a == b
