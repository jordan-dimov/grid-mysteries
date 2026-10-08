"""What we hold: a pure function of the daily manifests, self-contained, and
every captured resource described."""

from pathlib import Path

from grid_mysteries.capture.plan import PLAN
from grid_mysteries.rendering import vintages as v

REPO = Path(__file__).parents[1]


def row(day, source, resource, dataset, sha, nbytes, unchanged_from=None, skipped=None):
    return {
        "day": day,
        "source": source,
        "resource": resource,
        "dataset": dataset,
        "url": "https://example.test/x",
        "key": f"raw/{source}/{resource}/{unchanged_from or day}/{sha}",
        "sha256": sha,
        "bytes": nbytes,
        "fetched_at": f"{day}T06:30:00+00:00",
        "http": {},
        "extra": {"skipped": skipped} if skipped else {},
        "unchanged_from": unchanged_from,
    }


ROWS = [
    # a single-file resource: new on day 1, unchanged on day 2 (bytes point back), new on day 3
    row("2026-09-15", "neso", "tec-register", "NESO-TEC-REGISTER-META", "m1", 100),
    row("2026-09-15", "neso", "tec-register", "NESO-TEC-REGISTER", "f1", 1000),
    row("2026-09-16", "neso", "tec-register", "NESO-TEC-REGISTER-META", "m1", 100, "2026-09-15"),
    row("2026-09-16", "neso", "tec-register", "NESO-TEC-REGISTER", "f1", 1000, "2026-09-15"),
    row("2026-09-17", "neso", "tec-register", "NESO-TEC-REGISTER-META", "m2", 100),
    row("2026-09-17", "neso", "tec-register", "NESO-TEC-REGISTER", "f2", 2000),
    # a metadata-only day: the publisher said unchanged, the file was not fetched
    row(
        "2026-09-18",
        "neso",
        "tec-register",
        "NESO-TEC-REGISTER-META",
        "m2",
        100,
        "2026-09-17",
        "unchanged last_modified",
    ),
    # a many-dataset resource: two messages on one day
    row("2026-09-16", "elexon", "remit", "ELEXON-REMIT-a", "r1", 10),
    row("2026-09-16", "elexon", "remit", "ELEXON-REMIT-b", "r2", 20),
]


def test_summary_counts_files_days_and_the_current_file():
    tec, remit = sorted(v.summarise(ROWS), key=lambda s: s.source)[::-1]
    assert (tec.source, tec.resource) == ("neso", "tec-register")
    assert (tec.first_day, tec.last_day, tec.days) == ("2026-09-15", "2026-09-18", 4)
    assert tec.files == 2 and tec.bytes == 3000  # metadata is not a file
    assert tec.new_on_days == 2 and tec.datasets == 1
    assert tec.current_since == "2026-09-17"  # the latest file row's day (it was new that day)
    assert (remit.files, remit.datasets, remit.current_since, remit.bytes) == (2, 2, None, 30)


def test_unchanged_rows_point_at_the_day_first_seen():
    rows = ROWS[:4]  # day 1 new, day 2 unchanged
    (tec,) = [s for s in v.summarise(rows) if s.source == "neso"]
    assert tec.current_since == "2026-09-15" and tec.new_on_days == 1 and tec.files == 1


def test_page_is_deterministic_self_contained_and_honest():
    html = v.render_page(v.summarise(ROWS))
    assert html == v.render_page(v.summarise(ROWS))
    assert "<script" not in html and "a115.co.uk" not in html.split("<main>")[0]
    assert "2 resources, 4 distinct files, 3 kB" in html
    assert "current file first seen 17/09/2026" in html and "2 datasets" in html
    text = " ".join(html.split())  # the HTML wraps its prose; the words are what matter
    assert "held privately" in text and "What this page never claims" in text
    assert "data/manifests" in html
    assert v.render_page([]).count("No manifests yet.") == 1


def test_every_planned_and_every_captured_resource_is_described():
    for resource in PLAN:
        assert (resource.source, resource.resource) in v.DESCRIPTIONS, resource.name
        assert resource.source in v.PUBLISHERS, resource.source
    manifests = REPO / "data" / "manifests"
    if manifests.exists():
        for s in v.summarise(v.read_manifests(manifests)):
            assert (s.source, s.resource) in v.DESCRIPTIONS, (s.source, s.resource)


def test_sizes_and_days_read_as_people_write_them():
    assert v.size(999) == "999 B" and v.size(2_500) == "2 kB"
    assert v.size(3_400_000) == "3.4 MB" and v.size(1_200_000_000) == "1.2 GB"
    assert v.day_label("2026-10-08") == "08/10/2026"
