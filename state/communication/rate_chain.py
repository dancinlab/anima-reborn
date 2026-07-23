"""`RateCell(chain=)` — the parameter, its bit-identical default, and what a small chain costs.

Run from the repo root:

    PYTHONPATH=src python state/communication/rate_chain.py

`integrated_rate.py` measured that the inter-pair `chain` at 0.05 makes a 3-pair (6-unit) PAIRS
population INTEGRATED by the `phi_proxy` decay/separation test — the repo's valid verdict, never the
raw exact-Phi magnitude, which is a width-artefact there — while chain 0 is NOT integrated, and that
the held-depth margin over its shuffled floor does not measurably drop (0.240 disintegrated ->
0.268 integrated). So `rate.py`'s hardcoded chain 0 was a CHOICE. It is now a parameter, and this
measures the shipped engine with it (`state/CLAUDE.md`: a script here drives the engine, not a copy).

Three things are measured, all on `anima_reborn.rate.RateCell` itself:

[0] `default-stays-exact` — at the default `chain=CHAIN` (0.0) the cell is BIT-identical to the
    behaviour every published number was taken on: tell()/consume() outputs and a run of step()
    frames hash to fixtures captured from the pre-parameter code. `tests/test_rate_chain.py` pins
    the same fixtures; this script re-derives them.

[1] the two claims the cell exists for, re-measured at chain 0.05 with their own nulls:
    HOLD    — I(a_past ; held count | past sign) vs its within-sign shuffled floor (rate_code's
              control: a sign-only lookup scores exactly the floor).
    CONSUME — a FIXED current symbol (CUR_DEPTH), written under both current signs, with
              I(a_past ; current count | current sign) vs the same shuffled floor, plus the
              fidelity that both current signs survive the gain (the gain is positive by
              construction, so this must stay 1.000 — it is the guard, not the finding).

[2] the integration verdict, imported from `integrated_rate.py` so it is the same test: chain 0 is
    not integrated, chain 0.05 is, at 6 units. The exact directed Phi is printed BESIDE it and
    labelled an artefact (chain-0 independent pairs, which cannot integrate, still read ~5).

`report-the-rank`: the held count spans 0..N and the MI is reported in bits beside the number of
DISTINCT count values each arm actually visits — a depth code that visits two values carries a sign,
not depth, whatever the MI says.

Honest ceiling, and the reason the viewer says so too: the integration verdict is measured at 3
pairs / 6 units. At the cell's default 32 pairs the `phi_proxy` floor is not trustworthy
(`coupled.py`/`phi_proxy.py`), so a WIDE cell run at chain 0.05 is NOT thereby measured integrated —
it is running the value that measured integrated at a width where the verdict can be taken. Not
language, not a capability claim: a parameter, its default's bit-identity, and what the option costs.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from anima_reborn.rate import CHAIN, CUR_DEPTH, INTEGRATED_CHAIN, RateCell

_HERE = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rc = _load("rate_code")
ir = _load("integrated_rate")

AMPS = rc.AMPS
SIGNS = (1, -1)
TRIALS = 40
CHAINS = (0.0, INTEGRATED_CHAIN)
EXACT_UNITS = 2 * ir.EXACT_PAIRS   # 6 — where the decay-test verdict is takeable
REPLICATE_BASES = (60_000, 70_000, 80_000)   # independent seed bases for the margin spread

FIXTURE_FRAME_DIGEST ="78f81eb5c2276abbb58981bf450e8c2bc7eb3e0e43d009300bf977d9bf389579"
"""sha256 of 120 `step()` frames of `RateCell(seed=3)`, minus the new `chain` readout, captured from
the CURRENT (chain-0, pre-parameter) code before the parameter was added."""


def _tell_values() -> list[float]:
    return [RateCell(seed=seed).tell(d, s)
            for seed in range(4) for d in (0.2, 0.5, 0.8) for s in (1, -1)]


def _consume_values() -> list[int]:
    out: list[int] = []
    for seed in range(4):
        for d in (0.2, 0.5, 0.8):
            cell = RateCell(seed=seed)
            cell.tell(d, 1)
            out.append(cell.consume(0.5, 1))
            cell.tell(d, 1)
            out.append(cell.consume(0.5, -1))
    return out


def _frame_digest() -> str:
    """Frames minus the `chain` key — the key is new, the DYNAMICS are what must not have moved."""
    cell = RateCell(seed=3)
    frames = []
    for _ in range(120):
        cell.step()
        frames.append({k: v for k, v in cell.describe().items() if k != "chain"})
    return hashlib.sha256(json.dumps(frames, sort_keys=True).encode()).hexdigest()


def _hold(chain: float, *, shuffle_seed: int, base: int = 9_000) -> tuple[float, float, list[float], int]:
    """I(a_past ; held count | past sign), its shuffled floor, the per-depth mean rate at sign +,
    and how many distinct counts the + arm visits (`report-the-rank`)."""
    by_sign: dict[int, list[tuple[int, float]]] = {}
    per_depth: dict[int, list[float]] = {}
    seen: set[int] = set()
    k = 0
    for ai, a in enumerate(AMPS):
        for sign in SIGNS:
            for _ in range(TRIALS):
                cell = RateCell(chain=chain, seed=base + k)
                rate = cell.tell(a, sign)
                count = round(rate * cell.n_pairs)
                by_sign.setdefault(sign, []).append((ai, float(count)))
                if sign > 0:
                    per_depth.setdefault(ai, []).append(rate)
                    seen.add(count)
                k += 1
    obs, floor = rc._cond_depth(by_sign, shuffle_seed=shuffle_seed)
    means = [sum(per_depth[ai]) / len(per_depth[ai]) for ai in range(len(AMPS))]
    return obs, floor, means, len(seen)


def _consume(chain: float, *, shuffle_seed: int, base: int = 21_000) -> tuple[float, float, list[float], float, int]:
    """A FIXED current symbol under both signs: I(a_past ; current count | current sign), its
    shuffled floor, the per-depth mean count at current sign +, the two-sign fidelity, and the
    distinct-count width of the + arm."""
    by_sign: dict[int, list[tuple[int, float]]] = {}
    per_depth: dict[int, list[int]] = {}
    seen: set[int] = set()
    hits = 0
    total = 0
    k = 0
    for ai, a in enumerate(AMPS):
        for cur_sign in SIGNS:
            for _ in range(TRIALS):
                cell = RateCell(chain=chain, seed=base + k)
                cell.tell(a, 1)                       # past sign fixed +, as context_modulation.py
                count = cell.consume(CUR_DEPTH, cur_sign)
                by_sign.setdefault(cur_sign, []).append((ai, float(count)))
                up = count > cell.n_pairs / 2
                hits += int(up == (cur_sign > 0))
                total += 1
                if cur_sign > 0:
                    per_depth.setdefault(ai, []).append(count)
                    seen.add(count)
                k += 1
    obs, floor = rc._cond_depth(by_sign, shuffle_seed=shuffle_seed)
    means = [sum(per_depth[ai]) / len(per_depth[ai]) for ai in range(len(AMPS))]
    return obs, floor, means, hits / total, len(seen)


def main() -> None:
    print("RateCell(chain=) — the parameter, its bit-identical default, and the option's cost\n")

    print("[0] default-stays-exact — the default must be BIT-identical to the pre-parameter cell")
    tells = _tell_values()
    cons = _consume_values()
    frames = _frame_digest()
    print(f"    default chain                    = {CHAIN}")
    print(f"    tell() over 4 seeds x 3 depths x 2 signs = {[round(t, 5) for t in tells[:6]]} ...")
    print(f"    consume() over the same grid             = {cons[:6]} ...")
    print(f"    sha256(120 step() frames, minus `chain`) = {frames}")
    print(f"    matches the pre-parameter fixture        = {frames == FIXTURE_FRAME_DIGEST}")
    print("    (tests/test_rate_chain.py pins the tell/consume values elementwise)\n")

    print(f"[1] hold and consume at each chain — N = {RateCell().n_pairs} pairs, "
          f"{TRIALS} trials per (a_past, sign)")
    print(f"    current symbol FIXED at depth {CUR_DEPTH}, written under both signs\n")
    print(f"{'chain':>7}{'hold I(a;count|sign)':>22}{'floor':>8}{'margin':>8}"
          f"{'rate levels':>13}{'held rate by a_past':>34}")
    print("  " + "-" * 90)
    for ci, chain in enumerate(CHAINS):
        obs, floor, means, levels = _hold(chain, shuffle_seed=101 + ci)
        pretty = " ".join(f"{m:.2f}" for m in means)
        print(f"{chain:>7.2f}{obs:>22.3f}{floor:>8.3f}{obs - floor:>8.3f}"
              f"{levels:>13}   {pretty:>31}")

    print()
    print(f"{'chain':>7}{'consume I(a_past;read|sign)':>28}{'floor':>8}{'margin':>8}"
          f"{'fidelity':>10}{'levels':>8}{'read by a_past (sign +)':>32}")
    print("  " + "-" * 101)
    for ci, chain in enumerate(CHAINS):
        obs, floor, means, fid, levels = _consume(chain, shuffle_seed=201 + ci)
        pretty = " ".join(f"{m:.1f}" for m in means)
        print(f"{chain:>7.2f}{obs:>28.3f}{floor:>8.3f}{obs - floor:>8.3f}"
              f"{fid:>10.3f}{levels:>8}   {pretty:>29}")

    print(f"\n[1b] {len(REPLICATE_BASES)} independent seed-base replicates of the same two margins —")
    print("     so a chain-to-chain difference is read against the spread, not off one sweep")
    print(f"{'chain':>7}{'hold margins':>34}{'consume margins':>34}")
    print("  " + "-" * 74)
    for ci, chain in enumerate(CHAINS):
        holds, cons_m = [], []
        for ri, base in enumerate(REPLICATE_BASES):
            h_obs, h_floor, _, _ = _hold(chain, shuffle_seed=301 + 10 * ci + ri, base=base)
            c_obs, c_floor, _, _, _ = _consume(chain, shuffle_seed=401 + 10 * ci + ri,
                                               base=base + 5_000)
            holds.append(h_obs - h_floor)
            cons_m.append(c_obs - c_floor)
        hp = " ".join(f"{m:.3f}" for m in holds)
        cp = " ".join(f"{m:.3f}" for m in cons_m)
        print(f"{chain:>7.2f}{hp:>34}{cp:>34}")

    print(f"\n[2] the integration verdict — imported from integrated_rate.py, "
          f"{EXACT_UNITS} units ({ir.EXACT_PAIRS} pairs)")
    print(f"{'chain':>7}{'integrated (decay test)':>25}{'exact Phi (ARTEFACT)':>22}")
    print("  " + "-" * 54)
    for chain in CHAINS:
        integ = ir._integrated(chain, units=EXACT_UNITS)
        phi = ir._exact_phi(chain, units=EXACT_UNITS, seed=1)
        print(f"{chain:>7.2f}{('yes' if integ else 'no'):>25}{phi:>22.3f}")
    print("    the magnitude column is shown ONLY to expose the artefact: chain-0 independent pairs")
    print("    cannot integrate and still read large. The decay test is the verdict.")

    print("\n  VERDICT:")
    print("  `chain=` is a parameter with a bit-identical default. At chain 0.05 the cell still")
    print("  HOLDS the past depth (margin above its shuffled floor) and still CONSUMES it (a fixed")
    print("  current symbol reads by the held past, both current signs surviving), and 0.05 is the")
    print("  value that measures INTEGRATED at 6 units where the verdict can be taken.")
    print("  NOT claimed: that this 32-pair cell is integrated (the proxy floor is untrustworthy at")
    print("  that width) · that chain 0.05 improves anything · integration from a Phi magnitude.")


if __name__ == "__main__":
    main()
