"""017 addendum — the storage rows of the committed census, re-read with a
proposed per-MW queue fee laid beside them as an illustration.

Pure logic over the census's **committed evidence lines**
(`evidence/rows.ndjson`, `evidence/gate-rows.ndjson`); it never reads the
register copy. It is written after both of 017's declarations ran and is
therefore **outside R7 and outside version 2's six breakdowns**: nothing
here is a census breakdown, nothing here is promoted to a governed slot,
and an outbound use of any figure below needs a declaration of its own,
frozen first.

Three things are kept apart, in this order, and the names say which:

- **observation** — which committed rows print a storage plant type, their
  MW, and how far behind the copy's own date each row's date sits;
- **interpretation** — what a *proposed* fee, known here only from a
  second-hand report, could be read as covering, and what the register
  cannot say about that;
- **illustration** — a per-MW rate multiplied by the observed MW. It is an
  arithmetic product of a proposed rate and a published capacity. It is
  not a saving, a loss, a liability, a forecast or a sum anyone owes.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from statistics import median
from typing import Any, Final

#: The register's own spelling of the storage plant type, as printed.
STORAGE_TOKEN: Final = "Energy Storage System"
STORAGE_ONLY: Final = "storage only"
STORAGE_COMPOUND: Final = "storage in a compound type"
NOT_STORAGE: Final = "not storage"
#: Duration buckets in days behind the as-of date, upper bounds inclusive.
BUCKETS: Final[tuple[tuple[str, int | None], ...]] = (
    ("up to 90 days", 90),
    ("91 to 365 days", 365),
    ("366 to 730 days", 730),
    ("more than 730 days", None),
)
ZERO: Final = Decimal(0)


def plant_tokens(plant_type: str) -> list[str]:
    """The compound plant type split on the register's `;`, each token with
    runs of whitespace collapsed; a blank cell yields no tokens."""
    return [" ".join(t.split()) for t in plant_type.split(";") if t.strip()]


def storage_class(plant_type: str) -> str:
    """Storage only, storage inside a compound type, or not storage. The
    token must equal the register's spelling exactly; nothing is inferred
    from `BESS`, `battery` or any other word in the row."""
    tokens = plant_tokens(plant_type)
    if STORAGE_TOKEN not in tokens:
        return NOT_STORAGE
    return STORAGE_ONLY if len(tokens) == 1 else STORAGE_COMPOUND


def days_behind(effective: date, as_of: date) -> int:
    """How many days before the copy's own date the row's date falls."""
    return (as_of - effective).days


def bucket(days: int) -> str:
    for label, upper in BUCKETS:
        if upper is None or days <= upper:
            return label
    raise AssertionError("unreachable: the last bucket is open-ended")


@dataclass(frozen=True)
class StorageRow:
    index: int
    project_name: str
    plant_type: str
    storage_class: str
    status: str
    mw: Decimal | None
    effective: date
    days_behind: int
    bucket: str
    #: The day-month swapped reading, where one exists (017 R3), kept so the
    #: addendum can say how many storage rows would read as future-dated.
    effective_swapped: date | None
    #: The Gate cell **only where version 2 committed it** (the confirmed
    #: tier's overdue rows); every other row is "not in the committed
    #: evidence", never blank, never inferred.
    gate: str | None


def storage_rows(
    committed: list[dict[str, Any]], as_of: date, gate_rows: list[dict[str, Any]]
) -> list[StorageRow]:
    """The committed census rows whose plant type carries the storage token."""
    gates = {g["index"]: str(g.get("gate", "")) for g in gate_rows}
    out = []
    for line in committed:
        plant = str(line.get("plant_type", ""))
        cls = storage_class(plant)
        if cls == NOT_STORAGE:
            continue
        effective = date.fromisoformat(line["effective"])
        swapped = line.get("effective_swapped")
        mw = line.get("mw")
        days = days_behind(effective, as_of)
        out.append(
            StorageRow(
                index=int(line["index"]),
                project_name=str(line.get("project_name", "")),
                plant_type=plant,
                storage_class=cls,
                status=str(line.get("status", "")),
                mw=Decimal(str(mw)) if mw is not None else None,
                effective=effective,
                days_behind=days,
                bucket=bucket(days),
                effective_swapped=date.fromisoformat(swapped) if swapped else None,
                gate=gates.get(int(line["index"])),
            )
        )
    rank = {STORAGE_ONLY: 0, STORAGE_COMPOUND: 1}
    return sorted(out, key=lambda r: (rank[r.storage_class], -(r.mw or ZERO), r.project_name))


def total_mw(rows: list[StorageRow]) -> Decimal:
    """MW of rows that carry a capacity; a row without one is absent from the
    total, not zero (017 R5)."""
    return sum((r.mw for r in rows if r.mw is not None), ZERO)


def duration_distribution(rows: list[StorageRow]) -> dict[str, Any]:
    """Rows and MW per bucket, plus the range and median in days."""
    days = sorted(r.days_behind for r in rows)
    per_bucket = []
    for label, _upper in BUCKETS:
        members = [r for r in rows if r.bucket == label]
        per_bucket.append({"bucket": label, "rows": len(members), "mw": total_mw(members)})
    return {
        "rows": len(rows),
        "mw": total_mw(rows),
        "days_behind_min": days[0] if days else None,
        "days_behind_median": median(days) if days else None,
        "days_behind_max": days[-1] if days else None,
        "buckets": per_bucket,
    }


def by_plant_type(rows: list[StorageRow]) -> list[dict[str, Any]]:
    groups: dict[str, list[StorageRow]] = {}
    for r in rows:
        groups.setdefault(r.plant_type, []).append(r)
    out = [
        {
            "plant_type": k,
            "storage_class": members[0].storage_class,
            "rows": len(members),
            "mw": total_mw(members),
        }
        for k, members in groups.items()
    ]
    return sorted(out, key=lambda g: (-g["mw"], g["plant_type"]))


def illustration(mw: Decimal, rates_per_mw: list[Decimal]) -> list[dict[str, Any]]:
    """Rate times MW, as `Decimal`, and nothing else. The caller labels it."""
    return [{"rate_gbp_per_mw": rate, "mw": mw, "gbp": rate * mw} for rate in rates_per_mw]


def addendum(
    committed: list[dict[str, Any]],
    as_of: date,
    gate_rows: list[dict[str, Any]],
    rates_per_mw: list[Decimal],
) -> dict[str, Any]:
    """The whole addendum as one dict, observation first, illustration last."""
    rows = storage_rows(committed, as_of, gate_rows)
    committed_mw = sum(
        (Decimal(str(line["mw"])) for line in committed if line.get("mw") is not None), ZERO
    )
    only = [r for r in rows if r.storage_class == STORAGE_ONLY]
    compound = [r for r in rows if r.storage_class == STORAGE_COMPOUND]
    unreadable = sum(1 for line in committed if not plant_tokens(str(line.get("plant_type", ""))))
    confirmed = [r for r in rows if r.gate == "2"]
    swapped_future = [
        r for r in rows if r.effective_swapped is not None and r.effective_swapped >= as_of
    ]
    return {
        "observation": {
            "as_of": as_of,
            "committed_rows": len(committed),
            "committed_mw": committed_mw,
            "rows_with_no_readable_plant_type": unreadable,
            "storage_rows": len(rows),
            "storage_mw": total_mw(rows),
            "storage_row_share_of_census": _share(len(rows), len(committed)),
            "storage_capacity_share_of_census": _share(total_mw(rows), committed_mw),
            "storage_rows_zero_capacity": sum(1 for r in rows if r.mw == ZERO),
            "storage_rows_without_capacity": sum(1 for r in rows if r.mw is None),
            "storage_only": duration_distribution(only),
            "storage_compound": duration_distribution(compound),
            "by_plant_type": by_plant_type(rows),
            "by_status": _by_status(rows),
            "confirmed_tier_storage_rows": len(confirmed),
            "confirmed_tier_storage_mw": total_mw(confirmed),
            "confirmed_tier_storage": [r.project_name for r in confirmed],
            "gate_not_in_committed_evidence_rows": sum(1 for r in rows if r.gate is None),
            "storage_rows_swapped_reading_in_future": len(swapped_future),
            "storage_mw_swapped_reading_in_future": total_mw(swapped_future),
            "rows": rows,
        },
        "illustration": {
            "rates_gbp_per_mw": rates_per_mw,
            "storage_only": illustration(total_mw(only), rates_per_mw),
            "storage_only_and_compound": illustration(total_mw(rows), rates_per_mw),
            "confirmed_tier_storage": illustration(total_mw(confirmed), rates_per_mw),
        },
    }


def _share(part: Decimal | int, whole: Decimal | int) -> Decimal | None:
    """A share to four places, or None when the whole is nothing (017 R11:
    a row share and a capacity share are two numbers, never one)."""
    if not whole:
        return None
    return (Decimal(part) / Decimal(whole)).quantize(Decimal("0.0001"))


def _by_status(rows: list[StorageRow]) -> list[dict[str, Any]]:
    groups: dict[str, list[StorageRow]] = {}
    for r in rows:
        groups.setdefault(r.status, []).append(r)
    out = [{"status": k, "rows": len(m), "mw": total_mw(m)} for k, m in groups.items()]
    return sorted(out, key=lambda g: (-g["mw"], g["status"]))
