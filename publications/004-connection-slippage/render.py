"""Render Publication Pack 004's two visuals from committed evidence only.

Rates, counts and the pooled base rate are read from 005's and 006's
evidence summaries; nothing is typed here.
"""

import json
from decimal import Decimal
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.rendering.svg import BLUE, GRID, INK, INK_2, ORANGE, document, text

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


def slip_by_status() -> str:
    summary = json.loads(E005.read_text())
    rates = next(r for r in summary["q2"] if r["name"] == "first_status")["rates"]
    rows = sorted(
        ((r["stratum"], int(r["n"]), Decimal(r["rate_ge_24"])) for r in rates if int(r["n"]) >= 30),
        key=lambda t: t[2],
        reverse=True,
    )
    pooled = Decimal(summary["q3"]["pooled_rate"])
    label_w = 300
    plot_w = W - LEFT - RIGHT - label_w - 90
    top, gap = 118, 40
    height = top + len(rows) * gap + 80
    parts = document(
        W, height, title="Which grid connection dates slip? Share slipping by two years or more"
    )
    parts.append(
        text(
            30,
            60,
            "GB transmission-connected projects by the status they carried when first "
            "seen in the TEC Register, 2014–2025 (old regime)",
            size=13,
            fill=INK_2,
        )
    )
    parts.append(
        text(
            30,
            80,
            f"n = {summary['q1']['n']:,} project-stages observed ≥ 2 years; "
            "bars are the share whose contracted date moved ≥ 24 months",
            size=13,
            fill=INK_2,
        )
    )
    scale = plot_w / 0.40
    x0 = LEFT + label_w
    for i, (status, n, rate) in enumerate(rows):
        y = top + i * gap
        parts.append(text(x0 - 12, y + 16, status, size=13.5, fill=INK, anchor="end"))
        w = float(rate) * scale
        parts.append(hbar(x0, y, w, BLUE))
        parts.append(text(f"{x0 + w + 8:.1f}", y + 16, pct(rate), size=13.5, weight=700))
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
            "Source: NESO TEC Register archive (FOI-24-0031, FOI-24-0040, FOI-25-129, "
            "FOI-26-051, Wayback), Investigation 005. Pre-declared thresholds; see expert corner.",
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
    top, gap = 118, 44
    height = top + len(rows) * gap + 100
    parts = document(
        W, height, title="Does a late network make a late project? Not in the public record"
    )
    parts.append(
        text(
            30,
            60,
            "Same population, matched to NESO's Transmission Works Register (31 reports, "
            "2017–2025). Share slipping ≥ 24 months, by whether the project's",
            size=13,
            fill=INK_2,
        )
    )
    parts.append(
        text(
            30,
            80,
            "enabling works had already slipped within a year of the project first appearing.",
            size=13,
            fill=INK_2,
        )
    )
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
