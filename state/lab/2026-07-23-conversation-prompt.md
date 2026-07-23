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
