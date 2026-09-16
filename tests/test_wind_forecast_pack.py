"""016's data pack: the reading rules that turn pinned bytes into flat tables.

The pack asserts no forecast error, so what needs testing is the boundary
behaviour a contributor would otherwise be silently wrong about: the BST
settlement day, the hour-to-period mapping, and the rows the tables refuse
to carry.
"""

from datetime import UTC, date, datetime
from decimal import Decimal as D

import pytest

from grid_mysteries.investigations import wind_forecast_pack as pack

DAY = date(2026, 9, 8)


def test_settlement_day_starts_at_local_midnight_not_utc_midnight():
    assert pack.day_start_utc(DAY) == datetime(2026, 9, 7, 23, 0, tzinfo=UTC)
    assert pack.period_start(DAY, 1) == datetime(2026, 9, 7, 23, 0, tzinfo=UTC)
    assert pack.period_start(DAY, 48) == datetime(2026, 9, 8, 22, 30, tzinfo=UTC)


def test_a_winter_day_starts_at_utc_midnight():
    assert pack.day_start_utc(date(2026, 1, 15)) == datetime(2026, 1, 15, 0, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("day", "periods"),
    [(DAY, 48), (date(2026, 3, 29), 46), (date(2026, 10, 25), 50)],
)
def test_clock_change_days_do_not_have_48_periods(day, periods):
    assert pack.periods_in_day(day) == periods


def test_period_of_matches_elexons_own_mapping_for_the_witnessed_hour():
    """The pinned evolution witness maps 2026-09-08T12:00Z to period 27."""
    assert pack.period_of(DAY, datetime(2026, 9, 8, 12, 0, tzinfo=UTC)) == 27


def test_period_of_rejects_instants_that_are_not_period_boundaries_of_the_day():
    assert pack.period_of(DAY, datetime(2026, 9, 8, 12, 15, tzinfo=UTC)) is None
    assert pack.period_of(DAY, datetime(2026, 9, 8, 22, 30, tzinfo=UTC)) == 48
    # 23:00Z on the 8th is period 1 of the *next* settlement day, not period 49.
    assert pack.period_of(DAY, datetime(2026, 9, 8, 23, 0, tzinfo=UTC)) is None
    assert pack.period_of(DAY, datetime(2026, 9, 7, 22, 30, tzinfo=UTC)) is None


def test_naive_elexon_timestamps_are_read_as_utc():
    assert pack.parse_instant("2026-09-08T00:30:00") == datetime(2026, 9, 8, 0, 30, tzinfo=UTC)
    assert pack.parse_instant("2026-09-08T00:30:00Z") == datetime(2026, 9, 8, 0, 30, tzinfo=UTC)


def windfor(publish, start, mw):
    return {"dataset": "WINDFOR", "publishTime": publish, "startTime": start, "generation": mw}


def test_forecast_issues_keep_the_settlement_day_and_name_the_hour_it_covers():
    rows = pack.forecast_issue_rows(
        [
            windfor("2026-09-07T03:30:00Z", "2026-09-07T23:00:00Z", 10572),
            windfor("2026-09-07T03:30:00Z", "2026-09-08T12:00:00Z", 17944),
            windfor("2026-09-07T03:30:00Z", "2026-09-08T22:00:00Z", 16000),
            windfor("2026-09-07T03:30:00Z", "2026-09-08T23:00:00Z", 15000),
            windfor("2026-09-07T03:30:00Z", "2026-09-07T22:00:00Z", 14000),
        ],
        DAY,
    )
    assert [r["settlement_period"] for r in rows] == [1, 27, 47]
    assert [r["covers_periods"] for r in rows] == ["1-2", "27-28", "47-48"]
    assert rows[1]["forecast_mw"] == D("17944")
    assert rows[0]["target_start_utc"] == "2026-09-07T23:00:00Z"


def test_the_last_hour_of_the_day_covers_only_the_periods_that_exist():
    rows = pack.forecast_issue_rows(
        [windfor("2026-09-07T03:30:00Z", "2026-09-08T22:30:00Z", 16000)], DAY
    )
    assert rows == [] or rows[0]["covers_periods"] == "48"


def test_forecast_mw_is_decimal_never_float():
    rows = pack.forecast_issue_rows(
        [windfor("2026-09-07T03:30:00Z", "2026-09-08T12:00:00Z", 17944)], DAY
    )
    assert isinstance(rows[0]["forecast_mw"], D)


def test_b1440_rows_keep_only_the_target_day_and_sort_by_period():
    rows = pack.b1440_rows(
        [
            {
                "publishTime": "2026-09-07T16:45:11Z",
                "processType": "Day ahead",
                "businessType": "Wind generation",
                "psrType": "Wind Onshore",
                "startTime": "2026-09-08T22:30:00Z",
                "settlementDate": "2026-09-08",
                "settlementPeriod": 48,
                "quantity": 7602.0,
            },
            {
                "publishTime": "2026-09-06T16:45:03Z",
                "processType": "Day ahead",
                "businessType": "Wind generation",
                "psrType": "Wind Offshore",
                "startTime": "2026-09-07T23:00:00Z",
                "settlementDate": "2026-09-08",
                "settlementPeriod": 1,
                "quantity": 13814.0,
            },
            {
                "publishTime": "2026-09-08T16:45:00Z",
                "processType": "Day ahead",
                "businessType": "Solar generation",
                "psrType": "Solar",
                "startTime": "2026-09-09T11:00:00Z",
                "settlementDate": "2026-09-09",
                "settlementPeriod": 25,
                "quantity": 4000.0,
            },
        ],
        DAY,
    )
    assert [r["settlement_period"] for r in rows] == [1, 48]
    # Periods 1-2 fall in the previous clock day, so their "day ahead" issue
    # is a day older than the rest of the settlement day's.
    assert rows[0]["publish_time_utc"] == "2026-09-06T16:45:03Z"
    assert rows[0]["quantity_mw"] == D("13814.0")


def test_fuelinst_keeps_only_wind_rows_of_the_day():
    records = [
        {
            "publishTime": "2026-09-07T23:05:00Z",
            "startTime": "2026-09-07T23:00:00Z",
            "settlementDate": "2026-09-08",
            "settlementPeriod": 1,
            "fuelType": "WIND",
            "generation": 10572,
        },
        {
            "publishTime": "2026-09-07T23:05:00Z",
            "startTime": "2026-09-07T23:00:00Z",
            "settlementDate": "2026-09-08",
            "settlementPeriod": 1,
            "fuelType": "CCGT",
            "generation": 5000,
        },
        {
            "publishTime": "2026-09-07T22:05:00Z",
            "startTime": "2026-09-07T22:00:00Z",
            "settlementDate": "2026-09-07",
            "settlementPeriod": 47,
            "fuelType": "WIND",
            "generation": 9000,
        },
    ]
    rows = pack.fuelinst_wind_rows(records, DAY)
    assert len(rows) == 1
    assert rows[0]["generation_mw"] == D("10572")


def test_pn_segments_are_kept_as_published_and_never_integrated():
    records = [
        {
            "bmUnit": "T_SGRWO-1",
            "nationalGridBmUnit": "SGRWO-1",
            "settlementDate": "2026-09-08",
            "settlementPeriod": 48,
            "timeFrom": "2026-09-08T22:59:00Z",
            "timeTo": "2026-09-08T23:00:00Z",
            "levelFrom": 280,
            "levelTo": 278,
        },
        {
            "bmUnit": "T_SGRWO-1",
            "nationalGridBmUnit": "SGRWO-1",
            "settlementDate": "2026-09-08",
            "settlementPeriod": 48,
            "timeFrom": "2026-09-08T22:30:00Z",
            "timeTo": "2026-09-08T22:59:00Z",
            "levelFrom": 280,
            "levelTo": 280,
        },
    ]
    rows = pack.pn_rows(records, DAY)
    assert [r["time_from_utc"] for r in rows] == [
        "2026-09-08T22:30:00Z",
        "2026-09-08T22:59:00Z",
    ]
    assert rows[0]["level_to_mw"] == D("280")


def test_b1610_rows_read_naive_half_hour_end_times_as_utc():
    rows = pack.b1610_rows(
        [
            {
                "bmUnit": "T_MOWWO-4",
                "nationalGridBmUnitId": "MOWWO-4",
                "settlementDate": "2026-09-08",
                "settlementPeriod": 1,
                "halfHourEndTime": "2026-09-07T23:30:00",
                "settlementRunType": "II",
                "psrType": "Generation",
                "quantity": 0.0,
            }
        ],
        DAY,
    )
    assert rows[0]["half_hour_end_utc"] == "2026-09-07T23:30:00Z"
    assert rows[0]["quantity_mwh"] == D("0.0")


def register_row(**overrides):
    row = {
        "elexonBmUnit": "T_AAAAW-1",
        "nationalGridBmUnit": "AAAAW-1",
        "bmUnitName": "A Wind Farm",
        "leadPartyName": "A Co Ltd",
        "bmUnitType": "T",
        "fuelType": "WIND",
        "generationCapacity": "100.000",
        "gspGroupId": None,
        "eic": None,
    }
    return row | overrides


def test_a_bm_unit_registered_under_two_eics_keeps_both_rows_and_is_reported():
    """T_WLNYO-4 really is in the register twice, once per EIC. Merging the
    rows would hide a register fact; dropping one would lose an identifier.
    Both are kept, and the collision is named so a join can guard against it."""
    first = register_row(elexonBmUnit="T_WLNYO-4", bmUnitName="WALNEY_4", eic="48W00000WLNYO-4-")
    second = register_row(elexonBmUnit="T_WLNYO-4", bmUnitName="WALNEY_4", eic="48W00001WLNYO-4R")
    rows = pack.wind_register_rows([second, first, register_row()])
    assert [(r["elexonBmUnit"], r["eic"]) for r in rows] == [
        ("T_AAAAW-1", None),
        ("T_WLNYO-4", "48W00000WLNYO-4-"),
        ("T_WLNYO-4", "48W00001WLNYO-4R"),
    ]
    assert pack.duplicate_bm_units(rows) == ["T_WLNYO-4"]
    assert pack.queryable_units(
        pack.wind_unit_rows([second, first], cmis=[], tec=[], bid_paid_by_unit={})
    ) == ["T_WLNYO-4", "T_WLNYO-4"]


def test_rows_without_an_elexon_id_are_kept_but_marked_unqueryable():
    orphan = {"nationalGridBmUnit": "ACHYW-1", "elexonBmUnit": None, "fuelType": "WIND"}
    rows = pack.wind_unit_rows([register_row(), orphan], cmis=[], tec=[], bid_paid_by_unit={})
    assert [r["queryable"] for r in rows] == [True, False]
    assert pack.queryable_units(rows) == ["T_AAAAW-1"]


def test_non_wind_units_never_enter_the_pack():
    rows = pack.wind_unit_rows(
        [register_row(), register_row(elexonBmUnit="T_GAS-1", fuelType="CCGT")],
        cmis=[],
        tec=[],
        bid_paid_by_unit={},
    )
    assert [r["bm_unit"] for r in rows] == ["T_AAAAW-1"]


def test_side_of_b6_is_015s_ladder_applied_unchanged():
    cmis = [{"BMU ID": "T_AAAAW-1", "B6/EC5": "B6"}]
    rows = pack.wind_unit_rows([register_row()], cmis=cmis, tec=[], bid_paid_by_unit={})
    assert (rows[0]["north_of_b6"], rows[0]["side_of_b6"], rows[0]["side_grade"]) == (
        True,
        "north",
        "A",
    )


def test_a_unit_with_no_graded_evidence_is_unknown_not_south():
    rows = pack.wind_unit_rows([register_row()], cmis=[], tec=[], bid_paid_by_unit={})
    assert rows[0]["side_of_b6"] == "unknown"
    assert rows[0]["north_of_b6"] is False
    assert rows[0]["side_grade"] == "-"


def test_015s_bid_cashflow_is_carried_across_verbatim_and_absent_where_it_is_absent():
    rows = pack.wind_unit_rows(
        [register_row(), register_row(elexonBmUnit="T_BBBBW-1", nationalGridBmUnit="BBBBW-1")],
        cmis=[],
        tec=[],
        bid_paid_by_unit={"T_AAAAW-1": "59325.294479360002128492"},
    )
    assert rows[0]["bid_paid_gbp_015"] == "59325.294479360002128492"
    assert rows[1]["bid_paid_gbp_015"] is None
