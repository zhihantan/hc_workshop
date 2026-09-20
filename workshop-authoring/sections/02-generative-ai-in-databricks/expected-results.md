# Expected results — Section 02

**Facilitator-only.** Do not distribute this file in the participant workspace folder.

Genie Code wording, cell layout, aliases, and chart styling can vary. Validate governed sources, populations, measures, thresholds, safety constraints, and outputs rather than expecting identical generated code.

## Governed baseline

The inherited cohort query returns one row per `promotion_cohort` and uses:

- `MEASURE(eligible_contracts)` as the denominator;
- `MEASURE(fpd5_contracts)` as the numerator;
- `MEASURE(fpd5_rate)` as their governed ratio; and
- multiplication by 100 only for display.

Reference rates:

- 0% smartphone promotion: approximately **42.26%**;
- other eligible originations: approximately **21.03%**.

## Regional extension

The result must:

- read only `hc_workshop.workshop_shared.fpd_metrics`;
- filter to `promotion_cohort = '0% smartphone promotion'`;
- group at `region_code` grain;
- invoke the governed measures with `MEASURE(...)`;
- retain only regions with at least 20 eligible contracts;
- preserve counts beside the rate; and
- compare each region with the promotion-only baseline.

All six standard-data regions qualify:

- `REGION_VI`: 443 eligible, 239 FPD5, **53.95%**;
- `REGION_XI`: 243 eligible, 116 FPD5, **47.74%**;
- `NCR`: 1,832 eligible, 808 FPD5, **44.10%**;
- `REGION_III`: 473 eligible, 194 FPD5, **41.01%**;
- `REGION_IV_A`: 1,507 eligible, 595 FPD5, **39.48%**;
- `REGION_VII`: 429 eligible, 130 FPD5, **30.30%**.

`REGION_VI` is approximately **11.69 percentage points** above the promotion baseline. This is an investigation signal, not evidence that the region, promotion, store, or associate caused default or committed fraud.

## PySpark repair

The inherited helper incorrectly filters to `fpd5_flag = 1` before aggregation. That removes non-FPD5 eligible contracts from the denominator and produces 100% rates.

An acceptable repair:

- removes the pre-aggregation FPD5 filter;
- preserves one eligible source row per contract from `fpd_analysis`;
- counts eligible contracts from the full grouped population;
- sums the existing `fpd5_flag` for the numerator;
- remains read-only and DataFrame-based; and
- does not recreate the observation-date or settlement logic.

Checks should confirm:

- exactly two cohort rows;
- positive eligible counts;
- FPD5 counts do not exceed eligible counts; and
- rates agree within 0.05 percentage points with a read-only query of the governed Metric View.

## Dashboard showcase

The disposable **Genie Code Demo — FPD5 Overview** draft should contain:

- eligible-contract, FPD5-contract, and FPD5-rate KPIs;
- a promotion-cohort comparison;
- a five-store promotion ranking showing eligible contracts, FPD5 contracts, and FPD5 rate, with at least 10 eligible contracts;
- a promotion-cohort filter affecting the cohort comparison and store ranking but not the all-cohort KPI counters; and
- clear titles and percentage formatting.

It must use `fpd_metrics`, reconcile with the notebook, remain unpublished, and be deleted after the workshop. It is distinct from the prepared Section 01 **Unicorn FPD5 Overview** dashboard.

## Optional Agent extension

The participant continues with the existing private **Unicorn FPD5 Investigator — `<workspace_username>`**. It remains unshared and uses only `fpd_metrics`.

The target store-associate answer should:

- filter to the 0% smartphone promotion;
- use governed measures;
- apply at least 10 eligible contracts at store-associate grain;
- include eligible and FPD5 counts;
- state the `2026-09-01` observation date; and
- use investigation-signal language.

In a fresh conversation, the original cohort question should still return approximately **42.26%** versus **21.03%**.

## Shortest recovery

- **Generated SQL rebuilds FPD5:** reject it and require `fpd_metrics` measures.
- **Regional result differs:** check source, promotion filter, grain, `HAVING` threshold, denominator, and percentage conversion.
- **PySpark still reports 100%:** remove any `fpd5_flag` filter before `groupBy`.
- **Dashboard differs:** check Metric View source, store threshold, filter scope, and percentage formatting; do not publish.
- **Genie Code unavailable:** use the completed facilitator clone and keep participants focused on review and validation decisions.
- **Agent unavailable:** skip the optional extension; do not substitute a shared Agent.
