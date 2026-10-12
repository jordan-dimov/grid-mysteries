"""023 — Did projects that changed hands slip more? Pure.

The exposure is 019's own R4 rule (`queue_ownership.classify_change`, as
019's amendment 2 restates it) applied to the customer name a Project ID
prints at a window's two ends; the outcome is the movement of each
capacity-bearing stage's printed date between those ends, read as 014 v4
reads dates. No I/O.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import cached_property
from typing import Any, Final

from grid_mysteries.investigations import queue_ownership as qo

#: Exposure classes at a window's ends.
TRANSFER: Final = "transfer"
RENAME: Final = "rename"
SAME_NAME: Final = "same-name"
NOT_DETERMINABLE: Final = "not-determinable"
SEVERAL_NAMES: Final = "several-names"


def boundaries(runs: list[dict[str, Any]], b: date, c: date) -> list[tuple[str, str, str]]:
    """The name changes of one Project ID between copies *b* and *c*, from
    019's run-length history: consecutive runs whose earlier run was still
    printed on or after *b* and whose later run began on or before *c*, as
    (earlier name, later name, first copy with the later name)."""
    out = []
    for prev, nxt in zip(runs, runs[1:], strict=False):
        last = date.fromisoformat(prev.get("last_t_public") or prev["t_public"])
        first = date.fromisoformat(nxt["t_public"])
        if last >= b and first <= c and prev["name"] != nxt["name"]:
            out.append((prev["name"], nxt["name"], nxt["t_public"]))
    return out


def ends_class(
    pid: str,
    names_b: set[str],
    names_c: set[str],
    b: date,
    c: date,
    links: dict[str, qo.Link],
    admitted: dict[str, dict[str, Any]],
    profiles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """The exposure of one Project ID over a window: the printed customer
    name at each end, and 019's R4 verdict on the pair. A name admitted
    with several holders (019's copy-date rule) resolves at the end that
    prints it."""
    if len(names_b) != 1 or len(names_c) != 1:
        return {"class": SEVERAL_NAMES, "earlier": sorted(names_b), "later": sorted(names_c)}
    (name_b,), (name_c,) = names_b, names_c
    if name_b == name_c:
        return {"class": SAME_NAME, "earlier": name_b, "later": name_c}
    on = dict(links)
    for name, when in ((name_b, b), (name_c, c)):
        if name in on and admitted.get(name, {}).get("holders"):
            on[name] = qo.apply_admissions(on[name], admitted, on=when)
    change = qo.NameChange(pid, name_b, name_c, b.isoformat(), c.isoformat())
    verdict = qo.classify_change(change, on, profiles)
    return {
        "class": verdict["class"],
        "earlier": name_b,
        "later": name_c,
        "earlier_company": verdict["earlier_company"],
        "later_company": verdict["later_company"],
    }


@dataclass(frozen=True)
class StageMove:
    """One capacity-bearing stage of a Project ID dated at both ends."""

    project_id: str
    stage: str
    mw: Decimal
    status_b: str
    plant_type_b: str
    date_b: date
    date_c: date

    @property
    def days(self) -> int:
        return (self.date_c - self.date_b).days

    @cached_property
    def months(self) -> Decimal:
        return (Decimal(self.days) / Decimal("30.4375")).quantize(Decimal("0.1"))

    @property
    def mw_years(self) -> Decimal:
        return (self.mw * Decimal(self.days) / Decimal("365.25")).quantize(Decimal("0.001"))

    @cached_property
    def direction(self) -> str:
        return "later" if self.days > 0 else "earlier" if self.days < 0 else "unchanged"

    @cached_property
    def stratum(self) -> str:
        """Baseline `Project Status` crossed with 020 version 1's plant family."""
        from grid_mysteries.investigations.energisation_v1 import family

        return f"{self.status_b} | {family(self.plant_type_b)}"


Reader = Callable[[dict[str, object]], date | None]


DECLARATION_PREFIX: Final = "3f22f02f"
SEED: Final = 20261012
RESAMPLES: Final = 10_000
CONTRASTS: Final = (
    ("transfer vs same name", (TRANSFER,), (SAME_NAME,)),
    ("rename vs same name", (RENAME,), (SAME_NAME,)),
    ("transfer or rename vs same name", (TRANSFER, RENAME), (SAME_NAME,)),
)


def stages(
    rows_b: list[dict[str, object]],
    rows_c: list[dict[str, object]],
    read_b: Reader,
    read_c: Reader,
    in_scope: Callable[[str], bool],
) -> tuple[list[StageMove], dict[str, int]]:
    """The declaration's stages for one window, and the rows each condition
    removed: keyed (Project ID, normalised Stage), unique at each end and
    present at both; MW > 0 and not `Built` at the baseline; a date that
    parses at both ends; the id in scope."""
    from collections import Counter

    from grid_mysteries.investigations.overdue_queue import project_id
    from grid_mysteries.sources.tec_register import normalise_stage, parse_decimal

    def keyed(
        rows: list[dict[str, object]],
    ) -> tuple[dict[tuple[str, str], dict[str, object]], int]:
        keys = Counter(
            (project_id(r), normalise_stage(r.get("Stage"))) for r in rows if project_id(r)
        )
        unique = {
            (project_id(r), normalise_stage(r.get("Stage"))): r
            for r in rows
            if project_id(r) and keys[(project_id(r), normalise_stage(r.get("Stage")))] == 1
        }
        return unique, sum(n for n in keys.values() if n > 1)

    kb, dup_b = keyed(rows_b)
    kc, dup_c = keyed(rows_c)
    dropped: Counter[str] = Counter(
        {"duplicate key at baseline": dup_b, "duplicate key at current": dup_c}
    )
    out = []
    for key, row_b in sorted(kb.items()):
        pid, stage = key
        if key not in kc:
            dropped["not at the current end"] += 1
            continue
        row_c = kc[key]
        mw = parse_decimal(row_b.get("MW Increase / Decrease"))
        status = str(row_b.get("Project Status") or "").strip()
        if mw is None or mw <= 0:
            dropped["MW not above zero at baseline"] += 1
            continue
        if status.casefold() == "built":
            dropped["Built at baseline"] += 1
            continue
        db, dc = read_b(row_b), read_c(row_c)
        if db is None or dc is None:
            dropped["undated at an end"] += 1
            continue
        if not in_scope(pid):
            dropped["id not printed on 2026-09-29"] += 1
            continue
        out.append(StageMove(pid, stage, mw, status, str(row_b.get("Plant Type") or ""), db, dc))
    return out, dict(dropped)


def group_summary(moves: list[StageMove]) -> dict[str, Any]:
    from grid_mysteries.investigations.energisation import quantiles
    from grid_mysteries.investigations.energisation_v1 import wilson

    n = len(moves)
    by_id: dict[str, Decimal] = {}
    for m in moves:
        by_id[m.project_id] = by_id.get(m.project_id, Decimal(0)) + m.mw_years
    shares = {}
    for d in ("later", "unchanged", "earlier"):
        k = sum(1 for m in moves if m.direction == d)
        interval = wilson(k, n)
        shares[d] = {
            "k": k,
            "share": (Decimal(k) / n).quantize(Decimal("0.001")) if n else None,
            "wilson95": [str(x) for x in interval] if interval else None,
        }
    return {
        "ids": len(by_id),
        "stages": n,
        "mw": str(sum((m.mw for m in moves), Decimal(0))),
        "months": quantiles([m.months for m in moves]),
        "shares": shares,
        "net_mw_years_per_id": quantiles(sorted(by_id.values())),
        "net_mw_years_total": str(sum(by_id.values(), Decimal(0)).quantize(Decimal("0.001"))),
    }


def _share_later(moves: list[StageMove]) -> Decimal | None:
    return Decimal(sum(1 for m in moves if m.direction == "later")) / len(moves) if moves else None


def _median(moves: list[StageMove]) -> Decimal | None:
    from grid_mysteries.investigations.energisation import quantiles

    value = quantiles([m.months for m in moves])["median"]
    return value if isinstance(value, Decimal) else None


def stratum(m: StageMove) -> str:
    return m.stratum


def standardised(exposed: list[StageMove], reference: list[StageMove]) -> dict[str, Any]:
    """Σ_s w_s (p_exposed,s − p_reference,s) over strata holding stages of
    both groups, w_s the exposed group's share of its stages in them."""
    by_e: dict[str, list[StageMove]] = {}
    by_r: dict[str, list[StageMove]] = {}
    for m in exposed:
        by_e.setdefault(stratum(m), []).append(m)
    for m in reference:
        by_r.setdefault(stratum(m), []).append(m)
    shared = [s for s in by_e if s in by_r]
    n_shared = sum(len(by_e[s]) for s in shared)
    if not n_shared:
        return {"difference": None, "exposed_outside_shared_strata": len(exposed)}
    total = Decimal(0)
    for s in shared:
        pe, pr = _share_later(by_e[s]), _share_later(by_r[s])
        assert pe is not None and pr is not None
        total += Decimal(len(by_e[s])) / n_shared * (pe - pr)
    return {
        "difference": total,
        "exposed_outside_shared_strata": len(exposed) - n_shared,
    }


def strata_table(exposed: list[StageMove], reference: list[StageMove]) -> list[dict[str, Any]]:
    names = sorted({stratum(m) for m in exposed} | {stratum(m) for m in reference})
    out = []
    for s in names:
        e = [m for m in exposed if stratum(m) == s]
        r = [m for m in reference if stratum(m) == s]
        out.append(
            {
                "stratum": s,
                "exposed_stages": len(e),
                "reference_stages": len(r),
                "exposed_share_later": _q(_share_later(e)),
                "reference_share_later": _q(_share_later(r)),
                "exposed_median_months": _median(e),
                "reference_median_months": _median(r),
            }
        )
    return out


def _q(x: Decimal | None) -> Decimal | None:
    return x.quantize(Decimal("0.001")) if x is not None else None


def contrast(
    exposed: list[StageMove], reference: list[StageMove], rng: Any, resamples: int = RESAMPLES
) -> dict[str, Any]:
    """Crude and standardised differences (exposed minus reference) with a
    95 % percentile bootstrap that resamples ids, all their stages, with
    replacement within each group."""

    def by_id(moves: list[StageMove]) -> list[list[StageMove]]:
        groups: dict[str, list[StageMove]] = {}
        for m in moves:
            groups.setdefault(m.project_id, []).append(m)
        return [groups[k] for k in sorted(groups)]

    def stats(e: list[StageMove], r: list[StageMove]) -> tuple[Decimal | None, ...]:
        se, sr = _share_later(e), _share_later(r)
        me, mr = _median(e), _median(r)
        return (
            se - sr if se is not None and sr is not None else None,
            me - mr if me is not None and mr is not None else None,
            standardised(e, r)["difference"],
        )

    point = stats(exposed, reference)
    ge, gr = by_id(exposed), by_id(reference)
    draws: list[list[Decimal]] = [[], [], []]
    if ge and gr:
        for _ in range(resamples):
            e = [m for g in (ge[rng.randrange(len(ge))] for _ in ge) for m in g]
            r = [m for g in (gr[rng.randrange(len(gr))] for _ in gr) for m in g]
            for i, v in enumerate(stats(e, r)):
                if v is not None:
                    draws[i].append(v)

    def interval(values: list[Decimal]) -> list[str] | None:
        if not values:
            return None
        s = sorted(values)
        lo = s[int(0.025 * (len(s) - 1))]
        hi = s[int(0.975 * (len(s) - 1))]
        return [str(_q(lo)), str(_q(hi))]

    std = standardised(exposed, reference)
    return {
        "crude_share_later_difference": str(_q(point[0])) if point[0] is not None else None,
        "crude_share_later_ci95": interval(draws[0]),
        "crude_median_months_difference": str(point[1]) if point[1] is not None else None,
        "crude_median_months_ci95": interval(draws[1]),
        "standardised_share_later_difference": str(_q(point[2])) if point[2] is not None else None,
        "standardised_share_later_ci95": interval(draws[2]),
        "exposed_stages_outside_shared_strata": std["exposed_outside_shared_strata"],
        "strata": strata_table(exposed, reference),
    }
