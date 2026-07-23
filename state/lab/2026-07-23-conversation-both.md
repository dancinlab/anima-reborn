<!-- sidecar lab full · model=(default) · cwd=/Users/mini/dancinlab/anima-reborn · prompt=7308 chars · 2026-07-23T06:57:20.482Z -->

── fable (claude-fable-5) · exit 0 ──
I've read `dialogue.py`, the full RESULTS ledger, the `PAIRS` API, and `capacity.py`'s proven envelope. Here is the design.

---

# Design: 대화 — a free, live, 3-bit exchange, measured by blind probes

## 1. Which interpretation

**Recommendation: interpretation 3 (both), phased so the risky halves don't land blind.** The reasoning is that neither half alone delivers "사람과 대화가 가능하게":

- Free-form at 1 bit fixes the *exam feeling* but leaves the human with nothing to say. Two referents means that after the convention forms (a few minutes), every utterance is forced — there is no act of *choosing what to mean*, and choosing what to mean is the part of conversation this repo can honestly buy.
- 3 bits inside the 220-trial schedule is a bigger questionnaire. The owner's complaint is the questionnaire, not the vocabulary size.

The two multiply rather than add: 8 compositional referents give the human intentions to pick; the free loop lets them pick. And the risk does *not* multiply, because of one structural choice below (the factorized channel), which makes the 3-bit game statistically the *same size* as the 1-bit game, and one measurement choice (blind probes), which reuses the existing stats machinery unchanged in shape.

**One-line dissent:** if you want the smallest possible first step, pure free-form at 1 bit (interpretation 1) ships in half the commit and tests the interaction shape first — but it will feel like ping-pong with one paddle within five minutes, and the owner will ask for vocabulary next week anyway.

The rigid `소통` tab **stays untouched** as the reference instrument. This is a new engine class (`Conversation`) and a new tab (`대화`), which makes `default-stays-exact` for the existing session trivial and satisfies `viewer-newengine` cleanly.

## The one structural decision everything else hangs on: factorize

The proven 3-bit substrate is `Wiring.PAIRS`, 6 units, 3 odd pairs, `chain=0.2`, addressed only through the three differentials `d[2j]−d[2j+1]`. The channel is *physically* three 1-bit latches. So make the game match the physics:

- **Referents are compositional**, not 8 arbitrary glyphs: three binary attributes — shape (▲/●) × size (큰/작은) × fill (채움/빈) — rendered as one composite glyph. 8 referents = 3 attribute bits.
- **Signals are compositional**: three jamo pairs (ㄱ/ㄴ · ㄷ/ㄹ · ㅁ/ㅂ), one glyph chosen per slot. 8 signals = 3 signal bits.
- **Policies are factorized**: per bit *j*, a 2×2 send policy (referent-bit → signal-bit) and a 2×2 receive policy (word-bit → act-bit). `reinforce` is called per bit with that bit's own harness-computed success (`act_j == ref_j`) — same signature, same aperture audit, zero new update machinery.

Consequences, all favorable:

- **Trial counts do not blow up.** A full 8×8 tabular policy would see ~11 training trials per row and never converge inside a human session. Factorized, every exchange trains all three 2×2 tables at once — each bit sees the *full* trial count, so the 3-bit game learns as fast as today's 1-bit game. The permutation test cost is unchanged (it permutes labels).
- **What remains a genuine convention** is stated honestly: the code space is restricted by design to the 8 product codes (a polarity per latch, plus which signal-slot carries which attribute is fixed by slot order). Each bit's polarity is a genuine 50/50 convention formed by consequence; the factorization itself is the designer's, and the docs say so. The sentence is "three independently-established 1-bit sub-conventions," never "the engine discovered composition."
- **The rank trap resolves per-bit.** 8 symbols collapsing to 2 effective shows up directly as a bit whose support or accuracy fails — see §3b.

## 2. The turn, concretely

Two free-exchange shapes plus one probe shape. The human always knows which they're in.

**Human speaks (A).** The human composes an intention — three attribute toggles, forming a composite glyph they *chose to say* (this choice is what the exam never had). They compose the utterance — one jamo per slot — and press **보내기**. The viewer animates the signal driving the 6-unit channel (~1s of TELL+HOLD traces; the sender may see their own TELL — the display aperture protects only direction B). The engine reads the three latches, its receive policies act, and **the engine's act is shown as a composite glyph beside the human's intended one, with per-attribute ✓/✗**. That reveal *is* the reply: "I said big-filled-triangle, it did big-filled-circle — shape didn't land yet." The engine reinforces per-bit; the human adapts in their head.

**Engine speaks (B).** The engine gets a harness-drawn hidden referent (harness-drawn, not history-derived — see §3), its send policies pick a signal, the channel runs, and the human sees **only the three HOLD panels** (one per pair, session-fixed markers, no latch, no sign, no TELL — the second aperture, unchanged). The human sets the three attribute toggles to "what I heard" and confirms. Then the reveal: the engine's actual referent beside their reading, per-attribute ✓/✗. The engine's send policy reinforces per-bit.

Each free turn, the human picks who speaks: **말하기 / 듣기**. No schedule, no fixed count, a running *practice* tally labeled `연습` (explicitly never evidence). A session ends when the human presses **마치기**.

**Probe (측정).** At a pre-registered cadence the harness interposes a visually distinct exchange (dimmed frame, "확인 중" label): same mechanics, but the referent is harness-drawn from a balanced deck, **no reveal, no reinforcement**, and the arm (live / frozen / deaf / dscramble) is assigned invisibly. The human just answers and the conversation resumes. Probes are the entire evidence base.

How the human knows it worked: moment-to-moment, the per-attribute reveal in free play; at the end, the report screen with the probe verdict, its nulls, and its widths — the same report shape as today.

## 3. How measurement survives free play

**Rejected: a rolling permutation on the free log.** Free-play rows are unusable as evidence for three separate reasons: referents are human-chosen (their distribution is a behavior, not a design — exchangeability under label permutation fails), feedback is continuous (there is no held-out anything), and learning is nonstationary mid-log. Any p-value on that log would be decorative. The free log is stored (`preserve-state`) and summarized descriptively, never tested.

**Adopted: free play is the conversation; blind probes are the measurement.** What was pre-registered as a *block schedule* becomes a pre-registered *probe policy* — module-level constants, not runtime choices:

- **Day-0**: before any free play, 8 probes per direction (blind, no feedback). Low-powered as before; the display-leak gate lives in dscramble, as already documented.
- **Channel calibration**: at session start, ~24 machine-only symbol→word runs (zero clicks) reporting per-bit flip rate. `channel-before-carrier`: the wire's own fidelity is the human's accuracy ceiling and is printed beside it, so a 0.85 human isn't read against an imaginary 1.0. (`capacity.py` measured 88% *joint* reproducibility — the wire is not clean, and pretending otherwise would misattribute channel noise to the humans' convention.)
- **Live probes**: after a warm-up of 20 free exchanges, one probe per 3 free exchanges, direction and arm drawn from shuffled balanced decks. Verdict minima: **16 live probes per direction**, **8 frozen + 8 deaf + 12 dscramble** B-arm probes (dscramble gets more because it is the load-bearing audit). Direction A's frozen/deaf/scramble stay free counterfactuals on the same recorded signal, per-bit, no extra clicks.
- **Stopping rule is safe by blindness.** The human may quit whenever they like. They never see probe outcomes, so stopping cannot condition on the evidence; the permutation p on probes given n stays valid. Quitting because free play *feels* converged is selecting on the thing being measured actually existing — the conservative direction. If minima aren't met at 마치기, the verdict is `insufficient_probes`, stored as such (never a partial claim; aborted sessions counted in `sessions/README.md` as now).
- **Stats**: the existing `session_stats` shape, generalized. Headline per direction: joint exact-match accuracy on live probes (chance 1/8) with the label-permutation p (10,000, unchanged cost), plus per-bit accuracies each with its own per-bit permutation. Structural gates stay per-bit where chance is 0.5 (day-0, frozen, deaf ≤ 0.65 per bit, pooled across bits with the dependence noted); **dscramble audit**: session-voiding `audit_failed` if its max per-bit rate > 0.75 at n=12 (per-bit chance of a false void ≈ 1.9%, ≈ 6% across three bits — noted in the report) or joint > 0.30. Gates that merely *block* a claim stay loose; the gate that *voids* a session is the one sized against false alarms.

**What yoked cannot survive the move, and what that costs the sentence.** The rigid session's yoked block works because feedback is only a ✓/✗ banner, which a coin can fake. In a conversation the reply *is* the engine's actual act, shown — a coin-reward context would require displaying a fabricated act, i.e. lying on the display channel. So the free session has **no yoked arm**, and its sentence drops "through consequence": the free-session claim is *established and used*, with the consequence-mechanism claim remaining the rigid tab's (already-shipped) result. This is stated in the report, not papered over. (The four hard gates — day-0, frozen, deaf, dscramble — all port intact; yoked was already "supporting, not load-bearing" per the shipped code.)

**Why B referents stay harness-drawn even in free play**: any scheme where the engine's referent is derivable from history lets the human answer without reading the display. It would also, correctly, trip the dscramble audit and void the session — so the design forbids it rather than letting the audit catch it.

## 3b. The capacity changes, exactly

**Channel.** `channel_trace(symbol, *, bits=1, seed, deaf=False)` and `channel(symbol, *, bits=1, ...)`:
- `bits=1`: byte-for-byte the current code path — 2-unit RING, TELL=200/HOLD=120, same RNG draws.
- `bits=3`: 6 units, `Wiring.PAIRS`, `chain=0.2`, `ALTERNATING` during TELL, then `FIXED` + `drive=0` during HOLD (deaf: `FIXED` throughout, drive bit-unreachable — the trick generalizes unchanged). Per-unit drive vector: pair *j* gets `(+0.8, −0.8)` if symbol-bit *j* is 0, else `(−0.8, +0.8)`. Envelope: **TELL₃=400** (the value `capacity.py` proved the 88% reproducible share under; the 1-bit 200 is *not* assumed to transfer), HOLD₃=120. Read: word = the 3 sign bits of `v[2j]−v[2j+1]`. A one-off `state/` calibration script pins per-bit latch fidelity ≥ 95% before these constants freeze; if TELL₃=400 misses that bar, only the `bits=3` constants move.

**`default-stays-exact` test**: 1,600 `channel(s, seed=k)` runs with the new parameter defaulted must equal the pre-change outputs bit-for-bit (the same pin the last landing used), plus a signature check that `bits=1` is the default. The published 1-bit numbers never move.

**Policies**: three send + three receive 2×2 tables per context, `reinforce` unchanged. Frozen snapshots are per-bit.

**Display**: direction B shows three stacked HOLD panels, one per pair. Session-fixed: within-pair markers *and* panel order (pair identity must be stable or the channel is unreadable, same reason markers exist). Per-trial randomized: toggle side-assignment and initial toggle states (position/default are not codecs). `display_payload` keeps its exact three-argument signature and `_DISPLAY_KEYS` allow-list; `trace` becomes three grouped pairs, `markers` six.

**dscramble, generalized**: on a dscramble probe, independently flip each pair's identity (curve order + markers) with probability ½ each, **and** apply a uniformly random permutation to the panel order — killing both layers of the display convention (within-pair polarity and panel→attribute assignment). Scoring never touches the trace; the flip changes only what the human can access. A test pins that all three flips and the permutation actually vary.

**`report-the-rank`, sized for 8 symbols**: beside every accuracy — per-bit support (each must be 2/2), joint signal/act support out of 8, the empirical signal entropy in bits on live probes, and the fixed line "보유 상태 폭 3비트 (래치 3개)". The verdict names **k-of-3**: a bit counts only if its own per-bit permutation clears α and its support is 2/2; the headline sentence claims exactly *k* bits, so 8 glyphs riding on one live latch reports as the 1-bit result it is, not a 3-bit result with poor accuracy.

## 4. The honest framing

**The sentence UI + RESULTS.md may claim** (per session, never averaged):

> *이 사람과 이 엔진이 자유 교환 속에서 사적 k비트(k ≤ 3) 관습을 확립하고 사용했다 — 눈가림 프로브 n·순열 p·채널 자체 충실도·귀무(day-0 / frozen / deaf / dscramble) 옆에. 언어도, 이해도 아니다.*

**The sentence it must not claim**: anything with 이해/의미/대화(무수식)/알아듣다 — and no "through consequence" for the free session (no yoked arm, §3). "대화" appears in the tab name only with its subtitle: **대화 — 3비트 사적 관습, 언어가 아님**.

**Where the line is**: a human-sense conversation has open semantics, productive composition, and meaning on both sides. Here the referent set is 8, closed, harness-fixed; composition was installed by the designer, not discovered; and all meaning lives in the human — the engine side is three reinforced 2×2 lookups and three physical latches. What is *real*: the exchange is live, two-way, private-to-this-history, physically carried, and each party's behavior demonstrably depends on the other's learned half (frozen null) through the wire (deaf null) via the display alone (dscramble).

**Guards against the human's pattern-completion** (the human is the overclaim vector now): mechanical per-attribute ✓/✗ only — no anthropomorphic feedback, no moods, no "엔진이 기뻐합니다"; the free-play tally permanently labeled 연습이며 증거 아님; the report screen leads with nulls and widths before accuracy; the k-of-3 verdict wording is generated from the stats, never hand-written.

## 5. Minimal first commit vs deferred

**Phase 1 — one commit, no further decisions:**
1. `channel`/`channel_trace` grow `bits=` (default 1) + the 1,600-run bit-exact pin + the calibration script in `state/communication/` (its fidelity number recorded in RESULTS.md before the tab ships).
2. `Conversation` engine class beside `DialogueSession` (shared primitives `pick`/`reinforce`/`display_payload` untouched): factorized policies, probe scheduler with balanced decks and the constants above, free-log + probe-log separation, generalized `session_stats` (joint + per-bit + k-of-3 + entropy/support), generalized dscramble, `insufficient_probes` verdict, one-shot `take_report`.
3. Viewer per `viewer-newengine`: handler + `_HANDLERS` + `Viewer.__init__` + `TICK_RATES`; tab **대화** with toggle composer, three-panel trace display, probe styling, Korean-only UI via `ko()`; session writer to `state/communication/sessions/`. Restart the viewer after landing (`viewer-restart`).
4. Tests: aperture audits (signatures + B-frame schema), lockstep, dscramble variation, per-bit stats on synthetic logs, stopping-rule/idempotent-submit behavior — mirroring `test_dialogue_session.py`.

**Deferred**: the engine-repeats-back verb (a genuine DMTS read of the held latches as a free-play "잘 들었어?" move — charming, but a new claim surface); any yoked analogue; Wilson intervals / Holm across 6 bit-tests / 99,999 permutations (already deferred for the rigid tab); adaptive probe pacing; a vocabulary-usage histogram in free play.

The first real session should still be run by the owner and stored whatever its verdict — `sessions/` stays honest by counting everything.

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
session id: 019f8dbc-402d-7983-a809-b7816be31a0d
--------
user
# Design task: turn the rigid measurement game into a genuine live CONVERSATION with a human — honestly

The owner just saw the `소통` tab (a viewer tab, Python research repo `anima-reborn`) and said, in
Korean: **"사람과 대화가 가능하게 하고 싶어" — "I want it to be possible to actually have a
conversation with a person."** Design how. Return a concrete, implementable design (data flow,
interaction shape, capacity choice, controls, stats, honesty framing), precise enough to implement
in one commit without further decisions. Do NOT write full code.

## What exists now (just shipped — read against it)

`src/anima_reborn/dialogue.py` holds `DialogueSession` + the channel primitives. It is a **rigid,
pre-scheduled Lewis-Skyrms 2x2 signaling GAME**: exactly 220 forced-choice trials laid out in fixed
blocks (day-0 / train / held-out test / yoked), interleaving two directions:
- Direction A (human->engine): a referent glyph is shown, the human clicks one of two signal buttons;
  the signal drives a 2-unit RING channel (`channel()`: TELL 200 ticks + HOLD 120 ticks, read the
  latch bit `sign(v0-v1)`), the engine acts via a learned 2x2 policy, success = (act == referent).
- Direction B (engine->human): the engine picks a signal for a hidden referent, the human is shown
  ONLY the raw HOLD trace (no latch, no sign — the "second aperture") and clicks which referent.
- Learning is reward-gated (`reinforce(policy, state, choice, reward)` — reads one agent's own locals
  only). Success is harness-computed. Per-session existence proof (never averaged over people):
  permutation test + nulls (day-0, frozen-engine echo, deaf channel, signal scramble,
  display-identity scramble, yoked). Verdicts: two_way / one_way / no_session_evidence / audit_failed.

This is a MEASUREMENT, not a conversation. It feels like a 220-question exam, one bit per turn.

## The hard constraint you MUST respect (this repo is brutally honest, and I will hold you to it)

The engine's PROVEN capacity, measured in this repo (`state/communication/RESULTS.md`, `capacity.py`):
- A single ring of ANY even width holds **exactly 1 bit** (a theorem: the per-unit response is odd,
  decreasing, bounded, so no orbit longer than 2). Widening the ring buys nothing.
- Capacity lives in the wiring's CYCLE STRUCTURE: **`Wiring.PAIRS`** (units/2 cross-coupled latches)
  with a weak inter-pair `chain=0.2` holds **units/2 bits AND measures as integrated** (6 units = 3
  bits, directed Phi held under 4x sampling where the disjoint null collapses). Only an ODD number of
  pairs integrates (even pairs form a macro-ring that locks). Each pair is addressed by its DIFFERENTIAL
  mode `d[2j]-d[2j+1]` — the common mode dies in silence.
- The engine is NOT language and NOT understanding. The repo's maximum honest sentence is: *"this
  person and this engine established and used a private N-bit convention through consequence."* It has
  earned "holds a bit through silence" and "its own response depends on whether a probe agrees with
  what it holds" (delayed match-to-sample), and (with `align.py`) that co-occurrence-learned concepts
  survive the engine — but NOTHING experience-adjacent, no topics, no meaning-in-the-human-sense.

So a "conversation" here can NEVER be linguistic. The honest ceiling is a **live, two-way,
consequence-driven exchange of a few bits per turn, where a shared convention forms and is used, and
the human can feel it working.** Your job is to make that AS MUCH LIKE A CONVERSATION AS HONESTY
ALLOWS — and to say exactly where the line is.

## The interpretation fork — address ALL THREE, then recommend one

1. **Free-form live mode.** Replace/augment the 220-trial exam with an open, continuous back-and-forth:
   the human and engine take turns, no fixed schedule, the convention forms organically and gets USED,
   the human sees each exchange land or fail in real time. Still ~1 bit/turn. How does a "turn" work
   from the human's side? How does it FEEL like talking rather than testing? How do you keep the
   apertures sealed and success harness-computed WITHOUT a pre-registered block schedule (the honesty
   machinery currently depends on fixed blocks + permutation)? Can a free session still yield an honest
   per-session verdict, or does measurement require a separate "measured" phase bolted onto the free play?

2. **Capacity increase (richer vocabulary).** Move the channel from the 1-bit ring to the proven 3-bit
   `Wiring.PAIRS` (3 odd pairs, chain=0.2), so a "message" carries 3 bits = up to 8 distinct referents
   — a small VOCABULARY instead of a coin flip. What exactly changes: the channel (drive 6 units, read
   3 differential latches), the policies (now over 8 symbols/referents), the display (3 pairs of
   traces), the game. Does the existing 1-bit machinery generalize, or does 8-way blow up the trial
   counts / permutation? Keep `default-stays-exact` (a new wiring param must default to leaving the
   published 1-bit numbers BIT-identical, pinned by a test). What's the honest new sentence ("a private
   3-bit convention")? Watch the `report-the-rank` trap — 8 symbols that collapse to 2 effective is not
   3 bits.

3. **Both** — a free-form 3-bit conversation. Is this coherent, or does combining them multiply the
   risk (harder to measure, harder to keep honest)? If both, what's the minimal honest version?

## What I need — answer each explicitly

1. **Which interpretation** best serves "사람과 대화가 가능하게" while staying honest, and why. Give a
   one-line dissent if you'd pick differently from the obvious.
2. **The turn, concretely.** What one exchange looks like from the human's side in your chosen design —
   what they see, what they do, what the engine does back, how they know it worked. Make it feel like a
   loop between two parties, not a questionnaire.
3. **How measurement survives.** The current honesty rests on fixed blocks + a permutation test + the
   null battery (echo/deaf/scramble/display-scramble). If the interaction becomes free/organic, how do
   you still ship an honest per-session verdict with its nulls? (A "free play, then a short blind
   measured probe" split? A rolling permutation on the free log? Be specific.)
3b. **If capacity increases**, the exact channel/policy/display changes, the `default-stays-exact`
   test that keeps the 1-bit path bit-identical, and the rank/width report that stops an 8-symbol code
   collapsing to fewer effective bits.
4. **The honest framing.** The precise sentence the UI and RESULTS.md may claim, and the sentence they
   must NOT. Where exactly is the line between "a real-time two-way convention" and "a conversation" in
   the human sense — and how do you keep the UI from letting the human's pattern-completion overclaim?
5. **Minimal first commit.** The smallest version that delivers "it feels like talking with it" AND
   keeps every honesty rule (apertures sealed, harness-computed success, nulls, rank-beside-accuracy,
   never averaged over people). What's phase 1 vs deferred.

Honesty discipline you must keep: ship every claim with the null that could fake it; report the
effective rank/width beside any accuracy; a lossy stage can't create what wasn't fed to it; the display
is a channel scored before crediting what leaves it; never average over people; the engine is not
language.

codex
I’ll inspect the shipped dialogue, capacity, and reporting code first so the proposal uses the repo’s actual seams and can be implemented without hidden design choices.
  → Inspect dialogue, capacity, UI, tests, and RESULTS contracts
  • Map the three interpretations and select the minimal honest architecture
  • Specify turn flow, measurement/nulls, 3-bit generalization, framing, and first commit
exec
/bin/zsh -lc "pwd && rg --files | rg '("'^|/)(AGENTS'"\\.md|dialogue\\.py|capacity\\.py|align\\.py|RESULTS\\.md|.*dialog.*|.*viewer.*|.*communication.*|test.*\\.py)"'$'"' | head -200" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
/Users/mini/dancinlab/anima-reborn
src/anima_reborn/dialogue.py
src/anima_reborn/viewer/CLAUDE.md
src/anima_reborn/viewer/__main__.py
src/anima_reborn/viewer/__init__.py
src/anima_reborn/viewer/server.py
src/anima_reborn/viewer/page.html
src/anima_reborn/align.py
state/communication/attractor_canonicalization.py
state/communication/match.py
state/communication/concepts.py
state/communication/dialogue.py
state/communication/alternating_coupling.py
state/communication/RESULTS.md
state/communication/sessions/README.md
state/communication/aligned_drive.py
state/communication/capacity.py
state/communication/silence.py
state/communication/integration_vs_representation.py
state/coupling/RESULTS.md
state/lab/2026-07-23-dialogue-viewer-prompt.md
state/lab/2026-07-23-dialogue-viewer-both.md
state/lab/2026-07-22-communication-divergence-fable.md
state/lab/2026-07-22-communication-divergence-pilot.py
state/lab/2026-07-22-communication-divergence-prompt.md
tests/test_dialogue.py
tests/test_pipeline.py
tests/test_info.py
tests/test_base.py
tests/test_coupled.py
tests/test_align.py
tests/test_viewer.py
tests/test_dialogue_session.py
tests/test_substrate.py
tests/test_repulsion.py
tests/test_rhythm.py
tests/test_words.py
tests/test_crystal.py
tests/test_iit4.py
tests/test_emergence.py
tests/test_directed.py

exec
/bin/zsh -lc "wc -l src/anima_reborn/dialogue.py tests/test_dialogue.py tests/test_dialogue_session.py state/communication/capacity.py state/communication/RESULTS.md src/anima_reborn/viewer/server.py src/anima_reborn/viewer/page.html src/anima_reborn/viewer/CLAUDE.md && sed -n '1,260p' src/anima_reborn/dialogue.py && sed -n '261,620p' src/anima_reborn/dialogue.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
     627 src/anima_reborn/dialogue.py
      59 tests/test_dialogue.py
     155 tests/test_dialogue_session.py
     152 state/communication/capacity.py
     805 state/communication/RESULTS.md
     731 src/anima_reborn/viewer/server.py
    1191 src/anima_reborn/viewer/page.html
      85 src/anima_reborn/viewer/CLAUDE.md
    3805 total
"""Human<->engine dialogue — the live half, where a person takes the partner's seat.

The reproducible half (a SYNTHETIC seeded partner, 12-seed directional bars, every
null) lives in `state/communication/dialogue.py`, which imports the channel
primitives (`channel`, `pick`, `reinforce`) from HERE — a capability in `src/` is the
one the state script re-derives, not a copy of it. This module adds `DialogueSession`:
the same Lewis-Skyrms 2x2 signaling game with a real HUMAN in the partner's seat, run
one session at a time from the viewer.

A human is not seedable and cannot be a controlled variable, so the human claim is a
PER-SESSION existence proof, never averaged over people. One session carries its own
day-0 block, its own yoked block, and a permutation test on its own log.

Two apertures must not encode the answer, matching the two mouths of the
experimenter-owned interpreter:

- the update rule reads only ONE agent's own (state, choice, success):
  `reinforce(policy, state, choice, reward)` has no argument for the other agent's
  state. Static audit — a test inspects the signature.
- the display is the second aperture. In direction B the human is shown ONLY the raw
  HOLD trace (never the TELL drive it was given, never the latch bit, never a derived
  sign), through `display_payload`, whose signature likewise cannot reach the referent,
  the signal, the word, or the success. Button positions are randomized per trial so
  screen position is not a covert codec.

Success is computed by the harness (`act == referent`) inside the session — neither the
human nor the engine ever grades its own intention. The echo trap (the engine handing
the human's bit back so "recovery" measures the human's self-consistency) is caught by
a frozen day-0 policy snapshot evaluated as a counterfactual on the same recorded human
action: with the engine's LEARNED half removed, a trained human must collapse to chance.

The maximum sentence a perfect session earns is small: *this* person and *this* engine
established and used a private 1-bit convention through consequence — reported beside its
day-0, frozen, deaf, scramble, yoked and permutation numbers, and nothing more. Not
understanding, not language.
"""

from __future__ import annotations

import copy
import random
import statistics
from typing import Any

from .coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

__all__ = [
    "TELL",
    "HOLD",
    "RATE",
    "channel",
    "channel_trace",
    "pick",
    "reinforce",
    "display_payload",
    "session_stats",
    "DialogueSession",
]

TELL = 200
HOLD = 120
RATE = 0.3


def channel_trace(signal: int, *, seed: int, deaf: bool = False) -> list[tuple[float, float]]:
    """The engine as a noisy 1-bit wire, returning the whole HOLD trajectory.

    A signal drives the 2-unit ring during a TELL phase; then the drive is cut and the
    coupling frozen, and the ring is read over a HOLD phase. This returns the HOLD
    trajectory itself — the raw thing the human sees, with no sign, no difference, no
    latch derived for them. `deaf` sets coupling to 1.0 for the whole run so the drive
    is bit-for-bit unreachable, which is the null proving the channel was in the path.

    Stepping HOLD times one at a time draws the same WALK noise sequence as
    `engine.run(HOLD)`, so the final values — and therefore `channel`'s latch bit — stay
    bit-identical to the reproducible harness's original `_channel`.
    """
    drive = (0.8, -0.8) if signal == 0 else (-0.8, 0.8)
    engine = CoupledEngine(
        units=2, wiring=Wiring.RING,
        rhythm=FIXED if deaf else ALTERNATING,
        drive=drive, seed=seed, initial=(0.0, 0.0),
    )
    engine.run(TELL)
    engine.rhythm = FIXED
    engine.drive = 0.0
    trace: list[tuple[float, float]] = []
    for _ in range(HOLD):
        values = engine.step().values
        trace.append((values[0], values[1]))
    return trace


def channel(signal: int, *, seed: int, deaf: bool = False) -> int:
    """Hold a signal, read the latch bit — `sign(v0 - v1)` of the final HOLD state.

    This is the receiver the published numbers and the frozen-policy null were measured
    against (a learned policy over this bit, not a less-revision probe). The viewer reuses
    it unchanged rather than implementing a different receiver.
    """
    final = channel_trace(signal, seed=seed, deaf=deaf)[-1]
    return 0 if (final[0] - final[1]) > 0 else 1


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
    a single policy and cannot reach the other agent — the static audit is that this
    signature has no argument for anyone else's state."""
    policy[state][choice] += RATE * reward


# The strict allow-list for a direction-B pre-action frame. The human must not be told
# the answer, so nothing here may encode the referent, the signal, the latch word, or the
# success. Pinned by the aperture audit test.
_DISPLAY_KEYS = frozenset({"trace", "markers", "buttons"})


def display_payload(
    trace: list[tuple[float, float]],
    markers: list[str],
    buttons: list[str],
) -> dict[str, Any]:
    """Build the direction-B frame the human reads — the second aperture.

    Its ONLY inputs are the raw HOLD trace, the neutral per-session unit->marker
    bijection, and the (already randomized) button order. There is no argument for the
    referent, the signal, the latch word, or the success — a lossy display cannot leak an
    answer it was never handed. The two markers keep unit identity stable across trials
    (the 1-bit channel would be unreadable if the units were re-shuffled every trial),
    while positions are randomized so screen position is not a covert codec.
    """
    return {
        "trace": [[round(u0, 4), round(u1, 4)] for u0, u1 in trace],
        "markers": list(markers),
        "buttons": list(buttons),
    }


# ── one live session ────────────────────────────────────────────────────────────────

# Block schedule (trials per direction). Small enough to finish in ~10-15 minutes, with
# every block×direction stratum carrying balanced referents so the permutation preserves
# the human's own response bias.
DAY0_PER_DIR = 12
TRAIN_PER_DIR = 30
TEST_LIVE_PER_DIR = 24
TEST_NULL_B_PER_ARM = 8  # dedicated frozen / deaf B trials (the human must act on a trace)
YOKED_TRAIN_PER_DIR = 20
YOKED_TEST_PER_DIR = 12

_MAIN = "main"
_YOKED = "yoked"
_A = "a"  # human -> engine (human sends a signal for a shown referent)
_B = "b"  # engine -> human (human reads the held trace and names the referent)


def _balanced(rng: random.Random, n: int) -> list[int]:
    """A shuffled sequence of n referents with the two values as balanced as n allows."""
    seq = [i % 2 for i in range(n)]
    rng.shuffle(seq)
    return seq


class DialogueSession:
    """One person, one fresh game, one append-only log — never combined with another.

    Presented as a viewer engine: `step()` is the drain (it resolves a submitted trial
    and advances; with nothing pending it is a bit-exact no-op), and `reset()` starts a
    fresh session. It waits on human input rather than free-running, so its tick rate is
    an input-latency bound, not a simulation rate. All I/O stays in the viewer layer —
    the session only accumulates its log in memory and hands it over once, on completion.
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

        # Per-session vocabulary and the neutral unit markers. Which glyph is referent 0
        # and which marker is unit 0 are the session's own draw, not the experimenter's.
        pool_ref = ["●", "▲", "■", "◆"]
        pool_sig = ["ㄱ", "ㄴ", "ㄷ", "ㄹ"]
        self._rng.shuffle(pool_ref)
        self._rng.shuffle(pool_sig)
        markers = ["◇", "○"]
        if self._rng.random() < 0.5:
            markers = markers[::-1]
        self._vocab = {
            _MAIN: {"ref": pool_ref[0:2], "sig": pool_sig[0:2], "markers": markers},
            _YOKED: {"ref": pool_ref[2:4], "sig": pool_sig[2:4], "markers": markers[::-1]},
        }

        # Four uniform policies at day-0, so which convention forms is the session's own
        # history. The human has NO server-side policy — the human learns in their head.
        self._recv = {_MAIN: _uniform(), _YOKED: _uniform()}
        self._send = {_MAIN: _uniform(), _YOKED: _uniform()}
        # The echo control: the engine's day-0 map, frozen and never updated.
        self._frozen_recv = copy.deepcopy(self._recv[_MAIN])
        self._frozen_send = copy.deepcopy(self._send[_MAIN])

        self._schedule = self._build_schedule()
        self._cursor = 0
        self._log: list[dict[str, Any]] = []
        self._last_feedback: int | None = None
        self._report: dict[str, Any] | None = None
        self._report_taken = False
        self._pending: dict[str, Any] | None = None
        self._submitted: dict[str, Any] | None = None
        self._open_trial()

    def _build_schedule(self) -> list[dict[str, Any]]:
        rng = self._rng
        trials: list[dict[str, Any]] = []

        def add(block: str, direction: str, context: str, count: int, arm: str = "live") -> None:
            for referent in _balanced(rng, count):
                trials.append(
                    {"block": block, "dir": direction, "ctx": context, "ref": referent, "arm": arm}
                )

        add("day0", _A, _MAIN, DAY0_PER_DIR)
        add("day0", _B, _MAIN, DAY0_PER_DIR)
        add("train", _A, _MAIN, TRAIN_PER_DIR)
        add("train", _B, _MAIN, TRAIN_PER_DIR)
        # The held-out test: live A/B, plus dedicated frozen/deaf B trials the human must
        # act on. Direction-A frozen/deaf/scramble come free as counterfactuals at resolve
        # time (same recorded human signal), so they need no schedule rows.
        add("test", _A, _MAIN, TEST_LIVE_PER_DIR)
        add("test", _B, _MAIN, TEST_LIVE_PER_DIR)
        add("test", _B, _MAIN, TEST_NULL_B_PER_ARM, arm="frozen")
        add("test", _B, _MAIN, TEST_NULL_B_PER_ARM, arm="deaf")
        add("test", _B, _MAIN, TEST_NULL_B_PER_ARM, arm="dscramble")
        # Yoked: a second convention attempt on a FRESH engine and new vocabulary, reward a
        # coin — runs last, when the now-practiced human would help if anything could, so it
        # is the conservative direction.
        add("yoked_train", _A, _YOKED, YOKED_TRAIN_PER_DIR)
        add("yoked_train", _B, _YOKED, YOKED_TRAIN_PER_DIR)
        add("yoked_test", _A, _YOKED, YOKED_TEST_PER_DIR)
        add("yoked_test", _B, _YOKED, YOKED_TEST_PER_DIR)

        # Shuffle within each contiguous block so arms and directions interleave and the
        # human cannot read a per-block strategy, while blocks stay in order.
        out: list[dict[str, Any]] = []
        i = 0
        while i < len(trials):
            j = i
            block = trials[i]["block"]
            while j < len(trials) and trials[j]["block"] == block:
                j += 1
            chunk = trials[i:j]
            rng.shuffle(chunk)
            out.extend(chunk)
            i = j
        return out

    # -- trial machinery ---------------------------------------------------------------

    def _open_trial(self) -> None:
        if self._cursor >= len(self._schedule):
            self._pending = None
            self._finish()
            return
        spec = self._schedule[self._cursor]
        self._nonce += 1
        ctx = spec["ctx"]
        vocab = self._vocab[ctx]
        # Randomize which option sits on the left each trial: position is not a codec.
        order = [0, 1]
        self._rng.shuffle(order)
        channel_seed = self._channel_base + self._cursor * 13 + 1
        pending: dict[str, Any] = {
            "nonce": self._nonce,
            "spec": spec,
            "order": order,
            "channel_seed": channel_seed,
        }
        if spec["dir"] == _A:
            # Human sends: the referent is legitimately shown (they send FOR it). Options
            # are the two signal glyphs, in randomized order.
            pending["options"] = [vocab["sig"][k] for k in order]
        else:
            # Engine sends: pick a signal, run the channel, show ONLY the raw trace. The
            # options are the two referent glyphs, in randomized order.
            arm = spec["arm"]
            send_policy = self._frozen_send if arm == "frozen" else self._send[ctx]
            signal = pick(send_policy[spec["ref"]], self._rng)
            deaf = arm == "deaf"
            trace = channel_trace(signal, seed=channel_seed, deaf=deaf)
            # Display-identity scramble (the second-aperture null): on a `dscramble` trial
            # flip the two units' identity — both curve order and marker — with prob 1/2,
            # holding the referent, engine policy and buttons fixed. If the human's reading
            # is really the learned display convention, this must destroy it (the arm sits
            # at chance); if recovery survives, some unlogged cue leaks and the session is
            # `audit_failed`. Scoring never touches the trace, so flipping the shown copy
            # changes only what the human can access, not the truth `act == referent`.
            markers = list(vocab["markers"])
            display_trace = trace
            swapped = arm == "dscramble" and self._rng.random() < 0.5
            if swapped:
                markers = markers[::-1]
                display_trace = [(u1, u0) for u0, u1 in trace]
            pending["signal"] = signal
            pending["trace"] = trace
            pending["markers_swapped"] = swapped
            pending["display"] = display_payload(
                display_trace, markers, [vocab["ref"][k] for k in order]
            )
        self._pending = pending
        self._submitted = None

    def submit(self, nonce: int, choice: int) -> bool:
        """Record the human's choice for the current pending trial.

        Idempotent: a submission whose nonce is not the live pending nonce (a stale or
        double-clicked request) is ignored, so the log can never gain two entries for one
        trial. Returns whether it was accepted.
        """
        if self._pending is None or self._submitted is not None:
            return False
        if nonce != self._pending["nonce"]:
            return False
        if choice not in (0, 1):
            return False
        self._submitted = {"choice": int(choice)}
        return True

    def step(self) -> "DialogueSession":
        """Resolve a submitted trial and advance. A no-op when nothing is pending."""
        if self._pending is None or self._submitted is None:
            return self
        self._resolve(self._pending, self._submitted["choice"])
        self._cursor += 1
        self._open_trial()
        return self

    def _resolve(self, pending: dict[str, Any], choice: int) -> None:
        spec = pending["spec"]
        ctx = spec["ctx"]
        referent = spec["ref"]
        block = spec["block"]
        arm = spec["arm"]
        learning = block in ("train", "yoked_train")
        # Coin reward decouples consequence from success in the yoked block.
        coin = self._rng.random() < 0.5
        chosen = pending["order"][choice]  # option index -> identity index (0/1)
        entry: dict[str, Any] = {
            "block": block, "dir": spec["dir"], "ctx": ctx, "arm": arm,
            "referent": referent, "nonce": pending["nonce"],
        }

        if spec["dir"] == _A:
            signal = chosen
            word = channel(signal, seed=pending["channel_seed"])
            act = pick(self._recv[ctx][word], self._rng)
            success = int(act == referent)
            entry.update(signal=signal, word=word, act=act, success=success)
            # Counterfactual receivers on the SAME human signal — free nulls for A.
            if block in ("test", "yoked_test"):
                fword = channel(signal, seed=pending["channel_seed"])
                entry["frozen_success"] = int(
                    pick(self._frozen_recv[fword], self._rng) == referent
                )
                dword = channel(signal, seed=pending["channel_seed"], deaf=True)
                entry["deaf_success"] = int(
                    pick(self._recv[ctx][dword], self._rng) == referent
                )
                scrambled = self._rng.randrange(2)
                sword = channel(scrambled, seed=pending["channel_seed"])
                entry["scramble_success"] = int(
                    pick(self._recv[ctx][sword], self._rng) == referent
                )
            if learning:
                reward = float(coin) if block == "yoked_train" else float(success)
                reinforce(self._recv[ctx], word, act, reward)
        else:
            act = chosen  # the human's named referent
            success = int(act == referent)
            entry.update(
                signal=pending["signal"], act=act, success=success,
                markers_swapped=pending.get("markers_swapped", False),
            )
            if learning:
                reward = float(coin) if block == "yoked_train" else float(success)
                reinforce(self._send[ctx], referent, pending["signal"], reward)

        self._log.append(entry)
        # Feedback is surfaced only in learning blocks; measure blocks carry none.
        self._last_feedback = success if learning else None

    def _finish(self) -> None:
        if self._report is None:
            self._report = session_stats(self._log, vocab=self._vocab)

    # -- viewer read-side --------------------------------------------------------------

    @property
    def phase(self) -> str:
        if self._report is not None:
            return "done"
        return "measure" if self._is_measure() else "learn"

    def _is_measure(self) -> bool:
        if self._pending is None:
            return True
        return self._pending["spec"]["block"] not in ("train", "yoked_train")

    def describe(self) -> dict[str, Any]:
        """A read-only frame. In measure blocks it carries no success and no running
        tally — a live score would be feedback. The true arm/block truth stays in the log,
        never in the frame."""
        total = len(self._schedule)
        frame: dict[str, Any] = {
            "phase": self.phase,
            "round": min(self._cursor + (0 if self._pending is None else 1), total),
            "total": total,
            "token": self._token,
        }
        if self._pending is not None:
            spec = self._pending["spec"]
            ctx = spec["ctx"]
            vocab = self._vocab[ctx]
            pend: dict[str, Any] = {
                "nonce": self._pending["nonce"],
                "dir": spec["dir"],
                "buttons": self._pending["options"] if spec["dir"] == _A else self._pending["display"]["buttons"],
            }
            if spec["dir"] == _A:
                pend["referent"] = vocab["ref"][spec["ref"]]
            else:
                pend["trace"] = self._pending["display"]["trace"]
                pend["markers"] = self._pending["display"]["markers"]
            frame["pending"] = pend
            frame["learning"] = spec["block"] in ("train", "yoked_train")
            frame["feedback"] = self._last_feedback if frame["learning"] else None
        if self._report is not None:
            frame["report"] = self._report
        return frame

    def take_report(self) -> dict[str, Any] | None:
        """Hand the finished session's log+report to the viewer for one write, once.

        In-memory only — the flip is not I/O, so the engine stays I/O-free; the caller
        (the viewer handler) owns the file write.
        """
        if self._report is None or self._report_taken:
            return None
        self._report_taken = True
        return {"report": self._report, "log": self._log, "token": self._token}


def _uniform() -> list[list[float]]:
    return [[1.0, 1.0], [1.0, 1.0]]


# ── the per-session statistics ──────────────────────────────────────────────────────

_PERMUTATIONS = 10000


def _accuracy(rows: list[dict[str, Any]], key: str = "success") -> tuple[int, int]:
    hits = sum(int(r[key]) for r in rows if key in r)
    n = sum(1 for r in rows if key in r)
    return hits, n


def _permutation_p(rows: list[dict[str, Any]]) -> tuple[float, float]:
    """Permute the referent labels (balanced, so margins hold) and recompute accuracy
    with the human's/engine's actions fixed. The null: after preserving this session's own
    response bias, referents are exchangeable with respect to the recorded actions."""
    if not rows:
        return 0.0, 1.0
    acts = [r["act"] for r in rows]
    referents = [r["referent"] for r in rows]
    obs = statistics.mean(int(a == b) for a, b in zip(acts, referents))
    rng = random.Random(1234567)  # analysis RNG — the human was never seeded
    perm = list(referents)
    ge = 0
    for _ in range(_PERMUTATIONS):
        rng.shuffle(perm)
        acc = statistics.mean(int(a == b) for a, b in zip(acts, perm))
        if acc >= obs:
            ge += 1
    return obs, (1 + ge) / (1 + _PERMUTATIONS)


def _support(rows: list[dict[str, Any]], key: str) -> int:
    """How many of the two symbols the code actually used — the WIDTH beside the accuracy.
    A code collapsed to one symbol scores against a degenerate null and carries nothing."""
    return len({r[key] for r in rows if key in r})


def session_stats(log: list[dict[str, Any]], *, vocab: dict[str, Any] | None = None) -> dict[str, Any]:
    """Turn one person's log into per-direction verdicts. Directions are never averaged;
    sessions are never pooled. Every accuracy ships with its counts, its symbol supports,
    and the note that the held state is one bit wide however many samples it was drawn as."""
    alpha = 0.05

    def block(name: str, direction: str, arm: str = "live") -> list[dict[str, Any]]:
        return [r for r in log if r["block"] == name and r["dir"] == direction and r["arm"] == arm]

    directions: dict[str, Any] = {}
    for direction in (_A, _B):
        live = block("test", direction)
        obs, p = _permutation_p(live)
        hits, n = _accuracy(live)
        day0 = _accuracy(block("day0", direction))
        yoked = _accuracy(block("yoked_test", direction))
        # Nulls: direction A gets its counterfactual arms free; direction B uses dedicated
        # frozen/deaf trials.
        if direction == _A:
            frozen = _accuracy(live, "frozen_success")
            deaf = _accuracy(live, "deaf_success")
            scramble = _accuracy(live, "scramble_success")
            dscramble = (0, 0)  # display leak is a direction-B concern (A shows the referent)
        else:
            frozen = _accuracy(block("test", direction, arm="frozen"))
            deaf = _accuracy(block("test", direction, arm="deaf"))
            scramble = (0, 0)
            dscramble = _accuracy(block("test", direction, arm="dscramble"))
        sig_support = _support(live, "signal")
        act_support = _support(live, "act")

        def rate(pair: tuple[int, int]) -> float | None:
            return None if pair[1] == 0 else pair[0] / pair[1]

        nulls = {
            "day0": day0, "frozen": frozen, "deaf": deaf,
            "scramble": scramble, "dscramble": dscramble, "yoked": yoked,
        }
        # The hard gate is the permutation test plus the STRUCTURAL nulls that must sit at
        # chance: day-0 (a display leak would lift it), frozen (the echo — the engine's
        # learned half must be load-bearing), deaf (the channel must be in the path), and
        # for direction B the display-identity scramble (the targeted second-aperture null,
        # better powered than the 12-trial day-0). scramble and yoked are reported beside as
        # diagnostics, not gates — yoked is supporting, not the load-bearing null (fable).
        structural = (rate(day0), rate(frozen), rate(deaf), rate(dscramble))
        structural_ok = all(r is None or r <= 0.65 for r in structural)
        support_ok = sig_support == 2 and act_support == 2
        formed = obs > 0.5 and p <= alpha and support_ok and structural_ok
        directions[direction] = {
            "hits": hits, "n": n, "accuracy": obs, "p": p,
            "signal_support": sig_support, "act_support": act_support,
            "width_bits": 1,
            "nulls": {k: {"hits": v[0], "n": v[1], "rate": rate(v)} for k, v in nulls.items()},
            "verdict": "formed" if formed else "no_evidence",
        }

    # Cross-direction consistency: does the human's send code (A, from training) agree with
    # the engine's send code (B)? Reported as k/2 — never folded into accuracy, never called
    # a symmetric language.
    consistency = _cross_consistency(log)

    # A high display-identity-scramble null means the human read the answer through a cue
    # we did not intend (a leak), so any positive B accuracy is not communication evidence —
    # the whole session verdict is voided, not just direction B.
    dscramble_rate = directions[_B]["nulls"]["dscramble"]["rate"]
    audit_failed = dscramble_rate is not None and dscramble_rate > 0.65

    both = directions[_A]["verdict"] == "formed" and directions[_B]["verdict"] == "formed"
    if audit_failed:
        verdict = "audit_failed"
    elif both:
        verdict = "two_way_session_evidence"
    elif directions[_A]["verdict"] == "formed" or directions[_B]["verdict"] == "formed":
        verdict = "one_way_session_evidence"
    else:
        verdict = "no_session_evidence"

    return {
        "a": directions[_A],
        "b": directions[_B],
        "cross_direction_consistency": consistency,
        "verdict": verdict,
        "permutations": _PERMUTATIONS,
        "alpha": alpha,
    }


def _cross_consistency(log: list[dict[str, Any]]) -> float:
    """Compare the human's dominant referent->signal map (from training A) with the engine's
    dominant referent->signal map (from training B)."""
    human: dict[int, list[int]] = {0: [0, 0], 1: [0, 0]}
    engine: dict[int, list[int]] = {0: [0, 0], 1: [0, 0]}
    for r in log:
        if r["block"] != "train":
            continue
        if r["dir"] == _A:
            human[r["referent"]][r["signal"]] += 1
        else:
            engine[r["referent"]][r["signal"]] += 1

    def dominant(counts: list[int]) -> int | None:
        if counts[0] == counts[1]:
            return None
        return 0 if counts[0] > counts[1] else 1

    agree = 0
    seen = 0
    for referent in (0, 1):

exec
/bin/zsh -lc "sed -n '620,700p' src/anima_reborn/dialogue.py; sed -n '1,240p' tests/test_dialogue_session.py; sed -n '1,220p' tests/test_dialogue.py; sed -n '1,240p' state/communication/capacity.py; rg -n \"PAIRS|chain|capacity|dialogue|소통|rank|width|private|convention|language|integrat\" state/communication/RESULTS.md src/anima_reborn/viewer/server.py src/anima_reborn/viewer/page.html tests/test_viewer.py src/anima_reborn/coupled.py | head -300" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
    for referent in (0, 1):
        h = dominant(human[referent])
        e = dominant(engine[referent])
        if h is None or e is None:
            continue
        seen += 1
        agree += int(h == e)
    return agree / seen if seen else 0.5
"""The live human<->engine dialogue session and its two structural audits.

`DialogueSession` puts a real human in the partner's seat; the reproducible half (a
synthetic partner) is tested in `test_dialogue.py`. These pin the two apertures that must
not encode the answer — the update rule cannot see across the gap, and the display frame
cannot carry the referent — plus the session mechanics the viewer depends on: idempotent
submission, a no-op step with nothing pending, and a self-contained per-session verdict.
"""

from __future__ import annotations

import inspect

from anima_reborn import dialogue
from anima_reborn.dialogue import DialogueSession, channel, display_payload


def _play(session: DialogueSession, strategy) -> dict:
    """Drive a session to completion with a scripted human, returning its report."""
    steps = 0
    while session.phase != "done" and steps < 2000:
        pending = session._pending
        if pending is None:
            break
        session.submit(pending["nonce"], strategy(pending))
        session.step()
        steps += 1
    return session.describe()["report"]


class TestTheTwoAudits:
    def test_the_update_rule_reads_only_one_agents_locals(self) -> None:
        """The engine-side aperture: `reinforce` is handed one policy and one agent's own
        (state, choice, reward), with no argument for the other agent's state."""
        params = list(inspect.signature(dialogue.reinforce).parameters)
        assert params == ["policy", "state", "choice", "reward"], params

    def test_the_display_builder_cannot_reach_the_answer(self) -> None:
        """The display aperture: `display_payload`'s signature has no argument for the
        referent, the signal, the latch word, or the success."""
        params = list(inspect.signature(display_payload).parameters)
        assert params == ["trace", "markers", "buttons"], params

    def test_no_pre_action_b_frame_carries_the_answer(self) -> None:
        """Every direction-B frame the human is shown must contain only the raw trace, the
        neutral markers, and the buttons — never the referent, signal, word, or success."""
        forbidden = {"referent", "signal", "word", "act", "success", "ref", "arm"}
        session = DialogueSession(seed=1)
        seen_b = 0
        for _ in range(400):
            frame = session.describe()
            pending = frame.get("pending")
            if pending and pending["dir"] == "b":
                seen_b += 1
                assert set(pending) <= {"nonce", "dir", "buttons", "trace", "markers"}, pending
                assert not (set(pending) & forbidden), pending
            if session._pending is not None:
                session.submit(session._pending["nonce"], 0)
                session.step()
            if session.phase == "done":
                break
        assert seen_b > 0, "no direction-B trials were inspected"

    def test_the_b_trace_is_hold_only_never_the_drive(self) -> None:
        """The frame ships the HOLD trajectory (drive already cut), not the TELL phase —
        a lossy display cannot leak what it was never handed."""
        session = DialogueSession(seed=2)
        for _ in range(400):
            pending = session._pending
            if pending is None:
                break
            if pending["spec"]["dir"] == "b":
                assert len(pending["display"]["trace"]) == dialogue.HOLD
            session.submit(pending["nonce"], 0)
            session.step()


class TestSessionMechanics:
    def test_submission_is_idempotent(self) -> None:
        session = DialogueSession(seed=3)
        nonce = session._pending["nonce"]
        assert session.submit(nonce, 0) is True
        assert session.submit(nonce, 1) is False, "a second submit was accepted"
        assert session.submit(9999, 0) is False, "a stale nonce was accepted"
        before = len(session._log)
        session.step()
        assert len(session._log) == before + 1, "one trial produced more than one log row"

    def test_a_step_with_nothing_pending_is_a_no_op(self) -> None:
        session = DialogueSession(seed=4)
        cursor, log = session._cursor, len(session._log)
        session.step()  # no submission yet
        assert session._cursor == cursor and len(session._log) == log

    def test_a_session_completes_and_reports_both_directions(self) -> None:
        report = _play(DialogueSession(seed=5), lambda p: 0)
        assert report["verdict"] in {
            "two_way_session_evidence", "one_way_session_evidence",
            "no_session_evidence", "audit_failed",
        }
        for key in ("a", "b"):
            assert report[key]["verdict"] in {"formed", "no_evidence"}
            assert report[key]["width_bits"] == 1
            assert 0.0 <= report[key]["p"] <= 1.0

    def test_the_report_is_handed_over_exactly_once(self) -> None:
        session = DialogueSession(seed=6)
        _play(session, lambda p: 0)
        assert session.take_report() is not None
        assert session.take_report() is None, "the completed log was handed over twice"

    def test_a_fixed_strategy_is_refused(self) -> None:
        """Always pressing the first button establishes no convention through consequence,
        so the honest verdict is no evidence — the gate does not reward a degenerate code."""
        report = _play(DialogueSession(seed=8), lambda p: 0)
        assert report["verdict"] == "no_session_evidence"


class TestTheDisplayScrambleNull:
    """The second aperture, guarded by its own targeted null: flipping the display's unit
    identity per trial must destroy a reading that depends on the learned display
    convention, and a reading that survives the flip (a leak) voids the whole session."""

    def test_the_scramble_arm_is_scheduled_and_actually_flips(self) -> None:
        session = DialogueSession(seed=1)
        _play(session, lambda p: 0)
        rows = [e for e in session._log if e.get("arm") == "dscramble"]
        assert rows, "no display-scramble trials were scheduled"
        assert all("markers_swapped" in e for e in rows)
        assert {e["markers_swapped"] for e in rows} == {True, False}, "the flip never varied"

    def test_a_display_bypass_reading_fails_the_audit(self) -> None:
        """A 'human' who reads the true latch directly — bypassing the display — keeps
        recovering even when the display identity is scrambled, so the session is voided
        as audit_failed rather than being quietly reported as no evidence."""
        def leak(pending: dict) -> int:
            order = pending["order"]
            if pending["spec"]["dir"] == "a":
                return order.index(pending["spec"]["ref"])
            bit = channel(pending["signal"], seed=pending["channel_seed"])
            return order.index(bit)

        report = _play(DialogueSession(seed=11), leak)
        assert report["verdict"] == "audit_failed", report["verdict"]
        assert report["b"]["nulls"]["dscramble"]["rate"] > 0.65


class TestTheEchoControl:
    def test_the_frozen_engine_snapshot_stays_at_day_zero(self) -> None:
        """The echo null: the frozen policies are the day-0 (uniform) map and never learn,
        so a trained human meeting them cannot have their own bit handed back."""
        session = DialogueSession(seed=7)
        _play(session, lambda p: 0)
        assert session._frozen_recv == [[1.0, 1.0], [1.0, 1.0]]
        assert session._frozen_send == [[1.0, 1.0], [1.0, 1.0]]
"""The reproducible half of human<->engine dialogue, with a synthetic partner.

A human is not seedable, so the reproducible claim is measured against a scripted
stand-in; the real human takes the partner's seat in the viewer later. These pin
that the engine's reward-gated policy forms a convention, that the engine's
learned half is load-bearing (not an echo), and that the update rule cannot see
across the gap. Full game in `state/communication/dialogue.py`.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "state" / "communication"))

import dialogue  # noqa: E402


class TestAConventionForms:
    def test_both_directions_beat_chance(self) -> None:
        dyads = [dialogue.play(s, episodes=400) for s in range(3)]
        assert statistics.mean(d["a"] for d in dyads) > 0.7
        assert statistics.mean(d["b"] for d in dyads) > 0.7

    def test_the_engines_learned_half_is_load_bearing_not_an_echo(self) -> None:
        """Frozen at its random day-0 map, the engine cannot recover with a fully
        trained partner — so the code is not the engine handing the bit back."""
        frozen = [dialogue.play(s, episodes=400, frozen_engine=True)["a"] for s in range(3)]
        assert statistics.mean(frozen) < 0.6, frozen

    def test_the_consequence_establishes_it(self) -> None:
        yoked = [dialogue.play(s, episodes=400, yoked=True)["a"] for s in range(3)]
        assert statistics.mean(yoked) < 0.6, yoked

    def test_the_convention_is_private_to_the_pair(self) -> None:
        dyads = [dialogue.play(s, episodes=400) for s in range(3)]
        within = statistics.mean(
            dialogue._probe(d["policies"], seed=i, direction="a")
            for i, d in enumerate(dyads)
        )
        cross = statistics.mean(
            dialogue._probe(
                (dyads[i]["policies"][0], dyads[j]["policies"][1], None, None),
                seed=i * 100 + j, direction="a",
            )
            for i in range(3) for j in range(3) if i != j
        )
        assert within > 0.7, within
        assert cross < 0.65, cross


class TestTheStaticAudit:
    def test_the_update_rule_reads_only_one_agents_locals(self) -> None:
        import inspect

        params = list(inspect.signature(dialogue._reinforce).parameters)
        assert params == ["policy", "state", "choice", "reward"], params
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
src/anima_reborn/coupled.py:7:anything else. That is why every one of them measures zero integration: with no
src/anima_reborn/coupled.py:20:through `substrate` and `iit4`, the ring integrates and the other two do not —
src/anima_reborn/coupled.py:27:*integration is now created, and created is all this measures*.
src/anima_reborn/coupled.py:38:trade off monotonically. Coupling low enough to represent the drive integrates
src/anima_reborn/coupled.py:39:nothing; coupling high enough to integrate lets the ring's own attractor swamp
src/anima_reborn/coupled.py:44:— listen with the coupling off, integrate with it on. Measured at a matched
src/anima_reborn/coupled.py:51:It does NOT integrate more. An earlier reading here said it did, and that
src/anima_reborn/coupled.py:88:"""a0, a1, g0, g1 — two dimensions of each engine, and the default width.
src/anima_reborn/coupled.py:92:capacity grows with the units and Phi stops being computable past six, so a
src/anima_reborn/coupled.py:93:wider engine is one whose integration cannot be checked. Nothing above six may
src/anima_reborn/coupled.py:94:be called integrated on the strength of a narrower engine's reading."""
src/anima_reborn/coupled.py:97:"""Unit names at the default width. `names_for` generalizes them."""
src/anima_reborn/coupled.py:101:    """`a0 a1 g0 g1` at the default width, `u0..uN` otherwise — a wider engine
src/anima_reborn/coupled.py:126:"""Coupling during a rhythm's integrate phase. Enough for the ring to be
src/anima_reborn/coupled.py:138:    that the ring's integration comes from its wiring, and the only way to show
src/anima_reborn/coupled.py:148:    PAIRS = "pairs"
src/anima_reborn/coupled.py:149:    """Cross-coupled pairs, each a two-unit latch, optionally chained.
src/anima_reborn/coupled.py:151:    A single ring of any EVEN width holds exactly one bit, and that is a
src/anima_reborn/coupled.py:155:    the ring therefore cannot buy capacity — measured at 4, 6 and 8 units, all
src/anima_reborn/coupled.py:172:        if self is Wiring.PAIRS:
src/anima_reborn/coupled.py:174:                raise ValueError(f"pairs needs an even width, got {units}")
src/anima_reborn/coupled.py:180:        """The default-width wiring, kept because it is what every published
src/anima_reborn/coupled.py:187:        return self in (Wiring.RING, Wiring.PAIRS)
src/anima_reborn/coupled.py:196:    integrates nothing; above it the ring integrates and its own attractor
src/anima_reborn/coupled.py:207:    """Coupling while the integrate phase is on, in [0, 1]."""
src/anima_reborn/coupled.py:238:        listen/integrate cycle: half a cycle would report one phase's transition
src/anima_reborn/coupled.py:263:"""Ten ticks listening, ten integrating. The measured wall-break."""
src/anima_reborn/coupled.py:316:        chain: How much of a unit's partner-response is replaced by the same
src/anima_reborn/coupled.py:343:        chain: float = 0.0,
src/anima_reborn/coupled.py:355:        if not 0.0 <= chain <= 1.0:
src/anima_reborn/coupled.py:356:            raise ValueError(f"chain must be in [0, 1], got {chain}")
src/anima_reborn/coupled.py:359:        self.chain = chain
src/anima_reborn/coupled.py:404:        default width is exactly the `(a0-g0)^2 + (a1-g1)^2` over two that every
src/anima_reborn/coupled.py:405:        published reading used. An odd width has no such split and reads 0.0 —
src/anima_reborn/coupled.py:444:            if self.chain:
src/anima_reborn/coupled.py:445:                # Left alone at chain 0, so the wirings are what they always
src/anima_reborn/coupled.py:452:                partner = (1.0 - self.chain) * partner + self.chain * along
state/communication/RESULTS.md:1:# 소통을 위해 엔진에 무엇이 필요한가 — 첫 측정
state/communication/RESULTS.md:3:2026-07-22 · 재현 스크립트 `state/communication/integration_vs_representation.py`
state/communication/RESULTS.md:4:(실행: 저장소 루트에서 `PYTHONPATH=src python state/communication/integration_vs_representation.py`)
state/communication/RESULTS.md:6:"소통하려면 엔진에 뭐가 필요한가"를 발산 위임하면서, 가장 값싸게 검증 가능한 씨앗
state/communication/RESULTS.md:48:## 이게 왜 소통 질문의 답인가
state/communication/RESULTS.md:50:소통하려면 **두 가지가 동시에** 필요하다. 하나여야 하고(통합 — 그래야 "누가" 이해한다),
state/communication/RESULTS.md:56:따라서 소통을 향한 어떤 설계든 **이 상충을 깨는 것**이 첫 관문이다. 상충의 기전도 이름이
state/communication/RESULTS.md:112:### 왜 이게 소통 질문에 걸리는가
state/communication/RESULTS.md:121:- 이건 **벽이 깨질 수 있다**는 증거이지, 소통이 된다는 증거가 아니다. 표상이 살아
state/communication/RESULTS.md:437:### 그런데 폭은 (`report-the-rank`)
state/communication/RESULTS.md:544:재현 스크립트 `state/communication/capacity.py`, 결정 IIT 실행은 `coupled_phi(Wiring.PAIRS, ...)`.
state/communication/RESULTS.md:558:**용량은 유닛 수가 아니라 배선의 순환 구조**다. 최대 `units/2` 개의 2-순환 = `Wiring.PAIRS`.
state/communication/RESULTS.md:571:쌍 사이 약한 사슬(`chain=0.2`)이 걸리면 환원 불가가 된다:
state/communication/RESULTS.md:603:`chain=0`(분리된 래치 3개)도 3비트를 담고 각 래치가 저장을 통과한다 — **환원가능인데도**.
state/communication/RESULTS.md:605:아니다. `chain=0` 을 일급 귀무로 넣었고, 통합이 **기능**이 되는 유일한 곳은 교차-쌍 탐침이다.
state/communication/RESULTS.md:609:`Wiring.PAIRS` 에서 쌍 j 는 유닛 (2j, 2j+1) 의 반전 2-순환이고, 그 **차동** `d[2j]−d[2j+1]`
state/communication/RESULTS.md:631:**그러나 저장은 통합을 필요로 하지 않는다**: `chain=0`(분리 래치, 환원가능)도 62% 로 똑같이
state/communication/RESULTS.md:643:`chain=0` 의 0 은 **구조적**이다 — 쌍 사이 인과 경로가 없으니 정확히 0. 비영 응답은 **통합된
state/communication/RESULTS.md:665:## 방향 전환 — 소통은 엔진끼리가 아니라 사람↔엔진 (2026-07-23)
state/communication/RESULTS.md:667:`state/communication/` 라인 전체를 **엔진끼리 소통**으로 좇았으나, 소유자가 정정했다: 소통은
state/communication/RESULTS.md:676:  귀무가 가능. 재현 스크립트 `state/communication/dialogue.py`.
state/communication/RESULTS.md:721:## 뷰어 `소통` 탭 — 사람이 파트너 자리에 앉는다 (라이브 절반 착지) (2026-07-23)
state/communication/RESULTS.md:724:`src/anima_reborn/dialogue.py` 로 올리고(상태 스크립트는 이제 그걸 import 한다 — 사본이 아니라
state/communication/RESULTS.md:726:수렴했다(보고서: `state/lab/2026-07-23-dialogue-viewer-*.md`).
state/communication/RESULTS.md:756:- `report-the-rank`: 모든 정확도 옆에 신호폭/행동폭과 "보유 1비트"를 함께 낸다. 한 기호로 붕괴한
state/communication/RESULTS.md:768:  완주 로그는 한 번만 넘어감 — 모두 테스트로 고정(`tests/test_dialogue_session.py`).
state/communication/RESULTS.md:799:이 판정 경로 둘 다 테스트로 고정(`tests/test_dialogue_session.py::TestTheDisplayScrambleNull`).
state/communication/RESULTS.md:801:`report-the-rank`/`claims-need-controls` 그대로 — 주장(디스플레이를 읽어 회복했다)마다 그걸 위조할
src/anima_reborn/viewer/server.py:44:from ..dialogue import DialogueSession
src/anima_reborn/viewer/server.py:54:"""Where a completed human dialogue session is written — git-tracked with the rest of the
src/anima_reborn/viewer/server.py:70:    "dialogue": 8.0,
src/anima_reborn/viewer/server.py:353:    """The live human dialogue session — the one interactive tab.
src/anima_reborn/viewer/server.py:394:    "dialogue": _DialogueHandler,
src/anima_reborn/viewer/server.py:509:            "dialogue": DialogueSession(seed=seed),
src/anima_reborn/viewer/page.html:5:<meta name="viewport" content="width=device-width, initial-scale=1">
src/anima_reborn/viewer/page.html:27:  .wrap { max-width: 1080px; margin: 0 auto; padding: 28px 20px 64px; }
src/anima_reborn/viewer/page.html:60:  .ctl input[type=range] { width: 168px; accent-color: var(--a); }
src/anima_reborn/viewer/page.html:61:  .ctl b { color: var(--text); font-variant-numeric: tabular-nums; min-width: 34px; font-weight: 600; }
src/anima_reborn/viewer/page.html:68:  canvas { display: block; width: 100%; border-radius: 8px; background: var(--inset); }
src/anima_reborn/viewer/page.html:71:  @media (max-width: 760px) { .grid2, .grid-scatter { grid-template-columns: 1fr; } }
src/anima_reborn/viewer/page.html:113:  <button class="tab" data-tab="dialogue">💬 소통</button>
src/anima_reborn/viewer/page.html:469:<section class="panel" id="p-dialogue">
src/anima_reborn/viewer/page.html:473:      재현 가능한 절반(합성 파트너·12시드·모든 귀무)은 <strong>state/communication/dialogue.py</strong>
src/anima_reborn/viewer/page.html:524:  if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
src/anima_reborn/viewer/page.html:525:    canvas.width = Math.round(w * dpr);
src/anima_reborn/viewer/page.html:534:function drawTrace(canvas, values, color, vrange, capacity) {
src/anima_reborn/viewer/page.html:542:  const denom = Math.max(1, (capacity || values.length) - 1);
src/anima_reborn/viewer/page.html:659:  // 소통 — 판정 원시값(raw)만 매핑, 배지 색은 raw 로 판정한다.
src/anima_reborn/viewer/page.html:695:const PREFIX = { emergence: "em", crystal: "cr", repulsion: "rp", pipeline: "pl", base: "bs", coupled: "cp", align: "al", dialogue: "dg" };
src/anima_reborn/viewer/page.html:714:  if (name === "dialogue") return {};   // no sliders — the human's choice goes via submitChoice
src/anima_reborn/viewer/page.html:724:  dgNonce = null;        // re-entering 소통 rebuilds the current trial's buttons
src/anima_reborn/viewer/page.html:774:  else if (name === "dialogue") renderDialogue(data);
src/anima_reborn/viewer/page.html:958:// ── 소통 (dialogue) ──────────────────────────────────────────────────────────
src/anima_reborn/viewer/page.html:964:  one_way_session_evidence: "이 세션에서는 한 방향의 1비트 관례 증거만 있습니다. 양방향 소통으로 보고하지 않습니다.",
src/anima_reborn/viewer/page.html:966:  audit_failed: "감사 대조군 실패 — 디스플레이 뒤섞기 귀무가 우연을 넘습니다. 화면이 답을 흘렸다는 뜻이라, 이 세션의 어떤 양성 정확도에도 소통 증거를 부여하지 않습니다.",
src/anima_reborn/viewer/page.html:1037:      fetch(`/api/dialogue/control?nonce=${p.nonce}&choice=${idx}`).catch(() => {});
src/anima_reborn/viewer/page.html:1049:    return `<div class="metric" style="text-align:left;min-width:100%">
src/anima_reborn/viewer/page.html:1169:  fetch("/api/dialogue/reset").catch(() => {});
tests/test_viewer.py:294:            # in the `if` chain would miss whichever engine is the `else`.

exec
/bin/zsh -lc "sed -n '130,210p' src/anima_reborn/coupled.py; sed -n '300,470p' src/anima_reborn/coupled.py; sed -n '420,470p' state/communication/RESULTS.md; sed -n '535,665p' state/communication/RESULTS.md; sed -n '665,805p' state/communication/RESULTS.md; sed -n '340,380p' src/anima_reborn/viewer/server.py; sed -n '460,515p' src/anima_reborn/viewer/page.html; sed -n '950,1085p' src/anima_reborn/viewer/page.html" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
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
| **귀머거리** | 결합 → 1.00. 입력이 비트 단위로 안 닿음 = 자율 고리. **이게 침묵이다** |
| 지우기 | 입력 → 0, 리듬 유지. 절반의 시간 동안 "원점"을 **적극적으로 들려주는 것** |
| 누설 | 결합 → 0 **그리고** 입력 → 0. 모든 목표가 0 = 시간상수 17 의 순수 감쇠 |

### 측정 (16개 입력 · 4시드)

| 침묵 틱 | 고리/귀머거리 | 고리/지우기 | 고리/누설 | 전방향 | 자기참조 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0.843 | 0.843 | 0.843 | 0.794 | 0.231 |
| 60 | **1.210** | 0.236 | 0.039 | 0.099 | 0.000 |
| 120 | **1.423** | 0.170 | 0.001 | 0.003 | 0.000 |
| 240 | **1.431** | 0.112 | 0.000 | 0.000 | 0.000 |
| 480 | **1.430** | 0.052 | 0.000 | 0.000 | 0.000 |

**고리는 감쇠하지 않는다.** 오히려 커진 뒤 480틱까지 평평하다(1.4306 → 1.4304). 순수 누설은
60틱에, 전방향은 120틱에, 자기참조는 20틱에 죽는다. 되먹임 없는 어떤 배선도 못 하는 일이다.

### 그런데 폭은 (`report-the-rank`)

| 침묵 틱 | 유효 랭크 | 부호패턴 | 처음 폭 대비 |
| ---: | ---: | ---: | ---: |
| 0 | 2.10 | 9.8/16 | 100% |
| 20 | 1.19 | 6.2/16 | 18% |
| 60 이후 | **1.00** | **2.0/16** | **0%** |

**정확히 2개 패턴, 영원히.** 4비트가 들어가서 **1비트**가 나온다. 첫 표만 인용하면 "개념이
침묵을 견딘다"로 읽히는데, 견디는 건 개념이 아니라 **어느 쪽으로 밀렸는지**다.

### 그 1비트는 누구 것인가 — 개념인가 잡음인가

| 침묵 틱 | 최빈 일치 | **만장일치** | 판정 |
| ---: | ---: | ---: | --- |
| 120 · 240 · 480 | 86% | **62%** | 개념이 정한다 |
| *잡음만일 때 (구조적 바닥)* | *63.7%* | *0.78%* | |

⚠️ 처음에 나는 바닥을 "50%쯤"으로 적었는데 **틀렸다** — 8회 걷기·2개 유역이면 잡음만으로도
최빈 다수가 평균 5.09/8 = **63.7%** 다. 그래서 최빈 열은 판정에 부적합하고, **만장일치**가
날카롭다: 잡음 하 0.78% 대 실측 62% — **79배**.

### 판정

**되먹임이 이 저장소에서 처음으로 능력을 샀다.** 지금까지 Φ 는 "통합돼 있음"을 재기만 했지
고리가 무엇을 **할 수 있는지**는 아무것도 아니었다. 침묵을 견디는 것은 배선이 순환일 때만
가능하고, 세 대조군이 전부 0 으로 죽는 동안 고리만 남는다.

**그리고 그것은 1비트다.** 개념이 쓰고, 영원히 남고, 폭은 하나. 플립플롭이지 개념 저장소가
아니다. 이 문장에서 작은 쪽 단어를 쓰는 것이 정확하다.

### 안 얻은 것

- **"쓴다"는 여전히 아니다.** 붙잡은 상태를 소비하는 것이 없고, 엔진의 어떤 반응도 거기
- 4유닛에서 1비트는 구조적 상한이다. 유닛을 늘리면 용량이 늘지만 Φ 는 6유닛에서 측정
  불가가 되므로, **용량과 측정 가능성이 정면으로 부딪힌다** — 이게 이제 이 노선의 벽이다.

---

## 용량 대 측정 가능성 — 벽을 넘다: 위상학이 답이었다 (2026-07-23)

지연 표본대조가 남긴 벽: 4유닛 고리는 1비트, 유닛을 늘리면 용량은 늘 것 같지만 Φ 는 6유닛에서
측정 불가. 이 난제를 두 모델에 위임했고, **fable 이 내 측정을 독립 재현하고 증명까지 붙였다.**
재현 스크립트 `state/communication/capacity.py`, 결정 IIT 실행은 `coupled_phi(Wiring.PAIRS, ...)`.

### 유닛을 늘리는 게 애초에 틀린 수였다 — 짝수 고리는 항상 1비트 (정리)

유닛의 반응 f 는 홀·감소·유계라 주기가 2를 못 넘는다. 고리를 닫으면 f^N 의 고정점은 교대
배치와 그 반전 둘뿐 — **폭이 몇이든 정확히 2패턴**. 측정이 확인:

| 배선 | 유닛 | 도달 패턴 | 재현율 | 재현되는 보유 상태 | 비트 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 고리 | 4 | 2 | 62% | **2** | 1.00 |
| 고리 | 6 | 3 | 84% | **2** | 1.00 |
| 고리 | 8 | 25 | 78% | **2** | 1.00 |
| **쌍 3개 · 사슬 0.2** | 6 | 8 | 88% | **8** | **3.00** |

**용량은 유닛 수가 아니라 배선의 순환 구조**다. 최대 `units/2` 개의 2-순환 = `Wiring.PAIRS`.

### 홀수 고리는 진동하지만 출구가 아니다

홀수 폭은 일관된 배정이 없다 — 원점이 유일 고정점이고 복소 고윳값으로 불안정, 나선 발산 후
포화가 극한순환으로 가둔다. 부호 그림자는 **2N-순환**(fable 유도, 실측 폭 3·5·7 에서 6·10·14
패턴 = 정확히 2N). 그러나 위상은 **복원력 없는 중립 방향**이라 걷기에 확산한다 — 재현율이
0%·6%·20%. 짝수는 1비트를 영원히, 홀수는 떠내려가는 무언가를 더. 둘 다 적고 어느 하나만
인용하지 않는다.

### 결정타 — 그 6유닛은 통합돼 있다

쌍 3개를 그냥 두면 **분리된 래치 3개** = 인수분해된 계. 방향성 Φ 는 표본 인공물이라 붕괴한다.
쌍 사이 약한 사슬(`chain=0.2`)이 걸리면 환원 불가가 된다:

| 6유닛 쌍 3개 | 400→1600 시행 | 판정 |
| --- | ---: | --- |
| 분리 (사슬 0, 귀무) | 5.21 → **2.07** | 붕괴 |
| **사슬 0.2** | 13.11 → **13.11** | **유지** |

**6유닛이 3비트를 담으면서 동시에 하나다.** 벽을 넘었다.

### ⚠ 저장소 규칙의 결함 — `RECURRENCE_FLOOR` 는 폭에 전이되지 않는다

fable 이 짚었고 실측으로 확인: 인수분해된 6유닛 귀무의 붕괴값(2.07)이 이미 문턱 1.0 을 넘는다.
인공물은 폭이 커질수록 자란다. 그래서 6유닛 이상의 Φ 판정은 **크기가 아니라 "시행 4배에도
유지되는가"** 로만 선다. `claims-need-controls` 가 "문턱은 자기 귀무 대비 측정하라"고 한 것의
연장이며, 문턱이 **폭마다 다시** 측정돼야 함을 뜻한다.

### 갈린 지점

sol 의 전문(全文)은 이 실행 시점에 아직 도착 전이라, 위 설계·측정은 fable 안을 따랐다.
fable 이 스크래치에서 먼저 돌린 수치(분리 2.91→1.25, 사슬 39.5)와 내가 출하 엔진에서 다시
잰 수치(2.07, 13.11)는 크기가 다르나 **방향과 판정이 같다** — 사본이 아니라 엔진을 재는 이
저장소 규칙대로, 인용하는 것은 엔진 값이다.

---

## 대미 — 개념을 3비트 통합 기판에 태우다: 공존과 기능을 가르다 (2026-07-23)

넷을 따로 세웠다 — 통합(Φ) · 보유(침묵 1비트) · 사용(표본대조) · 용량(쌍 배선 3비트).
이것을 한 사슬로 잇는다: 정렬기가 배운 개념을 6유닛·3래치·사슬 엔진에 태워, 여러 개념을
동시에 붙잡고 쓰는가. 재현 스크립트 `state/communication/concepts.py`. 설계는 위임했다.

**fable 이 치명적 프레이밍 결함을 먼저 짚었다** (sol 도 상호정보량으로 같은 병목 공식화):
`chain=0`(분리된 래치 3개)도 3비트를 담고 각 래치가 저장을 통과한다 — **환원가능인데도**.
그래서 "통합 기판에 개념이 통과"가 나와도 얻는 문장은 **공존**이지 "통합이 개념을 나른다"가
아니다. `chain=0` 을 일급 귀무로 넣었고, 통합이 **기능**이 되는 유일한 곳은 교차-쌍 탐침이다.

### 주소지정 — 래치는 차동 모드 하나로만 쓰인다 (유도)

`Wiring.PAIRS` 에서 쌍 j 는 유닛 (2j, 2j+1) 의 반전 2-순환이고, 그 **차동** `d[2j]−d[2j+1]`
만이 비트를 쓰는 쌍안정 모드다. 공통 모드는 음성 되먹임이라 침묵에서 죽는다. 그래서 개념의
쓸 수 있는 채널은 6-벡터 전체가 아니라 **세 차동**이고, 정렬기의 좁음이 이걸 무너뜨릴 수
있어 엔진 이전에 정렬기 주소지정률부터 쟀다.

### Phase 0 — 정렬기 주소지정률 (엔진 없음 · 게이트)

dim=6 정렬기가 **1.85비트**를 주소지정한다(shuffled 1.51 초과). 통과. (유효 랭크 1.48 은
분산이 한 방향에 쏠렸다는 뜻이지 부호 정보가 1비트란 뜻이 아니었다 — 부호 엔트로피는 3.88비트.)

### Phase B — 개념이 침묵을 건너 양상을 넘어 남는가

| 갈래 | 교차양상 일치 | 최악 시드 | 순열 바닥 | 단어 수 |
| --- | ---: | ---: | ---: | ---: |
| **사슬 (3비트)** | **68%** | 55% | 48% | 4.6 |
| 분리 (사슬 0) | 62% | 50% | 41% | 5.1 |
| 대조군 (짝 흐트러뜨림) | **19%** | 5% | 41% | 4.1 |

**헤드라인은 교차양상 일치**다 — 양상 0 으로 들려주고 침묵을 건넌 단어가, 같은 개념을 양상 1
로 들려줬을 때와 같은가. 68% 대 shuffled 19%(순열 바닥 아래). **`단어 수` 는 신호가 아니라
대조 열이다** — shuffled 도 4.1개 쓴다. 즉 단어 수는 유역 점유이지 개념 기억이 아니다.

**그러나 저장은 통합을 필요로 하지 않는다**: `chain=0`(분리 래치, 환원가능)도 62% 로 똑같이
한다. fable 이 예측한 그대로다. 여기까지는 **공존**이지 "통합이 개념을 나른다"가 아니다.

### Phase C — 통합이 기능인가, 우연인가 (대미의 핵심)

한 쌍(pair 0)만 뒤집은 탐침에, 나머지 쌍들이 얼마나 움직이는가:

| 사슬 | 쌍 1-2 응답 | 판정 |
| --- | ---: | --- |
| 0.0 | **0.000000** | 분리된 부분은 응답할 수 없다 (인과 경로 없음) |
| 0.2 | **0.581** | 사슬이 영향을 나른다 |

`chain=0` 의 0 은 **구조적**이다 — 쌍 사이 인과 경로가 없으니 정확히 0. 비영 응답은 **통합된
전체가 부분이 못 하는 일을 하는 것**이며, 공존이 위조할 수 없는 유일한 문장이다.

### 판정 — 얻은 것과 안 얻은 것

**얻은 것 ①**: 함께 나타남으로 배운 개념이, 3비트를 담고 동시에 통합으로 측정되는 기판을
건너, 침묵을 지나, **양상을 넘어** 남는다(68% 대 순열 48% · shuffled 19%).

**얻은 것 ②**: 그 통합은 **기능한다** — 한 쌍의 변화가 사슬을 통해 다른 쌍으로 전해지고,
분리된 기판에서는 정확히 0. 부분이 못 하는 일을 전체가 한다.

**안 얻은 것 (핵심)**: **저장 자체는 통합을 요구하지 않는다.** 분리된 래치도 개념을 똑같이
붙잡는다. 그래서 "통합이 개념을 나른다"는 주장은 **하지 않는다** — 통합이 더한 것은 저장이
아니라 쌍 사이 응답이다. 그리고 개념은 여전히 내용 없는 해시 잠재값이고, 3비트·6유닛·선형
세계이며, 어떤 경험-인접 단어도 벌지 않았다.

*sol 은 fable 의 반대칭 임베딩 제안에 "위상 인지 회전은 손 설계 디코더로 성공을 위조할 수
있다"며 경계했다. 실측이 갈랐다 — 임베딩 없이 raw 정렬 벡터가 이미 1.85비트를 주소지정하므로,
임베딩을 쓰지 않아 그 우려를 피했다.*

---

## 방향 전환 — 소통은 엔진끼리가 아니라 사람↔엔진 (2026-07-23)
## 방향 전환 — 소통은 엔진끼리가 아니라 사람↔엔진 (2026-07-23)

`state/communication/` 라인 전체를 **엔진끼리 소통**으로 좇았으나, 소유자가 정정했다: 소통은
**사람(사용자)과 엔진** 사이의 것이다. 엔진끼리 신호 게임(`handshake.py`·`signaling.py`)은
revert 했고(엔진 능력 측정 — 침묵·표본대조·용량·개념 — 은 유지), 목표를 **양방향 대화**로
옮겼다: 사람이 신호를 주고 엔진이 반응하며, 성공/실패로 둘 **사이에** 관습이 선다.
설계는 두 모델에 위임했고 강하게 수렴했다.

### 핵심 통찰 — 사람은 seedable 하지 않으니 주장을 둘로 쪼갠다 (합의)

- **재현 가능한 주장**은 **합성 파트너**(사람의 seedable 대역)로 측정 — 12시드 방향 바와 모든
  귀무가 가능. 재현 스크립트 `state/communication/dialogue.py`.
- **사람 주장**은 세션당 존재 증명이 될 것 — 자기 day-0, 자기 yoked 블록, 자기 로그의 순열
  검정. 사람은 데이터이지 통제변수가 아니며, **사람들 평균은 절대 내지 않는다**. 이건 viewer
  사람-게임(다음 조각)에서.

### 재현 가능한 기반 (12 짝 · 양방향 · 2유닛 고리 채널)

성공은 **task 가 계산**한다(`act==referent`) — 어느 쪽도 자기 의도를 스스로 보상 못 한다.

| 갈래 | 회복 | 최악 | 판정 |
| --- | ---: | ---: | --- |
| **정상 (파트너→엔진)** | **0.922** | 0.767 | 관습 형성 · 12/12 |
| **정상 (엔진→파트너)** | **0.873** | 0.630 | 반대 방향도 |
| day-0 | 0.500 | | 우연 |
| yoked 피드백 | 0.489 | | 결과가 확립한다 |
| **frozen-engine (에코 검사)** | **0.496** | | **엔진이 load-bearing** |
| deaf 채널 | 0.486 | | 채널이 경로에 있다 |
| 신호 파괴 | 0.516 | | 신호가 필요하다 |
| 짝 교환 (전 교차) | 0.501 | | 역사에 사적 |

**교차방향 일관성 58%** — 두 방향이 같은 코드로 수렴하지 **않는다**. 정직하게 **독립적인
one-way 코드 두 개**로 보고하며, 대칭 관습으로 평균 내지 않는다(fable 지시).

### 결정적 새 대조군 — frozen-engine (에코 트랩)

사람-엔진의 트랩은 **실험자 소유 인터프리터**다(측정이 아니라 UI/훈련 루프에 숨음). 두 입:
① **디스플레이 코덱**(엔진→사람: 우리가 고른 렌더를 사람이 읽음) — viewer 에서 raw 궤적만·
위치 무작위화로 방어. ② **에코**(사람→엔진: 엔진이 입력을 되돌려주고 사람이 자기 일관성을 잼).
②를 여기서 잡는다: 엔진 정책을 day-0(무작위)로 **고정하면** 완전히 학습된 파트너도 붕괴한다
(0.496) — **엔진의 학습된 반쪽이 코드를 나른다**는 증거이고, 엔진이 되돌려주는 게 아니다.

### 정적 감사 (구조적)

`_reinforce(policy, state, choice, reward)` 는 한 에이전트의 **자기** (상태, 선택, 성공)만
인자로 받는다 — 상대의 상태에 닿을 인자가 없다. 테스트가 시그니처를 검사한다.

### 이 조각이 아닌 것

이건 **엔진 반쪽의 재현 가능한 측정**이다 — 파트너는 아직 합성이다. 진짜 사람-엔진 대화는
viewer 에서 사람이 파트너 자리에 앉을 때이며(다음 조각), 거기서 디스플레이가 답을 인코딩하지
않아야 한다는 두 번째 감사가 붙는다. 얻을 수 있는 최대 문장도 작다 — *"이 사람과 이 엔진이
결과를 통해 사적인 1비트 관습을 확립하고 썼다."* 이해도 언어도 아니고, 경험-인접 단어도 아니다.

---

## 뷰어 `소통` 탭 — 사람이 파트너 자리에 앉는다 (라이브 절반 착지) (2026-07-23)

위에서 "다음 조각"으로 남긴 것을 구현했다. 채널 프리미티브(`channel`·`pick`·`reinforce`)를
`src/anima_reborn/dialogue.py` 로 올리고(상태 스크립트는 이제 그걸 import 한다 — 사본이 아니라
출하 엔진을 재는 규칙), 그 위에 `DialogueSession` 을 얹었다. 설계는 두 모델에 위임했고 강하게
수렴했다(보고서: `state/lab/2026-07-23-dialogue-viewer-*.md`).

### 두 조리개, 뷰어에서 봉인

- **엔진 쪽**: `reinforce(policy, state, choice, reward)` 는 한 에이전트의 자기 로컬만 받는다 —
  시그니처에 상대 상태 인자가 없다(정적 감사, 테스트가 검사).
- **디스플레이 쪽**: 방향 B 에서 사람은 **가공하지 않은 HOLD 흔적만** 본다 — 래치 비트도, 부호도,
  TELL 구동도, 정답도 없이. `display_payload(trace, markers, buttons)` 의 시그니처가 대상·신호·단어·
  성공에 닿을 인자를 갖지 않고(감사 테스트), 어떤 사전-행동 B 프레임도 그 값들을 담지 않는다(스키마
  테스트). 버튼 위치는 매 시행 뒤섞이고(위치는 코덱이 아님), 단위-마커 대응만 세션 내내 고정된다
  (그래야 1비트 채널이 읽힌다). 성공은 하니스가 계산한다(`act==대상`) — 어느 쪽도 자기 의도를 스스로
  보상하지 못한다.

### 에코 대조군, 라이브

엔진 정책의 day-0(무작위) 스냅숏을 세션 시작에 떠서 절대 학습시키지 않는다. 방향 A 테스트에서는
**같은 사람 신호**를 이 고정 엔진으로도 통과시켜(추가 클릭 0) 반사실 회복을 잰다 — 학습된 사람이
고정 반쪽을 만나 우연으로 붕괴해야 엔진의 **학습된 반쪽이 코드를 나른다**는 것이지 엔진이 사람의
비트를 되돌려주는 게 아니다.

### 세션당 존재 증명 (사람은 seedable 하지 않으므로)

한 세션(≈200 클릭·10~20분) 안에 자기 블록이 모두 있다: day-0(피드백·학습 없음) · train(피드백,
엔진만 학습) · test(보류, 피드백·학습 없음) · yoked(새 엔진·새 어휘·동전 보상, 그리고 보류
yoked-test). 판정은 방향별(A·B, **절대 평균 안 함**)로:

- **하드 게이트** = 정확도 > 0.5 **그리고** 자기 로그의 순열 검정 p ≤ 0.05 **그리고** 신호폭·행동폭
  둘 다 2/2 **그리고** 구조적 귀무 셋(day-0·고정엔진·귀머거리)이 우연(≤0.65)에 앉음.
- 순열은 대상 라벨을 (여백 고정으로) 섞어 사람 행동을 고정한 채 정확도를 다시 잰다 — 귀무는
  "이 사람 자신의 반응 편향을 보존한 뒤 대상은 행동에 대해 교환 가능하다"이다(10,000회).
- `report-the-rank`: 모든 정확도 옆에 신호폭/행동폭과 "보유 1비트"를 함께 낸다. 한 기호로 붕괴한
  코드는 잘 맞혀도 폭이 0 이고, 그건 판정에 부적합하다.

로그+판정은 완주 시 `state/communication/sessions/` 에 저장된다(뷰어가 씀, 엔진은 I/O 없음).
운영자가 파트너인 동시에 실험자이므로 **중단·음성·양성 세션을 전부 남기고 개수를 함께 밝힌다**
(체리피킹 방지). `sessions/README.md` 참조.

### 검증 (스크립트·HTTP 왕복)

- 새 `channel` 은 옛 `_channel` 과 **비트 동일**(1,600 회 채널런 불일치 0) — 재현 절반의 출판 숫자가
  그대로다(`default-stays-exact`).
- `DialogueSession` 완주 220 시행 0.4초 안. 멱등 제출(한 시행 = 한 로그 행) · 무입력 step 은 no-op ·
  완주 로그는 한 번만 넘어감 — 모두 테스트로 고정(`tests/test_dialogue_session.py`).
- 뷰어 lockstep(엔진↔탭) 통과, 전체 스위트 그린. HTTP 왕복 확인: 탭/패널 렌더 · 한 수 제출이
  다음 시행으로 진행 · reset · 완주 세션이 `state/` 에 1개 파일로 저장.

### 아직 아닌 것 (얻지 않은 것)

- **진짜 사람 세션을 아직 안 돌렸다.** 착지한 것은 **도구**다 — 실제 존재 증명은 사람이 한 번
  완주해야 나온다. `sessions/` 는 그래서 지금 비어 있다(합성 세션은 증거가 아니라 넣지 않음).
- **day-0 는 12 시행이라 검정력이 낮다** — 우연으로도 ≥9/12 가 ~7%. 이 게이트가 진짜 세션을
  가끔 거짓-기각할 수 있는데, 주장을 **안 하는** 보수적 방향이라 그대로 둔다.
- sol 이 더 센 대조군을 제안했다(두 맥락 동시 live/yoked · 매-시행 디스플레이-정체성 뒤섞기 귀무 ·
  Wilson 구간 · Holm 보정 · 99,999 순열). 이번엔 fable 의 순차 블록 + day-0 을 디스플레이-누출
  행동 검사로 쓰는 안을 택했고(더 단순하고 기존 뷰어 구조에 맞음), 나머지 강화안(두 맥락·Wilson·
  Holm·99,999 순열)은 후속으로 남긴다.
- 여전히 4유닛·2유닛 고리·1비트다. 개념도 언어도 아니다.

### 후속 — 두 번째 조리개를 표적 귀무로 막음: 디스플레이 뒤섞기 (2026-07-23)

위 "아직 아닌 것"에서 **day-0(12시행)이 디스플레이-누출 검사로 검정력이 낮다**고 적었다. sol 이
설계해 둔 **디스플레이-정체성 뒤섞기 귀무**를 방향 B 에 착지시켜 그 구멍을 표적 대조군으로 메웠다.

**기전**: 방향 B 의 전용 `dscramble` 시행에서, 대상·엔진 정책·버튼을 고정한 채 **두 단위의 정체성
(곡선 순서 + 마커)을 절반 확률로 통째로 뒤집는다**. 채점은 흔적을 쓰지 않으므로(성공 = `act==대상`,
사람의 버튼에서만) 뒤집는 건 사람이 **볼 수 있는 것**만 바꾸지 진실값은 안 바꾼다. 사람의 회복이
정말 배운 디스플레이 규칙이면 이 뒤집기가 그걸 부수어야 한다(귀무가 우연에 앉음). 살아남으면 —
화면이 아닌 경로로 답을 읽었다는 뜻이라 — 세션 전체가 `audit_failed` 로 무효화된다(방향 B 하나가
아니라 세션 판정을 덮는다).

**측정 (실측)**: 화면을 **우회해 원시 래치를 직접 읽는** "누출" 사람을 스크립트로 넣었더니 —
옛 설계라면 그저 "근거 없음"으로 흘려보냈을 그 사람이 — dscramble **0.88**(> 0.65)로 잡혀
**`audit_failed`** 가 떴다. 뒤집기가 실제로 매 시행 절반 일어나는 것(swapped ∈ {True, False})과
이 판정 경로 둘 다 테스트로 고정(`tests/test_dialogue_session.py::TestTheDisplayScrambleNull`).
dscramble 은 방향 B 의 구조적 게이트에도 들어가, 이 귀무가 높으면 B 는 `formed` 이 될 수 없다.
`report-the-rank`/`claims-need-controls` 그대로 — 주장(디스플레이를 읽어 회복했다)마다 그걸 위조할
귀무(디스플레이를 못 읽게 뒤집으면 무너지는가)를 함께 낸다.

**아직 아닌 것**: day-0 검정력 자체는 여전히 낮다(표적 귀무가 생겼으니 하드-게이트 부담은 dscramble 로
옮겼다). 두 맥락 동시·Wilson·Holm·99,999 순열은 여전히 후속. 진짜 사람 세션은 여전히 미실행.
    The I/O lives here in the viewer, never in the engine. A missing or read-only tree is
    swallowed rather than crashing the stream — the session is still shown in the browser.
    """
    try:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d-%H%M%S")
        path = SESSIONS_DIR / f"{stamp}-{report['token']}.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


class _DialogueHandler:
    """The live human dialogue session — the one interactive tab.

    Unlike every other handler its engine waits on human input rather than free-running:
    `configure` carries the human's button press (a trial nonce and a choice) into the
    session, `step` (in the ticker) resolves it, and `describe` reads the frame. The
    session is a bit-exact no-op on a tick with nothing submitted, so the fixed tick rate
    is only an input-latency bound. On completion the finished log is written to `state/`.
    """

    @staticmethod
    def configure(session: DialogueSession, params: dict[str, list[str]]) -> None:
        raw_nonce = params.get("nonce")
        raw_choice = params.get("choice")
        if not raw_nonce or not raw_choice:
            return  # a plain frame request (sliders/one-shot) — nothing to submit
        try:
            nonce = int(raw_nonce[0])
            choice = int(raw_choice[0])
        except ValueError:
            return
        # Idempotent: a stale or double-submitted nonce is ignored by the session, so the
        # ticker re-applying the same persistent control dict cannot double-resolve a trial.
        session.submit(nonce, choice)

    @staticmethod
    def describe(session: DialogueSession) -> dict[str, Any]:
        frame = session.describe()
        report = session.take_report()
    <p class="note" style="margin-top:16px;padding-top:14px;border-top:1px solid var(--line)">
      <strong>출발점이 0 이 아닙니다.</strong> 두 양상이 같은 잠재값을 섞은 것이라, 아무것도
      배우지 않은 무작위 사영도 상관을 얼마간 갖습니다(운 나쁜 시드에서 0.397까지). 그래서
      화면의 모든 값은 <strong>자기 출발점 대비 증가분</strong>입니다 — 원시값으로 판정하면
      아무것도 안 배운 학습기가 통과합니다.
    </p>
  </div>
</section>

<section class="panel" id="p-dialogue">
  <div class="card">
    <h2>사람이 파트너 자리에 앉는다 — 사람↔엔진 대화</h2>
    <p class="note">
      재현 가능한 절반(합성 파트너·12시드·모든 귀무)은 <strong>state/communication/dialogue.py</strong>
      에 있습니다. 여기서는 <strong>당신</strong>이 파트너 자리에 앉아, 같은 신호 게임을 라이브로
      돌립니다. 사람은 seedable 하지 않으므로 이건 <strong>세션당 존재 증명</strong>입니다 —
      사람들 평균은 내지 않고, 이 세션의 자기 day-0·자기 yoked·자기 로그의 순열 검정으로만 판정합니다.
    </p>
    <p class="note" style="margin-top:-8px">
      화면은 <strong>답을 인코딩하지 않습니다</strong>(두 번째 조리개): 엔진이 보내는 쪽에서는
      <strong>가공하지 않은 흔적</strong>만 보이고(래치 비트도, 부호도, 정답도 없이), 버튼 위치는
      매 시행 뒤섞입니다. 성공은 오직 하니스가 계산합니다(<code>act == 대상</code>) — 어느 쪽도
      자기 의도를 스스로 보상하지 못합니다. 얻을 수 있는 최대 문장도 작습니다:
      <strong>이 사람과 이 엔진이 결과만으로 사적인 1비트 관례를 세우고 썼다</strong>. 이해도 언어도 아닙니다.
    </p>

    <div class="controls">
      <button class="act" id="dg-new">새 세션</button>
      <span class="label" style="margin-left:auto">진행 <b id="dg-progress">— / —</b> · <span id="dg-block">—</span></span>
    </div>

    <div id="dg-play">
      <p class="label" id="dg-instruction">새 세션을 시작하세요.</p>
      <div id="dg-referent" style="text-align:center;font-size:64px;line-height:1.1;margin:8px 0;min-height:70px"></div>
      <canvas id="dg-trace" height="200" style="display:none"></canvas>
      <p class="label" id="dg-markers" style="text-align:center;display:none"></p>
      <div id="dg-buttons" style="display:flex;gap:14px;justify-content:center;margin-top:14px"></div>
      <div class="status" id="dg-feedback" style="text-align:center;font-size:28px;min-height:34px"></div>
    </div>

    <div id="dg-report" style="display:none"></div>

    <div class="status" id="dg-status"></div>
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
    : d.drive.toFixed(2);
  $("cp-ticks").textContent = d.ticks;
  const status = $("cp-status");
  status.className = "status";
  const wall = d.reachable ? "" : " · 결합이 1.00 이라 입력이 닿을 틈이 없습니다 (벽)";
  status.textContent = (WIRING_TEXT[d.wiring] || "") + wall;
}

// ── 소통 (dialogue) ──────────────────────────────────────────────────────────
// The one interactive tab. The human's button press is the only input; the server
// schedules, scores and rewards. Buttons are rebuilt only when the trial nonce changes,
// so the 8 Hz stream of identical no-op frames does not reset a click.
const DIALOGUE_TEXT = {
  two_way_session_evidence: "이 세션에서만: 이 사람과 이 엔진이 결과만을 통해 두 개의 사적인 1비트 단방향 관례를 세우고, 피드백 없는 시험에서 썼습니다. 사람 일반·이해·언어에 대한 주장이 아닙니다.",
  one_way_session_evidence: "이 세션에서는 한 방향의 1비트 관례 증거만 있습니다. 양방향 소통으로 보고하지 않습니다.",
  no_session_evidence: "이 세션에서는 모든 대조군을 넘는 관례 증거가 없습니다.",
  audit_failed: "감사 대조군 실패 — 디스플레이 뒤섞기 귀무가 우연을 넘습니다. 화면이 답을 흘렸다는 뜻이라, 이 세션의 어떤 양성 정확도에도 소통 증거를 부여하지 않습니다.",
};
let dgNonce = null;

function drawDialogueTrace(canvas, trace, markers) {
  const { ctx, w, h } = fit(canvas);
  ctx.strokeStyle = "rgba(139,146,163,.16)";
  ctx.setLineDash([3, 3]);
  ctx.beginPath(); ctx.moveTo(0, h / 2); ctx.lineTo(w, h / 2); ctx.stroke();
  ctx.setLineDash([]);
  const vr = 1.0, colors = ["#7b9aff", "#ff7b9a"];
  for (let u = 0; u < 2; u++) {
    ctx.beginPath();
    ctx.strokeStyle = colors[u];
    ctx.lineWidth = 1.6;
    ctx.lineJoin = "round";
    for (let i = 0; i < trace.length; i++) {
      const norm = (trace[i][u] + vr) / (2 * vr);
      const x = (i / (trace.length - 1)) * w;
      const y = h - (norm * h * 0.84 + h * 0.08);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.fillStyle = colors[u];
    ctx.font = "600 13px ui-sans-serif, system-ui, sans-serif";
    ctx.fillText(markers[u], 6 + u * 28, 18);
  }
}

function renderDialogue(d) {
  $("dg-block").textContent = ko(d.phase);
  if (d.phase === "done") {
    $("dg-progress").textContent = `${d.total} / ${d.total}`;
    $("dg-play").style.display = "none";
    renderDialogueReport(d.report);
    return;
  }
  $("dg-play").style.display = "";
  $("dg-report").style.display = "none";
  const p = d.pending;
  if (!p) { $("dg-instruction").textContent = "새 세션을 시작하세요."; return; }
  $("dg-progress").textContent = `${d.round} / ${d.total}`;
  if (p.nonce === dgNonce) return;   // same trial — do not rebuild (would reset a click)

  // Flash the just-resolved trial's outcome, but only in learning blocks.
  const fb = $("dg-feedback");
  fb.textContent = (d.feedback === 1) ? "○" : (d.feedback === 0) ? "×" : "";
  fb.style.color = (d.feedback === 1) ? "var(--g)" : "#ff7b9a";

  dgNonce = p.nonce;
  const trace = $("dg-trace"), markers = $("dg-markers"), ref = $("dg-referent");
  if (p.dir === "a") {
    $("dg-instruction").textContent = "이 대상을 전할 신호를 고르세요.";
    ref.style.display = ""; ref.textContent = p.referent;
    trace.style.display = "none"; markers.style.display = "none";
  } else {
    $("dg-instruction").textContent = "이 흔적이 가리키는 대상을 고르세요.";
    ref.style.display = "none";
    trace.style.display = ""; markers.style.display = "";
    markers.textContent = `${p.markers[0]} / ${p.markers[1]}`;
    drawDialogueTrace(trace, p.trace, p.markers);
  }
  const box = $("dg-buttons");
  box.innerHTML = "";
  p.buttons.forEach((label, idx) => {
    const b = document.createElement("button");
    b.className = "act";
    b.style.fontSize = "28px"; b.style.padding = "10px 28px";
    b.textContent = label;
    b.addEventListener("click", () => {
      for (const c of box.children) c.disabled = true;
      fetch(`/api/dialogue/control?nonce=${p.nonce}&choice=${idx}`).catch(() => {});
    });
    box.appendChild(b);
  });
}

function renderDialogueReport(r) {
  $("dg-report").style.display = "";
  const dir = (key, name) => {
    const a = r[key];
    const nulls = Object.entries(a.nulls).map(([k, v]) =>
      `${ko(k)} ${v.rate === null ? "—" : v.rate.toFixed(2)}`).join(" · ");
    return `<div class="metric" style="text-align:left;min-width:100%">
      <div class="k">${name}</div>
      <div class="v" style="font-size:15px">
        <span class="badge ${a.verdict === "formed" ? "good" : "bad"}">${ko(a.verdict)}</span>
        정확도 ${a.hits}/${a.n} = ${a.accuracy.toFixed(2)} · p=${a.p.toFixed(4)}
        · 신호폭 ${a.signal_support}/2 · 행동폭 ${a.act_support}/2 · 보유 1비트
      </div>
      <div class="note" style="margin:4px 0 0">귀무: ${nulls}</div>
    </div>`;
  };
  $("dg-report").innerHTML = `
    <div class="status" style="margin-bottom:10px">${DIALOGUE_TEXT[r.verdict] || r.verdict}</div>
    <div class="metrics">
      ${dir("a", "A · 사람 → 엔진")}
      ${dir("b", "B · 엔진 → 사람")}
    </div>
    <p class="note" style="margin-top:10px">
      교차방향 일관성 ${(r.cross_direction_consistency * 2).toFixed(0)}/2
      (두 방향이 같은 코드면 2, 독립적 단방향 코드 둘이면 1) — 평균 내지 않고 그대로 보고합니다.
      순열 ${r.permutations}회 · α=${r.alpha}. 로그는 <code>state/communication/sessions/</code> 에 남습니다.
    </p>`;
}

const LEARNED = [];   // 배운 양의 이력 — 곡선이 자라는 걸 본다

function renderAlign(d) {
  LEARNED.push(d.learned);
  if (LEARNED.length > 300) LEARNED.shift();

  // 학습 곡선 + 기준선 0.30
  const { ctx, w, h } = fit($("al-curve"));
  const lo = -0.3, hi = 1.1;
  const y = v => h - ((v - lo) / (hi - lo)) * h * 0.86 - h * 0.07;

  ctx.strokeStyle = "rgba(168,230,104,.35)";
  ctx.setLineDash([4, 4]);
  ctx.beginPath(); ctx.moveTo(0, y(0.3)); ctx.lineTo(w, y(0.3)); ctx.stroke();

exec
/bin/zsh -lc "python -c 'import math
for n in (16,24,32):
 print(\"n\",n)
 for k in range(n+1):
  p=sum(math.comb(n,i)*(.125**i)*(.875**(n-i)) for i in range(k,n+1))
  if p<=.05:
   print(\"first\",k,k/n,p);break'" in /Users/mini/dancinlab/anima-reborn
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "python3 -c 'import math
for n in (16,24,32):
 print(\"n\",n)
 for k in range(n+1):
  p=sum(math.comb(n,i)*(.125**i)*(.875**(n-i)) for i in range(k,n+1))
  if p<=.05:
   print(\"first\",k,k/n,p);break'" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
n 16
first 5 0.3125 0.04066189058827874
n 24
first 7 0.2916666666666667 0.023881809715719685
n 32
first 8 0.25 0.03950571618792498

codex
The key architecture is clear: make “live exchange” and “evidence” two different states of one session. Free play can feel conversational; only a frozen, no-feedback probe can earn a verdict. I also found one audit detail worth fixing in the first commit: the current display-scramble swaps both traces and markers together, which preserves their pairing for a careful reader; the null must permute one side of that mapping, not both.
Repository contracts and the proposed architecture are now mapped, including the legacy bit-exact path and the display-audit correction.
  ✓ Inspect dialogue, capacity, UI, tests, and RESULTS contracts
  ✓ Map the three interpretations and select the minimal honest architecture
  ✓ Specify turn flow, measurement/nulls, 3-bit generalization, framing, and first commit
codex
## 1. Recommendation: both, with a hard boundary between play and proof

Choose interpretation 3: a free-form 3-bit live exchange, followed—only when requested—by a short frozen audit.

The two parts must have different contracts:

- Live exchange is adaptive, rewarding, interruptible, and conversation-like. It produces no evidentiary verdict.
- Blind check is fixed before the session, freezes learning, reveals no outcomes, and alone produces the per-session verdict.

This best serves “사람과 대화가 가능하게” because freedom makes it feel like an exchange while eight distinguishable cards give the human enough vocabulary to form patterns. The measurement boundary prevents that freedom from contaminating the evidence.

The alternatives:

| Interpretation | Result |
| --- | --- |
| Free 1-bit | Safest and easiest, but remains “yes/no ping-pong.” Useful fallback, not the best destination. |
| Scheduled 3-bit | Richer vocabulary but still feels like an eight-choice exam; 8×8 policies also need more experience. |
| Free 3-bit + blind check | Best experience, provided the free log is never treated as confirmatory evidence. |

Dissent case: if implementation risk matters more than conversational feel, ship free 1-bit first and retain the present 220-trial measurement unchanged.

## 2. The turn, concretely

One visible “exchange” consists of two half-turns and appears in a transcript.

### Human → engine

1. The human sees eight abstract cards, such as `● ▲ ■ ◆ ★ ✦ ⬟ ⬢`, with no semantic labels.
2. They freely choose which card to send. This is not assigned like a quiz.
3. They choose one of eight session-specific signal glyphs.
4. The signal drives the three-latch channel.
5. The engine decodes the final three differential bits, applies its learned 8×8 receiver policy, and reveals the card it selected.
6. The transcript adds:

   `나: ◆  →  엔진의 선택: ◆  ○`

   or:

   `나: ◆  →  엔진의 선택: ▲  ×`

7. The harness alone computes `success = engine_action == human_card`; that one bit is given to the engine update.

### Engine → human

1. The harness privately deals the engine one of eight cards. The UI must say “the harness dealt a hidden card,” not “the engine wanted to say…”.
2. The engine’s 8×8 sender policy selects a signal.
3. The human sees three small pair panels, each containing two raw curves from only the final 60 ticks of the 240-tick HOLD period.
4. They choose one of eight cards.
5. In free play only, the hidden card is revealed and the transcript adds:

   `엔진이 보낸 흔적  →  내 선택: ■  / 숨은 카드: ■  ○`

The next exchange starts immediately. The human may repeat a card, change strategy, pause, or request the blind check. There is no cumulative “score”; the transcript’s individual land/fail events provide the conversational consequence without turning the screen back into an exam.

Controls:

- `새 만남`
- `일시정지`
- `자유 교환 끝내기`
- `관례를 블라인드로 확인하고 종료`
- `증거 없이 종료`

The blind-check button warns that learning will freeze and cannot resume in that session.

## 3. How measurement survives

Do not run a rolling permutation test on free play. It would be invalidated by feedback, voluntary referent selection, repetition, adaptive stopping, and the human’s evolving strategy.

Use this state machine:

```text
BASELINE → FREE → AUDIT → DONE
                    ↘ ABANDONED
```

### Baseline

Before feedback begins, run 16 exchanges:

- 16 A trials: two per referent.
- 16 B trials: two per referent.
- No feedback, learning, target reveal, or running tally.

This is the actual day-0 comparison. The UI calls it a brief “first-contact calibration,” not conversation evidence.

### Free phase

Alternating A/B exchanges continue without a fixed limit. Every result is revealed and the main policies learn.

A readiness indicator—not a verdict—shows:

- exposures per referent in each direction;
- signal, held-word, and action support;
- current descriptive effective rank.

“Evidence-ready” appears after every referent has at least eight free exposures in both directions and all eight signal/held-word/action values have appeared. The user may audit earlier, but the likely result is honestly “insufficient width/evidence.”

A day-0 frozen engine and a coin-reward yoked engine run silently in parallel:

- A-yoked receiver receives the same channel word, chooses independently, and updates from a precommitted fair coin instead of success.
- B-yoked sender receives the same hidden referent, chooses independently, and updates from the same kind of coin tape.
- Neither yoked result reaches the display or affects the human.

This gives matched state exposure and update count without consequence coupling.

### Blind audit

When requested:

- Freeze the main, frozen, and yoked policies.
- Use an audit plan generated and committed at session creation.
- Hide block and arm.
- Disable feedback, target reveal, transcript additions, retry, and learning.
- Randomize button positions every trial.
- Complete exactly 88 choices:

| Direction/arm | Trials |
| --- | ---: |
| A live | 24: three per referent |
| B live | 24: three per referent |
| B frozen | 8: one per referent |
| B deaf | 8: one per referent |
| B signal-scramble | 8: one per referent |
| B display-scramble | 8: one per referent |
| B yoked | 8: one per referent |

A’s frozen, deaf, signal-scramble, and yoked results are counterfactuals on the same 24 recorded human signals, requiring no extra clicks.

The permutation test uses only live audit rows: shuffle referent labels while preserving their observed margins and holding actions fixed, 10,000 times. Apply Holm correction across the two directional live tests.

A direction forms only if all are true:

- live accuracy is at least `0.50`, against eight-way chance `0.125`;
- Holm-adjusted permutation `q ≤ 0.05`;
- effective rank is `8/8`;
- signal, held-word, and action supports are all `8/8`;
- every referent’s modal audit action is correct;
- day-0 is at most `4/16`;
- each 24-row A counterfactual is at most `6/24`;
- each eight-row B null is at most `2/8`.

Those null ceilings are pre-registered falsification thresholds, not assertions that chance equivalence was proved. Show counts and Wilson intervals for every live and null result.

Verdicts remain per session and per direction:

- `reciprocal_3bit_session_evidence`
- `two_directional_3bit_session_evidence`
- `one_way_session_evidence`
- `insufficient_effective_width`
- `no_session_evidence`
- `audit_failed`

`reciprocal` additionally requires cross-direction modal-code agreement `8/8`. Otherwise report two directional conventions, not one shared language.

If free play ends without the audit, the only result is:

> Exploratory live exchange completed. No measured session verdict was attempted.

### Important display-null correction

As currently written in [dialogue.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/dialogue.py), `dscramble` swaps both trace columns and their markers. A reader who follows the marker still sees the original trace-marker association, so that transformation does not necessarily destroy a legitimate learned display rule.

The new null must permute exactly one side:

- keep the six stable marker/color lanes fixed;
- uniformly permute the trace columns among those lanes, including independent within-pair swaps;
- leave target, signal, buttons, and scoring unchanged.

Add both tests:

- a lawful reader using only `display_payload` succeeds on live displays and collapses under `dscramble`;
- a bypass reader that accesses the hidden latch remains accurate and causes `audit_failed`.

## 3b. Exact 3-bit changes

### Channel

Support exactly two configurations initially:

```text
legacy: wiring=RING,  units=2, chain=0.0, TELL=200, HOLD=120
pairs3: wiring=PAIRS, units=6, chain=0.2, TELL=400, HOLD=240
```

Reject other dialogue configurations for now.

For signal `s ∈ [0,7]`, bit `j` drives pair `j` as:

```text
bit 0: (+0.8, -0.8)
bit 1: (-0.8, +0.8)
```

After HOLD, decode:

```text
b[j] = 0 if v[2j] - v[2j+1] > 0 else 1
word = b[0] | b[1] << 1 | b[2] << 2
```

The common mode is never read. `deaf` retains coupling `1.0` for the whole run.

The session randomly assigns eight signal glyphs to these eight drive words. That assignment is stable within the session and makes the convention private.

### Policies

Use flat categorical policies:

- sender: `referent[8] × signal[8]`;
- receiver: `held_word[8] × action[8]`;
- initial entries all `1.0`;
- retain the current reward-only `RATE = 0.3`.

Do not factor the policy into three 2×2 bit policies: that would impose compositional structure rather than allowing the eight-state convention to form.

The existing `pick` and `reinforce` logic generalizes mechanically; their one-agent-local aperture remains unchanged.

### Display

Direction B displays:

- three vertically stacked pair panels;
- two raw curves per panel;
- fixed neutral unit markers and colors for the session;
- only the final 60 HOLD samples;
- eight randomized referent buttons.

Never display the drive, signal glyph, differential, sign, packed word, target, success, or arm before the human acts.

### Rank beside accuracy

Report structural capacity and observed width separately:

> substrate: 3 differential latches / 8 held states  
> observed convention: effective rank `k/8 = log₂(k)` bits

For each stage, build an 8×8 modal-code matrix: a row receives a `1` only when it has a unique modal output; tied or undersampled rows remain zero. Its rank is the number of distinct resolved output symbols.

Report:

- sender rank `R→S`;
- held rank `S→W`;
- receiver/display rank `W→A`;
- end-to-end rank `R→A`;
- effective rank = their minimum.

Only `8/8 = 3.00 bits` may be called a 3-bit convention. A collapse to two outputs is reported as `2/8 = 1.00 bit`, regardless of accuracy or the substrate’s nominal capacity.

### Default stays exact

Extend the channel with default parameters corresponding to the legacy tuple. Keep the legacy execution branch unchanged; the PAIRS implementation is a separate branch.

Before refactoring, record a golden SHA-256 over the IEEE-754 bytes of all HOLD values for:

- both signals;
- deaf true/false;
- seeds `0…199`.

The test asserts that calling the new API with no wiring arguments produces the same golden hash and identical final latch results. Retain the existing comparison against the reproducible state harness. This pins the published 1-bit path, not merely its aggregate accuracy.

## 4. Honest framing

Maximum default claim:

> In this session, this person and this engine established and used two private directional eight-state conventions through consequence in feedback-free trials. The channel held three differential latch bits, and the observed effective rank was 8/8 in each direction.

Only with cross-direction agreement `8/8`:

> In this session, this person and this engine established and used a reciprocal private 3-bit convention through consequence.

Korean UI version:

> 이 세션에서 이 사람과 이 엔진은 결과를 통해 8개 상태를 구별하는 사적인 관례를 형성하고, 피드백 없는 시행에서 사용했습니다. 보유 기판은 3개의 차동 래치였고 관측 유효 폭은 8/8(3.00비트)이었습니다.

Forbidden claims include:

> The engine understood the person, knew what the symbol meant, chose a topic, felt something, used language, or held a human-like conversation.

Keep pattern-completion under control by using abstract cards only. No text box, semantic labels, emotions, “typing…” animation, conversational prose, or UI words such as “understood,” “meant,” or “said.” The tab may remain `소통`, but its permanent subtitle should be:

> 실시간 양방향 관례 교환 — 언어·이해가 아님

## 5. Minimal first commit

Implement the complete narrow vertical slice:

- preserve the current `DialogueSession` as `1비트 측정` research mode;
- add `ConversationSession` with `BASELINE/FREE/AUDIT/DONE`;
- add the proven six-unit PAIRS channel while keeping the legacy default bit-exact;
- add eight-card free turn selection and the alternating transcript;
- add frozen, deaf, signal-scramble, corrected display-scramble, and parallel yoked controls;
- add the 88-choice blind audit and per-session verdict;
- add stage ranks, effective bits, supports, counts, intervals, and nulls beside accuracy;
- persist started, completed, abandoned, and unaudited sessions—not only positive completions;
- update [RESULTS.md](/Users/mini/dancinlab/anima-reborn/state/communication/RESULTS.md) with the exact allowed and forbidden sentences;
- add aperture, lawful-display-reader, collapse-to-two-rank, null, and default-bit-exact tests.

Defer semantic vocabulary, text, topics, adaptive evidence, rolling free-log tests, more than eight states, compositional messages, and cross-person summaries. Those would create claims the substrate has not earned.
tokens used
77,620
## 1. Recommendation: both, with a hard boundary between play and proof

Choose interpretation 3: a free-form 3-bit live exchange, followed—only when requested—by a short frozen audit.

The two parts must have different contracts:

- Live exchange is adaptive, rewarding, interruptible, and conversation-like. It produces no evidentiary verdict.
- Blind check is fixed before the session, freezes learning, reveals no outcomes, and alone produces the per-session verdict.

This best serves “사람과 대화가 가능하게” because freedom makes it feel like an exchange while eight distinguishable cards give the human enough vocabulary to form patterns. The measurement boundary prevents that freedom from contaminating the evidence.

The alternatives:

| Interpretation | Result |
| --- | --- |
| Free 1-bit | Safest and easiest, but remains “yes/no ping-pong.” Useful fallback, not the best destination. |
| Scheduled 3-bit | Richer vocabulary but still feels like an eight-choice exam; 8×8 policies also need more experience. |
| Free 3-bit + blind check | Best experience, provided the free log is never treated as confirmatory evidence. |

Dissent case: if implementation risk matters more than conversational feel, ship free 1-bit first and retain the present 220-trial measurement unchanged.

## 2. The turn, concretely

One visible “exchange” consists of two half-turns and appears in a transcript.

### Human → engine

1. The human sees eight abstract cards, such as `● ▲ ■ ◆ ★ ✦ ⬟ ⬢`, with no semantic labels.
2. They freely choose which card to send. This is not assigned like a quiz.
3. They choose one of eight session-specific signal glyphs.
4. The signal drives the three-latch channel.
5. The engine decodes the final three differential bits, applies its learned 8×8 receiver policy, and reveals the card it selected.
6. The transcript adds:

   `나: ◆  →  엔진의 선택: ◆  ○`

   or:

   `나: ◆  →  엔진의 선택: ▲  ×`

7. The harness alone computes `success = engine_action == human_card`; that one bit is given to the engine update.

### Engine → human

1. The harness privately deals the engine one of eight cards. The UI must say “the harness dealt a hidden card,” not “the engine wanted to say…”.
2. The engine’s 8×8 sender policy selects a signal.
3. The human sees three small pair panels, each containing two raw curves from only the final 60 ticks of the 240-tick HOLD period.
4. They choose one of eight cards.
5. In free play only, the hidden card is revealed and the transcript adds:

   `엔진이 보낸 흔적  →  내 선택: ■  / 숨은 카드: ■  ○`

The next exchange starts immediately. The human may repeat a card, change strategy, pause, or request the blind check. There is no cumulative “score”; the transcript’s individual land/fail events provide the conversational consequence without turning the screen back into an exam.

Controls:

- `새 만남`
- `일시정지`
- `자유 교환 끝내기`
- `관례를 블라인드로 확인하고 종료`
- `증거 없이 종료`

The blind-check button warns that learning will freeze and cannot resume in that session.

## 3. How measurement survives

Do not run a rolling permutation test on free play. It would be invalidated by feedback, voluntary referent selection, repetition, adaptive stopping, and the human’s evolving strategy.

Use this state machine:

```text
BASELINE → FREE → AUDIT → DONE
                    ↘ ABANDONED
```

### Baseline

Before feedback begins, run 16 exchanges:

- 16 A trials: two per referent.
- 16 B trials: two per referent.
- No feedback, learning, target reveal, or running tally.

This is the actual day-0 comparison. The UI calls it a brief “first-contact calibration,” not conversation evidence.

### Free phase

Alternating A/B exchanges continue without a fixed limit. Every result is revealed and the main policies learn.

A readiness indicator—not a verdict—shows:

- exposures per referent in each direction;
- signal, held-word, and action support;
- current descriptive effective rank.

“Evidence-ready” appears after every referent has at least eight free exposures in both directions and all eight signal/held-word/action values have appeared. The user may audit earlier, but the likely result is honestly “insufficient width/evidence.”

A day-0 frozen engine and a coin-reward yoked engine run silently in parallel:

- A-yoked receiver receives the same channel word, chooses independently, and updates from a precommitted fair coin instead of success.
- B-yoked sender receives the same hidden referent, chooses independently, and updates from the same kind of coin tape.
- Neither yoked result reaches the display or affects the human.

This gives matched state exposure and update count without consequence coupling.

### Blind audit

When requested:

- Freeze the main, frozen, and yoked policies.
- Use an audit plan generated and committed at session creation.
- Hide block and arm.
- Disable feedback, target reveal, transcript additions, retry, and learning.
- Randomize button positions every trial.
- Complete exactly 88 choices:

| Direction/arm | Trials |
| --- | ---: |
| A live | 24: three per referent |
| B live | 24: three per referent |
| B frozen | 8: one per referent |
| B deaf | 8: one per referent |
| B signal-scramble | 8: one per referent |
| B display-scramble | 8: one per referent |
| B yoked | 8: one per referent |

A’s frozen, deaf, signal-scramble, and yoked results are counterfactuals on the same 24 recorded human signals, requiring no extra clicks.

The permutation test uses only live audit rows: shuffle referent labels while preserving their observed margins and holding actions fixed, 10,000 times. Apply Holm correction across the two directional live tests.

A direction forms only if all are true:

- live accuracy is at least `0.50`, against eight-way chance `0.125`;
- Holm-adjusted permutation `q ≤ 0.05`;
- effective rank is `8/8`;
- signal, held-word, and action supports are all `8/8`;
- every referent’s modal audit action is correct;
- day-0 is at most `4/16`;
- each 24-row A counterfactual is at most `6/24`;
- each eight-row B null is at most `2/8`.

Those null ceilings are pre-registered falsification thresholds, not assertions that chance equivalence was proved. Show counts and Wilson intervals for every live and null result.

Verdicts remain per session and per direction:

- `reciprocal_3bit_session_evidence`
- `two_directional_3bit_session_evidence`
- `one_way_session_evidence`
- `insufficient_effective_width`
- `no_session_evidence`
- `audit_failed`

`reciprocal` additionally requires cross-direction modal-code agreement `8/8`. Otherwise report two directional conventions, not one shared language.

If free play ends without the audit, the only result is:

> Exploratory live exchange completed. No measured session verdict was attempted.

### Important display-null correction

As currently written in [dialogue.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/dialogue.py), `dscramble` swaps both trace columns and their markers. A reader who follows the marker still sees the original trace-marker association, so that transformation does not necessarily destroy a legitimate learned display rule.

The new null must permute exactly one side:

- keep the six stable marker/color lanes fixed;
- uniformly permute the trace columns among those lanes, including independent within-pair swaps;
- leave target, signal, buttons, and scoring unchanged.

Add both tests:

- a lawful reader using only `display_payload` succeeds on live displays and collapses under `dscramble`;
- a bypass reader that accesses the hidden latch remains accurate and causes `audit_failed`.

## 3b. Exact 3-bit changes

### Channel

Support exactly two configurations initially:

```text
legacy: wiring=RING,  units=2, chain=0.0, TELL=200, HOLD=120
pairs3: wiring=PAIRS, units=6, chain=0.2, TELL=400, HOLD=240
```

Reject other dialogue configurations for now.

For signal `s ∈ [0,7]`, bit `j` drives pair `j` as:

```text
bit 0: (+0.8, -0.8)
bit 1: (-0.8, +0.8)
```

After HOLD, decode:

```text
b[j] = 0 if v[2j] - v[2j+1] > 0 else 1
word = b[0] | b[1] << 1 | b[2] << 2
```

The common mode is never read. `deaf` retains coupling `1.0` for the whole run.

The session randomly assigns eight signal glyphs to these eight drive words. That assignment is stable within the session and makes the convention private.

### Policies

Use flat categorical policies:

- sender: `referent[8] × signal[8]`;
- receiver: `held_word[8] × action[8]`;
- initial entries all `1.0`;
- retain the current reward-only `RATE = 0.3`.

Do not factor the policy into three 2×2 bit policies: that would impose compositional structure rather than allowing the eight-state convention to form.

The existing `pick` and `reinforce` logic generalizes mechanically; their one-agent-local aperture remains unchanged.

### Display

Direction B displays:

- three vertically stacked pair panels;
- two raw curves per panel;
- fixed neutral unit markers and colors for the session;
- only the final 60 HOLD samples;
- eight randomized referent buttons.

Never display the drive, signal glyph, differential, sign, packed word, target, success, or arm before the human acts.

### Rank beside accuracy

Report structural capacity and observed width separately:

> substrate: 3 differential latches / 8 held states  
> observed convention: effective rank `k/8 = log₂(k)` bits

For each stage, build an 8×8 modal-code matrix: a row receives a `1` only when it has a unique modal output; tied or undersampled rows remain zero. Its rank is the number of distinct resolved output symbols.

Report:

- sender rank `R→S`;
- held rank `S→W`;
- receiver/display rank `W→A`;
- end-to-end rank `R→A`;
- effective rank = their minimum.

Only `8/8 = 3.00 bits` may be called a 3-bit convention. A collapse to two outputs is reported as `2/8 = 1.00 bit`, regardless of accuracy or the substrate’s nominal capacity.

### Default stays exact

Extend the channel with default parameters corresponding to the legacy tuple. Keep the legacy execution branch unchanged; the PAIRS implementation is a separate branch.

Before refactoring, record a golden SHA-256 over the IEEE-754 bytes of all HOLD values for:

- both signals;
- deaf true/false;
- seeds `0…199`.

The test asserts that calling the new API with no wiring arguments produces the same golden hash and identical final latch results. Retain the existing comparison against the reproducible state harness. This pins the published 1-bit path, not merely its aggregate accuracy.

## 4. Honest framing

Maximum default claim:

> In this session, this person and this engine established and used two private directional eight-state conventions through consequence in feedback-free trials. The channel held three differential latch bits, and the observed effective rank was 8/8 in each direction.

Only with cross-direction agreement `8/8`:

> In this session, this person and this engine established and used a reciprocal private 3-bit convention through consequence.

Korean UI version:

> 이 세션에서 이 사람과 이 엔진은 결과를 통해 8개 상태를 구별하는 사적인 관례를 형성하고, 피드백 없는 시행에서 사용했습니다. 보유 기판은 3개의 차동 래치였고 관측 유효 폭은 8/8(3.00비트)이었습니다.

Forbidden claims include:

> The engine understood the person, knew what the symbol meant, chose a topic, felt something, used language, or held a human-like conversation.

Keep pattern-completion under control by using abstract cards only. No text box, semantic labels, emotions, “typing…” animation, conversational prose, or UI words such as “understood,” “meant,” or “said.” The tab may remain `소통`, but its permanent subtitle should be:

> 실시간 양방향 관례 교환 — 언어·이해가 아님

## 5. Minimal first commit

Implement the complete narrow vertical slice:

- preserve the current `DialogueSession` as `1비트 측정` research mode;
- add `ConversationSession` with `BASELINE/FREE/AUDIT/DONE`;
- add the proven six-unit PAIRS channel while keeping the legacy default bit-exact;
- add eight-card free turn selection and the alternating transcript;
- add frozen, deaf, signal-scramble, corrected display-scramble, and parallel yoked controls;
- add the 88-choice blind audit and per-session verdict;
- add stage ranks, effective bits, supports, counts, intervals, and nulls beside accuracy;
- persist started, completed, abandoned, and unaudited sessions—not only positive completions;
- update [RESULTS.md](/Users/mini/dancinlab/anima-reborn/state/communication/RESULTS.md) with the exact allowed and forbidden sentences;
- add aperture, lawful-display-reader, collapse-to-two-rank, null, and default-bit-exact tests.

Defer semantic vocabulary, text, topics, adaptive evidence, rolling free-log tests, more than eight states, compositional messages, and cross-person summaries. Those would create claims the substrate has not earned.
