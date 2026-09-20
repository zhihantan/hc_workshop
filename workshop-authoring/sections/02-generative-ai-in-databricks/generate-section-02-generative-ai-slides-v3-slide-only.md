# Final slide-only generation prompt — Generative AI in Databricks

Create the visible presentation slides for the opening **5 minutes** of the 60-minute Generative AI in Databricks workshop.

This prompt intentionally covers only the portion marked **Slides** in the facilitator delivery map. The remaining 55 minutes are delivered through the participant notebook, facilitator dashboard demonstration, optional private-Agent activity, and discussion.

## Source authority

Resolve conflicts in this order:

1. `facilitator-guide.md`
2. `../../../workshop-content/02-generative-ai-in-databricks/02-lab.py`
3. `drafts/generate-section-02-generative-ai-slides-v2-content-first.md`
4. `expected-results.md`
5. `facilitator-demo.py`
6. `README.md`
7. `../../../participant-materials/unicorn-finance-workshop-scenario.md`
8. `../../agenda/workshop-agenda.md`

## Delivery contract

Generate the smallest useful deck for this slide window:

| Time | Duration | Visible slide purpose |
|---|---:|---|
| 11:15–11:20 | 5 minutes | Genie Code's role and the developer's validation responsibility |

At 11:20, transition to `02-lab.py` and keep the visible presentation closed. Do not create later slides for the regional exercise, governed checkpoint, PySpark repair, `/optimize`, `/doc`, dashboard demonstration, optional Genie Agent extension, or final reflection.

Aim for approximately **2–3 concise slides**. Choose the exact count and titles yourself.

## Audience and continuity

- The real audience is Home Credit Philippines.
- Participants act as developers supporting Unicorn Finance's risk analytics team.
- Section 01 established a governed FPD5 baseline and a private Genie Agent.
- This section uses Genie Code to accelerate inherited technical work without weakening review or validation.
- The promotion remains Nova Mobile's fictional 0%-interest smartphone financing campaign.
- Elevated FPD5 remains an investigation signal, not proof of fraud or causality.

## Visible-slide content

### The handover assignment

Participants inherit analytical work that must be understood, extended, repaired, checked, and documented for the next developer.

Their section-level outcome is one validated personal notebook containing:

- an explained inherited query;
- a regional extension;
- an independently reconciled result;
- a repaired PySpark helper with executable checks;
- concise handover documentation.

Present this as the assignment, not as a preview of the answers.

### What Genie Code contributes

Genie Code can help a developer:

- explain existing SQL and PySpark;
- propose a plan before changing code;
- generate focused edits;
- run approved notebook actions;
- suggest optimization and documentation;
- help author a draft AI/BI Dashboard.

Do not present execution as proof of correctness.

### Human responsibility and working discipline

The core message is:

> Genie Code makes technical work faster, but governed definitions, permissions, human review, and independent validation make it trustworthy.

Use this working pattern:

```text
Context → concrete outcome → review → execute → governed reconciliation
```

The developer remains responsible for:

- selecting the governed source;
- preserving the eligible-contract denominator;
- reviewing plans and diffs before approval;
- validating generated results independently;
- rejecting unsupported performance or causal claims;
- documenting evidence for the next owner.

## Recommended visual ideas

Use simple visuals such as:

- an inherited notebook moving through understand → extend → repair → validate → hand over;
- a human-in-the-loop approval cycle;
- the five-step working pattern above;
- a trust boundary separating AI-generated proposals from governed validation.

Do not use detailed code, regional results, the 100% bug output, dashboard screenshots, or Agent responses on these opening slides.

## Presenter notes

Presenter notes may:

- refresh the trusted Section 01 FPD5 baseline without displaying its rates;
- distinguish Genie Code assistance from autonomous approval;
- explain that generated notebook cells still run on notebook compute;
- introduce `@` resources, `@cell`, and approval prompts verbally if useful;
- transition participants into their personal notebook clone.

End with:

> First, we will ask Genie Code to explain the inherited query before we allow it to change anything.

## Excluded from visible slides

Do not create slides for:

- regional values, rankings, or the 20-contract threshold;
- the governed reconciliation query;
- the inherited 100% PySpark result or its repair;
- executable assertion details;
- `/optimize` or `/doc` outputs;
- notebook-versus-warehouse debriefs;
- the disposable dashboard build;
- the optional private Genie Agent improvement;
- final ownership reflection.

Those topics belong to the live notebook or demonstration.

## Output request

Return:

1. the proposed slide count and narrative;
2. concise visible slide content;
3. presenter notes for each slide;
4. recommended visuals;
5. exact timing across the 5-minute slide window;
6. the final transition into `02-lab.py`;
7. a coverage check confirming that no excluded live-workspace topic became a visible slide.

Use a clean 16:9 workshop style. Keep the opening focused on working discipline and accountability rather than a broad generative-AI product tour.
