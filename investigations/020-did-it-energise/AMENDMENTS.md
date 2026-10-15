# 020 — dated findings outside the frozen amendments

The declaration (`fb8a3428…`) and amendments 1 to 4 are frozen files with
their proofs. What is learned between amendments is written here, dated;
a changed rule or a changed population is a further frozen amendment,
never an edit.

## Finding, not amendment — 2026-10-15: the 301-day hole is closed, and the population would change

NESO's EIR response FOI/26/216 (13 October 2026) put 83 TEC Register copies
of 2025-07-25 to 2026-05-15 into the archive on 2026-10-15
(`investigations/005-connection-date-credibility/ACQUISITION-FOI-26-216.md`).
Amendment 4 reads a project's copy gap as the days since the kept copy
before it in the combined sequence, "which is 301 days at 19/05/2026"; the
register-lag figures for 2025 and 2026 in `RESULTS.md` and the two charts
for the joint paper (`figures/captions.md`, 14/10/2026) carry that bound.

**Measured on 2026-10-15 without writing** (the population step of
`run.py --phase population` re-run in memory against the committed
`evidence/population.ndjson`, stopping before C2 would): over 791 usable
and 789 kept copies, 1,719 units have a first `Built` sighting against the
1,672 lines committed. **1,296 lines are unchanged; 373 would change, all
in the reformed regime** (their first `Built` copy moves from 2026-05-19 to
a copy inside the hole, 2025-12-02 for the first of them, and `first_seen`
with it; 11 also change customer, 3 change the copy before and its date);
**50 units are new** (29 reformed regime, 21 old regime, first printed
`Built` inside the hole); **3 committed units no longer have a first
`Built` sighting** under the same key. The run would refuse at C2 on the
first changed line, so nothing was written and nothing under the
declaration or amendments 1 to 4 changes.

**What follows, under this investigation's rules.** The population of
version 1 (amendment 4's 164 projects) was drawn from the committed lines;
a population drawn over the filled hole is a new rule version: a frozen
amendment 5 declaring the recompute, new J1 proposals for the units that
become measurable, a person's admissions (amendment 3, B3), B1610 walks
for the admitted units, and the labels and the register's lag re-run with
copy gaps no longer bounded by 301 days. That is the sponsor's decision,
recorded here when made. Until then every figure stands as computed on
2026-10-12 under amendment 4, with the 301-day bound stated.
