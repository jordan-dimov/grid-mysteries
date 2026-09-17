"""As-of Connection Record Certificate: build one, with its evidence bundle.

    uv run --group registers python investigations/014-gb-connection-slippage/certify.py \\
        --project "Clash Gour" --from 2021-03-31 --to 2025-07-22 [--stage 1] [--issued YYYY-MM-DD]

Writes ``certificates/<slug>/``:

- ``certificate.json``   the record (as-of states, every change, counts)
- ``CERTIFICATE.md``     the two-page certificate, a pure function of the record
- ``extracts.ndjson``    one line per copy consulted: publication date, the
                         copy's SHA-256, and the matching rows as published
- ``journal-extract.ndjson``  the archive's journal line for each copy
                         consulted (source, url, publication basis, digest)
- ``registers/``         the two full register copies in force on the dates
- ``MANIFEST.json``      the record and evidence files with SHA-256 and
                         size; its own SHA-256 is the certificate id and is
                         what gets witnessed (scripts/timestamp MANIFEST.json);
                         CERTIFICATE.md quotes that id, so it is not listed
                         (a hash cycle) and is witnessed beside it
- ``verify.py``          stdlib-only offline check of every digest

Existing bundles are never overwritten: a new certificate for the same
project and dates goes in a new directory.
"""

import argparse
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import dumps, write_json
from grid_mysteries.investigations import connection_record as cr
from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.rendering import connection_certificate as cert
from grid_mysteries.sources import tec_register as tr

HERE = Path(__file__).parent
CERTIFICATES = HERE / "certificates"
#: Both declarations the bundle is produced under: version 1 states the
#: archive's reading rules and the record's scope; version 2 adds the July
#: 2020 column aliases and the partial-export rule, which `certify.py`
#: applies (`cs.partial_exports`). Both digests go in the manifest.
DECLARATIONS = (HERE / "DECLARATION.md", HERE / "DECLARATION-v2.md")
JOURNAL = REPO_ROOT / tr.JOURNAL_PATH

VERIFY_PY = '''#!/usr/bin/env python3
"""Offline check of this evidence bundle: every file listed in MANIFEST.json
must hash to the digest recorded there; the manifest's own digest is the
certificate id, which CERTIFICATE.md must quote; the two register copies
and the as-of copies must match the journal extract. Standard library only.
Run from inside the bundle."""

import hashlib
import json
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
manifest_bytes = (here / "MANIFEST.json").read_bytes()
manifest = json.loads(manifest_bytes)
manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()
ok = True
print(f"MANIFEST.json sha256 {manifest_digest}  (this is the certificate id)")
certificate = here / "CERTIFICATE.md"
if not certificate.exists() or manifest_digest not in certificate.read_text():
    print("  !! CERTIFICATE.md does not quote this manifest's digest")
    ok = False
for entry in manifest["files"]:
    path = here / entry["path"]
    if not path.exists():
        print(f"  !! missing {entry['path']}")
        ok = False
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        ok = False
    state = "ok" if digest == entry["sha256"] else "!! DIGEST MISMATCH"
    print(f"  {state:>20} {entry['path']}")
record = json.loads((here / "certificate.json").read_text())
journal_text = (here / "journal-extract.ndjson").read_text()
journal = [json.loads(line) for line in journal_text.splitlines() if line.strip()]
by_date = {e["t_public"][:10]: e for e in journal}
for state in record["as_of"]:
    vintage = state.get("vintage")
    if vintage and by_date.get(vintage, {}).get("sha256") != state["sha256"]:
        print(f"  !! as-of copy {vintage} digest not in journal extract")
        ok = False
for entry in manifest["files"]:
    if entry["path"].startswith("registers/"):
        vintage = entry["path"].split("/", 1)[1][:10]
        if by_date.get(vintage, {}).get("sha256") != entry["sha256"]:
            print(f"  !! register copy {entry['path']} does not match the journal digest")
            ok = False
print("verify: OK" if ok else "verify: FAILED")
sys.exit(0 if ok else 1)
'''


def slug(text: str) -> str:
    return "-".join(tr.normalise(text).split())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="the register's project name")
    parser.add_argument("--stage", default=None)
    parser.add_argument("--from", dest="start", required=True, type=date.fromisoformat)
    parser.add_argument("--to", dest="end", required=True, type=date.fromisoformat)
    parser.add_argument("--issued", default=date.today().isoformat())
    args = parser.parse_args(argv)

    journal = {e["path"]: e for e in tr.one_per_date(tr.read_journal(JOURNAL))}
    parsed, _skipped = tr.load_vintages(JOURNAL, REPO_ROOT)
    vintages = [(t, rows, entry["sha256"], entry["path"]) for t, rows, entry in parsed]
    suspect = {
        s.t_public: s.note for s in cs.partial_exports([(t, len(rows)) for t, rows, _e in parsed])
    }
    observations = cr.track(vintages, args.project, args.stage, suspect=suspect)
    record = cr.record(observations, args.project, args.stage, (args.start, args.end))
    if any(s.get("vintage") is None for s in record["as_of"]):
        raise SystemExit("no register copy on or before one of the dates; nothing to certify")

    name = f"{slug(args.project)}-{args.start}-{args.end}"
    bundle_dir = CERTIFICATES / name
    if bundle_dir.exists():
        raise SystemExit(f"{bundle_dir} exists; a bundle is never overwritten")
    (bundle_dir / "registers").mkdir(parents=True)

    write_json(bundle_dir / "certificate.json", record)
    first, last = (cr.as_of(observations, d) for d in (args.start, args.end))
    assert first is not None and last is not None
    consulted = [o for o in observations if first.t_public <= o.t_public <= last.t_public]
    with (bundle_dir / "extracts.ndjson").open("w") as out:
        for o in consulted:
            out.write(
                dumps(
                    {
                        "t_public": o.t_public,
                        "sha256": o.sha256,
                        "path": o.path,
                        "rows": [
                            {label: cr.shown(r.get(col), kind) for label, col, kind in cr.FIELDS}
                            for r in o.rows
                        ],
                    }
                ).replace("\n", " ")
                + "\n"
            )
    with (bundle_dir / "journal-extract.ndjson").open("w") as out:
        for o in consulted:
            out.write(json.dumps(journal[o.path]) + "\n")
    for o in (first, last):
        source = REPO_ROOT / o.path
        target = bundle_dir / "registers" / source.name
        shutil.copyfile(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != o.sha256:
            raise SystemExit(f"copied register {source} does not hash as journalled")

    # The manifest lists the record and the evidence; the certificate text is
    # derived from them and quotes the manifest's digest, so it cannot itself
    # be listed (that would be a hash cycle). It is witnessed separately.
    listing = []
    for path in sorted(p for p in bundle_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(bundle_dir).as_posix()
        if rel in ("MANIFEST.json", "CERTIFICATE.md", "verify.py") or rel.startswith(
            ("MANIFEST.json.", "CERTIFICATE.md.")
        ):
            continue
        data = path.read_bytes()
        listing.append(
            {"path": rel, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        )
    declarations = [
        {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in DECLARATIONS
    ]
    declaration_sha256 = declarations[0]["sha256"]
    manifest = {
        "bundle": name,
        "issued": args.issued,
        "issuer": cert.ISSUER,
        "project": args.project,
        "stage": args.stage,
        "dates": [args.start.isoformat(), args.end.isoformat()],
        "declaration_sha256": declaration_sha256,
        "declarations": declarations,
        "rule": (
            "the certificate id is the SHA-256 of this file's bytes; every listed file hashes "
            "as recorded; CERTIFICATE.md is rendered from certificate.json and this file, "
            "quotes the certificate id, and is witnessed beside it"
        ),
        "files": listing,
    }
    manifest_text = dumps(manifest) + "\n"
    (bundle_dir / "MANIFEST.json").write_text(manifest_text)
    digest = hashlib.sha256(manifest_text.encode()).hexdigest()
    bundle_meta = {
        "issued": args.issued,
        "certificate_id": digest,
        "manifest_sha256": digest,
        "files": len(listing),
        "declaration_sha256": declaration_sha256,
        "declarations": declarations,
        "proofs": [],
    }
    (bundle_dir / "CERTIFICATE.md").write_text(cert.render_certificate(record, bundle_meta))
    (bundle_dir / "verify.py").write_text(VERIFY_PY)
    print(f"certificate {name}: id {digest}")
    print(
        f"  {len(consulted)} copies consulted, {len(record['changes'])} changes, "
        f"{len(listing)} files"
    )
    rel = bundle_dir.relative_to(REPO_ROOT)
    print(
        f"  stamp with: scripts/timestamp {rel}/MANIFEST.json "
        f"&& scripts/timestamp {rel}/CERTIFICATE.md"
    )


if __name__ == "__main__":
    sys.exit(main())
