# 017 — The queue that is past its own date

*Census over the copy of 2026-09-15. Declaration `DECLARATION.md`, SHA-256 `400b42f72b8c77759f88702d113594cdb2bb1b397f903486aaf39e92c7bc4b6d`, frozen and witnessed before any figure here was computed. Run 2026-09-17.*

## The mystery

In the copy of NESO's TEC Register published on 2026-09-15, **98 entries carrying 12,034.86 MW** have an effective date earlier than that publication date and a project status other than “Built” (96 distinct project ids, 11,984.86 MW, on the second reading below).

That sentence is deliberately narrow. It is not the claim that 12,034.86 MW of generation and storage is late — the register cannot support that, and this investigation does not make it. It is the claim that this many entries *say the date has passed and do not say Built*. What such an entry means is the second question, and the register does not answer it.

## The evidence

One copy of the register and nothing else: `data/raw/neso/tec-history/2026-09-15_neso-ckan.csv`, SHA-256 `d13406e495746f1b80e725321a5c7f95e21e0da16830bb6bd1f94ece172c9d5b`, 2,200 rows, fetched from the NESO data portal on 2026-09-15 and journalled with its resource URL and publication basis.

Every row of that copy falls in exactly one of four classes, which is check C3:

| Class | Rows |
|---|---|
| Dated earlier than the copy's own date, status not “Built” (**the census**) | **98** |
| Dated on or after the copy's own date, status not “Built” | 1,725 |
| Dated, status “Built” | 15 |
| No date the register's spellings can read | 362 |
| All rows | 2,200 |

Those two numbers meet: the copy carries 377 rows at “Built”, 15 of them dated, so 362 “Built” rows are undated — exactly the 362 undated rows in the copy. **Every row with no effective date is a row the register calls Built.** The register appears to clear the date once a project is built, which is why the residue this census measures — a date in the past with a status that is not Built — is the set of entries the register has neither moved on nor cleared.

For scale, the same copy carries 586,036.24 MW dated on or after 2026-09-15 across 1,736 rows, of which 503,676.63 MW is at status “Scoping”.

### By status, as the register prints it

| Status | Rows | MW |
|---|---|---|
| Consents Approved | 46 | 7,204.09 |
| Scoping | 35 | 2,877.5 |
| Under Construction/Commissioning | 8 | 1,435.52 |
| Awaiting Consents | 9 | 517.75 |

### By plant type, as the register prints it

The register prints compound plant types; this census keeps them whole and does not split a combined entry across its technologies.

| Plant type | Rows | MW |
|---|---|---|
| Wind Offshore | 5 | 4,800 |
| Energy Storage System | 43 | 3,706.95 |
| Energy Storage System;PV Array (Photo Voltaic/solar) | 23 | 1,081.12 |
| OCGT (Open Cycle Gas Turbine) | 3 | 897 |
| Wind Onshore | 10 | 555.79 |
| CCGT (Combined Cycle Gas Turbine) | 1 | 380 |
| Energy Storage System;Gas Reciprocating | 1 | 375 |
| Biomass | 1 | 150 |
| Thermal | 1 | 57 |
| Demand;PV Array (Photo Voltaic/solar) | 1 | 20 |
| Energy Storage System;Reactive Compensation | 4 | 12 |
| Reactive Compensation | 5 | 0 |

### By the year the date fell in

| Year | Rows | MW |
|---|---|---|
| 2020 | 1 | 380 |
| 2022 | 2 | 75 |
| 2023 | 6 | 336.6 |
| 2024 | 16 | 1,280.3 |
| 2025 | 39 | 4,792.37 |
| 2026 | 34 | 5,170.59 |

### The earliest dates on the list

| Effective from | Project | Connection site | Stage | Plant type | Status | MW |
|---|---|---|---|---|---|---|
| 2020-10-01 | Powersite @ Drakelow | Drakelow 400kV Substation | — | CCGT (Combined Cycle Gas Turbine) | Under Construction/Commissioning | 380 |
| 2022-02-21 | Arbroath Battery Substation | Arbroath GSP | — | Energy Storage System | Consents Approved | 35 |
| 2022-02-21 | Coupar Angus Battery | Coupar Angus 132/33kV GSP | — | Energy Storage System | Consents Approved | 40 |
| 2023-01-12 | Dollymans Storage | Rayleigh Main 132kV Substation | — | Energy Storage System | Scoping | 99.8 |
| 2023-05-31 | Cuxton 49.5MW BESS | Kingsnorth 400kV Substation | — | Energy Storage System | Consents Approved | 49.5 |
| 2023-08-02 | Pines Burn Wind Farm | Hawick GSP | — | Wind Onshore | Consents Approved | 50 |
| 2023-08-15 | Newtonwood BESS | Chesterfield GSP | — | Energy Storage System | Under Construction/Commissioning | 49.9 |
| 2023-10-31 | Dorenell Battery | Dorenell BESS 132KV substation | — | Wind Onshore | Scoping | 37.5 |
| 2023-11-01 | Seabank (Tertiary) | SEABANK 400/33kV SUBSTATION | — | Energy Storage System | Awaiting Consents | 49.9 |
| 2024-02-23 | Dalmarnock Road BESS | DALMARNOCK 132/33KV SUBSTATION | — | Energy Storage System | Scoping | 40 |

## The exhibit: one project, traced across every copy

A census of one copy cannot tell a reader whether a date that has passed is news or is eight years old, and it cannot see the entries whose date has not passed *yet* but has been rewritten repeatedly. For that the copies have to be read in sequence. The As-of Connection Record Certificate is 014's instrument for exactly that, and it is applied here to `Eggborough CCGT - OCGT - BESS`, 2,450 MW at Eggborough 400kV Substation, whose first stage is dated a fortnight after the copy this census reads.

It takes more than one certificate, and that is the first finding: **the register has called this project three different things.** A reader who searches today's copy for its current name and then looks for that name in older copies finds nothing before 1 July 2025.

Each bundle below is hash-addressed: its manifest's SHA-256 is the certificate id, the manifest lists every evidence file with its digest, and both the manifest and the certificate are witnessed by OpenTimestamps and by RFC 3161 tokens from two authorities. `python3 verify.py` inside a bundle recomputes every digest offline.

### `Eggborough`, 2014-01-31 to 2026-09-15

Bundle `eggborough-2014-01-31-2026-09-15`, certificate id `9896e04cbaf031b5a3de8668e6c9fc8567c0575c161af620388e94087430c54c`. 700 copies consulted (2014-01-31 to 2026-09-15); 2 with no matching row, 75 ambiguous, 2 suspect.

Every status the register published for this project's own row in the copies this bundle consulted — the row whose published plant type names a gas turbine plant or the hybrid label, which is what separates it from the coal station that shared its name until 2020 and from the storage project that took the name in 2024:

| Status as published | Copies | Rows | First copy | Last copy |
|---|---|---|---|---|
| Awaiting Consents | 400 | 400 | 2018-11-08 | 2023-12-29 |

| # | First shown in copy of | Field | Previously (last seen) | Now |
|---|---|---|---|---|
| 1 | 2014-05-12 | Agreement type | — (2014-05-09) | BCA |
| 2 | 2014-05-26 | Agreement type | BCA (2014-05-12) | — |
| 3 | 2014-07-04 | Agreement type | — (2014-05-26) | BCA |
| 4 | 2014-10-07 | Agreement type | BCA (2014-07-04) | — |
| 5 | 2015-05-08 | Presence | present (one row) (2015-04-24) | absent from a suspect copy (225 rows against 413 in the previous copy (46% fewer)) |
| 6 | 2015-05-18 | Presence | absent from a suspect copy (225 rows against 413 in the previous copy (46% fewer)) (2015-05-08) | present (one row) |
| 7 | 2015-09-23 | MW increase / decrease (stage TEC) | 0 (2015-09-11) | -1940 |
| 8 | 2015-09-23 | Cumulative total capacity (MW) | 1940 (2015-09-11) | 0 |
| 9 | 2015-09-23 | MW effective from (target date) | — (2015-09-11) | 2016-04-01 |
| 10 | 2016-04-05 | MW connected | 1940 (2016-03-31) | 0 |
| 11 | 2016-04-05 | MW increase / decrease (stage TEC) | -1940 (2016-03-31) | 0 |
| 12 | 2016-04-05 | MW effective from (target date) | 2016-04-01 (2016-03-31) | — |
| 13 | 2016-04-26 | Agreement type | — (2016-04-25) | BCA |
| 14 | 2016-05-25 | Agreement type | BCA (2016-05-04) | — |
| 15 | 2016-08-15 | Agreement type | — (2016-08-12) | BCA |
| 16 | 2016-08-30 | Agreement type | BCA (2016-08-15) | — |
| 17 | 2016-11-08 | Presence | present (one row) (2016-10-28) | absent |
| 18 | 2016-11-17 | Presence | absent (2016-11-08) | present (one row) |
| 19 | 2017-03-16 | Cumulative total capacity (MW) | 0 (2017-03-10) | 1870 |
| 20 | 2017-03-16 | MW effective from (target date) | — (2017-03-10) | 2017-04-01 |
| 21 | 2017-06-23 | MW connected | 0 (2017-06-15) | 1870 |
| 22 | 2018-11-08 | Presence | present (one row) (2018-11-01) | ambiguous (2 rows) |
| 23 | 2020-04-09 | Presence | ambiguous (2 rows) (2020-04-02) | present (one row) |
| 24 | 2020-06-05 | Connection site | Eggborough 400kV Substation (2020-05-28) | Eggborough 400kV |
| 25 | 2020-06-05 | Cumulative total capacity (MW) | 2450 (2020-05-28) | — |
| 26 | 2020-06-18 | Agreement type | — (2020-06-11) | Directly Connected |
| 27 | 2020-07-09 | Cumulative total capacity (MW) | — (2020-07-02) | 2450 |
| 28 | 2020-10-08 | Plant type | Hybrid (2020-10-01) | CCGT (Combined Cycle Gas Turbine); Energy Storage System; OCGT (Open Cycle Gas Turbine) |
| 29 | 2021-01-29 | MW effective from (target date) | 2024-10-01 (2021-01-26) | 2024-01-10 |
| 30 | 2021-02-02 | MW effective from (target date) | 2024-01-10 (2021-01-29) | 2024-10-01 |
| 31 | 2021-02-19 | MW effective from (target date) | 2024-10-01 (2021-02-16) | 2024-01-10 |
| 32 | 2021-02-23 | MW effective from (target date) | 2024-01-10 (2021-02-19) | 2024-10-01 |
| 33 | 2021-04-23 | MW effective from (target date) | 2024-10-01 (2021-04-20) | 2025-10-01 |
| 34 | 2021-05-28 | Customer name | Eggborough Power Ltd (2021-05-25) | EGGBOROUGH POWER LIMITED |
| 35 | 2021-07-30 | Plant type | CCGT (Combined Cycle Gas Turbine); Energy Storage System; OCGT (Open Cycle Gas Turbine) (2021-07-27) | Coal |
| 36 | 2021-08-03 | Plant type | Coal (2021-07-30) | CCGT (Combined Cycle Gas Turbine); Energy Storage System; OCGT (Open Cycle Gas Turbine) |
| 37 | 2021-11-26 | Project ID | — (2021-11-23) | a030Y000009rm7N |
| 38 | 2022-03-11 | MW effective from (target date) | 01/10/2025 (2022-03-09) | 2025-01-10 |
| 39 | 2022-03-16 | MW effective from (target date) | 2025-01-10 (2022-03-11) | 2025-10-01 |
| 40 | 2022-08-24 | Project ID | a030Y000009rm7N (2022-08-19) | a0l4L0000005ikt |
| 41 | 2022-09-16 | MW effective from (target date) | 2025-10-01 (2022-09-13) | 2026-10-01 |
| 42 | 2022-12-13 | Connection site | Eggborough 400kV (2022-12-09) | Eggborough 400kV Substation |
| 43 | 2023-06-16 | Presence | present (one row) (2023-06-13) | ambiguous (2 rows) |
| 44 | 2023-06-20 | Presence | ambiguous (2 rows) (2023-06-16) | present (one row) |
| 45 | 2023-12-05 | Presence | present (one row) (2023-12-01) | ambiguous (2 rows) |
| 46 | 2023-12-08 | Presence | ambiguous (2 rows) (2023-12-05) | present (one row) |
| 47 | 2024-01-05 | Customer name | EGGBOROUGH POWER LIMITED (2023-12-29) | SSE UTILITY SOLUTIONS LIMITED |
| 48 | 2024-01-05 | MW increase / decrease (stage TEC) | 2450 (2023-12-29) | 550 |
| 49 | 2024-01-05 | Cumulative total capacity (MW) | 2450 (2023-12-29) | 550 |
| 50 | 2024-01-05 | MW effective from (target date) | 2026-10-01 (2023-12-29) | 2032-06-16 |
| 51 | 2024-01-05 | Project status | Awaiting Consents (2023-12-29) | Scoping |
| 52 | 2024-01-05 | Plant type | CCGT (Combined Cycle Gas Turbine); Energy Storage System; OCGT (Open Cycle Gas Turbine) (2023-12-29) | Energy Storage System; PV Array (Photo Voltaic/solar) |
| 53 | 2024-01-05 | Project ID | a0l4L0000005ikt (2023-12-29) | a0l4L0000005ibx |
| 54 | 2024-06-18 | Project number | — (2024-06-14) | PRO-002049 |
| 55 | 2024-11-12 | Customer name | SSE UTILITY SOLUTIONS LIMITED (2024-11-05) | — |
| 56 | 2024-11-15 | Customer name | — (2024-11-12) | SSE EGGBOROUGH LIMITED |
| 57 | 2025-07-01 | Plant type | Energy Storage System;PV Array (Photo Voltaic/solar) (2025-04-01) | Energy Storage System |

### `Eggborough CCGT and BESS`, 2024-01-05 to 2025-07-22

Bundle `eggborough-ccgt-and-bess-2024-01-05-2025-07-22`, certificate id `0ed046aeba0f7d93c34b5fd78287dcbde92dc1eccc78eb0380452f011e3889e8`. 107 copies consulted (2024-01-05 to 2025-07-22); 2 with no matching row, 11 ambiguous, 0 suspect.

Every status the register published for this project's own row in the copies this bundle consulted — the row whose published plant type names a gas turbine plant or the hybrid label, which is what separates it from the coal station that shared its name until 2020 and from the storage project that took the name in 2024:

| Status as published | Copies | Rows | First copy | Last copy |
|---|---|---|---|---|
| Awaiting Consents | 105 | 116 | 2024-01-05 | 2025-04-01 |

| # | First shown in copy of | Field | Previously (last seen) | Now |
|---|---|---|---|---|
| 1 | 2024-06-18 | Project number | — (2024-06-14) | PRO-000136 |
| 2 | 2024-12-24 | Presence | present (one row) (2024-12-20) | ambiguous (2 rows) |
| 3 | 2025-07-01 | Presence | ambiguous (2 rows) (2025-04-01) | absent |

### `Eggborough CCGT - OCGT - BESS`, 2018-11-08 to 2026-09-15

Bundle `eggborough-ccgt-ocgt-bess-2018-11-08-2026-09-15`, certificate id `73b9152d2479f61cd5854ed1274f857a268bb2cede720e7bcb56d93ce1736b5c`. 512 copies consulted (2018-11-08 to 2026-09-15); 506 with no matching row, 6 ambiguous, 1 suspect.

Every status the register published for this project's own row in the copies this bundle consulted — the row whose published plant type names a gas turbine plant or the hybrid label, which is what separates it from the coal station that shared its name until 2020 and from the storage project that took the name in 2024:

| Status as published | Copies | Rows | First copy | Last copy |
|---|---|---|---|---|
| Awaiting Consents | 6 | 12 | 2025-07-01 | 2026-09-15 |

| # | First shown in copy of | Field | Previously (last seen) | Now |
|---|---|---|---|---|
| 1 | 2023-11-28 | Presence | absent (2023-11-24) | absent from a suspect copy (673 rows against 1392 in the previous copy (52% fewer)) |
| 2 | 2023-12-01 | Presence | absent from a suspect copy (673 rows against 1392 in the previous copy (52% fewer)) (2023-11-28) | absent |
| 3 | 2025-07-01 | Presence | absent (2025-04-01) | ambiguous (2 rows) |

### `Eggborough CCGT - OCGT - BESS`, stage 1, 2025-07-01 to 2026-09-15

Bundle `eggborough-ccgt-ocgt-bess-2025-07-01-2026-09-15`, certificate id `268237d523cfa2a94a211250fe363b18efdd39873b254aa3419cf3026d47ec09`. 6 copies consulted (2025-07-01 to 2026-09-15); 0 with no matching row, 0 ambiguous, 0 suspect.

Every status the register published for this project's own row in the copies this bundle consulted — the row whose published plant type names a gas turbine plant or the hybrid label, which is what separates it from the coal station that shared its name until 2020 and from the storage project that took the name in 2024:

| Status as published | Copies | Rows | First copy | Last copy |
|---|---|---|---|---|
| Awaiting Consents | 6 | 6 | 2025-07-01 | 2026-09-15 |

No change between the two copies in force.

### Reading the bundles in order

- The coal station's capacity leaves the register in the copy of **23 September 2015**: the stage TEC goes from 0 to −1,940 MW and the cumulative total from 1,940 MW to 0, effective 1 April 2016.
- A **second** row named `Eggborough` appears in the copy of **8 November 2018**. The bundle's extract for that copy publishes it as 2,450 MW, effective **1 April 2022**, status **Awaiting Consents**, plant type CCGT — beside the coal row, by then “Built” at 1,870 MW.
- The published target date then moves: 1 April 2022 until the copy of 2 April 2020; **1 October 2024** in the copy of 9 April 2020; **1 October 2025** in the copy of 23 April 2021; **1 October 2026** in the copy of 16 September 2022. It has not moved since — four years on the same date.
- Six of the changes listed above are the register printing one of those dates with day and month exchanged and then exchanging them back (1 October 2024 and 10 January 2024; 1 October 2025 and 10 January 2025). The certificate records what was published; the day-month correction is a test between two consecutive copies, which a certificate does not apply.
- In the copy of **5 January 2024** the name `Eggborough` stops being this project's. That one copy changes the customer, the capacity, the target date, the status, the plant type **and the project id** — the register has given the bare name to a different, smaller project, and this one continues under `Eggborough CCGT and BESS`.
- In the copy of **24 December 2024** that entry becomes two rows: the split into stages. By the copy of **1 July 2025** the name is `Eggborough CCGT - OCGT - BESS`, stage 1 at **1,999 MW effective 1 October 2026** and stage 2 at 451 MW effective 1 October 2027.
- The bundles between them see this project in **511 copies** of the register, from 2018-11-08 to 2026-09-15, and in every one of them the status reads “Awaiting Consents” — it has never read anything else.

### The two readings, and which one this investigation takes

The Planning Inspectorate decided the development consent order for the Eggborough gas plant on **20 September 2018**, under the Planning Act 2008, for up to about 2,500 MW. The register's first copy showing this entry as “Awaiting Consents” is seven weeks later, and every copy since says the same.

So either **the status field means a consent other than that order** — there are others a project of this kind needs — or **the field has not been refreshed in eight years**. This investigation does not choose. It publishes the record and says that the register does not, on its face, distinguish the two. The question has been put to NESO under the Environmental Information Regulations (FOI/26/216, answer due 13 October 2026) and the answer will be published here when it arrives, whichever way it goes.

*The consent order decision date above is stated from the public planning record and is **not pinned in this repository**; everything else in this section is a line of a witnessed certificate bundle. Pinning it is outstanding.*

That is the general point the exhibit is for. A status in this register is not dated, and a reader of one copy cannot tell a value written last week from one written in 2018. The census above counts 98 entries whose date has passed; it cannot tell you, from that copy alone, which of them the register has simply stopped looking at. Only the sequence of copies can, and the sequence is not published — it has to be rebuilt.

## What this does not say, and what could move it

**It does not say that any capacity is late.** The register's status is NESO's own best-known classification, and NESO says so. A row whose date has passed and whose status is not “Built” may have connected without the status being refreshed — which is the same staleness this investigation is about. The claim is about what the document says, and only that.

**Zero-capacity rows.** 8 of the 98 carry a published capacity of 0 MW. They are counted in the row count and add nothing to the MW total, so the row count and the MW figure are not two views of the same thing. Every selected row carries a capacity the register's number formats can read; none had to be excluded.

**Rows sharing a project id.** 2 project ids appear on more than one selected row. Counting rows gives 12,034.86 MW; counting each id once and keeping the largest of its rows gives 11,984.86 MW over 96 ids. Both readings were declared before the run and both are published; the rows are:

| Project id | Effective from | Project | Connection site | Stage | Plant type | Status | MW |
|---|---|---|---|---|---|---|---|
| a0l4L0000005ihQ | 2026-05-18 | Coylton 275kV Greener Grid Park | Coylton 275kV substation | 1 | Energy Storage System | Consents Approved | 50 |
| a0l4L0000005ihQ | 2026-04-30 | Coylton 275kV Greener Grid Park | Coylton 275kV substation | 2 | Energy Storage System | Scoping | 100 |
| a0l8e0000011zBp | 2025-05-31 | GF Upper Boat | Upper Boat 275kV Substation | 1 | Energy Storage System;Reactive Compensation | Scoping | 0 |
| a0l8e0000011zBp | 2025-10-31 | GF Upper Boat | Upper Boat 275kV Substation | 2 | Energy Storage System;Reactive Compensation | Scoping | 0 |

**Day and month.** Every dated cell in this copy is written `DD/MM/YYYY`, and the archive's schema report records that no other spelling appears in it. Six copies elsewhere in the archive do exchange day and month, so the census publishes the sensitivity: 18 of the selected rows (4,072.2 MW) have a date that could be read the other way round, and 2 of them (500 MW) would then not be past the date at all. The day-month correction is a test between two consecutive copies and is not applied to one copy.

**Against the ungoverned figures that prompted this.** The declaration records, before the freeze, what the author had already seen from an ad-hoc script outside this repository. The run agrees with it on the headline (98 rows, 12,034.86 MW), on the yearly table, on the eight zero-capacity rows, on the earliest entry, and on the scale line. It differs in two places, and the run is what is published:

- The scratch figures split the register's compound plant types across their technologies, which put 5,175 MW under Energy Storage. This census keeps compound types whole, as declared, so Energy Storage System alone is 3,706.95 MW and the rest sits under the combined labels in the table above.
- The two project ids that appear twice are the ones the scratch named, but not what it said they were. They are two genuine multi-stage entries — stage 1 and stage 2 of the same project, with different capacities and different dates — not a platform counted twice. Neither is a double count, which is why the two readings of the unit differ by 50 MW and not by more.

**Falsifiers declared before the run.** None fired. The three were: that day-month swapping could move more than a fifth of the selected MW into the future; that the copy carried a schema-report flag or a partial-export suspicion; and that the two readings of the unit differed by more than a tenth.

## Expert corner

- Declaration: `investigations/017-the-overdue-queue/DECLARATION.md`, SHA-256 `400b42f72b8c77759f88702d113594cdb2bb1b397f903486aaf39e92c7bc4b6d`, witnessed by OpenTimestamps and by RFC 3161 tokens from freetsa.org and DigiCert at the moment of the freeze, and committed with its proofs by `scripts/freeze`.
- Archive schema report the reading rules were written against: SHA-256 `ce3c61d735ff6349b553e6956d43ee042bd45a85995696dc15fff8620d33f570` (`archives/tec-register/`).
- The one copy: `data/raw/neso/tec-history/2026-09-15_neso-ckan.csv`, SHA-256 `d13406e495746f1b80e725321a5c7f95e21e0da16830bb6bd1f94ece172c9d5b`, 421,159 bytes, source `neso-ckan`, publication basis: CKAN resource last_modified 2026-09-15T16:48:30.055757 and filename tec-register-15-september-2026.csv; fetched live 2026-09-15
- Measure: `MW Increase / Decrease` as published, read as `Decimal`. The cumulative column is never added to it and never substituted for it.
- Boundary: an effective date **strictly earlier** than 2026-09-15, the copy's own publication date — not the date the census was run.
- Selected rows, one line each as published: `evidence/rows.ndjson` (98 lines, append-only). Summary: `evidence/census.json`.
- Checks that had to pass: C1 the status counts equal the schema report's for this copy; C2 dated plus undated is every row; C3 the four classes partition every row; C4 the copy is in the series' reading with the same row count, and is not suspect.

## Reproducibility

```
uv run --group registers python investigations/017-the-overdue-queue/run.py \
    --seal 400b42f72b8c --phase check
```

recomputes the census from the same copy and fails if a committed row would change. `scripts/check-rules` maps every rule in the declaration to the test that holds it; `scripts/verify-proofs` checks the declaration's timestamps against the roots committed under `trust/tsa/`.
