"""Render the two Method Study 001 charts as self-contained SVGs.

Reads ``evidence/analysis.json`` only; no analytics happen here. The SVGs
paint an explicit light surface so they are legible wherever the repo is
viewed. Colors are the validated reference dataviz palette: an ordinal
blue ramp for the funnel stages, a single blue series for the Pareto
curve, text in ink tokens.
"""

import json
import math

from grid_mysteries.evidence import evidence_dir
from grid_mysteries.rendering.svg import BLUE, BLUE_LIGHT, GRID, INK_2, SURFACE, document, text

EVIDENCE = evidence_dir(__file__)


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
        *document(
            width,
            height,
            title="What survives when apparent alternatives face public physical state?",
            x=left,
        ),
        text(
            left,
            58,
            "GB Balancing Mechanism, 336 settlement periods, 2026-08-04 to 2026-08-10. "
            "Conservative bound: ruled out only when zero headroom is provable.",
            size=13,
            fill=INK_2,
        ),
    ]
    y = 88
    plot_w = width - left - right - 190
    for title, before, after in panels:
        parts.append(text(left, y + 14, title, size=14, weight=600))
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
                text(left + bar_w + 10, y0 + bar_h / 2 + 5, _fmt(value), size=14, weight=600)
            )
            parts.append(text(left, y0 + bar_h + 15, f"{label}{share_text}", size=12, fill=INK_2))
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
        *document(width, height, title="How concentrated is the raw illusion?"),
        text(
            30,
            58,
            "Cumulative share of all raw pairwise inversions attributable to the top-ranked "
            "(BM unit, submitted price) groups.",
            size=13,
            fill=INK_2,
        ),
    ]
    for pct in (0.25, 0.5, 0.75, 1.0):
        gy = y_at(pct)
        parts.append(
            f'<line x1="{left}" y1="{gy}" x2="{left + plot_w}" y2="{gy}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        parts.append(text(left - 8, gy + 4, f"{pct:.0%}", size=12, fill=INK_2, anchor="end"))
    tick = 1
    while tick <= n_groups:
        tx = x_at(tick)
        parts.append(
            f'<line x1="{tx}" y1="{top + plot_h}" x2="{tx}" y2="{top + plot_h + 5}" '
            f'stroke="{INK_2}" stroke-width="1"/>'
        )
        parts.append(text(tx, top + plot_h + 22, _fmt(tick), size=12, fill=INK_2, anchor="middle"))
        tick *= 10
    parts.append(
        text(
            left + plot_w / 2,
            height - 12,
            f"group rank (log scale) — {_fmt(n_groups)} groups in total",
            size=13,
            fill=INK_2,
            anchor="middle",
        )
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
            text(px + 10, py - 8, f"top {_fmt(rank)}: {shares[rank]:.1%}", size=13, weight=600)
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
