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
7. a defensible record: the frozen declaration witnessed against roots we do not control, the committed evidence with source digests, and (for governed metrics, watches and forward-mystery lineage) the Morpholog record.

## Research doctrine

A skip is not automatically a mistake. A price difference is not automatically a saving. A backtest is not automatically tradable. Public data is not automatically the complete control-room state.

The default claim is therefore deliberately narrow:

> **"I cannot explain this event from the public state reconstructed here."**

That claim may later be corrected when an expert points out missing evidence. Corrections are part of the research record, not an embarrassment to erase.

## Stack

- **Python 3.14** for ingestion, analysis and rendering.
- **Polars** for columnar research data.
- **httpx** for public APIs.
- a small stdlib **argparse** CLI (`grid-mysteries`): toolchain state, digests, and the unattended capture job.
- **boto3** and the **OpenTimestamps** client in the `capture` dependency group; **openpyxl** and **xlrd** in `registers`.
- **Morpholog** (the release pinned in `scripts/install-morpholog`) for governed metrics with provenance, dated watches and the forward-mystery lineage.

Morpholog is intentionally not the analytics engine. Python computes; Morpholog records the small set of research claims that should remain defensible later. Standing instruments and forensic investigations from 012 onward are recorded in git with external witnesses instead (see `CLAUDE.md`, research doctrine).

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
    cli.py                   # researcher workflow (doctor, hash-source)
    corpus.py                # the consumed research corpus: window, layout, Decimal-strict loading
    models.py                # source-artefact data structure
    hashing.py               # content addressing
    stats.py                 # shared aggregation numerics
    sources/                 # anti-corruption layer over publishers: elexon, neso, tec_register, archive, pinning
    investigations/          # tested analytical logic, one module per study concept
    rendering/               # the chart palette and SVG tokens; the two public pages; the certificate
    capture/                 # the unattended vintage capture: plan, strategies, stores, witnessing, watchdog, state
    tec/                     # the TEC record engine: cells, importer, replay, identity, analysis, certificates
archives/                    # committed schema reports of the archives the readers are declared against
morpholog/                   # the governed research record (see morpholog/README.md)
tec/                         # the TEC register as its own governed record (see tec/README.md)
ops/                         # deployment design, AWS bootstrap, git hooks, systemd units for the watchdog
trust/tsa/                   # the RFC 3161 roots proofs are verified against
investigations/              # one directory per investigation or method study:
                             #   pre-declaration, runner scripts, committed evidence
publications/                # publication packs rendered from committed evidence only
scripts/
    check                    # the authoritative local gate (lint, types, tests, rule map, proofs, Morpholog)
    freeze                   # witness a declaration and commit it with its proofs
    timestamp, verify-timestamp, verify-proofs, check-rules, schema-report
    install-morpholog        # pinned, checksum-verified installer
    replay-research          # rebuild + verify the governed record from the repo alone
    check-controls           # negative tests: prove the record's locks lock
    record                   # the one safe way to extend the governed record
data/
    raw/                     # ignored; immutable content-addressed source downloads
    derived/                 # ignored; reproducible computed tables
```

## Research so far

The corpus week 2026-08-04..2026-08-10 is complete and published:

- **Investigation 001** selected, by a pre-declared deterministic rule,
  the week's largest apparent price inversion — and explained it (the
  "cheaper" unit had zero deliverable volume).
- **Method Studies 001/001B/001C/001D** then measured the naive
  price-only reading of the same corpus: 3,856,031 apparent inversions;
  every one of the naive screen's top 1,000 led by a physically
  impossible alternative; 90.5% of its £607.8m apparent notional gone
  after one deliverability check; agreement with NESO's own skip
  methodology raised from 35% to 65%; and the entire remaining
  disagreement attributed through the operator's published operational
  data — **zero unexplained cases in the week**. See
  `publications/001/` for the publication pack, and each study's
  directory for its pre-declaration, evidence and note.

Every hypothesis was registered before its data was touched, every
claim is bound to pinned evidence, and the governed record replays and
verifies from this repository alone (`./scripts/replay-research`).

## Publishing format

Every LinkedIn/public post should aim for three layers:

**The mystery** — one sentence a general reader understands.

**The evidence** — one chart and the minimum reconstruction supporting the question.

**Expert corner** — exact settlement period/BMU identifiers, source artefacts, assumptions and the question practitioners can falsify.

A good result can be "explained". A better result can be "I was wrong; here is the missing mechanism". The most interesting result is a pattern that survives repeated attempts to explain it away.

## The Balancing Bill (public page)

Investigation 013, *the cover price tracker*, has a public face: **The
Balancing Bill** (*who got paid to keep Britain's grid balanced, day by day*).
The name is public only; the investigation's id, folder, declaration and
evidence paths are unchanged. The page is `site/index.html`, generated by
`investigations/013-the-cover-price-tracker/run.py --phase render` as a pure
function of `evidence/tracker.json`, self-contained (inline CSS, no script,
no external assets) and committed. `render.yaml` describes the Render static
site: publish directory `site/`, no build step, automatic deploys off, so a
deploy is a deliberate act. Custom domain **balancingbill.a115.co.uk**; the
DNS record (CNAME to the Render service) is added on our side, and the domain
is listed in `render.yaml` so Render issues its certificate once it resolves.

## GB Connection Slippage (public page)

Investigation 014 publishes a second page from the same static site:
**GB Connection Slippage** (*how far Britain's contracted grid-connection
dates have moved, in megawatt-years*), at `site/connection-slippage/index.html`,
generated by `investigations/014-gb-connection-slippage/run.py --phase render`
as a pure function of `evidence/v2/` (append-only rows and a summary). Two
declarations exist: version 1 is kept as run, version 2 restates the reading
under a partial-export rule; each is witnessed by OpenTimestamps and two
RFC 3161 authorities at its freeze (`scripts/freeze`, verified offline by
`scripts/verify-proofs` against the roots in `trust/tsa/`). The series is
computed from the archive of TEC Register copies under
`data/raw/neso/tec-history/` (local, journalled, digest-pinned; its schema
report is under `archives/tec-register/`), which NESO's own portal cannot
reproduce because it publishes only the latest copy; from 2026-09-15 the
capture job in `ops/VINTAGE-CAPTURE.md` keeps that archive current.

## Data policy

Do not commit bulk source datasets. Store raw responses locally as immutable content-addressed files and commit only small fixtures where licensing permits. An investigation manifest should carry URLs/dataset identifiers, publication/fetch timestamps and SHA-256 digests so another researcher can retrieve and compare the source material.

## Licence

MIT. Source data remains subject to the terms of its original publisher.
