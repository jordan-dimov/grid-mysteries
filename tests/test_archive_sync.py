import json

from grid_mysteries import archive_sync as sync

DAY = [f"data/manifests/2026-10-23.ndjson{s}" for s in ("", *sync.PROOF_SUFFIXES)]
LOG = "investigations/013-the-cover-price-tracker/evidence/acquisition-log.json"


def test_classify_sorts_what_a_sync_commits_and_refuses_the_rest():
    plan = sync.classify(
        [("??", p) for p in DAY]
        + [
            ("M", "data/manifests/2026-10-22.ndjson.ots"),
            ("M", "investigations/025-the-exit-clock/DECLARATION.md.ots"),
            ("M", LOG),
            ("??", "investigations/013-the-cover-price-tracker/evidence/batch-06-manifest.json"),
            ("M", "src/grid_mysteries/cli.py"),
            ("??", "data/manifests/2026-10-23.ndjson.bak"),
            ("M", "data/manifests/2026-10-22.ndjson"),
        ]
    )
    assert set(plan.days) == {"2026-10-23"} and plan.incomplete_days() == {}
    assert len(plan.upgraded_proofs) == 2 and plan.grown == [LOG] and len(plan.batches) == 1
    assert [p for p, _ in plan.refused] == [
        "src/grid_mysteries/cli.py",
        "data/manifests/2026-10-23.ndjson.bak",
        "data/manifests/2026-10-22.ndjson",  # a committed manifest never changes
    ]


def test_a_day_missing_a_proof_file_is_incomplete():
    plan = sync.classify([("??", p) for p in DAY if not p.endswith(".digicert.tsr")])
    assert plan.incomplete_days() == {
        "2026-10-23": ["data/manifests/2026-10-23.ndjson.digicert.tsr"]
    }


def test_only_grew_accepts_appended_records_and_refuses_edits():
    old = {"seal": "d20d5920", "runs": [{"day": 1}, {"day": 2}]}
    grown = {**old, "runs": [{"day": 1}, {"day": 2}, {"day": 3}], "added": True}
    edited = {**old, "runs": [{"day": 1}, {"day": 9}, {"day": 3}]}
    dropped = {"runs": old["runs"]}
    b = lambda v: json.dumps(v).encode()  # noqa: E731
    assert sync.only_grew(b(old), b(grown))
    assert not sync.only_grew(b(old), b(edited))
    assert not sync.only_grew(b(old), b(dropped))
    assert not sync.only_grew(b([1, 2]), b([2, 1, 3]))
