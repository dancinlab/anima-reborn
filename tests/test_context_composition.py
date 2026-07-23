"""Conditional composition — the honest negative: the context gate cannot be told apart from
a planted lookup on this substrate.

Pins the mechanism identities (the no-gate write is the clean current word; the XOR arm is a
lookup on the log) and the estimator (interaction information is ~0 for independent inputs and
high for a synthetic XOR). The full synergy + depth-sensitivity sweep and the PRUNED verdict
live in `state/communication/context_composition.py` and RESULTS — a lookup and the gate score
the SAME synergy, and the depth control that would separate them sits at its floor.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "context_composition.py"
_spec = importlib.util.spec_from_file_location("context_composition", _PATH)
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)


class TestTheEstimator:
    def test_interaction_is_zero_for_independent_inputs(self) -> None:
        # R depends on C only, independent of P → no interaction information.
        rows = [(c, p, c) for c in range(8) for p in range(8) for _ in range(4)]
        assert abs(cc._interaction(rows)) < 1e-9, cc._interaction(rows)

    def test_interaction_is_high_for_xor(self) -> None:
        # R = C xor P over balanced inputs → full 3-bit synergy, marginals uninformative.
        rows = [(c, p, c ^ p) for c in range(8) for p in range(8)]
        assert cc._interaction(rows) > 2.9, cc._interaction(rows)
        assert cc._mi([(c, r) for c, _, r in rows]) < 1e-9  # R alone tells nothing about C

    def test_mi_matches_a_known_value(self) -> None:
        # Two perfectly-correlated 3-bit variables share 3 bits.
        rows = [(x, x) for x in range(8) for _ in range(3)]
        assert abs(cc._mi(rows) - 3.0) < 1e-9


class TestTheMechanism:
    def test_the_no_gate_write_is_the_clean_current_word(self) -> None:
        """At gate=0 the response is the ordinary current write — the past cannot reach it."""
        hits = 0
        for current in range(8):
            for s in range(6):
                diffs, _ = cc._held((current + 3) % 8, seed=100 + s)
                r = cc._response(current, diffs, gate=0.0, seed=200 + current * 7 + s)
                hits += int(r == current)
        assert hits >= 44, hits  # out of 48; the clean 3-bit channel is measured-clean

    def test_held_is_reproducible(self) -> None:
        assert cc._held(5, seed=9) == cc._held(5, seed=9)

    def test_the_xor_arm_is_a_lookup_on_the_symbol_log(self) -> None:
        rows = cc._collect(0.0, arm="xor")[:200]
        assert all(r == (c ^ p) for c, p, r in rows)
