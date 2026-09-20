# Slide-generation brief — Section 01: Data Analysis in Databricks

Use this document either as a complete prompt for an LLM that can generate presentation slides or as a curation guide for selecting and adapting existing Databricks slides.

## Instructions for the slide-generating LLM

Create a 16:9 deck for a 90-minute workshop section.

For every slide:

- provide a concise title;
- keep visible text to one message, three to five short bullets, or one simple comparison;
- assume some participants are new to lending and do not use English as their first language;
- use short sentences and one idea per sentence;
- use direct business questions instead of abstract analytical titles;
- explain every necessary technical term in everyday language;
- avoid unexplained words such as `origination`, `cohort`, `grain`, `denominator`, `reconcile`, `governed`, and `operational`;
- recommend a visual, diagram, or verified product screenshot;
- write detailed presenter notes;
- include the live-demo or participant-activity transition when applicable;
- label the slide as `Essential` or `Optional`;
- label the content strategy as `Create new`, `Curate existing collateral`, or `Hybrid`.

Use clean Databricks-style enterprise visuals, restrained orange/red accents, and diagrams over dense prose. Do not use decorative stock photography, full code listings, unsupported claims, or unverified workspace screenshots.

Treat the implemented section assets and timed facilitator guide as more authoritative than the high-level agenda. Concepts and decision frameworks belong on slides. Code, generated results, UI navigation, and operational evidence belong in the live workspace.

## Workshop scenario and analytical facts

- Unicorn Finance Philippines is a fictional consumer lender.
- Atlas Ridge Consulting has handed over an inherited Databricks lakehouse.
- A customer chooses a selected Nova Mobile phone at a participating store.
- The customer applies for a Unicorn Finance point-of-sale installment loan.
- If approved, the customer repays the amount borrowed over 6, 9, or 12 months.
- The customer pays 0% monthly interest because Nova Mobile pays Unicorn Finance a subsidy.
- The phone is not free. A processing fee or down payment may still apply.
- The campaign uses promotion code `ZERO_SMARTPHONE_2026` and analytical label `0% smartphone promotion`.
- Loan applications increased, and some stores and salespeople had more first-payment problems.
- Participants act as the new owners of the inherited analytical assets.
- All workshop data is synthetic.
- A high FPD5 rate is a reason to investigate, not proof of fraud.

Canonical FPD5 definition:

> Include only first installments for which `due_date + 5 days` is on or before the observation date. A null settlement date, or settlement on or after day five, counts as FPD5. The denominator is eligible contracts, not all applications or approvals.

Observation date:

> 2026-09-01

Reference cohort rates:

- 0% smartphone promotion: approximately 42.26%
- Other eligible originations: approximately 21.03%

Do not reveal these exact rates before participants complete the initial investigation.

## Section analysis

### Audience and purpose

The audience has basic SQL and Python familiarity. Some participants may be new to lending and may not use English as their first language. Slides must explain the business story before the technical workflow.

By the end of the section, they should be able to:

1. explain FPD5 and which loans are old enough to check;
2. choose notebook, Jobs, or SQL warehouse compute based on workload;
3. explain the serverless-versus-classic operating model and the role of Serverless, Pro, and Classic SQL warehouses;
4. use PySpark and SQL to answer clear business questions;
5. group the loans in a different way and explain the result;
6. save the result as a participant-specific Delta table and inspect its history;
7. check that the notebook, Metric View, dashboard, and private Genie Agent give the same answer;
8. inspect SQL workload evidence and distinguish queueing from spill.

### Timing and instructional arc

- 9:45–9:50 — assignment, FPD5 definition, eligibility, and caveat
- 9:50–9:57 — compute decision framing
- 9:57–10:15 — check where customers applied and when applications increased
- 10:15–10:27 — find loans old enough to check and compare FPD5 rates
- 10:27–10:39 — participant groups the loans in a different way and writes a summary
- 10:39–10:49 — save the result and view Delta history
- 10:49–10:56 — check that the Metric View and dashboard match
- 10:56–11:06 — private Genie Agent creation and verification
- 11:06–11:11 — Query History and Query Profile
- 11:11–11:15 — investigation checkpoint

Use eight core slides. An optional title slide and optional ownership close may be added only if they do not reduce hands-on time.

## Slide specifications

### Optional title slide — Data Analysis in Databricks

**Priority:** Optional  
**Strategy:** Create new

**Visible content**

- Check first-payment problems at Unicorn Finance
- Understand → compare → save → share → check
- 9:45 AM–11:15 AM

**Recommended visual**

A single left-to-right workflow with five stages. Do not use product-logo wallpaper.

**Presenter notes**

Explain that the section follows one question from the source data to a saved result, dashboard, Genie Agent, and SQL query.

**Transition**

Move immediately to the inherited business question.

---

### Slide 1 — Did promotion loans have more late first payments?

**Priority:** Essential  
**Strategy:** Create new

**Purpose**

Explain the phone loan, the first-payment question, and the safety warning.

**Visible content**

- Customers financed selected phones over 6, 9, or 12 months.
- Customers paid 0% monthly interest but still repaid the amount borrowed.
- FPD5 means the first payment was not fully paid before day five.
- Compare promotion loans with other loans old enough to check.
- A high rate is a reason to investigate, not proof of fraud.

**Recommended visual**

A simple funnel:

`Application → approved phone loan → first payment due → wait five days → FPD5 yes or no`

Add a small “investigate, do not infer fraud” callout.

**Presenter notes**

Explain that a loan cannot be checked until five days after its first payment was due. A payment on day five counts as FPD5. Do not reveal the expected rates yet. Explain that a busy store can have more late payments simply because it handles more loans.

**Transition**

“Before we check the data, let’s choose where the notebook and SQL should run.”

---

### Slide 2 — Choose compute by workload

**Priority:** Essential  
**Strategy:** Hybrid

**Curate from existing collateral**

Look for Databricks slides about compute selection, Serverless notebooks, Jobs compute, and SQL warehouses. Replace generic examples with the Unicorn Finance workflow.

**Visible comparison**

- Interactive Python and SQL notebook → Serverless notebook compute
- Automated notebook, Python, or wheel task → Serverless Jobs
- SQL, dashboard, BI, dbt, or Genie workload → Serverless SQL warehouse

Add concise exceptions:

- Classic notebook compute for R, RDDs, JARs, init scripts, or cluster-level customization.
- Classic Jobs compute for unsupported task types or required customization.
- Pro SQL warehouse when Serverless is unavailable or custom networking is required.

**Recommended visual**

A three-row decision matrix: workload, default, justified exception.

**Presenter notes**

All-purpose compute is interactive and is generally not the production Jobs default. Jobs compute belongs to an automated task. A SQL warehouse is SQL-optimized compute and can be Serverless, Pro, or Classic.

Ask:

> A scheduled Python notebook runs hourly on an analyst’s all-purpose compute. What should the new owner challenge?

Expected answer: move it to Serverless Jobs or justified classic Jobs compute, then define ownership and monitoring.

**Transition**

“The second decision is how much of the compute operating model we want to manage.”

---

### Slide 3 — Serverless versus classic is an operating-model choice

**Priority:** Essential  
**Strategy:** Curate existing collateral

**Visible comparison**

- Infrastructure and runtime upgrades: Databricks-managed versus customer-configured
- Startup and scaling: rapid/on demand versus provisioned
- Configuration freedom: intentionally constrained versus greater customization
- Operator responsibility: code, permissions, cost, quality, dependencies, and monitoring in both models

Add one prominent callout:

> Pro is a SQL warehouse type, not a universal compute layer.

**Recommended visual**

A two-column Serverless versus Classic matrix. Keep the SQL warehouse callout visually separate.

**Presenter notes**

Serverless removes infrastructure-management work; it does not remove ownership. Compute policies and Unity Catalog permissions still apply. Compare Serverless, Pro, and Classic only after the workload has been identified as SQL, BI, dashboard, dbt, or Genie.

**Live transition**

Open the participant notebook, show the eight inherited tables, and select the assigned Serverless notebook compute.

---

### Slide 4 — How will we answer the question?

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

`Check tables → see where customers applied → see when applications increased → find loans old enough to check → compare FPD5 counts and percentages`

Key messages:

- First see where customers applied.
- Then see when promotion applications increased.
- Check a loan when its first payment reaches day five after the due date.
- Show the number of FPD5 loans and the percentage together.
- Group the loans in different ways to find places that need a closer look.

**Recommended visual**

A simple vertical flow. Label every step with the question it answers.

**Presenter notes**

Use this slide briefly before the notebook. Do not organize the explanation around Python or SQL features. Pause at each simple question shown in the flow. The participant exercise changes `ANALYSIS_DIMENSION` and asks for a plain-language summary.

Approximately 81% of store applications come from the busiest 20% of stores. This does not mean those stores have the highest FPD5 percentage.

**Live transition**

Run the notebook through the store-and-salesperson comparison. Then give participants 12 uninterrupted minutes to group the loans in a different way.

---

### Slide 5 — Save the result for the next analyst

**Priority:** Essential  
**Strategy:** Hybrid

**Curate from existing collateral**

Use an existing Delta Lake transaction-log or time-travel visual if it is accurate and simple. Add the workshop-specific participant table flow.

**Visible content**

`Grouped result → your Delta table → add review_note → view history → read the earlier version`

Key messages:

- Save a result when another person will need it later.
- Add table fields deliberately.
- Every saved change adds to the table history.
- Old versions depend on retained files. They are not a backup.

**Recommended visual**

A before-and-after schema graphic plus a small transaction-history timeline.

**Presenter notes**

The table contains the participant’s real result. The notebook adds `review_note` for the next analyst. The number of rows should stay the same. Only the extra note field should be added.

The generated participant identifier supports ownership and cleanup. It is not a permission boundary.

**Live transition**

Write the table, alter the schema, update the note, inspect `DESCRIBE HISTORY`, and read an earlier version.

---

### Slide 6 — Does the dashboard show the same answer?

**Priority:** Essential  
**Strategy:** Hybrid

**Curate from existing collateral**

Look for current AI/BI Dashboard slides explaining governed datasets, draft/publish behavior, and data-permission modes. Replace generic assets with `fpd_metrics` and **Unicorn FPD5 Overview**.

**Visible content**

`Shared FPD5 calculation → dashboard draft → published dashboard → viewers`

Compare:

- Individual data permissions: the viewer’s Unity Catalog permissions and policies apply.
- Share data permissions: the publisher’s data permissions apply; the publishing identity becomes a control point.

Check:

- Who owns the FPD5 calculation?
- Which SQL warehouse runs the queries?
- Who can see the dashboard and data?
- Do the numbers match the notebook?

**Recommended visual**

A branching flow from the Metric View through a draft and published dashboard, with the two data-permission modes shown as separate branches.

**Presenter notes**

The workshop uses Individual data permissions because participants can already read the Metric View. Do not build the dashboard live. Open the prepared dashboard, check that its numbers match the notebook, use one filter, and explain that viewers see the published version.

**Live transition**

Open `hc_workshop.workshop_shared.fpd_metrics`, then **Unicorn FPD5 Overview**.

---

### Slide 7 — Ask the same question with Genie

**Priority:** Essential  
**Strategy:** Hybrid

**Visible content**

`Shared FPD5 calculation → Genie question → generated SQL → result → checked answer`

Quality loop:

1. Use only the shared `fpd_metrics` source.
2. Create the Agent in the owner’s private folder.
3. Ask the promotion question.
4. Check the SQL and result.
5. Save the answer for Section 02.

**Recommended visual**

A simple question-to-answer flow. Keep product metadata off the visible slide.

**Presenter notes**

Every participant creates **Unicorn FPD5 Investigator — `<workspace_username>`** in their private folder and attaches only `hc_workshop.workshop_shared.fpd_metrics`. The Agent remains unshared. Participants ask whether promotion loans had a higher FPD5 rate than the other eligible loans.

Do not place a long Agent instruction prompt, generated SQL, or the expected answer on the slide.

**Live transition**

Create the Agent with participants, ask the question, check the generated SQL, and confirm that the answer matches the Metric View.

---

### Slide 8 — What happened when the SQL ran?

**Priority:** Essential  
**Strategy:** Curate existing collateral

**Visible comparison**

- Queued → the warehouse was busy
- Spill → the query needed more memory and used disk
- Fetching → the query finished, but the client was still receiving results
- Long idle time → review the auto-stop setting
- Too much data read → check filters and table layout

Add two short callouts:

- A larger warehouse gives one query more resources.
- More clusters allow more queries to run at the same time.

**Recommended visual**

A simple word → meaning → first check layout.

**Presenter notes**

Use real SQL activity generated by the dashboard or Genie Agent. If the query has no spill or queue, say that this is a good result. Use a saved Query Profile only when you need an example.

Intelligent Workload Management wording applies only to Serverless SQL warehouses. Do not claim the same behavior when using a Pro fallback.

**Live transition**

Open warehouse Monitoring, locate a section-generated statement in Query History, and open Query Profile.

---

### Optional close — Who owns the inherited asset now?

**Priority:** Optional  
**Strategy:** Create new

**Visible content**

For one item, state:

- who owns it;
- one thing that could go wrong;
- how to check or fix it.

Assets: notebook, Delta table, Metric View, dashboard, Genie Agent, SQL warehouse.

**Recommended visual**

Six simple asset tiles around the owner/problem/check question.

**Presenter notes**

Use only if a visible close helps the facilitator. The required checkpoint may also be performed verbally. Bridge to Section 02: participants will use Genie Code to improve the same governed analysis and, optionally, the same private Agent.

## Keep off the slides

- Full SQL and Python cells
- Metric View YAML
- Exact FPD5 rates before the participant exercise
- Dashboard construction steps
- Query Profile click-by-click navigation
- Generated Genie SQL or prose answers
- Permission troubleshooting
- Participant-ID hashing implementation

## Collateral-curation search terms

- Databricks compute selection
- Serverless versus classic compute
- Serverless notebook and Serverless Jobs
- SQL warehouse Serverless Pro Classic
- Delta Lake transaction log, schema evolution, time travel
- AI/BI Dashboard draft publish data permissions
- Metric Views and governed metrics
- Genie Agents with Metric Views
- SQL warehouse monitoring and Query Profile

## Verify before final slide export

1. Current product name and UI entry point for Genie Agents.
2. Metric View YAML 1.1 support in the target SQL warehouse.
3. Individual data permissions versus Share data permissions labels and behavior.
4. Current Serverless, Pro, and Classic SQL warehouse terminology.
5. Intelligent Workload Management wording and its Serverless-only applicability.
6. Reference FPD5 results from the final seeded workshop dataset.
7. Runtime, warehouse, facilitator group, and dashboard values still marked `TBD`.

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

Do not generate implementation details that belong in notebooks, facilitator guides, or workspace setup. Do not expand the section scope merely to fill slides.
