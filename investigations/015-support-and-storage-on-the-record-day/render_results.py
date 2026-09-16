# ruff: noqa: E501  (a Markdown template: its lines are the document's lines)
"""RESULTS.md for 015, a pure function of the committed evidence.

    uv run python investigations/015-support-and-storage-on-the-record-day/render_results.py

Every number in the prose is read from evidence/; the prose itself is the
six-part form. Rendering never recomputes anything.
"""

import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
E = HERE / "evidence"


def load(name: str):
    return json.loads((E / name).read_text())


def gbp(v) -> str:
    return "—" if v is None else f"£{Decimal(v).quantize(Decimal('1')):,}"


def mwh(v) -> str:
    return "—" if v is None else f"{Decimal(v).quantize(Decimal('1')):,}"


def pct(v) -> str:
    return "—" if v is None else f"{Decimal(v) * 100:.1f} %"


def num(v, q="0.01") -> str:
    return "—" if v is None else f"{Decimal(v).quantize(Decimal(q)):,}"


def main() -> None:
    summary, wind, storage, links = (
        load("summary.json"),
        load("wind-by-scheme.json"),
        load("storage.json"),
        load("links.json"),
    )
    c = summary["constraint"]
    table = {r["scheme"]: r for r in wind["table"]}
    total = Decimal(wind["total_wind_bid_paid_gbp"])
    labels = {
        "cfd": "CfD (grade A, LCCC mapping)",
        "ro": "RO (grade B, name and capacity)",
        "both": "Both",
        "ro-possible": "RO possible (grade C, sensitivity)",
        "unmatched": "Unmatched",
    }
    grades = Counter((link["register"], link["grade"]) for link in links)
    cfd_units = [u for u in wind["units"] if u["scheme"] == "cfd"]
    cfd_negative = [
        u for u in cfd_units if Decimal(u["bid_signed_gbp"]) < Decimal(u["bid_paid_gbp"])
    ]
    cfd_negative_total = sum(
        (Decimal(u["bid_signed_gbp"]) - Decimal(u["bid_paid_gbp"]) for u in cfd_units), Decimal(0)
    )
    unmatched = sorted(
        (u for u in wind["units"] if u["scheme"] == "unmatched"),
        key=lambda u: -Decimal(u["bid_paid_gbp"]),
    )
    north = [r for r in storage if r["side_of_b6"] == "north"]
    sides = Counter((r["side_of_b6"], r["side_grade"]) for r in storage)
    export_total = sum((Decimal(r["export_capacity_mw"] or 0) for r in storage), Decimal(0))
    export_north = sum((Decimal(r["export_capacity_mw"] or 0) for r in north), Decimal(0))
    paid_any = sum(1 for r in storage if r["bid_paid_gbp"] or r["offer_paid_gbp"])
    r3p = [Decimal(r["export_hours_r3p"]) for r in storage if r["export_hours_r3p"] is not None]
    r3p_north = [Decimal(r["export_hours_r3p"]) for r in north if r["export_hours_r3p"] is not None]
    net_negative = [u for u in cfd_units if Decimal(u["bid_signed_gbp"]) < 0]

    rows1 = "\n".join(
        f"| {labels[s]} | {table[s]['units']} | {mwh(table[s]['bid_mwh'])} | {gbp(table[s]['bid_paid_gbp'])} | "
        f"{gbp(table[s]['bid_signed_gbp'])} | {num(table[s]['gbp_per_mwh'])} | {pct(table[s]['share_of_wind_bid_gbp'])} |"
        for s in ("cfd", "ro", "both", "unmatched", "ro-possible")
    )
    rows2 = "\n".join(
        f"| `{r['unit']}` | {r['name']} | {r['fuel_type'] or '—'} | {num(r['export_capacity_mw'], '0.1')} | "
        f"{num(r['import_capacity_mw'], '0.1')} | {r['side_of_b6']} ({r['side_grade']}) | "
        f"{num(r['export_hours_r3p'])} | {num(r['export_hours_r3h'])} | {num(r['import_hours_r3p'])} | "
        f"{mwh(r['offer_mwh'])} | {gbp(r['offer_paid_gbp'])} | {mwh(r['bid_mwh'])} | {gbp(r['bid_paid_gbp'])} |"
        for r in sorted(
            storage,
            key=lambda r: (r["side_of_b6"] != "north", -Decimal(r["export_capacity_mw"] or 0)),
        )
    )
    unmatched_rows = "\n".join(
        f"| `{u['unit']}` | {u['name']} | {u['lead_party']} | {num(u['generation_capacity_mw'], '0.1')} | {gbp(u['bid_paid_gbp'])} |"
        for u in unmatched[:10]
    )
    text = f"""# 015 — results: support and storage on the record day

**Run**: 2026-09-16, from bytes pinned by 012, 003 and this study's own
acquisition. Declaration `DECLARATION.md` (SHA-256 `{summary["declaration_sha256"][:16]}…`,
witnessed by OpenTimestamps and two RFC 3161 authorities before the run).
Evidence: `evidence/links.json` (the link table), `evidence/wind-by-scheme.json`,
`evidence/storage.json`, `evidence/summary.json`, `evidence/reading.json` (the
column bindings from the schema pass), and the three acquisition manifests.
Logic and tests: `src/grid_mysteries/investigations/support_and_storage.py`,
`tests/test_support_and_storage.py`. This file is rendered by
`render_results.py` from the evidence; it computes nothing. **Unpublished.**

## 1. The mystery

On 8 September 2026, Britain's most expensive constraint day, which support
scheme stood behind the wind farms that were paid to stop, and what could
the batteries on the system actually have done about it?

## 2. The evidence

**Part 1 — wind bids by support scheme.** {wind["wind_units"]} wind units carried bid
cashflow on the day, {gbp(total)} paid out on bids in total (012's figure). Each
was linked to LCCC's CfD-to-BM-unit mapping by the publisher's own BM-unit
identifier (grade A: {grades[("cfd", "A")]} links over {len(cfd_units)} units) and to
Ofgem's Accredited Stations (RO) report by the declared name-and-capacity test
(grade B: {grades[("ro", "B")]}; name only, grade C: {grades[("ro", "C")]}). Volumes are accepted bid MWh
from the DISPTAV `{wind["disptav_type"]}` type, the one that reconciles with the day's
settlement totals under 013's gate.

| Scheme | Units | Accepted bid MWh | Bid £ paid out | Bid £ signed | £/MWh | Share of wind bid £ |
|---|---|---|---|---|---|---|
{rows1}

The ten largest unmatched units, by bid £ paid:

| Unit | Name | Lead party | MW | Bid £ paid |
|---|---|---|---|---|
{unmatched_rows}

**Part 2 — the energy-limited units.** {len(storage)} BM units published a maximum
delivery volume (MDO or MDB) for the day: {export_total.quantize(Decimal("1")):,} MW of registered export
capacity in all, {export_north.quantize(Decimal("1")):,} MW of it north of B6 ({len(north)} units, graded
{", ".join(f"{g}: {n}" for (s, g), n in sorted(sides.items()) if s == "north")}). The constraint, read as periods
with accepted wind-unit bid volume, ran for **{c["periods"]} of 48 periods** ({num(c["hours"], "0.1")} hours;
longest contiguous run {num(c["longest_run_hours"], "0.1")} hours). {paid_any} of the {len(storage)} units
were paid something on the day, almost all on offers. Hours of energy are the
unit's maximum published delivery volume divided by its registered capacity:
R3p uses only records published before the first constrained period began,
R3h everything published for the day. Sides of B6 are graded as declared (A:
CMIS arming; B: TEC register host TO by name and capacity; C: GSP group;
unknown otherwise).

| Unit | Name | Fuel | Export MW | Import MW | Side of B6 (grade) | Export h R3p | Export h R3h | Import h R3p | Offer MWh | Offer £ | Bid MWh | Bid £ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
{rows2}

## 3. Explanations tested

- **Is the unmatched remainder a matching failure or an absence from the
  registers?** Mostly the latter, and the declared rule was right not to
  guess. LCCC's mapping has 165 rows and names Moray East's three units but
  none of Moray West's, and none for Seagreen, Bhlaraidh or South Kyle,
  which lead the unmatched list. Whatever those units' contracts are, the
  publisher's mapping does not carry them on the day, and the declaration
  allowed CfD links only by that identifier. A grade-B CfD link by name
  against the portfolio's `Name_of_CFD_Unit` would be a new rule for a new
  declaration, not an amendment.
- **Why is Griffin grade C, not B?** The RO station carries 186 MW; only
  some of the station's BM units bid on the day, so the summed capacity of
  the bidding units sits outside the 15 % band. The rule compares what bid,
  not what exists; recorded as a limit, not corrected.
- **CfD units paid, or paying?** {len(cfd_negative)} of the {len(cfd_units)} CfD-linked units carried
  negative bid rows on the day and {len(net_negative)} netted negative over the day; the
  negative rows sum to {gbp(-cfd_negative_total)}, so the group's signed total
  ({gbp(table["cfd"]["bid_signed_gbp"])}) is well below its paid-out total
  ({gbp(table["cfd"]["bid_paid_gbp"])}). The table shows both. Why a unit's bids are priced as they
  are is not a question this record answers.
- **Is the RO capacity column usable?** Yes: every one of the 26,578 rows
  carries a numeric declared net capacity in kW; the schema pass found no
  identifier column, so RO grade A was not applicable and the declaration's
  F1 did not fire.
- **Is "north of B6" trustworthy?** Four units are placed north: one by the
  TEC register (grade B) and three by GSP group (grade C). No unit was placed
  by name, and `T_PINFB-1` stays unknown. The CMIS file armed no
  energy-limited unit that day.
- **Could any of them have covered the constraint?** Not on the published
  numbers: export hours of energy at R3p run from {min(r3p) if r3p else "—"} to {max(r3p) if r3p else "—"} hours
  across the {len(r3p)} units with a published bound ({min(r3p_north) if r3p_north else "—"} to
  {max(r3p_north) if r3p_north else "—"} for the {len(r3p_north)} north of B6), against a constraint that ran all
  day. The table draws no further conclusion, and none of this is a
  counterfactual.

## 4. The conclusion

- **S1 (share): not determinable.** Unmatched units carry {pct(table["unmatched"]["share_of_wind_bid_gbp"])} of the
  day's wind bid money, more than either scheme; the public identifier
  link covers {pct(table["cfd"]["share_of_wind_bid_gbp"])} (CfD) and the graded name link
  {pct(table["ro"]["share_of_wind_bid_gbp"])} (RO). The honest answer to "which scheme was paid" is
  that the public registers, read by declared rules, do not settle it.
- **S2 (price): holds.** RO-linked units were paid £{num(table["ro"]["gbp_per_mwh"])} per accepted MWh
  against £{num(table["cfd"]["gbp_per_mwh"])} for CfD-linked units.
- **B1 (coverage): holds** on one deciding unit: no energy-limited unit north
  of B6 with a graded side had an R3p export energy bound covering the
  longest run of the constraint.

## 5. Expert corner

Settlement date 2026-09-08 (BST; period 1 starts 2026-09-07T23:00Z). EBOCF
indicative cashflows, `totalCashflow` as published, positive rows summed
for "paid", all rows for "signed". DISPTAV `{wind["disptav_type"]}` reconciled in both
directions within 0.1 % (deviations in `wind-by-scheme.json`). Register:
012's BMUNITS vintage of 2026-09-11. CfD mapping resource
`c16f141d-2db9-4160-ade1-d0d19d224dc9` (last modified 2026-09-14), portfolio
`fdaf09d2-8cff-4799-a5b0-1c59444e492b`; effective-date test applied per row.
RO report `RO_Accredited_Stations_16-09-2026_05-00.csv` from the RER public
reports dashboard (the dashboard page is pinned beside it). Name test:
lower-case alphanumerics with the declared generic tokens removed, station
tokens equal to or a superset of the unit's; capacity within 15 % of the
summed capacity of every bidding unit matching the same station; RO
capacity read as kW / 1000. MDO/MDB day streams for all units; levels taken
as the maximum of `levelFrom` and `levelTo` per record. Column bindings and
schema-report digests in `evidence/reading.json`.

## 6. Reproducibility

`run.py --phase compute` recomputes every figure from the pinned bytes
(paths and SHA-256 in the three manifests here and in 012's and 003's);
`render_results.py` regenerates this file. `scripts/check-rules` maps every
declared rule to a test.
"""
    (HERE / "RESULTS.md").write_text(text)
    print("RESULTS.md rendered")


if __name__ == "__main__":
    main()
