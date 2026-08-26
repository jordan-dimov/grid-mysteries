"""Render the Method Study 001C agreement waterfall as a self-contained SVG.

Reads ``evidence/disagreement-analysis.json`` only. Validated reference
dataviz palette; the peak layer carries the emphasis step, the rest the
light ordinal step. The decline after the peak is the finding, not a bug,
so it is drawn, labelled and never truncated.
"""

import json

from grid_mysteries.evidence import evidence_dir
from grid_mysteries.rendering.svg import BLUE, BLUE_LIGHT, INK_2, document, text

EVIDENCE = evidence_dir(__file__)


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
        *document(
            width, height, title="Agreement with NESO, one layer of operational truth at a time"
        ),
        text(
            30,
            58,
            "Share of 6,390 unit-day cells where the screen and NESO's stage-5 skip "
            "methodology agree. Adopting volumetric exclusions as binary filters "
            "over-corrects: the decline is the finding.",
            size=13,
            fill=INK_2,
        ),
    ]
    y = top
    for row in waterfall:
        rate = row["agreement_rate"]
        is_peak = rate == peak
        bar_w = max(3, round(plot_w * rate))
        parts.append(
            text(left - 12, y + 18, LABELS[row["layer"]], size=13, fill=INK_2, anchor="end")
        )
        parts.append(
            f'<rect x="{left}" y="{y}" width="{bar_w}" height="28" rx="4" '
            f'fill="{BLUE if is_peak else BLUE_LIGHT}"/>'
        )
        peak_note = "  ← peak" if is_peak else ""
        parts.append(text(left + bar_w + 10, y + 19, f"{rate:.1%}{peak_note}", size=14, weight=600))
        detail = (
            f"catches {row['neso_skips_caught']:,}/{row['neso_skips_total']:,}"
            f" · false alarms {row['false_alarms']:,}"
        )
        parts.append(text(left, y + 40, detail, size=11, fill=INK_2))
        y += row_h + gap
    parts.append("</svg>")
    (EVIDENCE / "waterfall.svg").write_text("\n".join(parts) + "\n")
    print("wrote waterfall.svg")


if __name__ == "__main__":
    render()
