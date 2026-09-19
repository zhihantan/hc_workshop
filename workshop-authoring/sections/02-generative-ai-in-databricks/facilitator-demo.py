# Databricks notebook source
# MAGIC %md
# MAGIC # Facilitator demo — Genie Code for governed FPD5 analysis
# MAGIC
# MAGIC **Facilitator-only.** Use a personal clone for rehearsal and delivery. Participants work only from their own clone of `workshop-content/02-generative-ai-in-databricks/participant-lab.py`.
# MAGIC
# MAGIC The demonstration follows one business handover: understand the inherited baseline, extend the risk investigation by region, repair its validation utility, and turn validated evidence into an unpublished dashboard draft.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Before participants arrive
# MAGIC
# MAGIC 1. Attach Serverless notebook compute and confirm Genie Code Agent mode is available.
# MAGIC 2. Add `hc_workshop.workshop_shared.fpd_metrics` with the `@` resource picker.
# MAGIC 3. Confirm the governed baseline is approximately 42.26% versus 21.03%.
# MAGIC 4. Keep a completed notebook clone and completed unpublished dashboard draft available as facilitator fallbacks.
# MAGIC 5. If using the optional extension, prepare only your own private Section 01 Agent.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Establish the inherited baseline
# MAGIC
# MAGIC Explain that Risk needs a regional investigation and a maintainable validation utility. The governed definition is unchanged: eligible contracts have reached the complete five-day observation window through `2026-09-01`.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   promotion_cohort,
# MAGIC   MEASURE(eligible_contracts) AS eligible_contracts,
# MAGIC   MEASURE(fpd5_contracts) AS fpd5_contracts,
# MAGIC   ROUND(MEASURE(fpd5_rate) * 100, 2) AS fpd5_rate_pct
# MAGIC FROM hc_workshop.workshop_shared.fpd_metrics
# MAGIC GROUP BY ALL
# MAGIC ORDER BY fpd5_rate_pct DESC

# COMMAND ----------
# MAGIC %md
# MAGIC Attach the query and output with `@cell` and ask:
# MAGIC
# MAGIC > Explain this inherited query to its next developer. Describe its grain, governed measures, eligible-contract denominator, `GROUP BY ALL`, and percentage conversion. Do not edit or run code.
# MAGIC
# MAGIC Check the explanation against the SQL before proceeding.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Extend the business investigation
# MAGIC
# MAGIC > Extend the inherited analysis for the 0% smartphone promotion by `region_code`. Use only the attached `fpd_metrics` Metric View and its governed measures. Include eligible contracts, FPD5 contracts, and FPD5 rate; keep only regions with at least 20 eligible contracts; sort by FPD5 rate; and add a readable bar chart. Compare the highest-rate qualifying region with the overall promotion rate. Keep the work read-only and describe hotspots only as investigation signals. First show me your plan. After I approve it, add and run the required cells in this notebook.
# MAGIC
# MAGIC Narrate the review: governed source, promotion-only population, regional grain, 20-contract `HAVING`, no writes, and no causal conclusion.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Repair the inherited validation utility

# COMMAND ----------
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

# COMMAND ----------
def build_cohort_validation(source_fqdn: str) -> DataFrame:
    """Summarize eligible and FPD5 contracts by promotion cohort."""
    eligible_contracts = spark.table(source_fqdn).filter(F.col("fpd5_flag") == 1)

    return (
        eligible_contracts.groupBy("promotion_cohort")
        .agg(
            F.countDistinct("contract_id").alias("eligible_contracts"),
            F.sum("fpd5_flag").alias("fpd5_contracts"),
        )
        .withColumn(
            "fpd5_rate_pct",
            F.round(
                F.col("fpd5_contracts") / F.col("eligible_contracts") * 100,
                2,
            ),
        )
        .orderBy(F.desc("fpd5_rate_pct"))
    )

# COMMAND ----------
cohort_validation = build_cohort_validation(
    "hc_workshop.workshop_shared.fpd_analysis"
)
display(cohort_validation)

# COMMAND ----------
# MAGIC %md
# MAGIC Attach the helper and output, then ask:
# MAGIC
# MAGIC > Diagnose why this PySpark helper reports 100% FPD5 for every cohort. Preserve the full eligible population when calculating the denominator, use the existing `fpd5_flag` only as the numerator, and do not redefine FPD5. Keep the function read-only and DataFrame-based. Add checks for two cohorts, positive eligible counts, and FPD5 counts not exceeding eligible counts. Compare the repaired rates with a read-only query of the governed `fpd_metrics` measures and assert agreement within 0.05 percentage points. Explain the bug and show the diff before editing or running.
# MAGIC
# MAGIC Review the diff. The repair removes the pre-aggregation filter and does not recreate date logic.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Review optimization and handover documentation
# MAGIC
# MAGIC Apply `/optimize` to the generated regional SQL. Accept a change only when it has a material rationale and preserves the reconciled result. Performance claims require Query Profile evidence.
# MAGIC
# MAGIC Apply `/doc` to add a concise explanation of regional grain, eligible-contract denominator, and 20-contract threshold.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Build the disposable dashboard draft
# MAGIC
# MAGIC Open a facilitator-owned dashboard named **Genie Code Demo — FPD5 Overview** and ask Genie Code:
# MAGIC
# MAGIC > Build a one-page FPD5 overview using only `@hc_workshop.workshop_shared.fpd_metrics`. Add three KPI counters for eligible contracts, FPD5 contracts, and FPD5 rate; a bar chart comparing promotion cohorts; a ranked bar chart of the five promotion stores with the highest FPD5 rate among stores with at least 10 eligible contracts; and a promotion-cohort filter. Reuse the Metric View measures, use clear titles and percentage formatting, and show me the plan before editing the dashboard. Do not publish it.
# MAGIC
# MAGIC Reconcile KPI values, threshold behavior, filter scope, and percentage formatting. Explain that the dashboard uses its SQL warehouse rather than notebook compute. Leave the draft unpublished and delete it after delivery.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Optional private-Agent maintenance
# MAGIC
# MAGIC In your own private **Unicorn FPD5 Investigator — `<workspace_username>`**, run the store-associate ranking question, ask Genie Code for the smallest context change that adds counts, observation date, investigation language, and the 10-contract threshold, then retest in a fresh conversation. Finish by rerunning the original cohort-comparison question.
