from datetime import date
from decimal import Decimal

from grid_mysteries.investigations.corporate_vitality import (
    arm_shares,
    classify,
    resolve,
    signal,
)
from grid_mysteries.investigations.corporate_vitality import (
    test1_verdict as verdict1,
)
from grid_mysteries.investigations.corporate_vitality import (
    test2 as run_test2,
)

FETCH = date(2026, 8, 28)


def hit(number, title, status="active", created="2018-01-01", ceased=None):
    return {
        "company_number": number,
        "title": title,
        "company_status": status,
        "date_of_creation": created,
        "date_of_cessation": ceased,
    }


def test_resolve_accepts_dissolved_exact_and_uses_lifespan_to_disambiguate():
    hits = [hit("1", "ORGANIC POWER LIMITED", "dissolved", "2000-01-01", "2020-05-01")]
    r = resolve("Organic Power Ltd", hits, [], {}, first_observed=date(2019, 1, 1))
    assert r.company_number == "1" and r.reason == "primary-exact"
    two = [
        hit("1", "ACME ONE LIMITED", "dissolved", "2000-01-01", "2010-01-01"),
        hit("2", "ACME ONE LIMITED", "active", "2015-01-01"),
    ]
    r = resolve("Acme One Ltd", two, [], {}, first_observed=date(2019, 1, 1))
    assert r.company_number == "2" and r.reason.endswith("+lifespan")
    both_alive = [hit("1", "ACME ONE LIMITED"), hit("2", "ACME ONE LIMITED")]
    assert (
        resolve("Acme One Ltd", both_alive, [], {}, first_observed=date(2019, 1, 1)).reason
        == "ambiguous"
    )


def test_resolve_falls_back_to_advanced_search_and_previous_names():
    adv = [hit("9", "HEIT PW LIMITED")]
    profiles = {
        "9": {"previous_company_names": [{"name": "HARMONY PW LIMITED", "ceased_on": "2024-01-01"}]}
    }
    r = resolve("Harmony PW Limited", [], adv, profiles, first_observed=date(2019, 1, 1))
    assert r.company_number == "9" and r.reason == "previous-name"
    assert (
        resolve("Nobody Ltd", [], [], {}, first_observed=date(2019, 1, 1)).reason
        == "no-exact-match"
    )


def test_classify_hierarchy():
    assert (
        classify(
            {"company_status": "dissolved", "date_of_cessation": "2021-03-02"}, [], fetch_date=FETCH
        ).tier
        == "V1"
    )
    liq = classify(
        {"company_status": "liquidation"},
        [
            {
                "date": "2022-02-02",
                "description": "liquidation-voluntary-extraordinary-resolution-to-wind-up",
            }
        ],
        fetch_date=FETCH,
    )
    assert liq.tier == "V2" and liq.on == date(2022, 2, 2) and not liq.undated
    gaz = classify(
        {"company_status": "active"},
        [{"date": "2025-01-10", "description": "gazette-notice-compulsory", "type": "GAZ1"}],
        fetch_date=FETCH,
    )
    assert gaz.tier == "V3" and gaz.on == date(2025, 1, 10)
    cured = classify(
        {"company_status": "active"},
        [
            {"date": "2025-01-10", "description": "gazette-notice-compulsory", "type": "GAZ1"},
            {
                "date": "2025-02-01",
                "description": "accounts-with-accounts-type-micro-entity",
                "type": "AA",
            },
        ],
        fetch_date=FETCH,
    )
    assert cured.tier == "V0"
    proposal = classify(
        {"company_status": "active", "company_status_detail": "active-proposal-to-strike-off"},
        [],
        fetch_date=FETCH,
    )
    assert proposal.tier == "V3" and proposal.undated
    overdue = classify(
        {"company_status": "active", "accounts": {"overdue": True, "next_due": "2025-12-31"}},
        [],
        fetch_date=FETCH,
    )
    assert overdue.tier == "V4"
    recent = classify(
        {"company_status": "active", "accounts": {"overdue": True, "next_due": "2026-06-30"}},
        [],
        fetch_date=FETCH,
    )
    assert recent.tier == "V0"
    dormant = classify(
        {
            "company_status": "active",
            "accounts": {"last_accounts": {"type": "dormant", "made_up_to": "2025-03-31"}},
        },
        [],
        fetch_date=FETCH,
    )
    assert dormant.tier == "V5"


def test_signal_identity_error_and_as_of():
    dissolved = classify(
        {"company_status": "dissolved", "date_of_cessation": "2018-03-02"}, [], fetch_date=FETCH
    )
    assert signal(dissolved, first_observed=date(2019, 1, 1), as_of=FETCH) == "identity-error"
    assert signal(dissolved, first_observed=date(2017, 1, 1), as_of=FETCH) == "strong"
    assert signal(dissolved, first_observed=date(2017, 1, 1), as_of=date(2018, 1, 1)) == "none"
    dormant = classify(
        {"company_status": "active", "accounts": {"last_accounts": {"type": "dormant"}}},
        [],
        fetch_date=FETCH,
    )
    assert signal(dormant, first_observed=date(2017, 1, 1), as_of=FETCH) == "none"


def _stage(cust, mw, first="2019-01-01", last="2025-01-01"):
    return {
        "customer_norm": cust,
        "mw": mw,
        "first_observed": first,
        "first_seen": first,
        "last_seen": last,
    }


def test_arm_shares_and_test1():
    states = {
        "a": classify(
            {"company_status": "dissolved", "date_of_cessation": "2022-01-01"}, [], fetch_date=FETCH
        ),
        "b": classify({"company_status": "active"}, [], fetch_date=FETCH),
        "c": None,
        "d": classify(
            {"company_status": "dissolved", "date_of_cessation": "2010-01-01"}, [], fetch_date=FETCH
        ),
    }
    stages = [_stage("a", "100"), _stage("b", "300"), _stage("c", "50"), _stage("d", "40")]
    arm = arm_shares("scoping", stages, states, as_of=FETCH)
    assert arm.mw_total == Decimal(490) and arm.mw_resolved == Decimal(400)
    assert arm.share_strong_mw == Decimal("0.25") and arm.n_identity_error == 1
    assert arm.share_strong_floor_mw == Decimal("0.2041")
    built = arm_shares("built", [_stage("b", "1000")], states, as_of=FETCH)
    v = verdict1(arm, built)
    assert v.verdict == "material" and v.gap_pp == Decimal("25.0")
    live = arm_shares("scoping", [_stage("b", "1000"), _stage("a", "10")], states, as_of=FETCH)
    assert verdict1(live, built).verdict == "live"
    uncovered = arm_shares("scoping", [_stage("c", "1000"), _stage("a", "10")], states, as_of=FETCH)
    assert not verdict1(uncovered, built).determinable


def test_test2_leading_and_hole_handling():
    states = {
        f"g{i}": classify(
            {"company_status": "dissolved", "date_of_cessation": "2024-06-01"}, [], fetch_date=FETCH
        )
        for i in range(12)
    }
    states["late"] = classify(
        {"company_status": "dissolved", "date_of_cessation": "2025-06-01"}, [], fetch_date=FETCH
    )
    states["live"] = classify({"company_status": "active"}, [], fetch_date=FETCH)
    gone = [_stage(f"g{i}", "10", first="2024-04-02", last="2025-01-01") for i in range(12)]
    gone.append(_stage("late", "10", first="2024-04-02", last="2025-01-01"))
    gone.append(_stage("hole", "10", first="2024-04-02", last="2025-07-22"))
    states["hole"] = classify(
        {"company_status": "dissolved", "date_of_cessation": "2025-03-01"}, [], fetch_date=FETCH
    )
    control = [_stage("live", "10", first="2024-04-02", last="2026-08-25")] * 20 + [
        _stage("g0", "10", first="2024-04-02", last="2026-08-25")
    ]
    r = run_test2(gone, control, states, as_of=FETCH)
    assert r.n_gone_strong == 14 and r.n_leading == 13
    assert r.n_strong_excl_hole == 13 and r.n_leading_excl_hole == 12
    assert r.verdict == "leading"
