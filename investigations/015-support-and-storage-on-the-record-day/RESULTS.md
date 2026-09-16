# 015 — results: support and storage on the record day

**Run**: 2026-09-16, from bytes pinned by 012, 003 and this study's own
acquisition. Declaration `DECLARATION.md` (SHA-256 `77a192f103fde896…`,
witnessed by OpenTimestamps and two RFC 3161 authorities before the run).
Evidence: `evidence/links.json` (the link table), `evidence/wind-by-scheme.json`,
`evidence/storage.json`, `evidence/summary.json`, `evidence/reading.json` (the
column bindings from the schema pass), and the three acquisition manifests.
Logic and tests: `src/grid_mysteries/investigations/support_and_storage.py`,
`tests/test_support_and_storage.py`. This file is rendered by
`render_results.py` from the evidence; it computes nothing. **Unpublished.**

## 1. The mystery

On 8 September 2026, Britain's most expensive constraint day, which support
scheme stood behind the wind farms that were paid to stop, and what could
the batteries on the system actually have done about it?

## 2. The evidence

**Part 1 — wind bids by support scheme.** 77 wind units carried bid
cashflow on the day, £3,768,601 paid out on bids in total (012's figure). Each
was linked to LCCC's CfD-to-BM-unit mapping by the publisher's own BM-unit
identifier (grade A: 28 links over 20 units) and to
Ofgem's Accredited Stations (RO) report by the declared name-and-capacity test
(grade B: 10; name only, grade C: 39). Volumes are accepted bid MWh
from the DISPTAV `Tagged` type, the one that reconciles with the day's
settlement totals under 013's gate.

| Scheme | Units | Accepted bid MWh | Bid £ paid out | Bid £ signed | £/MWh | Share of wind bid £ |
|---|---|---|---|---|---|---|
| CfD (grade A, LCCC mapping) | 20 | 35,295 | £953,815 | £429,737 | 27.02 | 25.3 % |
| RO (grade B, name and capacity) | 10 | 5,007 | £393,919 | £393,919 | 78.68 | 10.4 % |
| Both | 0 | 0 | £0 | £0 | — | 0.0 % |
| Unmatched | 36 | 67,414 | £1,694,937 | £1,694,937 | 25.14 | 45.0 % |
| RO possible (grade C, sensitivity) | 11 | 11,089 | £725,930 | £725,930 | 65.46 | 19.3 % |

The ten largest unmatched units, by bid £ paid:

| Unit | Name | Lead party | MW | Bid £ paid |
|---|---|---|---|---|
| `T_MOWWO-4` | Moray West OWF4 | Moray Offshore Wind West Ltd | 287.0 | £173,018 |
| `T_BHLAW-1` | Bhlaraidh Windfarm 1 | SSE Generation Ltd | 108.1 | £132,931 |
| `T_SOKYW-1` | South Kyle Wind Farm | South Kyle Wind Farm Limited | 426.9 | £119,904 |
| `T_SGRWO-6` | Seagreen1 Offshore WF 6 | Seagreen Wind Energy Limited | 380.0 | £108,363 |
| `T_AKGLW-3` | AIKENGALL2A-W | AIK2A Sustainable Energy Ltd | 163.4 | £85,705 |
| `T_CREAW-1` | Creag Riabhach Wind Farm | Creag Riabhach Wind Farm Ltd | 93.0 | £78,616 |
| `T_GORDW-1` | Gordon Bush | SSE Generation Ltd | 86.8 | £77,577 |
| `T_SGRWO-1` | Seagreen1 Offshore WF 1 | Seagreen Wind Energy Limited | 358.0 | £76,194 |
| `T_MOWWO-2` | Moray West OWF2 | Moray Offshore Wind West Ltd | 215.0 | £73,964 |
| `T_MOWWO-1` | Moray West OWF1 | Moray Offshore Wind West Ltd | 215.0 | £71,556 |

**Part 2 — the energy-limited units.** 28 BM units published a maximum
delivery volume (MDO or MDB) for the day: 950 MW of registered export
capacity in all, 149 MW of it north of B6 (4 units, graded
B: 1, C: 3). The constraint, read as periods
with accepted wind-unit bid volume, ran for **48 of 48 periods** (24.0 hours;
longest contiguous run 24.0 hours). 27 of the 28 units
were paid something on the day, almost all on offers. Hours of energy are the
unit's maximum published delivery volume divided by its registered capacity:
R3p uses only records published before the first constrained period began,
R3h everything published for the day. Sides of B6 are graded as declared (A:
CMIS arming; B: TEC register host TO by name and capacity; C: GSP group;
unknown otherwise).

| Unit | Name | Fuel | Export MW | Import MW | Side of B6 (grade) | Export h R3p | Export h R3h | Import h R3p | Offer MWh | Offer £ | Bid MWh | Bid £ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `E_LITRB-1` | Little Raith BESS | OTHER | 50.0 | -50.0 | north (C) | 1.14 | 1.72 | -0.10 | 50 | £6,692 | 224 | £0 |
| `E_ROARB-1` | Roaring Hill BESS | OTHER | 50.0 | -50.0 | north (C) | 0.97 | 1.67 | -0.05 | 37 | £4,868 | 200 | £0 |
| `E_JAMBB-1` | Jamesfield 1 Battery Storage | OTHER | 30.0 | -30.0 | north (C) | 0.94 | 1.47 | 0.00 | 21 | £2,895 | 124 | £0 |
| `E_JAMBB-2` | Jamesfield 2 Battery Storage | OTHER | 19.0 | -19.3 | north (B) | 0.93 | 1.31 | -0.23 | 18 | £2,387 | 60 | £0 |
| `T_NTRVB-1` | Native River | — | 57.0 | -57.0 | south (B) | 0.14 | 0.98 | -0.85 | 21 | £3,671 | 0 | £0 |
| `E_BURWB-2` | Burwell 1 | — | 52.0 | -52.0 | south (C) | 0.68 | 0.68 | 0.00 | 19 | £3,943 | 0 | £0 |
| `E_CHAPB-1` | Chapel Farm BESS | — | 50.2 | -50.2 | south (C) | 0.99 | 1.19 | -0.12 | 6 | £961 | 0 | £0 |
| `E_SKELB-1` | Skelmersdale Battery | — | 49.9 | -50.6 | south (C) | 0.88 | 0.88 | 0.00 | 0 | — | 0 | — |
| `E_CLAYB-1` | ClayTye Farm 1 Battery Storage | — | 49.5 | -49.5 | south (C) | 0.76 | 1.08 | -0.08 | 15 | £2,668 | 0 | £0 |
| `E_CLAYB-2` | ClayTye Farm 2 Battery Storage | — | 49.5 | -49.5 | south (C) | 1.06 | 1.19 | -0.12 | 11 | £1,882 | 0 | £0 |
| `E_ILMEB-1` | Ilmer Lane BESS | — | 49.5 | -49.5 | south (C) | 0.94 | 1.52 | -0.47 | 38 | £6,803 | 7 | £0 |
| `E_THMRB-1` | Thame Road  BESS | — | 49.5 | -49.5 | south (C) | 0.89 | 1.71 | -0.03 | 114 | £22,519 | 22 | £0 |
| `2__HANGE004` | 2__HANGE004 | — | 49.3 | -51.8 | south (C) | 0.68 | 0.68 | -0.09 | 22 | £3,357 | 6 | £0 |
| `2__HCMRO002` | 2__HCMRO002 | — | 47.4 | -37.4 | south (C) | 0.18 | 0.42 | -0.26 | 0 | £88 | 0 | £0 |
| `E_BARNB-1` | Hunningley Stairfoot BESS | — | 44.0 | -44.0 | south (B) | 0.61 | 0.61 | 0.00 | 45 | £8,121 | 3 | £0 |
| `2__MCMRO002` | 2__MCMRO002 | — | 36.8 | -37.1 | south (C) | 0.61 | 0.77 | -0.03 | 15 | £2,545 | 35 | £0 |
| `E_CONTB-1` | Contego Battery | — | 35.8 | -34.4 | south (B) | 0.56 | 0.81 | -0.41 | 22 | £3,941 | 0 | £0 |
| `2__FCMRO004` | 2__FCMRO004 | — | 35.7 | -35.7 | south (C) | 0.96 | 1.44 | -0.09 | 41 | £7,855 | 11 | £0 |
| `T_PINFB-1` | T_PINFB-1 | OTHER | 27.1 | -27.9 | unknown (-) | 0.92 | 0.92 | 0.00 | 9 | £1,720 | 9 | £0 |
| `E_CRSSB-1` | Carnegie Road 1 | — | 20.0 | -20.6 | south (C) | 0.00 | 0.26 | 0.00 | 4 | £497 | 0 | £0 |
| `E_FARNB-1` | Farnham BESS | — | 20.0 | -20.0 | south (B) | 0.91 | 1.11 | -0.43 | 14 | £2,328 | 1 | £0 |
| `E_HAWKB-1` | HawkersHill  Battery | — | 20.0 | -20.0 | south (C) | 0.95 | 0.95 | -1.05 | 6 | £1,261 | 0 | £0 |
| `E_OLDHB-1` | Oldham BESS | — | 20.0 | -20.0 | south (C) | 0.22 | 0.57 | 0.00 | 14 | £2,782 | 4 | £0 |
| `2__FCMRO003` | 2__FCMRO003 | — | 19.7 | -20.2 | south (C) | 1.19 | 1.83 | -0.40 | 0 | £44 | 21 | £0 |
| `E_BROAB-1` | Broadditch Battery | — | 11.0 | -11.0 | south (C) | 0.94 | 1.42 | -0.02 | 3 | £497 | 0 | £0 |
| `E_BHOLB-1` | Holes Bay Battery | — | 7.1 | -7.4 | south (C) | 0.67 | 0.99 | -0.66 | 0 | £19 | 0 | £0 |
| `V__AZENO002` | V__AZENO002 | OTHER | 0.0 | 0.0 | south (C) | — | — | — | 16 | £3,652 | 3 | £0 |
| `V__JZENO001` | V__JZENO001 | OTHER | 0.0 | 0.0 | south (C) | — | — | — | 0 | £73 | 0 | £0 |

## 3. Explanations tested

- **Is the unmatched remainder a matching failure or an absence from the
  registers?** Mostly the latter, and the declared rule was right not to
  guess. LCCC's mapping has 165 rows and names Moray East's three units but
  none of Moray West's, and none for Seagreen, Bhlaraidh or South Kyle,
  which lead the unmatched list. Whatever those units' contracts are, the
  publisher's mapping does not carry them on the day, and the declaration
  allowed CfD links only by that identifier. A grade-B CfD link by name
  against the portfolio's `Name_of_CFD_Unit` would be a new rule for a new
  declaration, not an amendment.
- **Why is Griffin grade C, not B?** The RO station carries 186 MW; only
  some of the station's BM units bid on the day, so the summed capacity of
  the bidding units sits outside the 15 % band. The rule compares what bid,
  not what exists; recorded as a limit, not corrected.
- **CfD units paid, or paying?** 10 of the 20 CfD-linked units carried
  negative bid cashflows on the day, £524,079 in all, so their
  signed total (£429,737) is well below their paid-out total
  (£953,815). The table shows both. Why a unit's bids are priced as they
  are is not a question this record answers.
- **Is the RO capacity column usable?** Yes: every one of the 26,578 rows
  carries a numeric declared net capacity in kW; the schema pass found no
  identifier column, so RO grade A was not applicable and the declaration's
  F1 did not fire.
- **Is "north of B6" trustworthy?** Four units are placed north: one by the
  TEC register (grade B) and three by GSP group (grade C). No unit was placed
  by name, and `T_PINFB-1` stays unknown. The CMIS file armed no
  energy-limited unit that day.
- **Could any of them have covered the constraint?** Not on the published
  numbers: export hours of energy at R3p run from 0.00 to 1.19 hours
  against a constraint that ran all day. The table draws no further
  conclusion, and none of this is a counterfactual.

## 4. The conclusion

- **S1 (share): not determinable.** Unmatched units carry 45.0 % of the
  day's wind bid money, more than either scheme; the public identifier
  link covers 25.3 % (CfD) and the graded name link
  10.4 % (RO). The honest answer to "which scheme was paid" is
  that the public registers, read by declared rules, do not settle it.
- **S2 (price): holds.** RO-linked units were paid £78.68 per accepted MWh
  against £27.02 for CfD-linked units.
- **B1 (coverage): holds** on one deciding unit: no energy-limited unit north
  of B6 with a graded side had an R3p export energy bound covering the
  longest run of the constraint.

## 5. Expert corner

Settlement date 2026-09-08 (BST; period 1 starts 2026-09-07T23:00Z). EBOCF
indicative cashflows, `totalCashflow` as published, positive rows summed
for "paid", all rows for "signed". DISPTAV `Tagged` reconciled in both
directions within 0.1 % (deviations in `wind-by-scheme.json`). Register:
012's BMUNITS vintage of 2026-09-11. CfD mapping resource
`c16f141d-2db9-4160-ade1-d0d19d224dc9` (last modified 2026-09-14), portfolio
`fdaf09d2-8cff-4799-a5b0-1c59444e492b`; effective-date test applied per row.
RO report `RO_Accredited_Stations_16-09-2026_05-00.csv` from the RER public
reports dashboard (the dashboard page is pinned beside it). Name test:
lower-case alphanumerics with the declared generic tokens removed, station
tokens equal to or a superset of the unit's; capacity within 15 % of the
summed capacity of every bidding unit matching the same station; RO
capacity read as kW / 1000. MDO/MDB day streams for all units; levels taken
as the maximum of `levelFrom` and `levelTo` per record. Column bindings and
schema-report digests in `evidence/reading.json`.

## 6. Reproducibility

`run.py --phase compute` recomputes every figure from the pinned bytes
(paths and SHA-256 in the three manifests here and in 012's and 003's);
`render_results.py` regenerates this file. `scripts/check-rules` maps every
declared rule to a test.
