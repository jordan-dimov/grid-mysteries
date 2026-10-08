"""What we hold: the public index of the vintage archive, at /vintages/.

The unattended capture (`grid_mysteries.capture`) fetches a planned list of
public resources every day and writes one manifest line per artefact it
looked at: the day, the publisher's URL, the SHA-256 of the bytes, where
the bytes are kept, and, when the bytes are the ones already held, the day
they were first seen. Each day's manifest is committed with its
OpenTimestamps and RFC 3161 proofs (`data/manifests/`). This page is a pure
function of those manifests: for every resource, how many days it has been
observed, how many distinct files have been held, how big they are, and
when the file the publisher serves today was first seen. It makes no claim
about why a publisher changed a file, only that the bytes differed.

The artefacts themselves are held privately, under their publishers'
terms; the manifests are public, and a copy of any artefact is available
against its digest. The page says so.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Final

from grid_mysteries.rendering.connection_slippage import CREDIBILITY, CSS, REPO_URL

TITLE: Final = "What we hold"
SUBTITLE: Final = (
    "The vintage archive: public electricity-system files captured every day, each copy "
    "held by its digest and each day's manifest witnessed"
)
CONTACT_EMAIL: Final = "jdimov@a115.co.uk"
MANIFESTS_URL: Final = f"{REPO_URL}/tree/main/data/manifests"

#: How a publisher is named on the page, by the manifest's `source`.
PUBLISHERS: Final[dict[str, str]] = {
    "neso": "NESO",
    "elexon": "Elexon",
    "eso": "ESO EAD (Bulgaria)",
    "contracts-finder": "Contracts Finder",
    "find-a-tender": "Find a Tender",
    "desnz": "DESNZ",
    "octopus": "Octopus Energy",
    "ukpn": "UK Power Networks",
    "nged": "National Grid Electricity Distribution",
    "ssen": "SSEN",
    "ofgem": "Ofgem",
}

#: One plain sentence per captured resource, by (source, resource). A
#: resource the manifests hold and this table does not name fails the test,
#: so nothing reaches the page undescribed.
DESCRIPTIONS: Final[dict[tuple[str, str], str]] = {
    ("neso", "tec-register"): (
        "The Transmission Entry Capacity register: every generation, storage and "
        "interconnector connection contract with its capacity and date, published about "
        "twice a week, each copy overwriting the last."
    ),
    ("neso", "daily-balancing-costs-2026-27"): (
        "Daily balancing costs for 2026-27, the file the Balancing Bill reads."
    ),
    ("neso", "daily-balancing-volume-2026-27"): "Daily balancing volumes for 2026-27.",
    ("neso", "disaggregated-bsad-2026-27"): (
        "Disaggregated balancing services adjustment data for 2026-27."
    ),
    ("neso", "day-ahead-constraint-flows-and-limits"): (
        "Day-ahead constraint flows and limits across the transmission boundaries."
    ),
    ("neso", "skip-rates-inmerit-allbm-2026-08"): (
        "Skip rates: in-merit Balancing Mechanism units, all units, for August 2026 (a "
        "monthly dataset with a new identifier each month)."
    ),
    ("neso", "skip-rates-exclusions-2026-08"): "Skip rates: the exclusions for August 2026.",
    ("neso", "eac"): (
        "Enduring Auction Capability results: response and reserve results by unit, the "
        "positions investigation 011 read."
    ),
    ("neso", "existing-agreements-register"): (
        "The Existing Agreements register, the one NESO list that names demand projects, "
        "overwritten in place under one document identifier."
    ),
    ("neso", "connections-reform-results-page"): (
        "The connections reform results page, which links the Existing Agreements register."
    ),
    ("neso", "24-months-ahead-constraint-cost-forecast"): (
        "The 24-months-ahead constraint cost forecast, a small file overwritten monthly."
    ),
    ("neso", "24-months-ahead-constraint-limits"): (
        "The 24-months-ahead constraint limits, published and overwritten the same way."
    ),
    ("neso", "bsuos-monthly-forecast"): (
        "The BSUoS monthly forecast package, every CSV it lists, a new one each month."
    ),
    ("elexon", "remit"): (
        "REMIT inside-information messages from Balancing Mechanism participants, each "
        "message's updates and withdrawals as they are published."
    ),
    ("eso", "joining-map"): (
        "The public connection-application map of Bulgaria's transmission operator, the "
        "instrument of forward study F004."
    ),
    ("contracts-finder", "ocds-daily"): (
        "UK public-sector contract notices published that day, in the Open Contracting "
        "Data Standard, every page."
    ),
    ("find-a-tender", "ocds-daily"): (
        "UK above-threshold tender notices updated that day, in the Open Contracting Data "
        "Standard, every page."
    ),
    ("desnz", "repd-quarterly-extract"): (
        "The Renewable Energy Planning Database quarterly extract; the publication page is "
        "captured daily so a new extract is held the day it lands."
    ),
    ("octopus", "product-agile-24-10-01"): (
        "The Agile Octopus tariff product (AGILE-24-10-01) from the supplier's public API."
    ),
    ("octopus", "smart-agile-page"): "The Agile Octopus product page.",
    ("octopus", "smart-tariffs-terms"): (
        "The smart tariffs terms and conditions page, which changes without notice."
    ),
    ("ukpn", "overall-queue-insights"): "Overall connection queue insights for UKPN's area.",
    ("ukpn", "large-demand-list"): (
        "The anonymised large demand connection list, the only DNO list of demand projects."
    ),
    ("ukpn", "data-centres-by-local-authority"): (
        "Operational and pipeline data-centre capacity by local authority."
    ),
    ("ukpn", "demand-modification-application-lead-times"): (
        "The longest demand modification-application lead times per grid supply point."
    ),
    ("nged", "connections-reform-register"): (
        "The connections reform register of projects NGED manages under CMP435, generation "
        "and storage only."
    ),
    ("nged", "connections-reform-outcomes"): (
        "Connections reform outcomes: NESO gate, phase and queue position per NGED-managed project."
    ),
    ("ssen", "embedded-capacity-register"): (
        "The Embedded Capacity Register package, every monthly copy the publisher lists "
        "as a separate resource."
    ),
    ("ofgem", "data-centre-connection-reforms"): (
        "The consultation page on proposed data-centre connection reforms, captured so the "
        "decision document is held the day it is published."
    ),
}


@dataclass(frozen=True)
class ResourceSummary:
    source: str
    resource: str
    first_day: str  # the first day the resource was observed
    last_day: str  # the last day it was observed
    days: int  # days on which it was observed
    files: int  # distinct files held (by digest; a publisher's metadata is not a file)
    new_on_days: int  # days on which at least one new file was held
    bytes: int  # the size of every distinct file held
    current_since: str | None  # for a single-file resource: the day today's bytes were first seen
    datasets: int  # distinct datasets the resource yields (one for a single-file resource)


def read_manifests(directory: Path) -> list[dict[str, Any]]:
    """Every manifest line under `directory`, in day order."""
    rows: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.ndjson")):
        with path.open() as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def is_metadata(row: dict[str, Any]) -> bool:
    return str(row.get("dataset", "")).endswith("-META")


def summarise(rows: Iterable[dict[str, Any]]) -> list[ResourceSummary]:
    """One summary per (source, resource), sorted by publisher then resource."""
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        by_key.setdefault((row["source"], row["resource"]), []).append(row)
    out = []
    for (source, resource), group in sorted(by_key.items()):
        days = sorted({r["day"] for r in group})
        files = [r for r in group if not is_metadata(r)]
        digests: dict[str, int] = {}
        for r in files:
            digests.setdefault(r["sha256"], int(r.get("bytes") or 0))
        new_days = {r["day"] for r in files if r.get("unchanged_from") is None}
        datasets = {r["dataset"] for r in files}
        current_since = None
        if len(datasets) == 1 and files:
            latest = max(files, key=lambda r: r["day"])
            current_since = latest.get("unchanged_from") or latest["day"]
        out.append(
            ResourceSummary(
                source,
                resource,
                days[0],
                days[-1],
                len(days),
                len(digests),
                len(new_days),
                sum(digests.values()),
                current_since,
                len(datasets),
            )
        )
    return out


def size(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f} GB"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} MB"
    if n >= 1_000:
        return f"{n / 1_000:.0f} kB"
    return f"{n} B"


def day_label(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{d}/{m}/{y}"


def publisher(source: str) -> str:
    return PUBLISHERS.get(source, source)


def describe(source: str, resource: str) -> str:
    try:
        return DESCRIPTIONS[(source, resource)]
    except KeyError as exc:
        raise KeyError(
            f"no public description for the captured resource {source}/{resource}"
        ) from exc


def render_row(s: ResourceSummary) -> str:
    if s.datasets == 1:
        current = f"current file first seen {day_label(s.current_since)}" if s.current_since else ""
    else:
        current = f"{s.datasets} datasets"
    return (
        "<tr>"
        f"<td>{escape(publisher(s.source))}</td>"
        f'<td><code>{escape(s.resource)}</code><br><span class="what">'
        f"{escape(describe(s.source, s.resource))}</span></td>"
        f"<td>{day_label(s.first_day)}</td>"
        f'<td class="n">{s.days}</td>'
        f'<td class="n">{s.files}</td>'
        f'<td class="n">{s.new_on_days}</td>'
        f'<td class="n">{escape(size(s.bytes))}</td>'
        f"<td>{escape(current)}</td>"
        "</tr>"
    )


VINTAGES_CSS: Final = """\
table.vintages{font-size:.85rem}
table.vintages td.n{text-align:right;white-space:nowrap}
table.vintages .what{color:var(--muted)}
p.notes{max-width:44rem}
"""


def render_page(summaries: list[ResourceSummary]) -> str:
    """The page, for the summaries given (empty is allowed and says so)."""
    first = min((s.first_day for s in summaries), default=None)
    last = max((s.last_day for s in summaries), default=None)
    files = sum(s.files for s in summaries)
    total = sum(s.bytes for s in summaries)
    span = (
        f"Manifests from {day_label(first)} to {day_label(last)}: {len(summaries)} resources, "
        f"{files} distinct files, {size(total)}."
        if first and last
        else "No manifests yet."
    )
    rows = "\n".join(render_row(s) for s in summaries)
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(TITLE)}</title>
<meta name="description" content="{escape(SUBTITLE)}">
<style>
{CSS}{VINTAGES_CSS}</style>
</head>
<body>
<header>
<h1>{escape(TITLE)}</h1>
<p class="subtitle">{escape(SUBTITLE)}</p>
</header>
<main>
<p class="notes">Public bodies in Britain's electricity system publish files that they then
overwrite: a register replaced twice a week, a forecast replaced monthly, a page edited in
place. Once replaced, the earlier copy is usually gone, and a question like &ldquo;what did
the register say on that date&rdquo; cannot be answered from the publisher. Since
{escape(day_label(first) if first else "the first capture")} an unattended job has fetched
each resource below every day and kept every copy whose bytes differed from the one held,
named by its SHA-256. {escape(span)}</p>
<table class="vintages">
<thead><tr><th>Publisher</th><th>Resource</th><th>Since</th><th>Days</th><th>Files</th>
<th>Days with a new file</th><th>Size</th><th>State</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
<p class="notes"><strong>What is public, and what is not.</strong> Each day's manifest, one
line per artefact with the publisher's URL, the digest and the day the bytes were first seen,
is committed to the repository with its OpenTimestamps proof and two RFC 3161 timestamps,
freetsa.org and DigiCert, taken the same day
(<a href="{escape(MANIFESTS_URL)}">data/manifests</a>). The artefacts themselves are held
privately, under their publishers' terms. A copy of any artefact, as held, is available
against its digest: write with the resource, the day and the digest from the manifest.</p>
<p class="notes"><strong>What this page never claims.</strong> A new file means the bytes
differed; it says nothing about why, or whether the publisher calls it a new version. A
day without a new file means the bytes matched, not that the publisher published nothing
elsewhere. Days are the capture's days, in UTC. Where a publisher's metadata said a file was
unchanged, the file was not fetched that day and the metadata is held instead. The archive
began on different days for different resources and has gaps where a fetch failed; the
manifests say which.</p>
</main>
<footer>
<p>{escape(CREDIBILITY)}</p>
<p>Questions, challenges or a copy of an artefact:
<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</footer>
</body>
</html>
"""


def render_from(directory: Path) -> str:
    return render_page(summarise(read_manifests(directory)))
