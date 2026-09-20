# Final slide-only generation prompt — Machine Learning with MLflow in Databricks

Create the visible presentation slides for the **Introduction to Machine Learning in Databricks** section (mostly hands-on).

This prompt intentionally covers only the portions carried on **slides** — the reusable **decision frameworks**. The feature build, training, MLflow tracking, Unity Catalog registration, and batch scoring are delivered live in the notebook, not on slides. Several slides are best shown **at the matching hands-on transition** rather than all up front.

## Source authority

Resolve conflicts in this order:

1. `../../../workshop-content/06-machine-learning-in-databricks/facilitator-guide.md`
2. `../../../workshop-content/06-machine-learning-in-databricks/participant-lab.py`
3. `../../../workshop-content/06-machine-learning-in-databricks/slide-outline.md`
4. `drafts/generate-section-06-machine-learning-slides-v2-content-first.md`
5. `../../../workshop-content/06-machine-learning-in-databricks/{README.md, expected-results.md}`
6. `../../../participant-materials/unicorn-finance-workshop-scenario.md`
7. `../../agenda/workshop-agenda.md`

Implemented workshop behavior is more authoritative than broad agenda language.

## Delivery contract

Generate approximately **seven concise slides** carrying the decision frameworks. Keep them tight — this section is mostly hands-on. Suggested placement (confirm exact minute windows against `facilitator-guide.md`):

| Slide | Moment in the section |
|---|---|
| 1 — Investigation → operable model | Opening |
| 2 — Legitimate features vs leakage | Before building the feature view |
| 3 — Split by time, not at random | Before the split |
| 4 — Interpretability + honest ceiling | Before training metrics appear |
| 5 — MLflow + Unity Catalog | Before the register step |
| 6 — Batch scoring vs real-time serving | Before batch scoring |
| 7 — Operational handover | Closing checkpoint |

Slides 5–7 are best shown at the matching hands-on transition. Do not create slides for the feature/training code, exact metric values, the coefficient table, or MLflow / Catalog Explorer navigation — those are live.

## Audience and role

- The real audience is Home Credit Philippines, with basic SQL and Python familiarity.
- Participants act as Unicorn Finance's internal data team taking ownership of an inherited Databricks platform after Atlas Ridge Consulting hands over.
- Here they train, govern, and operate an interpretable FPD5 model — then decide how the internal team runs it after handover.
- Unicorn Finance, Atlas Ridge, Nova Mobile, and all workshop records are fictional or synthetic.

## Visible-slide content

### Slide 1 — From investigation to operable model
- Sections 01–05 found FPD5 concentrated in the 0% smartphone promotion (and by store and sales associate).
- This section trains an interpretable model, registers it in Unity Catalog, and batch-scores the book — then hands it over.
- Prediction question: will a new contract be FPD5, decided **at origination**? (Same FPD5 denominator as every section: first installments that reached `due_date + 5 days` by `2026-09-01`.)
- Elevated predicted risk is an investigation signal, not confirmed fraud; all data is synthetic.

### Slide 2 — Legitimate features vs leakage (the single most important decision)
| Allowed — known at origination | Forbidden — describes the outcome |
|---|---|
| Customer (age, tenure, income, employment) | Installments |
| Application (requested amount, tenor, declared income, underwriting score, channel, promotion, item) | Payments |
| Product (type, interest method) | Collections |
| Store reference (merchant type, region) | Contract status / settlement |
- We predict *at origination*, so only decision-time attributes qualify. Outcome fields inflate metrics and produce a useless production model.
- Store / associate **identity** is an investigation signal, kept out of the borrower model.

### Slide 3 — Split by time, not at random
- Train on older vintages; validate on the newest. Mirrors production: we score future originations from past ones.
- Exposes vintage drift; a random split leaks future information across the boundary and flatters the score.

### Slide 4 — Interpretability over raw accuracy (and an honest ceiling)
- Logistic regression gives coefficient **reason codes** — readable for a lending decision and adverse-action explanation.
- Expect a **modest, well-calibrated** score (**≈0.63 ROC-AUC**), not a high-precision detector. A sudden 0.9 AUC would signal **leakage**, not success.
- Tested levers — richer features, gradient boosting, store/associate identity — don't materially beat it: the signal ceiling is in the (synthetic) data. Calibration and interpretability are the win.

### Slide 5 — Where the model lives: MLflow + Unity Catalog
- `MLflow run (params, metrics, artifact) → register → Unity Catalog model (versions, @champion alias, signature, lineage) → batch score`.
- MLflow records parameters, metrics, and the trained artifact. Unity Catalog records versions, the `@champion` alias, the model **signature**, and lineage back to `core_lending`.
- Promotion is an **alias move**; rollback is the same move back — no data copy.

### Slide 6 — Batch scoring vs real-time serving
| | Batch scoring (required here) | Real-time serving (optional) |
|---|---|---|
| Use when | A periodic origination-review queue | A decision inside the app flow, in milliseconds |
| Output | A governed Delta scores table, on a schedule | A REST endpoint + inference tables |
| This workshop | The required path | Discussed, not built |
- An online Feature Store and Lakehouse Monitoring are the next operational investments — name them, don't build them today.

### Slide 7 — The operational handover (the real deliverable)
- **Model:** owner · training data + leakage boundary · signature · `@champion` alias · promote/rollback path.
- **Experiment:** run history · metrics · reproducibility.
- **Scores table:** consumer · refresh cadence · model-version traceability.
- **Monitoring (future):** drift signal · performance metric · alert owner.
- Checkpoint: each participant names one owner, one retraining trigger, and one rollback step.

## Recommended visuals

- A two-column allowed-vs-forbidden feature table keyed to the leakage boundary.
- A time-split timeline (train older vintages → validate newest).
- The MLflow-run → Unity-Catalog-model → batch-score flow.
- A batch-vs-real-time serving comparison.

Do not fabricate product screenshots or workspace evidence.

## Presenter notes

- Restate the FPD5 definition and the leakage rule (origination-time features only).
- Set expectations before metrics appear: a modest, calibrated ≈0.63 ROC-AUC is the intended result; a suspiciously high score means leakage.
- Keep exact metric values, the coefficient reason-code table, and the flagged-count / precision numbers as checkpoints revealed **after** the matching exercise.

## Excluded from visible slides

- Full feature-building SQL and training code.
- Exact metric values (ROC-AUC, PR-AUC, calibration, decile lift) before the exercise.
- The coefficient reason-code table.
- Batch-score cohort reconciliation and the flagged-count / precision numbers.
- MLflow run UI and Unity Catalog lineage / alias navigation; `DESCRIBE HISTORY` on the scores table.

## Output request

Return: (1) the proposed slide count and narrative; (2) concise visible slide content; (3) presenter notes per slide; (4) recommended visuals; (5) the placement of each slide across the section; (6) the transitions into the live notebook; (7) a coverage check confirming no excluded live-workspace topic became a visible slide, and that batch scoring is shown as required while serving / monitoring are named as optional.

Use a clean 16:9 workshop style. Keep slides tight — this is a hands-on section.
