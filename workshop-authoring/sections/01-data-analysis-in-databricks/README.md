# Section 01 — Data Analysis in Databricks

**Status:** Draft — workspace validation and facilitator rehearsal required
**Time:** 9:45 AM–11:15 AM (90 minutes)

This directory contains maintainer and facilitator material. Participants use only [`01-lab.py`](../../../workshop-content/01-data-analysis-in-databricks/01-lab.py), which contains the complete investigation, exercises, UI instructions, validation guidance, and final reflection.

## Delivery authority

- Participant flow and outcomes: [`01-lab.py`](../../../workshop-content/01-data-analysis-in-databricks/01-lab.py)
- Timing, delivery surfaces, and facilitator talking points: [`facilitator-guide.md`](facilitator-guide.md)
- Final visible-slide generation: [`generate-section-01-data-analysis-slides-v3-slide-only.md`](generate-section-01-data-analysis-slides-v3-slide-only.md)

This README tracks release prerequisites, permissions, file ownership, and definition of done rather than repeating the delivery narrative.

## Prerequisites

- The administrator completed [`workshop-setup/README.md`](../../../workshop-setup/README.md).
- The standard dataset passed its final generator `SUCCESS` gate.
- [`section-01-facilitator-setup.sql`](../../../workshop-setup/section-01-facilitator-setup.sql) created `workshop_shared.fpd_analysis` and `workshop_shared.fpd_metrics`.
- The facilitator prepared and reconciled **Unicorn FPD5 Overview** using `workshop_shared.fpd_metrics`.
- Participants can use serverless notebook compute or approved Unity Catalog-compatible all-purpose compute.
- A serverless SQL warehouse is available for the dashboard, Genie Agents, and workload inspection.
- Participants can create and manage an unshared Genie Agent in their user folder.

Environment values to confirm before release:

- `WORKSHOP_RUNTIME`: **TBD**
- `SQL_WAREHOUSE`: **TBD**
- `FACILITATOR_GROUP`: **TBD**
- Dashboard URL: **TBD**

## Required permissions

Participants need:

- `USE CATALOG` on `hc_workshop`;
- `USE SCHEMA` and `SELECT` on `hc_workshop.core_lending`;
- `USE SCHEMA` and `CREATE TABLE` on `hc_workshop.workshop_labs`; participants own and modify the tables they create;
- `USE SCHEMA` and `SELECT` on `hc_workshop.workshop_shared`;
- permission to run the notebook and use its assigned compute;
- Databricks SQL workspace entitlement;
- `CAN USE` on the workshop SQL warehouse;
- permission to create and manage a Genie Agent in their user folder; and
- viewer access to the prepared dashboard.

The facilitator additionally needs permission to create or replace shared views, edit and publish the dashboard, and inspect the SQL warehouse workload.

## Participant-visible asset

Only this file should be distributed or imported into the participant-facing workshop folder:

- [`01-lab.py`](../../../workshop-content/01-data-analysis-in-databricks/01-lab.py)

It creates:

```text
hc_workshop.workshop_labs.unicorn_<runner_id>_fpd_investigation
```

The runner ID is derived from the participant's full workspace identity and a short hash. It prevents workshop naming collisions but is not a permission boundary.

## Facilitator assets

- [`facilitator-guide.md`](facilitator-guide.md) — timed delivery map plus concise talking points organized in participant-notebook order.
- [`section-01-facilitator-setup.sql`](../../../workshop-setup/section-01-facilitator-setup.sql) — shared analysis view and Metric View.
- [`generate-section-01-data-analysis-slides-v3-slide-only.md`](generate-section-01-data-analysis-slides-v3-slide-only.md) — final generation prompt limited to the facilitator guide's visible slide windows.
- [`drafts/`](drafts/README.md) — archived content-first and prescriptive slide sources.

## Definition of done

- The notebook reaches its final checkpoint without an unexpected error.
- Participants can explain FPD5 before running its calculation.
- The promotion rate is compared with other eligible originations using the declared observation window.
- Each participant changes the analytical grain and interprets the result with counts, rates, denominator, and caveat.
- The participant Delta table shows pre-note and post-note versions.
- The notebook result reconciles with `fpd_metrics`.
- Each participant creates one private Agent using only `fpd_metrics` and verifies its generated SQL.
- Participants inspect a section-generated SQL statement and can distinguish queueing from spill.
