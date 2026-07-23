<!-- sidecar lab full · model=(default) · cwd=/Users/mini/dancinlab/anima-reborn · prompt=4717 chars · 2026-07-23T09:37:37.266Z -->

── fable (claude-fable-5) · exit 0 ──
코드 확인을 마쳤습니다 — 핵심 구조 셋이 설계를 결정합니다: (1) `directed_big_phi`의 비용은 컷 루프가 아니라 그 위의 distinction 탐색(메커니즘 2^N × purview × partition)이 지배하므로, **컷만 샘플링해서는 천장이 안 올라갑니다** — 프록시는 distinction 사다리 전체를 더 싼 범함수로 대체해야 합니다. (2) `estimate_matrix`의 TPM은 unit별 ON-빈도의 곱-형태이고, substrate의 커널은 "이진 상태 → 재구성 → 새 엔진 → macro_step → 이진화"로 **구성상 마르코프**입니다 — 프록시가 같은 커널을 쓰면 측정 대상이 정확히 같아집니다. (3) `chain`은 `(i+2) % units`로 **닫힌** 매크로-링이므로, 6유닛 너머의 양성(통합) 팔은 홀수 쌍 폭 {10, 14, 18}에만 존재하고 {8, 12, 16, 20}은 잠금-널 폭입니다.

설계안입니다.

---

# 검증된 샘플링 directed-Φ 프록시 — 설계와 검증 프로토콜

## 0. 프록시가 무엇이고 무엇이 아닌가 (한 문장)

프록시는 big-Φ가 아니라 **방향 컷-정보(directed cut-information)** 입니다 — `ei.py`가 이미 연 "Φ의 하계 풍미(EI-계열)" 전례의 방향판·컷별 일반화이며, 크기는 `directed_big_phi`의 비트와 **절대 비교하지 않습니다**. 프록시가 IIT와 공유해야 하는 것은 크기가 아니라 세 가지뿐입니다: **영집합**(reducible ⟺ 0), **MIP 컷의 정체**, **순위**. 검증 사다리가 이 셋을 고정합니다.

## 1. 프록시의 정확한 정의

**측정 커널 (substrate와 동일).** 이진 상태 `s`에서: `±amplitude` 재구성 → 시드 스트림에서 파생된 새 `CoupledEngine` → `macro_step` 틱 → 0-임계 이진화 → `s'`. `coupled_matrix`의 step과 문자 그대로 같은 커널 — 샘플링 방식만 바뀌고 측정 대상은 바뀌지 않습니다.

**상태공간 샘플링 (궤적 레인, Lane S).** 시드 `r = 0..R-1`마다: 균일 랜덤 이진 상태에서 시작, 커널을 `T`회 반복 적용해 연속 전이쌍 `(s_t, s_{t+1})`을 기록. R개 런을 풀링. **예산 `B ≔ R·T` (기본 `B0 = 8 × 512 = 4096` 전이)**. 번인 폐기 없음(커널이 곧 측정 대상이므로 모든 전이가 유효 표본).

**컷별 손실 (추정기).** 방향 컷 `c = (A -/-> B)`에 대해, 풀링된 전이 카운트 위의 **정확 범주형 플러그인 조건부 MI**:

```
loss(c) = Σ_{i∈B}  Î( X_A(t) ; X_i(t+1) | X_Ā(t) )
```

`Î`는 관측된 삼중항 `(x_Ā, x_A, x'_i)` 카운트의 플러그인 추정 — 조건 셀 `x_Ā`를 경험적 빈도로 가중. 합성(미방문) 상태의 TPM 행을 평가할 필요가 전혀 없다는 것이 이 형태를 고른 이유입니다. 평활화 없음. **해석적 편향 보정(Miller–Madow)은 평결에 쓰지 않고 진단으로만 병기** — 편향은 3절의 동일-파이프라인 셔플 바닥이 같은 지지집합·같은 예산에서 *측정*합니다(`RECURRENCE_FLOOR`가 계산이 아니라 측정으로 정해진 것과 같은 철학).

**컷 계열 `C(W, seed)` (결정적).**
- 단독 컷: `{u} -/-> rest`와 `rest -/-> {u}`, 모든 u — 2W개 (feedforward의 공짜 방향을 정확히 담는 계열).
- PAIRS일 때 쌍-원자 호(arc) 컷: 쌍을 원자로 본 매크로-링 위의 모든 연속 호(1..P−1쌍) × 양방향 — MIP가 구조 경계에 앉는 경우를 담는 계열.
- 시드된 랜덤 균형 이분할 `M = 64`개(중복 제거) × 양방향.

**프록시 값.** `Φ̂ = min over C of loss(c)`, argmin 컷 병기. W ≤ 14에서는 계열 대신 **전체 방향 이분할 열거**가 컷별 비용이 싸서 가능하므로(2^(W−1)−1 분할 × 2), 계열은 그 너머에서만 필요 — 그리고 겹치는 폭에서 계열 vs 전체를 대조합니다(V3).

**모든 판독 옆에 붙는 폭 보고 (`report-the-rank`).** 방문 지지집합 크기 |S|, 방문 분포 엔트로피(비트), argmin 컷의 조건 셀 점유(셀당 표본 중앙값). 잠긴 계는 |S| ≈ 2로 읽히고, 그 ~0은 이 숫자가 설명합니다.

**편향 방향의 회계.** 컷-누락은 위로(과잉), 플러그인 MI도 위로(과잉) — 둘 다 셔플 바닥과 정확-일치 창이 잡습니다. 반대로 min-over-noisy-cuts의 선택 편향은 **아래로** — 통합을 과소보고하는 쪽이므로 안전한 방향이고, 문서에 그렇게 적습니다.

## 2. 지상 진실 대비 검증 — 3단 사다리

프록시의 수렴 목표를 먼저 정의합니다: **`Φ_π` ≔ 같은 범함수를, 측정된 상태-대-상태 체인(`estimate_state_matrix`)의 정상분포 π 가중으로, TPM 행에서 닫힌형으로 계산한 값** (W ≤ 6에서 거듭제곱 반복으로 정확히 계산 가능). Lane S는 B → ∞에서 정확히 `Φ_π`로 수렴합니다 — 진짜 "일치 창"은 여기 있습니다.

- **V1 — 범함수 타당성 (W = 2..6, `iit4` 대조).** 격자: {RING, PAIRS chain=0, PAIRS+chain(capacity.py가 쓴 그 값), FEEDFORWARD, SELF} × 시드 5개 × 폭 {2,4,6} (+RING 3,5). 같은 측정 TPM 위에서 전체-컷 `Φ_π`·균일가중판 vs `directed_big_phi`. 고정 조건: **(a) 영집합** — 해석적으로 지은 인수분해/feedforward TPM(레포가 `big_phi=0.000000` 검증에 쓴 방식 그대로)에서 `Φ` 계열이 **정확히 0.0** (부동소수 잔차 아님 — 공짜 방향의 조건부 MI는 항등적으로 0); **(b) MIP 컷** — 전체-컷 argmin이 `directed_big_phi.cut`과 일치(동률은 문서화), 불일치 사례는 기록하고 컷 계열이 IIT의 MIP를 **포함**하는지가 하류 요건; **(c) 순위** — 격자 전체에서 Spearman ρ ≥ 0.9 (명시 허용치; 미달이면 옮길 막대가 아니라 설명할 발견 — `iit4` 골든 규칙 준용).
- **V2 — 샘플링 수렴 (W = 2..6).** `|Φ̂ − Φ_π|`를 예산 B0 → 4B0 → 16B0에서 측정. 허용치: **16B0에서 격자 중앙값 상대오차 ≤ 10%, 그리고 오차가 예산에 단조 감소** — 문서와 테스트 양쪽에 고정(3절). **앵커 사례**: 발표된 6-유닛 `recurrence_evidence` 런의 kwargs 그대로에서 프록시가 같은 "held" 평결을 재현해야 함.
- **V3 — 컷 계열 적정성 (W = 10, 12, 14).** 전체-컷 열거가 아직 싼 폭에서, 계열 `C` vs 전체 열거: min이 셔플 바닥 이내로 일치하고 argmin이 계열 안에 있어야 함. 어긋나면 **계열을 넓히고 다시** — 이 규칙 자체가 테스트.

## 3. 인공물 통제 (하중을 받는 부분)

**셔플 바닥 — 측정된 자기-널.** `K = 20`회, 런 내부에서 후속자 짝짓기를 시드된 순열로 섞은(주변분포 보존, 시간 의존만 파괴) 데이터에 **동일한 파이프라인 전체**(같은 컷 계열, 같은 min)를 적용 → 셔플 min의 분포. **바닥 ≔ K개 셔플 min의 최댓값** (분포무관 ~95%, 고른 것이 아니라 그 예산·그 지지집합에서 잰 것). min 통계끼리 비교하므로 보정이 자기-일관적입니다.

**예산-수축 테스트 (`artefact-honesty`).** V2의 오차 감소가 `tests/test_phi_proxy.py`에 slow-마크로 고정되고 RESULTS에 곡선으로 기록됩니다. 추가로 널의 `Φ̂` 자체가 B0 → 4B0에서 반감 이상 수축하는지 기록 — 수축하지 않는 널 값은 발견이지 잡음이 아닙니다.

**폭-일치 널 배터리 (정확한 명세).**

| 폭 W | 양성 팔 | 같은 폭의 널 (동일 예산·컷 계열·셔플) |
|---|---|---|
| 8 | (없음 — 4쌍은 짝수라 잠금) | FEEDFORWARD(8) · SELF(8) · PAIRS(8, chain=0) · **짝수쌍+chain(8) = 잠금 널** |
| 10 | 5쌍 PAIRS+chain | FEEDFORWARD(10) · SELF(10) · PAIRS(10, chain=0) |
| 12 | (없음 — 6쌍 잠금) | 위와 동형 4종(12) |
| 14 | 7쌍 PAIRS+chain | 동형 3종(14) |
| 16·20 | (없음 — 잠금) | 잠금 널 + 동형 3종 (20은 비용 측정 후) |
| 18 | 9쌍 PAIRS+chain | 동형 3종(18) — 지지집합 2^9, 바닥이 신호를 덮는지가 여기서 판명 |

요건: 모든 널이 4B0에서 자기 바닥 아래(또는 B0 대비 반감), 양성 팔은 두 예산 모두에서 바닥 위 + 비반감. **{8, 12, 16, 20}이 양성 없는 널-전용 폭이라는 사실 자체가 이 배터리의 힘입니다** — 프록시가 폭이 넓다는 이유만으로 부풀면 이 폭들에서 즉시 드러납니다.

## 4. 평결 규칙

`RecurrenceEvidence`를 본뜬 `ProxyEvidence`:

```
held_by_proxy(W) ⟺
  (i)   Φ̂(B0) > floor(B0)  AND  Φ̂(4B0) > floor(4B0)      # floor = 동일-파이프라인 셔플 K=20의 max
  (ii)  Φ̂(4B0) > Φ̂(B0) / 2                                # `held` 규칙 그대로
  (iii) 같은 폭의 FEEDFORWARD·SELF·무체인 널 전부가 4B0에서 (i) 실패
  (iv)  지지집합 크기·엔트로피, argmin 컷, 전체 조건(W·wiring·chain·rhythm·tau·B·시드·컷 계열·K) 병기
```

**얻는 문장**: "폭 W에서 프록시-통합 분리 성립 — 컷-정보가 자기 셔플 바닥을 두 예산에서 넘고 반감하지 않았으며, 같은 폭·같은 예산의 세 널은 모두 바닥 아래였다 (조건: …). 측정 가능 벽이 6 → W로 이동했다 — 정확-Φ보다 약한, 프록시-강도의 주장으로서."

**금지 문장**: "폭 W에서 Φ = X" (크기 단독) · "프록시" 한정어 없는 "integrated" · 폭이 다른 판독끼리의 크기 비교 · 실제로 돌린 최대 W 너머로의 외삽("unbounded"류). `Φ̂`의 크기는 `directed_big_phi`의 비트와 같은 단위가 아니므로 나란히 적을 때도 항상 다른 이름으로 적습니다.

## 5. 단계별 첫 커밋

**커밋 1 — 순수 `state/` 측정 (src 무변경).** `state/phi_proxy/proxy.py` (src 엔진과 `iit4`를 *소비*만 함) + `state/phi_proxy/RESULTS.md` (런에서 채움: V1 표, V2 수렴 곡선, V3 대조, 널 배터리는 {8, 10, 12, 14}까지 — 18·20은 14에서 비용을 재고 기록한 뒤). 테스트 `tests/test_phi_proxy.py`: 해석적-TPM 정확-0, 소형계 MIP-컷 일치 2건, 계열-포함-MIP, W=4 예산-수축(slow). `default-stays-exact`는 자명하게 성립 — 엔진 파라미터 추가가 0건이고 `substrate.py`를 건드리지 않습니다(기존 골든·substrate 테스트 무손상이 핀).

**커밋 2 — 검증 통과 후 `src/` API.** `src/anima_reborn/phi_proxy.py`에 `phi_cut_proxy(...) -> ProxyReading`·`proxy_evidence(...) -> ProxyEvidence` (substrate의 자매 모듈; `MAX_UNITS` 캡은 정확-Φ의 것이므로 그대로 둠). "state의 스크립트는 사본이 아니라 출하된 엔진을 잰다" 규칙에 따라 `state/phi_proxy/proxy.py`를 출하 모듈의 드라이버로 재작성하고 **재측정을 별도 기록** (reports-are-evidence).

**연기**: `substrate.py` 판독에의 통합 · 뷰어 판독(프록시는 `step`/`reset` 엔진이 아니라 lockstep 의무는 없음 — 나중에 측정 패널로) · W=18/20 런 · 계층(부품 3)에서의 사용.

## 정직한 천장 — 미리 적어두는 것

프록시의 벽은 사라지는 게 아니라 이동합니다. (1) 닫힌 매크로-링 때문에 양성 팔은 홀수 쌍 폭에만 존재 — 다음 전선은 10, 그다음 14. (2) 표본 복잡도는 2^W가 아니라 **방문 지지집합(≈ 2^(W/2))과 조건 셀 점유**를 타고 오릅니다 — 셀이 얇아지면 셔플 바닥이 올라가고, 바닥이 신호를 덮는 첫 폭에서 평결은 정직하게 "보여지지 않음"입니다. (3) 프록시의 주장 범위는 **엔진의 방문 동역학 위에서의** 의존성입니다 — π가 닿지 않는 상태의 구조는 보이지 않으며, 문서에 그렇게 적습니다. 예상되는 정직한 결과물은 "벽이 6에서 10으로(어쩌면 14로) 이동했고, 여기 그 측정이 있다"이지 "임의 폭"이 아닙니다.

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
session id: 019f8e4d-328b-77a1-bc09-13f7814a3e96
--------
user
# Design task: a validated sampled directed-Φ proxy that raises the measurability ceiling honestly

Part 2 of the "engine parts toward the goal" plan (both of you converged last round;
`state/lab/2026-07-23-new-parts-*.md`). The long-term bottleneck is not raw capacity — PAIRS
gives units/2 bits — but MEASURABILITY: directed Φ (integrated information) is exact only to
~6 units, because it enumerates 2^N states and all bipartitions, so wider integrated
substrates cannot be SHOWN to be one integrated thing. Design the component that raises that
ceiling honestly. Return a concrete, implementable design + validation protocol. Do NOT write
full code.

## The repo you are extending (read it)

- `iit4/` — exact directed IIT 4.0 (`directed_big_phi`), bit-exact against its hexa origin. This
  is ground truth where it is computable (≤ ~6 units).
- `src/anima_reborn/substrate.py` — drives an engine from EVERY state → a MEASURED transition
  matrix (TPM) → directed Φ. `RECURRENCE_FLOOR` was calibrated at 4 units and does NOT transfer
  (the estimator artefact grows with width, so past 6 units the verdict is "held under 4x
  sampling", never the magnitude).
- `src/anima_reborn/coupled.py` — `CoupledEngine`, `Wiring` (RING / PAIRS / FEEDFORWARD / SELF),
  `chain`. Odd-count PAIRS + weak `chain` stays integrated; even pairs macro-lock; FEEDFORWARD
  and SELF are reducible (Φ ≈ 0) AT ANY WIDTH — these are the per-width nulls.
- Prior results (`state/communication/capacity.py`, `RESULTS.md`): 6 units / 3 pairs measured
  integrated (directed Φ held under 4x sampling where the disjoint null collapses). Past 6 units,
  exact Φ is intractable.

## The two things a proxy samples, and the danger

Exact Φ = min over bipartitions of the integration lost by that cut, over the full state space.
Two axes to sample:
1. **State space** — instead of all 2^N states, the empirical TPM over the states a seeded run
   actually visits (the extension of `substrate.py`'s "measured matrix" philosophy).
2. **Partition space** — instead of all bipartitions, a set of structural cuts (every pair
   boundary, every chain cut) plus N random balanced bipartitions, taking the min.

**The danger is directional and must be controlled**: cut-sampling can MISS the true
minimum-information partition (MIP), and missing it makes Φ look BIGGER — an estimator that errs
toward OVERCLAIM. State-sampling bias in MI estimation ALSO errs upward (the finite-sample MI
bias). So a naive proxy inflates Φ and fakes integration. Every design choice must fight this.

## What I need — answer each explicitly

1. **The exact proxy definition.** The sampling scheme for state space and partition space, how
   the min is taken, and the estimator (exact categorical MI on the visited-state TPM? a bias
   correction?). Be specific enough to implement without further choices.
2. **Validation against ground truth.** The protocol that pins the proxy to exact `iit4` where
   both are computable (units 2..6): must MATCH within a stated tolerance, AND the sampled-cut
   min must coincide with the exact MIP cut on small systems (or the cut family is widened until
   it does). A test fixes this.
3. **The artefact control (the load-bearing one).** How you PROVE the proxy is not just inflating:
   (a) the error vs exact must SHRINK as the sampling budget grows (recorded in docs AND a test —
   `artefact-honesty`); (b) the per-width nulls — FEEDFORWARD, SELF, even-pairs macro-lock,
   constructible at ANY width (8, 12, 20) — must sit at ~0 / collapse under the SAME budget while
   odd-PAIRS+chain holds. State the exact null battery and the widths.
4. **The verdict rule.** Given that magnitude does not transfer, the honest verdict past 6 units
   must be "separation from its own width-matched null, held as the budget grows" — never a bare
   number. Write the exact rule and the sentence it earns (and the sentence it must NOT).
5. **The phased first commit.** The smallest honest thing: is it a pure `state/` measurement
   (`phi_proxy.py` validating the estimator + the width nulls, filling RESULTS from the run) with
   the `src/` API following once validated — matching how every capability here landed? What is
   deferred (e.g. wiring the proxy into `substrate.py`; a viewer readout).

Keep the discipline: never a number that was not measured; the estimator's bias direction is
toward overclaim, so the controls that matter are the exact-match window, the budget-shrink test,
and the width-matched nulls; report separation, not magnitude; if a wider substrate cannot be
shown integrated even by the proxy, say so — the honest deliverable may be "the wall moved from 6
to N units, and here is the measured N", not "unbounded".

codex
I’m going to inspect the exact IIT implementation, substrate measurement path, coupled wiring semantics, and the prior “new parts” notes before fixing the proxy definition. I’ll keep this as a design/validation protocol—no implementation and no invented results.
exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g 'state/lab/2026-07-23-new-parts-*.md' -g 'iit4/**' -g 'src/anima_reborn/substrate.py' -g 'src/anima_reborn/coupled.py' -g 'state/communication/capacity.py' -g 'RESULTS.md' | sed -n '1,240p'" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
/Users/mini/dancinlab/anima-reborn
src/anima_reborn/coupled.py
src/anima_reborn/substrate.py
state/communication/RESULTS.md
state/communication/capacity.py
state/coupling/RESULTS.md
state/lab/2026-07-23-new-parts-both.md
state/lab/2026-07-23-new-parts-prompt.md

exec
/bin/zsh -lc "find .. -name AGENTS.md -print && find . -maxdepth 3 -type d -name 'iit4' -print && sed -n '1,260p' state/lab/2026-07-23-new-parts-both.md && sed -n '1,220p' state/lab/2026-07-23-new-parts-prompt.md" in /Users/mini/dancinlab/anima-reborn
 succeeded in 31332ms:
../traffic/apps/vpnguide/AGENTS.md
../traffic/apps/fanguide/AGENTS.md
../traffic/apps/marketinghub/AGENTS.md
../vpnguide/AGENTS.md
../bio/AGENTS.md
../fanguide-cta/AGENTS.md
../cake-wallet/AGENTS.md
../framely/AGENTS.md
../amen/web/node_modules/@elevenlabs/elevenlabs-js/AGENTS.md
../amen/web/AGENTS.md
../vibehandbook-cta/AGENTS.md
../vpnguide-cta/AGENTS.md
../vibehandbook/AGENTS.md
../.wt/hexa-nil/AGENTS.md
../.wt/axis1-b2crypto/AGENTS.md
../.wt/axis1-b1term/AGENTS.md
../void/macos/AGENTS.md
../void/test/fuzz-libvoid/AGENTS.md
../void/example/AGENTS.md
../void/zig-pkg/.tmp-0e1142a531a64c19/uucode-0.2.0/AGENTS.md
../void/src/benchmark/AGENTS.md
../void/src/inspector/AGENTS.md
../void/src/terminal/c/AGENTS.md
../fanguide/AGENTS.md
../marketinghub/AGENTS.md
../coinbypass-app-edgegigs-cta/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a122d4c0a0cd1aaaf/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a935b42fda361e404/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a4f533b4783ec4a21/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a32498fbede3bb55e/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a69cba889d5c962ab/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a6589bda67ff2a042/AGENTS.md
../hexa-matter/.claude/worktrees/agent-abf20e3a078edd3ec/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a1f84438ce4dd1831/AGENTS.md
../hexa-matter/.claude/worktrees/agent-aad5e9305d6396b0d/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a319bdb0f4512e935/AGENTS.md
../hexa-matter/.claude/worktrees/agent-adb4be5941b2403d0/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a6872eaf7400e403e/AGENTS.md
../hexa-matter/.claude/worktrees/agent-aeeca08e533140a2b/AGENTS.md
../hexa-matter/.claude/worktrees/agent-ab94a9c66d4d7094b/AGENTS.md
../hexa-matter/.claude/worktrees/agent-ae33eb98e7906a0f5/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a8be97b0135756727/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a6049e5866e7d0ecb/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a202902c495133306/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a14f510a267008d1c/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a393825b6ecf0566c/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a32edf4854dcde885/AGENTS.md
../hexa-matter/.claude/worktrees/agent-ab3f83d1464651f4c/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a1ae09d05d9c70d56/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a7acffb530dc55154/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a912a853463202f50/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a3d7485a4ae123524/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a860793f927c20cd9/AGENTS.md
../hexa-matter/.claude/worktrees/agent-ad05bcd7846924fce/AGENTS.md
../hexa-matter/.claude/worktrees/agent-acf1c0624cb8cbd23/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a2ef4f8d14df358a2/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a4c29e65eea7d9080/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a97d51506a5058624/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a2a8b633810e20fe6/AGENTS.md
../hexa-matter/.claude/worktrees/agent-a075bea98e28a8649/AGENTS.md
../hexa-matter/AGENTS.md
../marketinghub-cta/AGENTS.md
../demiurge/web/.next/standalone/web/AGENTS.md
../demiurge/web/.next/standalone/.claude/worktrees/agent-acc4ec45a7356041b/web/AGENTS.md
../demiurge/web/.next/standalone/.claude/worktrees/agent-acc25680c38d13c7d/web/AGENTS.md
../demiurge/web/.next/standalone/.claude/worktrees/agent-ab94f11664a475116/web/AGENTS.md
../demiurge/web/AGENTS.md
../demiurge/hexa-matter-archive/AGENTS.md
../atlas/AGENTS.md
../coinbypass-app/.claude/worktrees/landing-rewrite/AGENTS.md
../coinbypass-app/AGENTS.md
../archive-nexus/AGENTS.md
../hexa-lang/.worktrees/l4-rider/AGENTS.md
../hexa-lang/.worktrees/l4-bind-hook/AGENTS.md
../hexa-lang/.worktrees/ownlinkflip/AGENTS.md
../hexa-lang/.worktrees/l3-strftime/AGENTS.md
../hexa-lang/.worktrees/stager-fix/AGENTS.md
../hexa-lang/AGENTS.md
../mem/AGENTS.md
./src/anima_reborn/iit4
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
The prior notes agree on the component but leave a crucial ambiguity: “empirical TPM over visited states” cannot simply be passed to IIT as though unvisited states vanished. I’m checking the exact `directed_big_phi` input semantics and existing sampling conventions now, because that determines whether the proxy is a defensible approximation or a different statistic.
exec
/bin/zsh -lc "sed -n '1,260p' CLAUDE.md; sed -n '1,260p' src/anima_reborn/CLAUDE.md; sed -n '1,260p' src/anima_reborn/iit4/CLAUDE.md; sed -n '1,320p' src/anima_reborn/substrate.py; sed -n '1,360p' src/anima_reborn/coupled.py" in /Users/mini/dancinlab/anima-reborn
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
| `sequence.py` | `SequenceEngine`, the shift chain the `기억` tab drives — K proven 3-bit cells hold the last K symbols IN ORDER (time accumulation); per-cell integration, the inter-cell bridge a TRANSPORT claim only; `deaf_bridge=` is the null (default off, bit-identical). Measured by `state/communication/accumulation.py` | (new — not in the origin) |

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

exec
/bin/zsh -lc "sed -n '1,360p' src/anima_reborn/substrate.py; sed -n '300,620p' src/anima_reborn/coupled.py; sed -n '1,320p' src/anima_reborn/iit4/directed.py; sed -n '1,360p' src/anima_reborn/iit4/bigphi.py; sed -n '1,300p' src/anima_reborn/iit4/tpm.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
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
"""Directed system cuts — telling a loop apart from a chain.

`bigphi.big_phi` cuts a system in two and removes everything crossing the
divide, in both directions at once. That is the scheme inherited from the hexa
origin, and it has a consequence worth stating plainly: **it cannot see that a
feedforward system is reducible.** Measured on a four-unit chain where unit 0 is
exogenous and each later unit reads only the one before it, the undirected
measure reports 1.27 bits and does not shrink with more trials — where IIT 4.0
says zero, because nothing flows back.

A directed cut severs influence one way and leaves the other intact. Under a cut
that stops A from reaching B:

    a distinction survives unless its mechanism sits in A and its effect
    purview reaches into B (its prediction crossed the cut), or its cause
    purview sits in A and its mechanism in B (its memory crossed it)

and Phi is again the least damage any cut does. For the chain that minimum is
exactly zero, and for the right reason: cutting *into* the exogenous unit costs
nothing, because nothing was flowing that way. For a ring no direction is free —
measured, the cheapest directed cut still destroys 10.02 of 13.61 bits.

This lives beside `big_phi` rather than replacing it. The undirected measure is
bit-exact against the hexa engine and eleven golden cases depend on that; a
carve-out gets closed in the open, with both numbers available, not by quietly
changing what the old name means.

    from anima_reborn.iit4 import big_phi, directed_big_phi

    big_phi(chain, state).phi           # 1.27 — cannot see the reducibility
    directed_big_phi(chain, state).phi  # 0.00 — can

**The trap this could have fallen into.** A directed measure searches twice as
many cuts, so its minimum is always at most the undirected one — a lower number
is guaranteed by construction and proves nothing. What makes the zero real is
that the ring stays high through the same code, and that the winning cut on the
chain is identifiably the one pointing at the exogenous unit. Both are tests.

What this does not do: close the other inherited carve-outs. Partitions are
still all bipartitions of mechanism-and-purview, relations are still
second-order, and nothing is calibrated against PyPhi. See `iit4/CLAUDE.md`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .relation import PhiStructure, phi_structure
from .tpm import TransitionMatrix

__all__ = ["DirectedCut", "DirectedPhi", "directed_big_phi"]


@dataclass(frozen=True, slots=True)
class DirectedCut:
    """One direction of one bipartition: `source` stops reaching `sink`."""

    source: int
    """Units whose outgoing influence is severed."""
    sink: int
    """Units that stop hearing from `source`. The reverse direction survives."""

    def severs(self, mechanism: int, cause: int, effect: int) -> bool:
        """Whether this cut breaks a distinction.

        Two ways it can: the mechanism predicts across the cut, or it remembers
        across it. Either is a dependence the cut has removed.
        """
        predicts_across = bool(mechanism & self.source and effect & self.sink)
        remembers_across = bool(cause & self.source and mechanism & self.sink)
        return predicts_across or remembers_across

    def __str__(self) -> str:
        return f"{self.source:b} -/-> {self.sink:b}"


@dataclass(frozen=True, slots=True)
class DirectedPhi:
    """What the least damaging *directed* cut still destroys."""

    phi: float
    """Bits. Zero means some direction can be severed for free — the system is
    reducible in the sense IIT 4.0 means."""
    structure: PhiStructure
    cut: DirectedCut | None
    """The minimum-information directed partition, or None for a system too
    small to cut."""

    @property
    def is_recurrent(self) -> bool:
        """No direction is free, so influence must return. This is the claim the
        undirected measure could not make."""
        return self.phi > 0.0

    @property
    def total(self) -> float:
        return self.structure.total

    def __str__(self) -> str:
        verdict = "recurrent" if self.is_recurrent else "reducible"
        return (
            f"directed-phi={self.phi:.6f} of total={self.total:.6f} "
            f"[{verdict}] cut={self.cut}"
        )


def directed_big_phi(matrix: TransitionMatrix, state: int) -> DirectedPhi:
    """Measure irreducibility against directed cuts.

    Every bipartition is tried in both directions; unit 0 is pinned to one side
    so each directed cut is visited exactly once. Cost is twice `big_phi`'s cut
    loop, which is not where the expense lives — the distinction search above it
    dominates.
    """
    structure = phi_structure(matrix, state)
    found = structure.distinctions

    if matrix.n < 2:
        return DirectedPhi(phi=0.0, structure=structure, cut=None)

    all_units = (1 << matrix.n) - 1
    best_loss = float("inf")
    best_cut: DirectedCut | None = None

    for left in range(1, all_units):
        if not left & 1:
            # Unit 0 pinned left, so each unordered split is enumerated once
            # and both of its directions are tried below.
            continue
        right = all_units & ~left

        for cut in (DirectedCut(left, right), DirectedCut(right, left)):
            # Accumulate what the cut DESTROYS rather than what survives, and
            # subtract nothing. A cut that severs nothing then costs exactly
            # 0.0, where `total - survived` would leave float residue on the
            # order of 1e-16 and turn "reducible" into "almost reducible".
            lost = 0.0
            alive: dict[int, bool] = {}
            for distinction in found:
                intact = not cut.severs(
                    distinction.mechanism,
                    distinction.cause.purview,
                    distinction.effect.purview,
                )
                alive[distinction.mechanism] = intact
                if not intact:
                    lost += distinction.phi

            for relation in structure.relations:
                if not (alive[relation.left] and alive[relation.right]):
                    lost += relation.phi

            if lost < best_loss:
                best_loss, best_cut = lost, cut

    if best_loss == float("inf"):
        best_loss = 0.0
    return DirectedPhi(phi=max(0.0, best_loss), structure=structure, cut=best_cut)
"""M4 — system big-Phi: what the kindest cut still destroys.

Cut the system in two. A distinction survives only if everything it involves —
its mechanism and both purviews — lands on one side; a distinction that reaches
across the cut depended on a connection that is now gone. A relation survives
only if both its distinctions survive *on the same side*.

    loss(cut) = total - (what survived it)
    big-Phi   = min over cuts of loss(cut)

So big-Phi is what the *least damaging* cut still costs. Above zero means no
cut is free: the system is irreducible, a whole rather than parts that happen to
sit together. Exactly zero means some partition splits it losslessly, and the
system was never one thing.

Only the cuts with unit 0 on the left are enumerated, since a cut and its mirror
are the same cut.

Carve-out, stated plainly: irreducibility is measured as structure destroyed by
the cut. IIT 4.0 proper rebuilds the cause-effect structure on the partitioned
matrix and applies a normalization; the origin flags that gap as unfinished
calibration work, and this port carries the gap over rather than papering it.
By construction big-Phi lands in [0, total].

Ported from `dancinlab/selfhost-work` `stdlib/consciousness/iit4_bigphi.hexa`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .distinction import Distinction
from .relation import PhiStructure, phi_structure
from .tpm import TransitionMatrix

__all__ = ["SystemPhi", "big_phi", "side_of"]

SPANS = 0
"""The distinction reaches across the cut and does not survive it."""


def side_of(distinction: Distinction, left_mask: int, n: int) -> int:
    """Which side of a cut a distinction lies on: 1 left, 2 right, 0 spanning.

    Origin: `iit4_distinction_side`.
    """
    in_left = False
    in_right = False
    for unit in range(n):
        if distinction.involves(unit):
            if left_mask >> unit & 1:
                in_left = True
            else:
                in_right = True
    if in_left and in_right:
        return SPANS
    return 1 if in_left else 2


@dataclass(frozen=True, slots=True)
class SystemPhi:
    """The verdict on one system in one state."""

    phi: float
    """big-Phi, in bits. Zero means reducible — some cut costs nothing."""
    structure: PhiStructure
    cut: int
    """Left side of the minimum-information partition, as a unit bitmask. Zero
    when no cut was evaluated (a system of one unit)."""

    @property
    def is_irreducible(self) -> bool:
        """Whether the system holds together as one thing."""
        return self.phi > 0.0

    @property
    def total(self) -> float:
        return self.structure.total

    def __str__(self) -> str:
        verdict = "irreducible" if self.is_irreducible else "reducible"
        return (
            f"big-phi={self.phi:.6f} of total={self.total:.6f} "
            f"[{verdict}] cut={self.cut:b}"
        )


def big_phi(matrix: TransitionMatrix, system_state: int) -> SystemPhi:
    """Measure a system's irreducibility in a given state.

    Cost grows steeply: every mechanism searches every purview over every
    partition, so this is exponential in `n` several times over. n <= 5 is the
    practical ceiling.
    """
    structure = phi_structure(matrix, system_state)
    found = structure.distinctions
    total = structure.total

    if matrix.n < 2:
        # There is nothing to cut, so nothing can be lost.
        return SystemPhi(phi=0.0, structure=structure, cut=0)

    all_units = (1 << matrix.n) - 1
    best_loss = float("inf")
    best_cut = 0

    for left in range(1, all_units):
        if not left & 1:
            # Unit 0 pinned left, so each unordered cut is visited once.
            continue

        sides = [side_of(d, left, matrix.n) for d in found]
        survived = sum(d.phi for d, side in zip(found, sides) if side != SPANS)

        by_mechanism = {d.mechanism: side for d, side in zip(found, sides)}
        for relation in structure.relations:
            left_side = by_mechanism[relation.left]
            right_side = by_mechanism[relation.right]
            if left_side != SPANS and left_side == right_side:
                survived += relation.phi

        loss = total - survived
        if loss < best_loss:
            best_loss, best_cut = loss, left

    if best_loss == float("inf"):
        best_loss = 0.0
    return SystemPhi(phi=max(0.0, best_loss), structure=structure, cut=best_cut)
"""M1 — the transition matrix, the repertoires, and intrinsic difference.

Everything above this module is built from three ideas defined here.

**The transition matrix.** A system of `n` binary units is described by
`P(unit is ON next | the whole system is in state s)`. IIT 4.0 assumes the units
update conditionally independently given the current state, so one probability
per (state, unit) pair is enough — a state-by-node matrix rather than a full
2^n x 2^n joint.

**The repertoires.** Fix a *mechanism* (a subset of units, in its current state)
and ask what it says about a *purview* (another subset).

    effect repertoire  p(purview next  | mechanism now)  — what it predicts
    cause  repertoire  p(purview before | mechanism now)  — what it remembers

Units outside the constraint are averaged over uniformly, which is IIT's way of
saying "assume nothing about them". The cause direction is Bayes with a uniform
prior over the past.

**Intrinsic difference.** IIT 4.0's break from 3.0. Instead of summing a
divergence over all states, take the single largest pointwise term:

    ID(p || q) = max_x  p(x) * log2( p(x) / q(x) )

The maximizing `x` is the state the mechanism *specifies* — a distinction is
about one particular state, not a spread over all of them. Ties go to the lowest
index, which is what makes a run reproducible.

Ported from `dancinlab/selfhost-work` `stdlib/consciousness/iit4_tpm.hexa`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from collections.abc import Sequence

__all__ = [
    "TransitionMatrix",
    "IntrinsicDifference",
    "intrinsic_difference",
    "units_of",
    "expand",
    "compact_index",
]

_LN2 = math.log(2.0)
"""log2 is computed as `(log p - log q) / log 2` rather than with `math.log2`.
The two differ in the last bits, and the origin used this form — since intrinsic
difference is an argmax, a changed last bit can move the specified state."""

Q_SMOOTHING = 1.0e-10
"""Added to the reference distribution so a zero there is a large finite ratio
rather than an infinity. Origin: iit4_tpm.hexa:232."""

P_FLOOR = 1.0e-12
"""Below this a probability contributes nothing: p*log(p) -> 0 as p -> 0."""


def units_of(mask: int, n: int) -> tuple[int, ...]:
    """The unit indices set in `mask`, ascending. Origin: `iit4_units`."""
    return tuple(i for i in range(n) if mask >> i & 1)


def expand(compact: int, units: Sequence[int]) -> int:
    """Lift a purview-local state onto absolute unit positions.

    Bit `b` of `compact` is the state of `units[b]`. Origin: `iit4_expand`.
    """
    absolute = 0
    for bit, unit in enumerate(units):
        if compact >> bit & 1:
            absolute |= 1 << unit
    return absolute


def compact_index(absolute: int, units: Sequence[int]) -> int:
    """The inverse of `expand`. Origin: `iit4_compact_index`."""
    index = 0
    for bit, unit in enumerate(units):
        if absolute >> unit & 1:
            index |= 1 << bit
    return index


@dataclass(frozen=True, slots=True)
class IntrinsicDifference:
    """The largest pointwise divergence term, and where it occurred."""

    value: float
    """In bits. Zero or negative means the mechanism says nothing beyond the
    reference."""
    state: int
    """The purview state the mechanism specifies — the argmax, ties to the
    lowest index."""


def intrinsic_difference(
    p: Sequence[float], q: Sequence[float]
) -> IntrinsicDifference:
    """max_x p(x) log2(p(x)/q(x)). Origin: `intrinsic_difference`."""
    best_value = -1.0e308
    best_state = 0
    for state, px in enumerate(p):
        term = 0.0
        if px > P_FLOOR:
            term = px * (math.log(px) - math.log(q[state] + Q_SMOOTHING)) / _LN2
        if term > best_value:  # strict: the first maximizer keeps the slot
            best_value = term
            best_state = state
    return IntrinsicDifference(value=best_value, state=best_state)


class TransitionMatrix:
    """A state-by-node transition matrix over `n` binary units.

    `probability(state, unit)` is P(unit is ON at t+1 | system state is `state`
    at t). A state encodes unit `i` in bit `i`, 0 for OFF and 1 for ON.

    Marginals are memoized. Every measurement above this module asks for the
    same marginals over and over — the same purview under the same constraint
    recurs across partitions, mechanisms and subsystems — and the cache is what
    makes anything past n = 3 finish. It changes no result: `marginal_on` is a
    pure function of the matrix, which never changes after construction.
    """

    __slots__ = ("n", "_values", "_states", "_cache")

    def __init__(self, values: Sequence[float], n: int) -> None:
        """Build from a flat row-major sequence, `values[state * n + unit]`."""
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n}")
        states = 1 << n
        if len(values) != states * n:
            raise ValueError(
                f"a {n}-unit matrix needs {states * n} entries, got {len(values)}"
            )
        for i, v in enumerate(values):
            if not 0.0 <= v <= 1.0:
                raise ValueError(
                    f"entry {i} is {v}; every entry is a probability in [0, 1]"
                )
        self.n = n
        self._states = states
        self._values = tuple(float(v) for v in values)
        self._cache: dict[tuple[int, int, int], float] = {}

    @classmethod
    def from_rows(cls, rows: Sequence[Sequence[float]]) -> TransitionMatrix:
        """Build from one row per state: `rows[state][unit]`."""
        if not rows:
            raise ValueError("need at least one row")
        n = len(rows[0])
        if any(len(row) != n for row in rows):
            raise ValueError("every row must name the same units")
        if len(rows) != 1 << n:
            raise ValueError(
                f"{n} units need {1 << n} rows, got {len(rows)}"
            )
        return cls([v for row in rows for v in row], n)

    @property
    def states(self) -> int:
        """How many system states there are — 2^n."""
        return self._states

    @property
    def values(self) -> tuple[float, ...]:
        return self._values

    def probability(self, state: int, unit: int) -> float:
        """P(unit ON at t+1 | system in `state`). Origin: `tpm_on`."""
        return self._values[state * self.n + unit]

    def marginal_on(self, fix_mask: int, fix_state: int, target: int) -> float:
        """P(target ON next), averaging over every unit not in `fix_mask`.

        The units named by `fix_mask` are pinned to their values in `fix_state`;
        the rest are averaged with equal weight, which is IIT's maximum-entropy
        way of declining to assume anything about them. `fix_mask = 0` gives the
        unconstrained marginal. Origin: `iit4_marginal_on`.
        """
        # Only the low n bits name real units, and only the pinned bits of
        # `fix_state` matter — normalizing both keeps the cache from splitting
        # one marginal across several keys, and matches the origin, which
        # compares bit by bit over [0, n) alone.
        fix_mask &= self._states - 1
        pinned = fix_state & fix_mask
        key = (fix_mask, pinned, target)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        total = 0.0
        count = 0
        for state in range(self._states):
            if state & fix_mask == pinned:
                total += self._values[state * self.n + target]
                count += 1
        result = total / count if count else 0.0
        self._cache[key] = result
        return result

    def effect_repertoire(
        self, mechanism: int, mechanism_state: int, purview: int
    ) -> tuple[float, ...]:
        """What the mechanism says the purview will be. Origin:
        `effect_repertoire`."""
        units = units_of(purview, self.n)
        on = [
            self.marginal_on(mechanism, mechanism_state, unit) for unit in units
        ]
        return _product_distribution(on)

    def cause_repertoire(
        self, mechanism: int, mechanism_state: int, purview: int
    ) -> tuple[float, ...]:
        """What the mechanism says the purview was.

        Bayes with a uniform prior: for each candidate past purview state, how
        likely was it to leave the mechanism in the state it is now.
        Origin: `cause_repertoire`.
        """
        purview_units = units_of(purview, self.n)
        mechanism_units = units_of(mechanism, self.n)
        count = 1 << len(purview_units)

        likelihood = []
        total = 0.0
        for compact in range(count):
            past = expand(compact, purview_units)
            weight = 1.0
            for unit in mechanism_units:
                on = self.marginal_on(purview, past, unit)
                weight *= on if mechanism_state >> unit & 1 else 1.0 - on
            likelihood.append(weight)
            total += weight

        if total <= 0.0:
            # Nothing could have produced this state. Uniform is the honest
            # answer: the mechanism singles out no past at all.
            return (1.0 / count,) * count
        return tuple(w / total for w in likelihood)

    def unconstrained_effect(self, purview: int) -> tuple[float, ...]:
        """The purview's own marginal, with no mechanism constraining it."""
        return self.effect_repertoire(0, 0, purview)

    def unconstrained_cause(self, purview: int) -> tuple[float, ...]:
        """Uniform — the prior over the past, before any mechanism speaks."""
        count = 1 << len(units_of(purview, self.n))
        return (1.0 / count,) * count

    def __repr__(self) -> str:
        return f"TransitionMatrix(n={self.n}, states={self._states})"


def _product_distribution(on: Sequence[float]) -> tuple[float, ...]:
    """Joint over independent binary units from their ON probabilities."""
    count = 1 << len(on)
    out = []
    for compact in range(count):
        probability = 1.0
        for bit, p in enumerate(on):
            probability *= p if compact >> bit & 1 else 1.0 - p
        out.append(probability)
    return tuple(out)

exec
/bin/zsh -lc "sed -n '200,520p' src/anima_reborn/substrate.py; sed -n '1,360p' state/communication/capacity.py; sed -n '1,320p' state/communication/RESULTS.md; rg -n \"recurrence|trials|4x|PAIRS|macro|chain|directed\" tests state/communication/capacity.py src/anima_reborn/substrate.py | sed -n '1,320p'" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
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
# 소통을 위해 엔진에 무엇이 필요한가 — 첫 측정

2026-07-22 · 재현 스크립트 `state/communication/integration_vs_representation.py`
(실행: 저장소 루트에서 `PYTHONPATH=src python state/communication/integration_vs_representation.py`)

"소통하려면 엔진에 뭐가 필요한가"를 발산 위임하면서, 가장 값싸게 검증 가능한 씨앗
하나를 먼저 직접 쟀다. 씨앗은 죽었고, 죽는 과정에서 **더 쓸모 있는 것**이 나왔다.

## 씨앗: 양상 불변성 — 반증됨

"같은 개념이 서로 무관한 두 인코딩으로 들어와도 기판이 같은 곳으로 간다면, 기판은
인코딩이 아니라 **개념**을 붙잡은 것이다." 결합 0.5에서 측정:

| | 거리 |
| --- | ---: |
| 같은 단어 · 서로 무관한 두 인코딩 | 0.523 |
| 다른 단어 · 같은 인코딩 | 0.337 |

**앞이 더 크다.** 즉 기판이 가는 곳을 정하는 건 단어가 아니라 **인코딩**이다. 저장소가
이미 문서에 적어둔 것(`words.py`: "인코딩이 절대값을 결정한다")이 끌개 수준에서도 그대로다.

입력 **순서**를 100% 보존하는 단조변환 인코딩을 써도 종착점 순서 일치는 0%였다. 뭔가 더
근본적인 문제가 있다는 신호였다.

## 그래서 나온 것: 통합과 표상은 이 구조에서 정면으로 충돌한다

원인을 쫓다 보니 씨앗의 실패보다 중요한 게 나왔다. **고리 자신의 끌개가 입력을 덮는다.**

두 양을 같은 엔진에서 λ(각 유닛 목표 중 살아 있는 상대의 비중)만 바꿔가며 쟀다.

- **표상 비율** = 서로 다른 단어들이 만드는 종착점 퍼짐 ÷ 같은 단어가 잡음만으로 만드는
  퍼짐. 3을 넘어야 "입력이 결과에 보인다"고 할 수 있다.
- **통합** = 방향성 Φ. 기준선 1.0 (`substrate.RECURRENCE_FLOOR`, 결합 없는 귀무 대비 측정값).

| λ | 방향성 Φ | 표상 비율 | 둘 다? |
| ---: | ---: | ---: | --- |
| 0.0 | 0.000 | **8.41** | 통합 없음 |
| 0.1 | 0.001 | 6.83 | 통합 없음 |
| 0.2 | 0.012 | 4.86 | 통합 없음 |
| 0.3 | 0.157 | 2.71 | 통합 없음 |
| 0.4 | 0.591 | 0.69 | 통합 없음 |
| 0.5 | **1.024** | 0.38 | 표상 묻힘 |
| 0.7 | **11.393** | 0.12 | 표상 묻힘 |

**둘 다 되는 창이 없다.** 단조롭게 반비례하고, 교차하는 구간(λ≈0.4)에서는 **둘 다 부족**하다
— Φ 0.59는 기준선 아래, 표상 0.69는 잡음 수준.

## 이게 왜 소통 질문의 답인가

소통하려면 **두 가지가 동시에** 필요하다. 하나여야 하고(통합 — 그래야 "누가" 이해한다),
무언가에 **대한** 것이어야 한다(표상 — 그래야 "무엇을" 이해한다).

지금 구조는 **둘을 동시에 줄 수 없다.** 통합되는 순간 자기 끌개에 갇혀 들은 것을 표상하지
못하고, 표상하는 순간 통합이 없다.

따라서 소통을 향한 어떤 설계든 **이 상충을 깨는 것**이 첫 관문이다. 상충의 기전도 이름이
붙었다 — 고리의 끌개가 구동을 압도한다. 이걸 깨려면 최소한 이런 게 필요해 보인다:

- 끌개가 **하나가 아니라 여럿**이어서 입력이 어느 골짜기로 갈지 고르게 하거나,
- 결합이 **고정이 아니라 가변**이어서 들을 때와 통합할 때가 나뉘거나,
- 표상이 **끌개의 위치가 아니라 궤적/시간구조**에 실리거나 (결정의 잠금이 시간에 질서를
  실었던 것처럼)

셋 다 아직 측정하지 않았다. 여기 적는 이유는 **다음에 잴 것**이기 때문이지, 답이라서가 아니다.

## 한계

- 4유닛 · τ=17 · 문턱 0 · 특정 어휘 8단어에서의 측정이다. 상충의 **방향**은 λ 전 구간에서
  단조롭지만, 정확한 교차점은 이 조건들에 딸린 값이다.
- 표상 비율의 기준 3.0은 잡음 대비 배수로 고른 값이지 귀무에서 유도한 값이 아니다. 통합
  기준선(1.0)과 달리 이건 **측정으로 정한 문턱이 아니다** — 쓸 때 그렇게 취급할 것.

---

## 벽을 깨는 후보 측정 — 시간 다중화 (2026-07-22)

발산 위임이 도는 동안, 위에 "다음에 잴 것"으로 적어둔 세 후보 중 가장 값싼 것을 쟀다.
재현 스크립트 `state/communication/alternating_coupling.py`.

**착상**: 결합을 고정하지 말고 **켜고 끈다**. 꺼져 있을 때 듣고(표상), 켜져 있을 때
통합한다. 표상은 종착 위치가 아니라 **궤적**(최근 구간의 평균 + 변동)에서 읽는다 —
세 번째 후보를 접어 넣은 것이다.

거대걸음을 듣기·통합 한 주기가 온전히 들어가게 맞추고, 고정 대조군도 같은 폭을 쓴다.

| 구성 | 방향성 Φ | 표상(궤적) |
| --- | ---: | ---: |
| **교대 10/10** | **2.143** | **4.03** |
| 고정 0.35 (교대와 시간평균 동일) | 1.176 | 3.27 |
| 고정 0.50 | 7.268 | 0.32 |
| 고정 0.70 | 10.641 | 0.13 |
| **교대 20/20** | **14.586** | **3.49** |

### 살아남는 표현과 살아남지 못하는 표현

**살아남지 못함**: "교대는 두 기준을 동시에 넘는다." 넘기는 하지만 기준 3.0 은 내가
잡음 배수로 고른 값이고, 어휘 크기에 따라 고정 0.35 도 넘는다. 문턱 하나로 승부를
가르면 문턱을 고른 사람이 이긴다.

**살아남음**: **같은 수준의 통합에서 교대가 표상을 지킨다.** 고정 0.70 은 Φ 10.6 에
표상 0.13, 교대 20/20 은 **더 높은** Φ 14.6 에 표상 3.49 — **27배**. 이건 문턱과
무관하고, 어휘·시드를 바꿔도 방향이 뒤집히지 않았다.

> ⛔ **이 문단의 "더 높은 Φ" 는 틀렸다. 아래 「정정 ③」 참조 (2026-07-22, 같은 날 늦게).**
> 위 표의 교대 20/20 은 τ=40, 고정 0.70 은 τ=20 이다. Φ 는 τ 만으로도 오르므로 두 행을
> 맞대는 것은 비교가 아니다. 표상 27배는 남고, "더 높은 Φ 에서" 는 남지 않는다.

**결정적 대조군**: 고정 0.35 는 교대 10/10 과 **시간평균 결합이 같다**. 효과가 "평균
결합이 얼마냐"였다면 이 대조군이 재현했어야 하는데, Φ 도 표상도 더 낮다. 즉 작동하는
것은 평균이 아니라 **교대 자체**다.

### 왜 이게 소통 질문에 걸리는가

벽은 "통합되는 순간 자기 끌개에 갇혀 들은 것을 표상하지 못한다" 였다. 시간 다중화는
그 갇힘을 **시간으로 나눈다** — 끌개에 갇히는 구간과 바깥을 듣는 구간을 번갈아 두어,
한 주기 전체로 보면 둘 다 성립한다. 결정의 잠금이 질서를 **공간이 아니라 시간**에
실었던 것과 같은 수법이다.

### 아직 아닌 것

- 이건 **벽이 깨질 수 있다**는 증거이지, 소통이 된다는 증거가 아니다. 표상이 살아
  있다는 것과 그 표상이 **개념**이라는 것은 다른 주장이고, 양상 불변성은 여전히
  반증된 채다.
- 나머지 두 후보(끌개를 여럿으로 · 표상을 순수 시간구조에)는 아직 안 쟀다.
- 교대 주기 10/10·20/20 은 훑어본 값이지 최적화한 값이 아니다.

---

## D7(끌개 노선) 측정 — 죽음, 그리고 그보다 큰 정정 (2026-07-22)

발산 지도가 월요일 후보로 고른 D7(유역을 여럿 심어 many-to-one 붕괴를 만든다)을 쟀다.
재현 스크립트 `state/communication/attractor_canonicalization.py`. 방향은 죽었고, **죽이는
과정에서 지금까지의 공통 결론 하나를 정정**해야 했다.

### 정정 ① — "양상 불변성" 검사는 애초에 불가능했다

4,000단어에서 같은 단어의 두 독립 해시가 공유하는 정보:

| | 상호정보량 |
| --- | ---: |
| 두 독립 해시 (같은 단어에서 나옴) | 0.0185 비트 |
| 같은 값을 뒤섞은 귀무 | 0.0212 비트 |

**같다.** 공유 정보가 0이다. 어떤 동역학도 없는 정보를 복원할 수 없으므로, 이 검사는
기판의 성질이 아니라 **불가능한 과제**를 재고 있었다. 위임 보고서와 이 문서가 각각
"양상 불변성 반증"이라고 적은 것은 **둘 다 같은 착오**였다 — 두 계기가 같은 결론에
도달한 것은 재현이 아니라, 같은 잘못된 검사를 두 번 돌린 것이다.

공정한 검사는 **실제로 구조를 공유하는** 양상이어야 한다 (한 단어의 글과 소리가 그렇듯).

### 정정 ② — 공유 구조가 있어도 끌개는 기여하지 않는다

하나의 잠재값에서 나온 잡음 관측 두 개로 다시 쟀다. 대조군은 **끌개가 없는** 같은 기판.

| 양상 잡음 | 끌개 기판 | 대조군 |
| ---: | ---: | ---: |
| 0.5 | 83% | 83% |
| 1.0 | 62% | 62% |
| 1.5 | 60% | 60% |

**소수점까지 같다.** 일치는 입력이 이미 갖고 있던 공유 구조 때문이고, 동역학이 더한 것은
0이다.

### 하마터면 성공으로 보일 뻔한 것

이득을 낮추면 일치율이 **100%** 로 뛴다. 그런데 쓰인 유역이 **1개**다 — 모든 입력이 한
군데로 무너진 것이고, 100% 일치는 정보가 0이라서 나온 값이다. 유역을 다 쓰는 이득
2 이상에서는 일치율 50~60% 로, **끌개 없는 대조군보다 낮거나 같다.**

| 이득 | 일치율 | 쓰인 유역 | 판정 |
| ---: | ---: | ---: | --- |
| 1.0 | 100% | **1** | 붕괴 — 정보 0 |
| 1.5 | 100% | **1** | 붕괴 — 정보 0 |
| 2.0 | 50% | 4 | 대조군 이하 |
| 4.0 | 60% | 4 | 대조군 이하 |
| 8.0 | 58% | 4 | 대조군 이하 |

**일치율은 쓰인 유역 수와 함께 보지 않으면 의미가 없다.** 이 두 열을 같이 두지 않았다면
"이득 1에서 100% 정준화 달성"이라고 적었을 것이다.

### 남는 것

- D7 은 이 크기(4유닛 · 심은 유역 2~4개)에서 **죽었다.** 위임 보고서가 미리 경고한
  함정("유역을 심는 것은 설계자가 범주를 정하는 일") 그대로다.
- 벽(통합↔표상)은 여전히 **시간 다중화로 깨져 있다** — 그건 이 측정과 무관하게 유효하다.
- 정준화는 미해결이며, 이제 **문제의 모양이 더 정확하다**: 정준화는 서로 다른 입력이
  같은 것에서 나왔다는 **증거가 입력 안에 있을 때만** 가능하다. 그 증거를 만드는 것은
  동역학이 아니라 **함께 나타남(co-occurrence)** 이고, 그걸 이용하려면 이 저장소에 아직
  없는 것 — **가소성(학습)** 이 필요하다.

---

## 가소성 착지: `align.py` — 정준화가 실제로 일어난다 (2026-07-22)

D7 의 죽음이 남긴 문제의 모양("증거는 신호 안에 있어야 하고, 그걸 넣는 건 함께 나타남")을
그대로 구현했다. **학습에 한 번도 쓰지 않은 개념으로만 채점**한다.

| 조건 | 배운 양 (12시드 평균) | 최악 시드 |
| --- | ---: | ---: |
| 정상 (짝이 맞음) | **+0.780** | +0.566 |
| 대조군 (짝 흐트러뜨림) | −0.067 | −0.428 |

개념 **10개**만 봐도 처음 보는 개념이 정렬된다(+0.748). 짝의 목록이 아니라 **양상 사이의
대응**을 배웠다는 뜻이다. 양상이 비선형으로 얽혀도 작동한다(+0.704, 잡음 0.1).

### 또 하나의 "하마터면"

처음엔 원시 차이에 문턱 0.3 을 걸었다. 그런데 **학습 0쌍짜리 학습기가 통과했다** — 두 양상이
같은 잠재값을 섞은 것이라 무작위 사영도 상관을 갖고, 운 나쁜 시드는 0.397 까지 나온다
(12시드 평균 0.049). 문턱을 **자기 출발점 대비 증가분**으로 옮기자 학습 0쌍은 12/12 실패,
정상 학습은 6/6 통과가 됐다.

### 성능 버그도 하나

`step()` 이 매 걸음마다 `state` 를 돌려주게 짰는데, `state` 는 학습에 안 쓴 380쌍을 전부
재는 비싼 측정이라 4,000쌍 학습이 10분을 넘겼다. 학습(싼 것)과 채점(비싼 것)을 분리하고
고정된 세계의 관측을 캐시하니 **0.10초**가 됐다.

### 이것이 아닌 것

학습된 선형 사상 두 개다. 얻은 것은 "한 가지에 대한 닮지 않은 두 신호를 한곳으로 모을 수
있고, 그 모음이 처음 보는 개념에도 전이된다"뿐이다. 그 정렬을 **하류에서 무엇이 쓰는지**는
아무것도 답하지 않았고, 정렬과 결합 엔진은 아직 이어져 있지 않다.

---

## 리듬을 엔진에 올림, 그리고 정정 ③ — 27배는 τ 교락이었다 (2026-07-22)

교대 결합이 `state/` 스크립트에만 있고 엔진에는 없었다. `coupled.Rhythm` 으로 정식 구현하고
(`drive` 입력 + 결합 스케줄), 재도출 스크립트를 **엔진을 구동하도록** 바꿨다 — 사본을 재현하는
것은 남이 import 하는 것에 대한 증거가 아니다. 그 과정에서 위 「벽을 깨는 후보 측정」의
헤드라인이 무너졌다.

### 무엇이 틀렸나

| | 교대 20/20 | 고정 0.70 |
| --- | ---: | ---: |
| 앞선 표가 맞댄 것 | Φ 14.6 (**τ=40**) | Φ 10.6 (**τ=20**) |

Φ 는 **τ 만으로도 오른다** (같은 엔진: τ=17 에서 12.07, τ=34 에서 14.88). 두 행은 애초에
비교가 아니었다. τ 를 맞춰 다시 쟀다 (τ=40, 6400 시행, 5시드, drive=0.42):

| 구성 | 방향성 Φ | 표상 |
| --- | ---: | ---: |
| 교대 20/20 | **13.16 ± 0.53** | **3.49** |
| 고정 1.00 | 14.66 ± 0.08 | 0.00 |
| 고정 0.70 | 15.74 ± 0.13 | 0.13 |

교대가 **덜** 통합한다. 5시드 전부에서 최대 교대(13.433) < 최소 고정(14.554) — 시드 겹침
없음. **"더 높은 Φ 에서 27배" 는 반증됐다.**

### 그리고 방향조차 고정이 아니다 — 새 조건: `drive`

τ=40 에서 같은 비교를 입력값만 바꿔 다시 하면:

| 무엇을 들려주는가 | 교대 20/20 Φ |
| --- | ---: |
| 아무것도 (0.00) | 14.99 |
| 0.42 | 13.16 |
| −0.27 | 14.70 (고정 1.00 의 14.68 과 구분 불가) |

**리듬은 들을 수 있으므로 Φ 가 들은 것에 따라 움직인다. 고정 결합은 들을 수 없으므로 안
움직인다** (전이행렬이 비트 단위로 동일 — `tests/test_rhythm.py` 가 정확히 이걸 고정한다).
그래서 `drive` 없이 인용한 Φ 는 τ 없이 인용한 Φ 와 똑같이 틀린 문장이다.

### 살아남는 것

1. **벽은 실재한다.** 고정 결합에서 표상은 결합에 대해 단조 감소하고, 결합 1.00 에서는
   정확히 0 이며 입력이 **비트 단위로 닿지 않는다**.
2. **교대는 고정 결합이 전혀 갖지 못한 표상을 되살린다** — 3.49~4.03 대 0.00~0.13.
3. **효과는 평균이 아니라 리듬의 것이다.** τ 를 맞춘 시간평균 대조군(고정 0.35, τ=20,
   입력 없음): 교대 8.02 대 대조군 0.85, 1600~6400 시행에서 안정.
4. 따라서 얻은 문장은 **"벽을 넘었다"가 아니라 "교환비를 옮겼다"** 이다.

### 왜 두 세션이 같은 오독을 했나

앞선 세션과 이번 세션이 같은 결론에 도달했지만, 그건 **재현이 아니라 같은 잘못된 비교를 두 번
돌린 것**이다. 이 저장소에서 이런 일이 두 번째다 (첫 번째: 양상 불변성 검사가 애초에 불가능했던
건 — 「정정 ①」). 교훈은 같다: **합의는 증거가 아니고, 조건을 맞췄는지가 증거다.**

### 값싼 검증으로는 못 잡는다

τ=40 비교를 1600 시행으로 줄이면 순서가 **뒤집힌다** (교대 14.99 > 고정 14.73). 6400 시행이
있어야 분리된다. 그래서 이 비교는 테스트가 아니라 스크립트에 있고, 테스트는 대신 **정확히
참인 것**(리듬은 입력에 따라 전이행렬이 바뀌고 고정은 안 바뀐다)을 고정한다.

---

## 정렬기 → 결합엔진: 정렬은 통합 엔진을 통과한다 (2026-07-22)

`align.py` 가 배운 대응이 **하류에서 쓰이는가**는 저장소가 계속 열어둔 질문이었다.
`coupled.py` 가 `drive`(들려주는 것)를 받게 되면서 배선이 생겼고, 이제 유닛별 **벡터**로도
받는다 — 표상은 숫자 하나가 아니므로 스칼라로는 평균만 도착한다.
재현 스크립트 `state/communication/aligned_drive.py`.

설계는 두 모델(fable · sol)에 위임했고 크게 일치했다. 갈린 지점 하나 — 6→4 압축을 고정
무작위 행렬로 할 것(fable) 대 `Aligner(dim=4)` 로 어댑터를 아예 없앨 것(sol) — 은 값싸게
검증해서 sol 을 택했다: dim=4 에서도 학습된다(+0.787 대 대조군 −0.118). fable 의 무작위
행렬안은 강건성 변형으로 남겨둔다.

**sol 이 결함도 하나 짚었다**: `observe()` 가 결정적이라 같은 개념을 12번 반복 관측해도
**같은 값 하나**였다. 그러면 관측잡음 불변성이 아니라 엔진잡음만 재게 되고, 개념이 아니라
**표본 하나**를 채점하게 된다. `sample=` 을 추가했다 (`sample=0` 은 비트 단위로 종전과 동일).

### 측정 — 교차양상 식별

보류 개념 20개. 양상 0 의 반복 관측으로 원형을 만들고, 양상 1 의 **다른** 반복 관측으로
질의해서, 가장 가까운 원형이 자기 개념인 비율을 센다. 우연 = 1/20.

**1단계 — 입력 수준 (엔진 없음).** 엔진은 정보를 잃기만 하므로, 여기서 없으면 하류에서
만들어낼 수 없다.

| 갈래 | 정확도 | 최악 시드 | 유효 랭크 |
| --- | ---: | ---: | ---: |
| **학습됨** | **0.401** | 0.300 | 1.35 |
| 원신호 (정렬 없음) | 0.053 | 0.000 | 1.93 |
| 미학습 (0쌍) | 0.038 | 0.000 | 1.45 |
| 대조군 (짝 흐트러뜨림) | 0.056 | 0.008 | 1.20 |
| 순열 바닥 | 0.154 | (최대 0.233) | |

state/communication/capacity.py:16:`units / 2` bits — via `units / 2` two-cycles, which is `Wiring.PAIRS`.
state/communication/capacity.py:55:    units: int, drive: tuple[float, ...], *, wiring: Wiring, chain: float, seed: int
state/communication/capacity.py:61:        chain=chain,
state/communication/capacity.py:83:    units: int, *, wiring: Wiring = Wiring.RING, chain: float = 0.0
state/communication/capacity.py:92:            settled(units, drive, wiring=wiring, chain=chain, seed=w)
state/communication/capacity.py:102:def report(label: str, units: int, *, wiring: Wiring, chain: float = 0.0) -> None:
state/communication/capacity.py:103:    reachable, held, share = capacity(units, wiring=wiring, chain=chain)
state/communication/capacity.py:126:    for units, chain in ((4, 0.0), (6, 0.0), (6, 0.2), (10, 0.2)):
state/communication/capacity.py:129:            f"{pairs} pairs, chain {chain:.1f}"
state/communication/capacity.py:132:            wiring=Wiring.PAIRS,
state/communication/capacity.py:133:            chain=chain,
src/anima_reborn/substrate.py:18:otherwise; `trials` is the honest knob and the estimate is a sample.
src/anima_reborn/substrate.py:62:    directed_big_phi,
src/anima_reborn/substrate.py:76:    "recurrence_evidence",
src/anima_reborn/substrate.py:85:"""Samples per state. The estimate's error falls as 1/sqrt(trials), so this
src/anima_reborn/substrate.py:113:    trials: int = TRIALS,
src/anima_reborn/substrate.py:121:            later. Called `trials` times per state, so it must not carry
src/anima_reborn/substrate.py:124:        trials: Samples per state.
src/anima_reborn/substrate.py:133:    if trials < 1:
src/anima_reborn/substrate.py:134:        raise ValueError(f"trials must be >= 1, got {trials}")
src/anima_reborn/substrate.py:140:        for _ in range(trials):
src/anima_reborn/substrate.py:145:        values.extend(count / trials for count in counts)
src/anima_reborn/substrate.py:155:    trials: int = TRIALS,
src/anima_reborn/substrate.py:182:    return estimate_matrix(size, step, trials=trials, seed=seed)
src/anima_reborn/substrate.py:228:    trials: int = TRIALS,
src/anima_reborn/substrate.py:241:        trials: Samples per state when measuring the transition matrix.
src/anima_reborn/substrate.py:252:        trials=trials,
src/anima_reborn/substrate.py:282:    the finding: `phi` cuts undirected and cannot see that a feedforward system
src/anima_reborn/substrate.py:283:    is reducible, `directed_phi` cuts one way at a time and can. A claim about
src/anima_reborn/substrate.py:284:    recurrence uses the directed number.
src/anima_reborn/substrate.py:287:    the result. The same engine reads 12.07 at `macro_step = 17` and exactly
src/anima_reborn/substrate.py:293:    """Undirected big-Phi — comparable with the rest of the repo."""
src/anima_reborn/substrate.py:294:    directed_phi: float
src/anima_reborn/substrate.py:300:    macro_step: int
src/anima_reborn/substrate.py:301:    trials: int
src/anima_reborn/substrate.py:305:        """Exactly zero directed Phi — some direction severs for free.
src/anima_reborn/substrate.py:310:        `is_recurrent` — see `recurrence_evidence`.
src/anima_reborn/substrate.py:312:        return self.directed_phi == 0.0
src/anima_reborn/substrate.py:318:            f"directed={self.directed_phi:6.3f} "
src/anima_reborn/substrate.py:320:            f"complex={entity} (state {self.state:04b}, tau={self.macro_step}, "
src/anima_reborn/substrate.py:321:            f"{self.trials} trials)"
src/anima_reborn/substrate.py:329:    chain: float = 0.0,
src/anima_reborn/substrate.py:332:    macro_step: int | None = None,
src/anima_reborn/substrate.py:335:    trials: int = TRIALS,
src/anima_reborn/substrate.py:340:    One transition is `macro_step` engine ticks: reconstruct the units to
src/anima_reborn/substrate.py:342:    amplitude and macro-step both sit inside the result.
src/anima_reborn/substrate.py:345:    default macro-step follows the rhythm rather than the module constant. Half
src/anima_reborn/substrate.py:348:    if macro_step is None:
src/anima_reborn/substrate.py:349:        macro_step = rhythm.macro_step
src/anima_reborn/substrate.py:350:    if macro_step < 1:
src/anima_reborn/substrate.py:351:        raise ValueError(f"macro_step must be >= 1, got {macro_step}")
src/anima_reborn/substrate.py:361:            chain=chain,
src/anima_reborn/substrate.py:371:        return engine.run(macro_step).pattern
src/anima_reborn/substrate.py:373:    return estimate_matrix(units, step, trials=trials, seed=seed)
src/anima_reborn/substrate.py:380:    chain: float = 0.0,
src/anima_reborn/substrate.py:384:    macro_step: int | None = None,
src/anima_reborn/substrate.py:387:    trials: int = TRIALS,
src/anima_reborn/substrate.py:401:        macro_step: Engine ticks per measured transition. Defaults to the
src/anima_reborn/substrate.py:404:        trials: Samples per state. The artefact floor falls with this.
src/anima_reborn/substrate.py:406:    if macro_step is None:
src/anima_reborn/substrate.py:407:        macro_step = rhythm.macro_step
src/anima_reborn/substrate.py:411:        chain=chain,
src/anima_reborn/substrate.py:414:        macro_step=macro_step,
src/anima_reborn/substrate.py:417:        trials=trials,
src/anima_reborn/substrate.py:420:    undirected: SystemPhi = big_phi(matrix, state)
src/anima_reborn/substrate.py:421:    directed: DirectedPhi = directed_big_phi(matrix, state)
src/anima_reborn/substrate.py:426:        phi=undirected.phi,
src/anima_reborn/substrate.py:427:        directed_phi=directed.phi,
src/anima_reborn/substrate.py:430:        macro_step=macro_step,
src/anima_reborn/substrate.py:431:        trials=trials,
src/anima_reborn/substrate.py:582:"""Directed Phi a wiring must clear before recurrence is entertained.
src/anima_reborn/substrate.py:586:worst over eight seeds at 400 trials, decaying to 0.037 at 25600. This bar is
src/anima_reborn/substrate.py:591:`big_phi` and `directed_big_phi` return 0.000000. The residue is sampling, and
src/anima_reborn/substrate.py:600:    A single positive Phi means nothing on its own: at 6400 trials the
src/anima_reborn/substrate.py:602:    still measures 0.031 directed. Sampling noise manufactures structure, and a
src/anima_reborn/substrate.py:603:    bare threshold would call that recurrence.
src/anima_reborn/substrate.py:606:    uses: measure twice and see whether it shrinks. Artefacts halve as trials
src/anima_reborn/substrate.py:615:        """The directed value survived a fourfold increase in sampling."""
src/anima_reborn/substrate.py:616:        return self.fine.directed_phi > self.coarse.directed_phi / 2
src/anima_reborn/substrate.py:625:        0.037 mean over eight seeds at 400 / 1600 / 6400 / 25600 trials, with a
src/anima_reborn/substrate.py:628:        return self.fine.directed_phi > RECURRENCE_FLOOR and self.held
src/anima_reborn/substrate.py:634:            f"{self.coarse.trials}->{self.fine.trials} trials: "
src/anima_reborn/substrate.py:635:            f"{self.coarse.directed_phi:.3f} -> {self.fine.directed_phi:.3f} "
src/anima_reborn/substrate.py:641:def recurrence_evidence(
src/anima_reborn/substrate.py:644:    trials: int = TRIALS,
src/anima_reborn/substrate.py:656:        coarse=coupled_phi(wiring, trials=trials, with_complex=False, **kwargs),
src/anima_reborn/substrate.py:657:        fine=coupled_phi(wiring, trials=trials * factor, with_complex=False, **kwargs),
src/anima_reborn/substrate.py:665:    trials: int = TRIALS,
src/anima_reborn/substrate.py:679:    if trials < 1:
src/anima_reborn/substrate.py:680:        raise ValueError(f"trials must be >= 1, got {trials}")
src/anima_reborn/substrate.py:687:        for _ in range(trials):
src/anima_reborn/substrate.py:689:        matrix.append([count / trials for count in counts])
tests/test_pipeline.py:1:"""The full chain — does engine separation actually produce emergence?"""
tests/test_retention.py:3:Pins that the 6-unit PAIRS cell holds all three latch bits indefinitely under a deaf hold,
tests/test_retention.py:29:        the hold is active recurrence, not slow relaxation."""
tests/test_retention.py:34:        """Feedforward has no cycle to hold a state, so it falls to chance — recurrence is
tests/test_sequence.py:1:"""The SequenceEngine shift chain — the shipped working-memory engine.
tests/test_words.py:122:        measured = big_phi(estimate_matrix(4, step, trials=400, seed=1), 0b1111)
tests/test_base.py:14:Every EMERGENT assertion clears the bar by at least 4x, and every INDEPENDENT
tests/test_rhythm.py:88:        assert Rhythm(coupling=0.7, period=10).macro_step == 20
tests/test_rhythm.py:89:        assert Rhythm(coupling=0.7).macro_step == MACRO_STEP
tests/test_rhythm.py:154:        Resolvable: 8.08 vs 0.90 at 1600 trials, 8.02 vs 0.85 at 6400, so this
tests/test_rhythm.py:158:            coupled_phi(rhythm=ALTERNATING, trials=1600, seed=s, with_complex=False)
tests/test_rhythm.py:159:            .directed_phi
tests/test_rhythm.py:165:                macro_step=ALTERNATING.macro_step,
tests/test_rhythm.py:166:                trials=1600,
tests/test_rhythm.py:169:            ).directed_phi
tests/test_rhythm.py:189:            matrix = coupled_matrix(rhythm=rhythm, drive=drive, trials=100, seed=1)
tests/test_rhythm.py:297:    """The one capability recurrence buys rather than merely exhibits.
tests/test_rhythm.py:446:    shows up as a measurement. `Wiring.PAIRS` spends the units on two-cycles
tests/test_rhythm.py:447:    instead, and a weak inter-pair `chain` integrates them without collapsing
tests/test_rhythm.py:449:    forms a macro-ring that can agree globally and locks. Full sweep in
tests/test_rhythm.py:454:    def _settled(units, drive, *, wiring, chain, seed):
tests/test_rhythm.py:456:            wiring=wiring, units=units, chain=chain, rhythm=ALTERNATING,
tests/test_rhythm.py:464:    def _held(self, units, *, wiring, chain=0.0):
tests/test_rhythm.py:471:                self._settled(units, drive, wiring=wiring, chain=chain, seed=w)
tests/test_rhythm.py:482:    def test_pairs_hold_more_and_a_chain_makes_it_reproducible(self) -> None:
tests/test_rhythm.py:484:        assert self._held(6, wiring=Wiring.PAIRS, chain=0.2) == 8
tests/test_rhythm.py:486:    def test_chain_zero_leaves_every_wiring_bit_identical(self) -> None:
tests/test_rhythm.py:488:        chained = CoupledEngine(seed=2, drive=0.3, chain=0.0).run(300)
tests/test_rhythm.py:489:        assert plain.values == chained.values
tests/test_rhythm.py:493:            Wiring.PAIRS.sources_for(5)
tests/test_rhythm.py:500:    factorized system whose directed Phi is a sampling artefact that collapses
tests/test_rhythm.py:501:    under more trials. A weak inter-pair chain makes them irreducible, and the
tests/test_rhythm.py:502:    held-under-4x-sampling test — not the magnitude, which the artefact inflates
tests/test_rhythm.py:508:    def test_disjoint_pairs_collapse_and_chained_pairs_hold(self) -> None:
tests/test_rhythm.py:509:        def phi(chain: float, trials: int) -> float:
tests/test_rhythm.py:512:                    Wiring.PAIRS, units=6, chain=chain, state=0b010101,
tests/test_rhythm.py:513:                    trials=trials, seed=s, with_complex=False,
tests/test_rhythm.py:514:                ).directed_phi
tests/test_rhythm.py:519:        chained_low, chained_high = phi(0.2, 400), phi(0.2, 1600)
tests/test_rhythm.py:521:        # The null collapses with more sampling; the chained system holds.
tests/test_rhythm.py:523:        assert chained_high > chained_low * 0.8, (chained_low, chained_high)
tests/test_rhythm.py:524:        assert chained_high > disjoint_high * 3
tests/test_rhythm.py:530:    Three disjoint latches (`chain=0`) hold three bits and pass storage on their
tests/test_rhythm.py:534:    1-2 only through the chain, and with no chain that path is exactly zero.
tests/test_rhythm.py:539:    def _cross_pair_response(chain: float, *, seed: int) -> float:
tests/test_rhythm.py:542:            wiring=Wiring.PAIRS, units=6, chain=chain, rhythm=ALTERNATING,
tests/test_rhythm.py:552:                wiring=Wiring.PAIRS, units=6, chain=chain, rhythm=ALTERNATING,
tests/test_rhythm.py:568:    def test_chained_pairs_do(self) -> None:
tests/test_viewer.py:294:            # in the `if` chain would miss whichever engine is the `else`.
tests/test_conversation_channel.py:1:"""The 3-bit PAIRS channel added for the free-conversation tab, and its 1-bit exactness.
tests/test_conversation_channel.py:5:it (`default-stays-exact`). `bits=3` is the proven `Wiring.PAIRS` substrate, calibrated in
tests/test_dialogue_session.py:62:        assert seen_b > 0, "no direction-B trials were inspected"
tests/test_dialogue_session.py:128:        assert rows, "no display-scramble trials were scheduled"
tests/test_coupled.py:31:from anima_reborn.iit4 import directed_big_phi
tests/test_coupled.py:39:    recurrence_evidence,
tests/test_coupled.py:44:self-wired null still reads ~0.27 here, which is why recurrence is claimed from
tests/test_coupled.py:50:        evidence = recurrence_evidence(Wiring.RING, trials=TRIALS, seed=0)
tests/test_coupled.py:52:        assert evidence.fine.directed_phi > 5.0
tests/test_coupled.py:59:                Wiring.FEEDFORWARD, trials=TRIALS, seed=seed, with_complex=False
tests/test_coupled.py:62:            assert reading.directed_phi == 0.0
tests/test_coupled.py:65:        evidence = recurrence_evidence(Wiring.SELF, trials=TRIALS, seed=0)
tests/test_coupled.py:70:        reading = coupled_phi(Wiring.RING, trials=TRIALS, seed=0)
tests/test_coupled.py:75:    def test_a_single_reading_offers_no_recurrence_verdict(self) -> None:
tests/test_coupled.py:77:        positive Phi from one measurement cannot establish recurrence — the
tests/test_coupled.py:79:        reading = coupled_phi(Wiring.SELF, trials=400, seed=0, with_complex=False)
tests/test_coupled.py:80:        assert reading.directed_phi > 0.0
tests/test_coupled.py:87:            Wiring.FEEDFORWARD, trials=400, seed=0, with_complex=False
tests/test_coupled.py:96:        def floor(trials: int) -> float:
tests/test_coupled.py:99:                    Wiring.SELF, trials=trials, seed=s, with_complex=False
tests/test_coupled.py:100:                ).directed_phi
tests/test_coupled.py:109:        ring = recurrence_evidence(Wiring.RING, trials=400, seed=1)
tests/test_coupled.py:117:            coupled_phi(Wiring.SELF, trials=400, seed=s, with_complex=False).directed_phi
tests/test_coupled.py:124:            recurrence_evidence(trials=400, factor=1)
tests/test_coupled.py:133:            Wiring.RING, macro_step=1, trials=TRIALS, seed=0, with_complex=False
tests/test_coupled.py:136:        assert reading.directed_phi == 0.0
tests/test_coupled.py:140:            Wiring.RING, state=0b0101, trials=800, seed=0, with_complex=False
tests/test_coupled.py:143:        assert reading.macro_step == MACRO_STEP
tests/test_coupled.py:144:        assert reading.trials == 800
tests/test_coupled.py:146:        assert str(reading.trials) in str(reading)
tests/test_coupled.py:149:    def test_the_macro_step_is_the_substrate_time_constant(self) -> None:
tests/test_coupled.py:156:                Wiring.RING, state=state, trials=TRIALS, seed=0, with_complex=False
tests/test_coupled.py:157:            ).directed_phi
tests/test_coupled.py:268:    def test_the_matrix_rejects_a_zero_macro_step(self) -> None:
tests/test_coupled.py:271:        with pytest.raises(ValueError, match="macro_step must be >= 1"):
tests/test_coupled.py:272:            coupled_matrix(macro_step=0)
tests/test_coupled.py:291:    def measure(wiring: Wiring, *, trials: int = 6400, seed: int = 0):
tests/test_coupled.py:303:            estimate_state_matrix(UNITS, step, trials=trials, seed=seed), bits=True
tests/test_coupled.py:305:        phi = directed_big_phi(
tests/test_coupled.py:306:            estimate_matrix(UNITS, step, trials=trials, seed=seed), 0b0101
tests/test_coupled.py:311:        """The inherited claim, refuted. On a feedforward chain Phi is exactly
tests/test_coupled.py:338:        matrix = estimate_state_matrix(2, lambda s, r: (s + 1) % 4, trials=50, seed=1)
tests/test_coupled.py:343:        matrix = estimate_state_matrix(2, lambda s, r: (s + 1) % 4, trials=20, seed=1)
tests/test_coupled.py:350:        square = estimate_state_matrix(2, step, trials=20, seed=1)
tests/test_coupled.py:351:        by_node = estimate_matrix(2, step, trials=20, seed=1)
tests/test_coupled.py:356:        with pytest.raises(ValueError, match="trials must be >= 1"):
tests/test_coupled.py:357:            estimate_state_matrix(2, lambda s, r: s, trials=0)
tests/test_accumulation.py:1:"""Time accumulation: the K-cell chain holds the last K symbols in order.
tests/test_accumulation.py:3:Pins the shift chain's core (order preserved through clean bridges), the deaf-bridge null
tests/test_accumulation.py:27:            tape = acc.run_chain(stream, seed=s)
tests/test_accumulation.py:41:            tape = acc.run_chain(stream, seed=s, deaf_bridge=True)
tests/test_accumulation.py:50:        assert acc.run_chain(stream, seed=9) == acc.run_chain(stream, seed=9)
tests/test_directed.py:1:"""Directed cuts — closing the carve-out that could not tell a loop from a chain.
tests/test_directed.py:3:The undirected measure reads a strictly feedforward system at 1.27 bits and does
tests/test_directed.py:4:not shrink with more trials, where IIT 4.0 says zero. Cutting one direction at a
tests/test_directed.py:6:reason*, because a directed search tries twice as many cuts and so cannot help
tests/test_directed.py:10:directed, not weakened), and the winning cut on the chain is identifiably the
tests/test_directed.py:26:from anima_reborn.iit4 import TransitionMatrix, big_phi, directed_big_phi
tests/test_directed.py:65:def matrix_for(sources: list[int | None], *, trials: int = TRIALS, seed: int = 0):
tests/test_directed.py:66:    return estimate_matrix(4, wired(sources), trials=trials, seed=seed)
tests/test_directed.py:70:    def test_the_undirected_measure_cannot_see_a_chain_is_reducible(self) -> None:
tests/test_directed.py:75:    def test_the_directed_measure_can(self) -> None:
tests/test_directed.py:77:            assert directed_big_phi(matrix_for(FEEDFORWARD, seed=seed), STATE).phi == 0.0
tests/test_directed.py:83:        measured = directed_big_phi(matrix_for(FEEDFORWARD), STATE)
tests/test_directed.py:93:            measured = directed_big_phi(matrix_for(RING, seed=seed), STATE)
tests/test_directed.py:98:        """A directed search tries both directions of every split, so its
tests/test_directed.py:101:        undirected = big_phi(matrix_for(RING), STATE).phi
tests/test_directed.py:102:        directed = directed_big_phi(matrix_for(RING), STATE).phi
tests/test_directed.py:103:        assert directed <= undirected + 1e-12
tests/test_directed.py:104:        assert directed > undirected * 0.5
tests/test_directed.py:118:            directed_big_phi(matrix_for(SELF, seed=s), STATE).phi for s in range(3)
tests/test_directed.py:134:        measured = directed_big_phi(estimate_matrix(4, step, trials=8000, seed=1), STATE)
tests/test_directed.py:141:        measured = directed_big_phi(matrix_for([1, 0, 3, 2]), 0b0101)
tests/test_directed.py:145:        assert directed_big_phi(matrix_for(RING), STATE).phi > 5.0
tests/test_directed.py:151:            directed_big_phi(matrix_for(SELF, trials=400, seed=s), STATE).phi
tests/test_directed.py:155:            directed_big_phi(matrix_for(SELF, trials=6400, seed=s), STATE).phi
tests/test_directed.py:161:        coarse = directed_big_phi(matrix_for(RING, trials=400), STATE).phi
tests/test_directed.py:162:        fine = directed_big_phi(matrix_for(RING, trials=6400), STATE).phi
tests/test_directed.py:178:            assert directed_big_phi(matrix_for(RING), STATE).phi == 0.0
tests/test_directed.py:185:        assert directed_big_phi(matrix_for(RING), STATE).phi > 5.0
tests/test_directed.py:190:        measured = directed_big_phi(TransitionMatrix([0.0, 1.0], 1), 0b1)
tests/test_directed.py:197:        assert directed_big_phi(pair, 0b11).is_recurrent
tests/test_directed.py:202:        assert directed_big_phi(pair, 0b11).phi == 0.0
tests/test_directed.py:205:def test_the_undirected_goldens_are_untouched() -> None:
tests/test_substrate.py:35:def phi_at(epsilon: float, *, trials: int = 1600, seed: int = 1) -> float:
tests/test_substrate.py:39:        trials=trials,
tests/test_substrate.py:46:def mean_phi(epsilon: float, *, trials: int, seeds: int = 4) -> float:
tests/test_substrate.py:48:        phi_at(epsilon, trials=trials, seed=s) for s in range(seeds)
tests/test_substrate.py:56:        assert mean_phi(0.0, trials=1600) > 1.0
tests/test_substrate.py:57:        assert mean_phi(1.0, trials=1600) > 1.0
tests/test_substrate.py:62:        assert mean_phi(0.5, trials=6400) < 0.2
tests/test_substrate.py:66:        assert mean_phi(0.5, trials=1600) < mean_phi(0.05, trials=1600) / 5
tests/test_substrate.py:71:        always = mean_phi(0.0, trials=1600)
tests/test_substrate.py:72:        never = mean_phi(1.0, trials=1600)
tests/test_substrate.py:76:        reading = crystal_phi(size=SIZE, epsilon=0.02, trials=1600, seed=1)
tests/test_substrate.py:88:        floor did not shrink with more trials it would be real integration; it
tests/test_substrate.py:92:        coarse = mean_phi(0.5, trials=400)
tests/test_substrate.py:93:        fine = mean_phi(0.5, trials=6400)
tests/test_substrate.py:97:    def test_real_integration_does_not_shrink_with_more_trials(self) -> None:
tests/test_substrate.py:99:        coarse = mean_phi(0.05, trials=400)
tests/test_substrate.py:100:        fine = mean_phi(0.05, trials=6400)
tests/test_substrate.py:105:        assert mean_phi(0.05, trials=6400) > 10 * mean_phi(0.5, trials=6400)
tests/test_substrate.py:125:        reading = crystal_phi(size=SIZE, epsilon=0.02, trials=400, seed=1)
tests/test_substrate.py:130:            size=SIZE, epsilon=0.02, trials=400, seed=1, with_verdict=False
tests/test_substrate.py:165:    def mean_phi(trials: int, seeds: int = 3) -> float:
tests/test_substrate.py:167:        compare (0.23 to 0.71 at 400 trials)."""
tests/test_substrate.py:171:                    4, TestOnlyCouplingIntegrates.memoryless, trials=trials, seed=s
tests/test_substrate.py:179:        """And it takes a great many trials to see that, which is the trap: at
tests/test_substrate.py:182:        Measured: 0.406 at 400 trials, 0.189 at 1600, 0.094 at 8000, 0.051 at
tests/test_substrate.py:195:            size=SIZE, epsilon=0.02, trials=400, seed=1,
tests/test_substrate.py:199:            size=SIZE, epsilon=0.02, trials=4000, seed=1,
tests/test_substrate.py:215:        matrix = estimate_matrix(2, swap, trials=8, seed=1)
tests/test_substrate.py:222:        matrix = estimate_matrix(1, coin, trials=20000, seed=1)
tests/test_substrate.py:226:        first = crystal_matrix(size=3, epsilon=0.1, trials=100, seed=7)
tests/test_substrate.py:227:        second = crystal_matrix(size=3, epsilon=0.1, trials=100, seed=7)
tests/test_substrate.py:231:        matrix = crystal_matrix(size=3, epsilon=0.1, trials=100, seed=2)
tests/test_substrate.py:239:            estimate_matrix(MAX_UNITS + 1, lambda s, r: s, trials=1)
tests/test_substrate.py:246:        with pytest.raises(ValueError, match="trials must be >= 1"):
tests/test_substrate.py:247:            estimate_matrix(2, lambda s, r: s, trials=0)
tests/test_substrate.py:267:        reading = crystal_phi(size=SIZE, epsilon=0.02, trials=1600, seed=1)
tests/test_substrate.py:273:            size=SIZE, epsilon=0.02, trials=400, seed=1, with_complex=False
tests/test_substrate.py:283:                trials=400,
tests/test_substrate.py:297:                trials=800,

exec
/bin/zsh -lc "sed -n '560,730p' src/anima_reborn/substrate.py; sed -n '430,590p' tests/test_rhythm.py; sed -n '1,230p' tests/test_directed.py; sed -n '1,180p' tests/test_coupled.py; rg -n \"6 units|pairs|chain|4x|directed|capacity|macro-lock\" state/communication/RESULTS.md state/coupling/RESULTS.md | sed -n '1,220p'" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:

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
    def test_holding_nothing_is_pinned_at_chance_by_construction(self) -> None:
        """Not luck. When the held state does not depend on what was told, a
        comparison and its mirror use one identical state and disagree, so the
        two cancel exactly."""
        for wiring in (Wiring.FEEDFORWARD, Wiring.SELF):
            assert self._score(wiring, seed=1) == pytest.approx(0.5, abs=1e-12)
        assert self._score(Wiring.RING, seed=1, loaded=False) == pytest.approx(
            0.5, abs=1e-12
        )


class TestCapacityIsTopologyNotCount:
    """Widening a single ring buys no capacity, and the way up is the wiring.

    A single ring of any even width holds exactly one bit — a theorem (the
    response is odd, decreasing, bounded, so no orbit longer than two) that
    shows up as a measurement. `Wiring.PAIRS` spends the units on two-cycles
    instead, and a weak inter-pair `chain` integrates them without collapsing
    the capacity — but only for an ODD number of pairs, because an even number
    forms a macro-ring that can agree globally and locks. Full sweep in
    `state/communication/capacity.py`.
    """

    @staticmethod
    def _settled(units, drive, *, wiring, chain, seed):
        engine = CoupledEngine(
            wiring=wiring, units=units, chain=chain, rhythm=ALTERNATING,
            drive=drive, seed=seed, initial=(0.0,) * units,
        )
        engine.run(400)
        engine.rhythm = FIXED
        engine.drive = 0.0
        return tuple(v > 0 for v in engine.run(240).values)

    def _held(self, units, *, wiring, chain=0.0):
        total = 1 << units
        step = max(1, total // 64)
        held = set()
        for i in range(0, total, step):
            drive = tuple((((i >> k) & 1) * 2 - 1) * 0.8 for k in range(units))
            landed = {
                self._settled(units, drive, wiring=wiring, chain=chain, seed=w)
                for w in range(8)
            }
            if len(landed) == 1:
                held |= landed
        return len(held)

    def test_the_single_ring_holds_one_bit_at_every_even_width(self) -> None:
        for units in (4, 6, 8):
            assert self._held(units, wiring=Wiring.RING) == 2, units

    def test_pairs_hold_more_and_a_chain_makes_it_reproducible(self) -> None:
        """Three pairs reach eight held states — three bits, not one."""
        assert self._held(6, wiring=Wiring.PAIRS, chain=0.2) == 8

    def test_chain_zero_leaves_every_wiring_bit_identical(self) -> None:
        plain = CoupledEngine(seed=2, drive=0.3).run(300)
        chained = CoupledEngine(seed=2, drive=0.3, chain=0.0).run(300)
        assert plain.values == chained.values

    def test_pairs_needs_an_even_width(self) -> None:
        with pytest.raises(ValueError, match="pairs needs an even width"):
            Wiring.PAIRS.sources_for(5)


class TestChainedPairsIntegrate:
    """The wall broken: six units that hold three bits AND measure as one thing.

    Three disjoint pairs are three separate latches — capacity 3 bits, but a
    factorized system whose directed Phi is a sampling artefact that collapses
    under more trials. A weak inter-pair chain makes them irreducible, and the
    held-under-4x-sampling test — not the magnitude, which the artefact inflates
    at six units — is what separates the two. `RECURRENCE_FLOOR` was calibrated
    at four units and does NOT transfer, which is exactly why the criterion here
    is decay, not a threshold.
    """

    def test_disjoint_pairs_collapse_and_chained_pairs_hold(self) -> None:
        def phi(chain: float, trials: int) -> float:
            return statistics.mean(
                coupled_phi(
                    Wiring.PAIRS, units=6, chain=chain, state=0b010101,
                    trials=trials, seed=s, with_complex=False,
                ).directed_phi
                for s in range(2)
            )

        disjoint_low, disjoint_high = phi(0.0, 400), phi(0.0, 1600)
        chained_low, chained_high = phi(0.2, 400), phi(0.2, 1600)

        # The null collapses with more sampling; the chained system holds.
        assert disjoint_high < disjoint_low * 0.6, (disjoint_low, disjoint_high)
        assert chained_high > chained_low * 0.8, (chained_low, chained_high)
        assert chained_high > disjoint_high * 3


class TestIntegrationIsAFunctionNotACoincidence:
    """The capstone's one sentence that coexistence cannot fake.

    Three disjoint latches (`chain=0`) hold three bits and pass storage on their
    own while measuring as reducible — so "concepts survive on the integrated
    substrate" earns only coexistence. The one place integration is a FUNCTION
    is the cross-pair probe: a probe differing only within pair 0 can move pairs
    1-2 only through the chain, and with no chain that path is exactly zero.
    Full composition in `state/communication/concepts.py`.
    """

    @staticmethod
    def _cross_pair_response(chain: float, *, seed: int) -> float:
        drive = tuple((((5 >> k) & 1) * 2 - 1) * 0.8 for k in range(6))
        engine = CoupledEngine(
            wiring=Wiring.PAIRS, units=6, chain=chain, rhythm=ALTERNATING,
            drive=drive, seed=seed, initial=(0.0,) * 6,
        )
        engine.run(400)
        engine.rhythm = FIXED
        engine.drive = 0.0
        held = engine.run(240).values

        def move(start):
            probe = CoupledEngine(
                wiring=Wiring.PAIRS, units=6, chain=chain, rhythm=ALTERNATING,
                drive=0.0, seed=seed, initial=tuple(start),
            )
            return sum(
                sum((probe.step().values[i] - held[i]) ** 2 for i in range(2, 6))
                for _ in range(20)
            )

        flipped = list(held)
        flipped[0], flipped[1] = held[1], held[0]  # change pair 0 only
        return abs(move(flipped) - move(list(held)))

    def test_disjoint_pairs_cannot_respond_across_a_pair(self) -> None:
        """Exactly zero — there is no causal path between the pairs."""
        assert self._cross_pair_response(0.0, seed=1) == 0.0

    def test_chained_pairs_do(self) -> None:
        """The integrated whole moves where its parts cannot."""
        assert self._cross_pair_response(0.2, seed=1) > 0.01
"""Directed cuts — closing the carve-out that could not tell a loop from a chain.

The undirected measure reads a strictly feedforward system at 1.27 bits and does
not shrink with more trials, where IIT 4.0 says zero. Cutting one direction at a
time fixes that. These tests exist to make sure it fixes it *for the right
reason*, because a directed search tries twice as many cuts and so cannot help
returning a smaller number — a lower value proves nothing on its own.

What proves it: the ring stays high through the same code (so the search was
directed, not weakened), and the winning cut on the chain is identifiably the
one pointing at the exogenous unit (so the zero is structural, not numerical).

The battery at the end is the calibration set both delegated reviews converged
on: systems whose integration is known by construction, each of which the
measure must get right before it is trusted anywhere else.
"""

from __future__ import annotations

import math
import random
import statistics

import pytest

from anima_reborn.iit4 import TransitionMatrix, big_phi, directed_big_phi
from anima_reborn.pipeline import PULL, WALK
from anima_reborn.substrate import estimate_matrix

AMPLITUDE = 0.78
GAIN = 3.0
MACRO_STEP = 17
"""The substrate's time constant. Phi is zero at tau = 1 whatever the wiring —
see `state/coupling/RESULTS.md`."""

STATE = 0b0101
TRIALS = 6400

RING = [3, 0, 1, 2]
"""Closed cycle: every unit reads another, influence returns."""
FEEDFORWARD = [None, 0, 1, 2]
"""Unit 0 is exogenous; nothing flows back into it."""
SELF = [0, 1, 2, 3]
"""Each unit reads itself — no coupling at all, the null."""


def wired(sources: list[int | None]):
    def step(state: int, rng: random.Random) -> int:
        x = [AMPLITUDE if state >> i & 1 else -AMPLITUDE for i in range(4)]
        for _ in range(MACRO_STEP):
            nxt = list(x)
            for i, source in enumerate(sources):
                target = (
                    -AMPLITUDE
                    if source is None
                    else -AMPLITUDE * math.tanh(GAIN * x[source] / AMPLITUDE)
                )
                nxt[i] = x[i] + (target - x[i]) * PULL + (rng.random() - 0.5) * WALK
            x = nxt
        return sum(1 << i for i, v in enumerate(x) if v > 0)

    return step


def matrix_for(sources: list[int | None], *, trials: int = TRIALS, seed: int = 0):
    return estimate_matrix(4, wired(sources), trials=trials, seed=seed)


class TestTheCarveOutCloses:
    def test_the_undirected_measure_cannot_see_a_chain_is_reducible(self) -> None:
        """The defect, stated as a test so it stays visible after the fix."""
        readings = [big_phi(matrix_for(FEEDFORWARD, seed=s), STATE).phi for s in range(3)]
        assert min(readings) > 0.5, readings

    def test_the_directed_measure_can(self) -> None:
        for seed in range(3):
            assert directed_big_phi(matrix_for(FEEDFORWARD, seed=seed), STATE).phi == 0.0

    def test_the_zero_points_at_the_exogenous_unit(self) -> None:
        """Not a smaller number — the *right* cut. Unit 0 takes no input from
        the system, so severing everything aimed at it costs nothing, which is
        exactly why the theory calls a feedforward system reducible."""
        measured = directed_big_phi(matrix_for(FEEDFORWARD), STATE)
        assert measured.cut is not None
        assert measured.cut.sink == 0b0001
        assert measured.cut.source == 0b1110

    def test_a_ring_has_no_free_direction(self) -> None:
        """The positive control, and the whole reason the zero above means
        something: the same code, searching the same doubled space, still finds
        no cheap cut when influence returns."""
        for seed in range(3):
            measured = directed_big_phi(matrix_for(RING, seed=seed), STATE)
            assert measured.is_recurrent
            assert measured.phi > 5.0, measured

    def test_directing_the_cut_did_not_weaken_the_search(self) -> None:
        """A directed search tries both directions of every split, so its
        minimum can only fall. What must not happen is the ring falling with
        it."""
        undirected = big_phi(matrix_for(RING), STATE).phi
        directed = directed_big_phi(matrix_for(RING), STATE).phi
        assert directed <= undirected + 1e-12
        assert directed > undirected * 0.5


class TestCalibrationBattery:
    """Systems whose integration is known by construction.

    Both delegated reviews converged on wanting exactly this before the measure
    is trusted anywhere new, and the reasoning is the repo's own: a measure that
    cannot fail on a system with a known answer is not a measure.
    """

    def test_an_identity_network_has_no_integration(self) -> None:
        """Each unit copies itself. Whatever else it does, nothing is shared."""
        readings = [
            directed_big_phi(matrix_for(SELF, seed=s), STATE).phi for s in range(3)
        ]
        assert statistics.mean(readings) < 0.2, readings

    def test_a_shared_cause_is_not_integration(self) -> None:
        """Four units driven by one common source, reading nothing of each
        other. They correlate; they do not integrate."""

        def step(state: int, rng: random.Random) -> int:
            common = rng.random() - 0.5
            return sum(
                1 << i
                for i in range(4)
                if 0.2 * (rng.random() - 0.5) + 0.8 * common > 0
            )

        measured = directed_big_phi(estimate_matrix(4, step, trials=8000, seed=1), STATE)
        assert measured.phi < 0.2

    def test_two_disconnected_pairs_do_not_integrate_as_a_whole(self) -> None:
        """Each pair reads itself into a loop; the pairs never meet. Both halves
        are integrated, the whole is not — and the free cut is the one between
        them."""
        measured = directed_big_phi(matrix_for([1, 0, 3, 2]), 0b0101)
        assert measured.phi < 0.5, measured

    def test_a_closed_loop_does_integrate(self) -> None:
        assert directed_big_phi(matrix_for(RING), STATE).phi > 5.0

    def test_noise_estimates_shrink_with_samples(self) -> None:
        """The artefact discipline, applied to the new measure. A system with
        no coupling must read lower the harder you look."""
        coarse = statistics.mean(
            directed_big_phi(matrix_for(SELF, trials=400, seed=s), STATE).phi
            for s in range(3)
        )
        fine = statistics.mean(
            directed_big_phi(matrix_for(SELF, trials=6400, seed=s), STATE).phi
            for s in range(3)
        )
        assert fine < coarse / 2

    def test_a_real_signal_does_not(self) -> None:
        coarse = directed_big_phi(matrix_for(RING, trials=400), STATE).phi
        fine = directed_big_phi(matrix_for(RING, trials=6400), STATE).phi
        assert fine > coarse * 0.5
        assert fine > 5.0


class TestTheNumberCarriesItsConditions:
    def test_at_one_tick_nothing_integrates_whatever_the_wiring(self) -> None:
        """The timescale sits inside the result. One engine tick moves a unit 6%
        toward its target, so every unit merely copies itself, the matrix
        factorizes, and Phi is exactly zero — for the ring too. Quoting the
        ring's value without its tau is not shorthand, it is a false statement.
        """
        global MACRO_STEP
        original = MACRO_STEP
        try:
            MACRO_STEP = 1
            assert directed_big_phi(matrix_for(RING), STATE).phi == 0.0
            assert big_phi(matrix_for(RING), STATE).phi == 0.0
        finally:
            MACRO_STEP = original

    def test_the_ring_is_back_at_the_measured_value(self) -> None:
        """Guards the restore above, and pins the headline number."""
        assert directed_big_phi(matrix_for(RING), STATE).phi > 5.0


class TestSmallSystems:
    def test_a_single_unit_has_nothing_to_cut(self) -> None:
        measured = directed_big_phi(TransitionMatrix([0.0, 1.0], 1), 0b1)
        assert measured.phi == 0.0
        assert measured.cut is None

    def test_a_coupled_pair_is_recurrent(self) -> None:
        """Each unit becomes the other — influence returns in one step."""
        pair = TransitionMatrix([0, 0, 0, 1, 1, 0, 1, 1], 2)
        assert directed_big_phi(pair, 0b11).is_recurrent

    def test_independent_units_are_not(self) -> None:
        """Each unit becomes itself: two systems sharing a name."""
        pair = TransitionMatrix([0, 0, 1, 0, 0, 1, 1, 1], 2)
        assert directed_big_phi(pair, 0b11).phi == 0.0


def test_the_undirected_goldens_are_untouched() -> None:
    """The hexa parity contract is not what changed here. Closing a carve-out
    means adding a measure beside the old one, never redefining it."""
    coupled = TransitionMatrix([0, 0, 0, 1, 1, 0, 1, 1], 2)
    assert big_phi(coupled, 0b11).phi == 1.9999999994229218
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
state/communication/RESULTS.md:544:재현 스크립트 `state/communication/capacity.py`, 결정 IIT 실행은 `coupled_phi(Wiring.PAIRS, ...)`.
state/communication/RESULTS.md:571:쌍 사이 약한 사슬(`chain=0.2`)이 걸리면 환원 불가가 된다:
state/communication/RESULTS.md:603:`chain=0`(분리된 래치 3개)도 3비트를 담고 각 래치가 저장을 통과한다 — **환원가능인데도**.
state/communication/RESULTS.md:605:아니다. `chain=0` 을 일급 귀무로 넣었고, 통합이 **기능**이 되는 유일한 곳은 교차-쌍 탐침이다.
state/communication/RESULTS.md:631:**그러나 저장은 통합을 필요로 하지 않는다**: `chain=0`(분리 래치, 환원가능)도 62% 로 똑같이
state/communication/RESULTS.md:643:`chain=0` 의 0 은 **구조적**이다 — 쌍 사이 인과 경로가 없으니 정확히 0. 비영 응답은 **통합된
state/communication/RESULTS.md:814:고리 대신 검증된 `Wiring.PAIRS`(6유닛·3쌍·`chain=0.2`, `capacity.py` 가 3비트·통합으로 확인)를
state/communication/RESULTS.md:833:의 것이다. `capacity.py` 의 88% 는 다른 조건(무작위 시작의 재현율)이었고, 여기 구동-디코드 충실도
state/coupling/RESULTS.md:75:위 ⚠ 항목이 `src/anima_reborn/iit4/directed.py` 로 해결됐다. 기존 `big_phi` 는 **손대지
state/coupling/RESULTS.md:101:두 위임 리뷰가 공통으로 요구한 **보정 배터리**도 함께 통과한다 (`tests/test_directed.py`):

codex
The smallest honest first commit is measurement-only: `state/communication/phi_proxy.py`, committed validation fixtures/tests, and Korean results added only after the run. Do not expose a `src/` API until it passes the exact window, budget-convergence test, and wide null battery.

Two corrections are load-bearing:

- The current [`directed_big_phi`](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/iit4/directed.py) is not categorical mutual information. It sums destroyed IIT distinctions and relations in one specified state. A visited-state MI estimator is therefore a surrogate, not merely a faster implementation.
- Odd chained PAIRS cannot be tested at 8, 12, or 20 units: those widths contain 4, 6, and 10 pairs— all even and therefore macro-locking. The positive widths are 10, 14, and 22; 8, 12, and 20 are parity nulls.

Those facts must appear prominently in the result.

## 1. Exact proxy definition

### Measurement conditions

Every reading carries:

```text
units, wiring, chain, rhythm, drive policy, threshold,
tau, amplitude, gain, walk seed, state budget,
cut budget, cut seed, folds
```

Use the existing conditions unless the experiment explicitly says otherwise:

- Zero threshold.
- Existing `AMPLITUDE`, `GAIN`, `WALK`.
- `tau = rhythm.macro_step`; fixed systems therefore use the existing `MACRO_STEP`.
- Eight independent walk seeds, `0..7`.
- Nested state budgets `4,096 → 16,384 → 65,536` transition observations.
- Nested random-cut budgets `N → 2N → 4N`.
- The smaller reading is always an exact prefix of the larger seeded stream, so convergence is not confused with a different draw.

Generate observations from 64 independently seeded engine trajectories per configuration. Initialize each normally, discard ten macro-steps, then record non-overlapping `(X_t, X_t+τ)` pairs round-robin. `X` and `Y` are zero-threshold sign patterns. No state absent from the runs is fabricated.

Report alongside every result:

- Number of distinct current states.
- Effective support `2^H(X)`.
- Fraction of held-out states unseen in training.
- Per-state visit-count distribution.

If held-out context coverage is below 95% at the largest budget, the result is “not measurable at this width,” not zero and not integrated.

### Directed cut score

For a directed cut `A -/-> B`, the cut model removes knowledge of the source bits `X_A` when predicting each sink bit at the next macro-step.

For sink unit `j ∈ B`, estimate the out-of-sample log-score gain:

\[
D_{A\to B,j}
=
E\left[
\log_2
\frac{\hat P(Y_j\mid X)}
     {\hat P(Y_j\mid X_{\bar A})}
\right].
\]

Then:

\[
D_{A\to B}=\sum_{j\in B}D_{A\to B,j}.
\]

Implementation details are fixed:

- Five-fold cross-fitting.
- Split whole trajectories, never individual adjacent transitions.
- Train the full categorical model on contexts `X`.
- Train the cut model on contexts `X & ~A`.
- Use Jeffreys/KT binary smoothing:

\[
\hat P(Y_j=1\mid c)=\frac{n_1(c)+1/2}{n(c)+1}.
\]

- Score only held-out observations.
- Do not use the ordinary plug-in MI estimator.
- Do not clip negative estimates to zero.

The richer full model is penalized when its contexts are sparse, so finite-budget error is intentionally conservative. Clipping would restore an upward bias.

This score is a directed conditional-predictive-information proxy. It is not yet entitled to be called approximate IIT Φ.

### Cut family

Construct unordered structural partitions, canonicalizing unit 0 to the left, and evaluate both directions of each:

1. Every singleton-unit versus rest cut.
2. Every complete pair versus rest cut.
3. Every split between the two members of a PAIRS latch.
4. Every contiguous block of complete pairs versus the remaining pair-chain, over all rotations and block lengths.
5. Every prefix/suffix cut of FEEDFORWARD’s unit ordering.
6. `R = rN` unique seeded random balanced partitions, with `r ∈ {1,2,4}`.
7. From each random seed cut, perform deterministic one-unit move/swap descent until no neighboring cut has a lower held-out score. Retain every evaluated cut.

The cut sets are nested. Increasing the cut budget can only expose a cheaper cut; it cannot manufacture a larger minimum.

The raw proxy is:

\[
Q_{B,R}=\min_{c\in C_R} D_c.
\]

Retain the signed value internally. Public reporting past six units reports only its paired separation and budget trend.

### Optional scale calibration

A visited-state predictive score and IIT distinction loss need not share scale. Permit only one calibration:

\[
\widehat\Phi_{\text{proxy}}=\alpha Q,\qquad \alpha\ge0,
\]

where `α` is a single zero-intercept least-squares scale fitted on development fixtures. No intercept, width term, wiring term, or topology-specific calibration is allowed. A positive intercept would turn null residue into “integration.”

Use leave-one-topology-out predictions and hold out the six-unit cases from the first fit. This calibrated number exists only for the exact-window test. It is never a reported wide Φ magnitude.

## 2. Validation against exact `iit4`

### Locked ground-truth grid

Use exact `iit4` on units 2 through 6, covering:

- SELF.
- FEEDFORWARD.
- Closed RING.
- Disconnected PAIRS.
- Chained PAIRS with `chain=0.2`.
- Even-pair macro-lock where constructible.
- Analytic identity, feedforward, closed-loop, shared-cause, and disconnected-pair TPM fixtures already represented by [`tests/test_directed.py`](/Users/mini/dancinlab/anima-reborn/tests/test_directed.py).

For stochastic engines, create one committed high-budget TPM fixture and pass that identical TPM to exact IIT and to the sampler. This separates proxy error from two independently sampled dynamics.

Because exact Φ is state-specific, validation states must be fixed before running:

- The canonical alternating state `0101…`.
- Its complement.
- Two seeded non-attractor states per width.

Do not average states first and call the result exact Φ.

### Acceptance tolerances

On every held-out fixture:

- For exact Φ ≤ 1 bit: absolute error ≤ 0.10 bit.
- For exact Φ > 1 bit: relative error ≤ 10%.
- Exact-zero fixtures: the proxy’s 95% upper bound must be ≤ 0.10 bit.
- No fixture may be discarded as an “outlier.”

This is a gate, not a promised result. If conditional predictive information cannot meet it, it is not a directed-Φ proxy; it remains a separate causal-dependence metric and cannot move the IIT measurability ceiling.

### Exact MIP test

For every small fixture, compute all directed IIT cut losses, not only the returned minimum. Then require:

- The structural-plus-random family contains the exact directed MIP.
- The proxy-selected direction and partition equal the exact MIP.
- If exact IIT has tied MIPs, the selected cut must belong to that exact tied set and follow IIT’s existing deterministic tie order.

For units ≤6, also run the proxy over all directed cuts. Record separately:

\[
\text{cut gap}=Q_{\text{sampled cuts}}-Q_{\text{all cuts}}\ge0.
\]

The final validation budget requires cut gap exactly zero on the locked fixtures. If it fails, widen the generic family or random-cut count—never add a fixture-specific mask.

## 3. Artefact control

### `artefact-honesty` test

For each locked fixture and each nested budget, record:

\[
E_B=\operatorname{mean}\left|
\widehat\Phi_{\text{proxy},B}-\Phi_{\text{exact}}
\right|.
\]

The committed fixture must satisfy:

```text
E_16,384 < E_4,096
E_65,536 < E_16,384
E_65,536 <= E_4,096 / 2
```

Also require:

- MIP mismatch count is non-increasing with budget.
- MIP mismatch count is zero at the final budget.
- Sampled-cut gap is non-increasing as `N → 2N → 4N`.
- SELF and disconnected-PAIRS residue shrink under the same state-budget increase.
- A validated recurrent positive control does not shrink like the null.

The full measured errors belong in `RESULTS.md`; a compact committed count fixture pins the trend in CI. Do not make ordinary tests rerun the entire 65,536-sample width-22 experiment.

### Wide battery

All configurations use identical state budgets, cut budgets, seeds, `tau`, binarization, and estimator.

Parity/null widths:

| Width | Configuration | Expected role |
|---:|---|---|
| 8, 12, 20 | SELF | no-coupling null |
| 8, 12, 20 | FEEDFORWARD | directed reducibility null |
| 8, 12, 20 | PAIRS, `chain=0` | disconnected-latch null |
| 8, 12, 20 | PAIRS, `chain=0.2` | even-pair macro-lock null |

Positive widths and their width-matched nulls:

| Width | Candidate | Same-width nulls |
|---:|---|---|
| 10, 14, 22 | PAIRS, `chain=0.2`—5, 7, 11 pairs | SELF, FEEDFORWARD, PAIRS `chain=0` |

Thus `(8,10)`, `(12,14)`, and `(20,22)` are parity-control pairs, while each positive also has genuine same-width nulls.

Run in increasing order and stop at the first positive width that fails. A failure at 14 is not permission to skip to 22.

## 4. Verdict rule

For each width and budget, pair candidate and null readings by walk seed and cut seed. Define:

\[
\Delta_b(s)=Q_{\text{candidate},b}(s)
-\max_z Q_{\text{null }z,b}(s).
\]

A width earns a positive verdict only if all of these hold:

1. Exact-window validation and the MIP test have already passed.
2. Finest-budget context coverage is at least 95%.
3. `Δ > 0` on all eight paired seeds at both `4B` and `16B`.
4. The one-sided 95% confidence bound of the paired mean separation is above zero at both budgets.
5. Mean separation at `16B` is at least half its value at `4B`.
6. SELF and disconnected-PAIRS residue collapse by at least half from `B` to `16B`.
7. Increasing cuts from `N` to `4N` does not erase the candidate/null separation.
8. The neighboring even-pair macro-lock control collapses under the same estimator.

The earned sentence is:

> At W units, odd chained PAIRS remained separated from its W-unit SELF, FEEDFORWARD, and disconnected-PAIRS nulls as transition and cut budgets increased; under a proxy validated against exact directed IIT through six units, integration at this width is supported under the stated sampling conditions.

For W = 10, 14, or 22, add the corresponding neighboring 8, 12, or 20-unit macro-lock result.

It must not say:

> Φ is X bits at W units.

Nor:

> W units are exactly IIT-integrated, integration scales with width, or the ceiling is unbounded.

If the rule fails, the sentence is:

> Integration was not established at W units by the validated proxy under the largest completed budget.

## 5. Phased first commit

Yes—the first commit should be measurement-only:

- `state/communication/phi_proxy.py`
- Committed small-system TPM/count fixtures.
- Exact-match, MIP, and budget-shrink tests.
- The 8/12/20 null battery and then 10/14/22 positives.
- Korean additions to `state/communication/RESULTS.md`, populated only by the completed run.

No existing engine parameter changes, so `default-stays-exact` is satisfied structurally.

Defer until validation passes:

- `src/anima_reborn/phi_proxy.py` or any public evidence object.
- Integration into [`substrate.py`](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/substrate.py).
- Removing or changing `MAX_UNITS`.
- Any `.is_integrated` convenience property.
- Viewer readout.
- Hierarchical-engine claims that depend on measuring the wider whole.

The eventual public API should return an evidence bundle—budgets, cut family, coverage, selected cut, matched nulls, seedwise separations, and verdict—not a lone `float`.

The honest successful deliverable is therefore: “the exact ceiling remains six; the validated separation ceiling moved to the largest measured passing width N.” If the candidate MI statistic fails the exact window, the result is equally valuable and must be recorded plainly: this particular proxy did not move the wall.
tokens used
76,469
The smallest honest first commit is measurement-only: `state/communication/phi_proxy.py`, committed validation fixtures/tests, and Korean results added only after the run. Do not expose a `src/` API until it passes the exact window, budget-convergence test, and wide null battery.

Two corrections are load-bearing:

- The current [`directed_big_phi`](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/iit4/directed.py) is not categorical mutual information. It sums destroyed IIT distinctions and relations in one specified state. A visited-state MI estimator is therefore a surrogate, not merely a faster implementation.
- Odd chained PAIRS cannot be tested at 8, 12, or 20 units: those widths contain 4, 6, and 10 pairs— all even and therefore macro-locking. The positive widths are 10, 14, and 22; 8, 12, and 20 are parity nulls.

Those facts must appear prominently in the result.

## 1. Exact proxy definition

### Measurement conditions

Every reading carries:

```text
units, wiring, chain, rhythm, drive policy, threshold,
tau, amplitude, gain, walk seed, state budget,
cut budget, cut seed, folds
```

Use the existing conditions unless the experiment explicitly says otherwise:

- Zero threshold.
- Existing `AMPLITUDE`, `GAIN`, `WALK`.
- `tau = rhythm.macro_step`; fixed systems therefore use the existing `MACRO_STEP`.
- Eight independent walk seeds, `0..7`.
- Nested state budgets `4,096 → 16,384 → 65,536` transition observations.
- Nested random-cut budgets `N → 2N → 4N`.
- The smaller reading is always an exact prefix of the larger seeded stream, so convergence is not confused with a different draw.

Generate observations from 64 independently seeded engine trajectories per configuration. Initialize each normally, discard ten macro-steps, then record non-overlapping `(X_t, X_t+τ)` pairs round-robin. `X` and `Y` are zero-threshold sign patterns. No state absent from the runs is fabricated.

Report alongside every result:

- Number of distinct current states.
- Effective support `2^H(X)`.
- Fraction of held-out states unseen in training.
- Per-state visit-count distribution.

If held-out context coverage is below 95% at the largest budget, the result is “not measurable at this width,” not zero and not integrated.

### Directed cut score

For a directed cut `A -/-> B`, the cut model removes knowledge of the source bits `X_A` when predicting each sink bit at the next macro-step.

For sink unit `j ∈ B`, estimate the out-of-sample log-score gain:

\[
D_{A\to B,j}
=
E\left[
\log_2
\frac{\hat P(Y_j\mid X)}
     {\hat P(Y_j\mid X_{\bar A})}
\right].
\]

Then:

\[
D_{A\to B}=\sum_{j\in B}D_{A\to B,j}.
\]

Implementation details are fixed:

- Five-fold cross-fitting.
- Split whole trajectories, never individual adjacent transitions.
- Train the full categorical model on contexts `X`.
- Train the cut model on contexts `X & ~A`.
- Use Jeffreys/KT binary smoothing:

\[
\hat P(Y_j=1\mid c)=\frac{n_1(c)+1/2}{n(c)+1}.
\]

- Score only held-out observations.
- Do not use the ordinary plug-in MI estimator.
- Do not clip negative estimates to zero.

The richer full model is penalized when its contexts are sparse, so finite-budget error is intentionally conservative. Clipping would restore an upward bias.

This score is a directed conditional-predictive-information proxy. It is not yet entitled to be called approximate IIT Φ.

### Cut family

Construct unordered structural partitions, canonicalizing unit 0 to the left, and evaluate both directions of each:

1. Every singleton-unit versus rest cut.
2. Every complete pair versus rest cut.
3. Every split between the two members of a PAIRS latch.
4. Every contiguous block of complete pairs versus the remaining pair-chain, over all rotations and block lengths.
5. Every prefix/suffix cut of FEEDFORWARD’s unit ordering.
6. `R = rN` unique seeded random balanced partitions, with `r ∈ {1,2,4}`.
7. From each random seed cut, perform deterministic one-unit move/swap descent until no neighboring cut has a lower held-out score. Retain every evaluated cut.

The cut sets are nested. Increasing the cut budget can only expose a cheaper cut; it cannot manufacture a larger minimum.

The raw proxy is:

\[
Q_{B,R}=\min_{c\in C_R} D_c.
\]

Retain the signed value internally. Public reporting past six units reports only its paired separation and budget trend.

### Optional scale calibration

A visited-state predictive score and IIT distinction loss need not share scale. Permit only one calibration:

\[
\widehat\Phi_{\text{proxy}}=\alpha Q,\qquad \alpha\ge0,
\]

where `α` is a single zero-intercept least-squares scale fitted on development fixtures. No intercept, width term, wiring term, or topology-specific calibration is allowed. A positive intercept would turn null residue into “integration.”

Use leave-one-topology-out predictions and hold out the six-unit cases from the first fit. This calibrated number exists only for the exact-window test. It is never a reported wide Φ magnitude.

## 2. Validation against exact `iit4`

### Locked ground-truth grid

Use exact `iit4` on units 2 through 6, covering:

- SELF.
- FEEDFORWARD.
- Closed RING.
- Disconnected PAIRS.
- Chained PAIRS with `chain=0.2`.
- Even-pair macro-lock where constructible.
- Analytic identity, feedforward, closed-loop, shared-cause, and disconnected-pair TPM fixtures already represented by [`tests/test_directed.py`](/Users/mini/dancinlab/anima-reborn/tests/test_directed.py).

For stochastic engines, create one committed high-budget TPM fixture and pass that identical TPM to exact IIT and to the sampler. This separates proxy error from two independently sampled dynamics.

Because exact Φ is state-specific, validation states must be fixed before running:

- The canonical alternating state `0101…`.
- Its complement.
- Two seeded non-attractor states per width.

Do not average states first and call the result exact Φ.

### Acceptance tolerances

On every held-out fixture:

- For exact Φ ≤ 1 bit: absolute error ≤ 0.10 bit.
- For exact Φ > 1 bit: relative error ≤ 10%.
- Exact-zero fixtures: the proxy’s 95% upper bound must be ≤ 0.10 bit.
- No fixture may be discarded as an “outlier.”

This is a gate, not a promised result. If conditional predictive information cannot meet it, it is not a directed-Φ proxy; it remains a separate causal-dependence metric and cannot move the IIT measurability ceiling.

### Exact MIP test

For every small fixture, compute all directed IIT cut losses, not only the returned minimum. Then require:

- The structural-plus-random family contains the exact directed MIP.
- The proxy-selected direction and partition equal the exact MIP.
- If exact IIT has tied MIPs, the selected cut must belong to that exact tied set and follow IIT’s existing deterministic tie order.

For units ≤6, also run the proxy over all directed cuts. Record separately:

\[
\text{cut gap}=Q_{\text{sampled cuts}}-Q_{\text{all cuts}}\ge0.
\]

The final validation budget requires cut gap exactly zero on the locked fixtures. If it fails, widen the generic family or random-cut count—never add a fixture-specific mask.

## 3. Artefact control

### `artefact-honesty` test

For each locked fixture and each nested budget, record:

\[
E_B=\operatorname{mean}\left|
\widehat\Phi_{\text{proxy},B}-\Phi_{\text{exact}}
\right|.
\]

The committed fixture must satisfy:

```text
E_16,384 < E_4,096
E_65,536 < E_16,384
E_65,536 <= E_4,096 / 2
```

Also require:

- MIP mismatch count is non-increasing with budget.
- MIP mismatch count is zero at the final budget.
- Sampled-cut gap is non-increasing as `N → 2N → 4N`.
- SELF and disconnected-PAIRS residue shrink under the same state-budget increase.
- A validated recurrent positive control does not shrink like the null.

The full measured errors belong in `RESULTS.md`; a compact committed count fixture pins the trend in CI. Do not make ordinary tests rerun the entire 65,536-sample width-22 experiment.

### Wide battery

All configurations use identical state budgets, cut budgets, seeds, `tau`, binarization, and estimator.

Parity/null widths:

| Width | Configuration | Expected role |
|---:|---|---|
| 8, 12, 20 | SELF | no-coupling null |
| 8, 12, 20 | FEEDFORWARD | directed reducibility null |
| 8, 12, 20 | PAIRS, `chain=0` | disconnected-latch null |
| 8, 12, 20 | PAIRS, `chain=0.2` | even-pair macro-lock null |

Positive widths and their width-matched nulls:

| Width | Candidate | Same-width nulls |
|---:|---|---|
| 10, 14, 22 | PAIRS, `chain=0.2`—5, 7, 11 pairs | SELF, FEEDFORWARD, PAIRS `chain=0` |

Thus `(8,10)`, `(12,14)`, and `(20,22)` are parity-control pairs, while each positive also has genuine same-width nulls.

Run in increasing order and stop at the first positive width that fails. A failure at 14 is not permission to skip to 22.

## 4. Verdict rule

For each width and budget, pair candidate and null readings by walk seed and cut seed. Define:

\[
\Delta_b(s)=Q_{\text{candidate},b}(s)
-\max_z Q_{\text{null }z,b}(s).
\]

A width earns a positive verdict only if all of these hold:

1. Exact-window validation and the MIP test have already passed.
2. Finest-budget context coverage is at least 95%.
3. `Δ > 0` on all eight paired seeds at both `4B` and `16B`.
4. The one-sided 95% confidence bound of the paired mean separation is above zero at both budgets.
5. Mean separation at `16B` is at least half its value at `4B`.
6. SELF and disconnected-PAIRS residue collapse by at least half from `B` to `16B`.
7. Increasing cuts from `N` to `4N` does not erase the candidate/null separation.
8. The neighboring even-pair macro-lock control collapses under the same estimator.

The earned sentence is:

> At W units, odd chained PAIRS remained separated from its W-unit SELF, FEEDFORWARD, and disconnected-PAIRS nulls as transition and cut budgets increased; under a proxy validated against exact directed IIT through six units, integration at this width is supported under the stated sampling conditions.

For W = 10, 14, or 22, add the corresponding neighboring 8, 12, or 20-unit macro-lock result.

It must not say:

> Φ is X bits at W units.

Nor:

> W units are exactly IIT-integrated, integration scales with width, or the ceiling is unbounded.

If the rule fails, the sentence is:

> Integration was not established at W units by the validated proxy under the largest completed budget.

## 5. Phased first commit

Yes—the first commit should be measurement-only:

- `state/communication/phi_proxy.py`
- Committed small-system TPM/count fixtures.
- Exact-match, MIP, and budget-shrink tests.
- The 8/12/20 null battery and then 10/14/22 positives.
- Korean additions to `state/communication/RESULTS.md`, populated only by the completed run.

No existing engine parameter changes, so `default-stays-exact` is satisfied structurally.

Defer until validation passes:

- `src/anima_reborn/phi_proxy.py` or any public evidence object.
- Integration into [`substrate.py`](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/substrate.py).
- Removing or changing `MAX_UNITS`.
- Any `.is_integrated` convenience property.
- Viewer readout.
- Hierarchical-engine claims that depend on measuring the wider whole.

The eventual public API should return an evidence bundle—budgets, cut family, coverage, selected cut, matched nulls, seedwise separations, and verdict—not a lone `float`.

The honest successful deliverable is therefore: “the exact ceiling remains six; the validated separation ceiling moved to the largest measured passing width N.” If the candidate MI statistic fails the exact window, the result is equally valuable and must be recorded plainly: this particular proxy did not move the wall.
