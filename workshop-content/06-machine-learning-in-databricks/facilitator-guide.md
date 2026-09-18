# Facilitator guide — Introduction to Machine Learning in Databricks

**Facilitator-only:** Participants should start with `README.md`, `participant-lab.py`, and `exercises.md`.

## Delivery intent

This is the operational close of the FPD5 story: the earlier sections found the pattern; here we make it a governed, operable model. Every step answers one of four handover questions:

1. What is the asset, and what data may it legitimately use?
2. Where are its parameters, metrics, versions, aliases, and lineage recorded?
3. How is it promoted, rolled back, and re-run?
4. Who owns retraining, monitoring, and the consumers of its output?

Keep the modelling deliberately simple. The goal is an **interpretable, governed, operable** model, not the highest AUC. Batch scoring is the required path; treat Model Serving, online Feature Store, and Lakehouse Monitoring as optional discussion, not live builds.

## Before participants enter

1. Confirm the dataset passed its generator `SUCCESS` gate and all eight `core_lending` tables exist.
2. Confirm `workshop_labs` and `workshop_shared` exist in the workshop catalog and participants have `CREATE TABLE` + `CREATE MODEL` on `workshop_labs`.
3. Confirm `participant-lab.py` is available under `/Workspace/Shared/hc_workshop/workshop-content/06-machine-learning-in-databricks/`.
4. Confirm compute runs the notebook: serverless notebook compute (the first cell `%pip install`s MLflow and scikit-learn, then restarts Python) or a Databricks ML Runtime all-purpose resource.
5. Run the notebook once end-to-end on the assigned compute to warm the environment and confirm a registered model version and scores table appear.
6. Fill in the runtime, group, team ID, and any optional serving values marked `TBD` in the section README.
7. Rehearse with a non-admin participant identity.

The released lab passed an end-to-end workspace validation run (train → register → batch score) against `sean_development_catalog`. Confirm the same on the final workshop compute before the session.

## Minute-by-minute run of show

| Time | Minutes | Mode | Activity | Observable result |
|---|---:|---|---|---|
| 4:00–4:04 | 4 | Slide | Reconnect the FPD5 story; state the prediction question and leakage rule | Participants can state the target and the fiction boundary |
| 4:04–4:10 | 6 | Slides | Legitimate vs leakage features; time vs random split; batch vs serving | Participants justify origination-time features and a time split |
| 4:10–4:14 | 4 | Watch me | Open notebook, run the `%pip` setup, enter `team_id`, show source inventory | Libraries install, session restarts, eight tables confirmed |
| 4:14–4:28 | 14 | Run with me | Build the leakage-safe feature set, train with MLflow, check out-of-sample calibration and decile lift, read coefficients, register to UC + `champion` | Holdout calibration/decile shown; a registered version with signature, alias, and metrics |
| 4:28–4:36 | 8 | Run with me | Batch score the full book; reconcile predicted risk to the promotion cohort; note the review-queue size and precision | Predicted risk higher for the promotion cohort; ~5,485 flagged at 0.35 |
| 4:36–4:44 | 8 | Try it | Complete the model handover note | Owner, retrain trigger, threshold, and caveat recorded |
| 4:44–4:52 | 8 | Operate it | Inspect experiment, model version/alias/lineage, scores table; promote/rollback | Participants locate lineage and describe a rollback |
| 4:52–4:56 | 4 | Buffer | Absorb install, startup, or permission delay | Core checkpoint protected |
| 4:56–5:00 | 4 | Checkpoint | Assign operational ownership of the model | One owner, one retrain trigger, one rollback step named |

## 4:04–4:10 — Feature and split decisions

Use slides for the concepts before touching the notebook.

### Talking points

- **Leakage is the central risk.** We predict FPD5 at origination, so features may use only customer, application, product, and store-reference attributes known at decision time. Installments, payments, collections, contract status, and settlement describe the outcome — using them inflates metrics and produces a useless production model.
- **Split by time, not randomly.** Training on older vintages and validating on the newest mirrors scoring future originations and exposes vintage drift. A random split leaks future information across the boundary.
- **Interpretability first.** A logistic-regression scorer gives coefficient reason codes an operator and a reviewer can read, which matters for a lending decision and adverse-action explanation.
- **Batch vs serving.** Batch scoring on a schedule is the required path for a periodic origination-review queue. A real-time REST endpoint is justified only when a decision must happen in the application flow within milliseconds.

## 4:14–4:36 — Train, register, and batch score

### Exact UI path

1. **Workspace > Shared > hc_workshop > workshop-content > 06-machine-learning-in-databricks > participant-lab**
2. Attach serverless notebook compute (or the assigned ML Runtime resource) and enter the assigned `team_id`.
3. Run sequentially. Pause at:
   - **Setup:** explain that serverless installs MLflow/scikit-learn and restarts Python; on ML Runtime this is a no-op.
   - **Feature set:** stress the leakage rule and the one-row-per-contract grain; the cohort rates must match the analysis sections.
   - **Train:** point out MLflow autologging capturing parameters and metrics; note the modest, honest ROC-AUC (~0.63) and that the promotion and product carry most of the signal.
   - **Validation quality:** on the held-out recent vintages, calibration is close but slightly under-predicts (the newest vintages run riskier) — a vintage-drift talking point; the top decile is roughly 2.5× the bottom decile.
   - **Coefficients:** read the top risk-raising and risk-lowering drivers as reason codes.
   - **Register:** show the three-level UC name, the signature requirement, and the `champion` alias.
   - **Batch score:** score the full book for the review queue; connect predicted risk back to the promotion cohort, and note the flagged share (~5,485 at 0.35) and precision. This is the required inference path.

Do not reveal the exact metrics before groups reach them. Ask one group to read its handover note, then correct any causal or "confirmed fraud" overreach.

### Checkpoint

A registered model version exists with the `champion` alias and a signature; the scores table has one row per eligible contract; predicted risk is higher for the 0% smartphone promotion than for other originations.

## 4:44–4:52 — Operate the model

### Exact UI paths

1. **Catalog > `<catalog>` > workshop_labs > Models > `unicorn_<team_id>_<runner_id>_fpd`**
   - Show versions, the `champion` alias, tags, and the model signature.
   - Open **Lineage** and trace the version to its MLflow run and the `core_lending` tables.
2. **Experiments > (the notebook's experiment)**
   - Show the run's parameters, metrics, and artifacts; compare two runs if time allows.
3. **Catalog > workshop_labs > `unicorn_<team_id>_<runner_id>_fpd_scores`**
   - Show `model_name`/`model_version` columns and `DESCRIBE HISTORY`.

### Talking points

- Promotion is an alias move: register a new version, evaluate, then point `champion` at it. Rollback is the same move back — no data copy.
- The scores table records which model version produced each prediction, so an operator can reproduce and audit a decision.
- Model Serving would add a REST endpoint and inference tables; Lakehouse Monitoring would profile inputs and outputs and detect drift. Both are optional here; name them as the next operational investments.

## 4:56–5:00 — Handover checkpoint

Ask each team to state, for the model asset: one owner, one retraining trigger or cadence, and one rollback step. Build the checklist aloud through the section:

- Model: owner, training data and leakage boundary, signature, champion alias, promotion/rollback path.
- Experiment: run history, metrics, comparison, reproducibility.
- Scores table: consumer, refresh schedule, version traceability, cleanup boundary.
- Monitoring (future): drift signal, performance metric, alert owner.

## Fallbacks

- **No serverless notebook compute:** attach an approved Databricks ML Runtime all-purpose resource; the `%pip install` cell becomes a fast no-op. Record the exception.
- **`%pip install` blocked by policy:** use an ML Runtime resource where MLflow and scikit-learn are preinstalled.
- **Unity Catalog model registry unavailable:** stop and escalate; do not fall back to the workspace model registry for a governed handover. Explain that UC registration is the point of the exercise.
- **Model Serving not enabled:** keep to batch scoring; describe serving on a slide. Do not claim an endpoint was created.
- **Insufficient `workshop_labs` permission:** the administrator grants `CREATE TABLE` and `CREATE MODEL`; do not redirect output to `core_lending` or a personal catalog.

## Facilitator references

- [MLflow tracking](https://docs.databricks.com/mlflow/tracking)
- [Models in Unity Catalog](https://docs.databricks.com/machine-learning/manage-model-lifecycle/)
- [Model signatures](https://mlflow.org/docs/latest/model/signatures.html)
- [Batch inference](https://docs.databricks.com/machine-learning/model-inference/)
- [Model Serving](https://docs.databricks.com/machine-learning/model-serving/)
- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/)
