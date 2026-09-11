# 012 — the record day: results

**Status**: run 2026-09-11 under seal `a349ea80` (declaration SHA-256
`a349ea80378d05c1ae498291f22b599c245b486c8bfbf9de5c160523cf098b2c`,
byte-identical to the frozen file). Not published. Amendments 1 and 2
(`AMENDMENTS.md`, pre-acquisition) applied; the post-acquisition note
there is not applied.

## 1. The mystery

Britain's most expensive day of constraint management: how much of the
bill was paid to wind farms to stop, how much to other plant to start,
and how much sits outside the Balancing Mechanism, where the daily
trackers do not look?

## 2. The evidence

All eight window days carried published indicative cashflow (EBOCF) rows
for all 48 periods; F0 did not fire. R1 selected **2026-09-08**, runner-up
**2026-09-04**, as predicted from the source (P0 holds).

| Settlement day | Units | EBOCF total | Paid out | Paid in |
|---|---|---|---|---|
| 2026-09-01 | 269 | £10.56m | £12.73m | −£2.16m |
| 2026-09-02 | 232 | £2.20m | £4.76m | −£2.56m |
| 2026-09-03 | 298 | £14.66m | £15.79m | −£1.13m |
| **2026-09-04** | 403 | **£29.26m** | £30.05m | −£0.79m |
| 2026-09-05 | 311 | £16.75m | £17.51m | −£0.76m |
| 2026-09-06 | 352 | £18.13m | £19.34m | −£1.20m |
| 2026-09-07 | 342 | £17.82m | £19.75m | −£1.93m |
| **2026-09-08** | 352 | **£31.56m** | £33.61m | −£2.05m |

The selected day, money to units (`paid_out` £33,610,463), by the
register's fuel type:

| Class (register `fuelType`) | Offers (paid) | Bids (paid) | Share of paid out |
|---|---|---|---|
| Wind (`WIND`) | £500 | **£3,768,601** | **11.2 %** (bids) |
| Gas (`CCGT`, `OCGT`) | **£26,820,639** | £0 | **79.8 %** (offers) |
| Other (everything else, incl. no fuel type) | £2,960,139 | £60,583 | 9.0 % |

Outside the Balancing Mechanism, NESO's Disaggregated BSAD for the day:
617 rows, 600 non-zero, net cost **£3,333,990** (system-flagged `T`
£963,781 on 3,601 MWh; other £2,370,209 on 12,595 MWh), which is 9.9 %
of `paid_out`.

The comparison day, 2026-09-04, `paid_out` £30,049,726: wind bids
£5,394,895 (18.0 %), gas offers £18,677,716 (62.2 %), other offers
£5,748,024 (19.1 %); BSAD net £1,459,841 (4.9 %).

## 3. Explanations tested

**Sign convention (F2).** Held on both days by rows and by pounds:
2,558 positive wind-unit bid rows to 192 negative on 8 September (signed
sum +£3.24m); 3,328 to 82 on 4 September (+£5.25m). Positive bid
cashflow is money to the unit, as the BSC formulae say.

**P1, the split — holds.** Wind-unit bids are 11.2 % of money paid out
(threshold: below 25 %); gas-unit offers are 79.8 % (threshold: above
50 %). The source's "roughly 10 % and 90 %" reproduces as 11 % and 80 %
from published cashflows, with 9 % going to other classes, of which
biomass units took £1.08m, units with no register fuel type £1.06m,
`OTHER` £0.60m and pumped storage £0.22m. F3 did not fire.

**P2, the floor — holds.** Net BSAD cost is 9.9 % of `paid_out`
(threshold: at least 5 %). A Balancing-Mechanism-only reconstruction
understates 8 September's balancing spend by at least that much. On the
comparison day it is 4.9 %, just under the threshold, so P2 fails there:
the floor is a property of the record day, not of every big day. The
BSAD rows for both days were populated (Amendment 1's placeholder case
did not arise; the placeholder rows sat on 11 and 12 September in this
vintage).

**P3, the price — holds.** Volume-weighted price of accepted gas-unit
offers £229.53/MWh on 115,014 MWh (band: £231 ± 15 %). Premium over the
APX market index in the same periods, weighted by the same MWh: index
£146.89, premium **£82.64/MWh**, against the source's £106/MWh. No
threshold was declared; the gap is consistent with a different
reference price (the source does not say which "wholesale" it used) and
is reported, not adjudicated. On 4 September: £201.77/MWh, index
£91.12, premium £110.65.

**P4, the eight-day sum — reported, no threshold.** Window `paid_out`
£153.5m; window EBOCF total (net of money paid in) £140.9m. The source's
£130.2m and the Wasted Wind tracker's £128.8m sit 8 % below the net total
and 18 % below `paid_out`. Day by day the source is also below the net BM
total (8 September £29.65m against £31.56m; 4 September £26.67m against
£29.26m). The source's method resembles a net figure more than a gross
one and excludes something it does not name; what it excludes cannot be
determined from here.

**The source's figures, one by one (8 September).**

| Source (O1) | Reconstructed here | Note |
|---|---|---|
| £3.05m to wind farms | £3.77m paid on wind-unit bids; £3.24m net of wind-unit bid rows paid in | published indicative, TLM-inclusive |
| 117 GWh gas turn-up at £231/MWh | 115.0 GWh at £229.53 (declared rule); 116.6 GWh at £230.09 (post-hoc `Tagged`) | £26.82m paid on gas-unit offers |
| 114 GWh wind curtailed | 16.5 GWh under the declared DISPTAV rule; 118.8 GWh under `Tagged` (post-hoc) | see the DISPTAV finding below |
| £29.65m total | £31.56m BM net; £33.61m BM paid out; plus £3.33m BSAD net outside the BM | the source's total is not the sum of its two products |

And 4 September (O2): £4.95m to wind against £5.39m paid; 127 GWh
against 122.9 GWh (`Tagged`, post-hoc); £40/MWh against £42.75 (post-hoc);
91 GWh of gas at £207 against 90.7 GWh at £206.00 (post-hoc) or 77.6 GWh
at £201.77 (declared rule).

**Instrument finding: DISPTAV `Original` does not carry the day's
accepted bid volume.** Under the declared rule, wind-unit bid volume on
8 September is 16,464 MWh, paired with only £265,945 of the £3.77m paid,
a nonsensical £16.15/MWh. The system-prices dataset for the same day
publishes 143,704 MWh of total accepted bids; DISPTAV rows typed
`Tagged` sum to 143,685 MWh, `Original` to 24,806. On the offer side
`Original` (130,135 MWh) and `Tagged` (132,083) nearly coincide, so P3
survives either reading. The four types do not sum to the settlement
total and Elexon's endpoint description gives no semantics; the meaning
of `Original` is left open. The declared rule stands as run; the
`Tagged` pairing is reported as a labelled post-hoc sensitivity
(`evidence/posthoc-disptav.json`) and the lesson is recorded in
`AMENDMENTS.md` for future declarations, not applied to this window.

**Not tested here** (declared out of scope): the December-to-September
price trend (O3), day counts above 4 GW (O5), boundary limits (O6), and
whether 8 September is a record (needs earlier windows).

## 4. The conclusion

On 2026-09-08, the day with the highest published indicative Balancing
Mechanism cashflow in 1–8 September 2026, money paid out to units was
£33.6m. Of that, 11 % went to wind units on bids (paid to reduce), 80 %
to gas units on offers (paid to increase), and 9 % to other units. A
further £3.3m net was spent on adjustment actions outside the Balancing
Mechanism, a tenth again of the in-mechanism total. The source's reading
that the bill is mostly paid to gas plant to start, not to wind farms to
stop, reproduces from Elexon's published cashflows at 80 % and 11 %, and
its gas price of £231/MWh reproduces at £229.53. Its daily and eight-day
totals sit below the Balancing Mechanism's own net total by 6–9 %, so
they are not floors of the mechanism's spend but a narrower cut of it,
and they omit the £3.3m outside the mechanism.

Uncertainty: cashflows are indicative and pre-settlement; classification
uses the register's fuel type at the 2026-09-11 vintage; the `other`
class includes units with no fuel type and is biased upward; the
comparison day is one day, not a baseline; the premium over the index is
one provider's index and not the source's reference. Nothing here is a
saving, a loss, a boundary attribution, or a characterisation of any
party's conduct.

## 5. Expert corner

- **Selection**: `evidence/selection.json`; R1 over EBOCF `totalCashflow`,
  both directions, all periods, `/balancing/settlement/indicative/cashflows/all/{bid,offer}/{date}`.
  8 September EBOCF rows: 7,345 per direction, `createdDateTime` from
  2026-09-08T23:44:29Z to 2026-09-09T23:14:44Z (indicative, latest
  settlement run only). 4 September: 8,688 per direction.
- **Register**: `/reference/bmunits/all`, fetched 2026-09-11T17:00:09Z,
  SHA-256 `2ec3f7f5…`, 3,071 units: 284 `WIND`, 65 `CCGT`, 26 `OCGT`,
  2,484 with no `fuelType`. Classes: wind = `WIND`; gas = `CCGT`/`OCGT`;
  everything else `other`.
- **Sign**: positive `totalCashflow` = money to the unit. Checked, see §3.
- **Layers**: L1 (NESO Daily Balancing Costs 2026-27, resource
  `1d040751…`) and L4 (Daily Balancing Volume, `e781da74…`) carried no
  rows for either day; the 2026-09-11 vintage ends at 2026-09-01. As
  declared, absent; re-run when the files reach 8 September (they are an
  outcome to append, never a selection input). L3 (Disaggregated BSAD,
  `2be1a4d1…`, SHA-256 `6b319340…`) populated through 2026-09-10 with
  48 all-zero rows on 11 and 12 September.
- **P3 inputs**: gas-offer £ is EBOCF `totalCashflow` per unit-period,
  paired with DISPTAV `Original` `pairVolumes` (absolute sum) for the
  same unit-period; unit-periods with cashflow but no volume are dropped
  from both sides (£26.40m of £26.82m paired). MID provider `APXMIDP`,
  volume-weighted per period, 48 of 48 periods present, 0 periods
  without an index.
- **Stream alignment (worth a line, because an eyeball check would not
  catch it)**: Elexon's stream endpoints take UTC bounds and the `to`
  bound is inclusive. A settlement day in British Summer Time starts at
  23:00Z the evening before. The drafted runner pulled MID and FUELINST
  for the UTC clock day, which drops settlement periods 1–2 and picks up
  the next day's; keyed by period alone, two rows of 9 September would
  have entered 8 September's price series, from outside the declared
  window. Fixed before acquisition (`AMENDMENTS.md`, code corrections):
  MID is pulled `2026-09-07T23:00Z` to `2026-09-08T22:30Z` and both
  readers filter `settlementDate == day`. The pinned MID file holds 96
  rows, all dated 2026-09-08 (48 per provider); the FUELINST file holds
  5,760 rows for the day and 20 for the boundary slot of the previous
  day, which the filter drops.
- **DISPTAV data types** on 8 September, absolute pair volumes summed,
  MWh: bids `Original` 24,806 / `Original-Priced` 1,936 / `Re-priced`
  1,862 / `Tagged` 143,685; offers 130,135 / 5,236 / 0 / 132,083.
  System-prices totals: bids 143,704, offers 132,101. Endpoint
  `/balancing/settlement/indicative/volumes/all/{bid,offer}/{date}/{period}`.
- **Context, not evidence**: FUELINST mean MW on 8 September: wind
  13,109, CCGT 5,554, nuclear 3,244, biomass 2,602. System sell price
  ranged −£11.96 to £202.90/MWh. Wind-unit bid money by register GSP
  group: no group (transmission-connected) £3.56m, `_N` £0.08m, `_P`
  £0.13m; no boundary is inferred from this.
- **Amendments applied**: 1 (all-zero BSAD day = unpopulated, P2
  undecided; did not arise), 2 (sign convention by rows and pounds).
  Post-acquisition note: DISPTAV data types, not applied.

## 6. Reproducibility

- Declaration: `DECLARATION.md`, SHA-256 `a349ea80…`; amendments:
  `AMENDMENTS.md`.
- Run: `uv run python investigations/012-the-record-day/run.py --seal a349ea80 --phase all`
  (2026-09-11T17:00:09Z; `evidence/acquisition-log.json`).
- Pinned artefacts: 1 register + 3 NESO CSVs + 16 window EBOCF files +
  198 deep-record files (DISPTAV 192, MID 2, FUELINST 2, system prices
  2), each journalled with SHA-256 before any value was read:
  `evidence/{register,neso,window,deep}-{journal.ndjson,manifest.json}`;
  bytes under `data/raw/elexon/012/` and `data/raw/neso/012/` (local,
  immutable, not committed).
- Logic and tests: `src/grid_mysteries/investigations/record_day.py`,
  `tests/test_record_day.py` (15 tests). Outputs: `evidence/selection.json`,
  `evidence/results.json`. Post-hoc sensitivity:
  `posthoc_disptav.py` → `evidence/posthoc-disptav.json`.
- To challenge: change no threshold; re-run the phases `select`,
  `evaluate` from the pinned bytes, or re-acquire on a later date and
  compare `createdDateTime` vintages.
