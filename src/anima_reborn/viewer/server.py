"""The viewer's HTTP server — stdlib only, one engine of each kind.

Frames are **pushed**, not polled. Each engine has a ticker thread that steps it
at the origin's own rate — 60 Hz for emergence, 30 Hz for the repulsion field
and the pipeline, 20 Hz for the crystal — and publishes each new state to
whoever is subscribed over a single long-lived `text/event-stream` connection.
The page opens one stream, receives frames as fast as the engine produces them,
and draws on the display's own refresh.

Pulling instead would cap the frame rate at the poll interval and pay a request
round trip per frame; the engines cost 0.02-0.23 ms per tick, so that cap was
the only thing standing between this viewer and the origin's 60 fps.

A ticker runs only while at least one viewer is watching it, which is the same
thing the origin's page did by skipping inactive tabs.

One instance of each engine is shared by every connected browser, so two tabs
watch the same run rather than two diverging ones. A lock guards each engine,
since the server is threaded and the engines are mutable.
"""

from __future__ import annotations

import json
import socket
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from ..align import Aligner
from ..base import BaseEngine
from ..coupled import (
    ALTERNATING,
    FIXED,
    NAMES as COUPLED_NAMES,
    CoupledEngine,
    Wiring,
)
from ..crystal import TimeCrystal
from ..dialogue import DialogueSession
from ..emergence import EmergenceEngine
from ..pipeline import Pipeline
from ..repulsion import RepulsionField

__all__ = ["Viewer", "serve"]

PAGE = Path(__file__).parent / "page.html"

SESSIONS_DIR = Path(__file__).resolve().parents[3] / "state" / "communication" / "sessions"
"""Where a completed human dialogue session is written — git-tracked with the rest of the
work outputs (`preserve-state`). This is the viewer, the one place in the package that does
I/O; the session engine itself only accumulates its log in memory."""

MAX_STEPS_PER_REQUEST = 240
"""Cap on the `steps` of a one-shot `/api/<engine>` request. The streaming path
does not use it — a ticker's rate is fixed by the server, not by the client."""

TICK_RATES = {
    "emergence": 60.0,
    "crystal": 20.0,
    "repulsion": 30.0,
    "pipeline": 30.0,
    "base": 30.0,
    "coupled": 30.0,
    "align": 60.0,
    "dialogue": 8.0,
}
"""Ticks per second, carried from the origin's `setInterval` periods so the
engines run at the speed their thresholds were chosen against."""

PING_SECONDS = 10.0
"""How long a stream waits for a frame before sending a keep-alive comment. A
paused engine must still notice that its viewer has gone away."""


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(slots=True)
class _Guarded:
    """An engine and the lock that serializes access to it."""

    engine: Any
    lock: threading.Lock


def _number(params: dict[str, list[str]], key: str, default: float) -> float:
    raw = params.get(key)
    if not raw:
        return default
    try:
        return float(raw[0])
    except ValueError:
        return default


def _round(values: Any, places: int = 4) -> list[float]:
    """Trim the float noise out of the wire format — the page draws pixels, and
    seventeen significant digits per sample is most of the payload."""
    return [round(float(v), places) for v in values]


class _EmergenceHandler:
    @staticmethod
    def configure(engine: EmergenceEngine, params: dict[str, list[str]]) -> None:
        engine.coupling = _clamp(_number(params, "coupling", engine.coupling), 0.0, 1.0)

    @staticmethod
    def describe(engine: EmergenceEngine) -> dict[str, Any]:
        metrics = engine.metrics
        return {
            "left": _round(engine.left),
            "right": _round(engine.right),
            "ticks": engine.ticks,
            "range": engine.binning.vrange,
            "metrics": None
            if metrics is None
            else {
                "h_left": metrics.h_left,
                "h_right": metrics.h_right,
                "h_joint": metrics.h_joint,
                "mi": metrics.mutual_information,
                "verdict": metrics.verdict.value,
            },
        }


class _CrystalHandler:
    @staticmethod
    def configure(engine: TimeCrystal, params: dict[str, list[str]]) -> None:
        engine.epsilon = _clamp(_number(params, "epsilon", engine.epsilon), 0.0, 1.0)

    @staticmethod
    def describe(engine: TimeCrystal) -> dict[str, Any]:
        state = engine.state
        return {
            "spins": list(engine.spins),
            "history": _round(engine.history),
            "magnetization": state.magnetization,
            "ac1": state.ac1,
            "ac2": state.ac2,
            "ac4": state.ac4,
            "verdict": state.verdict.value,
        }


class _RepulsionHandler:
    @staticmethod
    def configure(engine: RepulsionField, params: dict[str, list[str]]) -> None:
        engine.separation = _clamp(_number(params, "separation", engine.separation), 0.0, 2.0)
        engine.noise = _clamp(_number(params, "noise", engine.noise), 0.0, 1.0)

    @staticmethod
    def describe(engine: RepulsionField) -> dict[str, Any]:
        state = engine.state
        if state is None:  # unreachable — a frame is only cut after a step
            raise ValueError("repulsion field has not been stepped")
        return {
            "a": _round(engine.a),
            "g": _round(engine.g),
            "concept": _round(state.concept),
            "meaning": _round(state.meaning),
            "context": _round(state.context),
            "sender": _round(state.sender),
            "tension": state.tension,
            "topic": state.topic,
            "curiosity": state.curiosity,
            "authenticity": state.authenticity,
            "mood": state.mood.value,
            "ticks": engine.ticks,
        }


class _PipelineHandler:
    @staticmethod
    def configure(engine: Pipeline, params: dict[str, list[str]]) -> None:
        engine.separation = _clamp(_number(params, "separation", engine.separation), 0.0, 2.0)

    @staticmethod
    def describe(engine: Pipeline) -> dict[str, Any]:
        state = engine.state
        return {
            "a": _round(engine.a),
            "g": _round(engine.g),
            "left": _round(engine.left),
            "right": _round(engine.right),
            "range": engine.binning.vrange,
            "tension": state.tension,
            "h_left": state.h_left,
            "h_right": state.h_right,
            "h_joint": state.h_joint,
            "mi": state.mutual_information,
            "verdict": state.verdict.value,
            "ticks": engine.ticks,
        }


class _BaseHandler:
    @staticmethod
    def configure(engine: BaseEngine, params: dict[str, list[str]]) -> None:
        engine.epsilon = _clamp(_number(params, "epsilon", engine.epsilon), 0.0, 1.0)
        engine.separation = _clamp(
            _number(params, "separation", engine.separation), 0.0, 2.0
        )

    @staticmethod
    def describe(engine: BaseEngine) -> dict[str, Any]:
        state = engine.state
        return {
            "a": _round(engine.a),
            "g": _round(engine.g),
            "left": _round(engine.left),
            "right": _round(engine.right),
            "magnetization": _round(engine.magnetization),
            "range": engine.binning.vrange,
            "phase": state.phase,
            "tension": state.tension,
            "h_left": state.h_left,
            "h_right": state.h_right,
            "mi": state.mutual_information,
            "verdict": state.verdict.value,
            "rhythm": state.crystal.verdict.value,
            "ac1": state.crystal.ac1,
            "ac2": state.crystal.ac2,
            "ticks": engine.ticks,
        }


class _CoupledHandler:
    """The coupled field.

    Phi is far too slow to compute per frame, so the panel streams the live
    dynamics and the measurement is a separate, deliberate act — the operator
    presses for it. A number this conditional should not arrive as ambient
    decoration.

    The rhythm is the one control here whose effect is visible without any
    measurement: on a fixed coupling the drive slider does nothing at all, which
    is the wall as something to watch rather than a claim to read.
    """

    @staticmethod
    def configure(engine: CoupledEngine, params: dict[str, list[str]]) -> None:
        raw = params.get("wiring")
        if raw:
            try:
                wiring = Wiring(raw[0])
            except ValueError:
                return  # unknown value: leave the engine as it is
            if wiring is not engine.wiring:
                engine.wiring = wiring
                engine.reset()  # a different wiring is a different system
        rhythms = params.get("rhythm")
        if rhythms:
            # Unknown value keeps the current rhythm, as with every control here.
            rhythm = {"fixed": FIXED, "alternating": ALTERNATING}.get(
                rhythms[0], engine.rhythm
            )
            if rhythm != engine.rhythm:
                engine.rhythm = rhythm
                engine.reset()  # a different rhythm is a different system
        engine.gain = max(0.1, _number(params, "gain", engine.gain))
        engine.drive = max(-1.0, min(1.0, _number(params, "drive", engine.drive)))

    @staticmethod
    def describe(engine: CoupledEngine) -> dict[str, Any]:
        state = engine.state
        return {
            "names": list(COUPLED_NAMES),
            "values": _round(state.values),
            "sources": [
                -1 if s is None else s for s in engine.wiring.sources
            ],
            "wiring": engine.wiring.value,
            "cyclic": engine.wiring.is_cyclic,
            "amplitude": engine.amplitude,
            "gain": engine.gain,
            "tension": state.tension,
            "pattern": state.pattern,
            "ticks": state.ticks,
            "rhythm": "alternating" if engine.rhythm.alternates else "fixed",
            "period": engine.rhythm.period or 0,
            "drive": engine.drive,
            "coupling": round(state.coupling, 4),
            "listening": state.listening,
            "reachable": engine.rhythm.mean < 1.0,
        }


class _AlignHandler:
    """The learner.

    Scoring is far more expensive than learning, so `describe` reads `state`
    once per frame while the ticker takes many steps between frames — the cost
    ratio the engine's own docstring warns about, respected here.
    """

    @staticmethod
    def configure(engine: Aligner, params: dict[str, list[str]]) -> None:
        engine.rate = max(1e-4, _number(params, "rate", engine.rate))
        engine.noise = max(0.0, _number(params, "noise", engine.noise))
        wanted = params.get("shuffled")
        if wanted:
            shuffled = wanted[0] == "1"
            if shuffled is not engine.shuffled:
                engine.shuffled = shuffled
                engine.reset()  # a different training regime is a different run

    @staticmethod
    def describe(engine: Aligner) -> dict[str, Any]:
        state = engine.state
        # One held-out concept, drawn the same way every frame, so the page can
        # show where its two modalities currently land.
        left = engine.project(engine.observe(10_000, modality=0), modality=0)
        right = engine.project(engine.observe(10_000, modality=1), modality=1)
        return {
            "same": state.same_concept,
            "different": state.different_concept,
            "gap": state.gap,
            "initial_gap": state.initial_gap,
            "learned": state.learned,
            "aligned": state.aligned,
            "pairs": state.pairs_seen,
            "shuffled": engine.shuffled,
            "rate": engine.rate,
            "noise": engine.noise,
            "left": _round(left),
            "right": _round(right),
        }


def _persist_session(report: dict[str, Any]) -> None:
    """Write a completed session's log and verdict to `state/communication/sessions/`.

    The I/O lives here in the viewer, never in the engine. A missing or read-only tree is
    swallowed rather than crashing the stream — the session is still shown in the browser.
    """
    try:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d-%H%M%S")
        path = SESSIONS_DIR / f"{stamp}-{report['token']}.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


class _DialogueHandler:
    """The live human dialogue session — the one interactive tab.

    Unlike every other handler its engine waits on human input rather than free-running:
    `configure` carries the human's button press (a trial nonce and a choice) into the
    session, `step` (in the ticker) resolves it, and `describe` reads the frame. The
    session is a bit-exact no-op on a tick with nothing submitted, so the fixed tick rate
    is only an input-latency bound. On completion the finished log is written to `state/`.
    """

    @staticmethod
    def configure(session: DialogueSession, params: dict[str, list[str]]) -> None:
        raw_nonce = params.get("nonce")
        raw_choice = params.get("choice")
        if not raw_nonce or not raw_choice:
            return  # a plain frame request (sliders/one-shot) — nothing to submit
        try:
            nonce = int(raw_nonce[0])
            choice = int(raw_choice[0])
        except ValueError:
            return
        # Idempotent: a stale or double-submitted nonce is ignored by the session, so the
        # ticker re-applying the same persistent control dict cannot double-resolve a trial.
        session.submit(nonce, choice)

    @staticmethod
    def describe(session: DialogueSession) -> dict[str, Any]:
        frame = session.describe()
        report = session.take_report()
        if report is not None:
            _persist_session(report)
        return frame


_HANDLERS: dict[str, Any] = {
    "emergence": _EmergenceHandler,
    "crystal": _CrystalHandler,
    "repulsion": _RepulsionHandler,
    "pipeline": _PipelineHandler,
    "base": _BaseHandler,
    "coupled": _CoupledHandler,
    "align": _AlignHandler,
    "dialogue": _DialogueHandler,
}


class _Ticker:
    """Steps one engine on its own thread and publishes each frame.

    Runs only while someone is subscribed. Subscribers wait on a condition
    rather than polling, so a frame reaches the browser as soon as it exists.
    """

    def __init__(self, guarded: _Guarded, handler: Any, rate: float) -> None:
        self._guarded = guarded
        self._handler = handler
        self._interval = 1.0 / rate
        self._condition = threading.Condition()
        self._frame: dict[str, Any] | None = None
        self._sequence = 0
        self._watchers = 0
        self._running = False
        self._generation = 0
        self._controls: dict[str, list[str]] = {}

    @property
    def rate(self) -> float:
        return 1.0 / self._interval

    @property
    def watchers(self) -> int:
        with self._condition:
            return self._watchers

    def control(self, params: dict[str, list[str]]) -> None:
        """Take the page's slider values. They are applied by the ticker before
        its next step rather than here, so control never races a step."""
        with self._condition:
            self._controls = params

    def subscribe(self) -> int:
        """Register a watcher and return the sequence number it has seen, so
        the first frame it receives is one it has not."""
        with self._condition:
            self._watchers += 1
            if not self._running:
                self._running = True
                # A new generation. The previous thread may still be inside its
                # sleep; when it wakes it will see a generation that is not its
                # own and retire, so a fast unsubscribe/subscribe — switching
                # tabs quickly — cannot leave two threads stepping one engine
                # at twice its rate.
                self._generation += 1
                threading.Thread(
                    target=self._run, args=(self._generation,), daemon=True
                ).start()
            return self._sequence

    def unsubscribe(self) -> None:
        with self._condition:
            self._watchers -= 1
            if self._watchers <= 0:
                self._watchers = 0
                self._running = False
                self._condition.notify_all()

    def wait(self, seen: int, timeout: float) -> tuple[int, dict[str, Any] | None]:
        """Block until a frame newer than `seen` exists, or the timeout expires.

        Returns the unchanged sequence number on timeout, which the caller uses
        as its cue to send a keep-alive.
        """
        with self._condition:
            self._condition.wait_for(lambda: self._sequence != seen, timeout)
            return self._sequence, self._frame

    def _run(self, generation: int) -> None:
        due = time.monotonic()
        while True:
            with self._condition:
                if not self._running or self._generation != generation:
                    return
                controls = self._controls

            with self._guarded.lock:
                engine = self._guarded.engine
                self._handler.configure(engine, controls)
                engine.step()
                frame = self._handler.describe(engine)

            with self._condition:
                self._sequence += 1
                self._frame = frame
                self._condition.notify_all()

            due += self._interval
            delay = due - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            else:
                # Fell behind — resync rather than sprint to catch up, which
                # would show as a burst of frames at the wrong speed.
                due = time.monotonic()


class Viewer:
    """Holds one of each engine, the ticker driving it, and its controls."""

    def __init__(self, *, seed: int | None = None) -> None:
        engines = {
            "emergence": EmergenceEngine(coupling=0.5, seed=seed),
            "crystal": TimeCrystal(epsilon=0.05, seed=seed),
            "repulsion": RepulsionField(seed=seed),
            "pipeline": Pipeline(seed=seed),
            "base": BaseEngine(seed=seed),
            "coupled": CoupledEngine(seed=seed),
            "align": Aligner(seed=seed),
            "dialogue": DialogueSession(seed=seed),
        }
        self._engines = {
            name: _Guarded(engine, threading.Lock())
            for name, engine in engines.items()
        }
        self._tickers = {
            name: _Ticker(guarded, _HANDLERS[name], TICK_RATES[name])
            for name, guarded in self._engines.items()
        }

    def names(self) -> tuple[str, ...]:
        return tuple(self._engines)

    def engine(self, name: str) -> Any:
        """The live engine behind one route.

        Handed out so the viewer can be embedded and inspected. Stepping it
        from outside races the ticker — read it, or take the lock.
        """
        return self._engines[name].engine

    def ticker(self, name: str) -> _Ticker:
        """The ticker driving one engine."""
        return self._tickers[name]

    def control(self, name: str, params: dict[str, list[str]]) -> dict[str, Any]:
        self._tickers[name].control(params)
        return {"ok": True}

    def reset(self, name: str) -> dict[str, Any]:
        guarded = self._engines[name]
        with guarded.lock:
            guarded.engine.reset()
        return {"reset": name}

    def advance(self, name: str, params: dict[str, list[str]]) -> dict[str, Any]:
        """Apply controls, step, and describe — the one-shot path.

        The page streams instead; this stays for scripting the viewer from a
        shell and for tests that want a frame without a socket.
        """
        guarded = self._engines[name]
        steps = int(_clamp(_number(params, "steps", 1.0), 1, MAX_STEPS_PER_REQUEST))
        with guarded.lock:
            engine = guarded.engine
            handler = _HANDLERS[name]
            handler.configure(engine, params)
            for _ in range(steps):
                engine.step()
            return handler.describe(engine)


class _Handler(BaseHTTPRequestHandler):
    server_version = "anima-reborn-viewer"
    protocol_version = "HTTP/1.1"
    """Keep-alive. Under HTTP/1.0 every request paid a fresh TCP handshake,
    which is most of the cost of a frame on anything but loopback. Every
    non-streaming response below sends a Content-Length, which is what makes
    connection reuse legal."""

    viewer: Viewer

    def do_GET(self) -> None:
        url = urlparse(self.path)
        path = url.path.rstrip("/") or "/"

        if path == "/":
            self._send_page()
            return

        if path.startswith("/api/"):
            self._route(path[len("/api/"):], parse_qs(url.query))
            return

        self._send_json({"error": "not found"}, status=404)

    def _route(self, route: str, params: dict[str, list[str]]) -> None:
        name, _, verb = route.partition("/")
        if name not in self.viewer.names():
            self._send_json({"error": f"unknown engine: {name}"}, status=404)
            return
        try:
            if verb == "stream":
                self._stream(name, params)
            elif verb == "control":
                self._send_json(self.viewer.control(name, params))
            elif verb == "reset":
                self._send_json(self.viewer.reset(name))
            elif verb == "":
                self._send_json(self.viewer.advance(name, params))
            else:
                self._send_json({"error": f"unknown action: {verb}"}, status=404)
        except (ValueError, KeyError) as exc:
            self._send_json({"error": str(exc)}, status=400)

    def _stream(self, name: str, params: dict[str, list[str]]) -> None:
        """Push frames until the browser goes away.

        The response has no length, so the connection cannot be reused; it is
        held open for the life of the stream instead.
        """
        ticker = self.viewer.ticker(name)
        if params:
            ticker.control(params)

        self.close_connection = True
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        seen = ticker.subscribe()
        try:
            self._write(f"retry: 500\nevent: hello\ndata: {json.dumps({'rate': ticker.rate})}\n\n")
            while True:
                sequence, frame = ticker.wait(seen, PING_SECONDS)
                if sequence == seen or frame is None:
                    # Nothing new. The comment is what detects a browser that
                    # closed without telling us.
                    self._write(": ping\n\n")
                    continue
                seen = sequence
                self._write(f"data: {json.dumps(frame)}\n\n")
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass  # the page navigated away; the finally clause is the cleanup
        finally:
            ticker.unsubscribe()

    def _write(self, text: str) -> None:
        self.wfile.write(text.encode())
        self.wfile.flush()

    def _send_page(self) -> None:
        try:
            body = PAGE.read_bytes()
        except OSError as exc:
            self._send_json({"error": f"page missing: {exc}"}, status=500)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            # The page navigated away mid-request. Nothing to recover, and it
            # is not worth a stack trace in the log.
            pass

    def log_message(self, fmt: str, *args: Any) -> None:
        """Silence the per-request log — a stream would otherwise log once per
        frame and bury the startup banner."""


def local_address() -> str:
    """The address of this machine another host on the network would use.

    Opens a UDP socket toward a routable address to learn which interface the
    kernel would pick; nothing is sent. Falls back to the loopback address when
    there is no route at all.
    """
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 9))  # TEST-NET-1, guaranteed unrouted
        return str(probe.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


def serve(
    *,
    host: str = "0.0.0.0",
    port: int = 8420,
    seed: int | None = None,
) -> None:
    """Run the viewer until interrupted.

    Args:
        host: Interface to bind. The default accepts connections from anywhere
            on the network, which is what makes the viewer reachable by IP;
            pass "127.0.0.1" to keep it on this machine.
        port: TCP port.
        seed: Seeds all four engines, so a demonstration can be repeated.
    """
    handler = type("_BoundHandler", (_Handler,), {"viewer": Viewer(seed=seed)})
    server = ThreadingHTTPServer((host, port), handler)
    server.daemon_threads = True

    reachable = local_address() if host in ("0.0.0.0", "::", "") else host
    banner = ["anima-reborn viewer", f"  local    http://127.0.0.1:{port}"]
    if reachable != "127.0.0.1":
        banner.append(f"  network  http://{reachable}:{port}")
    if host == "0.0.0.0":
        banner.append("  bound to every interface — anyone on this network can reach it")
    rates = " · ".join(f"{name} {int(hz)}Hz" for name, hz in TICK_RATES.items())
    banner.append(f"  {rates}")
    banner.append("  ctrl-c to stop")
    # Flushed explicitly: stdout is block-buffered whenever it is redirected to
    # a file or a pipe, which is exactly when someone needs to read the address
    # off the log.
    print("\n".join(banner), flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped", flush=True)
    finally:
        server.server_close()
