"""Render Publication Pack 006's grouped bars from evidence.json only."""

import json
from pathlib import Path

from grid_mysteries.rendering.svg import BLUE, BLUE_LIGHT, GRID, INK, INK_2, document, text

OUT = Path(__file__).resolve().parent
W, LEFT, RIGHT = 920, 60, 40
BAR = 22


def vbar(x: float, y_top: float, h: float, fill: str) -> str:
    """A column: square at the baseline, 4px-rounded cap."""
    r = min(4, h / 2)
    return (
        f'<path d="M{x:.1f},{y_top + h:.1f} V{y_top + r:.1f} '
        f"A{r},{r} 0 0 1 {x + r:.1f},{y_top:.1f} "
        f"H{x + BAR - r:.1f} A{r},{r} 0 0 1 {x + BAR:.1f},{y_top + r:.1f} "
        f'V{y_top + h:.1f} Z" fill="{fill}"/>'
    )


def within_year() -> str:
    e = json.loads((OUT / "evidence.json").read_text())
    rows = e["within_year_requests"]
    top, plot_h = 130, 260
    height = top + plot_h + 165
    parts = document(
        W, height, title="New transmission outage requests raised within the year, by phase"
    )
    parts.append(
        text(
            30,
            60,
            "National Grid Electricity Transmission KPIs 3a\u20133c, FY24 versus FY25.",
            size=13,
            fill=INK_2,
        )
    )
    parts.append(
        text(
            30,
            80,
            "The year-ahead plan improved (46% \u2192 50% delivered); "
            "the changes raised against it grew faster.",
            size=13,
            fill=INK_2,
        )
    )
    ceiling = 2500
    scale = plot_h / ceiling
    base = top + plot_h
    for tick in (0, 500, 1000, 1500, 2000, 2500):
        y = base - tick * scale
        parts.append(
            f'<line x1="{LEFT}" y1="{y:.1f}" x2="{W - RIGHT}" y2="{y:.1f}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        parts.append(text(LEFT - 8, f"{y + 4:.1f}", f"{tick:,}", size=11, fill=INK_2, anchor="end"))
    slot = (W - LEFT - RIGHT) / len(rows)
    for i, r in enumerate(rows):
        cx = LEFT + slot * i + slot / 2
        x24, x25 = cx - BAR - 1, cx + 1  # 2px surface gap between the pair
        h24, h25 = r["fy24"] * scale, r["fy25"] * scale
        parts.append(vbar(x24, base - h24, h24, BLUE_LIGHT))
        parts.append(vbar(x25, base - h25, h25, BLUE))
        parts.append(
            text(
                f"{x25 + BAR / 2:.1f}",
                f"{base - h25 - 8:.1f}",
                f"{r['fy25']:,}",
                size=13,
                weight=700,
                anchor="middle",
            )
        )
        change = (r["fy25"] - r["fy24"]) / r["fy24"] * 100
        parts.append(text(f"{cx:.1f}", base + 22, r["phase"], size=12.5, fill=INK, anchor="middle"))
        parts.append(
            text(
                f"{cx:.1f}",
                base + 42,
                f"{change:+.0f}% year on year",
                size=12,
                fill=INK_2,
                anchor="middle",
            )
        )
    ly = base + 70
    parts.append(f'<rect x="{LEFT}" y="{ly}" width="12" height="12" fill="{BLUE_LIGHT}"/>')
    parts.append(text(LEFT + 18, ly + 10, "FY24", size=12, fill=INK))
    parts.append(f'<rect x="{LEFT + 70}" y="{ly}" width="12" height="12" fill="{BLUE}"/>')
    parts.append(text(LEFT + 88, ly + 10, "FY25", size=12, fill=INK))
    parts.append(
        text(
            30,
            height - 40,
            f"Source: {e['source_kpi']};",
            size=11,
            fill=INK_2,
        )
    )
    parts.append(
        text(
            30,
            height - 24,
            "NESO Network Access Planning (\u22482,500 planned outages, >17,000 changes, "
            "65 engineers). "
            "Batch 01 candidate C7, with same-day correction.",
            size=11,
            fill=INK_2,
        )
    )
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    (OUT / "within-year.svg").write_text(within_year() + "\n")
    print("rendered within-year.svg")
