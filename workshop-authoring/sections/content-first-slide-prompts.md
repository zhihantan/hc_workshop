# Slide-generation prompts

Use the final slide-only prompts for Sections 01, 02, 03, 05, and 06 when generating the decks used during delivery. They contain only the visible slide portions from each facilitator guide.

The broader content-first prompts remain available as editorial inventories. The original prompts remain detailed prescriptive references.

## Final slide-only prompts

- [Data Analysis in Databricks](01-data-analysis-in-databricks/generate-section-01-data-analysis-slides-v3-slide-only.md)
- [Generative AI in Databricks](02-generative-ai-in-databricks/generate-section-02-generative-ai-slides-v3-slide-only.md)
- [Data Engineering in Databricks](03-data-engineering-in-databricks/generate-section-03-data-engineering-slides-v3-slide-only.md)
- [Governance and Access Control in Databricks](05-governance-and-access-control/generate-section-05-governance-slides-v3-slide-only.md)
- [Introduction to Machine Learning in Databricks](06-machine-learning-in-databricks/generate-section-06-machine-learning-slides-v3-slide-only.md)

These prompts encode:

- exact slide windows from the facilitator guide;
- visible slide topics;
- presenter-note boundaries;
- transitions into notebooks and demonstrations;
- explicit exclusions for live-workspace content.

## Why the content-first versions remain

The original prompts describe a specific slide-by-slide solution. They remain useful as detailed editorial references, but they can over-constrain a presentation-generating LLM.

The content-first versions instead provide:

- the business narrative;
- the messages that must land;
- authoritative definitions and validated facts;
- facilitator and participant responsibilities;
- live-workspace boundaries;
- scope exclusions and claims to avoid;
- the required output from the presentation-generating LLM.

They deliberately leave these decisions to the downstream LLM:

- slide count;
- slide titles;
- sequence and grouping;
- layouts and visual language;
- which ideas should be combined;
- which detail belongs on-screen or in presenter notes.

## Broader content-first prompts

- [Data Analysis in Databricks](01-data-analysis-in-databricks/drafts/generate-section-01-data-analysis-slides-v2-content-first.md)
- [Generative AI in Databricks](02-generative-ai-in-databricks/drafts/generate-section-02-generative-ai-slides-v2-content-first.md)
- [Data Engineering in Databricks](03-data-engineering-in-databricks/drafts/generate-section-03-data-engineering-slides-v2-content-first.md)
- [Governance and Access Control in Databricks](05-governance-and-access-control/drafts/generate-section-05-governance-slides-v2-content-first.md)
- [Introduction to Machine Learning in Databricks](06-machine-learning-in-databricks/drafts/generate-section-06-machine-learning-slides-v2-content-first.md)

## Original prescriptive prompts

These are preserved for comparison and detailed editorial reference:

- [Data Analysis — original](01-data-analysis-in-databricks/drafts/generate-section-01-data-analysis-slides.md)
- [Generative AI — original](02-generative-ai-in-databricks/drafts/generate-section-02-generative-ai-slides.md)
- [Data Engineering — slide outline](../../workshop-content/03-data-engineering-in-databricks/slide-outline.md)
- [Governance — original](05-governance-and-access-control/drafts/generate-section-05-governance-slides.md)
- [Machine Learning — slide outline](../../workshop-content/06-machine-learning-in-databricks/slide-outline.md)

## Recommended workflow

1. For Sections 01, 02, 03, 05, and 06, give the final slide-only prompt to the presentation-generating LLM.
2. Ask it to explain its proposed narrative and information architecture before finalizing slide copy.
3. Check the generated deck against the facilitator guide's slide windows and exclusions.
4. Use the broader content-first prompt to check factual coverage and presenter notes.
5. Use the original prompt only to check details that may have been lost—not to force the old slide structure.
6. Supply verified screenshots or existing collateral only after the narrative is approved.
7. Complete the prompt's fact, claim, environment, and rehearsal checklist before export.
