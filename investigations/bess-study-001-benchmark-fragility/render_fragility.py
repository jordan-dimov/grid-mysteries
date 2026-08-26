"""Render BESS Study 001's two charts as self-contained SVGs.

Reads ``evidence/fragility-analysis.json`` only — no number is typed by
hand. Semantics per the study Corrections: R3h/R3p are two
information-set views branching from the duration constraint, never
monotonic rungs; the revision flows are drawn as a diverging pair, not a
net bar.
"""

import json
from decimal import Decimal

from grid_mysteries.evidence import evidence_dir
from grid_mysteries.rendering.svg import BLUE, BLUE_LIGHT, GRID, INK, INK_2, RED, document, text

EVIDENCE = evidence_dir(__file__)
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


def heading(title: str, subtitle: str, height: int) -> list[str]:
    return [
        *document(W, height, title=title, x=LEFT, y=42, size=20, weight=700),
        text(LEFT, 66, subtitle, size=13, fill=INK_2),
    ]


def ladder_svg(d: dict) -> str:
    height = 700
    parts = heading(
        "Benchmark fragility: a battery counterfactual, made credible in stages",
        "July 2026, four-unit GC0166 early-submitter panel. Every figure is arithmetic "
        "on public numbers — never savings or achievable value.",
        height,
    )
    plot_w = W - 2 * LEFT - 200

    # Act 1: the collapse (R1 -> R2), drawn at R1 scale.
    parts.append(text(LEFT, 106, "1 · The price-only construct meets physics", size=14, weight=600))
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
            text(
                LEFT + bar + 10,
                y + 20,
                f"{money(value)} · {pct(value, d['r1'])} of R1",
                size=14,
                weight=700,
            )
        )
        parts.append(text(LEFT, y + 44, label, size=12, fill=INK_2))

    # Act 2: the duration constraint BRANCHES into two information sets,
    # drawn at R2 scale.
    parts.append(
        text(
            LEFT,
            292,
            "2 · The new GC0166 duration envelope — two information sets, not one rung",
            size=14,
            weight=600,
        )
    )
    parts.append(
        text(
            LEFT,
            312,
            f"(drawn at power-feasible scale, {money(d['r2'])} = full width; the two views are "
            "non-monotonic between each other)",
            size=12,
            fill=INK_2,
        )
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
            text(
                LEFT + bar + 10,
                y + 20,
                f"{money(value)} · {pct(value, d['r1'])} of R1",
                size=14,
                weight=700,
            )
        )
        parts.append(text(LEFT, y + 44, label, size=12, fill=INK_2))
    parts.append(
        text(
            LEFT,
            478,
            'Duration-awareness removed <tspan font-weight="700">'
            f"{(1 - d['r3h'] / d['r2']):.1%}</tspan> of what physics alone permitted.",
            size=13,
        )
    )

    # Act 3: operational-context disclosure.
    parts.append(
        text(LEFT, 530, "3 · Operational-context disclosure (not a verdict)", size=14, weight=600)
    )
    bar = max(4, round(plot_w * float(d["r4"] / d["r2"])))
    parts.append(f'<rect x="{LEFT}" y="546" width="{bar}" height="30" rx="4" fill="{INK}"/>')
    parts.append(
        text(
            LEFT + bar + 10,
            566,
            f"{money(d['r4'])} · {pct(d['r4'], d['r1'])} of R1",
            size=14,
            weight=700,
        )
    )
    parts.append(
        text(
            LEFT,
            590,
            "carries no published NESO exclusion context on either side of the comparison",
            size=12,
            fill=INK_2,
        )
    )
    parts.append(
        text(
            LEFT,
            646,
            "Sources: evidence/fragility-analysis.json · findings fnd-bess-001-fragility "
            "and fnd-bess-001-fragility-corrected · github.com/jordan-dimov/grid-mysteries",
            size=12,
            fill=INK_2,
        )
    )
    parts.append("</svg>")
    return "\n".join(parts)


def revisions_svg(d: dict) -> str:
    height = 420
    mid_x = W / 2
    scale = (W / 2 - 80) / float(max(d["future_only"], d["revised_away"]))
    parts = heading(
        "Hindsight does not just know more — it revises the feasible state",
        "Final-vintage MDO/MDB versus the envelope publicly observable 60 minutes before "
        "delivery, per settlement period, July 2026 panel.",
        height,
    )
    parts.append(
        f'<line x1="{mid_x}" y1="100" x2="{mid_x}" y2="300" stroke="{GRID}" stroke-width="2"/>'
    )
    added_w = round(float(d["future_only"]) * scale)
    removed_w = round(float(d["revised_away"]) * scale)
    parts.append(f'<rect x="{mid_x}" y="130" width="{added_w}" height="44" rx="4" fill="{BLUE}"/>')
    parts.append(
        text(
            mid_x + 12,
            130 - 10,
            f"+{money(d['future_only'])} added in hindsight",
            size=14,
            weight=700,
        )
    )
    parts.append(
        text(
            mid_x + 12,
            130 + 62,
            f"{d['n_future']:,} periods where the supporting envelope was published only "
            "after the decision cutoff",
            size=12,
            fill=INK_2,
        )
    )
    parts.append(
        f'<rect x="{mid_x - removed_w}" y="216" width="{removed_w}" height="44" rx="4" '
        f'fill="{RED}"/>'
    )
    parts.append(
        text(
            mid_x - 12,
            216 - 10,
            f"−{money(d['revised_away'])} revised away",
            size=14,
            weight=700,
            anchor="end",
        )
    )
    parts.append(
        text(
            mid_x - 12,
            216 + 62,
            f"{d['n_revised']:,} periods where the final vintage withdrew "
            "opportunity the public envelope had supported",
            size=12,
            fill=INK_2,
            anchor="end",
        )
    )
    net = d["future_only"] - d["revised_away"]
    parts.append(
        text(
            LEFT,
            340,
            f'The pooled net, <tspan font-weight="700">{money(net)}</tspan>, conceals both '
            "flows. Either direction grades a historical decision against a revised "
            "information set.",
            size=13,
        )
    )
    parts.append(
        text(
            LEFT,
            390,
            "Proves public availability only, never control-room knowledge. Sources: "
            "evidence/fragility-analysis.json · fnd-bess-001-fragility-corrected",
            size=12,
            fill=INK_2,
        )
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
