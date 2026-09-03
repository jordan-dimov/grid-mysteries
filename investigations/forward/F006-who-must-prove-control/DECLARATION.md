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
