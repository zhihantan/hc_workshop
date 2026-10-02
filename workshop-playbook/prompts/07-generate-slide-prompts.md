# Prompt 07 — Generate the slide prompts

**Use when:** a section plan has been finalized against its notebook (`04-plan-section.md`, mode `FINALIZE`). Run it per section as each one is finished, or once for all sections plus the opening and closing.
**Produces:** one slide-only prompt per section, opening-slide content, closing-slide content, and one consolidated master package to hand to a slide-generating model (for example Claude Design).
**Next:** generate the decks, then check them against each section plan.

Example outputs in this repository:

- `workshop-authoring/sections/01-data-analysis-in-databricks/generate-section-01-data-analysis-slides-v3-slide-only.md`
- `workshop-authoring/opening/workshop-opening-slides.md`
- `workshop-authoring/closing/workshop-closing-slides.md`
- `workshop-authoring/sections/all-sections-slide-generation-master.md`

## Why this shape

Three versions were tried for the Home Credit workshop. Prescriptive slide-by-slide prompts over-constrained the slide model. Content-first prompts (messages, facts, boundaries) worked better. The final version also limits each prompt to the Slides rows of the delivery map, so notebook and demo work never turns into slides.

## Prompt

````text
Create the slide-generation material for this workshop.

Read first:
1. workshop-playbook/workshop-standards.md (section 9: slide rules)
2. workshop-authoring/workshop-facts.md
3. workshop-authoring/agenda/workshop-agenda.md
4. workshop-authoring/story/<company>-story.md and participant-materials/<company>-workshop-scenario.md
5. For each section: section-plan.md (authoritative for Slides rows and the messages that must land) and the participant entry point

## Inputs

REPOSITORY_ROOT: [absolute path]
SECTIONS: [section numbers to cover, or ALL]
SLIDE_TOOL: [for example Claude Design, Google Slides via another model]
STYLE_NOTES: [for example clean 16:9, restrained Databricks accents]
INCLUDE_HANDS_ON_SLIDES: [yes | no — terse "do this now" walkthrough slides for each lab step]

## Part A — One slide-only prompt per section

Write workshop-authoring/sections/<NN>-<section>/generate-section-<NN>-<topic>-slides.md containing:

1. Scope: the total slide minutes and the statement that only the Slides rows of the section plan's delivery map are covered.
2. Source authority, in order: section plan, participant entry point, scenario, agenda.
3. Delivery contract: a table of each Slides row (time, minutes, purpose) and the exact point where the presentation hands over to the notebook or demo. Suggest an approximate slide count but let the slide model choose the count and titles.
4. Audience and role, including the fiction boundary.
5. Visible-slide content: the Cover and Say bullets of each Slides row, expanded into the messages that must land, definitions, and distinctions, written as content, not slide layouts.
6. Recommended visual ideas (simple diagrams, no fabricated screenshots).
7. What presenter notes may contain, and the final transition sentence.
8. Excluded from visible slides: every notebook, demo, and guided step in the section, by name.
9. Output request: proposed narrative and slide count, visible content, presenter notes, visuals, timing across the slide window, the transition, and a coverage check confirming no excluded topic became a slide.

## Part B — Opening slides

Write workshop-authoring/opening/workshop-opening-slides.md: about three slides for 5–7 minutes showing (1) the agenda as one journey, (2) the story and the participant's role with the interpretation boundary, (3) the data participants will explore — catalog and schemas, table lifecycle diagram, table list. Give visible content, visual, presenter notes, and transition for each.

## Part C — Closing slides

Write workshop-authoring/closing/workshop-closing-slides.md as slide content only (not a prompt to generate it): about seven slides for 8–10 minutes that mirror the opening — where the day started, the question chain across sections, what was delivered per section, before-versus-after ownership, the controls every asset needs, who owns what on Monday, and a one-minute participant reflection card. Presenter notes must distinguish participant work from facilitator demos.

## Part D — Master package

Write workshop-authoring/sections/all-sections-slide-generation-master.md: how to use it with SLIDE_TOOL, global rules, shared context (story, core metric, reference values marked "reveal only after the matching exercise", catalog layout), then opening, each section in agenda order (A. content slides; B. hands-on step list labelled Slides, Participant, Participant exercise, Facilitator demo, Guided, Discussion, if INCLUDE_HANDS_ON_SLIDES), closing content, and a coverage checklist. State which section numbers do not exist.

Also update workshop-authoring/sections/content-first-slide-prompts.md (or create it) as an index of the final prompts.

## Rules

- No full code, seeded results before their exercise, unverified screenshots, or invented workspace evidence on slides.
- Every definition and number matches the facts file exactly.
- Do not create slides for sections that were not built.

## Final response

List the files written, the slide minutes per section, and any section where the plan has no Slides row or where the plan and participant asset disagree.
````
