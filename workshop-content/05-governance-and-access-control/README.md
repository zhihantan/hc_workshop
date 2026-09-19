# Section 05 — Governance and Access Control in Databricks

**Status:** Draft — workspace preparation and facilitator rehearsal required
**Time:** 3:20 PM–3:50 PM (30 minutes)

Participants learn how Databricks authorization is evaluated across identity, workspace resources, runtime identity, and Unity Catalog. The section uses one controlled access failure to teach diagnosis, then closes with lineage and a business-oriented Discover domain.

This is a facilitator-led section. Participants do not build governance objects or complete a coding lab.

## Outcomes

By the end of the section, participants can:

1. Distinguish workspace-resource ACLs from Unity Catalog privileges.
2. Trace a data request through `USE CATALOG`, `USE SCHEMA`, and the required object privilege.
3. Explain how ownership, inherited grants, and runtime identity affect authorization.
4. Separate a permission failure from successful row-filter or column-mask enforcement.
5. Use Catalog Explorer and an error message to identify the failed authorization layer.
6. Explain the difference between a technical catalog hierarchy and a business-oriented Discover domain.
7. Use table- and column-level lineage as evidence when assessing impact.

## Workshop flow

- **Slides:** establish the layered access model, Unity Catalog hierarchy, and reusable diagnostic sequence.
- **Prepared notebook:** show the active identity, reproduce one intentional `USE SCHEMA` failure, apply the missing grant from an administrator session, and rerun the same query.
- **Workspace UI:** inspect inherited and direct grants in Catalog Explorer, trace lineage, compare a workspace asset ACL with its data permissions, and browse the prepared Discover domain.
- **Team checkpoint:** diagnose one additional scenario verbally using the participant checklist.

Data Classification is intentionally excluded. Domains are presented as a discovery and curation layer, not an authorization boundary.

## Prerequisites

- The administrator has completed `../../workshop-setup/README.md`.
- The standard dataset has passed its final generator `SUCCESS` gate.
- `../../workshop-setup/section-05-governance-demo-setup.sql` has been configured and run.
- A dedicated non-admin demo user belongs to the dedicated restricted demo group and does **not** belong to the workshop participant group.
- The demo user can open `facilitator-demo.py` and use the assigned SQL warehouse.
- The facilitator has prepared the Discover domain and lineage path described in `facilitator-guide.md`.

Environment values that must be confirmed before release:

- `WORKSHOP_CATALOG`: **`hc_workshop`**
- `SQL_WAREHOUSE`: **TBD — facilitator confirmation required**
- `GOVERNANCE_DEMO_USER`: **TBD — facilitator confirmation required**
- `GOVERNANCE_DEMO_GROUP`: **TBD — facilitator confirmation required**
- Discover domain URL: **TBD — facilitator confirmation required**

## Required permissions

The restricted demo identity needs:

- Workspace access and the Databricks SQL access entitlement.
- Permission to open and run the demonstration notebook.
- `CAN USE` on the workshop SQL warehouse.
- `BROWSE` and `USE CATALOG` on `hc_workshop`.
- `SELECT` on `hc_workshop.core_lending.customer`.
- No `USE SCHEMA` on `hc_workshop.core_lending` before the demonstration.

The facilitator needs:

- Permission to inspect all relevant grants in Catalog Explorer.
- Permission to grant and revoke `USE SCHEMA` on `hc_workshop.core_lending`.
- Access to workspace-resource permission dialogs for the notebook, warehouse, dashboard, or Genie Agent used in the comparison.
- Permission to manage discovery and curate the prepared domain.

Do not use a metastore admin, workspace admin, catalog owner, or member of the broadly privileged participant group as the restricted demo identity.

## Assets

Facilitator delivery:

- `slide-outline.md` — six-slide presentation outline.
- `facilitator-guide.md` — timed run of show, exact UI paths, setup, and fallbacks.
- `facilitator-demo.py` — read-only SQL notebook run by the restricted demo identity.
- `../../workshop-setup/section-05-governance-demo-setup.sql` — administrator setup and reset commands for the intentional missing-privilege scenario.

Participant takeaway:

- `access-diagnostic-checklist.md` — reusable sequence for diagnosing access problems.
- `exercises.md` — short scenario-based team checkpoint.
- `expected-results.md` — expected demo evidence and checkpoint answers.

## Definition of done

- The restricted identity can open the notebook and use its SQL warehouse.
- Before the live grant, the customer query fails because `USE SCHEMA` is missing.
- After the administrator grants `USE SCHEMA`, the identical query returns rows.
- Catalog Explorer shows where the three required privileges originate.
- The facilitator clearly separates workspace ACLs, runtime identity, and Unity Catalog privileges.
- A prepared table- or column-lineage graph is visible.
- The Discover domain contains representative data and workspace assets.
- Participants state that domain membership does not grant access to an underlying asset.
- The facilitator completes the core flow in 30 minutes without relying on Data Classification.
