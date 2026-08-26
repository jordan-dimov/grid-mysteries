from datetime import date
from decimal import Decimal

from grid_mysteries.investigations.tec_slippage import Observation, ProjectMetrics
from grid_mysteries.investigations.twr_attribution import (
    Attribution,
    TwrRow,
    TwrVintage,
    attribute_revisions,
    match_schemes,
    normalise_scheme,
    parse_twr_row,
    project_schemes,
    scheme_completion_by_vintage,
    slipped_before,
    t1_measurability,
    t2_discrimination,
    t3_reclassification,
    t4_descriptive,
    works_flag,
    works_moves,
)


def twr(name, customer, site, scheme, d, number=""):
    return TwrRow(name, customer, site, number, scheme, d)


def test_normalise_scheme_handles_drift_and_placeholders():
    assert normalise_scheme("SHETL-RI-089") == "SHET-RI-089"
    assert normalise_scheme(" shet-ri-007c ") == "SHET-RI-007C"
    assert normalise_scheme("SHET-RI-025b & NGET-RI-30204") == "SHET-RI-025B & NGET-RI-30204"
    assert normalise_scheme("SHET-RI-009 and SPT-RI-004") == "SHET-RI-009 & SPT-RI-004"
    assert normalise_scheme("Blank") is None and normalise_scheme("Works") is None
    assert normalise_scheme(None) is None


def test_proxy_completion_is_earliest_dependent_date_and_moves_are_signed():
    v1 = TwrVintage(
        date(2020, 1, 1),
        (
            twr("A", "Co", "S", "X-1", date(2023, 1, 1)),
            twr("B", "Co2", "S", "X-1", date(2022, 1, 1)),
        ),
    )
    v2 = TwrVintage(
        date(2020, 7, 1),
        (
            twr("A", "Co", "S", "X-1", date(2023, 1, 1)),
            twr("B", "Co2", "S", "X-1", date(2023, 6, 1)),
        ),
    )
    tl = scheme_completion_by_vintage([v2, v1])["X-1"]
    assert tl == [(date(2020, 1, 1), date(2022, 1, 1)), (date(2020, 7, 1), date(2023, 1, 1))]
    assert works_moves(tl) == [(date(2020, 7, 1), 12)]
    assert slipped_before(tl, date(2020, 8, 1)) and not slipped_before(tl, date(2020, 7, 1))


def test_join_prefers_project_number_then_customer_site_then_name_site():
    v = TwrVintage(
        date(2020, 1, 1),
        (
            twr("Wind A", "Co Ltd", "Site 1", "X-1", date(2023, 1, 1), "PRO-1"),
            twr("Wind B", "Other", "Site 2", "Y-9", date(2023, 1, 1)),
        ),
    )
    index = project_schemes([v])
    assert match_schemes("name:wind a|co ltd|site 1#1", index, "pro-1") == {"X-1"}
    assert match_schemes("name:renamed|co ltd|site 1#1", index) == {"X-1"}
    assert match_schemes("name:wind b|new owner|site 2#1", index) == {"Y-9"}
    assert match_schemes("name:nothing|nobody|nowhere#1", index) == set()


def obs(t, eff):
    return Observation(t, eff, "Scoping", Decimal(100), "Wind", "NGET", "S")


def test_attribution_windows_are_asymmetric_and_direction_matched():
    tec = [
        obs(date(2021, 1, 1), date(2025, 1, 1)),
        obs(date(2021, 6, 1), date(2027, 1, 1)),
        obs(date(2022, 1, 1), date(2026, 1, 1)),
    ]
    scheme_tl = {
        "X-1": [(date(2020, 12, 1), date(2025, 1, 1)), (date(2021, 3, 1), date(2027, 1, 1))]
    }
    out = attribute_revisions(tec, {"X-1"}, scheme_tl)
    assert out[0] == Attribution(date(2021, 6, 1), 24, "works_led", ("X-1",))
    assert out[1].outcome == "project_led"  # advance; no works advance in window
    assert attribute_revisions(tec, set(), scheme_tl)[0].outcome == "unattributable"
    late = {"X-1": [(date(2020, 1, 1), date(2025, 1, 1)), (date(2021, 10, 1), date(2027, 1, 1))]}
    assert (
        attribute_revisions(tec, {"X-1"}, late)[0].outcome == "project_led"
    )  # 122 days after: outside +90


def pm(key, first, slip, status="Scoping", to="NGET"):
    return ProjectMetrics(
        key,
        first,
        first.replace(year=first.year + 3),
        Decimal(3),
        None,
        None,
        1,
        slip,
        slip,
        False,
        status,
        "Wind",
        to,
        "<50",
        "3-5y",
        (),
    )


def test_t1_t2_t3_thresholds():
    vint = [
        TwrVintage(date(2017, 1, 1), ()),
        TwrVintage(date(2018, 1, 1), ()),
        TwrVintage(date(2019, 1, 1), ()),
        TwrVintage(date(2020, 1, 1), ()),
        TwrVintage(date(2021, 1, 1), ()),
    ]
    pop: list[ProjectMetrics] = []
    flags: dict[str, bool | None] = {}
    for cohort_start in (date(2020, 1, 1), date(2022, 6, 1)):
        for i in range(40):
            k = f"f{cohort_start.year}{i}"
            pop.append(pm(k, cohort_start, 36 if i < 20 else 0))
            flags[k] = True
        for i in range(40):
            k = f"u{cohort_start.year}{i}"
            pop.append(pm(k, cohort_start, 36 if i < 4 else 0))
            flags[k] = False
    t1 = t1_measurability(vint, pop, flags)
    assert t1.passes and t1.match_rate == Decimal(1) and t1.vintages == 5
    t2 = t2_discrimination(pop, flags)
    assert t2.rate_flagged == Decimal("0.5") and t2.rate_unflagged == Decimal("0.1") and t2.passes
    t3 = t3_reclassification(pop, flags)
    assert t3.pooled == Decimal("0.3") and t3.bands_status_only == {"Scoping": "mid"}
    assert t3.bands_status_x_flag == {"Scoping|works_slipped": "high", "Scoping|works_clean": "low"}
    assert t3.share_reclassified == Decimal(1) and t3.passes
    # gap of 19 points fails T2
    flags2 = dict(flags)
    pop2 = [
        pm(
            m.key,
            m.first_observed,
            36
            if (m.key.startswith("f") and int(m.key[5:]) < 11)
            else (36 if m.key.startswith("u") and int(m.key[5:]) < 4 else 0),
        )
        for m in pop
    ]
    assert not t2_discrimination(pop2, flags2).passes
    assert not t1_measurability(vint[:4], pop, flags).passes


def test_t4_reports_attribution_and_clustering():
    atts = {
        "k1": [Attribution(date(2021, 1, 1), 30, "works_led", ("X",))],
        "k2": [Attribution(date(2021, 1, 1), 26, "project_led", ())],
    }
    tl = {
        "X": [(date(2020, 1, 1), date(2025, 1, 1)), (date(2020, 7, 1), date(2026, 1, 1))],
        "Y": [(date(2020, 1, 1), date(2025, 1, 1)), (date(2020, 7, 1), date(2026, 6, 1))],
    }
    vint = [
        TwrVintage(date(2020, 1, 1), ()),
        TwrVintage(date(2020, 4, 1), ()),
        TwrVintage(date(2020, 7, 1), ()),
    ]
    t4 = t4_descriptive(atts, {"k1": "Scoping", "k2": "Built"}, tl, vint)
    assert t4.attribution_of_big_slips == {"works_led": 1, "project_led": 1}
    assert t4.works_moves_total == 2 and t4.works_moves_top_vintage_share == Decimal(1)
    assert t4.twr_median_gap_days == 91 and t4.attribution_resolvable


def test_parse_twr_row_maps_eras():
    r = parse_twr_row(
        {
            "Company Name": "RES",
            "Generator Name": "Aberarder",
            "Scheme Number": "SHETL-RI-089",
            "Connection Site": "Aberarder 132/33",
            "Connection Date": "30/06/2020",
        }
    )
    assert (r.customer, r.project_name, r.scheme, r.connection_date) == (
        "RES",
        "Aberarder",
        "SHETL-RI-089",
        date(2020, 6, 30),
    )
    r2 = parse_twr_row(
        {
            "Account Name": "L48",
            "Project Name": "[23-0225] X",
            "Project Number": "PRO-1",
            "Scheme Name": "SHET-RI-026",
            "Connection Site": "New Deer",
            "Mw Effective From": "2033-10-31 00:00:00",
        }
    )
    assert r2.project_number == "PRO-1" and r2.connection_date == date(2033, 10, 31)
    assert works_flag(pm("k", date(2020, 1, 1), 0), set(), {}) is None
