"""scripts/freeze, run in a throwaway repository with the witnesses stubbed:
the co-author trailer comes from --co-author or FREEZE_CO_AUTHOR, never from
the script, and a malformed one is refused before anything is stamped."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

FREEZE = Path(__file__).parent.parent / "scripts" / "freeze"
STUB_TIMESTAMP = """#!/usr/bin/env bash
set -e
for ext in ots tsq freetsa.tsr digicert.tsr timestamps.json; do echo stub > "$1.$ext"; done
"""
DECL = "investigations/999-test/DECLARATION.md"


@pytest.fixture
def repo(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy(FREEZE, scripts / "freeze")
    (scripts / "timestamp").write_text(STUB_TIMESTAMP)
    (scripts / "verify-timestamp").write_text("#!/usr/bin/env bash\nexit 0\n")
    for s in scripts.iterdir():
        s.chmod(0o755)
    decl = tmp_path / DECL
    decl.parent.mkdir(parents=True)
    decl.write_text("# 999 declaration\n")
    git = ["git", "-C", str(tmp_path)]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "config", "user.name", "Sponsor"], check=True)
    subprocess.run([*git, "config", "user.email", "sponsor@example.org"], check=True)
    subprocess.run([*git, "config", "commit.gpgsign", "false"], check=True)
    return tmp_path


def freeze(repo, *args, env_co_author=None):
    env = {k: v for k, v in os.environ.items() if k != "FREEZE_CO_AUTHOR"}
    if env_co_author is not None:
        env["FREEZE_CO_AUTHOR"] = env_co_author
    return subprocess.run(
        [str(repo / "scripts" / "freeze"), *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )


def last_message(repo):
    return subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--format=%B"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_the_co_author_argument_becomes_the_trailer(repo):
    out = freeze(repo, "--co-author", "Claude Opus 5.5 <noreply@anthropic.com>", DECL, "999 frozen")
    assert out.returncode == 0, out.stderr
    message = last_message(repo)
    assert message.startswith("999 frozen\n\n")
    assert message.strip().endswith("Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    assert "Fable" not in message


def test_the_argument_wins_over_the_environment_and_the_equals_form_works(repo):
    out = freeze(
        repo, DECL, "--co-author=A Session <a@example.org>", env_co_author="Other <o@example.org>"
    )
    assert out.returncode == 0, out.stderr
    assert last_message(repo).strip().endswith("Co-Authored-By: A Session <a@example.org>")


def test_the_environment_names_the_co_author_when_no_argument_does(repo):
    out = freeze(repo, DECL, env_co_author="Env Session <env@example.org>")
    assert out.returncode == 0, out.stderr
    assert last_message(repo).strip().endswith("Co-Authored-By: Env Session <env@example.org>")


def test_with_no_co_author_the_commit_has_no_trailer_and_the_default_message(repo):
    out = freeze(repo, DECL)
    assert out.returncode == 0, out.stderr
    message = last_message(repo)
    assert "Co-Authored-By" not in message
    assert message.startswith("999-test: frozen declaration (SHA-256 ")


def test_a_malformed_co_author_is_refused_before_anything_is_stamped(repo):
    for bad in ("Claude", "<noreply@anthropic.com>", "Claude noreply@anthropic.com", "C <x>"):
        out = freeze(repo, "--co-author", bad, DECL)
        assert out.returncode != 0 and "co-author must read" in out.stderr
        assert not (repo / f"{DECL}.ots").exists()


def test_a_frozen_declaration_is_not_frozen_again(repo):
    assert freeze(repo, DECL).returncode == 0
    again = freeze(repo, "--co-author", "S <s@example.org>", DECL)
    assert again.returncode != 0 and "not re-stamped" in again.stderr
