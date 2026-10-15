"""Catalyst Commercial, "UK Energy Market Report" (daily HTML page): a
broker-report aggregator's print of the previous day's settlements. The
edition of 15 October 2026 (settlement Wednesday 14 October 2026) carries
three tables: NBP gas by contract in pence per therm, UK baseload power in
GBP/MWh, and commodities including the UK ETS December allowance. It is not
the exchange's settlement file (ICE Endex NBP settlements are paid); it is
the only free dated print of the curve found. Read as 024's schema pass
found it (`archives/024-catalyst-report-2026-10-15/`).
"""

import html as html_lib
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

NBP_HEADER = ("Contract", "Settlement (p/therm)", "Change on the day")
COMMODITY_HEADER_PREFIX = ("Commodity", "Settlement")
UK_ETS_ROW = "UK ETS Dec-26"
DECIMAL = re.compile(r"^-?\d+(\.\d+)?$")
POUNDS_PER_TONNE = re.compile(r"^£\s?(\d+(\.\d+)?)/tonne$")


@dataclass(frozen=True)
class Table:
    header: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


def tables(text: str) -> list[Table]:
    out = []
    for tb in re.findall(r"<table.*?</table>", text, re.S):
        rows = [
            tuple(
                html_lib.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)
            )
            for row in re.findall(r"<tr.*?</tr>", tb, re.S)
        ]
        if rows:
            out.append(Table(rows[0], tuple(rows[1:])))
    return out


def settlement_line(text: str) -> str | None:
    m = re.search(r"Settlement \w+day \d{1,2} \w+ \d{4}, against \w+day \d{1,2} \w+ \d{4}", text)
    return m.group(0) if m else None


def format_profile(path: Path) -> dict:
    """Tables' headers, row labels and cell forms, with no value read."""
    text = path.read_text(encoding="utf-8")
    out = []
    for t in tables(text):
        out.append(
            {
                "header": list(t.header),
                "rows": len(t.rows),
                "row_labels": [r[0] for r in t.rows],
                "cells_per_row": sorted({len(r) for r in t.rows}),
                "settlement_forms": {
                    "decimal": sum(1 for r in t.rows if len(r) > 1 and DECIMAL.match(r[1])),
                    "pounds": sum(1 for r in t.rows if len(r) > 1 and POUNDS_PER_TONNE.match(r[1])),
                    "other": sum(
                        1
                        for r in t.rows
                        if len(r) < 2 or not (DECIMAL.match(r[1]) or POUNDS_PER_TONNE.match(r[1]))
                    ),
                },
            }
        )
    return {"tables": out, "settlement_line": settlement_line(text)}


def read_nbp(path: Path) -> dict[str, Decimal]:
    """Contract -> settlement in pence per therm, from the NBP table."""
    text = path.read_text(encoding="utf-8")
    t = next((t for t in tables(text) if t.header == NBP_HEADER), None)
    if t is None:
        raise ValueError("no NBP table with the declared header")
    out: dict[str, Decimal] = {}
    for r in t.rows:
        if len(r) != 3 or not DECIMAL.match(r[1]):
            raise ValueError(f"NBP row departs from the declared forms: {r!r}")
        if r[0] in out:
            raise ValueError(f"contract {r[0]} printed twice")
        out[r[0]] = Decimal(r[1])
    return out


def read_uk_ets(path: Path) -> Decimal:
    """The UK ETS Dec-26 settlement in GBP per tonne, from the commodities table."""
    text = path.read_text(encoding="utf-8")
    for t in tables(text):
        if t.header[:1] == COMMODITY_HEADER_PREFIX[:1]:
            for r in t.rows:
                if r[0] == UK_ETS_ROW:
                    m = POUNDS_PER_TONNE.match(r[1]) if len(r) > 1 else None
                    d = DECIMAL.match(r[1]) if len(r) > 1 else None
                    if m:
                        return Decimal(m.group(1))
                    if d:
                        return Decimal(r[1])
                    raise ValueError(f"UK ETS row departs from the declared forms: {r!r}")
    raise ValueError(f"no {UK_ETS_ROW!r} row")
