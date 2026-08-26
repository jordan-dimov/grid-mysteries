# Batch 02 — results

Batch frozen at `4563941874715c0ff1e9a5524c7a6c7ce9ec6501bdcb8ed89db9d48eeb2d2ff4`
(commit `d490e74`) under Generator v4 (`2ac6efa8…`). `BATCH-02.md` is never
edited; results accumulate here. K0: `K0-RESULTS.md`. K1/K2: `KILL-C*.md`.
K3: `K3-C18-DECLARATION.md` (frozen `31d083d`) and `K3-C18-RESULT.md`.

**BATCH 02 CLOSED, 2026-08-26.** Final funnel:

> **10 generated → 8 buyer-real → 6 publicly strain-testable → 1
> absorption failure → 1 measured strain → 0 capturable.**

All K1/K2 work was done on 2026-08-26 by six agents, one per candidate,
each confined to its frozen instrument, and recorded in the frozen order.
The session's web-search budget was exhausted throughout; every record
rests on direct fetches of publisher documents (Ofgem, NESO, Elexon, EA,
HSE, LRQA, legislation.gov.uk, DNO PDFs where reachable, Wayback) and
says so. No instrument was substituted; no candidate was rescued.

## The three answers, kept separate

| # | function | current absorber | absorption status | measured strain (v4 code) |
|---|---|---|---|---|
| **C11** | LV connection quotation at volume | DNO connections teams; ENA Connect & Notify (most domestic chargers and heat pumps never enter the function) | **adequate** — volume designed out; residual segment speeding up; self-serve inside the incumbent; Ofgem: LCT uptake "below projections" | **measured stable (improving)** — GSoP failures 4,000 → 3,860, penalties £2.0m → £1.5m on a higher tariff; time-to-quote −8/−9%, time-to-connect −15/−17%, FY23-24 → FY24-25 |
| **C18** | flexible-asset registration under the market facilitator | per-DNO/NESO market platforms (Piclo, Electron, Epex, Localflex, SMP); Elexon owns the rules since 12 Dec 2025 | **inadequate by the regulator's own finding; externalisation assigned to Elexon (FMAR, Mar 2025) and late**; forcing volume not yet arrived | **measured strain on (b)** — FMAR Q1-2026 milestones missed, consultation slipped to Sept 2026, Ofgem rating 2/5 "Poor" (30 Jul 2026); *the strain is in the replacement's delivery, not the incumbent function's workload* |
| **C14** | demand-pipeline conversion forecasting | DNO DFES (ENWL in-house; NGED via Regen); NESO FES + tRESP (excludes existing applications); Ofgem LRE mechanisms | **adequate** — expanded and partly externalised; nobody forecasts conversion of the existing queue | **measured stable (count)** — LRE re-opener applications 0/1/1/0 across four windows; one adverse determination (SSEN, £723m sought, Ofgem: DFES-driven timing "not sufficiently evidenced against … connection pipelines"); FES data-centre range 8 → 20 TWh |
| **C16** | MCP/SG permitting and compliance for standby fleets | operators; air-quality consultancies (EA-directed since 2019); EA three-tier permitting | **adequate** — simplified (6 of 9 standard-rules sets withdrawn), fees +26%, backlog of 1,000 cleared; **forcing variable arrives 1 Jan 2029**, and Defra is consulting on replacing permits with registration | **measured stable (proxy)** — EPR-wide timeliness rose across all four measured quarters; weak, non-attributable uptick in low-category breaches per assessed MCP/SG permit (0.14 → 0.26) |
| **C19** | HV authorisation at private networks | operators' APs, an Authorising Engineer (in-house or bought), contractors' APs under COMA — codified NHS 2006, MOD 2009 | **adequate — already externalised ~20 years** (one AE supplier incorporated 1996) | **measured stable (proxy)** — HSE electrical-contact injuries flat, population unresolved; public AE market 0–4 notices/yr, no outsourced switching-operation contracts |
| **C17** | contestable 33/132 kV works by ICPs | NERS ICPs/IDNOs + DNO businesses under the CiC Code of Practice (2015) | **adequate — already externalised** (competition since 2000; 132 kV-scope providers 75 → 242, 2015–2025) | **measured stable (register)**; ICP lead time and adoption time uninstrumented; DNO time-to-quote at HV/EHV fell in 3 of 4 published series |

## The funnel

| stage | count | candidates |
|---|---:|---|
| generated | 10 | C11–C20 |
| quarantined — adjacency (K0 not run) | 2 | C13, C20 |
| instrument: eligible now / proxy only / none | 3 / 3 / 2 | C11, C14, C18 / C16, C17, C19 / C12, C15 |
| K0 buyer-real | **8 of 8** | A: C17 (+C16) · B: C14, C19 (+C18) · C: C11, C12, C15, C16, C18 |
| quarantined — buyer-real, not publicly strain-testable | 2 | C12, C15 |
| reached a measured K1/K2 verdict | **6 of 6** run (3 on eligible-now instruments, 3 on declared proxies) | C11, C18, C14 / C16, C19, C17 |
| **K1 absorption inadequate** | **1** | C18 (regulator-declared; externalisation assigned and late) |
| of which *already externalised* (late) | 3 | C17 (2000/2015), C19 (~2006), C18 (assigned 2025, undelivered) |
| **K2 strain measured** | **1** | C18 — located in the replacement's delivery |
| **K3 capturable** | **0** | C18 killed at K3: strain is a delivery problem inside a funded, licence-backed Elexon programme with a supplier RFP in flight; no participant pays a third party to bridge it; every unmet function was absorbed as an FMAR rule or backlog item; residual out-of-scope functions have a buyer base of tens of FSPs and no observed purchase |

**Read:** 10 generated → 8 buyer-real → 6 publicly strain-testable → **1
absorption failure → 1 measured strain → 0 capturable.**

## Scoring against the pre-declared thresholds (BATCH-02.md §6)

- **P(buyer-real | generated) = 8/8** ≥ 6/8. **Met.** v4 preserved
  forced-function generation.
- **Instrument quality** = candidates reaching a measured K1/K2 verdict ÷
  candidates passing K0 = **6/8 = 0.75** ≥ 0.5. **Met** — with a
  definitional caveat recorded honestly: three of the six verdicts are on
  *declared proxies* with their inferential gap written into the record
  before the kill. Counting only eligible-now instruments the ratio is
  3/8 = 0.375, identical to Batch 01's replay. The threshold was declared
  without saying whether proxy-measured verdicts count; the v4 verdict
  codes treat them as "measured", so the pre-declared reading is 0.75, and
  the ambiguity is logged (L15) rather than resolved after the fact. What
  is not ambiguous: every one of the six returned a verdict *with its
  reason*, and none was "plausible but not measured".
- **Generator quality** = (K1 inadequate or K2 strain) ÷ measured =
  **1/6**. Reported, no threshold declared.
- **Conversion rates** (cross-batch record): P(buyer-real | generated)
  8/8; P(absorption inadequate | buyer-real, testable) 1/6; P(measured
  strain | inadequate) 1/1; P(capturable | strain) 0/1.

## Descriptive only: absorption failure by K0 class (n tiny)

| K0 class | candidates run at K1/K2 | absorption inadequate |
|---|---|---|
| A (external spend) | C17 | 0/1 |
| B (internal spend) | C14, C19 | 0/2 |
| C (obligation), incl. C+A / C+B | C11, C16, C18 | 1/3 (C18, which is also B) |

Nothing can be concluded from six observations. Recorded so the series
accumulates.

## What Batch 02 says about v4 — observations, not changes

1. **The forced-function generator survived.** 8/8 economic owners, 10/10
   incumbent guesses right again (every absorber named in the frozen row
   was found performing the function).
2. **Commercial scarcity begins at absorption, and the dominant absorption
   mode is "already externalised".** Three of the six testable candidates
   had left the incumbent years or decades ago (C17, C19) or been assigned
   to a named body by the regulator (C18). The P6 question ("has this
   function already left the incumbent, and when?") earned its place in
   its first outing.
3. **The one measured strain is in an adaptation in flight**, exactly the
   C6 shape from Batch 01: a replacement with an owner, a budget and a
   regulator scoring it "Poor". K3 asked whether that creates capturable
   demand and found that it does not: the distinction between *measured
   strain* and *commercial opportunity* is now a recorded result, not a
   principle.
4. **Forcing variables were mostly not yet present in the instruments**:
   LCT uptake "below projections" (C11), sub-1 MW flexibility volumes small
   (C18), standby-fleet deadline 2029 (C16), M1 clocks 2027 (C2 in Batch
   01). The generator finds forced functions ahead of the force arriving —
   which is the point of a forward track, and also why measured strain is
   rare.
5. **Instrument blindness fell from "8 of 10 froze an unobservable
   symptom" to "0 of 6 returned unmeasured".** The gate did its work, and
   it did it without touching outcomes.
6. **The generator is often early, and that is not a defect** (L17). The
   objective is closer to P(eventual commercially relevant strain |
   generated early enough to act), which only the dated re-observations
   below can accumulate. A low measured-strain rate is not, by itself,
   generator failure.
7. **Next batch declaration must report direct measurability and
   direct-plus-proxy screenability as two rates** (L16), never one
   "instrument quality".

## Closure

Batch 02 is closed. None of the other five K1/K2 candidates is reopened;
their dated re-observations are watches, not unfinished investigations.
C12 and C15 remain *buyer-real, not publicly strain-testable*. C13 and
C20 remain adjacency quarantines. Generator v4 is unchanged; L15–L17 are
logged for the BATCH-03 declaration.

## Dated reassessment points carried forward

- C18: Ofgem's next FMAR review, early October 2026; FMAR consultation
  September 2026; go-live target 30 Sept 2027.
- C14: SSEN LRE final determination, Q3 2026; January 2027 re-opener
  window.
- C16: Defra decision on registration vs permitting; MCP 1–5 MWth
  deadline 1 Jan 2029.
- C11: Ofgem ED annual report FY2025-26, expected ~Jan–Apr 2027; NGED LCT
  connection counts if access is granted.
- C17: any DNO's 2025-26 Major Connections Annual Report.
- C12, C15 (quarantined): Ofgem's promised derogation register; any DNO's
  demand-side curtailment series.

## Retrieval limitations, batch-wide

Web search unavailable for the whole batch; DNO websites (NGED, NPg, SPEN,
UKPN), ENA, Regen and several trade sites returned 403; Contracts Finder
keyword search unusable without a session; NGED's LCT connection counts
are access-gated. Each record names what it could not reach. The bias is
toward first-party regulator and operator publications and away from
practitioner testimony; for K1/K2 that is the right bias, and it is
stated rather than hidden.
