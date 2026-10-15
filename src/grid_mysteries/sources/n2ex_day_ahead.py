"""NESO Data Portal, "Day-Ahead Power Exchange prices (Nord Pool)", resource
`4f27eea5-7038-4f73-9740-e3e4ad47c26a` ("N2EX GB Day-Ahead Price"): one CSV
dump with the columns `Date`, `Delivery Period` (an hour label `HH:00 -
HH:00`) and `Price` (GBP/MWh, printed to six decimals). Read as 024's
schema pass found it (`archives/024-n2ex-day-ahead/`): 24 rows on every
printed date but the first and last, 24 distinct labels, no blanks.

The format profile reads the shape of every field and no value; the reader
returns prices as `Decimal` from the printed text.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

COLUMNS = ("Date", "Delivery Period", "Price")
LABEL = re.compile(r"^([01]\d|2[0-3]):00 - ([01]\d|2[0-3]):00$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DECIMAL = re.compile(r"^-?\d+\.\d{6}$")


@dataclass(frozen=True)
class HourPrice:
    day: date
    label: str
    price: Decimal

    @property
    def start_hour(self) -> int:
        return int(self.label[:2])


def _lines(path: Path) -> tuple[bool, list[str]]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw[3:].decode("utf-8") if bom else raw.decode("utf-8")
    return bom, text.split("\n")


def format_profile(path: Path) -> dict:
    """Encoding, header, field counts and field forms, with no value read."""
    bom, lines = _lines(path)
    if lines and lines[-1] == "":
        lines = lines[:-1]
    header = lines[0].split(",") if lines else []
    field_counts: dict[int, int] = {}
    forms = {
        "date": {"iso": 0, "other": 0},
        "label": {"hour-range": 0, "other": 0},
        "price": {"decimal-6": 0, "other": 0},
    }
    for line in lines[1:]:
        fields = line.split(",")
        field_counts[len(fields)] = field_counts.get(len(fields), 0) + 1
        if len(fields) == 3:
            forms["date"]["iso" if ISO_DATE.match(fields[0]) else "other"] += 1
            forms["label"]["hour-range" if LABEL.match(fields[1]) else "other"] += 1
            forms["price"]["decimal-6" if DECIMAL.match(fields[2]) else "other"] += 1
    return {
        "leading_byte_order_mark": bom,
        "carriage_returns": any(line.endswith("\r") for line in lines),
        "header": header,
        "rows": len(lines) - 1,
        "field_counts": {str(k): v for k, v in sorted(field_counts.items())},
        "forms": forms,
    }


def read(path: Path) -> Iterator[HourPrice]:
    """Every row as an `HourPrice`; a row that departs from the declared
    forms stops the read (the format check is meant to have refused first)."""
    _, lines = _lines(path)
    if lines[0].split(",") != list(COLUMNS):
        raise ValueError(f"unexpected header {lines[0]!r}")
    for n, line in enumerate(lines[1:], start=2):
        if not line:
            continue
        fields = line.rstrip("\r").split(",")
        if len(fields) != 3 or not (
            ISO_DATE.match(fields[0]) and LABEL.match(fields[1]) and DECIMAL.match(fields[2])
        ):
            raise ValueError(f"line {n} departs from the declared forms: {line!r}")
        yield HourPrice(date.fromisoformat(fields[0]), fields[1], Decimal(fields[2]))
