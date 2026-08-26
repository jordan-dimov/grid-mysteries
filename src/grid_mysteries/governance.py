"""Analysis-side access to governed v2 values via the generated client.

Doctrine (RESEARCH-V2-DESIGN.md item 8): a parameter that can change
which evidence is selected or what conclusion is reached has ONE
executable authoritative value — the `DeclaredParameter` claim. Analysis
code reads it through here; prose merely displays it. Duplicating an
authoritative constant into Python source or config is a defect.

The session comes from ``morpholog_client.open_session`` (pinned to the
programme's model hash at the handshake), so a drifted programme fails
loudly before any value is read.
"""

import os
from decimal import Decimal
from pathlib import Path

from morpholog_client import Session, open_session

V2_PROGRAMME = str(Path(__file__).resolve().parents[2] / "morpholog" / "research-v2-draft.morph")


def declared_parameter(session: Session, inquiry: str, name: str) -> Decimal:
    """The single authoritative value of a sealed protocol parameter.

    Raises ``LookupError`` if the parameter is not declared — analysis
    must never fall back to a code-side default for a governed value.
    """
    rows = session.claims_named("DeclaredParameter", where={"inquiry": inquiry, "name": name})
    if not rows:
        raise LookupError(f"no DeclaredParameter({inquiry!r}, {name!r}) in the governed record")
    if len(rows) > 1:  # unique by (inquiry, name) makes this unreachable
        raise LookupError(f"ambiguous DeclaredParameter({inquiry!r}, {name!r}): {len(rows)} rows")
    value = rows[0].args["parameter_value"]
    return value if isinstance(value, Decimal) else Decimal(str(value))


def require_acquisition_authorised(inquiry: str) -> None:
    """Refuse to acquire unless the governed record carries the human seal.

    `seal_protocol` is the only emitter of `DataAcquisitionAuthorised`, so
    a fetcher that checks for `ProtocolSealed` is the machine declining to
    look at unseen data before a human has authorised it. This is a
    cooperative control, not a cage — see the three-layer threat model in
    `morpholog/V2-LAUNCH-RUNBOOK.md` — but it is the control the process
    actually relies on, so it is tested in `scripts/rehearse-v2`.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "refusing to fetch: DATABASE_URL is unset, so the seal cannot be checked. "
            f"Acquisition is authorised only by ProtocolSealed({inquiry}) in the governed record."
        )
    with open_session(V2_PROGRAMME, database_url) as session:
        sealed = session.claims_named("ProtocolSealed", where={"inquiry": inquiry})
    if not sealed:
        raise SystemExit(
            f"refusing to fetch: no ProtocolSealed({inquiry}) in the governed record. "
            "Only the human seal emits DataAcquisitionAuthorised; see V2-LAUNCH-RUNBOOK.md."
        )
    print(f"seal present: {inquiry} protocol sealed — acquisition authorised", flush=True)
