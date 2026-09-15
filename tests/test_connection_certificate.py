from grid_mysteries.rendering import connection_certificate as cert

RECORD = {
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
