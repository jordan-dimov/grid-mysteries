# 015 — declaration, version 2: a CfD link by name for the unmatched remainder

**Frozen**: 2026-09-16 with `scripts/freeze`, witnessed by OpenTimestamps and
RFC 3161 tokens from freetsa.org and DigiCert and committed with the proofs.
**Not run.** Raised by the sponsor's instruction of 2026-09-16 after the
version 1 result, to be run only on a separate instruction; everything not
restated here is inherited from `DECLARATION.md` (SHA-256 `77a192f1…`)
verbatim, including both populations, the volume gate, Part 2 in full,
propositions S2 and B1, and every falsifier.

## Why a second version

Version 1 found the 8 September wind bid split **not determinable**: 45.0 %
of the wind bid money went to units the declared links could not place,
because LCCC's CfD-to-BM-unit mapping (165 rows) does not carry the BM
units of Moray West, Seagreen, Bhlaraidh or South Kyle, and version 1
allowed a CfD link only by that identifier. The question the thread asked
deserves the next rung of evidence, declared before it is looked at.

## Prior exposure (recorded, not hidden)

The author has seen version 1's results in full, including the ten largest
unmatched units by name and cashflow, and knows from the schema pass that
the portfolio carries `Name_of_CFD_Unit`, `Technology_Type`,
`Maximum_Contract_Capacity_MW` and `Status`. No name match against the
portfolio has been computed. The declared rule below was fixed without
testing whether any particular unit passes it.

## The one new rule: CfD grade B, by name and capacity

For a wind unit with no grade-A CfD link, a **grade B CfD link** exists to a
portfolio row when all three hold:

1. the row's `Name_of_CFD_Unit`, normalised by version 1's name test
   (lower-case alphanumerics, the same generic tokens removed, and
   additionally the tokens *string, strings, phase, ph, part* removed), is
   equal to or a token-superset of the unit's `bmUnitName` normalised the
   same way, **or** the unit's name tokens are a superset of the row's;
2. the row's `Maximum_Contract_Capacity_MW` is within 15 % of the summed
   `generationCapacity` of every wind unit in the day's population whose
   name passes test 1 against the same row (a contract spanning several BM
   units is compared with the sum of the units it names);
3. the row's `Status` is not a terminal status (any value whose lower-case
   form contains *terminated*, *withdrawn* or *cancelled* fails the test),
   and its `Expected_Start_Date`, where parseable, is on or before
   2026-09-08.

A unit passing tests 1 and 2 but not 3 is **grade C (CfD)**, reported in
the sensitivity table, never in the headline. A unit with several grade-B
CfD rows is linked to all of them and counted once. Grade A is unchanged
and takes precedence; a unit with a grade-B CfD link and a grade-B RO link
is *both*, as in version 1.

## What the run reports

The Part 1 table of version 1 with CfD split into grade A and grade B
rows, the unmatched remainder recomputed, and S1 re-decided under the
same wording. Version 1's table stands beside it; version 2 restates the
link, not the money.

## Falsifier added

- **F4** Two portfolio rows pass test 1 for one unit with capacities that
  differ by more than 15 % from each other: the link is *ambiguous*,
  reported as such, and the unit stays unmatched in the headline table.
