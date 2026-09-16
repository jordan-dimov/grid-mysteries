# ruff: noqa: E501  (a Markdown template: its lines are the document's lines)
"""The follow-up post for the record-day thread, rendered from 015's evidence.

    uv run python investigations/015-support-and-storage-on-the-record-day/render_post.py

Writes drafts/post-2026-09-16.md. A draft held for the sponsor; never posted
by any script. Every number comes from evidence/; nothing is computed here.
"""

import json
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
E = HERE / "evidence"


def load(name: str):
    return json.loads((E / name).read_text())


def gbp(v) -> str:
    return "—" if v is None else f"£{Decimal(v).quantize(Decimal('1')):,}"


def num(v, q="0.01") -> str:
    return "—" if v is None else f"{Decimal(v).quantize(Decimal(q)):,}"


def pct(v) -> str:
    return "—" if v is None else f"{Decimal(v) * 100:.0f}%"


def main() -> None:
    summary, wind, storage = load("summary.json"), load("wind-by-scheme.json"), load("storage.json")
    table = {r["scheme"]: r for r in wind["table"]}
    c = summary["constraint"]
    cfd_units = [u for u in wind["units"] if u["scheme"] == "cfd"]
    negative_rows = sum(
        1 for u in cfd_units if Decimal(u["bid_signed_gbp"]) < Decimal(u["bid_paid_gbp"])
    )
    net_negative = sum(1 for u in cfd_units if Decimal(u["bid_signed_gbp"]) < 0)
    north = [r for r in storage if r["side_of_b6"] == "north"]
    export_total = sum((Decimal(r["export_capacity_mw"] or 0) for r in storage), Decimal(0))
    export_north = sum((Decimal(r["export_capacity_mw"] or 0) for r in north), Decimal(0))
    r3p = [Decimal(r["export_hours_r3p"]) for r in storage if r["export_hours_r3p"] is not None]
    r3p_north = [Decimal(r["export_hours_r3p"]) for r in north if r["export_hours_r3p"] is not None]
    labels = {
        "cfd": "CfD (LCCC's own BM-unit mapping)",
        "ro": "RO (station name and capacity match)",
        "ro-possible": "Possibly RO (name only, shown for scale)",
        "unmatched": "Not placeable from the public registers",
    }
    rows1 = "\n".join(
        f"| {labels[s]} | {table[s]['units']} | {num(table[s]['bid_mwh'], '1')} | {gbp(table[s]['bid_paid_gbp'])} | {num(table[s]['gbp_per_mwh'])} | {pct(table[s]['share_of_wind_bid_gbp'])} |"
        for s in ("cfd", "ro", "ro-possible", "unmatched")
    )
    rows2 = "\n".join(
        f"| `{r['unit']}` | {r['name']} | {num(r['export_capacity_mw'], '1')} | {r['side_of_b6']} ({r['side_grade']}) | {num(r['export_hours_r3p'])} | {gbp(r['offer_paid_gbp'])} | {gbp(r['bid_paid_gbp'])} |"
        for r in sorted(
            storage,
            key=lambda r: (r["side_of_b6"] != "north", -Decimal(r["export_capacity_mw"] or 0)),
        )
    )
    text = f"""<!-- DRAFT, held for the sponsor's second seal. Not posted. Rendered from
investigations/015-support-and-storage-on-the-record-day/evidence by render_post.py. -->

# You asked, here is the answer: 8 September's wind bids by support scheme, and what the batteries could have done

Two questions from the thread on the record day deserved a number rather
than an opinion. Bogi asked which support scheme stood behind the wind
farms paid to stop. Nick asked what the batteries on the system could
actually have done. The method for both was written down and witnessed by
two timestamp authorities before any join was made, every link between a
BM unit and a register carries a confidence grade, and the evidence is
published with the digests. Two tables, no counterfactuals.

## 1. Who was behind the wind bids (Bogi)

{gbp(wind["total_wind_bid_paid_gbp"])} was paid to {wind["wind_units"]} wind units on bids on 8 September. Linked to
LCCC's CfD register by LCCC's own BM-unit mapping, and to Ofgem's RO register
by a declared name-and-capacity test:

| Support scheme | Units | Accepted bid MWh | Paid on bids | £/MWh | Share |
|---|---|---|---|---|---|
{rows1}

The honest headline is the last row. {pct(table["unmatched"]["share_of_wind_bid_gbp"])} of the money went to units the
public identifiers cannot place: LCCC's mapping does not carry the BM units
of Moray West, Seagreen, Bhlaraidh or South Kyle, which lead that group. A
second declaration that links CfD contracts by name is written and
witnessed; it has not been run, and it will be run only as a separate,
declared step. What the identifiers do settle: RO-linked units were paid
about £{num(table["ro"]["gbp_per_mwh"])} per accepted MWh against about £{num(table["cfd"]["gbp_per_mwh"])} for CfD-linked units, and
{negative_rows} of the {len(cfd_units)} CfD-linked units carried negative bid rows on the day,
{net_negative} of them netting negative across it.

## 2. What the batteries could do (Nick)

{len(storage)} BM units published an energy limit (a maximum delivery volume) for the
day, {export_total.quantize(Decimal("1")):,} MW of registered export capacity in all, {export_north.quantize(Decimal("1")):,} MW of it north of the
B6 boundary. The constraint ran for all {c["periods"]} settlement periods. "Hours of
energy" is the unit's own published limit divided by its registered
capacity, using only what was published before the constraint began.

| Unit | Name | Export MW | Side of B6 (grade) | Hours of energy | Paid on offers | Paid on bids |
|---|---|---|---|---|---|---|
{rows2}

Hours of energy ran from {min(r3p)} to {max(r3p)} across the set and {min(r3p_north)} to {max(r3p_north)}
for the units north of B6, against a constraint that ran all day. Sides
are graded: A from NESO's intertrip arming file, B from the TEC register's
host transmission owner, C from the GSP group; nothing is placed by name.
The table says what each unit was and what it was paid; it does not say
what any of them should have done.

Declaration `DECLARATION.md` (SHA-256 `{summary["declaration_sha256"][:16]}…`), evidence
and code: github.com/jordan-dimov/grid-mysteries, investigation 015.
"""
    (HERE / "drafts" / "post-2026-09-16.md").write_text(text)
    print("draft rendered")


if __name__ == "__main__":
    main()
