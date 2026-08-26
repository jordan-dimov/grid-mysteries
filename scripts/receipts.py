"""Assertions on Morpholog propose receipts, shared by the control, replay
and rehearsal scripts.

A receipt is the JSON object `morpholog propose` prints per row:
``status`` is ``committed`` or ``rejected``, and a rejection names the
refusing ``rule``. Assertions key on those two fields, never on prose.
Stdlib only: the rehearsal runs these under plain ``python3``, and the
receipt always arrives on stdin or as a parsed object, never spliced
into source text.

Command line:
    receipts.py committed <label>            one receipt on stdin
    receipts.py rule <rule> <label>          one receipt on stdin
    receipts.py all-committed <failure> [<indent>]   NDJSON on stdin
    receipts.py rules <expected-rules.json>          NDJSON on stdin
"""

import json
import sys


def expect_committed(receipt: dict, label: str) -> None:
    if receipt.get("status") != "committed":
        raise SystemExit(f"{label}: expected commit, got {receipt}")


def expect_rule(receipt: dict, rule: str, label: str) -> None:
    if receipt.get("status") != "rejected":
        raise SystemExit(f"{label}: expected rejection, got {receipt}")
    if receipt.get("rule") != rule:
        raise SystemExit(f"{label}: expected rule {rule!r}, got {receipt.get('rule')!r}")


def expect_all_committed(receipts: list[dict], failure: str) -> None:
    """Every receipt of a batch committed; otherwise print the offenders
    and exit with `failure`."""
    bad = [receipt for receipt in receipts if receipt.get("status") != "committed"]
    if bad:
        print(json.dumps(bad, indent=1))
        raise SystemExit(failure)


def expect_rules(receipts: list[dict], expected: dict[str, str]) -> list[str]:
    """Each receipt rejected by the rule expected for its row id; one
    failure line per deviation, plus one if the counts differ."""
    failures = []
    for receipt in receipts:
        row_id = str(receipt.get("row"))
        want = expected.get(row_id)
        if receipt.get("status") != "rejected":
            failures.append(f"row {row_id}: expected rejection, got {receipt.get('status')}")
        elif receipt.get("rule") != want:
            failures.append(f"row {row_id}: expected rule {want!r}, got {receipt.get('rule')!r}")
    if len(receipts) != len(expected):
        failures.append(f"{len(receipts)} receipts for {len(expected)} expected rows")
    return failures


def read_ndjson(stream) -> list[dict]:
    return [json.loads(line) for line in stream if line.strip()]


def main(argv: list[str]) -> None:
    match argv:
        case ["committed", label]:
            expect_committed(json.load(sys.stdin), label)
            print(f"   OK  {label}")
        case ["rule", rule, label]:
            expect_rule(json.load(sys.stdin), rule, label)
            print(f"   OK  {label} (rule {rule})")
        case ["all-committed", failure, *rest]:
            receipts = read_ndjson(sys.stdin)
            expect_all_committed(receipts, failure)
            indent = rest[0] if rest else "   "
            print(f"{indent}{len(receipts)} committed")
        case ["rules", expected_path]:
            with open(expected_path) as handle:
                expected = json.load(handle)
            receipts = read_ndjson(sys.stdin)
            failures = expect_rules(receipts, expected)
            if failures:
                raise SystemExit("controls: LOCKS DID NOT LOCK\n" + "\n".join(failures))
            print(f"   {len(receipts)} refused, every rule as expected")
        case _:
            raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
