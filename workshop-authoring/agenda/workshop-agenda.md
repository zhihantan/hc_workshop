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

- Choosing compute by workload: notebook compute, jobs compute, and SQL warehouses
- Understanding serverless versus classic operating models and Serverless, Pro, and Classic SQL warehouse types
- Exploring governed data with Python and SQL, then extending an inherited FPD5 investigation
- Persisting the investigation with Delta Lake and inspecting schema and transaction history
- Reusing a governed Metric View in an AI/BI Dashboard and private Genie Agent
- Inspecting the resulting SQL workload with Warehouse Monitoring, Query History, and Query Profile

**Recommended pre-reading**: [Get Started with SQL Analytics and BI on Databricks](https://customer-academy.databricks.com/learn/courses/3347/get-started-with-sql-analytics-and-bi-on-databricks)

---



### 11:15 AM – 12:15 PM: Generative AI in Databricks (1h)

- Accelerating development and analytics for technical users with Genie Code
- Understanding, extending, and repairing inherited SQL and PySpark with review and executable checks
- Supercharging coding assistants with AI Gateway and AI Toolkit
- Introduction to Genie and Genie One
- Demo: Ask natural-language questions about the analysis with Genie
- Optional if time: improving the participant-created Genie Agent with Genie Code and regression checks

**Recommended pre-reading**: [Genie overview](https://learn.microsoft.com/en-us/azure/databricks/genie/) · [AI Gateway overview](https://learn.microsoft.com/en-us/azure/databricks/ai-gateway/)

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

- Understanding the authorization layers: identities, workspace-resource permissions, runtime identity, and Unity Catalog
- Governing data and AI assets with Unity Catalog's three-level namespace, securables, inherited grants, and fine-grained policies
- Diagnosing access failures by tracing workspace access, compute access, and `USE CATALOG` → `USE SCHEMA` → object privileges
- Inspecting permissions and table- and column-level lineage in Catalog Explorer
- Organizing trusted data and workspace assets for business discovery with Domains and subdomains

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
