"""017 addendum — the storage rows of the committed census, with a proposed
per-MW queue fee laid beside them as an illustration.

    uv run python investigations/017-the-overdue-queue/addendum.py

Reads **only** the committed evidence of the two runs (`evidence/rows.ndjson`,
`evidence/gate-rows.ndjson`, and the two summaries for their digests and
totals). Never opens the register copy, fetches nothing, and needs no seal
because it computes no census: it re-reads rows that are already published
in `FINDINGS.md`. Writes `evidence/addendum-storage.json` and
`ADDENDUM-storage-fee.md`. It refuses if the committed rows do not sum to
the census's own headline, so it cannot run over an edited evidence file.

This is outside version 1's R7 and version 2's six breakdowns, by
construction: nothing here is added to `FINDINGS.md`, `post-facts.json` or
any governed slot. An outbound use of any figure below needs a declaration
of its own, frozen first.
"""

import dataclasses
import hashlib
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.evidence import write_json
from grid_mysteries.investigations import overdue_queue_addendum as add

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
ROWS = EVIDENCE / "rows.ndjson"
GATE_ROWS = EVIDENCE / "gate-rows.ndjson"
CENSUS = EVIDENCE / "census.json"
GATE = EVIDENCE / "gate.json"
OUT_JSON = EVIDENCE / "addendum-storage.json"
OUT_MD = HERE / "ADDENDUM-storage-fee.md"

#: The two rates the second-hand report attributes to Ofgem's proposal of
#: 2026-09-17 (etrmbiz slot `gb-battery-queue-fee-2026`). They are inputs to
#: an illustration, not facts established here.
RATES = [Decimal("3000"), Decimal("25000")]
FEE_SLOT = "gb-battery-queue-fee-2026"
DATA_CENTRE_SLOT = "gb-data-centre-queue-commitment-fee-2026"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ndjson(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def fmt_mw(value: object) -> str:
    return f"{Decimal(str(value)):,}" if value is not None else "—"


def fmt_days(value: object) -> str:
    """A day count; a median over an even count may be a half-day."""
    if value is None:
        return "—"
    d = Decimal(str(value))
    return f"{d.quantize(Decimal('1')) if d == d.to_integral_value() else d}"


def fmt_pct(value: object) -> str:
    return f"{Decimal(str(value)) * 100:.1f}%" if value is not None else "—"


def plural(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def fmt_gbp(value: Decimal) -> str:
    return f"£{value.quantize(Decimal('1')):,}"


def main() -> None:
    census = json.loads(CENSUS.read_text())
    gate = json.loads(GATE.read_text())
    committed = ndjson(ROWS)
    gate_rows = ndjson(GATE_ROWS)
    as_of = date.fromisoformat(census["as_of"])

    result = add.addendum(committed, as_of, gate_rows, RATES)
    obs = result["observation"]
    if obs["committed_rows"] != census["selected_rows"] or obs["committed_mw"] != Decimal(
        census["selected_mw"]
    ):
        raise SystemExit(
            "refusing: the committed rows do not sum to the census's own headline "
            f"({obs['committed_rows']} rows / {obs['committed_mw']} MW read; "
            f"{census['selected_rows']} / {census['selected_mw']} published)."
        )
    if len(gate_rows) != gate["confirmed_tier_overdue_rows"]:
        raise SystemExit("refusing: gate-rows.ndjson does not match gate.json's row count.")

    summary = {
        "investigation": "017",
        "kind": "addendum, outside R7 and outside version 2's breakdowns; not a governed slot",
        "computed_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "inputs": {
            "rows.ndjson": sha256(ROWS),
            "gate-rows.ndjson": sha256(GATE_ROWS),
            "census.json": sha256(CENSUS),
            "gate.json": sha256(GATE),
            "declaration_v1_sha256": census["declaration_sha256"],
            "declaration_v2_sha256": gate["declaration_sha256"],
            "copy_sha256": census["copy"]["sha256"],
        },
        "fee_slots_cited_not_rederived": [FEE_SLOT, DATA_CENTRE_SLOT],
        **result,
    }
    write_json(OUT_JSON, summary)
    OUT_MD.write_text(render(summary))
    print(
        f"storage rows {obs['storage_rows']} / {obs['storage_mw']} MW of "
        f"{obs['committed_rows']} / {obs['committed_mw']} MW; "
        f"plant type unreadable on {obs['rows_with_no_readable_plant_type']} rows"
    )


def render(s: dict[str, Any]) -> str:
    obs, ill, inputs = s["observation"], s["illustration"], s["inputs"]
    only, comp = obs["storage_only"], obs["storage_compound"]
    lines = [
        "# 017 — addendum: the storage rows, and a proposed fee laid beside them",
        "",
        f"*Computed {s['computed_at']} from the committed evidence of 017's two runs and "
        "nothing else: `evidence/rows.ndjson` (SHA-256 "
        f"`{inputs['rows.ndjson'][:16]}…`) and `evidence/gate-rows.ndjson` "
        f"(`{inputs['gate-rows.ndjson'][:16]}…`), under declarations "
        f"`{inputs['declaration_v1_sha256'][:8]}…` and `{inputs['declaration_v2_sha256'][:8]}…`. "
        "The register copy was not re-read; nothing was fetched.*",
        "",
        "**What this is.** A re-reading of rows the census already published, "
        "asked for on 2026-09-17 after Ofgem's proposal of a queue fee for "
        "battery projects. It is **outside** version 1's R7 (four breakdowns, "
        "no fifth after the run) and version 2's six Gate breakdowns, and it "
        "says so rather than pretending to be one of them. Nothing here enters "
        "`FINDINGS.md`, `post-facts.json` or any governed slot; an outbound use "
        "of a figure below needs its own frozen declaration. The three parts are "
        "kept apart: what the rows say, what a proposed fee could be read as "
        "covering, and an arithmetic illustration that is none of a saving, a "
        "loss, a liability or a forecast.",
        "",
        "## Observation — the rows as committed",
        "",
        f"The census is {obs['committed_rows']} rows / {fmt_mw(obs['committed_mw'])} MW: "
        f"entries in the copy of {obs['as_of']} dated earlier than that copy and not Built. "
        f"Plant type is readable on every one of them "
        f"({obs['rows_with_no_readable_plant_type']} rows carry no readable plant type). "
        "A row is *storage* when its printed plant type, split on the register's `;`, "
        f"carries the token `{add.STORAGE_TOKEN}` exactly; `BESS` or `battery` in a "
        "project name counts for nothing.",
        "",
        f"**{obs['storage_rows']} rows / {fmt_mw(obs['storage_mw'])} MW carry the storage "
        f"token**: {only['rows']} rows / {fmt_mw(only['mw'])} MW print it alone, and "
        f"{comp['rows']} rows / {fmt_mw(comp['mw'])} MW print it inside a compound type. "
        "A compound row's MW is the row's whole stage capacity; the register does not "
        "split it between technologies and neither does this. Two shares, as 017 R11 "
        f"requires: the storage rows are {fmt_pct(obs['storage_row_share_of_census'])} of "
        f"the census's rows and {fmt_pct(obs['storage_capacity_share_of_census'])} of its "
        f"MW. {plural(obs['storage_rows_zero_capacity'], 'storage row')} print a capacity "
        f"of 0 and {plural(obs['storage_rows_without_capacity'], 'storage row')} print no "
        "capacity (017 R5); they are counted as rows and add nothing to any MW figure.",
        "",
        "| Plant type as printed | Class | Rows | MW |",
        "|---|---|---|---|",
    ]
    for g in obs["by_plant_type"]:
        lines.append(
            f"| {g['plant_type']} | {g['storage_class']} | {g['rows']} | {fmt_mw(g['mw'])} |"
        )
    lines += ["", "| Status as printed (storage rows) | Rows | MW |", "|---|---|---|"]
    for g in obs["by_status"]:
        lines.append(f"| {g['status']} | {g['rows']} | {fmt_mw(g['mw'])} |")
    lines += [
        "",
        "### How far behind the copy's own date",
        "",
        "Days from the row's effective date to 2026-09-15, the copy's publication "
        "date (017 R2). Bucket upper bounds are inclusive.",
        "",
        "| | Storage only | Storage in a compound type |",
        "|---|---|---|",
        f"| Rows / MW | {only['rows']} / {fmt_mw(only['mw'])} "
        f"| {comp['rows']} / {fmt_mw(comp['mw'])} |",
        f"| Shortest, days | {fmt_days(only['days_behind_min'])} "
        f"| {fmt_days(comp['days_behind_min'])} |",
        f"| Median, days | {fmt_days(only['days_behind_median'])} "
        f"| {fmt_days(comp['days_behind_median'])} |",
        f"| Longest, days | {fmt_days(only['days_behind_max'])} "
        f"| {fmt_days(comp['days_behind_max'])} |",
    ]
    for b_only, b_comp in zip(only["buckets"], comp["buckets"], strict=True):
        lines.append(
            f"| {b_only['bucket']} | {plural(b_only['rows'], 'row')} / {fmt_mw(b_only['mw'])} MW "
            f"| {plural(b_comp['rows'], 'row')} / {fmt_mw(b_comp['mw'])} MW |"
        )
    lines += [
        "",
        "### The Gate cell, where the committed evidence carries it",
        "",
        "Version 2 committed a Gate cell only for the 17 overdue rows of the "
        "confirmed tier. "
        f"**{obs['confirmed_tier_storage_rows']} of those 17 are storage rows, "
        f"{fmt_mw(obs['confirmed_tier_storage_mw'])} MW**: "
        + ", ".join(obs["confirmed_tier_storage"])
        + f". For the other {obs['gate_not_in_committed_evidence_rows']} storage rows the "
        "Gate cell is **not in the committed evidence**. It is not blank and it is not "
        "inferred; a storage-by-Gate split of the whole census would be a seventh Gate "
        "breakdown and needs a version 3 declaration frozen before it is computed.",
        "",
        "**Swapped reading.** Storage rows whose date, read day-month swapped, would "
        "fall on or after the copy's date (017 R3): "
        f"{plural(obs['storage_rows_swapped_reading_in_future'], 'row')}, "
        f"{fmt_mw(obs['storage_mw_swapped_reading_in_future'])} MW. "
        "That is inside every figure above, as the census rule declares; anyone "
        "quoting the storage MW should quote this sentence with it.",
        "",
        "| Class | Project | Plant type | Status | MW | Effective | Days behind | Gate |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in obs["rows"]:
        r = dataclasses.asdict(row) if dataclasses.is_dataclass(row) else row
        gate_cell = r["gate"] if r["gate"] is not None else "not committed"
        lines.append(
            f"| {r['storage_class']} | {r['project_name']} | {r['plant_type']} | {r['status']} | "
            f"{fmt_mw(r['mw'])} | {r['effective']} | {r['days_behind']} | {gate_cell} |"
        )
    lines += [
        "",
        "## Interpretation — what a proposed fee could be read as covering",
        "",
        "Everything in this section rests on facts held as external assertions in "
        f"the business register (etrmbiz slots `{FEE_SLOT}` and `{DATA_CENTRE_SLOT}`), "
        "cited and not re-derived here. As those slots record it: on 2026-09-17 Ofgem "
        "proposed, for consultation, a fee for battery-storage projects waiting in the "
        "GB connections queue, £3,000 per MW and potentially £25,000 per MW if the "
        "queue remains significantly oversubscribed, refunded if the project connects. "
        "The slot also records that **Ofgem's own statement has not been read**; the "
        "figures are Bloomberg's report of it.",
        "",
        "What the register can and cannot say about which rows such a fee would reach:",
        "",
        "- The register prints `Energy Storage System`, not *battery*. Whether every "
        "row so labelled is a battery, and whether a compound `Energy Storage "
        "System;PV Array` row would be assessed on its whole MW, on a storage share, "
        "or not at all, is not knowable from the register.",
        "- Whether the proposal reaches projects that already hold an offer, or only "
        "new applications; whether it reaches transmission-connected projects, "
        "distribution-connected ones, or both; whether *per MW* means TEC or some "
        "other capacity; and whether Gate 1 and Gate 2 projects are treated alike — "
        "none of that is in the second-hand report, and none of it is inferred here.",
        "- A row that is past its date and not Built is, on the register's face, still "
        "in the queue. Whether NESO or Ofgem would count it as *waiting* under the "
        "proposal is their definition to supply, not this addendum's.",
        "",
        "So the honest statement is: **these are the storage rows the census found; "
        "which of them a fee that is only proposed would fall on is not determinable "
        "from the register, and is left open.**",
        "",
        "## Illustration — rate times MW, and nothing more",
        "",
        "**This is an illustration.** Each figure is a proposed per-MW rate multiplied "
        "by a published capacity. It is **not** a saving, a loss, a liability, an "
        "amount any party would post, owe or forfeit, or a forecast of what the "
        "consultation will decide. The rates are proposed, refundable on connection "
        "as reported, and may never apply to any row here.",
        "",
        "| Rows | MW | at £3,000 / MW | at £25,000 / MW |",
        "|---|---|---|---|",
    ]
    for label, key in (
        ("Storage only", "storage_only"),
        ("Storage only and compound together", "storage_only_and_compound"),
        ("Storage rows in the confirmed tier (Gate 2), a subset", "confirmed_tier_storage"),
    ):
        cells = ill[key]
        lines.append(
            f"| {label} | {fmt_mw(cells[0]['mw'])} | {fmt_gbp(Decimal(str(cells[0]['gbp'])))} "
            f"| {fmt_gbp(Decimal(str(cells[1]['gbp'])))} |"
        )
    lines += [
        "",
        "## What this addendum never claims",
        "",
        "- That any project is late, has failed, or will pay anything. The register "
        "records a plant type, a date and a status; the fee is a proposal; the "
        "product of the two is arithmetic.",
        "- That `Energy Storage System` means battery, or that a compound row is a battery row.",
        "- That the storage share of the census has any meaning beyond this copy, "
        "or that it is a breakdown of the census under either declaration.",
        "",
        "## Reproducibility",
        "",
        "`uv run python investigations/017-the-overdue-queue/addendum.py` recomputes "
        "this file and `evidence/addendum-storage.json` from the committed rows, and "
        "refuses if the rows no longer sum to the census's headline. Rules are in "
        "`grid_mysteries.investigations.overdue_queue_addendum`, tested in "
        "`tests/test_overdue_queue_addendum.py`. Input digests: "
        f"`rows.ndjson` `{inputs['rows.ndjson']}`; "
        f"`gate-rows.ndjson` `{inputs['gate-rows.ndjson']}`; "
        f"`census.json` `{inputs['census.json']}`; "
        f"`gate.json` `{inputs['gate.json']}`; "
        f"the copy `{inputs['copy_sha256']}`.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
