# Databricks notebook source
# MAGIC %md
# MAGIC # Section 01 — Check first-payment problems
# MAGIC
# MAGIC ## The business story
# MAGIC
# MAGIC Unicorn Finance offers loans to customers.
# MAGIC
# MAGIC Nova Mobile ran a promotion for selected smartphones:
# MAGIC
# MAGIC 1. A customer chose a phone at a participating store.
# MAGIC 2. The customer applied for a Unicorn Finance loan at the store. This is a **point-of-sale (POS) installment loan**.
# MAGIC 3. If the loan was approved, the customer was scheduled to repay the amount borrowed over 6, 9, or 12 monthly payments.
# MAGIC 4. The customer paid 0% monthly interest.
# MAGIC
# MAGIC Nova Mobile made a payment to Unicorn Finance to support the 0% offer. This payment is called a **subsidy**.
# MAGIC
# MAGIC The phone was not free. The customer still had to repay the amount borrowed. A processing fee or down payment could still apply. Approval was not guaranteed.
# MAGIC
# MAGIC The promotion is named `ZERO_SMARTPHONE_2026` in the data.
# MAGIC
# MAGIC After the promotion started, Unicorn Finance saw more loan applications. The company also saw more problems with first payments in some stores.
# MAGIC
# MAGIC ## Your task
# MAGIC
# MAGIC Answer three questions:
# MAGIC
# MAGIC 1. Were promotion loans more likely to have a late first payment?
# MAGIC 2. Were the problems spread across many locations, or focused in a few places?
# MAGIC 3. What should the next analyst know?
# MAGIC
# MAGIC All workshop data is made up. A high rate is a reason to investigate. It is not proof of fraud or wrongdoing.

# COMMAND ----------
# MAGIC %md
# MAGIC ## What FPD5 means
# MAGIC
# MAGIC **FPD5** stands for **First Payment Default at five days past due**.
# MAGIC
# MAGIC An **installment** is one scheduled monthly payment.
# MAGIC
# MAGIC In this workshop, a loan is counted as FPD5 when its first installment was not fully paid before day five. A payment on day five counts as FPD5.
# MAGIC
# MAGIC Here, **default** only describes the first payment at day five. It does not mean that the full loan was never repaid.
# MAGIC
# MAGIC We can check a loan on day five after its first payment was due. We call these loans **eligible loans**.
# MAGIC
# MAGIC We check the data as it looked on `2026-09-01`. A loan is eligible when:
# MAGIC
# MAGIC ```text
# MAGIC first installment due date + 5 days <= 2026-09-01
# MAGIC ```
# MAGIC
# MAGIC Examples:
# MAGIC
# MAGIC | What happened? | Can we check it yet? | FPD5? |
# MAGIC |---|---:|---:|
# MAGIC | Due August 20, fully paid August 23 | Yes | No |
# MAGIC | Due August 20, fully paid August 25 | Yes | Yes |
# MAGIC | Due August 20, still not fully paid | Yes | Yes |
# MAGIC | Due August 30 | No | Too soon to know |
# MAGIC
# MAGIC To calculate the FPD5 rate, we divide:
# MAGIC
# MAGIC ```text
# MAGIC loans with FPD5 / eligible loans
# MAGIC ```
# MAGIC
# MAGIC The total number of eligible loans is the **denominator**. We do not use all applications or all approved loans.

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
# MAGIC ## 1. Check the data we received
# MAGIC
# MAGIC The notebook needs eight tables. It also expects the data to be current through `2026-09-01`.
# MAGIC
# MAGIC Run the next cell. It will stop if a table is missing or the date is wrong.

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
# MAGIC ## 2. Where did customers apply?
# MAGIC
# MAGIC Before checking late payments, first look at the loan applications.
# MAGIC
# MAGIC We want to know:
# MAGIC
# MAGIC - Where did customers apply: a store, the mobile app, the website, or the call center?
# MAGIC - How many applications were approved, declined, or cancelled?
# MAGIC - Which applications used the smartphone promotion?
# MAGIC
# MAGIC **PySpark** is Python used to work with Spark data.
# MAGIC
# MAGIC The next cell labels the promotion applications, groups the applications, and counts them.

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
    )
    .orderBy("promotion_cohort", F.desc("applications"))
)

display(application_summary)

# COMMAND ----------
# MAGIC %md
# MAGIC **Look at the result:** Where do you see promotion applications? How many were approved?
# MAGIC
# MAGIC This table only describes applications. It does not tell us whether customers made their first payment.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Did applications increase during the promotion?
# MAGIC
# MAGIC Unicorn Finance saw more applications during the promotion period. The next query checks the monthly numbers.
# MAGIC
# MAGIC It shows **when** applications increased. It does not prove that the promotion caused the increase.
# MAGIC
# MAGIC The query uses SQL to count applications for each month.
# MAGIC
# MAGIC Create a chart with:
# MAGIC
# MAGIC - `application_month` on the horizontal axis;
# MAGIC - `applications` on the vertical axis; and
# MAGIC - `promotion_cohort` as the color.
# MAGIC
# MAGIC `promotion_cohort` means **promotion group**.
# MAGIC
# MAGIC Look for the month when promotion applications appear.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   DATE_TRUNC('MONTH', a.submitted_at) AS application_month,
# MAGIC   CASE
# MAGIC     WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026'
# MAGIC     THEN '0% smartphone promotion'
# MAGIC     ELSE 'Other applications'
# MAGIC   END AS promotion_cohort,
# MAGIC   COUNT(*) AS applications,
# MAGIC   SUM(CASE WHEN a.decision_code = 'APPROVED' THEN 1 ELSE 0 END) AS approved_applications
# MAGIC FROM hc_workshop.core_lending.loan_application AS a
# MAGIC GROUP BY ALL
# MAGIC ORDER BY application_month, promotion_cohort, applications DESC

# COMMAND ----------
# MAGIC %md
# MAGIC **Why do this first?** More applications can lead to more late payments simply because there are more loans.
# MAGIC
# MAGIC We therefore need to compare both:
# MAGIC
# MAGIC - the number of loans with a late first payment; and
# MAGIC - the percentage of eligible loans with a late first payment.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Which loans can we check for FPD5?
# MAGIC
# MAGIC An application is not yet a loan. Only an approved application can become a loan contract with scheduled payments.
# MAGIC
# MAGIC To check FPD5, we need loans that:
# MAGIC
# MAGIC - have a payment schedule in the `installment` table;
# MAGIC - have a first installment; and
# MAGIC - reached day five after the first-payment due date by `2026-09-01`.
# MAGIC
# MAGIC The next cell creates that list. It also marks each loan as FPD5 or not FPD5.

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
# MAGIC We now have the first-payment result. Next, add details about the loan, product, store, and salesperson.
# MAGIC
# MAGIC Each loan must appear exactly once. If a loan appears twice, the counts and rates will be wrong.

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
    raise RuntimeError("The FPD5 data has more than one row for a loan contract")

print(f"Created session temporary view: {FPD_VIEW}")
print(f"Eligible loans: {fpd_contracts.count():,}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Was FPD5 higher for the promotion?
# MAGIC
# MAGIC We now have the loans that are old enough to check. Start with the main business question.
# MAGIC
# MAGIC ### 5.1 Compare promotion loans with other loans
# MAGIC
# MAGIC The next query creates two groups:
# MAGIC
# MAGIC - loans from the 0% smartphone promotion; and
# MAGIC - all other eligible loans.
# MAGIC
# MAGIC For each group, it shows:
# MAGIC
# MAGIC - the total number of eligible loans;
# MAGIC - the number with FPD5; and
# MAGIC - the FPD5 percentage.
# MAGIC
# MAGIC The result calls the second group **Other eligible originations**. Here, an origination means a loan that was created.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   promotion_cohort,
# MAGIC   COUNT(*) AS eligible_contracts,
# MAGIC   SUM(fpd5_flag) AS fpd5_contracts,
# MAGIC   ROUND(AVG(fpd5_flag) * 100, 2) AS fpd5_rate_pct
# MAGIC FROM fpd_contracts
# MAGIC GROUP BY promotion_cohort
# MAGIC ORDER BY fpd5_rate_pct DESC

# COMMAND ----------
# MAGIC %md
# MAGIC Look at both the number and the percentage.
# MAGIC
# MAGIC A higher percentage tells us that the promotion needs more investigation. It does not tell us why the percentage is higher.

# COMMAND ----------
# MAGIC %md
# MAGIC ### 5.2 Are a few stores handling most applications?
# MAGIC
# MAGIC A busy store may have more late payments simply because it handles more applications.
# MAGIC
# MAGIC The next query uses all applications linked to a store. It checks how many come from the busiest 20% of stores.
# MAGIC
# MAGIC This is background information only. It does **not** identify promotion or FPD5 problem areas.

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
# MAGIC ### 5.3 Which stores and salespeople need a closer look?
# MAGIC
# MAGIC Among promotion loans, compare the FPD5 rate for each store and salesperson combination.
# MAGIC
# MAGIC The query only shows groups with at least 10 eligible loans. This reduces the chance that a very small group looks important by accident.

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
# MAGIC ### 5.4 Try it: group the loans in a different way
# MAGIC
# MAGIC **Timebox: 12 minutes**
# MAGIC
# MAGIC `ANALYSIS_DIMENSION` controls how the promotion loans are grouped.
# MAGIC
# MAGIC 1. Change it from `region_code` to `store_province` or `merchant_name`.
# MAGIC 2. Run the cell again.
# MAGIC 3. Compare the result with the store-and-salesperson result above.
# MAGIC
# MAGIC If you choose `region_code` or `store_province`, ask whether the problem covers a large area.
# MAGIC
# MAGIC If you choose `merchant_name`, ask whether the problem is focused on one retail partner.
# MAGIC
# MAGIC Always check the number of eligible loans as well as the percentage.

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
    HAVING COUNT(*) >= 10
    ORDER BY fpd5_rate_pct DESC, eligible_contracts DESC, segment
    """
)

display(participant_breakdown)

# COMMAND ----------
# MAGIC %md
# MAGIC Write down:
# MAGIC
# MAGIC 1. how you grouped the loans;
# MAGIC 2. the group with the highest FPD5 percentage;
# MAGIC 3. its number of eligible loans, number of FPD5 loans, and FPD5 percentage;
# MAGIC 4. whether the problem looks broad or focused; and
# MAGIC 5. one question you would ask next.
# MAGIC
# MAGIC Example follow-up questions:
# MAGIC
# MAGIC - Who is responsible for the FPD5 definition?
# MAGIC - How do we check that first-payment dates are correct?
# MAGIC - Did the promotion rules or store sales process change?
# MAGIC
# MAGIC Use this structure for your summary:
# MAGIC
# MAGIC > **Promotion:** ___ of ___ eligible loans were FPD5 (___%).
# MAGIC >
# MAGIC > **Other eligible loans:** The FPD5 rate was ___%.
# MAGIC >
# MAGIC > **My grouping:** When I grouped promotion loans by `<grouping>`, `<group>` had ___ FPD5 loans out of ___ eligible loans (___%).
# MAGIC >
# MAGIC > This result needs more investigation. It is not proof of fraud.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Save your work for the next analyst
# MAGIC
# MAGIC The temporary view will disappear when the notebook session ends.
# MAGIC
# MAGIC Save your result as a Delta table so another analyst can open it later.
# MAGIC
# MAGIC We will:
# MAGIC
# MAGIC
# MAGIC 1. create a table with a name that is unique to you;
# MAGIC 2. save your grouped result;
# MAGIC 3. add a follow-up note; and
# MAGIC 4. compare the table before and after the note was added.

# COMMAND ----------
# MAGIC %md
# MAGIC ### 6.1 Create your table name
# MAGIC
# MAGIC Every participant needs a different table name.
# MAGIC
# MAGIC The next cell uses your workspace login and adds a short code. This prevents participants from overwriting each other's tables.

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

print(f"Your saved table: {INVESTIGATION_FQ}")

# COMMAND ----------
# MAGIC %md
# MAGIC ### 6.2 Save your grouped result
# MAGIC
# MAGIC Save the result as a Delta table.
# MAGIC
# MAGIC If you run the full notebook again, this step replaces only your own table.

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
# MAGIC ### 6.3 View the first saved version
# MAGIC
# MAGIC Delta keeps a history of changes to a table. Each saved change gets a version number.
# MAGIC
# MAGIC Record the current version before changing the table.

# COMMAND ----------
baseline_version = int(
    spark.sql(f"DESCRIBE HISTORY {INVESTIGATION_FQ}")
    .agg(F.max("version"))
    .first()[0]
)

print(f"First saved Delta version: {baseline_version}")
display(
    spark.sql(f"DESCRIBE HISTORY {INVESTIGATION_FQ}")
    .select("version", "timestamp", "operation", "operationParameters")
    .orderBy(F.desc("version"))
)

# COMMAND ----------
# MAGIC %md
# MAGIC ### 6.4 Add a note for the next analyst
# MAGIC
# MAGIC Add a column that tells the next analyst what to check before drawing a conclusion.

# COMMAND ----------
if "review_note" not in spark.table(INVESTIGATION_FQ).columns:
    spark.sql(
        f"""
        ALTER TABLE {INVESTIGATION_FQ}
        ADD COLUMNS (review_note STRING COMMENT 'Follow-up action for this group')
        """
    )

spark.sql(
    f"""
    UPDATE {INVESTIGATION_FQ}
    SET review_note = 'Check customer mix, promotion rules, and the store sales process'
    """
)

display(spark.table(INVESTIGATION_FQ))

# COMMAND ----------
# MAGIC %md
# MAGIC ### 6.5 Compare the table before and after
# MAGIC
# MAGIC Read the old version and the current version. Check that the only new field is `review_note`.
# MAGIC
# MAGIC Delta can read an old version only while the required files still exist.
# MAGIC
# MAGIC Old versions help us check changes. They are not a backup.

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
                "before review note",
                baseline_version,
                before.count(),
                ", ".join(before.columns),
            ),
            (
                "after review note",
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
# MAGIC ## 7. Check the shared FPD5 calculation
# MAGIC
# MAGIC We calculated FPD5 in the notebook so you could see how it works.
# MAGIC
# MAGIC Unicorn Finance also stores the approved FPD5 calculation in a **Metric View**. A Metric View keeps a shared business calculation in one place.
# MAGIC
# MAGIC The dashboard and Genie Agent use this Metric View. They should not create their own versions of the FPD5 formula.
# MAGIC
# MAGIC Run the next cell. Check that the Metric View gives the same promotion rates as the notebook.

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
        "The shared Metric View hc_workshop.workshop_shared.fpd_metrics "
        "is not available. Stop here and ask for help. Do not create a "
        "different FPD5 formula in your own table or Agent."
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
# MAGIC - **21.03%** for the other eligible loans.
# MAGIC
# MAGIC If your result is very different, check:
# MAGIC
# MAGIC - the date is `2026-09-01`;
# MAGIC - you used only the first installment;
# MAGIC - a payment on day five counts as FPD5; and
# MAGIC - you divided by eligible loans, not all applications.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 8. Check the dashboard
# MAGIC
# MAGIC Open the **Unicorn FPD5 Overview** dashboard. It uses the same `fpd_metrics` Metric View.
# MAGIC
# MAGIC Check these items:
# MAGIC
# MAGIC 1. The summary numbers match the notebook.
# MAGIC 2. The promotion filter changes the charts.
# MAGIC 3. Each rate is shown with the number of eligible loans.
# MAGIC 4. The published dashboard is the version that viewers see. It may differ from an unpublished draft.
# MAGIC 5. The workshop participant group can view it, but **All account users** cannot.
# MAGIC
# MAGIC The goal is simple: the notebook and dashboard must give the same business answer.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 9. Create your private Genie Agent
# MAGIC
# MAGIC **Timebox: 10 minutes**
# MAGIC
# MAGIC A Genie Agent lets you ask questions about data in everyday language.
# MAGIC
# MAGIC Create an Agent that uses the shared FPD5 Metric View:
# MAGIC
# MAGIC 1. Open **Genie Agents** from the sidebar and select **New**.
# MAGIC 2. Add only `hc_workshop.workshop_shared.fpd_metrics` as the data source. Do not add the raw lending tables.
# MAGIC 3. Name the Agent **Unicorn FPD5 Investigator — `<your_workspace_username>`**. Replace the placeholder with the login name shown in your workspace.
# MAGIC 4. Select the SQL warehouse shown for this workshop. If you are unsure which one to use, stop and ask for help.
# MAGIC 5. Set the description to:
# MAGIC
# MAGIC    > Answers questions about first-payment problems in the synthetic Unicorn Finance data.
# MAGIC    > Uses only the `fpd_metrics` Metric View.
# MAGIC    > Shows the number of eligible loans and the FPD5 rate.
# MAGIC    > Describes high rates as reasons to investigate, not proof of fraud.
# MAGIC
# MAGIC 6. Add these common questions:
# MAGIC    - How does the promotion's FPD5 rate compare with the other eligible loans?
# MAGIC    - Which promotion stores have the highest FPD5 rate and at least 10 eligible loans?
# MAGIC    - Which store and salesperson combinations have the highest FPD5 rate and at least 10 eligible loans?
# MAGIC 7. Do not add more instructions yet. You will improve this same Agent in Section 02.
# MAGIC 8. In the Workspace browser, confirm that the Agent is in your user folder.
# MAGIC 9. Open **Share**.
# MAGIC    - Confirm that the Agent is not shared with **All account users**.
# MAGIC    - Confirm that it is not shared with the workshop group or another participant.
# MAGIC    - Workspace administrators may still have access.
# MAGIC 10. Ask:
# MAGIC
# MAGIC     > As of 2026-09-01, how does the promotion's FPD5 rate compare with the other eligible loans?
# MAGIC
# MAGIC 11. Open the SQL created by the Agent. Check that it uses `fpd_metrics`.
# MAGIC 12. Keep this Agent conversation. Do not delete it. You will return to the same answer and SQL in Section 02.

# COMMAND ----------
# MAGIC %md
# MAGIC Your Agent is ready when:
# MAGIC
# MAGIC - `fpd_metrics` is its only data source;
# MAGIC - it uses the workshop SQL warehouse;
# MAGIC - no other participant can open it;
# MAGIC - its SQL uses `MEASURE(...)`;
# MAGIC - its answer is close to 42.26% and 21.03%; and
# MAGIC - its answer includes the date and does not claim fraud.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 10. Check the SQL query
# MAGIC
# MAGIC The notebook ran its code on notebook compute. The dashboard and Genie Agent ran their SQL on the workshop SQL warehouse.
# MAGIC
# MAGIC **Query History** shows the SQL that ran on the warehouse. **Query Profile** shows where a query spent its time.
# MAGIC
# MAGIC 1. Open **Query History** and filter to the workshop SQL warehouse.
# MAGIC 2. Find one query created by the dashboard or Genie Agent.
# MAGIC 3. Open its **Query Profile**.
# MAGIC 4. Check how long the query waited, ran, and returned its result.
# MAGIC 5. Check which step took the longest and how much data it read.
# MAGIC
# MAGIC Words you may see:
# MAGIC
# MAGIC - **Queued:** The query waited because the warehouse was already busy.
# MAGIC - **Spill:** The query needed more memory and temporarily used disk.
# MAGIC - **Fetching:** The query finished, but the client was still receiving the result.
# MAGIC
# MAGIC More warehouse clusters help run more queries at the same time. A larger warehouse gives one query more resources.
# MAGIC
# MAGIC Your query may have no queueing or spill. That is a good result.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 11. What should you understand?
# MAGIC
# MAGIC Before finishing, check that you can answer these questions:
# MAGIC
# MAGIC - What does FPD5 mean?
# MAGIC - Why can we not check very recent first payments?
# MAGIC - What total did we use to calculate the FPD5 rate?
# MAGIC - Was the high rate spread across many places or focused in a smaller group?
# MAGIC - Why is a high rate not proof of fraud?
# MAGIC - What can the Delta table history show?
# MAGIC - Why do the dashboard and Genie Agent use the shared Metric View?
# MAGIC - What is the difference between a queued query and a query that spilled to disk?
# MAGIC
# MAGIC Choose one item: the notebook, Delta table, Metric View, dashboard, SQL warehouse, or Genie Agent.
# MAGIC
# MAGIC Write down:
# MAGIC
# MAGIC 1. who should own it;
# MAGIC 2. one thing that could go wrong; and
# MAGIC 3. how you would check or fix it.
