# Databricks notebook source
# MAGIC %md
# MAGIC # Section 02 — Generative AI in Databricks
# MAGIC
# MAGIC In Section 01, you manually built and validated an FPD5 analysis. Now you will use **Genie Code** to understand, extend, repair, and improve inherited SQL and PySpark from governed workshop assets.
# MAGIC
# MAGIC **Goal:** get to a useful answer faster without giving up governed definitions, permissions, or human review.
# MAGIC
# MAGIC **Safety rules:** use read-only data operations, verify generated work, and do not redefine FPD5 in notebook code. If you complete the optional Genie Agent extension, edit only the private Agent you created in Section 01 and keep it unshared. Describe elevated FPD5 as an investigation signal—not proof of fraud. All records are synthetic.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Before you begin
# MAGIC
# MAGIC 1. In Databricks, choose **File > Clone** and save this notebook under your own user folder. Genie Code will add and edit cells, so do not work in the shared workshop copy.
# MAGIC 2. Attach **Serverless** notebook compute.
# MAGIC 3. Open **Genie Code** from the notebook's right sidebar.
# MAGIC 4. In the Genie Code settings, choose an approval mode that asks you before tool actions during this lab.
# MAGIC 5. For the optional extension only, confirm **Unicorn FPD5 Investigator — `<your_workspace_username>`** from Section 01 is still in your personal user folder and is not shared with other participants.
# MAGIC
# MAGIC If your workspace does not show Genie Code, tell the facilitator and use the paired fallback demonstration.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Understand inherited analysis faster
# MAGIC
# MAGIC Imagine that the cohort query below was handed to you by another analyst. Run it first, but do not study every line yet.
# MAGIC
# MAGIC It uses the governed `hc_workshop.workshop_shared.fpd_metrics` Metric View created in Section 01.

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
# MAGIC ### Ask Genie Code to explain it
# MAGIC
# MAGIC In the Genie Code chat:
# MAGIC
# MAGIC 1. Type `@` and attach `hc_workshop.workshop_shared.fpd_metrics`.
# MAGIC 2. Use **Add context > Cells** or `@cell` to attach the query and its output.
# MAGIC 3. Paste the prompt below.
# MAGIC
# MAGIC > Explain this query to an analyst inheriting it. Describe the result grain, the three governed measures, the denominator, what `GROUP BY ALL` does, and why multiplying the rate by 100 does not redefine the metric. Just explain it; do not edit or run code.
# MAGIC
# MAGIC Check the explanation against the query. This is the first productivity pattern: **use Genie Code to shorten the time needed to understand existing work**.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Generate and iterate with a targeted prompt
# MAGIC
# MAGIC A reusable prompt contains five parts: **goal, context, constraints, output, and validation**. Continue in the same Genie Code conversation:
# MAGIC
# MAGIC > Extend the inherited analysis for the 0% smartphone promotion by `region_code`. Use only the attached `fpd_metrics` Metric View and its governed measures. Include eligible contracts, FPD5 contracts, and FPD5 rate; keep only regions with at least 20 eligible contracts; sort by FPD5 rate; and add a readable bar chart. Compare the highest-rate qualifying region with the overall promotion rate. Keep the work read-only and describe hotspots only as investigation signals. First show me your plan. After I approve it, add and run the required cells in this notebook.
# MAGIC
# MAGIC Before approving, confirm that the plan:
# MAGIC
# MAGIC - uses only `hc_workshop.workshop_shared.fpd_metrics`;
# MAGIC - uses `MEASURE(eligible_contracts)`, `MEASURE(fpd5_contracts)`, and `MEASURE(fpd5_rate)`;
# MAGIC - applies the 20-contract rule at the regional grain;
# MAGIC - contains no write operation;
# MAGIC - does not invent a causal or fraud conclusion.
# MAGIC
# MAGIC Follow up with a specific correction if one item is wrong. This is the second productivity pattern: **generate a useful first version, then refine it conversationally instead of rewriting the whole prompt**.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Verify the generated change
# MAGIC
# MAGIC Run this independent reference query after Genie Code finishes. The regional comparison should use its promotion rate as the baseline.

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
# MAGIC **Expected checkpoint:** the promotion is approximately **42.26%** FPD5 and other eligible originations are approximately **21.03%**. On the standard dataset, `REGION_VI` is the highest-rate qualifying promotion region at approximately **53.95%**, or **11.69 percentage points** above the overall promotion rate.
# MAGIC
# MAGIC If the results differ, ask Genie Code to inspect its source, dimensions, measures, threshold, and denominator. This is the third productivity pattern: **pair fast generation with a short, independent correctness check**.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Diagnose and repair inherited PySpark
# MAGIC
# MAGIC The helper below was handed over as a validation utility. It runs without an exception, but it contains a semantic denominator bug. Run it and inspect the suspicious result.

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
# MAGIC Both cohorts incorrectly show a 100% FPD5 rate. Attach the function and output with `@cell`, then ask Genie Code:
# MAGIC
# MAGIC > Diagnose why this PySpark helper reports 100% FPD5 for every cohort. Preserve the full eligible population when calculating the denominator, use the existing `fpd5_flag` only as the numerator, and do not redefine FPD5. Keep the function read-only and DataFrame-based. Add lightweight assertions that check the result has two cohorts, FPD5 contracts never exceed eligible contracts, and the rates reconcile within 0.05 percentage points of 42.26% and 21.03%. Explain the bug and show the diff before editing or running the notebook.
# MAGIC
# MAGIC Review the proposed change. The repair must remove the pre-aggregation FPD5 filter; it must not recreate the FPD5 date logic. Approve the focused edit, rerun the helper and checks, and confirm that the results reconcile with the Metric View query above.
# MAGIC
# MAGIC This is the fourth productivity pattern: **use Genie Code to find a semantic bug in inherited Python, then protect the repair with executable checks**.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Improve and document existing work
# MAGIC
# MAGIC Select the regional analysis cell generated by Genie Code and use `/optimize`, or ask:
# MAGIC
# MAGIC > Review this query for semantic correctness and performance. Preserve the governed Metric View measures and exact output. Suggest only material improvements, explain each one, and make no change if the query is already appropriate.
# MAGIC
# MAGIC Review the diff. If you accept a change, rerun the query and confirm that the regional counts and rates are unchanged. An optimization suggestion is not proof of an improvement; material performance claims require Query Profile evidence.
# MAGIC
# MAGIC Then use `/doc` or ask Genie Code to add a concise comment explaining the query's grain, denominator, and threshold.
# MAGIC
# MAGIC This is the fifth productivity pattern: **use Genie Code to improve maintainability, but keep semantic and performance validation in the workflow**.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Optional extension — Iteratively improve the Section 01 Genie Agent
# MAGIC
# MAGIC Complete this extension only if the core notebook and dashboard flow are on time and your private Section 01 Agent is available.
# MAGIC
# MAGIC Open **Unicorn FPD5 Investigator — `<your_workspace_username>`**, the private Agent you created in Section 01. Confirm that:
# MAGIC
# MAGIC 1. it is in your user folder;
# MAGIC 2. it is not shared with **All account users**, the workshop group, or another participant;
# MAGIC 3. `hc_workshop.workshop_shared.fpd_metrics` is its only data source.
# MAGIC
# MAGIC Continue in this Agent. Do not create a clone or a second Agent.

# COMMAND ----------
# MAGIC %md
# MAGIC ### Establish the baseline
# MAGIC
# MAGIC Start a new conversation in your Agent and ask:
# MAGIC
# MAGIC > Which store-associate pairs in the 0% smartphone promotion should we investigate first? Include only pairs with at least 10 eligible contracts. Show the store, sales associate, eligible contracts, FPD5 contracts, and FPD5 rate.
# MAGIC
# MAGIC Inspect the generated SQL and answer. Record whether it:
# MAGIC
# MAGIC - queries `hc_workshop.workshop_shared.fpd_metrics`;
# MAGIC - uses the governed `MEASURE(...)` expressions;
# MAGIC - applies the 10-contract threshold before ranking;
# MAGIC - includes counts alongside the rate;
# MAGIC - states the `2026-09-01` observation date;
# MAGIC - describes the result as an investigation signal.

# COMMAND ----------
# MAGIC %md
# MAGIC ### Give Genie Code a new stakeholder requirement
# MAGIC
# MAGIC Open Genie Code from your Agent's response and ask:
# MAGIC
# MAGIC > Improve this Genie Agent for the risk team. Whenever it reports an FPD5 rate, require the response to include eligible and FPD5 contract counts, state that results are observed through 2026-09-01, and describe hotspots only as investigation signals. For store or store-associate rankings, require at least 10 eligible contracts. Review the current response and context, then propose the smallest instruction, metadata, or verified example-SQL changes needed. Reuse the `fpd_metrics` definitions and do not duplicate the FPD5 formula. Show each change before saving it.
# MAGIC
# MAGIC Review every proposed change. Reject broad, duplicated, or unrelated context. Accept only the smallest changes that implement the new requirement.

# COMMAND ----------
# MAGIC %md
# MAGIC ### Retest and check for regression
# MAGIC
# MAGIC 1. Start a fresh conversation in your Agent and rerun the store-associate question.
# MAGIC 2. Confirm the SQL and answer now meet the checklist.
# MAGIC 3. Rerun this previously correct question:
# MAGIC
# MAGIC > How does FPD5 for the 0% smartphone promotion compare with other eligible originations?
# MAGIC
# MAGIC 4. Confirm the answer still reconciles to approximately **42.26%** versus **21.03%**.
# MAGIC
# MAGIC This is the sixth productivity pattern: **turn stakeholder feedback into a small Agent-context change, then test the target behavior and a regression question**.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Checkpoint
# MAGIC
# MAGIC Be ready to explain:
# MAGIC
# MAGIC 1. How did Genie Code help you understand inherited work?
# MAGIC 2. Which prompt structure made the generated change easier to control?
# MAGIC 3. What PySpark denominator bug did Genie Code repair, and what checks protected the result?
# MAGIC 4. How did you verify that an improvement preserved the result?
# MAGIC 5. If you completed the optional extension, what changed in your private Genie Agent, and how did you prove the original behavior still worked?
# MAGIC 6. Where could you apply the same SQL or Python workflow next week?
# MAGIC
# MAGIC Genie Code reduces manual effort across the workflow; you still own the requested outcome, review, validation, and final change.
