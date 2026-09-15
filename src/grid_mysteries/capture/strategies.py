"""Fetch strategies: each turns one plan resource into captured artefacts.

A strategy yields `Captured` items in fetch order and raises on a failure
that makes the resource's day incomplete; the run records the error and
moves on. Strategies never parse beyond what is needed to find the next
URL (a CKAN resource's download URL, a REMIT list's detail URLs, a page's
asset links, a GeoJSON's point ids).
"""

import json
import re
import time
import urllib.parse
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta

from grid_mysteries.capture.fetch import Fetcher, Response
from grid_mysteries.capture.plan import Resource

CKAN_ACTION = "https://api.neso.energy/api/3/action"
ASSET_LINK = re.compile(
    r'https://assets\.publishing\.service\.gov\.uk/[^"\']+\.(?:csv|xlsx|xls|ods)'
)
OCDS_MAX_PAGES = 200


@dataclass(frozen=True)
class Captured:
    dataset: str
    url: str
    body: bytes
    headers: dict[str, str] = field(default_factory=dict)
    extra: dict[str, str] = field(default_factory=dict)


class FetchError(RuntimeError):
    pass


def _get(fetcher: Fetcher, url: str, *, data: bytes | None = None) -> Response:
    response = fetcher.get(url, data=data)
    if not response.ok:
        raise FetchError(f"HTTP {response.status} for {url}")
    return response


def ckan(
    resource: Resource,
    fetcher: Fetcher,
    day: date,
    *,
    previous: dict[str, dict[str, str]] | None = None,
) -> Iterator[Captured]:
    """The resource's metadata, then its bytes, unless the portal's
    `last_modified` equals the one recorded at the last capture of the
    same resource: then only the metadata is captured and the manifest
    says so (`skipped: unchanged last_modified`). A 200 MB datastore dump
    that has not changed is not downloaded daily on the strength of a
    hash it would produce anyway."""
    rid = resource.params["resource_id"]
    show = _get(fetcher, f"{CKAN_ACTION}/resource_show?id={rid}")
    meta = json.loads(show.body)["result"]
    last_modified = str(meta.get("last_modified") or "")
    before = (previous or {}).get(f"{resource.resource}/{resource.name}", {})
    if last_modified and before.get("ckan_last_modified") == last_modified:
        yield Captured(
            f"{resource.name}-META",
            show.url,
            show.body,
            show.kept_headers(),
            {"skipped": "unchanged last_modified", "ckan_last_modified": last_modified},
        )
        return
    yield Captured(f"{resource.name}-META", show.url, show.body, show.kept_headers())
    download = _get(fetcher, meta["url"])
    yield Captured(
        resource.name,
        download.url,
        download.body,
        download.kept_headers(),
        {"ckan_last_modified": last_modified, "ckan_name": str(meta.get("name") or "")},
    )


def url(resource: Resource, fetcher: Fetcher, day: date) -> Iterator[Captured]:
    response = _get(fetcher, resource.params["url"])
    yield Captured(resource.name, response.url, response.body, response.kept_headers())


def eso_map(
    resource: Resource, fetcher: Fetcher, day: date, *, pause: Callable[[float], None] = time.sleep
) -> Iterator[Captured]:
    base = resource.params["base"]
    points = _get(fetcher, base + "get-points.php")
    yield Captured(f"{resource.name}-POINTS", points.url, points.body, points.kept_headers())
    lines = _get(fetcher, base + "get-lines.php")
    yield Captured(f"{resource.name}-LINES", lines.url, lines.body, lines.kept_headers())
    ids = [feature["properties"]["id"] for feature in json.loads(points.body)["features"]]
    for point_id in ids:
        body = urllib.parse.urlencode({"id": point_id}).encode()
        detail = _get(fetcher, base + "get-point-json.php", data=body)
        yield Captured(
            f"{resource.name}-POINT-{point_id}",
            f"{base}get-point-json.php?id={point_id}",
            detail.body,
            detail.kept_headers(),
        )
        pause(0.15)


def elexon_remit(resource: Resource, fetcher: Fetcher, day: date) -> Iterator[Captured]:
    """Messages published on the previous UTC day: the list, then each
    message by the detail URL the list itself carries."""
    previous = (day - timedelta(days=1)).isoformat()
    listing = _get(
        fetcher,
        f"{resource.params['base']}/remit/list/by-publish?from={previous}T00:00:00Z&to={previous}T23:59:59Z",
    )
    yield Captured(
        f"{resource.name}-LIST-{previous}", listing.url, listing.body, listing.kept_headers()
    )
    for item in json.loads(listing.body).get("data", []):
        detail = _get(fetcher, item["url"])
        yield Captured(
            f"{resource.name}-MESSAGE-{item['id']}",
            detail.url,
            detail.body,
            detail.kept_headers(),
            {
                "mrid": str(item.get("mrid") or ""),
                "revision": str(item.get("revisionNumber") or ""),
            },
        )


def ocds_daily(resource: Resource, fetcher: Fetcher, day: date) -> Iterator[Captured]:
    """Every page of the previous UTC day's release package; pages follow
    the package's own `links.next` until it is absent."""
    previous = (day - timedelta(days=1)).isoformat()
    next_url: str | None = resource.params["template"].format(day=previous)
    page = 1
    while next_url and page <= OCDS_MAX_PAGES:
        response = _get(fetcher, next_url)
        yield Captured(
            f"{resource.name}-{previous}-P{page:03d}",
            response.url,
            response.body,
            response.kept_headers(),
        )
        try:
            next_url = json.loads(response.body).get("links", {}).get("next")
        except ValueError:
            next_url = None
        page += 1


def gov_assets(resource: Resource, fetcher: Fetcher, day: date) -> Iterator[Captured]:
    page = _get(fetcher, resource.params["url"])
    yield Captured(f"{resource.name}-PAGE", page.url, page.body, page.kept_headers())
    for link in sorted(set(ASSET_LINK.findall(page.body.decode("utf-8", errors="replace")))):
        asset = _get(fetcher, link)
        yield Captured(
            f"{resource.name}-{link.rsplit('/', 1)[-1]}",
            asset.url,
            asset.body,
            asset.kept_headers(),
        )


STRATEGIES: dict[str, Callable[..., Iterator[Captured]]] = {
    "ckan": ckan,
    "url": url,
    "eso_map": eso_map,
    "elexon_remit": elexon_remit,
    "ocds_daily": ocds_daily,
    "gov_assets": gov_assets,
}
