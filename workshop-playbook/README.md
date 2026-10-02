# Workshop playbook

**Updated at:** 2026-10-01

Reusable prompts for building a story-driven Databricks enablement workshop like the Home Credit Philippines workshop delivered on 22 September 2026.

To start a new workshop, copy this folder into the new repository, fill in the facts file, and run the prompts in order.

## Contents

| File | Purpose |
|---|---|
| [`workshop-standards.md`](workshop-standards.md) | Rules every prompt applies: story, plain English, audience boundaries, notebook structure, multi-participant safety, section-plan and slide formats, Databricks correctness, validation. Not customer-specific |
| [`workshop-facts-template.md`](workshop-facts-template.md) | Template for everything customer-specific: audience, fictional story, core metric, dataset, catalog, environment, sections, glossary |
| [`examples/home-credit-unicorn-finance-facts.md`](examples/home-credit-unicorn-finance-facts.md) | Completed facts file for the Home Credit workshop |
| [`prompts/`](prompts/) | One prompt per build stage |

## Build order

| Step | Prompt | Produces |
|---|---|---|
| 1 | [`01-design-workshop.md`](prompts/01-design-workshop.md) | Facts file, story, agenda, participant opening scenario, repository skeleton |
| 2 | [`02-build-dataset.md`](prompts/02-build-dataset.md) | Dataset design, data dictionary, ER diagram, deterministic generator, validation SQL, reference values |
| 3 | [`03-build-environment-setup.md`](prompts/03-build-environment-setup.md) | Schema and shared-asset setup, grants, admin instructions (Markdown and PDF) |
| 4 | [`04-plan-section.md`](prompts/04-plan-section.md) | Section plan: outcomes, what to present, what to go through in the notebook. Becomes the facilitator's quick reference |
| 5 | [`05-build-section-notebook.md`](prompts/05-build-section-notebook.md) | Participant notebook (or participant guide), built from the plan |
| 6 | [`06-review-section.md`](prompts/06-review-section.md) | Read-only review with a verdict |
| 7 | [`07-generate-slide-prompts.md`](prompts/07-generate-slide-prompts.md) | Slide-only prompt per section, opening and closing content, master slide package |

Steps 1 to 3 run once for the workshop. Steps 4 to 7 repeat for each section in agenda order. Start with the section that defines the core metric.

### Per-section flow

Each section ends with three files: the plan, the notebook, and the slide prompt.

```text
04 PLAN ─▶ approve ─▶ 05 CREATE ─▶ your read-through ─▶ 05 REVIEW_AND_FIX ─▶ 06 review ─▶ 04 FINALIZE ─▶ 07 slide prompt
```

1. **Plan.** Run prompt 04 in `PLAN` mode. Approve the outcomes and the delivery map (which parts are slides, notebook, demo, or exercise) before any notebook exists.
2. **Notebook.** Run prompt 05 in `CREATE` mode. It builds what the plan describes.
3. **Your review.** Read the notebook yourself and write down what confuses you. Run prompt 05 in `REVIEW_AND_FIX` mode with your notes as `CURATOR_FEEDBACK`, then prompt 06.
4. **Finalize the plan.** Run prompt 04 in `FINALIZE` mode. It aligns the plan with the finished notebook and adds the talking points and reference results, so the plan becomes your facilitator guide.
5. **Slide prompt.** Run prompt 07 for the section.
6. **Setup.** Rerun prompt 03 if the section added a shared asset, grant, or required feature.

## Repository layout these prompts produce

```text
participant-materials/    opening scenario and reference PDFs for participants
workshop-content/         one participant entry point per section
workshop-setup/           admin setup, dataset generator, grants, admin instructions
workshop-authoring/
├── workshop-facts.md     filled-in facts file
├── story/  agenda/  dataset/
├── opening/  closing/
└── sections/<NN>-<section>/   section plan, slide prompt, optional facilitator demo, drafts
```

## Lessons from the Home Credit workshop

These are built into the standards and prompts. They are listed here so the reasons are not lost.

- **Story first.** Early notebooks felt like "running cells". Each part now answers one business question, and each step says why it is needed.
- **One participant file per section.** Separate README, exercises, and expected-results files made participants switch context. Everything participants need now lives in the notebook.
- **Plain English.** Sentences like "establish the origination context" were too hard for participants new to the domain or reading in a second language.
- **Describe the business event concretely.** "0% smartphone promotion" was unclear until it was explained as a point-of-sale installment loan at 0% interest, subsidized by the brand, and not a free phone.
- **Realistic notebook code.** Heavy configuration at the top confused participants. Code should look like what an inherited team would actually run.
- **Individual exercises.** Invented "teams" caused confusion. Participant assets use an automatic per-user prefix, and Genie Agents stay private in each user's folder.
- **The facilitator may not have access to the participant workspace.** The customer's admin runs all setup from written instructions, and demos run in the facilitator's own workspace. Setup is never part of the participant flow.
- **Create the catalog manually.** `CREATE CATALOG` from code failed because the account used Default Storage. The admin creates the catalog in Catalog Explorer first.
- **Minimum grants.** Participants do not need catalog-wide `ALL PRIVILEGES` or `MANAGE`.
- **Plan before the notebook, and keep one document.** In this workshop the slides-versus-notebook split was worked out after the notebooks, and the facilitator guide, slide prompts, and notebooks repeatedly drifted apart. The section plan now decides the split first and later becomes the facilitator guide.
- **Short facilitator reference.** Long guides were unreadable during delivery, and generic advice such as "use plain language" was noise. The useful parts were the delivery map (time, mode, focus) and the key ideas to say.
- **Content-first slide prompts.** Slide-by-slide prompts over-constrained the slide model. The final prompts give content and boundaries, and cover only the Slides windows in the delivery map.
- **Lock section numbers early.** Dropping Section 04 without renumbering caused repeated confusion about why Governance was Section 05.
- **Test in two loops.** Use Databricks Connect for fast Spark checks, then run the real notebook cell by cell in the workspace from a clean session.

## Home Credit instance

The prompts used to build this repository's sections are kept as the Home Credit instance:

- [`../workshop-authoring/prompts/content-generation-prompt.md`](../workshop-authoring/prompts/content-generation-prompt.md)
- [`../workshop-authoring/prompts/content-review-prompt.md`](../workshop-authoring/prompts/content-review-prompt.md)
- [`../workshop-authoring/prompts/generate-workshop-closing-slides.md`](../workshop-authoring/prompts/generate-workshop-closing-slides.md)
