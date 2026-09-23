"""As-of TEC record certificates: what the register printed about a project.

Pure assembly; the CLI does the I/O. For each date asked about, a
certificate relies on the latest publication the record holds on or before
it. That is not necessarily the one NESO had in force, because the archive
has gaps, so the certificate states the days between the two, flags more
than 60, and names any copy held for the interval that the record does not
include. It gives the transition that closed that publication's import and
the project's lines exactly as the record holds them: kinds, cells, record
key and line number. Between the first and last date it lists every
publication in which the project's lines changed (a line printed or no
longer printed), which is a statement about the record, not about identity.
It forecasts nothing and says nothing about entitlement.

Matching follows the existing certificate rule (`connection_record`): the
register's normalised project name and, where given, stage.
"""

from datetime import date
from typing import Any, Final

from grid_mysteries.sources.tec_register import normalise, normalise_stage
from grid_mysteries.tec import cells
from grid_mysteries.tec.replay import Publication

#: The stdlib-only script shipped in every bundle: fold the verified pack and
#: print the project's lines as of each closing transition.
LINES_FROM_PACK: Final = '''#!/usr/bin/env python3
"""Re-derive this certificate's lines from the pack alone (standard library).

    python3 lines_from_pack.py pack.json certificate.json

Folds the pack's transitions in order, keeping the Row claims, and at each
closing transition the certificate names prints the rows whose project name
(and stage, if the certificate names one) match. Run it after verify-pack."""
import json, re, sys
from decimal import Decimal, InvalidOperation

pack = json.load(open(sys.argv[1]))
cert = json.load(open(sys.argv[2]))
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()
def stage(s):
    s = str(s or "").strip()
    try:
        d = Decimal(s.replace(",", ""))
    except InvalidOperation:
        return s
    whole = d == d.to_integral_value()
    return str(d.normalize().to_integral_value()) if whole else str(d.normalize())
wanted = {}
for a in cert["as_of"]:
    if a.get("close_transition"):
        wanted.setdefault(a["close_transition"], []).append(a)
held = {}
ok = True
for row in pack["rows"]:
    for c in row["retracted_claims"]:
        if c["predicate"] == "Row":
            held.pop(c["args"][0]["value"], None)
    for c in row["asserted_claims"]:
        if c["predicate"] == "Row":
            held[c["args"][0]["value"]] = [a["value"] for a in c["args"]]
    for a in wanted.get(row["transition_id"], []):
        lines = sorted(
            k for k, v in held.items()
            if norm(v[3]) == norm(cert["project"])
            and (cert["stage"] is None or stage(v[6]) == stage(cert["stage"]))
        )
        same = lines == sorted(line["row"] for line in a["lines"])
        ok = ok and same
        print(f"{a['as_of']}: {len(lines)} line(s) in the pack, "
              f"{'as the certificate states' if same else 'DIFFERENT from the certificate'}")
sys.exit(0 if ok else 1)
'''


def matches(row: dict[str, object], project: str, stage: str | None) -> bool:
    if normalise(row.get("Project Name")) != normalise(project):
        return False
    return stage is None or normalise_stage(row.get("Stage")) == normalise_stage(stage)


def in_force(publications: list[Publication], on: date) -> Publication | None:
    candidates = [p for p in publications if p.published_on <= on]
    return candidates[-1] if candidates else None


def line(p: Publication, key: str, row: dict[str, object]) -> dict[str, Any]:
    kinds, values = cells.encode(row)
    return {
        "row": key,
        "line": p.keys.index(key) + 1,
        "kinds": kinds,
        "cells": dict(zip(cells.COLUMNS, values, strict=True)),
    }


def lines(p: Publication, project: str, stage: str | None) -> list[dict[str, Any]]:
    return [
        line(p, key, row)
        for key, row in zip(p.keys, p.rows, strict=True)
        if matches(row, project, stage)
    ]


def changes(
    publications: list[Publication], project: str, stage: str | None, start: date, end: date
) -> list[dict[str, Any]]:
    """Each publication after the one relied on for `start`, up to `end`, whose
    set of matching lines differs from the previous publication's: lines
    printed, and lines no longer printed."""
    first = in_force(publications, start)
    window = [
        p
        for p in publications
        if (first is None or p.published_on >= first.published_on) and p.published_on <= end
    ]
    out = []
    for before, after in zip(window, window[1:], strict=False):
        was = {
            k for k, r in zip(before.keys, before.rows, strict=True) if matches(r, project, stage)
        }
        now = {k for k, r in zip(after.keys, after.rows, strict=True) if matches(r, project, stage)}
        if now != was:
            out.append(
                {
                    "publication": after.vintage,
                    "published_on": after.published_on,
                    "sha256": after.sha256,
                    "close_transition": after.close_transition,
                    "previous": before.vintage,
                    "printed": sorted(now - was),
                    "no_longer_printed": sorted(was - now),
                }
            )
    return out


#: 014's hole rule: more than this many days between the publication a
#: certificate relies on and the date asked about is stated as a gap.
GAP_DAYS: Final = 60


def record(
    publications: list[Publication],
    project: str,
    stage: str | None,
    dates: list[date],
    provenance: dict[str, dict[str, Any]],
    not_in_record: list[tuple[date, str]] | None = None,
) -> dict[str, Any]:
    """The certificate's content. `provenance` maps a copy's sha256 to its
    journal or capture line; `not_in_record` lists copies we hold that the
    record does not (unreadable ones), as (publication date, sha256)."""
    as_of: list[dict[str, Any]] = []
    for on in dates:
        p = in_force(publications, on)
        if p is None:
            as_of.append({"as_of": on, "publication": None, "note": "no publication on or before"})
            continue
        found = lines(p, project, stage)
        days = (on - p.published_on).days
        unread = [
            {"published_on": d, "sha256": sha}
            for d, sha in sorted(not_in_record or [])
            if p.published_on < d <= on
        ]
        as_of.append(
            {
                "as_of": on,
                "publication": p.vintage,
                "published_on": p.published_on,
                "days_before": days,
                "gap": days > GAP_DAYS,
                "held_but_not_in_record": unread,
                "sha256": p.sha256,
                "file_format": p.file_format,
                "close_transition": p.close_transition,
                "provenance": provenance.get(p.sha256),
                "state": "absent"
                if not found
                else ("one line" if len(found) == 1 else f"{len(found)} lines"),
                "lines": found,
            }
        )
    window = sorted(dates)
    return {
        "project": project,
        "stage": stage,
        "dates": dates,
        "as_of": as_of,
        "changes": changes(publications, project, stage, window[0], window[-1]) if window else [],
        "publications_in_record": len(publications),
    }
