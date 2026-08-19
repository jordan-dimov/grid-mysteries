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

from __future__ import annotations

from decimal import Decimal

from morpholog_client import Session


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
