"""014 — GB Connection Slippage: gated, idempotent runner.

    uv run --group registers python investigations/014-gb-connection-slippage/run.py \\
        --seal <prefix of DECLARATION.md's SHA-256> --phase all [--run-date YYYY-MM-DD]
    uv run --group registers python investigations/014-gb-connection-slippage/run.py --phase render

Phases:

- ``fetch`` (needs the seal): pin today's live TEC Register from the data
  portal as a new vintage in ``data/raw/neso/tec-history`` and its journal,
  unless a live vintage for the resource's ``last_modified`` date is already
  journalled (then it is verified and skipped). Never overwrites.
- ``compute`` (needs the seal): verify every journalled vintage against its
  digest, parse it, drop any lacking a required column, run the declared
  series and write ``evidence/series.json``, ``evidence/vintage-manifest.json``
  and a line in ``evidence/run-log.json``. Idempotent and append-only: a row
  already in ``series.json`` for the same vintage bytes must recompute
  byte-identically or the run refuses (``--amend`` overrides, for a dated
  entry in AMENDMENTS.md).
- ``render``: ``SERIES.md`` and ``site/connection-slippage/index.html`` as
  pure functions of ``evidence/series.json``. Needs no seal.
- ``check`` (needs the seal): recompute and compare with the committed rows
  without writing anything, not even a run-log line. The idempotency check
  that belongs before a commit.

The seal is the declaration's digest: the command that computed carries the
prefix of the frozen rules it ran under, and the run log records it beside
the declaration's external timestamps.
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
EVIDENCE = HERE / "evidence"
DECLARATION = HERE / "DECLARATION.md"
SERIES_JSON = EVIDENCE / "series.json"
VINTAGE_MANIFEST = EVIDENCE / "vintage-manifest.json"
RUN_LOG = EVIDENCE / "run-log.json"
SERIES_MD = HERE / "SERIES.md"
SITE_INDEX = REPO_ROOT / "site" / "connection-slippage" / "index.html"
JOURNAL = REPO_ROOT / tr.JOURNAL_PATH
RAW_DIR = REPO_ROOT / tr.RAW_DIR
REQUIRED_COLUMNS = (
    "Project Name",
    "Customer Name",
    "Connection Site",
    "MW Increase / Decrease",
    "MW Effective From",
)
MIN_SEAL_LENGTH = 8


def declaration_digest() -> str:
    return hashlib.sha256(DECLARATION.read_bytes()).hexdigest()


def require_seal(seal: str | None) -> str:
    digest = declaration_digest()
    if not seal or len(seal) < MIN_SEAL_LENGTH or not digest.startswith(seal.lower()):
        raise SystemExit(
            f"refusing: --seal must be a prefix (>= {MIN_SEAL_LENGTH} hex) of the declaration's "
            f"SHA-256 {digest[:16]}…; the sponsor's seal is that prefix"
        )
    return digest


def declaration_timestamps() -> dict[str, Any] | None:
    sidecar = HERE / "DECLARATION.md.timestamps.json"
    if not sidecar.exists():
        return None
    stamps = json.loads(sidecar.read_text())
    return {
        "sha256": stamps["sha256"],
        "matches_declaration": stamps["sha256"] == declaration_digest(),
        "proofs": [
            {k: v for k, v in p.items() if k in ("kind", "tsa", "path", "tsa_time", "status")}
            for p in stamps["proofs"]
        ],
    }


# -------------------------------------------------------------------- fetch


def fetch(run_date: str) -> None:
    fetched_at = datetime.now(UTC)
    entry = tr.pin_live_vintage(JOURNAL, RAW_DIR, REPO_ROOT, fetched_at=fetched_at)
    if entry is None:
        print("fetch: live vintage for the resource's current last_modified date already pinned")
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


def previous_rows() -> dict[tuple[str, str], str]:
    """(t_public, sha256) -> serialised row, from the committed series."""
    if not SERIES_JSON.exists():
        return {}
    previous = json.loads(SERIES_JSON.read_text())
    out = {}
    for segment in previous.get("segments", []):
        for row in segment["rows"]:
            out[(row["t_public"], row["sha256"])] = dumps(row)
    return out


def compute(run_date: str, seal: str, *, amend: bool, write: bool = True) -> dict[str, Any]:
    digest = require_seal(seal)
    journal = tr.read_journal(JOURNAL)
    distinct = tr.one_per_date(journal)
    parsed, skipped = tr.load_vintages(JOURNAL, REPO_ROOT)
    usable, excluded = usable_vintages(parsed)
    print(
        f"vintages: {len(journal)} journal rows, {len(distinct)} distinct dates, "
        f"{len(parsed)} parsed, {len(usable)} usable, {len(skipped)} unparseable, "
        f"{len(excluded)} excluded"
    )
    result = cs.series(usable)
    committed = previous_rows()
    changed = []
    for segment in result["segments"]:
        for row in segment["rows"]:
            key = (row["t_public"].isoformat(), row["sha256"])
            if key in committed and committed[key] != dumps(json.loads(dumps(row))):
                changed.append(key[0])
    if not write:
        total = sum(len(s["rows"]) for s in result["segments"])
        new_rows = total - sum(
            1
            for s in result["segments"]
            for r in s["rows"]
            if (r["t_public"].isoformat(), r["sha256"]) in committed
        )
        print(
            f"check: {total} rows recomputed, {new_rows} not yet committed, "
            f"{len(changed)} committed row(s) would change"
            + (f" ({', '.join(changed[:5])})" if changed else "")
        )
        if changed:
            raise SystemExit(1)
        return result
    if changed and not amend:
        raise SystemExit(
            f"refusing: {len(changed)} committed row(s) would change on recompute "
            f"({', '.join(changed[:5])}…). Rows are append-only; record an amendment in "
            "AMENDMENTS.md and rerun with --amend."
        )
    computed_at = datetime.now(UTC).isoformat(timespec="seconds")
    series = {
        "investigation": "014",
        "declaration_sha256": digest,
        "declaration_timestamps": declaration_timestamps(),
        "seal": seal,
        "run_date": run_date,
        "computed_at": computed_at,
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
        **result,
    }
    write_json(SERIES_JSON, series)
    by_path = {e["path"]: e for e in distinct}
    manifest = [
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
    ]
    write_json(VINTAGE_MANIFEST, manifest)
    log = json.loads(RUN_LOG.read_text()) if RUN_LOG.exists() else []
    log.append(
        {
            "run_date": run_date,
            "computed_at": computed_at,
            "seal": seal,
            "declaration_sha256": digest,
            "vintages_usable": len(usable),
            "latest_vintage": usable[-1].t_public if usable else None,
            "amend": amend,
        }
    )
    write_json(RUN_LOG, log)
    head = series["headline"]
    if head:
        print(
            f"headline: {head['baseline']} -> {head['t_public']}: "
            f"net {head['mw_years_net']} MW-years "
            f"(later {head['mw_years_later']}, earlier {head['mw_years_earlier']}) over "
            f"{head['matched']} matched project-stages; chained {head['cumulative_mw_years_net']}"
        )
    return series


# ------------------------------------------------------------------- render


def render() -> None:
    series = json.loads(SERIES_JSON.read_text())
    SERIES_MD.write_text(page.render_markdown(series))
    SITE_INDEX.parent.mkdir(parents=True, exist_ok=True)
    SITE_INDEX.write_text(page.render_page(series))
    print(f"rendered {SERIES_MD.relative_to(REPO_ROOT)} and {SITE_INDEX.relative_to(REPO_ROOT)}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seal", help="prefix of DECLARATION.md's SHA-256 (fetch, compute)")
    parser.add_argument(
        "--phase", choices=("fetch", "compute", "render", "check", "all"), default="render"
    )
    parser.add_argument("--run-date", default=date.today().isoformat())
    parser.add_argument("--amend", action="store_true", help="allow committed rows to change")
    args = parser.parse_args(argv)
    if args.phase in ("fetch", "all"):
        require_seal(args.seal)
        fetch(args.run_date)
    if args.phase == "check":
        compute(args.run_date, args.seal, amend=False, write=False)
        return
    if args.phase in ("compute", "all"):
        compute(args.run_date, args.seal, amend=args.amend)
    if args.phase in ("render", "all"):
        render()


if __name__ == "__main__":
    sys.exit(main())
