# 014 — GB Connection Slippage: declaration, version 4

**Frozen**: 2026-09-23 with `scripts/freeze`, which witnesses this file by
OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert and
commits it with the proofs. Sealed by the sponsor's instruction of
2026-09-23 ("Seal 014 declaration v4 with one edit, then freeze"). Release
of the page remains the separate second seal, and this version is meant to
be in force before the series is first announced.

## What this version is, and is not

Versions 1 (`DECLARATION.md`, SHA-256 `e4aba4c9…`) and 2
(`DECLARATION-v2.md`, SHA-256 `f2209b3c…`) stand as run. Version 3
(`DECLARATION-v3.md`, SHA-256 `435988c7…`) stands as frozen and **was never
run to completion**: its first compute refused on its own falsifier F4 and
wrote no evidence (`AMENDMENTS.md`, 2026-09-23). This version replaces
version 3's **definition of a determined pairing**, and only that. It keeps
version 3's reporting (every movement figure split into the part the
register's stage labels determine and the figure under each of two named
rules, which are not bounds), its content rule exactly as declared, its
falsifiers F4 and F5, and everything version 3 inherits from version 2.

## Why (forced by version 3's own falsifier)

F4 reads: *"On any comparison, the two rules give different movements for
a group whose pairing is determined: the definition is wrong."* It fired on
27 comparisons (26 trailing-year, 1 calendar-year window) in four groups
(Barry Power Station, Bramford Tertiary, Corby, Thorpe Marsh). Version 3's
definition judged a group determined by the two copies compared alone,
while the declared content rule follows each row through every copy in
between. A group can print the same single stage label at both ends and be
restructured in between: Barry Power Station printed one row (-136 MW, for
2016-04-01) on 2015-04-13, a second row (+235 MW, for 2018-04-01) under the
same blank stage by 2016-03-07, and only the +235 MW row on 2016-04-12.
Version 3 called that pairing determined; the intermediate copies say it
is not.

## Prior exposure (recorded, not hidden)

Everything version 3's prior-exposure section records, and in addition,
from the diagnosis of version 3's refused compute (recorded in
`AMENDMENTS.md`, 2026-09-23):

- which comparisons and groups failed F4, and by how much (23,152.735
  MW-years in absolute terms);
- **the figures of both options for a restated definition, seen before this
  one was chosen**. Option (a), this version's definition: headline
  2024-07-19 to 2025-07-22 determined +53,221.271 over 88 groups, +4,602.222
  under version 2's rule, +8,321.596 under content matching. Option (b),
  version 3's definition kept with the content rule run on the two copies
  compared alone: determined +57,400.291 over 54 groups, +423.202 under
  version 2's rule, +2,531.432 under content matching (content total
  +59,931.723). Under both, the chain is unchanged: determined +392,125.567,
  +532,780.315 under version 2's rule, +534,180.588 under content matching;
- that under option (a) F4 holds on every comparison of the series.

**Option (b) was declined, by the sponsor, for two reasons.** F4's own text
names the definition as the thing to fix, not the rule it tests. And (b)
would call a pairing "determined" that the intermediate copies contradict:
under (b) Barry Power Station's -136 MW reduction and +235 MW row would be
paired as determined, because the two ends alone do not show the second row
arriving. Both sets of figures were in view when (a) was chosen; (a)
gives the smaller determined part.

**One edit was made after the sponsor's review of the draft, on
2026-09-23, before freezing:** the headline sentence takes the sponsor's
wording, which names groups "that went missing from a copy between"
separately from those restructured at either end or in a copy between.
Nothing else changed from the draft committed at `df4afdd`.

P1 and P2 are inherited unchanged and decided on version 2's figures, so
this version cannot improve the propositions' record.

## The definition

For a comparison of a baseline copy *B* with a current copy *C* of the same
segment, a **project group** is version 1's identity (the normalised project
name, customer name and connection site). The **copies of the comparison**
are *B*, *C* and every copy of the segment between them that the series
uses (a copy excluded by version 2's partial-export rule takes no part, as
in every other figure). A group present in both *B* and *C* has an
**undetermined pairing** when, in the copies of the comparison:

1. the multiset of its printed stage labels (numerals unified by reading
   rule 5, blank counted as a label) is not the same in every copy; a copy
   that does not print the group at all counts as a change; or
2. a label, blank included, is printed on more than one of its rows in any
   copy.

In every other group each row carries its own stage label, and the same
set, in every copy from *B* to *C*, so every identity rule that pairs a
stage with the stage of the same label, directly or copy by copy, gives the
same figure. That is the **determined part**. For consecutive copies (the
increments of the chain) the copies of the comparison are *B* and *C* alone,
so this definition and version 3's coincide there.

## What every movement figure reports

As version 3 declares, with this definition: for every trailing-year
comparison (the headline is the latest), every increment of the chain and
every calendar-year window, the **determined** part; the **undetermined**
part under version 2's rule and under content matching
(`tec-identity-content-v1`, `src/grid_mysteries/tec/identity.py`, SHA-256
`a0ee2ac0dcc6919e37061f89a5b0fc1c663cf566cb1a7df3a55f75c761aa0fb8`,
unchanged from version 3, units carried from copy to copy within a
segment); the number of groups with an undetermined pairing; and the
movement under each rule, the determined part plus that rule's
undetermined figure, named by its rule. The two are not bounds; other
pairings are possible and are not bounded here.

**Rounding.** A determined part is rounded by version 2's convention for a
net: its two gross sides (movements later, and movements earlier) are each
rounded to 0.001 MW-years and the net is their sum. The undetermined part
under a rule is that rule's net, rounded the same way, minus the
determined part, so the two always add up to the rule's published figure.

The chained total is reported the same way, with the undetermined share of
it under each rule as a percentage beside it (about 26% on the figures
already seen).

The headline is written in this form: "+53,221 MW-years is movement the
register's own stage labels determine. 88 project groups that were split,
merged, renumbered or printed repeated stages, at either end or in any copy
between, or that went missing from a copy between, add +4,602 under
version 2's rule and +8,322 under content matching, so the headline is
+57,823 or +61,543 depending on the rule; other pairings are possible and
are not bounded here."

## Falsifiers of the instrument

- **F4** On any comparison, the two rules give different movements for a
  group whose pairing is determined (movements compared exactly, each
  group's summed in a fixed order): the definition is wrong. The run
  refuses, and the cause is recorded before any rerun.
- **F5** The content rule's file no longer hashes to the digest above: the
  run refuses. A changed rule is a new declaration.

F0 to F3 are inherited.

## What is inherited unchanged

From version 3: the reporting above, except the definition it replaces.
From version 2, everything version 3 inherits: the mystery; the inputs,
the archive and the journal as the series' source; the hole and the regime
break; reading rules 1 to 5 with version 2's aliases and partial-export
rule; the unit; the headline arithmetic and its reconciliation items;
baselines, chain, windows and the 60-day hole rule; P1 and P2 with their
falsifier dates, decided on version 2's rule; F0 to F3; what the series
never claims; and the limits declared in advance. Where this file is
silent, version 3 speaks, and where version 3 is silent, version 2.

## Outputs

- `evidence/v4/rows.ndjson` (append-only, one line per usable copy: version
  2's row, byte for byte, plus the split for its trailing-year comparison,
  its increment and the chain), `evidence/v4/series.json` (the summary, with
  the split for the headline, the chain and every window),
  `evidence/v4/vintage-manifest.json`, `evidence/v4/run-log.json`.
- `SERIES.md` and `site/connection-slippage/index.html`, pure functions of
  the version 4 evidence, written only at release; version 2's record page
  is then kept as `SERIES-v2.md`.
- `evidence/rule-sources.json` names the test behind every rule, checked by
  `scripts/check-rules`, including the definition, F4 and F5.
