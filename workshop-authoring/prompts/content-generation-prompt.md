# Workshop content-generation prompt

**Updated at:** 2026-09-20

*Master prompt for creating, reviewing, or improving one workshop section at a time.*

## Use

Copy the prompt below and complete the input values.

- Use `CREATE` to author a new section.
- Use `REVIEW` to receive findings and a proposed participant journey without changing files.
- Use `REVIEW_AND_FIX` to review and implement the improvements.

The prompt is intentionally strict about participant experience. It prioritizes clarity, one connected story, small learning steps, and a minimal participant-facing file set.

## Prompt

````text
Create, review, or improve one section of the Home Credit Philippines Databricks workshop.

The participant experience is the primary design constraint. Build one clear journey around one business or operational assignment. Do not create a catalogue of product features.

Assume that:

- participants may be new to the lending domain;
- participants may be using Databricks for the first time;
- English may not be their first language; and
- technically correct language can still be too difficult.

Simplicity and clarity are more important than sounding technical.

## Inputs

TASK_MODE: [CREATE | REVIEW | REVIEW_AND_FIX]

REPOSITORY_ROOT: [absolute path to this repository]
WORKSPACE_ROOT: /Workspace/Shared/hc_workshop
WORKSHOP_CATALOG: hc_workshop
WORKSHOP_RUNTIME: [confirmed value or TBD]
SQL_WAREHOUSE: [confirmed value or TBD]
FACILITATOR_GROUP: [confirmed value or TBD]
OBSERVATION_DATE: 2026-09-01
DATASET_CONFIGURATION: [generator version 1.1.0, standard scale, master seed 20260922; or describe the approved alternative]

SECTION_NUMBER: [section number]
SECTION_NAME: [section name]
SECTION_DURATION_MINUTES: [agenda duration]
DELIVERY_MODE: [NOTEBOOK_LED | FACILITATOR_LED]

PARTICIPANT_BACKGROUND:
- [what participants already know]
- [what may be new to them]

SECTION_TOPICS:
- [topic that must be covered]
- [topic that must be covered]

BUSINESS_OR_OPERATIONAL_ASSIGNMENT:
[The question participants must answer or the outcome they must deliver. Leave blank only when it must be derived from the canonical story.]

FINAL_PARTICIPANT_DELIVERABLE:
[The saved result, decision, explanation, asset, or handover evidence participants produce.]

If an environment value is unknown:

- write `TBD — facilitator confirmation required` in maintainer or setup material;
- do not invent IDs, permissions, enabled features, runtimes, URLs, groups, warehouse names, or test results; and
- do not release participant instructions containing unresolved placeholders.

## Read first

Paths are relative to `REPOSITORY_ROOT`:

1. `workshop-authoring/story/unicorn-finance-story.md`
2. `workshop-authoring/agenda/workshop-agenda.md`
3. `workshop-authoring/dataset/dataset-design.md`
4. `workshop-authoring/dataset/dataset-guide.md`
5. `workshop-authoring/dataset/data-dictionary.md`
6. `workshop-authoring/dataset/source-schema.md`
7. `workshop-setup/dataset-generator/README.md`
8. Existing files for the selected section
9. Setup or downstream assets that depend on the selected section

Treat the implemented dataset, setup logic, and tested business definitions as more authoritative than broad agenda wording.

Preserve all unselected sections and unrelated user changes.

## Canonical workshop story

**Unicorn Finance Philippines — Credit with a little magic**

Unicorn Finance is a fictional consumer lender. Nova Mobile and Atlas Ridge Consulting are also fictional. Atlas Ridge built Unicorn Finance's Databricks platform and is handing it to Unicorn Finance's internal team.

Nova Mobile ran a promotion for selected smartphones:

1. A customer chose a phone at a participating store.
2. The customer applied for a Unicorn Finance point-of-sale installment loan.
3. If approved, the customer was scheduled to repay the amount borrowed over 6, 9, or 12 monthly payments.
4. The customer paid 0% monthly interest.
5. Nova Mobile paid Unicorn Finance a subsidy to support the 0% offer.

The phone was not free. A processing fee or down payment could still apply. Approval was not guaranteed.

The campaign uses:

- promotion code `ZERO_SMARTPHONE_2026`;
- product label `Unicorn 0% Brand Promotion`;
- analysis label `0% smartphone promotion`; and
- comparison label `Other eligible originations`.

When participants see `Other eligible originations`, explain that **origination** means a loan that was created.

Loan applications increased during the promotion period. Some stores and salespeople also had more first-payment problems.

This is a reason to investigate. It is not proof that:

- the promotion caused the increase;
- a store or salesperson caused a late payment;
- fraud occurred; or
- the synthetic data represents Home Credit production systems.

The fictional names, products, controls, data, and outcomes must not be presented as real Home Credit products, processes, controls, or confirmed business results.

Use one connected story across the workshop:

1. Find and understand the inherited assets.
2. Investigate the promotion and first-payment problem.
3. Ask questions with Genie and check the generated SQL.
4. Turn selected logic into a repeatable job or pipeline.
5. Protect sensitive data and inspect lineage.
6. Train, register, and batch-score an FPD model.

## Canonical FPD5 definition

FPD5 stands for **First Payment Default at five days past due**.

An installment is one scheduled monthly payment.

For this workshop:

- use only `installment_no = 1`;
- a loan becomes eligible on `due_date + 5 days`;
- use `OBSERVATION_DATE` as the declared as-of date;
- include it only when `date_add(due_date, 5) <= OBSERVATION_DATE`;
- a null settlement date counts as FPD5;
- settlement on or after `due_date + 5 days` counts as FPD5; and
- settlement before day five does not count as FPD5.

Payment on day five counts as FPD5.

Here, default only describes the first payment at day five. It does not mean that the whole loan was never repaid.

The FPD5 rate is:

```text
number of eligible loans with FPD5 / total number of eligible loans
```

Never calculate the rate from:

- all applications;
- all approvals;
- all created loans regardless of age; or
- only the loans that already have FPD5.

Build exactly one row per eligible fixed-term credit contract. Validate that `contract_id` is unique before calculating counts or rates. Do not join first installments directly to multiple payment rows.

The standard reference values below apply only when:

- `OBSERVATION_DATE` is `2026-09-01`; and
- `DATASET_CONFIGURATION` uses generator version `1.1.0`, standard scale, and master seed `20260922`.

Standard reference values:

- top-20% store application share: approximately 81.13% of all applications where `store_id` is not null;
- promotion FPD5 rate: approximately 42.26%; and
- other eligible-loan FPD5 rate: approximately 21.03%.

Do not reveal expected answers before participants complete the discovery step.

## Data and asset model

Use three schemas in `WORKSHOP_CATALOG`:

- `<WORKSHOP_CATALOG>.core_lending` — shared source tables; read-only for participants.
- `<WORKSHOP_CATALOG>.workshop_shared` — facilitator-owned shared views and Metric Views.
- `<WORKSHOP_CATALOG>.workshop_labs` — participant-created tables, views, and registered models.

The source contains:

- `customer`
- `retail_location`
- `loan_product`
- `loan_application`
- `credit_contract`
- `installment`
- `payment`
- `collection_action`

Use only columns and values defined in the data dictionary.

Do not:

- modify `core_lending`;
- use `main`, `hive_metastore`, or personal catalogs;
- create a schema per participant;
- treat a naming prefix as a security boundary; or
- add events or relationships that the dataset does not contain.

Use fully qualified names in notebook SQL and Unity Catalog DDL.

Name persistent participant assets:

```text
unicorn_<runner_id>_<asset>
```

Build `runner_id` automatically from:

- a sanitized username prefix; and
- a short deterministic hash of the full workspace identity.

The result must begin with a letter and contain only lowercase letters, numbers, and underscores. Never ask participants to enter an identifier manually.

Prefer a temporary view when the result does not need to survive the notebook session.

Cleanup may remove only assets with the current participant's exact prefix. Never use a broad wildcard or cleanup command that can remove another participant's asset.

Notebooks, jobs, pipelines, dashboards, experiments, and Genie Agents are workspace assets. They are not catalog objects.

`WORKSPACE_ROOT` is the shared location for workshop notebooks and other intentionally shared workshop material. It is not the location for private participant Genie Agents.

Create each participant's Genie Agent in that participant's `/Workspace/Users/<workspace-username>` folder. Keep it unshared with other participants.

## Non-negotiable participant-experience rules

### 1. Start with the assignment

At the beginning, explain:

- the business situation;
- the participant's role;
- the questions they will answer;
- the final item they will produce; and
- the safety or interpretation boundary.

Do this before discussing Databricks products.

For an unfamiliar business process, show a short numbered example before introducing its data fields.

### 2. Use plain English

Use:

- short sentences;
- one idea per sentence;
- common verbs such as `check`, `count`, `compare`, `save`, and `find`;
- direct questions as section titles;
- the same term consistently; and
- examples before formulas.

Avoid unnecessary synonyms and abstract noun phrases.

Do not write phrases such as:

- `establish the origination context`;
- `examine repayment outcomes`;
- `derive a cohort label`;
- `profile several fields`;
- `materially different population`;
- `operationalize the analytical asset`; or
- `reconcile governed semantics`.

Prefer:

- `see where customers applied`;
- `check whether the first payment was late`;
- `label the promotion applications`;
- `group and count the rows`;
- `check whether the groups look different`;
- `save the result for the next analyst`; and
- `check that the answers match`.

When a technical term is necessary, explain it immediately:

- **point of sale:** the loan is offered when the customer buys the item;
- **installment:** one scheduled monthly payment;
- **cohort:** a group;
- **grain:** what one row represents;
- **denominator:** the total used to calculate a rate;
- **Metric View:** a shared business calculation stored in one place;
- **queue:** a query is waiting because compute is busy;
- **spill:** a query needed more memory and temporarily used disk; and
- **lineage:** where data came from and what uses it.

Do not assume that a technically familiar word is clear to a first-time reader.

### 3. Organize around questions, not products

Each part must answer one business or operational question.

Good titles:

- `What data did we receive?`
- `Where did customers apply?`
- `Which loans are old enough to check?`
- `Was FPD5 higher for the promotion?`
- `Which places need a closer look?`
- `How do we save the result?`
- `Does the dashboard show the same answer?`

Weak titles:

- `Explore with PySpark`
- `SQL analysis`
- `Delta Lake`
- `Metric Views`
- `Genie`

PySpark, SQL, Delta, dashboards, and Genie support the story. They are not the story.

Before each major step, use one or two short sentences to explain:

1. what question it answers;
2. why the answer is needed; or
3. how it leads to the next step.

Do not repeat all three points when one clear sentence is enough.

After a result that requires interpretation, tell participants what to notice and what they must not conclude.

### 4. Keep one primary participant entry point

For a notebook-led section:

- the notebook is the participant source of truth;
- embed instructions, exercises, UI steps, validation, expected checkpoints, and reflection in the notebook;
- do not require participants to switch between the notebook, README, exercises, and expected-results files; and
- distribute only the files participants actually use.

For a facilitator-led section:

- use one integrated participant guide or worksheet;
- keep the assignment, evidence capture, exercise, and reflection together; and
- do not expose facilitator demonstration code as participant work.

Create a separate participant file only when participants genuinely use it independently of the primary entry point.

### 5. Separate participant, facilitator, and administrator content

Participant material must not contain:

- setup or rehearsal steps;
- facilitator timing recovery;
- administrator grants or cleanup;
- presenter cues;
- fallback demonstrations;
- answers revealed before the exercise;
- unresolved `TBD` values; or
- references to files participants cannot access.

Store:

- runnable participant material under `workshop-content/`;
- maintainer README files, facilitator guides, expected outputs, troubleshooting, and slide-authoring material under `workshop-authoring/sections/`; and
- environment setup under `workshop-setup/`.

Remove temporary slide outlines after their useful content is transferred to the final slide source.

### 6. Make notebook blocks small and teachable

A good notebook sequence is:

1. Markdown: ask one question and explain why it matters.
2. Code: perform one meaningful action.
3. Output: show the evidence needed for that question.
4. Markdown: explain what to notice.
5. Transition: state why the next question follows.

Keep each code cell:

- short enough to explain without scrolling through several unrelated operations;
- complete;
- sequential;
- safe to rerun;
- limited to one learning purpose; and
- free of unrelated output fields.

Split cells that combine several ideas, such as:

- creating a name;
- writing a table;
- capturing a version;
- changing a schema;
- updating data;
- comparing versions; and
- showing history.

Do not ask participants to type large prepared code blocks.

Keep configuration visible near the top.

Use comments and output labels that a participant can understand.

Remove a displayed field when the participant does not need it to answer the current question.

### 7. Make participant actions meaningful

A participant exercise must do more than rerun prepared code.

Ask participants to:

- change a meaningful grouping, parameter, rule, or filter;
- compare counts and percentages;
- explain what changed;
- identify uncertainty;
- record a follow-up question; or
- produce a saved result used later.

State:

- the timebox;
- the exact action;
- what to record;
- how to know the task is complete; and
- what conclusions are not supported.

Use a writing template when participants need to summarize evidence.

Keep expected numeric answers hidden until after the discovery step.

### 8. End with reflection, not a facilitator quiz

Use participant-facing language:

- `Before finishing, check that you can answer...`
- `What should you understand?`
- `Choose one item and write down...`

Ask participants to identify:

- who owns an item;
- one thing that could go wrong; and
- how they would check or fix it.

Do not place facilitator cleanup or delivery logistics in the participant reflection.

## Scope control

Create or change only the selected section and the references that directly depend on it.

- Treat `SECTION_TOPICS` as the curator's scope.
- Do not add a product merely because it appears elsewhere in the agenda.
- Do not add cross-sell analysis; the dataset has no offer-response event.
- Prefer the minimum number of products needed to complete the assignment.
- Use current Databricks names and current APIs.
- Do not use legacy `dlt` or `LIVE` syntax for Lakeflow Spark Declarative Pipelines.
- Do not invent product behavior, workspace UI, permission behavior, or feature availability.
- Ask a focused question only when the supplied topics cannot form a safe, runnable section.

## Databricks and technical correctness

### Compute

- Notebook Python and `spark.sql` run on the notebook's attached compute.
- A `%sql` cell in a mixed Python notebook also uses the notebook's attached compute.
- Dashboards and Genie Agents use a SQL warehouse.
- Do not tell participants to look for notebook Spark queries in SQL warehouse Query History.
- Jobs compute is for automated tasks; all-purpose compute is primarily interactive.
- Serverless reduces infrastructure work. It does not remove ownership of code, access, quality, cost, or monitoring.

### Unity Catalog and permissions

- Use the canonical catalog and schemas.
- Keep source data read-only.
- Explain workspace permissions separately from Unity Catalog data permissions.
- Do not imply that an object name or user-folder location is an absolute security boundary.
- Store a private participant Genie Agent in `/Workspace/Users/<workspace-username>`, not under `/Workspace/Shared`.
- A private participant Genie Agent must remain unshared with other participants. Workspace administrators may still have access.

### Metrics, dashboards, and Genie

- Keep one shared FPD5 definition.
- Use `<WORKSHOP_CATALOG>.workshop_shared.fpd_metrics` as the shared Metric View for FPD5 dashboards and Genie Agents.
- Use Metric View measures through `MEASURE(...)`.
- Use `fpd_metrics` as the participant Genie Agent's only data source unless a section explicitly requires another governed source.
- Do not duplicate the formula in dashboard widgets or Agent instructions.
- If `fpd_metrics` is required but unavailable, stop the participant path and restore it through facilitator setup. Do not silently recalculate FPD5 from raw tables.
- Verify dashboard SQL before treating a dashboard as complete.
- Verify generated SQL before trusting a written answer.
- Show counts beside percentages.
- State minimum group sizes used for rankings.
- Distinguish a high application count from a high FPD5 percentage.
- Distinguish timing from causation.
- Use exact confirmed warehouse and group names in released participant instructions.

### Delta

- Persist a result only when another person or process needs it later.
- Explain each write or schema change before running it.
- Make rerun behavior explicit.
- Explain that table history helps inspect changes.
- Explain that old-version access depends on retained files and is not a backup.

### Machine learning

- Keep batch scoring as the required path.
- Treat serving as optional unless the section assignment requires it.
- Avoid target leakage.
- Explain metrics and predictions in business language before introducing technical names.

## Delivery pattern

Every section must fit its agenda duration:

1. **Assignment** — explain the role, problem, questions, and final output.
2. **Understand** — introduce only the business and technical ideas needed for the assignment.
3. **Investigate together** — run short steps that answer the questions in order.
4. **Participant action** — change or extend a meaningful part of the work.
5. **Save or operate** — inspect ownership, access, dependencies, history, monitoring, or recovery because the assignment requires it.
6. **Reflection** — explain the result, uncertainty, owner, possible problem, and check or fix.

Prefer one complete workflow over maximum feature coverage.

Move disconnected comparisons, optional products, and advanced operations to facilitator reference material unless they directly support the assignment.

## Required outputs

Create the smallest useful participant-facing surface.

For a notebook-led section:

```text
workshop-content/<section-number>-<section-name>/
└── participant-lab.py  # or .sql
```

For a facilitator-led section:

```text
workshop-content/<section-number>-<section-name>/
└── participant-guide.md
```

Add another participant file only when independent use is necessary.

Create these standard authoring files:

```text
workshop-authoring/sections/<section-number>-<section-name>/
├── README.md
└── facilitator-guide.md
```

The facilitator guide must include:

- a minute-by-minute run of show;
- setup and rehearsal checks;
- expected results;
- likely errors;
- the shortest safe recovery path;
- fallbacks for optional features;
- checks that must not be skipped when time runs short; and
- participant-equivalent permission requirements.

Create these only when they add value outside the notebook or facilitator guide:

```text
expected-results.md
generate-...-slides.md
```

Do not create boilerplate files merely to complete a template.

Add section-specific setup files only when needed.

Update references when files are moved or removed. Do not leave stale links.

Update `workshop-content/README.md` status.

## Task-mode workflow

### CREATE

1. Read the required sources.
2. Define the assignment and final deliverable.
3. Design the participant journey.
4. Create the smallest required file set.
5. Validate the result.

### REVIEW

Do not edit files.

Return:

1. findings ordered by severity;
2. proposed participant journey;
3. files to keep, move, consolidate, or remove;
4. what should remain unchanged; and
5. validation or setup gaps.

Include unclear language, weak transitions, oversized blocks, and participant/facilitator boundary problems within the severity-ordered findings instead of repeating them in separate lists.

### REVIEW_AND_FIX

1. Perform the REVIEW workflow.
2. Preserve correct business logic and useful technical content.
3. Implement the improved journey.
4. Update all affected references and authoring guidance.
5. Validate the result.

Do not rewrite correct code merely to make the diff larger. Change code when it:

- conflicts with the explanation;
- shows unused or distracting fields;
- combines unrelated learning steps;
- is unsafe to rerun;
- uses an incorrect business rule; or
- prevents a clear participant workflow.

## Validation

Before finishing, complete all relevant checks.

### Participant read-through

Read the primary participant file from beginning to end as a first-time learner.

At every part, confirm the participant can answer:

- What am I doing?
- Why am I doing it?
- What should I notice?
- What should I do next?

Search for unexplained jargon and long sentences.

Check that headings describe questions or outcomes rather than products.

### Business correctness

- Compare the implementation with the canonical story and data dictionary.
- Check the exact FPD5 day-five boundary.
- Check the observation date.
- Check the numerator and denominator.
- Check what one row represents.
- Check minimum group sizes.
- Check that counts and percentages use the same population.
- Check that wording does not imply unsupported causation or fraud.

### Code and notebook structure

- Validate the Databricks source header.
- Validate every `COMMAND ----------` separator.
- Validate Python syntax.
- Validate SQL syntax when a runtime or parser is available.
- Check that code cells are sequential and safely rerunnable.
- Check that one cell does not teach several unrelated ideas.
- Check that displayed columns support the current question.
- Check participant-specific writes and cleanup boundaries.

### Files and references

- Validate local links.
- Search for references to removed or moved files.
- Confirm that the participant folder contains only participant assets.
- Confirm that facilitator and administrator instructions are outside the participant entry point.
- Preserve unrelated changes.

### Runtime

When workspace access is available:

- run the notebook cell by cell with participant-equivalent permissions;
- verify expected outputs;
- test a clean rerun;
- test the participant exercise;
- verify dashboard filters and permissions;
- verify Genie data sources, sharing, generated SQL, and answer;
- inspect a real Query Profile; and
- record the exact workspace, runtime, warehouse, and identity used.

When runtime access is unavailable, say clearly that the asset was not executed in Databricks.

Never claim a test passed when it was not run.

## Final response

For `REVIEW`, return the requested review structure and no implementation claim.

For `CREATE` or `REVIEW_AND_FIX`, list:

- participant experience created or changed;
- files created, moved, consolidated, or removed;
- important business or technical decisions;
- checks run and their results;
- runtime validation status;
- unresolved setup values; and
- deliberate omissions.

Do not paste complete generated files into chat.
````

## Recommended workshop generation order

Generate or validate Section 01 first. Its FPD5 definition and trusted results feed later sections.

Then generate dependent sections in agenda order so each section reuses the same story, definitions, and saved assets.
