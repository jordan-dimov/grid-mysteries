"""Is a captured artefact the publisher's answer, and is a run's set whole?

The watchdog's size band asks a proxy question, and it was wrong five times
in three weeks (2026-09-18 to 2026-10-03): weekends, a quiet Friday, a
bank-holiday-shaped gap, each a thin but genuine day. What the archive needs
to know is whether the bytes are the publisher's data, not a challenge or
error page, and, where the publisher pages its answer, whether every page
was taken. Those can be read from the bytes.

A verdict is ``True`` (valid), ``False`` (not the publisher's data, or an
incomplete set) or ``None`` (no structural test applies, as for an HTML page
captured as a page), each with a reason. Pure: bytes in, verdicts out.
"""

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

#: Strategies that may fetch an HTML page as the artefact itself; such a
#: page has no structure to test beyond "not a challenge".
PAGE_STRATEGIES = frozenset({"url", "gov_assets"})
#: URL marks of a data endpoint: HTML from one of these is never the data.
DATA_URL = ("/api/", "/exports/", ".csv", ".json", ".xlsx", ".xls", ".pdf", ".zip")
CHALLENGE_MARKERS = (
    b"cf-chl",
    b"challenge-platform",
    b"<title>Just a moment...</title>",
    b"Attention Required! | Cloudflare",
)
SNIFF = 65536
ZIP_MAGIC = b"PK\x03\x04"
OLE_MAGIC = b"\xd0\xcf\x11\xe0"
PDF_MAGIC = b"%PDF"


@dataclass(frozen=True)
class Verdict:
    valid: bool | None
    reason: str


def artefact(body: bytes, *, content_type: str, url: str, strategy: str) -> Verdict:
    """One artefact's bytes against what its strategy and response promise."""
    if not body:
        return Verdict(False, "empty body")
    head = body[:SNIFF]
    if any(m in head for m in CHALLENGE_MARKERS):
        return Verdict(False, "challenge page")
    kind = content_type.split(";")[0].strip().lower()
    path = url.split("?")[0].lower()
    lead = head.lstrip()[:1]
    if lead == b"<" and "xml" not in kind:
        if strategy in PAGE_STRATEGIES and "html" in kind and not any(m in path for m in DATA_URL):
            return Verdict(None, "an HTML page; no structural test")
        return Verdict(False, f"HTML where data was expected ({kind or 'no type'})")
    if "json" in kind or (lead in (b"{", b"[") and not path.endswith(".csv")):
        try:
            json.loads(body)
        except ValueError as exc:
            return Verdict(False, f"JSON does not parse: {exc}")
        return Verdict(True, "JSON parses")
    if "spreadsheetml" in kind or path.endswith((".xlsx", ".zip")):
        return Verdict(
            head.startswith(ZIP_MAGIC),
            "zip container" if head.startswith(ZIP_MAGIC) else "not a zip container",
        )
    if path.endswith(".xls") or "ms-excel" in kind:
        ok = head.startswith((OLE_MAGIC, ZIP_MAGIC))
        return Verdict(ok, "spreadsheet container" if ok else "not a spreadsheet container")
    if path.endswith(".pdf") or "pdf" in kind:
        return Verdict(
            head.startswith(PDF_MAGIC), "PDF" if head.startswith(PDF_MAGIC) else "not a PDF"
        )
    if (
        "csv" in kind
        or path.endswith(".csv")
        or kind in ("application/octet-stream", "text/event-stream")
    ):
        first = head.split(b"\n", 1)[0]
        if any(sep in first for sep in (b",", b";", b"\t")):  # Opendatasoft exports use ';'
            return Verdict(True, "delimited text with a header line")
        if head.startswith(ZIP_MAGIC):
            return Verdict(True, "zip container")
        return Verdict(False, "no delimited header line")
    return Verdict(None, f"no structural test for {kind or 'no type'}")


def ocds_run(pages: Sequence[tuple[str, bytes]], window: date) -> Verdict:
    """One day's OCDS release package, in page order: every page a package,
    every page but the last pointing on, the last pointing nowhere, and every
    release dated inside the window (the previous UTC day)."""
    if not pages:
        return Verdict(False, "no page captured")
    releases = 0
    for i, (dataset, body) in enumerate(pages):
        try:
            package = json.loads(body)
        except ValueError:
            return Verdict(False, f"{dataset}: not JSON")
        if not isinstance(package, dict) or not isinstance(package.get("releases"), list):
            return Verdict(False, f"{dataset}: not a release package")
        has_next = bool((package.get("links") or {}).get("next"))
        last = i == len(pages) - 1
        if last and has_next:
            return Verdict(False, f"{dataset}: the last page captured points to a next page")
        if not last and not has_next:
            return Verdict(False, f"{dataset}: a page before the last has no next link")
        outside = [
            r.get("date", "")
            for r in package["releases"]
            if not str(r.get("date", "")).startswith(window.isoformat())
        ]
        if outside:
            return Verdict(False, f"{dataset}: {len(outside)} release(s) dated outside {window}")
        releases += len(package["releases"])
    return Verdict(
        True,
        f"{len(pages)} page(s), {releases} release(s), all dated {window}, pagination complete",
    )
