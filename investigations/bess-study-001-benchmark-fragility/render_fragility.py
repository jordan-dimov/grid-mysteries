"""Render BESS Study 001's two charts as self-contained SVGs.

Reads ``evidence/fragility-analysis.json`` only — no number is typed by
hand. Semantics per the study Corrections: R3h/R3p are two
information-set views branching from the duration constraint, never
monotonic rungs; the revision flows are drawn as a diverging pair, not a
net bar.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from grid_mysteries.rendering.svg import BLUE, BLUE_LIGHT, FONT, GRID, INK, INK_2, SURFACE

EVIDENCE = Path(__file__).resolve().parent / "evidence"
RED = "#e34948"  # diverging warm pole (validated reference palette slot)
W = 920
LEFT = 40


def load() -> dict:
    a = json.loads((EVIDENCE / "fragility-analysis.json").read_text())
    pooled = {k: Decimal(v) for k, v in a["pooled"].items()}
    return {
        "r1": pooled["r1_price_only"],
        "r2": pooled["r2_power_feasible"],
        "r3h": pooled["r3h_duration_hindsight"],
        "r3p": pooled["r3p_duration_public"],
        "r4": pooled["r4_context_free"],
        "future_only": sum(Decimal(v) for v in a["future_only_gbp"].values()),
        "revised_away": sum(Decimal(v) for v in a["revised_away_gbp"].values()),
        "n_future": sum(a["hindsight_exceeds_public_periods"].values()),
        "n_revised": sum(a["public_exceeds_hindsight_periods"].values()),
    }


def money(v: Decimal) -> str:
    return f"£{v / Decimal(1_000_000):.1f}m" if v >= 1_000_000 else f"£{v:,.0f}"


def pct(v: Decimal, base: Decimal) -> str:
    return f"{v / base:.2%}" if v / base < Decimal("0.1") else f"{v / base:.1%}"


def ladder_svg(d: dict) -> str:
    height = 700
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}">',
        f'<rect width="{W}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="{LEFT}" y="42" {FONT} font-size="20" font-weight="700" fill="{INK}">'
        "Benchmark fragility: a battery counterfactual, made credible in stages</text>",
        f'<text x="{LEFT}" y="66" {FONT} font-size="13" fill="{INK_2}">'
        "July 2026, four-unit GC0166 early-submitter panel. Every figure is arithmetic "
        "on public numbers — never savings or achievable value.</text>",
    ]
    plot_w = W - 2 * LEFT - 200

    # Act 1: the collapse (R1 -> R2), drawn at R1 scale.
    parts.append(
        f'<text x="{LEFT}" y="106" {FONT} font-size="14" font-weight="600" fill="{INK}">'
        "1 · The price-only construct meets physics</text>"
    )
    for i, (label, value, color) in enumerate(
        [
            ("price-only: the price existed", d["r1"], BLUE_LIGHT),
            ("power-feasible (FPN/MEL/MIL)", d["r2"], BLUE),
        ]
    ):
        y = 122 + i * 64
        bar = max(4, round(plot_w * float(value / d["r1"])))
        parts.append(f'<rect x="{LEFT}" y="{y}" width="{bar}" height="30" rx="4" fill="{color}"/>')
        parts.append(
            f'<text x="{LEFT + bar + 10}" y="{y + 20}" {FONT} font-size="14" font-weight="700" '
            f'fill="{INK}">{money(value)} · {pct(value, d["r1"])} of R1</text>'
        )
        parts.append(
            f'<text x="{LEFT}" y="{y + 44}" {FONT} font-size="12" fill="{INK_2}">{label}</text>'
        )

    # Act 2: the duration constraint BRANCHES into two information sets,
    # drawn at R2 scale.
    parts.append(
        f'<text x="{LEFT}" y="292" {FONT} font-size="14" font-weight="600" fill="{INK}">'
        "2 · The new GC0166 duration envelope — two information sets, not one rung</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="312" {FONT} font-size="12" fill="{INK_2}">'
        f"(drawn at power-feasible scale, {money(d['r2'])} = full width; the two views are "
        "non-monotonic between each other)</text>"
    )
    branch = [
        ("final vintage — the published envelope, seen in hindsight", d["r3h"]),
        ("public-as-of — only what was observable 60 minutes before delivery", d["r3p"]),
    ]
    for i, (label, value) in enumerate(branch):
        y = 330 + i * 64
        bar = max(4, round(plot_w * float(value / d["r2"])))
        parts.append(f'<rect x="{LEFT}" y="{y}" width="{bar}" height="30" rx="4" fill="{BLUE}"/>')
        parts.append(
            f'<text x="{LEFT + bar + 10}" y="{y + 20}" {FONT} font-size="14" font-weight="700" '
            f'fill="{INK}">{money(value)} · {pct(value, d["r1"])} of R1</text>'
        )
        parts.append(
            f'<text x="{LEFT}" y="{y + 44}" {FONT} font-size="12" fill="{INK_2}">{label}</text>'
        )
    parts.append(
        f'<text x="{LEFT}" y="478" {FONT} font-size="13" fill="{INK}">'
        f'Duration-awareness removed <tspan font-weight="700">'
        f"{(1 - d['r3h'] / d['r2']):.1%}</tspan> of what physics alone permitted.</text>"
    )

    # Act 3: operational-context disclosure.
    parts.append(
        f'<text x="{LEFT}" y="530" {FONT} font-size="14" font-weight="600" fill="{INK}">'
        "3 · Operational-context disclosure (not a verdict)</text>"
    )
    bar = max(4, round(plot_w * float(d["r4"] / d["r2"])))
    parts.append(f'<rect x="{LEFT}" y="546" width="{bar}" height="30" rx="4" fill="{INK}"/>')
    parts.append(
        f'<text x="{LEFT + bar + 10}" y="{566}" {FONT} font-size="14" font-weight="700" '
        f'fill="{INK}">{money(d["r4"])} · {pct(d["r4"], d["r1"])} of R1</text>'
    )
    parts.append(
        f'<text x="{LEFT}" y="590" {FONT} font-size="12" fill="{INK_2}">'
        "carries no published NESO exclusion context on either side of the comparison</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="646" {FONT} font-size="12" fill="{INK_2}">'
        "Sources: evidence/fragility-analysis.json · findings fnd-bess-001-fragility "
        "and fnd-bess-001-fragility-corrected · github.com/jordan-dimov/grid-mysteries</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def revisions_svg(d: dict) -> str:
    height = 420
    mid_x = W / 2
    scale = (W / 2 - 80) / float(max(d["future_only"], d["revised_away"]))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}">',
        f'<rect width="{W}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="{LEFT}" y="42" {FONT} font-size="20" font-weight="700" fill="{INK}">'
        "Hindsight does not just know more — it revises the feasible state</text>",
        f'<text x="{LEFT}" y="66" {FONT} font-size="13" fill="{INK_2}">'
        "Final-vintage MDO/MDB versus the envelope publicly observable 60 minutes before "
        "delivery, per settlement period, July 2026 panel.</text>",
        f'<line x1="{mid_x}" y1="100" x2="{mid_x}" y2="300" stroke="{GRID}" stroke-width="2"/>',
    ]
    added_w = round(float(d["future_only"]) * scale)
    removed_w = round(float(d["revised_away"]) * scale)
    parts.append(f'<rect x="{mid_x}" y="130" width="{added_w}" height="44" rx="4" fill="{BLUE}"/>')
    parts.append(
        f'<text x="{mid_x + 12}" y="{130 - 10}" {FONT} font-size="14" font-weight="700" '
        f'fill="{INK}">+{money(d["future_only"])} added in hindsight</text>'
    )
    parts.append(
        f'<text x="{mid_x + 12}" y="{130 + 62}" {FONT} font-size="12" fill="{INK_2}">'
        f"{d['n_future']:,} periods where the supporting envelope was published only "
        "after the decision cutoff</text>"
    )
    parts.append(
        f'<rect x="{mid_x - removed_w}" y="216" width="{removed_w}" height="44" rx="4" '
        f'fill="{RED}"/>'
    )
    parts.append(
        f'<text x="{mid_x - 12}" y="{216 - 10}" {FONT} font-size="14" font-weight="700" '
        f'fill="{INK}" text-anchor="end">−{money(d["revised_away"])} revised away</text>'
    )
    parts.append(
        f'<text x="{mid_x - 12}" y="{216 + 62}" {FONT} font-size="12" fill="{INK_2}" '
        f'text-anchor="end">{d["n_revised"]:,} periods where the final vintage withdrew '
        "opportunity the public envelope had supported</text>"
    )
    net = d["future_only"] - d["revised_away"]
    parts.append(
        f'<text x="{LEFT}" y="340" {FONT} font-size="13" fill="{INK}">'
        f'The pooled net, <tspan font-weight="700">{money(net)}</tspan>, conceals both '
        "flows. Either direction grades a historical decision against a revised "
        "information set.</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="390" {FONT} font-size="12" fill="{INK_2}">'
        "Proves public availability only, never control-room knowledge. Sources: "
        "evidence/fragility-analysis.json · fnd-bess-001-fragility-corrected</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def render() -> None:
    d = load()
    (EVIDENCE / "fragility-ladder.svg").write_text(ladder_svg(d) + "\n")
    (EVIDENCE / "revision-flows.svg").write_text(revisions_svg(d) + "\n")
    print("wrote fragility-ladder.svg and revision-flows.svg")


if __name__ == "__main__":
    render()
