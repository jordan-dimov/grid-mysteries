from datetime import date
from decimal import Decimal as D

from hypothesis import given
from hypothesis import strategies as st

from grid_mysteries.investigations import connection_slippage as cs


def row(name="Wind A", customer="Co", site="Site", stage="", mw="100", eff="2027-10-30", cum=None):
    return {
        "Project Name": name,
        "Customer Name": customer,
        "Connection Site": site,
        "Stage": stage,
        "MW Increase / Decrease": mw,
        "Cumulative Total Capacity (MW)": cum if cum is not None else mw,
        "MW Effective From": eff,
    }


def vintage(t, rows, sha="0" * 64):
    return cs.VintageInput(t_public=t, rows=tuple(rows), sha256=sha, path=f"v/{t}")


# ------------------------------------------------------------------- entries


def test_identity_is_the_normalised_triple_and_stage_unifies_numeric_spellings():
    a = cs.entries([row(stage="1.00")])
    b = cs.entries([row(stage="1")])
    c = cs.entries([row(stage="")])
    assert list(a) == list(b) == list(c) == ["name:wind a|co|site#1"]
    assert list(cs.entries([row(name="Wind  A ", customer="CO.", site="SITE")])) == list(a)


def test_rows_sharing_an_identity_without_distinct_stages_are_numbered_by_date():
    e = cs.entries([row(eff="2029-10-30", mw="50"), row(eff="2027-10-30", mw="30")])
    assert e["name:wind a|co|site#1"].effective == date(2027, 10, 30)
    assert e["name:wind a|co|site#2"].effective == date(2029, 10, 30)


def test_swapped_reading_applies_only_to_ambiguous_dates():
    e = cs.entries([row(eff="2021-01-05"), row(name="B", eff="2025-10-31")], swapped=True)
    assert e["name:wind a|co|site#1"].effective == date(2021, 5, 1)
    assert e["name:b|co|site#1"].effective == date(2025, 10, 31)


# ----------------------------------------------------------------- pairwise


def pair(b_rows, c_rows):
    return cs.compare(
        cs.entries(b_rows),
        cs.entries(c_rows),
        baseline_date=date(2024, 1, 1),
        current_date=date(2025, 1, 1),
    )


def test_headline_is_baseline_mw_times_years_moved_later_positive():
    p = pair([row(mw="100", eff="2027-10-30")], [row(mw="100", eff="2028-10-30")])
    assert p.mw_years_net == D("100.205")  # 366 days / 365.25 × 100 MW
    assert p.mw_years_later == D("100.205") and p.mw_years_earlier == D("0.000")
    assert (p.matched, p.dated_both, p.later, p.earlier, p.unchanged) == (1, 1, 1, 0, 0)


def test_an_advance_is_negative_and_net_can_hide_it_so_gross_sides_are_kept():
    p = pair(
        [row(name="A", mw="100", eff="2027-10-30"), row(name="B", mw="100", eff="2027-10-30")],
        [row(name="A", mw="100", eff="2028-10-30"), row(name="B", mw="100", eff="2026-10-30")],
    )
    assert p.mw_years_later == D("100.205")
    assert p.mw_years_earlier == D("-99.932")  # 365 days back
    assert p.mw_years_net == D("0.273")
    assert (p.later, p.earlier) == (1, 1)


def test_capacity_changes_never_enter_the_headline_the_baseline_mw_weighs():
    p = pair([row(mw="100", eff="2027-10-30")], [row(mw="300", eff="2028-10-30")])
    assert p.mw_years_net == D("100.205")
    assert p.capacity_changed == 1 and p.capacity_delta_mw == D("200.00")


def test_new_entries_and_removals_are_reconciliation_items_not_headline():
    p = pair(
        [row(name="A", mw="100", eff="2027-10-30"), row(name="Gone", mw="40", eff="2027-10-30")],
        [row(name="A", mw="100", eff="2027-10-30"), row(name="New", mw="70", eff="2035-10-30")],
    )
    assert p.mw_years_net == D("0.000")
    assert (p.new_entries, p.new_mw) == (1, D("70.00"))
    assert (p.removed, p.removed_mw) == (1, D("40.00"))
    assert p.baseline_units == p.matched + p.removed
    assert p.current_units == p.matched + p.new_entries


def test_a_rename_is_a_removal_plus_a_new_entry_never_repaired():
    p = pair([row(customer="Old Co", eff="2027-10-30")], [row(customer="New Co", eff="2029-10-30")])
    assert p.matched == 0 and p.removed == 1 and p.new_entries == 1
    assert p.mw_years_net == D("0.000")


def test_undated_and_unweighted_units_are_counted_and_contribute_nothing():
    p = pair(
        [
            row(name="A", mw="100", eff=""),
            row(name="B", mw="", eff="2027-10-30"),
            row(name="C", mw="0", eff="2027-10-30"),
        ],
        [
            row(name="A", mw="100", eff="2028-10-30"),
            row(name="B", mw="", eff="2028-10-30"),
            row(name="C", mw="0", eff="2028-10-30"),
        ],
    )
    assert p.undated == 1
    assert p.unweighted == 2
    assert p.dated_both == 2
    assert p.mw_years_net == D("0.000")


def test_negative_stage_mw_weighs_by_its_absolute_value():
    p = pair([row(mw="-100", eff="2027-10-30")], [row(mw="-100", eff="2028-10-30")])
    assert p.mw_years_net == D("100.205")
    assert p.weighted_mw == D("100.00")


@given(
    st.lists(
        st.tuples(st.integers(0, 60), st.integers(1, 500), st.integers(-400, 400)),
        min_size=0,
        max_size=40,
    )
)
def test_reconciliation_identity_holds_for_any_population(units):
    b_rows, c_rows = [], []
    for i, (kind, mw, shift) in enumerate(units):
        base = date(2028, 1, 1)
        if kind % 3 != 0:
            b_rows.append(row(name=f"P{i}", mw=str(mw), eff=base.isoformat()))
        if kind % 3 != 1:
            c_rows.append(
                row(
                    name=f"P{i}",
                    mw=str(mw),
                    eff=(base + __import__("datetime").timedelta(days=shift)).isoformat(),
                )
            )
    p = pair(b_rows, c_rows)
    assert p.baseline_units == p.matched + p.removed
    assert p.current_units == p.matched + p.new_entries
    assert p.matched == p.dated_both + p.undated
    assert p.dated_both == p.later + p.earlier + p.unchanged
    assert p.mw_years_net == p.mw_years_later + p.mw_years_earlier


def test_f1_and_f2_flags_follow_the_declared_shares():
    base = [row(name=f"P{i}") for i in range(10)]
    churned = base[:8] + [row(name="N1"), row(name="N2")]  # 2 left + 2 joined = 40% of 10
    assert pair(base, churned).f1_churn is True
    mild = base[:9] + [row(name="N1")]  # 2 of 10 = 20%, not over
    assert pair(base, mild).f1_churn is False
    thin = base[:4]  # 4 matched of 10 baseline units
    assert pair(base, thin).f2_thin is True
    assert pair(base, base[:5]).f2_thin is False


# ---------------------------------------------------------------- swap test


def test_swap_test_flags_a_vintage_whose_disagreements_are_mostly_swaps():
    prev = cs.entries(
        [row(name=f"P{i}", eff="2027-12-01") for i in range(4)] + [row(name="X", eff="2027-12-01")]
    )
    cur_rows = [row(name=f"P{i}", eff="2027-01-12") for i in range(4)] + [
        row(name="X", eff="2029-12-01")
    ]
    test = cs.swap_test(prev, cs.entries(cur_rows))
    assert test == cs.SwapTest(disagreements=5, swap_explained=4, flagged=True)
    unflagged = cs.swap_test(
        prev, cs.entries([row(name=f"P{i}", eff="2027-01-12") for i in range(2)])
    )
    assert unflagged.flagged is False  # fewer than three explained


# ------------------------------------------------------------------- series


def test_year_earlier_baseline_is_the_latest_vintage_at_least_365_days_back():
    dates = [date(2023, 1, 1), date(2023, 6, 1), date(2024, 1, 1), date(2024, 1, 2)]
    assert cs.year_earlier_baseline(dates, date(2024, 1, 1)) == date(2023, 1, 1)
    assert cs.year_earlier_baseline(dates, date(2024, 6, 1)) == date(2023, 6, 1)
    assert cs.year_earlier_baseline(dates, date(2024, 5, 31)) == date(2023, 6, 1)  # leap year
    assert cs.year_earlier_baseline(dates, date(2023, 12, 1)) is None


def test_series_splits_at_the_regime_cutoff_and_chains_nothing_across_it():
    vintages = [
        vintage(date(2024, 1, 5), [row(eff="2027-10-30")]),
        vintage(date(2024, 7, 5), [row(eff="2028-10-30")]),
        vintage(date(2025, 1, 10), [row(eff="2029-10-30")]),
        vintage(date(2025, 7, 22), [row(eff="2029-10-30")]),
        vintage(date(2026, 5, 19), [row(eff="2031-10-30")]),
        vintage(date(2026, 8, 25), [row(eff="2031-10-30")]),
    ]
    out = cs.series(vintages)
    assert [s["regime"] for s in out["segments"]] == ["old", "new"]
    old, new = out["segments"]
    assert old["vintages"] == 4 and new["vintages"] == 2
    assert new["rows"][0]["vs_previous"] is None  # first of its segment: no chain from 2025-07-22
    assert out["regime_break"] == {
        "last_old": date(2025, 7, 22),
        "first_new": date(2026, 5, 19),
        "days": 301,
    }
    assert old["holes"] == [
        {"from": date(2024, 1, 5), "to": date(2024, 7, 5), "days": 182},
        {"from": date(2024, 7, 5), "to": date(2025, 1, 10), "days": 189},
        {"from": date(2025, 1, 10), "to": date(2025, 7, 22), "days": 193},
    ]
    # the headline is the last old-regime row against its year-earlier baseline
    assert out["headline"]["t_public"] == date(2025, 7, 22)
    assert out["headline"]["baseline"] == date(2024, 7, 5)
    assert out["headline"]["mw_years_net"] == D("99.932")  # 2028-10-30 -> 2029-10-30: 365 days
    # cumulative chain within the old segment: two one-year moves
    assert old["rows"][-1]["cumulative_mw_years_net"] == D("200.137")  # 366 + 365 days


def test_annual_windows_run_first_vintage_of_year_to_first_of_next_and_mark_partial():
    vintages = [
        vintage(date(2024, 1, 5), [row(eff="2027-10-30")]),
        vintage(date(2024, 12, 20), [row(eff="2027-10-30")]),
        vintage(date(2025, 1, 3), [row(eff="2028-10-30")]),
        vintage(date(2025, 7, 22), [row(eff="2029-10-30")]),
    ]
    annual = cs.series(vintages)["segments"][0]["annual"]
    assert [(a["year"], a["baseline"], a["current"], a["partial"]) for a in annual] == [
        (2024, date(2024, 1, 5), date(2025, 1, 3), False),
        (2025, date(2025, 1, 3), date(2025, 7, 22), True),
    ]
    assert annual[0]["mw_years_net"] == D("100.205")


def test_a_swapped_vintage_is_read_swapped_so_no_movement_is_manufactured():
    base = [row(name=f"P{i}", eff="2027-12-01") for i in range(4)]
    swapped = [row(name=f"P{i}", eff="2027-01-12") for i in range(4)]
    out = cs.series(
        [
            vintage(date(2024, 1, 5), base),
            vintage(date(2024, 1, 9), swapped),
            vintage(date(2024, 1, 12), base),
        ]
    )
    rows = out["segments"][0]["rows"]
    assert rows[1]["swap_test"]["flagged"] is True
    assert rows[1]["vs_previous"]["mw_years_net"] == D("0.000")
    assert rows[2]["swap_test"]["flagged"] is False
    assert rows[2]["vs_previous"]["mw_years_net"] == D("0.000")
    assert out["segments"][0]["swapped_vintages"] == [date(2024, 1, 9)]


def test_propositions_are_decided_by_their_instances_or_stay_undecided():
    vintages = [
        vintage(date(2023, 1, 5), [row(eff="2027-10-30")]),
        vintage(date(2024, 1, 5), [row(eff="2028-10-30")]),
        vintage(date(2025, 1, 5), [row(eff="2028-06-30")]),
        vintage(date(2025, 7, 22), [row(eff="2028-06-30")]),
    ]
    props = cs.series(vintages)["propositions"]
    assert props["P1"]["windows"] == [2023, 2024]
    assert props["P1"]["failing_years"] == [2024]
    assert props["P1"]["verdict"] == "fails"
    assert props["P2"]["verdict"] == "undecided" and props["P2"]["decided_on"] is None
    new = [
        vintage(date(2026, 5, 19), [row(eff="2031-10-30")]),
        vintage(date(2026, 8, 25), [row(eff="2032-10-30")]),
        vintage(date(2027, 5, 19), [row(eff="2032-10-30")]),
    ]
    p2 = cs.series(new)["propositions"]["P2"]
    assert p2["decided_on"] == date(2027, 5, 19)
    assert p2["verdict"] == "holds" and p2["chained_mw_years_net"] == D("100.205")
    assert cs.series(vintages)["propositions"]["P1"]["verdict"] == "fails"
    assert cs.series([vintages[-1]])["propositions"]["P1"]["verdict"] == "undecided"
