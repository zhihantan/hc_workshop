# Databricks notebook source
# MAGIC %md
# MAGIC # Investigate an access incident
# MAGIC
# MAGIC A Unicorn Finance risk analyst can find the trusted FPD5 analysis under **Consumer Lending > Origination Risk**, but cannot query it.
# MAGIC
# MAGIC We need to identify the executing identity, locate the first failed authorization gate, apply the narrowest approved repair, and verify the unchanged request.
# MAGIC
# MAGIC All workshop data and identities are fictional or synthetic.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Identify who is making the request
# MAGIC
# MAGIC Permissions are evaluated for the identity that executes the request. Confirm that identity before inspecting or changing any grants.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   current_user() AS runtime_principal,
# MAGIC   current_catalog() AS current_catalog,
# MAGIC   current_schema() AS current_schema,
# MAGIC   current_timestamp() AS observed_at;

# COMMAND ----------
# MAGIC %md
# MAGIC **Interpretation**
# MAGIC
# MAGIC Record the runtime principal and execution context in your participant guide. Opening a notebook as one user does not prove that every interactive or scheduled workload runs as that same identity.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Trace the governed read path
# MAGIC
# MAGIC Reading the trusted view requires all three Unity Catalog privileges:
# MAGIC
# MAGIC ```text
# MAGIC USE CATALOG → USE SCHEMA → SELECT
# MAGIC ```
# MAGIC
# MAGIC `BROWSE` can make the asset discoverable without granting access to its rows. Before running the query, record which gates you believe have already passed and predict whether the read will succeed.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Run the analyst's request
# MAGIC
# MAGIC The query displays ten synthetic rows only to test access. It does not validate the full FPD5 population, denominator, or business definition.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   application_id,
# MAGIC   contract_id,
# MAGIC   origination_date,
# MAGIC   promotion_cohort,
# MAGIC   fpd5_flag
# MAGIC FROM hc_workshop.workshop_shared.fpd_analysis
# MAGIC ORDER BY contract_id
# MAGIC LIMIT 10;

# COMMAND ----------
# MAGIC %md
# MAGIC **Interpretation**
# MAGIC
# MAGIC Stop at the error. Record the exact message, request ID if present, fully qualified object, requested action, and first failed gate. Distinguish direct grants, parent-securable inheritance, and access obtained through group membership before proposing a repair.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Verify the approved repair
# MAGIC
# MAGIC After the administrator applies the one missing privilege, rerun the analyst's request unchanged. Keeping the identity, compute, object, and SQL constant isolates whether that privilege was the cause.

# COMMAND ----------
# MAGIC %sql
# MAGIC SELECT
# MAGIC   application_id,
# MAGIC   contract_id,
# MAGIC   origination_date,
# MAGIC   promotion_cohort,
# MAGIC   fpd5_flag
# MAGIC FROM hc_workshop.workshop_shared.fpd_analysis
# MAGIC ORDER BY contract_id
# MAGIC LIMIT 10;

# COMMAND ----------
# MAGIC %md
# MAGIC **Interpretation**
# MAGIC
# MAGIC A successful result proves that the request now passes the notebook, warehouse, runtime-identity, catalog, schema, and view gates used in this test.
# MAGIC
# MAGIC It does not prove that every row is visible, that no row filter or column mask applies, or that the business definition is correct. Those questions require separate evidence.

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Complete the operational handover
# MAGIC
# MAGIC Use your participant guide to record:
# MAGIC
# MAGIC - the runtime principal and failed gate;
# MAGIC - the exact evidence and narrow repair;
# MAGIC - how the unchanged request verified the repair;
# MAGIC - downstream assets visible in lineage;
# MAGIC - what Domain placement proves and does not prove;
# MAGIC - one owner, risk, and recovery action.
