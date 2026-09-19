# Databricks notebook source
# DBTITLE 1,Install mlflow and scikit-learn
# MAGIC %pip install mlflow scikit-learn -q

# COMMAND ----------

# DBTITLE 1,Configuration and setup
import re, mlflow

# ── catalog ──────────────────────────────────────────────────────────
catalog = "hc_workshop"
try:
    spark.sql(f"USE CATALOG `{catalog}`")
    print(f"✔ Catalog '{catalog}' is valid and accessible.")
except Exception as e:
    raise RuntimeError(f"Cannot access catalog '{catalog}': {e}")

# ── source as-of date ────────────────────────────────────────────────
source_asof_date = "2026-09-01"
print(f"✔ Source as-of date: {source_asof_date}")

# ── user_id from email local-part ────────────────────────────────────
raw_email  = spark.sql("SELECT current_user()").first()[0]
local_part = raw_email.split("@")[0].lower()
user_id    = re.sub(r"[^a-z0-9]", "_", local_part)
print(f"✔ User ID: {user_id}  (email: {raw_email})")

# ── derived names (unicorn__fpd pattern) ─────────────────────────────
schema         = user_id
feature_view   = f"{catalog}.{schema}.unicorn__fpd_features"
model_name     = f"{catalog}.{schema}.unicorn__fpd_model"
scores_table   = f"{catalog}.{schema}.unicorn__fpd_scores"

print(f"\n── Derived Names ──")
print(f"  Feature view : {feature_view}")
print(f"  UC model     : {model_name}")
print(f"  Scores table : {scores_table}")

# ── register models in Unity Catalog ─────────────────────────────────
mlflow.set_registry_uri("databricks-uc")
print(f"\n✔ MLflow registry set to Unity Catalog.")

# COMMAND ----------

# DBTITLE 1,Validate core_lending tables
# Re-derive catalog in case kernel state was lost after %pip restart
try:
    catalog
except NameError:
    import re, mlflow
    catalog = "hc_workshop"
    spark.sql(f"USE CATALOG `{catalog}`")
    source_asof_date = "2026-09-01"
    raw_email  = spark.sql("SELECT current_user()").first()[0]
    local_part = raw_email.split("@")[0].lower()
    user_id    = re.sub(r"[^a-z0-9]", "_", local_part)
    schema         = user_id
    feature_view   = f"{catalog}.{schema}.unicorn__fpd_features"
    model_name     = f"{catalog}.{schema}.unicorn__fpd_model"
    scores_table   = f"{catalog}.{schema}.unicorn__fpd_scores"
    mlflow.set_registry_uri("databricks-uc")
    print("(Restored config after kernel restart)")

EXPECTED_TABLES = {
    "collection_action",
    "credit_contract",
    "customer",
    "installment",
    "loan_application",
    "loan_product",
    "payment",
    "retail_location",
}

query = (
    f"SELECT table_name FROM `{catalog}`.information_schema.tables "
    f"WHERE table_schema = 'core_lending'"
)
rows = spark.sql(query).collect()
existing = {row.table_name for row in rows}

missing = EXPECTED_TABLES - existing
if missing:
    raise RuntimeError(
        f"Missing core_lending table(s): {', '.join(sorted(missing))}"
    )

print(f"✔ All {len(EXPECTED_TABLES)} core_lending tables verified:")
for t in sorted(EXPECTED_TABLES):
    print(f"  • {catalog}.core_lending.{t}")

# COMMAND ----------

# DBTITLE 1,Build FPD5-labeled origination dataset
# restore config if kernel was restarted
try:
    catalog
except NameError:
    import re, mlflow
    catalog = "hc_workshop"
    spark.sql(f"USE CATALOG `{catalog}`")
    source_asof_date = "2026-09-01"
    raw_email  = spark.sql("SELECT current_user()").first()[0]
    user_id    = re.sub(r"[^a-z0-9]", "_", raw_email.split("@")[0].lower())
    schema = user_id
    feature_view = f"{catalog}.{schema}.unicorn__fpd_features"
    model_name   = f"{catalog}.{schema}.unicorn__fpd_model"
    scores_table = f"{catalog}.{schema}.unicorn__fpd_scores"
    mlflow.set_registry_uri("databricks-uc")
    print("(Restored config)")

from pyspark.sql import functions as F

SOURCE = f"{catalog}.core_lending"
ASOF   = source_asof_date  # "2026-09-01"

# ── 1. first installment per contract (for label only) ──────────────
first_inst = (
    spark.table(f"{SOURCE}.installment")
    .filter(F.col("installment_no") == 1)
    .filter(F.date_add(F.col("due_date"), 5) <= F.lit(ASOF).cast("date"))
    .select(
        "contract_id",
        F.when(
            F.col("settled_date").isNull() | (F.col("settled_date") >= F.date_add(F.col("due_date"), 5)),
            F.lit(1)
        ).otherwise(F.lit(0)).alias("fpd5"),
    )
)

# ── 2. fixed-term contracts only ────────────────────────────────────
contract = spark.table(f"{SOURCE}.credit_contract").select(
    "contract_id", "application_id", "principal_amount",
    "tenor_months", "monthly_interest_rate_pct", "processing_fee_amount",
    "subsidy_amount", "origination_date",
)

application = spark.table(f"{SOURCE}.loan_application").select(
    "application_id", "customer_id", "product_id", "store_id",
    "application_channel_code", "requested_amount", "requested_tenor_months",
    "declared_income_amount", "underwriting_score", "promotion_code",
    "promotion_sponsor_type_code", "item_category_code", "item_brand_name",
    "financed_amount",
)

product = spark.table(f"{SOURCE}.loan_product").select(
    "product_id", "product_type_code", "product_name", "interest_method_code",
)

customer = spark.table(f"{SOURCE}.customer").select(
    "customer_id", "birth_date", "sex_code", "employment_type_code",
    "monthly_income_amount", "province", "city_municipality", "customer_since_date",
)

store = spark.table(f"{SOURCE}.retail_location").select(
    "store_id",
    F.col("merchant_type_code").alias("store_merchant_type_code"),
    F.col("region_code").alias("store_region_code"),
)

# ── 3. join everything ──────────────────────────────────────────────
df_fpd5 = (
    first_inst
    .join(contract, "contract_id")
    .join(application, "application_id")
    .join(product, "product_id")
    .join(customer, "customer_id")
    .join(store, "store_id")
    .filter(F.col("product_type_code").isin("POS_INSTALLMENT", "CASH_LOAN"))
)

# ── 4. derived origination-time features ────────────────────────────
df_fpd5 = df_fpd5.withColumns({
    "customer_age_at_origination": F.months_between(
        F.col("origination_date"), F.col("birth_date")
    ).cast("int") / 12,
    "customer_tenure_months": F.months_between(
        F.col("origination_date"), F.col("customer_since_date")
    ).cast("int"),
    "income_to_principal_ratio": F.col("monthly_income_amount") / F.col("principal_amount"),
    "has_promotion": F.when(F.col("promotion_code").isNotNull(), 1).otherwise(0),
    "promotion_cohort": F.coalesce(F.col("promotion_code"), F.lit("NO_PROMO")),
})

df_fpd5 = df_fpd5.drop(
    "application_id", "customer_id", "product_id", "store_id",
    "birth_date", "customer_since_date",
)

# ── 5. register temp view & assert grain ────────────────────────────
df_fpd5.createOrReplaceTempView("fpd5_dataset")

total    = df_fpd5.count()
distinct = df_fpd5.select("contract_id").distinct().count()
assert total == distinct, f"Grain violation: {total} rows but {distinct} distinct contracts"
print(f"✔ {total:,} rows, 1:1 with contract_id (grain OK)")
print(f"  FPD5 rate: {df_fpd5.agg(F.mean('fpd5')).first()[0]:.2%}")

# ── 6. FPD5 rate by promotion cohort ─────────────────────────────────
print("\n── FPD5 rate by promotion cohort ──")
display(
    df_fpd5.groupBy("promotion_cohort")
    .agg(
        F.count("*").alias("contracts"),
        F.sum("fpd5").alias("fpd5_count"),
        F.round(F.avg("fpd5") * 100, 2).alias("fpd5_rate_pct"),
    )
    .orderBy(F.desc("fpd5_rate_pct"))
)

# COMMAND ----------

# DBTITLE 1,Train LogisticRegression with MLflow
# restore config if kernel was restarted
try:
    catalog
except NameError:
    import re, mlflow
    catalog = "hc_workshop"
    spark.sql(f"USE CATALOG `{catalog}`")
    source_asof_date = "2026-09-01"
    raw_email  = spark.sql("SELECT current_user()").first()[0]
    user_id    = re.sub(r"[^a-z0-9]", "_", raw_email.split("@")[0].lower())
    schema = user_id
    feature_view = f"{catalog}.{schema}.unicorn__fpd_features"
    model_name   = f"{catalog}.{schema}.unicorn__fpd_model"
    scores_table = f"{catalog}.{schema}.unicorn__fpd_scores"
    mlflow.set_registry_uri("databricks-uc")
    print("(Restored config)")

import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from mlflow.models import infer_signature

# ── 1. pull to pandas (rebuild dataset if temp view was lost) ────────
try:
    pdf = spark.table("fpd5_dataset").toPandas()
except Exception:
    from pyspark.sql import functions as F
    SOURCE = f"{catalog}.core_lending"
    ASOF   = source_asof_date
    first_inst = (
        spark.table(f"{SOURCE}.installment")
        .filter(F.col("installment_no") == 1)
        .filter(F.date_add(F.col("due_date"), 5) <= F.lit(ASOF).cast("date"))
        .select("contract_id",
                F.when(F.col("settled_date").isNull() | (F.col("settled_date") >= F.date_add(F.col("due_date"), 5)), 1
                ).otherwise(0).alias("fpd5"))
    )
    contract = spark.table(f"{SOURCE}.credit_contract").select(
        "contract_id","application_id","principal_amount","tenor_months",
        "monthly_interest_rate_pct","processing_fee_amount","subsidy_amount","origination_date")
    application = spark.table(f"{SOURCE}.loan_application").select(
        "application_id","customer_id","product_id","store_id",
        "application_channel_code","requested_amount","requested_tenor_months",
        "declared_income_amount","underwriting_score","promotion_code",
        "promotion_sponsor_type_code","item_category_code","item_brand_name","financed_amount")
    product = spark.table(f"{SOURCE}.loan_product").select(
        "product_id","product_type_code","product_name","interest_method_code")
    customer = spark.table(f"{SOURCE}.customer").select(
        "customer_id","birth_date","sex_code","employment_type_code",
        "monthly_income_amount","province","city_municipality","customer_since_date")
    store = spark.table(f"{SOURCE}.retail_location").select(
        "store_id",F.col("merchant_type_code").alias("store_merchant_type_code"),
        F.col("region_code").alias("store_region_code"))
    df_fpd5 = (first_inst.join(contract,"contract_id").join(application,"application_id")
        .join(product,"product_id").join(customer,"customer_id").join(store,"store_id")
        .filter(F.col("product_type_code").isin("POS_INSTALLMENT","CASH_LOAN")))
    df_fpd5 = df_fpd5.withColumns({
        "customer_age_at_origination": F.months_between(F.col("origination_date"),F.col("birth_date")).cast("int")/12,
        "customer_tenure_months": F.months_between(F.col("origination_date"),F.col("customer_since_date")).cast("int"),
        "income_to_principal_ratio": F.col("monthly_income_amount")/F.col("principal_amount"),
        "has_promotion": F.when(F.col("promotion_code").isNotNull(),1).otherwise(0),
        "promotion_cohort": F.coalesce(F.col("promotion_code"),F.lit("NO_PROMO")),
    }).drop("application_id","customer_id","product_id","store_id","birth_date","customer_since_date")
    df_fpd5.createOrReplaceTempView("fpd5_dataset")
    pdf = df_fpd5.toPandas()
    print("(Rebuilt fpd5_dataset from source tables)")

# coerce Decimal → float64
for c in pdf.select_dtypes(include=["object"]).columns:
    pdf[c] = pd.to_numeric(pdf[c], errors="ignore")
for c in pdf.columns:
    if "decimal" in str(pdf[c].dtype).lower():
        pdf[c] = pdf[c].astype("float64")

# ── 2. temporal split at 80th-percentile origination_date ────────────
cutoff = pdf["origination_date"].quantile(0.8)
print(f"Split cutoff (80th pctl): {cutoff}  "
      f"(train ≤ cutoff: {(pdf['origination_date'] <= cutoff).sum():,}, "
      f"val > cutoff: {(pdf['origination_date'] > cutoff).sum():,})")

train_mask = pdf["origination_date"] <= cutoff
val_mask   = ~train_mask

# ── 3. define feature columns ────────────────────────────────────────
drop_cols = {"contract_id", "fpd5", "origination_date", "promotion_code"}
feature_cols = [c for c in pdf.columns if c not in drop_cols]

numeric_cols = [c for c in feature_cols if pd.api.types.is_numeric_dtype(pdf[c])]
categorical_cols = [c for c in feature_cols if c not in numeric_cols]

print(f"Features: {len(feature_cols)} total  "
      f"({len(numeric_cols)} numeric, {len(categorical_cols)} categorical)")

X_train, y_train = pdf.loc[train_mask, feature_cols], pdf.loc[train_mask, "fpd5"]
X_val,   y_val   = pdf.loc[val_mask,   feature_cols], pdf.loc[val_mask,   "fpd5"]

# ── 4. sklearn pipeline ──────────────────────────────────────────────
numeric_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale",  StandardScaler()),
])

categorical_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
    ("ohe",    OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
])

preprocessor = ColumnTransformer([
    ("num", numeric_pipe,      numeric_cols),
    ("cat", categorical_pipe,  categorical_cols),
])

pipe = Pipeline([
    ("pre",   preprocessor),
    ("model", LogisticRegression(max_iter=1000)),
])

# ── 5. MLflow: autolog (no model) + manual run ───────────────────────
mlflow.sklearn.autolog(log_models=False)

with mlflow.start_run(run_name="fpd5_logistic_regression") as run:
    pipe.fit(X_train, y_train)

    # validation predictions
    y_prob = pipe.predict_proba(X_val)[:, 1]
    roc_auc = roc_auc_score(y_val, y_prob)
    pr_auc  = average_precision_score(y_val, y_prob)

    mlflow.log_metric("val_roc_auc", roc_auc)
    mlflow.log_metric("val_pr_auc",  pr_auc)
    mlflow.log_param("split_cutoff_date", str(cutoff))

    # signature on raw features
    signature = infer_signature(X_train.head(100), pipe.predict(X_train.head(100)))

    # log model with cloudpickle serialisation
    model_info = mlflow.sklearn.log_model(
        pipe,
        name="model",
        signature=signature,
        input_example=X_train.head(3),
        serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE,
    )

    print(f"\n── Results ──")
    print(f"  Val ROC-AUC : {roc_auc:.4f}")
    print(f"  Val PR-AUC  : {pr_auc:.4f}")
    print(f"  Run ID      : {run.info.run_id}")
    print(f"  Model URI   : {model_info.model_uri}")

# COMMAND ----------

# DBTITLE 1,Validation diagnostics and log to MLflow run
# Reconstruct training artifacts if kernel state was lost
try:
    X_val, y_val, y_prob, run
except NameError:
    import re, mlflow, mlflow.sklearn, numpy as np, pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, average_precision_score
    from sklearn.pipeline import Pipeline as SKPipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from pyspark.sql import functions as F

    catalog = "hc_workshop"
    spark.sql(f"USE CATALOG `{catalog}`")
    source_asof_date = "2026-09-01"
    raw_email = spark.sql("SELECT current_user()").first()[0]
    user_id = re.sub(r"[^a-z0-9]", "_", raw_email.split("@")[0].lower())
    schema = user_id
    model_name = f"{catalog}.{schema}.unicorn__fpd_model"
    mlflow.set_registry_uri("databricks-uc")

    SOURCE = f"{catalog}.core_lending"
    ASOF = source_asof_date
    first_inst = (spark.table(f"{SOURCE}.installment")
        .filter(F.col("installment_no") == 1)
        .filter(F.date_add(F.col("due_date"), 5) <= F.lit(ASOF).cast("date"))
        .select("contract_id", F.when(F.col("settled_date").isNull() | (F.col("settled_date") >= F.date_add(F.col("due_date"), 5)), 1).otherwise(0).alias("fpd5")))
    contract = spark.table(f"{SOURCE}.credit_contract").select("contract_id","application_id","principal_amount","tenor_months","monthly_interest_rate_pct","processing_fee_amount","subsidy_amount","origination_date")
    application = spark.table(f"{SOURCE}.loan_application").select("application_id","customer_id","product_id","store_id","application_channel_code","requested_amount","requested_tenor_months","declared_income_amount","underwriting_score","promotion_code","promotion_sponsor_type_code","item_category_code","item_brand_name","financed_amount")
    product = spark.table(f"{SOURCE}.loan_product").select("product_id","product_type_code","product_name","interest_method_code")
    customer = spark.table(f"{SOURCE}.customer").select("customer_id","birth_date","sex_code","employment_type_code","monthly_income_amount","province","city_municipality","customer_since_date")
    store = spark.table(f"{SOURCE}.retail_location").select("store_id",F.col("merchant_type_code").alias("store_merchant_type_code"),F.col("region_code").alias("store_region_code"))
    df_fpd5 = (first_inst.join(contract,"contract_id").join(application,"application_id").join(product,"product_id").join(customer,"customer_id").join(store,"store_id").filter(F.col("product_type_code").isin("POS_INSTALLMENT","CASH_LOAN")))
    df_fpd5 = df_fpd5.withColumns({"customer_age_at_origination":F.months_between(F.col("origination_date"),F.col("birth_date")).cast("int")/12,"customer_tenure_months":F.months_between(F.col("origination_date"),F.col("customer_since_date")).cast("int"),"income_to_principal_ratio":F.col("monthly_income_amount")/F.col("principal_amount"),"has_promotion":F.when(F.col("promotion_code").isNotNull(),1).otherwise(0),"promotion_cohort":F.coalesce(F.col("promotion_code"),F.lit("NO_PROMO"))})
    df_fpd5 = df_fpd5.drop("application_id","customer_id","product_id","store_id","birth_date","customer_since_date")
    pdf = df_fpd5.toPandas()
    for c in pdf.select_dtypes(include=["object"]).columns:
        pdf[c] = pd.to_numeric(pdf[c], errors="ignore")
    for c in pdf.columns:
        if "decimal" in str(pdf[c].dtype).lower():
            pdf[c] = pdf[c].astype("float64")
    cutoff = pdf["origination_date"].quantile(0.8)
    train_mask = pdf["origination_date"] <= cutoff
    drop_cols = {"contract_id","fpd5","origination_date","promotion_code"}
    feature_cols = [c for c in pdf.columns if c not in drop_cols]
    numeric_cols = [c for c in feature_cols if pd.api.types.is_numeric_dtype(pdf[c])]
    categorical_cols = [c for c in feature_cols if c not in numeric_cols]
    X_train = pdf.loc[train_mask, feature_cols]; y_train = pdf.loc[train_mask, "fpd5"]
    X_val = pdf.loc[~train_mask, feature_cols]; y_val = pdf.loc[~train_mask, "fpd5"]
    numeric_pipe = SKPipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())])
    categorical_pipe = SKPipeline([("impute",SimpleImputer(strategy="constant",fill_value="__MISSING__")),("ohe",OneHotEncoder(handle_unknown="ignore",sparse_output=True))])
    preprocessor = ColumnTransformer([("num",numeric_pipe,numeric_cols),("cat",categorical_pipe,categorical_cols)])
    pipe = SKPipeline([("pre",preprocessor),("model",LogisticRegression(max_iter=1000))])
    mlflow.sklearn.autolog(log_models=False)
    with mlflow.start_run(run_name="fpd5_logistic_regression") as run:
        pipe.fit(X_train, y_train)
        y_prob = pipe.predict_proba(X_val)[:, 1]
        roc_auc = roc_auc_score(y_val, y_prob)
        pr_auc = average_precision_score(y_val, y_prob)
        mlflow.log_metric("val_roc_auc", roc_auc)
        mlflow.log_metric("val_pr_auc", pr_auc)
        mlflow.log_param("split_cutoff_date", str(cutoff))
        from mlflow.models import infer_signature
        signature = infer_signature(X_train.head(100), pipe.predict(X_train.head(100)))
        model_info = mlflow.sklearn.log_model(pipe, name="model", signature=signature, input_example=X_train.head(3), serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE)
    print(f"(Rebuilt model — run {run.info.run_id}, ROC-AUC {roc_auc:.4f})")

# ── 1. predicted-vs-actual FPD5 by promotion cohort ───────────────────
val_df = X_val.copy()
val_df["fpd5_actual"]    = y_val.values
val_df["fpd5_predicted"] = y_prob

cohort_stats = (
    val_df.groupby("promotion_cohort")
    .agg(
        n            = ("fpd5_actual", "size"),
        actual_rate  = ("fpd5_actual", "mean"),
        pred_rate    = ("fpd5_predicted", "mean"),
    )
    .reset_index()
)
cohort_stats["abs_diff"] = (cohort_stats["pred_rate"] - cohort_stats["actual_rate"]).abs()
print("Predicted vs Actual FPD5 by cohort (validation set):")
print(cohort_stats.to_string(index=False, float_format="{:.4f}".format))

# ── 2. actual FPD5 rate in top / bottom predicted-risk deciles ───────
val_df["decile"] = pd.qcut(val_df["fpd5_predicted"], 10, labels=False, duplicates="drop") + 1
top_decile_rate    = val_df.loc[val_df["decile"] == val_df["decile"].max(), "fpd5_actual"].mean()
bottom_decile_rate = val_df.loc[val_df["decile"] == 1, "fpd5_actual"].mean()

print(f"\nTop predicted-risk decile  → actual FPD5 rate: {top_decile_rate:.4f}")
print(f"Bottom predicted-risk decile → actual FPD5 rate: {bottom_decile_rate:.4f}")
print(f"Lift (top / bottom): {top_decile_rate / bottom_decile_rate:.2f}x")

# ── 3. log everything to the existing MLflow run ────────────────────
with mlflow.start_run(run_id=run.info.run_id):
    for _, row in cohort_stats.iterrows():
        tag = row["promotion_cohort"].lower()
        mlflow.log_metric(f"val_actual_fpd5_{tag}",    row["actual_rate"])
        mlflow.log_metric(f"val_predicted_fpd5_{tag}", row["pred_rate"])

    mlflow.log_metric("val_fpd5_top_decile",    top_decile_rate)
    mlflow.log_metric("val_fpd5_bottom_decile", bottom_decile_rate)
    mlflow.log_metric("val_fpd5_decile_lift",   top_decile_rate / bottom_decile_rate)

print(f"\n✔ Metrics logged to run {run.info.run_id}")

# COMMAND ----------

# DBTITLE 1,Top 12 coefficient reason codes
import numpy as np

# Reconstruct pipeline if kernel state was lost
try:
    pipe
except NameError:
    import re, pandas as pd, mlflow, mlflow.sklearn
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline as SKPipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from pyspark.sql import functions as F

    catalog = "hc_workshop"
    spark.sql(f"USE CATALOG `{catalog}`")
    SOURCE = f"{catalog}.core_lending"
    ASOF = "2026-09-01"
    first_inst = (spark.table(f"{SOURCE}.installment").filter(F.col("installment_no") == 1)
        .filter(F.date_add(F.col("due_date"), 5) <= F.lit(ASOF).cast("date"))
        .select("contract_id", F.when(F.col("settled_date").isNull() | (F.col("settled_date") >= F.date_add(F.col("due_date"), 5)), 1).otherwise(0).alias("fpd5")))
    contract = spark.table(f"{SOURCE}.credit_contract").select("contract_id","application_id","principal_amount","tenor_months","monthly_interest_rate_pct","processing_fee_amount","subsidy_amount","origination_date")
    application = spark.table(f"{SOURCE}.loan_application").select("application_id","customer_id","product_id","store_id","application_channel_code","requested_amount","requested_tenor_months","declared_income_amount","underwriting_score","promotion_code","promotion_sponsor_type_code","item_category_code","item_brand_name","financed_amount")
    product = spark.table(f"{SOURCE}.loan_product").select("product_id","product_type_code","product_name","interest_method_code")
    customer = spark.table(f"{SOURCE}.customer").select("customer_id","birth_date","sex_code","employment_type_code","monthly_income_amount","province","city_municipality","customer_since_date")
    store = spark.table(f"{SOURCE}.retail_location").select("store_id",F.col("merchant_type_code").alias("store_merchant_type_code"),F.col("region_code").alias("store_region_code"))
    df_fpd5 = (first_inst.join(contract,"contract_id").join(application,"application_id").join(product,"product_id").join(customer,"customer_id").join(store,"store_id").filter(F.col("product_type_code").isin("POS_INSTALLMENT","CASH_LOAN")))
    df_fpd5 = df_fpd5.withColumns({"customer_age_at_origination":F.months_between(F.col("origination_date"),F.col("birth_date")).cast("int")/12,"customer_tenure_months":F.months_between(F.col("origination_date"),F.col("customer_since_date")).cast("int"),"income_to_principal_ratio":F.col("monthly_income_amount")/F.col("principal_amount"),"has_promotion":F.when(F.col("promotion_code").isNotNull(),1).otherwise(0),"promotion_cohort":F.coalesce(F.col("promotion_code"),F.lit("NO_PROMO"))})
    df_fpd5 = df_fpd5.drop("application_id","customer_id","product_id","store_id","birth_date","customer_since_date")
    pdf = df_fpd5.toPandas()
    for c in pdf.select_dtypes(include=["object"]).columns:
        pdf[c] = pd.to_numeric(pdf[c], errors="ignore")
    for c in pdf.columns:
        if "decimal" in str(pdf[c].dtype).lower():
            pdf[c] = pdf[c].astype("float64")
    cutoff = pdf["origination_date"].quantile(0.8)
    drop_cols = {"contract_id","fpd5","origination_date","promotion_code"}
    feature_cols = [c for c in pdf.columns if c not in drop_cols]
    numeric_cols = [c for c in feature_cols if pd.api.types.is_numeric_dtype(pdf[c])]
    categorical_cols = [c for c in feature_cols if c not in numeric_cols]
    X_train = pdf.loc[pdf["origination_date"] <= cutoff, feature_cols]
    y_train = pdf.loc[pdf["origination_date"] <= cutoff, "fpd5"]
    numeric_pipe = SKPipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())])
    categorical_pipe = SKPipeline([("impute",SimpleImputer(strategy="constant",fill_value="__MISSING__")),("ohe",OneHotEncoder(handle_unknown="ignore",sparse_output=True))])
    preprocessor = ColumnTransformer([("num",numeric_pipe,numeric_cols),("cat",categorical_pipe,categorical_cols)])
    pipe = SKPipeline([("pre",preprocessor),("model",LogisticRegression(max_iter=1000))])
    pipe.fit(X_train, y_train)
    print("(Rebuilt pipeline for coefficient extraction)")

feat_names = pipe.named_steps["pre"].get_feature_names_out()
coefs      = pipe.named_steps["model"].coef_[0]

reason_codes = (
    pd.DataFrame({"feature": feat_names, "coefficient": coefs})
    .assign(
        feature=lambda d: d["feature"].str.replace(r"^(num|cat)__", "", regex=True),
        abs_coef=lambda d: d["coefficient"].abs(),
        direction=lambda d: np.where(d["coefficient"] > 0, "raises FPD5 risk", "lowers FPD5 risk"),
    )
    .nlargest(12, "abs_coef")
    .drop(columns="abs_coef")
    .reset_index(drop=True)
)

print("Top 12 logistic-regression reason codes (by |coefficient|):\n")
print(reason_codes.to_string(index=False, float_format="{:+.4f}".format))

# COMMAND ----------

# DBTITLE 1,Register model in Unity Catalog
# Reconstruct state if kernel was restarted
try:
    model_name, model_info, roc_auc, run
except NameError:
    import re, pandas as pd, mlflow, mlflow.sklearn, numpy as np
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, average_precision_score
    from sklearn.pipeline import Pipeline as SKPipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from mlflow.models import infer_signature
    from pyspark.sql import functions as F

    catalog = "hc_workshop"
    spark.sql(f"USE CATALOG `{catalog}`")
    source_asof_date = "2026-09-01"
    raw_email = spark.sql("SELECT current_user()").first()[0]
    user_id = re.sub(r"[^a-z0-9]", "_", raw_email.split("@")[0].lower())
    schema = user_id
    model_name = f"{catalog}.{schema}.unicorn__fpd_model"
    scores_table = f"{catalog}.{schema}.unicorn__fpd_scores"
    mlflow.set_registry_uri("databricks-uc")

    SOURCE = f"{catalog}.core_lending"
    ASOF = source_asof_date
    first_inst = (spark.table(f"{SOURCE}.installment").filter(F.col("installment_no") == 1)
        .filter(F.date_add(F.col("due_date"), 5) <= F.lit(ASOF).cast("date"))
        .select("contract_id", F.when(F.col("settled_date").isNull() | (F.col("settled_date") >= F.date_add(F.col("due_date"), 5)), 1).otherwise(0).alias("fpd5")))
    contract = spark.table(f"{SOURCE}.credit_contract").select("contract_id","application_id","principal_amount","tenor_months","monthly_interest_rate_pct","processing_fee_amount","subsidy_amount","origination_date")
    application = spark.table(f"{SOURCE}.loan_application").select("application_id","customer_id","product_id","store_id","application_channel_code","requested_amount","requested_tenor_months","declared_income_amount","underwriting_score","promotion_code","promotion_sponsor_type_code","item_category_code","item_brand_name","financed_amount")
    product = spark.table(f"{SOURCE}.loan_product").select("product_id","product_type_code","product_name","interest_method_code")
    customer = spark.table(f"{SOURCE}.customer").select("customer_id","birth_date","sex_code","employment_type_code","monthly_income_amount","province","city_municipality","customer_since_date")
    store = spark.table(f"{SOURCE}.retail_location").select("store_id",F.col("merchant_type_code").alias("store_merchant_type_code"),F.col("region_code").alias("store_region_code"))
    df_fpd5 = (first_inst.join(contract,"contract_id").join(application,"application_id").join(product,"product_id").join(customer,"customer_id").join(store,"store_id").filter(F.col("product_type_code").isin("POS_INSTALLMENT","CASH_LOAN")))
    df_fpd5 = df_fpd5.withColumns({"customer_age_at_origination":F.months_between(F.col("origination_date"),F.col("birth_date")).cast("int")/12,"customer_tenure_months":F.months_between(F.col("origination_date"),F.col("customer_since_date")).cast("int"),"income_to_principal_ratio":F.col("monthly_income_amount")/F.col("principal_amount"),"has_promotion":F.when(F.col("promotion_code").isNotNull(),1).otherwise(0),"promotion_cohort":F.coalesce(F.col("promotion_code"),F.lit("NO_PROMO"))})
    df_fpd5 = df_fpd5.drop("application_id","customer_id","product_id","store_id","birth_date","customer_since_date")
    pdf = df_fpd5.toPandas()
    for c in pdf.select_dtypes(include=["object"]).columns:
        pdf[c] = pd.to_numeric(pdf[c], errors="ignore")
    for c in pdf.columns:
        if "decimal" in str(pdf[c].dtype).lower():
            pdf[c] = pdf[c].astype("float64")
    cutoff = pdf["origination_date"].quantile(0.8)
    train_mask = pdf["origination_date"] <= cutoff
    drop_cols = {"contract_id","fpd5","origination_date","promotion_code"}
    feature_cols = [c for c in pdf.columns if c not in drop_cols]
    numeric_cols = [c for c in feature_cols if pd.api.types.is_numeric_dtype(pdf[c])]
    categorical_cols = [c for c in feature_cols if c not in numeric_cols]
    X_train = pdf.loc[train_mask, feature_cols]; y_train = pdf.loc[train_mask, "fpd5"]
    X_val = pdf.loc[~train_mask, feature_cols]; y_val = pdf.loc[~train_mask, "fpd5"]
    numeric_pipe = SKPipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())])
    categorical_pipe = SKPipeline([("impute",SimpleImputer(strategy="constant",fill_value="__MISSING__")),("ohe",OneHotEncoder(handle_unknown="ignore",sparse_output=True))])
    preprocessor = ColumnTransformer([("num",numeric_pipe,numeric_cols),("cat",categorical_pipe,categorical_cols)])
    pipe = SKPipeline([("pre",preprocessor),("model",LogisticRegression(max_iter=1000))])
    mlflow.sklearn.autolog(log_models=False)
    with mlflow.start_run(run_name="fpd5_logistic_regression") as run:
        pipe.fit(X_train, y_train)
        y_prob = pipe.predict_proba(X_val)[:, 1]
        roc_auc = roc_auc_score(y_val, y_prob)
        pr_auc = average_precision_score(y_val, y_prob)
        mlflow.log_metric("val_roc_auc", roc_auc)
        mlflow.log_metric("val_pr_auc", pr_auc)
        mlflow.log_param("split_cutoff_date", str(cutoff))
        signature = infer_signature(X_train.head(100), pipe.predict(X_train.head(100)))
        model_info = mlflow.sklearn.log_model(pipe, name="model", signature=signature,
            input_example=X_train.head(3), serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE)
    print(f"(Rebuilt model — run {run.info.run_id}, ROC-AUC {roc_auc:.4f})")

from mlflow import MlflowClient
mlflow.set_registry_uri("databricks-uc")

# ── 0. ensure target schema exists ──────────────────────────────────
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")

# ── 1. validate artifact ───────────────────────────────────────────
pyfunc_model = mlflow.pyfunc.load_model(model_info.model_uri)
assert pyfunc_model.metadata.signature is not None, "Model has no signature"
assert pyfunc_model.input_example is not None, "Model has no input example"
print(f"✔ Artifact validated: {model_info.model_uri}")

# ── 2. register under MODEL_NAME ─────────────────────────────────────
registered_version = mlflow.register_model(
    model_uri=model_info.model_uri,
    name=model_name,
    await_registration_for=300,
)
model_version = registered_version.version
print(f"✔ Registered as {model_name} version {model_version}")

# ── 3. set 'champion' alias ──────────────────────────────────────────
registry_client = MlflowClient(registry_uri="databricks-uc")
registry_client.set_registered_model_alias(
    name=model_name, alias="champion", version=model_version,
)
print(f"✔ Alias 'champion' → version {model_version}")

# ── 4. tag version with validation ROC-AUC ───────────────────────────
registry_client.set_model_version_tag(
    name=model_name, version=model_version,
    key="val_roc_auc", value=str(round(roc_auc, 4)),
)
print(f"✔ Tagged version {model_version} with val_roc_auc={roc_auc:.4f}")

# COMMAND ----------

# DBTITLE 1,Score champion model and write scores table
# Reconstruct config if kernel was restarted
try:
    catalog, schema, model_name, scores_table, source_asof_date
except NameError:
    import re, mlflow
    catalog = "hc_workshop"
    spark.sql(f"USE CATALOG `{catalog}`")
    source_asof_date = "2026-09-01"
    raw_email = spark.sql("SELECT current_user()").first()[0]
    user_id = re.sub(r"[^a-z0-9]", "_", raw_email.split("@")[0].lower())
    schema = user_id
    model_name = f"{catalog}.{schema}.unicorn__fpd_model"
    scores_table = f"{catalog}.{schema}.unicorn__fpd_scores"
    mlflow.set_registry_uri("databricks-uc")
    print("(Restored config)")

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from pyspark.sql import functions as F

threshold = 0.35
mlflow.set_registry_uri("databricks-uc")
registry_client = MlflowClient(registry_uri="databricks-uc")
champion_version = registry_client.get_model_version_by_alias(
    name=model_name,
    alias="champion",
)
model_version = champion_version.version
model_uri = f"models:/{model_name}@champion"
champion_model = mlflow.sklearn.load_model(model_uri)
print(f"✔ Loaded champion model: {model_uri} (version {model_version})")

# rebuild eligible scoring dataset if temp view was lost
try:
    score_pdf = spark.table("fpd5_dataset").toPandas()
    print("✔ Reused fpd5_dataset temp view")
except Exception:
    SOURCE = f"{catalog}.core_lending"
    ASOF = source_asof_date
    first_inst = (
        spark.table(f"{SOURCE}.installment")
        .filter(F.col("installment_no") == 1)
        .filter(F.date_add(F.col("due_date"), 5) <= F.lit(ASOF).cast("date"))
        .select(
            "contract_id",
            F.when(
                F.col("settled_date").isNull() | (F.col("settled_date") >= F.date_add(F.col("due_date"), 5)),
                1,
            ).otherwise(0).alias("fpd5"),
        )
    )
    contract = spark.table(f"{SOURCE}.credit_contract").select(
        "contract_id", "application_id", "principal_amount", "tenor_months",
        "monthly_interest_rate_pct", "processing_fee_amount", "subsidy_amount", "origination_date",
    )
    application = spark.table(f"{SOURCE}.loan_application").select(
        "application_id", "customer_id", "product_id", "store_id",
        "application_channel_code", "requested_amount", "requested_tenor_months",
        "declared_income_amount", "underwriting_score", "promotion_code",
        "promotion_sponsor_type_code", "item_category_code", "item_brand_name", "financed_amount",
    )
    product = spark.table(f"{SOURCE}.loan_product").select(
        "product_id", "product_type_code", "product_name", "interest_method_code",
    )
    customer = spark.table(f"{SOURCE}.customer").select(
        "customer_id", "birth_date", "sex_code", "employment_type_code",
        "monthly_income_amount", "province", "city_municipality", "customer_since_date",
    )
    store = spark.table(f"{SOURCE}.retail_location").select(
        "store_id",
        F.col("merchant_type_code").alias("store_merchant_type_code"),
        F.col("region_code").alias("store_region_code"),
    )

    df_fpd5 = (
        first_inst
        .join(contract, "contract_id")
        .join(application, "application_id")
        .join(product, "product_id")
        .join(customer, "customer_id")
        .join(store, "store_id")
        .filter(F.col("product_type_code").isin("POS_INSTALLMENT", "CASH_LOAN"))
    )

    df_fpd5 = df_fpd5.withColumns({
        "customer_age_at_origination": F.months_between(F.col("origination_date"), F.col("birth_date")).cast("int") / 12,
        "customer_tenure_months": F.months_between(F.col("origination_date"), F.col("customer_since_date")).cast("int"),
        "income_to_principal_ratio": F.col("monthly_income_amount") / F.col("principal_amount"),
        "has_promotion": F.when(F.col("promotion_code").isNotNull(), 1).otherwise(0),
        "promotion_cohort": F.coalesce(F.col("promotion_code"), F.lit("NO_PROMO")),
    }).drop(
        "application_id", "customer_id", "product_id", "store_id", "birth_date", "customer_since_date"
    )

    df_fpd5.createOrReplaceTempView("fpd5_dataset")
    score_pdf = df_fpd5.toPandas()
    print("✔ Rebuilt fpd5_dataset from source tables")

# convert decimal-like object columns consistently with training
for c in score_pdf.select_dtypes(include=["object"]).columns:
    score_pdf[c] = pd.to_numeric(score_pdf[c], errors="ignore")
for c in score_pdf.columns:
    if "decimal" in str(score_pdf[c].dtype).lower():
        score_pdf[c] = score_pdf[c].astype("float64")

feature_cols = [c for c in score_pdf.columns if c not in {"contract_id", "fpd5", "origination_date", "promotion_code"}]
score_features = score_pdf[feature_cols]
score_pdf["fpd5_predicted"] = champion_model.predict_proba(score_features)[:, 1]
score_pdf["risk_flag_035"] = (score_pdf["fpd5_predicted"] >= threshold).astype(int)
score_pdf["model_name"] = model_name
score_pdf["model_version"] = int(model_version)
score_pdf["threshold"] = threshold
score_pdf = score_pdf.rename(columns={"fpd5": "fpd5_actual"})

output_cols = [
    "contract_id", "origination_date", "promotion_cohort", "fpd5_actual", "fpd5_predicted",
    "risk_flag_035", "threshold", "model_name", "model_version",
]
score_output = score_pdf[output_cols].copy()
score_sdf = spark.createDataFrame(score_output)
score_sdf.write.format("delta").mode("overwrite").saveAsTable(scores_table)
print(f"✔ Wrote {len(score_output):,} scored contracts to {scores_table}")

cohort_stats = (
    score_output.groupby("promotion_cohort")
    .agg(
        n=("contract_id", "size"),
        actual_rate=("fpd5_actual", "mean"),
        pred_rate=("fpd5_predicted", "mean"),
    )
    .reset_index()
)
cohort_stats["abs_diff"] = (cohort_stats["pred_rate"] - cohort_stats["actual_rate"]).abs()

flagged = score_output.loc[score_output["risk_flag_035"] == 1].copy()
flagged_count = int(len(flagged))
flagged_precision = float(flagged["fpd5_actual"].mean()) if flagged_count > 0 else 0.0

print("\nPredicted vs Actual FPD5 by cohort (all eligible contracts):")
print(cohort_stats.to_string(index=False, float_format="{:.4f}".format))
print(f"\nThreshold {threshold:.2f} flagged {flagged_count:,} of {len(score_output):,} contracts ({flagged_count / len(score_output):.2%})")
print(f"Precision at threshold {threshold:.2f}: {flagged_precision:.4f}")

display(spark.createDataFrame(cohort_stats))
display(spark.createDataFrame(pd.DataFrame([{
    "threshold": threshold,
    "flagged_count": flagged_count,
    "total_contracts": int(len(score_output)),
    "flagged_share": flagged_count / len(score_output),
    "precision": flagged_precision,
}])))

# COMMAND ----------

# DBTITLE 1,Summary: run ID, model info, and Delta history
# Restore config if kernel was restarted
try:
    catalog, schema, model_name, scores_table
except NameError:
    import re, mlflow
    catalog = "hc_workshop"
    spark.sql(f"USE CATALOG `{catalog}`")
    raw_email = spark.sql("SELECT current_user()").first()[0]
    user_id = re.sub(r"[^a-z0-9]", "_", raw_email.split("@")[0].lower())
    schema = user_id
    model_name = f"{catalog}.{schema}.unicorn__fpd_model"
    scores_table = f"{catalog}.{schema}.unicorn__fpd_scores"
    mlflow.set_registry_uri("databricks-uc")
    print("(Restored config)")

import mlflow
from mlflow import MlflowClient

mlflow.set_registry_uri("databricks-uc")
client = MlflowClient(registry_uri="databricks-uc")

# ── champion version info ────────────────────────────────────────────
champion_mv = client.get_model_version_by_alias(name=model_name, alias="champion")
print(f"Model name      : {model_name}")
print(f"Champion version: {champion_mv.version}")
print(f"Run ID          : {champion_mv.run_id}")
print(f"Status          : {champion_mv.status}")
print(f"Tags            : {champion_mv.tags}")

# ── Delta history for scores table ───────────────────────────────────
print(f"\n── Delta history for {scores_table} ──")
parts = scores_table.split(".")
qualified = ".".join(f"`{p}`" for p in parts)
display(spark.sql(f"DESCRIBE HISTORY {qualified} LIMIT 5"))