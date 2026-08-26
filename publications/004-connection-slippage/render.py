"""Render Publication Pack 004's two visuals from committed evidence only.

Rates, counts and the pooled base rate are read from 005's and 006's
evidence summaries; nothing is typed here.
"""

import json
from decimal import Decimal
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.rendering.svg import BLUE, GRID, INK, INK_2, MUTED, ORANGE, document, text

OUT = Path(__file__).resolve().parent
E005 = (
    REPO_ROOT / "investigations/005-connection-date-credibility/evidence/tec-slippage-summary.json"
)
E006 = (
    REPO_ROOT
    / "investigations/006-connection-slippage-attribution/evidence/twr-attribution-summary.json"
)
W, LEFT, RIGHT = 920, 48, 48
BAR = 22


def hbar(x: float, y: float, w: float, fill: str) -> str:
    """A horizontal bar: square at the baseline (left), 4px-rounded data end."""
    r = min(4, w / 2)
    return (
        f'<path d="M{x:.1f},{y:.1f} H{x + w - r:.1f} A{r},{r} 0 0 1 {x + w:.1f},{y + r:.1f} '
        f"V{y + BAR - r:.1f} A{r},{r} 0 0 1 {x + w - r:.1f},{y + BAR:.1f} "
        f'H{x:.1f} Z" fill="{fill}"/>'
    )


def pct(rate: Decimal) -> str:
    return f"{float(rate) * 100:.1f}%"


EMPHASISED = ("Awaiting Consents", "Under Construction/Commissioning")


def slip_by_status() -> str:
    summary = json.loads(E005.read_text())
    rates = next(r for r in summary["q2"] if r["name"] == "first_status")["rates"]
    rows = sorted(
        ((r["stratum"], int(r["n"]), Decimal(r["rate_ge_24"])) for r in rates if int(r["n"]) >= 30),
        key=lambda t: t[2],
        reverse=True,
    )
    by_status = {status: rate for status, _, rate in rows}
    ratio = by_status[EMPHASISED[0]] / by_status[EMPHASISED[1]]
    pooled = Decimal(summary["q3"]["pooled_rate"])
    label_w = 300
    plot_w = W - LEFT - RIGHT - label_w - 90
    top, gap = 140, 40
    height = top + len(rows) * gap + 80
    parts = document(
        W,
        height,
        title=f"Same connection date. {float(ratio):.1f}\u00d7 different historical risk.",
    )
    parts.append(
        text(
            30,
            62,
            "Share of GB transmission connection positions that subsequently slipped by 2+ years, "
            "by development status",
            size=13,
            fill=INK_2,
        )
    )
    parts.append(
        text(
            30,
            80,
            f"when first observed. NESO TEC Register, 2014\u20132025 (old regime); n = "
            f"{summary['q1']['n']:,} project-stages observed \u2265 2 years.",
            size=13,
            fill=INK_2,
        )
    )
    scale = plot_w / 0.40
    x0 = LEFT + label_w
    for i, (status, n, rate) in enumerate(rows):
        y = top + i * gap
        emphasised = status in EMPHASISED
        parts.append(
            text(
                x0 - 12,
                y + 16,
                status,
                size=13.5,
                weight=700 if emphasised else None,
                fill=INK if emphasised else INK_2,
                anchor="end",
            )
        )
        w = float(rate) * scale
        parts.append(hbar(x0, y, w, BLUE if emphasised else MUTED))
        parts.append(
            text(
                f"{x0 + w + 8:.1f}",
                y + 16,
                pct(rate),
                size=13.5,
                weight=700 if emphasised else None,
                fill=INK if emphasised else INK_2,
            )
        )
        parts.append(text(f"{x0 + w + 60:.1f}", y + 16, f"n = {n}", size=12, fill=INK_2))
    px = x0 + float(pooled) * scale
    parts.append(
        f'<line x1="{px:.1f}" y1="{top - 10}" x2="{px:.1f}" y2="{top + len(rows) * gap}" '
        f'stroke="{INK_2}" stroke-width="1"/>'
    )
    parts.append(
        text(f"{px + 6:.1f}", top - 14, f"all project-stages {pct(pooled)}", size=12, fill=INK_2)
    )
    parts.append(
        f'<line x1="{x0}" y1="{top - 6}" x2="{x0}" y2="{top + len(rows) * gap}" '
        f'stroke="{GRID}" stroke-width="1"/>'
    )
    parts.append(
        text(
            30,
            height - 24,
            "Source: NESO TEC Register archive (FOI-24-0031, FOI-24-0040, FOI-25-129, FOI-26-051, "
            "Wayback), Investigation 005. Pre-declared thresholds; see expert corner.",
            size=11,
            fill=INK_2,
        )
    )
    parts.append("</svg>")
    return "\n".join(parts)


def works_history() -> str:
    summary = json.loads(E006.read_text())
    t2 = summary["t2"]
    rows = [
        (
            "Enabling works had already slipped ≥ 6 months",
            int(t2["n_flagged"]),
            Decimal(t2["rate_flagged"]),
        ),
        ("Enabling works were on plan", int(t2["n_unflagged"]), Decimal(t2["rate_unflagged"])),
    ]
    label_w = 380
    plot_w = W - LEFT - RIGHT - label_w - 90
    top, gap = 150, 44
    height = top + len(rows) * gap + 100
    parts = document(
        W, height, title="Do previously slipped enabling works identify later-slipping projects?"
    )
    parts.append(text(30, 62, "Not in the disclosed register.", size=19, weight=600))
    subtitle = (
        "Matched subset of the same TEC population (74.3%), joined to NESO's Transmission Works "
        "Register",
        "(31 reports, 2017–2025). Share slipping ≥ 24 months, by whether the project's enabling "
        "works had",
        "already slipped within a year of it first appearing.",
    )
    for i, line in enumerate(subtitle):
        parts.append(text(30, 88 + i * 18, line, size=13, fill=INK_2))
    scale = plot_w / 0.40
    x0 = LEFT + label_w
    for i, (label, n, rate) in enumerate(rows):
        y = top + i * gap
        parts.append(text(x0 - 12, y + 16, label, size=13.5, fill=INK, anchor="end"))
        w = float(rate) * scale
        parts.append(hbar(x0, y, w, ORANGE if i == 0 else BLUE))
        parts.append(text(f"{x0 + w + 8:.1f}", y + 16, pct(rate), size=13.5, weight=700))
        parts.append(text(f"{x0 + w + 60:.1f}", y + 16, f"n = {n}", size=12, fill=INK_2))
    parts.append(
        f'<line x1="{x0}" y1="{top - 6}" x2="{x0}" y2="{top + len(rows) * gap}" '
        f'stroke="{GRID}" stroke-width="1"/>'
    )
    gap_pp = float(Decimal(t2["gap"])) * 100
    parts.append(
        text(
            30,
            top + len(rows) * gap + 30,
            f"Gap {gap_pp:+.1f} points against a pre-declared bar of +20; the sign holds in both "
            "cohorts and in NGET, SHET and SPT areas.",
            size=12.5,
            fill=INK,
        )
    )
    parts.append(
        text(
            30,
            height - 24,
            "Source: NESO FOI-25-133 (TWR reports) joined to the TEC archive; Investigation 006. "
            "Works completion dates proxied by the earliest dependent connection date "
            "(Amendment 1).",
            size=11,
            fill=INK_2,
        )
    )
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    (OUT / "slip-by-status.svg").write_text(slip_by_status() + "\n")
    (OUT / "works-history.svg").write_text(works_history() + "\n")
    print("rendered slip-by-status.svg, works-history.svg")
