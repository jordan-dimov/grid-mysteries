# 022 — Amendment 2 to the declaration: a misread high, and the funds' own financial years

**Status: drafted 2026-10-01 (night) on the sponsor's reading of
`FINDINGS.md` at `863635c`; frozen with `scripts/freeze` and run on the
sponsor's word of the same reading ("Run amendment 2, recompute,
re-render"), which is the seal for `compute` under it as the instruction
of 2026-10-01 was for 021's runner: `run.py --phase compute --seal
b8e6d53b… --amendment-seal <prefix of this file's SHA-256 as frozen>`.**
`DECLARATION.md` (SHA-256 `b8e6d53bf8e2529ac6caeaf419eb419b76c5f9f12927d647778f382cdd19d2e5`,
frozen at `6ffd05a`) is not edited; this file is read with it. Rows
computed under it carry the rule version `b8e6d53b.<this file's prefix>`;
the rows computed under `b8e6d53b` alone remain in the evidence as they
were written, and `FINDINGS.md` renders the latest rule version and says
which it supersedes. Nothing goes outside the repository until the
sponsor has read the new `FINDINGS.md`.

## 1. A December high read as an annual outturn (R-R5(x))

Under the declaration as frozen, GRID's annual report for 2024
(`https://greshamhouse.com/wp-content/uploads/2025/04/GRID-Annual-Report-31-December-2024.pdf`,
dated 2025-04-22 by its metadata) yielded two realised figures for GRID's
2024: `£59.8k/ MW` from "This translates to an annualised £/MW figure of
£59.8k/ MW in 2024", and `£91k/MW/yr` from a sentence on the year's highs
and lows, "… closed the year with highs and lows in 2024 of £91k/MW/yr
(December) and … (February)". R-R5 read the period named before the figure
("in 2024") and produced an annual outturn from a December high. Named
rather than fixed was right for an ambiguity; this is a misread, and
leaving it in the realised table invites the one correction a reader will
make. The sponsor's instruction: out, with the record saying why.

- **R-R5(x), extremes and bracketed months.** A clause stating a high or
  a low (`highs and lows`, `high of`, `low of`, `peak`, `record high`,
  `record low`, `highest`, `lowest`) is an extreme, not a period figure,
  and is declined. A month in brackets immediately after a figure
  (`£X (December)`) dates that figure to that month, over any year named
  before it; on a fund page that is a figure dated by a month, declined
  as R-R5 already has it; on a Modo page it is a monthly figure. Under
  this rule the `£91k/MW/yr` string is declined as a high, and GRID's 2024
  outturn is the `£59.8k/ MW` figure alone.

## 2. The funds' own financial-year outturns (R-R5(f2), R-M2)

The fleet mismatch is the weak comparison. The strong one is in the
corpus and was declined by design: HEIT's results for the year ended
31 October 2024 (`…/results-for-financial-year-ended-31-october-2024/8752544`,
pinned under amendment 1) print the portfolio's own revenue per MW for
that year, and the declaration's R-R5 declined it ("a fund figure dated
by a month, not a calendar year"), because an outturn had to be a
calendar year to be scored. The sponsor's reading of that RNS, about
£58k per MW, is recorded here as the sponsor's prior; the author read
the sentences with every digit masked ("Total net revenue generation for
the Period was £9.9 million (£99.9k/MW/Yr) …", "… generated revenue … of
£9.9 million over the Period (£99.9k/MW/Yr …)").

- **S1, the stated period** (schema pass, fund report regenerated): the
  first period a document states with its end, as printed (`year ended
  31 October 2024`, `period to 30 June 2025`, `six months ended …`),
  recorded as `text:period-end`. Of the 280 fund documents, 136 state
  one: `year ended` 34, `period ended` 33, `period to` 13, `period
  ending` 12, `six months ended` 10, `12 months ended` 6, `financial year
  ended` 4, `financial year ending` 4. The regenerated report is
  `archives/rns-grid-022/schema-report.json` (SHA-256 `bddd7be988d66e2eadd791ce318972ffa52197c784866a8b53b32d03e9560e25`;
  `SCHEMA.md` `f1dc2a14…`); the Modo report is untouched and keeps the
  digest the declaration cites (C1 checks both).
- **R-R5(f2), a fund's financial-year outturn.** On a fund page that
  states a period, a figure whose clause names no period of its own and
  says `for/over/during/in/throughout the period`, `the year` or `the
  financial year` is read as the fund's outturn for the stated period
  **when that period is a year** (`financial year`, `year`, `twelve
  months`, or `period` on a page whose title says final, full-year or
  annual results or names a financial year): basis realised, scope the
  fund's portfolio with any Capacity Market qualifier the sentence
  states, period labelled `year to <end date>` and never a calendar year.
  A stated period that is not a year (an interim, a quarter) is listed as
  such and not compared. A figure in a sentence with assumption words
  stays R-R4(f)'s. A financial-year outturn never enters the calendar
  index and never scores a forecast (R-S2 stands).
- **R-M2, the period mismatch.** A forecast figure with no outturn of its
  own scope and calendar period, published by a fund that has a
  financial-year outturn overlapping that period, is a **period
  mismatch**: the row prints the assumption and the fund's own outturn,
  states the overlap in months (calendar 2024 against the year to
  31 October 2024: ten of twelve), states a scope difference where the
  outturn does not carry the assumption's Capacity Market qualifier (not
  assumed either way), names the fleet outturn beside it as the scope
  mismatch it is, and adjusts nothing. R-M2 is taken before R-M; an
  in-year assumption keeps R-S1's status and names the overlapping
  outturn in its note, listed, not compared. The same applies to GRID
  and GSF where their years differ from the calendar (GRID's is the
  calendar year, so R-R5 already reads it; GSF's ends in March and has no
  assumption to meet).

## What this amendment does not change

R-S1 to R-S4, R-C, R-M, R-V, P-A to P-C and F1 to F4 as frozen; the
propositions are judged on scored rows only, and a period mismatch is not
a scored row, so the verdicts are expected to stand. Every string is
still listed with the rule that read or declined it.

## The page

The public write-up leads with the period-mismatch row (HEIT's assumption
for 2024 beside HEIT's own year to October 2024, both figures, the overlap
in months, nothing adjusted); the finding sentence comes second; the rest
as the sponsor set it.
