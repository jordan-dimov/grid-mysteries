"""F006 — pin public documents by digest (forward track: acquisition is not the
irreversible boundary, publication is; everything read is nonetheless pinned).

usage: pin.py <manifest-name> name=url [name=url ...]
Journals under data/raw/forward-f006/<manifest-name>/; manifest copied to
evidence/<manifest-name>-manifest.json. A refusal (403/404) is recorded in
evidence/<manifest-name>-unavailable.json, never retried by other means.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.hashing import sha256_file
from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.pinning import fetch_journalled, progress

HERE = Path(__file__).parent
UA = "grid-mysteries/0.1 (+research; public documents pinned by digest)"


def fetch(*, url: str, destination: Path, dataset: str) -> SourceArtifact:
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=60, follow_redirects=True, headers={"User-Agent": UA}) as client:
        response = client.get(url)
        response.raise_for_status()
        destination.write_bytes(response.content)
    return SourceArtifact(
        source="web", dataset=dataset, path=destination,
        sha256=sha256_file(destination), fetched_at=datetime.now(UTC),
    )


def main() -> int:
    batch, items = sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]]
    raw = REPO_ROOT / "data/raw/forward-f006" / batch
    unavailable_path = HERE / "evidence" / f"{batch}-unavailable.json"
    unavailable = json.loads(unavailable_path.read_text()) if unavailable_path.exists() else {}
    for name, url in items:
        suffix = ".pdf" if ".pdf" in url.lower() else ".html"
        try:
            fetch_journalled(
                [(name, url, raw / f"{name}{suffix}")],
                journal_path=raw / "journal.ndjson",
                manifest_path=raw / "manifest.json",
                repo_root=REPO_ROOT, fetch=fetch, sleep_seconds=0.5, progress=progress,
            )
        except Exception as error:  # noqa: BLE001 — recorded, never worked around
            unavailable[name] = {"url": url, "error": str(error).splitlines()[0],
                                 "at": datetime.now(UTC).isoformat()}
            print(f"UNAVAILABLE {name}: {unavailable[name]['error']}", flush=True)
    (HERE / "evidence").mkdir(exist_ok=True)
    if (raw / "manifest.json").exists():
        (HERE / "evidence" / f"{batch}-manifest.json").write_bytes((raw / "manifest.json").read_bytes())
    if unavailable:
        unavailable_path.write_text(json.dumps(unavailable, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
