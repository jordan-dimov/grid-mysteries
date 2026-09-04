# 011 — who loses eligibility: declaration

**Frozen**: 2026-09-04, before any request for this question has been made
from this repository to Ofgem, NESO, Elexon or Companies House. Sealed by
the commit that adds this file; its SHA-256 is recorded in `RESULTS.md`
when the run happens. Results go in `RESULTS.md`; amendments, if any, in
`AMENDMENTS.md`, dated; the investor brief in `BRIEF.md`. Acquisition
waits for the human seal (see *Acquisition gate*). Lesson L1 binds
throughout: **every instrument is tested for eligibility before its
silence is used.**

## Trigger

Ofgem is reported to have approved NESO's *Dynamic Response Services*
amendments to the terms and conditions related to balancing, effective
from 2026-07-31 for a first tranche and from a later date (reported as
2027-01-01) for a second. The reported substance: a BMU that fails to
submit a valid Final Physical Notification (FPN) for a settlement period
is deemed unavailable for the frequency-response services in that period
regardless of its technical capability; and a metering or baseline
compliance threshold (reported as 80 % over a rolling window of up to 28
days) becomes a condition of participation. The regulator has made a piece
of operational bookkeeping a revenue prerequisite. Nobody has yet said
which units that catches.

"Dynamic Response Services" is NESO's collective name for Dynamic
Containment, Dynamic Moderation and Dynamic Regulation. **The pinned terms
decide which services and which conditions apply, not the trade press.**

## The mystery

> Under the eligibility conditions now in force, which battery BMUs
> currently earning frequency-response revenue would have been deemed
> unavailable, for how many settlement periods, and what does that do to
> the revenue stack an investor in those units is underwriting?

Deliberately **not** "are skip rates falling": 002, 003 and 007 T3 own
skip share, and that answer predicts nothing about a named asset.

## Prior exposure (recorded, not hidden)

1. The trigger reached the sponsor through a Perplexity weekly summary of
   2026-09-04 citing pv-magazine (2026-07-07) and ess-news (2026-07-06).
   One web search confirmed that the Ofgem decision page and PDF exist
   (published June 2026, "Effective by 31 July 26" in the filename). The
   80 % figure, the 28-day window, the second effective date, the tranche
   each condition belongs to, and the definition of a valid FPN are all
   **unpinned**. Nothing from the secondary sources enters the record
   unpinned; every reported figure above is a claim to be checked against
   the pinned decision, and is not used if the decision does not carry it.
2. Investigation 008's reconnaissance (2026-08-27) read the **schema** of
   NESO's EAC "Response-Reserve Results By Unit" resource and matched
   154 of 171 in-merit battery units to it by id. No EAC quantity or price
   was pinned or placed beside any unit; J1 was frozen and has not run.
3. Investigations 001 (2026-08-04..10) and 002 (2026-08-11..17) and the
   method studies read PN and MELS for a handful of selected units and
   for the naive screen's top ranks; none classified the battery
   population by FPN presence. BESS Study 001 read PN, MELS and MILS for a
   **panel** of battery units over July 2026 (its question was benchmark
   fragility; FPN presence was not an output). Both overlaps with this
   study's windows are stated in *Population and windows* below.
4. While preparing this declaration (2026-09-04), and before writing it,
   the following were read from artefacts **already pinned** by earlier
   investigations, **identity and schema only, no series values**: the
   field names of one PN and one MELS artefact (2026-08-04, SP 20, pinned
   by 001); the `fuelType` distribution of the 001 Elexon BMU register
   vintage; and the `fuel` column of NESO's August 2026 in-merit file. The
   material fact learned is recorded in *Population* below because it
   changes the population rule: the Elexon register carries **no battery
   classification** (its `fuelType` is NESO's generation-fuel code and is
   null for most units; no value is `BATTERY`).

## Primary sources, pinned first, none from memory

Pinned as bytes under `data/raw/rules/011/` (documents) before any series
is fetched. URLs are supplied at the seal from the sponsor's search, never
typed from memory; each is recorded in `evidence/acquisition-log.json`
with its fetch time and SHA-256. **Any 404 or refusal is recorded as
unavailable**, not worked around with a browser agent. Beside every use of
a definition in `RESULTS.md`, the source's own words are quoted.

1. The Ofgem decision letter approving NESO's Dynamic Response Services
   amendments to the terms and conditions related to balancing, and the
   approved amendment text (the June 2026 PDF on ofgem.gov.uk).
2. NESO's November 2025 Dynamic Response Services consultation and the
   final submission to Ofgem, with the withdrawn amendments named.
3. NESO's service terms for Dynamic Containment, Dynamic Moderation and
   Dynamic Regulation as amended, including the availability-payment
   mechanics (what an availability payment is paid per, and what an
   unavailable settlement period forfeits).
4. The Grid Code and BSC definitions of a Physical Notification, a Final
   Physical Notification and Gate Closure, and the BSC rule for a BMU
   that submits no Physical Notification for a settlement period.
5. Elexon `reference/bmunits/all` — the BMU registration data: id map
   (`elexonBmUnit` ↔ `nationalGridBmUnit`), `leadPartyName`,
   `leadPartyId`, `bmUnitType`, `fuelType`, `generationCapacity`,
   `fpnFlag`. One fresh pinned snapshot; the 001 vintage is kept beside it
   and any unit whose lead party differs between vintages is listed.

The definitions used by the screen are:

- **Valid FPN** — as the pinned Ofgem-approved text defines it. Until that
  text is read, the screen's structural definitions are fixed as follows,
  and the pinned definition selects among them or amends them in
  `AMENDMENTS.md` before any result is written:
  - **V0 present**: at least one PN record for the unit carries this
    settlement date and period.
  - **V1 covering** (primary): the PN records for the unit in the period,
    taken as intervals `[timeFrom, timeTo)`, cover the whole 30 minutes
    without a gap.
  - **V2 non-zero** (sensitivity, never the verdict on its own): V1 holds
    and at least one record has a non-zero `levelFrom` or `levelTo`. A
    zero FPN is a legitimate physical notification for a battery at
    rest; V2 is reported so the reader can see how much of the result a
    stricter reading would add, and it is used as the verdict **only if
    the pinned terms say a zero FPN is not a valid FPN for response
    provision**.
  - **Timeliness** (submitted before Gate Closure): the published series
    carries no submission timestamp in the fields known at freeze
    (`bmUnit, nationalGridBmUnit, settlementDate, settlementPeriod,
    timeFrom, timeTo, levelFrom, levelTo`). If the pinned stream carries
    one, timeliness is tested and reported; if not, it is recorded as
    **unobservable from public data** and the screen's "valid" is
    explicitly "valid on the published post-gate-closure record".
- **Compliance test** (metering / baseline threshold) — as the pinned text
  defines it; tested only if the instrument gate finds a public per-BMU
  performance or compliance series (see gate item G5).
- **Holding a position** — the unit has an EAC accepted row for a
  response service whose delivery interval contains the settlement period
  and whose executed quantity is greater than zero.
- **Deemed unavailable** — the unit holds a position in the period and the
  period fails the selected FPN validity rule.

## Instrument gate (run after the seal and before any series value is read; passes on schema and metadata only)

Each instrument is assigned one state from the protocol vocabulary:
`eligible now` · `eligible later (date D)` · `proxy only` · `no viable
public instrument`. The gate reads field names, resource listings and
row counts; it reads **no value of any unit in either window**.

| id | instrument | series | what the gate checks | eligible if |
|---|---|---|---|---|
| G1 | FPN presence and coverage | Elexon Insights `PN` (per settlement period, all BMUs, or the `datasets/PN/stream` filtered to the population) | field names include unit id, settlement date and period, `timeFrom`, `timeTo`, level fields; whether a submission timestamp exists; whether a unit with **no** PN in a period is absent from the series (absence distinguishable from a zero-level record) | absence and zero are structurally distinct; if the series back-fills zeros for silent units, the instrument is **proxy only** and V0/V1 cannot be run |
| G2 | Declared availability | Elexon `MELS`, `MILS` | same fields; used only as context (a unit with MEL > 0 and no PN is technically capable, which is exactly the case the rule creates) | as G1 |
| G3 | Balancing acceptances | Elexon `BOALF` | field names; used only as context (a BOA in a period with no valid FPN would be anomalous and is listed) | as G1 |
| G4 | Response positions and prices | NESO EAC "Response-Reserve Results By Unit" (CKAN resource `a63ab354-7e68-44c2-ad96-c6f920c30e85` as identified by 008, or the monthly archive resources of the same package for July and August 2026, whichever the package listing shows complete for both windows) | header fields include `auctionUnit`, `serviceType`, `auctionProduct`, `executedQuantity`, `clearingPrice`, `deliveryStart`, `deliveryEnd`, `technologyType`; the timestamp basis (UTC or local) is inferred from where delivery boundaries fall relative to EFA-block boundaries and recorded | fields present and every delivery interval is a whole number of half-hours |
| G5 | Metering / baseline compliance | any NESO Data Portal resource returned by `package_search` for the declared queries (`dynamic containment performance`, `dynamic response performance monitoring`, `response services compliance`, `baseline compliance`, `frequency response delivery`) with per-BMU rows and a compliance or performance metric | listing only: resource names, fields, row counts | a per-BMU series exists; otherwise **no viable public instrument**, and that half of the rule is recorded as unobservable from public data — which is itself a finding |
| G6 | Registration and ownership | Elexon `reference/bmunits/all`; Companies House profiles for lead parties | field names; the lead-party name field | present |

A failed G1 stops the screen: the investigation then records an
**ineligible instrument** (falsifier F2) and publishes that. A failed G4
means no revenue can be attached and the study reports FPN silence only,
labelled as such.

## Population and windows (computed programmatically; the code decides, not a hand list)

**Population.** Every BMU that (a) holds at least one accepted response
position in the post-rule window and (b) is classified as battery
storage. Because the Elexon register carries no battery class (prior
exposure item 4), classification is: EAC `technologyType == "Batteries"`
(the dataset's own field, per the 008 schema reading), **cross-checked**
against the set of `bm_unit` ids with `fuel == BATTERY` in NESO's pinned
in-merit files; units in one set and not the other are listed with both
labels and included if either says battery, the disagreement reported.
Ids are matched exactly in National Grid form and mapped to Elexon form
through the pinned register; a unit that fails to map is listed as
unmapped and excluded from the screen (it cannot be joined to PN).

**Post-rule window (the test).** The latest complete run of 28 settlement
days ending at least three full days before this declaration's commit
(2026-09-04): **2026-08-04 to 2026-08-31 inclusive**. It lies wholly after
2026-07-31, so the first-tranche conditions are in force for all of it.
Overlap, stated by name: 001's window (2026-08-04..10) and 002's window
(2026-08-11..17) are its first fourteen days. Those runs read PN and MELS
for a handful of selected units, not the battery population, and the
overlap is stated rather than avoided because a post-rule window ending
before September cannot be chosen otherwise.

**Pre-rule counterfactual.** The same screen on the first 28 days before
2026-07-31: **2026-07-03 to 2026-07-30 inclusive**, labelled
*counterfactual* wherever it appears, so the reader sees whether behaviour
changed when the rule bit. It lies wholly inside July, which BESS Study
001 consumed (2026-07-01..31), because "the 28 days before the effective
date" admits no other choice; BESS 001 read PN, MELS and MILS for a panel
of battery units in that month for a different question, and did not
compute FPN presence. May (003) is untouched.

**If the pinned decision places the FPN condition in the second tranche**
(effective after this window), the post-rule window is *not* post-rule
for that condition. The screen still runs on both windows, the labels
change to *exposure before the condition bites*, and the target conclusion
narrows to what a unit would have lost had the condition applied. This is
recorded, not silently reinterpreted.

## The screen (fixed now; code in `src/grid_mysteries/investigations/eligibility_screen.py`)

One pure function with a small JSON contract, no network, replayable from
fixtures. For each unit and settlement period in a window:

1. was a valid FPN present under the selected rule (V0, V1 or V2);
2. was the unit holding an accepted response position covering that
   period (by service);
3. if it held a position and the FPN test failed, it is **deemed
   unavailable** for that period.

Output per unit: periods held; periods deemed unavailable (listed by
settlement date, period and service); share of held periods; revenue held
and revenue at stake, in `Decimal` pounds, computed as executed MW ×
clearing price (£/MW/h) × hours in the period, summed over the services
held. **Availability-payment mechanics are taken from the pinned service
terms**: the screen carries a `forfeit_scope` of either `period` (the
unavailable settlement period's payment is forfeited) or `block` (the
whole EFA block's payment is forfeited when any period in it is deemed
unavailable); both are computed, and the one the pinned terms support is
reported as primary, the other beside it. If the terms describe a
mechanism neither captures, that is an amendment before results are
written. Per window: totals, the distribution across units, and
concentration by lead party (from the register) and by owner (from
Companies House, §*Milestone*). The pre-rule window is run through the
identical function and labelled counterfactual.

Settlement periods are local (Europe/London) half-hours numbered from
00:00; EAC delivery intervals are mapped onto them after the timestamp
basis has been inferred and recorded (G4). A PN record is attributed to
the period its own `settlementDate` and `settlementPeriod` fields name.

## Target conclusion, written now to be defended or narrowed

> Of N battery BMUs holding response positions in the window, K had at
> least one period with no valid FPN while holding a position; for those
> K the periods at risk total X, worth about £Y at the auction clearing
> prices, concentrated in [portfolio or lead party].

If K is zero, the finding is that the population already complies and the
rule reprices nothing, published as such.

## Milestone test (applied at the end, recorded either way)

Can the result name a unit, lead party or portfolio for which the
response revenue an investor is underwriting is measurably at risk under
the rule? Lead parties are mapped to owners through the pinned register
and Companies House (the 009 machinery: legal-name search, profile,
resolution rule as in `corporate_vitality.resolve`). The bar: for a named
lead party, revenue at stake in the post-rule window **≥ 1 %** of that
party's response auction income in the same window under the primary
forfeit scope, and the periods at risk not all falling in one contiguous
run of under 24 hours (a single outage is not a bookkeeping exposure).
The one-page brief (`BRIEF.md`) is written for the largest exposure that
clears the bar. If none does, the brief says what a technical adviser
would now be asked and why public data cannot answer it.

## Falsifiers (published with the declaration)

The conclusion is **wrong**, and is published as such, if any holds:

- **F1** the pinned rule does not deem a unit unavailable on FPN grounds
  in the way reported (no such condition; a different trigger; the
  condition in the second tranche only — see *Population and windows*).
- **F2** the PN series cannot distinguish an invalid FPN from a valid
  zero (or from silence), so the screen cannot be run; the investigation
  records an ineligible instrument.
- **F3** the population shows no periods at risk (K = 0).
- **F4** the revenue at stake is below one percent of the units' auction
  income in the window, so the fact does not change a deal.

## Acquisition gate

Human seal, then, in this order: documents (§*Primary sources*, items
1–4) → Elexon register (item 5) → the instrument gate written to
`evidence/instrument-gate.json` → EAC results for both windows →
population computed and written to `evidence/population.json` → PN, MELS,
MILS and BOALF for the population for both windows → the screen →
Companies House for the lead parties in the result → `RESULTS.md` and
`BRIEF.md`. Everything is pinned under `data/raw/rules/011/`,
`data/raw/elexon/011/`, `data/raw/neso/011/` and
`data/raw/companies-house/<run-date>-011/`, journalled with SHA-256 before
any value is read into the screen; the manifest is copied to
`evidence/manifest.json`. The runner (`run.py`) refuses to fetch unless
invoked with `--seal <prefix of this file's SHA-256>`, so the seal is on
the record in the command that acquired the data. The Ofgem and NESO
documents are read for the definitions **before** the screen runs,
because the validity rule depends on them; the screen's results are
computed under **every** structural rule (V0, V1, V2) and both forfeit
scopes so that the choice of primary rule, made from the documents,
cannot steer the numbers.

## Out of scope for this run

Skip rates (002, 003, 007); the interconnector SO–SO trading cap; EU gas
storage; any Morpholog or product work; any page outside the repo.

## Limits declared in advance

The screen tests the published post-gate-closure PN record, not what NESO's
control room received or when. Response positions are EAC results; any
bilateral or legacy contract is invisible. Revenue at stake is a
counterfactual under the pinned payment mechanics, never a realised loss.
Lead party is not owner; the Companies House step names the registered
company, not the equity behind it. The metering/baseline condition is
tested only if a public per-BMU series exists. One 28-day window each
side of the effective date, in one year.
