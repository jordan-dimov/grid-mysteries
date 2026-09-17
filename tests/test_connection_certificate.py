from typing import Any

from grid_mysteries.rendering import connection_certificate as cert

RECORD: dict[str, Any] = {
    "project": "Clash Gour",
    "stage": None,
    "dates": ["2021-03-31", "2025-07-22"],
    "as_of": [
        {
            "as_of": "2021-03-31",
            "vintage": "2021-03-30",
            "sha256": "a" * 64,
            "path": "p1",
            "state": {
                "Project name": "Clash Gour",
                "MW effective from (target date)": "2025-10-30",
            },
        },
        {
            "as_of": "2025-07-22",
            "vintage": "2025-07-22",
            "sha256": "b" * 64,
            "path": "p2",
            "state": {
                "Project name": "Clash Gour",
                "MW effective from (target date)": "2029/10/30",
            },
        },
    ],
    "changes": [
        {
            "field": "MW effective from (target date)",
            "previous": "2025-10-30",
            "current": "2027-10-30",
            "first_shown": "2024-05-17",
            "first_shown_sha256": "d" * 64,
            "last_previous": "2024-05-14",
        }
    ],
    "vintages_consulted": 330,
    "vintages_absent": 0,
    "vintages_ambiguous": 0,
    "first_vintage": "2021-03-30",
    "last_vintage": "2025-07-22",
}


def test_certificate_prints_only_what_the_record_carries():
    text = cert.render_certificate(
        RECORD,
        {
            "issued": "2026-09-15",
            "certificate_id": "014-clash-gour-2021-03-31-2025-07-22",
            "manifest_sha256": "e" * 64,
            "files": 7,
            "declaration_sha256": "c" * 64,
            "proofs": ["freetsa.org token: 2026-09-15T21:00:00Z"],
        },
    )
    assert "| MW effective from (target date) | 2025-10-30 | 2029/10/30 |" in text
    assert (
        "| 1 | 2024-05-17 | MW effective from (target date) | "
        "2025-10-30 (2024-05-14) | 2027-10-30 |" in text
    )
    assert "no forecast" in text and "entitlement" in text
    assert "- freetsa.org token: 2026-09-15T21:00:00Z" in text
    assert "330 (2021-03-30 to 2025-07-22)" in text
    assert text == cert.render_certificate(
        RECORD,
        {
            "issued": "2026-09-15",
            "certificate_id": "014-clash-gour-2021-03-31-2025-07-22",
            "manifest_sha256": "e" * 64,
            "files": 7,
            "declaration_sha256": "c" * 64,
            "proofs": ["freetsa.org token: 2026-09-15T21:00:00Z"],
        },
    )


def test_certificate_names_every_declaration_it_was_produced_under():
    """The bundle applies version 1's reading rules and version 2's aliases
    and partial-export rule, so both digests are printed. A bundle issued
    before the field falls back to the single digest."""
    bundle = {
        "issued": "2026-09-17",
        "certificate_id": "x",
        "manifest_sha256": "e" * 64,
        "files": 7,
        "declaration_sha256": "c" * 64,
        "declarations": [
            {"file": "DECLARATION.md", "sha256": "c" * 64},
            {"file": "DECLARATION-v2.md", "sha256": "f" * 64},
        ],
        "proofs": [],
    }
    text = cert.render_certificate(RECORD, bundle)
    assert f"`DECLARATION.md` SHA-256 `{'c' * 64}`" in text
    assert f"`DECLARATION-v2.md` SHA-256 `{'f' * 64}`" in text

    older = {k: v for k, v in bundle.items() if k != "declarations"}
    older_text = cert.render_certificate(RECORD, older)
    assert f"`DECLARATION.md` SHA-256 `{'c' * 64}`" in older_text
    assert "DECLARATION-v2.md" not in older_text


def test_as_of_table_when_one_date_has_a_row_and_the_other_does_not():
    """A project present on one date and absent on the other used to print
    the state mapping as a Python dict; the presence line carries the
    difference and the field rows dash the side with no single row."""
    a, b = RECORD["as_of"]
    record = {**RECORD, "as_of": [a, {**b, "state": "absent"}]}
    text = cert.render_certificate(
        record,
        {
            "issued": "2026-09-17",
            "certificate_id": "x",
            "manifest_sha256": "e" * 64,
            "files": 5,
            "declaration_sha256": "c" * 64,
            "proofs": [],
        },
    )
    assert "| Presence | present (one row) | absent |" in text
    assert "| Project name | Clash Gour | — |" in text
    assert "{'Project name'" not in text
