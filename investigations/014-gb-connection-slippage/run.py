"""014 — GB Connection Slippage: gated, idempotent, append-only runner.

    uv run --group registers python investigations/014-gb-connection-slippage/run.py \\
        --seal <prefix of the declaration's SHA-256> --phase all [--run-date YYYY-MM-DD]
    uv run --group registers python investigations/014-gb-connection-slippage/run.py --phase render

Three declarations exist. ``--version 3`` (the default) is
``DECLARATION-v3.md`` with evidence under ``evidence/v3/``: version 2's
series unchanged, with every movement figure split into the part the
register's stage labels determine and the figure under each of two named
identity rules (F4 and F5 refuse). Its render goes to a preview directory
until the ``release`` phase, which is the sponsor's separate seal.
``--version 2`` is ``DECLARATION-v2.md`` with ``evidence/v2/`` (the
published series until version 3 is released). ``--version 1`` is the
first, ``DECLARATION.md`` with ``evidence/``: closed, kept as run, and
available to ``check`` only.

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
- ``render``: the record page and the site page as pure functions of the
  evidence. Needs no seal. Version 3 renders to ``PREVIEW`` (gitignored)
  until it is released.
- ``release`` (version 3 only, ``--confirm-release``): the sponsor's second
  seal, done by hand. Version 2's record page moves to ``SERIES-v2.md``;
  version 3's becomes ``SERIES.md`` and the site page.
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
from grid_mysteries.investigations import connection_slippage_v3 as v3
from grid_mysteries.rendering import connection_slippage as page
from grid_mysteries.sources import tec_register as tr

HERE = Path(__file__).parent
SITE_INDEX = REPO_ROOT / "site" / "connection-slippage" / "index.html"
#: Version 3's pages before the sponsor's release seal: gitignored, so no
#: merge or push can publish them by accident.
PREVIEW = REPO_ROOT / "data" / "derived" / "014-v3-preview"
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
        self.partial_export_rule = number >= 2
        self.append_only_rows = number >= 2
        self.closed = number == 1
        self.split = number >= 3

    @property
    def released(self) -> bool:
        """Version 3 is released once its record page has become SERIES.md,
        which moves version 2's to SERIES-v2.md."""
        return (HERE / "SERIES-v2.md").exists()

    @property
    def series_md(self) -> Path:
        if self.number == 1:
            return HERE / "SERIES-v1.md"
        if self.number == 2:
            return HERE / ("SERIES-v2.md" if self.released else "SERIES.md")
        return HERE / "SERIES.md" if self.released else PREVIEW / "SERIES.md"

    @property
    def site_index(self) -> Path | None:
        """Where this version's site page goes, if anywhere."""
        if self.number == 2:
            return None if self.released else SITE_INDEX
        if self.number == 3:
            return SITE_INDEX if self.released else PREVIEW / "index.html"
        return None

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


def require_v2_side_unchanged(rows: list[dict[str, Any]]) -> None:
    """Every row's version 2 fields must serialise byte for byte as version
    2's committed line for the same copy: version 3 only adds a `v3` key."""
    committed = committed_rows(Version(2))
    differing, missing = [], []
    for r in rows:
        key = (r["t_public"].isoformat(), r["sha256"])
        line = row_line({k: v for k, v in r.items() if k != "v3"})
        if key not in committed:
            missing.append(key[0])
        elif committed[key] != line:
            differing.append(key[0])
    if differing:
        raise SystemExit(
            f"refusing: the version 2 side of {len(differing)} row(s) differs from "
            f"evidence/v2 ({', '.join(differing[:5])})"
        )
    print(
        f"version 2 side: {len(rows) - len(missing)} row(s) byte-identical to evidence/v2"
        + (f"; {len(missing)} copy(ies) newer than version 2's last run" if missing else "")
    )


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
    if version.split:
        try:
            result = v3.series(
                usable, rule_digest=v3.declared_rule_digest(version.declaration.read_text())
            )
        except (v3.RuleDisagreement, v3.ContentRuleChanged) as exc:
            raise SystemExit(f"refusing: {exc}") from None
    else:
        result = cs.series(usable, partial_export_rule=version.partial_export_rule)
    rows = flatten_rows(result)
    if version.split:
        require_v2_side_unchanged(rows)
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
        "released": version.released if version.split else None,
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
    if head and version.split:
        split = head["v3"]["vs_year_earlier"]
        print(
            f"v3 headline: determined {split['determined']} over "
            f"{split['undetermined_groups']} undetermined group(s); "
            + ", ".join(f"{rule} {total}" for rule, total in split["total"].items())
        )
        print(
            f"v3 chain (old): determined {head['v3']['determined']}; "
            + ", ".join(f"{rule} {total}" for rule, total in head["v3"]["total"].items())
            + f"; undetermined share {head['v3']['undetermined_share_percent']}"
        )
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
    version.series_md.parent.mkdir(parents=True, exist_ok=True)
    version.series_md.write_text(page.render_markdown(series))
    written = [version.series_md]
    site = version.site_index
    if site is not None:
        site.parent.mkdir(parents=True, exist_ok=True)
        site.write_text(page.render_page(series))
        written.append(site)
    print("rendered " + " and ".join(str(p.relative_to(REPO_ROOT)) for p in written))


def release(confirm: bool) -> None:
    """The sponsor's second seal for version 3: its pages replace version 2's."""
    if not confirm:
        raise SystemExit("refusing: release is the sponsor's seal; pass --confirm-release")
    version = Version(3)
    if version.released:
        raise SystemExit("version 3 is already released")
    (HERE / "SERIES-v2.md").write_text(page.render_markdown(load_series(Version(2))))
    render(version)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seal", help="prefix of the declaration's SHA-256 (fetch, compute, check)"
    )
    parser.add_argument(
        "--phase",
        choices=("fetch", "compute", "render", "check", "all", "release"),
        default="render",
    )
    parser.add_argument("--version", type=int, choices=(1, 2, 3), default=3)
    parser.add_argument(
        "--confirm-release", action="store_true", help="the sponsor's release seal (release)"
    )
    parser.add_argument("--run-date", default=date.today().isoformat())
    parser.add_argument("--amend", action="store_true", help="allow committed rows to change")
    args = parser.parse_args(argv)
    version = Version(args.version)
    if args.phase == "release":
        release(args.confirm_release)
        return
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
