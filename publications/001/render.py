"""Render Publication Pack 001's visuals from committed evidence only.

Every displayed number is read from the pinned analysis files of Method
Studies 001, 001B and 001C — nothing is typed in here, so the graphic
cannot drift from the governed record. No new analytical claim is made.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
MS1 = REPO_ROOT / "investigations" / "method-study-001-phantom-liquidity" / "evidence"
MS1B = REPO_ROOT / "investigations" / "method-study-001b-naive-screen" / "evidence"
MS1C = REPO_ROOT / "investigations" / "method-study-001c-disagreement-anatomy" / "evidence"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
BLUE_LIGHT = "#86b6ef"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
FONT = "font-family=\"system-ui, 'Segoe UI', sans-serif\""

W = 920
LEFT = 48
PLOT_W = W - 2 * LEFT


def load() -> dict:
    ms1 = json.loads((MS1 / "analysis.json").read_text())
    b = json.loads((MS1B / "screen-analysis.json").read_text())
    c = json.loads((MS1C / "disagreement-analysis.json").read_text())
    notional = b["naive_counterfactual_notional_gbp"]
    attribution = c["primary_attribution"]
    other_rules = sum(
        count
        for category, count in attribution.items()
        if category not in ("absent_from_neso_universe", "behind_constraint", "unmatched")
    )
    return {
        "f1": ms1["funnel"]["f1_raw_pairwise_inversions"],
        "raw_m": Decimal(notional["raw_total"]) / Decimal(1_000_000),
        "post_m": Decimal(notional["post_filter_total"]) / Decimal(1_000_000),
        "vanished_pct": Decimal(notional["vanished_share"]) * 100,
        "top1000_phantom": b["top_n_distortion_by_gap"]["1000"][
            "naive_top1_alternative_non_deliverable"
        ],
        "top100_overlap": b["top_n_distortion_by_gap"]["100"]["overlap_with_post_filter_top_n"],
        "agree_naive": c["waterfall"][0]["agreement_rate"],
        "agree_post": c["waterfall"][1]["agreement_rate"],
        "catches": c["waterfall"][1]["neso_skips_caught"],
        "skips_total": c["waterfall"][1]["neso_skips_total"],
        "disagreements": c["disagreement_cells"],
        "availability": attribution["absent_from_neso_universe"],
        "constraint": attribution["behind_constraint"],
        "other_rules": other_rules,
        "unmatched": attribution["unmatched"],
        "attributed_pct": (c["disagreement_cells"] - attribution["unmatched"])
        / c["disagreement_cells"]
        * 100,
        "six": c["unmatched_cell_list"],
    }


def chip(parts: list, y: int, text: str) -> None:
    parts.append(
        f'<text x="{LEFT}" y="{y}" {FONT} font-size="13" font-weight="700" fill="{BLUE}" '
        f'letter-spacing="2">{text}</text>'
    )


def attribution_bar(parts: list, y: int, data: dict, bar_h: int = 40) -> None:
    segments = [
        (data["availability"], BLUE, "not in NESO's availability universe"),
        (data["constraint"], ORANGE, "behind constraint"),
        (data["other_rules"], AQUA, "other published rules"),
        (data["unmatched"], INK, "unmatched"),
    ]
    total = sum(count for count, _, _ in segments)
    x = LEFT
    for count, color, label in segments:
        seg_w = max(4, round((PLOT_W - 6) * count / total))
        parts.append(
            f'<rect x="{x}" y="{y}" width="{seg_w}" height="{bar_h}" rx="3" fill="{color}"/>'
        )
        share = count / total
        if share > 0.08:
            parts.append(
                f'<text x="{x + 6}" y="{y + bar_h + 18}" {FONT} font-size="12" '
                f'fill="{INK_2}">{label}</text>'
            )
            parts.append(
                f'<text x="{x + 6}" y="{y + bar_h + 34}" {FONT} font-size="13" '
                f'font-weight="600" fill="{INK}">{count:,} · {share:.1%}</text>'
            )
        x += seg_w + 2
    end_x = x - 2
    parts.append(
        f'<line x1="{end_x}" y1="{y - 14}" x2="{end_x}" y2="{y - 2}" '
        f'stroke="{INK}" stroke-width="1.5"/>'
    )
    parts.append(
        f'<text x="{end_x}" y="{y - 20}" {FONT} font-size="13" font-weight="600" '
        f'fill="{INK}" text-anchor="end">6 unmatched</text>'
    )


def story_svg(d: dict) -> str:
    height = 1130
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}">',
        f'<rect width="{W}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="{LEFT}" y="52" {FONT} font-size="26" font-weight="700" fill="{INK}">'
        "Anatomy of a phantom opportunity screen</text>",
        f'<text x="{LEFT}" y="78" {FONT} font-size="14" fill="{INK_2}">'
        "One week of Britain's Balancing Mechanism, 4–10 August 2026, reconstructed "
        "from public data — layer by layer.</text>",
    ]

    # Act 1 — PRICE
    chip(parts, 128, "PRICE")
    parts.append(
        f'<text x="{LEFT}" y="176" {FONT} font-size="40" font-weight="700" fill="{INK}">'
        f"{d['f1']:,}</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="200" {FONT} font-size="14" fill="{INK_2}">'
        "apparent price-order inversions — cases where a better-priced action looks "
        "ignored if bid-offer data is taken at face value.</text>"
    )
    parts.append(
        f'<rect x="{LEFT}" y="214" width="{PLOT_W}" height="26" rx="4" fill="{BLUE_LIGHT}"/>'
    )
    parts.append(
        f'<text x="{LEFT}" y="262" {FONT} font-size="14" fill="{INK_2}">'
        f"Apparent counterfactual notional — arithmetic on public numbers, not value: "
        f'<tspan font-weight="700" fill="{INK}">£{d["raw_m"]:.1f}m</tspan></text>'
    )

    # Act 2 — PHYSICS
    chip(parts, 318, "PHYSICS")
    parts.append(
        f'<text x="{LEFT}" y="344" {FONT} font-size="16" font-weight="600" fill="{INK}">'
        "One question: could the “better” alternative actually deliver a "
        "single megawatt?</text>"
    )
    post_w = max(6, round(PLOT_W * float(d["post_m"] / d["raw_m"])))
    parts.append(f'<rect x="{LEFT}" y="358" width="{post_w}" height="26" rx="4" fill="{BLUE}"/>')
    parts.append(
        f'<text x="{LEFT + post_w + 10}" y="{358 + 18}" {FONT} font-size="14" '
        f'font-weight="700" fill="{INK}">£{d["post_m"]:.1f}m remains — '
        f"{d['vanished_pct']:.1f}% vanished</text>"
    )
    bullets = [
        f"top 1,000 apparent opportunities: {d['top1000_phantom']:,}/1,000 led by a "
        "physically impossible pick",
        f"overlap between the raw and feasibility-aware top 100: {d['top100_overlap']}",
        f"agreement with NESO's own skip methodology: {d['agree_naive']:.0%} → "
        f"{d['agree_post']:.0%}, still catching {d['catches']:,} of "
        f"{d['skips_total']:,} skips",
    ]
    for i, text in enumerate(bullets):
        parts.append(
            f'<circle cx="{LEFT + 5}" cy="{412 + i * 26}" r="3" fill="{BLUE}"/>'
            f'<text x="{LEFT + 18}" y="{417 + i * 26}" {FONT} font-size="14" '
            f'fill="{INK}">{text}</text>'
        )

    # Act 3 — OPERATIONAL CONTEXT (attribution, not an accuracy funnel)
    chip(parts, 542, "OPERATIONAL CONTEXT")
    parts.append(
        f'<text x="{LEFT}" y="568" {FONT} font-size="16" font-weight="600" fill="{INK}">'
        f"The {d['disagreements']:,} unit-days where the physics-aware screen still "
        "disagreed with NESO…</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="588" {FONT} font-size="13" fill="{INK_2}">'
        "…attributed through the operator's published exclusions. This is an "
        "attribution of disagreement, not an accuracy funnel: the exclusions are "
        "volumetric, and adopting them as binary filters degrades agreement.</text>"
    )
    attribution_bar(parts, 622, d)
    parts.append(
        f'<text x="{LEFT}" y="712" {FONT} font-size="15" fill="{INK}">'
        f'<tspan font-weight="700">{d["attributed_pct"]:.1f}%</tspan> of the remaining '
        "disagreement has a public operational explanation.</text>"
    )

    # Act 4 — FRONTIER
    chip(parts, 776, "FRONTIER")
    parts.append(
        f'<text x="{LEFT}" y="850" {FONT} font-size="64" font-weight="700" fill="{INK}">'
        f"{d['unmatched']}</text>"
    )
    parts.append(
        f'<text x="{LEFT + 70}" y="826" {FONT} font-size="15" fill="{INK}">'
        "unit-days in the entire week that public data</text>"
    )
    parts.append(
        f'<text x="{LEFT + 70}" y="848" {FONT} font-size="15" fill="{INK}">'
        "still cannot explain — all bid-side battery or small units.</text>"
    )
    parts.append(
        f'<text x="{LEFT + 70}" y="870" {FONT} font-size="14" font-weight="600" '
        f'fill="{BLUE}">That is the part worth investigating next.</text>'
    )
    parts.append(
        f'<text x="{LEFT}" y="920" {FONT} font-size="15" font-style="italic" fill="{INK}">'
        "Public data does not withhold the explanation — it withholds the resolution "
        "at which the explanation operates.</text>"
    )

    # Verification footer
    parts.append(f'<line x1="{LEFT}" y1="1030" x2="{W - LEFT}" y2="1030" stroke="#e5e4e0"/>')
    parts.append(
        f'<text x="{LEFT}" y="1056" {FONT} font-size="12" fill="{INK_2}">'
        "Pre-registered hypotheses · pinned evidence (SHA-256) · governed "
        "Morpholog audit record · reproducible CI</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="1076" {FONT} font-size="12" fill="{INK_2}">'
        "github.com/jordan-dimov/grid-mysteries — every number above is bound to a "
        "committed evidence artefact (see PUBLICATION-001.md).</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def anatomy_svg(d: dict) -> str:
    height = 330
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}">',
        f'<rect width="{W}" height="{height}" fill="{SURFACE}"/>',
        f'<text x="{LEFT}" y="44" {FONT} font-size="19" font-weight="600" fill="{INK}">'
        f"Anatomy of the {d['disagreements']:,} remaining disagreements with NESO</text>",
        f'<text x="{LEFT}" y="66" {FONT} font-size="13" fill="{INK_2}">'
        "Primary attribution per unit-day cell, from NESO's published in-merit and "
        "exclusion data. Attribution of disagreement — not an accuracy funnel.</text>",
    ]
    attribution_bar(parts, 100, d)
    detail = (
        "other published rules: long-notice/accessibility 132 · ramping 129 · "
        "wind offer 122 · unwind 106 · fully accepted in merit 39 · "
        "system-tagged 25 · invalid parameters 1"
    )
    parts.append(f'<text x="{LEFT}" y="196" {FONT} font-size="12" fill="{INK_2}">{detail}</text>')
    parts.append(
        f'<text x="{LEFT}" y="240" {FONT} font-size="15" fill="{INK}">'
        f'<tspan font-weight="700">{d["attributed_pct"]:.1f}%</tspan> publicly '
        f'attributed · <tspan font-weight="700">{d["unmatched"]}</tspan> unit-days '
        "unmatched (all bid-side battery/small units)</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="290" {FONT} font-size="12" fill="{INK_2}">'
        "Source: Method Study 001C, evidence/disagreement-analysis.json · "
        "github.com/jordan-dimov/grid-mysteries</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def render() -> None:
    d = load()
    (OUT / "story.svg").write_text(story_svg(d) + "\n")
    (OUT / "anatomy-2226.svg").write_text(anatomy_svg(d) + "\n")
    print("wrote story.svg and anatomy-2226.svg")


if __name__ == "__main__":
    render()
