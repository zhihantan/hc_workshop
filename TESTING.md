# Workshop development testing

This document describes how workshop code is tested while it is being developed. It is an authoring workflow, not participant instructions.

## Test environment

- Workspace: `https://fevm-sean-development.cloud.databricks.com`
- Databricks CLI profile: `DEFAULT`
- Workspace Git folder: `/Workspace/Shared/hc_workshop`
- Workshop catalog: `hc_workshop`

Use the explicit `DEFAULT` profile for development commands even though it is also the configured CLI default.

## Development loop

### 1. Test Spark logic with Databricks Connect

Use Databricks Connect for the fast inner loop when developing DataFrame transformations, Spark SQL, schemas, joins, aggregations, and Delta writes.

Connect setup belongs in a temporary local development script, not in a participant notebook:

```python
from databricks.connect import DatabricksSession

spark = (
    DatabricksSession.builder
    .profile("DEFAULT")
    .serverless(True)
    .getOrCreate()
)
```

The local Python process is the Spark Connect client. Spark plans execute on serverless compute in the development workspace.

Prefer a fresh script run for repeatable checks. A long-lived Python or Jupyter process may be used when interactive state is useful, but results must not depend on state left by an earlier command.

### 2. Keep participant notebooks native

Participant notebooks use the `spark`, `dbutils`, widget, SQL-magic, and display facilities supplied by the Databricks notebook runtime. They must not initialize `DatabricksSession` or contain local profile configuration.

Databricks Connect validates Spark logic, but it does not fully validate notebook behavior such as:

- widget initialization and parameter handling;
- `%sql` and other notebook magic cells;
- `dbutils` calls;
- `display()` rendering;
- execution order and state shared between cells.

### 3. Validate the actual notebook in Databricks

After a coherent section is assembled:

1. Commit the local changes.
2. Pull them into `/Workspace/Shared/hc_workshop`.
3. Run the participant notebook cell by cell on serverless compute, following the participant path.
4. Confirm displayed results, created assets, expected failures, and recovery instructions.

An occasional serverless notebook job can provide a clean-state, top-to-bottom regression check. It supplements rather than replaces cell-by-cell validation because participants use the interactive notebook flow.

## Session state

- Python variables persist only while their Python process or notebook session remains alive.
- Spark temporary views and session configuration persist only for the associated Spark session.
- Re-running a standalone Connect script starts with fresh Python state and normally a new Spark session.
- Unity Catalog tables and cloud files persist independently of the client session.

Tests should create all required temporary state explicitly. They must not pass only because a previous interactive command created a variable or temporary view.

## Data safety

- Treat `hc_workshop.core_lending` as read-only.
- Write development artifacts only to the intended workshop lab or test location.
- Use a clearly isolated runner identity or test prefix when notebook parameters create participant-owned objects.
- Make cleanup explicit for persistent test tables.
- Never place workspace credentials, tokens, or user-specific authentication material in this repository.

## Evidence before marking a section ready

- Spark and SQL logic has been exercised against the development workspace.
- The actual notebook has passed the participant-style cell-by-cell flow from a clean session.
- Expected outputs match the section's `expected-results.md`.
- Persistent writes are limited to documented assets and reruns behave as documented.
- Notebook-specific features and error-recovery paths have been checked in the Databricks UI.
