"""Record a tracker compute run in the Balancing Bill record, one transact.

The plan (`plan`) is pure: given what the record holds and the runner's
`tracker.json`, it names the run, adds the settlement days the record does
not yet hold under their rule version, appends the NESO outcomes and BSAD
readings that are new, records the propositions' verdicts as of the run,
and closes the run. A day the record already holds identically costs
nothing. A day the record holds under the same rule version with
*different* figures is reported by name and the run is refused before
anything is proposed; the kernel's `day_is_new` gate is the backstop.

The run (`run`) reads the record's own state first, so it resumes from
wherever the record is and never trusts a local log. The one transact is
guarded by the recovery marker of `grid_mysteries.record`.
"""

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Final

from grid_mysteries import record

RECORD: Final = record.Record(
    name="bill",
    programme=Path("bill/bill-register.morph"),
    actor="bill_importer",
    key_id="bill-2026",
)
act = RECORD.act
#: The rule version tracked days are computed under today: 013's declaration
#: (SHA-256 d20d5920…) with Amendment 1 (SHA-256 326cc5fe…) in force.
RULE: Final = "013-d20d5920-A1"
RULES: Final = {
    RULE: (
        "d20d59203e7b7fda174c2c6deb2807159687bd9ddea39fe760961af884416473",
        "A1 326cc5fee3cbeead72335519fafffca71f561404eafd8eebcc2837d32322e11c",
    ),
    "seed-012": (
        "a349ea80",
        "1-8 September 2026 as investigation 012 published them, copied, never recomputed",
    ),
}
DAY_FIELDS: Final = (
    "source",
    "batch",
    "flag",
    "paid_out_gbp",
    "net_gbp",
    "paid_in_gbp",
    "wind_bid_gbp",
    "gas_offer_gbp",
    "other_gbp",
    "two_cut_gbp",
    "sign",
    "disptav_type",
    "gas_offer_mwh",
    "gas_offer_vwap_gbp_per_mwh",
    "mid_vwap_gbp_per_mwh",
    "premium_gbp_per_mwh",
    "bsad_vintage",
    "bsad_net_gbp",
    "bsad_share",
    "artefacts_sha256",
)
PROPOSITIONS: Final = ("T1", "T2", "T3", "T4")


def text(value: object) -> str:
    """A cell as the record stores it: the runner's text, "-" where blank."""
    return "-" if value is None else str(value)


def artefacts_digest(row: dict[str, Any]) -> str:
    digests = sorted(str(a["sha256"]) for a in row.get("artefacts") or [])
    return hashlib.sha256("\n".join(digests).encode()).hexdigest()


def rule_of(row: dict[str, Any]) -> str:
    return "seed-012" if row.get("seed") else RULE


def day_values(row: dict[str, Any]) -> tuple[str, ...]:
    """The DayRow cells for a tracker row, in DAY_FIELDS order."""
    sign = row.get("sign_convention_holds")
    flag = "seed" if row.get("seed") else ("record" if row.get("record") else "none")
    values = {
        "source": text(row.get("source")),
        "batch": text(row.get("batch", 0)),
        "flag": flag,
        "paid_out_gbp": text(row.get("paid_out_gbp")),
        "net_gbp": text(row.get("net_gbp")),
        "paid_in_gbp": text(row.get("paid_in_gbp")),
        "wind_bid_gbp": text(row.get("wind_bid_gbp")),
        "gas_offer_gbp": text(row.get("gas_offer_gbp")),
        "other_gbp": text(row.get("other_gbp")),
        "two_cut_gbp": text(row.get("two_cut_gbp")),
        "sign": "-" if sign is None else ("holds" if sign else "fails"),
        "disptav_type": text(row.get("disptav_type")),
        "gas_offer_mwh": text(row.get("gas_offer_mwh")),
        "gas_offer_vwap_gbp_per_mwh": text(row.get("gas_offer_vwap_gbp_per_mwh")),
        "mid_vwap_gbp_per_mwh": text(row.get("mid_vwap_same_periods_gbp_per_mwh")),
        "premium_gbp_per_mwh": text(row.get("premium_gbp_per_mwh")),
        "bsad_vintage": text(row.get("bsad_vintage")),
        "bsad_net_gbp": text(row.get("bsad_net_gbp")),
        "bsad_share": text(row.get("bsad_share")),
        "artefacts_sha256": artefacts_digest(row),
    }
    return tuple(values[f] for f in DAY_FIELDS)


def holds_word(holds: object) -> str:
    return "undecided" if holds is None else ("true" if holds else "false")


def verdict_detail(name: str, block: dict[str, Any]) -> str:
    if name == "T4":
        n = block.get("n", len(block.get("qualifying_days") or []))
        return (
            f"{n} of {block.get('min_days')} qualifying days; decided "
            f"{'yes' if block.get('decided') else 'no'}; rho {block.get('rho')}"
        )
    instances = block.get("instances") or []
    deciding = [i for i in instances if not i.get("seed")]
    return f"{len(instances)} instances, {len(deciding)} deciding"


# --------------------------------------------------------------------- state


@dataclass
class State:
    """What the record holds, as read from its claims."""

    rules: set[str] = field(default_factory=set)
    current: tuple[str, date] | None = None
    importing: bool = False
    rows: dict[tuple[str, str], tuple[str, ...]] = field(default_factory=dict)
    outcomes: set[str] = field(default_factory=set)
    outcome_revisions: set[tuple[str, str]] = field(default_factory=set)
    bsad_revisions: set[tuple[str, str]] = field(default_factory=set)
    bsad_confirmed: set[str] = field(default_factory=set)
    runs: set[str] = field(default_factory=set)


def read_state(api: Any) -> State:
    s = State()
    s.rules = {str(c.args["rule"]) for c in api.claims_named("RuleVersion")}
    current = api.claims_named("CurrentRun")
    if current:
        a = current[0].args
        s.current = (str(a["run"]), date.fromisoformat(str(a["run_date"])[:10]))
    s.importing = bool(api.claims_named("Importing"))
    for c in api.claims_named("DayRow"):
        a = c.args
        s.rows[(str(a["day"])[:10], str(a["rule"]))] = tuple(str(a[f]) for f in DAY_FIELDS)
    s.outcomes = {str(c.args["day"])[:10] for c in api.claims_named("Outcome")}
    s.outcome_revisions = {
        (str(c.args["day"])[:10], str(c.args["vintage"]))
        for c in api.claims_named("OutcomeRevision")
    }
    s.bsad_revisions = {
        (str(c.args["day"])[:10], str(c.args["vintage"])) for c in api.claims_named("BsadRevision")
    }
    s.bsad_confirmed = {str(c.args["day"])[:10] for c in api.claims_named("BsadConfirmed")}
    s.runs = {str(c.args["run"]) for c in api.claims_named("Run")}
    return s


# ---------------------------------------------------------------------- plan


@dataclass
class Plan:
    run: str
    run_date: date
    acts: list[dict[str, Any]]
    added: list[str]
    unchanged: list[str]
    changed: list[tuple[str, str]]  # (day, rule) held with different figures
    outcomes: int = 0
    revisions: int = 0
    bsad_revisions: int = 0
    confirmed: int = 0
    verdicts: int = 0


class PlanError(RuntimeError):
    pass


def plan(state: State, tracker: dict[str, Any], tracker_sha256: str) -> Plan:
    """The acts that bring the record up to this tracker file, or a refusal."""
    run_date = date.fromisoformat(tracker["run_date"])
    run = f"run-{tracker['run_date']}-{tracker_sha256[:12]}"
    if run in state.runs:
        raise PlanError(f"{run} is already in the record")
    if state.importing:
        raise PlanError("the record has a run open (Importing): refusing to continue")
    if state.current and state.current[1] > run_date:
        raise PlanError(
            f"run date {run_date} is before the record's current run {state.current[0]}"
        )
    acts: list[dict[str, Any]] = []
    for rule in sorted({rule_of(r) for r in tracker["rows"]} - state.rules):
        digest, amendments = RULES[rule]
        acts.append(
            act("declare_rule", rule=rule, declaration_sha256=digest, amendments=amendments)
        )
    if state.current is None:
        acts.append(
            act(
                "open_first_run",
                run=run,
                run_date=run_date.isoformat(),
                tracker_sha256=tracker_sha256,
                rule=RULE,
            )
        )
    else:
        acts.append(
            act(
                "open_run",
                run=run,
                run_date=run_date.isoformat(),
                tracker_sha256=tracker_sha256,
                rule=RULE,
                prior=state.current[0],
                prior_on=state.current[1].isoformat(),
            )
        )
    added: list[str] = []
    unchanged: list[str] = []
    changed: list[tuple[str, str]] = []
    p = Plan(run, run_date, acts, added, unchanged, changed)
    for row in tracker["rows"]:
        if not row.get("available"):
            continue
        day, rule = row["settlement_date"], rule_of(row)
        values = day_values(row)
        held = state.rows.get((day, rule))
        if held is None:
            acts.append(
                act(
                    "add_day",
                    run=run,
                    day=day,
                    rule=rule,
                    **dict(zip(DAY_FIELDS, values, strict=True)),
                )
            )
            added.append(day)
        elif held == values:
            unchanged.append(day)
        else:
            changed.append((day, rule))
            continue
        outcome = row.get("outcome") or {}
        if outcome.get("l1_constraints_gbp") is not None and day not in state.outcomes:
            acts.append(
                act(
                    "append_outcome",
                    run=run,
                    day=day,
                    vintage=text(outcome.get("vintage")),
                    l1_constraints_gbp=text(outcome.get("l1_constraints_gbp")),
                    l4_offers_mwh=text(outcome.get("l4_constraint_offers_mwh")),
                    l4_bids_mwh=text(outcome.get("l4_constraint_bids_mwh")),
                    ratio_l1_to_two_cut=text(outcome.get("ratio_l1_to_two_cut")),
                )
            )
            p.outcomes += 1
        if outcome.get("l1_constraints_gbp") is not None:
            for rev in row.get("outcome_revisions") or []:
                if (day, str(rev.get("vintage"))) in state.outcome_revisions:
                    continue
                acts.append(
                    act(
                        "revise_outcome",
                        run=run,
                        day=day,
                        vintage=text(rev.get("vintage")),
                        l1_constraints_gbp=text(rev.get("l1_constraints_gbp")),
                        l4_offers_mwh=text(rev.get("l4_constraint_offers_mwh")),
                        l4_bids_mwh=text(rev.get("l4_constraint_bids_mwh")),
                    )
                )
                p.revisions += 1
        for rev in row.get("bsad_revisions") or []:
            if (day, str(rev.get("vintage"))) in state.bsad_revisions:
                continue
            acts.append(
                act(
                    "revise_bsad",
                    run=run,
                    day=day,
                    vintage=text(rev.get("vintage")),
                    bsad_net_gbp=text(rev.get("bsad_net_gbp")),
                    bsad_share=text(rev.get("bsad_share")),
                )
            )
            p.bsad_revisions += 1
        confirmed = row.get("bsad_confirmed_vintage")
        if confirmed and day not in state.bsad_confirmed:
            acts.append(
                act(
                    "confirm_bsad",
                    run=run,
                    day=day,
                    vintage=str(confirmed),
                    bsad_net_gbp=text(row.get("bsad_deciding_net_gbp")),
                    bsad_share=text(row.get("bsad_deciding_share")),
                )
            )
            p.confirmed += 1
    if changed:
        raise PlanError(
            "the record already holds a different row for "
            + ", ".join(f"{day} under {rule}" for day, rule in changed)
            + ": a computed row never changes; a new reading is a new rule version"
        )
    propositions = tracker.get("propositions") or {}
    for name in PROPOSITIONS:
        block = propositions.get(name)
        if not isinstance(block, dict):
            continue
        acts.append(
            act(
                "record_verdict",
                run=run,
                proposition=name,
                holds=holds_word(block.get("holds")),
                detail=verdict_detail(name, block),
            )
        )
        p.verdicts += 1
    acts.append(act("close_run", run=run))
    return p


# ------------------------------------------------------------------ outcome


def run(
    repo_root: Path,
    database_url: str,
    tracker_path: Path,
    *,
    log: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Record one tracker file's compute run; returns a summary line."""
    marker = record.marker_path(repo_root, RECORD, database_url)
    record.refuse_if_marked(marker, "CurrentRun, Importing")
    raw = tracker_path.read_bytes()
    tracker = json.loads(raw)
    tracker_sha256 = hashlib.sha256(raw).hexdigest()
    api = RECORD.client(repo_root, database_url)
    try:
        p = plan(read_state(api), tracker, tracker_sha256)
    except PlanError as exc:
        raise record.ImportError_(str(exc)) from None
    started = time.monotonic()
    outcome = record.guarded_transact(api, marker, p.run, p.acts, {"run": p.run})
    line = {
        "run": p.run,
        "tracker_sha256": tracker_sha256,
        "days_added": p.added,
        "days_unchanged": len(p.unchanged),
        "outcomes": p.outcomes,
        "outcome_revisions": p.revisions,
        "bsad_revisions": p.bsad_revisions,
        "bsad_confirmed": p.confirmed,
        "verdicts": p.verdicts,
        "acts": len(p.acts),
        "seconds": round(time.monotonic() - started, 3),
        "close_transition": outcome.transition_ids[-1],
    }
    log(json.dumps(line))
    return line
