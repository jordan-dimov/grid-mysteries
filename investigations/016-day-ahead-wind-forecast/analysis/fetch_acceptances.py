"""016 analysis — pin the acceptance record for the 2026-09-08 settlement day.

DISPTAV bid-side accepted volumes and BOALF bid-offer acceptances, per
settlement period, all BM units as published. The wind filter is applied at
analysis time against the pack's own unit list, never at fetch time, so the
pinned archive stays the publisher's record of the day rather than our cut
of it. DISPTAV carries several `dataType` variants; the accepted volume the
D2 comparator uses is `Tagged` (015's declared rule), chosen in the analysis,
not here.

Pinned under the repo's acquisition habit — journalled, manifest digest,
externally witnessed by scripts/timestamp. The pinned bytes are the vintage
Elexon serves now.

    uv run python investigations/016-day-ahead-wind-forecast/analysis/fetch_acceptances.py
"""

from pathlib import Path

from grid_mysteries.corpus import PERIODS
from grid_mysteries.sources import elexon
from grid_mysteries.sources.pinning import pin, progress

HERE = Path(__file__).parent
DATA = HERE / "data"
DAY = "2026-09-08"


def main() -> None:
    jobs: list[tuple[str, str, Path]] = []
    for period in PERIODS:
        jobs.append(
            (
                "DISPTAV",
                elexon.acceptance_volumes_url("bid", DAY, period),
                DATA / "acceptances" / f"disptav_bid_p{period:02d}.json",
            )
        )
    for period in PERIODS:
        jobs.append(
            (
                "BOALF",
                elexon.acceptances_url(DAY, period),
                DATA / "acceptances" / f"boalf_p{period:02d}.json",
            )
        )
    pin(
        jobs,
        fetch=elexon.fetch_pinned,
        label="016-analysis-acceptances",
        progress=progress,
        journal_path=DATA / "acceptances-journal.ndjson",
        manifest_path=DATA / "acceptances-manifest.json",
    )


if __name__ == "__main__":
    main()
