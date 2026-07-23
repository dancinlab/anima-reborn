"""The English-bottleneck proof: real English does not survive the 3-bit engine.

These pin the certificate (the data-processing bound), the object being unrepresentable, the
deaf null, and the "shared bits are not meaning" scramble — so the honest answer to "make
real English conversation possible" cannot silently rot into an overclaim.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "state" / "communication" / "english_bottleneck.py"
_spec = importlib.util.spec_from_file_location("english_bottleneck", _PATH)
eb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eb)


class TestCorpus:
    def test_the_corpus_is_closed_and_balanced(self) -> None:
        assert len(eb.VERBS) == 8 and len(set(eb.VERBS)) == 8
        assert len(eb.OBJECTS) == 4 and len(set(eb.OBJECTS)) == 4
        assert len(eb.COMMANDS) == 32

    def test_unknown_input_is_out_of_domain(self) -> None:
        assert eb.out_of_domain("teleport", "box") is True
        assert eb.out_of_domain("move", "spaceship") is True
        assert eb.out_of_domain("move", "box") is False

    def test_only_the_verb_is_encoded_into_three_bits(self) -> None:
        for command in eb.COMMANDS:
            code = eb.encode_verb(command)
            assert 0 <= code <= 7  # at most 8 carrier symbols


class TestTheCertificate:
    def test_the_run_is_reproducible(self) -> None:
        assert eb.run_arm("live") == eb.run_arm("live")

    def test_the_data_processing_bound_holds(self) -> None:
        live = eb.run_arm("live")
        assert live["I_XY"] <= live["H_C"] + 1e-9
        assert live["H_C"] <= 3.0 + 1e-9
        assert live["I_XY"] <= 3.0 + 1e-9

    def test_the_object_is_unrepresentable(self) -> None:
        """It was never encoded, so no information about it can survive — the loss is
        capacity, not noise, and every output hides all four objects."""
        live = eb.run_arm("live")
        assert live["I_object_Y"] < 0.05, live["I_object_Y"]
        assert live["candidates"] == float(len(eb.OBJECTS))
        assert abs(live["residual_HXY"] - math.log2(len(eb.OBJECTS))) < 0.05

    def test_the_deaf_null_collapses(self) -> None:
        """Drive bit-unreachable: the carrier must lose the code, proving the engine was in
        the path at all."""
        deaf = eb.run_arm("deaf")
        assert deaf["I_CC"] < 0.2, deaf["I_CC"]
        assert deaf["I_XY"] <= deaf["floor_XY"] + 0.05

    def test_shared_bits_are_not_meaning(self) -> None:
        """A codebook that ignores the verb keeps sentence identity (I(X;Y) high) while the
        predeclared verb relation collapses — so "3 bits shared with English" is not "3 bits
        of English meaning"."""
        scramble = eb.run_arm("scramble")
        assert scramble["I_XY"] > 2.5
        assert scramble["I_verb_Y"] < scramble["I_XY"] - 1.0

    def test_the_engine_contribution_is_only_carrying(self) -> None:
        """The ideal (no-engine) carrier already scores the ceiling; the engine adds only
        the 3 bits the deaf arm loses."""
        ideal = eb.run_arm("ideal")
        deaf = eb.run_arm("deaf")
        assert ideal["I_CC"] > 2.9
        assert ideal["I_CC"] - deaf["I_CC"] > 2.5
