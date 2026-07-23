── fable (claude-fable-5) · exit 0 ──
Design read against the shipped code: `state/communication/dialogue.py` (the harness whose `_channel`/`_pick`/`_reinforce` the live session must reuse, not copy), `src/anima_reborn/viewer/server.py` (ticker/handler/control architecture), and `page.html` (tab/PREFIX/`ko()`/render conventions). Here is the design.

---

# `소통` tab — design

## 0. Shape of the one commit

- **`src/anima_reborn/dialogue.py`** (new engine module, stdlib, seedable, zero I/O): `channel()`, `pick()`, `reinforce()` moved up from the state script, plus a new `DialogueSession` class with `step()` / `reset()` — so `TestEngineViewerLockstep` detects it structurally and enforces the full wiring.
- **`state/communication/dialogue.py`**: refactored to import those primitives (per `state/` rule: once a capability lands in `src/`, the script drives the shipped engine). `default-stays-exact`: the refactor must preserve RNG call order bit-for-bit; pin with a test asserting `play(seed=0)` still returns the exact published `a`/`b` values.
- **`src/anima_reborn/viewer/server.py`**: `_DialogueHandler`, `_HANDLERS["dialogue"]`, `Viewer.__init__` entry, `TICK_RATES["dialogue"] = 10.0`, plus session-log write-out (the viewer is the I/O boundary).
- **`src/anima_reborn/dialogue_stats.py`** (or a function set inside `dialogue.py`): the permutation test and verdict builder — one implementation, called by both the viewer and a new `state/communication/session_stats.py` re-derivation script. The browser computes nothing (viewer rule: the page maps values to pixels, period).
- **`page.html`**: tab `💬 소통`, `PREFIX["dialogue"] = "dg"`, `renderDialogue(d)`, `ko()` additions.
- **`tests/`**: the audits below as tests.
- **`state/communication/sessions/`**: one JSON log per session, written at session end (and a stub at session start — see traps).

---

## 1. Session protocol

One session = one person, one fresh `DialogueSession`, one append-only log. A **round** = one direction-A trial then one direction-B trial, matching the shipped harness's interleaving. Vocabulary: two **referent glyphs** (e.g. `●` `▲`) and two **signal buttons** with unrelated labels (`신호 ㄱ` / `신호 ㄴ`). The glyph↔referent-index assignment is drawn at random at session start and logged — the experimenter does not choose which glyph is 0.

**Direction A trial (human sends):** the page shows one referent glyph under the heading `이번에 전할 것`. The human presses one of the two signal buttons. Server-side: the signal drives `channel()` (TELL 200 + HOLD 120, computed instantly, never animated), engine acts `pick(engine_recv[word])`, harness computes `success = (act == referent)`. In feedback blocks the human sees `○`/`×` and the engine reinforces with the same bit. The human never sees the trace of their own signal (see trap 8) and never sees the engine's act (redundant anyway: with 2 acts, referent + success determines it).

**Direction B trial (engine sends):** harness draws a hidden referent; engine picks `pick(engine_send[referent])`; channel runs. The page receives **only the HOLD-phase raw trace** (120 samples × 2 units) and draws two curves. The human presses one of the two **referent-glyph buttons** — their act is "which referent I think was meant." Harness computes `success = (act == referent)`; feedback per block.

**Block schedule** (constants in `dialogue.py`; rounds, each = A+B):

| block (log name) | rounds | presented to human as | feedback | learning | engine policies |
|---|---|---|---|---|---|
| `day0` | 20 | `측정` | none | none | uniform |
| `train` | 60 | `학습` | real `○`/`×` | both sides | live |
| `probe` = `test` 20 + `frozen` 15 + `deaf` 15, **shuffled together** | 50 | `측정` | none | none | trained / day-0 snapshot / trained + deaf channel |
| `yoked_train` | 30 | `학습` | coin-flip `○`/`×` | both sides, random reward | **fresh** uniform, **new vocabulary** (`■`/`◆`, `신호 ㄷ`/`ㄹ`), new channel seeds |
| `yoked_test` | 15 | `측정` | none | none | yoked-trained |

~175 rounds / 350 clicks, roughly 15–25 minutes. All three controls come from this one person's log:

- **Day-0** runs first, feedback withheld, nothing learns. It measures the human's *prior* — including any iconicity the display leaks (see §2). Expected 0.5; if it isn't, that number is reported and the claim becomes trained-minus-day-0, not trained-minus-0.5.
- **Probe** trials are feedback-withheld and frozen (no `reinforce` calls anywhere in the probe phase — test stays held-out), and the three probe kinds are interleaved and unlabeled, so the human cannot adopt a per-block strategy.
- **Yoked** runs last with a fresh engine and fresh vocabulary, because the human cannot be reset: it asks whether this same, now-practiced person can acquire a *second* convention when the feedback is a coin. Running it post-practice biases *against* the claim (practice would help them if anything could), which is the conservative direction. Deviation from the reproducible half: reward is a Bernoulli(½) bit (shown as `○`/`×` and fed to `reinforce`) rather than `rng.random()`, because the human must see a binary outcome — documented in the module docstring.

The human is told before starting: "학습 구간에서는 결과가 보이고, 측정 구간에서는 보이지 않습니다" — and nothing else about block structure.

---

## 2. The second aperture — the display

Two different obligations, and the design must not confuse them:

- **The trace rendering is the channel itself and must be STABLE.** Unit 0 is always the same curve colour/position, all session. If unit assignment were re-randomized per trial, `sign(v₀−v₁)` would be unreadable and the channel to the human would be destroyed — the human learning "왼쪽 곡선이 높으면 ▲" *through consequence* is precisely the convention being established. Stability is not a leak; a *referent-dependent* rendering would be.
- **Everything tying display geometry to the ANSWER is randomized server-side, per trial**: the left/right order of the two glyph buttons (direction B) and of the two signal buttons (direction A) is drawn from the session RNG each trial, and the glyph↔referent-index assignment is drawn once per session. The page renders buttons in the order the server sends; the page itself randomizes nothing (otherwise the layout wouldn't be in the log).

What the direction-B pre-act frame contains, exactly: `{trial, dir:"b", trace:[[…120 floats…],[…]], buttons:[glyph,glyph]}`. What it must **never** contain: the referent, the latch bit, any derived summary of the trace (no sign, no mean, no difference), the correct act, or the TELL phase. Showing TELL would show the drive itself — the human would read the wire's input, not the engine's held state, and the engine would stop being load-bearing (`channel-before-carrier`). Only HOLD ships: 120 samples, drive already 0, engine autonomous.

The mapping to `act == referent` without the UI knowing the answer: the referent is drawn and **logged at trial creation**, held server-side in `DialogueSession`, never serialized to the page before the act. The human clicks a glyph; the session compares indices; the page learns only `○`/`×` (and in `측정` blocks, not even that). The answer is not in the DOM, not in the payload, not in devtools.

**Display audits (the first of the two audits), all structural, all tests:**
1. The function that builds a pending direction-B frame takes `(hold_values, layout_rng)` and nothing else — signature audit, same pattern as the existing `_reinforce` signature test (which moves up to `src` with the function).
2. Schema audit: a test drives a session to a pending B trial and asserts the frame's key set is exactly the allowed set above.
3. Trace audit: asserts `len(trace[0]) == HOLD` (not `TELL + HOLD`).
4. Behavioural: the day-0 block *is* the aperture audit run on the real display — above-chance day-0 means the display leaked, and the verdict text says so automatically.

---

## 3. The echo control, live

Chosen mechanism: **snapshot-revert probe trials**, not a parallel shadow policy — it is the exact live analogue of the reproducible `frozen_engine` arm and needs no second engine.

At session start (before any learning) the session snapshots all four engine-side policies — trivially uniform, but taken programmatically. During the probe phase, the 15 `frozen` rounds run with the engine's policies swapped to that day-0 snapshot for the trial, then swapped back; interleaved and invisible among `test` rounds. Direction A: the human's trained sending meets a day-0 decode map → expected 0.5 — so test-block success cannot be the human's self-consistency reflected back; the engine's *learned* half is demonstrably in the path. Direction B: day-0 `engine_send` emits referent-independent signals → the human's trained reading lands at 0.5 — this doubles as the live **scramble** null, so no separate scramble block is needed.

The 15 `deaf` rounds (channel coupling 1.0 during TELL, drive bit-unreachable; trained policies) close the other half: both directions must fall to chance, proving the channel was in the path at all. If a deaf HOLD trace happens to look visibly odd, that does not rescue anything — the statistic is accuracy, and the referent information is absent from the trace by construction; detectability of the arm is not success in it.

Structural echo audit (the second of the two audits): the engine's act in direction A is produced by `pick(engine_recv[word])` where `word` comes only from the channel latch — `reinforce`'s signature has no argument for the other agent's state (existing test, retargeted at the `src` module), and a new test asserts the direction-A code path never receives the human's raw button identity, only the latch bit that survived the engine.

---

## 4. Per-session statistics

All computed by the shared Python stats module from the log; the log is self-contained (every referent, act, layout, and coin is logged explicitly, so analysis never re-runs RNG).

**Test statistic:** test-block accuracy, **per direction**: `obs_A = #(engine_act == referent)/20` over the 20 `test` rounds' A trials; `obs_B` likewise for the human's acts. Never combined, never averaged with each other.

**Permutation:** shuffle the referent sequence across the 20 test trials of that direction (margins fixed — this respects the human's/engine's response bias: an 80/20 act split changes the null, and the permutation prices that in), recompute accuracy per shuffle. 10,000 permutations, RNG seed for the shuffles logged in the results block. `p = (1 + #{perm ≥ obs}) / (1 + 10000)`. (This is Fisher's exact null on the 2×2 referent×act table, implemented as a permutation so it stays stdlib and generalizes if the game ever grows past 2×2.)

**Rank/width beside every accuracy (`report-the-rank`):** each accuracy ships with its raw counts (`18/20`) and the **symbol-usage margins** — e.g. `신호 사용 11:9`, `행동 사용 12:8`. A code collapsed to one symbol shows itself there and caps its own permutation null; the margins are the width of the code.

**The controls, each with its number:** day-0 (n/20 + its own permutation p — this is the display-leak check), frozen (n/15), deaf (n/15), yoked_test (n/15), each expected ~0.5. **Cross-direction consistency** per session: does the human's majority referent→signal map (from train-block behaviour) agree with the engine's? Reported as its own line (0, ½, or 1), never folded into anything — two one-way codes is the expected honest outcome, as in the synthetic run (58%).

**Verdict**, α = 0.01 per direction, fixed in code before any session, per-direction strings keyed off raw values through `ko()`:

- Formed: `A(사람→엔진): 관례 형성 — 18/20, p=0.0002` 
- Not formed: `B(엔진→사람): 근거 없음 — 12/20, p=0.25`
- Auto-caveats appended when triggered: day-0 above chance (`주의: 학습 전 정확도가 우연을 넘음 — 표시 장치 누출 가능`), any control significantly off 0.5, degenerate margins.
- The maximal headline, only when both the direction's p < α **and** frozen/deaf/yoked sit at chance: `이 사람과 이 엔진은 결과만을 통해 1비트 사적 관례를 만들고 사용했다.` One session, one person, existence proof — the verdict never claims more, and an aborted session's verdict is `중단됨 — 판정 없음`.

**Yoked honesty note baked into the verdict text:** yoked-at-chance cannot distinguish "nothing to learn from a coin" from "the human disengaged"; it is supporting evidence. The load-bearing per-session nulls are the permutation test plus frozen/deaf. Say so rather than overclaiming the yoked arm.

---

## 5. server.py / page.html wiring

**The session object** is `DialogueSession(seed=…)` in `src/anima_reborn/dialogue.py` — pure, stdlib, no clock/thread/socket (`engine-purity`); it holds: the four policies + day-0 snapshots, the block schedule and cursor, the pending trial (direction, committed referent, layout), the append-only in-memory log, and `stats()`. It exposes `step()` and `reset()` so the lockstep test finds it and forces the full 7-point wiring.

**It is not free-running, but it still lives under a `_Ticker`** — the existing control path is exactly the human-input channel, so no new HTTP verbs are needed:

- `TICK_RATES["dialogue"] = 10.0` — 10 Hz is an input-latency bound, not a simulation rate.
- Human clicks → the page hits `/api/dialogue/control?trial=<id>&input=<0|1>&token=<t>`; `ticker.control()` stores it; the ticker applies it via `configure()` before the next `step()`, so input never races a step — the existing race-free pattern, reused.
- **Idempotency is mandatory**: `_Ticker._controls` is *not* cleared after application and `configure` re-runs every tick, so an input must carry its `trial` id and the session must ignore ids already resolved. A test drives two ticks with the same control dict and asserts the log gained exactly one entry.
- `step()` is the drain point: if a valid pending input exists, resolve the trial — run `channel()` inline (320 ticks in microseconds; the TELL/HOLD run is never animated, so there is no timing side-channel correlated with the referent), compute the act, compute success **inside the session** (the harness seat: neither party ever grades itself — the engine's `reinforce` receives the harness bit, the human's `○`/`×` renders the harness bit), append the log entry, advance the schedule, draw the next trial's referent + layout and log them immediately. With no pending input, `step()` returns without mutating anything (pinned by a test — a no-op step must be bit-exact no-op).
- `describe()` reads only (viewer rule): `{phase, block_presented ("learn"/"measure"/"waiting"/"done"), round, total, pending: {dir, glyph|trace, buttons}, feedback, token}` — plus, in `done` phase only, the full `stats()` result. **During `측정`-presented blocks the frame carries no success information and no running tally** — only `k / K 진행`. The true block name (`test`/`frozen`/`deaf`) exists in the log, never in the frame.
- `reset` starts a fresh session and issues a new single-seat token; inputs with a stale token are ignored, so a second browser tab can watch but not answer.
- **Session-end I/O lives in the viewer layer**: when the session reaches `done`, the handler (not the session) writes the session's JSON dict to `state/communication/sessions/YYYY-MM-DD-HHMMSS.json`, once; it also writes a stub at session start (trap 5 below). Nothing about a trial is printed to stdout.

**page.html:** tab button `💬 소통`, panel, `PREFIX["dialogue"] = "dg"`, `renderDialogue(d)` drawing the two HOLD curves on a canvas, buttons in server-given order, `○`/`×` flash, progress line, and the final results table verbatim from `stats()`. `ko()` gains raw-keyed entries (`"learn"→"학습"`, `"measure"→"측정"`, `"waiting"→"대기"`, `"done"→"종료"`, verdict keys); badge classes key off the raw values; unmapped values fall through. Restart the server after landing (`viewer-restart`).

---

## 6. Traps to refuse (beyond the two named)

1. **Optional stopping / session file-drawer.** The operator *is* the participant; they could abandon bad sessions and keep the good one — a human 12-seeds-quietly-become-1 in reverse. Kill: a log stub is written at session *start*, aborted sessions persist as `중단됨 — 판정 없음`, and any report of a session must state how many session files exist in `state/communication/sessions/`. The stats script prints that count unconditionally.
2. **Live accuracy display leaking feedback into measure blocks.** A running tally is feedback. Kill: `측정` frames carry no success data at all; enforced by the schema audit test extended to probe-phase frames.
3. **Block-identity leakage → per-block strategy.** If the human can tell frozen/deaf trials apart from test trials, they can't *gain* accuracy (the information isn't there) but a visible structure invites weirdness in the log. Kill: probe kinds shuffled, identical presentation, block name absent from every frame.
4. **Training bleeding into the held-out measure.** Any `reinforce` during probe makes test-block accuracy partly trained-on-test. Kill: the probe phase makes zero `reinforce` calls; a test counts them.
5. **Post-hoc grading.** If the referent were drawn or could be re-drawn after the act, the harness seat is corrupted. Kill: referent committed to the log at trial *creation*; the analysis script checks every log entry's creation-order invariant.
6. **The page as a second implementation.** Any JS that computes a latch, an accuracy, or a p-value will drift from the Python and become the thing being measured. Kill: page renders server values only (existing viewer rule); the state-side `session_stats.py` re-derives every viewer-shown number from the raw log — same module, two callers.
7. **Double-applied input** from the persistent controls dict (9-threads-ticking-one-engine's cousin) — killed by trial-id idempotency + test, as above.
8. **The self-echo training set.** Showing the human the HOLD trace of *their own* direction-A signal hands them a labeled (signal → trace) corpus outside the reward loop; direction-B "reading" would then owe to a supervised side-channel, not consequence. Kill: direction A shows nothing but the referent, the buttons, and `○`/`×`.
9. **Averaging where averaging is forbidden.** Directions averaged into a fake symmetric code (the 58% lesson), or sessions averaged into a population claim. Kill: verdict strings are structurally per-direction and per-session; the stats module has no function that aggregates across sessions.
10. **Position as a covert codec.** A fixed geometric correspondence (left button ↔ left curve) is an experimenter-installed bridge. Kill: per-trial server-side layout randomization, logged, plus a post-hoc check in `session_stats.py` that layout does not predict referent in the log.

The two audits, named as deliverables: **(A) aperture audit** — frame-builder signature + schema + HOLD-only tests, with day-0 as its behavioural arm; **(B) echo audit** — `reinforce` signature test retargeted at `src`, plus the interleaved frozen/deaf probe arms as its behavioural half. Both live in `tests/`, both fail loudly, neither depends on anyone remembering.

The maximum sentence a perfect session earns stays what it was: *this* person and *this* engine established and used a private 1-bit convention through consequence — with the day-0, frozen, deaf, yoked and permutation numbers printed beside it, and nothing more.

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
session id: 019f8d50-8055-72d0-a9f3-b6ef9842453e
--------
user
# Design task: the `소통` (dialogue) tab in the anima-reborn viewer — human takes the partner's seat

You are designing a NEW viewer tab for a Python research repo. Return a concrete, implementable
design. This is the human↔engine half of a communication experiment whose reproducible
(synthetic-partner) half already shipped. Do NOT write the full code — return the DESIGN
(data flow, protocol, controls, stats, and the two audits), precise enough that an engineer
implements it in one commit without further decisions.

## Context you must respect (this repo has repeatedly caught itself on exactly these traps)

The shipped reproducible half is `state/communication/dialogue.py`. Key facts:

- A **Lewis-Skyrms 2x2 signaling game**, BOTH directions, against a SYNTHETIC seeded partner.
  Direction A: partner picks a signal for a referent → engine holds it deaf and acts by which
  probe its held state revises less → success = (act == referent), computed by the harness.
  Direction B: engine picks a signal for a hidden referent → partner reads held word and acts.
- The channel `_channel(signal, seed, deaf)` is a 2-unit RING `CoupledEngine`: drive the signal
  during a TELL phase (ALTERNATING rhythm), then freeze (FIXED, drive=0) for a HOLD phase, read
  latch bit = sign(values[0]-values[1]). `deaf=True` sets coupling 1.0 so the drive is unreachable.
- The ONLY update rule: `_reinforce(policy, state, choice, reward)` — reads ONE agent's own
  (state, choice, success). Structural static audit: its signature has NO argument for the other
  agent's state. A test inspects the signature.
- Measured (synthetic partner, 12 dyads): trained A 0.922 / B 0.873; day-0 0.500; yoked 0.489;
  frozen-engine (echo test) 0.496; deaf 0.486; scramble 0.516; partner-swap 0.501.
  Cross-direction consistency 58% → reported as TWO one-way codes, never averaged into a fake
  symmetric one.
- The max sentence obtainable is small: "THIS person and THIS engine established and used a
  private 1-bit convention through consequence." Not understanding, not language.

The two named traps for the HUMAN half (the whole reason a human can't just be a 13th seed):

1. **The human is not seedable** → the human claim is a PER-SESSION EXISTENCE PROOF, never
   averaged over people. It needs its OWN day-0, its OWN yoked block, and a PERMUTATION TEST on
   the human's own log. The human is data, not a controlled variable.
2. **The experimenter-owned interpreter** has two mouths, both must be sealed IN THE VIEWER:
   - the DISPLAY codec (engine→human: the human reads whatever render we chose) → the display is
     the SECOND APERTURE: raw traces only, positions randomized, success task-derived — the
     display must NOT encode the answer.
   - the ECHO trap (human→engine: engine hands the input back so "recovery" measures the human's
     own self-consistency) → already controlled in the reproducible half by frozen-engine; design
     how the live session reproduces this control.

## Existing viewer architecture (all current tabs are PASSIVE auto-ticking observers — this is different)

- `server.py`: `TICK_RATES` dict, `_HANDLERS` dict {name: handler}, `class Viewer.__init__`
  builds one `_Ticker(guarded, handler, rate)` per engine, streams JSON per tick over SSE-ish loop.
- `page.html`: per-tab `<button data-tab=NAME>`, a panel div, `PREFIX[name]`, `renderNAME(data)`.
- `viewer-newengine` rule: new engine → `_HANDLERS` + `Viewer.__init__` + `TICK_RATES` in server.py,
  then tab + panel + PREFIX + render in page.html. `tests/test_viewer.py::TestEngineViewerLockstep`
  fails on each omission.
- `ui-language`: Korean displayed strings via a `ko()` map; badge colour keys off the RAW value,
  never the translated string; unmapped values fall through.
- `engine-purity`: engines are stdlib-only, seedable, NO I/O; all I/O confined to viewer/.
- The `소통` tab is SESSION-SCOPED and INTERACTIVE (human clicks/inputs), unlike every other tab.

## What I need from you — answer each explicitly

1. **Session protocol.** Concretely: how does one live human session run? What does a "trial" look
   like from the human's side (what they see, what they input), for BOTH directions? How many
   trials, how are the day-0 block / yoked block / test block laid out in ONE session so all three
   controls come from the SAME person's log?
2. **The second aperture — display.** Exactly what raw signal is shown to the human and how is it
   randomized so the display cannot encode the answer? Give the concrete randomization (position
   swap? label scramble? per-trial?). How does the human's action map to (act==referent) WITHOUT
   the UI telling them which is right?
3. **The echo control, live.** How does the running session reproduce the frozen-engine null so we
   can show the human's recovery isn't the engine echoing them back? (A frozen-engine block in the
   same session? A parallel shadow policy?)
4. **The per-session statistics.** The exact permutation test on the human's own log: what is
   permuted, what is the test statistic, how many permutations, what's the null, what verdict
   string is honest. Remember: NO averaging over people, small max claim.
5. **server.py / page.html wiring.** What is the session-scoped engine object (it can't be a free-
   running ticker — it waits on human input)? How does the tick loop / handler differ from the
   passive engines? What state does the handler hold and stream? Where does the harness compute
   success so neither party self-rewards?
6. **Traps to refuse.** Name the ways this specific design could fake a positive result (beyond the
   two above) and the control that kills each.

Keep the honesty discipline of the repo: ship every claim with the null that could fake it; report
the rank/width beside any accuracy; a lossy stage can't create what wasn't fed to it; the display
is a channel that must be scored before crediting what leaves it.

codex
I’ll inspect the shipped dialogue harness and viewer/test contracts first, then turn those exact interfaces into a session protocol with no unresolved implementation choices.
exec
/bin/zsh -lc "sed -n '1,280p' state/communication/dialogue.py && sed -n '1,260p' viewer/server.py && rg -n \"TICK_RATES|_HANDLERS|class Viewer|PREFIX|render[A-Za-z]|data-tab|ko\\(\" viewer/page.html tests/test_viewer.py" in /Users/mini/dancinlab/anima-reborn
 exited 1 in 0ms:
"""Toward human<->engine dialogue: the reproducible half, with a synthetic partner.

Run from the repo root:

    PYTHONPATH=src python state/communication/dialogue.py

The goal is a two-way convention between a HUMAN and the engine — a person and
this substrate reaching a shared code through a live loop in the viewer. A human
is not seedable and cannot be a controlled variable, so the claim is split, as
both delegated designs insisted:

- **the reproducible claim** lives here, measured against a SYNTHETIC partner — a
  seedable stand-in for the human, so 12-seed directional bars and every null are
  possible. The real human takes the partner's seat later, in the viewer.
- **the human claim** will be a per-session existence proof (its own day-0, its
  own yoked block, a permutation test on its own log), never averaged over people.

**What is measured here.** Both directions of a Lewis-Skyrms game. Partner-sends:
the partner picks a signal for a referent, the engine holds it deaf and acts by
which probe its held state revises less (the `match.py` assay — no fitted decoder,
no chosen threshold). Engine-sends: the engine picks a signal for a hidden
referent, holds it, and the partner reads the held word and acts. Success is
`act == referent`, computed by the harness — NEVER judged by either party, so
nobody can reward their own intention.

**The static audit — the trap both designs named.** For engine-engine it was the
codec installed in the training loop; for human-engine it is the experimenter
owning the interpreter. The engine-side guarantee is unchanged and structural:
each update reads only its OWN agent's (state, choice, success). `_reinforce`
takes a single policy, one of its rows, a column, and the success bit — it cannot
see across the gap. In the viewer the display becomes the second aperture (raw
traces only, positions randomized); that is enforced there.

**The echo trap, caught here.** If the engine merely handed the partner's bit
back, "recovery" would measure the partner's self-consistency. The `frozen-engine`
arm freezes the engine's policy at its random day-0 map: a fully trained partner
must then collapse to chance, proving the engine's LEARNED half is load-bearing.
The `deaf` arm (coupling 1.0, drive unreachable) must sit at chance, proving the
channel was even in the path.
"""

from __future__ import annotations

import random
import statistics

from anima_reborn.coupled import ALTERNATING, FIXED, CoupledEngine, Wiring

EPISODES = 1200
RATE = 0.3
TAIL = 300
SEEDS = 12
TELL = 200
HOLD = 120


def _channel(signal: int, *, seed: int, deaf: bool = False) -> int:
    """The engine as a noisy 1-bit wire: hold a signal, read the latch bit.

    `deaf` sets coupling to 1.0 for the listen phase so the drive is unreachable
    — the held bit then owes nothing to the signal, which is the null proving the
    channel was in the path."""
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


def _pick(row: list[float], rng: random.Random) -> int:
    total = sum(row)
    threshold = rng.random() * total
    cumulative = 0.0
    for i, weight in enumerate(row):
        cumulative += weight
        if threshold < cumulative:
            return i
    return len(row) - 1


def _reinforce(policy: list[list[float]], state: int, choice: int, reward: float) -> None:
    """The only update rule. Reads ONE agent's own (state, choice, success). It
    is handed a single policy and cannot reach the other agent — the static audit
    is that this signature has no argument for anyone else's state."""
    policy[state][choice] += RATE * reward


def play(
    seed: int,
    *,
    episodes: int = EPISODES,
    yoked: bool = False,
    frozen_engine: bool = False,
    deaf: bool = False,
) -> dict[str, object]:
    """One dyad — synthetic partner and engine — learning both directions."""
    rng = random.Random(seed)
    # Four policies, each 2x2, symmetric at day-0 so which convention forms is the
    # dyad's own history, not ours.
    partner_send = [[1.0, 1.0], [1.0, 1.0]]  # partner: referent -> signal
    engine_recv = [[1.0, 1.0], [1.0, 1.0]]  # engine: held word -> act
    engine_send = [[1.0, 1.0], [1.0, 1.0]]  # engine: referent -> signal
    partner_recv = [[1.0, 1.0], [1.0, 1.0]]  # partner: held word -> act
    a_hist, b_hist = [], []

    for ep in range(episodes):
        # Direction A — partner sends, engine receives and acts.
        referent = rng.randrange(2)
        signal = _pick(partner_send[referent], rng)
        word = _channel(signal, seed=seed * 7 + ep, deaf=deaf)
        act = _pick(engine_recv[word], rng)
        success = 1.0 if act == referent else 0.0
        a_hist.append(success)
        reward = rng.random() if yoked else success
        _reinforce(partner_send, referent, signal, reward)
        if not frozen_engine:
            _reinforce(engine_recv, word, act, reward)

        # Direction B — engine sends, partner receives and acts.
        referent_b = rng.randrange(2)
        signal_b = _pick(engine_send[referent_b], rng)
        word_b = _channel(signal_b, seed=seed * 11 + ep, deaf=deaf)
        act_b = _pick(partner_recv[word_b], rng)
        success_b = 1.0 if act_b == referent_b else 0.0
        b_hist.append(success_b)
        reward_b = rng.random() if yoked else success_b
        if not frozen_engine:
            _reinforce(engine_send, referent_b, signal_b, reward_b)
        _reinforce(partner_recv, word_b, act_b, reward_b)

    return {
        "a": statistics.mean(a_hist[-TAIL:]),
        "b": statistics.mean(b_hist[-TAIL:]),
        "policies": (partner_send, engine_recv, engine_send, partner_recv),
    }


def _probe(policies, *, seed: int, direction: str, scramble: bool = False,
           trials: int = 200) -> float:
    """Frozen, feedback-withheld recovery — the held-out analogue for a game."""
    partner_send, engine_recv, engine_send, partner_recv = policies
    rng = random.Random(seed + 9000)
    hits = 0
    for ep in range(trials):
        referent = rng.randrange(2)
        if direction == "a":
            signal = _pick(partner_send[referent], rng)
            if scramble:
                signal = rng.randrange(2)
            word = _channel(signal, seed=seed * 7 + ep + 5000)
            hits += _pick(engine_recv[word], rng) == referent
        else:
            signal = _pick(engine_send[referent], rng)
            if scramble:
                signal = rng.randrange(2)
            word = _channel(signal, seed=seed * 11 + ep + 5000)
            hits += _pick(partner_recv[word], rng) == referent
    return hits / trials


def _cross_direction_consistency(policies) -> float:
    """Do the two directions use the SAME code, or are they two one-way codes?
    Compares the referent->signal maps a partner and an engine settled on."""
    partner_send, _, engine_send, _ = policies
    agree = sum(
        (partner_send[r][0] > partner_send[r][1]) == (engine_send[r][0] > engine_send[r][1])
        for r in (0, 1)
    )
    return agree / 2


def main() -> None:
    print("human<->engine dialogue — the reproducible half, synthetic partner")
    print(f"{EPISODES} episodes, {SEEDS} dyads, both directions, 2-unit ring channel\n")

    dyads = [play(seed) for seed in range(SEEDS)]
    trained_a = [d["a"] for d in dyads]
    trained_b = [d["b"] for d in dyads]
    yoked = [play(s, yoked=True)["a"] for s in range(SEEDS)]
    frozen = [play(s, frozen_engine=True)["a"] for s in range(SEEDS)]
    deaf = [play(s, deaf=True)["a"] for s in range(SEEDS // 2)]
    scrambled = [_probe(d["policies"], seed=i, direction="a", scramble=True)
                 for i, d in enumerate(dyads)]
    swapped = [
        _probe(
            (dyads[i]["policies"][0], dyads[j]["policies"][1], None, None),
            seed=i * 100 + j, direction="a",
        )
        for i in range(SEEDS) for j in range(SEEDS) if i != j
    ]
    consistency = statistics.mean(
        _cross_direction_consistency(d["policies"]) for d in dyads
    )

    print(f"{'arm':<28}{'recovery':>10}{'worst':>9}   verdict")
    print("-" * 62)
    print(f"{'trained (partner->engine)':<28}{statistics.mean(trained_a):>10.3f}"
          f"{min(trained_a):>9.3f}   a convention formed")
    print(f"{'trained (engine->partner)':<28}{statistics.mean(trained_b):>10.3f}"
          f"{min(trained_b):>9.3f}   the other direction too")
    print(f"{'day-0 (untrained)':<28}{0.5:>10.3f}{0.5:>9.3f}   chance")
    print(f"{'yoked feedback':<28}{statistics.mean(yoked):>10.3f}"
          f"{min(yoked):>9.3f}   consequence establishes it")
    print(f"{'frozen engine (echo test)':<28}{statistics.mean(frozen):>10.3f}"
          f"{min(frozen):>9.3f}   the ENGINE is load-bearing")
    print(f"{'deaf channel':<28}{statistics.mean(deaf):>10.3f}"
          f"{min(deaf):>9.3f}   the channel is in the path")
    print(f"{'signal scrambled':<28}{statistics.mean(scrambled):>10.3f}"
          f"{min(scrambled):>9.3f}   the signal is necessary")
    print(f"{'partner swap (all cross)':<28}{statistics.mean(swapped):>10.3f}"
          f"{'—':>9}   PRIVATE to a shared history")
    print(f"\n  cross-direction consistency: {consistency:.0%} "
          f"(1.0 = one shared code, 0.5 = two one-way codes)")

    wins = sum(a > 0.5 for a in trained_a)
    print(
        f"\n  trained beats day-0 on {wins}/{SEEDS} dyads. The frozen-engine arm is"
        f"\n  the one that matters most here: at day-0 engine maps a fully trained"
        f"\n  partner cannot recover, so the engine's LEARNED half carries the code —"
        f"\n  this is not the engine echoing the partner's input. This measures the"
        f"\n  ENGINE half; the human takes the partner's seat in the viewer, where the"
        f"\n  display becomes the second thing that must not encode the answer."
    )


if __name__ == "__main__":
    main()
sed: viewer/server.py: No such file or directory

exec
/bin/zsh -lc "rg --files | rg '("'^|/)(server'"\\.py|page\\.html|test_viewer\\.py|AGENTS\\.md)"'$'"'" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
src/anima_reborn/viewer/server.py
src/anima_reborn/viewer/page.html
tests/test_viewer.py

exec
/bin/zsh -lc "sed -n '1,360p' src/anima_reborn/viewer/server.py && sed -n '1,280p' tests/test_viewer.py && rg -n \"data-tab|PREFIX|function ko|const ko|render[A-Za-z]|EventSource|fetch\\(\" src/anima_reborn/viewer/page.html" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
"""The viewer's HTTP server — stdlib only, one engine of each kind.

Frames are **pushed**, not polled. Each engine has a ticker thread that steps it
at the origin's own rate — 60 Hz for emergence, 30 Hz for the repulsion field
and the pipeline, 20 Hz for the crystal — and publishes each new state to
whoever is subscribed over a single long-lived `text/event-stream` connection.
The page opens one stream, receives frames as fast as the engine produces them,
and draws on the display's own refresh.

Pulling instead would cap the frame rate at the poll interval and pay a request
round trip per frame; the engines cost 0.02-0.23 ms per tick, so that cap was
the only thing standing between this viewer and the origin's 60 fps.

A ticker runs only while at least one viewer is watching it, which is the same
thing the origin's page did by skipping inactive tabs.

One instance of each engine is shared by every connected browser, so two tabs
watch the same run rather than two diverging ones. A lock guards each engine,
since the server is threaded and the engines are mutable.
"""

from __future__ import annotations

import json
import socket
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from ..align import Aligner
from ..base import BaseEngine
from ..coupled import (
    ALTERNATING,
    FIXED,
    NAMES as COUPLED_NAMES,
    CoupledEngine,
    Wiring,
)
from ..crystal import TimeCrystal
from ..emergence import EmergenceEngine
from ..pipeline import Pipeline
from ..repulsion import RepulsionField

__all__ = ["Viewer", "serve"]

PAGE = Path(__file__).parent / "page.html"

MAX_STEPS_PER_REQUEST = 240
"""Cap on the `steps` of a one-shot `/api/<engine>` request. The streaming path
does not use it — a ticker's rate is fixed by the server, not by the client."""

TICK_RATES = {
    "emergence": 60.0,
    "crystal": 20.0,
    "repulsion": 30.0,
    "pipeline": 30.0,
    "base": 30.0,
    "coupled": 30.0,
    "align": 60.0,
}
"""Ticks per second, carried from the origin's `setInterval` periods so the
engines run at the speed their thresholds were chosen against."""

PING_SECONDS = 10.0
"""How long a stream waits for a frame before sending a keep-alive comment. A
paused engine must still notice that its viewer has gone away."""


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(slots=True)
class _Guarded:
    """An engine and the lock that serializes access to it."""

    engine: Any
    lock: threading.Lock


def _number(params: dict[str, list[str]], key: str, default: float) -> float:
    raw = params.get(key)
    if not raw:
        return default
    try:
        return float(raw[0])
    except ValueError:
        return default


def _round(values: Any, places: int = 4) -> list[float]:
    """Trim the float noise out of the wire format — the page draws pixels, and
    seventeen significant digits per sample is most of the payload."""
    return [round(float(v), places) for v in values]


class _EmergenceHandler:
    @staticmethod
    def configure(engine: EmergenceEngine, params: dict[str, list[str]]) -> None:
        engine.coupling = _clamp(_number(params, "coupling", engine.coupling), 0.0, 1.0)

    @staticmethod
    def describe(engine: EmergenceEngine) -> dict[str, Any]:
        metrics = engine.metrics
        return {
            "left": _round(engine.left),
            "right": _round(engine.right),
            "ticks": engine.ticks,
            "range": engine.binning.vrange,
            "metrics": None
            if metrics is None
            else {
                "h_left": metrics.h_left,
                "h_right": metrics.h_right,
                "h_joint": metrics.h_joint,
                "mi": metrics.mutual_information,
                "verdict": metrics.verdict.value,
            },
        }


class _CrystalHandler:
    @staticmethod
    def configure(engine: TimeCrystal, params: dict[str, list[str]]) -> None:
        engine.epsilon = _clamp(_number(params, "epsilon", engine.epsilon), 0.0, 1.0)

    @staticmethod
    def describe(engine: TimeCrystal) -> dict[str, Any]:
        state = engine.state
        return {
            "spins": list(engine.spins),
            "history": _round(engine.history),
            "magnetization": state.magnetization,
            "ac1": state.ac1,
            "ac2": state.ac2,
            "ac4": state.ac4,
            "verdict": state.verdict.value,
        }


class _RepulsionHandler:
    @staticmethod
    def configure(engine: RepulsionField, params: dict[str, list[str]]) -> None:
        engine.separation = _clamp(_number(params, "separation", engine.separation), 0.0, 2.0)
        engine.noise = _clamp(_number(params, "noise", engine.noise), 0.0, 1.0)

    @staticmethod
    def describe(engine: RepulsionField) -> dict[str, Any]:
        state = engine.state
        if state is None:  # unreachable — a frame is only cut after a step
            raise ValueError("repulsion field has not been stepped")
        return {
            "a": _round(engine.a),
            "g": _round(engine.g),
            "concept": _round(state.concept),
            "meaning": _round(state.meaning),
            "context": _round(state.context),
            "sender": _round(state.sender),
            "tension": state.tension,
            "topic": state.topic,
            "curiosity": state.curiosity,
            "authenticity": state.authenticity,
            "mood": state.mood.value,
            "ticks": engine.ticks,
        }


class _PipelineHandler:
    @staticmethod
    def configure(engine: Pipeline, params: dict[str, list[str]]) -> None:
        engine.separation = _clamp(_number(params, "separation", engine.separation), 0.0, 2.0)

    @staticmethod
    def describe(engine: Pipeline) -> dict[str, Any]:
        state = engine.state
        return {
            "a": _round(engine.a),
            "g": _round(engine.g),
            "left": _round(engine.left),
            "right": _round(engine.right),
            "range": engine.binning.vrange,
            "tension": state.tension,
            "h_left": state.h_left,
            "h_right": state.h_right,
            "h_joint": state.h_joint,
            "mi": state.mutual_information,
            "verdict": state.verdict.value,
            "ticks": engine.ticks,
        }


class _BaseHandler:
    @staticmethod
    def configure(engine: BaseEngine, params: dict[str, list[str]]) -> None:
        engine.epsilon = _clamp(_number(params, "epsilon", engine.epsilon), 0.0, 1.0)
        engine.separation = _clamp(
            _number(params, "separation", engine.separation), 0.0, 2.0
        )

    @staticmethod
    def describe(engine: BaseEngine) -> dict[str, Any]:
        state = engine.state
        return {
            "a": _round(engine.a),
            "g": _round(engine.g),
            "left": _round(engine.left),
            "right": _round(engine.right),
            "magnetization": _round(engine.magnetization),
            "range": engine.binning.vrange,
            "phase": state.phase,
            "tension": state.tension,
            "h_left": state.h_left,
            "h_right": state.h_right,
            "mi": state.mutual_information,
            "verdict": state.verdict.value,
            "rhythm": state.crystal.verdict.value,
            "ac1": state.crystal.ac1,
            "ac2": state.crystal.ac2,
            "ticks": engine.ticks,
        }


class _CoupledHandler:
    """The coupled field.

    Phi is far too slow to compute per frame, so the panel streams the live
    dynamics and the measurement is a separate, deliberate act — the operator
    presses for it. A number this conditional should not arrive as ambient
    decoration.

    The rhythm is the one control here whose effect is visible without any
    measurement: on a fixed coupling the drive slider does nothing at all, which
    is the wall as something to watch rather than a claim to read.
    """

    @staticmethod
    def configure(engine: CoupledEngine, params: dict[str, list[str]]) -> None:
        raw = params.get("wiring")
        if raw:
            try:
                wiring = Wiring(raw[0])
            except ValueError:
                return  # unknown value: leave the engine as it is
            if wiring is not engine.wiring:
                engine.wiring = wiring
                engine.reset()  # a different wiring is a different system
        rhythms = params.get("rhythm")
        if rhythms:
            # Unknown value keeps the current rhythm, as with every control here.
            rhythm = {"fixed": FIXED, "alternating": ALTERNATING}.get(
                rhythms[0], engine.rhythm
            )
            if rhythm != engine.rhythm:
                engine.rhythm = rhythm
                engine.reset()  # a different rhythm is a different system
        engine.gain = max(0.1, _number(params, "gain", engine.gain))
        engine.drive = max(-1.0, min(1.0, _number(params, "drive", engine.drive)))

    @staticmethod
    def describe(engine: CoupledEngine) -> dict[str, Any]:
        state = engine.state
        return {
            "names": list(COUPLED_NAMES),
            "values": _round(state.values),
            "sources": [
                -1 if s is None else s for s in engine.wiring.sources
            ],
            "wiring": engine.wiring.value,
            "cyclic": engine.wiring.is_cyclic,
            "amplitude": engine.amplitude,
            "gain": engine.gain,
            "tension": state.tension,
            "pattern": state.pattern,
            "ticks": state.ticks,
            "rhythm": "alternating" if engine.rhythm.alternates else "fixed",
            "period": engine.rhythm.period or 0,
            "drive": engine.drive,
            "coupling": round(state.coupling, 4),
            "listening": state.listening,
            "reachable": engine.rhythm.mean < 1.0,
        }


class _AlignHandler:
    """The learner.

    Scoring is far more expensive than learning, so `describe` reads `state`
    once per frame while the ticker takes many steps between frames — the cost
    ratio the engine's own docstring warns about, respected here.
    """

    @staticmethod
    def configure(engine: Aligner, params: dict[str, list[str]]) -> None:
        engine.rate = max(1e-4, _number(params, "rate", engine.rate))
        engine.noise = max(0.0, _number(params, "noise", engine.noise))
        wanted = params.get("shuffled")
        if wanted:
            shuffled = wanted[0] == "1"
            if shuffled is not engine.shuffled:
                engine.shuffled = shuffled
                engine.reset()  # a different training regime is a different run

    @staticmethod
    def describe(engine: Aligner) -> dict[str, Any]:
        state = engine.state
        # One held-out concept, drawn the same way every frame, so the page can
        # show where its two modalities currently land.
        left = engine.project(engine.observe(10_000, modality=0), modality=0)
        right = engine.project(engine.observe(10_000, modality=1), modality=1)
        return {
            "same": state.same_concept,
            "different": state.different_concept,
            "gap": state.gap,
            "initial_gap": state.initial_gap,
            "learned": state.learned,
            "aligned": state.aligned,
            "pairs": state.pairs_seen,
            "shuffled": engine.shuffled,
            "rate": engine.rate,
            "noise": engine.noise,
            "left": _round(left),
            "right": _round(right),
        }


_HANDLERS: dict[str, Any] = {
    "emergence": _EmergenceHandler,
    "crystal": _CrystalHandler,
    "repulsion": _RepulsionHandler,
    "pipeline": _PipelineHandler,
    "base": _BaseHandler,
    "coupled": _CoupledHandler,
    "align": _AlignHandler,
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

    @property
"""The viewer — that it drives the real engines, and does so exactly once.

These exercise `Viewer` directly rather than over a socket: the HTTP layer is
stdlib, the part worth testing is the wiring between the page's controls and
the engines.
"""

from __future__ import annotations

import importlib
import inspect
import json
import re
import time
from pathlib import Path

import pytest

import anima_reborn
from anima_reborn.viewer.server import (
    MAX_STEPS_PER_REQUEST,
    PAGE,
    TICK_RATES,
    Viewer,
    local_address,
)


def params(**kwargs: object) -> dict[str, list[str]]:
    """Query parameters as the handler receives them — every value a string."""
    return {key: [str(value)] for key, value in kwargs.items()}


class TestAdvance:
    def test_every_engine_answers(self) -> None:
        viewer = Viewer(seed=1)
        for name in viewer.names():
            payload = viewer.advance(name, params(steps=60))
            assert payload, name
            # The page receives this over the wire, so it has to survive JSON.
            assert json.loads(json.dumps(payload)) == payload

    def test_steps_advance_the_engine_exactly_once_each(self) -> None:
        """A reading must never cost an extra tick — that would make the engine
        run faster than the page asked for."""
        viewer = Viewer(seed=2)
        viewer.advance("emergence", params(steps=10))
        assert viewer.engine("emergence").ticks == 10

        viewer.advance("emergence", params(steps=5))
        assert viewer.engine("emergence").ticks == 15

    def test_the_repulsion_field_is_not_double_stepped(self) -> None:
        viewer = Viewer(seed=3)
        viewer.advance("repulsion", params(steps=7))
        assert viewer.engine("repulsion").ticks == 7

    def test_the_pipeline_is_not_double_stepped(self) -> None:
        viewer = Viewer(seed=4)
        viewer.advance("pipeline", params(steps=7))
        assert viewer.engine("pipeline").ticks == 7


class TestControls:
    def test_coupling_reaches_the_engine(self) -> None:
        viewer = Viewer(seed=5)
        payload = viewer.advance("emergence", params(steps=250, coupling=1.0))
        assert payload["metrics"]["verdict"] == "emergent"

    def test_epsilon_reaches_the_engine(self) -> None:
        viewer = Viewer(seed=6)
        assert viewer.advance("crystal", params(steps=400, epsilon=0.02))["verdict"] == "locked"
        assert viewer.advance("crystal", params(steps=400, epsilon=0.6))["verdict"] == "chaos"

    def test_separation_reaches_the_pipeline(self) -> None:
        viewer = Viewer(seed=7)
        apart = viewer.advance("pipeline", params(steps=400, separation=1.0))["mi"]
        viewer.reset("pipeline")
        together = viewer.advance("pipeline", params(steps=400, separation=0.0))["mi"]
        assert apart > together

    def test_out_of_range_controls_are_clamped_not_rejected(self) -> None:
        """A stale or hand-edited query string must not take an engine outside
        the range it validates."""
        viewer = Viewer(seed=8)
        viewer.advance("emergence", params(steps=1, coupling=99))
        assert viewer.engine("emergence").coupling == 1.0

        viewer.advance("crystal", params(steps=1, epsilon=-5))
        assert viewer.engine("crystal").epsilon == 0.0

    def test_unparseable_controls_fall_back_to_the_current_value(self) -> None:
        viewer = Viewer(seed=9)
        viewer.advance("emergence", params(steps=1, coupling="banana"))
        assert viewer.engine("emergence").coupling == 0.5

    def test_missing_controls_leave_the_engine_alone(self) -> None:
        viewer = Viewer(seed=10)
        viewer.advance("emergence", params(steps=1, coupling=0.8))
        viewer.advance("emergence", params(steps=1))
        assert viewer.engine("emergence").coupling == pytest.approx(0.8)

    def test_a_huge_step_request_is_capped(self) -> None:
        """A page that stopped polling for a minute must not be able to demand
        an unbounded amount of work when it comes back."""
        viewer = Viewer(seed=11)
        viewer.advance("emergence", params(steps=10_000_000))
        assert viewer.engine("emergence").ticks == MAX_STEPS_PER_REQUEST

    def test_steps_below_one_still_advance(self) -> None:
        viewer = Viewer(seed=12)
        viewer.advance("emergence", params(steps=0))
        assert viewer.engine("emergence").ticks == 1


class TestPayloads:
    def test_emergence_withholds_metrics_until_the_window_fills(self) -> None:
        viewer = Viewer(seed=13)
        assert viewer.advance("emergence", params(steps=10))["metrics"] is None
        assert viewer.advance("emergence", params(steps=100))["metrics"] is not None

    def test_crystal_payload_is_drawable(self) -> None:
        payload = Viewer(seed=14).advance("crystal", params(steps=100))
        assert len(payload["spins"]) == 64
        assert set(payload["spins"]) <= {1, -1}
        assert payload["verdict"] in {"locked", "building", "chaos"}

    def test_repulsion_payload_carries_every_channel(self) -> None:
        payload = Viewer(seed=15).advance("repulsion", params(steps=50))
        assert len(payload["a"]) == 16
        assert len(payload["concept"]) == 16
        assert len(payload["context"]) == 8
        assert len(payload["sender"]) == 4
        assert payload["mood"] in {
            "surprised", "excited", "thoughtful", "calm", "quiet",
        }


class TestReset:
    def test_reset_rewinds_the_engine(self) -> None:
        viewer = Viewer(seed=16)
        viewer.advance("emergence", params(steps=100))
        viewer.reset("emergence")
        assert viewer.engine("emergence").ticks == 0

    def test_reset_rejects_an_unknown_engine(self) -> None:
        with pytest.raises(KeyError):
            Viewer().reset("nope")


class TestSeeding:
    def test_a_seed_makes_the_whole_viewer_reproducible(self) -> None:
        first = Viewer(seed=99).advance("emergence", params(steps=250))
        second = Viewer(seed=99).advance("emergence", params(steps=250))
        assert first == second


class TestTicker:
    def test_a_ticker_runs_only_while_watched(self) -> None:
        viewer = Viewer(seed=20)
        ticker = viewer.ticker("emergence")
        assert ticker.watchers == 0

        ticker.subscribe()
        assert ticker.watchers == 1
        sequence, _ = ticker.wait(0, timeout=2.0)
        assert sequence > 0, "a subscribed ticker must produce frames"

        ticker.unsubscribe()
        assert ticker.watchers == 0
        settled = viewer.engine("emergence").ticks
        time.sleep(0.2)
        assert viewer.engine("emergence").ticks == settled, "an unwatched ticker must stop"

    def test_rapid_resubscribe_leaves_one_thread(self) -> None:
        """Switching tabs quickly must not leave the previous ticker thread
        alive alongside the new one — two threads would step a single engine at
        twice its rate."""
        viewer = Viewer(seed=21)
        ticker = viewer.ticker("emergence")
        for _ in range(8):
            ticker.subscribe()
            ticker.unsubscribe()

        ticker.subscribe()
        try:
            ticker.wait(0, timeout=2.0)
            before = viewer.engine("emergence").ticks
            time.sleep(0.5)
            elapsed = viewer.engine("emergence").ticks - before
        finally:
            ticker.unsubscribe()

        # 60 Hz for half a second is ~30 ticks. Two threads would roughly
        # double it, so the ceiling is what this test is really asserting.
        assert 10 < elapsed < 55, elapsed

    def test_controls_reach_a_running_ticker(self) -> None:
        viewer = Viewer(seed=22)
        viewer.control("emergence", params(coupling=1.0))
        ticker = viewer.ticker("emergence")
        ticker.subscribe()
        try:
            ticker.wait(0, timeout=2.0)
        finally:
            ticker.unsubscribe()
        assert viewer.engine("emergence").coupling == 1.0

    def test_every_engine_ticks_at_the_origins_rate(self) -> None:
        rates = {"emergence": 60.0, "crystal": 20.0, "repulsion": 30.0, "pipeline": 30.0}
        viewer = Viewer(seed=23)
        for name, expected in rates.items():
            assert viewer.ticker(name).rate == expected


class TestEngineViewerLockstep:
    """Every engine must be visible in the viewer, and vice versa.

    An engine nobody can watch tends to rot — the crystal sat unwired to
    anything for a while and it took a question to notice. So the rule is not a
    note in a guide, it is these tests: add an engine without a tab, or leave a
    tab pointing at an engine that no longer exists, and the suite fails.

    "Engine" is decided structurally rather than from a hand-written list, so a
    new one is caught the day it lands: a class defined in a top-level module of
    the package that has both `step` and `reset`.
    """

    @staticmethod
    def engine_modules() -> set[str]:
        found = set()
        package = Path(anima_reborn.__file__).parent
        for path in sorted(package.glob("*.py")):
            if path.stem.startswith("_"):
                continue
            module = importlib.import_module(f"anima_reborn.{path.stem}")
            for value in vars(module).values():
                if (
                    inspect.isclass(value)
                    and value.__module__ == module.__name__
                    and callable(getattr(value, "step", None))
                    and callable(getattr(value, "reset", None))
                ):
                    found.add(path.stem)
                    break
        return found

    @staticmethod
    def page() -> str:
        return PAGE.read_text(encoding="utf-8")

    def test_every_engine_has_a_route(self) -> None:
        missing = self.engine_modules() - set(Viewer().names())
        assert not missing, (
            f"engine(s) with no viewer route: {sorted(missing)} — "
            "add a handler to _HANDLERS and an instance to Viewer.__init__"
        )

    def test_no_route_points_at_a_missing_engine(self) -> None:
        orphans = set(Viewer().names()) - self.engine_modules()
        assert not orphans, f"viewer route(s) with no engine: {sorted(orphans)}"

    def test_every_route_has_a_tick_rate(self) -> None:
        assert set(Viewer().names()) == set(TICK_RATES)

    def test_every_route_has_a_tab_and_a_panel(self) -> None:
        page = self.page()
        for name in Viewer().names():
            assert f'data-tab="{name}"' in page, f"{name} has no tab button"
            assert f'id="p-{name}"' in page, f"{name} has no panel"

    def test_exactly_one_tab_is_active(self) -> None:
        page = self.page()
        assert page.count('class="tab active"') == 1
        assert page.count('class="panel active"') == 1

    def test_the_default_tab_and_panel_agree(self) -> None:
        page = self.page()
        tab = re.search(r'class="tab active" data-tab="(\w+)"', page)
        panel = re.search(r'class="panel active" id="p-(\w+)"', page)
106:  <button class="tab active" data-tab="base">🌱 기본 엔진</button>
107:  <button class="tab" data-tab="emergence">✨ 창발</button>
108:  <button class="tab" data-tab="crystal">🔮 시간 결정</button>
109:  <button class="tab" data-tab="repulsion">🧲 A × G 반발장</button>
110:  <button class="tab" data-tab="pipeline">🌊 파이프라인</button>
111:  <button class="tab" data-tab="coupled">🔗 결합장</button>
112:  <button class="tab" data-tab="align">🧩 양상 정렬</button>
622:const ko = v => KO[v] || v;
652:const PREFIX = { emergence: "em", crystal: "cr", repulsion: "rp", pipeline: "pl", base: "bs", coupled: "cp", align: "al" };
682:  stream = new EventSource(`/api/${name}/stream?${params}`);
690:    const status = $(PREFIX[name] + "-status");
694:    const status = $(PREFIX[name] + "-status");
702:  fetch(`/api/${name}/control?${params}`).catch(() => {});
723:  if (name === "emergence") renderEmergence(data);
724:  else if (name === "crystal") renderCrystal(data);
725:  else if (name === "repulsion") renderRepulsion(data);
726:  else if (name === "base") renderBase(data);
727:  else if (name === "coupled") renderCoupled(data);
728:  else if (name === "align") renderAlign(data);
729:  else renderPipeline(data);
732:function renderEmergence(d) {
752:function renderCrystal(d) {
766:function renderRepulsion(d) {
784:function renderPipeline(d) {
800:function renderBase(d) {
839:function renderCoupled(d) {
914:function renderAlign(d) {
1009:    fetch(`/api/${button.dataset.reset}/reset`).catch(() => {});

codex
The existing lockstep test only recognizes package-level `step/reset` engines. The interactive session therefore should be a viewer-owned protocol object, not a new core engine class; that preserves engine purity and avoids pretending a waiting human is a tickable system. I’m checking the HTTP lifecycle and UI conventions now.
exec
/bin/zsh -lc "sed -n '260,680p' src/anima_reborn/viewer/server.py && sed -n '80,210p' src/anima_reborn/viewer/page.html && sed -n '600,1040p' src/anima_reborn/viewer/page.html && sed -n '280,520p' tests/test_viewer.py && rg -n \"dialogue|communication|permutation|yoked|frozen.engine|echo\" tests state src README.md docs || true" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
        engine.gain = max(0.1, _number(params, "gain", engine.gain))
        engine.drive = max(-1.0, min(1.0, _number(params, "drive", engine.drive)))

    @staticmethod
    def describe(engine: CoupledEngine) -> dict[str, Any]:
        state = engine.state
        return {
            "names": list(COUPLED_NAMES),
            "values": _round(state.values),
            "sources": [
                -1 if s is None else s for s in engine.wiring.sources
            ],
            "wiring": engine.wiring.value,
            "cyclic": engine.wiring.is_cyclic,
            "amplitude": engine.amplitude,
            "gain": engine.gain,
            "tension": state.tension,
            "pattern": state.pattern,
            "ticks": state.ticks,
            "rhythm": "alternating" if engine.rhythm.alternates else "fixed",
            "period": engine.rhythm.period or 0,
            "drive": engine.drive,
            "coupling": round(state.coupling, 4),
            "listening": state.listening,
            "reachable": engine.rhythm.mean < 1.0,
        }


class _AlignHandler:
    """The learner.

    Scoring is far more expensive than learning, so `describe` reads `state`
    once per frame while the ticker takes many steps between frames — the cost
    ratio the engine's own docstring warns about, respected here.
    """

    @staticmethod
    def configure(engine: Aligner, params: dict[str, list[str]]) -> None:
        engine.rate = max(1e-4, _number(params, "rate", engine.rate))
        engine.noise = max(0.0, _number(params, "noise", engine.noise))
        wanted = params.get("shuffled")
        if wanted:
            shuffled = wanted[0] == "1"
            if shuffled is not engine.shuffled:
                engine.shuffled = shuffled
                engine.reset()  # a different training regime is a different run

    @staticmethod
    def describe(engine: Aligner) -> dict[str, Any]:
        state = engine.state
        # One held-out concept, drawn the same way every frame, so the page can
        # show where its two modalities currently land.
        left = engine.project(engine.observe(10_000, modality=0), modality=0)
        right = engine.project(engine.observe(10_000, modality=1), modality=1)
        return {
            "same": state.same_concept,
            "different": state.different_concept,
            "gap": state.gap,
            "initial_gap": state.initial_gap,
            "learned": state.learned,
            "aligned": state.aligned,
            "pairs": state.pairs_seen,
            "shuffled": engine.shuffled,
            "rate": engine.rate,
            "noise": engine.noise,
            "left": _round(left),
            "right": _round(right),
        }


_HANDLERS: dict[str, Any] = {
    "emergence": _EmergenceHandler,
    "crystal": _CrystalHandler,
    "repulsion": _RepulsionHandler,
    "pipeline": _PipelineHandler,
    "base": _BaseHandler,
    "coupled": _CoupledHandler,
    "align": _AlignHandler,
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

    @property
    def rate(self) -> float:
        return 1.0 / self._interval

    @property
    def watchers(self) -> int:
        with self._condition:
            return self._watchers

    def control(self, params: dict[str, list[str]]) -> None:
        """Take the page's slider values. They are applied by the ticker before
        its next step rather than here, so control never races a step."""
        with self._condition:
            self._controls = params

    def subscribe(self) -> int:
        """Register a watcher and return the sequence number it has seen, so
        the first frame it receives is one it has not."""
        with self._condition:
            self._watchers += 1
            if not self._running:
                self._running = True
                # A new generation. The previous thread may still be inside its
                # sleep; when it wakes it will see a generation that is not its
                # own and retire, so a fast unsubscribe/subscribe — switching
                # tabs quickly — cannot leave two threads stepping one engine
                # at twice its rate.
                self._generation += 1
                threading.Thread(
                    target=self._run, args=(self._generation,), daemon=True
                ).start()
            return self._sequence

    def unsubscribe(self) -> None:
        with self._condition:
            self._watchers -= 1
            if self._watchers <= 0:
                self._watchers = 0
                self._running = False
                self._condition.notify_all()

    def wait(self, seen: int, timeout: float) -> tuple[int, dict[str, Any] | None]:
        """Block until a frame newer than `seen` exists, or the timeout expires.

        Returns the unchanged sequence number on timeout, which the caller uses
        as its cue to send a keep-alive.
        """
        with self._condition:
            self._condition.wait_for(lambda: self._sequence != seen, timeout)
            return self._sequence, self._frame

    def _run(self, generation: int) -> None:
        due = time.monotonic()
        while True:
            with self._condition:
                if not self._running or self._generation != generation:
                    return
                controls = self._controls

            with self._guarded.lock:
                engine = self._guarded.engine
                self._handler.configure(engine, controls)
                engine.step()
                frame = self._handler.describe(engine)

            with self._condition:
                self._sequence += 1
                self._frame = frame
                self._condition.notify_all()

            due += self._interval
            delay = due - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            else:
                # Fell behind — resync rather than sprint to catch up, which
                # would show as a burst of frames at the wrong speed.
                due = time.monotonic()


class Viewer:
    """Holds one of each engine, the ticker driving it, and its controls."""

    def __init__(self, *, seed: int | None = None) -> None:
        engines = {
            "emergence": EmergenceEngine(coupling=0.5, seed=seed),
            "crystal": TimeCrystal(epsilon=0.05, seed=seed),
            "repulsion": RepulsionField(seed=seed),
            "pipeline": Pipeline(seed=seed),
            "base": BaseEngine(seed=seed),
            "coupled": CoupledEngine(seed=seed),
            "align": Aligner(seed=seed),
        }
        self._engines = {
            name: _Guarded(engine, threading.Lock())
            for name, engine in engines.items()
        }
        self._tickers = {
            name: _Ticker(guarded, _HANDLERS[name], TICK_RATES[name])
            for name, guarded in self._engines.items()
        }

    def names(self) -> tuple[str, ...]:
        return tuple(self._engines)

    def engine(self, name: str) -> Any:
        """The live engine behind one route.

        Handed out so the viewer can be embedded and inspected. Stepping it
        from outside races the ticker — read it, or take the lock.
        """
        return self._engines[name].engine

    def ticker(self, name: str) -> _Ticker:
        """The ticker driving one engine."""
        return self._tickers[name]

    def control(self, name: str, params: dict[str, list[str]]) -> dict[str, Any]:
        self._tickers[name].control(params)
        return {"ok": True}

    def reset(self, name: str) -> dict[str, Any]:
        guarded = self._engines[name]
        with guarded.lock:
            guarded.engine.reset()
        return {"reset": name}

    def advance(self, name: str, params: dict[str, list[str]]) -> dict[str, Any]:
        """Apply controls, step, and describe — the one-shot path.

        The page streams instead; this stays for scripting the viewer from a
        shell and for tests that want a frame without a socket.
        """
        guarded = self._engines[name]
        steps = int(_clamp(_number(params, "steps", 1.0), 1, MAX_STEPS_PER_REQUEST))
        with guarded.lock:
            engine = guarded.engine
            handler = _HANDLERS[name]
            handler.configure(engine, params)
            for _ in range(steps):
                engine.step()
            return handler.describe(engine)


class _Handler(BaseHTTPRequestHandler):
    server_version = "anima-reborn-viewer"
    protocol_version = "HTTP/1.1"
    """Keep-alive. Under HTTP/1.0 every request paid a fresh TCP handshake,
    which is most of the cost of a frame on anything but loopback. Every
    non-streaming response below sends a Content-Length, which is what makes
    connection reuse legal."""

    viewer: Viewer

    def do_GET(self) -> None:
        url = urlparse(self.path)
        path = url.path.rstrip("/") or "/"

        if path == "/":
            self._send_page()
            return

        if path.startswith("/api/"):
            self._route(path[len("/api/"):], parse_qs(url.query))
            return

        self._send_json({"error": "not found"}, status=404)

    def _route(self, route: str, params: dict[str, list[str]]) -> None:
        name, _, verb = route.partition("/")
        if name not in self.viewer.names():
            self._send_json({"error": f"unknown engine: {name}"}, status=404)
            return
        try:
            if verb == "stream":
                self._stream(name, params)
            elif verb == "control":
                self._send_json(self.viewer.control(name, params))
            elif verb == "reset":
                self._send_json(self.viewer.reset(name))
            elif verb == "":
                self._send_json(self.viewer.advance(name, params))
            else:
                self._send_json({"error": f"unknown action: {verb}"}, status=404)
        except (ValueError, KeyError) as exc:
            self._send_json({"error": str(exc)}, status=400)

    def _stream(self, name: str, params: dict[str, list[str]]) -> None:
        """Push frames until the browser goes away.

        The response has no length, so the connection cannot be reused; it is
        held open for the life of the stream instead.
        """
        ticker = self.viewer.ticker(name)
        if params:
            ticker.control(params)

        self.close_connection = True
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        seen = ticker.subscribe()
        try:
            self._write(f"retry: 500\nevent: hello\ndata: {json.dumps({'rate': ticker.rate})}\n\n")
            while True:
                sequence, frame = ticker.wait(seen, PING_SECONDS)
                if sequence == seen or frame is None:
                    # Nothing new. The comment is what detects a browser that
                    # closed without telling us.
                    self._write(": ping\n\n")
                    continue
                seen = sequence
                self._write(f"data: {json.dumps(frame)}\n\n")
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass  # the page navigated away; the finally clause is the cleanup
        finally:
            ticker.unsubscribe()

    def _write(self, text: str) -> None:
        self.wfile.write(text.encode())
        self.wfile.flush()

    def _send_page(self) -> None:
        try:
            body = PAGE.read_bytes()
        except OSError as exc:
            self._send_json({"error": f"page missing: {exc}"}, status=500)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            # The page navigated away mid-request. Nothing to recover, and it
            # is not worth a stack trace in the log.
            pass

    def log_message(self, fmt: str, *args: Any) -> None:
        """Silence the per-request log — a stream would otherwise log once per
        frame and bury the startup banner."""


def local_address() -> str:
    """The address of this machine another host on the network would use.

    Opens a UDP socket toward a routable address to learn which interface the
    kernel would pick; nothing is sent. Falls back to the loopback address when
    there is no route at all.
    """
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 9))  # TEST-NET-1, guaranteed unrouted
        return str(probe.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


def serve(
    *,
    host: str = "0.0.0.0",
    port: int = 8420,
    seed: int | None = None,
) -> None:
    """Run the viewer until interrupted.

    Args:
        host: Interface to bind. The default accepts connections from anywhere
            on the network, which is what makes the viewer reachable by IP;
            pass "127.0.0.1" to keep it on this machine.
        port: TCP port.
        seed: Seeds all four engines, so a demonstration can be repeated.
    """
    handler = type("_BoundHandler", (_Handler,), {"viewer": Viewer(seed=seed)})
    server = ThreadingHTTPServer((host, port), handler)
    server.daemon_threads = True

    reachable = local_address() if host in ("0.0.0.0", "::", "") else host
    banner = ["anima-reborn viewer", f"  local    http://127.0.0.1:{port}"]
    if reachable != "127.0.0.1":
        banner.append(f"  network  http://{reachable}:{port}")
    if host == "0.0.0.0":
        banner.append("  bound to every interface — anyone on this network can reach it")
    rates = " · ".join(f"{name} {int(hz)}Hz" for name, hz in TICK_RATES.items())
    banner.append(f"  {rates}")
    banner.append("  ctrl-c to stop")
    # Flushed explicitly: stdout is block-buffered whenever it is redirected to
    # a file or a pipe, which is exactly when someone needs to read the address
    # off the log.
    print("\n".join(banner), flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped", flush=True)
    finally:
        server.server_close()
    display: inline-block; padding: 4px 11px; border-radius: 999px;
    font-size: 12px; font-weight: 600; border: 1px solid var(--line); color: var(--dim);
  }
  .badge.good { background: rgba(168,230,104,.14); border-color: var(--accent); color: var(--accent); }
  .badge.mid  { background: rgba(255,190,102,.13); border-color: #ffbe66; color: #ffbe66; }
  .badge.bad  { background: rgba(255,123,154,.12); border-color: var(--g); color: var(--g); }

  .status { margin-top: 12px; color: var(--dim); font-size: 12.5px; min-height: 1.5em; }
  .err { color: var(--g); }
  footer { margin-top: 26px; color: var(--dim); font-size: 12px; }
  footer a { color: var(--a); }
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>🌱 anima-reborn — 엔진 뷰어</h1>
  <div class="sub">
    아래의 모든 숫자와 점은 <code>src/anima_reborn/</code> 의 파이썬 엔진에서
    프레임 단위로 밀려옵니다(push). 이 페이지는 <strong>그리기만</strong> 합니다.
  </div>
  <div class="fps" id="fps">연결 중…</div>
</header>

<nav>
  <button class="tab active" data-tab="base">🌱 기본 엔진</button>
  <button class="tab" data-tab="emergence">✨ 창발</button>
  <button class="tab" data-tab="crystal">🔮 시간 결정</button>
  <button class="tab" data-tab="repulsion">🧲 A × G 반발장</button>
  <button class="tab" data-tab="pipeline">🌊 파이프라인</button>
  <button class="tab" data-tab="coupled">🔗 결합장</button>
  <button class="tab" data-tab="align">🧩 양상 정렬</button>
</nav>

<!-- ── Emergence ──────────────────────────────────────────────────────── -->
<section class="panel" id="p-emergence">
  <div class="card">
    <h2>두 스트림, 하나의 공유 진동자</h2>
    <p class="note">
      각 스트림은 자기 잡음과 둘이 공유하는 사인파를 섞습니다. 결합도를 올리면
      어느 쪽 스트림에도 무언가를 더하지 않았는데 <em>둘의 쌍</em>에 정보가 생깁니다 —
      산점도가 대각선으로 모입니다.
    </p>

    <div class="controls">
      <label class="ctl">결합도 <input type="range" id="em-coupling" min="0" max="100" value="50"><b id="em-coupling-v">0.50</b></label>
      <button class="act" data-reset="emergence">초기화</button>
    </div>

    <div class="grid-scatter">
      <div>
        <p class="label">스트림 L / 스트림 R</p>
        <canvas id="em-l" height="120"></canvas>
        <div style="height:10px"></div>
        <canvas id="em-r" height="120"></canvas>
      </div>
      <div>
        <p class="label">L 대 R</p>
        <canvas id="em-scatter" height="260"></canvas>
      </div>
    </div>

    <div class="metrics">
      <div class="metric"><div class="k">H(L)</div><div class="v" id="em-hl">—</div></div>
      <div class="metric"><div class="k">H(R)</div><div class="v" id="em-hr">—</div></div>
      <div class="metric"><div class="k">H(L,R)</div><div class="v" id="em-hj">—</div></div>
      <div class="metric"><div class="k">상호정보량</div><div class="v" id="em-mi">—</div></div>
      <div class="metric"><div class="k">판정</div><div class="v"><span class="badge" id="em-badge">—</span></div></div>
    </div>
    <div class="status" id="em-status"></div>
  </div>
</section>

<!-- ── Time crystal ───────────────────────────────────────────────────── -->
<section class="panel" id="p-crystal">
  <div class="card">
    <h2>주어진 적 없는 박자를 스스로 지키는 링</h2>
    <p class="note">
      매 틱마다 구동이 64개 스핀을 전부 뒤집으려 하고 각각을 확률 ε 로 놓칩니다.
      그 손상을 이징(Ising) 결합이 복구합니다. ε 이 작으면 링은 주기-2 리듬으로 잠기고,
      ε 을 올리면 결정이 녹습니다.
    </p>

    <div class="controls">
      <label class="ctl">ε (실패율) <input type="range" id="cr-eps" min="0" max="60" value="5"><b id="cr-eps-v">0.05</b></label>
      <button class="act" data-reset="crystal">초기화</button>
    </div>

    <p class="label">스핀 사슬</p>
    <canvas id="cr-spins" height="56"></canvas>
    <div style="height:12px"></div>
    <p class="label">시간에 따른 자화</p>
    <canvas id="cr-mag" height="150"></canvas>

    <div class="metrics">
      <div class="metric"><div class="k">자화</div><div class="v" id="cr-m">—</div></div>
      <div class="metric"><div class="k">자기상관 지연1</div><div class="v" id="cr-ac1">—</div></div>
      <div class="metric"><div class="k">지연2</div><div class="v" id="cr-ac2">—</div></div>
      <div class="metric"><div class="k">지연4</div><div class="v" id="cr-ac4">—</div></div>
      <div class="metric"><div class="k">판정</div><div class="v"><span class="badge" id="cr-badge">—</span></div></div>
    </div>
    <div class="status" id="cr-status"></div>
  </div>
</section>

<!-- ── Repulsion ──────────────────────────────────────────────────────── -->
<section class="panel" id="p-repulsion">
  <div class="card">
    <h2>두 엔진 사이의 간극에서 사고하기</h2>
    <p class="note">
      엔진 A도 G도 단독으로는 읽히지 않습니다 — 오직 둘 사이의 간극만 읽힙니다.
      간극의 크기가 tension, 방향이 concept, 겹침이 meaning 입니다. 분리도를 0으로 내리면
      두 엔진이 하나로 붕괴합니다 — 평온한 게 아니라, 사고할 거리가 사라진 것입니다.
    </p>

    <div class="controls">
      <label class="ctl">분리도 <input type="range" id="rp-sep" min="0" max="150" value="60"><b id="rp-sep-v">0.60</b></label>
      <label class="ctl">잡음 <input type="range" id="rp-noise" min="0" max="100" value="20"><b id="rp-noise-v">0.20</b></label>
      <button class="act" data-reset="repulsion">초기화</button>
    </div>

    <div class="grid-scatter">
      <div>
        <p class="label">위상평면 — A, G 그리고 반발 벡터</p>
        <canvas id="rp-phase" height="280"></canvas>
      </div>
      <div>
        <p class="label">진정성(authenticity)</p>
        <canvas id="rp-auth" height="70"></canvas>
        <div style="height:12px"></div>
  ctx.beginPath(); ctx.arc(gx, gy, 5, 0, Math.PI * 2); ctx.fill();
  ctx.fillText("G", gx + 9, gy - 7);
}

function drawSpins(canvas, spins) {
  const { ctx, w, h } = fit(canvas);
  const cell = w / spins.length;
  for (let i = 0; i < spins.length; i++) {
    ctx.fillStyle = spins[i] > 0 ? "#7b9aff" : "#ff7b9a";
    ctx.fillRect(i * cell + 0.5, 4, Math.max(1, cell - 1), h - 8);
  }
}

// ── badges ─────────────────────────────────────────────────────────────────
const EMERGENCE_CLASS = { emergent: "good", partial: "mid", independent: "bad" };
// 표시 문자열만 한글로 바꾼다. 배지 색은 위의 원래 값(raw)으로 판정하고,
// 매핑에 없는 값은 원문 그대로 노출한다 — 없는 번역을 지어내지 않기 위해서다.
const KO = {
  emergent: "창발", partial: "부분적", independent: "독립",
  locked: "잠금", building: "형성 중", chaos: "융해",
  surprised: "놀람", excited: "격앙", thoughtful: "사려", calm: "평온", quiet: "고요",
};
const ko = v => KO[v] || v;
const EMERGENCE_TEXT = {
  emergent: "창발 ✨ — 어느 스트림도 혼자서는 갖지 못한 정보를 둘의 쌍이 담고 있습니다.",
  partial: "부분적 — 이 창 크기에서는 독립과 구분되지 않는 수준입니다.",
  independent: "독립 — 두 스트림이 공유하는 정보가 없습니다.",
};
const CRYSTAL_CLASS = { locked: "good", building: "mid", chaos: "bad" };
const CRYSTAL_TEXT = {
  locked: "잠금 ✨ — 주기-2 리듬. 구동과 반대 위상으로 맞물려 유지되고 있습니다.",
  building: "형성 중 — 지연1은 반대 위상으로 갔지만 지연2가 아직 따라오지 못했습니다.",
  chaos: "융해 — 구동의 불완전함이 이징 복구를 앞질렀습니다.",
};
const MOOD_CLASS = { surprised: "mid", excited: "bad", thoughtful: "good", calm: "good", quiet: "" };
const MOOD_TEXT = {
  surprised: "이번 틱에 간극이 급변했습니다.",
  excited: "높은 간극이 지속 — 두 엔진이 크게 벌어져 있습니다.",
  thoughtful: "사고가 일어나는 크기의 간극입니다.",
  calm: "작지만 실재하는 간극입니다.",
  quiet: "두 엔진이 하나로 붕괴 — 사고할 간극이 남지 않았습니다.",
};

function setBadge(el, text, cls) {
  el.textContent = text;
  el.className = "badge" + (cls ? " " + cls : "");
}

// ── streaming ──────────────────────────────────────────────────────────────
// The server pushes a frame per engine tick over one long-lived connection.
// Frames are stashed, not drawn on arrival; drawing happens on the display's
// own refresh, so a burst of frames costs one repaint rather than several.
const PREFIX = { emergence: "em", crystal: "cr", repulsion: "rp", pipeline: "pl", base: "bs", coupled: "cp", align: "al" };
const ROTATION = [];   // recent accumulated phase, so a stalled clock is visible

let active = "base";
let stream = null;
let pending = null;          // newest frame not yet drawn
let received = 0;            // frames since the last rate sample
let drawn = 0;
let engineRate = 0;

function controlsFor(name) {
  if (name === "emergence") return { coupling: $("em-coupling").value / 100 };
  if (name === "crystal") return { epsilon: $("cr-eps").value / 100 };
  if (name === "repulsion") return { separation: $("rp-sep").value / 100, noise: $("rp-noise").value / 100 };
  if (name === "base") return { epsilon: $("bs-eps").value / 100, separation: $("bs-sep").value / 100 };
  if (name === "coupled") return { wiring: $("cp-wiring").value, rhythm: $("cp-rhythm").value,
                                   gain: $("cp-gain").value / 10, drive: $("cp-drive").value / 10 };
  if (name === "align") return { rate: $("al-rate").value / 1000, noise: $("al-noise").value / 100,
                                 shuffled: $("al-shuffled").checked ? "1" : "0" };
  return { separation: $("pl-sep").value / 100 };
}

function connect(name) {
  if (stream) stream.close();
  pending = null;
  received = drawn = 0;
  ROTATION.length = 0;   // a stale span would distort the next rotation trace
  LEARNED.length = 0;

  const params = new URLSearchParams(controlsFor(name));
  stream = new EventSource(`/api/${name}/stream?${params}`);

  stream.addEventListener("hello", event => {
    engineRate = JSON.parse(event.data).rate;
  });
  stream.onmessage = event => {
    pending = JSON.parse(event.data);
    received++;
    const status = $(PREFIX[name] + "-status");
    if (status.classList.contains("err")) status.className = "status";
  };
  stream.onerror = () => {
    const status = $(PREFIX[name] + "-status");
    status.className = "status err";
    status.textContent = "스트림 끊김 — 재연결 중…";
  };
}

function pushControls(name) {
  const params = new URLSearchParams(controlsFor(name));
  fetch(`/api/${name}/control?${params}`).catch(() => {});
}

// ── draw loop ──────────────────────────────────────────────────────────────
function frame() {
  if (pending) {
    render(active, pending);
    pending = null;
    drawn++;
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

setInterval(() => {
  $("fps").textContent = `수신 ${received} fps · 그림 ${drawn}` +
    (engineRate ? ` · 엔진 ${Math.round(engineRate)} Hz` : "");
  received = drawn = 0;
}, 1000);

function render(name, data) {
  if (name === "emergence") renderEmergence(data);
  else if (name === "crystal") renderCrystal(data);
  else if (name === "repulsion") renderRepulsion(data);
  else if (name === "base") renderBase(data);
  else if (name === "coupled") renderCoupled(data);
  else if (name === "align") renderAlign(data);
  else renderPipeline(data);
}

function renderEmergence(d) {
  drawTrace($("em-l"), d.left, "#7b9aff", d.range, 250);
  drawTrace($("em-r"), d.right, "#a8e668", d.range, 250);
  drawScatter($("em-scatter"), d.left, d.right, d.range);

  const status = $("em-status");
  status.className = "status";
  if (!d.metrics) {
    status.textContent = `창을 채우는 중 — 엔트로피가 의미를 가지려면 ${d.left.length}/50 표본이 필요합니다.`;
    return;
  }
  const m = d.metrics;
  $("em-hl").textContent = m.h_left.toFixed(2);
  $("em-hr").textContent = m.h_right.toFixed(2);
  $("em-hj").textContent = m.h_joint.toFixed(2);
  $("em-mi").textContent = m.mi.toFixed(3);
  setBadge($("em-badge"), ko(m.verdict), EMERGENCE_CLASS[m.verdict]);
  status.textContent = EMERGENCE_TEXT[m.verdict];
}

function renderCrystal(d) {
  drawSpins($("cr-spins"), d.spins);
  drawTrace($("cr-mag"), d.history, "#7b9aff", 1.0, 300);
  const sign = v => (v >= 0 ? "+" : "") + v.toFixed(3);
  $("cr-m").textContent = sign(d.magnetization);
  $("cr-ac1").textContent = sign(d.ac1);
  $("cr-ac2").textContent = sign(d.ac2);
  $("cr-ac4").textContent = sign(d.ac4);
  setBadge($("cr-badge"), ko(d.verdict), CRYSTAL_CLASS[d.verdict]);
  const status = $("cr-status");
  status.className = "status";
  status.textContent = CRYSTAL_TEXT[d.verdict];
}

function renderRepulsion(d) {
  drawPhasePlane($("rp-phase"), d.a, d.g);
  drawBars($("rp-concept"), d.concept, "rgba(123,154,255,.85)", "rgba(255,123,154,.85)");
  drawBars($("rp-meaning"), d.meaning, "rgba(255,123,154,.85)", "rgba(123,154,255,.85)");
  drawBars($("rp-context"), d.context, "rgba(168,230,104,.85)", "rgba(168,230,104,.45)");
  drawBars($("rp-sender"), d.sender, "rgba(192,200,224,.85)", "rgba(192,200,224,.45)");
  drawGauge($("rp-auth"), d.authenticity);

  $("rp-tension").textContent = d.tension.toFixed(3);
  $("rp-topic").textContent = "#" + d.topic;
  $("rp-cur").textContent = d.curiosity.toFixed(3);
  $("rp-auth-v").textContent = d.authenticity.toFixed(3);
  setBadge($("rp-mood"), ko(d.mood), MOOD_CLASS[d.mood]);
  const status = $("rp-status");
  status.className = "status";
  status.textContent = MOOD_TEXT[d.mood];
}

function renderPipeline(d) {
  drawPhasePlane($("pl-phase"), d.a, d.g);
  drawScatter($("pl-scatter"), d.left, d.right, d.range);
  drawTrace($("pl-l"), d.left, "#7b9aff", d.range, 200);
  drawTrace($("pl-r"), d.right, "#a8e668", d.range, 200);

  $("pl-tension").textContent = d.tension.toFixed(3);
  $("pl-hl").textContent = d.h_left.toFixed(2);
  $("pl-hr").textContent = d.h_right.toFixed(2);
  $("pl-mi").textContent = d.mi.toFixed(3);
  setBadge($("pl-badge"), ko(d.verdict), EMERGENCE_CLASS[d.verdict]);
  const status = $("pl-status");
  status.className = "status";
  status.textContent = EMERGENCE_TEXT[d.verdict];
}

function renderBase(d) {
  drawPhasePlane($("bs-phase"), d.a, d.g);
  drawTrace($("bs-mag"), d.magnetization, "#7b9aff", 1.0, 300);
  drawTrace($("bs-l"), d.left, "#7b9aff", d.range, 200);
  drawTrace($("bs-r"), d.right, "#a8e668", d.range, 200);

  // Rotation only ever climbs, so plot it against its own recent span — a flat
  // line is the clock having stopped being paid for.
  ROTATION.push(d.phase);
  if (ROTATION.length > 200) ROTATION.shift();
  const lo = ROTATION[0], hi = ROTATION[ROTATION.length - 1];
  const span = Math.max(1e-6, hi - lo);
  drawTrace($("bs-rot"), ROTATION.map(v => ((v - lo) / span) * 2 - 1), "#a8e668", 1.0, 200);

  $("bs-phase-v").textContent = d.phase.toFixed(2);
  $("bs-tension").textContent = d.tension.toFixed(3);
  $("bs-mi").textContent = d.mi.toFixed(3);
  setBadge($("bs-rhythm"), ko(d.rhythm), CRYSTAL_CLASS[d.rhythm]);
  setBadge($("bs-badge"), ko(d.verdict), EMERGENCE_CLASS[d.verdict]);

  const status = $("bs-status");
  status.className = "status";
  if (d.rhythm === "locked" && d.verdict === "emergent") {
    status.textContent = "잠금이 회전 비용을 대고 있고, 움직이는 간극이 두 스트림을 묶고 있습니다.";
  } else if (d.rhythm !== "locked" && d.mi < 0.05) {
    status.textContent = `시계가 멈췄습니다. 간극은 여전히 ${d.tension.toFixed(3)} — 두 엔진은 벌어진 채입니다 — 그런데 그 안에서 아무 말도 오가지 않습니다.`;
  } else {
    status.textContent = "전이 중 — 판정과 관측 창 모두 변화보다 수백 틱 늦게 따라옵니다.";
  }
}

const WIRING_KO = { ring: "고리", feedforward: "전방향", self: "자기참조", pairs: "쌍" };
const WIRING_TEXT = {
  ring: "닫힌 순환 — 영향이 출발점으로 되돌아옵니다. 어떤 방향을 끊어도 공짜가 아닙니다.",
  feedforward: "되먹임 없음 — 첫 유닛은 바깥에서만 받습니다. 그쪽으로 향하는 영향을 끊으면 잃을 게 없어, 이론은 이걸 환원가능이라 부릅니다.",
  self: "결합 없음 — 각 유닛이 자기만 읽습니다. 통합할 것이 애초에 없습니다.",
  pairs: "교차결합 쌍 — 두 유닛이 서로를 읽는 래치. 고리 하나는 폭이 몇이든 1비트지만, 쌍 k개는 k비트를 담습니다. 용량은 유닛 수가 아니라 배선의 순환 구조입니다.",
};

function renderCoupled(d) {
  const { ctx, w, h } = fit($("cp-graph"));
  const cx = w / 2, cy = h / 2, R = Math.min(w, h) * 0.32;
  const at = i => [cx + R * Math.cos(-Math.PI / 2 + i * Math.PI / 2),
                   cy + R * Math.sin(-Math.PI / 2 + i * Math.PI / 2)];

  for (let i = 0; i < 4; i++) {
    const src = d.sources[i];
    if (src < 0) continue;
    const [sx, sy] = at(src), [tx, ty] = at(i);
    const angle = Math.atan2(ty - sy, tx - sx);
    const pad = 22;
    const x0 = sx + pad * Math.cos(angle), y0 = sy + pad * Math.sin(angle);
    const x1 = tx - pad * Math.cos(angle), y1 = ty - pad * Math.sin(angle);
    ctx.strokeStyle = d.cyclic ? "rgba(168,230,104,.85)" : "rgba(139,146,163,.55)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    if (src === i) {
      ctx.arc(tx, ty - 20, 12, 0, Math.PI * 2);
    } else {
      ctx.moveTo(x0, y0); ctx.lineTo(x1, y1);
      ctx.moveTo(x1, y1);
      ctx.lineTo(x1 - 9 * Math.cos(angle - Math.PI / 6), y1 - 9 * Math.sin(angle - Math.PI / 6));
      ctx.moveTo(x1, y1);
      ctx.lineTo(x1 - 9 * Math.cos(angle + Math.PI / 6), y1 - 9 * Math.sin(angle + Math.PI / 6));
    }
    ctx.stroke();
  }

  for (let i = 0; i < 4; i++) {
    const [x, y] = at(i);
    ctx.fillStyle = i < 2 ? "#7b9aff" : "#ff7b9a";
    ctx.globalAlpha = d.values[i] > 0 ? 1 : 0.35;
    ctx.beginPath(); ctx.arc(x, y, 15, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;
    ctx.fillStyle = "#14161c";
    ctx.font = "600 11px ui-sans-serif, system-ui, sans-serif";
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(d.names[i], x, y);
    ctx.textAlign = "start"; ctx.textBaseline = "alphabetic";
  }

  drawBars($("cp-bars"), d.values, "rgba(123,154,255,.85)", "rgba(255,123,154,.85)");

  const pat = fit($("cp-pattern"));
  const cell = pat.w / 4;
  for (let i = 0; i < 4; i++) {
    const on = (d.pattern >> i) & 1;
    pat.ctx.fillStyle = on ? "#a8e668" : "rgba(139,146,163,.25)";
    pat.ctx.fillRect(i * cell + 3, 8, cell - 6, pat.h - 16);
    pat.ctx.fillStyle = on ? "#14161c" : "#8b92a3";
    pat.ctx.font = "600 12px ui-sans-serif, system-ui, sans-serif";
    pat.ctx.textAlign = "center";
    pat.ctx.fillText(on ? "1" : "0", i * cell + cell / 2, pat.h / 2 + 4);
    pat.ctx.textAlign = "start";
  }

  setBadge($("cp-wiring-b"), WIRING_KO[d.wiring] || d.wiring, d.cyclic ? "good" : "");
  $("cp-tension").textContent = d.tension.toFixed(3);
  $("cp-pattern-v").textContent = d.pattern.toString(2).padStart(4, "0");
  setBadge($("cp-phase-b"), d.listening ? "듣는 중" : "통합 중", d.listening ? "" : "good");
  $("cp-coupling").textContent = d.coupling.toFixed(2);
  // 입력은 스칼라(모든 유닛에 같은 말) 또는 유닛별 벡터로 올 수 있다.
  $("cp-drive-b").textContent = Array.isArray(d.drive)
    ? d.drive.map(v => v.toFixed(2)).join(" ")
    : d.drive.toFixed(2);
  $("cp-ticks").textContent = d.ticks;
  const status = $("cp-status");
  status.className = "status";
  const wall = d.reachable ? "" : " · 결합이 1.00 이라 입력이 닿을 틈이 없습니다 (벽)";
  status.textContent = (WIRING_TEXT[d.wiring] || "") + wall;
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
  ctx.setLineDash([]);
  ctx.strokeStyle = "rgba(139,146,163,.25)";
  ctx.beginPath(); ctx.moveTo(0, y(0)); ctx.lineTo(w, y(0)); ctx.stroke();

  if (LEARNED.length > 1) {
    ctx.beginPath();
    ctx.strokeStyle = d.shuffled ? "#ff7b9a" : "#a8e668";
    ctx.lineWidth = 2;
    LEARNED.forEach((v, i) => {
      const x = (i / Math.max(1, LEARNED.length - 1)) * w;
      i === 0 ? ctx.moveTo(x, y(v)) : ctx.lineTo(x, y(v));
    });
    ctx.stroke();
  }
  ctx.fillStyle = "#8b92a3";
  ctx.font = "11px ui-sans-serif, system-ui, sans-serif";
  ctx.fillText("0.30", 4, y(0.3) - 4);

  // 같은 개념의 두 양상이 어디에 착지하는가 — 붙을수록 배운 것
  drawBars($("al-vectors"), d.left.concat(d.right),
           "rgba(123,154,255,.85)", "rgba(255,123,154,.85)");

  $("al-learned").textContent = (d.learned >= 0 ? "+" : "") + d.learned.toFixed(3);
  $("al-same").textContent = d.same.toFixed(3);
  $("al-diff").textContent = d.different.toFixed(3);
  $("al-pairs").textContent = d.pairs;
  setBadge($("al-badge"), d.aligned ? "정렬됨" : "미달", d.aligned ? "good" : "");

  const status = $("al-status");
  status.className = "status";
  if (d.shuffled) {
    status.textContent = "대조군 — 짝이 흐트러져 함께 나타남이 없습니다. 같은 신호·같은 학습률인데 배우지 못하는 것이 요점입니다.";
  } else if (d.aligned) {
    status.textContent = "학습에 없던 개념에서도 두 양상이 한곳으로 모입니다 — 짝을 외운 게 아니라 양상 사이의 대응을 배운 것입니다.";
  } else {
    status.textContent = "아직 배우는 중 — 출발점 대비 증가가 기준(0.30) 아래입니다.";
  }
}

// ── wiring ─────────────────────────────────────────────────────────────────
for (const tab of document.querySelectorAll(".tab")) {
  tab.addEventListener("click", () => {
    if (tab.dataset.tab === active) return;
    document.querySelectorAll(".tab").forEach(t => t.classList.toggle("active", t === tab));
    active = tab.dataset.tab;
    document.querySelectorAll(".panel").forEach(p => {
      p.classList.toggle("active", p.id === "p-" + active);
    });
    // One stream at a time: the engine behind a hidden tab stops ticking, the
    // same way the origin skipped inactive tabs.
    connect(active);
  });
}

const SLIDERS = [
  ["em-coupling", "em-coupling-v", "emergence"],
  ["cr-eps", "cr-eps-v", "crystal"],
  ["rp-sep", "rp-sep-v", "repulsion"],
  ["rp-noise", "rp-noise-v", "repulsion"],
  ["pl-sep", "pl-sep-v", "pipeline"],
  ["bs-eps", "bs-eps-v", "base"],
  ["bs-sep", "bs-sep-v", "base"],
  ["cp-gain", "cp-gain-v", "coupled"],
  ["cp-drive", "cp-drive-v", "coupled"],
  ["al-rate", "al-rate-v", "align"],
  ["al-noise", "al-noise-v", "align"],
];
for (const [input, output, engine] of SLIDERS) {
  const el = $(input), out = $(output);
  // 이득(0.5~8.0)과 입력(-1~1)만 10으로 나눈다 — 나머지 슬라이더는 전부 0~1 비율이다.
  const divisor = (input === "cp-gain" || input === "cp-drive") ? 10 : (input === "al-rate" ? 1000 : 100);
  const digits = divisor === 10 ? 1 : (divisor === 1000 ? 3 : 2);
  const sync = () => { out.textContent = (el.value / divisor).toFixed(digits); };
  el.addEventListener("input", () => { sync(); pushControls(engine); });
  sync();
}

$("cp-wiring").addEventListener("change", () => pushControls("coupled"));
$("cp-rhythm").addEventListener("change", () => pushControls("coupled"));
$("al-shuffled").addEventListener("change", () => { LEARNED.length = 0; pushControls("align"); });

for (const button of document.querySelectorAll("[data-reset]")) {
  button.addEventListener("click", () => {
    fetch(`/api/${button.dataset.reset}/reset`).catch(() => {});
  });
}

// A backgrounded tab gets no animation frames, so frames would pile up in the
// browser's buffer. Drop the stream while hidden and pick it back up on return.
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    if (stream) { stream.close(); stream = null; }
  } else {
    connect(active);
  }
});

connect(active);
</script>
</body>
</html>
        panel = re.search(r'class="panel active" id="p-(\w+)"', page)
        active = re.search(r'let active = "(\w+)";', page)
        assert tab and panel and active
        assert tab.group(1) == panel.group(1) == active.group(1)

    def test_every_route_is_drawable(self) -> None:
        """A tab that streams frames nothing knows how to draw is a blank
        panel, which looks like a broken engine."""
        page = self.page()
        prefix_line = page.split("const PREFIX =")[1].split("\n")[0]
        for name in Viewer().names():
            assert f"{name}:" in prefix_line, f"{name} is missing from the PREFIX map"
            # The dispatch runs one branch per engine and falls through to the
            # last, so the render function is the thing to check for — a name
            # in the `if` chain would miss whichever engine is the `else`.
            renderer = f"function render{name[0].upper()}{name[1:]}("
            assert renderer in page, f"{name} has no {renderer.strip('(')} function"

    def test_every_route_answers_with_a_drawable_frame(self) -> None:
        viewer = Viewer(seed=1)
        for name in viewer.names():
            payload = viewer.advance(name, params(steps=60))
            assert payload, name
            assert json.loads(json.dumps(payload)) == payload, name


def test_local_address_is_an_address() -> None:
    """Never raises and never returns empty, even with no route out."""
    address = local_address()
    assert address.count(".") == 3
    assert all(part.isdigit() for part in address.split("."))
rg: docs: No such file or directory (os error 2)
tests/test_dialogue.py:1:"""The reproducible half of human<->engine dialogue, with a synthetic partner.
tests/test_dialogue.py:6:learned half is load-bearing (not an echo), and that the update rule cannot see
tests/test_dialogue.py:7:across the gap. Full game in `state/communication/dialogue.py`.
tests/test_dialogue.py:16:sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "state" / "communication"))
tests/test_dialogue.py:18:import dialogue  # noqa: E402
tests/test_dialogue.py:23:        dyads = [dialogue.play(s, episodes=400) for s in range(3)]
tests/test_dialogue.py:27:    def test_the_engines_learned_half_is_load_bearing_not_an_echo(self) -> None:
tests/test_dialogue.py:30:        frozen = [dialogue.play(s, episodes=400, frozen_engine=True)["a"] for s in range(3)]
tests/test_dialogue.py:34:        yoked = [dialogue.play(s, episodes=400, yoked=True)["a"] for s in range(3)]
tests/test_dialogue.py:35:        assert statistics.mean(yoked) < 0.6, yoked
tests/test_dialogue.py:38:        dyads = [dialogue.play(s, episodes=400) for s in range(3)]
tests/test_dialogue.py:40:            dialogue._probe(d["policies"], seed=i, direction="a")
tests/test_dialogue.py:44:            dialogue._probe(
tests/test_dialogue.py:58:        params = list(inspect.signature(dialogue._reinforce).parameters)
state/CLAUDE.md:11:└─ communication/ what an engine would need in order to communicate: the
README.md:245:그래서 이 비교는 테스트가 아니라 `state/communication/alternating_coupling.py` 에 있고,
src/anima_reborn/CLAUDE.md:57:`state/communication/aligned_drive.py` measures whether concept identity survives the
src/anima_reborn/CLAUDE.md:65:than merely exhibits (`state/communication/silence.py`). It is exactly one bit: four sign
src/anima_reborn/CLAUDE.md:72:0.500 by construction (`state/communication/match.py`). A score near 1.0 there would be
src/anima_reborn/CLAUDE.md:81:pairs — an even number forms a macro-ring that locks. `state/communication/capacity.py`.
state/communication/attractor_canonicalization.py:5:    PYTHONPATH=src python state/communication/attractor_canonicalization.py
state/communication/match.py:5:    PYTHONPATH=src python state/communication/match.py
state/communication/concepts.py:5:    PYTHONPATH=src python state/communication/concepts.py
state/communication/dialogue.py:1:"""Toward human<->engine dialogue: the reproducible half, with a synthetic partner.
state/communication/dialogue.py:5:    PYTHONPATH=src python state/communication/dialogue.py
state/communication/dialogue.py:16:  own yoked block, a permutation test on its own log), never averaged over people.
state/communication/dialogue.py:34:**The echo trap, caught here.** If the engine merely handed the partner's bit
state/communication/dialogue.py:35:back, "recovery" would measure the partner's self-consistency. The `frozen-engine`
state/communication/dialogue.py:98:    yoked: bool = False,
state/communication/dialogue.py:99:    frozen_engine: bool = False,
state/communication/dialogue.py:120:        reward = rng.random() if yoked else success
state/communication/dialogue.py:122:        if not frozen_engine:
state/communication/dialogue.py:132:        reward_b = rng.random() if yoked else success_b
state/communication/dialogue.py:133:        if not frozen_engine:
state/communication/dialogue.py:179:    print("human<->engine dialogue — the reproducible half, synthetic partner")
state/communication/dialogue.py:185:    yoked = [play(s, yoked=True)["a"] for s in range(SEEDS)]
state/communication/dialogue.py:186:    frozen = [play(s, frozen_engine=True)["a"] for s in range(SEEDS)]
state/communication/dialogue.py:208:    print(f"{'yoked feedback':<28}{statistics.mean(yoked):>10.3f}"
state/communication/dialogue.py:209:          f"{min(yoked):>9.3f}   consequence establishes it")
state/communication/dialogue.py:210:    print(f"{'frozen engine (echo test)':<28}{statistics.mean(frozen):>10.3f}"
state/communication/dialogue.py:223:        f"\n  trained beats day-0 on {wins}/{SEEDS} dyads. The frozen-engine arm is"
state/communication/dialogue.py:226:        f"\n  this is not the engine echoing the partner's input. This measures the"
src/anima_reborn/align.py:13:(`state/communication/attractor_canonicalization.py`) did not help either; a
src/anima_reborn/words.py:275:    YOKED = "yoked"
src/anima_reborn/words.py:361:        live +0.078   one-way +0.008   yoked -0.000   no channel -0.002
src/anima_reborn/words.py:363:    The yoked control dying is what makes the first number mean anything, and
src/anima_reborn/words.py:392:        cause: measured, that alone lifts the yoked control from -0.001 to
state/communication/alternating_coupling.py:5:    PYTHONPATH=src python state/communication/alternating_coupling.py
state/communication/silence.py:5:    PYTHONPATH=src python state/communication/silence.py
state/communication/RESULTS.md:3:2026-07-22 · 재현 스크립트 `state/communication/integration_vs_representation.py`
state/communication/RESULTS.md:4:(실행: 저장소 루트에서 `PYTHONPATH=src python state/communication/integration_vs_representation.py`)
state/communication/RESULTS.md:78:재현 스크립트 `state/communication/alternating_coupling.py`.
state/communication/RESULTS.md:132:재현 스크립트 `state/communication/attractor_canonicalization.py`. 방향은 죽었고, **죽이는
state/communication/RESULTS.md:294:재현 스크립트 `state/communication/aligned_drive.py`.
state/communication/RESULTS.md:402:재현 스크립트 `state/communication/silence.py`.
state/communication/RESULTS.md:484:단어를 벌려면 지연 표본대조가 필요하다. 재현 스크립트 `state/communication/match.py`.
state/communication/RESULTS.md:544:재현 스크립트 `state/communication/capacity.py`, 결정 IIT 실행은 `coupled_phi(Wiring.PAIRS, ...)`.
state/communication/RESULTS.md:600:동시에 붙잡고 쓰는가. 재현 스크립트 `state/communication/concepts.py`. 설계는 위임했다.
state/communication/RESULTS.md:667:`state/communication/` 라인 전체를 **엔진끼리 소통**으로 좇았으나, 소유자가 정정했다: 소통은
state/communication/RESULTS.md:676:  귀무가 가능. 재현 스크립트 `state/communication/dialogue.py`.
state/communication/RESULTS.md:677:- **사람 주장**은 세션당 존재 증명이 될 것 — 자기 day-0, 자기 yoked 블록, 자기 로그의 순열
state/communication/RESULTS.md:690:| yoked 피드백 | 0.489 | | 결과가 확립한다 |
state/communication/RESULTS.md:691:| **frozen-engine (에코 검사)** | **0.496** | | **엔진이 load-bearing** |
state/communication/RESULTS.md:699:### 결정적 새 대조군 — frozen-engine (에코 트랩)
state/communication/aligned_drive.py:5:    PYTHONPATH=src python state/communication/aligned_drive.py
state/communication/aligned_drive.py:43:  unreachable, so `FIXED` must read the permutation floor. If it does not, the
state/communication/aligned_drive.py:178:    """Cross-modal identification, its permutation floor, and effective rank."""
state/communication/aligned_drive.py:306:        print(f"  {name} clears its OWN permutation ceiling on {clears}/{SEEDS} seeds")
state/communication/aligned_drive.py:380:        print(f"  {name} clears its OWN permutation ceiling on {clears}/{SEEDS} seeds")
state/communication/aligned_drive.py:396:        "\nbit-for-bit unreachable, so it must sit at the permutation floor."
state/communication/capacity.py:5:    PYTHONPATH=src python state/communication/capacity.py
state/communication/integration_vs_representation.py:5:    PYTHONPATH=src python state/communication/integration_vs_representation.py
state/lab/2026-07-22-communication-divergence-fable.md:4:지시문 원본: `state/lab/2026-07-22-communication-divergence-prompt.md`
state/lab/2026-07-22-communication-divergence-fable.md:5:파일럿 스크립트: `state/lab/2026-07-22-communication-divergence-pilot.py`
state/lab/2026-07-22-communication-divergence-fable.md:6:(실행: 저장소 루트에서 `PYTHONPATH=src python state/lab/2026-07-22-communication-divergence-pilot.py`)
state/lab/2026-07-22-communication-divergence-fable.md:301:(`state/communication/RESULTS.md` · Opus 4.8 · 서로의 존재를 모르는 채 4분 간격 커밋).
state/lab/2026-07-22-communication-divergence-prompt.md:3:보고서: `state/lab/2026-07-22-communication-divergence-fable.md`
state/lab/2026-07-22-communication-divergence-prompt.md:4:파일럿: `state/lab/2026-07-22-communication-divergence-pilot.py`
state/lab/2026-07-22-communication-divergence-prompt.md:39:  yoked. Real, consistent, and still far under the 0.30 emergence bar.
state/lab/2026-07-22-communication-divergence-prompt.md:86:   - communication as compression: the channel is too narrow for raw state, so whatever
state/lab/2026-07-22-consciousness-roadmap-fable.md:73:*Falsifiers:* λ = 0 must stay within noise of zero; a **yoked-replay control** (A reads a *recorded* partner from an independent run — partner-shaped statistics, no live channel) must kill the excess.
tests/test_words.py:408:    vocabulary: live +0.039, one-way +0.008, yoked -0.000, no channel -0.002.
tests/test_words.py:431:    def test_the_yoked_control_kills_it(self) -> None:
tests/test_words.py:442:    def test_the_yoked_recordings_must_not_share_a_source(self) -> None:
tests/test_rhythm.py:303:    `state/communication/silence.py`; pinned here so it cannot quietly stop
tests/test_rhythm.py:377:    `state/communication/match.py`.
tests/test_rhythm.py:450:    `state/communication/capacity.py`.
tests/test_rhythm.py:535:    Full composition in `state/communication/concepts.py`.
state/lab/2026-07-22-communication-divergence-pilot.py:1:"""Pilot measurement for the communication divergence report.
state/lab/2026-07-22-communication-divergence-pilot.py:8:`state/lab/2026-07-22-communication-divergence-fable.md` section 1 direction D1.
state/lab/2026-07-22-communication-divergence-pilot.py:24:Run from the repo root:  PYTHONPATH=src python state/lab/2026-07-22-communication-divergence-pilot.py

exec
/bin/zsh -lc "sed -n '650,725p' state/communication/RESULTS.md && sed -n '450,540p' state/communication/RESULTS.md && sed -n '1,100p' tests/test_dialogue.py && sed -n '610,745p' src/anima_reborn/viewer/page.html" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:

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
  조건부가 아니다. 두 모델이 같이 지목한 다음 검사는 **지연 표본대조** — 붙잡은 뒤 탐침을
  주고, 일치/불일치에 따라 엔진의 반응이 달라지는가. 아직 안 했다.
- 4유닛에서 1비트는 **구조적 상한**이다. 유닛을 늘리면 용량이 늘지만 Φ 는 6유닛에서 측정
  불가가 되므로, 용량과 측정 가능성이 여기서 정면으로 부딪힌다.
- sol 은 순열 검정만으로 끌개 교란이 처리된다고 봤으나, 붕괴가 이미 측정된 이상 fable 의
  명시적 유역-상한 쪽을 택했다.

---

## 지연 표본대조 — "쓴다"를 벌었다, 벌 수 있는 만큼만 (2026-07-23)

`silence.py` 는 고리가 침묵을 건너 1비트를 붙잡고 그 비트를 입력이 쓴다는 것까지 세웠다.
두 위임 설계가 똑같이 못 박은 다음 단계가 이것이다: **붙잡는 것은 쓰는 것이 아니고**, 더 센
단어를 벌려면 지연 표본대조가 필요하다. 재현 스크립트 `state/communication/match.py`.

**절차**: 무언가를 들려주고(400틱) → 귀머거리로 만들어 침묵(240틱) → **탐침**을 하나 준다.
엔진의 **반응**이 탐침이 붙잡은 것과 맞는지에 따라 달라지는가를 본다.

**왜 이건 "쓴다"를 벌 수 있나.** 이전 측정은 전부 우리가 엔진에 대고 하는 **판독**이다.
여기서 재는 양은 엔진 **자신의 반응** — 새 입력을 받아들이려면 얼마나 움직여야 하는가다.
학습도 없고, 해독기도 없고, 고른 문턱도 없다. 사전등록된 방향: **맞는 탐침은 덜 고쳐야 한다.**

### 상한을 재기 전에 유도했다

붙잡은 게 **1비트**(유역 2개)이므로, **같은 유역을 부르는 미끼는 원리적으로 구별 불가**다.
16개 입력이 k / 16−k 로 갈리면 완벽한 사용의 점수는 `(0.5(k−1) + (16−k)) / 15` 다.

| | 점수 |
| --- | ---: |
| 붙잡기만 하고 안 씀 | 0.500 |
| **붙잡은 1비트를 완벽히 씀** (실측 8.2/7.8 분할) | **0.758** |
| 1.000 | **불가능** — 1비트보다 많이 붙잡아야 나옴 |

### 측정 (16 입력 × 8 시드 · 전 미끼 15개 사용)

| 갈래 | 2지선다 | 최악 시드 | 판정 |
| --- | ---: | ---: | --- |
| **고리** | **0.729** | 0.725 | **붙잡은 비트의 89% 사용 · 8/8 시드 우연 이상** |
| 고리, 안 들려줌 | 0.500 | 0.500 | 안 씀 |
| 전방향 | 0.500 | 0.500 | 안 씀 |
| 자기참조 | 0.500 | 0.500 | 안 씀 |

### 대조군이 0.500 인 건 운이 아니라 **구조**다

붙잡은 상태가 **무엇을 들려줬는지와 무관**한 갈래에서는, (표적 t vs 미끼 f) 비교와 그 거울인
(표적 f vs 미끼 t) 비교가 **동일한 상태 하나**를 쓰므로 둘의 판정이 반대가 된다 — 정확히
하나만 적중. 그래서 **아무것도 안 붙잡은 갈래는 이 검사에서 우연을 넘을 수 없다.** 대조군이
안심용이 아니라 **빈틈없는** 이유이고, 고리의 여백이 채점 방식의 성질일 수 없는 이유다.

### 판정 — 얻은 문장

**엔진은 붙잡은 것을 쓴다.** 새 입력에 대한 엔진 자신의 반응이 그 입력이 붙잡은 것과 맞는지에
따라 달라지고, 순환 배선일 때만 그렇다. 이 저장소에서 처음으로 **엔진이 만드는 차이**이지
우리가 엔진에 대고 하는 판독이 아니다.

**그리고 그것은 1비트다.** 0.729 는 유도된 상한 0.758 의 89% 이고, 1.0 근처가 **아니어야**
맞다 — 1.0 이 나왔다면 침묵이 남긴 1비트가 아니라 **다른 것**을 재고 있다는 뜻이다.

### 안 얻은 것

- **개념이 아니라 비트다.** 16개 입력이 2개 유역으로 뭉개지므로, 쓰이는 것은 "무엇을
  들었는가"가 아니라 "어느 쪽으로 밀렸는가"다.
- 정렬된 개념 입력으로는 아직 안 돌렸다. 여기 입력은 정육면체 꼭짓점이라 **해독기 없는
  순수 엔진 성질**을 분리한 것이고, `align.py` 를 앞에 붙이는 것은 별도 실험이다.
- 4유닛에서 1비트는 구조적 상한이다. 유닛을 늘리면 용량이 늘지만 Φ 는 6유닛에서 측정
  불가가 되므로, **용량과 측정 가능성이 정면으로 부딪힌다** — 이게 이제 이 노선의 벽이다.

---

## 용량 대 측정 가능성 — 벽을 넘다: 위상학이 답이었다 (2026-07-23)
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
  }
}

// ── badges ─────────────────────────────────────────────────────────────────
const EMERGENCE_CLASS = { emergent: "good", partial: "mid", independent: "bad" };
// 표시 문자열만 한글로 바꾼다. 배지 색은 위의 원래 값(raw)으로 판정하고,
// 매핑에 없는 값은 원문 그대로 노출한다 — 없는 번역을 지어내지 않기 위해서다.
const KO = {
  emergent: "창발", partial: "부분적", independent: "독립",
  locked: "잠금", building: "형성 중", chaos: "융해",
  surprised: "놀람", excited: "격앙", thoughtful: "사려", calm: "평온", quiet: "고요",
};
const ko = v => KO[v] || v;
const EMERGENCE_TEXT = {
  emergent: "창발 ✨ — 어느 스트림도 혼자서는 갖지 못한 정보를 둘의 쌍이 담고 있습니다.",
  partial: "부분적 — 이 창 크기에서는 독립과 구분되지 않는 수준입니다.",
  independent: "독립 — 두 스트림이 공유하는 정보가 없습니다.",
};
const CRYSTAL_CLASS = { locked: "good", building: "mid", chaos: "bad" };
const CRYSTAL_TEXT = {
  locked: "잠금 ✨ — 주기-2 리듬. 구동과 반대 위상으로 맞물려 유지되고 있습니다.",
  building: "형성 중 — 지연1은 반대 위상으로 갔지만 지연2가 아직 따라오지 못했습니다.",
  chaos: "융해 — 구동의 불완전함이 이징 복구를 앞질렀습니다.",
};
const MOOD_CLASS = { surprised: "mid", excited: "bad", thoughtful: "good", calm: "good", quiet: "" };
const MOOD_TEXT = {
  surprised: "이번 틱에 간극이 급변했습니다.",
  excited: "높은 간극이 지속 — 두 엔진이 크게 벌어져 있습니다.",
  thoughtful: "사고가 일어나는 크기의 간극입니다.",
  calm: "작지만 실재하는 간극입니다.",
  quiet: "두 엔진이 하나로 붕괴 — 사고할 간극이 남지 않았습니다.",
};

function setBadge(el, text, cls) {
  el.textContent = text;
  el.className = "badge" + (cls ? " " + cls : "");
}

// ── streaming ──────────────────────────────────────────────────────────────
// The server pushes a frame per engine tick over one long-lived connection.
// Frames are stashed, not drawn on arrival; drawing happens on the display's
// own refresh, so a burst of frames costs one repaint rather than several.
const PREFIX = { emergence: "em", crystal: "cr", repulsion: "rp", pipeline: "pl", base: "bs", coupled: "cp", align: "al" };
const ROTATION = [];   // recent accumulated phase, so a stalled clock is visible

let active = "base";
let stream = null;
let pending = null;          // newest frame not yet drawn
let received = 0;            // frames since the last rate sample
let drawn = 0;
let engineRate = 0;

function controlsFor(name) {
  if (name === "emergence") return { coupling: $("em-coupling").value / 100 };
  if (name === "crystal") return { epsilon: $("cr-eps").value / 100 };
  if (name === "repulsion") return { separation: $("rp-sep").value / 100, noise: $("rp-noise").value / 100 };
  if (name === "base") return { epsilon: $("bs-eps").value / 100, separation: $("bs-sep").value / 100 };
  if (name === "coupled") return { wiring: $("cp-wiring").value, rhythm: $("cp-rhythm").value,
                                   gain: $("cp-gain").value / 10, drive: $("cp-drive").value / 10 };
  if (name === "align") return { rate: $("al-rate").value / 1000, noise: $("al-noise").value / 100,
                                 shuffled: $("al-shuffled").checked ? "1" : "0" };
  return { separation: $("pl-sep").value / 100 };
}

function connect(name) {
  if (stream) stream.close();
  pending = null;
  received = drawn = 0;
  ROTATION.length = 0;   // a stale span would distort the next rotation trace
  LEARNED.length = 0;

  const params = new URLSearchParams(controlsFor(name));
  stream = new EventSource(`/api/${name}/stream?${params}`);

  stream.addEventListener("hello", event => {
    engineRate = JSON.parse(event.data).rate;
  });
  stream.onmessage = event => {
    pending = JSON.parse(event.data);
    received++;
    const status = $(PREFIX[name] + "-status");
    if (status.classList.contains("err")) status.className = "status";
  };
  stream.onerror = () => {
    const status = $(PREFIX[name] + "-status");
    status.className = "status err";
    status.textContent = "스트림 끊김 — 재연결 중…";
  };
}

function pushControls(name) {
  const params = new URLSearchParams(controlsFor(name));
  fetch(`/api/${name}/control?${params}`).catch(() => {});
}

// ── draw loop ──────────────────────────────────────────────────────────────
function frame() {
  if (pending) {
    render(active, pending);
    pending = null;
    drawn++;
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

setInterval(() => {
  $("fps").textContent = `수신 ${received} fps · 그림 ${drawn}` +
    (engineRate ? ` · 엔진 ${Math.round(engineRate)} Hz` : "");
  received = drawn = 0;
}, 1000);

function render(name, data) {
  if (name === "emergence") renderEmergence(data);
  else if (name === "crystal") renderCrystal(data);
  else if (name === "repulsion") renderRepulsion(data);
  else if (name === "base") renderBase(data);
  else if (name === "coupled") renderCoupled(data);
  else if (name === "align") renderAlign(data);
  else renderPipeline(data);
}

function renderEmergence(d) {
  drawTrace($("em-l"), d.left, "#7b9aff", d.range, 250);
  drawTrace($("em-r"), d.right, "#a8e668", d.range, 250);
  drawScatter($("em-scatter"), d.left, d.right, d.range);

  const status = $("em-status");
  status.className = "status";
  if (!d.metrics) {
    status.textContent = `창을 채우는 중 — 엔트로피가 의미를 가지려면 ${d.left.length}/50 표본이 필요합니다.`;
    return;
  }
  const m = d.metrics;
  $("em-hl").textContent = m.h_left.toFixed(2);
  $("em-hr").textContent = m.h_right.toFixed(2);

exec
/bin/zsh -lc "sed -n '1,300p' src/anima_reborn/coupled.py" in /Users/mini/dancinlab/anima-reborn
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

codex
# Implementable design

One repository inconsistency must be resolved explicitly: the executable `dialogue.py` uses `word = sign(v0-v1)` followed by the learned `engine_recv[word]` policy, although its prose describes a less-revision probe action. The published numbers and frozen-policy null come from the executable path. The viewer should reuse that executable protocol. Do not silently implement a different probe-based receiver; if that prose is normative, fix and rerun the reproducible half first.

## 1. One live session

A session is one person, two anonymous contexts, and fixed preregistered counts. It is never combined with another session.

### Trial counts

| Phase | Trials | Feedback | Updates |
|---|---:|---|---|
| Practice | 4 each direction, excluded | explanatory | none |
| Day-0 | 16 per context per direction = 64 actions | none | none |
| Acquisition | 40 paired live/yoked rounds per direction = 160 actions | after both paired actions | engine policies only |
| Held-out test | A: 48 human actions; B: 144 human actions | none | none |

Total: 416 scored actions plus 8 practice actions, approximately 15–25 minutes.

Every direction/context/arm has exactly balanced referents. Orders are shuffled from a precommitted schedule. No early stopping or intermediate accuracy is shown.

### Two contexts

The participant sees two arbitrary context markers, such as `방 ◇` and `방 ○`. They are not told which is contingent.

Each context has independent:

- `engine_recv` and `engine_send` 2×2 policies.
- Human signal glyphs and their mapping to integer signals.
- Display unit-marker mapping.
- RNG substreams.

One context is live; the other is yoked. The assignment is revealed only in the final report.

### Direction A: human → engine

1. The page shows one stable target token, such as `◆` or `●`.
2. It shows two stable signal glyphs belonging to that context.
3. The signal buttons exchange left/right positions independently every trial.
4. The human clicks a signal identity, not “answer 0/1.”
5. The server maps the glyph to `signal`, runs TELL 200 + HOLD 120, obtains `word`, and samples the engine’s `act` from `engine_recv[word]`.
6. The server alone computes `success = int(act == referent)`.

The page never receives the engine’s action or a “correct signal.”

### Direction B: engine → human

1. The server chooses a hidden balanced referent.
2. It samples `signal` from `engine_send[referent]`.
3. It runs the same channel and records all 120 two-unit HOLD states.
4. The page receives only that raw trace and the two target tokens.
5. Target-token buttons exchange left/right positions independently every trial.
6. The human chooses a token identity; the server maps it to `act`.
7. The server computes `success = int(act == referent)`.

The hidden referent, engine signal, latch word, policy row, and correctness are absent from the pre-action response.

### Day-0

Both contexts and both directions are presented before any feedback or update. This produces 32 observations per direction when the two contexts are pooled, while retaining context-stratified rows in the log.

### Acquisition and yoked consequence

Each acquisition round contains two trials of the same direction, one from each context:

1. Present both trials in random context order.
2. Accept both human actions.
3. Compute both actual task successes.
4. Only after both actions, reveal consequences:
   - Live context reward = its own actual success.
   - Yoked context reward = the paired live context’s success.
5. Update each engine with its own local state and choice plus the routed reward.

Thus the yoked context receives the exact same marginal reward sequence at the exact same round numbers, but its reward is unrelated to its own current referent/action. The log stores `actual_success` and `reward` separately. The participant sees only `reward`, so the yoked UI must not reveal its actual result through text, timing, animation, or response shape.

The human has no server-side policy. Human learning consists only of their subsequent recorded choices.

### Held-out test

All policies are frozen, feedback is withheld, and all test counts are completed.

Direction A presents:

- 24 live-context trials.
- 24 yoked-context trials.

For each live human signal, the server also evaluates three invisible counterfactual receivers:

- Frozen day-0 engine.
- Deaf channel.
- Uniformly scrambled signal.

This needs no extra human action because all four receivers consume the same recorded human signal.

Direction B presents 24 trials from each of six arms, interleaved without arm labels:

- Live.
- Yoked.
- Frozen engine.
- Deaf channel.
- Uniform signal scramble.
- Display-identity scramble.

All non-yoked arms use the learned live context’s visible tokens and codec so the participant cannot identify a null from styling.

## 2. The display as the second aperture

### Normal display

The B-direction payload contains the 120 raw HOLD samples:

```text
trace = [[v0_t0, v1_t0], ..., [v0_t119, v1_t119]]
```

It does not contain the latch bit or a derived difference, sign, label, probability, suggested target, or success.

The canvas draws two un-smoothed polylines with:

- One shared symmetric y-scale.
- A numeric scale annotation.
- No threshold line and no “high/low” annotation.
- Two neutral, stable unit markers.

At session creation, each context independently randomizes the bijection:

```text
physical unit 0/1 ↔ neutral marker ◇/○
```

That mapping remains stable during normal trials because changing unit identity every trial would destroy the one-bit channel. On every trial, however:

- The vertical lane order is randomized.
- Target-token left/right position is randomized.
- In direction A, signal-glyph left/right position is randomized.

The neutral marker, not screen position or color, preserves unit identity. Marker assignment is independent of referents and committed before the session.

### Display-scramble null

In B test display-scramble trials, the physical-unit-to-marker mapping is independently swapped with probability ½ each trial, while the trace, engine policy, target balance, canvas, and button randomization remain unchanged.

If normal B recovery is real because the human learned to read the engine display, this manipulation must destroy it. If it remains high, some unlogged cue or answer leakage exists and the session receives `audit_failed`.

### Why the UI cannot tell the answer

- In A, the target is intentionally visible, but the UI never knows which signal the engine will act on.
- In B, the target identities are visible as possible actions, but the chosen referent is not sent to the browser.
- The client submits a stable choice ID, never a button index or x-coordinate.
- Success is computed after submission on the server from task identities.

## 3. Live echo control

At session creation, copy the live context’s initial policies:

```text
frozen_recv = deepcopy(live.engine_recv)  # [[1,1],[1,1]]
frozen_send = deepcopy(live.engine_send)  # [[1,1],[1,1]]
```

Record and hash them. They are never updated.

- In A test, the human’s learned live-context signal is passed through a fresh normal channel, but `act` is sampled from `frozen_recv[word]`. This is evaluated as a shadow outcome beside the real receiver.
- In B test, `frozen_send[referent]` supplies the signal; the human sees the resulting raw trace through the learned live display codec and acts normally.

This freezes only the learned engine policies, not the physical channel or the human. A fully trained human is therefore tested against the engine’s day-0 half. Frozen accuracy near chance shows that the engine’s learned mapping was load-bearing rather than merely returning the human’s bit.

## 4. Per-session statistics

### What is reported

Every accuracy row must include:

```text
hits / n · accuracy · 95% Wilson interval
task rank 2 · held-state width 1 bit · physical carrier 2 units
```

The 120×2 displayed samples do not make the channel “240-dimensional”; the held state has two latch states and therefore width one bit.

Report A and B in separate tables. Never average them.

Also report, separately for each direction:

- Referent→signal 2×2 contingency.
- Signal→held-word 2×2 contingency.
- Held-word→act 2×2 contingency.
- End-to-end referent→act accuracy.
- Observed signal and word support, `1/2` or `2/2`.
- Normal and every null arm.

Any orientation used to summarize a one-way code is learned from acquisition and applied unchanged to test. It is never selected on test.

Cross-direction consistency is only:

```text
dominant A and B mappings agree on k/2 referents
```

It is not a symmetric-code score and is not folded into accuracy.

### Primary permutation test

Use only frozen, feedback-free observations: day-0 and held-out test. Acquisition rows are not permuted.

Define:

```text
C_A = max(day0_A, yoked_A, frozen_A, deaf_A, signal_scramble_A)

C_B = max(day0_B, yoked_B, frozen_B, deaf_B,
          signal_scramble_B, display_scramble_B)

T = min(live_A - 0.5,
        live_B - 0.5,
        live_A - C_A,
        live_B - C_B)
```

This minimum requires two independent one-way codes and requires each to beat every relevant null. It never averages directions.

Run 99,999 permutations plus the observed arrangement:

- Within each preregistered `direction × phase/context/arm` stratum, permute the balanced referent labels.
- Hold human actions, traces, signal identities, button positions, lane orders, engine actions, and timing fixed.
- For A shadow arms, apply one referent permutation to the whole trial row so the correlations among live/frozen/deaf/scramble outcomes are preserved.
- Recompute every accuracy and `T`.

Use:

```text
p = (1 + count(T_perm >= T_observed)) / 100000
```

The permutation RNG seed is derived from the canonical final-log hash, making the analysis reproducible without pretending the human was seeded.

The null is: after preserving every side bias, context bias, response frequency, and display schedule in this person’s log, task referents are exchangeable with respect to recorded actions; no trialwise convention is required.

The full verdict requires:

- `T > 0`.
- One-sided permutation `p ≤ 0.05`.
- Both live arms have observed signal support `2/2` and held-word support `2/2`.
- Neither structural audit failed.
- The session completed its precommitted count.

If the joint test fails, compute direction-specific versions of the same statistic and Holm-correct the two p-values. This permits an honest one-way result.

Exact raw verdicts and Korean rendering:

- `two_way_session_evidence`:  
  `이 세션에서만: 이 사람과 이 엔진은 결과를 통해 두 개의 사적인 1비트 단방향 관습을 확립하고 피드백 없는 시험에서 사용했다. 사람 일반, 이해, 언어에 대한 주장이 아니다.`
- `one_way_session_evidence`:  
  `이 세션에서는 한 방향의 1비트 관습 증거만 있다. 양방향 소통으로 보고하지 않는다.`
- `no_session_evidence`:  
  `이 세션에서는 모든 대조군을 넘는 관습 증거가 없다.`
- `audit_failed`:  
  `감사 대조군이 실패했다. 이 세션의 양성 정확도에는 소통 증거를 부여하지 않는다.`

Badge color keys off these raw values; `ko()` supplies display text.

No cross-person mean, pooled p-value, “success rate across users,” or selective gallery is produced. Aborted and negative sessions remain exportable.

## 5. `server.py` and `page.html`

### Server-side object

Use a viewer-owned `DialogueSession`, not a new package engine:

```text
DialogueSession
  id, write_token, lock
  protocol_version, seed_commitment, fixed schedule
  phase, sequence, pending trial/pair
  live engine_send/engine_recv
  yoked engine_send/engine_recv
  frozen day-0 snapshots
  independent RNG streams
  display codecs
  append-only trial log
  final statistics
  condition variable for state changes
```

Each trial creates the same seeded two-unit `CoupledEngine` channel used by `dialogue.py`. The session owns learned policies; the channel remains per-trial, as in the reproducible harness.

Derive independent RNG streams from a secret session seed and labels such as `referent`, `engine-choice`, `channel`, `display`, and `analysis`. Commit to the seed, schedule, protocol version, arm assignment, and policy snapshots before the first scored action; reveal them at completion.

### Registry and ticker behavior

Do not add `dialogue` to `_HANDLERS` or `TICK_RATES`. A zero-Hz ticker is still the wrong abstraction.

Instead add:

```text
_SESSION_HANDLERS = {"dialogue": _DialogueSessionHandler}
```

`Viewer.names()` continues to mean passive tickable engines. Add `Viewer.session_names()` for interactive protocols, and update the page lockstep test to require tabs/panels/renderers for the union.

The dialogue stream is condition-driven:

- It publishes immediately when a session is created, an action is accepted, a pair completes, or the phase changes.
- It sends keep-alive comments while waiting.
- It never calls `step()` merely because a browser is watching.
- Leaving the tab disconnects the stream but does not reset or advance the session.

### HTTP surface

Add bounded JSON `POST` handling:

```text
POST /api/dialogue/session
POST /api/dialogue/session/<id>/action
POST /api/dialogue/session/<id>/advance
POST /api/dialogue/session/<id>/abort
GET  /api/dialogue/session/<id>/state
GET  /api/dialogue/session/<id>/stream
GET  /api/dialogue/session/<id>/log
```

Every prompt carries a single-use trial nonce. Duplicate submission returns the prior response without another action or update. Stale or out-of-order nonces are rejected.

A random write capability held in JavaScript memory protects actions because the viewer currently binds to the LAN. Session IDs alone may read/resume but cannot submit.

The server appends canonical JSONL after every accepted action. Each row contains all hidden experimental fields, randomization decisions, trace, policy checksums before/after, `actual_success`, routed `reward`, and timestamps. I/O remains under `viewer/`; core engines remain stdlib-only and I/O-free.

### Harness-owned scoring

The browser may submit only:

```text
trial_nonce
choice_id
```

The server resolves `choice_id` to `signal` or `act`, then computes:

```text
success = int(act == referent)
```

The client cannot submit success, reward, referent, engine word, or arm.

### Page controls

The tab needs only:

- `새 세션`
- `시작`
- Two choice buttons
- `다음`
- `중단` — permanently marks the session aborted
- `로그 내보내기` after completion

There is no reset, seed selector, arm selector, trial-count slider, correctness inspector, or live accuracy display.

Add:

- `data-tab="dialogue"`
- `id="p-dialogue"`
- `dialogue: "dg"` in `PREFIX`
- `renderDialogue(data)`
- A dialogue-specific connection path rather than generic passive `connect()`

Update the header claim that the page “only draws”: passive tabs only draw; the dialogue tab sends choice identities, while the server still schedules, scores, rewards, and analyzes.

## 6. Additional ways to fake a positive

| Fake positive | Control |
|---|---|
| Always choosing one target in an imbalanced test | Exactly balanced referents; permutation preserves action bias |
| Learning screen side instead of a token | Per-trial button and lane-position randomization; server receives identity, not position |
| A universal experimenter-chosen code | Per-session committed signal, target, and unit-marker bijections |
| Rewarding intention rather than outcome | Server-only `act == referent`; client cannot submit reward |
| Yoked feedback accidentally tracking its own success | Both paired actions precede feedback; yoked reward is copied from the paired live row; log both values |
| Learning during the test | Policies frozen, no feedback, no per-trial result, fixed test count |
| Engine bypassing the physical channel | Deaf and signal-scramble arms |
| Human reading a hidden answer field | B payload allowlist and forbidden-field test |
| Human reading a renderer convention | Day-0 display score plus per-trial display-identity scramble |
| Engine echoing the human | Day-0 frozen send/receive policies in the same trained session |
| Cherry-picking people, sessions, or stopping points | Precommitted counts; completed, aborted, negative, and positive logs retained; no cross-person aggregate |
| Correlated RNG streams leaking schedules | Domain-separated RNG streams and final seed/schedule verification |
| Double-clicking to obtain a favorable redraw | Single-use idempotent trial nonce |
| Calling two one-way mappings one symmetric language | Separate A/B tables and minimum statistic; cross-direction agreement reported only as `k/2` |
| A downstream display seeming informative when its input was not | Stagewise 2×2 tables; no credit if referent→signal or signal→word collapsed |
| A lossy stage being described as wider than its input | Every accuracy states rank 2 and width one bit; raw sample count is not capacity |

## The two structural audits

1. Reinforcement audit: retain the exact signature  
   `_reinforce(policy, state, choice, reward)`.  
   A signature test rejects any partner state, referent from the other agent, or direct access to the other policy.

2. Display-aperture audit: construct B prompts only through  
   `_display_payload(trace, unit_markers, lane_order, target_order)`.  
   Its signature and serialized allowlist contain no `referent`, `signal`, `word`, `success`, `reward`, policy, or arm. A test inspects both the signature and every pre-action payload.

Together with the behavioral frozen and display-scramble arms, these seal both mouths of the experimenter-owned interpreter.
tokens used
68,337
# Implementable design

One repository inconsistency must be resolved explicitly: the executable `dialogue.py` uses `word = sign(v0-v1)` followed by the learned `engine_recv[word]` policy, although its prose describes a less-revision probe action. The published numbers and frozen-policy null come from the executable path. The viewer should reuse that executable protocol. Do not silently implement a different probe-based receiver; if that prose is normative, fix and rerun the reproducible half first.

## 1. One live session

A session is one person, two anonymous contexts, and fixed preregistered counts. It is never combined with another session.

### Trial counts

| Phase | Trials | Feedback | Updates |
|---|---:|---|---|
| Practice | 4 each direction, excluded | explanatory | none |
| Day-0 | 16 per context per direction = 64 actions | none | none |
| Acquisition | 40 paired live/yoked rounds per direction = 160 actions | after both paired actions | engine policies only |
| Held-out test | A: 48 human actions; B: 144 human actions | none | none |

Total: 416 scored actions plus 8 practice actions, approximately 15–25 minutes.

Every direction/context/arm has exactly balanced referents. Orders are shuffled from a precommitted schedule. No early stopping or intermediate accuracy is shown.

### Two contexts

The participant sees two arbitrary context markers, such as `방 ◇` and `방 ○`. They are not told which is contingent.

Each context has independent:

- `engine_recv` and `engine_send` 2×2 policies.
- Human signal glyphs and their mapping to integer signals.
- Display unit-marker mapping.
- RNG substreams.

One context is live; the other is yoked. The assignment is revealed only in the final report.

### Direction A: human → engine

1. The page shows one stable target token, such as `◆` or `●`.
2. It shows two stable signal glyphs belonging to that context.
3. The signal buttons exchange left/right positions independently every trial.
4. The human clicks a signal identity, not “answer 0/1.”
5. The server maps the glyph to `signal`, runs TELL 200 + HOLD 120, obtains `word`, and samples the engine’s `act` from `engine_recv[word]`.
6. The server alone computes `success = int(act == referent)`.

The page never receives the engine’s action or a “correct signal.”

### Direction B: engine → human

1. The server chooses a hidden balanced referent.
2. It samples `signal` from `engine_send[referent]`.
3. It runs the same channel and records all 120 two-unit HOLD states.
4. The page receives only that raw trace and the two target tokens.
5. Target-token buttons exchange left/right positions independently every trial.
6. The human chooses a token identity; the server maps it to `act`.
7. The server computes `success = int(act == referent)`.

The hidden referent, engine signal, latch word, policy row, and correctness are absent from the pre-action response.

### Day-0

Both contexts and both directions are presented before any feedback or update. This produces 32 observations per direction when the two contexts are pooled, while retaining context-stratified rows in the log.

### Acquisition and yoked consequence

Each acquisition round contains two trials of the same direction, one from each context:

1. Present both trials in random context order.
2. Accept both human actions.
3. Compute both actual task successes.
4. Only after both actions, reveal consequences:
   - Live context reward = its own actual success.
   - Yoked context reward = the paired live context’s success.
5. Update each engine with its own local state and choice plus the routed reward.

Thus the yoked context receives the exact same marginal reward sequence at the exact same round numbers, but its reward is unrelated to its own current referent/action. The log stores `actual_success` and `reward` separately. The participant sees only `reward`, so the yoked UI must not reveal its actual result through text, timing, animation, or response shape.

The human has no server-side policy. Human learning consists only of their subsequent recorded choices.

### Held-out test

All policies are frozen, feedback is withheld, and all test counts are completed.

Direction A presents:

- 24 live-context trials.
- 24 yoked-context trials.

For each live human signal, the server also evaluates three invisible counterfactual receivers:

- Frozen day-0 engine.
- Deaf channel.
- Uniformly scrambled signal.

This needs no extra human action because all four receivers consume the same recorded human signal.

Direction B presents 24 trials from each of six arms, interleaved without arm labels:

- Live.
- Yoked.
- Frozen engine.
- Deaf channel.
- Uniform signal scramble.
- Display-identity scramble.

All non-yoked arms use the learned live context’s visible tokens and codec so the participant cannot identify a null from styling.

## 2. The display as the second aperture

### Normal display

The B-direction payload contains the 120 raw HOLD samples:

```text
trace = [[v0_t0, v1_t0], ..., [v0_t119, v1_t119]]
```

It does not contain the latch bit or a derived difference, sign, label, probability, suggested target, or success.

The canvas draws two un-smoothed polylines with:

- One shared symmetric y-scale.
- A numeric scale annotation.
- No threshold line and no “high/low” annotation.
- Two neutral, stable unit markers.

At session creation, each context independently randomizes the bijection:

```text
physical unit 0/1 ↔ neutral marker ◇/○
```

That mapping remains stable during normal trials because changing unit identity every trial would destroy the one-bit channel. On every trial, however:

- The vertical lane order is randomized.
- Target-token left/right position is randomized.
- In direction A, signal-glyph left/right position is randomized.

The neutral marker, not screen position or color, preserves unit identity. Marker assignment is independent of referents and committed before the session.

### Display-scramble null

In B test display-scramble trials, the physical-unit-to-marker mapping is independently swapped with probability ½ each trial, while the trace, engine policy, target balance, canvas, and button randomization remain unchanged.

If normal B recovery is real because the human learned to read the engine display, this manipulation must destroy it. If it remains high, some unlogged cue or answer leakage exists and the session receives `audit_failed`.

### Why the UI cannot tell the answer

- In A, the target is intentionally visible, but the UI never knows which signal the engine will act on.
- In B, the target identities are visible as possible actions, but the chosen referent is not sent to the browser.
- The client submits a stable choice ID, never a button index or x-coordinate.
- Success is computed after submission on the server from task identities.

## 3. Live echo control

At session creation, copy the live context’s initial policies:

```text
frozen_recv = deepcopy(live.engine_recv)  # [[1,1],[1,1]]
frozen_send = deepcopy(live.engine_send)  # [[1,1],[1,1]]
```

Record and hash them. They are never updated.

- In A test, the human’s learned live-context signal is passed through a fresh normal channel, but `act` is sampled from `frozen_recv[word]`. This is evaluated as a shadow outcome beside the real receiver.
- In B test, `frozen_send[referent]` supplies the signal; the human sees the resulting raw trace through the learned live display codec and acts normally.

This freezes only the learned engine policies, not the physical channel or the human. A fully trained human is therefore tested against the engine’s day-0 half. Frozen accuracy near chance shows that the engine’s learned mapping was load-bearing rather than merely returning the human’s bit.

## 4. Per-session statistics

### What is reported

Every accuracy row must include:

```text
hits / n · accuracy · 95% Wilson interval
task rank 2 · held-state width 1 bit · physical carrier 2 units
```

The 120×2 displayed samples do not make the channel “240-dimensional”; the held state has two latch states and therefore width one bit.

Report A and B in separate tables. Never average them.

Also report, separately for each direction:

- Referent→signal 2×2 contingency.
- Signal→held-word 2×2 contingency.
- Held-word→act 2×2 contingency.
- End-to-end referent→act accuracy.
- Observed signal and word support, `1/2` or `2/2`.
- Normal and every null arm.

Any orientation used to summarize a one-way code is learned from acquisition and applied unchanged to test. It is never selected on test.

Cross-direction consistency is only:

```text
dominant A and B mappings agree on k/2 referents
```

It is not a symmetric-code score and is not folded into accuracy.

### Primary permutation test

Use only frozen, feedback-free observations: day-0 and held-out test. Acquisition rows are not permuted.

Define:

```text
C_A = max(day0_A, yoked_A, frozen_A, deaf_A, signal_scramble_A)

C_B = max(day0_B, yoked_B, frozen_B, deaf_B,
          signal_scramble_B, display_scramble_B)

T = min(live_A - 0.5,
        live_B - 0.5,
        live_A - C_A,
        live_B - C_B)
```

This minimum requires two independent one-way codes and requires each to beat every relevant null. It never averages directions.

Run 99,999 permutations plus the observed arrangement:

- Within each preregistered `direction × phase/context/arm` stratum, permute the balanced referent labels.
- Hold human actions, traces, signal identities, button positions, lane orders, engine actions, and timing fixed.
- For A shadow arms, apply one referent permutation to the whole trial row so the correlations among live/frozen/deaf/scramble outcomes are preserved.
- Recompute every accuracy and `T`.

Use:

```text
p = (1 + count(T_perm >= T_observed)) / 100000
```

The permutation RNG seed is derived from the canonical final-log hash, making the analysis reproducible without pretending the human was seeded.

The null is: after preserving every side bias, context bias, response frequency, and display schedule in this person’s log, task referents are exchangeable with respect to recorded actions; no trialwise convention is required.

The full verdict requires:

- `T > 0`.
- One-sided permutation `p ≤ 0.05`.
- Both live arms have observed signal support `2/2` and held-word support `2/2`.
- Neither structural audit failed.
- The session completed its precommitted count.

If the joint test fails, compute direction-specific versions of the same statistic and Holm-correct the two p-values. This permits an honest one-way result.

Exact raw verdicts and Korean rendering:

- `two_way_session_evidence`:  
  `이 세션에서만: 이 사람과 이 엔진은 결과를 통해 두 개의 사적인 1비트 단방향 관습을 확립하고 피드백 없는 시험에서 사용했다. 사람 일반, 이해, 언어에 대한 주장이 아니다.`
- `one_way_session_evidence`:  
  `이 세션에서는 한 방향의 1비트 관습 증거만 있다. 양방향 소통으로 보고하지 않는다.`
- `no_session_evidence`:  
  `이 세션에서는 모든 대조군을 넘는 관습 증거가 없다.`
- `audit_failed`:  
  `감사 대조군이 실패했다. 이 세션의 양성 정확도에는 소통 증거를 부여하지 않는다.`

Badge color keys off these raw values; `ko()` supplies display text.

No cross-person mean, pooled p-value, “success rate across users,” or selective gallery is produced. Aborted and negative sessions remain exportable.

## 5. `server.py` and `page.html`

### Server-side object

Use a viewer-owned `DialogueSession`, not a new package engine:

```text
DialogueSession
  id, write_token, lock
  protocol_version, seed_commitment, fixed schedule
  phase, sequence, pending trial/pair
  live engine_send/engine_recv
  yoked engine_send/engine_recv
  frozen day-0 snapshots
  independent RNG streams
  display codecs
  append-only trial log
  final statistics
  condition variable for state changes
```

Each trial creates the same seeded two-unit `CoupledEngine` channel used by `dialogue.py`. The session owns learned policies; the channel remains per-trial, as in the reproducible harness.

Derive independent RNG streams from a secret session seed and labels such as `referent`, `engine-choice`, `channel`, `display`, and `analysis`. Commit to the seed, schedule, protocol version, arm assignment, and policy snapshots before the first scored action; reveal them at completion.

### Registry and ticker behavior

Do not add `dialogue` to `_HANDLERS` or `TICK_RATES`. A zero-Hz ticker is still the wrong abstraction.

Instead add:

```text
_SESSION_HANDLERS = {"dialogue": _DialogueSessionHandler}
```

`Viewer.names()` continues to mean passive tickable engines. Add `Viewer.session_names()` for interactive protocols, and update the page lockstep test to require tabs/panels/renderers for the union.

The dialogue stream is condition-driven:

- It publishes immediately when a session is created, an action is accepted, a pair completes, or the phase changes.
- It sends keep-alive comments while waiting.
- It never calls `step()` merely because a browser is watching.
- Leaving the tab disconnects the stream but does not reset or advance the session.

### HTTP surface

Add bounded JSON `POST` handling:

```text
POST /api/dialogue/session
POST /api/dialogue/session/<id>/action
POST /api/dialogue/session/<id>/advance
POST /api/dialogue/session/<id>/abort
GET  /api/dialogue/session/<id>/state
GET  /api/dialogue/session/<id>/stream
GET  /api/dialogue/session/<id>/log
```

Every prompt carries a single-use trial nonce. Duplicate submission returns the prior response without another action or update. Stale or out-of-order nonces are rejected.

A random write capability held in JavaScript memory protects actions because the viewer currently binds to the LAN. Session IDs alone may read/resume but cannot submit.

The server appends canonical JSONL after every accepted action. Each row contains all hidden experimental fields, randomization decisions, trace, policy checksums before/after, `actual_success`, routed `reward`, and timestamps. I/O remains under `viewer/`; core engines remain stdlib-only and I/O-free.

### Harness-owned scoring

The browser may submit only:

```text
trial_nonce
choice_id
```

The server resolves `choice_id` to `signal` or `act`, then computes:

```text
success = int(act == referent)
```

The client cannot submit success, reward, referent, engine word, or arm.

### Page controls

The tab needs only:

- `새 세션`
- `시작`
- Two choice buttons
- `다음`
- `중단` — permanently marks the session aborted
- `로그 내보내기` after completion

There is no reset, seed selector, arm selector, trial-count slider, correctness inspector, or live accuracy display.

Add:

- `data-tab="dialogue"`
- `id="p-dialogue"`
- `dialogue: "dg"` in `PREFIX`
- `renderDialogue(data)`
- A dialogue-specific connection path rather than generic passive `connect()`

Update the header claim that the page “only draws”: passive tabs only draw; the dialogue tab sends choice identities, while the server still schedules, scores, rewards, and analyzes.

## 6. Additional ways to fake a positive

| Fake positive | Control |
|---|---|
| Always choosing one target in an imbalanced test | Exactly balanced referents; permutation preserves action bias |
| Learning screen side instead of a token | Per-trial button and lane-position randomization; server receives identity, not position |
| A universal experimenter-chosen code | Per-session committed signal, target, and unit-marker bijections |
| Rewarding intention rather than outcome | Server-only `act == referent`; client cannot submit reward |
| Yoked feedback accidentally tracking its own success | Both paired actions precede feedback; yoked reward is copied from the paired live row; log both values |
| Learning during the test | Policies frozen, no feedback, no per-trial result, fixed test count |
| Engine bypassing the physical channel | Deaf and signal-scramble arms |
| Human reading a hidden answer field | B payload allowlist and forbidden-field test |
| Human reading a renderer convention | Day-0 display score plus per-trial display-identity scramble |
| Engine echoing the human | Day-0 frozen send/receive policies in the same trained session |
| Cherry-picking people, sessions, or stopping points | Precommitted counts; completed, aborted, negative, and positive logs retained; no cross-person aggregate |
| Correlated RNG streams leaking schedules | Domain-separated RNG streams and final seed/schedule verification |
| Double-clicking to obtain a favorable redraw | Single-use idempotent trial nonce |
| Calling two one-way mappings one symmetric language | Separate A/B tables and minimum statistic; cross-direction agreement reported only as `k/2` |
| A downstream display seeming informative when its input was not | Stagewise 2×2 tables; no credit if referent→signal or signal→word collapsed |
| A lossy stage being described as wider than its input | Every accuracy states rank 2 and width one bit; raw sample count is not capacity |

## The two structural audits

1. Reinforcement audit: retain the exact signature  
   `_reinforce(policy, state, choice, reward)`.  
   A signature test rejects any partner state, referent from the other agent, or direct access to the other policy.

2. Display-aperture audit: construct B prompts only through  
   `_display_payload(trace, unit_markers, lane_order, target_order)`.  
   Its signature and serialized allowlist contain no `referent`, `signal`, `word`, `success`, `reward`, policy, or arm. A test inspects both the signature and every pre-action payload.

Together with the behavioral frozen and display-scramble arms, these seal both mouths of the experimenter-owned interpreter.
[32mlab full: both sections saved → /Users/mini/.sidecar/lab/2026-07-23T04-58-54-545Z-full.md[0m
