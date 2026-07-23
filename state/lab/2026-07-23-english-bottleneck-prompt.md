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
