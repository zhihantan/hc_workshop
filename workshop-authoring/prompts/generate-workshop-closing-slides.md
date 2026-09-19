# Slide-generation brief — Unicorn Finance workshop close

Use this document as a complete prompt for an LLM that generates presentation slides or as a curation guide for manually building the closing deck.

The detailed source copy is in [`../closing/workshop-closing-slides.md`](../closing/workshop-closing-slides.md). Day-of delivery guidance is in [`../closing/facilitator-notes.md`](../closing/facilitator-notes.md).

## Instructions for the slide-generating LLM

Create a 16:9 closing deck for the final 8–10 minutes of a full-day Databricks workshop.

Produce seven core slides and one optional final slide. For every slide:

- provide a concise title;
- keep visible text to one message, up to five short bullets, or one simple comparison;
- recommend a visual or diagram;
- write detailed presenter notes;
- include a transition to the next slide;
- label the slide as `Essential` or `Optional`;
- label the content strategy as `Create new`, `Curate existing collateral`, or `Hybrid`.

Use clean enterprise visuals with restrained Databricks orange/red accents. Prefer one coherent visual story over product-logo wallpaper. Do not use decorative stock photography, full code listings, unverified workspace screenshots, invented participant results, or unsupported production-readiness claims.

The closing deck must mirror the opening Unicorn Finance narrative. It is not a product-feature recap.

## Workshop scenario

- Unicorn Finance Philippines is a fictional consumer lender.
- Atlas Ridge Consulting delivered a Databricks lakehouse and is handing operation to Unicorn Finance's internal team.
- A smartphone brand funded a limited 0% point-of-sale promotion.
- Application and approval volumes increased.
- FPD5 behavior appears concentrated in a small number of stores and sales associates.
- The pattern is an investigation signal, not proof of fraud, misconduct, or causality.
- All workshop data and results are synthetic.

For this workshop, FPD5 means the first installment reached five days past due before full settlement. Include only contracts whose first installment reached that observation point by the as-of date, 2026-09-01. A null settlement date, or settlement on or after day five, counts as FPD5. The denominator is eligible contracts, not all applications or approvals.

## Closing narrative

The deck must make this transformation explicit:

```text
START OF DAY
Inherited assets
Unresolved promotion signal
Unknown dependencies
Partner-to-internal-team handover

        ↓ workshop delivery ↓

END OF DAY
Reproducible evidence
Reviewed and validated improvements
Repeatable, monitored workloads
Layered access diagnosis and lineage
Tracked model and governed batch scores
Named ownership, monitoring, and recovery responsibilities
```

The final message is:

> The partner delivered the starting platform. Unicorn Finance now has a method for trusting, governing, operating, recovering, and improving what it owns.

## Outcomes delivered across the day

### Introduction to Databricks

Participants established a shared map of the workspace, Unity Catalog, compute surfaces, and the difference between data assets and workspace assets.

### Data Analysis in Databricks

The intended Unicorn Finance delivery is:

- a reproducible FPD5 cohort and hotspot analysis;
- a participant-owned Delta investigation result with history;
- a governed Metric View;
- a reconciled AI/BI Dashboard;
- a private Genie Agent with a verified baseline;
- SQL workload evidence from monitoring and query inspection.

### Generative AI in Databricks

The intended delivery is:

- an explained and extended regional FPD5 analysis;
- a repaired semantic denominator bug with executable checks;
- reviewed and documented, result-preserving improvements;
- a validated unpublished dashboard draft;
- optionally, a regression-tested Genie Agent improvement.

The message is not that AI output is automatically trustworthy. Governed definitions, permissions, review, and executable validation remain mandatory.

### Data Engineering in Databricks

The intended delivery is selected logic made repeatable through orchestrated Jobs and Lakeflow capabilities, explicit data-quality behavior, monitoring, and recovery responsibilities.

### Governance and Access Control

The intended delivery is:

- a reusable access-diagnostic sequence;
- evidence distinguishing workspace access, runtime identity, and Unity Catalog privileges;
- the narrowest repair for a controlled missing-privilege scenario;
- lineage-based downstream-impact evidence;
- a Consumer Lending discovery structure that organizes assets without granting access.

This was designed as a facilitator-led demonstration. Do not imply that participants ran or cloned the restricted-identity notebook.

### Machine Learning in Databricks

The intended delivery is:

- a leakage-safe, time-split FPD5 classifier;
- an MLflow run with parameters, metrics, and artifacts;
- a Unity Catalog registered model with a champion alias and lineage;
- governed batch-scoring output;
- ownership decisions covering retraining, monitoring, promotion, and rollback.

Predictions support investigation and prioritization; they do not establish fraud or misconduct.

## Slide specifications

### Slide 1 — At 9:00 AM: inherited assets, unanswered questions

**Priority:** Essential
**Strategy:** Create new

Show the partner handover, the 0% promotion signal, the non-causality warning, and the transfer of operating responsibility.

Key message:

> Assets existed. Trust and ownership still had to be established.

### Slide 2 — One question took us through the whole platform

**Priority:** Essential
**Strategy:** Create new

Use this question chain:

```text
What happened?
→ Can we trust the evidence?
→ Can the logic run repeatedly?
→ Can the right people use it safely?
→ Can we use it to support future decisions?
```

Map the stages to Analysis, AI-assisted development, Data Engineering, Governance, and Machine Learning.

### Slide 3 — By 5:00 PM: investigation became operated assets

**Priority:** Essential
**Strategy:** Hybrid

Show a stack connecting:

- trusted evidence;
- reviewed AI-assisted delivery;
- repeatable workloads;
- governed access and lineage;
- tracked model and batch scores.

Show validation, monitoring, and ownership as controls crossing every layer.

### Slide 4 — The handover changed from possession to control

**Priority:** Essential
**Strategy:** Create new

Use a two-column before-and-after comparison:

- inherited assets → understood dependencies and named responsibilities;
- easy-to-misstate metric → one governed definition;
- one-time analysis → repeatable, observable operation;
- access as yes/no → layered least-privilege diagnosis;
- model idea → tracked model, governed scores, and operating decisions.

Clarify in presenter notes that the workshop established the method; it did not make every artifact production-ready.

### Slide 5 — Trust came from controls, not from product names

**Priority:** Essential
**Strategy:** Create new

Show that every asset needs:

1. a business purpose and owner;
2. a governed source and definition;
3. appropriate compute and permissions;
4. an executable validation check;
5. a monitoring location;
6. a recovery or rollback action.

### Slide 6 — What Unicorn Finance owns on Monday

**Priority:** Essential
**Strategy:** Create new

Map responsibilities to:

- analysis owner;
- pipeline operator;
- data steward;
- model owner;
- platform team.

Treat these as responsibilities rather than mandatory job titles.

### Slide 7 — Make the handover real

**Priority:** Essential
**Strategy:** Create new

Create a participant reflection card asking for:

- one asset;
- its business purpose;
- its internal owner;
- one validation;
- its monitoring location;
- its first recovery action;
- its biggest operating blocker.

Allow 60–90 seconds for reflection and two short responses.

### Optional Slide 8 — The platform was delivered. Ownership starts now.

**Priority:** Optional
**Strategy:** Create new

Return to the handover visual from Slide 1. Move the assets fully to the Unicorn Finance side and replace the unresolved question with:

- Trust
- Operate
- Govern
- Improve

Close with:

> We started with inherited assets and an investigation signal. We finish with evidence, controls, operated workloads, and named responsibilities.

## Day-of accuracy requirements

The facilitator will classify activities as participant-completed, facilitator-demonstrated, discussed only, or skipped. Write presenter notes that can be adjusted to those distinctions.

Never say “you built,” “you tested,” or “you validated” unless participants actually completed that activity. Safe alternatives include:

- “We examined how to build…”
- “The facilitator demonstrated…”
- “We defined the validation required…”
- “The target delivery is…”

Do not insert exact FPD5 rates, pipeline status, model metrics, or participant findings unless the facilitator supplies verified values after the live activities.

## Final output requirements

Return:

1. a slide-by-slide deck with visible copy;
2. presenter notes for each slide;
3. a visual recommendation for each slide;
4. a transition for each slide;
5. a final list of day-of fields the facilitator must verify;
6. a statement confirming that no synthetic result was presented as a Home Credit production outcome.
