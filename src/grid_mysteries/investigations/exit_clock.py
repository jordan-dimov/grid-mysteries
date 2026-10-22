"""025 — The exit clock: pure rules.

Chains of TEC Register rows across copies, their last sighting, the User
Commitment trigger date implied by a printed connection date, the bands
around it and the hazard (exits per chain-month at risk) in each band. No
I/O; the runner (`investigations/025-the-exit-clock/run.py`) owns files.

The rules are those of `investigations/025-the-exit-clock/DECLARATION.md`;
the declaration's digest is recorded in the results, not here.
"""

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Final

from grid_mysteries.sources.tec_register import (
    normalise,
    normalise_stage,
    parse_date,
    parse_decimal,
)

#: Project ID is printed from this copy on (archive schema report, era table).
ID_ERA_FROM: Final = date(2021, 11, 26)
#: 014's regime break: copies dated here or later are the reformed regime.
REGIME_CUTOFF: Final = date(2025, 12, 1)
#: Salesforce ids print at 15 or 18 characters; the first 15 are the key (017).
ID_LENGTH: Final = 15
#: A copy pair in which more than this share of the earlier copy's keys is
#: absent from the later copy is a re-keying, not a set of departures.
REKEY_SHARE: Final = Decimal("0.5")
#: Built is the status that ends a chain without an exit.
BUILT: Final = "built"

READ_COLUMNS: Final = (
    "Project ID",
    "Project Number",
    "Project Name",
    "Customer Name",
    "Connection Site",
    "Stage",
    "Project Status",
    "Plant Type",
    "Agreement Type",
    "HOST TO",
    "MW Increase / Decrease",
    "Cumulative Total Capacity (MW)",
    "MW Effective From",
    "Gate",
)

BANDS: Final = (
    "more than 24 months before",
    "12 to 24 months before",
    "0 to 12 months before",
    "0 to 12 months after",
    "more than 12 months after",
)
UNDATED: Final = "no connection date"


# ------------------------------------------------------------------ keys


def text(value: object) -> str:
    return " ".join(str(value or "").split())


def project_id(row: dict[str, object]) -> str:
    return "".join(str(row.get("Project ID") or "").split())[:ID_LENGTH]


def triple(row: dict[str, object]) -> str:
    return "|".join(
        (
            normalise(row.get("Project Name")),
            normalise(row.get("Customer Name")),
            normalise(row.get("Connection Site")),
        )
    )


def is_id_era(t_public: date) -> bool:
    return t_public >= ID_ERA_FROM


def row_key(row: dict[str, object], t_public: date) -> str:
    """The chain key a row carries in a copy: its Project ID in the ID era
    (`id:`), else 005's normalised (name, customer, site) triple (`name:`).
    An ID-era row with no id falls back to the triple, marked so."""
    if is_id_era(t_public):
        pid = project_id(row)
        if pid:
            return f"id:{pid}"
        return f"noid:{triple(row)}"
    return f"name:{triple(row)}"


# ------------------------------------------------- admissible rows (I10)

#: Amendment 1 (22/10/2026): the register's fields besides the Project Name.
#: A row is a project row only if it prints the name and at least one of these.
ADMISSIBLE_FIELDS: Final = (
    "Customer Name",
    "Connection Site",
    "Project Status",
    "Plant Type",
    "HOST TO",
    "Agreement Type",
    "MW Connected",
    "MW Increase / Decrease",
    "Cumulative Total Capacity (MW)",
    "MW Effective From",
    "Stage",
    "Project ID",
    "Project Number",
    "Gate",
)


def fields_printed(row: dict[str, object]) -> tuple[str, ...]:
    """The admissible fields a row prints (non-blank), in the declared order."""
    return tuple(f for f in ADMISSIBLE_FIELDS if text(row.get(f)))


def admissible(row: dict[str, object]) -> bool:
    """I10: a row is admitted to chain-building only if it prints a Project
    Name and at least one other field of the register. A row printing a name
    alone, or no name, is a print artefact (a footer, a note, a heading).
    Nothing else about the row is read to decide."""
    return bool(text(row.get("Project Name"))) and bool(fields_printed(row))


def admit(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], int]:
    """The admitted rows of a copy, in printed order, and the count refused.
    The printed count (len(rows)) is what the partial-export rule and R3 see."""
    admitted = [r for r in rows if admissible(r)]
    return admitted, len(rows) - len(admitted)


def keyed(rows: list[dict[str, object]], t_public: date) -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = defaultdict(list)
    for r in rows:
        out[row_key(r, t_public)].append(r)
    return dict(out)


# ---------------------------------------------------------- continuity


@dataclass(frozen=True)
class Continuity:
    earlier: date
    later: date
    keys_earlier: int
    keys_later: int
    absent_from_later: int
    new_in_later: int

    @property
    def absent_share(self) -> Decimal:
        if not self.keys_earlier:
            return Decimal(0)
        return (Decimal(self.absent_from_later) / Decimal(self.keys_earlier)).quantize(
            Decimal("0.0001")
        )

    @property
    def rekeying(self) -> bool:
        return self.absent_share > REKEY_SHARE


def continuity(
    earlier: date, later: date, keys_earlier: set[str], keys_later: set[str]
) -> Continuity:
    return Continuity(
        earlier,
        later,
        len(keys_earlier),
        len(keys_later),
        len(keys_earlier - keys_later),
        len(keys_later - keys_earlier),
    )


# ------------------------------------------------------------ stitching

#: Matching tiers at a re-keying copy, strictest first. Each is the set of
#: row features that must agree between an unmatched row of the copy before
#: and an unmatched row of the re-keying copy.
STITCH_TIERS: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    ("project number", ("number",)),
    ("all five", ("name", "customer", "site", "stage", "cumulative")),
    ("name, site, stage", ("name", "site", "stage")),
    ("name, customer, stage", ("name", "customer", "stage")),
    ("name, customer, site", ("name", "customer", "site")),
    ("name, stage, cumulative", ("name", "stage", "cumulative")),
    ("customer, site, stage, cumulative", ("customer", "site", "stage", "cumulative")),
    ("name alone", ("name",)),
)


def features(row: dict[str, object]) -> dict[str, str]:
    """The row features the stitch compares. `number` is the Project Number
    where printed, else a per-row nonce that can match nothing."""
    cumulative = parse_decimal(row.get("Cumulative Total Capacity (MW)"))
    number = text(row.get("Project Number"))
    return {
        "number": number if number else f"\x00{id(row)}",
        "name": normalise(row.get("Project Name")),
        "customer": normalise(row.get("Customer Name")),
        "site": normalise(row.get("Connection Site")),
        "stage": normalise_stage(row.get("Stage")) or "1",
        "cumulative": str(cumulative.normalize()) if cumulative is not None else "",
    }


def chain_signature(rows: list[dict[str, object]], fields: tuple[str, ...]) -> tuple[str, ...]:
    """A chain's signature over its rows: the sorted tuple of per-row feature
    tuples, so a two-stage project matches a two-stage project."""
    return tuple(sorted("\x1f".join(features(r)[f] for f in fields) for r in rows))


@dataclass
class Stitch:
    """The outcome of matching the chains that vanish at a re-keying copy to
    the chains that appear in it."""

    matched: dict[str, str] = field(default_factory=dict)  # new key -> old key
    tier_of: dict[str, str] = field(default_factory=dict)  # new key -> tier label
    ambiguous_old: list[str] = field(default_factory=list)
    ambiguous_new: list[str] = field(default_factory=list)
    unmatched_old: list[str] = field(default_factory=list)
    unmatched_new: list[str] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        tiers = Counter(self.tier_of.values())
        return {
            "matched": len(self.matched),
            **{f"tier {label}": tiers.get(label, 0) for label, _ in STITCH_TIERS},
            "ambiguous_old": len(self.ambiguous_old),
            "ambiguous_new": len(self.ambiguous_new),
            "unmatched_old": len(self.unmatched_old),
            "unmatched_new": len(self.unmatched_new),
        }


def stitch(
    vanished: dict[str, list[dict[str, object]]],
    appeared: dict[str, list[dict[str, object]]],
) -> Stitch:
    """Match vanished chains to appeared chains tier by tier. Within a tier a
    signature shared by exactly one vanished and one appeared chain is a
    match; a signature shared by several on either side is ambiguous and
    those chains are left to the next tier; chains unmatched after the last
    tier are unmatched (an unmatched appeared chain is a new chain)."""
    out = Stitch()
    old_left = dict(vanished)
    new_left = dict(appeared)
    for label, fields in STITCH_TIERS:
        by_sig_old: dict[tuple[str, ...], list[str]] = defaultdict(list)
        by_sig_new: dict[tuple[str, ...], list[str]] = defaultdict(list)
        for k, rows in old_left.items():
            by_sig_old[chain_signature(rows, fields)].append(k)
        for k, rows in new_left.items():
            by_sig_new[chain_signature(rows, fields)].append(k)
        for sig, olds in by_sig_old.items():
            news = by_sig_new.get(sig)
            if not news:
                continue
            if len(olds) == 1 and len(news) == 1:
                out.matched[news[0]] = olds[0]
                out.tier_of[news[0]] = label
                del old_left[olds[0]]
                del new_left[news[0]]
    # Whatever is left: ambiguous if it shared a first-tier signature with
    # several on the other side at some tier, else unmatched. For the record
    # we re-test the first tier only; the distinction is descriptive.
    first = STITCH_TIERS[0][1]
    sig_old = defaultdict(list)
    sig_new = defaultdict(list)
    for k, rows in old_left.items():
        sig_old[chain_signature(rows, first)].append(k)
    for k, rows in new_left.items():
        sig_new[chain_signature(rows, first)].append(k)
    for sig, ks in sig_old.items():
        (out.ambiguous_old if sig in sig_new else out.unmatched_old).extend(ks)
    for sig, ks in sig_new.items():
        (out.ambiguous_new if sig in sig_old else out.unmatched_new).extend(ks)
    out.ambiguous_old.sort()
    out.ambiguous_new.sort()
    out.unmatched_old.sort()
    out.unmatched_new.sort()
    return out


# ---------------------------------------------------------------- clock


def financial_year_start(d: date) -> int:
    """The calendar year in which the GB financial year holding `d` begins
    (1 April to 31 March)."""
    return d.year if d.month >= 4 else d.year - 1


def trigger_date(connection: date) -> date:
    """CUSC Section 15 Part Two 2.2(a): the 1 April three Financial Years
    prior to the start of the Financial Year in which the Charging Date
    occurs. Branch (b), the Construction Agreement date when that is closer,
    cannot be read from the register and is not applied."""
    return date(financial_year_start(connection) - 3, 4, 1)


def months_between(earlier: date, later: date) -> int:
    """Whole calendar months from `earlier` to `later` (negative when later
    is earlier): the month difference, less one if the day has not come."""
    months = (later.year - earlier.year) * 12 + (later.month - earlier.month)
    if later.day < earlier.day:
        months -= 1
    return months


def band(at: date, trigger: date | None) -> str:
    """Which band `at` falls in relative to `trigger`. The month of the
    trigger itself counts as "0 to 12 months after"."""
    if trigger is None:
        return UNDATED
    if at < trigger:
        before = months_between(at, trigger)  # whole months still to run
        if before >= 24:
            return BANDS[0]
        if before >= 12:
            return BANDS[1]
        return BANDS[2]
    after = months_between(trigger, at)
    if after >= 12:
        return BANDS[4]
    return BANDS[3]


# ---------------------------------------------------------------- strata

_STORAGE: Final = re.compile(r"energy storage system|battery storage", re.I)


def plant_family(plant_type: object) -> str:
    """storage-only: every technology printed is storage; storage-mixed:
    storage with others; other: no storage printed; blank."""
    printed = text(plant_type)
    if not printed:
        return "blank"
    parts = [p.strip() for p in printed.split(";") if p.strip()]
    storage = [p for p in parts if _STORAGE.search(p)]
    if storage and len(storage) == len(parts):
        return "storage-only"
    if storage:
        return "storage-mixed"
    return "other"


def agreement_family(agreement: object) -> str:
    printed = normalise(agreement)
    if not printed:
        return "blank"
    if "embedded" in printed or printed in ("bega", "bella"):
        return "embedded"
    if "direct" in printed or printed == "bca":
        return "directly connected"
    if printed == "null":
        return "blank"
    return "other"


def status_family(status: object) -> str:
    printed = normalise(status)
    if not printed:
        return "blank"
    if printed == "built":
        return "Built"
    if "construction" in printed:
        return "Under Construction/Commissioning"
    if printed in ("consents approved", "consented"):
        return "Consents Approved"
    if printed == "awaiting consents":
        return "Awaiting Consents"
    if printed == "scoping":
        return "Scoping"
    return text(status)


def is_built(status: object) -> bool:
    return normalise(status) == BUILT


# ---------------------------------------------------------------- chains


@dataclass(frozen=True)
class Sighting:
    t_public: date
    sha256: str
    key: str
    rows: int
    status: str
    plant_type: str
    agreement: str
    host_to: str
    stage_mw: Decimal | None
    cumulative_mw: Decimal | None
    connection: date | None
    gate: str
    name: str
    customer: str
    site: str
    project_number: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "t_public": self.t_public.isoformat(),
            "sha256": self.sha256,
            "key": self.key,
            "rows": self.rows,
            "status": self.status,
            "plant_type": self.plant_type,
            "agreement": self.agreement,
            "host_to": self.host_to,
            "stage_mw": str(self.stage_mw) if self.stage_mw is not None else None,
            "cumulative_mw": str(self.cumulative_mw) if self.cumulative_mw is not None else None,
            "connection": self.connection.isoformat() if self.connection else None,
            "gate": self.gate,
            "name": self.name,
            "customer": self.customer,
            "site": self.site,
            "project_number": self.project_number,
        }


def sighting(
    t_public: date, sha256: str, key: str, rows: list[dict[str, object]], *, swapped: bool
) -> Sighting:
    """One chain's state in one copy, read from its rows. Where a chain has
    several rows (stages), the status, plant type, agreement, host TO, name,
    customer and site are taken from the first row that prints them; the
    stage MW is summed over rows; the cumulative MW is the largest printed;
    the connection date is the earliest printed (the first stage to connect
    is the first to be charged for)."""
    from grid_mysteries.sources.tec_register import swap_day_month

    def first(col: str) -> str:
        for r in rows:
            v = text(r.get(col))
            if v:
                return v
        return ""

    mws = [parse_decimal(r.get("MW Increase / Decrease")) for r in rows]
    cums = [parse_decimal(r.get("Cumulative Total Capacity (MW)")) for r in rows]
    dates = []
    for r in rows:
        d = parse_date(r.get("MW Effective From"))
        if d is not None and swapped:
            d = swap_day_month(d) or d
        if d is not None:
            dates.append(d)
    return Sighting(
        t_public=t_public,
        sha256=sha256,
        key=key,
        rows=len(rows),
        status=first("Project Status"),
        plant_type=first("Plant Type"),
        agreement=first("Agreement Type"),
        host_to=first("HOST TO"),
        stage_mw=sum((m for m in mws if m is not None), Decimal(0))
        if any(m is not None for m in mws)
        else None,
        cumulative_mw=max((c for c in cums if c is not None), default=None),
        connection=min(dates) if dates else None,
        gate=first("Gate"),
        name=first("Project Name"),
        customer=first("Customer Name"),
        site=first("Connection Site"),
        project_number=first("Project Number"),
    )


# --------------------------------------------------------- classification

EXIT: Final = "exit"
OPEN: Final = "open"
COMPLETED: Final = "completed"
PRESENT: Final = "present at series end"
NOT_DETERMINABLE: Final = "not determinable"
CLASSES: Final = (EXIT, OPEN, COMPLETED, PRESENT, NOT_DETERMINABLE)
#: E1: the archive's largest gap between consecutive copies (schema report).
N_DAYS: Final = 95


def classify(
    last_sighting: date,
    last_status: object,
    *,
    series_end: date,
    not_determinable: bool,
    n_days: int = N_DAYS,
) -> str:
    """E1 to E3 and I5: which class a chain falls in at the series end."""
    if not_determinable:
        return NOT_DETERMINABLE
    if last_sighting >= series_end:
        return PRESENT
    if is_built(last_status):
        return COMPLETED
    if (series_end - last_sighting).days >= n_days:
        return EXIT
    return OPEN


def exit_copy(last_sighting: date, copy_dates: list[date]) -> date:
    """E4: the first kept copy after the last sighting."""
    for d in copy_dates:
        if d > last_sighting:
            return d
    raise ValueError("no copy after the last sighting")


def month_start(d: date) -> date:
    return date(d.year, d.month, 1)


def months_in(first: date, last: date) -> list[date]:
    """K4: the first days of the calendar months from `first`'s to `last`'s
    inclusive."""
    out = []
    m = month_start(first)
    stop = month_start(last)
    while m <= stop:
        out.append(m)
        m = date(m.year + (m.month // 12), m.month % 12 + 1, 1)
    return out


def regime_of(d: date) -> str:
    return "new" if d >= REGIME_CUTOFF else "old"


# ----------------------------------------------------------------- hazard


def byar_interval(k: int, exposure: Decimal) -> tuple[Decimal, Decimal, Decimal] | None:
    """K5: hazard k ÷ exposure with Byar's 95 % interval on the count.
    Returns (hazard, lower, upper) per unit of exposure, or None when there
    is no exposure."""
    if exposure <= 0:
        return None
    z = Decimal("1.96")
    kd = Decimal(k)
    low = Decimal(0) if k == 0 else kd * (1 - 1 / (9 * kd) - z / (3 * kd.sqrt())) ** 3
    k1 = kd + 1
    high = k1 * (1 - 1 / (9 * k1) + z / (3 * k1.sqrt())) ** 3
    q = Decimal("0.000001")
    return (
        (kd / exposure).quantize(q),
        (max(low, Decimal(0)) / exposure).quantize(q),
        (high / exposure).quantize(q),
    )


def flat(intervals: list[tuple[Decimal, Decimal, Decimal] | None]) -> bool | None:
    """K6: the bands are flat within their uncertainty when every interval
    shares a common value. None when fewer than two bands have exposure."""
    present = [iv for iv in intervals if iv is not None]
    if len(present) < 2:
        return None
    return max(iv[1] for iv in present) <= min(iv[2] for iv in present)


# --------------------------------------------------------------- the joins

STOP_WORDS: Final = frozenset(
    [
        "bess",
        "battery",
        "batteries",
        "energy",
        "storage",
        "system",
        "systems",
        "facility",
        "farm",
        "solar",
        "wind",
        "power",
        "station",
        "substation",
        "grid",
        "national",
        "road",
        "lane",
        "land",
        "site",
        "project",
        "limited",
        "ltd",
        "park",
        "extension",
        "phase",
        "tertiary",
        "north",
        "south",
        "east",
        "west",
        "new",
        "connection",
        "generation",
        "renewables",
        "renewable",
        "plant",
        "works",
        "development",
        "developments",
        "holdings",
    ]
)


def place_tokens(value: object) -> frozenset[str]:
    """The normalised words of four letters or more that are not stop words."""
    return frozenset(
        w
        for w in normalise(value).split()
        if len(w) >= 4 and w not in STOP_WORDS and not w.isdigit()
    )


def within_one_mw(a: Decimal | None, b: Decimal | None) -> bool:
    return a is not None and b is not None and abs(a - b) <= 1
