# Slide-generation brief — Section 01: Data Analysis in Databricks

Use this document either as a complete prompt for an LLM that can generate presentation slides or as a curation guide for selecting and adapting existing Databricks slides.

## Instructions for the slide-generating LLM

Create a 16:9 deck for a 90-minute workshop section.

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

## Workshop scenario and analytical facts

- Unicorn Finance Philippines is a fictional consumer lender.
- Atlas Ridge Consulting has handed over an inherited Databricks lakehouse.
- The business launched a brand-funded 0% smartphone point-of-sale promotion.
- Promotion volume increased, and first-payment-default behavior appears concentrated by store and sales associate.
- Participants act as the new owners of the inherited analytical assets.
- All workshop data is synthetic.
- Elevated FPD5 is an investigation signal, not proof of fraud or causality.

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

The audience has basic SQL and Python familiarity. Participants are taking over an inherited analytical workflow rather than attending a generic feature tour.

By the end of the section, they should be able to:

1. explain First Payment Default at five days past due, its observation window, and its eligible-contract denominator;
2. choose notebook, Jobs, or SQL warehouse compute based on workload;
3. explain the serverless-versus-classic operating model and the role of Serverless, Pro, and Classic SQL warehouses;
4. use PySpark and SQL to answer distinct questions in one connected investigation;
5. change the analytical grain of the FPD5 investigation;
6. persist the result as a participant-specific Delta table and inspect its history;
7. trace one governed FPD5 definition through a Metric View, AI/BI dashboard, and private Genie Agent;
8. inspect SQL workload evidence and distinguish queueing from spill.

### Timing and instructional arc

- 9:45–9:50 — assignment, FPD5 definition, eligibility, and caveat
- 9:50–9:57 — compute decision framing
- 9:57–10:15 — source verification, application profile, and promotion timing
- 10:15–10:27 — eligible FPD5 population and concentration analysis
- 10:27–10:39 — participant changes analytical grain and writes a handover note
- 10:39–10:49 — Delta persistence and history
- 10:49–10:56 — Metric View and dashboard reconciliation
- 10:56–11:06 — private Genie Agent creation and verification
- 11:06–11:11 — Query History and Query Profile
- 11:11–11:15 — investigation checkpoint

Use eight core slides. An optional title slide and optional ownership close may be added only if they do not reduce hands-on time.

## Slide specifications

### Optional title slide — Data Analysis in Databricks

**Priority:** Optional  
**Strategy:** Create new

**Visible content**

- Unicorn Finance operational handover
- Compute → notebook → Delta → governed BI and Genie → operations
- 9:45 AM–11:15 AM

**Recommended visual**

A single left-to-right workflow with five stages. Do not use product-logo wallpaper.

**Presenter notes**

Explain that this is one connected workflow, not a tour of unrelated Databricks features. Participants create evidence, persist it, consume the same governed metric through multiple assets, and inspect the workload it generates.

**Transition**

Move immediately to the inherited business question.

---

### Slide 1 — Did the 0% promotion create an FPD5 hotspot?

**Priority:** Essential  
**Strategy:** Create new

**Purpose**

Establish the business question, analytical denominator, and fiction boundary.

**Visible content**

- Atlas Ridge handed over the platform.
- Promotion volume increased.
- FPD5 appears concentrated by store and sales associate.
- FPD5 means First Payment Default at five days past due.
- Count only first installments observed through day five as of 2026-09-01.
- Elevated FPD5 is an investigation signal, not confirmed fraud.

**Recommended visual**

A simple funnel:

`Originations → eligible first installments → FPD5 numerator → cohort/store/associate comparison`

Add a small “investigate, do not infer fraud” callout.

**Presenter notes**

Define FPD5 carefully. Emphasize that the denominator is eligible contracts. Settlement exactly on day five counts as FPD5. Do not reveal the expected cohort rates yet. Separate high origination-volume concentration from FPD5 hotspot analysis.

**Transition**

“Before we query the data, we need to choose compute from the workload.”

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

### Slide 4 — From promotion volume to a fair FPD5 comparison

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

`Unity Catalog tables → PySpark application profile → SQL monthly trend → eligible first installments → one row per eligible contract → cohort and hotspot comparison`

Key messages:

- Profile how applications entered before claiming anything about repayment.
- Test when promotion volume appeared before analyzing its outcomes.
- Exclude contracts that have not completed the five-day observation window.
- Declare grain and denominator before calculating a rate.
- Use counts and rates together when prioritizing segments for review.

**Recommended visual**

A vertical investigation flow in which every transformation is labeled with the business question it answers.

**Presenter notes**

Use this slide briefly while transitioning from source discovery into the notebook. Do not organize the explanation around language features. In the workspace, pause at source inventory, application context, promotion timing, eligibility, cohort comparison, volume concentration, and hotspot prioritization. The participant exercise changes `ANALYSIS_DIMENSION` and requires a written interpretation with evidence, denominator, caveat, and owner question.

Approximately 81% concentration in the source material refers to origination volume at top stores, not automatically to FPD5 concentration.

**Live transition**

Run the notebook through the hotspot analysis, then give participants 12 uninterrupted minutes for the grain-change exercise.

---

### Slide 5 — Make the investigation operable with Delta

**Priority:** Essential  
**Strategy:** Hybrid

**Curate from existing collateral**

Use an existing Delta Lake transaction-log or time-travel visual if it is accurate and simple. Add the workshop-specific participant table flow.

**Visible content**

`Participant breakdown → participant-specific Delta table → add review_note → inspect history → read earlier version`

Key messages:

- Persist a result when another person or process must use or operate it.
- Schema evolution should be explicit and reviewed.
- Every committed change creates table history.
- Time travel depends on retained logs and files; it is not a backup guarantee.

**Recommended visual**

A before-and-after schema graphic plus a small transaction-history timeline.

**Presenter notes**

The table is the participant’s real investigation output, not a disconnected sample. The lab adds `review_note` deliberately. The earlier and later versions must retain the same analytical row count. Version numbers may differ after reruns.

The generated participant identifier supports ownership and cleanup. It is not a permission boundary.

**Live transition**

Write the table, alter the schema, update the note, inspect `DESCRIBE HISTORY`, and read an earlier version.

---

### Slide 6 — A governed dashboard is more than charts

**Priority:** Essential  
**Strategy:** Hybrid

**Curate from existing collateral**

Look for current AI/BI Dashboard slides explaining governed datasets, draft/publish behavior, and data-permission modes. Replace generic assets with `fpd_metrics` and **Unicorn FPD5 Overview**.

**Visible content**

`Metric View → dashboard dataset → draft → publish → viewers`

Compare:

- Individual data permissions: the viewer’s Unity Catalog permissions and policies apply.
- Share data permissions: the publisher’s data permissions apply; the publishing identity becomes a control point.

Operator checklist:

- metric and dataset owner;
- SQL warehouse;
- data-permission mode;
- dashboard ACL and published snapshot;
- reconciliation query.

**Recommended visual**

A branching flow from the Metric View through a draft and published dashboard, with the two data-permission modes shown as separate branches.

**Presenter notes**

The workshop uses Individual data permissions because participants already have `SELECT` on the Metric View. Do not build the dashboard live. Open the prepared draft, reconcile it to the notebook, demonstrate a filter, discuss publishing, and show that the published view is a snapshot separate from the draft.

**Live transition**

Open `hc_workshop.workshop_shared.fpd_metrics`, then **Unicorn FPD5 Overview**.

---

### Slide 7 — Semantics first, then Genie

**Priority:** Essential  
**Strategy:** Hybrid

**Visible content**

`FPD5 source view → Metric View → dashboard and focused Genie Agent → question → generated SQL → result → verified answer`

Quality loop:

1. Start with one focused governed source.
2. Create the Agent in the owner’s private folder.
3. Ask a real business question.
4. Inspect generated SQL and results.
5. Save the baseline for the Section 02 improvement loop.

**Recommended visual**

A semantics pipeline. Under the Metric View, show small labels for fields, measures, comments, synonyms, and formats.

**Presenter notes**

Every participant creates **Unicorn FPD5 Investigator — `<workspace_username>`** in their private folder and attaches only `hc_workshop.workshop_shared.fpd_metrics`. The Agent remains unshared. The baseline question compares the promotion with other eligible originations as of 2026-09-01.

Do not place a long Agent instruction prompt, generated SQL, or the expected answer on the slide.

**Live transition**

Create the Agent with participants, ask the baseline question, inspect the generated SQL, and reconcile the result to the Metric View.

---

### Slide 8 — Inspect what the SQL workload did

**Priority:** Essential  
**Strategy:** Curate existing collateral

**Visible comparison**

- Sustained queueing → concurrency or capacity issue
- Disk spill or `DATA_SPILL` → one query exceeds available memory
- Long result fetching → client or session issue
- Long idle periods → auto-stop does not match usage
- Poor pruning or high reads → query or table-layout issue

Add three short callouts:

- Describe this as workload utilization, not host CPU utilization.
- Warehouse size mainly affects individual-query resources.
- Maximum clusters mainly affects concurrency.

**Recommended visual**

An evidence → likely issue → first action matrix.

**Presenter notes**

Use real SQL activity generated by the Metric View, dashboard, or Genie Agent. If the session has no spill or queue, say so and use a saved read-only Query Profile. Do not create a pathological query on the shared warehouse.

Intelligent Workload Management wording applies only to Serverless SQL warehouses. Do not claim the same behavior when using a Pro fallback.

**Live transition**

Open warehouse Monitoring, locate a section-generated statement in Query History, and open Query Profile.

---

### Optional close — Who owns the inherited asset now?

**Priority:** Optional  
**Strategy:** Create new

**Visible content**

For one asset, state:

- owner;
- operational risk;
- recovery action.

Assets: notebook, Delta table, Metric View, dashboard, Genie Agent, SQL warehouse.

**Recommended visual**

Six simple asset tiles around the owner/risk/recovery question.

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
