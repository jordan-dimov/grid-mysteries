from datetime import date, datetime
from decimal import Decimal

from grid_mysteries.sources import tec_register as tr


def test_every_date_spelling_the_register_has_used_parses():
    assert tr.parse_date("2027-10-30") == date(2027, 10, 30)
    assert tr.parse_date("2027/10/30") == date(2027, 10, 30)
    assert tr.parse_date("30/10/2027") == date(2027, 10, 30)
    assert tr.parse_date("31-Oct-21") == date(2021, 10, 31)
    assert tr.parse_date("01-Apr-2019") == date(2019, 4, 1)
    assert tr.parse_date("45960") == date(2025, 10, 30)  # Excel serial as text
    assert tr.parse_date(45960) == date(2025, 10, 30)
    assert tr.parse_date(45960.0) == date(2025, 10, 30)
    assert tr.parse_date(date(2025, 10, 30)) == date(2025, 10, 30)
    assert tr.parse_date(datetime(2025, 10, 30, 0, 0)) == date(2025, 10, 30)
    assert tr.parse_date("2025-10-30 00:00:00") == date(2025, 10, 30)


def test_unparseable_dates_are_undated_not_guessed():
    assert tr.parse_date("") is None
    assert tr.parse_date(None) is None
    assert tr.parse_date("57") is None
    assert tr.parse_date("TBC") is None
    assert tr.parse_date("2025-13-01") is None
    assert tr.parse_date("31/11/2025") is None
    assert tr.parse_date(True) is None
    assert tr.parse_date(3.5) is None


def test_swap_day_month_only_for_ambiguous_dates():
    assert tr.swap_day_month(date(2021, 1, 5)) == date(2021, 5, 1)
    assert tr.swap_day_month(date(2027, 1, 12)) == date(2027, 12, 1)
    assert tr.swap_day_month(date(2025, 10, 30)) is None  # day > 12
    assert tr.swap_day_month(date(2025, 3, 3)) is None  # day == month
    assert tr.swap_day_month(None) is None


def test_header_aliases_cover_every_era():
    assert tr.canon("Mw Increase/Decrease") == "MW Increase / Decrease"
    assert tr.canon("MW Increase / Decrease") == "MW Increase / Decrease"
    assert tr.canon("MW Increase Decrease") == "MW Increase / Decrease"
    assert tr.canon("MW Total") == "Cumulative Total Capacity (MW)"
    assert tr.canon("TEC Effective from Date") == "MW Effective From"
    assert tr.canon("MW Effective Date") == "MW Effective From"
    assert tr.canon("MW\nEffective From") == "MW Effective From"
    assert tr.canon("Customer") == "Customer Name"  # the 2020-07-23 copy's spelling
    assert tr.canon("Unknown column") is None


def test_stage_numeric_spellings_are_one_stage():
    assert tr.normalise_stage("1") == "1"
    assert tr.normalise_stage("1.0") == "1"
    assert tr.normalise_stage("1.00") == "1"
    assert tr.normalise_stage(1.0) == "1"
    assert tr.normalise_stage("2.5") == "2.5"
    assert tr.normalise_stage("") == ""
    assert tr.normalise_stage(None) == ""
    assert tr.normalise_stage("Phase A") == "Phase A"


def test_decimal_parsing_keeps_text_out_of_arithmetic():
    assert tr.parse_decimal("612") == Decimal("612")
    assert tr.parse_decimal("612.00") == Decimal("612.00")
    assert tr.parse_decimal("1,296") == Decimal("1296")
    assert tr.parse_decimal(333.33) == Decimal("333.33")
    assert tr.parse_decimal("") is None
    assert tr.parse_decimal("n/a") is None


def test_rows_from_matrix_finds_the_header_below_a_title_row():
    matrix: list[list[object]] = [
        ["TEC Register", None, None],
        ["Project Name", "Customer Name", "MW Increase/Decrease", "TEC Effective from Date"],
        ["Wind A", "Co", 100, datetime(2027, 10, 30)],
        ["", "", "", ""],
        [None, None, None, None],
    ]
    rows = tr.rows_from_matrix(matrix)
    assert rows == [
        {
            "Project Name": "Wind A",
            "Customer Name": "Co",
            "MW Increase / Decrease": 100,
            "MW Effective From": date(2027, 10, 30),
        }
    ]
    assert tr.rows_from_matrix([["nothing", "here"]]) == []


def test_one_per_date_drops_duplicates_and_prefers_the_richer_file():
    journal = [
        {"t_public": "2024-01-05", "path": "a", "row_count": 10},
        {"t_public": "2024-01-05", "path": "b", "row_count": 12},
        {"t_public": "2024-01-05", "path": "c", "row_count": 99, "duplicate_of": "b"},
        {"t_public": "2024-01-02T00:00:00", "path": "d", "row_count": 5},
    ]
    kept = tr.one_per_date(journal)
    assert [e["path"] for e in kept] == ["d", "b"]


# ------------------------------------------------------------- schema report


def test_every_era_header_row_maps_the_required_columns():
    """The archive's 25 column vocabularies (tests/fixtures/tec-register-eras.json,
    taken from the journal) must each map every column the series requires,
    except the four copies the report already flags for a missing column."""
    import json
    from pathlib import Path

    eras = json.loads((Path(__file__).parent / "fixtures/tec-register-eras.json").read_text())
    assert len(eras) >= 20
    known_gaps = {
        "2020-07-09",
        "2021-06-22",
    }  # customer column absent (three July 2020 copies; one 2021 file)
    for era in eras:
        mapped = {tr.canon(h) for h in era["headers"]}
        missing = set(tr.REQUIRED_COLUMNS) - mapped
        if era["first"] in known_gaps or not era["headers"]:
            continue
        assert not missing, (era["first"], missing, era["headers"])


def test_date_spelling_classifies_every_form_the_register_has_used():
    assert tr.date_spelling(date(2025, 10, 30)) == "date-cell"
    assert tr.date_spelling(datetime(2025, 10, 30)) == "date-cell"
    assert tr.date_spelling("2025-10-30") == "iso-dash"
    assert tr.date_spelling("2025/10/30") == "iso-slash"
    assert tr.date_spelling("30/10/2025") == "uk"
    assert tr.date_spelling("31-Oct-21") == "dd-mon-yy"
    assert tr.date_spelling("45960") == "serial"
    assert tr.date_spelling(45960) == "serial"
    assert tr.date_spelling("") == "blank"
    assert tr.date_spelling(None) == "blank"
    assert tr.date_spelling("TBC") == "other"


def entry(**kw):
    base = {
        "columns": [
            "Project Name",
            "Customer Name",
            "Connection Site",
            "MW Increase / Decrease",
            "MW Effective From",
        ],
        "source": "neso-doc",
        "format": "xlsx",
        "sha256": "0" * 64,
    }
    base.update(kw)
    return base


def test_copy_report_flags_partial_exports_missing_columns_and_undated_copies():
    rows: list[dict[str, object]] = [
        {
            "Project Name": f"P{i}",
            "Customer Name": "C",
            "Connection Site": "S",
            "MW Increase / Decrease": "1",
            "MW Effective From": "2027-10-30",
        }
        for i in range(50)
    ]
    ok = tr.copy_report(date(2023, 11, 24), rows, entry(), previous_rows=48)
    assert ok["flags"] == [] and ok["rows"] == 50 and ok["row_count_change"] == "0.042"
    partial = tr.copy_report(date(2023, 11, 28), rows[:20], entry(), previous_rows=50)
    assert partial["flags"] == ["row count fell 60% (possible partial export)"]
    no_customer = tr.copy_report(
        date(2020, 7, 9),
        rows,
        entry(
            columns=[
                "Project Name",
                "Connection Site",
                "MW Increase / Decrease",
                "MW Effective From",
            ]
        ),
        previous_rows=None,
    )
    assert no_customer["flags"] == ["missing columns ['Customer Name']"]
    undated: list[dict[str, object]] = [
        dict(r, **{"MW Effective From": ""}) for r in rows[:30]
    ] + rows[30:]
    assert (
        "more than half of rows undated"
        in tr.copy_report(date(2020, 1, 1), undated, entry(), None)["flags"]
    )
    odd: list[dict[str, object]] = [dict(rows[0], **{"MW Effective From": "TBC"})] + rows[1:]
    assert (
        "1 unparseable date cells" in tr.copy_report(date(2020, 1, 1), odd, entry(), None)["flags"]
    )


def test_schema_report_groups_eras_by_column_vocabulary():
    rows: list[dict[str, object]] = [
        {
            "Project Name": "P",
            "Customer Name": "C",
            "Connection Site": "S",
            "MW Increase / Decrease": "1",
            "MW Effective From": "2027-10-30",
        }
    ]
    v = [
        (
            date(2014, 1, 31),
            rows,
            entry(
                columns=[
                    "Project Name",
                    "Customer Name",
                    "Connection Site",
                    "Mw Increase/Decrease",
                    "TEC Effective from Date",
                ]
            ),
        ),
        (
            date(2014, 2, 13),
            rows,
            entry(
                columns=[
                    "Project Name",
                    "Customer Name",
                    "Connection Site",
                    "Mw Increase/Decrease",
                    "TEC Effective from Date",
                ]
            ),
        ),
        (
            date(2020, 7, 9),
            rows,
            entry(
                columns=[
                    "Project Name",
                    "Connection Site",
                    "MW Increase / Decrease",
                    "MW Effective From",
                ]
            ),
        ),
    ]
    report = tr.schema_report(v, skipped=[{"t_public": "2014-02-24", "error": "x"}])
    assert report["copies"] == 3 and len(report["eras"]) == 2
    assert report["eras"][0]["copies"] == 2 and report["eras"][0]["last"] == "2014-02-13"
    assert report["flagged"] == [
        {"t_public": "2020-07-09", "flags": ["missing columns ['Customer Name']"]}
    ]
    assert report["date_spelling_totals"]["iso-dash"] == 3
    assert report["unparseable"][0]["t_public"] == "2014-02-24"


def test_copy_report_counts_every_spelling_of_project_status():
    """A reader that selects on status is declared against the vocabulary the
    register printed, so the schema report carries it, blanks included."""
    rows: list[dict[str, object]] = [
        {"Project Name": "A", "Project Status": "Built"},
        {"Project Name": "B", "Project Status": " Under  Construction "},
        {"Project Name": "C", "Project Status": "Built"},
        {"Project Name": "D", "Project Status": None},
    ]
    entry: dict = {"columns": ["Project Name", "Project Status"], "sha256": "x", "source": "s"}
    report = tr.copy_report(date(2026, 9, 15), rows, entry, None)
    assert report["project_status"] == {"": 1, "Built": 2, "Under Construction": 1}

    whole = tr.schema_report([(date(2026, 9, 15), rows, entry)], [])
    assert whole["project_status_totals"] == {"Built": 2, "": 1, "Under Construction": 1}
    assert list(whole["project_status_totals"]) == ["Built", "", "Under Construction"]
