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
