"""020 version 1 (amendment 3, f84367c3…): the join at project level."""

from decimal import Decimal

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
