"""The context gate survives when the population integrates — measured like-for-like against chain 0.

`context_modulation.py` opened the multiplicative-modulation context window on a DISINTEGRATED
population (chain 0). `integrated_rate.py` found a small chain (0.05) integrates at no measured depth
cost. This pins the re-audit: at chain 0.05 the held past still reaches the current read, and it does
so AT LEAST AS WELL as the matched chain-0 control on the same seeds — coupling does not break the
gate. Two widths, both ODD (coupled.py's parity rule): 5 pairs (10 units), where the phi_proxy decay
test IS a verdict, and 33 pairs (66 units), where the count is wide enough that the full battery
passes but no integration verdict is available.

Guards kept honest:
  - bit-identity with `context_modulation` at chain 0 / N=32 (`default-stays-exact` in spirit: the
    chain thread must not have moved the disintegrated numbers).
  - the exact-Phi magnitude is still an artefact at 6 units (the `integrated_rate.py` guard).

Full battery + nulls live in `state/communication/integrated_context.py` and RESULTS.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent / "state" / "communication"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ic = _load("integrated_context")
cm = ic.cm

VERDICT_UNITS = 2 * ic.VERDICT_PAIRS   # 10
WORK = ic.WIDE_PAIRS                    # 33 pairs
VERDICT = ic.VERDICT_PAIRS             # 5 pairs
WINDOW_SMALL = 0.08                    # window base strength at the verdictable width (RESULTS)
WINDOW_WIDE = 0.08                     # window base strength at the working width (RESULTS)


class TestChainDoesNotMoveTheDisintegratedNumbers:
    def test_past_mean_bit_identical_to_context_modulation_at_chain0_n32(self) -> None:
        """Threading the chain must leave chain-0 / N=32 exactly what context_modulation measured."""
        for a in (0.2, 0.5, 0.8):
            for sign in (+1, -1):
                x = ic._past_mean(a, sign, chain=0.0, n_pairs=cm.N, seed=1234)
                y = cm._past_mean(a, sign, seed=1234)
                assert x == y, (a, sign, x, y)

    def test_mod_read_bit_identical_to_context_modulation_at_chain0_n32(self) -> None:
        for sign in (+1, -1):
            pm = cm._past_mean(0.5, sign, seed=555)
            a = ic._mod_read(0.5, sign, pm, cur_base=0.04, chain=0.0, n_pairs=cm.N, seed=777)
            b = cm._mod_read(0.5, sign, pm, cur_base=0.04, seed=777)
            assert a == b, (sign, a, b)


class TestIntegrationVerdict:
    def test_chain_zero_is_not_integrated_at_the_verdictable_width(self) -> None:
        """The decay/separation test — never the raw magnitude — says independent pairs do not."""
        assert ic._integrated(0.0, units=VERDICT_UNITS) is False

    def test_the_small_chain_integrates_at_the_verdictable_width(self) -> None:
        assert ic._integrated(0.05, units=VERDICT_UNITS) is True

    def test_exact_phi_magnitude_is_still_an_artefact_at_six_units(self) -> None:
        """THE GUARD (from integrated_rate.py): chain-0 independent pairs cannot integrate yet the
        exact directed Phi reads large at 6 units. Do not delete — if it ever reads ~0 the estimator
        changed and the docs' artefact note must be revisited."""
        phi0 = ic._exact_phi(0.0, units=6)
        assert phi0 > 1.0, phi0
        assert ic._integrated(0.0, units=6) is False


class TestContextSurvivesIntegration:
    def test_coupled_arm_reaches_the_read_at_least_as_well_as_the_control_verdictable(self) -> None:
        """The like-for-like question: on the SAME seeds, chain 0.05 must not read the past WORSE
        than chain 0.0. At the verdictable width the coupled arm in fact carries more."""
        obs05, floor05 = ic._mi_depth(ic._trials(WINDOW_SMALL, 0.05, VERDICT), shuffle_seed=23)
        obs00, floor00 = ic._mi_depth(ic._trials(WINDOW_SMALL, 0.0, VERDICT), shuffle_seed=23)
        assert obs05 > floor05 + 0.05, (obs05, floor05)      # window above floor
        assert obs05 >= obs00 - 0.03, (obs05, obs00)          # not worse than the control

    def test_the_full_battery_passes_on_the_coupled_arm_at_the_working_width(self) -> None:
        """At 33 pairs the coupled population passes the whole context battery (window, both signs,
        a_cur=0 collapse, shuffled kill)."""
        b = ic._battery(WORK, 0.05, tag="test")
        assert b["window"], b["sweep"]
        assert b["obs"] > b["floor"] + 0.05, (b["obs"], b["floor"])
        assert b["fid"] >= 0.95, b["fid"]
        assert b["shuffled"] < b["floor"] + 0.02, (b["shuffled"], b["floor"])
        assert b["acur"][0.0][0] <= b["acur"][0.0][1] + 0.05, b["acur"][0.0]   # a_cur=0 collapses
        assert b["obs"] > b["acur"][0.0][0] + 0.1, (b["obs"], b["acur"][0.0])   # past acts THROUGH current

    def test_chain_costs_no_measurable_entering_depth_at_odd_working_width(self) -> None:
        """The direct answer to 'does the chain cost depth at THIS width': at odd 33 pairs, no."""
        e05, _ = ic._entering(0.05, WORK, shuffle_seed=17)
        e00, _ = ic._entering(0.0, WORK, shuffle_seed=17)
        assert abs(e05 - e00) < 0.05, (e00, e05)              # entering depth unchanged by the chain

    def test_the_read_is_history_not_leak(self) -> None:
        """Shuffling the history kills the coupled arm's read (working width)."""
        b = ic._battery(WORK, 0.05, tag="test")
        assert b["shuffled"] < b["obs"] - 0.1, (b["obs"], b["shuffled"])


class TestReproducible:
    def test_deterministic(self) -> None:
        pm = ic._past_mean(0.5, +1, chain=0.05, n_pairs=VERDICT, seed=42)
        a = ic._mod_read(0.5, +1, pm, cur_base=WINDOW_SMALL, chain=0.05, n_pairs=VERDICT, seed=43)
        b = ic._mod_read(0.5, +1, pm, cur_base=WINDOW_SMALL, chain=0.05, n_pairs=VERDICT, seed=43)
        assert a == b
