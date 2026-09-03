"""010 — the household desk: gated acquisition and the declared case grid.

Refuses to fetch unless invoked with ``--seal <prefix of DECLARATION.md's
SHA-256>`` so the human seal is on the record in the command that acquired
the data. Order is fixed by the declaration: products index → product
documents → unit rates and standing charges → Elexon → backtests → rules
documents (read only after the numbers exist). Every response is
journalled under data/raw/ before any price is read into the model.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from itertools import product
from pathlib import Path
from typing import Any

from grid_mysteries.corpus import REPO_ROOT, day_range
from grid_mysteries.hashing import sha256_file
from grid_mysteries.investigations import household_desk as hd
from grid_mysteries.investigations.household_desk import LONDON, BatterySpec, Rate
from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources import elexon, octopus
from grid_mysteries.sources.pinning import fetch_journalled, progress

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"
DECLARATION = HERE / "DECLARATION.md"

REGIONS = ("C", "E", "J")
WINDOWS = {
    "summer": (date(2026, 6, 1), date(2026, 8, 31), "2026-05-31T21:00Z", "2026-09-01T00:00Z"),
    "winter": (date(2026, 1, 1), date(2026, 2, 28), "2025-12-31T22:00Z", "2026-03-01T00:00Z"),
}
HEADLINE = ("AGILE-24-10-01", "AGILE-OUTGOING-19-05-13")
EXPORT_LIMITS = {"g99-20kw": Decimal("20"), "g98-3ph": Decimal("11.04"), "g98-1ph": Decimal("3.68")}
DEGRADATION = (Decimal("0"), Decimal("2"), Decimal("5"))
FREE_SWEEP = tuple(Decimal(x) for x in (0, 10, 20, 30, 40, 60, 80, 100))
CAPACITY, INVERTER, EFFICIENCY = Decimal("200"), Decimal("20"), Decimal("0.90")
BLOOMBERG_DAY = date(2026, 6, 24)

#: Sources deliberately not fetched, with the reason, so the record shows
#: the gap rather than a browser-agent workaround.
RULES_NOT_ATTEMPTED = {
    "ukpn-g98-g99-pages": "UK Power Networks refuses scripted fetches; recorded as unavailable "
    "at the sponsor's instruction rather than retried with a browser agent",
}

RULES_DOCUMENTS = {
    "octopus-agile": "https://octopus.energy/smart/agile/",
    "octopus-agile-pricing-explained": "https://octopus.energy/blog/agile-pricing-explained/",
    "octopus-outgoing": "https://octopus.energy/smart/outgoing/",
    "octopus-go": "https://octopus.energy/go/",
    "octopus-intelligent-go": "https://octopus.energy/smart/intelligent-octopus-go/",
    "octopus-flux": "https://octopus.energy/smart/flux/",
    "octopus-intelligent-flux": "https://octopus.energy/smart/intelligent-flux/",
    # ENA library pages supplied by the sponsor at seal (the earlier
    # /industry/... path returned 404); G99 untested from here.
    "ena-erec-g98": "https://www.energynetworks.org/publications/engineering-recommendation-g98",
    "ena-erec-g99": "https://www.energynetworks.org/publications/engineering-recommendation-g99",
    "distribution-code": "https://www.dcode.org.uk/",
    "hmrc-vat-701-19": "https://www.gov.uk/guidance/vat-on-fuel-and-power-notice-70119",
}


def declaration_digest() -> str:
    return hashlib.sha256(DECLARATION.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(), parse_float=Decimal)


class Acquirer:
    def __init__(self, raw: Path, fetch) -> None:
        self.raw = raw
        self.fetch = fetch
        self.journal = raw / "journal.ndjson"
        self.manifest = raw / "manifest.json"

    def pin(self, jobs: list[tuple[str, str, Path]]) -> None:
        fetch_journalled(
            jobs,
            journal_path=self.journal,
            manifest_path=self.manifest,
            repo_root=REPO_ROOT,
            fetch=self.fetch,
            sleep_seconds=0.2,
            progress=progress,
        )

    def pin_pages(self, dataset: str, first_url: str, folder: Path) -> list[Path]:
        """Follow the API's own `next` links, one pinned file per page."""
        pages: list[Path] = []
        url: str | None = first_url
        number = 1
        while url:
            destination = folder / f"page-{number}.json"
            self.pin([(dataset, url, destination)])
            pages.append(destination)
            url = octopus.next_page(load_json(destination))
            number += 1
        return pages


def acquire_octopus(acq: Acquirer, log: dict[str, Any]) -> dict[tuple[str, str], str]:
    """Phases 1–3. Returns the tariff code actually pinned per (product, region)."""
    acq.pin_pages("octopus-products", octopus.products_url(), acq.raw / "products")
    index = {
        str(item.get("code"))
        for page in sorted((acq.raw / "products").glob("page-*.json"))
        for item in load_json(page).get("results", [])
    }
    codes: dict[tuple[str, str], str] = {}
    for prod in (*octopus.IMPORT_PRODUCTS, *octopus.EXPORT_PRODUCTS):
        if prod not in index:
            log.setdefault("products_absent_from_index", []).append(prod)
        destination = acq.raw / "product" / f"{prod}.json"
        try:
            acq.pin([("octopus-product", octopus.product_url(prod), destination)])
        except Exception as error:  # noqa: BLE001 — recorded, never guessed around
            log.setdefault("product_documents_unavailable", {})[prod] = str(error)
            continue
        document = load_json(destination)
        for region in REGIONS:
            found = octopus.tariff_codes_in_product(document, region)
            expected = octopus.tariff_code(prod, region)
            if not found:
                log.setdefault("tariff_missing", []).append(f"{prod}/{region}")
                continue
            if found != [expected]:
                log.setdefault("tariff_code_differs", {})[f"{prod}/{region}"] = found
            codes[(prod, region)] = expected if expected in found else found[0]
    for (prod, region), code in sorted(codes.items()):
        for window, (_, _, pf, pt) in WINDOWS.items():
            folder = acq.raw / "rates" / prod / region / window
            acq.pin_pages(
                "octopus-standard-unit-rates", octopus.unit_rates_url(prod, code, pf, pt), folder
            )
            acq.pin_pages(
                "octopus-standing-charges",
                octopus.standing_charges_url(prod, code, pf, pt),
                acq.raw / "standing" / prod / region / window,
            )
    return codes


def acquire_elexon(acq: Acquirer) -> None:
    jobs: list[tuple[str, str, Path]] = []
    for start, end, _, _ in WINDOWS.values():
        for day in day_range(start, (end - start).days + 1):
            folder = acq.raw / day
            jobs.append(("MID", elexon.day_stream_url("MID", day), folder / "mid.json"))
            jobs.append(
                ("SYSTEM-PRICES", elexon.system_prices_url(day), folder / "system-prices.json")
            )
    acq.pin(jobs)


def acquire_rules(acq: Acquirer, extra: dict[str, str], log: dict[str, Any]) -> None:
    log["rules_documents_not_attempted"] = RULES_NOT_ATTEMPTED
    for name, url in {**RULES_DOCUMENTS, **extra}.items():
        suffix = ".pdf" if url.lower().endswith(".pdf") else ".html"
        try:
            acq.pin([("rules-document", url, acq.raw / f"{name}{suffix}")])
        except Exception as error:  # noqa: BLE001
            log.setdefault("rules_documents_unavailable", {})[name] = {
                "url": url,
                "error": str(error),
            }


def rates_for(raw: Path, prod: str, region: str, window: str, side: octopus.Side) -> list[Rate]:
    pages = sorted((raw / "rates" / prod / region / window).glob("page-*.json"))
    if not pages:
        raise FileNotFoundError(f"no pinned rates for {prod}/{region}/{window}")
    return octopus.load_rates(pages, side=side, published_at=octopus.publication_rule(prod))


def request(
    imp: str,
    exp: str,
    region: str,
    window: str,
    *,
    export_limit: Decimal,
    degradation: Decimal,
    free: Decimal,
) -> dict[str, Any]:
    start, end, _, _ = WINDOWS[window]
    return {
        "battery_kwh": str(CAPACITY),
        "inverter_kw": str(INVERTER),
        "export_limit_kw": str(export_limit),
        "import_limit_kw": None,
        "round_trip_efficiency": str(EFFICIENCY),
        "degradation_p_per_kwh": str(degradation),
        "free_energy_kwh_per_day": str(free),
        "import_tariff": {"product": imp, "region": region},
        "export_tariff": {"product": exp, "region": region},
        "window": {"from": start.isoformat(), "to": end.isoformat()},
    }


def evaluate(
    raw_octopus: Path, raw_elexon: Path, codes: dict[tuple[str, str], str]
) -> dict[str, Any]:
    cache: dict[tuple[str, str, str, str], list[Rate]] = {}

    def rates(prod, region, window, side):
        key = (prod, region, window, side)
        if key not in cache:
            cache[key] = rates_for(raw_octopus, prod, region, window, side)
        return cache[key]

    def run(imp, exp, region, window, export_limit, degradation=Decimal(0), free=Decimal(0)):
        req = request(
            imp, exp, region, window, export_limit=export_limit, degradation=degradation, free=free
        )
        try:
            out = hd.backtest_json(
                req, rates(imp, region, window, "import"), rates(exp, region, window, "export")
            )
        except FileNotFoundError as error:
            out = {"request": req, "not_testable": str(error)}
        return out

    results: dict[str, Any] = {"cases": {}}
    cases = results["cases"]
    imp, exp = HEADLINE
    cases["1-headline"] = {
        f"{region}/{window}": run(imp, exp, region, window, EXPORT_LIMITS["g99-20kw"])
        for region in REGIONS
        for window in WINDOWS
    }
    cases["2-export-limit"] = {
        f"{region}/{window}/{name}": run(imp, exp, region, window, limit)
        for region in REGIONS
        for window in WINDOWS
        for name, limit in EXPORT_LIMITS.items()
        if name != "g99-20kw"
    }
    cases["3-pairs"] = {
        f"{i}+{e}/{region}/{window}/{name}": run(i, e, region, window, limit)
        for i, e in product(octopus.IMPORT_PRODUCTS, octopus.EXPORT_PRODUCTS)
        for region in REGIONS
        for window in WINDOWS
        for name, limit in EXPORT_LIMITS.items()
        if name in ("g99-20kw", "g98-1ph")
    }
    # Best pair by summer monthly net at 20 kW across regions — chosen from the
    # numbers, as the declaration says; permitted/not is labelled afterwards.
    ranked = sorted(
        (
            (Decimal(v["monthly_net_gbp_over_complete_months"]), k)
            for k, v in cases["3-pairs"].items()
            if "/summer/g99-20kw" in k and v.get("monthly_net_gbp_over_complete_months")
        ),
        reverse=True,
    )
    results["best_pair_summer_20kw"] = [(str(n), k) for n, k in ranked[:10]]
    best_i, best_e = ranked[0][1].split("/")[0].split("+") if ranked else HEADLINE
    cases["4-degradation"] = {
        f"{label}/{region}/{d}p": run(
            i, e, region, "summer", EXPORT_LIMITS["g99-20kw"], degradation=d
        )
        for label, (i, e) in (("headline", HEADLINE), ("best-pair", (best_i, best_e)))
        for region in REGIONS
        for d in DEGRADATION
        if d != 0
    }
    cases["5-solar"] = {
        f"{region}/{name}/{free}kwh": run(best_i, best_e, region, "summer", limit, free=free)
        for region in REGIONS
        for name, limit in EXPORT_LIMITS.items()
        if name in ("g99-20kw", "g98-1ph")
        for free in FREE_SWEEP
    }
    # Case 6 — 2026-06-24, region E, every pair.
    (bloomberg,) = hd.decision_days(BLOOMBERG_DAY, BLOOMBERG_DAY)
    peak_start = datetime(2026, 6, 24, 16, 0, tzinfo=LONDON).astimezone(UTC)
    peak_end = datetime(2026, 6, 24, 21, 0, tzinfo=LONDON).astimezone(UTC)
    day_cases: dict[str, Any] = {}
    for i, e in product(octopus.IMPORT_PRODUCTS, octopus.EXPORT_PRODUCTS):
        try:
            slots, why = hd.slots_for(
                bloomberg, rates(i, "E", "summer", "import"), rates(e, "E", "summer", "export")
            )
        except FileNotFoundError as error:
            day_cases[f"{i}+{e}"] = {"not_testable": str(error)}
            continue
        if why:
            day_cases[f"{i}+{e}"] = {"dropped": why}
            continue
        entry: dict[str, Any] = {}
        for name in ("g99-20kw", "g98-1ph"):
            kwh, pence, average = hd.export_receipts_in_window(
                slots,
                kwh=CAPACITY,
                discharge_kw=EXPORT_LIMITS[name],
                start=peak_start,
                end=peak_end,
            )
            spec = BatterySpec(CAPACITY, INVERTER, EXPORT_LIMITS[name], EFFICIENCY)
            optimum = hd.optimise_day(BLOOMBERG_DAY, slots, spec, [hd.ZERO] * len(slots))
            entry[name] = {
                "gross_export_16_21_kwh": str(kwh.quantize(hd.PENNY)),
                "gross_export_16_21_gbp": str(hd.pounds(pence)),
                "average_export_p_16_21": None
                if average is None
                else str(average.quantize(hd.PENNY)),
                "day_optimum": {
                    "imported_kwh": str(optimum.imported_kwh.quantize(hd.PENNY)),
                    "exported_kwh": str(optimum.exported_kwh.quantize(hd.PENNY)),
                    "gross_export_receipts_gbp": str(hd.pounds(optimum.export_revenue_p)),
                    "import_cost_gbp": str(hd.pounds(optimum.import_cost_p)),
                    "net_gbp": str(hd.pounds(optimum.net_p)),
                },
            }
        entry["half_hours"] = [
            {
                "start_utc": s.start.isoformat(),
                "import_p": str(s.import_p),
                "export_p": str(s.export_p),
            }
            for s in slots
        ]
        day_cases[f"{i}+{e}"] = entry
    cases["6-bloomberg-day"] = day_cases
    cases["7-wedge"] = wedge(
        raw_elexon, rates(imp, "E", "summer", "import"), rates(exp, "E", "summer", "export")
    )
    return results


def wedge(raw_elexon: Path, import_rates: list[Rate], export_rates: list[Rate]) -> dict[str, Any]:
    """Import inc VAT minus export in the same half-hour (region E, summer),
    the cap's incidence, and the Elexon layer beneath, per month."""
    export_at = {r.valid_from: r.pence_per_kwh for r in export_rates}
    rows = []
    for r in import_rates:
        e = export_at.get(r.valid_from)
        if e is not None and date(2026, 6, 1) <= r.valid_from.astimezone(LONDON).date() <= date(
            2026, 8, 31
        ):
            rows.append((r.valid_from, r.pence_per_kwh, e))
    if not rows:
        return {"not_testable": "no overlapping import/export half-hours"}
    wedges = sorted(p - e for _, p, e in rows)

    def pct(q: int) -> str:
        return str(wedges[min(len(wedges) - 1, (len(wedges) - 1) * q // 100)].quantize(hd.PENNY))

    cap = max(p for _, p, _ in rows)
    by_month: dict[str, dict[str, Any]] = {}
    for t, p, e in rows:
        m = by_month.setdefault(
            t.astimezone(LONDON).strftime("%Y-%m"),
            {"n": 0, "import": hd.ZERO, "export": hd.ZERO, "wedge_negative": 0},
        )
        m["n"] += 1
        m["import"] += p
        m["export"] += e
        m["wedge_negative"] += int(e * EFFICIENCY > p)
    months = {
        k: {
            "half_hours": v["n"],
            "mean_import_inc_vat_p": str((v["import"] / v["n"]).quantize(hd.PENNY)),
            "mean_export_p": str((v["export"] / v["n"]).quantize(hd.PENNY)),
            "half_hours_where_export_x_eta_exceeds_import": v["wedge_negative"],
        }
        for k, v in sorted(by_month.items())
    }
    elexon_layer = elexon_by_month(raw_elexon)
    for k, v in elexon_layer.items():
        months.setdefault(k, {}).update(v)
    return {
        "half_hours": len(rows),
        "wedge_p_percentiles": {"p10": pct(10), "p50": pct(50), "p90": pct(90)},
        "max_import_inc_vat_p": str(cap),
        "half_hours_at_max_import": sum(1 for _, p, _ in rows if p == cap),
        "months": months,
    }


def elexon_by_month(raw: Path) -> dict[str, dict[str, Any]]:
    """Monthly means of MID price by provider and of system sell/buy price.
    Field names are read defensively; a differing schema is recorded, not guessed."""
    acc: dict[str, dict[str, list[Decimal]]] = {}
    notes: set[str] = set()
    for folder in sorted(raw.glob("2026-*")):
        month = folder.name[:7]
        mid = folder / "mid.json"
        if mid.exists():
            payload = load_json(mid)
            records = payload.get("data", payload) if isinstance(payload, dict) else payload
            for rec in records if isinstance(records, list) else []:
                provider, price = rec.get("dataProvider"), rec.get("price")
                if provider is None or price is None:
                    notes.add("MID record lacks dataProvider/price")
                    continue
                acc.setdefault(month, {}).setdefault(f"mid_{provider}", []).append(
                    Decimal(str(price))
                )
        sp = folder / "system-prices.json"
        if sp.exists():
            payload = load_json(sp)
            records = payload.get("data", payload) if isinstance(payload, dict) else payload
            for rec in records if isinstance(records, list) else []:
                for field in ("systemSellPrice", "systemBuyPrice"):
                    if rec.get(field) is None:
                        notes.add(f"system-prices record lacks {field}")
                        continue
                    acc.setdefault(month, {}).setdefault(field, []).append(Decimal(str(rec[field])))
    out: dict[str, dict[str, Any]] = {}
    for month, series in acc.items():
        out[month] = {
            f"mean_{name}_gbp_per_mwh": str((sum(values) / len(values)).quantize(hd.PENNY))
            for name, values in series.items()
            if values
        }
    if notes:
        out["_schema_notes"] = {"notes": sorted(notes)}
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seal", required=True, help="prefix (≥ 8 hex) of DECLARATION.md's SHA-256"
    )
    parser.add_argument("--run-date", default=datetime.now(UTC).date().isoformat())
    parser.add_argument(
        "--phase", choices=("acquire", "evaluate", "rules", "press", "all"), default="all"
    )
    parser.add_argument(
        "--press-url", help="URL of the Bloomberg feature, pinned under data/raw/press/"
    )
    parser.add_argument("--press-note", help="metadata recorded with the press pin (token expiry)")
    parser.add_argument(
        "--press-file",
        help="a saved copy of the article (HTML or PDF) to pin when the publisher refuses fetches",
    )
    parser.add_argument("--note", action="append", default=[], help="note for the acquisition log")
    parser.add_argument(
        "--rules-url", action="append", default=[], help="name=url, extra rules document"
    )
    args = parser.parse_args()

    digest = declaration_digest()
    if len(args.seal) < 8 or not digest.startswith(args.seal.lower()):
        print(
            f"seal {args.seal!r} does not match DECLARATION.md sha256 {digest}; refusing",
            file=sys.stderr,
        )
        return 2
    date.fromisoformat(args.run_date)
    raw_octopus = REPO_ROOT / "data/raw/octopus" / f"{args.run_date}-010"
    raw_elexon = REPO_ROOT / "data/raw/elexon/010"
    raw_rules = REPO_ROOT / "data/raw/rules/010"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    log_path = EVIDENCE / "acquisition-log.json"
    log: dict[str, Any] = json.loads(log_path.read_text()) if log_path.exists() else {}
    log.update({"declaration_sha256": digest, "seal": args.seal, "run_date": args.run_date})
    if args.note:
        log.setdefault("notes", []).extend(args.note)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    codes_path = EVIDENCE / "tariff-codes.json"

    if args.phase in ("acquire", "all"):
        acq = Acquirer(raw_octopus, octopus.fetch_pinned)
        codes = acquire_octopus(acq, log)
        codes_path.write_text(
            json.dumps({f"{p}/{r}": c for (p, r), c in sorted(codes.items())}, indent=1) + "\n"
        )
        acquire_elexon(Acquirer(raw_elexon, elexon.fetch_pinned))
    if args.phase in ("press", "all") and (args.press_url or args.press_file):
        press = REPO_ROOT / "data/raw/press"
        # A gift link carries a bearer token; the committed log keeps the
        # article identity, never the credential.
        redacted = re.sub(r"accessToken=[^&]+", "accessToken=<redacted>", args.press_url or "")
        record: dict[str, Any] = {"url": redacted, "note": args.press_note}
        if args.press_file:
            source = Path(args.press_file)
            suffix = source.suffix.lower() or ".html"
            destination = press / f"010-bloomberg-2026-09-03{suffix}"

            def copy_saved(*, url: str, destination: Path, dataset: str) -> SourceArtifact:
                if destination.exists():
                    raise FileExistsError(f"pinned artefact already exists: {destination}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
                return SourceArtifact(
                    source="sponsor-saved-copy",
                    dataset=dataset,
                    path=destination,
                    sha256=sha256_file(destination),
                    fetched_at=datetime.now(UTC),
                )

            Acquirer(press, copy_saved).pin(
                [("press", args.press_url or f"file:{source.name}", destination)]
            )
            record["saved_copy"] = str(source)
        else:
            try:
                Acquirer(press, octopus.fetch_pinned).pin(
                    [("press", args.press_url, press / "010-bloomberg-2026-09-03.html")]
                )
            except Exception as error:  # noqa: BLE001 — recorded, not retried elsewhere
                record["error"] = re.sub(
                    r"accessToken=[^&']+", "accessToken=<redacted>", str(error).splitlines()[0]
                )
        log.setdefault("press_attempts", []).append(record)
    if args.phase in ("evaluate", "all"):
        codes = {tuple(k.split("/")): v for k, v in json.loads(codes_path.read_text()).items()}  # type: ignore[misc]
        results = evaluate(raw_octopus, raw_elexon, codes)
        results.update(log)
        results["amendments"] = "AMENDMENTS.md"
        results["rule"] = hd.RULE
        (EVIDENCE / "results.json").write_text(json.dumps(results, indent=1, default=str) + "\n")
        print(
            json.dumps(
                {
                    "headline": results["cases"]["1-headline"],
                    "best_pair_summer_20kw": results["best_pair_summer_20kw"],
                },
                indent=1,
            )
        )
    if args.phase in ("rules", "all"):
        extra = dict(item.split("=", 1) for item in args.rules_url)
        acquire_rules(Acquirer(raw_rules, octopus.fetch_pinned), extra, log)
    manifest = []
    for raw in (raw_octopus, raw_elexon, raw_rules, REPO_ROOT / "data/raw/press"):
        path = raw / "manifest.json"
        if path.exists():
            manifest.extend(json.loads(path.read_text()))
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(sorted(manifest, key=lambda e: e["path"]), indent=1) + "\n"
    )
    log_path.write_text(json.dumps(log, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
