"""Adapter for the Octopus Energy public tariff API (no key).

Endpoint shapes follow Octopus's published developer documentation. The
adapter builds URLs, pins immutable pages, and turns pinned pages into the
model's `Rate` intervals; analytics read only pinned files, never the live
API. Import prices are read inclusive of VAT (domestic 5 %); export
payments carry no VAT and every export row is checked for it.

The information set is stamped here, not in the model: an Agile rate is
known at 16:00 local on the calendar day whose 23:00 starts its Agile day;
a fixed time-of-use rate is known indefinitely. Any other tariff family a
later source adds (a five-minute wholesale pass-through, an EPEX-indexed
tariff) supplies its own `published_at` rule and the model is untouched.
"""

import json
import time
from collections.abc import Callable, Iterable, Mapping
from datetime import UTC, datetime, timedelta
from datetime import time as time_of_day
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

import httpx

from grid_mysteries.investigations.household_desk import LONDON, Rate
from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.http import fetch_artifact

BASE_URL = "https://api.octopus.energy/v1"
SOURCE = "octopus-energy-api"
PAGE_SIZE = 1500

Side = Literal["import", "export"]

#: Distribution-network regions as Octopus letters them; the letter is the
#: last component of a tariff code.
REGIONS: Mapping[str, str] = {
    "A": "Eastern England",
    "B": "East Midlands",
    "C": "London",
    "D": "Merseyside and Northern Wales",
    "E": "West Midlands",
    "F": "North Eastern England",
    "G": "North Western England",
    "H": "Southern England",
    "J": "South Eastern England",
    "K": "Southern Wales",
    "L": "South Western England",
    "M": "Yorkshire",
    "N": "Southern Scotland",
    "P": "Northern Scotland",
}

#: Products declared by 010 (`investigations/010-household-desk/DECLARATION.md`).
IMPORT_PRODUCTS = (
    "AGILE-24-10-01",
    "GO-VAR-22-10-14",
    "INTELLI-VAR-22-10-14",
    "FLUX-IMPORT-23-02-14",
    "INTELLI-FLUX-IMPORT-23-07-14",
)
EXPORT_PRODUCTS = (
    "AGILE-OUTGOING-19-05-13",
    "OUTGOING-VAR-24-10-26",
    "OUTGOING-PRIME-FIX-12M-26-06-23",
    "FLUX-EXPORT-23-02-14",
)
#: Products whose prices are set day by day and published the afternoon
#: before; everything else declared is a fixed or time-of-use schedule.
DAY_AHEAD_PRODUCTS = frozenset({"AGILE-24-10-01", "AGILE-OUTGOING-19-05-13"})

AGILE_PUBLICATION = time_of_day(16, 0)
AGILE_DAY_START = time_of_day(23, 0)

RATE_FIELDS = frozenset({"valid_from", "valid_to", "value_exc_vat", "value_inc_vat"})


def tariff_code(product: str, region: str) -> str:
    """The expected single-register electricity tariff code; the pinned
    product document, not this expectation, decides at run time."""
    if region not in REGIONS:
        raise ValueError(f"unknown region letter {region!r}")
    return f"E-1R-{product}-{region}"


def products_url(page: int = 1) -> str:
    return f"{BASE_URL}/products/?page={page}"


def product_url(product: str) -> str:
    return f"{BASE_URL}/products/{product}/"


def _stamp(moment: datetime | str) -> str:
    if isinstance(moment, str):
        return moment
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%MZ")


def unit_rates_url(
    product: str,
    tariff: str,
    period_from: datetime | str,
    period_to: datetime | str,
    *,
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> str:
    return (
        f"{BASE_URL}/products/{product}/electricity-tariffs/{tariff}/standard-unit-rates/"
        f"?period_from={_stamp(period_from)}&period_to={_stamp(period_to)}"
        f"&page_size={page_size}&page={page}"
    )


def standing_charges_url(
    product: str,
    tariff: str,
    period_from: datetime | str,
    period_to: datetime | str,
    *,
    page: int = 1,
    page_size: int = PAGE_SIZE,
) -> str:
    return (
        f"{BASE_URL}/products/{product}/electricity-tariffs/{tariff}/standing-charges/"
        f"?period_from={_stamp(period_from)}&period_to={_stamp(period_to)}"
        f"&page_size={page_size}&page={page}"
    )


def tariff_codes_in_product(document: Mapping[str, Any], region: str) -> list[str]:
    """Every single-register electricity tariff code the product document
    names for a region, across payment methods, de-duplicated and sorted."""
    tariffs = document.get("single_register_electricity_tariffs") or {}
    by_method = tariffs.get(f"_{region}") or {}
    codes = {
        str(entry["code"])
        for entry in by_method.values()
        if isinstance(entry, Mapping) and entry.get("code")
    }
    return sorted(codes)


def next_page(payload: Mapping[str, Any]) -> str | None:
    """The API's own URL for the following page, or None on the last page."""
    following = payload.get("next")
    return str(following) if following else None


def agile_published_at(valid_from: datetime) -> datetime:
    """16:00 local on the calendar day whose 23:00 begins the Agile day
    containing `valid_from`. Octopus publishes 'around 16:00'; occasional
    later publication makes this stamp slightly generous to the household."""
    local = valid_from.astimezone(LONDON)
    start_day = local.date() if local.time() >= AGILE_DAY_START else local.date() - timedelta(1)
    return datetime.combine(start_day, AGILE_PUBLICATION, tzinfo=LONDON)


def known_indefinitely(valid_from: datetime) -> None:
    return None


def publication_rule(product: str) -> Callable[[datetime], datetime | None]:
    return agile_published_at if product in DAY_AHEAD_PRODUCTS else known_indefinitely


def _moment(value: object) -> datetime | None:
    if value is None:
        return None
    text = str(value).replace("Z", "+00:00")
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None:
        raise ValueError(f"Octopus timestamp without offset: {value!r}")
    return moment.astimezone(UTC)


def parse_rates(
    payload: Mapping[str, Any],
    *,
    side: Side,
    published_at: Callable[[datetime], datetime | None],
) -> list[Rate]:
    """Rates from one pinned unit-rates page. Import reads `value_inc_vat`;
    export reads `value_exc_vat` and requires the two to agree, which is
    the API's own statement that a domestic export payment bears no VAT."""
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError("unit-rates page has no 'results' list")
    rates: list[Rate] = []
    for row in results:
        missing = RATE_FIELDS - set(row)
        if missing:
            raise ValueError(f"unit-rate row lacks {sorted(missing)}")
        exc, inc = Decimal(str(row["value_exc_vat"])), Decimal(str(row["value_inc_vat"]))
        if side == "export":
            if exc != inc:
                raise ValueError(f"export rate carries VAT: exc {exc} inc {inc} at {row}")
            price = exc
        else:
            price = inc
        valid_from = _moment(row["valid_from"])
        if valid_from is None:
            raise ValueError(f"unit-rate row without valid_from: {row}")
        rates.append(
            Rate(
                valid_from=valid_from,
                valid_to=_moment(row["valid_to"]),
                pence_per_kwh=price,
                published_at=published_at(valid_from),
            )
        )
    return rates


def load_rates(
    paths: Iterable[Path],
    *,
    side: Side,
    published_at: Callable[[datetime], datetime | None],
) -> list[Rate]:
    """Merge pinned pages into one sorted, overlap-free rate list. Pages
    from the API arrive newest first; duplicates across pages collapse."""
    seen: dict[datetime, Rate] = {}
    for path in paths:
        payload = json.loads(path.read_text(), parse_float=Decimal)
        for rate in parse_rates(payload, side=side, published_at=published_at):
            previous = seen.get(rate.valid_from)
            if previous is not None and previous != rate:
                raise ValueError(f"conflicting rates at {rate.valid_from}: {previous} vs {rate}")
            seen[rate.valid_from] = rate
    ordered = sorted(seen.values(), key=lambda r: r.valid_from)
    for earlier, later in zip(ordered, ordered[1:], strict=False):
        if earlier.valid_to is None or earlier.valid_to > later.valid_from:
            raise ValueError(f"overlapping rates: {earlier} then {later}")
    return ordered


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
            last_error = error
            if isinstance(error, httpx.HTTPStatusError) and error.response.status_code < 500:
                raise
            if attempt + 1 < attempts:
                time.sleep(retry_delay_seconds * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url} after {attempts} attempts") from last_error
