"""014 — GB Connection Slippage: gated, idempotent, append-only runner.

    uv run --group registers python investigations/014-gb-connection-slippage/run.py \\
        --seal <prefix of the declaration's SHA-256> --phase all [--run-date YYYY-MM-DD]
    uv run --group registers python investigations/014-gb-connection-slippage/run.py --phase render

Two declarations exist. ``--version 2`` (the default) is ``DECLARATION-v2.md``
with evidence under ``evidence/v2/``: reading rules with the July 2020
header aliases, the partial-export rule, and append-only rows. ``--version
1`` is the first, ``DECLARATION.md`` with ``evidence/``: closed, kept as
run, and available to ``check`` only.

Phases:

- ``fetch`` (needs the seal): pin today's live TEC Register from the data
  portal as a new copy in ``data/raw/neso/tec-history`` and its journal,
  unless a live copy for the resource's ``last_modified`` date is already
  journalled. Never overwrites.
- ``compute`` (needs the seal): verify every journalled copy against its
  digest, parse it, apply the declared reading rules, run the series and
  write the evidence. Rows are **append-only**: ``rows.ndjson`` gains one
  line per new copy and an existing line must be byte-identical to its
  recomputation or the run refuses (``--amend`` overrides, for a dated
  entry in AMENDMENTS.md). ``series.json`` holds the summary (headline,
  annual windows, propositions, flags, suspect copies, gaps) and is
  rewritten each run.
- ``check`` (needs the seal): recompute and compare with the committed
  rows without writing anything.
- ``render``: ``SERIES.md`` and ``site/connection-slippage/index.html`` as
  pure functions of the evidence. Needs no seal.
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import dumps, write_json
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.rendering import connection_slippage as page
from grid_mysteries.sources import tec_register as tr

HERE = Path(__file__).parent
SITE_INDEX = REPO_ROOT / "site" / "connection-slippage" / "index.html"
JOURNAL = REPO_ROOT / tr.JOURNAL_PATH
RAW_DIR = REPO_ROOT / tr.RAW_DIR
SCHEMA_REPORT = REPO_ROOT / "archives" / "tec-register" / "schema-report.json"
REQUIRED_COLUMNS = (
    "Project Name",
    "Customer Name",
    "Connection Site",
    "MW Increase / Decrease",
    "MW Effective From",
)
MIN_SEAL_LENGTH = 8


class Version:
    """Where one declaration's files live and which rules it declares."""

    def __init__(self, number: int) -> None:
        self.number = number
        name = "DECLARATION.md" if number == 1 else f"DECLARATION-v{number}.md"
        self.declaration = HERE / name
        self.evidence = HERE / "evidence" if number == 1 else HERE / "evidence" / f"v{number}"
        self.series_md = HERE / ("SERIES-v1.md" if number == 1 else "SERIES.md")
        self.partial_export_rule = number >= 2
        self.append_only_rows = number >= 2
        self.closed = number == 1

    @property
    def series_json(self) -> Path:
        return self.evidence / "series.json"

    @property
    def rows_ndjson(self) -> Path:
        return self.evidence / "rows.ndjson"

    @property
    def manifest(self) -> Path:
        return self.evidence / "vintage-manifest.json"

    @property
    def run_log(self) -> Path:
        return self.evidence / "run-log.json"

    def digest(self) -> str:
        return hashlib.sha256(self.declaration.read_bytes()).hexdigest()

    def require_seal(self, seal: str | None) -> str:
        digest = self.digest()
        if not seal or len(seal) < MIN_SEAL_LENGTH or not digest.startswith(seal.lower()):
            raise SystemExit(
                f"refusing: --seal must be a prefix (>= {MIN_SEAL_LENGTH} hex) of "
                f"{self.declaration.name}'s SHA-256 {digest[:16]}…"
            )
        return digest

    def timestamps(self) -> dict[str, Any] | None:
        sidecar = self.declaration.with_name(self.declaration.name + ".timestamps.json")
        if not sidecar.exists():
            return None
        stamps = json.loads(sidecar.read_text())
        return {
            "sha256": stamps["sha256"],
            "matches_declaration": stamps["sha256"] == self.digest(),
            "proofs": [
                {k: v for k, v in p.items() if k in ("kind", "tsa", "path", "tsa_time", "status")}
                for p in stamps["proofs"]
            ],
        }


# -------------------------------------------------------------------- fetch


def fetch() -> None:
    entry = tr.pin_live_vintage(JOURNAL, RAW_DIR, REPO_ROOT, fetched_at=datetime.now(UTC))
    if entry is None:
        print("fetch: live copy for the resource's current last_modified date already pinned")
    else:
        print(f"pinned {entry['path']} (t_public {entry['t_public']}, {entry['row_count']} rows)")


# ------------------------------------------------------------------ compute


def usable_vintages(
    parsed: list[tuple[date, list[dict[str, object]], dict]],
) -> tuple[list[cs.VintageInput], list[dict[str, Any]]]:
    usable, excluded = [], []
    for t, rows, entry in parsed:
        columns = {tr.canon(c) for c in (entry.get("columns") or [])}
        missing = [c for c in REQUIRED_COLUMNS if c not in columns]
        if missing:
            excluded.append({"t_public": t, "path": entry["path"], "missing": missing})
            continue
        usable.append(
            cs.VintageInput(
                t_public=t, rows=tuple(rows), sha256=entry["sha256"], path=entry["path"]
            )
        )
    return usable, excluded


def flatten_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"regime": segment["regime"], **row}
        for segment in result["segments"]
        for row in segment["rows"]
    ]


def committed_rows(version: Version) -> dict[tuple[str, str], str]:
    """(t_public, sha256) -> serialised row, from the committed evidence."""
    out: dict[tuple[str, str], str] = {}
    if version.append_only_rows:
        if version.rows_ndjson.exists():
            for line in version.rows_ndjson.read_text().splitlines():
                if line.strip():
                    row = json.loads(line)
                    out[(row["t_public"], row["sha256"])] = line
    elif version.series_json.exists():
        for segment in json.loads(version.series_json.read_text()).get("segments", []):
            for row in segment["rows"]:
                out[(row["t_public"], row["sha256"])] = dumps(row)
    return out


def row_line(row: dict[str, Any]) -> str:
    """One row as one NDJSON line, through the evidence serialiser."""
    return json.dumps(json.loads(dumps(row)), separators=(",", ":"))


def compute(version: Version, run_date: str, seal: str, *, amend: bool, write: bool) -> None:
    digest = version.require_seal(seal)
    if version.closed and write:
        raise SystemExit(f"refusing: version {version.number} is closed; use --phase check")
    journal = tr.read_journal(JOURNAL)
    distinct = tr.one_per_date(journal)
    parsed, skipped = tr.load_vintages(JOURNAL, REPO_ROOT)
    usable, excluded = usable_vintages(parsed)
    print(
        f"copies: {len(journal)} journal rows, {len(distinct)} distinct dates, "
        f"{len(parsed)} parsed, {len(usable)} usable, {len(skipped)} unparseable, "
        f"{len(excluded)} excluded"
    )
    result = cs.series(usable, partial_export_rule=version.partial_export_rule)
    rows = flatten_rows(result)
    committed = committed_rows(version)
    serialised = {
        (r["t_public"].isoformat(), r["sha256"]): (
            row_line(r)
            if version.append_only_rows
            # version 1 rows carry no regime field
            else dumps(json.loads(dumps({k: v for k, v in r.items() if k != "regime"})))
        )
        for r in rows
    }
    changed = [k[0] for k, text in serialised.items() if k in committed and committed[k] != text]
    new = [k for k in serialised if k not in committed]
    if not write:
        print(
            f"check: {len(rows)} rows recomputed, {len(new)} not yet committed, "
            f"{len(changed)} committed row(s) would change"
            + (f" ({', '.join(changed[:5])})" if changed else "")
        )
        if changed:
            raise SystemExit(1)
        return
    if changed and not amend:
        raise SystemExit(
            f"refusing: {len(changed)} committed row(s) would change on recompute "
            f"({', '.join(changed[:5])}…). Rows are append-only; record an amendment in "
            "AMENDMENTS.md and rerun with --amend."
        )
    computed_at = datetime.now(UTC).isoformat(timespec="seconds")
    version.evidence.mkdir(parents=True, exist_ok=True)
    if amend and changed:
        version.rows_ndjson.write_text("")
        new = list(serialised)
    with version.rows_ndjson.open("a") as out:
        for key in new:
            out.write(serialised[key] + "\n")
    summary: dict[str, Any] = {
        "investigation": "014",
        "declaration": version.declaration.name,
        "declaration_sha256": digest,
        "declaration_timestamps": version.timestamps(),
        "schema_report_sha256": (
            hashlib.sha256(SCHEMA_REPORT.read_bytes()).hexdigest()
            if SCHEMA_REPORT.exists()
            else None
        ),
        "seal": seal,
        "run_date": run_date,
        "computed_at": computed_at,
        "rows_file": version.rows_ndjson.name,
        "rows_appended": len(new),
        "rows_total": len(rows),
        "vintages": {
            "journal_rows": len(journal),
            "distinct_dates": len(distinct),
            "parsed": len(parsed),
            "usable": len(usable),
            "skipped": skipped,
            "excluded": excluded,
            "first": usable[0].t_public if usable else None,
            "last": usable[-1].t_public if usable else None,
        },
    }
    summary.update({k: v for k, v in result.items() if k != "segments"})
    summary["segments"] = [
        {k: v for k, v in segment.items() if k != "rows"} | {"rows": len(segment["rows"])}
        for segment in result["segments"]
    ]
    write_json(version.series_json, summary)
    by_path = {e["path"]: e for e in distinct}
    write_json(
        version.manifest,
        [
            {
                "dataset": "NESO-TEC-REGISTER",
                "t_public": v.t_public,
                "path": v.path,
                "sha256": v.sha256,
                "bytes": by_path[v.path].get("bytes"),
                "source": by_path[v.path].get("source"),
                "url": by_path[v.path].get("url"),
                "t_public_basis": by_path[v.path].get("t_public_basis"),
            }
            for v in usable
        ],
    )
    log = json.loads(version.run_log.read_text()) if version.run_log.exists() else []
    log.append(
        {
            "run_date": run_date,
            "computed_at": computed_at,
            "seal": seal,
            "declaration_sha256": digest,
            "vintages_usable": len(usable),
            "rows_appended": len(new),
            "latest_vintage": usable[-1].t_public if usable else None,
            "amend": amend,
        }
    )
    write_json(version.run_log, log)
    head = summary["headline"]
    if head:
        print(
            f"headline: {head['baseline']} -> {head['t_public']}: "
            f"net {head['mw_years_net']} MW-years (later {head['mw_years_later']}, "
            f"earlier {head['mw_years_earlier']}) over {head['matched']} matched; "
            f"chained {head['cumulative_mw_years_net']}"
        )
    print(
        f"rows: {len(new)} appended, {len(rows)} total; "
        f"suspect copies: {len(result['suspect_copies'])}"
    )


# ------------------------------------------------------------------- render


def load_series(version: Version) -> dict[str, Any]:
    """The summary with its rows re-attached, as the renderer expects."""
    series = json.loads(version.series_json.read_text())
    if version.append_only_rows:
        rows = [
            json.loads(line)
            for line in version.rows_ndjson.read_text().splitlines()
            if line.strip()
        ]
        for segment in series["segments"]:
            segment["rows"] = sorted(
                (r for r in rows if r["regime"] == segment["regime"]),
                key=lambda r: r["t_public"],
            )
    return series


def render(version: Version) -> None:
    series = load_series(version)
    version.series_md.write_text(page.render_markdown(series))
    SITE_INDEX.parent.mkdir(parents=True, exist_ok=True)
    SITE_INDEX.write_text(page.render_page(series))
    print(
        f"rendered {version.series_md.relative_to(REPO_ROOT)} and "
        f"{SITE_INDEX.relative_to(REPO_ROOT)}"
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seal", help="prefix of the declaration's SHA-256 (fetch, compute, check)"
    )
    parser.add_argument(
        "--phase", choices=("fetch", "compute", "render", "check", "all"), default="render"
    )
    parser.add_argument("--version", type=int, choices=(1, 2), default=2)
    parser.add_argument("--run-date", default=date.today().isoformat())
    parser.add_argument("--amend", action="store_true", help="allow committed rows to change")
    args = parser.parse_args(argv)
    version = Version(args.version)
    if args.phase in ("fetch", "all"):
        version.require_seal(args.seal)
        fetch()
    if args.phase == "check":
        compute(version, args.run_date, args.seal, amend=False, write=False)
        return
    if args.phase in ("compute", "all"):
        compute(version, args.run_date, args.seal, amend=args.amend, write=True)
    if args.phase in ("render", "all"):
        render(version)


if __name__ == "__main__":
    sys.exit(main())
