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
