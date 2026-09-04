# 011 — results: the rule the press reported does not exist; the rule Ofgem approved catches no contracted battery BMU; the 2027 duty is a non-BMU story

**Run**: 2026-09-04, sealed by the sponsor on digest `99498205` (commit
`c28454b`). Documents pinned 14:03 UTC; Amendment 1 (`AMENDMENTS.md`)
written from them **before** the Elexon register (14:05), the instrument
gate, the EAC results (14:07) or any physical series (14:08–14:17) was
requested; 962 artefacts journalled with SHA-256 (`evidence/manifest.json`).
Every number below comes from `evidence/results.json`,
`evidence/population.json`, `evidence/instrument-gate.json` or the pinned
document named beside it. Runner `run.py`; screen and tests
`src/grid_mysteries/investigations/eligibility_screen.py`,
`tests/test_eligibility_screen.py`. **Not published; publication waits for
the sponsor's second seal.**

Every £ figure is a **gross availability payment at the auction clearing
price** (executed MW × £/MW/h × 0.5 h per settlement period, Schedule 3's
V × P × 0.5 with K and F at one), never a realised receipt, a saving or a
loss. Clearing prices can be negative and 37 of the 153 units carry a
negative window total; the totals net them.

## 1. The mystery

Trade press reported that from 31 July 2026 a battery that fails to
submit a valid Final Physical Notification (FPN) for a settlement period
is deemed unavailable for Dynamic Containment, Moderation and Regulation
in that period, and that an 80 % compliance threshold over a rolling
28-day window becomes a condition of participation. If so, a piece of
operational bookkeeping had become a revenue prerequisite, and nobody had
said which units it catches. The question: which battery BMUs earning
response revenue would have been deemed unavailable, for how many periods,
and what does that do to the revenue an investor is underwriting?

## 2. The evidence

**The rule, from the pinned text.** NESO's *Response Services Service
Terms* v6 (effective 31 July 2026, published 23 July 2026), paragraph
5.10:

> Where, in relation to a Response Unit which is BM Participating, the
> Service Provider sets its FPN flag to FALSE, then for the purposes of
> paragraph 7 until such flag is reset to TRUE the Response Unit shall be
> deemed unavailable to deliver all Auction Products.

Ofgem's decision letter (Proposal 3): "a clarification that when a BMU
sets its FPN flag to FALSE it will be deemed unavailable […] to ensure
that BMU's are submitting the correct data and that the correct processes
are followed to de-register / re-register a BMU where providers wish to
switch between BMU and non-BMU". The approval "applies only to proposals
3, 9 and 10, and is effective by 31 July 2026".

The 80 % threshold is Proposal 2, approved **effective 1 January 2027**:
"a certain level of compliance (80%) over an Assessment Period" of "up to
28 EFA days immediately prior to an auction", and it "mainly affects
non-Balancing Mechanism Units". The per-period and per-EFA-block deemed
unavailability (Tiers 0 and 1), the 28-day suspension (Tier 2) and unit
suspension (Proposal 8) were **rejected**.

**The instruments** (`evidence/instrument-gate.json`, schema and counts
only, probe day 2026-09-01):

| instrument | state | what settled it |
|---|---|---|
| Elexon PN, MELS, MILS | eligible now | silent units are absent from the series, not zero-filled (PN: 2,466 distinct units against 3,062 registered); no submission timestamp in PN, so timeliness is unobservable; the MELS/MILS stream carries `notificationTime`, PN does not |
| Elexon BOALF | eligible now (context) | fields present |
| NESO EAC results by unit | eligible now | all eight declared fields present; 1,184,476 rows; naive timestamps read as UTC on the evidence of 64,927 EFA-boundary hits against 24,380 for the local reading over 236,575 window rows |
| Elexon register | eligible now | 3,062 units; `fpnFlag` TRUE 2,815, FALSE 155, null 2; no lead-party difference against the 001 vintage |
| NESO compliance / performance series by BMU (G5) | **no viable public instrument** | five searches; the only per-unit candidates are FFR post-tender reports from 2020–2022 |

**The population** (`evidence/population.json`): 181 EAC units held at
least one accepted DC, DM or DR position in the post-rule window; 177 are
`technologyType == Batteries` in the EAC results. Of those, **153 map to
an Elexon BMU** and form the screened population (149 EAC batteries plus
4 units the in-merit files call `BATTERY` and the EAC calls something
else; 8 more disagree the other way and are included). **28 do not map**
to any registered BMU: they are non-BMU response providers (ids such as
`GSET-01`…`08`, `HAB-23`, `EDFE-01`, `HAB12-FFR`), invisible in Elexon by
construction, and they held about **£101,214** of gross availability in
the post-rule window.

**Windows.** Post-rule 2026-08-04..31 (28 days, after the effective
date); counterfactual 2026-07-03..30 (28 days before it). Overlaps with
001, 002 and BESS Study 001 are as declared.

## 3. Explanations tested

| test | post-rule 2026-08-04..31 | counterfactual 2026-07-03..30 |
|---|---|---|
| units holding a response position (BMU batteries) | 153 | 148 |
| gross availability held | £8,967,517.48 | £8,764,749.25 |
| **primary — register flag FALSE (para 5.10)** | **0 units; £0.00** | **0 units; £0.00** |
| sensitivity — no PN record in a held period (V0 present / V1 covering) | 1 unit; 142 periods; £13,891.74 (0.15 %) | 1 unit; 50 periods; £3,016.32 (0.03 %) |
| sensitivity — block forfeit (rejected Tier 1) | £13,891.74 | £3,016.32 |
| sensitivity — non-zero FPN required (V2) | 153 units; 56,447 periods; £3,338,935.60 | 148 units; 52,197 periods; £3,328,369.33 |

- **F1 fired (different trigger).** The pinned rule is a standing
  registration flag, not a per-period validity test. Nothing in the
  pinned terms deems a unit unavailable for a period in which it holds a
  position but submits no or an invalid FPN, unless its flag is FALSE.
- **F3 fired (population complies).** Every one of the 153 contracted
  battery BMUs carries `fpnFlag = TRUE` at the register pin (14:05 UTC,
  2026-09-04). The register has no history, so this is "TRUE at the
  pin", not "TRUE throughout the window"; but nothing at the pin is
  deemed unavailable, and the rule cannot have repriced any of the £8.97m
  held. The 155 FALSE-flag units in the register include **no** battery:
  the only one with any EAC position is `E_BTNHL-1` (Conrad Energy gas
  reciprocating engine, Slow Reserve), outside the Response terms.
- **F2 did not fire.** PN silence is distinguishable from a zero PN, and
  the screen ran. The per-period result is one unit, `E_GRFLB-1` (Conrad
  Energy (Trading) Ltd, embedded, 40 MW, flag TRUE), holding DCH and DCL
  positions on 2026-08-04..06 (and 07-29..30 in the counterfactual) with
  **no PN, MEL or MIL record at all** in the published series for any of
  its 142 held periods, and no acceptances. That is the whole of the
  per-period exposure, 0.15 % of the population's revenue. Under the
  pinned rule it is not deemed unavailable. Why a BM-participating
  response unit publishes no physical data over its contracted periods,
  and why its positions stop after 6 August, is **publicly unexplained
  from the state reconstructed here**; it is one unit and one week, and
  no pattern is claimed.
- **V2 is not a rule.** A contracted battery's normal FPN is zero: 56,447
  of the population's held periods carry a zero-level FPN. A reading that
  required a non-zero FPN would deem the whole market unavailable, which
  is why it was declared as sensitivity only and is reported only to
  close it.
- **G5 (80 % compliance).** Not in force in the window; its population is
  mainly non-BMU; no public per-BMU compliance series exists. Half of the
  reported rule is unobservable from public data, as the declaration
  anticipated. The 28 unmapped units are the units it will bite.
- **Behaviour did not change when the rule bit.** The counterfactual and
  the test windows differ by five units and £0.2m of positions; the
  single silent unit is the same in both.

## 4. The conclusion

Of 153 battery BMUs holding Dynamic Containment, Moderation or Regulation
positions between 2026-08-04 and 2026-08-31, **none** would have been
deemed unavailable under the eligibility condition Ofgem approved for 31
July 2026, because that condition is a registration FPN flag and every
one of them has it set. The condition the press described, per-period
deemed unavailability for a missing FPN, was proposed as Tier 0 of a
performance regime and **rejected**. The 80 %-over-28-days threshold is
approved for 1 January 2027, is a data-submission duty, and falls mainly
on non-BMU providers: about 28 battery units holding about £101k of
gross availability per 28 days, roughly 1.1 % of what BMU batteries hold.
The rule in force reprices nothing in the BMU battery fleet; the fact
worth publishing is the correction.

Falsifiers F1 and F3 fired; F2 did not; F4 is moot because nothing is at
stake under the rule (and the largest sensitivity, 0.15 %, would have
failed it anyway).

## 5. Expert corner

- **Definitions used.** *Valid FPN* under the pinned rule: not a
  per-period concept; the test is the BSC registration FPN flag as
  carried in Elexon `reference/bmunits/all` `fpnFlag`. *Final Physical
  Notification Data* (BSC Section Q 3.2.2, pinned v41.0): "the data
  specified in the Physical Notification in respect of that BM Unit
  prevailing at Gate Closure"; *Gate Closure* (BSC Section X Annex X-1):
  "the spot time one hour before the spot time at the start of that
  Settlement Period"; *Physical Notification* (Grid Code Glossary): "Data
  that describes the BM Participant's best estimate of the expected input
  or output of Active Power of a BM Unit". The BSC rule for a BM Unit
  that submits no PN, and the Section K definition of the FPN Flag, are
  not in the pinned pages and are not asserted here. *Holding a
  position*: an EAC row with `serviceType == Response`, `auctionProduct`
  in {DCH, DCL, DMH, DML, DRH, DRL}, `executedQuantity > 0`, delivery
  interval containing the period. *Forfeit scope*: period (Schedule 3,
  F_aij = 0 at 0.1 % unavailability of the Settlement Period).
- **Units.** Population ids in `evidence/population.json` (Elexon and
  NGC form, lead party, flag). The silent unit: `E_GRFLB-1` / `GRFLB-1`,
  Conrad Energy (Trading) Ltd, `bmUnitType E`, 40.000 MW generation,
  −39.900 MW demand, GSP group `_A`, `fpnFlag` TRUE; DCH and DCL
  positions, participant CONRAD ENERGY (TRADING) LIMITED; 142 held periods
  2026-08-04..06 (window-clipped), 50 in 2026-07-29..30; zero PN, MELS,
  MILS and BOALF records. The FALSE-flag unit with reserve positions:
  `E_BTNHL-1` / `BTNHL-1`, Slow Reserve PSR.
- **Timestamps.** EAC `deliveryStart/End` are naive ISO and are read as
  UTC on the boundary evidence above; settlement periods are
  Europe/London half-hours; PN records are attributed by their own
  `settlementDate` and `settlementPeriod`.
- **Skipped rows** (post-rule): 196,329 non-response rows (PSR, PQR, NQR,
  PBR, NBR, NSR); 6,596 positions of the 28 unmapped non-BMU units; 0
  zero-quantity rows; 0 malformed intervals.
- **Fetch identities.** Documents (all 2026-09-04, 14:03 UTC):
  `ofgem-decision-pdf.pdf` `2ed908df…`; `ofgem-decision-pdf-jan27.pdf`
  `790fbc11…`; `ofgem-decision-reject.pdf` `1c946dfc…`;
  `neso-dc-service-terms.pdf` = DM = DR `52725f05…` (one combined NESO
  document, 1,097,368 bytes); `neso-drs-consultation-2025-11.pdf`
  `94aba23b…`; `neso-drs-final-submission.pdf` `a0382e54…`;
  `neso-procurement-rules-2026-07.pdf` `4384e55c…`;
  `grid-code-glossary-physical-notification.pdf` `4304a026…` (vintage
  unverified); `bsc-section-q-physical-notifications.html` `2b1989fa…`
  (v41.0 as pinned; a newer version may exist); `bsc-gate-closure-definition.html`
  `74e88815…`. Register `bmunits.json` `b15da673…` (14:05:51). EAC
  `eac-live.csv` `464e4bd5…` (179,125,224 bytes, 14:07:30; the package
  listing showed no monthly archive matching July or August 2026, so the
  live resource was pinned). Physical streams: 928 files under
  `data/raw/elexon/011/<window>/<utc-day>/`, 14:08:55–14:17:11, four
  chunks of ≤ 40 units per dataset per day; full digests in
  `evidence/manifest.json`.
- **Owners.** No lead party has exposure under the rule, so no Companies
  House request was made (`evidence/owners.json` is empty by
  construction); the 009 machinery is wired in `run.py` for the case
  where one does.
- **Limits.** The register flag is point-in-time. Timeliness of PNs is
  unobservable. Non-BMU providers' data submission is invisible. One
  28-day window each side of the effective date.

## 6. Reproducibility

`DECLARATION.md` (sha256 `99498205…`, unedited), `AMENDMENTS.md`,
`run.py --seal 99498205 --phase <documents|register|gate|eac|population|physical|evaluate|owners>`,
the pinned corpus under `data/raw/{rules,elexon,neso}/011/`, and
`evidence/{manifest,acquisition-log,instrument-gate,population,results,unit-chunks}.json`.
The screen replays from the pinned files with no network; `scripts/check`
runs its tests.
