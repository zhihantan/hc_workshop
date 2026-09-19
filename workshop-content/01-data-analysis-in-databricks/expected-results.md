# Expected results and troubleshooting

**Participant note:** Complete the focused exercise before opening this file.

These values assume the default standard-scale dataset, master seed `20260922`, and as-of date `2026-09-01`. A different approved generator configuration can produce different counts and rates.

## Observable results

### Source inventory

- All eight `core_lending` tables are listed.
- No missing-table exception is raised.
- The application summary contains the `IN_STORE`, `MOBILE_APP`, `WEB`, and `CALL_CENTER` channels and the `APPROVED`, `DECLINED`, and `CANCELLED` decisions.

### Application exploration

- POS installment is the largest product family.
- `Unicorn 0% Brand Promotion` appears during the promotion window.
- The SQL and PySpark results read the same Unity Catalog source data under the participant's identity.

### FPD5 analysis

- The temporary view has one row per eligible contract.
- The default standard-scale cohort rates are approximately:
  - 0% smartphone promotion: **42.26%**
  - Other eligible originations: **21.03%**
- The top 20% of stores account for approximately **81.13%** of in-store applications. This is origination-volume context, not a measure of FPD5 concentration.
- The store-associate ranking returns repeated pairs with at least 10 eligible promotion contracts.
- After changing `ANALYSIS_DIMENSION`, the participant breakdown contains one row per selected segment and retains the eligible-contract denominator.
- The selected dimension and segment can change the apparent concentration, but do not change the FPD5 definition.

Small rounding differences are acceptable only when the underlying generator configuration differs. Large differences usually mean that the as-of date, eligibility filter, installment number, or settlement boundary is wrong.

### Participant investigation table

- The table is named `unicorn_<runner_id>_fpd_investigation`.
- The baseline snapshot contains one row per value of the participant's selected dimension and the columns `analysis_dimension`, `segment`, `eligible_contracts`, `fpd5_contracts`, and `fpd5_rate_pct`.
- The evolved snapshot has the same analytical rows and adds a populated `review_note`.
- The post-evolution version is greater than the captured baseline version.
- `DESCRIBE HISTORY` shows the table write, column addition, and update.
- Rerunning the notebook is safe, but version numbers continue from the table's existing transaction history. Do not expect version `0`.
- The table name contains a sanitized runner ID plus a short hash derived from the participant's workspace identity, preventing collisions between participants.

### Metric View

- When `hc_workshop.workshop_shared.fpd_metrics` is available on the selected compute, the Metric View result matches the cohort rates calculated from the session temporary view.
- The rate is returned as a ratio, approximately `0.4226` and `0.2103`; the Metric View display format can render these as percentages in AI/BI.
- If the Metric View was deliberately omitted as a documented workspace fallback, the notebook reports that it is not installed and shows the equivalent session result. If the Metric View exists but its query fails, the notebook stops so the facilitator can diagnose the actual setup, permission, or compatibility error.

### Dashboard and participant-created Genie Agent

- Dashboard KPIs reconcile to the Metric View result.
- Changing the promotion filter updates every intended widget.
- The published dashboard remains unchanged until the facilitator republishes a changed draft.
- Each participant has one **Unicorn FPD5 Investigator — `<workspace_username>`** Agent in their own user folder.
- The Agent is not shared with all account users, the workshop group, or another participant.
- `hc_workshop.workshop_shared.fpd_metrics` is the Agent's only data source.
- The Genie Agent's generated SQL uses `MEASURE()` against `fpd_metrics`.
- The Genie answer identifies the observation date and does not claim confirmed fraud.

### SQL warehouse workload inspection

- Query History contains a dashboard, Metric View, or Genie-generated statement from the session.
- Participants can distinguish time spent waiting from time spent executing.
- A queue indicates concurrency or capacity pressure; spill indicates that an individual query exceeded available memory.
- If the live warehouse has neither symptom, the facilitator uses a saved read-only profile and does not manufacture a pathological query.

## Shortest recovery paths

### A source table is missing

Stop the lab. The administrator should rerun the dataset generator and confirm its final `SUCCESS` message. Do not create substitute participant tables.

### The as-of-date validation fails

Do not bypass the guard. Confirm that `installment` carries the expected `workshop.as_of_date` table property. If the administrator intentionally generated a different as-of date, update the notebook and shared FPD5 view together, rerun their validation, and republish dependent assets before participants continue.

### `USE_CATALOG`, `USE_SCHEMA`, or `SELECT` is denied

Ask the administrator to grant access to the workshop catalog and source schema. Do not redirect participants to `main`, `hive_metastore`, or a personal catalog.

### The participant Delta table cannot be created or replaced

Confirm that the participant has `USE SCHEMA` and `CREATE TABLE` on `workshop_labs`, and owns or can modify only their `unicorn_<runner_id>_fpd_investigation` table. If that participant-specific name is unexpectedly owned by another identity, stop and investigate rather than taking ownership.

### Python cells fail on a SQL warehouse

Attach the notebook to serverless notebook compute or Unity Catalog-compatible all-purpose compute. A notebook attached to a SQL warehouse supports SQL and Markdown cells, not the Python cells used in this lab.

### Serverless notebook compute is unavailable

Use an approved Unity Catalog-compatible classic all-purpose resource. Record the fallback and explain which configuration or library requirement justified it.

### The shared Metric View is missing

Run `../../workshop-setup/section-01-facilitator-setup.sql` on a compatible SQL warehouse, verify its final two queries, and confirm participant `SELECT` access. If Metric Views are unavailable in the target workspace, use the notebook's temporary-view fallback and omit participant Agent creation rather than duplicating the FPD5 formula or inventing a result. Record this as a blocker for Section 02.

### The dashboard shows different values

Check, in order:

1. Dataset source is `hc_workshop.workshop_shared.fpd_metrics`.
2. The dashboard filter is not excluding a cohort.
3. The draft was republished after changes.
4. The dashboard uses the same `2026-09-01` observation date.
5. The publisher or viewer has the intended Unity Catalog permissions.

### Queries queue

Open the warehouse Monitoring tab and inspect Peak Queued Queries, running queries, and cluster count. Sustained queueing is primarily a concurrency/capacity symptom; review maximum clusters and workload isolation before changing individual-query size.

### A query spills to disk

Open Query History, select the statement, and inspect Query Profile or the `DATA_SPILL` insight. Reduce scanned rows or wide columns and review the query plan; increase warehouse size when the query genuinely needs more memory. Adding clusters addresses concurrency, not the memory available to one query.

### Genie gives a plausible but wrong answer

Inspect the generated SQL and compare it with the trusted Metric View query. Confirm that the participant attached only `fpd_metrics` and did not accept a suggestion that duplicated the FPD5 formula. Keep the Agent private. Section 02 uses Genie Code to fix the smallest governed surface—metadata, a concise instruction, categorical value mapping, or verified example SQL—then reruns the affected question and a previously correct regression question.

### Another participant can open the Agent

Open the Agent's **Share** dialog and remove direct grants to other participants, the workshop group, or **All account users**. Confirm that the Agent is stored in the creator's user folder rather than **Shared**. Inherited workspace-administrator access is expected.

