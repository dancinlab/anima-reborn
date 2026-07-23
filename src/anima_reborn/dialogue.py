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
        h = dominant(human[referent])
        e = dominant(engine[referent])
        if h is None or e is None:
            continue
        seen += 1
        agree += int(h == e)
    return agree / seen if seen else 0.5
