"""The TEC record engine, run by hand on the laptop.

    uv run --group registers python -m grid_mysteries.tec import [--until YYYY-MM-DD]
    uv run python -m grid_mysteries.tec checkpoint [--witness]
    uv run python -m grid_mysteries.tec analyse
    uv run --group registers python -m grid_mysteries.tec certify --project NAME \\
        [--stage S] --on YYYY-MM-DD [--on YYYY-MM-DD ...]

The record lives in its own database (`TEC_DATABASE_URL`, default
`postgres:///grid_mysteries_tec`), never in the research record's. Imports
run after the watchdog has synced the capture archive; nothing here runs
on Render, and nothing here writes to any other Morpholog database.

`checkpoint` signs the record's tree head with the `tec-2026` key; with
`--witness` DigiCert's RFC 3161 authority countersigns it (only the hash
leaves the machine). `analyse` reads the record back through its audit log
up to the latest anchor and writes every analysis claim under
`tec/analysis/`, each naming its rule and the anchor it read. `certify`
builds a bundle under `data/derived/tec/certificates/`.
"""

import argparse
import gzip
import hashlib
import json
import os
import pickle
import shutil
import subprocess
import sys
import time
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Final

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import dumps, write_json
from grid_mysteries.tec import analysis, certificate, importer, replay, sources

DEFAULT_URL: Final = "postgres:///grid_mysteries_tec"
PROGRAMME: Final = REPO_ROOT / importer.PROGRAMME
ANCHORS: Final = REPO_ROOT / "tec" / "anchors"
ANALYSIS: Final = REPO_ROOT / "tec" / "analysis"
DERIVED: Final = REPO_ROOT / "data" / "derived" / "tec"
PUBLIC_KEY: Final = REPO_ROOT / "tec" / "trust" / "tec-2026.pub"
KEY_ID: Final = "tec-2026"
SIGNING_KEY: Final = Path(
    os.environ.get(
        "TEC_SIGNING_KEY", str(Path.home() / ".config/grid-mysteries/tec-signing-2026.pem")
    )
)
DIGICERT: Final = "rfc3161:http://timestamp.digicert.com"
DIGICERT_ROOT: Final = REPO_ROOT / "trust" / "tsa" / "digicert-trusted-root-g4.pem"
COMMITTED_014: Final = (
    REPO_ROOT / "investigations/014-gb-connection-slippage/evidence/v2/rows.ndjson"
)


def url() -> str:
    return os.environ.get("TEC_DATABASE_URL", DEFAULT_URL)


def morpholog(*args: str) -> str:
    return subprocess.run(["morpholog", *args], check=True, capture_output=True, text=True).stdout


def latest_anchor() -> tuple[Path, dict[str, Any]]:
    anchors = sorted(ANCHORS.glob("tree-*.json"), key=lambda p: int(p.stem.split("-")[1]))
    if not anchors:
        raise SystemExit("no anchor yet: run `checkpoint` first")
    return anchors[-1], json.loads(anchors[-1].read_text())


# ------------------------------------------------------------------ commands


def cmd_import(args: argparse.Namespace) -> None:
    until = date.fromisoformat(args.until) if args.until else None
    started = time.monotonic()
    try:
        done = importer.run(
            REPO_ROOT, url(), until=until, limit=args.limit, accept_stranded=args.accept_stranded
        )
    except importer.ImportError_ as exc:
        raise SystemExit(f"import: {exc}") from None
    acts = sum(d["acts"] for d in done)
    print(
        f"import: {len(done)} publication(s), {acts} acts, {time.monotonic() - started:.0f} s; "
        "run `checkpoint` next"
    )


def cmd_checkpoint(args: argparse.Namespace) -> None:
    argv = [
        "audit",
        "checkpoint",
        "--database-url",
        url(),
        "--signing-key",
        str(SIGNING_KEY),
        "--key-id",
        KEY_ID,
    ]
    if args.witness:
        argv += ["--witness", DIGICERT]
    proc = subprocess.run(["morpholog", *argv], capture_output=True, text=True)
    if not proc.stdout.strip():
        raise SystemExit(f"checkpoint failed:\n{proc.stderr}")
    anchor = json.loads(proc.stdout)
    path = ANCHORS / f"tree-{anchor['tree_size']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or "witnesses" in anchor:
        path.write_text(proc.stdout if proc.stdout.endswith("\n") else proc.stdout + "\n")
    print(f"anchor {path.relative_to(REPO_ROOT)} ({anchor.get('status', 'witnessed')})")
    if proc.returncode == 0:
        # The complete pack belongs to the checkpoint: export, verify, compress
        # and fold it once here, so every certificate starts from it.
        started = time.monotonic()
        pack = exported_pack(path, json.loads(path.read_text()))
        compressed(pack)
        publications_from(pack)
        print(f"pack {pack.relative_to(REPO_ROOT)} ready in {time.monotonic() - started:.0f} s")
    if proc.returncode != 0:
        raise SystemExit(
            "a timestamp authority failed; the checkpoint is recorded. Retry with\n"
            f"  morpholog audit witness --database-url {url()} --tree-size {anchor['tree_size']} "
            f"--witness {DIGICERT} > {path.relative_to(REPO_ROOT)}"
        )


def verify_command(pack: str, anchor: str, key: str, tsa: str) -> list[str]:
    return [
        "morpholog",
        "audit",
        "verify-pack",
        pack,
        "--anchor-file",
        anchor,
        "--require-signing-key",
        key,
        "--trusted-tsa-file",
        tsa,
    ]


def exported_pack(anchor_path: Path, anchor: dict[str, Any]) -> Path:
    """The complete pack at the anchor's tree size, exported once, verified
    offline against the anchor with the pinned key, and kept."""
    tree = anchor["tree_size"]
    pack = DERIVED / "packs" / f"tree-{tree}.ndjson"
    # Morpholog up to v0.0.11 exported one JSON document; a pack exported
    # then is kept as it is (it still verifies) rather than re-exported.
    legacy = pack.with_suffix(".json")
    if legacy.exists() and not pack.exists():
        pack = legacy
    if not pack.exists():
        pack.parent.mkdir(parents=True, exist_ok=True)
        tmp = pack.with_suffix(".tmp")
        with tmp.open("w") as out:
            subprocess.run(
                ["morpholog", "audit", "export", "--database-url", url(), "--tree-size", str(tree)],
                check=True,
                stdout=out,
            )
        tmp.rename(pack)
    result = subprocess.run(
        verify_command(str(pack), str(anchor_path), str(PUBLIC_KEY), str(DIGICERT_ROOT)),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"the pack does not verify against {anchor_path.name}:\n{result.stdout}")
    return pack


def cmd_analyse(args: argparse.Namespace) -> None:
    anchor_path, anchor = latest_anchor()
    record_ref = {
        "database": url().rsplit("/", 1)[-1],
        "anchor": str(anchor_path.relative_to(REPO_ROOT)),
        "tree_size": anchor["tree_size"],
        "root_hash": anchor["root_hash"],
        "checkpoint_hash": anchor["checkpoint_hash"],
    }
    started = time.monotonic()
    publications = list(replay.fold(replay.stream_audit(url(), limit=anchor["tree_size"])))
    print(
        f"analyse: {len(publications)} publications from the record "
        f"in {time.monotonic() - started:.0f} s"
    )
    paths = {c.sha256: str(c.path.relative_to(REPO_ROOT)) for c in sources.copies(REPO_ROOT)}
    committed = [x for x in COMMITTED_014.read_text().splitlines() if x.strip()]
    last_014 = max(date.fromisoformat(json.loads(x)["t_public"]) for x in committed)
    seen_by_014 = [p for p in publications if p.published_on <= last_014]

    usable, excluded = analysis.inputs(seen_by_014, paths)
    result = analysis.series_014(usable)
    diff = analysis.differential(analysis.row_lines(result), committed)
    write_json(
        ANALYSIS / "differential-014.json",
        {
            "rule": analysis.RULE_014,
            "record": record_ref,
            "against": str(COMMITTED_014.relative_to(REPO_ROOT)),
            "publications_to": last_014,
            "excluded_by_reading_rule_2": excluded,
            **diff,
        },
    )
    print(
        f"differential 014-v2: {diff['identical']}/{diff['compared']} identical, "
        f"{len(diff['differing'])} differing, missing {diff['missing_from_engine']}, "
        f"extra {diff['extra_in_engine']}"
    )

    sequence = analysis.kept(usable, result)
    by_014 = analysis.entries_014(sequence)
    by_content = analysis.entries_content(sequence)
    flaps = [
        # The spike compared every copy with the next, across the regime
        # break; its reproduction keeps that single sequence.
        analysis.flapping([analysis.entries_spike(seen_by_014)], analysis.RULE_SPIKE),
        analysis.flapping(analysis.by_segment(by_014), analysis.RULE_014),
        analysis.flapping(analysis.by_segment(by_content), analysis.RULE_CONTENT),
    ]
    write_json(ANALYSIS / "flapping.json", {"record": record_ref, "rules": flaps})
    for f in flaps:
        print(
            f"flapping {f['rule']}: {f['moves']} moves, "
            f"{f['reversed_by_next']} reversed by the next "
            f"({f['reversed_file_backed']} shown by the files, {f['reversed_not_in_files']} not; "
            f"{f['reversed_not_in_files_on_repeated_keys']} of those on repeated keys)"
        )
    content_series = analysis.series_by(by_content)
    reproduced = analysis.series_by(by_014)
    write_json(
        ANALYSIS / "series-content-v1.json",
        {
            "rule": analysis.RULE_CONTENT,
            "reading": analysis.RULE_014,
            "record": record_ref,
            "publications_to": last_014,
            "comparison_with_014_v2": analysis.compare_series(reproduced, content_series),
            "headline_difference": analysis.headline_difference(
                by_014,
                by_content,
                reproduced["headline"]["baseline"],
                reproduced["headline"]["t_public"],
            ),
            "chain_difference": analysis.chain_difference(by_014, by_content),
            "propositions": content_series["propositions"],
        },
    )
    print(f"content-v1 headline: {content_series['headline']}")
    print(f"014-v2 headline (through series_by): {reproduced['headline']}")


def provenance_map() -> dict[str, dict[str, Any]]:
    return {c.sha256: c.provenance for c in sources.copies(REPO_ROOT)}


def slug(project: str, stage: str | None, dates: list[date]) -> str:
    base = "-".join(project.lower().split())
    base = "".join(ch for ch in base if ch.isalnum() or ch == "-")
    stage_part = f"-stage-{stage}" if stage else ""
    return f"{base}{stage_part}-" + "-".join(d.isoformat() for d in dates)


def render(cert: dict[str, Any], anchor: dict[str, Any], issued: str, pack_name: str) -> str:
    out = [
        f"# TEC register record: {cert['project']}"
        + (f", stage {cert['stage']}" if cert["stage"] else ""),
        "",
        f"Issued {issued} from the governed TEC record (Morpholog programme "
        f"`tec_register`, {cert['publications_in_record']} publications), checkpoint at tree "
        f"size {anchor['tree_size']}, root `{anchor['root_hash']}`, signed with key `tec-2026`.",
        "",
        "This is what NESO's TEC register printed about the project, as of each date: the rows",
        "exactly as published, from the latest publication the record holds on or before",
        "that date. The archive has gaps; where the publication relied on is more than",
        f"{certificate.GAP_DAYS} days older than the date, or a copy held for the interval is not",
        "in the record, the entry says so. It is not a forecast and says nothing about",
        "entitlement.",
        "Rows are matched by the register's normalised project name"
        + (" and stage." if cert["stage"] else "."),
        "",
    ]
    for a in cert["as_of"]:
        out.append(f"## As of {a['as_of']}")
        out.append("")
        if a.get("publication") is None:
            out += [a.get("note", ""), ""]
            continue
        prov = a.get("provenance") or {}
        journal = prov.get("journal") or {}
        capture = prov.get("capture") or {}
        source = journal.get("url") or capture.get("url", "")
        basis = journal.get("t_public_basis") or (
            f"captured {capture.get('fetched_at')} by the vintage capture job" if capture else ""
        )
        out += [
            f"Publication of **{a['published_on']}** ({a['file_format']}), "
            f"SHA-256 `{a['sha256']}`.",
            f"Source: {source.split('?')[0]}  ",
            f"Dated by: {basis}  ",
            f"Record transition closing its import: `{a['close_transition']}`  ",
            f"Published {a['days_before']} day(s) before the date asked about"
            + (f" (**a gap of more than {certificate.GAP_DAYS} days**)." if a["gap"] else "."),
            "",
            f"**{a['state']}**",
            "",
        ]
        for u in a["held_but_not_in_record"]:
            out.append(
                f"A copy published {u['published_on']} (`{u['sha256'][:12]}…`) is held but is not "
                "in the record (it does not parse); what it printed is not stated here."
            )
            out.append("")
        for ln in a["lines"]:
            out.append(f"Line {ln['line']} (record key `{ln['row']}`, kinds `{ln['kinds']}`):")
            out.append("")
            out.append("| Column | As published |")
            out.append("|---|---|")
            for column, value in ln["cells"].items():
                if value != "":
                    out.append(f"| {column} | {value} |")
            out.append("")
    out.append("## Publications between the dates in which the project's lines changed")
    out.append("")
    if not cert["changes"]:
        out.append("None.")
    for c in cert["changes"]:
        out.append(
            f"- {c['published_on']} (`{c['sha256'][:12]}…`): {len(c['printed'])} line(s) printed, "
            f"{len(c['no_longer_printed'])} no longer printed"
        )
    out += [
        "",
        "## Verify it yourself",
        "",
        "```bash",
        f"gunzip -k {pack_name}.gz",
        f"morpholog audit verify-pack {pack_name} --anchor-file anchor.json \\",
        "  --require-signing-key tec-2026.pub --trusted-tsa-file digicert-trusted-root-g4.pem",
        f"python3 lines_from_pack.py {pack_name} certificate.json",
        "```",
        "",
        "The first command checks, with no database, that the pack is the complete record up",
        "to the anchor and that the anchor is signed by the pinned `tec-2026` key (and",
        "witnessed by DigiCert where the anchor carries a witness). The second re-derives the",
        "lines above from the pack alone. `MANIFEST.json` lists every file's SHA-256.",
        "",
    ]
    return "\n".join(out)


def compressed(pack: Path) -> Path:
    gz = pack.with_name(pack.name + ".gz")
    if not gz.exists() or gz.stat().st_mtime < pack.stat().st_mtime:
        with pack.open("rb") as src, gzip.open(gz, "wb", compresslevel=6) as dst:
            shutil.copyfileobj(src, dst)
    return gz


def publications_from(pack: Path) -> list[replay.Publication]:
    """The record's publications folded from a verified pack, cached beside
    it (a local convenience; the pack is the authority and is re-verified
    by every certificate that ships it)."""
    cache = pack.with_suffix(".publications.pickle")
    if cache.exists() and cache.stat().st_mtime >= pack.stat().st_mtime:
        with cache.open("rb") as handle:
            return list(pickle.load(handle))
    publications = list(replay.fold(replay.pack_rows(pack)))
    with cache.open("wb") as handle:
        pickle.dump(publications, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return publications


def cmd_certify(args: argparse.Namespace) -> None:
    started = time.monotonic()
    dates = [date.fromisoformat(d) for d in args.on]
    anchor_path, anchor = latest_anchor()
    pack = exported_pack(anchor_path, anchor)
    t_pack = time.monotonic() - started
    publications = publications_from(pack)
    in_record = {p.sha256 for p in publications}
    not_in_record = [
        (c.published_on, c.sha256) for c in sources.copies(REPO_ROOT) if c.sha256 not in in_record
    ]
    cert = certificate.record(
        publications, args.project, args.stage, dates, provenance_map(), not_in_record
    )
    # The runtime's own as-of read must agree with the pack.
    for a in cert["as_of"]:
        if not a.get("close_transition"):
            continue
        claims = json.loads(
            morpholog(
                "inspect",
                "claims",
                "--database-url",
                url(),
                "--predicate",
                "Row",
                "--as-of",
                a["close_transition"],
                "--named",
                str(PROGRAMME),
            )
        )
        runtime = sorted(
            c["args"]["row"]
            for c in claims
            if certificate.matches(
                {"Project Name": c["args"]["project_name"], "Stage": c["args"]["stage"]},
                args.project,
                args.stage,
            )
        )
        stated = sorted(line["row"] for line in a["lines"])
        if runtime != stated:
            raise SystemExit(f"as of {a['as_of']}: the runtime read and the pack disagree")
        a["runtime_as_of_read_agrees"] = True
    issued = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    out = DERIVED / "certificates" / slug(args.project, args.stage, dates)
    if out.exists():
        raise SystemExit(f"{out} exists; certificates are never overwritten")
    out.mkdir(parents=True)
    cert["issued"] = issued
    cert["anchor"] = {k: anchor[k] for k in ("tree_size", "root_hash", "checkpoint_hash")}
    write_json(out / "certificate.json", cert)
    (out / "CERTIFICATE.md").write_text(render(cert, anchor, issued, f"pack{pack.suffix}"))
    shutil.copyfile(anchor_path, out / "anchor.json")
    shutil.copyfile(PUBLIC_KEY, out / "tec-2026.pub")
    shutil.copyfile(DIGICERT_ROOT, out / "digicert-trusted-root-g4.pem")
    (out / "lines_from_pack.py").write_text(certificate.LINES_FROM_PACK)
    shutil.copyfile(compressed(pack), out / f"pack{pack.suffix}.gz")
    files = sorted(p for p in out.iterdir() if p.name != "MANIFEST.json")
    manifest = {
        "certificate": out.name,
        "issued": issued,
        "files": [
            {
                "path": p.name,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "bytes": p.stat().st_size,
            }
            for p in files
        ],
    }
    (out / "MANIFEST.json").write_text(dumps(manifest) + "\n")
    # Check the bundle the way a stranger would, from inside it.
    check = subprocess.run(
        [sys.executable, "lines_from_pack.py", str(pack), "certificate.json"],
        cwd=out,
        capture_output=True,
        text=True,
    )
    if check.returncode != 0:
        raise SystemExit(f"lines_from_pack.py disagrees with the certificate:\n{check.stdout}")
    print(check.stdout.strip())
    print(
        f"certificate {out.relative_to(REPO_ROOT)}: pack ready in {t_pack:.1f} s, "
        f"done in {time.monotonic() - started:.1f} s"
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m grid_mysteries.tec")
    commands = parser.add_subparsers(dest="command", required=True)
    imp = commands.add_parser("import")
    imp.add_argument("--until", default=None)
    imp.add_argument("--limit", type=int, default=None)
    imp.add_argument(
        "--accept-stranded",
        action="store_true",
        help="import newer copies although older readable ones are missing from the record",
    )
    cp = commands.add_parser("checkpoint")
    cp.add_argument("--witness", action="store_true", help="DigiCert countersigns the head")
    commands.add_parser("analyse")
    cert = commands.add_parser("certify")
    cert.add_argument("--project", required=True)
    cert.add_argument("--stage", default=None)
    cert.add_argument("--on", action="append", required=True)
    args = parser.parse_args(argv)
    {
        "import": cmd_import,
        "checkpoint": cmd_checkpoint,
        "analyse": cmd_analyse,
        "certify": cmd_certify,
    }[args.command](args)


if __name__ == "__main__":
    main()
