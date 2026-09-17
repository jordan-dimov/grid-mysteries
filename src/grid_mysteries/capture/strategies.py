"""Fetch strategies: each turns one plan resource into captured artefacts.

A strategy yields `Captured` items in fetch order and raises on a failure
that makes the resource's day incomplete; the run records the error and
moves on. Strategies never parse beyond what is needed to find the next
URL (a CKAN resource's download URL, a REMIT list's detail URLs, a page's
asset links, a GeoJSON's point ids).
"""

import hashlib
import json
import re
import time
import urllib.parse
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Final

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
    body: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    extra: dict[str, str] = field(default_factory=dict)
    #: A large body spooled to disk by the fetcher: hashed and uploaded from the file.
    path: Path | None = None
    size: int = 0
    sha256: str = ""

    @classmethod
    def of(cls, dataset: str, response: Response, extra: dict[str, str] | None = None) -> Captured:
        return cls(
            dataset,
            response.url,
            response.body,
            response.kept_headers(),
            extra or {},
            response.path,
            response.size,
            response.sha256,
        )

    def digest(self) -> str:
        return self.sha256 or hashlib.sha256(self.body).hexdigest()

    def length(self) -> int:
        return self.size if self.path is not None else len(self.body)


class FetchError(RuntimeError):
    pass


FORM: Final = "application/x-www-form-urlencoded"


def _get(
    fetcher: Fetcher,
    url: str,
    *,
    data: bytes | None = None,
    content_type: str | None = None,
    headers: dict[str, str] | None = None,
) -> Response:
    response = fetcher.get(url, data=data, content_type=content_type, headers=headers or None)
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
    base = resource.params.get("base", CKAN_ACTION)
    show = _get(fetcher, f"{base}/resource_show?id={rid}", headers=resource.headers)
    meta = json.loads(show.text())["result"]
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
    download = _get(fetcher, meta["url"], headers=resource.headers)
    yield Captured.of(
        resource.name,
        download,
        {"ckan_last_modified": last_modified, "ckan_name": str(meta.get("name") or "")},
    )


def ckan_package(
    resource: Resource,
    fetcher: Fetcher,
    day: date,
    *,
    previous: dict[str, dict[str, str]] | None = None,
) -> Iterator[Captured]:
    """A whole CKAN package: `package_show`, then every listed resource whose
    format is in `formats` (all, when unset) and whose `last_modified` differs
    from the one recorded at its last capture. Each file is its own dataset,
    `<name>-<resource id>`, so a package that adds a resource a month (NESO's
    BSUoS forecast) or keeps every monthly vintage (SSEN's register) is
    captured once per vintage and the unchanged ones cost one metadata line.
    `base` points the strategy at a portal other than NESO's."""
    base = resource.params.get("base", CKAN_ACTION)
    pid = resource.params["package_id"]
    wanted = {f.strip().upper() for f in resource.params.get("formats", "").split(",") if f}
    show = _get(fetcher, f"{base}/package_show?id={pid}", headers=resource.headers)
    yield Captured(f"{resource.name}-META", show.url, show.body, show.kept_headers())
    for item in json.loads(show.text())["result"].get("resources", []):
        rid, href = str(item.get("id") or ""), str(item.get("url") or "")
        fmt = str(item.get("format") or "").upper()
        if not rid or not href or (wanted and fmt not in wanted):
            continue
        dataset = f"{resource.name}-{rid}"
        last_modified = str(item.get("last_modified") or "")
        before = (previous or {}).get(f"{resource.resource}/{dataset}", {})
        if last_modified and before.get("ckan_last_modified") == last_modified:
            continue
        download = _get(fetcher, href, headers=resource.headers)
        yield Captured.of(
            dataset,
            download,
            {"ckan_last_modified": last_modified, "ckan_name": str(item.get("name") or "")},
        )


def url(resource: Resource, fetcher: Fetcher, day: date) -> Iterator[Captured]:
    response = _get(fetcher, resource.params["url"], headers=resource.headers)
    yield Captured.of(resource.name, response)


def eso_map(
    resource: Resource, fetcher: Fetcher, day: date, *, pause: Callable[[float], None] = time.sleep
) -> Iterator[Captured]:
    base = resource.params["base"]
    points = _get(fetcher, base + "get-points.php")
    yield Captured(f"{resource.name}-POINTS", points.url, points.body, points.kept_headers())
    lines = _get(fetcher, base + "get-lines.php")
    yield Captured(f"{resource.name}-LINES", lines.url, lines.body, lines.kept_headers())
    ids = [feature["properties"]["id"] for feature in json.loads(points.text())["features"]]
    for point_id in ids:
        body = urllib.parse.urlencode({"id": point_id}).encode()
        detail = _get(fetcher, base + "get-point-json.php", data=body, content_type=FORM)
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
    for item in json.loads(listing.text()).get("data", []):
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
            next_url = json.loads(response.text()).get("links", {}).get("next")
        except ValueError:
            next_url = None
        page += 1


def gov_assets(resource: Resource, fetcher: Fetcher, day: date) -> Iterator[Captured]:
    page = _get(fetcher, resource.params["url"])
    yield Captured(f"{resource.name}-PAGE", page.url, page.body, page.kept_headers())
    for link in sorted(set(ASSET_LINK.findall(page.text()))):
        asset = _get(fetcher, link)
        yield Captured.of(f"{resource.name}-{link.rsplit('/', 1)[-1]}", asset)


STRATEGIES: dict[str, Callable[..., Iterator[Captured]]] = {
    "ckan": ckan,
    "ckan_package": ckan_package,
    "url": url,
    "eso_map": eso_map,
    "elexon_remit": elexon_remit,
    "ocds_daily": ocds_daily,
    "gov_assets": gov_assets,
}
