"""017 — the census rules, each as the frozen declaration states them."""

from datetime import date
from decimal import Decimal
from typing import Any

from grid_mysteries.investigations import overdue_queue as oq
from grid_mysteries.rendering import overdue_queue as page

AS_OF = date(2026, 9, 15)


def row(
    name: str,
    effective: object,
    status: str = "Awaiting Consents",
    mw: object = "100",
    *,
    plant: str = "CCGT (Combined Cycle Gas Turbine)",
    pid: str = "",
    stage: str = "",
) -> dict[str, object]:
    return {
        "Project Name": name,
        "Customer Name": "A Customer",
        "Connection Site": "A Site 400kV",
        "Stage": stage,
        "MW Increase / Decrease": mw,
        "Cumulative Total Capacity (MW)": "9999",
        "MW Effective From": effective,
        "Project Status": status,
        "Plant Type": plant,
        "Project ID": pid,
        "Project Number": "PRO-0001",
    }


def test_past_its_date_is_strictly_before_the_copys_own_publication_date():
    """R2: the boundary is the copy's publication date, and it is strict."""
    result = oq.census(
        [
            row("Yesterday", "14/09/2026"),
            row("On the day", "15/09/2026"),
            row("Tomorrow", "16/09/2026"),
        ],
        AS_OF,
    )
    assert [r.project_name for r in result["rows"]] == ["Yesterday"]
    assert result["dated_not_built_future"] == 2


def test_built_is_excluded_and_every_other_spelling_is_not():
    """R4: case and whitespace are ignored, and only `built` is Built."""
    rows = [
        row("A", "01/10/2020", "Built"),
        row("B", "01/10/2020", "  BUILT  "),
        row("C", "01/10/2020", "Under Construction/Commissioning"),
        row("D", "01/10/2020", "Consents Approved"),
        row("E", "01/10/2020", ""),
    ]
    result = oq.census(rows, AS_OF)
    assert result["dated_built"] == 2
    assert [r.project_name for r in result["rows"]] == ["C", "D", "E"]
    assert [g["status"] for g in result["by_status"]] == [
        "",
        "Consents Approved",
        "Under Construction/Commissioning",
    ]


def test_an_undated_row_is_never_guessed_and_is_outside_the_census():
    """R3: blank and unparseable cells are undated, not overdue."""
    result = oq.census(
        [row("Blank", ""), row("Nonsense", "soon"), row("Dated", "01/10/2020")], AS_OF
    )
    assert result["undated"] == 2
    assert result["dated"] == 1
    assert result["selected_rows"] == 1


def test_a_missing_capacity_is_absent_and_a_zero_is_a_row_with_no_capacity():
    """R5: blank MW is excluded from totals; a parseable 0 is counted as a row."""
    result = oq.census(
        [
            row("Has MW", "01/10/2020", mw="380"),
            row("Zero MW", "01/10/2020", mw="0"),
            row("No MW", "01/10/2020", mw=""),
        ],
        AS_OF,
    )
    assert result["selected_rows"] == 3
    assert result["selected_mw"] == Decimal("380")
    assert result["selected_rows_zero_capacity"] == 1
    assert result["selected_rows_without_capacity"] == 1


def test_the_cumulative_column_is_never_the_measure():
    """R5: the measure is the stage's own TEC, never the cumulative total."""
    result = oq.census([row("P", "01/10/2020", mw="451")], AS_OF)
    assert result["selected_mw"] == Decimal("451")


def test_the_row_is_the_unit_and_a_repeated_project_id_is_published_both_ways():
    """R6: rows count once; ids are counted once too, keeping the largest."""
    rows = [
        row("Platform A", "01/10/2024", mw="540", pid="a0l8e0000011zBpAAI"),
        row("Platform B", "01/10/2024", mw="540", pid="a0l8e0000011zBp"),
        row("Elsewhere", "01/10/2024", mw="200", pid="a0l4L0000005ihQQAQ"),
    ]
    result = oq.census(rows, AS_OF)
    assert result["selected_rows"] == 3
    assert result["selected_mw"] == Decimal("1280")
    assert result["distinct_project_ids"] == 2
    assert result["selected_mw_largest_per_id"] == Decimal("740")
    assert [g["project_id"] for g in result["repeated_project_ids"]] == ["a0l8e0000011zBp"]


def test_a_row_without_a_project_id_cannot_be_shown_to_share_one():
    """R6: it stands alone, and the count of such rows is published."""
    result = oq.census([row("A", "01/10/2024", mw="10"), row("B", "01/10/2024", mw="20")], AS_OF)
    assert result["distinct_project_ids"] == 2
    assert result["selected_rows_without_project_id"] == 2
    assert result["selected_mw_largest_per_id"] == Decimal("30")


def test_compound_plant_types_are_kept_whole():
    """R7: the register prints compound types; a grouping never re-spells them."""
    compound = "CCGT (Combined Cycle Gas Turbine);Energy Storage System"
    result = oq.census(
        [
            row("A", "01/10/2024", mw="100", plant=compound),
            row("B", "01/10/2024", mw="50", plant="Energy Storage System"),
        ],
        AS_OF,
    )
    assert [g["plant_type"] for g in result["by_plant_type"]] == [
        compound,
        "Energy Storage System",
    ]


def test_breakdowns_by_year_are_in_year_order_and_the_earliest_are_first():
    """R7: the year table reads forwards; the earliest rows head the list."""
    rows = [
        row("New", "01/10/2025", mw="10"),
        row("Old", "01/10/2020", mw="20"),
        row("Middle", "01/10/2023", mw="30"),
    ]
    result = oq.census(rows, AS_OF)
    assert [g["year"] for g in result["by_year"]] == [2020, 2023, 2025]
    assert [r.project_name for r in result["earliest"]] == ["Old", "Middle", "New"]


def test_the_scale_line_covers_every_row_dated_on_or_after_the_as_of_date():
    """R7: including Built ones, and the Scoping share of them."""
    rows = [
        row("Future scoping", "01/10/2030", "Scoping", mw="500"),
        row("Future consented", "01/10/2030", "Consents Approved", mw="300"),
        row("Future built", "01/10/2030", "Built", mw="100"),
        row("Past", "01/10/2020", mw="50"),
    ]
    result = oq.census(rows, AS_OF)
    assert result["scale"]["mw_dated_on_or_after_as_of"] == Decimal("900")
    assert result["scale"]["mw_scoping_dated_on_or_after_as_of"] == Decimal("500")
    assert result["scale"]["rows_dated_on_or_after_as_of"] == 3


def test_the_swap_sensitivity_counts_the_dates_that_could_read_the_other_way():
    """R3: a day of 12 or less has a second reading; 13 or more has none."""
    rows = [
        row("Swappable to the future", "01/10/2020", mw="380"),
        row("Swappable, still past", "03/04/2019", mw="20"),
        row("Unambiguous", "30/10/2020", mw="100"),
    ]
    result = oq.census(rows, AS_OF)
    sens = result["swap_sensitivity"]
    assert sens["rows_with_a_swapped_reading"] == 2
    assert sens["rows_swapped_reading_not_past"] == 0
    assert sens["mw_swapped_reading_not_past"] == Decimal(0)
    assert result["rows"][0].effective_swapped == date(2020, 1, 10)
    assert result["rows"][2].effective_swapped is None


def test_f1_fires_when_swapping_would_move_more_than_a_fifth_to_the_future():
    rows = [
        # 10 January 2026 as printed; read the other way round it is
        # 1 October 2026, which is not past the as-of date at all.
        row("Would be future", "10/01/2026", mw="300"),
        row("Solid", "30/10/2020", mw="100"),
    ]
    result = oq.census(rows, AS_OF)
    assert result["rows"][0].effective == date(2026, 1, 10)
    assert result["rows"][0].effective_swapped == date(2026, 10, 1)
    key = "F1 swapped dates could move more than a fifth of the selected MW to the future"
    assert result["falsifiers"][key] is True


def test_f3_fires_when_the_two_readings_of_the_unit_diverge():
    rows = [
        row("A", "01/10/2024", mw="500", pid="dup"),
        row("B", "01/10/2024", mw="500", pid="dup"),
    ]
    result = oq.census(rows, AS_OF)
    key = "F3 the two readings of the unit differ by more than a tenth"
    assert result["falsifiers"][key] is True
    assert result["selected_mw"] == Decimal("1000")
    assert result["selected_mw_largest_per_id"] == Decimal("500")


def test_the_four_classes_partition_every_row():
    """C2 and C3: nothing is double counted and nothing falls out."""
    rows = [
        row("Overdue", "01/10/2020"),
        row("Future", "01/10/2030"),
        row("Built", "01/10/2020", "Built"),
        row("Undated", ""),
        row("Built future", "01/10/2030", "Built"),
    ]
    result = oq.census(rows, AS_OF)
    assert all(result["checks"].values())
    assert result["selected_rows"] == 1
    assert result["dated_not_built_future"] == 1
    assert result["dated_built"] == 2
    assert result["undated"] == 1


def test_the_exhibit_matcher_separates_the_gas_plant_from_what_shared_its_name():
    assert oq.names_a_gas_turbine_plant("CCGT")
    assert oq.names_a_gas_turbine_plant("HYBRID")
    assert oq.names_a_gas_turbine_plant(
        "CCGT (Combined Cycle Gas Turbine);Energy Storage System;OCGT (Open Cycle Gas Turbine)"
    )
    assert not oq.names_a_gas_turbine_plant("Coal")
    assert not oq.names_a_gas_turbine_plant("Energy Storage System;PV Array (Photo Voltaic/solar)")
    assert not oq.names_a_gas_turbine_plant("")


def test_status_trace_reports_every_status_a_bundles_rows_were_published_under():
    extracts = [
        {
            "t_public": "2018-11-08",
            "rows": [
                {"Project status": "Built", "Plant type": "Coal"},
                {"Project status": "Awaiting Consents", "Plant type": "CCGT"},
            ],
        },
        {
            "t_public": "2020-04-09",
            "rows": [{"Project status": "Awaiting Consents", "Plant type": "HYBRID"}],
        },
    ]
    trace = oq.status_trace(extracts, lambda r: oq.names_a_gas_turbine_plant(r["Plant type"]))
    assert trace == {
        "Awaiting Consents": {
            "rows": 2,
            "copies": ["2018-11-08", "2020-04-09"],
            "first_copy": "2018-11-08",
            "last_copy": "2020-04-09",
        }
    }


def test_two_stage_rows_in_one_copy_are_two_rows_but_one_copy():
    """A project split into stages publishes two rows per copy, and two
    bundles may consult the same copy; the copies are what aggregates."""
    extracts = [
        {
            "t_public": "2026-09-15",
            "rows": [
                {"Project status": "Awaiting Consents", "Plant type": "CCGT;OCGT"},
                {"Project status": "Awaiting Consents", "Plant type": "CCGT;OCGT"},
            ],
        }
    ]
    matcher = lambda r: oq.names_a_gas_turbine_plant(r["Plant type"])  # noqa: E731
    trace = oq.status_trace(extracts, matcher)
    assert trace["Awaiting Consents"]["rows"] == 2
    assert trace["Awaiting Consents"]["copies"] == ["2026-09-15"]
    assert oq.distinct_copies([trace, trace]) == ["2026-09-15"]


# ------------------------------------------------- version 2: the Gate column


def gated(
    name: str,
    effective: object,
    gate: str,
    status: str = "Scoping",
    mw: object = "100",
    pid: str = "",
    stage: str = "",
    site: str = "A Site 400kV",
) -> dict[str, object]:
    row_ = row(name, effective, status, mw, pid=pid, stage=stage)
    row_["Gate"] = gate
    row_["Connection Site"] = site
    return row_


def gate_run(
    rows: list[dict[str, object]], copies: list[tuple[str, list[dict[str, object]]]] | None = None
) -> dict:
    return oq.gate_census(rows, oq.census(rows, AS_OF), copies or [])


def test_the_register_prints_1_and_2_and_the_mapping_is_the_only_interpretation():
    """R9/R10: 1 and 2 map to the tiers; a blank maps to nothing and is
    never folded into a tier; an unknown value maps to nothing either."""
    assert oq.tier_of("1") == "Gate 1"
    assert oq.tier_of("2") == "Gate 2"
    assert oq.tier_of("") is None
    assert oq.tier_of("3") is None
    assert oq.gate_of({"Gate": " 2 "}) == "2"
    assert oq.gate_of({"Gate": None}) == ""
    assert oq.gate_of({}) == ""


def test_the_whole_copy_and_the_overdue_rows_are_both_split_by_gate():
    """G1 and G2, over the same rows, with the blank kept as its own class."""
    rows = [
        gated("Overdue confirmed", "01/10/2024", "2", mw="500"),
        gated("Overdue provisional", "01/10/2024", "1", mw="100"),
        gated("Overdue blank", "01/10/2024", "", mw="50"),
        gated("Future confirmed", "01/10/2030", "2", mw="900"),
    ]
    result = gate_run(rows)
    assert {g["gate"]: (g["rows"], g["mw"]) for g in result["g1_copy_by_gate"]} == {
        "2": (2, Decimal("1400")),
        "1": (1, Decimal("100")),
        "": (1, Decimal("50")),
    }
    overdue = {g["gate"]: g for g in result["g2_overdue_by_gate"]}
    assert overdue["2"]["rows"] == 1
    assert overdue["2"]["mw"] == Decimal("500")
    assert overdue["2"]["tier"] == "Gate 2"
    assert overdue[""]["tier"] is None
    assert result["confirmed_tier_overdue_rows"] == 1
    assert result["confirmed_tier_overdue_mw"] == Decimal("500")


def test_shares_are_always_a_row_share_and_a_capacity_share():
    """R11: the two are computed separately and neither stands for the other."""
    rows = [
        gated("Big overdue", "01/10/2024", "2", mw="900"),
        gated("Small overdue", "01/10/2024", "1", mw="100"),
        gated("Big future", "01/10/2030", "2", mw="9100"),
    ]
    confirmed = next(g for g in gate_run(rows)["g2_overdue_by_gate"] if g["gate"] == "2")
    assert confirmed["row_share_of_overdue"] == Decimal("0.5")
    assert confirmed["capacity_share_of_overdue"] == Decimal("0.9")
    assert confirmed["row_share_of_its_gate"] == Decimal("0.5")
    assert confirmed["capacity_share_of_its_gate"] == Decimal("0.09")
    assert oq.share(1, 0) is None


def test_the_gate_and_status_cross_tab_shows_which_statuses_sit_in_the_tier():
    """G3: the sharpest line in the piece has to come from a table."""
    rows = [
        gated("Scoping in the tier", "01/10/2024", "2", "Scoping", mw="500"),
        gated("Consented in the tier", "01/10/2024", "2", "Consents Approved", mw="300"),
        gated("Scoping outside", "01/10/2024", "", "Scoping", mw="20"),
    ]
    cross = gate_run(rows)["g3_overdue_by_gate_and_status"]
    assert [(c["gate"], c["status"], c["rows"], c["mw"]) for c in cross] == [
        ("", "Scoping", 1, Decimal("20")),
        ("2", "Scoping", 1, Decimal("500")),
        ("2", "Consents Approved", 1, Decimal("300")),
    ]


def test_a_shared_name_is_not_a_shared_entry_and_both_are_published():
    """G5: two rows of one name with different ids are two entries; the
    census says so and reports both readings."""
    rows = [
        gated("Platform", "01/10/2024", "2", mw="540", pid="a0l0000000000aa"),
        gated("Platform", "01/10/2024", "2", mw="540", pid="a0l0000000000bb"),
        gated("Twinned", "01/10/2024", "2", mw="200", pid="a0l0000000000cc", stage="1"),
        gated("Twinned", "01/10/2024", "2", mw="300", pid="a0l0000000000cc", stage="2"),
    ]
    g5 = gate_run(rows)["g5_repetition"]
    assert [g["key"] for g in g5["sharing_a_project_id"]] == ["a0l0000000000cc"]
    assert [g["key"] for g in g5["sharing_a_project_name"]] == ["platform", "twinned"]
    by_id = g5["sharing_a_project_id"][0]
    assert by_id["mw_summed"] == Decimal("500")
    assert by_id["mw_largest"] == Decimal("300")


def test_f5_fires_when_repetition_holds_more_than_a_tenth_of_the_tier():
    rows = [
        gated("Twin", "01/10/2024", "2", mw="500", pid="dup", stage="1"),
        gated("Twin", "01/10/2024", "2", mw="500", pid="dup", stage="2"),
    ]
    result = gate_run(rows)
    key = "F5 repeated ids or names hold more than a tenth of the overdue Gate 2 MW"
    assert result["falsifiers"][key] is True


def test_f4_fires_on_a_gate_value_the_pinned_definition_does_not_cover():
    rows = [gated("Odd", "01/10/2024", "3", mw="10")]
    result = gate_run(rows)
    assert result["unknown_gate_values"] == ["3"]
    key = "F4 the Gate column carries a value the pinned definition does not cover"
    assert result["falsifiers"][key] is True
    assert result["confirmed_tier_overdue_rows"] == 0


def test_f6_fires_when_too_few_gated_copies_are_readable():
    rows = [gated("A", "01/10/2024", "2", mw="10")]
    key = "F6 fewer than three gated copies are readable"
    assert gate_run(rows, [])["falsifiers"][key] is True
    three = [("2026-05-19", rows), ("2026-08-22", rows), ("2026-09-15", rows)]
    assert gate_run(rows, three)["falsifiers"][key] is False


def test_g6_reports_each_gated_copys_reading_and_never_guesses_an_absence():
    """The only evidence on whether a confirmed date was carried in already
    past, or set and then passed (R12)."""
    now = gated("P", "12/04/2026", "2", "Scoping", mw="500", pid="a0l0000000000aa")
    older = gated("P", "12/04/2026", "", "Scoping", mw="500", pid="a0l0000000000aa")
    moved = gated("P", "01/12/2026", "2", "Scoping", mw="500", pid="a0l0000000000aa")
    result = gate_run(
        [now],
        [("2026-05-19", [older]), ("2026-08-22", [moved]), ("2026-09-15", [now])],
    )
    entry = result["g4_confirmed_tier_overdue"][0]
    assert [(r.t_public, r.found, r.gate, r.effective_as_published) for r in entry.readings] == [
        ("2026-05-19", True, "", "12/04/2026"),
        ("2026-08-22", True, "2", "01/12/2026"),
        ("2026-09-15", True, "2", "12/04/2026"),
    ]
    absent = gate_run([now], [("2026-05-19", []), ("2026-09-15", [now])])
    first = absent["g4_confirmed_tier_overdue"][0].readings[0]
    assert first.found is False and first.effective is None and first.gate == ""


def test_the_matching_rule_is_the_project_id_with_the_stage():
    """Inherited from R6; the name and site are the fallback when a row
    carries no id, which on this copy never happens."""
    with_id = gated("A", "01/10/2024", "2", pid="a0l0000000000aaAAA", stage="1.0")
    assert oq.identity_key(with_id) == ("id:a0l0000000000aa", "1")
    without = gated("A", "01/10/2024", "2", stage="2", site="Some GSP")
    assert oq.identity_key(without) == ("name:a|some gsp", "2")


def test_g6_says_whether_the_date_had_already_passed_when_the_tier_was_set():
    """R12: the only question the four copies can answer. A row whose cell
    first reads the confirmed tier in a copy published after its date was
    assessed into the tier already carrying a date in the past."""
    now = gated("Late already", "23/02/2024", "2", mw="40", pid="a0l0000000000aa")
    before = gated("Late already", "23/02/2024", "", mw="40", pid="a0l0000000000aa")
    result = gate_run(
        [now],
        [("2026-05-19", [before]), ("2026-08-22", [now]), ("2026-09-15", [now])],
    )
    entry = result["g4_confirmed_tier_overdue"][0]
    assert entry.first_copy_in_the_tier == "2026-08-22"
    assert entry.date_when_first_in_the_tier == date(2024, 2, 23)
    assert entry.already_past_when_first_in_the_tier is True
    assert result["g6_summary"]["rows_whose_date_had_already_passed_when_first_in_the_tier"] == 1

    # A row gated while its date was still ahead of it is the other story.
    ahead = gated("Gated early", "30/10/2026", "2", mw="10", pid="a0l0000000000bb")
    ahead_before = gated("Gated early", "30/10/2026", "", mw="10", pid="a0l0000000000bb")
    passed = gated("Gated early", "30/06/2026", "2", mw="10", pid="a0l0000000000bb")
    second = gate_run(
        [passed],
        [("2026-05-19", [ahead_before]), ("2026-08-22", [ahead]), ("2026-09-15", [passed])],
    )
    row_ = second["g4_confirmed_tier_overdue"][0]
    assert row_.already_past_when_first_in_the_tier is False
    assert row_.dates_across_gated_copies == (date(2026, 6, 30), date(2026, 10, 30))
    assert second["g6_summary"]["rows_whose_gated_copies_publish_more_than_one_date"] == 1


def test_a_gated_copy_that_publishes_a_date_in_the_future_is_flagged():
    """The register printing one row's date two ways is the difference
    between a row being overdue and not being overdue at all, so the census
    reports the alternative reading and what the tier looks like without it."""
    now = gated("Ambiguous", "12/04/2026", "2", mw="500", pid="a0l0000000000aa")
    iso = gated("Ambiguous", "2026-12-04", "", mw="500", pid="a0l0000000000aa")
    other = gated("Plain", "30/10/2025", "2", mw="100", pid="a0l0000000000bb")
    result = gate_run(
        [now, other],
        [("2026-05-19", [iso, other]), ("2026-08-22", [now, other]), ("2026-09-15", [now, other])],
    )
    entry = next(g for g in result["g4_confirmed_tier_overdue"] if g.project_name == "Ambiguous")
    assert entry.dates_across_gated_copies_not_past == (date(2026, 12, 4),)
    assert entry.a_not_past_date_is_the_day_month_swap is True
    summary = result["g6_summary"]
    assert summary["rows_a_gated_copy_publishes_as_not_past"] == 1
    assert summary["mw_a_gated_copy_publishes_as_not_past"] == Decimal("500")
    assert summary["mw_if_those_rows_are_read_as_not_past"] == Decimal("100")
    assert summary["rows_if_those_rows_are_read_as_not_past"] == 1

    plain = next(g for g in result["g4_confirmed_tier_overdue"] if g.project_name == "Plain")
    assert plain.dates_across_gated_copies_not_past == ()
    assert plain.a_not_past_date_is_the_day_month_swap is False


def test_the_scoping_slot_carries_its_qualifiers_and_lists_only_projects():
    """G3 and G4 are declared breakdowns, so the figure is promoted rather
    than computed anew; the two readings and the per-row form of the
    'already past on entering the tier' finding travel with it, and no
    customer name leaves the repository."""
    census: dict[str, Any] = {
        "as_of": "2026-09-15",
        "rows_total": 2200,
        "copy": {"sha256": "d" * 64},
        "status_counts_all_rows": {"Scoping": 1484},
        "scale": {"rows_scoping_dated_on_or_after_as_of": 1449},
    }
    gate: dict[str, Any] = {
        "declaration_sha256": "8" * 64,
        "g2_overdue_by_gate": [{"gate": "2", "rows": 3, "mw": "600"}],
        "g4_confirmed_tier_overdue": [
            {
                "project_name": "Contested",
                "status": "Scoping",
                "mw": "300",
                "effective_as_published": "12/04/2026",
                "already_past_when_first_in_the_tier": True,
                "dates_across_gated_copies_not_past": ["2026-12-04"],
            },
            {
                "project_name": "Plain",
                "status": "Scoping",
                "mw": "100",
                "effective_as_published": "30/10/2025",
                "already_past_when_first_in_the_tier": True,
                "dates_across_gated_copies_not_past": [],
            },
            {
                "project_name": "Elsewhere",
                "status": "Consents Approved",
                "mw": "200",
                "effective_as_published": "30/10/2025",
                "already_past_when_first_in_the_tier": True,
                "dates_across_gated_copies_not_past": [],
            },
        ],
    }
    slot = page._scoping_slot(census, gate)["gb-tec-gate2-overdue-scoping-2026-09"]
    assert slot["rows"] == 2
    assert slot["value"] == Decimal("400")
    assert [r["project"] for r in slot["the_rows"]] == ["Contested", "Plain"]
    assert all(
        set(r) == {"project", "mw", "effective_from_as_printed", "status"} for r in slot["the_rows"]
    )
    travels = " ".join(slot["must_travel_with_the_claim"])
    assert "For each of these 2 rows individually" in travels
    assert "100 MW over 1 rows" in travels
    assert "1,484 of its 2,200 rows" in travels

    # If the finding did not hold for every one of them, the slot says so.
    gate["g4_confirmed_tier_overdue"][1]["already_past_when_first_in_the_tier"] = False
    weaker = page._scoping_slot(census, gate)["gb-tec-gate2-overdue-scoping-2026-09"]
    assert "holds for the wider set but not for every one" in (
        " ".join(weaker["must_travel_with_the_claim"])
    )


def test_a_correction_is_inserted_after_the_line_it_governs_and_the_text_is_kept():
    md = "# T\n\n**Claim that says too much.** More.\n\nNext paragraph."
    fixed = page.apply_corrections(
        md, [{"date": "2026-09-24", "after": "**Claim", "markdown": "> **Correction.** Narrower."}]
    )
    assert fixed == (
        "# T\n\n**Claim that says too much.** More.\n\n"
        "> **Correction.** Narrower.\n\nNext paragraph."
    )
    assert page.apply_corrections(md, None) == md


def test_a_correction_whose_anchor_is_missing_or_ambiguous_stops_the_render():
    import pytest

    for md in ("no anchor here", "**Claim a\n**Claim b"):
        with pytest.raises(ValueError):
            page.apply_corrections(md, [{"date": "d", "after": "**Claim", "markdown": "x"}])


def test_inline_markdown_escapes_text_and_lets_emphasis_run_across_code():
    assert page.inline_html("**reads `2`.** <b> & *say it*") == (
        "<strong>reads <code>2</code>.</strong> &lt;b&gt; &amp; <em>say it</em>"
    )
    assert page.inline_html("`a **not bold** <x>`") == "<code>a **not bold** &lt;x&gt;</code>"


def test_block_markdown_covers_what_findings_uses():
    html = page.markdown_html(
        "## H\n\npara one\ncontinues\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "> quote\n\n- x\n- y\n\n```\ncode <1>\n```"
    )
    assert "<h2>H</h2>" in html
    assert "<p>para one continues</p>" in html
    assert "<th>a</th><th>b</th>" in html and "<td>1</td><td>2</td>" in html
    assert "<blockquote><p>quote</p></blockquote>" in html
    assert "<ul><li>x</li><li>y</li></ul>" in html
    assert "<pre><code>code &lt;1&gt;</code></pre>" in html


def _page_inputs():
    census = {"as_of": "2026-09-15", "selected_rows": 98, "distinct_project_ids": 96}
    gate = {
        "g2_overdue_by_gate": [
            {"gate": "1", "rows": 7, "rows_in_copy": 756},
            {
                "gate": "2",
                "rows": 17,
                "rows_in_copy": 95,
                "row_share_of_its_gate": "0.1789",
                "capacity_share_of_its_gate": "0.1847",
            },
        ],
        "g6_summary": {
            "rows_a_gated_copy_publishes_as_not_past": 2,
            "rows_if_those_rows_are_read_as_not_past": 15,
        },
    }
    return census, gate


def test_the_page_leads_on_the_row_share_with_the_capacity_share_and_the_other_reading():
    census, gate = _page_inputs()
    findings = "# 017\n\n" + "\n\n".join(page.EXHIBIT_SUPPORT)
    html = page.render_page(findings, census, gate, next_declaration=("D-v3.md", "ab" * 32))
    lead = html[html.index('<p class="headline">') :]
    assert lead.index("17.9% of the tier's entries") < lead.index("18.5% of its capacity")
    assert "on that reading it is 15 entries" in html
    assert "98 entries (96 distinct project ids)" in html
    assert "D-v3.md" in html and "abababababababab…" in html
    assert "<h1>017</h1>" not in html


def test_the_page_refuses_when_findings_no_longer_supports_its_exhibit_sentence():
    import pytest

    census, gate = _page_inputs()
    with pytest.raises(ValueError):
        page.render_page("# 017\n\nnothing about Eggborough", census, gate)


# --------------------------------------------------------------- version 3

REF_AS_OF = date(2026, 9, 25)
NEXT_AS_OF = date(2026, 9, 29)


def test_the_filename_date_is_read_and_never_sets_the_as_of_date():
    """R2′: NESO's filename names a day; the as-of date stays last_modified."""
    assert oq.filename_date("tec-register-24-september-2026.csv") == date(2026, 9, 24)
    assert oq.filename_date("tec-register-28-September-2026.csv") == date(2026, 9, 28)
    assert oq.filename_date("tec-register.csv") is None
    assert oq.filename_date("tec-register-31-february-2026.csv") is None
    result = oq.census([row("A", "24/09/2026")], REF_AS_OF)
    assert result["as_of"] == REF_AS_OF


def test_the_filename_sensitivity_counts_rows_past_on_one_reading_only():
    """R2′: dated on or after the filename's date and before the as-of date."""
    result = oq.census(
        [
            row("Before both", "23/09/2026", mw="10"),
            row("On the filename day", "24/09/2026", mw="30"),
            row("On the as-of day", "25/09/2026", mw="50"),
        ],
        REF_AS_OF,
    )
    sens = oq.filename_sensitivity(result, date(2026, 9, 24))
    assert sens["differs"] is True
    assert [r.project_name for r in sens["moved"]] == ["On the filename day"]
    assert (sens["rows"], sens["mw"]) == (1, Decimal(30))
    same = oq.filename_sensitivity(result, REF_AS_OF)
    assert (same["differs"], same["rows"]) == (False, 0)
    assert oq.filename_sensitivity(result, None)["rows"] == 0


def test_f10_fires_when_the_filename_reading_moves_more_than_a_tenth():
    """F10: more than a tenth of the selected MW moves, so publish a range."""
    key = "F10 the filename reading moves more than a tenth of the selected MW"
    rows = [row("Old", "01/01/2025", mw="89"), row("Edge", "24/09/2026", mw="11")]
    result = oq.census(rows, REF_AS_OF)
    assert oq.filename_sensitivity(result, date(2026, 9, 24))[key] is True
    rows = [row("Old", "01/01/2025", mw="90"), row("Edge", "24/09/2026", mw="10")]
    result = oq.census(rows, REF_AS_OF)
    assert oq.filename_sensitivity(result, date(2026, 9, 24))[key] is False


def test_the_next_copy_is_the_earliest_on_or_after_the_date_and_gaps_are_named():
    """R1′: earliest last_modified on or after 29/09; a day with no TEC
    record between that date and the capture day is reported."""
    entries = [
        {"t_public": "2026-09-25", "fetched_at": "2026-09-26T06:31:03+00:00", "sha256": "a"},
        {"t_public": "2026-10-02", "fetched_at": "2026-10-03T06:31:03+00:00", "sha256": "c"},
        {"t_public": "2026-09-29", "fetched_at": "2026-09-30T06:31:04+00:00", "sha256": "b"},
    ]
    chosen = oq.next_copy(entries)
    assert chosen is not None and chosen["sha256"] == "b"
    assert oq.next_copy(entries[:1]) is None
    days = {date(2026, 9, 29), date(2026, 10, 1)}
    assert oq.capture_gaps(days, date(2026, 9, 29), date(2026, 10, 1)) == [date(2026, 9, 30)]
    assert oq.capture_gaps(days | {date(2026, 9, 30)}, date(2026, 9, 29), date(2026, 9, 30)) == []


def _copy_report(**over: Any) -> dict[str, Any]:
    report = {
        "columns": ["B", "A"],
        "date_spellings": {"uk": 10, "blank": 2, "iso-dash": 0, "other": 0},
        "project_status": {"Scoping": 5, "Built": 7},
        "gate": {"": 3, "1": 4, "2": 5},
        "flags": [],
    }
    return {**report, **over}


def test_n0_gates_the_next_census_on_its_schema_pass():
    """N0: same columns, uk and blank dates only, the five statuses, 1, 2 and
    blank under Gate, and no flag, or no census of that copy."""
    assert all(oq.n0(_copy_report(), ["A", "B"]).values())
    failing = {
        "N0 the same fifteen columns": _copy_report(columns=["A", "B", "C"]),
        "N0 date spellings only uk and blank": _copy_report(
            date_spellings={"uk": 10, "blank": 2, "iso-dash": 1}
        ),
        "N0 only the five Project Status spellings": _copy_report(
            project_status={"Scoping": 5, "Withdrawn": 1}
        ),
        "N0 only 1, 2 and blank under Gate": _copy_report(gate={"": 3, "3": 1}),
        "N0 no flag": _copy_report(flags=["row count fell 40% (possible partial export)"]),
    }
    for name, report in failing.items():
        verdict = oq.n0(report, ["A", "B"])
        assert verdict[name] is False, name
        assert sum(not ok for ok in verdict.values()) == 1, name


def test_g6_prime_reads_one_copy_per_digest_up_to_the_copy_under_census():
    """G6′: version 2's gated copies, then captured copies later than 15/09
    and no later than the copy under census, one reading per digest."""
    journalled = [
        {"t_public": "2026-08-22", "sha256": "j1"},
        {"t_public": "2026-09-15", "sha256": "same"},
    ]
    captured = [
        {"t_public": "2026-09-15", "sha256": "same"},
        {"t_public": "2026-09-18", "sha256": "c1"},
        {"t_public": "2026-09-25", "sha256": "c2"},
        {"t_public": "2026-09-29", "sha256": "c3"},
    ]
    since = date(2026, 9, 15)
    got = oq.gated_copies_for(journalled, captured, since, REF_AS_OF)
    assert [c["sha256"] for c in got] == ["j1", "same", "c1", "c2"]
    got = oq.gated_copies_for(journalled, captured, since, since)
    assert [c["sha256"] for c in got] == ["j1", "same"]


def _pair(ref_rows: list[dict[str, object]], next_rows: list[dict[str, object]]) -> Any:
    ref, nxt = oq.census(ref_rows, REF_AS_OF), oq.census(next_rows, NEXT_AS_OF)
    return oq.transitions(ref_rows, ref, next_rows, nxt), ref, nxt


def test_d2_classes_every_selected_row_and_the_classes_sum():
    """D2 and C11: in both; reference only (no row, Built, date later, other);
    next only ((a) new key, (b) the date arrived, (c) other)."""
    ref_rows = [
        row("Stays", "01/01/2025", pid="a0lSTAYS0000001"),
        row("Goes", "01/01/2025", pid="a0lGOES00000001", mw="10"),
        row("Built later", "01/01/2025", pid="a0lBUILT0000001", mw="20"),
        row("Moved later", "01/01/2025", pid="a0lMOVED0000001", mw="30"),
        row("Blanked", "01/01/2025", pid="a0lBLANK0000001", mw="40"),
        row("Arrives", "27/09/2026", pid="a0lARRIVE000001", mw="50"),
        row("Moved earlier", "01/12/2026", pid="a0lEARLY0000001", mw="60"),
    ]
    next_rows = [
        row("Stays", "01/01/2025", pid="a0lSTAYS0000001", mw="120"),
        row("Built later", "01/01/2025", "Built", pid="a0lBUILT0000001", mw="20"),
        row("Moved later", "01/01/2027", pid="a0lMOVED0000001", mw="30"),
        row("Blanked", "", pid="a0lBLANK0000001", mw="40"),
        row("Arrives", "27/09/2026", pid="a0lARRIVE000001", mw="50"),
        row("Moved earlier", "01/06/2026", pid="a0lEARLY0000001", mw="60"),
        row("New", "01/01/2026", pid="a0lNEW000000001", mw="70"),
    ]
    d2, ref, nxt = _pair(ref_rows, next_rows)
    names = {
        k: sorted((t.reference or t.next).project_name for t in v["members"])
        for k, v in d2["classes"].items()
    }
    assert names == {
        "in both": ["Stays"],
        "reference only: no row with that key": ["Goes"],
        "reference only: Built": ["Built later"],
        "reference only: date on or after the next as-of date": ["Moved later"],
        "reference only: other": ["Blanked"],
        "next only: (a) no row with that key in the reference copy": ["New"],
        "next only: (b) the date arrived": ["Arrives"],
        "next only: (c) other": ["Moved earlier"],
    }
    both = d2["classes"]["in both"]
    assert (both["mw_reference"], both["mw_next"]) == (Decimal(100), Decimal(120))
    assert d2["checks"]["C11 D2's classes sum to each census's selected rows and MW"] is True
    assert d2["classed_totals"]["reference"] == {"rows": 5, "mw": ref["selected_mw"]}
    assert d2["classed_totals"]["next"] == {"rows": 4, "mw": nxt["selected_mw"]}
    blanked = d2["classes"]["reference only: other"]["members"][0]
    assert (blanked.other_status, blanked.other_effective) == ("Awaiting Consents", None)


def test_d2_puts_a_key_on_two_rows_of_either_copy_in_no_class():
    """D2: an ambiguous key is listed, never classed; C11 counts it beside
    the classes so the totals still meet."""
    ref_rows = [
        row("Twice", "01/01/2025", pid="a0lTWICE0000001", mw="10"),
        row("Twice", "01/01/2026", pid="a0lTWICE0000001", mw="20"),
        row("Once", "01/01/2025", pid="a0lONCE00000001", mw="5"),
    ]
    next_rows = [
        row("Twice", "01/01/2025", pid="a0lTWICE0000001", mw="10"),
        row("Once", "01/01/2025", pid="a0lONCE00000001", mw="5"),
    ]
    d2, _ref, _nxt = _pair(ref_rows, next_rows)
    assert d2["ambiguous"]["keys"] == ["id:a0lTWICE0000001 | stage (blank)"]
    assert len(d2["ambiguous"]["reference_rows"]) == 2
    assert len(d2["ambiguous"]["next_rows"]) == 1
    assert list(d2["classes"]) == ["in both"]
    assert d2["checks"]["C11 D2's classes sum to each census's selected rows and MW"] is True


def test_f9_fires_when_more_than_a_tenth_of_a_copys_rows_cannot_be_matched():
    """F9: ambiguous or id-less selected rows above a tenth of either copy's
    selection withhold D2, leaving D1 alone."""
    key = "F9 more than a tenth of either copy's selected rows are ambiguous or have no id"
    matched = [row(f"R{i}", "01/01/2025", pid=f"a0lROW{i:09d}") for i in range(9)]
    d2, _r, _n = _pair([*matched, row("No id", "01/01/2025")], matched)
    assert d2["falsifiers"][key] is False
    d2, _r, _n = _pair(
        [*matched, row("No id", "01/01/2025"), row("No id 2", "01/01/2025")], matched
    )
    assert d2["unmatchable_rows"]["reference"] == 2
    assert d2["falsifiers"][key] is True


def test_d1_prints_each_copy_and_the_difference_with_both_as_of_dates():
    """D1: side by side, next minus reference, with both as-of dates."""
    ref_rows = [{**row("A", "01/01/2025", pid="a0lA00000000001", mw="100"), "Gate": "2"}]
    next_rows = [
        {**row("A", "01/01/2025", pid="a0lA00000000001", mw="100"), "Gate": "2"},
        {**row("B", "27/09/2026", pid="a0lB00000000001", mw="40"), "Gate": "1"},
        {**row("C", "01/01/2027", "Scoping", pid="a0lC00000000001", mw="7"), "Gate": ""},
    ]
    ref, nxt = oq.census(ref_rows, REF_AS_OF), oq.census(next_rows, NEXT_AS_OF)
    ref_gate, next_gate = oq.gate_census(ref_rows, ref, []), oq.gate_census(next_rows, nxt, [])
    d1 = oq.side_by_side((ref, ref_gate), (nxt, next_gate))
    diff = d1["difference_next_minus_reference"]
    assert d1["as_of_dates"] == [REF_AS_OF, NEXT_AS_OF]
    assert d1["days_between"] == 4
    assert (diff["selected_rows"], diff["selected_mw"]) == (1, Decimal(40))
    assert (diff["gate2_overdue_rows"], diff["gate2_overdue_mw"]) == (0, Decimal(0))
    assert diff["mw_scoping_dated_on_or_after_as_of"] == Decimal(7)
