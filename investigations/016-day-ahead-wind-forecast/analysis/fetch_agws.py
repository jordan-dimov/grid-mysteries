"""016 analysis — pin AGWS (B1630) for the 2026-09-08 settlement day.

Actual or estimated wind and solar net generation per bidding zone per
settlement period: the same-population observation pair for the pack's DGWS
forecast (Regulation (EU) 543/2013 items 14.1.d and 16.1.c). Pinned under the
repo's acquisition habit — journalled, manifest digest, externally witnessed
by scripts/timestamp. The pinned bytes are the vintage Elexon serves now; the
dataset is updated as measured values arrive, so the fetch instant in the
manifest is part of the evidence.

    uv run python investigations/016-day-ahead-wind-forecast/analysis/fetch_agws.py
"""

from pathlib import Path

from grid_mysteries.sources import elexon
from grid_mysteries.sources.pinning import pin, progress

HERE = Path(__file__).parent
DATA = HERE / "data"
URL = (
    "https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type/wind-and-solar"
    "?from=2026-09-07T23:00Z&to=2026-09-08T22:59Z"
)


def main() -> None:
    jobs = [("AGWS", URL, DATA / "agws_2026-09-08.json")]
    pin(
        jobs,
        fetch=elexon.fetch_pinned,
        label="016-analysis",
        progress=progress,
        journal_path=DATA / "agws-journal.ndjson",
        manifest_path=DATA / "agws-manifest.json",
    )


if __name__ == "__main__":
    main()
