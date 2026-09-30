from datetime import date
from decimal import Decimal

from grid_mysteries.investigations import energisation as en


def row(
    name="Alpha",
    customer="A LTD",
    site="S 400kV",
    status="Scoping",
    eff="30/06/2024",
    mw="100",
    stage="",
    pid="a0l4L0000005alpha",
    gate="",
    plant="Energy Storage System",
):
    return {
        "Project Name": name,
        "Customer Name": customer,
        "Connection Site": site,
        "Stage": stage,
        "MW Increase / Decrease": mw,
        "Cumulative Total Capacity (MW)": mw,
        "MW Effective From": eff,
        "Project Status": status,
        "Project ID": pid,
        "Gate": gate,
        "Plant Type": plant,
        "Agreement Type": "Direct Connection",
        "HOST TO": "NGET",
    }


def kept(*copies):
    """(regime, t_public, sha, rows, swapped) from (date, rows) pairs, one regime."""
    return [("new", d, f"sha{i}", rows, False) for i, (d, rows) in enumerate(copies)]


def test_transition_takes_the_date_printed_in_the_copy_before_built():
    seq = kept(
        (
            date(2024, 1, 5),
            [row(), row(name="Beta", pid="a0l4L0000005beta0", status="Built", eff="")],
        ),
        (
            date(2024, 3, 5),
            [
                row(eff="31/03/2024"),
                row(name="Beta", pid="a0l4L0000005beta0", status="Built", eff=""),
            ],
        ),
        (
            date(2024, 9, 5),
            [
                row(status="Built", eff=""),
                row(name="Beta", pid="a0l4L0000005beta0", status="Built", eff=""),
            ],
        ),
    )
    seen = en.sightings(seq)
    found = en.transitions(seen)
    by_name = {t.project_name: t for t in found}
    a = by_name["Alpha"]
    assert (
        a.klass == "transition"
        and a.first_built == date(2024, 9, 5)
        and a.last_before == date(2024, 3, 5)
    )
    assert (
        a.last_date_before_built == date(2024, 3, 31)
        and a.last_raw_date_before_built == "31/03/2024"
    )
    assert a.last_before_status == "Scoping" and a.date_at_first_built is None
    assert a.months_from_last_date_to_built_copy == Decimal("5.2")
    b = by_name["Beta"]
    assert (
        b.klass == "built-at-first-sight"
        and b.last_before is None
        and b.months_from_last_date_to_built_copy is None
    )


def test_a_unit_transitions_once_even_if_its_status_flaps():
    seq = kept(
        (date(2023, 1, 1), [row(eff="01/01/2023")]),
        (date(2023, 2, 1), [row(status="Built")]),
        (date(2023, 3, 1), [row(status="Scoping")]),
        (date(2023, 4, 1), [row(status="Built")]),
    )
    found = en.transitions(en.sightings(seq))
    assert len(found) == 1 and found[0].first_built == date(2023, 2, 1)
    assert found[0].months_from_last_date_to_built_copy == Decimal("1.0")


def test_a_renamed_unit_is_followed_by_content_identity_only_within_its_group():
    # Content identity groups by (name, customer, site); a different customer is a new unit,
    # so its Built is at first sight for that unit. This is 014's rule, recorded, not hidden.
    seq = kept(
        (date(2023, 1, 1), [row(eff="01/06/2023")]),
        (date(2023, 7, 1), [row(customer="B LTD", status="Built")]),
    )
    found = en.transitions(en.sightings(seq))
    assert [t.klass for t in found] == ["built-at-first-sight"]


def test_gate_two_rows_are_the_printed_twos_only():
    rows = [
        row(gate="2"),
        row(name="G1", gate="1"),
        row(name="Blank"),
        row(name="Two", gate="2", mw="50"),
    ]
    out = en.gate_two_rows(rows)
    assert [r["project_name"] for r in out] == ["Alpha", "Two"]
    assert out[1]["mw"] == Decimal("50") and out[0]["index"] == 0


def test_quantiles_and_summary():
    assert en.quantiles([]) == {
        "n": 0,
        "min": None,
        "p25": None,
        "median": None,
        "p75": None,
        "max": None,
    }
    q = en.quantiles([Decimal(x) for x in (5, 1, 3, 9, 7)])
    assert (q["min"], q["median"], q["max"]) == (Decimal(1), Decimal(5), Decimal(9))
    seq = kept(
        (
            date(2024, 1, 5),
            [
                row(eff="01/01/2024"),
                row(name="Beta", pid="a0l4L0000005beta0", eff=""),
                row(name="Gamma", pid="a0l4L0000005gamma", status="Built"),
            ],
        ),
        (
            date(2025, 1, 5),
            [
                row(status="Built"),
                row(name="Beta", pid="a0l4L0000005beta0", status="Built"),
                row(name="Gamma", pid="a0l4L0000005gamma", status="Built"),
            ],
        ),
    )
    s = en.summary(en.transitions(en.sightings(seq)))
    assert s["transitions"] == 3 and s["by_class"] == {"transition": 2, "built-at-first-sight": 1}
    assert s["measured"] == 1 and s["undated_before_built"] == 1
    assert (
        s["built_copy_later_than_six_months"] == 1 and s["by_year_of_built_copy"]["2025"]["n"] == 1
    )
    assert "Energy Storage System" in s["by_plant_type"]


# Amendment 1, A1


def test_a1_project_reference_date_is_the_latest_capacity_bearing_stage_date():
    seq = kept(
        (
            date(2024, 1, 5),
            [
                row(eff="30/06/2024", mw="100", stage="1"),
                row(eff="31/12/2026", mw="50", stage="2"),
                row(eff="30/06/2030", mw="0", stage="3"),
            ],
        ),
        (
            date(2024, 9, 5),
            [
                row(eff="", mw="100", stage="1", status="Built"),
                row(eff="31/12/2026", mw="50", stage="2", status="Built"),
                row(eff="30/06/2030", mw="0", stage="3", status="Built"),
            ],
        ),
    )
    seen = en.sightings(seq)
    found = en.project_transitions(seen, {"new": [date(2024, 1, 5), date(2024, 9, 5)]})
    assert len(found) == 1
    t = found[0]
    assert (
        t.klass == "transition"
        and t.reference_date == date(2026, 12, 31)
        and t.earliest_date == date(2024, 6, 30)
    )
    assert (
        t.capacity_mw == Decimal("150") and t.stages_zero_mw == 1 and t.stages_capacity_dated == 2
    )
    assert t.months_reference == Decimal("-27.8") and t.months_earliest == Decimal("2.2")
    s = en.project_summary(found)
    assert s["measured"] == 1 and s["built_copy_before_the_date"] == 1


def test_a1_labels_first_sight_undated_and_not_sighted_in_the_copy_before():
    seq = kept(
        (
            date(2024, 1, 5),
            [
                row(name="First", pid="a0l4L0000005first", status="Built"),
                row(name="Undated", pid="a0l4L0000005undat", eff="", mw="10"),
                row(name="Gap", pid="a0l4L0000005gap00", eff="01/01/2024", mw="10"),
            ],
        ),
        (
            date(2024, 5, 5),
            [
                row(name="First", pid="a0l4L0000005first", status="Built"),
                row(name="Undated", pid="a0l4L0000005undat", eff="", mw="10", status="Built"),
            ],
        ),
        (
            date(2024, 9, 5),
            [row(name="Gap", pid="a0l4L0000005gap00", eff="01/01/2024", mw="10", status="Built")],
        ),
    )
    found = en.project_transitions(
        en.sightings(seq), {"new": [date(2024, 1, 5), date(2024, 5, 5), date(2024, 9, 5)]}
    )
    assert {t.project_name: t.klass for t in found} == {
        "First": "built-at-first-sight",
        "Undated": "undated-before-built",
        "Gap": "not-sighted-in-copy-before",
    }


def test_a1_prime_splits_later_stages_and_measures_twice():
    seq = kept(
        (
            date(2024, 1, 5),
            [
                row(eff="30/06/2024", mw="100", stage="1"),
                row(eff="31/12/2026", mw="50", stage="2"),
                row(eff="30/06/2030", mw="0", stage="3"),
            ],
        ),
        (
            date(2024, 9, 5),
            [
                row(eff="", mw="100", stage="1", status="Built"),
                row(eff="31/12/2026", mw="50", stage="2", status="Built"),
                row(eff="30/06/2030", mw="0", stage="3", status="Built"),
            ],
        ),
    )
    order = {"new": [date(2024, 1, 5), date(2024, 9, 5)]}
    found = en.project_stages(en.sightings(seq), order)
    assert len(found) == 1
    t = found[0]
    assert [(s.stage, s.mw, s.later) for s in t.stages] == [
        ("1", Decimal("100"), False),
        ("2", Decimal("50"), True),
    ]
    assert t.klass == "transition" and t.later_mw == Decimal("50")
    # With the later stage: amendment 1's A1 exactly (the test above).
    assert t.months_with == en.project_transitions(en.sightings(seq), order)[0].months_reference
    assert t.months_with == Decimal("-27.8") and t.months_without == Decimal("2.2")
    s = en.stages_summary(found)
    assert s["projects_with_later_stages"] == 1 and s["later_stages_mw"] == Decimal("50")
    assert s["with_later_stages"]["built_copy_before_the_date"] == 1
    assert s["without_later_stages"]["built_copy_before_the_date"] == 0
    assert s["median_difference_without_minus_with"] == Decimal("30.0")
    assert s["moved_from_negative_to_non_negative"] == ["new|name:alpha|a ltd|s 400kv"]


def test_a1_prime_only_later_stages_has_no_second_measure():
    seq = kept(
        (date(2024, 1, 5), [row(eff="31/12/2026", mw="50", stage="2")]),
        (date(2024, 9, 5), [row(eff="31/12/2026", mw="50", stage="2", status="Built")]),
    )
    found = en.project_stages(en.sightings(seq), {"new": [date(2024, 1, 5), date(2024, 9, 5)]})
    (t,) = found
    assert t.klass == "only-later-stages" and t.months_without is None
    s = en.stages_summary(found)
    assert s["only_later_stages"] == 1
    assert s["with_later_stages"]["measured"] == 1 and s["without_later_stages"]["measured"] == 0
