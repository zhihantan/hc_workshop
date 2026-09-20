# Facilitator cue card — Governance and Access Control

**30 minutes · Participant source of truth:** [`participant-guide.md`](../../../workshop-content/05-governance-and-access-control/participant-guide.md)
**Facilitator demo:** [`facilitator-demo.py`](facilitator-demo.py)

## Goal

Diagnose one controlled incident without broadening access:

> A risk analyst can discover `hc_workshop.workshop_shared.fpd_analysis` under Consumer Lending > Origination Risk, but cannot query it.

Participants record the executing identity, failed gate, evidence, narrow repair, unchanged verification, downstream impact, Domain boundary, owner, risk, and recovery action.

## Before participants enter

- Use a dedicated non-admin user in a dedicated restricted group; exclude participant and administrative memberships.
- Run only the preparation statements in [`section-05-governance-demo-setup.sql`](../../../workshop-setup/section-05-governance-demo-setup.sql).
- Confirm notebook `CAN RUN`, warehouse `CAN USE`, catalog `BROWSE` and `USE CATALOG`, view `SELECT`, and no effective `USE SCHEMA`.
- Prepare separate restricted-user and administrator browser sessions.
- In the administrator SQL editor, copy the commented live `GRANT` and reset `REVOKE` statements without the leading `--`; do not use **Run all**.
- Rehearse the failure, repair, unchanged rerun, and reset.
- Verify lineage `fpd_analysis → fpd_metrics → verified consumer`.
- If Discover is available, assign only the verified `fpd_analysis` asset to **Consumer Lending > Origination Risk**.
- Save a failure capture, successful result, permissions/effective-access capture, and lineage capture. If Discover will be shown, save a Domain capture too.

## Run of show

| Time | Cue | Participant evidence |
|---|---|---|
| 0:00–0:03 | State the incident and smoke-test boundary | Seven handover questions understood |
| 0:03–0:07 | Explain notebook → warehouse → identity → UC path | Known and unknown gates identified |
| 0:07–0:16 | Restricted failure; administrator grants `USE SCHEMA`; unchanged rerun | Error, failed gate, repair, and verification recorded |
| 0:16–0:20 | Explain what success proves and does not prove | Workspace and data permissions separated |
| 0:20–0:24 | Inspect lineage | Downstream assets to retest recorded |
| 0:24–0:27 | Open Consumer Lending > Origination Risk | Discovery is separated from authorization |
| 0:27–0:30 | Complete handover | Owner, risk, and recovery action named |

## Live demonstration

1. As the restricted user, run the identity cell and read the session user aloud.
2. Explain that groups contribute effective access; the group is not the interactive user shown by the query.
3. Ask for a prediction, then run the `fpd_analysis` query.
4. Stop at the error and capture its exact text and request ID.
5. As administrator, distinguish direct grants to the group, access obtained through group membership, and any parent-securable inheritance.
6. Grant only `USE SCHEMA` on `hc_workshop.workshop_shared`.
7. Return to the restricted session and rerun the identical query.
8. Confirm ten synthetic rows; do not treat this as FPD5 result validation.
9. Show lineage before Discover.
10. State: Domain placement supports discovery; it does not grant `USE CATALOG`, `USE SCHEMA`, or `SELECT`.

## Answer key

- **Executing identity:** dedicated restricted demo user.
- **Failed gate:** `USE SCHEMA` on `hc_workshop.workshop_shared`.
- **Existing access:** notebook and warehouse access; catalog discovery/traversal; view `SELECT` through the dedicated group.
- **Repair:** grant only the missing schema privilege to the dedicated group.
- **Verification:** same user, warehouse, object, and SQL now return ten rows.
- **Impact:** retest `fpd_metrics` and the verified downstream consumer after definition, schema, access, or availability changes.
- **Avoid:** `ALL PRIVILEGES`, ownership changes, or grants to the human reporter before confirming the executing identity.

## Fallbacks and reset

- **Query succeeds early:** stop and inspect ownership, admin roles, nested groups, and broader grants.
- **Grant propagation delay:** refresh once and rerun the unchanged query.
- **Lineage or Discover unavailable:** use the saved capture; do not substitute an unrelated asset.
- **Restricted identity unavailable:** use captured evidence; never manufacture a failure against a participant.
- **After every rehearsal or delivery:** run the prepared `REVOKE USE SCHEMA`, then confirm the restricted query fails again.
