from datetime import date
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from grid_mysteries.investigations.tec_slippage import (
    Vintage,
    all_metrics,
    build_timelines,
    identity,
    match_report,
    months_between,
    parse_date,
    population,
    q1_dispersion,
    q2_predictability,
    q3_materiality,
)


def row(
    pid="",
    name="Wind A",
    customer="Co",
    site="Site",
    eff="2027-10-01",
    status="Scoping",
    mw="100",
    plant="Wind",
    to="NGET",
):
    return {
        "Project ID": pid,
        "Project Name": name,
        "Customer Name": customer,
        "Connection Site": site,
        "MW Effective From": eff,
        "Project Status": status,
        "Cumulative Total Capacity (MW)": mw,
        "Plant Type": plant,
        "HOST TO": to,
    }


def test_parse_date_iso_and_uk_forms():
    assert parse_date("2027-10-01") == date(2027, 10, 1)
    assert parse_date("01/10/2027") == date(2027, 10, 1)
    assert parse_date("") is None
    assert parse_date("not a date") is None


@given(st.dates(min_value=date(2000, 1, 1), max_value=date(2050, 1, 1)), st.integers(-600, 600))
def test_months_between_is_signed_and_additive(start, months):
    y, m = divmod(start.month - 1 + months, 12)
    later = date(start.year + y, m + 1, 1)
    assert months_between(start, later) == months
    assert months_between(later, start) == -months


def test_identity_prefers_project_id_then_normalised_triple():
    assert identity(row(pid="P1")) == "id:P1"
    assert identity(row(name="Wind  A!", customer="Co.", site="SITE")) == "name:wind a|co|site"


def test_timeline_metrics_count_revisions_and_signed_slip():
    vintages = [
        Vintage(date(2020, 1, 1), (row(eff="2025-04-01"),)),
        Vintage(date(2021, 1, 1), (row(eff="2027-10-01", status="Awaiting Consents"),)),
        Vintage(date(2022, 6, 1), (row(eff="2027-04-01"),)),
    ]
    metrics = all_metrics(build_timelines(vintages), last_vintage=date(2022, 6, 1))
    (m,) = metrics
    assert m.revisions == 2
    assert m.net_slip_months == 24
    assert m.max_single_revision_months == 30
    assert m.disappeared is False
    assert m.status_transitions == (
        ("Scoping", "Awaiting Consents"),
        ("Awaiting Consents", "Scoping"),
    )
    assert m.initial_lead_time_band == ">5y"  # 2020-01 -> 2025-04 is 5.25 years


def test_disappearance_is_separate_from_slip():
    vintages = [
        Vintage(date(2020, 1, 1), (row(name="Gone"), row(name="Stays"))),
        Vintage(date(2023, 1, 1), (row(name="Stays"),)),
    ]
    by_key = {
        m.key: m for m in all_metrics(build_timelines(vintages), last_vintage=date(2023, 1, 1))
    }
    assert by_key["name:gone|co|site"].disappeared is True
    assert by_key["name:gone|co|site"].net_slip_months is None
    assert by_key["name:stays|co|site"].disappeared is False


def _pop(slips, first_observed=date(2020, 1, 1), plant="Wind"):
    vintages = [
        Vintage(
            first_observed,
            tuple(row(name=f"P{i}", eff="2026-01-01", plant=plant) for i in range(len(slips))),
        ),
        Vintage(
            date(first_observed.year + 2, 6, 1),
            tuple(
                row(name=f"P{i}", eff=f"{2026 + (s // 12)}-{(s % 12) + 1:02d}-01", plant=plant)
                for i, s in enumerate(slips)
            ),
        ),
    ]
    return population(all_metrics(build_timelines(vintages), last_vintage=date(2024, 6, 1)))


def test_q1_threshold_boundaries():
    # 25% slip 36 months, 25% slip 0, rest 12: IQR 36-0? sorted quartiles -> passes
    pop = _pop([36] * 5 + [0] * 5 + [12] * 10)
    r = q1_dispersion(pop)
    assert (
        r.n == 20 and r.share_slipped_ge_24 == Decimal("0.25") and r.share_lt_6 == Decimal("0.25")
    )
    assert r.passes
    # everything slips the same: IQR 0 -> fails
    assert not q1_dispersion(_pop([24] * 20)).passes
    assert not q1_dispersion([]).passes


def test_q2_requires_ratio_and_both_cohorts():
    wind_a = _pop([36] * 20 + [0] * 20, first_observed=date(2020, 1, 1), plant="Wind")
    solar_a = _pop([36] * 5 + [0] * 35, first_observed=date(2020, 1, 1), plant="Solar")
    wind_b = _pop([36] * 20 + [0] * 20, first_observed=date(2022, 6, 1), plant="Wind")
    solar_b = _pop([36] * 5 + [0] * 35, first_observed=date(2022, 6, 1), plant="Solar")
    pop = wind_a + solar_a + wind_b + solar_b
    results = {r.name: r for r in q2_predictability(pop)}
    plant = results["plant_type"]
    assert plant.high == "Wind" and plant.low == "Solar" and plant.best_ratio == Decimal("4")
    assert plant.holds_in_both_cohorts and plant.passes
    q3 = q3_materiality(pop, list(results.values()))
    assert q3.pooled_rate == Decimal("0.3125") and q3.passes
    # same effect in one cohort only does not pass
    one_cohort = wind_a + solar_a
    assert not {r.name: r for r in q2_predictability(one_cohort)}["plant_type"].passes


def test_match_report_counts_identity_kinds():
    vintages = [Vintage(date(2020, 1, 1), (row(pid="P1"), row(name="X")))]
    report = match_report(build_timelines(vintages))
    assert (
        report.identities,
        report.by_project_id,
        report.by_name_triple,
        report.single_vintage_only,
    ) == (2, 1, 1, 2)
