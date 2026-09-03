# What a load-control licensee must be able to prove, by when — and which proofs no current system produces

*One page for a practitioner. Sources are the August 2026 policy package
(DESNZ government response, Ofgem decision, class-exemptions notice) and
the December 2025 draft conditions, all pinned by digest in F006. Dates
are the government's and carry its caveat "subject to parliamentary
scrutiny". Not published.*

## Are you in scope?

You are a **load controller** if you create or change a load control
signal to a private EV, a domestic-scale chargepoint, heat pump, storage
heater, heat battery, hot-water cylinder, hybrid heat pump or home
battery. You are a **flexibility service provider (FSP)** if you contract
with a domestic or small-business consumer for signals to be sent to
their appliance. The consumer, and anyone merely supplying them an
interface or a tariff, is not licensed. **Exempt as drafted**: control
only of other appliances (Class A); services only to larger businesses
(Class B); control "for the purpose of benefiting consumers" with no
trading in the Balancing Mechanism or imbalance arrangements, no service
to NESO or a DNO, and no contract with a party that does (Class C).
A tariff-only optimiser is exempt; the same platform selling into DFS is
not. The Order is out for representations until 7 September 2026.

## The clock

| when | what |
|---|---|
| Autumn 2026 | regulations laid; CAF profiles due "late 2026" |
| **1 March 2027** | application window opens. Apply within three months to be sure of a decision; Ofgem has nine months, after which the licence is deemed granted |
| ~Autumn 2027 | if you control ≥ 300 MW in aggregate: NIS designation as an Operator of Essential Services (Cyber Security and Resilience Bill) |
| 31 December 2027 | ESA Phase 1 device rules in force (heat, batteries); chargepoint rules already in force since June 2022 |
| **March 2028** | offence for unlicensed load control; conditions in force; Ombudsman ADR for FSPs |
| ~September 2029 | 18 months to demonstrate Tier 2 CAF compliance |
| end 2029 | formal NIS assurance for ≥ 300 MW |

## What you must prove, to whom

**At application (Ofgem, from 1 March 2027).** Identity, ownership,
directors; fit-and-proper statements; financial responsibility and
operational capability; a statement of intent on the consumer-protection
conditions; evidence of engagement with the BSC, CUSC and DCUSA; a CAF
self-assessment against the Tier 2 profile and a statement of intent to
comply by the government's timeline; aggregate controlled load. Domestic
supply licensees skip the managerial, financial and most consumer-
protection evidence (Pathway C).

**Continuously (Ofgem, from March 2028).** Quarterly RFI: complaints by
type and volume. Annually: a complaints report; returns on customer
numbers, load capacity, device types and volumes, propositions and
switching; a CAF assessment, a remedial action plan and a cyber
resilience audit (or an agreed equivalent); confirmation of no material
adverse financial change. Within 72 hours: any significant NIS incident.
Within three months: crossing 300 MW. On request: any information, in
the form requested. On inspection: access, documents, staff.

**Case by case (Energy Ombudsman, from March 2028).** That the complaint
was handled within eight weeks and what happened — in practice, what the
customer agreed to, what the device was told, and what it cost them.

## Which proofs no current system produces

The licence does **not** require any of the following, and the pinned
consultation responses show no one building or buying them:

1. **Per-signal authorisation and bounds** — evidence that each instruction
   was within what the consumer consented to. Consent today is captured at
   enrolment (register the device in the app; exclusivity terms), not per
   instruction.
2. **Device-level reconstruction months later** — what the device was told,
   when, by whom, across OEM cloud → controller → supplier. Operational
   telemetry exists with each party's own retention; no external standard
   defines what must be reconstructable, and Kraken's stated model is to
   handle the chain by supply-chain SLAs.
3. **Household-level attribution** — what a controller's action did to
   *this* household's half-hourly bill under MHHS. Market settlement uses
   NESO's P376 baseline; nothing attributes at the meter point.
4. **Portability evidence** — that devices can move between controllers.
   Octopus told Ofgem there is no standardised process; its own tariff
   excludes third-party control.
5. **Group-level aggregate load** — whether affiliates' licences aggregate
   toward 300 MW; DESNZ has deferred this to guidance.

The first three are exactly what a complaint, an information request or
an inspection will ask for. Whether that practice hardens into an
evidentiary standard is unknowable before the first Ombudsman cases on
licensed FSPs; until then, building for it is speculation, not
compliance.
