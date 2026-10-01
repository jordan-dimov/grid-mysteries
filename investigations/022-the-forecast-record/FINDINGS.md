# 022 — The Forecast Record, issue 1: findings

*Declaration `DECLARATION.md`, SHA-256 `b8e6d53bf8e2529ac6caeaf419eb419b76c5f9f12927d647778f382cdd19d2e5`, frozen and witnessed before any figure; acquisition plan `ACQUISITION.md`, SHA-256 `962cb9b5db8d33a7ae14fe3b516dd5f999936911040316a4fcc03e8aeeb0e188`; rule version `b8e6d53b`; run 2026-10-01, computed 2026-10-01T16:58:03+00:00. Every figure below is as published by the publisher named, on the date named, and read from the pinned page whose digest the evidence carries. Nothing here attributes an error to a cause or names an optimiser.*

## The mystery

> Battery revenue forecasts move hundreds of millions of pounds of fund value, and nobody has ever published how accurate they were.

## The finding

**The listed funds were valued on revenue curves. Their own documents (59 NAV announcements and 48 prospectus and placing documents among 280 pinned, back to 2021-03-08) cite those curves without a per-year level anyone can score, and the forecaster's public pages carry only in-year and horizon figures. Nobody who relied on these numbers can check them in public before 2029-01-01.** Of the 4 forecast vintage(s) the reading rules found on the public pages of GRID (fund RNS), HEIT (fund RNS), Modo Energy, none is scorable today (F1): each covers a period that has not ended, or the year of its own publication (in-year, never scored), or has no published outturn of its own scope. The per-asset cut is the paid product behind the public record. The not-yet-scorable table below is the result of issue 1, with the date each vintage becomes scorable.

## Scored comparisons

None.

## Not yet scorable (a result, not a gap)

| vintage | scope | period | forecast | status | scorable after | note |
|---|---|---|---|---|---|---|
| HEIT (fund RNS), 2023-05-23, `https://www.investegate.co.uk/announcement/rns/harmony-energy-income-trust--heit/trading-update-and-net-asset-value-/7538293` | HEIT portfolio-excl-cm | 2023 | £121,000 | in-year, never scored | - | published 2023-05-23, inside the period it covers |
| Modo Energy, 2024-07-24, `https://modoenergy.com/research/en/v31-gb-forecast-update-battery-energy-storage-modelling-changes-revenue-impact` | 2h | 2024 | £81,000 | in-year, never scored | - | published 2024-07-24, inside the period it covers |
| Modo Energy, 2025-01-13, `https://modoenergy.com/research/en/jan-24-forecast-update-bess-revenues-intraday-prices-dispatch-battery-energy-storage-model` | 2h | 2026 to 2028 | £87,000 | not yet scorable | 2029-01-01 | no realised figure of scope '2h' for 2026, 2027, 2028 |
| GRID (fund RNS), 2025-09-24, `https://greshamhouse.com/wp-content/uploads/2025/09/Gresham-House-Energy-Storage-Fund-Interim-Report-to-30-June-2025.pdf` | 2h | 2028 | £90,000 | not yet scorable | 2029-01-01 | no realised figure of scope '2h' for 2028 |

## The fund-cited forecast figures (the only fund-side forecasts in existence)

| publisher | published | period | figure | scope | Capacity Market | cited source | as printed | page |
|---|---|---|---|---|---|---|---|---|
| HEIT (fund RNS) | 2023-05-23 | 2023 | £121,000 | HEIT portfolio-excl-cm | excluded | source unnamed | £121,000 per MW/Yr | `https://www.investegate.co.uk/announcement/rns/harmony-energy-income-trust--heit/trading-update-and-net-asset-value-/7538293` |
| HEIT (fund RNS) | 2023-05-23 | 2024 | £123,000 | HEIT portfolio-excl-cm | excluded | source unnamed | £123,000 per MW/Yr | `https://www.investegate.co.uk/announcement/rns/harmony-energy-income-trust--heit/trading-update-and-net-asset-value-/7538293` |
| GRID (fund RNS) | 2025-09-24 | 2028 | £90,000 | 2h | not stated | third-party | £90k/MW/Yr | `https://greshamhouse.com/wp-content/uploads/2025/09/Gresham-House-Energy-Storage-Fund-Interim-Report-to-30-June-2025.pdf` (the same figure in `https://www.investegate.co.uk/announcement/rns/gresham-house-energy-storage-fund--grid/half-year-results-and-capital-allocation-policy/9127370`, one publication) |

## Scope mismatches (both figures listed, nothing adjusted)


A fund's assumption is for its own portfolio, under its own revenue definition (here, excluding the Capacity Market), over its own assets and durations. The fleet outturn is an index over every battery in Great Britain under the index's methodology. The two differ in population, in what counts as revenue and in duration mix, so forecast minus outturn would subtract one quantity from another and the difference would be a number without a meaning. Both figures are printed; the subtraction is not done.

| vintage | forecast scope | period | forecast | realised figure (its scope) | note |
|---|---|---|---|---|---|
| HEIT (fund RNS), 2023-05-23, `https://www.investegate.co.uk/announcement/rns/harmony-energy-income-trust--heit/trading-update-and-net-asset-value-/7538293` | HEIT portfolio-excl-cm | 2024 | £123,000 | £50,000 (fleet) | realised figure published for scope 'fleet', forecast is for 'HEIT portfolio-excl-cm'; reported, never adjusted; other scopes realised: GRID portfolio |

## The realised side, as published

### Annual figures read (R-R5)

| publisher | published | scope | year | figure | as printed | page |
|---|---|---|---|---|---|---|
| GSF (fund RNS) | 2023-07-17 | GSF portfolio | 2022 | £157,000 | £157,000/MW/yr | `https://www.investegate.co.uk/announcement/rns/gore-street-energy-storage-fund--gsf/final-results/7635539` |
| Modo Energy | 2024-01-29 | fleet | 2023 | £51,000 | £51k/MW/year | `https://modoenergy.com/research/en/capacity-market-revenues-battery-energy-storage-auction-derating-factors-december-2023` |
| Modo Energy | 2025-02-18 | fleet | 2024 | £50,000 | £50k/MW/year | `https://modoenergy.com/research/en/battery-revenues-operational-strategy-2024-gb-benchmark-year-review` |
| GRID (fund RNS) | 2025-04-22 | GRID portfolio | 2024 | £91,000 | £91k/MW/yr | `https://greshamhouse.com/wp-content/uploads/2025/04/GRID-Annual-Report-31-December-2024.pdf` |
| GRID (fund RNS) | 2025-04-22 | GRID portfolio | 2024 | £59,800 | £59.8k/ MW | `https://greshamhouse.com/wp-content/uploads/2025/04/GRID-Annual-Report-31-December-2024.pdf` |
| Modo Energy | 2025-05-08 | fleet | 2024 | £50,000 | £50k/MW/year | `https://modoenergy.com/research/en/battery-energy-storage-revenues-great-britain-gb-april-2025-benchmark-me-bess-` |
| GRID (fund RNS) | 2026-04-21 | GRID portfolio | 2025 | £68,600 | £68.6k/MW/year | `https://www.investegate.co.uk/announcement/rns/gresham-house-energy-storage-fund--grid/full-year-results-to-31-december-2025/9529253` |

More than one figure read for one scope and year (R-S3 reads one and names the others):

- GRID portfolio 2024: read £59,800 (£59.8k/ MW); also read £91,000 (£91k/MW/yr, 2025-04-22). Where the figures differ by more than rounding, the sentences are in `evidence/figures.ndjson` and the difference is not resolved here.
- fleet 2024: read £50,000 (£50k/MW/year); also read £50,000 (£50k/MW/year, 2025-02-18). Where the figures differ by more than rounding, the sentences are in `evidence/figures.ndjson` and the difference is not resolved here.

### Monthly index figures read (R-R5), by scope and year (R-S4)

| scope | year | months read | complete | mean of twelve |
|---|---|---|---|---|
| 1h | 2024 | 2 | no | - |
| fleet | 2023 | 4 | no | - |
| fleet | 2024 | 2, 3, 4, 5, 7, 8, 9, 10, 11, 12 | no | - |
| fleet | 2025 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 | yes | £67,717 |
| fleet | 2026 | 1, 2, 3, 4, 5, 6, 7, 8 | no | - |
| fleet-incl-cm | 2024 | 4 | no | - |

### Months printed differently on different pages (F4): both figures, both sources, both dates; the latest published read, nothing resolved

- fleet 2024-10: read £58,000 from `https://modoenergy.com/research/en/battery-energy-storage-research-roundup-great-britain-october-2024-revenues-buildout-forecast-capex-winter`; others £50,300 on 2024-11-19; £58,000 on 2024-11-06
- fleet 2025-01: read £79,000 from `https://modoenergy.com/research/en/battery-energy-storage-revenues-operations-january-2025-scotland-balancing-mechanism`; others £88,000 on 2025-02-07; £79,000 on 2025-02-28; £88,000 on 2025-02-14; £88,000 on 2025-02-14
- fleet 2024-09: read £37,500 from `https://modoenergy.com/research/en/gb-battery-energy-storage-operations-september-2024-benchmark-balancing-mechanism`; others £48,000 on 2024-10-04; £48,000 on 2024-10-04
- fleet 2024-08: read £46,000 from `https://modoenergy.com/research/en/gb-battery-energy-storage-revenue-august-2024-benchmark-balancing-mechanism`; others £46,000 on 2024-09-11; £56,000 on 2024-09-04; £56,000 on 2024-09-04

## Revisions between consecutive vintages (R-V)

No two consecutive vintages print a forecast for the same scope and period, so no revision pair exists; P-C is undecided.

## Per-asset and subset figures on the public pages (listed, not read)

These strings name an asset or the best-performing part of the fleet. The rules read none into any comparison; they are listed because they are public and an adviser may want them. The other strings declined by the same rule (swap basis risk, uplift ranges for individual batteries) stay in `evidence/figures.ndjson` under that rule.

| published | as printed | sentence | page |
|---|---|---|---|
| 2024-04-19 | £150k/MW/year | So, why has this happened, and how have some batteries earned upwards of an annualized £150k/MW/year on some days? | `https://modoenergy.com/research/en/negative-power-prices-location-balancing-mechanism-gb-benchmarking-battery-energy-storage` |
| 2024-06-06 | £70k/MW/year | However, one system implemented new strategies to earn over £70k/MW/year. | `https://modoenergy.com/research/en/battery-energy-storage-revenues-may-2024-balancing-mechanism-gb-benchmark` |
| 2025-02-07 | £122k/MW/year | Wishaw was the highest-earning battery, reaching £122k/MW/year , followed by Coventry, both leveraging Balancing Mechanism and wholesale trading strategies . | `https://modoenergy.com/research/en/battery-operations-revenues-strategy-gb-benchmark-december-2024-balancing-mechanism-wishaw-coventry` |
| 2025-02-14 | £122k/MW/year | Wishaw was the highest-earning battery, reaching £122k/MW/year, followed by Coventry. | `https://modoenergy.com/research/en/gb-research-roundup-january-2025-battery-energy-storage-great-britain-revenues-markets-wholesale-capacity-market-balancing-mechanism` |
| 2025-02-28 | £136k/MW/year | Jamesfield 2 was the highest-earning battery, earning £136k/MW/year - followed by three other batteries located within 20 miles. | `https://modoenergy.com/research/en/battery-energy-storage-revenues-operations-january-2025-scotland-balancing-mechanism` |
| 2025-02-28 | £132k/MW/year | However, the four highest-earning systems earned £132k/MW/year on average. | `https://modoenergy.com/research/en/battery-energy-storage-revenues-operations-january-2025-scotland-balancing-mechanism` |
| 2025-07-31 | £100k/MW/year | However, the top-performing systems earned over £100k/MW/year. | `https://modoenergy.com/research/en/gb-bess-revenues-battery-energy-storage-balancing-mechanism-wholesale-h1-2025-tclc` |
| 2026-06-04 | £94k/MW/year | In the last 12 months, the top quartile of two-hour batteries (which Modo Energy forecasts are calibrated to) have earned £94k/MW/year, 55% higher than the index over that period. | `https://modoenergy.com/research/en/gb-bess-revenues-may-2026-balancing-mechanism-negative-wholesale-spreads-wind` |

## What the reading rules did with every figure-looking string

| rule | strings |
|---|---|
| R-R2 a price per MWh, not a revenue per MW | 197 |
| R-R2 an hourly rate | 187 |
| R-R2 no period unit | 170 |
| R-R3 a revenue component, not the total | 120 |
| R-R0 JSON payload | 93 |
| R-R5 monthly figure | 58 |
| R-R5 a partial period (half, quarter, season or to date) | 50 |
| R-R5 period not stated | 48 |
| R-R0 title or navigation duplicate | 42 |
| R-R0 PDF sentence glued to page furniture | 39 |
| R-R4 potential, required, contracted or assumed, not a forecast or an outturn | 35 |
| R-R3 a named asset or subset, not the population | 22 |
| R-R2 a change, not a level | 21 |
| R-R6 published before 2021 | 20 |
| R-R5 another month than the page's own | 17 |
| R-R2 the starting point of a stated change, not its level | 17 |
| R-R2 range, not a point figure | 15 |
| R-R3 no population named in the clause | 12 |
| R-R5 a day, not a month or a year | 11 |
| R-R5 a fund figure dated by a month, not a calendar year | 11 |
| R-R5 annual figure, basis realised | 7 |
| R-R6 published before 2023 | 6 |
| R-R7 the page prints figures for its own month that differ by more than rounding; none read | 2 |
| R-R5 the year of publication, not complete | 2 |
| R-R5 annual figure, basis forecast, cited by the fund (third-party) | 2 |
| R-R5 annual figure, basis forecast, cited by the fund (source unnamed) | 2 |
| R-R7 the same month's figure, printed less precisely than another string on the page | 1 |
| R-R5 horizon figure, basis forecast | 1 |
| R-R5 endyear figure, basis forecast | 1 |
| R-R2 a multiplier other than k | 1 |

F1 (no scorable vintage): fires. F2 (the rules cannot read the corpus): silent, 28 of 407 per-year strings on English pages declined for a period or population not stated (6.9 %, threshold 33.3 %). F3 (a committed row would change): refused before writing, so silent by construction. F4 (the realised side restates itself beyond rounding): 4 month(s).

## Propositions

- **P-A**: undecided.
- **P-B**: undecided.
- **P-C**: undecided.
- GRID (fund RNS): P-A undecided, P-B undecided, P-C undecided (0 pair(s)).
- HEIT (fund RNS): P-A undecided, P-B undecided, P-C undecided (0 pair(s)).
- Modo Energy: P-A undecided, P-B undecided, P-C undecided (0 pair(s)).

## Method, in short

Every page was pinned under a sealed plan. A schema pass listed every figure-looking string as printed. The reading rules were written against that pass and frozen before any figure was read. A forecast is a published headline for a stated future period. An outturn is a published realised figure for a past calendar year, or the mean of twelve published monthly figures where no annual figure is published. A year counts only if the forecast was published before it began. A forecast and an outturn of different populations are listed side by side and never adjusted. Every string is in the evidence with the rule that read or declined it. No row changes once committed.

## What this never claims

That any forecast was wrong, careless or interested; that any error had a cause; that one publisher's forecasts are better or worse than another's; that an index level is a market fact rather than a published figure under its publisher's methodology; that a fund's reported revenue per megawatt is comparable to a fleet figure; or that any of this is a forecast of future revenue. Nothing here uses, reconstitutes or re-publishes any index as a benchmark; the figures quoted are those their publishers chose to publish on public pages.

## The record

`evidence/figures.ndjson`, `evidence/comparisons.ndjson`, `evidence/revisions.ndjson` and `evidence/months.json`, every row under rule version `b8e6d53b`; the pinned pages by digest in `evidence/pages-manifest.json` and `evidence/rns-manifest.json`; the schema reports under `archives/modo-pages-022/` (SHA-256 `4bbe6d793e97e73777de7e2e3c72dbf53dd33ed1440bf4f68aff1f79ac281ab6`) and `archives/rns-grid-022/` (SHA-256 `16820033b7b175ea1cf26b0cbd0901442bb88449f93017033a4429221aeba696`); `scripts/check`.
