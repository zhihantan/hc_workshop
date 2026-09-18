# Facilitator guide — Data Analysis in Databricks

**Facilitator-only:** Participants should start with `README.md`, `participant-lab.py`, and `exercises.md`.

## Delivery intent

This is an operational-takeover session, not a catalogue of Databricks features. Every product choice should answer one of four handover questions:

1. What workload is this asset serving?
2. Which compute should run it?
3. Which governed definition and permissions does it depend on?
4. Where does the new owner monitor and recover it?

Use `slide-outline.md` for concepts that are faster to compare on a slide. Switch to the workspace for actions participants need to recognize or repeat.

The following Generative AI session should build on this governed Genie Agent and cover the wider Genie family; do not repeat the Metric View setup or FPD5 verification.

## Before participants enter

1. Run `../../workshop-setup/section-01-facilitator-setup.sql` on the workshop SQL warehouse.
2. Confirm the source-table check returns `8`.
3. Confirm the Metric View returns approximately 42.26% FPD5 for the promotion and 21.03% for other eligible originations.
4. Confirm `participant-lab.py` is available under `/Workspace/Shared/hc_workshop/workshop-content/01-data-analysis-in-databricks/`.
5. Confirm the notebook runs on the assigned serverless notebook compute.
6. Rehearse with a non-admin participant identity.
7. Fill in the runtime, warehouse, group, dashboard URL, and Genie Agent URL marked `TBD` in the section README.
8. Confirm the presenter has `CAN MONITOR` on the SQL warehouse and `CAN MANAGE` if the live demonstration opens its Edit page.
9. Save one real healthy query profile and, if available, one queue or spill example for read-only fallback evidence.
10. Rehearse one Genie question with a known, evidence-backed before/after improvement and one regression question. Record both before the event.

### Prepare the dashboard

Create a draft named **Unicorn FPD5 Overview**:

1. Go to **New > Dashboard**.
2. In the **Data** tab, add `hc_workshop.workshop_shared.fpd_metrics` as the governed dataset.
3. Add three KPI counters: Eligible Contracts, FPD5 Contracts, and FPD5 Rate.
4. Add a monthly chart using Origination Month, Eligible Contracts, and FPD5 Rate.
5. Add a store ranking fixed to the 0% smartphone promotion, with at least 10 eligible contracts per store. Use Store, Eligible Contracts, and FPD5 Rate. Keep high-cardinality sales-associate detail in a table rather than a color series.
6. Add global filters for Promotion Cohort, Origination Month, and Region.
7. Add a detail table with Store Code, Store, Sales Associate ID, Eligible Contracts, FPD5 Contracts, and FPD5 Rate.
8. Verify the KPI, monthly, store, and store-associate grains against their matching validation queries in `../../workshop-setup/section-01-facilitator-setup.sql`.
9. Publish using **Individual data permissions** for the workshop because participants already have `SELECT` on the Metric View. Explain that **Share data permissions** runs through the publisher's permissions and must be reviewed carefully.

Do not build the entire dashboard live. Open the prepared draft, add or change one widget, demonstrate a filter, and publish the revised draft.

Dashboard URL: **TBD — facilitator confirmation required**

### Prepare the Genie Agent

Create a focused Genie Agent named **Unicorn FPD5 Investigator**:

1. Go to **Genie > Create Genie Agent**.
2. Set the description to:

   > Answers governed questions about eligible fixed-term contracts and FPD5 for the synthetic Unicorn Finance workshop. It compares promotion, product, channel, store, region, and sales-associate cohorts through the `fpd_metrics` Metric View and must describe hotspots as investigation signals rather than confirmed fraud.

3. Select only `hc_workshop.workshop_shared.fpd_metrics` as the curated source. Do not also attach `fpd_analysis` or the eight raw tables. This narrows the Agent's context but is not a data-access boundary; Unity Catalog permissions remain the access control.
4. Select the workshop serverless SQL warehouse.
5. Enable prompt matching features—format assistance and, where useful, entity matching—only for categorical fields such as Promotion Cohort, Product, Channel, Region, and Store. Do not enable entity matching on IDs or measures.
6. Add these sample questions:
   - How does FPD5 for the 0% smartphone promotion compare with other eligible originations?
   - Which promotion stores have the highest FPD5 rate, with at least 10 eligible contracts?
   - Which promotion store-associate pairs have the highest FPD5 rate, with at least 10 eligible contracts?
7. Add the following verified example SQL only if the baseline Agent needs help with the minimum-denominator and ranking shape:

```sql
SELECT
  fpd_metrics.store_code,
  fpd_metrics.store_name,
  fpd_metrics.sales_associate_id,
  MEASURE(fpd_metrics.eligible_contracts) AS eligible_contracts,
  MEASURE(fpd_metrics.fpd5_contracts) AS fpd5_contracts,
  MEASURE(fpd_metrics.fpd5_rate) AS fpd5_rate
FROM hc_workshop.workshop_shared.fpd_metrics
WHERE fpd_metrics.promotion_cohort = '0% smartphone promotion'
GROUP BY ALL
HAVING MEASURE(fpd_metrics.eligible_contracts) >= 10
ORDER BY fpd5_rate DESC, eligible_contracts DESC, store_code
LIMIT 15
```

8. Test the SQL before adding it. Keep the generated result for comparison during the live quality loop.
9. Share the Agent with participants only after confirming its generated SQL, result, permissions, and warehouse.

The three sample questions are workshop smoke checks, not a production benchmark. A production benchmark must be representative and non-duplicate, with checked SQL for deterministic questions and explicit evaluation criteria for multi-step Agent answers.

Genie Agent URL: **TBD — facilitator confirmation required**

## Minute-by-minute run of show

| Time | Minutes | Mode | Activity | Observable result |
|---|---:|---|---|---|
| 9:45–9:48 | 3 | Slide | Re-establish the handover scenario and FPD5 question | Participants can state the question and fiction boundary |
| 9:48–9:56 | 8 | Slides | Compute by workload; serverless versus classic | Participants choose compute from workload and constraints |
| 9:56–10:00 | 4 | Watch me | Find the notebook, source schema, and compute selector | Eight inherited tables are visible |
| 10:00–10:15 | 15 | Run with me | Run notebook through FPD5 cohort and hotspot analysis | Rates and concentration checks appear |
| 10:15–10:22 | 7 | Try it | Complete the hotspot handover note | Evidence, denominator, caveat, and owner question recorded |
| 10:22–10:29 | 7 | Slide + live | Delta history, schema evolution, time travel, and open formats | Runner-specific Delta table shows before/after versions |
| 10:29–10:40 | 11 | Watch me | Edit, filter, verify, and publish the prepared dashboard | Dashboard reconciles to governed metrics |
| 10:40–10:49 | 9 | Operate it | Inspect warehouse settings, monitoring, query history, and profile | Queue and spill lead to different actions |
| 10:49–11:00 | 11 | Watch me | Inspect the Metric View and run one rehearsed Genie quality pass | Agent SQL uses governed measures |
| 11:00–11:05 | 5 | Run with me | Ask one question and verify it against trusted SQL | Natural-language answer reconciles |
| 11:05–11:10 | 5 | Buffer | Absorb startup, permissions, or discussion delay | Core checkpoint remains protected |
| 11:10–11:15 | 5 | Checkpoint | Assign operational ownership | Participants name one owner, one risk, and one recovery action |

## 9:45–9:56 — Compute decisions

Use slides 1–3.

### Talking points

- There are two related decisions:
  1. **Workload surface:** interactive notebook, automated job, or SQL/BI.
  2. **Management model:** serverless by default or classic when a supported customization requires it.
- For interactive Python and SQL notebooks, prefer serverless notebook compute. Use classic all-purpose compute for requirements such as R, RDD APIs, JARs, init scripts, or cluster-level customization that serverless does not support.
- For automated notebook, Python, and wheel tasks, prefer serverless jobs. Use classic jobs compute for unsupported customization or task types such as Spark Submit. Avoid all-purpose compute for production jobs.
- For dashboards, BI tools, SQL tasks, and Genie Agents, use a SQL warehouse; prefer serverless.
- SQL warehouse types are serverless, pro, and classic. Pro remains relevant when serverless is unavailable or custom networking is required; classic is entry-level. Do not present SQL warehouses as a simple serverless/classic binary.
- Compute policies and Unity Catalog permissions remain operational controls; serverless removes infrastructure management, not ownership.

### Check for understanding

Ask: "A scheduled Python notebook currently runs every hour on an analyst's all-purpose compute. What should the receiving team challenge?" Expected answer: move the automated workload to serverless jobs or justified classic jobs compute, then define ownership and monitoring.

## 9:56–10:22 — Notebook analysis and exercise

### Exact UI path

1. **Workspace > Shared > hc_workshop > workshop-content > 01-data-analysis-in-databricks > participant-lab**
2. Use the notebook compute selector and choose the assigned **Serverless** notebook compute.
3. Run sequentially through the store-associate hotspot cell. Stop before the Delta section for the participant exercise.
4. When starting the Delta section, ask participants to enter their assigned `team_id`. Explain that it groups persistent workshop artifacts for cleanup; the notebook adds a runner suffix automatically to prevent teammates from overwriting each other.

Pause at the following cells:

- Source inventory: confirm the handover describes what actually exists.
- PySpark summary: explain that Python and SQL share Unity Catalog governance.
- SQL trend: add one notebook visualization; do not spend time formatting it.
- FPD5 population: stress grain, observation eligibility, and the inclusive day-five boundary.
- Cohort and concentration: connect counts, rates, and denominators.
- Try it: give teams seven uninterrupted minutes.

Do not reveal the exact expected rates until most groups have finished. Ask one group to read its two-sentence note, then correct causal or denominator overreach.

Use slide 4 while transitioning from source discovery to the Python and SQL cells.

## 10:22–10:29 — Delta Lake and open table formats

Use slide 5, then run the Delta cells.

### Talking points

- Delta Lake is the default table format on Databricks. It adds an open transaction log to Parquet files for ACID transactions, scalable metadata, schema enforcement, and batch/streaming use.
- Schema evolution is an explicit write decision. The lab enables `mergeSchema` for one append; do not enable broad session-wide auto-evolution casually.
- Every write creates a version. `DESCRIBE HISTORY` supports audit and diagnosis; `VERSION AS OF` or `TIMESTAMP AS OF` reads a retained snapshot.
- Time travel is not a backup promise. Both transaction-log history and old data files must still exist; `VACUUM` and retention settings determine availability.
- Apache Iceberg is also an open table format with ACID transactions, schema evolution, and time travel. Use managed Iceberg or Unity Catalog's Iceberg REST Catalog when cross-engine Iceberg read/write interoperability is the requirement.
- If Delta is the operational format but external Iceberg readers need access, evaluate External Iceberg Reads rather than copying data. Format choice follows interoperability and feature requirements, not fashion.

### Checkpoint

The result must show 10 rows and two columns before evolution, then 20 rows and three columns after evolution. Version numbers can differ after reruns.

## 10:29–10:40 — AI/BI Dashboard

Use slide 6, then open the prepared draft.

### Exact UI path

1. **Dashboards > Unicorn FPD5 Overview**
2. Open the **Data** tab and point out the governed Metric View.
3. Return to the canvas, change one title or add one visualization.
4. Apply the **Promotion Cohort** filter and verify KPI changes.
5. Select **Publish** and review the data-permission mode before confirming.
6. Open the published view and show that it is a snapshot separate from the draft.

### Talking points

- A dashboard draft is an editable workspace asset; viewers receive the last published snapshot.
- Metric Views keep KPI formulas outside individual widgets.
- **Individual data permissions** use each viewer's Unity Catalog permissions and enforce row filters and column masks per viewer.
- **Share data permissions** use the publisher's data permissions. This helps consumers without source access, but can expose data beyond direct grants and should use a governed publishing identity in production.
- The operator owns the dataset query, warehouse, publishing identity, refresh behavior, dashboard ACLs, and reconciliation test.

## 10:40–10:49 — Operate the SQL warehouse

Use slide 7.

### Exact UI paths

1. **SQL Warehouses > `<workshop warehouse>` > Edit**
   - Show type, size, minimum/maximum clusters, and auto-stop.
   - Do not change production-like settings during the workshop.
2. **SQL Warehouses > `<workshop warehouse>` > Monitoring**
   - Show running queries, queued queries, cluster count, Peak Query Count, and Query History.
3. **Query History > filter by `<workshop warehouse>` > select a dashboard query > See Query Profile**
   - Show scheduling versus execution time, longest operators, rows and bytes, pruning, and any spill insight.

### Symptom-to-action rules

- **Sustained queueing:** review concurrent demand, maximum clusters, workload isolation, and query arrival patterns.
- **Disk spill or `DATA_SPILL`:** reduce rows or wide columns, inspect joins and aggregations, then increase cluster size if the individual query needs more memory.
- **Long result fetching:** inspect the client or open session; more warehouse clusters do not fix a client that is not consuming results.
- **Idle cost:** review auto-stop against usage pattern. Serverless defaults to 10 minutes and can stop quickly; do not always choose the minimum because repeated cold starts can hurt interactive use.
- **Variable demand:** Intelligent Workload Management predicts query needs, queues when capacity is unavailable, and provisions or removes clusters. The owner still monitors whether the configured bounds meet the service level.

If there is no real spill or queue during the class, say so. Do not manufacture a pathological query against the shared workshop warehouse.

Use the saved read-only profile evidence prepared before the workshop when the live warehouse has no queue or spill example.

## 10:49–11:05 — Metric View and Genie Agent

Use slide 8, then open the prepared Agent.

### Metric View path

1. **Catalog > hc_workshop > workshop_shared > fpd_metrics**
2. Show the source, fields, measures, comments, synonyms, and percentage/currency formats.
3. Run the final Metric View cell in `participant-lab.py`.
4. Reconcile the result with the dashboard.

### Genie quality loop

1. Open **Genie > Unicorn FPD5 Investigator**.
2. Start a new conversation and ask the rehearsed question with its known target behavior.
3. Inspect the generated SQL and result before reading the prose as truth.
4. Show the rehearsed smallest structured improvement: field metadata, synonym, categorical matching, or the verified ranking example. Do not add a long instruction block.
5. Start a fresh conversation and rerun the affected question.
6. Rerun the previously correct cohort-comparison question as a regression check.
7. Keep the change only if it fixes the target without breaking the regression question.

If rehearsal finds no valid Agent defect, demonstrate SQL/result verification and make no change. Do not degrade a healthy Agent to manufacture a before/after story.

### Participant verification

Ask participants to run:

> As of 2026-09-01, how does FPD5 for the 0% smartphone promotion compare with other eligible originations?

They must inspect the generated SQL, confirm it queries `fpd_metrics` with `MEASURE()`, and reconcile the values to the notebook.

## 11:10–11:15 — Handover checkpoint

Build the asset checklist aloud during each segment. At the final checkpoint, ask each team to choose one asset and state one owner, one operational risk, and one recovery action:

- Notebook: owner, compute, parameters, source tables, output table, rerun behavior.
- Delta table: owner, history, retention dependency, retained-version read, cleanup boundary.
- Dashboard: dataset, warehouse, publisher credential mode, ACL, reconciliation query.
- SQL warehouse: manager, auto-stop, size, scaling bounds, queue/spill monitor.
- Metric View: metric owner, FPD5 definition, source view, permissions, change review.
- Genie Agent: domain owner, source scope, warehouse, test questions, SQL verification, rollback path.

## Fallbacks

- **No serverless notebook compute:** use approved Unity Catalog-compatible classic all-purpose compute and explain the exception.
- **No serverless SQL warehouse:** use an approved pro SQL warehouse; do not claim Intelligent Workload Management behavior for it.
- **No Metric View support:** query `fpd_analysis` directly, use the notebook fallback, and omit Metric View-specific Genie optimization.
- **No AI/BI Dashboard access:** use notebook visualizations and explain draft/publish and credential modes on slide 6.
- **No Genie Agent access:** run the trusted Metric View questions in the SQL editor and demonstrate the verification checklist without claiming an Agent result.
- **Insufficient monitoring permissions:** show the participant's own Query History, then state that warehouse-wide monitoring requires the appropriate warehouse permission.

## Facilitator references

- [Compute selection recommendations](https://docs.databricks.com/compute/choose-compute)
- [SQL warehouse sizing, scaling, and queuing](https://docs.databricks.com/compute/sql-warehouse/warehouse-behavior)
- [Monitor a SQL warehouse](https://docs.databricks.com/compute/sql-warehouse/monitor/)
- [Query history and Query Profile](https://docs.databricks.com/sql/user/queries/query-history)
- [Delta Lake](https://docs.databricks.com/delta/)
- [Apache Iceberg](https://docs.databricks.com/iceberg/)
- [AI/BI dashboards](https://docs.databricks.com/dashboards/)
- [Unity Catalog semantics](https://docs.databricks.com/uc-semantics/)
- [Genie Agents](https://docs.databricks.com/genie-agents/)

