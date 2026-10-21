"""Kill test 2: offer a recomputed tracker back to a second-shape Bill record
and let the kernel say, per day and per block, which figure moved.

    uv run python bill/kill-test-2/offer.py <tracker.json> <database_url> \
        bill/kill-test-2/bill-register-reaffirm.morph

Every available day becomes reaffirm_day / reaffirm_gas_offer / reaffirm_bsad
proposals (the figures the importer would record, via importer.day_claims);
the scratch programme's gates compare each offered figure with the held one.
A receipt is: committed (identical), rejected by a named gate with both
values (the figure moved), or bind failed (the record holds no such block).
"""

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

from grid_mysteries.bill import importer

tracker_path, url, programme = sys.argv[1:4]
tracker = json.loads(Path(tracker_path).read_text())


def q(amount, unit):
    return {"type": "quantity", "value": {"amount": amount, "unit": unit}}


def sub(v):
    return {"type": "subject", "value": v}


def dt(v):
    return {"type": "date", "value": v}


def dec(v):
    return {"type": "decimal", "value": v}


rows = []
for r in tracker["rows"]:
    if not r.get("available"):
        continue
    day, rule = r["settlement_date"], importer.rule_of(r)
    c = importer.day_claims(r)
    d = c["Day"]
    rows.append(
        {
            "transformation": "reaffirm_day",
            "actor": "kill_test_2",
            "day": day,
            "args": [
                dt(day),
                sub(rule),
                *[q(d[f], "GBP") for f in importer.MONEY_FIELDS],
                sub(d["artefacts_sha256"]),
            ],
        }
    )
    g = c["DayGasOffer"]
    if g:
        rows.append(
            {
                "transformation": "reaffirm_gas_offer",
                "actor": "kill_test_2",
                "day": day,
                "args": [
                    dt(day),
                    sub(rule),
                    sub(g["disptav_type"]),
                    q(g["offer_mwh"], "MWh"),
                    *[
                        q(g[f], "GBP_per_MWh")
                        for f in (
                            "offer_vwap_gbp_per_mwh",
                            "mid_vwap_gbp_per_mwh",
                            "premium_gbp_per_mwh",
                        )
                    ],
                ],
            }
        )
    b = c["DayBsad"]
    if b:
        rows.append(
            {
                "transformation": "reaffirm_bsad",
                "actor": "kill_test_2",
                "day": day,
                "args": [
                    dt(day),
                    sub(rule),
                    sub(b["vintage"]),
                    q(b["net_gbp"], "GBP"),
                    dec(b["share"]),
                ],
            }
        )
batch = "\n".join(json.dumps({k: v for k, v in x.items() if k != "day"}) for x in rows) + "\n"
out = subprocess.run(
    [
        os.environ.get("MORPHOLOG_BIN", "morpholog"),
        "propose",
        programme,
        "--batch",
        "-",
        "--database-url",
        url,
        "--explain-on-reject",
    ],
    input=batch,
    capture_output=True,
    text=True,
    check=True,
).stdout
receipts = [json.loads(line) for line in out.splitlines() if line.strip()]
tally = Counter()


def val(v):
    if v is None:
        return "?"
    if v.get("type") == "quantity":
        return f"{v['value']['amount']} {v['value']['unit']}"
    return str(v.get("value"))


for row, rc in zip(rows, receipts, strict=True):
    who = f"{row['day']} {row['transformation'].removeprefix('reaffirm_')}"
    st = rc.get("status")
    if st == "committed":
        tally["identical"] += 1
        continue
    if st == "rejected":
        rule = rc.get("rule")
        cmp = rc.get("compared")
        if cmp:
            tally["figure moved"] += 1
            left, op, right = val(cmp.get("left")), cmp.get("op"), val(cmp.get("right"))
            print(f"  MOVED   {who}: {rule}: record {left} {op} offered {right}")
        else:
            tally["refused"] += 1
            print(f"  REFUSED {who}: {rule}: {rc.get('reason', '')[:100]}")
    else:
        tally["no such block"] += 1
        print(f"  ABSENT  {who}: {rc.get('code') or rc.get('reason', '')[:100]}")
print(f"{len(rows)} offered: " + ", ".join(f"{v} {k}" for k, v in tally.items()))
