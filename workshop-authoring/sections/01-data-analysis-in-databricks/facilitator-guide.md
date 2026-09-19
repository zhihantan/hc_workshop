# Facilitator guide — Data Analysis in Databricks

**Facilitator-only.** Distribute only [`participant-lab.py`](../../../workshop-content/01-data-analysis-in-databricks/participant-lab.py) to participants.

## Delivery intent

Deliver one investigation, not a catalogue of features. Participants act as Unicorn Finance analysts taking ownership from Atlas Ridge Consulting. Every product action should help answer or operate this question:

> Does the 0% smartphone promotion show elevated first-payment default, and where should the business investigate?

The notebook supplies all participant instructions, exercises, expected checkpoints, Agent steps, and reflection prompts. Do not direct participants to a second document.

## Before participants enter

1. Run [`section-01-facilitator-setup.sql`](../../../workshop-setup/section-01-facilitator-setup.sql) on the workshop SQL warehouse.
2. Confirm the source-table check returns `8`.
3. Confirm `fpd_metrics` returns approximately 42.26% FPD5 for the promotion and 21.03% for other eligible originations.
4. Import only `participant-lab.py` into the participant-facing Section 01 workspace folder.
5. Confirm the notebook runs on the assigned serverless notebook compute.
6. Rehearse the full path with a non-admin identity in the demonstration account.
7. Have the sandbox administrator validate the same path with a participant-equivalent identity.
8. Confirm participants can write only their participant-specific table in `workshop_labs`.
9. Confirm participants can create an Agent in their user folder, select the workshop warehouse, attach `fpd_metrics`, and leave the Agent unshared.
10. Save one real healthy query profile and, if available, one queue or spill example for read-only fallback evidence.
11. Fill in the runtime, warehouse, facilitator group, and dashboard URL in the section maintainer README.

## Prepare the dashboard

Create a draft named **Unicorn FPD5 Overview**:

1. Go to **New > Dashboard**.
2. Add `hc_workshop.workshop_shared.fpd_metrics` as the governed dataset.
3. Add KPI counters for Eligible Contracts, FPD5 Contracts, and FPD5 Rate.
4. Add a monthly chart using Origination Month, Eligible Contracts, and FPD5 Rate.
5. Add a store ranking fixed to the 0% smartphone promotion with at least 10 eligible contracts per store.
6. Add global filters for Promotion Cohort, Origination Month, and Region.
7. Add a detail table with Store Code, Store, Sales Associate ID, Eligible Contracts, FPD5 Contracts, and FPD5 Rate.
8. Reconcile each grain with the validation queries in `section-01-facilitator-setup.sql`.
9. Publish using **Individual data permissions**.

Do not build the whole dashboard live. Open the prepared draft, reconcile it, demonstrate one filter, and explain the publish and permission choices.

## Rehearse the Agent path

Do not precreate or share a workshop Agent. Follow the steps embedded in `participant-lab.py`:

- create **Unicorn FPD5 Investigator — `<workspace_username>`**;
- attach only `hc_workshop.workshop_shared.fpd_metrics`;
- select the workshop SQL warehouse;
- add the prescribed description and common questions;
- verify the Workspace location and Share dialog;
- run the baseline cohort question; and
- inspect and save the generated SQL and response.

Create the Agent live in the demonstration account while participants do the same in their sandbox accounts.

## Run of show

| Time | Minutes | Mode | Activity | Observable result |
|---|---:|---|---|---|
| 9:45–9:50 | 5 | Frame | Assignment, FPD5 definition, eligibility, and caveat | Participants can explain the question and denominator |
| 9:50–9:57 | 7 | Explain | Choose compute by workload | Participants distinguish notebook and SQL compute |
| 9:57–10:15 | 18 | Run with me | Verify sources, profile applications, and inspect promotion timing | The business premise is tested before repayment analysis |
| 10:15–10:27 | 12 | Run with me | Build the eligible FPD5 population and test concentration | Counts, rates, grain, and volume context are distinguished |
| 10:27–10:39 | 12 | Try it | Change grain and write the handover note | Participant-generated evidence and caveat |
| 10:39–10:49 | 10 | Run with me | Persist the result and inspect Delta history | Before/after versions are visible |
| 10:49–10:56 | 7 | Watch and verify | Reconcile the Metric View and dashboard | Governed measures match the notebook |
| 10:56–11:06 | 10 | Run with me | Create and verify the private Genie Agent | Agent remains unshared and generated SQL reconciles |
| 11:06–11:11 | 5 | Operate it | Inspect one SQL statement and Query Profile | Queueing and spill are distinguished |
| 11:11–11:15 | 4 | Reflect | Complete the investigation checkpoint | One owner, risk, and recovery action are named |

If the section falls behind, skip cosmetic dashboard edits and use the saved query profile. Protect the participant grain exercise, private Agent baseline, and final reflection.

## Opening and compute framing

Start with the business assignment before introducing Databricks products.

Use these workload choices:

- interactive Python and SQL analysis: serverless notebook compute by default;
- automated notebooks, Python, and wheels: serverless jobs by default;
- dashboards, BI, SQL tasks, and Genie Agents: serverless SQL warehouse by default;
- classic compute only when a supported customization or environment constraint requires it.

Pro is a SQL warehouse type, not a universal compute layer. Serverless removes infrastructure management, not ownership of code, permissions, cost, data quality, or monitoring.

Check for understanding:

> A scheduled Python notebook runs every hour on an analyst's all-purpose compute. What should the new owner challenge?

Expected answer: move the automated workload to serverless jobs or justified classic jobs compute, then define ownership and monitoring.

## Notebook investigation

Open:

**Workspace > Shared > hc_workshop > workshop-content > 01-data-analysis-in-databricks > participant-lab**

Run sequentially and pause at these questions:

1. **FPD5 definition:** Why is a contract due on August 30 not eligible on September 1?
2. **Source verification:** Does the handover contain the expected data and observation date?
3. **Application profile:** Which channels contain the promotion, and why is this not repayment evidence?
4. **Monthly SQL trend:** Did promotion volume actually appear when claimed?
5. **Eligible population:** Why would using every application bias the denominator?
6. **Cohort comparison:** What do the rates and counts establish?
7. **Store volume:** Why is application concentration not the same as FPD5 concentration?
8. **Store-associate result:** Why retain a minimum denominator?

At the participant exercise, allow 12 uninterrupted minutes. Ask participants to change `ANALYSIS_DIMENSION`, rerun the result, and complete the handover note in the notebook. Do not reveal the exact rates before most participants finish.

Correct these common interpretation errors:

- calling all originated contracts eligible;
- treating payment before day five as FPD5;
- treating high application volume as a high FPD5 rate;
- ranking a one-contract segment as a meaningful hotspot; or
- describing the synthetic signal as confirmed fraud.

## Delta handover

The notebook separates the Delta workflow into five stages. Explain the purpose before each cell:

1. derive a collision-resistant participant table name;
2. persist the participant's actual breakdown;
3. capture the baseline transaction version;
4. add the operational review note; and
5. compare retained versions.

The row count should stay constant while the later schema adds `review_note`. Version numbers can differ after reruns.

Key messages:

- persistence is justified because another owner needs the result;
- schema changes should be explicit;
- transaction history supports audit and diagnosis; and
- time travel depends on retention and is not a backup guarantee.

## Metric View and dashboard

Open:

1. **Catalog > hc_workshop > workshop_shared > fpd_metrics**
2. **Dashboards > Unicorn FPD5 Overview**

Show that the same governed measures serve the notebook reconciliation, dashboard, and Genie Agent.

Explain:

- the dashboard draft is editable, while viewers receive the last published snapshot;
- **Individual data permissions** apply each viewer's Unity Catalog permissions;
- **Share data permissions** use the publisher's permissions and make that identity a control point; and
- the operator owns the dataset, warehouse, publishing identity, refresh behavior, ACLs, and reconciliation test.

## Private Genie Agent

Follow the participant notebook exactly. After everyone asks the baseline question:

1. inspect generated SQL before reading the prose as truth;
2. confirm it queries `fpd_metrics`;
3. confirm it invokes governed measures;
4. reconcile approximately 42.26% versus 21.03%;
5. confirm the observation date is stated;
6. confirm the answer avoids a fraud conclusion; and
7. confirm the Agent is not shared with other participants.

Section 02 returns to this same Agent. Participants do not clone or create another Agent.

## SQL workload inspection

Use SQL generated during the section:

1. open **Query History** and filter to the workshop warehouse;
2. locate a dashboard- or Genie-generated statement that queries the Metric View;
3. open **Query Profile**;
4. separate waiting, execution, and result-fetching time; and
5. inspect operators, bytes, pruning, and spill evidence.

Do not imply that the notebook's `spark.sql` or `%sql` cells ran on the SQL warehouse. They ran on the notebook's attached compute; the dashboard and Genie Agent generated the warehouse workload inspected here.

Use these symptom-to-action rules:

- sustained queueing: inspect concurrency, maximum clusters, arrival patterns, and workload isolation;
- disk spill: reduce scanned or wide data, inspect joins and aggregations, then consider a larger warehouse;
- long result fetching: inspect client behavior;
- idle cost: review auto-stop against usage.

If the live query has no spill or queueing, say so. Use the saved read-only profile to explain a missing symptom; do not manufacture a pathological query.

## Final reflection

Use the final notebook checkpoint. Ask two or three participants to name:

- one asset;
- its owner;
- one operational risk; and
- one recovery or validation action.

Do not add cleanup or facilitator logistics to the participant notebook.

## Fallbacks

- **No serverless notebook compute:** use approved Unity Catalog-compatible classic all-purpose compute and explain the exception.
- **Metric View missing:** restore it with `section-01-facilitator-setup.sql`. Participants should stop rather than recreate the governed definition.
- **No dashboard access:** use the notebook and Metric View result, then explain the prepared dashboard with screenshots.
- **No Genie access:** continue with the live demonstration and have participants verify the generated SQL; do not share or clone the demonstration Agent.
- **Agent creation stalls:** inspect the live generated SQL and record the affected identity for sandbox follow-up.
- **Insufficient monitoring permission:** use each participant's own Query History and the saved profile.
- **Participant table write denied:** confirm `USE SCHEMA` and `CREATE TABLE` on `workshop_labs`; do not redirect writes to a personal or ungoverned catalog.

## References

- [Compute selection recommendations](https://docs.databricks.com/compute/choose-compute)
- [Delta Lake](https://docs.databricks.com/delta/)
- [Unity Catalog metric views](https://docs.databricks.com/uc-semantics/)
- [AI/BI dashboards](https://docs.databricks.com/dashboards/)
- [Genie Agents](https://docs.databricks.com/genie-agents/)
- [Query history and Query Profile](https://docs.databricks.com/sql/user/queries/query-history)
