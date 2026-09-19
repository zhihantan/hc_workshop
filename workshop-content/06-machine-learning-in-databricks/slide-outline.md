# Recommended slide outline — Section 06

Use seven concise slides. The slides carry the **decision frameworks**; the notebook carries the code, metrics, and evidence. This section is mostly hands-on, so keep the slides tight — several (Slides 5–7) are best shown at the matching hands-on transition rather than all up front.

## Slide 1 — From investigation to operable model

**Title:** We found the FPD5 hotspot — now make it a governed model.

Show:

- Sections 01–05 found FPD5 concentrated in the 0% smartphone promotion (and by store and sales associate).
- This section trains an interpretable model, registers it in Unity Catalog, and batch-scores the book — then hands it over.
- Prediction question: will a new contract be FPD5, decided **at origination**?
- FPD5 denominator: first installments that reached `due_date + 5 days` by `2026-09-01`.
- Elevated predicted risk is an investigation signal, not confirmed fraud; all data is synthetic.

Transition: "First, decide which features we're even allowed to use."

## Slide 2 — Legitimate features vs leakage

**Best as a slide:** the single most important modeling decision.

| Allowed — known at origination | Forbidden — describes the outcome |
|---|---|
| Customer (age, tenure, income, employment) | Installments |
| Application (requested amount, tenor, declared income, underwriting score, channel, promotion, item) | Payments |
| Product (type, interest method) | Collections |
| Store reference (merchant type, region) | Contract status / settlement |

Call out:

- We predict at origination, so only decision-time attributes qualify.
- Using outcome fields inflates metrics and produces a useless production model.
- Store/associate *identity* is an investigation signal, kept out of the borrower model.

Transition: "How we split the data matters as much as which features we use."

## Slide 3 — Split by time, not at random

**Best as a slide:** prevent the default random-split habit.

- Train on older vintages; validate on the newest.
- Mirrors production: we score future originations from past ones.
- Exposes vintage drift — newer vintages can run riskier than the training window.
- A random split leaks future information across the boundary and flatters the score.

Transition: "With features and split decided, we choose a model we can explain."

## Slide 4 — Interpretability over raw accuracy (and an honest ceiling)

**Best as a slide:** set expectations before the metrics appear in the notebook.

- Logistic regression gives coefficient **reason codes** — readable for a lending decision and adverse-action explanation.
- Expect a **modest, well-calibrated** score (~0.63 ROC-AUC), not a high-precision detector.
- A sudden 0.9 AUC would signal **leakage**, not success.
- Tested levers — richer features, gradient boosting, store/associate identity — don't materially beat it: the signal ceiling is in the (synthetic) data. Calibration and interpretability are the win.

Transition: "Training is one thing; governing the model is the point of this section."

## Slide 5 — Where the model lives: MLflow + Unity Catalog

**Best as a slide before the register step.** Separate experiment tracking from the governed registry.

```text
MLflow run                    Unity Catalog model
(params, metrics, artifact) → register → (versions, @champion alias,
                                          signature, lineage) → batch score
```

- MLflow records parameters, metrics, and the trained artifact.
- Unity Catalog records versions, the `champion` alias, the model signature, and lineage back to `core_lending`.
- Promotion is an **alias move**; rollback is the same move back — no data copy.

Transition: "How we serve predictions is a deliberate choice, not an afterthought."

## Slide 6 — Batch scoring vs real-time serving

**Best as a slide:** one reusable decision.

| | Batch scoring (required here) | Real-time serving (optional) |
|---|---|---|
| Use when | A periodic origination-review queue | A decision must happen in the app flow, in milliseconds |
| Output | A governed Delta scores table, on a schedule | A REST endpoint + inference tables |
| This workshop | The required path | Discussed, not built |

Call out: an online Feature Store and Lakehouse Monitoring are the next operational investments — name them, don't build them today.

Transition: "Finally, name who owns this after Atlas Ridge leaves."

## Slide 7 — The operational handover

**Best as a slide:** the section's real deliverable.

- **Model:** owner, training data + leakage boundary, signature, champion alias, promote/rollback path.
- **Experiment:** run history, metrics, reproducibility.
- **Scores table:** consumer, refresh cadence, model-version traceability.
- **Monitoring (future):** drift signal, performance metric, alert owner.

Checkpoint: each participant names one owner, one retraining trigger, and one rollback step.

## Keep off the slides

Use the notebook or live workspace for:

- Full feature-building SQL and training code.
- Exact metric values (ROC-AUC, PR-AUC, calibration, decile lift) before the exercise.
- The coefficient reason-code table.
- Batch-score cohort reconciliation and the flagged-count / precision numbers.
- MLflow run UI and Unity Catalog lineage/alias navigation.
- `DESCRIBE HISTORY` on the scores table.
