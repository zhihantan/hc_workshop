# Workshop standards

**Updated at:** 2026-10-01

*Reusable rules applied by every prompt in this playbook. Customer-specific values live in the workshop facts file, never here.*

Placeholders such as `<CATALOG>` or `<CORE_METRIC>` refer to fields in the facts file (`workshop-facts.md`, created from `workshop-facts-template.md`).

## 1. Audience assumptions

Assume that participants:

- may be new to the customer's business domain;
- may be using Databricks for the first time;
- may not speak English as a first language; and
- can be confused by text that is technically correct.

Simplicity and clarity are release requirements, not style preferences.

## 2. One story, not a feature tour

- The whole workshop follows one fictional company and one business event from the facts file.
- Each section delivers one assignment for that company. Products support the assignment; they are not the story.
- Every section starts with the assignment: business situation, participant role, questions to answer, final deliverable, and the interpretation boundary (for example, "a signal, not proof").
- Explain an unfamiliar business process with a short numbered example before showing its data fields.
- Each part answers one question. Use question headings such as `Which loans are old enough to check?`, not product headings such as `Explore with PySpark` or `Delta Lake`.
- Before each major step, one or two sentences say what question it answers, why it is needed now, or how it leads to the next step.
- After a result that needs interpretation, say what to notice and what must not be concluded.
- Prefer one complete workflow over maximum feature coverage. Move disconnected products to optional or facilitator reference material.

### Delivery pattern

Every section fits its duration and follows:

1. Assignment — role, problem, questions, final output, interpretation boundary.
2. Understand — only the business and technical ideas this assignment needs, with an example before any formula.
3. Investigate together — short steps that answer the questions in order.
4. Participant action — change or extend a meaningful part of the work.
5. Save or operate — ownership, access, dependencies, history, monitoring, or recovery, because the assignment needs it.
6. Reflection — result, uncertainty, owner, one risk, one check or fix.

## 3. Plain English

- Short sentences, one idea each.
- Common verbs: `check`, `count`, `compare`, `save`, `find`.
- Use the same term for the same concept everywhere.
- Show an example before a formula.
- Explain a necessary technical term immediately, using the facts-file glossary.
- Avoid abstract noun phrases such as `establish the origination context`, `derive a cohort label`, `operationalize the analytical asset`, or `reconcile governed semantics`. Prefer `see where customers applied`, `label the promotion applications`, `save the result for the next analyst`, `check that the answers match`.
- Describe the fictional business event concretely. If a participant could misread it (for example, "0% promotion" read as "free phone"), state plainly what it is and what it is not.

## 4. Audience boundaries and file layout

Three audiences, three locations:

| Audience | Location | Contains |
|---|---|---|
| Participant | `participant-materials/`, `workshop-content/<NN>-<section>/` | Opening scenario and reference PDFs; one entry point per section |
| Facilitator and maintainer | `workshop-authoring/` | Story, agenda, dataset design, section plans, slide prompts, facilitator demos, drafts |
| Administrator | `workshop-setup/` | Catalog, schema, dataset, shared-asset setup, grants, admin instructions, jobs |

Participant material must not contain setup or rehearsal steps, presenter cues, timing recovery, administrator grants, fallback demonstrations, answers revealed before the exercise, unresolved `TBD` values, or links to files participants cannot open.

### One participant entry point per section

- **Notebook-led section:** the notebook is the participant source of truth. Instructions, exercises, UI steps, validation, checkpoints, and reflection all live in it. Name it with the section number (for example `01-lab.py`) so files are distinguishable once imported.
- **Facilitator-led section:** one integrated participant guide or worksheet (for example `05-participant-guide.md`). Facilitator demonstration code lives under `workshop-authoring/sections/`, not with participant files.
- Add another participant file only when participants use it independently.
- Remove temporary slide outlines once their content moves into the final slide prompt.

### Three files per section

Every section has exactly three core files, created in this order:

```text
workshop-authoring/sections/<NN>-<section>/section-plan.md                    # 1. plan, then facilitator guide (section 8)
workshop-content/<NN>-<section>/<NN>-lab.py                                   # 2. notebook or participant guide
workshop-authoring/sections/<NN>-<section>/generate-section-<NN>-<topic>-slides.md   # 3. slide prompt (section 9)
```

Add only when needed:

```text
workshop-authoring/sections/<NN>-<section>/facilitator-demo.py   # the facilitator runs code participants do not
workshop-authoring/sections/<NN>-<section>/drafts/               # superseded versions worth keeping
workshop-setup/section-<NN>-facilitator-setup.sql                # shared assets this section needs
```

Do not add a separate section README or facilitator guide. Permissions and shared-asset setup belong in `workshop-setup/`; status, outcomes, and talking points belong in the section plan.

Keep section numbers identical to the agenda. If a section is dropped, decide once whether later sections are renumbered, and record the decision in the facts file.

## 5. Notebook structure

A learning block is:

1. Markdown: one question and why it matters.
2. Code: one meaningful action.
3. Output: only the evidence needed for that question.
4. Markdown: what to notice.
5. Transition: why the next question follows.

Code cells must be short, complete, sequential, safe to rerun, and limited to one learning purpose. Split cells that combine naming, writing, versioning, schema change, update, comparison, and history.

- Code should look like realistic inherited team code. Keep configuration visible near the top but minimal; hide environment plumbing that does not teach anything.
- Do not ask participants to type large prepared blocks.
- Do not display fields the participant does not need for the current question.
- Participant notebooks use the runtime-provided `spark`, `dbutils`, widgets, `%sql`, and `display()`. Never put Databricks Connect or profile configuration in a participant notebook.

## 6. Participant actions and reflection

A participant exercise changes or extends something meaningful: a grouping, parameter, rule, or filter; a comparison of counts and percentages; an explanation of uncertainty; a follow-up question; or a saved result used later.

Each exercise states the timebox, the exact action, what to record, how to know it is complete, and which conclusions are not supported. Use a writing template when participants summarize evidence. Keep expected numbers hidden until after the discovery step.

End each section with participant-facing reflection ("Before finishing, check that you can explain…"). Ask for one owner, one thing that could go wrong, and how to check or fix it. Never put facilitator cleanup or logistics in the reflection.

## 7. Multi-participant safety

- Every exercise is individual unless the facts file says otherwise. Do not invent teams.
- Source data is read-only for participants.
- Participants write to the shared labs schema using `<ASSET_PREFIX>_<runner_id>_<asset>`. `runner_id` is derived automatically from a sanitized username prefix plus a short deterministic hash of the full workspace identity; it begins with a letter and contains only lowercase letters, digits, and underscores. Never ask participants to type an identifier.
- Use a per-participant schema only when a product needs its own target (for example, a pipeline target schema), and record why in the section plan.
- Cleanup removes only the current participant's exact prefix. No broad wildcards.
- A naming prefix prevents collisions. It is not a security boundary.
- Private workspace assets (for example, Genie Agents) live in `/Workspace/Users/<workspace-username>` and stay unshared. Workspace administrators can still see them; do not claim otherwise.
- Prefer temporary views for results that do not need to outlive the session.

## 8. Section plan format

The section plan is written before the notebook and is the foundation for everything else in the section. It decides the outcomes, what is presented on slides, and what participants go through in the notebook. After the notebook is built, the same file becomes the facilitator's quick reference during delivery, so there is one document and nothing to keep in sync.

It is not a run book and not presentation advice.

### Structure

```markdown
# Section <NN> — <name>

**Status:** PLANNED | NOTEBOOK BUILT | DELIVERY READY
**Scheduled:** <time> · <minutes> minutes
**Participant entry point:** <link, once it exists>

## Outcomes
- **Assignment:** <one question participants answer for the fictional company>
- **Participants leave with:** <the saved result, decision, asset, or handover note>
- **Participants can explain:** <two to four ideas>
- **Reuses / depends on:** <earlier assets, shared assets, setup>

## Delivery map
| Time | Minutes | Mode | Focus |
|---|---:|---|---|

## 1. <part title, phrased as a question> · <Mode> · <minutes>
- **Goal:** <what this part achieves>
- **Cover:** <three to six bullets: for Slides, the messages that must land; for Notebook, the steps and the evidence each produces; for a demo, what is shown and why>
- **Participant action:** <only for exercises: action, what to record, done when>
- **Say:** <added once the notebook is built: definitions, distinctions, reference results to reveal after discovery, caveats>

(repeat for each delivery-map row, in order)

## Closing question
<one question>
```

### Rules

- Mode is one of `Slides`, `Notebook`, `Notebook exercise`, `Facilitator demo`, `Guided participant activity`, `Discussion`. Delivery-map rows are contiguous and add up to the section duration, including navigation and discussion.
- Facilitator demos are never labelled as participant work.
- Bullets are one idea each and under about 25 words. The whole plan should fit on about two printed pages, so the facilitator can scan it during delivery.
- Do not include generic advice ("use plain language", "pause for questions"), setup steps, grant statements, troubleshooting trees, or rehearsal checklists. Setup lives in `workshop-setup/`.
- Once the notebook exists, the notebook is the source of truth for order and content. If they disagree, update the plan to match the notebook, unless the notebook is wrong.

## 9. Slide rules

- Slides cover only the `Slides` rows of the section plan's delivery map. Notebook, demo, and guided UI work is delivered live.
- Slide prompts are content-first: the messages that must land, authoritative definitions, boundaries, exclusions, and the required output. Leave slide count, titles, layout, and visual language to the slide-generating model. Earlier prescriptive, slide-by-slide prompts over-constrained the output.
- Never put full code, seeded reference results before the matching exercise, unverified screenshots, or invented workspace evidence on slides.
- The opening deck shows the agenda, the story, and the dataset. The closing deck mirrors the opening and shows what changed by the end of the day.
- Presenter notes may say "you built" only for work participants actually did. Use "the facilitator demonstrated" for demos.

## 10. Databricks correctness

### Compute

- Notebook Python, `spark.sql`, and `%sql` cells in a Python notebook run on the notebook's attached compute.
- AI/BI dashboards and Genie Agents run on a SQL warehouse. Only warehouse statements appear in SQL Query History.
- Jobs compute is for automated work; all-purpose compute is for interactive work.
- Serverless removes infrastructure work, not ownership of code, access, quality, cost, or monitoring.

### Unity Catalog and workspace

- Use `<CATALOG>` with three schemas: `<SOURCE_SCHEMA>` (read-only source), `<SHARED_SCHEMA>` (facilitator-owned shared views and Metric Views), `<LABS_SCHEMA>` (participant outputs and registered models).
- Use fully qualified names in notebook SQL and DDL. Never use `main`, `hive_metastore`, or personal catalogs.
- Notebooks, jobs, pipelines, dashboards, experiments, and Genie Agents are workspace assets, not catalog objects.
- Explain workspace permissions separately from Unity Catalog privileges.
- Grant the minimum privileges each section needs. Do not grant catalog-wide `ALL PRIVILEGES` or `MANAGE` to participants.

### Metrics, dashboards, and Genie

- Define `<CORE_METRIC>` once, in a shared Metric View (`<SHARED_METRIC_VIEW>`), and reuse it in dashboards and Genie Agents through `MEASURE(...)`.
- Do not duplicate the formula in widgets or Agent instructions. If the Metric View is missing, stop and escalate; do not silently recalculate.
- Verify generated SQL before trusting a written answer. Show counts beside percentages and state minimum group sizes for rankings.
- Distinguish volume from rate and timing from causation.

### Delta, pipelines, and ML

- Persist a result only when someone needs it later. Explain every write or schema change and its rerun behavior.
- Table history helps inspect changes; time travel depends on retained files and is not a backup.
- Use current Lakeflow names and APIs. Do not introduce legacy `dlt` or `LIVE` syntax.
- Keep batch scoring as the required ML path; serving is optional unless the assignment needs it. Avoid target leakage and split by time.

### Product claims

Do not invent product behavior, UI paths, permission behavior, or feature availability. When unsure, check current Databricks documentation and say what was checked.

## 11. Validation and honesty

- Read every participant asset start to finish as a first-time learner: at each part, can they say what they are doing, why, what to notice, and what comes next?
- Check business rules against the facts file: population, eligibility, numerator, denominator, grain, edge cases, as-of date.
- Validate notebook source headers, `COMMAND ----------` separators, Python and SQL syntax, local links, and references to moved files.
- Develop Spark logic quickly with Databricks Connect from a local script, then run the real notebook cell by cell in the workspace with participant-equivalent permissions from a clean session.
- Record the workspace, identity, compute, warehouse, and dataset configuration used for every runtime check.
- Never claim a test passed when it was not run. Unknown environment values stay `TBD — facilitator confirmation required` in authoring material and must be resolved before participant release.
