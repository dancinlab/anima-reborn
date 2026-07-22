# lab full — 단어 실험 설계 · fable

질문: "A G 에 각각 단어들을 넣고 창발이 일어나는지 볼까"
지시문: `state/lab/2026-07-22-words-prompt.md`
구현 결과: `src/anima_reborn/words.py` (순환이동 귀무값·전달아닌생성 지적을 채택)

---

Everything is measured. Here is the assessment.

---

# Yes — there is a version whose result is not determined by the encoding, and it survived measurement

The honest experiment is: **words are a continuing drive (never an initial condition), and the reported number is never absolute MI — it is aligned MI minus a circular-shift surrogate null**, with the null computed on the *same run, same encoding, same cadence, same substrate*. The encoding determines the magnitude of what goes in; it cannot determine whether the number survives a time shift, because the shift preserves everything the encoding produced and destroys only temporal alignment. That, plus two substrate-owned findings (a cadence passband at the substrate's own memory constant, and a provable-and-measured inability to create binding), is the experiment worth building.

The direct answer to the owner's question ("A와 G에 각각 단어들을 넣고 창발이 일어나는지"): **emergence is transmitted, never created.** If the two word streams are unrelated — which is what "각각" naturally means — measured binding is zero (−0.038…+0.085 bits over 8 seeds, indistinguishable from the null). If the streams share word alignment, binding appears, scales with the shared fraction, and clears every bar. The substrate's role is a filter with a measurable passband, not a binder.

Prototype scripts (stdlib-only, importing the repo's own `info.py` estimator and exact drift constants) are at `/tmp/word-emergence/` (`wordlib.py`, `run3.py`); every number below reproduces from seeds 0–7 with word-stream RNG `Random(1000+seed)` over a fixed 32-word vocabulary.

## 1. The substrate does not retain an initial condition — measured, and it settles the design

The drift law is linear, so a perturbation's decay is deterministic (noise cancels between twin trajectories):

| | half-life | e-fold | equilibrium noise std |
|---|---:|---:|---:|
| driven dims 0–1 (`PULL=0.06`) | **12 ticks** | 17 | 0.033 |
| damped dims 2–7 (`DAMPING=0.985`) | 46 ticks | 67 | 0.069 |

A typical word component (0.39 = `SEP·1.3·0.5`) sinks below the observation-noise std (0.116) in **20 ticks** and below the walk floor in **40** — both before `MIN_SAMPLES_FOR_METRICS = 50` even lets a first MI reading exist. So "seed A and G with word vectors" is answered before it is asked: the word is gone before the first measurement. Words must arrive as a drive — each engine's dim-0/1 targets are the current word's encoded levels, held for `HOLD` ticks, replacing the rotating target entirely (no shared target, no antiphase: the only path between the streams is the word streams themselves).

## 2. The falsifiable claim — one survivor, three kills

**Survivor: "a word stream drives each engine; binding = aligned MI − shift null."** Your suspicion that this reduces to "correlated inputs give correlated outputs" is correct *for absolute MI* — and it is worse than trivial, because at the house window it is false in the dangerous direction: at hold=32, window=200, two **independent** word streams read median **0.302 bits absolute MI** — the emergence bar itself. Held words make the window's effective sample size ~6 blocks, not 200, and the plug-in estimator's bias explodes far past the known 0.155 iid floor. Any naive port of the pipeline's readout would print `창발` for unrelated words. But the substrate adds three non-trivial, encoding-independent things:

- **A passband.** Binding vs hold (same stream, window=1000, medians): 0.056 (hold=1) → 0.236 (4) → 0.467 (8) → 0.713 (16) → 0.927 (32) → 0.860 (64). Half-saturation sits at hold 8–16, bracketing the driven dims' measured memory (half-life 12, e-fold 17). The knee's position is a property of `PULL`, not of the hash.
- **A no-creation guarantee.** A and G never read each other (true in every engine in this repo — the gap is not a coupling), so with independent inputs the streams are independent by construction. Measured: binding for independent streams −0.038/+0.013/+0.085, for shuffled streams −0.092/−0.024/+0.032.
- **Attenuation.** ~1.6–2.3 bits go in (mi_in), at most ~1.05 come out — and the plug-in estimate of mi_out *exceeded* mi_in by up to +0.101 bits in 192 runs (shared relaxation ramps carry time structure the per-tick input pairs don't), so a `mi_out ≤ mi_in` assertion must **not** be written; the estimator is not DPI-safe on autocorrelated windows. Document it; don't test it.

**Killed: related-vs-unrelated word pairs.** No stdlib encoding carries meaning. Character/edit-distance encodings carry *form*, and any "related" geometry would be my construction — the contrast would measure the encoder, with the substrate as a bystander that transmits whatever geometry it is fed. Not answerable in this repo; saying so is the result.

**Killed: Φ of the word-driven substrate.** Architecture decides it: every dim's update reads only itself plus its exogenous target, so the TPM factorizes and true Φ = 0 in every state, words or no words. Measured on units (a0, a1, g0, g1), fixed words cat/dog: **Φ = 0.000 exactly** at binarize stand-in ±0.4 (dynamics can't cross the threshold in one tick — the units are frozen at the substrate's timescale), and ≤ 0.056 non-monotone sampling artefact at ±0.05, far under `substrate.py`'s known 0.3 artefact floor at 400 trials.

**The crux control (2d):** the circular time-shift surrogate — `MI(L, rotate(R, Δ))`, Δ ∈ {37, 83, 127}, median — IS the control that separates "the substrate bound them" from "the encoding contained the binding," because it keeps the encoding's entire contribution (marginals, block structure, autocorrelation, estimator bias) and removes only alignment. Reporting `mi_in` alongside handles the remaining honesty: the claim is never creation, only transmission.

## 3. Encoding: blake2b → two levels in (−1, 1)

`enc(word) = blake2b(word, digest_size=16)` → bytes 0–8 and 8–16 each mapped to (−1, 1); dim 0 gets `SEP·1.3·e₀`, dim 1 gets `SEP·1.0·e₁` (house amplitudes). Why: stdlib, deterministic across processes (`hash()` is salted — unusable), any word admissible, no vocabulary file. **What it supports:** word *identity* only — same word, same level; different words, independent levels. **What it cannot support:** any claim about meaning or relatedness. Also state plainly: the house sampler observes dim 0 only, so the channel is effectively scalar — an 8-dim "word embedding" here would be theater, which is why the encoding is honest about being two levels.

## 4. API and placement

I see `words.py` is already registered in `src/anima_reborn/CLAUDE.md` ("words as a continuing drive, always paired with a null control") — this design matches that row.

- `src/anima_reborn/words.py`: `WordField` (top-level class with `step`/`reset`, so `TestEngineViewerLockstep` detects it structurally), `WordState` (frozen, slotted), `encode_word()`. Constructor: `WordField(words_a, words_b, *, hold=HOLD, dim=8, history=WINDOW, seed=None, binning=None)` — two word sequences in, cycled; correlation/shuffle conditions are constructed by the *caller* (tests, viewer handler), keeping the engine pure. `step() -> WordState`, `run(n)`, `state` property that reads without advancing, `reset()` re-randomizes vectors and clears windows but keeps the streams.
- Constants with measured provenance in docstrings: `HOLD = 32` (past the passband knee at 8–16), `WINDOW = 1000` (where the independent-stream artefact dies: median absolute MI 0.302 at the house 200 → 0.121 at 1000), `SHIFTS = (37, 83, 127)` (coprime to HOLD, beyond the 17-tick memory).
- `WordState` carries the **triple** — `mi` (aligned), `null`, `binding` — plus `tension`, current `word_a`/`word_b`, and `verdict = Emergence.classify(mi)`, legitimate only because WINDOW=1000 puts the bar inside the measured gap (indep max 0.209 < 0.30 < 0.952 same min); the docstring says so and the tests pin both edges. No fused "boundness" scalar, per the house rule.
- Viewer, same commit: handler with `configure`/`describe` (describe reads, never steps), `_HANDLERS` + `Viewer.__init__` + `TICK_RATES` (30 Hz, like `base`), and in `page.html` a tab, panel, `PREFIX` entry, `renderWords()`, Korean UI via `ko()`. Controls as sliders: `정합도` p ∈ [0,1] (handler builds stream B = stream A with prob p, else fresh draw — p=1 is same, p=0 is independent) and `유지 틱` for hold. Restart the viewer after landing.

## 5. Tests that can fail, with the numbers behind them

All at hold=32, ticks=6000, window=1000, seeds 0–7 unless noted; asserted bounds leave ~2× slack against the measured extremes:

- **Washout** — twin-gap decay `(1−PULL)^t`: half-life exactly 12 ticks; a seeded word vector is at the noise floor before the 50-sample metrics gate opens (this test is the reason words are a drive).
- **Same stream binds** — binding > 0.5 on every seed (measured min **+0.742**, ~8× the worst null-side excursion 0.09, ~5× the iid floor).
- **No creation** — independent streams: |binding| < 0.2 every seed (measured −0.038…+0.085) and aligned MI < 0.30 every seed (measured max 0.209 — never EMERGENT). Shuffled partner: same bound (measured −0.092…+0.032).
- **Dose-response** — median binding monotone over p ∈ {0, .25, .5, .75, 1}: measured 0.013 < 0.075 < 0.149 < 0.482 < 0.927 (medians only — per-seed ranges overlap zero at p ≤ 0.5, same reason the house coupling test uses means).
- **Passband** — median binding(hold=1) < 0.1 (measured 0.056) and binding(hold=32) > 3× binding(hold=4) (measured 0.927 vs 0.236); knee bracketed at the substrate's measured e-fold.
- **The artefact pin** (artefact-honesty): at the house window 200, *independent* word streams read median absolute MI ≥ 0.25 (measured 0.302 — bar-level), collapsing to ≤ 0.15 at window 1000 (measured 0.121). This is the test that makes it impossible to ever quote absolute MI for held words at the house window.
- **Φ is architecture** — stand-in ±0.4: `phi == 0.0` exactly; ±0.05: artefact < 0.1 at 400 trials (measured ≤ 0.056).

## 6. What is and is not answerable

Answerable, and now measured: whether two word streams bind *through this substrate*, at what cadence the substrate can carry them, what it costs (attenuation), and that the substrate never invents binding. Not answerable, and should be said in the docs in exactly these words: anything about the words' **meaning** (needs semantics no stdlib encoder has — any related/unrelated result would be a property of my encoder); absolute MI at the house window (bar-level artefact); Φ (zero by architecture — A and G have never read each other in any engine here, and words don't change that). One unmeasured observation worth flagging as expectation only: with word drives, dim-0 tension becomes `enc(w_A) − enc(w_G)` — identical words collapse the field toward `quiet`, disagreement is tension — a nice viewer narrative, but I did not measure the mood distribution and it should not be claimed until someone does.
