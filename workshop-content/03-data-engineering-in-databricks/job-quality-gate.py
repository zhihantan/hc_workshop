# Databricks notebook source
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
dbutils.widgets.text("schema", "de_zhihan_tan", "Pipeline target schema")
dbutils.widgets.text("as_of_date", "2026-09-01", "As-of date")
dbutils.widgets.text("max_drop_pct", "5.0", "Max allowed installment drop %")

CATALOG = "sean_development_catalog"
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
