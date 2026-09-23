# 014 — GB Connection Slippage: declaration, version 3

**Frozen**: 2026-09-23 with `scripts/freeze`, which witnesses this file by
OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert and
commits it with the proofs. Sealed by the sponsor's instruction of
2026-09-23 ("Seal 014 declaration v3 with two edits, then freeze"). Release
of the page remains the separate second seal, and version 3 is meant to be
in force before the series is first announced.

## What this version is, and is not

Versions 1 (`DECLARATION.md`, SHA-256 `e4aba4c9…`) and 2
(`DECLARATION-v2.md`, SHA-256 `f2209b3c…`) stand as run, with their
evidence under `evidence/` and `evidence/v2/`. This version **restates how
the figures are reported**, not the question, the unit, the reading rules,
the arithmetic, the baselines, the segments, the windows or the
propositions, all of which are inherited from version 2 verbatim.

One thing changes. Every movement figure the series reports is split into
the part the register itself determines and the part that depends on an
identity rule, and the second part is published under each of two named
rules. The two are not bounds: other pairings are possible and are not
bounded here. The figure version 2 publishes is one of the two.

## Why (forced by an artefact made after version 2 was frozen)

The TEC record engine (`tec/`, built 2026-09-23 from the sponsor's brief of
the same day) holds every publication as NESO printed it and reproduces
version 2's 698 committed rows byte for byte from that record
(`tec/analysis/differential-014.json`). Running version 2's arithmetic with
a second identity rule (content matching, `tec-identity-content-v1`)
showed that the unit rule of version 1 ("where stages are not distinct, an
identity's rows are ordered by effective date then cumulative capacity and
numbered") decides some of the figures: it pairs a row of one copy with a
row of another where the register does not say they are the same, and
when two dates in one project cross, it re-pairs them. Both rules are
defensible; neither pairing is a published move.

## Prior exposure (recorded, not hidden)

The author has seen, from the record at anchor `tec/anchors/tree-137384.json`
(`tec/analysis/series-content-v1.json`, `flapping.json`):

- the headline (2024-07-19 to 2025-07-22) under version 2's rule, +57,823.493
  MW-years, and under content matching, +61,542.867; the 16 project groups
  in which they differ (Fiddlers Ferry BESS, Rat Hall Mod App, Sofia
  Offshore Wind Farm, Capenhurst, Lovedean Tertiary and eleven others), and
  that without the 54 groups defined below both give +57,400.290;
- the chained total of the old regime under version 2's rule, +532,780.315,
  and under content matching, +534,180.588; that the rules differ on 57 of
  693 links, only in groups defined below; and that without those groups,
  link by link, both give +392,125.567;
- date moves reversed by the unit's next move: 6 of 87 under version 2's
  rule are not printed that way in the files, 0 of 81 under content
  matching.

**Two edits were made after the sponsor's review of the draft, on
2026-09-23, before freezing.** (1) The headline sentence names two rules
instead of stating bounds (the sponsor's wording), and the same
two-named-rules wording replaces every place the draft spoke of a range,
its ends, or the lower and higher figure. (2) The undetermined share of
the chained total is stated beside it as a percentage; on the figures
already seen it is 26.4% under version 2's rule (140,654.748 of
532,780.315) and 26.6% under content matching (142,055.021 of
534,180.588). Nothing else changed from the draft committed at `a75d772`.

**The definition below was chosen after seeing that it closes both gaps
exactly.** It is a reporting rule, and it cannot change any proposition's
verdict: P1 and P2 are inherited unchanged and are decided, as before, on
the figures version 2's rule gives (below). This version therefore cannot
improve the propositions' record.

## The definition

For a comparison of a baseline copy *B* with a current copy *C*, a
**project group** is version 1's identity (the normalised project name,
customer name and connection site). A group present in both copies has an
**undetermined pairing** when either:

1. the multiset of its printed stage labels (numerals unified by reading
   rule 5, blank counted as a label) differs between *B* and *C*: a split,
   a merge or a renumbering; or
2. a label, blank included, is printed on more than one of its rows in *B*
   or in *C*.

In every other group each row carries its own stage label, the same set on
both sides, so every identity rule that pairs a stage with the stage of the
same label gives the same figure. That is the **determined part**.

## What every movement figure reports

For every trailing-year comparison (the headline is the latest), every
increment of the chain, and every calendar-year window:

- **determined**: the movement summed over units of groups whose pairing is
  determined, by version 2's arithmetic;
- **undetermined, version 2's rule**: the movement summed over units of
  groups with an undetermined pairing, as version 2 pairs them;
- **undetermined, content matching**: the same groups, paired by
  `tec-identity-content-v1` (`src/grid_mysteries/tec/identity.py`, SHA-256
  `a0ee2ac0dcc6919e37061f89a5b0fc1c663cf566cb1a7df3a55f75c761aa0fb8`),
  whose units are carried from copy to copy within a segment;
- the number of groups with an undetermined pairing, and the movement
  under each rule: the determined part plus that rule's undetermined
  figure, named by its rule. The two are not bounds; other pairings are
  possible and are not bounded here.

The chained total is reported the same way: the determined parts of the
increments summed, and the chain under each rule. Beside the chained total
stands the undetermined share of it under each rule, as a percentage
(about 26% on the figures already seen). Version 2's figure is always one of
the two and is still reported by name, so no published number disappears.

The headline is written in this form: "+57,400 MW-years is movement the
register's own stage labels determine. 54 project groups that were split,
merged, renumbered or printed repeated stages add +423 under version 2's
rule and +4,143 under content matching, so the headline is +57,823 or
+61,543 depending on the rule; other pairings are possible and are not
bounded here."

## Falsifiers of the instrument (added)

- **F4** On any comparison, the two rules give different movements for a
  group whose pairing is determined: the definition is wrong. The run
  refuses, and the cause is recorded before any rerun.
- **F5** The content rule's file no longer hashes to the digest above: the
  run refuses. A changed rule is a new declaration.

F0 to F3 are inherited.

## What is inherited unchanged from version 2

Everything not stated above: the mystery; the inputs, the archive and the
journal as the series' source (the TEC record reproduces it, but the
series does not read from it); the hole and the regime break; reading
rules 1 to 5 with version 2's aliases and partial-export rule; the unit;
the headline arithmetic and its reconciliation items; baselines, chain,
windows and the 60-day hole rule; P1 and P2 with their falsifier dates,
decided on version 2's rule; F0 to F3; what the series never claims; and
the limits declared in advance. Where this file is silent, version 2 speaks.

## Outputs

- `evidence/v3/rows.ndjson` (append-only, one line per usable copy: version
  2's row plus the split above for its trailing-year comparison and its
  increment), `evidence/v3/series.json` (the summary, with the split for
  the headline, the chain and every window), `evidence/v3/vintage-manifest.json`,
  `evidence/v3/run-log.json`.
- `SERIES.md` and `site/connection-slippage/index.html`, pure functions of
  the version 3 evidence; version 2's record page is kept as `SERIES-v2.md`.
- `evidence/rule-sources.json` names the test behind every rule, checked by
  `scripts/check-rules`, including the definition and F4.
