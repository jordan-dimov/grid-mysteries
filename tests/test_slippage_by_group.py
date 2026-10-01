"""Investigation 021: 014's series cut by plant type and host TO."""

from datetime import date

from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import slippage_by_group as sbg


def row(name, stage, mw, eff, plant="Wind Onshore", host="NGET", customer="C", site="S"):
    return {
        "Project Name": name,
        "Customer Name": customer,
        "Connection Site": site,
        "Stage": stage,
        "MW Increase / Decrease": mw,
        "MW Effective From": date.fromisoformat(eff) if eff else None,
        "Plant Type": plant,
        "HOST TO": host,
    }


# ----------------------------------------------------------- schema pass


def test_unit_keys_align_row_by_row_with_entries():
    rows = [
        row("A", "1", 10, "2025-01-01"),
        row("A", "2", 20, "2026-01-01"),
        row("B", "", 5, "2025-06-01"),
        row("C", "", 5, "2025-06-01"),
        row("C", "", 7, "2025-07-01"),  # two rows, no distinct stage: numbered by date
    ]
    keys = cs.unit_keys(rows)
    assert len(keys) == len(rows)
    assert set(keys) == set(cs.entries(rows))
    assert keys[2].endswith("#1") and keys[3].endswith("#1") and keys[4].endswith("#2")


def test_tags_read_the_grouping_keys_as_printed_with_whitespace_collapsed():
    rows = [row("A", "1", 10, "2025-01-01", plant=" Energy  Storage System ", host=None)]
    tagged = sbg.tags(rows)
    (value,) = tagged.values()
    assert value == {"plant_type": "Energy Storage System", "host_to": ""}


def test_key_stability_counts_changes_of_a_unit_between_consecutive_copies():
    first = [row("A", "1", 10, "2025-01-01", plant="Wind Onshore", host="SPT")]
    second = [
        row("A", "1", 10, "2025-01-01", plant="Wind Onshore;Energy Storage System", host="SPT")
    ]
    third = [
        row("A", "1", 10, "2025-01-01", plant="Wind Onshore;Energy Storage System", host="SPT")
    ]
    out = sbg.key_stability(
        [(date(2024, 1, 1), first), (date(2024, 2, 1), second), (date(2024, 3, 1), third)]
    )
    assert out["matched_units_over_consecutive_copies"] == 2
    assert out["plant_type"]["units_changed"] == 1
    assert out["plant_type"]["transitions"] == [
        {"from": "Wind Onshore", "to": "Wind Onshore;Energy Storage System", "units": 1}
    ]
    assert out["host_to"]["units_changed"] == 0
    assert [c["t_public"] for c in out["copies_with_a_change"]] == ["2024-02-01"]
