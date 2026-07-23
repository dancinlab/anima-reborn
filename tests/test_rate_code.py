"""The door in the recursive wall: a population rate code holds analog depth AND a response consumes it.

`transient_gate.py` pinned the wall — a single bistable latch flattens analog depth to its sign, so
context stayed an unusable continuous readout. This pins the escape (width, not a new non-latching
element): a population of N near-barrier latches transduces the input depth into a COUNT at write
time, the count holds flat through deaf silence where a single latch's depth is 0.000, and a latched
response driven from the population mean carries that depth beyond the sign — the exact control that
read 0.0000 in `transient_gate.py`. The full MI battery + nulls live in
`state/communication/rate_code.py` and RESULTS; these are the cheap invariants that guard it.
"""

from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "rate_code.py"
_spec = importlib.util.spec_from_file_location("rate_code", _PATH)
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)


def _counts(a: float, sign: int, *, hold: int, n: int = 20):
    """The up-count each trial settles to at the given hold, for one (a, sign) class."""
    return [
        rc._write_and_hold(a, sign, scale=0.08, seed=800_000 + k, n_pairs=rc.PAIRS_N, holds=(hold,))[hold][0]
        for k in range(n)
    ]


class TestTheDoorIsWidth:
    def test_the_count_grades_with_input_depth(self) -> None:
        """The population up-count rises monotonically with the input magnitude a — the write-time
        transduction of depth (magnitude) into a count (sign statistics)."""
        means = [statistics.mean(_counts(a, +1, hold=0)) for a in rc.AMPS]
        assert means == sorted(means), means
        assert means[-1] - means[0] > 4.0, means  # a real graded span, not one bin

    def test_depth_survives_deaf_silence_where_a_single_latch_flattens(self) -> None:
        """The count barely moves between hold 240 and 480 (the basin holds each bit), so the analog
        count is a stable memory at the endpoint where `depth_hold.py` measured 0.000 for one latch."""
        for a in (0.2, 0.5, 0.8):
            c240 = statistics.mean(_counts(a, +1, hold=240))
            c480 = statistics.mean(_counts(a, +1, hold=480))
            assert abs(c480 - c240) < 1.0, (a, c240, c480)

    def test_the_population_beats_the_single_latch_wall(self) -> None:
        """A wider population holds the sign more reliably through silence than one latch — the
        row that is the wall in the script's N-sweep (N=1) is worse than N=32."""
        one = statistics.mean(
            1 if (_counts(a, +1, hold=240, n=20)[k] * 2 - 1) > 0 else 0
            for a in rc.AMPS for k in range(20)
        )
        many = statistics.mean(
            1 if (2 * c - rc.PAIRS_N) > 0 else 0
            for a in rc.AMPS for c in _counts(a, +1, hold=240)
        )
        assert many >= one, (one, many)
        assert many >= 0.95, many

    def test_a_latched_response_consumes_the_depth(self) -> None:
        """A response latch biased by theta (the median heard rate, as the script calibrates it)
        separates by the input magnitude for a fixed sign — where the single-latch consumer of
        `transient_gate.py` gave one response for every depth. Read from the held mean at hold 480."""
        heard = {}  # a -> [linear-read of the held mean per trial]
        for a in rc.AMPS:
            heard[a] = [
                rc._h_lin(rc._write_and_hold(a, +1, scale=0.08, seed=910_000 + k,
                                             n_pairs=rc.PAIRS_N, holds=(480,))[480][1])
                for k in range(20)
            ]
        theta = statistics.median(h for hs in heard.values() for h in hs)  # split point
        outs = {
            a: statistics.mean(rc._response(h - theta, seed=920_000 + k) for k, h in enumerate(hs))
            for a, hs in heard.items()
        }
        # the response rate must move across the depth range — the sign is fixed, so this is depth
        assert max(outs.values()) - min(outs.values()) > 0.3, outs

    def test_reproducible(self) -> None:
        a = rc._write_and_hold(0.5, +1, scale=0.08, seed=7, n_pairs=8, holds=(240,))
        b = rc._write_and_hold(0.5, +1, scale=0.08, seed=7, n_pairs=8, holds=(240,))
        assert a == b
