"""A TEC register row as the record holds it: cells as published.

Pure; no I/O. The declared reader (`sources.tec_register.read_vintage`)
maps each copy's headers to the canonical columns and hands back text,
integers, floats, spreadsheet date cells or blanks. The record stores
every cell as text and a `kinds` string with one character per column
saying what the cell was:

    t  text, verbatim (whitespace included)
    i  an integer cell, as its digits (`340`)
    f  a float cell, written canonically: an integral value as its digits
       (`340`), any other as Python prints it (`340.5`)
    d  a spreadsheet date cell, as an ISO date
    -  blank, or a column the copy does not carry

`decode` inverts `encode` exactly, so any analysis reading the record
sees the values the reader saw. The spreadsheet's display format is not
recorded; a date cell is a date, whatever it looked like on screen.

A row's key is a digest of its cells (not its kinds), plus its occurrence
among identical rows of the same publication. So the same line printed in
a CSV copy (`"340"`), an xlsx copy (integer 340) and an xls copy (float
340.0) is one row whose kinds differ, which the record states as a change
of kinds, not of content. The key says nothing about which
row of one publication is which row of another; that is identity, and it
is the analysis's job, never the record's.
"""

import hashlib
import json
from collections import Counter
from datetime import date
from typing import Final

from grid_mysteries.sources.tec_register import CANONICAL_COLUMNS

COLUMNS: Final = CANONICAL_COLUMNS
#: The record's argument name for each canonical column, in the same order.
FIELDS: Final = (
    "project_id",
    "project_number",
    "project_name",
    "customer_name",
    "connection_site",
    "stage",
    "mw_connected",
    "mw_change",
    "cumulative_mw",
    "mw_effective_from",
    "project_status",
    "agreement_type",
    "host_to",
    "plant_type",
    "gate",
)
assert len(FIELDS) == len(COLUMNS) == 15

Cells = tuple[str, ...]


class CellError(ValueError):
    pass


def encode_cell(value: object) -> tuple[str, str]:
    """(kind, text) for one cell as the reader returned it."""
    if value is None:
        return "-", ""
    if isinstance(value, bool):
        raise CellError(f"boolean cell {value!r}: the reader never returns one")
    if isinstance(value, str):
        return "t", value
    if isinstance(value, int):
        return "i", str(value)
    if isinstance(value, float):
        return "f", str(int(value)) if value.is_integer() else repr(value)
    if isinstance(value, date):
        return "d", value.isoformat()
    raise CellError(f"cell of type {type(value).__name__}: {value!r}")


def decode_cell(kind: str, text: str) -> object:
    if kind == "-":
        return None
    if kind == "t":
        return text
    if kind == "i":
        return int(text)
    if kind == "f":
        return float(text)
    if kind == "d":
        return date.fromisoformat(text)
    raise CellError(f"unknown cell kind {kind!r}")


def encode(row: dict[str, object]) -> tuple[str, Cells]:
    """The record's (kinds, cells) for one reader row."""
    pairs = [encode_cell(row.get(column)) for column in COLUMNS]
    return "".join(kind for kind, _ in pairs), tuple(text for _, text in pairs)


def decode(kinds: str, cells: Cells) -> dict[str, object]:
    """The reader row back from the record. A blank cell and an absent
    column both read as None, which is how every rule reads them."""
    return {
        column: decode_cell(kind, text)
        for column, kind, text in zip(COLUMNS, kinds, cells, strict=True)
        if kind != "-"
    }


def digest(cells: Cells) -> str:
    payload = json.dumps(list(cells), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def keyed(rows: list[dict[str, object]]) -> dict[str, tuple[str, Cells]]:
    """Every row of one publication under its record key, in file order:
    `<digest>#<n>`, where n counts identical rows (1 for the first)."""
    seen: Counter[str] = Counter()
    out: dict[str, tuple[str, Cells]] = {}
    for row in rows:
        kinds, cells = encode(row)
        base = digest(cells)
        seen[base] += 1
        out[f"{base}#{seen[base]}"] = (kinds, cells)
    return out


def columns_carried(rows: list[dict[str, object]]) -> str:
    """The canonical columns a copy carries, comma-separated, in canonical order."""
    present = {column for row in rows for column in row}
    return ",".join(column for column in COLUMNS if column in present)


def line_order(keys_in_file_order: list[str]) -> str:
    """The file order of a publication's rows as indexes into its sorted keys."""
    position = {key: i for i, key in enumerate(sorted(keys_in_file_order))}
    return ",".join(str(position[key]) for key in keys_in_file_order)


def in_file_order(keys: list[str], order: str) -> list[str]:
    """Inverse of `line_order`: the keys in the publication's line order."""
    ordered = sorted(keys)
    indexes = [int(i) for i in order.split(",")] if order else []
    if sorted(indexes) != list(range(len(ordered))):
        raise CellError("line order is not a permutation of the publication's rows")
    return [ordered[i] for i in indexes]
