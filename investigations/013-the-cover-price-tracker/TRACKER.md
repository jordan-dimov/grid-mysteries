# The Balancing Bill — tracker (investigation 013, the cover price tracker)

*Public name: **The Balancing Bill**, who got paid to keep Britain's grid
balanced, day by day. The investigation's id, folder, declaration, module and
evidence paths keep their names; only the render, the page and the drafts use
the public name. The page at `site/index.html` is a pure function of
`evidence/tracker.json`.*

**One number, on a schedule.** For every GB settlement date from
2026-09-09, the gross money paid out to units in the Balancing Mechanism
(Elexon's published indicative cashflows, EBOCF, both directions, positive
values only, labelled *paid out*), with the same day split four ways and
laid beside what sits outside the mechanism. The method is 012's, frozen in
`DECLARATION.md` (SHA-256 `d20d59203e7b7fda174c2c6deb2807159687bd9ddea39fe760961af884416473`), and every rule below was fixed before
any tracker day was fetched. Batches are weekly and fetched at least three
full days after their last date. Every day gets a row; nothing is selected
by hand. A day is flagged **record** when its paid-out exceeds every earlier
row's, seed rows included.

**Columns.** *Paid out* and *net* are the mechanism's gross and net published
cashflow. *Wind bids* is money paid on bids by units the register types
`WIND` (paid to reduce); *gas offers* is money paid on offers by `CCGT` and
`OCGT` units (paid to increase); *other* is the residual of paid-out. *Gas
offer £/MWh* pairs those pounds with accepted MWh from the DISPTAV data type
that reconciles with the day's system-prices acceptance totals within 0.1 %
in both directions (the *DISPTAV type* column names it); if none reconciles
the price is not computed. *Premium* is that price less the APX market
index (`APXMIDP`) weighted by the same MWh in the same periods. *BSAD net*
is NESO's Disaggregated BSAD for the day, outside the mechanism; an all-zero
day is *unpopulated*, not zero. *Sign* records that wind-unit bid cashflows
were predominantly positive by rows and by pounds. *NESO Constraints* is
NESO's own attribution (Daily Balancing Costs 2026-27), blank until its file
reaches the day, then appended with the vintage date and never revised in
place; *L1 ÷ two cuts* divides it by wind bids plus gas offers.

**Seed rows** (1–8 September, marked *seed (012)*) are 012's published
figures, copied, not recomputed; they set the bar for the first record and
are never flagged. Their price columns (†) are 012's declared `Original`
rule, which reconciles on offers but not on bids. Cashflows are indicative
and pre-settlement; nothing here is a saving, a loss, a boundary attribution
or a characterisation of any party. Every artefact digest is in
`evidence/tracker.json`.

Last computed 2026-09-26T13:12:13Z (run date 2026-09-26). NESO vintages on disk:
2026-09-15, 2026-09-16, 2026-09-17, 2026-09-18, 2026-09-19, 2026-09-20, 2026-09-21, 2026-09-22, 2026-09-23, 2026-09-24, 2026-09-25, 2026-09-26.

## Propositions

- **T1** — on record days the Disaggregated BSAD net share of paid-out exceeds 5 %: undecided (0 instances). Falsifier date 2027-03-31.
- **T2** — NESO's Constraints figure, when published, exceeds the two cuts (wind-unit bids + gas-unit offers paid) for the same day: **fails** (22 instances, 14 deciding). Falsifier date 2027-03-31.
- **T3** — on record days the gas-offer premium over APXMIDP exceeds £50/MWh: undecided (0 instances). Falsifier date 2027-03-31.
- **T4** — NESO's Constraints figure as a share of the two cuts rises with the wind share of accepted bid volume (Spearman rho >= 0.50 over at least 20 qualifying days from 2026-09-16): undecided (6 qualifying days; decided once on 2027-03-31). Declaration SHA-256 `0f3b5a96…`.
- Record days so far: none. As of 2026-09-26.

**T2 failed on 9 September 2026.**

Before any tracker day was fetched, the declaration stated that NESO's own Constraints figure for a day would come out larger than two cuts of the mechanism's payouts: money paid on bids to wind units (paid to reduce output) plus money paid on offers to gas units (paid to increase it). The first day that could decide it was 9 September. NESO's figure is £4.13m; the two cuts come to £8.0m, so NESO's figure is 51.5% of them. NESO's file covers all 48 settlement periods for that day and is identical across five daily versions (15 to 19 September), so this is not a revision still to come. The declaration says this outcome is the publication. This note is that publication.

What it means: the two cuts are not contained in what NESO calls constraints. Money paid to gas units to increase output buys more than constraint management: on 9 September at least £3.72m of the £7.85m, close to half, sits outside NESO's Constraints figure. Where NESO books it has not been checked here.

What it does not mean: it says nothing about whether NESO's figure is right, and nothing about the size of the bill. The paid-out column is unaffected.

A reading, not yet tested: the ratio seems to follow the wind. On the windiest seed days (4 and 5 September) NESO's figure was about 130% of the two cuts; on the calmest (2 and 9 September) about half. That pattern was noticed after the numbers were seen, so it proves nothing. It will be sealed as a new proposition before batch 2 is fetched on 26 September and decided by later days only. T2 stays marked failed.

Two cautions on the table. The sign check on wind-unit bids failed on six of seven tracker days, so the wind-bids column is ambiguous on those days; the verdict above does not depend on it, because gas offers alone (£7.85m) exceed NESO's figure. And BSAD for 12 and 13 September reads close to zero (£72.86 and £47.48); that is correct under the declared rule, but NESO may not have finished filling those days, so read them as provisional.

## The table

Money in £m; shares of paid-out. Blank means not computable from what is
pinned, never zero.

| Day | Flag | Paid out £m | Net £m | Wind bids £m (share) | Gas offers £m (share) | Other £m (share) | Gas offer £/MWh | Premium £/MWh | DISPTAV type | BSAD net £m (share) | Sign | NESO Constraints £m (vintage) | L1 ÷ two cuts |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|
| 2026-09-01 | seed (012) | 12.73 | 10.56 | 1.44 (11.3 %) | 9.65 (75.8 %) | 1.63 (12.8 %) |  |  |  |  | holds | 13.14 (2026-09-15) | 118.4 % |
| 2026-09-02 | seed (012) | 4.76 | 2.20 | 0.04 (0.9 %) ‡ | 4.52 (94.8 %) | 0.20 (4.3 %) |  |  |  |  | **fails** | 2.19 (2026-09-15) | 48.0 % |
| 2026-09-03 | seed (012) | 15.79 | 14.66 | 1.88 (11.9 %) | 12.57 (79.6 %) | 1.34 (8.5 %) |  |  |  |  | holds | 14.54 (2026-09-15) | 100.6 % |
| 2026-09-04 | seed (012) | 30.05 | 29.26 | 5.39 (18.0 %) | 18.68 (62.2 %) | 5.98 (19.9 %) | 201.77 | 110.65 | Original † | 1.46 (4.9 %) | holds | 31.66 (2026-09-15) | 131.5 % |
| 2026-09-05 | seed (012) | 17.51 | 16.75 | 3.84 (21.9 %) | 9.07 (51.8 %) | 4.61 (26.3 %) |  |  |  |  | holds | 17.02 (2026-09-15) | 131.9 % |
| 2026-09-06 | seed (012) | 19.34 | 18.13 | 2.03 (10.5 %) | 14.84 (76.8 %) | 2.47 (12.8 %) |  |  |  |  | holds | 18.13 (2026-09-15) | 107.5 % |
| 2026-09-07 | seed (012) | 19.75 | 17.82 | 1.49 (7.6 %) | 16.99 (86.0 %) | 1.26 (6.4 %) |  |  |  |  | holds | 19.83 (2026-09-21) | 107.3 % |
| 2026-09-08 | seed (012) | 33.61 | 31.56 | 3.77 (11.2 %) | 26.82 (79.8 %) | 3.02 (9.0 %) | 229.53 | 82.64 | Original † | 3.33 (9.9 %) | holds | 32.67 (2026-09-15) | 106.8 % |
| 2026-09-09 |  | 8.13 | 5.39 | 0.17 (2.0 %) ‡ | 7.85 (96.5 %) | 0.12 (1.5 %) | 224.54 | 73.89 | Tagged | 0.25 (3.0 %) | **fails** | 4.13 (2026-09-15) | 51.5 % |
| 2026-09-10 |  | 15.13 | 11.96 | 0.49 (3.2 %) ‡ | 13.90 (91.9 %) | 0.74 (4.9 %) | 229.81 | 93.43 | Tagged | 2.25 (14.8 %) | **fails** | 12.69 (2026-09-21) | 88.2 % |
| 2026-09-11 |  | 9.78 | 6.88 | 0.19 (2.0 %) ‡ | 7.72 (78.9 %) | 1.87 (19.1 %) | 252.39 | 83.61 | Tagged | 2.11 (21.5 %) | **fails** | 8.33 (2026-09-21) | 105.3 % |
| 2026-09-12 |  | 23.54 | 22.40 | 2.80 (11.9 %) | 17.68 (75.1 %) | 3.07 (13.0 %) | 228.22 | 120.93 | Tagged | 0.00 (0.0 %) | holds | 21.91 (2026-09-26) | 107.0 % |
| 2026-09-13 |  | 4.28 | 2.88 | 0.00 (0.0 %) ‡ | 3.86 (90.3 %) | 0.41 (9.7 %) |  |  | none reconciles | 0.00 (0.0 %) | **fails** | 0.38 (2026-09-21) | 9.9 % |
| 2026-09-14 |  | 6.71 | 2.23 | 0.01 (0.2 %) ‡ | 6.60 (98.4 %) | 0.09 (1.4 %) | 240.23 | 61.28 | Tagged | 2.61 (38.9 %) | **fails** | 3.01 (2026-09-21) | 45.4 % |
| 2026-09-15 |  | 11.52 | 8.56 | 0.44 (3.8 %) ‡ | 9.89 (85.9 %) | 1.19 (10.3 %) | 239.22 | 90.96 | Tagged | 1.35 (11.8 %) | **fails** | 8.88 (2026-09-21) | 85.9 % |
| 2026-09-16 |  | 9.33 | 6.37 | 0.50 (5.4 %) | 8.50 (91.1 %) | 0.33 (3.6 %) | 239.37 | 88.84 | Tagged | 1.50 (16.1 %) | holds | 8.19 (2026-09-21) | 91.1 % |
| 2026-09-17 |  | 28.81 | 27.60 | 4.09 (14.2 %) | 20.46 (71.0 %) | 4.27 (14.8 %) | 229.79 | 111.49 | Tagged | 1.68 (5.8 %) | holds | 29.29 (2026-09-26) | 119.3 % |
| 2026-09-18 |  | 25.29 | 24.62 | 4.06 (16.0 %) | 17.49 (69.2 %) | 3.74 (14.8 %) | 224.45 | 139.77 | Tagged | 1.42 (5.6 %) | holds | 28.36 (2026-09-26) | 131.6 % |
| 2026-09-19 |  | 29.32 | 29.21 | 6.82 (23.3 %) | 18.37 (62.7 %) | 4.12 (14.1 %) | 223.54 | 182.43 | Tagged | 0.96 (3.3 %) | holds | 31.83 (2026-09-26) | 126.3 % |
| 2026-09-20 |  | 22.11 | 21.53 | 5.37 (24.3 %) | 14.31 (64.7 %) | 2.43 (11.0 %) | 206.10 | 156.46 | Tagged | 0.52 (2.4 %) | holds | 23.04 (2026-09-26) | 117.1 % |
| 2026-09-21 |  | 6.56 | 4.36 | 0.14 (2.2 %) ‡ | 5.28 (80.5 %) | 1.14 (17.3 %) | 246.38 | 73.87 | Tagged | 0.40 (6.1 %) | **fails** | 4.31 (2026-09-26) | 79.4 % |
| 2026-09-22 |  | 3.95 | 2.17 | 0.11 (2.9 %) ‡ | 3.17 (80.3 %) | 0.67 (16.9 %) |  |  | none reconciles | 0.86 (21.8 %) | **fails** | 2.91 (2026-09-26) | 88.7 % |

‡ The sign check on wind-unit bids failed on the marked days, so the wind-bids figure on those days is ambiguous; each row in `evidence/tracker.json` carries both readings.
