# Rebuild the FPD5 model with the Databricks Assistant (Genie)

This runbook reproduces the **exact same** registered model, MLflow run, and batch-scores
table as the released Section 06 lab (`participant-lab.py`). Each step gives a **prompt** you
can type into the Databricks Assistant (the in-notebook ✨ "Genie"/Assistant) **and the exact
code** it should generate. Run the cells top to bottom in a Databricks notebook. If you paste
the code directly instead of prompting, you get the identical result — the prompts are only a
convenience.

> **What "Genie" means here.** Databricks *Genie spaces* answer natural-language questions over
> data with SQL — they do not train models. Model building is done by the **Databricks
> Assistant** inside a notebook. This runbook targets the Assistant. If you meant something
> else by "Genie Code," the code cells stand on their own in any Databricks notebook.

## What you will reproduce

The lab names every asset after the **runner's login email** — `<user_id>` is the email's
local-part, sanitized (e.g. `zhihan.tan@databricks.com` → `zhihan_tan`). There is no team id.

| Asset | Value |
|---|---|
| Registered model | `sean_development_catalog.workshop_labs.unicorn_<user_id>_fpd` (alias `@champion`) |
| MLflow run | `val_roc_auc ≈ 0.627`, `val_pr_auc ≈ 0.412`, calibration + decile metrics |
| Scores table | `unicorn_<user_id>_fpd_scores` — 25,440 rows, one per eligible contract |
| Cohort reconciliation | promo ≈ 41.3% predicted / 42.26% actual; other ≈ 20.4% / 21.03% |

The model is a plain `LogisticRegression` on a deterministic time split, so training is
**reproducible**: the same data produces the same coefficients and the same metrics every run.

> **The model name follows whoever runs it.** Run as `zhihan.tan@databricks.com` and you get
> `unicorn_zhihan_tan_fpd`; run as someone else and the `<user_id>` changes accordingly. To force
> a specific id regardless of who runs it, set `user_id = "zhihan_tan"` in Step 2.
>
> **Re-running registers a *new version*** (v2, v3, …) of that user's model — identically trained —
> and repoints `@champion` to it. That is expected.

## Before you start

- **Compute:** serverless notebook compute (Step 1 installs the libraries) **or** a Databricks
  ML Runtime cluster (libraries preinstalled — Step 1 becomes a no-op).
- **Data:** `sean_development_catalog` must contain the read-only `core_lending` schema (8 tables,
  as-of date `2026-09-01`) and a `workshop_labs` schema you can write to (`CREATE TABLE`,
  `CREATE MODEL`).
- Create a new Python notebook, attach compute, and work through the steps. No team id or widget
  to set — the notebook derives your `user_id` from your login automatically.

---

## Step 1 — Install the ML libraries

**Prompt:** *"Install mlflow and scikit-learn quietly with pip, then restart Python."*

```python
%pip install --quiet mlflow scikit-learn
```

```python
dbutils.library.restartPython()
```

*On ML Runtime you can skip this step.*

---

## Step 2 — Configure the run and derive the object names

**Prompt:** *"Set catalog to sean_development_catalog and validate it. Confirm the source as-of date
is 2026-09-01. Derive a user_id from the current user's email local-part (lowercased, non-alphanumerics
to underscores), and build the feature-view, UC model, and scores-table names as unicorn_<user_id>_fpd*.
Register models in Unity Catalog."*

```python
import re
from datetime import date
import mlflow
from mlflow.tracking import MlflowClient
from pyspark.sql import functions as F

CATALOG = "sean_development_catalog"

WORKSHOP_CATALOG = "sean_development_catalog"   # released target catalog
AS_OF_DATE = date.fromisoformat("2026-09-01")
FPD5_GRACE_DAYS = 5

if CATALOG != WORKSHOP_CATALOG:
    raise ValueError(f"This runbook writes only to {WORKSHOP_CATALOG}.")

CATALOG_SQL = f"`{CATALOG}`"
CORE_SQL = f"{CATALOG_SQL}.`core_lending`"
LABS_SQL = f"{CATALOG_SQL}.`workshop_labs`"

# Confirm the source as-of date matches before deriving any labels.
source_as_of_date = (
    spark.sql(f"DESCRIBE DETAIL {CORE_SQL}.`installment`")
    .selectExpr("properties['workshop.as_of_date'] AS d").first()[0]
)
if source_as_of_date != AS_OF_DATE.isoformat():
    raise ValueError(f"as-of mismatch: source is {source_as_of_date!r}, expected {AS_OF_DATE.isoformat()}")

# Per-user id from the login email, e.g. zhihan.tan@databricks.com -> zhihan_tan
current_user = spark.sql("SELECT current_user() AS u").first().u
user_id = re.sub(r"[^a-z0-9_]", "_", current_user.split("@")[0].lower()).strip("_") or "user"
if not user_id[0].isalpha():
    user_id = f"u_{user_id}"
user_id = user_id[:40]
# To force a specific id regardless of who runs it, uncomment:
# user_id = "zhihan_tan"

FEATURE_VIEW = f"unicorn_{user_id}_fpd_features"
MODEL_NAME = f"{CATALOG}.workshop_labs.unicorn_{user_id}_fpd"
SCORES_TABLE = f"unicorn_{user_id}_fpd_scores"
SCORES_FQ = f"{CATALOG}.workshop_labs.{SCORES_TABLE}"

mlflow.set_registry_uri("databricks-uc")   # register models in Unity Catalog
# Optional: co-locate runs in a named experiment (otherwise the notebook's own experiment is used)
# mlflow.set_experiment(f"/Shared/hc_workshop/fpd5_{user_id}")
print("model:", MODEL_NAME)
```

**Expected:** prints `model: sean_development_catalog.workshop_labs.unicorn_<user_id>_fpd`.

---

## Step 3 — Confirm the inherited source tables

**Prompt:** *"Check that all eight core_lending tables exist and raise if any are missing."*

```python
expected_tables = {"customer","retail_location","loan_product","loan_application",
                   "credit_contract","installment","payment","collection_action"}
actual_tables = {r.tableName for r in spark.sql(f"SHOW TABLES IN {CORE_SQL}").collect()}
missing = expected_tables - actual_tables
if missing:
    raise RuntimeError(f"Workshop dataset incomplete. Missing: {sorted(missing)}")
print(f"All {len(expected_tables)} source tables present in {CATALOG}.core_lending")
```

---

## Step 4 — Build the leakage-safe FPD5 feature set

**Prompt:** *"Build one row per eligible fixed-term contract. Label FPD5 from the first
installment (settled_date is null or on/after due_date + 5 days), keeping only first installments
where due_date + 5 days <= 2026-09-01. Use only origination-time features from customer,
application, product, and store-reference — never installments/payments/collections/contract
status/settlement. Register it as a temp view, assert one row per contract, and show FPD5 rate by
promotion cohort."*

```python
features = spark.sql(
    f"""
    WITH first_installment AS (
      SELECT
        contract_id,
        CASE
          WHEN settled_date IS NULL OR settled_date >= date_add(due_date, {FPD5_GRACE_DAYS})
          THEN 1 ELSE 0
        END AS fpd5_flag
      FROM {CORE_SQL}.`installment`
      WHERE installment_no = 1
        AND date_add(due_date, {FPD5_GRACE_DAYS}) <= DATE'{AS_OF_DATE.isoformat()}'
    )
    SELECT
      c.contract_id,
      c.origination_date,
      f.fpd5_flag,
      FLOOR(datediff(c.origination_date, cust.birth_date) / 365.25) AS applicant_age_years,
      datediff(c.origination_date, cust.customer_since_date)        AS customer_tenure_days,
      CAST(cust.monthly_income_amount AS DOUBLE)                    AS monthly_income_amount,
      cust.employment_type_code,
      CAST(a.requested_amount AS DOUBLE)     AS requested_amount,
      a.requested_tenor_months,
      CAST(a.declared_income_amount AS DOUBLE) AS declared_income_amount,
      CAST(a.underwriting_score AS DOUBLE)   AS underwriting_score,
      a.application_channel_code,
      CASE WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026' THEN 1 ELSE 0 END AS is_zero_smartphone_promo,
      a.item_category_code,
      CAST(a.financed_amount AS DOUBLE)      AS financed_amount,
      ROUND(CAST(a.requested_amount AS DOUBLE) / NULLIF(CAST(a.declared_income_amount AS DOUBLE), 0), 4) AS loan_to_income,
      p.product_type_code,
      p.interest_method_code,
      COALESCE(l.merchant_type_code, 'NO_STORE') AS merchant_type_code,
      COALESCE(l.region_code, 'NO_STORE')        AS store_region_code,
      COALESCE(a.sales_associate_id, 'NO_ASSOCIATE') AS sales_associate_id,
      CASE WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026'
           THEN '0% smartphone promotion' ELSE 'Other eligible originations' END AS promotion_cohort
    FROM {CORE_SQL}.`credit_contract` AS c
    JOIN {CORE_SQL}.`loan_application` AS a ON c.application_id = a.application_id
    JOIN {CORE_SQL}.`customer`         AS cust ON a.customer_id = cust.customer_id
    JOIN {CORE_SQL}.`loan_product`     AS p ON a.product_id = p.product_id
    JOIN first_installment             AS f ON c.contract_id = f.contract_id
    LEFT JOIN {CORE_SQL}.`retail_location` AS l ON a.store_id = l.store_id
    """
)
features.createOrReplaceTempView(FEATURE_VIEW)

if features.groupBy("contract_id").count().filter("count > 1").count():
    raise RuntimeError("FPD5 feature set is not at one-row-per-contract grain")

print(f"Eligible contracts: {features.count():,}")
display(
    features.groupBy("promotion_cohort").agg(
        F.count("*").alias("eligible_contracts"),
        F.sum("fpd5_flag").alias("fpd5_contracts"),
        F.round(F.avg("fpd5_flag") * 100, 2).alias("fpd5_rate_pct"),
    ).orderBy(F.desc("fpd5_rate_pct"))
)
```

**Expected:** `Eligible contracts: 25,440`; promotion cohort ≈ 42.26%, other ≈ 21.03%.

---

## Step 5 — Train the interpretable model with MLflow tracking

**Prompt:** *"Pull the features to pandas, split by origination_date at the 80th percentile (older
vintages train, newest validate), build a pipeline with median-impute + scale for numeric and
constant-impute + one-hot for categorical, and fit a LogisticRegression(max_iter=1000). Turn on
MLflow autologging without logging the model, then in a run log val ROC-AUC and PR-AUC, the split
cutoff, a model signature, and the model with cloudpickle."*

```python
import pandas as pd
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = ["applicant_age_years","customer_tenure_days","monthly_income_amount","requested_amount",
           "requested_tenor_months","declared_income_amount","underwriting_score","financed_amount",
           "loan_to_income","is_zero_smartphone_promo"]
CATEGORICAL = ["employment_type_code","application_channel_code","item_category_code",
               "product_type_code","interest_method_code","merchant_type_code","store_region_code"]
LABEL = "fpd5_flag"

pdf = (features.select("contract_id","origination_date",LABEL,"promotion_cohort","sales_associate_id",
                       *NUMERIC,*CATEGORICAL).toPandas())
pdf["origination_date"] = pd.to_datetime(pdf["origination_date"])
for col in CATEGORICAL:
    pdf[col] = pdf[col].astype("string").fillna("MISSING")

cutoff = pdf["origination_date"].quantile(0.8)     # ~80% oldest train, newest ~20% validate
train_mask = pdf["origination_date"] <= cutoff
X_cols = NUMERIC + CATEGORICAL
X_train, y_train = pdf.loc[train_mask, X_cols], pdf.loc[train_mask, LABEL]
X_valid, y_valid = pdf.loc[~train_mask, X_cols], pdf.loc[~train_mask, LABEL]
print(f"split at {cutoff.date()}: train={len(X_train):,} validate={len(X_valid):,}")

pre = ColumnTransformer([
    ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC),
    ("cat", Pipeline([("impute", SimpleImputer(strategy="constant", fill_value="MISSING")),
                      ("ohe", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL),
])
pipe = Pipeline([("prep", pre), ("clf", LogisticRegression(max_iter=1000))])

mlflow.sklearn.autolog(log_models=False, silent=True)
with mlflow.start_run(run_name=f"fpd5_{user_id}") as run:
    pipe.fit(X_train, y_train)
    valid_proba = pipe.predict_proba(X_valid)[:, 1]
    val_auc = roc_auc_score(y_valid, valid_proba)
    val_pr = average_precision_score(y_valid, valid_proba)
    mlflow.log_metric("val_roc_auc", val_auc)
    mlflow.log_metric("val_pr_auc", val_pr)
    mlflow.log_param("time_split_cutoff", str(cutoff.date()))
    signature = infer_signature(X_valid, pipe.predict(X_valid))
    mlflow.sklearn.log_model(pipe, artifact_path="model",
                             serialization_format="cloudpickle", signature=signature)
    run_id = run.info.run_id
print(f"Validation ROC-AUC {val_auc:.3f} | PR-AUC {val_pr:.3f}")
```

**Expected:** split at `2026-03-31`; `Validation ROC-AUC 0.627 | PR-AUC 0.412`.

---

## Step 6 — Log out-of-sample calibration and decile lift

**Prompt:** *"On the validation set, compute predicted-vs-actual FPD5 by cohort and the actual FPD5
rate in the top and bottom predicted-risk deciles, and log them as metrics on the same run."*

```python
val_eval = pdf.loc[~train_mask, [LABEL, "is_zero_smartphone_promo"]].copy()
val_eval["predicted_risk"] = valid_proba
val_eval["cohort"] = val_eval["is_zero_smartphone_promo"].map(
    {1: "0% smartphone promotion", 0: "Other eligible originations"})
val_eval["risk_decile"] = pd.qcut(val_eval["predicted_risk"].rank(method="first"), 10, labels=False) + 1

calibration = (val_eval.groupby("cohort").agg(
    contracts=(LABEL, "size"),
    avg_predicted_pct=("predicted_risk", lambda s: round(float(s.mean()) * 100, 2)),
    actual_fpd5_pct=(LABEL, lambda s: round(float(s.mean()) * 100, 2))).reset_index())
decile_lift = (val_eval[val_eval["risk_decile"].isin([1, 10])].groupby("risk_decile").agg(
    contracts=(LABEL, "size"),
    actual_fpd5_pct=(LABEL, lambda s: round(float(s.mean()) * 100, 2))).reset_index())

with mlflow.start_run(run_id=run_id):
    for _, r in calibration.iterrows():
        tag = "promo" if r["cohort"].startswith("0%") else "other"
        mlflow.log_metric(f"val_{tag}_predicted_pct", float(r["avg_predicted_pct"]))
        mlflow.log_metric(f"val_{tag}_actual_pct", float(r["actual_fpd5_pct"]))
    _dec = decile_lift.set_index("risk_decile")["actual_fpd5_pct"].to_dict()
    mlflow.log_metric("val_decile10_actual_pct", float(_dec.get(10, 0.0)))
    mlflow.log_metric("val_decile1_actual_pct", float(_dec.get(1, 0.0)))

display(spark.createDataFrame(calibration))
display(spark.createDataFrame(decile_lift))
```

**Expected:** promo ≈ 41% predicted / 44% actual, other ≈ 20% / 24%; decile 10 ≈ 49%, decile 1 ≈ 21%.

---

## Step 7 — Read the coefficient reason codes

**Prompt:** *"Show the 12 largest logistic-regression coefficients as reason codes, marking whether
each raises or lowers FPD5 risk."*

```python
feat_names = pipe.named_steps["prep"].get_feature_names_out()
coefs = pipe.named_steps["clf"].coef_[0]
drivers = (spark.createDataFrame(
        [(n.split("__", 1)[-1], float(c)) for n, c in zip(feat_names, coefs)],
        ["feature", "coefficient"])
    .withColumn("direction", F.when(F.col("coefficient") > 0, "raises FPD5 risk").otherwise("lowers FPD5 risk"))
    .orderBy(F.desc(F.abs(F.col("coefficient")))).limit(12))
display(drivers)
```

**Expected:** the 0% smartphone promo flag and cash-loan product are among the top risk-raisers; a higher underwriting score lowers risk.

---

## Step 8 — Register the model in Unity Catalog and set `@champion`

**Prompt:** *"Register the logged model in Unity Catalog under MODEL_NAME, set the champion alias to
the new version, and tag the version with its validation ROC-AUC."*

```python
version = mlflow.register_model(f"runs:/{run_id}/model", MODEL_NAME).version
client = MlflowClient()
client.set_registered_model_alias(MODEL_NAME, "champion", version)
client.set_model_version_tag(MODEL_NAME, version, "val_roc_auc", f"{val_auc:.3f}")
print(f"Registered {MODEL_NAME} version {version} @champion")
```

**Expected:** a new version registered with alias `@champion` and tag `val_roc_auc=0.627`.

---

## Step 9 — Batch score the eligible population

**Prompt:** *"Load the champion model by alias, score every eligible contract, flag risk at 0.35,
write a Delta table with model_name/model_version, then show predicted-vs-actual by cohort and the
flagged count and precision at the threshold."*

```python
RISK_THRESHOLD = 0.35

champion = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}@champion")
scores_pdf = pdf[["contract_id", LABEL, "promotion_cohort", "product_type_code",
                  "store_region_code", "sales_associate_id"]].copy()
scores_pdf["fpd5_risk"] = champion.predict_proba(pdf[X_cols])[:, 1]
scores_pdf["fpd5_risk_flag"] = (scores_pdf["fpd5_risk"] >= RISK_THRESHOLD).astype(int)
scores_pdf = scores_pdf.rename(columns={LABEL: "fpd5_actual"})
for _c in ["promotion_cohort", "product_type_code", "store_region_code", "sales_associate_id"]:
    scores_pdf[_c] = scores_pdf[_c].astype(str)

scores_sdf = (spark.createDataFrame(scores_pdf)
    .withColumn("scored_at", F.current_timestamp())
    .withColumn("model_name", F.lit(MODEL_NAME))
    .withColumn("model_version", F.lit(str(version))))
(scores_sdf.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(SCORES_FQ))
print(f"Wrote {scores_sdf.count():,} scored contracts to {SCORES_FQ}")

display(spark.table(SCORES_FQ).groupBy("promotion_cohort").agg(
    F.count("*").alias("contracts"),
    F.round(F.avg("fpd5_risk") * 100, 2).alias("avg_predicted_risk_pct"),
    F.round(F.avg("fpd5_actual") * 100, 2).alias("actual_fpd5_pct"),
    F.sum("fpd5_risk_flag").alias("flagged_high_risk")).orderBy(F.desc("avg_predicted_risk_pct")))

total = spark.table(SCORES_FQ).count()
prec = spark.table(SCORES_FQ).where("fpd5_risk_flag = 1").agg(
    F.count("*").alias("n"), F.round(F.avg("fpd5_actual") * 100, 2).alias("precision_pct")).first()
print(f"At threshold {RISK_THRESHOLD}: flagged {prec.n:,} of {total:,} "
      f"({prec.n/total*100:.1f}%), precision {prec.precision_pct}%.")
```

**Expected:** 25,440 rows; promo ≈ 41.3% predicted / 42.26% actual, other ≈ 20.4% / 21.03%; flagged ≈ 5,485 (≈21.6%), precision ≈ 41.5%.

---

## Step 10 — Verify you reproduced the reference instance

**Prompt:** *"Print the run id, model name, and champion version, and show the last few Delta history
entries for the scores table."*

```python
print("MLflow run id:", run_id)
print("Registered model:", MODEL_NAME, "| champion version:", version)
display(spark.sql(f"DESCRIBE HISTORY {LABS_SQL}.`{SCORES_TABLE}`")
        .select("version", "timestamp", "operation").orderBy(F.desc("version")).limit(3))
```

You have reproduced the reference instance when: the eligible population is **25,440**, validation
**ROC-AUC ≈ 0.627 / PR-AUC ≈ 0.412**, a model version carries the **`@champion`** alias with a
signature and a `val_roc_auc` tag, and the scores table holds **25,440** rows with predicted risk
concentrated in the promotion cohort. These match the released `expected-results.md`.

> Everything above is deterministic except the model *name*, which follows the runner's login email.
> Run as `zhihan.tan@databricks.com` (or set `user_id = "zhihan_tan"`) to land on the exact name
> `sean_development_catalog.workshop_labs.unicorn_zhihan_tan_fpd`.
