# C7 — outage and access planning coordination across the TO/DNO boundary

**Batch**: 01 (`5f352ebb…`) · **Generator**: v3 (`ab45edbe…`)
**Run**: 2026-08-23, fourth in the frozen kill order.
**Verdict**: **absorption strain evidenced.** First in the batch. Measured,
monotonic over three years, published by the incumbent, and acknowledged
by it in its own words.

## Eligibility, settled before any number was retrieved

Pre-declared in `../LESSONS-PENDING.md`: **outage-related constraint cost
is ineligible for this hypothesis.** It measures whether an outage was
economically consequential, not whether the workflow that planned it is
overloaded. UKERC's 2026 piece on transmission unavailability confirms
the trap is live — it *asks* whether outages "could be arranged... such
that key circuits were more available in periods of high wind and high
expected constraint costs". That is a research question, not evidence of
coordination failure, and it was not used as one.

The eligible instrument is **NGET's annual Network Access Planning
KPIs**, published under the GB Network Access Policy, which measure "the
TOs capability to construct and deliver a robust outage plan".

## The measurement (NGET, all figures from its own KPI publications)

| KPI | FY22 | FY23 | FY24 |
|---|---|---|---|
| 1a Outages in year-ahead plan | 1,914 | 2,155 | 1,810 |
| 1b YA outages delivered | 1,164 | 1,085 | 838 |
| **1c % of YA plan delivered** | **61%** | **50%** | **46%** |
| 2a Started on the agreed date | 32% | 26% | 25% |
| 2b Started in the agreed week | 39% | 31% | 30% |
| 2c Changed for a *positive* reason | 10% | 7% | 5% |
| 4 Assets out of service >1×/year | 1,157 | 1,181 | **2,846** |
| 6 Started within 60 min of agreed time | 53% | 44% | 45% |
| 8 Non-firm access curtailed by outages | — | 0% | **3.62%** |
| 12 In-service works | 953 | 508 | 448 |

NGET's own commentary: *"delivering these outages in accordance with the
plan has dropped. In FY24 we delivered 46%"*, and the drops in start-date
and start-week adherence are stated explicitly.

**The strain is not fault-driven.** System faults *fell* over the period
(260 → 64) while other unplanned outages rose (173 → 350). So the decline
in plan adherence is not explained by more equipment breaking — which is
the ordinary-engineering confounder the eligibility test required be
separable.

## The system of record cannot see itself

Two KPIs are unreportable because of the tool that runs the process:

- KPI 3 (new within-year outages, by phase) — *"Due to issues in the data
  from ESO's Outage Management tool (ENAMS), this KPI will not be
  published for this financial year."*
- KPI 5 (outage coordination / work bundling) — *"Due to the nature in
  which NGET records information in Outage management tool (ENAMS) it
  cannot be reported in a volumetric way."*

The measure literally named **"Outage coordination"** is the one the
coordination system cannot produce. That is a cross-organisational
data-quality failure in the workflow's own instrument, and it is the
`cross-organisational` + `data-intensive` force appearing as a defect
rather than as a description.

## Verdict

**Absorption strain evidenced.** Plan adherence fell 61% → 50% → 46% over
three years while positive-reason changes also fell — the churn is not
optimisation, it is slippage. Access curtailment for non-firm connections
went from zero to 3.62%. Repeat outages on the same assets rose 2.4×. The
incumbent publishes this, acknowledges the direction, and cannot report
two of its own coordination KPIs because the shared system does not hold
the data well enough.

Under project doctrine this is the case that survives the kill: required
coordination work is growing and delivery capacity is visibly not keeping
pace.

**What is not established**: that this is externalisable. The buyer is a
regulated monopoly with in-house planners and a live reform programme
(System Access Reform, targeting >80% of planned outages inside a 6-year
rolling plan; eNAMS already deployed). Propositions 2 and 3 are unearned.
That work is deliberately not done here.

## Sources (accessed 2026-08-23)

NGET, *Network Access Planning Key Performance Indicators*, July 2023
(FY23 data) and July 2024 (FY22–FY24 series), fetched from
`nationalgrid.com` and extracted locally. *GB Network Access Policy*
(NGET/NGESO). NESO Network Access Planning, eNAMS and System Access
Reform pages. UKERC, *Transmission Network Unavailability* — cited only
to show the trap, not as evidence.

---

# Correction, 2026-08-23 (same day, before publication)

Three claims in the record above are withdrawn. Two were my errors; one
is superseded by data I have not been able to obtain.

## 1. The faults argument is invalid — withdrawn

I wrote that the decline "is not fault-driven" because system faults fell
260 → 64. **NGET says the fall is an artefact of its own recording
change**, in the same document I read:

> "between FY23 and FY24, we have changed how we record faults and
> unplanned outages in ENAMS. We now record fault outages for those
> assets that have been switched out by automatic operation. This change
> in approach has driven the reduction in number of system faults
> reported in FY24 and the increase in unplanned outages."

I extracted the KPI table and did not read the commentary beneath it.
The ordinary-engineering confounder is therefore **not** separated, which
was the load-bearing step of the eligibility argument. Withdrawn
entirely.

## 2. The 2,846 figure is superseded — withdrawn

Reported as repeat asset removals rising 2.4×. NGET is understood to have
revalidated FY24 to 1,480, with FY25 falling to 640. I could not obtain
the source document (see §4), so the figure is withdrawn rather than
restated.

## 3. The 3.62% non-firm curtailment is withdrawn

It applies to very few sites, and is understood to fall to 0.09% in FY25
on a single 8.17-hour outage. It was the weakest link when written and
should not have been included.

## 4. FY25 data exists and I could not verify it

A later KPI publication reportedly shows year-ahead plan delivery
recovering to 50%, exact-date starts to 28%, and within-year requests
rising sharply (delivery-phase 1,438 → 2,184). **I could not locate or
fetch that document**, and the citation offered for it resolves to the
July 2024 publication, which cannot contain FY25. These figures are
therefore **neither used nor relied upon**, and the phrase "monotonic
over three years" is withdrawn as unsafe.

## Verdict after correction

**Held at absorption strain evidenced, but re-based on different
evidence.** It no longer rests on a trend in NGET's adherence KPIs. It
rests on NESO's own published description of the workload, which I
fetched and verified verbatim:

- a typical final year-ahead plan contains **~2,500 outages**;
- NESO then processes **over 17,000 TO outage changes** to that plan in a
  typical year — ~7,500 in Optimisation timescales, ~10,000 in Delivery;
- **"Any outage changes received following the initial TO submission
  means the NESO detailed outage assessment needs to begin again."**;
- the work is done by **a team of 65 engineers**;
- NESO states the system "has become increasingly complex over recent
  years as we decarbonise... resulting in not only an increased workload
  but also an increased interaction between outages."

That is the incumbent describing rising required work against a named,
finite team, with a restart-on-change process — direct, first-party, and
not dependent on any inference I made. The verified KPI 5 defect stands:
the metric named "Outage coordination" cannot be reported volumetrically
because of how eNAMS records the data.

**Lesson, recorded once and not elaborated**: I read a KPI table and not
the commentary that qualified it. Cheap forcing observations must include
the source's own caveats, or the instrument is being misread rather than
merely mis-chosen.

---

# FY25 data obtained and verified, 2026-08-23

Source: *Network Access Planning KPIs*, National Grid, **July 2026**
(FY25 / T2Y4), supplied directly. Every disputed figure is confirmed.

| KPI | FY22 | FY23 | FY24 | FY25 |
|---|---|---|---|---|
| 1a Outages in YA plan | 1,914 | 2,155 | 1,810 | 2,055 |
| 1c **% of YA plan delivered** | 61% | 50% | 46% | **50%** |
| 2a Started on agreed date | 32% | 26% | 25% | **28%** |
| 2b Started in agreed week | 39% | 31% | 30% | **35%** |
| 2c Changed for a positive reason | 10% | 7% | 5% | 6% |
| **3a New within-year, pre-Optimisation** | – | – | 470 | **711** (+51%) |
| **3b New within-year, in Optimisation** | – | – | 928 | **1,253** (+35%) |
| **3c New within-year, in Delivery** | – | – | 1,438 | **2,184** (+52%) |
| 4 Assets out >1×/year | 1,157 | 1,181 | **1,480** (was 2,846) | 640 |
| 5 **"Outage coordination"** | – | – | – | **– (still unreportable)** |
| 6 Started within 60 min | 53% | 44% | 45% | 43% |
| 8 Non-firm access curtailed | 0% | 0% | 3.62% | 0.09% |
| 10a System faults | – | 260 | 64 | 81 |

**All three withdrawn claims are confirmed withdrawn.** KPI 4's FY24
value is footnoted as corrected from 2,846 "following discovery of
discrepancy in how we reported this". The 3.62% arose from a single
busbar outage at Kemsley on a measure that "applies to only a very
limited number of sites". Faults rose 64 → 81, on top of the FY24
recording change.

**And the trend claim is confirmed wrong in the direction I had it.**
NGET: "delivery rose to 50% of the YA plan in FY25, up from 46%… 28% of
outages started on the agreed date and 35% started in the agreed week…
**reversing the prior decline**."

## The real finding, which is better than the one I withdrew

The year-ahead plan is **improving** while the rate of change against it
is **accelerating**. Within-year requests rose in every phase, most in
the shortest-notice one:

> "In FY25, within-year outage requests increased across all phases
> compared with FY24: prior to the Optimisation Phase they were about 51%
> higher, during the Optimisation Phase they rose by about 35%, and
> during the Delivery Phase they were about 52% higher."

NGET names the drivers — "network security, asset faults, and external
drivers such as customer requests" — and states the remedy is
"enhancements to plan build and coordination through planning
transformation… reducing those emerging within year". It also says
outright that it is "undertaking planning and delivery transformation
programmes" continuing into RIIO-T3.

Two further verified details:

- KPI 5 remains blank for all four years: work bundling "cannot be
  reported in a volumetric way" because of how eNAMS records it — though
  NGET states **91% of its outages have more than one piece of work
  planned**.
- KPI 6 fell to 43%, and NGET attributes it to "complexities we have
  coordinating outage releases across multiple stakeholders… These
  complexities of stakeholder coordination have existed in each of the
  four years of T2."

## Verdict, final

**Absorption strain evidenced**, now on fully verified first-party
evidence and a *sharper* mechanism than originally claimed: **replanning
volume is growing faster than the plan is improving.** NESO processes
>17,000 changes against a ~2,500-outage plan with 65 engineers, every
change restarting assessment; NGET's own within-year request counts rose
~51%/35%/52% in a single year, most steeply inside the final three weeks.

Both institutions are adapting and say so. This is an adaptation race
with a measured numerator, not a failure. Propositions 2 and 3 remain
unearned and are not attempted.
