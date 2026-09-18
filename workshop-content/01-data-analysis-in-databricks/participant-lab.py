# Databricks notebook source
# MAGIC %md
# MAGIC # Section 01 — Data Analysis in Databricks
# MAGIC
# MAGIC **Scenario:** Atlas Ridge Consulting has handed over Unicorn Finance's analytical platform. We will verify the inherited data, calculate first-payment default consistently, and leave behind an auditable participant-owned Delta asset.
# MAGIC
# MAGIC **FPD5 definition:** Include only first installments for which `due_date + 5 days` is on or before the declared as-of date. A null settlement date or settlement on/after day five counts as FPD5.
# MAGIC
# MAGIC All records are synthetic. An elevated rate is an investigation signal, not proof of fraud.

# COMMAND ----------
import re
from datetime import date
from pyspark.sql import functions as F

CATALOG = "hc_workshop"
AS_OF_DATE = date(2026, 9, 1)

CORE_SCHEMA = f"{CATALOG}.core_lending"
LABS_SCHEMA = f"{CATALOG}.workshop_labs"
SHARED_SCHEMA = f"{CATALOG}.workshop_shared"
FPD_VIEW = "fpd_contracts"

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Find the inherited source assets
# MAGIC
# MAGIC The source schema is shared and read-only. Start by checking what exists instead of relying on a handover document alone.

# COMMAND ----------
expected_tables = {
    "customer",
    "retail_location",
    "loan_product",
    "loan_application",
    "credit_contract",
    "installment",
    "payment",
    "collection_action",
}

inventory = spark.sql(f"SHOW TABLES IN {CORE_SCHEMA}")
actual_tables = {row.tableName for row in inventory.collect()}
missing_tables = expected_tables - actual_tables

if missing_tables:
    raise RuntimeError(f"Workshop dataset is incomplete. Missing: {sorted(missing_tables)}")

source_as_of_date = (
    spark.sql(f"DESCRIBE DETAIL {CORE_SCHEMA}.installment")
    .selectExpr("properties['workshop.as_of_date'] AS workshop_as_of_date")
    .first()[0]
)
if source_as_of_date != AS_OF_DATE.isoformat():
    raise ValueError(
        f"The inherited installment table is dated {source_as_of_date!r}; "
        f"this analysis expects {AS_OF_DATE.isoformat()}."
    )

display(inventory.orderBy("tableName"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Explore with PySpark
# MAGIC
# MAGIC Use DataFrames for interactive profiling and transformations that benefit from Python. The same Unity Catalog permissions apply whether the table is accessed from Python or SQL.

# COMMAND ----------
applications = spark.table(f"{CORE_SCHEMA}.loan_application")

application_summary = (
    applications.groupBy("application_channel_code", "decision_code")
    .agg(
        F.count("*").alias("applications"),
        F.round(F.sum("requested_amount"), 2).alias("requested_amount_php"),
        F.round(F.avg("underwriting_score"), 2).alias("average_underwriting_score"),
    )
    .orderBy(F.desc("applications"))
)

display(application_summary)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Explore with SQL
# MAGIC
# MAGIC This query joins applications to product definitions and exposes the promotion period. Use the visualization control under the result to plot `application_month` on the x-axis and `applications` on the y-axis, colored by `product_name`.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   DATE_TRUNC('MONTH', a.submitted_at) AS application_month,
# MAGIC   p.product_name,
# MAGIC   COALESCE(a.promotion_code, 'NO_PROMOTION') AS promotion_code,
# MAGIC   COUNT(*) AS applications,
# MAGIC   SUM(CASE WHEN a.decision_code = 'APPROVED' THEN 1 ELSE 0 END) AS approved_applications
# MAGIC FROM hc_workshop.core_lending.loan_application AS a
# MAGIC JOIN hc_workshop.core_lending.loan_product AS p
# MAGIC   ON a.product_id = p.product_id
# MAGIC GROUP BY ALL
# MAGIC ORDER BY application_month, applications DESC

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Build the eligible FPD5 population
# MAGIC
# MAGIC Grain matters: the output must contain exactly one row per eligible fixed-term contract. We use a session-scoped temporary view because the analysis does not need another shared persistent table.

# COMMAND ----------
fpd_contracts = spark.sql(
    f"""
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
      FROM {CORE_SCHEMA}.installment
      WHERE installment_no = 1
        AND date_add(due_date, 5) <= DATE'{AS_OF_DATE.isoformat()}'
    )
    SELECT
      a.application_id,
      c.contract_id,
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
    FROM {CORE_SCHEMA}.credit_contract AS c
    JOIN {CORE_SCHEMA}.loan_application AS a
      ON c.application_id = a.application_id
    JOIN {CORE_SCHEMA}.loan_product AS p
      ON a.product_id = p.product_id
    JOIN first_installment AS f
      ON c.contract_id = f.contract_id
    LEFT JOIN {CORE_SCHEMA}.retail_location AS l
      ON a.store_id = l.store_id
    """
)

fpd_contracts.createOrReplaceTempView(FPD_VIEW)

duplicate_contracts = (
    fpd_contracts.groupBy("contract_id")
    .count()
    .filter(F.col("count") > 1)
    .count()
)
if duplicate_contracts:
    raise RuntimeError("FPD5 dataset is not at one-row-per-contract grain")

print(f"Created session temporary view: {FPD_VIEW}")
print(f"Eligible contracts: {fpd_contracts.count():,}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Compare cohorts and concentration
# MAGIC
# MAGIC The denominator is **eligible contracts**, not all applications and not all approved contracts.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   promotion_cohort,
# MAGIC   COUNT(*) AS eligible_contracts,
# MAGIC   SUM(fpd5_flag) AS fpd5_contracts,
# MAGIC   ROUND(AVG(fpd5_flag) * 100, 2) AS fpd5_rate_pct,
# MAGIC   ROUND(SUM(principal_amount), 2) AS originated_principal_php
# MAGIC FROM fpd_contracts
# MAGIC GROUP BY promotion_cohort
# MAGIC ORDER BY fpd5_rate_pct DESC

# COMMAND ----------
# MAGIC %sql
# MAGIC WITH store_volume AS (
# MAGIC   SELECT store_id, COUNT(*) AS applications
# MAGIC   FROM hc_workshop.core_lending.loan_application
# MAGIC   WHERE store_id IS NOT NULL
# MAGIC   GROUP BY store_id
# MAGIC ),
# MAGIC ranked AS (
# MAGIC   SELECT
# MAGIC     store_id,
# MAGIC     applications,
# MAGIC     ROW_NUMBER() OVER (ORDER BY applications DESC, store_id) AS store_rank,
# MAGIC     COUNT(*) OVER () AS store_count
# MAGIC   FROM store_volume
# MAGIC )
# MAGIC SELECT
# MAGIC   ROUND(
# MAGIC     100.0 * SUM(CASE
# MAGIC       WHEN store_rank <= CEIL(store_count * 0.20) THEN applications
# MAGIC       ELSE 0
# MAGIC     END) / SUM(applications),
# MAGIC     2
# MAGIC   ) AS top_20_pct_store_application_share
# MAGIC FROM ranked

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   store_code,
# MAGIC   store_name,
# MAGIC   sales_associate_id,
# MAGIC   COUNT(*) AS eligible_contracts,
# MAGIC   SUM(fpd5_flag) AS fpd5_contracts,
# MAGIC   ROUND(AVG(fpd5_flag) * 100, 2) AS fpd5_rate_pct
# MAGIC FROM fpd_contracts
# MAGIC WHERE promotion_code = 'ZERO_SMARTPHONE_2026'
# MAGIC GROUP BY store_code, store_name, sales_associate_id
# MAGIC HAVING COUNT(*) >= 10
# MAGIC ORDER BY fpd5_rate_pct DESC, eligible_contracts DESC, store_code
# MAGIC LIMIT 15

# COMMAND ----------
# MAGIC %md
# MAGIC ### Try it
# MAGIC
# MAGIC Use the three results above to complete `exercises.md`. Your conclusion must include the eligible-contract denominator and must not call the pattern confirmed fraud.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Delta Lake: schema evolution and time travel
# MAGIC
# MAGIC This demonstration creates one table in `workshop_labs`. Your assigned team ID groups workshop assets for handover and cleanup. The notebook adds your username automatically so teammates do not overwrite each other's table.
# MAGIC
# MAGIC 1. Create or replace a ten-row Delta table with two columns.
# MAGIC 2. Append ten rows containing a new `review_note` column with per-write schema evolution enabled.
# MAGIC 3. Read the captured baseline version and current version.
# MAGIC
# MAGIC In production, time travel works only while the transaction log and referenced data files are retained. Do not shorten `VACUUM` retention casually.

# COMMAND ----------
dbutils.widgets.text("team_id", "team01", "Assigned team ID")
TEAM_ID = dbutils.widgets.get("team_id").strip().lower()

if not TEAM_ID or not TEAM_ID.replace("_", "").isalnum():
    raise ValueError(
        "Enter the assigned team ID using only letters, numbers, or underscores "
        "(for example, team01)."
    )

current_user = spark.sql("SELECT current_user()").first()[0]
RUNNER_ID = re.sub(r"[^a-z0-9]+", "_", current_user.split("@")[0].lower()).strip("_")

DELTA_DEMO_TABLE = f"unicorn_{TEAM_ID}_{RUNNER_ID}_delta_demo"
DELTA_DEMO_FQ = f"{LABS_SCHEMA}.{DELTA_DEMO_TABLE}"

print(f"Delta demo table: {DELTA_DEMO_FQ}")

# COMMAND ----------
spark.sql(
    f"""
    CREATE OR REPLACE TABLE {DELTA_DEMO_FQ}
    USING DELTA
    COMMENT 'Participant-owned table for the workshop schema-evolution and time-travel demonstration'
    AS
    SELECT application_id, decision_code
    FROM {CORE_SCHEMA}.loan_application
    WHERE application_id BETWEEN 1 AND 10
    """
)

baseline_version = int(
    spark.sql(f"DESCRIBE HISTORY {DELTA_DEMO_FQ}")
    .agg(F.max("version"))
    .first()[0]
)

evolved_rows = (
    spark.table(f"{CORE_SCHEMA}.loan_application")
    .filter(F.col("application_id").between(11, 20))
    .select(
        "application_id",
        "decision_code",
        F.lit("Added through explicit per-write schema evolution").alias("review_note"),
    )
)

spark.sql(
    f"DELETE FROM {DELTA_DEMO_FQ} WHERE application_id BETWEEN 11 AND 20"
)

(
    evolved_rows.write.format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(DELTA_DEMO_FQ)
)

current_version = int(
    spark.sql(f"DESCRIBE HISTORY {DELTA_DEMO_FQ}")
    .agg(F.max("version"))
    .first()[0]
)

before = spark.read.option("versionAsOf", baseline_version).table(DELTA_DEMO_FQ)
after = spark.read.option("versionAsOf", current_version).table(DELTA_DEMO_FQ)

display(
    spark.createDataFrame(
        [
            (
                "before schema evolution",
                baseline_version,
                before.count(),
                ", ".join(before.columns),
            ),
            (
                "after schema evolution",
                current_version,
                after.count(),
                ", ".join(after.columns),
            ),
        ],
        ["snapshot", "delta_version", "row_count", "columns"],
    )
)

display(
    spark.sql(f"DESCRIBE HISTORY {DELTA_DEMO_FQ}")
    .select("version", "timestamp", "operation", "operationParameters")
    .orderBy(F.desc("version"))
    .limit(5)
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Query the governed Metric View
# MAGIC
# MAGIC Before the workshop, the facilitator creates `hc_workshop.workshop_shared.fpd_metrics` by running `workshop-setup/section-01-facilitator-setup.sql`. This governed Metric View centralizes names, measures, formats, and the FPD5 formula for dashboards and Genie.

# COMMAND ----------
metric_view_sql = f"{SHARED_SCHEMA}.fpd_metrics"
metric_view_exists = (
    spark.sql(
        f"""
        SELECT COUNT(*) AS asset_count
        FROM {CATALOG}.information_schema.tables
        WHERE table_schema = 'workshop_shared'
          AND table_name = 'fpd_metrics'
        """
    )
    .first()
    .asset_count
    > 0
)

if metric_view_exists:
    metric_result = spark.sql(
        f"""
        SELECT
          promotion_cohort,
          MEASURE(eligible_contracts) AS eligible_contracts,
          MEASURE(fpd5_contracts) AS fpd5_contracts,
          MEASURE(fpd5_rate) AS fpd5_rate
        FROM {metric_view_sql}
        GROUP BY ALL
        ORDER BY fpd5_rate DESC
        """
    )
    display(metric_result)
    print("Shared Metric View query succeeded.")
else:
    print("Shared Metric View is not installed; showing the documented fallback result.")
    display(
        spark.table(FPD_VIEW)
        .groupBy("promotion_cohort")
        .agg(
            F.count("*").alias("eligible_contracts"),
            F.sum("fpd5_flag").alias("fpd5_contracts"),
            F.avg("fpd5_flag").alias("fpd5_rate"),
        )
        .orderBy(F.desc("fpd5_rate"))
    )

# COMMAND ----------
# MAGIC %md
# MAGIC ## Checkpoint
# MAGIC
# MAGIC Be ready to answer:
# MAGIC
# MAGIC - Why was notebook compute appropriate for the Python and SQL exploration?
# MAGIC - Why should the dashboard and Genie Agent use a SQL warehouse?
# MAGIC - What is the difference between a queued query and a query that spills to disk?
# MAGIC - Which FPD5 denominator did we use?
# MAGIC - What does the Delta transaction history let an operator inspect or recover?
# MAGIC - Which evidence would be needed before treating the hotspot as more than an investigation signal?
# MAGIC
# MAGIC Leave `hc_workshop.workshop_labs.unicorn_<team_id>_<runner_id>_delta_demo` in place for the handover review. The facilitator can remove team-prefixed lab assets after the workshop.

