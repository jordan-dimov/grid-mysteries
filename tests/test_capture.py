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
    cap.run_capture([TEC], CannedFetcher(canned_tec()), store, day=date(2026, 9, 16))
    lines = [
        json.loads(line)
        for line in (tmp_path / "manifests/2026-09-16.ndjson").read_text().splitlines()
    ]
    assert lines[1]["unchanged_from"] == "2026-09-15"
    assert not (tmp_path / "raw/neso/tec-register/2026-09-16").exists()
    latest = json.loads((tmp_path / "status/vintage-capture/latest.json").read_text())
    assert latest["digests"]["tec-register/NESO-TEC-REGISTER"]["day"] == "2026-09-15"
    assert latest["resources"][0]["unchanged"] == 2
    changed = canned_tec(body=b"Project Name,Customer\nA,C\n")
    cap.run_capture([TEC], CannedFetcher(changed), store, day=date(2026, 9, 17))
    lines = [
        json.loads(line)
        for line in (tmp_path / "manifests/2026-09-17.ndjson").read_text().splitlines()
    ]
    assert lines[1]["unchanged_from"] is None
    assert (tmp_path / lines[1]["key"]).exists()


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
