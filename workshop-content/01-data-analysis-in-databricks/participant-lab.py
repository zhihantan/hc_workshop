# Databricks notebook source
# MAGIC %md
# MAGIC # Section 01 — Investigate first-payment default
# MAGIC
# MAGIC ## Your assignment
# MAGIC
# MAGIC Atlas Ridge Consulting has handed Unicorn Finance an inherited analytical platform. Risk and operations have noticed that a 0% smartphone promotion produced more originations and may also have a higher rate of early payment problems.
# MAGIC
# MAGIC Your job is to produce a defensible answer to three questions:
# MAGIC
# MAGIC 1. Is first-payment default higher for the promotion than for all other eligible originations?
# MAGIC 2. Is the signal broad, or concentrated in particular locations or sales channels?
# MAGIC 3. What evidence, governed assets, and operating information should the next owner receive?
# MAGIC
# MAGIC All records are synthetic. An elevated rate identifies contracts that need investigation; it does not prove fraud, misconduct, or causality.

# COMMAND ----------
# MAGIC %md
# MAGIC ## What FPD5 means
# MAGIC
# MAGIC **FPD5** means **First Payment Default at five days past due**.
# MAGIC
# MAGIC In this workshop, a contract is counted as FPD5 when its first scheduled installment:
# MAGIC
# MAGIC - is still unsettled five days after its due date; or
# MAGIC - was settled on or after that fifth day.
# MAGIC
# MAGIC A contract is **eligible** for the analysis only after the complete five-day observation window has passed. With an observation date of `2026-09-01`, the rule is:
# MAGIC
# MAGIC ```text
# MAGIC first installment due date + 5 days <= 2026-09-01
# MAGIC ```
# MAGIC
# MAGIC Examples:
# MAGIC
# MAGIC | First installment outcome | Eligible? | FPD5? |
# MAGIC |---|---:|---:|
# MAGIC | Due August 20, settled August 23 | Yes | No |
# MAGIC | Due August 20, settled August 25 | Yes | Yes |
# MAGIC | Due August 20, still unsettled | Yes | Yes |
# MAGIC | Due August 30 | No | Not yet observable |
# MAGIC
# MAGIC The denominator is therefore **eligible contracts**, not all applications, all approvals, or all originated contracts.

# COMMAND ----------
import hashlib
import re
from datetime import date

from pyspark.sql import functions as F

CATALOG = "hc_workshop"
AS_OF_DATE = date(2026, 9, 1)

CORE_SCHEMA = f"{CATALOG}.core_lending"
LABS_SCHEMA = f"{CATALOG}.workshop_labs"
SHARED_SCHEMA = f"{CATALOG}.workshop_shared"
ELIGIBLE_INSTALLMENT_VIEW = "eligible_first_installments"
FPD_VIEW = "fpd_contracts"

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Verify the inherited sources
# MAGIC
# MAGIC Before answering the business question, confirm that the handover contains the expected lending lifecycle and that the source uses the agreed observation date. An analysis built on missing or differently dated data is not comparable with the governed result.

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
# MAGIC ## 2. Understand how applications entered the business
# MAGIC
# MAGIC Before examining repayment outcomes, establish the origination context. We want to know which channels carried the promotion, how decisions were distributed, and whether the promotion represents a materially different application population.
# MAGIC
# MAGIC PySpark is useful here because an analyst can interactively derive a cohort label and profile several fields in one DataFrame workflow.

# COMMAND ----------
applications = spark.table(f"{CORE_SCHEMA}.loan_application")

application_summary = (
    applications.withColumn(
        "promotion_cohort",
        F.when(
            F.col("promotion_code") == "ZERO_SMARTPHONE_2026",
            F.lit("0% smartphone promotion"),
        ).otherwise(F.lit("Other applications")),
    )
    .groupBy("promotion_cohort", "application_channel_code", "decision_code")
    .agg(
        F.count("*").alias("applications"),
        F.round(F.sum("requested_amount"), 2).alias("requested_amount_php"),
        F.round(F.avg("underwriting_score"), 2).alias("average_underwriting_score"),
    )
    .orderBy("promotion_cohort", F.desc("applications"))
)

display(application_summary)

# COMMAND ----------
# MAGIC %md
# MAGIC **Interpret the result:** Which application channels contain the promotion? Do not infer repayment behavior yet—an application profile describes demand and underwriting decisions, not whether an originated contract made its first payment.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Determine when promotion volume appeared
# MAGIC
# MAGIC Risk reported that promotion volume increased. Test that premise before investigating payment outcomes.
# MAGIC
# MAGIC SQL makes the monthly aggregation easy to inspect and reuse in a visualization. Plot `application_month` on the x-axis and `applications` on the y-axis, colored by `promotion_cohort`. The result should show when the promotion entered the origination mix.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   DATE_TRUNC('MONTH', a.submitted_at) AS application_month,
# MAGIC   CASE
# MAGIC     WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026'
# MAGIC     THEN '0% smartphone promotion'
# MAGIC     ELSE 'Other applications'
# MAGIC   END AS promotion_cohort,
# MAGIC   p.product_name,
# MAGIC   COUNT(*) AS applications,
# MAGIC   SUM(CASE WHEN a.decision_code = 'APPROVED' THEN 1 ELSE 0 END) AS approved_applications
# MAGIC FROM hc_workshop.core_lending.loan_application AS a
# MAGIC JOIN hc_workshop.core_lending.loan_product AS p
# MAGIC   ON a.product_id = p.product_id
# MAGIC GROUP BY ALL
# MAGIC ORDER BY application_month, promotion_cohort, applications DESC

# COMMAND ----------
# MAGIC %md
# MAGIC **Why this matters:** Higher application volume can produce more problem contracts even when the underlying rate is unchanged. The next steps therefore compare both counts and rates using a fair, observable denominator.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Build the eligible FPD5 population
# MAGIC
# MAGIC Risk has asked which originated contracts crossed the workshop's first-payment-default threshold and therefore need further attention.
# MAGIC
# MAGIC We cannot answer that from applications alone:
# MAGIC
# MAGIC - only originated contracts have repayment schedules;
# MAGIC - the `installment` table contains the fixed-term schedules used by this analysis;
# MAGIC - only installment number `1` is relevant to **first** payment default;
# MAGIC - recent first installments must be excluded until all five observation days have passed.
# MAGIC
# MAGIC First, isolate the observable first installments and assign the FPD5 flag.

# COMMAND ----------
eligible_first_installments = spark.sql(
    f"""
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
    """
)

eligible_first_installments.createOrReplaceTempView(ELIGIBLE_INSTALLMENT_VIEW)

display(
    eligible_first_installments.agg(
        F.count("*").alias("eligible_first_installments"),
        F.sum("fpd5_flag").alias("fpd5_first_installments"),
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC Next, connect each eligible first installment to its contract, application, product, and retail context. The output grain must be exactly one row per eligible contract so that every contract contributes once to the denominator.

# COMMAND ----------
fpd_contracts = spark.sql(
    f"""
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
    JOIN {ELIGIBLE_INSTALLMENT_VIEW} AS f
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
# MAGIC ## 5. Test whether the signal is elevated and concentrated
# MAGIC
# MAGIC We now have a fair population. Work through the questions in order rather than jumping directly to a list of high-rate stores.
# MAGIC
# MAGIC ### 5.1 Is FPD5 higher for the promotion?
# MAGIC
# MAGIC Compare the promotion with all other eligible originations. The denominator in each row is the number of contracts that had reached the five-day observation point.

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
# MAGIC %md
# MAGIC Record both the count and the rate. A higher rate supports further investigation, but this comparison alone does not explain why the difference exists.

# COMMAND ----------
# MAGIC %md
# MAGIC ### 5.2 Could raw store volume create a misleading hotspot?
# MAGIC
# MAGIC High-volume stores naturally produce more applications and potentially more FPD5 contracts. Measure how concentrated application volume is before interpreting a hotspot.
# MAGIC
# MAGIC This result is **origination-volume context**. It is not an FPD5 concentration measure and must not be presented as one.

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
# MAGIC %md
# MAGIC ### 5.3 Which store and associate combinations need review?
# MAGIC
# MAGIC Rank promotion cohorts by **rate**, while retaining the eligible and FPD5 counts. The minimum of 10 eligible contracts avoids prioritizing a segment based on a tiny denominator.

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
# MAGIC ### 5.4 Your investigation: change the analytical grain
# MAGIC
# MAGIC **Timebox: 12 minutes**
# MAGIC
# MAGIC A hotspot can appear broad at one grain and localized at another. Change `ANALYSIS_DIMENSION` to `store_province` or `merchant_name`, rerun the cell, and compare the result with the store-associate ranking.

# COMMAND ----------
ANALYSIS_DIMENSION = "region_code"
ALLOWED_DIMENSIONS = {
    "region_code",
    "store_province",
    "merchant_name",
}

if ANALYSIS_DIMENSION not in ALLOWED_DIMENSIONS:
    raise ValueError(
        f"Choose one of these dimensions: {sorted(ALLOWED_DIMENSIONS)}"
    )

participant_breakdown = spark.sql(
    f"""
    SELECT
      '{ANALYSIS_DIMENSION}' AS analysis_dimension,
      {ANALYSIS_DIMENSION} AS segment,
      COUNT(*) AS eligible_contracts,
      SUM(fpd5_flag) AS fpd5_contracts,
      ROUND(AVG(fpd5_flag) * 100, 2) AS fpd5_rate_pct
    FROM {FPD_VIEW}
    WHERE promotion_code = 'ZERO_SMARTPHONE_2026'
    GROUP BY {ANALYSIS_DIMENSION}
    ORDER BY fpd5_rate_pct DESC, eligible_contracts DESC, segment
    """
)

display(participant_breakdown)

# COMMAND ----------
# MAGIC %md
# MAGIC Record:
# MAGIC
# MAGIC 1. the dimension you selected;
# MAGIC 2. its highest-rate segment;
# MAGIC 3. the segment's eligible-contract count, FPD5 count, and FPD5 rate;
# MAGIC 4. whether this looks broader or more localized than the store-associate result; and
# MAGIC 5. one operational question that would reduce uncertainty—for example, who owns the FPD5 definition or which control validates settlement dates.
# MAGIC
# MAGIC Use this handover structure:
# MAGIC
# MAGIC > Among contracts whose first installment had reached the five-day observation point by 2026-09-01, the 0% smartphone promotion had an FPD5 rate of ___% versus ___% for other eligible originations. At the `<dimension>` grain, `<segment>` had ___ FPD5 contracts from ___ eligible contracts (___%); this is a synthetic investigation signal that requires customer-mix, campaign, control, and operational evidence before any conclusion.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Preserve the investigation for handover
# MAGIC
# MAGIC The temporary view disappears with the notebook session. Unicorn Finance needs a durable result that another owner can find, inspect, and recover.
# MAGIC
# MAGIC We will:
# MAGIC
# MAGIC 1. create a participant-specific Delta table from your selected breakdown;
# MAGIC 2. inspect its baseline version;
# MAGIC 3. add an operational review note; and
# MAGIC 4. compare the two retained versions.

# COMMAND ----------
# MAGIC %md
# MAGIC ### 6.1 Choose a collision-resistant table name
# MAGIC
# MAGIC Derive the table name from your full workspace identity so that participants do not overwrite one another's investigation.

# COMMAND ----------
current_user = spark.sql("SELECT current_user()").first()[0]
runner_base = (
    re.sub(r"[^a-z0-9_]", "_", current_user.split("@")[0].lower()).strip("_")
    or "user"
)
if not runner_base[0].isalpha():
    runner_base = f"u_{runner_base}"

RUNNER_ID = (
    f"{runner_base[:12]}_"
    f"{hashlib.sha256(current_user.encode()).hexdigest()[:6]}"
)

INVESTIGATION_TABLE = f"unicorn_{RUNNER_ID}_fpd_investigation"
INVESTIGATION_FQ = f"{LABS_SCHEMA}.{INVESTIGATION_TABLE}"

print(f"Participant investigation table: {INVESTIGATION_FQ}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### 6.2 Persist your selected breakdown
# MAGIC
# MAGIC Write the result as a Delta table. `overwriteSchema` makes a complete notebook rerun reproducible for your participant-specific table.

# COMMAND ----------
(
    participant_breakdown.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(INVESTIGATION_FQ)
)

display(spark.table(INVESTIGATION_FQ))

# COMMAND ----------
# MAGIC %md
# MAGIC ### 6.3 Capture and inspect the baseline
# MAGIC
# MAGIC Each committed Delta change receives a transaction-log version. Capture the current version before changing the table.

# COMMAND ----------
baseline_version = int(
    spark.sql(f"DESCRIBE HISTORY {INVESTIGATION_FQ}")
    .agg(F.max("version"))
    .first()[0]
)

print(f"Baseline Delta version: {baseline_version}")
display(
    spark.sql(f"DESCRIBE HISTORY {INVESTIGATION_FQ}")
    .select("version", "timestamp", "operation", "operationParameters")
    .orderBy(F.desc("version"))
)

# COMMAND ----------
# MAGIC %md
# MAGIC ### 6.4 Add the operational follow-up
# MAGIC
# MAGIC The analytical result tells the next owner where to look. Add a review column that records what should be validated before anyone treats the signal as a conclusion.

# COMMAND ----------
if "review_note" not in spark.table(INVESTIGATION_FQ).columns:
    spark.sql(
        f"""
        ALTER TABLE {INVESTIGATION_FQ}
        ADD COLUMNS (review_note STRING COMMENT 'Operational follow-up for this segment')
        """
    )

spark.sql(
    f"""
    UPDATE {INVESTIGATION_FQ}
    SET review_note = 'Validate customer mix, campaign design, and origination controls'
    """
)

display(spark.table(INVESTIGATION_FQ))

# COMMAND ----------
# MAGIC %md
# MAGIC ### 6.5 Compare the retained versions
# MAGIC
# MAGIC Read the baseline and current versions to verify what changed. Time travel works only while the transaction log and referenced data files are retained; it is not a substitute for a backup or recovery strategy.

# COMMAND ----------
current_version = int(
    spark.sql(f"DESCRIBE HISTORY {INVESTIGATION_FQ}")
    .agg(F.max("version"))
    .first()[0]
)

before = spark.read.option("versionAsOf", baseline_version).table(INVESTIGATION_FQ)
after = spark.read.option("versionAsOf", current_version).table(INVESTIGATION_FQ)

display(
    spark.createDataFrame(
        [
            (
                "before operational note",
                baseline_version,
                before.count(),
                ", ".join(before.columns),
            ),
            (
                "after operational note",
                current_version,
                after.count(),
                ", ".join(after.columns),
            ),
        ],
        ["snapshot", "delta_version", "row_count", "columns"],
    )
)

display(
    spark.sql(f"DESCRIBE HISTORY {INVESTIGATION_FQ}")
    .select("version", "timestamp", "operation", "operationParameters")
    .orderBy(F.desc("version"))
    .limit(5)
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Reconcile the governed Metric View
# MAGIC
# MAGIC The notebook made the FPD5 logic visible so that you could inspect it. Dashboards and Genie Agents should not each recreate that formula independently.
# MAGIC
# MAGIC `hc_workshop.workshop_shared.fpd_metrics` centralizes the fields, measures, display formats, and FPD5 definition. Query it and confirm that its promotion comparison reconciles with the notebook result.

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

if not metric_view_exists:
    raise RuntimeError(
        "The required Metric View hc_workshop.workshop_shared.fpd_metrics "
        "is unavailable. Stop here and ask workshop support; do not recreate "
        "the governed FPD5 definition in a personal table or Agent."
    )

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

# COMMAND ----------
# MAGIC %md
# MAGIC The standard workshop dataset should show approximately:
# MAGIC
# MAGIC - **42.26%** for the 0% smartphone promotion;
# MAGIC - **21.03%** for other eligible originations.
# MAGIC
# MAGIC If your earlier result differs materially, recheck the observation date, installment number, inclusive day-five boundary, and eligible-contract denominator before continuing.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 8. Trace the same metric into the dashboard
# MAGIC
# MAGIC The **Unicorn FPD5 Overview** dashboard is another consumer of `fpd_metrics`. As you open it, verify:
# MAGIC
# MAGIC 1. the KPIs reconcile with the Metric View query;
# MAGIC 2. the promotion filter updates the intended visualizations;
# MAGIC 3. rates retain visible denominators;
# MAGIC 4. the published dashboard is a snapshot distinct from its editable draft; and
# MAGIC 5. the selected data-permission mode matches the intended audience.
# MAGIC
# MAGIC The purpose is not merely to display charts. It is to confirm that the governed definition survives when the analysis moves from a notebook into a reusable business asset.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 9. Create your private Genie Agent
# MAGIC
# MAGIC **Timebox: 10 minutes**
# MAGIC
# MAGIC Create a focused natural-language interface to the same governed metric:
# MAGIC
# MAGIC 1. Open **Genie Agents** from the sidebar and select **New**.
# MAGIC 2. Add only `hc_workshop.workshop_shared.fpd_metrics` as the data source. Do not add raw `core_lending` tables or recreate the FPD5 formula.
# MAGIC 3. Name the Agent **Unicorn FPD5 Investigator — `<your_workspace_username>`**.
# MAGIC 4. Select the workshop SQL warehouse.
# MAGIC 5. Set the description to:
# MAGIC
# MAGIC    > Answers governed questions about eligible fixed-term contracts and FPD5 for the synthetic Unicorn Finance workshop. It compares promotion, product, channel, store, region, and sales-associate cohorts through the `fpd_metrics` Metric View and must describe hotspots as investigation signals rather than confirmed fraud.
# MAGIC
# MAGIC 6. Add these common questions:
# MAGIC    - How does FPD5 for the 0% smartphone promotion compare with other eligible originations?
# MAGIC    - Which promotion stores have the highest FPD5 rate, with at least 10 eligible contracts?
# MAGIC    - Which promotion store-associate pairs have the highest FPD5 rate, with at least 10 eligible contracts?
# MAGIC 7. Do not tune the Agent context yet. Section 02 will improve this same baseline Agent.
# MAGIC 8. In the Workspace browser, confirm that the Agent is in your user folder.
# MAGIC 9. Open **Share** and confirm that it is not shared with **All account users**, the workshop participant group, or another participant. Inherited workspace-administrator access is expected.
# MAGIC 10. Ask:
# MAGIC
# MAGIC     > As of 2026-09-01, how does FPD5 for the 0% smartphone promotion compare with other eligible originations?
# MAGIC
# MAGIC 11. Inspect the generated SQL before accepting the prose answer.
# MAGIC 12. Save the baseline response and generated SQL for Section 02.

# COMMAND ----------
# MAGIC %md
# MAGIC Your Agent is ready when:
# MAGIC
# MAGIC - `fpd_metrics` is its only data source;
# MAGIC - it uses the workshop SQL warehouse;
# MAGIC - it remains unshared with other participants;
# MAGIC - the generated SQL invokes governed measures with `MEASURE(...)`;
# MAGIC - the result reconciles to approximately 42.26% and 21.03%; and
# MAGIC - the response names the observation date and does not claim confirmed fraud.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 10. Inspect the SQL workload you created
# MAGIC
# MAGIC The notebook's Python and SQL cells ran on its attached notebook compute. The dashboard and Genie Agent use the workshop SQL warehouse, even though all three surfaces can consume the same governed Metric View.
# MAGIC
# MAGIC Operating the solution means inspecting the warehouse workload rather than assuming a successful dashboard or Agent answer was efficient.
# MAGIC
# MAGIC 1. Open **Query History** and filter to the workshop SQL warehouse.
# MAGIC 2. Locate one dashboard- or Genie-generated statement from this session that queries the Metric View.
# MAGIC 3. Open its **Query Profile**.
# MAGIC 4. Compare time spent waiting, executing, and fetching results.
# MAGIC 5. Check the longest operators, rows and bytes processed, pruning, and any spill insight.
# MAGIC
# MAGIC Interpret symptoms carefully:
# MAGIC
# MAGIC - sustained queueing usually indicates concurrency or capacity pressure;
# MAGIC - disk spill means an individual query exceeded available memory;
# MAGIC - long result fetching can indicate a slow or abandoned client;
# MAGIC - adding clusters helps concurrency, while increasing warehouse size primarily gives an individual query more resources.
# MAGIC
# MAGIC If your query has no queueing or spill, that is a healthy observation—not a missing result.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 11. Investigation checkpoint
# MAGIC
# MAGIC Before finishing, make sure you can explain:
# MAGIC
# MAGIC - what FPD5 stands for and why recent first installments are excluded;
# MAGIC - which denominator you used and why;
# MAGIC - whether the promotion signal is broad or concentrated in your selected dimension;
# MAGIC - why the result requires investigation rather than a fraud conclusion;
# MAGIC - what the Delta transaction history lets the next owner inspect;
# MAGIC - why the dashboard and Genie Agent use the governed Metric View and a SQL warehouse; and
# MAGIC - how you would distinguish a queued query from one that spilled to disk.
# MAGIC
# MAGIC Choose one asset—the notebook, Delta table, Metric View, dashboard, SQL warehouse, or Genie Agent—and write down:
# MAGIC
# MAGIC 1. its owner;
# MAGIC 2. one operational risk; and
# MAGIC 3. one recovery or validation action.
