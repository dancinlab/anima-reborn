"""IIT 4.0 — parity with the hexa origin, and the theory's own invariants.

The golden table below was dumped from the hexa engine itself
(`dancinlab/selfhost-work` `stdlib/consciousness/iit4_*.hexa`) at full float
precision, and equality here is exact. Phi is an argmax over partitions and
purviews, so a change in the last bit can move which partition wins and
silently change the answer — a tolerance would hide precisely the kind of drift
worth catching.
"""

from __future__ import annotations

import math

import pytest

from anima_reborn.iit4 import (
    NO_COMPLEX,
    Direction,
    TransitionMatrix,
    average_effective_information,
    big_phi,
    column_mean,
    complex_spectrum,
    congruent_overlap,
    distinctions,
    effective_information,
    find_complex,
    intrinsic_difference,
    mice,
    phi_structure,
    small_phi,
    subsystem,
)


# ── the networks ───────────────────────────────────────────────────────────
def copy_pair() -> TransitionMatrix:
    """Each unit becomes the other. Mutually coupled, so irreducible."""
    return TransitionMatrix([0, 0, 0, 1, 1, 0, 1, 1], 2)


def self_pair() -> TransitionMatrix:
    """Each unit becomes itself. Two systems sharing a name, so reducible."""
    return TransitionMatrix([0, 0, 1, 0, 0, 1, 1, 1], 2)


def noise_pair() -> TransitionMatrix:
    """Every transition equally likely — no causal structure at all."""
    return TransitionMatrix([0.5] * 8, 2)


def probabilistic_pair() -> TransitionMatrix:
    """Asymmetric and non-deterministic, so the floats are not round numbers."""
    return TransitionMatrix([0.1, 0.9, 0.8, 0.2, 0.3, 0.7, 0.6, 0.4], 2)


def embedded_core() -> TransitionMatrix:
    """A coupled pair {0,1} with an independent unit 2 bolted on.

    The whole is reducible — unit 2 cuts away for free — but the pair inside is
    not. This is what the exclusion postulate is for.
    """
    return TransitionMatrix(
        [float(v) for s in range(8) for v in ((s >> 1) & 1, s & 1, (s >> 2) & 1)], 3
    )


def basic_network() -> TransitionMatrix:
    """PyPhi's standard three-node example: A = OR, B = AND, C = XOR."""
    return TransitionMatrix(
        # fmt: off
        [0, 0, 0,  0, 0, 1,  1, 0, 1,  1, 0, 0,
         1, 1, 0,  1, 1, 1,  1, 1, 1,  1, 1, 0],
        # fmt: on
        3,
    )


# ── parity ─────────────────────────────────────────────────────────────────
# case -> (phi, total, sum_phi_d, sum_phi_r, distinction_count)
GOLDEN = {
    "copy@11": (1.9999999994229218, 1.9999999994229218, 1.9999999994229218, 0.0, 2),
    "self@11": (0.0, 1.9999999994229218, 1.9999999994229218, 0.0, 2),
    "noise@11": (0.0, 0.0, 0.0, 0.0, 0),
    "prob@00": (0.0, 0.39314064078121, 0.39314064078121, 0.0, 1),
    "prob@01": (
        0.46107977240793074,
        0.9072807166142157,
        0.6767408304102503,
        0.2305398862039654,
        2,
    ),
    "prob@11": (0.0, 0.446200944206285, 0.446200944206285, 0.0, 1),
    "embedded@111": (0.0, 2.9999999991343826, 2.9999999991343826, 0.0, 3),
    "embedded@000": (0.0, 2.9999999991343826, 2.9999999991343826, 0.0, 3),
    "basic@001": (
        3.7548875003600997,
        3.7548875003600997,
        2.1699250004324258,
        1.584962499927674,
        4,
    ),
    "basic@101": (
        2.084962499639135,
        2.084962499639135,
        1.584962499927674,
        0.499999999711461,
        3,
    ),
}

CASES = {
    "copy@11": (copy_pair, 0b11),
    "self@11": (self_pair, 0b11),
    "noise@11": (noise_pair, 0b11),
    "prob@00": (probabilistic_pair, 0b00),
    "prob@01": (probabilistic_pair, 0b01),
    "prob@11": (probabilistic_pair, 0b11),
    "embedded@111": (embedded_core, 0b111),
    "embedded@000": (embedded_core, 0b000),
    "basic@001": (basic_network, 0b001),
    "basic@101": (basic_network, 0b101),
}


@pytest.mark.parametrize("case", sorted(GOLDEN))
def test_matches_the_hexa_engine_bit_for_bit(case: str) -> None:
    build, state = CASES[case]
    measured = big_phi(build(), state)
    expected = GOLDEN[case]

    assert measured.phi == expected[0]
    assert measured.total == expected[1]
    assert measured.structure.distinction_phi == expected[2]
    assert measured.structure.relation_phi == expected[3]
    assert len(measured.structure.distinctions) == expected[4]


def test_the_complex_matches_the_hexa_engine() -> None:
    found = find_complex(embedded_core(), 0b111)
    assert found.units == 0b011
    assert found.phi == 1.9999999994229218
    assert found.size == 2


# ── what the theory claims ─────────────────────────────────────────────────
class TestIrreducibility:
    def test_mutually_coupled_units_are_one_thing(self) -> None:
        measured = big_phi(copy_pair(), 0b11)
        assert measured.is_irreducible
        assert measured.phi == pytest.approx(2.0, abs=1e-9)

    def test_independent_units_are_not(self) -> None:
        """Each unit only ever looks at itself, so there is a free cut. The
        structure is not empty — each unit specifies plenty — but none of it
        survives being asked to hold together."""
        measured = big_phi(self_pair(), 0b11)
        assert not measured.is_irreducible
        assert measured.phi == 0.0
        assert measured.total > 0.0

    def test_noise_specifies_nothing_at_all(self) -> None:
        measured = big_phi(noise_pair(), 0b11)
        assert measured.total == 0.0
        assert measured.phi == 0.0
        assert measured.structure.distinctions == ()

    def test_phi_never_exceeds_the_structure_it_cuts(self) -> None:
        """big-Phi is what a cut destroys, so it is bounded by what exists."""
        for build, state in CASES.values():
            measured = big_phi(build(), state)
            assert 0.0 <= measured.phi <= measured.total + 1e-12

    def test_a_single_unit_has_nothing_to_cut(self) -> None:
        measured = big_phi(TransitionMatrix([0.0, 1.0], 1), 0b1)
        assert measured.phi == 0.0
        assert measured.cut == 0


class TestExclusion:
    def test_the_complex_is_the_coupled_pair_not_the_whole(self) -> None:
        """The three-unit system is reducible, yet a complex lives inside it.
        This is the exclusion postulate doing its job: the entity is the
        maximal subsystem, not whatever the caller happened to hand over."""
        assert big_phi(embedded_core(), 0b111).phi == 0.0

        found = find_complex(embedded_core(), 0b111)
        assert found.exists
        assert found.units == 0b011
        assert not found.units >> 2 & 1, "the independent unit must be excluded"

    def test_a_noise_substrate_hosts_no_complex(self) -> None:
        assert find_complex(noise_pair(), 0b11) == NO_COMPLEX
        assert not NO_COMPLEX.exists

    def test_the_spectrum_never_overlaps(self) -> None:
        """A unit belongs to at most one complex."""
        seen = 0
        for found in complex_spectrum(basic_network(), 0b001):
            assert not found.units & seen
            seen |= found.units

    def test_the_spectrum_is_ranked(self) -> None:
        spectrum = complex_spectrum(basic_network(), 0b001)
        assert [c.phi for c in spectrum] == sorted(
            (c.phi for c in spectrum), reverse=True
        )

    def test_the_spectrum_leads_with_the_maximal_complex(self) -> None:
        matrix, state = embedded_core(), 0b111
        spectrum = complex_spectrum(matrix, state)
        assert spectrum
        assert spectrum[0].units == find_complex(matrix, state).units

    def test_an_empty_subsystem_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one unit"):
            subsystem(copy_pair(), 0, 0b11)

    def test_a_subsystem_is_a_system(self) -> None:
        part = subsystem(embedded_core(), 0b011, 0b111)
        assert part.n == 2
        assert part.states == 4
        assert len(part.values) == 8


class TestDistinctions:
    def test_a_distinction_reports_both_directions(self) -> None:
        found = distinctions(copy_pair(), 0b11)
        assert found
        for d in found:
            assert d.phi == min(d.cause.phi, d.effect.phi)
            assert d.cause.direction is Direction.CAUSE
            assert d.effect.direction is Direction.EFFECT
            assert d.exists

    def test_involves_covers_mechanism_and_both_purviews(self) -> None:
        d = distinctions(basic_network(), 0b001)[0]
        for unit in range(3):
            bit = 1 << unit
            expected = bool(
                d.mechanism & bit or d.cause.purview & bit or d.effect.purview & bit
            )
            assert d.involves(unit) is expected

    def test_small_phi_is_never_negative(self) -> None:
        matrix = probabilistic_pair()
        for mechanism in range(1, 4):
            for purview in range(1, 4):
                for direction in Direction:
                    phi, _ = small_phi(matrix, mechanism, 0b01, purview, direction)
                    assert phi >= 0.0

    def test_mice_picks_a_real_purview(self) -> None:
        found = mice(basic_network(), 0b001, 0b001, Direction.EFFECT)
        assert found.purview != 0
        assert found.phi >= 0.0
        assert 0 <= found.state < (1 << bin(found.purview).count("1"))

    def test_noise_yields_no_distinctions(self) -> None:
        assert distinctions(noise_pair(), 0b11) == ()


class TestRepertoires:
    @pytest.mark.parametrize("state", [0b00, 0b01, 0b10, 0b11])
    def test_repertoires_are_distributions(self, state: int) -> None:
        matrix = probabilistic_pair()
        for purview in (0b01, 0b10, 0b11):
            for repertoire in (
                matrix.effect_repertoire(0b11, state, purview),
                matrix.cause_repertoire(0b11, state, purview),
                matrix.unconstrained_effect(purview),
                matrix.unconstrained_cause(purview),
            ):
                assert sum(repertoire) == pytest.approx(1.0)
                assert all(p >= 0.0 for p in repertoire)

    def test_an_unconstrained_effect_is_the_bare_marginal(self) -> None:
        matrix = probabilistic_pair()
        assert matrix.unconstrained_effect(0b11) == matrix.effect_repertoire(0, 0, 0b11)

    def test_an_unconstrained_cause_is_uniform(self) -> None:
        assert probabilistic_pair().unconstrained_cause(0b11) == (0.25,) * 4

    def test_marginal_caching_returns_the_same_number(self) -> None:
        """The cache exists for speed and must change nothing."""
        matrix = basic_network()
        first = matrix.marginal_on(0b101, 0b101, 1)
        assert matrix.marginal_on(0b101, 0b101, 1) == first
        # Bits outside the mask are not part of the question.
        assert matrix.marginal_on(0b101, 0b111, 1) == first


class TestIntrinsicDifference:
    def test_identical_distributions_carry_no_difference(self) -> None:
        uniform = (0.25,) * 4
        assert intrinsic_difference(uniform, uniform).value == pytest.approx(
            0.0, abs=1e-9
        )

    def test_it_takes_the_max_not_the_sum(self) -> None:
        """The IIT 4.0 break from 3.0: one pointwise term, not a divergence."""
        p = (0.5, 0.5, 0.0, 0.0)
        q = (0.25,) * 4
        result = intrinsic_difference(p, q)
        assert result.value == pytest.approx(0.5, abs=1e-9)  # not 1.0, the KL sum

    def test_ties_go_to_the_lowest_index(self) -> None:
        """Reproducibility depends on this."""
        p = (0.5, 0.5, 0.0, 0.0)
        assert intrinsic_difference(p, (0.25,) * 4).state == 0

    def test_it_names_the_specified_state(self) -> None:
        p = (0.0, 0.0, 0.0, 1.0)
        assert intrinsic_difference(p, (0.25,) * 4).state == 3


class TestCongruence:
    def test_disjoint_purviews_do_not_relate(self) -> None:
        assert not congruent_overlap(0b01, 0, 0b10, 0, 2)

    def test_sharing_a_unit_and_agreeing_relates(self) -> None:
        # Both say unit 0 is ON.
        assert congruent_overlap(0b01, 0b1, 0b11, 0b01, 2)

    def test_sharing_a_unit_and_disagreeing_does_not(self) -> None:
        # One says unit 0 is ON, the other says OFF.
        assert not congruent_overlap(0b01, 0b1, 0b11, 0b10, 2)


class TestStructure:
    def test_totals_add_up(self) -> None:
        structure = phi_structure(basic_network(), 0b001)
        assert structure.total == pytest.approx(
            structure.distinction_phi + structure.relation_phi
        )
        assert len(structure) == len(structure.distinctions)

    def test_a_relation_never_outweighs_what_it_binds(self) -> None:
        structure = phi_structure(basic_network(), 0b001)
        by_mechanism = {d.mechanism: d.phi for d in structure.distinctions}
        for relation in structure.relations:
            assert relation.phi <= min(
                by_mechanism[relation.left], by_mechanism[relation.right]
            ) + 1e-12


class TestMatrixValidation:
    def test_rejects_the_wrong_number_of_entries(self) -> None:
        with pytest.raises(ValueError, match="needs 8 entries"):
            TransitionMatrix([0.0] * 7, 2)

    def test_rejects_a_non_probability(self) -> None:
        with pytest.raises(ValueError, match="probability in"):
            TransitionMatrix([0.0, 0.0, 0.0, 1.5, 0.0, 0.0, 0.0, 0.0], 2)

    def test_rejects_an_empty_system(self) -> None:
        with pytest.raises(ValueError, match="n must be >= 1"):
            TransitionMatrix([], 0)

    def test_from_rows_rejects_a_short_table(self) -> None:
        with pytest.raises(ValueError, match="need 4 rows"):
            TransitionMatrix.from_rows([[0.0, 0.0], [1.0, 1.0]])

    def test_from_rows_rejects_ragged_rows(self) -> None:
        with pytest.raises(ValueError, match="same units"):
            TransitionMatrix.from_rows([[0.0, 0.0], [1.0], [0.0, 0.0], [1.0, 1.0]])

    def test_from_rows_and_flat_agree(self) -> None:
        rows = TransitionMatrix.from_rows([[0.1, 0.9], [0.8, 0.2], [0.3, 0.7], [0.6, 0.4]])
        assert rows.values == probabilistic_pair().values


# ── effective information ──────────────────────────────────────────────────
class TestEffectiveInformation:
    def test_a_deterministic_cycle_is_maximally_informative(self) -> None:
        """Three states in a loop: each start point pins the next exactly, so
        EI is ln 3 nats — the whole uncertainty of the reference."""
        cycle = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
        assert effective_information(cycle) == pytest.approx((math.log(3),) * 3)

    def test_a_uniform_system_carries_none(self) -> None:
        assert effective_information([[1 / 3] * 3] * 3) == (0.0, 0.0, 0.0)

    def test_bits_and_nats_agree(self) -> None:
        cycle = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
        in_nats = effective_information(cycle)
        in_bits = effective_information(cycle, bits=True)
        for nats, bits in zip(in_nats, in_bits):
            assert bits == pytest.approx(nats / math.log(2))

    def test_an_ordinary_matrix_can_never_be_singular(self) -> None:
        """The reference is the column mean of the same matrix, so a zero there
        means no state reaches that target — and then the numerator is zero
        too. The singular branch simply has no ordinary input."""
        matrices = [
            [[0.0, 1.0], [0.0, 0.0]],
            [[1.0, 0.0], [0.0, 1.0]],
            [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            [[0.9, 0.1], [0.0, 1.0]],
        ]
        for matrix in matrices:
            assert all(v != math.inf for v in effective_information(matrix)), matrix

    def test_a_subnormal_probability_can_still_reach_it(self) -> None:
        """The one way in is arithmetic, not causal: 5e-324 divided by the two
        states underflows to zero, so the reference vanishes while the row keeps
        a positive probability. Reporting infinity is the honest answer;
        smoothing it would invent a finite number."""
        matrix = [[5e-324, 1.0], [0.0, 1.0]]
        assert effective_information(matrix)[0] == math.inf

    def test_the_average_skips_infinities(self) -> None:
        """One singular state must not make the whole average useless."""
        matrix = [[5e-324, 1.0], [0.0, 1.0]]
        assert average_effective_information(matrix) == 0.0

    def test_the_average_of_a_cycle(self) -> None:
        cycle = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
        assert average_effective_information(cycle) == pytest.approx(math.log(3))

    def test_column_mean_is_the_reference(self) -> None:
        assert column_mean([[1.0, 0.0], [0.0, 1.0]]) == (0.5, 0.5)

    def test_rejects_a_non_square_matrix(self) -> None:
        with pytest.raises(ValueError, match="must be\\s+square"):
            effective_information([[0.5, 0.5, 0.0], [0.5, 0.5, 0.0]])

    def test_rejects_a_negative_probability(self) -> None:
        with pytest.raises(ValueError, match="negative probability"):
            effective_information([[-0.5, 1.5], [0.5, 0.5]])


def test_effective_information_is_a_floor_under_phi() -> None:
    """EI is IIT's conservative lower bound, so a system with no integration at
    all should not show effective information either. Checked on the noise
    system, where both are structurally zero.

    Note this compares two different lanes — EI takes a state-to-state matrix,
    big-Phi takes state-by-node — so it is a sanity check on the pair, not a
    numeric identity.
    """
    uniform_transitions = [[0.25] * 4 for _ in range(4)]
    assert average_effective_information(uniform_transitions) == 0.0
    assert big_phi(noise_pair(), 0b11).phi == 0.0
