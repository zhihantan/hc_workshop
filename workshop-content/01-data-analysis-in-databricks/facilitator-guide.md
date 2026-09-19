# Facilitator guide — Data Analysis in Databricks

**Facilitator-only:** Participants should start with `README.md`, `participant-lab.py`, and `exercises.md`.

## Delivery intent

This is an operational-takeover session, not a catalogue of Databricks features. Every product choice should answer one of four handover questions:

1. What workload is this asset serving?
2. Which compute should run it?
3. Which governed definition and permissions does it depend on?
4. Where does the new owner monitor and recover it?

Use `slide-outline.md` for concepts that are faster to compare on a slide. Switch to the workspace for actions participants need to recognize or repeat.

The following Generative AI session uses Genie Code to iteratively improve the private Agent each participant creates here. The facilitator creates the same Agent live in the demonstration account while participants follow in the sandbox; there is no prepared or shared source Agent.

## Before participants enter

1. Run `../../workshop-setup/section-01-facilitator-setup.sql` on the workshop SQL warehouse.
2. Confirm the source-table check returns `8`.
3. Confirm the Metric View returns approximately 42.26% FPD5 for the promotion and 21.03% for other eligible originations.
4. Confirm `participant-lab.py` is available under `/Workspace/Shared/hc_workshop/workshop-content/01-data-analysis-in-databricks/`.
5. Confirm the notebook runs on the assigned serverless notebook compute.
6. Rehearse the complete participant path with a non-admin identity in the demonstration account, delete the rehearsal-only Agent before delivery, and have the sandbox administrator validate the same path with a participant-equivalent identity.
7. Fill in the runtime, warehouse, facilitator group, and dashboard URL marked `TBD` in the section README.
8. Confirm the presenter has `CAN MONITOR` on the SQL warehouse and `CAN MANAGE` if the live demonstration opens its Edit page.
9. Save one real healthy query profile and, if available, one queue or spill example for read-only fallback evidence.
10. Confirm participants can create a Genie Agent in their own user folder, select the workshop warehouse, attach `fpd_metrics`, and keep the Agent unshared.
11. Rehearse the cohort and store-associate questions and record their expected SQL behavior for the Section 01 verification and Section 02 iteration.

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

Do not build the entire dashboard live. Open the prepared draft, reconcile it, demonstrate a filter, and publish it. Change one widget only if the section is ahead of schedule.

Dashboard URL: **TBD — facilitator confirmation required**

### Rehearse the Genie Agent creation path

Do not precreate or share a workshop Agent. Use the exact steps in `exercises.md`: create one Agent in the current user's private folder, attach only `hc_workshop.workshop_shared.fpd_metrics`, select the workshop SQL warehouse, add the prescribed description and common questions, verify the Share dialog, and run the baseline cohort question.

The facilitator performs those same steps in the demonstration account while participants follow in the sandbox. Do not ask participants to open, clone, or depend on the facilitator's Agent.

## Minute-by-minute run of show

| Time | Minutes | Mode | Activity | Observable result |
|---|---:|---|---|---|
| 9:45–9:48 | 3 | Slide | Re-establish the handover scenario and FPD5 question | Participants can state the question and fiction boundary |
| 9:48–9:55 | 7 | Slides | Choose the workload surface and operating model | Participants distinguish notebook, jobs, and SQL compute and the SQL warehouse types |
| 9:55–10:00 | 5 | Watch me | Find the notebook, source schema, and compute selector | Eight inherited tables are visible |
| 10:00–10:18 | 18 | Run with me | Run notebook through FPD5 cohort and hotspot analysis | Rates and concentration checks appear |
| 10:18–10:30 | 12 | Try it | Change the analytical grain and write the handover note | Participant-generated evidence, denominator, caveat, and owner question recorded |
| 10:30–10:40 | 10 | Run with me | Persist the investigation and inspect Delta history | Participant-specific result shows before/after schemas |
| 10:40–10:50 | 10 | Watch me | Trace the Metric View into the prepared dashboard | Dashboard reconciles to the notebook and governed metrics |
| 10:50–11:00 | 10 | Run with me | Create a private Genie Agent and verify one baseline question | Each Agent uses governed measures and remains unshared |
| 11:00–11:06 | 6 | Operate it | Inspect the SQL workload generated during the section | Participants locate a real query and distinguish queue from spill |
| 11:06–11:10 | 4 | Flex | Absorb UI latency or permission recovery | Final checkpoint remains protected |
| 11:10–11:15 | 5 | Checkpoint | Assign operational ownership | Participants name one owner, one risk, and one recovery action |

If the section falls behind, skip the optional dashboard edit and use the prepared query profile. Protect the participant-authored breakdown, private Agent baseline, and final checkpoint.

## 9:45–9:55 — Business hook and compute decisions

Use slides 1–3. Introduce the tools participants will use now; do not attempt a complete compute product survey.

### Talking points

- There are two related decisions:
  1. **Workload surface:** interactive notebook, automated job, or SQL/BI.
  2. **Management model:** serverless by default or classic when a supported customization requires it.
- For interactive Python and SQL notebooks, prefer serverless notebook compute. Use classic all-purpose compute for requirements such as R, RDD APIs, JARs, init scripts, or cluster-level customization that serverless does not support.
- For automated notebook, Python, and wheel tasks, prefer serverless jobs. Use classic jobs compute for unsupported customization or task types such as Spark Submit. Avoid all-purpose compute for production jobs.
- For dashboards, BI tools, SQL tasks, and Genie Agents, use a SQL warehouse; prefer serverless.
- SQL warehouse types are Serverless, Pro, and Classic. **Pro is a SQL warehouse type, not a universal compute layer.** Pro remains relevant when serverless is unavailable or custom networking is required; Classic is entry-level.
- Compute policies and Unity Catalog permissions remain operational controls; serverless removes infrastructure management, not ownership.
- Tell participants that the section will return to Warehouse Monitoring and Query Profile after the dashboard and Genie Agent have generated real SQL activity.

### Check for understanding

Ask: "A scheduled Python notebook currently runs every hour on an analyst's all-purpose compute. What should the new owner challenge?" Expected answer: move the automated workload to serverless jobs or justified classic jobs compute, then define ownership and monitoring.

## 9:55–10:30 — Notebook analysis and participant extension

### Exact UI path

1. **Workspace > Shared > hc_workshop > workshop-content > 01-data-analysis-in-databricks > participant-lab**
2. Use the notebook compute selector and choose the assigned **Serverless** notebook compute.
3. Run sequentially through the store-associate hotspot cell.
4. At **Try it**, ask participants to change `ANALYSIS_DIMENSION`, rerun the breakdown, and complete the first task in `exercises.md`.
5. Stop before the Delta section until the 12-minute exercise timebox ends.
6. When starting the Delta section, explain that the notebook derives a collision-resistant runner ID from each participant's full workspace identity and uses it in the persistent table name.

Pause at the following cells:

- Source inventory: confirm the handover describes what actually exists.
- PySpark summary: explain that Python and SQL share Unity Catalog governance.
- SQL trend: add one notebook visualization; do not spend time formatting it.
- FPD5 population: stress grain, observation eligibility, and the inclusive day-five boundary.
- Cohort and concentration: connect counts, rates, and denominators.
- Try it: give participants 12 uninterrupted minutes to change the grain, rerun, interpret the output, and write their note.

Do not reveal the exact expected rates until most participants have finished. Ask one participant which dimension they changed and how the result affected their interpretation, then correct causal or denominator overreach.

Use slide 4 while transitioning from source discovery to the Python and SQL cells.

## 10:30–10:40 — Persist the investigation with Delta Lake

Use slide 5, then run the Delta cells.

### Talking points

- Delta Lake is the default table format on Databricks. It adds an open transaction log to Parquet files for ACID transactions, scalable metadata, schema enforcement, and batch/streaming use.
- The table persists the breakdown each participant just produced; it is not a disconnected sample dataset.
- Schema evolution is explicit. The lab adds `review_note` deliberately rather than enabling broad session-wide automatic evolution.
- Every committed table change creates a version. `DESCRIBE HISTORY` supports audit and diagnosis; `VERSION AS OF` or `TIMESTAMP AS OF` reads a retained snapshot.
- Time travel is not a backup promise. Both transaction-log history and old data files must still exist; `VACUUM` and retention settings determine availability.

### Checkpoint

The baseline and evolved snapshots must have the same analytical row count. The baseline has five analytical columns; the evolved snapshot adds `review_note`. Version numbers can differ after reruns.

## 10:40–10:50 — Governed Metric View and AI/BI Dashboard

Use slide 6, then open the prepared draft.

### Exact UI path

1. **Catalog > hc_workshop > workshop_shared > fpd_metrics**
2. Show the source, fields, measures, comments, synonyms, and percentage/currency formats.
3. Run the final Metric View cell in `participant-lab.py` and reconcile it with the notebook cohort result.
4. Open **Dashboards > Unicorn FPD5 Overview**.
5. Open the **Data** tab and point out the same governed Metric View.
6. Return to the canvas. If the section is ahead of schedule, change one title; otherwise preserve the prepared draft.
7. Apply the **Promotion Cohort** filter and verify KPI changes.
8. Select **Publish** and review the data-permission mode before confirming.
9. Open the published view and show that it is a snapshot separate from the draft.

### Talking points

- A dashboard draft is an editable workspace asset; viewers receive the last published snapshot.
- Metric Views keep the FPD5 formula and reusable measures outside individual widgets and Agent instructions.
- **Individual data permissions** use each viewer's Unity Catalog permissions and enforce row filters and column masks per viewer.
- **Share data permissions** use the publisher's data permissions. This helps consumers without source access, but can expose data beyond direct grants and should use a governed publishing identity in production.
- The operator owns the dataset query, warehouse, publishing identity, refresh behavior, dashboard ACLs, and reconciliation test.

## 10:50–11:00 — Create and verify the private Genie Agent

Use slide 7, then have everyone follow the Agent-creation steps in `exercises.md`. Create the Agent live in the demonstration account while participants perform the same actions in the sandbox.

### Agent creation and baseline verification

1. Open **Genie Agents**, select **New**, and choose only `hc_workshop.workshop_shared.fpd_metrics`.
2. Create **Unicorn FPD5 Investigator — `<workspace_username>`** in the current user's folder.
3. Apply the description, warehouse, and common questions from `exercises.md`. Do not tune the Agent context yet.
4. Confirm the Agent appears in the current user's folder in the Workspace browser. Open **Share** and confirm it is not shared with all account users, the workshop group, or another participant.
5. Ask:

> As of 2026-09-01, how does FPD5 for the 0% smartphone promotion compare with other eligible originations?

6. Inspect the generated SQL and result before reading the prose as truth.
7. Confirm the SQL uses `fpd_metrics`, invokes governed measures, and reconciles to approximately 42.26% versus 21.03%.
8. Confirm the answer states the observation date and avoids a confirmed-fraud claim.

Save the baseline response and generated SQL. Section 02 returns to this same private Agent, improves it with Genie Code, and regression-tests this answer.

## 11:00–11:06 — Inspect the SQL warehouse workload

Use slide 8. Return to the compute concepts from the opening, now using SQL activity generated by the Metric View, dashboard, and Genie Agent.

### Exact UI paths

1. **SQL Warehouses > `<workshop warehouse>` > Monitoring**
   - Show running and queued queries, query volume, and cluster count.
2. **Query History > filter by `<workshop warehouse>`**
   - Locate a dashboard or Genie-generated statement from this session.
3. Select the statement and open **See Query Profile**.
   - Show scheduling versus execution time, longest operators, rows and bytes, pruning, and any spill insight.

Describe this as **workload utilization**, not host-level CPU utilization. Serverless abstracts infrastructure management; operators use demand, queueing, scaling, duration, profile evidence, and cost to decide whether action is needed.

### Symptom-to-action rules

- **Sustained queueing:** review concurrent demand, maximum clusters, workload isolation, and query arrival patterns.
- **Disk spill or `DATA_SPILL`:** reduce rows or wide columns, inspect joins and aggregations, then increase warehouse size if the individual query genuinely needs more memory.
- **Long result fetching:** inspect the client or open session; more warehouse clusters do not fix a client that is not consuming results.
- **Idle cost:** review auto-stop against the usage pattern rather than always selecting the minimum.
- **Variable demand:** Intelligent Workload Management predicts query needs and manages serverless admission and scaling; the owner still monitors service levels and spend.

If there is no real spill or queue during the class, say so. Do not manufacture a pathological query against the shared workshop warehouse. Use the saved read-only profile prepared before the workshop to explain the missing symptom.

## 11:10–11:15 — Handover checkpoint

Build the asset checklist aloud during each segment. At the final checkpoint, ask each participant to choose one asset and state one owner, one operational risk, and one recovery action:

- Notebook: owner, compute, parameters, source tables, output table, rerun behavior.
- Delta table: owner, history, retention dependency, retained-version read, cleanup boundary.
- Dashboard: dataset, warehouse, publisher credential mode, ACL, reconciliation query.
- SQL warehouse: manager, auto-stop, size, scaling bounds, queue/spill monitor.
- Metric View: metric owner, FPD5 definition, source view, permissions, change review.
- Genie Agent: domain owner, source scope, warehouse, test questions, SQL verification, rollback path.

## Fallbacks

- **No serverless notebook compute:** use approved Unity Catalog-compatible classic all-purpose compute and explain the exception.
- **No serverless SQL warehouse:** use an approved pro SQL warehouse; do not claim Intelligent Workload Management behavior for it.
- **No Metric View support:** query `fpd_analysis` directly, use the notebook fallback, and omit participant Agent creation rather than duplicating the FPD5 formula in Agent instructions. Record this as a blocker for Section 02.
- **No AI/BI Dashboard access:** use notebook visualizations and explain draft/publish and credential modes on slide 6.
- **No Genie Agent access:** continue with the facilitator's live demonstration, run the trusted Metric View question in the participant SQL editor, and demonstrate the verification checklist without claiming a participant Agent result. Do not replace the missing personal Agent with a shared one.
- **Agent creation stalls:** use the remaining time to inspect the facilitator's generated SQL and answer. Record the affected identity or entitlement for sandbox follow-up; do not share or clone the facilitator's Agent across accounts.
- **Insufficient monitoring permissions:** show the participant's own Query History, then state that warehouse-wide monitoring requires the appropriate warehouse permission.

## Facilitator references

- [Compute selection recommendations](https://docs.databricks.com/compute/choose-compute)
- [SQL warehouse sizing, scaling, and queuing](https://docs.databricks.com/compute/sql-warehouse/warehouse-behavior)
- [Monitor a SQL warehouse](https://docs.databricks.com/compute/sql-warehouse/monitor/)
- [Query history and Query Profile](https://docs.databricks.com/sql/user/queries/query-history)
- [Delta Lake](https://docs.databricks.com/delta/)
- [AI/BI dashboards](https://docs.databricks.com/dashboards/)
- [Unity Catalog semantics](https://docs.databricks.com/uc-semantics/)
- [Genie Agents](https://docs.databricks.com/genie-agents/)

