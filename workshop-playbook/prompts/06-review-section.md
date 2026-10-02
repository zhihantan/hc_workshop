# Prompt 06 — Review assets (read-only)

**Use when:** a section plan, notebook, slide prompt, or setup asset is drafted; again before release.
**Produces:** a severity-ordered review with a verdict. No file changes.
**Next:** fix accepted findings with `04-plan-section.md` (plan findings) or `05-build-section-notebook.md` in `REVIEW_AND_FIX` mode (notebook findings).

Generic version of `workshop-authoring/prompts/content-review-prompt.md`, the Home Credit instance.

## Prompt

````text
Review completed workshop assets. Do not edit, move, create, or delete files. Do not change any Databricks resource, permission, dashboard, Agent, job, pipeline, model, or data.

Read first (paths relative to REPOSITORY_ROOT):
1. workshop-playbook/workshop-standards.md — every applicable rule is a review criterion
2. workshop-authoring/workshop-facts.md
3. Every asset in REVIEW_TARGETS
4. The section plan
5. The related participant entry point, read start to finish
For STANDARD depth also read the story, agenda, dataset design, data dictionary, the whole section folder, and its setup files.
For THOROUGH depth also read downstream sections that reuse this section's labels, tables, models, dashboards, or Agents.

## Inputs

REPOSITORY_ROOT: [absolute path]
REVIEW_TARGETS: [files or folders]
TARGET_TYPE: [COMPLETE_SECTION | SECTION_PLAN | PARTICIPANT_ASSET | SETUP_ASSET | SLIDE_PROMPT]
SECTION_NUMBER and SECTION_NAME: [or N/A]
SECTION_DURATION_MINUTES: [or N/A]
EXPECTED_PARTICIPANT_OUTCOME: [what participants should understand, create, or hand over]
RUNTIME_EVIDENCE: [NONE | workspace, identity, compute, results already available]
REVIEW_DEPTH: [QUICK | STANDARD | THOROUGH]

## Focus by target type

- COMPLETE_SECTION: everything, including whether the plan, notebook, and slide prompt agree.
- SECTION_PLAN: the format in standards section 8; one assignment and a concrete deliverable; part titles are questions; the delivery map adds up to the duration; slide time is short and hands-on time dominates; demos are not labelled as participant work; after FINALIZE, the plan matches the notebook and reference results match the facts file; no generic presentation advice or setup steps.
- PARTICIPANT_ASSET: matches the plan's Notebook rows in order; story, plain English, notebook structure, exercises, audience boundary, core-metric correctness, multi-participant safety.
- SETUP_ASSET: idempotence, minimum grants, no hard-coded storage or IDs, admin can run it without facilitator access, clear success signal.
- SLIDE_PROMPT: covers only the Slides rows of the section plan's delivery map; content-first, not slide-by-slide; no early answers or code; explicit exclusions; transition into the live part.

## Severity

- Blocker: unsafe, cannot run, teaches a wrong rule, exposes data or private assets, or blocks the outcome.
- High: participant can proceed but learns something wrong or misleading, the story breaks, or participant material contains facilitator-only content.
- Medium: usable but harder than necessary — jargon, weak transitions, unused fields, unclear completion criteria, missing minimum group size.
- Low: a focused improvement with no real learning or correctness impact.

Do not inflate preferences into findings. Combine findings with the same root cause.

## Each finding

[ID] [Severity] Short title
Evidence: <path:line or section>
Current behavior: <what exists>
Why it matters: <reason>
Recommended change: <specific fix, including replacement wording for language findings>

## Output, in order

1. Verdict: NOT READY (any Blocker or High) | READY WITH FIXES | READY FOR RUNTIME VALIDATION | READY FOR DELIVERY (only with participant-equivalent runtime evidence and a facilitator rehearsal).
2. Summary in five bullets or fewer: the journey, the strongest part, the main risk, finding counts by severity, runtime status.
3. Findings by severity.
4. Participant journey in plain language (N/A for standalone setup assets).
5. File and audience boundaries: participant entry point, other participant files, facilitator files, setup files, redundant files, broken references.
6. What should remain unchanged.
7. Validation status: static checks passed, runtime checks proven, runtime checks missing, unresolved environment values.
8. Recommended fix order, by finding ID.

Never claim runtime success from reading code. Keep the review concise; evidence matters more than volume.
````
