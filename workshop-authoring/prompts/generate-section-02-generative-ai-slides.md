# Slide-generation brief — Section 02: Generative AI in Databricks

Use this document either as a complete prompt for an LLM that can generate presentation slides or as a curation guide for selecting and adapting existing Databricks slides.

## Instructions for the slide-generating LLM

Create a 16:9 deck for a 60-minute workshop section.

For every slide:

- provide a concise title;
- keep visible text to one message, three to five short bullets, or one simple comparison;
- recommend a visual, diagram, or verified product screenshot;
- write detailed presenter notes;
- include the live-demo or participant-activity transition when applicable;
- label the slide as `Essential` or `Optional`;
- label the content strategy as `Create new`, `Curate existing collateral`, or `Hybrid`.

Use clean Databricks-style enterprise visuals, restrained orange/red accents, and diagrams over dense prose. Do not use decorative stock photography, full code listings, unsupported claims, or unverified workspace screenshots.

Treat the implemented section assets and timed facilitator guide as more authoritative than the high-level agenda. Concepts and decision frameworks belong on slides. Code, generated results, UI navigation, and operational evidence belong in the live workspace.

## Authoritative scope decision

This is a Genie Code productivity section, not a broad generative-AI product tour.

The high-level agenda mentions AI Gateway, AI Toolkit, Genie One, and an introductory Genie demonstration. Those topics are not implemented in the section assets:

- Do not add AI Gateway, AI Toolkit, Genie One, Benchmarks, or a second Genie introduction to the core deck.
- Section 01 already introduced Genie Agents and had participants create a private Agent.
- If a stakeholder requires the unsupported agenda topics, use one optional parking-lot slide and state that no supporting workshop exercise has been authored.

Core message:

> Genie Code makes technical work faster, but governed definitions, permissions, and human validation still make it trustworthy.

Repeatable working pattern:

> Context → concrete outcome → review → execution → independent validation

The user remains responsible for source selection, permissions, semantic correctness, validation, and approval.

## Workshop scenario and analytical facts

- Unicorn Finance Philippines is a fictional consumer lender.
- Atlas Ridge Consulting has handed over an inherited Databricks lakehouse.
- The section continues the 0% smartphone promotion and FPD5 investigation from Section 01.
- Participants reuse `hc_workshop.workshop_shared.fpd_metrics`.
- The PySpark validation exercise uses `hc_workshop.workshop_shared.fpd_analysis`.
- All workshop data is synthetic.
- Elevated FPD5 is an investigation signal, not proof of fraud or causality.

Canonical FPD5 definition:

> Include only first installments for which `due_date + 5 days` is on or before the observation date. A null settlement date, or settlement on or after day five, counts as FPD5. The denominator is eligible contracts, not all applications or approvals.

Observation date:

> 2026-09-01

Reference cohort rates:

- 0% smartphone promotion: approximately 42.26%
- Other eligible originations: approximately 21.03%

These rates may now be used as validation checkpoints because participants completed the initial investigation in Section 01.

## Section analysis

### Outcomes

By the end of the section, participants should be able to:

1. use notebook, cell, and data context to understand inherited work;
2. generate and refine governed SQL analysis with a structured prompt;
3. validate generated work against independent invariants;
4. diagnose and repair a realistic PySpark denominator bug;
5. use `/optimize` and `/doc` with review discipline;
6. explain how Genie Code can author an AI/BI Dashboard while publication remains a human decision;
7. apply the same loop to their own work.

Optional outcome:

- update and regression-test the private Genie Agent created in Section 01.

### Timing and instructional arc

- 11:15–11:20 — frame the working loop and explain inherited SQL
- 11:20–11:32 — guided regional FPD5 analysis
- 11:32–11:44 — participant diagnoses and repairs PySpark denominator bug
- 11:44–11:49 — `/optimize` and `/doc`
- 11:49–12:01 — facilitator-only AI/BI Dashboard showcase
- 12:01–12:07 — approvals, permissions, diffs, rerun safety, and recovery
- 12:07–12:12 — optional private-Agent improvement or buffer
- 12:12–12:15 — next-week use case and validation checkpoint

Use ten concise core slides interleaved with live work. The optional Agent slide is used only if all required checkpoints are complete.

## Slide specifications

### Slide 1 — From manual investigation to Genie Code

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

- Section 01 established the governed FPD5 definition and baseline.
- This hour accelerates understanding, generation, repair, documentation, and delivery.
- Governed sources and human validation remain mandatory.

**Recommended visual**

A before-and-after workflow:

`Manual inherited analysis → Genie Code-assisted workflow`

Keep `fpd_metrics` visible as the unchanged governed foundation.

**Presenter notes**

Do not reintroduce Genie Agents. Participants created one in Section 01. This section primarily uses Genie Code in notebooks and dashboard authoring.

**Live transition**

Open the personal clone of the facilitator demo notebook with the Genie Code sidebar visible.

---

### Slide 2 — The working pattern and ownership boundary

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

`Context → outcome → review → execute → validate`

Human ownership remains with:

- source and permission selection;
- semantic correctness;
- approval and publication;
- independent validation.

**Recommended visual**

A five-stage loop with human-gate icons at Review and Validate.

**Presenter notes**

Repeat the boundary throughout the section. Genie Code can propose and execute actions, but the user is accountable for the result.

**Transition**

“The first productivity gain comes from supplying the right context before asking for a change.”

---

### Slide 3 — Attach context before you ask

**Priority:** Essential  
**Strategy:** Hybrid

**Visible content**

- Attach the governed Metric View with `@`.
- Attach query and output with `@cell`.
- Ask for explanation before modification.
- Work in a personal clone.
- Use approval mode that asks before tool actions.

**Recommended visual**

Use a verified Genie Code UI screenshot or a clean mockup showing the `@` resource, `@cell`, and approval boundary.

**Presenter notes**

The productivity message is not “always start from blank.” It is “reduce the time required to understand inherited work without skipping verification.”

Participants should be able to explain the query grain, governed measures, denominator, `GROUP BY ALL`, and percentage conversion before changing anything.

**Live transition**

Run the inherited cohort query and ask Genie Code for an explanation only.

---

### Slide 4 — Use a five-part prompt

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

- Goal
- Context
- Constraints
- Output
- Validation

Workshop constraints:

- use only `fpd_metrics`;
- invoke governed measures with `MEASURE(...)`;
- analyze at region grain;
- keep regions with at least 20 eligible contracts;
- stay read-only and use investigation-signal language;
- show the plan before editing.

**Recommended visual**

Five connected prompt blocks. Put one short FPD5 example under each block.

**Presenter notes**

Do not place the full notebook prompt on the slide. Participants use the detailed prompt in the notebook. The slide teaches a reusable structure.

**Live transition**

Participants submit the regional-extension prompt, review the proposed plan, approve the edits, and run the result.

---

### Slide 5 — Validate generated analysis with invariants

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

- Source is `fpd_metrics`.
- Measures use `MEASURE(...)`.
- No raw-table FPD5 reimplementation.
- No writes.
- Region threshold is applied at region grain.
- Comparison uses the overall promotion rate.
- Interpretation avoids fraud or causality claims.

**Recommended visual**

A compact validation checklist. Add a small “generated layout may vary; invariants may not” callout.

**Presenter notes**

Generated wording, cell layout, and chart styling are nondeterministic. Correctness is determined by governed source, measures, filters, safety constraints, and reference outputs.

After generation, the cohort result should reconcile to approximately 42.26% and 21.03%.

**Live transition**

Run the independent checkpoint query and compare it with the generated regional result.

---

### Slide 6 — Diagnose a semantic bug, not just a syntax error

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

Wrong:

`Filter to fpd5_flag = 1 → aggregate → every cohort appears to be 100%`

Correct:

`Keep full eligible population → count contracts as denominator → sum fpd5_flag as numerator`

Validation checks:

- exactly two cohorts;
- FPD5 contracts cannot exceed eligible contracts;
- rates reconcile within tolerance.

**Recommended visual**

A two-column wrong-versus-right denominator diagram. Do not show the full PySpark function.

**Presenter notes**

This code runs successfully but is semantically wrong. Ask participants to notice the suspicious 100% result before using Genie Code. The repair must not recreate the FPD5 date logic; it should use the already governed `fpd5_flag`.

**Live transition**

Participants attach the function and output, request diagnosis and repair, review the diff, rerun, and execute the assertions.

---

### Slide 7 — `/optimize` and `/doc` require judgment

**Priority:** Essential  
**Strategy:** Hybrid

**Visible content**

- An optimization suggestion is a hypothesis.
- “No change needed” is an acceptable outcome.
- Accept only result-preserving changes with a material rationale.
- Performance claims need Query Profile evidence.
- Documentation should state grain, denominator, and threshold.

**Recommended visual**

A review decision:

`Material rationale + validated same result? → accept; otherwise reject`

**Presenter notes**

Do not reward visible change for its own sake. `/doc` should add a concise explanation, not restate every line of SQL.

**Live transition**

Use `/optimize` and `/doc` on the generated regional analysis.

---

### Slide 8 — Apply the same loop to an AI/BI Dashboard

**Priority:** Essential  
**Strategy:** Hybrid

**Visible content**

Facilitator showcase:

- draft **Genie Code Demo — FPD5 Overview**;
- reuse `fpd_metrics`;
- create three KPIs;
- compare cohorts;
- rank top promotion stores with a minimum denominator;
- add a cohort filter;
- reconcile and leave unpublished.

**Recommended visual**

A dashboard wireframe with three KPI tiles, one cohort chart, one store ranking, and one filter. Add a visible “Facilitator showcase — not participant build” label.

**Presenter notes**

The draft dashboard is distinct from Section 01’s manually prepared **Unicorn FPD5 Overview**. Genie Code automates planning and authoring steps. The facilitator still owns source validation, metric reconciliation, filter behavior, permissions, and the publish decision.

**Live transition**

Open the disposable draft, review the plan, allow Genie Code changes, reconcile values, and leave it unpublished.

---

### Slide 9 — Approve, reject, and recover deliberately

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

Approve:

- reviewed plan;
- understood diff;
- read-only query execution.

Reject:

- raw-table FPD5 logic;
- any write;
- duplicated metric definition;
- broad instruction changes without need.

Recover:

- verify grants and resource visibility;
- use completed fallback assets;
- check source, measures, filters, and rate formatting.

**Recommended visual**

Three columns: Approve, Reject, Recover.

**Presenter notes**

Name the most likely failures without turning the slide into a troubleshooting runbook. The full recovery details stay in the facilitator guide.

**Transition**

If the required notebook and dashboard checkpoints are complete, optionally improve the private Agent. Otherwise, use the remaining time as buffer and proceed to the close.

---

### Slide 10 — What became faster, and what remains yours?

**Priority:** Essential  
**Strategy:** Create new

**Visible comparison**

Faster:

- understand;
- generate;
- repair;
- document;
- review optimization ideas;
- author a dashboard draft.

Still yours:

- define the outcome;
- provide context;
- review changes;
- validate results;
- decide what to publish or share.

**Recommended visual**

A balanced two-column “Faster / Still mine” close.

**Presenter notes**

Ask each participant to name one workflow they will use next week and one validation check they will apply.

---

### Optional slide — Improve the private Genie Agent

**Priority:** Optional  
**Strategy:** Create new

**Visible content**

`Inspect baseline → add smallest necessary context → fresh-chat retest → cohort regression`

Requirements for ranking answers:

- include counts;
- include observation date;
- use investigation language;
- enforce a minimum denominator.

**Recommended visual**

A four-step regression loop.

**Presenter notes**

Participants continue with **Unicorn FPD5 Investigator — `<workspace_username>`** created in Section 01. They do not create, clone, or share another Agent. The Agent continues to use only `fpd_metrics`. Do not duplicate the FPD5 formula in Agent instructions.

Retest both the target store-associate question and the original cohort comparison.

## Keep off the slides

- Full Genie Code prompts
- Full SQL and PySpark code
- Exact generated cell layout
- Full regional result table
- Complete permission grants
- Admin enablement procedures
- Fallback-clone procedures
- Detailed troubleshooting runbook
- AI Gateway, AI Toolkit, Genie One, or Benchmarks as core content

## Collateral-curation search terms

- Genie Code notebook context
- Databricks Assistant or Genie Code `@` and `@cell`
- Genie Code agentic notebook actions and approvals
- Genie Code `/optimize` and `/doc`
- Genie Code for AI/BI Dashboard authoring
- AI-assisted coding review and validation

Most slides should be newly created because the workshop’s context, validation invariants, and denominator-bug lesson are specific. Curate only current product UI screenshots and accurate high-level Genie Code workflow visuals.

## Verify before final slide export

1. Current product name and UI entry point for Genie Agents.
2. Current Genie Code UI for `@`, `@cell`, `/optimize`, `/doc`, and dashboard authoring.
3. Partner-powered AI enablement wording and Genie Code regional availability.
4. Metric View `MEASURE(...)` syntax and supported query behavior.
5. Dashboard-authoring availability and unpublished-draft behavior.
6. Reference FPD5 results from the final seeded workshop dataset.
7. Region threshold of 20 versus store-ranking threshold of 10.

Until rehearsal confirms these details, use conceptual diagrams rather than unverified screenshots and do not hardcode URLs or identity names.

## Final output request

Return:

1. the final slide order;
2. slide title and concise on-slide copy;
3. recommended visual or source collateral;
4. detailed speaker notes;
5. live-demo or participant-activity transition;
6. Essential/Optional label;
7. Create/Curate/Hybrid label;
8. a list of screenshots, diagrams, or existing slides the human author must supply;
9. a final claim-verification checklist.

Do not generate implementation details that belong in notebooks, facilitator guides, or workspace setup. Do not expand the section scope merely to fill slides. If an agenda item is unsupported by the authored workshop assets, identify the gap instead of fabricating content.
