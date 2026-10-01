# 022 — The Forecast Record, issue 1: declaration (draft, not frozen)

**Status: drafted 2026-10-01 before the schema pass (committed at
`18e5a70`), completed the same evening against the schema reports it
cites below, for the sponsor's reading; not frozen, no comparison
computed.** On the sponsor's word this file is frozen with
`scripts/freeze` (OpenTimestamps and RFC 3161 witnesses, committed with
its proofs) and the seal for `run.py --phase compute` is the digest prefix
of this file as frozen; `compute` refuses without the seal, without the
proof sidecar, or if the bytes have changed since the freeze. The
acquisition plan `ACQUISITION.md` (SHA-256 `962cb9b5db8d33a7ae14fe3b516dd5f999936911040316a4fcc03e8aeeb0e188`, frozen and
sealed `962cb9b5db8d33a7`) and its `AMENDMENT-1.md` (SHA-256 `c39c5f90da09e80ef9e5f6fc6ad4245e817197fb84da498fd9b8910f9f3957b6`,
frozen and run on the sponsor's word of 2026-10-01, evening: the funds'
documents from 2021 as a forecast side) govern what was fetched; this
file governs what is read and computed. Completed a second time, the same
night, after the amendment's schema pass, with the fund rules below. Nothing goes outside the repository until the
sponsor has read `FINDINGS.md` and a host conversation has started.

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
After the schema pass and before this file was completed:

6. **The schema reports were read with every digit masked.** To write
   R-R1 to R-R7 the author read the reports' tallies (spellings, date
   fields, tokens, flags) and the sentences around the figure-looking
   strings on the English pages and the RNS documents **with every digit
   replaced by `9`** (`re.sub(r"\d", "9", …)` over every printed string),
   so that the phrasing could be learned without the values. No figure
   was seen unmasked by the author; the committed reports carry the
   values, as they must.
7. **The reader was dry-run on the masked reports, five times, before
   this file was completed**, printing per rule how many strings it read
   or declined and, for each figure read, its publisher, basis, scope,
   period and publication date (not its value). Those runs showed that
   under these rules the corpus yields **two forecast figures from Modo
   Energy's public pages, neither scorable before 2029-01-01** (one for
   the year of its own publication, one for a horizon that has not
   ended), **five realised annual figures read** (Modo Energy's fleet
   figure for 2023 and, from two pages, for 2024; GSF's 2022 calendar-year
   figure; GRID's 2025 figure), **twelve monthly fleet figures for 2025**
   (so R-S4 yields a 2025 fleet figure) and four months printed
   differently on different pages beyond rounding (F4), so that **F1 will fire,
   P-A and P-B will be undecided, and P-C will be undecided** for want
   of a revision pair. That is known before the freeze and is stated
   here. The propositions are the sponsor's of 2026-10-01 and are not
   changed by it; no comparison, error or revision was computed; the
   not-yet-scorable table is the result of issue 1, as the plan said it
   might be.
8. **After amendment 1, the same night.** The 240 fund documents' schema
   report was read the same way, digits masked, and the reader dry-run on
   it. Those runs showed: the funds' documents add **three cited forecast
   figures** (HEIT's Investment Adviser's revenue assumptions excluding the
   Capacity Market for 2023, the year of their publication, and for 2024,
   published 2023-05-23, scope its portfolio; a third-party forecasters'
   level for two-hour assets for 2028, cited by GRID on 2025-09-24 in an
   RNS and its interim report, one publication under R-R0) and **two
   realised portfolio figures for GRID's 2024** on the documents of
   2025-04-22 (beside GRID's 2025 and GSF's 2022, R-S3 reading the later
   by id and naming the other); that HEIT publishes no calendar-year
   outturn of its own, so its 2024 assumption meets the fleet outturn only
   as a **scope mismatch** (R-M), listed and never adjusted, and its 2023
   assumption is in-year; and therefore that **no vintage is scorable
   today**, as before the amendment. The propositions are unchanged. The fund rules (R-R0's
   furniture and same-day rules, R-R1's RNS header and PDF dates, R-R3's
   portfolio qualifier, R-R4(f), R-R6's 2021 window) were written from
   those masked runs; no scoring rule, proposition or threshold changed.
9. **What the dry runs changed.** Each dry run changed reading rules
   (the clause, the page's month, rounding agreement, the starting point
   of a change, the fund's year from its RNS title), never a scoring
   rule, a proposition or a threshold. Those are listed in the commit
   that completed this file.

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

## Inputs

- **The pages**, pinned under the sealed plan on 2026-10-01 and listed in
  `investigations/022-the-forecast-record/evidence/pages-manifest.json`
  (SHA-256 `fb4ac6aa112ffdae3ebbbfcfdc54786a588ddf8c23c01881cccb630c07f38925`; 2,744 Modo Energy pages) and
  `investigations/022-the-forecast-record/evidence/rns-manifest.json`
  (SHA-256 `4c9b2476d99e97bfaee450293db4f650febbaacaf3f3256daddd0fe4546ad599`; 280 RNS documents and listings, 40 under the plan and 240 under amendment 1), every artefact
  hashed to its manifest before anything is read (C1). The two pages the
  index selected and the site answered 404 are in
  `evidence/acquisition-log.json`, not read.
- **The schema reports this file is written against**, regenerated by
  `scripts/schema-report modo-022` after amendment 1 and committed with this
  file's completion:
  `archives/modo-pages-022/schema-report.json` (SHA-256 `4bbe6d793e97e73777de7e2e3c72dbf53dd33ed1440bf4f68aff1f79ac281ab6`;
  `SCHEMA.md` beside it `415c9724…`) and
  `archives/rns-grid-022/schema-report.json` (SHA-256 `16820033b7b175ea1cf26b0cbd0901442bb88449f93017033a4429221aeba696`;
  `SCHEMA.md` `95add453…`). The runner refuses if either hashes
  differently (C1). Cited from them:
  - every one of the 442 English Modo pages (`/research/en/`) declares
    `meta:article:published_time` and `json:datePublished`, and no page
    declares a `<time datetime>`; the research sitemap carries each
    article under seven language paths (`de`, `en`, `es`, `fr`, `it`,
    `ja`, `pt`) with the same figures in translated spellings
    (`/MW/Jahr`, `/MW/año`, `/MW/anno`, `/MW/年`, `/MW/ano`), so R-R0 reads
    the English path only;
  - the spellings in use: `£9k/MW/year` (378 on the English pages) is the
    per-year form, with `£9k/MW/yr`, `£9k/MW/y`, `£9k per MW per year`,
    `£9/kW/year`, `£9k to £9k/MW/year`; `£9k/MW` and `£9/MW` carry no
    period; `£9/MWh` is a price and `£9/MW/h`, `£9/MW/hr`, `£9/MW/hour` an
    hourly rate; the RNS documents add `£9 per MW/yr`, `£9/MW per year`,
    `£9 / MW / yr`, `£9 per MW per annum`, `£9k/MW per annum`;
  - every English page carries the token `log in` (site chrome), so a
    paywall-looking token says nothing about a page and is not used;
  - 91 of the 442 English pages carry a figure-looking string; the
    monthly index posts (`ME BESS GB: Revenues … in <Month> <Year>`, `GB
    BESS revenues … in <Month> <Year>`, `GB Battery energy storage
    revenues … in <Month>`) carry their month in the title and restate
    the previous month and the year-earlier month in the same sentence;
  - of the 262 HTML RNS pages, 108 (the newer Investegate template)
    declare `json:dateCreated` and 144 print the RNS date as a text line
    within three lines after `RNS Number :` (`D Month YYYY`, recorded as
    `text:rns-header`); the 18 PDFs declare no date in their text and
    carry a `CreationDate` in their metadata (`pdf:CreationDate`, as
    `pdfinfo` prints it); the fund pages on `gsenergystoragefund.com`
    (an interstitial disclaimer) and Investegate's own `investors` page
    declare none;
  - PDFs are now read in `pdftotext`'s reading order (A7(iii)), which
    keeps a sentence whole but glues a page's running headers into it
    (`GRID Annual Report 2024 Strategic report …`), the fact R-R0's
    furniture rule is written against;
  - the funds' documents spell the per-year unit `per MW/Yr`, `per MW per
    year`, `/MW per year`, `per MW per annum`, and the Capacity Market
    auction price `per kW/year`, `/kw/yr`.

## Reading rules, written against the schema reports

Implemented in `read_page`, `periods_in`, `choose_months` and
`annual_from_months` of
`src/grid_mysteries/investigations/forecast_record.py`, each with a test
named in `evidence/rule-sources.json`. Every figure-looking string of the
schema reports is listed in `evidence/figures.ndjson` with the rule that
read or declined it (R-R7), so the share read is a published number.

- **R-R0, which pages and which strings.** Modo Energy's pages under
  `/research/en/` are read; the six other language paths of each article
  are pinned and listed, not read. RNS listings and documents on
  Investegate are read as HTML; a PDF is read from its reading-order text
  (A7(iii)), and a PDF sentence carrying page furniture (`Annual Report`,
  `Interim Report`, `Strategic report`, `Governance`, `Other information`,
  `Investment Manager's review`, `Financial statements`, `Notes to the`)
  is declined. A string whose sentence is a JSON payload (begins `{` or
  carries `":"`), or is the page's title or its navigation echo (`Back …`),
  is declined. A string repeated verbatim in one sentence is read at its
  own place in it. The same figure (publisher, date, basis, scope, period,
  value) printed in two documents of one day, an RNS and its report, is
  one publication: the first by URL is kept and the other listed.
- **R-R1, the publication date**: `meta:article:published_time`, else
  `json:datePublished`, else `json:dateCreated` (the Investegate
  listing's), the first ten characters as an ISO date; else the RNS header
  date the page prints (`D Month YYYY`); else a PDF's `CreationDate`; a
  page declaring none is listed and not read.
- **R-R2, the figure**: the string is parsed as a pound amount, an
  optional `k`, `m` or `bn`, an optional range, a unit (`MW`, `kW`,
  `MWh`, `kWh`) and an optional period (`year`, `yr`, `y`, `annum`;
  `month`; `hour`, `hr`, `h`). `k` multiplies by a thousand; `m` or `bn`
  is declined; `/kW` multiplies by a thousand; `/MWh` and `/kWh` are
  declined (a price); an hourly or monthly rate is declined; a range is
  declined; a string with no period is declined unless its sentence says
  "annualised" or "annualized". A figure is read in whole pounds. A
  **change** is not a level and is declined: `by £`, `rose/fell/up/down/
  increased/decreased/reduced/dropped/rising/subtracting/contributing/
  added/jumped/surged/grew £`, `£X higher/lower/more/less/up/down`, a
  `reduction/uplift/boost/swing/increase/drop/fall/rise/decline of £`,
  `up to £`, `over £`, `more than £`, `exceeded this by`; and the **starting
  point** of a stated change (`from (around) £X to £Y`) is declined, `£Y`
  being the level.
- **R-R3, the population**, read from the figure's **clause** (the text
  between commas, semicolons, colons or spaced dashes around it): a clause
  naming a revenue component (`wholesale`, `balancing mechanism`,
  `frequency response`, `reserve`, `capacity market`, `imbalance`,
  `dynamic containment/regulation/moderation`, `ancillary`, `trading
  revenue`, `merchant markets`, `arbitrage`, `in the service`, `reactive
  power`, `offer dispatch`, `duos`, `tnuos`, `auction`, `clearing price`,
  `cleared at`, `t-4`, `t-1`) is declined, the qualifier "excluding/
  including Capacity Market" excepted; a clause, or the clause before it,
  naming a subset or an asset (`highest-earning`, `top-performing`, `top
  quartile`, `best`, `beat`, `one battery`, `one system`, `some
  batteries`, `four batteries`, `individual batteries`, `upwards of`, the
  asset names `Jamesfield`, `Wishaw`, `Coventry`, `Capenhurst`, `Wormald
  Green`, and the swap vocabulary `basis risk`, `fixed leg`, `floating
  leg`, `swap`, `perfect forecasting`, `would've`, `would have`) is
  declined. A duration in the clause (`1`, `2`, `4`, `8`, `one`, `two`,
  `four`, `eight` with `h`, `hr`, `hour`, `hours`) gives the scope `1h`,
  `2h`, `4h` or `8h`; else the scope is `fleet` when the clause names it
  (`Great Britain`, `GB`, `GB BESS`, `ME BESS`, `index`, `batteries`,
  `battery energy storage`, `battery revenues`, `battery storage
  revenues`, `BESS`, `fleet`, `the benchmark`), or the page is a monthly
  index post, or the sentence names it and carries no component or subset
  word; else the string is declined. "Excluding Capacity Market" in the
  sentence makes the scope `…-excl-cm`, "with/including Capacity Market"
  `…-incl-cm`. A fund's figure has the scope "`<ticker>` portfolio", with
  the same Capacity Market qualifier; a fund citing a curve for a stated
  population ("two-hour assets", "the GB market") names that population,
  not its own portfolio (R-R4(f)).
- **R-R4, the basis**: a sentence with `potential`, `must increase`,
  `required`, `worth`, `toll`, `agreement`, `contract`, `viable`,
  `scenario`, `sensitivity`, `assumed`, `assuming`, `estimate`, `could
  be`, `could generate`, `capex`, `cost`, `valu…`, `minimum` or `floor` is
  declined (potential, required, contracted or assumed). A period in the
  future, or a horizon or end-year form, is a **forecast** and needs a
  forecast word in the sentence (`forecast`, `project`, `outlook`,
  `expect`, `will`, `would`, `out to`, `by 20xx`, `end of 20xx`, `long
  term`, `horizon`), else it is declined; a past calendar year is
  **realised**; the year of publication is a forecast if a forecast word
  is present (in-year, listed by R-S1, never scored), else declined as
  not complete. **R-R4(f), a fund's cited forecast.** On a fund's page, a
  sentence with `assum…`, `forecast`, `projection`, `projected`, `curve`,
  `expected` or `anticipat…` and a future period is a **forecast published
  by the fund**: its publisher is the fund, its scope is as R-R3 reads it,
  and the source the sentence names (`Modo`, `Aurora`, `Baringa`,
  `Cornwall Insight`, `AFRY`, `LCP`, `Timera`, `Energy Aspects`, `BNEF`,
  `third-party`, `independent`) is recorded as `cited_source`, else
  "source unnamed". Such a sentence with a past period is declined (an
  assumption is not an outturn). The potential-words rule does not apply
  to it.
- **R-R5, the period.** Candidates in the sentence: a month with a year
  (not preceded by a day number, so `31 March 2024` is a date, not a
  month); a month alone, read as its most recent occurrence at or before
  the page's month (the title's month on a monthly post, else the
  publication month); an annual form (`in/for all of/across/throughout/
  during/over 2024`, `2024 average`, `2024 revenues`, `the 2024 calendar
  year`, `FY2024`, `average 2024 revenues`); a horizon (`out to/through/
  until/towards/to 2030`: the publication year plus one to 2030); an
  end-year (`by/at the end of/in/for 2030`); and partial markers (`H1`,
  `Q1`, halves, `winter`, `summer`, `so far`, `to date`, `last N months`,
  a month-to-month span, `the period`, `this year`, `last year`). A
  partial marker in the clause, or the clause before it, declines the
  string. Otherwise the candidate **within the clause nearest the
  figure** is read; if the clause names none, a Modo page takes the
  nearest in the sentence, and a fund page takes the financial year from
  the RNS title (`to 31 December YYYY`) when the sentence says `for the
  year`, `during the year`, `the portfolio generated` or `over the year`,
  else declines. A month is a **monthly figure** (R-S4): on a monthly
  index post only the page's own month is read and any other month is
  declined; on another page a month is read only within three months
  before publication; a fund figure dated by a month is declined.
- **R-R6, since 2023, and the funds since 2021** (A7(iv)): a Modo page
  published before 2023-01-01, or a fund document before 2021-01-01, is
  listed and not read. The paywall-looking tokens are not used (every English page
  carries `log in`); a figure in the served text is public (A4).
- **R-R7, agreement and the record of every string.** On a monthly index
  post, the strings read for the page's month must agree to the nearest
  £1,000; the most precisely printed is read (then the latest) and the
  others are declined as less precise; strings differing beyond rounding
  mean none is read from that page. Every string is listed with the rule
  that read or declined it.

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
  a figure published for the year outranks a twelve-month mean (R-S4),
  then the latest published is read (it supersedes); the others are named
  beside it.
- **R-S4, the realised year from twelve months.** For each scope and
  calendar year in which all twelve monthly figures are read, their
  arithmetic mean in whole pounds is a realised figure
  (`mean-12m:<scope>:<year>`, "mean of twelve monthly figures as
  published", dated by the latest of the twelve posts). Per month, where
  several pages print a figure that agrees to the nearest £1,000, the most
  precisely printed is read, then the latest; where they differ beyond
  rounding, the latest published is read and the difference is listed
  (F4). The months and the choice are in `evidence/months.json`.
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

Each is decided on the scored rows of every publisher together, and is
**undecided** when no vintage is scorable (P-A, P-B) or no revision pair
exists (P-C); the same three are reported per publisher beside the whole,
never as a separate verdict.

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
- **F2** Of the per-year strings (a `per year` unit in any spelling) on
  the English Modo pages, more than a third are declined for a period or
  a population the rules could not find (`R-R5 period not stated`, `R-R3
  no population named in the clause`): the corpus is **not determinable**
  under these rules; every string is published with the rule that declined
  it, and no proposition is judged.
- **F3** A committed row of `evidence/figures.ndjson`,
  `evidence/comparisons.ndjson` or `evidence/revisions.ndjson` would change
  on recompute under the same rule version: the run refuses. There is no
  `--amend`; a changed figure is a new declaration beside this one, and a
  row is recorded once per rule version (the kill test of 2026-09-25,
  `bill/KILL-TEST.md`).
- **F4** The realised side restates itself (pages print figures for the
  same scope and month, or year, that differ beyond rounding): R-S3 and
  R-S4 read the latest and every difference is listed in
  `evidence/months.json` and in `FINDINGS.md`.

## Checks the runner makes before and after computing

- **C1** Every artefact in the manifests hashes to its recorded digest;
  the schema reports on disk hash to the digests cited above.
- **C2** Every figure row names its page's digest, the string as printed,
  and the rule that read it; every unread string names the rule that
  declined it (R-R7).
- **C3** The comparison rows are exactly one per forecast figure.
- **C4** No figure of basis `potential` enters the figures.

A failed check refuses the run and is recorded in `AMENDMENTS.md` before
any rerun; nothing is written.

## Outputs

- `evidence/figures.ndjson`: one line per figure-looking string of the
  schema reports (read as a figure, read as a monthly figure, or declined,
  with its rule), append-only, carrying `rule_version` (this file's
  SHA-256 prefix), the page digest, the offset and the string as printed.
- `evidence/months.json` (rewritten each run): R-S4's months per scope
  and year, the choice per month and the differences beyond rounding.
- `evidence/comparisons.ndjson`: one line per forecast figure, with its
  status and, where scored, the errors; append-only, `rule_version`.
- `evidence/revisions.ndjson`: one line per revision pair; append-only.
- `evidence/summary.json` (rewritten each run): digests, the seal, the
  run date, every figure, the same-day duplicates, the propositions with
  their instances (per publisher beside the whole), the not-yet-scorable
  table, F1, F2 and F4.
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
012 onward: this file with its proofs, `ACQUISITION.md` and
`AMENDMENT-1.md` with their proofs,
the committed evidence with `rule_version` on every row, the schema
reports under `archives/`, and `scripts/check`. No row is proposed to a
Morpholog database by this declaration.
