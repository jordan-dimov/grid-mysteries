"""The Balancing Bill: the public page of investigation 013.

A pure function of `evidence/tracker.json`: every number on the page comes
from a row of that file, nothing is computed here beyond formatting, and the
same tracker always renders the same bytes. Self-contained HTML, inline CSS,
no script, no external asset. The investigation keeps its id, folder and
declaration name; "The Balancing Bill" is the public name only.
"""

from datetime import date
from decimal import Decimal
from html import escape
from typing import Any

TITLE = "The Balancing Bill"
SUBTITLE = "Who got paid to keep Britain's grid balanced, day by day"
REPO_URL = "https://github.com/jordan-dimov/grid-mysteries"
INVESTIGATION_PATH = "investigations/013-the-cover-price-tracker"
CREDIBILITY = (
    "Built by Jordan Dimov, A115. Previously built trading and settlement systems "
    "at Shell, Centrica and Limejump."
)
CALL_TO_ACTION = "Need a day reconstructed for a dispute or a lender? jdimov@a115.co.uk"
CALL_TO_ACTION_EMAIL = "jdimov@a115.co.uk"

INTRO = (
    "When there is more wind in Scotland than the cables can carry, the grid "
    "operator pays wind farms to switch off and other stations to switch on. "
    "This page shows what that cost each day and who got the money, worked out "
    "from the official published data with a method locked before the data was "
    "looked at."
)

COLUMNS = (
    "Day",
    "Paid out",
    "To wind farms, for switching off",
    "To gas stations, for switching on",
    "Everything else",
    "Price paid to gas, £/MWh",
    "Above the market price by",
    "Spent outside the main market",
    "Grid operator's own figure",
    "Official figure vs the headline number",
)

BLANK = "—"
MILLION = Decimal(1_000_000)


# ---------------------------------------------------------------- formatting


def money_m(value: str | None) -> str:
    """£ as millions with two decimals, e.g. £33.61m."""
    if value is None:
        return BLANK
    return f"£{(Decimal(value) / MILLION).quantize(Decimal('0.01')):,.2f}m"


def percent(value: str | None) -> str:
    if value is None:
        return BLANK
    return f"{(Decimal(value) * 100).quantize(Decimal('0.1'))}%"


def money_and_share(gbp: str | None, share: str | None) -> str:
    if gbp is None:
        return BLANK
    return f"{money_m(gbp)} ({percent(share)})" if share is not None else money_m(gbp)


def price(value: str | None) -> str:
    if value is None:
        return BLANK
    return f"£{Decimal(value):,.2f}"


def day_label(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


def not_yet_published(as_of: str) -> str:
    return f"not yet published (as of {day_label(as_of)})"


# --------------------------------------------------------------------- cells


def row_cells(row: dict[str, Any], as_of: str) -> list[str]:
    """The ten cells of one table row, as plain text (no markup); the
    renderer escapes and decorates them. Mirrors COLUMNS in order."""
    seed = bool(row.get("seed"))
    if not row.get("available"):
        return [day_label(row["settlement_date"])] + ["no published data"] + [BLANK] * 8
    gas_price = price(row.get("gas_offer_vwap_gbp_per_mwh"))
    if seed and row.get("gas_offer_vwap_gbp_per_mwh") is not None:
        gas_price += " †"
    outcome = row.get("outcome") or {}
    l1 = outcome.get("l1_constraints_gbp")
    if l1 is not None:
        neso_cell = f"{money_m(l1)} (published {day_label(outcome['vintage'])})"
        ratio = outcome.get("ratio_l1_to_two_cut")
        versus = (
            f"{Decimal(ratio).quantize(Decimal('0.01'))}× the headline number"
            if ratio is not None
            else BLANK
        )
    else:
        neso_cell = not_yet_published(as_of)
        versus = BLANK
    if row.get("bsad_net_gbp") is not None:
        outside = money_and_share(row["bsad_net_gbp"], row.get("bsad_share"))
    elif row.get("bsad_placeholder_only"):
        outside = "not yet populated"
    else:
        outside = BLANK
    return [
        day_label(row["settlement_date"]),
        money_m(row["paid_out_gbp"]),
        money_and_share(row["wind_bid_gbp"], row.get("wind_bid_share")),
        money_and_share(row["gas_offer_gbp"], row.get("gas_offer_share")),
        money_and_share(row["other_gbp"], row.get("other_share")),
        gas_price,
        price(row.get("premium_gbp_per_mwh")),
        outside,
        neso_cell,
        versus,
    ]


def render_table_row(row: dict[str, Any], as_of: str) -> str:
    cells = row_cells(row, as_of)
    badges = ""
    if row.get("seed"):
        badges += ' <span class="tag seed" title="Copied from investigation 012">seed</span>'
    if row.get("record"):
        badges += ' <span class="tag record">record</span>'
    classes = " ".join(
        c for c in ("seed" if row.get("seed") else "", "record" if row.get("record") else "") if c
    )
    when = f'<time datetime="{escape(row["settlement_date"])}">{escape(cells[0])}</time>'
    first = f'<th scope="row">{when}{badges}</th>'
    rest = "".join(f"<td>{escape(c)}</td>" for c in cells[1:])
    return f'<tr class="{classes}">{first}{rest}</tr>' if classes else f"<tr>{first}{rest}</tr>"


def render_table(rows: list[dict[str, Any]], as_of: str) -> str:
    """Newest day first."""
    ordered = sorted(rows, key=lambda r: r["settlement_date"], reverse=True)
    head = "".join(f'<th scope="col">{escape(c)}</th>' for c in COLUMNS)
    body = "\n".join(render_table_row(r, as_of) for r in ordered)
    return f"<table>\n<thead><tr>{head}</tr></thead>\n<tbody>\n{body}\n</tbody>\n</table>"


def render_corrections(corrections: list[dict[str, Any]] | None) -> str:
    if not corrections:
        return (
            "<p>None so far. When a figure on this page is corrected, the correction "
            "is listed here with its date and the old and new values; the old value "
            "is never silently overwritten.</p>"
        )
    items = "".join(
        f'<li><time datetime="{escape(c["date"])}">{escape(day_label(c["date"]))}</time>: '
        f"{escape(c['text'])}</li>"
        for c in corrections
    )
    return f"<ol>{items}</ol>"


# ---------------------------------------------------------------------- page


CSS = """\
:root{--ink:#1c1c1c;--muted:#5d5d5d;--rule:#d9d9d9;--bg:#fbfaf7;--seed:#eef0f4;--rec:#8a1c1c}
*{box-sizing:border-box}
body{margin:0;padding:1.25rem 1rem 3rem;background:var(--bg);color:var(--ink);
font:16px/1.5 Georgia,"Times New Roman",serif;max-width:72rem;margin-inline:auto}
h1{font-size:2rem;line-height:1.15;margin:0 0 .25rem}
h2{font-size:1.2rem;margin:2rem 0 .5rem}
.subtitle{color:var(--muted);font-size:1.1rem;margin:0 0 1.25rem}
p{max-width:44rem}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:1rem -1rem;padding:0 1rem}
table{border-collapse:collapse;width:100%;min-width:64rem;font-size:.9rem;
font-family:system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
th,td{padding:.45rem .5rem;border-bottom:1px solid var(--rule);text-align:right;
vertical-align:top;white-space:nowrap}
thead th{text-align:right;font-weight:600;color:var(--muted);white-space:normal;
vertical-align:bottom;font-size:.8rem}
thead th:first-child,tbody th{text-align:left}
tbody th{font-weight:600}
tr.seed td,tr.seed th{background:var(--seed);color:var(--muted)}
tr.record th{color:var(--rec)}
.tag{display:inline-block;font-size:.7rem;font-weight:600;letter-spacing:.02em;
text-transform:uppercase;padding:.05rem .35rem;border-radius:.2rem;margin-left:.35rem;
vertical-align:middle}
.tag.seed{background:#dfe3ea;color:#3b4250}
.tag.record{background:var(--rec);color:#fff}
.notes{font-size:.9rem;color:var(--muted);max-width:44rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--rule);
font-size:.95rem;color:var(--muted)}
a{color:inherit}
@media (max-width:600px){body{padding:1rem .75rem 2rem}h1{font-size:1.6rem}
table{font-size:.8rem}th,td{padding:.35rem .4rem}}
"""


def render_page(tracker: dict[str, Any], repo_url: str = REPO_URL) -> str:
    rows = tracker["rows"]
    as_of = tracker["run_date"]
    declaration = f"{repo_url}/blob/main/{INVESTIGATION_PATH}/DECLARATION.md"
    evidence = f"{repo_url}/tree/main/{INVESTIGATION_PATH}/evidence"
    digest = tracker.get("declaration_sha256", "")
    records = [r for r in rows if r.get("record")]
    record_line = (
        "Record days so far: " + ", ".join(day_label(r["settlement_date"]) for r in records) + "."
        if records
        else "No day has yet exceeded the seed rows' highest paid-out total."
    )
    prompt, email = CALL_TO_ACTION.removesuffix(CALL_TO_ACTION_EMAIL), CALL_TO_ACTION_EMAIL
    contact = f'{escape(prompt)}<a href="mailto:{email}">{email}</a>'
    latest = max((r["settlement_date"] for r in rows), default=None)
    latest_text = f" The latest day shown is {day_label(latest)}." if latest else ""
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(TITLE)}</title>
<meta name="description" content="{escape(SUBTITLE)}">
<style>
{CSS}</style>
</head>
<body>
<header>
<h1>{escape(TITLE)}</h1>
<p class="subtitle">{escape(SUBTITLE)}</p>
</header>
<main>
<p>{escape(INTRO)}{escape(latest_text)}</p>

<div class="scroll">
{render_table(rows, as_of)}
</div>

<p class="notes">Money in millions of pounds; percentages are shares of the day's paid-out
total. Rows marked <em>seed</em> are the eight days of 1 to 8 September 2026,
reconstructed by the earlier investigation that set this page's method; they set
the bar for the first <em>record</em> and are never themselves flagged.
&dagger; On seed rows the gas price uses that investigation's original volume
rule, which agrees with the settlement totals for switching-on but not for
switching-off; every later row uses the volume type that reconciles with the
settlement totals, and if none does the price is left blank.
<em>Not yet populated</em> means the grid operator's file for that day still holds
placeholder rows. <em>Not yet published</em> means the grid operator's own
attribution has not yet reached that day; it is added, with the date it
appeared, when it does. The <em>headline number</em> is wind payments plus gas
payments, which is what the daily trackers add up. A blank means the figure
could not be computed from what is pinned, never that it is zero.
{record_line}</p>

<h2>How the numbers are made</h2>
<p>The rules that pick the days, split the money and decide what counts were
written down and sealed before any day's data was fetched, and the sealed
text is never edited afterwards. <em>Paid out</em> is the gross money paid to
generators and other units in Great Britain's Balancing Mechanism on a
settlement day, from Elexon's published indicative cashflows. <em>To wind
farms</em> is money paid on bids by units registered as wind; <em>to gas
stations</em> is money paid on offers by gas units; <em>everything else</em> is
the remainder. The gas price pairs those pounds with the accepted volumes; the
market price is the APX day-ahead index for the same half-hours. <em>Spent
outside the main market</em> is the grid operator's published adjustment
trading for the day. <em>Grid operator's own figure</em> is its published
constraints cost, laid beside ours when it appears. Cashflows are indicative
and pre-settlement, and nothing here is a saving, a loss, or an attribution to
any cable or company.</p>
<p class="notes">Declaration (SHA-256 <code>{escape(digest[:16])}…</code>):
<a href="{escape(declaration)}">{escape(INVESTIGATION_PATH)}/DECLARATION.md</a>.
Evidence, every row and every source digest: <a href="{escape(evidence)}">evidence/</a>.
Code and tests: <a href="{escape(repo_url)}">{escape(repo_url.removeprefix("https://"))}</a>.
Page generated {escape(tracker.get("computed_at", "")[:10])} from
<code>evidence/tracker.json</code>; the page is a pure function of that file.</p>

<h2>Corrections</h2>
{render_corrections(tracker.get("corrections"))}
</main>
<footer>
<p>{escape(CREDIBILITY)}</p>
<p>{contact}</p>
</footer>
</body>
</html>
"""
