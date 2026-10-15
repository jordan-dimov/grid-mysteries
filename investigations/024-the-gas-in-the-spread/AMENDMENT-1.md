# 024 — Amendment 1: the gas cross-check (Ofgem's monthly day-ahead price against SAP)

**Written 2026-10-15, after the declaration (`739471d0…`) was frozen and
computed, on the sponsor's instruction of that evening ("do the cross-check
and update our results").** Frozen by `scripts/freeze` after the schema
pass of its source and before any value of that source is read for this
question. It adds a cross-check; it changes nothing computed under the
declaration, whose results stand as committed (`evidence/results.json`,
RESULTS.md of commit 2d0753c).

## Why

The declaration's first caveat: SAP is a within-day system price, not the
NBP day-ahead assessment, and "if a free one turns up it is a cross-check in
this run, never a replacement". One turned up, monthly, from Ofgem. This
amendment declares how it is read and compared before it is read.

## The source, pinned 15/10/2026

- Ofgem, wholesale market indicators, chart **"Gas prices: day-ahead
  contracts – monthly average (Great Britain)"**, data portal node 175055,
  served by everviz under chart key `YFsS4g98P`; the inject script the
  portal renders (`data/raw/ofgem/024/wmi-gas-day-ahead-monthly-everviz-inject-YFsS4g98P-2026-10-15.js`,
  SHA-256 `a304e0726a41…`) carries the series as an embedded CSV, and the
  portal page (`data/raw/ofgem/024/wholesale-market-indicators-page-2026-10-15.html`,
  `f8a6aef72fec…`) carries the chart's description. Both are in
  `evidence/sources-manifest.json` (`48e0239c…`).
- Ofgem's description, from the page: "the average price of gas for next
  day delivery on the wholesale market in Great Britain … The data until 28
  February 2021 comes from a third-party Price Reporting Agency's price
  assessment of over-the-counter trading through brokers … From 1 March
  2021, the data is Ofgem analysis of broker data and is an average monthly
  price weighted by volume." Credits as printed: "Ofgem analysis of broker
  data"; axis unit "p/therm".
- Licence: Ofgem's copyright page permits reproduction of its Crown
  copyright material and excludes material identified as a third party's.
  The months compared here (January 2022 onward) are all in Ofgem's own
  analysis; the pre-March-2021 agency assessment is not read.
- No Ofgem CSV endpoint exists; the everviz inject is what the portal's
  chart and its download button draw from. A hypothetical later edition of
  the chart would be a new pin, not this one.

## Prior exposure, stated

- While locating the CSV inside the script, the author saw its first rows:
  monthly prices of October 2009 to early 2010, outside every period.
- **The schema pass** (`archives/024-ofgem-gas-day-ahead-monthly/schema-report.json`,
  SHA-256 `fea333c0e384…`), which read no value: header `Category`,
  `Price`; 201 rows from `10/01/2009` to `06/01/2026`, every date the
  first of a month in month/day/year form, every price a decimal; title,
  credits and axis unit as above. **The series ends at June 2026**, so the
  cross-check cannot reach September 2026, and the first-half comparison
  below is what it can do.
- The SAP monthly means of `results.json` are known to the author (they
  are in RESULTS.md). The Ofgem values are not.

## The reading rule

- A row's month is the (year, month) of its `Category`; its price is in
  pence per therm, converted to GBP/MWh as price × 10 ÷ 29.3071 (the
  statutory kilowatt-hours per therm), exact in Decimal, then quantised to
  six places. A repeated month or a row outside the forms stops the read
  (`sources/ofgem_wmi.py`, tested).
- SAP for a month is the month's `gas_mean` of the declaration's results
  (the simple mean of the daily SAP × 10 over the month's days), unchanged.

## What is computed

- For every calendar month from January 2022 that both series hold: Ofgem
  in GBP/MWh, SAP, the difference (Ofgem − SAP) and its share of SAP; the
  month's mean spread (from the results) over each gas price, as ratio A
  on SAP and ratio A on Ofgem. Months either series lacks are listed and
  skipped.
- By year, over the months compared: the mean of the monthly SAP means and
  of the monthly Ofgem prices, and the sum of monthly mean spreads over the
  sum of monthly gas prices on each series (months weighted equally, so the
  SAP column may differ in the third decimal from the day-weighted ratio A
  of the results).
- **Materiality**: the SAP caveat is **material** if any month from January
  2025 differs by more than 5 % of SAP in either direction, the 5 % being
  F1's own threshold; otherwise the difference is **within the two
  measures' weighting** and the caveat is carried as written.
- **F1 on the cross-check series**: ratio A over January to June 2026
  against January to June 2025 (the 2026 months both series hold), on SAP
  and on Ofgem, each as the mean of the six monthly mean spreads over the
  mean of the six monthly gas prices. The F1 verdict **stands** on the
  cross-check if the Ofgem-based ratio for the 2026 half is below the 2025
  half's by more than 5 %; otherwise it is reported as not confirmed on the
  day-ahead series, and the declaration's F1 verdict is not changed by it,
  only annotated.

## Checks, or the run stops

- C1 both pinned files hash to their manifest digests; C2 the inject's
  header, row count and forms are the schema pass's.

## What this never claims

- That Ofgem's monthly average is the NBP day-ahead assessment a trader
  would quote: it is a volume-weighted mean of broker-traded day-ahead
  contracts over a month, and the daily series behind it is not published.
- Anything about September 2026, which Ofgem has not yet published.

## Outputs

`evidence/cross-check.json`; a section in RESULTS.md headed "Cross-check",
rendered by `run.py --phase render` from that file; nothing else in
RESULTS.md changes.
