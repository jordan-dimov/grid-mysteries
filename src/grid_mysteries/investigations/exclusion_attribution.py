"""Attribution of screen-vs-NESO disagreement cells to NESO exclusion categories.

Method Study 001C joins every disagreement cell (feasibility-aware screen
flags it; NESO stage 5 records no skip) to NESO's published Exclusion
Reasons rows. This module holds the pure mapping rules; they are declared
in METHOD-STUDY-001C.md before any window aggregate is computed.

NESO reason strings may be comma-joined compounds of atomic reasons. The
atomic vocabulary below was confirmed from the July 2026 resource
(outside the study corpus); an unrecognised fragment is preserved as
``unrecognised`` rather than silently dropped.
"""

from __future__ import annotations

from decimal import Decimal

#: Atomic reason -> category, in the declared layer order (July 2026
#: frequency order; groups declared up front).
ATOMIC_REASON_CATEGORY = {
    "Wind offer": "wind_offer",
    "Behind constraint": "behind_constraint",
    "System-tagged": "system_tagged",
    "Unwind": "unwind",
    "Unit ramping between 0 and SEL or 0 and SIL": "ramping",
    "Long notice 0 to SIL or 0 to SEL": "long_notice_or_access",
    "Cannot take a long notice unit offline": "long_notice_or_access",
    "Inaccessible long notice unit": "long_notice_or_access",
    "Inaccessible very long notice unit": "long_notice_or_access",
    "Inaccessible pumped storage through zero": "long_notice_or_access",
    "Invalid physical/dynamic parameter": "invalid_parameters",
}

#: Cumulative waterfall layer order (fixed, declared before computation).
LAYER_ORDER = [
    "wind_offer",
    "behind_constraint",
    "system_tagged",
    "unwind",
    "ramping",
    "long_notice_or_access",
    "invalid_parameters",
    "unrecognised",
]


def split_reasons(reason_string: str) -> list[str]:
    """Split a possibly compound NESO reason string into atomic reasons.

    Compounds are ", "-joined atomics; splitting greedily rejoins fragments
    that belong to one atomic reason containing a comma (none observed, but
    the fallback keeps unknown text visible as a single fragment).
    """
    fragments = [fragment.strip() for fragment in reason_string.split(",")]
    reasons: list[str] = []
    pending = ""
    for fragment in fragments:
        candidate = f"{pending}, {fragment}" if pending else fragment
        if candidate in ATOMIC_REASON_CATEGORY:
            reasons.append(candidate)
            pending = ""
        elif fragment in ATOMIC_REASON_CATEGORY:
            if pending:
                reasons.append(pending)
            reasons.append(fragment)
            pending = ""
        else:
            pending = candidate
    if pending:
        reasons.append(pending)
    return reasons


def categorise(reason_string: str) -> list[str]:
    return [
        ATOMIC_REASON_CATEGORY.get(reason, "unrecognised")
        for reason in split_reasons(reason_string)
    ]


def excluded_volume_by_category(rows: list[dict]) -> dict[str, Decimal]:
    """Sum absolute excluded volume per category over a cell's exclusion rows.

    A compound row's volume counts once per category it names (the split is
    not published), so per-category volumes overlap by design; they rank
    categories, they do not partition energy.
    """
    volumes: dict[str, Decimal] = {}
    for row in rows:
        volume = abs(Decimal(row["excluded_volume_MWh"] or "0"))
        for category in set(categorise(row["exclusion_reason"])):
            volumes[category] = volumes.get(category, Decimal(0)) + volume
    return volumes


def primary_category(rows: list[dict]) -> str | None:
    """The cell's primary attribution: largest excluded volume, ties broken
    by the declared layer order. None when the cell has no exclusion rows."""
    volumes = excluded_volume_by_category(rows)
    if not volumes:
        return None
    order = {category: index for index, category in enumerate(LAYER_ORDER)}
    return min(volumes, key=lambda c: (-volumes[c], order.get(c, len(order))))
