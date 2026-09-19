# Databricks notebook source
# MAGIC %md
# MAGIC # Facilitator demo — Genie Code for governed FPD5 analysis
# MAGIC
# MAGIC **Purpose:** show how Genie Code reduces manual effort across inherited SQL and PySpark workflows and applies the same working pattern to dashboard authoring.
# MAGIC
# MAGIC Use a fresh clone of this notebook for every rehearsal or delivery. The live demo intentionally lets Genie Code add and edit cells.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Demo setup
# MAGIC
# MAGIC Before participants arrive:
# MAGIC
# MAGIC 1. Clone this notebook into your user folder and attach Serverless compute.
# MAGIC 2. Confirm Genie Code is visible and agentic actions are available.
# MAGIC 3. Set Genie Code to an approval mode that asks before tool actions.
# MAGIC 4. Add `hc_workshop.workshop_shared.fpd_metrics` as context with the `@` resource picker.
# MAGIC 5. Confirm the reference cohort query returns approximately **42.26%** for the promotion and **21.03%** for other eligible originations.
# MAGIC 6. Keep a second, already-completed clone ready as the fallback.
# MAGIC 7. Prepare the disposable dashboard draft. If time permits the optional Agent walkthrough, use the private **Unicorn FPD5 Investigator — `<your_workspace_username>`** that you created live in Section 01.
# MAGIC
# MAGIC Do not use a participant's notebook or the shared Git copy for the demonstration.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Understand inherited analysis faster
# MAGIC
# MAGIC Say:
# MAGIC
# MAGIC > Most analysts do not start from a blank page. They inherit notebooks, queries, and business definitions. We will use Genie Code throughout that workflow: understand, modify, diagnose, improve, and deliver.
# MAGIC
# MAGIC Run the inherited query below.

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
# MAGIC Attach this cell and its output with `@cell`, then ask:
# MAGIC
# MAGIC > Explain this query to an analyst inheriting it. Describe the grain, governed measures, denominator, and percentage conversion. Just explain it; do not edit or run code.
# MAGIC
# MAGIC Compare the explanation with the actual query. The point is faster understanding, not delegating accountability.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Generate and iterate with targeted prompts
# MAGIC
# MAGIC Introduce the reusable prompt structure: **goal, context, constraints, output, and validation**. Then paste:
# MAGIC
# MAGIC > Extend the inherited analysis for the 0% smartphone promotion by `region_code`. Use only the attached `fpd_metrics` Metric View and its governed measures. Include eligible contracts, FPD5 contracts, and FPD5 rate; keep only regions with at least 20 eligible contracts; sort by FPD5 rate; and add a readable bar chart. Compare the highest-rate qualifying region with the overall promotion rate. Keep the work read-only and describe hotspots only as investigation signals. First show me your plan. After I approve it, add and run the required cells in this notebook.
# MAGIC
# MAGIC Narrate the review before approving:
# MAGIC
# MAGIC - Is the requested source the governed Metric View?
# MAGIC - Are the actions read-only?
# MAGIC - Is the 20-contract threshold applied at the regional grain?
# MAGIC - Does the interpretation avoid causal and fraud claims?
# MAGIC
# MAGIC Let Genie Code add and execute the cells. If one detail is wrong, give a targeted follow-up instead of rewriting the full prompt. Show that generated output is normal notebook code its owner can inspect, rerun, version, and review.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Verify, diagnose, and improve existing code
# MAGIC
# MAGIC Run this independent reference query and compare its promotion rate with the generated regional result.

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
# MAGIC If the answers disagree, use a correction prompt rather than accepting a plausible explanation:
# MAGIC
# MAGIC > The generated regional comparison does not reconcile with the independent promotion rate. Inspect the source, dimensions, threshold, measures, and denominator. Explain the mismatch, then revise only the incorrect cells. Keep the analysis read-only.

# COMMAND ----------
# MAGIC %md
# MAGIC ### Diagnose and repair inherited PySpark
# MAGIC
# MAGIC The next helper runs, but it contains a semantic denominator bug. Run it and ask participants what looks suspicious.

# COMMAND ----------
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


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


cohort_validation = build_cohort_validation(
    "hc_workshop.workshop_shared.fpd_analysis"
)
display(cohort_validation)

# COMMAND ----------
# MAGIC %md
# MAGIC Attach the helper and output with `@cell`, then ask:
# MAGIC
# MAGIC > Diagnose why this PySpark helper reports 100% FPD5 for every cohort. Preserve the full eligible population when calculating the denominator, use the existing `fpd5_flag` only as the numerator, and do not redefine FPD5. Keep the function read-only and DataFrame-based. Add lightweight assertions that check the result has two cohorts, FPD5 contracts never exceed eligible contracts, and the rates reconcile within 0.05 percentage points of 42.26% and 21.03%. Explain the bug and show the diff before editing or running the notebook.
# MAGIC
# MAGIC The focused repair removes the pre-aggregation filter while preserving the governed `fpd5_flag`. Review the diff, allow the edit, rerun the function and checks, and reconcile the result with the Metric View query.

# COMMAND ----------
# MAGIC %md
# MAGIC ### Explain and optimize with judgment
# MAGIC
# MAGIC Select the generated regional query and try:
# MAGIC
# MAGIC > Explain the grain, denominator, minimum-volume filter, and ordering in plain language for the analyst who will own this after handover.
# MAGIC
# MAGIC Then ask:
# MAGIC
# MAGIC > Review this query for semantic correctness and performance. Preserve the governed Metric View measures and exact output. Suggest only material improvements, explain the evidence for each one, and make no change if the query is already appropriate.
# MAGIC
# MAGIC Emphasize that an AI suggestion is not performance evidence. Material changes still require result comparison and, for expensive queries, Query Profile validation.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Build a simple AI/BI Dashboard
# MAGIC
# MAGIC Open a new, facilitator-owned draft dashboard named **Genie Code Demo — FPD5 Overview**. In the dashboard canvas, give Genie Code this prompt:
# MAGIC
# MAGIC > Build a one-page FPD5 overview using only `@hc_workshop.workshop_shared.fpd_metrics`. Add three KPI counters for eligible contracts, FPD5 contracts, and FPD5 rate; a bar chart comparing promotion cohorts; a ranked bar chart of the five promotion stores with the highest FPD5 rate among stores with at least 10 eligible contracts; and a promotion-cohort filter. Reuse the Metric View measures, use clear titles and percentage formatting, and show me the plan before editing the dashboard. Do not publish it.
# MAGIC
# MAGIC Review the proposed datasets, widgets, filters, and layout before allowing changes. Then inspect the draft:
# MAGIC
# MAGIC - Do the KPI values reconcile with the notebook?
# MAGIC - Is the minimum-volume rule applied before ranking stores?
# MAGIC - Does the filter affect the intended widgets?
# MAGIC - Are rate values formatted as percentages?
# MAGIC
# MAGIC Emphasize that Genie Code can create datasets, visualizations, filters, and layout, but the author still owns validation and publication. Leave the dashboard unpublished and delete the disposable draft after the workshop.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Optional extension — Iteratively improve the Section 01 Genie Agent
# MAGIC
# MAGIC Run this extension only if the required notebook and dashboard checkpoints are complete.
# MAGIC
# MAGIC Open **Unicorn FPD5 Investigator — `<your_workspace_username>`**, the private Agent you created in Section 01. Do not create another Agent or clone.
# MAGIC
# MAGIC Ask the baseline question:
# MAGIC
# MAGIC > Which store-associate pairs in the 0% smartphone promotion should we investigate first? Include only pairs with at least 10 eligible contracts. Show the store, sales associate, eligible contracts, FPD5 contracts, and FPD5 rate.
# MAGIC
# MAGIC Inspect the SQL and response. Then open Genie Code from the response and ask:
# MAGIC
# MAGIC > Improve this Genie Agent for the risk team. Whenever it reports an FPD5 rate, require the response to include eligible and FPD5 contract counts, state that results are observed through 2026-09-01, and describe hotspots only as investigation signals. For store or store-associate rankings, require at least 10 eligible contracts. Review the current response and context, then propose the smallest instruction, metadata, or verified example-SQL changes needed. Reuse the `fpd_metrics` definitions and do not duplicate the FPD5 formula. Show each change before saving it.
# MAGIC
# MAGIC Review and accept only focused changes. Start a fresh conversation, rerun the target question, and then rerun the cohort-comparison question as a regression check.
# MAGIC
# MAGIC Keep the Agent private. The productivity story is: **inspect → change with Genie Code → retest → regression check**.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Closing checkpoint
# MAGIC
# MAGIC Ask participants:
# MAGIC
# MAGIC 1. Where did Genie Code remove manual effort from the workflow?
# MAGIC 2. What did you still inspect or validate?
# MAGIC 3. Which workflow—understanding code, generating analysis, repairing Python, optimization, dashboarding, or optionally iterating on a Genie Agent—would you use first?
# MAGIC
# MAGIC Close with:
# MAGIC
# MAGIC > Genie Code is most productive when it stays inside the workflow: give it relevant context, request a concrete outcome, review its actions, and validate the result.
