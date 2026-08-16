"""Render Method Study 001B's two charts as self-contained SVGs.

Reads ``evidence/screen-analysis.json`` and ``evidence/screen.parquet``
only; no analytics happen here. Validated reference dataviz palette:
ordinal blue ramp (before/after), ink text tokens, explicit light surface.
"""

from __future__ import annotations

import json
import math
from decimal import Decimal
from pathlib import Path

from grid_mysteries.rendering.svg import BLUE, BLUE_LIGHT, FONT, GRID, INK, INK_2, SURFACE

EVIDENCE = Path(__file__).resolve().parent / "evidence"


def funnel_svg(analysis: dict) -> str:
    notional = analysis["naive_counterfactual_notional_gbp"]
    raw_m = Decimal(notional["raw_total"]) / Decimal(1_000_000)
    post_m = Decimal(notional["post_filter_total"]) / Decimal(1_000_000)
    top100 = analysis["top_n_distortion_by_gap"]["100"]
    deliverable_top1 = 100 - top100["naive_top1_alternative_non_deliverable"]
    overlap = top100["overlap_with_post_filter_top_n"]

    width, height = 920, 470
    left, bar_h, gap = 30, 34, 12
    plot_w = width - 2 * left - 200
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="{left}" y="36" {FONT} font-size="19" font-weight="600" fill="{INK}">'
        "What happens to the opportunity screen?</text>",
        f'<text x="{left}" y="58" {FONT} font-size="13" fill="{INK_2}">'
        "One week of GB balancing data, 2026-08-04 to 2026-08-10. 25,326 accepted actions "
        "had an apparently better-priced alternative in raw bid-offer data.</text>",
    ]

    def panel(y: int, title: str, rows: list[tuple[str, float, float, str]]) -> int:
        parts.append(
            f'<text x="{left}" y="{y}" {FONT} font-size="14" font-weight="600" '
            f'fill="{INK}">{title}</text>'
        )
        y0 = y + 12
        for label, value, fraction, color in rows:
            bar_w = max(3, round(plot_w * fraction))
            parts.append(
                f'<rect x="{left}" y="{y0}" width="{bar_w}" height="{bar_h}" rx="4" '
                f'fill="{color}"/>'
            )
            parts.append(
                f'<text x="{left + bar_w + 10}" y="{y0 + bar_h / 2 + 5}" {FONT} '
                f'font-size="14" font-weight="600" fill="{INK}">{value}</text>'
            )
            parts.append(
                f'<text x="{left}" y="{y0 + bar_h + 15}" {FONT} font-size="12" '
                f'fill="{INK_2}">{label}</text>'
            )
            y0 += bar_h + gap + 14
        return y0

    y = panel(
        92,
        "Naive counterfactual notional — arithmetic on public numbers, not value",
        [
            ("raw screen: accepted MWh × apparent gap", f"£{raw_m:.1f}m", 1.0, BLUE_LIGHT),
            (
                "after removing provably non-deliverable alternatives "
                f"({Decimal(notional['vanished_share']) * 100:.1f}% vanished)",
                f"£{post_m:.1f}m",
                float(post_m / raw_m),
                BLUE,
            ),
        ],
    )
    panel(
        y + 26,
        "The screen's top 100 apparent opportunities (ranked by gap)",
        [
            ("raw top 100", "100", 1.0, BLUE_LIGHT),
            (
                "whose #1 pick could actually deliver",
                str(deliverable_top1),
                max(deliverable_top1 / 100, 0.004),
                BLUE,
            ),
            (
                "still in the top 100 once feasibility is applied",
                str(overlap),
                max(overlap / 100, 0.004),
                BLUE,
            ),
        ],
    )
    parts.append("</svg>")
    return "\n".join(parts)


def dumbbell_svg() -> str:
    import polars as pl

    table = pl.read_parquet(EVIDENCE / "screen.parquet")
    rows = sorted(
        table.iter_rows(named=True),
        key=lambda r: (
            -Decimal(r["naive_gap_gbp_per_mwh"]),
            r["settlement_date"],
            r["settlement_period"],
            r["direction"],
            r["accepted_unit"],
            r["accepted_pair_id"],
        ),
    )[:20]

    width, height = 920, 640
    left, right, top, bottom = 230, 40, 96, 54
    plot_w, plot_h = width - left - right, height - top - bottom
    lo, hi = 100.0, 20000.0

    def x_at(value: float) -> float:
        return left + plot_w * (math.log10(value) - math.log10(lo)) / (
            math.log10(hi) - math.log10(lo)
        )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="30" y="36" {FONT} font-size="19" font-weight="600" fill="{INK}">'
        "The screen's top 20, before and after one physics question</text>",
        f'<text x="30" y="58" {FONT} font-size="13" fill="{INK_2}">'
        "Apparent £/MWh advantage of the best alternative: taking bid-offer data at face "
        "value (light) vs keeping only alternatives that could deliver (dark).</text>",
    ]
    for tick in (100, 1000, 10000):
        tx = x_at(tick)
        parts.append(
            f'<line x1="{tx}" y1="{top}" x2="{tx}" y2="{top + plot_h}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{tx}" y="{top + plot_h + 20}" {FONT} font-size="12" fill="{INK_2}" '
            f'text-anchor="middle">£{tick:,}</text>'
        )
    parts.append(
        f'<text x="{left + plot_w / 2}" y="{height - 12}" {FONT} font-size="13" '
        f'fill="{INK_2}" text-anchor="middle">apparent gap, £/MWh (log scale)</text>'
    )

    step = plot_h / len(rows)
    for i, r in enumerate(rows):
        cy = top + step * (i + 0.5)
        naive_x = x_at(float(Decimal(r["naive_gap_gbp_per_mwh"])))
        post_x = x_at(float(Decimal(r["post_gap_gbp_per_mwh"])))
        label = f"{r['accepted_unit']}  {r['settlement_date'][5:]} p{r['settlement_period']}"
        parts.append(
            f'<text x="{left - 12}" y="{cy + 4}" {FONT} font-size="12" fill="{INK_2}" '
            f'text-anchor="end">{label}</text>'
        )
        parts.append(
            f'<line x1="{post_x}" y1="{cy}" x2="{naive_x}" y2="{cy}" '
            f'stroke="{BLUE_LIGHT}" stroke-width="2"/>'
        )
        parts.append(
            f'<circle cx="{naive_x}" cy="{cy}" r="5" fill="{BLUE_LIGHT}" '
            f'stroke="{SURFACE}" stroke-width="2"/>'
        )
        parts.append(
            f'<circle cx="{post_x}" cy="{cy}" r="5" fill="{BLUE}" '
            f'stroke="{SURFACE}" stroke-width="2"/>'
        )

    legend_y = top - 18
    parts.append(
        f'<circle cx="{left + 8}" cy="{legend_y}" r="5" fill="{BLUE_LIGHT}"/>'
        f'<text x="{left + 18}" y="{legend_y + 4}" {FONT} font-size="12" fill="{INK}">'
        "raw bid-offer data</text>"
        f'<circle cx="{left + 158}" cy="{legend_y}" r="5" fill="{BLUE}"/>'
        f'<text x="{left + 168}" y="{legend_y + 4}" {FONT} font-size="12" fill="{INK}">'
        "deliverable alternatives only (~40× smaller)</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def render() -> None:
    analysis = json.loads((EVIDENCE / "screen-analysis.json").read_text())
    (EVIDENCE / "screen-funnel.svg").write_text(funnel_svg(analysis) + "\n")
    (EVIDENCE / "rank-distortion.svg").write_text(dumbbell_svg() + "\n")
    print("wrote screen-funnel.svg and rank-distortion.svg")


if __name__ == "__main__":
    render()
