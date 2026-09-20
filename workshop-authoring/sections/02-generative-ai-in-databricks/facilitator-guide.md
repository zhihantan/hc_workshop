# Facilitator talking points — Generative AI in Databricks

**Participant notebook:** [`02-lab.py`](../../../workshop-content/02-generative-ai-in-databricks/02-lab.py)
**Scheduled:** 11:15 AM–12:15 PM · 60 minutes

## Delivery map

| Time | Minutes | Mode | Surface and focus |
|---|---:|---|---|
| 11:15–11:20 | 5 | Slides | Genie Code's role and the developer's validation responsibility |
| 11:20–11:27 | 7 | Notebook | Use Genie Code to explain the inherited governed SQL |
| 11:27–11:39 | 12 | Notebook exercise | Extend the promotion analysis to regional grain |
| 11:39–11:44 | 5 | Notebook | Run the independent governed regional checkpoint |
| 11:44–11:54 | 10 | Notebook exercise | Diagnose and repair the PySpark denominator bug |
| 11:54–11:59 | 5 | Notebook | Review `/optimize` and `/doc` proposals |
| 11:59–12:08 | 9 | Facilitator demo | Build and validate the unpublished AI/BI Dashboard draft |
| 12:08–12:12 | 4 | Optional guided activity | Improve the participant's private Genie Agent, or use as buffer |
| 12:12–12:15 | 3 | Notebook and discussion | Owner, risk, recovery, and practical next use |

## 1. What Genie Code contributes

- Genie Code helps a developer understand, extend, debug, document, and optimize inherited notebook work.
- It can propose edits and execution, but the participant reviews the plan, diff, source, and result before approval.
- The developer remains responsible for the population, denominator, business meaning, permissions, and validation.

## 2. Understand inherited SQL before changing it

- The starting query uses the governed `fpd_metrics` Metric View.
- One row represents one promotion cohort.
- `MEASURE(...)` invokes governed measures; `GROUP BY ALL` groups by the selected dimensions.
- Multiplication by 100 changes display units, not the underlying metric definition.
- Ask Genie Code to explain the query first rather than immediately rewriting it.

## 3. Extend the investigation to region

- Keep `fpd_metrics` as the only source and filter to the promotion cohort.
- Group by `region_code`; retain eligible contracts, FPD5 contracts, and FPD5 rate.
- Apply the 20-eligible-contract rule at regional grain.
- The threshold stabilizes this workshop comparison; it is not part of FPD5 or a statistical-significance claim.

## 4. Validate generated analysis

- Generated code is a draft until an independent query produces the same rows, counts, and rates.
- The governed checkpoint should return six qualifying regions.
- `REGION_VI` is approximately **53.95%**, or **11.69 percentage points** above the **42.26%** promotion baseline.
- If results differ, inspect the source, promotion filter, grouping, measures, `HAVING` rule, denominator, and percentage conversion before continuing.

## 5. Diagnose the PySpark denominator bug

- Let participants observe the suspicious result: both cohorts appear to be 100%.
- The helper filters to `fpd5_flag = 1` before aggregation, removing non-FPD5 eligible contracts from the denominator.
- The repair keeps the full eligible population, counts contracts for the denominator, and sums `fpd5_flag` for the numerator.
- Validate exactly two cohorts, positive eligible counts, FPD5 counts no greater than eligible counts, and Metric View agreement within 0.05 percentage points.

## 6. Notebook compute versus SQL warehouse

- In this lab, Python, PySpark, `spark.sql(...)`, and `%sql` run on the notebook's Serverless compute.
- Genie Code assists with the notebook, but approved notebook cells still run on that notebook compute.
- The AI/BI dashboard and private Genie Agent execute their analytical SQL on a SQL warehouse.
- Notebook `%sql` statements should not be presented as SQL warehouse Query History activity.

## 7. Review optimization and documentation

- `/optimize` is a proposal, not proof that a query is faster.
- Accept a change only when the result remains identical and there is a material rationale.
- Performance claims require Query Profile evidence.
- `/doc` should capture the grouping, eligible-contract denominator, and threshold without duplicating the FPD5 formula.

## 8. Turn evidence into a dashboard

- The disposable dashboard uses only `fpd_metrics` and remains unpublished.
- KPI counters show the all-cohort baseline.
- The promotion filter affects the cohort comparison and store ranking, not the all-cohort KPI counters.
- Store rankings retain eligible and FPD5 counts beside the rate and require at least 10 eligible contracts.
- The point is to show that generated presentation assets still require reconciliation and publication decisions.

## 9. Optional private Genie Agent improvement

- Continue with the participant's private Section 01 Agent; do not create a second Agent.
- Keep `fpd_metrics` as its only data source.
- Add the smallest instruction or verified example needed for counts, observation date, investigation language, and the 10-contract ranking rule.
- Test the target question and the original cohort comparison in fresh conversations to detect regression.

## Closing question

Where did AI accelerate the work, and which review or validation step prevented speed from weakening trust?
