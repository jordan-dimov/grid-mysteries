# 016 — amendments

Append-only. Each entry says what changed in the pack, why, and what a reader
who already has an earlier copy should do about it.

---

## 2026-09-16 — the side-of-B6 ladder corrected; four defects named

**What prompted it.** An external calibrated classifier (TypeSafe `jev-latest`,
run 2026-09-16 from the `etrmbiz` repository, `research/typesafe-experiment-2026-09-16/`)
was asked one yes/no question per candidate pair — *is this TEC register row
the same generation project as this BM unit* — over 652 pairs covering 194
named wind BM units of `wind_units.csv`. It agreed with 71 of the ladder's 75
register matches and disputed four. **Nothing it produced is relied on for any
figure here.** It is a proposer: it surfaced places worth looking at, and every
one was then checked by hand against the register vintage and the BM unit
reference. Two of its disputes turned out to be defects in our rule; two turned
out to be the model under-confident and the rule right. The defects are
recorded below as defects of the rule, not as model findings, and the corrected
reading reproduces without the model.

### The five cases it named, verified by hand

| Case | Model's reading | Verdict after checking the register | What it was |
|---|---|---|---|
| `E_BABAW-1` Baillie Wind Farm, 52.5 MW | ladder row `Baillie Greener Grid Park` p 0.04; prefers `Baillie Wind Farm` p 0.90 | **Model right, ladder wrong** | `Baillie Greener Grid Park` is 48 MW, `Energy Storage System;Reactive Compensation`, Statkraft UK Ltd, *Scoping*, effective 2030. `Baillie Wind Farm` is 52.5 MW, `Wind Onshore`, Baillie Windfarm Limited, *Built*. Exact name, exact capacity, right plant, and it sits one line below the row the rule took. Defects **D1** and **D2**. |
| `T_KENNW-1` Kennoxhead, 60 MW | ladder row `Kennoxhead Wind Farm Extension` p 0.10; prefers `Kennoxhead Wind Farm` p 0.35 | **Ladder right, model wrong** | The row the model prefers is 112 MW, *Consents Approved*, effective 28/04/2028, customer Perigus Energy UK Limited — it cannot be a unit generating on 8 September 2026. The row the ladder took is 60.0 MW against the unit's 60.000, *Built*, customer `KENNOXHEAD WIND FARM LIMITED`, which is the unit's lead party verbatim. The model was pulled by the exact name string; capacity, status and counterparty all point the other way. The register's naming is the trap: here the row called *Extension* is the built one. No change. |
| `E_TULWW-2` Tullo Extension, 25 MW | ladder row `Twinshiels (Tullo 2) Wind Farm` p 0.19, no alternative | **Ladder right, model under-confident** | 25.0 MW against 25.000, SHET, *Built*. The other Tullo row (`Tullo Wind Farm`, 17 MW) is `E_TULWW-1`, which the ladder places on it. The two units and the two rows pair off exactly on capacity. No change. |
| `T_HRSTW-1` Harestanes, 142.3 MW | ladder row `Harestanes` p 0.48, no alternative | **Ladder right on the side, but by luck** | The register carries `Harestanes` twice: stage 1 at 125 MW (*Built*) and stage 2 at 163.3 MW (*Under Construction*, effective 2028). Both are within 15 % of 142.3 (12.2 % and 14.8 %), both SPT. 015's rule took stage 1 because it sorts first, not because anything chose it. The side is right and unchanged; the *reason* was file order. Defect **D1**, now visible in the basis string, which says two rows matched and both are north. |
| `2__PENEC001` Rothes Windfarm, 54.501 MW | ladder row `Markinch (Rothes) Biomass CHP Plant` p 0.68 — plant type wrong, not flagged strongly | **Ladder wrong** | A 55 MW biomass CHP plant in Fife is not a 54.5 MW wind farm in Moray. It matched on one shared name token and a capacity that agrees to 0.9 % by coincidence, with nothing in the rule testing what the plant burns. The register carries no Rothes wind row at all. Defect **D2**. The unit now falls through to its GSP group `_P` and is graded C instead of B; the side, north, is unchanged. |

### The four defects, and what each fix is

All four are in the TEC step of 015's ladder as applied to wind.

- **D1 — first match wins.** 015 walks the register in file order and returns
  on the first row that passes name and capacity. Fixed: every passing row is
  collected; the side is returned only where all of them agree, and where they
  disagree the rule declines rather than resolving the disagreement by file
  order. The cited row is the one whose capacity is closest, and the basis
  string now says how many rows matched.
- **D2 — no plant type test.** Fixed: a wind BM unit may only link to a
  register row whose `Plant Type` names wind. Hybrid rows
  (`Energy Storage System;Wind Onshore`) still count as wind rows.
- **D3 — `OFTO` falls through in silence.** 015 put `SHET` and `SPT` north and
  `NGET` south and left `OFTO` in neither set, so a unit that matched an
  offshore transmission owner's row was left ungraded rather than placed.
  `OFTO` names a licence, not a geography, so it is resolved from
  `evidence/ofto-rows.json`: all 15 OFTO rows of this vintage, each checked by
  hand against its connection site and onshore landfall. **A vintage whose OFTO
  set has not been enumerated that way yields `unknown`, never `south`.** In
  this vintage every Scottish offshore project (Beatrice, Moray East and West,
  Seagreen, Inch Cape, Neart na Gaoithe, Kincardine, Hywind, Aberdeen) is
  hosted by SHET or SPT rather than OFTO, which is why all 15 OFTO rows land in
  England or Wales. That is an observed fact about this vintage and is not
  carried forward as an assumption.
- **D4 — the name test cannot see a roman numeral.** `WALNEY_1` and `Walney I
  Offshore Wind Farm` are one project written two ways, as are `Craig 2` and
  `Craig II`. Fixed by normalising `i` to `x` to digits on both sides. This is a
  normalisation of the existing test, not a loosening: the rule still matches
  only where the unit's tokens are wholly contained in the row's.

**Deliberately not fixed: the BM-unit index suffix.** `Ormonde Energy Limited 1`
and `Farr Unit 1` carry an index the register row does not. Stripping it would
let the rule match names the unit does not contain, which is the one property
015's ladder promised to keep (*"the ladder never guesses from a name"*). Those
units are placed, if at all, through a reviewed link (grade R) and not by the
rule.

### The design question the offshore farms expose, decided before it was applied

**One register row, many BM units.** A TEC row is a connection, not a meter:
Dudgeon's 400 MW row faces four BM units, London Array's 630 MW row four,
Farr's 92 MW row two. Under 015's rule the capacity test compares the row with
a single unit, so a multi-BMU station fails it by construction and the
mismatch is structural rather than a sign of error.

> **The rule.** For a candidate register row *R* and a BM unit *U* whose name
> test passes against *R*, let *G(R)* be the distinct wind BM units of the
> register vintage whose name test also passes against *R*, de-duplicated on
> the Elexon id. The capacity test passes where *R*'s cumulative total capacity
> sits within 15 % of **either** *U*'s own registered capacity **or** the sum
> over *G(R)*. Where *G(R)* is *U* alone the two limbs are the same test, so
> 015's rule is the special case and single-unit stations are unaffected.

The group is defined by the row, not by a guess at a name stem, so it needs no
second name heuristic. The tolerance is 015's 15 %, unchanged.

Because the rule's name test deliberately still refuses the unit-index suffix,
the group limb rarely fires on its own in this vintage — the multi-BMU offshore
farms are exactly the ones whose unit names carry `BMU 1`, `Generator BMU 2` and
so on. The limb is nonetheless declared and implemented now, so that it governs
hand review today and is already on the record if the name test is ever
loosened.

### The admission rule for model-proposed links

Written down here, and in `evidence/reviewed-links.json` beside the links
themselves, so it governs the next pass as well as this one.

1. **A model never writes a side.** It proposes a candidate link with a
   probability. The link enters the record only as a claim carrying the model's
   name and version as provenance.
2. **A probability threshold selects the review queue.** Above it a named human
   reads the register row and the BM unit record and records accept or reject
   with a reason. Below it nothing happens.
3. **Acceptance needs the same evidence the rule needs**: the row's plant type
   must name wind, its `HOST TO` (or, for `OFTO`, the vintage enumeration) must
   imply a side, and its capacity must sit within 15 % of the unit's own
   capacity or of the declared group's total. A name agreement the capacity
   does not support is not enough, whatever the probability.
4. **Admitted links carry grade `R`**, never A, B or C. Dropping every grade R
   row recovers a classification no model and no reviewer touched, and
   `wind_units.csv` is built so that this is a filter, not a re-run.
5. **Nothing is ever auto-adopted into a sealed result**, and no sealed
   declaration is re-run under a rule it did not use.

**On the threshold, plainly:** the 0.8 cut used here was chosen *after* the
classifier's run was read. It is therefore a review-queue cut and **not** a
pre-declaration, and it is recorded as such in `evidence/reviewed-links.json`.
For any future pass the threshold is declared before the model is run, and the
queue it selects is reviewed whole — including the entries a reviewer would
rather not have seen.

### What the 17 high-probability proposals came to

The classifier offered 17 units at p ≥ 0.8 whose ladder row was absent. Every
one was checked by hand against the register vintage and the BM unit reference.

- **5 the corrected rule reaches on its own, with no review at all**:
  `T_BOWLW-1` Barrow, `T_WLNYW-1` Walney 1, `T_WLNYO-2` Walney 2,
  `T_WTMSO-1` Westermost Rough (all D3, the OFTO enumeration) and
  `T_GNFSW-2` Gunfleet Sands 2 (D4, `II` read as `2`). These are grade B.
- **5 that already carried a side before any of this**, and still do: `T_AKGLW-2`
  Aikengall II, `T_CRYRW-3` Crystal Rig III, `T_CRYRW-4` Crystal Rig IV and
  `T_FALGW-1` Fallago Rig are on the CMIS intertrip arming list (grade A);
  `E_CRGTW-1` Craig 2 was graded C from its GSP group and is now grade B from
  `Craig II Wind Farm` (D4). No side changed. The classifier's list overstated
  its own novelty here: it read "no TEC row in the basis" as "unknown", which
  for these five it was not.
- **5 accepted as reviewed links (grade R)**: `T_BHLAW-1` Bhlaraidh (0.1 %
  capacity gap), `T_ANSUW-1` An Suidhe (0.3 %), `T_STRNW-1` Strathy North
  (3.4 %), `T_FARR-1` Farr 1 (0.0 %) — all north — and `T_OMNDW-1` Ormonde
  (0.5 %, south, placed from the OFTO enumeration and not from the label). Each
  was missed by the rule for the same reason: a BM-unit index or a lead-party
  word in the unit name that the register row does not carry.
- **2 rejected**:
  - `T_SOKYW-1` South Kyle, p 0.91. The name agrees exactly, but the BM unit is
    registered at 426.916 MW against a 235 MW row — 45 % apart against a 15 %
    tolerance. The register's only other South Kyle row (`South Kyle 2 Wind
    farm`, 92.4 MW, *Scoping*) does not close the gap either. Name agreement
    alone does not place a unit. **Not determinable from the declared evidence.**
  - `T_THNTO-1` Thanet, p 0.83. Thanet's two BM units are registered at 287.699
    and 230.159 MW, summing to 517.9 MW against a 300 MW row — 173 % of it.
    Neither limb of the capacity test is informative here, and `T_THNTO-1`'s
    4.3 % per-unit agreement with 300 MW is an arithmetic coincidence rather
    than evidence. Rejected, and `T_THNTO-2` with it. Both stay `unknown`.

**One sibling admitted alongside**: `T_FARR-2` Farr 2, proposed at 0.77 and so
below the queue cut, shares `T_FARR-1`'s register row and passes the per-unit
capacity limb on its own (92.000 MW against 92 MW). Placing one half of a
station and not the other would be an artefact of where the cut fell, so it is
admitted with its sibling and named here as a sibling admission rather than as
one of the 17.

### The side-of-B6 count, before and after

| | north | south | unknown |
|---|---:|---:|---:|
| Before (published pack, commit `cf7e519`) | 99 | 12 | 173 |
| After the corrected **rule** alone (grades A, B, C) | 99 | 17 | 168 |
| After the rule **and** the six reviewed links (grades A, B, C, R) | **104** | **18** | **162** |

Grades after: A 11, B 81, C 24, R 6, ungraded 162. Of the 162 still unknown, 51
are the id-less skeleton register rows, which no rule can reach.

Eleven units were newly placed and three had their basis corrected without
their side changing (`E_BABAW-1` Baillie, `2__PENEC001` Rothes, `E_BTUIW-3`
Beinn an Tuirc III, the last of which the D2 and D1 fixes lifted from grade C to
grade B). **No unit moved from one side of B6 to the other.**

### What is *not* adopted

The classifier put another 20 proposals in the 0.6 to 0.8 band, most of them the
multi-BMU offshore farms. They were **not reviewed** in this pass and none is
admitted. The declared group limb is recorded against them here so the next
pass starts from arithmetic rather than from a fresh judgement:

| Register row | BM units | Row MW | Group MW | Group gap | Would pass |
|---|---:|---:|---:|---:|---|
| Dudgeon Offshore Wind Farm | 4 | 400 | 402.0 | 0.5 % | group limb |
| Rampion Offshore Wind Farm | 2 | 400 | 400.2 | 0.05 % | group limb |
| London Array Offshore Wind Farm | 4 | 630 | 704.1 | 10.5 % | group limb (OFTO) |
| Galloper Wind Farm | 1 | 348 | 385.8 | 9.8 % | per-unit |
| Gunfleet Sands Offshore Wind Farm | 1 | 99.9 | 108.0 | 7.5 % | per-unit |
| Windy Standard II (Brockloch Rig) | 1 | 61.5 | 61.5 | 0.0 % | per-unit |
| Dogger Bank Project A | 1 | 1200 | 302.4 | 297 % | neither |
| Dogger Bank Project 4 (Dogger Bank B) | 2 | 1200 | 454.6 | 164 % | neither |

Dudgeon, Rampion and London Array are exactly what the group limb was written
for: no single BM unit is within 15 % of the row, and the four or two of them
together are within 0.5 %, 0.05 % and 10.5 %. Dogger Bank is the opposite case
— the register row is the whole project and the BM units are a fraction of it —
and would be refused.

### Effect on other investigations

**None.** 015's `side_of_b6` in
`src/grid_mysteries/investigations/support_and_storage.py` is left
byte-identical, defects and all: it is the rule that ran under 015's sealed,
externally witnessed declaration, and a sealed result is never re-run under a
rule it did not use. A test
(`test_015s_own_ladder_is_left_exactly_as_it_ran_under_its_seal`) pins that,
including 015's Baillie match. 015 graded sides for its 28 energy-limited units
only; none of the units corrected here is among them.

### What changed on disk

- `src/grid_mysteries/investigations/wind_forecast_pack.py` — the corrected
  ladder (`side_of_b6_corrected`) and its helpers, with each defect named in
  the code.
- `tests/test_wind_forecast_pack.py` — a test per defect, per limb of the
  capacity rule, and per property of grade R.
- `evidence/ofto-rows.json` — the 15 OFTO rows of this vintage with their
  landfall and side, checked by hand.
- `evidence/reviewed-links.json` — the admission rule, the proposer, the
  reviewer, and the eight reviewed candidates with their verdicts and reasons.
- `evidence/rule-sources.json` — the rule-to-test map, checked by `scripts/check`.
- `data/wind_units.csv` — regenerated; `side_of_b6`, `side_grade` and
  `side_basis` changed on 14 rows, and `north_of_b6` follows `side_of_b6`.
- `evidence/pack.json` — re-hashed, and now carries
  `wind_units_by_side_grade` and the digests of the two evidence files the
  ladder reads.

**If you already hold a copy of the pack**, only `wind_units.csv` changed. No
other CSV, no pinned byte and no acquisition was touched; `run.py --phase
export` reproduces every file from the same pinned bytes. Read `side_grade`
before using a side, and drop grade `R` if you would rather not rely on a
human-admitted link.
