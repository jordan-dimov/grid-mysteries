# 013 — the cover price tracker: declaration

**Frozen**: 2026-09-11, before any request for a settlement date on or after
2026-09-09 has been made from this repository to Elexon or to NESO's
balancing-cost, balancing-volume or BSAD resources. Sealed by the commit that
adds this file; its SHA-256 is recorded in `evidence/acquisition-log.json`
by every run that fetches. Rows go in `evidence/tracker.json` and
`TRACKER.md`; amendments, if any, in `AMENDMENTS.md`, dated, and an amended
rule never runs against a batch that taught the amendment. Acquisition
waits for the human seal (see *Acquisition gate*).

## What this is

A **standing forensic instrument**, not a one-off mystery. Investigation 012
reconstructed one day (2026-09-08) and found that Britain's most expensive
day of constraint management was mostly money paid to gas plant to start,
not to wind farms to stop; that a tenth again sat outside the Balancing
Mechanism; and that the daily third-party trackers publish a narrower cut of
the mechanism's spend than the mechanism itself. Each of those is a claim
about one day. This tracker publishes **one public number on a schedule**,
so that the claims can be tested as the year goes on, and lays NESO's own
figure beside ours when it lands.

The number is **the cover price**: the gross money paid out to units in the
Balancing Mechanism on a settlement day, from Elexon's published indicative
cashflows (EBOCF, both directions, positive values only). It is what the
system paid, that day, to cover what its own schedule could not.

## The mystery

> How much does Britain pay each day to cover what its schedule cannot, who
> is paid to stop and who to start, and how much of the bill do the daily
> trackers and NESO's own attribution each leave out?

## Inheritance from 012 (method) and its lessons (applied here as rules)

The tracker inherits 012's declaration, amendments and code: the L2 ledger,
the register classes, the four accounting layers kept separate, the sign
check by rows and by pounds (012 Amendment 2), the BSAD placeholder rule
(012 Amendment 1), and the settlement-day stream alignment (012 code
corrections). Its one new rule is 012's post-acquisition instrument finding,
which 012 recorded and did not apply and which the project's own rule
forbids applying to 1–8 September: the *volume gate* below.

## Prior exposure (recorded, not hidden)

1. Settlement dates 2026-09-01 to 2026-09-08 are exposed by 012 (EBOCF for
   all eight days; DISPTAV, MID, FUELINST, system prices and BSAD for
   2026-09-04 and 2026-09-08). They enter this tracker **only as labelled
   seed rows**, copied from 012's committed evidence
   (`investigations/012-the-record-day/evidence/{selection,results}.json`),
   never recomputed, never re-fetched, never flagged.
2. 012's pinned Disaggregated BSAD CSV (2026-09-11 vintage) holds populated
   rows for 1–10 September and 48 all-zero rows for 11 and 12 September;
   012's Daily Balancing Costs and Volume CSVs end at 2026-09-01. No value
   from that CSV for any date after 2026-09-08 has been read. The seed rows
   for 1–3 and 5–7 September carry no BSAD figure because 012 computed none;
   the CSV is not re-read to fill them.
3. Kilowatts *Dispatches* (read 2026-09-11, via 012) reported that 2026 has
   had twelve days above 4 GW of average curtailment. That is the only
   third-party figure for the tracker window known to this repository, and
   it names no date on or after 2026-09-09.
4. Nothing under `data/raw/elexon/013/` or `data/raw/neso/013/` exists.

## Window and cadence

**Window**: every GB settlement date from **2026-09-09** onward, all 48
periods, open-ended.

**Batches**: seven consecutive settlement dates, the first 2026-09-09 to
2026-09-15, then 09-16 to 09-22, and so on. A batch may be fetched on or
after the **fourth calendar day after its last settlement date**, so that
three full days have elapsed (batch 1: on or after 2026-09-19). Elexon's
indicative cashflows for a day appeared within about 24 hours in 012; the
lag is for the later settlement runs, not for availability, and is fixed
here so that no batch is fetched early because a day looked interesting.
Every batch eligible at the run date and not yet pinned is fetched, in
date order. Batches are never skipped and never fetched out of order.

**No selection.** Every day in a batch gets a row. There is no rule that
picks a day; there is only a flag.

## The flag

A day is flagged **record** when its `paid_out` exceeds every earlier row's
`paid_out` in the tracker's history, **seed rows included**. Equal does
not exceed. Seed rows set the bar (2026-09-08, £33,610,463) and are never
flagged. A day whose EBOCF response carries no rows is *unavailable*,
listed, and neither flagged nor counted as a bar. The flag is recomputed
from the rows on every run, so it depends only on the rows, never on when
they were appended.

## Sign convention, checked per day (012 Amendment 2)

EBOCF `totalCashflow` is read as published: positive is money to the unit,
negative is money from the unit. Per day, the convention **holds** only if
wind-unit bid rows are more often positive than negative **and** their
signed sum is positive. When it fails the row says so, and the row also
carries the inverted reading (money on negative wind-unit bid rows as a
share of money paid in), so nothing rests on one reading.

## Four accounting layers, kept separate, never reconciled (as in 004 and 012)

- **L1** NESO published `Constraints` £ for the day (Daily Balancing Costs
  2026-2027), summed over its rows; blank until NESO's file reaches the
  day.
- **L2** Published indicative BM cashflow (EBOCF) per unit and direction,
  classified by the batch's pinned register `fuelType`: **wind** = `WIND`;
  **gas** = `CCGT` or `OCGT`; **other** = everything else, including units
  with no fuel type, never guessed. Accepted MWh per unit from DISPTAV
  under the *volume gate*.
- **L3** Disaggregated BSAD cost and volume for the day, split by
  `TradeFlag`; a day of all-zero rows is *unpopulated*, not zero (012
  Amendment 1), and its columns stay blank.
- **L4** NESO published constraint bid and offer MWh (Daily Balancing
  Volume 2026-2027); blank until the file reaches the day.

`paid_out` is the sum of positive L2 cashflows on a day; `paid_in` the sum
of negative ones; `net` their sum as published.

## Columns, per day

1. `paid_out` (gross) and `net`.
2. Wind-unit bid £ (positive rows) and its share of `paid_out`.
3. Gas-unit offer £ (positive rows) and its share.
4. Other: `paid_out` less the two above (so it includes wind offers and gas
   bids, both negligible in 012), and its share.
5. Gas-offer volume-weighted price, £/MWh: gas-unit offer £ paired with
   accepted MWh per unit and period under the *volume gate*; unit-periods
   with cashflow but no volume are dropped from both sides, as in 012.
6. Its premium over the APX market index (MID, provider `APXMIDP`),
   weighted by the same gas MWh in the same periods; periods without an
   index are excluded and counted, never filled.
7. Disaggregated BSAD net £ and its share of `paid_out`.
8. NESO `Constraints` £ (L1) and constraint bid/offer MWh (L4), blank until
   NESO's 2026-27 files reach the day, then **appended as outcome with the
   vintage date**. The first vintage that carries the day is kept; a later
   vintage that differs is listed as a revision, and the first is never
   edited.
9. The ratio of L1 to the tracker's **two cuts** (wind-unit bid £ plus
   gas-unit offer £), once both exist; the ratio to `paid_out` is kept
   beside it.

Also recorded per day: coverage (periods with rows, units), the sign
check, the DISPTAV type chosen and every type's deviation, the MID periods
present, the NESO vintage read for L3, and the SHA-256 of every artefact
the row was computed from.

## Volume gate (012's instrument lesson, applied as a declared rule)

Accepted MWh for a day come from the DISPTAV rows of **one `dataType`,
chosen per day by test**: the type whose day totals of absolute pair
volumes, summed over all units and all 48 periods, reconcile with the same
day's system-prices dataset totals (`totalAcceptedOfferVolume` and
`totalAcceptedBidVolume`, absolute) to **within 0.1 percent in both
directions**. If more than one type reconciles, the one with the smallest
worst-direction deviation is chosen, then declared order (`Original`,
`Original-Priced`, `Re-priced`, `Tagged`). A zero settlement total
reconciles only with a zero type total. **If no type reconciles, the
volume columns are blank and the price is not computed** for that day; the
day's row records every type's deviation so the reader can see how far
off each was. The chosen type and the deviations are recorded per day.

Elexon's Insights API description for the endpoint
(`/balancing/settlement/indicative/volumes/all/{bid,offer}/{date}/{period}`)
gives **no semantics for the four data types**. 012 established
empirically that `Tagged` reconciled with the settlement totals on 4 and
8 September (to within 0.02 %) while `Original` carried about a sixth of
the accepted bid volume. The tracker does not assume `Tagged` will keep
reconciling; it tests every day.

## Stream alignment (012 code corrections)

Elexon's stream endpoints take UTC bounds and the `to` bound is inclusive.
A settlement day in British Summer Time runs from 23:00Z the evening before
to 22:30Z (period 48 start); in GMT it is the clock day, ending 23:30Z.
MID is requested from `D-1T23:00Z` to `DT23:30Z` for every day, a window
that covers the settlement day under both BST and GMT and overlaps its
neighbours by up to an hour, and the reader filters to `settlementDate ==
D` before any value is used, so the clock-change weekends (2026-10-25 and
2027-03-28 fall in the window) are handled by the filter, not by the
request. Rows for another day are dropped and never enter a price.
FUELINST is not fetched: no column needs it.

## Propositions and their falsifiers, declared before any tracker day is fetched

- **T1 (the floor holds beyond one day)**: on **record days**, the
  Disaggregated BSAD net share of `paid_out` **exceeds 5 percent**. 012
  found 9.9 % on 8 September and 4.9 % on the runner-up; T1 says the floor
  is a property of record days, not of one day. Decided only on record days
  whose BSAD is populated.
- **T2 (the validation event)**: NESO's `Constraints` figure for a day,
  when published, **exceeds the two cuts** for the same day (wind-unit bid
  £ plus gas-unit offer £, which is the Balancing-Mechanism-only cut the
  daily trackers headline). Decided on tracked days (2026-09-09 onward)
  that have an L1 outcome; seed days are shown as context and do not
  decide.
- **T3 (the price)**: on **record days**, the gas-offer premium over
  `APXMIDP` is **above £50/MWh**. 012 found £82.64 and £110.65. Decided
  only on record days where a DISPTAV type reconciles.

Each proposition is decided by its instances: it **holds** while every
instance holds, **fails** on the first counterexample, and is **undecided**
while no instance exists. **Falsifier date 2027-03-31 for all three.** At
that date, each is reported as it stands: a proposition still undecided
because no record day occurred is reported as exactly that, which is
itself a finding about 8 September.

Verdicts are recorded per run in `evidence/tracker.json` and never rounded
into a score.

## Falsifiers of the instrument (not of the propositions)

- **F0** A day's EBOCF carries no rows at acquisition: the row is
  *unavailable*, the batch is otherwise complete, and the day is listed for
  a dated refetch (`--refetch`), which pins a new vintage beside the first
  and never overwrites it.
- **F1** No DISPTAV type reconciles on a day: volume columns blank, price
  not computed, deviations recorded. If this happens on three or more days
  in one batch, the gate itself is the finding and is reported in
  `TRACKER.md` before any price is discussed.
- **F2** The sign convention fails on a day: the row says so and carries
  both readings.
- **F3** NESO's L1 for a day, when it lands, is **below** the two cuts:
  T2 fails for that day, and the reading that NESO's category is a
  broader attribution than the mechanism's own paid-out is not
  supported; that is the publication.

## Outputs

- `evidence/tracker.json`: every row (seed and tracked), every column,
  every artefact digest, the reconciliation per day, the outcomes and
  revisions, and the propositions as of the run.
- `TRACKER.md`: the method paragraph, the propositions as they stand, and
  the table, seed rows labelled `seed (012)` and their price columns marked
  as 012's declared rule.
- `drafts/draft-post-<date>.md`: for each flagged record day, a draft held
  for the sponsor, never overwritten once written, **never posted by the
  runner**. Release is the sponsor's second seal, as in 012.
- `evidence/acquisition-log.json`: seal prefix, declaration digest, every
  run's date and batches.

## Acquisition gate

Human seal, then for each eligible batch in order: Elexon BM-unit register
(one vintage per batch, used to classify that batch's days) → per day, in
date order, EBOCF both directions, DISPTAV both directions for 48 periods,
MID stream and system prices → NESO's three 2026-27 CSVs (one vintage per
run date). Everything is pinned under `data/raw/elexon/013/` and
`data/raw/neso/013/`, journalled with SHA-256 before any value is read;
manifests are copied to `evidence/`. The runner (`run.py`) refuses to fetch
unless invoked with `--seal <prefix of this file's SHA-256>` and refuses
any batch before its earliest fetch date. Computing and rendering read only
pinned bytes and 012's committed evidence and need no seal. The runner is
idempotent: an already-pinned artefact is verified against its journalled
digest and skipped.

## What this never claims

- No cost is attributed to a transmission boundary or a "constraint"; no
  public unit-to-boundary mapping exists (003).
- NESO's `Constraints` is NESO's attribution; the mapping from acceptances
  into it is not public and is not inferred. The ratio column compares two
  published figures and explains neither.
- Indicative cashflows are indicative, TLM-inclusive and pre-settlement;
  they are never final settlement money.
- No counterfactual: nothing here is a saving, a loss or a "should have".
- Mechanism, never accusation: no unit, party or technology is
  characterised as gaming anything.
- "Record" means the highest `paid_out` in this tracker's history from
  2026-09-01, not in any longer history; the tracker opens no earlier
  window.
- A flagged day is a **draft**, not a post. The runner cannot publish.

## Limits declared in advance

The register vintage classifies units as of its batch's pin date, not the
settlement date; aggregator and virtual units carry no fuel type and stay
`other`, which biases that class upward and never wind or gas; MID is one
provider's index, not "the wholesale price"; the two cuts are the
tracker's construction of what the daily trackers headline, not those
trackers' own figures, which are not pinned; NESO's files may reach a day
weeks late, so T2 may stand undecided long after the day; the record bar
starts from an eight-day seed, so early record days are likelier than
late ones and that is expected, not evidence. The sponsor's next-milestone
note says no new investigation opens by default; this one was opened on
the sponsor's instruction of 2026-09-11 as a distribution instrument, and
says so.
