# Facilitator guide — Generative AI in Databricks

**Duration:** 60 minutes
**Participant notebook:** `participant-lab.py`
**Live-demo notebook:** `facilitator-demo.py`

## Teaching intent

This section should feel like a direct acceleration of Section 01, not a disconnected AI feature tour. Participants have already seen the effort required to discover data, encode FPD5 correctly, debug code, and interpret results. Genie Code now helps them do that technical work faster across governed SQL and PySpark workflows.

The primary outcome is a repeatable working pattern: provide relevant context, request a concrete outcome, review the proposed actions, and validate the result. The dashboard showcase and participant-owned Genie Agents demonstrate that the same pattern extends beyond notebooks.

Repeat this boundary throughout:

> Genie Code can generate and execute work, but the user remains responsible for source selection, permissions, semantic correctness, validation, and approval.

## Before the session

1. Complete the Section 01 checks in `../01-data-analysis-in-databricks/facilitator-guide.md`.
2. Import `facilitator-demo.py` and `participant-lab.py` into `/Workspace/Shared/hc_workshop/02-generative-ai-in-databricks`.
3. Clone `facilitator-demo.py` into your user folder. Use this personal clone for the live demo.
4. Create a second clone, complete the regional analysis and error repair, and keep it ready as the notebook fallback.
5. With a participant-equivalent identity, confirm:
   - Genie Code is visible in a notebook;
   - Serverless compute can run the reference Metric View query;
   - `hc_workshop.workshop_shared.fpd_metrics` appears in the `@` resource picker;
   - Genie Code can propose notebook edits and query execution;
   - the shared starter can be cloned into the user's workspace folder.
6. Confirm the reference result is approximately 42.26% for the promotion and 21.03% for other eligible originations.
7. Create a disposable draft dashboard named **Genie Code Demo — FPD5 Overview** and confirm Genie Code for dashboard authoring is available. Keep a completed unpublished draft as the fallback.
8. Confirm a participant-equivalent identity can read `hc_workshop.workshop_shared.fpd_analysis` from PySpark and run the intentionally flawed validation helper.
9. For the optional extension, confirm the private **Unicorn FPD5 Investigator — `<workspace_username>`** created in Section 01 can be opened and edited with Genie Code.
10. Rehearse the optional Agent-improvement flow with a disposable private Agent in the demonstration account, then delete it so Section 01 starts from creation.
11. For the optional extension, confirm participant Agents remain in their respective user folders and are not shared with other participants.

Genie Code output is nondeterministic. Rehearse the path and the review decisions, but do not depend on exact wording or an exact set of generated cells.

## Minute-by-minute run of show

| Time | Minutes | Mode | Activity | Observable result |
|---|---:|---|---|---|
| 11:15–11:20 | 5 | Watch me | Frame the context → outcome → review → validation loop and explain inherited SQL | Participants can identify what Genie Code accelerates and what they still own |
| 11:20–11:32 | 12 | Run with me | Generate and refine the governed regional analysis | A correct regional result and chart reconcile to the promotion baseline |
| 11:32–11:44 | 12 | Try it | Diagnose and repair the inherited PySpark denominator bug; add checks | Rates reconcile and the generated assertions pass |
| 11:44–11:49 | 5 | Run with me | Use `/optimize` and `/doc` with review discipline | Participants accept only justified, result-preserving changes |
| 11:49–12:01 | 12 | Watch me | Build and validate the unpublished AI/BI Dashboard | Dashboard datasets, filters, and values reconcile with the notebook |
| 12:01–12:07 | 6 | Operate it | Review permissions, approval boundaries, diffs, rerun safety, and recovery | Participants can name one approval and one recovery decision |
| 12:07–12:12 | 5 | Optional | Curate and regression-test the private Genie Agent, or use as buffer | Agent behavior improves without breaking the cohort question |
| 12:12–12:15 | 3 | Checkpoint | Choose a next-week use case and state its validation check | Each participant identifies one concrete daily workflow |

Protect the required notebook, PySpark, dashboard, and checkpoint activities. If the session slips, omit the optional Agent extension rather than compressing validation.

## Four required items for the session

### 1. Understand inherited work faster

Open `participant-lab.py` and run the inherited cohort query. Attach the query and output with `@cell`, attach `fpd_metrics`, and use the explanation prompt from the notebook.

Ask participants to check whether Genie Code correctly explains:

- the result grain;
- the governed measures and denominator;
- `GROUP BY ALL`;
- percentage conversion.

The productivity message is not “start from blank.” It is “reduce the time needed to understand work you inherited without skipping verification.”

Observable checkpoint: participants can explain the query before changing it.

### 2. Generate and iterate on an analysis

Introduce the reusable prompt structure: **goal, context, constraints, output, and validation**.

Ask participants to:

1. Clone `participant-lab.py` into their user folder.
2. Attach the Metric View and inherited query.
3. Paste the regional-extension prompt.
4. Review the proposed plan before approval.
5. Let Genie Code add and run the cells.
6. Give a targeted follow-up if one detail is wrong.
7. Compare the result with the independent checkpoint.

Circulate and check that the 20-contract threshold is applied at the regional grain and that the comparison uses the overall promotion rate.

If generation stalls, use the completed notebook clone. Do not sacrifice the remaining productivity workflows while waiting.

Observable checkpoint: each participant has a valid regional result and can identify the five parts of the prompt.

### 3. Explain, diagnose, and improve existing code

Participants continue in their notebook:

1. Run the inherited PySpark validation helper and observe the suspicious 100% rates.
2. Attach the function and output with `@cell`.
3. Ask Genie Code to explain and repair the denominator bug without redefining FPD5.
4. Review the proposed diff before acceptance.
5. Rerun the repaired helper and the generated lightweight assertions.
6. Reconcile the result with the Metric View reference.
7. Use `/optimize` on the generated regional query.
8. Accept a change only if it preserves the validated result and has a material rationale.
9. Use `/doc` to add a concise explanation of the grain, denominator, and threshold.

The correct PySpark repair removes the `fpd5_flag = 1` filter before aggregation. It retains the full eligible-contract population as the denominator, uses the existing `fpd5_flag` only as the numerator, and does not recreate the governed date logic.

Make the performance point explicit: a suggestion is a hypothesis. Query Profile evidence is required before claiming a material performance improvement.

Observable checkpoint: participants have personally used Genie Code to understand SQL, generate analysis, repair PySpark, add executable checks, and improve code.

### 4. Build a simple AI/BI Dashboard

Open the disposable **Genie Code Demo — FPD5 Overview** draft dashboard and use the dashboard prompt from `facilitator-demo.py`.

Show how Genie Code:

- plans the dashboard;
- reuses the governed Metric View;
- creates datasets and visualizations;
- adds a filter;
- arranges the page.

Review the plan before allowing changes. When the draft is complete, reconcile its KPI values with the notebook, verify the store threshold and filter behavior, and leave it unpublished.

This is a focused showcase, not another participant build. If dashboard authoring stalls, open the completed unpublished fallback and review what Genie Code created.

Observable checkpoint: participants can name which dashboard-authoring steps were automated and which publication checks remain with the author.

### Optional extension — Iteratively improve the Section 01 Genie Agent

Run this only after the required notebook and dashboard checkpoints. Participants already learned what a Genie Agent is in Section 01. This activity focuses on how technical practitioners use Genie Code to maintain one as requirements evolve.

Each participant:

1. Opens **Unicorn FPD5 Investigator — `<workspace_username>`**, the private Agent created in Section 01.
2. Confirms that it is in their user folder, is not shared with another participant, and uses only `fpd_metrics`.
3. Runs the baseline store-associate question from `participant-lab.py`.
4. Opens Genie Code from the response and supplies the new risk-team response requirements.
5. Reviews every proposed instruction, metadata, or example-SQL change.
6. Accepts only the smallest changes needed.
7. Starts a fresh chat and reruns the target question.
8. Reruns the cohort-comparison question as a regression check.

Every participant edits only their own Agent. There is no shared source Agent and no cloning step.

The baseline may already satisfy some requirements. That is acceptable: the stakeholder requirement still makes the expected behavior explicit. Do not add duplicated FPD5 formulas or broad instruction blocks simply to create a visible diff.

Optional checkpoint: each participant's private Agent meets the new response requirements, remains unshared, and still returns approximately 42.26% versus 21.03% for the regression question.

## Likely errors and shortest recovery

### Genie Code is not visible

This is usually a workspace enablement, entitlement, or availability issue, not a notebook defect. Use the completed fallback notebook for the notebook activities and have the participant follow the facilitator's Agent walkthrough. Record the identity and setting for follow-up after the session.

### The Metric View does not appear in the resource picker

Confirm `USE CATALOG`, `USE SCHEMA`, and `SELECT` privileges. Open the Metric View in Catalog Explorer to distinguish an access issue from resource-picker discovery. If access is valid, paste the fully qualified name in the prompt and retry attaching context.

### Genie Code proposes raw-table logic

Do not approve it. Reply:

> Use only `hc_workshop.workshop_shared.fpd_metrics` and its governed measures. Do not reimplement FPD5 from raw tables.

### Genie Code proposes a write

Do not approve it. Restate the read-only constraint and explicitly prohibit `CREATE`, `REPLACE`, `INSERT`, `UPDATE`, `DELETE`, and `MERGE`.

### Generated rates do not match the reference

Check, in order:

1. source is `fpd_metrics`;
2. cohort is grouped by `promotion_cohort`;
3. measures are invoked with `MEASURE(...)`;
4. no extra filter changed the eligible population;
5. rate conversion multiplies by 100 only for display.

Use the correction prompt in the facilitator notebook.

### Notebook edits do not appear or generation takes too long

Confirm the user is in a writable personal clone. Retry once in the same conversation. If it still fails, move to the completed facilitator clone and keep the session on schedule.

### The PySpark helper still reports 100%

Inspect the repaired helper for a filter on `fpd5_flag` before `groupBy`. The full source population from `fpd_analysis` must reach the aggregation. Use the contract count as the denominator and `SUM(fpd5_flag)` as the numerator.

### PySpark cannot read the governed analysis view

Confirm that the notebook uses Serverless notebook compute or approved Unity Catalog-compatible all-purpose compute. Then verify `USE CATALOG`, `USE SCHEMA`, and `SELECT` on `hc_workshop.workshop_shared.fpd_analysis`.

### Dashboard authoring is unavailable or stalls

Confirm Genie Code for dashboard authoring is enabled, the facilitator has Databricks SQL access, and the selected warehouse is usable. Switch to the completed unpublished draft if the live build cannot finish.

### Dashboard values do not reconcile

Check that the dashboard reused `fpd_metrics`, invoked governed measures, applied the store threshold before ranking, and did not multiply an already formatted percentage. Do not publish the draft.

### The optional Agent extension cannot be opened or edited

Confirm that Section 01 created the Agent in the participant's user folder, the current user owns it, and the participant has Databricks SQL access, `CAN USE` on the selected Pro or Serverless SQL warehouse, and `SELECT` on `fpd_metrics`. If this cannot be fixed immediately, skip the optional extension for that participant. Do not introduce a shared fallback Agent.

### A participant accidentally shared their Agent

Open **Share**, remove grants to other participants, the workshop group, or **All account users**, and confirm the Agent is in the creator's user folder before continuing.

### Genie Code proposes duplicating the FPD5 formula

Reject the change. FPD5 belongs in the Metric View. Agent context should add response behavior or a verified query shape without creating a second metric definition.

## Deliberate omissions

- Genie Agent curation is optional. Participants do not create or clone another Agent; if time permits, they continue with the private Agent created in Section 01.
- Participants do not create or modify data tables.
- Participants do not build the AI/BI dashboard themselves.
- The facilitator dashboard remains an unpublished disposable draft.
- Benchmarks and Genie One are outside this productivity-focused hour.
- Elevated FPD5 remains a synthetic investigation signal, not a fraud or causality conclusion.
