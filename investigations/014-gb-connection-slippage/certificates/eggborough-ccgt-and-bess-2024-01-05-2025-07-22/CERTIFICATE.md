# As-of Connection Record Certificate

**Project:** Eggborough CCGT and BESS  
**Dates certified:** 2024-01-05 and 2025-07-22  
**Certificate id:** `0ed046aeba0f7d93c34b5fd78287dcbde92dc1eccc78eb0380452f011e3889e8`  
**Issued:** 2026-09-17 by A115 Ltd (Grid Mysteries)  
**Register copies consulted:** 107 (2024-01-05 to 2025-07-22); 2 with no matching row, 11 ambiguous, 0 suspect (partial exports)

*Independently verifiable provenance, publication time and reconstruction methodology, suitable for scrutiny by counsel, experts, lenders and regulators.*

## 1. What the register published on each date

| Field | As published on 2024-01-05 (copy of 2024-01-05) | As published on 2025-07-22 (copy of 2025-07-22) |
|---|---|---|
| Presence | present (one row) | absent |
| Project name | Eggborough CCGT and BESS | — |
| Customer name | EGGBOROUGH POWER LIMITED | — |
| Connection site | Eggborough 400kV Substation | — |
| Stage | — | — |
| MW connected | 0 | — |
| MW increase / decrease (stage TEC) | 2450 | — |
| Cumulative total capacity (MW) | 2450 | — |
| MW effective from (target date) | 2026-10-01 | — |
| Project status | Awaiting Consents | — |
| Agreement type | Directly Connected | — |
| Host TO | NGET | — |
| Plant type | CCGT (Combined Cycle Gas Turbine); Energy Storage System; OCGT (Open Cycle Gas Turbine) | — |
| Project ID | a0l4L0000005ikt | — |
| Project number | — | — |
| Gate | — | — |

Copy in force on 2024-01-05: SHA-256 `04e301644373bd28dab7d68d44fa8a6a89cbe4bab0cffcc363bb04a7d19d8535`  
Copy in force on 2025-07-22: SHA-256 `d875470279cc562b07fbe128ecc66f6215711614eee8bf5134012dbbec97bde3`

## 2. Every change between the two dates

Each change is dated by the first copy of the register that showed it; the previous value is dated by the last copy that still carried it. Between those two copies no copy is held, so the change entered the published register somewhere in that interval.

| # | First shown in copy of | Field | Previously published (last seen in copy of) | Newly published |
|---|---|---|---|---|
| 1 | 2024-06-18 | Project number | — (2024-06-14) | PRO-000136 |
| 2 | 2024-12-24 | Presence | present (one row) (2024-12-20) | ambiguous (2 rows) |
| 3 | 2025-07-01 | Presence | ambiguous (2 rows) (2025-04-01) | absent |

## 3. Scope

This certificate states what NESO's published Transmission Entry Capacity (TEC) Register said about the named project on each of the two dates, and every change between them, each with the first copy of the register that showed it. It is a factual record of publication. It contains no forecast of energisation, no view on the cause of any change, and no opinion on any party's contractual entitlement. NESO's own caveat applies: project status in the register is NESO's best-known classification, not authoritative project information.

## 4. Method

Copies of the register (vintages) come from NESO's disclosures under the Environmental Information Regulations (one file per publication date), Wayback Machine captures of the data-portal resource, and live fetches of that resource; each copy's publication date and its SHA-256 are journalled at acquisition. The copy in force on a date is the latest published on or before it. Rows are matched to the project by the register's own project name (letters and digits, case ignored) and, where stated, stage; customer name and connection site are attributes whose changes are recorded. A copy with no matching row is an absence and one with several is ambiguous; both are recorded as changes of presence. A copy whose row count is more than a fifth below the previous copy's and whose successor recovers is a suspect copy (a partial export); an absence from such a copy is reported as that, not as an absence from the register. Values are compared as published, with dates parsed (so a respelled date is not a change), numbers compared numerically and text compared ignoring case and whitespace; the printed values are the published spellings. Two declared unifications apply: the register's project id is compared on its 15-character form (the 18-character form appends a checksum to the same id), and the agreement-type labels "Directly Connected" and "Direct Connection" are one label. Every other difference in published text is a change.

## 5. Evidence bundle

This certificate is rendered from `certificate.json` in the bundle and from the bundle's manifest. The manifest (`MANIFEST.json`, SHA-256 `0ed046aeba0f7d93c34b5fd78287dcbde92dc1eccc78eb0380452f011e3889e8`, which is the certificate id) lists 5 files with their digests: the certificate record, the rows matched in every copy consulted (`extracts.ndjson`), the journal lines that identify each copy's source, publication basis and digest (`journal-extract.ndjson`), and the two full register copies in force on the certified dates (`registers/`). This document quotes the manifest's digest and so is not listed in it; it is witnessed beside it. Run `python3 verify.py` in the bundle to recompute every digest offline. The manifest's digest and this document's are each witnessed by OpenTimestamps and by RFC 3161 tokens from two authorities, in the files beside them.


Declarations under which the register archive is maintained and this certificate produced, in investigations/014-gb-connection-slippage/: `DECLARATION.md` SHA-256 `e4aba4c923b58e9c36e10d16d9a715d6cae1ce90081c9ed1f1b8bf5196f8c01a`; `DECLARATION-v2.md` SHA-256 `f2209b3cfd4dd0b276f1776293d60f83c65f3354db42b13e28348848c79a7a45`.

---

A115 Ltd (Grid Mysteries). Factual findings only; no expert opinion is expressed. Reproduction of the method is invited; the code and tests are public.
