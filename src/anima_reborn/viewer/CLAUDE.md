# src/anima_reborn/viewer/ — the I/O boundary

The browser view of the engines. This is the **only** package in `anima_reborn` allowed
to open a socket, read a clock, spawn a thread or hold mutable shared state — the
engines next door stay pure, and that separation is the point.

| file | role |
| --- | --- |
| `server.py` | `Viewer` (one engine of each kind + a lock each) and the stdlib HTTP server |
| `page.html` | the whole UI — canvas drawing, controls, polling. No build step, no CDN |
| `__main__.py` | `python -m anima_reborn.viewer` |

## The rule that makes the viewer worth having

**The browser must never simulate anything.** Every number and every plotted point comes
from a Python engine over `/api/<engine>`; the page maps values to pixels and nothing
else. The moment a formula from `emergence.py` or `crystal.py` gets reimplemented in
JavaScript, the viewer stops being evidence about the port and becomes a second,
unverified implementation that will silently drift.

## Contract

- `GET /` → `page.html`
- `GET /api/<engine>/stream?<controls>` → **the path the page uses.** One long-lived
  `text/event-stream`; the engine's ticker pushes a frame per tick
- `GET /api/<engine>/control?<controls>` → hand the ticker new slider values
- `GET /api/<engine>/reset` → rewind that engine
- `GET /api/<engine>?steps=N&<controls>` → one-shot: step `N` times and return a frame.
  Kept for `curl` and for tests that want a frame without a socket

Controls are clamped, never rejected: a stale query string must not push an engine
outside the range it validates. Unparseable values fall back to the engine's current
setting. `steps` is capped at `MAX_STEPS_PER_REQUEST` on the one-shot path; the stream
has no such knob because its rate belongs to the server.

## Why push rather than poll

Polling capped the frame rate at the poll interval and paid a TCP handshake per frame
(`BaseHTTPRequestHandler` defaults to HTTP/1.0). Measured: engines cost 0.02–0.23 ms per
tick and a LAN round trip is 1.1 ms, so nothing but the poll loop stood between this
viewer and the origin's 60 fps. `TICK_RATES` carries the origin's `setInterval` periods (and 30 Hz for `base`, which has no origin),
so an engine runs at the speed its thresholds were chosen against.

`protocol_version = "HTTP/1.1"` enables keep-alive, which is why every non-streaming
response **must** send a `Content-Length`. The stream deliberately does not, and sets
`Connection: close` instead.

## Ticker threads

`_Ticker` steps one engine and broadcasts frames to subscribers over a `Condition`. It
runs only while watched. Restarting carries a **generation** number: a thread whose
generation is stale retires, so a fast unsubscribe/subscribe — switching tabs quickly —
cannot leave two threads stepping one engine. Without that guard, eight quick tab
switches left nine threads running at 9× the intended rate;
`tests/test_viewer.py::TestTicker::test_rapid_resubscribe_leaves_one_thread` fails
loudly if the guard is removed.

## When adding an engine

1. Add a handler class with `configure(engine, params)` and `describe(engine) -> dict`,
   and register it in `_HANDLERS` and `Viewer.__init__`.
2. `describe` must **read** state, never advance it. Every engine exposes a state
   property for this; `advance` already stepped exactly as many times as asked. A
   describe that steps makes the engine run faster than the page requested —
   `tests/test_viewer.py` has a test per engine guarding precisely this.
3. Round floats on the way out (`_round`). The page draws pixels; full float repr is
   most of the payload and none of the picture.
4. Add a tab, a render function and a `STEPS` entry in `page.html`.

## Binding

`serve()` defaults to `0.0.0.0` so another machine on the network can reach the viewer
by IP, and says so in the startup banner. There is no authentication — this is a
development viewer for a trusted network, not a public service.
