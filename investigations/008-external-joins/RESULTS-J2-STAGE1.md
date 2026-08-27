# 008 · J2 stage 1 — results: **not determinable** as sealed

**Run**: 2026-08-27, `run_j2_stage1.py`, storage-only cohort exactly as
sealed in `DECLARATION-J2-SPV-FINANCING.md` (sha256 `8bdfedcc…`, commit
`831d061`). Sponsor chose to run the sealed cohort rather than widen it.
Inputs: 105 Companies House responses (43 searches, 31 profiles, 31
charge lists) pinned under `data/raw/companies-house/2026-08-27/`, manifest
copied to `evidence/j2-stage1-manifest.json` (sha256 `89c23c44…`); output
`evidence/j2-stage1.json`.

## Verdict under the sealed rule

Built arm **26** projects, Scoping arm **29** — both below the sealed
minimum of 40 per arm. **Not determinable.** No kill, no survival, no
decision sentence; under the age/timing guard nothing here could carry one
anyway.

## The screen figures, published as the screen they are

Portfolio customers (≥ 5 TEC projects) are split out as declared.

| arm | projects | resolved | resolved share | any charge | charge created **after** TEC first appearance | median company age at last vintage |
|---|---|---|---|---|---|---|
| Built, non-portfolio | 15 | 10 | 67 % | **10 / 10** | 5 / 10 | 6.2 y |
| Scoping ≥ 3 y, non-portfolio | 21 | 13 | 62 % | **5 / 13** | 1 / 13 | 5.0 y |
| Built, portfolio customers | 11 | 11 | 100 % | 9 / 11 | 6 / 11 | 7.5 y |
| Scoping ≥ 3 y, portfolio customers | 8 | 8 | 100 % | 7 / 8 | 2 / 8 | 7.5 y |

Observed, nothing more: every resolved non-portfolio Built SPV has a
registered charge and half of them registered one after the project
appeared in TEC; among long-Scoping non-portfolio SPVs the figures are
5 of 13 and 1 of 13. The Built companies are also about a year older.
With ten and thirteen companies these are not estimates of anything;
they are the reason a widened cohort would be worth the calls.

## Identity, as found

43 customer names → 31 unique active exact matches (72 %), 11 no exact
match, 1 exact but dissolved. The misses are informative for Stage 2's
resolution table:

- **renames**: `HARMONY PW LIMITED` (TEC) is now `HEIT PW LIMITED` at
  Companies House (Harmony Energy Income Trust); an exact-current-name rule
  cannot see this. A previous-names search would.
- **search depth**: `IGP SOLAR 19/20/21/25 LIMITED` are not in the top-20
  hits for their own names (Companies House relevance ranking); a
  `company_name_includes` or advanced search would find them.
- **dissolved SPVs**: `ORGANIC POWER LTD` (03432968) is dissolved — for a
  project still Scoping in TEC, that is itself a finding class Stage 2
  should count, not discard.

The resolution rule is kept as sealed for this run; improving it is a
Stage-2 amendment, declared before Stage 2's fetch.

## What happens next

Nothing under this declaration: it says a below-minimum cohort is
recorded as such. A widened cohort (all plant types: 125 / 112) is a
pre-fetch amendment the sponsor may make; if made, the storage projects
fetched here are reused from their pinned copies (the journal refuses to
refetch), and the widened run is the first run that can be scored.
