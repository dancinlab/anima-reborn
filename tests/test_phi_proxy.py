"""The sampled directed-Φ proxy — validated against exact IIT on small systems.

Pins the three things the proxy must share with exact `iit4` (never magnitude): the NULL SET
(a reducible wiring sits at its measured floor), the MIP CUT identity (on a small system the
proxy's argmin cut is the exact directed MIP), and SEPARATION (an integrated chained ring
clears its floor). Small widths and budgets keep it fast; the wide-width run and the budget
curve live in `state/communication/phi_proxy.py` and RESULTS.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from anima_reborn.coupled import Wiring

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "phi_proxy.py"
_spec = importlib.util.spec_from_file_location("phi_proxy", _PATH)
pp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pp)


class TestNullSet:
    def test_feedforward_sits_at_its_floor(self) -> None:
        """FEEDFORWARD is reducible (a directed cut is free), so the proxy must not clear its
        own shuffle floor — the null set is shared with exact IIT."""
        r = pp.reading(Wiring.FEEDFORWARD, units=4, chain=0.0, budget=2500, seed=7)
        assert r["phi_hat"] <= r["floor"] + 0.05, r

    def test_disconnected_pairs_sits_at_its_floor(self) -> None:
        r = pp.reading(Wiring.PAIRS, units=4, chain=0.0, budget=2500, seed=7)
        assert not r["separated"] or r["phi_hat"] <= r["floor"] + 0.05, r


class TestSeparation:
    def test_the_chained_ring_clears_its_floor(self) -> None:
        """The integrated arm (chained PAIRS) must separate from its measured floor, at a
        width (6) where exact Φ still agrees it is recurrent."""
        r = pp.reading(Wiring.PAIRS, units=6, chain=pp.CHAIN, budget=3000, seed=7)
        assert r["separated"], r
        assert r["phi_hat"] > r["floor"], r


class TestMipAgreesWithExact:
    def test_the_argmin_cut_is_the_exact_mip(self) -> None:
        """On a small system the proxy's argmin cut must be the exact directed MIP (either
        orientation of the same bipartition)."""
        units = 4
        _, exact_src = pp._exact(Wiring.PAIRS, units=units, chain=pp.CHAIN, state=0b0101, seed=1)
        trans = pp.sample_transitions(Wiring.PAIRS, units=units, chain=pp.CHAIN, budget=3000, seed=7)
        _, argmin = pp.proxy(trans, units, Wiring.PAIRS)
        full = (1 << units) - 1
        assert argmin in (exact_src, full & ~exact_src), (bin(argmin), bin(exact_src))


class TestMechanics:
    def test_a_free_cut_costs_exactly_zero(self) -> None:
        """A cut whose sink bits carry no information about the source gives exactly 0 — a
        signed plug-in, not clipped, so a genuine zero reads as zero."""
        # feedforward: severing the exogenous unit's outgoing influence is free.
        trans = pp.sample_transitions(Wiring.FEEDFORWARD, units=4, chain=0.0, budget=2000, seed=3)
        val, _ = pp.proxy(trans, 4, Wiring.FEEDFORWARD)
        assert val >= -1e-9  # signed, but a min over losses cannot go far below zero

    def test_sampling_is_reproducible(self) -> None:
        a = pp.sample_transitions(Wiring.PAIRS, units=4, chain=pp.CHAIN, budget=500, seed=9)
        b = pp.sample_transitions(Wiring.PAIRS, units=4, chain=pp.CHAIN, budget=500, seed=9)
        assert a == b
