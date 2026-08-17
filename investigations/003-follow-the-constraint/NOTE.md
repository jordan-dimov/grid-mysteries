# Follow the Constraint: fourteen days behind the Scotland–England boundary

*Investigation 003 research note. Every rule was committed before May
was fetched; the episode, the excerpt day and the focus unit all
selected themselves under pre-committed mechanical rules. Cashflows are
Elexon's **published indicative BM cashflows**; monetary figures are
published figures presented side by side, never a constructed "cost of
RRT".*

## What the frozen rule selected

> **Selected: constraint group SSE-SP, 2026-05-18 to 2026-05-31**
> **repeat-curtailment score: 8,259 · storage bid-down volume: 69,869 MWh**

For fourteen consecutive days of published constraint cost at the
Scotland–England boundary group, the public record shows storage units
being bid down, later appearing scheduled to export again, and being bid
down again — **8,259 repeat-curtailment cycles consistent with
repetitive re-trading**. The episode ends at our declared window's edge:
**our window ends on 31 May; the constraint episode may not.**

On the busiest day for this pattern (20 May, selected by rule), it
happened **1,060 times**. One battery, `E_DOLLB-1`, went through the
pattern **21 times that day**: repeatedly scheduled to export, then
instructed down through zero into substantial import — at times around
99 MW — across **88 distinct acceptances** in a single day.

## The reel (excerpt frames, from the pinned ledger)

Every frame of the 368-frame excerpt ledger is classified **observed**,
**supported inference**, or **not publicly observable**. There is
exactly one frame in the third column, and it is the important one:

- *Observed* — final physical notification schedules export.
- *Observed* — acceptance instructs the unit from its export schedule
  through zero to −44 MW, then −99 MW.
- *Observed* — published indicative BM bid cashflow for the period.
- *Observed* — a later final notification schedules export again.
- **Not publicly observable** — *whether energy retained through
  curtailment was re-sold in the intraday market between instructions —
  the step Ofgem's mechanism names.*
- *Observed* — the unit is instructed down again.
- *Observed* — concurrent offer-side cashflows across non-storage units
  (concurrency observed; causal substitution is not asserted).

Two further observed facts, stated without interpretation:

- **None of the focus unit's 88 acceptances that day is SO-flagged** in
  the public record: they register as unflagged energy actions during a
  published constraint-cost episode.
- The acceptance sequence begins before 01:00 and recurs through the
  day; final physical notifications are final vintages — the
  intra-period revision history that would show *when* schedules changed
  is not public.

## The fourteen-day decomposition

Published figures side by side. **Scope caveat, essential**: BM
cashflows below are **GB-wide totals over the episode dates** for the
165 NESO-classified storage units and for everything else. **The public
record shows where the constraint boundary is** (NESO publishes the
Scotland network diagram locating the constraint groups, pinned in
`evidence/reference-manifest.json`) **but provides no authoritative
mapping telling us which BM cashflows belong to that boundary**: the
thermal-cost dataset is date + group + daily cost only, and the
specialised datasets that do associate individual units with schemes
(e.g. CMIS intertrip arming, which labels particular BMUs B6/EC5 —
also pinned) cover specific services, not a general BMU-to-group
mapping. Localising the money is therefore not publicly supportable;
only NESO's own constraint-cost line is boundary-specific.

| Quantity (episode dates 18–31 May) | Value |
|---|---:|
| Published indicative BM cashflow, storage bids (GB-wide) | −£6,736,338 |
| Published indicative BM cashflow, storage offers (GB-wide) | +£9,152,108 |
| Published indicative BM cashflow, non-storage bids (GB-wide) | −£3,524,447 |
| Published indicative BM cashflow, non-storage offers (GB-wide) | +£78,392,272 |
| **Published outturn constraint cost, SSE-SP group** | **£11,510,565** |
| Repeat-curtailment cycles consistent with RRT | 8,259 |
| Storage bid-down volume | 69,869 MWh |
| **Intraday re-sales between instructions** | **not publicly observable** |

Cashflow signs follow the BSC convention: a negative bid cashflow is
money flowing from the unit (it buys back undelivered energy, or is paid
to absorb at negative prices when positive); no line above is a saving,
a waste, or a "cost of RRT".

## What the hypothesis resolution is

The registered hypothesis asked whether the full sequence of publicly
observable actions could be reconstructed and its cashflows accounted
for, with each apparently perverse step explained by visible incentives.
The resolution is **partly confirmed, with the boundary now precisely
mapped**:

- The observable sequence **is** reconstructable, half-hour by
  half-hour, at scale — 368 frames with zero gaps for the excerpt alone.
- The published money **is** accountable — to the penny of Elexon's own
  indicative settlement figures.
- Two links are **not publicly observable**, and they are exactly the
  links the policy debate turns on: **(1)** the intraday re-sale that
  turns repetition into *re-trading*, and **(2)** the mapping of units
  to constraint groups that would localise the money to the boundary.

Britain is considering policy changes around a phenomenon Ofgem
estimates at roughly £90m a year. The public can reconstruct almost the
entire machine — the schedules, the instructions, the repetitions, the
payments, even where the boundary sits — except the trade in the middle
and an authoritative assignment of cashflows to the boundary. **The
public record can show the repetitive part. It cannot, by itself, prove
the re-trading economics.** That is not a limitation of this
investigation; it is its finding.

*Reference-layer note: the boundary diagram and CMIS artefacts above
were pinned after the May market corpus was closed, to substantiate the
mapping claim. They are context for an observability statement, not May
market data; no selection or accounting figure depends on them.*

## Reproduction

`select_episode.py` (selection, run once after the machinery was
committed blind), `reconstruct.py excerpt|ledger|accounting`. Evidence:
`selected-episode.json`, `excerpt.json`, `episode-ledger.json`,
`episode-accounting.json`, manifests for the closed May corpus (6,045
Elexon + 5 NESO + 31 PN artefacts). Corpus discipline: May 2026 had zero
prior project exposure; 2026-08-11..17 remains untouched.
