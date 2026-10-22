# 025, the exit clock: when projects leave the TEC Register, measured against the User Commitment trigger date

*Computed 2026-10-22 under the frozen declaration `bc052984…` (`DECLARATION.md`, proofs beside it) from every TEC Register copy the repository holds to 2026-10-20 (791 kept copies) and the documents pinned 22/10/2026 (`evidence/sources-manifest.json`). **Held for the sponsor; nothing here is public, and nothing goes to Ofgem or the introducer until sealed.** Every figure is reproducible by `run.py --phase compute --seal bc052984`; the per-chain appendix is `FINDINGS-APPENDIX.md` (held, names projects).*

## The mystery

Ofgem's CMP470 consultation (17/09/2026) would charge battery projects to stay in the connection queue, on the reading that a project faces little incentive to reassess its viability until its User Commitment trigger date, the 1 April three financial years before its connection date, after which the Wider Cancellation Charge applies. The question put to the register's history: **when do projects actually leave, relative to that date, and does the rate of leaving change as the date approaches and passes?**

## The answer, narrowly

1. **Exits are few.** Of 2,644 project chains the register has printed since January 2014, 494 left it (status not Built, absent for at least 95 days before 2026-10-20); 96 of those were storage projects leaving before the connections-reform break of December 2025 (71 storage-only). **Kill condition (b) fired**: fewer than 200 storage exits in the old regime, so the series is reported as thin and no storage hazard below is called a pattern.
2. **No bunching before the trigger date, on any clock.** For storage, the exit rate in the twelve months before the trigger (2.17 exits per 100 chain-years, interval 0.79 to 4.73) is indistinguishable from the rate more than two years before it (1.61, 1.13 to 2.21). The same holds under clock B (trigger from the connection date first printed: 2.87 against 2.22) and clock C (the date as printed in each copy: 2.01 against 2.12).
3. **The rate rises after the trigger, under clock A only.** More than twelve months after the trigger implied by the last-printed connection date, storage left at 12.20 per 100 chain-years (8.40 to 17.13), seven times the far-before rate; the bands are not flat within their uncertainty (K6: False). Under clocks B and C the bands **are** flat (True, True). Interpretation, offered not asserted: clock A reads the trigger from the date a project last printed, so a project that leaves with a stale, passed or imminent connection date sits far "after" its trigger by construction; the rise says projects leave late in their own printed programme (017's overdue residue), not that they leave because the bill arrived.
4. **All technologies together show the same shape, with more exits.** 485 old-regime exits: 4.43 per 100 chain-years far before the trigger, 11.77 in the year before, 13.22 in the year after, 26.28 beyond. Here the rate does step up from the far-before band to the two years before the trigger (11.39), which storage alone does not show; the controls are mostly wind and gas chains from 2014 to 2021.
5. **Against Ofgem's 72.** Ofgem counted 72 storage projects that "exited the connection queue or changed their technology classification" between 2023 and 2025 (6.7 % a year). This series counts 65 storage exits with exit copies from January 2023 to November 2025 (8, 25, 32 by year), and on Ofgem's own annual-snapshot footing 16 storage chains reclassified away from storage between snapshots. The counts meet within a factor of two (F1 silent); the **rates** do not: 0.0 %, 1.4 % and 2.2 % of storage chains present at each January snapshot had left by the next, against 6.7 %; Scoping 1.6 % and 2.6 % against Ofgem's 7.4 % for Scoping or Awaiting Consents; Consents Approved 0.0 % against 3 %; Under Construction 0.0 % against 0 %. The direction agrees (earlier stages leave more; nothing leaves from construction); the level does not, and the candidates are in the reconciliation section.

What this does **not** say: why any project left; what any project had posted or accrued; that a trigger date caused anything. The register records absence.

## Provisional to sealed

The first compute of 22/10/2026 was discarded before any line was committed: it produced 13 chains holding two keys in one copy, a runner defect against rule I2: a key returned to the register while its chain was already continuing under a stitched key, and the runner let the chain carry both (discarded `chains.ndjson` SHA-256 `a41057c3798a33e2…`, the note in `evidence/run-log.json`). The rerun under the same sealed declaration moved the headline by: chains 2,631 to 2,644; exits 493 to 494; storage exits in the old regime 95 to 96. The 13 are reported below as a stitching finding.

## The evidence

- **Copies**: 793 usable, 791 kept (014's partial-export rule excluded 2: 2015-05-08, 2023-11-28), 2014-01-31 to 2026-10-20; every copy verified against its journalled or manifested digest (C1); the series end fixed at 2026-10-20 and copies published after it unread.
- **Chains**: 2,644. Classes (C3): 2,083 present at the series end, 494 left, 57 completed (last printed as Built), 4 open (last seen after 2026-07-17), 6 not determinable (all before the Project ID era, at the June 2020 re-keying). **Kill (a) did not fire**: the ID-era not-determinable share is 0.0 %.
- **Stitching**: 2,933 key changes carried a chain across a change of key, by tier: all five 1,449, name, customer, stage 701, name, site, stage 608, customer, site, stage, cumulative 108, name alone 45, name, stage, cumulative 21, name, customer, site 1. 426 keys returned to their chain after an interruption (I9); 200 chains were interrupted at least once; 1,184 stage reductions (rows lost while the chain stayed); 367 chains changed plant family at some point (I7), none of them counted as an exit for that reason.
- **Exposure**: 132,065 chain-months at risk over the series.

### Monthly exit series (old regime, exit copies January 2014 to November 2025)

| year | all exits | storage exits |
|---|---|---|
| 2014 | 94 | 0 |
| 2015 | 44 | 0 |
| 2016 | 39 | 0 |
| 2017 | 12 | 0 |
| 2018 | 30 | 3 |
| 2019 | 21 | 3 |
| 2020 | 52 | 10 |
| 2021 | 34 | 13 |
| 2022 | 18 | 2 |
| 2023 | 39 | 8 |
| 2024 | 54 | 25 |
| 2025 | 48 | 32 |

The monthly series itself (counts and MW, all and storage) is the `monthly` block of `evidence/results.json`, drawn in `figures/monthly-exits.png` (held). 2014's 94 exits fall in a year of sparse, differently formatted copies (gaps up to 95 days, single-copy column eras) and should be read as the register settling, not as a wave. Storage exits in the old regime cluster in 2025-07 (16), 2024-09 (7), 2020-02 (5).

### Hazard by band (storage, old regime)

**Clock A: trigger from the connection date printed at last sighting**

| band (clock A, trigger from the connection date at last sighting) | exits | chain-months at risk | exits per 100 chain-years | 95 % interval |
|---|---|---|---|---|
| more than 24 months before | 37 | 27,644 | 1.61 | 1.13 to 2.21 |
| 12 to 24 months before | 8 | 4,009 | 2.40 | 1.03 to 4.72 |
| 0 to 12 months before | 6 | 3,316 | 2.17 | 0.79 to 4.73 |
| 0 to 12 months after | 11 | 2,719 | 4.86 | 2.42 to 8.69 |
| more than 12 months after | 33 | 3,246 | 12.20 | 8.40 to 17.13 |
| no connection date | 1 | 4,043 | 0.30 | 0.00 to 1.65 |

**Clock B: trigger from the connection date printed at first sighting**

| band (clock A, trigger from the connection date at last sighting) | exits | chain-months at risk | exits per 100 chain-years | 95 % interval |
|---|---|---|---|---|
| more than 24 months before | 37 | 20,042 | 2.22 | 1.56 to 3.05 |
| 12 to 24 months before | 7 | 2,839 | 2.96 | 1.19 to 6.10 |
| 0 to 12 months before | 7 | 2,927 | 2.87 | 1.15 to 5.91 |
| 0 to 12 months after | 10 | 3,052 | 3.93 | 1.88 to 7.23 |
| more than 12 months after | 34 | 14,127 | 2.89 | 2.00 to 4.04 |
| no connection date | 1 | 1,990 | 0.60 | 0.01 to 3.36 |

**Clock C: exposure placed by the date printed in each copy; exits by clock A**

| band (clock A, trigger from the connection date at last sighting) | exits | chain-months at risk | exits per 100 chain-years | 95 % interval |
|---|---|---|---|---|
| more than 24 months before | 37 | 20,942 | 2.12 | 1.49 to 2.92 |
| 12 to 24 months before | 8 | 3,225 | 2.98 | 1.28 to 5.87 |
| 0 to 12 months before | 6 | 3,578 | 2.01 | 0.73 to 4.38 |
| 0 to 12 months after | 11 | 3,730 | 3.54 | 1.76 to 6.33 |
| more than 12 months after | 33 | 10,462 | 3.78 | 2.61 to 5.32 |
| no connection date | 1 | 3,040 | 0.39 | 0.00 to 2.20 |

**Clock A, storage-only (plant type prints storage and nothing else)**

| band (clock A, trigger from the connection date at last sighting) | exits | chain-months at risk | exits per 100 chain-years | 95 % interval |
|---|---|---|---|---|
| more than 24 months before | 24 | 11,300 | 2.55 | 1.63 to 3.79 |
| 12 to 24 months before | 5 | 2,071 | 2.90 | 0.93 to 6.76 |
| 0 to 12 months before | 5 | 1,839 | 3.26 | 1.05 to 7.61 |
| 0 to 12 months after | 10 | 1,606 | 7.47 | 3.58 to 13.74 |
| more than 12 months after | 26 | 2,092 | 14.91 | 9.74 to 21.85 |
| no connection date | 1 | 3,063 | 0.39 | 0.00 to 2.18 |

**Clock A, every chain**

| band (clock A, trigger from the connection date at last sighting) | exits | chain-months at risk | exits per 100 chain-years | 95 % interval |
|---|---|---|---|---|
| more than 24 months before | 170 | 46,071 | 4.43 | 3.79 to 5.15 |
| 12 to 24 months before | 68 | 7,163 | 11.39 | 8.85 to 14.44 |
| 0 to 12 months before | 56 | 5,708 | 11.77 | 8.89 to 15.29 |
| 0 to 12 months after | 50 | 4,540 | 13.22 | 9.81 to 17.42 |
| more than 12 months after | 134 | 6,118 | 26.28 | 22.02 to 31.13 |
| no connection date | 7 | 39,581 | 0.21 | 0.09 to 0.44 |

**Clock A, chains that print no storage technology (the control)**

| band (clock A, trigger from the connection date at last sighting) | exits | chain-months at risk | exits per 100 chain-years | 95 % interval |
|---|---|---|---|---|
| more than 24 months before | 133 | 18,427 | 8.66 | 7.25 to 10.26 |
| 12 to 24 months before | 60 | 3,154 | 22.83 | 17.42 to 29.38 |
| 0 to 12 months before | 50 | 2,392 | 25.08 | 18.62 to 33.07 |
| 0 to 12 months after | 39 | 1,821 | 25.70 | 18.27 to 35.13 |
| more than 12 months after | 101 | 2,872 | 42.20 | 34.37 to 51.28 |
| no connection date | 6 | 35,538 | 0.20 | 0.07 to 0.44 |

Flatness (K6, the five bands' intervals share a value): storage A False, B True, C True; storage-only A False; all A False; other A False.

### The clock, exit by exit

Months from exit copy to trigger (clock A; negative means the exit came before the trigger), storage, old regime: 10 exits more than 24 months before, 23 at 12 to 24 before, 11 in the year before, 6 in the year after, 45 more than a year after; 1 with no connection date. Drawn with the bands shaded in `figures/exit-clock.png` (held).

### Strata (storage, old regime, clock A)

| stratum at last sighting | exits | chain-months | exits per 100 chain-years |
|---|---|---|---|
| Project Status: Awaiting Consents | 14 | 4,666 | 3.60 |
| Project Status: Built | 0 | 6,051 | 0.00 |
| Project Status: Consents Approved | 2 | 6,087 | 0.39 |
| Project Status: Scoping | 76 | 26,923 | 3.39 |
| Project Status: Terminated | 2 | 60 | 40.00 |
| Project Status: Under Construction/Commissioning | 2 | 1,190 | 2.02 |
| Agreement Type: blank | 13 | 143 | 109.09 |
| Agreement Type: directly connected | 76 | 38,570 | 2.36 |
| Agreement Type: embedded | 7 | 6,264 | 1.34 |
| Host TO: NGET | 70 | 32,002 | 2.62 |
| Host TO: SHET | 15 | 5,177 | 3.48 |
| Host TO: SPT | 11 | 7,798 | 1.69 |
| First-observation cohort: 2014 | 0 | 134 | 0.00 |
| First-observation cohort: 2014 opening | 0 | 2,431 | 0.00 |
| First-observation cohort: 2015 | 0 | 254 | 0.00 |
| First-observation cohort: 2016 | 2 | 197 | 12.18 |
| First-observation cohort: 2017 | 0 | 204 | 0.00 |
| First-observation cohort: 2018 | 14 | 3,497 | 4.80 |
| First-observation cohort: 2019 | 3 | 1,250 | 2.88 |
| First-observation cohort: 2020 | 12 | 4,974 | 2.90 |
| First-observation cohort: 2021 | 8 | 4,581 | 2.10 |
| First-observation cohort: 2022 | 6 | 5,954 | 1.21 |
| First-observation cohort: 2023 | 24 | 13,595 | 2.12 |
| First-observation cohort: 2024 | 21 | 6,499 | 3.88 |
| First-observation cohort: 2025 | 6 | 1,407 | 5.12 |

The stage split Ofgem can set beside its 7.4 / 3 / 0: storage chains at Scoping or Awaiting Consents left at 3.42 per 100 chain-years over the whole old regime, Consents Approved at 0.39, Under Construction at 2.02 (a rate per 100 chain-years is comparable to a percentage per year).

### Regimes

- Reformed regime (exit copies from 2025-12-01): 9 exits, by Project Status {'Scoping': 9}, by Gate at last sighting {'1': 1, '(blank)': 8}. Too few for any table; the candidate in CANDIDATES.md waits for the series to lengthen.
- The register's row count through the Gate 2 reset: 2,242 on 2025-10-03, 2,233 on 2025-11-25, 2,229 on 2026-02-27. **The queue reset is not visible as a mass departure from the TEC Register.**

## Explanations tested

### Reconciliation to Ofgem (O1, O2)

Annual snapshots as Ofgem had them (the first kept copy on or after 1 January, and the last old-regime copy), storage chains present, the share that had left by the next snapshot, and the share reclassified away from storage:

| snapshot | next | status | present | left | left share | reclassified away |
|---|---|---|---|---|---|---|
| 2023-01-06 | 2024-01-05 | Awaiting Consents | 54 | 0 | 0.0 % | 0 |
| 2023-01-06 | 2024-01-05 | Built | 18 | 0 | 0.0 % | 0 |
| 2023-01-06 | 2024-01-05 | Consents Approved | 25 | 0 | 0.0 % | 0 |
| 2023-01-06 | 2024-01-05 | Scoping | 222 | 0 | 0.0 % | 0 |
| 2023-01-06 | 2024-01-05 | Under Construction/Commissioning | 4 | 0 | 0.0 % | 0 |
| 2023-01-06 | 2024-01-05 | all | 323 | 0 | 0.0 % | 0 |
| 2024-01-05 | 2025-01-03 | Awaiting Consents | 102 | 1 | 1.0 % | 1 |
| 2024-01-05 | 2025-01-03 | Built | 31 | 0 | 0.0 % | 0 |
| 2024-01-05 | 2025-01-03 | Consents Approved | 46 | 0 | 0.0 % | 0 |
| 2024-01-05 | 2025-01-03 | Scoping | 613 | 10 | 1.6 % | 1 |
| 2024-01-05 | 2025-01-03 | Under Construction/Commissioning | 12 | 0 | 0.0 % | 0 |
| 2024-01-05 | 2025-01-03 | all | 804 | 11 | 1.4 % | 2 |
| 2025-01-03 | 2025-11-28 | Awaiting Consents | 104 | 1 | 1.0 % | 1 |
| 2025-01-03 | 2025-11-28 | Built | 45 | 0 | 0.0 % | 2 |
| 2025-01-03 | 2025-11-28 | Consents Approved | 70 | 0 | 0.0 % | 0 |
| 2025-01-03 | 2025-11-28 | Scoping | 948 | 25 | 2.6 % | 11 |
| 2025-01-03 | 2025-11-28 | Under Construction/Commissioning | 10 | 0 | 0.0 % | 0 |
| 2025-01-03 | 2025-11-28 | all | 1177 | 26 | 2.2 % | 14 |

Window count (O2): 65 storage exits with exit copies 2023-01 to 2025-11 (42 storage-only), by status at last sighting {'Consents Approved': 1, 'Scoping': 60, 'Awaiting Consents': 4}. Ofgem: 72 exited or reclassified, 6.7 % a year.

Candidates for the gap in rates, none asserted: (i) **denominator**: Ofgem's queue is NESO's full connections queue, which includes distribution-connected projects below the TEC Register's threshold and projects not yet on the register; a smaller, earlier-stage population would both raise the rate and hold more of the exits; (ii) **classification**: Ofgem's figure lumps exits with reclassification, and the register's reclassifications under one key are counted here as reclassifications (16 away from storage across the snapshots) and never as exits; (iii) **snapshot dates**: Ofgem's are not published; (iv) **re-keying**: a snapshot pair that spans a re-keying copy sees every project leave unless it is stitched, and the August 2022 re-issue lies just before Ofgem's first window.

### The stitching caveat (the question Ofgem will ask)

Identity is the whole method. 1,449 of the 2,933 key changes were at the three re-keying copies and matched on every feature; the next two tiers (701 on name, customer and stage; 608 on name, site and stage) are mostly re-spelt sites and customers at the June 2020 format change and at the re-issues. In the Project ID era, outside the re-keying copies, only **28** stitches were made (name, site, stage 15, name alone 8, customer, site, stage, cumulative 2, all five 2, name, stage, cumulative 1); that is the most by which stitching can have hidden an ID-era exit. The stitch's one caught failure: **13 keys returned to the register while their chain was already printed under another key** (at 2023-02-14 (3), 2023-06-16 (1), 2023-12-05 (6), 2024-03-26 (3)), all in the ID era and none at a re-keying boundary. Each was a project sharing its **name** with a different project (different customer, mostly a different site and MW): the name-based tiers had merged two projects, the returning id separated them, and the runner now keeps the id's chain and treats the row as new. These are the copies 017's certificates show as "presence ambiguous (2 rows)". Nothing says how many unreturned merges remain; the bound above (28 ID-era stitches outside re-keyings) is the honest ceiling.

### The joins (addendum J1 to J3), run on the storage exits

- **J1 REPD** (battery rows, July 2026 extract): matched 21 of 101 storage exits (20.8 %; ID era 17.8 %), 7 ambiguous, by tier {'b: place token and capacity': 15, 'a: operator and place token': 2, "c: operator's only battery row": 4}. **Below the 70 % threshold: the matched subset is reported and the join stops.** Classes among the matched: no planning event before exit 8, application pending at exit 6, refused, withdrawn or expired before exit 5, abandoned (undated) 2. One sentence per class: no matched storage exit was consented at exit; 5 left after a refusal, withdrawal or expiry; 2 are abandoned in the planning record; 6 left with an application pending; 8 left with a planning record that holds no event before the exit. Coordinates were not used (the register prints none).
- **J2 Capacity Market Register** (storage CMUs, 21/10/2026): matched 16 (15.8 %; ID era 16.4 %), 33 ambiguous (one customer with several CMUs at one site), by tier {'a: company and place token': 6, 'c: place token and capacity': 6, 'b: company and capacity': 4}. **Below 70 %: matched subset only.** Classes: never held 14, agreement awarded after exit 1, agreement held at exit 1. No matched exit had a terminated capacity agreement, so the termination-against-exit timing table is empty: {}.
- **J3 Companies House** (019's links, profiles and charges refreshed 2026-10-22, 71 companies): 24.3 % of all exits linked (49.5 % of storage exits, 54.8 % in the ID era; 019 resolved names on current ids, so pre-2021 customers are mostly unlinked). Of the linked, 37.5 % had a live charge at exit; company status now {'active': 119, 'dissolved': 1}; classes {'not linked': 374, 'live charge at exit': 45, 'neither': 74, 'dissolved, more than twelve months from exit': 1}. One sentence: the companies behind linked exits are almost all still active, and more than a third carried a live charge when their project left the register, which is the case Ofgem should worry about and the one this register cannot explain.

Why the joins are thin: the register prints a substation and a developer's project name; REPD prints a planning site and the applicant; the Capacity Market prints a unit name and the applicant. A place token shared by both is rare when the register's name is a substation and REPD's is a road. The declared next step, if the sponsor wants the joins to carry weight, is an amendment that sends the unmatched residue to a model as **proposer** (016's admission rule), with the proposals pinned and admitted by a declared rule; the declared tiers stay the record.

## Conclusion

From the register's own history, storage projects did not leave in a bunch before their User Commitment trigger date in 2014 to 2025; under every clock the year before the trigger looks like the years before that. What rises is the exit rate **after** the trigger implied by a project's last-printed connection date, and that rise disappears when the clock is set by the date first printed or by the date as it stood each month: it is the signature of projects leaving late in their own programme. With 96 storage exits the intervals are wide and the series is thin by its own kill rule; this is a described measurement, not a verdict on CMP470. The premise that "projects leave when the bill arrives" is neither confirmed nor refuted by bunching; it is simply not what the register shows happening before the date.

## Expert corner

- **Re-keying dates**: 2020-05-28 to 2020-06-05, 2021-11-23 to 2021-11-26, 2022-08-19 to 2022-08-24 (more than half of keys absent); Project ID printed from 2021-11-26 (`a03…` ids), re-issued 2022-08-24 (`a0l…`); Project Number from 2024-06-18. 2024-01-05 is **not** a re-keying (0 of 1,452 ids absent), contrary to the prompt's expectation; the id change the 017 Eggborough certificate shows there is one project's.
- **The trigger rule**: CUSC Section 15 v1.14 Part Two 2.2(a), read on `MW Effective From` as the Charging Date; branch (b) (the Construction Agreement date when closer) and any contractual variation are not applied. Ofgem's own footnote uses the same rule of thumb. A project whose connection date was re-set had a different trigger before the re-set; clocks B and C carry that.
- **CMP223 embedded percentages** (2024-25 statement, section 5): secured amount after the trigger 42 % of the cancellation charge before key consents and 10 % after for directly connected; 45 % and 26 % for embedded; 100 % before the trigger. Zonal tariffs 2024-25 by zone code A1 to T6 (GBP 0 to 15,677.41 per MW). No 2025-26 or 2026-27 statement exists; the 15/01/2026 letter froze securities to 30/09/2026.
- **Regime break**: copies from 2025-12-01; row count 2,242 to 2,229 across it.
- **Gap between last sighting and exit copy**: median 7 days, maximum 95; the register's resolution, not the project's timing.
- **Not computed**: the zone mapping (no public site-to-zone list; phase 2 stopped); the DNO register join (J4, candidate); the EIR validation (`EIR-REQUEST-NESO-TERMINATIONS.md`, drafted for the sponsor, not sent).
- **Watch**: `w-025-monthly-exit-series`, due 30/11/2026 and monthly, extends the series from the daily capture under this declaration.

## Reproducibility

`DECLARATION.md` `bc05298419069041ae21b75d0fc556f5ecb48224eb947806325f704f4eb4cd78`; schema report `fa3cbb802f61d3b6…`; sources manifest `55f47fb98d19e50b…`; `evidence/results.json`, `evidence/joins-results.json`, `evidence/format-check.json`, `evidence/run-log.json` (committed); `evidence/chains.ndjson` (append-only, C5), `evidence/exits.ndjson`, `evidence/joins.ndjson`, `evidence/reused-keys.json`, `FINDINGS-APPENDIX.md` (held). Rules: `src/grid_mysteries/investigations/exit_clock.py`, tests `tests/test_exit_clock.py`, map `evidence/rule-sources.json`.
