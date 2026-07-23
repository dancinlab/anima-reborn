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
state/communication/aligned_drive.py
state/communication/conversation_channel.py
state/communication/capacity.py
state/communication/silence.py
state/communication/integration_vs_representation.py
state/coupling/RESULTS.md
state/coupling/verify_coupling.py
state/lab/2026-07-23-conversation-both.md
state/lab/2026-07-23-dialogue-viewer-prompt.md
state/lab/2026-07-22-consciousness-roadmap-prompt.md
state/lab/2026-07-22-base-engine-fable.md
state/lab/2026-07-22-base-engine-prompt.md
state/lab/2026-07-23-dialogue-viewer-both.md
state/lab/2026-07-22-words-fable.md
state/lab/2026-07-22-consciousness-roadmap-sol.md
state/lab/2026-07-22-communication-divergence-fable.md
state/lab/2026-07-23-english-bottleneck-both.md
state/lab/2026-07-22-communication-divergence-pilot.py
state/lab/2026-07-23-conversation-prompt.md
state/lab/2026-07-22-words-prompt.md
state/lab/2026-07-22-communication-divergence-prompt.md
state/lab/2026-07-22-consciousness-roadmap-fable.md
state/lab/2026-07-23-english-bottleneck-prompt.md
tests/test_dialogue.py
tests/test_pipeline.py
tests/test_info.py
tests/test_base.py
tests/test_coupled.py
tests/test_conversation_channel.py
tests/test_align.py
tests/test_viewer.py
tests/test_conversation.py
tests/test_dialogue_session.py
tests/test_substrate.py
tests/test_repulsion.py
tests/test_rhythm.py
tests/test_english_bottleneck.py
tests/test_words.py
tests/test_crystal.py
tests/test_iit4.py
tests/test_emergence.py
tests/test_directed.py
pyproject.toml
LICENSE

exec
/bin/zsh -lc "sed -n '1,260p' CLAUDE.md && sed -n '1,260p' src/anima_reborn/CLAUDE.md && sed -n '1,260p' src/anima_reborn/iit4/CLAUDE.md" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
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
# src/anima_reborn/ — the engines

Headless Python ports of the four browser engines in
[`dancinlab/anima-experience`](https://github.com/dancinlab/anima-experience) `index.html`.
Rendering, timers and DOM wiring stay in the origin; only the maths lives here.

## Files

| file | engine | origin |
| --- | --- | --- |
| `info.py` | entropy · joint entropy · mutual information · `Binning` | `bin` / `entropy` / `jointEntropy` |
| `emergence.py` | two streams sharing one oscillator | emergence tab |
| `crystal.py` | driven Ising ring, period-2 lock | DTC tab (`dtc_demo.py`) |
| `repulsion.py` | A × G latent field | A × G tab (moods from `tension_link.py`) |
| `pipeline.py` | repulsion → sampled streams → emergence | pipeline tab |
| `base.py` | all four under the crystal's clock — rotation only while LOCKED | (new — not in the origin) |
| `coupled.py` | A and G reading each other — the only engine here with nonzero integration, and `Rhythm`, which is when they do | (new — not in the origin) |
| `align.py` | the only module that LEARNS — co-occurrence teaches two modalities to meet | (new — not in the origin) |
| `substrate.py` | drive an engine from every state → measured TPM → Phi | (new — not in the origin) |
| `words.py` | words as a continuing drive, always paired with a null control | (new — not in the origin) |
| `dialogue.py` | the Lewis-Skyrms signaling game — `channel`/`pick`/`reinforce` primitives (imported by the `state/` reproducible half) plus `DialogueSession`, the live human-in-the-partner's-seat half the viewer's `소통` tab drives. `channel(bits=3)` adds the PAIRS path | (new — not in the origin) |
| `conversation.py` | `Conversation`, the FREE 3-bit exchange (`BASELINE→FREE→AUDIT→DONE`) the `대화` tab drives — factorized per-bit policies, the corrected display-scramble null, k-of-3 rank; the free log is never evidence, only the blind audit is | (new — not in the origin) |

`pipeline.py` imports `PHASE_RATE` / `PULL` / `DAMPING` from `repulsion.py` — the two
engines share one drift law, and it is defined once.

`coupled.py` is where the repo stops being a set of driven simulations. Everywhere else a
unit reads itself and something exogenous, which is why Phi is zero by architecture; there
the source is a live partner. Its falsifiers ship as part of its API (`Wiring.FEEDFORWARD`,
`Wiring.SELF`) rather than living only in tests — the claim is that the wiring is what
produces the integration, and that is only checkable if the other wirings are reachable.

`Rhythm` is the same module's second claim and its harder one. Add a `drive` and a wall
appears: on a fixed coupling, integration and representation trade off monotonically and
no value holds both — at full coupling the drive is not weak but *unreachable*, bit for
bit. A rhythm meets the two demands at different times instead of the same one, and beats
the control that matters (a fixed coupling at the rhythm's own time average). Two rules
follow. Measure a rhythm over a WHOLE listen/integrate cycle — `Rhythm.macro_step`, which
`substrate` defaults to — since half a cycle reports one phase's transition matrix and
labels it the engine's. And keep `Rhythm()` bit-exact with the pre-rhythm engine, because
every Phi already published was measured on it.

`align.py` is the only module that changes with experience, and it earns that by
measurement rather than ambition: dynamics alone cannot canonicalize, because the evidence
that two signals are one concept must be IN the signals and co-occurrence is what puts it
there. Its falsifier (`shuffled=True`) is public API for the same reason the wirings are.
Two rules it must keep — score only on held-out concepts, and report the gain over the
learner's OWN untrained baseline, which is not zero. A third arrived with `contrast`:
report how many effective dimensions the learned space uses, because pulling toward a
midpoint narrows it (1.21 of four, below the raw signals' 1.93) and a narrow space scores
well while carrying little. The push that fixes it must be by the unit direction and must
stop at a distance; by the raw displacement it runs away to rank 1.00, which is worse
than the contraction. `observe(..., sample=n)` draws a
fresh noise realization of the same concept; a consumer that repeats a noisy process on
one fixed observation is measuring that process's noise and scoring an exemplar.

The two are connected: `CoupledEngine(drive=...)` takes a per-unit vector, so an aligned
representation arrives as itself rather than as its average, and
`state/communication/aligned_drive.py` measures whether concept identity survives the
engine — 81% of it does with the midpoint rule alone, 86% with the push on. Measure the
drive BEFORE the engine every time: the engine can only lose information, so a trajectory
score alone cannot be attributed to it, and the deaf arm (coupling 1.0, drive
bit-unreachable) is what proves the engine was in the path at all.

Made deaf AFTER being told, the ring keeps its state forever while every acyclic wiring
falls to a fixed point — the first capability in this repo that recurrence buys rather
than merely exhibits (`state/communication/silence.py`). It is exactly one bit: four sign
inversions round the cycle make the loop's net sign positive, so the autonomous ring is
bistable, and that is a derivation the measurement then confirmed.

"Uses" is now earned too, and only just: loaded then probed, the ring's own response
depends on whether the probe agrees with what it holds — 0.729 against a ceiling of
0.758 that one bit allows, on 8/8 seeds, while every arm holding nothing is pinned at
0.500 by construction (`state/communication/match.py`). A score near 1.0 there would be
a bug, not a better result. The bound is topological, not a matter of size: a single ring of ANY even width holds
exactly one bit (a theorem — the response is odd, decreasing, bounded, so no orbit longer
than two), so widening it buys nothing. Capacity lives in the wiring's cycle structure, so
`Wiring.PAIRS` (units/2 latches) with a weak inter-pair `chain` holds units/2 bits AND
measures as integrated — 6 units, 3 bits, directed Phi held under 4x sampling where the
disjoint null collapses. Two rules it forces: `RECURRENCE_FLOOR` was calibrated at four
units and does NOT transfer (the artefact grows with width, so the decay test is the
verdict past six, never the magnitude), and the chain only integrates for an ODD number of
pairs — an even number forms a macro-ring that locks. `state/communication/capacity.py`.

`base.py` is the one module here that is **not** a port: it composes the four under a
single mortal clock. Its thesis, its measured constant `EPSILON`, and the line between
what it designs in and what it discovers are all stated in its docstring — keep them
there and keep them honest. `iit4/` has its own guide.

`viewer/` is the browser view of all five, and the one place in this package that does
I/O. The rules below apply to the engine files here, not to it — see its own guide.

## Adding or changing an engine — the viewer moves with it

An engine nobody can watch rots: the crystal sat wired to nothing for a while and it took
a question to notice. So a viewer change ships in the **same commit** as the engine change,
and it is enforced rather than remembered.

New engine:

1. `viewer/server.py` — a handler class with `configure` / `describe`, an entry in
   `_HANDLERS`, an instance in `Viewer.__init__`, a `TICK_RATES` rate.
2. `viewer/page.html` — a tab button, a panel, a `PREFIX` entry, and a `render<Name>()`
   function. Korean UI text (`ui-language` in the repo root guide).
3. Restart the viewer. `page.html` is re-read per request; `server.py` is not.

Changed readout: update `describe()` **and** the panel that draws it, together.

`tests/test_viewer.py::TestEngineViewerLockstep` fails on any of: an engine with no route,
a route with no engine, a missing tick rate, a missing tab or panel, a missing render
function, or a default tab that disagrees with `let active`. "Engine" is detected
structurally — any class in a top-level module with both `step` and `reset` — so a new one
is caught the day it lands, without anyone updating a list.

## Rules for changes here

- **Standard library only.** No numpy, no torch. If a change seems to need one, it
  belongs in a consumer, not in an engine.
- **No I/O, no clock, no threads.** Everything an engine needs arrives as an argument.
  Wall-clock time enters exactly once, through `RepulsionField`'s injectable `clock`.
- **Seedable.** Every stochastic engine takes `seed=` and owns a private
  `random.Random`. Never call the module-level `random` functions.
- **Immutable readings.** State objects are frozen slotted dataclasses, so a reading can
  be compared and stored. Engines are mutable; what they return is not.
- **Constants carry their origin.** A numeric literal that came from the origin is named,
  module-level, and documented with where it came from. Do not inline it.
- **Do not invent.** If the origin's behaviour is unclear, say so in the docstring rather
  than guessing. Deliberate departures from the origin are listed in the README.

## The estimator caveat

`info.py` is the plain plug-in estimator, matching the origin — no bias correction. On
the default 250-sample window it reports ~0.155 bits for genuinely independent streams.
That floor is pinned by `tests/test_emergence.py`; if you touch the estimator or the
default window, expect those tests to fail and update them deliberately, never by
loosening the bound.
# src/anima_reborn/iit4/ — Integrated Information Theory 4.0

A port of the hexa IIT 4.0 engine in `dancinlab/selfhost-work`
(`stdlib/consciousness/iit4_*.hexa` and `stdlib/iit_ei.hexa`). It answers one
question: is this system, in this state, one thing — or parts that happen to sit
together?

## The chain

| module | engine | origin |
| --- | --- | --- |
| `tpm.py` | M1 — matrix, repertoires, intrinsic difference | `iit4_tpm.hexa` |
| `distinction.py` | M2 — small-phi, MICE, distinctions | `iit4_distinction.hexa` |
| `relation.py` | M3 — congruent relations, Phi-structure | `iit4_relation.hexa` |
| `bigphi.py` | M4 — system big-Phi over the minimum cut | `iit4_bigphi.hexa` |
| `directed.py` | the same over DIRECTED cuts — tells a loop from a chain | (new — closes a carve-out) |
| `exclusion.py` | M10 + M13 — maximal complex, spectrum | `iit4_complex.hexa` |
| `ei.py` | effective information, a lower bound on Phi | `iit_ei.hexa` |

Each layer imports only the one below it. Do not add a back edge.

## Parity is the contract

`tests/test_iit4.py` holds a golden table dumped from the hexa engine at full
float precision, and compares with **exact equality** across every reported
field — phi, total, sum of distinction phi, sum of relation phi, and the
distinction count. Eleven cases, all bit-identical.

That strictness is not fussiness. Phi is an argmax over partitions and purviews,
so a last-bit change can select a different partition and move the answer
discontinuously. A tolerance would hide exactly the drift worth catching.

Consequences for anyone editing here:

- **Compute log2 as `(log p - log q) / log 2`**, never `math.log2`. They differ
  in the last bits and the origin used the former.
- **Keep `Q_SMOOTHING = 1e-10`** exactly where it is. It is why a perfect
  two-unit system reads 1.9999999994229218 and not 2.0.
- **Do not "clean up" a tie-break.** Lowest index on an intrinsic-difference
  tie, larger subset then lower mask on a complex tie. Reproducibility is the
  only reason those rules exist.
- If a change moves a golden number, that is a finding to explain, not a test to
  update.

## Carve-outs — inherited, not closed

State these when reporting results; do not let a reader assume otherwise.

- Partitions are all bipartitions of mechanism-and-purview, the standard
  tractable scheme, **not** IIT 4.0's own partition set.
- big-Phi is the Phi-structure destroyed by the system cut. IIT 4.0 proper
  rebuilds the cause-effect structure on the partitioned matrix with a
  normalization factor.
- **CLOSED, loudly:** `big_phi`'s cut is undirected and so reads a strictly
  feedforward chain at 1.27 bits where the theory says zero. `directed_big_phi`
  cuts one direction at a time and reads it 0.000 exactly, while the ring stays
  at 10.02 through the same code. `big_phi` is unchanged — the goldens depend on
  it — so both numbers are available and the old name still means what it did.
  Use `directed_big_phi` for any claim about recurrence.
- Relations are second-order only — pairs, bound by `min(phi_d)`.
- Nothing here is calibrated against PyPhi. On PyPhi's standard three-node
  network this engine reports 3.7548875003600997, which is this engine's number
  and not a claim about the theory's.

## Cost

Exponential several times over: every mechanism searches every purview across
every partition, and `find_complex` repeats that for all `2^n - 1` subsets.
Rough shape at n = 3: `big_phi` about 5 ms, `find_complex` about 6 ms. Six units
is slow, seven is unreasonable. `substrate.py` caps measurable systems at six
for this reason.

`TransitionMatrix` memoizes `marginal_on`, which is what makes anything past
three units finish at all. The cache is keyed on the mask and the pinned bits
only; it changes no result, because the matrix is immutable after construction.

## The `+inf` branch in `ei.py`

Kept, and very nearly unreachable — the reference is the column mean of the same
matrix, so a zero there implies a zero numerator. The one way in is arithmetic:
a subnormal probability whose division by the state count underflows. There is a
test for both facts. Do not delete the guard, and do not claim it fires in
ordinary use.

exec
/bin/zsh -lc "sed -n '1,340p' src/anima_reborn/coupled.py
sed -n '1,360p' src/anima_reborn/substrate.py
sed -n '1,380p' src/anima_reborn/align.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
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
"""The bridge — measuring one of our own engines with IIT 4.0.

The engines in this package produce behaviour. `iit4` measures whether a system
is one thing. This module joins them: it drives an engine from every state it
could be in, watches where it goes, and hands the resulting transition matrix to
Phi.

    from anima_reborn.substrate import crystal_phi

    print(crystal_phi(size=4, epsilon=0.02, seed=1))

**How the matrix is obtained.** IIT needs `P(unit is ON next | system state)`.
For a stochastic engine that is not something to derive on paper — the Ising
sweep visits spins in order, each decision conditioned on flips already made —
so it is *measured*: pin the system to a state, run one step, record which units
came back ON, and repeat. That is an empirical transition matrix, and its error
falls off as one over the square root of the trial count. Nothing here pretends
otherwise; `trials` is the honest knob and the estimate is a sample.

**Why the crystal.** Of the four engines it is the only one whose state is
natively binary — a spin is up or down, which is exactly what a unit is. The
others live in continuous latent space, and turning that into bits means
choosing a threshold. A threshold is a modeling decision that would end up
inside the Phi it produces, so this module refuses to make one silently:
`binarize` exists and takes the rule from the caller.

**What the crystal has to do with consciousness: nothing, and that is the
point.** It is a substrate with a known, tunable amount of causal structure, so
it can say whether the measurement responds to structure at all. The drive that
flips every spin acts on each one independently and integrates nothing; the
Ising coupling, where each spin answers to its neighbours, is the only thing
that can. So Phi should follow the coupling and collapse when noise drowns it —
a prediction that can fail, and `tests/test_substrate.py` is where it is put at
risk.
"""

from __future__ import annotations

import math
import random
import statistics
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .coupled import (
    AMPLITUDE,
    FIXED,
    GAIN,
    MACRO_STEP,
    UNITS,
    CoupledEngine,
    Rhythm,
    Wiring,
)
from .crystal import COUPLING, EPSILON, INVERSE_TEMPERATURE, CrystalVerdict, TimeCrystal
from .iit4 import (
    Complex,
    DirectedPhi,
    SystemPhi,
    TransitionMatrix,
    big_phi,
    directed_big_phi,
    find_complex,
)

__all__ = [
    "CoupledReading",
    "RECURRENCE_FLOOR",
    "RecurrenceEvidence",
    "Representation",
    "SubstrateReading",
    "coupled_matrix",
    "coupled_phi",
    "representation",
    "signature",
    "recurrence_evidence",
    "binarize",
    "crystal_matrix",
    "crystal_phi",
    "estimate_matrix",
    "estimate_state_matrix",
]

TRIALS = 400
"""Samples per state. The estimate's error falls as 1/sqrt(trials), so this
buys precision, not correctness — and Phi is an argmax, so a noisy matrix can
pick a different partition rather than merely a nearby number."""

MAX_UNITS = 6
"""Above this, measuring Phi stops finishing. Every mechanism searches every
purview over every partition, and `find_complex` repeats all of it per subset."""


def binarize(values: Sequence[float], threshold: float = 0.0) -> int:
    """Pack values into a state, one bit per value, ON when above `threshold`.

    Offered for callers who want to measure a continuous engine, and left as
    the caller's call on purpose: the threshold decides what counts as a unit
    being on, and therefore decides the Phi. It is a choice about the model,
    not a fact about the engine.
    """
    state = 0
    for i, value in enumerate(values):
        if value > threshold:
            state |= 1 << i
    return state


def estimate_matrix(
    n: int,
    step: Callable[[int, random.Random], int],
    *,
    trials: int = TRIALS,
    seed: int | None = None,
) -> TransitionMatrix:
    """Measure a stepping process's transition matrix by driving it.

    Args:
        n: Number of binary units.
        step: Takes a state and a random source, returns the state one step
            later. Called `trials` times per state, so it must not carry
            anything over between calls — the whole point is that each trial is
            an independent draw from the same starting state.
        trials: Samples per state.
        seed: Fixes the sampling.

    Returns:
        A `TransitionMatrix` whose entries are ON-frequencies rather than exact
        probabilities.
    """
    if not 1 <= n <= MAX_UNITS:
        raise ValueError(f"n must be in [1, {MAX_UNITS}], got {n}")
    if trials < 1:
        raise ValueError(f"trials must be >= 1, got {trials}")

    rng = random.Random(seed)
    values: list[float] = []
    for state in range(1 << n):
        counts = [0] * n
        for _ in range(trials):
            following = step(state, rng)
            for unit in range(n):
                if following >> unit & 1:
                    counts[unit] += 1
        values.extend(count / trials for count in counts)
    return TransitionMatrix(values, n)


def crystal_matrix(
    *,
    size: int = 4,
    epsilon: float = EPSILON,
    coupling: float = COUPLING,
    beta: float = INVERSE_TEMPERATURE,
    trials: int = TRIALS,
    seed: int | None = None,
) -> TransitionMatrix:
    """The time crystal's transition matrix, measured over one drive period.

    A spin being up is a unit being ON. One step is what the crystal itself
    calls a step: an Ising sweep, then the imperfect global flip.
    """
    if size > MAX_UNITS:
        raise ValueError(
            f"size must be <= {MAX_UNITS} to stay measurable, got {size}"
        )

    def step(state: int, rng: random.Random) -> int:
        spins = [1 if state >> i & 1 else -1 for i in range(size)]
        ring = TimeCrystal(
            size=size,
            epsilon=epsilon,
            coupling=coupling,
            beta=beta,
            history=1,
            seed=rng.getrandbits(63),
            initial=spins,
        )
        ring.step()
        return sum(1 << i for i, spin in enumerate(ring.spins) if spin > 0)

    return estimate_matrix(size, step, trials=trials, seed=seed)


@dataclass(frozen=True, slots=True)
class SubstrateReading:
    """What IIT 4.0 says about one of our engines.

    `verdict` is the engine's own read on itself — the crystal's period-2 lock —
    kept alongside Phi so the two can be compared rather than conflated. They
    are different claims: one is about rhythm in time, the other about the
    system being one thing.
    """

    phi: float
    """big-Phi of the whole substrate, in bits."""
    complex_units: int
    """Bitmask of the maximal complex — the part that is the entity. Zero when
    there is none."""
    complex_phi: float
    total: float
    """Unpartitioned Phi-structure the cut was measured against."""
    distinctions: int
    verdict: CrystalVerdict | None = None
    """The crystal's own lock verdict, when the substrate is a crystal."""

    @property
    def is_integrated(self) -> bool:
        return self.phi > 0.0

    def __str__(self) -> str:
        entity = f"{self.complex_units:b}" if self.complex_units else "none"
        rhythm = f" rhythm={self.verdict.value}" if self.verdict else ""
        return (
            f"phi={self.phi:.6f} of total={self.total:.6f} "
            f"({self.distinctions} distinctions) complex={entity}"
            f" phi_c={self.complex_phi:.6f}{rhythm}"
        )


def crystal_phi(
    *,
    size: int = 4,
    epsilon: float = EPSILON,
    coupling: float = COUPLING,
    beta: float = INVERSE_TEMPERATURE,
    state: int | None = None,
    trials: int = TRIALS,
    seed: int | None = None,
    with_complex: bool = True,
    with_verdict: bool = True,
) -> SubstrateReading:
    """Measure the time crystal's integrated information.

    Args:
        size: Spins in the ring, at most `MAX_UNITS`.
        epsilon: Per-spin probability the drive misses.
        state: Which ring configuration to measure Phi at. Defaults to the
            all-up state — Phi is a property of a system *in a state*, never of
            the system alone.
        trials: Samples per state when measuring the transition matrix.
        with_complex: Also search for the maximal complex. Roughly doubles the
            work and is what tells you *which part* is the entity.
        with_verdict: Also run the ring long enough to read its own lock
            verdict, for comparison against Phi.
    """
    matrix = crystal_matrix(
        size=size,
        epsilon=epsilon,
        coupling=coupling,
        beta=beta,
        trials=trials,
        seed=seed,
    )
    at = (1 << size) - 1 if state is None else state
    measured: SystemPhi = big_phi(matrix, at)

    entity: Complex | None = find_complex(matrix, at) if with_complex else None

    verdict = None
    if with_verdict:
        ring = TimeCrystal(
            size=size, epsilon=epsilon, coupling=coupling, beta=beta, seed=seed
        )
        verdict = ring.run(400).verdict

    return SubstrateReading(
        phi=measured.phi,
        complex_units=entity.units if entity else 0,
        complex_phi=entity.phi if entity else 0.0,
        total=measured.total,
        distinctions=len(measured.structure.distinctions),
        verdict=verdict,
    )


@dataclass(frozen=True, slots=True)
class CoupledReading:
    """What IIT 4.0 says about the coupled engine, with its conditions attached.

    Both measures are reported because they disagree, and the disagreement is
    the finding: `phi` cuts undirected and cannot see that a feedforward system
    is reducible, `directed_phi` cuts one way at a time and can. A claim about
    recurrence uses the directed number.

    The conditions are fields rather than documentation because they are part of
    the result. The same engine reads 12.07 at `macro_step = 17` and exactly
    0.0000 at 1.
    """

    wiring: Wiring
    phi: float
    """Undirected big-Phi — comparable with the rest of the repo."""
    directed_phi: float
    """Directed big-Phi. Zero means some direction of influence can be severed
    for free, which is what reducible means."""
    complex_units: int
    """Bitmask of the maximal complex, or 0 when there is none."""
    state: int
    macro_step: int
    trials: int

    @property
    def is_reducible(self) -> bool:
        """Exactly zero directed Phi — some direction severs for free.

        This direction is safe to read off one measurement: a sampled matrix can
        invent structure but cannot invent its absence, so a zero here is a zero.
        The opposite claim is not symmetric, which is why there is no
        `is_recurrent` — see `recurrence_evidence`.
        """
        return self.directed_phi == 0.0

    def __str__(self) -> str:
        entity = f"{self.complex_units:04b}" if self.complex_units else "none"
        return (
            f"{self.wiring.value:<12} phi={self.phi:6.3f} "
            f"directed={self.directed_phi:6.3f} "
            f"{'[reducible]' if self.is_reducible else '           '} "
            f"complex={entity} (state {self.state:04b}, tau={self.macro_step}, "
            f"{self.trials} trials)"
        )


def coupled_matrix(
    wiring: Wiring = Wiring.RING,
    *,
    units: int = UNITS,
    chain: float = 0.0,
    rhythm: Rhythm = FIXED,
    drive: float = 0.0,
    macro_step: int | None = None,
    gain: float = GAIN,
    amplitude: float = AMPLITUDE,
    trials: int = TRIALS,
    seed: int | None = None,
) -> TransitionMatrix:
    """Measure the coupled engine's transition matrix.

    One transition is `macro_step` engine ticks: reconstruct the units to
    +/-`amplitude` from the state, run, threshold at zero. Reconstruction
    amplitude and macro-step both sit inside the result.

    A rhythm must be measured over a whole listen/integrate cycle, so the
    default macro-step follows the rhythm rather than the module constant. Half
    a cycle would report one phase's matrix and label it the engine's.
    """
    if macro_step is None:
        macro_step = rhythm.macro_step
    if macro_step < 1:
        raise ValueError(f"macro_step must be >= 1, got {macro_step}")
    if units > MAX_UNITS:
        raise ValueError(
            f"units must be <= {MAX_UNITS} to stay measurable, got {units}"
        )

    def step(state: int, rng: random.Random) -> int:
        engine = CoupledEngine(
            wiring=wiring,
            units=units,
"""Learning that two very different signals are about the same thing.

Everything before this in the package is fixed: the wiring is given, the
constants are given, and nothing the engines meet ever changes them. This is the
first module that **learns**, and it is here because measurement demanded it
rather than because learning is interesting.

The chain that led here. `words.py` established that the substrate carries the
code and not the concept. The obvious fix — check whether one concept arriving
through two encodings lands in the same place — turned out to be an impossible
test: two independent hashes of one word share 0.0185 bits against a shuffled
null of 0.0212, so there is nothing in them to recover. Planting attractors
(`state/communication/attractor_canonicalization.py`) did not help either; a
substrate with no attractors agreed exactly as often, to the digit.

What that leaves is the shape of the real problem. **Two signals can only be
recognized as one concept if the evidence that they belong together is in the
signals — and what puts it there is co-occurrence, not dynamics.** Using
co-occurrence means changing with experience. Hence this.

**The mechanism.** Two modalities, each with its own projection. A pair arrives
together, and each projection is nudged toward the midpoint of where the two
currently land. Optionally (`contrast`), a non-partner is pushed away from that
same place by the unit direction, stopping once it is `margin` away. Nothing
else. There is no global objective — in particular nothing maximizes Phi or
mutual information, which this repo refused for the good reason that an
optimizer harvests the estimator's artefact.

**Why the push exists, and why it is off by default.** Pulling is all the
midpoint rule does, so nothing opposes contraction and the shared space narrows
toward a line: 1.21 of four effective dimensions, LOWER than the raw
observations' 1.93. Adding the other half of what co-occurrence says lifts that
to 1.48 and identification from 0.418 to 0.583. It is off by default because
every number published before it was measured without it.

The obvious version of it was worse than the problem. Pushing by the raw
displacement makes the step grow with the distance already gained, one direction
runs away, and the rank falls to exactly 1.00 — the collapse that scores well and
carries nothing, which is what killed the attractor route. `tests/test_align.py`
keeps that version around as a subclass so the artefact stays pinned.

**What makes it more than memorizing.** It is scored on concepts it never
trained on. Ten training concepts are enough to align concepts it has never
seen, so what it acquired is the correspondence between the modalities rather
than a table of pairs.

**The falsifier ships with it.** `shuffled=True` trains on the same signals with
the pairing destroyed — same statistics, same rate, same everything, no
co-occurrence. Over twelve seeds an honest run gains 0.780 and the control gains
-0.067.

**And the baseline is not zero.** Both modalities mix the same latent, so even
untrained random projections retain correlation — up to 0.397 on an unlucky
seed. Everything is therefore reported as the gain over this learner's OWN
untrained gap, because a verdict on the raw number would pass a learner that
never saw anything.

**What this is not.** It is two learned linear maps. Calling that understanding
would be the overclaim this repo keeps refusing; what it earns is that two
dissimilar signals about one thing can be brought to one place, and that the
bringing generalizes. Whether anything downstream *uses* that is a separate
question nothing here answers.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass

__all__ = ["Aligner", "AlignState", "DIM", "CONCEPTS", "NOISE", "RATE"]

DIM = 6
"""Width of a modality vector, and of the shared space they are brought into."""

CONCEPTS = 40
"""Concepts in the training pool. Ten already suffice — measured gap +0.748 at
ten, +0.519 at five — which is the evidence that the correspondence is what is
learned rather than the pairs."""

HELD_OUT = 20
"""Concepts kept out of training entirely. Every reported number is scored on
these; a learner that only memorized reads zero here."""

NOISE = 0.3
"""Per-component observation noise on each modality. The gap degrades gracefully
with it: +0.948 / +0.716 / +0.421 / +0.103 at 0.1 / 0.3 / 0.6 / 1.0."""

RATE = 0.01
"""Learning rate of the nudge toward the midpoint."""

CONTRAST = 0.0
"""How hard a NON-partner is pushed apart, relative to `rate`. Zero by default,
which leaves the learner bit-identical to the one every published number was
measured on.

Why it exists. The midpoint rule only ever pulls, so nothing opposes contraction
and the shared space shrinks: measured over 12 seeds at `dim=4`, the trained
projections occupy 1.35 effective dimensions against the raw observations' 1.93.
That is not the rank-1 collapse that killed the attractor route, but it is close
to a line, and it means most of what a vector-drive engine could be told goes
unused. Co-occurrence teaches what goes together AND what does not; only the
first half was implemented.

With it on at 0.3 and `MARGIN` 1.0, cross-modal identification of held-out
concepts goes from 0.418 to 0.583 and the rank from 1.21 to 1.48, while the
shuffled control stays at the floor — so the push is teaching from the pairing
rather than improving the signals. Not a tuned point: the reading holds at
0.535-0.583 across contrast 0.1-0.6 and margin 0.5-2.0, and the plateau is the
evidence rather than the peak."""

MARGIN = 1.0
"""How far a non-partner has to be before the push stops.

The stopping distance is what actually widens the space, and it is a separate
job from pushing by the unit direction. Measured over six seeds at `dim=4`, in
effective dimensions of four: 1.21 with no push at all, 1.00 pushing by the raw
displacement, 1.12 pushing by the direction with nothing to stop it, and 1.48
pushing by the direction and stopping. Neither half is the other's spare."""

INITIAL_SCALE = 0.3
"""Projections start random, and must. Starting at zero makes both projections
land on the origin, the midpoint is the origin too, and the update is
identically zero forever — the learner never leaves its initial state."""


def _concept_vector(concept: int, dim: int) -> list[float]:
    """A concept's latent value. Hashed so it is deterministic across runs and
    carries no structure anyone designed."""
    digest = hashlib.blake2b(f"c|{concept}".encode(), digest_size=dim).digest()
    return [(b / 255.0) * 2 - 1 for b in digest]


@dataclass(frozen=True, slots=True)
class AlignState:
    """How well the two modalities have been brought together.

    Every field is scored on held-out concepts. Training-set agreement is not
    reported at all, because it cannot distinguish learning from memorizing.
    """

    same_concept: float
    """Mean cosine between the two projections when both come from ONE held-out
    concept. In [-1, 1]."""
    different_concept: float
    """The same, for projections of two DIFFERENT held-out concepts."""
    initial_gap: float
    """What this learner's gap was before it saw anything.

    Not zero, and that matters. Both modalities are mixings of one latent, so
    even random projections of them retain some correlation — measured over
    twelve seeds the untrained gap averages 0.049 but reaches 0.397 on the
    unluckiest. A verdict on the raw gap would let an untrained learner pass.
    """
    pairs_seen: int

    @property
    def gap(self) -> float:
        """How much closer one concept's two views are than two concepts' views.
        Read `learned` instead unless you want the raw number."""
        return self.same_concept - self.different_concept

    @property
    def learned(self) -> float:
        """The gap this learner ADDED. The only number that is about learning."""
        return self.gap - self.initial_gap

    @property
    def aligned(self) -> bool:
        """Measured against the shuffled control rather than chosen: over twelve
        seeds an honest run gains 0.780 (worst 0.566) and the control gains
        -0.067 (worst -0.428). The bar sits between them with room on both."""
        return self.learned > 0.3

    def __str__(self) -> str:
        return (
            f"learned={self.learned:+.3f} (gap {self.gap:+.3f} from "
            f"{self.initial_gap:+.3f}) after {self.pairs_seen} pairs"
            f"{' [aligned]' if self.aligned else ''}"
        )


class Aligner:
    """Two modalities of one world, and the correspondence between them.

    Args:
        dim: Width of each modality and of the shared space.
        concepts: Size of the training pool.
        noise: Observation noise per component.
        rate: How far each projection moves toward the midpoint per pair.
        contrast: How hard a non-partner is pushed apart, relative to `rate`.
            Zero leaves the learner exactly as it was. Above zero it opposes the
            contraction the midpoint rule cannot see — still a local rule over
            what did and did not co-occur, not a global objective, because an
            optimizer would harvest the estimator's artefact.
        shuffled: **The falsifier.** Pair each modality-A observation with a
            different concept's modality-B observation — same signals, same
            statistics, co-occurrence destroyed. Public API rather than a test
            fixture, because the claim is that co-occurrence is what teaches,
            and that is only checkable if it can be removed.
        seed: Fixes the modalities, the noise and the initial projections.
    """

    def __init__(
        self,
        *,
        dim: int = DIM,
        concepts: int = CONCEPTS,
        noise: float = NOISE,
        rate: float = RATE,
        contrast: float = CONTRAST,
        margin: float = MARGIN,
        shuffled: bool = False,
        seed: int | None = None,
    ) -> None:
        if dim < 2:
            raise ValueError(f"dim must be >= 2, got {dim}")
        if concepts < 2:
            raise ValueError(f"concepts must be >= 2, got {concepts}")
        if rate <= 0.0:
            raise ValueError(f"rate must be > 0, got {rate}")
        if noise < 0.0:
            raise ValueError(f"noise must be >= 0, got {noise}")
        if contrast < 0.0:
            raise ValueError(f"contrast must be >= 0, got {contrast}")
        if margin <= 0.0:
            raise ValueError(f"margin must be > 0, got {margin}")

        self.dim = dim
        self.concepts = concepts
        self.noise = noise
        self.rate = rate
        self.contrast = contrast
        self.margin = margin
        self.shuffled = shuffled
        self._seed = seed
        self._rng = random.Random(seed)
        self._world = self._make_world()
        self._left, self._right = self._initial_projections()
        self._pairs = 0
        self._held_out_views: list[tuple[list[float], list[float]]] | None = None
        self._initial_gap = self._measure().gap

    # ── the world ──────────────────────────────────────────────────────────
    def _make_world(self) -> tuple[list[list[float]], list[list[float]]]:
        """Two ways of looking at the same concepts. Each modality is its own
        random mixing of the latent, so neither resembles the other."""
        rng = random.Random(self._rng.getrandbits(32))
        return (
            [[rng.gauss(0, 1) for _ in range(self.dim)] for _ in range(self.dim)],
            [[rng.gauss(0, 1) for _ in range(self.dim)] for _ in range(self.dim)],
        )

    def _initial_projections(self) -> tuple[list[list[float]], list[list[float]]]:
        rng = random.Random(self._rng.getrandbits(32))
        return (
            [
                [rng.gauss(0, INITIAL_SCALE) for _ in range(self.dim)]
                for _ in range(self.dim)
            ],
            [
                [rng.gauss(0, INITIAL_SCALE) for _ in range(self.dim)]
                for _ in range(self.dim)
            ],
        )

    def observe(self, concept: int, *, modality: int, sample: int = 0) -> list[float]:
        """One noisy observation of a concept through one modality.

        Deterministic in `(concept, modality, sample)`, so an observation can be
        re-derived rather than stored. `sample` draws a DIFFERENT noise
        realization of the same concept through the same modality; `sample=0` is
        the only one that existed before and is unchanged bit for bit.

        Repeats matter downstream. A consumer that re-runs a noisy process on
        one fixed observation is measuring that process's noise, not invariance
        to observation noise, and would be scoring an exemplar rather than a
        concept.
        """
        latent = _concept_vector(concept, self.dim)
        mixing = self._world[modality]
        key = concept * 2 + modality
        if sample:
            # Spelled out rather than hashed, so the stream does not depend on
            # anything about the interpreter's hashing.
            key = (key * 1_000_003 + sample) & 0x7FFFFFFF
        rng = random.Random(key ^ (self._seed or 0))
        return [
            sum(mixing[i][j] * latent[j] for j in range(self.dim))
            + rng.gauss(0, self.noise)
            for i in range(self.dim)
        ]

    def project(self, observation: list[float], *, modality: int) -> list[float]:
        """Where a modality's observation lands in the shared space."""
        weights = self._left if modality == 0 else self._right
        return [
            sum(weights[i][j] * observation[j] for j in range(self.dim))
            for i in range(self.dim)
        ]

    # ── learning ───────────────────────────────────────────────────────────
    def step(self) -> None:
        """Take one co-occurring pair and nudge both projections together.

        The rule is local: each projection moves toward the midpoint of where
        the two currently land. Nothing computes a global score, which is what
        keeps the refused Phi-optimizer out.

        Returns nothing on purpose, unlike the engines. Learning is cheap and
        scoring is not — `state` re-measures every held-out pair — so returning
        a reading from every step would make a run of a few thousand pairs
        thousands of times more expensive than the learning it is doing.
        """
        concept = self._rng.randrange(self.concepts)
        partner = concept
        if self.shuffled:
            # Same observations, wrong partner — co-occurrence removed.
            partner = self._rng.randrange(self.concepts)

        left_view = self.observe(concept, modality=0)
        right_view = self.observe(partner, modality=1)
        here = self.project(left_view, modality=0)
        there = self.project(right_view, modality=1)
        midpoint = [(here[i] + there[i]) / 2 for i in range(self.dim)]

        for i in range(self.dim):
            left_error = midpoint[i] - here[i]
            right_error = midpoint[i] - there[i]
            for j in range(self.dim):
                self._left[i][j] += self.rate * left_error * left_view[j]
                self._right[i][j] += self.rate * right_error * right_view[j]

        if self.contrast:
            self._push_apart(concept, here)

        self._pairs += 1

    def _push_apart(self, concept: int, here: list[float]) -> None:
        """The other half of what co-occurrence says: this did NOT come with it.

        The same local rule with its sign reversed — move the non-partner's
        projection away from where the partner landed instead of toward it.
        Nothing global is computed, so this is still the pairing teaching the
        projections rather than an objective being optimized.
        """
        other = self._rng.randrange(self.concepts)
        if other == concept:
            return  # not a non-partner
        view = self.observe(other, modality=1)
        there = self.project(view, modality=1)
        gap = math.dist(there, here)
        if gap >= self.margin:
            return  # already far enough; an unbounded push has no scale to stop at
        for i in range(self.dim):
            away = (there[i] - here[i]) / max(gap, 1e-9)
            for j in range(self.dim):
                self._right[i][j] += self.rate * self.contrast * away * view[j]

    def run(self, pairs: int) -> AlignState:
        """Learn from `pairs` pairs, then measure once."""
        if pairs < 1:
            raise ValueError(f"pairs must be >= 1, got {pairs}")
        for _ in range(pairs):
            self.step()
        return self.state

    # ── reading ────────────────────────────────────────────────────────────
    @property
    def pairs_seen(self) -> int:
        return self._pairs

    @property
    def state(self) -> AlignState:
        """Scored on held-out concepts only — reading does not train."""
        return self._measure()

    def _measure(self) -> AlignState:
        # The world never changes, so the held-out observations are the same

exec
/bin/zsh -lc "rg -n \"class CoupledEngine|def __init__|def step|def reset|chain|def recurrence_evidence|class RecurrenceEvidence|def representation|class Representation|def signature|def coupled_phi\" src/anima_reborn/coupled.py src/anima_reborn/substrate.py
rg -n \"effective|rank|width|participation|capacity|forget|null|shift|cross|pair\" state/communication/*.py tests/test_coupled.py tests/test_substrate.py tests/test_align.py | sed -n '1,320p'" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
src/anima_reborn/substrate.py:168:    def step(state: int, rng: random.Random) -> int:
src/anima_reborn/substrate.py:329:    chain: float = 0.0,
src/anima_reborn/substrate.py:357:    def step(state: int, rng: random.Random) -> int:
src/anima_reborn/substrate.py:361:            chain=chain,
src/anima_reborn/substrate.py:376:def coupled_phi(
src/anima_reborn/substrate.py:380:    chain: float = 0.0,
src/anima_reborn/substrate.py:411:        chain=chain,
src/anima_reborn/substrate.py:452:class Representation:
src/anima_reborn/substrate.py:484:def signature(
src/anima_reborn/substrate.py:527:def representation(
src/anima_reborn/substrate.py:597:class RecurrenceEvidence:
src/anima_reborn/substrate.py:641:def recurrence_evidence(
src/anima_reborn/coupled.py:149:    """Cross-coupled pairs, each a two-unit latch, optionally chained.
src/anima_reborn/coupled.py:307:class CoupledEngine:
src/anima_reborn/coupled.py:316:        chain: How much of a unit's partner-response is replaced by the same
src/anima_reborn/coupled.py:336:    def __init__(
src/anima_reborn/coupled.py:343:        chain: float = 0.0,
src/anima_reborn/coupled.py:355:        if not 0.0 <= chain <= 1.0:
src/anima_reborn/coupled.py:356:            raise ValueError(f"chain must be in [0, 1], got {chain}")
src/anima_reborn/coupled.py:359:        self.chain = chain
src/anima_reborn/coupled.py:423:    def step(self) -> CoupledState:
src/anima_reborn/coupled.py:444:            if self.chain:
src/anima_reborn/coupled.py:445:                # Left alone at chain 0, so the wirings are what they always
src/anima_reborn/coupled.py:452:                partner = (1.0 - self.chain) * partner + self.chain * along
src/anima_reborn/coupled.py:501:    def reset(self) -> None:
state/communication/english_bottleneck.py:23:capacity, only overclaim). This takes sol's fixed closed corpus + exact categorical MI (no
state/communication/english_bottleneck.py:32:  is not noise, it is capacity.
state/communication/english_bottleneck.py:35:- the effective output width 2^H(Y) beside every number (`report-the-rank`).
state/communication/english_bottleneck.py:37:Arms (each its own null):
state/communication/english_bottleneck.py:93:def _mutual_information(pairs: list[tuple]) -> float:
state/communication/english_bottleneck.py:94:    """Exact categorical MI in bits over observed (a, b) pairs — plug-in estimator."""
state/communication/english_bottleneck.py:95:    n = len(pairs)
state/communication/english_bottleneck.py:98:    joint = Counter(pairs)
state/communication/english_bottleneck.py:99:    marg_a = Counter(a for a, _ in pairs)
state/communication/english_bottleneck.py:100:    marg_b = Counter(b for _, b in pairs)
state/communication/english_bottleneck.py:110:def _permutation_floor(pairs: list[tuple], trials: int = 200) -> float:
state/communication/english_bottleneck.py:111:    """The MI a shuffled pairing yields — the finite-sample bias floor. A real MI must clear
state/communication/english_bottleneck.py:113:    a_vals = [a for a, _ in pairs]
state/communication/english_bottleneck.py:114:    b_vals = [b for _, b in pairs]
state/communication/english_bottleneck.py:206:        pairs = math.ceil(bits)
state/communication/english_bottleneck.py:207:        print(f"    a {n_words}-word utterance needs {bits:.0f} bits = {pairs} latches "
state/communication/english_bottleneck.py:208:              f"= {2 * pairs} units; Φ is unmeasurable past ~6 units (3 pairs), so beyond 3 "
state/communication/match.py:7:`silence.py` established that the ring holds one bit across silence and that the
state/communication/match.py:29:16-k across the two basins, perfect use of the held bit scores
state/communication/match.py:41:nothing across silence (measured: they fall to their fixed points by 20 and 120
state/communication/match.py:161:    print(f"basin split across drives : {split}")
state/communication/attractor_canonicalization.py:13:hashes of the same word share no information — measured across 4000 words, their
state/communication/attractor_canonicalization.py:14:mutual information is 0.0185 bits against a shuffled null of 0.0212. Identical.
state/communication/attractor_canonicalization.py:42:"""Two orthogonal patterns, so four basins counting sign. Hopfield capacity is
state/communication/attractor_canonicalization.py:110:    """Mutual information between two hashes of the same word, and its null."""
state/communication/attractor_canonicalization.py:138:    observed, null = independent_encodings_share_nothing()
state/communication/attractor_canonicalization.py:141:    print(f"  shuffled null      : {null:.4f} bits")
state/communication/attractor_canonicalization.py:148:        pairs = [two_views(w, noise) for w in WORDS]
state/communication/attractor_canonicalization.py:150:            basin(settle(a, gain=4)) == basin(settle(b, gain=4)) for a, b in pairs
state/communication/attractor_canonicalization.py:154:            for a, b in pairs
state/communication/attractor_canonicalization.py:156:        n = len(pairs)
state/communication/attractor_canonicalization.py:162:    pairs = [two_views(w, 1.5) for w in WORDS]
state/communication/attractor_canonicalization.py:164:        landed = [basin(settle(a, gain=gain)) for a, _ in pairs]
state/communication/attractor_canonicalization.py:167:            basin(settle(a, gain=gain)) == basin(settle(b, gain=gain)) for a, b in pairs
state/communication/attractor_canonicalization.py:168:        ) / len(pairs)
state/communication/dialogue.py:13:  seedable stand-in for the human, so 12-seed directional bars and every null are
state/communication/dialogue.py:31:see across the gap. In the viewer the display becomes the second aperture (raw
state/communication/dialogue.py:137:def _cross_direction_consistency(policies) -> float:
state/communication/dialogue.py:168:        _cross_direction_consistency(d["policies"]) for d in dyads
state/communication/dialogue.py:186:    print(f"{'partner swap (all cross)':<28}{statistics.mean(swapped):>10.3f}"
state/communication/dialogue.py:188:    print(f"\n  cross-direction consistency: {consistency:.0%} "
state/communication/alternating_coupling.py:99:    # so tau is printed per row and a comparison across two of them is not a
state/communication/capacity.py:5:    PYTHONPATH=src python state/communication/capacity.py
state/communication/capacity.py:9:and it does not: **a single ring of ANY even width holds exactly one bit.**
state/communication/capacity.py:14:width. Capacity therefore lives in the CYCLE STRUCTURE of the wiring rather than
state/communication/capacity.py:18:**Odd rings are a different animal and not a way out.** With an odd width there
state/communication/capacity.py:22:6, 10 and 14 patterns at widths 3, 5 and 7, exactly `2N`. But a phase is a
state/communication/capacity.py:24:of being held: at width 3 only 0% of drives land reproducibly, at 5 only 6%, at
state/communication/capacity.py:25:7 only 19%. Even widths hold one bit forever; odd widths hold more of something
state/communication/capacity.py:28:**What counts as capacity here.** Only states the DRIVE reproduces. A pattern
state/communication/capacity.py:31:`WALKS` independent walks land on the same pattern, and capacity is the number
state/communication/capacity.py:35:pattern count grows with width, add units. If it is pinned at two while pairs
state/communication/capacity.py:82:def capacity(
state/communication/capacity.py:103:    reachable, held, share = capacity(units, wiring=wiring, chain=chain)
state/communication/capacity.py:112:    print(f"capacity — {WALKS} walks per drive, tell {TELL}, deaf silence {SILENCE}")
state/communication/capacity.py:127:        pairs = units // 2
state/communication/capacity.py:129:            f"{pairs} pairs, chain {chain:.1f}"
state/communication/capacity.py:130:            f"{' (odd k)' if pairs % 2 else ' (even k)'}",
state/communication/capacity.py:137:        "\nThe ring is pinned at two held states whatever its width, which is the"
state/communication/capacity.py:138:        "\ntheorem showing up as a measurement. Odd widths reach more patterns and"
state/communication/capacity.py:140:        "\nCapacity is the wiring's cycle structure, so the way up is pairs."
state/communication/capacity.py:144:        "\nself-wired null and does not transfer. The artefact grows with width, so"
state/communication/capacity.py:147:        "\nsurvives the change of width."
state/communication/concepts.py:16:while measuring as reducible (the null that collapses 5.2 -> 2.1). So "concepts
state/communication/concepts.py:19:place integration can be a FUNCTION rather than a coincidence is the cross-pair
state/communication/concepts.py:20:probe (Phase C): a probe that differs only within pair 0 can move pairs 1-2 only
state/communication/concepts.py:23:**What addresses a latch.** With `Wiring.PAIRS` each pair j is units (2j, 2j+1),
state/communication/concepts.py:169:# ── Phase B: does the aligned CONCEPT survive silence, across modalities? ──
state/communication/concepts.py:171:    print("Phase B — the aligned concept surviving silence, read across modalities")
state/communication/concepts.py:174:        "cross-modal agreement is the headline: a concept told through modality 0"
state/communication/concepts.py:180:        f"{'arm':<20}{'cross-modal':>12}{'worst seed':>12}"
state/communication/concepts.py:226:        "\n  which measure as reducible) holds the concept across modalities just as"
state/communication/concepts.py:235:    """The cross-pair probe. A probe that differs only within pair 0 can move
state/communication/concepts.py:236:    pairs 1-2 only through the chain; at chain=0 that response is exactly zero by
state/communication/concepts.py:238:    print("Phase C — cross-pair response: is integration a function, not a coincidence?")
state/communication/concepts.py:239:    print("a probe differing only in pair 0; measure how much pairs 1-2 move\n")
state/communication/concepts.py:240:    print(f"{'chain':<10}{'pairs 1-2 response':>20}   reading")
state/communication/concepts.py:254:                flipped[0], flipped[1] = held[1], held[0]  # flip pair 0 only
state/communication/concepts.py:256:                # response of pairs 1-2 to a pair-0-only change
state/communication/concepts.py:266:        "\n  chain=0 is zero BY CONSTRUCTION (no causal path between pairs), so a"
state/communication/concepts.py:288:    """Total movement of pairs 1-2 over a probe cycle, from a given start."""
state/communication/integration_vs_representation.py:47:"""`substrate.RECURRENCE_FLOOR` — measured against the uncoupled null."""
state/communication/integration_vs_representation.py:111:    Returns (same word across encodings, different words within one encoding).
tests/test_align.py:11:the training pairs, and an untrained baseline that is not zero.
tests/test_align.py:24:def learned(*, shuffled: bool = False, pairs: int = 4000, seeds: int = 8, **kwargs):
tests/test_align.py:26:        Aligner(shuffled=shuffled, seed=s, **kwargs).run(pairs).learned
tests/test_align.py:37:    def test_destroying_the_pairing_kills_it(self) -> None:
tests/test_align.py:39:        pairing is wrong, so there is no co-occurrence to learn from."""
tests/test_align.py:63:        """A learner that memorized pairs could not generalize from ten. One
tests/test_align.py:173:        already achieved, so one direction runs away and the effective rank goes
tests/test_align.py:177:        assert _rank(1, contrast=0.3, margin=1e9, cls=_Unscaled) < 1.05
tests/test_align.py:183:        over six seeds at `dim=4`: rank 1.21 with no push, 1.00 unscaled, 1.12
tests/test_align.py:186:            _rank(s, contrast=0.3, margin=1e9) for s in range(4)
tests/test_align.py:189:            _rank(s, contrast=0.3, margin=1.0) for s in range(4)
tests/test_align.py:195:        without = statistics.mean(_rank(s) for s in range(4))
tests/test_align.py:197:            _rank(s, contrast=0.3, margin=1.0) for s in range(4)
tests/test_align.py:203:        signals rather than teaching from the pairing."""
tests/test_align.py:229:def _rank(seed: int, *, cls: type[Aligner] = Aligner, **kwargs) -> float:
tests/test_align.py:255:    def test_reset_forgets_what_was_learned(self) -> None:
tests/test_align.py:261:        assert aligner.pairs_seen == 0
tests/test_align.py:268:        before = aligner.pairs_seen
tests/test_align.py:271:        assert aligner.pairs_seen == before
tests/test_align.py:273:    def test_projections_have_the_declared_width(self) -> None:
tests/test_align.py:288:        with pytest.raises(ValueError, match="pairs must be >= 1"):
state/communication/conversation_channel.py:8:ring: `Wiring.PAIRS` (6 units, 3 odd pairs, `chain=0.2`), proven in `capacity.py` to hold
state/communication/conversation_channel.py:16:- **per-bit fidelity** = P(decoded latch bit == driven bit), each of the 3 pairs, over all
state/communication/conversation_channel.py:17:  8 symbols and many seeds. Each pair is addressed only through its differential
state/communication/conversation_channel.py:20:  `capacity.py` reported as ~88%.
state/communication/conversation_channel.py:21:- **the deaf null**: coupling 1.0 for the whole run makes the drive bit-unreachable, so the
state/communication/conversation_channel.py:41:    """Per-unit drive: pair j is pushed to sign +/- by bit j of the symbol."""
state/communication/conversation_channel.py:49:def pairs_word(symbol: int, *, seed: int, tell: int, hold: int, deaf: bool = False) -> int:
state/communication/conversation_channel.py:50:    """Drive the 3 pairs for `symbol`, hold, and read the 3 differential sign bits."""
state/communication/conversation_channel.py:74:            word = pairs_word(symbol, seed=seed * 13 + 1, tell=tell, hold=hold, deaf=deaf)
state/communication/conversation_channel.py:85:    print("3-bit PAIRS channel calibration — 6 units, 3 odd pairs, chain=0.2")
state/communication/conversation_channel.py:102:    # The deaf null at a representative setting — the channel must be in the path.
state/communication/aligned_drive.py:20:The measurement is cross-modal identification on held-out concepts. Build a
state/communication/aligned_drive.py:33:  directions would improve separation without pairing teaching anything, so
state/communication/aligned_drive.py:35:- The architecture. `untrained` is the same projections at zero pairs.
state/communication/aligned_drive.py:40:  nothing; that is what killed the attractor route. Effective rank of the
state/communication/aligned_drive.py:55:its wrong partner independently, so about 1 pair in `concepts` is accidentally
state/communication/aligned_drive.py:62:Walk seeds are crossed with concepts rather than assigned to them, so nothing
state/communication/aligned_drive.py:96:0.535-0.583 across contrast 0.1-0.6 and margin 0.5-2.0, against 0.418 without
state/communication/aligned_drive.py:99:drives the effective rank to exactly 1.00."""
state/communication/aligned_drive.py:160:def effective_rank(points: list[list[float]]) -> float:
state/communication/aligned_drive.py:178:    """Cross-modal identification, its permutation floor, and effective rank."""
state/communication/aligned_drive.py:187:        effective_rank(list(prototypes.values())),
state/communication/aligned_drive.py:192:"""Engine walks per drive, crossed with concepts. Six matches the six
state/communication/aligned_drive.py:262:        f"cross-modal identification on {len(HELD_OUT)} held-out concepts, "
state/communication/aligned_drive.py:265:    print(f"dim={DIM}, {PAIRS} pairs, {SEEDS} seeds, chance = 1/{len(HELD_OUT)}\n")
state/communication/aligned_drive.py:268:    ranks: dict[str, list[float]] = {}
state/communication/aligned_drive.py:290:        for name, (accuracy, floor, rank) in readings.items():
state/communication/aligned_drive.py:292:            ranks.setdefault(name, []).append(rank)
state/communication/aligned_drive.py:295:    print(f"{'arm':<12}{'accuracy':>12}{'worst seed':>13}{'eff. rank':>12}")
state/communication/aligned_drive.py:300:            f"{min(arms[name]):>13.3f}{statistics.mean(ranks[name]):>12.2f}"
state/communication/aligned_drive.py:331:        f"RING, {WALKS} crossed walks per drive, 800 ticks, tail 300, "
tests/test_coupled.py:32:from anima_reborn.iit4.ei import average_effective_information
tests/test_coupled.py:44:self-wired null still reads ~0.27 here, which is why recurrence is claimed from
tests/test_coupled.py:67:        assert not evidence.held, "the null must collapse with more sampling"
tests/test_coupled.py:78:        self-wired null reads well above zero at any finite trial count."""
tests/test_coupled.py:91:    def test_the_null_floor_decays_with_sampling(self) -> None:
tests/test_coupled.py:113:    def test_the_floor_is_measured_against_the_null(self) -> None:
tests/test_coupled.py:302:        ei = average_effective_information(
tests/test_coupled.py:320:        null_ei, null_phi = self.measure(Wiring.SELF)
tests/test_coupled.py:323:        assert null_phi < 0.5
tests/test_coupled.py:325:        assert null_ei > ring_ei / 2, (null_ei, ring_ei)
state/communication/silence.py:24:  It is the null that says how much retention is merely "not yet cold".
state/communication/silence.py:28:apart the states still are; effective rank and the count of distinct
state/communication/silence.py:35:capacity in deaf silence is therefore ONE BIT by construction, not a concept
state/communication/silence.py:65:"""Ticks summarized, one whole cycle, fixed across every delay. A window that
state/communication/silence.py:117:def effective_rank(points: list[list[float]]) -> float:
state/communication/silence.py:185:    print(f"{'silence':>8}{'eff. rank':>12}{'sign-patterns':>16}{'width kept':>13}")
state/communication/silence.py:187:    width_at_zero: float | None = None
state/communication/silence.py:189:        ranks, patterns = [], []
state/communication/silence.py:197:            ranks.append(effective_rank(points))
state/communication/silence.py:199:        rank = statistics.mean(ranks)
state/communication/silence.py:200:        if width_at_zero is None:
state/communication/silence.py:201:            width_at_zero = rank
state/communication/silence.py:202:        # Against its OWN width at the moment the telling stopped, rather than a
state/communication/silence.py:205:        kept = (rank - 1.0) / max(width_at_zero - 1.0, 1e-9)
state/communication/silence.py:207:            f"{silence:>8}{rank:>12.2f}"

exec
/bin/zsh -lc "sed -n '330,530p' src/anima_reborn/coupled.py
sed -n '300,720p' src/anima_reborn/substrate.py
sed -n '1,190p' state/communication/capacity.py
sed -n '1,360p' state/communication/concepts.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
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
    macro_step: int
    trials: int

    @property
    def is_reducible(self) -> bool:
        """Exactly zero directed Phi — some direction severs for free.

        This direction is safe to read off one measurement: a sampled matrix can
        invent structure but cannot invent its absence, so a zero here is a zero.
        The opposite claim is not symmetric, which is why there is no
        `is_recurrent` — see `recurrence_evidence`.
        """
        return self.directed_phi == 0.0

    def __str__(self) -> str:
        entity = f"{self.complex_units:04b}" if self.complex_units else "none"
        return (
            f"{self.wiring.value:<12} phi={self.phi:6.3f} "
            f"directed={self.directed_phi:6.3f} "
            f"{'[reducible]' if self.is_reducible else '           '} "
            f"complex={entity} (state {self.state:04b}, tau={self.macro_step}, "
            f"{self.trials} trials)"
        )


def coupled_matrix(
    wiring: Wiring = Wiring.RING,
    *,
    units: int = UNITS,
    chain: float = 0.0,
    rhythm: Rhythm = FIXED,
    drive: float = 0.0,
    macro_step: int | None = None,
    gain: float = GAIN,
    amplitude: float = AMPLITUDE,
    trials: int = TRIALS,
    seed: int | None = None,
) -> TransitionMatrix:
    """Measure the coupled engine's transition matrix.

    One transition is `macro_step` engine ticks: reconstruct the units to
    +/-`amplitude` from the state, run, threshold at zero. Reconstruction
    amplitude and macro-step both sit inside the result.

    A rhythm must be measured over a whole listen/integrate cycle, so the
    default macro-step follows the rhythm rather than the module constant. Half
    a cycle would report one phase's matrix and label it the engine's.
    """
    if macro_step is None:
        macro_step = rhythm.macro_step
    if macro_step < 1:
        raise ValueError(f"macro_step must be >= 1, got {macro_step}")
    if units > MAX_UNITS:
        raise ValueError(
            f"units must be <= {MAX_UNITS} to stay measurable, got {units}"
        )

    def step(state: int, rng: random.Random) -> int:
        engine = CoupledEngine(
            wiring=wiring,
            units=units,
            chain=chain,
            rhythm=rhythm,
            drive=drive,
            gain=gain,
            amplitude=amplitude,
            seed=rng.getrandbits(63),
            initial=tuple(
                amplitude if state >> i & 1 else -amplitude for i in range(units)
            ),
        )
        return engine.run(macro_step).pattern

    return estimate_matrix(units, step, trials=trials, seed=seed)


def coupled_phi(
    wiring: Wiring = Wiring.RING,
    *,
    units: int = UNITS,
    chain: float = 0.0,
    rhythm: Rhythm = FIXED,
    drive: float = 0.0,
    state: int = 0b0101,
    macro_step: int | None = None,
    gain: float = GAIN,
    amplitude: float = AMPLITUDE,
    trials: int = TRIALS,
    seed: int | None = None,
    with_complex: bool = True,
) -> CoupledReading:
    """Measure the coupled engine's integration.

    Args:
        wiring: Which engine to measure. Pass `Wiring.SELF` or
            `Wiring.FEEDFORWARD` for the falsifiers.
        rhythm: When the units read each other. Integration is a property of the
            engine *including its rhythm*, so this sits in the reading.
        drive: What the engine is being told while measured.
        state: Which pattern to measure at — Phi belongs to a system *in a
            state*. The default is the ring's own attractor.
        macro_step: Engine ticks per measured transition. Defaults to the
            rhythm's own cycle. At 1 every wiring reads exactly zero; see
            `coupled.MACRO_STEP`.
        trials: Samples per state. The artefact floor falls with this.
    """
    if macro_step is None:
        macro_step = rhythm.macro_step
    matrix = coupled_matrix(
        wiring,
        units=units,
        chain=chain,
        rhythm=rhythm,
        drive=drive,
        macro_step=macro_step,
        gain=gain,
        amplitude=amplitude,
        trials=trials,
        seed=seed,
    )
    undirected: SystemPhi = big_phi(matrix, state)
    directed: DirectedPhi = directed_big_phi(matrix, state)
    entity: Complex | None = find_complex(matrix, state) if with_complex else None

    return CoupledReading(
        wiring=wiring,
        phi=undirected.phi,
        directed_phi=directed.phi,
        complex_units=entity.units if entity else 0,
        state=state,
        macro_step=macro_step,
        trials=trials,
    )


REPRESENTATION_TICKS = 800
"""Ticks per trajectory. Long enough that the ring has settled into whatever it
settles into, so the reading is not about the transient."""

REPRESENTATION_TAIL = 300
"""Ticks summarized, taken from the end. Mean AND variability per unit, because
an alternating engine never stops moving and its position alone throws away what
its motion keeps."""

NOISE_SEEDS = 12
"""Repeats of ONE drive under different walks — the within-drive spread that the
between-drive spread has to beat. This is the null, and it is structural rather
than chosen: at a ratio of 1.0 the drives separate exactly as much as the same
drive separates from itself."""


@dataclass(frozen=True, slots=True)
class Representation:
    """How much of what an engine was told survives in what it does.

    Two spreads, in the same units. `by_drive` is how far apart different drives
    put the engine; `by_noise` is how far apart ONE drive puts it across
    different walks. Their ratio is the reading, and 1.0 is the floor by
    construction rather than by choice.
    """

    by_drive: float
    by_noise: float
    drives: int
    ticks: int

    @property
    def ratio(self) -> float:
        return self.by_drive / max(self.by_noise, 1e-9)

    @property
    def represents(self) -> bool:
        """Whether the drive is recoverable from the trajectory at all."""
        return self.ratio > 1.0

    def __str__(self) -> str:
        return (
            f"representation={self.ratio:6.2f} "
            f"(between {self.by_drive:.4f} / within {self.by_noise:.4f}, "
            f"{self.drives} drives, {self.ticks} ticks)"
            f"{'' if self.represents else ' [at the noise floor]'}"
        )


def signature(
    drive: float | Sequence[float],
    *,
    wiring: Wiring = Wiring.RING,
    rhythm: Rhythm = FIXED,
    seed: int = 0,
    ticks: int = REPRESENTATION_TICKS,
    tail: int = REPRESENTATION_TAIL,
    gain: float = GAIN,
    amplitude: float = AMPLITUDE,
) -> list[float]:
    """What an engine told `drive` does, as `UNITS` means then `UNITS` spreads.

    The tail of the trajectory rather than its endpoint, and its variability
    alongside its position — an engine running a rhythm never stops moving, and
    where it is throws away what its motion keeps. Public because a caller
    asking "does what I told it survive" needs the same summary `representation`
    scores, and a second copy of it would drift.
    """
    engine = CoupledEngine(
        wiring=wiring,
        rhythm=rhythm,
        drive=drive,
        gain=gain,
        amplitude=amplitude,
        seed=seed,
        initial=(0.0,) * UNITS,
    )
    recent: list[tuple[float, ...]] = []
    for tick in range(ticks):
        values = engine.step().values
        if tick >= ticks - tail:
            recent.append(values)
    return [
        statistics.mean(point[i] for point in recent) for i in range(UNITS)
    ] + [statistics.pstdev([point[i] for point in recent]) for i in range(UNITS)]


def _spread(points: Sequence[Sequence[float]]) -> float:
    centre = [statistics.mean(p[i] for p in points) for i in range(len(points[0]))]
    return statistics.mean(math.dist(p, centre) for p in points)


def representation(
    drives: Sequence[float | Sequence[float]],
    *,
    wiring: Wiring = Wiring.RING,
    rhythm: Rhythm = FIXED,
    seed: int = 1,
    noise_seeds: int = NOISE_SEEDS,
    ticks: int = REPRESENTATION_TICKS,
    tail: int = REPRESENTATION_TAIL,
    gain: float = GAIN,
    amplitude: float = AMPLITUDE,
) -> Representation:
    """Measure how much of its drive an engine's trajectory still carries.

    The other half of the wall. `coupled_phi` says whether the engine is
    irreducible; this says whether anything it was told is still in it. On a
    fixed coupling the two trade off monotonically and there is no setting where
    both hold — which is why `Rhythm` exists.

    Args:
        drives: What to tell the engine, one value per trial, in [-1, 1].
        rhythm: When the units read each other. This is the argument the
            measurement is about.
        seed: Fixes the walk for the between-drive comparison, so different
            drives differ by their drive and not by their noise.
        noise_seeds: Repeats of `drives[0]` that form the within-drive null.
    """
    if len(drives) < 2:
        raise ValueError(f"drives must have at least 2 values, got {len(drives)}")
    if noise_seeds < 2:
        raise ValueError(f"noise_seeds must be >= 2, got {noise_seeds}")
    if tail < 2 or tail > ticks:
        raise ValueError(f"tail must be in [2, {ticks}], got {tail}")

    def measure(drive: float | Sequence[float], walk: int) -> list[float]:
        return signature(
            drive,
            wiring=wiring,
            rhythm=rhythm,
            seed=walk,
            ticks=ticks,
            tail=tail,
            gain=gain,
            amplitude=amplitude,
        )

    return Representation(
        by_drive=_spread([measure(d, seed) for d in drives]),
        by_noise=_spread([measure(drives[0], w) for w in range(noise_seeds)]),
        drives=len(drives),
        ticks=ticks,
    )


RECURRENCE_FLOOR = 1.0
"""Directed Phi a wiring must clear before recurrence is entertained.

Measured against the null rather than picked: four units reading only
themselves, where the true value is exactly zero, produce 0.251 mean and 0.547
worst over eight seeds at 400 trials, decaying to 0.037 at 25600. This bar is
above every one of those, and the ring measures ~9.9 — a factor of sixty.

Verified separately that the measure itself is not the source: on an exactly
factorized transition matrix, built analytically with no sampling at all, both
`big_phi` and `directed_big_phi` return 0.000000. The residue is sampling, and
sampling alone.
"""


@dataclass(frozen=True, slots=True)
class RecurrenceEvidence:
    """Whether integration survives being looked at harder.

    A single positive Phi means nothing on its own: at 6400 trials the
    self-wired null — four units reading only themselves, no coupling anywhere —
    still measures 0.031 directed. Sampling noise manufactures structure, and a
    bare threshold would call that recurrence.

    What separates signal from floor is the same discipline the rest of the repo
    uses: measure twice and see whether it shrinks. Artefacts halve as trials
    grow; a real coupling does not.
    """

    coarse: CoupledReading
    fine: CoupledReading

    @property
    def held(self) -> bool:
        """The directed value survived a fourfold increase in sampling."""
        return self.fine.directed_phi > self.coarse.directed_phi / 2

    @property
    def is_recurrent(self) -> bool:
        """Integration that is substantial AND did not shrink.

        Both conditions, because either alone is fooled. The magnitude bar of
        `RECURRENCE_FLOOR` is measured, not chosen: the self-wired null — no
        coupling anywhere, true Phi exactly zero — reads 0.251 / 0.155 / 0.081 /
        0.037 mean over eight seeds at 400 / 1600 / 6400 / 25600 trials, with a
        worst seed of 0.547. The bar sits nearly twice that worst case.
        """
        return self.fine.directed_phi > RECURRENCE_FLOOR and self.held

    def __str__(self) -> str:
        trend = "held" if self.held else "collapsed"
        return (
            f"{self.coarse.wiring.value:<12} "
            f"{self.coarse.trials}->{self.fine.trials} trials: "
            f"{self.coarse.directed_phi:.3f} -> {self.fine.directed_phi:.3f} "
            f"({trend}) "
            f"{'RECURRENT' if self.is_recurrent else 'not established'}"
        )


def recurrence_evidence(
    wiring: Wiring = Wiring.RING,
    *,
    trials: int = TRIALS,
    factor: int = 4,
    **kwargs: Any,
) -> RecurrenceEvidence:
    """Measure a wiring twice and report whether its integration held.

    Recurrence is not readable from one number, so this refuses to return one.
    Any keyword `coupled_phi` accepts is forwarded to both measurements.
    """
    if factor < 2:
        raise ValueError(f"factor must be >= 2, got {factor}")
    return RecurrenceEvidence(
        coarse=coupled_phi(wiring, trials=trials, with_complex=False, **kwargs),
        fine=coupled_phi(wiring, trials=trials * factor, with_complex=False, **kwargs),
    )


def estimate_state_matrix(
    n: int,
    step: Callable[[int, random.Random], int],
    *,
    trials: int = TRIALS,
    seed: int | None = None,
) -> list[list[float]]:
    """Measure a process's state-to-state transition matrix.

    A different object from `estimate_matrix`, which records each unit's ON
    frequency and assumes the units are conditionally independent. This counts
    whole successor states, which is what `iit4.ei` needs — the two lanes take
    different inputs and are not views of one thing.

    Rows sum to one by construction.
    """
    if not 1 <= n <= MAX_UNITS:
        raise ValueError(f"n must be in [1, {MAX_UNITS}], got {n}")
    if trials < 1:
        raise ValueError(f"trials must be >= 1, got {trials}")

    rng = random.Random(seed)
    states = 1 << n
    matrix = []
    for state in range(states):
        counts = [0] * states
        for _ in range(trials):
            counts[step(state, rng)] += 1
        matrix.append([count / trials for count in counts])
    return matrix
"""How much can it hold, and does adding units help? No — change the topology.

Run from the repo root:

    PYTHONPATH=src python state/communication/capacity.py

`silence.py` and `match.py` established that the four-unit ring holds one bit and
uses it. The obvious next move was more units. This measures whether that works,
and it does not: **a single ring of ANY even width holds exactly one bit.**

That is a theorem before it is a measurement. Each unit's response is odd,
decreasing and bounded, so it has no periodic orbit longer than two; closing the
cycle admits only the alternating configuration and its negation, for every even
width. Capacity therefore lives in the CYCLE STRUCTURE of the wiring rather than
in the unit count, and the most a one-source-per-unit engine can hold is
`units / 2` bits — via `units / 2` two-cycles, which is `Wiring.PAIRS`.

**Odd rings are a different animal and not a way out.** With an odd width there
is no consistent assignment to fall into: the origin is the only fixed point and
it is unstable with complex eigenvalues, so the engine spirals out and saturation
bounds it into a limit cycle. Its sign shadow is a `2 * units` cycle — measured
6, 10 and 14 patterns at widths 3, 5 and 7, exactly `2N`. But a phase is a
NEUTRAL direction with no restoring force, so it diffuses under the walk instead
of being held: at width 3 only 0% of drives land reproducibly, at 5 only 6%, at
7 only 19%. Even widths hold one bit forever; odd widths hold more of something
that is drifting away. Both are reported, neither is quoted alone.

**What counts as capacity here.** Only states the DRIVE reproduces. A pattern
reached under one walk and not another is the walk's, not the concept's — the
trap `silence.py` was written to catch — so a drive counts only when all
`WALKS` independent walks land on the same pattern, and capacity is the number
of distinct patterns among those.

**The pre-registered rule, fixed before the run.** If the ring's reproducible
pattern count grows with width, add units. If it is pinned at two while pairs
read about `2^k`, change the topology. It was pinned.
"""

from __future__ import annotations

import math

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

TELL = 400
SILENCE = 240
WALKS = 8
MAX_DRIVES = 64
"""Cap on how many corner drives are tried. Widths past six have more corners
than are worth enumerating, and a capped sweep that is stated is honest where a
silent truncation would not be."""


def settled(
    units: int, drive: tuple[float, ...], *, wiring: Wiring, chain: float, seed: int
) -> tuple[bool, ...]:
    """The sign pattern left after being told something and then made deaf."""
    engine = CoupledEngine(
        wiring=wiring,
        units=units,
        chain=chain,
        rhythm=ALTERNATING,
        drive=drive,
        seed=seed,
        initial=(0.0,) * units,
    )
    engine.run(TELL)
    engine.rhythm = FIXED  # deaf — the drive cannot be heard at all
    engine.drive = 0.0
    return tuple(v > 0 for v in engine.run(SILENCE).values)


def corners(units: int) -> list[tuple[float, ...]]:
    total = 1 << units
    step = max(1, total // MAX_DRIVES)
    return [
        tuple((((i >> k) & 1) * 2 - 1) * 0.8 for k in range(units))
        for i in range(0, total, step)
    ]


def capacity(
    units: int, *, wiring: Wiring = Wiring.RING, chain: float = 0.0
) -> tuple[int, int, float]:
    """Reachable patterns, reproducible patterns, and the reproducible share."""
    reachable: set[tuple[bool, ...]] = set()
    reproducible: set[tuple[bool, ...]] = set()
    drives = corners(units)
    agreed = 0
    for drive in drives:
        landed = [
            settled(units, drive, wiring=wiring, chain=chain, seed=w)
            for w in range(WALKS)
        ]
        reachable.update(landed)
        if len(set(landed)) == 1:
            agreed += 1
            reproducible.add(landed[0])
    return len(reachable), len(reproducible), agreed / len(drives)


def report(label: str, units: int, *, wiring: Wiring, chain: float = 0.0) -> None:
    reachable, held, share = capacity(units, wiring=wiring, chain=chain)
    bits = math.log2(held) if held else 0.0
    print(
        f"{label:<28}{units:>6}{reachable:>11}{share:>13.0%}{held:>15}{bits:>7.2f}",
        flush=True,
    )


def main() -> None:
    print(f"capacity — {WALKS} walks per drive, tell {TELL}, deaf silence {SILENCE}")
    print("only states the DRIVE reproduces are counted as held\n")
    print(
        f"{'configuration':<28}{'units':>6}{'reachable':>11}{'reproduced':>13}"
        f"{'held states':>15}{'bits':>7}"
    )
    print("-" * 80)

    for units in (4, 6, 8):
        report(f"single ring", units, wiring=Wiring.RING)
    print()
    for units in (3, 5, 7):
        report(f"single ring (odd — spins)", units, wiring=Wiring.RING)
    print()
    for units, chain in ((4, 0.0), (6, 0.0), (6, 0.2), (10, 0.2)):
        pairs = units // 2
        report(
            f"{pairs} pairs, chain {chain:.1f}"
            f"{' (odd k)' if pairs % 2 else ' (even k)'}",
            units,
            wiring=Wiring.PAIRS,
            chain=chain,
        )

    print(
        "\nThe ring is pinned at two held states whatever its width, which is the"
        "\ntheorem showing up as a measurement. Odd widths reach more patterns and"
        "\nreproduce almost none of them — a drifting phase, not a held state."
        "\nCapacity is the wiring's cycle structure, so the way up is pairs."
    )
    print(
        "\nNOTE: `substrate.RECURRENCE_FLOOR` = 1.0 was calibrated on the FOUR-unit"
        "\nself-wired null and does not transfer. The artefact grows with width, so"
        "\nany verdict at six units or more needs its own floor measured first —"
        "\nthe held-under-more-sampling criterion, not the magnitude, is what"
        "\nsurvives the change of width."
    )


if __name__ == "__main__":
    main()
"""The whole chain on the 3-bit integrated substrate — concepts, held and used.

Run from the repo root:

    PYTHONPATH=src python state/communication/concepts.py

Four things were built and measured separately: the ring INTEGRATES, it HOLDS a
bit through silence, it USES what it holds, and `Wiring.PAIRS` with a chain holds
`units/2` bits while still integrating. Each used designed inputs (cube corners)
to isolate the engine from any learner. This joins them: learned concepts on the
six-unit, three-latch, chained engine, asked whether concept identity is held as
more than one bit and whether the engine uses it.

**The confound the composition creates, and how it is handled.** `chain=0` — three
DISJOINT latches — already holds three bits and each latch passes on its own,
while measuring as reducible (the null that collapses 5.2 -> 2.1). So "concepts
on the integrated substrate pass" would earn only *coexistence*, never "integration
carries concepts". `chain=0` therefore ships as a first-class arm, and the only
place integration can be a FUNCTION rather than a coincidence is the cross-pair
probe (Phase C): a probe that differs only within pair 0 can move pairs 1-2 only
through the chain, and at `chain=0` that path is exactly zero by construction.

**What addresses a latch.** With `Wiring.PAIRS` each pair j is units (2j, 2j+1),
an inverting two-cycle whose DIFFERENTIAL `d[2j] - d[2j+1]` is the bistable mode
that writes the bit; the common mode has negative feedback and dies in silence.
So a concept's usable channel is the three differentials, not the full six-vector,
and the aligner's narrowness could collapse them — which is why Phase 0 measures
the aligner's own address rate with no engine in the path before anything else.

**Gates.** Phase 0 kills the whole thing if the aligned code carries no more than
one bit of address (a lossy engine cannot recreate address diversity never fed to
it). Only if it passes do the engine phases run.
"""

from __future__ import annotations

import collections
import math
import statistics

from anima_reborn.align import Aligner
from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

DIM = 6
CONCEPTS = 40
HELD_OUT = list(range(10_000, 10_020))
CONTRAST = 0.3
MARGIN = 1.0
PAIRS = 3
CHAIN = 0.2

TELL = 400
SILENCE = 240
PROBE = 20
WALKS = 8
SAMPLES = 12
SEEDS = 8
PAIRS_ARM = Wiring.PAIRS


def aligned(seed: int, *, shuffled: bool = False, contrast: float = CONTRAST) -> Aligner:
    learner = Aligner(
        dim=DIM, concepts=CONCEPTS, seed=seed, contrast=contrast, margin=MARGIN,
        shuffled=shuffled,
    )
    learner.run(4000)
    return learner


def drive_of(
    learner: Aligner, concept: int, modality: int, sample: int, scale: float
) -> tuple[float, ...]:
    point = learner.project(
        learner.observe(concept, modality=modality, sample=sample), modality=modality
    )
    return tuple(max(-1.0, min(1.0, v / scale)) for v in point)


def training_scale(learner: Aligner, modality: int) -> float:
    biggest = 0.0
    for concept in range(learner.concepts):
        point = learner.project(learner.observe(concept, modality=modality), modality=modality)
        biggest = max(biggest, max(abs(v) for v in point))
    return max(biggest, 1e-9)


def differentials(drive: tuple[float, ...]) -> tuple[float, ...]:
    """The three writable functionals — one per latch."""
    return tuple(drive[2 * j] - drive[2 * j + 1] for j in range(PAIRS))


def address(drive: tuple[float, ...]) -> tuple[bool, ...]:
    return tuple(d > 0 for d in differentials(drive))


# ── Phase 0: can the aligned code even address three latches? (no engine) ──
def phase0() -> bool:
    print("Phase 0 — aligner address rate, no engine in the path")
    print(f"{'arm':<12}{'stable concepts':>16}{'distinct words':>16}{'bits':>7}")
    print("-" * 51)
    verdict = {}
    for name, shuffled in (("trained", False), ("shuffled", True)):
        words, stable, bits = [], [], []
        for seed in range(SEEDS):
            learner = aligned(seed, shuffled=shuffled)
            scale = training_scale(learner, 0)
            seed_words = set()
            seed_stable = 0
            for concept in HELD_OUT:
                addrs = {
                    address(drive_of(learner, concept, 0, s, scale))
                    for s in range(1, SAMPLES + 1)
                }
                if len(addrs) == 1:
                    seed_stable += 1
                    seed_words |= addrs
            words.append(len(seed_words))
            stable.append(seed_stable / len(HELD_OUT))
            bits.append(math.log2(len(seed_words)) if seed_words else 0.0)
        verdict[name] = (statistics.mean(words), statistics.mean(bits))
        print(
            f"{name:<12}{statistics.mean(stable):>15.0%}"
            f"{statistics.mean(words):>16.1f}{statistics.mean(bits):>7.2f}",
            flush=True,
        )
    passed = verdict["trained"][1] > 1.0 and verdict["trained"][0] > verdict["shuffled"][0]
    print(
        f"\n  {'PASS' if passed else 'KILL'}: trained carries "
        f"{verdict['trained'][1]:.2f} bits of address"
        f"{' (> 1, and beats shuffled)' if passed else ' — one bit or less, dead here'}\n"
    )
    return passed


# ── engine helpers ──
def hold(
    learner: Aligner, concept: int, modality: int, *, seed: int, chain: float, scale: float
) -> tuple[bool, ...]:
    """The three latch bits after telling a concept and going deaf."""
    engine = CoupledEngine(
        wiring=PAIRS_ARM, units=DIM, chain=chain, rhythm=ALTERNATING,
        drive=drive_of(learner, concept, modality, 0, scale), seed=seed, initial=(0.0,) * DIM,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    values = engine.run(SILENCE).values
    return tuple((values[2 * j] - values[2 * j + 1]) > 0 for j in range(PAIRS))


def _permuted_floor(held_by_concept, top_by_concept) -> float:
    """Cross-modal agreement with the concept labels shuffled — what this match
    reports for no correspondence. The empirical floor beside the shuffled arm."""
    import random as _random
    concepts = list(top_by_concept)
    rng = _random.Random(17)
    best = 0.0
    for _ in range(200):
        order = list(concepts)
        rng.shuffle(order)
        agree = statistics.mean(
            1.0 if held_by_concept[a] == top_by_concept[b] else 0.0
            for a, b in zip(concepts, order)
        )
        best = max(best, agree)
    return best


# ── Phase B: does the aligned CONCEPT survive silence, across modalities? ──
def phaseB() -> None:
    print("Phase B — the aligned concept surviving silence, read across modalities")
    print(f"tell {TELL}, deaf silence {SILENCE}, {WALKS} walks, {SEEDS} seeds\n")
    print(
        "cross-modal agreement is the headline: a concept told through modality 0"
        "\nand held through silence lands on the same latch word as the same concept"
        "\ntold through modality 1. distinct words is a CONTROL column — shuffled"
        "\nuses just as many, so word count is basin occupancy, not concept memory.\n"
    )
    print(
        f"{'arm':<20}{'cross-modal':>12}{'worst seed':>12}"
        f"{'perm floor':>12}{'words':>7}"
    )
    print("-" * 63)

    for name, shuffled, chain in (
        ("chained (3-bit)", False, CHAIN),
        ("disjoint chain=0", False, 0.0),
        ("shuffled aligner", True, CHAIN),
    ):
        per_seed_agree, per_seed_words, floors = [], [], []
        for seed in range(SEEDS):
            learner = aligned(seed, shuffled=shuffled)
            scale0 = training_scale(learner, 0)
            scale1 = training_scale(learner, 1)
            words = set()
            top_by_concept, held1_by_concept = {}, {}
            for concept in HELD_OUT:
                held0 = [
                    hold(learner, concept, 0, seed=w, chain=chain, scale=scale0)
                    for w in range(WALKS)
                ]
                top, n = collections.Counter(held0).most_common(1)[0]
                if n == WALKS:
                    words.add(top)
                top_by_concept[concept] = top
                held1_by_concept[concept] = hold(
                    learner, concept, 1, seed=0, chain=chain, scale=scale1
                )
            per_seed_agree.append(
                statistics.mean(
                    1.0 if held1_by_concept[c] == top_by_concept[c] else 0.0
                    for c in HELD_OUT
                )
            )
            floors.append(_permuted_floor(held1_by_concept, top_by_concept))
            per_seed_words.append(len(words))
        print(
            f"{name:<20}{statistics.mean(per_seed_agree):>11.0%}"
            f"{min(per_seed_agree):>12.0%}{statistics.mean(floors):>12.0%}"
            f"{statistics.mean(per_seed_words):>7.1f}",
            flush=True,
        )

    print(
        "\n  Storage does NOT require integration: chain=0 (three disjoint latches,"
        "\n  which measure as reducible) holds the concept across modalities just as"
        "\n  well. That is the confound made explicit — passing here is coexistence,"
        "\n  not 'integration carries the concept'. Phase C is where integration is a"
        "\n  function rather than a coincidence.\n"
    )


# ── Phase C: does the integrated whole respond where disjoint parts cannot? ──
def phaseC() -> None:
    """The cross-pair probe. A probe that differs only within pair 0 can move
    pairs 1-2 only through the chain; at chain=0 that response is exactly zero by
    construction, so a nonzero response IS integration acting as function."""
    print("Phase C — cross-pair response: is integration a function, not a coincidence?")
    print("a probe differing only in pair 0; measure how much pairs 1-2 move\n")
    print(f"{'chain':<10}{'pairs 1-2 response':>20}   reading")
    print("-" * 52)

    for chain in (0.0, CHAIN):
        responses = []
        for seed in range(SEEDS):
            learner = aligned(seed)
            scale = training_scale(learner, 0)
            for concept in HELD_OUT[:8]:
                held = list(
                    _hold_state(learner, concept, seed=seed, chain=chain, scale=scale)
                )
                base = _probe_move(held, held, chain=chain, seed=seed)
                flipped = list(held)
                flipped[0], flipped[1] = held[1], held[0]  # flip pair 0 only
                moved = _probe_move(held, flipped, chain=chain, seed=seed)
                # response of pairs 1-2 to a pair-0-only change
                responses.append(abs(moved - base))
        mean = statistics.mean(responses)
        reading = (
            "exactly zero — disjoint parts cannot respond"
            if mean < 1e-9
            else "nonzero — the chain carries the influence"
        )
        print(f"{chain:<10.1f}{mean:>20.6f}   {reading}", flush=True)
    print(
        "\n  chain=0 is zero BY CONSTRUCTION (no causal path between pairs), so a"
        "\n  nonzero chained response is the integrated whole doing what its parts"
        "\n  cannot — the one sentence coexistence cannot fake."
    )


def _hold_state(
    learner: Aligner, concept: int, *, seed: int, chain: float, scale: float
) -> tuple[float, ...]:
    engine = CoupledEngine(
        wiring=PAIRS_ARM, units=DIM, chain=chain, rhythm=ALTERNATING,
        drive=drive_of(learner, concept, 0, 0, scale), seed=seed, initial=(0.0,) * DIM,
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    return engine.run(SILENCE).values


def _probe_move(
    held: list[float], start: list[float], *, chain: float, seed: int
) -> float:
    """Total movement of pairs 1-2 over a probe cycle, from a given start."""
    engine = CoupledEngine(
        wiring=PAIRS_ARM, units=DIM, chain=chain, rhythm=ALTERNATING,
        drive=0.0, seed=seed, initial=tuple(start),
    )
    moved = 0.0
    for _ in range(PROBE):
        values = engine.step().values
        moved += sum((values[i] - held[i]) ** 2 for i in range(2, DIM))
    return moved


def main() -> None:
    if not phase0():
        print("Dead at the aligner. The engine cannot recreate address diversity")
        print("that was never fed to it — the fix is upstream, in align.py.")
        return
    phaseB()
    phaseC()


if __name__ == "__main__":
    main()

codex
The repo confirms an important distinction for the build order: storage already scales in disjoint latches, but the only earned “whole does what parts cannot” result is a local cross-pair influence test. So the first new part should expand meaningful composition without relying on an unvalidated large-width Φ number. I’m checking the channel audit and exact-compatibility tests next.
exec
/bin/zsh -lc "sed -n '1,280p' state/communication/english_bottleneck.py
sed -n '1,190p' state/communication/conversation_channel.py
sed -n '1,330p' tests/test_coupled.py
sed -n '1,230p' tests/test_substrate.py
sed -n '1,260p' src/anima_reborn/conversation.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
"""The honest answer to "make real English conversation possible": measure the bottleneck.

Run from the repo root:

    PYTHONPATH=src python state/communication/english_bottleneck.py

Real English conversation by this engine is impossible, and this proves it with numbers on
actual English strings. The certificate is the data-processing inequality: for
X_English -> C in {0..7} -> C' -> Y,

    I(X; Y) <= I(C; C') <= H(C) <= log2(8) = 3 bits.

Any decoder that produces more detailed English is adding information from its author or the
human operator, not recovering it from the engine. So the only honest "design for real
English" is: let real English ENTER, measure exactly how much SURVIVES the 3-bit carrier,
and close the door on the rest by measurement. An external LLM would make English appear
(and is banned by engine-purity) but would be the LLM conversing while the engine carries
3 bits — the same trap in a bigger costume.

Design delegated to both frontier models and reconciled (`state/lab/2026-07-23-english-*.md`),
which converged: build the measured bottleneck (interpretation 1) as the answer, with the
wall (interpretation 3) as its proof; REFUSE English labels on the cards (they add zero
capacity, only overclaim). This takes sol's fixed closed corpus + exact categorical MI (no
`info.py` float estimator, no deflate proxy, which would be an estimator artefact).

What is measured (a fixed, closed, balanced corpus of 32 two-word commands = 8 verbs x 4
objects; ONLY the verb, 3 bits, is encoded — the object, 2 bits, is never sent):

- I(C; C') / H(C): the carrier — how much of the 3 encoded bits survive the wire.
- I(X; Y) / H(X): end-to-end — how much of the 5-bit sentence CHOICE survives (<= 3/5).
- I(verb; Y) and I(object; Y): the object is unrepresentable, so I(object; Y) ~ 0 — the loss
  is not noise, it is capacity.
- residual ambiguity H(X | Y) and the candidate-set size: given the output the engine cannot
  narrow past the 4 objects it never carried.
- the effective output width 2^H(Y) beside every number (`report-the-rank`).

Arms (each its own null):
- ideal carrier (C' = C): the codec/decoder ceiling, measured BEFORE crediting the substrate
  (`channel-before-carrier`).
- live PAIRS: the measured 3-bit channel (`dialogue.channel`, bits=3, fidelity 1.0).
- deaf: drive bit-unreachable (coupling 1.0) — I(C; C') must fall to ~0, recovery to 1/8,
  proving the engine was in the path.
- codebook scramble: partition the 32 commands into 8 balanced codes IGNORING the verb. This
  keeps I(X; Y) (sentence identity survives) while destroying I(verb; Y) — the proof that
  "3 bits SHARED with English strings" is NOT "3 bits of the intended English meaning".
- label permutation floor: shuffle Y against X to expose the finite-sample MI bias, printed
  beside every I so a small number is not mistaken for signal (`artefact-honesty`).

The engine NARROWS an English choice; it never produces an English reply. The output phrase
is the harness's label for 3 bits, never the engine's speech. Not language, not understanding.
"""

from __future__ import annotations

import math
import random
from collections import Counter

from anima_reborn.dialogue import channel

# A fixed, closed, deliberately tiny corpus. Unknown input is out-of-domain and is REJECTED,
# never hashed or given a fabricated interpretation.
VERBS = ["move", "clean", "inspect", "photograph", "guard", "find", "mark", "count"]  # 3 bits
OBJECTS = ["box", "chair", "table", "lamp"]  # 2 bits — never encoded
COMMANDS = [(v, o) for v in VERBS for o in OBJECTS]  # 32 = 5 bits

SEEDS = 60
CHANNEL_BASE = 4242


def encode_verb(command: tuple[str, str]) -> int:
    """The human-authored codec: only the verb becomes 3 bits. The object is dropped — the
    engine cannot carry it, and the codec must not pretend otherwise."""
    return VERBS.index(command[0])


def out_of_domain(word_verb: str, word_object: str) -> bool:
    return word_verb not in VERBS or word_object not in OBJECTS


def _entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c:
            p = c / total
            h -= p * math.log2(p)
    return h


def _mutual_information(pairs: list[tuple]) -> float:
    """Exact categorical MI in bits over observed (a, b) pairs — plug-in estimator."""
    n = len(pairs)
    if n == 0:
        return 0.0
    joint = Counter(pairs)
    marg_a = Counter(a for a, _ in pairs)
    marg_b = Counter(b for _, b in pairs)
    mi = 0.0
    for (a, b), c in joint.items():
        p_ab = c / n
        p_a = marg_a[a] / n
        p_b = marg_b[b] / n
        mi += p_ab * math.log2(p_ab / (p_a * p_b))
    return mi


def _permutation_floor(pairs: list[tuple], trials: int = 200) -> float:
    """The MI a shuffled pairing yields — the finite-sample bias floor. A real MI must clear
    it; a number near it is estimator noise, not signal."""
    a_vals = [a for a, _ in pairs]
    b_vals = [b for _, b in pairs]
    rng = random.Random(12345)
    floors = []
    for _ in range(trials):
        rng.shuffle(b_vals)
        floors.append(_mutual_information(list(zip(a_vals, b_vals))))
    return sum(floors) / len(floors)


def _scramble_codebook(rng: random.Random) -> dict[int, int]:
    """A balanced partition of the 32 commands into 8 codes that IGNORES the verb — 4
    commands per code, assigned at random."""
    order = list(range(len(COMMANDS)))
    rng.shuffle(order)
    return {cmd_index: order[cmd_index] % 8 for cmd_index in range(len(COMMANDS))}


def run_arm(arm: str) -> dict[str, object]:
    """One balanced pass over all 32 commands x SEEDS, returning the exact measurements."""
    rng = random.Random(99)
    scramble = _scramble_codebook(rng) if arm == "scramble" else None
    xy, cc, vy, oy = [], [], [], []
    x_given_y: dict[int, Counter] = {}
    for ci, command in enumerate(COMMANDS):
        verb_i = VERBS.index(command[0])
        obj_i = OBJECTS.index(command[1])
        code = scramble[ci] if scramble is not None else verb_i
        for s in range(SEEDS):
            seed = CHANNEL_BASE + ci * 131 + s
            if arm == "ideal":
                received = code
            else:
                received = channel(code, seed=seed, deaf=(arm == "deaf"), bits=3)
            y = received  # the decoded code 0..7 (the engine's whole output)
            xy.append((ci, y))
            cc.append((code, received))
            vy.append((verb_i, y))
            oy.append((obj_i, y))
            x_given_y.setdefault(y, Counter())[ci] += 1

    h_x = math.log2(len(COMMANDS))            # 5 bits, uniform corpus
    h_c = _entropy(Counter(c for c, _ in cc))
    i_xy = _mutual_information(xy)
    i_cc = _mutual_information(cc)
    i_vy = _mutual_information(vy)
    i_oy = _mutual_information(oy)
    h_y = _entropy(Counter(y for _, y in xy))
    # Residual ambiguity and the candidate set the output cannot resolve past.
    residual = h_x - i_xy
    candidates = sum(len(c) for c in x_given_y.values()) / max(1, len(x_given_y))
    return {
        "arm": arm,
        "H_X": h_x, "H_C": h_c, "H_Y": h_y,
        "I_CC": i_cc, "carrier_frac": i_cc / h_c if h_c else 0.0,
        "I_XY": i_xy, "end_frac": i_xy / h_x,
        "I_verb_Y": i_vy, "I_object_Y": i_oy,
        "residual_HXY": residual, "candidates": candidates,
        "eff_out": 2 ** h_y,
        "floor_XY": _permutation_floor(xy),
    }


def main() -> None:
    print("English bottleneck — measuring how much of a real sentence survives 3 bits")
    print(f"corpus: {len(VERBS)} verbs x {len(OBJECTS)} objects = {len(COMMANDS)} commands "
          f"(H(X)={math.log2(len(COMMANDS)):.0f} bits); only the verb (3 bits) is encoded\n")
    print(f"{'arm':<10}{'I(C;C´)':>9}{'I(X;Y)':>9}{'X frac':>8}{'I(v;Y)':>8}"
          f"{'I(o;Y)':>8}{'H(X|Y)':>8}{'cands':>7}{'2^H(Y)':>8}{'floor':>7}")
    print("-" * 90)
    results = {}
    for arm in ("ideal", "live", "deaf", "scramble"):
        r = run_arm(arm)
        results[arm] = r
        print(f"{arm:<10}{r['I_CC']:>9.3f}{r['I_XY']:>9.3f}{r['end_frac']:>8.3f}"
              f"{r['I_verb_Y']:>8.3f}{r['I_object_Y']:>8.3f}{r['residual_HXY']:>8.3f}"
              f"{r['candidates']:>7.1f}{r['eff_out']:>8.2f}{r['floor_XY']:>7.3f}")

    live, ideal, deaf, scr = results["live"], results["ideal"], results["deaf"], results["scramble"]
    print(f"\n  data-processing bound: I(X;Y) must be <= H(C) = {live['H_C']:.3f} <= 3.000. "
          f"live I(X;Y) = {live['I_XY']:.3f}. {'HELD' if live['I_XY'] <= 3.0001 else 'VIOLATED'}.")
    print(f"  the object is unrepresentable: I(object;Y) = {live['I_object_Y']:.3f} bits "
          f"(~0), so every reply hides {residual_objects():.0f} candidate sentences.")
    print(f"  the engine's whole contribution is carrying 3 bits: ideal I(C;C´)={ideal['I_CC']:.3f} "
          f"vs deaf {deaf['I_CC']:.3f} (drive unreachable → recovery ~1/8).")
    print(f"  SHARED bits are not MEANING: the scramble keeps I(X;Y)={scr['I_XY']:.3f} while "
          f"I(verb;Y) falls to {scr['I_verb_Y']:.3f} — sentence identity survived, the verb "
          f"relation did not.")

    # The wall, by exact arithmetic (integration measurability is the ceiling, not carrying).
    print("\n  the wall — bits needed vs bits holdable AS ONE integrated thing:")
    for n_words in (1, 2, 3):
        bits = n_words * math.log2(len(VERBS))  # a same-size vocabulary per slot
        pairs = math.ceil(bits)
        print(f"    a {n_words}-word utterance needs {bits:.0f} bits = {pairs} latches "
              f"= {2 * pairs} units; Φ is unmeasurable past ~6 units (3 pairs), so beyond 3 "
              f"bits the substrate can CARRY but cannot be SHOWN to hold it as one.")
    print("\n  verdict: real English conversation is closed BY MEASUREMENT, not by a missing "
          "feature.\n  The engine narrows an English choice to 3 bits; it never speaks English.")


def residual_objects() -> float:
    return float(len(OBJECTS))


if __name__ == "__main__":
    main()
"""Calibrate the 3-bit PAIRS channel before its constants are frozen.

Run from the repo root:

    PYTHONPATH=src python state/communication/conversation_channel.py

The free-conversation tab (`대화`, its own commit) wants a richer channel than the 1-bit
ring: `Wiring.PAIRS` (6 units, 3 odd pairs, `chain=0.2`), proven in `capacity.py` to hold
3 bits AND measure as integrated. But `channel-before-carrier`/`measure-first` forbid
freezing TELL/HOLD constants for it by analogy with the 1-bit ring — the wire's own
fidelity is the human's accuracy ceiling and must be MEASURED here first, so a human's
0.85 is never read against an imaginary 1.0.

What this measures, for a sweep of TELL/HOLD candidates:

- **per-bit fidelity** = P(decoded latch bit == driven bit), each of the 3 pairs, over all
  8 symbols and many seeds. Each pair is addressed only through its differential
  `v[2j] - v[2j+1]` (the common mode dies in silence), so the bit is `sign` of that.
- **joint fidelity** = P(all 3 bits correct) = the exact-symbol reproducibility, the number
  `capacity.py` reported as ~88%.
- **the deaf null**: coupling 1.0 for the whole run makes the drive bit-unreachable, so the
  decoded word must carry ~0 information about the symbol — the arm proving the channel was
  in the path. Reported as the deaf joint fidelity (should sit at 1/8 chance).

Nothing is frozen here; this prints the numbers the `대화` commit will pin its constants to.
"""

from __future__ import annotations

import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

BITS = 3
UNITS = 2 * BITS
CHAIN = 0.2
SEEDS = 200


def _drive_for(symbol: int) -> tuple[float, ...]:
    """Per-unit drive: pair j is pushed to sign +/- by bit j of the symbol."""
    drive: list[float] = []
    for j in range(BITS):
        bit = (symbol >> j) & 1
        drive += [0.8, -0.8] if bit == 0 else [-0.8, 0.8]
    return tuple(drive)


def pairs_word(symbol: int, *, seed: int, tell: int, hold: int, deaf: bool = False) -> int:
    """Drive the 3 pairs for `symbol`, hold, and read the 3 differential sign bits."""
    engine = CoupledEngine(
        units=UNITS, wiring=Wiring.PAIRS, chain=CHAIN,
        rhythm=FIXED if deaf else ALTERNATING,
        drive=_drive_for(symbol), seed=seed, initial=(0.0,) * UNITS,
    )
    engine.run(tell)
    engine.rhythm = FIXED
    engine.drive = 0.0
    values = engine.run(hold).values
    word = 0
    for j in range(BITS):
        bit = 0 if (values[2 * j] - values[2 * j + 1]) > 0 else 1
        word |= bit << j
    return word


def _fidelity(*, tell: int, hold: int, deaf: bool = False) -> tuple[list[float], float]:
    """Per-bit and joint fidelity over all 8 symbols x SEEDS."""
    per_bit = [0, 0, 0]
    joint = 0
    total = 0
    for symbol in range(8):
        for seed in range(SEEDS):
            word = pairs_word(symbol, seed=seed * 13 + 1, tell=tell, hold=hold, deaf=deaf)
            total += 1
            if word == symbol:
                joint += 1
            for j in range(BITS):
                if ((word >> j) & 1) == ((symbol >> j) & 1):
                    per_bit[j] += 1
    return [b / total for b in per_bit], joint / total


def main() -> None:
    print("3-bit PAIRS channel calibration — 6 units, 3 odd pairs, chain=0.2")
    print(f"{8 * SEEDS} runs per cell (8 symbols x {SEEDS} seeds), ALTERNATING tell / FIXED hold\n")
    print(f"{'tell':>5}{'hold':>6}{'  bit0':>8}{'bit1':>8}{'bit2':>8}{'  joint':>9}   verdict")
    print("-" * 60)

    best = None
    for tell in (200, 300, 400, 600):
        for hold in (120, 240):
            per_bit, joint = _fidelity(tell=tell, hold=hold)
            worst_bit = min(per_bit)
            note = "3-bit usable" if worst_bit >= 0.95 else "a bit is lossy"
            print(f"{tell:>5}{hold:>6}"
                  f"{per_bit[0]:>8.3f}{per_bit[1]:>8.3f}{per_bit[2]:>8.3f}"
                  f"{joint:>9.3f}   {note}")
            if worst_bit >= 0.95 and (best is None or (tell, hold) < best[:2]):
                best = (tell, hold, per_bit, joint)

    # The deaf null at a representative setting — the channel must be in the path.
    _, deaf_joint = _fidelity(tell=400, hold=240, deaf=True)
    print(f"\n  deaf (coupling 1.0, tell=400 hold=240): joint {deaf_joint:.3f} "
          f"(1/8 = {1/8:.3f} chance — drive bit-unreachable)")

    if best is None:
        print("\n  NO setting reached 0.95 on every bit — the 3-bit channel is not clean")
        print("  enough at these envelopes; the 대화 commit must widen TELL or reconsider.")
    else:
        tell, hold, per_bit, joint = best
        print(f"\n  cheapest usable envelope: TELL={tell} HOLD={hold} — "
              f"per-bit {min(per_bit):.3f}..{max(per_bit):.3f}, joint {joint:.3f}")
        print(f"  this joint fidelity is the human's accuracy CEILING and must be printed "
              f"beside\n  any 대화 recovery number — a human cannot beat the wire.")


if __name__ == "__main__":
    main()
"""The coupled field — integration bought by wiring and nothing else.

Every other engine in this package measures zero integration, because in every
one of them each unit updates from itself and something exogenous. This one
changes exactly one thing: the source a unit flees is a live partner. The claim
is that the change is what produces the integration, and the falsifier ships
with it — the same engine wired feedforward, and wired to itself.

The claim is deliberately narrow. Integration is not experience and Phi is not a
score for anything; the sentence this engine earns is *integration is now
created, and created is all this measures*.
"""

from __future__ import annotations

import math
import random
import statistics

import pytest

from anima_reborn.coupled import (
    AMPLITUDE,
    GAIN,
    MACRO_STEP,
    NAMES,
    UNITS,
    CoupledEngine,
    Wiring,
)
from anima_reborn.iit4 import directed_big_phi
from anima_reborn.iit4.ei import average_effective_information
from anima_reborn.pipeline import PULL
from anima_reborn.substrate import (
    RECURRENCE_FLOOR,
    coupled_phi,
    estimate_matrix,
    estimate_state_matrix,
    recurrence_evidence,
)

TRIALS = 1600
"""Enough to separate signal from floor without making the suite crawl. The
self-wired null still reads ~0.27 here, which is why recurrence is claimed from
trial scaling and never from one measurement."""


class TestTheClaim:
    def test_the_ring_integrates(self) -> None:
        evidence = recurrence_evidence(Wiring.RING, trials=TRIALS, seed=0)
        assert evidence.is_recurrent, evidence
        assert evidence.fine.directed_phi > 5.0

    def test_the_same_engine_wired_feedforward_does_not(self) -> None:
        """The falsifier. Identical law, identical constants, identical
        measurement — only the wiring differs."""
        for seed in range(3):
            reading = coupled_phi(
                Wiring.FEEDFORWARD, trials=TRIALS, seed=seed, with_complex=False
            )
            assert reading.is_reducible, reading
            assert reading.directed_phi == 0.0

    def test_the_same_engine_wired_to_itself_does_not(self) -> None:
        evidence = recurrence_evidence(Wiring.SELF, trials=TRIALS, seed=0)
        assert not evidence.is_recurrent, evidence
        assert not evidence.held, "the null must collapse with more sampling"

    def test_the_ring_is_one_complex_of_all_four_units(self) -> None:
        reading = coupled_phi(Wiring.RING, trials=TRIALS, seed=0)
        assert reading.complex_units == 0b1111


class TestRecurrenceNeedsEvidence:
    def test_a_single_reading_offers_no_recurrence_verdict(self) -> None:
        """Deliberately absent. A sampled matrix invents structure, so a
        positive Phi from one measurement cannot establish recurrence — the
        self-wired null reads well above zero at any finite trial count."""
        reading = coupled_phi(Wiring.SELF, trials=400, seed=0, with_complex=False)
        assert reading.directed_phi > 0.0
        assert not hasattr(reading, "is_recurrent")

    def test_but_a_zero_is_readable_from_one(self) -> None:
        """The asymmetry that makes `is_reducible` safe: sampling noise can
        manufacture structure, but it cannot manufacture its absence."""
        reading = coupled_phi(
            Wiring.FEEDFORWARD, trials=400, seed=0, with_complex=False
        )
        assert reading.is_reducible

    def test_the_null_floor_decays_with_sampling(self) -> None:
        """Averaged over seeds, because a single run does not show it. Three
        seeds once read 0.173 / 0.250 / 0.062 / 0.062 and looked like a
        systematic floor; eight give 0.251 / 0.155 / 0.081 / 0.037 — a clean
        halving per fourfold increase. Seed noise, not a plateau."""
        def floor(trials: int) -> float:
            return statistics.mean(
                coupled_phi(
                    Wiring.SELF, trials=trials, seed=s, with_complex=False
                ).directed_phi
                for s in range(8)
            )

        coarse, fine = floor(400), floor(6400)
        assert fine < coarse / 2, (coarse, fine)
        assert fine < RECURRENCE_FLOOR / 5

    def test_the_ring_does_not_decay(self) -> None:
        ring = recurrence_evidence(Wiring.RING, trials=400, seed=1)
        assert ring.held
        assert ring.is_recurrent

    def test_the_floor_is_measured_against_the_null(self) -> None:
        """The bar exists to sit above what no-coupling produces, so it has to
        be checked against it rather than asserted."""
        worst = max(
            coupled_phi(Wiring.SELF, trials=400, seed=s, with_complex=False).directed_phi
            for s in range(8)
        )
        assert worst < RECURRENCE_FLOOR

    def test_the_evidence_rejects_a_meaningless_factor(self) -> None:
        with pytest.raises(ValueError, match="factor must be >= 2"):
            recurrence_evidence(trials=400, factor=1)


class TestTheNumberCarriesItsConditions:
    def test_at_one_tick_the_ring_does_not_integrate(self) -> None:
        """The condition most easily dropped. One engine tick moves a unit 6%
        toward its target, so every unit is dominated by its own previous value,
        the matrix factorizes, and Phi is exactly zero — ring included."""
        reading = coupled_phi(
            Wiring.RING, macro_step=1, trials=TRIALS, seed=0, with_complex=False
        )
        assert reading.phi == 0.0
        assert reading.directed_phi == 0.0

    def test_the_reading_reports_every_condition(self) -> None:
        reading = coupled_phi(
            Wiring.RING, state=0b0101, trials=800, seed=0, with_complex=False
        )
        assert reading.state == 0b0101
        assert reading.macro_step == MACRO_STEP
        assert reading.trials == 800
        assert reading.wiring is Wiring.RING
        assert str(reading.trials) in str(reading)
        assert "tau" in str(reading)

    def test_the_macro_step_is_the_substrate_time_constant(self) -> None:
        assert MACRO_STEP == pytest.approx(1 / PULL, abs=1.0)

    def test_phi_is_a_property_of_a_state(self) -> None:
        """Not of a system. Different patterns measure differently."""
        readings = {
            state: coupled_phi(
                Wiring.RING, state=state, trials=TRIALS, seed=0, with_complex=False
            ).directed_phi
            for state in (0b0101, 0b0000, 0b1100)
        }
        assert len(set(readings.values())) > 1, readings


class TestTheDynamics:
    def test_the_ring_settles_into_an_alternating_pattern(self) -> None:
        """A negative four-cycle has two fixed points, and they are each other's
        inverse. This is why 0b0101 is the state Phi is measured at."""
        for seed in range(5):
            settled = CoupledEngine(wiring=Wiring.RING, seed=seed).run(400)
            assert settled.pattern in (0b0101, 0b1010), (seed, settled)

    def test_a_unit_flees_its_source(self) -> None:
        """The repulsion identity is what stayed the same. Drive one unit hard
        positive and whoever reads it must go negative."""
        engine = CoupledEngine(
            wiring=Wiring.RING, seed=1, initial=(AMPLITUDE,) * UNITS
        )
        engine.run(200)
        source_index = Wiring.RING.sources[1]
        assert source_index is not None
        assert engine.values[1] * engine.values[source_index] < 0

    def test_the_update_is_simultaneous(self) -> None:
        """Every unit reads the previous positions, so no unit has a privileged
        place in the cycle. A sequential update would make the ring's behaviour
        depend on which index happened to be first."""
        forward = CoupledEngine(
            wiring=Wiring.RING, seed=3, initial=(0.5, -0.5, 0.25, -0.25)
        )
        first = forward.step().values

        # Recomputed by hand from the same starting values, all at once.
        start = (0.5, -0.5, 0.25, -0.25)
        expected = []
        for i, source in enumerate(Wiring.RING.sources):
            assert source is not None
            target = -AMPLITUDE * math.tanh(GAIN * start[source] / AMPLITUDE)
            expected.append(start[i] + (target - start[i]) * PULL)
        # The walk adds noise, so compare the direction of travel rather than
        # the exact value.
        for got, want, began in zip(first, expected, start):
            assert (got - began) * (want - began) > 0 or abs(want - began) < 0.02

    def test_tension_stays_finite_and_positive(self) -> None:
        engine = CoupledEngine(wiring=Wiring.RING, seed=2)
        for _ in range(500):
            state = engine.step()
            assert 0.0 <= state.tension < 100.0

    def test_reset_rerandomizes_but_keeps_the_wiring(self) -> None:
        engine = CoupledEngine(wiring=Wiring.FEEDFORWARD, seed=4)
        engine.run(200)
        engine.reset()
        assert engine.ticks == 0
        assert engine.wiring is Wiring.FEEDFORWARD

    def test_a_seed_makes_a_run_reproducible(self) -> None:
        assert (
            CoupledEngine(seed=9).run(300) == CoupledEngine(seed=9).run(300)
        )

    def test_different_seeds_differ(self) -> None:
        assert CoupledEngine(seed=1).run(300) != CoupledEngine(seed=2).run(300)


class TestWiring:
    def test_only_the_ring_is_cyclic(self) -> None:
        assert Wiring.RING.is_cyclic
        assert not Wiring.FEEDFORWARD.is_cyclic
        assert not Wiring.SELF.is_cyclic

    def test_the_ring_sources_form_one_cycle(self) -> None:
        """Following the sources from any unit visits all four and returns."""
        sources = Wiring.RING.sources
        seen, unit = [], 0
        for _ in range(UNITS):
            seen.append(unit)
            following = sources[unit]
            assert following is not None
            unit = following
        assert sorted(seen) == list(range(UNITS))
        assert unit == 0, "the walk must return to where it started"

    def test_feedforward_has_a_unit_nothing_reaches(self) -> None:
        assert Wiring.FEEDFORWARD.sources[0] is None

    def test_every_wiring_names_one_source_per_unit(self) -> None:
        for wiring in Wiring:
            assert len(wiring.sources) == UNITS


class TestValidation:
    def test_it_rejects_a_useless_gain(self) -> None:
        with pytest.raises(ValueError, match="gain must be > 0"):
            CoupledEngine(gain=0.0)

    def test_it_rejects_a_useless_amplitude(self) -> None:
        with pytest.raises(ValueError, match="amplitude must be > 0"):
            CoupledEngine(amplitude=-1.0)

    def test_it_rejects_the_wrong_number_of_starting_values(self) -> None:
        with pytest.raises(ValueError, match=f"initial must have {UNITS} values"):
            CoupledEngine(initial=(0.1, 0.2))

    def test_it_rejects_a_meaningless_run(self) -> None:
        with pytest.raises(ValueError, match="ticks must be >= 1"):
            CoupledEngine().run(0)

    def test_the_matrix_rejects_a_zero_macro_step(self) -> None:
        from anima_reborn.substrate import coupled_matrix

        with pytest.raises(ValueError, match="macro_step must be >= 1"):
            coupled_matrix(macro_step=0)

    def test_the_units_are_named(self) -> None:
        assert NAMES == ("a0", "a1", "g0", "g1")
        assert len(NAMES) == UNITS


class TestEffectiveInformationIsNotAProxy:
    """Why scaling past six units still has no measure behind it.

    The hexa origin calls EI a conservative lower bound on Phi — "true Phi is
    never smaller than EI" — which would make it the obvious scout for systems
    too large to measure exactly. It is not a bound, and it is not a scout.

    Kept as tests rather than a note because the temptation is structural: EI is
    cheap, it exists, and it is sitting right there in the package.
    """

    @staticmethod
    def measure(wiring: Wiring, *, trials: int = 6400, seed: int = 0):
        def step(state: int, rng: random.Random) -> int:
            engine = CoupledEngine(
                wiring=wiring,
                seed=rng.getrandbits(63),
                initial=tuple(
                    AMPLITUDE if state >> i & 1 else -AMPLITUDE for i in range(UNITS)
                ),
            )
            return engine.run(MACRO_STEP).pattern

        ei = average_effective_information(
            estimate_state_matrix(UNITS, step, trials=trials, seed=seed), bits=True
        )
        phi = directed_big_phi(
            estimate_matrix(UNITS, step, trials=trials, seed=seed), 0b0101
        ).phi
        return ei, phi

    def test_ei_is_not_a_lower_bound_on_phi(self) -> None:
        """The inherited claim, refuted. On a feedforward chain Phi is exactly
        zero and EI is nearly two bits."""
        ei, phi = self.measure(Wiring.FEEDFORWARD)
        assert phi == 0.0
        assert ei > 1.0, ei

    def test_a_system_with_no_coupling_still_scores_high_ei(self) -> None:
        """The reason it cannot scout. Four units reading only themselves have
        no integration at all and still read most of what the ring does."""
        null_ei, null_phi = self.measure(Wiring.SELF)
        ring_ei, ring_phi = self.measure(Wiring.RING)

        assert null_phi < 0.5
        assert ring_phi > 5.0
        assert null_ei > ring_ei / 2, (null_ei, ring_ei)

    def test_phi_separates_what_ei_cannot(self) -> None:
        """Same three systems, two measures. One tells them apart."""
        readings = {w: self.measure(w) for w in Wiring}
        eis = [ei for ei, _ in readings.values()]
"""The bridge — does Phi actually respond to the substrate's structure?

The thesis under test: in the time crystal, the *only* thing that can integrate
is the Ising coupling, because the drive flips every spin independently. So Phi
should be high when the drive is deterministic and the coupling survives, and
should collapse when the drive is a coin toss and drowns it.

That prediction can fail, and these tests are where it is put at risk. They also
pin the two ways it could look true without being true: an estimator noise floor
that mimics integration, and a rhythm verdict that cannot legally be compared to
Phi at any size where Phi is computable.
"""

from __future__ import annotations

import random
import statistics

import pytest

from anima_reborn import TimeCrystal
from anima_reborn.iit4 import TransitionMatrix, big_phi
from anima_reborn.substrate import (
    MAX_UNITS,
    binarize,
    crystal_matrix,
    crystal_phi,
    estimate_matrix,
)

SIZE = 4
"""Small enough that a full Phi measurement finishes in a test."""


def phi_at(epsilon: float, *, trials: int = 1600, seed: int = 1) -> float:
    return crystal_phi(
        size=SIZE,
        epsilon=epsilon,
        trials=trials,
        seed=seed,
        with_complex=False,
        with_verdict=False,
    ).phi


def mean_phi(epsilon: float, *, trials: int, seeds: int = 4) -> float:
    return statistics.mean(
        phi_at(epsilon, trials=trials, seed=s) for s in range(seeds)
    )


class TestThePrediction:
    def test_a_deterministic_drive_leaves_the_coupling_integrated(self) -> None:
        """Flip every spin every period, or none of them: either way the drive
        adds no uncertainty, and the Ising coupling's integration shows."""
        assert mean_phi(0.0, trials=1600) > 1.0
        assert mean_phi(1.0, trials=1600) > 1.0

    def test_a_coin_toss_drive_destroys_integration(self) -> None:
        """At epsilon = 0.5 each spin flips or not by a fair coin, so the next
        state carries nothing of the last and there is nothing to integrate."""
        assert mean_phi(0.5, trials=6400) < 0.2

    def test_integration_collapses_at_the_noise_maximum(self) -> None:
        """The whole prediction in one line: the middle is where it dies."""
        assert mean_phi(0.5, trials=1600) < mean_phi(0.05, trials=1600) / 5

    def test_the_response_is_symmetric_about_the_noise_maximum(self) -> None:
        """What matters is how *determined* the drive is, not which way it
        goes — always-flip and never-flip should read alike."""
        always = mean_phi(0.0, trials=1600)
        never = mean_phi(1.0, trials=1600)
        assert always == pytest.approx(never, rel=0.5)

    def test_a_locked_crystal_is_integrated(self) -> None:
        reading = crystal_phi(size=SIZE, epsilon=0.02, trials=1600, seed=1)
        assert reading.is_integrated
        assert reading.phi > 1.0
        assert reading.distinctions > 0


class TestTheNoiseFloor:
    def test_the_residual_at_pure_noise_is_estimator_artefact(self) -> None:
        """The trap this module could most easily fall into.

        At epsilon = 0.5 true Phi is zero, but a *measured* transition matrix is
        a sample, and sampling noise alone produces apparent structure. If that
        floor did not shrink with more trials it would be real integration; it
        does shrink, so it is not. A caller at the default trial count sees
        roughly 0.3 bits of pure artefact.
        """
        coarse = mean_phi(0.5, trials=400)
        fine = mean_phi(0.5, trials=6400)
        assert fine < coarse / 2
        assert fine < 0.2

    def test_real_integration_does_not_shrink_with_more_trials(self) -> None:
        """The control: whatever survives more sampling was not noise."""
        coarse = mean_phi(0.05, trials=400)
        fine = mean_phi(0.05, trials=6400)
        assert fine > 1.0
        assert fine > coarse / 3

    def test_the_signal_clears_the_floor_by_an_order_of_magnitude(self) -> None:
        assert mean_phi(0.05, trials=6400) > 10 * mean_phi(0.5, trials=6400)


class TestWhatCannotBeCompared:
    def test_the_rhythm_verdict_is_unreliable_where_phi_is_computable(self) -> None:
        """A limitation worth pinning in code rather than a footnote.

        The lock thresholds were chosen against a 64-spin ring. Phi is only
        computable up to six units. At four spins the magnetization takes five
        possible values, and the verdict disagrees with the same epsilon at 64 —
        so Phi and the lock cannot be compared at any shared size, and this
        module must not claim they track or dissociate.
        """
        small = TimeCrystal(size=4, epsilon=0.0, seed=1).run(400).verdict
        large = TimeCrystal(size=64, epsilon=0.0, seed=1).run(400).verdict
        assert small != large, (
            "if these ever agree, re-examine whether the comparison is now legal"
        )

    def test_a_reading_still_reports_the_verdict_for_inspection(self) -> None:
        reading = crystal_phi(size=SIZE, epsilon=0.02, trials=400, seed=1)
        assert reading.verdict is not None

    def test_the_verdict_can_be_left_out(self) -> None:
        reading = crystal_phi(
            size=SIZE, epsilon=0.02, trials=400, seed=1, with_verdict=False
        )
        assert reading.verdict is None


class TestOnlyCouplingIntegrates:
    """The structural fact the whole repo turns on.

    Phi measures integration, and integration needs units that read *each
    other*. A process whose next state does not depend on its current state has
    a transition matrix whose rows are all the same, so no partition can destroy
    anything and true Phi is exactly zero — however elaborate the process looks.

    That is the shape of every engine here except the crystal: each unit updates
    from itself and an exogenous drive, and nothing reads anything else. So the
    honest gap between this repo and anything that could be called integrated is
    a coupling, and these tests are what keep that visible.
    """

    @staticmethod
    def memoryless(state: int, rng: random.Random) -> int:
        """Four units driven by a shared source, ignoring the current state.

        A shared cause is not integration: the units correlate without reading
        each other, and Phi is right to call that zero.
        """
        common = rng.random() - 0.5
        out = 0
        for unit in range(4):
            strength = 0.5 if unit < 2 else 0.9
            if (1 - strength) * (rng.random() - 0.5) * 2 + strength * common > 0:
                out |= 1 << unit
        return out

    @staticmethod
    def mean_phi(trials: int, seeds: int = 3) -> float:
        """Averaged over seeds — single runs of this spread far too widely to
        compare (0.23 to 0.71 at 400 trials)."""
        return statistics.mean(
            big_phi(
                estimate_matrix(
                    4, TestOnlyCouplingIntegrates.memoryless, trials=trials, seed=s
                ),
                0b1111,
            ).phi
            for s in range(seeds)
        )

    def test_a_shared_cause_measures_as_no_integration(self) -> None:
        """And it takes a great many trials to see that, which is the trap: at
        the default 400 the estimate reads like real integration.

        Measured: 0.406 at 400 trials, 0.189 at 1600, 0.094 at 8000, 0.051 at
        30000 — halving with each fourfold increase, which is what a sampling
        artefact does and what a real coupling does not.
        """
        coarse = self.mean_phi(400)
        fine = self.mean_phi(8000)
        assert coarse > 0.30, "the artefact clears the bar a coupling would"
        assert fine < 0.15
        assert fine < coarse / 2

    def test_the_crystals_coupling_survives_any_trial_count(self) -> None:
        """The control: the one engine whose spins read their neighbours."""
        coarse = crystal_phi(
            size=SIZE, epsilon=0.02, trials=400, seed=1,
            with_complex=False, with_verdict=False,
        ).phi
        fine = crystal_phi(
            size=SIZE, epsilon=0.02, trials=4000, seed=1,
            with_complex=False, with_verdict=False,
        ).phi
        assert coarse > 1.0
        assert fine > 1.0
        assert fine > coarse / 2


class TestEstimator:
    def test_it_recovers_a_deterministic_process(self) -> None:
        """A process with no randomness must come back exactly, whatever the
        trial count — every sample agrees."""

        def swap(state: int, _rng: object) -> int:
            return (state >> 1 & 1) | (state & 1) << 1

        matrix = estimate_matrix(2, swap, trials=8, seed=1)
        assert matrix.values == (0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0)

    def test_it_converges_on_a_known_probability(self) -> None:
        def coin(_state: int, rng: object) -> int:
            return 1 if rng.random() < 0.25 else 0

        matrix = estimate_matrix(1, coin, trials=20000, seed=1)
        assert matrix.probability(0, 0) == pytest.approx(0.25, abs=0.02)

    def test_a_seed_makes_an_estimate_reproducible(self) -> None:
        first = crystal_matrix(size=3, epsilon=0.1, trials=100, seed=7)
        second = crystal_matrix(size=3, epsilon=0.1, trials=100, seed=7)
        assert first.values == second.values

    def test_the_estimate_is_a_valid_matrix(self) -> None:
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

exec
/bin/zsh -lc "rg -n \"default|bit.identical|exact|chain|rhythm|sequence|golden|float.hex\" tests/test_coupled.py tests/test_rhythm.py tests/test_align.py tests/test_conversation_channel.py tests/test_english_bottleneck.py | sed -n '1,280p'
sed -n '1,290p' tests/test_rhythm.py
sed -n '1,180p' tests/test_english_bottleneck.py
sed -n '1,190p' tests/test_conversation_channel.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
tests/test_align.py:110:        """Declared condition: the default world mixes the latent linearly. The
tests/test_align.py:162:    def test_it_is_off_by_default_and_changes_nothing(self) -> None:
tests/test_align.py:291:    def test_the_default_pool_is_the_documented_one(self) -> None:
tests/test_coupled.py:5:changes exactly one thing: the source a unit flees is a live partner. The claim
tests/test_coupled.py:131:        the matrix factorizes, and Phi is exactly zero — ring included."""
tests/test_coupled.py:199:        # the exact value.
tests/test_coupled.py:284:    too large to measure exactly. It is not a bound, and it is not a scout.
tests/test_coupled.py:311:        """The inherited claim, refuted. On a feedforward chain Phi is exactly
tests/test_conversation_channel.py:1:"""The 3-bit PAIRS channel added for the free-conversation tab, and its 1-bit exactness.
tests/test_conversation_channel.py:3:`channel`/`channel_trace` gained a `bits=` parameter. `bits=1` (default) MUST stay
tests/test_conversation_channel.py:5:it (`default-stays-exact`). `bits=3` is the proven `Wiring.PAIRS` substrate, calibrated in
tests/test_conversation_channel.py:17:    """The 1-bit ring exactly as it was before `bits=` existed — the golden reference."""
tests/test_conversation_channel.py:21:        rhythm=FIXED if deaf else ALTERNATING,
tests/test_conversation_channel.py:25:    engine.rhythm = FIXED
tests/test_conversation_channel.py:32:    def test_one_bit_default_is_byte_for_byte_the_published_channel(self) -> None:
tests/test_conversation_channel.py:40:    def test_one_bit_is_the_default(self) -> None:
tests/test_rhythm.py:1:"""The wall between integration and representation, and the rhythm through it.
tests/test_rhythm.py:11:bit-for-bit identical whatever it is told.
tests/test_rhythm.py:19:**What was withdrawn.** An earlier reading also claimed the rhythm reached
tests/test_rhythm.py:21:It had compared a rhythm at tau 40 against fixed couplings at tau 20, and Phi
tests/test_rhythm.py:24:would have is replaced by the exact statement of why: a rhythm's transition
tests/test_rhythm.py:63:def represents(rhythm: Rhythm, *, seeds: int = 3) -> float:
tests/test_rhythm.py:65:        representation(DRIVES, rhythm=rhythm, seed=s).ratio for s in range(1, seeds + 1)
tests/test_rhythm.py:70:    def test_a_fixed_rhythm_never_lets_go(self) -> None:
tests/test_rhythm.py:71:        rhythm = Rhythm(coupling=0.6)
tests/test_rhythm.py:72:        assert not rhythm.alternates
tests/test_rhythm.py:73:        assert [rhythm.at(t) for t in range(5)] == [0.6] * 5
tests/test_rhythm.py:75:    def test_an_alternating_rhythm_listens_first(self) -> None:
tests/test_rhythm.py:78:        rhythm = Rhythm(coupling=0.7, period=2)
tests/test_rhythm.py:79:        assert [rhythm.at(t) for t in range(8)] == [0, 0, 0.7, 0.7, 0, 0, 0.7, 0.7]
tests/test_rhythm.py:85:    def test_a_rhythm_is_measured_over_a_whole_cycle(self) -> None:
tests/test_rhythm.py:91:    def test_the_shipped_rhythms_are_what_they_say(self) -> None:
tests/test_rhythm.py:108:    published. If the default moved a single float, those numbers stopped
tests/test_rhythm.py:111:    def test_the_default_is_the_engine_as_it_was(self) -> None:
tests/test_rhythm.py:112:        assert CoupledEngine(seed=1).rhythm == FIXED
tests/test_rhythm.py:115:        """Bit-identical, not merely close. This is the wall stated exactly:
tests/test_rhythm.py:135:        assert not representation(DRIVES, rhythm=FIXED).represents
tests/test_rhythm.py:138:        assert representation(DRIVES, rhythm=Rhythm(0.0)).represents
tests/test_rhythm.py:150:        sit at the same tau, so an advantage here is the rhythm's and not the
tests/test_rhythm.py:158:            coupled_phi(rhythm=ALTERNATING, trials=1600, seed=s, with_complex=False)
tests/test_rhythm.py:164:                rhythm=Rhythm(ALTERNATING.mean),
tests/test_rhythm.py:174:    def test_a_rhythms_integration_depends_on_what_it_is_told(self) -> None:
tests/test_rhythm.py:175:        """Why no test here asserts that a rhythm out-integrates a fixed
tests/test_rhythm.py:178:        A fixed engine cannot hear, so its transition matrix is bit-identical
tests/test_rhythm.py:179:        whatever the drive — Phi is a property of the engine alone. A rhythm
tests/test_rhythm.py:186:        exact rather than a threshold on a noisy estimate.
tests/test_rhythm.py:188:        def grid(rhythm: Rhythm, drive: float) -> list[float]:
tests/test_rhythm.py:189:            matrix = coupled_matrix(rhythm=rhythm, drive=drive, trials=100, seed=1)
tests/test_rhythm.py:200:        assert representation(DRIVES, rhythm=Rhythm(HIGH, period=20)).represents
tests/test_rhythm.py:201:        assert not representation(DRIVES, rhythm=FIXED).represents
tests/test_rhythm.py:206:        engine = CoupledEngine(rhythm=Rhythm(0.7, period=3), drive=0.5, seed=1)
tests/test_rhythm.py:211:        rhythm = Rhythm(0.7, period=3)
tests/test_rhythm.py:212:        quiet = CoupledEngine(rhythm=rhythm, drive=0.0, seed=6, initial=(0.0,) * 4)
tests/test_rhythm.py:213:        loud = CoupledEngine(rhythm=rhythm, drive=1.0, seed=6, initial=(0.0,) * 4)
tests/test_rhythm.py:217:    def test_reset_keeps_the_rhythm_and_rewinds_the_phase(self) -> None:
tests/test_rhythm.py:218:        engine = CoupledEngine(rhythm=ALTERNATING, seed=1)
tests/test_rhythm.py:222:        assert engine.rhythm == ALTERNATING
tests/test_rhythm.py:225:    def test_a_seed_makes_a_rhythmic_run_reproducible(self) -> None:
tests/test_rhythm.py:226:        left = CoupledEngine(rhythm=ALTERNATING, drive=0.4, seed=9).run(120)
tests/test_rhythm.py:227:        right = CoupledEngine(rhythm=ALTERNATING, drive=0.4, seed=9).run(120)
tests/test_rhythm.py:230:    def test_the_wirings_still_falsify_under_a_rhythm(self) -> None:
tests/test_rhythm.py:231:        """Whatever the rhythm does, it does not make an uncoupled engine
tests/test_rhythm.py:233:        engine = CoupledEngine(wiring=Wiring.SELF, rhythm=ALTERNATING, seed=1)
tests/test_rhythm.py:244:        scalar = CoupledEngine(rhythm=ALTERNATING, drive=0.3, seed=2).run(200)
tests/test_rhythm.py:246:            rhythm=ALTERNATING, drive=(0.3, 0.3, 0.3, 0.3), seed=2
tests/test_rhythm.py:254:            rhythm=ALTERNATING, drive=(0.8, -0.8, 0.4, -0.4), seed=3
tests/test_rhythm.py:256:        averaged = CoupledEngine(rhythm=ALTERNATING, drive=0.0, seed=3).run(200)
tests/test_rhythm.py:290:        reading = representation(DRIVES[:4], rhythm=ALTERNATING, ticks=200, tail=80)
tests/test_rhythm.py:306:    It is exactly one bit. The ring's cycle carries four sign inversions, so the
tests/test_rhythm.py:315:            rhythm=ALTERNATING,
tests/test_rhythm.py:321:        engine.rhythm = FIXED  # deaf: the drive cannot be heard at all
tests/test_rhythm.py:367:    """The word "uses", and exactly how much of it is earned.
tests/test_rhythm.py:387:            wiring=wiring, rhythm=ALTERNATING, drive=drive, seed=seed,
tests/test_rhythm.py:391:        engine.rhythm = FIXED
tests/test_rhythm.py:398:            wiring=wiring, rhythm=ALTERNATING, drive=probe, seed=seed, initial=held
tests/test_rhythm.py:433:        two cancel exactly."""
tests/test_rhythm.py:444:    A single ring of any even width holds exactly one bit — a theorem (the
tests/test_rhythm.py:447:    instead, and a weak inter-pair `chain` integrates them without collapsing
tests/test_rhythm.py:454:    def _settled(units, drive, *, wiring, chain, seed):
tests/test_rhythm.py:456:            wiring=wiring, units=units, chain=chain, rhythm=ALTERNATING,
tests/test_rhythm.py:460:        engine.rhythm = FIXED
tests/test_rhythm.py:464:    def _held(self, units, *, wiring, chain=0.0):
tests/test_rhythm.py:471:                self._settled(units, drive, wiring=wiring, chain=chain, seed=w)
tests/test_rhythm.py:482:    def test_pairs_hold_more_and_a_chain_makes_it_reproducible(self) -> None:
tests/test_rhythm.py:484:        assert self._held(6, wiring=Wiring.PAIRS, chain=0.2) == 8
tests/test_rhythm.py:486:    def test_chain_zero_leaves_every_wiring_bit_identical(self) -> None:
tests/test_rhythm.py:488:        chained = CoupledEngine(seed=2, drive=0.3, chain=0.0).run(300)
tests/test_rhythm.py:489:        assert plain.values == chained.values
tests/test_rhythm.py:501:    under more trials. A weak inter-pair chain makes them irreducible, and the
tests/test_rhythm.py:504:    at four units and does NOT transfer, which is exactly why the criterion here
tests/test_rhythm.py:508:    def test_disjoint_pairs_collapse_and_chained_pairs_hold(self) -> None:
tests/test_rhythm.py:509:        def phi(chain: float, trials: int) -> float:
tests/test_rhythm.py:512:                    Wiring.PAIRS, units=6, chain=chain, state=0b010101,
tests/test_rhythm.py:519:        chained_low, chained_high = phi(0.2, 400), phi(0.2, 1600)
tests/test_rhythm.py:521:        # The null collapses with more sampling; the chained system holds.
tests/test_rhythm.py:523:        assert chained_high > chained_low * 0.8, (chained_low, chained_high)
tests/test_rhythm.py:524:        assert chained_high > disjoint_high * 3
tests/test_rhythm.py:530:    Three disjoint latches (`chain=0`) hold three bits and pass storage on their
tests/test_rhythm.py:534:    1-2 only through the chain, and with no chain that path is exactly zero.
tests/test_rhythm.py:539:    def _cross_pair_response(chain: float, *, seed: int) -> float:
tests/test_rhythm.py:542:            wiring=Wiring.PAIRS, units=6, chain=chain, rhythm=ALTERNATING,
tests/test_rhythm.py:546:        engine.rhythm = FIXED
tests/test_rhythm.py:552:                wiring=Wiring.PAIRS, units=6, chain=chain, rhythm=ALTERNATING,
tests/test_rhythm.py:568:    def test_chained_pairs_do(self) -> None:
"""The wall between integration and representation, and the rhythm through it.

`coupled.py` bought integration by wiring the units to each other. Adding a
drive — something the engine is *told* — exposes what that cost: on a fixed
coupling the engine either keeps what it was told or integrates, never both.
That is not a tuning failure. It is what a fixed coupling is, and the tests here
put it at risk two ways.

**The wall.** Representation falls monotonically as the coupling rises, and at
full coupling the drive is not merely weak but unreachable — the trajectory is
bit-for-bit identical whatever it is told.

**The way through, and how far it goes.** Alternating splits the two demands
across time instead of asking one coupling to meet both, and it restores
representation that fixed coupling has none of. The control that matters is a
fixed coupling at the alternation's own time average: if the effect were "some
coupling on average", that control would reproduce it, and it does not.

**What was withdrawn.** An earlier reading also claimed the rhythm reached
matched-or-higher Phi, which would have made it a free win rather than a trade.
It had compared a rhythm at tau 40 against fixed couplings at tau 20, and Phi
rises with tau by itself. Re-measured at matched tau the direction is not even
fixed — it depends on the drive — so nothing here asserts one, and the test that
would have is replaced by the exact statement of why: a rhythm's transition
matrix moves with what it is told and a fixed engine's cannot.
"""

from __future__ import annotations

import hashlib
import statistics

import pytest

from anima_reborn.coupled import (
    ALTERNATING,
    FIXED,
    HIGH,
    MACRO_STEP,
    PERIOD,
    CoupledEngine,
    Rhythm,
    Wiring,
)
from anima_reborn.substrate import coupled_matrix, coupled_phi, representation

WORDS = [
    "고양이", "자동차", "바다", "연필", "하늘", "돌멩이", "웃음", "기차",
    "구름", "의자", "강물", "종이", "산", "모래", "노래", "버스",
]
"""Sixteen drives. The reading scales with what the inputs carry, and eight left
the ratio close enough to the floor to be argued about."""


def encode(word: str) -> float:
    digest = hashlib.blake2b(word.encode("utf-8"), digest_size=2).digest()
    return int.from_bytes(digest, "big") / 65535.0 * 2.0 - 1.0


DRIVES = [encode(w) for w in WORDS]


def represents(rhythm: Rhythm, *, seeds: int = 3) -> float:
    return statistics.mean(
        representation(DRIVES, rhythm=rhythm, seed=s).ratio for s in range(1, seeds + 1)
    )


class TestTheSchedule:
    def test_a_fixed_rhythm_never_lets_go(self) -> None:
        rhythm = Rhythm(coupling=0.6)
        assert not rhythm.alternates
        assert [rhythm.at(t) for t in range(5)] == [0.6] * 5

    def test_an_alternating_rhythm_listens_first(self) -> None:
        """A run should begin by taking something in, not by settling into the
        ring's attractor with nothing heard."""
        rhythm = Rhythm(coupling=0.7, period=2)
        assert [rhythm.at(t) for t in range(8)] == [0, 0, 0.7, 0.7, 0, 0, 0.7, 0.7]

    def test_the_mean_is_what_a_fixed_control_must_match(self) -> None:
        assert Rhythm(coupling=0.7, period=10).mean == pytest.approx(0.35)
        assert Rhythm(coupling=0.7).mean == pytest.approx(0.7)

    def test_a_rhythm_is_measured_over_a_whole_cycle(self) -> None:
        """Half a cycle would report one phase's transition matrix and call it
        the engine's."""
        assert Rhythm(coupling=0.7, period=10).macro_step == 20
        assert Rhythm(coupling=0.7).macro_step == MACRO_STEP

    def test_the_shipped_rhythms_are_what_they_say(self) -> None:
        assert FIXED == Rhythm(coupling=1.0, period=None)
        assert ALTERNATING == Rhythm(coupling=HIGH, period=PERIOD)

    def test_configuration_is_validated(self) -> None:
        with pytest.raises(ValueError, match="coupling must be in"):
            Rhythm(coupling=1.4)
        with pytest.raises(ValueError, match="coupling must be in"):
            Rhythm(coupling=-0.1)
        with pytest.raises(ValueError, match="period must be >= 1"):
            Rhythm(period=0)
        with pytest.raises(ValueError, match="drive must be in"):
            CoupledEngine(drive=2.0)


class TestTheDefaultChangedNothing:
    """Rhythms were added to an engine whose measurements were already
    published. If the default moved a single float, those numbers stopped
    referring to this code."""

    def test_the_default_is_the_engine_as_it_was(self) -> None:
        assert CoupledEngine(seed=1).rhythm == FIXED

    def test_at_full_coupling_the_drive_is_unreachable(self) -> None:
        """Bit-identical, not merely close. This is the wall stated exactly:
        a unit whose target is entirely its partner cannot hear anything."""
        deaf = CoupledEngine(seed=5, drive=0.0).run(400)
        shouted = CoupledEngine(seed=5, drive=1.0).run(400)
        assert deaf.values == shouted.values

    def test_and_the_reading_says_so(self) -> None:
        state = CoupledEngine(seed=5).run(10)
        assert state.coupling == 1.0
        assert not state.listening


class TestTheWall:
    def test_representation_falls_as_the_coupling_rises(self) -> None:
        readings = [represents(Rhythm(c)) for c in (0.0, 0.35, 0.7, 1.0)]
        assert readings == sorted(readings, reverse=True), readings

    def test_at_the_top_nothing_of_the_drive_survives(self) -> None:
        """Different drives separate the engine no more than one drive separates
        from itself — the floor is structural, not a chosen bar."""
        assert not representation(DRIVES, rhythm=FIXED).represents

    def test_and_at_the_bottom_it_all_does(self) -> None:
        assert representation(DRIVES, rhythm=Rhythm(0.0)).represents


class TestTheWayThrough:
    def test_alternating_represents_where_the_same_coupling_cannot(self) -> None:
        """`HIGH` held fixed destroys the drive; released half the time it does
        not, at the same coupling value."""
        assert represents(Rhythm(HIGH)) < 1.0
        assert represents(ALTERNATING) > 3.0

    def test_it_integrates_more_than_a_fixed_coupling_at_its_own_mean(self) -> None:
        """The control that matters. Both spend the same coupling on average and
        sit at the same tau, so an advantage here is the rhythm's and not the
        mean's. Measured with nothing being said (`drive` 0), which is a
        condition and not an oversight — see the next test for why.

        Resolvable: 8.08 vs 0.90 at 1600 trials, 8.02 vs 0.85 at 6400, so this
        is not the estimator's bias being read as a difference.
        """
        alternating = statistics.mean(
            coupled_phi(rhythm=ALTERNATING, trials=1600, seed=s, with_complex=False)
            .directed_phi
            for s in range(2)
        )
        same_mean = statistics.mean(
            coupled_phi(
                rhythm=Rhythm(ALTERNATING.mean),
                macro_step=ALTERNATING.macro_step,
                trials=1600,
                seed=s,
                with_complex=False,
            ).directed_phi
            for s in range(2)
        )
        assert alternating > same_mean, (alternating, same_mean)

    def test_a_rhythms_integration_depends_on_what_it_is_told(self) -> None:
        """Why no test here asserts that a rhythm out-integrates a fixed
        coupling, and why the claim that it does was withdrawn.

        A fixed engine cannot hear, so its transition matrix is bit-identical
        whatever the drive — Phi is a property of the engine alone. A rhythm
        hears, so its matrix moves with the drive, and its Phi moves too:
        measured at tau 40, alternating 20/20 reads 14.99 told nothing, 13.16
        told 0.42, and is indistinguishable from fixed coupling told -0.27.
        A direction quoted without the drive is therefore not a finding.

        This is checked on the matrices rather than on Phi because it is then
        exact rather than a threshold on a noisy estimate.
        """
        def grid(rhythm: Rhythm, drive: float) -> list[float]:
            matrix = coupled_matrix(rhythm=rhythm, drive=drive, trials=100, seed=1)
            return [
                matrix.probability(state, unit)
                for state in range(16)
                for unit in range(4)
            ]

        assert grid(FIXED, 0.0) == grid(FIXED, 0.9)
        assert grid(ALTERNATING, 0.0) != grid(ALTERNATING, 0.9)

    def test_what_it_buys_is_representation_the_other_has_none_of(self) -> None:
        assert representation(DRIVES, rhythm=Rhythm(HIGH, period=20)).represents
        assert not representation(DRIVES, rhythm=FIXED).represents


class TestTheEngineCarriesIt:
    def test_the_phase_is_visible_in_the_reading(self) -> None:
        engine = CoupledEngine(rhythm=Rhythm(0.7, period=3), drive=0.5, seed=1)
        phases = [engine.step().listening for _ in range(9)]
        assert phases == [True] * 3 + [False] * 3 + [True] * 3

    def test_a_drive_moves_it_only_while_listening(self) -> None:
        rhythm = Rhythm(0.7, period=3)
        quiet = CoupledEngine(rhythm=rhythm, drive=0.0, seed=6, initial=(0.0,) * 4)
        loud = CoupledEngine(rhythm=rhythm, drive=1.0, seed=6, initial=(0.0,) * 4)
        # First tick is a listen tick, so one step already separates them.
        assert quiet.step().values != loud.step().values

    def test_reset_keeps_the_rhythm_and_rewinds_the_phase(self) -> None:
        engine = CoupledEngine(rhythm=ALTERNATING, seed=1)
        engine.run(PERIOD + 1)
        assert not engine.state.listening
        engine.reset()
        assert engine.rhythm == ALTERNATING
        assert engine.state.listening

    def test_a_seed_makes_a_rhythmic_run_reproducible(self) -> None:
        left = CoupledEngine(rhythm=ALTERNATING, drive=0.4, seed=9).run(120)
        right = CoupledEngine(rhythm=ALTERNATING, drive=0.4, seed=9).run(120)
        assert left == right

    def test_the_wirings_still_falsify_under_a_rhythm(self) -> None:
        """Whatever the rhythm does, it does not make an uncoupled engine
        behave like the ring."""
        engine = CoupledEngine(wiring=Wiring.SELF, rhythm=ALTERNATING, seed=1)
        assert engine.run(200).coupling in (0.0, HIGH)


class TestAVectorDrive:
    """A scalar says the same thing to every unit, which is all a single number
    can say. A representation is not a single number, so it arrives as its
    average unless the engine can be told one value per unit."""

    def test_a_scalar_is_the_same_thing_said_to_every_unit(self) -> None:
        """Bit-identical, so nothing measured before vectors existed moved."""
        scalar = CoupledEngine(rhythm=ALTERNATING, drive=0.3, seed=2).run(200)
        spelled = CoupledEngine(
            rhythm=ALTERNATING, drive=(0.3, 0.3, 0.3, 0.3), seed=2
        ).run(200)
        assert scalar.values == spelled.values

    def test_it_says_something_a_scalar_cannot(self) -> None:
        """Same mean, different message — so the vector is not arriving as its
        average, which is the whole reason for it."""
        vector = CoupledEngine(
            rhythm=ALTERNATING, drive=(0.8, -0.8, 0.4, -0.4), seed=3
        ).run(200)
        averaged = CoupledEngine(rhythm=ALTERNATING, drive=0.0, seed=3).run(200)
        assert vector.values != averaged.values

    def test_the_engine_still_cannot_hear_it_at_full_coupling(self) -> None:
        deaf = CoupledEngine(drive=(0.8, -0.8, 0.4, -0.4), seed=4).run(200)
        silent = CoupledEngine(drive=0.0, seed=4).run(200)
        assert deaf.values == silent.values

    def test_it_is_validated_on_every_assignment(self) -> None:
        engine = CoupledEngine(seed=1)
        with pytest.raises(ValueError, match="drive must be one value or 4"):
            engine.drive = (0.1, 0.2)
        with pytest.raises(ValueError, match="drive must be in"):
            engine.drive = (0.1, 0.2, 0.3, 1.5)
        with pytest.raises(ValueError, match="drive must be in"):
            CoupledEngine(drive=2.0)

    def test_it_reads_back_in_the_shape_it_was_given(self) -> None:
        engine = CoupledEngine(seed=1, drive=(0.1, 0.2, 0.3, 0.4))
        assert engine.drive == (0.1, 0.2, 0.3, 0.4)
        engine.drive = 0.5
        assert engine.drive == 0.5


class TestRepresentationIsValidated:
    def test_it_needs_something_to_compare(self) -> None:
        with pytest.raises(ValueError, match="drives must have at least 2"):
            representation([0.5])
        with pytest.raises(ValueError, match="noise_seeds must be >= 2"):
            representation(DRIVES, noise_seeds=1)
        with pytest.raises(ValueError, match="tail must be in"):
            representation(DRIVES, ticks=50, tail=80)

    def test_the_reading_carries_its_conditions(self) -> None:
        reading = representation(DRIVES[:4], rhythm=ALTERNATING, ticks=200, tail=80)
"""The English-bottleneck proof: real English does not survive the 3-bit engine.

These pin the certificate (the data-processing bound), the object being unrepresentable, the
deaf null, and the "shared bits are not meaning" scramble — so the honest answer to "make
real English conversation possible" cannot silently rot into an overclaim.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "english_bottleneck.py"
_spec = importlib.util.spec_from_file_location("english_bottleneck", _PATH)
eb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eb)


class TestCorpus:
    def test_the_corpus_is_closed_and_balanced(self) -> None:
        assert len(eb.VERBS) == 8 and len(set(eb.VERBS)) == 8
        assert len(eb.OBJECTS) == 4 and len(set(eb.OBJECTS)) == 4
        assert len(eb.COMMANDS) == 32

    def test_unknown_input_is_out_of_domain(self) -> None:
        assert eb.out_of_domain("teleport", "box") is True
        assert eb.out_of_domain("move", "spaceship") is True
        assert eb.out_of_domain("move", "box") is False

    def test_only_the_verb_is_encoded_into_three_bits(self) -> None:
        for command in eb.COMMANDS:
            code = eb.encode_verb(command)
            assert 0 <= code <= 7  # at most 8 carrier symbols


class TestTheCertificate:
    def test_the_run_is_reproducible(self) -> None:
        assert eb.run_arm("live") == eb.run_arm("live")

    def test_the_data_processing_bound_holds(self) -> None:
        live = eb.run_arm("live")
        assert live["I_XY"] <= live["H_C"] + 1e-9
        assert live["H_C"] <= 3.0 + 1e-9
        assert live["I_XY"] <= 3.0 + 1e-9

    def test_the_object_is_unrepresentable(self) -> None:
        """It was never encoded, so no information about it can survive — the loss is
        capacity, not noise, and every output hides all four objects."""
        live = eb.run_arm("live")
        assert live["I_object_Y"] < 0.05, live["I_object_Y"]
        assert live["candidates"] == float(len(eb.OBJECTS))
        assert abs(live["residual_HXY"] - math.log2(len(eb.OBJECTS))) < 0.05

    def test_the_deaf_null_collapses(self) -> None:
        """Drive bit-unreachable: the carrier must lose the code, proving the engine was in
        the path at all."""
        deaf = eb.run_arm("deaf")
        assert deaf["I_CC"] < 0.2, deaf["I_CC"]
        assert deaf["I_XY"] <= deaf["floor_XY"] + 0.05

    def test_shared_bits_are_not_meaning(self) -> None:
        """A codebook that ignores the verb keeps sentence identity (I(X;Y) high) while the
        predeclared verb relation collapses — so "3 bits shared with English" is not "3 bits
        of English meaning"."""
        scramble = eb.run_arm("scramble")
        assert scramble["I_XY"] > 2.5
        assert scramble["I_verb_Y"] < scramble["I_XY"] - 1.0

    def test_the_engine_contribution_is_only_carrying(self) -> None:
        """The ideal (no-engine) carrier already scores the ceiling; the engine adds only
        the 3 bits the deaf arm loses."""
        ideal = eb.run_arm("ideal")
        deaf = eb.run_arm("deaf")
        assert ideal["I_CC"] > 2.9
        assert ideal["I_CC"] - deaf["I_CC"] > 2.5
"""The 3-bit PAIRS channel added for the free-conversation tab, and its 1-bit exactness.

`channel`/`channel_trace` gained a `bits=` parameter. `bits=1` (default) MUST stay
byte-for-byte the published 1-bit ring — the reproducible half's numbers were measured on
it (`default-stays-exact`). `bits=3` is the proven `Wiring.PAIRS` substrate, calibrated in
`state/communication/conversation_channel.py`; these pin its driven-decode fidelity and its
deaf null so the channel's own fidelity (the human's accuracy ceiling) cannot silently rot.
"""

from __future__ import annotations

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring
from anima_reborn.dialogue import HOLD, TELL, channel, channel_trace


def _old_one_bit_channel(signal: int, *, seed: int, deaf: bool = False) -> int:
    """The 1-bit ring exactly as it was before `bits=` existed — the golden reference."""
    drive = (0.8, -0.8) if signal == 0 else (-0.8, 0.8)
    engine = CoupledEngine(
        units=2, wiring=Wiring.RING,
        rhythm=FIXED if deaf else ALTERNATING,
        drive=drive, seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    values = engine.run(HOLD).values
    return 0 if (values[0] - values[1]) > 0 else 1


class TestDefaultStaysExact:
    def test_one_bit_default_is_byte_for_byte_the_published_channel(self) -> None:
        for seed in range(300):
            for signal in (0, 1):
                for deaf in (False, True):
                    assert channel(signal, seed=seed, deaf=deaf) == _old_one_bit_channel(
                        signal, seed=seed, deaf=deaf
                    ), (seed, signal, deaf)

    def test_one_bit_is_the_default(self) -> None:
        # A single latch: two possible words, and the trace is 2 units wide.
        assert channel(1, seed=1) in (0, 1)
        assert len(channel_trace(0, seed=1)[-1]) == 2


class TestThreeBitChannel:
    def test_driven_decode_is_clean(self) -> None:
        """Calibrated at joint 1.000 — a strongly driven bistable latch from origin settles
        deterministically, so the wire is not what limits a human's recovery."""
        hits = 0
        total = 0
        for symbol in range(8):
            for seed in range(40):
                total += 1
                if channel(symbol, seed=seed * 13 + 1, bits=3) == symbol:
                    hits += 1
        assert hits / total >= 0.99, hits / total

    def test_the_trace_is_six_units_wide(self) -> None:
        trace = channel_trace(5, seed=3, bits=3)
        assert len(trace) == HOLD
        assert all(len(row) == 6 for row in trace)

    def test_deaf_carries_no_symbol(self) -> None:
        """Coupling 1.0 makes the drive bit-unreachable, so the decoded word cannot track
        the symbol — the null proving the channel was in the path (calibrated at 1/8)."""
        hits = 0
        total = 0
        for symbol in range(8):
            for seed in range(40):
                total += 1
                if channel(symbol, seed=seed * 13 + 1, bits=3, deaf=True) == symbol:
                    hits += 1
        assert hits / total <= 0.30, hits / total

    def test_a_bad_bit_count_is_rejected(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            channel(0, seed=1, bits=2)

Repository constraints and null patterns are now grounded. The synthesis distinguishes repeated transmission from impossible same-width delayed recall, and separates functional irreducibility certificates from exact Φ.
  ✓ Inspect repository guidance and the cited engine, measurement, learner, and null implementations
  ✓ Evaluate directions A–E against the proven constraints and identify the first component
  → Produce a concrete architecture, validations/nulls, compatibility contract, and phased plan
  ✓ Inspect repository guidance and the cited engine, measurement, learner, and null implementations
  ✓ Evaluate directions A–E against the proven constraints and identify the first component
  ✓ Produce a concrete architecture, validations/nulls, compatibility contract, and phased plan
codex
The true bottleneck is **composition across time**, not raw latch capacity. The engine already has a measured 3-bit carrier; the smallest honest frontier move is to reuse that carrier over multiple audited turns while preserving order and limited context.

Build **A first, but not as an impossible same-width tape**. A six-unit system with eight distinguishable held states cannot silently retain an arbitrary multi-symbol history. It can transmit up to three new bits each turn, or retain a three-bit summary/context, but it cannot do both without paying capacity.

One-line dissent: if “more content held simultaneously as one integrated entity” is mandatory, build C first and do not start D until C passes.

## Recommended architecture

### 1. `TemporalChannel`: repeated, ordered use of the existing carrier

Add a new `sequence.py`, initially as a wrapper around the existing PAIRS engine rather than a new response law.

Each fixed-length slot runs:

1. **WRITE:** `Wiring.PAIRS`, differential drive, alternating rhythm.
2. **HOLD:** fixed full coupling, zero drive—the existing deaf hold.
3. **EMIT:** read the three pair differentials.
4. **ADVANCE:** overwrite those latches with the next symbol.

The wrapper may retain the public phase and slot index, but **must not retain past symbols or decoded outputs**. The receiver’s transcript is allowed to accumulate information; the engine is not thereby claiming sequence memory.

For a feedback-free audit,

\[
I(X_{1:T};Y_{1:T}) \leq \sum_t H(C_t) \leq 3T.
\]

That is a channel-use bound, not a measured result and not simultaneous integrated capacity. Interactive free play remains non-evidence, following [conversation.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/conversation.py:1); measurement happens only in a frozen, balanced, feedback-free audit.

Measure:

- Exact categorical \(I(X_{1:T};Y_{1:T})\) on a fixed balanced sequence corpus.
- Per-slot \(I(X_t;Y_t)\) and the surviving fraction relative to the ideal carrier.
- Exact-sequence recovery and order recovery on sequences with identical symbol histograms.
- \(2^{H(Y_{1:T})}\), distinct reproducible output sequences, and effective temporal rank beside capacity.
- Retention versus the WRITE→EMIT deaf delay.

Required arms:

- **Ideal carrier:** same temporal codec with no substrate.
- **Deaf:** full coupling during WRITE, making the drive unreachable.
- **Time shift:** circularly shift output slots relative to inputs, preserving symbol frequencies while destroying temporal correspondence.
- **Order erased:** sort or bag the outputs; this must fail on same-symbol/different-order pairs.
- **Forgetting null:** reset after WRITE, or substitute an acyclic wiring before EMIT.
- **Final-state-only audit:** suppress intermediate emissions and decode the whole history from the final six-unit state. This should expose the eight-state ceiling and prevents the transcript from being mislabeled engine memory.

This earns “ordered multi-turn transmission,” not “the engine remembers an arbitrarily long sentence.”

### 2. `ContextGate`: genuine but bounded temporal state

After repeated transmission works, add pair-selective timing:

- One pair remains in HOLD and carries context.
- The other two pairs enter WRITE and carry the next payload.
- On a context-update phase, the roles reverse.
- All updates remain simultaneous and use the current tanh response.

This likely needs an optional per-pair coupling schedule in [coupled.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/coupled.py:423), rather than changing the response function. It explicitly pays for memory: reserving a context latch leaves fewer payload latches.

The capability test is delayed conditional response:

> Present the same payload after two different held contexts; the later engine response must distinguish the contexts after silence.

Nulls:

- Reset or overwrite the context before the payload.
- `chain=0`, which removes the cross-pair causal path.
- A fixed-coupling schedule at the selective rhythm’s time average.
- Shuffle context–payload pairings while retaining both marginals.

Report context fidelity, payload fidelity, joint output width, and effective rank. A high response with collapsed payload width is not success.

### 3. E: `GroundedSequenceLearner`

This is the highest-leverage semantic component, but it depends on the temporal carrier.

Add a new `protocol.py`; do not overload `align.py`, whose earned claim is cross-modal co-occurrence alignment. The learner should acquire a finite compositional convention from consequences:

- A message consists of temporally separated role/value tokens.
- Separate local policies learn the token used for each role/value and the receiver’s corresponding action factor.
- Reinforcement comes from an externally observable task outcome, not English labels.
- Temporal position supplies the role boundary. That factorization is designer-provided and must be declared as such.

Train on only some role-value combinations and audit on unseen combinations. Success then means constituent mappings compose beyond memorized messages.

Required nulls:

- **Held-out combinations:** the headline.
- **Time-shifted pairing:** correct signals and outcomes, wrong temporal correspondence.
- **Yoked reward:** identical reward history made independent of the learner’s message/action.
- **Frozen learner:** measured untrained baseline.
- **Flat codebook control:** may memorize seen combinations but should not generalize.
- **Semantic scramble:** preserve message identity while destroying the declared relation to the task, analogous to the English codebook scramble.
- **Channel-before-carrier:** audit intended token sequences before and after the substrate.

Report used symbols per role, entropy/effective width, policy rank, held-out accuracy gain over the learner’s own baseline, and the shuffled/yoked floors.

The earned claim would be: “a finite grounded convention composed across turns and generalized to held-out combinations.” It would still not be English.

## Direction-by-direction verdict

### A. Time accumulation: proceed, with a correction

Time is the best first escape for communication. It raises transcript information without widening the instantaneously measured system.

But “write \(T\) symbols, remain silent, then retrieve all \(T\) from the same six units” is impossible beyond the state capacity. Any implementation that passes by retaining a Python list is an external tape. The final-state-only audit kills that overclaim.

Use `TemporalChannel` for ordered transmission and `ContextGate` for bounded temporal dependence.

### B. Multistable units: prune for now

A candidate law could be a coupled multi-well system,

\[
x_i' = x_i + \eta\left[-V_i'(x_i)+\text{partner response}+\text{drive}\right]+\epsilon,
\]

where \(V_i\) has several stable minima. But fixed well locations are designer-planted categories—the same failure mode as D7. A periodic response merely hides those categories in phase intervals.

The only admissible later version would learn well locations from co-occurrence, freeze them before audit, and pass:

- Held-out cross-modal basin agreement.
- Shuffled-co-occurrence and untrained controls.
- Reproducible basin occupancy across walks.
- Retention and use, not just attractor count.
- Effective occupied width, not nominal \(k\).

The current Φ machinery does not apply unchanged: it assumes binary units. A \(k\)-ary TPM has \(k^n\) states; one-hot encoding changes the mechanism and worsens the measurement wall. Therefore B cannot presently earn “more integrated bits per unit.”

### C. Scalable integration measurement: required before hierarchy claims

Add two explicitly different lanes to `substrate.py`.

#### C0. Directed Interventional Min-Cut certificate

For every declared directed edge \(u\rightarrow v\), estimate a non-cancelling causal effect using paired interventions:

\[
e_{u\to v}
=
\mathbb{E}_{x_{\setminus u},a,b}
JS\!\left(
P(Y_v\mid do(X_u=a),x_{\setminus u}),
P(Y_v\mid do(X_u=b),x_{\setminus u})
\right).
\]

Use common random seeds for paired trials. Construct the weighted directed causal graph and compute its minimum directed cut with a deterministic stdlib implementation. This scales with measured edges and intervention samples, rather than all global states.

It is a **cut certificate**, not Φ. It can establish that influence returns across every directed cut and quantify the weakest measured causal seam.

Validation against exact directed Φ:

- On all systems up to six units, always compute both.
- Include RING, SELF, FEEDFORWARD, disjoint PAIRS, chained odd PAIRS, multiple states, rhythms, gains and macro-steps.
- Require exact agreement on reducible versus irreducible cases.
- Require the proxy null to approach zero as intervention samples grow.
- Record estimation error, state/context coverage and seed dispersion.
- A severed-edge control must collapse the corresponding cut.
- Width alone must not raise the null.

“Match exact Φ” cannot honestly mean equal numeric units for a different functional. Under the strict reading, the public API should return exact `directed_big_phi` below the size cap and a distinctly typed `CutCertificate` above it—never a wide-width field named `phi`.

#### C1. Sampled directed-Φ research lane

If an actual approximation is pursued, sample TPM rows, mechanisms, purviews, partitions and directed cuts using nested deterministic budgets. Its acceptance contract is:

- Exhaustive mode on small systems returns the existing exact result bit-for-bit.
- Approximation error against exact Φ shrinks with both transition and structural sample budgets.
- SELF/FEEDFORWARD artefacts shrink toward zero with samples.
- Candidate-cut coverage is reported; sampling only convenient cuts cannot certify the minimum.
- Wide results include budget, coverage, confidence interval and null trajectory.

Until those gates pass, it is an experiment—not evidence that a wide system is integrated.

### D. Hierarchy: viable only after C

Do not compose two modules. With three pairs per module, an even number of modules recreates an even macro-cycle and invites locking. Start with an odd number of odd-pair modules.

Add a separate `hierarchy.py` rather than complicating the old default path. Each module is a six-unit PAIRS engine. A sparse gateway ring adds slow inter-module influence:

\[
p_{m,i} =
(1-\alpha-\beta_i)F(x_{m,i\oplus1})
+\alpha F(x_{m,i+2})
+\beta_iF(x_{m-1,g(i)}),
\]

where \(F(z)=-A\tanh(gz/A)\), \(\alpha\) is the intra-module chain and \(\beta_i\) is nonzero only at declared gateway units. All modules read one simultaneous snapshot.

Measure three separate things:

- **Storage:** reproducible joint differential words across walks, plus effective output width/rank.
- **Binding as function:** flip only a gateway pair in module 0 and measure response in later modules.
- **Irreducibility:** C’s directed cut certificate; exact Φ is unavailable at this width.

Nulls:

- `β=0`: equally capable disjoint modules.
- Sever one gateway direction.
- Shuffle module outputs after independent execution.
- Even module count as the macro-lock control.
- Strong gateway coupling that collapses joint rank: high response with low width is failure.

Without a validated C result, the honest claim is only “coupled modules transmit cross-module influence,” not “one integrated hierarchy.”

## `default-stays-exact`

Prefer new modules for the first phase, so existing constructors do not move at all.

If `CoupledEngine` later gains a per-pair schedule or alternate response, its default must be `None` and take the original branch before any new arithmetic or RNG draw. Do not compute `old + 0 * new`; even that can move floating-point results.

Pin:

- Checked-in `float.hex()` trajectories for representative RING/PAIRS/SELF/FEEDFORWARD configurations.
- Exact `CoupledState` equality across fixed seeds, drives, rhythms and chains.
- Exact `coupled_matrix(...).values` for fixed seeds and trials.
- Existing one-bit channel equality across all existing test seeds.
- Published default dialogue/conversation outputs and IIT goldens.
- Unchanged RNG consumption, demonstrated by later trajectory equality.

This extends the existing compatibility discipline in [test_rhythm.py](/Users/mini/dancinlab/anima-reborn/tests/test_rhythm.py:106) and [test_conversation_channel.py](/Users/mini/dancinlab/anima-reborn/tests/test_conversation_channel.py:29).

Any new top-level engine also needs the viewer route/readout in the same change, per the repo’s lockstep rule.

## Phased build plan

1. **Temporal carrier.** Build fixed-length `TemporalChannel` on the unchanged six-unit engine. Ship balanced sequence audits, time-shift/order/deaf/forgetting nulls, effective width, and the final-state-only ceiling test.

2. **Bounded context and grounding.** Add pair-selective timing, measure context-dependent use, then add `GroundedSequenceLearner`. Require frozen blind audits on held-out combinations and yoked/time-shifted controls.

3. **Scalable measurement.** Build the directed interventional min-cut certificate and validate it beside exact directed Φ at small widths. Pursue sampled Φ only as a separately typed research lane.

4. **Odd modular hierarchy.** Add sparse slow gateways between an odd number of odd-pair modules. Ship storage, rank, cross-module function and severed-link controls. Make no whole-system integration claim unless Phase 3 passed.

5. **Multistability only if learned.** Revisit B only after data-derived basins and a categorical measurement path exist. A hand-written periodic or polynomial multi-well should be rejected.

## Honest ceiling

If all phases work, the engine gains:

- More information **across a transcript**.
- A bounded internal context that affects later responses.
- A finite grounded convention that composes on held-out combinations.
- Potentially more simultaneous physical storage in a measured causal hierarchy.

It does not gain open-ended memory, open vocabulary, English generation, or language understanding. It becomes closer to language only in specific measurable ingredients—order, context, grounding and compositional generalization. The human-facing English remains a label or interface around a finite protocol unless its semantic relations are independently learned and audited.
tokens used
91,557
The true bottleneck is **composition across time**, not raw latch capacity. The engine already has a measured 3-bit carrier; the smallest honest frontier move is to reuse that carrier over multiple audited turns while preserving order and limited context.

Build **A first, but not as an impossible same-width tape**. A six-unit system with eight distinguishable held states cannot silently retain an arbitrary multi-symbol history. It can transmit up to three new bits each turn, or retain a three-bit summary/context, but it cannot do both without paying capacity.

One-line dissent: if “more content held simultaneously as one integrated entity” is mandatory, build C first and do not start D until C passes.

## Recommended architecture

### 1. `TemporalChannel`: repeated, ordered use of the existing carrier

Add a new `sequence.py`, initially as a wrapper around the existing PAIRS engine rather than a new response law.

Each fixed-length slot runs:

1. **WRITE:** `Wiring.PAIRS`, differential drive, alternating rhythm.
2. **HOLD:** fixed full coupling, zero drive—the existing deaf hold.
3. **EMIT:** read the three pair differentials.
4. **ADVANCE:** overwrite those latches with the next symbol.

The wrapper may retain the public phase and slot index, but **must not retain past symbols or decoded outputs**. The receiver’s transcript is allowed to accumulate information; the engine is not thereby claiming sequence memory.

For a feedback-free audit,

\[
I(X_{1:T};Y_{1:T}) \leq \sum_t H(C_t) \leq 3T.
\]

That is a channel-use bound, not a measured result and not simultaneous integrated capacity. Interactive free play remains non-evidence, following [conversation.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/conversation.py:1); measurement happens only in a frozen, balanced, feedback-free audit.

Measure:

- Exact categorical \(I(X_{1:T};Y_{1:T})\) on a fixed balanced sequence corpus.
- Per-slot \(I(X_t;Y_t)\) and the surviving fraction relative to the ideal carrier.
- Exact-sequence recovery and order recovery on sequences with identical symbol histograms.
- \(2^{H(Y_{1:T})}\), distinct reproducible output sequences, and effective temporal rank beside capacity.
- Retention versus the WRITE→EMIT deaf delay.

Required arms:

- **Ideal carrier:** same temporal codec with no substrate.
- **Deaf:** full coupling during WRITE, making the drive unreachable.
- **Time shift:** circularly shift output slots relative to inputs, preserving symbol frequencies while destroying temporal correspondence.
- **Order erased:** sort or bag the outputs; this must fail on same-symbol/different-order pairs.
- **Forgetting null:** reset after WRITE, or substitute an acyclic wiring before EMIT.
- **Final-state-only audit:** suppress intermediate emissions and decode the whole history from the final six-unit state. This should expose the eight-state ceiling and prevents the transcript from being mislabeled engine memory.

This earns “ordered multi-turn transmission,” not “the engine remembers an arbitrarily long sentence.”

### 2. `ContextGate`: genuine but bounded temporal state

After repeated transmission works, add pair-selective timing:

- One pair remains in HOLD and carries context.
- The other two pairs enter WRITE and carry the next payload.
- On a context-update phase, the roles reverse.
- All updates remain simultaneous and use the current tanh response.

This likely needs an optional per-pair coupling schedule in [coupled.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/coupled.py:423), rather than changing the response function. It explicitly pays for memory: reserving a context latch leaves fewer payload latches.

The capability test is delayed conditional response:

> Present the same payload after two different held contexts; the later engine response must distinguish the contexts after silence.

Nulls:

- Reset or overwrite the context before the payload.
- `chain=0`, which removes the cross-pair causal path.
- A fixed-coupling schedule at the selective rhythm’s time average.
- Shuffle context–payload pairings while retaining both marginals.

Report context fidelity, payload fidelity, joint output width, and effective rank. A high response with collapsed payload width is not success.

### 3. E: `GroundedSequenceLearner`

This is the highest-leverage semantic component, but it depends on the temporal carrier.

Add a new `protocol.py`; do not overload `align.py`, whose earned claim is cross-modal co-occurrence alignment. The learner should acquire a finite compositional convention from consequences:

- A message consists of temporally separated role/value tokens.
- Separate local policies learn the token used for each role/value and the receiver’s corresponding action factor.
- Reinforcement comes from an externally observable task outcome, not English labels.
- Temporal position supplies the role boundary. That factorization is designer-provided and must be declared as such.

Train on only some role-value combinations and audit on unseen combinations. Success then means constituent mappings compose beyond memorized messages.

Required nulls:

- **Held-out combinations:** the headline.
- **Time-shifted pairing:** correct signals and outcomes, wrong temporal correspondence.
- **Yoked reward:** identical reward history made independent of the learner’s message/action.
- **Frozen learner:** measured untrained baseline.
- **Flat codebook control:** may memorize seen combinations but should not generalize.
- **Semantic scramble:** preserve message identity while destroying the declared relation to the task, analogous to the English codebook scramble.
- **Channel-before-carrier:** audit intended token sequences before and after the substrate.

Report used symbols per role, entropy/effective width, policy rank, held-out accuracy gain over the learner’s own baseline, and the shuffled/yoked floors.

The earned claim would be: “a finite grounded convention composed across turns and generalized to held-out combinations.” It would still not be English.

## Direction-by-direction verdict

### A. Time accumulation: proceed, with a correction

Time is the best first escape for communication. It raises transcript information without widening the instantaneously measured system.

But “write \(T\) symbols, remain silent, then retrieve all \(T\) from the same six units” is impossible beyond the state capacity. Any implementation that passes by retaining a Python list is an external tape. The final-state-only audit kills that overclaim.

Use `TemporalChannel` for ordered transmission and `ContextGate` for bounded temporal dependence.

### B. Multistable units: prune for now

A candidate law could be a coupled multi-well system,

\[
x_i' = x_i + \eta\left[-V_i'(x_i)+\text{partner response}+\text{drive}\right]+\epsilon,
\]

where \(V_i\) has several stable minima. But fixed well locations are designer-planted categories—the same failure mode as D7. A periodic response merely hides those categories in phase intervals.

The only admissible later version would learn well locations from co-occurrence, freeze them before audit, and pass:

- Held-out cross-modal basin agreement.
- Shuffled-co-occurrence and untrained controls.
- Reproducible basin occupancy across walks.
- Retention and use, not just attractor count.
- Effective occupied width, not nominal \(k\).

The current Φ machinery does not apply unchanged: it assumes binary units. A \(k\)-ary TPM has \(k^n\) states; one-hot encoding changes the mechanism and worsens the measurement wall. Therefore B cannot presently earn “more integrated bits per unit.”

### C. Scalable integration measurement: required before hierarchy claims

Add two explicitly different lanes to `substrate.py`.

#### C0. Directed Interventional Min-Cut certificate

For every declared directed edge \(u\rightarrow v\), estimate a non-cancelling causal effect using paired interventions:

\[
e_{u\to v}
=
\mathbb{E}_{x_{\setminus u},a,b}
JS\!\left(
P(Y_v\mid do(X_u=a),x_{\setminus u}),
P(Y_v\mid do(X_u=b),x_{\setminus u})
\right).
\]

Use common random seeds for paired trials. Construct the weighted directed causal graph and compute its minimum directed cut with a deterministic stdlib implementation. This scales with measured edges and intervention samples, rather than all global states.

It is a **cut certificate**, not Φ. It can establish that influence returns across every directed cut and quantify the weakest measured causal seam.

Validation against exact directed Φ:

- On all systems up to six units, always compute both.
- Include RING, SELF, FEEDFORWARD, disjoint PAIRS, chained odd PAIRS, multiple states, rhythms, gains and macro-steps.
- Require exact agreement on reducible versus irreducible cases.
- Require the proxy null to approach zero as intervention samples grow.
- Record estimation error, state/context coverage and seed dispersion.
- A severed-edge control must collapse the corresponding cut.
- Width alone must not raise the null.

“Match exact Φ” cannot honestly mean equal numeric units for a different functional. Under the strict reading, the public API should return exact `directed_big_phi` below the size cap and a distinctly typed `CutCertificate` above it—never a wide-width field named `phi`.

#### C1. Sampled directed-Φ research lane

If an actual approximation is pursued, sample TPM rows, mechanisms, purviews, partitions and directed cuts using nested deterministic budgets. Its acceptance contract is:

- Exhaustive mode on small systems returns the existing exact result bit-for-bit.
- Approximation error against exact Φ shrinks with both transition and structural sample budgets.
- SELF/FEEDFORWARD artefacts shrink toward zero with samples.
- Candidate-cut coverage is reported; sampling only convenient cuts cannot certify the minimum.
- Wide results include budget, coverage, confidence interval and null trajectory.

Until those gates pass, it is an experiment—not evidence that a wide system is integrated.

### D. Hierarchy: viable only after C

Do not compose two modules. With three pairs per module, an even number of modules recreates an even macro-cycle and invites locking. Start with an odd number of odd-pair modules.

Add a separate `hierarchy.py` rather than complicating the old default path. Each module is a six-unit PAIRS engine. A sparse gateway ring adds slow inter-module influence:

\[
p_{m,i} =
(1-\alpha-\beta_i)F(x_{m,i\oplus1})
+\alpha F(x_{m,i+2})
+\beta_iF(x_{m-1,g(i)}),
\]

where \(F(z)=-A\tanh(gz/A)\), \(\alpha\) is the intra-module chain and \(\beta_i\) is nonzero only at declared gateway units. All modules read one simultaneous snapshot.

Measure three separate things:

- **Storage:** reproducible joint differential words across walks, plus effective output width/rank.
- **Binding as function:** flip only a gateway pair in module 0 and measure response in later modules.
- **Irreducibility:** C’s directed cut certificate; exact Φ is unavailable at this width.

Nulls:

- `β=0`: equally capable disjoint modules.
- Sever one gateway direction.
- Shuffle module outputs after independent execution.
- Even module count as the macro-lock control.
- Strong gateway coupling that collapses joint rank: high response with low width is failure.

Without a validated C result, the honest claim is only “coupled modules transmit cross-module influence,” not “one integrated hierarchy.”

## `default-stays-exact`

Prefer new modules for the first phase, so existing constructors do not move at all.

If `CoupledEngine` later gains a per-pair schedule or alternate response, its default must be `None` and take the original branch before any new arithmetic or RNG draw. Do not compute `old + 0 * new`; even that can move floating-point results.

Pin:

- Checked-in `float.hex()` trajectories for representative RING/PAIRS/SELF/FEEDFORWARD configurations.
- Exact `CoupledState` equality across fixed seeds, drives, rhythms and chains.
- Exact `coupled_matrix(...).values` for fixed seeds and trials.
- Existing one-bit channel equality across all existing test seeds.
- Published default dialogue/conversation outputs and IIT goldens.
- Unchanged RNG consumption, demonstrated by later trajectory equality.

This extends the existing compatibility discipline in [test_rhythm.py](/Users/mini/dancinlab/anima-reborn/tests/test_rhythm.py:106) and [test_conversation_channel.py](/Users/mini/dancinlab/anima-reborn/tests/test_conversation_channel.py:29).

Any new top-level engine also needs the viewer route/readout in the same change, per the repo’s lockstep rule.

## Phased build plan

1. **Temporal carrier.** Build fixed-length `TemporalChannel` on the unchanged six-unit engine. Ship balanced sequence audits, time-shift/order/deaf/forgetting nulls, effective width, and the final-state-only ceiling test.

2. **Bounded context and grounding.** Add pair-selective timing, measure context-dependent use, then add `GroundedSequenceLearner`. Require frozen blind audits on held-out combinations and yoked/time-shifted controls.

3. **Scalable measurement.** Build the directed interventional min-cut certificate and validate it beside exact directed Φ at small widths. Pursue sampled Φ only as a separately typed research lane.

4. **Odd modular hierarchy.** Add sparse slow gateways between an odd number of odd-pair modules. Ship storage, rank, cross-module function and severed-link controls. Make no whole-system integration claim unless Phase 3 passed.

5. **Multistability only if learned.** Revisit B only after data-derived basins and a categorical measurement path exist. A hand-written periodic or polynomial multi-well should be rejected.

## Honest ceiling

If all phases work, the engine gains:

- More information **across a transcript**.
- A bounded internal context that affects later responses.
- A finite grounded convention that composes on held-out combinations.
- Potentially more simultaneous physical storage in a measured causal hierarchy.

It does not gain open-ended memory, open vocabulary, English generation, or language understanding. It becomes closer to language only in specific measurable ingredients—order, context, grounding and compositional generalization. The human-facing English remains a label or interface around a finite protocol unless its semantic relations are independently learned and audited.
