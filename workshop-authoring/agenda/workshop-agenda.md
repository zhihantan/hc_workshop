# Databricks Enablement — Home Credit Philippines

**Updated at:** 2026-09-16

*The first and only full-day workshop is confirmed for 22 September 2026; this is not workshop 1 of 3 or an open scheduling window.*

**22 September 2026 (Tuesday) · Full day · Face-to-face at Ore, 14F**

---

## Workshop scenario

Hands-on exercises use **Unicorn Finance Philippines**, a fictional consumer lender taking over an inherited Databricks lakehouse. All workshop records are synthetic and do not represent Home Credit production data or systems.

---

### Pre-requisites

- Basic familiarity with SQL and Python
- Sign up for [Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition) to explore the platform hands-on (you can use your personal email)
- Create a free [Databricks Academy](https://www.databricks.com/learn) account using your **corporate email**
- Complete the **"Databricks Fundamentals"** self-paced path (~1 hour)

---



## Morning



### 9:00 AM – 9:30 AM: Introduction to Databricks

- Understanding the Databricks Data Intelligence Platform and how it fits together
- Navigating the workspace: notebooks, SQL editor, Catalog Explorer, and dashboards
- Governing all data and AI assets from one place with Unity Catalog

**Getting started**: [Databricks overview & tutorials](https://learn.microsoft.com/en-us/azure/databricks/getting-started/) · [Free Databricks training](https://learn.microsoft.com/en-us/azure/databricks/getting-started/free-training/)

---



### 9:45 AM – 11:15 AM: Data Analysis in Databricks (1.5h)

- Framing the Nova Mobile promotion and the governed FPD5 definition
- Distinguishing notebook compute, Jobs compute, and SQL warehouses by workload
- Exploring application context with Python and SQL, then building the eligible FPD5 population
- Comparing cohorts and investigating store, associate, or regional concentration without making causal claims
- Persisting the investigation with Delta Lake and inspecting schema and transaction history
- Reconciling the notebook with a governed Metric View and prepared AI/BI Dashboard
- Creating and validating a private Genie Agent grounded only in the Metric View
- Inspecting dashboard- and Agent-generated SQL with Query History and Query Profile

**Recommended pre-reading**: [Get Started with SQL Analytics and BI on Databricks](https://customer-academy.databricks.com/learn/courses/3347/get-started-with-sql-analytics-and-bi-on-databricks)

---



### 11:15 AM – 12:15 PM: Generative AI in Databricks (1h)

- Using Genie Code to explain inherited governed SQL before changing it
- Extending the FPD5 investigation to regional grain and reconciling generated results
- Diagnosing and repairing an inherited PySpark denominator bug with executable checks
- Reviewing `/optimize` and `/doc` suggestions without accepting unsupported claims
- Demo: generating and validating an unpublished AI/BI Dashboard draft with Genie Code
- Optional if time: improving the participant's private Section 01 Genie Agent and regression-testing it

**Recommended pre-reading**: [Genie overview](https://learn.microsoft.com/en-us/azure/databricks/genie/)

---



### 12:15 PM – 1:15 PM: Lunch Break

---



## Afternoon



### 1:20 PM – 3:20 PM: Data Engineering in Databricks (2h)

- Scheduling and orchestrating workflows with Databricks Jobs (DAGs, parameterization, monitoring, alerts)
- Building data pipelines declaratively with Lakeflow Pipelines: Streaming Tables, Materialized Views, and the medallion architecture
- Building pipelines visually with the low-code Lakeflow Designer
- Enforcing data quality with Expectations (WARN / DROP ROW / FAIL)
- Ingesting from SaaS sources with Lakeflow Connect (managed connectors)
- Monitoring pipeline health and observability

**Recommended pre-reading**: [Get Started with Databricks for Data Engineering](https://customer-academy.databricks.com/learn/courses/2469/get-started-with-databricks-for-data-engineering)

---



### 3:20 PM – 3:50 PM: Governance and Access Control in Databricks (30 min)

- Tracing the authorization path across notebook access, SQL warehouse access, runtime identity, and Unity Catalog
- Diagnosing a controlled missing-`USE SCHEMA` failure through `USE CATALOG` → `USE SCHEMA` → `SELECT`
- Applying the narrowest repair from a separate administrator session and verifying the unchanged request
- Inspecting direct, inherited, and group-derived access evidence in Catalog Explorer
- Using table- and column-level lineage to identify downstream assets that require retesting
- Comparing technical governance in Catalog Explorer with business discovery in a prepared Discover Domain, when available
- Completing an incident handover with the failed gate, evidence, repair, owner, risk, and recovery action

**Recommended pre-reading**: [Get Started with Data Governance on Databricks](https://customer-academy.databricks.com/learn/courses/4677/get-started-with-data-governance-on-databricks)

---



### 4 PM – 5 PM: Introduction to Machine Learning in Databricks (1h)

- Tracking and comparing experiments with MLflow (autologging, parameters, metrics, artifacts)
- Managing model lifecycle with the Model Registry in Unity Catalog (versioning, aliases, lineage)
- Engineering and serving features at low latency with the Feature Store and Online Feature Stores
- Deploying models as REST endpoints with Model Serving (serverless autoscaling, CPU/GPU)
- Running inference at scale with batch and SQL-native AI functions
- Monitoring model performance with data profiling, drift detection, and inference tables

**Recommended pre-reading**: [Get Started with Databricks for Machine Learning](https://customer-academy.databricks.com/learn/courses/2460/get-started-with-databricks-for-machine-learning)

---



## Resources

- **Docs**: [https://learn.microsoft.com/en-us/azure/databricks/](https://learn.microsoft.com/en-us/azure/databricks/)
- **Community**: [https://community.databricks.com/](https://community.databricks.com/)
