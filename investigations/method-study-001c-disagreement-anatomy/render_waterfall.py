"""Render the Method Study 001C agreement waterfall as a self-contained SVG.

Reads ``evidence/disagreement-analysis.json`` only. Validated reference
dataviz palette; the peak layer carries the emphasis step, the rest the
light ordinal step. The decline after the peak is the finding, not a bug,
so it is drawn, labelled and never truncated.
"""

from __future__ import annotations

import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent / "evidence"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
BLUE_LIGHT = "#86b6ef"
BLUE = "#2a78d6"
FONT = "font-family=\"system-ui, 'Segoe UI', sans-serif\""

LABELS = {
    "naive_price_screen": "naive price screen (BOD at face value)",
    "physical_deliverability": "+ physical deliverability (FPN/MEL/MIL)",
    "minus_wind_offer": "− NESO 'Wind offer' exclusions",
    "minus_behind_constraint": "− 'Behind constraint' (binary adoption)",
    "minus_system_tagged": "− 'System-tagged'",
    "minus_unwind": "− 'Unwind'",
    "minus_ramping": "− ramping exclusions",
    "minus_long_notice_or_access": "− long-notice / accessibility",
}


def render() -> None:
    analysis = json.loads((EVIDENCE / "disagreement-analysis.json").read_text())
    waterfall = analysis["waterfall"]
    peak = max(row["agreement_rate"] for row in waterfall)

    width = 920
    row_h, gap = 46, 8
    top, left, right = 96, 330, 40
    height = top + len(waterfall) * (row_h + gap) + 44
    plot_w = width - left - right
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="30" y="36" {FONT} font-size="19" font-weight="600" fill="{INK}">'
        "Agreement with NESO, one layer of operational truth at a time</text>",
        f'<text x="30" y="58" {FONT} font-size="13" fill="{INK_2}">'
        "Share of 6,390 unit-day cells where the screen and NESO's stage-5 skip "
        "methodology agree. Adopting volumetric exclusions as binary filters "
        "over-corrects: the decline is the finding.</text>",
    ]
    y = top
    for row in waterfall:
        rate = row["agreement_rate"]
        is_peak = rate == peak
        bar_w = max(3, round(plot_w * rate))
        parts.append(
            f'<text x="{left - 12}" y="{y + 18}" {FONT} font-size="13" fill="{INK_2}" '
            f'text-anchor="end">{LABELS[row["layer"]]}</text>'
        )
        parts.append(
            f'<rect x="{left}" y="{y}" width="{bar_w}" height="28" rx="4" '
            f'fill="{BLUE if is_peak else BLUE_LIGHT}"/>'
        )
        peak_note = "  ← peak" if is_peak else ""
        parts.append(
            f'<text x="{left + bar_w + 10}" y="{y + 19}" {FONT} font-size="14" '
            f'font-weight="600" fill="{INK}">{rate:.1%}{peak_note}</text>'
        )
        detail = (
            f"catches {row['neso_skips_caught']:,}/{row['neso_skips_total']:,}"
            f" · false alarms {row['false_alarms']:,}"
        )
        parts.append(
            f'<text x="{left}" y="{y + 40}" {FONT} font-size="11" fill="{INK_2}">{detail}</text>'
        )
        y += row_h + gap
    parts.append("</svg>")
    (EVIDENCE / "waterfall.svg").write_text("\n".join(parts) + "\n")
    print("wrote waterfall.svg")


if __name__ == "__main__":
    render()
