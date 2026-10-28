# 025 the exit clock: archive notes (dated findings; nothing here is frozen)

The declaration (`bc052984…`) and Amendment 1 (`4a76ec63…`) are the sealed
texts. This file records what later happens to the archive they read, before
any amendment answers it.

## 2026-10-28: 76 copies added inside the series, and a reader defect

**Copies.** The archive gained 51 TEC Register publication dates from NESO's
EIR response FOI/26/245 and 25 from NESO's published response FOI-26-226
(`investigations/005-connection-date-credibility/ACQUISITION-FOI-26-245.md`).
Inside this series (to 2026-10-20) that makes 76 copies (44 in 2025, 31 in
2026, 2023-06-30). 2025, the series' thinnest year in the old regime, goes
from 57 copies held to 101. The format check, replicated read-only on
2026-10-28 (`evidence/format-check.json` not rewritten), refuses all 76 as
"copy not in the schema report". No copy the compute read has changed or
gone: further copies of held dates are journalled `further_copy` and never
chosen. **No figure moved, because nothing was recomputed.** Figures 1 and 8 of
`SPONSOR-SHEET.md` stand as restated under Amendment 1.

**The reader defect.** From 2020-06-18 to 2024-05-30 the published register
prints a project's name on its first stage row only, and `read_vintage`
keeps only rows that print a name: 40,107 rows in 346 copies were never
read (`archives/tec-register/SCHEMA.md`, "Rows the reader drops"). In the
Project ID era most of them carry the ID of the named row above (86 of 99
on 2022-06-30, 148 of 183 on 2024-04-26). The rest carry their own ID and
usually a customer, which is a project this series never chained. Before
2021-11 nothing on the row says which. What this means for 025's figures,
not computed:

- a stage or project on unnamed rows is invisible until 2024-05-31 and
  then appears, which is an entry and not an exit, so exposure before
  2024-05-31 is understated;
- one that left the register before 2024-05-31 was never seen, so its exit
  is not counted; the old regime's exits for multi-stage projects, storage
  among them (`Energy Storage System` and `Energy Storage System; PV Array`
  are the commonest plant types on the dropped rows), are a lower bound;
- Amendment 1's schema-pass addendum ("Project Name is never blank",
  `blank-patterns.json`) counted rows the reader returned, so it could not
  see these rows; its two name-only rows are a different thing and stand.

**What an Amendment 2 would have to state**, for the sponsor: (a) admit the
76 copies, with a fresh schema report and format check; (b) a reading rule
for unnamed rows, which the counts show is not simply "carry the name
down", with the FOI-26-226 month-end CSVs (which print the name on every
row, 37 dates from 2021-08-31 to 2024-04-26) as its check; (c) as in
Amendment 1, every leaf that moves listed with its old and new value. Under
the doctrine, the expectation is stated before the run. Until then
`SPONSOR-SHEET.md` figures 1 and 8 (adopted in BEDROCK as
`tec-exit-clock-*-2026-10`) are unmoved but carry this open question.

## 2026-10-28, evening: Amendment 2 computed, and kill (a) fired

Amendment 2 (`AMENDMENT-2.md`, `c0973a61…`, frozen at c3053d7) was computed
under the three sealed texts (`run.py --phase compute --seal bc052984`):
format check 869 copies, 0 differences; `evidence/results.json` now holds the
Amendment 2 compute, `evidence/results-amendment-1.json` the one it replaces
(`6fc3d59e…`), and `amendment_2.moved` lists 1,450 leaves that moved.

**Kill (a) fired.** The ID-era not-determinable share is 10.85 % (277 of
2,554 chains) against the declaration's 10 %, and the declaration says the
investigation stops and says so. It stops here. The cause is not the
continuation rule: 276 of the 277 are chains first seen on 2026-05-22 and
last seen on 2026-06-19. In those four weeks, and only those, the
FOI-26-226 copies print a per-row `a1f` identifier in the Project ID column
in place of the per-project `a0l` one (Project Number is stable). The
139 multi-stage projects whose rows took one `a1f` identifier per stage
cannot be stitched one-to-many, so their per-stage chains exist for four
weeks and end not determinable at the switch back. The project-level chains
return to their own keys on 2026-06-23 (I9) and continue. Without that
window the share would be about 1 in 2,278. Whether NESO published those
identifiers or its export took another field is not known; no published copy
of the window is held.

**What moved, for the record (not for use: the compute is stopped):**

- Chains: 2,642 to 2,923.
- Exits: 492 to 495; old regime 483 to 490.
- Figure 1, storage exits in the old regime: **96 to 97**.
- Figure 8, all technologies, clock A, old regime, per 100 chain-years:
  4.43 to 4.54, 11.39 to 11.12, 11.77 to 12.18, 13.22 to 13.10 and 26.28 to
  26.00. Every interval overlaps the one it replaces.
- Flatness verdicts: unchanged.

The amendment's expectations 1 and 2 held: chains rose, and old-regime and
storage exits did not fall. **Expectation 3 was wrong.** Reformed-regime
exits fell from 9 to 5 (figure 9). Five of Amendment 1's nine were last
seen on 2026-05-19, the copy before the 95-day gap the new copies close:
three are seen again in July and August (now open), one falls in the `a1f`
window (not determinable), and one is re-dated by an earlier first
sighting. Figure 9's "9 exits since 1 December 2025" partly measured the
gap.

**Not done, because the investigation is stopped:** the joins, FINDINGS, the
appendix, the figures and the sponsor's sheet were not re-rendered. They stand
as rendered under Amendment 1 and describe that compute. `SPONSOR-SHEET.md`
figures 1 and 8 (BEDROCK `tec-exit-clock-*-2026-10`) are not restated from a
stopped compute. Nothing from 025 goes to Ofgem.

**For the sponsor.** Either the stop stands (025 reports that, with the
archive it now reads, its own kill fires), or an Amendment 3, taught by this
run, says how the four-week `a1f` window is read: for example, by the Project
Number, which is stable across it, or by not reading that window's ID column as
the Project ID. Either way, the Amendment 2 compute stays on record beside
whatever follows.
