"""The project's small operational CLI: toolchain state, digests, capture.

Deliberately stdlib-only at import time. Every artefact digest the research
record relies on is computed by `grid_mysteries.hashing`, not here; the
capture commands import the capture package only when invoked, so the CLI
stays usable without boto3 or httpx installed.
"""

import argparse
import os
import platform
import shutil
import sys
from datetime import UTC, date, datetime
from pathlib import Path

from grid_mysteries.hashing import sha256_file


def doctor() -> None:
    """Show the local research-toolchain state."""
    print(f"python={platform.python_version()}")
    print(f"python_ok={sys.version_info >= (3, 14)}")
    print(f"morpholog={shutil.which('morpholog') or 'not found'}")


def app(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="grid-mysteries", description="Research Britain's electricity mysteries."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Show the local research-toolchain state.")
    digest = commands.add_parser("hash-source", help="Print a source artefact's SHA-256 digest.")
    digest.add_argument("path", type=Path)
    capture = commands.add_parser("capture", help="The unattended vintage capture job.")
    capture_commands = capture.add_subparsers(dest="capture_command", required=True)
    capture_commands.add_parser("plan", help="List the resources the plan captures, and TO_ADD.")
    run = capture_commands.add_parser("run", help="Capture every planned resource for one day.")
    run.add_argument("--day", default=None, help="UTC day (default today)")
    run.add_argument(
        "--store",
        default=os.environ.get("VINTAGE_STORE", ""),
        help="s3://bucket or a local directory (env VINTAGE_STORE)",
    )
    run.add_argument("--only", action="append", default=[], help="resource name (repeatable)")
    run.add_argument(
        "--healthcheck",
        default=os.environ.get("HEALTHCHECK_URL_CAPTURE", ""),
        help="healthchecks.io ping URL (env HEALTHCHECK_URL_CAPTURE)",
    )

    args = parser.parse_args(argv)
    if args.command == "doctor":
        doctor()
    elif args.command == "capture":
        capture_command(args)
    else:
        print(sha256_file(args.path))


def capture_command(args: argparse.Namespace) -> None:
    from grid_mysteries.capture.plan import PLAN, TO_ADD

    if args.capture_command == "plan":
        for resource in PLAN:
            print(
                f"{resource.name:36s} {resource.strategy:12s} {resource.source}/{resource.resource}"
            )
        for name, note in TO_ADD:
            print(f"TO ADD: {name}: {note}")
        return
    if not args.store:
        raise SystemExit("capture run: --store or VINTAGE_STORE is required")
    from grid_mysteries.capture.fetch import HttpFetcher
    from grid_mysteries.capture.run import healthcheck_pinger, run_capture
    from grid_mysteries.capture.store import store_from_url

    day = date.fromisoformat(args.day) if args.day else datetime.now(UTC).date()
    plan = [r for r in PLAN if not args.only or r.name in args.only]
    fetcher = HttpFetcher()
    status = run_capture(
        plan,
        fetcher,
        store_from_url(args.store),
        day=day,
        ping=healthcheck_pinger(fetcher, args.healthcheck or None),
    )
    for r in status.resources:
        print(
            f"{r.name:36s} {r.artefacts:5d} artefacts {r.bytes:11,d} bytes"
            + (f"  ERROR {r.error}" if r.error else "")
        )
    print(f"{'ok' if status.ok else 'FAILED'}: manifest {status.manifest_key}")
    if not status.ok:
        sys.exit(1)


if __name__ == "__main__":
    app()
