# Expected results — Generative AI in Databricks

Genie Code output can vary in wording, cell layout, SQL aliases, and visualization style. Validate the invariants below instead of expecting byte-for-byte generated code.

## Main analysis

### Explanation of inherited work

Genie Code should explain that the inherited query:

- returns one row per `promotion_cohort`;
- invokes three governed Metric View measures;
- uses eligible contracts as the FPD5 denominator;
- groups by every selected non-aggregate field through `GROUP BY ALL`;
- multiplies the ratio by 100 only for display.

Wording can vary, but an explanation that claims the query recalculates FPD5 from raw rows is incorrect.

### Source and safety

- The generated analytical SQL reads `hc_workshop.workshop_shared.fpd_metrics`.
- It uses the Metric View measures through `MEASURE(...)`.
- It does not rebuild FPD5 from raw application, contract, installment, or settlement columns.
- It contains no `CREATE`, `REPLACE`, `INSERT`, `UPDATE`, `DELETE`, or `MERGE`.

### Cohort comparison

On the standard workshop dataset:

- 0% smartphone promotion FPD5 rate: approximately **42.26%**.
- Other eligible originations FPD5 rate: approximately **21.03%**.
- The underlying Metric View returns rate ratios near `0.4226` and `0.2103`; multiplying by 100 is display conversion, not a different measure.

The eligible-contract and FPD5 counts must agree with the independent reference query in `participant-lab.py`.

## Dashboard showcase

The facilitator's unpublished dashboard draft should contain:

- KPI counters for eligible contracts, FPD5 contracts, and FPD5 rate;
- a promotion-cohort comparison;
- a five-store promotion ranking;
- a promotion-cohort filter;
- clear titles and percentage formatting.

For the store ranking:

- The result is filtered to `promotion_cohort = '0% smartphone promotion'`.
- Each row is one store, normally identified by `store_code` and `store_name`.
- The output includes eligible contracts, FPD5 contracts, and FPD5 rate.
- `HAVING MEASURE(eligible_contracts) >= 10` or equivalent is applied before ranking.
- The result is ordered by FPD5 rate descending and limited to five stores.

The dashboard values must reconcile with the notebook and Metric View. It remains unpublished and is deleted after the workshop.

## Participant regional extension

The regional result should:

- be filtered to the 0% smartphone promotion;
- contain one row per `region_code`;
- include governed eligible-contract, FPD5-contract, and FPD5-rate measures;
- exclude regions with fewer than 20 eligible contracts;
- sort by FPD5 rate descending;
- compare the highest-rate qualifying region with the overall promotion rate, not the all-contract rate.

On the standard workshop dataset, all six regions qualify:

- `REGION_VI`: 443 eligible, 239 FPD5, **53.95%**.
- `REGION_XI`: 243 eligible, 116 FPD5, **47.74%**.
- `NCR`: 1,832 eligible, 808 FPD5, **44.10%**.
- `REGION_III`: 473 eligible, 194 FPD5, **41.01%**.
- `REGION_IV_A`: 1,507 eligible, 595 FPD5, **39.48%**.
- `REGION_VII`: 429 eligible, 130 FPD5, **30.30%**.

The top qualifying region is `REGION_VI`, approximately **11.69 percentage points** above the overall promotion rate of 42.26%.

The narrative should describe a hotspot as a reason to investigate campaign execution, customer mix, operational processes, and data quality. It must not say the region, store, associate, or promotion caused default or committed fraud.

## Participant PySpark diagnosis and improvement

The inherited `build_cohort_validation` helper runs, but it is semantically wrong. It filters to `fpd5_flag = 1` before aggregation, so every retained contract appears in both the numerator and denominator and both cohorts report a 100% FPD5 rate.

An acceptable Genie Code repair:

- removes the pre-aggregation FPD5 filter;
- keeps one eligible source row per contract from `hc_workshop.workshop_shared.fpd_analysis`;
- calculates eligible contracts from the full grouped population;
- calculates FPD5 contracts from `fpd5_flag`;
- computes the rate from those two aggregates;
- remains read-only, uses built-in DataFrame expressions, and does not redefine how `fpd5_flag` is derived.

The repaired output should contain the same two cohorts as the Metric View and reconcile to approximately **42.26%** and **21.03%**. Lightweight checks should confirm:

- exactly two cohort rows are returned;
- eligible contracts are positive;
- FPD5 contracts never exceed eligible contracts;
- the two rates agree with the independent reference values within a small tolerance.

For `/optimize`:

- no change is an acceptable outcome when the query is already appropriate;
- any accepted change preserves the source, grain, threshold, measures, row counts, and rates;
- a generated suggestion alone is not evidence of improved performance.

For `/doc`, the added explanation should identify the regional grain, eligible-contract denominator, and 20-contract minimum.

## Optional individual Genie Agent iteration

Each participant continues with the independently named **Unicorn FPD5 Investigator — `<workspace_username>`** created in Section 01. It remains in the participant's user folder, is not shared with other participants, and uses only `fpd_metrics`.

After the Genie Code-assisted context update, the participant Agent's store-associate answer should:

- query `hc_workshop.workshop_shared.fpd_metrics`;
- filter to the 0% smartphone promotion;
- use governed `MEASURE(...)` expressions;
- group at store and sales-associate grain;
- apply at least 10 eligible contracts before ranking;
- show eligible contracts, FPD5 contracts, and FPD5 rate;
- state that results are observed through `2026-09-01`;
- describe hotspots as investigation signals rather than confirmed fraud.

The accepted change should be focused. It may add a concise instruction, improve metadata, or add verified example SQL, but it must not duplicate the FPD5 formula outside the Metric View.

In a fresh conversation, the cohort regression answer should remain approximately **42.26%** versus **21.03%**.

## Checkpoint answers

Participants should be able to state:

- **What became faster:** understanding inherited work, generating and iterating on analysis, semantic bug repair, documentation, optimization review, dashboard authoring, and—if attempted—implementing a Genie Agent requirement.
- **What remained with the user:** defining the outcome, selecting context, reviewing actions and diffs, validating results, and deciding whether an asset is ready to publish or share.
- **Reusable workflow:** context → concrete outcome → review → execution → independent validation.

## Troubleshooting

### Headline rates differ

Check that the generated cohort SQL uses only `fpd_metrics`, groups by `promotion_cohort`, invokes measures with `MEASURE(...)`, and has no extra date, product, store, or region filter. Then rerun the independent reference query.

### A rate appears as `0.4226` instead of `42.26%`

The measure is a ratio. Apply percentage formatting or multiply by 100 for a numeric percentage display. Do not multiply a value that has already been converted.

### The generated analysis rebuilds FPD5

Reject the plan and restate:

> Use only `hc_workshop.workshop_shared.fpd_metrics` and its governed measures. Do not reimplement the FPD5 formula from raw tables.

### The store or region ranking includes tiny groups

Ask Genie Code to put the denominator condition in `HAVING` at the grouped grain, then rerun and recheck the row counts.

### The generated chart sorts alphabetically

Ask Genie Code to sort the source result by FPD5 rate descending and preserve that order in the visualization.

### The comparison uses all contracts

Ask for a separate overall aggregate filtered to the promotion cohort, then compare the regional value with that result.

### Genie Code is unavailable

Use the facilitator's completed walkthrough in the demonstration account. The participant should still review the generated query against this file's invariants and identify one correction or approval decision.

### Dashboard authoring is unavailable

Use the completed unpublished facilitator draft. Reconcile its datasets, values, filters, and layout instead of attempting a live build.

### The optional participant Agent cannot be opened or edited

Confirm that Section 01 created the Agent in the participant's user folder, that the current user is its owner, and that the user has Databricks SQL access, `CAN USE` on the selected warehouse, and `SELECT` on `fpd_metrics`. If the issue cannot be resolved immediately, skip the optional extension; do not substitute a shared Agent.

### Genie Code proposes a second FPD5 formula

Reject it. Ask for a response-behavior instruction, metadata improvement, or verified example query that reuses the Metric View measures.

### The repaired PySpark result still shows 100%

Inspect the helper for a filter on `fpd5_flag` before `groupBy`. The full eligible population must reach the aggregation. Use `SUM(fpd5_flag)` for the numerator and the full contract count for the denominator.

### PySpark cannot read `fpd_analysis`

Confirm the notebook is attached to Serverless notebook compute or approved Unity Catalog-compatible all-purpose compute. Then confirm `USE CATALOG`, `USE SCHEMA`, and `SELECT` on `hc_workshop.workshop_shared.fpd_analysis`.

### The Agent was accidentally shared

Open **Share**, remove grants to other participants, the workshop group, or **All account users**, and confirm the Agent is in the creator's user folder. Then continue in that private Agent.
