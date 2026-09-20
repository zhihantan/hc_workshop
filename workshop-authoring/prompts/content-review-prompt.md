# Workshop content-review prompt

**Updated at:** 2026-09-20

*Master prompt for reviewing completed workshop assets without editing them.*

## Use

Copy the prompt below and complete the input values.

Use this after a section, notebook, participant guide, facilitator guide, slide brief, setup asset, dashboard specification, or Agent workflow has been created.

This prompt is review-only. It produces evidence-based findings and a recommended fix order. Use `content-generation-prompt.md` in `REVIEW_AND_FIX` mode after the review is accepted.

## Prompt

````text
Review completed Home Credit Philippines Databricks workshop assets.

Do not edit, move, create, or delete files.

Do not change Databricks resources, permissions, dashboards, Agents, jobs, pipelines, models, or data.

The purpose of this review is to determine whether the assets are:

- easy to understand;
- correct;
- safe;
- connected by one clear story;
- appropriate for the available time;
- usable by participants without unnecessary context switching; and
- ready for workspace validation or release.

Assume that:

- participants may be new to lending;
- participants may be new to Databricks;
- English may not be their first language; and
- technically correct content may still be too difficult.

Simplicity and clarity are release requirements, not optional style preferences.

## Inputs

REPOSITORY_ROOT: [absolute path to this repository]
WORKSPACE_ROOT: [/Workspace/Shared/hc_workshop or confirmed alternative]
WORKSHOP_CATALOG: [hc_workshop or confirmed alternative]
WORKSHOP_RUNTIME: [confirmed value or unknown]
SQL_WAREHOUSE: [confirmed value or unknown]
FACILITATOR_GROUP: [confirmed value or unknown]

REVIEW_TARGETS:
- [file, directory, notebook, or asset specification to review]
- [additional target when needed]

TARGET_TYPE: [COMPLETE_SECTION | PARTICIPANT_ASSET | FACILITATOR_ASSET | SETUP_ASSET | SLIDE_BRIEF | ASSET_SPECIFICATION]

SECTION_NUMBER: [section number or N/A]
SECTION_NAME: [section name or asset purpose]
SECTION_DURATION_MINUTES: [agenda duration or N/A]
DELIVERY_MODE: [NOTEBOOK_LED | FACILITATOR_LED | MIXED | N/A]

PARTICIPANT_BACKGROUND:
- [what participants already know]
- [what may be new to them]

EXPECTED_PARTICIPANT_OUTCOME:
[What participants should understand, decide, create, or hand over.]

OBSERVATION_DATE: 2026-09-01
DATASET_CONFIGURATION: [generator version 1.1.0, standard scale, master seed 20260922; or describe the approved alternative]

RUNTIME_EVIDENCE:
[NONE | describe workspace, identity, runtime, warehouse, execution results, screenshots, or logs already available]

REVIEW_DEPTH: [QUICK | STANDARD | THOROUGH]

If an input is unknown, state the gap. Do not invent the value.

## Applicability

Apply only standards relevant to `TARGET_TYPE`.

- `COMPLETE_SECTION`: apply every relevant standard.
- `PARTICIPANT_ASSET`: apply participant journey, language, code, task, business, technical, and file-boundary standards.
- `FACILITATOR_ASSET`: apply facilitator readiness, business, technical, timing, fallback, and participant-alignment standards.
- `SETUP_ASSET`: apply business logic, schema, permission, safety, rerun, dependency, and cleanup standards.
- `SLIDE_BRIEF`: apply plain-language, business-story, timing, early-answer, participant-alignment, and presenter-note standards.
- `ASSET_SPECIFICATION`: apply the business, technical, permission, ownership, and validation standards relevant to that asset.

For non-participant targets, read the related participant asset when one exists so that alignment can be checked. When no participant asset exists or a participant-specific standard does not apply, mark it `N/A` rather than inventing a participant journey.

## Review boundaries

This is a read-only review.

Allowed:

- read files;
- inspect local diffs and references;
- validate syntax without executing workshop writes;
- inspect existing runtime evidence;
- compare assets with canonical definitions;
- check local links; and
- identify missing runtime validation.

Not allowed unless the user separately authorizes it:

- editing files;
- running notebook cells that write data;
- creating or changing workspace assets;
- changing permissions;
- publishing dashboards;
- creating or sharing Genie Agents;
- deploying jobs or pipelines; or
- deleting participant or facilitator assets.

When a definitive review requires runtime execution, report the validation gap and the exact test that remains.

## Read first

Paths are relative to `REPOSITORY_ROOT`:

Read these at every review depth:

1. `workshop-authoring/prompts/content-generation-prompt.md`
2. `workshop-authoring/story/unicorn-finance-story.md`
3. `workshop-authoring/dataset/data-dictionary.md`
4. Every asset in `REVIEW_TARGETS`
5. The related primary participant asset when one exists

For `STANDARD`, also read:

6. `workshop-authoring/agenda/workshop-agenda.md`
7. `workshop-authoring/dataset/dataset-design.md`
8. `workshop-authoring/dataset/dataset-guide.md`
9. `workshop-authoring/dataset/source-schema.md`
10. `workshop-setup/dataset-generator/README.md`
11. The complete selected section, including facilitator and maintainer assets
12. Setup assets directly required by the participant path

For `THOROUGH`, also read:

13. Downstream sections that consume the selected section's data, labels, tables, models, dashboard, or Agent
14. Cross-repository references to files or assets that the selected section creates, moves, or deletes

Treat implemented dataset logic and tested business definitions as more authoritative than broad agenda wording.

Treat every applicable requirement in `content-generation-prompt.md` as a review criterion. The standards below make the most important checks explicit; they do not replace or narrow the generation prompt.

When a related participant journey exists, read it from beginning to end instead of reviewing isolated sentences.

## Severity levels

Use these severities consistently.

### Blocker

The asset is unsafe, cannot run, teaches a materially wrong rule, exposes data or assets incorrectly, or cannot achieve the participant outcome.

Examples:

- wrong FPD5 numerator or denominator;
- destructive cleanup that can affect another participant;
- participant instructions depend on a missing asset;
- private Agent is shared with participants;
- code cannot run in the stated environment; or
- participant steps require permissions they do not have.

### High

The participant can proceed, but the section teaches a wrong or seriously misleading concept, has a broken narrative, or contains a major delivery failure.

Examples:

- promotion wording implies unsupported causation;
- notebook and dashboard use different business definitions;
- a key term is never explained;
- a large cell hides several learning steps;
- participant material contains facilitator-only instructions; or
- notebook queries are incorrectly described as SQL warehouse queries.

### Medium

The content is usable but unnecessarily difficult, ambiguous, inconsistent, or likely to cause mistakes.

Examples:

- jargon-heavy explanations;
- weak transitions;
- unused result fields;
- unclear completion criteria;
- confusing file structure;
- missing minimum group size;
- unclear rerun behavior; or
- facilitator recovery guidance is incomplete.

### Low

A focused improvement would make the content easier to use, but it does not materially block learning or correctness.

Do not inflate preferences into findings. Every finding must identify a real participant, facilitator, correctness, safety, or maintenance impact.

## Evidence requirements

Every finding must include:

1. a unique ID using `B`, `H`, `M`, or `L` plus a number;
2. severity;
3. exact file path and line or section reference;
4. the current wording or behavior;
5. why it matters;
6. the participant, facilitator, technical, or safety impact; and
7. a concrete recommended change.

Do not write vague findings such as:

- `This could be clearer.`
- `Consider simplifying.`
- `The flow may be confusing.`

Instead, identify the exact confusing term, missing transition, incorrect behavior, or oversized block and propose simpler wording or structure.

Combine duplicate findings that have the same root cause.

## Review standard 1: One clear participant journey

Confirm that the primary participant asset begins with:

- the business situation;
- the participant's role;
- the questions to answer;
- the final participant deliverable; and
- the safety or interpretation boundary.

Confirm that the section follows one connected assignment.

For every major part, ask:

- What question does this part answer?
- Why is the answer needed?
- Does the result lead naturally to the next part?
- Is the participant producing evidence used later?

Flag:

- feature-tour structure;
- unrelated product demonstrations;
- abrupt transitions;
- code that does not support the assignment;
- exercises whose output is never used; and
- operational content added only because the product supports it.

Prefer question-based headings such as:

- `What data did we receive?`
- `Where did customers apply?`
- `Which loans are old enough to check?`
- `Was FPD5 higher for the promotion?`
- `Which places need a closer look?`
- `How do we save the result?`
- `Does the dashboard show the same answer?`

Flag headings that make the product the story, such as:

- `Explore with PySpark`
- `SQL analysis`
- `Delta Lake`
- `Metric Views`
- `Genie`

## Review standard 2: Plain English and accessibility

Read participant-visible text as someone who is new to both the domain and the dataset.

Check for:

- long sentences;
- several ideas in one sentence;
- abstract noun phrases;
- unexplained acronyms;
- unexplained lending terms;
- unexplained analytics terms;
- unexplained Databricks terms;
- different words used for the same concept;
- formulas shown before examples; and
- instructions that assume hidden UI or domain knowledge.

Flag phrases such as:

- `establish the origination context`;
- `examine repayment outcomes`;
- `derive a cohort label`;
- `profile several fields`;
- `materially different population`;
- `operationalize the analytical asset`;
- `reconcile governed semantics`;
- `change the analytical grain`; or
- `inspect the observable population`.

Prefer:

- `see where customers applied`;
- `check whether the first payment was late`;
- `label the promotion applications`;
- `group and count the rows`;
- `check whether the groups look different`;
- `save the result for the next analyst`;
- `check that the answers match`; and
- `group the loans in a different way`.

When a technical term is necessary, confirm that it is explained immediately:

- **point of sale:** the loan is offered when the customer buys the item;
- **installment:** one scheduled monthly payment;
- **cohort:** a group;
- **grain:** what one row represents;
- **denominator:** the total used to calculate a rate;
- **Metric View:** a shared business calculation stored in one place;
- **queue:** a query waits because compute is busy;
- **spill:** a query needed more memory and temporarily used disk; and
- **lineage:** where data came from and what uses it.

Check that direct questions and common verbs are used where possible.

Do not require every sentence to be elementary. Necessary technical terms can remain when they are introduced clearly and used consistently.

## Review standard 3: Canonical business story

Confirm that the Nova Mobile campaign is explained accurately:

1. A customer chooses a selected phone at a participating store.
2. The customer applies for a Unicorn Finance point-of-sale installment loan.
3. If approved, the customer is scheduled to repay the amount borrowed over 6, 9, or 12 monthly payments.
4. The customer pays 0% monthly interest.
5. Nova Mobile pays Unicorn Finance a subsidy to support the 0% offer.

Whenever the campaign is introduced to participants, require a clear statement that:

- the phone is not free;
- the customer still has to repay the amount borrowed;
- a processing fee or down payment may still apply; and
- approval is not guaranteed.

Confirm that the content does not imply:

- a free phone;
- zero down payment;
- zero fees;
- guaranteed approval;
- completed repayment;
- that the promotion caused an increase;
- that a location or salesperson caused FPD5;
- confirmed fraud; or
- that fictional data represents Home Credit production systems.

Canonical identifiers:

- promotion code: `ZERO_SMARTPHONE_2026`
- product label: `Unicorn 0% Brand Promotion`
- analysis label: `0% smartphone promotion`
- comparison label: `Other eligible originations`

When `Other eligible originations` is participant-visible, check that **origination** is explained as a loan that was created.

Confirm that Unicorn Finance, Nova Mobile, and Atlas Ridge Consulting are identified as fictional where the audience could otherwise misunderstand.

## Review standard 4: FPD5 correctness

Confirm that:

- FPD5 means **First Payment Default at five days past due**;
- only `installment_no = 1` is used;
- the loan becomes eligible on `due_date + 5 days`;
- `date_add(due_date, 5) <= OBSERVATION_DATE`;
- null settlement counts as FPD5;
- settlement on or after day five counts as FPD5;
- settlement before day five does not count as FPD5;
- payment on day five counts as FPD5;
- one row represents one eligible fixed-term credit contract;
- `contract_id` is unique before aggregation;
- the numerator is eligible loans with FPD5; and
- the denominator is all eligible loans in the selected group.

Flag calculations based on:

- applications;
- approvals;
- all created loans regardless of age;
- only defaulted loans;
- multiple payment rows per contract; or
- inconsistent populations between count and rate.

Confirm that **default** is explained in its limited workshop meaning. It describes the first payment at day five. It does not mean that the full loan was never repaid.

Reference results are valid only for:

- observation date `2026-09-01`;
- generator version `1.1.0`;
- standard scale; and
- master seed `20260922`.

Expected reference values:

- top-20% store share: approximately 81.13% of applications where `store_id` is not null;
- promotion FPD5 rate: approximately 42.26%; and
- other eligible-loan FPD5 rate: approximately 21.03%.

Confirm that expected answers are not revealed before the participant discovery step.

## Review standard 5: Notebook and code structure

For Databricks source notebooks, confirm:

- the source header is correct;
- `COMMAND ----------` separators are valid;
- configuration is visible near the top;
- cells run in a clear order;
- each cell has one learning purpose;
- cells are safely rerunnable;
- write behavior is explicit;
- displayed fields support the current question;
- output labels are understandable; and
- code does not hide an important business rule.

A good learning block is:

1. a short Markdown question;
2. one sentence explaining why it matters;
3. one code cell performing one meaningful action;
4. the evidence needed for that question; and
5. a short interpretation or transition when needed.

Flag cells that combine unrelated actions, such as:

- creating an asset name;
- writing a table;
- capturing a version;
- changing a schema;
- updating rows;
- comparing versions; and
- showing history.

Do not require excessive commentary around obvious cells. One clear sentence may be enough.

Check that:

- Python syntax is valid;
- SQL uses real columns and values;
- joins preserve the intended row count;
- persistent participant assets follow `unicorn_<runner_id>_<asset>`;
- `runner_id` uses a sanitized username prefix plus a short deterministic hash of the full workspace identity;
- `runner_id` begins with a letter and contains only lowercase letters, numbers, and underscores;
- participants are not asked to enter an identifier manually;
- participant writes use only participant-specific assets;
- cleanup affects only the current participant's exact prefix; and
- no broad wildcard can remove another participant's assets.

## Review standard 6: Participant action and learning

Confirm that participant work is more than running prepared cells.

A meaningful action may ask participants to:

- change a grouping, parameter, rule, or filter;
- compare counts and percentages;
- explain what changed;
- identify uncertainty;
- record a follow-up question;
- inspect generated SQL; or
- save a result used later.

Check that every participant task states:

- the timebox;
- the exact action;
- what to record;
- how to know it is complete; and
- what conclusions are not supported.

Confirm that:

- the exercise output is used later;
- small groups are not ranked without a justified minimum size;
- counts are shown beside percentages;
- application volume is not confused with FPD5 percentage; and
- timing is not described as causation.

## Review standard 7: Participant-facing file structure

Confirm that participants have one primary entry point.

For a notebook-led section:

- the notebook contains the assignment, instructions, exercises, UI steps, validation, and reflection;
- participants do not need to switch among README, exercises, expected-results, and notebook files; and
- the participant folder contains only files participants actually use.

For a facilitator-led section:

- participants use one integrated guide or worksheet;
- the guide contains the assignment, evidence capture, activity, and reflection; and
- facilitator demonstration assets are not presented as participant work.

Flag participant material containing:

- setup or rehearsal instructions;
- facilitator timing recovery;
- administrator grants or cleanup;
- presenter cues;
- fallback demonstrations;
- answers shown too early;
- unresolved `TBD` values;
- links to unavailable files; or
- facilitator-only troubleshooting.

Confirm that:

- participant assets are under `workshop-content/`;
- maintainer and facilitator assets are under `workshop-authoring/sections/`;
- setup is under `workshop-setup/`;
- removed files have no stale references; and
- temporary slide outlines are removed after their content is transferred.

## Review standard 8: Facilitator readiness

Confirm that the facilitator guide contains:

- participant-equivalent setup and rehearsal checks;
- a minute-by-minute run of show;
- timings that fit `SECTION_DURATION_MINUTES`;
- expected results;
- likely errors;
- the shortest safe recovery path;
- fallbacks for optional features;
- checks that must not be skipped when time runs short;
- exact UI paths where useful; and
- clear separation between participant, facilitator, and administrator actions.

Check that facilitator language does not reintroduce jargon removed from participant material.

Check that slide briefs:

- use short visible text;
- support the participant journey;
- explain the business story before product concepts;
- do not expose expected answers too early;
- do not duplicate notebook code;
- distinguish visible content from presenter notes; and
- avoid decorative or unrelated product slides.

## Review standard 9: Databricks correctness

### Compute

Confirm that:

- notebook Python and `spark.sql` use notebook compute;
- `%sql` in a mixed Python notebook uses notebook compute;
- dashboards and Genie Agents use a SQL warehouse;
- participants are not told to find notebook Spark queries in SQL warehouse Query History;
- Jobs compute is used for automated tasks; and
- serverless is not described as removing ownership of code, access, quality, cost, or monitoring.

### Unity Catalog and workspace permissions

Confirm that:

- `<WORKSHOP_CATALOG>.core_lending` contains shared source tables and remains read-only for participants;
- `<WORKSHOP_CATALOG>.workshop_shared` contains facilitator-owned shared views and Metric Views;
- `<WORKSHOP_CATALOG>.workshop_labs` contains participant-created tables, views, and registered models;
- the source model uses only `customer`, `retail_location`, `loan_product`, `loan_application`, `credit_contract`, `installment`, `payment`, and `collection_action`;
- the content does not invent events, tables, or relationships that are absent from the data dictionary;
- the content does not add cross-sell analysis because the dataset has no offer-response event;
- participants do not receive a separate schema;
- fully qualified names are used;
- `main`, `hive_metastore`, and personal catalogs are not used;
- workspace permissions are not confused with Unity Catalog data permissions;
- a naming prefix is not described as a security boundary;
- notebooks, jobs, pipelines, dashboards, experiments, and Genie Agents are treated as workspace assets rather than catalog objects;
- shared workshop notebooks use the intended shared workspace location; and
- private participant Agents are stored in `/Workspace/Users/<workspace-username>`, not `/Workspace/Shared`.

### Metric Views, dashboards, and Genie

Confirm that:

- `<WORKSHOP_CATALOG>.workshop_shared.fpd_metrics` is the shared FPD5 source;
- Metric View measures use `MEASURE(...)`;
- dashboards and participant Genie Agents do not recreate the FPD5 formula;
- `fpd_metrics` is the Agent's only data source unless another governed source is explicitly required;
- the participant path stops if a required Metric View is unavailable;
- generated SQL is inspected before trusting a written answer;
- dashboard SQL is verified;
- dashboard numbers match the notebook;
- filters work as described; and
- exact confirmed warehouse and group names replace placeholders before release.

### Agent privacy

Confirm that:

- each participant creates their own Agent;
- the Agent is in the participant's user folder;
- the Agent is not shared with all account users, the workshop group, or another participant; and
- administrator access is not described as impossible.

### Delta

Confirm that:

- persistence has a clear reason;
- every write or schema change is explained;
- rerun behavior is safe and documented;
- history is used to inspect changes; and
- time travel is not described as a backup.

### Jobs and pipelines

When present, confirm that:

- current Lakeflow APIs and terminology are used;
- legacy `dlt` or `LIVE` syntax is not introduced;
- retries, quality behavior, parameters, monitoring, rerun, and recovery are explained; and
- automated work does not run on an analyst's interactive compute without justification.

### Machine learning

When present, confirm that:

- batch scoring is the required path unless the assignment explicitly requires serving;
- target leakage is avoided;
- evaluation metrics are explained in business language;
- registry names are participant-safe;
- registered models use Unity Catalog; and
- ownership, retraining, monitoring, and rollback are addressed.

## Review standard 10: Scope and timing

Confirm that:

- the assets cover the selected topics and no unrelated product coverage;
- every activity supports the assignment;
- navigation and discussion time are included;
- participant exercises have realistic timeboxes;
- optional content is clearly marked;
- the section can finish within the agenda duration; and
- critical learning is protected when time runs short.

Flag maximum-feature-coverage designs.

Prefer one complete workflow over several disconnected demonstrations.

## Review standard 11: Validation evidence

Separate:

- checks proven by source inspection;
- checks proven by syntax or static validation;
- checks proven by runtime evidence; and
- checks not yet performed.

Never claim runtime success from code inspection alone.

When runtime evidence is supplied, verify that it names:

- workspace;
- identity or permission level;
- runtime or compute;
- SQL warehouse;
- dataset configuration;
- observation date;
- cells or assets tested;
- expected and actual results; and
- clean-rerun behavior.

When runtime evidence is missing, list the exact remaining tests.

For notebook-led sections, typical remaining tests include:

- run every cell in order;
- run the participant exercise;
- rerun from a clean session;
- rerun persistent write cells;
- verify expected counts and rates;
- verify dashboard filters and sharing;
- verify Agent source, privacy, generated SQL, and answer; and
- inspect a real Query Profile.

## Review workflow

### QUICK

Use when the user wants an initial screening.

1. Read the mandatory every-depth sources, every review target, and the related participant asset when one exists.
2. Apply the highest-impact standards relevant to `TARGET_TYPE`.
3. Report only Blocker, High, and important Medium findings.

### STANDARD

1. Read the complete participant journey.
2. Read the facilitator and maintainer assets.
3. Check setup and directly dependent assets.
4. Apply all relevant review standards.
5. Run safe static checks.
6. Report findings and validation gaps.

### THOROUGH

1. Perform the STANDARD review.
2. Trace every participant instruction to its code, UI action, expected result, and recovery path.
3. Check all local references and moved-file paths.
4. Compare repeated business definitions across the repository.
5. Inspect downstream sections for incompatible labels, schemas, or saved assets.
6. Review available runtime evidence in detail.

## Required output

Return the review in this order.

### 1. Verdict

Choose one:

- **NOT READY**
- **READY WITH FIXES**
- **READY FOR RUNTIME VALIDATION**
- **READY FOR DELIVERY**

Use:

- **NOT READY** when any Blocker or High finding remains, or the participant outcome cannot be completed safely.
- **READY WITH FIXES** when only Medium or Low findings remain.
- **READY FOR RUNTIME VALIDATION** when no substantive static findings remain but participant-equivalent runtime execution or facilitator rehearsal is not proven.
- **READY FOR DELIVERY** only when no substantive findings remain and participant-equivalent runtime execution plus facilitator rehearsal are proven.

### 2. Summary

In five or fewer bullets, state:

- the participant journey;
- the strongest part;
- the main risk;
- the number of findings by severity; and
- the runtime-validation status.

### 3. Findings

List findings in severity order.

For each finding, use:

```text
[ID] [Severity] Short title
Evidence: <path:line or asset section>
Current behavior: <what exists now>
Why it matters: <the correctness, learning, safety, or maintenance reason>
Impact: <participant, facilitator, technical system, or safety boundary affected>
Recommended change: <specific fix>
```

Do not repeat the same root cause in several findings.

If no substantive findings remain, say so explicitly.

### 4. Participant journey

For `COMPLETE_SECTION`, `PARTICIPANT_ASSET`, `FACILITATOR_ASSET`, or `SLIDE_BRIEF`, summarize the current participant journey in plain language. Do not repeat detailed defects. Refer to finding IDs for missing steps, weak transitions, unused outputs, or unrelated activities.

For a standalone `SETUP_ASSET` or `ASSET_SPECIFICATION` with no related participant flow, write `N/A` and briefly state the asset's purpose instead.

### 5. File and audience boundaries

List without repeating detailed findings:

- the primary participant entry point;
- other participant-visible files;
- facilitator-only files;
- administrator/setup files;
- redundant files; and
- stale or broken references.

### 6. What should remain unchanged

Identify correct business logic, useful code, effective explanations, and valuable activities that should be preserved. Do not restate defects.

### 7. Validation status

Separate:

- static checks passed;
- runtime checks proven;
- runtime checks missing; and
- unresolved environment values.

### 8. Recommended fix order

Give the shortest safe sequence:

1. Blockers and correctness.
2. Participant comprehension and story.
3. Cell or file structure.
4. Facilitator readiness.
5. Runtime validation.

Refer to finding IDs instead of repeating each finding.

Keep the review concise. Evidence matters more than volume.

Do not edit files.
````
