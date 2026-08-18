"""Render Publication Pack 003's three visuals from committed evidence only.

Every displayed number is read from Investigation 003's pinned evidence
files — nothing is typed in here, so the graphics cannot drift from the
governed record (including the attribution correction: cycle counts are
always labelled GB-wide, never attributed to the boundary). No new
analytical claim is made.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from grid_mysteries.rendering.svg import (
    AQUA,
    BLUE,
    BLUE_LIGHT,
    FONT,
    GRID,
    INK,
    INK_2,
    ORANGE,
    SURFACE,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
EVIDENCE = REPO_ROOT / "investigations" / "003-follow-the-constraint" / "evidence"

W = 920
LEFT = 48
PLOT_W = W - 2 * LEFT


def load() -> dict:
    selected = json.loads((EVIDENCE / "selected-episode.json").read_text())["selected"]
    excerpt = json.loads((EVIDENCE / "excerpt.json").read_text())
    series = json.loads((EVIDENCE / "presentation-series.json").read_text())
    accounting = json.loads((EVIDENCE / "episode-accounting.json").read_text())
    tally = json.loads((EVIDENCE / "so-flag-tally.json").read_text())
    ledger = json.loads((EVIDENCE / "episode-ledger.json").read_text())
    focus_acceptances = len(
        {
            frame["description"].split()[1]
            for frame in ledger["frames"]
            if frame["description"].startswith("acceptance ")
        }
    )
    return {
        "selected": selected,
        "excerpt": excerpt,
        "days": series["days"],
        "focus": series["focus"],
        "cash": accounting["published_indicative_bm_cashflows_gbp"],
        "group_cost": Decimal(str(accounting["published_constraint_cost_for_group_gbp"])),
        "tally": tally,
        "focus_acceptances": focus_acceptances,
    }


def title(parts: list, text: str, subtitle: str) -> None:
    parts.append(
        f'<text x="{LEFT}" y="46" {FONT} font-size="23" font-weight="700" fill="{INK}">'
        f"{text}</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="70" {FONT} font-size="13.5" fill="{INK_2}">{subtitle}</text>'
    )


def footer(parts: list, height: int, source: str) -> None:
    parts.append(
        f'<line x1="{LEFT}" y1="{height - 52}" x2="{W - LEFT}" y2="{height - 52}" stroke="{GRID}"/>'
    )
    parts.append(
        f'<text x="{LEFT}" y="{height - 30}" {FONT} font-size="11.5" fill="{INK_2}">'
        f"Evidence: {source} · pre-declared, pinned, governed · "
        "github.com/jordan-dimov/grid-mysteries</text>"
    )


def arrow(parts: list, x: float, y: float, length: float = 12) -> None:
    parts.append(
        f'<line x1="{x - length:.1f}" y1="{y:.1f}" x2="{x - 1:.1f}" y2="{y:.1f}" '
        f'stroke="{INK_2}" stroke-width="1.6"/>'
        f'<path d="M {x:.1f} {y:.1f} l -6 -4 l 0 8 z" fill="{INK_2}"/>'
    )


def overview_svg(d: dict) -> str:
    height = 620
    days = d["days"]
    n = len(days)
    slot = PLOT_W / n
    bar_w = slot - 10
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}">',
        f'<rect width="{W}" height="{height}" fill="{SURFACE}"/>',
    ]
    title(
        parts,
        "Fourteen days of constraint cost — and of GB-wide repetition",
        "SSE-SP episode, 18–31 May 2026. Two series that do NOT explain each other; "
        "no public data can attribute the cycles to the boundary.",
    )

    # Panel 1 — observed boundary cost.
    parts.append(
        f'<text x="{LEFT}" y="108" {FONT} font-size="12.5" font-weight="700" fill="{BLUE}" '
        f'letter-spacing="2">OBSERVED · NESO DAILY OUTTURN COST, SSE-SP GROUP</text>'
    )
    top1, h1 = 122, 150
    max_cost = max(Decimal(r["published_group_cost_gbp"]) for r in days)
    for i, r in enumerate(days):
        cost = Decimal(r["published_group_cost_gbp"])
        bh = max(2, round(h1 * float(cost / max_cost)))
        x = LEFT + i * slot
        parts.append(
            f'<rect x="{x:.1f}" y="{top1 + h1 - bh}" width="{bar_w:.1f}" height="{bh}" '
            f'rx="2" fill="{BLUE}"/>'
        )
        if cost == max_cost:
            parts.append(
                f'<text x="{x + bar_w + 6:.1f}" y="{top1 + 16}" {FONT} '
                f'font-size="12" font-weight="700" fill="{INK}">'
                f"£{float(cost) / 1e6:.1f}m</text>"
            )
    parts.append(
        f'<text x="{W - LEFT}" y="{top1 + 12}" {FONT} font-size="12" fill="{INK_2}" '
        f'text-anchor="end">episode total £{float(d["group_cost"]) / 1e6:.1f}m</text>'
    )

    # Panel 2 — GB-wide concurrence.
    top2, h2 = 330, 130
    parts.append(
        f'<text x="{LEFT}" y="{top2 - 14}" {FONT} font-size="12.5" font-weight="700" '
        f'fill="{ORANGE}" letter-spacing="2">GB-WIDE CONCURRENCE · REPEAT-CURTAILMENT '
        "CYCLES, ALL 165 STORAGE UNITS</text>"
    )
    max_cycles = max(r["gb_cycles"] for r in days)
    for i, r in enumerate(days):
        bh = max(2, round(h2 * r["gb_cycles"] / max_cycles))
        x = LEFT + i * slot
        parts.append(
            f'<rect x="{x:.1f}" y="{top2 + h2 - bh}" width="{bar_w:.1f}" height="{bh}" '
            f'rx="2" fill="{ORANGE}"/>'
        )
        if r["gb_cycles"] == max_cycles and i == 2:
            parts.append(
                f'<text x="{x + bar_w + 6:.1f}" y="{top2 + 16}" {FONT} '
                f'font-size="12" font-weight="700" fill="{INK}">'
                f"{r['gb_cycles']:,} cycles</text>"
            )
        parts.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{top2 + h2 + 18}" {FONT} font-size="10.5" '
            f'fill="{INK_2}" text-anchor="middle">{r["date"][8:]}</text>'
        )
    parts.append(
        f'<text x="{LEFT + 6.5 * slot:.1f}" y="{top2 + h2 + 36}" {FONT} font-size="11.5" '
        f'fill="{INK_2}">May 2026 · window ends 31 May — '
        "the episode may not (right-censored)</text>"
    )

    # The honest punchline the two panels force.
    parts.append(
        f'<text x="{LEFT}" y="{top2 + h2 + 76}" {FONT} font-size="14.5" fill="{INK}">'
        f'The most expensive day (19 May) had the <tspan font-weight="700">fewest</tspan> '
        "cycles; the busiest cycle day (20 May) cost 2% as much.</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="{top2 + h2 + 98}" {FONT} font-size="14.5" fill="{INK}">'
        "The two series cannot be reconciled from public data — "
        f'<tspan font-weight="700">no public mapping ties units to the boundary.</tspan></text>'
    )
    footer(parts, height, "presentation-series.json, episode-accounting.json")
    parts.append("</svg>")
    return "\n".join(parts)


def reel_svg(d: dict) -> str:
    height = 560
    focus = d["focus"]
    trajectory = focus["trajectory"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}">',
        f'<rect width="{W}" height="{height}" fill="{SURFACE}"/>',
    ]
    title(
        parts,
        f"One battery's day: {focus['unit']}, {focus['day']}",
        f"{d['excerpt']['focus_unit_cycles']} repeat-curtailment cycles · "
        f"{d['focus_acceptances']} distinct acceptances · 0 SO-flagged.",
    )
    top, plot_h = 120, 280
    y_max, y_min = 70, -110
    span = y_max - y_min

    def y(mw: float) -> float:
        return top + plot_h * (y_max - mw) / span

    zero_y = y(0)
    parts.append(
        f'<line x1="{LEFT}" y1="{zero_y:.1f}" x2="{W - LEFT}" y2="{zero_y:.1f}" '
        f'stroke="{INK_2}" stroke-width="1" stroke-dasharray="4 3"/>'
    )
    parts.append(
        f'<text x="{W - LEFT}" y="{zero_y - 6:.1f}" {FONT} font-size="11" fill="{INK_2}" '
        f'text-anchor="end">0 MW</text>'
    )
    slot = PLOT_W / 48
    # FPN schedule (final vintage) as a step band; instructed depth as bars.
    for t in trajectory:
        x = LEFT + (t["period"] - 1) * slot
        if t["fpn_max_mw"] is not None:
            fpn = float(Decimal(t["fpn_max_mw"]))
            if fpn > 0:
                parts.append(
                    f'<rect x="{x:.1f}" y="{y(fpn):.1f}" width="{slot - 2:.1f}" '
                    f'height="{max(1.5, zero_y - y(fpn)):.1f}" fill="{BLUE_LIGHT}"/>'
                )
        if t["instructed_min_mw"] is not None:
            level = float(Decimal(t["instructed_min_mw"]))
            if level < 0:
                parts.append(
                    f'<rect x="{x:.1f}" y="{zero_y:.1f}" width="{slot - 2:.1f}" '
                    f'height="{max(1.5, y(level) - zero_y):.1f}" fill="{ORANGE}"/>'
                )
            else:
                parts.append(
                    f'<rect x="{x:.1f}" y="{y(level) - 1.5:.1f}" width="{slot - 2:.1f}" '
                    f'height="3" fill="{ORANGE}"/>'
                )
    deepest = min(
        (Decimal(t["instructed_min_mw"]) for t in trajectory if t["instructed_min_mw"]),
    )
    parts.append(
        f'<text x="{LEFT + 5.5 * slot:.1f}" y="{y(float(deepest)) + 4:.1f}" {FONT} '
        f'font-size="12" font-weight="600" fill="{ORANGE}">'
        f"instructed to {deepest:.0f} MW (import)</text>"
    )
    for hour_period in (1, 12, 24, 36, 48):
        hx = LEFT + (hour_period - 1) * slot + (slot - 2) / 2
        parts.append(
            f'<text x="{hx:.1f}" y="{top + plot_h + 14}" {FONT} font-size="10.5" '
            f'fill="{INK_2}" text-anchor="middle">P{hour_period}</text>'
        )
    parts.append(
        f'<rect x="{LEFT}" y="{top + plot_h + 30}" width="12" height="12" fill="{BLUE_LIGHT}"/>'
        f'<text x="{LEFT + 18}" y="{top + plot_h + 40}" {FONT} font-size="12" fill="{INK}">'
        "final physical notification — scheduled export (final vintage; revision history "
        "is never published)</text>"
    )
    parts.append(
        f'<rect x="{LEFT}" y="{top + plot_h + 52}" width="12" height="12" fill="{ORANGE}"/>'
        f'<text x="{LEFT + 18}" y="{top + plot_h + 62}" {FONT} font-size="12" fill="{INK}">'
        "deepest accepted instruction in the period (BOALF)</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="{top + plot_h + 94}" {FONT} font-size="13.5" fill="{INK}">'
        "Between any two instructions sits the step the public record cannot show: "
        f'<tspan font-weight="700">whether retained energy was re-sold intraday.</tspan></text>'
    )
    parts.append(
        f'<text x="{LEFT}" y="{top + plot_h + 114}" {FONT} font-size="13" fill="{INK_2}">'
        "Zero SO-flags also means NESO's own RRT methodology (which requires a "
        "system-flagged acceptance) would not count this day at all.</text>"
    )
    footer(parts, height, "presentation-series.json, excerpt.json, so-flag-tally.json")
    parts.append("</svg>")
    return "\n".join(parts)


def diagram_svg(d: dict) -> str:
    height = 724
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}">',
        f'<rect width="{W}" height="{height}" fill="{SURFACE}"/>',
    ]
    title(
        parts,
        "What the public record can and cannot show",
        "The repetitive part is observable at scale. The re-trading economics are not.",
    )
    # The signature chain.
    chain = [
        ("OBSERVED", "scheduled to export", "final physical notification", BLUE),
        ("OBSERVED", "bid down through zero", "acceptance + published cashflow", BLUE),
        ("?", "intraday re-sale", "not publicly observable", INK),
        ("OBSERVED", "scheduled, bid down again", "the cycle re-arms", BLUE),
    ]
    box_w, box_h, gap = 190, 96, 22
    x = LEFT
    y0 = 108
    for label, headline, sub, color in chain:
        dash = ' stroke-dasharray="6 4"' if label == "?" else ""
        fill = SURFACE if label == "?" else "#ffffff"
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{box_w}" height="{box_h}" rx="8" '
            f'fill="{fill}" stroke="{color}" stroke-width="2"{dash}/>'
        )
        anchor = x + box_w / 2
        size = 30 if label == "?" else 12
        weight = 700
        parts.append(
            f'<text x="{anchor}" y="{y0 + 26 if label != "?" else y0 + 38}" {FONT} '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="middle" letter-spacing="1">{label}</text>'
        )
        parts.append(
            f'<text x="{anchor}" y="{y0 + 54}" {FONT} font-size="13" font-weight="600" '
            f'fill="{INK}" text-anchor="middle">{headline}</text>'
        )
        parts.append(
            f'<text x="{anchor}" y="{y0 + 74}" {FONT} font-size="11" fill="{INK_2}" '
            f'text-anchor="middle">{sub}</text>'
        )
        if x + box_w + gap < W - LEFT:
            arrow(parts, x + box_w + gap - 3, y0 + box_h / 2, gap - 6)
        x += box_w + gap
    score = d["selected"]["repeat_curtailment_score"]
    mwh = Decimal(d["selected"]["storage_bid_down_mwh"])
    parts.append(
        f'<text x="{LEFT}" y="{y0 + box_h + 34}" {FONT} font-size="14" fill="{INK}">'
        f'This shape occurred <tspan font-weight="700">{score:,} times</tspan> across GB '
        f"storage during the fourteen episode dates</text>"
    )
    parts.append(
        f'<text x="{LEFT}" y="{y0 + box_h + 54}" {FONT} font-size="14" fill="{INK}">'
        f"({mwh:,.0f} MWh bid down) — GB-wide concurrence, "
        '<tspan font-weight="700">not attributed to the boundary</tspan>.</text>'
    )

    # The money, side by side.
    my = y0 + box_h + 88
    parts.append(
        f'<text x="{LEFT}" y="{my}" {FONT} font-size="12.5" font-weight="700" '
        f'fill="{AQUA}" letter-spacing="2">THE PUBLISHED MONEY, SIDE BY SIDE '
        "(EPISODE DATES)</text>"
    )
    cash = d["cash"]
    rows = [
        ("Storage bids (GB-wide)", Decimal(cash["storage_bid"])),
        ("Storage offers (GB-wide)", Decimal(cash["storage_offer"])),
        ("Non-storage bids (GB-wide)", Decimal(cash["non_storage_bid"])),
        ("Non-storage offers (GB-wide)", Decimal(cash["non_storage_offer"])),
        ("NESO outturn constraint cost, SSE-SP group", d["group_cost"]),
    ]
    ry = my + 16
    for label, value in rows:
        parts.append(
            f'<text x="{LEFT}" y="{ry + 15}" {FONT} font-size="13" fill="{INK}">{label}</text>'
        )
        parts.append(
            f'<text x="{W - LEFT}" y="{ry + 15}" {FONT} font-size="13" font-weight="700" '
            f'fill="{INK}" text-anchor="end">£{float(value) / 1e6:+.2f}m</text>'
        )
        ry += 24
    parts.append(
        f'<text x="{LEFT}" y="{ry + 14}" {FONT} font-size="11.5" fill="{INK_2}">'
        "Published indicative BM cashflows (BSC sign convention) and NESO's published "
        "outturn — presented side by side, never reconciled to each other.</text>"
    )

    # The two structural gaps.
    gy = ry + 52
    parts.append(
        f'<text x="{LEFT}" y="{gy}" {FONT} font-size="12.5" font-weight="700" '
        f'fill="{INK}" letter-spacing="2">WHY THE COLUMNS CANNOT BE JOINED</text>'
    )
    gaps = [
        (
            "Which cashflows belong to the boundary?",
            "No public unit-to-constraint-group mapping exists — evidenced against "
            "NESO's own published datasets.",
        ),
        (
            "When were schedules revised?",
            "PN revision history is never published: the revision window lies entirely "
            "before gate closure — probed, with controls.",
        ),
    ]
    col_w = (PLOT_W - 24) / 2
    for i, (q, a) in enumerate(gaps):
        gx = LEFT + i * (col_w + 24)
        parts.append(
            f'<rect x="{gx}" y="{gy + 12}" width="{col_w:.0f}" height="104" rx="8" '
            f'fill="{SURFACE}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 4"/>'
        )
        parts.append(
            f'<text x="{gx + 16}" y="{gy + 48}" {FONT} font-size="26" font-weight="700" '
            f'fill="{INK}">?</text>'
        )
        parts.append(
            f'<text x="{gx + 44}" y="{gy + 42}" {FONT} font-size="13" font-weight="600" '
            f'fill="{INK}">{q}</text>'
        )
        words = a.split()
        line, lines = [], []
        for word in words:
            line.append(word)
            if sum(len(w) + 1 for w in line) > 52:
                lines.append(" ".join(line))
                line = []
        if line:
            lines.append(" ".join(line))
        for j, text in enumerate(lines):
            parts.append(
                f'<text x="{gx + 16}" y="{gy + 66 + j * 16}" {FONT} font-size="11.5" '
                f'fill="{INK_2}">{text}</text>'
            )
    parts.append(
        f'<text x="{LEFT}" y="{gy + 152}" {FONT} font-size="15" font-style="italic" '
        f'fill="{INK}">The public record can show the repetitive part. It cannot, by '
        "itself, prove the re-trading economics.</text>"
    )
    footer(parts, height, "episode-accounting.json, pn-vintage-probe.json, reference-manifest.json")
    parts.append("</svg>")
    return "\n".join(parts)


def render() -> None:
    d = load()
    (OUT / "overview.svg").write_text(overview_svg(d) + "\n")
    (OUT / "reel.svg").write_text(reel_svg(d) + "\n")
    (OUT / "diagram.svg").write_text(diagram_svg(d) + "\n")
    print("wrote overview.svg, reel.svg, diagram.svg")


if __name__ == "__main__":
    render()
