-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Governance facilitator setup — restricted access scenario
-- MAGIC
-- MAGIC This notebook prepares a dedicated group for the Governance and Access Control demonstration.
-- MAGIC
-- MAGIC Before running any statement:
-- MAGIC
-- MAGIC 1. Create a dedicated account group and non-admin demo user.
-- MAGIC 2. Replace every instance of `<governance-demo-group>` below with that group.
-- MAGIC 3. Confirm the user is **not** a member of the workshop participant group or another group with broader access to `hc_workshop`.
-- MAGIC 4. Attach the workshop SQL warehouse.
-- MAGIC
-- MAGIC **Do not select Run all.** The live grant and reset are separate facilitator actions.

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Prepare before the session
-- MAGIC
-- MAGIC The intentional state is:
-- MAGIC
-- MAGIC - the group can discover and traverse the catalog;
-- MAGIC - the group has `SELECT` on the target table;
-- MAGIC - the group does **not** have `USE SCHEMA` on `core_lending`.
-- MAGIC
-- MAGIC This isolates one missing prerequisite without changing participant access.

-- COMMAND ----------
GRANT BROWSE
ON CATALOG hc_workshop
TO `<governance-demo-group>`;

-- COMMAND ----------
GRANT USE CATALOG
ON CATALOG hc_workshop
TO `<governance-demo-group>`;

-- COMMAND ----------
GRANT SELECT
ON TABLE hc_workshop.core_lending.customer
TO `<governance-demo-group>`;

-- COMMAND ----------
REVOKE USE SCHEMA
ON SCHEMA hc_workshop.core_lending
FROM `<governance-demo-group>`;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC Inspect the prepared state. The schema result must not contain `USE SCHEMA` for the dedicated group.

-- COMMAND ----------
SHOW GRANTS `<governance-demo-group>`
ON CATALOG hc_workshop;

-- COMMAND ----------
SHOW GRANTS `<governance-demo-group>`
ON SCHEMA hc_workshop.core_lending;

-- COMMAND ----------
SHOW GRANTS `<governance-demo-group>`
ON TABLE hc_workshop.core_lending.customer;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Live repair — run only when prompted
-- MAGIC
-- MAGIC Run this single statement from the administrator session after the restricted query fails.

-- COMMAND ----------
-- GRANT USE SCHEMA
-- ON SCHEMA hc_workshop.core_lending
-- TO `<governance-demo-group>`;

-- COMMAND ----------
-- MAGIC %md
-- MAGIC ## Reset after rehearsal or delivery
-- MAGIC
-- MAGIC Run this single statement after the demonstration so the intentional failure is ready for the next rehearsal.

-- COMMAND ----------
-- REVOKE USE SCHEMA
-- ON SCHEMA hc_workshop.core_lending
-- FROM `<governance-demo-group>`;
