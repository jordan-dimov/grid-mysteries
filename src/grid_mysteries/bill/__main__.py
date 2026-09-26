"""Command line for the Balancing Bill record (`python -m grid_mysteries.bill`).

    register-key   admit the pinned signing key's AuditSigningKey claim, once
    import         record the tracker's current compute run (one transact)
    checkpoint     sign a checkpoint (DigiCert countersigns with --witness),
                   keep the anchor under bill/anchors/, export and verify the pack
    verify         `audit verify` with the DigiCert root

The record lives in its own database (`BILL_DATABASE_URL`, default
`postgres:///grid_mysteries_bill`), never the research record's. Nothing
here runs on Render: the tracker-013 job proposes nothing; the laptop
records after it computes.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Final

from grid_mysteries.bill import importer
from grid_mysteries.corpus import REPO_ROOT

DEFAULT_URL: Final = "postgres:///grid_mysteries_bill"
PROGRAMME: Final = REPO_ROOT / importer.PROGRAMME
TRACKER: Final = REPO_ROOT / "investigations/013-the-cover-price-tracker/evidence/tracker.json"
ANCHORS: Final = REPO_ROOT / "bill" / "anchors"
PACKS: Final = REPO_ROOT / "data" / "derived" / "bill" / "packs"
PUBLIC_KEY: Final = REPO_ROOT / "bill" / "trust" / "bill-2026.pub"
KEY_ID: Final = "bill-2026"
SIGNING_KEY: Final = Path(
    os.environ.get(
        "BILL_SIGNING_KEY", str(Path.home() / ".config/grid-mysteries/bill-signing-2026.pem")
    )
)
DIGICERT: Final = "rfc3161:http://timestamp.digicert.com"
DIGICERT_ROOT: Final = REPO_ROOT / "trust" / "tsa" / "digicert-trusted-root-g4.pem"


def url() -> str:
    return os.environ.get("BILL_DATABASE_URL", DEFAULT_URL)


def morpholog(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["morpholog", *args], capture_output=True, text=True)


def cmd_register_key(args: argparse.Namespace) -> None:
    from morpholog_client.adapter import Morpholog

    api = Morpholog(str(PROGRAMME), url())
    if api.claims_named("AuditSigningKey"):
        print("a signing key is already registered; nothing to do")
        return
    public = PUBLIC_KEY.read_text().strip()
    result = api.transact(
        [importer.act("register_audit_signing_key", key_id=KEY_ID, public_key=public)]
    )
    outcome = importer.classify(result, None)
    if outcome.status != "committed":
        raise SystemExit(f"register-key: {outcome.status} ({outcome.detail})")
    print(f"registered {KEY_ID} ({public[:24]}…) in {outcome.transition_ids[-1]}")


def cmd_import(args: argparse.Namespace) -> None:
    tracker = Path(args.tracker) if args.tracker else TRACKER
    try:
        line = importer.run(REPO_ROOT, url(), tracker)
    except importer.ImportError_ as exc:
        raise SystemExit(f"import: {exc}") from None
    print(
        f"import: {line['run']} recorded; {len(line['days_added'])} day(s) added, "
        f"{line['days_unchanged']} unchanged, {line['outcomes']} outcome(s), "
        f"{line['outcome_revisions']} outcome revision(s), {line['bsad_revisions']} BSAD "
        f"revision(s), {line['bsad_confirmed']} confirmed, {line['verdicts']} verdict(s); "
        "run `checkpoint --witness` next"
    )


def verify_command(pack: Path, anchor: Path) -> list[str]:
    return [
        "morpholog",
        "audit",
        "verify-pack",
        str(pack),
        "--anchor-file",
        str(anchor),
        "--require-signing-key",
        str(PUBLIC_KEY),
        "--trusted-tsa-file",
        str(DIGICERT_ROOT),
    ]


def exported_pack(anchor_path: Path, anchor: dict[str, Any]) -> Path:
    """The complete pack at the anchor's tree size (NDJSON, Morpholog pack
    format 4), exported once and verified offline against the anchor with
    the pinned key."""
    tree = anchor["tree_size"]
    pack = PACKS / f"tree-{tree}.ndjson"
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
    result = subprocess.run(verify_command(pack, anchor_path), capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"the pack does not verify against {anchor_path.name}:\n{result.stdout}")
    return pack


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
    proc = morpholog(*argv)
    if not proc.stdout.strip():
        raise SystemExit(f"checkpoint failed:\n{proc.stderr}")
    anchor = json.loads(proc.stdout)
    path = ANCHORS / f"tree-{anchor['tree_size']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or "witnesses" in anchor:
        path.write_text(proc.stdout if proc.stdout.endswith("\n") else proc.stdout + "\n")
    print(f"anchor {path.relative_to(REPO_ROOT)} ({anchor.get('status', 'witnessed')})")
    if proc.returncode != 0:
        raise SystemExit(
            "a timestamp authority failed; the checkpoint is recorded. Retry with\n"
            f"  morpholog audit witness --database-url {url()} --tree-size {anchor['tree_size']} "
            f"--witness {DIGICERT} > {path.relative_to(REPO_ROOT)}"
        )
    pack = exported_pack(path, json.loads(path.read_text()))
    print(f"pack {pack.relative_to(REPO_ROOT)} verified against the anchor with {KEY_ID}")


def cmd_verify(args: argparse.Namespace) -> None:
    proc = morpholog(
        "audit", "verify", "--database-url", url(), "--trusted-tsa-file", str(DIGICERT_ROOT)
    )
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m grid_mysteries.bill")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("register-key")
    imp = commands.add_parser("import")
    imp.add_argument("--tracker", default=None, help="a tracker.json other than 013's")
    cp = commands.add_parser("checkpoint")
    cp.add_argument("--witness", action="store_true", help="DigiCert countersigns the head")
    commands.add_parser("verify")
    args = parser.parse_args(argv)
    {
        "register-key": cmd_register_key,
        "import": cmd_import,
        "checkpoint": cmd_checkpoint,
        "verify": cmd_verify,
    }[args.command](args)


if __name__ == "__main__":
    main()
