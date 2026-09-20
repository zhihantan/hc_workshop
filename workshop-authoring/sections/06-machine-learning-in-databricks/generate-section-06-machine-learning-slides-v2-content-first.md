# Content-first slide brief — Introduction to Machine Learning in Databricks

Use this document as the complete content input for an LLM creating presentation support for the Introduction to Machine Learning in Databricks workshop section.

This is intentionally **not** a slide outline. Do not preserve the headings below as slide titles or create one slide per topic. Decide the slide count, titles, order, grouping, layouts, and visuals yourself. The presentation should carry the decision frameworks and protect hands-on time.

## Source authority

When resolving conflicts, use this priority:

1. `workshop-content/06-machine-learning-in-databricks/participant-lab.py`
2. `workshop-content/06-machine-learning-in-databricks/facilitator-guide.md`
3. `workshop-content/06-machine-learning-in-databricks/README.md`
4. `workshop-content/06-machine-learning-in-databricks/expected-results.md`
5. `workshop-content/06-machine-learning-in-databricks/{genie-code-runbook.md, participant-genie-code-lab.py, slide-outline.md}`
6. `participant-materials/unicorn-finance-workshop-scenario.md`
7. `workshop-authoring/agenda/workshop-agenda.md`

Implemented workshop behavior is more authoritative than broad agenda language.

## Audience and role

- The real audience is Home Credit Philippines, with basic SQL and Python familiarity.
- Participants act as Unicorn Finance's internal data team; here they build a first **governed** machine-learning model on the FPD5 foundation.
- Unicorn Finance, Atlas Ridge, the records, and all workshop results are fictional or synthetic.

## Business narrative

Section 01 found the FPD5 hotspot; the business now asks whether FPD5 can be **predicted at origination** to inform risk decisions *before* a contract is booked. Participants train, register, and batch-score a model that estimates FPD5 probability from origination-time information only, then judge honestly what it can and cannot do.

## Messages that must land

- Use **origination-time features only**. Anything known only *after* origination — payments, settlement dates, collections, the first-installment outcome — is **leakage** and must never be a feature. Leakage is the central discipline of the section.
- The prediction target is the **same FPD5 label** used across the workshop.
- **MLflow** tracks the experiment; **Unity Catalog** governs the registered model (with a champion alias) and the scores table.
- Be **honest about quality**: validation ROC-AUC is ~**0.63**. The model behaves as a **cohort / segment risk detector near a data ceiling** set by the limited origination-time signal — not a high-precision individual predictor. Communicate limits, not hype.
- A model that registers is not a model you trust: **validate** predicted cohort rates against the known figures and inspect precision at the decision threshold.
- **Serverless** does not remove responsibility for leakage, governance, calibration, or monitoring.
- Do **not** use sensitive or prohibited attributes as features.

## Content inventory

### The FPD5 label and training population

- Same definition as Sections 01 and 03: eligible fixed-term contracts where `first installment due date + 5 days <= 2026-09-01`; `fpd5_flag` is 1 when that first installment is unsettled or settled on or after day five.
- The training population is the gold `fpd_origination` layer: **25,440** eligible contracts, overall ~**25.14%** FPD5 (0% smartphone promotion ~**42.26%**, other eligible originations ~**21.03%**).

### Features — origination-time only

- **Allowed:** application and underwriting context, contract terms (principal, tenor, monthly rate), customer attributes (age, declared income, employment type), product type, store region / merchant type, promotion cohort, application channel.
- **Forbidden (leakage):** `settled_date`, any payment or collection fact, anything describing the first-installment outcome, and any other post-origination field.
- **Prohibited as features:** sensitive attributes (for example `sex_code`) — excluded by design.

### Model, tracking, and registry

- A scikit-learn pipeline (for example a `ColumnTransformer` feeding a gradient-boosted or logistic model), with **MLflow autolog**, `infer_signature`, and `cloudpickle`.
- Registered to Unity Catalog as `hc_workshop.workshop_labs.unicorn_<user_id>_fpd` with the **`@champion`** alias (note the alias-visibility gotcha — it resolves via the aliases endpoint, not the model-versions list); batch scores to `unicorn_<user_id>_fpd_scores`; features view `unicorn_<user_id>_fpd_features`.
- The canonical catalog is `hc_workshop`; the reference instance used `sean_development_catalog`.

### Performance and honest framing

- Validation ROC-AUC ~**0.627**, PR-AUC ~**0.412**. Predicted cohort rates track actual (promotion ~41% predicted vs ~42.26% actual; other ~20% vs ~21.03%). At a 0.35 threshold, roughly **5,485** contracts are flagged, precision ~**41.5%**.
- Interpretation: the model **separates cohorts / segments** and reproduces the promotion signal; the modest AUC is a **data ceiling** from origination-time-only features, not a defect. It supports triage and prioritization, not individual certainty.

### Genie Code companion

- `participant-genie-code-lab` + `genie-code-runbook`: build the same model through the **Genie Code** natural-language assistant — catalog `hc_workshop`, `workshop_labs` schema, the same leakage-safe features, and **no** sensitive attributes.

## Facilitator responsibilities

The facilitator must:

- confirm the FPD5 gold population and the `workshop_labs` schema exist, with `CREATE MODEL` permission;
- rehearse train → register → batch-score headless and confirm the reference model, scores, and validation numbers;
- frame **leakage** before features and correct any post-origination feature;
- set expectations about the ~0.63 AUC (cohort detector, data ceiling) and **not oversell**;
- show the Unity Catalog registry, the champion alias, and the scores table, and reconcile predicted vs actual cohort rates;
- never modify `core_lending`; use fully-qualified names.

## Participant responsibilities

Participants:

- state the label and the leakage boundary before building features;
- train, log to MLflow, register to Unity Catalog, set the champion alias, and batch-score;
- validate predicted cohort rates against the known ~42% / ~21% and inspect precision at the decision threshold;
- explain why the model is a cohort detector rather than an individual oracle;
- name governance and monitoring owners.

## What belongs in presentation content

Useful presentation content includes:

- the prediction question and the leakage mental model;
- the origination-time feature boundary;
- the MLflow + Unity Catalog governance flow (track → register → alias → score);
- the honest performance framing (AUC, cohort detector, data ceiling);
- validation discipline (reconcile to known rates, inspect threshold precision);
- the Genie Code natural-language alternative.

Keep these in the live workspace:

- full training and scoring code;
- feature lists and the feature view;
- MLflow runs and the registry screens;
- exact metrics before the exercise;
- the scores table;
- Genie Code forms, generated SQL, and responses.

Use verified screenshots only. Prefer conceptual representations when the target workspace UI has not been rehearsed.

## Optional material

Include only if it improves comprehension without reducing hands-on time:

- calibration detail and precision-recall trade-offs at the threshold;
- a short bridge from Section 03's gold layer to the feature view;
- the Genie Code companion path.

Optional material must not become required product coverage.

## Claims and misconceptions to avoid

Do not:

- use any post-origination feature (payments, settlement, collections, first-installment outcome) — leakage;
- present the model as a high-accuracy individual predictor, or imply causality;
- oversell the ~0.63 AUC, or hide it;
- use sensitive attributes (for example `sex_code`) as features;
- claim a registered or aliased model is validated merely because it registered;
- reveal the reference metrics or cohort rates before participants train;
- imply Serverless removes responsibility for leakage, governance, or monitoring;
- fabricate metrics, screenshots, URLs, identities, or environment values.

## Output request for the slide-generating LLM

Using this content inventory, design effective 16:9 presentation support for the workshop section.

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

Do not generate full implementation code, complete training pipelines, fabricated screenshots, or unsupported product claims.
