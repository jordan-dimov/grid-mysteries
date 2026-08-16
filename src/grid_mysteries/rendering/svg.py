"""Shared tokens for the project's self-contained SVG charts.

The validated reference dataviz palette (light surface committed
deliberately — charts are viewed on repository pages): ordinal blue ramp
for before/after and funnel stages, categorical slots for part-to-whole,
ink tokens for all text. Chart *composition* stays with each study's
renderer; only the design constants are shared, so every chart draws
from one validated palette.
"""

from __future__ import annotations

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e5e4e0"

# Ordinal blue ramp (validated light-end at 2.06:1) and categorical slots.
BLUE_LIGHT = "#86b6ef"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"

FONT = "font-family=\"system-ui, 'Segoe UI', sans-serif\""
