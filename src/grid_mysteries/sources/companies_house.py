"""Companies House Public Data API: URL builders, legal-name normalisation and
an authenticated, journalled fetch.

The API needs a free key sent as the HTTP basic-auth username. Nothing here
decides anything about a company; resolution rules live in
``grid_mysteries.investigations.spv_financing``.
"""

import os
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

import httpx

from grid_mysteries.hashing import sha256_file
from grid_mysteries.models import SourceArtifact

BASE_URL = "https://api.company-information.service.gov.uk"
KEY_ENV = "COMPANIES_HOUSE_API_KEY"
# Documented limit: 600 requests per five minutes. 0.55 s between calls
# stays under it with margin.
MIN_SECONDS_BETWEEN_CALLS = 0.55

_SUFFIXES: tuple[tuple[str, str], ...] = (
    ("PUBLIC LIMITED COMPANY", "PLC"),
    ("LIMITED LIABILITY PARTNERSHIP", "LLP"),
    ("LIMITED", "LTD"),
    ("COMPANY", "CO"),
)


def normalise_company_name(name: object) -> str:
    """Case-, punctuation- and suffix-insensitive form of a legal company name."""
    text = str(name or "").upper().replace("&", " AND ")
    text = re.sub(r"[^A-Z0-9 ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    for long, short in _SUFFIXES:
        text = re.sub(rf"\b{long}\b", short, text)
    return text


def search_url(name: str, *, items_per_page: int = 20) -> str:
    return f"{BASE_URL}/search/companies?q={quote(name)}&items_per_page={items_per_page}"


def profile_url(company_number: str) -> str:
    return f"{BASE_URL}/company/{company_number}"


def charges_url(company_number: str) -> str:
    return f"{BASE_URL}/company/{company_number}/charges?items_per_page=100"


def api_key() -> str:
    key = os.environ.get(KEY_ENV, "").strip()
    if not key:
        raise RuntimeError(f"{KEY_ENV} is not set; no Companies House request is possible")
    return key


class AuthenticatedFetcher:
    """Pin one JSON response per URL, throttled, with the key as basic-auth user.

    A 404 is pinned too (as the body Companies House returns), because
    "this company has no charges" is evidence, not an error.
    """

    def __init__(self, key: str, *, timeout_seconds: float = 30.0) -> None:
        self._auth = httpx.BasicAuth(key, "")
        self._timeout = timeout_seconds
        self._last_call = 0.0

    def __call__(self, *, url: str, destination: Path, dataset: str) -> SourceArtifact:
        if destination.exists():
            raise FileExistsError(f"pinned artefact already exists: {destination}")
        wait = MIN_SECONDS_BETWEEN_CALLS - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with httpx.Client(timeout=self._timeout, auth=self._auth) as client:
            response = client.get(url, headers={"Accept": "application/json"})
        self._last_call = time.monotonic()
        if response.status_code not in (200, 404):
            response.raise_for_status()
        destination.write_bytes(response.content)
        return SourceArtifact(
            source="companies-house",
            dataset=dataset,
            path=destination,
            sha256=sha256_file(destination),
            fetched_at=datetime.now(UTC),
        )


def advanced_search_url(name: str, *, size: int = 20) -> str:
    return f"{BASE_URL}/advanced-search/companies?company_name_includes={quote(name)}&size={size}"


def filing_history_url(company_number: str) -> str:
    return f"{BASE_URL}/company/{company_number}/filing-history?items_per_page=100"
