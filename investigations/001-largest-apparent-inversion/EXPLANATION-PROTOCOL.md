# Explanation-status protocol for Mystery 001

Committed after the deterministic selection, **before any deep inspection
of the selected case**, so that the evidential standard cannot drift to
fit whatever the evidence turns out to show. This protocol freezes the
vocabulary and the standard of proof, not the explanations themselves.

## Statuses

Every candidate mechanism examined by this investigation must be assigned
exactly one of:

- **explained** — pinned public evidence demonstrates the mechanism
  operated *and* accounts for the apparent inversion on its own.
- **contributes** — pinned public evidence demonstrates the mechanism
  operated and materially narrows the anomaly, but does not account for
  it alone.
- **ruled out** — pinned public evidence contradicts the mechanism.
- **compatible but unproven** — the mechanism is consistent with the
  pinned evidence, but no pinned evidence demonstrates it actually
  operated. *Plausibility alone always lands here, never higher.*
- **not observable publicly** — deciding the mechanism requires evidence
  that no public dataset provides; the missing observable must be named
  precisely.

## Evidential standard

1. A status of **explained**, **contributes**, or **ruled out** must cite
   specific pinned artefacts (path + SHA-256) and state the exact records
   relied on. Uncited claims default to **compatible but unproven**.
2. Only mechanisms with status **explained** or **contributes** may appear
   in the conclusion as explanation. "There was probably a constraint" is
   not an explanation; it is **compatible but unproven**.
3. Evidence fetched for this stage is pinned under the same immutability
   rules as the selection data and recorded in
   `evidence/case-manifest.json`.
4. The registered null hypothesis resolves as:
   - **explained** — mechanisms with status *explained*/*contributes*
     jointly account for the selected inversion;
   - **partly explained** — they account for a material part, with the
     residual attributed only to named *not observable publicly* items;
   - **publicly unexplained** — a material residual remains and no
     mechanism reaches *explained*/*contributes* status for it.
5. Statuses may be revised only by later commits that preserve the prior
   assignment in the Corrections section of the investigation README.

## Mechanisms to examine (from the investigation template)

location/constraint; dynamic limits/ramping; prior dispatch state;
physical notification/availability (including whether the unaccepted
unit had any deliverable volume in the direction concerned); published
exclusion or flagging classification (SO-flag, RR, STOR, deemed);
submission semantics (sentinel/defensive pricing); data revision and
publication timing. Mechanisms may be added during the investigation;
none may be removed.
