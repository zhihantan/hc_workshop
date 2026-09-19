# Databricks notebook source
# MAGIC %md
# MAGIC # Section 06 — Introduction to Machine Learning in Databricks
# MAGIC
# MAGIC **Scenario:** Atlas Ridge Consulting built Unicorn Finance's analytics and is handing over operations. Sections 01–05 investigated the 0% smartphone promotion and its first-payment-default (FPD5) hotspots. In this section we train an **interpretable** FPD5 model, track it with MLflow, register it in Unity Catalog, and **batch-score** the eligible population — then decide how the internal team operates it after handover.
# MAGIC
# MAGIC **FPD5 definition (identical to every prior section):** consider only first installments where `due_date + 5 days` is on or before the declared as-of date. A null settlement date, or settlement on/after day five, counts as FPD5.
# MAGIC
# MAGIC **Leakage rule:** we predict FPD5 *at origination*, so features may use only application-, customer-, product-, and store-reference attributes known at decision time. We never use installments, payments, collections, contract status, or settlement — those describe the outcome we are predicting.
# MAGIC
# MAGIC All records are synthetic. An elevated predicted rate is an investigation signal, not proof of fraud.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Setup — install ML libraries
# MAGIC
# MAGIC Serverless notebook compute needs MLflow and scikit-learn for this section. Run this cell first; the Python session restarts automatically. On Databricks ML Runtime these are preinstalled.

# COMMAND ----------
# MAGIC %pip install --quiet mlflow scikit-learn

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
import re
from datetime import date

import mlflow
from mlflow.tracking import MlflowClient
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "sean_development_catalog", "Workshop catalog")

CATALOG = dbutils.widgets.get("catalog").strip()

# Canonical design catalog is `hc_workshop`. This deployment is retargeted to
# `sean_development_catalog`, where the generated dataset was published. A
# facilitator revalidates and updates this constant to move the lab.
WORKSHOP_CATALOG = "sean_development_catalog"
AS_OF_DATE = date.fromisoformat("2026-09-01")
FPD5_GRACE_DAYS = 5

if CATALOG != WORKSHOP_CATALOG:
    raise ValueError(
        f"This released notebook can write only to {WORKSHOP_CATALOG}. "
        "A facilitator must update and revalidate the notebook for a different workshop catalog."
    )

CATALOG_SQL = f"`{CATALOG}`"
CORE_SQL = f"{CATALOG_SQL}.`core_lending`"
LABS_SQL = f"{CATALOG_SQL}.`workshop_labs`"

# Confirm the source as-of date matches this notebook before deriving any labels.
source_as_of_date = (
    spark.sql(f"DESCRIBE DETAIL {CORE_SQL}.`installment`")
    .selectExpr("properties['workshop.as_of_date'] AS workshop_as_of_date")
    .first()[0]
)
if source_as_of_date != AS_OF_DATE.isoformat():
    raise ValueError(
        f"Notebook as-of date {AS_OF_DATE.isoformat()} does not match "
        f"the source table property {source_as_of_date!r}."
    )

# Per-user id derived from the login email, so each participant owns a uniquely named model and table.
current_user = spark.sql("SELECT current_user() AS user_name").first().user_name
user_id = re.sub(r"[^a-z0-9_]", "_", current_user.split("@")[0].lower()).strip("_") or "user"
if not user_id[0].isalpha():
    user_id = f"u_{user_id}"
user_id = user_id[:40]  # keep object names to a sane length

FEATURE_VIEW = f"unicorn_{user_id}_fpd_features"
MODEL_NAME = f"{CATALOG}.workshop_labs.unicorn_{user_id}_fpd"
SCORES_TABLE = f"unicorn_{user_id}_fpd_scores"
SCORES_FQ = f"{CATALOG}.workshop_labs.{SCORES_TABLE}"

mlflow.set_registry_uri("databricks-uc")  # register models in Unity Catalog

display(
    spark.createDataFrame(
        [
            ("user_id", user_id),
            ("catalog", CATALOG),
            ("as_of_date", AS_OF_DATE.isoformat()),
            ("feature_view", FEATURE_VIEW),
            ("registered_model", MODEL_NAME),
            ("scores_table", SCORES_FQ),
        ],
        ["setting", "value"],
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Confirm the inherited source (Watch me)
# MAGIC
# MAGIC The eight `core_lending` tables are shared and read-only. Only fixed-term POS and cash contracts have installments, so only they are eligible for FPD5.

# COMMAND ----------
expected_tables = {
    "customer", "retail_location", "loan_product", "loan_application",
    "credit_contract", "installment", "payment", "collection_action",
}
actual_tables = {r.tableName for r in spark.sql(f"SHOW TABLES IN {CORE_SQL}").collect()}
missing = expected_tables - actual_tables
if missing:
    raise RuntimeError(f"Workshop dataset is incomplete. Missing: {sorted(missing)}")
print(f"All {len(expected_tables)} source tables present in {CATALOG}.core_lending")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Build the leakage-safe FPD5 feature set (Run with me)
# MAGIC
# MAGIC One row per eligible fixed-term contract. The label is the canonical FPD5 flag; every feature is known at origination. We keep this as a session-scoped, user-prefixed temporary view — the model, not another shared table, is the asset we hand over.

# COMMAND ----------
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
      -- customer attributes known at origination
      FLOOR(datediff(c.origination_date, cust.birth_date) / 365.25) AS applicant_age_years,
      datediff(c.origination_date, cust.customer_since_date)        AS customer_tenure_days,
      CAST(cust.monthly_income_amount AS DOUBLE)                    AS monthly_income_amount,
      cust.employment_type_code,
      -- application attributes captured at decision time
      CAST(a.requested_amount AS DOUBLE)     AS requested_amount,
      a.requested_tenor_months,
      CAST(a.declared_income_amount AS DOUBLE) AS declared_income_amount,
      CAST(a.underwriting_score AS DOUBLE)   AS underwriting_score,
      a.application_channel_code,
      CASE WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026' THEN 1 ELSE 0 END AS is_zero_smartphone_promo,
      a.item_category_code,
      CAST(a.financed_amount AS DOUBLE)      AS financed_amount,
      ROUND(CAST(a.requested_amount AS DOUBLE) / NULLIF(CAST(a.declared_income_amount AS DOUBLE), 0), 4) AS loan_to_income,
      -- product commercial rules
      p.product_type_code,
      p.interest_method_code,
      -- store reference context (attributes, not outcomes); NO_STORE for digital/direct
      COALESCE(l.merchant_type_code, 'NO_STORE') AS merchant_type_code,
      COALESCE(l.region_code, 'NO_STORE')        AS store_region_code,
      -- kept for analysis/scoring output only; NOT a model feature (identity leakage / high cardinality)
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

print(f"Created session temporary view: {FEATURE_VIEW}")
print(f"Eligible contracts: {features.count():,}")
display(
    features.groupBy("promotion_cohort").agg(
        F.count("*").alias("eligible_contracts"),
        F.sum("fpd5_flag").alias("fpd5_contracts"),
        F.round(F.avg("fpd5_flag") * 100, 2).alias("fpd5_rate_pct"),
    ).orderBy(F.desc("fpd5_rate_pct"))
)
display(
    features.groupBy("product_type_code").agg(
        F.count("*").alias("eligible_contracts"),
        F.round(F.avg("fpd5_flag") * 100, 2).alias("fpd5_rate_pct"),
    ).orderBy(F.desc("eligible_contracts"))
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Train an interpretable model with MLflow tracking (Run with me)
# MAGIC
# MAGIC We split **by time** on `origination_date` (train on older vintages, validate on the most recent) so the evaluation mirrors scoring future originations. MLflow autologging captures parameters, metrics, and the environment; we add the validation metrics explicitly.

# COMMAND ----------
import pandas as pd
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = [
    "applicant_age_years", "customer_tenure_days", "monthly_income_amount",
    "requested_amount", "requested_tenor_months", "declared_income_amount",
    "underwriting_score", "financed_amount", "loan_to_income", "is_zero_smartphone_promo",
]
CATEGORICAL = [
    "employment_type_code", "application_channel_code", "item_category_code",
    "product_type_code", "interest_method_code", "merchant_type_code", "store_region_code",
]
LABEL = "fpd5_flag"

pdf = (
    features.select("contract_id", "origination_date", LABEL,
                    "promotion_cohort", "sales_associate_id", *NUMERIC, *CATEGORICAL)
    .toPandas()
)
pdf["origination_date"] = pd.to_datetime(pdf["origination_date"])
for col in CATEGORICAL:
    pdf[col] = pdf[col].astype("string").fillna("MISSING")

cutoff = pdf["origination_date"].quantile(0.8)  # ~80% oldest vintages train, newest 20% validate
train_mask = pdf["origination_date"] <= cutoff
X_cols = NUMERIC + CATEGORICAL
X_train, y_train = pdf.loc[train_mask, X_cols], pdf.loc[train_mask, LABEL]
X_valid, y_valid = pdf.loc[~train_mask, X_cols], pdf.loc[~train_mask, LABEL]
print(f"Time split at {cutoff}:  train={len(X_train):,}  validate={len(X_valid):,}")
print(f"FPD5 base rate — train {y_train.mean():.3f} | validate {y_valid.mean():.3f}")

pre = ColumnTransformer(
    [
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="constant", fill_value="MISSING")),
                          ("ohe", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL),
    ]
)
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
    signature = infer_signature(X_valid, pipe.predict(X_valid))  # UC requires a signature
    mlflow.sklearn.log_model(
        pipe, artifact_path="model", serialization_format="cloudpickle", signature=signature
    )
    run_id = run.info.run_id

print(f"Validation ROC-AUC: {val_auc:.3f}  |  PR-AUC: {val_pr:.3f}  (base rate {y_valid.mean():.3f})")

# COMMAND ----------
# MAGIC %md
# MAGIC ### Validation-set quality (out-of-sample)
# MAGIC
# MAGIC Calibration and rank-ordering are measured only on the held-out recent vintages, so they reflect how the model scores originations it did not train on.

# COMMAND ----------
val_eval = pdf.loc[~train_mask, [LABEL, "is_zero_smartphone_promo"]].copy()
val_eval["predicted_risk"] = valid_proba
val_eval["cohort"] = val_eval["is_zero_smartphone_promo"].map(
    {1: "0% smartphone promotion", 0: "Other eligible originations"}
)
val_eval["risk_decile"] = pd.qcut(val_eval["predicted_risk"].rank(method="first"), 10, labels=False) + 1

calibration = (
    val_eval.groupby("cohort").agg(
        contracts=(LABEL, "size"),
        avg_predicted_pct=("predicted_risk", lambda s: round(float(s.mean()) * 100, 2)),
        actual_fpd5_pct=(LABEL, lambda s: round(float(s.mean()) * 100, 2)),
    ).reset_index()
)
decile_lift = (
    val_eval[val_eval["risk_decile"].isin([1, 10])].groupby("risk_decile").agg(
        contracts=(LABEL, "size"),
        actual_fpd5_pct=(LABEL, lambda s: round(float(s.mean()) * 100, 2)),
    ).reset_index()
)
with mlflow.start_run(run_id=run_id):  # track validation quality on the same run
    for _, r in calibration.iterrows():
        tag = "promo" if r["cohort"].startswith("0%") else "other"
        mlflow.log_metric(f"val_{tag}_predicted_pct", float(r["avg_predicted_pct"]))
        mlflow.log_metric(f"val_{tag}_actual_pct", float(r["actual_fpd5_pct"]))
    _dec = decile_lift.set_index("risk_decile")["actual_fpd5_pct"].to_dict()
    mlflow.log_metric("val_decile10_actual_pct", float(_dec.get(10, 0.0)))
    mlflow.log_metric("val_decile1_actual_pct", float(_dec.get(1, 0.0)))

print("Validation calibration by cohort (predicted vs actual):")
display(spark.createDataFrame(calibration))
print("Validation rank-ordering — decile 1 = lowest predicted risk, 10 = highest:")
display(spark.createDataFrame(decile_lift))

# COMMAND ----------
# MAGIC %md
# MAGIC ### Interpretability — top risk drivers
# MAGIC
# MAGIC Logistic-regression coefficients are the model's reason codes. Positive values push FPD5 risk up.

# COMMAND ----------
feat_names = pipe.named_steps["prep"].get_feature_names_out()
coefs = pipe.named_steps["clf"].coef_[0]
drivers = (
    spark.createDataFrame(
        [(n.split("__", 1)[-1], float(c)) for n, c in zip(feat_names, coefs)],
        ["feature", "coefficient"],
    )
    .withColumn("direction", F.when(F.col("coefficient") > 0, "raises FPD5 risk").otherwise("lowers FPD5 risk"))
    .orderBy(F.desc(F.abs(F.col("coefficient"))))
    .limit(12)
)
display(drivers)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Register the model in Unity Catalog (Run with me)
# MAGIC
# MAGIC Registering in UC gives the model a governed three-level name, versions, aliases, and lineage back to the run and source tables. We promote this version to the `champion` alias.

# COMMAND ----------
version = mlflow.register_model(f"runs:/{run_id}/model", MODEL_NAME).version
client = MlflowClient()
client.set_registered_model_alias(MODEL_NAME, "champion", version)
client.set_model_version_tag(MODEL_NAME, version, "val_roc_auc", f"{val_auc:.3f}")

print(f"Registered {MODEL_NAME} version {version} and set alias @champion")
display(
    spark.createDataFrame(
        [(MODEL_NAME, str(version), "champion", f"{val_auc:.3f}")],
        ["registered_model", "version", "alias", "val_roc_auc"],
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Batch score the eligible population (Run with me — required path)
# MAGIC
# MAGIC Batch scoring is the required productionisation path for this workshop. Model quality was measured on the held-out validation vintages above; here we load the `@champion` model by alias and score **every** eligible contract to build the operational review queue, writing to a per-user Delta table in `workshop_labs`. The output is overwritten on rerun.

# COMMAND ----------
RISK_THRESHOLD = 0.35  # tunable review operating point; ~1.65x the base rate in precision

champion = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}@champion")
scores_pdf = pdf[
    ["contract_id", LABEL, "promotion_cohort", "product_type_code", "store_region_code", "sales_associate_id"]
].copy()
scores_pdf["fpd5_risk"] = champion.predict_proba(pdf[X_cols])[:, 1]
scores_pdf["fpd5_risk_flag"] = (scores_pdf["fpd5_risk"] >= RISK_THRESHOLD).astype(int)
scores_pdf = scores_pdf.rename(columns={LABEL: "fpd5_actual"})
for _c in ["promotion_cohort", "product_type_code", "store_region_code", "sales_associate_id"]:
    scores_pdf[_c] = scores_pdf[_c].astype(str)

scores_sdf = (
    spark.createDataFrame(scores_pdf)  # reuse pdf; no re-read of the feature-view join
    .withColumn("scored_at", F.current_timestamp())
    .withColumn("model_name", F.lit(MODEL_NAME))
    .withColumn("model_version", F.lit(str(version)))
)
(scores_sdf.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
    .saveAsTable(SCORES_FQ))
print(f"Wrote {scores_sdf.count():,} scored contracts to {SCORES_FQ}")

# The model, trained only on origination-time features, should still concentrate
# predicted risk in the promotion cohort — reconcile this with the analysis sections.
display(
    spark.table(SCORES_FQ).groupBy("promotion_cohort").agg(
        F.count("*").alias("contracts"),
        F.round(F.avg("fpd5_risk") * 100, 2).alias("avg_predicted_risk_pct"),
        F.round(F.avg("fpd5_actual") * 100, 2).alias("actual_fpd5_pct"),
        F.sum("fpd5_risk_flag").alias("flagged_high_risk"),
    ).orderBy(F.desc("avg_predicted_risk_pct"))
)

# Operating point: how big is the review queue and how precise is it?
total_scored = spark.table(SCORES_FQ).count()
flagged = spark.table(SCORES_FQ).where("fpd5_risk_flag = 1")
prec = flagged.agg(
    F.count("*").alias("n"),
    F.round(F.avg("fpd5_actual") * 100, 2).alias("precision_pct"),
).first()
print(
    f"At review threshold {RISK_THRESHOLD}: flagged {prec.n:,} of {total_scored:,} contracts "
    f"({prec.n / total_scored * 100:.1f}% of the book), precision {prec.precision_pct}%."
)

# COMMAND ----------
# MAGIC %md
# MAGIC ### Try it
# MAGIC
# MAGIC Complete `exercises.md` using the validation metrics, the risk drivers, and the batch-score cohort table. Your handover note must state the eligible-contract denominator and must not call the pattern confirmed fraud.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Operate the model after handover (Operate it)
# MAGIC
# MAGIC Inspect what the internal team now owns. In **Catalog Explorer → `{catalog}` → `workshop_labs` → Models**, open the registered model and confirm:
# MAGIC
# MAGIC - the `champion` alias points at the version you registered;
# MAGIC - **Lineage** links the version to its MLflow run and the `core_lending` source tables;
# MAGIC - the scores table `unicorn_<user_id>_fpd_scores` carries `model_name` and `model_version` for traceability.
# MAGIC
# MAGIC Rerunning trains a new version; promoting it is a one-line alias move, and rollback is the same move back. Model Serving (a REST endpoint) is **optional** for this workshop; batch scoring above is the required path.

# COMMAND ----------
print("MLflow run id:", run_id)
print("Registered model:", MODEL_NAME, "| champion version:", version)
display(
    spark.sql(f"DESCRIBE HISTORY {LABS_SQL}.`{SCORES_TABLE}`")
    .select("version", "timestamp", "operation")
    .orderBy(F.desc("version")).limit(3)
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Checkpoint
# MAGIC
# MAGIC Be ready to answer:
# MAGIC
# MAGIC - Which features are allowed for an origination-time model, and which tables are forbidden as leakage?
# MAGIC - Why did we split by `origination_date` instead of randomly?
# MAGIC - Where does MLflow record parameters and metrics, and where does Unity Catalog record versions, aliases, and lineage?
# MAGIC - How do you promote a new champion and how do you roll back?
# MAGIC - Which is the required inference path here, and when would serving be justified?
# MAGIC - Why is a high predicted-risk store or associate still only an investigation signal?
# MAGIC
# MAGIC Leave `{catalog}.workshop_labs.unicorn_<user_id>_fpd` and its scores table in place for the handover review. The facilitator can remove the per-user lab assets after the workshop.
