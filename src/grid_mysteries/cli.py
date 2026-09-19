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
        "--no-witness", action="store_true", help="skip the manifest timestamping step"
    )
    for name, help_text in (
        ("pull-state", "Download an instrument's state from the archive into the repository."),
        ("push-state", "Upload an instrument's pinned artefacts and journals to the archive."),
    ):
        sub = capture_commands.add_parser(name, help=help_text)
        sub.add_argument("--store", default=os.environ.get("VINTAGE_STORE", ""))
        sub.add_argument("--name", required=True, help="instrument name, e.g. 013")
        sub.add_argument("--repo-root", default=".", type=Path)
        sub.add_argument("--path", action="append", default=[], type=Path, help="repo-relative")
        sub.add_argument(
            "--include", action="append", default=[], help="file-name glob (push only, repeatable)"
        )
        sub.add_argument(
            "--overwrite",
            action="store_true",
            help="pull only: the archive wins for a file that differs (the unattended job, "
            "whose working copy is the image's build-time snapshot); never on the laptop",
        )
    check = capture_commands.add_parser("check", help="The watchdog: five checks and a sync.")
    check.add_argument("--store", default=os.environ.get("VINTAGE_STORE", ""))
    check.add_argument("--repo-root", default=".", type=Path)
    check.add_argument("--include-bytes", action="store_true", help="also mirror raw/ locally")
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
        raise SystemExit("capture: --store or VINTAGE_STORE is required")
    if args.capture_command == "check":
        watchdog_command(args)
        return
    if args.capture_command in ("pull-state", "push-state"):
        state_command(args)
        return
    from grid_mysteries.capture.fetch import HttpFetcher
    from grid_mysteries.capture.run import healthcheck_pinger, run_capture
    from grid_mysteries.capture.store import store_from_url

    day = date.fromisoformat(args.day) if args.day else datetime.now(UTC).date()
    plan = [r for r in PLAN if not args.only or r.name in args.only]
    fetcher = HttpFetcher()
    witness = None
    if not args.no_witness:
        import tempfile

        from grid_mysteries.capture.timestamp import witness as witness_fn

        workdir = Path(tempfile.mkdtemp(prefix="vintage-proofs-"))

        def witness(data: bytes, name: str) -> dict[str, bytes]:
            return witness_fn(data, name, workdir, fetcher=fetcher)

    status = run_capture(
        plan,
        fetcher,
        store_from_url(args.store),
        day=day,
        ping=healthcheck_pinger(fetcher, args.healthcheck or None),
        witness=witness,
    )
    for r in status.resources:
        print(
            f"{r.name:36s} {r.artefacts:5d} artefacts {r.bytes:11,d} bytes"
            + (f"  ERROR {r.error}" if r.error else "")
        )
    if status.store_error:
        print(f"store: {status.store_error}")
    if status.witness_error:
        print(f"witness: {status.witness_error}")
    elif status.proof_keys:
        print(f"witnessed: {', '.join(status.proof_keys)}")
    print(f"{'ok' if status.ok else 'FAILED'}: manifest {status.manifest_key}")
    if not status.ok:
        sys.exit(1)


def state_command(args: argparse.Namespace) -> None:
    from grid_mysteries.capture import state
    from grid_mysteries.capture.store import store_from_url

    store = store_from_url(args.store)
    root = args.repo_root.resolve()
    if args.capture_command == "pull-state":
        lines = state.pull(store, root, args.name, overwrite=args.overwrite)
    else:
        if not args.path:
            raise SystemExit("push-state: at least one --path is required")
        lines = state.push(store, root, args.name, args.path, include=args.include or None)
    for line in lines:
        print(line)
    print(f"{args.capture_command} {args.name}: {len(lines)} file(s)")
    if any(line.startswith("MISMATCH") for line in lines):
        sys.exit(1)


def watchdog_command(args: argparse.Namespace) -> None:
    from grid_mysteries.capture.store import S3Store, store_from_url
    from grid_mysteries.capture.watchdog import run_watchdog, s3_settings

    store = store_from_url(args.store)
    settings = s3_settings(store.bucket, store.client) if isinstance(store, S3Store) else None
    report = run_watchdog(
        store,
        repo_root=args.repo_root.resolve(),
        settings=settings,
        include_bytes=args.include_bytes,
    )
    for check in report.checks:
        print(f"{'ok ' if check.ok else '!! '} {check.name}: {check.detail}")
    for line in report.synced:
        print(f"sync {line}")
    failed = not report.ok or any(s.startswith("MISMATCH") for s in report.synced)
    print("check-vintages: FAILED" if failed else "check-vintages: OK")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    app()
