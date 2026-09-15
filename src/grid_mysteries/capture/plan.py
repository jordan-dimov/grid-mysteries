"""The capture plan: which public resources the daily job copies, and how.

Data, not code. Each resource names a fetch strategy (`strategies.py`) and
the parameters it needs. Identifiers come from the investigations that
pinned them; a resource whose identifier is not in the repository is in
`TO_ADD`, with the investigation that will supply it, and is not fetched.
The job never parses what it captures.
"""

from dataclasses import dataclass, field
from typing import Final


@dataclass(frozen=True)
class Resource:
    name: str
    source: str
    resource: str
    strategy: str
    params: dict[str, str] = field(default_factory=dict)
    note: str = ""


NESO_TEC_REGISTER: Final = "17becbab-e3e8-473f-b303-3806f43a6a10"

PLAN: Final[tuple[Resource, ...]] = (
    # NESO data portal (CKAN): one resource_show plus the download per resource.
    Resource(
        "NESO-TEC-REGISTER",
        "neso",
        "tec-register",
        "ckan",
        {"resource_id": NESO_TEC_REGISTER},
        "005/014; the register NESO overwrites twice a week",
    ),
    Resource(
        "NESO-DAILY-BALANCING-COSTS-26-27",
        "neso",
        "daily-balancing-costs-2026-27",
        "ckan",
        {"resource_id": "1d040751-f77f-4641-9130-d49f8cbfe54f"},
        "013 L1",
    ),
    Resource(
        "NESO-DAILY-BALANCING-VOLUME-26-27",
        "neso",
        "daily-balancing-volume-2026-27",
        "ckan",
        {"resource_id": "e781da74-6c35-4296-81dd-250cee869c19"},
        "013 L4",
    ),
    Resource(
        "NESO-DISAGGREGATED-BSAD-26-27",
        "neso",
        "disaggregated-bsad-2026-27",
        "ckan",
        {"resource_id": "2be1a4d1-6b10-4c62-a01c-924942a3748f"},
        "013 L3",
    ),
    Resource(
        "NESO-DA-CONSTRAINT-FLOWS-LIMITS",
        "neso",
        "day-ahead-constraint-flows-and-limits",
        "ckan",
        {"resource_id": "38a18ec1-9e40-465d-93fb-301e80fd1352"},
        "003",
    ),
    Resource(
        "NESO-SKIP-INMERIT-ALLBM-2026-08",
        "neso",
        "skip-rates-inmerit-allbm-2026-08",
        "ckan",
        {"resource_id": "ce31e61b-ebc5-4c6f-846f-d5a971e019a0"},
        "method study 001b; monthly resource, a new id each month (see TO_ADD)",
    ),
    Resource(
        "NESO-SKIP-EXCLUSIONS-2026-08",
        "neso",
        "skip-rates-exclusions-2026-08",
        "ckan",
        {"resource_id": "a82a2a20-6f08-4d7d-a2ed-221527ba75c2"},
        "method study 001b; monthly resource",
    ),
    Resource(
        "NESO-EAC",
        "neso",
        "eac",
        "ckan",
        {"resource_id": "a63ab354-7e68-44c2-ad96-c6f920c30e85"},
        "011, identified by 008's reconnaissance",
    ),
    # Elexon Insights: REMIT messages published on the previous UTC day, then
    # each message by the detail URL the list itself gives.
    Resource(
        "ELEXON-REMIT",
        "elexon",
        "remit",
        "elexon_remit",
        {"base": "https://data.elexon.co.uk/bmrs/api/v1"},
        "update and withdrawal sequence per message; list then detail",
    ),
    # ESO (Bulgaria) map, moved verbatim from scripts/snapshot-eso-map.
    Resource(
        "ESO-MAP",
        "eso",
        "joining-map",
        "eso_map",
        {"base": "https://webapps.eso.bg/joining/public/map/api/"},
        "F004 O2 instrument",
    ),
    # Daily OCDS release packages for the previous UTC day.
    Resource(
        "CONTRACTS-FINDER-OCDS",
        "contracts-finder",
        "ocds-daily",
        "ocds_daily",
        {
            "template": (
                "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"
                "?publishedFrom={day}T00:00:00&publishedTo={day}T23:59:59&limit=100"
            )
        },
        "paged; every page captured",
    ),
    Resource(
        "FIND-A-TENDER-OCDS",
        "find-a-tender",
        "ocds-daily",
        "ocds_daily",
        {
            "template": (
                "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"
                "?updatedFrom={day}T00:00:00&updatedTo={day}T23:59:59&limit=100"
            )
        },
        "paged; every page captured",
    ),
    # DESNZ REPD: the publication page and every csv/xlsx asset it links.
    Resource(
        "DESNZ-REPD",
        "desnz",
        "repd-quarterly-extract",
        "gov_assets",
        {
            "url": (
                "https://www.gov.uk/government/publications/"
                "renewable-energy-planning-database-quarterly-extract"
            )
        },
        "quarterly; the page is captured daily so a new extract is caught the day it lands",
    ),
    # Octopus: the API product 010 pinned, and the terms pages that change silently.
    Resource(
        "OCTOPUS-AGILE-PRODUCT",
        "octopus",
        "product-agile-24-10-01",
        "url",
        {"url": "https://api.octopus.energy/v1/products/AGILE-24-10-01/"},
        "010",
    ),
    Resource(
        "OCTOPUS-SMART-TARIFF-TERMS",
        "octopus",
        "smart-tariffs-terms",
        "url",
        {"url": "https://octopus.energy/policies/smart-tariffs-terms-and-condition/"},
        "010 pinned by hand; the terms change silently",
    ),
    Resource(
        "OCTOPUS-AGILE-PAGE",
        "octopus",
        "smart-agile-page",
        "url",
        {"url": "https://octopus.energy/smart/agile/"},
        "010",
    ),
)

TO_ADD: Final[tuple[tuple[str, str], ...]] = (
    ("NESO connections queue snapshots", "no resource id pinned by any investigation yet"),
    ("NESO embedded register", "014 (the 2026-08-22 copy was fetched by hand; id to record)"),
    ("NESO constraint breakdown 2026-27", "013 follow-up; id not in the repository"),
    (
        "NESO skip-rate monthly resources",
        "a new resource id each month; a package_show listing strategy is part 3's follow-up",
    ),
    ("DNO connection registers", "when published; no URL pinned"),
    ("Companies House filings", "waits for the identity link table (move 3)"),
)


def by_name(name: str) -> Resource:
    for resource in PLAN:
        if resource.name == name:
            return resource
    raise KeyError(name)
