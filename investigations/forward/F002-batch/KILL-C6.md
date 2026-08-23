# C6 kill record — prequalification and delivery verification for small flexible assets

**Batch**: 01 (`5f352ebb…`) · **Generator**: v3 (`ab45edbe…`)
**Run**: 2026-08-23, third in the frozen kill order.
**Verdict**: **absorption strain plausible but not measured** →
**downgraded**, not promoted. The frozen forcing observation was run and
returned *eligible instrument, series not published*.

## 1. Existing job

Split, as frozen: aggregators/Capacity Providers submit; the **EMR
Delivery Body** prequalifies; **Delivery Partners** perform Metering
Assessment, Metering Tests and DSR Test validation. Government sets the
Rules and has been actively rewriting them.

## 2. Workflow — and the scarce unit of work

The unit question was pre-declared in `../LESSONS-PENDING.md` (L6) before
this candidate was run. Government answers it directly:

> "Low-capacity DSR CMUs participation requires **considerable
> administrative burden** for Applicants, Capacity Providers, and
> Delivery Partners."

> "there is **no distinction between the information required** for
> components with a very large capacity versus low-capacity components"

So the unit is the **component**, and the information requirement does
*not* scale down with capacity. Asset-count amplification does **not**
evaporate here by default — which is the opposite of what the L6 trap
predicted was likely.

And it is not one-off:

> "Large volume, low-capacity CMU components within aggregated portfolios
> are **likely to change through the Delivery Year**"

Portfolios churn, so verification is **continuous**, not a gate passed
once.

## 3. The decomposition, preserved rather than averaged

The candidate names two functions. They have different economics and are
**not** collapsed into a single verdict:

| | prequalification | delivery verification |
|---|---|---|
| unit | per component, information undifferentiated by size | per CMU test, plus Metering Assessment and Metering Tests on churning components |
| frequency | at entry | continuous through the Delivery Year |
| direction of travel | **being actively reduced** — collation of identical components into one business-model entry; relaxed demand-side metering (NESO Phase 1 Operational Metering Review, Oct 2025); lowered sub-MW eligibility in DFS and Static FFR | **not addressed by capability** — the remedy chosen was a calendar buffer and a penalty |
| named bottleneck | — | Delivery Partners completing **validation processes** |

If strain lives anywhere in C6, it lives in the **right-hand column**.

## 4. Declared strain symptom (frozen, not chosen now)

> Prequalification backlogs; rejection rates rise; metering-assessment
> turnaround lengthens.
> Forcing observation: Capacity Market delivery-body prequalification
> results and timetables.

## 5. Forcing it

**Eligibility (L1) first**: the CM prequalification and delivery-body
process *can*, by construction, contain these events — rejections,
termination notices for missing DSR Test Certificates, and Metering
Assessment turnaround are all things that mechanism produces. **The
instrument is eligible.** That is the first of three candidates for which
this is true.

**What the instrument yields:**

Corroborating, and revealed rather than merely asserted —

- Government states the burden has grown: "This growth has increased
  demands on administrative and processing functions for both DSR
  providers and delivery bodies."
- A named, recurring, material failure: "in recent years there have been
  **significant numbers of Unproven DSR CMUs** which have won T-4
  agreements and subsequently **failed to achieve a DSR Test Certificate**
  ahead of the delivery year."
- Rules changed specifically to relieve queueing: a separation period of
  10 (T-1) / 20 (T-4) working days introduced "to reduce the risk of
  bottlenecks and to provide sufficient opportunity for validation
  activities."
- Respondents sought "increased transparency on the turnaround times" and
  raised delivery-partner capacity.
- The remedy chosen was **administrative and punitive** — buffers plus a
  £5,000/MW TF1 termination fee for failing to provide a DSR Test
  Certificate. Government did **not** adopt sampling, telemetry
  standards, automation or third-party verification.

Contradicting, and substantial —

- The interface **is** being standardised, statutorily and on a
  multi-year plan: the SSES Programme's licensing framework and Energy
  Smart Appliance interoperability specification; time-of-use tariff data
  standardisation with first phase due February 2027; Elexon delivering
  enduring SSES governance through the BSC.
- CM Prequalification 2026 changes are explicitly intended to "reduce
  administrative burdens where appropriate".
- NESO's Routes to Market review is lowering barriers, quarterly.

**What the instrument does not yield: the numbers.** No published series
for DSR Test Certificate failure counts, prequalification rejection
rates, or Delivery Partner metering-assessment turnaround. The
government's own response confirms the absence — it quantifies none of
its own claims.

## 6. Verdict

**Absorption strain plausible but not measured**, and therefore
**downgraded**. Under v3 a candidate may not sit in "plausible"
accumulating research, and this one does not.

The structure is the most interesting seen so far: current burden is
attested at the component level and continuous through the delivery year;
the deployed adaptation is real but largely **lands in 2027**; and the
one function nobody has automated is the one where the bottleneck was
named. That is the *shape* of unfinished adaptation. It is not a
measurement of it, and the distinction is the whole discipline.

**The single observation that would resolve C6**, if it were obtainable:
DSR Test Certificate failure counts and Delivery Partner metering
assessment turnaround times, per prequalification round. Both exist —
NESO/EMR Delivery Body generates them operationally. Neither is published.
C6 is therefore recorded as **blocked on non-public operational data**,
not as a live thesis.

## 7. What this says about the generator

- **First eligible instrument in three candidates** (L1 does not recur).
- **A third instrument outcome appears**: eligible, but the series is not
  published. Distinct from ineligible, and it needs its own name — logged
  as L7.
- **L5 sharpens rather than recurs.** C5 and C1 were adaptation
  *completed*. C6 is adaptation **in flight and racing the load**, with no
  public measurement of which is winning. `AdaptationGap(t)` is exactly
  the quantity that is unobservable here.
- **L6 was pre-declared and was wrong in a useful direction.** The trap
  anticipated that asset-count amplification would evaporate into
  aggregator-level work. Government's own words say the per-component
  information requirement is undifferentiated by capacity — the
  amplification is real, and is only now being deliberately collapsed.

Not acted on.

## Sources (accessed 2026-08-23)

- DESNZ, *Capacity Market: proposals to modernise Rules and improve
  participation and delivery assurance of consumer-led flexibility* —
  government response (GOV.UK).
- DESNZ, *Capacity Market: consumer-led flexibility* call for evidence
  (GOV.UK).
- DESNZ/NESO/Ofgem, *Clean Flexibility Roadmap: 2026 update*
  (`assets.publishing.service.gov.uk`, fetched and extracted locally) —
  CM CLF volumes of 2.6 GW (T-4) and 0.7 GW (T-1) derated; NESO Routes to
  Market review; Phase 1 Operational Metering Review (Oct 2025); SSES
  Programme, ESA interoperability, time-of-use tariff standardisation
  (first phase February 2027); Elexon SSES governance via the BSC.
- NESO EMR Delivery Body Capacity Market pages; Capacity Market Rules
  modernisation response (TF1 £5,000/MW).

**Not used as evidence of demand**: UKRI's June 2026 tender for up to
£25m of consumer-led flexibility innovation funding. Under the F001
signal ladder this sits below `InvestorCapital`, let alone
`BuyerSpend` — it is a grant-maker's belief that a gap exists, not a
buyer paying to close one.

**Retrieval limitation**: GOV.UK material was read through the fetch
tool's extraction rather than pinned by digest, except the Clean
Flexibility Roadmap PDF, which was fetched and its text extracted
locally.
