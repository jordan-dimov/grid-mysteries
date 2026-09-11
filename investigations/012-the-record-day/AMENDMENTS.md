# 012 — the record day: amendments

The declaration (`DECLARATION.md`, SHA-256 `a349ea80…`) is frozen and is
not edited. Everything below was written **before acquisition**: no
Elexon or NESO row for 1–8 September 2026 had been requested from this
repository when these entries were dated. Each entry names what changes,
why, and what evidence prompted it. Nothing here moves a threshold.

## Review of 2026-09-11 (pre-seal)

Reviewed against `CLAUDE.md`: the declaration, `record_day.py`, its tests
and `run.py`. Prior-exposure inventory re-checked on disk: the three NESO
CSVs already under `data/raw/neso/` are the 2026-08-22 vintage and hold no
September row; no `data/raw/elexon/012`, `data/raw/neso/012` or
`2026-09-*` folder exists. Pinned record shapes from 004 and 010 (EBOCF,
DISPTAV, MID, FUELINST, system prices) match the fields the code reads.
Tests, ruff and mypy pass.

### Amendment 1 — a BSAD day of all-zero rows is *not yet populated*, not zero (P2)

**What the declaration says.** L3 is "Disaggregated BSAD cost and volume
per period, split by `TradeFlag`", and P2 fails "if BSAD is near zero or
negative".

**What the instrument does.** NESO's dump carries 48 rows of zero cost
and zero volume for days it has not populated. In the 2026-08-22 vintage
already on disk, 2026-08-22 and 2026-08-23 each have 48 such rows, while
populated days carry hundreds of non-zero rows (2026-08-19: 663 of 663;
2026-08-21: 154 of 174). Read literally, an unpopulated selected day would
make P2 *fail* on a placeholder, which is an instrument gap dressed as a
finding.

**Amendment.** A day whose BSAD rows are all zero in both cost and volume
is recorded as `placeholder_only`, L3 is **unavailable** for it, and P2 is
**undecided** (`None`), with a re-run date, exactly as F0 treats a missing
EBOCF day. P2 is decided only on a day with at least one non-zero row.
Implemented in `record_day.bsad_summary`, tested. A populated day with a
genuinely small or negative net is still a P2 failure, as declared.

### Amendment 2 — the sign-convention check must hold by rows *and* by pounds (F2)

**What the declaration says.** The convention fails if wind-unit bid
cashflows on the selected day are "not predominantly positive".

**Why it needs a definition.** The drafted code judged "predominantly" by
row count alone. On 004's pinned 2026-06-24, wind-unit bid rows were 27
positive to 62 negative with a signed sum of −£238k, so the two measures
agree there; but a day of many small negative rows and a few large
positive ones (or the reverse) would let one measure pass while the other
fails, and the drafted check would call that a pass.

**Amendment.** The convention holds only if positive rows outnumber
negative rows **and** the signed sum of wind-unit bid cashflows is
positive. Either failing fires F2 and the shares are reported both ways.
Both measures are printed in `results.json`. This can only make F2 fire
more readily, never less.

### Code corrections (no declaration meaning changed)

- **MID and FUELINST streams were requested by clock day, not settlement
  day.** The Insights stream endpoints take UTC bounds and the `to` bound
  is inclusive (verified on 010's pinned 2026-08-06 MID file: rows run
  from 2026-08-06T00:00Z to 2026-08-07T00:00Z, 92 for the day and 6 for
  the next). In BST a settlement day runs from 23:00Z the evening before,
  so a clock-day pull drops periods 1–2 and picks up the next day's, and
  `mid_prices` keyed by period alone would have labelled 9 September's
  periods 1–2 as 8 September's — two rows from outside the declared
  window feeding P3. The runner now requests MID from `D-1T23:00Z` to
  `DT22:30Z` and FUELINST by publish time from `D-1T23:00Z` to
  `DT23:00Z`, and both readers filter to `settlementDate == day` before any
  value is used. The declaration's "MID stream … for the selected and
  comparison days only" is what this now does.
- **P3 numerator.** The gas-offer VWAP pairs EBOCF pounds with DISPTAV
  MWh per unit and period; unit-periods with published cashflow but no
  `Original` DISPTAV volume are excluded from both sides. `results.json`
  carries the L2 gas-offer total beside the P3 numerator so the gap is
  visible. No change; noted so the reader is not surprised.

## Post-acquisition note of 2026-09-11 (after the sealed run; **not applied** to this window)

Written after `run.py --seal a349ea80 --phase all` completed at
2026-09-11T17:00Z. Nothing in it changes a verdict of this run; the
declared rule stands as run and is reported as such in `RESULTS.md`.

**DISPTAV `dataType`.** The declaration bound accepted MWh to DISPTAV rows
with `dataType == "Original"`. On the pinned data those rows carry 24.8 GWh
of accepted bids on 2026-09-08 against 143.7 GWh of total accepted bid
volume published in the same day's system-prices dataset, and for
wind-classified units 16.5 GWh. Rows with `dataType == "Tagged"` sum to
143.7 GWh (both directions reconcile with the system-prices totals to
within 0.02 %); for wind units they carry 118.8 GWh, beside the source's
114 GWh. On the offer side `Original` and `Tagged` nearly coincide
(130.1 vs 132.1 GWh), which is why P3's gas-offer price is barely
sensitive (£229.53 under the declared rule, £230.09 under `Tagged`).

Elexon's Insights API description for the endpoint states no semantics
for the four data types (`Original`, `Original-Priced`, `Re-priced`,
`Tagged`). The legacy BMRA interface definition, read through a
third-party transcription that cites Elexon's interface definition
documents, disaggregates the period total acceptance volume into
*tagged*, *repriced* and *originally-priced* elements. On the pinned
data the four Insights types do not sum to the settlement total, so
their exact meaning is left **open**. What is established empirically:
`Tagged` is the type that reconciles with the settlement total, and
`Original` under-reads bid volume by a factor of about six on both days.

Consequences, recorded rather than applied:

- The run's wind-bid MWh and £/MWh under the declared rule (16.5 GWh,
  £16.15/MWh on 8 September) are reported as what the rule produced and
  labelled as not reconciling. The `Tagged` pairing is reported beside
  them as a **post-hoc sensitivity** from `posthoc_disptav.py`, never as
  a verdict.
- Investigation 004 used the same `Original` rule for its half-hour; its
  offer-side figures are as robust as P3 here, its bid-side volumes are
  not, and that is noted for 004 as an outcome to append, not a rewrite.
- Any future declaration that pairs cashflow with DISPTAV volume should
  bind to the data type that reconciles with the system-prices totals
  and make that reconciliation a declared gate. Under the project's rule,
  that amended method may not be run against 1–8 September 2026.
