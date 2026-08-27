from datetime import date
from decimal import Decimal

from grid_mysteries.investigations.spv_financing import (
    ArmSummary,
    arms,
    charge_facts,
    customer_of,
    last_status,
    resolve,
    stage1_verdict,
    summarise_arm,
)
from grid_mysteries.sources.companies_house import normalise_company_name


def _row(
    key, first_status, transitions="", span="3.5", first="2019-01-04", plant="Energy Storage System"
):
    return {
        "key": key,
        "first_status": first_status,
        "status_transitions": transitions,
        "observation_span_years": span,
        "first_observed": first,
        "last_observed": "2024-06-01",
        "plant_type": plant,
    }


def test_customer_and_last_status():
    row = _row(
        "name:site a|acme energy one limited|gsp#1",
        "Scoping",
        "Scoping->Consents Approved;Consents Approved->Built",
    )
    assert customer_of(row["key"]) == "acme energy one limited"
    assert last_status(row) == "Built"
    assert last_status(_row("name:x|y|z#1", "Scoping")) == "Scoping"


def test_arms_apply_the_sealed_cohort_rules():
    rows = [
        _row("name:a|c1|s#1", "Scoping", "Scoping->Built"),  # built arm
        _row(
            "name:b|c2|s#1",
            "Awaiting Consents",
            "Awaiting Consents->Under Construction/Commissioning",
        ),
        _row("name:c|c3|s#1", "Scoping"),  # scoping arm
        _row("name:d|c4|s#1", "Scoping", span="2.5"),  # too short for scoping arm
        _row("name:e|c5|s#1", "Built", ""),  # first status not eligible
        _row(
            "name:f|c6|s#1", "Scoping", "Scoping->Built", first="2024-01-05"
        ),  # outside 005 population
        _row("name:g|c7|s#1", "Scoping", "Scoping->Built", plant="CCGT"),  # not storage
    ]
    built, scoping = arms(rows)
    assert [r["key"] for r in built] == ["name:a|c1|s#1", "name:b|c2|s#1"]
    assert [r["key"] for r in scoping] == ["name:c|c3|s#1"]
    built_all, _ = arms(rows, storage_only=False)
    assert len(built_all) == 3


def test_normalise_company_name_is_suffix_and_punctuation_insensitive():
    assert normalise_company_name("Acme Energy One Limited") == "ACME ENERGY ONE LTD"
    assert normalise_company_name("ACME ENERGY ONE LTD.") == "ACME ENERGY ONE LTD"
    assert normalise_company_name("Acme & Co Public Limited Company") == "ACME AND CO PLC"


def test_resolve_requires_exactly_one_active_exact_match():
    hits = [
        {"title": "ACME ENERGY ONE LIMITED", "company_number": "1", "company_status": "active"},
        {"title": "ACME ENERGY TWO LIMITED", "company_number": "2", "company_status": "active"},
    ]
    assert resolve("Acme Energy One Ltd", hits).company_number == "1"
    assert resolve("Acme Energy Three Ltd", hits).reason == "no-exact-match"
    dissolved = [
        {"title": "ACME ENERGY ONE LIMITED", "company_number": "1", "company_status": "dissolved"}
    ]
    assert resolve("Acme Energy One Ltd", dissolved).reason == "exact-but-not-active"
    twice = hits + [
        {"title": "Acme Energy One Ltd", "company_number": "3", "company_status": "active"}
    ]
    assert resolve("Acme Energy One Ltd", twice).reason == "ambiguous-active"


def test_charge_facts_use_the_first_charge_after_tec_appearance():
    profile = {"date_of_creation": "2017-03-01"}
    charges = {
        "items": [
            {"created_on": "2018-05-01"},
            {"created_on": "2020-02-10"},
            {"created_on": "2025-01-01"},
        ]
    }
    facts = charge_facts(
        "1", profile, charges, first_observed=date(2019, 1, 4), last_observed=date(2024, 6, 1)
    )
    assert facts.n_charges == 3
    assert facts.n_after_first_observed == 1
    assert facts.first_created == date(2018, 5, 1)
    assert facts.first_created_after_first_observed == date(2020, 2, 10)
    empty = charge_facts(
        "2",
        {},
        {"errors": [{"error": "not found"}]},
        first_observed=date(2019, 1, 4),
        last_observed=date(2024, 6, 1),
    )
    assert empty.n_charges == 0 and empty.incorporated is None


def test_summarise_arm_and_verdict():
    projects = [_row(f"name:p{i}|cust{i}|s#1", "Scoping", "Scoping->Built") for i in range(4)]
    facts = {
        "cust0": charge_facts(
            "a",
            {"date_of_creation": "2015-06-01"},
            {"items": [{"created_on": "2020-01-01"}]},
            first_observed=date(2019, 1, 4),
            last_observed=date(2024, 6, 1),
        ),
        "cust1": charge_facts(
            "b",
            {"date_of_creation": "2018-06-01"},
            {"items": []},
            first_observed=date(2019, 1, 4),
            last_observed=date(2024, 6, 1),
        ),
        "cust2": None,
    }
    summary = summarise_arm("built", projects, facts)
    assert summary.n_resolved == 2 and summary.resolved_share == Decimal("0.5")
    assert summary.incidence == Decimal(
        "0.5"
    ) and summary.incidence_after_first_observed == Decimal("0.5")
    assert summary.median_company_age_years == Decimal("7.5")

    def arm(label, n, resolved, with_charge):
        return ArmSummary(
            label,
            n,
            resolved,
            Decimal(resolved) / Decimal(n),
            with_charge,
            Decimal(with_charge) / Decimal(resolved),
            0,
            Decimal(0),
            None,
        )

    assert not stage1_verdict(arm("b", 30, 30, 20), arm("s", 50, 50, 5)).determinable
    survives = stage1_verdict(arm("b", 50, 40, 30), arm("s", 50, 40, 10))
    assert survives.survives and survives.gap_pp == Decimal("50.0")
    killed = stage1_verdict(arm("b", 50, 40, 14), arm("s", 50, 40, 10))
    assert killed.determinable and not killed.survives and killed.gap_pp == Decimal("10.0")
    unresolved = stage1_verdict(arm("b", 50, 20, 20), arm("s", 50, 40, 10))
    assert not unresolved.survives and "resolved" in unresolved.note
