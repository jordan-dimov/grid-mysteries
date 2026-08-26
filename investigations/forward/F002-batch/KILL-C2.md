# C2 kill record — post-Gate-2 connection evidence maintenance across a developer portfolio

**Batch**: 01 (`5f352ebb…`) · **Generator**: v3 (`ab45edbe…`)
**Run**: 2026-08-26, tenth and last in the frozen kill order. **QUARANTINED
as declared in `BATCH-01.md`**: C2 is adjacent to F001's mined corpus, so
its result is recorded but **does not count toward Generator v3's score**.
**Verdict**: **absorption strain plausible but not measured → downgraded**
(L7: the resolving series exists and has a publication date — 1 Feb 2027 —
before which the symptom cannot exist).

Research performed by a background agent under the v3 kill discipline; the
record below is its report, unedited except for this header.

## 1. Existing job — who maintains milestone evidence after Gate 2 today

Under CUSC Section 16 (CMP376, Ofgem decision 13 Nov 2023) as amended by
CMP434/435 (TMO4+), the *User* — the developer — is the sole party obliged
to produce evidence. NESO's *Updated QM Guidance, December 2025* (doc
375081) sets the mechanics:

- Milestones M1 (planning application submitted), M2 (planning secured), M3
  (land secured; plus ongoing "Original Red Line Boundary" ≥50% compliance
  from M2 onward), M5–M8 (contestable design, construction plan, project
  commitment, construction start). M4 does not apply to transmission. M1 is
  forward-calculated 18/24/36/48 months from the Gate 2 offer by technology
  class; M2–M8 are calculated back from the contract Completion Date.
- "Evidence will be uploaded by the User to the Connections Portal for NESO
  approval." NESO replies "within 10 business days"; automatic 60- and
  30-calendar-day reminders "issued via the customer portal";
  missed/insufficient evidence triggers a "Default Milestone Remedy Period
  Notice" with 60 days to cure; M1–M3 are automatic termination, M5–M8 are
  NESO discretion after escalation with the TO.
- "It is the responsibility of the User to identify, apply for and provide
  evidence for any exceptions."

So the function is absorbed today by **developer in-house grid/consents
teams**, supported by planning and land lawyers for the underlying
documents, with **NESO's Connections Portal** as the counterparty system
(the QM FAQs, doc 294776, note that at the time of the workshops "the
Connections Portal doesn't allow for the submission of evidence" and an
upload function was to be "deployed in January"). Distribution-connected
customers route via their DNO (handbook, doc 373546). No consultancy
reached advertises a discrete post-Gate-2 milestone-maintenance service
(one data point, [S]).

## 2. Eligibility BEFORE numbers

| Predicted symptom | Published by construction? | Distinguishable from ordinary causes? |
|---|---|---|
| Milestone-evidence **resubmission volume** | **No.** No NESO publication counts evidence submissions, rejections or resubmissions. The only commitment is QM Guidance footnote 8: "NESO will provide an anonymised copy of the insufficient evidence that they have 'rejected' on their website in a timely manner" — no such page exists on the queue-management page today. | n/a |
| **Termination rate** | **Partly, and only from 3 Aug 2026.** CUSC s.15 (CMP448, Ofgem decision 8 Dec 2025, live 2 Jan 2026) obliges NESO to "measure and publish the activation metric every six months": cumulative GW of *NESO* terminations and capacity reductions of Gate 2 projects that have not passed M1, against a 6.5 GW trigger. First value published 3 Aug 2026. | **Partly.** Ofgem: "self-terminations will not count towards the activation metric, therefore only the projects that fail to progress are used" — by design the evidence-failure subset. But M1-only, GW-only, six-monthly, and cannot separate "couldn't evidence" from "chose not to because the project died commercially". |
| **Queue-exit rate** | **Yes but reason-blind.** The TEC Register (twice-weekly, single overwritten CKAN resource — no vintages kept by NESO) shows entries/exits by Project ID with no exit-reason field. NESO flags: "some data correction updates may take longer than usual while a temporary data change governance process is in place to support Connections Reform." | **No.** Exits pool commercial withdrawal, self-termination, NESO termination, de-duplication and data correction. |
| Milestone compliance outcomes | **No.** Not published anywhere found; the handbook's "Queue Management Milestones" chapter is listed as *coming next*. | n/a |

Of the two predicted symptoms, one (resubmissions) is unobservable by
construction; the other (terminations) has just acquired a published
instrument that is well-targeted (excludes self-terminations) but
*structurally cannot yet be non-zero*.

## 3. The frozen observation, run

**Gate 2 outcomes (NESO Detailed Results Data, doc 374936, Jan 2026;
pipeline released 8 Dec 2025):** Phase 1 (by 2030) Gate 2 offers
**143,403.0 MW**; Phase 2 (by 2035) **238,017.2 MW**; headline "381.5GW …
ready-to-build"; "1500 applications reviewed in just 5 months." Gate 1
outcomes by reason (Table 8, GW): self-elected 205.7; **failed readiness
4.5**; failed strategic alignment 217.3; did not apply 127.3; total 554.8.
Evidence (readiness) failure at Gate 2 itself was ~0.8% of Gate 1 volume —
the gate was overwhelmingly a strategic-alignment filter, not an
evidence-quality filter. NESO's caveat: figures "are subject to change …
where: a) projects are removed from the connections pipeline, for example
through self-termination or termination by NESO".

**Timing (NESO timeline page):** initial queue formed Dec 2025; Protected
offers 13 Feb–mid-Apr 2026 (transmission); Gate 2 Phase 1 offers
mid-May–mid-Sep 2026; Phase 2 early Sep 2026–mid-Jan 2027; distribution
later. **Offers are still being issued today.** With M1 set 18–48 months
forward from the offer, the earliest M1 due dates fall in late 2027.

**Published termination series (NESO PCF page, update dated 3/8/26):** "The
3 August 2026 marks the first publication of the activation metric … We can
confirm that the metric currently sits at **0MW** and therefore the
threshold is not met and no further action is required by NESO this time."
Next value due 1 Feb 2027.

**TEC Register vintage movement (Project ID diff; Wayback 2025-03-21 and
2025-07-22 vs live 2026-08-25):**

| Window | Exits | Entries | Notes |
|---|---|---|---|
| 2025-03-21 → 2025-07-22 | 23 projects / 3.9 GW | 212 / 58.2 GW | pre-reform application surge |
| 2025-07-22 → 2026-08-25 | **42 projects / 19.0 GW** (40 "Scoping", 2 "Awaiting Consents"; 35 of 42 BESS or BESS+solar) | 18 / 5.2 GW | survivors' net capacity change −6.2 GW; register total 785 → 735 GW |

Gate column (populated only once countersigned), 2026-08-25: blank 1,372
rows / 444 GW; Gate 1 743 / 278 GW; **Gate 2 only 85 rows / 12.9 GW** — the
register has recorded ~3% of the 381.5 GW Gate 2 pipeline as countersigned.
Movement in it right now measures offer administration, not milestone
attrition. No Wayback capture exists between Jul 2025 and Aug 2026.

**Pre-reform baseline (NGESO open letter, 13 Nov 2023):** "232 projects
accounting for c.45GW … due to connect by the end of 2025 … 144 of these
projects potentially at high risk … c.29GW." No follow-up publication of
how many were actually terminated under CMP376 was found.

**Cross-organisational load signals (qualitative only):** handbook — "as we
are expecting high volumes of contact following notifications, it may take
a little longer to fully resolve more complex" cases; a formal complaint
route exists but no counts are published. Timely Connections Report Oct
2025–Mar 2026 explicitly *excludes* Gate 1/2 offers.

## 4. Contradicting evidence

- **Process is portal-based and semi-automated on NESO's side** (upload,
  10-business-day response, automatic reminders). The developer's side is
  not automated by anything NESO provides, but it is the same document set
  the developer already holds for its own consents work.
- **Evidence failure at the assessment gate was tiny** (4.5 GW "failed
  readiness" vs 217.3 GW strategic-alignment failure): developers coped with
  a one-off, deadline-driven, ~1,500-application evidence exercise. Weak but
  real evidence that the incumbent absorbs *episodic* evidence work; C2's
  thesis depends on *continuous* work being different.
- **Zero NESO terminations to date** (PCF metric 0 MW) — consistent with
  "too early", not with "absorption stable".
- **No consultancy scaling signal found** — but search was crippled (§7), so
  this is absence of evidence.

## 5. Verdict and reasoning

**Plausible but not measured.** Not *stable*: nothing observed shows the
incumbent handling post-Gate-2 continuous evidence at scale, because the
scale has not arrived. Not *strain evidenced*: the only exits visible (42
projects / 19 GW) are reason-blind and dominated by pre-reform-vintage
BESS/solar scoping projects — ordinary commercial attrition of a 700+ GW
speculative queue. Not *not determinable*, because the instrument *will*
determine it: the CMP448 activation metric is, by Ofgem's design, the
NESO-terminated-for-failure-to-progress subset — the cleanest possible
public proxy for C2's symptom — published six-monthly (1 Feb / 1 Aug).
C2's falsifier therefore has a date: **if the 1 Feb 2027 and 1 Aug 2027
metrics remain near zero while Gate 2 countersignatures approach the ~380
GW pipeline, absorption is stable; if the metric climbs toward 6.5 GW
before the first M1 cohort (late 2027–2028) has fallen due, strain is
evidenced.** Resubmission volume will never be observable from public data
unless NESO honours footnote 8. "Developers need this" is not promoted to
"developers pay for it".

Under v3 a candidate may not sit in *plausible*; C2 is **downgraded**,
recorded with the observation that resolves it (PCF activation metric,
1 Feb 2027) and the party that holds the unpublished one (NESO, rejected
evidence counts).

## 6. What this says about the generator

C2 was well-formed on *function* and on *forcing* — a legally new,
continuous, cross-organisational obligation created on a known date — but
its *symptom* column was written without checking whether the symptom
could exist yet. The forcing variable (M1 due dates) is 18–48 months
downstream of an offer programme still running, so the kill could not
resolve before ~2027 whatever was gathered. The generator should carry an
"earliest observable date" derived from the mechanism's own timetable, and
flag any predicted symptom that is not a published series by construction
(resubmissions) as needing a substitute instrument declared at freeze
time. Positive lesson: the cheapest evidence was a single NESO page (PCF
metric = 0 MW) — regulatory metrics created for one purpose (a fee
trigger) can be the best public proxy for a different question, and the
generator should look for those deliberately.

## 7. Sources and retrieval limitations (accessed 2026-08-25/26)

**[V]** NESO connections-reform landing, results, timeline pages; NESO
Detailed Results Data PDF (doc 374936, Jan 2026; tables read from
rasterised pages); EA Register v2.0 (doc 373996); "What next" handbook (doc
373546); Queue Management page; Updated QM Guidance Dec 2025 (doc 375081);
QM FAQs (doc 294776); NGESO open letter 13 Nov 2023 (doc 293556); PCF page
(update 3/8/26); Ofgem CMP448 decision letter (doc 374071); TEC Register
CKAN + CSV 2026-08-25; Wayback TEC CSVs 2025-07-22 and 2025-03-21; Timely
Connections Report Oct 2025–Mar 2026 (doc 381856); Ofgem CMP376 decision
page.
**[S]** Roadnight Taylor homepage; NESO "about connections reform" page;
reports.neso.energy dashboards (figures in PNGs).
**[N]** consultancy/trade-press coverage of post-Gate-2 workload; Ofgem
connections-reform programme page; CMP376 decision PDF text; archived TEC
vintages between Jul 2025 and Aug 2026.

**Limitation:** the session's WebSearch budget was exhausted before this
run started; all findings come from direct fetches of known NESO/Ofgem/
Wayback URLs (~45 tool calls). This biases the record toward NESO's own
publications and against third-party testimony — acceptable for the frozen
observation, but §4's "no consultancy scaling signal" is untested rather
than negative.
