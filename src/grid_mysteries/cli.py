"""The project's small operational CLI: toolchain state and digests.

Deliberately stdlib-only. Two commands do not justify a CLI framework
dependency, and every artefact digest the research record relies on is
computed by `grid_mysteries.hashing`, not here.
"""

import argparse
import platform
import shutil
import sys
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

    args = parser.parse_args(argv)
    if args.command == "doctor":
        doctor()
    else:
        print(sha256_file(args.path))


if __name__ == "__main__":
    app()
