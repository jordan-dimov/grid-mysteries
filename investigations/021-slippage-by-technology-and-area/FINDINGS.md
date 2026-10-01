# 021 — Where the dates move: 014's slippage series by plant type and by host transmission owner

*Declaration `DECLARATION.md`, SHA-256 `76ad7dc36ffda6373f798bb3dad08aa4ea8083262037c48a69ecadeb5f6a91d1`, frozen and witnessed before any figure here was computed. Run 2026-10-01 under seal `76ad7dc3`, rule version `76ad7dc3`. Every figure is from `evidence/comparisons.ndjson` and `evidence/groups.ndjson`, which carry three decimals; this page shows megawatt-years to the nearest whole unit and shares to 0.1 %.*

## The mystery

When Britain's contracted grid-connection dates move, in aggregate, is the movement concentrated in particular technologies or in particular transmission areas, or is it spread in proportion to the capacity each holds?

## The reading, and what it is not

The date read here is the one in each project's connection agreement as the TEC Register prints it, moved by agreed variation between two copies of the register; it is never a promise, and nothing here says why any of them moved. The reading offered is **how much information a register date carries by technology and by area**: a group whose share of net movement exceeds its share of dated capacity is a group whose dates, over that window and under this reading, carried less information than the rest. It is not a reading of who is to blame. Cause, from 006: of the 213 slips of 24 months or more in 005's population, 60 % were project-led, 26 % works-led and 14 % unattributable; nothing here revises that split or attributes any group's movement to a cause.

The population and arithmetic are 014 version 4's, unchanged (C1 and C2 pass, see the expert corner): for every project-stage present in both copies with a date in both, its capacity at the baseline times the years its date moved, later positive. A project-stage whose plant type or host TO reads differently at the two ends is in the **key changed** bucket and is never reassigned (R2); a blank key is the group (blank) (R3); compound plant types are kept whole (R1). Every group's net is split into the part the register's stage labels determine and the part that depends on the identity rule, as 014 version 4 splits the series.

## The headline window, 19 July 2024 to 22 July 2025

Net movement +57,823 MW-years under version 2's rule over 889 project-stages dated at both ends and weighing 292,764 MW; +53,221 of it is movement the register's stage labels determine, and 88 project groups with an undetermined pairing add +4,602 under version 2's rule or +8,322 under content matching (014 version 4). Key changed between the two copies: 5 dated project-stages, 812 MW, +67 MW-years; unified by the spelling table: 0. Cause, from 006: of the 213 slips of 24 months or more in 005's population, 60 % were project-led, 26 % works-led and 14 % unattributable; nothing here revises that split or attributes any group's movement to a cause.

### By host transmission owner

| Host TO | Units at baseline / matched | Dated project-stages (later / earlier / unchanged) | Dated capacity, MW | Share of capacity | Net, MW-years (014 v2) | Determined | Undetermined (v2 / content) | Share of net | Share of determined | Concentration, points | Thin (R7) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NGET | 1,151 / 748 | 601 (118 / 21 / 462) | 236,778 | 80.9 % | +47,258 | +39,933 | +7,325 / +11,069 | 81.7 % | 75.0 % | +0.8 | no |
| SHET | 338 / 255 | 171 (44 / 4 / 123) | 38,416 | 13.1 % | +4,376 | +7,903 | -3,527 / -3,577 | 7.6 % | 14.8 % | -5.5 | no |
| SPT | 374 / 122 | 112 (30 / 2 / 80) | 16,757 | 5.7 % | +6,123 | +5,319 | +804 / +829 | 10.6 % | 10.0 % | +4.9 | yes |
| OFTO | 17 / 15 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | no |
| key changed | 0 / 7 | 5 (1 / 0 / 4) | 812 | 0.3 % | +67 | +67 | +0 / +0 | 0.1 % | 0.1 % | -0.2 | — |

Marks: none.

### By plant type

Net movement +57,823 MW-years under version 2's rule over 889 project-stages dated at both ends and weighing 292,764 MW; +53,221 of it is movement the register's stage labels determine, and 88 project groups with an undetermined pairing add +4,602 under version 2's rule or +8,322 under content matching (014 version 4). Key changed between the two copies: 92 dated project-stages, 54,434 MW, +14,028 MW-years; unified by the spelling table: 0. Cause, from 006: of the 213 slips of 24 months or more in 005's population, 60 % were project-led, 26 % works-led and 14 % unattributable; nothing here revises that split or attributes any group's movement to a cause.

| Plant type | Units at baseline / matched | Dated project-stages (later / earlier / unchanged) | Dated capacity, MW | Share of capacity | Net, MW-years (014 v2) | Determined | Undetermined (v2 / content) | Share of net | Share of determined | Concentration, points | Thin (R7) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Energy Storage System;PV Array (Photo Voltaic/solar) | 424 / 211 | 211 (50 / 6 / 155) | 69,851 | 23.9 % | +21,160 | +14,078 | +7,082 / +7,970 | 36.6 % | 26.5 % | +12.7 | yes |
| Energy Storage System | 576 / 306 | 270 (42 / 12 / 216) | 57,891 | 19.8 % | +16,562 | +15,445 | +1,117 / +1,142 | 28.6 % | 29.0 % | +8.8 | no |
| Wind Offshore | 149 / 91 | 50 (5 / 3 / 42) | 47,688 | 16.3 % | -7,011 | -3,700 | -3,310 / -2,508 | -12.1 % | -7.0 % | -28.4 | no |
| Wind Onshore | 306 / 173 | 122 (40 / 1 / 81) | 12,210 | 4.2 % | +5,473 | +5,007 | +466 / +466 | 9.5 % | 9.4 % | +5.3 | no |
| Demand;Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation | 18 / 13 | 13 (0 / 0 / 13) | 7,007 | 2.4 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -2.4 | no |
| Pump Storage | 18 / 10 | 7 (2 / 0 / 5) | 4,596 | 1.6 % | +2,798 | +2,798 | +0 / +0 | 4.8 % | 5.3 % | +3.2 | no |
| Nuclear | 12 / 8 | 3 (0 / 0 / 3) | 4,280 | 1.5 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -1.5 | no |
| PV Array (Photo Voltaic/solar) | 39 / 18 | 17 (4 / 0 / 13) | 3,814 | 1.3 % | +606 | +606 | +0 / +0 | 1.0 % | 1.1 % | -0.3 | yes |
| Energy Storage System;Wind Onshore | 38 / 25 | 24 (7 / 0 / 17) | 3,621 | 1.2 % | +1,053 | +1,053 | +0 / +0 | 1.8 % | 2.0 % | +0.6 | no |
| Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore | 20 / 8 | 8 (0 / 0 / 8) | 3,149 | 1.1 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -1.1 | yes |
| Energy Storage System;Nuclear;PV Array (Photo Voltaic/solar);Reactive Compensation;Wind Onshore | 3 / 3 | 3 (0 / 0 / 3) | 3,000 | 1.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -1.0 | no |
| Energy Storage System;Wind Offshore | 5 / 3 | 2 (0 / 0 / 2) | 3,000 | 1.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -1.0 | no |
| CCGT (Combined Cycle Gas Turbine);Energy Storage System | 2 / 2 | 2 (0 / 1 / 1) | 2,500 | 0.9 % | -2,502 | +0 | -2,502 / -2,502 | -4.3 % | 0.0 % | -5.2 | no |
| Energy Storage System;OCGT (Open Cycle Gas Turbine) | 8 / 8 | 7 (0 / 0 / 7) | 2,250 | 0.8 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -0.8 | no |
| Energy Storage System;Nuclear;PV Array (Photo Voltaic/solar);Wind Onshore | 4 / 2 | 2 (0 / 0 / 2) | 2,000 | 0.7 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -0.7 | no |
| CCGT (Combined Cycle Gas Turbine);Energy Storage System;OCGT (Open Cycle Gas Turbine) | 5 / 1 | 1 (0 / 0 / 1) | 1,800 | 0.6 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -0.6 | yes |
| Energy Storage System;Reactive Compensation | 26 / 14 | 14 (3 / 0 / 11) | 1,595 | 0.5 % | +1,345 | +1,269 | +76 / +101 | 2.3 % | 2.4 % | +1.8 | no |
| CCGT (Combined Cycle Gas Turbine) | 53 / 36 | 3 (0 / 0 / 3) | 1,465 | 0.5 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -0.5 | no |
| Demand;Energy Storage System;PV Array (Photo Voltaic/solar) | 5 / 2 | 2 (2 / 0 / 0) | 1,332 | 0.5 % | +2,663 | +1,999 | +664 / +664 | 4.6 % | 3.8 % | +4.1 | yes |
| Demand;Energy Storage System | 13 / 8 | 8 (0 / 0 / 8) | 1,300 | 0.4 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -0.4 | no |
| Energy Storage System;Hydro;Nuclear;PV Array (Photo Voltaic/solar);Wind Onshore | 1 / 1 | 1 (0 / 0 / 1) | 1,000 | 0.3 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -0.3 | no |
| Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation | 4 / 2 | 2 (0 / 0 / 2) | 900 | 0.3 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -0.3 | no |
| OCGT (Open Cycle Gas Turbine) | 16 / 14 | 3 (0 / 0 / 3) | 897 | 0.3 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -0.3 | no |
| Biomass | 10 / 9 | 2 (0 / 1 / 1) | 210 | 0.1 % | -39 | -39 | +0 / +0 | -0.1 % | -0.1 % | -0.2 | no |
| Tidal | 10 / 1 | 1 (1 / 0 / 0) | 210 | 0.1 % | +770 | +0 | +770 / +998 | 1.3 % | 0.0 % | +1.2 | yes |
| CHP (Combined Heat and Power) | 14 / 12 | 1 (0 / 0 / 1) | 162 | 0.1 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | -0.1 | no |
| Energy Storage System;Gas Reciprocating | 2 / 1 | 1 (1 / 0 / 0) | 135 | 0.0 % | +675 | +675 | +0 / +0 | 1.2 % | 1.3 % | +1.2 | no |
| Waste | 3 / 2 | 2 (1 / 0 / 1) | 123 | 0.0 % | +242 | +242 | +0 / +0 | 0.4 % | 0.5 % | +0.4 | no |
| Demand;Wind Onshore | 1 / 1 | 1 (0 / 0 / 1) | 112 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | no |
| Thermal | 8 / 7 | 2 (0 / 0 / 2) | 105 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | no |
| Gas Reciprocating | 11 / 7 | 2 (0 / 0 / 2) | 57 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | no |
| Coal | 2 / 1 | 1 (0 / 0 / 1) | 50 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | no |
| Demand;PV Array (Photo Voltaic/solar) | 4 / 1 | 1 (0 / 0 / 1) | 20 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | yes |
| CCGT (Combined Cycle Gas Turbine);Demand | 2 / 0 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | yes |
| CCGT (Combined Cycle Gas Turbine);Demand;Energy Storage System | 6 / 0 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | yes |
| CCGT (Combined Cycle Gas Turbine);Reactive Compensation | 1 / 1 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | no |
| CHP (Combined Heat and Power);Energy Storage System | 1 / 0 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | yes |
| Demand;PV Array (Photo Voltaic/solar);Waste | 1 / 0 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | yes |
| Demand;Wind Offshore | 2 / 0 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | yes |
| Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation;Wind Onshore | 1 / 0 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | yes |
| Energy Storage System;PV Array (Photo Voltaic/solar);Wind Offshore | 1 / 0 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | yes |
| Hydro | 30 / 30 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | no |
| Oil & AGT (Advanced Gas Turbine) | 3 / 3 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | no |
| PV Array (Photo Voltaic/solar);Wind Onshore | 1 / 0 | 0 (0 / 0 / 0) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | yes |
| Reactive Compensation | 21 / 13 | 8 (0 / 0 / 8) | 0 | 0.0 % | +0 | +0 | +0 / +0 | 0.0 % | 0.0 % | +0.0 | no |
| key changed | 0 / 99 | 92 (35 / 3 / 54) | 54,434 | 18.6 % | +14,028 | +13,788 | +239 / +1,991 | 24.3 % | 25.9 % | +5.7 | — |

Marks: none.

### The storage reading, two ways

The register prints compound plant types and this cut keeps them whole, so energy storage can be read as the label alone or as every group with the label among its components. Both are reported; neither is the right one.

| Reading | Groups | Dated project-stages | Dated capacity, MW | Share of capacity | Net, MW-years (v2) | Determined | Share of net | Concentration, points |
|---|---|---|---|---|---|---|---|---|
| Storage alone | 1 | 270 | 57,891 | 19.8 % | +16,562 | +15,445 | 28.6 % | +8.8 |
| Storage including compounds | 21 | 571 | 162,331 | 55.4 % | +40,955 | +34,519 | 70.8 % | +15.4 |

Cause, from 006: of the 213 slips of 24 months or more in 005's population, 60 % were project-led, 26 % works-led and 14 % unattributable; nothing here revises that split or attributes any group's movement to a cause.

## Propositions, as declared and as decided

- **P-A** (no single host TO carries more than two thirds of the headline window's net movement while holding less than half of its dated capacity): **holds**. NGET 81.7 % of net (75.0 % of the determined part) against 80.9 % of capacity; SHET 7.6 % of net (14.8 % of the determined part) against 13.1 % of capacity; SPT 10.6 % of net (10.0 % of the determined part) against 5.7 % of capacity, thin; OFTO 0.0 % of net (0.0 % of the determined part) against 0.0 % of capacity. The determined reading agrees.
- **P-B** (in the headline window the net movement is positive in every host TO with at least thirty dated project-stages): **holds**. NGET 601 dated, +47,258 MW-years (+39,933 determined); SHET 171 dated, +4,376 MW-years (+7,903 determined); SPT 112 dated, +6,123 MW-years (+5,319 determined), thin. The determined reading agrees.
- **P-C** (energy storage including compounds carries a share of net movement within fifteen points of its share of dated capacity in the headline window): **fails**. Including compounds (21 groups): 70.8 % of net against 55.4 % of capacity, +15.4 points; share of the determined part 65.0 %. Storage alone: 28.6 % of net against 19.8 % of capacity (+8.8 points); it does not decide P-C.

## Conclusion

Over the headline window, 19 July 2024 to 22 July 2025, under this reading and with the 006 cause split standing unrevised:

- **By area**, net movement is spread close to dated capacity: NGET 80.9 % of dated capacity and 81.7 % of net (+0.8 points); SHET 13.1 % of dated capacity and 7.6 % of net (-5.5 points); SPT 5.7 % of dated capacity and 10.6 % of net (+4.9 points, thin). P-A **holds**; P-B **holds**.
- **By technology**, the largest groups are Energy Storage System;PV Array (Photo Voltaic/solar) 23.9 % of capacity and 36.6 % of net (+12.7 points, thin); Energy Storage System 19.8 % of capacity and 28.6 % of net (+8.8 points); Wind Offshore 16.3 % of capacity and -12.1 % of net (-28.4 points); Wind Onshore 4.2 % of capacity and 9.5 % of net (+5.3 points). Energy storage including compounds (21 register labels) holds 55.4 % of dated capacity and 70.8 % of net under version 2's rule (+15.4 points), and 65.0 % of the determined part (+9.6 points); storage alone 19.8 % of capacity and 28.6 % of net (+8.8 points). P-C **fails** on the rule it is judged on; it would hold on the determined reading, so the margin is one the identity rule decides, not the register.
- **What the by-technology reading rests on**: 18.6 % of the window's dated capacity printed a different plant type at the two ends and is in the key-changed bucket, never reassigned; the technology shares above are shares of the whole, that bucket included.

A share of net above a share of capacity says the register's dates for that group carried less information over this window than the rest's; it does not say why, and 006's split (three fifths project-led, a quarter works-led, the rest unattributable) is the only cause evidence this project holds.

## What the key-changed bucket holds

A project-stage whose plant type or host TO reads differently at the two ends of a window is in the key-changed bucket (R2). The schema pass (`archives/tec-register/schema-report.json`) counts, between every pair of consecutive copies, the project-stages whose printed key changed; for each window whose bucket holds at least 5 % of dated capacity, the copies inside it where that count was largest are listed. The counts are over every project-stage printed in both copies of a pair, not only the dated population, so they bound the bucket rather than equal it.

- 19 July 2024 to 22 July 2025, by plant type: bucket 92 dated project-stages, 18.6 % of dated capacity, +14,028 MW-years; the schema pass counts 150 key changes between consecutive copies inside the window, most at 2025-07-01 (60), 2025-03-21 (21), 2025-07-22 (16).
- 2014 (31 January 2014 to 9 January 2015), by plant type: bucket 2 dated project-stages, 5.6 % of dated capacity, +2,398 MW-years; the schema pass counts 14 key changes between consecutive copies inside the window, most at 2014-12-19 (5), 2014-10-07 (3), 2014-05-09 (2).
- 2019 (3 January 2019 to 2 January 2020), by plant type: bucket 4 dated project-stages, 5.3 % of dated capacity, +3,137 MW-years; the schema pass counts 8 key changes between consecutive copies inside the window, most at 2019-01-24 (2), 2019-04-04 (2), 2019-05-23 (2).
- 2020 (2 January 2020 to 7 January 2021), by plant type: bucket 7 dated project-stages, 5.5 % of dated capacity, -61 MW-years; the schema pass counts 94 key changes between consecutive copies inside the window, most at 2020-06-05 (61), 2020-10-08 (25), 2020-11-26 (4).

## The calendar-year windows of the old regime

Each complete calendar year as 014 lists it (first copy on or after 1 January to the first copy on or after the next). The 2020 window spans the register's relabelling of 2020-06-05 and is where the key-changed bucket is expected to be largest.

### By host transmission owner

Each cell: share of dated capacity / share of net movement (concentration in points).

| Window | Net, MW-years (v2) | Determined | NGET | SPT | SHET | OFTO | (blank) | key changed | Marks |
|---|---|---|---|---|---|---|---|---|---|
| 2014 (31 January 2014 to 9 January 2015) | +20,198 | +19,678 | 81.6 % / 90.4 % (+8.8) thin | 3.8 % / 0.5 % (-3.3) | 14.6 % / 9.1 % (-5.5) | — | — | — | — |
| 2015 (9 January 2015 to 4 January 2016) | +23,194 | +12,348 | 85.1 % / 95.4 % (+10.3) | 8.7 % / 0.7 % (-8.0) | 6.2 % / 3.8 % (-2.4) | — | — | 0.0 % / 0.0 % (+0.0) | — |
| 2016 (4 January 2016 to 5 January 2017) | +23,132 | +19,544 | 83.5 % / 75.2 % (-8.3) | 7.9 % / 14.8 % (+6.9) | 8.6 % / 10.0 % (+1.4) | 0.0 % / 0.0 % (+0.0) | — | 0.0 % / 0.0 % (+0.0) | — |
| 2017 (5 January 2017 to 4 January 2018) | +26,175 | +13,678 | 81.4 % / 83.2 % (+1.8) | 7.1 % / 5.3 % (-1.8) | 10.7 % / -2.5 % (-13.2) | 0.8 % / 13.9 % (+13.1) | — | — | — |
| 2018 (4 January 2018 to 3 January 2019) | +68,399 | +26,714 | 80.6 % / 90.7 % (+10.1) | 8.9 % / 4.9 % (-4.0) | 8.9 % / 4.4 % (-4.5) | 1.6 % / 0.0 % (-1.6) | — | — | — |
| 2019 (3 January 2019 to 2 January 2020) | +11,000 | +5,724 | 84.0 % / 82.8 % (-1.2) | 6.1 % / 3.8 % (-2.3) | 7.4 % / 11.9 % (+4.5) | 2.4 % / 1.5 % (-0.9) | — | 0.0 % / 0.0 % (+0.0) | — |
| 2020 (2 January 2020 to 7 January 2021) | +2,903 | +1,371 | 68.2 % / 66.0 % (-2.2) thin | 14.3 % / 8.3 % (-6.0) thin | 17.6 % / 25.7 % (+8.1) thin | 0.0 % / 0.0 % (+0.0) thin | — | — | — |
| 2021 (7 January 2021 to 5 January 2022) | +12,745 | +7,104 | 68.0 % / 57.9 % (-10.1) | 15.0 % / 43.4 % (+28.4) | 13.0 % / 11.6 % (-1.4) | 4.0 % / -13.0 % (-17.0) | — | — | — |
| 2022 (5 January 2022 to 6 January 2023) | +8,396 | +4,789 | 27.1 % / 62.5 % (+35.4) thin | 24.8 % / 16.2 % (-8.6) thin | 45.8 % / 11.9 % (-33.9) thin | 2.2 % / 9.4 % (+7.2) | — | — | — |
| 2023 (6 January 2023 to 5 January 2024) | +13,584 | +1,770 | 64.5 % / 62.3 % (-2.2) | 15.3 % / 23.2 % (+7.9) | 18.7 % / 14.4 % (-4.3) | 0.0 % / 0.0 % (+0.0) | 0.0 % / 0.0 % (+0.0) thin | 1.5 % / 0.0 % (-1.5) | — |
| 2024 (5 January 2024 to 3 January 2025) | +48,797 | +27,518 | 78.4 % / 80.6 % (+2.2) | 7.7 % / 9.4 % (+1.7) thin | 13.9 % / 9.8 % (-4.1) | 0.0 % / 0.0 % (+0.0) | — | 0.0 % / 0.1 % (+0.1) | — |

Cause, from 006: of the 213 slips of 24 months or more in 005's population, 60 % were project-led, 26 % works-led and 14 % unattributable; nothing here revises that split or attributes any group's movement to a cause.

### By plant type

Groups holding at least 5.0 % of the window's dated capacity are named; the rest are folded with their summed shares. Every group is in `evidence/groups.ndjson`.

| Window | Net, MW-years (v2) | Determined | Key changed (share of capacity) | Groups | Marks |
|---|---|---|---|---|---|
| 2014 (31 January 2014 to 9 January 2015) | +20,198 | +19,678 | 5.6 % | CCGT (Combined Cycle Gas Turbine): 42.1 % of capacity, 73.7 % of net (+31.6); Nuclear: 15.3 % of capacity, 0.0 % of net (-15.3); Wind Onshore: 13.3 % of capacity, 6.2 % of net (-7.1); Wind Offshore: 10.8 % of capacity, 3.6 % of net (-7.2) thin; Pump Storage: 6.6 % of capacity, 0.0 % of net (-6.6); 14 other groups: 6.1 % of capacity, 4.6 % of net | — |
| 2015 (9 January 2015 to 4 January 2016) | +23,194 | +12,348 | 1.4 % | Nuclear: 39.1 % of capacity, 32.4 % of net (-6.7); CCGT (Combined Cycle Gas Turbine): 35.6 % of capacity, 50.1 % of net (+14.5); Wind Offshore: 10.7 % of capacity, 11.3 % of net (+0.6) thin; Wind Onshore: 6.6 % of capacity, 2.9 % of net (-3.7) thin; 9 other groups: 6.7 % of capacity, 3.4 % of net | — |
| 2016 (4 January 2016 to 5 January 2017) | +23,132 | +19,544 | 0.0 % | Nuclear: 30.0 % of capacity, 37.5 % of net (+7.5); Wind Offshore: 28.9 % of capacity, 23.0 % of net (-5.9); CCGT (Combined Cycle Gas Turbine): 24.1 % of capacity, 18.4 % of net (-5.7); Wind Onshore: 10.0 % of capacity, 7.2 % of net (-2.8); 10 other groups: 6.9 % of capacity, 14.0 % of net | — |
| 2017 (5 January 2017 to 4 January 2018) | +26,175 | +13,678 | 0.0 % | Wind Offshore: 37.6 % of capacity, 43.7 % of net (+6.1); Nuclear: 25.1 % of capacity, 32.1 % of net (+7.0); CCGT (Combined Cycle Gas Turbine): 20.4 % of capacity, 19.8 % of net (-0.6); Wind Onshore: 9.0 % of capacity, 4.6 % of net (-4.4); 11 other groups: 7.8 % of capacity, -0.3 % of net | — |
| 2018 (4 January 2018 to 3 January 2019) | +68,399 | +26,714 | 1.7 % | Nuclear: 31.3 % of capacity, 74.6 % of net (+43.3); Wind Offshore: 30.0 % of capacity, 20.7 % of net (-9.3); CCGT (Combined Cycle Gas Turbine): 17.7 % of capacity, 2.4 % of net (-15.3); Wind Onshore: 6.3 % of capacity, 2.3 % of net (-4.0); Wave: 5.7 % of capacity, 0.0 % of net (-5.7); 10 other groups: 7.3 % of capacity, 0.0 % of net | — |
| 2019 (3 January 2019 to 2 January 2020) | +11,000 | +5,724 | 5.3 % | Wind Offshore: 33.5 % of capacity, 2.3 % of net (-31.2); CCGT (Combined Cycle Gas Turbine): 18.9 % of capacity, 33.3 % of net (+14.4); Nuclear: 17.0 % of capacity, 0.0 % of net (-17.0); Wind Onshore: 7.9 % of capacity, 22.8 % of net (+14.9); Wave: 6.4 % of capacity, 0.0 % of net (-6.4); 13 other groups: 10.9 % of capacity, 13.1 % of net | — |
| 2020 (2 January 2020 to 7 January 2021) | +2,903 | +1,371 | 5.5 % | Nuclear: 31.6 % of capacity, 52.6 % of net (+21.0) thin; Wind Onshore: 29.4 % of capacity, 31.9 % of net (+2.5) thin; Wind Offshore: 16.7 % of capacity, 8.8 % of net (-7.9) thin; OCGT (Open Cycle Gas Turbine): 11.3 % of capacity, 0.0 % of net (-11.3) thin; 14 other groups: 5.4 % of capacity, 8.8 % of net | — |
| 2021 (7 January 2021 to 5 January 2022) | +12,745 | +7,104 | 0.5 % | Wind Offshore: 40.8 % of capacity, 53.1 % of net (+12.3); CCGT (Combined Cycle Gas Turbine): 15.8 % of capacity, 14.4 % of net (-1.4); Wind Onshore: 15.0 % of capacity, 14.8 % of net (-0.2); Nuclear: 9.2 % of capacity, 0.0 % of net (-9.2); Energy Storage System;PV Array (Photo Voltaic/solar): 6.3 % of capacity, 0.0 % of net (-6.3); 17 other groups: 12.4 % of capacity, 13.8 % of net | — |
| 2022 (5 January 2022 to 6 January 2023) | +8,396 | +4,789 | 0.3 % | Wind Offshore: 73.6 % of capacity, 50.1 % of net (-23.5) thin; Wind Onshore: 9.4 % of capacity, 19.0 % of net (+9.6) thin; Energy Storage System;PV Array (Photo Voltaic/solar): 6.6 % of capacity, 18.0 % of net (+11.4) thin; 22 other groups: 10.1 % of capacity, 12.4 % of net | — |
| 2023 (6 January 2023 to 5 January 2024) | +13,584 | +1,770 | 0.7 % | Wind Offshore: 42.9 % of capacity, -42.5 % of net (-85.4); Energy Storage System: 16.4 % of capacity, 12.8 % of net (-3.6); Energy Storage System;PV Array (Photo Voltaic/solar): 16.2 % of capacity, 5.4 % of net (-10.8); Wind Onshore: 9.2 % of capacity, 20.8 % of net (+11.6); CCGT (Combined Cycle Gas Turbine): 5.2 % of capacity, 94.1 % of net (+88.9); 30 other groups: 9.3 % of capacity, 9.4 % of net | — |
| 2024 (5 January 2024 to 3 January 2025) | +48,797 | +27,518 | 3.8 % | Energy Storage System;PV Array (Photo Voltaic/solar): 28.2 % of capacity, 20.8 % of net (-7.4); Wind Offshore: 22.5 % of capacity, 32.2 % of net (+9.7); Energy Storage System: 18.9 % of capacity, 5.1 % of net (-13.8); Wind Onshore: 5.1 % of capacity, 9.6 % of net (+4.5); 37 other groups: 21.9 % of capacity, 22.9 % of net | — |

Cause, from 006: of the 213 slips of 24 months or more in 005's population, 60 % were project-led, 26 % works-led and 14 % unattributable; nothing here revises that split or attributes any group's movement to a cause.

### The storage reading, two ways, per window

| Window | Storage alone: share of capacity / share of net (points) | Including compounds: share of capacity / share of net (points) | Marks |
|---|---|---|---|
| 2014 (31 January 2014 to 9 January 2015) | — / — (—) | — / — (—) | — |
| 2015 (9 January 2015 to 4 January 2016) | — / — (—) | — / — (—) | — |
| 2016 (4 January 2016 to 5 January 2017) | — / — (—) | — / — (—) | — |
| 2017 (5 January 2017 to 4 January 2018) | 0.0 % / 0.0 % (+0.0) | 0.0 % / 0.0 % (+0.0) | — |
| 2018 (4 January 2018 to 3 January 2019) | 0.0 % / 0.0 % (+0.0) | 0.0 % / 0.0 % (+0.0) | — |
| 2019 (3 January 2019 to 2 January 2020) | 0.0 % / 0.0 % (+0.0) | 0.0 % / 0.0 % (+0.0) | — |
| 2020 (2 January 2020 to 7 January 2021) | 0.0 % / 0.0 % (+0.0) | 0.0 % / 0.0 % (+0.0) | — |
| 2021 (7 January 2021 to 5 January 2022) | 4.2 % / 3.2 % (-1.0) | 12.0 % / 7.8 % (-4.2) | — |
| 2022 (5 January 2022 to 6 January 2023) | 4.3 % / 0.2 % (-4.1) | 11.9 % / 18.2 % (+6.3) | — |
| 2023 (6 January 2023 to 5 January 2024) | 16.4 % / 12.8 % (-3.6) | 34.7 % / 21.0 % (-13.7) | — |
| 2024 (5 January 2024 to 3 January 2025) | 18.9 % / 5.1 % (-13.8) | 60.6 % / 21.7 % (-38.9) | — |

Thin groups under R7 (matched fewer than half of the group's baseline units; figures published, not suppressed): 2014 (31 January 2014 to 9 January 2015), by plant type: Wind Offshore, Tidal, IGCC with CCS, Large Unit Coal, Nuclear APR, Nuclear EPR, OCGT (Open Cycle Gas Turbine), Oil & AGT (Advanced Gas Turbine), Small Unit Coal, Wave; 2014 (31 January 2014 to 9 January 2015), by host transmission owner: NGET; 2015 (9 January 2015 to 4 January 2016), by plant type: Wind Offshore, Wind Onshore, Tidal, Wave, Thermal, (blank); 2016 (4 January 2016 to 5 January 2017), by plant type: Wave; 2017 (5 January 2017 to 4 January 2018), by plant type: PV Array (Photo Voltaic/solar), Hydro, Oil & AGT (Advanced Gas Turbine); 2018 (4 January 2018 to 3 January 2019), by plant type: Thermal, PV Array (Photo Voltaic/solar); 2019 (3 January 2019 to 2 January 2020), by plant type: Coal, Tidal, Battery Storage, Oil & AGT (Advanced Gas Turbine); 2020 (2 January 2020 to 7 January 2021), by plant type: Nuclear, Wind Onshore, Wind Offshore, OCGT (Open Cycle Gas Turbine), Pump Storage, CCGT (Combined Cycle Gas Turbine), PV Array (Photo Voltaic/solar), Battery Storage, Biomass, CHP (Combined Heat and Power), Coal, Gas Reciprocating, Hybrid, Hydro, Oil & AGT (Advanced Gas Turbine), Thermal, Tidal, Wave; 2020 (2 January 2020 to 7 January 2021), by host transmission owner: NGET, SHET, SPT, OFTO; 2021 (7 January 2021 to 5 January 2022), by plant type: Energy Storage System;Reactive Compensation, CCGT (Combined Cycle Gas Turbine);OCGT (Open Cycle Gas Turbine), Energy Storage System;Gas Reciprocating, Oil & AGT (Advanced Gas Turbine), PV Array (Photo Voltaic/solar);Waste; 2022 (5 January 2022 to 6 January 2023), by plant type: Wind Offshore, Wind Onshore, Energy Storage System;PV Array (Photo Voltaic/solar), Energy Storage System, PV Array (Photo Voltaic/solar), Pump Storage, OCGT (Open Cycle Gas Turbine), Gas Reciprocating, Biomass, CCGT (Combined Cycle Gas Turbine), CCGT (Combined Cycle Gas Turbine);Energy Storage System;OCGT (Open Cycle Gas Turbine), CHP (Combined Heat and Power), Coal, Energy Storage System;Gas Reciprocating, Energy Storage System;Reactive Compensation, Energy Storage System;Wind Offshore, Energy Storage System;Wind Onshore, Hydro, Nuclear, Oil & AGT (Advanced Gas Turbine), Reactive Compensation, Thermal, (blank); 2022 (5 January 2022 to 6 January 2023), by host transmission owner: SHET, NGET, SPT; 2023 (6 January 2023 to 5 January 2024), by plant type: PV Array (Photo Voltaic/solar), Gas Reciprocating, CCGT (Combined Cycle Gas Turbine);Energy Storage System;OCGT (Open Cycle Gas Turbine), Coal, Demand;Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation, Demand;Wind Offshore, Energy Storage System;PV Array (Photo Voltaic/solar);Wind Offshore, Hybrid, (blank); 2023 (6 January 2023 to 5 January 2024), by host transmission owner: (blank); 2024 (5 January 2024 to 3 January 2025), by plant type: Demand;PV Array (Photo Voltaic/solar), Coal, Demand;Energy Storage System;PV Array (Photo Voltaic/solar), Demand;Energy Storage System;Wind Offshore, Demand;Wind Offshore; 2024 (5 January 2024 to 3 January 2025), by host transmission owner: SPT.

## The reformed regime, copy to copy

The copies from 2026-05-19 carry re-baselined dates and are compared copy to copy, never with the old regime.

### By host transmission owner

Each cell: share of dated capacity / share of net movement (concentration in points).

| Window | Net, MW-years (v2) | Determined | NGET | SPT | SHET | OFTO | (blank) | key changed | Marks |
|---|---|---|---|---|---|---|---|---|---|
| 19 May 2026 to 22 August 2026 | +18,880 | +17,147 | 75.8 % / 78.9 % (+3.1) | 11.0 % / 17.0 % (+6.0) | 13.1 % / 4.1 % (-9.0) | 0.0 % / 0.0 % (+0.0) | — | 0.1 % / 0.0 % (-0.1) | — |
| 22 August 2026 to 25 August 2026 | -3 | +0 | 74.6 % / 100.0 % (+25.4) | 11.9 % / -0.0 % (-11.9) | 13.5 % / -0.0 % (-13.5) | 0.0 % / -0.0 % (-0.0) | — | — | **shares not read** (R9: net within ±1,000 MW-years) |
| 25 August 2026 to 15 September 2026 | +6,250 | +5,776 | 74.3 % / 73.2 % (-1.1) | 12.0 % / 4.1 % (-7.9) | 13.7 % / 22.8 % (+9.1) | 0.0 % / 0.0 % (+0.0) | — | 0.0 % / 0.0 % (+0.0) | — |

Cause, from 006: of the 213 slips of 24 months or more in 005's population, 60 % were project-led, 26 % works-led and 14 % unattributable; nothing here revises that split or attributes any group's movement to a cause.

### By plant type

Groups holding at least 5.0 % of the window's dated capacity are named; the rest are folded with their summed shares. Every group is in `evidence/groups.ndjson`.

| Window | Net, MW-years (v2) | Determined | Key changed (share of capacity) | Groups | Marks |
|---|---|---|---|---|---|
| 19 May 2026 to 22 August 2026 | +18,880 | +17,147 | 1.2 % | Energy Storage System: 28.1 % of capacity, 29.6 % of net (+1.5); Energy Storage System;PV Array (Photo Voltaic/solar): 22.4 % of capacity, 1.5 % of net (-20.9); Wind Offshore: 14.1 % of capacity, 8.9 % of net (-5.2); CCGT (Combined Cycle Gas Turbine): 5.1 % of capacity, 0.0 % of net (-5.1); 56 other groups: 29.1 % of capacity, 55.7 % of net | — |
| 22 August 2026 to 25 August 2026 | -3 | +0 | 0.0 % | Energy Storage System: 29.3 % of capacity, -0.0 % of net (-29.3); Energy Storage System;PV Array (Photo Voltaic/solar): 23.2 % of capacity, -0.0 % of net (-23.2); Wind Offshore: 14.4 % of capacity, -0.0 % of net (-14.4); 57 other groups: 32.9 % of capacity, 100.0 % of net | **shares not read** (R9: net within ±1,000 MW-years) |
| 25 August 2026 to 15 September 2026 | +6,250 | +5,776 | 0.0 % | Energy Storage System: 29.6 % of capacity, 10.1 % of net (-19.5); Energy Storage System;PV Array (Photo Voltaic/solar): 23.2 % of capacity, 0.4 % of net (-22.8); Wind Offshore: 14.4 % of capacity, 65.6 % of net (+51.2); 57 other groups: 32.8 % of capacity, 23.9 % of net | — |

Cause, from 006: of the 213 slips of 24 months or more in 005's population, 60 % were project-led, 26 % works-led and 14 % unattributable; nothing here revises that split or attributes any group's movement to a cause.

### The storage reading, two ways, per window

| Window | Storage alone: share of capacity / share of net (points) | Including compounds: share of capacity / share of net (points) | Marks |
|---|---|---|---|
| 19 May 2026 to 22 August 2026 | 28.1 % / 29.6 % (+1.5) | 68.5 % / 80.8 % (+12.3) | — |
| 22 August 2026 to 25 August 2026 | 29.3 % / 0.0 % (-29.3) | 69.6 % / 100.0 % (+30.4) | **shares not read** (R9: net within ±1,000 MW-years) |
| 25 August 2026 to 15 September 2026 | 29.6 % / 10.1 % (-19.5) | 70.2 % / 10.5 % (-59.7) | — |

Thin groups under R7 (matched fewer than half of the group's baseline units; figures published, not suppressed): 19 May 2026 to 22 August 2026, by plant type: Demand;Energy Storage System;PV Array (Photo Voltaic/solar);Reactive Compensation, CHP (Combined Heat and Power);Energy Storage System;PV Array (Photo Voltaic/solar);Wind Onshore; 25 August 2026 to 15 September 2026, by plant type: Interconnector.

## What this never claims

Everything 014 never claims, and: that a technology or an area is worse at anything; that a compound label says which technology moved; that any project will connect, or when. A group's concentration reading is a property of the register's dates over one window under one reading, with the 006 cause split standing unrevised beside it.

## Expert corner

- Declaration `DECLARATION.md` SHA-256 `76ad7dc36ffda6373f798bb3dad08aa4ea8083262037c48a69ecadeb5f6a91d1`; proofs: opentimestamps pending calendar attestation until upgraded, rfc3161 https://freetsa.org/tsr, rfc3161 http://timestamp.digicert.com.
- Schema pass `archives/tec-register/schema-report.json` SHA-256 `9ed878f499db8a8c2e248b7c11ea37e75ee1142af140fa3f5b01f36d638f8b37`; 014 version 4 manifest SHA-256 `4b53edabbf721076a532e6cf8cee6ea3917832c6d38b51431e250a54ed7495b8` (700 usable copies, 2014-01-31 to 2026-09-15, C1 passed); content rule SHA-256 `a0ee2ac0dcc6919e37061f89a5b0fc1c663cf566cb1a7df3a55f75c761aa0fb8` (C5 passed).
- C2: every one of the 15 comparisons recomputed to 014 version 4's committed net, determined part, undetermined group count, dated count and weighted capacity exactly. C3 and C4 passed on every group (the determined part is rule-independent; counts and capacities sum exactly; nets within rounding).
- Rule version `76ad7dc3`; rows appended: 30 comparison lines and 542 group lines; unfit comparisons (F-G4): none; shares not read (R9): 76ad7dc3|new|copy-to-copy|2026-08-22|2026-08-25|plant_type, 76ad7dc3|new|copy-to-copy|2026-08-22|2026-08-25|host_to.
- Shares are over every bucket of a comparison, key changed and (blank) included, so they sum to 100 % up to rounding; a group's concentration is its share of net minus its share of dated capacity, both under version 2's rule. Counts and capacities are under version 2's rule; movement figures are given under both rules.

## Reproducibility

```
uv run --group registers python investigations/021-slippage-by-technology-and-area/run.py --seal 76ad7dc3 --phase check
uv run python investigations/021-slippage-by-technology-and-area/run.py --phase render
scripts/check
```
