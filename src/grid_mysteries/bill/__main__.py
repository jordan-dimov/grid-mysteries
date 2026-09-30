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
import sys
from pathlib import Path
from typing import Final

from grid_mysteries import record
from grid_mysteries.bill import importer
from grid_mysteries.corpus import REPO_ROOT

RECORD: Final = importer.RECORD
TRACKER: Final = REPO_ROOT / "investigations/013-the-cover-price-tracker/evidence/tracker.json"
url = RECORD.url


def cmd_register_key(args: argparse.Namespace) -> None:
    api = RECORD.client(REPO_ROOT, url())
    if api.claims_named("AuditSigningKey"):
        print("a signing key is already registered; nothing to do")
        return
    public = RECORD.public_key.read_text().strip()
    result = api.transact(
        [importer.act("register_audit_signing_key", key_id=RECORD.key_id, public_key=public)]
    )
    outcome = record.classify(result, None)
    if outcome.status != "committed":
        raise SystemExit(f"register-key: {outcome.status} ({outcome.detail})")
    print(f"registered {RECORD.key_id} ({public[:24]}…) in {outcome.transition_ids[-1]}")


def cmd_import(args: argparse.Namespace) -> None:
    tracker = Path(args.tracker) if args.tracker else TRACKER
    try:
        line = importer.run(REPO_ROOT, url(), tracker)
    except record.ImportError_ as exc:
        raise SystemExit(f"import: {exc}") from None
    print(
        f"import: {line['run']} recorded; {len(line['days_added'])} day(s) added, "
        f"{line['days_unchanged']} unchanged, {line['outcomes']} outcome(s), "
        f"{line['outcome_revisions']} outcome revision(s), {line['bsad_revisions']} BSAD "
        f"revision(s), {line['bsad_confirmed']} confirmed, {line['verdicts']} verdict(s); "
        "run `checkpoint --witness` next"
    )


def cmd_checkpoint(args: argparse.Namespace) -> None:
    _, _, pack = record.checkpoint_and_export(RECORD, url(), witness=args.witness)
    print(f"pack {pack.relative_to(REPO_ROOT)} verified against the anchor with {RECORD.key_id}")


def cmd_verify(args: argparse.Namespace) -> None:
    proc = record.run(
        "audit", "verify", "--database-url", url(), "--trusted-tsa-file", str(record.DIGICERT_ROOT)
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
