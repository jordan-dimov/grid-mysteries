"""020 version 1 (amendment 3, f84367c3…): the join at project level."""

from decimal import Decimal
from typing import Any

from grid_mysteries.investigations import energisation_v1 as v1


def unit(eid, ng, name, party, gen, demand="0", fuel=None):
    return {
        "elexonBmUnit": eid,
        "nationalGridBmUnit": ng,
        "bmUnitName": name,
        "leadPartyName": party,
        "generationCapacity": gen,
        "demandCapacity": demand,
        "fuelType": fuel,
    }


def filler(n):
    """Units that make *wind* and *limited* common (1 % or more of S1)."""
    return [unit(f"E_F{i}", f"F{i}-1", "Some Wind Farm", "Filler Limited", "1") for i in range(n)]


def project(
    name="carrington power station",
    customer="carrington power ltd",
    site="carrington",
    plant="CCGT",
    mw="910",
    cum=None,
):
    return v1.Project(
        "old|name:x", name, customer, site, plant, Decimal(mw), Decimal(cum) if cum else None
    )


def test_tokens_are_four_characters_or_more_with_a_letter():
    assert v1.tokens("A1 Carrington 2024 CCGT-unit") == {"carrington", "ccgt", "unit"}


def test_a_token_carried_by_one_percent_of_units_never_counts():
    units = filler(199) + [unit("T_X-1", "X-1", "Rare Wind", "Rare Co", "50")]
    common = v1.common_tokens(units)
    assert "wind" in common and "farm" in common and "rare" not in common
    only_wind = project(
        name="big wind", customer="nobody", site="nowhere", plant="Wind Onshore", mw="1"
    )
    assert v1.candidates(only_wind, units, common) == []


def test_a_unit_candidate_needs_a_counted_token_and_capacity_within_25_percent():
    units = [
        unit("T_CARR-1", "CARR-1", "Carrington Power Ltd - Unit 1", "Carrington Power Ltd", "800"),
        unit("T_CARR-9", "CARR-9", "Carrington Power Ltd - Unit 9", "Carrington Power Ltd", "600"),
    ]
    found = v1.candidates(project(), units, frozenset())
    assert [c["units"] for c in found if c["kind"] == "unit"] == [["T_CARR-1"]]


def test_cumulative_mw_also_qualifies_a_unit():
    units = [unit("T_A-1", "A-1", "Alpha Station", "Alpha Co", "100")]
    assert v1.candidates(project(name="alpha station", mw="20", cum="110"), units, frozenset())
    assert not v1.candidates(project(name="alpha station", mw="20"), units, frozenset())


def test_a_project_split_across_units_is_a_set_candidate_by_stem():
    units = [
        unit(
            "T_CARR-1",
            "CARR-1",
            "Carrington Power Ltd - Unit 1",
            "Carrington Power Ltd",
            "470",
            fuel="CCGT",
        ),
        unit(
            "T_CARR-2",
            "CARR-2",
            "Carrington Power Ltd - Unit 2",
            "Carrington Power Ltd",
            "470",
            fuel="CCGT",
        ),
    ]
    found = v1.candidates(project(), units, frozenset())
    assert [(c["kind"], c["units"], c["capacity_mw"]) for c in found] == [
        ("set", ["T_CARR-1", "T_CARR-2"], "940")
    ]
    assert found[0]["fuel"] == "match" and found[0]["exact"] is False
    assert v1.stem("CARR-12") == "CARR" and v1.stem("WLNYO3") == "WLNYO"


def test_storage_capacity_may_be_the_demand_capacity():
    units = [unit("E_BESS-1", "BESS-1", "Coalburn Battery", "Alcemi", "5", demand="-49.9")]
    store = project(
        name="coalburn battery",
        customer="alcemi",
        site="coalburn",
        plant="Energy Storage System",
        mw="50",
    )
    gen = project(
        name="coalburn battery", customer="alcemi", site="coalburn", plant="Wind Onshore", mw="50"
    )
    assert [c["capacity_mw"] for c in v1.candidates(store, units, frozenset())] == ["49.9"]
    assert v1.candidates(gen, units, frozenset()) == []


def test_exact_needs_the_name_capacity_within_5_percent_and_fuel():
    units = [unit("T_K-1", "K-1", "Kype Muir", "Banks", "88", fuel="WIND")]
    kype = project(
        name="kype muir", customer="banks renewables", site="kype", plant="Wind Onshore", mw="88.4"
    )
    assert v1.candidates(kype, units, frozenset())[0]["exact"] is True
    kype_far = project(
        name="kype muir", customer="banks", site="kype", plant="Wind Onshore", mw="100"
    )
    assert v1.candidates(kype_far, units, frozenset())[0]["exact"] is False
    no_fuel = [unit("T_K-1", "K-1", "Kype Muir", "Banks", "88")]
    assert v1.candidates(kype, no_fuel, frozenset())[0]["fuel"] == "unknown"


def test_candidates_order_by_tokens_shared_then_capacity_ratio():
    units = [
        unit("T_B-1", "B-1", "Glen Station", "Other", "120"),
        unit("T_A-1", "A-1", "Glen Station", "Glen Owner", "100"),
        unit("T_C-1", "C-1", "Glen Station", "Other", "101"),
    ]
    glen = project(name="glen station", customer="glen owner", site="x", plant="CCGT", mw="100")
    assert [c["units"][0] for c in v1.candidates(glen, units, frozenset())] == [
        "T_A-1",
        "T_C-1",
        "T_B-1",
    ]


def test_plant_families():
    assert v1.family("Wind Offshore") == "offshore wind"
    assert v1.family("CCGT (Combined Cycle Gas Turbine)") == "thermal"
    assert v1.family("Energy Storage System;Reactive Compensation") == "storage"
    assert v1.family("Demand;Energy Storage System") == "storage"
    assert v1.family("Energy Storage System; Wind Onshore") == "hybrid"
    assert v1.family("PV Array (Photo Voltaic/solar)") == "solar"
    assert v1.family("HYBRID") == "hybrid"
    assert v1.family("Pump Storage") == "other"


def test_j3_embedded_from_agreement_type():
    assert v1.embedded(["Embedded", "BEGA"]) is True
    assert v1.embedded(["Embedded", "Directly Connected"]) is False
    assert v1.embedded(["", "Null"]) is None
    assert v1.embedded(["Embedded", ""]) is False


def test_project_text_is_the_keys_triple():
    p = v1.project_from_key("old|name:a b|c d|e f", "CCGT", Decimal(1), None)
    assert (p.name, p.customer, p.site) == ("a b", "c d", "e f")


def test_wilson_interval():
    assert v1.wilson(0, 0) is None
    interval = v1.wilson(5, 10)
    assert interval is not None
    low, high = interval
    assert low == Decimal("0.237") and high == Decimal("0.763")


# ------------------------------------------------------------- B4 and B5

import json  # noqa: E402
import random  # noqa: E402
from datetime import date  # noqa: E402


def test_windows_walk_back_seven_days_and_stop_at_the_floor():
    found = list(v1.windows_back(date(2015, 1, 20), floor=date(2015, 1, 1)))
    assert found == [
        (date(2015, 1, 14), date(2015, 1, 20)),
        (date(2015, 1, 7), date(2015, 1, 13)),
        (date(2015, 1, 1), date(2015, 1, 6)),
    ]


def rec(unit="T_A-1", day="2020-01-01", q="1.5", run="SF"):
    return {
        "dataset": "B1610",
        "psrType": "Wind Onshore",
        "bmUnit": unit,
        "settlementDate": day,
        "settlementPeriod": 1,
        "halfHourEndTime": f"{day}T00:30:00Z",
        "settlementRunType": run,
        "quantity": q,
    }


def test_format_check_before_any_value_is_read():
    good = json.dumps([rec()]).encode()
    assert v1.format_check(good, {"T_A-1"}) == []
    assert v1.format_check(json.dumps({"data": [rec()]}).encode(), {"T_A-1"}) == []
    assert v1.format_check(b"\xef\xbb\xbf" + good, {"T_A-1"})[0] == "byte-order mark"
    missing = rec()
    del missing["quantity"]
    assert "lacks" in v1.format_check(json.dumps([missing]).encode(), {"T_A-1"})[0]
    assert "not requested" in v1.format_check(good, {"T_B-1"})[0]
    assert "not UTF-8 JSON" in v1.format_check(b"<html>", {"T_A-1"})[0]


def test_proxy_is_the_earliest_positive_day_over_every_run_type():
    windows = [
        [rec(day="2020-01-03", q="0"), rec(day="2020-01-04", q="2", run="II")],
        [
            rec(day="2020-01-01", q="0"),
            rec(day="2020-01-02", q="-1"),
            rec(day="2020-01-03", q="0.1", run="RF"),
        ],
    ]
    assert v1.proxy(windows) == (date(2020, 1, 3), "RF")
    assert v1.proxy([[rec(q="0")]]) is None


def test_labels_partition_the_projects():
    walk = v1.Walk(10, True, False, (date(2020, 1, 1), "SF"))
    assert v1.label(True, "directly-connected", True, walk) == "metered"
    assert (
        v1.label(True, "", True, v1.Walk(600, True, True, (date(2015, 1, 1), "SF")))
        == "metered-before-the-walk"
    )
    assert v1.label(True, "", True, v1.Walk(9, True, False, None)) == "registered-not-metered"
    assert v1.label(True, "", True, v1.Walk(600, False, False, None)) == "no-metered-record"
    assert v1.label(False, "embedded-or-distribution", True, None) == "embedded-or-distribution"
    assert v1.label(False, "directly-connected", True, None) == "unmatched"
    assert v1.label(False, "not-determinable", False, None) == "no-candidate"


def test_distribution_shares_and_the_median_interval():
    values = [Decimal(x) for x in ("-1", "0", "3", "6.0", "7", "12")]
    d = v1.distribution(values, random.Random(v1.SEED))
    assert (d["before"]["k"], d["within_six_months"]["k"], d["later"]["k"]) == (1, 3, 2)
    lo, hi = (Decimal(x) for x in d["median_ci95"])
    assert lo <= d["median"] <= hi
    small = v1.distribution(values[:4], random.Random(v1.SEED))
    assert small["median_ci95"] is None and small["median_ci95_note"] == "n < 5, no interval"


# ------------------------------------------------------------- amendment 4


def test_a2_effective_floor_and_censoring():
    walks = {
        "a": [{"from": "2019-02-05", "records": 3}, {"from": "2019-01-29", "records": 5}],
        "b": [{"from": "2021-03-01", "records": 2}, {"from": "2021-02-22", "records": 0}],
    }
    floor = v1.effective_floor(walks)
    assert floor == date(2019, 1, 29)
    assert v1.censored(walks["a"], floor) is True
    assert v1.censored(walks["b"], floor) is False
    assert v1.censored([{"from": "2020-01-01", "records": 0}], floor) is False


def test_a3_second_sightings_keep_the_earlier_project():
    admitted = [
        ("old|gh", date(2018, 12, 6), ("E_GOSHS-1",)),
        ("old|gh2", date(2020, 10, 22), ("E_GOSHS-1",)),
        ("old|x", date(2020, 10, 22), ("E_X-1",)),
    ]
    assert v1.second_sightings(admitted) == {"old|gh2": "old|gh"}


def test_a1_first_appearance_spans_regimes_with_the_combined_gap():
    seen_first = {
        "old|p": ("old", "p", date(2020, 1, 10)),
        "new|p": ("new", "p", date(2026, 5, 19)),
        "new|q": ("new", "q", date(2026, 5, 19)),
    }
    kept = [date(2020, 1, 3), date(2020, 1, 10), date(2025, 7, 22), date(2026, 5, 19)]
    out = v1.first_appearances(seen_first, kept)
    assert out["new|p"] == (date(2020, 1, 10), 7)
    assert out["new|q"] == (date(2026, 5, 19), 301)


# ---- amendment 5 -------------------------------------------------------------


def test_carry_over_keeps_admissions_still_proposed_and_refusals_with_the_same_candidates():
    from grid_mysteries.investigations import energisation_v1 as v1

    earlier: dict[str, dict[str, Any]] = {
        "k1": {"decision": "admitted", "units": ["T_A-1"]},
        "k2": {"decision": "refused", "units": None},
        "k3": {"decision": "admitted", "units": ["T_C-1"]},
        "k4": {"decision": "refused", "units": None},
    }
    earlier_candidates = {
        "k1": [["T_A-1"]],
        "k2": [["T_B-1"]],
        "k3": [["T_C-1"]],
        "k4": [["T_D-1"]],
    }
    now = {
        "k1": [["T_A-1"], ["T_A-2"]],  # still proposed: carried
        "k2": [["T_B-1"]],  # same candidates: refusal carried
        "k3": [["T_X-1"]],  # admitted units no longer proposed: pre-screen
        "k4": [["T_D-1"], ["T_D-2"]],  # refusal with a changed candidate set: pre-screen
        "k5": [["T_E-1"]],  # new key: pre-screen
        "k6": [],  # no candidate: nothing to decide
    }
    carried, prescreen = v1.carry_over(earlier, earlier_candidates, now)
    assert set(carried) == {"k1", "k2"} and all(
        c["carried_from_amendment_4"] for c in carried.values()
    )
    assert carried["k1"]["units"] == ["T_A-1"]
    assert prescreen == ["k3", "k4", "k5"]


def test_f5_fires_when_a_year_median_leaves_its_earlier_interval():
    from decimal import Decimal

    from grid_mysteries.investigations import energisation_v1 as v1

    before = {
        "year 2025": {"median": "7.1", "median_ci95": ["2.0", "13.1"], "n": 15},
        "year 2026": {"median": "8.1", "median_ci95": ["4.2", "9.8"], "n": 9},
    }
    inside = {
        "year 2025": {"median": "3.0", "median_ci95": ["1.0", "5.0"], "n": 40},
        "year 2026": {"median": "4.2", "median_ci95": ["2.0", "6.0"], "n": 30},
    }
    assert v1.f5_fires(before, inside)["fires"] is False
    outside = {
        "year 2025": {"median": "1.9", "median_ci95": ["1.0", "3.0"], "n": 40},
        "year 2026": {"median": "5.0", "median_ci95": None, "n": 3},
    }
    r = v1.f5_fires(before, outside)
    assert (
        r["fires"] is True
        and r["years"]["2025"]["outside"] is True
        and r["years"]["2026"]["outside"] is False
    )
    assert (
        v1.f5_fires(before, {})["fires"] is False
        and v1.f5_fires(before, {})["years"]["2025"]["outside"] is None
    )
    assert Decimal(v1.F6_TOLERANCE) == Decimal("1.0")


def test_f6_fires_when_the_overall_delay_median_moves_more_than_a_month():
    from grid_mysteries.investigations import energisation_v1 as v1

    assert v1.f6_fires({"median": "4.1"}, {"median": "5.1"})["fires"] is False
    assert v1.f6_fires({"median": "4.1"}, {"median": "5.2"})["fires"] is True
    assert v1.f6_fires({"median": "4.1"}, {"median": "2.9"})["fires"] is True
    assert v1.f6_fires({"median": "4.1"}, {})["fires"] is False
