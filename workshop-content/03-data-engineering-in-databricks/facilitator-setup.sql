-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Facilitator setup — Section 03 (Data Engineering)
-- MAGIC
-- MAGIC Run once on the workshop SQL warehouse **before** participants start. This creates the shared
-- MAGIC **raw landing** that the participant Lakeflow pipeline ingests: a subset of `core_lending`
-- MAGIC (the FPD5-relevant transactional feeds) tagged as a clean daily batch.
-- MAGIC
-- MAGIC A second, **deliberately dirty batch** (the `-- DIRTY BATCH` cells) is landed *during* the
-- MAGIC session so the pipeline's Expectations demonstrably fire (WARN / DROP ROW / FAIL UPDATE).
-- MAGIC Land the WARN/DROP batch first (pipeline still completes, rows dropped/flagged); land the
-- MAGIC FAIL batch to show a broken key halting the update and triggering the Job alert.
-- MAGIC
-- MAGIC - Catalog: `hc_workshop`
-- MAGIC - As-of date: `2026-09-01` · FPD5 grace: 5 days
-- MAGIC - Landing schema: `workshop_shared` (facilitator-managed), tables prefixed `lending_raw_`
-- MAGIC
-- MAGIC If the workshop catalog changes, replace every `hc_workshop` reference consistently.

-- COMMAND ----------
-- MAGIC %md ## 0. Confirm the source dataset is present

-- COMMAND ----------
SELECT COUNT(*) AS core_lending_tables
FROM hc_workshop.information_schema.tables
WHERE table_schema = 'core_lending'
  AND table_name IN ('loan_application', 'credit_contract', 'installment',
                     'customer', 'loan_product', 'retail_location');

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## 1. Clean daily batch (batch_date = 2026-09-01)
-- MAGIC Each `lending_raw_*` table is the `core_lending` feed for the columns the pipeline needs,
-- MAGIC tagged with a `batch_date` and an `_ingested_at` landing timestamp. Dimensions
-- MAGIC (customer, product, store) stay in `core_lending` and are read directly by the pipeline.

-- COMMAND ----------
CREATE OR REPLACE TABLE hc_workshop.workshop_shared.lending_raw_loan_application AS
SELECT
  application_id, customer_id, product_id, store_id,
  application_channel_code,
  CAST(requested_amount        AS DOUBLE) AS requested_amount,
  requested_tenor_months,
  CAST(declared_income_amount  AS DOUBLE) AS declared_income_amount,
  CAST(underwriting_score      AS DOUBLE) AS underwriting_score,
  promotion_code, item_category_code,
  CAST(financed_amount         AS DOUBLE) AS financed_amount,
  DATE'2026-09-01' AS batch_date,
  current_timestamp() AS _ingested_at
FROM hc_workshop.core_lending.loan_application;

-- COMMAND ----------
CREATE OR REPLACE TABLE hc_workshop.workshop_shared.lending_raw_credit_contract AS
SELECT
  contract_id, application_id,
  CAST(principal_amount          AS DOUBLE) AS principal_amount,
  tenor_months,
  CAST(monthly_interest_rate_pct AS DOUBLE) AS monthly_interest_rate_pct,
  origination_date,
  DATE'2026-09-01' AS batch_date,
  current_timestamp() AS _ingested_at
FROM hc_workshop.core_lending.credit_contract;

-- COMMAND ----------
CREATE OR REPLACE TABLE hc_workshop.workshop_shared.lending_raw_installment AS
SELECT
  installment_id, contract_id, installment_no, due_date,
  CAST(total_due_amount AS DOUBLE) AS total_due_amount,
  settled_date,
  DATE'2026-09-01' AS batch_date,
  current_timestamp() AS _ingested_at
FROM hc_workshop.core_lending.installment;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## 2. Grants (apply after FACILITATOR_GROUP / participant identities are confirmed)
-- MAGIC Participants need to read the landing and write their own pipeline target schema.

-- COMMAND ----------
-- Example — uncomment and set <participant-group>:
-- GRANT USE CATALOG ON CATALOG hc_workshop TO `<participant-group>`;
-- GRANT USE SCHEMA, SELECT ON SCHEMA hc_workshop.workshop_shared TO `<participant-group>`;
-- GRANT USE SCHEMA, SELECT ON SCHEMA hc_workshop.core_lending TO `<participant-group>`;
-- GRANT CREATE SCHEMA ON CATALOG hc_workshop TO `<participant-group>`;  -- each creates their own pipeline target schema

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## 3. DIRTY BATCH — WARN + DROP (run during the data-quality demo)
-- MAGIC Appends `batch_date = 2026-09-02` rows built by mutating real rows. These violate DROP/WARN
-- MAGIC expectations only (no broken keys), so the pipeline **completes** but reports dropped/flagged
-- MAGIC rows in the event log. Re-runnable: delete the 2026-09-02 batch first to reset.

-- COMMAND ----------
-- installment: negative amount (DROP) and some NULL due dates (DROP). Settlement timing is left
-- untouched on purpose — early/late/unsettled is the FPD5 outcome, not a data-quality defect.
INSERT INTO hc_workshop.workshop_shared.lending_raw_installment
SELECT installment_id + 90000000 AS installment_id, contract_id, installment_no,
       CASE WHEN installment_id % 2 = 0 THEN NULL ELSE due_date END AS due_date,  -- NULL due date → DROP
       -1 * total_due_amount AS total_due_amount,          -- negative amount → DROP
       settled_date,
       DATE'2026-09-02' AS batch_date, current_timestamp() AS _ingested_at
FROM hc_workshop.core_lending.installment
WHERE installment_no = 1 ORDER BY installment_id LIMIT 40;

-- COMMAND ----------
-- loan_application: extreme loan-to-income (WARN), zero declared income (DROP)
INSERT INTO hc_workshop.workshop_shared.lending_raw_loan_application
SELECT application_id + 90000000 AS application_id, customer_id, product_id, store_id,
       application_channel_code,
       CAST(requested_amount AS DOUBLE) * 50 AS requested_amount,   -- extreme LTI → WARN
       requested_tenor_months,
       0.0 AS declared_income_amount,                               -- zero income → DROP
       CAST(underwriting_score AS DOUBLE), promotion_code, item_category_code,
       CAST(financed_amount AS DOUBLE),
       DATE'2026-09-02' AS batch_date, current_timestamp() AS _ingested_at
FROM hc_workshop.core_lending.loan_application
ORDER BY application_id LIMIT 40;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## 4. DIRTY BATCH — FAIL (run to show a broken key halting the pipeline + Job alert)
-- MAGIC A NULL `contract_id` violates a `FAIL UPDATE` expectation: the pipeline update aborts and the
-- MAGIC orchestrating Job's failure alert fires. Delete the 2026-09-03 batch to reset.

-- COMMAND ----------
INSERT INTO hc_workshop.workshop_shared.lending_raw_installment
SELECT installment_id + 95000000 AS installment_id,
       CAST(NULL AS BIGINT) AS contract_id,                -- broken key → FAIL UPDATE
       installment_no, due_date,
       CAST(total_due_amount AS DOUBLE), settled_date,
       DATE'2026-09-03' AS batch_date, current_timestamp() AS _ingested_at
FROM hc_workshop.core_lending.installment
WHERE installment_no = 1 ORDER BY installment_id LIMIT 10;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Reset helpers
-- MAGIC ```sql
-- MAGIC DELETE FROM hc_workshop.workshop_shared.lending_raw_installment       WHERE batch_date > DATE'2026-09-01';
-- MAGIC DELETE FROM hc_workshop.workshop_shared.lending_raw_loan_application   WHERE batch_date > DATE'2026-09-01';
-- MAGIC ```
