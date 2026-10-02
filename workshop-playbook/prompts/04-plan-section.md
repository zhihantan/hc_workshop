# Prompt 04 — Plan a section

**Use when:** before any notebook is written for a section (mode `PLAN`), and again once the notebook is built (mode `FINALIZE`).
**Produces:** `workshop-authoring/sections/<NN>-<section>/section-plan.md`, which becomes the facilitator's quick reference after `FINALIZE`.
**Next:** after `PLAN`, run `05-build-section-notebook.md`. After `FINALIZE`, run `07-generate-slide-prompts.md`.

The plan is the foundation of the section. It decides the outcomes, what you present, and what participants go through in the notebook. The notebook and the slide prompt are both built from it.

## Prompt

````text
Plan one section of this Databricks workshop.

Read first (paths relative to REPOSITORY_ROOT):
1. workshop-playbook/workshop-standards.md — section 8 defines the plan format
2. workshop-authoring/workshop-facts.md — this section's assignment, deliverable, topics, and dependencies
3. workshop-authoring/story/<company>-story.md
4. workshop-authoring/agenda/workshop-agenda.md
5. workshop-authoring/dataset/data-dictionary.md
6. Plans and notebooks of earlier sections this one reuses
7. In FINALIZE mode: the section's participant entry point and any facilitator-demo file

## Inputs

TASK_MODE: [PLAN | FINALIZE]
REPOSITORY_ROOT: [absolute path]
SECTION_NUMBER and SECTION_NAME: [from the agenda]
SCHEDULED_TIME: [for example 9:45–11:15, 90 minutes]
DELIVERY_MODE: [NOTEBOOK_LED | FACILITATOR_LED]
MUST_PRESENT: [ideas that must be on slides, for example "notebook versus SQL warehouse compute"; or DERIVE]
MUST_DEMO: [things the facilitator shows rather than participants doing them; or DERIVE]
MUST_SAY_POINTS: [reminders for delivery; or NONE]
CURATOR_FEEDBACK: [your notes on a previous draft, or NONE]

## PLAN mode

1. Write the Outcomes block: one assignment question, what participants leave with, two to four ideas they can explain, and what the section reuses or depends on.
2. Design the delivery map. Follow the delivery pattern in workshop-standards.md section 2. Decide for every part whether it is Slides, Notebook, Notebook exercise, Facilitator demo, Guided participant activity, or Discussion, and how many minutes it gets.
   - Put concepts and decision frameworks on Slides. Keep slide time short; most time goes to hands-on work.
   - Put anything participants run or inspect in the Notebook.
   - Use Facilitator demo for steps participants cannot do safely or in time.
   - Include navigation and discussion time. Rows must add up exactly to the duration.
3. Write one block per delivery-map row with Goal, Cover, and (for exercises) Participant action. For Slides rows, Cover lists the messages that must land. For Notebook rows, Cover lists the steps and the evidence each one produces. Leave Say empty.
4. List anything the section needs from setup (shared views, Metric Views, grants, features) under Reuses / depends on.
5. Set Status to PLANNED.

Stop and present the plan for approval. Flag topics that do not fit the time or the story, and recommend whether to cut, demo, or make them optional.

## FINALIZE mode

1. Read the notebook end to end. It is now the source of truth for order and content.
2. Update the delivery map and blocks so they match the notebook. Report every change you make.
3. Fill each Say line with what the facilitator must say: definitions, distinctions, thresholds, caveats, and reference results from the facts file, marked to reveal only after the matching discovery step. Place the MUST_SAY_POINTS where they belong.
4. Add the participant entry point link and set Status to NOTEBOOK BUILT. Set DELIVERY READY only after a workspace run and a rehearsal are confirmed.
5. Check that the plan still fits on about two printed pages. Cut wording before cutting content.

If asked for offline study material, render all section plans to PDF and combine them into one file.

## Rules

- Apply workshop-standards.md, especially section 2 (one story) and section 8 (plan format).
- Part titles are questions, not product names.
- No generic presentation advice, setup steps, or troubleshooting in the plan.
- Every definition and number matches the facts file.

## Final response

PLAN: show the Outcomes block and the delivery map, and list open questions. FINALIZE: list the changes made to match the notebook, any notebook problems found, and the current status.
````
