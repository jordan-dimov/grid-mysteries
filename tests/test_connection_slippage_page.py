from grid_mysteries.rendering import connection_slippage as page

PAIR = {
    "baseline": "2024-07-05",
    "current": "2025-07-22",
    "baseline_units": 1800,
    "current_units": 2035,
    "matched": 1500,
    "new_entries": 535,
    "new_mw": "41234.50",
    "removed": 300,
    "removed_mw": "9876.00",
    "dated_both": 1400,
    "undated": 100,
    "unweighted": 20,
    "unchanged": 1000,
    "later": 350,
    "earlier": 50,
    "weighted_mw": "120000.00",
    "mw_years_net": "12345.678",
    "mw_years_later": "14000.100",
    "mw_years_earlier": "-1654.422",
    "capacity_changed": 40,
    "capacity_delta_mw": "-250.00",
    "f1_churn": False,
    "f2_thin": True,
}


def series(**extra):
    row = {
        "t_public": "2025-07-22",
        "sha256": "ab" * 32,
        "path": "data/raw/neso/tec-history/2025-07-22_wayback.csv",
        "rows": 2035,
        "units": 2035,
        "dated": 1726,
        "weighted": 1705,
        "swap_test": {"disagreements": 0, "swap_explained": 0, "flagged": False},
        "vs_previous": dict(PAIR, baseline="2025-07-01", mw_years_net="10.000"),
        "year_earlier_baseline": "2024-07-05",
        "vs_year_earlier": PAIR,
        "cumulative_mw_years_net": "99999.999",
    }
    return {
        "declaration_sha256": "c" * 64,
        "computed_at": "2026-09-15T20:00:00+00:00",
        "run_date": "2026-09-15",
        "vintages": {
            "journal_rows": 751,
            "distinct_dates": 731,
            "parsed": 699,
            "usable": 697,
            "skipped": [],
            "excluded": [],
        },
        "segments": [
            {
                "regime": "old",
                "first": "2014-01-31",
                "last": "2025-07-22",
                "vintages": 694,
                "swapped_vintages": ["2021-01-29"],
                "holes": [{"from": "2025-01-23", "to": "2025-03-21", "days": 57}],
                "annual": [dict(PAIR, year=2025, partial=True)],
                "rows": [row],
            },
            {
                "regime": "new",
                "first": "2026-05-19",
                "last": "2026-08-25",
                "vintages": 3,
                "swapped_vintages": [],
                "holes": [],
                "annual": [],
                "rows": [
                    dict(
                        row, t_public="2026-08-25", vs_year_earlier=None, year_earlier_baseline=None
                    )
                ],
            },
        ],
        "regime_break": {"last_old": "2025-07-22", "first_new": "2026-05-19", "days": 301},
        "propositions": {
            "P1": {
                "statement": "every complete year positive",
                "windows": [2015, 2016],
                "failing_years": [2016],
                "verdict": "fails",
            },
            "P2": {
                "statement": "reformed regime positive after a year",
                "start": "2026-05-19",
                "falsifier_date": "2027-06-30",
                "verdict": "undecided",
                "decided_on": None,
                "chained_mw_years_net": None,
            },
        },
        "f1_links": ["2020-07-30"],
        "f2_rows": ["2025-07-22"],
        "headline": {
            "t_public": "2025-07-22",
            "baseline": "2024-07-05",
            "mw_years_net": "12345.678",
            "mw_years_later": "14000.100",
            "mw_years_earlier": "-1654.422",
            "matched": 1500,
            "dated_both": 1400,
            "cumulative_mw_years_net": "99999.999",
        },
        **extra,
    }


def test_pair_cells_round_to_whole_units_and_keep_signs():
    assert page.pair_cells(PAIR) == [
        "5 Jul 2024",
        "22 Jul 2025",
        "1,500",
        "+12,346",
        "14,000",
        "-1,654",
        "350 / 50 / 1,000",
        "535 (41,235)",
        "300 (9,876)",
        "40 (-250)",
        "F2: matched under half of baseline",
    ]
    assert page.pair_cells(dict(PAIR, f2_thin=False))[-1] == "—"


def test_f1_is_shown_only_on_consecutive_links():
    html = page.render_page(series())
    assert html.count("F1: joined plus left over 20% of baseline") == 0
    churned = series()
    churned["segments"][0]["rows"][0]["vs_previous"]["f1_churn"] = True
    assert page.render_page(churned).count("F1: joined plus left over 20% of baseline") == 1


def test_headline_sentence_reads_from_the_headline_block_only():
    text = page.headline_sentence(series())
    assert "Between 5 Jul 2024 and 22 Jul 2025" in text
    assert "1,500 project-stages" in text
    assert "+12,346 megawatt-years" in text
    assert "14,000 later, -1,654 earlier" in text
    assert "+100,000 megawatt-years" in text
    assert "no headline" in page.headline_sentence(dict(series(), headline=None))


def test_page_is_self_contained_and_deterministic():
    html = page.render_page(series())
    assert html == page.render_page(series())
    assert "<script" not in html and "http" not in html.split("<body>")[0].split("<style>")[0]
    assert "GB Connection Slippage" in html
    assert "Regime break." in html
    assert "29 Jan 2021" in html  # the swapped vintage is disclosed
    assert "2025 (to 22 Jul 2025, partial)" in html
    assert "Since the reform: a separate series" in html
    assert 'class="partial"' in html
    assert "cccccccccccccccc…" in html
    assert "<strong>P1</strong>" in html and "not positive in 2016" in html
    assert "falsifier date 30 Jun 2027" in html
    assert "F1</strong> fired on 1 link(s)" in html


def test_markdown_lists_gaps_and_points_to_the_evidence():
    md = page.render_markdown(series())
    assert md.startswith("# GB Connection Slippage — series (investigation 014)")
    assert "| 2025 (to 22 Jul 2025, partial) |" in md
    assert "- Regime break: no copy between 2025-07-22 and 2026-05-19 (301 days)" in md
    assert "- 2021-01-29: day-month swapped dates" in md
    assert "evidence/series.json" in md
    assert (
        "- **P1** — every complete year positive: **fails** "
        "(2 complete years; not positive in 2016)." in md
    )
