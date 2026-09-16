# GB Connection Slippage — series (investigation 014)

*How far Britain's contracted grid-connection dates have moved, in megawatt-years. The page at `site/connection-slippage/index.html` and this file are pure functions of `evidence/series.json`.*

**Declaration** `DECLARATION-v2.md`, SHA-256 `f2209b3cfd4dd0b276f1776293d60f83c65f3354db42b13e28348848c79a7a45`, witnessed before the run. Computed 2026-09-16T07:37:17Z (run date 2026-09-16). Copies of the register: 752 journal rows, 732 distinct publication dates, 700 parsed, 700 usable (32 unparseable, 0 lacking a required column).

## Headline

Between 19 Jul 2024 and 22 Jul 2025, 1,147 project-stages were on the register at both dates and 889 of them carried a connection date on both copies. Among those, 197 moved later, 27 earlier and 665 did not move. Their dates moved by a net +57,823 megawatt-years (83,867 later, 26,044 earlier). Chained copy to copy across the old regime only (694 copies, 31 Jan 2014 to 22 Jul 2025; the reformed regime is a separate series), the movement is +532,780 megawatt-years. That exceeds the sum of the year windows below (+293,599) because the chain also counts project-stages present in two consecutive copies but not at both ends of a year.

## Propositions

- **P1** — every complete calendar-year window of the old regime has positive net movement: **holds** (11 complete years).
- **P2** — chained net movement of the reformed regime from its first copy to the first copy at least 365 days later is positive: **undecided** (falsifier date 2027-06-30).
- **F1** fired on 6 consecutive-copy link(s); **F2** on 192 year-on-year row(s).

## Year by year (old regime)

| Year | From | To | Project-stages at both dates | Dated at both ends | Net movement, MW-years | Moved later, MW-years | Moved earlier, MW-years | Dates later / earlier / unchanged | Joined (MW) | Left (MW) | Capacity changed (net MW) | F2 thin population |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2014 | 31 Jan 2014 | 9 Jan 2015 | 213 | 89 | +20,198 | 20,549 | -351 | 19 / 3 / 67 | 213 (48,883) | 207 (62,759) | 31 (+3,626) | — |
| 2015 | 9 Jan 2015 | 4 Jan 2016 | 237 | 104 | +23,194 | 23,291 | -97 | 30 / 5 / 69 | 189 (33,783) | 189 (37,731) | 32 (-9,125) | — |
| 2016 | 4 Jan 2016 | 5 Jan 2017 | 341 | 171 | +23,132 | 25,878 | -2,746 | 45 / 4 / 122 | 88 (17,240) | 85 (22,155) | 52 (+10,313) | — |
| 2017 | 5 Jan 2017 | 4 Jan 2018 | 342 | 186 | +26,175 | 29,759 | -3,584 | 47 / 7 / 132 | 98 (15,873) | 87 (11,581) | 45 (-1,792) | — |
| 2018 | 4 Jan 2018 | 3 Jan 2019 | 351 | 141 | +68,399 | 69,869 | -1,470 | 48 / 8 / 85 | 129 (26,707) | 89 (19,365) | 64 (-1,061) | — |
| 2019 | 3 Jan 2019 | 2 Jan 2020 | 334 | 140 | +11,000 | 11,129 | -130 | 40 / 4 / 96 | 201 (27,296) | 146 (30,203) | 46 (-5,032) | — |
| 2020 | 2 Jan 2020 | 7 Jan 2021 | 102 | 39 | +2,903 | 3,045 | -142 | 18 / 3 / 18 | 472 (75,071) | 433 (73,254) | 9 (-675) | F2: matched under half of baseline |
| 2021 | 7 Jan 2021 | 5 Jan 2022 | 425 | 210 | +12,745 | 14,650 | -1,905 | 43 / 5 / 162 | 308 (96,500) | 149 (30,552) | 29 (-3,177) | — |
| 2022 | 5 Jan 2022 | 6 Jan 2023 | 182 | 105 | +8,396 | 8,488 | -92 | 26 / 1 / 78 | 740 (162,264) | 551 (108,381) | 9 (-790) | F2: matched under half of baseline |
| 2023 | 6 Jan 2023 | 5 Jan 2024 | 665 | 417 | +13,584 | 20,614 | -7,030 | 51 / 4 / 362 | 798 (270,167) | 257 (74,383) | 41 (+934) | — |
| 2024 | 5 Jan 2024 | 3 Jan 2025 | 990 | 765 | +48,797 | 57,516 | -8,719 | 108 / 16 / 641 | 983 (312,618) | 473 (155,276) | 29 (-3,511) | — |
| 2025 (to 22 Jul 2025, partial) | 3 Jan 2025 | 22 Jul 2025 | 1,578 | 1,264 | +35,076 | 57,346 | -22,270 | 153 / 17 / 1,094 | 702 (216,666) | 395 (135,021) | 93 (-7,025) | — |

## Since the reform (separate series, copy to copy)

| Copy of | From | To | Project-stages at both dates | Dated at both ends | Net movement, MW-years | Moved later, MW-years | Moved earlier, MW-years | Dates later / earlier / unchanged | Joined (MW) | Left (MW) | Capacity changed (net MW) | F2 thin population |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 15 Sep 2026 | 25 Aug 2026 | 15 Sep 2026 | 2,183 | 1,823 | +6,250 | 6,250 | 0 | 10 / 0 / 1,813 | 17 (4,084) | 17 (8,019) | 1 (-65) | — |
| 25 Aug 2026 | 22 Aug 2026 | 25 Aug 2026 | 2,194 | 1,834 | -3 | 0 | -3 | 0 / 1 / 1,833 | 6 (1,391) | 4 (766) | 4 (-710) | — |
| 22 Aug 2026 | 19 May 2026 | 22 Aug 2026 | 2,031 | 1,677 | +18,880 | 19,443 | -563 | 45 / 5 / 1,627 | 167 (35,843) | 199 (50,883) | 25 (-2,109) | — |

## Gaps, breaks and copies not used

- Regime break: no copy between 2025-07-22 and 2026-05-19 (301 days); nothing is chained across it.
- 2015-05-08: suspect copy, 225 rows against 413 in the previous copy (46% fewer); excluded (the next copy recovered).
- 2023-11-28: suspect copy, 673 rows against 1392 in the previous copy (52% fewer); excluded (the next copy recovered).
- old regime: no copy between 2014-07-04 and 2014-10-07 (95 days).
- old regime: no copy between 2025-04-01 and 2025-07-01 (91 days).
- 2021-01-29: day-month swapped dates, read exchanged back.
- 2021-02-19: day-month swapped dates, read exchanged back.
- 2022-03-11: day-month swapped dates, read exchanged back.
- new regime: no copy between 2026-05-19 and 2026-08-22 (95 days).
- 2014-02-24: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-02-28: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-03-04: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-03-11: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-03-20: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-03-25: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-03-28: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-04-01: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-04-08: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-04-10: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-04-17: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-04-23: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-04-25: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-04-30: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-06-13: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-06-20: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-06-27: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-07-11: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-07-18: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-07-25: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-08-01: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-08-11: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-08-15: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-08-22: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-08-29: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-09-05: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-09-12: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-09-19: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-09-26: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-10-17: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2014-10-24: not parsed (2014 .xls layout the spreadsheet reader rejects).
- 2021-06-22: not parsed (no header row found).

Every copy's row, both comparisons and the swap test are in `evidence/series.json`; the copies themselves are listed with digests in `evidence/vintage-manifest.json`.
