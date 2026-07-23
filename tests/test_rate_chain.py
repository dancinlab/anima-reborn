"""`RateCell(chain=)` — the default stays bit-identical, and a small chain keeps hold + consume.

`rate.py`'s RateCell was hardcoded chain 0. `state/communication/integrated_rate.py` measured that
chain 0.05 makes a 6-unit population integrated (phi_proxy decay test) at no measured held-depth
cost, so chain 0 was a CHOICE. This pins the parameter:

- `default-stays-exact` (MANDATORY): with the default chain the cell is BIT-identical to the
  pre-parameter behaviour every published number was taken on — tell()/consume() outputs and a run
  of step() frames match fixtures CAPTURED from the chain-0 code before the parameter existed. If
  this ever breaks, a trajectory moved and every downstream Phi/MI number must be re-derived.
- a small chain (0.05) still HOLDS the past depth (held rate rises with a_past) and still CONSUMES
  it (a fixed current symbol reads by the held past, BOTH current signs surviving the positive gain).
- the integration verdict is the phi_proxy decay test at 6 units — chain 0 not integrated, chain
  0.05 integrated — NEVER the raw exact-Phi magnitude (a width-artefact; guarded in
  tests/test_integrated_rate.py). This width (32 pairs) is NOT where that verdict is takeable, and
  the test asserts that scoping, not that the wide cell integrates.

Full sweep + nulls in `state/communication/rate_chain.py` and RESULTS.
"""

from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

import pytest

from anima_reborn.rate import CHAIN, INTEGRATED_CHAIN, PAST_DEPTHS, RateCell

# The pre-parameter fixtures — captured by running the CHAIN-0 code before `chain=` was added.
FIXTURE_TELL = [
    0.78125, 0.125, 0.9375, 0.0625, 1.0, 0.0,
    0.84375, 0.1875, 0.96875, 0.03125, 1.0, 0.0,
    0.78125, 0.28125, 0.9375, 0.125, 1.0, 0.0,
    0.5625, 0.28125, 0.9375, 0.03125, 1.0, 0.0,
]
FIXTURE_CONSUME = [
    26, 5, 30, 2, 30, 2, 30, 8, 31, 3, 31, 1,
    31, 7, 32, 2, 32, 2, 21, 7, 31, 0, 31, 0,
]
FIXTURE_FRAME_DIGEST = "78f81eb5c2276abbb58981bf450e8c2bc7eb3e0e43d009300bf977d9bf389579"


class TestDefaultStaysExact:
    def test_default_chain_is_zero(self) -> None:
        assert CHAIN == 0.0
        assert RateCell(seed=0).chain == 0.0

    def test_tell_is_bit_identical_at_the_default(self) -> None:
        got = [RateCell(seed=seed).tell(d, s)
               for seed in range(4) for d in (0.2, 0.5, 0.8) for s in (1, -1)]
        assert got == FIXTURE_TELL, got

    def test_consume_is_bit_identical_at_the_default(self) -> None:
        got = []
        for seed in range(4):
            for d in (0.2, 0.5, 0.8):
                cell = RateCell(seed=seed)
                cell.tell(d, 1)
                got.append(cell.consume(0.5, 1))
                cell.tell(d, 1)
                got.append(cell.consume(0.5, -1))
        assert got == FIXTURE_CONSUME, got

    def test_step_frames_are_bit_identical_at_the_default(self) -> None:
        """120 step() frames hash to the pre-parameter digest — the `chain` readout is new, so it is
        excluded from the hash; the DYNAMICS are what must not have moved."""
        import hashlib
        import json

        cell = RateCell(seed=3)
        frames = []
        for _ in range(120):
            cell.step()
            frames.append({k: v for k, v in cell.describe().items() if k != "chain"})
        digest = hashlib.sha256(json.dumps(frames, sort_keys=True).encode()).hexdigest()
        assert digest == FIXTURE_FRAME_DIGEST, digest

    def test_explicit_default_matches_implicit(self) -> None:
        assert RateCell(seed=1, chain=CHAIN).tell(0.5, 1) == RateCell(seed=1).tell(0.5, 1)

    def test_chain_out_of_range_is_an_error(self) -> None:
        with pytest.raises(ValueError):
            RateCell(seed=0, chain=1.5)
        with pytest.raises(ValueError):
            RateCell(seed=0, chain=-0.1)


class TestSmallChainKeepsTheCell:
    def test_held_rate_still_rises_with_past_depth(self) -> None:
        rates = [statistics.mean(RateCell(seed=s, chain=INTEGRATED_CHAIN).tell(d, 1)
                                 for s in range(8)) for d in PAST_DEPTHS]
        assert rates == sorted(rates), rates
        assert rates[-1] - rates[0] > 0.15, rates

    def test_current_read_still_tracks_the_held_past(self) -> None:
        counts = []
        for d in PAST_DEPTHS:
            cs = []
            for s in range(8):
                cell = RateCell(seed=s, chain=INTEGRATED_CHAIN)
                cell.tell(d, 1)
                cs.append(cell.consume(0.5, 1))
            counts.append(statistics.mean(cs))
        assert counts[-1] - counts[0] > 1.5, counts

    def test_both_current_signs_survive_the_gain(self) -> None:
        cell = RateCell(seed=1, chain=INTEGRATED_CHAIN)
        cell.tell(0.8, 1)
        assert cell.consume(0.5, +1) > cell.n_pairs // 2
        cell.tell(0.8, 1)
        assert cell.consume(0.5, -1) < cell.n_pairs // 2

    def test_step_cycles_at_a_small_chain_and_describe_reports_it(self) -> None:
        cell = RateCell(seed=3, chain=INTEGRATED_CHAIN)
        seen = set()
        for _ in range(200):
            cell.step()
            seen.add(cell.describe()["phase"])
        assert seen == {"tell", "hold", "consume"}, seen
        assert cell.describe()["chain"] == INTEGRATED_CHAIN

    def test_reproducible(self) -> None:
        a = RateCell(seed=7, chain=INTEGRATED_CHAIN).tell(0.5, 1)
        b = RateCell(seed=7, chain=INTEGRATED_CHAIN).tell(0.5, 1)
        assert a == b


_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "integrated_rate.py"
_spec = importlib.util.spec_from_file_location("integrated_rate", _PATH)
ir = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ir)

UNITS = 2 * ir.EXACT_PAIRS   # 6 — the width where the decay-test verdict is takeable


class TestIntegrationVerdictScoping:
    def test_the_chain_defaults_are_the_measured_pair(self) -> None:
        """The default is the disintegrated one; INTEGRATED_CHAIN is the value measured integrated."""
        assert CHAIN == 0.0
        assert INTEGRATED_CHAIN == 0.05

    def test_default_chain_is_not_integrated_at_six_units(self) -> None:
        assert ir._integrated(CHAIN, units=UNITS) is False

    def test_integrated_chain_is_integrated_at_six_units(self) -> None:
        assert ir._integrated(INTEGRATED_CHAIN, units=UNITS) is True

    def test_the_verdict_is_the_decay_test_not_the_magnitude(self) -> None:
        """THE SCOPING GUARD: at 6 units the exact directed Phi reads large even for chain-0
        independent pairs (which cannot integrate) — a width-artefact. The verdict is the decay
        test, and it says the default does NOT integrate while the magnitude is large. If the exact
        magnitude ever reads ~0 here, the estimator changed; do not silently delete this."""
        phi0 = ir._exact_phi(CHAIN, units=UNITS, seed=1)
        assert phi0 > 1.0, phi0
        assert ir._integrated(CHAIN, units=UNITS) is False
