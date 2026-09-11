# 012 — the record day: declaration

**Frozen**: 2026-09-11, before any request for settlement dates 1–8
September 2026 has been made from this repository to Elexon or to NESO's
balancing-cost, balancing-volume or BSAD resources. Sealed by the commit
that adds this file; its SHA-256 is recorded in `evidence/acquisition-log.json`
when the run happens. Results go in `RESULTS.md`; amendments, if any, in
`AMENDMENTS.md`, dated. Acquisition waits for the human seal (see
*Acquisition gate*).

## Trigger and observations under test

Kilowatts *Dispatches*, "Are we about to set a record for curtailment
costs?", published 2026-09-08 and updated 2026-09-09 (author "Ben"),
relayed on 2026-09-11 through a generated weekly briefing held in the
sponsor's business repository. The post's load-bearing figures are the
**observations**; each is a third party's reconstruction from Elexon
settlement data and is treated as a claim, not a fact:

- **O1** 2026-09-08: 114 GWh of wind curtailed, £3.05m paid to wind
  farms; 117 GWh of gas "turn-up" at £231/MWh; total constraint cost
  £29.65m, a record, 11 % above the previous one.
- **O2** 2026-09-04: 127 GWh curtailed, £4.95m to wind (£40/MWh); 91 GWh
  of gas at £207/MWh; total £26.67m, "the most expensive day of constraint
  management in at least five years".
- **O3** The price NESO pays gas for constraint turn-up went from
  £100/MWh in December 2025 to £217/MWh in September 2026; the premium
  over wholesale widened from £25–45/MWh through most of 2025 to £106/MWh.
- **O4** 1–8 September totals £130.2m by the post's method against
  £128.8m on the Wasted Wind tracker, agreement to within 1.1 %.
- **O5** 2026 has had 12 days above 4 GW average curtailment so far,
  against 20 in the whole of 2025.
- **O6** Boundary limits on the days: B6 4,120 MW against 5,298 MW of
  demanded flow; B4/B5 1,867 MW against 2,990 MW.

Two arithmetic notes recorded before acquisition, because they are the
reason to reconstruct rather than quote. The briefing said 119 GWh where
the post says 114 GWh. And 117 GWh at £231/MWh is £27.0m, which with
£3.05m to wind is £30.1m, not £29.65m; the post's total is therefore not
the simple sum of its two headline products, and what it nets or excludes
is not stated.

## The mystery

> Britain's most expensive day of constraint management: how much of the
> bill was paid to wind farms to stop, how much to other plant to start,
> and how much sits outside the Balancing Mechanism, where the daily
> trackers do not look?

## Prior exposure (recorded, not hidden)

1. The six observations above were read on 2026-09-11 from the secondary
   source. That is the only exposure of any 1–8 September figure. No
   Elexon or NESO row for those dates has been read by this repository.
2. On 2026-09-11, before this declaration, `resource_show` **metadata**
   (no rows) was read for three NESO resources: *Daily Balancing Costs
   2026-2027* (last modified 2026-09-04), *Daily Balancing Volume
   2026-2027* (2026-09-04) and *Disaggregated BSAD 2026-27* (metadata
   modified 2026-09-11). Consequence, fixed now: NESO's own `Constraints`
   attribution for the window is **expected to be absent** at
   acquisition. Its later publication is an outcome to append, never a
   selection input.
3. Investigation 007's September out-of-sample test (`DECLARATION-T3-SEPTEMBER.md`)
   is sealed and unrun; it will read NESO's monthly in-merit file for
   September, a different dataset, and has fetched nothing. The window is
   shared; the data is not.
4. Investigations 010 and 011 pinned no Balancing Mechanism, cashflow,
   market-index or BSAD data for September 2026. The ESO connection-map
   snapshots taken on 3, 5 and 8 September are not market data.
5. Investigation 004 (June 2026) established the method reused here and
   one prior finding that shapes a proposition below: on 24 June the
   large positive balancing adjustment sat **outside** the Balancing
   Mechanism (Disaggregated BSAD, £9.19m on the day). That finding is
   the author of **P2**; nothing from June is used as September evidence.

## What this never claims

- No cost is attributed to a transmission boundary (B6, B4/B5) or to a
  "constraint". No public unit-to-boundary mapping exists (003, evidenced).
  Locational statements use the GSP group from the pinned BM-unit
  register, labelled as context.
- NESO's `Constraints` category is NESO's attribution; the mapping from
  acceptances into it is not public and is not inferred (004 boundary 1).
- Published indicative cashflows (EBOCF) are indicative, TLM-inclusive
  and pre-settlement; they are labelled as such and never as final
  settlement money.
- A `TradeFlag` of `T` on a BSAD row is contextual evidence, not category
  membership or boundary attribution.
- No counterfactual: nothing here is a saving, a loss or a "should have".
- Mechanism, never accusation: no unit, party or technology is
  characterised as gaming anything. If the split is mundane, the mundane
  split is the publication.
- **O3's December-to-September trend and O5's day counts are out of scope**
  for this run: they need windows this declaration does not open. O6 is
  reported as the source's figure only; boundary limits are not
  reconstructed here.

## Window and selection rule (computed by code, not chosen by hand)

**Window**: settlement dates 2026-09-01 to 2026-09-08 inclusive, all 48
settlement periods.

**R1**: the selected day is the window day with the **highest total
published indicative Balancing Mechanism cashflow**, the sum of every
unit's `totalCashflow` in Elexon's EBOCF dataset over both directions and
all periods. Ties break by the earlier date. The runner-up under the same
rule is the comparison day. **P0 (prediction, from O1/O2)**: R1 selects
2026-09-08 and the runner-up is 2026-09-04. A different answer is
reported as such and the selected day still stands.

A day whose EBOCF response carries no rows is **unavailable**, listed,
and excluded from R1 (F0 below). Coverage (periods with at least one
row) is reported for every day.

## Sign convention, fixed in advance

EBOCF `totalCashflow` is read as published under the BSC formulae: a
positive value is money to the unit, a negative value is money from the
unit. A wind unit accepted on a negatively priced bid therefore shows a
positive bid cashflow (paid to reduce). The convention is checked, not
assumed: `RESULTS.md` reports the sign distribution of wind-unit bid
cashflows on the selected day, and if it is not predominantly positive
the convention is recorded as failed and every share below is reported
with the sign inverted as well.

## Four accounting layers, kept separate, never reconciled (as in 004)

- **L1** NESO published `Constraints` £ per period (Daily Balancing Costs
  2026-2027), if rows exist for the day; expected absent.
- **L2** Published indicative BM cashflow (EBOCF) per unit and direction,
  classified by the pinned register's `fuelType`: **wind** = `WIND`;
  **gas** = `CCGT` or `OCGT`; **other** = everything else, including
  units with no fuel type, which stay "unclassified" and are never
  guessed. Accepted MWh per unit from DISPTAV `Original` rows on the
  selected and comparison days.
- **L3** Disaggregated BSAD cost and volume per period, split by
  `TradeFlag`.
- **L4** NESO published constraint bid/offer MWh (Daily Balancing Volume
  2026-2027), if rows exist.

`paid_out` is the sum of positive L2 cashflows on a day; `paid_in` the
sum of negative ones; `total` their sum as published.

## Propositions and the thresholds that decide them

- **P1 (the split)**: on the selected day, wind-unit bid cashflow is
  **below 25 %** of `paid_out` and gas-unit offer cashflow is **above
  50 %** of `paid_out`. O1 implies roughly 10 % and 90 %; the thresholds
  are set where the story would change, not where the source puts it.
- **P2 (the floor)**: on the selected day, net Disaggregated BSAD cost is
  **at least 5 %** of `paid_out`. If it holds, a Balancing-Mechanism-only
  reconstruction understates the day's balancing spend by at least that
  much, and O1's total is a floor. If BSAD is near zero or negative, P2
  fails and the post's total is not materially a floor.
- **P3 (the price)**: the volume-weighted average price of accepted
  offers on gas units on the selected day (L2 £ over DISPTAV MWh) is
  **within ±15 % of £231/MWh**, and its premium over the APX market
  index price (MID, provider `APXMIDP`, weighted by the same gas MWh in
  the same periods) is reported against O3's £106/MWh with no threshold.
- **P4 (the eight-day sum)**: the window sum of L2 `paid_out` and of L2
  `total` are reported beside O4's £130.2m and £128.8m, no threshold;
  the comparison says which of the two the post's method resembles.

## Falsifiers, declared before the run

- **F0** EBOCF carries no rows for 2026-09-08 at acquisition: the
  instrument is not yet available; the run records the gap and a re-run
  date, and no selection is made.
- **F1** R1 selects a day other than 2026-09-08: P0 fails; the selected
  day is analysed and the source's day is reported as the comparison.
- **F2** The sign convention fails (wind-unit bid cashflows predominantly
  negative): shares are reported both ways and the conclusion is limited
  to what survives both readings.
- **F3** P1 fails: the "90 % is not the wind farms" reading does not
  reproduce from published cashflows, and that is the publication.

## Acquisition gate

Human seal, then, in this order: Elexon BM-unit register (a fresh
vintage) → NESO's three 2026-27 CSVs → EBOCF, both directions, for each
window day → **R1 runs offline** and `evidence/selection.json` is written
→ DISPTAV (both directions, 48 periods), MID stream, FUELINST stream and
system prices for the selected and comparison days only → L1–L4 computed
→ propositions evaluated → `RESULTS.md`. Everything is pinned under
`data/raw/elexon/012/` and `data/raw/neso/012/`, journalled with SHA-256
before any value is read into the ledgers; manifests are copied to
`evidence/`. The runner (`run.py`) refuses to fetch unless invoked with
`--seal <prefix of this file's SHA-256>`, so the seal is on the record in
the command that acquired the data. Fetching a whole week of per-period
data to choose one day would expose more of the window than the rule
needs; that is why the deep record is pulled for two days only.

## Out of scope for this run

The December 2025 to September 2026 price trend (O3) and the
above-4 GW day counts (O5), each needing its own declared window;
boundary limits (O6); BOALF acceptance chronology and SO-flags;
NESO's constraint-cost breakdown by boundary; any Morpholog or product
work; any page outside the repo.

## Limits declared in advance

Indicative cashflows are not settlement; the register vintage classifies
units as of the pin date, not the settlement date; aggregator and
virtual units carry no fuel type and stay unclassified, which biases
the "other" class upward and never the wind or gas classes; MID is one
provider's index, not "the wholesale price"; the comparison day is one
day, not a baseline. The sponsor's next-milestone note says no new
investigation opens by default; this one was opened on the sponsor's
instruction of 2026-09-11 for distribution, and says so.
