"""OpenTimestamps proof sweep. Fixtures are the real proof of the 2026-09-15
capture manifest, as issued (pending) and as first upgraded on 2026-09-19
(three calendars, blocks 967193, 967198 and 967211)."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from grid_mysteries import proofs

FIXTURES = Path(__file__).parent / "fixtures/proofs"
PENDING = (FIXTURES / "2026-09-15.ndjson.pending.ots").read_bytes()
UPGRADED = (FIXTURES / "2026-09-15.ndjson.upgraded.ots").read_bytes()
DIGEST = "0b27d12e50071e275c434d1837ac138b6865132b1ec02ba39174a73e4c3f7ece"
ROOTS = {
    967193: "ececf3e183a0cfcd57ac28612737a9aad2062f93ec80cf581c6b45dc1335cb8c",
    967198: "ef9edaef5ba996a1d473df069629d896697c9ca792759439f074fbc7989dc858",
    967211: "f90ec5272af0de8975c4cb0b33035cf580c60ab1edd1c7961baa2c61b712668a",
}
STAMPED = datetime(2026, 9, 15, 22, 11, 48, tzinfo=UTC)


def chain(roots=ROOTS):
    return lambda height: roots[height]


def down(height):
    raise TimeoutError("explorer down")


def stamped(tmp_path: Path, body: bytes = PENDING, digest: str = DIGEST) -> Path:
    path = tmp_path / "2026-09-15.ndjson.ots"
    path.write_bytes(body)
    sidecar = {"sha256": digest, "stamped_at_utc_local_clock": STAMPED.isoformat()}
    (tmp_path / "2026-09-15.ndjson.timestamps.json").write_text(json.dumps(sidecar))
    return path


def run(path, *, upgrade=lambda body: UPGRADED, explorers=None, hours=10, **kw):
    return proofs.sweep(
        [path],
        upgrade=upgrade,
        explorers=explorers or {"a": chain(), "b": chain()},
        now=lambda: STAMPED + timedelta(hours=hours),
        **kw,
    )


def test_read_tells_pending_from_complete():
    assert proofs.read(PENDING) == proofs.Proof(DIGEST, ())
    assert proofs.read(UPGRADED).anchors == tuple(sorted(ROOTS.items()))


def test_is_upgrade_of_accepts_only_the_same_digest_newly_anchored():
    assert proofs.is_upgrade_of(UPGRADED, PENDING)
    assert not proofs.is_upgrade_of(PENDING, UPGRADED)
    assert not proofs.is_upgrade_of(UPGRADED, UPGRADED)
    assert not proofs.is_upgrade_of(b"garbage", PENDING)


def test_a_confirmed_upgrade_replaces_the_proof_in_place(tmp_path: Path):
    path = stamped(tmp_path)
    [line] = run(path)
    assert line.ok and line.changed and "967193, 967198, 967211 confirmed by a, b" in line.detail
    assert path.read_bytes() == UPGRADED
    assert run(path) == []  # complete proofs are skipped unless verify_all


def test_a_contradicted_upgrade_is_a_fault_and_is_not_kept(tmp_path: Path):
    path = stamped(tmp_path)
    [line] = run(path, explorers={"a": chain(), "b": chain({**ROOTS, 967198: "00" * 32})})
    assert not line.ok and "contradicted" in line.detail and "b reports" in line.detail
    assert path.read_bytes() == PENDING


def test_an_unreachable_explorer_holds_the_upgrade_until_the_proof_is_stale(tmp_path: Path):
    path = stamped(tmp_path)
    [line] = run(path, explorers={"a": chain(), "b": down})
    assert line.ok and not line.changed and "upgrade held" in line.detail
    assert path.read_bytes() == PENDING
    [line] = run(path, explorers={"a": chain(), "b": down}, hours=49)
    assert not line.ok and "over 48 h" in line.detail


def test_a_proof_calendars_have_not_anchored_is_fine_until_48_hours(tmp_path: Path):
    path = stamped(tmp_path)
    [line] = run(path, upgrade=lambda body: body, hours=47)
    assert line.ok and "not anchored it yet" in line.detail
    [line] = run(path, upgrade=lambda body: body, hours=49)
    assert not line.ok
    [line] = run(path, upgrade=lambda body: (_ for _ in ()).throw(OSError("no ots")), hours=1)
    assert line.ok and "upgrade failed: OSError" in line.detail


def test_a_proof_for_other_bytes_than_its_sidecar_is_a_fault(tmp_path: Path):
    path = stamped(tmp_path, digest="ab" * 32)
    [line] = run(path)
    assert not line.ok and "not the sidecar's" in line.detail
    assert path.read_bytes() == PENDING


def test_verify_all_reconfirms_complete_proofs(tmp_path: Path):
    path = stamped(tmp_path, UPGRADED)
    [line] = run(path, verify_all=True)
    assert line.ok and line.detail.startswith("confirmed")
    [line] = run(path, verify_all=True, explorers={"a": chain({**ROOTS, 967211: "ff" * 32})})
    assert not line.ok


def test_watchdog_keeps_a_local_upgrade_and_still_flags_divergence(tmp_path: Path):
    from grid_mysteries.capture import watchdog as wd
    from grid_mysteries.capture.store import LocalStore

    store = LocalStore(tmp_path / "bucket")
    store.put("proofs/2026-09-15.ndjson.ots", PENDING)
    store.put("proofs/2026-09-16.ndjson.ots", PENDING)
    local = tmp_path / "repo/data/manifests"
    local.mkdir(parents=True)
    (local / "2026-09-15.ndjson.ots").write_bytes(UPGRADED)
    (local / "2026-09-16.ndjson.ots").write_bytes(PENDING + b"x")
    assert wd.sync(store, tmp_path / "repo") == [
        f"MISMATCH proofs/2026-09-16.ndjson.ots -> {local / '2026-09-16.ndjson.ots'}"
    ]
    assert (local / "2026-09-15.ndjson.ots").read_bytes() == UPGRADED
