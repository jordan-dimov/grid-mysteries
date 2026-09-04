from datetime import UTC, date, datetime, timedelta
from decimal import Decimal as D
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from grid_mysteries.investigations import eligibility_screen as es
from grid_mysteries.investigations.eligibility_screen import (
    LONDON,
    PNRecord,
    Position,
    concentration,
    contiguous_runs,
    fpn_status,
    infer_timestamp_basis,
    milestone,
    period_of,
    period_start_utc,
    periods_in_day,
    pn_from_record,
    positions_from_eac_rows,
    response_family,
    screen,
    window_periods,
)

AUG_4 = date(2026, 8, 4)


# --------------------------------------------------------------------------
# Settlement-period arithmetic


def test_period_counts_follow_the_clock_changes() -> None:
    assert periods_in_day(date(2026, 3, 29)) == 46  # clocks forward
    assert periods_in_day(date(2026, 10, 25)) == 50  # clocks back
    assert periods_in_day(AUG_4) == 48


def test_period_one_starts_at_local_midnight_and_period_of_inverts_it() -> None:
    start = period_start_utc(AUG_4, 1)
    assert start == datetime(2026, 8, 3, 23, 0, tzinfo=UTC)  # BST
    assert period_of(start) == ("2026-08-04", 1)
    assert period_of(start + timedelta(minutes=29)) == ("2026-08-04", 1)
    assert period_of(start + timedelta(minutes=30)) == ("2026-08-04", 2)
    assert period_of(period_start_utc(AUG_4, 48)) == ("2026-08-04", 48)
    with pytest.raises(ValueError):
        period_start_utc(AUG_4, 49)
    with pytest.raises(ValueError):
        period_of(datetime(2026, 8, 4, 0, 0))


def test_window_periods_spans_inclusive_days_in_order() -> None:
    periods = window_periods(date(2026, 8, 30), date(2026, 8, 31))
    assert len(periods) == 96
    assert periods[0] == ("2026-08-30", 1)
    assert periods[-1] == ("2026-08-31", 48)


# --------------------------------------------------------------------------
# Timestamp basis


def test_basis_is_utc_when_starts_sit_on_efa_boundaries_read_as_utc() -> None:
    # EFA 1 of a BST day starts at 23:00 local = 22:00Z.
    starts = [datetime(2026, 8, 3, 22, 0), datetime(2026, 8, 4, 2, 0), datetime(2026, 8, 4, 6, 0)]
    out = infer_timestamp_basis(starts)
    assert out["basis"] == "utc"
    assert out["on_efa_boundary"] == {"utc": 3, "local": 0}


def test_basis_is_local_when_starts_read_as_clock_time() -> None:
    starts = [datetime(2026, 8, 3, 23, 0), datetime(2026, 8, 4, 3, 0)]
    assert infer_timestamp_basis(starts)["basis"] == "local"


def test_basis_is_undetermined_in_winter_or_without_rows() -> None:
    # In GMT the two readings coincide, so nothing can be inferred.
    assert infer_timestamp_basis([datetime(2026, 1, 5, 23, 0)])["basis"] == "undetermined"
    assert infer_timestamp_basis([])["basis"] == "no-rows"
    aware = [datetime(2026, 8, 3, 22, 0, tzinfo=UTC)]
    assert infer_timestamp_basis(aware)["basis"] == "undetermined"


# --------------------------------------------------------------------------
# FPN status


def pn(unit: str, period: int, start_min: int, end_min: int, level=D(0)) -> PNRecord:
    base = period_start_utc(AUG_4, period)
    return PNRecord(
        unit=unit,
        settlement_date="2026-08-04",
        period=period,
        time_from=base + timedelta(minutes=start_min),
        time_to=base + timedelta(minutes=end_min),
        level_from=level,
        level_to=level,
    )


def bounds(period: int) -> tuple[datetime, datetime]:
    start = period_start_utc(AUG_4, period)
    return start, start + timedelta(minutes=30)


def test_absent_zero_partial_and_split_pns_are_distinguished() -> None:
    assert fpn_status([], *bounds(10)) == {"present": False, "covering": False, "non_zero": False}
    zero = fpn_status([pn("U", 10, 0, 30)], *bounds(10))
    assert zero == {"present": True, "covering": True, "non_zero": False}
    partial = fpn_status([pn("U", 10, 0, 15)], *bounds(10))
    assert partial == {"present": True, "covering": False, "non_zero": False}
    gap = fpn_status([pn("U", 10, 0, 10), pn("U", 10, 20, 30)], *bounds(10))
    assert gap["present"] and not gap["covering"]
    split = fpn_status([pn("U", 10, 15, 30, D(5)), pn("U", 10, 0, 15)], *bounds(10))
    assert split == {"present": True, "covering": True, "non_zero": True}


def test_a_record_that_overhangs_the_period_still_covers_it() -> None:
    # A stream record for a longer level segment, attributed to this period.
    assert fpn_status([pn("U", 10, -30, 60, D(-3))], *bounds(10))["covering"] is True


def test_pn_from_record_reads_the_insights_fields_and_z_timestamps() -> None:
    rec = pn_from_record(
        {
            "bmUnit": "2__ABATT001",
            "nationalGridBmUnit": "BATT-1",
            "settlementDate": "2026-08-04",
            "settlementPeriod": 10,
            "timeFrom": "2026-08-04T03:30:00Z",
            "timeTo": "2026-08-04T04:00:00Z",
            "levelFrom": 12.5,
            "levelTo": "12.5",
        }
    )
    assert rec.unit == "2__ABATT001"
    assert rec.time_from == datetime(2026, 8, 4, 3, 30, tzinfo=UTC)
    assert rec.level_from == D("12.5") == rec.level_to


# --------------------------------------------------------------------------
# Positions


def test_response_family_reads_the_dataset_vocabulary_not_a_guess() -> None:
    assert response_family("Dynamic Containment", "DCL") == "DC"
    assert response_family("DMH") == "DM"
    assert response_family("dr-l") == "DR"
    assert response_family("Quick Reserve", "QR") is None
    assert response_family("DRIVER") is None  # 'DR' followed by a non-H/L letter


def eac_row(**overrides):
    row = {
        "auctionUnit": "BATT-1",
        "serviceType": "Dynamic Containment",
        "auctionProduct": "DCL",
        "executedQuantity": "10",
        "clearingPrice": "1.23",
        "deliveryStart": "2026-08-04T06:00:00",  # EFA 3, 07:00 local, as UTC
        "deliveryEnd": "2026-08-04T10:00:00",
        "technologyType": "Batteries",
    }
    row.update(overrides)
    return row


UNIT_MAP = {"BATT-1": "2__ABATT001", "BATT-2": "2__ABATT002"}


def test_positions_map_units_and_count_every_reason_for_skipping() -> None:
    rows = [
        eac_row(),
        eac_row(executedQuantity="0"),
        eac_row(serviceType="Quick Reserve", auctionProduct="QR"),
        eac_row(auctionUnit="NOTABATT"),
        eac_row(deliveryEnd="2026-08-04T06:10:00"),
    ]
    out = positions_from_eac_rows(rows, unit_map=UNIT_MAP, basis="utc")
    (pos,) = out["positions"]
    assert pos.unit == "2__ABATT001" and pos.family == "DC"
    assert pos.mw == D(10) and pos.price_gbp_per_mw_h == D("1.23")
    assert pos.periods() == [("2026-08-04", p) for p in range(15, 23)]
    assert out["unmapped_units"] == ["NOTABATT"]
    assert out["skipped"] == {
        "zero_quantity": 1,
        "not_response": 1,
        "unmapped": 1,
        "bad_interval": 1,
    }
    assert out["service_vocabulary"] == {
        "Dynamic Containment|DCL": "DC",
        "Quick Reserve|QR": None,
    }


def test_local_basis_shifts_the_delivery_interval() -> None:
    out = positions_from_eac_rows(
        [eac_row(deliveryStart="2026-08-04T07:00:00", deliveryEnd="2026-08-04T11:00:00")],
        unit_map=UNIT_MAP,
        basis="local",
    )
    assert out["positions"][0].periods()[0] == ("2026-08-04", 15)


# --------------------------------------------------------------------------
# The screen


def block_position(unit: str, mw="10", price="1.23", family="DC") -> Position:
    return Position(
        unit=unit,
        service="Dynamic Containment",
        product="DCL",
        family=family,
        delivery_start=datetime(2026, 8, 4, 6, 0, tzinfo=UTC),
        delivery_end=datetime(2026, 8, 4, 10, 0, tzinfo=UTC),
        mw=D(mw),
        price_gbp_per_mw_h=D(price),
    )


REQUEST = {
    "window": {"from": "2026-08-04", "to": "2026-08-04"},
    "units": ["2__ABATT001", "2__ABATT002"],
    "validity_rule": "covering",
    "forfeit_scope": "period",
}


def full_day(unit: str, *, skip=(), level=D(0)) -> list[PNRecord]:
    return [pn(unit, p, 0, 30, level) for p in range(1, 49) if p not in skip]


def test_screen_deems_periods_unavailable_and_prices_them_in_decimal() -> None:
    records = full_day("2__ABATT001") + full_day("2__ABATT002", skip={16, 17})
    result = screen(
        REQUEST, records, [block_position("2__ABATT001"), block_position("2__ABATT002")]
    )

    a, b = result["units"]["2__ABATT001"], result["units"]["2__ABATT002"]
    assert a["periods_held"] == b["periods_held"] == 8
    assert a["revenue_held_gbp"] == "49.20"  # 10 MW × £1.23 × 0.5 h × 8
    assert a["primary"]["periods_deemed_unavailable"] == 0
    assert a["primary"]["revenue_at_stake_gbp"] == "0.00"
    assert b["primary"]["periods_deemed_unavailable"] == 2
    assert b["primary"]["share_of_held_periods"] == "0.2500"
    assert b["primary"]["revenue_at_stake_gbp"] == "12.30"  # 2 × 6.15, exact
    assert b["primary"]["runs"] == [2]
    assert b["by_rule"]["covering"]["revenue_at_stake_gbp"] == {"period": "12.30", "block": "49.20"}
    assert [p["period"] for p in b["unavailable_periods"]] == [16, 17]
    assert b["unavailable_periods"][0]["fpn"] == {
        "present": False,
        "covering": False,
        "non_zero": False,
    }
    totals = result["totals"]
    assert totals["units_holding"] == 2
    assert totals["units_with_any_unavailable"] == 1
    assert totals["periods_at_risk"] == 2
    assert totals["revenue_held_gbp"] == "98.40"
    assert totals["revenue_at_stake_gbp"] == "12.30"
    assert totals["share_of_revenue_held"] == "0.1250"
    assert result["window"]["periods"] == 48
    assert result["rule"] == es.RULE


def test_every_rule_and_scope_is_computed_whatever_the_primary() -> None:
    # Zero-level PNs everywhere: 'present' and 'covering' pass, 'non_zero' fails.
    result = screen(REQUEST, full_day("2__ABATT001"), [block_position("2__ABATT001")])
    by_rule = result["totals"]["by_rule"]
    assert by_rule["present"]["periods_at_risk"] == 0
    assert by_rule["covering"]["periods_at_risk"] == 0
    assert by_rule["non_zero"]["periods_at_risk"] == 8
    assert by_rule["non_zero"]["revenue_at_stake_gbp"] == {"period": "49.20", "block": "49.20"}
    stricter = screen(
        {**REQUEST, "validity_rule": "non_zero", "forfeit_scope": "block"},
        full_day("2__ABATT001"),
        [block_position("2__ABATT001")],
    )
    assert stricter["totals"]["revenue_at_stake_gbp"] == "49.20"
    assert stricter["request"]["validity_rule"] == "non_zero"


def test_the_population_already_complying_is_a_zero_result_not_an_error() -> None:
    result = screen(REQUEST, full_day("2__ABATT001", level=D(5)), [block_position("2__ABATT001")])
    assert result["totals"]["units_with_any_unavailable"] == 0
    assert result["totals"]["by_rule"]["non_zero"]["periods_at_risk"] == 0


def test_units_outside_the_population_and_periods_outside_the_window_are_ignored() -> None:
    outside = Position(
        unit="2__ABATT001",
        service="Dynamic Containment",
        product="DCL",
        family="DC",
        delivery_start=datetime(2026, 8, 5, 6, 0, tzinfo=UTC),
        delivery_end=datetime(2026, 8, 5, 10, 0, tzinfo=UTC),
        mw=D(10),
        price_gbp_per_mw_h=D(1),
    )
    result = screen(REQUEST, [], [block_position("2__OTHER"), outside])
    assert result["units"] == {}
    assert result["totals"]["units_holding"] == 0
    assert result["totals"]["share_of_revenue_held"] is None


def test_overlapping_services_in_one_period_count_once_for_periods_and_add_revenue() -> None:
    dc = block_position("2__ABATT001")
    dm = block_position("2__ABATT001", mw="4", price="2", family="DM")
    result = screen(REQUEST, [], [dc, dm])
    u = result["units"]["2__ABATT001"]
    assert u["periods_held"] == 8
    assert u["primary"]["periods_deemed_unavailable"] == 8
    assert u["revenue_held_gbp"] == "81.20"  # 49.20 + 4 × 2 × 0.5 × 8
    assert u["primary"]["revenue_at_stake_gbp"] == "81.20"
    assert u["unavailable_periods"][0]["families"] == ["DC", "DM"]
    assert u["by_family"]["DM"] == {"periods_held": 8, "revenue_held_gbp": "32.00"}


def test_unknown_rule_or_scope_is_refused() -> None:
    with pytest.raises(ValueError):
        screen({**REQUEST, "validity_rule": "strict"}, [], [])
    with pytest.raises(ValueError):
        screen({**REQUEST, "forfeit_scope": "month"}, [], [])


# --------------------------------------------------------------------------
# Concentration and milestone


def test_contiguous_runs() -> None:
    assert contiguous_runs([]) == []
    assert contiguous_runs([5, 6, 7, 10, 12, 13]) == [3, 1, 2]
    assert contiguous_runs([3, 3, 4]) == [2]


def test_concentration_groups_by_lead_party_largest_exposure_first() -> None:
    records = full_day("2__ABATT001") + full_day("2__ABATT002", skip={16, 17})
    result = screen(
        REQUEST, records, [block_position("2__ABATT001"), block_position("2__ABATT002")]
    )
    parties = concentration(result, {"2__ABATT001": "Alpha Ltd", "2__ABATT002": "Beta Ltd"})
    assert [p["party"] for p in parties] == ["Beta Ltd", "Alpha Ltd"]
    assert parties[0]["revenue_at_stake_gbp"] == "12.30"
    assert parties[0]["share_of_revenue_held"] == "0.2500"
    assert parties[0]["runs"] == [2]
    assert concentration(result, {})[0]["party"] == "unknown"


def test_milestone_bar_needs_one_percent_and_more_than_a_single_short_outage() -> None:
    parties: list[dict[str, Any]] = [
        {"party": "single-outage", "share_of_revenue_held": "0.2500", "runs": [2]},
        {"party": "day-long-outage", "share_of_revenue_held": "0.0100", "runs": [48]},
        {"party": "recurring", "share_of_revenue_held": "0.0100", "runs": [1, 1]},
        {"party": "below-bar", "share_of_revenue_held": "0.0099", "runs": [1, 1]},
        {"party": "no-exposure", "share_of_revenue_held": None, "runs": []},
    ]
    assert [p["party"] for p in milestone(parties)] == ["day-long-outage", "recurring"]
    assert milestone(parties, bar=D("0.02")) == []


# --------------------------------------------------------------------------
# Properties


@settings(max_examples=60, deadline=None)
@given(
    missing=st.sets(st.integers(min_value=15, max_value=22)),
    mw=st.decimals(min_value=D("0.1"), max_value=D("100"), places=1),
    price=st.decimals(min_value=D("0"), max_value=D("50"), places=2),
)
def test_at_stake_never_exceeds_held_and_block_dominates_period(missing, mw, price) -> None:
    unit = "2__ABATT001"
    result = screen(
        {**REQUEST, "units": [unit]},
        full_day(unit, skip=missing),
        [block_position(unit, mw=str(mw), price=str(price))],
    )
    u = result["units"][unit]
    held = D(u["revenue_held_gbp"])
    for rule in es.VALIDITY_RULES:
        period_stake = D(u["by_rule"][rule]["revenue_at_stake_gbp"]["period"])
        block_stake = D(u["by_rule"][rule]["revenue_at_stake_gbp"]["block"])
        assert D(0) <= period_stake <= block_stake <= held
    assert u["primary"]["periods_deemed_unavailable"] == len(missing)
    assert (D(u["primary"]["share_of_held_periods"]) == D(0)) == (not missing)


def test_local_zone_is_europe_london() -> None:
    assert LONDON.key == "Europe/London"
