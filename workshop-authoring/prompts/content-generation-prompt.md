# Workshop content-generation prompt

**Updated at:** 2026-09-16

*Concise master prompt for creating the Home Credit Databricks workshop one section at a time.*

## Use

Set the shared environment inputs, describe the section you want to create, and give the agent access to this repository. `SECTION_TOPICS` is intentionally curator-owned; the prompt does not prescribe mandatory topics.

## Prompt

````text
Create one section of the Home Credit Philippines Databricks workshop. Participants will first follow a live screen-share, then run the provided notebook themselves. The goal is operational takeover of assets built by Tiger Analytics, not a broad product tour.

## Inputs

REPOSITORY_ROOT: [absolute path to this repository]
WORKSPACE_ROOT: /Workspace/Shared/homecredit-workshop
WORKSHOP_CATALOG: hc_workshop
WORKSHOP_RUNTIME: TBD
SQL_WAREHOUSE: TBD
FACILITATOR_GROUP: TBD
TEAM_ID: [assigned lowercase team ID]

SECTION_NUMBER: [01-06]
SECTION_NAME: [section name]
SECTION_DURATION_MINUTES: [agenda duration]
SECTION_TOPICS:
- [topic to cover]
- [topic to cover]

If an environment value is unknown, write `TBD — facilitator confirmation required`. Never invent IDs, permissions, enabled features, runtimes, or test results.

## Read first

Paths are relative to `REPOSITORY_ROOT`:

1. `workshop-authoring/story/unicorn-finance-story.md` — canonical company and workshop narrative.
2. `workshop-authoring/agenda/workshop-agenda.md` — agenda and timing.
3. `workshop-authoring/dataset/dataset-design.md` — dataset design decisions.
4. `workshop-authoring/dataset/dataset-guide.md` — relationships and analytical paths.
5. `workshop-authoring/dataset/data-dictionary.md` — authoritative columns and values.
6. `workshop-authoring/dataset/source-schema.md` — source-model decisions.
7. `workspace-setup/dataset-generator/README.md` — environment and validation.

Write generated material only under `workshop-content/`. Preserve all unselected sections.

## Story

**Unicorn Finance Philippines — Credit with a little magic**

Unicorn Finance is a fictional consumer lender offering POS installment loans, cash loans, Unicorn Flex revolving credit, and Unicorn Visa. Its implementation partner, Atlas Ridge Consulting, has delivered a Databricks lakehouse and is handing operations to the internal team. Atlas Ridge is the fictional stand-in for Tiger Analytics.

A brand-subsidised 0% smartphone promotion increased originations. First-payment default then became concentrated in a few stores and sales associates. Participants must investigate whether the pattern reflects campaign design, weak controls, customer mix, or potential fraud; never label it as confirmed fraud.

Use one continuous story:

1. Find the inherited platform assets.
2. Investigate the promotion and FPD pattern.
3. Ask governed questions with Genie and verify the answers.
4. Productionise the analysis as a monitored pipeline/job.
5. Protect sensitive data and inspect lineage.
6. Train, register, and batch-score an FPD model.

Never imply that the synthetic data or schema represents Home Credit production systems.

## Data and schema model

Use three schemas in `WORKSHOP_CATALOG`:

- `<WORKSHOP_CATALOG>.core_lending` — shared source tables; read-only for participants.
- `<WORKSHOP_CATALOG>.workshop_shared` — facilitator-owned views or metric views used by dashboards and Genie.
- `<WORKSHOP_CATALOG>.workshop_labs` — shared participant tables, views, and registered models.

Do not create a schema per participant. Use an assigned team ID and name participant-created objects:

```text
unicorn_<team_id>_<asset>
```

Validate `TEAM_ID` against `^[a-z][a-z0-9_]{0,19}$`. Prefer temporary views when persistence is unnecessary. Cleanup may affect only objects with the assigned prefix. Prefixes prevent workshop collisions but are not a security boundary; use separate team schemas only if participants are untrusted or need long-lived isolation.

Never modify `<WORKSHOP_CATALOG>.core_lending` or use `main`, `hive_metastore`, or personal catalogs. Use fully qualified names in notebook SQL and Unity Catalog DDL.

Notebooks, jobs, pipelines, dashboards, experiments, and Genie Agents are workspace assets, not catalog objects. Store them under `WORKSPACE_ROOT` with clear ownership and permissions.

The source contains:

`customer`, `retail_location`, `loan_product`, `loan_application`, `credit_contract`, `installment`, `payment`, and `collection_action`.

FPD5 means the first installment reached five days past due before full settlement. Include only rows where `installment_no = 1` and `date_add(due_date, 5) <= as_of_date`. A null settlement or settlement on/after day five is FPD.

Useful standard-scale checks: top-20% store share ≈ 81.13%; promotion FPD ≈ 42.26%; other FPD ≈ 21.03%.

## Delivery pattern

Every section must fit its agenda duration and follow:

1. **Watch me** — exact UI path and short facilitator demonstration.
2. **Run with me** — complete, short notebook cells run in sequence.
3. **Try it** — one focused participant exercise.
4. **Operate it** — inspect ownership, parameters, dependencies, permissions, lineage, run history, or recovery.
5. **Checkpoint** — confirm an observable result.

Include a minute-by-minute run of show, expected results, likely errors, the shortest recovery path, and a fallback for unavailable optional features. Clearly separate facilitator-only and admin-only steps.

## Section input

Create only the section described by `SECTION_NUMBER`, `SECTION_NAME`, `SECTION_DURATION_MINUTES`, and `SECTION_TOPICS`. Treat the supplied topics as the curator's scope: do not add unrelated product coverage merely because it appears elsewhere in the agenda. Ask for clarification only when the supplied topics cannot form a runnable section.

## Required outputs

Create `workshop-content/<section-number>-<section-name>/` with only the files needed:

- `README.md` — duration, outcomes, prerequisites, permissions, assets, and definition of done.
- `facilitator-guide.md` — screen path, talking points, timing, errors, and handover lens.
- `participant-lab.py` or `.sql` — runnable Databricks source notebook.
- `exercises.md` — participant task and validation.
- `expected-results.md` — expected outputs and troubleshooting.

Add section-specific setup files only when needed. Update `workshop-content/README.md` status. Put shared setup under `workshop-content/shared/` and operational handover material under `workshop-content/07-handover-and-operations/`.

## Rules

- Use only columns in the data dictionary.
- Use the same FPD5 definition everywhere.
- Keep participant cells short, complete, sequential, idempotent, and safely rerunnable.
- Databricks source notebooks must have the correct source header and `COMMAND ----------` separators.
- Do not ask participants to type long code during the demonstration.
- Do not add cross-sell analysis; the dataset has no offer-response event.
- Use modern Databricks terminology and modern Lakeflow APIs, not legacy `dlt` or `LIVE`.
- Verify dashboard SQL before treating a dashboard as complete.
- Keep batch scoring as the required ML path; serving is optional.
- End every section with what participants must operate after the Tiger handover.

Before finishing, validate paths, notebook format, columns, catalog usage, rerun safety, expected results, and section timing. Test runnable assets in the sandbox when access is available; otherwise mark them untested.

In the final response, list files created, tests run, unresolved setup, and deliberate omissions. Do not paste generated files into chat.
````

## Recommended generation order

Generate section 01 first, then section 02. The trusted analytical outputs from section 02 should feed the dashboard and Genie exercises.
