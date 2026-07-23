<!-- sidecar lab full · model=(default) · cwd=/Users/mini/dancinlab/anima-reborn · prompt=5640 chars · 2026-07-23T07:58:31.587Z -->

── fable (claude-fable-5) · exit 0 ──
Memory saved. Here is the complete design deliverable:

---

# The honest answer to "실제 영어 대화가능하게 설계"

**The answer is no — and the deliverable is the design that proves it live, with the owner's own sentences, quantified.** Real English conversation requires unbounded bits per utterance; this substrate holds 3 measurable-integrated bits, and that ceiling is a theorem plus a measurement, not an engineering shortfall. The only honest "design for real English" is therefore: let real English **enter**, measure exactly how much of it **survives** the engine, and close the door on the rest **by measurement**. An external LLM would make English appear (and is banned by `engine-purity`), but even permitted, it would be the LLM conversing while the engine carries 3 bits — the same trap with a bigger costume. Named and refused.

## 1. Which interpretation

**Interpretation 1 (measure the English bottleneck) is the feature, with interpretation 3 (the wall, closed by measurement) as its companion result.** They are two halves of one answer: the wall experiment says *why* 3 bits is the ceiling; the live bottleneck tab lets the owner *feel* it — type a real sentence, watch 3 bits come out the other side.

- **Interpretation 2 (English-labeled cards) is refused as a standalone.** Labeling buys nothing measurable — the bits are identical — and adds pure overclaim surface: the human's pattern-completion does all the English work and credits the engine. There is exactly one honest place for labels (v2, post-audit, provenance-tagged — see §5), and the line between it and the trap is stated there explicitly.
- **Interpretation 3 alone** would be the purist's ship (one-line dissent: a sol-style reviewer would land only the proof and stop). But it gives the owner a document, not a thing to touch, and this repo's culture is measurement *plus* a live viewer.
- **Interpretation 4 (engine as measured relay between two English speakers)** is honest but needs a second live seat — deferred. Its core experience (two utterances identical after the bottleneck) is captured more cheaply by the **collision display** below, the single most valuable anti-projection element in the design.

## 2. The concrete feature: the `영어` tab — `EnglishBottleneck`

New module `src/anima_reborn/english.py`, class `EnglishBottleneck` (has `step`/`reset`, so `TestEngineViewerLockstep` auto-detects it; ships with all seven viewer touchpoints per `viewer-newengine`). Stdlib only (`zlib` is stdlib), seedable, no I/O — typing stays in `viewer/`.

**The codebook — and who does the reading.** A fixed, always-visible codebook of 8 English phrases (with Korean glosses), e.g. `hello` / `yes` / `no` / `more` / `stop` / `good` / `bad` / `bye`. Crucially, **the human is the encoder**: they type a free English utterance, then themselves pick which of the 8 classes it means. This is deliberate — a keyword classifier would be a fake NLP stage whose own fidelity we'd have to measure against human intent (`channel-before-carrier`), and it would let the UI pretend the machine reads English. With the human as encoder, the design states plainly: *all* English competence on screen belongs to the human and the codec; the engine receives 3 bits even from a perfect encoder. The wall is the channel, not the codec.

**The flow, per utterance:**
1. Human types real English. The harness measures its description length: `len(zlib.compress(text, 9)) − empty_baseline`, in bits, displayed as "서술 길이 ~X비트 (deflate 근사, 상한)" — a *measured* proxy, labeled as such, short-string overhead recorded in docs and a test (`artefact-honesty`).
2. Human picks the class (0–7). UI shows the quantization: "X비트 → 3비트."
3. The 3 bits enter the measured-clean `channel(bits=3)` PAIRS wire (`dialogue.channel`, fidelity 1.000, TELL=200/HOLD=120), are held in the integrated substrate through the HOLD window, and read out.
4. The recovered 3 bits decode to the codebook phrase — displayed **bits-first** (the six ◇○□△▽☆ lanes), phrase second, in a visually distinct panel tagged "코드북 라벨 (하네스)". The full 8-phrase codebook stays on screen with the selection highlighted, so the reply's 7 unchosen alternatives are always visible.

**Measured per session (nothing assumed):**
- **I(class_in; class_out)** — exact, ≤ 3 bits by construction; the headline surviving-information number. We do *not* claim to measure "MI over English" (open space, unmeasurable in-session); we measure the class channel exactly and bound English survival by it.
- **Effective input bits** = entropy of the class distribution the human actually used (`report-the-rank`): utterances collapsed onto 2 classes report ~1 effective bit, not 3.
- **Per-utterance surviving-fraction bound**: ≤ 3/X against the deflate proxy.
- **Channel fidelity** printed beside every recovery (`channel-before-carrier`).

**The nulls (same commit, live buttons in the UI):**
- **Deaf arm** — drive bit-unreachable (coupling 1.0, per `aligned_drive.py`): recovery must sit at 1/8; proves the engine was in the path at all.
- **No-engine arm** — class → phrase directly, bypassing the substrate: scores perfectly by construction, and that is its *point* — it shows on screen that every drop of English fluency belongs to codec + human, and the engine's entire contribution is what the deaf arm loses: carrying 3 bits.
- **Lane-scramble** — data permuted among fixed appearance lanes (the corrected null from `conversation.py`), guarding the bits-first display against appearance-reading.

**The collision display.** The session log groups utterances by encoded class and shows the equivalence classes explicitly: *"오늘 입력한 문장 중 9개가 엔진에게는 전부 같은 것이었습니다"* — the 9 sentences listed side by side. Nothing communicates "3 bits, forever" more viscerally, and it is pure measured fact.

**The wall experiment: `state/communication/english_wall.py`.** Runnable, seeded, one script:
- Exact arithmetic: a closed vocabulary of size V needs ⌈log₂V⌉ bits/word — even a toy 26-word vocabulary needs 10 bits for a two-word utterance, i.e. 20 units / 10 pairs (even — which `capacity.py` already showed locks into a macro-ring).
- Measured side: sweep odd pairs p ∈ {3, 5, 7, 9, 11}; at each width measure (a) raw channel fidelity and (b) the *decay-test* integration verdict (past six units the decay test is the verdict, never the `RECURRENCE_FLOOR` magnitude — calibrated at four units, does not transfer). RESULTS.md already records Φ unmeasurable past ~6 units; the script re-derives it at the English-relevant widths rather than quoting it forward.
- Deliverable: the frontier of bits-holdable-integrated vs. bits-English-needs, with no crossing. Verdict written only after the numbers exist.

## 3. The verdict sentences — the exact line

**May claim (Korean, per `doc-language`/`ui-language`):**

> "사람의 실제 영어 문장(서술 길이 중앙값 X비트, deflate 근사)이 8-부호 코드북으로 양자화되어 측정된 3비트 채널(충실도 f, 무입력 대조 1/8)을 통과했다 — 문장당 살아남은 정보는 최대 3비트, 세션 실측 상호정보 I비트, 실효 입력 폭 E비트. 언어도, 이해도 아니다."

and, after `english_wall.py` produces its numbers:

> "N비트를 통합된 상태로 보유하는 데 필요한 유닛 수와 통합이 측정 가능한 유닛 수는 [측정된 지점]에서 갈라진다 — 통합된 영어는 설계 부족이 아니라 측정으로 닫혔다."

**Must NOT appear, in any phrasing:** "엔진이 영어로 대화한다/응답했다/이해했다/말했다" — any sentence whose English-producing grammatical subject is the engine. The decoded phrase is never the engine's output; the engine's output is 3 bits and the phrase is the harness's label for them. A phrase displayed without its provenance tag is a bug of the same severity as an unmeasured number.

## 4. Keeping the human's pattern-completion honest

Six structural mechanisms, not disclaimers: (1) bits-first rendering — lanes above the phrase, phrase in a codec-styled panel tagged "코드북 라벨 (하네스)", never anything resembling a speech bubble from the engine; (2) the full 8-phrase codebook permanently on screen — projection needs an open possibility space, and this closes it; (3) the collision display; (4) deaf and no-engine arms as one-click buttons, so the "conversation" can be broken and un-Englished live; (5) the report leads with the surviving-bits number before any transcript; (6) human-as-encoder itself — you cannot mistake the engine for a reader of your sentence when you just performed that reading yourself, every turn.

## 5. Smallest honest first commit, and what is deferred

- **Commit 1 — the answer:** `state/communication/english_wall.py` + its RESULTS.md section (Korean). Pure `state/`, no engine change, no viewer obligation. The owner gets the real answer — the measured wall — before any feature ships.
- **Commit 2 — the instrument:** `english.py` + the `영어` tab (all seven lockstep touchpoints in one commit, per `viewer-lockstep`) + tests (deflate-overhead pin, deaf-arm 1/8, lockstep) + a docstring carrying the max-honest sentence, mirroring `conversation.py`'s.
- **Deferred:** (a) *v2 — the only honest home for interpretation 2*: after a `대화` session's blind audit verifies a k≤3-bit convention, the codebook phrases may label **that audited convention**, provenance-tagged, audit numbers leading; labels on unaudited free play stay banned — that is precisely the line between v2 and the trap. (b) The two-human relay (interpretation 4), needing a second live seat. (c) Store-and-recall ("the engine remembered ≤3 bits of what you said yesterday") riding on the `silence.py` deaf-hold result. Every deferred item keeps the same verdict grammar: the engine carries; it never speaks.

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
session id: 019f8df7-2792-7171-a9df-a19d20e6856f
--------
user
# Design task: the owner asked for REAL English conversation. Design the maximally HONEST response.

The owner of `anima-reborn` (a Python research repo whose whole culture is refusing to
overclaim) just said, in Korean: **"실제 영어 대화가능하게 설계" — "design it so that ACTUAL
English conversation is possible."** They have already seen the `대화` tab: a free, live 3-bit
exchange of abstract cards, honestly labeled "not language, not understanding." They now want
real English.

Your job is NOT to fake it. It is to design the maximally honest thing we can actually build,
and to state precisely where the wall is. Return a concrete, implementable design plus the
honesty framing. Do NOT write full code.

## The hard, non-negotiable facts (this repo proved them; do not hand-wave them)

1. **The substrate holds at most 3 bits.** A single ring of any even width holds exactly 1 bit
   (a theorem: the per-unit response is odd, decreasing, bounded → no orbit longer than 2).
   `Wiring.PAIRS` holds units/2 bits AND stays integrated only for an ODD number of pairs, and
   the integration measure Φ becomes unmeasurable past ~6 units. So the measurable-integrated
   capacity ceiling is ~3 bits. English is unbounded: one English word carries ~10-40 bits, a
   sentence hundreds. 3 bits distinguishes 8 things, forever.
2. **engine-purity is a hard rule**: standard library only, zero runtime deps, no network, no
   external model, all I/O confined to `viewer/`. So you CANNOT call an external LLM to produce
   English — and even if you could, that would be the LLM conversing, not the engine.
3. **The repo's honesty rules are hard rules**, enforced by tests: measure-first (no number that
   wasn't measured), claims-need-controls (every claim ships with the null that could fake it),
   report-the-rank (report effective width beside any accuracy), channel-before-carrier (score
   what enters a stage before crediting what leaves it), and the standing refusal to claim
   "language" or "understanding."
4. The existing honest instrument: `Conversation` (free 3-bit exchange + blind audit), and
   `align.py` (the only learner — co-occurrence teaches two modalities to meet, scored only on
   held-out concepts).

## The trap to name and refuse

Slapping 8 English words on the 8 cards makes the UI LOOK like English while carrying 3 bits.
That is the display-encodes-the-answer trap in a new costume: the human's pattern-completion
supplies the "English," the engine supplies 3 bits. Any design must make that impossible to
mistake — the English must never be presented as the engine's, and the report must lead with
how many bits actually survived.

## The interpretations to evaluate (address each, then recommend)

1. **Measure the English bottleneck (the wall, as a real result).** The human types real English;
   it is encoded to the engine's few bits, held/transmitted through the engine, decoded back
   toward English. MEASURE how much survives — mutual information in bits between input and
   output English, against the deaf/scramble nulls and the channel's own capacity. The honest
   deliverable is a NUMBER: "~3 bits of your sentence survived; the rest did not" — a
   demonstration that English conversation is NOT happening, quantified. Is this honest,
   buildable stdlib-only, and does it actually answer the owner? What exactly is measured, what
   is the null, what is the verdict sentence?
2. **An English-LABELED 3-bit codec, brutally framed.** The 8 cards carry English words (a
   fixed 8-word closed vocabulary), the convention forms by consequence as now, but the report
   and UI relentlessly show it is 3 bits and the words are the human's projection. Where is the
   line between this and interpretation-1's honesty? Does labeling buy anything real, or does it
   only add overclaim risk?
3. **Prove it is impossible and stop.** Sometimes the honest deliverable is a measurement that
   closes the door: show that to carry even a two-word English utterance you would need N units,
   at which Φ is unmeasurable, so "integrated English" is out of reach BY MEASUREMENT. Is there a
   crisp, runnable experiment that establishes this wall, so the owner has the real answer rather
   than a toy?
4. Is there ANY other honest sense in which this engine can engage English — e.g., as a lossy
   RELAY between two English-speaking humans where we measure preserved information (the engine
   as a measured communication bottleneck, not a speaker)? If so, design it.

## What I need — answer each explicitly

1. **Which interpretation** is the honest, buildable answer to "real English conversation," and
   why. One-line dissent if you'd choose differently.
2. **The concrete experiment / feature**: what is encoded, what the engine does, what is decoded,
   what is measured, in one commit, stdlib-only, seedable, with its nulls. If it involves an
   English corpus, it must be a small fixed stdlib-embeddable one (no download).
3. **The verdict sentence** the UI and RESULTS.md may claim, and the sentence they must NOT —
   the exact line between "English passed through a measured 3-bit bottleneck" and "the engine
   conversed in English."
4. **How to keep the human's pattern-completion from overclaiming** when English text is on screen.
5. **The smallest honest first commit**, and what is deferred.

Keep the discipline: never write a number that was not measured; ship every claim with the null
that could fake it; report the surviving fraction / effective bits beside any accuracy; the
engine is not language. If the honest answer is "you cannot, and here is the proof," say so
plainly and design the proof.

codex
I’ll anchor the design in the repo’s existing interfaces and measurement conventions, then give an explicit recommendation, one-commit experiment, nulls, and exact allowed/forbidden claims. I’m treating “actual English conversation” as a capability claim to test—not as permission to relabel the 3-bit cards.
exec
/bin/zsh -lc "pwd && rg --files -g '"'!*__pycache__*'"' | sed -n '1,240p'" in /Users/mini/dancinlab/anima-reborn
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
state/lab/2026-07-22-communication-divergence-pilot.py
state/lab/2026-07-23-conversation-prompt.md
state/lab/2026-07-22-words-prompt.md
state/lab/2026-07-22-communication-divergence-prompt.md
state/lab/2026-07-22-consciousness-roadmap-fable.md
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
tests/test_words.py
tests/test_crystal.py
tests/test_iit4.py
tests/test_emergence.py
tests/test_directed.py
pyproject.toml
LICENSE

exec
/bin/zsh -lc "sed -n '1,260p' CLAUDE.md && sed -n '1,260p' src/anima_reborn/CLAUDE.md && sed -n '1,260p' src/anima_reborn/viewer/CLAUDE.md && sed -n '1,280p' src/anima_reborn/conversation.py && sed -n '1,320p' src/anima_reborn/align.py" in /Users/mini/dancinlab/anima-reborn
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
# src/anima_reborn/viewer/ — the I/O boundary

The browser view of the engines. This is the **only** package in `anima_reborn` allowed
to open a socket, read a clock, spawn a thread or hold mutable shared state — the
engines next door stay pure, and that separation is the point.

| file | role |
| --- | --- |
| `server.py` | `Viewer` (one engine of each kind + a lock each) and the stdlib HTTP server |
| `page.html` | the whole UI — canvas drawing, controls, polling. No build step, no CDN |
| `__main__.py` | `python -m anima_reborn.viewer` |

## The rule that makes the viewer worth having

**The browser must never simulate anything.** Every number and every plotted point comes
from a Python engine over `/api/<engine>`; the page maps values to pixels and nothing
else. The moment a formula from `emergence.py` or `crystal.py` gets reimplemented in
JavaScript, the viewer stops being evidence about the port and becomes a second,
unverified implementation that will silently drift.

## Contract

- `GET /` → `page.html`
- `GET /api/<engine>/stream?<controls>` → **the path the page uses.** One long-lived
  `text/event-stream`; the engine's ticker pushes a frame per tick
- `GET /api/<engine>/control?<controls>` → hand the ticker new slider values
- `GET /api/<engine>/reset` → rewind that engine
- `GET /api/<engine>?steps=N&<controls>` → one-shot: step `N` times and return a frame.
  Kept for `curl` and for tests that want a frame without a socket

Controls are clamped, never rejected: a stale query string must not push an engine
outside the range it validates. Unparseable values fall back to the engine's current
setting. `steps` is capped at `MAX_STEPS_PER_REQUEST` on the one-shot path; the stream
has no such knob because its rate belongs to the server.

## Why push rather than poll

Polling capped the frame rate at the poll interval and paid a TCP handshake per frame
(`BaseHTTPRequestHandler` defaults to HTTP/1.0). Measured: engines cost 0.02–0.23 ms per
tick and a LAN round trip is 1.1 ms, so nothing but the poll loop stood between this
viewer and the origin's 60 fps. `TICK_RATES` carries the origin's `setInterval` periods (and 30 Hz for `base`, which has no origin),
so an engine runs at the speed its thresholds were chosen against.

`protocol_version = "HTTP/1.1"` enables keep-alive, which is why every non-streaming
response **must** send a `Content-Length`. The stream deliberately does not, and sets
`Connection: close` instead.

## Ticker threads

`_Ticker` steps one engine and broadcasts frames to subscribers over a `Condition`. It
runs only while watched. Restarting carries a **generation** number: a thread whose
generation is stale retires, so a fast unsubscribe/subscribe — switching tabs quickly —
cannot leave two threads stepping one engine. Without that guard, eight quick tab
switches left nine threads running at 9× the intended rate;
`tests/test_viewer.py::TestTicker::test_rapid_resubscribe_leaves_one_thread` fails
loudly if the guard is removed.

## Lockstep with the engines

Every engine has a tab, and every tab has an engine — checked by
`tests/test_viewer.py::TestEngineViewerLockstep`, not by memory. It fails on an engine
with no route, a route with no engine, a missing tick rate, tab, panel, `PREFIX` entry or
`render<Name>()`, and on a default tab that disagrees with `let active`.

Restart after any `.py` edit: `page.html` is re-read on every request, `server.py` is
loaded once at process start. A fresh page against a stale server is what
`스트림 끊김` (stream interrupted) in the UI actually means.

## When adding an engine

1. Add a handler class with `configure(engine, params)` and `describe(engine) -> dict`,
   and register it in `_HANDLERS` and `Viewer.__init__`.
2. `describe` must **read** state, never advance it. Every engine exposes a state
   property for this; `advance` already stepped exactly as many times as asked. A
   describe that steps makes the engine run faster than the page requested —
   `tests/test_viewer.py` has a test per engine guarding precisely this.
3. Round floats on the way out (`_round`). The page draws pixels; full float repr is
   most of the payload and none of the picture.
4. Add a tab, a render function and a `STEPS` entry in `page.html`.

## Binding

`serve()` defaults to `0.0.0.0` so another machine on the network can reach the viewer
by IP, and says so in the startup banner. There is no authentication — this is a
development viewer for a trusted network, not a public service.
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

exec
/bin/zsh -lc "sed -n '1,260p' src/anima_reborn/conversation.py && sed -n '260,620p' src/anima_reborn/conversation.py && sed -n '1,300p' state/communication/capacity.py && sed -n '1,320p' state/communication/RESULTS.md && sed -n '1,240p' src/anima_reborn/info.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
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
                int(pick(self._frozen_recv[j][word_bits[j]], self._rng) == ref_bits[j])
                for j in range(BITS)
            ]
            dword = _bits_of(channel(signal, seed=pending["channel_seed"], deaf=True, bits=BITS))
            entry["deaf_success"] = [
                int(pick(self._recv[j][dword[j]], self._rng) == ref_bits[j])
                for j in range(BITS)
            ]
            sc = self._rng.randrange(8)
            sword = _bits_of(channel(sc, seed=pending["channel_seed"], bits=BITS))
            entry["scramble_success"] = [
                int(pick(self._recv[j][sword[j]], self._rng) == ref_bits[j])
                for j in range(BITS)
            ]
            self._probe_log.append(entry)
        else:
            for j in range(BITS):
                reinforce(self._recv[j], word_bits[j], act_bits[j], float(successes[j]))
            self._free_log.append(entry)
            self._reveal(_A, referent, _pack(act_bits), successes)
        self._after_resolved()

    def _resolve_b(self, pending: dict[str, Any], move: dict[str, Any]) -> None:
        blind = pending["blind"]
        referent = pending["referent"]
        act = int(move.get("act", 0)) % 8
        ref_bits = _bits_of(referent)
        act_bits = _bits_of(act)
        successes = tuple(int(act_bits[j] == ref_bits[j]) for j in range(BITS))
        entry = {
            "dir": _B, "arm": pending["arm"], "blind": blind, "phase": self._phase,
            "referent": referent, "signal": pending["signal"], "act": act,
            "success": list(successes), "markers_swapped": pending.get("markers_swapped", False),
        }
        if blind:
            self._probe_log.append(entry)
        else:
            sig_bits = _bits_of(pending["signal"])
            for j in range(BITS):
                reinforce(self._send[j], ref_bits[j], sig_bits[j], float(successes[j]))
            self._free_log.append(entry)
            self._reveal(_B, referent, act, successes)
        self._after_resolved()

    def _reveal(self, direction: str, referent: int, act: int, successes: tuple[int, ...]) -> None:
        self._last_reveal = {
            "dir": direction, "referent": referent, "act": act, "success": list(successes),
        }
        self._transcript.append(dict(self._last_reveal))
        if len(self._transcript) > 40:
            self._transcript.pop(0)

    def _after_resolved(self) -> None:
        if self._phase in ("baseline", "audit"):
            self._cursor += 1
        self._open_next()

    def _begin_audit(self) -> None:
        # Freeze learning: the audit runs on the policies as they are now, never updating.
        self._phase = "audit"
        self._cursor = 0
        self._audit = self._blind_plan(
            AUDIT_LIVE_PER_DIR, arms_b=("live", "frozen", "deaf", "dscramble")
        )
        self._open_next()

    def _finish(self) -> None:
        if self._report is None:
            self._report = conversation_stats(self._probe_log)

    # -- viewer read-side --------------------------------------------------------------

    @property
    def phase(self) -> str:
        return self._phase

    def describe(self) -> dict[str, Any]:
        frame: dict[str, Any] = {
            "phase": self._phase,
            "free_turns": len(self._free_log),
            "token": self._token,
            "transcript": list(self._transcript[-8:]),
        }
        if self._phase in ("baseline", "audit"):
            plan = self._baseline if self._phase == "baseline" else self._audit
            frame["progress"] = {"done": self._cursor, "total": len(plan)}
        if self._pending is not None:
            p = self._pending
            pend: dict[str, Any] = {"nonce": p["nonce"], "mode": p["mode"]}
            if p["mode"] == "compose_a":
                pend["show_referent"] = p.get("show_referent")
                pend["blind"] = p["blind"]
            elif p["mode"] == "read_b":
                pend["trace"] = p["display"]["trace"]
                pend["markers"] = p["display"]["markers"]
                pend["blind"] = p["blind"]
            frame["pending"] = pend
            frame["reveal"] = self._last_reveal if not p.get("blind") else None
        if self._report is not None:
            frame["report"] = self._report
        return frame

    def take_report(self) -> dict[str, Any] | None:
        if self._report is None or self._report_taken:
            return None
        self._report_taken = True
        return {
            "report": self._report, "token": self._token,
            "free_log": self._free_log, "probe_log": self._probe_log,
        }


# ── the per-session statistics ──────────────────────────────────────────────────────

_PERMUTATIONS = 10000


def _rate(hits: int, n: int) -> float | None:
    return None if n == 0 else hits / n


def _bit_permutation(rows: list[dict[str, Any]], j: int) -> tuple[int, int, float]:
    """Per-bit accuracy on live rows and its label-permutation p (referent-bit shuffled,
    actions fixed). Returns (hits, n, p)."""
    acts = [(r["act"] >> j) & 1 for r in rows]
    refs = [(r["referent"] >> j) & 1 for r in rows]
    n = len(rows)
    if n == 0:
        return 0, 0, 1.0
    hits = sum(int(a == b) for a, b in zip(acts, refs))
    obs = hits / n
    rng = random.Random(90001 + j)
    perm = list(refs)
    ge = 0
    for _ in range(_PERMUTATIONS):
        rng.shuffle(perm)
        if statistics.mean(int(a == b) for a, b in zip(acts, perm)) >= obs:
            ge += 1
    return hits, n, (1 + ge) / (1 + _PERMUTATIONS)


def _support(rows: list[dict[str, Any]], key: str, j: int) -> int:
    return len({(r[key] >> j) & 1 for r in rows})


def _null_rate(rows: list[dict[str, Any]], *, key: str = "success") -> float | None:
    """Joint accuracy (all 3 bits correct) over rows; `key` selects the success list."""
    n = len(rows)
    if n == 0:
        return None
    hits = sum(1 for r in rows if all(r[key]))
    return hits / n


def conversation_stats(probe_log: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-direction, per-bit verdict from the blind audit only. Never averaged over
    people; the free log is not evidence. Reports effective width k/3 beside accuracy —
    only k bits whose own permutation clears alpha and whose support is 2/2 are claimed."""
    alpha = 0.05

    def rows(direction: str, arm: str = "live", phase: str = "audit") -> list[dict[str, Any]]:
        return [
            r for r in probe_log
            if r["dir"] == direction and r["arm"] == arm and r.get("phase") == phase
        ]

    has_audit = any(r.get("phase") == "audit" for r in probe_log)

    directions: dict[str, Any] = {}
    for direction in (_A, _B):
        live = rows(direction)  # audit-phase live rows only — never the day-0 baseline
        baseline = rows(direction, "live", phase="baseline")
        per_bit = []
        k = 0
        for j in range(BITS):
            hits, n, p = _bit_permutation(live, j)
            sig_support = _support(live, "signal", j)
            act_support = _support(live, "act", j)
            formed = (n > 0 and hits / n > 0.5 and p <= alpha
                      and sig_support == 2 and act_support == 2)
            k += int(formed)
            per_bit.append({
                "bit": j, "hits": hits, "n": n, "accuracy": _rate(hits, n), "p": p,
                "signal_support": sig_support, "act_support": act_support,
                "formed": formed,
            })
        joint_hits = sum(1 for r in live if all(r["success"]))
        # Nulls. Direction A: free counterfactuals on the same signal. Direction B: dedicated
        # arms. dscramble is the load-bearing display audit.
        if direction == _A:
            nulls = {
                "day0": _null_rate(baseline),
                "frozen": _null_rate(live, key="frozen_success"),
                "deaf": _null_rate(live, key="deaf_success"),
                "scramble": _null_rate(live, key="scramble_success"),
            }
        else:
            nulls = {
                "day0": _null_rate(baseline),
                "frozen": _null_rate(rows(direction, "frozen")),
                "deaf": _null_rate(rows(direction, "deaf")),
                "dscramble": _null_rate(rows(direction, "dscramble")),
            }
        directions[direction] = {
            "per_bit": per_bit,
            "k_of_3": k,
            "joint_hits": joint_hits, "joint_n": len(live),
            "joint_accuracy": _rate(joint_hits, len(live)),
            "effective_bits": k,
            "nulls": {key: {"rate": val} for key, val in nulls.items()},
        }

    # audit_failed if the display-scramble null (direction B) is not near chance: the human
    # read the answer through a cue the display was not meant to carry.
    dsc = directions[_B]["nulls"].get("dscramble", {}).get("rate")
    audit_failed = dsc is not None and dsc > 0.375  # joint chance 1/8; 0.375 = 3x chance

    ka, kb = directions[_A]["k_of_3"], directions[_B]["k_of_3"]
    if not has_audit:
        verdict = "no_audit"
    elif audit_failed:
        verdict = "audit_failed"
    elif ka > 0 and kb > 0:
        verdict = "two_way_session_evidence"
    elif ka > 0 or kb > 0:
        verdict = "one_way_session_evidence"
    else:
        verdict = "no_session_evidence"

    return {
        "a": directions[_A], "b": directions[_B],
        "verdict": verdict, "permutations": _PERMUTATIONS, "alpha": alpha,
        "channel_fidelity": 1.0,  # measured in state/communication/conversation_channel.py
        "width_note": "substrate 3 latches / 8 states; claimed = k of 3 bits",
    }
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

codex
The key distinction is now clear: a fixed English renderer can make the channel’s mutual information look maximally good while preserving no sentence meaning at all. So the experiment must report two separate stages—what the encoder extracted from English, then what the substrate preserved—and must never treat a canned decoder string as evidence of language.
exec
/bin/zsh -lc "rg -n \"def channel|def channel_trace|class Wiring|PAIRS|capacity|mutual|fidelity|effective|deaf|scram\" src/anima_reborn/dialogue.py src/anima_reborn/coupled.py state/communication/capacity.py state/communication/conversation_channel.py tests/test_conversation_channel.py tests/test_conversation.py README.md | sed -n '1,280p' && sed -n '1,240p' state/communication/conversation_channel.py && sed -n '1,260p' tests/test_conversation_channel.py && sed -n '1,240p' tests/test_conversation.py" in /Users/mini/dancinlab/anima-reborn
 succeeded in 0ms:
tests/test_conversation.py:6:frame carries no answer), the corrected display-scramble null (a lawful reader collapses
tests/test_conversation.py:19:    access). Under a display-scramble this reads the permuted data and is wrong."""
tests/test_conversation.py:54:    # The lawful reader sees only the display — the trace as shown (possibly scrambled).
tests/test_conversation.py:88:        """Reading the shown trace collapses under the scramble, so the display null stays
tests/test_conversation.py:92:        assert report["b"]["nulls"]["dscramble"]["rate"] <= 0.375
tests/test_conversation.py:95:        """Reading the true latch survives the scramble, so the display null stays high and
tests/test_conversation.py:99:        assert report["b"]["nulls"]["dscramble"]["rate"] > 0.375
tests/test_conversation.py:121:    def test_a_dscramble_probe_actually_permutes(self) -> None:
tests/test_conversation.py:123:        # push straight to the audit so dscramble arms appear
tests/test_conversation.py:131:            if session._pending and session._pending.get("arm") == "dscramble"
tests/test_conversation.py:133:        assert any(swapped), "no dscramble probe reported a swap"
state/communication/capacity.py:5:    PYTHONPATH=src python state/communication/capacity.py
state/communication/capacity.py:16:`units / 2` bits — via `units / 2` two-cycles, which is `Wiring.PAIRS`.
state/communication/capacity.py:28:**What counts as capacity here.** Only states the DRIVE reproduces. A pattern
state/communication/capacity.py:31:`WALKS` independent walks land on the same pattern, and capacity is the number
state/communication/capacity.py:57:    """The sign pattern left after being told something and then made deaf."""
state/communication/capacity.py:68:    engine.rhythm = FIXED  # deaf — the drive cannot be heard at all
state/communication/capacity.py:82:def capacity(
state/communication/capacity.py:103:    reachable, held, share = capacity(units, wiring=wiring, chain=chain)
state/communication/capacity.py:112:    print(f"capacity — {WALKS} walks per drive, tell {TELL}, deaf silence {SILENCE}")
state/communication/capacity.py:132:            wiring=Wiring.PAIRS,
src/anima_reborn/dialogue.py:34:day-0, frozen, deaf, scramble, yoked and permutation numbers, and nothing more. Not
src/anima_reborn/dialogue.py:65:# The 3-bit channel is the proven `Wiring.PAIRS` substrate (units/2 latches, integrated at
src/anima_reborn/dialogue.py:67:# fidelity at 1.000 (joint) over the whole TELL/HOLD sweep, with the deaf null at 1/8, so
src/anima_reborn/dialogue.py:69:PAIRS_CHAIN = 0.2
src/anima_reborn/dialogue.py:73:    """Per-unit drive for the PAIRS channel: pair j is pushed +/- by bit j of `symbol`."""
src/anima_reborn/dialogue.py:81:def channel_trace(
src/anima_reborn/dialogue.py:82:    signal: int, *, seed: int, deaf: bool = False, bits: int = 1
src/anima_reborn/dialogue.py:88:    is the 6-unit `Wiring.PAIRS` (3 odd latches, chain 0.2), each pair driven +/- by one bit
src/anima_reborn/dialogue.py:90:    frozen for a HOLD phase. `deaf` sets coupling to 1.0 for the whole run so the drive is
src/anima_reborn/dialogue.py:101:        wiring, units, chain = Wiring.PAIRS, 6, PAIRS_CHAIN
src/anima_reborn/dialogue.py:107:        rhythm=FIXED if deaf else ALTERNATING,
src/anima_reborn/dialogue.py:119:def channel(signal: int, *, seed: int, deaf: bool = False, bits: int = 1) -> int:
src/anima_reborn/dialogue.py:124:    final = channel_trace(signal, seed=seed, deaf=deaf, bits=bits)[-1]
src/anima_reborn/dialogue.py:165:    3-bit PAIRS channel), the neutral per-unit markers, and the (already randomized) button
src/anima_reborn/dialogue.py:187:TEST_NULL_B_PER_ARM = 8  # dedicated frozen / deaf B trials (the human must act on a trace)
src/anima_reborn/dialogue.py:274:        # The held-out test: live A/B, plus dedicated frozen/deaf B trials the human must
src/anima_reborn/dialogue.py:275:        # act on. Direction-A frozen/deaf/scramble come free as counterfactuals at resolve
src/anima_reborn/dialogue.py:280:        add("test", _B, _MAIN, TEST_NULL_B_PER_ARM, arm="deaf")
src/anima_reborn/dialogue.py:281:        add("test", _B, _MAIN, TEST_NULL_B_PER_ARM, arm="dscramble")
src/anima_reborn/dialogue.py:336:            deaf = arm == "deaf"
src/anima_reborn/dialogue.py:337:            trace = channel_trace(signal, seed=channel_seed, deaf=deaf)
src/anima_reborn/dialogue.py:338:            # Display-identity scramble (the second-aperture null): on a `dscramble` trial
src/anima_reborn/dialogue.py:347:            swapped = arm == "dscramble" and self._rng.random() < 0.5
src/anima_reborn/dialogue.py:412:                dword = channel(signal, seed=pending["channel_seed"], deaf=True)
src/anima_reborn/dialogue.py:413:                entry["deaf_success"] = int(
src/anima_reborn/dialogue.py:416:                scrambled = self._rng.randrange(2)
src/anima_reborn/dialogue.py:417:                sword = channel(scrambled, seed=pending["channel_seed"])
src/anima_reborn/dialogue.py:418:                entry["scramble_success"] = int(
src/anima_reborn/dialogue.py:558:        # frozen/deaf trials.
src/anima_reborn/dialogue.py:561:            deaf = _accuracy(live, "deaf_success")
src/anima_reborn/dialogue.py:562:            scramble = _accuracy(live, "scramble_success")
src/anima_reborn/dialogue.py:563:            dscramble = (0, 0)  # display leak is a direction-B concern (A shows the referent)
src/anima_reborn/dialogue.py:566:            deaf = _accuracy(block("test", direction, arm="deaf"))
src/anima_reborn/dialogue.py:567:            scramble = (0, 0)
src/anima_reborn/dialogue.py:568:            dscramble = _accuracy(block("test", direction, arm="dscramble"))
src/anima_reborn/dialogue.py:576:            "day0": day0, "frozen": frozen, "deaf": deaf,
src/anima_reborn/dialogue.py:577:            "scramble": scramble, "dscramble": dscramble, "yoked": yoked,
src/anima_reborn/dialogue.py:581:        # learned half must be load-bearing), deaf (the channel must be in the path), and
src/anima_reborn/dialogue.py:582:        # for direction B the display-identity scramble (the targeted second-aperture null,
src/anima_reborn/dialogue.py:583:        # better powered than the 12-trial day-0). scramble and yoked are reported beside as
src/anima_reborn/dialogue.py:585:        structural = (rate(day0), rate(frozen), rate(deaf), rate(dscramble))
src/anima_reborn/dialogue.py:602:    # A high display-identity-scramble null means the human read the answer through a cue
src/anima_reborn/dialogue.py:605:    dscramble_rate = directions[_B]["nulls"]["dscramble"]["rate"]
src/anima_reborn/dialogue.py:606:    audit_failed = dscramble_rate is not None and dscramble_rate > 0.65
state/communication/conversation_channel.py:1:"""Calibrate the 3-bit PAIRS channel before its constants are frozen.
state/communication/conversation_channel.py:8:ring: `Wiring.PAIRS` (6 units, 3 odd pairs, `chain=0.2`), proven in `capacity.py` to hold
state/communication/conversation_channel.py:11:fidelity is the human's accuracy ceiling and must be MEASURED here first, so a human's
state/communication/conversation_channel.py:16:- **per-bit fidelity** = P(decoded latch bit == driven bit), each of the 3 pairs, over all
state/communication/conversation_channel.py:19:- **joint fidelity** = P(all 3 bits correct) = the exact-symbol reproducibility, the number
state/communication/conversation_channel.py:20:  `capacity.py` reported as ~88%.
state/communication/conversation_channel.py:21:- **the deaf null**: coupling 1.0 for the whole run makes the drive bit-unreachable, so the
state/communication/conversation_channel.py:23:  in the path. Reported as the deaf joint fidelity (should sit at 1/8 chance).
state/communication/conversation_channel.py:49:def pairs_word(symbol: int, *, seed: int, tell: int, hold: int, deaf: bool = False) -> int:
state/communication/conversation_channel.py:52:        units=UNITS, wiring=Wiring.PAIRS, chain=CHAIN,
state/communication/conversation_channel.py:53:        rhythm=FIXED if deaf else ALTERNATING,
state/communication/conversation_channel.py:67:def _fidelity(*, tell: int, hold: int, deaf: bool = False) -> tuple[list[float], float]:
state/communication/conversation_channel.py:68:    """Per-bit and joint fidelity over all 8 symbols x SEEDS."""
state/communication/conversation_channel.py:74:            word = pairs_word(symbol, seed=seed * 13 + 1, tell=tell, hold=hold, deaf=deaf)
state/communication/conversation_channel.py:85:    print("3-bit PAIRS channel calibration — 6 units, 3 odd pairs, chain=0.2")
state/communication/conversation_channel.py:93:            per_bit, joint = _fidelity(tell=tell, hold=hold)
state/communication/conversation_channel.py:102:    # The deaf null at a representative setting — the channel must be in the path.
state/communication/conversation_channel.py:103:    _, deaf_joint = _fidelity(tell=400, hold=240, deaf=True)
state/communication/conversation_channel.py:104:    print(f"\n  deaf (coupling 1.0, tell=400 hold=240): joint {deaf_joint:.3f} "
state/communication/conversation_channel.py:114:        print(f"  this joint fidelity is the human's accuracy CEILING and must be printed "
tests/test_conversation_channel.py:1:"""The 3-bit PAIRS channel added for the free-conversation tab, and its 1-bit exactness.
tests/test_conversation_channel.py:5:it (`default-stays-exact`). `bits=3` is the proven `Wiring.PAIRS` substrate, calibrated in
tests/test_conversation_channel.py:6:`state/communication/conversation_channel.py`; these pin its driven-decode fidelity and its
tests/test_conversation_channel.py:7:deaf null so the channel's own fidelity (the human's accuracy ceiling) cannot silently rot.
tests/test_conversation_channel.py:16:def _old_one_bit_channel(signal: int, *, seed: int, deaf: bool = False) -> int:
tests/test_conversation_channel.py:21:        rhythm=FIXED if deaf else ALTERNATING,
tests/test_conversation_channel.py:35:                for deaf in (False, True):
tests/test_conversation_channel.py:36:                    assert channel(signal, seed=seed, deaf=deaf) == _old_one_bit_channel(
tests/test_conversation_channel.py:37:                        signal, seed=seed, deaf=deaf
tests/test_conversation_channel.py:38:                    ), (seed, signal, deaf)
tests/test_conversation_channel.py:64:    def test_deaf_carries_no_symbol(self) -> None:
tests/test_conversation_channel.py:72:                if channel(symbol, seed=seed * 13 + 1, bits=3, deaf=True) == symbol:
src/anima_reborn/coupled.py:92:capacity grows with the units and Phi stops being computable past six, so a
src/anima_reborn/coupled.py:136:class Wiring(Enum):
src/anima_reborn/coupled.py:148:    PAIRS = "pairs"
src/anima_reborn/coupled.py:155:    the ring therefore cannot buy capacity — measured at 4, 6 and 8 units, all
src/anima_reborn/coupled.py:172:        if self is Wiring.PAIRS:
src/anima_reborn/coupled.py:187:        return self in (Wiring.RING, Wiring.PAIRS)
README.md:452:용량은 **배선의 순환 구조**에 있습니다. `units/2` 개의 2-순환이 최대이고, 그게 `Wiring.PAIRS`
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
"""The free 3-bit conversation engine and its honesty controls.

`Conversation` is the live, free-form counterpart to `DialogueSession`: a person and the
engine take turns, a convention forms in free play, and only a blind, learning-frozen audit
yields a verdict. These pin the load-bearing controls — the display aperture (a blind B
frame carries no answer), the corrected display-scramble null (a lawful reader collapses
under it while a latch-bypass reader trips `audit_failed`), and the k-of-3 rank — plus the
session mechanics the viewer depends on.
"""

from __future__ import annotations

from anima_reborn.conversation import BITS, Conversation
from anima_reborn.dialogue import channel


def _decode_shown(trace: list[list[float]]) -> int:
    """A lawful reader: decode the referent from the trace AS SHOWN (the display is its only
    access). Under a display-scramble this reads the permuted data and is wrong."""
    final = trace[-1]
    word = 0
    for j in range(BITS):
        bit = 0 if (final[2 * j] - final[2 * j + 1]) > 0 else 1
        word |= bit << j
    return word


def _run(reader, *, seed: int, free: int) -> dict:
    """Drive a session: an identity sender in A, `reader` in B, then request the audit."""
    session = Conversation(seed=seed)
    steps = 0
    spoke = 0
    while session.phase != "done" and steps < 6000:
        p = session._pending
        if p is None:
            break
        if p["mode"] == "choose":
            if session.phase == "free" and spoke < free:
                session.submit(p["nonce"], {"move": "speak" if spoke % 2 == 0 else "listen"})
                spoke += 1
            else:
                session.submit(p["nonce"], {"move": "audit"})
        elif p["mode"] == "compose_a":
            ref = p["show_referent"] if p["show_referent"] is not None else spoke % 8
            session.submit(p["nonce"], {"sig": ref, "ref": ref})  # identity send
        else:  # read_b
            session.submit(p["nonce"], {"act": reader(session, p)})
        session.step()
        steps += 1
    return session.describe()["report"]


def _honest(session, p):
    # The lawful reader sees only the display — the trace as shown (possibly scrambled).
    return _decode_shown(p["display"]["trace"])


def _bypass(session, p):
    # Reads the true latch directly from the pending, ignoring the display — a leak.
    pend = session._pending
    return channel(pend["signal"], seed=pend["channel_seed"], bits=BITS)


class TestLifecycle:
    def test_a_session_completes_with_a_verdict(self) -> None:
        report = _run(lambda s, p: 0, seed=1, free=4)
        assert report["verdict"] in {
            "two_way_session_evidence", "one_way_session_evidence",
            "no_session_evidence", "audit_failed", "no_audit",
        }
        for key in ("a", "b"):
            assert report[key]["k_of_3"] in (0, 1, 2, 3)
            assert len(report[key]["per_bit"]) == BITS

    def test_ending_without_the_audit_is_no_audit(self) -> None:
        session = Conversation(seed=1)
        # drive baseline blindly, then end at the first free choose
        while session._pending and session._pending["mode"] != "choose":
            session.submit(session._pending["nonce"], {"sig": 0, "act": 0})
            session.step()
        session.submit(session._pending["nonce"], {"move": "end"})
        session.step()
        assert session.describe()["report"]["verdict"] == "no_audit"


class TestTheDisplayScrambleNull:
    def test_a_lawful_reader_does_not_trip_the_audit(self) -> None:
        """Reading the shown trace collapses under the scramble, so the display null stays
        near chance — a genuine session is not falsely voided."""
        report = _run(_honest, seed=2, free=40)
        assert report["verdict"] != "audit_failed"
        assert report["b"]["nulls"]["dscramble"]["rate"] <= 0.375

    def test_a_bypass_reader_trips_the_audit(self) -> None:
        """Reading the true latch survives the scramble, so the display null stays high and
        the whole session is voided as audit_failed."""
        report = _run(_bypass, seed=2, free=40)
        assert report["verdict"] == "audit_failed"
        assert report["b"]["nulls"]["dscramble"]["rate"] > 0.375


class TestTheDisplayAperture:
    def test_no_blind_b_frame_carries_the_answer(self) -> None:
        forbidden = {"referent", "signal", "word", "act", "success", "ref", "arm"}
        session = Conversation(seed=3)
        seen = 0
        for _ in range(300):
            frame = session.describe()
            pend = frame.get("pending")
            if pend and pend["mode"] == "read_b" and pend.get("blind"):
                seen += 1
                assert set(pend) <= {"nonce", "mode", "trace", "markers", "blind"}, pend
                assert not (set(pend) & forbidden), pend
            if session._pending is not None:
                session.submit(session._pending["nonce"], {"sig": 0, "act": 0, "move": "audit"})
                session.step()
            if session.phase == "done":
                break
        assert seen > 0, "no blind direction-B frames were inspected"

    def test_a_dscramble_probe_actually_permutes(self) -> None:
        session = Conversation(seed=4)
        # push straight to the audit so dscramble arms appear
        while session.phase != "audit" and session._pending:
            mv = {"move": "audit"} if session._pending["mode"] == "choose" else {"sig": 0, "act": 0}
            session.submit(session._pending["nonce"], mv)
            session.step()
        swapped = [
            session._pending["markers_swapped"]
            for _ in _walk_audit(session)
            if session._pending and session._pending.get("arm") == "dscramble"
        ]
        assert any(swapped), "no dscramble probe reported a swap"


def _walk_audit(session):
    """Yield once per audit probe as it is resolved, exposing the pending arm."""
    while session.phase == "audit" and session._pending:
        yield session._pending
        session.submit(session._pending["nonce"], {"sig": 0, "act": 0})
        session.step()


class TestMechanics:
    def test_submission_is_idempotent(self) -> None:
        session = Conversation(seed=5)
        nonce = session._pending["nonce"]
        assert session.submit(nonce, {"sig": 0}) is True
        assert session.submit(nonce, {"sig": 1}) is False
        assert session.submit(9999, {"sig": 0}) is False
        before = len(session._probe_log)
        session.step()
        assert len(session._probe_log) == before + 1

    def test_a_step_with_nothing_pending_is_a_no_op(self) -> None:
        session = Conversation(seed=6)
        cursor = session._cursor
        session.step()
        assert session._cursor == cursor

    def test_the_report_is_handed_over_once(self) -> None:
        session = Conversation(seed=7)
        _run(lambda s, p: 0, seed=7, free=2)
        # drive the seed-7 instance itself
        s = Conversation(seed=7)
        while s.phase != "done" and s._pending:
            mv = ({"move": "audit"} if s._pending["mode"] == "choose"
                  else {"sig": 0, "act": 0})
            s.submit(s._pending["nonce"], mv)
            s.step()
        assert s.take_report() is not None
        assert s.take_report() is None

codex
## 1. Recommendation

The honest answer is: **real English conversation by this engine is impossible under the stated constraints.** Build interpretation 1 as a measured bottleneck demonstration, use interpretation 3 as its proof, and describe interpretation 4 as the only honest English-facing application.

The core certificate is:

\[
X_{\text{English}}\rightarrow C\in\{0,\ldots,7\}\rightarrow C'\rightarrow Y
\]

By the data-processing inequality:

\[
I(X;Y)\le I(C;C')\le H(C)\le \log_2 8=3\text{ bits}.
\]

Any decoder producing more detailed English is adding information from its author, corpus, rules, or human operator—not recovering it from the engine.

Interpretations:

1. **Measure the bottleneck — recommended.** Honest and stdlib-buildable. It answers the owner by testing the request and quantifying the failure. It does not make English conversation happen.
2. **Eight English labels — reject as the headline.** Labels may improve human usability, but add zero capacity. They are UI-authored code names and sharply increase overclaim risk.
3. **Prove impossibility — required conclusion.** The capacity theorem already proves the general result; the new experiment makes the wall visible on actual English strings.
4. **Human-to-human English relay — valid secondary feature.** The humans converse; the engine transports their three-bit code. This must be called a relay, never an English-speaking engine.

Dissent: if the owner primarily wants an English-speaking-human experience rather than an engine capability, I would implement interpretation 4 first—but retain exactly the same relay labeling and audit.

## 2. Concrete one-commit experiment

Call it an **English bottleneck audit**, not English conversation.

Reuse the measured PAIRS carrier in [dialogue.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/dialogue.py) and the capacity result in [capacity.py](/Users/mini/dancinlab/anima-reborn/state/communication/capacity.py).

### Fixed corpus

Embed a balanced corpus of 32 grammatical two-word commands:

- Eight compatible verbs, such as `move`, `clean`, `inspect`, `photograph`, `guard`, `find`, `mark`, `count`.
- Four objects: `box`, `chair`, `table`, `lamp`.
- Their Cartesian product gives 32 exact utterance choices.

This is deliberately tiny and closed. Unknown input is rejected as out-of-domain; it must never fall back to hashing, keywords, or a fabricated interpretation.

A single fixed phrase has no information by itself—the uncertainty belongs to the choice ensemble. For this uniform 32-choice task, the runnable certificate computes that zero-error identity transmission requires five latches, hence ten PAIRS units. Five pairs is structurally the required odd count, but Φ is no longer measurable there. It must print **“integration unmeasurable,” not “zero integration.”**

### Codec and flow

```text
English command X=(verb, object)
    → exact, human-authored codec E
    → C=verb index, three bits
    → existing six-unit PAIRS carrier
    → received C′
    → human-authored candidate renderer D
    → four possible commands sharing the decoded verb
```

The object is never encoded. The decoder must not invent one. It should output, for example:

> `move [object not transmitted]`  
> Possible originals: move box / move chair / move table / move lamp

The engine therefore narrows an English choice; it does not produce an English reply.

### Measurements

Use exact categorical entropy and mutual information, not the float-binning estimator in `info.py`.

For an exhaustive balanced schedule, repeated over independently drawn channel seeds, report:

- Source entropy \(H(X)\).
- Information entering the carrier: \(I(X;C)\).
- Carrier information: \(I(C;C')\), divided by \(H(C)\).
- End-to-end information: \(I(X;Y)\), divided by \(H(X)\).
- Verb-token information \(I(V;Y)\).
- Object-token information \(I(O;Y)\).
- Per-bit and joint carrier accuracy.
- Output support, output entropy, and \(2^{H(Y)}\) effective output categories beside every accuracy.
- Residual ambiguity \(H(X\mid Y)\) and candidate-set size.

All printed values come from that run; RESULTS must not be pre-filled with expected values.

### Required arms

- **Ideal carrier:** set \(C'=C\). This measures the codec/decoder ceiling before crediting the substrate.
- **Live PAIRS:** actual three-bit channel.
- **Deaf:** identical schedule and seeds, with the drive unreachable.
- **Balanced codebook scramble:** randomly partition the same 32 commands into eight equally occupied codes while keeping the carrier and decoder budget unchanged.
- **Label-permutation null:** permute displayed English glosses after decoding while keeping channel states fixed.

The important expected diagnostic—not a result to write before running—is that a scrambled codebook can retain substantial \(I(X;Y)\) merely by partitioning sentence identities while losing the predeclared verb relation. This proves why “three bits shared with English strings” is not automatically “three bits of English meaning.”

Use a fixed `seed=`, independent channel seeds, matched trial order, and label-permutation estimates to expose finite-sample MI floors.

`align.py` should not be involved. [align.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/align.py) can learn cross-modal co-occurrence, but it cannot create capacity or supply general English semantics. Any future use would require held-out phrases, its shuffled learner, untrained baseline, and effective rank.

## 3. Exact claim boundary

After running the experiment, the Korean UI and [RESULTS.md](/Users/mini/dancinlab/anima-reborn/state/communication/RESULTS.md) may say:

> 고정된 32개 2단어 명령 선택 과제에서 입력 문장 선택과 출력 후보 집합의 공유 정보는 `{I_XY}` / `{H_X}`비트(`{fraction}`)로 측정되었다. 기판에 들어간 `{H_C}`비트 중 `{I_CC}`비트(`{carrier_fraction}`)가 남았으며, deaf 귀무는 `{deaf}`, 균형 코드북 뒤섞기 귀무는 `{scramble}`였다. 출력 영어는 사람이 작성한 코덱의 표기이며, 엔진은 영어를 생성하거나 이해하지 않았다.

Short allowed English summary:

> English utterance choices passed through a measured three-bit bottleneck; only a predeclared token category was encoded.

It must not say:

> The engine understood the sentence and conversed in English, preserving about three bits of its meaning.

Nor may it say “three bits of your sentence survived” without specifying **sentence-choice identity or the exact annotated field**. Semantic similarity has not been measured.

## 4. Preventing human pattern-completion

- Never use chat bubbles labeled “engine says.”
- Label every string by provenance: `human input`, `human-authored codec gloss`, `human reconstruction`, or `carrier state`.
- Lead every report with surviving bits/fraction and ambiguity, not a transcript or accuracy.
- Keep the raw code `0–7` visible beside every English label.
- Show all indistinguishable candidate sentences; never silently choose a fluent completion.
- Keep English labels out of blind decisions. Reveal them only afterward or include a label-permutation arm.
- Test the viewer aperture as [Conversation](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/conversation.py) already does: the receiver payload must contain no source text, answer, referent, timing cue, or source-dependent candidate ordering.
- Treat free play as descriptive only. Evidence comes from a balanced, feedback-free, frozen audit.
- Name the tab `영어 병목` or `3비트 영어 릴레이`, never `영어 대화`.

Eight word labels buy only mnemonic usability. If desired, compare labels against neutral cards in a randomized human-interface study; the result would be about human error, not engine language.

## 5. Smallest honest first commit

The first commit should contain:

- A pure, no-I/O measurement module for the fixed corpus, codec, categorical MI, and report structure.
- `state/communication/english_bottleneck.py`, using the existing three-bit channel and printing all conditions, stages, ranks, and nulls.
- Tests pinning corpus balance, unknown-input rejection, seed reproducibility, maximum eight carrier symbols, the missing-object decoder, and the data-processing bound.
- A Korean RESULTS section populated only after running the script.

Do **not** add English labels to the current `대화` tab in this commit.

Defer:

- The two-browser human relay.
- Arbitrary free English, which must use explicit human self-encoding into three bits.
- Human reconstruction and blind forced-choice audits.
- Any learned encoder or `align.py` experiment.
- Any viewer-authored fluent response generator.

Those additions can make English-speaking humans interact through the engine. None can upgrade the engine into an English speaker.
tokens used
52,390
## 1. Recommendation

The honest answer is: **real English conversation by this engine is impossible under the stated constraints.** Build interpretation 1 as a measured bottleneck demonstration, use interpretation 3 as its proof, and describe interpretation 4 as the only honest English-facing application.

The core certificate is:

\[
X_{\text{English}}\rightarrow C\in\{0,\ldots,7\}\rightarrow C'\rightarrow Y
\]

By the data-processing inequality:

\[
I(X;Y)\le I(C;C')\le H(C)\le \log_2 8=3\text{ bits}.
\]

Any decoder producing more detailed English is adding information from its author, corpus, rules, or human operator—not recovering it from the engine.

Interpretations:

1. **Measure the bottleneck — recommended.** Honest and stdlib-buildable. It answers the owner by testing the request and quantifying the failure. It does not make English conversation happen.
2. **Eight English labels — reject as the headline.** Labels may improve human usability, but add zero capacity. They are UI-authored code names and sharply increase overclaim risk.
3. **Prove impossibility — required conclusion.** The capacity theorem already proves the general result; the new experiment makes the wall visible on actual English strings.
4. **Human-to-human English relay — valid secondary feature.** The humans converse; the engine transports their three-bit code. This must be called a relay, never an English-speaking engine.

Dissent: if the owner primarily wants an English-speaking-human experience rather than an engine capability, I would implement interpretation 4 first—but retain exactly the same relay labeling and audit.

## 2. Concrete one-commit experiment

Call it an **English bottleneck audit**, not English conversation.

Reuse the measured PAIRS carrier in [dialogue.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/dialogue.py) and the capacity result in [capacity.py](/Users/mini/dancinlab/anima-reborn/state/communication/capacity.py).

### Fixed corpus

Embed a balanced corpus of 32 grammatical two-word commands:

- Eight compatible verbs, such as `move`, `clean`, `inspect`, `photograph`, `guard`, `find`, `mark`, `count`.
- Four objects: `box`, `chair`, `table`, `lamp`.
- Their Cartesian product gives 32 exact utterance choices.

This is deliberately tiny and closed. Unknown input is rejected as out-of-domain; it must never fall back to hashing, keywords, or a fabricated interpretation.

A single fixed phrase has no information by itself—the uncertainty belongs to the choice ensemble. For this uniform 32-choice task, the runnable certificate computes that zero-error identity transmission requires five latches, hence ten PAIRS units. Five pairs is structurally the required odd count, but Φ is no longer measurable there. It must print **“integration unmeasurable,” not “zero integration.”**

### Codec and flow

```text
English command X=(verb, object)
    → exact, human-authored codec E
    → C=verb index, three bits
    → existing six-unit PAIRS carrier
    → received C′
    → human-authored candidate renderer D
    → four possible commands sharing the decoded verb
```

The object is never encoded. The decoder must not invent one. It should output, for example:

> `move [object not transmitted]`  
> Possible originals: move box / move chair / move table / move lamp

The engine therefore narrows an English choice; it does not produce an English reply.

### Measurements

Use exact categorical entropy and mutual information, not the float-binning estimator in `info.py`.

For an exhaustive balanced schedule, repeated over independently drawn channel seeds, report:

- Source entropy \(H(X)\).
- Information entering the carrier: \(I(X;C)\).
- Carrier information: \(I(C;C')\), divided by \(H(C)\).
- End-to-end information: \(I(X;Y)\), divided by \(H(X)\).
- Verb-token information \(I(V;Y)\).
- Object-token information \(I(O;Y)\).
- Per-bit and joint carrier accuracy.
- Output support, output entropy, and \(2^{H(Y)}\) effective output categories beside every accuracy.
- Residual ambiguity \(H(X\mid Y)\) and candidate-set size.

All printed values come from that run; RESULTS must not be pre-filled with expected values.

### Required arms

- **Ideal carrier:** set \(C'=C\). This measures the codec/decoder ceiling before crediting the substrate.
- **Live PAIRS:** actual three-bit channel.
- **Deaf:** identical schedule and seeds, with the drive unreachable.
- **Balanced codebook scramble:** randomly partition the same 32 commands into eight equally occupied codes while keeping the carrier and decoder budget unchanged.
- **Label-permutation null:** permute displayed English glosses after decoding while keeping channel states fixed.

The important expected diagnostic—not a result to write before running—is that a scrambled codebook can retain substantial \(I(X;Y)\) merely by partitioning sentence identities while losing the predeclared verb relation. This proves why “three bits shared with English strings” is not automatically “three bits of English meaning.”

Use a fixed `seed=`, independent channel seeds, matched trial order, and label-permutation estimates to expose finite-sample MI floors.

`align.py` should not be involved. [align.py](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/align.py) can learn cross-modal co-occurrence, but it cannot create capacity or supply general English semantics. Any future use would require held-out phrases, its shuffled learner, untrained baseline, and effective rank.

## 3. Exact claim boundary

After running the experiment, the Korean UI and [RESULTS.md](/Users/mini/dancinlab/anima-reborn/state/communication/RESULTS.md) may say:

> 고정된 32개 2단어 명령 선택 과제에서 입력 문장 선택과 출력 후보 집합의 공유 정보는 `{I_XY}` / `{H_X}`비트(`{fraction}`)로 측정되었다. 기판에 들어간 `{H_C}`비트 중 `{I_CC}`비트(`{carrier_fraction}`)가 남았으며, deaf 귀무는 `{deaf}`, 균형 코드북 뒤섞기 귀무는 `{scramble}`였다. 출력 영어는 사람이 작성한 코덱의 표기이며, 엔진은 영어를 생성하거나 이해하지 않았다.

Short allowed English summary:

> English utterance choices passed through a measured three-bit bottleneck; only a predeclared token category was encoded.

It must not say:

> The engine understood the sentence and conversed in English, preserving about three bits of its meaning.

Nor may it say “three bits of your sentence survived” without specifying **sentence-choice identity or the exact annotated field**. Semantic similarity has not been measured.

## 4. Preventing human pattern-completion

- Never use chat bubbles labeled “engine says.”
- Label every string by provenance: `human input`, `human-authored codec gloss`, `human reconstruction`, or `carrier state`.
- Lead every report with surviving bits/fraction and ambiguity, not a transcript or accuracy.
- Keep the raw code `0–7` visible beside every English label.
- Show all indistinguishable candidate sentences; never silently choose a fluent completion.
- Keep English labels out of blind decisions. Reveal them only afterward or include a label-permutation arm.
- Test the viewer aperture as [Conversation](/Users/mini/dancinlab/anima-reborn/src/anima_reborn/conversation.py) already does: the receiver payload must contain no source text, answer, referent, timing cue, or source-dependent candidate ordering.
- Treat free play as descriptive only. Evidence comes from a balanced, feedback-free, frozen audit.
- Name the tab `영어 병목` or `3비트 영어 릴레이`, never `영어 대화`.

Eight word labels buy only mnemonic usability. If desired, compare labels against neutral cards in a randomized human-interface study; the result would be about human error, not engine language.

## 5. Smallest honest first commit

The first commit should contain:

- A pure, no-I/O measurement module for the fixed corpus, codec, categorical MI, and report structure.
- `state/communication/english_bottleneck.py`, using the existing three-bit channel and printing all conditions, stages, ranks, and nulls.
- Tests pinning corpus balance, unknown-input rejection, seed reproducibility, maximum eight carrier symbols, the missing-object decoder, and the data-processing bound.
- A Korean RESULTS section populated only after running the script.

Do **not** add English labels to the current `대화` tab in this commit.

Defer:

- The two-browser human relay.
- Arbitrary free English, which must use explicit human self-encoding into three bits.
- Human reconstruction and blind forced-choice audits.
- Any learned encoder or `align.py` experiment.
- Any viewer-authored fluent response generator.

Those additions can make English-speaking humans interact through the engine. None can upgrade the engine into an English speaker.
