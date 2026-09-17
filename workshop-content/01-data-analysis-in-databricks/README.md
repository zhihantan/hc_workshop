# Section 01 — Data Analysis in Databricks

**Status:** Draft — workspace validation and facilitator rehearsal required  
**Time:** 9:45 AM–11:15 AM (90 minutes)

Participants investigate Unicorn Finance's 0% smartphone promotion and first-payment-default pattern while learning how analytical assets run and are operated on Databricks.

## Outcomes

By the end of the section, participants can:

1. Choose notebook, jobs, or SQL warehouse compute based on the workload rather than habit.
2. Explain when serverless is the default and when classic customization is justified.
3. Explore and transform Unity Catalog data with PySpark and SQL in one notebook.
4. Explain how Delta Lake history, schema evolution, and time travel support safe operations, and where Apache Iceberg fits.
5. Read a governed AI/BI dashboard and distinguish draft, published, shared-data, and individual-data behavior.
6. Diagnose SQL warehouse symptoms using queue, spill, query-profile, and activity evidence.
7. Query a governed Metric View, ask the same question through a Genie Agent, and verify the generated answer.

## Workshop flow

- **Slide-led decisions:** compute selection, serverless versus classic, open table formats, dashboard sharing, and warehouse symptom-to-action guidance.
- **Live and hands-on:** notebook exploration, FPD5 derivation, Delta history and evolution, dashboard interaction, query profile inspection, and Genie verification.
- **Focused exercise:** identify a promotion hotspot without claiming that the pattern proves fraud.

This split keeps the seven requested topics inside 90 minutes. It does not attempt seven separate product labs.

## Prerequisites

- The administrator has completed `../../workspace-setup/README.md`.
- The standard dataset has passed its final generator `SUCCESS` gate.
- `facilitator-setup.sql` has successfully created the shared analysis view and Metric View.
- The facilitator has prepared the dashboard and Genie Agent described in `facilitator-guide.md`.
- Participants can use serverless notebook compute or a Unity Catalog-compatible all-purpose compute resource.
- A serverless SQL warehouse is available for the dashboard, Genie Agent, and warehouse-operations demonstration.

Environment values that must be confirmed before release:

- `WORKSHOP_RUNTIME`: **TBD — facilitator confirmation required**
- `SQL_WAREHOUSE`: **TBD — facilitator confirmation required**
- `FACILITATOR_GROUP`: **TBD — facilitator confirmation required**
- Dashboard URL: **TBD — facilitator confirmation required**
- Genie Agent URL: **TBD — facilitator confirmation required**
- Agenda reconciliation: **TBD — the supplied Section 01 scope differs from the current data-analysis bullets in `workshop-authoring/agenda/workshop-agenda.md`**

## Required permissions

Participants need:

- `USE CATALOG` on `hc_workshop`.
- `USE SCHEMA` and `SELECT` on `hc_workshop.core_lending`.
- `USE SCHEMA`, `CREATE TABLE`, and permission to modify their own team-prefixed table in `hc_workshop.workshop_labs`.
- `USE SCHEMA` and `SELECT` on the shared assets in `hc_workshop.workshop_shared`.
- Permission to run the imported notebook and use its assigned compute.
- `CAN USE` on the workshop SQL warehouse.
- Viewer access to the prepared dashboard and Genie Agent.

The facilitator additionally needs permission to create or replace views in `workshop_shared`, edit and publish the dashboard, manage the Genie Agent, `CAN MONITOR` on the SQL warehouse, and `CAN MANAGE` if the live demonstration opens warehouse settings.

## Assets

Participant entry point:

- `participant-lab.py` — imported Databricks Python source notebook with Python and SQL cells.
- `exercises.md` — the focused participant investigation.
- `expected-results.md` — open after completing the exercise for observable results and recovery paths.

Facilitator-only delivery files:

- `facilitator-guide.md` — minute-by-minute delivery, UI paths, talking points, and fallbacks.
- `facilitator-setup.sql` — idempotent shared view and Metric View setup.
- `slide-outline.md` — recommended presentation slides and transitions to live demonstration.

Each participant's lab creates only:

```text
hc_workshop.workshop_labs.unicorn_<team_id>_<runner_id>_delta_demo
```

It never modifies `hc_workshop.core_lending`. Its analytical FPD5 dataset is a session-scoped temporary view.

## Definition of done

- The participant notebook reaches its final checkpoint without an unexpected error.
- The promotion FPD5 rate is higher than the non-promotion rate using the declared eligible population.
- The participant can explain why the pattern is an investigation signal, not proof of fraud.
- The Delta demonstration shows a pre-evolution and post-evolution table version.
- The dashboard and Metric View use the same FPD5 definition as the notebook.
- The participant can distinguish a queue symptom from a spill symptom.
- A Genie answer is checked against its generated SQL and the governed Metric View result.
- The team can name the owner, compute dependency, permissions, monitoring location, and recovery action for each inherited analytical asset.

