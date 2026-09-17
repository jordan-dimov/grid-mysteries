#!/usr/bin/env python3
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
