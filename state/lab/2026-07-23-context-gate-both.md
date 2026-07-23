<!-- sidecar lab full · model=(default) · cwd=/Users/mini/dancinlab/anima-reborn · prompt=5363 chars · 2026-07-23T10:22:51.098Z -->

── fable (claude-fable-5) · exit 0 ──
설계를 마쳤습니다. 프롬프트와 보고서를 관례대로 저장했고(`state/lab/2026-07-23-context-gate-prompt.md` · `-fable.md`), 핵심 결정은 이것입니다: **게이트는 규칙이 아니라 히스테리시스입니다.** 이전 스케치("다리의 부호/게이트를 이전 셀 상태가 변조")를 그대로 구현하면 변조 규칙 자체가 설계자의 룩업이 될 위험이 있어서, 변조를 버리고 `retention.py`가 이미 측정해 둔 분지 장벽을 재사용하는 쪽으로 날카롭게 다듬었습니다. 다섯 질문에 답합니다.

## 1. 메커니즘 — 원점 쓰기를 장벽 근처의 이력-시작 쓰기로

현행 `turn()`은 셀 0을 `initial=(0,)*6`, 진폭 ±0.8로 **원점에서** 덮어씁니다 — 과거가 쓰기에 작용할 물리적 경로가 없습니다. 추가하는 것은 `SequenceEngine(context: float = 0.0)` 하나:

- `context=0`(기본): 기존 코드 경로 그대로 — 비트 동일, 시드×턴 격자의 tape 전체 일치로 핀 (`default-stays-exact`).
- `context>0`: 덮어쓰기 직전 셀 0의 **아날로그 보유값**을 캡처해 `initial=prev_values`, `amplitude=0.8*(1-context)`로 씁니다. 이행은 `dialogue.channel_trace`에 defaulted kwargs(`initial=None, amplitude=0.8`) 추가 — 기본 경로는 기존 test_dialogue 핀이 그대로 지킵니다.

왜 `if`가 아닌가: 진폭이 장벽 영역에 있으면, 현재 비트가 과거와 일치하는 쌍은 앉아 있는 분지가 드라이브로 강화되어 유지되고, 불일치 쌍은 장벽을 넘어야 하며 성공은 진폭·분지 깊이·그 시행의 WALK 노이즈의 함수입니다. 문맥은 코드 분기가 아니라 **장벽 통과 확률**에 삽니다. 게이트가 닿는 과거는 정확히 한 턴뿐임을 명시합니다.

## 2. 시너지 측정

read는 모호성 없이: r_t = `turn(s_t)` 직후 `tape()[0]` — 표준 HOLD를 거친 셀 0의 차동 부호 디코드 word. 양은 상호작용정보 **II = I(r; s_t, s_{t-1}) − I(r;s_t) − I(r;s_{t-1})**, 정확 범주형 plug-in + 측정된 셔플 플로어(`accumulation.py`의 `_floor` 관례). 비트별(2×2×2, 주 신호 — 게이트가 쌍별로 작용하므로)과 word-레벨(8×8×8, 큰 플로어 동반)을 모두, 교차-비트 II(~플로어여야 함)와 유효 폭 2^H(r)을 옆에 붙여서(`report-the-rank`). 해석적 예측(측정 아님): 히스테리시스 채널의 II는 순수 덮어쓰기와 순수 복사 양 극단에서 정확히 0, 중간에서 양수(p=0.5 이론값 ~+0.12 bits/bit) — **II(context)의 역U 곡선 자체가 반증 가능한 시그니처**라 곡선 전체를 잽니다.

## 3. 널 배터리 — 그리고 함정의 정확한 이름

함정부터: **II는 필요조건이지 충분조건이 아닙니다.** 순수 복사는 II=0으로 자동 사망하지만(측정의 성질), 설계자가 `r = cur XOR past`를 배선한 룩업은 II=+1로 만점을 받습니다 — D7의 재림이 정확히 이 모양. 그래서 라우팅 통제가 하중을 집니다.

| 통제 | 죽이는 가짜 |
|---|---|
| (a) 셔플 이력 | 추정기 편향의 유령 시너지 — 플로어 측정 |
| (b) 게이트 오프(context=0) | 게이트가 아닌 곳에서 온 II — 문맥은 게이트가 산 것 |
| (c) 귀머거리 게이트(진폭 감소 유지, `initial`만 원점) | 진폭 변화 단독 효과 — 시너지가 보유 상태를 **경유**함의 증명 |
| (d) 룩업 대조 팔(복사·XOR 파이썬 함수) | II 단독의 불충분성을 수치로 시연(복사 0, XOR +1) |
| (e) **섭동 라우팅** — 홀드 중 쌍 j를 반대 분지로 jolt 후 쓰기 | 심볼-로그 레벨의 모든 결정론적 룩업, XOR 포함 — 효과는 jolt된 물리 상태를 따라가야 하고 룩업은 로그를 따라감. 정량: I(r_j; jolt후 부호\|s_t) ≫ 플로어, I(r_j; 명목 s_{t-1}\|s_t, 보유부호) ≈ 플로어 |
| (f) 깊이 그라데이션(직전 홀드 길이 변화) | 깊이를 못 보는 word-레벨 룩업 — 플립 확률이 아날로그 깊이에 연속 반응해야 |

프롬프트의 "새 랜덤 심볼" 통제는 (a)+시행마다 iid 신선 심볼로 이행됩니다 — 엔진에 학습이 없으므로 '외운 규칙'의 실체는 설계자 배선이고, 그것을 죽이는 것이 (e)입니다.

## 4. 평결과 천장

얻는 문장: "게이트 강도 c*에서 최신 셀의 읽기는 현재 심볼과 엔진이 보유하던 직전 상태에 공동으로 의존했다 — II +X bits(셔플 플로어 대비), 게이트 오프·귀머거리 게이트에서 소멸, 섭동 시 효과가 심볼 로그가 아니라 물리 상태를 따라감." 금지: "문맥을 이해한다" · "합성 의미" · "용량 증가". 천장의 정확한 위치: **시너지는 같은 3비트 예산에서 나옵니다** — II가 양수가 되는 만큼 현재 충실도 I(r;s_t)가 깎이며, 이 트레이드(문맥의 가격)를 표로 보고합니다. 선은 '사용되는 워킹 메모리'까지이고, 조합적 공간 위의 체계성(지시·통사)은 이 기판에 없으므로 주장하지 않습니다.

## 5. 단계 커밋

- **커밋 1 (측정만, src 무변경):** `state/communication/context_gate.py` — phase 0은 반대 분지에서 시작한 쌍의 P(flip | amplitude) 덮어쓰기 곡선(raw `CoupledEngine`, `retention.py`가 `sequence.py`에 앞섰던 전례). **장벽 창이 없으면(노이즈 폭 안에서 0/1 스텝형) 정직한 결과는 "복사 너머 시너지 없음 — 프루닝"이고 거기서 멈춥니다.** 창이 있으면 같은 스크립트가 II(context) 곡선 + 널 (a)–(f)를 측정, RESULTS.md에 조건과 함께 기록.
- **커밋 2:** `sequence.py`의 `context=` + `channel_trace` kwargs + 비트동일 핀 + 스크립트를 shipped 엔진 구동으로 전환 + 게이트 켬 망각 곡선 재측정 + `기억` 탭 뷰어 확장(`viewer-lockstep` 같은 커밋).
- **유예:** `conversation.py`의 다중 턴 기억-대화 게임(블라인드 동결 감사 — sol의 경계대로 수신자 기록 누적을 엔진 기억으로 셈하지 않음), 한 턴 초과 문맥, 계층과의 결합.

보고서 전문은 `state/lab/2026-07-23-context-gate-fable.md`에 있습니다. 커밋은 하지 않았습니다.

── sol (gpt-5.6-sol) · exit 0 ──
OpenAI Codex v0.144.6
--------
workdir: /Users/mini/dancinlab/anima-reborn
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f8e78-c326-7d91-9a1e-26ada736ce91
--------
user
# Design task: conditional composition — the held past ACTS on the current write, measured honestly

Part 4 of the "engine parts toward the goal" plan (both of you converged last round;
`state/lab/2026-07-23-new-parts-*.md`). Parts 1-2 landed: `src/anima_reborn/sequence.py` — a
shift chain of K proven 3-bit cells that holds the last K symbols IN ORDER (memory), measured
in `state/communication/accumulation.py`; and `state/communication/phi_proxy.py` — a validated
sampled directed-Φ proxy that moved the integration-measurability wall 6 → 10 units.

But the shift chain is a RECORDER: it holds, it does not USE the past. Both of you named the
next honest step toward language: **the held past must ACT on the current write** — context.
Design that component + the measurement that proves it is real, not planted. Return a concrete
architecture + validation protocol. Do NOT write full code.

## What exists (read it)

- `src/anima_reborn/sequence.py`: `SequenceEngine`, K=4 cells (6-unit `Wiring.PAIRS`, chain=0.2),
  each holds 3 bits deaf. `turn(symbol)` shifts every held word one cell down (via a clean
  `dialogue.channel(bits=3)` bridge) then writes the new symbol to cell 0. `tape()` reads all K.
- `state/communication/accumulation.py` measured: 12 bits held in order, deaf-bridge / time-shift
  / cross-cell / perturbation nulls all pass; the bridge is a TRANSPORT claim, never integration.
- `state/communication/retention.py`: the deaf-hold is a self-correcting basin (small jolt
  recovers, large jolt crosses a finite barrier), so the state lives in the engine's DYNAMICS,
  not a Python variable.
- `src/anima_reborn/coupled.py`: `CoupledEngine`, per-unit `drive` (a vector), `chain`, `Rhythm`.

## Your own prior sketches (reconcile and sharpen these)

- fable: "the bridge's sign/gate is MODULATED by the previous cell's differential state. Measure
  SYNERGY — the amount I(read; s_t, s_{t-1}) exceeds the sum of the individual MIs — null =
  shuffled history."
- sol: a `ContextGate` — genuine but BOUNDED temporal state; the receiver's transcript may
  accumulate info but the engine must not thereby be credited with sequence memory; free play is
  descriptive only, evidence comes from a blind frozen audit.

## The trap you must both name and kill

History-dependence is trivial to FAKE: if the "context effect" is just the bridge deterministically
copying the previous cell (a rule the designer wired in), that is not the engine composing — it is
the designer's lookup table. The D7 death (`attractor_canonicalization.py`) is the ancestor: a
planted structure that scores. The control must isolate GENUINE synergy (the whole read depends on
the pair (current, past) BEYOND what each contributes alone AND beyond a deterministic copy) from
a planted rule, with a shuffled-history null and a "no-gate" baseline.

## What I need — answer each explicitly

1. **The mechanism.** The smallest honest way the held past acts on the current write, added to
   `sequence.py` (or a sibling), stdlib + seedable + `engine-purity`. Exactly what modulates what:
   does the previous cell's held differential bias the current cell's drive/gate? Keep it a DYNAMICAL
   coupling (measurable), not a Python `if`. `default-stays-exact`: it must default OFF, leaving
   `SequenceEngine` bit-identical, pinned by a test.
2. **The measurement of synergy.** The exact quantity: interaction information / synergy
   I(read ; current, past) − I(read;current) − I(read;past), or a co-information, computed with
   exact categorical MI (not `info.py`'s binning) over sampled reads. What is "read" here — a held
   cell, a probe response? State it so it is unambiguous.
3. **The nulls (the load-bearing part).** At minimum: (a) shuffled-history — pair each read with a
   RANDOM past instead of its true past, synergy must vanish; (b) no-gate baseline — the same engine
   with the gate off, synergy ~0 (context is what the gate buys, `channel-before-carrier`); (c) the
   deterministic-copy control — show the synergy is not reproducible by a fixed lookup (e.g. the
   gate's effect survives when the past is a NEW random symbol the engine could not have memorized a
   rule for). Give the exact null battery and what each kills.
4. **The honest verdict + ceiling.** The sentence it earns and the sentence it must NOT. Even with
   context, I(X;Y) ≤ 3 bits per moment stays bound; the claim is "the current exchange depended on
   the held past, by measured synergy above its shuffled-history null" — working memory that is
   USED, not language. Where exactly is the line?
5. **The phased first commit.** Smallest honest thing: a pure `state/` measurement (a sibling of
   `accumulation.py`) driving `SequenceEngine` with the gate, filling RESULTS from the run — matching
   how every part here landed — with the `src/` gate parameter + a viewer readout following. What is
   deferred (e.g. the multi-turn working-memory conversation game in `conversation.py`)?

Keep the discipline: never a number that was not measured; every capability with the null that could
fake it; report effective rank/width beside any synergy; the engine is not language — the gain is
CONTEXT (current depends on held past), earned by synergy over a shuffled-history null, nothing more.
If the honest result is "the gate adds no measurable synergy beyond the copy," say so and prune it.

codex
I’ll inspect the landed sequence/retention/measurement code and both prior design notes, then pin the proposal to the actual engine interfaces and measurement conventions. I’ll keep all thresholds and expected outcomes as preregistered criteria, not invented results.
  → Inspect current engine, measurements, tests, and prior Part 4 sketches
  • Design the minimal default-off dynamical context coupling
  • Specify exact synergy estimator and load-bearing null battery
  • Define earned claim, ceiling, and phased first commit
exec
/bin/zsh -lc "pwd && rg --files src/anima_reborn state | rg '(sequence|coupled|accumulation|retention|phi_proxy|2026-07-23-new-parts|conversation|attractor_canonicalization|info\\.py)'" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
/Users/mini/dancinlab/anima-reborn
src/anima_reborn/coupled.py
src/anima_reborn/info.py
state/communication/attractor_canonicalization.py
state/communication/retention.py
state/communication/phi_proxy.py
state/communication/conversation_channel.py
state/communication/accumulation.py
src/anima_reborn/sequence.py
src/anima_reborn/conversation.py
state/lab/2026-07-23-conversation-both.md
state/lab/2026-07-23-new-parts-both.md
state/lab/2026-07-23-new-parts-prompt.md
state/lab/2026-07-23-conversation-prompt.md

exec
/bin/zsh -lc "wc -l src/anima_reborn/sequence.py src/anima_reborn/coupled.py src/anima_reborn/info.py state/communication/accumulation.py state/communication/retention.py state/communication/attractor_canonicalization.py state/lab/2026-07-23-new-parts-both.md && sed -n '1,260p' src/anima_reborn/sequence.py && sed -n '1,260p' src/anima_reborn/coupled.py && sed -n '1,240p' state/lab/2026-07-23-new-parts-both.md" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
     116 src/anima_reborn/sequence.py
     506 src/anima_reborn/coupled.py
     135 src/anima_reborn/info.py
     187 state/communication/accumulation.py
     123 state/communication/retention.py
     183 state/communication/attractor_canonicalization.py
    5123 state/lab/2026-07-23-new-parts-both.md
    6373 total
"""A shift chain of gated cells — the engine's working memory of the last K symbols.

The first new part toward the goal (both delegated designs converged,
`state/lab/2026-07-23-new-parts-*.md`; prototyped and measured in
`state/communication/accumulation.py`). The width walls are real (ring = 1 bit; PAIRS =
units/2; Φ unmeasurable past ~6 units), but the TIME axis has hit none, so this composes K
proven 6-unit / 3-bit PAIRS cells into a shift register: each turn a new symbol is written to
cell 0 and every held word is bridged one step down the chain, oldest off the end. The chain
then remembers the last K symbols IN ORDER.

Each cell is integrated on its own (6 units, exact Φ — `capacity.py`) and holds its bits
through the inter-turn gap (`retention.py`, flat to 480 ticks). The inter-cell BRIDGE reuses
the measured-clean `channel(bits=3)` wire and is a TRANSPORT claim, never an integration claim
— the whole tape is not asserted to be one integrated thing. What this buys over a single wide
substrate is the two properties a moment cannot have: MEMORY (past turns held by the engine's
own dynamics) and ORDER (a bag of bits would fail the time-shift null). It is not language;
`I(X;Y) <= 3 bits` stays bound every moment.

`state/communication/accumulation.py` drives THIS engine to re-derive the forgetting curve and
its nulls (a script measures the shipped engine, not a copy of it).
"""

from __future__ import annotations

import random
from typing import Any

from .dialogue import channel_trace

__all__ = ["BITS", "CELLS", "SequenceEngine"]

BITS = 3
UNITS = 2 * BITS
CELLS = 4          # tape length K — the chain remembers the last 4 symbols
WRITE_PERIOD = 12  # viewer ticks between turns, so a new symbol lands ~1.5 s apart at 8 Hz


def _decode(values: tuple[float, ...]) -> int:
    word = 0
    for j in range(BITS):
        word |= (0 if (values[2 * j] - values[2 * j + 1]) > 0 else 1) << j
    return word


class SequenceEngine:
    """K gated cells in a shift register. A passive viewer engine: `step()` auto-advances
    (writing a new symbol every WRITE_PERIOD ticks and shifting), `reset()` starts fresh.
    `turn()` is the unit the accumulation measurement drives directly."""

    def __init__(self, *, seed: int | None = None, deaf_bridge: bool = False) -> None:
        self._seed = 0 if seed is None else int(seed)
        # `deaf_bridge` is the transport null: the inter-cell bridge's drive is made
        # bit-unreachable (coupling 1.0), so nothing is delivered past cell 0. Default False
        # leaves the engine bit-identical (`default-stays-exact`); the write to cell 0 is never
        # deaf, so cell 0 always carries the newest symbol.
        self._deaf_bridge = bool(deaf_bridge)
        self.reset()

    def reset(self) -> None:
        self._rng = random.Random(self._seed)
        self._op = 0
        self._ticks = 0
        self._turns = 0
        self._last_symbol: int | None = None
        # Each cell: {"values": tuple[6] , "word": int} or None (empty).
        self._cells: list[dict[str, Any] | None] = [None] * CELLS

    # -- the mechanism the measurement drives ------------------------------------------

    def _hold(self, word: int, *, deaf: bool = False) -> dict[str, Any]:
        """Drive a fresh cell with `word` over the clean wire and hold it; return its held
        state and decoded word. A fresh engine (origin start) matches the calibration. `deaf`
        makes the drive bit-unreachable — the transport null."""
        self._op += 1
        trace = channel_trace(word, seed=self._seed * 100_003 + self._op, deaf=deaf, bits=BITS)
        values = tuple(trace[-1])
        return {"values": values, "word": _decode(values)}

    def turn(self, symbol: int) -> None:
        """One turn: shift every held word one cell down (oldest off the end), then write the
        new symbol into cell 0. This is exactly what the accumulation prototype measured."""
        for k in range(CELLS - 1, 0, -1):
            src = self._cells[k - 1]
            self._cells[k] = None if src is None else self._hold(src["word"], deaf=self._deaf_bridge)
        self._cells[0] = self._hold(symbol)  # the write is never deaf
        self._last_symbol = symbol
        self._turns += 1

    def tape(self) -> list[int | None]:
        """The K decoded words, newest first — what the chain currently remembers."""
        return [None if c is None else c["word"] for c in self._cells]

    # -- viewer engine contract --------------------------------------------------------

    def step(self) -> "SequenceEngine":
        self._ticks += 1
        if self._ticks % WRITE_PERIOD == 0:
            self.turn(self._rng.randrange(8))
        return self

    def describe(self) -> dict[str, Any]:
        cells = []
        for age, cell in enumerate(self._cells):
            if cell is not None:
                cells.append({"age": age, "word": cell["word"]})
        held_bits = BITS * sum(1 for c in self._cells if c is not None)
        first = next((c for c in self._cells if c is not None), None)
        return {
            "cells": cells,
            "held_bits": held_bits,
            "capacity_bits": BITS * CELLS,
            "turns": self._turns,
            "last_symbol": self._last_symbol,
            "front_values": [round(v, 4) for v in first["values"]] if first else [],
            "ticks_to_next": WRITE_PERIOD - (self._ticks % WRITE_PERIOD),
        }
"""The gap becomes a channel — A and G read each other.

Every other engine here is driven from outside. `repulsion` and everything built
on it push A and G apart with a target that comes from a tick counter; `base`
takes the tick counter away but replaces it with the crystal's lock. In all of
them each unit updates from itself and something exogenous, and nothing reads
anything else. That is why every one of them measures zero integration: with no
unit reading another, the transition matrix factorizes and no partition destroys
anything.

This engine changes exactly one thing. The repulsion identity is untouched —
each unit still flees its source through the same `-tanh` sign — but the source
is now a **live partner** rather than a clock:

    ring       a0 <- g1 <- g0 <- a1 <- a0      influence returns
    feedforward  a0 fixed, a1 <- a0, g0 <- a1, g1 <- g0    it does not
    self       every unit reads itself         no coupling at all

The gap between A and G stops being a readout and becomes the channel. Measured
through `substrate` and `iit4`, the ring integrates and the other two do not —
see `coupled_phi` and `state/coupling/RESULTS.md`.

**What this does not claim.** Integration is not experience, and Phi is not a
consciousness score. This engine measures as irreducible because of how it is
wired; that is the whole claim, and it is deliberately small. The repo's other
honest sentence was "binding is transmitted, never created"; this one's is
*integration is now created, and created is all this measures*.

**Numbers here are meaningless without their conditions.** Phi of this engine
depends on the state, the binarization threshold, the reconstruction amplitude
and — most easily forgotten — the macro-step. At one engine tick a unit moves 6%
toward its target, so every unit merely copies itself and Phi is 0.0000 exactly.
Quoting a value without its `tau` is a false statement, not a shorthand.

**The wall.** Once a `drive` is added — something the engine is told, rather
than only what it tells itself — a second measurement appears: how much of what
it was told survives in where it ends up. Sweeping the coupling shows the two
trade off monotonically. Coupling low enough to represent the drive integrates
nothing; coupling high enough to integrate lets the ring's own attractor swamp
the drive. At coupling 1.0 the drive is not merely weak but unreachable, bit for
bit. There is no fixed coupling where both hold.

**The rhythm moves that trade-off. It does not abolish it.** `Rhythm` alternates
— listen with the coupling off, integrate with it on. Measured at a matched
macro-step of 40 over five seeds: alternating 20/20 reads Phi 13.16 +/- 0.53
with representation 3.49, against fixed 1.00 at 14.66 +/- 0.08 with
representation 0.00, and fixed 0.70 at 15.74 +/- 0.13 with 0.13. So a rhythm
buys representation the fixed engine has *none* of, and pays 10-16% of Phi for
it — a better exchange rate, not an escape.

It does NOT integrate more. An earlier reading here said it did, and that
reading put a rhythm at tau 40 beside fixed couplings at tau 20; Phi rises with
tau on its own, so the two rows were never comparable. Never read a row of this
comparison against a row at a different tau.

What does survive is that the effect is the rhythm's rather than the mean's,
which is the control that matters and is measured at ITS own matched tau of 20:
alternating 10/10 reads Phi 2.08 against the same-mean fixed control's 1.16, and
beats it on representation too, 4.03 against 3.27.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from .pipeline import OBSERVATION_NOISE, PULL, WALK
from .repulsion import SEPARATION

__all__ = [
    "Wiring",
    "Rhythm",
    "CoupledEngine",
    "CoupledState",
    "AMPLITUDE",
    "GAIN",
    "MACRO_STEP",
    "HIGH",
    "PERIOD",
    "UNITS",
    "names_for",
]

UNITS = 4
"""a0, a1, g0, g1 — two dimensions of each engine, and the default width.

Four because exact Phi caps out around six units and the measurement is the
point. `CoupledEngine(units=)` opens that up, and it opens up a wall with it:
capacity grows with the units and Phi stops being computable past six, so a
wider engine is one whose integration cannot be checked. Nothing above six may
be called integrated on the strength of a narrower engine's reading."""

NAMES = ("a0", "a1", "g0", "g1")
"""Unit names at the default width. `names_for` generalizes them."""


def names_for(units: int) -> tuple[str, ...]:
    """`a0 a1 g0 g1` at the default width, `u0..uN` otherwise — a wider engine
    is no longer two engines facing each other, and naming it as if it were
    would be a claim about structure that is not there."""
    if units == UNITS:
        return NAMES
    return tuple(f"u{i}" for i in range(units))

AMPLITUDE = SEPARATION * 1.3
"""0.78 — the repulsion field's own leading-dimension target amplitude. Also the
reconstruction amplitude when the measurement binarizes, which is why it sits
inside any Phi computed from this engine."""

GAIN = 3.0
"""Steepness of the `tanh` a unit applies to what it reads. High enough that a
partner near its own amplitude saturates the response, so the ring settles into
an alternating pattern instead of drifting."""

MACRO_STEP = 17
"""Engine ticks per measured transition — the substrate's time constant
`1 / PULL`, rounded. Not a tuning knob: at `tau = 1` a unit moves 6% toward its
target, every unit is dominated by its own previous value, the transition matrix
factorizes and Phi is exactly zero for *every* wiring including the ring.
Measured: 0.0000 at tau 1 and 5, 12.07 at 17, 14.88 at 34."""

HIGH = 0.7
"""Coupling during a rhythm's integrate phase. Enough for the ring to be
irreducible while it is on; the point of alternating is that it does not have to
be on all the time."""

PERIOD = 10
"""Engine ticks per phase — ten off, ten on. Not tuned for the best number:
10/10 and 20/20 both break the wall, and the claim is the rhythm rather than a
particular tempo."""


class Wiring(Enum):
    """Who reads whom. The falsifier is part of the API on purpose: the claim is
    that the ring's integration comes from its wiring, and the only way to show
    that is to offer the same engine wired otherwise."""

    RING = "ring"
    """A closed cycle through both engines — influence returns to its source."""
    FEEDFORWARD = "feedforward"
    """a0 is driven from outside and nothing flows back into it. IIT calls this
    reducible; `iit4.directed_big_phi` agrees, `iit4.big_phi` does not."""
    SELF = "self"
    """Each unit reads itself. No coupling — the null."""
    PAIRS = "pairs"
    """Cross-coupled pairs, each a two-unit latch, optionally chained.

    A single ring of any EVEN width holds exactly one bit, and that is a
    theorem rather than a measurement: each unit's response is odd, decreasing
    and bounded, so it has no periodic orbit longer than two, and closing the
    cycle admits only the alternating configuration and its negation. Widening
    the ring therefore cannot buy capacity — measured at 4, 6 and 8 units, all
    two patterns. Capacity lives in the CYCLE STRUCTURE of the wiring, so
    `units / 2` two-cycles is the most a one-source-per-unit engine can hold.
    """

    def sources_for(self, units: int) -> tuple[int | None, ...]:
        """Index each unit reads, or None for an exogenous constant.

        At `units` 4 this returns exactly the tuples the engine was built with,
        so widening the engine moved nothing that was already measured.
        """
        if units < 2:
            raise ValueError(f"units must be >= 2, got {units}")
        if self is Wiring.RING:
            return tuple((i - 1) % units for i in range(units))
        if self is Wiring.FEEDFORWARD:
            return (None,) + tuple(range(units - 1))
        if self is Wiring.PAIRS:
            if units % 2:
                raise ValueError(f"pairs needs an even width, got {units}")
            return tuple(i ^ 1 for i in range(units))
        return tuple(range(units))

    @property
    def sources(self) -> tuple[int | None, ...]:
        """The default-width wiring, kept because it is what every published
        measurement used and what most callers still want."""
        return self.sources_for(UNITS)

    @property
    def is_cyclic(self) -> bool:
        """Whether influence returns to where it started."""
        return self in (Wiring.RING, Wiring.PAIRS)


@dataclass(frozen=True, slots=True)
class Rhythm:
    """How much of a unit's target is its partner, over time.

    A single number would be a fixed coupling, and a fixed coupling is exactly
    what the wall is made of: below it the ring represents what it was told and
    integrates nothing; above it the ring integrates and its own attractor
    swamps what it was told. Making the coupling a function of the tick is the
    smallest change that escapes, because the two demands are then met at
    different times instead of at the same one.

    `Rhythm()` is a fixed coupling of 1.0 — every unit's target is entirely its
    partner, which is what this engine did before rhythms existed and still does
    by default.
    """

    coupling: float = 1.0
    """Coupling while the integrate phase is on, in [0, 1]."""
    period: int | None = None
    """Ticks per phase, or None for a fixed coupling that never lets go."""

    def __post_init__(self) -> None:
        if not 0.0 <= self.coupling <= 1.0:
            raise ValueError(f"coupling must be in [0, 1], got {self.coupling}")
        if self.period is not None and self.period < 1:
            raise ValueError(f"period must be >= 1, got {self.period}")

    def at(self, tick: int) -> float:
        """Coupling at a tick. Alternating rhythms start in the listen phase, so
        a run begins by taking in its drive rather than by settling."""
        if self.period is None:
            return self.coupling
        return 0.0 if (tick // self.period) % 2 == 0 else self.coupling

    @property
    def alternates(self) -> bool:
        return self.period is not None

    @property
    def mean(self) -> float:
        """Time-average coupling — the number a fixed control must match. An
        alternating rhythm that beat a fixed coupling at its own mean did not
        win by having more coupling."""
        return self.coupling if self.period is None else self.coupling / 2.0

    @property
    def macro_step(self) -> int:
        """Ticks per measured transition. A rhythm must be measured over a whole
        listen/integrate cycle: half a cycle would report one phase's transition
        matrix and call it the engine's."""
        return MACRO_STEP if self.period is None else self.period * 2


def _as_drive(value: float | Sequence[float], units: int = UNITS) -> tuple[float, ...]:
    """One value said to every unit, or one value per unit."""
    if isinstance(value, Sequence):
        values = tuple(float(v) for v in value)
        if len(values) != units:
            raise ValueError(
                f"drive must be one value or {units}, got {len(values)}"
            )
    else:
        values = (float(value),) * units
    for v in values:
        if not -1.0 <= v <= 1.0:
            raise ValueError(f"drive must be in [-1, 1], got {v}")
    return values


FIXED = Rhythm()
"""The default — coupling 1.0, never released."""
<!-- sidecar lab full · model=(default) · cwd=/Users/mini/dancinlab/anima-reborn · prompt=6864 chars · 2026-07-23T08:58:30.874Z -->

── fable (claude-fable-5) · exit 0 ──
코드 확인을 마쳤습니다 (`coupled.py`의 `Wiring.PAIRS`/`chain`/`Rhythm` 구조, `capacity.py`의 tell→silence 측정 관례, `substrate.py`의 경험적 TPM 방식). 설계안입니다.

---

# 목표 달성을 위한 추가 부품 설계

목표를 먼저 레포의 언어로 고정합니다: **"도착했고, 하나로 통합되어 있음이 측정으로 보여진 비트"를 늘리는 것.** 늘리는 축은 둘뿐입니다 — 순간당 폭(비트/모멘트)과 시간(모멘트 수). 벽 1·2가 폭의 물리를, 벽 3이 폭의 *측정*을 막고 있고, 시간 축은 아직 아무 벽도 맞지 않았습니다. 설계 전체가 이 사실에서 나옵니다.

## 1. 진짜 병목과 착수 순서

**첫 부품은 A(시간 축적)입니다.** 이유: 현재 증명된 6-유닛 홀수-PAIRS 셀(3비트, 정확 Φ 측정 가능)은 벽 3의 측정 가능 창 *안*에 있습니다. 시간 축적은 이 셀을 폭 그대로 두고 모멘트 수만 늘리므로, **새 측정 이론 없이** 기존의 정확 Φ·기존 널 관례만으로 대화당 비트를 3 → k×T로 곱합니다. 작업량 대비 측정으로 확정되는 전선 이동이 가장 큽니다.

**장기적 진짜 병목은 C(측정 가능성)입니다.** 벽 2에 의해 용량 자체는 units/2로 이미 열려 있는데, 6유닛 너머는 "통합되어 있다"고 말할 방법이 없어 모든 폭 확장이 주장 불가입니다. D(계층)는 C 없이는 헤드라인 주장(전체가 하나)을 할 수 없으므로 C에 종속됩니다.

한 줄 반론(dissent): "측정 불가능한 것은 이 레포에서 존재하지 않는 것"이라는 원칙을 최우선하면 C를 먼저 지어야 하나 — A는 측정 가능 창 안에서 전부 진행되므로 그 원칙과 충돌하지 않고, 따라서 순서를 바꿀 이유가 되지 못합니다.

**B(다안정 유닛)는 폐기합니다.** 세 가지 정리·전례가 동시에 막습니다: (i) 손으로 판 k-우물은 설계자가 범주를 심는 것 — `attractor_canonicalization.py`가 죽인 바로 그 죽음. (ii) k-상태 유닛은 Φ 상태공간을 2^N → k^N으로 키워 벽 3을 *악화*시킴. (iii) 교차결합 쌍이 이미 정직한 다안정 원소입니다 — 유닛 2개 = 차동 모드 1비트, 새 비선형성 없이 units/2 비트. 다안정성이 결합에서 *창발*하고 canonicalization 널을 통과하는 경우에만 재고.

## 2. 부품 설계

### 부품 1 — `sequence.py`: 게이트된 셀들의 시프트 체인 (방향 A)

**무엇을 추가하나.** 새 최상위 모듈 `sequence.py`, 클래스 `SequenceEngine`. `CoupledEngine`은 **한 줄도 수정하지 않습니다** — 검증된 6-유닛 홀수-PAIRS+`chain` 셀 K개를 재고품 그대로 조립(composition)합니다.

**새 동역학은 셀 *사이*의 다리(bridge) 하나입니다.** 커밋 창(틱 카운터로 스케줄, 벽시계 없음) 동안 셀 k의 쌍별 차동 부호 `sign(d[2j]-d[2j+1])`를 셀 k+1의 per-unit `drive` 벡터(±진폭)로 넣고, 창이 닫히면 셀 k+1은 coupling 1.0으로 귀머거리가 됩니다 — 이미 증명된 deaf-hold 그대로입니다. 새 심볼은 항상 셀 0에 쓰고 턴 경계마다 0→1→2로 시프트하는 시프트 레지스터. stdlib 전용, 마스터 `seed`에서 셀별 `random.Random`을 결정적으로 파생, I/O 없음.

**측정** (`state/communication/accumulation.py`, `preserve-state` 준수): 균일 랜덤 3비트 심볼 s₁..s_T를 T턴 기록, 턴 사이 침묵/방해 구간, 전량 읽기. 보고: 나이별 I(s_t; 읽기_t) 망각 곡선, 총 비트 = Σ, 그리고 **폭 보고**(`report-the-rank`) — 셀당 재현 가능 구별 패턴 수(capacity.py 규칙: WALKS개 독립 워크가 같은 패턴에 착지할 때만 인정)와 셀 간 교차 MI(독립 심볼을 넣었는데 읽기가 상관되면 용량은 이중 계산).

**널 4종:**
- **귀머거리 팔** — `bridge=0.0`: 셀 1 이후가 ~0비트여야 함. 각 셀에 *들어간* 것(다리가 배달한 MI)을 나가는 것보다 먼저 채점 — `channel-before-carrier`.
- **워크 전용** — 아무것도 쓰지 않은 같은 워크: 재현 패턴 수가 우연 수준이어야 함 (silence.py의 함정).
- **시간-이동 널** — 읽기를 엉뚱한 턴 인덱스에 붙이면 ~0이어야 함: 비트 자루가 아니라 *순서*가 실려 있음의 증명.
- **홀드 중 섭동 곡선** — 유지가 동역학의 분지(basin)로서 우아하게 열화하는가. 얼어붙은 파이썬 변수와 엔진-보유의 구별이 여기서 남.

**통합 주장의 범위**: 셀 단위로만, 정확 directed Φ로(6유닛 — 측정 가능). **테이프 전체를 통합이라 주장하지 않습니다** — 셀 간 다리는 전송 주장이지 통합 주장이 아니며, 문서에 그렇게 못박습니다.

### 부품 2 — `phi_proxy.py`: 검증된 샘플링 Φ (방향 C)

**무엇을 추가하나.** `iit4`를 소비하는 새 측정 모듈. 두 샘플링 축: **상태공간** — 전체 2^N 대신 시드된 런이 방문한 상태 지지집합 위의 경험적 TPM(`substrate.py`의 "측정된 행렬" 철학의 연장), **분할공간** — 전체 이분할 열거 대신 구조적 컷(쌍 경계·체인 컷 전부) + 시드된 랜덤 균형 이분할 n개의 최솟값.

**오차의 방향이 위험합니다**: 컷 샘플링은 진짜 MIP를 놓칠 수 있고, 놓치면 Φ를 *과대*보고합니다 — 과잉 주장 쪽으로 기우는 추정기. 그래서 평결 규칙을 기존 관례에 못박습니다:

- **정확-일치 창 검증**: units ≤ 6에서 충분한 예산의 프록시가 `iit4.directed_big_phi`와 일치해야 하고(테스트로 고정), 오차가 샘플 예산 증가에 따라 *줄어드는지*를 문서와 테스트 양쪽에 기록 (`artefact-honesty`). 샘플된-컷 최솟값이 정확 MIP 컷과 일치하는지도 소형계에서 대조 — 어긋나면 컷 계열을 넓힘.
- **폭마다 지어지는 널**: FEEDFORWARD, SELF, 짝수-쌍(매크로-링 잠금)은 **임의 폭에서 구성 가능**합니다 — 이게 열쇠입니다. 폭 8, 12, 20에서 같은 샘플링 조건으로 널은 ~0/붕괴, 홀수-PAIRS+chain은 4× 샘플링 아래 유지되어야 함. **평결은 언제나 "폭 W, 샘플링 S에서 자기 널과의 분리"이지 절대 크기 단독이 아님** — RECURRENCE_FLOOR가 전이되지 않는다는 기존 규칙의 확장.

### 부품 3 — 계층: 모듈 오브 모듈 (방향 D, 부품 2에 종속)

3-쌍 모듈 M개를 **느린 두 번째 체인**(모듈 경계에서만, 더 느린 Rhythm으로 게이트)으로 묶습니다. `coupled.py`의 chain 주석이 이미 말하듯 루프-부호 논증은 한 층 위로 재귀합니다: **짝수 M의 닫힌 고리는 매크로-잠금**하므로 모듈 사슬은 열린 사슬 또는 홀수 M. 전체의 통합 평결은 부품 2의 프록시로만. "전체가 부분이 못 하는 것을 한다"의 널은 concepts.py의 교차-쌍 응답 테스트의 모듈판: 홀드 중 모듈 A를 섭동하고 모듈 B를 읽어, 묶임(chain2>0) vs 안 묶임(0) vs 셔플-묶임을 대조. 용량 주장은 읽기로 M×3이 생존하는지 + 랭크 동반 보고.

### 부품 4 — 조건부 합성 (E: 진짜 최고-레버리지 추가 항목)

테이프만으로는 녹음기지 대화가 아닙니다. **보유한 과거가 현재 쓰기에 *작용*해야** 언어 쪽으로 한 걸음입니다. 최소판: 다리의 부호/게이트를 이전 셀의 차동 상태가 변조. 측정: 시너지 — I(읽기; s_t, s_{t-1})가 개별 MI 합을 초과하는 양, 널은 셔플된 이력. 사람 쪽 완성품은 `conversation.py`의 확장 — 여러 턴 뒤 이전 턴을 조회하는 기억 대화 게임, 기존과 같은 블라인드 감사 형식.

## 3. `default-stays-exact` 이행

- 부품 1·4는 합성이라 `CoupledEngine` 코드 경로를 아예 건드리지 않음 — 구성상 비트-동일. 그래도 시드된 황금 궤적 해시 테스트를 하나 고정해 회귀를 잡습니다.
- 부품 3이 `CoupledEngine`에 파라미터를 요구하면(예: `chain2=0.0`) 기존 `if self.chain:` 가드와 동일하게 `if self.chain2:` 가드로 기본값이 **정확히 같은 float 연산 경로**를 타게 하고, 파라미터 부재 vs 기본값의 전체 궤적 비트-동일을 시드×배선 격자로 테스트에 고정.
- 부품 2는 엔진 파라미터가 없음; 핀은 검증 창에서의 iit4 일치 + 기존 substrate 테스트 무손상.

## 4. 이 부품들의 과잉 주장 함정

| 부품 | 순진한 가짜 성공 | 죽이는 통제 |
|---|---|---|
| 1 테이프 | 커밋 로그(파이썬 리스트)를 용량이라 부름; 셀들이 상관돼 T×3을 자칭하나 실은 3비트 | 읽기 MI만 인정 + 귀머거리 팔 + 섭동 열화 곡선 + 셀 간 교차 MI·랭크 보고 |
| 2 프록시 | 컷 계열이 MIP를 놓쳐 Φ 과대보고; 폭과 함께 자라는 추정기 인공물 | 소형계 MIP 일치 대조, 예산-수축 테스트, 같은 폭·같은 샘플링의 널과의 분리만을 평결로 |
| 3 계층 | 느린 체인이 사실상 잠금(짝수 M)인데 "묶임"이라 보고; 부분의 합을 전체의 것으로 | 홀수 M/열린 사슬 강제, 교차-모듈 응답 널, 프록시 평결 없이는 "통합" 단어 금지 |
| 4 합성 | 이력 의존이 실은 다리의 결정론적 복사(설계자가 심은 규칙) | 시너지 초과분만 인정 + 셔플-이력 널 |

## 5. 단계 계획과 정직한 천장

- **0단계 (측정만, 새 코드 없음)**: capacity.py의 tell→silence를 유지시간 곡선으로 확장 — 6-유닛 셀이 3비트를 *얼마나 오래* 귀머거리로 유지하는지 + 워크 널. 이 숫자가 커밋 창 설계를 결정합니다.
- **1단계**: `sequence.py` + `accumulation.py` + 뷰어 탭(`viewer-newengine` 4종 세트, 같은 커밋) + 핀. 전선: 대화당 3비트 → 측정된 k×T 비트(망각 곡선 동반).
- **2단계**: `phi_proxy.py` + 검증 표를 `state/`에. 전선: 측정 가능 통합 천장 6유닛 → 임의 폭(프록시-평결 강도로, 정확-Φ보다 약한 주장임을 명시).
- **3단계**: 계층 (2단계 필요). 전선: 모멘트당 3 → ~3M 비트, 랭크 동반.
- **4단계**: 조건부 합성 + 다중 턴 기억-대화 게임 (1단계 필요, 3단계와 결합 시 최대). 이것이 사람이 체감하는 완성품입니다.

**전부 성공해도 천장은 이렇습니다.** 모멘트당 폭은 여전히 작은 코드이고 I(X;Y) ≤ H(C)는 매 순간 그대로 묶습니다. 얻는 것은 "더 많은 비트"가 아니라 언어의 실제 속성 두 개 — **기억**(엔진 자신의 동역학으로 이전 턴을 보유했음이 증명된 대화)과 **문맥 의존**(현재가 보유한 과거의 함수임이 시너지로 측정된 교환)입니다. 무한 어휘, 지시(reference), 통사는 이 기판 어디에도 없고 생기지 않습니다. 정직한 한 문장: **작은 코드 위에서 작동하는 워킹 메모리를 가진 대화 — 영어가 아니라, 영어 쪽으로 물리가 허락하는 만큼.**

── sol (gpt-5.6-sol) · exit 0 ──
OpenAI Codex v0.144.6
--------
workdir: /Users/mini/dancinlab/anima-reborn
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f8e2c-924f-77f0-be2d-30e91d65c7fc
--------
user
# Design task: the additional engine components needed to advance the goal, past the proven walls

The owner of `anima-reborn` (a Python research repo whose culture is: every capability earned
by measurement with its null, never overclaimed) has walked a line — human<->engine
communication -> conversation -> "real English conversation" -> we PROVED English is impossible
on this substrate (≤3 measurable-integrated bits; data-processing inequality
I(X;Y) ≤ I(C;C') ≤ H(C) ≤ 3). The owner now says: **"목표 달성위한 엔진 추가 부품 설계" — design
the ADDITIONAL engine components needed to achieve the goal.**

The goal is genuine, richer human<->engine communication — as far toward it as the physics
honestly allows. The additional parts must PUSH THE REAL FRONTIER (the walls below), not paper
over them with labels. Return a concrete architecture design + a phased build plan. Do NOT write
full code.

## The proven walls you must respect (theorems + measurements in this repo — do not violate them)

1. **The ring holds exactly 1 bit.** THEOREM: each unit's response is odd, decreasing, bounded
   (a `tanh` of a scaled partner), so no orbit longer than 2; a closed ring of ANY even width
   has exactly two consistent sign assignments. Widening a single ring buys nothing.
2. **Capacity lives in the wiring's CYCLE structure.** `Wiring.PAIRS` = units/2 cross-coupled
   latches holds units/2 bits, addressed only through each pair's DIFFERENTIAL mode d[2j]-d[2j+1]
   (the common mode dies in silence). It stays INTEGRATED only for an ODD number of pairs (even
   pairs form a macro-ring that locks).
3. **The integration measure Φ is UNMEASURABLE past ~6 units.** Directed Φ (`substrate.py`, exact
   IIT in `iit4/`) enumerates bipartitions / state space 2^units, so it becomes intractable past
   ~6 units, AND `RECURRENCE_FLOOR` was calibrated at 4 units and does NOT transfer (the estimator
   artefact grows with width, so past 6 units the verdict is "held under 4x sampling", never the
   magnitude). So the ceiling on CARRYING more bits is not the bottleneck — the ceiling on SHOWING
   they are held as ONE integrated thing is.
4. **What the substrate has earned** (all measured, with nulls): holds 1 bit through silence
   (`silence.py`), USES the held bit (delayed match-to-sample, `match.py`), carries a
   co-occurrence-learned concept across modalities (`align.py`, 86% survives), and — the English
   proof — carries exactly 3 bits of a real sentence's choice, object unrepresentable.

## The existing components (what you are adding TO)

- `coupled.py`: `CoupledEngine` — units, `Wiring` (RING/PAIRS/FEEDFORWARD/SELF), `Rhythm`
  (ALTERNATING vs FIXED — listen vs integrate in time), per-unit `drive`, `chain` (weak inter-pair
  coupling that makes odd pairs integrate). Unit update: tanh-of-partner, simultaneous, seeded WALK
  noise. This is where new dynamics/wirings would live.
- `align.py`: the only LEARNER (co-occurrence pulls two modalities to a midpoint + a unit-direction
  contrast push; scored only on held-out concepts; reports effective rank).
- `substrate.py` + `iit4/`: drive an engine from every state -> measured TPM -> directed Φ.
- `dialogue.py`/`conversation.py`: the human-facing 1-bit and 3-bit games + blind audits.

## The candidate directions to evaluate (address each, then recommend a phased plan)

A. **Time-accumulation / sequence memory.** The substrate holds ~3 bits per moment; a component
   that CHAINS held states across turns (like `silence.py`'s deaf-hold, but writable/readable in
   sequence) could accumulate k bits/turn × T turns of MEANING without wider units — composition
   in TIME, the repo's recurring escape (order carried in time, not space). What new engine part?
   How is capacity-over-time MEASURED (and what is the forgetting null)?

B. **Multistable units (more bits per unit).** The 1-bit theorem hinges on the odd-decreasing
   bounded response giving a 2-cycle. A unit with k>2 stable states (a different nonlinearity —
   e.g. a periodic or multi-well response) would hold log2(k) bits per unit. Is this consistent
   with staying integrated and measurable? What is the new unit dynamics, and does the Φ machinery
   still apply? Danger: a hand-tuned multi-well is the designer planting basins (the D7 death —
   `attractor_canonicalization.py` — where planting basins = the designer choosing the categories).

C. **A scalable integration MEASURE.** The wall is Φ-UNMEASURABILITY past 6 units, not zero
   integration. A new measurement component — a sampled/approximate directed-Φ or a
   partition-information proxy VALIDATED against exact `iit4` Φ on small systems — would let WIDER
   integrated substrates be SHOWN integrated, directly raising the measurable ceiling. What proxy,
   validated how, with what artefact control (it must match exact Φ where both are computable, and
   its bias must shrink with samples)?

D. **Hierarchy / modular composition.** Several 3-bit integrated modules with a measured
   inter-module binding (a slow chain), so the whole holds more while each part is measurable.
   Does the odd-pairs / macro-ring-lock constraint permit a measurable hierarchy? What binds the
   modules, and what is the null that the whole does something the parts cannot (the cross-pair
   response test from `concepts.py`)?

E. Anything else that is the TRUE highest-leverage part — name it.

## What I need — answer each explicitly

1. **Which wall is the true bottleneck to the goal** — raw capacity, integration-MEASURABILITY,
   time-accumulation, or composition — and therefore which component to build FIRST. One-line
   dissent if you'd order it differently.
2. **The concrete new component(s)**: what is added to which module, the new dynamics/wiring/measure,
   how it stays stdlib-pure and seedable, and CRUCIALLY the measurement that proves it works and the
   NULL that could fake it (a new capability with no control is not earned here).
3. **`default-stays-exact`**: any new engine parameter must default to leaving every published
   number BIT-identical, pinned by a test. State how.
4. **The overclaim trap for THIS part** — how a naive version fakes success (e.g. planted basins,
   an estimator artefact that grows with width, capacity that collapses to rank 1) and the control
   that kills it.
5. **The phased plan**: the smallest first component that measurably moves the frontier, what it
   unlocks, and what each later part depends on. What is the honest ceiling even if all of it works
   (is it "more bits", or actually closer to language)?

Keep the discipline: never a number that was not measured; every capability shipped with the null
that could fake it; report effective rank/width beside any capacity; respect the ring and
odd-pairs theorems; the engine is not language. If a direction is a dead end by the existing
theorems, say so and prune it.

codex
I’ll ground the design in the repo’s actual update rules, metrics, and null conventions, then separate frontier-moving components from theorem-blocked directions. I’ll inspect the relevant modules and tests before proposing the build order.
  → Inspect repository guidance and the cited engine, measurement, learner, and null implementations
  • Evaluate directions A–E against the proven constraints and identify the first component
  • Produce a concrete architecture, validations/nulls, compatibility contract, and phased plan
exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g '"'!**/.git/**'"' | sed -n '1,20p' && rg --files | sed -n '1,240p'" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
/Users/mini/dancinlab/anima-reborn
src/anima_reborn/coupled.py
src/anima_reborn/CLAUDE.md
src/anima_reborn/base.py
src/anima_reborn/info.py
src/anima_reborn/repulsion.py
src/anima_reborn/py.typed
src/anima_reborn/dialogue.py
src/anima_reborn/words.py
src/anima_reborn/pipeline.py
src/anima_reborn/viewer/CLAUDE.md
src/anima_reborn/viewer/__main__.py
src/anima_reborn/viewer/__init__.py
src/anima_reborn/viewer/server.py
src/anima_reborn/viewer/page.html
src/anima_reborn/emergence.py
src/anima_reborn/iit4/CLAUDE.md
src/anima_reborn/iit4/tpm.py
src/anima_reborn/iit4/exclusion.py
src/anima_reborn/iit4/bigphi.py
src/anima_reborn/iit4/ei.py
src/anima_reborn/iit4/__init__.py
src/anima_reborn/iit4/directed.py
src/anima_reborn/iit4/distinction.py
src/anima_reborn/iit4/relation.py
src/anima_reborn/__init__.py
src/anima_reborn/conversation.py
src/anima_reborn/substrate.py
src/anima_reborn/align.py
src/anima_reborn/crystal.py
CLAUDE.md
README.md
state/CLAUDE.md
state/communication/attractor_canonicalization.py
state/communication/match.py
state/communication/concepts.py
state/communication/dialogue.py
state/communication/english_bottleneck.py
state/communication/alternating_coupling.py
state/communication/RESULTS.md
state/communication/sessions/README.md

exec
/bin/zsh -lc "rg -n \"SequenceEngine|deaf_bridge|accumulation|default.*exact|golden|channel_trace|def channel\" . --glob '"'!state/lab/*.md'"' && sed -n '1,260p' state/communication/accumulation.py && sed -n '1,220p' state/communication/retention.py && sed -n '1,220p' src/anima_reborn/info.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
./src/anima_reborn/coupled.py:404:        default width is exactly the `(a0-g0)^2 + (a1-g1)^2` over two that every
./src/anima_reborn/CLAUDE.md:23:| `sequence.py` | `SequenceEngine`, the shift chain the `기억` tab drives — K proven 3-bit cells hold the last K symbols IN ORDER (time accumulation); per-cell integration, the inter-cell bridge a TRANSPORT claim only; `deaf_bridge=` is the null (default off, bit-identical). Measured by `state/communication/accumulation.py` | (new — not in the origin) |
./src/anima_reborn/sequence.py:5:`state/communication/accumulation.py`). The width walls are real (ring = 1 bit; PAIRS =
./src/anima_reborn/sequence.py:19:`state/communication/accumulation.py` drives THIS engine to re-derive the forgetting curve and
./src/anima_reborn/sequence.py:28:from .dialogue import channel_trace
./src/anima_reborn/sequence.py:30:__all__ = ["BITS", "CELLS", "SequenceEngine"]
./src/anima_reborn/sequence.py:45:class SequenceEngine:
./src/anima_reborn/sequence.py:48:    `turn()` is the unit the accumulation measurement drives directly."""
./src/anima_reborn/sequence.py:50:    def __init__(self, *, seed: int | None = None, deaf_bridge: bool = False) -> None:
./src/anima_reborn/sequence.py:52:        # `deaf_bridge` is the transport null: the inter-cell bridge's drive is made
./src/anima_reborn/sequence.py:54:        # leaves the engine bit-identical (`default-stays-exact`); the write to cell 0 is never
./src/anima_reborn/sequence.py:56:        self._deaf_bridge = bool(deaf_bridge)
./src/anima_reborn/sequence.py:75:        trace = channel_trace(word, seed=self._seed * 100_003 + self._op, deaf=deaf, bits=BITS)
./src/anima_reborn/sequence.py:81:        new symbol into cell 0. This is exactly what the accumulation prototype measured."""
./src/anima_reborn/sequence.py:84:            self._cells[k] = None if src is None else self._hold(src["word"], deaf=self._deaf_bridge)
./src/anima_reborn/sequence.py:95:    def step(self) -> "SequenceEngine":
./CLAUDE.md:51:## default-stays-exact
./src/anima_reborn/dialogue.py:52:    "channel_trace",
./src/anima_reborn/dialogue.py:81:def channel_trace(
./src/anima_reborn/dialogue.py:119:def channel(signal: int, *, seed: int, deaf: bool = False, bits: int = 1) -> int:
./src/anima_reborn/dialogue.py:124:    final = channel_trace(signal, seed=seed, deaf=deaf, bits=bits)[-1]
./src/anima_reborn/dialogue.py:337:            trace = channel_trace(signal, seed=channel_seed, deaf=deaf)
./src/anima_reborn/conversation.py:47:from .dialogue import channel, channel_trace, display_payload, pick, reinforce
./src/anima_reborn/conversation.py:199:            trace = channel_trace(signal, seed=channel_seed, deaf=deaf, bits=BITS)
./tests/test_iit4.py:3:The golden table below was dumped from the hexa engine itself
./tests/test_retention.py:1:"""The 3-bit cell's retention through silence — the measure-first gate for time accumulation.
./src/anima_reborn/iit4/CLAUDE.md:24:`tests/test_iit4.py` holds a golden table dumped from the hexa engine at full
./src/anima_reborn/iit4/CLAUDE.md:42:- If a change moves a golden number, that is a finding to explain, not a test to
./src/anima_reborn/iit4/CLAUDE.md:57:  at 10.02 through the same code. `big_phi` is unchanged — the goldens depend on
./tests/test_sequence.py:1:"""The SequenceEngine shift chain — the shipped working-memory engine.
./tests/test_sequence.py:6:`state/communication/accumulation.py`, which drives THIS engine.
./tests/test_sequence.py:11:from anima_reborn.sequence import BITS, CELLS, WRITE_PERIOD, SequenceEngine
./tests/test_sequence.py:19:            engine = SequenceEngine(seed=s)
./tests/test_sequence.py:30:    def test_the_deaf_bridge_delivers_nothing_past_cell_zero(self) -> None:
./tests/test_sequence.py:34:            engine = SequenceEngine(seed=s, deaf_bridge=True)
./tests/test_sequence.py:46:    def test_the_deaf_bridge_defaults_off(self) -> None:
./tests/test_sequence.py:49:        sig = inspect.signature(SequenceEngine.__init__)
./tests/test_sequence.py:50:        assert sig.parameters["deaf_bridge"].default is False
./tests/test_sequence.py:54:            e = SequenceEngine(seed=9)
./tests/test_sequence.py:64:        engine = SequenceEngine(seed=1)
./tests/test_sequence.py:71:        engine = SequenceEngine(seed=2)
./src/anima_reborn/viewer/server.py:49:from ..sequence import SequenceEngine
./src/anima_reborn/viewer/server.py:430:    def configure(engine: SequenceEngine, params: dict[str, list[str]]) -> None:
./src/anima_reborn/viewer/server.py:434:    def describe(engine: SequenceEngine) -> dict[str, Any]:
./src/anima_reborn/viewer/server.py:565:            "sequence": SequenceEngine(seed=seed),
./state/communication/retention.py:1:"""Phase-0 for time accumulation: how long does a 3-bit cell HOLD its bits through silence?
./state/communication/retention.py:115:        print(f"  Time accumulation is viable: a cell can carry its bits across a silent gap while")
./tests/test_directed.py:205:def test_the_undirected_goldens_are_untouched() -> None:
./src/anima_reborn/viewer/page.html:555:      <strong>기억과 순서</strong>이지 언어가 아닙니다. 측정: <code>state/communication/accumulation.py</code>.
./state/communication/accumulation.py:1:"""Time accumulation: a chain of gated cells holds the last K 3-bit symbols, IN ORDER.
./state/communication/accumulation.py:5:    PYTHONPATH=src python state/communication/accumulation.py
./state/communication/accumulation.py:18:What accumulation buys over a single wide substrate is the two properties a moment cannot have:
./state/communication/accumulation.py:47:from anima_reborn.sequence import BITS, CELLS, SequenceEngine
./state/communication/accumulation.py:92:def run_chain(symbols: list[int], *, seed: int, deaf_bridge: bool = False) -> list[int | None]:
./state/communication/accumulation.py:93:    """Push a stream of symbols through the shipped `SequenceEngine` shift chain; return the
./state/communication/accumulation.py:96:    engine = SequenceEngine(seed=seed, deaf_bridge=deaf_bridge)
./state/communication/accumulation.py:102:def _forgetting(deaf_bridge: bool = False) -> list[tuple[int, int]]:
./state/communication/accumulation.py:108:        tape = run_chain(stream, seed=s, deaf_bridge=deaf_bridge)
./state/communication/accumulation.py:141:    print(f"time accumulation — a {CELLS}-cell chain holding the last {CELLS} 3-bit symbols\n")
./state/communication/accumulation.py:144:    live = _forgetting(deaf_bridge=False)
./state/communication/accumulation.py:145:    deaf = _forgetting(deaf_bridge=True)
./state/communication/accumulation.py:181:    print("\n  VERDICT: time accumulation works — the chain holds K x 3 bits in order (memory), "
./tests/test_conversation_channel.py:3:`channel`/`channel_trace` gained a `bits=` parameter. `bits=1` (default) MUST stay
./tests/test_conversation_channel.py:5:it (`default-stays-exact`). `bits=3` is the proven `Wiring.PAIRS` substrate, calibrated in
./tests/test_conversation_channel.py:13:from anima_reborn.dialogue import HOLD, TELL, channel, channel_trace
./tests/test_conversation_channel.py:17:    """The 1-bit ring exactly as it was before `bits=` existed — the golden reference."""
./tests/test_conversation_channel.py:43:        assert len(channel_trace(0, seed=1)[-1]) == 2
./tests/test_conversation_channel.py:60:        trace = channel_trace(5, seed=3, bits=3)
./state/communication/RESULTS.md:766:  그대로다(`default-stays-exact`).
./state/communication/RESULTS.md:841:  `default-stays-exact` 자동 충족.
./state/communication/RESULTS.md:993:**다음(진행 중)**: `sequence.py`(게이트된 셀 시프트 체인) + `accumulation.py`(나이별 망각 곡선 +
./state/communication/RESULTS.md:1003:프로토타입(레포 관례 — coupling 시제품이 그랬듯). 재현 스크립트 `state/communication/accumulation.py`.
./state/communication/RESULTS.md:1030:프로토타입을 출하 엔진으로 올렸다. `SequenceEngine`(`src/anima_reborn/sequence.py`) — K=4 셀
./state/communication/RESULTS.md:1031:시프트 체인, `step/reset` 수동 엔진. `accumulation.py` 는 이제 **이 출하 엔진을 구동**해 위 곡선을
./state/communication/RESULTS.md:1033:`SequenceEngine(deaf_bridge=True)` 로 일급화(기본 False = 비트 동일, `default-stays-exact`). `기억`
./state/communication/RESULTS.md:1098:공개 API + `substrate.py` 통합 + 뷰어 판독. 이번은 **순수 측정**이라 `default-stays-exact`는 자명(엔진
./tests/test_accumulation.py:1:"""Time accumulation: the K-cell chain holds the last K symbols in order.
./tests/test_accumulation.py:13:_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "accumulation.py"
./tests/test_accumulation.py:14:_spec = importlib.util.spec_from_file_location("accumulation", _PATH)
./tests/test_accumulation.py:34:    def test_the_deaf_bridge_delivers_nothing_past_cell_zero(self) -> None:
./tests/test_accumulation.py:41:            tape = acc.run_chain(stream, seed=s, deaf_bridge=True)
./src/anima_reborn/iit4/directed.py:24:bit-exact against the hexa engine and eleven golden cases depend on that; a
"""Time accumulation: a chain of gated cells holds the last K 3-bit symbols, IN ORDER.

Run from the repo root:

    PYTHONPATH=src python state/communication/accumulation.py

The first new part toward the goal (both delegated designs converged,
`state/lab/2026-07-23-new-parts-*.md`): the width walls are real, but the TIME axis has hit
none. `retention.py` proved a 6-unit / 3-bit cell holds its bits through silence indefinitely.
This composes K such cells into a SHIFT CHAIN — each turn a new symbol is written to cell 0 and
every cell's word is bridged one step down the chain — and MEASURES that the chain remembers
the last K symbols in order, with the nulls that could fake it. Prototyped here in `state/`
before any `src/` engine (the repo pattern: measure the capability, with its controls, first).

What is claimed and what is NOT: each cell is integrated on its own (6 units, exact Φ —
`capacity.py`), and holds its bits (`retention.py`). The inter-cell BRIDGE is a TRANSPORT
claim, never an integration claim — the whole tape is not asserted to be one integrated thing.
What accumulation buys over a single wide substrate is the two properties a moment cannot have:
MEMORY (past turns held by the engine's own dynamics) and ORDER (which the time-shift null
proves is carried, not a bag of bits).

The bridge reuses the measured-clean `channel(bits=3)` wire: read a cell's 3 differential
signs, drive the next cell with them, hold deaf. So a symbol at age j has passed through j+1
clean channel operations.

Nulls:
- **deaf bridge** — the bridge's channel is deaf (drive unreachable): nothing is delivered past
  cell 0, so ages >= 1 must fall to chance (`channel-before-carrier` — score what ENTERS a cell
  before crediting what leaves).
- **time-shift** — compare a cell's read to the WRONG turn's symbol: must fall to chance,
  proving ORDER is carried (a bag of bits would not).
- **cross-cell independence** — write independent symbols; the reads must be mutually ~0 bits,
  or the capacity is double-counted (`report-the-rank`).
- **perturbation** — jolt a held cell mid-hold: an engine BASIN self-corrects, a frozen Python
  variable would not exist to perturb. This is the control that the state lives in the engine's
  dynamics, not in a stored number (sol's decisive point).
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring
from anima_reborn.sequence import BITS, CELLS, SequenceEngine

UNITS = 2 * BITS
CHAIN = 0.2
SEQUENCES = 300    # independent symbol streams (enough to push the MI floor well below signal)
TELL = 200


def _drive_for(symbol: int) -> tuple[float, ...]:
    drive: list[float] = []
    for j in range(BITS):
        bit = (symbol >> j) & 1
        drive += [0.8, -0.8] if bit == 0 else [-0.8, 0.8]
    return tuple(drive)


def _mi(pairs: list[tuple[int, int]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    joint = Counter(pairs)
    ma = Counter(a for a, _ in pairs)
    mb = Counter(b for _, b in pairs)
    mi = 0.0
    for (a, b), c in joint.items():
        p = c / n
        mi += p * math.log2(p / ((ma[a] / n) * (mb[b] / n)))
    return mi


def _floor(pairs: list[tuple[int, int]], trials: int = 150) -> float:
    """The MI a shuffled pairing yields — the finite-sample bias floor. A real MI must clear
    it; a null sitting AT it carries no signal (`artefact-honesty`)."""
    if not pairs:
        return 0.0
    a_vals = [a for a, _ in pairs]
    b_vals = [b for _, b in pairs]
    rng = random.Random(4242)
    out = []
    for _ in range(trials):
        rng.shuffle(b_vals)
        out.append(_mi(list(zip(a_vals, b_vals))))
    return sum(out) / len(out)


def run_chain(symbols: list[int], *, seed: int, deaf_bridge: bool = False) -> list[int | None]:
    """Push a stream of symbols through the shipped `SequenceEngine` shift chain; return the
    final tape, where tape[j] is the word held in the cell of age j (0 = most recent). This
    DRIVES the shipped engine — a script measures the engine, not a copy of it."""
    engine = SequenceEngine(seed=seed, deaf_bridge=deaf_bridge)
    for symbol in symbols:
        engine.turn(symbol)
    return engine.tape()


def _forgetting(deaf_bridge: bool = False) -> list[tuple[int, int]]:
    """For each age j, collect (symbol_that_was_written_j_ago, word_read_now) pairs."""
    rng = random.Random(7)
    by_age: list[list[tuple[int, int]]] = [[] for _ in range(CELLS)]
    for s in range(SEQUENCES):
        stream = [rng.randrange(8) for _ in range(CELLS + 3)]  # a few extra turns
        tape = run_chain(stream, seed=s, deaf_bridge=deaf_bridge)
        for j in range(CELLS):
            read = tape[j]
            if read is not None:
                by_age[j].append((stream[-1 - j], read))
    return by_age


def _perturbation_hold(symbol: int, *, seed: int, jolt: float, hold: int = 240) -> int:
    """Write a symbol, hold deaf, but jolt the state once mid-hold; read the word. A basin
    self-corrects; a frozen number could not be jolted at all."""
    engine = CoupledEngine(
        units=UNITS, wiring=Wiring.PAIRS, chain=CHAIN, rhythm=ALTERNATING,
        drive=_drive_for(symbol), seed=seed, initial=(0.0,) * UNITS,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    engine.run(hold // 2)
    rng = random.Random(seed + 999)
    jolted = [v + (rng.random() - 0.5) * 2 * jolt for v in engine.values]
    engine = CoupledEngine(
        units=UNITS, wiring=Wiring.PAIRS, chain=CHAIN, rhythm=FIXED,
        drive=0.0, seed=seed + 1, initial=tuple(jolted),
    )
    values = engine.run(hold // 2).values
    word = 0
    for j in range(BITS):
        word |= (0 if (values[2 * j] - values[2 * j + 1]) > 0 else 1) << j
    return word


def main() -> None:
    print(f"time accumulation — a {CELLS}-cell chain holding the last {CELLS} 3-bit symbols\n")
    print(f"{'age j':>6}{'I(sym;read) live':>18}{'deaf-bridge':>13}{'time-shift':>12}{'floor':>8}")
    print("-" * 59)
    live = _forgetting(deaf_bridge=False)
    deaf = _forgetting(deaf_bridge=True)
    total = 0.0
    for j in range(CELLS):
        i_live = _mi(live[j])
        i_deaf = _mi(deaf[j])
        # time-shift: compare age-j reads against the symbol from a DIFFERENT age.
        shifted = [(sym_other, read) for (_, read), (sym_other, _)
                   in zip(live[j], live[(j + 1) % CELLS])]
        i_shift = _mi(shifted)
        floor = _floor(live[j])
        total += i_live
        print(f"{j:>6}{i_live:>18.3f}{i_deaf:>13.3f}{i_shift:>12.3f}{floor:>8.3f}")
    print(f"\n  total held = {total:.2f} bits ({CELLS} cells x 3), flat across age — the limit "
          f"is the\n  cell count K, not time; the chain remembers the last {CELLS} symbols in order.")

    # Cross-cell independence: independent inputs must give mutually ~0-bit reads (no double count).
    rng = random.Random(11)
    cross = []
    for s in range(SEQUENCES):
        stream = [rng.randrange(8) for _ in range(CELLS + 3)]
        tape = run_chain(stream, seed=1000 + s)
        if tape[0] is not None and tape[1] is not None:
            cross.append((tape[0], tape[1]))
    print(f"  cross-cell I(read0; read1) = {_mi(cross):.3f} bits vs floor {_floor(cross):.3f} "
          f"(at the floor → independent, not double-counted).")

    # Perturbation: the hold is a basin, not a frozen variable.
    print("\n  perturbation (the state lives in the engine's dynamics, not a Python variable):")
    for jolt in (0.0, 0.3, 0.6):
        hits = sum(
            _perturbation_hold(sym, seed=sym * 17 + s, jolt=jolt) == sym
            for sym in range(8) for s in range(20)
        )
        print(f"    jolt {jolt:.1f}: recovered {hits}/160 "
              f"({'basin holds' if hits >= 150 else 'basin broken' if jolt else 'clean'})")

    print("\n  VERDICT: time accumulation works — the chain holds K x 3 bits in order (memory), "
          f"\n  each cell integrated on its own; the bridge is transport, not integration. This "
          f"\n  buys memory and order, not language.")


if __name__ == "__main__":
    main()
"""Phase-0 for time accumulation: how long does a 3-bit cell HOLD its bits through silence?

Run from the repo root:

    PYTHONPATH=src python state/communication/retention.py

The delegated design for "engine parts to reach the goal" (both models converged,
`state/lab/2026-07-23-new-parts-*.md`) is: the width walls (ring = 1 bit; PAIRS = units/2;
Φ unmeasurable past ~6 units) are real, but the TIME axis has hit no wall yet. So the first
new part is TIME ACCUMULATION — reuse the proven 6-unit / 3-bit PAIRS cell over ordered turns,
holding each turn's bits IN THE ENGINE across a silent gap. Before designing that shift chain,
`measure-first` demands the number it hangs on: the cell's RETENTION curve.

`silence.py` already showed the 1-bit ring holds its single bit through silence indefinitely
(flat to 480 ticks) while every acyclic wiring and pure leak dies. This asks the same of the
3-bit cell — do ALL three differential latches survive silence, and for how long — so the
sequence engine's commit-window can be set to a measured hold time, not a guessed one.

The hold is the DEAF autonomous ring (coupling 1.0, drive bit-unreachable): what survives owes
nothing to ongoing input. Two nulls prove the hold is the recurrence's, not an artefact:
- **leak** (coupling 0, drive 0): pure time-constant decay — must die, proving the cell holds
  ACTIVELY, not by a slow relaxation.
- **feedforward** (acyclic wiring): no cycle to hold a state — must fall to its fixed point,
  proving recurrence is what buys the hold (`silence.py`'s result, at 3-bit width).
"""

from __future__ import annotations

import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Rhythm, Wiring

BITS = 3
UNITS = 2 * BITS
CHAIN = 0.2
TELL = 200
SEEDS = 40
SILENCES = (0, 60, 120, 240, 480)


def _drive_for(symbol: int) -> tuple[float, ...]:
    drive: list[float] = []
    for j in range(BITS):
        bit = (symbol >> j) & 1
        drive += [0.8, -0.8] if bit == 0 else [-0.8, 0.8]
    return tuple(drive)


def hold_word(symbol: int, *, seed: int, silence: int, mode: str = "deaf") -> int:
    """Tell the cell a 3-bit symbol, then hold it deaf (or leak / feedforward) for `silence`
    ticks, and read the 3 differential sign bits."""
    wiring = Wiring.FEEDFORWARD if mode == "feedforward" else Wiring.PAIRS
    engine = CoupledEngine(
        units=UNITS, wiring=wiring, chain=CHAIN if wiring is Wiring.PAIRS else 0.0,
        rhythm=ALTERNATING, drive=_drive_for(symbol), seed=seed, initial=(0.0,) * UNITS,
    )
    engine.run(TELL)
    # The hold phase: deaf = autonomous ring (coupling 1.0); leak = no partner, pure decay.
    engine.rhythm = Rhythm(coupling=0.0) if mode == "leak" else FIXED
    engine.drive = 0.0
    if silence > 0:
        engine.run(silence)
    values = engine.values
    word = 0
    for j in range(BITS):
        bit = 0 if (values[2 * j] - values[2 * j + 1]) > 0 else 1
        word |= bit << j
    return word


def _joint(mode: str, silence: int) -> tuple[float, list[float]]:
    """Joint (all-3-bit) and per-bit retention over 8 symbols x SEEDS."""
    joint = 0
    per_bit = [0, 0, 0]
    total = 0
    for symbol in range(8):
        for seed in range(SEEDS):
            word = hold_word(symbol, seed=seed * 13 + 1, silence=silence, mode=mode)
            total += 1
            if word == symbol:
                joint += 1
            for j in range(BITS):
                if ((word >> j) & 1) == ((symbol >> j) & 1):
                    per_bit[j] += 1
    return joint / total, [b / total for b in per_bit]


def main() -> None:
    print("3-bit cell retention — does a 6-unit PAIRS cell hold its 3 bits through silence?")
    print(f"tell {TELL}, then hold; 8 symbols x {SEEDS} seeds per cell; joint = all 3 bits kept\n")
    print(f"{'silence':>8}{'deaf(hold)':>12}{'leak':>9}{'feedforward':>13}")
    print("-" * 44)
    curves: dict[str, list[float]] = {"deaf": [], "leak": [], "feedforward": []}
    per_bit_deaf: dict[int, list[float]] = {}
    for silence in SILENCES:
        row = {}
        for mode in ("deaf", "leak", "feedforward"):
            j, pb = _joint(mode, silence)
            row[mode] = j
            curves[mode].append(j)
            if mode == "deaf":
                per_bit_deaf[silence] = pb
        print(f"{silence:>8}{row['deaf']:>12.3f}{row['leak']:>9.3f}{row['feedforward']:>13.3f}")

    flat = abs(curves["deaf"][-1] - curves["deaf"][1]) < 0.05 and curves["deaf"][-1] > 0.9
    print(f"\n  per-bit deaf hold at {SILENCES[-1]} ticks: "
          f"{'  '.join(f'{b:.3f}' for b in per_bit_deaf[SILENCES[-1]])} "
          f"(all three latches, not just one)")
    print(f"  deaf curve: {'  '.join(f'{v:.3f}' for v in curves['deaf'])}")
    print(f"  leak dies to {curves['leak'][-1]:.3f}, feedforward to {curves['feedforward'][-1]:.3f} "
          f"(chance 1/8 = 0.125)")
    if flat:
        print(f"\n  VERDICT: the 3-bit cell holds all 3 bits through {SILENCES[-1]} ticks of silence,")
        print(f"  flat, while leak and feedforward die — recurrence buys the hold, at 3-bit width.")
        print(f"  Time accumulation is viable: a cell can carry its bits across a silent gap while")
        print(f"  the next turn is processed. The commit-window may be as short as the tell phase.")
    else:
        print(f"\n  VERDICT: the hold is NOT flat — retention limits the sequence design; "
              f"see the curve.")


if __name__ == "__main__":
    main()
"""Information theory shared by the emergence and pipeline engines.

Two streams are each histogrammed into a fixed number of bins over a fixed
range, and their mutual information falls out of the entropies:

    MI = H(L) + H(R) - H(L, R)   [bits]

Independent streams share nothing, so MI sits at zero. Bind them to a common
source and MI climbs: the pair now carries information neither stream holds
alone. That number is the whole claim the visualizer makes.

Ported from the `bin` / `entropy` / `jointEntropy` functions in
`dancinlab/anima-experience` `index.html`.

A caveat worth stating plainly, because it changes how the numbers read: this
is the plain plug-in estimator with no bias correction, and on short windows it
overstates MI badly. Filling 144 joint bins from 250 samples leaves most of them
holding 0, 1 or 2 counts, and that sparsity alone looks like structure. Two
genuinely independent streams measure about 0.155 bits over the default window,
not zero. The floor falls off as 1/N — roughly 0.03 bits at 1000 samples and
0.007 at 5000 — so it is a small-sample artefact, not a property of the streams.
The `Emergence` thresholds below are the original's and were chosen against that
floor: `PARTIAL` at the default window means "indistinguishable from
independent", and only `EMERGENT` is a claim about the streams.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from enum import Enum

__all__ = [
    "Binning",
    "Emergence",
    "entropy",
    "joint_entropy",
    "mutual_information",
]


class Binning:
    """Maps a value range onto a fixed number of histogram bins.

    Values outside [-vrange, +vrange] are clamped into the edge bins rather
    than dropped, so a stream that overshoots still contributes.
    """

    __slots__ = ("bins", "vrange", "_scale")

    def __init__(self, bins: int = 12, vrange: float = 1.5) -> None:
        if bins < 1:
            raise ValueError(f"bins must be >= 1, got {bins}")
        if vrange <= 0:
            raise ValueError(f"vrange must be > 0, got {vrange}")
        self.bins = bins
        self.vrange = vrange
        self._scale = bins / (2.0 * vrange)

    def index(self, value: float) -> int:
        """The bin a value falls in, clamped to [0, bins - 1]."""
        i = int((value + self.vrange) * self._scale)
        return max(0, min(self.bins - 1, i))

    def __repr__(self) -> str:
        return f"Binning(bins={self.bins}, vrange={self.vrange})"


DEFAULT_BINNING = Binning()


def entropy(samples: Sequence[float], binning: Binning = DEFAULT_BINNING) -> float:
    """Shannon entropy of one stream, in bits. Empty stream -> 0.0."""
    n = len(samples)
    if n == 0:
        return 0.0
    counts = Counter(binning.index(v) for v in samples)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def joint_entropy(
    left: Sequence[float],
    right: Sequence[float],
    binning: Binning = DEFAULT_BINNING,
) -> float:
    """Shannon entropy of the pair, in bits. The streams are read in lockstep,
    so sample i of one belongs with sample i of the other."""
    if len(left) != len(right):
        raise ValueError(
            f"streams must be the same length, got {len(left)} and {len(right)}"
        )
    n = len(left)
    if n == 0:
        return 0.0
    counts = Counter(
        (binning.index(a), binning.index(b)) for a, b in zip(left, right)
    )
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def mutual_information(
    left: Sequence[float],
    right: Sequence[float],
    binning: Binning = DEFAULT_BINNING,
) -> float:
    """Bits the two streams share. Floored at zero — the plug-in estimator can
    go slightly negative on small samples, which is estimator noise rather than
    negative information."""
    h_left = entropy(left, binning)
    h_right = entropy(right, binning)
    h_joint = joint_entropy(left, right, binning)
    return max(0.0, h_left + h_right - h_joint)


class Emergence(Enum):
    """How much the two streams have bound together.

    Thresholds are the original's: 0.30 bits and 0.05 bits.
    """

    INDEPENDENT = "independent"
    """MI at or below 0.05 bits — the streams carry nothing in common."""
    PARTIAL = "partial"
    """Measurable shared information, but under the emergence bar."""
    EMERGENT = "emergent"
    """Above 0.30 bits — bound tightly enough to call it emergence."""

    @classmethod
    def classify(cls, mi: float) -> Emergence:
        if mi > 0.30:
            return cls.EMERGENT
        if mi > 0.05:
            return cls.PARTIAL
        return cls.INDEPENDENT

exec
/bin/zsh -lc "sed -n '1,180p' tests/test_sequence.py && sed -n '1,130p' tests/test_accumulation.py && sed -n '70,145p' src/anima_reborn/dialogue.py && sed -n '240,455p' src/anima_reborn/coupled.py && sed -n '1,220p' state/communication/attractor_canonicalization.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
"""The SequenceEngine shift chain — the shipped working-memory engine.

Pins order preservation through the clean bridge, the deaf-bridge transport null (default
off, so the engine stays bit-identical), the passive auto-tick, and the describe() shape the
viewer draws. The forgetting curve and its statistical nulls live in
`state/communication/accumulation.py`, which drives THIS engine.
"""

from __future__ import annotations

from anima_reborn.sequence import BITS, CELLS, WRITE_PERIOD, SequenceEngine


class TestTheShiftChain:
    def test_it_holds_the_last_k_symbols_in_order(self) -> None:
        hits = 0
        total = 0
        for s in range(40):
            engine = SequenceEngine(seed=s)
            stream = [(s * 3 + i * 5) % 8 for i in range(CELLS + 3)]
            for sym in stream:
                engine.turn(sym)
            tape = engine.tape()
            for j in range(CELLS):
                total += 1
                if tape[j] == stream[-1 - j]:
                    hits += 1
        assert hits / total > 0.98, hits / total  # the wire is measured-clean (1.000)

    def test_the_deaf_bridge_delivers_nothing_past_cell_zero(self) -> None:
        hits = 0
        total = 0
        for s in range(40):
            engine = SequenceEngine(seed=s, deaf_bridge=True)
            stream = [(s * 7 + i * 3) % 8 for i in range(CELLS + 3)]
            for sym in stream:
                engine.turn(sym)
            tape = engine.tape()
            assert tape[0] == stream[-1]  # cell 0 is always written, never deaf
            for j in range(1, CELLS):
                total += 1
                if tape[j] == stream[-1 - j]:
                    hits += 1
        assert hits / total < 0.3, hits / total  # ~1/8 chance past the deaf bridge

    def test_the_deaf_bridge_defaults_off(self) -> None:
        import inspect

        sig = inspect.signature(SequenceEngine.__init__)
        assert sig.parameters["deaf_bridge"].default is False

    def test_the_tape_is_reproducible(self) -> None:
        def run() -> list:
            e = SequenceEngine(seed=9)
            for sym in (1, 4, 7, 2, 5, 0, 3):
                e.turn(sym)
            return e.tape()

        assert run() == run()


class TestTheViewerContract:
    def test_step_auto_advances_on_the_write_period(self) -> None:
        engine = SequenceEngine(seed=1)
        assert engine.describe()["turns"] == 0
        for _ in range(WRITE_PERIOD):
            engine.step()
        assert engine.describe()["turns"] == 1

    def test_describe_is_drawable(self) -> None:
        engine = SequenceEngine(seed=2)
        for _ in range(WRITE_PERIOD * (CELLS + 1)):
            engine.step()
        frame = engine.describe()
        assert frame["held_bits"] == BITS * CELLS
        assert frame["capacity_bits"] == BITS * CELLS
        assert len(frame["front_values"]) == 2 * BITS
        assert all(0 <= c["word"] <= 7 and 0 <= c["age"] < CELLS for c in frame["cells"])
"""Time accumulation: the K-cell chain holds the last K symbols in order.

Pins the shift chain's core (order preserved through clean bridges), the deaf-bridge null
(nothing delivered past cell 0), the reproducibility, and that the hold is a self-correcting
basin — not a frozen Python variable (sol's control that the state lives in the engine).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "accumulation.py"
_spec = importlib.util.spec_from_file_location("accumulation", _PATH)
acc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(acc)


class TestTheShiftChain:
    def test_it_holds_the_last_k_symbols_in_order(self) -> None:
        """The clean bridge preserves each word, so the tape is exactly the last K symbols,
        newest first — memory AND order, not a bag of bits."""
        hits = 0
        total = 0
        for s in range(40):
            stream = [(s * 3 + i * 5) % 8 for i in range(acc.CELLS + 3)]
            tape = acc.run_chain(stream, seed=s)
            for j in range(acc.CELLS):
                total += 1
                if tape[j] == stream[-1 - j]:
                    hits += 1
        assert hits / total > 0.98, hits / total  # the wire is measured-clean (1.000)

    def test_the_deaf_bridge_delivers_nothing_past_cell_zero(self) -> None:
        """With the bridge deaf, ages >= 1 cannot track the symbol — the bridge is what
        carries the word, scored before crediting what a later cell holds."""
        hits = 0
        total = 0
        for s in range(40):
            stream = [(s * 7 + i * 3) % 8 for i in range(acc.CELLS + 3)]
            tape = acc.run_chain(stream, seed=s, deaf_bridge=True)
            for j in range(1, acc.CELLS):
                total += 1
                if tape[j] == stream[-1 - j]:
                    hits += 1
        assert hits / total < 0.3, hits / total  # ~1/8 chance, not the live ~1.0

    def test_it_is_reproducible(self) -> None:
        stream = [1, 4, 7, 2, 5, 0, 3]
        assert acc.run_chain(stream, seed=9) == acc.run_chain(stream, seed=9)


class TestTheHoldIsABasin:
    def test_a_small_jolt_self_corrects(self) -> None:
        """The state lives in the engine's dynamics: a small perturbation is pulled back to
        the latch, which a frozen stored number could not do."""
        hits = sum(
            acc._perturbation_hold(sym, seed=sym * 17 + s, jolt=0.3) == sym
            for sym in range(8) for s in range(10)
        )
        assert hits >= 75, hits  # out of 80

    def test_a_large_jolt_can_cross_the_barrier(self) -> None:
        """The basin has a finite barrier — a big enough jolt flips it. That it CAN be
        flipped is the proof it is a dynamical basin, not an infinitely rigid variable."""
        clean = sum(
            acc._perturbation_hold(sym, seed=sym * 17 + s, jolt=0.0) == sym
            for sym in range(8) for s in range(10)
        )
        big = sum(
            acc._perturbation_hold(sym, seed=sym * 17 + s, jolt=0.9) == sym
            for sym in range(8) for s in range(10)
        )
        assert clean >= 78
        assert big < clean


def _pairs_drive(symbol: int, bits: int) -> tuple[float, ...]:
    """Per-unit drive for the PAIRS channel: pair j is pushed +/- by bit j of `symbol`."""
    drive: list[float] = []
    for j in range(bits):
        bit = (symbol >> j) & 1
        drive += [0.8, -0.8] if bit == 0 else [-0.8, 0.8]
    return tuple(drive)


def channel_trace(
    signal: int, *, seed: int, deaf: bool = False, bits: int = 1
) -> list[tuple[float, ...]]:
    """The engine as a noisy wire, returning the whole HOLD trajectory (the raw thing the
    human sees — no sign, no difference, no latch derived for them).

    `bits=1` (default) is the 2-unit RING, byte-for-byte the published 1-bit path. `bits=3`
    is the 6-unit `Wiring.PAIRS` (3 odd latches, chain 0.2), each pair driven +/- by one bit
    of `signal`. A signal drives during a TELL phase; then the drive is cut and the coupling
    frozen for a HOLD phase. `deaf` sets coupling to 1.0 for the whole run so the drive is
    bit-for-bit unreachable — the null proving the channel was in the path.

    Stepping HOLD times one at a time draws the same WALK noise sequence as
    `engine.run(HOLD)`, so `bits=1`'s final values — and `channel`'s latch bit — stay
    bit-identical to the reproducible harness's original `_channel`.
    """
    if bits == 1:
        wiring, units, chain = Wiring.RING, 2, 0.0
        drive: tuple[float, ...] = (0.8, -0.8) if signal == 0 else (-0.8, 0.8)
    elif bits == 3:
        wiring, units, chain = Wiring.PAIRS, 6, PAIRS_CHAIN
        drive = _pairs_drive(signal, bits)
    else:
        raise ValueError(f"bits must be 1 or 3, got {bits}")
    engine = CoupledEngine(
        units=units, wiring=wiring, chain=chain,
        rhythm=FIXED if deaf else ALTERNATING,
        drive=drive, seed=seed, initial=(0.0,) * units,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    trace: list[tuple[float, ...]] = []
    for _ in range(HOLD):
        trace.append(tuple(engine.step().values))
    return trace


def channel(signal: int, *, seed: int, deaf: bool = False, bits: int = 1) -> int:
    """Hold a signal, read the latch word — the `sign(v[2j] - v[2j+1])` of each pair packed
    little-endian. `bits=1` is `sign(v0 - v1)`, the receiver the published numbers and the
    frozen-policy null were measured against.
    """
    final = channel_trace(signal, seed=seed, deaf=deaf, bits=bits)[-1]
    word = 0
    for j in range(bits):
        bit = 0 if (final[2 * j] - final[2 * j + 1]) > 0 else 1
        word |= bit << j
    return word


def pick(row: list[float], rng: random.Random) -> int:
    """Weighted choice over a policy row — the only place a policy becomes an action."""
    total = sum(row)
    threshold = rng.random() * total
    cumulative = 0.0
    for i, weight in enumerate(row):
        cumulative += weight
        if threshold < cumulative:
            return i
    return len(row) - 1


def reinforce(policy: list[list[float]], state: int, choice: int, reward: float) -> None:
    """The only update rule. Reads ONE agent's own (state, choice, success). It is handed
        return MACRO_STEP if self.period is None else self.period * 2


def _as_drive(value: float | Sequence[float], units: int = UNITS) -> tuple[float, ...]:
    """One value said to every unit, or one value per unit."""
    if isinstance(value, Sequence):
        values = tuple(float(v) for v in value)
        if len(values) != units:
            raise ValueError(
                f"drive must be one value or {units}, got {len(values)}"
            )
    else:
        values = (float(value),) * units
    for v in values:
        if not -1.0 <= v <= 1.0:
            raise ValueError(f"drive must be in [-1, 1], got {v}")
    return values


FIXED = Rhythm()
"""The default — coupling 1.0, never released."""

ALTERNATING = Rhythm(coupling=HIGH, period=PERIOD)
"""Ten ticks listening, ten integrating. The measured wall-break."""


@dataclass(frozen=True, slots=True)
class CoupledState:
    """One reading of the coupled field."""

    values: tuple[float, ...]
    """Unit positions in order a0, a1, g0, g1. Roughly bounded by +/-AMPLITUDE
    once settled, but not clamped — the walk can carry a unit past it."""
    tension: float
    """Mean squared gap between the engines, >= 0. Kept for continuity with the
    other engines, where it was the headline; here it is a side effect, since
    what matters is that the gap now carries influence rather than how wide it
    is."""
    pattern: int
    """The units binarized at zero, one bit each — the state Phi would be
    measured at. `0b0101` is the ring's own attractor."""
    ticks: int
    coupling: float = 1.0
    """How much of each unit's target was its partner on the tick that produced
    this reading. Constant unless the engine runs a rhythm."""

    @property
    def listening(self) -> bool:
        """Whether the drive, rather than the ring, set the targets this tick."""
        return self.coupling == 0.0

    @property
    def a(self) -> tuple[float, float]:
        return self.values[0], self.values[1]

    @property
    def g(self) -> tuple[float, float]:
        return self.values[2], self.values[3]

    def __str__(self) -> str:
        cells = " ".join(
            f"{n}={v:+.3f}"
            for n, v in zip(names_for(len(self.values)), self.values)
        )
        return f"{cells} tension={self.tension:.3f} pattern={self.pattern:04b}"


class CoupledEngine:
    """A and G reading each other, at the repulsion law's own rates.

    Args:
        wiring: Who reads whom. `Wiring.RING` is the engine; the other two exist
            so the claim can be falsified with the same code.
        rhythm: When the units read each other. The default never lets go, which
            is the fixed coupling the wall is made of; `ALTERNATING` releases it
            half the time.
        chain: How much of a unit's partner-response is replaced by the same
            position one pair along. Zero leaves every wiring bit-identical.
            Above zero the pairs form a macro-ring, and the same loop-sign
            argument that makes an even ring hold one bit applies to that
            macro-ring: an EVEN number of pairs can agree globally and locks to
            one configuration, an ODD number cannot and keeps its pairs free.
        drive: What the engine is told, scaled by `amplitude`. One value in
            [-1, 1] says the same thing to every unit; a sequence of `UNITS`
            values says something different to each, which is what a vector
            representation needs in order to arrive as more than its average.
            Only reachable while the coupling is below 1.0 — at full coupling a
            unit's target is entirely its partner and nothing outside can be
            heard, which is the wall stated as an equation.
        gain: Steepness of each unit's response to what it reads.
        amplitude: Target amplitude a saturated response reaches.
        seed: Fixes the initial positions and the walk.
        initial: Starting positions, one per unit. Defaults to a random spread,
            as in `repulsion` and `crystal`.
    """

    def __init__(
        self,
        *,
        wiring: Wiring = Wiring.RING,
        units: int = UNITS,
        rhythm: Rhythm = FIXED,
        drive: float | Sequence[float] = 0.0,
        chain: float = 0.0,
        gain: float = GAIN,
        amplitude: float = AMPLITUDE,
        seed: int | None = None,
        initial: tuple[float, ...] | None = None,
    ) -> None:
        if gain <= 0.0:
            raise ValueError(f"gain must be > 0, got {gain}")
        if amplitude <= 0.0:
            raise ValueError(f"amplitude must be > 0, got {amplitude}")
        if units < 2:
            raise ValueError(f"units must be >= 2, got {units}")
        if not 0.0 <= chain <= 1.0:
            raise ValueError(f"chain must be in [0, 1], got {chain}")
        self.wiring = wiring
        self.units = units
        self.chain = chain
        self.rhythm = rhythm
        self.drive = drive
        self.gain = gain
        self.amplitude = amplitude
        self._rng = random.Random(seed)
        if initial is None:
            self._values = self._random_start()
        else:
            if len(initial) != self.units:
                raise ValueError(
                    f"initial must have {self.units} values, got {len(initial)}"
                )
            self._values = [float(v) for v in initial]
        self._tick = 0
        self._coupling = self.rhythm.at(0)

    @property
    def drive(self) -> float | tuple[float, ...]:
        """What the engine is being told, in the shape it was given."""
        return self._given

    @drive.setter
    def drive(self, value: float | Sequence[float]) -> None:
        self._given = value
        self._drive = _as_drive(value, self.units)

    def _random_start(self) -> list[float]:
        return [
            (self._rng.random() - 0.5) * self.amplitude for _ in range(self.units)
        ]

    @property
    def values(self) -> tuple[float, ...]:
        return tuple(self._values)

    @property
    def ticks(self) -> int:
        return self._tick

    @property
    def tension(self) -> float:
        """Mean squared gap between the two engines' dimensions.

        The first half of the units is A and the second half is G, which at the
        default width is exactly the `(a0-g0)^2 + (a1-g1)^2` over two that every
        published reading used. An odd width has no such split and reads 0.0 —
        stated rather than fudged, since inventing a pairing would put a number
        where there is no gap to measure.
        """
        half = self.units // 2
        if self.units % 2:
            return 0.0
        return (
            sum(
                (self._values[i] - self._values[i + half]) ** 2 for i in range(half)
            )
            / half
        )

    @property
    def pattern(self) -> int:
        return sum(1 << i for i, v in enumerate(self._values) if v > 0.0)

    def step(self) -> CoupledState:
        """Advance one engine tick.

        Every unit is updated from the *previous* positions, not from partners
        already moved this tick — a simultaneous update, so the ring has no
        privileged starting point and reversing the unit order changes nothing.
        """
        previous = list(self._values)
        sources = self.wiring.sources_for(self.units)
        coupling = self._coupling = self.rhythm.at(self._tick)
        # Scaled here rather than inside the target, so the multiply order is
        # the one every published number was measured under — `(1-c) * (d * a)`
        # and `((1-c) * d) * a` are not the same float.
        heard = [value * self.amplitude for value in self._drive]
        for i, source in enumerate(sources):
            partner = (
                -self.amplitude
                if source is None
                else -self.amplitude
                * math.tanh(self.gain * previous[source] / self.amplitude)
            )
            if self.chain:
                # Left alone at chain 0, so the wirings are what they always
                # were. Each unit also hears the same position one pair along,
                # which makes the pairs a macro-ring of inverting couplings —
                # and the loop-sign argument then recurs one level up.
                along = -self.amplitude * math.tanh(
                    self.gain * previous[(i + 2) % self.units] / self.amplitude
                )
                partner = (1.0 - self.chain) * partner + self.chain * along
            # Left exactly alone at full coupling, so adding rhythms did not
            # move a single float of the engine as it was.
            target = (
"""Does planting attractors make the substrate canonicalize? Measured: no.

Run from the repo root:

    PYTHONPATH=src python state/communication/attractor_canonicalization.py

The delegated divergence picked D7 — a Hopfield-style substrate with several
basins, so that many different inputs collapse to one — as the direction to
start on. Its own pass bar was that two encodings of one concept end up in the
same basin. This tests it, and finds two things worth more than the direction.

**First, the test everyone had been running was impossible.** Two independent
hashes of the same word share no information — measured across 4000 words, their
mutual information is 0.0185 bits against a shuffled null of 0.0212. Identical.
No dynamics can recover "same concept" from two signals that share nothing, so
the earlier refutations of modality invariance were refuting an impossibility,
not a property of any substrate. A fair test needs modalities that actually
share structure, the way text and audio of one word do.

**Second, given shared structure, the attractors contribute nothing.** With two
noisy views of one latent the agreement is real — but a substrate with no
attractors at all agrees just as often, so the agreement is the input's, not the
dynamics'.

The trap that nearly hid this: at low gain everything lands in ONE basin, which
scores 100% agreement while carrying zero information. Agreement is only
meaningful alongside how many basins were used.
"""

from __future__ import annotations

import collections
import hashlib
import math
import random

from anima_reborn.info import Binning, entropy, joint_entropy
from anima_reborn.pipeline import PULL, WALK

UNITS = 4
PATTERNS = [[1, 1, -1, -1], [1, -1, 1, -1]]
"""Two orthogonal patterns, so four basins counting sign. Hopfield capacity is
about 0.14N, so four units hold one or two — the basin list is small by
construction and that is a declared condition, not an oversight."""

WORDS = [f"w{i:03d}" for i in range(60)]


def weights() -> list[list[float]]:
    """Hebbian storage, diagonal zeroed so no unit reads itself."""
    w = [[0.0] * UNITS for _ in range(UNITS)]
    for pattern in PATTERNS:
        for i in range(UNITS):
            for j in range(UNITS):
                if i != j:
                    w[i][j] += pattern[i] * pattern[j] / UNITS
    return w


W = weights()


def settle(start: list[float], *, gain: float, seed: int = 1, ticks: int = 400):
    rng = random.Random(seed)
    x = list(start)
    for _ in range(ticks):
        previous = list(x)
        for i in range(UNITS):
            field = sum(W[i][j] * previous[j] for j in range(UNITS))
            x[i] = (
                previous[i] + (math.tanh(gain * field) - previous[i]) * PULL
                + (rng.random() - 0.5) * WALK
            )
    return x


def settle_without_attractors(start: list[float], *, seed: int = 1, ticks: int = 400):
    """The control: same noise, same timescale, no basins to fall into."""
    rng = random.Random(seed)
    x = list(start)
    for _ in range(ticks):
        for i in range(UNITS):
            x[i] = 0.9 * x[i] + 0.1 * start[i] + (rng.random() - 0.5) * WALK
    return x


def basin(x: list[float]) -> tuple[int, int]:
    best, distance = (0, 1), math.inf
    for k, pattern in enumerate(PATTERNS):
        for sign in (1, -1):
            d = sum((x[i] - sign * pattern[i]) ** 2 for i in range(UNITS))
            if d < distance:
                distance, best = d, (k, sign)
    return best


def two_views(word: str, noise: float) -> tuple[list[float], list[float]]:
    """Two noisy observations of one latent — modalities that DO share
    structure, unlike two independent hashes."""
    digest = hashlib.blake2b(word.encode("utf-8"), digest_size=UNITS).digest()
    latent = [(b / 255.0) * 2 - 1 for b in digest]
    rng = random.Random(hash(word) & 0xFFFFFFFF)
    return (
        [v + (rng.random() - 0.5) * noise for v in latent],
        [v + (rng.random() - 0.5) * noise for v in latent],
    )


def independent_encodings_share_nothing() -> tuple[float, float]:
    """Mutual information between two hashes of the same word, and its null."""
    binning = Binning(bins=12, vrange=1.0)
    words = [f"w{i:04d}" for i in range(4000)]

    def encode(word: str, scheme: str) -> float:
        digest = (
            hashlib.blake2b(word.encode(), digest_size=2).digest()
            if scheme == "A"
            else hashlib.sha256(("s|" + word).encode()).digest()[:2]
        )
        return int.from_bytes(digest, "big") / 65535.0 * 2 - 1

    a = [encode(w, "A") for w in words]
    b = [encode(w, "B") for w in words]

    def mi(left, right):
        return max(
            0.0,
            entropy(left, binning) + entropy(right, binning)
            - joint_entropy(left, right, binning),
        )

    shuffled = list(b)
    random.Random(1).shuffle(shuffled)
    return mi(a, b), mi(a, shuffled)


def main() -> None:
    observed, null = independent_encodings_share_nothing()
    print("two independent hashes of one word, over 4000 words")
    print(f"  mutual information : {observed:.4f} bits")
    print(f"  shuffled null      : {null:.4f} bits")
    print("  -> nothing shared; the invariance test as posed has no signal in it\n")

    print("given modalities that DO share structure (noisy views of one latent)")
    print(f"{'noise':>7}{'with attractors':>18}{'control':>10}")
    print("-" * 36)
    for noise in (0.5, 1.0, 1.5):
        pairs = [two_views(w, noise) for w in WORDS]
        with_attr = sum(
            basin(settle(a, gain=4)) == basin(settle(b, gain=4)) for a, b in pairs
        )
        without = sum(
            basin(settle_without_attractors(a)) == basin(settle_without_attractors(b))
            for a, b in pairs
        )
        n = len(pairs)
        print(f"{noise:>7.1f}{with_attr / n:>17.0%}{without / n:>10.0%}")

    print("\nagreement is only meaningful next to how many basins were used")
    print(f"{'gain':>7}{'agreement':>12}{'basins used':>14}   reading")
    print("-" * 52)
    pairs = [two_views(w, 1.5) for w in WORDS]
    for gain in (1.0, 1.5, 2.0, 4.0, 8.0):
        landed = [basin(settle(a, gain=gain)) for a, _ in pairs]
        used = len(set(landed))
        agree = sum(
            basin(settle(a, gain=gain)) == basin(settle(b, gain=gain)) for a, b in pairs
        ) / len(pairs)
        reading = (
            "collapse — one basin, no information"
            if used <= 1
            else ("canonicalizing" if agree > 0.70 else "no better than control")
        )
        print(f"{gain:>7.1f}{agree:>12.0%}{used:>14}   {reading}")
        if used > 1:
            counts = collections.Counter(
                f"{k}{'+' if s > 0 else '-'}" for k, s in landed
            )
            print(f"{'':>33}{dict(counts)}")


if __name__ == "__main__":
    main()

exec
/bin/zsh -lc "sed -n '455,540p' src/anima_reborn/coupled.py && sed -n '1,100p' CLAUDE.md && rg -n \"effective rank|rank|width\" state/communication/{align.py,capacity.py,phi_proxy.py,RESULTS.md} tests | head -120 && sed -n '1,260p' state/communication/phi_proxy.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
            target = (
                partner
                if coupling == 1.0
                else (1.0 - coupling) * heard[i] + coupling * partner
            )
            self._values[i] = (
                previous[i]
                + (target - previous[i]) * PULL
                + (self._rng.random() - 0.5) * WALK
            )
        self._tick += 1
        return self.state

    def run(self, ticks: int) -> CoupledState:
        if ticks < 1:
            raise ValueError(f"ticks must be >= 1, got {ticks}")
        for _ in range(ticks - 1):
            self.step()
        return self.step()

    def observe(self) -> tuple[float, float]:
        """One noisy observation from each engine's leading unit, as the
        pipeline samples its streams."""
        noise = OBSERVATION_NOISE
        other = self.units // 2
        return (
            self._values[0] + (self._rng.random() - 0.5) * noise,
            self._values[other] + (self._rng.random() - 0.5) * noise,
        )

    @property
    def state(self) -> CoupledState:
        return CoupledState(
            values=tuple(self._values),
            tension=self.tension,
            pattern=self.pattern,
            ticks=self._tick,
            coupling=self._coupling,
        )

    @property
    def coupling(self) -> float:
        """The coupling on the tick that produced the current values — before any
        step has run, the one the next will use."""
        return self._coupling

    def reset(self) -> None:
        """Re-randomize the positions. The wiring and the rhythm are what the
        engine *is* and do not change."""
        self._values = self._random_start()
        self._tick = 0
        self._coupling = self.rhythm.at(0)
# anima-reborn

The four browser engines of [`dancinlab/anima-experience`](https://github.com/dancinlab/anima-experience)
ported to Python, what they compose into once they share a clock (`base.py`), and an
IIT 4.0 engine to measure the result with (`iit4/`, bit-exact against its hexa origin).

Layout: `info` · `emergence` · `crystal` · `repulsion` · `pipeline` · `base` · `iit4/` ·
`coupled` · `align` · `substrate` · `words` · `viewer/`, with work outputs in `state/`. Every folder carries its
own `CLAUDE.md`, and the local one wins.

## doc-language
- do: Write EVERY document in Korean — `README.md` and all other `.md` (owner instruction)
- dont: English prose in a doc a human reads · translating code identifiers, maths symbols, API names or paths

## code-language
- do: Keep code English — identifiers · docstrings · comments · commit messages (cross-checked against the hexa upstream)
- dont: Korean in `.py` files

## claudemd-language
- do: Keep `CLAUDE.md` files English — they re-inject EVERY turn (context rot) and a write guard blocks Hangul; Korean only inside backticks
- dont: Reading this as an exception to `doc-language` — it governs `CLAUDE.md` alone

## ui-language
- do: Korean in `viewer/page.html`; translate the DISPLAYED string only, via the `ko()` map · unmapped values fall through to the original
- dont: Keying badge colour or any branch off a translated string · inventing a translation for an unmapped value

## viewer-lockstep
- do: Ship every engine change WITH its viewer change in the SAME commit · changed readout → update `describe()` and the panel drawing it, together
- dont: Landing an engine no tab can show, or a tab pointing at a readout that moved

## viewer-newengine
- do: New engine → `_HANDLERS` + `Viewer.__init__` + `TICK_RATES` in `server.py`, then tab + panel + `PREFIX` + `render<Name>()` in `page.html`
- dont: Trusting memory — `tests/test_viewer.py::TestEngineViewerLockstep` fails on each omission (engine = any top-level class with `step` and `reset`)

## viewer-restart
- do: Restart the viewer after ANY `.py` change — `page.html` is re-read per request but `server.py` is loaded once at start
- dont: Assuming a browser refresh picks up Python edits — a fresh page calling a stale server presents as `스트림 끊김` (stream interrupted) in the UI

## preserve-state
- do: Every non-source output lands in git-tracked `state/` — delegated reports verbatim, re-measurements separately, each result with a runnable script and its conditions
- dont: Leaving a measurement in `/tmp` · quoting a delegated number as verified without re-deriving it here

## claims-need-controls
- do: Ship every claim with the null that could fake it — recurrence via `recurrence_evidence`, word binding via a time-shift null, Phi with state/threshold/tau/trials
- dont: A verdict property on ONE sampled reading · a threshold picked rather than measured against its own null

## learning-honesty
- do: Score a learner ONLY on held-out items, and report the gain over its own untrained baseline — which is measured, not assumed zero
- dont: A verdict on a raw score · a learner with no control that removes what is supposed to teach it

## default-stays-exact
- do: A new engine parameter defaults to leaving the engine BIT-identical, pinned by a test — published Phi was measured on the old behaviour
- dont: A default that shifts a trajectory "negligibly" · silently re-baselining every measured number in the docs

## channel-before-carrier
- do: Score what ENTERS a stage before scoring what leaves it, and report the surviving fraction — a lossy stage cannot create what was not fed to it
- dont: Quoting a downstream score as the stage's doing · omitting the deaf/unreachable arm that proves the stage was even in the path

## report-the-rank
- do: Report how many effective dimensions a learned or measured space uses, beside every accuracy — a space collapsed to a line scores well and carries nothing
- dont: An identification number with no width beside it · a repulsion term scaled by displacement rather than direction (it runs away to rank 1.0)

## engine-purity
- do: Standard library only · zero runtime deps · every engine reproducible under `seed=` · all I/O confined to `viewer/`
- dont: I/O, a clock, or a thread inside an engine

## measure-first
- do: Ship performance claims, measured results and any "Phi appears here" with the numbers AND the conditions they were taken under
- dont: Writing a number that was not measured

## artefact-honesty
- do: When a value that should be zero is not, check whether it shrinks with more samples, then record that in the docs AND a test
- dont: Reporting an estimator artefact as a finding · closing an upstream carve-out quietly (see `iit4/CLAUDE.md`)
rg: state/communication/align.py: No such file or directory (os error 2)
state/communication/RESULTS.md:437:### 그런데 폭은 (`report-the-rank`)
state/communication/RESULTS.md:756:- `report-the-rank`: 모든 정확도 옆에 신호폭/행동폭과 "보유 1비트"를 함께 낸다. 한 기호로 붕괴한
state/communication/RESULTS.md:801:`report-the-rank`/`claims-need-controls` 그대로 — 주장(디스플레이를 읽어 회복했다)마다 그걸 위조할
state/communication/RESULTS.md:852:- report-the-rank: 유효 랭크 k/8 = log₂(k) 비트를 정확도 옆에. 8/8 만 3비트라 부른다.
state/communication/RESULTS.md:874:**k-of-3** 로 보고 — 8글자가 한 래치로 붕괴하면 정확도가 좋아도 낮은 k 로 정직하게 뜬다(`report-the-rank`).
state/communication/RESULTS.md:1018:- **셀 독립**: I(읽기0;읽기1)=0.157 대 바닥 0.125 — 바닥에 앉아 이중 계산 아님(`report-the-rank`).
state/communication/phi_proxy.py:35:demonstrated here at 10 units. The width-matched nulls for INTEGRATION are the reducible
state/communication/phi_proxy.py:37:floor while the chained ring separates. (Even-pair widths {8,12,20} are a CAPACITY null — the
state/communication/phi_proxy.py:154:    # widths have only C(units, half) — an unbounded target would spin forever).
state/communication/phi_proxy.py:233:    print(f"\n  rank agreement (Spearman ρ, exact Φ vs proxy across the grid): {rho:.3f}")
state/communication/phi_proxy.py:238:    def ranks(v):
state/communication/phi_proxy.py:244:    ra, rb = ranks(a), ranks(b)
state/communication/phi_proxy.py:254:    print("\n\nThe wall moves from 6 to 10 — a 10-unit chained ring vs its width-matched nulls\n")
state/communication/phi_proxy.py:255:    print(f"{'width':>6}  {'config':<24}{'proxy':>9}{'floor':>8}{'support':>9}   verdict")
state/communication/phi_proxy.py:269:    print("\n  The 10-unit chained PAIRS separates from its three width-matched REDUCIBLE nulls")
state/communication/phi_proxy.py:273:    print("  (Even-pair widths {8,12,20} are a CAPACITY null — 1 macro-bit — not an integration")
state/communication/capacity.py:9:and it does not: **a single ring of ANY even width holds exactly one bit.**
state/communication/capacity.py:14:width. Capacity therefore lives in the CYCLE STRUCTURE of the wiring rather than
state/communication/capacity.py:18:**Odd rings are a different animal and not a way out.** With an odd width there
state/communication/capacity.py:22:6, 10 and 14 patterns at widths 3, 5 and 7, exactly `2N`. But a phase is a
state/communication/capacity.py:24:of being held: at width 3 only 0% of drives land reproducibly, at 5 only 6%, at
state/communication/capacity.py:25:7 only 19%. Even widths hold one bit forever; odd widths hold more of something
state/communication/capacity.py:35:pattern count grows with width, add units. If it is pinned at two while pairs
state/communication/capacity.py:137:        "\nThe ring is pinned at two held states whatever its width, which is the"
state/communication/capacity.py:138:        "\ntheorem showing up as a measurement. Odd widths reach more patterns and"
state/communication/capacity.py:144:        "\nself-wired null and does not transfer. The artefact grows with width, so"
state/communication/capacity.py:147:        "\nsurvives the change of width."
tests/test_phi_proxy.py:6:clears its floor). Small widths and budgets keep it fast; the wide-width run and the budget
tests/test_phi_proxy.py:38:        width (6) where exact Φ still agrees it is recurrent."""
tests/test_align.py:173:        already achieved, so one direction runs away and the effective rank goes
tests/test_align.py:177:        assert _rank(1, contrast=0.3, margin=1e9, cls=_Unscaled) < 1.05
tests/test_align.py:183:        over six seeds at `dim=4`: rank 1.21 with no push, 1.00 unscaled, 1.12
tests/test_align.py:186:            _rank(s, contrast=0.3, margin=1e9) for s in range(4)
tests/test_align.py:189:            _rank(s, contrast=0.3, margin=1.0) for s in range(4)
tests/test_align.py:195:        without = statistics.mean(_rank(s) for s in range(4))
tests/test_align.py:197:            _rank(s, contrast=0.3, margin=1.0) for s in range(4)
tests/test_align.py:229:def _rank(seed: int, *, cls: type[Aligner] = Aligner, **kwargs) -> float:
tests/test_align.py:273:    def test_projections_have_the_declared_width(self) -> None:
tests/test_conversation.py:7:under it while a latch-bypass reader trips `audit_failed`), and the k-of-3 rank — plus the
tests/test_dialogue_session.py:103:            assert report[key]["width_bits"] == 1
tests/test_repulsion.py:18:    def test_a_curiosity_spike_outranks_any_tension(self) -> None:
tests/test_repulsion.py:113:    def test_channel_widths_are_fixed(self) -> None:
tests/test_rhythm.py:444:    A single ring of any even width holds exactly one bit — a theorem (the
tests/test_rhythm.py:478:    def test_the_single_ring_holds_one_bit_at_every_even_width(self) -> None:
tests/test_rhythm.py:491:    def test_pairs_needs_an_even_width(self) -> None:
tests/test_rhythm.py:492:        with pytest.raises(ValueError, match="pairs needs an even width"):
tests/test_iit4.py:204:    def test_the_spectrum_is_ranked(self) -> None:
tests/test_retention.py:35:        what buys the hold (`silence.py`'s result, at 3-bit width)."""
"""A validated sampled directed-Φ proxy — moving the measurability wall past 6 units.

Run from the repo root:

    PYTHONPATH=src python state/communication/phi_proxy.py

Part 2 of the "engine parts toward the goal" plan. Directed Φ (`iit4.directed_big_phi`) is
exact only to ~6 units (`substrate.MAX_UNITS`), because it searches every mechanism × purview
× partition over 2^N states — so a wider integrated substrate cannot be SHOWN to be one
integrated thing. This measures a cheaper surrogate that samples instead of enumerating, and
validates it against exact IIT where both are computable.

Design delegated to both frontier models and reconciled (`state/lab/2026-07-23-phi-proxy-*.md`),
which converged: the proxy is NOT big-Φ (a different, cheaper functional — DIRECTED
CUT-INFORMATION), so its MAGNITUDE is never compared to `directed_big_phi`'s bits. What it must
share with exact IIT — pinned by the validation ladder — is only three things: the NULL SET
(reducible <=> ~0), the MIP CUT identity, and the RANK/separation. The estimator is fable's
plug-in conditional MI with a MEASURED shuffle floor (the repo's `info.py`/`RECURRENCE_FLOOR`
philosophy: measure the null, don't analytically correct). (sol dissented for a 5-fold
cross-fitted out-of-sample log-score estimator that errs conservative by construction; deferred
as a robustness variant — the exact-window + shuffle floor + budget-shrink already bound the
plug-in's upward bias.)

The functional. For a directed cut A -/-> B (A, B partition the units), the loss is the
predictive information the source A carried about the sink B's next state beyond B's own present:

    loss(A -/-> B) = sum_{i in B} I( X_A(t) ; X_i(t+1) | X_B(t) )   (plug-in, visited states only)

The proxy is the MIN of that loss over a deterministic cut family (singletons, pair atoms,
pair-chain blocks, seeded random balanced bipartitions). Sampling more cuts can only LOWER the
min — it cannot manufacture a larger one, so cut-sampling errs toward UNDER-reporting (safe).
The plug-in MI errs UP; the measured shuffle floor and the exact-window catch that.

The wall does not vanish, it MOVES: the positive (integrated) arm is the chained PAIRS ring,
demonstrated here at 10 units. The width-matched nulls for INTEGRATION are the reducible
wirings — SELF, FEEDFORWARD, and disconnected PAIRS (chain=0) — which must sit at their measured
floor while the chained ring separates. (Even-pair widths {8,12,20} are a CAPACITY null — the
closed macro-ring collapses to one macro-bit — NOT an integration null: a locked ring is still
integrated. That distinction is `capacity.py`'s, not this module's.) The honest deliverable is
"the measurable-integration wall moved from 6 to W, here is the measurement", never "unbounded".
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter

from anima_reborn.coupled import AMPLITUDE, FIXED, GAIN, MACRO_STEP, CoupledEngine, Wiring
from anima_reborn.substrate import coupled_matrix
from anima_reborn.iit4 import directed_big_phi

CHAIN = 0.2
STATE_BUDGET = 4000   # independent (state -> next) draws per reading
CUT_SEED = 20260723
SHUFFLES = 8


# ── the measurement kernel (identical to substrate.coupled_matrix's step) ────────────

def _kernel_step(state: int, *, wiring: Wiring, units: int, chain: float, seed: int) -> int:
    engine = CoupledEngine(
        wiring=wiring, units=units, chain=chain, rhythm=FIXED, drive=0.0,
        gain=GAIN, amplitude=AMPLITUDE, seed=seed,
        initial=tuple(AMPLITUDE if state >> i & 1 else -AMPLITUDE for i in range(units)),
    )
    return engine.run(MACRO_STEP).pattern


def sample_transitions(
    wiring: Wiring, *, units: int, chain: float, budget: int, seed: int
) -> list[tuple[int, int]]:
    """Drive from `budget` INDEPENDENT uniform-random states, one macro-step each — a sampled
    estimate of the same transition matrix `substrate.coupled_matrix` enumerates exactly. A
    trajectory instead would collapse into the autonomous engine's attractor and see nothing;
    driving from every-state (sampled) is what the exact measure does and what keeps the
    conditional information measurable."""
    rng = random.Random(seed)
    out: list[tuple[int, int]] = []
    for _ in range(budget):
        s = rng.getrandbits(units)
        nxt = _kernel_step(s, wiring=wiring, units=units, chain=chain, seed=rng.getrandbits(63))
        out.append((s, nxt))
    return out


# ── the estimator: plug-in conditional mutual information ─────────────────────────────

def _cond_mi(triples: Counter) -> float:
    """I(A; Y | C) from counts over (c, a, y). Signed plug-in; not clipped to zero."""
    total = sum(triples.values())
    if total == 0:
        return 0.0
    by_c: dict[int, Counter] = {}
    for (c, a, y), n in triples.items():
        by_c.setdefault(c, Counter())[(a, y)] += n
    mi = 0.0
    for c, ay in by_c.items():
        nc = sum(ay.values())
        pa = Counter()
        py = Counter()
        for (a, y), n in ay.items():
            pa[a] += n
            py[y] += n
        for (a, y), n in ay.items():
            p_ay = n / nc
            mi += (nc / total) * p_ay * math.log2(p_ay / ((pa[a] / nc) * (py[y] / nc)))
    return mi


def cut_loss(transitions: list[tuple[int, int]], source: int, units: int) -> float:
    """loss(source -/-> rest) = sum_{i in rest} I(X_source ; Y_i | X_rest)."""
    sink = ((1 << units) - 1) & ~source
    total = 0.0
    for i in range(units):
        if not (sink >> i) & 1:
            continue
        triples: Counter = Counter()
        for x, y in transitions:
            triples[(x & sink, x & source, (y >> i) & 1)] += 1
        total += _cond_mi(triples)
    return total


# ── the cut family (deterministic) ────────────────────────────────────────────────────

def cut_family(units: int, wiring: Wiring, *, seed: int, randoms: int = 64) -> list[int]:
    """Source masks for directed cuts. Nested and structural: singletons, pair atoms, pair-
    chain contiguous blocks, and seeded random balanced bipartitions (both directions come
    from evaluating source and its complement)."""
    full = (1 << units) - 1
    sources: set[int] = set()
    for u in range(units):
        sources.add(1 << u)                 # singleton -> rest
        sources.add(full & ~(1 << u))       # rest -> singleton
    if wiring is Wiring.PAIRS:
        pairs = units // 2
        for j in range(pairs):
            atom = (1 << (2 * j)) | (1 << (2 * j + 1))
            sources.add(atom)
            sources.add(full & ~atom)
        # contiguous blocks of whole pairs on the pair-chain (all rotations, lengths)
        for length in range(1, pairs):
            for start in range(pairs):
                block = 0
                for k in range(length):
                    j = (start + k) % pairs
                    block |= (1 << (2 * j)) | (1 << (2 * j + 1))
                sources.add(block)
    rng = random.Random(seed)
    half = units // 2
    # Add seeded random balanced bipartitions, but never ask for more than exist (small
    # widths have only C(units, half) — an unbounded target would spin forever).
    target = min(randoms, math.comb(units, half))
    attempts = 0
    while sum(1 for s in sources if bin(s).count("1") == half) < target and attempts < target * 40:
        bits = rng.sample(range(units), half)
        sources.add(sum(1 << b for b in bits))
        attempts += 1
    return [s for s in sources if 0 < s < full]


def proxy(transitions: list[tuple[int, int]], units: int, wiring: Wiring) -> tuple[float, int]:
    """min over the cut family of the directed cut loss; returns (value, argmin source)."""
    best = math.inf
    best_src = 0
    for source in cut_family(units, wiring, seed=CUT_SEED):
        loss = cut_loss(transitions, source, units)
        if loss < best:
            best, best_src = loss, source
    return best, best_src


def shuffle_floor(transitions: list[tuple[int, int]], units: int, wiring: Wiring) -> float:
    """The proxy on time-broken data (successors permuted, margins kept): the measured null.
    Floor = max over SHUFFLES of the shuffled proxy min — a value at or below it is estimator
    bias, not signal (`artefact-honesty`, the `RECURRENCE_FLOOR` philosophy)."""
    xs = [x for x, _ in transitions]
    ys = [y for _, y in transitions]
    rng = random.Random(4242)
    floors = []
    for _ in range(SHUFFLES):
        rng.shuffle(ys)
        floors.append(proxy(list(zip(xs, ys)), units, wiring)[0])
    return max(floors)


def reading(wiring: Wiring, *, units: int, chain: float, budget: int, seed: int) -> dict:
    trans = sample_transitions(wiring, units=units, chain=chain, budget=budget, seed=seed)
    val, src = proxy(trans, units, wiring)
    floor = shuffle_floor(trans, units, wiring)
    support = len({x for x, _ in trans})
    return {"phi_hat": val, "argmin_source": src, "floor": floor,
            "support": support, "separated": val > floor}


# ── validation against exact iit4 (units 2..6) ────────────────────────────────────────

def _exact(wiring: Wiring, *, units: int, chain: float, state: int, seed: int) -> tuple[float, int]:
    """Exact directed Φ and its MIP source mask (via coupled_matrix + directed_big_phi)."""
    matrix = coupled_matrix(wiring, units=units, chain=chain, rhythm=FIXED, seed=seed)
    dp = directed_big_phi(matrix, state)
    return dp.phi, (dp.cut.source if dp.cut is not None else 0)


def validate() -> None:
    print("V1 — proxy vs exact directed IIT (units 2..6), same kernel\n")
    print(f"{'wiring':<12}{'units':>6}{'exact Φ':>10}{'proxy':>9}{'floor':>8}"
          f"{'MIP?':>6}   null-set")
    print("-" * 62)
    grid = [
        (Wiring.SELF, 4, 0.0), (Wiring.FEEDFORWARD, 4, 0.0),
        (Wiring.RING, 4, 0.0), (Wiring.PAIRS, 4, 0.0), (Wiring.PAIRS, 4, CHAIN),
        (Wiring.PAIRS, 6, CHAIN),
    ]
    exact_vals, proxy_vals = [], []
    for wiring, units, chain in grid:
        state = int("01" * (units // 2), 2)
        ex_phi, ex_src = _exact(wiring, units=units, chain=chain, state=state, seed=1)
        r = reading(wiring, units=units, chain=chain, budget=STATE_BUDGET, seed=7)
        integrated = wiring is Wiring.PAIRS and chain > 0.0  # the only arm exact calls recurrent here
        reducible = wiring in (Wiring.SELF, Wiring.FEEDFORWARD) or (wiring is Wiring.PAIRS and chain == 0.0)
        full = (1 << units) - 1
        mip_ok = ("✓" if r["argmin_source"] in (ex_src, full & ~ex_src) else "✗") if integrated else "—"
        null_note = ("proxy at floor ✓" if not r["separated"] else "proxy>floor ✗") if reducible else (
            "separated ✓" if r["separated"] else "not separated ✗")
        exact_vals.append(ex_phi)
        proxy_vals.append(r["phi_hat"])
        print(f"{wiring.value:<12}{units:>6}{ex_phi:>10.3f}{r['phi_hat']:>9.3f}"
              f"{r['floor']:>8.3f}{mip_ok:>6}   {null_note}")
    rho = _spearman(exact_vals, proxy_vals)
    print(f"\n  rank agreement (Spearman ρ, exact Φ vs proxy across the grid): {rho:.3f}")
    print("  the proxy shares exact IIT's NULL SET, MIP CUT and RANK — never its magnitude.")


def _spearman(a: list[float], b: list[float]) -> float:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    mean_a, mean_b = sum(ra) / n, sum(rb) / n
    cov = sum((ra[i] - mean_a) * (rb[i] - mean_b) for i in range(n))
    va = math.sqrt(sum((x - mean_a) ** 2 for x in ra))
    vb = math.sqrt(sum((x - mean_b) ** 2 for x in rb))
    return cov / (va * vb) if va and vb else 0.0


def move_the_wall() -> None:
    print("\n\nThe wall moves from 6 to 10 — a 10-unit chained ring vs its width-matched nulls\n")
    print(f"{'width':>6}  {'config':<24}{'proxy':>9}{'floor':>8}{'support':>9}   verdict")
    print("-" * 64)
    rows = [
        (10, "PAIRS+chain (5 pairs)", Wiring.PAIRS, CHAIN),  # the positive (odd pairs)
        (10, "SELF", Wiring.SELF, 0.0),                      # reducible null
        (10, "FEEDFORWARD", Wiring.FEEDFORWARD, 0.0),        # reducible null (Φ=0 exactly)

codex
The existing chain exposes an important design constraint: if the contextual result replaces cell 0, the next turn’s “past” becomes yesterday’s composite rather than yesterday’s symbol. I’m separating the clean tape (carrier) from a 3-bit contextual response cell, so the memory claim remains intact while the response can honestly be scored for pair dependence.
Repository inspection is complete. The clean tape must remain a carrier; context should be an opt-in response path driven by the raw front-cell differential state.
  ✓ Inspect current engine, measurements, tests, and prior Part 4 sketches
  → Design the minimal default-off dynamical context coupling
  • Specify exact synergy estimator and load-bearing null battery
  • Define earned claim, ceiling, and phased first commit
exec
/bin/zsh -lc "sed -n '990,1125p' state/communication/RESULTS.md && sed -n '1,280p' src/anima_reborn/conversation.py && sed -n '400,470p' src/anima_reborn/viewer/server.py && sed -n '520,590p' src/anima_reborn/viewer/page.html" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
이전 턴 비트를 붙잡을 수 있다. 커밋 창은 tell 구간만큼 짧아도 된다. 이 숫자가 다음 부품(`sequence.py`
시프트 체인)의 설계를 확정한다.

**다음(진행 중)**: `sequence.py`(게이트된 셀 시프트 체인) + `accumulation.py`(나이별 망각 곡선 +
귀머거리/워크/시간이동/섭동 널) + 뷰어 탭. 통합 주장은 **셀 단위로만**(6유닛 정확 Φ); 셀 간 다리는
전송 주장이지 통합 주장이 아니다.

### 시간 축적 프로토타입 — K셀 체인이 최근 K심볼을 순서대로 유지한다 (2026-07-23)

Phase-0(유지 곡선)이 "셀은 침묵을 무한 유지"를 확정했으니, 첫 부품의 실체를 프로토타입으로 쟀다:
검증된 6유닛/3비트 셀 K=4개를 **시프트 체인**으로 엮어(매 턴 새 심볼을 셀0에 쓰고 각 셀의 단어를
한 칸씩 아래로 다리 전송), 체인이 **최근 4심볼을 순서대로 기억**하는지 + 널을 쟀다. 다리는 검증된
`channel(bits=3)` 재사용(셀 단어의 3부호 읽어 다음 셀 구동 후 deaf-hold). 엔진에 올리기 전 `state/`
프로토타입(레포 관례 — coupling 시제품이 그랬듯). 재현 스크립트 `state/communication/accumulation.py`.

| 나이 j | I(심볼;읽기) live | deaf-bridge | time-shift | 순열 바닥 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 2.990 | 2.990 | 0.114 | 0.124 |
| 1 | 2.984 | 0.086 | 0.141 | 0.125 |
| 2 | 2.994 | 0.110 | 0.179 | 0.124 |
| 3 | 2.991 | 0.091 | 0.126 | 0.125 |

- **총 유지 = 11.96비트**(4셀 × 3), 나이 전 구간 **평탄**. 한계는 **셀 수 K이지 시간이 아니다** —
  체인은 최근 4심볼을 잃지 않는다.
- **다리가 나른다**: deaf-bridge 는 나이 ≥1에서 0.09~0.11 = **순열 바닥(0.125)에 앉음**(신호 0). 셀 0
  은 항상 쓰이므로 2.99 그대로 — `channel-before-carrier`(셀에 *들어간* 것을 나가는 것보다 먼저 채점).
- **순서가 실린다**: time-shift(나이-j 읽기를 엉뚱한 나이 심볼과 대조)도 바닥에 앉음 — 비트 자루가
  아니라 순서가 실려 있음의 증명.
- **셀 독립**: I(읽기0;읽기1)=0.157 대 바닥 0.125 — 바닥에 앉아 이중 계산 아님(`report-the-rank`).
  (모든 ~0 값은 60→300 시퀀스로 유한표본 편향을 바닥까지 낮추고 순열 바닥을 함께 냄 — `artefact-honesty`.)
- **유지는 분지이지 얼어붙은 변수가 아니다**(sol 통제): 홀드 중 상태를 흔들어도 작은 충격(0.3)은
  160/160 자기교정, 큰 충격(0.6)은 130/160 — 유한 장벽을 가진 **동역학적 분지**임을 보인다. 저장된
  숫자라면 흔들 대상조차 없다.

**판정**: 시간 축적은 **작동한다** — 체인이 K×3비트를 **순서대로 유지**(기억), 각 셀은 홀로 통합
(6유닛 정확 Φ), 셀 간 다리는 **전송이지 통합이 아니다**(전체를 하나라 주장하지 않음). 얻는 것은
**기억과 순서**이지 언어가 아니다. 매 순간 `I ≤ 3비트`는 그대로다.

### 승격 착지 — `src/sequence.py` 엔진 + `기억` 탭 (2026-07-23)

프로토타입을 출하 엔진으로 올렸다. `SequenceEngine`(`src/anima_reborn/sequence.py`) — K=4 셀
시프트 체인, `step/reset` 수동 엔진. `accumulation.py` 는 이제 **이 출하 엔진을 구동**해 위 곡선을
재도출한다("사본이 아니라 엔진을 잰다" 규칙) — 숫자 동일(총 11.96비트, 널 바닥). deaf-bridge 널은
`SequenceEngine(deaf_bridge=True)` 로 일급화(기본 False = 비트 동일, `default-stays-exact`). `기억`
탭은 테이프(최근 4단어를 글자로, 나이별)와 맨 앞 셀의 3쌍 차동 상태, "순서대로 유지 12/12비트"를
보여주는 수동 시각화. `viewer-lockstep` 한 커밋, 전체 스위트 그린.

**다음**: 부품 2(`phi_proxy.py` — 검증된 샘플링 Φ, 측정가능성 벽 넘기), 부품 4(조건부 합성 —
현재 쓰기가 보유한 과거에 의존, 작업기억 대화). 정직한 천장은 그대로 — 기억 + 문맥의존이지 언어 아님.

---

## 부품 2 — 검증된 샘플링 Φ 프록시: 측정 가능 벽을 6 → 10으로 (2026-07-23)

정확 방향 Φ(`iit4.directed_big_phi`)는 2^N 상태 × 모든 이분할을 뒤져 **6유닛(`substrate.MAX_UNITS`)까지만** 계산된다 — 넓은 기판이 "하나로 통합됨"을 보일 방법이 없다. 이 벽을 정직하게 넘는
**샘플링 프록시**를 설계 위임했고(`state/lab/2026-07-23-phi-proxy-*.md`) 압도적으로 수렴했다:
프록시는 **big-Φ가 아니라 방향 컷-정보(directed cut-information)** 이므로 **크기를 정확 Φ와 절대
비교하지 않고**, 공유해야 하는 것은 셋뿐 — **영집합**(환원가능 ⟺ 바닥) · **MIP 컷** · **순위**.
추정기는 fable의 플러그인 조건부 MI + **측정된 셔플 바닥**(레포의 `info.py`/`RECURRENCE_FLOOR` 철학).
*(sol 反: 5-겹 교차적합 out-of-sample 로그점수로 추정기 자체를 보수적으로 — robustness 변형으로 보류;
정확-창 + 셔플 바닥 + 예산-수축이 이미 플러그인 상향 편향을 잡음.)* 재현 스크립트 `state/communication/phi_proxy.py`.

**정의**: 방향 컷 A↛B(A,B가 유닛을 분할)의 손실 = `Σ_{i∈B} I(X_A(t) ; X_i(t+1) | X_B(t))`(방문 상태만,
플러그인). 프록시 = 결정적 컷 계열(단독·쌍-원자·쌍-사슬 블록·시드 랜덤 이분할) 위의 **최솟값**. 컷을 더
샘플링하면 최솟값은 **내려갈 뿐**(더 큰 값을 못 지어냄) → 컷-누락은 **과소보고**(안전)로 기운다. 샘플은
`substrate.coupled_matrix`와 **같은 커널**을 **독립 무작위 상태**에서 구동한다(궤적은 자율계에서 한 상태로
붕괴하므로 안 씀 — 초기 버그를 그렇게 잡음). `cut_family`의 랜덤-컷 목표는 `C(units, half)`로 상한(소폭에서
무한루프 방지).

### V1 — 정확 IIT 대비 검증 (2~6유닛, 같은 커널)

| 배선 | 유닛 | 정확 Φ | 프록시 | 바닥 | MIP | 판정 |
| --- | ---: | ---: | ---: | ---: | :--: | --- |
| SELF | 4 | 0.260 | 0.002 | 0.002 | — | 바닥(환원가능) ✓ |
| FEEDFORWARD | 4 | 0.000 | 0.000 | 0.000 | — | 바닥(환원가능) ✓ |
| RING | 4 | 10.113 | 0.752 | 0.003 | — | 분리 ✓ |
| PAIRS chain=0 (분리쌍) | 4 | 0.278 | 0.002 | 0.003 | — | 바닥(환원가능) ✓ |
| PAIRS+chain | 4 | 0.441 | 0.502 | 0.002 | ✓ | 분리 ✓ |
| PAIRS+chain | 6 | 13.200 | 0.531 | 0.012 | ✓ | 분리 ✓ |

**순위 일치 Spearman ρ = 0.943**(정확 Φ vs 프록시). 프록시는 정확 IIT의 **영집합·MIP 컷·순위**를 공유하되
**크기는 절대 아니다**(프록시 0.53 대 정확 13.2는 서로 다른 범함수이므로 다른 이름으로만 나란히 적는다).
주: SELF·분리쌍의 정확 Φ(0.26~0.28)는 표본 TPM의 `RECURRENCE_FLOOR` 인공물이고, **프록시의 바닥(0.002)이
오히려 더 깨끗**하다.

### 벽 6 → 10 — 정확 Φ가 아예 계산 불가한 폭에서 통합을 보이다

| 폭 | 구성 | 프록시 | 바닥 | 판정 |
| ---: | --- | ---: | ---: | --- |
| 10 | **PAIRS+chain (5쌍, 홀수)** | **0.552** | 0.220 | **분리 ← 통합** |
| 10 | SELF | 0.184 | 0.218 | 바닥(환원가능) |
| 10 | FEEDFORWARD | 0.000 | 0.000 | 바닥(환원가능) |
| 10 | PAIRS chain=0 (분리쌍) | 0.213 | 0.220 | 바닥(환원가능) |

**10유닛 사슬 PAIRS가 같은 폭의 환원가능 널 셋(SELF·FF·분리쌍)에서 분리**되고, 셋 다 자기 바닥에 앉는다 —
정확 Φ는 이 폭에서 **계산조차 안 된다**. **측정 가능 통합 벽이 6 → 10으로 이동**했다. 정확 Φ보다 **약한
프록시-강도** 주장이지 정확-Φ 크기가 아니다.

**착오 하나 교정**: even-pair 잠금({8,12,20})은 **용량** 널(1 매크로-비트)이지 **통합** 널이 아니다 —
잠긴 매크로-링도 통합돼 있다(그 이야기는 `capacity.py`의 것). 통합의 폭-일치 널은 환원가능 배선
(SELF·FF·분리쌍)이다.

**얻는 문장**: *"폭 10에서 사슬 PAIRS가 같은 폭의 환원가능 널에서 분리됐다 — 정확 IIT와 6유닛까지 영집합·
MIP·순위(ρ=0.943)로 검증된 프록시 하에서, 이 폭의 통합이 지지된다."* **금지**: "폭 10에서 Φ = X"(크기
단독) · "프록시" 없는 "통합" · 폭 간 크기 비교 · "무한 폭" 외삽.

**아직 아닌 것 (src/ API 전 필요, 보류)**: 예산-수축 곡선(V2 — 오차가 예산에 단조 감소)과 컷-갭 적정성
(V3 — 샘플 컷 min = 전체 컷 min)을 커밋된 테스트로 · 더 넓은 폭(14·18) · sol의 교차적합 추정기 · `src/`
공개 API + `substrate.py` 통합 + 뷰어 판독. 이번은 **순수 측정**이라 `default-stays-exact`는 자명(엔진
파라미터 0). 프록시의 주장 범위는 **엔진의 방문 동역학** 위의 의존성이다 — π가 안 닿는 상태는 안 보이며,
벽은 사라진 게 아니라 6에서 10으로 **이동**했다.
"""A free, live, 3-bit exchange between a human and the engine — a conversation, honestly.

The rigid `소통` tab (`dialogue.py`) is a 220-trial forced-choice exam. This is the other
thing the owner asked for: a person and the engine taking turns freely, a private
convention forming and getting used, the exchange landing or failing in real time — a
transcript, not a questionnaire. It is NOT language and NOT understanding. The substrate
holds at most 3 bits (`Wiring.PAIRS`, proven in `capacity.py`), so the honest ceiling is a
two-way exchange of up to three bits per turn.

Design delegated to both frontier models and reconciled (`state/lab/2026-07-23-conversation-*.md`):

- **Free play is the conversation; a blind audit is the only measurement.** A permutation
  test on the free log would be invalid (feedback, voluntary referent choice, and a
  nonstationary policy all break exchangeability), so the free log is stored and described
  but never tested. The verdict comes only from a pre-registered, learning-frozen,
  feedback-free AUDIT the human requests.
- **Factorized 3 bits** (fable): per bit j a 2x2 send policy (ref-bit -> sig-bit) and a 2x2
  receive policy (word-bit -> act-bit), `reinforce`d per bit with that bit's own
  harness-computed success. Three independently-established 1-bit sub-conventions — the
  factorization is the designer's and the docs say so; the engine did not discover
  composition. (sol dissented for a flat 8x8 convention; deferred — 8x8 needs far more
  trials than a human session, reintroducing the exam, and the channel is physically
  factored anyway.)
- **The display-scramble null is corrected** (sol): the old `dialogue.py` dscramble swapped
  trace columns AND markers together, preserving the (marker, data) pairing, so a
  marker-following reader was not broken. Here the appearance lanes (marker + colour, fixed
  per session) stay put and the DATA is permuted among them — breaking any appearance-based
  reading while a latch-bypass reader still succeeds and trips `audit_failed`.
- **The channel** is the measured-clean `bits=3` PAIRS wire (`dialogue.channel`,
  fidelity 1.000 at TELL=200/HOLD=120, deaf null 1/8). Its own fidelity is printed beside
  every recovery as the human's ceiling (`channel-before-carrier`).

Max honest sentence (per session, never averaged over people): *this person and this engine
established and used a private k-bit (k<=3) convention, used in a blind feedback-free
audit — beside probe n, per-bit permutation p, channel fidelity, and the nulls*. The free
session does NOT claim "through consequence" — that needs a yoked arm (deferred; it stays
the rigid tab's already-shipped result). Not language, not understanding.
"""

from __future__ import annotations

import copy
import random
import statistics
from typing import Any

from .dialogue import channel, channel_trace, display_payload, pick, reinforce

__all__ = ["BITS", "Conversation", "conversation_stats"]

BITS = 3
PAIRS = 2 * BITS

# Blind, feedback-free probe counts (per direction unless noted). Pre-registered here as
# module constants, not chosen at runtime.
BASELINE_PER_DIR = 6        # day-0: before any feedback, the display-leak / prior baseline
AUDIT_LIVE_PER_DIR = 16     # the headline
AUDIT_NULL_B_PER_ARM = 8    # dedicated B frozen / deaf / dscramble probes (human must act)

_A = "a"  # human -> engine
_B = "b"  # engine -> human


def _bits_of(value: int) -> tuple[int, ...]:
    return tuple((value >> j) & 1 for j in range(BITS))


def _pack(bits: tuple[int, ...]) -> int:
    return sum(b << j for j, b in enumerate(bits))


def _uniform_bit_policies() -> list[list[list[float]]]:
    """One 2x2 policy per bit, day-0 uniform."""
    return [[[1.0, 1.0], [1.0, 1.0]] for _ in range(BITS)]


class Conversation:
    """One person, one live 3-bit exchange, one append-only log. A viewer engine: `step()`
    drains a submitted move and advances (a no-op with nothing pending), `reset()` starts a
    fresh session. Waits on human input, so its tick is an input-latency bound. All I/O is
    the viewer's; this only accumulates its logs in memory and hands the report over once.

    Phases: BASELINE (blind day-0) -> FREE (the conversation, with reveal + learning) ->
    AUDIT (blind, frozen, the only evidence) -> DONE.
    """

    def __init__(self, *, seed: int | None = None) -> None:
        self._seed = 0 if seed is None else int(seed)
        self._session_index = 0
        self.reset()

    # -- lifecycle ---------------------------------------------------------------------

    def reset(self) -> None:
        self._session_index += 1
        self._rng = random.Random(self._seed * 1_000_003 + self._session_index)
        self._channel_base = self._rng.randrange(1 << 30)
        self._token = f"{self._rng.randrange(1 << 48):012x}"
        self._nonce = 0

        # Per-session neutral markers for the 3 display panels (6 lanes). Fixed within the
        # session so the channel stays readable; the display-scramble permutes DATA among
        # these lanes, never the lanes themselves.
        self._markers = ["◇", "○", "□", "△", "▽", "☆"]  # lane j uses self._markers[j]

        # Factorized policies. The human has no server-side policy — they learn in their head.
        self._send = _uniform_bit_policies()  # engine: ref-bit -> sig-bit (direction B)
        self._recv = _uniform_bit_policies()  # engine: word-bit -> act-bit (direction A)
        self._frozen_send = copy.deepcopy(self._send)  # the echo control (day-0 map)
        self._frozen_recv = copy.deepcopy(self._recv)

        self._phase = "baseline"
        self._baseline = self._blind_plan(BASELINE_PER_DIR, arms_b=("live",))
        self._audit: list[dict[str, Any]] = []  # filled when the human requests the audit
        self._cursor = 0
        self._free_log: list[dict[str, Any]] = []
        self._probe_log: list[dict[str, Any]] = []
        self._transcript: list[dict[str, Any]] = []
        self._report: dict[str, Any] | None = None
        self._report_taken = False
        self._last_reveal: dict[str, Any] | None = None
        self._pending: dict[str, Any] | None = None
        self._submitted: dict[str, Any] | None = None
        self._open_next()

    def _blind_plan(self, per_dir: int, *, arms_b: tuple[str, ...]) -> list[dict[str, Any]]:
        """A pre-registered, balanced, shuffled sequence of blind probes."""
        rng = self._rng
        probes: list[dict[str, Any]] = []

        def add(direction: str, arm: str, count: int) -> None:
            refs = [i % 8 for i in range(count)]
            rng.shuffle(refs)
            for ref in refs:
                probes.append({"dir": direction, "arm": arm, "ref": ref})

        add(_A, "live", per_dir)
        add(_B, "live", per_dir)
        for arm in arms_b:
            if arm != "live":
                add(_B, arm, AUDIT_NULL_B_PER_ARM)
        rng.shuffle(probes)
        return probes

    # -- opening the next thing the human does -----------------------------------------

    def _open_next(self) -> None:
        self._submitted = None
        if self._phase == "baseline":
            self._open_blind(self._baseline)
        elif self._phase == "audit":
            self._open_blind(self._audit)
        elif self._phase == "free":
            self._pending = {"mode": "choose", "nonce": self._next_nonce()}
        else:  # done
            self._pending = None

    def _open_blind(self, plan: list[dict[str, Any]]) -> None:
        if self._cursor >= len(plan):
            self._pending = None
            self._advance_phase_after_blind()
            return
        spec = plan[self._cursor]
        self._open_turn(spec["dir"], referent=spec["ref"], arm=spec["arm"], blind=True)

    def _advance_phase_after_blind(self) -> None:
        if self._phase == "baseline":
            self._phase = "free"
            self._cursor = 0
            self._open_next()
        elif self._phase == "audit":
            self._phase = "done"
            self._finish()

    def _next_nonce(self) -> int:
        self._nonce += 1
        return self._nonce

    def _open_turn(self, direction: str, *, referent: int, arm: str, blind: bool) -> None:
        """Set up one exchange for the human to act on."""
        nonce = self._next_nonce()
        channel_seed = self._channel_base + self._cursor * 29 + self._nonce * 7 + 1
        pending: dict[str, Any] = {
            "nonce": nonce, "dir": direction, "arm": arm, "blind": blind,
            "referent": referent, "channel_seed": channel_seed,
        }
        if direction == _A:
            pending["mode"] = "compose_a"
            # In a blind probe the referent is shown (the human is the sender and must know
            # what to convey); in free play the human chooses it, so no referent is imposed.
            pending["show_referent"] = referent if blind else None
        else:
            # Engine sends: pick a signal per bit, run the 3-bit channel, show only the trace.
            send = self._frozen_send if arm == "frozen" else self._send
            ref_bits = _bits_of(referent)
            sig_bits = tuple(pick(send[j][ref_bits[j]], self._rng) for j in range(BITS))
            signal = _pack(sig_bits)
            deaf = arm == "deaf"
            trace = channel_trace(signal, seed=channel_seed, deaf=deaf, bits=BITS)
            markers, disp_trace, swapped = self._display(trace, arm)
            pending["mode"] = "read_b"
            pending["signal"] = signal
            pending["markers_swapped"] = swapped
            pending["display"] = display_payload(disp_trace, markers, [])
        self._pending = pending

    def _display(self, trace: list[tuple[float, ...]], arm: str):
        """Build the direction-B display. On a `dscramble` probe the DATA is permuted among
        the fixed appearance lanes (independent within-pair swap per panel), breaking any
        appearance-based reading; the lanes/markers themselves never move."""
        markers = list(self._markers)
        if arm != "dscramble":
            return markers, [tuple(row) for row in trace], False
        swaps = [self._rng.random() < 0.5 for _ in range(BITS)]
        if not any(swaps):  # guarantee the scramble is visible at least sometimes
            swaps[self._rng.randrange(BITS)] = True
        disp = []
        for row in trace:
            out = list(row)
            for j in range(BITS):
                if swaps[j]:
                    out[2 * j], out[2 * j + 1] = out[2 * j + 1], out[2 * j]
            disp.append(tuple(out))
        return markers, disp, True

    # -- the human's move --------------------------------------------------------------

    def submit(self, nonce: int, move: dict[str, Any]) -> bool:
        """Record the human's move for the current pending step. Idempotent on nonce."""
        if self._pending is None or self._submitted is not None:
            return False
        if nonce != self._pending["nonce"]:
            return False
        self._submitted = move
        return True

    def step(self) -> "Conversation":
        if self._pending is None or self._submitted is None:
            return self
        pending, move = self._pending, self._submitted
        mode = pending["mode"]
        if mode == "choose":
            self._resolve_choice(move)
        elif mode == "compose_a":
            self._resolve_a(pending, move)
        elif mode == "read_b":
            self._resolve_b(pending, move)
        self._submitted = None
        return self

    def _resolve_choice(self, move: dict[str, Any]) -> None:
        what = move.get("move")
        if what == "speak":
            self._open_turn(_A, referent=0, arm="live", blind=False)
        elif what == "listen":
            referent = self._rng.randrange(8)  # harness-drawn, never history-derivable
            self._open_turn(_B, referent=referent, arm="live", blind=False)
        elif what == "audit":
            self._begin_audit()
        elif what == "end":
            self._phase = "done"
            self._finish()

    def _resolve_a(self, pending: dict[str, Any], move: dict[str, Any]) -> None:
        blind = pending["blind"]
        referent = pending["referent"] if blind else int(move.get("ref", 0)) % 8
        signal = int(move.get("sig", 0)) % 8
        word = channel(signal, seed=pending["channel_seed"], bits=BITS)
        word_bits = _bits_of(word)
        ref_bits = _bits_of(referent)
        act_bits = tuple(pick(self._recv[j][word_bits[j]], self._rng) for j in range(BITS))
        successes = tuple(int(act_bits[j] == ref_bits[j]) for j in range(BITS))
        entry = {
            "dir": _A, "arm": pending["arm"], "blind": blind, "phase": self._phase,
            "referent": referent, "signal": signal, "word": word, "act": _pack(act_bits),
            "success": list(successes),
        }
        if blind:
            # Free counterfactual nulls on the same recorded signal — no extra human action.
            entry["frozen_success"] = [
            return
        try:
            nonce = int(raw_nonce[0])
        except ValueError:
            return
        move: dict[str, Any] = {}
        if "move" in params:
            move["move"] = params["move"][0]
        for key in ("sig", "ref", "act"):
            if key in params:
                try:
                    move[key] = int(params[key][0])
                except ValueError:
                    pass
        session.submit(nonce, move)

    @staticmethod
    def describe(session: Conversation) -> dict[str, Any]:
        frame = session.describe()
        report = session.take_report()
        if report is not None:
            _persist_session(report)
        return frame


class _SequenceHandler:
    """The shift-chain working memory — a passive engine that writes a new symbol every few
    ticks and shifts the tape. No controls; the page draws the held words and their ages."""

    @staticmethod
    def configure(engine: SequenceEngine, params: dict[str, list[str]]) -> None:
        pass  # auto-advancing; nothing to steer

    @staticmethod
    def describe(engine: SequenceEngine) -> dict[str, Any]:
        return engine.describe()


_HANDLERS: dict[str, Any] = {
    "emergence": _EmergenceHandler,
    "crystal": _CrystalHandler,
    "repulsion": _RepulsionHandler,
    "pipeline": _PipelineHandler,
    "base": _BaseHandler,
    "coupled": _CoupledHandler,
    "align": _AlignHandler,
    "dialogue": _DialogueHandler,
    "conversation": _ConversationHandler,
    "sequence": _SequenceHandler,
}


class _Ticker:
    """Steps one engine on its own thread and publishes each frame.

    Runs only while someone is subscribed. Subscribers wait on a condition
    rather than polling, so a frame reaches the browser as soon as it exists.
    """

    def __init__(self, guarded: _Guarded, handler: Any, rate: float) -> None:
        self._guarded = guarded
        self._handler = handler
        self._interval = 1.0 / rate
        self._condition = threading.Condition()
        self._frame: dict[str, Any] | None = None
        self._sequence = 0
        self._watchers = 0
        self._running = False
        self._generation = 0
        self._controls: dict[str, list[str]] = {}

      뒤섞는 귀무가 화면 누출을 잡습니다. 최대 문장: <strong>이 사람과 이 엔진이 사적 k비트(k≤3)
      관례를 세우고 눈가림 시험에서 썼다</strong>. <strong>이해도 언어도 아닙니다.</strong>
    </p>

    <div class="controls">
      <button class="act" id="cv-new">새 만남</button>
      <span class="label" style="margin-left:auto"><span id="cv-phase">—</span> · <b id="cv-progress"></b></span>
    </div>

    <div id="cv-stage">
      <p class="label" id="cv-instruction">새 만남을 시작하세요.</p>
      <div id="cv-show" style="text-align:center;font-size:40px;letter-spacing:6px;min-height:48px;margin:6px 0"></div>
      <div id="cv-traces" style="display:none"></div>
      <div id="cv-composer" style="display:none;margin-top:10px"></div>
      <div id="cv-actions" style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:14px"></div>
    </div>

    <div id="cv-transcript" style="margin-top:16px"></div>
    <div id="cv-report" style="display:none;margin-top:12px"></div>
    <div class="status" id="cv-status"></div>
  </div>
</section>

<section class="panel" id="p-sequence">
  <div class="card">
    <h2>작업기억 — 최근 K개를 순서대로 붙잡는 시프트 체인</h2>
    <p class="note">
      폭의 벽(한 순간 최대 3비트)은 그대로지만 <strong>시간 축은 벽이 없습니다</strong>. 검증된
      3비트 셀 4개를 <strong>시프트 체인</strong>(=한 칸씩 밀어내는 줄)으로 엮어, 매 턴 새 기호를
      맨 앞에 쓰고 나머지를 한 칸씩 뒤로 옮깁니다. 체인은 <strong>최근 4개를 순서대로</strong>
      기억합니다 — 총 12비트.
    </p>
    <p class="note" style="margin-top:-8px">
      각 셀은 <strong>홀로 통합</strong>(6유닛 정확 Φ)이고 침묵을 건너 자기 비트를 붙잡습니다. 셀
      사이 다리는 <strong>전송</strong>이지 통합이 아니라, 전체를 하나라 주장하지 않습니다. 얻는 것은
      <strong>기억과 순서</strong>이지 언어가 아닙니다. 측정: <code>state/communication/accumulation.py</code>.
    </p>

    <div class="metrics">
      <div class="metric"><div class="k">순서대로 유지</div><div class="v"><span id="sq-held">—</span> 비트</div></div>
      <div class="metric"><div class="k">지나간 턴</div><div class="v" id="sq-turns">—</div></div>
      <div class="metric"><div class="k">다음 기호까지</div><div class="v" id="sq-next">—</div></div>
    </div>

    <p class="label" style="margin-top:14px">테이프 — 최신(왼쪽) → 가장 오래됨(오른쪽)</p>
    <div id="sq-tape" style="display:flex;gap:10px;margin-top:6px;min-height:96px"></div>

    <p class="label" style="margin-top:14px">맨 앞 셀이 지금 붙잡은 상태 (3쌍의 차동)</p>
    <canvas id="sq-front" height="70"></canvas>

    <div class="status" id="sq-status"></div>
  </div>
</section>

<footer>
  기본 창 크기(250표본)에서는 <strong>완전히 독립인</strong> 두 스트림도 상호정보량이
  약 <b>0.155비트</b>로 찍힙니다 — 결합이 아니라 표본이 적어서 생기는 인공물입니다.
  그래서 이 화면의 <b>부분적</b>은 “독립과 구분되지 않음”이라는 뜻이고,
  스트림에 대한 실제 주장은 <b>창발</b>뿐입니다.
</footer>

</div>

<script>
"use strict";

// ── canvas helpers ─────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

function fit(canvas) {
  const dpr = window.devicePixelRatio || 1;

codex
The critical measurement point is now fixed: the requested interaction score is a valid sufficient test for pair dependence, but it cannot by itself exclude every planted lookup—an XOR table scores maximally. The protocol therefore needs both the information nulls and a causal raw-state intervention; the verdict must explicitly stop short of “the engine discovered composition.”
The architecture, estimator, null battery, compatibility contract, and claim boundary are fully specified. No code or unmeasured result was produced.
  ✓ Inspect current engine, measurements, tests, and prior Part 4 sketches
  ✓ Design the minimal default-off dynamical context coupling
  ✓ Specify exact synergy estimator and load-bearing null battery
  ✓ Define earned claim, ceiling, and phased first commit
codex
The smallest honest component is a bounded, one-turn `ContextGate`: the existing tape continues recording symbols unchanged, while the raw differential state of the previous front cell multiplicatively modulates a separate 3-bit response cell. This reconciles fable’s dynamical gate with sol’s bounded-state, frozen-audit requirement.

Crucially, synergy alone cannot prove “not planted.” A fixed XOR lookup scores maximal synergy. The design therefore earns only measured, state-mediated context dependence—not spontaneous or learned composition.

## 1. Mechanism

Add `context_gate: float = 0.0` to [sequence.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/sequence.py).

The dataflow is:

```text
clean tape cell holding P ── raw differentials ──┐
                                                ×── 3-bit response cell R
current symbol C ─────────── current drive ─────┘

clean SequenceEngine tape: shift P, write C exactly as before
```

Do not overwrite tape cell 0 with the composite. Otherwise the next turn’s “past” would be the previous composite rather than the previous symbol, silently destroying the recorder’s established meaning.

For pair `j`:

- `x_j ∈ {-1,+1}` is the existing current-symbol drive orientation.
- `δ_j(t) = p[2j](t) - p[2j+1](t)` is the actual held differential, never the stored `word`.
- `h_j(t) = tanh(GAIN × δ_j(t) / (2 × AMPLITUDE))`.
- The response drive is

\[
q_j(t)=x_j[(1-g)+g\,h_j(t)]
\]

and the response pair receives the existing differential drive `(0.8q_j, -0.8q_j)`.

At `g=0`, this is the ordinary current write. At full gating, the orientation depends jointly on current and past—approximately a bitwise XOR under the existing sign convention. The multiplication is a smooth state equation, not a branch or 64-entry symbol table.

The response is produced by a fresh 6-unit `Wiring.PAIRS`, `chain=0.2` cell using the existing tell/hold dynamics. During the write, the context state remains in deaf hold and may be stepped in lockstep, so the modulator is a live basin state. It is bounded to the immediately previous cell and one response; it does not accumulate a transcript or hidden policy.

Purity requirements:

- Standard library only, reusing `CoupledEngine`.
- Dedicated seed derivation and operation counter for the response path, so it cannot perturb tape seeds.
- No I/O, clock, or thread.
- `tape()` remains the clean last-K-symbol carrier.
- Add an unambiguous `context_read() -> int | None`; that, not `tape()[0]`, is `R`.

Default exactness is load-bearing: `context_gate=0.0` must dispatch through the current `turn()` path before any extra RNG draw, float operation, response allocation, or operation-counter increment. Tests compare omitted versus explicit zero after every turn across seeds, including every raw cell value—not merely decoded tape words.

## 2. Exact synergy measurement

Use a balanced factorial audit:

- `C`: current symbol, all eight categories.
- `P_written`: previous symbol sent to the engine.
- `P_h`: previous symbol decoded from the raw held differential immediately before composition.
- `R`: `context_read()` immediately after the contextual response cell finishes its fixed tell/hold window.

The headline score uses the state the gate actually received:

\[
S = I(R;(C,P_h))-I(R;C)-I(R;P_h)
\]

This is the negative of the usual co-information sign convention. It is a sufficient synergistic-interaction score under balanced independent `C` and `P`, but not a general nonnegative PID measure. Do not clip negative values.

All variables are categorical:

- `C`, `P_h`, and `R`: integers `0…7`.
- `(C,P_h)`: one of 64 exact pairs.
- MI is computed directly from `Counter` frequencies:

\[
I(A;B)=\sum_{a,b}p(a,b)\log_2\frac{p(a,b)}{p(a)p(b)}
\]

No `info.py` binning.

Run every one of the 64 `(C,P_written)` pairs once per audit-seed block, with fresh engine resets and disjoint calibration/audit seed lists. Gate strength may be selected on calibration seeds, but is frozen before the audit. A suitable concrete audit is 40 seed blocks, giving 2,560 reads per arm, plus 999 seeded history permutations. These are sampling conditions, not claimed outcomes.

Report beside `S`:

- `I(P_written;P_h)`: whether context reached the gate.
- `I(C;tape()[0])`: whether the clean current carrier still works.
- `H(R)` and effective categorical width `2^H(R)`.
- Occupied/reproducible response categories out of 8.
- Joint pair support out of 64.
- Per-bit interaction scores, so one responsive latch cannot masquerade as three.
- Tape accuracy and cross-cell MI from the established [accumulation.py](/Users/mini/dancinlab/anima-reborn/state/communication/accumulation.py) conventions.

## 3. Null battery

| Arm/control | Exact construction | What it kills |
|---|---|---|
| Shuffled history | Within each current-symbol/seed block, permute `P_h` across reads and recompute `S`, 999 times | Accidental marginal MI and finite-sample interaction bias; true pairing must exceed this distribution |
| No gate | Identical symbols, seeds, tell/hold budget, but `context_gate=0.0`; take the ordinary current read as `R` | Shows what context buys beyond the already-clean current channel |
| Past-copy arm | Use the existing clean bridge to write only `P_h` into the response cell; current drive is unreachable | A deterministic past copy has high `I(R;P_h)` but interaction score at its shuffle distribution |
| Current-copy arm | Ordinary clean current write, ignoring past | Confirms that perfect current fidelity alone scores no synergy |
| Deaf/unreachable context | Keep the current response path live but feed a deaf or independently drawn context cell | Proves the held carrier is actually in the causal path |
| Raw-state/metadata swap | Exchange two cells’ six raw values while leaving their stored `word` fields untouched; separately swap only metadata | The response must follow raw differential state, not a Python word, label, or `if` |
| Basin intervention | Small within-basin jolt versus a barrier-crossing jolt before composition | Small jolts should preserve the effect; crossed states should change it according to the new actual differential |
| Held-out table control | Fit a literal `(C,P)→R` table on calibration pair rows, then test omitted pair rows and fresh perturbed states | Kills a lookup learned from calibration observations; tests generalization of the continuous state law |

The pass rule is conjunctive:

1. Frozen-audit `S` exceeds its shuffled-history distribution and its paired no-gate/copy arms.
2. No-gate and copy arms are indistinguishable from their own shuffle distributions.
3. The response follows raw-state swaps but not metadata-only swaps.
4. More than one latch contributes, and response width does not collapse.
5. The clean tape retains its already-measured carrier performance.

If any fails—especially if the live arm is reproducible by the copy arm or only a collapsed response category carries the effect—the gate is pruned.

### The unavoidable planted-rule limit

No finite categorical audit can prove that a deterministic engine is not reproducible by *some* fixed lookup: any mapping from 64 input pairs to eight responses can be tabulated. A “new random symbol” is also not genuinely new in this eight-symbol alphabet.

Therefore:

- The controls can exclude current-copy, past-copy, Python-label lookup, lookup fitted from audit data, and disconnected history.
- They cannot establish that the multiplication law was discovered rather than designed.
- The source inspection plus raw-state intervention establish that the designed interaction is implemented in engine dynamics.

A stronger “learned composition” claim would require a separately trained gate, an untrained/yoked control, a hidden codebook chosen after training, and frozen performance on genuinely withheld relations. That is a later component, not something this deterministic gate earns.

## 4. Honest verdict and ceiling

If it passes, the earned sentence is:

> In a frozen balanced audit, the current 3-bit response depended on the immediately preceding engine-held state: its categorical interaction score exceeded its shuffled-history distribution and the no-gate/copy controls, and causal raw-state interventions moved the response.

Short repo wording:

> The current exchange depended on the held past, by measured synergy above its shuffled-history null.

It must not say:

- “The engine discovered or learned composition.”
- “The engine understands context.”
- “The K-cell tape is one integrated system.”
- “The current exchange contains K×3 bits.”
- “This is language or conversation.”

The bound remains exact:

\[
I(R;C,P_h)\le H(R)\le\log_2 8=3\text{ bits per response}.
\]

The tape may retain K ordered symbols over time, but only one 3-bit contextual response is exchanged at a moment. The gain is working memory that is used in a designed, causally verified contextual transduction—nothing semantic or linguistic yet.

## 5. Smallest landing

The first landing should contain:

1. `state/communication/context_composition.py`

   A pure, seedable balanced audit driving the shipped `SequenceEngine`, implementing exact categorical MI, permutation distributions, all matched arms, raw-state interventions, and width reporting.

2. Minimal `sequence.py` surface

   `context_gate=0.0`, separate response state, `context_read()`, and the hard zero-path compatibility guard.

3. Tests

   Bit-exact default trajectory, seed reproducibility, tape unaffected by active response, raw-state versus metadata intervention, and measurement-kernel tests.

4. Viewer lockstep

   In the same source commit, because of the repository rule: show the clean current word, held previous differential, gate state, and contextual response separately. Do not derive a “synergy” verdict from a single live trajectory.

5. Measured documentation

   Run the audit first, then fill the Korean `state/communication/RESULTS.md` section with the actual live/null values, sampling conditions, widths, and pass or prune verdict. No placeholder capability numbers.

Deferred:

- Multi-turn working-memory game in `conversation.py`.
- Free-play interpretation; only a later blind frozen audit may provide evidence.
- Using ages deeper than one turn.
- Learned/adaptive context gates.
- Semantic grounding, syntax, or claims that the whole tape is integrated.

This preserves the established recorder in [sequence.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/sequence.py), reuses the basin evidence from [retention.py](/Users/mini/dancinlab/anima-reborn/state/communication/retention.py), and adds exactly one frontier claim: immediate context, measured causally and against the controls that can fake it.
tokens used
86,708
The smallest honest component is a bounded, one-turn `ContextGate`: the existing tape continues recording symbols unchanged, while the raw differential state of the previous front cell multiplicatively modulates a separate 3-bit response cell. This reconciles fable’s dynamical gate with sol’s bounded-state, frozen-audit requirement.

Crucially, synergy alone cannot prove “not planted.” A fixed XOR lookup scores maximal synergy. The design therefore earns only measured, state-mediated context dependence—not spontaneous or learned composition.

## 1. Mechanism

Add `context_gate: float = 0.0` to [sequence.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/sequence.py).

The dataflow is:

```text
clean tape cell holding P ── raw differentials ──┐
                                                ×── 3-bit response cell R
current symbol C ─────────── current drive ─────┘

clean SequenceEngine tape: shift P, write C exactly as before
```

Do not overwrite tape cell 0 with the composite. Otherwise the next turn’s “past” would be the previous composite rather than the previous symbol, silently destroying the recorder’s established meaning.

For pair `j`:

- `x_j ∈ {-1,+1}` is the existing current-symbol drive orientation.
- `δ_j(t) = p[2j](t) - p[2j+1](t)` is the actual held differential, never the stored `word`.
- `h_j(t) = tanh(GAIN × δ_j(t) / (2 × AMPLITUDE))`.
- The response drive is

\[
q_j(t)=x_j[(1-g)+g\,h_j(t)]
\]

and the response pair receives the existing differential drive `(0.8q_j, -0.8q_j)`.

At `g=0`, this is the ordinary current write. At full gating, the orientation depends jointly on current and past—approximately a bitwise XOR under the existing sign convention. The multiplication is a smooth state equation, not a branch or 64-entry symbol table.

The response is produced by a fresh 6-unit `Wiring.PAIRS`, `chain=0.2` cell using the existing tell/hold dynamics. During the write, the context state remains in deaf hold and may be stepped in lockstep, so the modulator is a live basin state. It is bounded to the immediately previous cell and one response; it does not accumulate a transcript or hidden policy.

Purity requirements:

- Standard library only, reusing `CoupledEngine`.
- Dedicated seed derivation and operation counter for the response path, so it cannot perturb tape seeds.
- No I/O, clock, or thread.
- `tape()` remains the clean last-K-symbol carrier.
- Add an unambiguous `context_read() -> int | None`; that, not `tape()[0]`, is `R`.

Default exactness is load-bearing: `context_gate=0.0` must dispatch through the current `turn()` path before any extra RNG draw, float operation, response allocation, or operation-counter increment. Tests compare omitted versus explicit zero after every turn across seeds, including every raw cell value—not merely decoded tape words.

## 2. Exact synergy measurement

Use a balanced factorial audit:

- `C`: current symbol, all eight categories.
- `P_written`: previous symbol sent to the engine.
- `P_h`: previous symbol decoded from the raw held differential immediately before composition.
- `R`: `context_read()` immediately after the contextual response cell finishes its fixed tell/hold window.

The headline score uses the state the gate actually received:

\[
S = I(R;(C,P_h))-I(R;C)-I(R;P_h)
\]

This is the negative of the usual co-information sign convention. It is a sufficient synergistic-interaction score under balanced independent `C` and `P`, but not a general nonnegative PID measure. Do not clip negative values.

All variables are categorical:

- `C`, `P_h`, and `R`: integers `0…7`.
- `(C,P_h)`: one of 64 exact pairs.
- MI is computed directly from `Counter` frequencies:

\[
I(A;B)=\sum_{a,b}p(a,b)\log_2\frac{p(a,b)}{p(a)p(b)}
\]

No `info.py` binning.

Run every one of the 64 `(C,P_written)` pairs once per audit-seed block, with fresh engine resets and disjoint calibration/audit seed lists. Gate strength may be selected on calibration seeds, but is frozen before the audit. A suitable concrete audit is 40 seed blocks, giving 2,560 reads per arm, plus 999 seeded history permutations. These are sampling conditions, not claimed outcomes.

Report beside `S`:

- `I(P_written;P_h)`: whether context reached the gate.
- `I(C;tape()[0])`: whether the clean current carrier still works.
- `H(R)` and effective categorical width `2^H(R)`.
- Occupied/reproducible response categories out of 8.
- Joint pair support out of 64.
- Per-bit interaction scores, so one responsive latch cannot masquerade as three.
- Tape accuracy and cross-cell MI from the established [accumulation.py](/Users/mini/dancinlab/anima-reborn/state/communication/accumulation.py) conventions.

## 3. Null battery

| Arm/control | Exact construction | What it kills |
|---|---|---|
| Shuffled history | Within each current-symbol/seed block, permute `P_h` across reads and recompute `S`, 999 times | Accidental marginal MI and finite-sample interaction bias; true pairing must exceed this distribution |
| No gate | Identical symbols, seeds, tell/hold budget, but `context_gate=0.0`; take the ordinary current read as `R` | Shows what context buys beyond the already-clean current channel |
| Past-copy arm | Use the existing clean bridge to write only `P_h` into the response cell; current drive is unreachable | A deterministic past copy has high `I(R;P_h)` but interaction score at its shuffle distribution |
| Current-copy arm | Ordinary clean current write, ignoring past | Confirms that perfect current fidelity alone scores no synergy |
| Deaf/unreachable context | Keep the current response path live but feed a deaf or independently drawn context cell | Proves the held carrier is actually in the causal path |
| Raw-state/metadata swap | Exchange two cells’ six raw values while leaving their stored `word` fields untouched; separately swap only metadata | The response must follow raw differential state, not a Python word, label, or `if` |
| Basin intervention | Small within-basin jolt versus a barrier-crossing jolt before composition | Small jolts should preserve the effect; crossed states should change it according to the new actual differential |
| Held-out table control | Fit a literal `(C,P)→R` table on calibration pair rows, then test omitted pair rows and fresh perturbed states | Kills a lookup learned from calibration observations; tests generalization of the continuous state law |

The pass rule is conjunctive:

1. Frozen-audit `S` exceeds its shuffled-history distribution and its paired no-gate/copy arms.
2. No-gate and copy arms are indistinguishable from their own shuffle distributions.
3. The response follows raw-state swaps but not metadata-only swaps.
4. More than one latch contributes, and response width does not collapse.
5. The clean tape retains its already-measured carrier performance.

If any fails—especially if the live arm is reproducible by the copy arm or only a collapsed response category carries the effect—the gate is pruned.

### The unavoidable planted-rule limit

No finite categorical audit can prove that a deterministic engine is not reproducible by *some* fixed lookup: any mapping from 64 input pairs to eight responses can be tabulated. A “new random symbol” is also not genuinely new in this eight-symbol alphabet.

Therefore:

- The controls can exclude current-copy, past-copy, Python-label lookup, lookup fitted from audit data, and disconnected history.
- They cannot establish that the multiplication law was discovered rather than designed.
- The source inspection plus raw-state intervention establish that the designed interaction is implemented in engine dynamics.

A stronger “learned composition” claim would require a separately trained gate, an untrained/yoked control, a hidden codebook chosen after training, and frozen performance on genuinely withheld relations. That is a later component, not something this deterministic gate earns.

## 4. Honest verdict and ceiling

If it passes, the earned sentence is:

> In a frozen balanced audit, the current 3-bit response depended on the immediately preceding engine-held state: its categorical interaction score exceeded its shuffled-history distribution and the no-gate/copy controls, and causal raw-state interventions moved the response.

Short repo wording:

> The current exchange depended on the held past, by measured synergy above its shuffled-history null.

It must not say:

- “The engine discovered or learned composition.”
- “The engine understands context.”
- “The K-cell tape is one integrated system.”
- “The current exchange contains K×3 bits.”
- “This is language or conversation.”

The bound remains exact:

\[
I(R;C,P_h)\le H(R)\le\log_2 8=3\text{ bits per response}.
\]

The tape may retain K ordered symbols over time, but only one 3-bit contextual response is exchanged at a moment. The gain is working memory that is used in a designed, causally verified contextual transduction—nothing semantic or linguistic yet.

## 5. Smallest landing

The first landing should contain:

1. `state/communication/context_composition.py`

   A pure, seedable balanced audit driving the shipped `SequenceEngine`, implementing exact categorical MI, permutation distributions, all matched arms, raw-state interventions, and width reporting.

2. Minimal `sequence.py` surface

   `context_gate=0.0`, separate response state, `context_read()`, and the hard zero-path compatibility guard.

3. Tests

   Bit-exact default trajectory, seed reproducibility, tape unaffected by active response, raw-state versus metadata intervention, and measurement-kernel tests.

4. Viewer lockstep

   In the same source commit, because of the repository rule: show the clean current word, held previous differential, gate state, and contextual response separately. Do not derive a “synergy” verdict from a single live trajectory.

5. Measured documentation

   Run the audit first, then fill the Korean `state/communication/RESULTS.md` section with the actual live/null values, sampling conditions, widths, and pass or prune verdict. No placeholder capability numbers.

Deferred:

- Multi-turn working-memory game in `conversation.py`.
- Free-play interpretation; only a later blind frozen audit may provide evidence.
- Using ages deeper than one turn.
- Learned/adaptive context gates.
- Semantic grounding, syntax, or claims that the whole tape is integrated.

This preserves the established recorder in [sequence.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/sequence.py), reuses the basin evidence from [retention.py](/Users/mini/dancinlab/anima-reborn/state/communication/retention.py), and adds exactly one frontier claim: immediate context, measured causally and against the controls that can fake it.
