# anima-reborn

The four browser engines of [`dancinlab/anima-experience`](https://github.com/dancinlab/anima-experience)
ported to Python, what they compose into once they share a clock (`base.py`), and an
IIT 4.0 engine to measure the result with (`iit4/`, bit-exact against its hexa origin).

Layout: `info` · `emergence` · `crystal` · `repulsion` · `pipeline` · `base` · `iit4/` ·
`substrate` · `viewer/`. Every folder carries its own `CLAUDE.md`, and the local one wins.

## doc-language
- do: Write EVERY document in Korean — `README.md` and all other `.md` (owner instruction)
- dont: English prose in a doc a human reads · translating code identifiers, maths symbols, API names or paths

## code-language
- do: Keep code English — identifiers · docstrings · comments · commit messages (cross-checked against the hexa upstream)
- dont: Korean in `.py` files

## claudemd-language
- do: Keep `CLAUDE.md` files English — they re-inject EVERY turn (context rot) and a write guard blocks Hangul; Korean only inside backticks
- dont: Reading this as an exception to `doc-language` — it governs `CLAUDE.md` alone

## ui-language
- do: Korean in `viewer/page.html`; translate the DISPLAYED string only, via the `ko()` map · unmapped values fall through to the original
- dont: Keying badge colour or any branch off a translated string · inventing a translation for an unmapped value

## engine-purity
- do: Standard library only · zero runtime deps · every engine reproducible under `seed=` · all I/O confined to `viewer/`
- dont: I/O, a clock, or a thread inside an engine

## measure-first
- do: Ship performance claims, measured results and any "Phi appears here" with the numbers AND the conditions they were taken under
- dont: Writing a number that was not measured

## artefact-honesty
- do: When a value that should be zero is not, check whether it shrinks with more samples, then record that in the docs AND a test
- dont: Reporting an estimator artefact as a finding · closing an upstream carve-out quietly (see `iit4/CLAUDE.md`)
