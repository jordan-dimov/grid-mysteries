"""011 — who loses eligibility: gated acquisition, instrument gate, screen.

Refuses to fetch unless invoked with ``--seal <prefix of DECLARATION.md's
SHA-256>`` so the human seal is on the record in the command that acquired
the data. Order is fixed by the declaration: documents → Elexon register →
instrument gate (schema and metadata only) → EAC results → population →
PN/MELS/MILS/BOALF for the population → the screen on both windows →
Companies House for the lead parties in the result. Every response is
journalled under data/raw/ before any value is read into the screen.

Documents are supplied at the seal as ``--document name=url`` (never typed
from memory); a declared name not supplied, or a 404, is recorded as
unavailable. The primary validity rule and forfeit scope are chosen from
the pinned documents and passed as ``--validity-rule`` / ``--forfeit-scope``
with ``--rule-note`` quoting the source; every rule and scope is computed
regardless.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import BMUNITS_PATH, REPO_ROOT, day_range, load_records
from grid_mysteries.investigations import eligibility_screen as es
from grid_mysteries.investigations.corporate_vitality import resolve
from grid_mysteries.sources import companies_house as ch
from grid_mysteries.sources import documents, elexon, neso
from grid_mysteries.sources.pinning import fetch_journalled, progress

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
DECLARATION = HERE / "DECLARATION.md"

WINDOWS: dict[str, tuple[date, date]] = {
    "post_rule": (date(2026, 8, 4), date(2026, 8, 31)),
    "counterfactual": (date(2026, 7, 3), date(2026, 7, 30)),
}
EFFECTIVE_DATE = date(2026, 7, 31)
GATE_PROBE_DAY = "2026-09-01"  # outside both windows; schema only
EAC_RESOURCE = "a63ab354-7e68-44c2-ad96-c6f920c30e85"  # identified by 008's reconnaissance
COMPLIANCE_QUERIES = (
    "dynamic containment performance",
    "dynamic response performance monitoring",
    "response services compliance",
    "baseline compliance",
    "frequency response delivery",
)
DECLARED_DOCUMENTS = (
    "ofgem-decision-page",
    "ofgem-decision-pdf",
    "neso-drs-consultation-2025-11",
    "neso-drs-final-submission",
    "neso-dc-service-terms",
    "neso-dm-service-terms",
    "neso-dr-service-terms",
    "grid-code-glossary-physical-notification",
    "bsc-section-q-physical-notifications",
    "bsc-gate-closure-definition",
)
IN_MERIT_FILES = ("inmerit_allbm_2026-07.csv", "inmerit_allbm_2026-08.csv")
STREAM_DATASETS = ("PN", "MELS", "MILS", "BOALF")
UNIT_CHUNK = 40

RAW_RULES = REPO_ROOT / "data/raw/rules/011"
RAW_ELEXON = REPO_ROOT / "data/raw/elexon/011"
RAW_NESO = REPO_ROOT / "data/raw/neso/011"


def declaration_digest() -> str:
    return hashlib.sha256(DECLARATION.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(), parse_float=Decimal)


def records_of(path: Path) -> list[dict]:
    payload = load_json(path)
    if isinstance(payload, dict):
        return payload.get("data", payload.get("result", []))
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, default=str, sort_keys=False) + "\n")


class Acquirer:
    def __init__(self, raw: Path, fetch) -> None:
        self.raw = raw
        self.fetch = fetch

    def pin(self, jobs: list[tuple[str, str, Path]], *, sleep: float = 0.2) -> None:
        fetch_journalled(
            jobs,
            journal_path=self.raw / "journal.ndjson",
            manifest_path=self.raw / "manifest.json",
            repo_root=REPO_ROOT,
            fetch=self.fetch,
            sleep_seconds=sleep,
            progress=progress,
        )

    def try_pin(self, dataset: str, url: str, destination: Path, log: dict, key: str) -> bool:
        try:
            self.pin([(dataset, url, destination)])
            return True
        except Exception as error:  # noqa: BLE001 — recorded, never guessed around
            log.setdefault("unavailable", {})[key] = {
                "url": url,
                "error": str(error).splitlines()[0],
            }
            return False


# --------------------------------------------------------------------------
# Phase 1: documents


def acquire_documents(supplied: dict[str, str], log: dict) -> None:
    acq = Acquirer(RAW_RULES, documents.fetch_pinned)
    log["documents"] = {}
    for name in DECLARED_DOCUMENTS:
        url = supplied.get(name)
        if not url:
            log["documents"][name] = {"state": "not supplied at seal"}
            continue
        destination = RAW_RULES / f"{name}{documents.suffix_for(url)}"
        ok = acq.try_pin("rules-document", url, destination, log, f"document:{name}")
        log["documents"][name] = {"state": "pinned" if ok else "unavailable", "url": url}
    for name, url in supplied.items():
        if name not in DECLARED_DOCUMENTS:
            destination = RAW_RULES / f"{name}{documents.suffix_for(url)}"
            ok = acq.try_pin("rules-document", url, destination, log, f"document:{name}")
            log["documents"][name] = {
                "state": "pinned" if ok else "unavailable",
                "url": url,
                "note": "supplied at seal beyond the declared list",
            }


# --------------------------------------------------------------------------
# Phase 2: register


def acquire_register() -> Path:
    destination = RAW_ELEXON / "bmunits.json"
    Acquirer(RAW_ELEXON, elexon.fetch_pinned).pin([("BMUNITS", elexon.bmunits_url(), destination)])
    return destination


def register_maps(path: Path) -> dict[str, Any]:
    records = records_of(path)
    ng_to_elexon = {
        str(r["nationalGridBmUnit"]): str(r["elexonBmUnit"])
        for r in records
        if r.get("nationalGridBmUnit")
    }
    by_elexon = {str(r["elexonBmUnit"]): r for r in records}
    differences = []
    if BMUNITS_PATH.exists():
        old = {str(r["elexonBmUnit"]): r for r in load_records(BMUNITS_PATH)}
        for unit, r in by_elexon.items():
            o = old.get(unit)
            if o and o.get("leadPartyName") != r.get("leadPartyName"):
                differences.append(
                    {"unit": unit, "001": o.get("leadPartyName"), "011": r.get("leadPartyName")}
                )
    return {
        "ng_to_elexon": ng_to_elexon,
        "lead_party": {u: r.get("leadPartyName") for u, r in by_elexon.items()},
        "lead_party_id": {u: r.get("leadPartyId") for u, r in by_elexon.items()},
        "fpn_flag": {u: r.get("fpnFlag") for u, r in by_elexon.items()},
        "generation_capacity": {u: r.get("generationCapacity") for u, r in by_elexon.items()},
        "fuel_type_counts": dict(Counter(str(r.get("fuelType")) for r in records)),
        "units": len(records),
        "lead_party_differences_vs_001_vintage": differences,
    }


# --------------------------------------------------------------------------
# Phase 3: instrument gate (schema and metadata only)


def instrument_gate(register: dict[str, Any], log: dict) -> dict[str, Any]:
    gate: dict[str, Any] = {"probe_day": GATE_PROBE_DAY, "note": "keys and counts only"}
    acq = Acquirer(RAW_ELEXON / "gate", elexon.fetch_pinned)
    fpn_units = sum(1 for v in register["fpn_flag"].values() if v)
    for dataset in ("PN", "MELS", "MILS"):
        dest = RAW_ELEXON / "gate" / f"{dataset.lower()}_{GATE_PROBE_DAY}_p01.json"
        if not acq.try_pin(
            dataset, elexon.physical_url(dataset, GATE_PROBE_DAY, 1), dest, log, f"gate:{dataset}"
        ):
            gate[dataset] = {"state": "no viable public instrument", "reason": "probe failed"}
            continue
        recs = records_of(dest)
        units = {str(r.get("bmUnit")) for r in recs}
        zero = sum(
            1
            for r in recs
            if Decimal(str(r.get("levelFrom", 0))) == 0 and Decimal(str(r.get("levelTo", 0))) == 0
        )
        gate[dataset] = {
            "fields": sorted(recs[0].keys()) if recs else [],
            "records": len(recs),
            "distinct_units": len(units),
            "registered_units": register["units"],
            "registered_units_with_fpn_flag": fpn_units,
            "zero_level_records": zero,
            "submission_timestamp_field": [
                k
                for k in (recs[0].keys() if recs else [])
                if "time" in k.lower() and k not in ("timeFrom", "timeTo")
            ],
            # Silence is distinguishable from a zero only if silent units are
            # absent from the series rather than back-filled with zeros.
            "absence_distinguishable_from_zero": len(units) < register["units"],
        }
        gate[dataset]["state"] = (
            "eligible now" if gate[dataset]["absence_distinguishable_from_zero"] else "proxy only"
        )
    dest = RAW_ELEXON / "gate" / f"boalf_{GATE_PROBE_DAY}_p01.json"
    if acq.try_pin("BOALF", elexon.acceptances_url(GATE_PROBE_DAY, 1), dest, log, "gate:BOALF"):
        recs = records_of(dest)
        gate["BOALF"] = {
            "fields": sorted(recs[0].keys()) if recs else [],
            "records": len(recs),
            "state": "eligible now (context)",
        }
    # Stream form of the same series, for the fields it carries.
    sample_units = [u for u in register["ng_to_elexon"].values()][:2]
    for dataset in STREAM_DATASETS:
        dest = RAW_ELEXON / "gate" / f"{dataset.lower()}_stream_{GATE_PROBE_DAY}.json"
        if acq.try_pin(
            dataset,
            elexon.day_stream_url(dataset, GATE_PROBE_DAY, sample_units),
            dest,
            log,
            f"gate:{dataset}-stream",
        ):
            recs = records_of(dest)
            gate.setdefault("stream", {})[dataset] = {
                "fields": sorted(recs[0].keys()) if recs else [],
                "records": len(recs),
                "units_requested": sample_units,
                "units_returned": sorted({str(r.get("bmUnit")) for r in recs}),
            }
    # G4: EAC fields without values.
    nacq = Acquirer(RAW_NESO / "gate", neso.fetch_pinned)
    dest = RAW_NESO / "gate" / "eac-fields.json"
    if nacq.try_pin(
        "NESO-EAC-FIELDS", neso.datastore_fields_url(EAC_RESOURCE), dest, log, "gate:EAC"
    ):
        result = load_json(dest).get("result", {})
        fields = [f.get("id") for f in result.get("fields", [])]
        needed = {
            "auctionUnit",
            "serviceType",
            "auctionProduct",
            "executedQuantity",
            "clearingPrice",
            "deliveryStart",
            "deliveryEnd",
            "technologyType",
        }
        gate["EAC"] = {
            "fields": fields,
            "total_rows": result.get("total"),
            "missing_fields": sorted(needed - set(fields)),
            "state": "eligible now" if needed <= set(fields) else "proxy only",
        }
    # G5: is there any per-BMU compliance or performance series?
    gate["compliance"] = {"queries": {}, "candidates": []}
    for query in COMPLIANCE_QUERIES:
        slug = re.sub(r"[^a-z0-9]+", "-", query)
        dest = RAW_NESO / "gate" / f"search-{slug}.json"
        if not nacq.try_pin(
            "NESO-PACKAGE-SEARCH", neso.package_search_url(query), dest, log, f"gate:search:{slug}"
        ):
            continue
        result = load_json(dest).get("result", {})
        packages = []
        for pkg in result.get("results", []):
            packages.append(pkg.get("name"))
            for res in pkg.get("resources", []):
                text = " ".join(
                    str(x)
                    for x in (
                        pkg.get("name"),
                        pkg.get("title"),
                        res.get("name"),
                        res.get("description"),
                    )
                ).lower()
                if any(w in text for w in ("performance", "compliance", "delivery", "monitoring")):
                    gate["compliance"]["candidates"].append(
                        {
                            "package": pkg.get("name"),
                            "resource": res.get("name"),
                            "id": res.get("id"),
                            "format": res.get("format"),
                        }
                    )
        gate["compliance"]["queries"][query] = {"count": result.get("count"), "packages": packages}
    seen: set[str] = set()
    per_bmu = []
    for cand in gate["compliance"]["candidates"][:10]:
        rid = cand.get("id")
        if not rid or rid in seen:
            continue
        seen.add(rid)
        dest = RAW_NESO / "gate" / f"fields-{rid}.json"
        if nacq.try_pin(
            "NESO-FIELDS", neso.datastore_fields_url(rid), dest, log, f"gate:fields:{rid}"
        ):
            fields = [str(f.get("id")) for f in load_json(dest).get("result", {}).get("fields", [])]
            cand["fields"] = fields
            lowered = " ".join(fields).lower()
            cand["per_bmu"] = any(w in lowered for w in ("bmu", "unit")) and any(
                w in lowered
                for w in ("performance", "compliance", "availability", "score", "delivered")
            )
            if cand["per_bmu"]:
                per_bmu.append(cand["resource"])
    gate["compliance"]["state"] = (
        f"candidate per-BMU series found, human review required: {per_bmu}"
        if per_bmu
        else "no viable public instrument"
    )
    gate["register"] = {"state": "eligible now", "units": register["units"]}
    return gate


# --------------------------------------------------------------------------
# Phase 4: EAC results


def acquire_eac(log: dict) -> list[Path]:
    acq = Acquirer(RAW_NESO, neso.fetch_pinned)
    show = RAW_NESO / "eac-resource-show.json"
    acq.pin([("NESO-EAC-RESOURCE", neso.resource_show_url(EAC_RESOURCE), show)])
    package_id = load_json(show)["result"]["package_id"]
    listing = RAW_NESO / "eac-package-show.json"
    acq.pin([("NESO-EAC-PACKAGE", neso.package_show_url(package_id), listing)])
    resources = load_json(listing)["result"]["resources"]
    log["eac_package"] = {"package_id": package_id, "resources": [r.get("name") for r in resources]}
    chosen: list[tuple[str, str]] = []
    for month, words in (
        ("2026-07", ("2026-07", "jul", "july")),
        ("2026-08", ("2026-08", "aug", "august")),
    ):
        for res in resources:
            name = str(res.get("name", "")).lower()
            if "2026" in name and any(w in name for w in words) and res.get("id") != EAC_RESOURCE:
                chosen.append((f"eac-archive-{month}", res["id"]))
                break
    if len(chosen) < 2:
        chosen = [("eac-live", EAC_RESOURCE)]
    log["eac_resources_pinned"] = chosen
    paths = []
    for name, rid in chosen:
        dest = RAW_NESO / f"{name}.csv"
        acq.pin([(f"NESO-EAC-{name}", neso.dump_url(rid), dest)], sleep=0)
        paths.append(dest)
    return paths


def eac_rows(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        rows.extend(neso.read_csv_path(path))
    return rows


def rows_in(rows: list[dict], start: date, end: date) -> list[dict]:
    # Delivery starts are compared as text on the date prefix; a day either
    # side is kept so basis inference and period mapping never clip a block.
    lo = (start - timedelta(days=1)).isoformat()
    hi = (end + timedelta(days=1)).isoformat()
    return [r for r in rows if lo <= str(r.get("deliveryStart", ""))[:10] <= hi]


# --------------------------------------------------------------------------
# Phase 5: population


def in_merit_batteries() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for name in IN_MERIT_FILES:
        path = neso.NESO_RAW / name
        if not path.exists():
            continue
        with path.open(newline="") as handle:
            units = {
                row["bm_unit"] for row in csv.DictReader(handle) if row.get("fuel") == "BATTERY"
            }
        out[name] = sorted(units)
    return out


def build_population(rows: list[dict], register: dict[str, Any], basis: str) -> dict[str, Any]:
    start, end = WINDOWS["post_rule"]
    window_rows = rows_in(rows, start, end)
    eac_batteries = {
        str(r["auctionUnit"])
        for r in window_rows
        if "batter" in str(r.get("technologyType", "")).lower()
    }
    in_merit = in_merit_batteries()
    in_merit_set = {u for units in in_merit.values() for u in units}
    holders = {
        str(r["auctionUnit"])
        for r in window_rows
        if es.response_family(r.get("serviceType"), r.get("auctionProduct"))
        and Decimal(str(r.get("executedQuantity") or 0)) > 0
    }
    ng_to_elexon = register["ng_to_elexon"]
    members, unmapped = [], []
    for ng in sorted(holders):
        labels = {"eac_batteries": ng in eac_batteries, "in_merit_battery": ng in in_merit_set}
        if not any(labels.values()):
            continue
        elexon_id = ng_to_elexon.get(ng)
        entry = {
            "ng_unit": ng,
            "elexon_unit": elexon_id,
            **labels,
            "lead_party": register["lead_party"].get(elexon_id or ""),
        }
        (members if elexon_id else unmapped).append(entry)
    return {
        "rule": (
            "holds >= 1 accepted response position in the post-rule window "
            "and is a battery by EAC technologyType or in-merit fuel"
        ),
        "window": {"from": start.isoformat(), "to": end.isoformat()},
        "timestamp_basis": basis,
        "holders_any_technology": len(holders),
        "units": members,
        "unmapped": unmapped,
        "classification_disagreements": [
            m for m in members if m["eac_batteries"] != m["in_merit_battery"]
        ],
        "in_merit_files_read": {k: len(v) for k, v in in_merit.items()},
    }


# --------------------------------------------------------------------------
# Phase 6: physical data for the population


def acquire_physical(units: list[str], log: dict) -> None:
    acq = Acquirer(RAW_ELEXON, elexon.fetch_pinned)
    chunks = [units[i : i + UNIT_CHUNK] for i in range(0, len(units), UNIT_CHUNK)]
    for window, (start, end) in WINDOWS.items():
        # One UTC day earlier too: a BST settlement day begins at 23:00Z the day before.
        days = day_range(start - timedelta(days=1), (end - start).days + 2)
        for day in days:
            for dataset in STREAM_DATASETS:
                for n, chunk in enumerate(chunks, 1):
                    dest = RAW_ELEXON / window / day / f"{dataset.lower()}_c{n:02d}.json"
                    acq.try_pin(
                        dataset,
                        elexon.day_stream_url(dataset, day, chunk),
                        dest,
                        log,
                        f"physical:{window}:{day}:{dataset}:{n}",
                    )
    write_json(EVIDENCE / "unit-chunks.json", chunks)


def stream_records(window: str, dataset: str) -> list[dict]:
    out: list[dict] = []
    seen: set[tuple] = set()
    for path in sorted((RAW_ELEXON / window).glob(f"*/{dataset.lower()}_c*.json")):
        for r in records_of(path):
            key = (
                r.get("bmUnit"),
                r.get("settlementDate"),
                r.get("settlementPeriod"),
                r.get("timeFrom"),
                r.get("timeTo"),
                r.get("acceptanceNumber"),
            )
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
    return out


# --------------------------------------------------------------------------
# Phase 7: the screen


def context(window: str, result: dict, units: list[str]) -> dict[str, Any]:
    """For the periods deemed unavailable: was the unit declaring capability
    (MEL > 0 or MIL < 0), and was it being dispatched (a BOA)?"""
    capable: dict[tuple[str, str, int], bool] = defaultdict(bool)
    for dataset, sign in (("MELS", 1), ("MILS", -1)):
        for r in stream_records(window, dataset):
            level = max(
                Decimal(str(r.get("levelFrom", 0))) * sign, Decimal(str(r.get("levelTo", 0))) * sign
            )
            key = (str(r["bmUnit"]), str(r["settlementDate"])[:10], int(r["settlementPeriod"]))
            capable[key] = capable[key] or level > 0
    boa: set[tuple[str, str, int]] = set()
    for r in stream_records(window, "BOALF"):
        try:
            boa.add((str(r["bmUnit"]), str(r["settlementDate"])[:10], int(r["settlementPeriod"])))
        except KeyError, ValueError, TypeError:
            continue
    out = {}
    for unit, u in result["units"].items():
        periods = u["unavailable_periods"]
        if not periods:
            continue
        keys = [(unit, p["settlement_date"], p["period"]) for p in periods]
        out[unit] = {
            "unavailable_periods": len(keys),
            "declared_capable": sum(1 for k in keys if capable.get(k)),
            "with_boa": sum(1 for k in keys if k in boa),
        }
    return out


def evaluate(
    rows: list[dict], register: dict[str, Any], population: dict[str, Any], args
) -> dict[str, Any]:
    units = [m["elexon_unit"] for m in population["units"]]
    basis = population["timestamp_basis"]
    results: dict[str, Any] = {"windows": {}}
    for window, (start, end) in WINDOWS.items():
        built = es.positions_from_eac_rows(
            rows_in(rows, start, end), unit_map=register["ng_to_elexon"], basis=basis
        )
        pn = [
            es.pn_from_record(r)
            for r in stream_records(window, "PN")
            if str(r.get("bmUnit")) in set(units)
        ]
        request = {
            "window": {"from": start.isoformat(), "to": end.isoformat()},
            "units": units,
            "validity_rule": args.validity_rule,
            "forfeit_scope": args.forfeit_scope,
        }
        result = es.screen(request, pn, built["positions"])
        parties = es.concentration(result, register["lead_party"])
        results["windows"][window] = {
            "label": "post-rule (test)" if window == "post_rule" else "counterfactual (pre-rule)",
            "screen": result,
            "context": context(window, result, units),
            "concentration_by_lead_party": parties,
            "milestone_cleared": es.milestone(parties),
            "positions": {
                "count": len(built["positions"]),
                "skipped": built["skipped"],
                "unmapped_units": built["unmapped_units"],
                "service_vocabulary": built["service_vocabulary"],
            },
            "pn_records": len(pn),
        }
    return results


# --------------------------------------------------------------------------
# Phase 8: owners (Companies House)


def acquire_owners(
    results: dict[str, Any], register: dict[str, Any], run_date: str, log: dict
) -> dict[str, Any]:
    key = os.environ.get(ch.KEY_ENV) or os.environ.get("CH_API_KEY", "")
    if not key:
        log["owners"] = "no Companies House key in the environment; owners not resolved"
        return {}
    fetch = ch.AuthenticatedFetcher(key)
    raw = REPO_ROOT / "data/raw/companies-house" / f"{run_date}-011"
    acq = Acquirer(raw, fetch)
    parties = [
        p
        for p in results["windows"]["post_rule"]["concentration_by_lead_party"]
        if Decimal(p["revenue_at_stake_gbp"]) > 0 and p["party"] != "unknown"
    ][:10]
    out: dict[str, Any] = {}
    start = WINDOWS["post_rule"][0]
    for p in parties:
        name = p["party"]
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:80]
        dest = raw / "search" / f"{slug}.json"
        if not acq.try_pin("ch-search", ch.search_url(name), dest, log, f"ch:search:{slug}"):
            continue
        hits = load_json(dest).get("items", [])
        resolution = resolve(name, hits, [], {}, first_observed=start)
        entry: dict[str, Any] = {
            "lead_party": name,
            "company_number": resolution.company_number,
            "reason": resolution.reason,
            "candidates": list(resolution.candidates),
        }
        if resolution.company_number:
            pdest = raw / "company" / resolution.company_number / "profile.json"
            if acq.try_pin(
                "ch-profile",
                ch.profile_url(resolution.company_number),
                pdest,
                log,
                f"ch:profile:{resolution.company_number}",
            ):
                profile = load_json(pdest)
                entry["profile"] = {
                    k: profile.get(k)
                    for k in (
                        "company_name",
                        "company_status",
                        "date_of_creation",
                        "type",
                        "sic_codes",
                    )
                }
        out[name] = entry
    return out


# --------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seal", required=True, help="prefix (≥ 8 hex) of DECLARATION.md's SHA-256"
    )
    parser.add_argument("--run-date", default=datetime.now(UTC).date().isoformat())
    parser.add_argument(
        "--phase",
        choices=(
            "documents",
            "register",
            "gate",
            "eac",
            "population",
            "physical",
            "evaluate",
            "owners",
            "all",
        ),
        default="all",
    )
    parser.add_argument(
        "--document",
        action="append",
        default=[],
        help="name=url of a declared document, supplied at the seal",
    )
    parser.add_argument("--validity-rule", choices=es.VALIDITY_RULES, default="covering")
    parser.add_argument("--forfeit-scope", choices=es.FORFEIT_SCOPES, default="period")
    parser.add_argument(
        "--rule-note", help="the pinned words that selected the primary rule and scope"
    )
    parser.add_argument("--note", action="append", default=[])
    args = parser.parse_args()

    digest = declaration_digest()
    if len(args.seal) < 8 or not digest.startswith(args.seal.lower()):
        print(
            f"seal {args.seal!r} does not match DECLARATION.md sha256 {digest}; refusing",
            file=sys.stderr,
        )
        return 2
    date.fromisoformat(args.run_date)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    log_path = EVIDENCE / "acquisition-log.json"
    log: dict[str, Any] = json.loads(log_path.read_text()) if log_path.exists() else {}
    log.update(
        {
            "declaration_sha256": digest,
            "seal": args.seal,
            "run_date": args.run_date,
            "effective_date": EFFECTIVE_DATE.isoformat(),
        }
    )
    log.setdefault("notes", []).extend(args.note)
    if args.rule_note:
        log["primary_rule"] = {
            "validity_rule": args.validity_rule,
            "forfeit_scope": args.forfeit_scope,
            "note": args.rule_note,
        }
    phases = (
        {args.phase}
        if args.phase != "all"
        else {
            "documents",
            "register",
            "gate",
            "eac",
            "population",
            "physical",
            "evaluate",
            "owners",
        }
    )

    try:
        if "documents" in phases:
            acquire_documents(dict(item.split("=", 1) for item in args.document), log)
        register_path = RAW_ELEXON / "bmunits.json"
        if "register" in phases:
            register_path = acquire_register()
        register = register_maps(register_path) if register_path.exists() else None
        if "gate" in phases:
            assert register, "register must be pinned before the gate"
            write_json(EVIDENCE / "instrument-gate.json", instrument_gate(register, log))
        eac_paths = sorted(RAW_NESO.glob("eac-*.csv"))
        if "eac" in phases:
            eac_paths = acquire_eac(log)
        rows = eac_rows(eac_paths) if eac_paths and phases & {"population", "evaluate"} else []
        if "population" in phases:
            assert register
            starts = []
            for r in rows_in(rows, *WINDOWS["post_rule"]):
                try:
                    starts.append(es.parse_timestamp(r["deliveryStart"]))
                except KeyError, ValueError:
                    continue
            inference = es.infer_timestamp_basis(starts)
            log["timestamp_basis"] = inference
            basis = inference["basis"] if inference["basis"] in ("utc", "local") else "utc"
            if inference["basis"] not in ("utc", "local"):
                log.setdefault("notes", []).append(
                    f"timestamp basis {inference['basis']}; utc assumed and flagged"
                )
            write_json(EVIDENCE / "population.json", build_population(rows, register, basis))
        population = (
            load_json(EVIDENCE / "population.json")
            if (EVIDENCE / "population.json").exists()
            else None
        )
        if "physical" in phases:
            assert population
            acquire_physical([m["elexon_unit"] for m in population["units"]], log)
        if "evaluate" in phases:
            assert register and population
            results = evaluate(rows, register, population, args)
            results["rule"] = es.RULE
            results["declaration_sha256"] = digest
            results["primary_rule"] = log.get("primary_rule")
            write_json(EVIDENCE / "results.json", results)
            for window, w in results["windows"].items():
                t = w["screen"]["totals"]
                print(
                    window,
                    json.dumps(
                        {
                            k: t[k]
                            for k in (
                                "units_holding",
                                "units_with_any_unavailable",
                                "periods_at_risk",
                                "revenue_held_gbp",
                                "revenue_at_stake_gbp",
                                "share_of_revenue_held",
                            )
                        }
                    ),
                )
        if "owners" in phases and (EVIDENCE / "results.json").exists():
            assert register
            write_json(
                EVIDENCE / "owners.json",
                acquire_owners(load_json(EVIDENCE / "results.json"), register, args.run_date, log),
            )
    finally:
        manifest = []
        for raw in (
            RAW_RULES,
            RAW_ELEXON,
            RAW_ELEXON / "gate",
            RAW_NESO,
            RAW_NESO / "gate",
            REPO_ROOT / "data/raw/companies-house" / f"{args.run_date}-011",
        ):
            path = raw / "manifest.json"
            if path.exists():
                manifest.extend(json.loads(path.read_text()))
        write_json(EVIDENCE / "manifest.json", sorted(manifest, key=lambda e: e["path"]))
        write_json(log_path, log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
