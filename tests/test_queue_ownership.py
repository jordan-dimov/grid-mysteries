from datetime import date
from decimal import Decimal

from grid_mysteries.investigations import queue_ownership as qo


def row(
    customer="ZENOBE STALYBRIDGE LIMITED",
    mw="150.00",
    pid="a0l4L0000005iuVQAQ",
    status="Scoping",
    gate="",
):
    return {
        "Project Name": "X",
        "Customer Name": customer,
        "MW Increase / Decrease": mw,
        "Project ID": pid,
        "Project Status": status,
        "Gate": gate,
    }


def hit(number, title, status="active", created="2022-08-16", ceased=None):
    return {
        "company_number": number,
        "title": title,
        "company_status": status,
        "date_of_creation": created,
        "date_of_cessation": ceased,
    }


# R1


def test_r1_names_collapse_whitespace_keep_case_and_sum_mw():
    rows = [row("A  Ltd"), row("A Ltd", mw="10"), row("a ltd", mw="1", pid="a0l4L0000005other")]
    out = qo.names(rows)
    assert set(out) == {"A Ltd", "a ltd"}
    assert out["A Ltd"].rows == 2 and out["A Ltd"].mw == Decimal("160.00")
    assert out["A Ltd"].project_ids == {"a0l4L0000005iuV"}
    assert qo.case_pairs(out) == [["A Ltd", "a ltd"]]
    assert not out["A Ltd"].no_suffix and qo.names([row("John Smith")])["John Smith"].no_suffix
    assert qo.has_company_suffix("ACME PLC") and qo.has_company_suffix("Acme Energy LLP")
    assert not qo.has_company_suffix("Scottish Power Renewables")


# R2


def test_r2_exactly_one_exact_candidate_resolves():
    hits = [hit("14299411", "ZENOBE STALYBRIDGE LIMITED"), hit("1", "ZENOBE ENERGY LIMITED")]
    lk = qo.resolve("Zenobe Stalybridge Ltd", hits, None, {}, first_seen=date(2023, 1, 1))
    assert lk.klass == "exact" and lk.company_number == "14299411" and lk.resolved


def test_r2_several_exact_candidates_are_ambiguous_dissolved_included():
    hits = [hit("1", "ACME LIMITED"), hit("2", "ACME LTD", status="dissolved", ceased="2020-01-01")]
    lk = qo.resolve("Acme Limited", hits, None, {}, None)
    assert lk.klass == "ambiguous" and lk.company_number is None and lk.candidates == ("1", "2")


def test_r2_previous_name_resolves_and_no_advanced_search_is_unresolved():
    hits = [hit("9", "SOMETHING ELSE LTD")]
    assert qo.resolve("FlexibleGridPower2 Ltd", hits, None, {}, None).klass == "unresolved"
    adv = [hit("10683876", "HUNTERSTON GRID 1 LTD", created="2017-03-22")]
    profiles = {
        "10683876": {
            "previous_company_names": [
                {"name": "FLEXIBLEGRIDPOWER2 LTD", "ceased_on": "2025-06-26"}
            ]
        }
    }
    lk = qo.resolve("FlexibleGridPower2 Ltd", hits, adv, profiles, first_seen=date(2021, 11, 1))
    assert lk.klass == "previous-name" and lk.company_number == "10683876"
    none = qo.resolve("Nobody Here Ltd", hits, adv, profiles, None)
    assert none.klass == "unresolved" and none.candidates == ("9",)


def test_r2_identity_guard_refuses_a_company_created_after_the_name_was_printed():
    hits = [hit("5", "REUSED NAME LIMITED", created="2024-05-01")]
    lk = qo.resolve("Reused Name Limited", hits, None, {}, first_seen=date(2022, 1, 1))
    assert lk.klass == "identity-guard" and lk.company_number is None and lk.candidates == ("5",)
    ok = qo.resolve("Reused Name Limited", hits, None, {}, first_seen=date(2024, 6, 1))
    assert ok.klass == "exact"


def test_r2_admission_overrides_only_unresolved_links():
    unresolved = qo.Link("A", "unresolved", None, ("1", "2"), "")
    admitted = {
        "A": {"decision": "admitted", "company_number": "2", "on": "2026-10-01", "by": "JD"}
    }
    out = qo.apply_admissions(unresolved, admitted)
    assert out.klass == "admitted" and out.company_number == "2" and out.resolved
    refused = qo.apply_admissions(
        unresolved, {"A": {"decision": "refused", "on": "2026-10-01", "by": "JD"}}
    )
    assert refused.klass == "refused" and not refused.resolved
    exact = qo.Link("A", "exact", "1", ("1",), "")
    assert qo.apply_admissions(exact, admitted) == exact


# R3


def test_r3_under_a_year_old_is_measured_from_the_copy_date():
    assert qo.under_a_year_old({"date_of_creation": "2025-09-29"}) is True
    assert qo.under_a_year_old({"date_of_creation": "2025-09-28"}) is False
    assert qo.under_a_year_old({}) is None
    assert qo.age_years({"date_of_creation": "2016-09-29"}) == Decimal("10.0")


# R4


def test_r4_name_changes_and_their_classes():
    history = {
        "p1": [
            {"t_public": "2022-01-01", "name": "OLD LTD"},
            {"t_public": "2023-05-01", "name": "NEW LTD"},
        ],
        "p2": [{"t_public": "2022-01-01", "name": "SAME LTD"}],
        "p3": [
            {"t_public": "2022-01-01", "name": "A LTD"},
            {"t_public": "2022-06-01", "name": "B LTD"},
            {"t_public": "2023-01-01", "name": "C LTD"},
        ],
    }
    changes = qo.name_changes(history)
    assert [(c.project_id, c.earlier, c.later) for c in changes] == [
        ("p1", "OLD LTD", "NEW LTD"),
        ("p3", "A LTD", "B LTD"),
        ("p3", "B LTD", "C LTD"),
    ]
    links = {
        "OLD LTD": qo.Link("OLD LTD", "exact", "100", ("100",), ""),
        "NEW LTD": qo.Link("NEW LTD", "exact", "100", ("100",), ""),
        "A LTD": qo.Link("A LTD", "exact", "1", ("1",), ""),
        "B LTD": qo.Link("B LTD", "exact", "2", ("2",), ""),
        "C LTD": qo.Link("C LTD", "unresolved", None, (), ""),
    }
    profiles = {"100": {"previous_company_names": [{"name": "OLD LTD", "ceased_on": "2023-03-15"}]}}
    out = [qo.classify_change(c, links, profiles) for c in changes]
    assert out[0]["class"] == "rename" and out[0]["companies_house_date"] == "2023-03-15"
    assert out[0]["register_lag_days"] == (date(2023, 5, 1) - date(2023, 3, 15)).days
    assert out[1]["class"] == "transfer" and out[1]["register_lag_days"] is None
    assert out[2]["class"] == "not-determinable"


def test_r4_rename_by_previous_name_when_only_the_later_company_resolves():
    c = qo.NameChange("p", "OLD LTD", "NEW LTD", "2022-01-01", "2023-05-01")
    links = {"NEW LTD": qo.Link("NEW LTD", "exact", "7", ("7",), "")}
    profiles = {
        "7": {"previous_company_names": [{"name": "OLD LIMITED", "ceased_on": "2023-04-01"}]}
    }
    assert qo.classify_change(c, links, profiles)["class"] == "rename"


# R5


def test_r5_psc_summary_counts_and_never_returns_a_name():
    psc = {
        "items": [
            {
                "name": "Alice Example",
                "kind": "individual-person-with-significant-control",
                "notified_on": "2020-01-01",
            },
            {
                "name": "Holdco SARL",
                "kind": "corporate-entity-person-with-significant-control",
                "notified_on": "2021-01-01",
                "identification": {"country_registered": "Luxembourg"},
            },
            {
                "name": "Gone Ltd",
                "kind": "corporate-entity-person-with-significant-control",
                "notified_on": "2019-01-01",
                "ceased_on": "2020-06-01",
                "identification": {"country_registered": "England"},
            },
        ]
    }
    statements = {"items": [{"statement": "no-individual-or-entity-with-signficant-control"}]}
    out = qo.psc_summary(psc, statements)
    assert out["psc_total"] == 3 and out["psc_current"] == 2
    assert out["psc_current_corporate"] == 1 and out["psc_current_individual"] == 1
    assert out["psc_corporate_outside_uk"] == 1 and out["psc_earliest_notified_on"] == "2020-01-01"
    assert out["statements"] == ["no-individual-or-entity-with-signficant-control"]
    assert "Alice" not in str(out) and "Holdco" not in str(out)


# R6


def test_r6_charges_live_when_outstanding_or_part_satisfied():
    charges = {
        "items": [
            {
                "status": "outstanding",
                "created_on": "2024-03-01",
                "persons_entitled": [{"name": "Bank A"}],
            },
            {
                "status": "fully-satisfied",
                "created_on": "2020-01-01",
                "persons_entitled": [{"name": "Bank B"}],
            },
            {
                "status": "part-satisfied",
                "created_on": "2023-01-01",
                "persons_entitled": [{"name": "Bank A"}, {"name": "Trustee C"}],
            },
        ]
    }
    out = qo.charge_facts(charges)
    assert out["charged"] and out["charges_live"] == 2 and out["charges_total"] == 3
    assert (
        out["earliest_live_created_on"] == "2023-01-01"
        and out["latest_live_created_on"] == "2024-03-01"
    )
    assert out["chargees"] == ["Bank A", "Trustee C"]
    assert not qo.charge_facts({"items": []})["charged"] and not qo.charge_facts({})["charged"]


# Figures and falsifiers


def test_resolution_figure_and_f1_f2():
    all_names = {
        "A LTD": qo.Name("A LTD", 2, Decimal(100), {"1"}),
        "B LTD": qo.Name("B LTD", 1, Decimal(50), {"2"}),
        "C LTD": qo.Name("C LTD", 1, Decimal(50), {"3"}),
        "Someone": qo.Name("Someone", 1, Decimal(1), {"4"}),
    }
    links = {
        "A LTD": qo.Link("A LTD", "exact", "1", ("1",), ""),
        "B LTD": qo.Link("B LTD", "identity-guard", None, ("2",), ""),
        "C LTD": qo.Link("C LTD", "admitted", "3", ("3",), ""),
        "Someone": qo.Link("Someone", "unresolved", None, (), ""),
    }
    f = qo.resolution_figure(all_names, links)
    assert f["resolved_names"] == 2 and f["resolved_share_of_names"] == Decimal("0.500")
    assert f["by_class"]["no-suffix"]["names"] == 1 and f["by_class"]["exact"]["mw"] == Decimal(100)
    assert f["F1_fires"] is True
    assert f["identity_guard_share_of_rule_resolved"] == Decimal("0.500") and f["F2_fires"] is True
    assert qo.share(0, 0) is None and qo.share(1, 3) == Decimal("0.333")
