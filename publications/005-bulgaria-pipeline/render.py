"""Render Publication Pack 005's ladder from evidence.json only."""

import json
from pathlib import Path

from grid_mysteries.rendering.svg import BLUE, GRID, INK, INK_2, ORANGE, document, text

OUT = Path(__file__).resolve().parent
W, LEFT, RIGHT, BAR = 920, 48, 48, 22


def hbar(x: float, y: float, w: float, fill: str) -> str:
    r = min(4, w / 2)
    if w <= 0:
        return ""
    return (
        f'<path d="M{x:.1f},{y:.1f} H{x + w - r:.1f} A{r},{r} 0 0 1 {x + w:.1f},{y + r:.1f} '
        f"V{y + BAR - r:.1f} A{r},{r} 0 0 1 {x + w - r:.1f},{y + BAR:.1f} "
        f'H{x:.1f} Z" fill="{fill}"/>'
    )


def ladder() -> str:
    e = json.loads((OUT / "evidence.json").read_text())
    rows = e["figures"]
    ref = e["reference"]
    label_w = 330
    plot_w = W - LEFT - RIGHT - label_w - 110
    top, gap = 118, 44
    height = top + len(rows) * gap + 130
    parts = document(W, height, title="Bulgaria's data-centre pipeline, stage by stage (MW)")
    parts.append(
        text(
            30,
            60,
            "ESO EAD figures as of 3 August 2026; installed capacity as reported August 2026. "
            "One scale for all four bars.",
            size=13,
            fill=INK_2,
        )
    )
    top_mw = max(max(r["mw"] for r in rows), ref["mw"])
    scale = plot_w / top_mw
    x0 = LEFT + label_w
    for i, r in enumerate(rows):
        y = top + i * gap
        parts.append(text(x0 - 12, y + 16, r["stage"], size=13.5, fill=INK, anchor="end"))
        w = r["mw"] * scale
        last = i == len(rows) - 1
        parts.append(hbar(x0, y, max(w, 2.0) if r["mw"] > 0 else 0, ORANGE if last else BLUE))
        label = f"{r['mw']:,} MW" if r["mw"] else "0 MW"
        if last:
            label = f"≈{r['mw']} MW"
        parts.append(text(f"{x0 + max(w, 2.0) + 8:.1f}", y + 16, label, size=13.5, weight=700))
    rx = x0 + ref["mw"] * scale
    parts.append(
        f'<line x1="{rx:.1f}" y1="{top - 10}" x2="{rx:.1f}" y2="{top + len(rows) * gap}" '
        f'stroke="{INK_2}" stroke-width="1"/>'
    )
    parts.append(
        text(
            f"{rx:.1f}",
            top - 14,
            f"{ref['label']}: {ref['mw']:,} MW",
            size=12,
            fill=INK_2,
            anchor="middle",
        )
    )
    parts.append(
        f'<line x1="{x0}" y1="{top - 6}" x2="{x0}" y2="{top + len(rows) * gap}" '
        f'stroke="{GRID}" stroke-width="1"/>'
    )
    q = e["quote"]
    qy = top + len(rows) * gap + 30
    parts.append(text(30, qy, f"\u201c{q['translation']}\u201d", size=12.5, fill=INK))
    parts.append(
        text(30, qy + 18, f"\u2014 {q['who']}, Capital.bg, 19 August 2026", size=12, fill=INK_2)
    )
    parts.append(
        text(
            30,
            height - 40,
            "Sources per bar in evidence.json: economic.bg 2026-08-12 (ESO figures); "
            "Mediapool 2026-05-26;",
            size=11,
            fill=INK_2,
        )
    )
    parts.append(
        text(
            30,
            height - 24,
            "Capital.bg 2026-08-19; ESO draft development plan 2026\u20132035. "
            "Forward Mysteries F003 / F004.",
            size=11,
            fill=INK_2,
        )
    )
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    (OUT / "ladder.svg").write_text(ladder() + "\n")
    print("rendered ladder.svg")
