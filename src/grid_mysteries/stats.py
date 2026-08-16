"""Small shared numerics for study aggregation."""

from __future__ import annotations


def percentile(sorted_values: list, fraction: float):
    """Nearest-rank percentile over an already-sorted list (the convention
    declared and used by the method studies)."""
    index = min(len(sorted_values) - 1, int(fraction * len(sorted_values)))
    return sorted_values[index]
