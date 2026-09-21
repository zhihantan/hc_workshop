# Databricks notebook source
# MAGIC %md
# MAGIC # Unicorn Finance workshop — BUILD (consolidated, `hc_workshop`)
# MAGIC
# MAGIC **Canonical `hc_workshop` version of the `unicorn-workshop-build` job, as one self-contained notebook.** Run **after** the data-setup notebook. Steps:
# MAGIC
# MAGIC 1. **Section 01 analysis views** — `workshop_shared.fpd_analysis` + `fpd_metrics`.
# MAGIC 2. **Run the FPD5 medallion** — trigger the declarative pipeline (built from `participant-pipeline.sql`) via the SDK. A declarative pipeline cannot run as plain notebook cells, so set the `pipeline_id` widget.
# MAGIC 3. **Quality gate + run summary** — drop-rate gate; writes `fpd_run_summary`.
# MAGIC 4. **Train / register / batch-score** the interpretable FPD5 model in Unity Catalog.
# MAGIC
# MAGIC Runnable `sean_development_catalog` equivalent = the `unicorn-workshop-build` job + `instructor/` notebooks (workspace-only).

# COMMAND ----------

# MAGIC %pip install --quiet mlflow scikit-learn

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# Widgets for the build. `pipeline_id` is the FPD5 medallion pipeline created from
# workshop-content/03-data-engineering-in-databricks/participant-pipeline.sql
# (target catalog hc_workshop, target schema = the pipeline's own schema).
dbutils.widgets.text("pipeline_id", "", "FPD5 medallion pipeline id (create from participant-pipeline.sql)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Section 01 — governed analysis views

# COMMAND ----------

# Section 01 governed analysis views (fpd_analysis + the fpd_metrics Metric View).
spark.sql(r"""
CREATE OR REPLACE VIEW hc_workshop.workshop_shared.fpd_analysis
COMMENT 'One row per fixed-term contract whose first installment reached the FPD5 observation point by 2026-09-01. Synthetic workshop data only.'
AS
WITH first_installment AS (
  SELECT
    contract_id,
    due_date AS first_due_date,
    settled_date AS first_settled_date,
    CASE
      WHEN settled_date IS NULL
        OR settled_date >= date_add(due_date, 5)
      THEN 1
      ELSE 0
    END AS fpd5_flag
  FROM hc_workshop.core_lending.installment
  WHERE installment_no = 1
    AND date_add(due_date, 5) <= DATE'2026-09-01'
)
SELECT
  a.application_id,
  c.contract_id,
  CAST(a.submitted_at AS DATE) AS application_date,
  c.origination_date,
  p.product_name,
  p.product_type_code,
  a.application_channel_code,
  a.promotion_code,
  CASE
    WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026'
    THEN '0% smartphone promotion'
    ELSE 'Other eligible originations'
  END AS promotion_cohort,
  COALESCE(l.store_code, 'NO_STORE') AS store_code,
  COALESCE(l.store_name, 'No physical store') AS store_name,
  COALESCE(l.merchant_name, 'No physical merchant') AS merchant_name,
  COALESCE(l.province, 'NO_STORE') AS store_province,
  COALESCE(l.region_code, 'NO_STORE') AS region_code,
  COALESCE(a.sales_associate_id, 'NO_ASSOCIATE') AS sales_associate_id,
  c.principal_amount,
  f.first_due_date,
  f.first_settled_date,
  f.fpd5_flag
FROM hc_workshop.core_lending.credit_contract AS c
JOIN hc_workshop.core_lending.loan_application AS a
  ON c.application_id = a.application_id
JOIN hc_workshop.core_lending.loan_product AS p
  ON a.product_id = p.product_id
JOIN first_installment AS f
  ON c.contract_id = f.contract_id
LEFT JOIN hc_workshop.core_lending.retail_location AS l
  ON a.store_id = l.store_id
""")
spark.sql(r"""
CREATE OR REPLACE VIEW hc_workshop.workshop_shared.fpd_metrics
WITH METRICS
LANGUAGE YAML
AS $$
  version: 1.1
  source: hc_workshop.workshop_shared.fpd_analysis
  comment: "Governed first-payment-default metrics for eligible Unicorn Finance fixed-term contracts. FPD5 means the first installment was unsettled or settled on or after five days past due, observed through 2026-09-01."
  fields:
    - name: origination_date
      expr: origination_date
      comment: "Date on which the eligible credit contract originated."
      display_name: "Origination Date"
      synonyms: ["contract date", "booking date"]
      format:
        type: date
        date_format: year_month_day
    - name: origination_month
      expr: "CAST(DATE_TRUNC('MONTH', origination_date) AS DATE)"
      comment: "Calendar month in which the eligible credit contract originated."
      display_name: "Origination Month"
      synonyms: ["booking month", "vintage month"]
    - name: product_name
      expr: product_name
      comment: "Commercial name of the requested lending product."
      display_name: "Product"
      synonyms: ["loan product", "credit product"]
    - name: product_type
      expr: product_type_code
      comment: "Product family code for the eligible contract."
      display_name: "Product Type"
      synonyms: ["product family"]
    - name: application_channel
      expr: application_channel_code
      comment: "Channel through which the source application was submitted."
      display_name: "Application Channel"
      synonyms: ["origination channel", "channel"]
    - name: promotion_cohort
      expr: promotion_cohort
      comment: "Comparison cohort: 0% smartphone promotion or all other eligible originations."
      display_name: "Promotion Cohort"
      synonyms: ["promo cohort", "campaign cohort", "promotion"]
    - name: merchant_name
      expr: merchant_name
      comment: "Retail partner associated with the physical origination, or the no-store label."
      display_name: "Merchant"
      synonyms: ["retail partner", "merchant"]
    - name: store_code
      expr: store_code
      comment: "Stable code for the physical origination store, or NO_STORE."
      display_name: "Store Code"
      synonyms: ["location code"]
    - name: store_name
      expr: store_name
      comment: "Display name of the physical origination store."
      display_name: "Store"
      synonyms: ["retail location", "location"]
    - name: store_province
      expr: store_province
      comment: "Province of the physical origination store, or NO_STORE."
      display_name: "Store Province"
      synonyms: ["province", "location province"]
    - name: region_code
      expr: region_code
      comment: "Philippine administrative region code of the physical origination store."
      display_name: "Region"
      synonyms: ["store region", "administrative region"]
    - name: sales_associate_id
      expr: sales_associate_id
      comment: "Synthetic assisting sales-associate identifier. Treat as sensitive during governance exercises."
      display_name: "Sales Associate ID"
      synonyms: ["associate", "seller ID"]
    - name: first_due_date
      expr: first_due_date
      comment: "Due date of the first scheduled installment."
      display_name: "First Due Date"
      synonyms: ["first installment due date"]
      format:
        type: date
        date_format: year_month_day
  measures:
    - name: eligible_contracts
      expr: COUNT(1)
      comment: "Number of fixed-term contracts whose first installment reached the five-day observation point by 2026-09-01."
      display_name: "Eligible Contracts"
      synonyms: ["observed contracts", "FPD denominator"]
      format:
        type: number
        decimal_places:
          type: exact
          places: 0
        abbreviation: compact
    - name: fpd5_contracts
      expr: SUM(fpd5_flag)
      comment: "Number of eligible contracts that met the workshop FPD5 definition."
      display_name: "FPD5 Contracts"
      synonyms: ["first payment defaults", "five-day first payment defaults"]
      format:
        type: number
        decimal_places:
          type: exact
          places: 0
        abbreviation: compact
    - name: fpd5_rate
      expr: "MEASURE(`fpd5_contracts`) * 1.0 / NULLIF(MEASURE(`eligible_contracts`), 0)"
      comment: "FPD5 contracts divided by eligible contracts at the selected dimension grain."
      display_name: "FPD5 Rate"
      synonyms: ["first payment default rate", "FPD rate"]
      format:
        type: percentage
        decimal_places:
          type: exact
          places: 2
    - name: originated_principal
      expr: SUM(principal_amount)
      comment: "Total principal in Philippine pesos for eligible fixed-term contracts."
      display_name: "Originated Principal"
      synonyms: ["booked principal", "financed principal"]
      format:
        type: currency
        currency_code: PHP
        decimal_places:
          type: max
          places: 2
        abbreviation: compact
    - name: average_principal
      expr: AVG(principal_amount)
      comment: "Average principal in Philippine pesos per eligible fixed-term contract."
      display_name: "Average Principal"
      synonyms: ["average ticket", "average financed amount"]
      format:
        type: currency
        currency_code: PHP
        decimal_places:
          type: max
          places: 2
$$
""")
display(spark.sql("SELECT * FROM hc_workshop.workshop_shared.fpd_analysis LIMIT 5"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Run the FPD5 medallion pipeline (declarative; triggered via SDK)

# COMMAND ----------

import time
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
pid = dbutils.widgets.get("pipeline_id").strip()
if not pid:
    print("pipeline_id not set — create the FPD5 medallion pipeline from "
          "workshop-content/03-data-engineering-in-databricks/participant-pipeline.sql "
          "(serverless, target catalog hc_workshop), set the pipeline_id widget, and re-run this cell. "
          "Skipping the medallion run for now.")
else:
    upd = w.pipelines.start_update(pipeline_id=pid, full_refresh=True)
    print(f"Started pipeline update {upd.update_id} (full refresh)")
    TERMINAL = {"COMPLETED", "FAILED", "CANCELED"}
    while True:
        try:
            u = w.pipelines.get_update(pipeline_id=pid, update_id=upd.update_id)
            state = u.update.state.value if u.update and u.update.state else "?"
        except Exception as e:
            print("  (poll error — monitor in the Pipelines UI)", e); break
        print("  state:", state)
        if state in TERMINAL:
            if state != "COMPLETED":
                raise Exception(f"Medallion pipeline update ended {state}")
            break
        time.sleep(20)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Data-quality gate + run summary

# COMMAND ----------

# MAGIC %md
# MAGIC # Job task — data-quality gate + run summary (Section 03)
# MAGIC
# MAGIC The orchestrating Job runs this **after** the Lakeflow pipeline. It compares the pipeline's
# MAGIC bronze vs silver row counts and **fails the task** if the installment drop rate exceeds the
# MAGIC threshold — stopping a bad data day from silently propagating and firing the Job's failure
# MAGIC alert. On success it appends a **run-summary** row for observability.
# MAGIC
# MAGIC Parameterized by the pipeline target schema and the as-of date (set by the Job).

# COMMAND ----------
dbutils.widgets.text("schema", "de_<user_id>", "Pipeline target schema (e.g. de_jsmith; the Job overrides this)")
dbutils.widgets.text("as_of_date", "2026-09-01", "As-of date")
dbutils.widgets.text("max_drop_pct", "5.0", "Max allowed installment drop %")

CATALOG = "hc_workshop"
SCHEMA = dbutils.widgets.get("schema").strip()
AS_OF = dbutils.widgets.get("as_of_date").strip()
MAX_DROP = float(dbutils.widgets.get("max_drop_pct"))
S = f"`{CATALOG}`.`{SCHEMA}`"

# COMMAND ----------
bronze = spark.table(f"{S}.fpd_bronze_installment").count()
silver = spark.table(f"{S}.fpd_silver_installment").count()
drop_pct = 0.0 if bronze == 0 else round((bronze - silver) / bronze * 100, 2)
print(f"installments — bronze={bronze:,}  silver={silver:,}  dropped={drop_pct}%  (threshold {MAX_DROP}%)")

# COMMAND ----------
# Quality gate: fail the task (→ Job failure alert) if too many rows were dropped.
if drop_pct > MAX_DROP:
    raise Exception(
        f"DATA QUALITY GATE FAILED: installment drop {drop_pct}% exceeds the {MAX_DROP}% threshold. "
        "Downstream refresh is blocked; investigate the latest landing batch."
    )
print("Quality gate passed.")

# COMMAND ----------
# Publish a run-summary row (observability): eligible population, FPD5 rate, and quality counters.
from pyspark.sql import functions as F

gold = spark.table(f"{S}.fpd_origination")
summary = (
    gold.groupBy().agg(
        F.count("*").alias("eligible_contracts"),
        F.round(F.avg("fpd5_flag") * 100, 2).alias("fpd5_rate_pct"),
    )
    .withColumn("run_at", F.current_timestamp())
    .withColumn("as_of_date", F.lit(AS_OF))
    .withColumn("bronze_installments", F.lit(bronze))
    .withColumn("silver_installments", F.lit(silver))
    .withColumn("installment_drop_pct", F.lit(drop_pct))
)
(summary.write.format("delta").mode("append").option("mergeSchema", "true")
    .saveAsTable(f"{CATALOG}.{SCHEMA}.fpd_run_summary"))

display(
    spark.table(f"{CATALOG}.{SCHEMA}.fpd_run_summary").orderBy(F.desc("run_at")).limit(5)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Train, register, and batch-score the FPD5 model

# COMMAND ----------

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
import re
from datetime import date

import mlflow
from mlflow.tracking import MlflowClient
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "hc_workshop", "Workshop catalog")

CATALOG = dbutils.widgets.get("catalog").strip()

# Workshop catalog. A facilitator can point the lab at a different catalog
# by updating this constant (and the `catalog` widget above) and revalidating.
WORKSHOP_CATALOG = "hc_workshop"
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
