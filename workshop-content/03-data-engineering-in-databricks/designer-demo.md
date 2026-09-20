# Optional extension — Lakeflow Designer (no-code) demo

**Audience:** facilitator-led demo (optionally hands-on). ~10 min core, +10 min stretch.
**Scenario role:** the *analyst self-service* counterpart to the code-based pipeline.

> **Before you demo — confirm live.** Lakeflow Designer is a fast-moving, UI-driven feature; its
> availability may require a preview to be enabled for your workspace, and menu/label details shift.
> Open Designer in the workshop workspace and click through Part A once before the session. The
> steps below are grounded in the current Databricks docs (links at the end) but the workspace is
> the source of truth. This is an **interactive no-code tool**, so this asset is a walkthrough, not
> runnable code — there is nothing to `import` or run headlessly.

## Why this demo, and where it fits

Participants have just built the FPD5 medallion the **engineer's** way: a Lakeflow Declarative
Pipeline authored in SQL, with Expectations, a Job, and a quality gate. **Lakeflow Designer is the
same platform seen from the analyst's chair** — a visual, no-code, AI-native canvas where a risk or
marketing analyst at Unicorn Finance builds and schedules their own governed data prep **without
writing SQL and without waiting on the engineering team**.

The point to make: *governed self-service.* The analyst reads the **same Unity Catalog data**, every
operator is **backed by generated code** you can inspect, the output is **governed by Unity Catalog**,
and the prep is **schedulable to production** (Git, Jobs, bundles) — it is not a throwaway spreadsheet.

**Reach for Designer when:** an analyst needs to shape or aggregate governed data themselves, iterate
visually, and preview results row-by-row. **Reach for the code pipeline when:** you need
streaming/incremental ingest, the full Expectation tiers on a medallion, and engineer-owned,
version-controlled transformation logic. Same lakehouse, same governance — different authoring surface.

## Prerequisites

- Lakeflow Designer enabled in the workshop workspace (confirm — may be a preview).
- The existing Section 03 datasets already exist (built by `facilitator-setup.sql` and the pipeline):
  - Raw landing: `hc_workshop.workshop_shared.lending_raw_{installment, credit_contract, loan_application}`
  - Dimensions: `hc_workshop.core_lending.{loan_product, customer, retail_location}`
  - Governed gold (from the code pipeline): `hc_workshop.de_<user_id>.fpd_origination`
  - Catalog is `hc_workshop`.
- `USE CATALOG` + `SELECT` on those schemas, and `CREATE` on a target schema the analyst owns.

## Operator quick-reference (what's on the canvas)

A **visual data prep** is a graph of **operators** producing a result. The ones this demo uses:

| Operator | Purpose |
|---|---|
| **Source** | Read an existing Unity Catalog table (or ingest a new source) |
| **Join** | Combine datasets on matching keys |
| **Filter** | Split rows by a condition into **Included** / **Excluded** outputs (Excluded = quarantine) |
| **Guardrails** | Validate data (not-null, unique, regex, expressions) with a failure mode: **warn-and-continue**, **warn-and-block**, or **fail workflow** |
| **Prepare** | Derived/calculated columns via a **Formula** (natural language or SQL), type casts, text cleanup |
| **Aggregate** | Group and summarize (SUM, AVG, COUNT, …) |
| **Output** | Materialize to a UC **table**, **materialized view**, or file (choose catalog/schema, name, write mode) |

Throughout, the **Genie Code** assistant turns a natural-language description into operators — the
same natural-language authoring participants saw in the Section 06 Genie Code lab, now applied to a pipeline.

## Data-quality: the bridge to Expectations

Designer expresses the **same three quality intents** participants just learned as Expectation tiers —
so this is a reinforcement, not a new concept:

| Intent | Code pipeline (Expectation) | Designer (no-code) |
|---|---|---|
| Record the violation, keep the row | bare `EXPECT` → **WARN** | **Guardrails → warn-and-continue** |
| Quarantine the bad row | `ON VIOLATION DROP ROW` | **Filter →** route to the **Excluded** output (or **Guardrails → warn-and-block**) |
| Halt on corruption | `ON VIOLATION FAIL UPDATE` | **Guardrails → fail workflow** |

Same rule as the code section still holds: **never gate settlement timing** — early/on-time/late/unsettled
is the FPD5 *outcome*, not a defect.

## Part A — Core demo: cohort FPD5 metrics on the governed gold (no code)

*The realistic pattern: the analyst builds a metric view on top of the layer engineering already governs.*

1. **New prep.** Click **+** in the sidebar → **Visual data prep**.
2. **Source.** Click **Select source operator** → **Select an existing table** → choose
   `hc_workshop.de_<user_id>.fpd_origination` (the gold the code pipeline produced). It lands on the canvas.
3. **Aggregate — via Genie Code.** Open the **Genie Code** prompt and type:
   > *"Group by the origination month (truncate origination_date to month) and promotion_cohort. Count the contracts, and compute the FPD5 rate as the average of fpd5_flag times 100, rounded to 2 decimals. Name the columns eligible_contracts and fpd5_rate_pct."*

   Genie Code adds a **Prepare** (month) + **Aggregate** operator. (Or add **Aggregate** manually: group by `promotion_cohort` and a month column, `COUNT(*)` and `AVG(fpd5_flag)`.)
4. **Preview.** Select the Aggregate operator; the **output pane** shows the cohort rates. Reconcile aloud
   with Section 01 / expected-results: **0% smartphone promotion ≈ 42.3%**, **other ≈ 21.0%**, overall **25.14%**.
5. **Output.** Add an **Output** operator → type **Materialized view**, name `fpd_cohort_metrics_designer`,
   location `hc_workshop.de_<user_id>` (your delivery catalog + schema), write mode **Overwrite** → **Run**.
6. **Show the governance.** Open **inspect code** on any operator — the analyst's clicks are backed by
   real, UC-governed code. Click **Schedule** to show it can become a production job. **This is the moment:**
   *no code was written, yet the result is governed and productionizable.*

**Expected result:** one row per origination month × cohort, cohort rates matching the code pipeline's
`fpd_daily_metrics` — the analyst reproduced a governed metric view with zero SQL.

## Part B — Stretch: build eligible-origination FPD5 from raw, with Guardrails

*Show Designer can also do the heavier lift the code pipeline does — including data quality — no code.*

1. **Source** `hc_workshop.workshop_shared.lending_raw_installment`.
2. **Guardrails** (data quality — the Expectations parallel):
   - `contract_id` **not null** → **fail workflow** (broken key ≈ `FAIL UPDATE`).
   - `due_date` not null and `total_due_amount >= 0` → **warn-and-block** (≈ `DROP ROW`).
3. **Filter** to the eligible first installment — via **Genie Code**:
   > *"Keep only rows where installment_no = 1 and due_date plus 5 days is on or before 2026-09-01."*

   The **Excluded** output is the quarantine — point at it as the visual equivalent of a dropped row.
4. **Prepare** the label — via **Genie Code**:
   > *"Add a column fpd5_flag that is 1 when settled_date is null or settled_date is on or after due_date plus 5 days, otherwise 0."*
5. **Join** to `lending_raw_credit_contract`, then `lending_raw_loan_application`, then
   `core_lending.loan_product`; **Filter** `product_type_code` IN (`POS_INSTALLMENT`, `CASH_LOAN`).
6. **Output** a table `fpd_origination_designer` in `hc_workshop.de_<user_id>` → **Run**.

**Expected result:** ~**25,440** eligible contracts with an FPD5 label — the code pipeline's gold grain,
rebuilt on the canvas. Diff the two tables live to show they agree.

## Talking points

- **Governed self-service, not shadow IT.** Every operator is backed by inspectable code; the output is
  a UC-governed table/MV; the prep schedules to production. The analyst didn't fork the data — they built
  on the same governed lakehouse the engineers did.
- **One platform, two front doors.** Designer (analyst, visual/NL) and Declarative Pipelines (engineer,
  code) produce the same kind of governed asset. Teams pick the authoring surface, not a different stack.
- **Data quality is portable knowledge.** WARN / DROP / FAIL from the code section reappear as
  Guardrails modes + the Filter Excluded output — participants already know the decision framework.
- **Genie Code everywhere.** The same natural-language authoring from the Section 06 Genie Code lab now
  drives a pipeline — reinforce the through-line.

## When *not* to use Designer (be honest)

- **Streaming / incremental ingest** and the full medallion Expectation semantics are the code
  pipeline's strength — that's why Section 03's core is built there.
- Complex engineer-owned logic that must live in version control as the source of truth belongs in the
  declarative pipeline; Designer's generated code is great for analyst preps and hand-offs, less so as the
  canonical home for a team's core transformations.

## References (verified)

- What is Lakeflow Designer — https://docs.databricks.com/aws/en/designer/what-is-lakeflow-designer
- Create a visual data prep — https://docs.databricks.com/aws/en/designer/build-transformation
- Built-in operators (incl. **Guardrails**, **Filter**) — https://docs.databricks.com/aws/en/designer/built-in-operators
- Ingest data into Designer — https://docs.databricks.com/aws/en/designer/ingest-data
- Move a data prep to production — https://docs.databricks.com/aws/en/designer/production
