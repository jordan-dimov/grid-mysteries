"""Render the two Method Study 001 charts as self-contained SVGs.

Reads ``evidence/analysis.json`` only; no analytics happen here. The SVGs
paint an explicit light surface so they are legible wherever the repo is
viewed. Colors are the validated reference dataviz palette: an ordinal
blue ramp for the funnel stages, a single blue series for the Pareto
curve, text in ink tokens.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent / "evidence"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e5e4e0"
BLUE_LIGHT = "#86b6ef"  # ordinal step 250 (validated light-end, 2.06:1)
BLUE = "#2a78d6"  # ordinal step 450 / series hue
FONT = "font-family=\"system-ui, 'Segoe UI', sans-serif\""


def _fmt(n: int) -> str:
    return f"{n:,}"


def funnel_svg(analysis: dict) -> str:
    funnel = analysis["funnel"]
    panels = [
        (
            "Pairwise price-order inversions",
            funnel["f1_raw_pairwise_inversions"],
            funnel["f7_residual_pairwise_inversions"],
        ),
        (
            "Unique better-priced alternatives",
            funnel["f3_unique_alternatives"],
            funnel["f7_residual_alternatives"],
        ),
    ]
    width, bar_h, gap = 920, 34, 14
    left, right = 30, 30
    panel_h = 2 * bar_h + gap + 58
    height = 88 + len(panels) * (panel_h + 26)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="{left}" y="36" {FONT} font-size="19" font-weight="600" fill="{INK}">'
        "What survives when apparent alternatives face public physical state?</text>",
        f'<text x="{left}" y="58" {FONT} font-size="13" fill="{INK_2}">'
        "GB Balancing Mechanism, 336 settlement periods, 2026-08-04 to 2026-08-10. "
        "Conservative bound: ruled out only when zero headroom is provable.</text>",
    ]
    y = 88
    plot_w = width - left - right - 190
    for title, before, after in panels:
        parts.append(
            f'<text x="{left}" y="{y + 14}" {FONT} font-size="14" font-weight="600" '
            f'fill="{INK}">{title}</text>'
        )
        y0 = y + 26
        for label, value, color in (
            ("raw (BOD taken at face value)", before, BLUE_LIGHT),
            ("survive the physical-state checks", after, BLUE),
        ):
            bar_w = max(3, round(plot_w * value / before))
            parts.append(
                f'<rect x="{left}" y="{y0}" width="{bar_w}" height="{bar_h}" '
                f'rx="4" fill="{color}"/>'
            )
            share = value / before
            share_text = f" ({share:.1%} of raw)" if value != before else ""
            parts.append(
                f'<text x="{left + bar_w + 10}" y="{y0 + bar_h / 2 + 5}" {FONT} '
                f'font-size="14" font-weight="600" fill="{INK}">{_fmt(value)}</text>'
            )
            parts.append(
                f'<text x="{left}" y="{y0 + bar_h + 15}" {FONT} font-size="12" '
                f'fill="{INK_2}">{label}{share_text}</text>'
            )
            y0 += bar_h + gap + 8
        y += panel_h + 26
    parts.append("</svg>")
    return "\n".join(parts)


def pareto_svg(analysis: dict) -> str:
    conc = analysis["f4_concentration"]
    n_groups = conc["n_groups"]
    shares = {int(k): float(v) for k, v in conc["cumulative_share_of_f1_at_group_rank"].items()}
    shares[n_groups] = 1.0
    width, height = 920, 420
    left, right, top, bottom = 70, 30, 88, 56
    plot_w, plot_h = width - left - right, height - top - bottom

    def x_at(rank: int) -> float:
        return left + plot_w * math.log10(rank) / math.log10(n_groups)

    def y_at(share: float) -> float:
        return top + plot_h * (1 - share)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="30" y="36" {FONT} font-size="19" font-weight="600" fill="{INK}">'
        "How concentrated is the raw illusion?</text>",
        f'<text x="30" y="58" {FONT} font-size="13" fill="{INK_2}">'
        "Cumulative share of all raw pairwise inversions attributable to the top-ranked "
        "(BM unit, submitted price) groups.</text>",
    ]
    for pct in (0.25, 0.5, 0.75, 1.0):
        gy = y_at(pct)
        parts.append(
            f'<line x1="{left}" y1="{gy}" x2="{left + plot_w}" y2="{gy}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{left - 8}" y="{gy + 4}" {FONT} font-size="12" fill="{INK_2}" '
            f'text-anchor="end">{pct:.0%}</text>'
        )
    tick = 1
    while tick <= n_groups:
        tx = x_at(tick)
        parts.append(
            f'<line x1="{tx}" y1="{top + plot_h}" x2="{tx}" y2="{top + plot_h + 5}" '
            f'stroke="{INK_2}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{tx}" y="{top + plot_h + 22}" {FONT} font-size="12" fill="{INK_2}" '
            f'text-anchor="middle">{_fmt(tick)}</text>'
        )
        tick *= 10
    parts.append(
        f'<text x="{left + plot_w / 2}" y="{height - 12}" {FONT} font-size="13" '
        f'fill="{INK_2}" text-anchor="middle">group rank (log scale) — {_fmt(n_groups)} '
        "groups in total</text>"
    )

    points = sorted(shares.items())
    path = " ".join(
        f"{'M' if i == 0 else 'L'}{x_at(rank):.1f},{y_at(share):.1f}"
        for i, (rank, share) in enumerate(points)
    )
    parts.append(
        f'<path d="{path}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-linejoin="round"/>'
    )
    for rank in (1, 10, 100):
        if rank not in shares:
            continue
        px, py = x_at(rank), y_at(shares[rank])
        parts.append(
            f'<circle cx="{px}" cy="{py}" r="5" fill="{BLUE}" stroke="{SURFACE}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{px + 10}" y="{py - 8}" {FONT} font-size="13" font-weight="600" '
            f'fill="{INK}">top {_fmt(rank)}: {shares[rank]:.1%}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def render() -> None:
    analysis = json.loads((EVIDENCE / "analysis.json").read_text())
    (EVIDENCE / "funnel.svg").write_text(funnel_svg(analysis) + "\n")
    (EVIDENCE / "concentration.svg").write_text(pareto_svg(analysis) + "\n")
    print("wrote funnel.svg and concentration.svg")


if __name__ == "__main__":
    render()
