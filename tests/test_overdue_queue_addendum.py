"""017 addendum — storage classification, duration buckets and the
illustration, over committed evidence lines rather than register rows."""

from datetime import date
from decimal import Decimal

from grid_mysteries.investigations import overdue_queue_addendum as add

AS_OF = date(2026, 9, 15)


def line(index: int, plant: str, effective: str, mw: str | None = "10", **extra: object) -> dict:
    return {
        "index": index,
        "project_name": f"Project {index}",
        "plant_type": plant,
        "status": "Scoping",
        "mw": mw,
        "effective": effective,
        "effective_swapped": None,
        **extra,
    }


def test_storage_class_is_the_registers_token_and_nothing_else():
    assert add.storage_class("Energy Storage System") == add.STORAGE_ONLY
    assert add.storage_class("Energy Storage System;PV Array (Photo Voltaic/solar)") == (
        add.STORAGE_COMPOUND
    )
    assert add.storage_class("PV Array;  Energy   Storage System ") == add.STORAGE_COMPOUND
    assert add.storage_class("Wind Onshore") == add.NOT_STORAGE
    # A name saying BESS is not a plant type saying storage.
    assert add.storage_class("Reactive Compensation") == add.NOT_STORAGE
    assert add.storage_class("Demand;PV Array (Photo Voltaic/solar)") == add.NOT_STORAGE
    assert add.storage_class("") == add.NOT_STORAGE
    assert add.storage_class("energy storage system") == add.NOT_STORAGE


def test_buckets_are_inclusive_at_their_upper_bound_and_open_ended_at_the_top():
    assert add.bucket(0) == "up to 90 days"
    assert add.bucket(90) == "up to 90 days"
    assert add.bucket(91) == "91 to 365 days"
    assert add.bucket(365) == "91 to 365 days"
    assert add.bucket(366) == "366 to 730 days"
    assert add.bucket(730) == "366 to 730 days"
    assert add.bucket(731) == "more than 730 days"
    assert add.bucket(5000) == "more than 730 days"


def test_days_behind_is_counted_from_the_copys_own_date():
    assert add.days_behind(date(2026, 9, 14), AS_OF) == 1
    assert add.days_behind(date(2024, 9, 15), AS_OF) == 730


def test_storage_rows_keep_only_storage_and_carry_the_gate_only_where_committed():
    committed = [
        line(1, "Energy Storage System", "2026-08-31", "50"),
        line(2, "Wind Onshore", "2026-08-31", "60"),
        line(3, "Energy Storage System;PV Array (Photo Voltaic/solar)", "2024-01-01", "25"),
        line(4, "Energy Storage System", "2025-01-01", None),
    ]
    gate_rows = [{"index": 1, "gate": "2"}]
    rows = add.storage_rows(committed, AS_OF, gate_rows)
    assert [r.index for r in rows] == [1, 4, 3]  # storage-only first, heaviest first
    assert rows[0].gate == "2"
    assert rows[1].gate is None  # not "blank": version 2 committed no cell for it
    assert rows[2].storage_class == add.STORAGE_COMPOUND
    assert rows[1].mw is None
    assert add.total_mw(rows) == Decimal("75")


def test_duration_distribution_counts_rows_and_mw_per_bucket_and_gives_the_median():
    committed = [
        line(1, "Energy Storage System", "2026-09-14", "1"),
        line(2, "Energy Storage System", "2026-01-01", "2"),
        line(3, "Energy Storage System", "2024-01-01", "4"),
    ]
    rows = add.storage_rows(committed, AS_OF, [])
    dist = add.duration_distribution(rows)
    assert dist["rows"] == 3 and dist["mw"] == Decimal("7")
    assert dist["days_behind_min"] == 1
    assert dist["days_behind_median"] == 257
    assert dist["days_behind_max"] == 988
    assert [(b["bucket"], b["rows"], b["mw"]) for b in dist["buckets"]] == [
        ("up to 90 days", 1, Decimal("1")),
        ("91 to 365 days", 1, Decimal("2")),
        ("366 to 730 days", 0, Decimal("0")),
        ("more than 730 days", 1, Decimal("4")),
    ]


def test_illustration_is_rate_times_mw_as_decimal():
    out = add.illustration(Decimal("100.5"), [Decimal("3000"), Decimal("25000")])
    assert out[0]["gbp"] == Decimal("301500.0")
    assert out[1]["gbp"] == Decimal("2512500.0")
    assert isinstance(out[1]["gbp"], Decimal)


def test_addendum_reports_unreadable_plant_types_and_swapped_readings():
    committed = [
        line(1, "Energy Storage System", "2026-04-12", "500", effective_swapped="2026-12-04"),
        line(2, "", "2026-01-01", "5"),
        line(3, "Energy Storage System", "2026-07-31", "50", effective_swapped=None),
    ]
    out = add.addendum(committed, AS_OF, [{"index": 1, "gate": "2"}], [Decimal("3000")])
    obs = out["observation"]
    assert obs["committed_rows"] == 3 and obs["committed_mw"] == Decimal("555")
    assert obs["rows_with_no_readable_plant_type"] == 1
    assert obs["storage_rows"] == 2 and obs["storage_mw"] == Decimal("550")
    assert obs["storage_rows_swapped_reading_in_future"] == 1
    assert obs["storage_mw_swapped_reading_in_future"] == Decimal("500")
    assert obs["confirmed_tier_storage_rows"] == 1
    assert obs["gate_not_in_committed_evidence_rows"] == 1
    assert out["illustration"]["storage_only"][0]["gbp"] == Decimal("1650000")
    assert out["illustration"]["confirmed_tier_storage"][0]["gbp"] == Decimal("1500000")
