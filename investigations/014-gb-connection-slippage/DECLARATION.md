# 014 — GB Connection Slippage: declaration

**Frozen**: 2026-09-15, before any megawatt-year figure was computed from
the archive. Sealed by the commit that adds this file; its SHA-256 is
witnessed by OpenTimestamps and by RFC 3161 tokens from two authorities
(proofs beside this file) before the first run, and is recorded in
`evidence/series.json` and `evidence/run-log.json` by every run. Rows go in
`evidence/series.json`, `SERIES.md` and `site/connection-slippage/index.html`;
amendments, if any, in `AMENDMENTS.md`, dated. An amended rule applies from
the next vintage forward and never restates a row it learned from; a
restated history is a new declaration published beside this one, never a
replacement. The sponsor's seal for this instrument is the instruction of
2026-09-15 ("seal, run, and leave the results unpublished for review");
release is a separate, second seal.

## What this is

A **standing public series**, in the shape of 013 (one page, a pure
function of committed evidence, rows appended on a schedule and never
edited). It was opened on the sponsor's instruction of 2026-09-15 (the
evidence-subcontractor plan of that date), which overrides the
next-milestone note's default that no new investigation opens, and says so.

The number is **GB connection slippage in megawatt-years**: for every
project-stage present in both a baseline copy of NESO's TEC Register and a
later copy, its capacity times the movement of its published target date
in years, summed. It cannot be reproduced from the register NESO publishes
today, because NESO publishes only the latest copy; it can be reproduced
from the copies this project holds, which are listed with digests.

## The mystery

> How far do Britain's contracted grid-connection dates move, in aggregate,
> once the projects that join, leave or change size are set aside?

## Prior exposure (recorded, not hidden)

1. Investigation 005 (2026-08-26) and 006 assembled the archive this series
   reads and published aggregates from it (net slip quantiles, the Q1–Q3
   verdicts, cohort tables, a per-project metrics table). Nothing in 005 is
   a megawatt-year figure. This declaration's author read 005's RESULTS,
   AMENDMENTS and per-project metrics table before writing this file, the
   last of them to choose a project for the certificate exemplar (a
   factual record, not a finding of this series).
2. To write the reading rules below, the author inspected the archive's
   column vocabularies and the spellings and formats of its date and
   capacity cells, and counted, per copy, how many dates disagreed with the
   previous copy and how many of those disagreements a day-month exchange
   explained. No capacity-weighted movement was computed. The findings that
   shaped the rules: 005's runner never mapped the stage-capacity column
   and left `YYYY/MM/DD`, `DD-Mon-YY` and Excel-serial dates unparsed
   (those cells were undated in 005); three copies (2021-01-29, 2021-02-19,
   2022-03-11) carry date cells with day and month exchanged; one copy
   (2024-04-02) carries dates as raw serial numbers; four copies lack an
   identity column (2020-07-09, 2020-07-16, 2020-07-23, 2021-06-22); 32
   early-2014 `.xls` files do not parse. These are recorded for 005 as a
   correction candidate and are **not** applied to 005's published figures
   retroactively.
3. No copy of the register dated after 2026-08-25 has been read from this
   repository before this file was frozen.

## Inputs

The journalled archive under `data/raw/neso/tec-history/` (`journal.ndjson`:
751 rows, one duplicate marked, 731 distinct publication dates, 2014-01-31
to 2026-08-25), assembled by 005 from NESO's EIR disclosures (FOI-24-0040
for 2014–2020, FOI-24-0031 for 2021 to January 2025, FOI-25-129 for April
and July 2025, FOI-26-051 for 19 May 2026), Wayback Machine captures of the
data-portal resource, and live fetches of the resource (CKAN
`17becbab-e3e8-473f-b303-3806f43a6a10`). Each copy's publication date basis
and SHA-256 are in the journal and are copied to
`evidence/vintage-manifest.json` by every run.

**The hole.** No copy is held between **2025-07-22 and 2026-05-19** (301
days), the connections-reform re-baselining period. An EIR request for the
copies in that interval (005's `EIR-REQUEST-TEC-2025-26.md`) is ready to
send and unsent at freeze. When it is answered, its copies enter the archive
as new journal rows and the series is recomputed under this declaration;
they fall inside the regime break below, so they cannot change any row of
the old-regime series.

**The regime break.** Copies dated **2025-12-01 or later** carry dates
re-baselined by the reform (Gate 2 offers, `Gate` column from November
2025). They form a **separate segment**, compared copy to copy from its own
first copy, and are never chained to, or compared with, any earlier copy.
This is what 005 did in excluding them from Q1–Q3.

**New copies.** Each run pins the live resource as a new copy when its
`last_modified` date is not yet journalled (`run.py --phase fetch`, under
the seal), so the reformed-regime segment grows from now on. Runs happen
when invoked, and unattended once the capture job of the deployment note
(2026-09-15) exists; there are no batch seals (Amendment 1 of that note).

## Reading rules

1. **One copy per publication date.** A journal row marked as a duplicate
   is ignored; where two files claim one date, the one with more rows is
   used. Every file is verified against its journalled SHA-256 before it is
   read; a mismatch stops the run.
2. **Columns** are mapped by name to one vocabulary: project name, customer
   name, connection site, stage, `MW Connected`, `MW Increase / Decrease`
   (2014 spellings `Mw Increase/Decrease` and `MW Increase Decrease`),
   `Cumulative Total Capacity (MW)` (2014–2020 `MW Total`), `MW Effective
   From` (2014 `TEC Effective from Date`, 2014–2020 `MW Effective Date`),
   project status, agreement type, host TO, plant type, project ID, project
   number, gate. A copy lacking any of **project name, customer name,
   connection site, `MW Increase / Decrease` or `MW Effective From`** is
   excluded and listed. A file that does not parse is listed, not guessed.
3. **Dates** are read from spreadsheet date cells, `YYYY-MM-DD`,
   `YYYY/MM/DD`, `DD/MM/YYYY`, `DD-Mon-YY` (years 2000–2099) and Excel
   serial numbers (as numbers, or five-digit strings). Anything else is
   undated.
4. **Day-month swap test**, per copy, against the previous usable copy of
   the same segment: over units present in both with a date on both sides,
   count disagreements, and among them those whose current date equals the
   previous date with day and month exchanged. If at least **3** are so
   explained and they are at least **half** of all disagreements, the copy
   is read with every ambiguous date (day ≤ 12, day ≠ month) exchanged.
   The counts and the flag are published for every copy.
5. **Stage** numerals are unified (`1`, `1.0`, `1.00` are one stage); blank
   stays blank. Capacity cells are read as decimals; text is never coerced.

## The unit

**(identity, stage)**, 005 Amendment 1. Identity is the normalised
(project name, customer name, connection site) triple (lower-case
alphanumerics, single spaces), never `Project ID` (005 found it unstable
across eras). Stage is the register's stage where one row per identity or
every row's stage is distinct; otherwise an identity's rows are ordered by
effective date then cumulative capacity and numbered. Splits and merges are
never repaired: a change of customer name or site string is a removal and
a new entry, and is reported as such.

## The headline, defined

For a baseline copy *B* and a current copy *C*, over every unit present in
both **with a parseable date in both**:

    movement(unit) = |MW_B| × (date_C − date_B in days) / 365.25

summed over units, in **megawatt-years**, later positive. `MW_B` is the
unit's `MW Increase / Decrease` **in the baseline copy**, so a change of
capacity never enters the headline; a unit whose baseline capacity is blank
or zero is counted as *unweighted* and contributes nothing. The two gross
sides (moved later, moved earlier) are each quantised to 0.001 MW-years and
the net is their sum. Rows report, beside the net: units in *B* and *C*;
matched; dated on both sides; undated; unweighted; counts moved later,
earlier and unchanged; the capacity summed over the weighted units; and the
**reconciliation items** — new entries (count, MW at *C*), removals (count,
MW at *B*), capacity changes among matched units (count, net MW). They are
published next to the headline and never inside it. Two identities hold by
construction: units(*B*) = matched + removed; units(*C*) = matched + new.

**Baselines.** Every usable copy *C* is compared with (a) the **previous
usable copy** of its segment (the increment), and (b) the **latest usable
copy at least 365 days before it** in the same segment (the trailing year).
**The headline of the series at any copy is (b).** The increments are also
summed from the segment's first copy as a chained total, published as a
second line and labelled as a chain (it counts a unit while it is present in
two consecutive copies, so it survives renames better and mixes populations
across time). **Calendar-year windows** (the first copy on or after 1
January to the first copy on or after the next 1 January; the last year
closes on the segment's last copy and is marked partial) are the page's
year-by-year table, computed by the same rule.

**Gaps.** Any interval of more than 60 days between consecutive usable
copies is listed as a hole; the regime break is listed separately.

## Propositions, declared before the run

- **P1 (direction, old regime).** In every complete calendar-year window of
  the old-regime segment, the net movement is **positive** (later). 005
  found that a fifth of project-stages slip two years or more and advances
  are rare; P1 says that holds in aggregate for every year 2015–2024. It is
  decided by the first run: it holds if every complete window is positive,
  fails on the first window that is not, and the failing years are named.
- **P2 (direction, reformed regime).** Over the reformed-regime segment,
  the chained net movement from its first copy (2026-05-19) to the first
  copy at least 365 days later is **positive**. Falsifier date
  **2027-06-30**: if no copy 365 days after 2026-05-19 exists by then, P2
  is reported as undecided, which is itself a finding about the archive.

Neither proposition is a forecast of any project's energisation; both are
claims about the published register's aggregate behaviour.

## Falsifiers of the instrument

- **F0** The swap test flags a copy in the reformed-regime segment: the
  export artefact persists, and the flag is reported on the page.
- **F1** Between consecutive usable copies, removals plus new entries exceed
  **20 %** of the baseline's units: the identity rule is failing on that
  link, and the link is listed as such on the page before its figures.
- **F2** For a trailing-year comparison, matched units are fewer than
  **half** of the baseline's units: the headline population is thin, and the
  row says so; the figure is published, not suppressed.
- **F3** A committed row changes on recompute from the same bytes: the run
  refuses, and the cause is recorded as an amendment before any rerun.

## Outputs

- `evidence/series.json`: every usable copy's row (digest, unit counts,
  the swap test, both comparisons, the chained total), the annual windows,
  holes, the regime break, the headline, the declaration digest and its
  external timestamps, the run date and time.
- `evidence/vintage-manifest.json`: every usable copy with source, URL,
  publication basis, bytes and SHA-256.
- `evidence/run-log.json`: one line per run (date, seal, declaration
  digest, copies, latest copy).
- `SERIES.md` and `site/connection-slippage/index.html`: pure functions of
  `evidence/series.json`, rendered by `run.py --phase render`.

## What this never claims

- Why any date moved: network works, consents, the developer, NESO
  administration and reform are indistinguishable here (005 F-1 stands).
- Whether any project will connect, or when; nothing here is a forecast.
- Anything about entitlement, breach, or the conduct of any party.
- That a removal is attrition: identity churn, transfer to the embedded
  register and renaming are all removals (005 F-3).
- That the headline is a cost: megawatt-years are a measure of published
  movement, not money.

## Limits declared in advance

The archive is twice-weekly through 2021–2024 and sparser before and after;
a trailing-year comparison's baseline can sit up to 60 days before the
nominal year, and the row names it. Identity churn is large (005: 5,498 of
7,778 project-stages vanish before the last copy), so the year-on-year
population is a fraction of the register, and the reconciliation items say
how large. Stage capacity is the register's own figure and can be revised;
the baseline copy's figure weighs. NESO's caveat that project status is its
best-known classification applies to every column read. The certificate
exemplar built beside this series (`certificates/`) tracks a project by
name and stage, not by the full identity, and says so in its own method
paragraph; its rule is not this series' rule.
