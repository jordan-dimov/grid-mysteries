# 024 — The gas in the spread: Declaration

**Written 2026-10-15 on the sponsor's handover of that day (etrmbiz
`notes/2026-10-15-grid-mysteries-prompt-024-gas-in-the-spread.md`), which
opened this investigation and so satisfies the no-new-investigation-by-default
rule of `investigations/NEXT-MILESTONE.md`.** Frozen by `scripts/freeze`
after the acquisition and the schema pass and before any price is read for
this question. Changes after the freeze are amendments. It is a credibility
piece with a live peg, not a capital-decision fact, and is published and
moved on from under the doctrine's rule for exactly that.

## The mystery

> Great Britain's daily day-ahead spread in September 2026 was the widest in
> thirteen months. Did the power market get more volatile, or did gas get
> dearer?

The peg: Bloomberg, 15/10/2026, "Europe's $40 billion battery bet set for
big winter payout", leads with a GB September spread of about GBP 123/MWh,
up 80 % on a year earlier; Modo Energy's monthly note gives GBP 122/MWh with
gas averaging GBP 64/MWh. The method is Julien Jomaux's for Germany (GEM
Energy Analytics, "The evolution of the spread: 2026 update", 24/09/2026):
the daily spread divided by the gas price, and the spread split into a
negative, a merit-order and a scarcity leg. Nobody has published it for GB.
It is carried over with attribution; nothing in it is calibrated here.

## Prior exposure, stated

- **Scratch figures, computed outside this repository on 15/10/2026 by the
  etrmbiz session, unsealed, from earlier pulls of the same two series
  (not the files pinned here); recorded in etrmbiz
  `research/gb-spread-gas-normalised-first-cut-2026-10-15.md`.** Daily
  max-minus-min of the N2EX hourly file averaged by period, gas as the ONS
  SAP times ten: September 2026 spread 121.7 and gas 64.5; 2026 to 14/10
  spread 77.5 against 71.4 on the same dates of 2025; the spread-over-gas
  ratio 1.79 for 2026 to 14/10 against 2.25 for 2025's same dates, and 1.89
  for September 2026 against 2.81 for September 2025; by calendar year,
  spread, gas and ratio 2022 157.6 / 71.2 / 2.21, 2023 70.9 / 34.4 / 2.06,
  2024 61.2 / 28.7 / 2.13, 2025 68.6 / 30.4 / 2.25. The spread figures
  replicate a published number, so there is no selection to protect; **the
  ratio and the three-leg split are the new quantities, and this
  declaration is written knowing the ratio's rough value.** The scratch
  figures are not evidence and are never cited as results; RESULTS.md
  prints them beside the declared measure so etrmbiz can check them.
- **Published figures.** Modo: GBP 122 and GBP 64 for September 2026, and
  "GBP 45/MWh wider than September 2025" (which implies about 58 % up);
  Bloomberg: about GBP 123, up 80 %. The scratch measure gave about 60 %.
  **The discrepancy is open and is not resolved by picking the measure that
  matches Bloomberg**: the run reports what the declared measure gives and
  notes the difference.
- **The author's look at the file's layout.** Before the pin, the first 600
  bytes of the NESO dump were read for the column names and the row shape
  (the note's names, `Price (GBP/MWh)` and a numbered period, are not what
  the file prints). Those bytes show six prices of 20 and 21 September 2021,
  outside every period declared below.
- **The schema pass**, which read no price: the archive reports and
  supplements cited below (row counts, forms, labels, rows per date, date
  ranges, the carbon tables' layout).
- No spread, ratio or leg has been computed from the pinned files.

## Sources, pinned 15/10/2026

All fetched by `run.py --phase acquire` on the sponsor's authorisation in
the handover ("to be pinned and schema-reported before the declaration");
journalled and verified against `evidence/sources-manifest.json`
(`4362ca05…`); a pinned file is never refetched or overwritten.

| dataset | path | SHA-256 | fetched (UTC) | bytes |
|---|---|---|---|---|
| `govuk-ukets-ccm-monthly-average-prices` | `data/raw/govuk/024/ccm-trigger-prices-and-average-monthly-prices-full-table-2026-10-15.html` | `932725ca74e4…` | 2026-10-15T18:44:29Z | 124,262 |
| `govuk-ukets-markets-guidance` | `data/raw/govuk/024/uk-emissions-trading-scheme-markets-2026-10-15.html` | `07cd65e8ab5c…` | 2026-10-15T18:52:19Z | 137,887 |
| `neso-n2ex-day-ahead` | `data/raw/neso/024/n2ex-day-ahead-dump-2026-10-15.csv` | `ab8202a72eae…` | 2026-10-15T18:42:54Z | 1,575,075 |
| `neso-n2ex-day-ahead-resource-metadata` | `data/raw/neso/024/resource-show-4f27eea5-7038-4f73-9740-e3e4ad47c26a-2026-10-15.json` | `4097147bf8cb…` | 2026-10-15T18:44:29Z | 874 |
| `ons-sap-gas-daily` | `data/raw/ons/024/systemaveragepriceofgasdataset151026.xlsx` | `c84b724a9524…` | 2026-10-15T18:42:54Z | 127,625 |
| `ons-sap-gas-dataset-page` | `data/raw/ons/024/systemaveragepricesapofgas-dataset-page-2026-10-15.html` | `58b37e4cd54b…` | 2026-10-15T18:44:30Z | 51,517 |

- **Power**: NESO Data Portal, "Day-Ahead Power Exchange prices (Nord Pool)",
  resource `4f27eea5-7038-4f73-9740-e3e4ad47c26a` ("N2EX GB Day-Ahead
  Price"), the CKAN datastore dump; NESO Open Data Licence (the package
  metadata, `license_id` `ESO`). The resource's `last_modified` reads
  2026-09-21T12:38:33 and the package's `metadata_modified`
  2026-10-15T11:30:17; the dump itself runs to 16/10/2026. The N2EX hourly
  auction is one of two GB day-ahead auctions (EPEX runs the other); the
  portal does not say which time zone `Delivery Period` is printed in.
- **Gas**: ONS, "System Average Price (SAP) of gas", edition of 15/10/2026
  (cover sheet: data coverage January 2018 to October 2026, published 15
  October 2026, next publication to be confirmed; official statistics in
  development; source National Gas Transmission, On-the-Day Commodity
  Market); Open Government Licence v3.0. **This is a within-day system
  price, not the NBP day-ahead assessment.** No free daily NBP day-ahead
  series was found (EEX, Argus and LEBA sell it); if one turns up it is a
  cross-check in this run, never a replacement.
- **Carbon**: gov.uk, UK ETS Authority, "Cost Containment Mechanism (CCM)
  trigger prices and average monthly prices: full table", page updated
  12/10/2026 (next monthly update 10/11/2026), Open Government Licence
  v3.0, with the guidance page that defines its figure: "the monthly average
  carbon price is calculated by dividing the sum of the end of day
  settlement prices for the relevant December futures contract during each
  month by the number of days in the month for which a price is published".
  Ember's carbon price viewer, which the handover named, no longer exists
  as a dataset page (it redirects to a Flourish chart with no download), and
  no free daily UK allowance series with a stated licence was found (two
  web searches, ICE and EEX sell theirs). The handover's fallback applies:
  **a monthly carbon value from an official publication, and the merit-order
  boundary is coarse.** Carbon Price Support is GBP 18/t, a fixed rate.

## The schema pass, cited

- `archives/024-n2ex-day-ahead/schema-report.json` (`3c06553f…`) and
  `day-structure.json` (`4ec2b425…`): 44,448 rows, columns
  `Date`, `Delivery Period`, `Price`; 1,853 printed dates from 2021-09-20 to
  2026-10-16, none missing; 24 distinct period labels `HH:00 - HH:00`;
  **24 rows on every date except the first (2 rows: `22:00 - 23:00`,
  `23:00 - 00:00`) and the last (22 rows, those two labels missing)**; no
  repeated (date, label) key; no blank; prices printed to six decimals.
- `archives/024-ons-sap-gas/schema-report.json` (`34371f4e…`) and
  `date-structure.json` (`bbf66769…`): sheet `1.Daily SAP Gas`, header on
  row 5 (`Date`, `SAP actual day`, `SAP seven-day rolling average`), 3,206
  dated rows from 2018-01-01 to 2026-10-11, none missing, none duplicated,
  every `SAP actual day` cell a number, in p/kWh.
- `archives/024-govuk-ukets-monthly-prices/schema-report.json` (`ae6f9046…`): two
  tables, 18 rows Aug-21 to Jan-23 with a three-month monitoring period and
  51 rows Feb-23 to Apr-27 with a six-month one; each row prints its
  period's months by name and one `£xx.xx` average price per month; 21
  cells of the six-month table are text (the months not yet observed).

## The unit: what a day is

- **The printed date is the day.** The file prints 24 hours on every date
  including Great Britain's clock-change dates (27/03/2022, 30/10/2022 and
  their successors), so its hours are a fixed-offset clock, not local
  wall-clock time. UTC is the likeliest offset (midnight BST is 23:00
  UTC), but the series begins at `22:00 - 23:00` on 20/09/2021 and ends at
  `21:00 - 22:00` on 16/10/2026, one hour earlier at both ends than a UTC
  print of the auction's delivery days would, and NESO documents no time
  zone; the offset is therefore an assumption, stated, not a fact. The scratch read and, as far as its published figure shows, Modo's
  measure take the printed date, so the printed date is the primary unit
  and the Modo reproduction (F2) tests it.
- **Beside it, the local day**: each printed hour is read as UTC and
  assigned to its Europe/London calendar day (`gas_in_the_spread.local_day`),
  which gives 23 hours on the spring and 25 on the autumn clock-change day.
  Every period figure is reported on both units; the local-day figures are
  labelled as resting on the UTC reading, and if the hours are not UTC they
  are mislabelled by a constant offset.
- **Validity**: a day with 23, 24 or 25 prices is measured; a day with
  fewer than 23 or more than 25 is excluded from every average and counted
  (`days_excluded_by_price_count`). On the printed unit that excludes
  20/09/2021 and 16/10/2026 and nothing else; on the local unit the first
  and last local days are partial and excluded. A date printing a label
  twice would be excluded (none does).
- **The spread** of a day is its highest hourly price minus its lowest
  (Jomaux's TB1), in GBP/MWh, on Decimals from the printed text.

## Gas, carbon and the CCGT proxy

- **Gas** for a day is the ONS `SAP actual day` of that calendar date, times
  ten (p/kWh to GBP/MWh), exact.
- **Carbon** for a day is the UK allowance's monthly average price for the
  day's calendar month, read by the rule in `sources/ukets_monthly.py`: in
  the row for month M with a k-month monitoring period, `Month j average
  price` is the average of month M − (k + 1 − j); a month printed in several
  rows must print one value or the run stops (C3); plus Carbon Price
  Support at GBP 18/t. A day whose month prints no value (October 2026 at
  the freeze) has no carbon and no legs, and is counted.
- **The CCGT cost proxy** is Jomaux's: 2 × gas + 0.4 × carbon, in GBP/MWh
  with gas in GBP/MWh and carbon in GBP/t. **It is his, not calibrated
  here.** In GB terms: 2 × gas is a 50 % thermal efficiency on the gas
  price as GB quotes it (per kWh on the higher heating value, so about 55 %
  on the lower heating value that plant data sheets quote); 0.4 t/MWh is
  0.2 t of CO2 per MWh of gas at that efficiency. It carries no transport
  cost, no variable operating cost and no capacity-market or balancing
  revenue; it is a boundary between two legs, not a cost of generation.

## The three legs

For each hour, the price is split into the part below zero (the negative
part, at most zero), the part between zero and the CCGT proxy (the
merit-order part) and the part above the proxy (the scarcity part); the
parts sum to the price. Each part is a non-decreasing function of the
price, so the day's highest price has the highest value of every part and
the lowest price the lowest, and the day's **negative, merit-order and
scarcity legs** are the differences of each part between those two hours:
each is non-negative and the three sum exactly to the spread
(`gas_in_the_spread.legs`, tested on a wholly negative day, a day without
scarcity, a day with all three and a flat day). The negative leg is the
part of the spread that lies below zero, the merit-order leg the part
between zero and the proxy, the scarcity leg the part above it.

## Periods and averages

- **Periods**: calendar years 2022 to 2025 (2022 is the first full year and
  includes the crisis); **2026 to date**, 01/01/2026 to 15/10/2026 (the
  fetch date); **2025 same dates**, 01/01/2025 to 15/10/2025; and every
  calendar month from January 2022 to October 2026 (partial, labelled so).
- **Period averages** are simple means over days: the spread over the
  period's measured days; gas over its days with a gas price; each leg over
  its days with legs. Counts of each are printed with every figure.
- **The ratio**, two definitions, both reported, the first leading:
  **A**, the period's mean spread divided by its mean gas price, both means
  over the days with both a spread and a gas price; **B**, the mean over
  those days of the daily spread divided by the daily gas price. Jomaux's
  text does not say which he uses.
- **Each leg's share** of the spread is the period's mean leg over the
  period's mean spread on the days with legs, by year and by month.

## Checks each run must pass, or it stops

- **C1** Every pinned file hashes to its manifest digest.
- **C2** The format check (`run.py --phase format`, `evidence/format-check.json`)
  finds every file in the format the schema pass recorded: no byte-order
  mark, the header, three fields on every line and the three forms on
  every field of the CSV; the sheet names, header row and cell forms of
  the workbook; the table count, headers and cell forms of the page. A
  departure no frozen amendment reads stops the compute.
- **C3** Every month of the carbon tables prints one value.
- **C4** For every day with legs, the three legs sum to the spread exactly.
- **C5** `evidence/days.ndjson` is append-only: a committed line that would
  change on recompute stops the run.

## Falsifiers, declared in advance

- **F1** The ratio A for 2026 to date is **not below** 2025's same dates by
  more than 5 % (ratio 2026 ≥ 0.95 × ratio 2025): then the headline rise is
  not mostly gas and the sponsor's scratch reading was wrong.
- **F2** The September 2026 mean spread on the printed unit does **not**
  reproduce Modo's GBP 122 within GBP 2: then the measure differs from the
  published one and the comparison to Bloomberg is not like for like.

## Explanations to test and record, not assume

- That the 2026 fall in the ratio is a gas-shock artefact: gas rose faster
  than the evening peak could follow, which Jomaux's own German series also
  shows for 2026. Tested by the monthly ratio against the monthly gas price
  across 2025 and 2026 (does the ratio fall in the months gas jumps and
  recover after), and recorded either way.
- That the ratio is lower in GB than in Germany (about 2 against about 3)
  because GB has less solar depth and more gas on the margin. **A reading,
  not a finding**, unless the negative leg's share shows it; the run prints
  that share by year and says whether it does.

## What this never claims

- That the spread is "caused" by gas: the ratio is an accounting identity on
  two averages, and the legs are a boundary drawn with a borrowed proxy.
- Anything about battery revenue, which trades a different product (the
  spread a battery can capture, net of cycling and efficiency).
- Anything about the NBP day-ahead price, which is not what SAP measures.
- That a comparison with Jomaux's German figures is like for like: his gas
  and carbon series, his day and his hours are not these.

## Caveats, in the order the piece must carry them

1. SAP is a within-day system price, not the NBP day-ahead assessment.
2. The N2EX hourly auction is one of two GB day-ahead auctions.
3. 2022 is the first full year of the file and includes the crisis.
4. The merit-order proxy is Jomaux's, uncalibrated, on a monthly carbon price.
5. The 60 % against 80 % year-on-year difference for September is unresolved.

## Order of work

1. This file is frozen. 2. Format check. 3. Compute under the seal (pinned
bytes only; no network). 4. RESULTS.md, figures and captions. 5. Report to
the sponsor; nothing is published from this repository (etrmbiz writes the
piece, credits Jomaux's method and names the sources, never this
repository).

## Outputs

`evidence/format-check.json`, `evidence/days.ndjson` (one line per day and
unit: prices, spread, gas, carbon, proxy, legs), `evidence/results.json`,
`evidence/rule-sources.json`, `evidence/run-log.json`, `RESULTS.md`
(committed); `figures/` (out of git) with `captions.md`.
