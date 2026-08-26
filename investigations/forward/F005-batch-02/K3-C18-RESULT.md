# K3 result — C18

**Declaration**: `K3-C18-DECLARATION.md`, frozen at commit `31d083d`,
digest `592f0162710bb6c43327efd2a46ccbad053a5ad8d3ed8829aca10bf701103bd9`.
**Run**: 2026-08-26, one agent, ~38 tool calls, direct fetches only.
**Verdict**: **K3 KILL — strain exists, but capture remains internal to
the incumbent programme.** The recorded prior ("expected to die") is
confirmed.

## Condition 1 — external spend caused by the strain: not found [N]

- Contracts Finder REST v2 (from 2024-06-01), seven keyword queries
  ("flexibility market platform", "flexibility services platform",
  "flexibility market facilitator", "Piclo" = 0 hits, "Electron
  flexibility", "flexibility asset registration", "distribution
  flexibility procurement platform"): nothing relevant. Weak negative —
  DNOs procure under utilities rules — but no vendor announcement naming a
  buyer for registration or reallocation work surfaced anywhere either.
- Elexon's own supplier is still unprocured and inside the programme [V]:
  16 Jun 2026 — "progress in procuring a technical provider"; "Procurement
  activities and technical partner selection – September 2026". Appendix A
  (23 Jun 2026): "potential suppliers of the FMAR solution have been asked
  by Elexon what additional features or functions could be provided by the
  central FMAR supplier to reduce cost … Option 4 has been shared with
  suppliers as an iteration of the proposed options sent in the RFP." The
  value-add and interoperability functions are being pulled *into* the
  central supplier's scope.
- Vendor side [V]: Piclo `/plans` — every FSP selling feature (register
  assets, portfolio, dispatch, settlement) is included on every tier
  including Free; only API support is tiered. Electron help-centre FSP
  guides: register/edit/delete/export only — no FSP-to-FSP transfer. No
  FSP or DNO statement of paying a third party for multi-platform
  registration or reallocation.

## Condition 2 — a necessary function left unserved: partial, and every attestation lands inside the programme

- Elexon Day-1 minded-to (23 Jun 2026) [V]: users are "required to
  register the same asset data multiple times … creating an unnecessary
  administrative burden, cost and complexity"; platform-hopping "not
  feasible, particularly for hundreds of small-scale assets". "You said,
  we did": *single market-entry platform* → "not … in scope for Day-1;
  kept under review"; *single onboarding across SOs* → rejected "due to
  security concerns … FSPs will continue to onboard separately with each
  platform"; *data conflict resolution between FSPs* → deferred to the
  September consultation; CM/wholesale → out of scope.
- Ofgem annual assessment (30 Jul 2026) [V]: FMAR 2/5 "Poor"; confidence
  2.3/5; §4.19 the design "could unintentionally create barriers … for
  mid-sized or resource-constrained organisations that may struggle to
  absorb additional administrative requirements"; §4.20 "ambiguity around
  … asset primacy, data ownership".
- SAB report (27 May 2026) [V]: "lack of clarity creates tangible
  operational risks for DSOs and technology providers"; "Should there be
  more urgency in sorting out the issue of duplicate MPAN registrations?"
- Reallocation — opportunity register O-7 (June 2026) [V]: "Strong
  industry pull … Increase in time-sensitivity following extensive
  stakeholder feedback"; solution "a rule … whether built into FMAR or
  managed by the various market platforms"; Delivery Plan (Jul 2026):
  O3.3 = Consult → Decide → *Phase 2*; the 24 Jul 2026 workshops are
  still "check that we understand the problem, its scope and complexity".

Nobody states that they pay a third party, built a parallel system, or
delayed entry at a measured cost. Every complaint is a request *to* the
funded programme, and the programme has absorbed each into a rule, a
backlog item or a scope note.

## Condition 3 — an addressable supplier role outside Day-1 scope: scope gaps exist; no buyer

- Explicit Day-1 exclusions [V]: single market-entry portal; cross-SO
  single onboarding; CM/wholesale; possibly DFS; assets ≥1 MW; unit
  registration (O-44, backlog); BM registration (O-39, backlog); platforms
  beyond Piclo / Electron / EPEX / Market Gateway / SMP.
- **The population is tiny.** Appendix A, FSPs via API / via UI: Piclo 5 /
  TBC; Electron 10 / 25; Market Gateway 11 / 34; EPEX 17 / 28; NESO SMP
  15 / 643; DFS 4 / TBC. Roughly 40–60 API FSPs and ~100 UI FSPs across
  all DNO platforms — dozens of potential buyers, not thousands. Elexon
  calls FSP commercial registration "lower priority given one-off nature".
- The one function with pull (reallocation) is being handled as a *rule*
  whose implementation will sit with FMAR or the market platforms — both
  incumbents. No independent-supplier slot is contemplated. Data migration
  is "federated": SOs cleanse their own data, so remediation falls to six
  DNOs/NESO and their already-contracted platform vendors.
- `ProvisionPurchased`: none. `ProvisionExists` only generically (free
  Piclo/Electron portfolio tooling).

## Repeat-spend route: none evidenced

Registration is one-off per FSP per platform; reallocation events are
infrequent and being ruled-in; migration and data-quality work lands
inside existing DNO–platform contracts.

## Verdict

**K3 KILL.** The strain is genuine and dated (Ofgem 2/5, missed
milestones, 2.3/5 confidence, a reallocation blocker with "strong industry
pull"), but it is a delivery problem inside an already-funded,
licence-backed Elexon programme with a supplier RFP in flight. No market
participant is shown paying anyone to bridge it; every unmet function
named by users has been absorbed as an FMAR rule, backlog item, or "kept
under review" note; the residual outside-scope functions have a buyer
base of tens of FSPs and no observed purchase. The candidate was not
broadened.

**This is the batch's distinction between *measured strain* and
*commercial opportunity*, made concrete: an incumbent replacement
struggling is not a buyer need escaping the incumbent.**

## Not attempted, for budget
DNO SLC 31E FY25/26 reports and ADE / Flex Assure consultation responses
— the only remaining places a Condition-1 spend line could plausibly
hide; the chance they overturn the verdict is rated low given the FSP
counts above. Failed fetches: Elexon FMAR legacy URL (404); Ofgem site
search; flexiblepower.co.uk and nationalgrid.co.uk (403); epexspot
localflex (redirect); piclomax.com (JS-only); support.piclo.energy;
electron.net/news (404).
