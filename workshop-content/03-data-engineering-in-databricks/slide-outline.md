# Recommended slide outline — Section 03

Use seven concise slides. The slides carry the **decision frameworks**; the pipeline and Job carry the code, quality metrics, and lineage. This is a hands-on, 2-hour section — keep slides tight and move to the workspace quickly (Slides 5–7 are best shown at the matching hands-on transition).

## Slide 1 — From one-off query to reliable pipeline

**Title:** We found the FPD5 hotspot — now make its data trustworthy every day.

Show:

- Section 01 queried `core_lending` by hand; Section 06 modelled it. Both assume the data is fresh, correct, and monitored.
- The inherited pipeline is ad hoc. Here we make the FPD5 layer a governed, quality-gated, scheduled pipeline.
- Four handover questions: layers & source of truth · where quality is enforced · schedule/gate/alert · who owns it.

Transition: "First, the shape of a reliable pipeline — the medallion."

## Slide 2 — The medallion: bronze, silver, gold

**Best as a slide:** one mental model participants reuse all section.

```text
landing (raw feeds)  →  BRONZE ingest  →  SILVER validate & conform  →  GOLD business layer
                         (as-is)           (Expectations live here)      (consumers trust this)
```

- Bronze = faithful raw ingest, no logic. Silver = validated/conformed. Gold = the layer dashboards and models read.
- Consumers read **gold**, never bronze. Our gold `fpd_origination` is the same FPD5 layer Section 01 analysed.

Transition: "Two table types build these layers — pick by how the data arrives."

## Slide 3 — Streaming Table vs Materialized View

**Best as a slide:** a reusable choice.

| | Streaming Table | Materialized View |
|---|---|---|
| Processes | New rows incrementally (append-only source) | Full recompute of a query |
| Use for | Bronze ingest, silver cleaning | Gold aggregates and joins (`fpd_origination`, `fpd_daily_metrics`) |
| Cost shape | Proportional to new data | Proportional to the whole result |

Call out: choose incremental for feeds, recompute for derived tables — not a generic winner.

Transition: "Silver is where we enforce quality — and the tier is a business decision."

## Slide 4 — Expectations: WARN, DROP, FAIL

**Best as a slide:** choose the tier from the **consequence**, not by habit.

| Tier | Meaning | Use when | FPD5 example |
|---|---|---|---|
| `WARN` (bare EXPECT) | Record the violation, keep the row | Suspicious but usable | Extreme loan-to-income |
| `DROP ROW` | Quarantine the row | Impossible value you must not analyse | Negative amount, missing due date, zero income |
| `FAIL UPDATE` | Halt the pipeline | Corruption that must never propagate | Null `contract_id` (broken key) |

**Crucial:** settlement timing is **never** an Expectation — early / on-time / late / unsettled is the FPD5 *outcome we measure*, not a data defect. Gating it silently deletes good data.

Transition to the live pipeline; return here after the dirty-batch demo.

## Slide 5 — Pipeline vs Job: transformation vs orchestration

**Best as a slide before building the Job.**

```text
Pipeline  = the transformation + quality (bronze→silver→gold, Expectations)
Job (DAG) = schedule · parameters · quality gate · downstream tasks · retries · alerts
```

- The pipeline defines *what* the data is; the Job defines *when, in what order, and what happens on failure*.
- Our Job: `run_pipeline` → `quality_gate` (fails and alerts if drops breach a threshold), parameterized by `as_of_date`, on a schedule.

Transition to Workflows to build the Job.

## Slide 6 — Observability: know the pipeline is healthy

**Best as a slide plus the live event log and run monitoring.**

- **Event log** — per-Expectation pass / drop / warn counts (the quality metrics).
- **Run monitoring** — Job run timeline, task durations, retries; pipeline update history.
- **Lineage** — raw → bronze → silver → gold → consumer, automatically in Catalog Explorer.
- **Run summary** — a durable `fpd_run_summary` row per run (eligible count, FPD5 rate, drop rate).
- The **failure alert** is the tripwire — nobody watches a green pipeline; they get paged on a red one.

## Slide 7 — The operational handover

**Best as a slide:** the section's real deliverable.

- **Pipeline:** owner, source landing, quality thresholds, gold consumers.
- **Job:** schedule/SLA, parameters, gate threshold, alert destination.
- **Observability:** event log, run summary, lineage, alert owner.
- **On FAIL:** who is paged, and the two-step recovery (fix the landing, full refresh).

Checkpoint: each participant names one owner, one schedule, and one on-FAIL response.

## Keep off the slides

Use the workspace or participant files for:

- The full pipeline SQL and Expectation clauses.
- Exact layer row counts and the 25,440 gold figure before the exercise.
- The Job JSON and the quality-gate notebook.
- Event-log navigation and the lineage graph.
- The dirty-batch mechanics and the reset.
