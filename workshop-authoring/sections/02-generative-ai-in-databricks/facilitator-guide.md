# Facilitator guide — Generative AI in Databricks

**Duration:** 60 minutes
**Participant entry point:** [`participant-lab.py`](../../../workshop-content/02-generative-ai-in-databricks/participant-lab.py)
**Facilitator demo:** [`facilitator-demo.py`](facilitator-demo.py)

## Teaching intent

Keep one business story throughout: a developer must extend Unicorn Finance's governed regional FPD5 investigation, repair an inherited validation utility, and hand over evidence another developer can trust.

The working pattern is:

> Context → concrete outcome → review → execution → governed reconciliation

Genie Code can propose and execute work. The participant remains responsible for population, denominator, permissions, semantic correctness, evidence, and approval.

## Before the session

1. Complete the Section 01 checks.
2. Import only `participant-lab.py` into the participant-facing Section 02 workspace folder.
3. Keep `facilitator-demo.py`, this guide, expected results, and fallback assets outside that folder.
4. Confirm a participant-equivalent identity can:
   - clone the notebook into a user folder;
   - use Serverless notebook compute;
   - read `fpd_metrics` and `fpd_analysis`;
   - attach the Metric View with `@`;
   - use Genie Code Agent mode with approval prompts; and
   - approve notebook edits and cell execution.
5. Confirm the governed baseline and six-region checkpoint in [`expected-results.md`](expected-results.md).
6. Prepare and rehearse a disposable unpublished dashboard using a usable SQL warehouse.
7. Keep a completed personal notebook clone and completed unpublished dashboard as facilitator fallbacks.
8. For the optional extension, confirm participant-created Agents remain private and editable by their owners.

## Run of show

| Time | Minutes | Mode | Business purpose | Observable result |
|---|---:|---|---|---|
| 11:15–11:20 | 5 | Frame | Assign the risk-analytics handover and refresh FPD5 eligibility | Participants can state the population, denominator, date, and caveat |
| 11:20–11:27 | 7 | Run with me | Establish what the inherited governed query already proves | Participants verify one Genie Code explanation |
| 11:27–11:39 | 12 | Try it | Identify qualifying promotion-region signals | Generated result includes counts, rate, threshold, and chart |
| 11:39–11:44 | 5 | Validate | Reconcile every generated region with the governed checkpoint | Six rows reconcile; top region and baseline are correct |
| 11:44–11:54 | 10 | Try it | Repair the validation utility and add executable checks | Rates reconcile and checks pass |
| 11:54–11:59 | 5 | Operate it | Document handover and assess `/optimize` suggestions | Only justified, result-preserving changes are accepted |
| 11:59–12:08 | 9 | Watch me | Turn validated evidence into an unpublished dashboard draft | Participants complete the dashboard observation checklist |
| 12:08–12:12 | 4 | Optional | Apply and regression-test one private-Agent requirement | Target and cohort questions pass |
| 12:12–12:15 | 3 | Reflect | Record owner, risk, recovery, and next-week use | Each participant leaves with an operating commitment |

If time slips, omit the optional Agent extension. Do not compress governed reconciliation or reflection.

## Delivery guidance

### Assignment and definition refresh

Have participants clone before running anything. Ask one person to explain why an August 30 first installment is not eligible on September 1. Correct population misunderstandings before opening Genie Code.

### Inherited baseline

Participants should ask for an explanation, not a rewrite. Verify that Genie Code identifies:

- one row per promotion cohort;
- governed `MEASURE(...)` expressions;
- eligible contracts as denominator;
- `GROUP BY ALL`; and
- multiplication by 100 as display conversion.

### Regional extension

Review the plan before approval. The 20-contract condition must be applied at regional grain after filtering to the promotion cohort. Make clear that the threshold is a workshop stability rule, not part of FPD5 and not proof of statistical significance.

After generation, participants run the pre-authored checkpoint. If results disagree, stop and correct the generated work before interpreting it.

### PySpark repair

Let participants observe the 100% result before naming the bug. The correct repair removes the pre-aggregation `fpd5_flag` filter, retains the full eligible population, and reuses the existing flag only as numerator.

Generated checks must compare with a live read-only Metric View query rather than rely only on copied constants.

### Dashboard handover

State explicitly that **Genie Code Demo — FPD5 Overview** is a disposable draft and is separate from Section 01's prepared **Unicorn FPD5 Overview**.

Use [`facilitator-demo.py`](facilitator-demo.py) for the prompt. Ask participants to use the observation checklist in their notebook. Reconcile before discussing visual polish and leave the dashboard unpublished.

### Optional private Agent

Participants edit only the Agent they created in Section 01. The Agent's Pro or Serverless SQL warehouse is distinct from notebook compute. Accept the smallest context change and retest both target and regression questions in fresh conversations.

## Technical boundaries

- Notebook SQL and PySpark run on notebook compute.
- AI/BI dashboard datasets and Genie Agent questions use SQL warehouses.
- Do not imply notebook `%sql` appears in SQL warehouse Query History.
- Generated analytical SQL uses only `fpd_metrics`.
- The PySpark helper reads only `fpd_analysis`.
- No participant action writes or replaces workshop data.
- FPD5 remains governed by the Metric View source and is never recreated in Agent instructions.

## Recovery

- **Genie Code unavailable:** switch to the completed facilitator clone and have participants review decisions and invariants.
- **Metric View unavailable:** verify `USE CATALOG`, `USE SCHEMA`, and `SELECT`; stop rather than duplicating logic from raw tables.
- **Regional mismatch:** check source, promotion filter, grain, `HAVING`, denominator, and percentage conversion.
- **PySpark remains 100%:** inspect for any pre-aggregation `fpd5_flag` filter.
- **Dashboard authoring stalls:** use the completed unpublished draft and perform reconciliation.
- **Agent cannot be edited:** skip the optional extension; do not introduce a shared fallback Agent.

## After the session

Delete the disposable facilitator dashboard and personal demonstration artifacts. Do not ask participants to perform facilitator cleanup.
