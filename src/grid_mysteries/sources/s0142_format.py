"""The format of an S0142 file as 018's reader depends on it, and nothing else.

The schema pass (``scripts/schema-report s0142``) profiles a few files in
full, values included, before a declaration is written. The acquisition then
fetches many files nobody has seen, and on 2026-10-03 eight of 144 began with
a byte-order mark the schema pass never met; the compute found it by crashing
part-way through, after rows had been written. This profile is read between
acquisition and compute: encoding, the flow version, and the field counts of
the record types the reader uses. It reads no value: no amount, no sign, no
party, no count of lines.
"""

import gzip
from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path

BOM = b"\xef\xbb\xbf"
#: The record types `p415_compensation.summarise` reads.
READ = (b"AAA", b"SRH", b"SPI", b"BPH", b"SP7", b"BP7", b"APC", b"ZZZ")


def profile(lines: Iterable[bytes]) -> dict:
    """One file's lines (bytes, as stored) to its format facts."""
    leading_bom = False
    non_ascii_lines = 0
    flow = None
    widths: dict[str, set[int]] = defaultdict(set)
    first = True
    for line in lines:
        if first:
            first = False
            if line.startswith(BOM):
                leading_bom, line = True, line[len(BOM) :]
        if not line.isascii():
            non_ascii_lines += 1
            continue
        rid = line[:3]
        if rid not in READ or line[3:4] != b"|":
            continue
        fields = line.rstrip(b"\r\n").count(b"|")  # the trailing pipe ends the last field
        widths[rid.decode()].add(fields)
        if rid == b"AAA" and flow is None:
            flow = line.split(b"|")[1].decode()
    return {
        "leading_byte_order_mark": leading_bom,
        "non_ascii_lines": non_ascii_lines,
        "flow_version": flow,
        "field_counts": {r: sorted(w) for r, w in sorted(widths.items())},
    }


def profile_file(path: Path) -> dict:
    with gzip.open(path, "rb") as fh:
        return profile(fh)


def differences(expected: Mapping, seen: Mapping) -> list[str]:
    """How a file's format departs from the expected (the schema pass's):
    a mark, a non-ASCII line, another flow version, a record type read but
    absent, or a field count not met before. Each is named, never judged."""
    out = []
    if seen["leading_byte_order_mark"] and not expected["leading_byte_order_mark"]:
        out.append("leading byte-order mark")
    if seen["non_ascii_lines"] > expected["non_ascii_lines"]:
        out.append(f"{seen['non_ascii_lines']} line(s) with a non-ASCII byte")
    if seen["flow_version"] != expected["flow_version"]:
        out.append(f"flow version {seen['flow_version']} (expected {expected['flow_version']})")
    for rid in expected["field_counts"]:
        if rid not in seen["field_counts"]:
            out.append(f"no {rid} record")
    for rid, widths in seen["field_counts"].items():
        new = sorted(set(widths) - set(expected["field_counts"].get(rid, [])))
        if new:
            out.append(f"{rid} with {', '.join(map(str, new))} field(s)")
    return out


def expected_from(profiles: Iterable[Mapping]) -> dict:
    """The union of the schema pass's files: what has been seen."""
    ps = list(profiles)
    widths: dict[str, set[int]] = defaultdict(set)
    for p in ps:
        for rid, w in p["field_counts"].items():
            widths[rid].update(w)
    flows = {p["flow_version"] for p in ps}
    if len(flows) != 1:
        raise ValueError(f"the schema pass's files print {len(flows)} flow versions")
    return {
        "leading_byte_order_mark": any(p["leading_byte_order_mark"] for p in ps),
        "non_ascii_lines": max(p["non_ascii_lines"] for p in ps),
        "flow_version": flows.pop(),
        "field_counts": {r: sorted(w) for r, w in sorted(widths.items())},
    }
