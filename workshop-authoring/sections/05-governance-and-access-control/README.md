# Governance and Access Control in Databricks

**Status:** Draft — final slides, workspace validation, and timed rehearsal required
**Time:** 3:20 PM–3:50 PM (30 minutes)
**Delivery mode:** Facilitator-led incident diagnosis with one participant guide

The internal `05` identifier preserves repository paths. Use the topic title and scheduled time with participants.

## Delivery authority

- Participant evidence and handover: [`05-participant-guide.md`](../../../workshop-content/05-governance-and-access-control/05-participant-guide.md)
- Timing, delivery surfaces, and facilitator talking points: [`facilitator-guide.md`](facilitator-guide.md)
- Restricted-identity demonstration: [`facilitator-demo.py`](facilitator-demo.py)
- Final visible-slide generation: [`generate-section-05-governance-slides-v3-slide-only.md`](generate-section-05-governance-slides-v3-slide-only.md)

This README tracks release prerequisites, permissions, file ownership, and definition of done rather than repeating the delivery narrative.

## Authoring boundaries

- This is a facilitator-led demonstration; participants do not run code or change permissions.
- The same `fpd_analysis` view is used for the access request, lineage, and Domain walkthrough.
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
- `drafts/` — archived content-first and prescriptive slide sources.

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

- Final slides follow the v3 slide-only prompt and the facilitator guide's visible slide windows.
- The participant-facing folder contains only `05-participant-guide.md`.
- The restricted identity fails on `fpd_analysis` because `USE SCHEMA` is missing.
- After the single grant, the unchanged query returns ten synthetic rows.
- Catalog Explorer distinguishes direct grants to the group, any parent-securable inheritance, and the user's group-derived effective access.
- Lineage visibly connects `fpd_analysis` to `fpd_metrics` and at least one downstream consumer.
- The Domain walkthrough uses the same `fpd_analysis` asset and states the discovery-versus-authorization boundary.
- The facilitator completes the full flow in 30 minutes.
- The setup, demo, reset, local links, and notebook source format have been validated.
