# Prompt — Add Data Engineering and Machine Learning to the workshop visual

Use this prompt after the Data Engineering and Machine Learning delivery assets have been authored.

---

Update the existing workshop presenter canvas:

`/Users/sean.chang/.cursor/projects/Users-sean-chang-projects-demo-hc-workshop-hc-workshop/canvases/workshop-section-briefs.canvas.tsx`

Add the following two sections without rewriting or weakening the existing Introduction, Data Analysis, Generative AI, or Governance flows:

1. Data Engineering in Databricks
2. Introduction to Machine Learning in Databricks

Before editing:

1. Read the Cursor Canvas skill.
2. Read `workshop-authoring/agenda/workshop-agenda.md`.
3. Read the existing canvas.
4. Read every authored README, facilitator guide, slide outline, participant notebook, exercise, expected-results file, and setup asset for the two sections.
5. Treat the implemented assets and timed facilitator guides as authoritative. Do not invent a demonstration or hands-on activity merely because it appears in the high-level agenda.

For each section, add:

- The section title, scheduled time, and duration.
- One concise high-level goal describing what participants will achieve.
- A chronological, numbered delivery flow.
- For every step:
  - minute window within the section;
  - one primary mode: `Slides`, `Notebook`, `Guided UI`, or `Checkpoint`;
  - a short presenter-facing title;
  - two to four specific talking points;
  - one transition sentence that tells the presenter exactly what comes next.
- A final checkpoint that confirms the intended learning outcome or operational handover.

Quality requirements:

- The minute windows must be contiguous and add up exactly to the section duration.
- Put concepts and decision frameworks on slides.
- Put code participants execute or inspect in notebook steps.
- Put product navigation and prepared assets in Guided UI steps.
- Do not describe facilitator demonstrations as participant hands-on work.
- Keep the delivery sequence realistic; account for navigation and discussion time.
- Preserve the Unicorn Finance narrative and the existing FPD5 definition.
- Keep data-quality implementation in Data Engineering.
- For Machine Learning, clearly separate the required batch-scoring path from optional Model Serving, online features, and production monitoring extensions.
- If the authored files do not support a requested agenda item, identify the gap instead of fabricating content.

Canvas requirements:

- Keep the current presenter run-of-show interaction.
- Add the new sections to the topic selector.
- Update the authored-topic and instructional-time summaries.
- Ensure Previous and Next navigation works for every new step.
- Keep the visual flat and minimal: no gradients, shadows, decorative icons, or hardcoded colors.
- Use only `cursor/canvas` imports and host-theme tokens.
- Do not create a separate Markdown brief.
- Confirm that the Canvas TypeScript check reports no errors.

After editing, summarize:

- the ordered flow added for each section;
- any agenda items omitted because supporting assets do not yet exist;
- any timing or workspace validation still required.
