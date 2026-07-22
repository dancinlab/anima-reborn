"""`python -m anima_reborn.viewer` — run the browser viewer."""

from __future__ import annotations

import argparse

from .server import serve


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m anima_reborn.viewer",
        description="Serve a browser view of the anima-reborn engines.",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="interface to bind (default: %(default)s, reachable from the network; "
        "pass 127.0.0.1 to keep it on this machine)",
    )
    parser.add_argument(
        "--port", type=int, default=8420, help="TCP port (default: %(default)s)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="seed all four engines so a demonstration repeats exactly",
    )
    args = parser.parse_args()
    serve(host=args.host, port=args.port, seed=args.seed)


if __name__ == "__main__":
    main()
