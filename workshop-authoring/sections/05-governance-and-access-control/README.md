# Governance and Access Control in Databricks

**Status:** Draft — final slides, workspace validation, and timed rehearsal required
**Time:** 3:20 PM–3:50 PM (30 minutes)
**Delivery mode:** Facilitator-led incident diagnosis with one participant guide

The internal `05` identifier preserves repository paths. Use the topic title and scheduled time with participants.

## Assignment and delivery

Participants act as the new owners of Unicorn Finance's inherited Databricks platform. A risk analyst can discover the trusted `hc_workshop.workshop_shared.fpd_analysis` view under **Consumer Lending > Origination Risk**, but cannot query it.

The section follows that same asset from discovery through diagnosis, repair, verification, lineage, and handover. Participants record evidence in:

`../../../workshop-content/05-governance-and-access-control/05-participant-guide.md`

They do not run or clone the demonstration notebook, change permissions, or build governance objects.

## Outcomes

By the end of the section, participants can:

1. identify the runtime principal before changing access;
2. separate notebook, SQL warehouse, and Unity Catalog permissions;
3. diagnose `USE CATALOG → USE SCHEMA → SELECT`;
4. distinguish direct grants, parent-securable inheritance, and group-derived access;
5. apply and verify the narrowest repair;
6. use lineage to identify downstream assets that require retesting;
7. explain why Discover Domain placement does not grant access;
8. complete an operational handover with an owner, risk, and recovery action.

## Scope boundaries

- The demonstration uses one missing `USE SCHEMA` privilege on `workshop_shared`.
- The same `fpd_analysis` view is used for the query, lineage, and Domain walkthrough.
- The query is an access smoke test, not a recalculation or validation of FPD5.
- Row filters, column masks, ABAC, Data Classification, storage credentials, external locations, Delta Sharing, and full privilege inventories are not configured live.
- Jobs and dashboard credential modes are optional transfer examples, not separate demonstrations.
- Domains are a Public Preview discovery feature built with governed tags, not an authorization boundary.

## Assets

Participant-facing:

- `../../../workshop-content/05-governance-and-access-control/05-participant-guide.md` — the only participant entry point.

Facilitator-only:

- `facilitator-guide.md` — timed delivery map plus concise participant-facing talking points for the live incident.
- `facilitator-demo.py` — screen-shared read-only notebook run by the restricted identity.
- `generate-section-05-governance-slides-v3-slide-only.md` — final generation prompt limited to the facilitator guide's visible slide windows.
- `generate-section-05-governance-slides-v2-content-first.md` — broader content inventory for editorial reference.
- `generate-section-05-governance-slides.md` — prescriptive four-slide editorial reference.

Administrator-only:

- `../../../workshop-setup/section-05-governance-demo-setup.sql` — prepare, repair, inspect, and reset the restricted scenario.

There is intentionally no participant lab notebook.

## Required preparation

- The dataset generator passed its final `SUCCESS` gate.
- `section-01-facilitator-setup.sql` created `workshop_shared.fpd_analysis` and `fpd_metrics`.
- A dedicated non-admin demo user belongs only to the restricted demo group relevant to this scenario.
- The demo identity has notebook `CAN RUN`, SQL warehouse `CAN USE`, catalog `BROWSE` and `USE CATALOG`, and `SELECT` on `fpd_analysis`.
- The demo identity has no effective `USE SCHEMA` on `workshop_shared` through direct grants, parent-securable inheritance, or group membership before the demonstration.
- The lineage path from `fpd_analysis` to `fpd_metrics` and the FPD5 dashboard is visible.
- If Domains are used, the required account and workspace previews are enabled, **Consumer Lending > Origination Risk** is published, and `fpd_analysis` is assigned.

Environment values still requiring confirmation:

- `WORKSHOP_CATALOG`: **`hc_workshop`**
- `SQL_WAREHOUSE`: **TBD — facilitator confirmation required**
- `GOVERNANCE_DEMO_USER`: **TBD — facilitator confirmation required**
- `GOVERNANCE_DEMO_GROUP`: **TBD — facilitator confirmation required**
- Discover domain URL: **TBD — facilitator confirmation required**

## Definition of done

- Final slides preserve the assignment and incident flow in the content-first brief and use titles rather than section numbers.
- The participant-facing folder contains only `05-participant-guide.md`.
- The restricted identity fails on `fpd_analysis` because `USE SCHEMA` is missing.
- After the single grant, the unchanged query returns ten synthetic rows.
- Catalog Explorer distinguishes direct grants to the group, any parent-securable inheritance, and the user's group-derived effective access.
- Lineage visibly connects `fpd_analysis` to `fpd_metrics` and at least one downstream consumer.
- The Domain walkthrough uses the same `fpd_analysis` asset and states the discovery-versus-authorization boundary.
- The facilitator completes the full flow in 30 minutes.
- The setup, demo, reset, local links, and notebook source format have been validated.
