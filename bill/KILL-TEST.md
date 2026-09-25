# The Balancing Bill as a record: the kill test (25/09/2026)

Before building a second record engine for investigation 013 (the
Balancing Bill), the cheapest question capable of killing it: **does the
kernel refuse something the current runner accepts silently?** If not,
a thirty-line Python guard would do and the engine is not built.

## Method

Batch 1 of 013 (settlement days 2026-09-09 to 2026-09-15, plus the eight
seed rows) as committed in `evidence/tracker.json` at `0033bf5`, recomputed
twice in a scratch checkout from the same pinned bytes:

1. **unchanged**: the committed code, run on 25/09/2026;
2. **altered**: one constant changed, the volume gate's reconciliation
   tolerance from 0.1 % to 5 % (`RECONCILE_TOLERANCE` in
   `cover_price.py`), the kind of "small fix" a future session might make.

Against them, a one-predicate programme (`kill-test/bill-register.morph`):
`DayRow(day, rule, source, …figures…, artefacts_digest)`, `unique by (day,
rule)`, append only, with one transformation `add_day` whose only gate is
`day_is_new`. `kill-test/rows.py` turns tracker rows into proposals (the
figures as printed, `-` where not computable, and the SHA-256 over the
sorted digests of the row's artefacts); `kill-test/offer.py` skips rows
that already stand identically and proposes the rest. The programme is on
the compiled route (`morpholog check -v`). Throwaway database, dropped
afterwards.

## Measured

| | current runner (`run.py --phase compute`) | the record |
|---|---|---|
| committed rows imported | n/a | 15 committed |
| same rows offered again | rewrites the file, exit 0 | 15 refused `day_is_new`; nothing changes |
| unchanged code, recomputed six days later | **rewrites 8 of 15 rows**, exit 0: `outcome` filled for 6 days (the declared append), and `bsad_vintage` plus `artefacts` moved on all 7 tracked days | the 7 changed rows refused by name, 8 identical rows skipped |
| altered tolerance | **rewrites 7 of 15 rows**, exit 0: 2026-09-13 gains a price (`none reconciles` → `Tagged`, £242.35/MWh, premium £42.82) and the six others carry a new `reconciliation` block | the 7 changed rows refused by name |
| what is left behind | a diff in git, if anyone reads it | 29 refusals in the rejection log, each naming the day and the failed gate; 15 claims stand |

## Verdict

**The engine survives.** The kernel refuses, by name and with a log, what
the runner rewrites without a word. A Python guard could refuse too, but it
would be the runner policing itself, with no record of the attempt and no
witnessed checkpoint over what stands.

## What the test found about 013 itself, which matters before batch 2

The declaration gives L1 and L4 (NESO's Constraints £ and MWh) the rule
"first vintage kept, later vintages listed as revisions, never edited".
It gives **L3 (Disaggregated BSAD) no such rule**: the runner reads BSAD
from the latest NESO vintage on disk at compute time and records which
vintage it read. On 25/09 the values had not moved, but the provenance had
(`bsad_vintage` 2026-09-19 → 2026-09-25 on every tracked day), and the
tracker itself marks 12 and 13 September's BSAD as provisional. Batch 2's
compute will read batch 1's L3 from the 26/09 vintage. If NESO has filled
those days by then, two committed figures change on the public page with
no revision trail. The declaration permits it; the "committed row never
changes" doctrine does not.

Options for the sponsor, before batch 2 is computed:

1. leave L3 as declared (it floats with the latest vintage; the vintage
   read is recorded per row), and say so on the page;
2. amend: L3 becomes append-only like L1 (first vintage kept, later ones
   listed), applied from batch 2's compute onward. On batch 1 this keeps
   the 19/09 reading, which is what stands today, so no committed value
   moves; the amendment is dated in `AMENDMENTS.md` and its rule is that
   batch 2's data did not teach it (this test did, on 25/09, before batch
   2 was fetched).

Either way, the runner should refuse to change a committed row's declared
figures on recompute, and that is what the record engine is for.

## Not measured

Whether the record's as-of read or a per-day certificate has a reader.
That was not the question tonight; the question was whether the kernel
earns its place at all, and it does.
