"""NESO's TEC Register, vintage by vintage: reading every era's file into rows.

The archive under `data/raw/neso/tec-history/` is journalled
(`journal.ndjson`, one line per file: `t_public`, `path`, `sha256`,
`format`, `source`). This module turns a journalled vintage into rows keyed
by canonical column names, parses every date spelling the register has
used, pins a new live vintage from the data portal, and nothing else. It
knows nothing about slippage; that is `investigations.connection_slippage`.

Column vocabularies per era (from the journal):

- 2014: `Mw Connected`, `Mw Increase/Decrease`, `MW Total`, `TEC Effective
  from Date`; from December 2014 `MW Effective Date`.
- 2015-02 to 2020-05: `MW Increase / Decrease`, `MW Total`, `MW Effective
  Date`.
- 2020-06 onward: `Stage`, `MW Increase / Decrease`, `Cumulative Total
  Capacity (MW)` (absent in four June 2020 files), `MW Effective From`;
  `Project ID` from 2021-11, `Gate` from 2025-12.

Date spellings seen in the effective-date column: spreadsheet date cells,
`YYYY-MM-DD`, `YYYY/MM/DD`, `DD/MM/YYYY`, `DD-Mon-YY`, and raw Excel serial
numbers (one April 2024 file). Six vintages carry date cells with day and
month swapped for days up to 12; detecting that is a per-vintage test in
the slippage module, and `swap_day_month` is the correction it applies.

Investigation 005's runner mapped neither the stage MW column nor the
`YYYY/MM/DD`, `DD-Mon-YY` and serial spellings, so those cells read as
blank there. This reader is the one 014 declares; 005's runner is left as
it ran.
"""

import csv
import json
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Final

from grid_mysteries.hashing import sha256_file

JOURNAL_PATH: Final = Path("data/raw/neso/tec-history/journal.ndjson")
RAW_DIR: Final = Path("data/raw/neso/tec-history")
CKAN_RESOURCE_ID: Final = "17becbab-e3e8-473f-b303-3806f43a6a10"
CKAN_RESOURCE_SHOW: Final = (
    f"https://api.neso.energy/api/3/action/resource_show?id={CKAN_RESOURCE_ID}"
)

ALIASES: Final[dict[str, str]] = {
    "project id": "Project ID",
    "plant id": "Project ID",
    "record id": "Project ID",
    "project number": "Project Number",
    "project name": "Project Name",
    "customer name": "Customer Name",
    "customer": "Customer Name",
    "user": "Customer Name",
    "connection site": "Connection Site",
    "connection point": "Connection Site",
    "stage": "Stage",
    "mw connected": "MW Connected",
    "mw increase / decrease": "MW Increase / Decrease",
    "mw increase/decrease": "MW Increase / Decrease",
    "mw increase decrease": "MW Increase / Decrease",
    "cumulative total capacity (mw)": "Cumulative Total Capacity (MW)",
    "mw total": "Cumulative Total Capacity (MW)",
    "mw effective from": "MW Effective From",
    "mw effective date": "MW Effective From",
    "tec effective from date": "MW Effective From",
    "project status": "Project Status",
    "agreement type": "Agreement Type",
    "host to": "HOST TO",
    "plant type": "Plant Type",
    "electricity connection: plant type": "Plant Type",
    "gate": "Gate",
}

CANONICAL_COLUMNS: Final = tuple(dict.fromkeys(ALIASES.values()))

_ISO: Final = re.compile(r"^(?P<y>\d{4})[-/](?P<m>\d{1,2})[-/](?P<d>\d{1,2})(?:[ T].*)?$")
_UK: Final = re.compile(r"^(?P<d>\d{1,2})/(?P<m>\d{1,2})/(?P<y>\d{4})(?:[ T].*)?$")
_MON: Final = re.compile(r"^(?P<d>\d{1,2})-(?P<mon>[A-Za-z]{3})-(?P<y>\d{2}|\d{4})$")
_SERIAL: Final = re.compile(r"^\d{5}(?:\.0+)?$")
_EXCEL_EPOCH: Final = date(1899, 12, 30)
_MONTHS: Final = {
    m: i
    for i, m in enumerate(
        ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"),
        start=1,
    )
}


def canon(header: object) -> str | None:
    key = " ".join(str(header or "").lower().replace("\n", " ").split())
    return ALIASES.get(key)


def _safe_date(y: int, m: int, d: int) -> date | None:
    try:
        return date(y, m, d)
    except ValueError:
        return None


def parse_date(value: object) -> date | None:
    """Every spelling the register's effective-date column has used.

    Spreadsheet date cells; `YYYY-MM-DD` and `YYYY/MM/DD`; `DD/MM/YYYY`;
    `DD-Mon-YY` (two-digit years are 2000-2099); and Excel serial numbers
    as numbers or five-digit strings. Anything else is undated, never
    guessed.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, int | float) and not isinstance(value, bool):
        if 20000 <= value <= 80000 and float(value).is_integer():
            return _EXCEL_EPOCH + timedelta(days=int(value))
        return None
    text = str(value or "").strip()
    if not text:
        return None
    if found := _ISO.match(text):
        return _safe_date(int(found["y"]), int(found["m"]), int(found["d"]))
    if found := _UK.match(text):
        return _safe_date(int(found["y"]), int(found["m"]), int(found["d"]))
    if found := _MON.match(text):
        month = _MONTHS.get(found["mon"].lower())
        if month is None:
            return None
        year = int(found["y"])
        year = year + 2000 if year < 100 else year
        return _safe_date(year, month, int(found["d"]))
    if _SERIAL.match(text):
        return _EXCEL_EPOCH + timedelta(days=int(float(text)))
    return None


def swap_day_month(value: date | None) -> date | None:
    """The day-month swapped reading of a date, where one exists.

    A date whose day and month are both 12 or less and differ has a second
    valid reading with them exchanged; this returns it. Unambiguous dates
    (day above 12, or day equal to month) return None.
    """
    if value is None or value.day > 12 or value.day == value.month:
        return None
    return _safe_date(value.year, value.day, value.month)


def parse_decimal(value: object) -> Decimal | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return Decimal(str(value))
    text = str(value or "").replace(",", "").strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def normalise(text: object) -> str:
    """Lower-case alphanumerics separated by single spaces (005's rule)."""
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip()


def normalise_stage(value: object) -> str:
    """`Stage` as the register prints it, with numeric spellings unified:
    1, 1.0 and 1.00 are one stage; blank stays blank."""
    text = str(value or "").strip()
    if not text:
        return ""
    number = parse_decimal(text)
    if number is None:
        return text
    return (
        str(number.normalize().to_integral_value())
        if number == number.to_integral_value()
        else str(number.normalize())
    )


def _cell(value: object) -> object:
    if isinstance(value, datetime):
        return value.date()
    return value


def rows_from_matrix(matrix: list[list[object]]) -> list[dict[str, object]]:
    """Rows keyed by canonical column name from a sheet given as a matrix.

    The header row is the first row that carries a `Project Name` column;
    rows above it (titles, notes) are skipped and rows without a project
    name are dropped.
    """
    header_index = next(
        (i for i, r in enumerate(matrix) if any(canon(c) == "Project Name" for c in r)), None
    )
    if header_index is None:
        return []
    headers = [canon(c) for c in matrix[header_index]]
    out = []
    for r in matrix[header_index + 1 :]:
        row = {h: _cell(v) for h, v in zip(headers, r, strict=False) if h}
        if str(row.get("Project Name") or "").strip():
            out.append(row)
    return out


def read_vintage(path: Path, fmt: str = "") -> list[dict[str, object]]:
    """Rows of one vintage file: csv, xlsx or xls; the sheet with most rows."""
    suffix = path.suffix.lower()
    if fmt == "csv" or suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
            return rows_from_matrix([list(r) for r in csv.reader(f)])
    if suffix == ".xlsx":
        import openpyxl

        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        best: list[dict[str, object]] = []
        for ws in wb.worksheets:
            rows = rows_from_matrix([list(r) for r in ws.iter_rows(values_only=True)])
            if len(rows) > len(best):
                best = rows
        return best
    if suffix == ".xls":
        import xlrd

        book = xlrd.open_workbook(path)
        best = []
        for sh in book.sheets():
            matrix = []
            for i in range(sh.nrows):
                vals: list[object] = []
                for j in range(sh.ncols):
                    c = sh.cell(i, j)
                    if c.ctype == xlrd.XL_CELL_DATE:
                        vals.append(datetime(*xlrd.xldate_as_tuple(c.value, book.datemode)).date())
                    else:
                        vals.append(c.value)
                matrix.append(vals)
            rows = rows_from_matrix(matrix)
            if len(rows) > len(best):
                best = rows
        return best
    return []


# ------------------------------------------------------------------ journal


def read_journal(journal_path: Path) -> list[dict]:
    return [json.loads(line) for line in journal_path.read_text().splitlines() if line.strip()]


def one_per_date(journal: list[dict]) -> list[dict]:
    """One journal entry per publication date: duplicates are dropped and,
    where two files claim one date, the one with more rows is kept."""
    by_date: dict[str, dict] = {}
    for entry in journal:
        if entry.get("duplicate_of"):
            continue
        d = entry["t_public"][:10]
        if d not in by_date or (entry.get("row_count") or 0) > (by_date[d].get("row_count") or 0):
            by_date[d] = entry
    return [by_date[d] for d in sorted(by_date)]


def verify_entry(entry: dict, repo_root: Path) -> Path:
    """The vintage's path, after checking its bytes still hash as journalled."""
    path = repo_root / entry["path"]
    digest = sha256_file(path)
    if digest != entry["sha256"]:
        raise RuntimeError(f"{entry['path']} no longer matches its journalled digest")
    return path


def load_vintages(
    journal_path: Path, repo_root: Path
) -> tuple[list[tuple[date, list[dict[str, object]], dict]], list[dict]]:
    """Every parsable vintage as (t_public, rows, journal entry), in date
    order, each file verified against its journalled digest first; plus the
    entries that could not be parsed, with the error."""
    vintages, skipped = [], []
    for entry in one_per_date(read_journal(journal_path)):
        path = verify_entry(entry, repo_root)
        try:
            rows = read_vintage(path, entry.get("format", ""))
        except Exception as exc:  # noqa: BLE001 - recorded, not hidden
            skipped.append(
                {
                    "t_public": entry["t_public"][:10],
                    "path": entry["path"],
                    "error": repr(exc)[:200],
                }
            )
            continue
        if not rows:
            skipped.append(
                {
                    "t_public": entry["t_public"][:10],
                    "path": entry["path"],
                    "error": "no header/rows parsed",
                }
            )
            continue
        vintages.append((date.fromisoformat(entry["t_public"][:10]), rows, entry))
    return vintages, skipped


# ----------------------------------------------------------------- live pin


def pin_live_vintage(
    journal_path: Path, raw_dir: Path, repo_root: Path, *, fetched_at: datetime
) -> dict | None:
    """Pin today's live TEC Register from the data portal as a new vintage.

    The vintage date is the CKAN resource's `last_modified` date, as for the
    archive's earlier live pins. If the journal already holds a `neso-ckan`
    entry for that date the file is verified and nothing is fetched (None
    is returned); an existing file that is not journalled is refused.
    """
    import httpx

    with httpx.Client(timeout=120, follow_redirects=True) as client:
        meta = client.get(CKAN_RESOURCE_SHOW).json()["result"]
        t_public = str(meta["last_modified"])[:10]
        existing = [
            e
            for e in read_journal(journal_path)
            if e.get("source") == "neso-ckan" and e["t_public"][:10] == t_public
        ]
        if existing:
            verify_entry(existing[0], repo_root)
            return None
        destination = raw_dir / f"{t_public}_neso-ckan.csv"
        if destination.exists():
            raise RuntimeError(f"{destination} exists but is not journalled; refusing to touch")
        response = client.get(meta["url"])
        response.raise_for_status()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.content)
    rows = read_vintage(destination, "csv")
    columns = list(rows[0].keys()) if rows else []
    entry = {
        "url": meta["url"],
        "source": "neso-ckan",
        "t_public": t_public,
        "t_public_basis": (
            f"CKAN resource last_modified {meta['last_modified']} and filename "
            f"{meta['url'].rsplit('/', 1)[-1]}; fetched live {fetched_at.date().isoformat()}"
        ),
        "path": str(destination.relative_to(repo_root)),
        "sha256": sha256_file(destination),
        "bytes": destination.stat().st_size,
        "format": "csv",
        "columns": columns,
        "row_count": len(rows),
        "fetched_at": fetched_at.isoformat(),
    }
    with journal_path.open("a") as out:
        out.write(json.dumps(entry) + "\n")
    return entry


# ------------------------------------------------------------- schema report

DATE_SPELLINGS: Final = (
    "date-cell",
    "iso-dash",
    "iso-slash",
    "uk",
    "dd-mon-yy",
    "serial",
    "blank",
    "other",
)
REQUIRED_COLUMNS: Final = (
    "Project Name",
    "Customer Name",
    "Connection Site",
    "MW Increase / Decrease",
    "MW Effective From",
)
#: A copy whose row count falls by more than this share against the previous
#: copy is flagged as a possible partial export.
ROW_COUNT_DROP: Final = Decimal("0.2")
UNDATED_SHARE: Final = Decimal("0.5")


def date_spelling(value: object) -> str:
    """Which of the register's date spellings a cell uses (for the report)."""
    if isinstance(value, datetime | date):
        return "date-cell"
    if isinstance(value, int | float) and not isinstance(value, bool):
        return "serial" if 20000 <= value <= 80000 else "other"
    text = str(value or "").strip()
    if not text:
        return "blank"
    if _ISO.match(text):
        return "iso-dash" if "-" in text[:8] else "iso-slash"
    if _UK.match(text):
        return "uk"
    if _MON.match(text):
        return "dd-mon-yy"
    if _SERIAL.match(text):
        return "serial"
    return "other"


def copy_report(
    t_public: date, rows: list[dict[str, object]], entry: dict, previous_rows: int | None
) -> dict[str, Any]:
    """One copy's schema facts: columns, blank rates, date spellings, row-count
    change, and the flags a reader should see before trusting the copy."""
    columns = sorted({tr for tr in (canon(c) for c in (entry.get("columns") or [])) if tr})
    n = len(rows)
    blanks = {
        col: sum(1 for r in rows if not str(r.get(col) or "").strip()) for col in REQUIRED_COLUMNS
    }
    spellings = dict.fromkeys(DATE_SPELLINGS, 0)
    for r in rows:
        spellings[date_spelling(r.get("MW Effective From"))] += 1
    flags: list[str] = []
    missing = [c for c in REQUIRED_COLUMNS if c not in columns]
    if missing:
        flags.append(f"missing columns {missing}")
    change: Decimal | None = None
    if previous_rows:
        change = (Decimal(n) - Decimal(previous_rows)) / Decimal(previous_rows)
        if change <= -ROW_COUNT_DROP:
            flags.append(f"row count fell {abs(change) * 100:.0f}% (possible partial export)")
    if n and Decimal(spellings["blank"] + spellings["other"]) / Decimal(n) > UNDATED_SHARE:
        flags.append("more than half of rows undated")
    if spellings["other"]:
        flags.append(f"{spellings['other']} unparseable date cells")
    return {
        "t_public": t_public.isoformat(),
        "source": entry.get("source"),
        "format": entry.get("format"),
        "sha256": entry.get("sha256"),
        "rows": n,
        "row_count_change": str(change.quantize(Decimal("0.001"))) if change is not None else None,
        "columns": columns,
        "blank": blanks,
        "date_spellings": spellings,
        "flags": flags,
    }


def schema_report(
    vintages: list[tuple[date, list[dict[str, object]], dict]], skipped: list[dict]
) -> dict[str, Any]:
    """The archive's schema report: every copy's facts, the eras (runs of one
    column vocabulary), the spelling totals, and the flagged copies."""
    copies: list[dict[str, Any]] = []
    previous: int | None = None
    for t, rows, entry in vintages:
        copies.append(copy_report(t, rows, entry, previous))
        previous = len(rows)
    eras: list[dict[str, Any]] = []
    for c in copies:
        if eras and eras[-1]["columns"] == c["columns"]:
            eras[-1]["last"] = c["t_public"]
            eras[-1]["copies"] += 1
        else:
            eras.append(
                {
                    "first": c["t_public"],
                    "last": c["t_public"],
                    "copies": 1,
                    "columns": c["columns"],
                }
            )
    totals = dict.fromkeys(DATE_SPELLINGS, 0)
    for c in copies:
        for k, v in c["date_spellings"].items():
            totals[k] += v
    return {
        "archive": "neso/tec-register",
        "copies": len(copies),
        "unparseable": skipped,
        "eras": eras,
        "date_spelling_totals": totals,
        "flagged": [{"t_public": c["t_public"], "flags": c["flags"]} for c in copies if c["flags"]],
        "per_copy": copies,
    }
