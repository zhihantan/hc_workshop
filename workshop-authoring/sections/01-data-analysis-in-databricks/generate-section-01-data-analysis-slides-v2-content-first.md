# Content-first slide brief — Data Analysis in Databricks

Use this document as the complete content input for an LLM creating presentation support for the 90-minute Data Analysis in Databricks workshop.

This is intentionally **not** a slide outline. Do not preserve the headings below as slide titles or create one slide per topic. Decide the slide count, titles, order, grouping, layouts, and visuals yourself. The presentation should support the live investigation and protect hands-on time.

## Source authority

When resolving conflicts, use this priority:

1. `workshop-content/01-data-analysis-in-databricks/participant-lab.py`
2. `workshop-authoring/sections/01-data-analysis-in-databricks/facilitator-guide.md`
3. `workshop-authoring/sections/01-data-analysis-in-databricks/README.md`
4. `workshop-setup/section-01-facilitator-setup.sql`
5. `participant-materials/unicorn-finance-workshop-scenario.md`
6. `workshop-authoring/agenda/workshop-agenda.md`

Implemented workshop behavior is more authoritative than broad agenda language.

## Audience and role

- The real audience is Home Credit Philippines, with basic SQL and Python familiarity.
- Participants act as Unicorn Finance's internal data team after Atlas Ridge Consulting hands over an inherited Databricks platform.
- They need to understand, validate, operate, and improve inherited assets—not merely run prepared code.
- Unicorn Finance, Atlas Ridge, the records, and all workshop results are fictional or synthetic.

## Business narrative

A brand-funded 0% smartphone point-of-sale promotion increased application and origination volume. FPD5 appears elevated for the promotion cohort and concentrated in some stores or sales associates.

This is an investigation signal, not proof of fraud, misconduct, operational failure, or causality.

The business needs to know:

- whether the promotion cohort shows elevated FPD5 compared with other eligible contracts;
- whether the signal is broad or concentrated;
- which evidence and definitions can be trusted;
- which analytical assets must be operated after the partner handover;
- who owns validation, permissions, monitoring, and recovery.

The conceptual journey is:

```text
Verify inherited sources
→ understand application and promotion context
→ define a fair observable population
→ compare counts and rates at explicit grains
→ investigate concentration
→ persist participant evidence
→ reconcile governed metrics
→ consume the same semantics in dashboard and Genie
→ inspect the resulting SQL workload
→ name ownership and recovery responsibilities
```

This journey is not a required slide sequence.

## Messages that must land

- Start with the business question and denominator, not with SQL or PySpark syntax.
- Application volume provides demand and underwriting context; it is not repayment evidence.
- More volume can produce more problem contracts without changing the underlying rate.
- A rate is interpretable only when grain, numerator, denominator, and observation window are explicit.
- Counts and rates belong together.
- Small denominators can create misleading rankings.
- The promotion pattern identifies where to investigate; it does not establish why the pattern occurred.
- A notebook result is not sufficient for handover. The result must also be durable, governed, reconcilable, observable, and owned.
- One governed definition should serve notebooks, dashboards, and Genie Agents.
- Serverless reduces infrastructure-management effort; it does not remove responsibility for code, permissions, quality, cost, dependencies, validation, monitoring, or recovery.
- A dashboard or Genie answer is not trustworthy merely because it executes.

## Content inventory

### FPD5 and eligibility

- FPD5 means **First Payment Default at five days past due**.
- It applies to the first scheduled installment.
- The observation date is **2026-09-01**.
- A contract is eligible only when:

  `first installment due date + 5 days <= 2026-09-01`

- An eligible first installment is FPD5 when it is unsettled or settled on or after day five.
- Settlement exactly on day five counts as FPD5.
- A recent installment that has not completed the five-day window is not yet observable.
- The denominator is eligible fixed-term contracts—not applications, approvals, all originations, or only defaults.
- The analytical population has one row per eligible contract.

### Inherited lending data

The source check expects eight connected `core_lending` tables:

- `customer`
- `retail_location`
- `loan_product`
- `loan_application`
- `credit_contract`
- `installment`
- `payment`
- `collection_action`

The analysis must distinguish:

- application mix and promotion timing;
- eligible contracts with observable first installments;
- origination-volume concentration;
- FPD5 count and rate concentration.

Application concentration must never be relabeled as FPD5 concentration.

### Cohort and hotspot analysis

- Promotion code: `ZERO_SMARTPHONE_2026`
- Promotion label: `0% smartphone promotion`
- Comparison label: `Other eligible originations`
- Compare eligible-contract counts, FPD5 counts, and FPD5 rates.
- Store and store-associate ranking requires at least **10 eligible contracts**.
- Participants change analytical grain using `region_code`, `store_province`, or `merchant_name`.
- Participants retain evidence, denominator, caveat, and an operational question in their handover note.
- High-rate segments are investigation priorities, not confirmed causes.

For the standard seeded dataset:

- promotion cohort FPD5 rate: approximately **42.26%**;
- other eligible originations: approximately **21.03%**.

These are validation checkpoints. Do not reveal them before participants complete the initial investigation.

The approximately 81% concentration referenced by the source material concerns origination volume at top stores. It is not automatically an FPD5 concentration statistic.

### Compute choices

The workload should determine compute:

- interactive Python and SQL analysis → Serverless notebook compute by default;
- automated notebook, Python, or wheel tasks → Serverless Jobs by default;
- SQL, dashboards, BI, dbt, or Genie workloads → Serverless SQL warehouse by default;
- classic compute → a justified exception when customization or environmental constraints require it.

Keep these concepts distinct:

- **classic operating model** describes customer-configured compute and infrastructure responsibility;
- **Classic SQL warehouse** is a specific SQL warehouse type;
- **Serverless**, **Pro**, and **Classic** are warehouse types only in a SQL-warehouse discussion;
- **Pro** is not a universal compute layer.

Notebook `%sql`, `spark.sql`, and PySpark run on the notebook's attached compute. Dashboard and Genie Agent queries run on the assigned SQL warehouse.

### Delta handover

Participants persist their selected analysis in a participant-specific table under `hc_workshop.workshop_labs`.

Communicate that:

- persistence is justified because another person or process needs the result;
- the participant-derived suffix reduces naming collisions but is not a permission boundary;
- schema evolution should be explicit and reviewed;
- the exercise adds `review_note` after capturing the baseline version;
- row count should remain stable while the schema changes;
- transaction history supports audit and diagnosis;
- time travel depends on retained transaction logs and files;
- time travel is not a backup or complete recovery strategy.

### Governed semantics

Facilitator setup creates:

- `hc_workshop.workshop_shared.fpd_analysis`
- `hc_workshop.workshop_shared.fpd_metrics`

`fpd_metrics` centralizes governed dimensions and measures for:

- eligible contracts;
- FPD5 contracts;
- FPD5 rate;
- display formats, comments, and synonyms.

Consumers invoke governed measures using `MEASURE(...)`.

The participant notebook exposes the calculation so learners can understand it. Downstream dashboards and Genie Agents consume the Metric View instead of recreating the definition.

If `fpd_metrics` is unavailable:

- participants stop;
- they do not create a local substitute;
- they do not rebuild FPD5 inside a dashboard or Agent;
- the facilitator restores and validates the shared asset with the setup SQL before participants continue.

### Prepared AI/BI Dashboard

The facilitator prepares, validates, and publishes **Unicorn FPD5 Overview**.

The dashboard demonstrates:

- governed Metric View consumption;
- eligible-contract, FPD5-contract, and FPD5-rate KPIs;
- monthly context;
- promotion filtering;
- rankings with visible denominators;
- the difference between editable draft and published snapshot;
- an intentional data-permission mode.

The workshop uses **Individual data permissions**, where each viewer's Unity Catalog permissions and policies apply. **Share data permissions** instead use the publisher's data permissions and make the publishing identity a control point.

Participants view, filter, and reconcile the dashboard. They do not build, publish, or repair it during this section.

### Private Genie Agent

Each participant creates:

`Unicorn FPD5 Investigator — <workspace_username>`

Requirements:

- personal user folder;
- workshop SQL warehouse;
- only `hc_workshop.workshop_shared.fpd_metrics` as a source;
- not shared with other participants or broad account groups.

Participants:

- ask the baseline cohort-comparison question;
- inspect generated SQL before trusting the prose;
- confirm use of governed measures;
- reconcile the result to the Metric View;
- confirm the observation date;
- confirm the answer avoids fraud and causal claims;
- retain the baseline response and SQL for Section 02.

### SQL workload evidence

Use SQL generated by the dashboard or a participant's private Genie Agent.

Participants should understand:

- sustained queueing → concurrency or capacity pressure;
- disk spill → an individual query exceeded available memory;
- long result fetching → client or session behavior;
- poor pruning or excessive reads → query or data-layout concern.

Warehouse size mainly affects resources available to an individual query. Maximum clusters mainly affects concurrency. Adding clusters is not the same as making one query larger.

Healthy queries may show no queueing or spill. Do not manufacture a pathological query. Serverless Intelligent Workload Management claims must not be applied to Pro or Classic warehouses without verification.

## Facilitator responsibilities

The facilitator must:

- validate all eight sources and the seeded cohort results;
- rehearse the complete path with a participant-equivalent non-admin identity;
- prepare and reconcile the dashboard;
- verify its publication and Individual data-permission behavior;
- confirm notebook compute, warehouse, grants, and private Agent creation;
- save a healthy Query Profile and optional read-only queue or spill example;
- frame the business question and denominator before introducing products;
- protect the participant grain-change exercise;
- avoid revealing reference rates too early;
- correct causal, denominator, grain, and volume-versus-rate errors;
- demonstrate the prepared dashboard rather than build it live;
- guide participants through private Agent creation and validation;
- distinguish facilitator-wide monitoring evidence from participants' own Query History and Query Profile access;
- use saved evidence when live activity is healthy or permissions are limited;
- close with an owner, operational risk, and recovery or validation action.

## Participant responsibilities

Participants:

- explain FPD5 eligibility before calculating it;
- verify sources and observation date;
- profile application context and promotion timing;
- build and validate the eligible population;
- compare promotion and comparison cohorts using counts and rates;
- distinguish origination volume from repayment behavior;
- change analytical grain and write a non-causal handover note;
- persist and inspect their Delta output;
- reconcile the governed Metric View;
- stop and request support if the Metric View is missing;
- verify the prepared dashboard;
- create and validate a private Genie Agent;
- inspect generated SQL;
- inspect a relevant warehouse statement and Query Profile;
- name an owner, risk, and recovery or validation action.

## What belongs in presentation content

Useful presentation content includes:

- business assignment and handover context;
- FPD5 observation-window and denominator mental model;
- grain, numerator, denominator, count-versus-rate reasoning;
- compute-selection principles;
- Serverless versus classic operating responsibilities;
- governed semantic flow from analysis to Metric View to consumers;
- Delta history and retention concepts;
- dashboard permission and publication models;
- Genie validation discipline;
- queueing-versus-spill reasoning;
- ownership, monitoring, validation, and recovery responsibilities.

Keep these in the live workspace:

- full SQL and Python;
- initial results before the exercise;
- participant-selected breakdowns;
- generated table names and Delta version numbers;
- Metric View YAML;
- dashboard navigation and exact results;
- Genie setup forms, generated SQL, and responses;
- Query History records and Query Profile details;
- troubleshooting and setup actions.

Use verified screenshots only. Prefer conceptual representations when the target workspace UI has not been rehearsed.

## Optional material

Include only if it improves comprehension without reducing hands-on time:

- why Databricks provides an active Spark session;
- deeper examples of justified classic compute;
- additional Metric View metadata;
- deeper Individual-versus-Share data-permission comparison;
- additional transaction-log and retention detail;
- saved queue or spill evidence;
- a short bridge to Section 02.

Optional material must not become required product coverage.

## Claims and misconceptions to avoid

Do not:

- say the promotion caused or created FPD5;
- describe a store, region, merchant, or associate as fraudulent or causally responsible;
- use applications, approvals, or all originations as the denominator;
- treat settlement before day five as FPD5;
- exclude settlement exactly on day five;
- interpret application-volume concentration as FPD5 concentration;
- rank tiny denominators as meaningful hotspots;
- reveal seeded rates before the initial investigation;
- describe time travel as a backup guarantee;
- imply a participant suffix provides access control;
- imply Serverless removes operational ownership;
- conflate classic operating models with Classic SQL warehouses;
- imply notebook SQL ran on a SQL warehouse;
- imply participants build or publish the prepared dashboard;
- imply participants administer or inspect every user's warehouse activity;
- continue with a local fallback when the Metric View is missing;
- recreate FPD5 separately in a dashboard or Agent;
- accept Genie prose without inspecting SQL;
- imply more clusters necessarily accelerate one query;
- fabricate queueing, spill, UI behavior, screenshots, URLs, identities, or environment values.

## Output request for the slide-generating LLM

Using this content inventory, design effective 16:9 presentation support for the 90-minute workshop.

You decide:

- slide count;
- titles;
- sequence and grouping;
- visual language;
- what belongs on-screen versus in presenter notes;
- where the presentation should yield to the live workspace;
- which elements are essential or optional;
- which elements should be created, curated, or hybrid.

Do not mirror notebook headings mechanically or force one slide per topic.

Return:

1. a short explanation of the chosen presentation approach;
2. concise slide content and detailed presenter notes;
3. live-workspace and participant-activity transitions;
4. visual or collateral recommendations;
5. Essential/Optional and Create/Curate/Hybrid labels;
6. a coverage check against the mandatory content above;
7. a list of human-supplied screenshots or workspace evidence;
8. a final fact, claim, terminology, role-boundary, and environment-verification checklist.

Do not generate full implementation code, complete queries, Metric View YAML, fabricated screenshots, or unsupported product claims.
