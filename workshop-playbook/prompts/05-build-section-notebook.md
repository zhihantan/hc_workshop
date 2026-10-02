# Prompt 05 — Build, review, or fix the section notebook

**Use when:** the section plan is approved (`04-plan-section.md`, mode `PLAN`).
**Produces:** the participant entry point under `workshop-content/`, plus a facilitator demo or setup file only when the plan needs one.
**Next:** `06-review-section.md`, then `04-plan-section.md` in `FINALIZE` mode.

Generic version of `workshop-authoring/prompts/content-generation-prompt.md`, the Home Credit instance.

## Modes

- `CREATE` — build the notebook from the approved plan.
- `REVIEW` — findings only, no file changes.
- `REVIEW_AND_FIX` — review, then implement. Use this after your own read-through, pasting your feedback into `CURATOR_FEEDBACK`.

## Prompt

````text
Build, review, or improve the participant notebook for one section of this Databricks workshop.

The approved section plan is the design. Build what it describes. Do not redesign the section or add products it does not include.

Read first (paths relative to REPOSITORY_ROOT):
1. workshop-authoring/sections/<NN>-<section>/section-plan.md — the approved plan
2. workshop-playbook/workshop-standards.md — apply every rule
3. workshop-authoring/workshop-facts.md — the only source of customer-specific facts
4. workshop-authoring/dataset/data-dictionary.md
5. Notebooks and setup assets of earlier sections this one reuses
6. Existing files for this section

Treat the implemented dataset, setup logic, and tested definitions as more authoritative than agenda wording. Preserve other sections and unrelated changes.

## Inputs

TASK_MODE: [CREATE | REVIEW | REVIEW_AND_FIX]
REPOSITORY_ROOT: [absolute path]
SECTION_NUMBER and SECTION_NAME: [from the plan]
CURATOR_FEEDBACK: [your review notes, or NONE]
DEV_WORKSPACE_PROFILE: [profile for testing, or NONE]

If an environment value is unknown, write `TBD — facilitator confirmation required` in authoring material. Do not invent IDs, permissions, features, runtimes, URLs, groups, warehouse names, or test results.

## How the plan maps to the notebook

- Notebook and Notebook exercise rows become notebook parts, in plan order, with the plan's part title as the heading.
- Slides rows do not become notebook content. Add at most one short Markdown cell that recaps the idea participants just heard, when the notebook needs it.
- Facilitator demo rows are not participant work. If the demo runs code, put it in workshop-authoring/sections/<NN>-<section>/facilitator-demo.py. In the notebook, add only a one-line pointer such as "The facilitator will show…".
- Guided participant activity rows become numbered UI steps inside the notebook.
- The opening Markdown states the plan's assignment, deliverable, and interpretation boundary. The final Markdown is the participant reflection.
- If the plan cannot be built as written (a missing column, an impossible step, not enough time), stop and say what must change in the plan. Do not quietly deviate.

## Required outputs

Notebook-led:
  workshop-content/<NN>-<section>/<NN>-lab.py   (or .sql)

Facilitator-led:
  workshop-content/<NN>-<section>/<NN>-participant-guide.md

Only when the plan needs them:
  workshop-authoring/sections/<NN>-<section>/facilitator-demo.py
  workshop-setup/section-<NN>-facilitator-setup.sql   (then rerun prompt 03 for grants and admin instructions)

Do not create a section README, exercises.md, expected-results.md, or slide outlines. Expected results go into the plan's Say lines during FINALIZE. Update workshop-content/README.md status and fix every reference to moved or removed files.

## Workflow

CREATE: read the plan and sources → build the notebook part by part → validate → report any place where the plan should change.

REVIEW: do not edit. Return findings ordered by severity, covering plan-to-notebook mismatches, unclear language, weak transitions, oversized cells, and audience-boundary problems; files to keep, move, or remove; what should stay unchanged; and validation gaps.

REVIEW_AND_FIX: evaluate each CURATOR_FEEDBACK point and say whether you agree and why → do the REVIEW → implement → validate. Preserve correct business logic and useful code. Change code only when it conflicts with the explanation, shows distracting fields, combines unrelated steps, is unsafe to rerun, uses a wrong rule, or blocks a clear workflow. If the fix changes the section's flow, list the plan updates needed.

## Validation

Apply workshop-standards.md section 11. In addition:
- every Notebook row in the plan has a matching notebook part, in the same order;
- check the core-metric boundary cases, as-of date, numerator, denominator, and grain against the facts file;
- confirm counts and percentages use the same population and rankings state a minimum group size;
- confirm participant writes and cleanup use only the participant's own prefix;
- if DEV_WORKSPACE_PROFILE is available, test Spark logic with Databricks Connect, then say which cells still need a cell-by-cell run in the workspace.

## Final response

For REVIEW: the review structure only. For CREATE or REVIEW_AND_FIX: what was built or changed, files touched, any plan changes needed, checks run with results, runtime status, open TBD values, and deliberate omissions. Do not paste whole files.
````
