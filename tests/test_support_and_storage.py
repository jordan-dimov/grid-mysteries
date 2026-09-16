from datetime import UTC, date, datetime
from decimal import Decimal as D

from grid_mysteries.investigations import support_and_storage as ss

READING = {
    "cfd_map_bmu": "BMU_Id",
    "cfd_map_id": "CFD_Id",
    "cfd_map_from": "Effective_From",
    "cfd_map_to": "Effective_date_to",
    "cfd_id": "CFD_ID",
    "cfd_name": "Name_of_CFD_Unit",
    "cfd_technology": "Technology_Type",
    "cfd_capacity": "Maximum_Contract_Capacity_MW",
    "cfd_status": "Status",
    "ro_id": "Accreditation reference",
    "ro_station": "Station name",
    "ro_capacity": "Station DNC in kW",
    "ro_capacity_unit": "kW",
    "ro_bmu": None,
}
DAY = date(2026, 9, 8)


def unit(uid, name, cap="50.000", dem="0", fuel="WIND", gsp=None, ng=None, lead="Co Ltd"):
    return {
        "elexonBmUnit": uid,
        "nationalGridBmUnit": ng or uid.replace("T_", ""),
        "bmUnitName": name,
        "generationCapacity": cap,
        "demandCapacity": dem,
        "fuelType": fuel,
        "gspGroupId": gsp,
        "leadPartyName": lead,
        "bmUnitType": "T",
    }


# --------------------------------------------------------------- normalising


def test_name_match_strips_the_declared_generic_tokens_and_needs_a_superset():
    assert ss.name_match("Clash Gour Wind Farm", "Clash Gour")
    assert ss.name_match("Beinn an Tuirc III Windfarm", "Beinn an Tuirc III")
    assert not ss.name_match("Beinn an Tuirc II", "Beinn an Tuirc III")
    assert not ss.name_match("Wind Farm", "Wind Farm")  # nothing left after generic tokens
    assert ss.name_match("Griffin Wind Farm Extension", "Griffin")


def test_capacity_tolerance_is_fifteen_percent_of_the_reference():
    assert ss.within_tolerance(D("115"), D("100")) and not ss.within_tolerance(D("116"), D("100"))
    assert not ss.within_tolerance(None, D("100")) and not ss.within_tolerance(D("1"), D("0"))


def test_period_start_is_bst_for_the_record_day():
    assert ss.period_start_utc(DAY, 1) == datetime(2026, 9, 7, 23, 0, tzinfo=UTC)
    assert ss.period_start_utc(DAY, 48) == datetime(2026, 9, 8, 22, 30, tzinfo=UTC)


# ---------------------------------------------------------------- link table


def test_cfd_link_is_grade_a_only_when_effective_on_the_day():
    u = unit("T_ABCW-1", "Abc Wind Farm")
    mapping = [
        {
            "CFD_Id": "AAA-ABC-001",
            "BMU_Id": "T_ABCW-1",
            "Effective_From": "2020-01-01 00:00:00.0000000",
            "Effective_date_to": "",
        },
        {
            "CFD_Id": "AAA-OLD-002",
            "BMU_Id": "T_ABCW-1",
            "Effective_From": "2018-01-01 00:00:00.0000000",
            "Effective_date_to": "2024-03-20 00:00:00.0000000",
        },
        {
            "CFD_Id": "AAA-FUT-003",
            "BMU_Id": "ABCW-1",
            "Effective_From": "2027-01-01 00:00:00.0000000",
            "Effective_date_to": "",
        },
    ]
    portfolio = {
        "AAA-ABC-001": {
            "Name_of_CFD_Unit": "Abc",
            "Technology_Type": "Onshore Wind",
            "Maximum_Contract_Capacity_MW": "49.9",
            "Status": "Operational",
        }
    }
    links = ss.cfd_links(u, mapping, portfolio, DAY, READING)
    assert [(link.target, link.grade) for link in links] == [("AAA-ABC-001", "A")]
    assert links[0].extra["technology"] == "Onshore Wind"


def test_ro_links_grade_b_needs_name_and_capacity_and_c_without():
    u = unit("T_ABCW-1", "Abc Wind Farm", cap="50.000")
    ro = [
        {
            "Accreditation reference": "R1",
            "Station name": "Abc Wind Farm",
            "Station DNC in kW": "48,000",
        },
        {
            "Accreditation reference": "R2",
            "Station name": "Abc Wind Farm Phase 2",
            "Station DNC in kW": "20,000",
        },
        {
            "Accreditation reference": "R3",
            "Station name": "Co Ltd Solar",
            "Station DNC in kW": "5,000",
        },
        {
            "Accreditation reference": "R4",
            "Station name": "Elsewhere",
            "Station DNC in kW": "50,000",
        },
    ]
    links = ss.ro_links(u, ro, READING, {"R1": D("50"), "R2": D("50")})
    assert [(link.target, link.grade) for link in links] == [("R1", "B"), ("R2", "C"), ("R3", "C")]
    assert ss.scheme_of(links) == "ro"
    assert ss.scheme_of([link for link in links if link.grade == "C"]) == "ro-possible"
    assert ss.scheme_of([]) == "unmatched"


def test_ro_grade_a_applies_only_with_an_identifier_column():
    u = unit("T_ABCW-1", "Abc")
    reading = dict(READING, ro_bmu="BMU")
    ro = [
        {
            "Accreditation reference": "R9",
            "Station name": "Other",
            "Station DNC in kW": "1",
            "BMU": "T_ABCW-1",
        }
    ]
    assert [link.grade for link in ss.ro_links(u, ro, reading, {})] == ["A"]


def test_scheme_both_when_cfd_and_ro_link():
    links = [ss.Link("u", "cfd", "c", "A", ""), ss.Link("u", "ro", "r", "B", "")]
    assert ss.scheme_of(links) == "both"


# ---------------------------------------------------------------- side of B6


def test_side_of_b6_ladder_grades_a_then_b_then_c_then_unknown():
    cmis = [{"BMU ID": "WHILW-1", "B6/EC5": "B6"}]
    tec = [
        {
            "Project Name": "Griffin Wind Farm",
            "HOST TO": "SHET",
            "Cumulative Total Capacity (MW)": "156",
        },
        {
            "Project Name": "Southern Park",
            "HOST TO": "NGET",
            "Cumulative Total Capacity (MW)": "100",
        },
    ]
    assert ss.side_of_b6(unit("T_WHILW-1", "Whitelee", ng="WHILW-1"), cmis, tec) == (
        "north",
        "A",
        "CMIS intertrip arming lists the unit against B6",
    )
    side, grade, basis = ss.side_of_b6(unit("T_GRIFW-1", "Griffin", cap="150"), cmis, tec)
    assert (side, grade) == ("north", "B") and "SHET" in basis
    assert ss.side_of_b6(unit("T_SPARK-1", "Southern Park", cap="100"), cmis, tec)[:2] == (
        "south",
        "B",
    )
    assert ss.side_of_b6(unit("2__ABC001", "Battery", cap="20", gsp="_P"), cmis, tec)[:2] == (
        "north",
        "C",
    )
    assert ss.side_of_b6(unit("2__ABC002", "Battery", cap="20", gsp="_A"), cmis, tec)[:2] == (
        "south",
        "C",
    )
    assert ss.side_of_b6(unit("T_NOWHERE", "Nowhere", cap="20"), cmis, tec) == (
        "unknown",
        "-",
        "no graded evidence",
    )


# ----------------------------------------------------------- energy bounds


def mdo(unit_id, level, published):
    return {"bmUnit": unit_id, "levelFrom": level, "levelTo": level, "publishTime": published}


def test_energy_bound_hindsight_and_public_as_of_differ_by_publish_time():
    records = [
        mdo("B1", 40, "2026-09-07T20:00:00Z"),
        mdo("B1", 60, "2026-09-08T10:00:00Z"),
        mdo("B2", 5, "2026-09-07T20:00:00Z"),
    ]
    assert ss.energy_bound(records, "B1", None) == D("60")
    assert ss.energy_bound(records, "B1", datetime(2026, 9, 8, 6, 0, tzinfo=UTC)) == D("40")
    assert ss.energy_bound(records, "B3", None) is None
    assert ss.hours(D("60"), D("30")) == D("2.00") and ss.hours(D("60"), D("-30")) == D("2.00")
    assert ss.hours(None, D("30")) is None and ss.hours(D("60"), D("0")) is None


# ------------------------------------------------------------- end to end


def disptav(unit_id, kind, mwh):
    return {"bmUnit": unit_id, "dataType": kind, "pairVolumes": {"v1": str(mwh)}}


def test_run_splits_wind_bids_by_scheme_and_lays_out_the_energy_limited_units():
    register = {
        "T_CFDW-1": unit("T_CFDW-1", "Cfd Wind", cap="100"),
        "T_ROW-1": unit("T_ROW-1", "Ro Wind", cap="50"),
        "T_NONE-1": unit("T_NONE-1", "Mystery Wind", cap="10"),
        "2__BATT001": unit("2__BATT001", "North Battery", cap="20", dem="-20", fuel=None, gsp="_P"),
        "T_PUMP-1": unit("T_PUMP-1", "Pump", cap="300", dem="-300", fuel="PS"),
    }
    bids = [
        {"settlementPeriod": 10, "bmUnit": "T_CFDW-1", "totalCashflow": 1000},
        {"settlementPeriod": 10, "bmUnit": "T_ROW-1", "totalCashflow": 3000},
        {"settlementPeriod": 11, "bmUnit": "T_ROW-1", "totalCashflow": -50},
        {"settlementPeriod": 10, "bmUnit": "T_NONE-1", "totalCashflow": 100},
        {"settlementPeriod": 10, "bmUnit": "2__BATT001", "totalCashflow": 40},
    ]
    offers = [{"settlementPeriod": 20, "bmUnit": "2__BATT001", "totalCashflow": 70}]
    # Tagged reconciles: bids 10 + 30 + 1 + 2 = 43 in p10, 1 in p11; offers 2 in p20
    disptav_files: dict[tuple[str, int], list[dict]] = {
        (d, p): [] for d in ("bid", "offer") for p in range(1, 49)
    }
    disptav_files[("bid", 10)] = [
        disptav("T_CFDW-1", "Tagged", 10),
        disptav("T_ROW-1", "Tagged", 30),
        disptav("T_NONE-1", "Tagged", 1),
        disptav("2__BATT001", "Tagged", 2),
        disptav("T_ROW-1", "Original", 5),
    ]
    disptav_files[("bid", 11)] = [disptav("T_ROW-1", "Tagged", 1)]
    disptav_files[("offer", 20)] = [disptav("2__BATT001", "Tagged", 2)]
    prices = [{"totalAcceptedBidVolume": -44, "totalAcceptedOfferVolume": 2}]
    mapping = [
        {
            "CFD_Id": "AAA-CFD-1",
            "BMU_Id": "T_CFDW-1",
            "Effective_From": "2020-01-01 00:00:00.0000000",
            "Effective_date_to": "",
        }
    ]
    portfolio = [
        {
            "CFD_ID": "AAA-CFD-1",
            "Name_of_CFD_Unit": "Cfd Wind",
            "Technology_Type": "Onshore Wind",
            "Maximum_Contract_Capacity_MW": "100",
            "Status": "Operational",
        }
    ]
    ro = [
        {"Accreditation reference": "R1", "Station name": "Ro Wind", "Station DNC in kW": "50,000"}
    ]
    mdo_rows = [
        mdo("2__BATT001", 10, "2026-09-07T20:00:00Z"),
        mdo("2__BATT001", 30, "2026-09-08T12:00:00Z"),
        mdo("T_PUMP-1", 900, "2026-09-07T20:00:00Z"),
    ]
    mdb_rows = [mdo("2__BATT001", 15, "2026-09-07T20:00:00Z")]
    out = ss.run(
        day=DAY,
        register=register,
        bids=bids,
        offers=offers,
        disptav=disptav_files,
        prices=prices,
        mapping=mapping,
        portfolio=portfolio,
        ro=ro,
        cmis=[],
        tec=[],
        mdo=mdo_rows,
        mdb=mdb_rows,
        reading=READING,
    )
    assert out["reconciliation"]["chosen"] == "Tagged"
    table = {row["scheme"]: row for row in out["wind"]["table"]}
    assert (table["cfd"]["units"], table["cfd"]["bid_paid_gbp"], table["cfd"]["bid_mwh"]) == (
        1,
        D("1000"),
        D("10"),
    )
    assert (
        table["ro"]["units"],
        table["ro"]["bid_paid_gbp"],
        table["ro"]["bid_signed_gbp"],
        table["ro"]["bid_mwh"],
    ) == (1, D("3000"), D("2950"), D("31"))
    assert table["ro"]["gbp_per_mwh"] == D("96.77") and table["cfd"]["gbp_per_mwh"] == D("100.00")
    assert table["unmatched"]["units"] == 1 and table["unmatched"]["share_of_wind_bid_gbp"] == D(
        "0.0244"
    )
    assert out["propositions"] == {"S1": "holds", "S2": "fails", "B1": "undecided"}
    assert out["constraint"]["periods"] == 2 and out["constraint"]["longest_run_hours"] == D("1")
    assert out["constraint"]["first_period"] == 10
    storage = {row["unit"]: row for row in out["storage"]}
    assert set(storage) == {"2__BATT001", "T_PUMP-1"}
    b = storage["2__BATT001"]
    assert (b["side_of_b6"], b["side_grade"]) == ("north", "C")
    assert b["export_hours_r3h"] == D("1.50") and b["export_hours_r3p"] == D(
        "0.50"
    )  # 30/20 vs 10/20
    assert b["import_hours_r3h"] == D("0.75")
    assert (b["bid_paid_gbp"], b["offer_paid_gbp"], b["bid_mwh"], b["offer_mwh"]) == (
        D("40"),
        D("70"),
        D("2"),
        D("2"),
    )
    p = storage["T_PUMP-1"]
    assert (
        p["fuel_type"] == "PS"
        and p["export_hours_r3h"] == D("3.00")
        and p["import_hours_r3h"] is None
    )
    assert p["bid_rows"] == 0 and p["bid_paid_gbp"] is None
    assert out["constraint"]["b1_deciding_units"] == 0  # grade C units do not decide B1
    links = out["links"]
    assert {(link["unit"], link["register"], link["grade"]) for link in links} == {
        ("T_CFDW-1", "cfd", "A"),
        ("T_ROW-1", "ro", "B"),
    }
