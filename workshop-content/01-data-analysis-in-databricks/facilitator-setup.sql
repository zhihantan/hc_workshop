-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Facilitator setup — Section 01
-- MAGIC
-- MAGIC Run this notebook on the workshop SQL warehouse before participant access.
-- MAGIC
-- MAGIC - Default catalog: `hc_workshop`
-- MAGIC - As-of date: `2026-09-01`
-- MAGIC - SQL warehouse: **TBD — facilitator confirmation required**
-- MAGIC - Facilitator group: **TBD — facilitator confirmation required**
-- MAGIC
-- MAGIC If the workshop catalog changes, replace every `hc_workshop` reference consistently before running. This notebook creates only facilitator-owned assets in `workshop_shared`.

-- COMMAND ----------
SELECT
  COUNT(*) AS source_table_count
FROM hc_workshop.information_schema.tables
WHERE table_schema = 'core_lending'
  AND table_name IN (
    'customer',
    'retail_location',
    'loan_product',
    'loan_application',
    'credit_contract',
    'installment',
    'payment',
    'collection_action'
  );

-- COMMAND ----------
CREATE OR REPLACE VIEW hc_workshop.workshop_shared.fpd_analysis
COMMENT 'One row per fixed-term contract whose first installment reached the FPD5 observation point by 2026-09-01. Synthetic workshop data only.'
AS
WITH first_installment AS (
  SELECT
    contract_id,
    due_date AS first_due_date,
    settled_date AS first_settled_date,
    CASE
      WHEN settled_date IS NULL
        OR settled_date >= date_add(due_date, 5)
      THEN 1
      ELSE 0
    END AS fpd5_flag
  FROM hc_workshop.core_lending.installment
  WHERE installment_no = 1
    AND date_add(due_date, 5) <= DATE'2026-09-01'
)
SELECT
  a.application_id,
  c.contract_id,
  CAST(a.submitted_at AS DATE) AS application_date,
  c.origination_date,
  p.product_name,
  p.product_type_code,
  a.application_channel_code,
  a.promotion_code,
  CASE
    WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026'
    THEN '0% smartphone promotion'
    ELSE 'Other eligible originations'
  END AS promotion_cohort,
  COALESCE(l.store_code, 'NO_STORE') AS store_code,
  COALESCE(l.store_name, 'No physical store') AS store_name,
  COALESCE(l.merchant_name, 'No physical merchant') AS merchant_name,
  COALESCE(l.province, 'NO_STORE') AS store_province,
  COALESCE(l.region_code, 'NO_STORE') AS region_code,
  COALESCE(a.sales_associate_id, 'NO_ASSOCIATE') AS sales_associate_id,
  c.principal_amount,
  f.first_due_date,
  f.first_settled_date,
  f.fpd5_flag
FROM hc_workshop.core_lending.credit_contract AS c
JOIN hc_workshop.core_lending.loan_application AS a
  ON c.application_id = a.application_id
JOIN hc_workshop.core_lending.loan_product AS p
  ON a.product_id = p.product_id
JOIN first_installment AS f
  ON c.contract_id = f.contract_id
LEFT JOIN hc_workshop.core_lending.retail_location AS l
  ON a.store_id = l.store_id;

-- COMMAND ----------
CREATE OR REPLACE VIEW hc_workshop.workshop_shared.fpd_metrics
WITH METRICS
LANGUAGE YAML
AS $$
  version: 1.1
  source: hc_workshop.workshop_shared.fpd_analysis
  comment: "Governed first-payment-default metrics for eligible Unicorn Finance fixed-term contracts. FPD5 means the first installment was unsettled or settled on or after five days past due, observed through 2026-09-01."
  fields:
    - name: origination_date
      expr: origination_date
      comment: "Date on which the eligible credit contract originated."
      display_name: "Origination Date"
      synonyms: ["contract date", "booking date"]
      format:
        type: date
        date_format: year_month_day
    - name: origination_month
      expr: "CAST(DATE_TRUNC('MONTH', origination_date) AS DATE)"
      comment: "Calendar month in which the eligible credit contract originated."
      display_name: "Origination Month"
      synonyms: ["booking month", "vintage month"]
    - name: product_name
      expr: product_name
      comment: "Commercial name of the requested lending product."
      display_name: "Product"
      synonyms: ["loan product", "credit product"]
    - name: product_type
      expr: product_type_code
      comment: "Product family code for the eligible contract."
      display_name: "Product Type"
      synonyms: ["product family"]
    - name: application_channel
      expr: application_channel_code
      comment: "Channel through which the source application was submitted."
      display_name: "Application Channel"
      synonyms: ["origination channel", "channel"]
    - name: promotion_cohort
      expr: promotion_cohort
      comment: "Comparison cohort: 0% smartphone promotion or all other eligible originations."
      display_name: "Promotion Cohort"
      synonyms: ["promo cohort", "campaign cohort", "promotion"]
    - name: merchant_name
      expr: merchant_name
      comment: "Retail partner associated with the physical origination, or the no-store label."
      display_name: "Merchant"
      synonyms: ["retail partner", "merchant"]
    - name: store_code
      expr: store_code
      comment: "Stable code for the physical origination store, or NO_STORE."
      display_name: "Store Code"
      synonyms: ["location code"]
    - name: store_name
      expr: store_name
      comment: "Display name of the physical origination store."
      display_name: "Store"
      synonyms: ["retail location", "location"]
    - name: store_province
      expr: store_province
      comment: "Province of the physical origination store, or NO_STORE."
      display_name: "Store Province"
      synonyms: ["province", "location province"]
    - name: region_code
      expr: region_code
      comment: "Philippine administrative region code of the physical origination store."
      display_name: "Region"
      synonyms: ["store region", "administrative region"]
    - name: sales_associate_id
      expr: sales_associate_id
      comment: "Synthetic assisting sales-associate identifier. Treat as sensitive during governance exercises."
      display_name: "Sales Associate ID"
      synonyms: ["associate", "seller ID"]
    - name: first_due_date
      expr: first_due_date
      comment: "Due date of the first scheduled installment."
      display_name: "First Due Date"
      synonyms: ["first installment due date"]
      format:
        type: date
        date_format: year_month_day
  measures:
    - name: eligible_contracts
      expr: COUNT(1)
      comment: "Number of fixed-term contracts whose first installment reached the five-day observation point by 2026-09-01."
      display_name: "Eligible Contracts"
      synonyms: ["observed contracts", "FPD denominator"]
      format:
        type: number
        decimal_places:
          type: exact
          places: 0
        abbreviation: compact
    - name: fpd5_contracts
      expr: SUM(fpd5_flag)
      comment: "Number of eligible contracts that met the workshop FPD5 definition."
      display_name: "FPD5 Contracts"
      synonyms: ["first payment defaults", "five-day first payment defaults"]
      format:
        type: number
        decimal_places:
          type: exact
          places: 0
        abbreviation: compact
    - name: fpd5_rate
      expr: "MEASURE(`fpd5_contracts`) * 1.0 / NULLIF(MEASURE(`eligible_contracts`), 0)"
      comment: "FPD5 contracts divided by eligible contracts at the selected dimension grain."
      display_name: "FPD5 Rate"
      synonyms: ["first payment default rate", "FPD rate"]
      format:
        type: percentage
        decimal_places:
          type: exact
          places: 2
    - name: originated_principal
      expr: SUM(principal_amount)
      comment: "Total principal in Philippine pesos for eligible fixed-term contracts."
      display_name: "Originated Principal"
      synonyms: ["booked principal", "financed principal"]
      format:
        type: currency
        currency_code: PHP
        decimal_places:
          type: max
          places: 2
        abbreviation: compact
    - name: average_principal
      expr: AVG(principal_amount)
      comment: "Average principal in Philippine pesos per eligible fixed-term contract."
      display_name: "Average Principal"
      synonyms: ["average ticket", "average financed amount"]
      format:
        type: currency
        currency_code: PHP
        decimal_places:
          type: max
          places: 2
$$;

-- COMMAND ----------
SELECT
  promotion_cohort,
  MEASURE(eligible_contracts) AS eligible_contracts,
  MEASURE(fpd5_contracts) AS fpd5_contracts,
  MEASURE(fpd5_rate) AS fpd5_rate
FROM hc_workshop.workshop_shared.fpd_metrics
GROUP BY ALL
ORDER BY fpd5_rate DESC;

-- COMMAND ----------
SELECT
  origination_month,
  promotion_cohort,
  MEASURE(eligible_contracts) AS eligible_contracts,
  MEASURE(fpd5_contracts) AS fpd5_contracts,
  MEASURE(fpd5_rate) AS fpd5_rate
FROM hc_workshop.workshop_shared.fpd_metrics
GROUP BY ALL
ORDER BY origination_month, promotion_cohort;

-- COMMAND ----------
SELECT
  store_code,
  store_name,
  MEASURE(eligible_contracts) AS eligible_contracts,
  MEASURE(fpd5_contracts) AS fpd5_contracts,
  MEASURE(fpd5_rate) AS fpd5_rate
FROM hc_workshop.workshop_shared.fpd_metrics
WHERE promotion_cohort = '0% smartphone promotion'
GROUP BY ALL
HAVING MEASURE(eligible_contracts) >= 10
ORDER BY fpd5_rate DESC, eligible_contracts DESC, store_code
LIMIT 15;

-- COMMAND ----------
SELECT
  store_code,
  store_name,
  sales_associate_id,
  MEASURE(eligible_contracts) AS eligible_contracts,
  MEASURE(fpd5_contracts) AS fpd5_contracts,
  MEASURE(fpd5_rate) AS fpd5_rate
FROM hc_workshop.workshop_shared.fpd_metrics
WHERE promotion_cohort = '0% smartphone promotion'
GROUP BY ALL
HAVING MEASURE(eligible_contracts) >= 10
ORDER BY fpd5_rate DESC, eligible_contracts DESC, store_code
LIMIT 15;

-- COMMAND ----------
-- Apply grants only after FACILITATOR_GROUP and participant identities are confirmed.
-- Example:
-- GRANT SELECT ON VIEW hc_workshop.workshop_shared.fpd_analysis TO `<participant-group>`;
-- GRANT SELECT ON VIEW hc_workshop.workshop_shared.fpd_metrics TO `<participant-group>`;

