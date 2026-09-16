"""The As-of Connection Record Certificate, rendered from its record.

A pure function of the certificate's JSON (`certificate.json`) and the
bundle manifest: every value printed is one the record carries. The text
is the template for any project; only the record changes.
"""

from datetime import date
from typing import Any

ISSUER = "A115 Ltd (Grid Mysteries)"
CLAIM = (
    "Independently verifiable provenance, publication time and reconstruction "
    "methodology, suitable for scrutiny by counsel, experts, lenders and regulators."
)
SCOPE = (
    "This certificate states what NESO's published Transmission Entry Capacity (TEC) "
    "Register said about the named project on each of the two dates, and every change "
    "between them, each with the first copy of the register that showed it. It is a "
    "factual record of publication. It contains no forecast of energisation, no view "
    "on the cause of any change, and no opinion on any party's contractual entitlement. "
    "NESO's own caveat applies: project status in the register is NESO's best-known "
    "classification, not authoritative project information."
)
METHOD = (
    "Copies of the register (vintages) come from NESO's disclosures under the "
    "Environmental Information Regulations (one file per publication date), Wayback "
    "Machine captures of the data-portal resource, and live fetches of that resource; "
    "each copy's publication date and its SHA-256 are journalled at acquisition. The "
    "copy in force on a date is the latest published on or before it. Rows are matched "
    "to the project by the register's own project name (letters and digits, case "
    "ignored) and, where stated, stage; customer name and connection site are "
    "attributes whose changes are recorded. A copy with no matching row is an absence "
    "and one with several is ambiguous; both are recorded as changes of presence. A "
    "copy whose row count is more than a fifth below the previous copy's and whose "
    "successor recovers is a suspect copy (a partial export); an absence from such a "
    "copy is reported as that, not as an absence from the register. "
    "Values are compared as published, with dates parsed (so a respelled date is not a "
    "change), numbers compared numerically and text compared ignoring case and "
    "whitespace; the printed values are the published spellings. Two declared "
    "unifications apply: the register's project id is compared on its 15-character "
    "form (the 18-character form appends a checksum to the same id), and the "
    'agreement-type labels "Directly Connected" and "Direct Connection" are one '
    "label. Every other difference in published text is a change."
)


def day(value: object) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value or "")


def _as_of_table(record: dict[str, Any]) -> list[str]:
    a, b = record["as_of"]
    lines = [
        "| Field | As published on "
        f"{day(a['as_of'])} (copy of {day(a.get('vintage'))}) | As published on "
        f"{day(b['as_of'])} (copy of {day(b.get('vintage'))}) |",
        "|---|---|---|",
    ]
    if isinstance(a.get("state"), dict) and isinstance(b.get("state"), dict):
        for field in a["state"]:
            lines.append(f"| {field} | {a['state'][field] or '—'} | {b['state'][field] or '—'} |")
    else:
        lines.append(f"| Presence | {a.get('state')} | {b.get('state')} |")
    lines += [
        "",
        f"Copy in force on {day(a['as_of'])}: SHA-256 `{a.get('sha256', '')}`  ",
        f"Copy in force on {day(b['as_of'])}: SHA-256 `{b.get('sha256', '')}`",
    ]
    return lines


def _changes_table(record: dict[str, Any]) -> list[str]:
    changes = record["changes"]
    if not changes:
        return ["No change between the two copies in force."]
    lines = [
        "| # | First shown in copy of | Field | "
        "Previously published (last seen in copy of) | Newly published |",
        "|---|---|---|---|---|",
    ]
    for i, c in enumerate(changes, start=1):
        lines.append(
            f"| {i} | {day(c['first_shown'])} | {c['field']} | {c['previous'] or '—'} "
            f"({day(c['last_previous'])}) | {c['current'] or '—'} |"
        )
    return lines


def render_certificate(record: dict[str, Any], bundle: dict[str, Any]) -> str:
    """The certificate, two pages of Markdown.

    `bundle` carries: issued (date), certificate_id, manifest_sha256,
    files (count), declaration_sha256, proofs (list of text lines).
    """
    a, b = record["as_of"]
    stage = f", stage {record['stage']}" if record.get("stage") else ""
    lines = [
        "# As-of Connection Record Certificate",
        "",
        f"**Project:** {record['project']}{stage}  ",
        f"**Dates certified:** {day(a['as_of'])} and {day(b['as_of'])}  ",
        f"**Certificate id:** `{bundle['certificate_id']}`  ",
        f"**Issued:** {day(bundle['issued'])} by {ISSUER}  ",
        f"**Register copies consulted:** {record['vintages_consulted']} "
        f"({day(record['first_vintage'])} to {day(record['last_vintage'])}); "
        f"{record['vintages_absent']} with no matching row, "
        f"{record['vintages_ambiguous']} ambiguous, "
        f"{record.get('vintages_suspect', 0)} suspect (partial exports)",
        "",
        f"*{CLAIM}*",
        "",
        "## 1. What the register published on each date",
        "",
        *_as_of_table(record),
        "",
        "## 2. Every change between the two dates",
        "",
        "Each change is dated by the first copy of the register that showed it; the "
        "previous value is dated by the last copy that still carried it. Between those "
        "two copies no copy is held, so the change entered the published register "
        "somewhere in that interval.",
        "",
        *_changes_table(record),
        "",
        "## 3. Scope",
        "",
        SCOPE,
        "",
        "## 4. Method",
        "",
        METHOD,
        "",
        "## 5. Evidence bundle",
        "",
        f"This certificate is rendered from `certificate.json` in the bundle and from the "
        f"bundle's manifest. The manifest (`MANIFEST.json`, SHA-256 `{bundle['manifest_sha256']}`, "
        f"which is the certificate id) lists {bundle['files']} files with their digests: the "
        "certificate record, the rows matched in every copy consulted (`extracts.ndjson`), "
        "the journal lines that identify each copy's source, publication basis and digest "
        "(`journal-extract.ndjson`), and the two full register copies in force on the "
        "certified dates (`registers/`). This document quotes the manifest's digest and so "
        "is not listed in it; it is witnessed beside it. Run `python3 verify.py` in the "
        "bundle to recompute every digest offline. The manifest's digest and this document's "
        "are each witnessed by OpenTimestamps and by RFC 3161 tokens from two authorities, in "
        "the files beside them.",
        "",
    ]
    for proof in bundle.get("proofs", []):
        lines.append(f"- {proof}")
    lines += [
        "",
        f"Series declaration under which the register archive is maintained: SHA-256 "
        f"`{bundle['declaration_sha256']}` "
        "(investigations/014-gb-connection-slippage/DECLARATION.md).",
        "",
        "---",
        "",
        f"{ISSUER}. Factual findings only; no expert opinion is expressed. "
        "Reproduction of the method is invited; the code and tests are public.",
        "",
    ]
    return "\n".join(lines)
