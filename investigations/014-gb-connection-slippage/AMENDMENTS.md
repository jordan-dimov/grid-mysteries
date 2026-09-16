# 014 — amendments and dated findings

`DECLARATION.md` is frozen (SHA-256 `e4aba4c9…`, witnessed 2026-09-15 20:12
UTC). Everything learned after it is written here, dated. An amended rule
applies from the next copy forward and never restates a row it learned
from; a restated history is a new declaration published beside this one.

## Finding, not amendment — 2026-09-16: the three July 2020 copies were excluded for a reader gap, not a NESO omission

The declaration's prior-exposure section says four copies "lack an identity
column" (2020-07-09, 2020-07-16, 2020-07-23, 2021-06-22), and the first run
excluded the three July 2020 copies under reading rule 2. The archive schema
report (`archives/tec-register/SCHEMA.md`, introduced 2026-09-16) shows the
cause: those three copies carry the customer column under the bare header
**"Customer"**, which the reader's alias table did not map. The column was
present; the reader was not. (2021-06-22 is different: its header row never
parses.) The shared reader now maps "Customer" and "Electricity Connection:
Plant Type" (the 2020-07-23 spelling).

**Effect on the sealed series: none applied.** The committed
`evidence/series.json` was computed with the three copies excluded, exactly
as the declaration's rule read them at the time, and `run.py` refuses to
change a committed row without `--amend`. `run.py --phase check` (added
2026-09-16) measures the effect: with the three copies included, **420 of
the 697 committed rows would change**, because the chained total
(`cumulative_mw_years_net`) carries every increment forward from 2020-07-30
and the trailing-year rows whose baseline falls in the affected window
move too; the annual windows keep their endpoints, and the headline row's
year-on-year figure is unaffected. Whether to recompute under `--amend`
(a restated chain, recorded as such) or to leave the first publication as
run is the sponsor's decision, recorded here when made.

## Finding — 2026-09-16: two copies look like partial exports and are inside the series

The schema report flags **2015-05-08** (row count fell 46 % against the
previous copy) and **2023-11-28** (fell 52 %). Both are in the series as
ordinary copies; the declaration has no partial-export rule. F1 fired on
both links, which is the instrument doing its job after the fact. The
2023-11-28 copy is also the one in which Clash Gour was absent for one copy
in the certificate exemplar. A rule excluding copies whose row count falls
by more than a fifth against the previous copy, or reporting them as
suspect, belongs in the next declaration of this series and in the
certificate template, not in this one by amendment.
