"""The honest answer to "make real English conversation possible": measure the bottleneck.

Run from the repo root:

    PYTHONPATH=src python state/communication/english_bottleneck.py

Real English conversation by this engine is impossible, and this proves it with numbers on
actual English strings. The certificate is the data-processing inequality: for
X_English -> C in {0..7} -> C' -> Y,

    I(X; Y) <= I(C; C') <= H(C) <= log2(8) = 3 bits.

Any decoder that produces more detailed English is adding information from its author or the
human operator, not recovering it from the engine. So the only honest "design for real
English" is: let real English ENTER, measure exactly how much SURVIVES the 3-bit carrier,
and close the door on the rest by measurement. An external LLM would make English appear
(and is banned by engine-purity) but would be the LLM conversing while the engine carries
3 bits — the same trap in a bigger costume.

Design delegated to both frontier models and reconciled (`state/lab/2026-07-23-english-*.md`),
which converged: build the measured bottleneck (interpretation 1) as the answer, with the
wall (interpretation 3) as its proof; REFUSE English labels on the cards (they add zero
capacity, only overclaim). This takes sol's fixed closed corpus + exact categorical MI (no
`info.py` float estimator, no deflate proxy, which would be an estimator artefact).

What is measured (a fixed, closed, balanced corpus of 32 two-word commands = 8 verbs x 4
objects; ONLY the verb, 3 bits, is encoded — the object, 2 bits, is never sent):

- I(C; C') / H(C): the carrier — how much of the 3 encoded bits survive the wire.
- I(X; Y) / H(X): end-to-end — how much of the 5-bit sentence CHOICE survives (<= 3/5).
- I(verb; Y) and I(object; Y): the object is unrepresentable, so I(object; Y) ~ 0 — the loss
  is not noise, it is capacity.
- residual ambiguity H(X | Y) and the candidate-set size: given the output the engine cannot
  narrow past the 4 objects it never carried.
- the effective output width 2^H(Y) beside every number (`report-the-rank`).

Arms (each its own null):
- ideal carrier (C' = C): the codec/decoder ceiling, measured BEFORE crediting the substrate
  (`channel-before-carrier`).
- live PAIRS: the measured 3-bit channel (`dialogue.channel`, bits=3, fidelity 1.0).
- deaf: drive bit-unreachable (coupling 1.0) — I(C; C') must fall to ~0, recovery to 1/8,
  proving the engine was in the path.
- codebook scramble: partition the 32 commands into 8 balanced codes IGNORING the verb. This
  keeps I(X; Y) (sentence identity survives) while destroying I(verb; Y) — the proof that
  "3 bits SHARED with English strings" is NOT "3 bits of the intended English meaning".
- label permutation floor: shuffle Y against X to expose the finite-sample MI bias, printed
  beside every I so a small number is not mistaken for signal (`artefact-honesty`).

The engine NARROWS an English choice; it never produces an English reply. The output phrase
is the harness's label for 3 bits, never the engine's speech. Not language, not understanding.
"""

from __future__ import annotations

import math
import random
from collections import Counter

from anima_reborn.dialogue import channel

# A fixed, closed, deliberately tiny corpus. Unknown input is out-of-domain and is REJECTED,
# never hashed or given a fabricated interpretation.
VERBS = ["move", "clean", "inspect", "photograph", "guard", "find", "mark", "count"]  # 3 bits
OBJECTS = ["box", "chair", "table", "lamp"]  # 2 bits — never encoded
COMMANDS = [(v, o) for v in VERBS for o in OBJECTS]  # 32 = 5 bits

SEEDS = 60
CHANNEL_BASE = 4242


def encode_verb(command: tuple[str, str]) -> int:
    """The human-authored codec: only the verb becomes 3 bits. The object is dropped — the
    engine cannot carry it, and the codec must not pretend otherwise."""
    return VERBS.index(command[0])


def out_of_domain(word_verb: str, word_object: str) -> bool:
    return word_verb not in VERBS or word_object not in OBJECTS


def _entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c:
            p = c / total
            h -= p * math.log2(p)
    return h


def _mutual_information(pairs: list[tuple]) -> float:
    """Exact categorical MI in bits over observed (a, b) pairs — plug-in estimator."""
    n = len(pairs)
    if n == 0:
        return 0.0
    joint = Counter(pairs)
    marg_a = Counter(a for a, _ in pairs)
    marg_b = Counter(b for _, b in pairs)
    mi = 0.0
    for (a, b), c in joint.items():
        p_ab = c / n
        p_a = marg_a[a] / n
        p_b = marg_b[b] / n
        mi += p_ab * math.log2(p_ab / (p_a * p_b))
    return mi


def _permutation_floor(pairs: list[tuple], trials: int = 200) -> float:
    """The MI a shuffled pairing yields — the finite-sample bias floor. A real MI must clear
    it; a number near it is estimator noise, not signal."""
    a_vals = [a for a, _ in pairs]
    b_vals = [b for _, b in pairs]
    rng = random.Random(12345)
    floors = []
    for _ in range(trials):
        rng.shuffle(b_vals)
        floors.append(_mutual_information(list(zip(a_vals, b_vals))))
    return sum(floors) / len(floors)


def _scramble_codebook(rng: random.Random) -> dict[int, int]:
    """A balanced partition of the 32 commands into 8 codes that IGNORES the verb — 4
    commands per code, assigned at random."""
    order = list(range(len(COMMANDS)))
    rng.shuffle(order)
    return {cmd_index: order[cmd_index] % 8 for cmd_index in range(len(COMMANDS))}


def run_arm(arm: str) -> dict[str, object]:
    """One balanced pass over all 32 commands x SEEDS, returning the exact measurements."""
    rng = random.Random(99)
    scramble = _scramble_codebook(rng) if arm == "scramble" else None
    xy, cc, vy, oy = [], [], [], []
    x_given_y: dict[int, Counter] = {}
    for ci, command in enumerate(COMMANDS):
        verb_i = VERBS.index(command[0])
        obj_i = OBJECTS.index(command[1])
        code = scramble[ci] if scramble is not None else verb_i
        for s in range(SEEDS):
            seed = CHANNEL_BASE + ci * 131 + s
            if arm == "ideal":
                received = code
            else:
                received = channel(code, seed=seed, deaf=(arm == "deaf"), bits=3)
            y = received  # the decoded code 0..7 (the engine's whole output)
            xy.append((ci, y))
            cc.append((code, received))
            vy.append((verb_i, y))
            oy.append((obj_i, y))
            x_given_y.setdefault(y, Counter())[ci] += 1

    h_x = math.log2(len(COMMANDS))            # 5 bits, uniform corpus
    h_c = _entropy(Counter(c for c, _ in cc))
    i_xy = _mutual_information(xy)
    i_cc = _mutual_information(cc)
    i_vy = _mutual_information(vy)
    i_oy = _mutual_information(oy)
    h_y = _entropy(Counter(y for _, y in xy))
    # Residual ambiguity and the candidate set the output cannot resolve past.
    residual = h_x - i_xy
    candidates = sum(len(c) for c in x_given_y.values()) / max(1, len(x_given_y))
    return {
        "arm": arm,
        "H_X": h_x, "H_C": h_c, "H_Y": h_y,
        "I_CC": i_cc, "carrier_frac": i_cc / h_c if h_c else 0.0,
        "I_XY": i_xy, "end_frac": i_xy / h_x,
        "I_verb_Y": i_vy, "I_object_Y": i_oy,
        "residual_HXY": residual, "candidates": candidates,
        "eff_out": 2 ** h_y,
        "floor_XY": _permutation_floor(xy),
    }


def main() -> None:
    print("English bottleneck — measuring how much of a real sentence survives 3 bits")
    print(f"corpus: {len(VERBS)} verbs x {len(OBJECTS)} objects = {len(COMMANDS)} commands "
          f"(H(X)={math.log2(len(COMMANDS)):.0f} bits); only the verb (3 bits) is encoded\n")
    print(f"{'arm':<10}{'I(C;C´)':>9}{'I(X;Y)':>9}{'X frac':>8}{'I(v;Y)':>8}"
          f"{'I(o;Y)':>8}{'H(X|Y)':>8}{'cands':>7}{'2^H(Y)':>8}{'floor':>7}")
    print("-" * 90)
    results = {}
    for arm in ("ideal", "live", "deaf", "scramble"):
        r = run_arm(arm)
        results[arm] = r
        print(f"{arm:<10}{r['I_CC']:>9.3f}{r['I_XY']:>9.3f}{r['end_frac']:>8.3f}"
              f"{r['I_verb_Y']:>8.3f}{r['I_object_Y']:>8.3f}{r['residual_HXY']:>8.3f}"
              f"{r['candidates']:>7.1f}{r['eff_out']:>8.2f}{r['floor_XY']:>7.3f}")

    live, ideal, deaf, scr = results["live"], results["ideal"], results["deaf"], results["scramble"]
    print(f"\n  data-processing bound: I(X;Y) must be <= H(C) = {live['H_C']:.3f} <= 3.000. "
          f"live I(X;Y) = {live['I_XY']:.3f}. {'HELD' if live['I_XY'] <= 3.0001 else 'VIOLATED'}.")
    print(f"  the object is unrepresentable: I(object;Y) = {live['I_object_Y']:.3f} bits "
          f"(~0), so every reply hides {residual_objects():.0f} candidate sentences.")
    print(f"  the engine's whole contribution is carrying 3 bits: ideal I(C;C´)={ideal['I_CC']:.3f} "
          f"vs deaf {deaf['I_CC']:.3f} (drive unreachable → recovery ~1/8).")
    print(f"  SHARED bits are not MEANING: the scramble keeps I(X;Y)={scr['I_XY']:.3f} while "
          f"I(verb;Y) falls to {scr['I_verb_Y']:.3f} — sentence identity survived, the verb "
          f"relation did not.")

    # The wall, by exact arithmetic (integration measurability is the ceiling, not carrying).
    print("\n  the wall — bits needed vs bits holdable AS ONE integrated thing:")
    for n_words in (1, 2, 3):
        bits = n_words * math.log2(len(VERBS))  # a same-size vocabulary per slot
        pairs = math.ceil(bits)
        print(f"    a {n_words}-word utterance needs {bits:.0f} bits = {pairs} latches "
              f"= {2 * pairs} units; Φ is unmeasurable past ~6 units (3 pairs), so beyond 3 "
              f"bits the substrate can CARRY but cannot be SHOWN to hold it as one.")
    print("\n  verdict: real English conversation is closed BY MEASUREMENT, not by a missing "
          "feature.\n  The engine narrows an English choice to 3 bits; it never speaks English.")


def residual_objects() -> float:
    return float(len(OBJECTS))


if __name__ == "__main__":
    main()
