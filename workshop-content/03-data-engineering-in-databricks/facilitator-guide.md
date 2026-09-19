# Facilitator guide — Data Engineering in Databricks

**Facilitator-only:** Participants start with `README.md`, `participant-pipeline.sql`, and `exercises.md`.

## Delivery intent

This is where the FPD5 story becomes *operable*. Sections 01 and 06 read and modelled `core_lending` by hand; here we make the FPD5 layer a governed, quality-gated, scheduled pipeline. Every step answers one of four handover questions:

1. What are the pipeline layers, and which is the trustworthy source of truth for consumers?
2. Where is data quality enforced, and what happens when it is violated?
3. How is the pipeline scheduled, gated, and alerted?
4. Who owns refreshes, quality thresholds, and the downstream consumers?

Keep the modelling out of scope — gold reuses the exact FPD5 definition from every prior section. The goal is a **reliable, observable, governed** data foundation, not new features. Batch/scheduled pipelines are the required path; Lakeflow Connect and Designer are optional discussion.

## Before participants enter

1. Run `facilitator-setup.sql` on the SQL warehouse — it creates `workshop_shared.lending_raw_{loan_application, credit_contract, installment}` (clean batch, `2026-09-01`). Do **not** run the DIRTY BATCH cells yet.
2. Confirm `core_lending`, `workshop_shared`, `workshop_labs` exist and participants have the permissions in the section README.
3. Confirm participants can create a serverless pipeline and a serverless Job, and can create their own `de_<user_id>` schema.
4. Create the pipeline once yourself end-to-end (train-of-thought below) to warm the path and confirm a registered gold table appears.
5. Fill in the runtime/serverless, group, and alert-email values marked `TBD` in the README.
6. Rehearse the dirty-batch demo and the reset.

The released assets passed an end-to-end validation run (pipeline → Job → quality gate) against `sean_development_catalog`. Confirm the same on the final workshop compute before the session.

## Minute-by-minute run of show

| Time | Min | Mode | Activity | Observable result |
|---|---:|---|---|---|
| 1:20–1:30 | 10 | Slides | Reconnect the FPD5 story; why DE; medallion; the four handover questions | Participants state what "operationalize" means here |
| 1:30–1:42 | 12 | Slides | Streaming Table vs Materialized View; the three Expectation tiers; pipelines vs Jobs; serverless | Participants can justify each layer and Expectation tier |
| 1:42–2:05 | 23 | Watch → Run | Create a serverless pipeline from `participant-pipeline.sql`; run it; watch bronze→silver→gold populate | Gold `fpd_origination` = 25,440; cohort rates match Section 01 |
| 2:05–2:25 | 20 | Run → Operate | Land the WARN/DROP batch, refresh; then the FAIL batch; read the event-log quality metrics | 40 dropped / 40 warned, update completes; FAIL batch halts the update |
| 2:25–2:50 | 25 | Run | Build the Job DAG (`run_pipeline` → `quality_gate`); set parameter, schedule (paused), failure alert; run it | Both tasks succeed; `fpd_run_summary` row written |
| 2:50–3:05 | 15 | Operate | Observability: run monitoring, event log, lineage graph, run summary; the alert as tripwire | Participants locate quality metrics and lineage |
| 3:05–3:15 | 10 | Try it | Extend the pipeline/Job or diagnose a seeded failure (`exercises.md`) | A new Expectation or task, or a correct diagnosis |
| 3:15–3:20 | 5 | Checkpoint | Operational handover: owner, schedule/SLA, on-FAIL response, consumers | One owner, one schedule, one alert named |

## 1:30–1:42 — Concept decisions (slides)

- **Medallion.** Bronze = faithful raw ingest (no logic); silver = validated & conformed (Expectations live here); gold = business layer consumers trust. Consumers read gold, never bronze.
- **Streaming Table vs Materialized View.** A Streaming Table ingests append-only sources incrementally (bronze, silver). A Materialized View fully recomputes a query result (gold `fpd_origination`, `fpd_daily_metrics`). Choose incremental for feeds, recompute for derived aggregates/joins.
- **Expectation tiers — choose from the business consequence:** `WARN` (record the violation, keep the row) for suspicious-but-usable; `DROP ROW` for impossible values you must not analyse; `FAIL UPDATE` for corruption that must never propagate (broken keys). Stress: **settlement timing is never an expectation** — early/late/unsettled is the FPD5 outcome we measure.
- **Pipeline vs Job.** The pipeline *is* the data transformation + quality. The Job *orchestrates* it — schedule, parameters, a quality gate, downstream tasks, retries, alerts.

## 1:42–2:05 — Build and run the pipeline

### Exact UI path
1. **Workflows → Delta Live Tables / Lakeflow Pipelines → Create pipeline** (serverless).
2. Source: the `participant-pipeline` notebook. **Target:** catalog `sean_development_catalog`, schema `de_<user_id>`.
3. **Start**. Watch the graph: three bronze → three silver → `fpd_origination` + `fpd_daily_metrics`.

Pause at: the DAG graph (lineage is automatic), the silver Expectations panel (0 violations on clean data), and the gold row count (25,440). Reconcile the cohort rates aloud with Section 01 (promotion ≈42%, other ≈21%).

## 2:05–2:25 — The data-quality demo (the heart of the section)

Run the setup's DIRTY BATCH cells, then refresh the pipeline:

1. **WARN/DROP batch** (`## 3.` in `facilitator-setup.sql`): refresh the pipeline (a normal update ingests the new batch). It **completes**. Open the silver Expectations: `nonneg_due` dropped 40, `positive_income` dropped 40, `sane_lti` warned 40. Bronze grew; silver did not; gold stays 25,440 — **bad data was quarantined, not propagated.**
2. **FAIL batch** (`## 4.`): refresh again. The update **fails** on `valid_contract (FAIL UPDATE)` — a broken key stops everything. This is the moment to make: quality is not a report you read later; it can *halt the line*.
3. **Reset** (`## Reset helpers`): delete the `> 2026-09-01` batches and run a **full refresh**; gold returns to 25,440.

## 2:25–2:50 — Orchestrate with a Job

### Exact UI path
1. **Workflows → Create Job** (or import `job-definition.json`, substituting the pipeline id, the `de_<user_id>` schema, the `job-quality-gate` notebook path, and the alert email).
2. Task `run_pipeline` = the pipeline; task `quality_gate` = the `job-quality-gate` notebook, depending on `run_pipeline`.
3. Add the `as_of_date` **parameter**, a daily **schedule** (leave **PAUSED** for the workshop), and an **on-failure email**.
4. **Run now**. Both tasks go green; `fpd_run_summary` gets a row (eligible 25,440, drop 0%).

Talking points: the DAG makes dependencies explicit; the gate is a soft safety net (fails if drops breach a threshold) beneath the hard `FAIL UPDATE`; the schedule + alert are what turn a notebook into an operated pipeline.

## 2:50–3:05 — Observability

- **Run monitoring:** the Job run timeline, task durations, retries; the pipeline update history.
- **Event log:** silver Expectation pass/drop/warn counts per constraint (the quality metrics).
- **Lineage:** Catalog Explorer shows raw → bronze → silver → gold → (dashboard/model) automatically.
- **Run summary:** `fpd_run_summary` is the durable, queryable record — eligible count, FPD5 rate, drop rate per run.

## 3:15–3:20 — Handover checkpoint

Ask each participant to name, for the pipeline: one **owner**, one **schedule/SLA**, and one **on-FAIL response** (who is alerted, what they do). Build the checklist aloud:

- Pipeline: owner, source landing, quality thresholds, target consumers.
- Job: schedule, parameters, gate threshold, alert destination.
- Observability: event log, run summary, lineage, the alert as tripwire.

## Fallbacks

- **No serverless pipeline entitlement:** the facilitator demos one shared pipeline; participants inspect the graph, event log, and gold, then build the Job against the shared pipeline id. Record the exception.
- **`CREATE SCHEMA` blocked:** the administrator pre-creates each `de_<user_id>` target schema and grants ownership.
- **Job serverless notebook blocked:** attach an approved compute to the `quality_gate` task; the logic is unchanged.
- **Dirty-batch demo runs long:** show the WARN/DROP batch only; describe the FAIL batch on a slide. Always run the reset before the next group.

## Facilitator references

- [Lakeflow Declarative Pipelines](https://docs.databricks.com/delta-live-tables/)
- [Pipeline expectations](https://docs.databricks.com/delta-live-tables/expectations.html)
- [Databricks Jobs / Workflows](https://docs.databricks.com/workflows/)
- [Pipeline event log](https://docs.databricks.com/delta-live-tables/observability.html)
- [Streaming tables and materialized views](https://docs.databricks.com/tables/streaming.html)
