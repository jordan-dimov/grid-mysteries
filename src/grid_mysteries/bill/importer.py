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
wherever the record is and never trusts a local log. Each transact is
guarded by a recovery marker kept per database, cleared only on a positive
non-commit (a rejection, or an error code the runtime documents as
"nothing was recorded"); anything else keeps it and the next run refuses
until someone has read the record and removed it.
"""

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Final

PROGRAMME: Final = Path("bill/bill-register.morph")
REGISTER: Final = "bill"
ACTOR: Final = "bill_importer"
MARKER_DIR: Final = Path("data/derived/bill")
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
#: Error codes the runtime documents as "nothing was recorded" (v0.0.12,
#: `morpholog schema --result`, propose_error_code). `commit_outcome_unknown`
#: is deliberately absent; a code not listed here keeps the marker.
NOT_COMMITTED_CODES: Final = frozenset(
    {
        "actor_assertion_unauthorised",
        "duplicate_intent",
        "invalid_arguments",
        "invalid_request",
        "kernel_error",
        "not_committed",
        "serialization_failure",
        "unknown_transformation",
    }
)
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


def act(transformation: str, **args: object) -> dict[str, Any]:
    return {"transformation": transformation, "actor": ACTOR, "args_named": args}


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


class ImportError_(RuntimeError):
    pass


@dataclass
class Outcome:
    status: str  # committed | not-committed | unknown
    detail: str = ""
    transition_ids: list[str] = field(default_factory=list)


def classify(result: object, error: BaseException | None) -> Outcome:
    """committed / not-committed / unknown, from a transact's result or error."""
    from morpholog_client import envelopes
    from morpholog_client.adapter import MorphologRequestError

    if error is None:
        if isinstance(result, envelopes.AtomicCommitted):
            return Outcome("committed", "", [a.outcome.transition_id for a in result.acts])
        if isinstance(result, envelopes.AtomicRejected):
            return Outcome("not-committed", f"act {result.act} refused [{result.rule}]")
        return Outcome("unknown", f"unrecognised result {result!r}"[:300])
    if isinstance(error, MorphologRequestError) and error.code in NOT_COMMITTED_CODES:
        return Outcome("not-committed", f"{error.code}: {error.error}"[:300])
    return Outcome("unknown", f"{type(error).__name__}: {error}"[:300])


def marker_path(repo_root: Path, database_url: str) -> Path:
    tag = hashlib.sha256(database_url.encode()).hexdigest()[:12]
    return repo_root / MARKER_DIR / f".import-{tag}.marker"


def run(
    repo_root: Path,
    database_url: str,
    tracker_path: Path,
    *,
    log: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Record one tracker file's compute run; returns a summary line."""
    from morpholog_client.adapter import Morpholog

    marker = marker_path(repo_root, database_url)
    if marker.exists():
        raise ImportError_(
            f"recovery marker {marker} exists: a previous run's outcome is unknown. "
            "Read the record (CurrentRun, Importing) and remove the marker by hand."
        )
    raw = tracker_path.read_bytes()
    tracker = json.loads(raw)
    tracker_sha256 = hashlib.sha256(raw).hexdigest()
    api = Morpholog(str(repo_root / PROGRAMME), database_url)
    try:
        p = plan(read_state(api), tracker, tracker_sha256)
    except PlanError as exc:
        raise ImportError_(str(exc)) from None
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"run": p.run, "acts": len(p.acts)}) + "\n")
    started = time.monotonic()
    result: object = None
    error: BaseException | None = None
    try:
        result = api.transact(p.acts)
    except Exception as exc:  # noqa: BLE001 - classified below
        error = exc
    outcome = classify(result, error)
    if outcome.status == "not-committed":
        marker.unlink()
        raise ImportError_(f"{p.run} was not committed ({outcome.detail}); record unchanged")
    if outcome.status != "committed":
        raise ImportError_(
            f"{p.run}: commit outcome UNKNOWN ({outcome.detail}); marker left at {marker}"
        )
    marker.unlink()
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
