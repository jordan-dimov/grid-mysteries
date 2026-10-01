# 022 — The Forecast Record, issue 1: declaration (draft, not frozen)

**Status: a draft written 2026-10-01 before the schema pass; not frozen,
no figure computed, nothing fetched.** This file is frozen with
`scripts/freeze` only after `ACQUISITION.md` has been sealed and run and
the schema reports exist, because its reading rules (R-R) are written
against those reports and cite them by digest; a declaration written
against an archive with no schema report is guessed, not frozen. The
sections marked **[after the schema pass]** are empty on purpose. The
sponsor's seal for `compute` is the digest prefix of this file as frozen.
Nothing goes outside the repository until the sponsor has read
`FINDINGS.md` and a host conversation has started.

## The mystery

> Battery revenue forecasts move hundreds of millions of pounds of fund
> value, and nobody has ever published how accurate they were.

This investigation scores every public GB battery revenue forecast
headline against the published realised figure for the period it
covered, under rules fixed before any number is read. It attributes no
error to any cause, names no optimiser, and never says "wrong": a
forecast is **overstated by** or **understated by** a stated amount, as
published by its publisher on a stated date, against an outturn as
published on a stated date.

## Prior exposure

`ACQUISITION.md`, "Prior exposure", items 1 to 5, stand here in full.
**[after the schema pass]** the tallies of the schema reports (spellings,
tokens, dates, flags) will have been read to write R-R; no figure will
have been parsed from any string before this file is frozen, and that is
stated here with the reports' digests.

## Vocabulary

- **Forecast**: a published headline figure, in pounds per megawatt per
  year, for a stated future period, as the page printed it. Basis
  `forecast`.
- **Outturn** (the realised figure): a published realised figure, in
  pounds per megawatt per year, for a stated past period, as the page
  printed it. Basis `realised`. A figure a page calls potential,
  benchmark-potential or achievable is basis `potential` and is never an
  outturn.
- **Vintage**: one publication: (publisher, publication date, page URL).
  A page carries one vintage and may carry several figures.
- **Scope**: the population a figure describes: `fleet` (the whole GB
  fleet or the index), a duration (`1h`, `2h`, `4h`, `8h`, as the page
  printed it), or a named portfolio (the listed fund's own assets).
- **Period**: the calendar years a figure covers, inclusive. A figure for
  one year has a period of one year; "across the full forecast horizon"
  is the period the page states for the horizon, or no period if the
  page states none.
- **Publisher**: Modo Energy, or the listed fund as named in its RNS.

## Inputs **[after the schema pass]**

- The pages: `evidence/pages-manifest.json` (SHA-256 to be cited) and
  `evidence/rns-manifest.json` (SHA-256 to be cited), every artefact
  hashed to its manifest before anything is read (C1).
- The schema reports: `archives/modo-pages-022/schema-report.json`
  (SHA-256 to be cited) and `archives/rns-grid-022/schema-report.json`
  (SHA-256 to be cited), with the facts cited from each.

## Reading rules **[after the schema pass]**

Written against the spellings and date fields the schema reports show,
each with a test. They must fix, and only these:

- **R-R1, the publication date**: which declared date field is the
  publication date, in which order of precedence, and that a page
  declaring none is listed and not read.
- **R-R2, the figure**: how a printed string becomes a Decimal in pounds
  per megawatt per year (the `k` multiplier; `/kW/year` times a thousand;
  a `per month` figure times twelve only if the page states it as a
  monthly rate, else not read; a **range** is listed as a range and is
  never read as a point figure; a figure with no "per year" is read only
  if its sentence states the year it covers, else not read).
- **R-R3, scope** from the sentence and the page: a duration token in the
  sentence gives the duration scope; `fleet`, `index` or `average` with
  no duration gives `fleet`; a sentence with two durations is not read;
  a fund's own figure is its named portfolio.
- **R-R4, basis** from the sentence and the page: `forecast`,
  `projection`, `outlook` or a future period give `forecast`; `index`,
  `earned`, `realised`, `actual`, `outturn` or a past period give
  `realised`; `potential` or `benchmark` give `potential`; a conflict is
  not read.
- **R-R5, the period** from the sentence: the calendar year or years it
  names; a sentence naming none is "period not stated" and is not
  scored; a horizon named only as "to 2030" from a page published in
  year Y is the period Y+1 to 2030.
- **R-R6, since 2023**: a page whose publication date is before
  2023-01-01 is listed and not read. A page flagged paywall-looking is
  read like any other, because the text served to an anonymous client is
  public (A4); the flag is printed beside its figures.
- **R-R7, every unread string is listed** with the rule that declined it,
  so the share read is a published number (F2).

## Scorability (R-S), the comparison (R-C), the mismatch (R-M), the revisions (R-V)

Implemented in `src/grid_mysteries/investigations/forecast_record.py`;
each with a test named in `evidence/rule-sources.json`.

- **R-S1** A horizon year counts only if the forecast was published
  before the year began; a figure for the year of its own publication is
  **in-year** and is never scored, listed as such.
- **R-S2** A forecast figure is **scorable** when every year of its period
  is eligible under R-S1 and has a realised figure of the **same scope**
  (basis `realised`, period one year). A one-year figure is scored
  against that year's realised figure; a multi-year figure against the
  mean of its years' realised figures, quantised to the pound, and the
  row says so.
- **R-S3** Where several realised figures exist for one scope and year,
  the latest published is read (it supersedes); the earlier ones are
  named beside it.
- **R-C** For a scorable figure: signed error = forecast − realised, in
  pounds per megawatt per year quantised to the pound, and as a
  percentage of the realised figure quantised to 0.1; absolute error is
  its magnitude. One row per forecast figure, per vintage, per period.
- **R-M** A forecast figure with no realised figure of its own scope for
  its years, but with realised figures of another scope covering them
  (a fleet outturn against a duration-specific forecast, or a fund's
  portfolio outturn against a fleet forecast), is a **scope mismatch**:
  the row lists both figures and both scopes and carries **no error**.
  Nothing is ever adjusted from one scope to another.
- **Not yet scorable** is a result: each forecast figure with no realised
  counterpart yet is listed with the date it becomes scorable (the first
  day after its period ends, or today if the period has ended and no
  figure has been published).
- **R-V** For one publisher, consecutive vintages that both print a
  forecast for the same scope and period are a revision pair, the later
  value against the earlier: down, up or unchanged. Every forecast figure
  takes part, scorable or not; one figure per vintage per key is read
  (the first by id) and duplicates on a page are listed.

## Propositions, judged before the first compute

Each is decided on the scored rows only, and is **undecided** when no
vintage is scorable (P-A, P-B) or no revision pair exists (P-C).

- **P-A (every vintage overstated its first realised year).** Every
  scorable vintage has a positive signed error in every scored row of
  its first realised year. *Falsified* by one scorable vintage whose
  first realised year is understated, exact, or mixed across scopes.
- **P-B (the nearest-year error exceeds a fifth in most vintages).** In
  more than half of the scorable vintages, the absolute error in
  **every** scored row of the first realised year exceeds 20.0 % of the
  realised figure. A vintage mixed across scopes counts as not
  exceeding. *Falsified* when the exceeding vintages are half or fewer.
- **P-C (revisions ran downward).** Over every revision pair, down
  outnumbers up. *Falsified* when up equals or exceeds down.

## Falsifiers of the instrument

- **F1** No vintage is scorable: the page is the not-yet-scorable table,
  published as the result of issue 1, with the dates each vintage becomes
  scorable; P-A and P-B are undecided and say so.
- **F2** The reading rules read fewer than half of the figure-looking
  strings on pages whose basis tokens are forecast-dominant: the corpus is
  **not determinable** under these rules; the unread strings are
  published with the rule that declined each, and no proposition is
  judged.
- **F3** A committed row of `evidence/figures.ndjson`,
  `evidence/comparisons.ndjson` or `evidence/revisions.ndjson` would change
  on recompute under the same rule version: the run refuses. There is no
  `--amend`; a changed figure is a new declaration beside this one, and a
  row is recorded once per rule version (the kill test of 2026-09-25,
  `bill/KILL-TEST.md`).
- **F4** The realised side restates itself (a later page prints a
  different realised figure for the same scope and year): R-S3 reads the
  latest and the restatement is a published row of its own; a
  restatement larger than 10 % of the earlier figure is named in
  `FINDINGS.md` beside every comparison that depends on it.

## Checks the runner makes before and after computing

- **C1** Every artefact in the manifests hashes to its recorded digest;
  the schema reports on disk hash to the digests cited above.
- **C2** Every figure row names its page's digest, the string as printed,
  and the rule that read it; every unread string names the rule that
  declined it (R-R7).
- **C3** The count of scored, mismatched, not-yet-scorable and in-year
  rows equals the count of forecast figures.
- **C4** No row carries a figure of basis `potential` as an outturn.

A failed check refuses the run and is recorded in `AMENDMENTS.md` before
any rerun; nothing is written.

## Outputs

- `evidence/figures.ndjson`: one line per figure read (and per string
  declined, with its rule), append-only, carrying `rule_version` (this
  file's SHA-256 prefix), the page digest and the string as printed.
- `evidence/comparisons.ndjson`: one line per forecast figure, with its
  status and, where scored, the errors; append-only, `rule_version`.
- `evidence/revisions.ndjson`: one line per revision pair; append-only.
- `evidence/summary.json` (rewritten each run): digests, the seal, the
  run date, the propositions with their instances, the not-yet-scorable
  table, F1 to F4.
- `evidence/run-log.json`; `evidence/rule-sources.json`.
- `FINDINGS.md`, a pure function of the evidence (`run.py --phase
  render`): every sentence "as published by Modo Energy on <date>" or
  "as reported by <fund> on <date>"; the not-yet-scorable table as a
  result, not a gap.

## Rules for the page

No optimiser is named. No cause is attributed to any error; in the
spirit of 006's cause split, the page says what moved, not why.
"Forecast" means the published headline; "outturn" means the published
realised figure; never "wrong", only "overstated by" or "understated
by". A page that says "two of nine vintages are scorable today and both
overstated the first year by about a fifth" is the right size for issue
1; the sentence is written from the rows, whatever they say.

## Expert corner

- Every page digest, every string as printed, every rule that read or
  declined it, in `evidence/`.
- **The Benchmarks Regulation note.** This investigation scores
  published headline figures against published realised figures. It
  administers no benchmark, calculates no index, redistributes no index
  level and offers nothing for use in a financial contract; it quotes
  figures as published, with their dates, for the purpose of checking
  them. Modo Energy's own public account (recorded in F002's kill C5)
  is that its GB battery index is FCA-authorised under the UK Benchmarks
  Regulation; nothing here uses, reconstitutes or re-publishes that index
  as a benchmark, and the realised figures read are those Modo and the
  listed fund chose to publish on public pages.
- **What a fund reports is a portfolio, not the fleet** (R-M): a fund's
  revenue per megawatt is scope "its portfolio" and never scores a fleet
  or duration forecast; it is listed beside them as a mismatch row, both
  figures visible.

## What this never claims

That any forecast was wrong, careless or interested; that any error had
a cause; that one publisher's forecasts are better or worse than
another's (one publisher is scored here); that an index level is a
market fact rather than a published figure under its publisher's
methodology; that a fund's reported revenue per megawatt is comparable
to a fleet figure; or that any of this is a forecast of future revenue.

## The record

Git plus external witnesses, as for every forensic investigation from
012 onward: this file with its proofs, `ACQUISITION.md` with its proofs,
the committed evidence with `rule_version` on every row, the schema
reports under `archives/`, and `scripts/check`. No row is proposed to a
Morpholog database by this declaration.
