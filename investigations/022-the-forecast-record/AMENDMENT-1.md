# 022 — Amendment 1 to the acquisition plan: fund-cited forecast figures

**Status: drafted 2026-10-01 (evening) on the sponsor's question after
reading the completed declaration at `a6410b9`; frozen with
`scripts/freeze` and run on the sponsor's word of the same evening ("if
no, add them before the freeze"), which is the seal for this fetch as the
instruction of 2026-10-01 was for 021's runner; the runner's `index-2`
and `acquire-2` phases take that word as `--amendment-seal`, a prefix of
this file's SHA-256 as frozen, beside the plan's own seal
`962cb9b5db8d33a7`.** `ACQUISITION.md` (SHA-256 `962cb9b5…`) is not
edited; this file adds to it and is read with it.

## The question, and the answer

The sponsor asked whether fund-cited forecast figures were in scope:
fund prospectuses, annual reports and NAV announcements cite dated
revenue assumptions by year, often third-party curves, and the 2021 to
2023 vintages for 2024 and 2025 are scorable today.

**They were not in scope as forecasts.** The plan's A5(ii) pinned the
three funds' *results* documents as the realised comparator: the anchor
text rule matched `results` and `report` only, over the first three
Investegate listing pages of each fund (about eighteen months of
announcements), so NAV announcements, prospectuses, placings and trading
updates were never listed; the Gresham House annual and interim report
PDFs were pinned but the declaration's R-R0 declines a PDF because
`pdftotext -layout` interleaves its columns; and the declaration's R-R4
declines a figure whose sentence says "assumed" or "estimate" as
potential, required, contracted or assumed, which is exactly how a fund
cites a revenue curve. What the pinned fund text carries on the forecast
side, read with every digit masked before this amendment: one sentence in
GRID's half-year results of 2025-09-24 citing third-party forecasters'
2026 merchant revenue level for two-hour assets, one benchmark comparison
in GSF's half-year report of 2025-12-15, and in GRID's annual report PDFs
(layout text) sentences on the merchant revenue assumed in the Company's
three-year plan and on a merchant revenue rate on uncontracted assets.
Recorded as prior exposure; no value was seen unmasked.

## What this amendment adds (A7)

- **A7(i), every Investegate announcement page of each fund.** For
  `GRID`, `GSF` and `HEIT` the runner pins
  `https://www.investegate.co.uk/company/<ticker>?page=<n>` for `n` from
  4 upward until a page carries no link to an announcement
  (`/announcement/`), or `n` reaches 40, whichever first; pages 1 to 3
  are read again from the bytes pinned under the plan.
- **A7(ii), the widened link rule.** On every listing page (1 to the
  last), every anchor whose visible text matches, case-insensitively,
  `results|report|net asset value|\bnav\b|prospectus|placing|issue|
  fundrais|valuation|trading update|portfolio update|investor
  presentation|capital markets|business update|acquisition|strategy`
  is listed as (absolute URL, text) in `evidence/run-index-2.json`,
  duplicates by URL dropped, and every listed document not already in
  `evidence/rns-manifest.json` is pinned to `data/raw/rns/022/` under the
  same journal, so the schema pass covers the funds' documents as one
  set. The widened rule also runs over the Gresham House and Gore Street
  pages pinned under the plan.
- **A7(iii), PDFs read in reading order.** The schema pass reads a PDF
  with `pdftotext` in its default reading order rather than `-layout`,
  which keeps a two-column page's sentences whole; the report says which
  mode produced its text. The layout-mode report stands in git history at
  `2cc8c3e`. Whether a PDF's sentences are then coherent enough to read
  is the declaration's R-R0 to decide, against the regenerated report.
- **A7(iv), the vintage window for the funds.** The plan's "since 2023"
  was Modo Energy's; for the funds the sponsor names the 2021 to 2023
  vintages, so fund documents from 2021-01-01 are pinned and the
  declaration's R-R6 is restated for fund pages. Modo's window is not
  changed.

Half a second separates requests, failures are recorded and skipped,
nothing is fetched under another agent or path, and no document URL is
guessed into this amendment. The probes of 2026-10-01 (evening), by HEAD
only, status code and nothing else: see `evidence/run-index-2.json` for
what each listing page carried.

## What this amendment does not do

It reads no figure and writes no reading rule. The declaration's R-R0,
R-R4 and R-R6 are restated for fund documents after the regenerated
schema report exists, in `DECLARATION.md` before its freeze, and the
propositions are judged over every scorable vintage of every publisher,
reported per publisher.
