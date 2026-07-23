"""The live human<->engine dialogue session and its two structural audits.

`DialogueSession` puts a real human in the partner's seat; the reproducible half (a
synthetic partner) is tested in `test_dialogue.py`. These pin the two apertures that must
not encode the answer — the update rule cannot see across the gap, and the display frame
cannot carry the referent — plus the session mechanics the viewer depends on: idempotent
submission, a no-op step with nothing pending, and a self-contained per-session verdict.
"""

from __future__ import annotations

import inspect

from anima_reborn import dialogue
from anima_reborn.dialogue import DialogueSession, channel, display_payload


def _play(session: DialogueSession, strategy) -> dict:
    """Drive a session to completion with a scripted human, returning its report."""
    steps = 0
    while session.phase != "done" and steps < 2000:
        pending = session._pending
        if pending is None:
            break
        session.submit(pending["nonce"], strategy(pending))
        session.step()
        steps += 1
    return session.describe()["report"]


class TestTheTwoAudits:
    def test_the_update_rule_reads_only_one_agents_locals(self) -> None:
        """The engine-side aperture: `reinforce` is handed one policy and one agent's own
        (state, choice, reward), with no argument for the other agent's state."""
        params = list(inspect.signature(dialogue.reinforce).parameters)
        assert params == ["policy", "state", "choice", "reward"], params

    def test_the_display_builder_cannot_reach_the_answer(self) -> None:
        """The display aperture: `display_payload`'s signature has no argument for the
        referent, the signal, the latch word, or the success."""
        params = list(inspect.signature(display_payload).parameters)
        assert params == ["trace", "markers", "buttons"], params

    def test_no_pre_action_b_frame_carries_the_answer(self) -> None:
        """Every direction-B frame the human is shown must contain only the raw trace, the
        neutral markers, and the buttons — never the referent, signal, word, or success."""
        forbidden = {"referent", "signal", "word", "act", "success", "ref", "arm"}
        session = DialogueSession(seed=1)
        seen_b = 0
        for _ in range(400):
            frame = session.describe()
            pending = frame.get("pending")
            if pending and pending["dir"] == "b":
                seen_b += 1
                assert set(pending) <= {"nonce", "dir", "buttons", "trace", "markers"}, pending
                assert not (set(pending) & forbidden), pending
            if session._pending is not None:
                session.submit(session._pending["nonce"], 0)
                session.step()
            if session.phase == "done":
                break
        assert seen_b > 0, "no direction-B trials were inspected"

    def test_the_b_trace_is_hold_only_never_the_drive(self) -> None:
        """The frame ships the HOLD trajectory (drive already cut), not the TELL phase —
        a lossy display cannot leak what it was never handed."""
        session = DialogueSession(seed=2)
        for _ in range(400):
            pending = session._pending
            if pending is None:
                break
            if pending["spec"]["dir"] == "b":
                assert len(pending["display"]["trace"]) == dialogue.HOLD
            session.submit(pending["nonce"], 0)
            session.step()


class TestSessionMechanics:
    def test_submission_is_idempotent(self) -> None:
        session = DialogueSession(seed=3)
        nonce = session._pending["nonce"]
        assert session.submit(nonce, 0) is True
        assert session.submit(nonce, 1) is False, "a second submit was accepted"
        assert session.submit(9999, 0) is False, "a stale nonce was accepted"
        before = len(session._log)
        session.step()
        assert len(session._log) == before + 1, "one trial produced more than one log row"

    def test_a_step_with_nothing_pending_is_a_no_op(self) -> None:
        session = DialogueSession(seed=4)
        cursor, log = session._cursor, len(session._log)
        session.step()  # no submission yet
        assert session._cursor == cursor and len(session._log) == log

    def test_a_session_completes_and_reports_both_directions(self) -> None:
        report = _play(DialogueSession(seed=5), lambda p: 0)
        assert report["verdict"] in {
            "two_way_session_evidence", "one_way_session_evidence",
            "no_session_evidence", "audit_failed",
        }
        for key in ("a", "b"):
            assert report[key]["verdict"] in {"formed", "no_evidence"}
            assert report[key]["width_bits"] == 1
            assert 0.0 <= report[key]["p"] <= 1.0

    def test_the_report_is_handed_over_exactly_once(self) -> None:
        session = DialogueSession(seed=6)
        _play(session, lambda p: 0)
        assert session.take_report() is not None
        assert session.take_report() is None, "the completed log was handed over twice"

    def test_a_fixed_strategy_is_refused(self) -> None:
        """Always pressing the first button establishes no convention through consequence,
        so the honest verdict is no evidence — the gate does not reward a degenerate code."""
        report = _play(DialogueSession(seed=8), lambda p: 0)
        assert report["verdict"] == "no_session_evidence"


class TestTheDisplayScrambleNull:
    """The second aperture, guarded by its own targeted null: flipping the display's unit
    identity per trial must destroy a reading that depends on the learned display
    convention, and a reading that survives the flip (a leak) voids the whole session."""

    def test_the_scramble_arm_is_scheduled_and_actually_flips(self) -> None:
        session = DialogueSession(seed=1)
        _play(session, lambda p: 0)
        rows = [e for e in session._log if e.get("arm") == "dscramble"]
        assert rows, "no display-scramble trials were scheduled"
        assert all("markers_swapped" in e for e in rows)
        assert {e["markers_swapped"] for e in rows} == {True, False}, "the flip never varied"

    def test_a_display_bypass_reading_fails_the_audit(self) -> None:
        """A 'human' who reads the true latch directly — bypassing the display — keeps
        recovering even when the display identity is scrambled, so the session is voided
        as audit_failed rather than being quietly reported as no evidence."""
        def leak(pending: dict) -> int:
            order = pending["order"]
            if pending["spec"]["dir"] == "a":
                return order.index(pending["spec"]["ref"])
            bit = channel(pending["signal"], seed=pending["channel_seed"])
            return order.index(bit)

        report = _play(DialogueSession(seed=11), leak)
        assert report["verdict"] == "audit_failed", report["verdict"]
        assert report["b"]["nulls"]["dscramble"]["rate"] > 0.65


class TestTheEchoControl:
    def test_the_frozen_engine_snapshot_stays_at_day_zero(self) -> None:
        """The echo null: the frozen policies are the day-0 (uniform) map and never learn,
        so a trained human meeting them cannot have their own bit handed back."""
        session = DialogueSession(seed=7)
        _play(session, lambda p: 0)
        assert session._frozen_recv == [[1.0, 1.0], [1.0, 1.0]]
        assert session._frozen_send == [[1.0, 1.0], [1.0, 1.0]]
