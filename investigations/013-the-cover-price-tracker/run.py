"""013 — the cover price tracker: weekly gated acquisition, one row per day.

    uv run python investigations/013-the-cover-price-tracker/run.py --seal <prefix> --phase all
    uv run python investigations/013-the-cover-price-tracker/run.py --phase render

Acquisition refuses to run unless invoked with ``--seal <prefix of
DECLARATION.md's SHA-256>``, so the human seal is on the record in the
command that fetched. Batches are the declaration's: seven settlement
dates from 2026-09-09, each fetchable on or after the fourth calendar day
after its last date. Every batch eligible at ``--run-date`` and not yet
pinned is fetched, in date order: register (one vintage per batch) →
NESO's three 2026-27 CSVs (one vintage per run date) → per day EBOCF
(both directions), DISPTAV (both directions, 48 periods), MID stream and
system prices. Idempotent: an already-pinned artefact is verified against
its journalled digest and skipped, never refetched or overwritten.

``compute`` and ``render`` read only pinned bytes and 012's committed
evidence; they need no seal. Seed rows (1–8 September) are copied from
012's published figures, never recomputed.
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import PERIODS, REPO_ROOT, load_records
from grid_mysteries.evidence import write_json
from grid_mysteries.investigations import cover_price as cp
from grid_mysteries.investigations import cover_price_t4 as t4
from grid_mysteries.investigations import record_day as rd
from grid_mysteries.rendering import balancing_bill
from grid_mysteries.sources import elexon, neso
from grid_mysteries.sources.pinning import load_journal, pin, progress

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
DRAFTS = HERE / "drafts"
DECLARATION = HERE / "DECLARATION.md"
DECLARATION_T4 = HERE / "DECLARATION-T4.md"
TRACKER_JSON = EVIDENCE / "tracker.json"
TRACKER_MD = HERE / "TRACKER.md"
SITE_INDEX = REPO_ROOT / "site" / "index.html"
RAW_ELEXON = REPO_ROOT / "data" / "raw" / "elexon" / "013"
RAW_NESO = REPO_ROOT / "data" / "raw" / "neso" / "013"
SEED_EVIDENCE = REPO_ROOT / "investigations" / "012-the-record-day" / "evidence"

DIRECTIONS = cp.DIRECTIONS

NESO_INPUTS = [
    (
        "NESO-DAILY-BALANCING-COSTS-26-27",
        "1d040751-f77f-4641-9130-d49f8cbfe54f",
        "daily_balancing_costs_2026-27.csv",
    ),
    (
        "NESO-DAILY-BALANCING-VOLUME-26-27",
        "e781da74-6c35-4296-81dd-250cee869c19",
        "daily_balancing_volume_2026-27.csv",
    ),
    (
        "NESO-DISAGGREGATED-BSAD-26-27",
        "2be1a4d1-6b10-4c62-a01c-924942a3748f",
        "disaggregated_bsad_2026-27.csv",
    ),
]


def declaration_digest() -> str:
    return hashlib.sha256(DECLARATION.read_bytes()).hexdigest()


def t4_frozen() -> bool:
    """T4 is computed only once DECLARATION-T4.md is witnessed: its proof
    sidecar exists and still describes the file's bytes."""
    sidecar = DECLARATION_T4.with_name(DECLARATION_T4.name + ".timestamps.json")
    if not DECLARATION_T4.exists() or not sidecar.exists():
        return False
    stamped = json.loads(sidecar.read_text())["sha256"]
    return stamped == hashlib.sha256(DECLARATION_T4.read_bytes()).hexdigest()


def journal(name: str) -> dict[str, Path]:
    return {
        "journal_path": EVIDENCE / f"{name}-journal.ndjson",
        "manifest_path": EVIDENCE / f"{name}-manifest.json",
    }


def mid_stream_url(day: str) -> str:
    """MID rows covering the settlement day under BST (23:00Z the evening
    before to 22:30Z) and GMT (00:00Z to 23:30Z): one superset window, the
    `to` bound inclusive (012, code corrections); the reader then filters
    `settlementDate == day`, which drops the neighbouring day's rows."""
    previous = (date.fromisoformat(day) - timedelta(days=1)).isoformat()
    return f"{elexon.BASE_URL}/datasets/MID/stream?from={previous}T23:00Z&to={day}T23:30Z"


def batch_dir(index: int) -> Path:
    return RAW_ELEXON / f"batch-{index:02d}"


def day_dir(day: str, vintage: str | None = None) -> Path:
    base = RAW_ELEXON / day
    return base if vintage is None else base / f"refetch-{vintage}"


# ---------------------------------------------------------------- acquisition


def acquire_batch(index: int, refetch_vintage: str | None = None) -> None:
    days = cp.batch_dates(index)
    jobs: list[tuple[str, str, Path]] = []
    if refetch_vintage is None:
        jobs.append(("BMUNITS", elexon.bmunits_url(), batch_dir(index) / "bmunits.json"))
    for day in days:
        target = day_dir(day, refetch_vintage)
        for direction in DIRECTIONS:
            jobs.append(
                ("EBOCF", elexon.cashflows_url(direction, day), target / f"ebocf_{direction}.json")
            )
        for period in PERIODS:
            for direction in DIRECTIONS:
                jobs.append(
                    (
                        "DISPTAV",
                        elexon.acceptance_volumes_url(direction, day, period),
                        target / f"disptav_{direction}_p{period:02d}.json",
                    )
                )
        jobs.append(("MID", mid_stream_url(day), target / "mid.json"))
        jobs.append(("SYSTEM-PRICES", elexon.system_prices_url(day), target / "system-prices.json"))
    name = f"batch-{index:02d}" if refetch_vintage is None else f"batch-{index:02d}-refetch"
    pin(jobs, fetch=elexon.fetch_pinned, label=name, progress=progress, **journal(name))


def acquire_neso(run_date: str) -> None:
    jobs = [
        (dataset, neso.dump_url(resource), RAW_NESO / run_date / filename)
        for dataset, resource, filename in NESO_INPUTS
    ]
    pin(
        jobs,
        fetch=neso.fetch_pinned,
        label=f"neso {run_date}",
        sleep_seconds=0.5,
        progress=progress,
        **journal("neso"),
    )


# -------------------------------------------------------------------- reading


def manifest_entries() -> dict[str, dict]:
    """path -> journal entry, over every journal this tracker has written."""
    entries: dict[str, dict] = {}
    for path in sorted(EVIDENCE.glob("*-journal.ndjson")):
        entries.update(load_journal(path))
    return entries


def artefacts_for(paths: list[Path], entries: dict[str, dict]) -> list[dict]:
    out = []
    for path in paths:
        rel = str(path.relative_to(REPO_ROOT))
        entry = entries.get(rel)
        if entry is not None:
            out.append({"dataset": entry["dataset"], "path": rel, "sha256": entry["sha256"]})
    return out


def fuel_map(index: int) -> tuple[dict[str, str], Path]:
    path = batch_dir(index) / "bmunits.json"
    return {str(r["elexonBmUnit"]): (r.get("fuelType") or "") for r in load_records(path)}, path


def neso_vintages() -> list[str]:
    return sorted(p.name for p in RAW_NESO.iterdir() if p.is_dir()) if RAW_NESO.exists() else []


def neso_rows(vintage: str, filename: str, day: str, date_col: str) -> list[dict]:
    path = RAW_NESO / vintage / filename
    if not path.exists():
        return []
    return [row for row in neso.read_csv_path(path) if row[date_col][:10] == day]


def bsad_for(day: str, vintage: str) -> dict[str, Any] | None:
    rows = neso_rows(vintage, "disaggregated_bsad_2026-27.csv", day, "Date")
    return rd.bsad_summary(rows) if rows else None


def l1_l4_for(day: str, vintage: str) -> tuple[Decimal | None, Decimal | None, Decimal | None]:
    costs = neso_rows(vintage, "daily_balancing_costs_2026-27.csv", day, "SETT_DATE")
    constraints = [Decimal(r["Constraints"]) for r in costs if (r.get("Constraints") or "").strip()]
    volumes = neso_rows(vintage, "daily_balancing_volume_2026-27.csv", day, "SETT_DATE")
    offers = (
        sum((Decimal(r["Constraint Offers (MWh)"] or "0") for r in volumes), rd.ZERO)
        if volumes
        else None
    )
    bids = (
        sum((Decimal(r["Constraint Bids (MWh)"] or "0") for r in volumes), rd.ZERO)
        if volumes
        else None
    )
    return (sum(constraints, rd.ZERO) if constraints else None), offers, bids


def day_vintage(day: str) -> Path | None:
    """The pinned folder for a day whose EBOCF carries rows: the first fetch,
    else the latest refetch. None when nothing pinned carries rows."""
    candidates = [day_dir(day)]
    base = day_dir(day)
    if base.exists():
        candidates += sorted(p for p in base.iterdir() if p.name.startswith("refetch-"))
    with_rows = [
        c
        for c in candidates
        if all((c / f"ebocf_{d}.json").exists() for d in DIRECTIONS)
        and any(load_records(c / f"ebocf_{d}.json") for d in DIRECTIONS)
    ]
    if with_rows:
        return with_rows[-1]
    return candidates[0] if (candidates[0] / "ebocf_offer.json").exists() else None


# --------------------------------------------------------------------- rows


def tracked_row(day: str, entries: dict[str, dict]) -> dict[str, Any]:
    index = cp.batch_index(day)
    folder = day_vintage(day)
    row: dict[str, Any] = {
        "settlement_date": day,
        "seed": False,
        "batch": index,
        "source": f"013 batch {index:02d}",
        "available": False,
    }
    if folder is None:
        row["status"] = "not pinned"
        return row
    fuel_of, register_path = fuel_map(index)
    rows: list[rd.Cashflow] = []
    for direction in DIRECTIONS:
        rows.extend(rd.cashflow_rows(load_records(folder / f"ebocf_{direction}.json"), direction))
    led = rd.ledger(day, rows, fuel_of)
    row["vintage"] = folder.name if folder.name.startswith("refetch-") else "first fetch"
    row["register_path"] = str(register_path.relative_to(REPO_ROOT))
    pinned = [register_path] + sorted(folder.glob("*.json"))
    row["artefacts"] = artefacts_for(pinned, entries)
    if not led.available:
        row["status"] = "EBOCF carries no rows; re-acquire as a dated refetch"
        return row
    row.update(cp.money_columns(led))
    # Volume gate: choose the DISPTAV type by reconciliation, then pair.
    cash = cp.cash_index(rows)
    pairing = cp.VolumePairing()
    disptav_present = True
    for period in PERIODS:
        for direction in DIRECTIONS:
            path = folder / f"disptav_{direction}_p{period:02d}.json"
            if not path.exists():
                disptav_present = False
                continue
            pairing.add_period(period, direction, load_records(path), cash, fuel_of)
    prices_path = folder / "system-prices.json"
    if disptav_present and prices_path.exists():
        settlement = cp.settlement_totals(load_records(prices_path))
        reconciliation = cp.reconcile(pairing.totals, settlement)
    else:
        reconciliation = {"chosen": None, "note": "DISPTAV or system prices not pinned"}
    row["reconciliation"] = reconciliation
    row["disptav_type"] = reconciliation["chosen"]
    mid_path = folder / "mid.json"
    mid = rd.mid_prices(load_records(mid_path), settlement_date=day) if mid_path.exists() else {}
    row["mid_periods"] = len(mid)
    row.update(cp.volume_columns(pairing, reconciliation["chosen"], mid))
    # L3 append-only (013 Amendment 1): every pinned NESO vintage in order,
    # first populated reading kept, later differing readings listed, the
    # reading confirmed by the next vintage decides T1. 012 Amendment 1
    # (all-zero rows are unpopulated) applies to each vintage.
    row.update(cp.bsad_by_vintage([(v, bsad_for(day, v)) for v in neso_vintages()], led.paid_out))
    return row


def seed_rows() -> list[dict[str, Any]]:
    """1–8 September as 012 published them: ledgers from selection.json,
    BSAD and price for the two deep days from results.json, digests from
    012's manifests. Nothing is recomputed and nothing new is read."""
    selection = json.loads((SEED_EVIDENCE / "selection.json").read_text())
    results = json.loads((SEED_EVIDENCE / "results.json").read_text())
    manifests: list[dict] = []
    for name in ("register", "neso", "window", "deep"):
        manifests.extend(json.loads((SEED_EVIDENCE / f"{name}-manifest.json").read_text()))
    shared = [
        {"dataset": e["dataset"], "path": e["path"], "sha256": e["sha256"]}
        for e in manifests
        if e["dataset"] in {"BMUNITS", "NESO-DISAGGREGATED-BSAD-26-27"}
    ]
    out = []
    for day in cp.SEED_DATES:
        led_json = selection["ledgers"][day]
        paid_out = Decimal(led_json["paid_out_gbp"])
        wind_bid = Decimal(led_json["paid_out_by_class_gbp"]["wind"]["bid"])
        gas_offer = Decimal(led_json["paid_out_by_class_gbp"]["gas"]["offer"])
        other = paid_out - wind_bid - gas_offer
        signed = Decimal(led_json["by_class_gbp"]["wind"]["bid"])
        pos, neg = led_json["wind_bid_rows"]["positive"], led_json["wind_bid_rows"]["negative"]
        row: dict[str, Any] = {
            "settlement_date": day,
            "seed": True,
            "source": "012 the record day (published figures, not recomputed)",
            "available": led_json["available"],
            "periods_with_rows": led_json["periods_with_rows"],
            "units": led_json["units"],
            "paid_out_gbp": str(paid_out),
            "net_gbp": led_json["total_gbp"],
            "paid_in_gbp": led_json["paid_in_gbp"],
            "wind_bid_gbp": str(wind_bid),
            "wind_bid_share": rd.shown(rd.share(wind_bid, paid_out)),
            "gas_offer_gbp": str(gas_offer),
            "gas_offer_share": rd.shown(rd.share(gas_offer, paid_out)),
            "other_gbp": str(other),
            "other_share": rd.shown(rd.share(other, paid_out)),
            "two_cut_gbp": str(wind_bid + gas_offer),
            "sign_convention_holds": pos > neg and signed > rd.ZERO,
            "wind_bid_rows": {"positive": pos, "negative": neg},
            "wind_bid_signed_gbp": str(signed),
            "disptav_type": None,
            "reconciliation": None,
            "gas_offer_vwap_gbp_per_mwh": None,
            "premium_gbp_per_mwh": None,
            "bsad_available": False,
            "bsad_net_gbp": None,
            "bsad_share": None,
            "artefacts": shared
            + [
                {"dataset": e["dataset"], "path": e["path"], "sha256": e["sha256"]}
                for e in manifests
                if f"/{day}/" in e["path"]
            ],
        }
        deep = results["days"].get(day)
        if deep is not None:
            price = deep["L2"]["gas_offer_price"]
            row.update(
                {
                    "disptav_type": "Original",
                    "disptav_basis": (
                        "012 declared rule; offer-side Original and Tagged nearly coincide "
                        "(115.0 vs 116.6 GWh on 8 September), bid-side Original does not "
                        "reconcile; see 012 AMENDMENTS.md post-acquisition note"
                    ),
                    "gas_offer_mwh": price["gas_offer_mwh"],
                    "gas_offer_vwap_gbp_per_mwh": price["gas_offer_vwap_gbp_per_mwh"],
                    "mid_vwap_same_periods_gbp_per_mwh": price["mid_vwap_same_periods_gbp_per_mwh"],
                    "premium_gbp_per_mwh": price["premium_gbp_per_mwh"],
                }
            )
            row.update(cp.bsad_columns(deep["L3"], paid_out))
            row["bsad_vintage"] = "2026-09-11 (012)"
        out.append(row)
    return out


def load_tracker() -> dict[str, Any]:
    if TRACKER_JSON.exists():
        return json.loads(TRACKER_JSON.read_text())
    return {"rows": []}


def append_outcomes(rows: list[dict[str, Any]], previous: dict[str, dict[str, Any]]) -> None:
    """L1/L4 are append-only: the first vintage that carries the day is kept;
    a later vintage that differs is listed under `outcome_revisions`."""
    vintages = neso_vintages()
    for row in rows:
        day = row["settlement_date"]
        old = previous.get(day, {})
        row["outcome"] = old.get("outcome")
        row["outcome_revisions"] = old.get("outcome_revisions", [])
        if not row.get("available"):
            continue
        two_cut, paid_out = Decimal(row["two_cut_gbp"]), Decimal(row["paid_out_gbp"])
        for vintage in vintages:
            l1, l4o, l4b = l1_l4_for(day, vintage)
            candidate = cp.outcome_columns(l1, l4o, l4b, vintage, two_cut, paid_out)
            if candidate is None:
                continue
            if row["outcome"] is None:
                row["outcome"] = candidate
            elif {k: v for k, v in candidate.items() if k != "vintage"} != {
                k: v for k, v in row["outcome"].items() if k != "vintage"
            } and vintage not in {r["vintage"] for r in row["outcome_revisions"]} | {
                row["outcome"]["vintage"]
            }:
                row["outcome_revisions"].append(candidate)


def compute(run_date: str) -> dict[str, Any]:
    entries = manifest_entries()
    vintages = neso_vintages()
    previous = {r["settlement_date"]: r for r in load_tracker().get("rows", [])}
    rows = seed_rows()
    pinned_days = (
        sorted(p.name for p in RAW_ELEXON.iterdir() if p.is_dir() and p.name[:4].isdigit())
        if RAW_ELEXON.exists()
        else []
    )
    for day in pinned_days:
        rows.append(tracked_row(day, entries))
    append_outcomes(rows, previous)
    ordered = cp.flag_records(rows)
    tracker = {
        "investigation": "013 the cover price tracker",
        "declaration_sha256": declaration_digest(),
        "computed_at": datetime.now(UTC).isoformat(),
        "run_date": run_date,
        "neso_vintages": vintages,
        "rows": ordered,
        "propositions": cp.evaluate(ordered, date.fromisoformat(run_date)),
    }
    if t4_frozen():
        tracker["propositions"]["T4"] = t4.evaluate(
            ordered,
            date.fromisoformat(run_date),
            hashlib.sha256(DECLARATION_T4.read_bytes()).hexdigest(),
        )
    write_json(TRACKER_JSON, tracker)
    return tracker


# ------------------------------------------------------------------ rendering


METHOD = """\
# The Balancing Bill — tracker (investigation 013, the cover price tracker)

*Public name: **The Balancing Bill**, who got paid to keep Britain's grid
balanced, day by day. The investigation's id, folder, declaration, module and
evidence paths keep their names; only the render, the page and the drafts use
the public name. The page at `site/index.html` is a pure function of
`evidence/tracker.json`.*

**One number, on a schedule.** For every GB settlement date from
2026-09-09, the gross money paid out to units in the Balancing Mechanism
(Elexon's published indicative cashflows, EBOCF, both directions, positive
values only, labelled *paid out*), with the same day split four ways and
laid beside what sits outside the mechanism. The method is 012's, frozen in
`DECLARATION.md` (SHA-256 `{digest}`), and every rule below was fixed before
any tracker day was fetched. Batches are weekly and fetched at least three
full days after their last date. Every day gets a row; nothing is selected
by hand. A day is flagged **record** when its paid-out exceeds every earlier
row's, seed rows included.

**Columns.** *Paid out* and *net* are the mechanism's gross and net published
cashflow. *Wind bids* is money paid on bids by units the register types
`WIND` (paid to reduce); *gas offers* is money paid on offers by `CCGT` and
`OCGT` units (paid to increase); *other* is the residual of paid-out. *Gas
offer £/MWh* pairs those pounds with accepted MWh from the DISPTAV data type
that reconciles with the day's system-prices acceptance totals within 0.1 %
in both directions (the *DISPTAV type* column names it); if none reconciles
the price is not computed. *Premium* is that price less the APX market
index (`APXMIDP`) weighted by the same MWh in the same periods. *BSAD net*
is NESO's Disaggregated BSAD for the day, outside the mechanism; an all-zero
day is *unpopulated*, not zero. *Sign* records that wind-unit bid cashflows
were predominantly positive by rows and by pounds. *NESO Constraints* is
NESO's own attribution (Daily Balancing Costs 2026-27), blank until its file
reaches the day, then appended with the vintage date and never revised in
place; *L1 ÷ two cuts* divides it by wind bids plus gas offers.

**Seed rows** (1–8 September, marked *seed (012)*) are 012's published
figures, copied, not recomputed; they set the bar for the first record and
are never flagged. Their price columns (†) are 012's declared `Original`
rule, which reconciles on offers but not on bids. Cashflows are indicative
and pre-settlement; nothing here is a saving, a loss, a boundary attribution
or a characterisation of any party. Every artefact digest is in
`evidence/tracker.json`.

Last computed {computed_at} (run date {run_date}). NESO vintages on disk:
{vintages}.

## Propositions

{propositions}
{note}
## The table

Money in £m; shares of paid-out. Blank means not computable from what is
pinned, never zero.

"""


def render_propositions(verdicts: dict[str, Any]) -> str:
    def word(value: bool | None) -> str:
        return "undecided" if value is None else ("holds" if value else "**fails**")

    lines = []
    for key in ("T1", "T2", "T3"):
        block = verdicts[key]
        instances = block["instances"]
        lines.append(
            f"- **{key}** — {block['claim']}: {word(block['holds'])} "
            f"({len(instances)} instance{'s' if len(instances) != 1 else ''}"
            + (f", {block['deciding_instances']} deciding" if "deciding_instances" in block else "")
            + f"). Falsifier date {verdicts['falsifier_date']}."
        )
    if "T4" in verdicts:
        lines.append(render_t4(verdicts["T4"]))
    records = verdicts["record_days"]
    lines.append(
        f"- Record days so far: {', '.join(records) if records else 'none'}. "
        f"As of {verdicts['as_of']}."
    )
    return "\n".join(lines)


def render_t4(block: dict[str, Any]) -> str:
    word, detail = t4.describe(block)
    word = "**fails**" if word == "fails" else word
    return (
        f"- **T4** — {block['claim']}: {word} ({detail}). Declaration SHA-256 "
        f"`{block['declaration_sha256'][:8]}…`."
    )


def latest_record_anchor() -> dict[str, Any] | None:
    """The Balancing Bill record's latest checkpoint (bill/anchors/), for the
    page to cite; None before the record's first checkpoint."""
    anchors = sorted(
        (REPO_ROOT / "bill" / "anchors").glob("tree-*.json"),
        key=lambda p: int(p.stem.split("-")[1]),
    )
    if not anchors:
        return None
    anchor = json.loads(anchors[-1].read_text())
    return {
        "tree_size": anchor["tree_size"],
        "root_hash": anchor["root_hash"],
        "anchor_path": str(anchors[-1].relative_to(REPO_ROOT)),
    }


def render(tracker: dict[str, Any]) -> None:
    text = METHOD.format(
        digest=tracker["declaration_sha256"],
        computed_at=tracker["computed_at"][:19] + "Z",
        run_date=tracker["run_date"],
        vintages=", ".join(tracker["neso_vintages"]) or "none",
        propositions=render_propositions(tracker["propositions"]),
        note="".join(f"\n{p}\n" for p in balancing_bill.t2_failure_note(tracker["propositions"])),
    )
    TRACKER_MD.write_text(text + cp.render_table(tracker["rows"]) + "\n")
    SITE_INDEX.parent.mkdir(parents=True, exist_ok=True)
    SITE_INDEX.write_text(balancing_bill.render_page(tracker, record=latest_record_anchor()))
    for row in tracker["rows"]:
        if row.get("record"):
            write_draft(row)


DRAFT = """\
# The Balancing Bill: {day} sets a new record

*Grid Mysteries 013 (public name: The Balancing Bill), draft held for the
sponsor. Not released. Figures are published indicative cashflows,
pre-settlement; every digest is in `evidence/tracker.json`.*

On {day}, gross money paid out to units in Britain's Balancing Mechanism
was **£{paid_out}m**, above every earlier day The Balancing Bill holds (the
previous bar was £{prior}m). Net of money paid in, the mechanism's figure
was £{net}m.

Where it went:

- **£{wind}m ({wind_share})** to wind units, on bids, for reducing output.
- **£{gas}m ({gas_share})** to gas units, on offers, for increasing output.
- **£{other}m ({other_share})** to everything else.

{price_paragraph}

{bsad_paragraph}

{neso_paragraph}

Nothing here attributes money to a transmission boundary, and nothing is a
saving or a loss. The rule that flagged this day was frozen before it was
fetched; the sponsor decides whether this goes out.
"""


def write_draft(row: dict[str, Any]) -> None:
    DRAFTS.mkdir(parents=True, exist_ok=True)
    path = DRAFTS / f"draft-post-{row['settlement_date']}.md"
    if path.exists():
        return

    def m(v: str | None) -> str:
        return cp._m(v)

    if row.get("gas_offer_vwap_gbp_per_mwh") is not None:
        price_paragraph = (
            f"The gas offers were accepted at a volume-weighted "
            f"**£{row['gas_offer_vwap_gbp_per_mwh']}/MWh** on "
            f"{Decimal(row['gas_offer_mwh']):,.0f} MWh (DISPTAV `{row['disptav_type']}`, "
            f"the type that reconciles with the day's settlement totals), a premium of "
            f"£{row['premium_gbp_per_mwh']}/MWh over the APX index in the same periods."
        )
    else:
        price_paragraph = (
            "No DISPTAV data type reconciled with the day's settlement acceptance "
            "totals, so no accepted-volume price is computed for this day."
        )
    if row.get("bsad_net_gbp") is not None:
        bsad_paragraph = (
            f"Outside the mechanism, NESO's Disaggregated BSAD nets to "
            f"**£{m(row['bsad_net_gbp'])}m**, {cp._pct(row['bsad_share'])} again on top of "
            f"the in-mechanism money."
        )
    else:
        bsad_paragraph = (
            "NESO's Disaggregated BSAD for the day was not yet populated when this "
            "was computed; the outside-the-mechanism figure is appended when it lands."
        )
    outcome = row.get("outcome") or {}
    if outcome.get("l1_constraints_gbp") is not None:
        neso_paragraph = (
            f"NESO's own Constraints figure for the day, published later (vintage "
            f"{outcome['vintage']}), is £{m(outcome['l1_constraints_gbp'])}m, "
            f"{cp._pct(outcome['ratio_l1_to_two_cut'])} of wind bids plus gas offers."
        )
    else:
        neso_paragraph = (
            "NESO's own Constraints attribution for the day is not yet published; it "
            "is appended to the tracker, with its vintage, when it is."
        )
    path.write_text(
        DRAFT.format(
            day=row["settlement_date"],
            paid_out=m(row["paid_out_gbp"]),
            prior=m(row.get("prior_max_paid_out_gbp")),
            net=m(row["net_gbp"]),
            wind=m(row["wind_bid_gbp"]),
            wind_share=cp._pct(row["wind_bid_share"]),
            gas=m(row["gas_offer_gbp"]),
            gas_share=cp._pct(row["gas_offer_share"]),
            other=m(row["other_gbp"]),
            other_share=cp._pct(row["other_share"]),
            price_paragraph=price_paragraph,
            bsad_paragraph=bsad_paragraph,
            neso_paragraph=neso_paragraph,
        )
    )
    print(f"draft held for the sponsor: {path.relative_to(REPO_ROOT)}")


# ----------------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seal", help="prefix (≥ 8 hex) of DECLARATION.md's SHA-256")
    parser.add_argument("--run-date", default=datetime.now(UTC).date().isoformat())
    parser.add_argument("--phase", choices=("acquire", "compute", "render", "all"), default="all")
    parser.add_argument(
        "--batch", type=int, action="append", help="fetch only this batch (repeatable)"
    )
    parser.add_argument(
        "--refetch",
        type=int,
        help="re-acquire this batch's days as a dated refetch vintage (for days pinned empty)",
    )
    parser.add_argument("--note", action="append", default=[])
    args = parser.parse_args()

    run_date = date.fromisoformat(args.run_date)
    digest = declaration_digest()
    fetching = args.phase in ("acquire", "all")
    if fetching:
        if not args.seal or len(args.seal) < 8 or not digest.startswith(args.seal.lower()):
            print(
                f"seal {args.seal!r} does not match DECLARATION.md sha256 {digest}; "
                "refusing to fetch",
                file=sys.stderr,
            )
            return 2
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        log_path = EVIDENCE / "acquisition-log.json"
        log: dict[str, Any] = json.loads(log_path.read_text()) if log_path.exists() else {}
        log.update({"declaration_sha256": digest, "seal": args.seal})
        if args.note:
            log.setdefault("notes", []).extend(args.note)
        eligible = cp.eligible_batches(run_date)
        wanted = args.batch or eligible
        too_early = [b for b in wanted if b not in eligible]
        if too_early:
            print(
                f"batch(es) {too_early} not fetchable on {run_date}: earliest "
                f"{[cp.earliest_fetch_date(b).isoformat() for b in too_early]}",
                file=sys.stderr,
            )
            return 3
        log.setdefault("runs", []).append(
            {
                "run_date": args.run_date,
                "at": datetime.now(UTC).isoformat(),
                "batches": wanted,
                "refetch": args.refetch,
            }
        )
        write_json(log_path, log)
        if args.refetch is not None:
            acquire_batch(args.refetch, refetch_vintage=args.run_date)
        else:
            for index in wanted:
                acquire_batch(index)
        acquire_neso(args.run_date)
    tracker = None
    if args.phase in ("compute", "all"):
        tracker = compute(args.run_date)
    elif args.phase == "render":
        # The page and TRACKER.md are pure functions of the committed
        # tracker.json, which the Balancing Bill record names by digest: a
        # render never recomputes it (a recompute would re-stamp computed_at
        # and change the digest the record holds).
        if not TRACKER_JSON.exists():
            print("nothing to render: run --phase compute first", file=sys.stderr)
            return 1
        tracker = load_tracker()
    if args.phase in ("render", "all") and tracker is not None:
        render(tracker)
        records = tracker["propositions"]["record_days"]
        print(f"rows {len(tracker['rows'])}, record days {records or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
