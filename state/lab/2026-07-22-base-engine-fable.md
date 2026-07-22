# lab full — 기본 엔진 설계 · fable

질문: "자 이제 여기 있는것들을 이용해 기본엔진을 만들어봐"
지시문: `state/lab/2026-07-22-base-engine-prompt.md`
구현 결과: `src/anima_reborn/base.py` (수치가 소수점까지 재현됨)

---

All measurements are in and they settle every open question in the design. Here it is, grounded in the code and in runs of a prototype against the actual package (scripts left at `/tmp/base_proto.py` and `/tmp/melt_proto.py` if you want to rerun them — they use the repo's own venv).

---

# The base engine: `base.py` — the four engines under one clock, and the clock is the crystal

## 0. What I measured first (so the design is evidence, not taste)

I prototyped four candidate couplings and swept `epsilon` × 8 seeds × 800 ticks, measuring end-of-run MI (window 200), tension, locked-tick fraction, and accumulated phase:

| coupling | eps=0.02 | eps=0.05 | eps=0.10 | eps=0.20 | eps=0.50 | verdict on the coupling |
|---|---|---|---|---|---|---|
| **gate** (phase advances only while `CrystalVerdict.LOCKED`) | MI **1.35** (min 1.26) | 0.50 (min 0.01) | **0.005** | 0.004 | 0.004 | sharp, seed-stable transition |
| beat (±`PHASE_RATE` per sign-alternation of m) | 1.40 | 0.97 | 1.29 | 0.99 | 0.07 | leaks rotation far past melt; **non-monotone** |
| clutch (rate × max(0, −ac1)) | 1.41 | 1.12 | 1.35 | 1.20 | 0.02 | same leak, worse |
| free-running (= pipeline) | 1.21 | 1.21 | 1.21 | 1.21 | 1.21 | control: binding never depended on the crystal |

Tension under the gate: **0.176 locked vs 0.184 melted** — the gap does not care whether the crystal is alive. Mid-run melt (eps 0.02→0.5 at tick 800): MI 1.40 → 0.01 within ~400 ticks. Refreeze (→0.02): MI back above 0.85–1.4 within ~800 ticks, all seeds. All deterministic under seed.

---

## 1. The thesis, one sentence

**Shared information downstream is paid for in temporal order upstream: the two sampled streams hold emergent MI exactly while the crystal's period-2 lock animates the separation between A and G — melt the crystal and the gap survives (tension ≈ 0.18 on both sides) but the information in it dies (MI 1.35 → 0.005 bits); refreeze it and the information returns.**

No single engine makes this claim. Emergence says coupling→MI, with a free sine as clock. Crystal says a lock exists, and nothing consumes it. Repulsion says the gap carries channels, with a free tick-clock rotating its target. Pipeline says *"separation is what produces shared information"* (its own docstring, `pipeline.py:12`) — and the base engine measurably **corrects** that claim: under a melted crystal, separation persists at pipeline-typical levels while MI sits at `INDEPENDENT`. It is not the gap that binds the streams; it is the *motion* of the gap, and the motion is bought entirely by the lock. That is the unification: crystal supplies temporal order, repulsion converts it into a moving gap, the pipeline's sampling turns the gap into two streams, and emergence's estimator reads the binding out.

## 2. The composition

One feed-forward chain, one new mechanism (an *accumulated* phase), zero new constants:

```
TimeCrystal.step() ──verdict──▶ gate ──▶ phase += PHASE_RATE if LOCKED else 0
                                              │
                              repulsion-law drift of A, G toward
                              ±(separation·1.3·sin φ, separation·1.0·cos φ)   [dims 0–1; rest decay]
                                              │
                              sample L = a[0]+noise, R = g[0]+noise            [pipeline law]
                                              │
                              info.py: H(L), H(R), H(L,R), MI, Emergence verdict
```

The single structural change versus the existing engines: everywhere else, `phase = tick * PHASE_RATE` — the rotation is a gift from the tick counter. In the base engine phase is a **state variable that only the crystal's lock can advance**. The tick counter no longer appears in the drive.

Why this wiring and not the alternatives you listed:

- **Crystal → phase, chosen, as a verdict gate.** The gate uses `CrystalVerdict.classify`'s existing pinned thresholds (`ac1 < −0.85 ∧ ac2 > 0.80`, origin constants in `crystal.py:94-98`) — no new numbers. Measured consequence: chaos means *exactly* zero rotation, so the melted regime is a frozen target; A and G hover at static ±target, tension stays ~0.18, and the streams' only variation is independent noise → MI at `INDEPENDENT`. Sharp, monotone-in-the-mean, seed-stable.
- **Crystal as beat-oscillator (the "purer" version), measured and rejected.** Advancing phase per sign-alternation of magnetization keeps the tick counter fully out, but the measurement kills it: residual anti-correlation in the *melted* ring (ac1 ≈ −0.13 in chaos) still rotates the target at roughly half speed, so MI stays emergent at eps 0.10–0.20 where the verdict says chaos, and the dose-response is non-monotone (0.55 at eps 0.15, 0.99 at 0.20) with seed spread too wide to write a test against. The honest reading: sub-verdict temporal order *also* binds — true, interesting, and untestable at this window size. The gate buys falsifiability by quantizing "order" at the crystal's own pinned thresholds.
- **Repulsion tension → emergence coupling, rejected.** `EmergenceEngine(coupling=f(tension))` restates emergence's own coupling→MI claim through a fabricated mapping `f`; it adds a knob and no new falsifiable content. The control row proves the deeper problem: MI rides on *rotation*, not tension level — tension was ~0.18–0.25 in every row of the table while MI ranged 0.004–1.41.
- **MI fed back into the drive, refused — see §4.**
- **State machine with four lanes, refused** — that is a scheduler, not a claim.

Why the existing classes `Pipeline` and `EmergenceEngine` are *not* embedded: each hard-codes its own free clock (`tick * PHASE_RATE` at `pipeline.py:138`, `sin(0.1·t)` at `emergence.py:111`), which is precisely the thing the base engine abolishes. Instead the base engine follows the house's own composition precedent — `pipeline.py` imports `PHASE_RATE`/`PULL`/`DAMPING` from `repulsion.py` rather than embedding `RepulsionField` — and does the same, additionally importing `WALK`, `OBSERVATION_NOISE`, `MIN_SAMPLES_FOR_METRICS` from `pipeline.py`. Emergence participates as its measurement half (`info.py`, which *is* `EmergenceEngine.metrics`) plus its mechanism (two streams = private noise + one shared source), with the crystal-driven target replacing the free sine as the shared source. `TimeCrystal` is embedded as a real instance — it is the one engine whose internal dynamics the base engine needs, not just its law.

Limiting case worth knowing: at `epsilon=0` the drive never misses, the gate is open ~permanently, and the base engine degenerates to the pipeline (measured: 1.35 vs 1.21 bits — the small difference is the ac-history warm-up before the gate first opens). The base engine is a strict generalization of the pipeline with the clock made mortal.

## 3. State object and public API

```python
# src/anima_reborn/base.py
"""Base engine — the four engines composed under one clock, which is the crystal's."""

from .crystal import CrystalState, CrystalVerdict, TimeCrystal
from .info import Binning, Emergence, entropy, joint_entropy
from .pipeline import MIN_SAMPLES_FOR_METRICS, OBSERVATION_NOISE, WALK
from .repulsion import DAMPING, PHASE_RATE, PULL

DIM = 8            # as pipeline.py — structure lives in the leading dims
HISTORY = 200      # as pipeline.py — rolling observation window
SEPARATION = 0.60  # as repulsion.py / pipeline.py

EPSILON = 0.02
"""Default drive imperfection. Deliberately NOT the crystal's own 0.05: measured
over seeds 0-7 x 800 ticks, 0.05 sits on the verdict-flicker boundary (locked
28.6% of ticks, end-of-run MI ranging 0.01-1.39 by seed alone), while 0.02 locks
94% of ticks and always binds (MI >= 1.26). 0.02 is the value test_crystal pins
as LOCKED."""


@dataclass(frozen=True, slots=True)
class BaseState:
    crystal: CrystalState        # the substrate's clock, verbatim (nested frozen dataclass)
    tension: float               # mean squared A-G gap, >= 0; survives a melt (~0.18)
    phase: float                 # accumulated target rotation, radians, >= 0;
                                 #   advances by PHASE_RATE only on LOCKED ticks
    h_left: float                # bits, [0, log2(12)]
    h_right: float               # bits, [0, log2(12)]
    h_joint: float               # bits, [0, log2(144)]
    mutual_information: float    # bits, >= 0 (plug-in estimator — see info.py caveat)
    verdict: Emergence           # the binding readout

    def __str__(self) -> str:
        return (
            f"[{self.crystal.verdict.value}] phase={self.phase:.2f} "
            f"tension={self.tension:.3f} MI={self.mutual_information:.3f} "
            f"[{self.verdict.value}]"
        )


class BaseEngine:
    def __init__(
        self,
        *,
        epsilon: float = EPSILON,        # live control, [0, 1] — validated by TimeCrystal
        separation: float = SEPARATION,  # live control, unvalidated (as pipeline)
        dim: int = DIM,                  # >= 2
        history: int = HISTORY,          # >= 1
        seed: int | None = None,
        binning: Binning | None = None,  # default Binning(bins=12, vrange=1.6), as pipeline
    ) -> None: ...

    # controls — settable mid-run (the viewer's sliders)
    epsilon: float      # property delegating to the embedded crystal's validated setter
    separation: float

    # readouts — read, never advance (viewer/CLAUDE.md rule)
    a: tuple[float, ...]
    g: tuple[float, ...]
    left: tuple[float, ...]      # observation window, oldest first
    right: tuple[float, ...]
    ticks: int
    tension: float
    phase: float
    state: BaseState             # zeros + INDEPENDENT until 50 samples, as PipelineState

    def step(self) -> BaseState: ...
    def run(self, ticks: int) -> BaseState: ...   # ticks >= 1, as pipeline/crystal
    def reset(self) -> None: ...                  # crystal.reset(), re-randomize A/G,
                                                  # clear windows, phase = 0.0, tick = 0
```

Decidable details worth pinning in the docstrings:

- **Tick order:** `crystal.step()` → read the *freshly returned* verdict → `phase += PHASE_RATE if LOCKED else 0.0` → drift A/G toward ±targets at the new phase (pipeline's exact loop, `phase` substituted for `tick * PHASE_RATE`) → append `a[0] + U(±OBSERVATION_NOISE/2)` and the G counterpart → return `state`.
- **Seeding:** `master = random.Random(seed)`; the crystal gets `master.getrandbits(64)`, the field/observation RNG gets a second `getrandbits(64)`. Two derived streams, not one shared one, so a change to the crystal's internal draw count (e.g. `size`) cannot silently reshuffle the field's noise. `seed=None` stays honest: the master is system-seeded, children follow.
- **The crystal instance is not exposed.** `epsilon` is a delegating property; the crystal's reading arrives frozen inside `BaseState.crystal`. Exposing the live instance would let a caller step it out of band and desynchronize the one clock the engine has.
- **No clock parameter.** The base engine never touches `RepulsionField`'s circadian machinery, so unlike `repulsion.py` it needs no injectable `clock` — it is deterministic under `seed=` with no further arguments.

Viewer: a fifth tab per `viewer/CLAUDE.md`'s four-step checklist — controls `epsilon` and `separation`, plot the magnetization history, both streams, and the MI trace; `describe` reads `state` only.

## 4. What the base engine must NOT do

- **No MI→drive feedback loop.** This is the seductive one ("does it converge, oscillate, run away?") and it is unfalsifiable with this estimator. At the default window the plug-in MI never reads below ~0.155 bits for full-range streams, so a loop feeding MI into `separation` or `epsilon` self-excites on estimator bias — its fixed point is a property of the artefact, not the dynamics. And there is no clean correction: I measured that the floor is *configuration-dependent* (frozen, low-entropy streams read 0.005, not 0.155), so no constant can be honestly subtracted. Any convergence claim would be a claim about the histogram.
- **No aggregate "aliveness" scalar.** The state carries `CrystalVerdict` and `Emergence` separately; any `f(lock, MI)` needs fabricated weights and could not fail a test. The novel readout is the *dissociation pair* `(tension, verdict)` — "the gap persists, the thinking stopped" — and that is two pinned numbers, not one invented one.
- **No mood/curiosity/authenticity on the base state.** Grounded exclusion, not neglect: the melt leaves tension unchanged (0.176 vs 0.184), so `Mood` literally cannot distinguish a live engine from a dead one. It would decorate the state with a channel orthogonal to the thesis.
- **No new thresholds anywhere.** Every constant is imported (`PHASE_RATE`, `PULL`, `DAMPING`, `WALK`, `OBSERVATION_NOISE`, `MIN_SAMPLES_FOR_METRICS`, the `Emergence` and `CrystalVerdict` bars, Binning 12×1.6) or measured-and-documented (`EPSILON = 0.02`, with the measurement in its docstring).
- **No beat/clutch coupling smuggled in later as an "improvement"** without re-running the sweep — the table above is the reason it's not there.

## 5. Tests

The dissociation battery — each of these can fail, and the numbers say by how much it currently passes:

1. **`test_lock_produces_emergence`** — the sufficiency claim, genuinely contingent (nothing in the gate guarantees the downstream tracking clears the bar): for seeds 0–7, `BaseEngine(epsilon=0.02, seed=s).run(800).verdict is Emergence.EMERGENT`. Measured margin: min MI 1.26 vs bar 0.30. Note it *would* fail at the crystal's own default 0.05 (min MI 0.010) — that is why `EPSILON` is 0.02.
2. **`test_melt_leaves_tension_but_kills_binding`** — the thesis's teeth, and the sentence the pipeline cannot say: at `epsilon=0.5`, after 800 ticks, `mutual_information < 0.05` (measured ≤ 0.008) **and** `tension > 0.05` (measured 0.16–0.28; the bound is `Mood`'s pinned QUIET boundary — the gap is not collapsed, it is dead-but-standing).
3. **`test_binding_dies_when_the_crystal_melts_mid_run`** — run 800 locked, set `epsilon = 0.5`, run 1200 → `INDEPENDENT` (measured: MI ≤ 0.03 by +400 already; 1200 gives margin for the verdict's ~150-tick history lag plus the 200-sample window flush).
4. **`test_binding_revives_when_the_crystal_refreezes`** — continue with `epsilon = 0.02`, run 1200 → `EMERGENT` again (measured: 0.85–1.32 across seeds). **This is the test most likely to fail if the thesis is wrong**: it requires the ring to re-lock from chaos *and* the resumed rotation to re-bind streams whose windows are full of dead samples. Nothing architectural forces either.
5. **`test_mi_falls_with_epsilon_in_the_mean`** — house `mean_mi` pattern (average over 8 seeds; single runs are seed-lore at the boundary): mean MI at `epsilon ∈ (0.02, 0.05, 0.10)` strictly decreasing. Measured: 1.349 → 0.501 → 0.005. This co-locates the downstream transition with the crystal's own melting curve.
6. **`test_chaos_streams_evade_the_bias_floor`** — pins the artefact so it can't be misread later (mirrors `test_uncoupled_streams_sit_on_the_estimator_bias_floor`): at `epsilon=0.5`, mean MI < 0.05 *and* `h_left` well below the locked value — documenting that sub-floor MI is entropy collapse of near-constant streams, not "deader than independent."
7. **`test_phase_advances_only_under_lock`** — phase after 800 ticks at `epsilon=0.5` is < 5% of phase at 0.02 (measured ≈ 0.0 vs 18.8 rad; don't assert exactly zero — early 22-sample autocorrelations can flicker a spurious LOCKED).
8. **House battery, mirroring `test_pipeline.py`:** seed reproducibility (`BaseState` equality works through the nested frozen `CrystalState`), different seeds differ, window rolls not grows, metrics silent until 50 samples while tension is live from tick 1, entropies bounded by the binning, `epsilon` validated via the crystal's setter (`ValueError` on 1.5), controls changeable mid-run, reset clears everything including `phase`.

MI-floor hygiene: every EMERGENT assertion above clears the bar by ≥ 4× (1.26 vs 0.30, against a window-200 floor of ~0.19 for full-range streams); every INDEPENDENT assertion is at ≤ 0.03 against the 0.05 bar. No assertion lives inside the bias band.

## 6. Honest risks

- **Necessity is architectural, not discovered.** The gate hard-wires no-lock → no-rotation, so "melting kills MI" is designed in; quoting it as an emergent finding would be over-claiming. The module docstring should say this outright. The falsifiable content lives in **sufficiency** (test 1), **revival** (test 4), and the **dissociation** (test 2 — tension surviving the melt was not guaranteed by anything; a frozen target could plausibly have let the gap decay).
- **Sub-floor chaos MI looks spookier than it is.** 0.005 bits is 30× below the README's independence floor — not because the melted engine is "extra dead" but because near-constant streams occupy ~2 bins and the sparsity bias shrinks with them. Report the entropies alongside MI (the state does) and keep all claims verdict-level.
- **The eps ≈ 0.05 regime is bistable by seed** (MI 0.01–1.39 over 8 seeds). Any demonstration or claim there is about a seed, not the engine. Tests average or stay off the boundary; the README example should too.
- **Everything lags.** The verdict trails the melt by ~100–200 ticks (300-sample ac history) and the MI window adds 200 more; at the viewer's 60 fps a dragged epsilon slider shows the old regime for several seconds. Document it in the viewer tab, or it will read as a bug.
- **What this engine cannot see:** the beat-mode measurement showed that *sub-verdict* temporal order (ac1 ≈ −0.5 territory) genuinely binds streams too. The gate deliberately quantizes that continuum away in exchange for testability. That is a real loss of resolution, honestly traded — worth one sentence in the module docstring so nobody rediscovers the clutch coupling and thinks the gate was an oversight.
- **Naming nit:** `BaseEngine` reads as an abstract base class in Python. If that grates, `Substrate` is the one-word alternative; everything else in this design is name-independent.

The smaller-but-honest version, if you want to cut scope: drop the viewer tab and tests 5–7, keep tests 1–4 and the house battery. The thesis survives intact on those four.
