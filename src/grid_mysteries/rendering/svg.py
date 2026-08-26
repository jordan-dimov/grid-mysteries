"""Shared tokens and primitives for the project's self-contained SVG charts.

The validated reference dataviz palette (light surface committed
deliberately — charts are viewed on repository pages): ordinal blue ramp
for before/after and funnel stages, categorical slots for part-to-whole,
a warm diverging pole, ink tokens for all text. Chart *composition* stays
with each study's renderer; only the design constants and the two
attribute-order-stable primitives below are shared, so every chart draws
from one validated palette and every text element serialises identically.
"""

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e5e4e0"

# Ordinal blue ramp (validated light-end at 2.06:1) and categorical slots.
BLUE_LIGHT = "#86b6ef"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
# Diverging warm pole (validated reference palette slot).
RED = "#e34948"

FONT = "font-family=\"system-ui, 'Segoe UI', sans-serif\""


def text(
    x: float | str,
    y: float | str,
    content: str,
    *,
    size: float | str,
    weight: int | None = None,
    fill: str = INK,
    anchor: str | None = None,
) -> str:
    """One `<text>` element. Attribute order is fixed (x, y, font, size,
    weight, fill, anchor) because committed SVGs are diffed byte-for-byte;
    coordinates are interpolated exactly as passed, so a caller that wants
    `.1f` formatting passes the formatted string."""
    attributes = f'x="{x}" y="{y}" {FONT} font-size="{size}"'
    if weight is not None:
        attributes += f' font-weight="{weight}"'
    attributes += f' fill="{fill}"'
    if anchor is not None:
        attributes += f' text-anchor="{anchor}"'
    return f"<text {attributes}>{content}</text>"


def document(
    width: float | str,
    height: float | str,
    *,
    title: str | None = None,
    x: float | str = 30,
    y: float | str = 36,
    size: float | str = 19,
    weight: int = 600,
) -> list[str]:
    """The opening lines of a chart: root element, painted surface and,
    when given, the title text at (x, y)."""
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
    ]
    if title is not None:
        lines.append(text(x, y, title, size=size, weight=weight))
    return lines
