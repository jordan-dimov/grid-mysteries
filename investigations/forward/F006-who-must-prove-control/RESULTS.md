# F006 — results: the licence forces proof of *cyber posture, complaints handling and aggregate load*; it does not force proof of what any device was told, and nobody is buying that proof

**Declaration** frozen `b4109419…` (commit `9b6b491`), public-as-of
2026-09-03. Blind generation committed first (`be6f05d`), then 68
public-as-of pins and the instrument gate, then the freeze; kills run the
same day from the pinned record plus 31 kill-phase pins
(`evidence/kills-manifest.json`). Records: `K0-BUYER-REALITY.md`,
`K1-K2-ABSORPTION-STRAIN.md`, `K3-CAPTURE.md`; brief: `BRIEF.md`.
**Not published; the sponsor's seal at release is the boundary.**

## The answer to the question

> When control of a household's battery, car and heat pump becomes a
> licensed activity, what must a licensee be able to prove, to whom, at
> what moment — and who is already positioned to prove it?

**To Ofgem, from 1 March 2027 (application) and March 2028 (conditions in
force):** that it is fit, financially responsible and operationally
capable; a statement of intent on consumer protection; a CAF self-
assessment against the Tier 2 profile with a statement of intent, then an
annual CAF assessment, remedial plan and cyber audit within 18 months of
March 2028; incident notification within 72 hours; notification within
three months of crossing 300 MW; quarterly complaints type and volume; an
annual complaints report; annual customer, load, device and switching
returns; and any information "when and in the form requested". **To the
Energy Ombudsman, from March 2028** (from 8 January 2026 for Flex Assure
members): that a complaint was handled within eight weeks and, case by
case, what happened. **To DESNZ/NCSC as an Operator of Essential
Services, from around Autumn 2027 if ≥ 300 MW:** Tier 1 CAF, formal
assurance from 2029.

**Who is positioned to prove it:** the suppliers-turned-controllers
(Kraken and its licensees, EDF, SSE, ScottishPower, OVO, British Gas
responded; all already run complaints reporting, RFIs and annual
adequacy self-assessments under the supply licence, and Pathway C exempts
them from most of the new evidence); the OEMs for override and device
logs (a duty since 2022); the Security Governance Group and the ISO
27001/SOC 2 audit market for cyber; Flex Assure for the two domestic
providers that pay for it; the Ombudsman for redress.

**What no one must prove:** which signal a device was sent, when, under
what consent and bounds; whether an override was honoured; what a
controller's action did to a particular household's half-hourly bill;
that a customer's devices can move to another controller. None of these
is a condition. They surface only as the content of a complaint, an
information request or an inspection — and the pinned responses show no
controller saying it cannot produce them and no buyer paying anyone to.

## Funnel

> **8 generated → 7 buyer-real (P7 split) → 6 publicly testable → 4
> absorbed successfully, 1 absorbed by assignment, 1 unforced → 1 weak
> measured strain → 0 capturable.**

| stage | count | functions |
|---|---:|---|
| generated | 8 | P1–P8 |
| instrument: eligible now / eligible later / proxy only / none | 3 / 2 / 2 / 1 | P1, P3, P6 / P7 (after 2026-09-07), P5 (EPR 2027-03) / P2, P4 / P8 |
| K0 buyer-real | 7 + split | C: P2, P5, P6, P7 (market-facing); C-weak: P1, P3, P8; C+B narrowed: P4; **fail**: P7 tariff-only agents |
| quarantined — buyer-real, not publicly strain-testable | 1 | P8 |
| K1 absorbed successfully | 4 | P2 (already externalised to product regulation, 2022), P1, P3, P4 (market level) |
| K1 absorbed by assignment, capacity untested | 1 | P5 |
| K1 unabsorbed and unforced | 1 | P7 (exempt class) |
| K2 measured stable / strain / not yet / unpublished | 2 / 1 / 2 / 1 | P1, P3 / P6 / P5, P7 / P4 |
| K3 capturable | 0 | P6 killed: efficiently served, rule pending |

Blind priors scored: P2 and P5 predicted absorbed — right. P3 and P4
predicted unabsorbed — **wrong in the way that matters**: they are not
unabsorbed, they are unforced; the licence never asks. P7 predicted to
decide the agent class — it did, by splitting it.

## The three propositions

1. **The problem is coming** — earned, dated, primary: offence from March
   2028; window 1 March 2027; cyber conditions with an 18-month runway;
   NIS for ≥ 300 MW from about Autumn 2027.
2. **A buyer is compelled** — earned for cyber assurance, complaints
   handling, aggregate-load notification and the FSP conduct conditions;
   **not** for per-signal proof, household attribution or portability
   evidence, which no condition compels.
3. **Existing solutions are inadequate** — **not earned anywhere.** Cyber:
   a mature audit market plus an appointed assessor. Complaints: supplier
   machinery plus the Ombudsman. Aggregate load: the controller's own
   counters plus forthcoming guidance.

**Honest output: a described problem. No opportunity is named.** The
sponsor's third falsifier fired first, as designed: the pinned conditions
are satisfiable by machinery the incumbents already run, and the "ledger"
function the study was built around has no forced buyer.

## Falsifiers, status

- **F1** (slip beyond 2028 / withdrawal): not fired; one quarter's slip
  already absorbed (end-2027 → March 2028). Watch: SI laid by 31 Dec 2026.
- **F2** (exemption wide enough to exclude independent controllers and
  agent platforms): **fires for tariff-only agent platforms** under Class C
  as drafted; does not fire for controllers selling into DFS, DSO
  markets or the BM. Watch: the final Order after 7 Sep 2026.
- **F3** (conditions satisfiable by existing logs): **fires** for P1–P3.

## Profile across dimensions (no composite)

| dimension | reading | why |
|---|---|---|
| constraint strength | high | a criminal offence with a date, a regulator with a window and a tacit-authorisation clock |
| evidence quality | high | primary, pinned, dated; the August 2026 package is final policy, not proposal |
| scenario robustness | medium | dates slipped once; Class C and a small-controller exemption still open; CAF profiles unpublished |
| recognition gap | **low** | 21 named respondents including every large incumbent; Flex Assure positioned as "interim compliance bridge"; Salesforce selling the system of record |
| buyer pain | low–medium | RFI cost (£24k/yr), three-month application crunch, cyber runway for small firms; no pain expressed about proof of control |
| solution adequacy | high for what is required; unknown for what is not | supplier and OEM machinery, SGG, audit market; per-signal proof untested because undemanded |
| action lead | ~18 months to March 2028; ~3 years to cyber assurance | ample for incumbents; tight for a new entrant with no supply licence |
| reflexivity | low | publication of this study would not change a statutory timetable |

**Branch of greatest information value:** whether the *practice* of
Condition 6 requests, inspections and Ombudsman cases comes to demand
per-signal evidence that operational telemetry cannot supply months
later. That is not knowable before the first cases. The cheapest
observation is the Ombudsman's FSP case data (its H1 2026 data was
published 24 August 2026; FSP cases have been eligible since 8 January
2026), read for whether any case turned on what a device was told.

## Watches (dated)

| date | observation | resolves |
|---|---|---|
| 2026-09-07 → publication | representations on the class exemptions; final Order text | F2; the agent-platform class |
| by 2026-12-31 | Load Control Licence Regulations laid | F1 |
| late 2026 | Tier 1/Tier 2 CAF profiles published | P5 evidence standard |
| 2027-03-01 | application window opens; EPR notices | P1(b), P5 instruments become eligible |
| 2027-06-01 | end of the "apply within three months" period | volume of the first wave |
| 2027-12 | first nine-month tacit authorisations | Ofgem's service level |
| 2028-03 | conditions in force; Ombudsman ADR for licensees | P3 practice; first Condition 6 requests |
| 2029-09 | Tier 2 CAF compliance due | P5 strain, if any |

## Lessons for the generator (logged, not promoted)

- **L18 (proposed).** A forced function can be *unforced at the standard
  the generator imagined*: the licence compels the outcome (fair
  treatment, redress, cyber posture) and leaves the evidentiary standard
  to practice. The v4 chain should ask, before K1, "at what standard of
  proof does the obligation bite, and who sets it?" — here the Ombudsman
  and Ofgem's case officers, not the conditions.
- **L19 (proposed).** When the forcing variable is a licence, the cheapest
  buyer-reality read is the *application form*: what evidence the
  regulator asks for on day one is the whole of what is forced on day one.
