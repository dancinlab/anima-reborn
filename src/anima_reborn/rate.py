"""A population rate cell — the engine part the `state/communication/` line measured into being.

The `기억` chain (`sequence.py`) holds a symbol's SIGN. This holds its analog DEPTH, and lets a
later symbol be modulated by it — the two things a single bistable latch cannot do at once, shown
across four measurements and their nulls:

- `state/communication/rate_code.py`: a population of N near-barrier PAIRS latches transduces an
  input's analog depth into a COUNT at write time (magnitude -> sign statistics, which the basin
  preserves), so the held count is a STABLE analog value where a single latch keeps only the sign
  (I(a; count | sign) = 0.98 bits, flat through 480 deaf ticks; the single latch reads 0.000).
- `state/communication/context_modulation.py`: a SECOND population's current write, MULTIPLIED by a
  positive gain derived from the held count, reads differently by the held past while keeping its
  own sign (the gain never flips it) — context that additive gating could not deliver
  (I(a_past; read | sign) = 0.275 above floor, both current signs surviving, and with no current
  symbol the past collapses to floor: it acts THROUGH the current, genuine modulation).
- `state/communication/context_synergy.py`: that composition is super-additive (interaction
  information 0.168 > floor), honestly larger than — not against a clean zero of — the additive gate.

This engine is that mechanism, live: it cycles TELL (write a past depth into the population) ->
HOLD (the count holds the depth through silence) -> CONSUME (a fixed current symbol, multiplied by
the held count, reads differently by the held past). It DRIVES `CoupledEngine`, adds no new physics,
and is the reproducible half made watchable — the numbers still live in `state/`, measured there.

Not language, and at the DEFAULT not integration: `chain=0.0` leaves the latches independent, so Phi
factorizes across the pairs and this buys held depth and usable context, not Phi. That default is a
CHOICE rather than a necessity, and the choice was measured — `state/communication/integrated_rate.py`
sweeps the inter-pair `chain` on a Phi-measurable 3-pair population and finds the two are NOT
exclusive: chain 0 is not integrated (the `phi_proxy` decay/separation test, never the raw exact-Phi
magnitude, which is a width-artefact there), while chain 0.05 IS integrated with the held-depth
margin over its shuffled floor 0.268 vs chain 0's 0.240 — no measured depth cost. A larger chain does
trade it away (0.20 -> margin 0.040). So `chain=` is exposed: the cell CAN integrate at a small chain
at no measured depth cost, while the default stays bit-identical to every published measurement.
Bounded by the population width either way (a fraction of a bit of past per read).
"""

from __future__ import annotations

import random
from typing import Any

from .coupled import ALTERNATING, FIXED, AMPLITUDE, CoupledEngine, Wiring

__all__ = ["RateCell", "PAIRS_N", "PAST_DEPTHS", "CHAIN", "INTEGRATED_CHAIN"]

PAIRS_N = 32
"""Latches in the population — the count lives in 0..N. Width buys the coexistence a single latch
cannot have: `rate_code.py`'s N=1 row has neither retention nor depth, N=32 has both."""

WRITE_SCALE = 0.08
"""Near-barrier write scale for the PAST population — the graded regime where the count tracks the
input depth (rate_code.py's chosen scale; stronger writes saturate to all-up and carry no depth)."""

GAIN_BASE = 0.5
"""Positive floor of the consume gain, so the current symbol always has a sign of its own."""

GAIN_K = 1.0
"""Past-depth -> gain slope: how strongly the held count modulates the current write."""

CUR_BASE = 0.04
"""Base current write strength — the window (context_modulation.py) where the past reaches the read
AND both current signs survive."""

CUR_DEPTH = 0.5
"""The current symbol is held FIXED so the viewer shows it reading differently by the held PAST —
the context effect, isolated."""

PAST_DEPTHS = (0.2, 0.5, 0.8)
"""The past depths cycled, low to high, so the held rate visibly rises with the input."""

CHAIN = 0.0
"""Default inter-pair coupling: 0.0 = independent latches, NOT integrated. `default-stays-exact` —
every number published for this cell was measured here. `INTEGRATED_CHAIN` is the measured
alternative."""

INTEGRATED_CHAIN = 0.05
"""The chain `state/communication/integrated_rate.py` measured as integrated (phi_proxy decay test,
3 pairs / 6 units) at no measured held-depth cost. Not the default — offered as the option."""

TELL_TICKS = 192      # internal engine ticks to write the past population (~ the measured TELL)
HOLD_TICKS = 96       # deaf hold — the count sits still, the analog memory
CONSUME_TICKS = 120   # the modulated current write settles
STRIDE = 8            # internal engine ticks advanced per RateCell.step (frames stay ~8 Hz)

_PHASES = ("tell", "hold", "consume")
_DURATIONS = {"tell": TELL_TICKS, "hold": HOLD_TICKS, "consume": CONSUME_TICKS}


def _count_up(values: tuple[float, ...], n_pairs: int) -> int:
    return sum(1 for i in range(n_pairs) if (values[2 * i] - values[2 * i + 1]) > 0)


def _mean_delta(values: tuple[float, ...], n_pairs: int) -> float:
    return sum(values[2 * i] - values[2 * i + 1] for i in range(n_pairs)) / n_pairs


class RateCell:
    """A hold-and-consume analog register. A passive viewer engine: `step()` advances the current
    phase, cycling TELL -> HOLD -> CONSUME; `reset()` starts fresh. `tell()` / `consume()` are the
    units the `state/` measurements drive directly (a script measures the shipped engine).

    `chain=` is the inter-pair coupling handed to every population this cell builds. It defaults to
    `CHAIN` (0.0 — independent latches, not integrated), which keeps the cell bit-identical to the
    behaviour every published number was measured on. `INTEGRATED_CHAIN` (0.05) is the value
    `state/communication/integrated_rate.py` measured as integrated by the phi_proxy decay test at 3
    pairs / 6 units, with no measured held-depth cost. That verdict is scoped to that width: at this
    cell's default 32 pairs the proxy floor is not trustworthy, so a wide cell running chain 0.05 is
    NOT thereby measured integrated."""

    def __init__(self, *, n_pairs: int = PAIRS_N, chain: float = CHAIN,
                 seed: int | None = None) -> None:
        self.n_pairs = int(n_pairs)
        self.chain = float(chain)
        if not 0.0 <= self.chain <= 1.0:
            raise ValueError(f"chain must be in [0, 1], got {chain}")
        self._seed = 0 if seed is None else int(seed)
        self.reset()

    def reset(self) -> None:
        self._rng = random.Random(self._seed)
        self._op = 0
        self._phase = "tell"
        self._clock = 0            # internal ticks elapsed in the current phase
        self._depth_idx = 0
        self._cycles = 0
        self._history: list[dict[str, Any]] = []   # recent (past_depth, cur_count) — the context
        self._held_rate: float | None = None       # the count captured at end of HOLD
        self._held_mean: float | None = None
        self._cur: CoupledEngine | None = None
        self._cur_count: int | None = None
        self._past_depth = PAST_DEPTHS[0]
        self._past_sign = 1
        self._pop = self._fresh_population(self._past_depth, self._past_sign)

    # -- the mechanism the measurements drive ------------------------------------------

    def _fresh_population(self, depth: float, sign: int) -> CoupledEngine:
        """N near-barrier latches told the signed depth. Random initials are the per-latch spread
        that makes which basin each falls into graded in the depth (rate_code.py)."""
        self._op += 1
        d = WRITE_SCALE * depth * sign
        return CoupledEngine(
            units=2 * self.n_pairs, wiring=Wiring.PAIRS, chain=self.chain, rhythm=ALTERNATING,
            drive=(d, -d) * self.n_pairs, seed=self._seed * 100_003 + self._op,
        )

    def tell(self, depth: float, sign: int) -> float:
        """Write a past depth into a fresh population and hold it deaf; return the held rate
        (count / N) — the analog memory. This is exactly what `rate_code.py` measures."""
        pop = self._fresh_population(depth, sign)
        pop.run(TELL_TICKS)
        pop.rhythm = FIXED
        pop.drive = 0.0
        pop.run(HOLD_TICKS)
        self._pop = pop
        self._held_mean = _mean_delta(pop.values, self.n_pairs)
        self._held_rate = _count_up(pop.values, self.n_pairs) / self.n_pairs
        return self._held_rate

    def consume(self, depth: float, sign: int) -> int:
        """Write a current symbol MULTIPLIED by a positive gain from the held count; return its
        up-count. The gain never flips the sign, so the current symbol survives while the held past
        modulates the read (context_modulation.py)."""
        if self._held_mean is None:
            raise ValueError("consume before tell — nothing is held")
        self._op += 1
        gain = GAIN_BASE + GAIN_K * abs(self._held_mean)
        d = CUR_BASE * depth * sign * gain
        cur = CoupledEngine(
            units=2 * self.n_pairs, wiring=Wiring.PAIRS, chain=self.chain, rhythm=ALTERNATING,
            drive=(d, -d) * self.n_pairs, seed=self._seed * 100_003 + self._op,
        )
        cur.run(TELL_TICKS)
        cur.rhythm = FIXED
        cur.drive = 0.0
        cur.run(HOLD_TICKS)
        self._cur = cur
        self._cur_count = _count_up(cur.values, self.n_pairs)
        return self._cur_count

    # -- viewer engine contract --------------------------------------------------------

    def step(self) -> "RateCell":
        """Advance the current phase by STRIDE internal ticks; roll to the next phase at its end."""
        phase = self._phase
        remaining = STRIDE
        if phase == "tell":
            self._pop.rhythm = ALTERNATING
            self._pop.drive = (WRITE_SCALE * self._past_depth * self._past_sign,
                               -WRITE_SCALE * self._past_depth * self._past_sign) * self.n_pairs
            self._pop.run(remaining)
        elif phase == "hold":
            self._pop.rhythm = FIXED
            self._pop.drive = 0.0
            self._pop.run(remaining)
        else:  # consume
            if self._cur is not None:
                self._cur.rhythm = FIXED
                self._cur.drive = 0.0
                self._cur.run(remaining)
        self._clock += remaining
        if self._clock >= _DURATIONS[phase]:
            self._advance_phase()
        return self

    def _advance_phase(self) -> None:
        phase = self._phase
        if phase == "tell":
            self._phase = "hold"
        elif phase == "hold":
            # freeze the held analog value, then build the modulated current write
            self._held_mean = _mean_delta(self._pop.values, self.n_pairs)
            self._held_rate = _count_up(self._pop.values, self.n_pairs) / self.n_pairs
            gain = GAIN_BASE + GAIN_K * abs(self._held_mean)
            self._op += 1
            d = CUR_BASE * CUR_DEPTH * 1 * gain
            self._cur = CoupledEngine(
                units=2 * self.n_pairs, wiring=Wiring.PAIRS, chain=self.chain, rhythm=ALTERNATING,
                drive=(d, -d) * self.n_pairs, seed=self._seed * 100_003 + self._op,
            )
            self._cur.run(TELL_TICKS)  # settle the current write once, then hold-read live
            self._phase = "consume"
        else:  # consume -> record and pick the next past depth
            self._cur_count = _count_up(self._cur.values, self.n_pairs)
            self._history.append({"past_depth": self._past_depth, "cur_count": self._cur_count})
            self._history = self._history[-len(PAST_DEPTHS) * 3:]
            self._cycles += 1
            self._depth_idx = (self._depth_idx + 1) % len(PAST_DEPTHS)
            self._past_depth = PAST_DEPTHS[self._depth_idx]
            self._past_sign = 1
            self._held_rate = None
            self._held_mean = None
            self._cur = None
            self._cur_count = None
            self._pop = self._fresh_population(self._past_depth, self._past_sign)
            self._phase = "tell"
        self._clock = 0

    def _signs(self, engine: CoupledEngine | None) -> list[int]:
        if engine is None:
            return []
        v = engine.values
        return [1 if (v[2 * i] - v[2 * i + 1]) > 0 else 0 for i in range(self.n_pairs)]

    def describe(self) -> dict[str, Any]:
        pop_signs = self._signs(self._pop)
        count = sum(pop_signs)
        return {
            "phase": self._phase,
            "n_pairs": self.n_pairs,
            "chain": round(self.chain, 4),
            "past_depth": round(self._past_depth, 3),
            "past_sign": self._past_sign,
            "cur_depth": CUR_DEPTH,
            "population": pop_signs,
            "count": count,
            "rate": round(count / self.n_pairs, 4),
            "held_rate": None if self._held_rate is None else round(self._held_rate, 4),
            "current": self._signs(self._cur),
            "cur_count": self._cur_count,
            "history": list(self._history),
            "past_levels": list(PAST_DEPTHS),
            "cycles": self._cycles,
            "progress": round(self._clock / _DURATIONS[self._phase], 3),
            "amplitude": round(AMPLITUDE, 4),
        }
