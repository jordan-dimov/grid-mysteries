# 017 — addendum: the storage rows, and a proposed fee laid beside them

*Computed 2026-09-17T22:54:47+00:00 from the committed evidence of 017's two runs and nothing else: `evidence/rows.ndjson` (SHA-256 `696d9a1841a63106…`) and `evidence/gate-rows.ndjson` (`3b34a38486b962d2…`), under declarations `400b42f7…` and `82856d65…`. The register copy was not re-read; nothing was fetched.*

**What this is.** A re-reading of rows the census already published, asked for on 2026-09-17 after Ofgem's proposal of a queue fee for battery projects. It is **outside** version 1's R7 (four breakdowns, no fifth after the run) and version 2's six Gate breakdowns, and it says so rather than pretending to be one of them. Nothing here enters `FINDINGS.md`, `post-facts.json` or any governed slot; an outbound use of a figure below needs its own frozen declaration. The three parts are kept apart: what the rows say, what a proposed fee could be read as covering, and an arithmetic illustration that is none of a saving, a loss, a liability or a forecast.

## Observation — the rows as committed

The census is 98 rows / 12,034.86 MW: entries in the copy of 2026-09-15 dated earlier than that copy and not Built. Plant type is readable on every one of them (0 rows carry no readable plant type). A row is *storage* when its printed plant type, split on the register's `;`, carries the token `Energy Storage System` exactly; `BESS` or `battery` in a project name counts for nothing.

**71 rows / 5,175.07 MW carry the storage token**: 43 rows / 3,706.95 MW print it alone, and 28 rows / 1,468.12 MW print it inside a compound type. A compound row's MW is the row's whole stage capacity; the register does not split it between technologies and neither does this. Two shares, as 017 R11 requires: the storage rows are 72.4% of the census's rows and 43.0% of its MW. 3 storage rows print a capacity of 0 and 0 storage rows print no capacity (017 R5); they are counted as rows and add nothing to any MW figure.

| Plant type as printed | Class | Rows | MW |
|---|---|---|---|
| Energy Storage System | storage only | 43 | 3,706.95 |
| Energy Storage System;PV Array (Photo Voltaic/solar) | storage in a compound type | 23 | 1,081.12 |
| Energy Storage System;Gas Reciprocating | storage in a compound type | 1 | 375 |
| Energy Storage System;Reactive Compensation | storage in a compound type | 4 | 12 |

| Status as printed (storage rows) | Rows | MW |
|---|---|---|
| Scoping | 28 | 2,298.2 |
| Consents Approved | 30 | 1,945.1 |
| Awaiting Consents | 8 | 474.25 |
| Under Construction/Commissioning | 5 | 457.52 |

### How far behind the copy's own date

Days from the row's effective date to 2026-09-15, the copy's publication date (017 R2). Bucket upper bounds are inclusive.

| | Storage only | Storage in a compound type |
|---|---|---|
| Rows / MW | 43 / 3,706.95 | 28 / 1,468.12 |
| Shortest, days | 14 | 50 |
| Median, days | 326 | 319 |
| Longest, days | 1667 | 745 |
| up to 90 days | 7 rows / 306.8 MW | 6 rows / 597.8 MW |
| 91 to 365 days | 16 rows / 1,968.15 MW | 11 rows / 467.8 MW |
| 366 to 730 days | 10 rows / 906.4 MW | 10 rows / 390.52 MW |
| more than 730 days | 10 rows / 525.6 MW | 1 row / 12 MW |

### The Gate cell, where the committed evidence carries it

Version 2 committed a Gate cell only for the 17 overdue rows of the confirmed tier. **13 of those 17 are storage rows, 1,317.42 MW**: Eccles BESS, Zenobe Eccles Battery Storage, Coylton 275kV Greener Grid Park, Persley Croft BESS, Holmston Farm Battery Energy Storage System, Lovat Estate BESS, Glenrothes BESS, Bankside BESS, Balbougie Energy Centre, Dalmarnock Road BESS, Whitelaw Brae BESS, Bilbo Farm, Kincraig Energy Centre. For the other 58 storage rows the Gate cell is **not in the committed evidence**. It is not blank and it is not inferred; a storage-by-Gate split of the whole census would be a seventh Gate breakdown and needs a version 3 declaration frozen before it is computed.

**Swapped reading.** Storage rows whose date, read day-month swapped, would fall on or after the copy's date (017 R3): 1 row, 500 MW. That is inside every figure above, as the census rule declares; anyone quoting the storage MW should quote this sentence with it.

| Class | Project | Plant type | Status | MW | Effective | Days behind | Gate |
|---|---|---|---|---|---|---|---|
| storage only | Eccles BESS | Energy Storage System | Scoping | 500 | 2026-04-12 | 156 | 2 |
| storage only | Zenobe Eccles Battery Storage | Energy Storage System | Scoping | 400 | 2026-04-30 | 138 | 2 |
| storage only | Monk Fryston SSE | Energy Storage System | Consents Approved | 320 | 2025-10-31 | 319 | not committed |
| storage only | Sheaf Energy | Energy Storage System | Consents Approved | 249 | 2025-04-30 | 503 | not committed |
| storage only | WindyHill BESS2 Facility | Energy Storage System | Scoping | 200 | 2025-07-27 | 415 | not committed |
| storage only | Axminster | Energy Storage System | Awaiting Consents | 120 | 2024-10-31 | 684 | not committed |
| storage only | Coylton 275kV Greener Grid Park | Energy Storage System | Scoping | 100 | 2026-04-30 | 138 | not committed |
| storage only | Zenobe Blackhillock 300 MW | Energy Storage System | Consents Approved | 100 | 2026-04-01 | 167 | not committed |
| storage only | Dollymans Storage | Energy Storage System | Scoping | 99.8 | 2023-01-12 | 1342 | not committed |
| storage only | Stella Battery Energy Storage | Energy Storage System | Scoping | 78 | 2025-09-27 | 353 | not committed |
| storage only | Legacy Tertiary Connection | Energy Storage System | Consents Approved | 57 | 2024-08-31 | 745 | not committed |
| storage only | Lister Drive Shaw | Energy Storage System | Scoping | 57 | 2026-09-01 | 14 | not committed |
| storage only | Mill Hill Tertiary Connection | Energy Storage System | Consents Approved | 57 | 2025-10-24 | 326 | not committed |
| storage only | Whitegate Tertiary Connection | Energy Storage System | Consents Approved | 57 | 2024-06-30 | 807 | not committed |
| storage only | Willington | Energy Storage System | Scoping | 57 | 2026-06-30 | 77 | not committed |
| storage only | Coylton 275kV Greener Grid Park | Energy Storage System | Consents Approved | 50 | 2026-05-18 | 120 | 2 |
| storage only | Persley Croft BESS | Energy Storage System | Scoping | 50 | 2026-07-31 | 46 | 2 |
| storage only | Sundon | Energy Storage System | Scoping | 50 | 2025-09-05 | 375 | not committed |
| storage only | Harrington Franklin Limited | Energy Storage System | Awaiting Consents | 49.95 | 2025-10-31 | 319 | not committed |
| storage only | Holmston Farm Battery Energy Storage System | Energy Storage System | Scoping | 49.9 | 2026-07-31 | 46 | 2 |
| storage only | Iron Acton | Energy Storage System | Consents Approved | 49.9 | 2026-04-13 | 155 | not committed |
| storage only | Lovat Estate BESS | Energy Storage System | Scoping | 49.9 | 2026-05-31 | 107 | 2 |
| storage only | Newtonwood BESS | Energy Storage System | Under Construction/Commissioning | 49.9 | 2023-08-15 | 1127 | not committed |
| storage only | Overhill BESS | Energy Storage System | Consents Approved | 49.9 | 2024-10-31 | 684 | not committed |
| storage only | Provan Gas Works BESS | Energy Storage System | Scoping | 49.9 | 2026-06-30 | 77 | not committed |
| storage only | Seabank (Tertiary) | Energy Storage System | Awaiting Consents | 49.9 | 2023-11-01 | 1049 | not committed |
| storage only | Wright Street BESS | Energy Storage System | Scoping | 49.9 | 2025-10-31 | 319 | not committed |
| storage only | Cuxton 49.5MW BESS | Energy Storage System | Consents Approved | 49.5 | 2023-05-31 | 1203 | not committed |
| storage only | Fairholme BESS | Energy Storage System | Consents Approved | 47.5 | 2025-02-28 | 564 | not committed |
| storage only | Indian Queens | Energy Storage System | Consents Approved | 47.5 | 2024-07-30 | 777 | not committed |
| storage only | Mannington Tertiary | Energy Storage System | Consents Approved | 47.5 | 2025-10-30 | 320 | not committed |
| storage only | Minety | Energy Storage System | Consents Approved | 47.5 | 2024-10-31 | 684 | not committed |
| storage only | Pond Hill Farm 1 | Energy Storage System | Consents Approved | 47.5 | 2025-04-30 | 503 | not committed |
| storage only | Pond Hill Farm 2 BESS | Energy Storage System | Consents Approved | 47.5 | 2025-05-31 | 472 | not committed |
| storage only | St Dennis Hendra | Energy Storage System | Consents Approved | 47.5 | 2024-10-31 | 684 | not committed |
| storage only | Glenrothes BESS | Energy Storage System | Consents Approved | 46 | 2025-10-30 | 320 | 2 |
| storage only | Bankside BESS | Energy Storage System | Consents Approved | 43 | 2025-11-24 | 295 | 2 |
| storage only | Balbougie Energy Centre | Energy Storage System | Consents Approved | 42 | 2026-07-31 | 46 | 2 |
| storage only | Coupar Angus Battery | Energy Storage System | Consents Approved | 40 | 2022-02-21 | 1667 | not committed |
| storage only | Dalmarnock Road BESS | Energy Storage System | Scoping | 40 | 2024-02-23 | 935 | 2 |
| storage only | Arbroath Battery Substation | Energy Storage System | Consents Approved | 35 | 2022-02-21 | 1667 | not committed |
| storage only | Ardoch Farm Battery Storage | Energy Storage System | Scoping | 27 | 2026-04-30 | 138 | not committed |
| storage only | Whitelaw Brae BESS | Energy Storage System | Scoping | 1 | 2026-07-31 | 46 | 2 |
| storage in a compound type | Thurrock Power Station | Energy Storage System;Gas Reciprocating | Under Construction/Commissioning | 375 | 2026-06-30 | 77 | not committed |
| storage in a compound type | Benthead Solar | Energy Storage System;PV Array (Photo Voltaic/solar) | Scoping | 63 | 2025-04-03 | 530 | not committed |
| storage in a compound type | Cowley (Tertiary) | Energy Storage System;PV Array (Photo Voltaic/solar) | Scoping | 57 | 2025-11-14 | 305 | not committed |
| storage in a compound type | Melksham (Tertiary) | Energy Storage System;PV Array (Photo Voltaic/solar) | Scoping | 57 | 2026-06-26 | 81 | not committed |
| storage in a compound type | Norwich | Energy Storage System;PV Array (Photo Voltaic/solar) | Consents Approved | 57 | 2025-12-18 | 271 | not committed |
| storage in a compound type | Walpole 1 (Tertiary) | Energy Storage System;PV Array (Photo Voltaic/solar) | Scoping | 57 | 2025-08-01 | 410 | not committed |
| storage in a compound type | Wymondley | Energy Storage System;PV Array (Photo Voltaic/solar) | Awaiting Consents | 57 | 2025-10-31 | 319 | not committed |
| storage in a compound type | Bicker Fen 1 Solar | Energy Storage System;PV Array (Photo Voltaic/solar) | Awaiting Consents | 50 | 2025-09-26 | 354 | not committed |
| storage in a compound type | Bicker Fen 2 Solar | Energy Storage System;PV Array (Photo Voltaic/solar) | Awaiting Consents | 50 | 2026-07-27 | 50 | not committed |
| storage in a compound type | Wymondley Solar Farm | Energy Storage System;PV Array (Photo Voltaic/solar) | Consents Approved | 50 | 2025-10-31 | 319 | not committed |
| storage in a compound type | Braintree | Energy Storage System;PV Array (Photo Voltaic/solar) | Awaiting Consents | 49.9 | 2024-10-30 | 685 | not committed |
| storage in a compound type | Bramford Tertiary | Energy Storage System;PV Array (Photo Voltaic/solar) | Consents Approved | 49.9 | 2026-07-16 | 61 | not committed |
| storage in a compound type | JBM Solar 13 - Melksham | Energy Storage System;PV Array (Photo Voltaic/solar) | Scoping | 49.9 | 2026-07-17 | 60 | not committed |
| storage in a compound type | Landulph | Energy Storage System;PV Array (Photo Voltaic/solar) | Consents Approved | 49.9 | 2026-05-18 | 120 | not committed |
| storage in a compound type | West Weybridge (Tertiary) | Energy Storage System;PV Array (Photo Voltaic/solar) | Scoping | 49.9 | 2025-10-31 | 319 | not committed |
| storage in a compound type | Norwich Yare | Energy Storage System;PV Array (Photo Voltaic/solar) | Consents Approved | 49.5 | 2025-12-18 | 271 | not committed |
| storage in a compound type | Mannington | Energy Storage System;PV Array (Photo Voltaic/solar) | Consents Approved | 47.5 | 2025-11-30 | 289 | not committed |
| storage in a compound type | Somerford | Energy Storage System;PV Array (Photo Voltaic/solar) | Consents Approved | 47.5 | 2025-06-30 | 442 | not committed |
| storage in a compound type | Southfields | Energy Storage System;PV Array (Photo Voltaic/solar) | Awaiting Consents | 47.5 | 2025-06-30 | 442 | not committed |
| storage in a compound type | Claydon Solar B (A033) | Energy Storage System;PV Array (Photo Voltaic/solar) | Scoping | 45 | 2025-04-11 | 522 | not committed |
| storage in a compound type | Tale Lane Solar / A008 Langford | Energy Storage System;PV Array (Photo Voltaic/solar) | Scoping | 35 | 2025-04-15 | 518 | not committed |
| storage in a compound type | Bilbo Farm | Energy Storage System;PV Array (Photo Voltaic/solar) | Scoping | 25 | 2024-10-31 | 684 | 2 |
| storage in a compound type | Kincraig Energy Centre | Energy Storage System;PV Array (Photo Voltaic/solar) | Under Construction/Commissioning | 20.62 | 2025-04-30 | 503 | 2 |
| storage in a compound type | Keithick 16 Solar & BESS | Energy Storage System;PV Array (Photo Voltaic/solar) | Consents Approved | 16 | 2026-06-30 | 77 | not committed |
| storage in a compound type | Swansea Greener Grid Park - Connection 1 | Energy Storage System;Reactive Compensation | Under Construction/Commissioning | 12 | 2024-08-31 | 745 | not committed |
| storage in a compound type | Cryogenic Battery System (Synchronous) | Energy Storage System;Reactive Compensation | Under Construction/Commissioning | 0 | 2026-05-08 | 130 | not committed |
| storage in a compound type | GF Upper Boat | Energy Storage System;Reactive Compensation | Scoping | 0 | 2025-05-31 | 472 | not committed |
| storage in a compound type | GF Upper Boat | Energy Storage System;Reactive Compensation | Scoping | 0 | 2025-10-31 | 319 | not committed |

## Interpretation — what a proposed fee could be read as covering

Everything in this section rests on facts held as external assertions in the business register (etrmbiz slots `gb-battery-queue-fee-2026` and `gb-data-centre-queue-commitment-fee-2026`), cited and not re-derived here. As those slots record it: on 2026-09-17 Ofgem proposed, for consultation, a fee for battery-storage projects waiting in the GB connections queue, £3,000 per MW and potentially £25,000 per MW if the queue remains significantly oversubscribed, refunded if the project connects. The slot also records that **Ofgem's own statement has not been read**; the figures are Bloomberg's report of it.

What the register can and cannot say about which rows such a fee would reach:

- The register prints `Energy Storage System`, not *battery*. Whether every row so labelled is a battery, and whether a compound `Energy Storage System;PV Array` row would be assessed on its whole MW, on a storage share, or not at all, is not knowable from the register.
- Whether the proposal reaches projects that already hold an offer, or only new applications; whether it reaches transmission-connected projects, distribution-connected ones, or both; whether *per MW* means TEC or some other capacity; and whether Gate 1 and Gate 2 projects are treated alike — none of that is in the second-hand report, and none of it is inferred here.
- A row that is past its date and not Built is, on the register's face, still in the queue. Whether NESO or Ofgem would count it as *waiting* under the proposal is their definition to supply, not this addendum's.

So the honest statement is: **these are the storage rows the census found; which of them a fee that is only proposed would fall on is not determinable from the register, and is left open.**

## Illustration — rate times MW, and nothing more

**This is an illustration.** Each figure is a proposed per-MW rate multiplied by a published capacity. It is **not** a saving, a loss, a liability, an amount any party would post, owe or forfeit, or a forecast of what the consultation will decide. The rates are proposed, refundable on connection as reported, and may never apply to any row here.

| Rows | MW | at £3,000 / MW | at £25,000 / MW |
|---|---|---|---|
| Storage only | 3,706.95 | £11,120,850 | £92,673,750 |
| Storage only and compound together | 5,175.07 | £15,525,210 | £129,376,750 |
| Storage rows in the confirmed tier (Gate 2), a subset | 1,317.42 | £3,952,260 | £32,935,500 |

## What this addendum never claims

- That any project is late, has failed, or will pay anything. The register records a plant type, a date and a status; the fee is a proposal; the product of the two is arithmetic.
- That `Energy Storage System` means battery, or that a compound row is a battery row.
- That the storage share of the census has any meaning beyond this copy, or that it is a breakdown of the census under either declaration.

## Reproducibility

`uv run python investigations/017-the-overdue-queue/addendum.py` recomputes this file and `evidence/addendum-storage.json` from the committed rows, and refuses if the rows no longer sum to the census's headline. Rules are in `grid_mysteries.investigations.overdue_queue_addendum`, tested in `tests/test_overdue_queue_addendum.py`. Input digests: `rows.ndjson` `696d9a1841a631069f80dfd1a453b3614f4bb195ef8506106762fe3fc7a6dad5`; `gate-rows.ndjson` `3b34a38486b962d2834c29bdd0f7146554abf9df75c785e83c47cc2ebd67e8b2`; `census.json` `dfde14da46aa7409437b8a3585f74a583c1185410c04f23006b6c0a987c1a050`; `gate.json` `ad91e6677b677d866851d2409f926218ebf0e247158d740542c994a116174ce9`; the copy `d13406e495746f1b80e725321a5c7f95e21e0da16830bb6bd1f94ece172c9d5b`.
