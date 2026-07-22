"""A local server that renders the engines in a browser.

The engines themselves stay headless — this package is the only place in
`anima_reborn` that opens a socket, reads a clock or holds mutable shared
state. The browser does no simulation of its own: it polls, and draws whatever
Python sends back. What you see on the page is this package's output, not a
JavaScript reimplementation of it.

    python -m anima_reborn.viewer

By default it binds every interface, so another machine on the same network can
reach it by IP.
"""

from __future__ import annotations

from .server import Viewer, serve

__all__ = ["Viewer", "serve"]
