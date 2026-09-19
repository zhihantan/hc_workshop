-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Section 03 — FPD5 medallion pipeline (Lakeflow Declarative Pipelines, SQL)
-- MAGIC
-- MAGIC This notebook is the **source for a Lakeflow pipeline**, not a notebook you run cell by cell.
-- MAGIC Create a **serverless** pipeline with this file as its source and:
-- MAGIC
-- MAGIC - **Target catalog:** `hc_workshop` (canonical; a delivery may retarget, e.g. `sean_development_catalog`)
-- MAGIC - **Target schema:** `de_<your_user_id>` (e.g. `de_zhihan_tan`) — each participant targets their own schema
-- MAGIC
-- MAGIC It reads the shared **raw landing** (`workshop_shared.lending_raw_*`) and the clean
-- MAGIC `core_lending` dimensions, and builds the medallion:
-- MAGIC
-- MAGIC ```
-- MAGIC lending_raw_*  →  BRONZE (streaming ingest)  →  SILVER (Expectations)  →  GOLD (fpd_origination + fpd_daily_metrics)
-- MAGIC ```
-- MAGIC
-- MAGIC The gold `fpd_origination` table is the same FPD5 layer Section 01 analysed by hand and
-- MAGIC Section 06 modelled — here it is produced by a governed, quality-gated pipeline.

-- COMMAND ----------
-- MAGIC %md ## Bronze — raw ingest (Streaming Tables)
-- MAGIC Append-only incremental ingest from the landing zone. No transformation yet.

-- COMMAND ----------
CREATE OR REFRESH STREAMING TABLE fpd_bronze_installment
  COMMENT 'Raw installment feed, ingested incrementally from the landing zone.'
AS SELECT * FROM STREAM(hc_workshop.workshop_shared.lending_raw_installment);

-- COMMAND ----------
CREATE OR REFRESH STREAMING TABLE fpd_bronze_contract
  COMMENT 'Raw credit-contract feed, ingested incrementally from the landing zone.'
AS SELECT * FROM STREAM(hc_workshop.workshop_shared.lending_raw_credit_contract);

-- COMMAND ----------
CREATE OR REFRESH STREAMING TABLE fpd_bronze_application
  COMMENT 'Raw loan-application feed, ingested incrementally from the landing zone.'
AS SELECT * FROM STREAM(hc_workshop.workshop_shared.lending_raw_loan_application);

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Silver — validated & conformed (Expectations live here)
-- MAGIC `FAIL UPDATE` stops the pipeline on a broken key (corrupt data must never flow downstream);
-- MAGIC `DROP ROW` quarantines impossible values; a bare `EXPECT` **warns** but keeps the row.

-- COMMAND ----------
CREATE OR REFRESH STREAMING TABLE fpd_silver_installment (
  CONSTRAINT valid_contract   EXPECT (contract_id IS NOT NULL)      ON VIOLATION FAIL UPDATE,
  CONSTRAINT valid_due_date   EXPECT (due_date IS NOT NULL)         ON VIOLATION DROP ROW,
  CONSTRAINT nonneg_due       EXPECT (total_due_amount >= 0)        ON VIOLATION DROP ROW,
  CONSTRAINT observed_window  EXPECT (due_date <= DATE'2026-12-31') -- WARN (keep)
)
  COMMENT 'Validated installments. Broken keys fail the update; missing due dates and negative amounts are dropped. NOTE: settlement timing (early / on-time / late / unsettled) is NOT gated here — it is exactly the FPD5 outcome we measure downstream.'
AS SELECT installment_id, contract_id, installment_no, due_date, total_due_amount, settled_date
   FROM STREAM(fpd_bronze_installment);

-- COMMAND ----------
CREATE OR REFRESH STREAMING TABLE fpd_silver_contract (
  CONSTRAINT valid_contract    EXPECT (contract_id IS NOT NULL)   ON VIOLATION FAIL UPDATE,
  CONSTRAINT nonneg_principal  EXPECT (principal_amount IS NULL OR principal_amount >= 0)  ON VIOLATION DROP ROW,
  CONSTRAINT positive_tenor    EXPECT (tenor_months > 0)          -- WARN (revolving lines may have null tenor; gold keeps only fixed-term)
)
  COMMENT 'Validated credit contracts. Future-of-as-of originations are kept — they are valid, just outside the FPD5 observation window, which gold filters.'
AS SELECT contract_id, application_id, principal_amount, tenor_months, monthly_interest_rate_pct, origination_date
   FROM STREAM(fpd_bronze_contract);

-- COMMAND ----------
CREATE OR REFRESH STREAMING TABLE fpd_silver_application (
  CONSTRAINT valid_application EXPECT (application_id IS NOT NULL)                                     ON VIOLATION FAIL UPDATE,
  CONSTRAINT positive_income   EXPECT (declared_income_amount > 0)                                     ON VIOLATION DROP ROW,
  CONSTRAINT sane_lti          EXPECT (requested_amount / NULLIF(declared_income_amount, 0) < 20)      -- WARN (keep)
)
  COMMENT 'Validated loan applications.'
AS SELECT application_id, customer_id, product_id, store_id, application_channel_code,
          requested_amount, requested_tenor_months, declared_income_amount, underwriting_score,
          promotion_code, item_category_code, financed_amount
   FROM STREAM(fpd_bronze_application);

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Gold — the governed FPD5 layer
-- MAGIC `fpd_origination`: one row per eligible fixed-term contract with the canonical FPD5 label and
-- MAGIC origination-time features (the layer Section 06 trains on). `fpd_daily_metrics`: the vintage ×
-- MAGIC cohort FPD5 rate that feeds the Section 01 dashboard.

-- COMMAND ----------
CREATE OR REFRESH MATERIALIZED VIEW fpd_origination
  COMMENT 'One row per eligible fixed-term contract with FPD5 label + origination-time features.'
AS
WITH first_inst AS (
  SELECT contract_id,
         CASE WHEN settled_date IS NULL OR settled_date >= date_add(due_date, 5) THEN 1 ELSE 0 END AS fpd5_flag
  FROM fpd_silver_installment
  WHERE installment_no = 1
    AND date_add(due_date, 5) <= DATE'2026-09-01'
)
SELECT
  c.contract_id,
  c.origination_date,
  f.fpd5_flag,
  CASE WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026'
       THEN '0% smartphone promotion' ELSE 'Other eligible originations' END AS promotion_cohort,
  p.product_type_code,
  p.interest_method_code,
  FLOOR(datediff(c.origination_date, cust.birth_date) / 365.25) AS applicant_age_years,
  CAST(cust.monthly_income_amount AS DOUBLE) AS monthly_income_amount,
  cust.employment_type_code,
  a.application_channel_code,
  a.item_category_code,
  a.requested_amount,
  a.declared_income_amount,
  a.underwriting_score,
  a.financed_amount,
  c.principal_amount,
  c.tenor_months,
  c.monthly_interest_rate_pct,
  COALESCE(l.merchant_type_code, 'NO_STORE') AS merchant_type_code,
  COALESCE(l.region_code, 'NO_STORE')        AS store_region_code
FROM fpd_silver_contract AS c
JOIN fpd_silver_application AS a ON c.application_id = a.application_id
JOIN hc_workshop.core_lending.loan_product AS p ON a.product_id = p.product_id
JOIN hc_workshop.core_lending.customer AS cust ON a.customer_id = cust.customer_id
LEFT JOIN hc_workshop.core_lending.retail_location AS l ON a.store_id = l.store_id
JOIN first_inst AS f ON c.contract_id = f.contract_id
WHERE p.product_type_code IN ('POS_INSTALLMENT', 'CASH_LOAN');

-- COMMAND ----------
CREATE OR REFRESH MATERIALIZED VIEW fpd_daily_metrics
  COMMENT 'FPD5 rate by origination vintage and promotion cohort — feeds the AI/BI dashboard.'
AS
SELECT
  date_trunc('MONTH', origination_date) AS origination_month,
  promotion_cohort,
  COUNT(*)                       AS eligible_contracts,
  SUM(fpd5_flag)                 AS fpd5_contracts,
  ROUND(AVG(fpd5_flag) * 100, 2) AS fpd5_rate_pct
FROM fpd_origination
GROUP BY 1, 2;
