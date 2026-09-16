# 014 — GB Connection Slippage: declaration, version 2

**Frozen**: 2026-09-16 with `scripts/freeze`, which witnesses this file by
OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert and
commits it with the proofs. Sealed by the sponsor's instruction of
2026-09-16 ("proceed with your recommendations") to restate the series'
reading under a second declaration published beside the first. Release of
the page remains the separate second seal.

## What this version is, and is not

Version 1 (`DECLARATION.md`, SHA-256 `e4aba4c9…`, witnessed 2026-09-15
20:12 UTC, run the same day) stands as run: its evidence under `evidence/`
and its rows are not edited, and its runner refuses to change them. This
version **restates the reading**, not the question, the unit, the headline
arithmetic, the baselines, the segments or the propositions, all of which
are inherited from version 1 verbatim and are not repeated here except
where a rule changes. Three things change, each forced by an artefact made
after version 1 was frozen:

1. **Reading rule 2, column aliases.** The archive schema report
   (`archives/tec-register/schema-report.json`, SHA-256
   `3213dca108f27cb90eb5febbb4b47b83ac213f484598081aff971fd7dd72fd2c`,
   committed at `b891080`) showed that the three copies version 1 excluded
   for "lacking an identity column" (2020-07-09, 2020-07-16, 2020-07-23)
   carry the customer column under the header **"Customer"**, and that
   2020-07-23 spells plant type "Electricity Connection: Plant Type". Both
   are mapped. The exclusion rule itself is unchanged; those copies no
   longer meet it. Only 2021-06-22, whose header row does not parse,
   remains outside.
2. **A partial-export rule.** Per regime segment, in date order: a copy
   whose row count falls by more than **one fifth** against the previous
   kept copy is *suspect*. It is **excluded** from the series (it takes no
   part in any link, baseline or annual window, and the chain skips it)
   only if the following copy's row count is more than one fifth above
   the suspect copy's; a shrink that persists is a real shrink, so the
   copy is **kept and marked**, and it becomes the baseline for the next
   comparison. Every suspect copy is listed with its counts, whether
   excluded or kept. The rule is symmetric by design so that it cannot
   remove a copy whose only fault is being inconvenient. The schema report
   flags two copies, 2015-05-08 and 2023-11-28; the rule, not the report,
   decides.
3. **Evidence layout.** Rows are **append-only**: `evidence/v2/rows.ndjson`
   holds one line per usable copy (the row exactly as version 1 defined
   it, plus its regime), appended by each run and never rewritten; a line
   that would change on recompute stops the run, as before.
   `evidence/v2/series.json` holds the summary (headline, annual windows,
   propositions, flags, suspect copies, gaps, counts, this declaration's
   digest and timestamps, the schema report's digest) and is rewritten
   each run. The page shows the last 400 days of individual copies and
   links the rows file for the rest. `SERIES.md` is version 2's record
   page; version 1's is kept as `SERIES-v1.md`.

## Prior exposure (recorded, not hidden)

The author has seen version 1's results in full: a headline of
+57,823.493 MW-years for 2024-07-19 to 2025-07-22 over 1,147 matched
project-stages, a chained total of +533,046.984 MW-years, P1 holding in
all eleven complete years, P2 undecided, F1 on eleven links, F2 on 191
rows. A `--phase check` run under version 1's rules with the two aliases
applied reported that 420 of the 697 committed rows would change, all of
them through the chained total and the trailing-year rows after
2020-07-30; no annual window changes its endpoints. **The propositions are
therefore not re-chosen**: P1, P2 and their falsifier dates are inherited
unchanged, so this version cannot improve their record, only restate the
reading they are decided on. No figure under the partial-export rule has
been computed before this freeze.

## What is inherited unchanged from version 1

The mystery; the inputs and the archive; the hole and the regime break;
reading rules 1, 3, 4 and 5; the unit; the headline and its
reconciliation items; the baselines, the chain, the calendar-year windows
and the 60-day hole rule; propositions P1 and P2 with their falsifier
dates; instrument falsifiers F0 to F3; what the series never claims; and
the limits declared in advance. Where this file is silent, version 1
speaks.

## Outputs

- `evidence/v2/rows.ndjson`, `evidence/v2/series.json`,
  `evidence/v2/vintage-manifest.json`, `evidence/v2/run-log.json`.
- `SERIES.md` and `site/connection-slippage/index.html`, pure functions of
  the version 2 evidence.
- `evidence/rule-sources.json` names the test behind every rule of both
  versions, checked by `scripts/check-rules`.
