# C18 kill record — registering and maintaining flexible-asset data across DSO and ESO markets under the market facilitator

**Batch**: 02 (`45639418…`) · **Generator**: v4 (`2ac6efa8…`)
**K0**: PASS, class C + B (licence obligations on DNOs/NESO; BSC-funded Elexon programme).
**Instrument state at gate**: eligible now via (b); (a) eligible later; (c) proxy.
**Run**: 2026-08-26, second of six in the frozen K1/K2 order.

**K1 — current absorber**: each DNO's flexibility team on its contracted
market platform (Piclo, Electron, Epex, UKPN Localflex, NGED in-house)
plus NESO's Single Market Platform, with FSPs/aggregators carrying the
multiple-entry burden. Elexon owns the rulebook (Flexibility Market
Rules, go-live 12 Dec 2025), not today's registration operation.
**K1 — absorption status**: **INADEQUATE by the regulator's own finding,
and already externalised on paper** — Ofgem assigned a common register
(FMAR) to Elexon in March 2025 — **but not delivered**; the forcing
variable (sub-1 MW asset volume in DSO markets) has not yet arrived.
**K2 — measured strain**: **MEASURED STRAIN on symptom (b)** — FMAR
milestones slipped ~two quarters; Ofgem rated FMAR 2/5 "Poor" (30 Jul
2026) — with the caveat that the strain is in Elexon's delivery of the
*replacement*, not in the incumbent registration function's workload.
(a) **not yet observable** (FMAR go-live target Sept 2027). (c)
**unmeasured — instrument ineligible** (SLC 31E reports carry no
registration attribution).

Research performed by a background agent under the v4 kill discipline;
the record below is its report, unedited except for this header.

## 1. Current absorber

**Registration is performed per System Operator, on that SO's contracted
market platform, with the data entry done by the FSP/aggregator.**

- [V] FMAR Day 1 minded-to position (Elexon, 23 Jun 2026): "In the initial
  scope, FMAR will only integrate with the following platforms … NESO:
  Single Market Platform (SMP); Market Platforms: Piclo, Electron, Epex
  Spot and Market Gateway (NGED's in house platform)"; "FSPs who use UIs to
  register will continue to register assets on existing registration
  platforms".
- [V] SLC 31E 2025-26 reports (Ofgem, 22 Jun 2026): Northern Powergrid "We
  replaced our previous Dispatch and Settlement platform so that FSPs now
  experience a single end-to-end market platform, Piclo, from commercial
  qualification and asset registration through bidding to dispatch and
  settlement"; SPEN via Piclo and Electron DPS; UKPN "Our tendering platform
  Localflex, also provides direct support for FSPs to be onboarded"; SSEN
  "asset registration and registration on our dispatch and payment
  platforms".
- [V] What Elexon has taken over — self-assessment 2025-26 (Ofgem Annex B,
  30 Jul 2026): handover from ENA Open Networks; governance documents
  uploaded 1 Dec 2025, "formal Go-Live on 12 December 2025"; inherited
  products are now Flexibility Market Rules (FMR-PQC, FMR-PD, FMR-PR,
  FMR-SBM, FMR-VSM, FMR-E2E …); "Dispatch API – the handover of this work
  from the ENA was delayed due to needing further refinement and
  additional assurance". None is an operational registration service.
- [V] The externalised solution is decided but not built: "In its March
  2025 decision on FMAR, Ofgem confirmed the introduction of a common
  registration framework and associated digital infrastructure"; "Ofgem
  has appointed Elexon to deliver Flexibility Market Asset Registration";
  Day-1 "(September 2027)"; "The register will initially focus on smaller
  scale assets (under 1MW)"; formal design consultation "in September
  2026".
- [V] Aggregators' burden: stakeholders find "integration with different
  platforms for asset submission to be challenging … lack of confidence in
  the robustness of System Operator registration platform APIs"; UI
  re-entry "not feasible, particularly for hundreds of small-scale
  assets". Ofgem: "FSPs and asset operators are often required to register
  the same asset data multiple times across different local and national
  flexibility markets".

## 2. Absorption status

**Inadequate by regulator's finding; externalisation already assigned
(Elexon/FMAR, March 2025) but not delivered; forcing variable not yet
arrived.**

- **(i) Already externalised — on paper.** [V] The market has answered
  "who will own this"; the candidate's space is bounded by FMAR's scope,
  and the minded-to keeps "one single platform for market entry" *out* of
  Day-1 ("will not be included in the existing scope for FMAR Day-1; but
  will be kept under review").
- **(ii) Forcing variable not yet arrived.** Volume evidence: [V] SLC 31E
  2024-25 (6 Oct 2025): ENWL "tendered for 486.4MW … accepted … 47.28MW";
  UKPN TR11 "tendering 226MW and awarding 23MW"; SPEN "151.4 MW … 24.7 MW
  procured"; NPg "3.9MW". SLC 31E 2025-26 (22 Jun 2026): ENWL "tendered for
  1588MW … capacity contracted of 8.059MW"; SPEN "tendered 710MW" (prior
  year 146.37 tendered / 24.20 contracted); NPg 96 MW tendered; UKPN 5.07
  + 25.02 MW contracted. Tendered volumes rising 3–5× y/y while contracted
  volumes remain single-digit to tens of MW per DNO. **Registrations may be
  increasing; the contracted base to maintain is small.** SSEN: day-ahead
  eligible FSPs "from 1 to 11. While two FSPs have actively participated so
  far". No DNO publishes a count of registered assets [N].
- **(iii) "Inadequate" is the regulator's declared premise, not a measured
  breakdown.** [V] Ofgem "identified the registration and onboarding
  process for small-scale flexibility assets as a key barrier to market
  participation". But DNOs report *improving* absorption: SSEN "enhanced
  our approach to onboarding … helped to fast-track asset registration";
  NPg consolidated onto one platform "reducing the effort and complexity
  for FSPs". No DNO reports a registration backlog or onboarding-time
  metric.
- **(iv) Strain exists on the *reallocation* sub-function.** [V] Reviewed
  delivery plan (16 Jul 2026): "Enable consistent re-allocation of assets
  between FSPs — Acceleration of activity — Strong industry pull for
  intervention; current blocker to access"; workshops 27 Jul / 4 Aug 2026:
  "Processes for reallocating assets can vary across markets and
  platforms. This can create uncertainty about which provider is
  responsible for an asset". This is the one place where cross-
  organisational absorption is visibly failing today.

## 3. Measured strain

### (b) Delivery-plan diff — original (Dec 2025) vs "Reviewed July 2026"

Artefacts [V]: original plan (PDF created 2025-12-18, 31 pp, sha256
`a017b37c…`); reviewed (2026-07-16, 24 pp, sha256 `63a72e53…`).

| Item | Original | Reviewed | Movement |
|---|---|---|---|
| FMAR design consultation | "consultation in Q1 2026" | "FMAR Q3 consultation"; O3.2 Working groups → Consult → Decision → "Initial build" by Dec-26 | **~2 quarters later**; web page: "September 2026" |
| FMAR early implementation | "may start in late 2026" | "Design, build & test release 1" spans 2026 | "subject to uncertainty" |
| FMAR go-live | "By 30 September 2027" (Ofgem objective) | unchanged | held; Elexon: "we cannot put dates to the critical path" |
| DNO procurement & dispatch data frequency | decision late June 2026 | "delayed to early August" — "avoid conflicts with industry consultation and key reporting deadlines" | +~6 weeks |
| Dispatch API (DNO and NESO) | Q1–Q2 2026 | "timings TBC"; "Scope, requirements and testing approach are still being replanned … Treat timings as uncertain" | TBC |
| Enable capacity release | activity | **removed** — "Uncertain value / dependencies on future work" | dropped |
| Asset re-allocation | separate activity | **accelerated** — "Strong industry pull … current blocker to access" | earlier |
| Register churn | — | "22 changes, 11 new items and two items maintained without change" | — |

Elexon's stated reasons [V]: "Ofgem feedback highlighted the need to be
more strategic; Open issues necessitated validating and replanning
selected workstreams; Concerns were raised at the Stakeholder Advisory
Board … ; Stakeholder input, including through FMAR, added new evidence;
The initial months of delivery revealed new practical insight." Caveats:
"This reprioritisation is not a one-off"; "Timelines are dependent on
industry availability"; "External Support: Support being onboarded across
several activities".

**Ofgem's independent measurement of the same slippage** [V]:
- Q1 2026 performance report (22 Apr 2026): FMAR "weak"; "several key
  milestones have been missed and we have yet to see a full end-to-end
  project plan"; "these delays come from Elexon operating with significant
  resourcing and capability gaps over the course of 2025"; "the delays
  incurred do not appear to have been communicated clearly or
  transparently".
- Annual performance assessment 2025-26 (30 Jul 2026): Market Facilitator
  (excl. FMAR) **4/5 Good**; FMAR **2/5 Poor** — "Several key deliverables
  remain incomplete, important elements of the Day 1 solution are still
  under development, and stakeholder confidence in the programme remains
  low"; survey confidence 2.3/5, "8% agree … 38% disagree"; "timelines are
  arbitrary, having been set before scope and delivery approaches were
  fully defined"; Elexon "not yet appropriate to assign firm dates across
  the programme". Next review "early October".
- Elexon self-assessment: "Until recently, it has not been clear that
  adequate capability / capacity was being assembled for the delivery of
  FMAR"; now considering "staggered implementation options".

Trackers [N]: Power BI embeds, not fetchable; Baseline Statement V2.0
body not exposed.

### (c) SLC 31E under-subscription and attribution

Under-subscription is visible as tendered ≫ contracted (ENWL 1588 MW vs
8.059 MW; SPEN 710 MW vs prior 24.20 MW). [V] **No DNO attributes any of it
to registration or onboarding.** NPg's FSP feedback on non-participation:
"They need to develop a better understanding of their asset portfolio …
They need to develop a new product/software offering to onboard their
customers … Their assets are too small, or are located outside of areas
where we are seeking flexibility" — asset readiness and geography. Vintage
correction: the 2025-26 SLC 31E set was published 22 Jun 2026 (the gate
recorded 2025-10-06 as latest).

### Verdict codes

- **(b) MEASURED STRAIN** — FMAR Q1-2026 milestones missed (Ofgem 22 Apr
  2026), consultation moved to Sept 2026, FMAR 2/5 Poor (30 Jul 2026),
  Dispatch API "timings TBC". **The strain is in Elexon's delivery
  capacity and scope stability, not in the registration function's
  workload.** Non-FMAR market-facilitator work rated Good.
- **(a) NOT YET OBSERVABLE** (FMAR consultation Sept 2026; go-live Sept
  2027; no DNO publishes onboarding-time series).
- **(c) UNMEASURED — INSTRUMENT INELIGIBLE** (no registration attribution;
  DNOs report onboarding improving).

**Distinction preserved:** registrations/tenders are increasing (tendered
MW up 3–5× y/y at ENWL and SPEN); the *registration function* shows no
measured strain; the measured strain is in building its replacement. The
one live absorption failure with "strong industry pull" is **asset
reallocation between FSPs across platforms**, accelerated by Elexon in
July 2026.

**K1: inadequate (regulator-declared), externalisation assigned and late.
K2: measured strain (b), located in the replacement's delivery.** This is
the C6 shape — adaptation in flight, racing the load — with the
difference that the adaptation has an owner, a budget and a regulator
scoring it. K3 would have to ask what is left once FMAR exists; not
attempted here.

## Failed / not obtained
Ofgem site search (JS); Power BI trackers; Baseline Statement V2.0 Excel
path; SSEN and NGED 2025-26 headline MW (texts retained); FMAR minded-to
Miro flows (password-gated); Ofgem FMAR decision (March 2025) and
Governance Framework Document not fetched directly.
