# 013 — the cover price tracker: Amendment 1

**Frozen on its own**, by `scripts/freeze` (OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert, committed with the file), so that `AMENDMENTS.md` can keep growing. `DECLARATION.md` (SHA-256 `d20d59203e7b7fda174c2c6deb2807159687bd9ddea39fe760961af884416473`, sealed 2026-09-11) and `DECLARATION-T4.md` (frozen 2026-09-19) stand unchanged.

## Amendment 1 — L3 (Disaggregated BSAD) is append-only, first vintage kept; T1 is decided on the first confirmed reading

**Dated 2026-09-25, 22:30 UTC.** Written after batch 1 was computed
(2026-09-19) and before any Elexon data for a settlement day from
2026-09-16 was fetched: batch 2 is fetched by `tracker-013` at 09:00 UTC on
2026-09-26. Taught by the record-engine kill test of 2026-09-25
(`bill/KILL-TEST.md`), not by any tracker day, so the rule may run against
batch 2 and later; on batch 1 it moves no figure (verified below).

**What the declaration says.** Column 8 (NESO's L1 and L4) is "appended as
outcome with the vintage date. The first vintage that carries the day is
kept; a later vintage that differs is listed as a revision, and the first
is never edited." Column 7 (L3, Disaggregated BSAD net £ and its share of
`paid_out`) has no such rule; the declaration only records "the NESO
vintage read for L3".

**What the instrument does.** `tracked_row` reads L3 from the latest NESO
vintage on disk at compute time. So a recompute on a later day re-reads
every committed day's BSAD from a newer file. The kill test showed it: an
unchanged recompute on 2026-09-25 moved `bsad_vintage` from 2026-09-19 to
2026-09-25 on all seven tracked days, silently, exit 0. The values did not
move that day, but NESO fills days over more than one vintage: in the
pinned files, 2026-09-15, 09-16, 09-17 and 09-18 each first appear as 48
zero rows, fill in the next vintage or two, and 2026-09-16 grew again
between two populated vintages (441 rows and £1,500,802, then 616 rows and
£1,552,051). A committed BSAD figure could therefore change on the public
page with no trail, which the declaration permits and the project's
"committed row never changes" rule does not.

**What "provisional" was.** A hand-typed list of two days (2026-09-12 and
2026-09-13, `PROVISIONAL_BSAD_DAYS`), marked § on the page with the note
that NESO may not have finished filling them. A judgement, not a rule; it
is retired by this amendment.

**Amendment.**

1. **L3 is append-only.** For a tracked day, every pinned NESO vintage is
   read in date order. The reading of the **first vintage in which the day
   is populated** (at least one non-zero row, 012 Amendment 1) is kept as
   the row's `bsad_vintage`, `bsad_net_gbp`, `bsad_share` and `bsad_rows`,
   and is never edited. A later vintage whose reading (rows, net £) differs
   from the last one listed is appended to `bsad_revisions` with its
   vintage date. A day populated in no pinned vintage stays unpopulated
   (blank, never zero), as before.
2. **A reading is confirmed by the next vintage.** The first populated
   vintage whose reading is reproduced unchanged (rows and net £) by the
   next pinned vintage is the day's `bsad_confirmed_vintage`. Until one
   exists the day's L3 is **provisional** (`bsad_provisional: true`,
   marked § on the page). This replaces the hand list; the § note now says
   what the mark means.
3. **T1 is decided on the confirmed reading.** For a record day, T1's
   instance uses the share of `paid_out` from the confirmed vintage
   (`bsad_deciding_share`), which may differ from the first reading shown
   on the page; a record day with no confirmed reading yet leaves T1
   undecided for that day, never failed. Seed rows are unchanged: their L3
   is 012's, copied, and 012's Amendment 1 already treats all-zero days
   as unpopulated.

**Effect on batch 1 (measured by recomputing batch 1 under the amended
rule from the same pinned bytes).** No figure moves. `bsad_vintage` on the
seven tracked days becomes the first populated vintage (2026-09-15 for
2026-09-09 to 09-14, 2026-09-17 for 2026-09-15) instead of the vintage
that happened to be latest at compute time; the values in those vintages
are the ones already on the page. 2026-09-12 and 2026-09-13 have been
identical across all eleven pinned vintages, so under rule 2 they are
confirmed and lose the § mark; the caution that NESO might still fill
them is replaced by the rule that says when a reading counts. Verified
in this checkout on 2026-09-25 before this file was frozen: a compute under
the amended rule from the pinned bytes, compared row by row with the
committed `tracker.json` of `0033bf5`, differs only in `bsad_vintage` (as
above) and in `outcome` (the declared L1 append from vintages pinned since
19/09); every other field, the artefact lists included, is identical, and
T1, T2 and T3 stand as they were. The file produced by that check was not
kept; batch 1 is recomputed with batch 2, under this rule.

**Implemented in** `cover_price.bsad_by_vintage` (pure over the readings
in vintage order), `run.py::tracked_row` (reads every vintage, not the
latest), `cover_price.evaluate` (T1 on the deciding share) and
`cover_price.render_table` (the § note), with tests for first-kept,
revision listing, confirmation, the provisional flag and T1's use of the
confirmed reading.
