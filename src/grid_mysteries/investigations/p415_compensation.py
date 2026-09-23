"""018 — P415 supplier compensation after P511: pure reading and tests.

Reads Elexon S0142 settlement reports (SAA-I014 sub-flow 2) line by line and
reduces one file to the P415 quantities per BSC Party, as the file prints
them. Nothing here fetches, and nothing here names a party: the key is the
BSC Party Id on the ``BPH`` record above each ``BP7``, never a name.

Positions are 0-based with index 0 the record id, as in
``archives/elexon-s0142/SCHEMA.md``; the trailing pipe every record ends with
is not a field. The bindings of positions to IDD field names are the
declaration's (``investigations/018-.../DECLARATION.md``, rule R2), and the
constants below are the only place they are written in code.
"""

import re
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal

# R2: BP7 positions (IDD Part 1, S0142 BP7, P415 fields).
BP7_UNIT = 1
BP7_SUPPLIER_COMPENSATION_VOLUME = 22
BP7_SECONDARY_COMPENSATION_VOLUME = 23
BP7_SUPPLIER_COMPENSATION_CASHFLOW = 25
BPH_PARTY = 8
SP7_PERIOD = 1
SRH_DATE, SRH_RUN = 1, 2
AAA_FLOW = 1
# APC (Aggregate Party Day Charges): N0653 Daily Virtual Lead Party
# Compensation Cashflow (a debit when positive, BSC Section T 1.2.3) and N0654
# Daily Supplier Compensation Cashflow (a credit when positive).
APC_CHARGED = 11
APC_PAID = 12
# SPI: N0659 Supplier Sourcing Cost, the last field of the record.
SPI_PERIOD = 1
SPI_SUPPLIER_SOURCING_COST = 53
FLOW_VERSION = "S0142013"
BP7_DATA_FIELDS = 25

# R3: where each quantity may appear. A non-blank value anywhere else is an
# off-prefix cell: counted, reported, and a failed check (C2).
VTP_PREFIX = "V__"
SUPPLIER_PREFIX = "2__"

# R4: settlement runs in order. Any other run code is reported and never
# selected (C5).
RUN_ORDER = ("II", "SF", "R1", "R2", "R3", "RF", "DF")

NAME = re.compile(r"S0142_(\d{8})_([A-Z0-9]{2})_(\d{14})\.gz")


@dataclass(frozen=True)
class S0142File:
    filename: str
    settlement_date: date
    run: str
    published: datetime  # the stamp in the filename, as printed (no zone stated)


def parse_name(filename: str) -> S0142File:
    m = NAME.fullmatch(filename)
    if not m:
        raise ValueError(f"not an S0142 file name: {filename!r}")
    return S0142File(
        filename=filename,
        settlement_date=datetime.strptime(m.group(1), "%Y%m%d").date(),
        run=m.group(2),
        published=datetime.strptime(m.group(3), "%Y%m%d%H%M%S"),
    )


def run_rank(run: str) -> int | None:
    return RUN_ORDER.index(run) if run in RUN_ORDER else None


def latest_run(files: Iterable[S0142File], *, minimum: str = "SF") -> S0142File | None:
    """R4: the latest known run at or after ``minimum``; unknown runs never win.

    Two files for the same run (a republication) resolve to the later
    publication stamp."""
    floor = RUN_ORDER.index(minimum)
    ranked = [(run_rank(f.run), f.published, f) for f in files]
    eligible = [(r, p, f) for r, p, f in ranked if r is not None and r >= floor]
    return max(eligible, key=lambda t: (t[0], t[1]))[2] if eligible else None


@dataclass
class DaySummary:
    settlement_date: date
    run: str
    periods: set[int] = field(default_factory=set)
    bp7_lines: int = 0
    vtp_volume: dict[str, Decimal] = field(default_factory=lambda: defaultdict(Decimal))
    supplier_cash: dict[str, Decimal] = field(default_factory=lambda: defaultdict(Decimal))
    supplier_volume: dict[str, Decimal] = field(default_factory=lambda: defaultdict(Decimal))
    charged: dict[str, Decimal] = field(default_factory=lambda: defaultdict(Decimal))
    apc_paid: dict[str, Decimal] = field(default_factory=lambda: defaultdict(Decimal))
    off_prefix: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    orphan_bp7: int = 0
    flow_version: str | None = None
    spi_periods: set[int] = field(default_factory=set)
    bp7_widths: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    # sum over BP7 rows of volume x the period's Supplier Sourcing Cost (C6)
    paid_at_ssc: Decimal = Decimal(0)
    vtp_at_ssc: Decimal = Decimal(0)

    @property
    def vtp_volume_total(self) -> Decimal:
        return sum(self.vtp_volume.values(), Decimal(0))

    @property
    def supplier_cash_total(self) -> Decimal:
        return sum(self.supplier_cash.values(), Decimal(0))

    @property
    def supplier_volume_total(self) -> Decimal:
        return sum(self.supplier_volume.values(), Decimal(0))

    @property
    def charged_total(self) -> Decimal:
        return sum(self.charged.values(), Decimal(0))

    @property
    def apc_paid_total(self) -> Decimal:
        return sum(self.apc_paid.values(), Decimal(0))


def _fields(line: str) -> list[str]:
    p = line.rstrip("\r\n").split("|")
    return p[:-1] if p and p[-1] == "" else p


def _cell(p: Sequence[str], i: int) -> Decimal | None:
    return Decimal(p[i]) if i < len(p) and p[i] != "" else None


def summarise(lines: Iterable[str]) -> DaySummary:
    """One S0142 file to its P415 quantities per BSC Party (R1-R3)."""
    summary: DaySummary | None = None
    party: str | None = None
    period: int | None = None
    flow: str | None = None
    ssc: dict[int, Decimal] = {}
    for line in lines:
        p = _fields(line)
        r = p[0]
        if r == "AAA":
            flow = p[AAA_FLOW]
        elif r == "SRH":
            summary = DaySummary(
                settlement_date=datetime.strptime(p[SRH_DATE], "%Y%m%d").date(),
                run=p[SRH_RUN],
                flow_version=flow,
            )
        elif r == "SPI":
            party, period = None, None
            if summary is not None:
                summary.spi_periods.add(int(p[SPI_PERIOD]))
            cost = _cell(p, SPI_SUPPLIER_SOURCING_COST)
            if cost is not None:
                ssc[int(p[SPI_PERIOD])] = cost
        elif r == "BPH":
            party, period = p[BPH_PARTY], None
        elif r == "APC" and summary is not None and party is not None:
            for pos, into in ((APC_CHARGED, summary.charged), (APC_PAID, summary.apc_paid)):
                value = _cell(p, pos)
                if value is not None:
                    into[party] += value
        elif r == "SP7":
            period = int(p[SP7_PERIOD])
        elif r == "BP7":
            if summary is None:
                raise ValueError("BP7 before SRH")
            summary.bp7_lines += 1
            summary.bp7_widths[len(p) - 1] += 1
            if party is None or period is None:
                summary.orphan_bp7 += 1
                continue
            summary.periods.add(period)
            unit = p[BP7_UNIT]
            vtp = _cell(p, BP7_SECONDARY_COMPENSATION_VOLUME)
            s_vol = _cell(p, BP7_SUPPLIER_COMPENSATION_VOLUME)
            s_cash = _cell(p, BP7_SUPPLIER_COMPENSATION_CASHFLOW)
            if vtp is not None:
                if unit.startswith(VTP_PREFIX):
                    summary.vtp_volume[party] += vtp
                    summary.vtp_at_ssc += vtp * ssc.get(period, Decimal("NaN"))
                else:
                    summary.off_prefix[f"{BP7_SECONDARY_COMPENSATION_VOLUME}:{unit[:3]}"] += 1
            for pos, value, into in (
                (BP7_SUPPLIER_COMPENSATION_VOLUME, s_vol, summary.supplier_volume),
                (BP7_SUPPLIER_COMPENSATION_CASHFLOW, s_cash, summary.supplier_cash),
            ):
                if value is None:
                    continue
                if unit.startswith(SUPPLIER_PREFIX):
                    into[party] += value
                    if pos == BP7_SUPPLIER_COMPENSATION_VOLUME:
                        summary.paid_at_ssc += value * ssc.get(period, Decimal("NaN"))
                else:
                    summary.off_prefix[f"{pos}:{unit[:3]}"] += 1
    if summary is None:
        raise ValueError("no SRH record")
    return summary


def checks(s: DaySummary, *, expect: S0142File, pennies: Decimal = Decimal("1.00")) -> dict:
    """C1-C3 and C6-C7 on one file; each is True, or False with the reason in the value.

    C6 compares the paid cash with volume x Supplier Sourcing Cost summed
    row by row, and C7 the BP7 cash with the APC day total, each within
    ``pennies`` per party-day of rounding (the file prints cash to 2 dp and
    volumes to 3 dp)."""
    parties = max(len(s.supplier_cash), 1)
    tol = pennies * parties
    per_party = all(
        abs(s.supplier_cash.get(k, Decimal(0)) - s.apc_paid.get(k, Decimal(0))) <= pennies
        for k in set(s.supplier_cash) | set(s.apc_paid)
    )
    return {
        "C1 header matches name and layout": (
            s.settlement_date == expect.settlement_date
            and s.run == expect.run
            and s.flow_version == FLOW_VERSION
            and set(s.bp7_widths) == {BP7_DATA_FIELDS}
        ),
        "C2 no off-prefix or orphan P415 cell": not s.off_prefix and s.orphan_bp7 == 0,
        "C3 48 settlement periods": len(s.spi_periods) == 48 and s.periods <= s.spi_periods,
        "C6 paid cash is volume x Supplier Sourcing Cost": (
            not s.paid_at_ssc.is_nan() and abs(s.supplier_cash_total - s.paid_at_ssc) <= tol
        ),
        "C7 BP7 cash equals the APC day total, party by party": per_party
        and abs(s.supplier_cash_total - s.apc_paid_total) <= tol,
    }


def shares(values: Mapping[str, Decimal]) -> list[tuple[str, Decimal, Decimal | None]]:
    """(party, value, share of the total) largest first; share is None on a zero total."""
    total = sum(values.values(), Decimal(0))
    rows = sorted(values.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(k, v, (v / total) if total else None) for k, v in rows]


def pooled(days: Iterable[DaySummary], attr: str) -> dict[str, Decimal]:
    out: dict[str, Decimal] = defaultdict(Decimal)
    for d in days:
        for k, v in getattr(d, attr).items():
            out[k] += v
    return dict(out)


def mean_daily(days: Sequence[DaySummary], attr: str) -> Decimal:
    if not days:
        raise ValueError("empty window")
    return sum((getattr(d, attr) for d in days), Decimal(0)) / len(days)


def h1_ratio(
    post: Sequence[DaySummary], baseline: Sequence[DaySummary], *, kill_below: Decimal
) -> dict:
    """H1: mean daily supplier compensation cash, post over baseline.

    Killed if the ratio is below ``kill_below``; holds otherwise. A baseline
    whose mean is not positive decides nothing."""
    post_mean = mean_daily(post, "supplier_cash_total")
    base_mean = mean_daily(baseline, "supplier_cash_total")
    if base_mean <= 0:
        return {
            "post_mean": post_mean,
            "baseline_mean": base_mean,
            "ratio": None,
            "verdict": "not decided",
        }
    ratio = post_mean / base_mean
    return {
        "post_mean": post_mean,
        "baseline_mean": base_mean,
        "ratio": ratio,
        "verdict": "killed" if ratio < kill_below else "holds",
    }


def h2_handover(
    baseline: Sequence[DaySummary],
    post: Sequence[DaySummary],
    attr: str,
    *,
    baseline_above: Decimal,
    post_below: Decimal,
) -> dict:
    """H2, one side: the baseline's largest party carries more than
    ``baseline_above`` of the pooled baseline quantity, and less than
    ``post_below`` of the pooled post quantity. The party is chosen on the
    baseline alone; its post share is then read, never re-chosen."""
    base = shares(pooled(baseline, attr))
    if not base or base[0][2] is None:
        return {"party": None, "baseline_share": None, "post_share": None, "verdict": "not decided"}
    party, _, base_share = base[0]
    post_pool = pooled(post, attr)
    post_total = sum(post_pool.values(), Decimal(0))
    if not post_total:
        return {
            "party": party,
            "baseline_share": base_share,
            "post_share": None,
            "verdict": "not decided",
        }
    post_share = post_pool.get(party, Decimal(0)) / post_total
    assert base_share is not None
    holds = base_share > baseline_above and post_share < post_below
    return {
        "party": party,
        "baseline_share": base_share,
        "post_share": post_share,
        "verdict": "holds" if holds else "fails",
    }


def restatement(runs: Sequence[DaySummary], attr: str) -> list[dict]:
    """H3: each run's value and its movement from the latest run, as a
    fraction of the latest run's absolute value (None when that is zero)."""
    ordered = sorted(runs, key=lambda d: RUN_ORDER.index(d.run))
    latest = getattr(ordered[-1], attr)
    return [
        {
            "run": d.run,
            "value": getattr(d, attr),
            "movement": (abs(getattr(d, attr) - latest) / abs(latest)) if latest else None,
        }
        for d in ordered
    ]


def _days(start: date, end: date, *, step: int = 1, exclude: tuple[date, ...] = ()) -> list[date]:
    out, d = [], start
    while d <= end:
        if d not in exclude:
            out.append(d)
        d += timedelta(days=step)
    return out


# The declaration's windows, fixed before acquisition. The two schema-pass
# days (2026-02-17, 2026-08-28) are in no test window; 2026-02-17 is in C4.
SCHEMA_PASS_DAYS = (date(2026, 2, 17), date(2026, 8, 28))
WINDOWS: dict[str, list[date]] = {
    "FEB": _days(date(2026, 2, 1), date(2026, 2, 28), exclude=SCHEMA_PASS_DAYS),
    "PRE": _days(date(2026, 8, 10), date(2026, 8, 23)),
    "POST": _days(date(2026, 8, 24), date(2026, 9, 6), exclude=SCHEMA_PASS_DAYS),
    "SERIES": _days(date(2025, 9, 3), date(2026, 8, 19), step=7),
    "C4": _days(date(2026, 2, 1), date(2026, 2, 28)),
}
RESTATE = (date(2025, 9, 3), date(2025, 11, 5), date(2026, 1, 7), date(2026, 3, 4))
INDEX_FROM = date(2025, 9, 3)


def build_index(names: Iterable[str]) -> dict[date, list[S0142File]]:
    """Listed file names to {settlement date: files}; foreign names are dropped."""
    index: dict[date, list[S0142File]] = defaultdict(list)
    for n in names:
        try:
            f = parse_name(n)
        except ValueError:
            continue
        index[f.settlement_date].append(f)
    return dict(index)


def select(index: Mapping[date, Sequence[S0142File]]) -> dict:
    """R4 and C5: the file each window day is read on, the RESTATE runs, and
    the window days with no run at or after SF (missing)."""
    chosen: dict[str, dict[date, S0142File]] = {}
    missing: dict[str, list[date]] = {}
    for name, days in WINDOWS.items():
        chosen[name], missing[name] = {}, []
        for d in days:
            f = latest_run(index.get(d, ()))
            if f is None:
                missing[name].append(d)
            else:
                chosen[name][d] = f
    restate = {
        d: sorted(
            (f for f in index.get(d, ()) if run_rank(f.run) is not None),
            key=lambda f: (RUN_ORDER.index(f.run), f.published),
        )
        for d in RESTATE
    }
    unknown = sorted({f.run for files in index.values() for f in files if run_rank(f.run) is None})
    return {"chosen": chosen, "missing": missing, "restate": restate, "unknown_runs": unknown}


def restate_verdict(movements: Sequence[Decimal | None], *, above: Decimal, days: int) -> str:
    """H3: holds if at least ``days`` of the SF-to-latest movements exceed ``above``."""
    if any(m is None for m in movements) or len(movements) < days:
        return "not decided"
    return "holds" if sum(1 for m in movements if m is not None and m > above) >= days else "fails"
