# Grid Mysteries

**One surprising event on Britain's electricity system. Reconstructed from public data. Open to falsification.**

Grid Mysteries is an open research project for investigating things that look strange in GB power-market data: an apparently cheaper Balancing Mechanism action that was skipped, wind curtailed while Britain imports power, a violent forecast revision, an unusual negative-price episode, or any other event where the headline explanation is not enough.

The project is deliberately not a feed of hot takes. Each published mystery should have:

1. a concrete event that a non-specialist can understand;
2. the public source data needed to reproduce it;
3. an explicit distinction between observation and interpretation;
4. a list of explanations checked and not checked;
5. a falsifiable conclusion, including "still unexplained" where appropriate;
6. a compact expert appendix so practitioners can challenge the analysis;
7. a Morpholog evidence record for the research acts worth defending.

## Research doctrine

A skip is not automatically a mistake. A price difference is not automatically a saving. A backtest is not automatically tradable. Public data is not automatically the complete control-room state.

The default claim is therefore deliberately narrow:

> **"I cannot explain this event from the public state reconstructed here."**

That claim may later be corrected when an expert points out missing evidence. Corrections are part of the research record, not an embarrassment to erase.

## Stack

- **Python 3.14** for ingestion, analysis and rendering.
- **Polars** for columnar research data.
- **httpx** for public APIs.
- **Typer** for a small command-line workflow.
- **Morpholog** (the release pinned in `scripts/install-morpholog`) for governed evidence: source artefacts, hypotheses and published findings.

Morpholog is intentionally not the analytics engine. Python computes; Morpholog records the small set of research claims that should remain defensible later.

## Quick start

```bash
uv sync --dev
./scripts/install-morpholog
./scripts/check
uv run grid-mysteries doctor
```

`scripts/check` is the authoritative local gate (Ruff lint + format, pytest, and
`morpholog check morpholog/research.morph`); CI runs the same script.

The installer pins Morpholog to the release named in `scripts/install-morpholog` and verifies the published SHA-256 digest for supported platforms.

## Layout

```text
src/grid_mysteries/
    cli.py                   # researcher workflow
    models.py                # investigation/source data structures
    hashing.py               # content addressing
    sources/                 # public-data adapters
    investigations/         # reusable analytical investigations
    rendering/              # publication-ready output helpers
morpholog/
    research.morph           # governed research record
investigations/
    000-template/            # one folder per public investigation
scripts/
    install-morpholog        # pinned binary installer
data/
    raw/                     # ignored; immutable source downloads
    derived/                 # ignored; reproducible computed tables
```

## First research target

The first concrete investigation is **apparently non-economic balancing dispatch**:

> A lower-priced action appears available while a higher-priced action is accepted. Can the difference be explained from public information?

The initial code does **not** claim to identify a true NESO error. It provides the plumbing for recording the event, pinning the source artefacts and progressively testing explanations such as dynamic limits, physical position, previous dispatch and published exclusion classifications.

## Publishing format

Every LinkedIn/public post should aim for three layers:

**The mystery** — one sentence a general reader understands.

**The evidence** — one chart and the minimum reconstruction supporting the question.

**Expert corner** — exact settlement period/BMU identifiers, source artefacts, assumptions and the question practitioners can falsify.

A good result can be "explained". A better result can be "I was wrong; here is the missing mechanism". The most interesting result is a pattern that survives repeated attempts to explain it away.

## Data policy

Do not commit bulk source datasets. Store raw responses locally as immutable content-addressed files and commit only small fixtures where licensing permits. An investigation manifest should carry URLs/dataset identifiers, publication/fetch timestamps and SHA-256 digests so another researcher can retrieve and compare the source material.

## Licence

MIT. Source data remains subject to the terms of its original publisher.
