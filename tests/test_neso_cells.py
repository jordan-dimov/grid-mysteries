from decimal import Decimal

from grid_mysteries.investigations.neso_cells import intensity_by_cell


def row(unit: str, period: int, gap: str, classification: str = "not_ruled_out") -> dict:
    return {
        "settlement_date": "2026-08-06",
        "settlement_period": period,
        "direction": "bid",
        "bm_unit": unit,
        "max_gap_gbp_per_mwh": gap,
        "classification": classification,
    }


def test_intensity_takes_period_max_then_sums_across_periods() -> None:
    rows = [
        row("E_UNIT-1", 10, "5"),  # two pairs in one period: max wins
        row("E_UNIT-1", 10, "8"),
        row("E_UNIT-1", 11, "2"),  # second period adds
    ]

    naive, post = intensity_by_cell(rows, {"E_UNIT-1": "UNIT-NGC"})

    cell = ("2026-08-06", "bid", "UNIT-NGC")
    assert naive[cell] == Decimal("10")
    assert post[cell] == Decimal("10")


def test_non_deliverable_rows_count_only_toward_naive() -> None:
    rows = [
        row("E_UNIT-1", 10, "8", classification="non_deliverable"),
        row("E_UNIT-1", 11, "2"),
    ]

    naive, post = intensity_by_cell(rows, {})

    cell = ("2026-08-06", "bid", "E_UNIT-1")  # unmapped units keep their id
    assert naive[cell] == Decimal("10")
    assert post[cell] == Decimal("2")
