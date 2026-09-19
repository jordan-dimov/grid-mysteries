# 013 — The cover price tracker: declaration T4

**A fourth proposition, sealed on its own.** Written 2026-09-19, after
batch 1 was computed and before any data for a settlement day from
2026-09-16 onward was fetched or read. Frozen by `scripts/freeze`, which
witnesses these bytes with OpenTimestamps and RFC 3161 tokens from
freetsa.org and DigiCert and commits the file with its proofs.

## What this declaration is, and is not

`DECLARATION.md` (SHA-256 `d20d59203e7b7fda174c2c6deb2807159687bd9ddea39fe760961af884416473`,
sealed 2026-09-11) **stands unchanged**. Its rows, reading rules, layers and
propositions T1 to T3 are not amended, re-chosen or recomputed. **T2 failed
on 2026-09-09 and stays failed.** T4 is a new proposition over the same
tracker rows, not a repair of T2, and it adds no data.

## Where T4 comes from, and why it is tested only on later days

After batch 1, the tracker's own table showed a pattern. NESO's Constraints
figure was about 130 % of the two cuts on the seed days with the largest
wind-bid shares (2026-09-04: 131.5 %; 2026-09-05: 131.9 %), and about half
on the days with the smallest (2026-09-02: 48.0 %; 2026-09-09: 51.5 %). That
pattern was noticed after the numbers were seen, so those days cannot test
it. **No settlement day before 2026-09-16 counts toward T4.**

What was known when this was written: the tracker rows for 2026-09-01 to
2026-09-15 (`evidence/tracker.json` at commit `0033bf5`, SHA-256
`d93711653dc980c9e5c0d010c79acc0a5a5f81d48f79308201864a758e0c9f60`), and
NESO's cost file, which on 2026-09-19 ended at 2026-09-09. What was not
known:
- any Elexon data for a day from 2026-09-16; batch 2 is fetched by
  `tracker-013` at 09:00 UTC on 2026-09-26, after this freeze;
- any NESO figure for a day from 2026-09-10. NESO's files are pinned daily
  by the tracker, and none has been opened for those days.

## T4

**NESO's Constraints figure as a share of the two cuts rises with the wind
share of accepted bid volume.** Across the qualifying days, Spearman's rank
correlation between *x* and *y* is **at least 0.50**.

- **x, the wind share of accepted bid volume.** For a day, `wind_bid_mwh`
  (accepted bid MWh on units the batch's register types `WIND`, from the
  DISPTAV data type chosen by `DECLARATION.md`'s volume gate) divided by
  the absolute value of `reconciliation.settlement_mwh.bid` (the day's
  accepted bid MWh from Elexon's system-prices data). Both are absolute
  volumes. x has no sign reading, which is why it is used rather than the
  £ wind-bid share of paid-out: that share's numerator depends on the sign
  check, which failed on 6 of the 7 batch-1 days.
- **y, NESO's Constraints over the two cuts.** For a day,
  `outcome.l1_constraints_gbp` at its **first vintage** (as
  `DECLARATION.md` keeps it; revisions are never used) divided by
  `two_cut_gbp` (wind-unit bid £ plus gas-unit offer £, as declared there).
  It is computed exactly from those two figures, not from the tracker's
  4-decimal ratio, whose rounding would create ties.
- **A qualifying day** meets all of these:
  - its settlement date is from 2026-09-16 to 2027-03-31 inclusive;
  - it is not a seed row, and the row is available;
  - a DISPTAV type reconciles, so x exists;
  - the settlement bid total is not zero;
  - L1 exists and its first vintage is dated on or before 2027-03-31;
  - the two cuts are positive.
- **The statistic.** Spearman's ρ: Pearson's correlation of the ranks of
  x and of y over the qualifying days, with tied values given the average
  of their positions. The comparison ρ ≥ 0.50 is made exactly, in rational
  arithmetic; the ρ printed beside the verdict is rounded to four decimals
  for display only. If x or y takes a single value on every qualifying
  day, ρ does not exist, nothing can be seen to rise, and T4 is not
  reached.
- **The verdict, decided once, on or after 2027-03-31.**
  - At least 20 qualifying days and ρ ≥ 0.50: **holds**.
  - At least 20 qualifying days and ρ < 0.50: **fails**.
  - Fewer than 20: **undecided**, reported as exactly that. That would be a
    finding about NESO's publication lag or the volume gate.
  
  Because an L1 first published after 2027-03-31 never enters, every run on
  or after that date reaches the same verdict.
- **Before 2027-03-31** the tracker reports only the number of qualifying
  days and their dates. It never reports a running ρ, so nobody can stop on
  a favourable stretch.
- **Falsifier date: 2027-03-31**, the same as T1 to T3.

**Why 0.50 and 20.** 0.50 asks for a clear monotone relation, not a merely
detectable one. With 20 days and no real relation, ρ ≥ 0.50 occurs about
1.2 % of the time (one-tailed, t-approximation). The window holds 197
settlement days, so 20 is reachable even if NESO publishes weeks late or
the volume gate fails on many days. Neither number was chosen by computing
anything on the days before 2026-09-16.

## Shown beside the verdict, never deciding

When the verdict is reported, and not before, the tracker also reports:
- ρ computed with the £ wind-bid share of paid-out instead of x;
- ρ over the qualifying days whose sign check holds;
- the scatter of x against y.

These say how much the verdict depends on the choice of x. They cannot
change it.

## What T4 does not claim

- **It is not about causes.** A rising ratio would be consistent with NESO
  booking more of the mechanism's payouts as constraints on windy days. It
  would not show why, and it attributes nothing to any unit, boundary or
  company.
- **It does not judge NESO's figure**, and it does not measure the size of
  the bill.
- **It does not revive T2.**

## Implementation, tests and schema

- **The rule is implemented** in `src/grid_mysteries/investigations/cover_price_t4.py`
  (commit `4f29897`, file SHA-256
  `a7d3e3b73d86a91696216ddca248b9901c63dd037d55f8b88d9c79c13f2bb2b8`), a
  pure function of tracker rows.
- **`run.py` computes T4 only while this file's proof sidecar matches its
  bytes.** It records the result under `propositions.T4` in
  `evidence/tracker.json`, with this declaration's SHA-256.
- **Every rule above is mapped to a test** in `evidence/rule-sources.json`,
  which `scripts/check-rules` enforces.
- **The schema pass was limited to T4's input fields.** T4 reads no new
  archive, only fields of 013's own rows: `settlement_date`, `seed`,
  `available`, `disptav_type`, `wind_bid_mwh`,
  `reconciliation.settlement_mwh.bid`, `two_cut_gbp`,
  `outcome.l1_constraints_gbp` and `outcome.vintage`, plus
  `wind_bid_share` and `sign_convention_holds` for the context figures only.
  Their names and value types were read on 2026-09-19 from the
  `tracker.json` cited above. No value of x, y or ρ was computed for any
  day.

## Not part of this declaration

A second form of the question splits the gas offers at the source, using
NESO's SO-flag on individual acceptances from Elexon's settlement stack. It
needs new data, a schema pass, a declared calibration against EBOCF and a
deploy. If pursued, it gets its own declaration, window and falsifier date,
starting no earlier than batch 3. The CADL flag marks short-duration
acceptances, not constraints, and would not enter it.
