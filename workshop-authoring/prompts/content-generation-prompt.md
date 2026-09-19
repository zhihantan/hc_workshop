# Workshop content-generation prompt

**Updated at:** 2026-09-16

*Concise master prompt for creating the Home Credit Databricks workshop one section at a time.*

## Use

Set the shared environment inputs, describe the section you want to create, and give the agent access to this repository. `SECTION_TOPICS` is intentionally curator-owned; the prompt does not prescribe mandatory topics.

## Prompt

````text
Create one section of the Home Credit Philippines Databricks workshop. Give participants one primary entry point and one coherent business or operational assignment. In notebook-led sections, participants run and extend the notebook after a live screen-share. In facilitator-led sections, participants complete one integrated guide or worksheet while the facilitator operates restricted, administrative, or preview-only surfaces. The goal is to build confidence using Databricks through one coherent, end-to-end developer workflow. Operational takeover of assets built by Tiger Analytics provides the scenario and ownership lens; it must not turn the section into a broad product tour.

## Inputs

REPOSITORY_ROOT: [absolute path to this repository]
WORKSPACE_ROOT: /Workspace/Shared/hc_workshop
WORKSHOP_CATALOG: hc_workshop
WORKSHOP_RUNTIME: TBD
SQL_WAREHOUSE: TBD
FACILITATOR_GROUP: TBD

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
7. `workshop-setup/dataset-generator/README.md` — environment and validation.

Write runnable participant material under `workshop-content/` and maintainer, facilitator, expected-output, troubleshooting, and slide-authoring material under `workshop-authoring/sections/`. Preserve all unselected sections.

## Story

**Unicorn Finance Philippines — Credit with a little magic**

Unicorn Finance is a fictional consumer lender offering POS installment loans, cash loans, Unicorn Flex revolving credit, and Unicorn Visa. Its implementation partner, Atlas Ridge Consulting, has delivered a Databricks lakehouse and is handing operations to internal developers. Atlas Ridge is the fictional stand-in for Tiger Analytics.

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

Do not create a schema per participant. Name persistent participant-created objects with an identifier derived automatically from `current_user()`:

```text
unicorn_<runner_id>_<asset>
```

Construct `runner_id` from a sanitized username prefix plus a short deterministic hash of the full workspace identity. It must begin with a letter and contain only lowercase letters, numbers, and underscores. Never ask participants to enter an identifier manually. Prefer temporary views when persistence is unnecessary. Cleanup may affect only objects with that participant's prefix. Prefixes prevent workshop collisions but are not a security boundary; use separate schemas only if participants are untrusted or need long-lived isolation.

Never modify `<WORKSHOP_CATALOG>.core_lending` or use `main`, `hive_metastore`, or personal catalogs. Use fully qualified names in notebook SQL and Unity Catalog DDL.

Notebooks, jobs, pipelines, dashboards, experiments, and Genie Agents are workspace assets, not catalog objects. Store them under `WORKSPACE_ROOT` with clear ownership and permissions.

The source contains:

`customer`, `retail_location`, `loan_product`, `loan_application`, `credit_contract`, `installment`, `payment`, and `collection_action`.

FPD5 means the first installment reached five days past due before full settlement. Include only rows where `installment_no = 1` and `date_add(due_date, 5) <= as_of_date`. A null settlement or settlement on/after day five is FPD.

Useful standard-scale checks: top-20% store share ≈ 81.13%; promotion FPD ≈ 42.26%; other FPD ≈ 21.03%.

## Delivery pattern

Every section must fit its agenda duration and follow:

1. **Assignment** — state the participant role, business or operational problem, questions to answer, and final deliverable.
2. **Investigate with me** — use the minimum slides and live evidence required to advance that assignment.
3. **Participant action** — run short cells in a notebook-led section or record and interpret evidence in a facilitator-led section.
4. **Operate it** — inspect ownership, parameters, dependencies, permissions, lineage, run history, or recovery because the assignment requires it.
5. **Reflection** — confirm an observable result and have participants explain the evidence, owner, risk, and recovery action.

Include a minute-by-minute run of show, expected results, likely errors, the shortest recovery path, and a fallback for unavailable optional features. Clearly separate facilitator-only and admin-only steps.

Prefer one connected workflow over maximum feature coverage. Move disconnected comparisons, advanced operations, and optional products to facilitator reference material unless they directly support the section outcome.

## Section input

Create only the section described by `SECTION_NUMBER`, `SECTION_NAME`, `SECTION_DURATION_MINUTES`, and `SECTION_TOPICS`. Treat the supplied topics as the curator's scope: do not add unrelated product coverage merely because it appears elsewhere in the agenda. Ask for clarification only when the supplied topics cannot form a runnable section.

## Required outputs

Create `workshop-content/<section-number>-<section-name>/` with the smallest participant-facing surface possible:

- `participant-lab.py` or `.sql` for a notebook-led section, or `participant-guide.md` for a facilitator-led section.
- Embed participant instructions, exercises, validation criteria, and reflection prompts in that notebook when the section is notebook-led.
- Consolidate the assignment, evidence capture, exercise, validation criteria, and reflection in the participant guide when the section is facilitator-led.
- Create a separate checklist or exercise file only when participants genuinely use it independently of the primary entry point.

Keep the maintainer README, facilitator guide, expected outputs, troubleshooting, and temporary slide-authoring material under `workshop-authoring/sections/<section-number>-<section-name>/`. Add section-specific setup files only when needed. Update `workshop-content/README.md` status. Put shared setup under `workshop-content/shared/` and operational handover material under `workshop-content/07-handover-and-operations/`.

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

Generate section 01 first, then section 02. The trusted analytical outputs from section 01 should feed the dashboard and private Genie Agent that Section 02 improves.
