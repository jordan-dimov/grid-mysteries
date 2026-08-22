"""Replay v2 batches as the login roles the record itself names.

v2's actor policy binds each actor to an exact PostgreSQL `session_user`,
so a replay connecting as some other role has every governed row refused
— the batches would stop being replayable the moment governance is
established. This helper closes that: it reads the actor->login-role
mapping out of the committed `establish_governance` row, provisions those
roles in the DISPOSABLE replay database, and proposes each row through
the connection whose session_user matches the row's actor.

Ordering is preserved (row by row, batch by batch); the mapping is taken
from the record, never hardcoded, so a future rename replays correctly.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

PROGRAMME = "morpholog/research-v2-draft.morph"
REPLAY_PASSWORD = "replay-only-disposable"


def run(argv: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, **kwargs)


def role_url(base_url: str, role: str) -> str:
    """The base URL rewritten to connect as ``role`` over TCP."""
    parts = urlsplit(base_url)
    host = parts.hostname or "localhost"
    port = parts.port or 5432
    database = parts.path.lstrip("/")
    return f"postgres://{role}:{REPLAY_PASSWORD}@{host}:{port}/{database}"


def actor_roles(batches: list[Path]) -> dict[str, str]:
    """actor -> login role, read from the committed governance bootstrap."""
    for batch in batches:
        for line in batch.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row["transformation"] == "establish_governance":
                args = row["args_named"]
                return {
                    args["human_actor"]: args["human_login_role"],
                    args["machine_actor"]: args["machine_login_role"],
                }
    return {}


def provision(base_url: str, roles: set[str]) -> None:
    """Create the replay login roles, and NEVER touch one that exists.

    PostgreSQL roles are CLUSTER-wide, not per-database: dropping or
    recreating a role here would rewrite the credentials of the real
    deployment's roles of the same name, on the same cluster. So a role
    that already exists is a hard stop — replay belongs on a disposable
    cluster (CI's service container), never alongside production.
    """
    existing = run(
        [
            "psql",
            base_url,
            "-tAc",
            "select rolname from pg_roles where rolname = any(%s)"
            % ("array[" + ",".join(f"'{r}'" for r in sorted(roles)) + "]"),
        ]
    )
    if existing.returncode != 0:
        raise SystemExit(f"could not inspect roles: {existing.stderr.strip()}")
    clash = sorted(name for name in existing.stdout.split() if name)
    if clash:
        raise SystemExit(
            "refusing to provision replay roles: "
            + ", ".join(clash)
            + " already exist on this PostgreSQL cluster.\n"
            "Roles are cluster-wide, so creating them here would rewrite the real "
            "deployment's credentials. Run the v2 replay against a DISPOSABLE cluster "
            "(as CI does with its postgres service container), not the cluster that "
            "hosts the research database."
        )
    statements = []
    for role in sorted(roles):
        statements += [
            f"CREATE ROLE {role} LOGIN PASSWORD '{REPLAY_PASSWORD}';",
            f"GRANT USAGE ON SCHEMA morpholog TO {role};",
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA morpholog TO {role};",
            f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA morpholog TO {role};",
        ]
    result = run(["psql", base_url, "-q", "-v", "ON_ERROR_STOP=1", "-c", " ".join(statements)])
    if result.returncode != 0:
        raise SystemExit(f"could not provision replay roles: {result.stderr.strip()}")


def main() -> None:
    base_url, *batch_paths = sys.argv[1:]
    batches = [Path(p) for p in batch_paths]
    mapping = actor_roles(batches)
    if not mapping:
        raise SystemExit("no establish_governance row found; cannot learn the actor bindings")
    provision(base_url, set(mapping.values()))
    urls = {actor: role_url(base_url, role) for actor, role in mapping.items()}

    for batch in batches:
        rows = [json.loads(line) for line in batch.read_text().splitlines() if line.strip()]
        for index, row in enumerate(rows, start=1):
            actor = row["actor"]
            # The bootstrap runs before any policy exists; every later row
            # must go through the role its actor is bound to.
            url = urls.get(actor, base_url)
            result = run(
                [
                    "morpholog",
                    "propose",
                    PROGRAMME,
                    row["transformation"],
                    "--actor",
                    actor,
                    "--args-named",
                    json.dumps(row["args_named"]),
                    "--database-url",
                    url,
                ]
            )
            receipt = json.loads(result.stdout) if result.stdout.strip() else {}
            if receipt.get("status") != "committed":
                raise SystemExit(
                    f"replay: {batch.name} row {index} ({row['transformation']}, actor {actor}) "
                    f"did not commit: {result.stdout.strip() or result.stderr.strip()}"
                )
        print(f"     {len(rows)} committed (as the record's own login roles)")


if __name__ == "__main__":
    main()
