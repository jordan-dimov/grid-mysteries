"""013's fourth proposition, T4 (`DECLARATION-T4.md`): NESO's Constraints
figure as a share of the two cuts rises with the wind share of accepted bid
volume.

Decided once, on the falsifier date, by Spearman's rank correlation over the
qualifying days; before that date only the count of qualifying days is
reported, so nobody can stop early on a good run. The comparison with the
threshold is exact (ranks are Fractions and rho >= 1/2 is tested without a
square root); the rho printed beside the verdict is rounded for display
only. Pure over tracker rows: no I/O, no clock.
"""

from datetime import date
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Any, Final

WINDOW_START: Final = date(2026, 9, 16)
FALSIFIER_DATE: Final = date(2027, 3, 31)
RHO_MIN: Final = Fraction(1, 2)
MIN_DAYS: Final = 20
CLAIM: Final = (
    "NESO's Constraints figure as a share of the two cuts rises with the wind share of "
    "accepted bid volume (Spearman rho >= 0.50 over at least 20 qualifying days from "
    "2026-09-16)"
)


def wind_volume_share(row: dict[str, Any]) -> Fraction | None:
    """x: accepted bid MWh on WIND units over the day's accepted bid MWh from
    system prices, both absolute; None unless the volume gate chose a type."""
    if row.get("disptav_type") is None or row.get("wind_bid_mwh") is None:
        return None
    settlement = (row.get("reconciliation") or {}).get("settlement_mwh") or {}
    total = settlement.get("bid")
    if total is None or Fraction(Decimal(total)) == 0:
        return None
    return Fraction(Decimal(row["wind_bid_mwh"])) / abs(Fraction(Decimal(total)))


def constraint_share(row: dict[str, Any]) -> Fraction | None:
    """y: NESO's Constraints at its first vintage over the two cuts, exact
    (not the tracker's 4-decimal ratio, whose rounding would make ties);
    None when L1 is absent, arrived after the falsifier date, or the two
    cuts are not positive."""
    outcome = row.get("outcome") or {}
    l1, vintage = outcome.get("l1_constraints_gbp"), outcome.get("vintage")
    if l1 is None or vintage is None or date.fromisoformat(vintage) > FALSIFIER_DATE:
        return None
    two_cut = row.get("two_cut_gbp")
    if two_cut is None or Fraction(Decimal(two_cut)) <= 0:
        return None
    return Fraction(Decimal(l1)) / Fraction(Decimal(two_cut))


def qualifying(rows: list[dict[str, Any]]) -> list[tuple[str, Fraction, Fraction]]:
    out = []
    for row in rows:
        day = date.fromisoformat(row["settlement_date"])
        if row.get("seed") or day < WINDOW_START or day > FALSIFIER_DATE:
            continue
        if not row.get("available"):
            continue
        x, y = wind_volume_share(row), constraint_share(row)
        if x is not None and y is not None:
            out.append((row["settlement_date"], x, y))
    return out


def ranks(values: list[Fraction]) -> list[Fraction]:
    """1-based ranks; tied values share the average of their positions."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [Fraction(0)] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = Fraction(i + j + 2, 2)
        for k in range(i, j + 1):
            out[order[k]] = average
        i = j + 1
    return out


def spearman_at_least(
    xs: list[Fraction], ys: list[Fraction], bound: Fraction
) -> tuple[bool, Decimal | None]:
    """Whether Spearman's rho (Pearson on average ranks) is >= `bound`
    (exact), and rho rounded to 4 d.p. for display; a constant variable has
    no rho and cannot rise, so it does not reach the bound."""
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    zero = Fraction(0)
    mx, my = sum(rx, zero) / n, sum(ry, zero) / n
    cov = sum(((a - mx) * (b - my) for a, b in zip(rx, ry, strict=True)), zero)
    vx = sum(((a - mx) * (a - mx) for a in rx), zero)
    vy = sum(((b - my) * (b - my) for b in ry), zero)
    if vx == 0 or vy == 0:
        return False, None
    if bound <= 0:
        raise ValueError("the exact comparison assumes a positive bound")
    reaches = cov >= 0 and cov * cov >= bound * bound * vx * vy
    with localcontext() as ctx:
        ctx.prec = 40
        rho = (Decimal(cov.numerator) / Decimal(cov.denominator)) / (
            (Decimal(vx.numerator) / Decimal(vx.denominator))
            * (Decimal(vy.numerator) / Decimal(vy.denominator))
        ).sqrt()
    return reaches, rho.quantize(Decimal("0.0001"))


def evaluate(rows: list[dict[str, Any]], as_of: date, declaration_sha256: str) -> dict[str, Any]:
    days = qualifying(rows)
    decided = as_of >= FALSIFIER_DATE
    block: dict[str, Any] = {
        "claim": CLAIM,
        "declaration_sha256": declaration_sha256,
        "window_start": WINDOW_START.isoformat(),
        "falsifier_date": FALSIFIER_DATE.isoformat(),
        "rho_min": "0.50",
        "min_days": MIN_DAYS,
        "qualifying_days": [d for d, _, _ in days],
        "n": len(days),
        "decided": decided,
        "rho": None,
        "holds": None,
    }
    if not decided or len(days) < MIN_DAYS:
        return block
    reaches, rho = spearman_at_least([x for _, x, _ in days], [y for _, _, y in days], RHO_MIN)
    block.update(rho=None if rho is None else str(rho), holds=reaches)
    block["context"] = context(rows, days)
    return block


def context(rows: list[dict[str, Any]], days: list[tuple[str, Fraction, Fraction]]) -> dict:
    """Reported with the verdict and never deciding it: rho with the £
    wind-bid share of paid-out in place of x, rho over the qualifying days
    whose sign check holds, and every qualifying day's (x, y)."""
    by_day = {r["settlement_date"]: r for r in rows}

    def rho_of(pairs: list[tuple[Fraction, Fraction]]) -> str | None:
        if len(pairs) < 2:
            return None
        rho = spearman_at_least([a for a, _ in pairs], [b for _, b in pairs], RHO_MIN)[1]
        return None if rho is None else str(rho)

    gbp = [
        (Fraction(Decimal(by_day[d]["wind_bid_share"])), y)
        for d, _, y in days
        if by_day[d].get("wind_bid_share") is not None
    ]
    sign_holds = [(x, y) for d, x, y in days if by_day[d].get("sign_convention_holds") is True]
    return {
        "rho_with_gbp_wind_bid_share": rho_of(gbp),
        "rho_on_sign_check_holds_days": rho_of(sign_holds),
        "sign_check_holds_days": len(sign_holds),
        "points": [
            {
                "settlement_date": d,
                "x": str(Decimal(x.numerator) / Decimal(x.denominator)),
                "y": str(Decimal(y.numerator) / Decimal(y.denominator)),
            }
            for d, x, y in days
        ],
    }


def describe(block: dict[str, Any]) -> tuple[str, str]:
    """(verdict word, detail) for both renderers; until the falsifier date
    only the count of qualifying days, never a running statistic."""
    n = block["n"]
    days = f"{n} qualifying day{'s' if n != 1 else ''}"
    if block["holds"] is None:
        if block["decided"]:
            return "undecided", f"{days}, fewer than {block['min_days']}"
        return "undecided", f"{days}; decided once on {block['falsifier_date']}"
    return ("holds" if block["holds"] else "fails"), f"rho {block['rho']} over {days}"
