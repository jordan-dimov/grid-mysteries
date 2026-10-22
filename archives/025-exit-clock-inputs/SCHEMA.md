# Schema report: 025 exit-clock inputs (every TEC Register copy held)

Written 2026-10-22 by `run.py --phase schema`; `schema-report.json` beside this file has every copy. 793 usable copies from 2014-01-31 to 2026-10-20 (791 kept under 014's partial-export rule), 32 unreadable. **No exit is counted here**: the continuity figures below are aggregates over copy pairs, never a dated series, and no chain's last sighting is read.

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
| 2025-01-28 | 2025-03-21 | 52 |
| 2025-04-01 | 2025-07-01 | 91 |
| 2026-05-19 | 2026-08-22 | 95 |

- Suspect copies under the partial-export rule: 2 (2 excluded).

## Key continuity between consecutive kept copies

790 pairs. A pair in which more than 0.5 of the earlier copy's chain keys are absent from the later copy is a **re-keying**:

| earlier | later | keys earlier | keys later | absent | new | absent share | id prefixes earlier | id prefixes later | stitch |
|---|---|---|---|---|---|---|---|---|---|
| 2020-05-28 | 2020-06-05 | 511 | 518 | 299 | 306 | 0.5851 | {} | {} | {'matched': 292, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 43, 'tier name, customer, stage': 214, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 35, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 7, 'unmatched_new': 14} |
| 2021-11-23 | 2021-11-26 | 682 | 683 | 682 | 683 | 1.0000 | {} | {'a03': 683} | {'matched': 682, 'tier project number': 0, 'tier all five': 680, 'tier name, site, stage': 0, 'tier name, customer, stage': 1, 'tier name, customer, site': 1, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 1} |
| 2022-08-19 | 2022-08-24 | 833 | 834 | 827 | 828 | 0.9928 | {'a03': 833} | {'a0l': 828, 'a03': 6} | {'matched': 827, 'tier project number': 0, 'tier all five': 767, 'tier name, site, stage': 4, 'tier name, customer, stage': 54, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 1, 'tier customer, site, stage, cumulative': 1, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 1} |

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
| 2020-07-30 | 2020-08-06 | 518 | 31 | 32 | 0.0598 | {'matched': 30, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 29, 'tier name, customer, stage': 1, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 1, 'unmatched_new': 2} |
| 2020-08-06 | 2020-08-13 | 519 | 46 | 49 | 0.0886 | {'matched': 46, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 41, 'tier name, customer, stage': 3, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 2, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 3} |
| 2021-10-29 | 2021-11-02 | 673 | 38 | 39 | 0.0565 | {'matched': 38, 'tier project number': 0, 'tier all five': 0, 'tier name, site, stage': 0, 'tier name, customer, stage': 38, 'tier name, customer, site': 0, 'tier name, stage, cumulative': 0, 'tier customer, site, stage, cumulative': 0, 'tier name alone': 0, 'ambiguous_old': 0, 'ambiguous_new': 0, 'unmatched_old': 0, 'unmatched_new': 1} |

Over the other pairs, the share of the earlier copy's keys absent from the later copy: {'n': '787', 'p50': '0.0006', 'p90': '0.0118', 'p99': '0.0637', 'max': '0.2715'}; the share of the later copy's keys new: {'n': '787', 'p50': '0.0027', 'p90': '0.0158', 'p99': '0.0757', 'max': '0.2636'}.

## Vocabularies (cells, all usable copies)

### Agreement Type

| printed | cells |
|---|---|
| Direct Connection | 282589 |
| Directly Connected | 267864 |
| Embedded | 130535 |
| (blank) | 118376 |
| BCA | 1890 |
| BEGA | 454 |
| Null | 24 |

### Project Status

| printed | cells |
|---|---|
| Scoping | 417843 |
| Built | 213950 |
| Consents Approved | 82009 |
| Awaiting Consents | 74131 |
| Under Construction/Commissioning | 12744 |
| (blank) | 510 |
| Terminated | 431 |
| Active | 110 |
| Consented | 4 |

### Plant Type spellings that print a storage technology

| printed | cells |
|---|---|
| Energy Storage System | 178120 |
| Energy Storage System;PV Array (Photo Voltaic/solar) | 72165 |
| Energy Storage System; PV Array (Photo Voltaic/solar) | 46184 |
| Energy Storage System;Wind Onshore | 13796 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore | 6568 |
| Battery Storage | 4133 |
| Demand;Energy Storage System;PV Array (Photo Voltaic/solar) | 4082 |
| Demand;Energy Storage System | 3780 |
| Energy Storage System;Reactive Compensation | 3635 |
| Energy Storage System; Wind Onshore | 3496 |
| Demand;Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation | 3007 |
| Energy Storage System; Reactive Compensation | 2682 |
| Energy Storage System; PV Array (Photo Voltaic/solar); Wind Onshore | 1638 |
| Energy Storage System;Nuclear;PV Array (Photo Voltaic/solar);Wind Onshore | 1377 |
| Demand; Energy Storage System; PV Array (Photo Voltaic/solar); Reactive Compensation | 1351 |
| Demand; Energy Storage System | 1293 |
| CCGT (Combined Cycle Gas Turbine); Energy Storage System; OCGT (Open Cycle Gas Turbine) | 970 |
| Energy Storage System;OCGT (Open Cycle Gas Turbine) | 868 |
| Energy Storage System;Gas Reciprocating | 861 |
| CCGT (Combined Cycle Gas Turbine);Energy Storage System | 760 |
| Energy Storage System;Wind Offshore | 725 |
| CCGT (Combined Cycle Gas Turbine);Energy Storage System;OCGT (Open Cycle Gas Turbine) | 640 |
| Demand;Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore | 588 |
| Energy Storage System;Nuclear;PV Array (Photo Voltaic/solar);Reactive Compensation;Wind Onshore | 507 |
| Energy Storage System;Tidal | 495 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation;Wind Onshore | 466 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation | 466 |
| Energy Storage System; Gas Reciprocating | 431 |
| CCGT (Combined Cycle Gas Turbine);Demand;Energy Storage System | 396 |
| Demand;Energy Storage System;Reactive Compensation | 313 |
| Energy Storage System; Wind Offshore | 300 |
| CHP (Combined Heat and Power);Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore | 277 |
| CCGT (Combined Cycle Gas Turbine); Energy Storage System | 264 |
| Energy Storage System; Nuclear; PV Array (Photo Voltaic/solar); Reactive Compensation; Wind Onshore | 255 |
| Energy Storage System; Nuclear; PV Array (Photo Voltaic/solar); Wind Onshore | 251 |
| Demand; Energy Storage System; PV Array (Photo Voltaic/solar) | 250 |
| Energy Storage System; OCGT (Open Cycle Gas Turbine) | 233 |
| Demand;Energy Storage System;Nuclear;PV Array (Photo Voltaic/solar);Wind Onshore | 219 |
| Energy Storage System;Pump Storage;Thermal | 198 |
| Demand;Energy Storage System;Wind Onshore | 195 |
| Energy Storage System;Hydro;Nuclear;PV Array (Photo Voltaic/solar);Wind Onshore | 166 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Wind Offshore | 166 |
| Energy Storage System; PV Array (Photo Voltaic/solar); Reactive Compensation | 156 |
| Energy Storage System; PV Array (Photo Voltaic/solar); Wind Offshore | 145 |
| CCGT (Combined Cycle Gas Turbine); Demand; Energy Storage System | 144 |
| Demand; Energy Storage System; Wind Offshore | 120 |
| CCGT (Combined Cycle Gas Turbine);Demand;Energy Storage System;Hydrogen;OCGT (Open Cycle Gas Turbine) | 110 |
| CCGT (Combined Cycle Gas Turbine);Demand;Energy Storage System;OCGT (Open Cycle Gas Turbine);Hydrogen | 102 |
| CCGT (Combined Cycle Gas Turbine);Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore | 96 |
| Energy Storage System; PV Array (Photo Voltaic/solar); Reactive Compensation; Wind Onshore | 78 |
| CHP (Combined Heat and Power);Energy Storage System | 64 |
| Energy Storage System;Hydrogen;PV Array (Photo Voltaic/solar);Wind Onshore | 55 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore;Hydrogen | 34 |
| CHP (Combined Heat and Power); Energy Storage System | 32 |
| Energy Storage System; Hydro; Nuclear; PV Array (Photo Voltaic/solar); Wind Onshore | 31 |
| Energy Storage System;Hydrogen | 6 |
| Demand;Energy Storage System;Wind Offshore | 4 |
| CCGT (Combined Cycle Gas Turbine);Demand;Energy Storage System;OCGT (Open Cycle Gas Turbine) | 3 |
| Demand, Energy Storage System, Wind Offshore | 2 |
| Energy Storage System;PV Array (Photo Voltaic/solar);Waste | 2 |
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
