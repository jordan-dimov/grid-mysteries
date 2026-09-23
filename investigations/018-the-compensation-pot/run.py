"""018 — the compensation pot after P511: gated, idempotent runner.

    uv run python investigations/018-the-compensation-pot/run.py \\
        --seal <prefix of DECLARATION.md's SHA-256> --phase index
    uv run python investigations/018-the-compensation-pot/run.py --seal <prefix> --phase acquire
    uv run python investigations/018-the-compensation-pot/run.py --phase compute

``index`` pins the P114 S0142 listing for every publication date from
2025-09-03 to the day before the run and writes ``evidence/run-index.json``.
``acquire`` refuses under C5 until every POST day has an SF run listed, then
pins one BM unit register vintage and every S0142 file the declaration's
windows select. ``compute`` reads pinned bytes only. The Portal key comes
from ``ELEXON_PORTAL_KEY`` (in etrmbiz's ``.envrc``) and is never
journalled, printed or committed.
"""

import argparse
import gzip
import hashlib
import json
import sys
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import write_json
from grid_mysteries.hashing import sha256_file
from grid_mysteries.investigations import p415_compensation as p4
from grid_mysteries.sources import elexon, elexon_portal
from grid_mysteries.sources.pinning import load_journal, pin, progress

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
DECLARATION = HERE / "DECLARATION.md"
RAW = REPO_ROOT / "data" / "raw" / "elexon" / "018"
SCHEMA_PASS = RAW / "schema-pass"

KILL_H1 = Decimal("0.50")
H2_BASELINE_ABOVE = Decimal("0.50")
H2_VTP_POST_BELOW = Decimal("0.10")
H2_SUP_POST_BELOW = Decimal("0.25")
H3_ABOVE, H3_DAYS = Decimal("0.05"), 2
C4_BAND = Decimal("0.15")
ELEXON_FEB_PAID = Decimal("5576308")
ELEXON_FEB_VTP_MWH = Decimal("63827.48")
MAX_MISSING = 2
DECISIVE = ("C1", "C2", "C3", "C6", "C7")
PRE_CONTEXT_PARTY = "ALMAPERJ"


def declaration_digest() -> str:
    return hashlib.sha256(DECLARATION.read_bytes()).hexdigest()


def require_seal(seal: str | None) -> str:
    digest = declaration_digest()
    if not seal or len(seal) < 8 or not digest.startswith(seal.lower()):
        raise SystemExit(
            f"refusing: --seal must be a prefix of DECLARATION.md's SHA-256 {digest[:16]}…"
        )
    if not (HERE / "DECLARATION.md.timestamps.json").exists():
        raise SystemExit("refusing: DECLARATION.md is not frozen (no proof sidecar)")
    return digest


def journal(name: str) -> dict[str, Path]:
    return {
        "journal_path": EVIDENCE / f"{name}-journal.ndjson",
        "manifest_path": EVIDENCE / f"{name}-manifest.json",
    }


def index(seal: str | None) -> None:
    require_seal(seal)
    last = datetime.now(UTC).date() - timedelta(days=1)
    jobs = []
    d = p4.INDEX_FROM
    while d <= last:
        jobs.append(
            ("P114-S0142-LIST", elexon_portal.list_url(d.isoformat()), RAW / "list" / f"{d}.json")
        )
        d += timedelta(days=1)
    pin(jobs, **journal("list"), fetch=elexon_portal.fetch, label="listings", sleep_seconds=0.2)
    write_json(EVIDENCE / "run-index.json", run_index())


def run_index() -> dict:
    listed: dict[str, str] = {}
    for entry in load_journal(EVIDENCE / "list-journal.ndjson").values():
        body = json.loads((REPO_ROOT / entry["path"]).read_text() or "{}")
        if isinstance(body, dict):
            listed.update({str(k): str(v) for k, v in body.items()})
    files = sorted(listed)
    by_day = p4.build_index(files)
    return {
        "listed_publication_dates": sorted(
            Path(p).stem for p in load_journal(EVIDENCE / "list-journal.ndjson")
        ),
        "files": {n: listed[n] for n in files},
        "settlement_dates": {str(d): sorted(f.run for f in fs) for d, fs in sorted(by_day.items())},
    }


def selection() -> dict:
    idx = json.loads((EVIDENCE / "run-index.json").read_text())
    return p4.select(p4.build_index(idx["files"]))


def wanted(sel: dict) -> list[p4.S0142File]:
    files = {f.filename: f for window in sel["chosen"].values() for f in window.values()}
    files.update({f.filename: f for runs in sel["restate"].values() for f in runs})
    return sorted(files.values(), key=lambda f: (f.settlement_date, f.run))


def acquire(seal: str | None) -> None:
    digest = require_seal(seal)
    sel = selection()
    if sel["missing"]["POST"]:
        days = ", ".join(str(d) for d in sel["missing"]["POST"])
        raise SystemExit(f"C5: POST days with no SF run listed yet: {days}. Re-run index later.")
    if sel["unknown_runs"]:
        print(f"C5: unknown run codes listed and never selected: {sel['unknown_runs']}")
    today = datetime.now(UTC).date().isoformat()
    pin(
        [("BMUNITS", elexon.bmunits_url(), RAW / f"bmunits-{today}.json")],
        **journal("register"),
        fetch=elexon.fetch_pinned,
        label="register",
    )
    jobs = [
        ("P114-S0142", elexon_portal.download_url(f.filename), RAW / "s0142" / f.filename)
        for f in wanted(sel)
    ]
    pin(jobs, **journal("s0142"), fetch=elexon_portal.fetch, label="s0142", progress=progress)
    log_path = EVIDENCE / "acquisition-log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {"acquisitions": []}
    log["acquisitions"].append(
        {
            "at": datetime.now(UTC).isoformat(),
            "declaration_sha256": digest,
            "seal": seal,
            "files": len(jobs),
        }
    )
    write_json(log_path, log)


def read_day(f: p4.S0142File) -> tuple[p4.DaySummary, dict, str]:
    path = RAW / "s0142" / f.filename
    if not path.exists() and (SCHEMA_PASS / f.filename).exists():
        path = SCHEMA_PASS / f.filename  # 2026-02-17 R3, for C4 only
    with gzip.open(path, "rt", encoding="ascii") as fh:
        s = p4.summarise(fh)
    return s, p4.checks(s, expect=f), sha256_file(path)


def compute() -> None:
    sel = selection()
    days_path = EVIDENCE / "days.ndjson"
    done = (
        {json.loads(line)["file"] for line in days_path.read_text().splitlines()}
        if days_path.exists()
        else set()
    )
    summaries: dict[str, tuple[p4.DaySummary, dict]] = {}
    with days_path.open("a") as out:
        for f in wanted(sel):
            s, chk, sha = read_day(f)
            summaries[f.filename] = (s, chk)
            if f.filename in done:
                continue
            out.write(
                json.dumps(
                    {
                        "file": f.filename,
                        "sha256": sha,
                        "settlement_date": str(s.settlement_date),
                        "run": s.run,
                        "checks": chk,
                        "paid": {k: str(v) for k, v in sorted(s.supplier_cash.items())},
                        "vtp_volume": {k: str(v) for k, v in sorted(s.vtp_volume.items())},
                        "charged": {k: str(v) for k, v in sorted(s.charged.items())},
                        "supplier_volume": {
                            k: str(v) for k, v in sorted(s.supplier_volume.items())
                        },
                    }
                )
                + "\n"
            )

    def ok(f: p4.S0142File) -> bool:
        return all(v for k, v in summaries[f.filename][1].items() if k.split()[0] in DECISIVE)

    windows: dict[str, list[p4.DaySummary]] = {}
    excluded: dict[str, list[str]] = {}
    for name, chosen in sel["chosen"].items():
        windows[name] = [summaries[f.filename][0] for f in chosen.values() if ok(f)]
        excluded[name] = [f.filename for f in chosen.values() if not ok(f)]
    missing = {k: len(sel["missing"][k]) + len(excluded[k]) for k in sel["missing"]}
    decidable = {k: missing[k] <= MAX_MISSING for k in ("FEB", "PRE", "POST")}

    def against_elexon(days: list[p4.DaySummary]) -> dict:
        paid = sum((d.supplier_cash_total for d in days), Decimal(0))
        vtp = sum((d.vtp_volume_total for d in days), Decimal(0))
        return {
            "days": len(days),
            "runs": sorted({d.run for d in days}),
            "paid": paid,
            "vtp_volume": vtp,
            "paid_vs_elexon": paid / ELEXON_FEB_PAID - 1,
            "vtp_vs_elexon": vtp / ELEXON_FEB_VTP_MWH - 1,
        }

    # C4 is decided on each February day's SF run; the latest run is beside it.
    c4 = against_elexon(windows["C4"])
    c4["passes"] = (
        c4["days"] == 28
        and abs(c4["paid_vs_elexon"]) <= C4_BAND
        and abs(c4["vtp_vs_elexon"]) <= C4_BAND
    )
    c4["latest_run_beside"] = against_elexon(windows["C4-LATEST"])

    results: dict = {
        "declaration_sha256": declaration_digest(),
        "computed_at": datetime.now(UTC).isoformat(),
        "runs_read": {k: sorted({d.run for d in v}) for k, v in windows.items()},
        "missing_or_excluded": {
            "missing": {k: [str(d) for d in v] for k, v in sel["missing"].items()},
            "excluded": excluded,
        },
        "C4": c4,
    }
    publishable = c4["passes"]
    h: dict = {}
    for base in ("FEB", "PRE"):
        if decidable[base] and decidable["POST"]:
            h[f"H1-{base}"] = p4.h1_ratio(
                windows["POST"], windows[base], kill_below=KILL_H1, measure=p4.H1_MEASURE[base]
            )
            h[f"H1-{base}"]["reported"] = {
                m: p4.mean_daily(windows["POST"], m) / p4.mean_daily(windows[base], m)
                if p4.mean_daily(windows[base], m)
                else None
                for m in p4.H1_REPORTED
            }
        else:
            h[f"H1-{base}"] = {"verdict": "not decided"}
    if decidable["FEB"] and decidable["POST"]:
        h["H2-VTP"] = p4.h2_handover(
            windows["FEB"],
            windows["POST"],
            "vtp_volume",
            baseline_above=H2_BASELINE_ABOVE,
            post_below=H2_VTP_POST_BELOW,
        )
        h["H2-SUP"] = p4.h2_handover(
            windows["FEB"],
            windows["POST"],
            "supplier_cash",
            baseline_above=H2_BASELINE_ABOVE,
            post_below=H2_SUP_POST_BELOW,
        )
    else:
        h["H2-VTP"] = h["H2-SUP"] = {"verdict": "not decided"}
    # the same computation against PRE, reported with no threshold
    h2_pre = {}
    if windows["PRE"] and windows["POST"]:
        for side, attr, below in (
            ("VTP", "vtp_volume", H2_VTP_POST_BELOW),
            ("SUP", "supplier_cash", H2_SUP_POST_BELOW),
        ):
            out = p4.h2_handover(
                windows["PRE"],
                windows["POST"],
                attr,
                baseline_above=H2_BASELINE_ABOVE,
                post_below=below,
            )
            out.pop("verdict")
            h2_pre[side] = out

    restate = {}
    movements = []
    for d, runs in sel["restate"].items():
        read = [summaries[f.filename][0] for f in runs if ok(f)]
        rows = p4.restatement(read, "supplier_cash_total") if read else []
        sf = next((r["movement"] for r in rows if r["run"] == "SF"), None)
        movements.append(sf)
        restate[str(d)] = {
            "paid": rows,
            "vtp_volume": p4.restatement(read, "vtp_volume_total") if read else [],
            "sf_to_latest": sf,
        }
    h["H3"] = {
        "days": restate,
        "verdict": p4.restate_verdict(movements, above=H3_ABOVE, days=H3_DAYS),
    }
    provisional = h["H3"]["verdict"] == "holds"
    for k in ("H1-FEB", "H1-PRE", "H2-VTP", "H2-SUP"):
        if not publishable:
            h[k]["published"] = "withheld: C4 failed (F5)"
        elif provisional:
            h[k]["published"] = "provisional until POST reaches R1 (H3 holds)"
    results["hypotheses"] = h
    results["context"] = {
        # PRE follows Ofgem's 10/08 decision and may already be affected.
        "h2_against_pre": h2_pre,
        "pre_almaperj_vtp_volume": {
            "by_day": {
                str(d.settlement_date): d.vtp_volume.get(PRE_CONTEXT_PARTY, Decimal(0))
                for d in sorted(windows["PRE"], key=lambda d: d.settlement_date)
            },
            "share_of_pre": dict(
                (k, sh) for k, _, sh in p4.shares(p4.pooled(windows["PRE"], "vtp_volume"))
            ).get(PRE_CONTEXT_PARTY),
        },
        "largest": {
            name: {
                "vtp_volume": p4.shares(p4.pooled(v, "vtp_volume"))[:5],
                "paid": p4.shares(p4.pooled(v, "supplier_cash"))[:5],
                "charged": p4.shares(p4.pooled(v, "charged"))[:5],
            }
            for name, v in windows.items()
            if v and name not in ("C4", "C4-LATEST")
        },
        "series": [
            {
                "settlement_date": d.settlement_date,
                "run": d.run,
                "paid": d.supplier_cash_total,
                "charged": d.charged_total,
                "vtp_volume": d.vtp_volume_total,
                "supplier_volume": d.supplier_volume_total,
            }
            for d in sorted(windows["SERIES"], key=lambda d: d.settlement_date)
        ],
    }
    write_json(EVIDENCE / "results.json", results)
    print(json.dumps({k: v.get("verdict") for k, v in h.items()}, indent=1))
    print(f"C4: {'passes' if c4['passes'] else 'FAILS (F5)'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--seal", help="prefix (>= 8 hex) of DECLARATION.md's SHA-256")
    parser.add_argument("--phase", choices=("index", "acquire", "compute"), required=True)
    args = parser.parse_args()
    if args.phase == "index":
        index(args.seal)
    elif args.phase == "acquire":
        acquire(args.seal)
    else:
        compute()


if __name__ == "__main__":
    sys.exit(main())
