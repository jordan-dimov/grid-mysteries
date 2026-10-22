# 013 — the cover price tracker: Amendment 2

**Frozen on its own**, by `scripts/freeze` (OpenTimestamps and RFC 3161 tokens from freetsa.org and DigiCert, committed with the file), so that `AMENDMENTS.md` can keep growing. `DECLARATION.md` (SHA-256 `d20d59203e7b7fda174c2c6deb2807159687bd9ddea39fe760961af884416473`, sealed 2026-09-11), `DECLARATION-T4.md` (frozen 2026-09-19) and `AMENDMENT-1.md` (SHA-256 `326cc5fee3cbeead72335519fafffca71f561404eafd8eebcc2837d32322e11c`, frozen 2026-09-25) stand unchanged.

## Amendment 2 — L4 is read under either spelling of NESO's volume-file header, admitted by vintage date; any third spelling is a named refusal

**Dated 2026-10-22, evening (UTC).** Written after batches 3 to 5 were
fetched (03/10, 10/10 and 17/10/2026 by `tracker-013`) and before any of
them was computed. Taught by the record-engine kill test of 21/10/2026
(`bill/KILL-TEST-2.md`, "What the test found about 013 itself"), not by any
tracker day's figure: the amendment reads a header, never a value, so the
window it runs against cannot have taught it. Raised on the sponsor's
instruction of 22/10/2026 (item 5 of the 025 close-out).

**What the declaration says.** L4 is "NESO published constraint bid and
offer MWh (Daily Balancing Volume 2026-2027); blank until the file reaches
the day", appended as outcome with the vintage date under column 8's
append-only rule (first vintage kept, later differing vintages listed as
revisions). The runner reads the two columns by their names as the file
printed them when the declaration was written: `Constraint Offers (MWh)`
and `Constraint Bids (MWh)`.

**What changed in the world.** NESO renamed the columns of its daily
balancing volume file. The 31 pinned vintages from 2026-09-15 to
2026-10-15 carry the header

    SETT_DATE,SETT_PERIOD,Energy Imbalance (MWh),Frequency Control Offers (MWh),Frequency Control Bids (MWh),Positive Reserve (MWh),Constraint Offers (MWh),Constraint Bids (MWh),Negative Reserve (MWh),Other (MWh)

and every vintage from 2026-10-16 (seven to 2026-10-22) carries

    SETT_DATE,SETT_PERIOD,Energy Imbalance MWh,Frequency Control Offers MWh,Frequency Control Bids MWh,Positive Reserve MWh,Constraint Offers MWh,Constraint Bids MWh,Negative Reserve MWh,Other MWh

The parentheses are gone; the column order, count and meaning are the same.
The runner reads L1 and L4 from every pinned vintage in date order, so on
the laptop `--phase compute` fails with `KeyError: 'Constraint Offers
(MWh)'` before writing anything. That is the doctrine's format check firing
as a crash instead of a named refusal: no frozen rule reads the new
spelling.

**Amendment.**

1. **Two spellings are admitted, by vintage date.** For a vintage dated
   before 2026-10-16, L4's two columns are read as `Constraint Offers (MWh)`
   and `Constraint Bids (MWh)` and nothing else, as before. For a vintage
   dated 2026-10-16 or later, each column is read under whichever of its two
   spellings the file carries: `Constraint Offers (MWh)` or `Constraint
   Offers MWh`, and `Constraint Bids (MWh)` or `Constraint Bids MWh`. The
   value is read from exactly one column; the spelling is not recorded as a
   figure.
2. **A third spelling is a named refusal.** A vintage in which a column is
   present under neither admitted spelling, or under both at once, is
   refused by name (the vintage date, the column, the header found) before
   any value is read, and the compute stops. A later rename needs its own
   dated amendment; nothing here reads it.
3. **Nothing earlier is re-read.** The vintages before 2026-10-16 carry only
   the old spelling, which the rule reads as it always has; every committed
   row's figures and kept outcome vintage are therefore unchanged by this
   amendment, and the runner's first compute under it must show so (the 22
   days the Balancing Bill record holds under rule version
   `013-d20d5920-A1`, byte for byte, as the kill test's arm A already showed
   for the vintages to 15/10). A later vintage that differs from a day's kept
   outcome is listed as a dated revision under the existing rule, and may now
   include vintages from 16/10.
4. **Rule version.** Every tracked day computed under this amendment
   carries rule version `013-d20d5920-A2` (the declaration with Amendments
   1 and 2 in force). The Balancing Bill record holds each computed row once
   per rule version and a day recomputed under a new rule version is a
   second set beside the first (`bill/README.md`), so the 22 days it holds
   under `013-d20d5920-A1` are recorded again under A2 as that second set,
   and the record itself then shows whether the amendment moved a figure:
   the two sets must agree figure for figure, which the first compute under
   this amendment verifies before import and states in its commit. Nothing
   under A1 is altered or retracted.

**What this does not do.** It moves no threshold, decides no proposition,
and reads no value differently. The L1 file (`daily_balancing_costs_2026-27.csv`)
and the L3 file (`disaggregated_bsad_2026-27.csv`) kept their headers
through the same vintages and are not touched.

**Runs against.** Batches 3 to 5 (settlement days 2026-09-30 to
2026-10-20, fetched 03/10, 10/10 and 17/10/2026), computed for the first
time under this amendment, and every later batch. On batches 1 and 2 no
figure moves.

**Tests.** `A2.1` either admitted spelling resolves to one column from the
vintage of 2026-10-16; `A2.2` before 2026-10-16 only the old spelling is
admitted; `A2.3` a header under neither or both spellings is refused by
name; `A2.4` a recompute under a new rule version is a second row beside
the first, never a replacement. Mapped in `evidence/rule-sources.json`.
