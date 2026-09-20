# Consolidated master slide package — Unicorn Finance Workshop (all sections + hands-on labs)

Master input for **Claude Design**. Based on `all-sections-slide-generation-prompts-v3.md`, extended two ways:

1. **Adds Sections 03 (Data Engineering) and 06 (Machine Learning with MLflow)** — the original package had only 01, 02, 05.
2. **Adds the step-by-step hands-on lab for every section** — so Claude Design generates, per section, **both** the content/concept slides **and** hands-on lab-walkthrough slides.

## How to use with Claude Design

Generate, in workshop order:

1. The **workshop opening** slides.
2. For each section **01 → 02 → 03 → 05 → 06**, two blocks:
   - **A. Content slides** — from the section's slide prompt (concepts, decision frameworks, the visible slide windows).
   - **B. Hands-on lab slides** — terse "do this now" walkthrough slides from the section's step-by-step. Mark facilitator demos vs participant hands-on.
3. The **workshop close** slides.

Global rules: clean 16:9, one idea per slide, decision frameworks as tables, business-led and technically accurate. **Keep off the slides** (reveal live): full SQL/Python, the Job JSON, exact seeded figures/metrics *before* the matching exercise, and UI navigation — each section lists specifics. Never fabricate screenshots or workspace evidence. All records are synthetic; an elevated rate is an **investigation signal**, never proof of fraud, misconduct, or causality. Sections **04 and 07 are not built** — do not generate slides for them.

## Shared context (every section)

- **Scenario:** Unicorn Finance's internal data team takes ownership of a Databricks platform built by Atlas Ridge Consulting. Nova Mobile's `ZERO_SMARTPHONE_2026` 0%-interest smartphone-financing promotion (customers repay principal over 6/9/12 months at 0% interest; processing fee/down payment may apply) raised volume; FPD5 appears concentrated in some stores/associates.
- **FPD5 (identical in every section):** only a contract's **first** installment, and only where `due_date + 5 days` ≤ the as-of date **`2026-09-01`**. Null settlement, or settlement on/after day five, counts as FPD5. Denominator = **eligible contracts**.
- **Validated figures** (facilitator context — reveal only *after* the matching exercise): eligible **25,440**; overall **25.14%**; **promotion 42.26%** (4,927) vs **other 21.03%** (20,513); worst promotion region **`REGION_VI` ≈ 53.95%** (~11.69 pts over baseline); interpretable model **≈0.63 ROC-AUC**.
- **Unity Catalog:** `hc_workshop` → `core_lending` (protected synthetic source, 8 tables) · `workshop_shared` (governed views/metrics) · `workshop_labs` (participant outputs).

---

# Workshop opening — introductory slides
**Duration:** 5–7 min · **Slides:** 3 · use at the 9:00 AM start.

## Opening Slide 1 — Today's workshop journey
**Visible content:** "Databricks Enablement — 22 September 2026" with the agenda (9:00 Intro · 9:45 Data Analysis · 11:15 Generative AI · 12:15 Lunch · 1:20 Data Engineering · 3:20 Governance · 4:00 Machine Learning). **One continuous outcome:** understand, validate, operate, govern, and improve an inherited Databricks platform.
**Visual:** horizontal timeline of six topics; separate morning investigation / afternoon operationalization / final model lifecycle, kept as one journey.
**Notes:** one connected workshop, not unrelated demos; each topic produces or validates something Unicorn Finance must operate; the same business event, data, and FPD5 definition connect the sessions.

## Opening Slide 2 — The platform was delivered. Ownership starts today.
**Visible content:** "Today, you are the internal data team at Unicorn Finance Philippines." Atlas Ridge handed over data, notebooks, dashboards, metrics, pipelines, models, and AI assets. Nova Mobile's campaign raised volume while FPD5 appears concentrated in a few stores/associates. *"What happened, which evidence can we trust, and what must Unicorn Finance operate after the handover?"* The pattern is an investigation signal — not proof of fraud, misconduct, or causality.
**Visual:** Atlas Ridge → handover → (assets) → ownership → Unicorn Finance internal team, with the campaign question as focal point.
**Notes:** all entities/records synthetic; "0%" = 0% monthly interest (principal still repaid); FPD5 = first installment reached five days past due before full settlement; the workshop is about ownership.

## Opening Slide 3 — The data we will explore
**Visible content:** the `hc_workshop` structure (`core_lending` / `workshop_shared` / `workshop_labs`); the lending lifecycle (`customer → loan_application → credit_contract → installment → payment`, with `collection_action`, `loan_product`, `retail_location`); the eight source tables.
**Visual:** simple lifecycle diagram emphasizing application → contract → first installment → payment (supports FPD5).
**Notes:** synthetic; `core_lending` = protected source; `workshop_shared` = governed definitions; `workshop_labs` = participant outputs; each section reuses the data for a different operational question.

---

# Section 01 — Data Analysis in Databricks
**Duration:** 90 min · **Lab:** `01-lab.py` · **Goal:** determine whether the promotion cohort shows elevated FPD5 and where it concentrates, using governed, reconcilable analysis.

## A. Content slides
- **Business question:** "Does Nova Mobile's 0% campaign show elevated FPD5, and where should the business investigate?" Establish the promotion mechanics, that volume rose, and the investigation-not-proof boundary.
- **FPD5 & eligibility:** first installment only; must reach day five past due by `2026-09-01`; unsettled or settled ≥ day five = FPD5; settled before day five = not; denominator = eligible contracts. Make **count vs rate** visible. (Do not show seeded rates on the opening slides.)
- **Compute by workload:** Python/PySpark/`spark.sql`/`%sql` run on the notebook's **Serverless** compute; `%sql` changes cell language, not the engine; Databricks supplies `spark`; scheduled work → **Jobs** compute; **AI/BI Dashboards + Genie** run on a **SQL warehouse** (visible in Query History).
- *Visuals:* handover with the open question; a first-installment day-five timeline; count-vs-rate; a three-column notebook/Jobs/warehouse map. *Transition:* "Now we test the inherited data in the notebook."

## B. Hands-on lab — step-by-step
1. **(Slides, 12 min)** Business question / FPD5 / eligibility, then the compute model.
2. **(Participant)** Verify the `core_lending` sources; explore application mix, channels, product, stores, campaign timing (busiest ~20% of stores ≈ 81% of applications — demand, not an FPD5 verdict).
3. **(Participant)** Build the eligible FPD5 population; compare promotion vs other eligible originations (ref ≈ 42.26% vs 21.03%).
4. **(Participant exercise)** Change the analytical grouping (store/associate; ≥10 eligible contracts); write the handover note (evidence, denominator, caveat, follow-up).
5. **(Participant)** Persist to a participant-specific Delta table; inspect Delta history (the schema change adding `review_note`).
6. **(Facilitator demo)** The `fpd_metrics` Metric View and the prepared AI/BI Dashboard.
7. **(Guided activity)** Create + validate each participant's **private** Genie Agent on `fpd_metrics`; inspect generated SQL before trusting it.
8. **(Facilitator demo)** SQL Query History and Query Profile.
9. **(Discussion)** Ownership, validation, monitoring, recovery per asset.

*Keep off slides:* source queries, seeded percentages pre-exercise, Delta/time-travel + dashboard + Genie + Query History screens.

---

# Section 02 — Generative AI in Databricks
**Duration:** 60 min · **Lab:** `02-lab.py` · **Goal:** use **Genie Code** to understand, extend, debug, document, and optimize inherited governed work — with the developer owning validation.

## A. Content slides
- **The assignment:** inherit analytical work to understand, extend, repair, check, and document — producing one validated personal notebook (explained query, regional extension, independent reconciliation, repaired PySpark helper, concise handover doc). Present as the assignment, not the answers.
- **What Genie Code contributes:** explain SQL/PySpark, propose a plan, generate focused edits, run approved actions, suggest `/optimize` + `/doc`, help draft a dashboard. Execution ≠ proof of correctness.
- **Human responsibility / working discipline:** *"Genie Code makes technical work faster, but governed definitions, permissions, human review, and independent validation make it trustworthy."* Pattern: `Context → concrete outcome → review → execute → governed reconciliation`. Developer owns: governed source, eligible-contract denominator, plan/diff review, independent validation, rejecting unsupported perf/causal claims, documenting evidence.
- *Visuals:* inherited notebook moving understand → extend → repair → validate → hand over; human-in-the-loop approval cycle; a trust boundary (AI proposals vs governed validation). *Transition:* "First, ask Genie Code to explain the inherited query before changing anything."

## B. Hands-on lab — step-by-step
1. **(Slides, 5 min)** Genie Code's role + the developer's validation responsibility.
2. **(Participant)** Use Genie Code to **explain** the inherited governed SQL (uses `fpd_metrics`; `MEASURE(...)`, `GROUP BY ALL`; ×100 = display units).
3. **(Participant exercise)** Extend to **regional** grain (source stays `fpd_metrics`, promotion filter, group by `region_code`, ≥20 eligible contracts).
4. **(Participant)** Run the independent governed checkpoint — expect **6 regions**; `REGION_VI` ≈ 53.95%.
5. **(Participant exercise)** Diagnose + repair the PySpark **denominator bug** (helper filters `fpd5_flag = 1` before aggregation → both cohorts look 100%; fix keeps the full eligible population); validate two cohorts, FPD5 ≤ eligible, Metric-View agreement within 0.05 pts.
6. **(Participant)** Review `/optimize` (proposal, not proof — accept only if identical result + rationale; Query Profile is the evidence) and `/doc`.
7. **(Facilitator demo)** Build + validate an unpublished AI/BI Dashboard draft on `fpd_metrics`.
8. **(Optional guided)** Improve the participant's private Genie Agent; retest for regression.
9. **(Discussion)** Owner, risk, recovery; where AI accelerated work without weakening trust.

*Keep off slides:* the inherited/buggy/fixed code, regional values pre-checkpoint, `/optimize` + `/doc` output, dashboard construction.

---

# Section 03 — Data Engineering in Databricks  *(added)*
**Duration:** ~120 min (mostly hands-on) · **Pipeline:** `participant-pipeline.sql` · **Job:** `job-quality-gate.py` · **Goal:** turn the one-off FPD5 query into a governed, quality-gated, scheduled pipeline whose gold layer every consumer trusts.

## A. Content slides
- **Medallion:** `landing → BRONZE (as-is) → SILVER (Expectations) → GOLD (consumers trust this)`; consumers read gold, never bronze; gold `fpd_origination` = the Section 01 FPD5 layer.
- **Streaming Table vs Materialized View:** incremental append (bronze/silver) vs full recompute (gold) — choose by how data arrives.
- **Expectations by consequence:** `WARN` (keep — extreme loan-to-income) · `DROP ROW` (quarantine — negative amount, missing due date, zero income) · `FAIL UPDATE` (halt — null `contract_id`). **Settlement timing is never an Expectation** — it is the FPD5 outcome, not a defect.
- **Pipeline vs Job:** pipeline = what the data is (transformation + quality); Job (DAG) = when, in what order, and what happens on failure (schedule, params, quality gate, alerts).
- **Observability:** event log (pass/drop/warn), run monitoring, automatic lineage, a durable `fpd_run_summary`; the **failure alert is the tripwire**.
- **Handover:** owner · source landing · quality thresholds · gold consumers · on-FAIL recovery.
- *Visuals:* four-box medallion; ST-vs-MV table; three-tier Expectation ladder; pipeline-vs-Job split.

## B. Hands-on lab — step-by-step
1. **(Slides)** One-off query → reliable pipeline; medallion; ST vs MV.
2. **(Participant)** Create a **serverless** Lakeflow Declarative Pipeline with the pipeline SQL as source; target catalog + per-participant schema `de_<user_id>`.
3. **(Participant)** Run it (full refresh); watch bronze → silver → gold build.
4. **(Participant)** Query gold `fpd_origination` / `fpd_daily_metrics`; confirm 25,440 eligible + the cohort split match Section 01.
5. **(Participant)** Open the **event log**; read per-Expectation counts. *(Slide: Expectations WARN/DROP/FAIL.)*
6. **(Facilitator demo)** Land the WARN/DROP dirty batch; re-run → pipeline **completes** with rows flagged/dropped.
7. **(Facilitator demo)** Land the null-`contract_id` batch; re-run → `FAIL UPDATE` **halts** the update.
8. **(Participant)** Build the Job `run_pipeline → quality_gate`; parameterize `as_of_date`; set the gate threshold; add `on_failure` alert; leave the schedule paused. *(Slide: Pipeline vs Job.)*
9. **(Participant)** Trigger the Job; both tasks succeed; open `fpd_run_summary`; trace lineage. *(Slide: Observability.)*
10. **(Participant)** Recover — fix the landing, **full refresh** (a `FAIL UPDATE` row persists in the bronze stream; incremental re-fails); handover checkpoint (one owner, one schedule, one on-FAIL response).

*Keep off slides:* full pipeline SQL + Expectation clauses, the 25,440 figure pre-exercise, the Job JSON + gate notebook, event-log/lineage nav, dirty-batch mechanics + reset.

---

# Section 05 — Governance and Access Control
**Duration:** 30 min (facilitator-led) · **Guide:** `05-participant-guide.md` · **Demo:** `facilitator-demo.py` · **Goal:** diagnose and repair a restricted-access incident via the Unity Catalog authorization chain, applying the narrowest fix and verifying with an unchanged rerun.

## A. Content slides
- **Incident + assignment:** a risk analyst can *discover* `hc_workshop.workshop_shared.fpd_analysis` (under Consumer Lending > Origination Risk) but cannot query it. Identify the executing identity and first failed gate; apply the narrowest approved change; rerun unchanged to verify. The ten-row query is an access **smoke test** — it does not recalculate FPD5.
- **Authorization chain:** `notebook CAN RUN → warehouse CAN USE → runtime identity → USE CATALOG → USE SCHEMA → SELECT → authorized result`. Workspace permissions and UC privileges are separate; groups contribute via membership; `BROWSE` aids discovery, grants no rows; passing one gate ≠ passing the next.
- **Evidence to collect:** runtime identity; asset + compute; fully-qualified object + action; exact error + request ID; direct/inherited/group-derived grants; timestamp.
- **What the repair proves / does not prove:** the unchanged rerun proves this request now passes each gate; ten rows do **not** prove the FPD5 definition is correct, that all rows are visible, that no mask/filter/dynamic-view applies, or that a broader grant was needed.
- *Visuals:* discoverable-but-blocked asset; gated path; evidence packet; before/after with only `USE SCHEMA` changing; a "proves / does not prove" two-column debrief.

## B. Hands-on lab — step-by-step  *(primarily facilitator demonstration + guided discussion)*
1. **(Slides)** Incident + assignment + smoke-test boundary; the authorization chain + evidence.
2. **(Facilitator demo)** Reproduce the restricted-user failure; walk the gates; identify the missing **`USE SCHEMA`** on `workshop_shared`.
3. **(Facilitator demo)** As administrator, grant **only** `USE SCHEMA` to the restricted group; **rerun the unchanged SQL** (same user/warehouse/object) → 10 rows verify.
4. **(Slides/discussion)** What the repair proves and does not prove.
5. **(Facilitator demo)** Table + column **lineage** in Catalog Explorer (`fpd_analysis → fpd_metrics → dashboard`) for retest decisions.
6. **(Facilitator demo)** The Consumer Lending **Domain** in Discover (curation ≠ authorization).
7. **(Participant guide/discussion)** Complete the incident handover (runtime identity, failed gate, evidence, narrow repair, unchanged verification, downstream retests, owner, risk, recovery).

*Keep off slides:* live `current_user()`, the intentional error text, the actual `GRANT`, the query output, lineage/Discover screens.

---

# Section 06 — Machine Learning with MLflow in Databricks  *(added)*
**Duration:** mostly hands-on · **Lab:** `participant-lab.py` · **Goal:** train an interpretable FPD5 model, track it with MLflow, register/govern it in Unity Catalog, batch-score the book, and hand it over.

## A. Content slides
- **Legitimate features vs leakage:** allowed = origination-time (customer, application, product, store reference); forbidden = outcome (installments, payments, collections, contract status/settlement). Store/associate *identity* is an investigation signal, kept out of the borrower model.
- **Split by time, not at random:** train older vintages, validate the newest; random split leaks future info and flatters the score.
- **Interpretability + honest ceiling:** logistic regression → coefficient reason codes; expect a modest, calibrated **≈0.63 ROC-AUC**; a 0.9 signals **leakage**; richer models don't materially beat it (signal ceiling is in the synthetic data).
- **MLflow + Unity Catalog:** `MLflow run (params, metrics, artifact) → register → UC model (versions, @champion alias, signature, lineage) → batch score`. Promotion = an alias move; rollback = the same move back.
- **Batch scoring vs real-time serving:** batch (required) = governed Delta scores table on a schedule; real-time (optional) = REST endpoint + inference tables; online Feature Store + Lakehouse Monitoring named as future, not built.
- **Handover:** model owner/leakage boundary/signature/champion/rollback; experiment history; scores-table consumer/cadence; future monitoring.

## B. Hands-on lab — step-by-step
1. **(Setup)** Install `mlflow` + `scikit-learn` on serverless; restart Python; confirm the `core_lending` sources. *(Slide: investigation → operable model.)*
2. **(Participant)** Build the **leakage-safe** feature view (origination-time only; exclude installments/payments/collections/settlement). *(Slide: features vs leakage.)*
3. **(Participant)** **Time-split** — train older vintages, hold out the newest.
4. **(Participant)** Train the interpretable model; **log params/metrics/artifact to MLflow**; review ROC-AUC/PR-AUC, calibration, reason codes. *(Slide: interpretability + ceiling.)*
5. **(Participant)** **Register** in Unity Catalog as `unicorn_<user_id>_fpd` with a signature; set **`@champion`**; confirm lineage to `core_lending`. *(Slide: MLflow + UC.)*
6. **(Participant)** **Batch-score** the eligible population into a governed Delta scores table (25,440 rows). *(Slide: batch vs serving.)*
7. **(Participant)** Reconcile predicted vs actual FPD5 by cohort; inspect flagged count + precision at the threshold.
8. **(Guided UI)** Explore versions/alias/signature/lineage in Catalog Explorer; open the MLflow run history.
9. **(Discussion)** Handover: one owner, one retraining trigger, one rollback step.

*Keep off slides:* full feature/training code, exact metrics/coefficients/precision pre-exercise, MLflow + Catalog Explorer screens, `DESCRIBE HISTORY`.

---

# Workshop close — slide-ready content
**Duration:** 8–10 min · **Core slides:** 7 (+1 optional). Visible content is slide copy; notes are not for the slide.

## Close Slide 1 — At 9:00 AM: inherited assets, unanswered questions
Atlas Ridge had delivered the platform; Nova Mobile's campaign raised volume; FPD5 appeared concentrated by store/associate; the signal was not proof; ownership was moving to Unicorn Finance. **Bottom line:** assets existed; trust and ownership still had to be established. *Visual:* handover line with one unresolved-question marker.

## Close Slide 2 — One question took us through the whole platform
`What happened? → Can we trust the evidence? → Can the logic run repeatedly? → Can the right people use it safely? → Can we use it for future decisions?` mapped to Analysis · AI-assisted development · Data engineering · Governance · Machine learning. *Notes:* the same synthetic lifecycle + FPD5 definition connected the work.

## Close Slide 3 — By 5:00 PM: investigation became operated assets
Trusted evidence (reproducible FPD5 + governed metrics) · Faster delivery (AI-assisted changes with review + checks) · Repeatable operation (orchestration + quality + monitoring) · Safe access (least-privilege + lineage + discovery) · Predictive asset (tracked, registered, governed batch scoring). *Visual:* layered stack with validation/monitoring/ownership as three rails. *Notes:* say "built/tested/observed" only for what was actually done; mark demos as demos.

## Close Slide 4 — The handover changed from possession to control
"Started with" (inherited assets + unknown dependencies; easy-to-misstate denominator; one-time analysis; access as one yes/no; a model idea) vs "Finished with" (one governed FPD5 definition; reviewed changes + executable validation; repeatable workloads + monitoring/recovery; layered least-privilege + lineage; a tracked model + governed scores + ownership decisions). *Notes:* "finished" = method + ownership established, not that everything is production-ready.

## Close Slide 5 — Trust came from controls, not from product names
Every asset needs: (1) a business purpose + owner; (2) a governed source + definition; (3) appropriate compute + permissions; (4) an executable validation check; (5) a monitoring location; (6) a recovery/rollback action. *Notes:* tie each to the day (FPD5 denominator; Genie Code review; Jobs/pipeline quality + recovery; the governance identity/privilege separation; MLflow + UC lineage).

## Close Slide 6 — What Unicorn Finance owns on Monday
Analysis owner (definition, reconciliation, interpretation) · Pipeline operator (schedule, quality, alert, rerun, recovery) · Data steward (grants, discovery, lineage, impact) · Model owner (features, evaluation, promotion, drift, rollback) · Platform team (compute policy, shared services, observability, escalation). **Shared:** changes reviewed, validated, monitored, documented. *Notes:* responsibilities, not job titles.

## Close Slide 7 — Make the handover real
Choose one asset from today and write: (1) business purpose; (2) internal owner; (3) one validation check; (4) where it is monitored; (5) its first recovery action. **Prompt:** "What would prevent your team from operating this asset tomorrow?" *Notes:* 60–90 seconds; a few teams share their biggest operating gap.

## Close Slide 8 (optional) — The platform was delivered. Ownership starts now.
*"We started with inherited assets and an investigation signal. We finish with evidence, controls, operated workloads, and named responsibilities."* Unicorn Finance can now ask not only "Does it run?" but "Can we trust, govern, recover, and improve it?" *Visual:* the Slide-1 handover line with assets fully on the Unicorn side + labels Trust / Operate / Govern / Improve. *Notes:* restate the fiction boundary; end on ownership, not features.

---

## Coverage checklist (confirm in the generated decks)

- Opening (3) + closing (7, +1 optional) present; sections in order 01 → 02 → 03 → 05 → 06, each with **A. content slides** and **B. hands-on lab** slides.
- Every FPD5 definition matches the shared context; as-of date `2026-09-01`.
- Data-quality/Expectations stays in 03; leakage + model in 06; authorization chain in 05.
- Batch scoring shown as required; Model Serving / online features / monitoring named as optional/future, not built.
- No exact seeded figure or code block on a slide before its matching exercise.
- Each section ends on its operational-handover checkpoint; Sections 04 and 07 are not generated.
