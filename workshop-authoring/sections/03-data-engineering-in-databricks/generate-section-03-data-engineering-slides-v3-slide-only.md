# Final slide-only generation prompt — Data Engineering in Databricks

Create the visible presentation slides for the **Data Engineering in Databricks** section (~2 hours, mostly hands-on).

This prompt intentionally covers only the portions carried on **slides** — the reusable **decision frameworks**. The pipeline build, the Expectations dirty-batch demo, the Job, and event-log / lineage navigation are delivered live in the workspace, not on slides. Several slides are best shown **at the matching hands-on transition** rather than all up front.

## Source authority

Resolve conflicts in this order:

1. `../../../workshop-content/03-data-engineering-in-databricks/facilitator-guide.md`
2. `../../../workshop-content/03-data-engineering-in-databricks/participant-pipeline.sql`
3. `../../../workshop-content/03-data-engineering-in-databricks/slide-outline.md`
4. `drafts/generate-section-03-data-engineering-slides-v2-content-first.md`
5. `../../../workshop-content/03-data-engineering-in-databricks/{README.md, job-quality-gate.py, expected-results.md}`
6. `../../../participant-materials/unicorn-finance-workshop-scenario.md`
7. `../../agenda/workshop-agenda.md`

Implemented workshop behavior is more authoritative than broad agenda language.

## Delivery contract

Generate approximately **seven concise slides** carrying the decision frameworks. Keep them tight and move to the workspace quickly. Suggested placement (confirm exact minute windows against `facilitator-guide.md`):

| Slide | Moment in the section |
|---|---|
| 1 — One-off query → reliable pipeline | Opening |
| 2 — The medallion | Opening |
| 3 — Streaming Table vs Materialized View | Before building the pipeline |
| 4 — Expectations: WARN / DROP / FAIL | Before the silver build; return after the dirty-batch demo |
| 5 — Pipeline vs Job | Before building the Job |
| 6 — Observability | With the live event log / run monitoring |
| 7 — Operational handover | Closing checkpoint |

Slides 5–7 are best shown at the matching hands-on transition. Do not create slides for the pipeline SQL, the Job JSON, event-log navigation, or the dirty-batch mechanics — those are live.

## Audience and role

- The real audience is Home Credit Philippines, with basic SQL and Python familiarity.
- Participants act as Unicorn Finance's internal data team after Atlas Ridge Consulting hands over an inherited Databricks platform.
- Here they **operationalize** the inherited FPD5 analysis into a governed, monitored, scheduled pipeline — not merely run prepared code.
- Unicorn Finance, Atlas Ridge, Nova Mobile, and all workshop records are fictional or synthetic.

## Visible-slide content

### Slide 1 — From one-off query to reliable pipeline
- Section 01 queried `core_lending` by hand; Section 06 modelled it. Both assume the data is fresh, correct, and monitored.
- We rebuild the FPD5 layer as a governed, quality-gated, scheduled pipeline.
- Four handover questions: layers & source of truth · where quality is enforced · schedule / gate / alert · who owns it.

### Slide 2 — The medallion: bronze → silver → gold
- `landing (raw feeds) → BRONZE ingest (as-is) → SILVER validate & conform (Expectations here) → GOLD business layer (consumers trust this)`.
- Bronze = faithful raw ingest, no logic. Silver = validated / conformed. Gold = the layer dashboards and models read.
- Consumers read **gold**, never bronze. Our gold `fpd_origination` is the same FPD5 layer Section 01 analysed.

### Slide 3 — Streaming Table vs Materialized View
| | Streaming Table | Materialized View |
|---|---|---|
| Processes | New rows incrementally (append-only source) | Full recompute of a query |
| Use for | Bronze ingest, silver cleaning | Gold aggregates & joins (`fpd_origination`, `fpd_daily_metrics`) |
| Cost shape | Proportional to new data | Proportional to the whole result |
- Choose incremental for feeds, recompute for derived tables — not a generic winner.

### Slide 4 — Expectations: WARN, DROP, FAIL (choose by consequence)
| Tier | Meaning | Use when | FPD5 example |
|---|---|---|---|
| `WARN` (bare `EXPECT`) | Record the violation, keep the row | Suspicious but usable | Extreme loan-to-income |
| `DROP ROW` | Quarantine the row | Impossible value you must not analyse | Negative amount, missing due date, zero income |
| `FAIL UPDATE` | Halt the pipeline | Corruption that must never propagate | Null `contract_id` (broken key) |
- **Crucial:** settlement timing is **never** an Expectation — early / on-time / late / unsettled is the FPD5 *outcome we measure*, not a data defect. Gating it silently deletes good data.

### Slide 5 — Pipeline vs Job: transformation vs orchestration
- `Pipeline = the transformation + quality (bronze→silver→gold, Expectations)`.
- `Job (DAG) = schedule · parameters · quality gate · downstream tasks · retries · alerts`.
- The pipeline defines *what* the data is; the Job defines *when, in what order, and what happens on failure*. Our Job: `run_pipeline` → `quality_gate`, parameterized by `as_of_date`, on a paused schedule.

### Slide 6 — Observability: know the pipeline is healthy
- **Event log** — per-Expectation pass / drop / warn counts. **Run monitoring** — run timeline, task durations, retries.
- **Lineage** — raw → bronze → silver → gold → consumer, automatically in Catalog Explorer. **Run summary** — a durable `fpd_run_summary` row per run.
- The **failure alert** is the tripwire — nobody watches a green pipeline; they get paged on a red one.

### Slide 7 — The operational handover (the real deliverable)
- **Pipeline:** owner · source landing · quality thresholds · gold consumers.
- **Job:** schedule / SLA · parameters · gate threshold · alert destination.
- **On FAIL:** who is paged, and the two-step recovery — **fix the landing, then full refresh** (a `FAIL UPDATE` row persists in the bronze stream; an incremental re-run re-fails).
- Checkpoint: each participant names one owner, one schedule, and one on-FAIL response.

## Recommended visuals

- The four-box medallion flow with a quality badge on silver.
- A two-column Streaming Table vs Materialized View comparison.
- A three-tier Expectation ladder keyed to the FPD5 examples.
- A pipeline-vs-Job split (what the data is · when it runs).

Do not fabricate product screenshots or workspace evidence.

## Presenter notes

- Restate the FPD5 definition and the as-of date `2026-09-01` briefly.
- Reinforce: consumers read gold; the Expectation tier follows the business consequence; settlement timing is never gated; serverless reduces infra effort but not ownership.
- Keep the 25,440 gold figure and the cohort rates (42.26% vs 21.03%) as validation checkpoints revealed **after** participants run the pipeline.

## Excluded from visible slides

- The full pipeline SQL and Expectation clauses.
- Exact layer row counts and the 25,440 gold figure before the exercise.
- The Job JSON and the quality-gate notebook.
- Event-log navigation, the lineage graph, the dirty-batch mechanics, and the reset.

## Output request

Return: (1) the proposed slide count and narrative; (2) concise visible slide content; (3) presenter notes per slide; (4) recommended visuals; (5) the placement of each slide across the section; (6) the transitions into the live pipeline / Job; (7) a coverage check confirming no excluded live-workspace topic became a visible slide.

Use a clean 16:9 workshop style. Keep slides tight — this is a hands-on section.
