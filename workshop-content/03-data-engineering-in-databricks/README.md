# Section 03 — Data Engineering in Databricks

**Status:** Draft — pipeline, Job, and quality gate passed an end-to-end serverless validation run; facilitator rehearsal, access grants, and TBD confirmations remain
**Time:** 1:20 PM–3:20 PM (2 hours)

Participants **operationalize the FPD5 data foundation**. Sections 01 and 06 *queried* and *modelled* `core_lending` by hand; here we make that foundation a governed, monitored, scheduled pipeline the business can depend on. Using Lakeflow Declarative Pipelines they build a medallion (bronze → silver → gold) with **data-quality Expectations**, orchestrate it with a **Databricks Job** that includes a quality gate and failure alert, and inspect **observability** — event logs, run monitoring, lineage, and a run summary.

> **Deployment note:** The canonical design catalog is `hc_workshop`. This instance is retargeted to **`sean_development_catalog`**, where the dataset was published. Every rule (FPD5 definition, schema layout, leakage boundary) is unchanged. A facilitator repoints the section by replacing the catalog references in `facilitator-setup.sql` and `participant-pipeline.sql`.

## Outcomes

By the end of the section, participants can:

1. Explain the medallion architecture and when to use a **Streaming Table** vs a **Materialized View**.
2. Build a Lakeflow Declarative Pipeline (SQL) that ingests a landing zone and refines it to a governed gold layer.
3. Enforce data quality with **Expectations** and choose `WARN` vs `DROP ROW` vs `FAIL UPDATE` from the business consequence.
4. Orchestrate the pipeline with a **Databricks Job** — a task DAG, parameters, a schedule, a quality gate, and a failure alert.
5. Diagnose pipeline health with the **event log**, run monitoring, lineage, and a run-summary table.
6. Name what the internal team must own to run this reliably after the Atlas Ridge handover.

## Workshop flow

- **Slide-led decisions:** medallion layers, Streaming Table vs Materialized View, the three Expectation tiers, pipelines vs Jobs.
- **Live and hands-on:** build and run the medallion pipeline; land a dirty batch and watch Expectations quarantine (`DROP`) and halt (`FAIL`) bad data; wrap it in a Job with a quality gate; inspect observability.
- **Focused exercise:** extend the pipeline or the Job and diagnose a seeded failure.

Batch/scheduled pipelines are the required path here. Lakeflow **Connect** (managed ingestion) and **Designer** (low-code) are named as optional extensions, not built.

## Prerequisites

- The administrator has run `facilitator-setup.sql` to create the shared raw landing (`workshop_shared.lending_raw_*`).
- The `core_lending`, `workshop_shared`, and `workshop_labs` schemas exist in the workshop catalog; the standard dataset passed its generator `SUCCESS` gate.
- Participants can create a **serverless Lakeflow pipeline** and a **serverless Job**, and can create their own target schema.
- A SQL warehouse is available for ad hoc verification queries.

Environment values that must be confirmed before release:

- `WORKSHOP_CATALOG`: **`sean_development_catalog`** for this instance (canonical value is `hc_workshop`)
- `WORKSHOP_RUNTIME` / serverless entitlements: **TBD — facilitator confirmation required**
- `FACILITATOR_GROUP` and participant group: **TBD — facilitator confirmation required**
- Failure-alert email/destination for the Job: **TBD**

## Required permissions

Participants need:

- `USE CATALOG` on the workshop catalog.
- `USE SCHEMA` + `SELECT` on `core_lending` and on `workshop_shared` (the raw landing).
- `CREATE SCHEMA` on the workshop catalog (each participant's pipeline targets their own `de_<user_id>` schema), or a pre-created target schema they own.
- Permission to create and run a serverless pipeline and a serverless Job.

The facilitator additionally owns `workshop_shared` (the landing) and manages the shared dirty-batch cells during the data-quality demo.

## Assets

- `participant-pipeline.sql` — the Lakeflow Declarative Pipeline source (bronze → silver + Expectations → gold). Attach it to a serverless pipeline.
- `job-definition.json` — the orchestration template (Job DAG: pipeline → quality gate; parameters, schedule, alert).
- `job-quality-gate.py` — the notebook the Job's quality-gate task runs (drop-rate gate + run summary).
- `exercises.md` — the focused extend/diagnose exercise.
- `expected-results.md` — observable results and recovery paths (open after the exercise).

Facilitator-only:

- `facilitator-setup.sql` — creates the shared raw landing and the WARN/DROP/FAIL dirty-batch cells.
- `facilitator-guide.md` — minute-by-minute delivery, UI paths, talking points, and fallbacks.
- `slide-outline.md` — recommended slide outline (decision frameworks on slides).

Each participant's pipeline creates, in their `de_<user_id>` schema:

```text
fpd_bronze_installment / _contract / _application   (Streaming Tables — raw ingest)
fpd_silver_installment / _contract / _application   (Streaming Tables — Expectations)
fpd_origination                                     (Materialized View — governed FPD5 layer)
fpd_daily_metrics                                   (Materialized View — vintage × cohort FPD5 rate)
fpd_run_summary                                     (Delta table — Job run summary, observability)
```

It reads the shared landing and `core_lending` dimensions read-only; it never modifies `core_lending`.

## Definition of done

- The pipeline completes and the gold `fpd_origination` is at one-row-per-eligible-contract grain, reproducing the cohort rates (promotion higher than other originations).
- A dirty batch demonstrates all three Expectation tiers: rows `DROP`ped, rows `WARN`ed, and a broken key `FAIL`ing the update.
- The Job runs the pipeline, the quality gate passes on clean data (and fails on a breach), and a `fpd_run_summary` row is written.
- Participants can explain Streaming Table vs Materialized View, choose an Expectation tier from the business consequence, read the event log, and name one owner / schedule / alert for the handover.
