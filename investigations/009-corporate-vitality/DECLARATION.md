# 009 — corporate vitality of the TEC queue: declaration

**Frozen**: 2026-08-27, before any Companies House record for this
question has been requested. Sealed by the commit that adds this file.
Cohorts were sized from the TEC archive alone (`RECONNAISSANCE.md`); no
company state has been read. The 008/J2 Stage-1 outcomes are **not**
evidence here and are not reused.

## The question

> Among TEC project-stages that have remained **Scoping for at least three
> years**, what share of **MW** is attached to a corporate entity carrying
> a **strong public inactivity signal**, versus Built / Under Construction
> positions — and does such a signal tend to appear **before** a project
> disappears from the register?

Both answers are wanted. Large: headline queued MW overstates
economically live competition for capacity. Tiny: the entities behind
long-standing queue positions are overwhelmingly live, against the
"zombie queue" narrative.

## What this never claims

Corporate inactivity is **not** project death: development may continue
under another entity, the project may be transferred, an SPV may be
re-formed. MW is contracted capacity, not built capacity. No figure here
is a "releasable" or "phantom" GW; it is *MW attached to an entity that
shows a strong public inactivity signal*, and it is reported as such.
Weak indicators — company age, absence of charges, absence of recent
filings, dormant accounts — are **never** counted toward a verdict.

## Corporate-state hierarchy (objective Companies House facts only)

Evaluated per resolved company, as of the fetch date, from the profile
and filing-history endpoints; each state carries a **date**.

| tier | state | rule | date used |
|---|---|---|---|
| **V1 strong** | Dissolved | `company_status` ∈ {dissolved, converted-closed, closed, removed} | `date_of_cessation` |
| **V2 strong** | Insolvency process | `company_status` ∈ {liquidation, receivership, administration, voluntary-arrangement, insolvency-proceedings} | earliest filing whose description starts `liquidation-` |
| **V3 strong** | Strike-off in progress | `company_status_detail == "active-proposal-to-strike-off"`, **or** a `gazette-notice-voluntary` / `gazette-notice-compulsory` (or `-compulsary`) filing with no later `gazette-filings-brought-up-to-date`, accounts or confirmation-statement filing | first-Gazette filing date |
| **V4 moderate** | Materially overdue | `accounts.overdue` with `accounts.next_due` ≥ 183 days before the fetch date, **or** the same for `confirmation_statement` | the `next_due` date |
| **V5 weak** | Dormant | `accounts.last_accounts.type == "dormant"` | `made_up_to` |
| V0 | Live | none of the above | — |

**Strong signal = V1 ∪ V2 ∪ V3.** The bars use strong only. V4 is added
in a secondary reading; V5 is tabulated and never scored. A state whose
date is **earlier than the project's first TEC appearance** is treated as
an identity error (a re-used name), and the project is *unresolved*, not
signalled.

## Identity resolution (fixed before the fetch)

1. Search `q=<TEC customer name>` (20 hits, pinned). Candidates = hits
   whose `title` normalises (case, punctuation, LTD/LIMITED/PLC/LLP) to
   the TEC name, **including dissolved companies**.
2. If no candidate: advanced search `company_name_includes=<name>` (pinned);
   then, for each hit, the profile's `previous_company_names` is checked
   for an exact normalised match (renames).
3. If more than one candidate: keep those whose life
   (`date_of_creation` → `date_of_cessation` or open) contains the
   project's first TEC appearance; if still more than one, **unresolved**.
4. Customers holding ≥ 5 TEC projects are *portfolio* companies: resolved
   and reported separately (their state attaches to many MW at once), and
   excluded from the primary bars.

Every mapping is written to `evidence/` with its reason. **Coverage bar**:
≥ 70 % of each arm's MW resolved, otherwise the arm is *not determinable*.

## Test 1 — materiality (MW-weighted)

**Arms** (from `RECONNAISSANCE.md`, fixed): *Scoping ≥ 3 y* — 229
project-stages, 64,325 MW, 164 customers; *Built / UC* — 393 stages,
79,379 MW, 275 customers. Primary population excludes portfolio customers.

**Statistic**: $S_{arm}$ = strong-signal MW ÷ resolved MW, where a stage's
MW is counted as signalled if its resolved company is in V1–V3 with the
state date after the project's first TEC appearance and on or before
2026-08-22.

**Bars**
- **Material** if $S_{scoping} \ge 10\%$ **and** $S_{scoping} - S_{built} \ge 8$ pp.
- **Live** if $S_{scoping} \le 3\%$.
- Otherwise **indeterminate**, reported as such.

Reported alongside, never scored: count-weighted shares; $S$ with V4
added; $S$ with unresolved MW counted as *no signal* (the conservative
floor); the same by plant type and by TO; portfolio customers
separately; the V5 dormant share.

## Test 2 — leading indicator

**Population**: the 73 current-regime project-stages that were last seen
Scoping, are absent from the 2026-08-25 register, and were observed ≥ 6
months (the 41 observed < 6 months are reported, not scored).
**Control**: 150 present-Scoping stages from the same regime, chosen by
a deterministic rule — every 6th stage in the list sorted by normalised
customer name then Project ID — fixed before any fetch.

**Statistics**
- $I_{gone}$, $I_{present}$: share of stages (count and MW) whose company
  carries a strong signal dated on or before 2026-08-25.
- $L$: among disappeared stages with a strong signal, the share whose
  signal date is **before the stage's last-seen vintage** (and after its
  first). "Before disappearance" is measured against the last vintage in
  which the stage appears — conservative, because the 27 stages last seen
  2025-07-22 may have left at any point in the ten-month archive hole;
  $L$ is reported with and without them.

**Bars**
- **Leading** if $I_{gone} \ge 3 \times I_{present}$ **and** $L \ge 50\%$ with
  ≥ 10 signal-bearing disappeared stages.
- **Label, not signal** if ≥ 10 signal-bearing stages and $L < 25\%$.
- **Not determinable** if fewer than 10 disappeared stages carry a strong
  signal, or $I_{gone} < 5\%$.
- Otherwise indeterminate.

## Outcomes, fixed now

- **Material + Leading** → *the TEC queue contains a measurable share of
  MW attached to corporate ghosts, and the ghost state is visible in
  public filings before the position leaves the register.* Decision: a
  buyer or NESO analyst can discount headline queued MW by an observable,
  dated corporate signal.
- **Material + Label** → *the share is real but the corporate signal
  arrives after the position is already gone*; useful for sizing the
  queue, useless as a warning.
- **Live** (either timing result) → *despite the zombie narrative, the
  entities behind long-standing queue positions are overwhelmingly live
  on public evidence*; published as the negative it is.
- **Not determinable** → recorded with the coverage figures; the test may
  be re-run on a later register vintage under this declaration without
  amendment.

## Acquisition gate

Human seal, then: searches, profiles and filing histories pinned under
`data/raw/companies-house/<run-date>/` with journal and manifest before
any state is evaluated; the manifest is copied to `evidence/`. Order of
operations is fixed so that resolution completes for every arm before
any state field is read.
