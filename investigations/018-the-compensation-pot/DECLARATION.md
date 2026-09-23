# 018 — The compensation pot after P511: declaration

**Written** 2026-09-23, after the schema pass below, and amended the same
day, before the freeze, at the sponsor's direction (C4 on SF runs; H1
decided on volume against February and on cash against 10 to 23 August;
PRE declared a conservative baseline). No S0142 file for a settlement
date in any window named here has been requested from this repository. Frozen by `scripts/freeze`, which witnesses these bytes
with OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert and
commits the file with its proofs. Results go in `RESULTS.md` and amendments,
if any, in `AMENDMENTS.md`, dated. Acquisition waits for the human seal
(see *Acquisition gate*).

## The mystery

> Ofgem changed the rules on 24 August 2026 (P511) after £18.9m of
> mutualised supplier compensation had been paid in six months, most of it
> arising from one arrangement. Did the pot shrink afterwards, or did it
> just change hands?

## Background, as the sources state it

Under BSC modification P415 (live 7 November 2024) a Virtual Trading Party
(VTP) sells the gap between a centrally computed baseline and metered
consumption at its customers' sites. The supplier whose position that moves
is compensated at the Supplier Compensation Reference Price (SCRP), from a
pot every supplier funds in proportion to its Final Demand (BSC Section T
§4.3C and §4.11; SCRP Methodology Document v2.0).

Elexon's P510 Initial Written Assessment slides (`p510-iwa-slides.pdf`,
SHA-256 `d044098a1ff8989fdbf60da2a9ba9ed38229e85b0fcb2ead4b26254297410385`,
from `https://www.elexon.co.uk/bsc/documents/change/modifications/p501-p550/p510-iwa-slides/`,
downloaded 2026-09-23 in etrmbiz and matched to that URL by digest; all
documents are listed in `evidence/sources-manifest.json`) give two tables
for 1 September 2025 to 28 February 2026:

- **Mutualised Supplier Compensation Cashflow by recipient**, "Source:
  Elexon MR1A (Party Daily Settlement Data)": £18,898,688 in total, of
  which £5,576,308 in February 2026; SEFE Energy Limited £14,324,207.
- **Secondary BM Unit Compensation Volume by VTP**, "Source: Elexon
  SAA-I014 Reports": 209,471.24 MWh in total, of which 63,827.48 MWh in
  February 2026; Almape Holdings Limited 163,259.05 MWh. The slide text
  says "circa 2.1m MWh" where its table sums to 209,471 MWh; £18.9m over
  209k MWh is about £90/MWh, which is the SCRP's order, so the table is the
  figure used here and the text is taken as a slip.

P511 (Ofgem decision published 10 August 2026, implemented 24 August 2026)
restricted VTP eligibility by a metering point's largest half-hourly export.
Its proposal form attributes "approx. 75%" of the compensation to "a single
supplier + VTP + generator configuration" without naming it.

## Prior exposure (recorded, not hidden)

1. **Two S0142 files were read in full** before this declaration: settlement
   date 2026-02-17, run R3 (`S0142_20260217_R3_20260922224432.gz`, SHA-256
   `8a06ca4a…c9a34ca`) and settlement date 2026-08-28, run SF
   (`S0142_20260828_SF_20260922223519.gz`, SHA-256 `fd7dd099…b738b8f`),
   fetched 2026-09-23 about 11:23 UTC from etrmbiz and copied here to
   `data/raw/elexon/018/schema-pass/`. Figures seen from them, keyed by the
   file's BSC Party Id:

   | | 2026-02-17 R3 | 2026-08-28 SF |
   |---|---|---|
   | Secondary BM Unit Compensation Volume | 3,113 MWh | 3,119 MWh |
   | largest VTP parties | `ALMAPERJ` 83.0 %, `AXLEENER` 14.5 %, `LONDELEC` 1.8 % | `AXLEENER` 63.3 %, `LONDELEC` 33.1 %, `ZENOBER1` 2.1 % |
   | Supplier Compensation Cashflow, paid (BP7) | £265,663.10 | £277,986.39 |
   | largest recipients | `GMTR` 84.9 %, `MERCURY` 10.0 %, `NITTWO01` 4.0 % | `MERCURY` 56.1 %, `NITTWO01` 16.9 %, `BRITGAS` 15.6 %, `LENCO` 13.2 % |
   | Virtual Lead Party Compensation Cashflow, charged (APC) | £271,454.63 | £307,312.92 |
   | Supplier Sourcing Cost (SPI) | 87.21 every period | 98.53 every period |

   **These two days taught the hypotheses below, and neither is in any test
   window.** 2026-02-17 is read once more, only for check C4 (a
   reproduction of Elexon's February total), and never for H1 to H3.
2. The handover from etrmbiz (`notes/2026-09-23-p415-handover-to-grid-mysteries.md`
   and `notes/2026-09-23-p415-virtual-trading-parties.md` in that
   repository) keyed parties by the four letters inside the unit id and
   reported `BGAS`/`TILL` 16.2 % and `EDFE` 13.1 % on 2026-08-28; keyed by
   the file's own party header, the same day reads `BRITGAS` 15.6 % and
   `LENCO` 13.2 %. The difference is the keying rule, which R1 fixes.
3. Elexon's monthly figures for September 2025 to February 2026 (above)
   are known. January and February 2026 paid £5,485,199 and £5,576,308.
4. The charged side exceeded the paid side on both seen days (by about 2 %
   and 10 %). This was noticed in the schema pass; it is reported below as
   context and is **not** a hypothesis of this declaration.
5. The reading code of this investigation
   (`src/grid_mysteries/investigations/p415_compensation.py`) was run on
   the two files while it was written, to check R1 to R3 and C1 to C7
   against them; every check passed on both, and the figures in item 1 are
   its output.
6. Nothing else from S0142 or from any Elexon settlement report has been
   read for any date. No P114 listing has been requested from this
   repository.

## The schema pass this is written against

`archives/elexon-s0142/schema-report.json`, SHA-256
`2a2f4e9d3e892d16d1dd40181d35abcd33ca6c37fab1fbb7ed1440df04808163`,
regenerated by `scripts/schema-report s0142 elexon-s0142 <the two files>`
and committed at `435a367`, before this declaration. Its scope is those two files and
nothing else. It is cited for these facts:

- both files print flow version `S0142013` in their `AAA` record, and every
  `BP7` record arrives with 25 data fields after the record id;
- every `BP7` sits under a `BPH` (BSC Party Header) and an `SP7`
  (Settlement Period Header), after all 48 `SPI` records;
- the non-blank cells at `BP7` positions 22 and 25 are all on units whose
  id begins `2__`, and at position 23 all on units beginning `V__`;
- `SPI` position 53 is a single value on every period of each file.

The field names come from Elexon's **NETA IDD Part 2 spreadsheet v43.0**
(`NETA-IDD-Part-2_spreadsheet_v43.0.xls`, SHA-256
`814c506592f4418bf981693969c7402db45020fedfb8b47573d431eacb23a117`,
fetched 2026-09-23T10:37:46Z from
`https://assets.elexon.co.uk/wp-content/uploads/sites/11/2026/06/23161551/NETA-IDD-Part-2_spreadsheet_v43.0.xls`),
sheet `SO`, flow S0142 "SAA-I014: Settlement Report: sub-flow 2". That
spreadsheet defines flow version 014, whose `BP7` adds two P444 fields
(positions 26 and 27) after the 25 the files carry, and whose `APC` adds
one P444 field after position 12. Positions 1 to 25 of `BP7` and 1 to 12 of
`APC` are read with v014's names; nothing after them is read.

## Reading rules

**R1 — the party is the file's.** A `BP7` value belongs to the BSC Party Id
at position 8 of the `BPH` record above it (IDD item N0045). The four
letters inside a unit id are never used as a key. A `BP7` with no `BPH` and
`SP7` above it is an orphan: counted, never summed.

**R2 — the fields.** `BP7` position 1 BM Unit Id (N0034); 22 Period BM Unit
Supplier Compensation Volume (N0668); 23 Period Secondary BM Unit
Compensation Volume (N0669); 25 Period Supplier Compensation Cashflow
(N0656). `APC` position 11 Daily Virtual Lead Party Compensation Cashflow
(N0653) and 12 Daily Supplier Compensation Cashflow (N0654). `SPI` position
1 Settlement Period and 53 Supplier Sourcing Cost (N0659). Values are read
as `Decimal` exactly as printed. A blank is absent; a printed zero is a
value.

**R3 — where each quantity may sit.** Positions 22 and 25 are summed only
on units whose id begins `2__`, and position 23 only on units beginning
`V__`. A non-blank value anywhere else is an off-prefix cell, counted and
reported, never summed, and fails check C2.

**R4 — the run.** Runs are ordered II < SF < R1 < R2 < R3 < RF < DF. For
every window below except C4 a day is read on its **latest run at or after
SF** published at acquisition (C4 reads each day's SF run); two files for the same run resolve to the later
publication stamp in the file name. II is never used outside H3. A run code
outside that list is reported and never selected.

**R5 — the four measures.** For a day and a party:
- **paid** = Σ `BP7`[25], the compensation a supplier received;
- **VTP volume** = Σ `BP7`[23], the volume a VTP's trading generated;
- **charged** = `APC`[11], a supplier's contribution to the pot (a debit
  when positive, BSC Section T §1.2.3);
- **supplier compensation volume** = Σ `BP7`[22], the volume behind paid
  (paid is this volume × the period's Supplier Sourcing Cost, check C6).

The day's total of each is the sum over parties. Paid is what Elexon's
£18.9m counts ("Mutualised Supplier Compensation Cashflow", MR1A). H1's
deciding measure depends on its baseline and is fixed under H1; every
measure is reported for both baselines.

**R6 — names.** A party is printed as its BSC Party Id. A name is added
only where the BM unit register pinned at acquisition (Elexon Insights
`reference/bmunits/all`) maps that id to a lead party name, and is labelled
as that register's. Where the register does not carry the id, the id stands
alone. Elexon's P510 slides name "SEFE Energy Limited" and "Almape Holdings
Limited"; RESULTS may quote those names as Elexon's, beside the ids, and
never asserts which id they belong to unless R6's register does.

## Windows (settlement dates, fixed now)

- **FEB**: 2026-02-01 to 2026-02-28, **excluding 2026-02-17**. 27 days.
  Elexon's own reference month, and the last month in its tables.
- **PRE**: 2026-08-10 to 2026-08-23. 14 days, before implementation and in
  the same SCRP quarter as POST. **PRE follows Ofgem's decision of
  2026-08-10**, so behaviour in it may already have responded to P511: a
  party that expected to lose eligibility could have stopped before
  24 August. PRE is therefore a **conservative baseline**: if the pot
  had already shrunk in PRE, H1-PRE is biased towards holding, and a
  POST-to-PRE ratio near one says less than a POST-to-FEB ratio near one.
  `ALMAPERJ`'s VTP volume in PRE, per day and as a share of PRE, is
  reported as context so a reader can see whether that happened.
- **POST**: 2026-08-24 to 2026-09-06, **excluding 2026-08-28**. 13 days.
- **SERIES**: every Wednesday from 2025-09-03 to 2026-08-19, 51 days.
  Context only; no threshold applies to it.
- **RESTATE**: 2025-09-03, 2025-11-05, 2026-01-07 and 2026-03-04, each on
  **every run** published at acquisition, II included.
- **C4**: all 28 days of February 2026, 2026-02-17 included, only for the
  reproduction check, each read on its **SF run** (not the latest run), with
  the latest run at or after SF read beside it.

No window contains a clock-change day.

## Hypotheses and the thresholds that decide them

**H1 — the pot changed hands, not size.** A mean daily measure over POST,
divided by the same measure over a baseline, decided twice:
- **H1-FEB** against FEB, decided on **supplier compensation volume
  (MWh)**. The SCRP changes with the price cap quarter (the Supplier
  Sourcing Cost read 87.21 on the February day and 98.53 on the August day
  seen), so a cash ratio against February would mix volume and price.
- **H1-PRE** against PRE, decided on **paid (£)**, because PRE and POST
  sit in the same SCRP quarter.
- Each is **killed** if its ratio is **below 0.50**, and holds otherwise.
- For both baselines, paid, supplier compensation volume, VTP volume and
  charged are all reported as ratios, and only the measure named above
  decides.

Why 0.50: if P511 removed the largest arrangement and nothing replaced it,
the ratio would sit near a quarter (Elexon's February tables put about
four-fifths of the volume on one VTP); if the volume was fully replaced it
would sit near one. Half is between the two stories, set where the answer
would change, not where the seen days put it.

The volume behind paid (supplier compensation volume) and the volume VTPs
generated (VTP volume) are not equal: charged exceeded paid by about 2 % and
10 % on the two seen days. H1-FEB is decided on the paid side's volume
because H1 is about the pot paid out; VTP volume is reported beside it.

**H2 — concentration changed hands.** Each side is decided on FEB against
POST. The party is chosen on FEB alone, and its POST share is then read and
never re-chosen.
- **H2-VTP** holds if FEB's largest VTP party carries **more than 50 %** of
  FEB's pooled VTP volume and **less than 10 %** of POST's.
- **H2-SUP** holds if FEB's largest recipient carries **more than 50 %** of
  FEB's pooled paid and **less than 25 %** of POST's.

POST's own largest parties and their shares, and the same computation
against PRE, are reported with no threshold.

**H3 — the run matters.** For each RESTATE day, the movement of daily paid
from its SF run to its latest run, as a fraction of the latest. H3 holds if
that movement exceeds **5 %** on **at least two of the four days**. The
II-to-latest movement and the same figures for VTP volume are reported with
no threshold. If H3 holds, every H1 and H2 verdict is published as
**provisional** until POST has reached R1, because POST is read on SF while
FEB is read on a later run.

## Checks the run must pass, or it stops

- **C1** Each file's `SRH` settlement date and run equal those in its
  name; its `AAA` prints `S0142013`; every `BP7` has 25 data fields.
- **C2** No off-prefix P415 cell and no orphan `BP7` (R1, R3).
- **C3** 48 `SPI` periods, and every `BP7` period among them.
- **C4** Over all 28 February days, each on its **SF run**, total paid is
  within **±15 %** of Elexon's £5,576,308 and total VTP volume within
  **±15 %** of 63,827.48 MWh. SF is the run Elexon's analysis for the P510
  assessment (early 2026) could have used; the one February day already
  seen, on R3, sits about 33 % (paid) and 37 % (VTP volume) above Elexon's
  February daily average, so a comparison on later runs could fail for
  reasons of restatement or day-to-day spread rather than reading. The same
  totals on each day's latest run are reported beside C4, with no band. If
  a February day has no SF run listed, C4 fails. Outside the band, the
  reading is suspect and **no H verdict is published** until the difference
  is explained in `AMENDMENTS.md`.
- **C5** Every day in FEB, PRE and POST has a run at or after SF, and every
  selected run is in R4's list. **The acquisition refuses to fetch any
  window file until the P114 listings show an SF run for every POST day.**
- **C6** On every file, paid equals Σ over `BP7` rows of position 22 ×
  that period's Supplier Sourcing Cost, within £1.00 per paying party. This
  tests the binding of R2, not a hypothesis.
- **C7** On every file, paid per party equals `APC`[12] for that party
  within £1.00, and in total within £1.00 per paying party.

A file that fails C1, C2, C3, C6 or C7 is excluded, listed with the failed
check, and its day counts as missing. If more than two days of FEB, PRE or
POST are missing, the hypotheses using that window are **not decided**.

## Falsifiers, declared in advance

- **F1** H1-FEB killed: POST's mean daily supplier compensation volume is
  below half of February's.
- **F2** H1-PRE killed: POST's mean daily paid is below half of the
  fortnight before implementation.
- **F3** H2-VTP fails: February's largest VTP party still carries 10 % or
  more of POST's volume, or February was not concentrated.
- **F4** H2-SUP fails: February's largest recipient still receives 25 % or
  more of POST's paid, or February was not concentrated.
- **F5** C4 fails: the reading does not reproduce Elexon's February month
  on SF runs, and that is published before anything else.

If F1 and F2 disagree, both are published in the same sentence and neither
headline is used alone.

## What this never claims

- **That `ALMAPERJ` and `GMTR`, or Almape Holdings and SEFE Energy, were
  one configuration.** No source read shows it. Both concentrations may be
  reported side by side; the link is never asserted or implied.
- **That anyone broke a rule.** The activity was within the rules as they
  stood; P511 changed the rules.
- **That P511 caused any change.** H1 and H2 compare levels and shares in
  windows before and after a date. The market was also growing (Elexon's
  monthly figures rose every month), half-hourly settlement migration was
  under way, and the SCRP moves by quarter. A difference is reported as a
  difference.
- **Savings, losses or "should have".** No counterfactual pot is computed.
- **That POST is typical of what follows.** It is thirteen days.
- **That charged minus paid is an error, a leak or anyone's money.** It is
  reported as two published figures and their difference.

## Outputs

- `evidence/run-index.json` — every S0142 file listed by P114 from
  2025-09-03 to the acquisition date: settlement date, run, file name,
  listed publication time.
- `evidence/days.ndjson` — one line per file read: its identity and digest,
  the check results, and paid, VTP volume, charged and supplier
  compensation volume by party. Append-only.
- `evidence/results.json` — C1 to C7, H1 to H3 with their inputs, the
  falsifier verdicts, and this declaration's digest.
- `RESULTS.md` — the verdicts, then the context: the SERIES by month, the
  largest parties per window, charged against paid, names under R6.
- `evidence/rule-sources.json` — the test behind every rule above.

## Acquisition gate

Human seal, then, in this order, from `run.py`:

1. **index** — the P114 S0142 listing for every publication date from
   2025-09-03 to the day of the run, each pinned under
   `data/raw/elexon/018/list/` and journalled. The run index is built
   offline from the pinned listings.
2. **acquire** — refuses under C5 until every POST day has an SF run
   listed. Then the BM unit register (one fresh vintage), and every file
   the windows select, pinned under `data/raw/elexon/018/s0142/` and
   journalled with SHA-256 before any value is read. C4's SF runs for all
   28 February days, 2026-02-17 included, are fetched with them and used
   only for C4. 2026-02-17's latest run is read for the reporting beside C4.
3. **compute** — offline, from pinned bytes only.

`run.py` refuses `index` and `acquire` unless invoked with
`--seal <prefix of this file's SHA-256>`, so the seal is on the record in
the command that acquired the data. The Portal key is read from the
environment at request time and never journalled, printed or committed.
Raw S0142 files stay under `data/raw/` and are not committed or
republished; the P114 licence permits derived analysis, not
redistribution.

## Out of scope

Who funds the pot beyond the charged-by-party table; baselining; P510's
cost-benefit scenarios; MR1A/MR1B; any period after 2026-09-06 except as a
later declaration's window; the commercial follow-through, which stays in
etrmbiz.
