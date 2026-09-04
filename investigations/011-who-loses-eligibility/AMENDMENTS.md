# 011 — amendments

## Amendment 1 — the pinned rule is a registration flag, not a per-period FPN test (2026-09-04, before any series was fetched or any result written)

**Made after** the thirteen rules documents were pinned under
`data/raw/rules/011/` (journal `journal.ndjson`, digests in
`evidence/manifest.json`) and **before** the Elexon register, the
instrument gate, the EAC results or any physical series were requested.
The declaration (`DECLARATION.md`, §*Primary sources*) provides for
exactly this: "the pinned definition selects among them or amends them in
`AMENDMENTS.md` before any result is written."

### What the pinned text says

NESO, *Response Services Service Terms*, Version 6, "Effective From: 31
July 2026", "Date Published: 23 July 2026" (`neso-dc-service-terms.pdf`,
identical bytes pinned under the DM and DR names because NESO publishes
one combined document), paragraph 5.10:

> Where, in relation to a Response Unit which is BM Participating, the
> Service Provider sets its FPN flag to FALSE, then for the purposes of
> paragraph 7 until such flag is reset to TRUE the Response Unit shall be
> deemed unavailable to deliver all Auction Products.

Paragraph 7.2:

> For the avoidance of doubt, no settlement value shall be calculated
> pursuant to paragraph 7.1 and the formulae in Schedule 3 in respect of
> any period or periods of deemed unavailability pursuant to paragraphs 5
> or 6.

Schedule 3, *Calculation of Settlement Value*:

> With respect to each Response Contract, a settlement value shall be
> calculated for each Settlement Period in accordance with the following
> formula: S_aij = Round(((P_aj − ((1 − K_aij × F_aij) × PF_aj)) × V_aij ×
> 0.5), 2) […] F_aij is zero (0) if Response Unit i has any period or
> periods of unavailability for Auction Product a within Settlement Period
> j at or in excess of (either individually or in aggregate over all such
> periods) 0.1% of the duration of that Settlement Period, and is one (1)
> otherwise;

Ofgem, *Decision to approve … Effective by 31 July 26*
(`ofgem-decision-pdf.pdf`), Proposal 3:

> NESO has proposed to add a clarification that when a BMU sets its FPN
> flag to FALSE it will be deemed unavailable for Dynamic Response
> Services. This amendment aims to ensure that BMU's are submitting the
> correct data and that the correct processes are followed to de-register
> / re-register a BMU where providers wish to switch between BMU and
> non-BMU […] One stakeholder disagreed, stating that if the BMU is
> submitting the relevant data then the FPN flag is irrelevant to the
> availability of the unit. NESO responded that if the unit has an FPN
> flag set to FALSE then it will not be submitting the correct data (as
> NESO would not be receiving a PN from the unit). […] we have decided to
> approve NESO's proposal to deem units as unavailable for Dynamic
> Response if the FPN flag is set to FALSE.

and: "this approval applies only to proposals 3, 9 and 10, and is
effective by 31 July 2026."

Ofgem, *Decision to approve … Effective 1 January 2027*
(`ofgem-decision-pdf-jan27.pdf`), Proposal 2:

> We understand participants will need to achieve a certain level of
> compliance (80%) over an Assessment Period in order to remain be active
> within daily auctions. This amendment mainly affects non-Balancing
> Mechanism Units ("non-BMU"), as Balancing Mechanism Units ("BMU")
> already submit this data in accordance with the Grid Code.

footnote 7: "Assessment Period refers to the period of up to 28 EFA days
immediately prior to an auction."

Ofgem, *Decision to reject …* (`ofgem-decision-reject.pdf`): Proposal 6,
the Tiered Performance Regime ("Tier 0 – Units will be deemed unavailable
for settlement periods where breaches occur. Tier 1 – Units will be deemed
unavailable for the entire EFA block where the breaches occur. Tier 2 –
Units will be temporarily suspended from the market for a duration of 28
days. Tier 3 – Units will be de-registered from the market.") and Proposal
8, Unit Suspension, were **rejected**.

BSC Section Q (`bsc-section-q-physical-notifications.html`, v41.0 as
pinned) 3.2.2: "For each Settlement Period, the Final Physical
Notification Data in respect of a BM Unit shall be the data specified in
the Physical Notification in respect of that BM Unit prevailing at Gate
Closure." BSC Section X Annex X-1: "Gate Closure: means: (i) in relation
to a Settlement Period, the spot time one hour before the spot time at
the start of that Settlement Period". Grid Code Glossary
(`grid-code-glossary-physical-notification.pdf`): "Physical Notification:
Data that describes the BM Participant's best estimate of the expected
input or output of Active Power of a BM Unit". The BSC rule for a BM Unit
that submits **no** Physical Notification, and the definition of the
registration "FPN Flag" (BSC Section K registration data), are **not in
the pinned pages**; the pinned Section Q carries no "deemed zero" clause
that the extraction found. Recorded as not established from the pins.

### What changes

1. **Falsifier F1 has fired before any series was fetched**: the pinned
   rule deems a unit unavailable on a *different trigger* from the one
   reported. The trigger is the unit's registration **FPN flag set to
   FALSE**, a standing property of a BM Participating Response Unit, not
   a per-settlement-period test of whether a valid FPN was submitted. The
   80 %-over-28-days condition exists but belongs to the **second tranche
   (1 January 2027)**, is a data-submission duty that "mainly affects
   non-BMU" units, and is not in force in either window. The reported
   "28-day suspension" is the **rejected** Tier 2.
2. **Primary test**: the Elexon register's `fpnFlag` for each unit in the
   population. A BM Participating unit whose flag is FALSE is deemed
   unavailable for all Auction Products while the flag stays FALSE, so
   under the pinned terms its entire held revenue in the window is at
   stake. The register is a **point-in-time snapshot with no history**;
   the result is therefore "units contracted in the window whose flag is
   FALSE at the pin", and the write-up says so. Implemented as
   `eligibility_screen.flag_screen`, same output shape as the per-period
   screen so concentration and the milestone test apply unchanged
   (`results.json` → `windows.<w>.flag_rule`, labelled `primary: true`).
3. **The per-period rules V0/V1/V2 are demoted to sensitivity.** They are
   still computed, on both windows, exactly as declared, because NESO's
   own rationale ties the flag to PN silence ("NESO would not be
   receiving a PN from the unit"): the per-period silence of a unit with
   its flag TRUE is a description of bookkeeping, not a deemed
   unavailability under the pinned terms. No number from them is a
   "revenue at stake" under the rule.
4. **Forfeit scope is `period`**, settled by Schedule 3 (settlement value
   per Settlement Period, F_aij = 0 at 0.1 % unavailability of that
   period). `block` is the rejected Tier 1 and is reported only as the
   sensitivity the declaration already committed to.
5. **G5 (metering / baseline compliance)**: the gate still runs its
   declared searches, but the condition is not in force in the window and
   its population is mainly non-BMU, which Elexon PN cannot contain by
   construction — L1 ineligibility either way. Recorded as such.
6. **The target conclusion** is narrowed in advance to: "of N battery
   BMUs holding response positions in the window, K carry an FPN flag of
   FALSE at the register pin; their held revenue in the window is £Y". If
   K is zero the population already complies and the rule reprices
   nothing.

Runner change recorded: `run.py` gained `flag_screen` output and a
content-type probe for extension-less NESO download URLs; `run.py`
`--rule-note` carries the sponsor's words at the seal. Nothing in
`DECLARATION.md` is edited.
