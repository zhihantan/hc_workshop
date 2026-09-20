# Content-first slide brief — Generative AI in Databricks

Use this document as the complete content input for an LLM creating presentation support for the 60-minute Generative AI in Databricks workshop.

This is intentionally **not** a slide outline. Do not preserve the headings below as slide titles or create one slide per topic. Decide the slide count, titles, order, grouping, layouts, and visuals yourself. Slides should support the hands-on workflow rather than compete with it.

## Source authority

When resolving conflicts, use this priority:

1. `workshop-content/02-generative-ai-in-databricks/02-lab.py`
2. `workshop-authoring/sections/02-generative-ai-in-databricks/facilitator-guide.md`
3. `workshop-authoring/sections/02-generative-ai-in-databricks/expected-results.md`
4. `workshop-authoring/sections/02-generative-ai-in-databricks/facilitator-demo.py`
5. `workshop-authoring/sections/02-generative-ai-in-databricks/README.md`
6. `participant-materials/unicorn-finance-workshop-scenario.md`
7. `workshop-authoring/agenda/workshop-agenda.md`

Implemented workshop behavior is more authoritative than unsupported agenda topics.

## Audience and role

- The real audience is Home Credit Philippines technical users with basic SQL and Python familiarity.
- Participants act as developers supporting Unicorn Finance's risk analytics team.
- Atlas Ridge Consulting has handed over an inherited Databricks platform.
- Section 01 established the FPD5 investigation, governed Metric View, prepared dashboard, and private participant Genie Agent.
- Participants are learning disciplined AI-assisted development, not attending a broad generative-AI product tour.
- All companies, records, findings, and results are fictional or synthetic.

## Business narrative

Unicorn Finance trusts the governed FPD5 baseline from Section 01. Risk now needs to know where the promotion signal is concentrated.

The promotion is Nova Mobile's brand-subsidized financing campaign for selected smartphones. Approved customers repay principal over 6, 9, or 12 months at 0% monthly interest. A processing fee may apply. “0%” refers only to contractual interest; it does not mean a free phone, zero down payment, zero fees, or guaranteed approval.

A developer must:

- use Genie Code to understand inherited work;
- extend the governed analysis to regional grain;
- reconcile the generated result;
- diagnose a PySpark validation helper that executes successfully but returns suspicious 100% rates;
- repair the semantic defect without redefining FPD5;
- leave evidence and documentation another developer can trust.

The facilitator then demonstrates how validated evidence can become an unpublished AI/BI Dashboard draft.

The reusable working pattern is:

```text
Context
→ concrete outcome
→ review
→ execution
→ governed reconciliation
```

The central message is:

> Genie Code makes technical work faster, but governed definitions, permissions, human review, and independent validation make it trustworthy.

## Messages that must land

- AI assistance accelerates understanding, generation, repair, documentation, and asset authoring; it does not transfer accountability.
- Generated code is a draft until source, population, grain, denominator, threshold, result, and safety constraints are checked.
- Code can run successfully and still be semantically wrong.
- Reuse governed measures instead of rebuilding business logic in prompts, SQL, Python, dashboards, or Agent instructions.
- Counts should accompany rates so small denominators remain visible.
- Generated layout, wording, chart style, and cell structure can vary; governed invariants cannot.
- Human responsibilities include selecting context, reviewing plans and diffs, approving actions, validating results, and deciding whether to publish or share.
- “No change needed” is a valid `/optimize` outcome.
- Performance claims require evidence such as Query Profile, not confidence in generated wording.
- Elevated FPD5 remains an investigation signal, not proof of fraud, misconduct, causality, or statistical significance.

## Content inventory

### Governed FPD5 foundation

- FPD5 means **First Payment Default at five days past due**.
- The observation date is **2026-09-01**.
- A contract is eligible only when:

  `first installment due date + 5 days <= 2026-09-01`

- A null settlement date, or settlement on or after day five, counts as FPD5.
- The denominator is eligible contracts—not applications, approvals, all originations, or only defaults.
- Multiplying a governed rate by 100 changes its display, not its definition.

Reference cohort checkpoints:

- 0% smartphone promotion: approximately **42.26%**;
- other eligible originations: approximately **21.03%**.

These synthetic checkpoints can be used because participants completed the initial investigation in Section 01.

### Governed sources

- `hc_workshop.workshop_shared.fpd_metrics` supplies analytical SQL, regional analysis, dashboard data, and the optional Agent.
- Required measures are:
  - `MEASURE(eligible_contracts)`
  - `MEASURE(fpd5_contracts)`
  - `MEASURE(fpd5_rate)`
- `hc_workshop.workshop_shared.fpd_analysis` contains one row per eligible contract and is used by the PySpark validation helper.
- Participants do not recreate the eligibility or settlement-date logic.
- Participant work remains read-only and does not replace workshop data.

### Genie Code working discipline

A reusable request should communicate:

- goal;
- context;
- constraints;
- required output;
- validation.

Participants attach relevant resources and cells, ask for explanation before modification, request a plan before execution, and review proposed changes before approval.

The productivity message is not “start from blank.” It is “understand inherited work faster without skipping verification.”

### Regional investigation

The regional analysis must:

- use only `fpd_metrics`;
- filter to the 0% smartphone promotion;
- group at `region_code` grain;
- retain counts with rates;
- keep regions with at least **20 eligible contracts**;
- compare regions with the overall promotion baseline;
- remain read-only;
- use investigation-signal language.

For the standard seeded dataset, all six regions qualify:

- `REGION_VI`: 443 eligible, 239 FPD5, **53.95%**
- `REGION_XI`: 243 eligible, 116 FPD5, **47.74%**
- `NCR`: 1,832 eligible, 808 FPD5, **44.10%**
- `REGION_III`: 473 eligible, 194 FPD5, **41.01%**
- `REGION_IV_A`: 1,507 eligible, 595 FPD5, **39.48%**
- `REGION_VII`: 429 eligible, 130 FPD5, **30.30%**

`REGION_VI` is the highest qualifying signal, approximately **11.69 percentage points** above the **42.26%** promotion baseline.

Do not reveal these regional answers before participants generate their result. Use them during governed reconciliation.

### Distinct minimum-denominator rules

Do not merge these thresholds:

- regional participant analysis → at least **20 eligible contracts**;
- facilitator dashboard store ranking → at least **10 eligible contracts**;
- optional Agent store or store-associate ranking → at least **10 eligible contracts**.

These are workshop stability and ranking rules. They do not change FPD5 and do not establish statistical significance.

### Semantic denominator defect

Preserve discovery:

- participants first run the inherited helper;
- both cohorts incorrectly show 100%;
- participants assess whether that result is plausible;
- only then should Genie Code be asked to diagnose it.

Do not reveal the cause or repair in presentation content before the activity.

After participant diagnosis, communicate that:

- filtering to `fpd5_flag = 1` before aggregation removes non-FPD5 eligible contracts from the denominator;
- the repair retains the full eligible population;
- eligible contracts form the denominator;
- the existing `fpd5_flag` supplies the numerator;
- the code stays read-only and DataFrame-based;
- the repair does not recreate FPD5 date logic.

Executable checks must verify:

- exactly two cohort rows;
- positive eligible counts;
- FPD5 counts never exceed eligible counts;
- repaired rates agree with a live read-only `fpd_metrics` query within **0.05 percentage points**.

### Optimization and documentation

- An optimization suggestion is a hypothesis.
- “No change needed” is acceptable.
- Accept only changes with a material rationale and preserved results.
- A performance claim requires Query Profile evidence.
- `/doc` should capture grain, denominator, threshold, assumptions, and validation concisely.
- Documentation should help the next owner rather than restate every line of code.

### Facilitator dashboard showcase

The facilitator uses Genie Code to author a disposable draft named **Genie Code Demo — FPD5 Overview**.

It is separate from Section 01's prepared **Unicorn FPD5 Overview**.

The draft must:

- use only `fpd_metrics`;
- include eligible-contract, FPD5-contract, and FPD5-rate KPIs;
- compare promotion cohorts;
- rank five promotion stores using at least 10 eligible contracts;
- retain counts beside rates;
- include a promotion-cohort filter;
- apply the filter to the cohort comparison and store ranking but not the all-cohort KPI counters;
- use correct percentage formatting;
- reconcile with the notebook;
- remain unpublished.

Participants observe and record:

1. whether only `fpd_metrics` is used;
2. whether cohort values reconcile;
3. whether counts and the 10-contract rule remain visible;
4. whether the filter affects the cohort comparison and store ranking but leaves the all-cohort KPI counters unchanged;
5. which checks and publication decisions still belong to the dashboard author.

The facilitator owns source validation, reconciliation, filter behavior, permissions, formatting, publication, and deletion after the session.

### Compute and ownership boundaries

- Notebook SQL and PySpark run on Serverless notebook compute.
- Dashboard datasets and Genie Agent questions run on a Pro or Serverless SQL warehouse.
- Notebook `%sql` should not be described as SQL warehouse activity.
- Genie Code may author a draft, but the user remains responsible for validation and publication.
- Participants work only in personal clones of `02-lab.py`.
- `facilitator-demo.py`, expected results, fallback assets, and detailed recovery instructions remain facilitator-only.

## Facilitator responsibilities

The facilitator must:

- import or distribute only `02-lab.py`;
- keep the facilitator notebook and answers private;
- ensure participants clone the participant lab into personal folders before editing;
- refresh FPD5 eligibility, denominator, observation date, and investigation caveat;
- confirm participants understand the inherited query before modification;
- review the regional plan for source, measures, promotion filter, grain, 20-contract rule, read-only behavior, and non-causal language;
- stop interpretation if generated regional results do not reconcile;
- let participants observe the suspicious 100% output before naming the bug;
- require a focused repair and live Metric View comparison;
- treat optimization suggestions as hypotheses;
- build and reconcile the disposable dashboard while participants complete the observation checklist;
- leave the dashboard unpublished;
- protect governed reconciliation and reflection if time slips;
- use completed fallback assets for review rather than duplicating governed logic.

## Participant responsibilities

Participants:

- clone `02-lab.py` into a personal user folder;
- attach Serverless notebook compute;
- use a Genie Code approval mode that asks before tool actions;
- attach `fpd_metrics`, inherited query, and output as context;
- ask for explanation before modification;
- verify grain, governed measures, denominator, grouping, and percentage conversion;
- use a structured request to extend the analysis to regions;
- review the proposed plan before permitting edits or execution;
- reconcile all six qualifying regional rows;
- interpret the top signal with counts and caveats;
- run the inherited helper and question the 100% output;
- request diagnosis and a focused diff;
- approve only a repair that preserves the full eligible population and governed definition;
- run assertions and live Metric View reconciliation;
- review `/optimize` and `/doc` output critically;
- complete the facilitator-dashboard observation checklist;
- record an owner, risk, recovery action, and next-week use with retained validation.

## Optional private Genie Agent extension

Use this only when:

- all required notebook and dashboard checkpoints are complete;
- time remains before the closing reflection;
- the participant owns the private Section 01 Agent;
- the Agent is editable and unshared;
- `fpd_metrics` remains its only source.

Participants do not create, clone, or share another Agent.

They apply the smallest necessary context change and test:

- the target store-associate question in a fresh conversation;
- the original cohort comparison as a regression check.

If the owner cannot edit the Agent, omit the extension. Do not provide a shared fallback Agent.

## What belongs in presentation content

Useful presentation content includes:

- business handover and participant role;
- the context-to-reconciliation working pattern;
- human ownership and approval boundaries;
- governed-definition and denominator principles;
- structured prompting as a reusable mental model;
- generated drafts versus governed evidence;
- semantic correctness versus successful execution;
- review criteria for optimization and documentation;
- notebook-compute versus SQL-warehouse distinction;
- dashboard-author responsibilities;
- ownership, risk, validation, and recovery.

Keep these in the live workspace:

- notebook cloning and UI navigation;
- full Genie Code requests;
- full SQL and PySpark;
- generated plans, diffs, and cell layouts;
- query and assertion execution;
- the full regional result;
- dashboard authoring interactions;
- filter testing and reconciliation evidence;
- optional Agent editing and fresh-conversation regression.

Keep these facilitator-only:

- `facilitator-demo.py`;
- expected-results material;
- completed fallback notebook and dashboard;
- detailed recovery instructions;
- setup and cleanup procedures.

## Scope exclusions

The implemented core section does not support:

- AI Gateway;
- AI Toolkit;
- Genie One;
- Benchmarks;
- a second introductory Genie demonstration.

Do not add them to the core presentation merely because they appear in the high-level agenda. If a stakeholder insists, place them in clearly labeled parking-lot material and state that no workshop exercise supports them.

## Claims and misconceptions to avoid

Do not:

- describe “0%” as a free phone, zero total cost, zero down payment, zero fees, or guaranteed approval;
- claim elevated FPD5 proves fraud, misconduct, causality, or statistical significance;
- imply `REGION_VI` caused the result;
- confuse the 20-contract and 10-contract rules;
- treat either threshold as part of FPD5;
- use applications, approvals, all originations, or only defaults as the denominator;
- expose the denominator repair before participants diagnose the 100% result;
- imply Genie Code output is correct because it executes;
- promise deterministic generated layouts or wording;
- claim optimization guarantees better performance;
- imply the dashboard is automatically validated or safe to publish;
- imply notebook compute powers dashboards or Genie Agents;
- give participants the facilitator notebook;
- tell participants to create another Agent in Section 02;
- share an Agent with the workshop group or all account users;
- rebuild FPD5 from raw tables;
- fabricate UI behavior, product availability, regional availability, screenshots, identities, or environment values.

## Output request for the slide-generating LLM

Using this content inventory, design effective 16:9 presentation support for the 60-minute workshop.

You decide:

- slide count;
- titles;
- sequence and grouping;
- visual language;
- what belongs on-screen versus in presenter notes;
- where the presentation should yield to the live workspace;
- which elements are essential or optional;
- which elements should be created, curated, or hybrid.

Preserve two sequencing requirements:

1. do not disclose the denominator defect or repair before participant diagnosis;
2. if used, the optional Agent activity happens after required checkpoints and before the closing reflection.

Return:

1. a short explanation of the chosen presentation approach;
2. concise slide content and detailed presenter notes;
3. live-workspace and participant-activity transitions;
4. visual or collateral recommendations;
5. Essential/Optional and Create/Curate/Hybrid labels;
6. a coverage check against the mandatory content above;
7. a list of human-supplied screenshots or workspace evidence;
8. a product, numerical-claim, role-boundary, and environment-verification checklist;
9. a list of intentionally excluded agenda topics.

Do not force one inventory section into one slide, expose exercise answers prematurely, generate full code, fabricate screenshots, or expand scope merely to fill presentation time.
