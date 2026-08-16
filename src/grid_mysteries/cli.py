from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path

import typer

from grid_mysteries.hashing import sha256_file

app = typer.Typer(no_args_is_help=True, help="Research Britain's electricity mysteries.")


@app.command()
def doctor() -> None:
    """Show the local research-toolchain state."""
    typer.echo(f"python={platform.python_version()}")
    typer.echo(f"python_ok={sys.version_info >= (3, 14)}")
    typer.echo(f"morpholog={shutil.which('morpholog') or 'not found'}")


@app.command("hash-source")
def hash_source(path: Path) -> None:
    """Print a source artefact's SHA-256 digest."""
    typer.echo(sha256_file(path))


if __name__ == "__main__":
    app()
