# Databricks notebook source
# MAGIC %md
# MAGIC # Unicorn Finance workshop — DATA SETUP (consolidated, `hc_workshop`)
# MAGIC
# MAGIC **Canonical `hc_workshop` version of the `unicorn-workshop-data-setup` job, as one self-contained notebook.**
# MAGIC Runs the three data-provisioning steps end to end:
# MAGIC
# MAGIC 1. **Create schemas** — `core_lending`, `workshop_shared`, `workshop_labs`.
# MAGIC 2. **Generate the synthetic dataset** — deterministically build the eight `core_lending` tables.
# MAGIC 3. **Land the clean raw batch** — `workshop_shared.lending_raw_*` from `core_lending`.
# MAGIC
# MAGIC Prerequisite: the `hc_workshop` catalog must already exist (create it in Catalog Explorer with **Use default storage**).
# MAGIC The runnable `sean_development_catalog` equivalents live in the workspace-only `instructor/` folder + the `unicorn-workshop-data-setup` job.

# COMMAND ----------

# MAGIC %md
# MAGIC # Set up workshop Unity Catalog schemas
# MAGIC
# MAGIC Before running this notebook, create the `hc_workshop` catalog manually in
# MAGIC Catalog Explorer and select **Use default storage**. This notebook then provisions
# MAGIC the three schemas used throughout the workshop.
# MAGIC
# MAGIC ## Configuration
# MAGIC Edit the values in the next cell before selecting **Run all**. The settings are
# MAGIC visible in the notebook source and do not depend on widgets.

# COMMAND ----------

# ruff: noqa: F821
from __future__ import annotations

import re

# CONFIGURATION — edit these values before running the notebook.
CATALOG = "hc_workshop"
CORE_SCHEMA = "core_lending"
SHARED_SCHEMA = "workshop_shared"
LABS_SCHEMA = "workshop_labs"

# COMMAND ----------

IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

SCHEMAS = {
    CORE_SCHEMA: "Synthetic core lending source data; read-only for workshop participants",
    SHARED_SCHEMA: "Facilitator-managed trusted views and metrics for dashboards and Genie",
    LABS_SCHEMA: "Participant-owned workshop tables, views, and registered models with per-user prefixes",
}

for object_type, identifier in [
    ("catalog", CATALOG),
    ("core schema", CORE_SCHEMA),
    ("shared schema", SHARED_SCHEMA),
    ("labs schema", LABS_SCHEMA),
]:
    if not IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(f"Invalid {object_type} identifier: {identifier!r}")

if len(SCHEMAS) != 3:
    raise ValueError("CORE_SCHEMA, SHARED_SCHEMA, and LABS_SCHEMA must be distinct")


def quoted(identifier: str) -> str:
    return f"`{identifier}`"


catalog_sql = quoted(CATALOG)
catalog_exists = (
    spark.sql("SHOW CATALOGS")
    .filter(f"catalog = '{CATALOG}'")
    .limit(1)
    .count()
    > 0
)
if not catalog_exists:
    raise RuntimeError(
        f"Catalog {CATALOG!r} does not exist. Create it manually in Catalog Explorer "
        "using 'Use default storage', then rerun this notebook."
    )

for schema_name, description in SCHEMAS.items():
    namespace = f"{catalog_sql}.{quoted(schema_name)}"
    escaped_description = description.replace("'", "''")
    spark.sql(
        f"CREATE SCHEMA IF NOT EXISTS {namespace} "
        f"COMMENT '{escaped_description}'"
    )
    spark.sql(f"DESCRIBE SCHEMA {namespace}").collect()

spark.sql(f"USE CATALOG {catalog_sql}")
spark.sql(f"USE SCHEMA {quoted(CORE_SCHEMA)}")

display(
    spark.createDataFrame(
        [
            (CATALOG, schema_name, description, "READY")
            for schema_name, description in SCHEMAS.items()
        ],
        ["catalog", "schema", "purpose", "status"],
    )
)

print(
    "SUCCESS: workshop namespaces are ready: "
    + ", ".join(f"{CATALOG}.{schema_name}" for schema_name in SCHEMAS)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Generate the synthetic `core_lending` dataset
# MAGIC Deterministic (seeded) generation of the eight source tables; `WRITE_MODE='overwrite'` makes it a repeatable rebuild.

# COMMAND ----------

# MAGIC %md
# MAGIC # Unicorn Finance workshop dataset generator
# MAGIC
# MAGIC Run this notebook on Unity Catalog-enabled Databricks compute. It provisions
# MAGIC `hc_workshop.core_lending` by default and deterministically generates the eight
# MAGIC workshop tables. Create the `hc_workshop` catalog manually with Default Storage
# MAGIC before running the workshop setup. All records are synthetic.
# MAGIC
# MAGIC ## Configuration
# MAGIC Edit the values in the next cell before selecting **Run all**. Configuration
# MAGIC is stored visibly in the notebook source; no widget initialization is required.

# COMMAND ----------

# ruff: noqa: F821
from __future__ import annotations

import re
import uuid
from datetime import date

from pyspark.errors import PySparkException
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType

# CONFIGURATION — edit these values before running the notebook.
CATALOG = "hc_workshop"
SCHEMA = "core_lending"
MASTER_SEED = 20260922
AS_OF_DATE = "2026-09-01"
SCALE = "standard"  # small | standard | large
WRITE_MODE = "overwrite"  # overwrite | error

GENERATOR_NAME = "unicorn_finance_workshop"
LEGACY_GENERATOR_NAMES = {"home_credit_workshop"}
GENERATOR_VERSION = "1.1.0"

CATALOG = CATALOG.strip()
SCHEMA = SCHEMA.strip()
MASTER_SEED = int(MASTER_SEED)
AS_OF_DATE = AS_OF_DATE.strip()
SCALE = SCALE.strip()
WRITE_MODE = WRITE_MODE.strip()

IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

if not IDENTIFIER_PATTERN.fullmatch(CATALOG):
    raise ValueError(f"Invalid catalog identifier: {CATALOG!r}")
if not IDENTIFIER_PATTERN.fullmatch(SCHEMA):
    raise ValueError(f"Invalid schema identifier: {SCHEMA!r}")
if not DATE_PATTERN.fullmatch(AS_OF_DATE):
    raise ValueError("as_of_date must use YYYY-MM-DD")
try:
    date.fromisoformat(AS_OF_DATE)
except ValueError as error:
    raise ValueError("as_of_date must be a valid calendar date") from error
if SCALE not in {"small", "standard", "large"}:
    raise ValueError(f"Unsupported scale: {SCALE!r}")
if WRITE_MODE not in {"overwrite", "error"}:
    raise ValueError(f"Unsupported write_mode: {WRITE_MODE!r}")

SCALE_FACTOR = {"small": 0.1, "standard": 1.0, "large": 5.0}[SCALE]
N_CUSTOMERS = max(1_500, int(15_000 * SCALE_FACTOR))
N_LOCATIONS = max(100, int(1_000 * SCALE_FACTOR))
N_APPLICATIONS = max(4_000, int(40_000 * SCALE_FACTOR))
NUM_PARTITIONS = {"small": 8, "standard": 16, "large": 64}[SCALE]
HOT_STORE_COUNT = max(1, int(N_LOCATIONS * 0.20))
COLD_STORE_COUNT = N_LOCATIONS - HOT_STORE_COUNT
PROMO_HOTSPOT_COUNT = min(12, HOT_STORE_COUNT)

CATALOG_SQL = f"`{CATALOG}`"
SCHEMA_SQL = f"`{SCHEMA}`"
BUILD_SUFFIX = uuid.uuid4().hex[:8]
BUILD_SCHEMA = f"{SCHEMA}__build_{BUILD_SUFFIX}"
BUILD_SCHEMA_SQL = f"`{BUILD_SCHEMA}`"
TARGET_NAMESPACE = f"{CATALOG_SQL}.{SCHEMA_SQL}"
BUILD_NAMESPACE = f"{CATALOG_SQL}.{BUILD_SCHEMA_SQL}"
RUN_ID = f"{GENERATOR_VERSION}-{MASTER_SEED}-{AS_OF_DATE}-{SCALE}"
TABLE_NAMES = [
    "customer",
    "retail_location",
    "loan_product",
    "loan_application",
    "credit_contract",
    "installment",
    "payment",
    "collection_action",
]
TABLE_DESCRIPTIONS: dict[str, str] = {}

spark.conf.set("spark.sql.session.timeZone", "UTC")

print(
    f"Generator={GENERATOR_NAME} version={GENERATOR_VERSION} "
    f"namespace={CATALOG}.{SCHEMA} seed={MASTER_SEED} "
    f"as_of_date={AS_OF_DATE} scale={SCALE} write_mode={WRITE_MODE} "
    f"build_schema={BUILD_SCHEMA}"
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Deterministic generation helpers
# MAGIC
# MAGIC Every pseudo-random value is a pure function of the master seed, generator
# MAGIC version, field namespace, and stable row ID. It does not depend on Spark
# MAGIC partition placement or task execution order.

# COMMAND ----------

MONEY = DecimalType(18, 2)
RATE = DecimalType(7, 4)


def hash_bucket(stable_id: F.Column, namespace: str, modulo: int) -> F.Column:
    """Return a deterministic integer in [0, modulo)."""
    token = F.concat_ws(
        "|",
        F.lit(str(MASTER_SEED)),
        F.lit(GENERATOR_VERSION),
        F.lit(namespace),
        stable_id.cast("string"),
    )
    # Fifteen hex digits fit safely inside a signed BIGINT.
    numeric = F.conv(F.substring(F.sha2(token, 256), 1, 15), 16, 10).cast("long")
    return F.pmod(numeric, F.lit(modulo)).cast("int")


def uniform(stable_id: F.Column, namespace: str) -> F.Column:
    """Return a deterministic value strictly between zero and one."""
    return (hash_bucket(stable_id, namespace, 1_000_000).cast("double") + F.lit(0.5)) / F.lit(
        1_000_000.0
    )


def normal(stable_id: F.Column, namespace: str) -> F.Column:
    """Deterministic standard normal using a Box-Muller transform."""
    u1 = uniform(stable_id, f"{namespace}.u1")
    u2 = uniform(stable_id, f"{namespace}.u2")
    return F.sqrt(F.lit(-2.0) * F.log(u1)) * F.cos(F.lit(2.0 * 3.141592653589793) * u2)


def pick(values: list[str], stable_id: F.Column, namespace: str) -> F.Column:
    """Deterministically select one item from a small static list."""
    choices = F.array(*[F.lit(value) for value in values])
    return F.element_at(choices, hash_bucket(stable_id, namespace, len(values)) + F.lit(1))


def deterministic_timestamp(date_col: F.Column, stable_id: F.Column, namespace: str) -> F.Column:
    """Place an event at a deterministic second within the supplied UTC date."""
    midnight = F.unix_timestamp(date_col.cast("timestamp"))
    return F.from_unixtime(midnight + hash_bucket(stable_id, namespace, 86_400)).cast("timestamp")


def end_of_day(date_col: F.Column) -> F.Column:
    """Return 23:59:59 UTC on the supplied date."""
    midnight = F.unix_timestamp(date_col.cast("timestamp"))
    return F.from_unixtime(midnight + F.lit(86_399)).cast("timestamp")


def money(value: F.Column) -> F.Column:
    return F.round(value, 2).cast(MONEY)


def fq_table(table_name: str) -> str:
    return f"{BUILD_NAMESPACE}.`{table_name}`"


def target_table(table_name: str) -> str:
    return f"{TARGET_NAMESPACE}.`{table_name}`"


def write_table(df: DataFrame, table_name: str, description: str) -> None:
    TABLE_DESCRIPTIONS[table_name] = description
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fq_table(table_name))
    )
    escaped_description = description.replace("'", "''")
    spark.sql(f"COMMENT ON TABLE {fq_table(table_name)} IS '{escaped_description}'")
    spark.sql(
        f"""
        ALTER TABLE {fq_table(table_name)}
        SET TBLPROPERTIES (
          'workshop.generator' = '{GENERATOR_NAME}',
          'workshop.generator_version' = '{GENERATOR_VERSION}',
          'workshop.master_seed' = '{MASTER_SEED}',
          'workshop.as_of_date' = '{AS_OF_DATE}',
          'workshop.scale' = '{SCALE}',
          'workshop.run_id' = '{RUN_ID}',
          'workshop.synthetic' = 'true'
        )
        """
    )


AS_OF = F.to_date(F.lit(AS_OF_DATE))
WINDOW_START = F.add_months(AS_OF, -24)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Provision the Unity Catalog namespace

# COMMAND ----------

catalog_exists = (
    spark.sql("SHOW CATALOGS")
    .filter(F.col("catalog") == CATALOG)
    .limit(1)
    .count()
    > 0
)
if not catalog_exists:
    raise RuntimeError(
        f"Catalog {CATALOG!r} does not exist. Create it manually in Catalog Explorer "
        "using 'Use default storage', then rerun the workshop setup."
    )
spark.sql(
    f"CREATE SCHEMA IF NOT EXISTS {TARGET_NAMESPACE} "
    f"COMMENT 'Synthetic core lending data for workshop exercises'"
)
spark.sql(
    f"CREATE SCHEMA IF NOT EXISTS {BUILD_NAMESPACE} "
    f"COMMENT 'Validated build area for the Unicorn Finance workshop generator'"
)
spark.sql(f"USE CATALOG {CATALOG_SQL}")
spark.sql(f"USE SCHEMA {SCHEMA_SQL}")


def table_exists(schema_name: str, table_name: str) -> bool:
    return spark.catalog.tableExists(f"{CATALOG}.{schema_name}.{table_name}")


def assert_generator_owned(schema_name: str, table_name: str) -> None:
    fully_qualified = f"{CATALOG_SQL}.`{schema_name}`.`{table_name}`"
    detail = spark.sql(f"DESCRIBE DETAIL {fully_qualified}").select("format", "properties").first()
    properties = detail["properties"] or {}
    accepted_generator_names = LEGACY_GENERATOR_NAMES | {GENERATOR_NAME}
    if (
        detail["format"].lower() != "delta"
        or properties.get("workshop.generator") not in accepted_generator_names
    ):
        raise RuntimeError(
            f"Refusing to overwrite {CATALOG}.{schema_name}.{table_name}: "
            "the existing object is not a Delta table owned by this generator."
        )


existing_targets = [
    table_name
    for table_name in TABLE_NAMES
    if table_exists(SCHEMA, table_name)
]
if WRITE_MODE == "error" and existing_targets:
    raise RuntimeError(
        "write_mode=error and target tables already exist: "
        + ", ".join(existing_targets)
        + ". No workshop tables were changed."
    )
for existing_table in existing_targets:
    assert_generator_owned(SCHEMA, existing_table)
    spark.table(target_table(existing_table)).limit(1).count()
    spark.sql(
        f"""
        ALTER TABLE {target_table(existing_table)}
        SET TBLPROPERTIES ('workshop.generator' = '{GENERATOR_NAME}')
        """
    )

for build_table in TABLE_NAMES:
    if table_exists(BUILD_SCHEMA, build_table):
        assert_generator_owned(BUILD_SCHEMA, build_table)

PREFLIGHT_NAME = f"_generator_preflight_{BUILD_SUFFIX}"
PREFLIGHT_TABLE = f"{BUILD_NAMESPACE}.`{PREFLIGHT_NAME}`"
TARGET_PREFLIGHT_TABLE = f"{TARGET_NAMESPACE}.`{PREFLIGHT_NAME}`"
try:
    spark.sql(
        f"""
        CREATE TABLE {PREFLIGHT_TABLE}
        USING DELTA
        TBLPROPERTIES ('workshop.generator' = '{GENERATOR_NAME}')
        AS SELECT 1 AS permission_probe
        """
    )
    spark.sql(f"COMMENT ON TABLE {PREFLIGHT_TABLE} IS 'Temporary workshop permission probe'")
    spark.sql(
        f"ALTER TABLE {PREFLIGHT_TABLE} SET TBLPROPERTIES ('workshop.run_id' = '{RUN_ID}')"
    )
    spark.sql(f"CREATE TABLE {TARGET_PREFLIGHT_TABLE} DEEP CLONE {PREFLIGHT_TABLE}")
    spark.sql(
        f"CREATE OR REPLACE TABLE {TARGET_PREFLIGHT_TABLE} DEEP CLONE {PREFLIGHT_TABLE}"
    )
    spark.sql(
        f"COMMENT ON TABLE {TARGET_PREFLIGHT_TABLE} IS 'Temporary workshop publication probe'"
    )
    spark.sql(
        f"""
        ALTER TABLE {TARGET_PREFLIGHT_TABLE}
        SET TBLPROPERTIES ('workshop.run_id' = '{RUN_ID}')
        """
    )
finally:
    spark.sql(f"DROP TABLE IF EXISTS {TARGET_PREFLIGHT_TABLE}")
    spark.sql(f"DROP TABLE IF EXISTS {PREFLIGHT_TABLE}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Product catalogue

# COMMAND ----------

loan_product = spark.sql(
    """
    SELECT *
    FROM VALUES
      (1L, 'UNICORN_EASY_4M',    'Unicorn Easy Plan',         'POS_INSTALLMENT', 'ADD_ON',            3000.00,  30000.00,  4,  4, 0.0000, 3.9900, DATE'2024-01-01', NULL, true),
      (2L, 'UNICORN_POS_A',      'Unicorn Standard',          'POS_INSTALLMENT', 'ADD_ON',            5000.00,  80000.00,  6, 24, 1.9900, 5.9900, DATE'2024-01-01', NULL, true),
      (3L, 'UNICORN_POS_B',      'Unicorn Standard Plus',     'POS_INSTALLMENT', 'ADD_ON',           10000.00, 120000.00,  6, 24, 1.4900, 4.9900, DATE'2024-01-01', NULL, true),
      (4L, 'UNICORN_ZERO_PROMO', 'Unicorn 0% Brand Promotion','POS_INSTALLMENT', 'ADD_ON',            8000.00,  60000.00,  6, 12, 0.0000, 0.0000, DATE'2026-03-01', DATE'2026-04-15', false),
      (5L, 'UNICORN_CASH',       'Unicorn Cash',              'CASH_LOAN',       'ADD_ON',            5000.00, 150000.00,  6, 36, 1.4900, 8.9900, DATE'2024-01-01', NULL, true),
      (6L, 'UNICORN_CASH_PLUS',  'Unicorn Cash Plus',         'CASH_LOAN',       'ADD_ON',           30000.00, 250000.00, 12, 60, 1.4900, 6.9900, DATE'2024-01-01', NULL, true),
      (7L, 'UNICORN_FLEX',       'Unicorn Flex',              'REVOLVING_LINE',  'DECLINING_BALANCE', 3000.00,  50000.00, NULL, NULL, 0.0000, 4.0000, DATE'2024-01-01', NULL, true),
      (8L, 'UNICORN_VISA',       'Unicorn Visa',              'CREDIT_CARD',     'DECLINING_BALANCE', 5000.00, 100000.00, NULL, NULL, 3.0000, 3.0000, DATE'2024-01-01', NULL, true)
    AS product(
      product_id, product_code, product_name, product_type_code,
      interest_method_code, min_principal_amount, max_principal_amount,
      min_tenor_months, max_tenor_months, min_monthly_rate_pct,
      max_monthly_rate_pct, effective_from, effective_to, active_flag
    )
    """
).select(
    "product_id",
    "product_code",
    "product_name",
    "product_type_code",
    "interest_method_code",
    F.col("min_principal_amount").cast(MONEY).alias("min_principal_amount"),
    F.col("max_principal_amount").cast(MONEY).alias("max_principal_amount"),
    F.col("min_tenor_months").cast("int").alias("min_tenor_months"),
    F.col("max_tenor_months").cast("int").alias("max_tenor_months"),
    F.col("min_monthly_rate_pct").cast(RATE).alias("min_monthly_rate_pct"),
    F.col("max_monthly_rate_pct").cast(RATE).alias("max_monthly_rate_pct"),
    "effective_from",
    "effective_to",
    "active_flag",
).withColumn(
    "effective_from",
    F.when(F.col("product_id") == 4, F.add_months(AS_OF, -6)).otherwise(F.col("effective_from")),
).withColumn(
    "effective_to",
    F.when(F.col("product_id") == 4, F.date_add(F.add_months(AS_OF, -6), 45)).otherwise(
        F.col("effective_to")
    ),
)

write_table(
    loan_product,
    "loan_product",
    "Synthetic versioned commercial rules for Unicorn Finance lending products.",
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Retail locations

# COMMAND ----------

location_base = spark.range(1, N_LOCATIONS + 1, numPartitions=NUM_PARTITIONS).withColumnRenamed(
    "id", "store_id"
)
location_market = hash_bucket(F.col("store_id"), "retail_location.market", 100)
location_geo = hash_bucket(F.col("store_id"), "retail_location.geography", 100)

retail_location = (
    location_base.withColumn(
        "merchant_name",
        F.when(location_market < 28, F.lit("Apex Retail"))
        .when(location_market < 43, F.lit("BrightHome"))
        .when(location_market < 52, F.lit("Nova Mobile"))
        .when(location_market < 60, F.lit("ValueMart"))
        .otherwise(F.lit("Independent Retail Partner")),
    )
    .withColumn(
        "merchant_code",
        F.when(location_market < 28, F.lit("APEX"))
        .when(location_market < 43, F.lit("BRIGHTHOME"))
        .when(location_market < 52, F.lit("NOVA_MOBILE"))
        .when(location_market < 60, F.lit("VALUEMART"))
        .otherwise(
            F.concat(
                F.lit("IND-"),
                F.lpad(hash_bucket(F.col("store_id"), "retail_location.merchant", 250).cast("string"), 3, "0"),
            )
        ),
    )
    .withColumn(
        "merchant_type_code",
        F.when(location_market < 60, F.lit("LARGE_CHAIN")).otherwise(F.lit("INDEPENDENT")),
    )
    .withColumn(
        "province",
        F.when(location_geo < 30, F.lit("Metro Manila"))
        .when(location_geo < 42, F.lit("Cavite"))
        .when(location_geo < 53, F.lit("Cebu"))
        .when(location_geo < 63, F.lit("Laguna"))
        .when(location_geo < 71, F.lit("Bulacan"))
        .when(location_geo < 78, F.lit("Rizal"))
        .when(location_geo < 84, F.lit("Pampanga"))
        .when(location_geo < 90, F.lit("Davao del Sur"))
        .when(location_geo < 95, F.lit("Batangas"))
        .otherwise(F.lit("Iloilo")),
    )
    .withColumn(
        "city_municipality",
        F.when(location_geo < 10, F.lit("Quezon City"))
        .when(location_geo < 20, F.lit("Manila"))
        .when(location_geo < 30, F.lit("Makati"))
        .when(location_geo < 42, F.lit("Bacoor"))
        .when(location_geo < 53, F.lit("Cebu City"))
        .when(location_geo < 63, F.lit("Calamba"))
        .when(location_geo < 71, F.lit("Malolos"))
        .when(location_geo < 78, F.lit("Antipolo"))
        .when(location_geo < 84, F.lit("San Fernando"))
        .when(location_geo < 90, F.lit("Davao City"))
        .when(location_geo < 95, F.lit("Lipa"))
        .otherwise(F.lit("Iloilo City")),
    )
    .withColumn(
        "region_code",
        F.when(location_geo < 30, F.lit("NCR"))
        .when(location_geo < 42, F.lit("REGION_IV_A"))
        .when(location_geo < 53, F.lit("REGION_VII"))
        .when(location_geo < 63, F.lit("REGION_IV_A"))
        .when(location_geo < 71, F.lit("REGION_III"))
        .when(location_geo < 78, F.lit("REGION_IV_A"))
        .when(location_geo < 84, F.lit("REGION_III"))
        .when(location_geo < 90, F.lit("REGION_XI"))
        .when(location_geo < 95, F.lit("REGION_IV_A"))
        .otherwise(F.lit("REGION_VI")),
    )
    .withColumn("store_code", F.format_string("STORE-%06d", F.col("store_id")))
    .withColumn(
        "store_name",
        F.concat_ws(
            " - ",
            F.col("merchant_name"),
            F.col("city_municipality"),
            F.lpad(F.col("store_id").cast("string"), 4, "0"),
        ),
    )
    .withColumn(
        "opened_date",
        F.date_sub(AS_OF, hash_bucket(F.col("store_id"), "retail_location.opened", 3_000) + F.lit(365)),
    )
    .withColumn("active_flag", hash_bucket(F.col("store_id"), "retail_location.active", 100) >= F.lit(3))
    .withColumn("updated_at", deterministic_timestamp(AS_OF, F.col("store_id"), "retail_location.updated"))
    .select(
        "store_id",
        "store_code",
        "store_name",
        "merchant_code",
        "merchant_name",
        "merchant_type_code",
        "city_municipality",
        "province",
        "region_code",
        "opened_date",
        "active_flag",
        "updated_at",
    )
)

write_table(
    retail_location,
    "retail_location",
    "Synthetic merchant and physical store locations used for POS origination analysis.",
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Customers

# COMMAND ----------

FIRST_NAMES = [
    "Maria",
    "Jose",
    "Angel",
    "John",
    "Mark",
    "Anne",
    "Grace",
    "Carlo",
    "Liza",
    "Paolo",
    "Rose",
    "Miguel",
    "Joy",
    "Rafael",
    "Nina",
    "Luis",
]
LAST_NAMES = [
    "Santos",
    "Reyes",
    "Cruz",
    "Garcia",
    "Mendoza",
    "Bautista",
    "Flores",
    "Gonzales",
    "Ramos",
    "Aquino",
    "Castillo",
    "Navarro",
    "Villanueva",
    "Torres",
    "Rivera",
    "Diaz",
]

customer_base = spark.range(1, N_CUSTOMERS + 1, numPartitions=NUM_PARTITIONS).withColumnRenamed(
    "id", "customer_id"
)
customer_geo = hash_bucket(F.col("customer_id"), "customer.geography", 100)
income_z = normal(F.col("customer_id"), "customer.income")

customer = (
    customer_base.withColumn("customer_no", F.format_string("CUST-%010d", F.col("customer_id")))
    .withColumn(
        "national_id_no",
        F.concat(F.lit("SYN-ID-"), F.lpad(F.col("customer_id").cast("string"), 12, "0")),
    )
    .withColumn("first_name", pick(FIRST_NAMES, F.col("customer_id"), "customer.first_name"))
    .withColumn("last_name", pick(LAST_NAMES, F.col("customer_id"), "customer.last_name"))
    .withColumn(
        "birth_date",
        F.date_sub(
            AS_OF,
            F.lit(21 * 365)
            + hash_bucket(F.col("customer_id"), "customer.age_days", 40 * 365),
        ),
    )
    .withColumn(
        "sex_code",
        F.when(hash_bucket(F.col("customer_id"), "customer.sex", 100) < 52, F.lit("F"))
        .when(hash_bucket(F.col("customer_id"), "customer.sex", 100) < 98, F.lit("M"))
        .otherwise(F.lit(None).cast("string")),
    )
    .withColumn(
        "mobile_number",
        F.concat(F.lit("+63900"), F.lpad(F.col("customer_id").cast("string"), 7, "0")),
    )
    .withColumn(
        "email_address",
        F.when(
            hash_bucket(F.col("customer_id"), "customer.has_email", 100) < 72,
            F.concat(
                F.lower(F.col("first_name")),
                F.lit("."),
                F.lower(F.col("last_name")),
                F.lit("."),
                F.col("customer_id").cast("string"),
                F.lit("@example.invalid"),
            ),
        ).otherwise(F.lit(None).cast("string")),
    )
    .withColumn(
        "employment_type_code",
        F.when(hash_bucket(F.col("customer_id"), "customer.employment", 100) < 48, F.lit("SALARIED"))
        .when(hash_bucket(F.col("customer_id"), "customer.employment", 100) < 72, F.lit("SELF_EMPLOYED"))
        .when(hash_bucket(F.col("customer_id"), "customer.employment", 100) < 91, F.lit("INFORMAL"))
        .when(hash_bucket(F.col("customer_id"), "customer.employment", 100) < 97, F.lit("UNEMPLOYED"))
        .otherwise(F.lit("RETIRED")),
    )
    .withColumn(
        "monthly_income_amount",
        money(
            F.greatest(
                F.lit(8_000.0),
                F.least(F.lit(250_000.0), F.exp(F.log(F.lit(25_000.0)) + F.lit(0.60) * income_z)),
            )
        ),
    )
    .withColumn(
        "province",
        F.when(customer_geo < 32, F.lit("Metro Manila"))
        .when(customer_geo < 44, F.lit("Cavite"))
        .when(customer_geo < 55, F.lit("Cebu"))
        .when(customer_geo < 65, F.lit("Laguna"))
        .when(customer_geo < 73, F.lit("Bulacan"))
        .when(customer_geo < 80, F.lit("Rizal"))
        .when(customer_geo < 86, F.lit("Pampanga"))
        .when(customer_geo < 92, F.lit("Davao del Sur"))
        .when(customer_geo < 96, F.lit("Batangas"))
        .otherwise(F.lit("Iloilo")),
    )
    .withColumn(
        "city_municipality",
        F.when(customer_geo < 11, F.lit("Quezon City"))
        .when(customer_geo < 22, F.lit("Manila"))
        .when(customer_geo < 32, F.lit("Makati"))
        .when(customer_geo < 44, F.lit("Bacoor"))
        .when(customer_geo < 55, F.lit("Cebu City"))
        .when(customer_geo < 65, F.lit("Calamba"))
        .when(customer_geo < 73, F.lit("Malolos"))
        .when(customer_geo < 80, F.lit("Antipolo"))
        .when(customer_geo < 86, F.lit("San Fernando"))
        .when(customer_geo < 92, F.lit("Davao City"))
        .when(customer_geo < 96, F.lit("Lipa"))
        .otherwise(F.lit("Iloilo City")),
    )
    .withColumn(
        "customer_since_date",
        F.date_sub(
            AS_OF,
            hash_bucket(F.col("customer_id"), "customer.since", 2_190) + F.lit(731),
        ),
    )
    .withColumn(
        "created_at",
        deterministic_timestamp(F.col("customer_since_date"), F.col("customer_id"), "customer.created"),
    )
    .withColumn(
        "updated_at",
        deterministic_timestamp(
            F.date_sub(AS_OF, hash_bucket(F.col("customer_id"), "customer.updated_days", 180)),
            F.col("customer_id"),
            "customer.updated",
        ),
    )
    .select(
        "customer_id",
        "customer_no",
        "national_id_no",
        "first_name",
        "last_name",
        "birth_date",
        "sex_code",
        "mobile_number",
        "email_address",
        "employment_type_code",
        "monthly_income_amount",
        "province",
        "city_municipality",
        "customer_since_date",
        "created_at",
        "updated_at",
    )
)

write_table(
    customer,
    "customer",
    "Synthetic borrower and prospect profiles containing governance-lab PII.",
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Loan applications

# COMMAND ----------

application_base = spark.range(
    1, N_APPLICATIONS + 1, numPartitions=NUM_PARTITIONS
).withColumnRenamed("id", "application_id")
product_draw = hash_bucket(F.col("application_id"), "loan_application.product", 100)

application_with_product = application_base.withColumn(
    "product_id",
    F.when(product_draw < 10, F.lit(1))
    .when(product_draw < 45, F.lit(2))
    .when(product_draw < 55, F.lit(3))
    .when(product_draw < 70, F.lit(4))
    .when(product_draw < 80, F.lit(5))
    .when(product_draw < 85, F.lit(6))
    .when(product_draw < 95, F.lit(7))
    .otherwise(F.lit(8))
    .cast("long"),
)

application_date = F.when(
    F.col("product_id") == 4,
    F.date_add(
        F.add_months(AS_OF, -6),
        hash_bucket(F.col("application_id"), "loan_application.promo_day", 46),
    ),
).otherwise(
    F.date_add(WINDOW_START, hash_bucket(F.col("application_id"), "loan_application.day", 730))
)

amount_z = normal(F.col("application_id"), "loan_application.amount")
amount_median = (
    F.when(F.col("product_id") == 1, F.lit(12_000.0))
    .when(F.col("product_id").isin(2, 3), F.lit(25_000.0))
    .when(F.col("product_id") == 4, F.lit(32_000.0))
    .when(F.col("product_id") == 5, F.lit(45_000.0))
    .when(F.col("product_id") == 6, F.lit(90_000.0))
    .when(F.col("product_id") == 7, F.lit(18_000.0))
    .otherwise(F.lit(35_000.0))
)
amount_maximum = (
    F.when(F.col("product_id") == 1, F.lit(30_000.0))
    .when(F.col("product_id") == 2, F.lit(80_000.0))
    .when(F.col("product_id") == 3, F.lit(120_000.0))
    .when(F.col("product_id") == 4, F.lit(60_000.0))
    .when(F.col("product_id") == 5, F.lit(150_000.0))
    .when(F.col("product_id") == 6, F.lit(250_000.0))
    .when(F.col("product_id") == 7, F.lit(50_000.0))
    .otherwise(F.lit(100_000.0))
)
amount_minimum = (
    F.when(F.col("product_id") == 1, F.lit(3_000.0))
    .when(F.col("product_id") == 2, F.lit(5_000.0))
    .when(F.col("product_id") == 3, F.lit(10_000.0))
    .when(F.col("product_id") == 4, F.lit(8_000.0))
    .when(F.col("product_id") == 5, F.lit(5_000.0))
    .when(F.col("product_id") == 6, F.lit(30_000.0))
    .when(F.col("product_id") == 7, F.lit(3_000.0))
    .otherwise(F.lit(5_000.0))
)
requested_amount = money(
    F.greatest(
        amount_minimum,
        F.least(amount_maximum, F.exp(F.log(amount_median) + F.lit(0.50) * amount_z)),
    )
)

underwriting_score = F.greatest(
    F.lit(300.0),
    F.least(
        F.lit(850.0),
        F.round(F.lit(650.0) + F.lit(95.0) * normal(F.col("application_id"), "loan_application.score"), 0),
    ),
).cast(DecimalType(7, 2))

approval_threshold = (
    F.when(F.col("product_id").isin(1, 2, 3, 4), F.lit(555.0))
    .when(F.col("product_id").isin(5, 6), F.lit(620.0))
    .when(F.col("product_id") == 7, F.lit(610.0))
    .otherwise(F.lit(680.0))
)

general_store_id = F.when(
    hash_bucket(F.col("application_id"), "loan_application.store_tier", 100) < 80,
    hash_bucket(F.col("application_id"), "loan_application.hot_store", HOT_STORE_COUNT)
    + F.lit(1),
).otherwise(
    hash_bucket(F.col("application_id"), "loan_application.cold_store", COLD_STORE_COUNT)
    + F.lit(HOT_STORE_COUNT + 1)
)

assigned_store_id = F.when(
    (F.col("product_id") == 4)
    & (hash_bucket(F.col("application_id"), "loan_application.promo_hotspot", 100) < 35),
    hash_bucket(
        F.col("application_id"),
        "loan_application.promo_hotspot_store",
        PROMO_HOTSPOT_COUNT,
    )
    + F.lit(1),
).otherwise(general_store_id)

loan_application = (
    application_with_product.withColumn(
        "customer_id",
        (hash_bucket(F.col("application_id"), "loan_application.customer", N_CUSTOMERS) + F.lit(1)).cast("long"),
    )
    .withColumn("application_no", F.format_string("APP-%012d", F.col("application_id")))
    .withColumn("submitted_date", application_date)
    .withColumn(
        "submitted_at",
        deterministic_timestamp(F.col("submitted_date"), F.col("application_id"), "loan_application.submitted"),
    )
    .withColumn(
        "application_channel_code",
        F.when(F.col("product_id").isin(1, 2, 3, 4), F.lit("IN_STORE"))
        .when(F.col("product_id").isin(7, 8), F.lit("MOBILE_APP"))
        .when(hash_bucket(F.col("application_id"), "loan_application.cash_channel", 100) < 70, F.lit("MOBILE_APP"))
        .when(hash_bucket(F.col("application_id"), "loan_application.cash_channel", 100) < 90, F.lit("CALL_CENTER"))
        .otherwise(F.lit("WEB")),
    )
    .withColumn(
        "store_id",
        F.when(
            F.col("application_channel_code") == "IN_STORE",
            assigned_store_id.cast("long"),
        ).otherwise(F.lit(None).cast("long")),
    )
    .withColumn(
        "sales_associate_id",
        F.when(
            F.col("application_channel_code") == "IN_STORE",
            F.concat(
                F.lit("SA-"),
                F.lpad(F.col("store_id").cast("string"), 6, "0"),
                F.lit("-"),
                F.lpad(
                    (
                        hash_bucket(
                            F.col("application_id"),
                            "loan_application.local_associate",
                            5,
                        )
                        + F.lit(1)
                    ).cast("string"),
                    2,
                    "0",
                ),
            ),
        ).otherwise(F.lit(None).cast("string")),
    )
    .withColumn("requested_amount", requested_amount)
    .withColumn(
        "requested_tenor_months",
        F.when(F.col("product_id") == 1, F.lit(4))
        .when(
            F.col("product_id").isin(2, 3),
            F.element_at(
                F.array(F.lit(6), F.lit(9), F.lit(12), F.lit(18), F.lit(24)),
                hash_bucket(F.col("application_id"), "loan_application.pos_tenor", 5) + F.lit(1),
            ),
        )
        .when(
            F.col("product_id") == 4,
            F.element_at(
                F.array(F.lit(6), F.lit(9), F.lit(12)),
                hash_bucket(F.col("application_id"), "loan_application.promo_tenor", 3) + F.lit(1),
            ),
        )
        .when(
            F.col("product_id") == 5,
            F.element_at(
                F.array(F.lit(6), F.lit(12), F.lit(18), F.lit(24), F.lit(36)),
                hash_bucket(F.col("application_id"), "loan_application.cash_tenor", 5) + F.lit(1),
            ),
        )
        .when(
            F.col("product_id") == 6,
            F.element_at(
                F.array(F.lit(12), F.lit(18), F.lit(24), F.lit(36), F.lit(48), F.lit(60)),
                hash_bucket(F.col("application_id"), "loan_application.cash_plus_tenor", 6) + F.lit(1),
            ),
        )
        .otherwise(F.lit(None).cast("int")),
    )
    .withColumn(
        "declared_income_amount",
        money(
            F.greatest(
                F.lit(8_000.0),
                F.least(
                    F.lit(250_000.0),
                    F.exp(
                        F.log(F.lit(25_000.0))
                        + F.lit(0.65) * normal(F.col("application_id"), "loan_application.income")
                    ),
                ),
            )
        ),
    )
    .withColumn("underwriting_score", underwriting_score)
    .withColumn(
        "decision_code",
        F.when(hash_bucket(F.col("application_id"), "loan_application.cancel", 100) < 3, F.lit("CANCELLED"))
        .when(F.col("underwriting_score") >= approval_threshold, F.lit("APPROVED"))
        .otherwise(F.lit("DECLINED")),
    )
    .withColumn(
        "decision_reason_code",
        F.when(F.col("decision_code") == "APPROVED", F.lit(None).cast("string"))
        .when(F.col("decision_code") == "CANCELLED", F.lit("CUSTOMER_CANCELLED"))
        .when(F.col("underwriting_score") < F.lit(500), F.lit("CREDIT_SCORE"))
        .when(F.col("requested_amount") > F.col("declared_income_amount") * F.lit(4.0), F.lit("AFFORDABILITY"))
        .otherwise(F.lit("POLICY_RULE")),
    )
    .withColumn(
        "promotion_code",
        F.when(F.col("product_id") == 4, F.lit("ZERO_SMARTPHONE_2026")).otherwise(
            F.lit(None).cast("string")
        ),
    )
    .withColumn(
        "promotion_sponsor_type_code",
        F.when(F.col("product_id") == 4, F.lit("BRAND")).otherwise(F.lit(None).cast("string")),
    )
    .withColumn(
        "item_category_code",
        F.when(F.col("product_id") == 4, F.lit("SMARTPHONE"))
        .when(
            F.col("product_id").isin(1, 2, 3)
            & (hash_bucket(F.col("application_id"), "loan_application.item", 100) < 58),
            F.lit("SMARTPHONE"),
        )
        .when(
            F.col("product_id").isin(1, 2, 3)
            & (hash_bucket(F.col("application_id"), "loan_application.item", 100) < 78),
            F.lit("APPLIANCE"),
        )
        .when(F.col("product_id").isin(1, 2, 3), F.lit("LAPTOP"))
        .otherwise(F.lit(None).cast("string")),
    )
    .withColumn(
        "item_brand_name",
        F.when(F.col("product_id") == 4, F.lit("Nova Mobile"))
        .when(
            F.col("item_category_code") == "SMARTPHONE",
            pick(
                ["Nova Mobile", "Orion", "Aster", "Vela", "Pulse", "Kite"],
                F.col("application_id"),
                "loan_application.phone_brand",
            ),
        )
        .when(
            F.col("item_category_code").isNotNull(),
            pick(
                ["Northstar", "Lumi", "Solace", "Vertex", "Kinetic", "Harbor"],
                F.col("application_id"),
                "loan_application.other_brand",
            ),
        )
        .otherwise(F.lit(None).cast("string")),
    )
    .withColumn(
        "financed_amount",
        F.when(F.col("product_id").isin(1, 2, 3, 4), money(F.col("requested_amount") * F.lit(0.90))).otherwise(
            F.lit(None).cast(MONEY)
        ),
    )
    .withColumn(
        "decided_at",
        F.from_unixtime(
            F.unix_timestamp(F.col("submitted_at"))
            + hash_bucket(F.col("application_id"), "loan_application.decision_seconds", 540)
            + F.lit(60)
        ).cast("timestamp"),
    )
    .withColumn("created_at", F.col("submitted_at"))
    .withColumn("updated_at", F.col("decided_at"))
    .select(
        "application_id",
        "application_no",
        "customer_id",
        "product_id",
        "store_id",
        "sales_associate_id",
        "application_channel_code",
        "requested_amount",
        "requested_tenor_months",
        "declared_income_amount",
        "underwriting_score",
        "decision_code",
        "decision_reason_code",
        "promotion_code",
        "promotion_sponsor_type_code",
        "item_category_code",
        "item_brand_name",
        "financed_amount",
        "submitted_at",
        "decided_at",
        "created_at",
        "updated_at",
    )
)

write_table(
    loan_application,
    "loan_application",
    "Synthetic credit applications with underwriting decisions, stores, promotions, and financed items.",
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Credit contracts

# COMMAND ----------

applications_for_contract = spark.table(fq_table("loan_application")).filter(
    F.col("decision_code") == "APPROVED"
)
products_for_contract = spark.table(fq_table("loan_product"))


def default_cohort() -> F.Column:
    """Hidden deterministic performance driver; it is not written as a source field."""
    risky_store = F.coalesce(
        F.col("store_id") <= F.lit(PROMO_HOTSPOT_COUNT),
        F.lit(False),
    )
    risky_associate = F.coalesce(
        F.col("sales_associate_id").endswith("-01"),
        F.lit(False),
    )
    risk_draw = uniform(F.col("application_id"), "performance.default")
    probability = (
        F.when(
            (F.col("product_id") == 4) & risky_store & risky_associate,
            F.lit(0.72),
        )
        .when((F.col("product_id") == 4) & risky_store, F.lit(0.48))
        .when((F.col("product_id") == 4) & risky_associate, F.lit(0.24))
        .when(F.col("product_id") == 4, F.lit(0.14))
        .when(F.col("product_id").isin(5, 6), F.lit(0.18))
        .when(F.col("product_id").isin(1, 2, 3), F.lit(0.07))
        .otherwise(F.lit(0.04))
    )
    return risk_draw < probability


contract_joined = applications_for_contract.alias("a").join(
    products_for_contract.alias("p"), on="product_id", how="inner"
)

monthly_rate = (
    F.col("p.min_monthly_rate_pct").cast("double")
    + (
        F.col("p.max_monthly_rate_pct").cast("double")
        - F.col("p.min_monthly_rate_pct").cast("double")
    )
    * uniform(F.col("application_id"), "credit_contract.rate")
)

credit_contract = (
    contract_joined.withColumn("contract_id", F.col("application_id"))
    .withColumn("contract_no", F.format_string("CTR-%012d", F.col("application_id")))
    .withColumn("origination_date", F.to_date(F.col("decided_at")))
    .withColumn("is_default_cohort", default_cohort())
    .withColumn(
        "maturity_date",
        F.when(
            F.col("requested_tenor_months").isNotNull(),
            F.add_months(F.col("origination_date"), F.col("requested_tenor_months")),
        ).otherwise(F.lit(None).cast("date")),
    )
    .withColumn(
        "contract_status_code",
        F.when(
            F.col("is_default_cohort") & (F.col("origination_date") <= F.date_sub(AS_OF, 90)),
            F.lit("DEFAULTED"),
        )
        .when(F.col("maturity_date").isNotNull() & (F.col("maturity_date") < AS_OF), F.lit("CLOSED"))
        .otherwise(F.lit("ACTIVE")),
    )
    .withColumn("currency_code", F.lit("PHP"))
    .withColumn(
        "principal_amount",
        F.when(
            F.col("product_type_code") == "POS_INSTALLMENT",
            F.coalesce(F.col("financed_amount"), F.col("requested_amount")),
        )
        .when(F.col("product_type_code") == "CASH_LOAN", F.col("requested_amount"))
        .otherwise(F.lit(None).cast(MONEY)),
    )
    .withColumn(
        "credit_limit_amount",
        F.when(F.col("product_type_code").isin("REVOLVING_LINE", "CREDIT_CARD"), F.col("requested_amount")).otherwise(
            F.lit(None).cast(MONEY)
        ),
    )
    .withColumn("tenor_months", F.col("requested_tenor_months"))
    .withColumn("monthly_interest_rate_pct", F.round(monthly_rate, 4).cast(RATE))
    .withColumn("interest_method_code", F.col("p.interest_method_code"))
    .withColumn(
        "processing_fee_amount",
        F.when(F.col("product_type_code") == "POS_INSTALLMENT", money(F.col("principal_amount") * F.lit(0.03)))
        .when(F.col("product_type_code") == "CASH_LOAN", money(F.col("principal_amount") * F.lit(0.02)))
        .otherwise(F.lit(0).cast(MONEY)),
    )
    .withColumn(
        "subsidy_amount",
        F.when(F.col("product_id") == 4, money(F.col("principal_amount") * F.lit(0.08))).otherwise(
            F.lit(0).cast(MONEY)
        ),
    )
    .withColumn(
        "disbursed_at",
        F.from_unixtime(F.unix_timestamp(F.col("decided_at")) + F.lit(3_600)).cast("timestamp"),
    )
    .withColumn(
        "closed_at",
        F.when(
            F.col("contract_status_code") == "CLOSED",
            end_of_day(
                F.least(
                    F.date_add(F.col("maturity_date"), 46),
                    AS_OF,
                )
            ),
        ).otherwise(F.lit(None).cast("timestamp")),
    )
    .withColumn("created_at", F.col("disbursed_at"))
    .withColumn(
        "updated_at",
        F.when(F.col("closed_at").isNotNull(), F.col("closed_at")).otherwise(
            F.greatest(
                F.col("created_at"),
                deterministic_timestamp(AS_OF, F.col("contract_id"), "credit_contract.updated"),
            )
        ),
    )
    .select(
        "contract_id",
        "contract_no",
        "application_id",
        "contract_status_code",
        "currency_code",
        "principal_amount",
        "credit_limit_amount",
        "tenor_months",
        "monthly_interest_rate_pct",
        "interest_method_code",
        "processing_fee_amount",
        "subsidy_amount",
        "origination_date",
        "maturity_date",
        "disbursed_at",
        "closed_at",
        "created_at",
        "updated_at",
    )
)

write_table(
    credit_contract,
    "credit_contract",
    "Synthetic accepted contracts containing fixed-term principal or revolving credit limits.",
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Installment schedules

# COMMAND ----------

contracts_for_schedule = (
    spark.table(fq_table("credit_contract"))
    .filter(F.col("tenor_months").isNotNull())
    .alias("c")
    .join(
        spark.table(fq_table("loan_application"))
        .select(
            "application_id",
            "product_id",
            "store_id",
            "sales_associate_id",
            "promotion_code",
        )
        .alias("a"),
        on="application_id",
        how="inner",
    )
)

schedule_base = contracts_for_schedule.withColumn(
    "installment_no", F.explode(F.sequence(F.lit(1), F.col("tenor_months")))
).withColumn(
    "installment_id", (F.col("contract_id") * F.lit(100) + F.col("installment_no")).cast("long")
)

schedule_with_due = (
    schedule_base.withColumn("due_date", F.add_months(F.col("origination_date"), F.col("installment_no")))
    .withColumn("is_default_cohort", default_cohort())
    .withColumn("behavior_draw", uniform(F.col("installment_id"), "installment.behavior"))
    .withColumn("is_due", F.col("due_date") <= AS_OF)
)

behavior = (
    F.when(~F.col("is_due"), F.lit("FUTURE"))
    .when(
        (F.col("contract_status_code") == "CLOSED") & (F.col("behavior_draw") < F.lit(0.90)),
        F.lit("PAID_ON_TIME"),
    )
    .when(F.col("contract_status_code") == "CLOSED", F.lit("PAID_LATE"))
    .when(F.col("is_default_cohort") & (F.col("installment_no") <= 3), F.lit("UNPAID"))
    .when(F.col("behavior_draw") < F.lit(0.82), F.lit("PAID_ON_TIME"))
    .when(
        (F.col("behavior_draw") < F.lit(0.90)) & (F.col("due_date") < AS_OF),
        F.lit("PAID_LATE"),
    )
    .when(F.col("behavior_draw") < F.lit(0.90), F.lit("PAID_ON_TIME"))
    .when(F.col("behavior_draw") < F.lit(0.95), F.lit("PARTIAL"))
    .otherwise(F.lit("UNPAID"))
)

days_past_due_now = F.greatest(F.lit(0), F.datediff(AS_OF, F.col("due_date")))


def fee_for_dpd(dpd: F.Column) -> F.Column:
    return (
        F.when(dpd < 5, F.lit(0.0))
        .when(dpd < 30, F.lit(200.0))
        .when(dpd < 60, F.lit(400.0))
        .when(dpd < 90, F.lit(600.0))
        .otherwise(F.lit(800.0))
    )


def partial_payment_milestone(installment_id: F.Column, current_dpd: F.Column) -> F.Column:
    draw = hash_bucket(installment_id, "payment.partial_milestone", 100)
    return (
        F.when(
            current_dpd >= 90,
            F.when(draw < 40, F.lit(5))
            .when(draw < 70, F.lit(30))
            .when(draw < 90, F.lit(60))
            .otherwise(F.lit(90)),
        )
        .when(
            current_dpd >= 60,
            F.when(draw < 50, F.lit(5))
            .when(draw < 80, F.lit(30))
            .otherwise(F.lit(60)),
        )
        .when(
            current_dpd >= 30,
            F.when(draw < 60, F.lit(5)).otherwise(F.lit(30)),
        )
        .when(current_dpd >= 5, F.lit(5))
        .otherwise(current_dpd)
    )


late_fee = fee_for_dpd(days_past_due_now)

installment = (
    schedule_with_due.withColumn("behavior", behavior)
    .withColumn(
        "regular_principal_due_amount",
        money(F.col("principal_amount") / F.col("tenor_months")),
    )
    .withColumn(
        "principal_due_amount",
        F.when(
            F.col("installment_no") == F.col("tenor_months"),
            money(
                F.col("principal_amount")
                - F.col("regular_principal_due_amount") * (F.col("tenor_months") - F.lit(1))
            ),
        ).otherwise(F.col("regular_principal_due_amount")),
    )
    .withColumn(
        "interest_due_amount",
        money(
            F.when(
                F.col("interest_method_code") == "ADD_ON",
                F.col("principal_amount") * F.col("monthly_interest_rate_pct").cast("double") / F.lit(100.0),
            ).otherwise(F.lit(0.0))
        ),
    )
    .withColumn(
        "fee_due_amount",
        money(
            F.when(F.col("behavior").isin("UNPAID", "PARTIAL"), late_fee).otherwise(F.lit(0.0))
        ),
    )
    .withColumn(
        "total_due_amount",
        money(
            F.col("principal_due_amount")
            + F.col("interest_due_amount")
            + F.col("fee_due_amount")
        ),
    )
    .withColumn(
        "partial_payment_dpd",
        partial_payment_milestone(
            F.col("installment_id"),
            days_past_due_now,
        ),
    )
    .withColumn(
        "partial_payment_amount",
        money(
            (
                F.col("principal_due_amount")
                + F.col("interest_due_amount")
                + fee_for_dpd(F.col("partial_payment_dpd"))
            )
            * F.lit(0.50)
        ),
    )
    .withColumn(
        "outstanding_amount",
        money(
            F.when(F.col("behavior").isin("PAID_ON_TIME", "PAID_LATE"), F.lit(0.0))
            .when(
                F.col("behavior") == "PARTIAL",
                F.col("total_due_amount") - F.col("partial_payment_amount"),
            )
            .otherwise(F.col("total_due_amount"))
        ),
    )
    .withColumn(
        "installment_status_code",
        F.when(F.col("behavior").isin("PAID_ON_TIME", "PAID_LATE"), F.lit("PAID"))
        .when(F.col("behavior") == "PARTIAL", F.lit("PARTIAL"))
        .when(F.col("behavior") == "UNPAID", F.lit("OVERDUE"))
        .otherwise(F.lit("SCHEDULED")),
    )
    .withColumn(
        "settled_date",
        F.when(
            F.col("behavior") == "PAID_ON_TIME",
            F.date_sub(F.col("due_date"), hash_bucket(F.col("installment_id"), "installment.early_days", 4)),
        )
        .when(
            F.col("behavior") == "PAID_LATE",
            F.date_add(
                F.col("due_date"),
                F.least(
                    hash_bucket(F.col("installment_id"), "installment.late_days", 45) + F.lit(1),
                    F.greatest(F.lit(0), F.datediff(AS_OF, F.col("due_date"))),
                ),
            ),
        )
        .otherwise(F.lit(None).cast("date")),
    )
    .withColumn("created_at", F.col("origination_date").cast("timestamp"))
    .withColumn(
        "updated_at",
        F.when(
            F.col("settled_date").isNotNull(),
            end_of_day(F.col("settled_date")),
        ).otherwise(end_of_day(AS_OF)),
    )
    .select(
        "installment_id",
        "contract_id",
        "installment_no",
        "due_date",
        "principal_due_amount",
        "interest_due_amount",
        "fee_due_amount",
        "total_due_amount",
        "outstanding_amount",
        "installment_status_code",
        "settled_date",
        "created_at",
        "updated_at",
    )
)

write_table(
    installment,
    "installment",
    "Synthetic fixed-term repayment schedules with paid, partial, overdue, and future obligations.",
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Payment events

# COMMAND ----------

installments_for_payment = spark.table(fq_table("installment")).filter(
    F.col("due_date") <= AS_OF
)

current_payment_dpd = F.greatest(F.lit(0), F.datediff(AS_OF, F.col("due_date")))
partial_payment_dpd = partial_payment_milestone(
    F.col("installment_id"),
    current_payment_dpd,
)

payment_attempts = (
    installments_for_payment.withColumn("partial_payment_dpd", partial_payment_dpd)
    .withColumn(
        "partial_payment_date",
        F.date_add(F.col("due_date"), F.col("partial_payment_dpd")),
    )
    .withColumn(
        "attempt_count",
        F.when(
            (F.col("installment_status_code") == "PAID")
            & (F.col("settled_date") > F.col("due_date"))
            & (hash_bucket(F.col("installment_id"), "payment.retry", 100) < 35),
            F.lit(2),
        ).otherwise(F.lit(1)),
    )
    .withColumn("attempt_no", F.explode(F.sequence(F.lit(1), F.col("attempt_count"))))
    .withColumn(
        "payment_id", (F.col("installment_id") * F.lit(10) + F.col("attempt_no")).cast("long")
    )
)

is_retry_failure = (F.col("attempt_count") == 2) & (F.col("attempt_no") == 1)
is_posted = (
    (F.col("installment_status_code").isin("PAID", "PARTIAL"))
    & ~is_retry_failure
)

payment = (
    payment_attempts.withColumn(
        "payment_status_code",
        F.when(is_posted, F.lit("POSTED")).otherwise(F.lit("FAILED")),
    )
    .withColumn(
        "payment_at",
        F.when(
            is_posted & (F.col("installment_status_code") == "PARTIAL"),
            deterministic_timestamp(
                F.col("partial_payment_date"),
                F.col("payment_id"),
                "payment.partial_time",
            ),
        )
        .when(
            is_posted & F.col("settled_date").isNotNull(),
            deterministic_timestamp(F.col("settled_date"), F.col("payment_id"), "payment.posted_time"),
        ).otherwise(
            deterministic_timestamp(
                F.col("due_date"),
                F.col("payment_id"),
                "payment.failed_time",
            )
        ),
    )
    .withColumn(
        "payment_amount",
        money(
            F.when(
                F.col("payment_status_code") == "FAILED",
                F.col("principal_due_amount") + F.col("interest_due_amount"),
            )
            .when(
                F.col("installment_status_code") == "PARTIAL",
                (
                    F.col("principal_due_amount")
                    + F.col("interest_due_amount")
                    + fee_for_dpd(F.col("partial_payment_dpd"))
                )
                * F.lit(0.50),
            )
            .otherwise(F.col("total_due_amount"))
        ),
    )
    .withColumn(
        "payment_channel_code",
        F.when(hash_bucket(F.col("payment_id"), "payment.channel", 100) < 40, F.lit("APP"))
        .when(hash_bucket(F.col("payment_id"), "payment.channel", 100) < 68, F.lit("PAYMENT_CENTER"))
        .when(hash_bucket(F.col("payment_id"), "payment.channel", 100) < 88, F.lit("BANK_TRANSFER"))
        .otherwise(F.lit("STORE")),
    )
    .withColumn(
        "failure_reason_code",
        F.when(
            F.col("payment_status_code") == "FAILED",
            F.when(hash_bucket(F.col("payment_id"), "payment.failure", 100) < 70, F.lit("INSUFFICIENT_FUNDS"))
            .when(hash_bucket(F.col("payment_id"), "payment.failure", 100) < 90, F.lit("CHANNEL_ERROR"))
            .otherwise(F.lit("ACCOUNT_RESTRICTED")),
        ).otherwise(F.lit(None).cast("string")),
    )
    .withColumn(
        "posted_at",
        F.when(F.col("payment_status_code") == "POSTED", F.col("payment_at")).otherwise(
            F.lit(None).cast("timestamp")
        ),
    )
    .withColumn("payment_reference", F.format_string("PAY-%014d", F.col("payment_id")))
    .withColumn("created_at", F.col("payment_at"))
    .select(
        "payment_id",
        "payment_reference",
        "contract_id",
        "installment_id",
        "payment_at",
        "payment_amount",
        "payment_channel_code",
        "payment_status_code",
        "failure_reason_code",
        "posted_at",
        "created_at",
    )
)

write_table(
    payment,
    "payment",
    "Synthetic payment attempts and receipts, including deterministic retries and failures.",
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 8. Collection actions

# COMMAND ----------

delinquent_installments = (
    spark.table(fq_table("installment"))
    .filter(F.col("installment_status_code").isin("OVERDUE", "PARTIAL"))
    .withColumn("current_dpd", F.datediff(AS_OF, F.col("due_date")))
    .filter(F.col("current_dpd") >= 5)
)

partial_payment_events = (
    spark.table(fq_table("payment"))
    .filter(F.col("payment_status_code") == "POSTED")
    .groupBy("installment_id")
    .agg(
        F.min("payment_at").alias("payment_received_at"),
        F.sum("payment_amount").cast(MONEY).alias("payment_received_amount"),
    )
)

collection_milestones = (
    delinquent_installments.join(
        partial_payment_events,
        on="installment_id",
        how="left",
    )
    .withColumn(
        "payment_received_dpd",
        F.when(
            F.col("payment_received_at").isNotNull(),
            F.datediff(F.to_date(F.col("payment_received_at")), F.col("due_date")),
        ),
    )
    .withColumn(
        "days_past_due_at_action",
        F.explode(F.array(F.lit(5), F.lit(30), F.lit(60), F.lit(90))),
    )
    .filter(F.col("days_past_due_at_action") <= F.col("current_dpd"))
    .filter(
        F.col("payment_received_dpd").isNull()
        | (F.col("days_past_due_at_action") <= F.col("payment_received_dpd"))
    )
)

collection_action = (
    collection_milestones.withColumn(
        "collection_action_id",
        (F.col("installment_id") * F.lit(100) + F.col("days_past_due_at_action")).cast("long"),
    )
    .withColumn(
        "scheduled_action_at",
        deterministic_timestamp(
            F.date_add(F.col("due_date"), F.col("days_past_due_at_action")),
            F.col("collection_action_id"),
            "collection_action.time",
        ),
    )
    .withColumn(
        "action_type_code",
        F.when(F.col("days_past_due_at_action") == 5, F.lit("SMS"))
        .when(F.col("days_past_due_at_action") == 30, F.lit("CALL"))
        .when(F.col("days_past_due_at_action") == 60, F.lit("NOTICE"))
        .otherwise(F.lit("FIELD_VISIT")),
    )
    .withColumn(
        "outcome_code",
        F.when(
            F.col("payment_received_dpd").isNotNull()
            & (F.col("days_past_due_at_action") == F.col("payment_received_dpd")),
            F.lit("PAYMENT_RECEIVED"),
        )
        .when(hash_bucket(F.col("collection_action_id"), "collection_action.outcome", 100) < 35, F.lit("NO_CONTACT"))
        .when(hash_bucket(F.col("collection_action_id"), "collection_action.outcome", 100) < 62, F.lit("CONTACTED"))
        .otherwise(F.lit("PROMISE_TO_PAY")),
    )
    .withColumn(
        "action_at",
        F.when(
            F.col("outcome_code") == "PAYMENT_RECEIVED",
            F.col("payment_received_at"),
        ).otherwise(F.col("scheduled_action_at")),
    )
    .withColumn(
        "promise_to_pay_date",
        F.when(
            F.col("outcome_code") == "PROMISE_TO_PAY",
            F.date_add(
                F.to_date(F.col("action_at")),
                hash_bucket(F.col("collection_action_id"), "collection_action.promise_days", 14) + F.lit(1),
            ),
        ).otherwise(F.lit(None).cast("date")),
    )
    .withColumn(
        "promise_amount",
        F.when(
            F.col("outcome_code") == "PROMISE_TO_PAY",
            money(F.col("outstanding_amount") * F.lit(0.50)),
        ).otherwise(F.lit(None).cast(MONEY)),
    )
    .withColumn(
        "amount_collected",
        F.when(
            F.col("outcome_code") == "PAYMENT_RECEIVED",
            F.col("payment_received_amount"),
        ).otherwise(
            F.lit(0).cast(MONEY)
        ),
    )
    .withColumn(
        "agent_id",
        F.when(
            F.col("action_type_code").isin("CALL", "FIELD_VISIT"),
            F.concat(
                F.lit("COL-"),
                F.lpad(
                    (hash_bucket(F.col("collection_action_id"), "collection_action.agent", 500) + F.lit(1)).cast(
                        "string"
                    ),
                    4,
                    "0",
                ),
            ),
        ).otherwise(F.lit(None).cast("string")),
    )
    .withColumn("created_at", F.col("action_at"))
    .select(
        "collection_action_id",
        "contract_id",
        "installment_id",
        "action_at",
        "days_past_due_at_action",
        "action_type_code",
        "outcome_code",
        "promise_to_pay_date",
        "promise_amount",
        "amount_collected",
        "agent_id",
        "created_at",
    )
)

write_table(
    collection_action,
    "collection_action",
    "Synthetic collection attempts and outcomes at 5, 30, 60, and 90 days past due.",
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Validation

# COMMAND ----------


def table_summary(table_name: str) -> DataFrame:
    df = spark.table(fq_table(table_name))
    canonical_row = F.concat_ws(
        "||",
        *[
            F.coalesce(F.col(column_name).cast("string"), F.lit("<NULL>"))
            for column_name in df.columns
        ],
    )
    return df.agg(
        F.lit(table_name).alias("table_name"),
        F.count(F.lit(1)).alias("row_count"),
        F.sum(
            F.pmod(F.xxhash64(canonical_row), F.lit(2_147_483_647)).cast(
                DecimalType(38, 0)
            )
        ).alias("logical_checksum"),
    )


summary = (
    table_summary("customer")
    .unionByName(table_summary("retail_location"))
    .unionByName(table_summary("loan_product"))
    .unionByName(table_summary("loan_application"))
    .unionByName(table_summary("credit_contract"))
    .unionByName(table_summary("installment"))
    .unionByName(table_summary("payment"))
    .unionByName(table_summary("collection_action"))
)

display(summary.orderBy("table_name"))


def orphan_check(
    check_name: str,
    child_table: str,
    child_key: str,
    parent_table: str,
    parent_key: str,
) -> DataFrame:
    child = spark.table(fq_table(child_table)).filter(F.col(child_key).isNotNull()).alias("child")
    parent = spark.table(fq_table(parent_table)).select(parent_key).alias("parent")
    return (
        child.join(
            parent,
            F.col(f"child.{child_key}") == F.col(f"parent.{parent_key}"),
            "left_anti",
        )
        .agg(F.count(F.lit(1)).alias("failure_count"))
        .withColumn("check_name", F.lit(check_name))
        .select("check_name", "failure_count")
    )


def duplicate_check(check_name: str, table_name: str, primary_key: str) -> DataFrame:
    return (
        spark.table(fq_table(table_name))
        .groupBy(primary_key)
        .count()
        .filter(F.col("count") > 1)
        .agg(F.coalesce(F.sum(F.col("count") - F.lit(1)), F.lit(0)).alias("failure_count"))
        .withColumn("check_name", F.lit(check_name))
        .select("check_name", "failure_count")
    )


fk_checks = (
    orphan_check("application_customer", "loan_application", "customer_id", "customer", "customer_id")
    .unionByName(
        orphan_check("application_location", "loan_application", "store_id", "retail_location", "store_id")
    )
    .unionByName(
        orphan_check("application_product", "loan_application", "product_id", "loan_product", "product_id")
    )
    .unionByName(
        orphan_check("contract_application", "credit_contract", "application_id", "loan_application", "application_id")
    )
    .unionByName(
        orphan_check("installment_contract", "installment", "contract_id", "credit_contract", "contract_id")
    )
    .unionByName(
        orphan_check("payment_contract", "payment", "contract_id", "credit_contract", "contract_id")
    )
    .unionByName(
        orphan_check("payment_installment", "payment", "installment_id", "installment", "installment_id")
    )
    .unionByName(
        orphan_check(
            "collection_contract", "collection_action", "contract_id", "credit_contract", "contract_id"
        )
    )
    .unionByName(
        orphan_check(
            "collection_installment", "collection_action", "installment_id", "installment", "installment_id"
        )
    )
)

display(fk_checks.orderBy("check_name"))

pk_checks = duplicate_check("customer_pk", "customer", "customer_id")
for table_name, primary_key in [
    ("retail_location", "store_id"),
    ("loan_product", "product_id"),
    ("loan_application", "application_id"),
    ("credit_contract", "contract_id"),
    ("installment", "installment_id"),
    ("payment", "payment_id"),
    ("collection_action", "collection_action_id"),
]:
    pk_checks = pk_checks.unionByName(
        duplicate_check(f"{table_name}_pk", table_name, primary_key)
    )

display(pk_checks.orderBy("check_name"))

consistency_checks = spark.sql(
    f"""
    SELECT 'expected_customer_rows' AS check_name,
           ABS(COUNT(*) - {N_CUSTOMERS}) AS failure_count
    FROM {fq_table("customer")}
    UNION ALL
    SELECT 'expected_location_rows', ABS(COUNT(*) - {N_LOCATIONS})
    FROM {fq_table("retail_location")}
    UNION ALL
    SELECT 'expected_product_rows', ABS(COUNT(*) - 8)
    FROM {fq_table("loan_product")}
    UNION ALL
    SELECT 'expected_application_rows', ABS(COUNT(*) - {N_APPLICATIONS})
    FROM {fq_table("loan_application")}
    UNION ALL
    SELECT 'application_timestamp_order', COUNT(*)
    FROM {fq_table("loan_application")}
    WHERE submitted_at >= CAST(date_add(DATE'{AS_OF_DATE}', 1) AS TIMESTAMP)
       OR (decided_at IS NOT NULL AND decided_at < submitted_at)
    UNION ALL
    SELECT 'contract_timestamp_order', COUNT(*)
    FROM {fq_table("credit_contract")} c
    JOIN {fq_table("loan_application")} a USING (application_id)
    WHERE c.created_at < a.submitted_at
       OR c.updated_at < c.created_at
       OR (c.closed_at IS NOT NULL AND c.closed_at < c.created_at)
       OR c.created_at >= CAST(date_add(DATE'{AS_OF_DATE}', 1) AS TIMESTAMP)
    UNION ALL
    SELECT 'contract_amount_type', COUNT(*)
    FROM {fq_table("credit_contract")}
    WHERE (principal_amount IS NULL AND credit_limit_amount IS NULL)
       OR (principal_amount IS NOT NULL AND credit_limit_amount IS NOT NULL)
    UNION ALL
    SELECT 'installment_principal_reconciliation', COUNT(*)
    FROM {fq_table("credit_contract")} c
    JOIN (
      SELECT contract_id, SUM(principal_due_amount) AS scheduled_principal
      FROM {fq_table("installment")}
      GROUP BY contract_id
    ) i USING (contract_id)
    WHERE ABS(c.principal_amount - i.scheduled_principal) > 0.01
    UNION ALL
    SELECT 'payment_timestamp_after_as_of', COUNT(*)
    FROM {fq_table("payment")}
    WHERE payment_at >= CAST(date_add(DATE'{AS_OF_DATE}', 1) AS TIMESTAMP)
       OR (posted_at IS NOT NULL AND posted_at <> payment_at)
    UNION ALL
    SELECT 'payment_status_consistency', COUNT(*)
    FROM {fq_table("payment")}
    WHERE (payment_status_code = 'POSTED'
           AND (posted_at IS NULL OR failure_reason_code IS NOT NULL))
       OR (payment_status_code = 'FAILED'
           AND (posted_at IS NOT NULL OR failure_reason_code IS NULL))
    UNION ALL
    SELECT 'partial_payment_balance_reconciliation', COUNT(*)
    FROM {fq_table("installment")} i
    JOIN (
      SELECT installment_id, SUM(payment_amount) AS posted_amount
      FROM {fq_table("payment")}
      WHERE payment_status_code = 'POSTED'
      GROUP BY installment_id
    ) p USING (installment_id)
    WHERE i.installment_status_code = 'PARTIAL'
      AND ABS(i.total_due_amount - i.outstanding_amount - p.posted_amount) > 0.01
    UNION ALL
    SELECT 'payment_before_servicing_update', COUNT(*)
    FROM {fq_table("payment")} p
    JOIN {fq_table("installment")} i USING (installment_id)
    WHERE p.payment_at > i.updated_at
    UNION ALL
    SELECT 'payment_after_contract_close', COUNT(*)
    FROM {fq_table("payment")} p
    JOIN {fq_table("credit_contract")} c USING (contract_id)
    WHERE c.closed_at IS NOT NULL
      AND p.payment_at > c.closed_at
    UNION ALL
    SELECT 'collection_payment_reconciliation', COUNT(*)
    FROM {fq_table("collection_action")} ca
    LEFT JOIN {fq_table("payment")} p
      ON ca.installment_id = p.installment_id
     AND ca.action_at = p.payment_at
     AND ca.amount_collected = p.payment_amount
     AND p.payment_status_code = 'POSTED'
    WHERE (ca.outcome_code = 'PAYMENT_RECEIVED' AND p.payment_id IS NULL)
       OR (ca.outcome_code <> 'PAYMENT_RECEIVED' AND ca.amount_collected <> 0)
    UNION ALL
    SELECT 'collection_timestamp_order', COUNT(*)
    FROM {fq_table("collection_action")} ca
    JOIN {fq_table("installment")} i USING (installment_id)
    WHERE ca.action_at < CAST(i.due_date AS TIMESTAMP)
       OR ca.action_at >= CAST(date_add(DATE'{AS_OF_DATE}', 1) AS TIMESTAMP)
    """
)

display(consistency_checks.orderBy("check_name"))

all_structural_checks = (
    fk_checks.unionByName(pk_checks)
    .unionByName(consistency_checks)
)
if all_structural_checks.filter(F.col("failure_count") > 0).count() > 0:
    raise RuntimeError(
        "Structural validation failed in the isolated build schema; "
        "the target workshop tables were not published."
    )

story_check = spark.sql(
    f"""
    WITH first_installment AS (
      SELECT contract_id,
             MAX(CASE WHEN settled_date IS NULL
                            OR settled_date >= date_add(due_date, 5)
                      THEN 1 ELSE 0 END) AS first_payment_default
      FROM {fq_table("installment")}
      WHERE installment_no = 1
        AND date_add(due_date, 5) <= DATE'{AS_OF_DATE}'
      GROUP BY contract_id
    )
    SELECT
      CASE WHEN a.promotion_code = 'ZERO_SMARTPHONE_2026'
           THEN '0% smartphone promotion'
           ELSE 'other originations'
      END AS cohort,
      COUNT(*) AS contracts,
      ROUND(AVG(COALESCE(f.first_payment_default, 0)) * 100, 2) AS first_payment_default_pct
    FROM {fq_table("credit_contract")} c
    JOIN {fq_table("loan_application")} a USING (application_id)
    JOIN first_installment f USING (contract_id)
    GROUP BY 1
    ORDER BY 1
    """
)

display(story_check)

story_gates = spark.sql(
    f"""
    WITH first_installment AS (
      SELECT contract_id,
             MAX(CASE WHEN settled_date IS NULL
                            OR settled_date >= date_add(due_date, 5)
                      THEN 1 ELSE 0 END) AS first_payment_default
      FROM {fq_table("installment")}
      WHERE installment_no = 1
        AND date_add(due_date, 5) <= DATE'{AS_OF_DATE}'
      GROUP BY contract_id
    ),
    eligible_contracts AS (
      SELECT
        a.application_id,
        a.store_id,
        a.sales_associate_id,
        a.promotion_code,
        f.first_payment_default
      FROM {fq_table("credit_contract")} c
      JOIN {fq_table("loan_application")} a USING (application_id)
      JOIN first_installment f USING (contract_id)
    ),
    store_volume AS (
      SELECT store_id, COUNT(*) AS applications
      FROM {fq_table("loan_application")}
      WHERE store_id IS NOT NULL
      GROUP BY store_id
    ),
    ranked_store_volume AS (
      SELECT
        store_id,
        applications,
        ROW_NUMBER() OVER (ORDER BY applications DESC, store_id) AS store_rank,
        COUNT(*) OVER () AS store_count
      FROM store_volume
    ),
    store_concentration AS (
      SELECT
        SUM(CASE WHEN store_rank <= CEIL(store_count * 0.20)
                 THEN applications ELSE 0 END) * 1.0 / SUM(applications) AS top_20_share
      FROM ranked_store_volume
    ),
    cohort_rates AS (
      SELECT
        AVG(CASE WHEN promotion_code = 'ZERO_SMARTPHONE_2026'
                 THEN first_payment_default END) AS promo_fpd,
        AVG(CASE WHEN promotion_code <> 'ZERO_SMARTPHONE_2026'
                      OR promotion_code IS NULL
                 THEN first_payment_default END) AS other_fpd
      FROM eligible_contracts
    ),
    promo_performance AS (
      SELECT
        SUM(CASE WHEN store_id <= {PROMO_HOTSPOT_COUNT}
                 THEN first_payment_default ELSE 0 END) * 1.0
          / NULLIF(SUM(first_payment_default), 0) AS hotspot_default_share
      FROM eligible_contracts
      WHERE promotion_code = 'ZERO_SMARTPHONE_2026'
    ),
    associate_repetition AS (
      SELECT MAX(contract_count) AS max_contracts_per_associate
      FROM (
        SELECT
          store_id,
          sales_associate_id,
          COUNT(*) AS contract_count
        FROM eligible_contracts
        WHERE promotion_code = 'ZERO_SMARTPHONE_2026'
        GROUP BY store_id, sales_associate_id
      )
    ),
    designated_associate_performance AS (
      SELECT
        COUNT(CASE WHEN sales_associate_id LIKE '%-01' THEN 1 END) AS designated_contracts,
        COUNT(CASE WHEN sales_associate_id NOT LIKE '%-01' THEN 1 END) AS peer_contracts,
        AVG(CASE WHEN sales_associate_id LIKE '%-01'
                 THEN first_payment_default END) AS designated_fpd,
        AVG(CASE WHEN sales_associate_id NOT LIKE '%-01'
                 THEN first_payment_default END) AS peer_fpd
      FROM eligible_contracts
      WHERE promotion_code = 'ZERO_SMARTPHONE_2026'
        AND store_id <= {PROMO_HOTSPOT_COUNT}
    )
    SELECT 'top_20_store_concentration' AS check_name,
           CASE WHEN top_20_share >= 0.75 THEN 0 ELSE 1 END AS failure_count
    FROM store_concentration
    UNION ALL
    SELECT 'promo_fpd_gap',
           CASE WHEN promo_fpd >= other_fpd + 0.05 THEN 0 ELSE 1 END
    FROM cohort_rates
    UNION ALL
    SELECT 'promo_hotspot_default_share',
           CASE WHEN hotspot_default_share >= 0.50 THEN 0 ELSE 1 END
    FROM promo_performance
    UNION ALL
    SELECT 'repeated_store_associate_pairs',
           CASE WHEN max_contracts_per_associate >= 5 THEN 0 ELSE 1 END
    FROM associate_repetition
    UNION ALL
    SELECT 'promo_associate_fpd_lift',
           CASE WHEN designated_contracts >= 20
                     AND peer_contracts >= 80
                     AND designated_fpd >= peer_fpd + 0.10
                THEN 0 ELSE 1 END
    FROM designated_associate_performance
    """
)

display(story_gates.orderBy("check_name"))

if story_gates.filter(F.col("failure_count") > 0).count() > 0:
    raise RuntimeError(
        "Workshop-story validation failed in the isolated build schema; "
        "the target workshop tables were not published."
    )

# COMMAND ----------
# MAGIC %md
# MAGIC ## Publish the validated release
# MAGIC
# MAGIC Each target table is replaced atomically from the validated build. If
# MAGIC the multi-table publish fails, completed replacements are restored to
# MAGIC their prior Delta versions (or dropped if this was the first release).

# COMMAND ----------

def publish_validated_release() -> None:
    target_snapshots: dict[str, tuple[bool, int | None]] = {}
    for table_name in TABLE_NAMES:
        if table_exists(SCHEMA, table_name):
            prior_version = (
                spark.sql(f"DESCRIBE HISTORY {target_table(table_name)} LIMIT 1")
                .select("version")
                .first()["version"]
            )
            target_snapshots[table_name] = (True, prior_version)
        else:
            target_snapshots[table_name] = (False, None)

    published_tables: list[str] = []
    try:
        for table_name in TABLE_NAMES:
            create_verb = (
                "CREATE OR REPLACE TABLE" if WRITE_MODE == "overwrite" else "CREATE TABLE"
            )
            spark.sql(
                f"{create_verb} {target_table(table_name)} "
                f"DEEP CLONE {fq_table(table_name)}"
            )
            published_tables.append(table_name)
            escaped_description = TABLE_DESCRIPTIONS[table_name].replace("'", "''")
            spark.sql(
                f"COMMENT ON TABLE {target_table(table_name)} IS '{escaped_description}'"
            )
            spark.sql(
                f"""
                ALTER TABLE {target_table(table_name)}
                SET TBLPROPERTIES (
                  'workshop.generator' = '{GENERATOR_NAME}',
                  'workshop.generator_version' = '{GENERATOR_VERSION}',
                  'workshop.master_seed' = '{MASTER_SEED}',
                  'workshop.as_of_date' = '{AS_OF_DATE}',
                  'workshop.scale' = '{SCALE}',
                  'workshop.run_id' = '{RUN_ID}',
                  'workshop.synthetic' = 'true'
                )
                """
            )

        publication_failures = []
        for table_name in TABLE_NAMES:
            detail = (
                spark.sql(f"DESCRIBE DETAIL {target_table(table_name)}")
                .select("format", "properties")
                .first()
            )
            properties = detail["properties"] or {}
            if (
                detail["format"].lower() != "delta"
                or properties.get("workshop.generator") != GENERATOR_NAME
                or properties.get("workshop.run_id") != RUN_ID
            ):
                publication_failures.append(table_name)

        if publication_failures:
            raise RuntimeError(
                "Publication gate found incomplete or mixed target tables: "
                + ", ".join(publication_failures)
            )
    except Exception as publication_error:
        rollback_failures = []
        for table_name in reversed(published_tables):
            existed_before, prior_version = target_snapshots[table_name]
            try:
                if existed_before:
                    spark.sql(
                        f"RESTORE TABLE {target_table(table_name)} "
                        f"TO VERSION AS OF {prior_version}"
                    )
                else:
                    spark.sql(f"DROP TABLE IF EXISTS {target_table(table_name)}")
            except PySparkException as rollback_error:
                rollback_failures.append(f"{table_name}: {rollback_error}")

        if rollback_failures:
            raise RuntimeError(
                "Publication failed and rollback was incomplete. Do not release the dataset. "
                + " | ".join(rollback_failures)
            ) from publication_error
        raise RuntimeError(
            "Publication failed; all completed target replacements were rolled back. "
            "The validated build schema was retained for diagnosis."
        ) from publication_error


PUBLICATION_LOCK_TABLE = f"{TARGET_NAMESPACE}.`_generator_publication_lock`"
try:
    spark.sql(
        f"""
        CREATE TABLE {PUBLICATION_LOCK_TABLE}
        USING DELTA
        TBLPROPERTIES ('workshop.generator' = '{GENERATOR_NAME}')
        AS SELECT
          '{RUN_ID}' AS run_id,
          current_timestamp() AS acquired_at
        """
    )
except PySparkException as lock_error:
    raise RuntimeError(
        f"Could not acquire publication lock {CATALOG}.{SCHEMA}._generator_publication_lock. "
        "Another generator may be publishing, or a prior interrupted run left a stale lock."
    ) from lock_error

try:
    publish_validated_release()
finally:
    spark.sql(f"DROP TABLE IF EXISTS {PUBLICATION_LOCK_TABLE}")

for table_name in TABLE_NAMES:
    spark.sql(f"DROP TABLE IF EXISTS {fq_table(table_name)}")
spark.sql(f"DROP SCHEMA {BUILD_NAMESPACE}")

print(
    f"SUCCESS: generated, validated, and published {CATALOG}.{SCHEMA} "
    f"with seed={MASTER_SEED}, as_of_date={AS_OF_DATE}, scale={SCALE}."
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Land the clean raw batch into `workshop_shared`
# MAGIC Clean daily batch (`batch_date = 2026-09-01`) only — the WARN/DROP/FAIL dirty batches are driven separately.

# COMMAND ----------

spark.sql("""
CREATE OR REPLACE TABLE hc_workshop.workshop_shared.lending_raw_loan_application AS
SELECT application_id, customer_id, product_id, store_id, application_channel_code,
       CAST(requested_amount AS DOUBLE) AS requested_amount, requested_tenor_months,
       CAST(declared_income_amount AS DOUBLE) AS declared_income_amount,
       CAST(underwriting_score AS DOUBLE) AS underwriting_score,
       promotion_code, item_category_code,
       CAST(financed_amount AS DOUBLE) AS financed_amount,
       DATE'2026-09-01' AS batch_date, current_timestamp() AS _ingested_at
FROM hc_workshop.core_lending.loan_application
""")
spark.sql("""
CREATE OR REPLACE TABLE hc_workshop.workshop_shared.lending_raw_credit_contract AS
SELECT contract_id, application_id, CAST(principal_amount AS DOUBLE) AS principal_amount, tenor_months,
       CAST(monthly_interest_rate_pct AS DOUBLE) AS monthly_interest_rate_pct, origination_date,
       DATE'2026-09-01' AS batch_date, current_timestamp() AS _ingested_at
FROM hc_workshop.core_lending.credit_contract
""")
spark.sql("""
CREATE OR REPLACE TABLE hc_workshop.workshop_shared.lending_raw_installment AS
SELECT installment_id, contract_id, installment_no, due_date,
       CAST(total_due_amount AS DOUBLE) AS total_due_amount, settled_date,
       DATE'2026-09-01' AS batch_date, current_timestamp() AS _ingested_at
FROM hc_workshop.core_lending.installment
""")
display(spark.sql("""
SELECT 'loan_application' AS tbl, COUNT(*) n FROM hc_workshop.workshop_shared.lending_raw_loan_application
UNION ALL SELECT 'credit_contract', COUNT(*) FROM hc_workshop.workshop_shared.lending_raw_credit_contract
UNION ALL SELECT 'installment', COUNT(*) FROM hc_workshop.workshop_shared.lending_raw_installment ORDER BY tbl
"""))
