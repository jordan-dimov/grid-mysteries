# Schema report: 025 exit-clock inputs (every TEC Register copy held)

Written 2026-10-28 by `run.py --phase schema`; `schema-report.json` beside this file has every copy. 869 usable copies from 2014-01-31 to 2026-10-20 (867 kept under 014's partial-export rule), 32 unreadable. **No exit is counted here**: the continuity figures below are aggregates over copy pairs, never a dated series, and no chain's last sighting is read.

## Copies and gaps

- Project ID printed from 2021-11-26; Project Number from 2024-06-18; regime break 2025-12-01.
- Largest gap between consecutive usable copies: **95 days**. Gaps over 30 days:

| from | to | days |
|---|---|---|
| 2014-02-21 | 2014-04-04 | 42 |
| 2014-04-04 | 2014-05-09 | 35 |
| 2014-05-26 | 2014-07-04 | 39 |
| 2014-07-04 | 2014-10-07 | 95 |
| 2014-10-07 | 2014-11-07 | 31 |
| 2015-07-17 | 2015-09-11 | 56 |

- Suspect copies under the partial-export rule: 2 (2 excluded).

## Key continuity between consecutive kept copies

866 pairs. A pair in which more than 0.5 of the earlier copy's chain keys are absent from the later copy is a **re-keying**:

| earlier | later | keys earlier | keys later | absent | new | absent share | id prefixes earlier | id prefixes later | stitch |
|---|---|---|---|---|---|---|---|---|---|
| 2020-05-28 | 2020-06-05 | 511 | 518 | 299 | 306 | 0.5851 | {} | {} | {'matched': 292, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 43, 'tier name, customer, stage': 214, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 35, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 7, 'unmatched_new': 14} |
| 2021-11-23 | 2021-11-26 | 690 | 691 | 690 | 691 | 1.0000 | {} | {'a03': 691} | {'matched': 690, 'tier project number': 0, 'tier all five': 686, 'tier name, site, stage': 2, 'tier name, customer, stage': 1, 'tier name, customer, site': 1, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 1} |
| 2022-08-19 | 2022-08-24 | 845 | 847 | 838 | 840 | 0.9917 | {'a03': 845} | {'a0l': 840, 'a03': 7} | {'matched': 838, 'tier project number': 0, 'tier all five': 780, 'tier name, site, stage': 2, 'tier name, customer, stage': 54, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 1, 'tier customer, site, stage, cumulative': 1, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 2} |
| 2026-05-19 | 2026-05-22 | 2081 | 2218 | 2081 | 2218 | 1.0000 | {'a0l': 2081} | {'a1f': 2218} | {'matched': 1942, 'tier project number': 1941, 'tier all five': 1, 'tier name, site, stage': 0, 'tier name, customer, stage': 0, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 139, 'unmatched_new': 276} |
| 2026-06-19 | 2026-06-23 | 2217 | 2068 | 2217 | 2068 | 1.0000 | {'a1f': 2217} | {'a0l': 2068} | {'matched': 1941, 'tier project number': 1941, 'tier all five': 0, 'tier name, site, stage': 0, 'tier name, customer, stage': 0, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 276, 'unmatched_new': 127} |

Pairs that are not re-keyings but lose more than 0.05 of their keys, with the stitch's outcome on the vanished and appeared chains (counts only):

| earlier | later | keys earlier | absent | new | absent share | stitch |
|---|---|---|---|---|---|---|
| 2014-05-26 | 2014-07-04 | 381 | 50 | 24 | 0.1312 | {'matched': 1, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 0, 'tier name, customer, stage': 1, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 49, 'unmatched_new': 23} |
| 2014-07-04 | 2014-10-07 | 355 | 32 | 34 | 0.0901 | {'matched': 14, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 12, 'tier name, customer, stage': 0, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 1, 'tier customer, site, stage, cumulative': 1, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 18, 'unmatched_new': 20} |
| 2014-12-05 | 2014-12-19 | 372 | 101 | 97 | 0.2715 | {'matched': 90, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 39, 'tier name, customer, stage': 47, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 3, 'tier customer, site, stage, cumulative': 1, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 11, 'unmatched_new': 7} |
| 2015-01-26 | 2015-02-13 | 369 | 20 | 24 | 0.0542 | {'matched': 8, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 2, 'tier name, customer, stage': 5, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 1, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 12, 'unmatched_new': 16} |
| 2015-03-20 | 2015-03-31 | 369 | 22 | 21 | 0.0596 | {'matched': 15, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 1, 'tier name, customer, stage': 11, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 1, 'tier customer, site, stage, cumulative': 2, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 7, 'unmatched_new': 6} |
| 2015-09-23 | 2015-10-20 | 377 | 24 | 25 | 0.0637 | {'matched': 22, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 10, 'tier name, customer, stage': 3, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 8, 'tier customer, site, stage, cumulative': 1, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 2, 'unmatched_new': 3} |
| 2016-10-28 | 2016-11-08 | 381 | 32 | 0 | 0.0840 | {'matched': 0, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 0, 'tier name, customer, stage': 0, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 32, 'unmatched_new': 0} |
| 2017-04-20 | 2017-04-27 | 377 | 22 | 22 | 0.0584 | {'matched': 22, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 21, 'tier name, customer, stage': 0, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 1, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 0} |
| 2019-06-27 | 2019-07-04 | 460 | 38 | 38 | 0.0826 | {'matched': 38, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 38, 'tier name, customer, stage': 0, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 0} |
| 2020-03-12 | 2020-03-18 | 499 | 43 | 44 | 0.0862 | {'matched': 43, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 3, 'tier name, customer, stage': 40, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 1} |
| 2020-04-02 | 2020-04-09 | 499 | 33 | 36 | 0.0661 | {'matched': 31, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 0, 'tier name, customer, stage': 30, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 1, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 2, 'unmatched_new': 5} |
| 2020-07-30 | 2020-08-06 | 527 | 31 | 32 | 0.0588 | {'matched': 30, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 29, 'tier name, customer, stage': 1, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 1, 'unmatched_new': 2} |
| 2020-08-06 | 2020-08-13 | 528 | 47 | 50 | 0.0890 | {'matched': 47, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 42, 'tier name, customer, stage': 3, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 2, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 3} |
| 2021-10-29 | 2021-11-02 | 681 | 38 | 39 | 0.0558 | {'matched': 38, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 0, 'tier name, customer, stage': 38, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 1} |

Over the other pairs, the share of the earlier copy's keys absent from the later copy: {'n': '861', 'p50': '0.0000', 'p90': '0.0101', 'p99': '0.0596', 'max': '0.2715'}; the share of the later copy's keys new: {'n': '861', 'p50': '0.0026', 'p90': '0.0132', 'p99': '0.0676', 'max': '0.2636'}.

## Vocabularies (cells, all usable copies)

### Agreement Type

| printed | cells |
|---|---|
| Direct Connection | 412089 |
| Directly Connected | 307091 |
| Embedded | 163842 |
| (blank) | 118377 |
| BCA | 1890 |
| BEGA | 454 |
| Null | 43 |

### Project Status

| printed | cells |
|---|---|
| Scoping | 551494 |
| Built | 241569 |
| Consents Approved | 101843 |
| Awaiting Consents | 91157 |
| Under Construction/Commissioning | 16630 |
| (blank) | 547 |
| Terminated | 432 |
| Active | 110 |
| Consented | 4 |

### Plant Type spellings that print a storage technology

| printed | cells |
|---|---|
| Energy Storage System | 237486 |
| Energy Storage System;PV Array (Photo Voltaic/solar) | 104789 |
| Energy Storage System; PV Array (Photo Voltaic/solar) | 59632 |
| Energy Storage System;Wind Onshore | 20827 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore | 9841 |
| Demand;Energy Storage System;PV Array (Photo Voltaic/solar) | 5635 |
| Demand;Energy Storage System | 5353 |
| Energy Storage System;Reactive Compensation | 5162 |
| Demand;Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation | 4380 |
| Battery Storage | 4133 |
| Energy Storage System; Reactive Compensation | 3998 |
| Energy Storage System; Wind Onshore | 3988 |
| Energy Storage System;Nuclear;PV Array (Photo Voltaic/solar);Wind Onshore | 2017 |
| Energy Storage System; PV Array (Photo Voltaic/solar); Wind Onshore | 1648 |
| CCGT (Combined Cycle Gas Turbine); Energy Storage System; OCGT (Open Cycle Gas Turbine) | 1600 |
| Energy Storage System;Gas Reciprocating | 1393 |
| Demand; Energy Storage System; PV Array (Photo Voltaic/solar); Reactive Compensation | 1352 |
| Energy Storage System;OCGT (Open Cycle Gas Turbine) | 1313 |
| Demand; Energy Storage System | 1302 |
| CCGT (Combined Cycle Gas Turbine);Energy Storage System | 1134 |
| Energy Storage System;Wind Offshore | 1049 |
| CCGT (Combined Cycle Gas Turbine);Energy Storage System;OCGT (Open Cycle Gas Turbine) | 910 |
| Demand;Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore | 800 |
| Energy Storage System;Nuclear;PV Array (Photo Voltaic/solar);Reactive Compensation;Wind Onshore | 742 |
| Energy Storage System; Gas Reciprocating | 714 |
| Energy Storage System;Tidal | 690 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation | 672 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation;Wind Onshore | 663 |
| Energy Storage System; OCGT (Open Cycle Gas Turbine) | 637 |
| CCGT (Combined Cycle Gas Turbine);Demand;Energy Storage System | 552 |
| Demand;Energy Storage System;Reactive Compensation | 458 |
| CHP (Combined Heat and Power);Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore | 448 |
| Demand;Energy Storage System;Nuclear;PV Array (Photo Voltaic/solar);Wind Onshore | 369 |
| Energy Storage System; Wind Offshore | 301 |
| Energy Storage System;Pump Storage;Thermal | 276 |
| Demand;Energy Storage System;Wind Onshore | 272 |
| CCGT (Combined Cycle Gas Turbine); Energy Storage System | 266 |
| Energy Storage System; Nuclear; PV Array (Photo Voltaic/solar); Reactive Compensation; Wind Onshore | 256 |
| Demand; Energy Storage System; PV Array (Photo Voltaic/solar) | 251 |
| Energy Storage System; Nuclear; PV Array (Photo Voltaic/solar); Wind Onshore | 251 |
| Energy Storage System;Hydro;Nuclear;PV Array (Photo Voltaic/solar);Wind Onshore | 241 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Wind Offshore | 241 |
| Energy Storage System; PV Array (Photo Voltaic/solar); Reactive Compensation | 172 |
| CCGT (Combined Cycle Gas Turbine);Demand;Energy Storage System;Hydrogen;OCGT (Open Cycle Gas Turbine) | 172 |
| Energy Storage System; PV Array (Photo Voltaic/solar); Wind Offshore | 146 |
| CCGT (Combined Cycle Gas Turbine); Demand; Energy Storage System | 144 |
| CCGT (Combined Cycle Gas Turbine);Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore | 127 |
| Demand; Energy Storage System; Wind Offshore | 120 |
| CCGT (Combined Cycle Gas Turbine);Demand;Energy Storage System;OCGT (Open Cycle Gas Turbine);Hydrogen | 116 |
| Energy Storage System;Hydrogen;PV Array (Photo Voltaic/solar);Wind Onshore | 86 |
| Energy Storage System; PV Array (Photo Voltaic/solar); Reactive Compensation; Wind Onshore | 78 |
| CCGT (Combined Cycle Gas Turbine);Demand;Energy Storage System;OCGT (Open Cycle Gas Turbine) | 75 |
| CHP (Combined Heat and Power);Energy Storage System | 64 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore;Hydrogen | 34 |
| CHP (Combined Heat and Power); Energy Storage System | 32 |
| Energy Storage System; Hydro; Nuclear; PV Array (Photo Voltaic/solar); Wind Onshore | 31 |
| Energy Storage System;Thermal | 9 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Waste | 8 |
| Energy Storage System;Hydrogen | 7 |
| Demand;Energy Storage System;Wind Offshore | 4 |
| Demand, Energy Storage System, Wind Offshore | 2 |
| Energy storage system | 1 |

## Per copy (first and last five; every copy in schema-report.json)

| t_public | regime | kept | rows | chains | id chains | no-id chains | multi-row chains | blank Project Status | blank Plant Type | blank Agreement Type | blank MW Effective From |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2014-01-31 | old | True | 420 | 368 | 0 | 0 | 28 | 0 | 0 | n/a | 130 |
| 2014-02-13 | old | True | 412 | 367 | 0 | 0 | 27 | 0 | 0 | n/a | 130 |
| 2014-02-17 | old | True | 417 | 370 | 0 | 0 | 32 | 0 | 0 | n/a | 129 |
| 2014-02-21 | old | True | 410 | 370 | 0 | 0 | 25 | 0 | 0 | n/a | 128 |
| 2014-04-04 | old | True | 405 | 368 | 0 | 0 | 23 | 0 | 0 | n/a | 175 |
| 2026-10-06 | new | True | 2196 | 2054 | 2054 | 0 | 122 | 0 | 0 | 0 | 365 |
| 2026-10-09 | new | True | 2225 | 2082 | 2082 | 0 | 123 | 0 | 0 | 0 | 368 |
| 2026-10-13 | new | True | 2225 | 2082 | 2082 | 0 | 123 | 0 | 0 | 0 | 368 |
| 2026-10-16 | new | True | 2226 | 2082 | 2082 | 0 | 124 | 0 | 0 | 0 | 368 |
| 2026-10-20 | new | True | 2227 | 2083 | 2083 | 0 | 124 | 0 | 0 | 0 | 369 |
