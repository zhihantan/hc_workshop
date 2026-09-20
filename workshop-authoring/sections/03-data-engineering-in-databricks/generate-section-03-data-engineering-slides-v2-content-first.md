# Content-first slide brief — Data Engineering in Databricks

Use this document as the complete content input for an LLM creating presentation support for the 2-hour Data Engineering in Databricks workshop.

This is intentionally **not** a slide outline. Do not preserve the headings below as slide titles or create one slide per topic. Decide the slide count, titles, order, grouping, layouts, and visuals yourself. The presentation should carry the decision frameworks and protect hands-on time.

## Source authority

When resolving conflicts, use this priority:

1. `workshop-content/03-data-engineering-in-databricks/participant-pipeline.sql`
2. `workshop-content/03-data-engineering-in-databricks/facilitator-guide.md`
3. `workshop-content/03-data-engineering-in-databricks/README.md`
4. `workshop-content/03-data-engineering-in-databricks/facilitator-setup.sql`
5. `workshop-content/03-data-engineering-in-databricks/{job-definition.json, job-quality-gate.py, expected-results.md, designer-demo.md, slide-outline.md}`
6. `participant-materials/unicorn-finance-workshop-scenario.md`
7. `workshop-authoring/agenda/workshop-agenda.md`

Implemented workshop behavior is more authoritative than broad agenda language.

## Audience and role

- The real audience is Home Credit Philippines, with basic SQL and Python familiarity.
- Participants act as Unicorn Finance's internal data team after Atlas Ridge Consulting hands over an inherited Databricks platform.
- Here they **operationalize** the inherited FPD5 analysis into a governed, monitored, scheduled pipeline — not merely run prepared code.
- Unicorn Finance, Atlas Ridge, the records, and all workshop results are fictional or synthetic.

## Business narrative

Sections 01 (analysis) and 06 (modelling) established that the 0% smartphone promotion cohort shows elevated FPD5. Both assumed the underlying FPD5 data was fresh, correct, and monitored — but the inherited pipeline is ad hoc. This section makes the FPD5 layer a **governed, quality-gated, scheduled** data foundation the business can depend on every day.

This is an operational maturity story, not a new analytical finding.

The conceptual journey is:

```text
landing (raw feeds)
→ bronze ingest (as-is)
→ silver validate & conform (Expectations)
→ gold business layer (consumers trust this)
→ orchestrate with a Job (schedule, quality gate, alert)
→ observe (event log, run summary, lineage)
→ hand over ownership
```

This journey is not a required slide sequence. Four handover questions frame it: what are the layers and the source of truth; where is quality enforced and what happens on violation; how is it scheduled, gated, and alerted; who owns refreshes, thresholds, and consumers.

## Messages that must land

- Consumers read **gold**, never bronze.
- **Streaming Table vs Materialized View** is a choice driven by how data arrives — incremental append vs full recompute — not a default winner.
- The **Expectation tier** (`WARN` / `DROP ROW` / `FAIL UPDATE`) is chosen from the **business consequence**, not by habit.
- **Settlement timing is never an Expectation.** Early / on-time / late / unsettled is the FPD5 *outcome being measured*, not a data defect; gating it silently deletes good data.
- The **pipeline** defines *what* the data is; the **Job** defines *when*, *in what order*, and *what happens on failure*.
- The Job's quality gate is a **soft safety net** beneath the **hard** `FAIL UPDATE` expectation.
- Nobody watches a green pipeline; the **failure alert is the tripwire**.
- **Serverless** reduces infrastructure-management effort; it does not remove responsibility for code, permissions, quality, cost, dependencies, validation, monitoring, or recovery.
- A pipeline that merely runs is not a handover — it must also be governed, observable, and owned.

## Content inventory

### The FPD5 gold layer (shared with Sections 01 and 06)

- FPD5 means **First Payment Default at five days past due**, on the first scheduled installment.
- Observation date **2026-09-01**; a contract is eligible when `first installment due date + 5 days <= 2026-09-01`.
- `fpd5_flag` is 1 when the eligible first installment is unsettled or settled on or after day five (settlement exactly on day five counts as FPD5).
- Gold **`fpd_origination`**: one row per eligible fixed-term contract = **25,440**.
  - 0% smartphone promotion cohort: **4,927** contracts, ~**42.26%** FPD5.
  - Other eligible originations: **20,513** contracts, ~**21.03%** FPD5.
  - Overall: ~**25.14%**.
- Gold **`fpd_daily_metrics`**: FPD5 rate by origination month × cohort.
- These figures match Sections 01 and 06. They are validation checkpoints — do not reveal them before participants build and run the pipeline.

### Medallion architecture and table types

- **Bronze** = faithful raw ingest (Streaming Tables), no logic, from `hc_workshop.workshop_shared.lending_raw_{installment, credit_contract, loan_application}`.
- **Silver** = validated & conformed (Streaming Tables; Expectations live here).
- **Gold** = the business layer (Materialized Views): `fpd_origination` + `fpd_daily_metrics`, joining silver to `hc_workshop.core_lending` dimensions (`loan_product`, `customer`, `retail_location`).
- **Streaming Table** = incremental append (bronze ingest, silver cleaning). **Materialized View** = full recompute of a query (gold aggregates and joins). Choose incremental for feeds, recompute for derived tables.
- Each participant's pipeline writes its own `de_<user_id>` schema. The workshop catalog is `hc_workshop`.

### Expectations — the three tiers

- **`FAIL UPDATE`** (corruption must never propagate): `valid_contract` (contract_id not null), `valid_application` (application_id not null).
- **`DROP ROW`** (quarantine impossible values): `valid_due_date` (due date not null), `nonneg_due` (amount ≥ 0), `positive_income` (declared income > 0), `nonneg_principal` (null-tolerant).
- **`WARN`** (suspicious but usable, row kept): `sane_lti` (requested / income < 20), `positive_tenor` (null-tolerant — a non-positive tenor is suspicious; a null tenor on revolving lines is expected and passes).
- On the clean batch: **0 rows dropped or failed**. The `sane_lti` WARN flags ~**17** rare high loan-to-income applications, which are kept — WARN counts on clean data are expected and correct.
- Settlement timing is deliberately **not** gated.

### The data-quality demo

- **WARN/DROP batch** (`batch_date = 2026-09-02`): ~40 negative-amount / null-due installments and ~40 zero-income / extreme-loan-to-income applications. The pipeline **completes**; bad rows are quarantined at silver; bronze grows, silver is unchanged, gold stays **25,440**.
- **FAIL batch** (`batch_date = 2026-09-03`, null `contract_id`): the pipeline update **fails** on `valid_contract` (`FAIL UPDATE`) — a broken key halts the line.
- **Reset requires a full refresh, not an incremental one.** The FAIL batch's rows are already committed to the bronze streaming table and remain pending for silver, so an incremental update re-reads and re-fails; only a full refresh (truncate + reprocess the clean landing) clears them. Gold returns to 25,440.

### Orchestration — the Job

- DAG: `run_pipeline` (pipeline task) → `quality_gate` (notebook task, depends on `run_pipeline`).
- `quality_gate` compares bronze vs silver installment counts; if the drop rate exceeds the threshold (default 5%) it raises and fails the task (firing the failure alert); otherwise it appends a `fpd_run_summary` row (eligible contracts, FPD5 rate, drop %).
- Parameter `as_of_date`; a daily schedule left **PAUSED** for the workshop; an on-failure email.
- On clean data both tasks succeed; `fpd_run_summary` shows eligible **25,440**, drop **0%**.

### Observability

- **Event log**: per-Expectation pass / drop / warn counts.
- **Run monitoring**: Job run timeline, task durations, retries; pipeline update history.
- **Lineage**: Catalog Explorer shows raw → bronze → silver → gold → consumers automatically.
- **Run summary**: durable, queryable `fpd_run_summary` rows.
- The **failure alert** is the operational tripwire.

### Optional — Lakeflow Designer (no-code)

- The **analyst counterpart**: a visual, no-code, AI-native canvas (with the **Genie Code** natural-language assistant) that builds a governed data prep on the **same** Unity Catalog data.
- Data-quality concepts carry over: the **Guardrails** operator (warn-and-continue / warn-and-block / fail workflow) and the **Filter** Included/Excluded split map to `WARN` / `DROP ROW` / `FAIL UPDATE`.
- Availability may require a preview — confirm before demoing. See `designer-demo.md`.

### Compute and scope

- Serverless pipeline and serverless Job by default. **Lakeflow Connect** (managed ingestion) is an optional mention; **Designer** is an optional no-code demo. This section builds the batch/declarative path.

## Facilitator responsibilities

The facilitator must:

- run `facilitator-setup.sql` to land the clean batch before the session, and **not** run the dirty-batch cells yet;
- create the pipeline once end-to-end to warm the path and confirm gold = 25,440 and the cohort rates;
- rehearse both the dirty-batch demo and the full-refresh reset;
- fill the README `TBD` values (serverless entitlements, participant / facilitator groups, alert email) and confirm grants;
- in the demo, land the WARN/DROP batch first (pipeline completes), then the FAIL batch (pipeline halts), read the event-log quality metrics, then reset with a **full refresh**;
- build the Job, run it green, show `fpd_run_summary`, and frame the failure alert as the tripwire;
- never modify `core_lending`; use fully-qualified names;
- close with an owner, a schedule / SLA, and an on-FAIL response.

## Participant responsibilities

Participants:

- explain the medallion and choose Streaming Table vs Materialized View per layer;
- build and run the pipeline, confirm gold = 25,440, and reconcile the cohort rates with Section 01;
- choose an Expectation tier from the business consequence and never gate settlement timing;
- diagnose the seeded FAIL and give the two-step full-refresh recovery;
- build or extend the Job DAG and state task-dependency semantics;
- read the event log, run summary, and lineage; name one owner, one schedule, and one on-FAIL response.

## What belongs in presentation content

Useful presentation content includes:

- the medallion mental model and why consumers read gold;
- Streaming Table vs Materialized View reasoning;
- the three Expectation tiers chosen by business consequence, and the settlement-timing rule;
- pipeline vs Job (transformation vs orchestration);
- observability (event log, run summary, lineage, alert as tripwire);
- the operational handover (owner, schedule, on-FAIL).

Keep these in the live workspace:

- the full pipeline SQL and Expectation clauses;
- exact layer row counts and the 25,440 gold figure before the exercise;
- the Job JSON and the quality-gate notebook;
- event-log navigation and the lineage graph;
- the dirty-batch mechanics and the reset.

Use verified screenshots only. Prefer conceptual representations when the target workspace UI has not been rehearsed.

## Optional material

Include only if it improves comprehension without reducing hands-on time:

- the Lakeflow Designer no-code demo;
- a short bridge from Sections 01 and 06 into this section;
- deeper event-log or lineage detail.

Optional material must not become required product coverage.

## Claims and misconceptions to avoid

Do not:

- gate settlement timing with an Expectation (it is the FPD5 outcome, not a defect);
- say the promotion caused or created FPD5, or describe a store, region, merchant, or associate as fraudulent or causally responsible;
- weaken a `FAIL UPDATE` expectation to force a pass;
- claim an incremental refresh resets the pipeline after a FAIL batch (it re-fails; only a full refresh clears the bronze stream);
- claim "0 violations on clean data" (0 DROP/FAIL, but the WARN tier flags ~17 rows);
- imply consumers read bronze;
- imply Serverless removes operational ownership;
- present the 25,440 figure or the cohort rates before participants build the pipeline;
- fabricate event-log counts, screenshots, URLs, identities, or environment values.

## Output request for the slide-generating LLM

Using this content inventory, design effective 16:9 presentation support for the 2-hour workshop.

You decide:

- slide count;
- titles;
- sequence and grouping;
- visual language;
- what belongs on-screen versus in presenter notes;
- where the presentation should yield to the live workspace;
- which elements are essential or optional;
- which elements should be created, curated, or hybrid.

Do not mirror notebook or SQL headings mechanically or force one slide per topic.

Return:

1. a short explanation of the chosen presentation approach;
2. concise slide content and detailed presenter notes;
3. live-workspace and participant-activity transitions;
4. visual or collateral recommendations;
5. Essential/Optional and Create/Curate/Hybrid labels;
6. a coverage check against the mandatory content above;
7. a list of human-supplied screenshots or workspace evidence;
8. a final fact, claim, terminology, role-boundary, and environment-verification checklist.

Do not generate full implementation code, complete pipeline SQL, the Job JSON, fabricated screenshots, or unsupported product claims.
