# F006 — K1 absorption and K2 strain, six functions in the frozen order

**Frozen order**: P2 → P5 → P7 → P1/P3 → P6 → P4. Verdicts carry their
reason (v4 §6). Every quotation is from a pinned artefact; the responses
archive (`ofgem-lcl-consultation-responses-2026-08.zip`, 21 files,
published 7 August 2026) was read in full for the four functions whose
eligible-now instrument it is.

## P2 — override

**K1 absorber**: the device maker under SI 2021/1467 (owner override of
default hours and of DSR, in force 30 June 2022; on-device security log;
12-month consumption record) and, from 31 December 2027, the ESA Phase 1
regulations for heat and batteries. **Already externalised to product
regulation in 2022** (P6 question). The licence does not ask the
controller to prove an override was honoured; the Ombudsman and Flex Assure
asked for "must" and Ofgem's decision left it in guidance. **K1: absorbed,
successfully** — the function sits with the party that builds the button.
**K2**: `unmeasured — instrument proxy, not opened` (OPSS enforcement
actions were the declared proxy; K1 settled the candidate without them).

## P5 — cyber baseline

**K1 absorbers**: the applicant's own security function; external
auditors (respondents propose ISO 27001 and SOC 2 Type II as CRA
equivalents, Ofgem decision §6.19); Flex Assure's periodic independent
audits (2 of 12 domestic DFS providers); the SSES Security Governance
Group, "which will operate from Autumn 2026", supporting Ofgem "with
assessing the cyber security evidence provided as part of load control
licence applications" (`elexon-sses-sgg-page`); Ofgem itself in the first
year of applications (decision §6.47). The assurance function is
**assigned and purchasable**: a mature audit market plus a regulator-
appointed assessor. Strain candidate recorded from the incumbent's own
words: BEAMA — multi-vendor architectures with "legacy systems already
deployed in consumers' homes" make end-to-end CAF alignment "sequential
rather than parallel", asks for 24 months; ADE — applicants "will only
have three months to satisfy the wide breadth of evidence requirements";
Kraken — licensing cost "could lock those load controllers out of the
market". **K1: absorbed by assignment; capacity untested until the first
assessments.** **K2**: `not yet observable (application evidence from
2027-03-01; annual CAF assessments from 2028-03; NIS assurance grace to
2029-12)`. Deferred, not quarantined; watch dates below.

## P7 — exemption boundary

**K1**: the boundary is being written by DESNZ (notice closed 7 September
2026) and will be enforced by Ofgem from March 2028; the function "prove
you are exempt" has no absorber because, as drafted, exemption is
self-determined by purpose and contracts. Contested in the incumbents'
own words (Kraken Q13: is a supplier whose customers "use the supplier's
tariff information to optimise their device" a load controller? "it's not
the customer that is deciding"). **K1: unabsorbed but also unforced for
the exempt class; forced and self-served for the licensed class.**
**K2**: `not yet observable (final Order text; enforcement 2028-03)`.

## P1 and P3 — authorisation, bounds, reconstruction

**K1 absorbers found performing the function today**: supplier platforms
— consent is captured *at enrolment* (Octopus smart-tariff terms 2.3.1.5:
register the device in the app within seven days; "Low Carbon Technology
… that we control under one of our smart tariffs"), exclusivity avoids
conflicting instructions (IOG FAQ), complaints are recorded under
existing supply-licence processes (Octopus response Q12: "clear guidance
will be needed on complaints recording"; "suppliers have already begun to
collate their own data", citing LCP's household flexibility market
monitor, 16 December 2025); OEM clouds and device logs (SI 2021/1467
security log; Myenergi on role separation); Flex Assure ("Records of
customer complaints are maintained" is a self-assessment item;
independent audits); the Energy Ombudsman (ADR since 8 January 2026 for
members; for licensees from March 2028). **What no absorber performs and
no buyer asks for**: per-signal authorisation evidence and device-level
reconstruction to an external standard. In 21 responses, none states that
retrospective consent or instruction evidence is costly or impossible;
the costs cited are RFI administration (Octopus: "close to the upper-end
of Ofgem's estimate of £24,000"; Kraken: "could exceed the calculated
amounts"). Kraken's position is that the FSP should be the single
accountable party and "manage the risk within their supply chain through
service level agreements" — the reconstruction chain OEM → controller →
supplier is to be handled by contract, not by an external ledger.
**K1: absorbed successfully at the level the licence demands; the
higher-standard proof is unforced and unbought.** **K2 on the eligible-now
instrument**: `measured stable` — the responses could contain symptom
(a) and do not. **Falsifier F3 fires** for P1 and P3.

## P6 — aggregate-load accounting

**K1 absorber**: the licensee's own portfolio system (Axle: "300k live
devices", "2GW total shiftable load capacity", `axle-home`) plus
self-notification under 9.6 and the annual RFI. **K2 on the eligible-now
instrument**: `measured strain (weak — standardisation pressure)`: OVO,
BEAMA and Myenergi each ask how the 300 MW threshold is counted, across
group entities, and how tier transitions are handled; the government
response "acknowledges the practical questions raised about the operation
of the 300 MW" and defers to guidance. The pressure is on the rule-writer,
not on an absorber failing to count; proceeds to K3 because v4 lists
standardisation pressure as revealed strain.

## P4 — settlement attribution

**K1 absorbers**: NESO's DFS baseline (P376, retained for domestic;
optional self-nomination for I&C from 9 April 2026) and the providers'
weekly settlement submissions; supplier settlement under MHHS. Market-
level attribution is absorbed and rule-governed. Household-level
attribution (what a controller's action did to *this* bill) has no rule,
no condition and no buyer: Ofgem's complaints RFI is by type and volume.
**K1: absorbed at market level; unforced at household level.** **K2**:
`unmeasured — unpublished (SLC 31E reports carry no attribution field, as
Batch 02 C18 recorded on 2026-08-26; per-provider DFS settlement disputes
are held by NESO)`.

## Funnel after K1/K2

| stage | count | functions |
|---|---:|---|
| generated | 8 | P1–P8 |
| K0 buyer-real | 7 (+1 split) | P1–P6, P8; P7 split |
| quarantined — buyer-real, not publicly strain-testable | 1 | P8 |
| reached K1 | 6 | P2, P5, P7, P1/P3, P6, P4 |
| K1 absorbed successfully | 4 | P2 (product regulation, 2022), P1, P3 (supplier/OEM/Ombudsman machinery), P4 (market level) |
| K1 absorbed by assignment, capacity untested | 1 | P5 (SGG + audit market) |
| K1 unabsorbed / unforced | 1 | P7 (exempt class) |
| K2 measured stable | 2 | P1, P3 |
| K2 measured strain | 1 | P6 (weak, standardisation pressure) |
| K2 not yet observable | 2 | P5, P7 |
| K2 unmeasured — unpublished | 1 | P4 |
| proceeding to K3 | 1 | P6 |
