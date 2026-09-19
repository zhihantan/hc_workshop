# Databricks notebook source
# MAGIC %md
# MAGIC # Section 02 — Generative AI in Databricks
# MAGIC
# MAGIC ## Your assignment
# MAGIC
# MAGIC You are a developer supporting Unicorn Finance's risk analytics team after the Atlas Ridge Consulting handover. The team trusts the governed FPD5 baseline from Section 01, but now needs to identify regional investigation signals and make the inherited validation code safe for another developer to maintain.
# MAGIC
# MAGIC By the end of this section, deliver one validated personal notebook that:
# MAGIC
# MAGIC 1. explains the inherited governed analysis;
# MAGIC 2. identifies qualifying promotion regions that warrant investigation;
# MAGIC 3. repairs a PySpark denominator bug and protects the repair with executable checks; and
# MAGIC 4. documents the grain, denominator, threshold, and validation evidence for handover.
# MAGIC
# MAGIC The notebook evidence will then be used to review a facilitator-built dashboard draft. If time allows, you will apply the same controlled-change workflow to the private Genie Agent you created in Section 01.
# MAGIC
# MAGIC All records are synthetic. Elevated FPD5 is an investigation signal—not proof of fraud, misconduct, or causality.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Definition refresh before you calculate
# MAGIC
# MAGIC **FPD5** means **First Payment Default at five days past due**. A contract is FPD5 when its first scheduled installment is still unsettled five days after its due date or was settled on or after that fifth day.
# MAGIC
# MAGIC A contract enters the eligible population only when its complete five-day observation window has passed:
# MAGIC
# MAGIC ```text
# MAGIC first installment due date + 5 days <= 2026-09-01
# MAGIC ```
# MAGIC
# MAGIC For example, an installment due on August 20 and settled on August 25 is eligible and FPD5. An installment due on August 30 is not yet observable on September 1 and must not enter either the numerator or denominator.
# MAGIC
# MAGIC The denominator is therefore **eligible contracts**, not applications, approvals, all originations, or only contracts that defaulted. Use the governed `fpd_metrics` measures for analysis and the one-row-per-eligible-contract `fpd_analysis` view only for the validation helper. Do not recreate the date or eligibility logic in this notebook.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Prepare your controlled working copy
# MAGIC
# MAGIC 1. In Databricks, choose **File > Clone** and save this notebook under your own user folder. Genie Code will add and edit cells, so do not work in the shared workshop copy.
# MAGIC 2. Attach **Serverless** notebook compute.
# MAGIC 3. Open **Genie Code** from the notebook's right sidebar.
# MAGIC 4. In the Genie Code settings, choose an approval mode that asks you before tool actions during this lab.
# MAGIC 5. For the optional extension only, confirm **Unicorn FPD5 Investigator — `<your_workspace_username>`** from Section 01 is still in your personal user folder and is not shared with other participants.
# MAGIC
# MAGIC Stop and ask for assistance if you cannot create a personal clone, attach the assigned notebook compute, or open Genie Code. Do not continue in the shared notebook.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Establish what the inherited analysis already proves
# MAGIC
# MAGIC Before changing the investigation, establish what the handed-over query already proves. Run it to recover the governed promotion baseline that every later result must reconcile with.
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
# MAGIC Check the explanation against the query. Record one point Genie Code made faster to understand and one point you verified directly from the SQL.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Find where the promotion signal is concentrated
# MAGIC
# MAGIC The promotion baseline is elevated, but a broad cohort rate does not tell Risk where to investigate. Extend the analysis to regional grain while keeping counts beside the rate so a small denominator cannot look more important than it is.
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
# MAGIC The 20-contract threshold is a workshop stability rule for this regional comparison. It is not part of the FPD5 definition and does not establish statistical significance. Follow up with a specific correction if one plan item is wrong.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Reconcile the regional evidence before using it
# MAGIC
# MAGIC Generated code is a draft until its population, grain, denominator, and result are checked. Run this governed checkpoint after Genie Code finishes and compare every qualifying region with the generated result.

# COMMAND ----------
# MAGIC %sql
# MAGIC WITH promotion_baseline AS (
# MAGIC   SELECT MEASURE(fpd5_rate) * 100 AS promotion_rate_pct
# MAGIC   FROM hc_workshop.workshop_shared.fpd_metrics
# MAGIC   WHERE promotion_cohort = '0% smartphone promotion'
# MAGIC ),
# MAGIC qualifying_regions AS (
# MAGIC   SELECT
# MAGIC     region_code,
# MAGIC     MEASURE(eligible_contracts) AS eligible_contracts,
# MAGIC     MEASURE(fpd5_contracts) AS fpd5_contracts,
# MAGIC     MEASURE(fpd5_rate) * 100 AS fpd5_rate_pct
# MAGIC   FROM hc_workshop.workshop_shared.fpd_metrics
# MAGIC   WHERE promotion_cohort = '0% smartphone promotion'
# MAGIC   GROUP BY ALL
# MAGIC   HAVING MEASURE(eligible_contracts) >= 20
# MAGIC )
# MAGIC SELECT
# MAGIC   region_code,
# MAGIC   eligible_contracts,
# MAGIC   fpd5_contracts,
# MAGIC   ROUND(fpd5_rate_pct, 2) AS fpd5_rate_pct,
# MAGIC   ROUND(fpd5_rate_pct - promotion_rate_pct, 2) AS percentage_points_vs_promotion
# MAGIC FROM qualifying_regions
# MAGIC CROSS JOIN promotion_baseline
# MAGIC ORDER BY fpd5_rate_pct DESC

# COMMAND ----------
# MAGIC %md
# MAGIC After running the checkpoint, you should find six qualifying regions. `REGION_VI` should be highest at approximately **53.95%**, which is **11.69 percentage points** above the promotion baseline of **42.26%**.
# MAGIC
# MAGIC If the generated and governed results differ, do not continue. Ask Genie Code to inspect its source, promotion filter, dimensions, measures, threshold, and denominator. Then rerun both results.
# MAGIC
# MAGIC **Interpretation prompt:** Which region should Risk investigate first, how many eligible and FPD5 contracts support that signal, and what additional evidence would be needed before drawing a conclusion?

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Repair the validation utility before handover
# MAGIC
# MAGIC The regional result now has governed reference evidence. The inherited PySpark helper below is supposed to provide a second validation path, but it contains a semantic denominator bug. First define the handed-over function without changing it.

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
# MAGIC %md
# MAGIC Run the inherited helper. Ask yourself whether a 100% rate for both cohorts is plausible before asking Genie Code to diagnose it.

# COMMAND ----------
cohort_validation = build_cohort_validation(
    "hc_workshop.workshop_shared.fpd_analysis"
)
display(cohort_validation)

# COMMAND ----------
# MAGIC %md
# MAGIC Both cohorts incorrectly show a 100% FPD5 rate. Attach the function and output with `@cell`, then ask Genie Code:
# MAGIC
# MAGIC > Diagnose why this PySpark helper reports 100% FPD5 for every cohort. Preserve the full eligible population when calculating the denominator, use the existing `fpd5_flag` only as the numerator, and do not redefine FPD5. Keep the function read-only and DataFrame-based. Add lightweight assertions that check the result has two cohorts, eligible counts are positive, and FPD5 contracts never exceed eligible contracts. Also compare the repaired rates with a read-only query of the governed `fpd_metrics` measures and assert that they agree within 0.05 percentage points. Explain the bug and show the diff before editing or running the notebook.
# MAGIC
# MAGIC Review the proposed change. The repair must remove the pre-aggregation FPD5 filter; it must not recreate the FPD5 date logic. Approve the focused edit, rerun the helper and checks, and confirm that the results reconcile with the Metric View query above.
# MAGIC
# MAGIC **Interpretation prompt:** Why can code that runs successfully still be unsafe to hand over, and which assertion would catch this exact denominator regression?

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Prepare the regional analysis for its next owner
# MAGIC
# MAGIC Select the regional analysis cell generated by Genie Code and use `/optimize`, or ask:
# MAGIC
# MAGIC > Review this query for semantic correctness and performance. Preserve the governed Metric View measures and exact output. Suggest only material improvements, explain each one, and make no change if the query is already appropriate.
# MAGIC
# MAGIC Review the diff. If you accept a change, rerun the query and confirm that the regional counts and rates are unchanged. An optimization suggestion is not proof of an improvement; material performance claims require Query Profile evidence.
# MAGIC
# MAGIC Then use `/doc` or ask Genie Code to add a concise comment explaining the query's grain, denominator, and threshold.
# MAGIC
# MAGIC Before continuing, confirm that the notebook now contains the regional evidence, the governed reconciliation, the repaired helper, passing checks, and a concise explanation of the grain, denominator, and threshold.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Watch the evidence become a dashboard draft
# MAGIC
# MAGIC The facilitator will now use Genie Code to build **Genie Code Demo — FPD5 Overview**, a disposable unpublished dashboard. This is separate from the prepared **Unicorn FPD5 Overview** used in Section 01.
# MAGIC
# MAGIC The business reason for this step is to show how validated notebook evidence can become a consumable delivery asset without moving the FPD5 definition out of the Metric View.
# MAGIC
# MAGIC As you watch, record:
# MAGIC
# MAGIC 1. whether the dashboard uses only `fpd_metrics`;
# MAGIC 2. whether its cohort values reconcile with this notebook;
# MAGIC 3. whether the store ranking retains counts and the 10-contract minimum;
# MAGIC 4. whether the promotion filter affects the intended widgets; and
# MAGIC 5. which checks and publication decisions still belong to the dashboard author.
# MAGIC
# MAGIC The facilitator leaves this draft unpublished. Dashboard queries run on a SQL warehouse; they do not run on this notebook's Serverless compute.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Optional extension — Apply a stakeholder requirement to your private Genie Agent
# MAGIC
# MAGIC Complete this extension only when instructed and when your private Section 01 Agent is available. The Agent uses a Pro or Serverless SQL warehouse, not this notebook's compute.
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
# MAGIC The store and associate minimum of 10 eligible contracts is the existing Agent ranking rule. It is distinct from the 20-contract regional exercise threshold and does not change the governed metric.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Before finishing
# MAGIC
# MAGIC Make sure you can explain:
# MAGIC
# MAGIC 1. which contracts are eligible for FPD5 and why the denominator matters;
# MAGIC 2. which regional signal should be investigated first, with its counts, rate, and caveat;
# MAGIC 3. why the inherited PySpark helper returned 100% and which check prevents that regression;
# MAGIC 4. which work ran on notebook compute and which dashboard or Agent work used a SQL warehouse; and
# MAGIC 5. which generated change you approved, rejected, or corrected and why.
# MAGIC
# MAGIC Record:
# MAGIC
# MAGIC - one owner for the validated notebook;
# MAGIC - one risk if its governed source or observation date changes;
# MAGIC - one recovery action if a future result fails reconciliation; and
# MAGIC - one SQL or Python workflow where you will apply this pattern next week, including the validation you will retain.
# MAGIC
# MAGIC Genie Code reduced manual effort, but you still own the requested outcome, review, evidence, validation, and final change.
