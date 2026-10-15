"""Ofgem, wholesale market indicators, "Gas prices: day-ahead contracts –
monthly average (Great Britain)" (data portal chart node 175055): the chart
is served by everviz as an inject script whose options carry the data as a
CSV string, `"Category","Price"`, one row per month dated as the month's
first day in month/day/year form, the price in pence per therm. Ofgem's
description: to 28 February 2021 a price reporting agency's assessment of
over-the-counter broker trades; from 1 March 2021 Ofgem analysis of broker
data, a monthly average weighted by volume. Read as 024's schema pass found
it (`archives/024-ofgem-gas-day-ahead-monthly/`).
"""

import json
import re
from decimal import Decimal
from pathlib import Path

#: Kilowatt-hours per therm, the statutory conversion (Units of Measurement
#: Regulations); pence per therm times ten over this is pounds per MWh.
KWH_PER_THERM = Decimal("29.3071")
HEADER = ("Category", "Price")
US_DATE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
DECIMAL = re.compile(r"^-?\d+(\.\d+)?$")


def extract_csv(text: str) -> str:
    """The CSV string inside the inject script's `"data":{"csv":"..."}`."""
    m = re.search(r'"data":\{"csv":("(?:[^"\\]|\\.)*")', text)
    if not m:
        raise ValueError("no data.csv string in the inject script")
    return json.loads(m.group(1))


def rows(text: str) -> list[tuple[str, str]]:
    out = []
    for line in extract_csv(text).splitlines():
        if not line.strip():
            continue
        cells = [c.strip().strip('"') for c in line.split(",")]
        if len(cells) != 2:
            raise ValueError(f"not two cells: {line!r}")
        out.append((cells[0], cells[1]))
    return out


def chart_facts(text: str) -> dict:
    """Title, credits and axis unit as the options print them."""
    facts = {}
    nested = r"(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*?"
    for key, pattern in (
        ("title", r'"title":\{' + nested + r'"text":"((?:[^"\\]|\\.)*)"'),
        ("credits", r'"credits":\{' + nested + r'"text":"((?:[^"\\]|\\.)*)"'),
        ("y_axis_title", r'"yAxis":\{' + nested + r'"title":\{"text":"((?:[^"\\]|\\.)*)"'),
    ):
        m = re.search(pattern, text, re.S)
        facts[key] = json.loads(f'"{m.group(1)}"') if m else None
    return facts


def format_profile(path: Path) -> dict:
    """Header, row count and cell forms, with no value read."""
    text = path.read_text(encoding="utf-8")
    all_rows = rows(text)
    header, body = all_rows[0], all_rows[1:]
    forms = {"date": {"us-date-first-of-month": 0, "other": 0}, "price": {"decimal": 0, "other": 0}}
    for d, p in body:
        m = US_DATE.match(d)
        forms["date"]["us-date-first-of-month" if m and m.group(2) == "01" else "other"] += 1
        forms["price"]["decimal" if DECIMAL.match(p) else "other"] += 1
    return {"header": list(header), "rows": len(body), "forms": forms, **chart_facts(text)}


def read(path: Path) -> dict[tuple[int, int], Decimal]:
    """(year, month) -> the month's average day-ahead price in pence per therm."""
    all_rows = rows(path.read_text(encoding="utf-8"))
    if all_rows[0] != HEADER:
        raise ValueError(f"unexpected header {all_rows[0]!r}")
    out: dict[tuple[int, int], Decimal] = {}
    for d, p in all_rows[1:]:
        m = US_DATE.match(d)
        if not m or m.group(2) != "01" or not DECIMAL.match(p):
            raise ValueError(f"row departs from the declared forms: {(d, p)!r}")
        key = (int(m.group(3)), int(m.group(1)))
        if key in out:
            raise ValueError(f"month {key} printed twice")
        out[key] = Decimal(p)
    return out


def to_gbp_per_mwh(pence_per_therm: Decimal) -> Decimal:
    return pence_per_therm * 10 / KWH_PER_THERM
