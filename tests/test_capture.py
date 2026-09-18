import json
from datetime import UTC, date, datetime
from pathlib import Path

from grid_mysteries.capture import run as cap
from grid_mysteries.capture.fetch import CannedFetcher, Response
from grid_mysteries.capture.plan import PLAN, TO_ADD, Resource, by_name
from grid_mysteries.capture.store import LocalStore
from grid_mysteries.capture.strategies import eso_map, gov_assets

CKAN = "https://api.neso.energy/api/3/action"
TEC = by_name("NESO-TEC-REGISTER")
TEC_ID = TEC.params["resource_id"]


def clock(*stamps):
    it = iter(stamps)
    last = stamps[-1]
    return lambda: next(it, last)


def canned_tec(body=b"Project Name,Customer\nA,B\n", last_modified="2026-09-15T16:48:30"):
    meta = {
        "result": {
            "url": "https://api.neso.energy/dl/tec.csv",
            "last_modified": last_modified,
            "name": "TEC Register",
        }
    }
    return {
        f"{CKAN}/resource_show?id={TEC_ID}": json.dumps(meta).encode(),
        "https://api.neso.energy/dl/tec.csv": Response(
            "https://api.neso.energy/dl/tec.csv",
            200,
            body,
            {"content-type": "text/csv", "etag": '"abc"'},
        ),
    }


def test_plan_names_are_unique_and_every_strategy_is_known():
    names = [r.name for r in PLAN]
    assert len(names) == len(set(names))
    from grid_mysteries.capture.strategies import STRATEGIES

    assert {r.strategy for r in PLAN} <= set(STRATEGIES)
    assert TO_ADD  # what is not captured is written down
    # 2026-09-18: Cloudflare challenges Render's egress on NGED's PDF paths and
    # the whole ENA page, whatever the user agent; the PDFs are excluded by
    # format and the ENA page is written down, not fetched.
    for name in ("NGED-CONNECTIONS-REFORM-REGISTER", "NGED-CONNECTIONS-REFORM-OUTCOMES"):
        assert "PDF" not in by_name(name).params["formats"].upper().split(",")
    assert all(r.name != "ENA-CONNECTIONS-DASHBOARD" for r in PLAN)
    assert any("ENA connections dashboard" in item for item, _ in TO_ADD)


def test_ckan_capture_writes_bytes_manifest_and_status(tmp_path: Path):
    store = LocalStore(tmp_path)
    fetcher = CannedFetcher(canned_tec())
    pings = []
    status = cap.run_capture(
        [TEC],
        fetcher,
        store,
        day=date(2026, 9, 15),
        now=clock(datetime(2026, 9, 15, 6, 30, tzinfo=UTC)),
        ping=lambda ok, body: pings.append((ok, body)),
    )
    assert status.ok and status.resources[0].artefacts == 2
    lines = [
        json.loads(line)
        for line in (tmp_path / "manifests/2026-09-15.ndjson").read_text().splitlines()
    ]
    assert [line["dataset"] for line in lines] == ["NESO-TEC-REGISTER-META", "NESO-TEC-REGISTER"]
    register = lines[1]
    assert register["key"] == f"raw/neso/tec-register/2026-09-15/{register['sha256']}"
    assert (tmp_path / register["key"]).read_bytes() == b"Project Name,Customer\nA,B\n"
    assert register["http"] == {"content-type": "text/csv", "etag": '"abc"'}
    assert register["extra"]["ckan_last_modified"] == "2026-09-15T16:48:30"
    assert register["unchanged_from"] is None
    latest = json.loads((tmp_path / "status/vintage-capture/latest.json").read_text())
    assert latest["digests"]["tec-register/NESO-TEC-REGISTER"]["day"] == "2026-09-15"
    assert (tmp_path / "status/vintage-capture/2026-09-15.json").exists()
    assert pings == [(True, "NESO-TEC-REGISTER: 2 artefacts")]


def test_same_bytes_on_a_later_day_are_not_rewritten_and_say_unchanged_from(tmp_path: Path):
    store = LocalStore(tmp_path)
    cap.run_capture([TEC], CannedFetcher(canned_tec()), store, day=date(2026, 9, 15))
    # the portal re-touched the resource (new last_modified) but the bytes are the same
    same_bytes = canned_tec(last_modified="2026-09-16T08:00:00")
    cap.run_capture([TEC], CannedFetcher(same_bytes), store, day=date(2026, 9, 16))
    lines = [
        json.loads(line)
        for line in (tmp_path / "manifests/2026-09-16.ndjson").read_text().splitlines()
    ]
    assert lines[1]["unchanged_from"] == "2026-09-15"
    assert lines[1]["key"].startswith("raw/neso/tec-register/2026-09-15/")
    # only the metadata (which carries the new date) is new bytes on the 16th
    assert len(list((tmp_path / "raw/neso/tec-register/2026-09-16").iterdir())) == 1
    latest = json.loads((tmp_path / "status/vintage-capture/latest.json").read_text())
    assert latest["digests"]["tec-register/NESO-TEC-REGISTER"]["day"] == "2026-09-15"
    assert latest["resources"][0]["unchanged"] == 1  # the META response carries a new date
    changed = canned_tec(body=b"Project Name,Customer\nA,C\n", last_modified="2026-09-17T08:00:00")
    cap.run_capture([TEC], CannedFetcher(changed), store, day=date(2026, 9, 17))
    lines = [
        json.loads(line)
        for line in (tmp_path / "manifests/2026-09-17.ndjson").read_text().splitlines()
    ]
    assert lines[1]["unchanged_from"] is None
    assert (tmp_path / lines[1]["key"]).exists()


def test_a_large_response_spooled_to_disk_is_uploaded_from_the_file(tmp_path: Path):
    import hashlib

    big = b"x" * 1000
    spool = tmp_path / "spool.bin"
    spool.write_bytes(big)
    responses = canned_tec()
    responses["https://api.neso.energy/dl/tec.csv"] = Response(
        "https://api.neso.energy/dl/tec.csv",
        200,
        headers={"content-type": "text/csv"},
        path=spool,
        size=len(big),
        sha256=hashlib.sha256(big).hexdigest(),
    )
    store = LocalStore(tmp_path / "bucket")
    status = cap.run_capture([TEC], CannedFetcher(responses), store, day=date(2026, 9, 15))
    assert status.resources[0].bytes >= 1000
    lines = [
        json.loads(line)
        for line in (tmp_path / "bucket/manifests/2026-09-15.ndjson").read_text().splitlines()
    ]
    assert lines[1]["sha256"] == hashlib.sha256(big).hexdigest() and lines[1]["bytes"] == 1000
    assert (tmp_path / "bucket" / lines[1]["key"]).read_bytes() == big
    assert not spool.exists()  # the temporary file is removed after upload


def test_ckan_download_is_skipped_while_last_modified_is_unchanged(tmp_path: Path):
    store = LocalStore(tmp_path)
    first = CannedFetcher(canned_tec())
    cap.run_capture([TEC], first, store, day=date(2026, 9, 15))
    second = CannedFetcher(canned_tec())
    status = cap.run_capture([TEC], second, store, day=date(2026, 9, 16))
    assert [c[0] for c in second.calls] == [f"{CKAN}/resource_show?id={TEC_ID}"]
    assert status.resources[0].artefacts == 1
    lines = [
        json.loads(line)
        for line in (tmp_path / "manifests/2026-09-16.ndjson").read_text().splitlines()
    ]
    assert lines[0]["extra"]["skipped"] == "unchanged last_modified"
    third = CannedFetcher(canned_tec(body=b"new", last_modified="2026-09-17T09:00:00"))
    status = cap.run_capture([TEC], third, store, day=date(2026, 9, 17))
    assert len(third.calls) == 2 and status.resources[0].artefacts == 2
    latest = json.loads((tmp_path / "status/vintage-capture/latest.json").read_text())
    assert latest["extras"]["tec-register/NESO-TEC-REGISTER"]["ckan_last_modified"] == (
        "2026-09-17T09:00:00"
    )


def test_one_failing_resource_does_not_stop_the_others_and_pings_fail(tmp_path: Path):
    broken = Resource("BROKEN", "neso", "broken", "ckan", {"resource_id": "nope"})
    pings = []
    status = cap.run_capture(
        [broken, TEC],
        CannedFetcher(canned_tec()),
        LocalStore(tmp_path),
        day=date(2026, 9, 15),
        ping=lambda ok, body: pings.append((ok, body)),
    )
    assert status.ok is False
    error = status.resources[0].error
    assert error is not None and error.startswith("FetchError: HTTP 404")
    assert status.resources[1].artefacts == 2
    assert pings[0][0] is False and "BROKEN: 0 artefacts ERROR" in pings[0][1]
    unknown = Resource("ODD", "x", "x", "teleport")
    status = cap.run_capture(
        [unknown], CannedFetcher({}), LocalStore(tmp_path), day=date(2026, 9, 15)
    )
    assert status.resources[0].error == "unknown strategy 'teleport'"


def test_witness_proofs_land_under_proofs_and_a_witness_failure_is_reported(tmp_path: Path):
    store = LocalStore(tmp_path)
    status = cap.run_capture(
        [TEC],
        CannedFetcher(canned_tec()),
        store,
        day=date(2026, 9, 15),
        witness=lambda data, name: {f"{name}.ots": b"OTS", f"{name}.tsq": b"TSQ"},
    )
    assert status.proof_keys == ["proofs/2026-09-15.ndjson.ots", "proofs/2026-09-15.ndjson.tsq"]
    assert store.get("proofs/2026-09-15.ndjson.ots") == b"OTS"

    def broken(data, name):
        raise RuntimeError("no tsa")

    status = cap.run_capture(
        [TEC], CannedFetcher(canned_tec()), store, day=date(2026, 9, 16), witness=broken
    )
    assert status.witness_error == "RuntimeError: no tsa" and status.ok is True


def test_a_store_that_refuses_writes_still_pings_fail_and_reports(tmp_path: Path):
    class Refusing(LocalStore):
        def put(self, key, data, *, content_type="application/octet-stream"):
            raise PermissionError("AccessDenied: PutObject")

    pings = []
    status = cap.run_capture(
        [TEC],
        CannedFetcher(canned_tec()),
        Refusing(tmp_path),
        day=date(2026, 9, 15),
        ping=lambda ok, body: pings.append((ok, body)),
        witness=lambda data, name: {f"{name}.ots": b"OTS"},
    )
    assert status.ok is False
    assert status.store_error is not None and "AccessDenied" in status.store_error
    assert status.proof_keys == []  # no witnessing of a manifest that was never stored
    assert pings[0][0] is False and pings[0][1].startswith("STORE ERROR PermissionError")


def test_healthcheck_pinger_hits_fail_on_failure_and_never_raises():
    fetcher = CannedFetcher({})
    ping = cap.healthcheck_pinger(fetcher, "https://hc-ping.com/abc")
    assert ping is not None
    ping(True, "fine")
    ping(False, "broken")
    assert [c[0] for c in fetcher.calls] == [
        "https://hc-ping.com/abc",
        "https://hc-ping.com/abc/fail",
    ]
    assert fetcher.calls[1][1] == b"broken"
    assert cap.healthcheck_pinger(fetcher, None) is None


def test_remit_follows_the_detail_urls_the_list_gives():
    remit = by_name("ELEXON-REMIT")
    listing = {
        "data": [
            {
                "url": "https://data.elexon.co.uk/bmrs/api/v1/remit/917154",
                "id": 917154,
                "mrid": "M1",
                "revisionNumber": 3,
            }
        ]
    }
    list_url = (
        "https://data.elexon.co.uk/bmrs/api/v1/remit/list/by-publish"
        "?from=2026-09-14T00:00:00Z&to=2026-09-14T23:59:59Z"
    )
    fetcher = CannedFetcher(
        {
            list_url: json.dumps(listing).encode(),
            "https://data.elexon.co.uk/bmrs/api/v1/remit/917154": b'{"id": 917154}',
        }
    )
    got = list(cap.STRATEGIES["elexon_remit"](remit, fetcher, date(2026, 9, 15)))
    assert [g.dataset for g in got] == [
        "ELEXON-REMIT-LIST-2026-09-14",
        "ELEXON-REMIT-MESSAGE-917154",
    ]
    assert got[1].extra == {"mrid": "M1", "revision": "3"}


def test_ocds_pages_follow_links_next_for_the_previous_day():
    cf = by_name("CONTRACTS-FINDER-OCDS")
    first = cf.params["template"].format(day="2026-09-14")
    fetcher = CannedFetcher(
        {
            first: json.dumps(
                {"releases": [], "links": {"next": "https://example.org/p2"}}
            ).encode(),
            "https://example.org/p2": json.dumps({"releases": []}).encode(),
        }
    )
    got = list(cap.STRATEGIES["ocds_daily"](cf, fetcher, date(2026, 9, 15)))
    assert [g.dataset for g in got] == [
        "CONTRACTS-FINDER-OCDS-2026-09-14-P001",
        "CONTRACTS-FINDER-OCDS-2026-09-14-P002",
    ]


def test_eso_map_captures_points_lines_and_every_point_with_a_pause():
    eso = by_name("ESO-MAP")
    base = eso.params["base"]
    points = {"features": [{"properties": {"id": 7}}, {"properties": {"id": 9}}]}
    fetcher = CannedFetcher(
        {
            base + "get-points.php": json.dumps(points).encode(),
            base + "get-lines.php": b"{}",
            base + "get-point-json.php": b'{"id": "x"}',
        }
    )
    pauses: list[float] = []
    got = list(eso_map(eso, fetcher, date(2026, 9, 15), pause=pauses.append))
    assert [g.dataset for g in got] == [
        "ESO-MAP-POINTS",
        "ESO-MAP-LINES",
        "ESO-MAP-POINT-7",
        "ESO-MAP-POINT-9",
    ]
    assert fetcher.calls[2] == (base + "get-point-json.php", b"id=7")
    assert (
        fetcher.content_types[2] == "application/x-www-form-urlencoded"
    )  # the endpoint 400s without it
    assert got[2].url.endswith("get-point-json.php?id=7")
    assert pauses == [0.15, 0.15]


def test_gov_assets_captures_the_page_and_each_linked_extract():
    repd = by_name("DESNZ-REPD")
    page = b'<a href="https://assets.publishing.service.gov.uk/media/1/REPD_Q2_2026.csv">csv</a> <a href="https://assets.publishing.service.gov.uk/media/2/REPD_Q2_2026.xlsx">x</a>'
    fetcher = CannedFetcher(
        {
            repd.params["url"]: page,
            "https://assets.publishing.service.gov.uk/media/1/REPD_Q2_2026.csv": b"a,b",
            "https://assets.publishing.service.gov.uk/media/2/REPD_Q2_2026.xlsx": b"PK",
        }
    )
    got = list(gov_assets(repd, fetcher, date(2026, 9, 15)))
    assert [g.dataset for g in got] == [
        "DESNZ-REPD-PAGE",
        "DESNZ-REPD-REPD_Q2_2026.csv",
        "DESNZ-REPD-REPD_Q2_2026.xlsx",
    ]


def test_local_store_refuses_unsafe_keys_and_lists_by_prefix(tmp_path: Path):
    import pytest

    store = LocalStore(tmp_path)
    with pytest.raises(ValueError):
        store.put("../escape", b"x")
    store.put("manifests/2026-09-15.ndjson", b"{}\n")
    store.put("manifests/2026-09-16.ndjson", b"{}\n")
    assert list(store.keys("manifests")) == [
        "manifests/2026-09-15.ndjson",
        "manifests/2026-09-16.ndjson",
    ]
    assert list(store.keys("nothing")) == []
    assert store.get("missing") is None


def test_ckan_base_parameter_and_headers_reach_the_fetcher():
    from grid_mysteries.capture.strategies import ckan

    base = "https://data-api.example/api/3/action"
    meta = {"result": {"url": "https://data-api.example/dl/x.csv", "last_modified": "t1"}}
    fetcher = CannedFetcher(
        {
            f"{base}/resource_show?id=r1": json.dumps(meta).encode(),
            "https://data-api.example/dl/x.csv": b"a,b\n1,2\n",
        }
    )
    resource = Resource(
        "X", "x", "x", "ckan", {"resource_id": "r1", "base": base}, headers={"User-Agent": "UA"}
    )
    captured = list(ckan(resource, fetcher, date(2026, 9, 18)))
    assert [c[0] for c in fetcher.calls] == [
        f"{base}/resource_show?id=r1",
        "https://data-api.example/dl/x.csv",
    ]
    assert fetcher.headers == [{"User-Agent": "UA"}, {"User-Agent": "UA"}]
    assert [c.dataset for c in captured] == ["X-META", "X"]


def test_ckan_package_captures_each_listed_file_once_per_vintage(tmp_path: Path):
    base = "https://data-api.example/api/3/action"

    def package(*items):
        return json.dumps({"result": {"resources": list(items)}}).encode()

    aug = {"id": "aaa", "url": "https://x/aug.xlsx", "format": "XLSX", "last_modified": "t-aug"}
    sep = {"id": "bbb", "url": "https://x/sep.xlsx", "format": "XLSX", "last_modified": "t-sep"}
    pdf = {"id": "ccc", "url": "https://x/note.pdf", "format": "PDF", "last_modified": "t-pdf"}
    resource = Resource(
        "R", "r", "register", "ckan_package", {"base": base, "package_id": "p", "formats": "XLSX"}
    )
    store = LocalStore(tmp_path)
    first = CannedFetcher(
        {f"{base}/package_show?id=p": package(aug, pdf), "https://x/aug.xlsx": b"AUG"}
    )
    status = cap.run_capture([resource], first, store, day=date(2026, 9, 18))
    assert [c[0] for c in first.calls] == [f"{base}/package_show?id=p", "https://x/aug.xlsx"]
    assert status.resources[0].artefacts == 2  # the listing and the one wanted file
    second = CannedFetcher(
        {f"{base}/package_show?id=p": package(aug, sep, pdf), "https://x/sep.xlsx": b"SEP"}
    )
    status = cap.run_capture([resource], second, store, day=date(2026, 9, 19))
    # August is unchanged by last_modified and is not re-downloaded; September is new.
    assert [c[0] for c in second.calls] == [f"{base}/package_show?id=p", "https://x/sep.xlsx"]
    lines = [
        json.loads(line)
        for line in (tmp_path / "manifests/2026-09-19.ndjson").read_text().splitlines()
    ]
    assert {line["dataset"] for line in lines} == {"R-META", "R-bbb"}
    latest = json.loads((tmp_path / "status/vintage-capture/latest.json").read_text())
    assert latest["extras"]["register/R-aaa"]["ckan_last_modified"] == "t-aug"
    assert latest["extras"]["register/R-bbb"]["ckan_last_modified"] == "t-sep"


def test_url_strategy_sends_the_resources_headers():
    from grid_mysteries.capture.strategies import url as url_strategy

    fetcher = CannedFetcher({"https://ena.example/page": b"<html/>"})
    resource = Resource(
        "E", "ena", "page", "url", {"url": "https://ena.example/page"}, headers={"User-Agent": "B"}
    )
    list(url_strategy(resource, fetcher, date(2026, 9, 18)))
    assert fetcher.headers == [{"User-Agent": "B"}]


def test_a_keyed_resource_is_never_fetched_without_its_key_and_gets_the_header_with_it(
    tmp_path: Path,
):
    import os

    from grid_mysteries.capture.plan import UKPN_KEY

    resource = Resource(
        "K", "ukpn", "keyed", "url", {"url": "https://u/export.csv"}, secret_header=UKPN_KEY
    )
    store = LocalStore(tmp_path)
    fetcher = CannedFetcher({"https://u/export.csv": b"a;b\n1;2\n"})
    os.environ.pop("UKPN_API_KEY", None)
    status = cap.run_capture([resource], fetcher, store, day=date(2026, 9, 18))
    assert fetcher.calls == []
    assert status.resources[0].error is not None and "UKPN_API_KEY" in status.resources[0].error
    os.environ["UKPN_API_KEY"] = "k3y"
    try:
        status = cap.run_capture([resource], fetcher, store, day=date(2026, 9, 18))
    finally:
        del os.environ["UKPN_API_KEY"]
    assert status.resources[0].error is None and status.resources[0].artefacts == 1
    assert fetcher.headers == [{"Authorization": "Apikey k3y"}]
    lines = (tmp_path / "manifests/2026-09-18.ndjson").read_text()
    assert "k3y" not in lines  # the secret never reaches the manifest
