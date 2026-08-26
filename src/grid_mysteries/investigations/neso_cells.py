"""Daily comparison cells against NESO's skip methodology.

Method Study 001B declared the comparison cell as (settlement date,
direction, NGC unit) with an *opportunity intensity*: the sum over
settlement periods of the unit's largest qualifying gap that period
(GBP/MWh·periods, a declared monotone proxy). 001C and 001D reuse the
same construction, so it lives here rather than being imported across
study directories.
"""

from decimal import Decimal

Cell = tuple[str, str, str]  # settlement date, direction, NGC unit


def intensity_by_cell(
    alternative_rows: list[dict], elexon_to_ngc: dict[str, str]
) -> tuple[dict[Cell, Decimal], dict[Cell, Decimal]]:
    """(naive, post-filter) opportunity intensity per cell."""
    per_period_naive: dict[tuple, Decimal] = {}
    per_period_post: dict[tuple, Decimal] = {}
    for r in alternative_rows:
        ngc = elexon_to_ngc.get(r["bm_unit"], r["bm_unit"])
        key = (r["settlement_date"], r["direction"], ngc, r["settlement_period"])
        gap = Decimal(r["max_gap_gbp_per_mwh"])
        per_period_naive[key] = max(per_period_naive.get(key, Decimal(0)), gap)
        if r["classification"] != "non_deliverable":
            per_period_post[key] = max(per_period_post.get(key, Decimal(0)), gap)

    naive: dict[Cell, Decimal] = {}
    post: dict[Cell, Decimal] = {}
    for (day, direction, ngc, _period), gap in per_period_naive.items():
        naive[(day, direction, ngc)] = naive.get((day, direction, ngc), Decimal(0)) + gap
    for (day, direction, ngc, _period), gap in per_period_post.items():
        post[(day, direction, ngc)] = post.get((day, direction, ngc), Decimal(0)) + gap
    return naive, post
