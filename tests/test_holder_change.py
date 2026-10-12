"""023 (3f22f02f…): did projects that changed hands slip more."""

import random
from datetime import date
from decimal import Decimal

from grid_mysteries.investigations import holder_change as hc
from grid_mysteries.investigations import queue_ownership as qo
from grid_mysteries.sources.tec_register import parse_date

B, C = date(2024, 7, 19), date(2025, 7, 22)


def link(name, number):
    return qo.Link(name, "exact", number, (number,), "", qo.RULE_VERSION_V2)


def test_boundaries_are_the_runs_changing_between_the_ends():
    runs = [
        {"t_public": "2023-01-01", "name": "A LTD", "last_t_public": "2024-08-01"},
        {"t_public": "2024-08-05", "name": "B LTD", "last_t_public": "2025-08-01"},
        {"t_public": "2025-08-05", "name": "C LTD", "last_t_public": "2026-09-29"},
    ]
    assert hc.boundaries(runs, B, C) == [("A LTD", "B LTD", "2024-08-05")]
    early = [
        {"t_public": "2023-01-01", "name": "A LTD", "last_t_public": "2024-01-01"},
        {"t_public": "2024-01-05", "name": "B LTD"},
    ]
    assert hc.boundaries(early, B, C) == []


def test_ends_class_follows_019_r4_on_the_end_names():
    links = {
        "A LTD": link("A LTD", "1"),
        "B LTD": link("B LTD", "2"),
        "A LIMITED": link("A LIMITED", "1"),
    }
    assert hc.ends_class("p", {"A LTD"}, {"A LTD"}, B, C, links, {}, {})["class"] == hc.SAME_NAME
    assert hc.ends_class("p", {"A LTD"}, {"B LTD"}, B, C, links, {}, {})["class"] == hc.TRANSFER
    assert hc.ends_class("p", {"A LTD"}, {"A LIMITED"}, B, C, links, {}, {})["class"] == hc.RENAME
    assert hc.ends_class("p", {"A LTD"}, {"Z"}, B, C, links, {}, {})["class"] == hc.NOT_DETERMINABLE
    assert (
        hc.ends_class("p", {"A LTD", "B LTD"}, {"A LTD"}, B, C, links, {}, {})["class"]
        == hc.SEVERAL_NAMES
    )


def test_a_name_with_several_holders_resolves_at_the_end_that_prints_it():
    links = {
        "SHARED": qo.Link("SHARED", "unresolved", None, (), "", qo.RULE_VERSION_V2),
        "B LTD": link("B LTD", "2"),
    }
    admitted = {
        "SHARED": {
            "name": "SHARED",
            "decision": "admitted",
            "holders": [
                {"company_number": "2", "from": "2020-01-01", "until": "2025-01-01"},
                {"company_number": "9", "from": "2025-01-01"},
            ],
        }
    }
    # On the baseline (2024) SHARED was company 2, as is B LTD: a rename.
    assert (
        hc.ends_class("p", {"SHARED"}, {"B LTD"}, B, C, links, admitted, {})["class"] == hc.RENAME
    )


def row(pid, stage, mw, status, effective, plant="Wind Onshore"):
    return {
        "Project ID": pid,
        "Stage": stage,
        "MW Increase / Decrease": mw,
        "Project Status": status,
        "MW Effective From": effective,
        "Plant Type": plant,
        "Customer Name": "X",
    }


def read(r):
    return parse_date(r.get("MW Effective From"))


def test_stages_keep_only_the_declared_rows_and_count_the_rest():
    rows_b = [
        row("a", "1", "50", "Scoping", "2026-01-01"),
        row("a", "2", "0", "Scoping", "2026-01-01"),
        row("b", "", "20", "Built", "2020-01-01"),
        row("c", "", "20", "Scoping", ""),
        row("d", "", "20", "Scoping", "2027-01-01"),
        row("d", "", "30", "Scoping", "2027-06-01"),
        row("e", "", "10", "Scoping", "2027-01-01"),
        row("gone", "", "10", "Scoping", "2027-01-01"),
        row("x", "", "10", "Scoping", "2027-01-01"),
    ]
    rows_c = [
        row("a", "1.0", "50", "Awaiting Consents", "2027-01-01"),
        row("a", "2", "0", "Scoping", "2026-01-01"),
        row("b", "", "20", "Built", "2020-01-01"),
        row("c", "", "20", "Scoping", "2028-01-01"),
        row("d", "", "20", "Scoping", "2027-01-01"),
        row("e", "", "10", "Scoping", "2026-06-01"),
        row("x", "", "10", "Scoping", "2027-01-01"),
    ]
    moves, dropped = hc.stages(rows_b, rows_c, read, read, lambda pid: pid != "x")
    assert [(m.project_id, m.stage, m.days) for m in moves] == [("a", "1", 365), ("e", "", -214)]
    assert dropped == {
        "duplicate key at baseline": 2,
        "duplicate key at current": 0,
        "not at the current end": 1,
        "MW not above zero at baseline": 1,
        "Built at baseline": 1,
        "undated at an end": 1,
        "id not printed on 2026-09-29": 1,
    }


def move(pid, days, mw="10", status="Scoping", plant="Wind Onshore"):
    b = date(2026, 1, 1)
    return hc.StageMove(
        pid, "", Decimal(mw), status, plant, b, date.fromordinal(b.toordinal() + days)
    )


def test_the_measure_months_mw_years_and_direction():
    m = move("a", 365, mw="100")
    assert (
        m.months == Decimal("12.0") and m.mw_years == Decimal("99.932") and m.direction == "later"
    )
    assert move("a", 0).direction == "unchanged" and move("a", -1).direction == "earlier"


def test_standardised_weights_strata_by_the_exposed_groups_mix():
    exposed = [move("e1", 10), move("e2", 0), move("e3", 10, status="Consents Approved")]
    reference = [move("r1", 0), move("r2", 0), move("r3", 10, status="Consents Approved")]
    # Scoping: 1/2 vs 0/2, weight 2/3; Consents Approved: 1/1 vs 1/1, weight 1/3.
    assert hc.standardised(exposed, reference)["difference"] == Decimal(2) / 3 * Decimal("0.5")
    only = [move("e4", 5, status="Under Construction")]
    assert hc.standardised(only, reference) == {
        "difference": None,
        "exposed_outside_shared_strata": 1,
    }


def test_contrast_is_deterministic_under_its_seed_and_resamples_ids():
    exposed = [move(f"e{i}", 30 * (i % 3)) for i in range(12)]
    reference = [move(f"r{i}", 30 * (i % 5 == 0)) for i in range(20)]
    a = hc.contrast(exposed, reference, random.Random(hc.SEED), resamples=200)
    b = hc.contrast(exposed, reference, random.Random(hc.SEED), resamples=200)
    assert a == b
    assert a["crude_share_later_difference"] == "0.467"
    lo, hi = (Decimal(x) for x in a["crude_share_later_ci95"])
    assert lo <= Decimal("0.467") <= hi


def test_group_summary_counts_ids_and_shares():
    s = hc.group_summary([move("a", 10), move("a", 0), move("b", -5)])
    assert s["ids"] == 2 and s["stages"] == 3
    assert s["shares"]["later"]["k"] == 1 and s["shares"]["unchanged"]["k"] == 1
