# Databricks notebook source
# MAGIC %md
# MAGIC # Section 03 — self-service setup: create the FPD5 pipeline + Job
# MAGIC
# MAGIC Run this notebook **once** to provision the Section 03 data-engineering assets in one shot — no UI clicking, no editing `job-definition.json` placeholders. It:
# MAGIC
# MAGIC 1. ensures your **target schema** exists (`<catalog>.de_<your_user_id>` by default);
# MAGIC 2. creates the **Lakeflow Declarative Pipeline (SDP)** from `participant-pipeline.sql`;
# MAGIC 3. creates the orchestrating **Job** — `run_pipeline` → `quality_gate` — wired to that pipeline (parameterized, paused schedule, failure alert), i.e. it materializes `job-definition.json` with the pipeline it just created.
# MAGIC
# MAGIC It is **idempotent**: if a pipeline/Job with the target name already exists, it reuses it instead of creating a duplicate.
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - The workshop **catalog exists** (default `hc_workshop`) and you can `CREATE SCHEMA` in it.
# MAGIC - `participant-pipeline` and `job-quality-gate` are imported in the workspace at the paths in the widgets.
# MAGIC - The shared landing is present (`workshop_shared.lending_raw_*`) — run the data-setup first if not.
# MAGIC - You may create a **serverless pipeline** and a **serverless Job**.

# COMMAND ----------
dbutils.widgets.text("catalog", "hc_workshop", "1. Workshop catalog")
dbutils.widgets.text("target_schema", "", "2. Pipeline target schema (blank = de_<your_user_id>)")
dbutils.widgets.text("pipeline_source_path", "/Shared/hc_workshop/workshop-content/03-data-engineering-in-databricks/participant-pipeline", "3. participant-pipeline notebook path")
dbutils.widgets.text("quality_gate_path", "/Shared/hc_workshop/workshop-content/03-data-engineering-in-databricks/job-quality-gate", "4. job-quality-gate notebook path")
dbutils.widgets.text("alert_email", "", "5. on_failure alert email (blank = you)")
dbutils.widgets.text("max_drop_pct", "5.0", "6. Quality-gate max installment drop %")
dbutils.widgets.text("as_of_date", "2026-09-01", "7. As-of date")
dbutils.widgets.dropdown("run_now", "false", ["false", "true"], "8. Trigger a first run after creating?")

# COMMAND ----------
import re
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
me = w.current_user.me().user_name
user_id = re.sub(r"[^A-Za-z0-9]", "_", me.split("@")[0]).lower()

CATALOG   = dbutils.widgets.get("catalog").strip()
SCHEMA    = dbutils.widgets.get("target_schema").strip() or f"de_{user_id}"
PIPE_SRC  = dbutils.widgets.get("pipeline_source_path").strip()
GATE_PATH = dbutils.widgets.get("quality_gate_path").strip()
EMAIL     = dbutils.widgets.get("alert_email").strip() or me
MAX_DROP  = dbutils.widgets.get("max_drop_pct").strip()
AS_OF     = dbutils.widgets.get("as_of_date").strip()
RUN_NOW   = dbutils.widgets.get("run_now") == "true"

PIPELINE_NAME = f"fpd5-medallion-{user_id}"
JOB_NAME      = f"fpd5-medallion-job-{user_id}"
print(f"catalog={CATALOG}  target schema={SCHEMA}  user={user_id}")
print(f"pipeline name='{PIPELINE_NAME}'  job name='{JOB_NAME}'  alert={EMAIL}")
print(f"pipeline source={PIPE_SRC}\nquality gate={GATE_PATH}")

# COMMAND ----------
# MAGIC %md ## 1. Ensure the target schema exists

# COMMAND ----------
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{CATALOG}`.`{SCHEMA}`")
print(f"Target schema ready: {CATALOG}.{SCHEMA}")

# COMMAND ----------
# MAGIC %md ## 2. Create (or reuse) the Lakeflow Declarative Pipeline
# MAGIC Serverless, `CURRENT` channel, ANSI SQL on — the same settings the workshop validated. The pipeline's source is `participant-pipeline.sql`; its tables land in `<catalog>.<target_schema>`.

# COMMAND ----------
from databricks.sdk.service.pipelines import PipelineLibrary, NotebookLibrary

existing_pipeline = next((p for p in w.pipelines.list_pipelines() if p.name == PIPELINE_NAME), None)
if existing_pipeline:
    pipeline_id = existing_pipeline.pipeline_id
    print(f"Reusing existing pipeline '{PIPELINE_NAME}': {pipeline_id}")
else:
    created = w.pipelines.create(
        name=PIPELINE_NAME,
        serverless=True,
        catalog=CATALOG,
        schema=SCHEMA,
        channel="CURRENT",
        development=True,
        continuous=False,
        configuration={"spark.sql.ansi.enabled": "true"},
        libraries=[PipelineLibrary(notebook=NotebookLibrary(path=PIPE_SRC))],
    )
    pipeline_id = created.pipeline_id
    print(f"Created pipeline '{PIPELINE_NAME}': {pipeline_id}")

# COMMAND ----------
# MAGIC %md ## 3. Create (or reuse) the orchestrating Job
# MAGIC DAG: `run_pipeline` (pipeline task) → `quality_gate` (notebook task). Parameterized by `as_of_date`, a **paused** daily schedule, and an `on_failure` email. Equivalent to `job-definition.json` with `<PIPELINE_ID>` filled in.

# COMMAND ----------
from databricks.sdk.service.jobs import (
    Task, PipelineTask, NotebookTask, TaskDependency,
    JobParameterDefinition, CronSchedule, JobEmailNotifications, PauseStatus,
)

existing_job = next((j for j in w.jobs.list() if j.settings and j.settings.name == JOB_NAME), None)
if existing_job:
    job_id = existing_job.job_id
    print(f"Reusing existing job '{JOB_NAME}': {job_id}")
else:
    created_job = w.jobs.create(
        name=JOB_NAME,
        tags={"workshop": "section-03-data-engineering"},
        parameters=[JobParameterDefinition(name="as_of_date", default=AS_OF)],
        tasks=[
            Task(
                task_key="run_pipeline",
                description="Refresh the FPD5 medallion (bronze -> silver + Expectations -> gold).",
                pipeline_task=PipelineTask(pipeline_id=pipeline_id, full_refresh=False),
            ),
            Task(
                task_key="quality_gate",
                description="Fail + alert if the installment drop rate breaches the threshold; else publish a run summary.",
                depends_on=[TaskDependency(task_key="run_pipeline")],
                notebook_task=NotebookTask(
                    notebook_path=GATE_PATH,
                    base_parameters={
                        "schema": SCHEMA,
                        "as_of_date": "{{job.parameters.as_of_date}}",
                        "max_drop_pct": MAX_DROP,
                    },
                ),
            ),
        ],
        schedule=CronSchedule(
            quartz_cron_expression="0 0 6 * * ?",
            timezone_id="Asia/Manila",
            pause_status=PauseStatus.PAUSED,
        ),
        email_notifications=JobEmailNotifications(on_failure=[EMAIL]),
        max_concurrent_runs=1,
    )
    job_id = created_job.job_id
    print(f"Created job '{JOB_NAME}': {job_id}")

# COMMAND ----------
# MAGIC %md ## 4. Links (and optional first run)

# COMMAND ----------
host = (w.config.host or "").rstrip("/")
print(f"Pipeline: {host}/pipelines/{pipeline_id}")
print(f"Job:      {host}/jobs/{job_id}")

if RUN_NOW:
    run = w.jobs.run_now(job_id=job_id)
    print(f"Triggered job run {run.run_id}: {host}/jobs/{job_id}/runs/{run.run_id}")
else:
    print("run_now=false — open the Job above and Run it (or set run_now=true and re-run this cell) to build the medallion the first time.")
