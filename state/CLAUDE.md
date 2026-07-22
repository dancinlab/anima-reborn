# state/ — work outputs, kept in the repo

Everything this project produced that is not source: delegated design reports, measurement
runs, verification scripts. Git-tracked and committed, per the cross-project `preserve-state`
rule — an experiment that lives only in `/tmp` did not happen.

```
state/
├─ lab/           delegated design reports (frontier models) + the prompts that produced them
├─ coupling/      the ring-coupling measurement: script + results
└─ communication/ what an engine would need in order to communicate: the
                  integration/representation wall, the rhythm through it, and
                  the two directions that died
```

## a script here measures the engine, not a copy of it

`alternating_coupling.py` first ran against a hand-rolled ring, and reproducing a claim
about a copy is not evidence about anything anyone imports. Once a capability lands in
`src/`, the script that re-derives it drives the shipped engine.

## what belongs here
- do: Delegated reports · measurement runs · one-off verification scripts · the prompt that produced each report, stored beside it
- dont: Anything imported by `src/` · a second outputs directory somewhere else · results with no script or conditions beside them

## reports are evidence, not decisions
- do: Store a report verbatim, and record the independent re-measurement separately (`coupling/RESULTS.md` is the pattern) · name the numbers that did NOT reproduce
- dont: Editing a report to match what was later found · treating a delegated number as verified because it is written down

## every result carries its conditions
- do: Ship state · threshold · timescale · trial count · seeds with any Phi, and a runnable script that re-derives it
- dont: A number with no way to reproduce it — `Phi = 12` without `tau = 17` is a false statement, not a shorthand

## naming
- do: `YYYY-MM-DD-<topic>-<source>.md`, so a report and its prompt sort together
- dont: Version or copy suffixes (`-v2`, `-final`) — history is git's job
