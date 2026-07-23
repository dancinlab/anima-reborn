# Design task: is a DEPTH-PRESERVING hold possible? Measure the retention ↔ analog-depth trade-off

Part 4 (conditional composition) just PRUNED: a context gate on `sequence.py`'s held state is
indistinguishable from a planted XOR lookup, because the clean bistable hold (`retention.py` =
1.000 flat through 480 ticks) SATURATES away the sub-word analog depth a genuinely dynamical
context gate would need. The held |delta| is always past the barrier (0.79..1.39), so the response
reads only the SIGN (the word), never depth. Verdict in `state/communication/RESULTS.md`:
"clean-holding memory and a raw-state-mediated context gate cannot coexist on this latch."

That is a hypothesis, not a proven wall. The honest next step, in this repo's style (the early
integration↔representation λ-sweep), is to MEASURE the trade-off: is there ANY hold regime that
keeps enough analog depth for context AND stays stable enough to be memory — or is the trade
strict? Design that measurement. Return a concrete, runnable design + the nulls. Do NOT write full
code.

## What exists (read it)

- `src/anima_reborn/coupled.py`: `CoupledEngine`, `Wiring.PAIRS` (units/2 latches), `chain`,
  `Rhythm` (ALTERNATING listen/integrate vs FIXED = coupling 1.0 autonomous hold), per-unit `drive`,
  `GAIN`, `AMPLITUDE`, `WALK` noise. The hold today = drive a symbol (TELL, ALTERNATING), then
  FIXED + drive 0 for HOLD → a saturated bistable latch.
- `state/communication/retention.py`: the deaf hold keeps all 3 bits flat to 480 ticks; leak
  (coupling 0) and feedforward die — recurrence buys the hold, and it is a self-correcting BASIN
  with a finite barrier (`_perturbation_hold`).
- `state/communication/context_composition.py`: the pruning — the response follows sign not depth,
  I(R; depth | current, past-word) at floor at every drive scale.
- The early wall (`RESULTS.md` top, `alternating_coupling.py`): integration and representation
  trade off monotonically; a rhythm (ALTERNATING) moved the exchange ratio but did not break it.

## The candidate axes to evaluate (address each, then recommend what to measure first)

A. **Weaker / partial coupling hold.** A hold at coupling < 1.0 (or a low-coupling Rhythm) may not
   fully saturate — the held value could keep analog depth proportional to the input — but may also
   decay or lose the bit. Sweep the hold coupling and measure BOTH retention (does the sign survive
   silence) AND depth-preservation (does the held |delta| still carry the input's analog magnitude,
   e.g. mutual information between input drive strength and held |delta|).
B. **Leaky-integrator hold.** A hold that relaxes toward its input rather than a basin (like the
   `words.py` continuing-drive or a slow decay) keeps analog depth but forgets — the opposite
   corner. Is there a middle?
C. **Read depth from the TRAJECTORY, not the endpoint.** The pruning read the final held state.
   Maybe the analog depth lives in HOW FAST the pair settled (settling time / overshoot), which a
   sign-only lookup cannot see even if the endpoint saturates. Does I(R or a probe ; settling-time |
   sign) exceed floor? This would rescue context without changing the hold at all.
D. **A second, non-latching analog register** carried alongside the clean latch (the latch holds the
   bit for memory, a separate leaky unit holds the depth for context). Two registers, one each for
   the two things that cannot coexist in one.

## What I need — answer each explicitly

1. **The trade-off measurement.** The single cleanest experiment: what parameter is swept (hold
   coupling? rhythm? a leak rate?), and the TWO quantities plotted against it — retention
   (sign-survival through silence, vs its walk/feedforward null) and depth-preservation (mutual
   information between the input's analog magnitude and the held analog depth, vs a shuffled null).
   The shape of the two curves against the swept parameter IS the deliverable — a crossing window,
   or a strict anticorrelation (the wall, quantified).
2. **Whether C (trajectory depth) rescues context cheaply** — is settling-time / transient a real
   sub-word channel a lookup cannot fake, measurable now without changing the hold? If yes, that may
   be the smallest win; specify the measurement and its null.
3. **The nulls.** For each quantity: retention needs its walk/feedforward null; depth-preservation
   needs a shuffled-input null and must be scored on HELD-OUT input magnitudes (not the ones used to
   define the buckets); the trajectory channel needs a control that the endpoint sign alone does not
   already carry it.
4. **The honest verdict + ceiling.** If a window exists, the claim is only "there is a hold regime
   that keeps analog depth D while retaining the bit at fidelity F" — a trade-off point, NOT
   "context works" (that still needs the full gate audit re-run in the window). If the trade is
   strict, the claim is "the retention↔depth wall is real, here is the measured anticorrelation."
   Where is the line, and what must NOT be said.
5. **Phased first commit.** The smallest pure-`state/` measurement (a sibling script) that plots the
   trade-off + the trajectory-channel check, filling RESULTS from the run — matching how every part
   here landed. What is deferred (re-running the context gate in a found window; any `src/` change).

Keep the discipline: never a number that was not measured; every quantity with the null that could
fake it; score depth-preservation on held-out magnitudes; report effective width beside any depth
channel; if both A–D dead-end by measurement, say so and record the wall with numbers — a strict
retention↔depth anticorrelation is itself a real, honest result. The engine is not language; the
most this frontier can buy is re-opening CONTEXT (current depends on held past), nothing more.
