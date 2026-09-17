# Databricks notebook source
# MAGIC %md
# MAGIC # Set up workshop Unity Catalog schemas
# MAGIC
# MAGIC Run this administrator notebook before the dataset generator. It creates the
# MAGIC catalog when needed and provisions the three schemas used throughout the workshop.
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
    LABS_SCHEMA: "Team-prefixed workshop tables, views, and registered models",
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
spark.sql(
    f"CREATE CATALOG IF NOT EXISTS {catalog_sql} "
    f"COMMENT 'Synthetic Unicorn Finance assets for the Databricks workshop'"
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
