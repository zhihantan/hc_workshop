# Expected results and troubleshooting

**Participant note:** Complete the focused exercise before opening this file.

These values assume the default standard-scale dataset, master seed `20260922`, and as-of date `2026-09-01`, scored by the released interpretable logistic-regression model. They were captured from an end-to-end validation run against `sean_development_catalog`. A different approved generator configuration, model, or split can produce different numbers.

## Observable results

### Setup and features

- The `%pip install` cell installs MLflow and scikit-learn, then the Python session restarts. On ML Runtime this is a fast no-op.
- All eight `core_lending` tables are present; the eligible FPD5 population is **25,440** contracts at one row per contract (POS installment 21,955; cash loan 3,485 — only fixed-term products have installments).
- Cohort FPD5 rates reproduce the analysis sections:
  - 0% smartphone promotion: **42.26%**
  - Other eligible originations: **21.03%**
  - Overall: **25.14%**

### Training and validation quality (out-of-sample)

- The time split is at `origination_date` **2026-03-31** (≈80% oldest vintages train, newest ≈20% validate); the exact counts print in the notebook.
- Validation **ROC-AUC ≈ 0.63** and **PR-AUC ≈ 0.41** on the held-out recent vintages. This is a deliberately modest, honest score: the promotion flag and product carry most of the signal, so the model is a useful screen rather than a high-precision detector.
- **Calibration by cohort** (validation set): predicted vs actual FPD5 is close — promotion ≈**41%** predicted vs ≈**44%** actual; other originations ≈**20%** predicted vs ≈**24%** actual. The newest vintages run slightly riskier than the older training vintages, so the model mildly under-predicts them — a realistic vintage-drift talking point.
- **Rank-ordering** (validation set): the highest predicted-risk decile has ≈**49%** actual FPD5 versus ≈**21%** in the lowest decile.
- The coefficient table lists the strongest risk drivers. The **0% smartphone promotion flag** and **cash-loan product** are among the largest risk-raising terms; a higher **underwriting score** lowers predicted risk. Exact coefficients vary slightly with the environment.

### Registration

- A model version is registered as `<catalog>.workshop_labs.unicorn_<user_id>_fpd` with the `champion` alias, a model signature, and a `val_roc_auc` tag.
- Catalog Explorer shows lineage from the version to its MLflow run and the `core_lending` source tables.

### Batch scoring (full eligible book)

- The scores table `unicorn_<user_id>_fpd_scores` has one row per eligible contract and carries `model_name` and `model_version`.
- Scored across the whole book, predicted risk reproduces the known cohort gap: promotion ≈**41.3%** predicted (vs **42.26%** actual), other ≈**20.4%** predicted (vs **21.03%** actual).
- At the review threshold **0.35**, about **5,485** contracts are flagged (≈**21.6%** of the book) — effectively the entire promotion cohort plus a few hundred higher-risk other originations — with precision ≈**41.5%** (about 1.65× the base rate).

Small differences are acceptable when the environment or library versions differ. Large differences usually mean the as-of date, eligibility filter, leakage rule, or split changed.

## Shortest recovery paths

### `ModuleNotFoundError: No module named 'mlflow'` (or `sklearn`)

Run the first `%pip install` cell and let the Python session restart before running later cells, or attach a Databricks ML Runtime resource. Do not `import` the libraries before the install cell has run.

### `Model ... did not contain any signature metadata`

Unity Catalog requires a signature. Confirm the `infer_signature(...)` call runs and its result is passed to `log_model`. Do not register a model logged without a signature.

### `references untrusted types` on model save

The released notebook logs with `serialization_format="cloudpickle"`. If a customized notebook removed that, restore it rather than adding broad trusted-type overrides.

### The catalog or as-of-date validation fails

Do not bypass the guard. Confirm the notebook was released for the configured workshop catalog and that `installment` carries the expected `workshop.as_of_date` property. If an administrator generated a different as-of date or catalog, update the notebook and revalidate before continuing.

### `CREATE MODEL` or `CREATE TABLE` is denied in `workshop_labs`

Ask the administrator to grant `USE SCHEMA`, `CREATE TABLE`, and `CREATE MODEL` on `workshop_labs`. Do not redirect output to `core_lending`, `main`, `hive_metastore`, or a personal catalog.

### A source table is missing

Stop the lab. The administrator reruns the dataset generator and confirms its final `SUCCESS` message. Do not create substitute source tables.

### Predicted risk does not separate the cohorts

Check that the leakage rule held (only origination-time features), that the label uses the day-five boundary, and that the eligible population filter (`installment_no = 1`, `due_date + 5 <= as_of`) is intact. A flat separation usually means a feature or label error, not a modeling failure.
