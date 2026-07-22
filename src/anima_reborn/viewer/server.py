"""The viewer's HTTP server — stdlib only, one engine of each kind.

The browser drives every engine by polling: each request carries the current
control values, asks for a few ticks, and gets back the state to draw. Holding
the engines here rather than in the page is the whole point — the picture is of
the Python port's behaviour.

One instance of each engine is shared by every connected browser, so two tabs
watch the same run rather than two diverging ones. A lock guards each engine,
since the server is threaded and the engines are mutable.
"""

from __future__ import annotations

import json
import socket
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from ..crystal import TimeCrystal
from ..emergence import EmergenceEngine
from ..pipeline import Pipeline
from ..repulsion import RepulsionField

__all__ = ["Viewer", "serve"]

PAGE = Path(__file__).parent / "page.html"

MAX_STEPS_PER_REQUEST = 240
"""A slow client that stops polling for a while must not be able to ask for a
hundred thousand ticks in one request when it comes back."""


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(slots=True)
class _Guarded:
    """An engine and the lock that serializes access to it."""

    engine: Any
    lock: threading.Lock


class Viewer:
    """Holds one of each engine and answers the page's polls."""

    def __init__(self, *, seed: int | None = None) -> None:
        self._engines = {
            "emergence": _Guarded(EmergenceEngine(coupling=0.5, seed=seed), threading.Lock()),
            "crystal": _Guarded(TimeCrystal(epsilon=0.05, seed=seed), threading.Lock()),
            "repulsion": _Guarded(RepulsionField(seed=seed), threading.Lock()),
            "pipeline": _Guarded(Pipeline(seed=seed), threading.Lock()),
        }

    def names(self) -> tuple[str, ...]:
        return tuple(self._engines)

    def engine(self, name: str) -> Any:
        """The live engine behind one route.

        Handed out so the viewer can be embedded and inspected. Stepping it
        from outside races the page's polls — read it, or take the lock.
        """
        return self._engines[name].engine

    def reset(self, name: str) -> dict[str, Any]:
        guarded = self._engines[name]
        with guarded.lock:
            guarded.engine.reset()
        return {"reset": name}

    def advance(self, name: str, params: dict[str, list[str]]) -> dict[str, Any]:
        """Apply the page's controls, step the engine, and describe it."""
        guarded = self._engines[name]
        steps = int(_clamp(_number(params, "steps", 1.0), 1, MAX_STEPS_PER_REQUEST))
        with guarded.lock:
            engine = guarded.engine
            handler = _HANDLERS[name]
            handler.configure(engine, params)
            for _ in range(steps):
                engine.step()
            return handler.describe(engine)


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
        if state is None:  # unreachable — `advance` always steps at least once
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
            "noise": engine.noise,
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
        }


_HANDLERS: dict[str, Any] = {
    "emergence": _EmergenceHandler,
    "crystal": _CrystalHandler,
    "repulsion": _RepulsionHandler,
    "pipeline": _PipelineHandler,
}


class _Handler(BaseHTTPRequestHandler):
    server_version = "anima-reborn-viewer"
    viewer: Viewer

    def do_GET(self) -> None:
        url = urlparse(self.path)
        path = url.path.rstrip("/") or "/"

        if path == "/":
            self._send_page()
            return

        if path.startswith("/api/"):
            self._send_api(path[len("/api/"):], parse_qs(url.query))
            return

        self._send_json({"error": "not found"}, status=404)

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

    def _send_api(self, route: str, params: dict[str, list[str]]) -> None:
        name, _, verb = route.partition("/")
        if name not in self.viewer.names():
            self._send_json({"error": f"unknown engine: {name}"}, status=404)
            return
        try:
            if verb == "reset":
                self._send_json(self.viewer.reset(name))
            elif verb == "":
                self._send_json(self.viewer.advance(name, params))
            else:
                self._send_json({"error": f"unknown action: {verb}"}, status=404)
        except (ValueError, KeyError) as exc:
            self._send_json({"error": str(exc)}, status=400)

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
            # The page navigated away mid-poll. Nothing to recover, and it is
            # not worth a stack trace in the log.
            pass

    def log_message(self, fmt: str, *args: Any) -> None:
        """Silence the per-request log — the page polls several times a second
        and the noise buries the startup banner."""


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
