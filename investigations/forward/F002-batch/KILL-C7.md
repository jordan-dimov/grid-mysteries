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
