"""017 — the census rules, each as the frozen declaration states them."""

from datetime import date
from decimal import Decimal

from grid_mysteries.investigations import overdue_queue as oq

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
