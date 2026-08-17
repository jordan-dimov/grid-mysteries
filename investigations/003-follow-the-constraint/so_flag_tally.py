"""Descriptive SO-flag tally over the selected episode's dates.

Post-selection description (like the accounting): counts distinct
(unit, acceptanceNumber) BOALF acceptances for the declared GB storage
universe over 2026-05-18..31 and how many carry ``soFlag`` on any row.
Motivated by NESO's RRT identification methodology (pinned Ofgem paper,
June 2026), whose second criterion admits only system-flagged bid
acceptances. Output: evidence/so-flag-tally.json.
"""

from __future__ import annotations

import json

from acquire import EVIDENCE, RAW
from select_episode import storage_universe

from grid_mysteries.corpus import PERIODS, load_records

EPISODE_DATES = [f"2026-05-{day:02d}" for day in range(18, 32)]
FOCUS_UNIT = "E_DOLLB-1"


def run() -> None:
    mapped, _ = storage_universe()
    units = set(mapped)
    acceptances: dict[tuple[str, int], bool] = {}
    for day in EPISODE_DATES:
        for period in PERIODS:
            for r in load_records(RAW / day / f"boalf_p{period:02d}.json"):
                unit = str(r["bmUnit"])
                if unit in units:
                    key = (unit, int(r["acceptanceNumber"]))
                    acceptances[key] = acceptances.get(key, False) or bool(r["soFlag"])
    focus = [(n, v) for (u, n), v in acceptances.items() if u == FOCUS_UNIT]
    out = {
        "scope": (
            "GB-wide declared storage universe, episode dates 2026-05-18..31, "
            "distinct (unit, acceptanceNumber)"
        ),
        "storage_acceptances": len(acceptances),
        "storage_acceptances_so_flagged": sum(1 for v in acceptances.values() if v),
        "storage_units_with_acceptances": len({u for (u, _) in acceptances}),
        "storage_units_with_so_flagged_acceptances": len(
            {u for (u, n), v in acceptances.items() if v}
        ),
        f"focus_unit_{FOCUS_UNIT}_acceptances": len(focus),
        f"focus_unit_{FOCUS_UNIT}_so_flagged": sum(1 for _, v in focus if v),
    }
    (EVIDENCE / "so-flag-tally.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    run()
