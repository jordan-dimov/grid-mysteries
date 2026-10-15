"""gov.uk, "Cost Containment Mechanism (CCM) trigger prices and average
monthly prices: full table" (UK ETS Authority, under "Taking part in the UK
Emissions Trading Scheme markets"): two HTML tables, one row per assessment
month, each printing the UK allowance's average price for every month of
that row's monitoring period (three months to January 2023, six from
February 2023) as `£xx.xx`. Read as 024's schema pass found it
(`archives/024-govuk-ukets-monthly-prices/`).

The reading rule: in the row for month M with a k-month monitoring period,
`Month j average price` is the average price of month M − (k + 1 − j). A
month printed in several rows must print one value, or the read stops.
"""

import html as html_lib
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
ROW_LABEL = re.compile(r"^([A-Z][a-z]{2})-(\d{2})$")
POUNDS = re.compile(r"^£\s?(\d+(?:\.\d+)?)$")


@dataclass(frozen=True)
class Table:
    header: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    @property
    def window(self) -> int:
        return sum(1 for h in self.header if h.endswith("average price"))


def tables(text: str) -> list[Table]:
    body = text[text.find('<div class="govspeak">') :]
    body = body[: body.find("</main>")] if "</main>" in body else body
    out = []
    for tb in re.findall(r"<table.*?</table>", body, re.S):
        rows = [
            tuple(
                html_lib.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)
            )
            for row in re.findall(r"<tr.*?</tr>", tb, re.S)
        ]
        out.append(Table(rows[0], tuple(rows[1:])))
    return out


def month_of(label: str) -> tuple[int, int]:
    m = ROW_LABEL.match(label)
    if not m or m.group(1) not in MONTHS:
        raise ValueError(f"not a Mon-YY label: {label!r}")
    return 2000 + int(m.group(2)), MONTHS.index(m.group(1)) + 1


def months_before(year: int, month: int, k: int) -> list[tuple[int, int]]:
    """The k calendar months before (year, month), earliest first."""
    out = []
    y, m = year, month
    for _ in range(k):
        m -= 1
        if m == 0:
            y, m = y - 1, 12
        out.append((y, m))
    return list(reversed(out))


def format_profile(path: Path) -> dict:
    """Table count, headers, row counts and cell forms, with no value read."""
    out = []
    for t in tables(path.read_text(encoding="utf-8")):
        price_cols = [i for i, h in enumerate(t.header) if h.endswith("average price")]
        forms = {"pounds": 0, "other": 0}
        for r in t.rows:
            for i in price_cols:
                forms["pounds" if i < len(r) and POUNDS.match(r[i]) else "other"] += 1
        out.append(
            {
                "header": list(t.header),
                "rows": len(t.rows),
                "row_labels_mon_yy": sum(1 for r in t.rows if ROW_LABEL.match(r[0])),
                "average_price_forms": forms,
            }
        )
    return {"tables": out}


def read(path: Path) -> dict[tuple[int, int], Decimal]:
    """(year, month) -> average UK allowance price in GBP/t, from every row
    that prints it; a disagreement between rows stops the read, a cell that
    is not `£xx.xx` is skipped (the months not yet observed)."""
    out: dict[tuple[int, int], Decimal] = {}
    for t in tables(path.read_text(encoding="utf-8")):
        k = t.window
        price_cols = [i for i, h in enumerate(t.header) if h.endswith("average price")]
        period_col = next(i for i, h in enumerate(t.header) if "monitoring period" in h)
        for r in t.rows:
            year, month = month_of(r[0])
            months = months_before(year, month, k)
            printed = [x.strip()[:3] for x in r[period_col].split(",")]
            if printed != [MONTHS[m - 1] for _, m in months]:
                period = r[period_col]
                raise ValueError(f"row {r[0]}: period {period!r} is not the {k} months before it")
            for (y, m), i in zip(months, price_cols, strict=True):
                cell = POUNDS.match(r[i]) if i < len(r) else None
                if not cell:
                    continue
                value = Decimal(cell.group(1))
                if (y, m) in out and out[y, m] != value:
                    raise ValueError(f"month {y}-{m:02d} prints {out[y, m]} and {value}")
                out[y, m] = value
    return out
