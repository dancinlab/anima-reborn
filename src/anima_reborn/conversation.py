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
