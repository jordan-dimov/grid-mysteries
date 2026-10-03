# 018 — The compensation pot after P511: results

Computed 2026-10-03 13:13 UTC under `DECLARATION.md` (`3ebd9015…`) and `AMENDMENT-1.md` (`d308b8c1…`, the byte-order mark), rule version `3ebd9015.d308b8c1`. Rendered from `evidence/results.json` by `run.py --phase render`; every figure below is that file's. Not published.

> Ofgem changed the rules on 24 August 2026 (P511) after £18.9m of mutualised
> supplier compensation had been paid in six months, most of it arising from one
> arrangement. Did the pot shrink afterwards, or did it just change hands?

## The verdicts

**C4 passes.** Read on each day's SF run, the 28 days of February 2026 total £5,717,881 paid and 65,020.3 MWh of VTP volume, +2.5 % and +1.9 % from Elexon's £5,576,308 and 63,827.48 MWh (P510 Initial Written Assessment slides), inside the declared ±15 %.

**H3 holds, so every H1 and H2 verdict is provisional** until POST has reached its R1 run: POST is read on SF, FEB on R3.

**H1, both baselines in one sentence.** POST's mean daily supplier compensation volume was 1.31 times FEB's (3,046.6 MWh against 2,324.5 MWh a day), and POST's mean daily paid was 0.56 times PRE's (£300,195 against £540,187 a day); each is killed below 0.50, so H1-FEB holds and H1-PRE holds (provisional until POST reaches R1, because H3 holds).

**H2-VTP holds (provisional until POST reaches R1, because H3 holds).** FEB's largest VTP party, `ALMAPERJ`, carried 79.1 % of FEB's pooled VTP volume and -0.0002 % of POST's (holds above 50 % in FEB and below 10 % in POST).

**H2-SUP holds (provisional until POST reaches R1, because H3 holds).** FEB's largest recipient, `GMTR`, carried 78.3 % of FEB's pooled paid and 0.1 % of POST's (holds above 50 % in FEB and below 25 % in POST).

**H3 holds.** Daily paid moved from its SF run to its latest run by more than 5 % on 2 of the four RESTATE days (holds on two or more):

| day | SF paid | latest run | latest paid | SF to latest |
|---|---|---|---|---|
| 2025-09-03 | £18,131 | R3 | £18,054 | 0.4 % |
| 2025-11-05 | £107,066 | R3 | £115,900 | 7.6 % |
| 2026-01-07 | £242,038 | R3 | £259,109 | 6.6 % |
| 2026-03-04 | £64,973 | R2 | £64,313 | 1.0 % |

| falsifier | fired |
|---|---|
| F1 H1-FEB killed | no |
| F2 H1-PRE killed | no |
| F3 H2-VTP fails | no |
| F4 H2-SUP fails | no |
| F5 C4 fails | no |

## Checks

**C5.** Every FEB, PRE and POST day had a run at or after SF; runs read: FEB R3; PRE R1, SF; POST SF; SERIES R1, R2, R3, SF; C4 SF; C4-LATEST R3. Days with no qualifying run listed: none.

**C1 to C3, C6, C7.** 5 file(s) failed a decisive check and are excluded (the day counts as missing in a window; a RESTATE day is read on its other runs):

| file | read in | failed | off-prefix cells (position:prefix) |
|---|---|---|---|
| `S0142_20250924_R3_20260429080153.gz` | SERIES | C2; C7 | `22:C__` 11, `25:C__` 11 |
| `S0142_20251001_R3_20260507080204.gz` | SERIES | C2; C7 | `22:C__` 21, `25:C__` 21 |
| `S0142_20251008_R3_20260514080245.gz` | SERIES | C2; C7 | `22:C__` 21, `25:C__` 21 |
| `S0142_20260107_R2_20260501090158.gz` | RESTATE | C2; C7 | `22:C__` 20, `25:C__` 20 |
| `S0142_20260304_R1_20260424100159.gz` | RESTATE | C2; C7 | `22:C__` 27, `25:C__` 27 |

**Amendment 1.** 8 files began with a UTF-8 byte-order mark and were read with it removed: `S0142_20260219_R3_20260924153711.gz`, `S0142_20260220_R3_20260925081324.gz`, `S0142_20260221_R3_20260925080832.gz`, `S0142_20260222_R3_20260925090033.gz`, `S0142_20260603_R2_20260924163249.gz`, `S0142_20260805_R1_20260924152439.gz`, `S0142_20260901_SF_20260924075713.gz`, `S0142_20260902_SF_20260925075754.gz`.

Beside C4, the same 28 days on their latest run (R3): £5,739,131 paid (+2.9 %) and 65,270.6 MWh (+2.3 %), no band.

## Context (no threshold applies)

**Every measure against both baselines** (POST mean daily ÷ baseline mean daily):

| measure | against FEB | against PRE |
|---|---|---|
| paid | 1.48 | 0.56 |
| supplier compensation volume | 1.31 | 0.56 |
| VTP volume | 1.42 | 0.59 |
| charged | 1.61 | 0.59 |

Deciding: H1-FEB on supplier compensation volume, H1-PRE on paid.

**H2's computation against PRE**: `ALMAPERJ` 42.1 % of PRE's VTP volume, -0.0002 % of POST's; `GMTR` 42.6 % of PRE's paid, 0.1 % of POST's.

**`ALMAPERJ` in PRE** (PRE follows Ofgem's decision of 10 August): 42.1 % of PRE's VTP volume; by day 10/08 1,719, 11/08 2,171, 12/08 2,113, 13/08 2,192, 14/08 197, 15/08 2,383, 16/08 2,701, 17/08 3,539, 18/08 1,080, 19/08 3,512, 20/08 3,627, 21/08 3,606, 22/08 2,257, 23/08 1,558 MWh.

**Charged against paid**, each window's days read (two published figures and their difference):

| window | days | paid | charged | charged − paid |
|---|---|---|---|---|
| FEB | 27 | £5,473,468 | £5,420,682 | −£52,786 (-1.0 %) |
| PRE | 14 | £7,562,619 | £7,648,659 | £86,040 (+1.1 %) |
| POST | 13 | £3,902,540 | £4,199,456 | £296,916 (+7.6 %) |
| SERIES | 48 | £9,588,555 | £9,447,700 | −£140,855 (-1.5 %) |

**Largest parties per window**, by share of the window's pooled total:

*FEB (February 2026 less 17/02)*

| | VTP volume | paid | charged |
|---|---|---|---|
| 1 | `ALMAPERJ` 79.1 % | `GMTR` 78.3 % | `LENCO` (EDF Energy Customers Limited) 17.0 % |
| 2 | `AXLEENER` (Axle Energy Limited) 18.1 % | `MERCURY` (Octopus Energy Limited) 11.3 % | `MERCURY` (Octopus Energy Limited) 12.9 % |
| 3 | `LONDELEC` (EDF Energy Limited) 2.4 % | `NITTWO01` (E.ON Next Energy Ltd) 5.2 % | `BRITGAS` (British Gas Trading Ltd) 12.5 % |
| 4 | `ZENOBER1` 0.4 % | `BRITGAS` (British Gas Trading Ltd) 2.1 % | `NITTWO01` (E.ON Next Energy Ltd) 7.7 % |
| 5 | `FLEXTRCY` (Flexitricity Limited) 0.1 % | `COULOMB` 0.8 % | `NPOWER02` (Npower Commercial Gas Limited) 5.4 % |

*PRE (10 to 23 August 2026)*

| | VTP volume | paid | charged |
|---|---|---|---|
| 1 | `ALMAPERJ` 42.1 % | `GMTR` 42.6 % | `LENCO` (EDF Energy Customers Limited) 17.0 % |
| 2 | `AXLEENER` (Axle Energy Limited) 40.0 % | `MERCURY` (Octopus Energy Limited) 31.5 % | `MERCURY` (Octopus Energy Limited) 11.9 % |
| 3 | `LONDELEC` (EDF Energy Limited) 10.8 % | `NITTWO01` (E.ON Next Energy Ltd) 10.0 % | `BRITGAS` (British Gas Trading Ltd) 11.4 % |
| 4 | `REFLEXI` 3.9 % | `BRITGAS` (British Gas Trading Ltd) 8.9 % | `NITTWO01` (E.ON Next Energy Ltd) 6.7 % |
| 5 | `POWONTEC` (Joulen) 1.4 % | `LENCO` (EDF Energy Customers Limited) 3.8 % | `NPOWER02` (Npower Commercial Gas Limited) 5.9 % |

*POST (24 August to 6 September 2026 less 28/08)*

| | VTP volume | paid | charged |
|---|---|---|---|
| 1 | `AXLEENER` (Axle Energy Limited) 51.1 % | `MERCURY` (Octopus Energy Limited) 52.6 % | `LENCO` (EDF Energy Customers Limited) 16.9 % |
| 2 | `LONDELEC` (EDF Energy Limited) 32.9 % | `NITTWO01` (E.ON Next Energy Ltd) 17.7 % | `MERCURY` (Octopus Energy Limited) 12.4 % |
| 3 | `REFLEXI` 9.8 % | `BRITGAS` (British Gas Trading Ltd) 16.0 % | `BRITGAS` (British Gas Trading Ltd) 11.8 % |
| 4 | `POWONTEC` (Joulen) 3.5 % | `LENCO` (EDF Energy Customers Limited) 14.2 % | `NITTWO01` (E.ON Next Energy Ltd) 7.1 % |
| 5 | `ZENOBER1` 1.8 % | `SPSUP01` (ScottishPower Energy Retail) 2.0 % | `NPOWER02` (Npower Commercial Gas Limited) 5.7 % |

*SERIES (Wednesdays, 3 September 2025 to 19 August 2026)*

| | VTP volume | paid | charged |
|---|---|---|---|
| 1 | `ALMAPERJ` 58.2 % | `GMTR` 57.3 % | `LENCO` (EDF Energy Customers Limited) 17.2 % |
| 2 | `AXLEENER` (Axle Energy Limited) 34.1 % | `MERCURY` (Octopus Energy Limited) 23.2 % | `BRITGAS` (British Gas Trading Ltd) 12.0 % |
| 3 | `LONDELEC` (EDF Energy Limited) 4.3 % | `NITTWO01` (E.ON Next Energy Ltd) 8.5 % | `MERCURY` (Octopus Energy Limited) 11.8 % |
| 4 | `REFLEXI` 1.8 % | `BRITGAS` (British Gas Trading Ltd) 5.5 % | `NITTWO01` (E.ON Next Energy Ltd) 6.9 % |
| 5 | `ZENOBER1` 0.9 % | `LENCO` (EDF Energy Customers Limited) 1.4 % | `NPOWER02` (Npower Commercial Gas Limited) 5.8 % |

**SERIES by month** (mean per Wednesday read; excluded Wednesdays are not in the mean):

| month | Wednesdays read | paid | charged | VTP volume | supplier compensation volume |
|---|---|---|---|---|---|
| 2025-09 | 3 | £25,359 | £25,359 | 278.9 MWh | 278.9 MWh |
| 2025-10 | 3 | £58,018 | £58,018 | 648.5 MWh | 648.5 MWh |
| 2025-11 | 4 | £93,307 | £88,732 | 991.8 MWh | 1,042.9 MWh |
| 2025-12 | 5 | £118,899 | £106,387 | 1,189.1 MWh | 1,328.9 MWh |
| 2026-01 | 4 | £207,601 | £210,037 | 2,408.5 MWh | 2,380.5 MWh |
| 2026-02 | 4 | £248,610 | £250,075 | 2,867.5 MWh | 2,850.7 MWh |
| 2026-03 | 4 | £121,155 | £72,508 | 831.4 MWh | 1,389.2 MWh |
| 2026-04 | 5 | £96,000 | £91,706 | 1,114.9 MWh | 1,167.0 MWh |
| 2026-05 | 4 | £186,840 | £190,149 | 2,311.6 MWh | 2,271.3 MWh |
| 2026-06 | 4 | £221,784 | £238,167 | 2,895.3 MWh | 2,696.0 MWh |
| 2026-07 | 5 | £483,215 | £486,573 | 4,938.4 MWh | 4,904.1 MWh |
| 2026-08 | 3 | £510,219 | £525,191 | 5,330.3 MWh | 5,178.2 MWh |

## Names (R6)

Names are the BM unit register's (Elexon Insights `reference/bmunits/all`, pinned at acquisition, data/raw/elexon/018/bmunits-2026-10-03.json (SHA-256 3c40f1f1c30d0fe2…)), mapping a lead party id to its name. Ids printed without a name are not carried by that register. Elexon's P510 slides name "SEFE Energy Limited" as the largest recipient and "Almape Holdings Limited" as the largest VTP for September 2025 to February 2026. The register does not carry `GMTR` or `ALMAPERJ`, so which id either of Elexon's names belongs to is not asserted here.

## What this does not claim

That `ALMAPERJ` and `GMTR` (or Almape Holdings and SEFE Energy) were one configuration; that anyone broke a rule; that P511 caused any change (the windows compare levels and shares before and after a date, while the market grew, half-hourly settlement migration went on and the SCRP moves by quarter); savings, losses or "should have"; that thirteen days of POST are typical of what follows; that charged minus paid is an error, a leak or anyone's money.

## Record

- register: `data/raw/elexon/018/bmunits-2026-10-03.json (SHA-256 3c40f1f1c30d0fe2…)`
- results.json SHA-256: `cc0fdf6fa56842292530d6c40a1021adedbb66f323292077bafce07133f72f83`
- days.ndjson SHA-256: `1ee8f5f2f9cfabd82eb88e4903c1dd3840a94f8eb444f35021831ba0d58a5217`
- run-index-acquired.json SHA-256: `22ac2257d0927b314d1b715b5aa86c5a3bb053f94e7e522b723c5c03a897ad55`
- format-check.json SHA-256: `ca7070da5e7e079495a728d26a596c6b857d558146ae66c287402ad7f4006905`
- s0142-manifest.json SHA-256: `fecd8b23ece69478e3b0d2f5f053a70bdb7b67d85cee3afc9a1f52b5084e036d`
- rule tests: `evidence/rule-sources.json`
