# Follow the Constraint: fourteen days behind the Scotland–England boundary

*Investigation 003 research note. Every rule was committed before May
was fetched; the episode, the excerpt day and the focus unit all
selected themselves under pre-committed mechanical rules. Cashflows are
Elexon's **published indicative BM cashflows**; monetary figures are
published figures presented side by side, never a constructed "cost of
RRT". This note incorporates the governed correction
`fnd-003-attribution-corrected` (see **Corrections** below); the
original finding remains on the record as published.*

## The question

Britain's system operator estimates that repetitive re-trading (RRT) by
electricity **storage** behind transmission constraints added roughly
**£99m** to balancing costs in FY 2025/26, up from roughly £64m the year
before — with **pumped storage around 80%** of the two-year total
(Ofgem policy paper, June 2026, pinned in
`evidence/reference-manifest.json`). Ofgem is explicit that the
behaviour is **not prohibited in itself** and can occur while an asset
is fully compliant with the Transmission Constraint Licence Condition;
changes to how storage is dispatched behind constraints are under
active assessment.

We asked: **how much of that mechanism can be reconstructed from public
data?** The answer, precisely mapped, is: the repetitions, yes, at
scale. The diagnosis, no.

## What the frozen rule selected

> **Selected: constraint group SSE-SP, 2026-05-18 to 2026-05-31**
> **repeat-curtailment score: 8,259 · storage bid-down volume: 69,869 MWh**
> *Both figures are GB-wide storage activity over the episode's dates —
> not activity attributed to SSE-SP. See Corrections.*

NESO published fourteen consecutive days of constraint cost at the
Scotland–England SSE-SP boundary group — **£11.5m**. Over exactly those
dates, GB-wide public market data shows storage units being bid down,
later appearing scheduled to export again, and being bid down again —
**8,259 repeat-curtailment cycles consistent with repetitive
re-trading**, involving 69,869 MWh of storage bid-down volume. The
episode ends at our declared window's edge: **our window ends on 31
May; the constraint episode may not.**

We cannot say how many of those cycles happened behind SSE-SP, because
no public dataset assigns storage units to that boundary. That is not a
defect the selector could have avoided: a constraint-group filter on
units is **not publicly implementable** — which is itself part of this
investigation's finding, applied to our own method.

On the busiest day for this pattern (20 May, selected by rule), it
happened **1,060 times** across GB storage. One battery, `E_DOLLB-1`,
went through the pattern **21 times that day**: repeatedly scheduled to
export, then instructed down through zero into substantial import — at
times around 99 MW — across **88 distinct acceptances** in a single
day.

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

## Where the public record stops: reproducing the official diagnosis

NESO's £99m estimate is not a count of patterns like ours. As described
in the pinned Ofgem paper, its methodology classifies a settlement
period as possible RRT only when **three criteria** hold: a positive
FPN; a **system-flagged bid acceptance**; and a **net upward revision
of the PN** within a 3/6/12-hour horizon **after** an earlier
system-flagged acceptance. Checking each criterion against the public
record, over the fourteen episode dates:

1. **Positive FPN** — public, but **final vintages only**. Observable.
2. **System-flagged bid acceptance** — the flag is public (BOALF
   `soFlag`). Descriptive tally (`evidence/so-flag-tally.json`): of
   **90,020** distinct storage-unit acceptances GB-wide over the
   episode dates, **2,904 (3.2%) are SO-flagged**. The focus unit
   `E_DOLLB-1` recorded **1,492 acceptances with zero SO-flags** — so
   its 21 excerpt-day cycles, however vivid, **cannot be presented as a
   demonstrated constraint-driven RRT example**; under the described
   methodology its day would not enter the classification at all.
3. **PN revised upward after the flagged acceptance** — requires
   **timestamped PN revision history**, which is **not public**. Only
   final vintages are published. This criterion cannot be evaluated
   from public data for any unit, ever.

So the honest statement is stronger than a caveat: **our 8,259 is not
NESO's number, and no amount of public data can turn it into NESO's
number.** The repeat-curtailment score is a concurrence signature —
mechanism-consistent repetition, GB-wide, during a published
constraint-cost episode. The official diagnosis is computed from
information the public record does not contain.

## The fourteen-day decomposition

Published figures side by side. **All BM cashflows below are GB-wide
totals over the episode dates** for the 165 NESO-classified storage
units and for everything else. **The public record shows where the
constraint boundary is** (NESO publishes the Scotland network diagram
locating the constraint groups, pinned in
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
| Repeat-curtailment cycles, GB-wide storage, episode dates | 8,259 |
| Storage bid-down volume, GB-wide, episode dates | 69,869 MWh |
| Storage acceptances SO-flagged, GB-wide, episode dates | 2,904 of 90,020 |
| **Intraday re-sales between instructions** | **not publicly observable** |
| **Cycles attributable to SSE-SP** | **not publicly determinable** |

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
- Three links are **not publicly observable**, and they are exactly the
  links the diagnosis turns on: **(1)** the intraday re-sale that turns
  repetition into *re-trading*; **(2)** the mapping of units to
  constraint groups that would localise activity and money to the
  boundary; **(3)** the point-in-time PN revision history on which
  NESO's own RRT identification methodology is built.

Britain is weighing dispatch-rule changes around a phenomenon NESO
estimates at roughly £99m a year. The public can reconstruct almost the
entire machine — the schedules, the instructions, the repetitions, the
payments, even where the boundary sits. **The public record can show
the repetitive part. It cannot, by itself, prove the re-trading
economics — nor reproduce the official diagnosis.** That is not a
limitation of this investigation; it is its finding.

The missing pieces are specific and small: **point-in-time PN
revisions** and **authoritative constraint attribution**. If a £99m
market-design problem is to inform dispatch-rule changes, publishing
those two inputs would let outsiders reproduce the diagnosis rather
than take it on trust. Until then, the public can observe the symptoms;
it cannot independently reproduce the diagnosis.

## Corrections

1. **2026-08-17, after the governed finding was published but before
   any public post** (`fnd-003-attribution-corrected`; the original
   finding stands). The earlier draft of this note juxtaposed the
   8,259-cycle score with the SSE-SP boundary in a way that read as
   attribution. The frozen selection rule scores an episode by counting
   cycles across the **entire declared GB storage universe** over the
   episode's dates; no constraint-group filter was declared, and none
   is publicly implementable. All headline figures are now labelled
   GB-wide-concurrent. In the same correction: the policy context
   figure is updated from "~£90m/year" to Ofgem's June 2026 paper
   (NESO estimate, ~£99m FY 2025/26, 12-hour window, up from ~£64m;
   pumped storage ~80% of the two-year total — hence "storage", never
   "batteries", for aggregates), and the methodology-reproduction
   analysis above was added, with the SO-flag tally as pinned evidence.

*Reference-layer note: the Ofgem paper, boundary diagram and CMIS
artefacts were pinned after the May market corpus was closed, to
substantiate observability and policy-context claims. They are context,
not May market data; no selection or accounting figure depends on
them.*

## Reproduction

`select_episode.py` (selection, run once after the machinery was
committed blind), `reconstruct.py excerpt|ledger|accounting`. Evidence:
`selected-episode.json`, `excerpt.json`, `episode-ledger.json`,
`episode-accounting.json`, `so-flag-tally.json`, manifests for the
closed May corpus (6,045 Elexon + 5 NESO + 31 PN artefacts) and the
reference layer (Ofgem RRT paper, Scotland network diagram, CMIS
intertrip arming). Corpus discipline: May 2026 had zero prior project
exposure; 2026-08-11..17 remains untouched.
