# F006 — K0 Buyer Reality, all eight functions

**Declaration frozen at** `b4109419e7c3d15e6aa26f302e6cb14182491c9cd1da72f95a86f7861143bb34`
(commit `9b6b491`). **Run**: 2026-09-03, after freeze. Evidence: the
public-as-of pins (`evidence/public-as-of-manifest.json`, **68**
artefacts — §6 of the declaration says 61, a count taken before the last
pins; corrected here, the frozen file untouched) and the kill-phase pins
(`evidence/kills-manifest.json`; two refusals in
`evidence/kills-unavailable.json`: one self-signed certificate at
flexassure.org.uk, one 404 at theade.co.uk, not retried by other means).
The Ofgem responses archive was opened for the first time in this phase.

K0 asks one thing: does the function have an identifiable economic owner
today? **A** external spend · **B** internal spend by an identifiable
owner · **C** dated hard obligation. Per the freeze, a class-C reading that
rests only on Condition 6 (information on request) is marked **C-weak**.

| # | function | class | dated primary evidence | recurring / repeatable | verdict |
|---|---|---|---|---|---|
| **P1** authorisation & bounds | **C-weak** | No pinned condition requires consent or bounds evidence per signal. What exists: Condition 12.3 (principal terms clear before and after contract); Schedule 2 of the draft regulations bringing FSPs under the Complaints Handling Standards Regulations 2008 and the Redress Scheme Order; Ombudsman ADR for licensees from March 2028 (government response 2026) and, since 8 January 2026, for Flex Assure domestic members (`ombudsman-adr-fsps-news`); Condition 6. A vendor markets "a CRM as their system of record showing that consumer consent … managed in a secure, auditable cloud platform" (Salesforce response, 2026) — `ProvisionExists`, not spend. | recurring (complaints) | **PASS (C-weak)** — the owner is compelled to *answer complaints*, not to *prove each signal* |
| **P2** override | **C** (on the device maker) | SI 2021/1467: a chargepoint must let the owner override default charging hours and "override the provision of demand side response services", in force 30 June 2022; ESA Phase 1 extends override to heat and batteries from 31 December 2027. For controllers the licence carries only guidance ("FSPs *should* provide the option", Annex D); the Energy Ombudsman and Flex Assure both asked for "must" (responses, February 2026). | per product | **PASS (C)** — owner is the OEM, since 2022 |
| **P3** reconstruction | **C-weak** | Condition 6 (information "when and in the form requested"); complaints regime (8-week rule to Ombudsman); inspection 9.25(d) — cyber scope only; quarterly RFI on complaints *type and volume* (Ofgem decision Table 4) — aggregate, not per device. | recurring (quarterly) | **PASS (C-weak)** |
| **P4** settlement attribution | **C + B**, market level only | NESO DFS procurement rules (10 August 2026 document, rules effective 9 April 2026): P376 baseline retained for domestic participants; weekly settlement submissions by the provider; MHHS makes every household half-hourly settled by May 2027. Provider settlement teams are the owner. **No condition or rule owns household-level attribution** of a bill outcome to a controller's action. | recurring (weekly) | **PASS, narrowed** — owner exists for market settlement; none for the household |
| **P5** cyber baseline | **C** (strong) + **A** (voluntary) | Condition 9.7 annual CAF Assessment, 9.9 remedial plan, 9.13 annual cyber audit "or an equivalent", from March 2028 with an 18-month implementation period (government response 2026); at application from 1 March 2027 a CAF self-assessment and statement of intent (Ofgem decision §6.30); ≥ 300 MW: NIS designation via the CSR Bill "around Autumn 2027", assurance grace to "year end 2029". Class A today: Flex Assure independently audits members — **2 of the 12 domestic DFS registered providers** (Electric Miles, Shuffle Energy) carry the mark on NESO's list updated 25 August 2026 (`neso-dfs-registered-providers-list`); Axle, Octopus, British Gas, Equiwatt, Hildebrand and others do not. | recurring (annual) | **PASS (C)** |
| **P6** aggregate-load accounting | **C** | Condition 9.6: notify the Secretary of State within three months of controlling ≥ 300 MW; annual RFI "on load capacity, device types and volumes" (Ofgem decision Table 6). OVO's response: cumulative load across a corporate group's several licensees "could easily exceed 300MW" while each stays below — a definitional gap the government response acknowledges. | recurring (annual) | **PASS (C)** |
| **P7** exemption boundary | **C** for market-facing controllers; **none** for tariff-only agents | s.4(1)(g) offence from March 2028 forces every controller to determine its status. **The consumer-agent case, decided from the pinned text**: (i) a consumer's *own* agent on the consumer's own devices — the consumer is the end-user, s.4(3K)(b): no licence, no exemption needed; the DESNZ consultation says organisations "providing the user interface" are not licensed either. (ii) A third-party agent platform that creates or changes signals is a load controller **unless** Class C applies; the notice's intent is that Class C fails only where the entity trades in wholesale/BM or imbalance markets, provides flexibility services to NESO or DNOs, or holds a contract with such a party "in relation to the use of the load control in question". A tariff-only agent platform with no such contract is exempt as drafted; the same platform enrolling customers in DFS is not. The Startup Coalition's warning that dynamic wholesale-price optimisation "may be captured" while simple TOU response "may fall outside" is recorded as the live ambiguity. | one-off (status) | **SPLIT** — PASS (C) for the Axle/Octopus class; **FAIL** for tariff-only agent platforms (no obligation, so no buyer) |
| **P8** portability | **C-weak** | Condition 13.2 (must not unduly prevent switching); annual switching RFI (Ofgem Table 6). Octopus: "Reporting on switching may be difficult given the lack of standardised industry processes"; Octopus's own FAQ: a customer with third-party control "can't be on Intelligent Octopus Go at the same time" (`octopus-iog-third-party-control-faq`). | recurring (annual) | **PASS (C-weak)**; no public instrument → quarantined after K0 |

**Funnel after K0**: 8 generated → 7 buyer-real (P7 split: one class in,
one out) → 6 proceed to K1/K2 (P8 quarantined *buyer-real, not publicly
strain-testable*; resolving observation: Ofgem's annual switching RFI
outputs, held by Ofgem, or the ESA Phase 2 interoperability regulations
planned for 2027).

**The consumer-agent buyer class**, answered as the sponsor asked: it
exists as a *licensee* only where the agent's operator also sells the
household's flexibility into a market or to a network. A platform whose
agents optimise purely against the household's tariff — the shape of the
Bloomberg Kent case — is outside the licence under Class C as drafted, and
the household's own agent is outside it by statute. **Falsifier F2 fires
for that sub-class.** Whether the final Order keeps Class C as drafted is
a dated watch (representations closed 7 September 2026).
