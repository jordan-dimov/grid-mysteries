"""Adapters for the Elexon Insights Solution API (BMRS successor).

Endpoint and field semantics come from Elexon's published Insights API and
dataset documentation. Each fetch pins an immutable local artefact; analytics
must read only pinned files, never the live API.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Literal

import httpx

from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.http import fetch_artifact

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
SOURCE = "elexon-insights"

Direction = Literal["bid", "offer"]


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
