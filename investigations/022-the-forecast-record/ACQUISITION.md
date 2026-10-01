# 022 — The Forecast Record, issue 1: the acquisition and schema pass (the sealable plan)

**Status: a draft for the sponsor's eye, written 2026-10-01, not frozen,
nothing fetched.** The fetch runs only after the sponsor's word. On that
word this file is frozen by `scripts/freeze` (OpenTimestamps and RFC 3161
witnesses, committed with its proofs) and the seal for the runner is a
prefix of its SHA-256 as frozen; `run.py` refuses `index` and `acquire`
without the seal, without the proof sidecar, or if the bytes have changed
since the freeze. Opened on the sponsor's instruction of 2026-10-01
(etrmbiz handover note
`notes/2026-10-01-grid-mysteries-prompt-forecast-record-issue-1.md`),
which overrides the next-milestone note's default that no new
investigation opens, and says so. Nothing goes outside the repository
until the sponsor has read `FINDINGS.md` and a host conversation has
started.

This file is the first of the three named steps, in the repository's
order: **the schema pass** (this plan, gated by the seal, computing
nothing), then **the freeze** (`DECLARATION.md`, written against the
schema report it cites by digest, witnessed before any figure), then
**results** (a runner that refuses to change a committed row). A reading
rule cannot be written without looking at the formats, so the look is
this declared step with its committed artefact, not a private glance.

## The mystery

> Battery revenue forecasts move hundreds of millions of pounds of fund
> value, and nobody has ever published how accurate they were.

Issue 1 scores every public GB battery revenue forecast headline against
the published realised figure for the period it covered. This plan pins
the corpus and reports its shape; it scores nothing.

## Prior exposure (recorded, not hidden)

1. **The model that drafted this file** carries training memory, to
   mid-2026, of Modo Energy's public writing, including the general level
   of its published forecasts and index figures. No figure from that
   memory is written anywhere in this repository, no page was chosen by
   it, and the propositions under test were given by the sponsor, not
   derived from it. It is recorded so a reader can weigh it, as 016's rule
   has it: a model is a proposer here, never a source.
2. **F002's kill C5** (`investigations/forward/F002-batch/KILL-C5.md`,
   August 2026) recorded, from Modo's own public account, that its GB
   battery index is FCA-authorised as a benchmark underpinning
   fixed-for-floating revenue swaps, that the Leaderboard began in
   January 2020, and that over 90 % of GB batteries are owned or operated
   by Modo users. No revenue figure was recorded there.
3. **The sponsor's instruction** illustrates the right size of page with
   the sentence "two of nine vintages are scorable today and both
   overstated the first year by about a fifth". That is an illustration
   of size, recorded here as the sponsor's prior, not a figure read from
   any page.
4. **Entry points probed on 2026-10-01 by HTTP HEAD only** (status code
   and final URL; no body was read, no research page was requested):
   `https://modoenergy.com/robots.txt` 200; `https://modoenergy.com/sitemap.xml`
   200, served as `application/xml`; `https://www.investegate.co.uk/company/GRID`
   200; `https://greshamhouse.com/real-assets/new-energy/gresham-house-energy-storage-fund-plc/`
   200 after a redirect to
   `https://greshamhouse.com/real-assets/energy-transition-investment/gresham-house-energy-storage-fund-plc/`;
   `https://www.londonstockexchange.com/stock/GRID/gresham-house-energy-storage-fund-plc/analysis`
   200. `https://www.investegate.co.uk/companies/GRID` 404 and is not used.
5. Nothing from Modo Energy and no RNS document has been pinned, opened
   or read under this investigation before this file is frozen.

## The corpus

### The forecast side: Modo Energy's public pages

- **A1, discovery from the site's own sitemap.** The runner pins
  `https://modoenergy.com/robots.txt`, follows every `Sitemap:` line it
  carries, pins each sitemap, follows a sitemap index to its children and
  pins those, and takes the union of every `urlset` entry (URL and
  `lastmod` as printed) as the universe of pages. If robots.txt names no
  sitemap, `https://modoenergy.com/sitemap.xml` is used and the fallback
  is recorded. Every pinned sitemap is journalled with its digest, so the
  universe is reproducible from pinned bytes alone.
- **A2, selection by token, every URL listed with its reason.** A URL is
  selected when its path, lower-cased, contains one of `forecast`,
  `revenue`, `index`, `benchmark`, `outlook` (the first in that order is
  the recorded reason); a URL ending in an image, font, stylesheet or
  script extension is never selected. **Every** URL of the universe is
  written to `evidence/run-index.json` with `selected` and the reason, so
  what was not pinned is as visible as what was. The token list is
  deliberately inclusive: pinning a public page that turns out irrelevant
  costs nothing, while a forecast page missed is a false negative the
  record cannot see. No date filter is applied at discovery: a sitemap's
  `lastmod` is a modification date, not a publication date, and "since
  2023" is a reading rule for the declaration, applied to the publication
  date each page declares (S1), not to the sitemap.
- **A3, pinning.** Each selected URL is requested once with an anonymous
  client (`GET`, redirects followed, no cookie, no credential, no key)
  whose user agent names this project, and the bytes served are written
  to `data/raw/modo/022/pages/<path>.html` and journalled with their
  SHA-256 the moment they land; the manifest derived from the journal is
  committed as `evidence/pages-manifest.json`. A pinned file is never
  overwritten; a second run verifies what is on disk against the journal
  and skips it. A request answered with an error (status 400 or above, a
  timeout, a transport failure) is recorded in
  `evidence/acquisition-log.json` with the URL and the error, is not
  retried in the same run, and is retried by the next run. Half a second
  separates requests.
- **A4, never from paid pages.** No login, subscription, cookie or key is
  used, so what is pinned is exactly what Modo Energy serves to anyone.
  A page whose served text carries a paywall-looking token (S3) is
  flagged in the schema report; a figure that appears in the served text
  is public by construction, and whether a flagged page's figures are
  read is a reading rule for the declaration.
- **A6, robots.txt is honoured.** A selected URL whose path falls under a
  `Disallow:` rule for `User-agent: *` is listed in the index as "not
  fetched: disallowed by robots.txt" and is not requested.

### The realised side

- **A5(i), Modo's own index pages** are part of the same selection (the
  token `index`, and `revenue` for annual reviews); nothing further is
  needed to pin them. Which of them carry a fleet or by-duration realised
  figure, in pounds per megawatt per year, for a stated period, is what
  the schema pass makes visible.
- **A5(ii), the listed fund's reported figures from RNS.** The runner
  pins two listing pages as served, `https://www.investegate.co.uk/company/GRID`
  and the Gresham House Energy Storage Fund page named in prior exposure
  4 (its redirected URL), and lists every anchor on them whose visible
  text matches, case-insensitively,
  `(annual|final|full[- ]year|interim|half[- ]year(ly)?)\b.*\b(results|report)`,
  as (absolute URL, text) in `evidence/run-index.json`; `acquire` pins
  every listed document to `data/raw/rns/022/`, journalled, manifest
  committed as `evidence/rns-manifest.json`. The sponsor's instruction
  names the fund's FY2024 and FY2025 annual results and its H1 2026
  interim results as public; if a listing page as served does not carry
  them (a paginated or client-rendered listing is the expected cause),
  the index records what it did carry and an amendment to this plan
  names the direct URLs. No document URL is guessed into this plan.

## The schema pass: what is recorded, and that nothing is computed

Run by `scripts/schema-report modo-022` (`run.py --phase schema`) over
the journalled bytes after each digest is checked; written to
`archives/modo-pages-022/` and `archives/rns-grid-022/` (`SCHEMA.md` and
`schema-report.json`) and committed, so that the declaration can cite the
report's digest.

- **S1, per page**: URL, path, SHA-256, bytes, the title, every date-like
  declaration the page makes about itself (`<meta>` published and
  modified times, JSON-LD `datePublished` and `dateModified`, `<time
  datetime>`), as printed and by where it was found, and the length of
  the page's text. Which of those is the publication date is a reading
  rule, declared later against this tally.
- **S2, every figure-looking string, as printed, with its sentence.** The
  pattern is a pound sign, a number with optional thousands separators
  and decimals, an optional `k`, `m` or `bn`, an optional range, then
  "per MW" or "per kW" (or MWh, kWh) in slash or word form, with an
  optional "per year" in any of its spellings (`/year`, `/yr`, `per
  annum`, `/a`, and `/month`), matched case-insensitively on the page's
  text with tags stripped, entities unescaped and JSON payloads kept as
  text (a client-rendered page carries its content in `__NEXT_DATA__`
  or JSON-LD). Each match is recorded as the string printed, its
  spelling with every digit run replaced by `9`, its offset, the
  sentence it sits in (bounded by sentence punctuation or the end of a
  block element), and the duration, basis, horizon and year tokens that
  sentence uses, counted. **No string is parsed to a number, no scope,
  basis or period is assigned, and no figure is computed.** Spellings are
  tallied across pages so the reading rule can be written against the
  spellings in use.
- **S3, per page tallies** of duration tokens (`1-hour`, `one-hour`,
  `1h`, `2-hour`, `two-hour`, `2h`, `4-hour`, `8-hour` and their
  variants), basis tokens (`forecast`, `projection`, `outlook`, `index`,
  `realised`, `realized`, `actual`, `outturn`, `potential`, `benchmark`,
  `leaderboard`, `fleet`, `average`, `typical`), horizon tokens (`full
  forecast horizon`, `decade`, `long-term`, `annual`, `monthly`),
  paywall-looking tokens (`subscribe`, `subscriber`, `log in`, `sign in`,
  `paywall`, `premium`, `members only`, `unlock`, `free trial`, `request
  a demo`) and the calendar years 2020 to 2059 mentioned.
- **S4, flags**: a page declaring no date, a page with no figure-looking
  string, a page with under 500 characters of text (a redirect stub or a
  wall).
- **S5, the scope of the pass**, stated for the declaration to cite: the
  pages are those `evidence/pages-manifest.json` and
  `evidence/rns-manifest.json` list, each hashed to its journalled
  digest; a page that fails that check refuses the pass.

## What this plan does not do

It reads no figure, assigns no scope, basis or period, scores nothing,
ranks no page, names no optimiser and writes no `DECLARATION.md`. The
scoring rules the sponsor's instruction states (scorability, the signed
and absolute error, the scope-mismatch rule, the propositions P-A, P-B
and P-C) are implemented as pure functions with tests
(`src/grid_mysteries/investigations/forecast_record.py`,
`tests/test_forecast_record.py`, mapped in `evidence/rule-sources.json`)
so that the declaration can cite them; they run on no data until the
declaration is frozen, and the reading rule that turns a printed string
into a figure does not exist until the schema report does.

## Outputs of this step

- `evidence/run-index.json`: the plan's digest and the seal, every
  sitemap pinned, every URL with its selection and reason, the robots
  rules applied, the RNS listings and the links they carried, failures.
- `evidence/discovery-manifest.json`, `evidence/pages-manifest.json`,
  `evidence/rns-manifest.json`: every pinned artefact with URL, path,
  SHA-256, bytes and fetch time (journals stay local by the repository's
  rule; a manifest is content-identical to its journal).
- `evidence/acquisition-log.json`: each phase run, under which plan
  digest and seal, with what failed.
- `archives/modo-pages-022/` and `archives/rns-grid-022/`: the schema
  reports.

## The seal

The sponsor's seal is a prefix of at least eight hexadecimal characters
of this file's SHA-256 as frozen. The runner checks the prefix, the
presence of `ACQUISITION.md.timestamps.json`, and that the sidecar's
digest is this file's digest now. A change to this plan after the freeze
is an amendment (`AMENDMENTS.md`, frozen in turn), never an edit.
