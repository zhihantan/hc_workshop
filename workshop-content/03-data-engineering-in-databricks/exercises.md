# Exercise — Harden and operate the pipeline

**Timebox:** 10 minutes

Pick **one** track. Use `participant-pipeline.sql`, your running pipeline, and `job-definition.json`.

## Track A — Add a data-quality Expectation

A reviewer notes that some applications carry an implausible `requested_tenor_months`. Add an Expectation to `fpd_silver_application`:

1. Decide the tier from the **business consequence** — is an out-of-range tenor *suspicious-but-usable* (`WARN`), *impossible* (`DROP ROW`), or *corruption* (`FAIL UPDATE`)? Justify it in one sentence.
2. Add the `CONSTRAINT` (e.g., `EXPECT (requested_tenor_months BETWEEN 1 AND 120)`), redeploy the pipeline, and refresh.
3. Report: how many rows did it flag or drop on the clean batch, and did gold's row count change?

## Track B — Extend the Job DAG

Add a third task to `job-definition.json` that runs **after** `quality_gate` and publishes something a consumer uses — e.g., a SQL/notebook task that `CREATE OR REPLACE`s a `fpd_latest_cohort_rates` view from `fpd_daily_metrics`.

1. Add the task with a `depends_on` of `quality_gate`.
2. State what should happen to your new task if `quality_gate` fails, and why (task dependency semantics).
3. Run the Job and confirm the run graph shows three tasks in order.

## Track C — Diagnose the FAIL

The facilitator landed the FAIL batch and the pipeline stopped. Without weakening any Expectation:

1. Name the exact Expectation and table that halted the update, and why it is `FAIL UPDATE` rather than `DROP ROW`.
2. Give the two-step recovery (what to remove from the landing, and which refresh mode to use).
3. Explain how the orchestrating Job surfaced this failure to an operator.

## Validation

Your answer is complete when it:

- Chooses an Expectation tier (or task dependency) and **justifies it from the business consequence**, not by guessing.
- States the observed effect on silver and gold row counts (quality issues stop at silver; gold stays 25,440 on the clean book).
- Does not gate on settlement timing (early/late/unsettled is the FPD5 outcome, not a defect).
- Names how the pipeline or Job made the outcome **observable** — event log, run summary, or failure alert.
