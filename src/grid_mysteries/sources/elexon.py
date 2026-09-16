"""Adapters for the Elexon Insights Solution API (BMRS successor).

Endpoint and field semantics come from Elexon's published Insights API and
dataset documentation. Each fetch pins an immutable local artefact; analytics
must read only pinned files, never the live API.
"""

import time
from collections.abc import Iterable
from datetime import date, timedelta
from pathlib import Path

import httpx

from grid_mysteries.corpus import DIRECTIONS, Direction, physical_path, window_path
from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.http import fetch_artifact

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
SOURCE = "elexon-insights"

PHYSICAL_DATASETS = ("PN", "MELS", "MILS")
#: The per-period datasets `period_jobs` knows how to pin, in the order an
#: investigation's full acquisition requests them.
PERIOD_DATASETS = ("BOD", "DISPTAV", "BOALF", *PHYSICAL_DATASETS)


def bid_offer_url(settlement_date: str, settlement_period: int) -> str:
    """All-BMU bid-offer data (dataset BOD) for one settlement period."""
    return (
        f"{BASE_URL}/balancing/bid-offer/all"
        f"?settlementDate={settlement_date}&settlementPeriod={settlement_period}"
    )


def acceptance_volumes_url(
    direction: Direction, settlement_date: str, settlement_period: int
) -> str:
    """All-BMU indicative acceptance volumes (dataset DISPTAV) for one period."""
    return (
        f"{BASE_URL}/balancing/settlement/indicative/volumes/all"
        f"/{direction}/{settlement_date}/{settlement_period}"
    )


def acceptances_url(settlement_date: str, settlement_period: int) -> str:
    """All-BMU bid-offer acceptances (dataset BOALF) for one settlement period."""
    return (
        f"{BASE_URL}/balancing/acceptances/all"
        f"?settlementDate={settlement_date}&settlementPeriod={settlement_period}"
    )


def physical_url(dataset: str, settlement_date: str, settlement_period: int) -> str:
    """All-BMU physical data (PN, MELS, MILS, ...) for one settlement period."""
    return (
        f"{BASE_URL}/balancing/physical/all"
        f"?dataset={dataset}&settlementDate={settlement_date}&settlementPeriod={settlement_period}"
    )


def day_stream_url(dataset: str, day: str, bm_units: Iterable[str] = ()) -> str:
    """One calendar day of a dataset stream, [day 00:00Z, next day 00:00Z),
    optionally filtered to the given BM units."""
    next_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    url = f"{BASE_URL}/datasets/{dataset}/stream?from={day}T00:00Z&to={next_day}T00:00Z"
    return url + "".join(f"&bmUnit={unit}" for unit in bm_units)


def cashflows_url(direction: Direction, settlement_date: str) -> str:
    """All-BMU published indicative cashflows (dataset EBOCF) for one
    settlement day and direction; one request covers every period."""
    return f"{BASE_URL}/balancing/settlement/indicative/cashflows/all/{direction}/{settlement_date}"


def period_jobs(
    settlement_date: str,
    periods: Iterable[int],
    *,
    datasets: Iterable[str] = PERIOD_DATASETS,
) -> list[tuple[str, str, Path]]:
    """(dataset, url, destination) pinning jobs for every period of one day.

    Datasets are emitted per period in the order given; DISPTAV expands to
    one job per direction (offer, then bid). Destinations follow the pinned
    corpus layout in `grid_mysteries.corpus`, so every investigation that
    pins a per-period artefact lands it where every reader looks.
    """
    jobs: list[tuple[str, str, Path]] = []
    for period in periods:
        for dataset in datasets:
            if dataset == "BOD":
                url = bid_offer_url(settlement_date, period)
                jobs.append((dataset, url, window_path("bod", settlement_date, period)))
            elif dataset == "DISPTAV":
                for direction in DIRECTIONS:
                    url = acceptance_volumes_url(direction, settlement_date, period)
                    destination = window_path(f"disptav_{direction}", settlement_date, period)
                    jobs.append((dataset, url, destination))
            elif dataset == "BOALF":
                url = acceptances_url(settlement_date, period)
                jobs.append((dataset, url, window_path("boalf", settlement_date, period)))
            elif dataset in PHYSICAL_DATASETS:
                url = physical_url(dataset, settlement_date, period)
                jobs.append((dataset, url, physical_path(dataset, settlement_date, period)))
            else:
                raise ValueError(f"no per-period pinning layout for dataset {dataset!r}")
    return jobs


def fetch_pinned(
    *,
    url: str,
    destination: Path,
    dataset: str,
    attempts: int = 3,
    retry_delay_seconds: float = 2.0,
) -> SourceArtifact:
    """Fetch one artefact with bounded retries on transient failures."""
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return fetch_artifact(url=url, destination=destination, source=SOURCE, dataset=dataset)
        except (httpx.TransportError, httpx.HTTPStatusError) as error:
            if isinstance(error, httpx.HTTPStatusError) and error.response.status_code < 500:
                raise
            last_error = error
            if attempt < attempts - 1:
                time.sleep(retry_delay_seconds * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url} after {attempts} attempts") from last_error


def bmunits_url() -> str:
    """The BM Unit registration reference: id map, lead party, fuel type,
    capacities, FPN flag — one snapshot per pin, kept as a vintage."""
    return f"{BASE_URL}/reference/bmunits/all"


def system_prices_url(settlement_date: str) -> str:
    """Settlement system prices (buy and sell) for every period of one day."""
    return f"{BASE_URL}/balancing/settlement/system-prices/{settlement_date}"


def windfor_stream_url(publish_from: str, publish_to: str) -> str:
    """Every WINDFOR issue published in [publish_from, publish_to].

    WINDFOR is NESO's wind generation forecast for the wind farms visible to
    it with operational metering, published up to eight times a day (03:30,
    05:30, 08:30, 10:30, 12:30, 16:30, 19:30, 23:30). Filtering by publish
    time — rather than taking the endpoint's default latest issue — is what
    makes the forecast's evolution, not just its final value, recoverable.
    """
    return (
        f"{BASE_URL}/datasets/WINDFOR/stream"
        f"?publishDateTimeFrom={publish_from}&publishDateTimeTo={publish_to}"
    )


def wind_forecast_evolution_url(start_time: str) -> str:
    """Every WINDFOR issue for one target hour, carrying the publisher's own
    settlement date and period for that hour."""
    return f"{BASE_URL}/forecast/generation/wind/evolution?startTime={start_time}&format=json"


def wind_solar_day_ahead_url(
    start_from: str, start_to: str, process_type: str = "day ahead"
) -> str:
    """Day-ahead wind and solar generation forecast (DGWS, ex-B1440) for
    target times in [start_from, start_to]."""
    encoded = process_type.replace(" ", "%20")
    return (
        f"{BASE_URL}/forecast/generation/wind-and-solar/day-ahead"
        f"?from={start_from}&to={start_to}&processType={encoded}&format=json"
    )


def _unit_filter(bm_units: Iterable[str]) -> str:
    return "".join(f"&bmUnit={unit}" for unit in bm_units)


def pn_stream_url(
    settlement_date: str, bm_units: Iterable[str], *, period_from: int = 1, period_to: int = 48
) -> str:
    """Final physical notifications for one settlement day, for the given
    BM units. PN rows are point-MW segments, not per-period levels."""
    return (
        f"{BASE_URL}/datasets/PN/stream"
        f"?from={settlement_date}&to={settlement_date}"
        f"&settlementPeriodFrom={period_from}&settlementPeriodTo={period_to}"
        + _unit_filter(bm_units)
    )


def b1610_stream_url(
    settlement_date: str, bm_units: Iterable[str], *, period_from: int = 1, period_to: int = 48
) -> str:
    """Half-hourly actual metered generation (B1610) for one settlement day,
    for the given BM units. Metered volume (MWh), not instantaneous power."""
    return (
        f"{BASE_URL}/datasets/B1610/stream"
        f"?from={settlement_date}&to={settlement_date}"
        f"&settlementPeriodFrom={period_from}&settlementPeriodTo={period_to}"
        + _unit_filter(bm_units)
    )
