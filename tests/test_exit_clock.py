"""025 (bc052984…): the exit clock's rules."""

from datetime import date
from decimal import Decimal as D

from grid_mysteries.investigations import exit_clock as ec


def row(
    name="Wind A",
    customer="Co Ltd",
    site="Site 400kV",
    stage="",
    mw="100",
    cum="100",
    eff="2027-10-30",
    pid="",
    status="Scoping",
    plant="Energy Storage System",
    number="",
):
    return {
        "Project ID": pid,
        "Project Number": number,
        "Project Name": name,
        "Customer Name": customer,
        "Connection Site": site,
        "Stage": stage,
        "MW Increase / Decrease": mw,
        "Cumulative Total Capacity (MW)": cum,
        "MW Effective From": eff,
        "Project Status": status,
        "Plant Type": plant,
        "Agreement Type": "Directly Connected",
        "HOST TO": "NGET",
        "Gate": "",
    }


# ---------------------------------------------------------------- keys (I2)


def test_key_is_the_project_id_in_the_id_era_and_the_triple_before_it():
    r = row(pid="a0l4L0000005ikt123", name="Wind  A", customer="CO. LTD", site="site 400KV")
    assert ec.row_key(r, date(2021, 11, 26)) == "id:a0l4L0000005ikt"
    assert ec.row_key(r, date(2021, 11, 23)) == "name:wind a|co ltd|site 400kv"
    assert ec.row_key(row(pid=""), date(2022, 1, 1)).startswith("noid:")


def test_keyed_groups_a_chains_stage_rows_under_one_key():
    rows = [row(pid="a0l1", stage="1"), row(pid="a0l1", stage="2"), row(pid="a0l2")]
    k = ec.keyed(rows, date(2024, 1, 1))
    assert sorted(k) == ["id:a0l1", "id:a0l2"] and len(k["id:a0l1"]) == 2


# -------------------------------------------------------- continuity (I5)


def test_a_pair_losing_more_than_half_its_keys_is_a_rekeying():
    c = ec.continuity(
        date(2022, 8, 19), date(2022, 8, 24), {"a", "b", "c", "d"}, {"d", "e", "f", "g"}
    )
    assert c.absent_from_later == 3 and c.new_in_later == 3 and c.absent_share == D("0.75")
    assert c.rekeying
    assert not ec.continuity(date(2022, 1, 1), date(2022, 1, 5), {"a", "b"}, {"a", "c"}).rekeying


# ------------------------------------------------------------ stitch (I4)


def test_stitch_matches_strictest_tier_first_and_records_the_tier():
    vanished = {"name:a": [row(name="A", site="Old Spelling 132 kV")], "name:b": [row(name="B")]}
    appeared = {
        "id:1": [row(name="A", site="Old Spelling 132kV", pid="1")],
        "id:2": [row(name="B", pid="2")],
    }
    st = ec.stitch(vanished, appeared)
    assert st.matched == {"id:1": "name:a", "id:2": "name:b"}
    assert st.tier_of["id:2"] == "all five"
    assert st.tier_of["id:1"] == "name, customer, stage"


def test_stitch_leaves_shared_signatures_to_later_tiers_and_reports_the_rest():
    # Two vanished chains share every feature but cumulative MW with one appeared chain.
    vanished = {
        "name:x1": [row(name="X", cum="50", mw="50")],
        "name:x2": [row(name="X", cum="60", mw="60")],
    }
    appeared = {
        "id:9": [row(name="X", cum="50", mw="50", pid="9")],
        "id:z": [row(name="Z", pid="z")],
    }
    st = ec.stitch(vanished, appeared)
    assert st.matched == {"id:9": "name:x1"}
    assert st.unmatched_old == ["name:x2"] and st.unmatched_new == ["id:z"]


def test_stitch_uses_the_project_number_before_anything_else():
    vanished = {
        "id:old": [row(name="Renamed Entirely", customer="Seller", pid="old", number="PRO-1")]
    }
    appeared = {
        "id:new": [
            row(name="Brand New Name", customer="Buyer", pid="new", number="PRO-1", cum="7", mw="7")
        ]
    }
    st = ec.stitch(vanished, appeared)
    assert st.matched == {"id:new": "id:old"} and st.tier_of["id:new"] == "project number"


def test_a_two_stage_chain_never_matches_a_one_stage_chain():
    vanished = {
        "name:a": [row(name="A", stage="1", cum="100"), row(name="A", stage="2", cum="200")]
    }
    appeared = {"id:1": [row(name="A", stage="1", cum="100", pid="1")]}
    st = ec.stitch(vanished, appeared)
    assert st.matched == {} and st.unmatched_old == ["name:a"] and st.unmatched_new == ["id:1"]


# -------------------------------------------------------------- clock (K1)


def test_trigger_is_1_april_three_financial_years_before_the_charging_financial_year():
    cases = [
        (date(2027, 10, 1), date(2024, 4, 1)),  # FY 2027/28 -> 1 April 2024
        (date(2028, 3, 31), date(2024, 4, 1)),  # still FY 2027/28
        (date(2028, 4, 1), date(2025, 4, 1)),  # FY 2028/29
        (date(2024, 1, 10), date(2020, 4, 1)),  # FY 2023/24
    ]
    for connection, trigger in cases:
        assert ec.trigger_date(connection) == trigger


def test_whole_months_between():
    assert ec.months_between(date(2024, 4, 1), date(2026, 4, 1)) == 24
    assert ec.months_between(date(2024, 4, 15), date(2026, 4, 1)) == 23
    assert ec.months_between(date(2026, 4, 1), date(2024, 4, 1)) == -24


# -------------------------------------------------------------- bands (K3)


def test_band_boundaries_around_a_1_april_2024_trigger():
    cases = [
        (date(2022, 3, 31), "more than 24 months before"),
        (date(2022, 4, 1), "more than 24 months before"),
        (date(2022, 4, 2), "12 to 24 months before"),
        (date(2023, 4, 1), "12 to 24 months before"),
        (date(2023, 4, 2), "0 to 12 months before"),
        (date(2024, 3, 31), "0 to 12 months before"),
        (date(2024, 4, 1), "0 to 12 months after"),
        (date(2025, 3, 31), "0 to 12 months after"),
        (date(2025, 4, 1), "more than 12 months after"),
    ]
    for at, band in cases:
        assert ec.band(at, date(2024, 4, 1)) == band


def test_no_connection_date_is_its_own_band():
    assert ec.band(date(2024, 1, 1), None) == ec.UNDATED


# ------------------------------------------------------------- strata (S1)


def test_plant_family_reads_storage_only_mixed_other_and_blank():
    assert ec.plant_family("Energy Storage System") == "storage-only"
    assert ec.plant_family("Battery Storage") == "storage-only"
    assert (
        ec.plant_family("Energy Storage System;PV Array (Photo Voltaic/solar)") == "storage-mixed"
    )
    assert ec.plant_family("Energy Storage System; Reactive Compensation") == "storage-mixed"
    assert ec.plant_family("Wind Onshore") == "other"
    assert ec.plant_family("") == "blank"


def test_agreement_and_status_families_follow_the_printed_vocabularies():
    assert (
        ec.agreement_family("Direct Connection")
        == ec.agreement_family("BCA")
        == "directly connected"
    )
    assert ec.agreement_family("Embedded") == ec.agreement_family("BEGA") == "embedded"
    assert ec.agreement_family("Null") == ec.agreement_family("") == "blank"
    assert ec.status_family("Consented") == "Consents Approved"
    assert (
        ec.status_family("Under Construction/Commissioning") == "Under Construction/Commissioning"
    )
    assert ec.status_family("Terminated") == "Terminated"
    assert ec.is_built("Built") and not ec.is_built("Scoping")


# ---------------------------------------------------------- sighting (I1)


def test_sighting_takes_the_earliest_date_the_summed_mw_and_the_largest_cumulative():
    rows = [
        row(stage="1", mw="50", cum="50", eff="2028-10-01"),
        row(stage="2", mw="70", cum="120", eff="2027-04-01"),
    ]
    s = ec.sighting(date(2024, 1, 5), "ab" * 32, "id:1", rows, swapped=False)
    assert s.rows == 2 and s.stage_mw == D("120") and s.cumulative_mw == D("120")
    assert s.connection == date(2027, 4, 1)
    swapped = ec.sighting(
        date(2024, 1, 5), "ab" * 32, "id:1", [row(eff="2027-10-05")], swapped=True
    )
    assert swapped.connection == date(2027, 5, 10)


# ------------------------------------------------------- classes (E1 to E3)


def test_classify_exit_open_completed_present_and_not_determinable():
    end = date(2026, 10, 20)
    assert (
        ec.classify(date(2026, 7, 17), "Scoping", series_end=end, not_determinable=False) == ec.EXIT
    )
    assert (
        ec.classify(date(2026, 7, 18), "Scoping", series_end=end, not_determinable=False) == ec.OPEN
    )
    assert (
        ec.classify(date(2026, 1, 1), "Built", series_end=end, not_determinable=False)
        == ec.COMPLETED
    )
    assert ec.classify(end, "Scoping", series_end=end, not_determinable=False) == ec.PRESENT
    assert (
        ec.classify(date(2022, 8, 19), "Scoping", series_end=end, not_determinable=True)
        == ec.NOT_DETERMINABLE
    )


def test_exit_copy_is_the_first_kept_copy_after_the_last_sighting_and_months_span_inclusive():
    copies = [date(2024, 1, 5), date(2024, 1, 9), date(2024, 1, 12)]
    assert ec.exit_copy(date(2024, 1, 9), copies) == date(2024, 1, 12)
    assert ec.months_in(date(2023, 11, 15), date(2024, 2, 2)) == [
        date(2023, 11, 1),
        date(2023, 12, 1),
        date(2024, 1, 1),
        date(2024, 2, 1),
    ]
    assert ec.regime_of(date(2025, 11, 28)) == "old" and ec.regime_of(date(2025, 12, 1)) == "new"


# ------------------------------------------------------------- hazard (K5)


def test_byar_interval_brackets_the_hazard_and_is_zero_floored():
    ten = ec.byar_interval(10, D(1000))
    none = ec.byar_interval(0, D(500))
    assert ten is not None and none is not None
    h, lo, hi = ten
    assert h == D("0.01") and lo < h < hi
    h0, lo0, hi0 = none
    assert h0 == 0 and lo0 == 0 and hi0 > 0
    assert ec.byar_interval(3, D(0)) is None


def test_flatness_is_a_shared_value_across_every_bands_interval():
    a = (D("0.010"), D("0.005"), D("0.015"))
    b = (D("0.012"), D("0.008"), D("0.018"))
    c = (D("0.030"), D("0.020"), D("0.040"))
    assert ec.flat([a, b]) is True
    assert ec.flat([a, b, c]) is False
    assert ec.flat([a, None]) is None


# ------------------------------------------------------------ joins (J1, J2)


def test_place_tokens_drop_stop_words_short_words_and_numbers():
    assert ec.place_tokens("Fiddlers Ferry BESS 275kV Substation") == {"fiddlers", "ferry", "275kv"}
    assert ec.place_tokens("Station Road, Fiddlers Ferry - Battery Energy Storage") == {
        "fiddlers",
        "ferry",
    }
    assert ec.within_one_mw(D("49.9"), D("50")) and not ec.within_one_mw(D("48"), D("50"))
    assert not ec.within_one_mw(None, D("50"))


# ------------------------------------------------- admissible rows (I10)


def test_a_row_printing_a_name_alone_is_refused():
    assert not ec.admissible({"Project Name": "Confidential Information - Do Not Distribute"})
    assert not ec.admissible({"Project Name": "x", "Customer Name": "  ", "Plant Type": None})


def test_a_row_printing_a_name_and_one_other_field_is_admitted():
    assert ec.admissible({"Project Name": "A", "Customer Name": "B"})
    assert ec.admissible({"Project Name": "A", "MW Effective From": "2027-10-01"})
    assert ec.fields_printed({"Project Name": "A", "HOST TO": "NGET", "Stage": "1"}) == (
        "HOST TO",
        "Stage",
    )


def test_a_row_printing_no_name_is_refused():
    assert not ec.admissible({"Customer Name": "B", "Project Status": "Scoping", "HOST TO": "NGET"})
    assert not ec.admissible({})


def test_admit_keeps_printed_order_and_counts_the_refused():
    rows: list[dict[str, object]] = [
        {"Project Name": "A", "Customer Name": "B"},
        {"Project Name": "footer"},
        {"Project Name": "C", "Project Status": "Built", "HOST TO": "SPT"},
    ]
    admitted, refused = ec.admit(rows)
    assert [r["Project Name"] for r in admitted] == ["A", "C"] and refused == 1
    assert len(rows) == 3
