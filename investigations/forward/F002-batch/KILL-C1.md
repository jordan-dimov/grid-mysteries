# C1 kill record — half-hourly settlement data quality assurance for suppliers under MHHS

**Batch**: 01 (`5f352ebb…`) · **Generator**: v3 (`ab45edbe…`)
**Run**: 2026-08-23, second in the frozen kill order.
**Verdict**: **absorption stable**, on the absorber's revealed investment.
The steady-state load test is **not yet eligible** and this record does
not claim to have run it.

## 1. Existing job

The function is **code-mandated and institutionally owned**. Elexon's
Performance Assurance Framework exists precisely to assure that energy is
allocated between Suppliers correctly, that Suppliers and Supplier Agents
transfer metering data accurately, and that trading charges are
calculated to BSC requirements. PARMS serials measure the processes;
PARMS data comes from Supplier Meter Registration Agents and the Supplier
Volume Allocation Agent. There is a Performance Assurance Board, an
annual reporting cycle, and named Performance Assurance Parties.

The frozen guess ("supplier ops teams and Elexon-qualified data agents")
was half right and missed the important half: **the assurance layer is
not only a supplier cost centre, it is a central regulated function with
its own institution.**

## 2. Workflow

Elexon is **building capacity ahead of the volume, as software**:

- the **Data Acquisition Hub**, built to ingest the ~1.5bn meter readings
  per day expected post-migration, and feeding the Smart Meter Data
  Repository;
- the **Data Integration Platform**, cloud infrastructure for
  industry-wide half-hourly data sharing, taken into full Elexon
  operation from September 2025 under P474;
- the **Confidential Assurance Reporting Platform**, an in-house
  reporting solution that "will enable Suppliers to view key BSC
  performance assurance metrics defined within the Performance Assurance
  Framework" and gives Performance Assurance Parties reports in near
  real-time;
- a **redesign of the Performance Assurance Techniques** themselves for
  MHHS, including a new internal platform for MHHS Supplier Charges under
  BSCP710, and engagement on the impacts of a shortened Settlement
  Calendar;
- **Kinnect** completed, legacy BMRS switched off, contributing to a
  reported £3.8m cost saving.

This is the case v3 was built to recognise: **workload rising by orders
of magnitude while the absorber's cost falls**, because the capacity is
software, not headcount. P482, which splits BSC Agent services, is
justified partly on "more competitive pricing" — the opposite direction
from the frozen symptom.

## 3. Declared strain symptom (frozen, not chosen now)

> Exception volumes and clearing times rise; agent pricing or headcount
> grows; performance-assurance escalations increase.
> Forcing observation: Elexon Performance Assurance reporting and MHHS
> programme defect/progress data.

## 4. Forcing it, and an eligibility failure

**MHHS is mid-migration.** By early August 2026 roughly half of industry
MPANs had migrated; around 80% is expected by Milestone 14 in October
2026; migration completes at Milestone 15 in May 2027 and cutover to the
new arrangements is Milestone 16 in July 2027, after which Elexon expects
to process up to 500 billion half-hourly readings a year.

Therefore:

- **PAF/PARMS reporting** is an eligible instrument in principle, but
  **cannot yet contain** the hypothesised steady-state failure, because
  steady state does not begin until 2027.
- **MHHS programme defect/progress data is ineligible**, by the rule C5
  produced. It measures a transition. C1's frozen boundary names
  supplier ops teams and data agents — business-as-usual roles — and
  business-as-usual symptoms. Migration pain is a different population.

## 5. The narrative refused

> "MHHS is enormously complicated and participants are struggling with
> migration, therefore assurance must be a growing opportunity."

Refused. Large programmes reliably generate consultants, qualification
advisers, test assurance and implementation work — the MHHS qualification
advisory content now circulating is exactly this. **That is transition
expenditure, and it ends.** None of it is evidence that an enduring
function has become externalisable, and C1's frozen boundary does not
permit it to count.

## 6. Verdict

**Absorption stable.** The evidence is positive, not merely an absence:
the responsible institution is provisioning for a roughly
thousandfold data increase in advance, in software, while reducing cost,
and is delivering the assurance metrics to Suppliers as a platform rather
than leaving each to build its own.

The boundary is stated plainly: this verdict rests on the **absorber's
revealed investment**, not on observed performance under full load.
Whether that investment proves sufficient becomes observable after July
2027. That is a reassessment point, **not a falsifier**, and it does not
keep C1 alive in the meantime — under v3 a candidate may not sit
accumulating research on an unmeasured hope.

## 7. What this says about the generator

- The candidate is a **transition mistaken for a structural change**. The
  generator saw a real and enormous volume increase and inferred an
  externalisable function from it. Volume alone did the work; the
  absorber's *capability trajectory* was never asked about.
- **L1 recurs.** Half of C1's forcing observation was ineligible by
  construction. That is now two candidates out of two with an
  eligibility defect.

Not acted on. Logged in `../LESSONS-PENDING.md`.

## Sources (accessed 2026-08-23)

- Elexon Annual Report and Financial Statements 2024/25
  (`assets.elexon.com`) — Data Acquisition Hub and 1.5bn readings/day;
  DIP and P474; Confidential Assurance Reporting Platform; Kinnect
  completion and £3.8m saving; P482 and BSC Agent service splitting.
- Elexon Performance Assurance Framework and PARMS reference pages;
  Annual Performance Assurance Report 2024/25.
- MHHS Programme milestone and migration-progress reporting; Elexon MHHS
  next-steps statement, February 2026; Transitional Operations Group
  papers, 2026.

**Retrieval limitation, recorded honestly**: `elexon.co.uk` returns HTTP
403 to this environment (Cloudflare). The annual report PDF was fetched
from `assets.elexon.com` and its text extracted locally; the PAF, PARMS
and MHHS milestone material was read through search-tool summaries and is
therefore **not pinned by digest**. The load-bearing facts here — central
platform build-out, migration timeline, falling cost — are corroborated
across the fetched PDF and the programme reporting, but the pinning gap
is the same one C5 recorded.
