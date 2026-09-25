"""tracker.json rows -> add_day proposal rows (NDJSON on stdout)."""

import hashlib
import json
import sys
from pathlib import Path

tracker = json.loads(Path(sys.argv[1]).read_text())
rule = tracker["declaration_sha256"][:16]


def v(x: object) -> str:
    return "-" if x is None else str(x)


for r in tracker["rows"]:
    digests = sorted(a["sha256"] for a in r.get("artefacts", []))
    args = {
        "day": r["settlement_date"],
        "rule": rule,
        "source": r["source"],
        "paid_out_gbp": v(r["paid_out_gbp"]),
        "net_gbp": v(r["net_gbp"]),
        "wind_bid_gbp": v(r["wind_bid_gbp"]),
        "gas_offer_gbp": v(r["gas_offer_gbp"]),
        "other_gbp": v(r["other_gbp"]),
        "two_cut_gbp": v(r["two_cut_gbp"]),
        "sign": "holds" if r["sign_convention_holds"] else "fails",
        "disptav_type": v(r.get("disptav_type")),
        "gas_offer_vwap": v(r.get("gas_offer_vwap_gbp_per_mwh")),
        "premium": v(r.get("premium_gbp_per_mwh")),
        "bsad_net_gbp": v(r.get("bsad_net_gbp")),
        "artefacts_digest": hashlib.sha256("\n".join(digests).encode()).hexdigest(),
    }
    print(json.dumps({"transformation": "add_day", "actor": "kill_test", "args_named": args}))
