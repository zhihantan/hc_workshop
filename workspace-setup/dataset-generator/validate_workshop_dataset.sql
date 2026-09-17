-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Validate the Unicorn Finance workshop dataset
-- MAGIC
-- MAGIC Run after `generate_workshop_dataset.py`. Every result should either
-- MAGIC report zero failures or show the intended workshop distribution.
-- MAGIC
-- MAGIC ## Configuration
-- MAGIC Edit the values in the next cell to match the generator before selecting
-- MAGIC **Run all**. The settings are visible in the notebook source.

-- COMMAND ----------

DECLARE OR REPLACE VARIABLE workshop_catalog STRING DEFAULT 'hc_workshop';
DECLARE OR REPLACE VARIABLE workshop_schema STRING DEFAULT 'core_lending';
DECLARE OR REPLACE VARIABLE workshop_as_of_date DATE DEFAULT DATE'2026-09-01';

-- COMMAND ----------

USE CATALOG IDENTIFIER(session.workshop_catalog);
USE SCHEMA IDENTIFIER(session.workshop_schema);

SELECT
  current_catalog() AS validation_catalog,
  current_schema() AS validation_schema,
  session.workshop_as_of_date AS validation_as_of_date;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Tables and row counts

-- COMMAND ----------

SHOW TABLES;

-- COMMAND ----------

SELECT 'customer' AS table_name, COUNT(*) AS row_count FROM customer
UNION ALL SELECT 'retail_location', COUNT(*) FROM retail_location
UNION ALL SELECT 'loan_product', COUNT(*) FROM loan_product
UNION ALL SELECT 'loan_application', COUNT(*) FROM loan_application
UNION ALL SELECT 'credit_contract', COUNT(*) FROM credit_contract
UNION ALL SELECT 'installment', COUNT(*) FROM installment
UNION ALL SELECT 'payment', COUNT(*) FROM payment
UNION ALL SELECT 'collection_action', COUNT(*) FROM collection_action
ORDER BY table_name;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Primary-key uniqueness

-- COMMAND ----------

SELECT 'customer.customer_id' AS check_name, COUNT(*) - COUNT(DISTINCT customer_id) AS failures FROM customer
UNION ALL SELECT 'retail_location.store_id', COUNT(*) - COUNT(DISTINCT store_id) FROM retail_location
UNION ALL SELECT 'loan_product.product_id', COUNT(*) - COUNT(DISTINCT product_id) FROM loan_product
UNION ALL SELECT 'loan_application.application_id', COUNT(*) - COUNT(DISTINCT application_id) FROM loan_application
UNION ALL SELECT 'credit_contract.contract_id', COUNT(*) - COUNT(DISTINCT contract_id) FROM credit_contract
UNION ALL SELECT 'installment.installment_id', COUNT(*) - COUNT(DISTINCT installment_id) FROM installment
UNION ALL SELECT 'payment.payment_id', COUNT(*) - COUNT(DISTINCT payment_id) FROM payment
UNION ALL SELECT 'collection_action.collection_action_id', COUNT(*) - COUNT(DISTINCT collection_action_id) FROM collection_action
ORDER BY check_name;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Foreign-key integrity

-- COMMAND ----------

SELECT 'application_customer' AS check_name, COUNT(*) AS failures
FROM loan_application a LEFT ANTI JOIN customer c ON a.customer_id = c.customer_id
UNION ALL
SELECT 'application_location', COUNT(*)
FROM loan_application a LEFT ANTI JOIN retail_location l ON a.store_id = l.store_id
WHERE a.store_id IS NOT NULL
UNION ALL
SELECT 'application_product', COUNT(*)
FROM loan_application a LEFT ANTI JOIN loan_product p ON a.product_id = p.product_id
UNION ALL
SELECT 'contract_application', COUNT(*)
FROM credit_contract c LEFT ANTI JOIN loan_application a ON c.application_id = a.application_id
UNION ALL
SELECT 'installment_contract', COUNT(*)
FROM installment i LEFT ANTI JOIN credit_contract c ON i.contract_id = c.contract_id
UNION ALL
SELECT 'payment_contract', COUNT(*)
FROM payment p LEFT ANTI JOIN credit_contract c ON p.contract_id = c.contract_id
UNION ALL
SELECT 'payment_installment', COUNT(*)
FROM payment p LEFT ANTI JOIN installment i ON p.installment_id = i.installment_id
WHERE p.installment_id IS NOT NULL
UNION ALL
SELECT 'collection_contract', COUNT(*)
FROM collection_action ca LEFT ANTI JOIN credit_contract c ON ca.contract_id = c.contract_id
UNION ALL
SELECT 'collection_installment', COUNT(*)
FROM collection_action ca LEFT ANTI JOIN installment i ON ca.installment_id = i.installment_id
WHERE ca.installment_id IS NOT NULL
ORDER BY check_name;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Contract and payment consistency

-- COMMAND ----------

SELECT 'contract_requires_one_amount_type' AS check_name, COUNT(*) AS failures
FROM credit_contract
WHERE (principal_amount IS NULL AND credit_limit_amount IS NULL)
   OR (principal_amount IS NOT NULL AND credit_limit_amount IS NOT NULL)
UNION ALL
SELECT 'approved_application_for_every_contract', COUNT(*)
FROM credit_contract c
JOIN loan_application a USING (application_id)
WHERE a.decision_code <> 'APPROVED'
UNION ALL
SELECT 'posted_payment_has_posted_at', COUNT(*)
FROM payment
WHERE payment_status_code = 'POSTED' AND posted_at IS NULL
UNION ALL
SELECT 'failed_payment_has_reason', COUNT(*)
FROM payment
WHERE payment_status_code = 'FAILED' AND failure_reason_code IS NULL
UNION ALL
SELECT 'nonnegative_outstanding', COUNT(*)
FROM installment
WHERE outstanding_amount < 0
UNION ALL
SELECT 'payment_status_consistency', COUNT(*)
FROM payment
WHERE (payment_status_code = 'POSTED'
       AND (posted_at IS NULL OR failure_reason_code IS NOT NULL))
   OR (payment_status_code = 'FAILED'
       AND (posted_at IS NOT NULL OR failure_reason_code IS NULL))
UNION ALL
SELECT 'collection_payment_reconciliation', COUNT(*)
FROM collection_action ca
LEFT JOIN payment p
  ON ca.installment_id = p.installment_id
 AND ca.action_at = p.payment_at
 AND ca.amount_collected = p.payment_amount
 AND p.payment_status_code = 'POSTED'
WHERE (ca.outcome_code = 'PAYMENT_RECEIVED' AND p.payment_id IS NULL)
   OR (ca.outcome_code <> 'PAYMENT_RECEIVED' AND ca.amount_collected <> 0)
UNION ALL
SELECT 'partial_payment_balance_reconciliation', COUNT(*)
FROM installment i
JOIN (
  SELECT installment_id, SUM(payment_amount) AS posted_amount
  FROM payment
  WHERE payment_status_code = 'POSTED'
  GROUP BY installment_id
) p USING (installment_id)
WHERE i.installment_status_code = 'PARTIAL'
  AND ABS(i.total_due_amount - i.outstanding_amount - p.posted_amount) > 0.01
UNION ALL
SELECT 'payment_after_installment_update', COUNT(*)
FROM payment p
JOIN installment i USING (installment_id)
WHERE p.payment_at > i.updated_at
UNION ALL
SELECT 'payment_after_contract_close', COUNT(*)
FROM payment p
JOIN credit_contract c USING (contract_id)
WHERE c.closed_at IS NOT NULL
  AND p.payment_at > c.closed_at;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Product and application mix

-- COMMAND ----------

SELECT
  p.product_type_code,
  COUNT(*) AS applications,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS application_pct,
  ROUND(AVG(CASE WHEN a.decision_code = 'APPROVED' THEN 1 ELSE 0 END) * 100, 2) AS approval_pct
FROM loan_application a
JOIN loan_product p USING (product_id)
GROUP BY p.product_type_code
ORDER BY applications DESC;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Intended analytical story

-- COMMAND ----------

WITH store_volume AS (
  SELECT store_id, COUNT(*) AS applications
  FROM loan_application
  WHERE store_id IS NOT NULL
  GROUP BY store_id
),
ranked AS (
  SELECT
    store_id,
    applications,
    ROW_NUMBER() OVER (ORDER BY applications DESC, store_id) AS store_rank,
    COUNT(*) OVER () AS store_count
  FROM store_volume
)
SELECT
  ROUND(
    SUM(CASE WHEN store_rank <= CEIL(store_count * 0.20)
             THEN applications ELSE 0 END) * 100.0 / SUM(applications),
    2
  ) AS top_20_store_application_pct
FROM ranked;

-- COMMAND ----------

WITH first_installment AS (
  SELECT
    contract_id,
    MAX(CASE WHEN settled_date IS NULL
                   OR settled_date >= date_add(due_date, 5)
             THEN 1 ELSE 0 END) AS first_payment_default
  FROM installment
  WHERE installment_no = 1
    AND date_add(due_date, 5) <= session.workshop_as_of_date
  GROUP BY contract_id
)
SELECT
  CASE
    WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026' THEN '0% smartphone promotion'
    ELSE 'other originations'
  END AS cohort,
  COUNT(*) AS contracts,
  ROUND(AVG(COALESCE(f.first_payment_default, 0)) * 100, 2) AS first_payment_default_pct
FROM credit_contract c
JOIN loan_application a USING (application_id)
JOIN first_installment f USING (contract_id)
GROUP BY 1
ORDER BY 1;

-- COMMAND ----------

WITH first_installment AS (
  SELECT
    contract_id,
    MAX(CASE WHEN settled_date IS NULL
                   OR settled_date >= date_add(due_date, 5)
             THEN 1 ELSE 0 END) AS first_payment_default
  FROM installment
  WHERE installment_no = 1
    AND date_add(due_date, 5) <= session.workshop_as_of_date
  GROUP BY contract_id
)
SELECT
  l.merchant_name,
  l.store_name,
  a.sales_associate_id,
  COUNT(*) AS promo_contracts,
  SUM(f.first_payment_default) AS first_payment_defaults,
  ROUND(AVG(f.first_payment_default) * 100, 2) AS first_payment_default_pct
FROM credit_contract c
JOIN loan_application a USING (application_id)
JOIN retail_location l ON a.store_id = l.store_id
JOIN first_installment f USING (contract_id)
WHERE a.promotion_code = 'ZERO_SMARTPHONE_2026'
GROUP BY l.merchant_name, l.store_name, a.sales_associate_id
HAVING COUNT(*) >= 2
ORDER BY first_payment_default_pct DESC, promo_contracts DESC
LIMIT 25;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Delinquency and collections

-- COMMAND ----------

SELECT
  CASE
    WHEN due_date > session.workshop_as_of_date THEN 'NOT_DUE'
    WHEN outstanding_amount = 0 THEN 'CURRENT_OR_PAID'
    WHEN datediff(session.workshop_as_of_date, due_date) = 0 THEN 'DUE_TODAY'
    WHEN datediff(session.workshop_as_of_date, due_date) < 5 THEN '1-4'
    WHEN datediff(session.workshop_as_of_date, due_date) < 30 THEN '5-29'
    WHEN datediff(session.workshop_as_of_date, due_date) < 60 THEN '30-59'
    WHEN datediff(session.workshop_as_of_date, due_date) < 90 THEN '60-89'
    ELSE '90+'
  END AS dpd_bucket,
  COUNT(*) AS installments,
  ROUND(SUM(outstanding_amount), 2) AS outstanding_php
FROM installment
GROUP BY 1
ORDER BY 1;

-- COMMAND ----------

SELECT
  days_past_due_at_action,
  action_type_code,
  outcome_code,
  COUNT(*) AS actions,
  ROUND(SUM(promise_amount), 2) AS promised_php,
  ROUND(SUM(amount_collected), 2) AS collected_php
FROM collection_action
GROUP BY days_past_due_at_action, action_type_code, outcome_code
ORDER BY days_past_due_at_action, action_type_code, outcome_code;
