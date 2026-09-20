# Facilitator talking points — Data Analysis in Databricks

**Participant notebook:** [`01-lab.py`](../../../workshop-content/01-data-analysis-in-databricks/01-lab.py)
**Scheduled:** 9:45 AM–11:15 AM · 90 minutes

## Delivery map

| Time | Minutes | Mode | Surface and focus |
|---|---:|---|---|
| 9:45–9:50 | 5 | Slides | Business question, promotion, FPD5, eligibility, and investigation boundary |
| 9:50–9:57 | 7 | Slides | Notebook compute, Jobs compute, and SQL warehouse distinctions |
| 9:57–10:15 | 18 | Notebook | Verify sources; explore application mix and campaign timing |
| 10:15–10:27 | 12 | Notebook | Build the eligible FPD5 population and compare cohorts |
| 10:27–10:39 | 12 | Notebook exercise | Change analytical grouping and write the handover note |
| 10:39–10:49 | 10 | Notebook | Persist the result and inspect Delta history |
| 10:49–10:56 | 7 | Facilitator demo | Metric View and prepared AI/BI Dashboard |
| 10:56–11:06 | 10 | Guided participant activity | Create and validate each participant's private Genie Agent |
| 11:06–11:11 | 5 | Facilitator demo | SQL Query History and Query Profile |
| 11:11–11:15 | 4 | Notebook and discussion | Ownership, operational risk, validation, and recovery |

## 1. Business question and FPD5

- Nova Mobile subsidizes selected smartphone loans so customers pay 0% monthly interest; customers still repay principal.
- The question is whether the promotion cohort has higher FPD5 and where the signal is concentrated.
- A contract is eligible only after its first installment reaches day five past due by `2026-09-01`.
- It is FPD5 when the first installment remains unsettled at that point or was settled on or after day five.
- Compare both counts and rates. A high rate is an investigation signal, not proof of fraud or causality.

## 2. Notebook exploration and compute

- Databricks notebooks combine Markdown, Python, PySpark, and SQL in one workflow.
- In this lab, Python, PySpark, `spark.sql(...)`, and `%sql` all run on the notebook's attached Serverless compute.
- `%sql` changes the notebook cell language; it does not move that cell to a SQL warehouse.
- Databricks provides the `spark` session. Participants do not create `SparkContext` or `SparkSession`.
- A SQL warehouse runs the dashboard and Genie Agent queries. Those statements appear in SQL Query History.
- For scheduled Python or notebook work, use Jobs compute rather than keeping interactive notebook compute running.

## 3. Establish the business context

- Start with `loan_application` to understand channels, product mix, stores, and campaign timing.
- Application volume shows demand and concentration; it does not show repayment behavior.
- The busiest 20% of stores handle about 81% of applications. That is not automatically an FPD5 hotspot.

## 4. Build the eligible FPD5 population

- Move from applications to contracts and first installments.
- The denominator is eligible contracts, not every application, approval, or only defaulted contracts.
- Compare the promotion cohort with other eligible originations before changing the analytical grain.
- Reference result: approximately **42.26%** for the promotion versus **21.03%** for other eligible originations.

## 5. Investigate concentration

- Rank segments by FPD5 rate while retaining eligible and FPD5 contract counts.
- Require at least 10 eligible contracts for store or store-associate rankings.
- Participants change the grouping dimension and record the evidence, denominator, caveat, and follow-up question.

## 6. Persist the handover in Delta

- Save the participant's result only after it has a clear handover purpose.
- The participant-specific table avoids collisions in the shared lab schema.
- Delta history shows the original write and the later schema change that adds `review_note`.
- Time travel depends on retained files; it is useful for diagnosis but is not a backup.

## 7. Reuse governed metrics

- `fpd_analysis` contains one row per eligible contract.
- `fpd_metrics` centralizes the shared FPD5 measures and dimensions.
- The notebook, dashboard, and Genie Agent reuse the same Metric View instead of rebuilding the formula.
- Reconciliation means checking that each surface returns the same governed result.

## 8. Dashboard and Genie Agent

- **Dashboard:** distinguish editable draft from published snapshot; viewers use **Individual data permissions** in this workshop.
- **Genie Agent:** it is private to the participant and uses only `fpd_metrics`.
- Inspect generated SQL before trusting the written answer: source, `MEASURE(...)`, denominator, filters, date, and caveat must be correct.

## 9. Operate the SQL workload

- Use Query History to locate dashboard- or Genie-generated SQL warehouse statements.
- In Query Profile, distinguish waiting time, execution time, result fetching, scanned data, pruning, and spill.
- Queueing suggests a concurrency or workload-isolation question; spill suggests reviewing data volume, joins, aggregations, and warehouse sizing.

## Closing question

For each asset created or used, ask: who owns it, how is it validated, where is it monitored, and what is the recovery action?
