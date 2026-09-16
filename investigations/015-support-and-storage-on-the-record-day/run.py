"""015 — support and storage on the record day: gated runner.

    uv run python investigations/015-support-and-storage-on-the-record-day/run.py \\
        --seal <prefix of DECLARATION.md's SHA-256> --phase acquire
    uv run python investigations/015-support-and-storage-on-the-record-day/run.py --phase compute

``acquire`` (needs the seal) pins, once and journalled: LCCC's CfD-to-BM-unit
mapping and contract portfolio (datastore dumps, CSV resources, definitions,
resource_show metadata), Ofgem's Renewable Electricity Register public
reports dashboard and its *Accredited Stations (RO)* CSV, and Elexon's MDO
and MDB day streams for 2026-09-08. ``compute`` reads only pinned bytes,
012's and 003's committed manifests and ``evidence/reading.json`` (the
column bindings from the schema pass), and writes the evidence and
``RESULTS.md``. Idempotent over pinned bytes.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import httpx

from grid_mysteries.corpus import REPO_ROOT, load_records
from grid_mysteries.evidence import write_json
from grid_mysteries.hashing import sha256_file
from grid_mysteries.sources import elexon
from grid_mysteries.sources.http import fetch_artifact
from grid_mysteries.sources.pinning import load_journal, pin, progress

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
DECLARATION = HERE / "DECLARATION.md"
DAY = "2026-09-08"
RAW_LCCC = REPO_ROOT / "data" / "raw" / "lccc" / "015"
RAW_OFGEM = REPO_ROOT / "data" / "raw" / "ofgem" / "015"
RAW_ELEXON = REPO_ROOT / "data" / "raw" / "elexon" / "015"
RAW_012 = REPO_ROOT / "data" / "raw" / "elexon" / "012"
CMIS = REPO_ROOT / "data" / "raw" / "neso" / "cmis_arming_2026-27.csv"
TEC_COPY = REPO_ROOT / "data" / "raw" / "neso" / "tec-history" / "2026-09-15_neso-ckan.csv"
LCCC_API = "https://dp.lowcarboncontracts.uk/api/3/action"
LCCC = {
    "LCCC-CFD-BMU-MAPPING": "c16f141d-2db9-4160-ade1-d0d19d224dc9",
    "LCCC-CFD-BMU-MAPPING-CSV": "26fc2b66-7c92-45d4-9a70-acbd1631f4c3",
    "LCCC-CFD-BMU-MAPPING-DEFINITIONS": "d49acec2-cab0-4342-8bac-b77cba8bf092",
    "LCCC-CFD-PORTFOLIO": "fdaf09d2-8cff-4799-a5b0-1c59444e492b",
    "LCCC-CFD-PORTFOLIO-CSV": "7bdfb0cb-fe99-44eb-b07b-2047e82f5601",
    "LCCC-CFD-PORTFOLIO-DEFINITIONS": "b6fed2c0-e679-4c02-8716-dbd0caa100dd",
}
RER_DASHBOARD = "https://rer.ofgem.gov.uk/Reports/Dashboard"
UA = "grid-mysteries-015/1 (research; jdimov@a115.co.uk)"


def declaration_digest() -> str:
    return hashlib.sha256(DECLARATION.read_bytes()).hexdigest()


def require_seal(seal: str | None) -> str:
    digest = declaration_digest()
    if not seal or len(seal) < 8 or not digest.startswith(seal.lower()):
        raise SystemExit(
            f"refusing: --seal must be a prefix of DECLARATION.md's SHA-256 {digest[:16]}…"
        )
    return digest


def journal(name: str) -> dict[str, Path]:
    return {
        "journal_path": EVIDENCE / f"{name}-journal.ndjson",
        "manifest_path": EVIDENCE / f"{name}-manifest.json",
    }


def fetch_lccc(*, url: str, destination: Path, dataset: str):
    return fetch_artifact(url=url, destination=destination, source="lccc", dataset=dataset)


def fetch_browserlike(*, url: str, destination: Path, dataset: str):
    """Ofgem's dashboard and SharePoint links need a browser-like agent and a
    cookie jar across redirects; otherwise the same immutable pinning."""
    from grid_mysteries.models import SourceArtifact

    if destination.exists():
        raise FileExistsError(
            f"pinned artefact already exists, refusing to overwrite: {destination}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=120, follow_redirects=True, headers={"User-Agent": UA}) as client:
        response = client.get(url)
        response.raise_for_status()
        destination.write_bytes(response.content)
    return SourceArtifact(
        source="ofgem",
        dataset=dataset,
        path=destination,
        sha256=sha256_file(destination),
        fetched_at=datetime.now(UTC),
    )


def acquire() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    jobs = []
    for dataset, rid in LCCC.items():
        jobs.append(
            (
                f"{dataset}-META",
                f"{LCCC_API}/resource_show?id={rid}",
                RAW_LCCC / f"{rid}.resource_show.json",
            )
        )
        if dataset.endswith("-CSV") or dataset.endswith("-DEFINITIONS"):
            meta = httpx.get(
                f"{LCCC_API}/resource_show?id={rid}", timeout=60, headers={"User-Agent": UA}
            ).json()["result"]
            jobs.append((dataset, meta["url"], RAW_LCCC / f"{rid}.csv"))
        else:
            jobs.append(
                (
                    dataset,
                    f"https://dp.lowcarboncontracts.uk/datastore/dump/{rid}",
                    RAW_LCCC / f"{rid}.dump.csv",
                )
            )
    pin(jobs, fetch=fetch_lccc, label="lccc", progress=progress, **journal("lccc"))
    # Ofgem: the dashboard page first (provenance of the link), then the RO stations CSV it links.
    dash = RAW_OFGEM / "rer-reports-dashboard.html"
    pin(
        [("OFGEM-RER-DASHBOARD", RER_DASHBOARD, dash)],
        fetch=fetch_browserlike,
        label="ofgem",
        progress=progress,
        **journal("ofgem"),
    )
    html = dash.read_text(errors="replace")
    links = re.findall(
        r'<a href="(https://ofgemcloud\.sharepoint\.com/[^"]+)">\s*Download\s*</a>', html
    )
    if len(links) < 2:
        raise SystemExit("F0: the dashboard did not expose the download links; pin the CSV by hand")
    # The second Download on the dashboard is Accredited Stations (RO); the
    # served file name (RO_Accredited_Stations_<date>_05-00.csv) confirms it.
    ro_link = links[1]
    pin(
        [("OFGEM-RO-ACCREDITED-STATIONS", ro_link, RAW_OFGEM / "ro-accredited-stations.csv")],
        fetch=fetch_browserlike,
        label="ofgem",
        progress=progress,
        **journal("ofgem"),
    )
    jobs = [
        (ds, elexon.day_stream_url(ds, DAY), RAW_ELEXON / f"{ds.lower()}_{DAY}.json")
        for ds in ("MDO", "MDB")
    ]
    pin(jobs, fetch=elexon.fetch_pinned, label="elexon", progress=progress, **journal("elexon"))
    print("acquired; now the schema pass (scripts/schema-report csv …), then evidence/reading.json")


# ------------------------------------------------------------------ compute


def read_csv(path: Path) -> list[dict[str, str]]:
    import csv

    with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def compute() -> None:
    from grid_mysteries.investigations import support_and_storage as ss

    reading = json.loads((EVIDENCE / "reading.json").read_text())
    register = {r["elexonBmUnit"]: r for r in load_records(RAW_012 / "bmunits.json")}
    bids = load_records(RAW_012 / DAY / "ebocf_bid.json")
    offers = load_records(RAW_012 / DAY / "ebocf_offer.json")
    disptav = {
        (direction, period): load_records(RAW_012 / DAY / f"disptav_{direction}_p{period:02d}.json")
        for direction in ("bid", "offer")
        for period in range(1, 49)
    }
    prices = load_records(RAW_012 / DAY / "system-prices.json")
    mapping = read_csv(RAW_LCCC / f"{LCCC['LCCC-CFD-BMU-MAPPING']}.dump.csv")
    portfolio = read_csv(RAW_LCCC / f"{LCCC['LCCC-CFD-PORTFOLIO']}.dump.csv")
    ro = read_csv(RAW_OFGEM / "ro-accredited-stations.csv")
    cmis = read_csv(CMIS)
    tec = read_csv(TEC_COPY)
    mdo = load_records(RAW_ELEXON / f"mdo_{DAY}.json")
    mdb = load_records(RAW_ELEXON / f"mdb_{DAY}.json")
    result = ss.run(
        day=date.fromisoformat(DAY),
        register=register,
        bids=bids,
        offers=offers,
        disptav=disptav,
        prices=prices,
        mapping=mapping,
        portfolio=portfolio,
        ro=ro,
        cmis=cmis,
        tec=tec,
        mdo=mdo,
        mdb=mdb,
        reading=reading,
    )
    manifests: list[dict[str, Any]] = []
    for name in ("lccc", "ofgem", "elexon"):
        manifests += list(load_journal(journal(name)["journal_path"]).values())
    result["declaration_sha256"] = declaration_digest()
    result["computed_at"] = datetime.now(UTC).isoformat(timespec="seconds")
    result["artefacts_acquired"] = [
        {"dataset": e["dataset"], "path": e["path"], "sha256": e["sha256"]} for e in manifests
    ]
    write_json(EVIDENCE / "links.json", result.pop("links"))
    write_json(EVIDENCE / "wind-by-scheme.json", result.pop("wind"))
    write_json(EVIDENCE / "storage.json", result.pop("storage"))
    write_json(EVIDENCE / "summary.json", result)
    print(json.dumps({k: result[k] for k in ("propositions", "constraint")}, indent=1, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seal")
    parser.add_argument("--phase", choices=("acquire", "compute"), required=True)
    args = parser.parse_args()
    if args.phase == "acquire":
        require_seal(args.seal)
        acquire()
    else:
        compute()


if __name__ == "__main__":
    sys.exit(main())
