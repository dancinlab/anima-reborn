# src/anima_reborn/iit4/ — Integrated Information Theory 4.0

A port of the hexa IIT 4.0 engine in `dancinlab/selfhost-work`
(`stdlib/consciousness/iit4_*.hexa` and `stdlib/iit_ei.hexa`). It answers one
question: is this system, in this state, one thing — or parts that happen to sit
together?

## The chain

| module | engine | origin |
| --- | --- | --- |
| `tpm.py` | M1 — matrix, repertoires, intrinsic difference | `iit4_tpm.hexa` |
| `distinction.py` | M2 — small-phi, MICE, distinctions | `iit4_distinction.hexa` |
| `relation.py` | M3 — congruent relations, Phi-structure | `iit4_relation.hexa` |
| `bigphi.py` | M4 — system big-Phi over the minimum cut | `iit4_bigphi.hexa` |
| `directed.py` | the same over DIRECTED cuts — tells a loop from a chain | (new — closes a carve-out) |
| `exclusion.py` | M10 + M13 — maximal complex, spectrum | `iit4_complex.hexa` |
| `ei.py` | effective information, a lower bound on Phi | `iit_ei.hexa` |

Each layer imports only the one below it. Do not add a back edge.

## Parity is the contract

`tests/test_iit4.py` holds a golden table dumped from the hexa engine at full
float precision, and compares with **exact equality** across every reported
field — phi, total, sum of distinction phi, sum of relation phi, and the
distinction count. Eleven cases, all bit-identical.

That strictness is not fussiness. Phi is an argmax over partitions and purviews,
so a last-bit change can select a different partition and move the answer
discontinuously. A tolerance would hide exactly the drift worth catching.

Consequences for anyone editing here:

- **Compute log2 as `(log p - log q) / log 2`**, never `math.log2`. They differ
  in the last bits and the origin used the former.
- **Keep `Q_SMOOTHING = 1e-10`** exactly where it is. It is why a perfect
  two-unit system reads 1.9999999994229218 and not 2.0.
- **Do not "clean up" a tie-break.** Lowest index on an intrinsic-difference
  tie, larger subset then lower mask on a complex tie. Reproducibility is the
  only reason those rules exist.
- If a change moves a golden number, that is a finding to explain, not a test to
  update.

## Carve-outs — inherited, not closed

State these when reporting results; do not let a reader assume otherwise.

- Partitions are all bipartitions of mechanism-and-purview, the standard
  tractable scheme, **not** IIT 4.0's own partition set.
- big-Phi is the Phi-structure destroyed by the system cut. IIT 4.0 proper
  rebuilds the cause-effect structure on the partitioned matrix with a
  normalization factor.
- **CLOSED, loudly:** `big_phi`'s cut is undirected and so reads a strictly
  feedforward chain at 1.27 bits where the theory says zero. `directed_big_phi`
  cuts one direction at a time and reads it 0.000 exactly, while the ring stays
  at 10.02 through the same code. `big_phi` is unchanged — the goldens depend on
  it — so both numbers are available and the old name still means what it did.
  Use `directed_big_phi` for any claim about recurrence.
- Relations are second-order only — pairs, bound by `min(phi_d)`.
- Nothing here is calibrated against PyPhi. On PyPhi's standard three-node
  network this engine reports 3.7548875003600997, which is this engine's number
  and not a claim about the theory's.

## Cost

Exponential several times over: every mechanism searches every purview across
every partition, and `find_complex` repeats that for all `2^n - 1` subsets.
Rough shape at n = 3: `big_phi` about 5 ms, `find_complex` about 6 ms. Six units
is slow, seven is unreasonable. `substrate.py` caps measurable systems at six
for this reason.

`TransitionMatrix` memoizes `marginal_on`, which is what makes anything past
three units finish at all. The cache is keyed on the mask and the pinned bits
only; it changes no result, because the matrix is immutable after construction.

## The `+inf` branch in `ei.py`

Kept, and very nearly unreachable — the reference is the column mean of the same
matrix, so a zero there implies a zero numerator. The one way in is arithmetic:
a subnormal probability whose division by the state count underflows. There is a
test for both facts. Do not delete the guard, and do not claim it fires in
ordinary use.
