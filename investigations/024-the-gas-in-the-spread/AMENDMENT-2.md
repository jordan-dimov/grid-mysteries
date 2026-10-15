# 024 — Amendment 2: the forward record (the spread implied by the ratio and the forward gas curve)

**Written 2026-10-15, after the declaration (`739471d0…`) and amendment 1
(`30c3f2a7…`) were frozen and computed, on the sponsor's handover of that
evening (etrmbiz `notes/2026-10-15-grid-mysteries-prompt-024-forward-record.md`).**
Frozen by `scripts/freeze` after the schema pass of its source and before
any value of that source is read for this question. It is a **prediction**,
so the human gate is publication, and the falsifiers go out with the
claim. It is **not a Forward Mystery** under the generator: no buyer, no
absorption and no opportunity is claimed. It is a dated forecast appended
to a forensic record in the shape of 013's forecast note, scored as a
vector, never a verdict. Nothing under the declaration or amendment 1
changes: this adds a source, a conversion, a derived table and watches.

## Prior exposure, stated

- On 15/10/2026 the etrmbiz session read Catalyst Commercial's report of
  15/10/2026 (settlement Wednesday 14/10/2026) and converted its NBP table
  by hand: day-ahead 209.00 p/therm, Nov-26 216.01, Dec-26 218.98, Q1-27
  216.17, Summer-27 159.70, Winter-27 152.20; UK ETS Dec-26 GBP 65.10/t;
  at 10 ÷ 29.3071 GBP/MWh per p/therm, 71.31, 73.71, 74.72, 73.76, 54.49,
  51.93. It multiplied these by 024's yearly ratio band and saw winter
  2026-27 at about 133 to 167 GBP/MWh, Summer-27 98 to 123, Winter-27 93 to
  117. **Those numbers are unsealed scratch and are never cited as
  results**; they are disclosed so this declaration cannot be written as if
  the author had not seen them.
- While writing the reader, the author saw the forms of the commodities
  table's cells (currency, slash, unit) and the UK ETS row as printed.
- **The schema pass** (`archives/024-catalyst-report-2026-10-15/schema-report.json`,
  SHA-256 `35eafe66f552…`), which read no value: three tables of three
  cells per row; table 0 headed `Contract`, `Settlement (p/therm)`,
  `Change on the day` with rows `Day-ahead`, `Nov-26`, `Dec-26`, `Jan-27`,
  `Q1-27`, `Summer-27`, `Winter-27`, every settlement a decimal; table 1
  the baseload power equivalents in £/MWh (not read); table 2 headed
  `Commodity`, `Settlement 14 Oct`, `Change on the day` with a row
  `UK ETS Dec-26` whose settlement prints as `£…/tonne`; the settlement
  line "Settlement Wednesday 14 October 2026, against Tuesday 13 October
  2026"; and the page's own terms, quoted below.
- The ratio band's rough values are known to the author from RESULTS.md
  (1.79 and 2.25); the amendment reads them from the file, never types them.

## The source, pinned 15/10/2026

Catalyst Commercial, "UK Energy Market Report - 15 October 2026",
`https://www.catalyst-commercial.co.uk/works/uk-energy-market-report-15-october-2026/`,
the HTML page (`data/raw/catalyst/024/uk-energy-market-report-15-october-2026.html`,
SHA-256 `8ba4b5b3a48f…`, in `evidence/sources-manifest.json`
`afce3a36edb1…`). **It is a broker-report aggregator's page, not the
exchange's settlement file** (ICE Endex NBP settlements are paid), and it
is the only free dated print of the curve found. Its footer, verbatim:
"Settlement figures are for 14 October 2026 and indicative market levels
are as at the morning of 15 October 2026. Source data: UK and European
wholesale market settlements. Commentary and analysis may be quoted with
attribution and a link to this page. Forward-season levels stated here are
indicative editorial estimates and are not licensed market data; they must
not be redistributed as a price feed." The record therefore calls the
curve **Catalyst's indicative print**, quotes it with attribution and a
link, and redistributes no feed: six dated numbers inside an analysis. A
later edition is a new pin, never a rewrite of this one.

## Conversion, declared

One therm is 29.3071 kWh, so **GBP/MWh = p/therm × 10 ÷ 29.3071**
(`sources/ofgem_wmi.KWH_PER_THERM`, the constant amendment 1 declared),
exact in Decimal, quantised to six places for the record.

## The ratio band, declared

From `evidence/results.json` as sealed under `739471d0…` (SHA-256
`47e768153755…` at this writing), printed unit: the yearly ratio A (mean
daily spread over mean SAP gas) for **2023, 2024, 2025 and 2026 to date**;
the **low edge** is the least of the four and the **high edge** the
greatest; the **central case** is "2026 to date" alone. Read by
`gas_in_the_spread.ratio_band`, tested against a results-shaped fixture, so
the edges are never typed. The band is four annual means of a monthly
series whose monthly range is far wider (the record prints the 2025-26
monthly minimum and maximum beside it); **a month outside the band is not
a falsification, a season is.** 2022 is outside the band's periods: it is
the crisis year and the first full year of the file.

## The implied spread, declared

- For each contract the page prints among **Nov-26, Dec-26, Q1-27,
  Summer-27 and Winter-27**: gas in GBP/MWh times the low edge, the central
  case and the high edge. Jan-27 is printed and not used (it lies inside
  Q1-27); Day-ahead is converted for reference only.
- **Winter 2026-27** as the simple mean of Nov-26, Dec-26 and Q1-27 in
  GBP/MWh, times the same three. NBP seasons run October to March and April
  to September; the page prints no Oct-26 (balance of month), so **winter
  2026-27 here is November to March**, and the record says so wherever it
  prints the figure. Summer-27 and Winter-27 are the printed seasons.
- The page's UK ETS Dec-26 line is read, recorded in `evidence/forward.json`
  and **enters no figure**: the implied spread is gas times ratio only.

## Scoring, as a vector, appended as outcomes arrive

For each season, in this order: **(a)** the realised mean gas price (ONS
SAP as 024 reads it, and Ofgem's monthly day-ahead price when it reaches
the season's months) against the pinned forward; **(b)** the realised
ratio A for the season, 024's measure re-run under its declaration for the
new months, against the band; **(c)** the realised mean daily spread
against the implied band. A miss is attributed in that order: **gas moved**
(the curve was wrong, the ratio held); **the ratio moved** (the curve was
right, the structure changed); **both**. The record never says "right" or
"wrong" alone. Outcomes are appended to `evidence/forward.json` and the
RESULTS.md section, never edited in.

## Falsifiers, published with the claim

- **F3** The realised ratio A for a full NBP season (winter 2026-27 as
  November to March, or Summer-27) lies outside the band by more than
  0.15: then the structure moved and the ratio is not a stable multiple.
- **F4** The realised season spread lies outside the implied band although
  the season's realised gas lies within 10 % of the pinned forward: then
  the miss is not gas, and the ratio method failed on its own terms.

## Outcome schedule

A dated watch per season end in the Morpholog v3 record, opened as 013's
are (`open_watch`, about `024`, holder A115, since the resolving
observation is 024's own re-run), so `check-record` refuses to let one
lapse: **w-024-winter-2026-27** due 2027-03-31; **w-024-summer-27** due
2027-09-30; **w-024-winter-27** due 2028-03-31.

## Checks, or the run stops

- C1 the page hashes to its manifest digest; C2 its tables' headers, row
  labels, cell forms and settlement line are the schema pass's.

## What this never claims

- A forecast of gas: the corridor is the forward gas curve times a
  historical ratio band, and it inherits every error of the curve.
- That the ratio is stable: that is what F3 tests.
- Anything a battery can capture: the spread is the day-ahead hourly
  max-minus-min, not a traded product.

## Outputs

`evidence/forward.json` (the implied table with the digests of the page and
of results.json it was derived from, the band's provenance, the watches,
an empty outcomes list); a section "Forward record (amendment 2)" in
RESULTS.md after the cross-check and before the caveats; one chart,
`figures/chart-4-implied-forward-spread.png` and `.svg` (out of git), with
its caption in `figures/captions.md`; the three watches in
`morpholog/batches/110-forward-launch.v3.ndjson` through `scripts/record`.
