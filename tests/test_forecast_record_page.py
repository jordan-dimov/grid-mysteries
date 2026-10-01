from grid_mysteries.rendering import forecast_record as page

SUMMARY = {
    "declaration_sha256": "d" * 64,
    "plan_sha256": "p" * 64,
    "rule_version": "dddddddd",
    "run_date": "2026-10-01",
    "computed_at": "2026-10-01T16:00:00+00:00",
    "schema_modo_sha256": "m" * 64,
    "schema_rns_sha256": "r" * 64,
    "propositions": {
        "P-A": {"verdict": "undecided", "per_vintage": {}},
        "P-B": {"verdict": "undecided"},
        "P-C": {"verdict": "undecided", "pairs": 0},
    },
    "falsifiers": {
        "F1": True,
        "F2": {
            "per_year_strings": 400,
            "unexplained": 40,
            "share_pct": "10.0",
            "threshold_pct": "33.3",
            "fires": False,
        },
    },
}
ROW = {
    "key": "dddddddd|x",
    "rule_version": "dddddddd",
    "forecast_id": "x",
    "vintage": ["Modo Energy", "2025-01-13", "https://modoenergy.com/research/en/f1"],
    "scope": "2h",
    "period_start": 2026,
    "period_end": 2030,
    "status": "not yet scorable",
    "forecast": "90000",
    "realised": None,
    "realised_ids": [],
    "realised_scope": None,
    "signed_error": None,
    "absolute_error": None,
    "signed_error_pct": None,
    "absolute_error_pct": None,
    "scorable_after": "2031-01-01",
    "note": "no realised figure of scope '2h' for 2026, 2027, 2028, 2029, 2030",
}


def test_findings_lists_the_not_yet_scorable_table_as_a_result_and_never_says_wrong() -> None:
    text = page.render_findings(
        SUMMARY,
        [
            {
                "rule_version": "dddddddd",
                "outcome": "declined",
                "rule": "R-R2 no period unit",
                "figure": None,
            }
        ],
        [ROW],
        [],
        {
            "detail": [
                {
                    "scope": "fleet",
                    "year": 2025,
                    "months_read": list(range(1, 13)),
                    "complete": True,
                    "mean": "61000",
                }
            ],
            "restated": [],
        },
    )
    assert "none is scorable today" in text
    assert "| Modo Energy, 2025-01-13" in text and "2031-01-01" in text
    assert "£61,000" in text
    body = text.split("## What this never claims")[0].lower()
    assert "wrong" not in body and "wasteful" not in body
    assert "F1 (no scorable vintage): fires" in text
