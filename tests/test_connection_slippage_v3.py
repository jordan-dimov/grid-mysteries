"""014 declaration version 3: the determined part, the two named rules, F4 and F5."""

import hashlib
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from grid_mysteries.investigations import connection_slippage as cs
from grid_mysteries.investigations import connection_slippage_v3 as v3
from grid_mysteries.tec import analysis

DECLARATION = Path(__file__).parents[1] / (
    "investigations/014-gb-connection-slippage/DECLARATION-v3.md"
)


def row(name, stage, mw, eff):
    return {
        "Project Name": name,
        "Customer Name": "C",
        "Connection Site": "S",
        "Stage": stage,
        "MW Increase / Decrease": mw,
        "MW Effective From": date.fromisoformat(eff),
    }


def copy(day, rows):
    return cs.VintageInput(date.fromisoformat(day), tuple(rows), day, f"{day}.csv")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------------- F5


def test_the_frozen_declaration_states_the_content_rules_digest_and_it_matches():
    stated = v3.declared_rule_digest(DECLARATION.read_text())
    assert stated == digest(v3.CONTENT_RULE_FILE)


def test_f5_a_changed_content_rule_file_refuses(tmp_path):
    changed = tmp_path / "identity.py"
    changed.write_text(v3.CONTENT_RULE_FILE.read_text() + "\n# a changed rule\n")
    with pytest.raises(v3.ContentRuleChanged, match="F5"):
        v3.series(
            [copy("2020-01-01", [row("A", "1", 10, "2025-01-01")])],
            rule_digest=digest(v3.CONTENT_RULE_FILE),
            rule_file=changed,
        )


# ------------------------------------------------------------------- F4


def two_stage_history():
    a = [row("A", "1", 10, "2025-01-01"), row("A", "2", 20, "2026-01-01")]
    b = [row("A", "1", 10, "2025-06-01"), row("A", "2", 20, "2026-01-01")]
    return [copy("2020-01-01", a), copy("2020-02-01", b)]


def test_the_determined_part_is_the_same_under_both_rules_and_is_reported():
    result = v3.series(two_stage_history(), rule_digest=digest(v3.CONTENT_RULE_FILE))
    link = result["segments"][0]["rows"][1]["v3"]["vs_previous"]
    assert link["undetermined_groups"] == 0
    assert link["determined"] == link["total"][v3.RULE_V2] == link["total"][v3.RULE_CONTENT]
    assert link["determined"] > 0


def test_f4_a_planted_disagreement_on_a_determined_group_refuses():
    def re_pairing_rule(kept):
        # The content rule, then stage 1's date swapped with stage 2's in the
        # current copy: a different pairing of a group the labels determine.
        out = analysis.entries_content(kept)
        k, entries = out[-1]
        one, two = sorted(entries)
        swapped = {
            one: replace(entries[one], effective=entries[two].effective),
            two: replace(entries[two], effective=entries[one].effective),
        }
        return [*out[:-1], (k, swapped)]

    with pytest.raises(v3.RuleDisagreement, match="F4"):
        v3.series(
            two_stage_history(),
            rule_digest=digest(v3.CONTENT_RULE_FILE),
            content_entries=re_pairing_rule,
        )


def test_f4_fires_on_a_group_restructured_between_two_determined_ends():
    # Barry Power Station's shape (2015-16): one row at each end, a second
    # row in between; the carried content rule follows the rows, version 2's
    # rule pairs the two ends. Recorded in AMENDMENTS.md, 2026-09-23.
    history = [
        copy("2015-04-13", [row("B", None, -136, "2016-04-01")]),
        copy(
            "2016-03-07",
            [row("B", None, -235, "2016-04-01"), row("B", None, 235, "2018-04-01")],
        ),
        copy("2016-04-12", [row("B", None, 235, "2018-04-01")]),
    ]
    with pytest.raises(v3.RuleDisagreement, match="F4"):
        v3.series(history, rule_digest=digest(v3.CONTENT_RULE_FILE))


def test_equal_movements_summed_in_another_order_are_not_a_disagreement():
    def entry(key, mw, a, b):
        return (
            cs.Entry(key, "g", str(key), Decimal(mw), date.fromisoformat(a), a),
            cs.Entry(key, "g", str(key), Decimal(mw), date.fromisoformat(b), b),
        )

    specs = [("x", "43.5", "2024-06-30"), ("y", "42", "2024-06-30"), ("z", "10.5", "2029-06-30")]
    pairs = {k: entry(k, mw, a, "2026-06-01") for k, mw, a in specs}
    v2 = ({k: p[0] for k, p in pairs.items()}, {k: p[1] for k, p in pairs.items()})
    reordered = (
        {k: v2[0][k] for k in reversed(list(v2[0]))},
        {k: v2[1][k] for k in reversed(list(v2[1]))},
    )
    rows: list[dict[str, object]] = [
        {"Project Name": "g", "Stage": s, "Customer Name": "", "Connection Site": ""} for s in "123"
    ]
    out = v3.split(
        v2, reordered, (rows, rows), baseline=date(2024, 10, 15), current=date(2024, 10, 22)
    )
    assert out["total"][v3.RULE_V2] == out["total"][v3.RULE_CONTENT]
