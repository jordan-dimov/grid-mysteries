"""017 — the outbound document and the facts it is allowed to state.

    uv run python investigations/017-the-overdue-queue/render_post.py

Writes `evidence/post-facts.json` (one entry per BEDROCK candidate slot,
each with the exact sentence it licenses and the artefacts behind it) and
`drafts/post-<run date>.md`, the draft that quotes them. Both are pure
functions of the committed evidence and of the certificates 014 issued;
neither posts anything.
"""

import json
import sys
from pathlib import Path

from grid_mysteries.corpus import REPO_ROOT
from grid_mysteries.evidence import write_json
from grid_mysteries.rendering import overdue_queue as page

HERE = Path(__file__).parent
CENSUS_JSON = HERE / "evidence" / "census.json"
FACTS_JSON = HERE / "evidence" / "post-facts.json"
DRAFTS = HERE / "drafts"


def main() -> None:
    sys.path.insert(0, str(HERE))
    from run import certificates  # noqa: PLC0415 - the runner owns bundle reading

    census = json.loads(CENSUS_JSON.read_text())
    certs = certificates()
    write_json(FACTS_JSON, page.post_facts(census, certs))
    DRAFTS.mkdir(exist_ok=True)
    draft = DRAFTS / f"post-{census['run_date']}.md"
    draft.write_text(page.render_post(census, certs))
    print(f"wrote {FACTS_JSON.relative_to(REPO_ROOT)} and {draft.relative_to(REPO_ROOT)}")
    print("Draft only. Nothing is posted.")


if __name__ == "__main__":
    sys.exit(main())
