# Recommended slide outline — Section 01

Use eight concise slides. The slides establish decision frameworks; the workspace demonstrates execution and evidence.

## Slide 1 — The inherited question

**Title:** Did the 0% promotion create an FPD5 hotspot?

Show:

- Atlas Ridge has handed over the platform.
- Promotion volume increased.
- FPD5 appears concentrated by store and sales associate.
- FPD5 denominator: first installments that reached `due_date + 5 days` by `2026-09-01`.
- Elevated FPD5 is an investigation signal, not confirmed fraud.

Transition: "Before querying, choose compute from the workload."

## Slide 2 — Choose compute by workload

**Best as a slide:** participants need one stable comparison they can reuse.

| Workload | Default choice | Use a classic option when |
|---|---|---|
| Interactive Python and SQL notebook | Serverless notebook compute | R, RDDs, JARs, init scripts, or cluster-level customization is required |
| Automated notebook, Python, or wheel | Serverless jobs | The task needs unsupported customization or a classic-only task type |
| SQL, dashboard, BI, dbt, or Genie | Serverless SQL warehouse | Serverless is unavailable or custom networking requires a pro warehouse |

Call out:

- All-purpose compute is interactive; it is generally not the production-jobs default.
- Jobs compute is attached to an automated task, not kept running for ad hoc analysis.
- A SQL warehouse is SQL-optimized compute and can be serverless, pro, or classic.

## Slide 3 — Serverless versus classic is an operating-model choice

**Best as a slide:** compare responsibilities, not marketing labels.

| Question | Serverless | Classic |
|---|---|---|
| Who manages infrastructure and runtime upgrades? | Databricks manages the compute plane and runtime rollout | Shared responsibility; the customer selects configuration and runtime upgrade cadence |
| Startup and scaling | On demand and rapid | Provisioned; typically slower |
| Configuration freedom | Intentionally constrained | Greater node, networking, library, and Spark configuration control |
| Good default for this section | Notebook, jobs, and SQL warehouse workloads | Only a justified unsupported requirement |
| Operator still owns | Code, permissions, cost, quality, dependencies, and monitoring | The same, plus infrastructure choices |

Footnote: Pro SQL warehouses sit between serverless and classic for some networking and availability requirements.

Transition to live notebook.

## Slide 4 — One governed dataset, two notebook languages

**Keep this slide visual and brief.**

Flow:

```text
Unity Catalog tables
        ↓
PySpark profile → SQL transformation → temporary FPD5 view
        ↓
counts + rates + concentration evidence
```

Key message:

- Python and SQL use the same governed source.
- Choose the language for the task, not a separate data copy.
- Declare grain and denominator before calculating a rate.

Use the notebook—not the slide—to show code and results.

## Slide 5 — Open table formats make data changes operable

**Best as a slide plus one live Delta demonstration.**

| Capability | Delta Lake | Apache Iceberg |
|---|---|---|
| Open table format over object storage | Yes | Yes |
| ACID transactions and versioned metadata | Yes | Yes |
| Schema evolution and time travel | Yes | Yes |
| Databricks default format | Yes | No |
| Strong fit in this story | Native Databricks workloads and operational history | Cross-engine Iceberg interoperability |

Add three cautions:

- Schema evolution should be enabled deliberately per write.
- Time travel depends on retained logs and data files; it is not a backup guarantee.
- Choose a format from interoperability and feature requirements, not from a generic winner/loser comparison.

Transition to the team Delta table's before/after history.

## Slide 6 — A governed dashboard is more than charts

**Best as a slide before the prepared dashboard.**

```text
Metric View → dashboard dataset → draft → publish → viewers
      │                              │
      └ governed KPI definition      └ explicit data-permission mode
```

Compare:

- **Individual data permissions:** viewer's Unity Catalog permissions, row filters, and masks apply.
- **Share data permissions:** publisher's data permissions apply; useful for consumers without source grants, but the publishing identity becomes a control point.

Operator checklist:

- Dataset and metric owner
- SQL warehouse
- Publisher credential mode
- Dashboard ACL and published snapshot
- Reconciliation query

Use the workspace to add one widget, filter, verify, and publish.

## Slide 7 — Tune a SQL warehouse from symptoms

**Best as a slide:** prevent the common "make it bigger" response.

| Evidence | Likely issue | First actions |
|---|---|---|
| Sustained queued queries | Concurrency or capacity bound | Review maximum clusters, arrival patterns, and workload isolation |
| Bytes spilled or `DATA_SPILL` | One query exceeds available memory | Reduce scanned/wide data, inspect joins and aggregations, then consider a larger size |
| Long fetching state | Client is slow or left a session open | Inspect and stop result fetching; fix client behavior |
| Long idle periods | Auto-stop does not match usage | Review auto-stop against interactive and scheduled demand |
| Poor pruning or very high read volume | Query or table-layout issue | Filter earlier, select fewer columns, inspect statistics and clustering |

Call out:

- Cluster **size** primarily helps individual-query resources.
- Maximum **clusters** primarily helps concurrency.
- Intelligent Workload Management automates serverless admission and scaling within configured bounds; operators still monitor service levels and spend.

Transition to SQL Warehouse Monitoring and Query Profile.

## Slide 8 — Semantics first, then Genie

**Best as a slide plus live question/SQL verification.**

```text
FPD5 source view
      ↓
Metric View
(fields, measures, comments, synonyms, formats)
      ↓
Dashboard + focused Genie Agent
      ↓
question → generated SQL → result → verified answer
```

Quality loop:

1. Start with a focused governed source.
2. Ask a real question.
3. Inspect generated SQL and results.
4. Classify the failure.
5. Change the smallest structured surface.
6. Rerun the affected and regression questions.
7. Keep, revise, or roll back.

Do not put a long Genie instruction prompt on the slide. Emphasize that Metric View definitions, descriptions, synonyms, categorical matching, and verified example query shapes are preferred to a broad rulebook.

## Keep off the slides

Use the live workspace or participant files for:

- Full SQL and Python cells.
- Exact FPD5 output values before the exercise.
- Dashboard construction details.
- Query Profile navigation.
- Metric View YAML.
- Generated Genie SQL and answers.
- Troubleshooting steps.

