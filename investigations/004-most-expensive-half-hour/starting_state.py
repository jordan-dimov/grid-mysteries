"""Emit the p38/p39 door snapshot as traceable evidence.

Two governed metrics — the CCGT fleet's published headroom as the warned
window opened, and NESO's own stated margin exclusion — had no evidence
file behind them. A governed number nobody can trace to a file is the
hole `EvidenceMetric` exists to close, so this writes one.

Deterministic and post-selection: reads only pinned artefacts, changes
no earlier evidence file (their digests are bound in the record).
"""

from __future__ import annotations

import json
import re
from decimal import Decimal

from acquire import EVIDENCE, RAW

from grid_mysteries.corpus import BMUNITS_PATH, load_records, physical_path

DAY = "2026-06-24"
DOOR = 39  # first period of the originally warned 19:00-22:00 BST window


def run() -> None:
    fuel = {
        str(r["elexonBmUnit"]): (r.get("fuelType") or "unclassified")
        for r in load_records(BMUNITS_PATH)
    }
    fpn = {
        str(x["bmUnit"]): max(Decimal(str(x["levelFrom"])), Decimal(str(x["levelTo"])))
        for x in load_records(physical_path("PN", DAY, DOOR))
    }
    mel = {
        str(x["bmUnit"]): Decimal(str(x["levelTo"]))
        for x in load_records(physical_path("MELS", DAY, DOOR))
    }
    headroom: dict[str, Decimal] = {}
    for unit, scheduled in fpn.items():
        kind = fuel.get(unit, "unclassified")
        headroom[kind] = headroom.get(kind, Decimal(0)) + max(
            Decimal(0), mel.get(unit, Decimal(0)) - scheduled
        )

    # NESO's own stated exclusion, taken from the pinned warning text.
    warnings = load_records(RAW / DAY / "syswarn.json")
    excluded = []
    for record in warnings:
        text = str(record.get("warningText", ""))
        for match in re.finditer(r"(\d+)\s*MW of generation is excluded", text):
            excluded.append({"published": record["publishTime"], "megawatts": match.group(1)})

    out = {
        "labelling": (
            "Published headroom is MEL - FPN at the door period, aggregated by NESO fuel "
            "class. For intermittent generation MEL is an availability FORECAST, not firm "
            "deliverable capability (Investigation 002), so the wind figure is not callable "
            "capacity. The exclusion figures are NESO's own words in its published warning."
        ),
        "day": DAY,
        "door_period": DOOR,
        "published_headroom_mw_by_fuel": {
            k: str(v) for k, v in sorted(headroom.items(), key=lambda kv: -kv[1])
        },
        "neso_stated_margin_exclusion_mw": excluded,
        # The exclusion NESO stated in the notice that was live on the
        # selected day (reissued 2026-06-24 07:10), keyed so a governed
        # metric can point at it without depending on list order.
        "neso_stated_exclusion_mw_on_selected_day": next(
            (e["megawatts"] for e in excluded if e["published"].startswith("2026-06-24")),
            None,
        ),
    }
    (EVIDENCE / "starting-state.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"CCGT published headroom at p{DOOR}: {headroom.get('CCGT')} MW")
    print(f"NESO stated exclusions: {[e['megawatts'] for e in excluded]}")


if __name__ == "__main__":
    run()
