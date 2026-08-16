# Method Study 001B — The naive opportunity screen

## Status and corpus discipline

Retrospective method-development study on the already-consumed
**2026-08-04..2026-08-10** corpus, building directly on Method Study 001's
classifications. Explicitly not Investigation 002; no data after
2026-08-10 is touched. This document — unit of analysis, metrics,
tie-breaks and labelling rules — is committed **before** any result below
is computed.

## Research question

> If you built a GB balancing "opportunity" or "skip" screen directly from
> public bid-offer data, would it rank the right things?

Audience note, declared up front: no competent BM desk builds such a
screen — BOD's FPN-relative semantics are textbook, and NESO and
sophisticated analysts use explicit availability/skip methodologies. The
antagonist of this study is not any analyst; it is **the seductive but
wrong answer you get when price data is easier to obtain than operational
truth**. The study measures the first-order error of that answer; deeper
errors (location, dynamics, timing) remain unmeasured here and can only
make it worse.

## Registered hypothesis

> For the majority (more than half) of accepted actions that have at least
> one apparent better-priced alternative under Investigation 001's
> BOD-only rule, the naive screen's single top-ranked alternative is
> provably non-deliverable under Method Study 001's conservative
> physical-state bound.

## Unit of analysis

One **accepted action**: a distinct (settlement date, settlement period,
direction, accepted BM unit, accepted pair id) with DISPTAV `Original`
accepted volume, participating in at least one Investigation-001-rule
inversion. For each accepted action:

- **Naive screen**: among its qualifying alternatives (Investigation 001
  rule, unchanged), the single best-priced one — largest price gap;
  ties broken by alternative unit id then pair id, ascending.
- **Physical-state screen**: remove alternatives classified
  `non_deliverable` by Method Study 001 (classification reused verbatim
  from `../method-study-001-phantom-liquidity/evidence/alternatives.parquet`);
  the best remaining alternative, by the same rule. If none remains, the
  apparent opportunity **vanishes** and its post-filter gap is zero.

## Declared metrics

All at the accepted-action level (the 3.86 m pairwise count is never the
denominator), split by direction and in total:

1. Accepted actions with ≥1 qualifying alternative.
2. Share whose **naive #1 alternative is provably non-deliverable**.
3. Share whose opportunity **vanishes entirely** under the filter.
4. Apparent-gap reduction (naive gap − post-filter gap), £/MWh:
   median, p75, p90, p99.
5. **Top-N ranking distortion** for N = 10, 100, 1000, under two declared
   rankings: primary by naive gap; secondary by naive notional (below).
   For each: how many of the raw top N have a non-deliverable #1, how
   many vanish, and the overlap |top-N raw ∩ top-N post-filter| (the
   post-filter ranking uses post-filter gap/notional and excludes
   vanished actions).
6. **Naive counterfactual notional** = |accepted volume MWh| × apparent
   gap, per accepted action; totals before and after the filter, and the
   share of raw notional that vanishes. **Labelling rule, binding on all
   outputs: this is arithmetic on public numbers. It is never a saving,
   cost, missed revenue or achievable value, and the note must state
   that even the post-filter notional remains unadjudicated for timing,
   dynamics and location.**
7. Technology (fuel type) and GSP-group concentration of the surviving
   top 100 (primary ranking), from the pinned BM-unit reference vintage.

## External validation against NESO's own skip methodology

NESO publishes an official skip-rate dataset (data portal, "Skip Rates"):
per **calendar day × NGC BM unit × Bid/Offer × methodology stage 0–5**,
the available, in-merit, accepted and skipped volumes (In Merit All
Balancing Mechanism resources), plus per-exclusion rows with stage and
reason (Exclusion Reasons resources). Schema and stage/reason vocabulary
were confirmed from the **July 2026** resources only, so this declaration
is not shaped by the window's numbers. NESO's result is **the
authoritative external reference, not absolute ground truth**: its
definitions (availability-based in-merit stacks, daily aggregation)
differ from this study's, so no precision/recall language is used.

Declared comparison, computed only after the August 2026 resources are
pinned:

- **Pinned inputs**: the August 2026 "In Merit All Balancing Mechanism"
  and "Exclusion Reasons" CSVs (month-to-date at fetch vintage),
  journalled and immutable; comparison restricted to the window dates;
  per-date row coverage reported, and any window date NESO has not yet
  published is excluded from the matrix and reported as such. The
  "In Merit Post System Action" variant is not used: our screen does not
  remove system-flagged accepted actions, so All-BM is the aligned
  comparator.
- **Cell**: (window date, direction, NGC unit), joined to Elexon unit ids
  via the pinned BM-unit reference. Cells come from the union of both
  sources' units; scope differences are reported, never hidden.
- **NESO says skip**: summed `skipped_volume_MWh` over pairs at the final
  stage (5) of the All-BM file is > 0 for that cell.
- **Naive screen flags cell**: the unit qualifies as a better-priced
  unaccepted alternative (Investigation 001 rule) in ≥1 settlement period
  of that date/direction. **Feasibility-aware flags cell**: same with
  provably non-deliverable alternatives removed.
- **Agreement matrices**: naive × NESO and feasibility-aware × NESO
  (2×2 counts each, plus the per-direction split).
- **Magnitude relationship**: Spearman rank correlation between NESO
  stage-5 skipped volume and the cell's declared opportunity intensity —
  the sum over settlement periods of the unit's largest qualifying gap
  (£/MWh·periods; a declared monotone proxy, not a physical quantity) —
  reported naive and post-filter.
- **Top-20 disagreements**: among cells the feasibility-aware screen
  flags but NESO's stage 5 does not mark as skipped, the 20 with the
  highest post-filter intensity; for each, the NESO Exclusion Reasons
  rows for that unit/date are tabulated. The converse disagreement
  (NESO skip, naive screen silent) is counted and characterised. These
  disagreements are expected to reveal the reconstruction's next missing
  dimensions (e.g. "Behind constraint" — location).

## Residual anatomy (top 20 survivors)

For the top 20 accepted actions by post-filter gap: without changing any
filter, inspect public BOALF acceptance flags for those settlement
periods (newly pinned, journalled), the already-pinned PN/MELS/MILS
state, and reference technology/GSP data. Classify observations only
under the existing explanation-status vocabulary of
`../001-largest-apparent-inversion/EXPLANATION-PROTOCOL.md`
(plausibility never rises above *compatible but unproven*). The question
is whether the residue is random or structurally concentrated.

## Outputs

- `evidence/screen-analysis.json` — all metrics above.
- `evidence/screen.parquet` — one row per accepted action.
- `evidence/neso-comparison.json` + `evidence/neso-manifest.json` — the
  external validation and its pinned artefacts.
- `evidence/anatomy.json` + `evidence/case-boalf-manifest.json` — the
  top-20 anatomy and its pinned artefacts.
- `evidence/screen-funnel.svg`, `evidence/rank-distortion.svg`.
- `NOTE.md` — candidate headline is the ranking-distortion result; the
  notional is subordinate. No dramatic conclusion is manufactured.
- Morpholog: investigation `ms-001b-naive-screen`, the hypothesis above,
  source manifests, and a finding only for claims the completed study
  supports.

## Reproduction

```bash
uv run python investigations/method-study-001b-naive-screen/screen.py analyse       # offline
uv run python investigations/method-study-001b-naive-screen/screen.py fetch-neso    # pins NESO skip-rate CSVs
uv run python investigations/method-study-001b-naive-screen/screen.py neso-compare  # offline
uv run python investigations/method-study-001b-naive-screen/screen.py fetch-anatomy # ≤20 pinned BOALF artefacts
uv run python investigations/method-study-001b-naive-screen/screen.py anatomy       # offline
uv run python investigations/method-study-001b-naive-screen/screen.py charts        # offline
```
