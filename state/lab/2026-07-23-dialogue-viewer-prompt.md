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
