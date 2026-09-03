# Forward Mystery F006 — who must prove control?

**Generator**: v4 (`investigations/forward/CANDIDATE-PROTOCOL.md`,
`2ac6efa8e873100d4d06937d61e3f06e38cdcccd86b4fc50fca7ef3d911b2558`).
**Generated**: 2026-09-03. **Public-as-of**: 2026-09-03.
**State**: GENERATED. Committed in this state so that the generation
digest predates any pinned primary document, any metadata reading and
any market evidence. §6 (pinned forcing variable, with each source's own
caveats), §7 (instrument states) and §8 (freeze: kill order, thresholds)
are appended afterwards; nothing above §6 is edited. The file's digest at
the freezing commit is the study's identity. For the forward track the
human gate is **publication**: the falsifiers are frozen here, with the
claim, and nothing is released without the sponsor's seal.

**Standing note.** The 2026-08-26 recalibration limits desk research on a
new opportunity to two hours before a buyer conversation. The sponsor
commissioned this study on 2026-09-03 as an explicit exception, because
the forcing variable is a dated statutory obligation whose text can be
pinned, and because the third falsifier is built to kill it early. That
decision is the sponsor's and is recorded, not re-argued.

## 1. The question

Great Britain intends to make **load control** — controlling by digital
signal the flow of electricity into or out of domestic batteries, EV
chargepoints and heat pumps — a **licensable activity** under the
Electricity Act 1989, with consumer-protection licence conditions and a
cyber-security baseline, and an offence for doing it unlicensed. In the
same period Market-wide Half-Hourly Settlement puts every household on
half-hourly settlement.

> **When control of a household's battery, car and heat pump becomes a
> licensed activity, what must a licensee be able to prove, to whom, at
> what moment — and who is already positioned to prove it?**

Deliberately *not* "will home flexibility grow" or "will there be
virtual power plants". Everyone knows that; it predicts nothing. The
question is about **proof obligations**: the evidentiary functions the
licence forces into existence, who absorbs them, and whether any of them
escapes its absorber.

## 2. Prior exposure, recorded

On 2026-09-03, before this declaration, a Perplexity research run in
**another repository** produced the timeline and scope summarised in §3
and a reading of the consumer-protection guidance. **Everything in §3 is
therefore a hypothesis with a known author.** Each date and scope
statement is replaced in §6 by a pinned primary document quoted with its
own caveats, or is recorded as *not found in a primary source*. Nothing
from that run enters the record unpinned. The Wilkes case (a consumer's
own AI agent controlling the consumer's own devices) comes from the
Bloomberg feature behind Investigation 010 and is used here only as a
named instance of a class, not as evidence.

## 3. The forcing variable, as hypothesised (to be replaced by §6)

- DESNZ, Smart Secure Electricity Systems (SSES) programme: **Load
  Control Licence Regulations** making load control licensable under the
  Electricity Act 1989. Hypothesised schedule: regulations laid autumn
  2026; applications opening by end-2026; a twelve-month transition; the
  obligation (an offence if unlicensed) around end-2027; an alternative
  published schedule about a quarter later.
- Scope: anyone controlling the flow of electricity into or out of
  domestic batteries, EV chargepoints and heat pumps by digital signal.
- Licensees carry consumer-protection licence conditions and a cyber
  baseline; an **enhanced tier above 300 MW** of aggregate controlled
  load; **class exemptions**, one for control that benefits only the
  consumer.
- Alongside: **MHHS** puts every customer on half-hourly settlement, with
  the migration window running to May 2027.
- Adjacent: Energy Smart Appliance (ESA) regulations; the 2021 smart
  chargepoint regulations already in force; PAS 1878 / PAS 1879.

## 4. Generation — the v4 chain, run blind

Force vocabulary as v2/v3: `continuous` · `cross-organisational` ·
`data-intensive` · `high-volume` · `latency-sensitive` · `standardisable`
· `independence-required` · `liability-bearing` · `comparable-across-assets`
· `specialist-human-workflow` · `rising-transaction-volume` ·
`expensive-adviser-labour`. Three co-present external changes are used:
**the licence** (obligation + conditions + offence), **MHHS** (every
household's consumption becomes a half-hourly financial fact), and the
**ESA / smart-chargepoint device regulations** (device-side logging and
interoperability duties). Each forced function below names the buyer
class and the **incumbent guess, blind** — written before any
incumbent-market evidence is read, so that K1 can score the guess.

| # | Forced function (what a licensee must be able to prove) | Forces | Buyer class | Incumbent guess (blind) | Predicted strain symptoms | Candidate public series (named for the gate, values unread) |
|---|---|---|---|---|---|---|
| **P1** | **Authorisation and bounds**: every control signal sent to a consumer's device was authorised by that consumer and stayed within the consented bounds (devices, times, depth, price/comfort limits) | continuous, high-volume, liability-bearing | licensed load controllers: supplier platforms (Kraken and its licensees), independent controllers / aggregators, OEM clouds, chargepoint operators, consumer-agent platforms | the controller's own platform consent records and event logs (Kraken; OEM clouds; CPO back-ends), built for operations, not for proof | (a) consultation responses from controllers cite the cost or impossibility of retrospective consent evidence; (b) licence applications delayed or conditional on consent evidence; (c) complaint categories for "control without consent" appear | DESNZ / Ofgem consultation response lists and published responses; Ofgem register of load-control licence applications (once open); Ofgem supplier complaints reporting (if cause-split) |
| **P2** | **Override**: the consumer could override at any time, the override channel worked, and the controller honoured it | continuous, liability-bearing, standardisable | as P1, plus device OEMs whose firmware implements override | OEM app/firmware plus PAS 1878-style override design; the controller's incident tickets | (a) override failures appear in complaints or Ombudsman cases; (b) OEM firmware recalls / updates citing override | Energy Ombudsman published case categories; OZEV smart chargepoint compliance statements register; OEM security advisories (no series) |
| **P3** | **Reconstruction**: what a given device was told, when, by whom and why, reconstructed for a complaint, a dispute or an Ofgem information request, months later | data-intensive, independence-required, liability-bearing | licensees (respond); Ofgem and the Ombudsman (request); suppliers under complaints handling | the controller's operational telemetry store and the supplier's complaints machinery; OEM cloud logs with OEM retention policies; for chargepoints, the 2021 regulations' logging duty | (a) Ofgem information requests to load controllers; (b) enforcement or compliance cases citing incomplete records; (c) complaints-handling standards missed by suppliers with control products | Ofgem enforcement / compliance case register; Ofgem complaints-handling standards reporting; Ombudsman case data |
| **P4** | **Settlement attribution**: attributing a household's half-hourly settlement outcome (its bill, or the supplier's settlement cost) to the controller's actions versus the household's own behaviour — the flexibility "counterfactual" at household level | data-intensive, cross-organisational, comparable-across-assets | suppliers (settlement risk holders), controllers selling flexibility, DNOs/NESO buying it, consumers disputing bills | supplier billing systems under MHHS; DSO/NESO baselining rules (Elexon flexibility market rules); Kraken's internal attribution | (a) baseline / attribution disputes in flexibility markets; (b) MHHS-era billing complaints citing smart control; (c) DSO tender rules changing baselining | Ofgem SLC 31E flexibility procurement reports (annual, per DNO); Elexon flexibility market rules versions; Ofgem complaints reporting |
| **P5** | **Cyber baseline**: demonstrating the licence's cyber-security baseline (and the enhanced tier above 300 MW of aggregate controlled load) to the licensing authority, on application and continuously | standardisable, independence-required, expensive-adviser-labour | every applicant; enhanced-tier licensees | certification bodies and test labs already testing PAS 1878 / ETSI EN 303 645 / DCC security; NCSC guidance; the applicant's own security function; consultants | (a) certification-body capacity and lead times; (b) applications refused or delayed on cyber grounds; (c) audit / assurance job adverts at controllers | Ofgem licence-application register (once open); certification-body scheme lists (metadata); Companies House filings of named controllers (headcount, R&D) |
| **P6** | **Aggregate-load accounting**: knowing and evidencing the aggregate controlled load at any moment against the 300 MW enhanced-tier threshold, across devices, OEM APIs and sub-contracted control | continuous, data-intensive, cross-organisational | controllers near the threshold; the licensing authority | the controller's portfolio system; NESO/DNO service registrations (partial view) | (a) threshold definitions contested in consultation responses; (b) controllers restructuring portfolios below the tier | consultation responses; Companies House group structures of named controllers |
| **P7** | **Exemption boundary**: proving that control "benefits only the consumer" so that no licence is needed — the consumer-agent case (a consumer's own agent controlling the consumer's own devices) | liability-bearing, standardisable | consumer-agent platforms; OEM apps with local optimisation; installers | nobody today — the boundary does not yet exist; the exemption order text will define it | (a) exemption-scope arguments in consultation responses; (b) exemption determinations / guidance requests | DESNZ consultation responses; the class exemption order amendment text |
| **P8** | **Portability / switching proof**: evidencing that a consumer can move devices between load controllers and that control data follows or is deleted | cross-organisational, standardisable | licensees; OEMs; consumers | OEM account systems; ESA interoperability requirements; no cross-party function today | (a) switching complaints; (b) interoperability requirements in the ESA regulations | ESA regulation text (metadata); Ombudsman categories |

**Blind priors, written now.** The functions most likely to be absorbed
by existing machinery are **P2** (override is a device-design duty
already in PAS 1878 and the 2021 regulations) and **P5** (a certification
market already exists). The functions most likely to lack an absorber are
**P3** (reconstruction to an external standard of proof, months later,
across a chain of OEM cloud → controller → supplier that no single party
controls) and **P4** (household-level attribution, which no party today
is paid to produce independently). **P7** is the boundary that decides
whether the consumer-agent buyer class exists at all. Recorded so K1
can score the priors, not to steer them.

## 5. Evidence used only to justify generation

Only the hypothesised forcing variable in §3 and public facts already in
this project's record: Investigation 010 (Octopus tariff pairing rules
and the smart-tariff terms; the Bloomberg feature's two GB households),
Batch 02 C18 (Elexon market facilitator, FMAR delivery strain, SLC 31E
reports), Batch 01 C1 (MHHS as a transition programme). **No
incumbent-market evidence, buyer evidence or instrument values were
examined before this section was committed.** Where the K1 absorber is
a party already characterised in the record (Elexon FMAR, Kraken's
tariff terms), that is disclosed here as adjacency, not quarantined: the
study is a single mystery, not a batch, and the sponsor chose it.

## 6. Pinned forcing variable — appended after acquisition, before freeze

*(empty until the primary documents are pinned; each date beside the
source's own caveat; every 404 recorded as unavailable)*

## 7. Instrument states — appended by the gate

*(empty until the gate runs; metadata only; see v4 §3)*

## 8. Freeze — appended after the gate

*(kill order, K0 evidence classes, falsifiers restated against pinned
text, thresholds, freeze digest)*

---

## 6. Pinned forcing variable — appended 2026-09-03, before freeze

Everything below is read from documents pinned under
`data/raw/forward-f006/public-as-of/` (SHA-256 per file in
`evidence/public-as-of-manifest.json`, 61 artefacts, fetched 2026-09-03).
Every date carries the source's own caveat. Where §3's hypothesis differs,
the pinned text replaces it. **No consultation response, incumbent
statement or instrument value was opened**: the responses archive was
pinned and its file list read; its contents wait for K1.

**Statute.** Energy Act 2023 s.238: an *energy smart appliance* is "an
appliance which is capable of adjusting the immediate or future flow of
electricity into or out of itself or another appliance in response to a
load control signal", and a *load control signal* is "a digital
communication sent via a relevant electronic communications network to an
energy smart appliance for the purpose of causing or otherwise
facilitating such an adjustment" (`energy-act-2023-s238`). The power to
make load control licensable is s.56FBA of the Electricity Act 1989,
inserted by s.249 and Sch. 19 para 2 of the 2023 Act (recited in the
draft regulations' preamble).

**The draft regulations** (`desnz-lcl-draft-regulations-2026`, "DRAFT …
laid before Parliament under section 56FBB(4)", consultation draft of
December 2025): new s.4(1)(g) makes carrying on a load control activity
without a licence an offence; s.4(3J) defines the activity as performing
the function of a load controller *or* contracting with a consumer for
signals to be sent to an ESA at their premises; s.4(3K)(b): "a person does
not perform the function of a load controller … if they are an end-user of
that energy smart appliance". Reg. 1(2): the offence provisions come into
force 12 months after the regulations are made. Schedule 2 brings
consumer-facing licensees (FSPs) into the Consumers, Estate Agents and
Redress Act 2007, the Complaints Handling Standards Regulations 2008
(including publication of complaints information) and the Redress Scheme
Order 2008. *Caveat*: a consultation draft; the 2026 government response
(below) changes the load-controller definition, and the instrument
planned for Autumn 2026 has not been laid.

**Government response, 2026** (`desnz-lcl-government-response-2026-pdf`,
DESNZ 2026, published alongside Ofgem's 7 August 2026 decision per that
decision's §1): "To lay the load control licence regulations in
Parliament in Autumn 2026"; "For applications for a load control licence
to now open in March 2027, subject to parliamentary scrutiny"; "For the
requirement to hold a licence to come into force in March 2028, 12 months
after" the window opens, with a 12-month transition written into the
regulations. "Controlling the timing of sending a load control signal" is
removed from the licensable function; "changing a load control signal" is
licensable only where it changes the signal's effect on the ESA. A new
exemption is introduced "for load control which is for the purpose of
benefitting the consumer (e.g. from a manufacturer providing device
optimisation) and not for the purpose of providing services to persons
operating a transmission or distribution system or persons engaged in the
wholesale trading of electricity". Ofgem receives derogation powers. FSPs
join the Energy Ombudsman scheme when the requirement takes effect. The
Tier 2 cyber implementation period is 18 months "from the point" the
conditions come into force, "now planned for March 2028". *Caveat*: §3's
"end of 2026 / end of 2027" (the December 2025 plan) is superseded by a
schedule one quarter later, exactly the "alternative published schedule"
the sponsor's brief anticipated.

**Ofgem's decision** (`ofgem-sses-implementation-decision-2026-08`,
"Publication date: 07 August 2026"; stages: consultation closed 18
February 2026, responses published 7 August 2026): the application
window "intended to be 01 March 2027"; applicants wanting assurance of a
decision before the requirement bites "should submit their application
within the first 3 months"; **tacit authorisation** — a licence is deemed
granted if Ofgem has not decided within nine months; three application
pathways (A non-suppliers: full evidence; B non-domestic suppliers; C
domestic suppliers: exempt from managerial/financial and certain
consumer-protection evidence); class derogations "before the licence
legally comes into force in March 2028"; licence revocable for NIS
non-compliance; in the first year Ofgem assesses every application, then
the BSC Security Governance Group takes on technical cyber assessments.
**Monitoring** (Tables 4–6): quarterly RFI on complaints type and volume;
annual licensee complaints report; annual returns on other conditions;
annual RFI on customer numbers, load capacity, device types and volumes,
propositions, switching; formal data-sharing with the Energy Ombudsman;
possible market-insights monitoring "before the load control licence
becomes legally enforceable in late 2027" (the decision's own phrase,
inconsistent with its March 2028 date — quoted as found). **Compliance
priorities**: cyber security first, treating customers fairly second,
operational/financial/management controls third. **Cyber evidence at
application**: "a self-assessment against the relevant CAF Profile … and
a statement of intent to achieve compliance by the Government-defined
timelines".

**The draft standard conditions** (`desnz-lcl-draft-standard-conditions-pdf`,
December 2025 draft; government response 2026: "no substantive changes"
to conditions 3–8, 11–14): Condition 6 — give information to the
Authority or Secretary of State "when and in the form requested";
Condition 9 — 9.6 notify the Secretary of State within three months of
controlling ≥ 300 MW aggregate load; 9.7 an annual **CAF Assessment**
(defined as "either a self-assessment or a third-party audited
assessment"); 9.9 an annual Remedial Action Plan; 9.13 an annual "cyber
resilience audit or an equivalent form of audit if agreed in advance";
9.16–9.21 notify NIS incidents "no later than 72 hours"; 9.23–9.26
inspections, including allowing an inspector to "print, copy or remove
any document or information"; Condition 10 — "pay due regard to the
effects that the Load Control Activity could have on an Energy Smart
Appliance and the electricity system" and ensure "any data source that
is used to inform Load Control Activity, is from a trusted and validated
source"; Conditions 11–14 (FSPs) — standards of conduct, suitability and
no mis-selling, principal terms made clear "ahead of time … and post
Contract confirmation", exit steps and no undue prevention of switching,
proportionate exit fees. **Read for what is absent**: no condition
requires a licensee to record the load control signals it sends, to hold
evidence of a consumer's consent to a specific instruction, to evidence
that an override was available or honoured, or to retain any such record
for any period. Override appears only in Ofgem's draft consumer-protection
guidance (`ofgem-lcl-annex-d-consumer-protection-guidance`: "FSPs
*should* provide the option for customers to override load control
requests"). This absence is the pivot of the study and is pinned as such.

**The class exemptions** (`desnz-class-exemptions-statutory-notice-pdf`,
published 7 August 2026, "Closing date: 7 September 2026";
`desnz-class-exemptions-draft-order-2027-pdf`, "comes into force on [**
November 2027]" — a bracketed placeholder inconsistent with March 2028,
quoted as found): Class A (control only of ESAs outside the Phase 1
definitions / private EVs / ancillary appliances); Class B (flexibility
services only to consumers who are not domestic or small-business);
**Class C** — persons "carrying on load control activity for the purpose
of benefiting consumers, and not carrying on such activity for the
purpose of providing services to" transmission or distribution system
operators or wholesale traders. Policy intent as stated: the exemption
does **not** apply if the entity trades in the Balancing Mechanism or
imbalance arrangements, provides a flexibility service to NESO or DNOs
(Capacity Market, flexibility markets, ancillary/balancing services), "or
has a contract in place, in relation to the use of the load control in
question, with an entity … who is trading in the above markets or
provides a flexibility service to NESO or DNOs". The 2024 framing that
responding to time-of-use tariffs or day-ahead prices "could benefit
suppliers" is recited as history; the notice does not state whether
tariff-only optimisation by a third party is Class C. Options for a
further small-load-controller exemption at 1, 5, 10 or 35 MW are floated.
*Caveat*: proposals under s.5(2)–(3) notice; final Order undated.

**Cyber tiers** (`desnz-tier-1-load-control-consultation-2026`, issued
23 June 2026, respond by 1 September 2026): organisations controlling
≥ 300 MW in aggregate become NIS Operators of Essential Services via the
Cyber Security and Resilience Bill, Royal Assent expected "Spring 2027",
in force "around Autumn 2027"; Tier 1 CAF profile to be published "late
2026"; a grace period with "year end 2029" proposed for formal assurance.
Below 300 MW: Tier 2 via the licence (Condition 9).

**Devices.** ESA Phase 1 regulations (`desnz-esa-phase1-consultation-2025-12-pdf`,
closed 5 February 2026; gov.uk page: "We are analysing your feedback"):
to be laid "Q1/2 2026"; requirements in force from 31 December 2027; EVSCP
amendments about six months after making, "expected … Q4 2026". The
existing Electric Vehicles (Smart Charge Points) Regulations 2021
(SI 2021/1467, `ev-smart-charge-points-regs-2021-reg-log`): a chargepoint
must be able to measure or calculate power every second and record
consumption for the preceding 12 months, must let the owner override
default charging hours and "override the provision of demand side
response services", and must incorporate an on-device *security log*;
the statement of compliance is the manufacturer's, and the seller's
register (reg. 14) is private. PAS 1878:2021 and PAS 1879:2021 pages
pinned (`bsi-pas-1878-page`, `bsi-pas-1879-page`).

**MHHS.** Ofgem approved CR055 on 29 November 2024
(`ofgem-mhhs-cr055-decision-page`): migration from October 2025, cutover
July 2027; the programme site (`mhhs-programme-home`, undated banner)
reports "50% of all Industry Meter Point Administration Numbers (MPANs)
migrated"; the migration end of May 2027 is the programme's date.

**EU comparator only.** ACER's proposal for a network code on demand
response reached the Commission on 7 March 2025; the Commission's
targeted consultation page is pinned (`eu-nc-dr-commission-consultation`).
Not used in any kill.

**Unavailable.** None of the declared sources returned 404 or 403 on
2026-09-03 (`evidence/public-as-of-unavailable.json` absent).

## 7. Instrument states — appended by the gate, 2026-09-03 (metadata only)

The gate read schemas, page structure, publication calendars and file
lists; no series value and no response text was opened. Existence checks
per v4 §3: 1 existence · 2 population · 3 observability · 4 earliest date
· 5 risk-bearing.

| # | symptom → series | checks | **state** |
|---|---|---|---|
| **P1** authorisation & bounds | (a) controllers' consultation responses: `ofgem-lcl-consultation-responses-2026-08.zip`, 21 files (ADE, Myenergi, Drax, Salesforce, SSEN, Scottish Power, BUUK, RECCo, OVO, Kraken, CSE, Octopus, Startup Coalition, SSE, BEAMA, Flex Assure, Energy Ombudsman, Citizens Advice, EDF, Energy UK ×2) — published 7 Aug 2026, documentary, one-off | 1✓ 2✓ (the obligated class, in its own words) 3✓ 4✓ 5✓ | **eligible now (a)** |
| | (b) licence applications delayed/conditional: Ofgem notices of application and the Electronic Public Register (`ofgem-epr-home`) — grants published; refusals "with reasons" to the applicant only | 1✓ 2✓ 3 partial 4 ✗ until 2027-03-01 | eligible later (2027-03-01) |
| | (c) complaint category "control without consent": Ofgem customer-service data (`ofgem-customer-service-data-portal`, per-supplier volumes, no cause split); Ombudsman "top three complaint types" (`energy-ombudsman-complaints-data`) | 2 ✗ aggregates away | no viable instrument |
| **P2** override | OPSS enforcement actions under the 2021 regulations (`opss-evscp-enforcement-page`: undertakings, compliance notices, penalties) — device-side, manufacturers; controller behaviour not observed | 1✓ 2 ✗ (wrong party) 3✓ 4✓ | **proxy only** (gap: a device recall says nothing about a controller honouring an override) |
| **P3** reconstruction | (a) responses as P1(a) — controllers' own statements on records and retention | as P1(a) | **eligible now (a)** |
| | (b) Ofgem compliance/enforcement cases (`ofgem-compliance-cases`, `ofgem-enforcement-cases`) — compliance activity "from the end of the transition period" | 4 ✗ until 2028-03 | eligible later (2028-03) |
| **P4** settlement attribution | SLC 31E flexibility procurement reports (`ofgem-slc31e-reports-2024-25`, annual per DNO, MW/£) — attribution to household control not a field (as C18 found) | 2 ✗ | **proxy only** (gap: procured volumes, not disputes) |
| **P5** cyber baseline | Companies House accounts of named controllers — Kraken Technologies 12014731 (next accounts to 31 Jan 2026 due 31 Oct 2026), Axle Energy 14633671 (to 28 Feb 2026 due 30 Nov 2026), Kaluza 12218299, EV Energy 15046510 — annual; spend not function-specific; EPR as P1(b) | 1✓ 2✓ 3 partial 4✓ | **proxy only** (gap: headcount/R&D are not cyber-assurance spend); EPR eligible later (2027-03-01) |
| **P6** aggregate-load accounting | responses as P1(a) (the 2026 government response records respondents asking for "clearer definitions, especially around the 300 MW threshold") | as P1(a) | **eligible now (a)** |
| **P7** exemption boundary | representations on the statutory notice (closing 7 Sep 2026; summary undated) and the final Order; the draft Order's text exists now | 1✓ 2✓ 3✓ 4 ✗ until publication | **eligible later (after 2026-09-07, date not fixed)**; the draft text is read at K0 |
| **P8** portability | Ofgem's annual switching RFI is not public; Ombudsman aggregates; ESA Phase 2 (interoperability) planned 2027 | 1 ✗ | **no viable public instrument** — K0 still runs |

Guidance applied (P8 of v4): Ofgem licensing is a free public function,
so its service-level symptom is the nine-month determination clock and
tacit authorisation, observable on the EPR from 2027-12 at the earliest;
recorded as a watch, not adopted as a strain instrument here.

**Hindsight guard.** In extracting dates from the government response and
Ofgem's decision, summaries of stakeholder views were unavoidably seen
(e.g. "several proposed that licensing should apply only to contracted
services"; respondents asking for 300 MW definitions; suggestions of ISO
27001 / SOC 2 as audit equivalents). These are recorded here so they
cannot later be presented as K1 findings; K1 must cite the responses
themselves.

## 8. Freeze — 2026-09-03

Nothing above this line is edited after this commit. The digest of this
file at the freezing commit is the study's identity.

**Kill order.** K0 on all eight functions, in P-order, from pinned
documents plus dated primary evidence of spend. Then K1 for every K0
passer, by ascending cost of observation: **P2** (a device duty already
in pinned law) → **P5** (an existing certification market) → **P7** (the
draft Order's text and the notice's intent) → **P1 / P3** (the responses
archive, then OEM and platform public documents) → **P6** → **P4** → **P8**.
K2 only on symptoms whose state is *eligible now*: P1(a), P3(a), P6(a),
each read from the responses archive, with the source's caveats quoted.
K3 only for `measured strain`.

**K0 evidence classes** (v4 §5): **C** exists on its face for P1–P6 as
generic licence duties dated March 2028 on an identifiable budget owner
(every licensee) — but K0 must say, per function, whether the pinned
condition compels *that proof* or only *information on request*; a
function whose only class-C support is Condition 6 is recorded as
"C-weak". **A/B**: named buyers paying third parties, or an identifiable
owner employing people or systems specifically for the function, dated
2025–2026. Recurring vs repeatable recorded, not scored. **The
consumer-agent case** is decided at K0 under P7 from s.4(3K)(b) (a
consumer's own agent is the end-user) and the Class C intent (a
third-party platform with no contract with a trading party or NESO/DNO
service): it fixes whether the agent-platform buyer class exists.

**Falsifiers, restated against pinned text.**
- **F1** The regulations are not laid by 31 December 2026, the requirement
  date moves beyond 31 December 2028, or the regulations are withdrawn.
  As pinned, the date has already slipped one quarter (end-2027 →
  March 2028).
- **F2** The final Order keeps Class C wide enough that independent load
  controllers and consumer-agent platforms optimising against a tariff,
  with no contract with a trading or flexibility-service party, need no
  licence. As drafted, the notice's intent excludes only parties trading
  in wholesale/BM markets, providing services to NESO/DNOs, or contracted
  to such parties.
- **F3** The pinned conditions — information on request (6), annual CAF
  assessment, remedial plan and cyber audit (9.7–9.14), 72-hour incident
  notification (9.16), inspection (9.23–9.26), trusted data sources (10),
  the FSP conduct conditions (11–14), quarterly complaints RFIs and annual
  reports — are satisfiable by the logging, complaints and security
  machinery the OEM clouds, Kraken and its licensees already run. **The
  pinned text already contains no signal-logging, consent-record or
  override-evidence duty**, so F3 is expected to fire for P1–P3 unless
  K1 finds the proof function forced by another route (Ombudsman
  evidence standards, Condition 6 requests in practice, the Phase 2 ESA
  regulations, or buyers demanding it contractually).

**What is scored.** A single mystery, not a batch: the funnel is
reported per function (8 generated → K0 → K1 → K2 → K3), and the study's
output is the profile across the eight dimensions with the branch of
greatest information value named. No threshold is declared; the three
propositions (problem coming; buyer compelled; existing solutions
inadequate) are earned separately or the honest output is a described
problem. Publication waits for the sponsor's seal.
