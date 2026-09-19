# Databricks notebook source
# MAGIC %md
# MAGIC # Facilitator demo — Diagnose access across Databricks
# MAGIC
# MAGIC **Purpose:** reproduce one controlled authorization failure and diagnose the failed layer.
# MAGIC
# MAGIC Run this notebook as the dedicated non-admin governance demo user on the workshop SQL warehouse. Do not run it as a workspace admin, metastore admin, catalog owner, or workshop participant.
# MAGIC
# MAGIC The notebook is read-only. An administrator applies the one temporary grant from a separate SQL editor by following `section-05-governance-demo-setup.sql`.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Confirm the identity and execution context
# MAGIC
# MAGIC Before looking at grants, confirm **who** is making the request and **where** it is running.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   current_user() AS active_identity,
# MAGIC   current_catalog() AS active_catalog,
# MAGIC   current_schema() AS active_schema,
# MAGIC   current_timestamp() AS observed_at;

# COMMAND ----------
# MAGIC %md
# MAGIC Say:
# MAGIC
# MAGIC > Access is evaluated for the active identity, not for the person who originally authored this notebook. A scheduled Job can use a different **Run as** identity, and a shared dashboard can use either viewer or publisher data permissions. Always identify the runtime principal before changing grants.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Inspect the three Unity Catalog gates
# MAGIC
# MAGIC Reading a table normally requires:
# MAGIC
# MAGIC 1. `USE CATALOG` on its catalog;
# MAGIC 2. `USE SCHEMA` on its schema; and
# MAGIC 3. an action privilege such as `SELECT` on the table.
# MAGIC
# MAGIC The restricted demo group was intentionally given the first and third privileges, but not the second.
# MAGIC
# MAGIC Use the object **Permissions** tab from the administrator session to inspect the complete direct and inherited grant set. A non-owner might see only their own grants.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Reproduce the intentional failure
# MAGIC
# MAGIC Ask the team to predict the outcome before running the cell.
# MAGIC
# MAGIC The identity can discover the catalog and has `SELECT` on the table. The query must still fail because it cannot traverse the parent schema.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   customer_id,
# MAGIC   customer_no,
# MAGIC   employment_type_code,
# MAGIC   customer_since_date
# MAGIC FROM hc_workshop.core_lending.customer
# MAGIC ORDER BY customer_id
# MAGIC LIMIT 10;

# COMMAND ----------
# MAGIC %md
# MAGIC Stop on the error. Capture:
# MAGIC
# MAGIC - active identity;
# MAGIC - fully qualified object name;
# MAGIC - attempted action;
# MAGIC - exact error and request ID, if present;
# MAGIC - notebook and SQL warehouse;
# MAGIC - direct and inherited grants on each parent.
# MAGIC
# MAGIC In the administrator session, open:
# MAGIC
# MAGIC **Catalog > hc_workshop > core_lending > Permissions**
# MAGIC
# MAGIC Confirm that the dedicated demo group is missing `USE SCHEMA`. Apply only that privilege using the prepared setup SQL. Do not grant `ALL PRIVILEGES`.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Rerun the identical request
# MAGIC
# MAGIC After the administrator grants `USE SCHEMA`, rerun this unchanged cell. Ten synthetic, non-sensitive fields should appear.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   customer_id,
# MAGIC   customer_no,
# MAGIC   employment_type_code,
# MAGIC   customer_since_date
# MAGIC FROM hc_workshop.core_lending.customer
# MAGIC ORDER BY customer_id
# MAGIC LIMIT 10;

# COMMAND ----------
# MAGIC %md
# MAGIC The repair worked because the request now passes all three gates:
# MAGIC
# MAGIC ```text
# MAGIC USE CATALOG → USE SCHEMA → SELECT
# MAGIC ```
# MAGIC
# MAGIC This does not prove that every row and value is unrestricted. Row filters and column masks are evaluated after object access succeeds and can legitimately change the result without producing a permission error.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Separate workspace access from data access
# MAGIC
# MAGIC The demo user could open this notebook and use its warehouse before the table query succeeded.
# MAGIC
# MAGIC - Notebook and SQL warehouse access are workspace-resource permissions.
# MAGIC - Table access is a Unity Catalog privilege.
# MAGIC - The runtime identity connects the two layers.
# MAGIC
# MAGIC A single workflow can therefore fail at more than one layer. Fix the first failed gate instead of broadening unrelated permissions.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Closing diagnostic
# MAGIC
# MAGIC Ask:
# MAGIC
# MAGIC > A user can open a notebook and query the table interactively, but its scheduled Job fails with `PERMISSION_DENIED`. What should we inspect first?
# MAGIC
# MAGIC Expected response: inspect the Job's **Run as** identity and that identity's Unity Catalog privileges before changing the user's grants.
# MAGIC
# MAGIC After the session, run the reset command in `section-05-governance-demo-setup.sql` so the scenario remains reproducible.
