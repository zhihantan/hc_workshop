# Expected results and troubleshooting

**Participant note:** Complete the focused exercise before opening this file.

These values assume the default standard-scale dataset (master seed `20260922`, as-of date `2026-09-01`) and the released `participant-pipeline.sql`. They were captured from an end-to-end validation run of the released pipeline. Small differences are acceptable when the environment differs; large differences usually mean the landing, Expectations, or FPD5 boundary changed.

## Raw landing (facilitator setup)

`facilitator-setup.sql` lands the clean daily batch (`batch_date = 2026-09-01`):

| Table | Rows |
|---|--:|
| `lending_raw_loan_application` | 40,000 |
| `lending_raw_credit_contract` | 29,803 |
| `lending_raw_installment` | 346,871 |

## Pipeline — clean batch (the baseline)

On the clean batch **every row passes**; nothing is dropped:

| Layer | `installment` | `contract` | `application` |
|---|--:|--:|--:|
| bronze | 346,871 | 29,803 | 40,000 |
| silver | 346,871 | 29,803 | 40,000 |

- Gold **`fpd_origination`**: **25,440** rows, one per eligible fixed-term contract (POS installment + cash loan whose first installment reached `due_date + 5 days` by `2026-09-01`) — the same eligible population Section 01 analysed and Section 06 modelled.
  - 0% smartphone promotion: **4,927** contracts, **42.26%** FPD5
  - Other eligible originations: **20,513** contracts, **21.03%** FPD5
  - Overall: **25.14%**
- Gold **`fpd_daily_metrics`**: one row per origination month × cohort. Example (Other originations): 2024-09 → 939 eligible, 17.57%; 2024-10 → 923, 19.07%. The 0% promotion cohort runs materially higher, matching Section 01.

## Data quality — the dirty batch

Landing the WARN/DROP batch (`batch_date = 2026-09-02`, ~40 rows each) and refreshing the pipeline: **the update still completes**, and the bad rows are quarantined at silver rather than flowing to gold.

| Expectation | Table | Tier | Violations |
|---|---|---|--:|
| `nonneg_due` (total_due_amount ≥ 0) | installment | DROP ROW | 40 |
| `positive_income` (declared_income > 0) | application | DROP ROW | 40 |
| `sane_lti` (requested/income < 20) | application | WARN (kept) | 40 |

- After the WARN/DROP batch: bronze grows (installment 346,911, application 40,040) but **silver is unchanged** (346,871 / 40,000) — the 40 negative-amount installments and 40 zero-income applications are dropped; the 40 extreme-loan-to-income applications are flagged but kept. **Gold stays 25,440** — bad data never reached the business layer.
- Landing the FAIL batch (`batch_date = 2026-09-03`, null `contract_id`) and refreshing: the **pipeline update FAILS** on `valid_contract (ON VIOLATION FAIL UPDATE)`. A broken key stops everything — and, run under the Job, fires the failure alert.
- Reset: delete the `> 2026-09-01` batches and run a **full refresh**; gold returns to 25,440.

## Orchestration — the Job

The Job DAG (`run_pipeline` → `quality_gate`) succeeds on clean data. `job-quality-gate` compares silver vs bronze installment counts and appends a `fpd_run_summary` row:

| eligible_contracts | fpd5_rate_pct | bronze_installments | silver_installments | installment_drop_pct |
|--:|--:|--:|--:|--:|
| 25,440 | 25.14 | 346,871 | 346,871 | 0.0 |

If the drop rate exceeds the threshold (default 5%), the `quality_gate` task raises and the Job fails — the softer safety net beneath the hard `FAIL UPDATE` expectation.

## Shortest recovery paths

### The pipeline update fails immediately with an expectation error
A `FAIL UPDATE` expectation (e.g. `valid_contract`) was violated — usually the seeded FAIL batch. Delete `batch_date > 2026-09-01` from the landing and run a **full refresh**. Do not weaken a `FAIL UPDATE` expectation to force a pass.

### Gold has far fewer than 25,440 rows / FPD5 rate looks too high
A silver Expectation is dropping legitimate rows. The classic mistake is gating on settlement timing — early/on-time settlement is the FPD5 *outcome*, not a defect. Confirm the silver expectations match the released file (broken key → FAIL; missing due date / negative amount → DROP; timing is never gated).

### `Table or view not found` for `fpd_bronze_*`
The pipeline target catalog/schema is wrong, or the pipeline has not run yet. Confirm the pipeline's target is `hc_workshop.de_<your_user_id>` (or your delivery catalog) and that the update completed.

### Streaming source error after a landing DELETE
Streaming Tables reject deletes/updates in their source. After resetting the landing, run the pipeline with **full refresh** (it reprocesses from scratch and ignores the streaming checkpoint).

### The Job's quality-gate task fails on clean data
The drop-rate threshold (`max_drop_pct`) is too low, or a silver Expectation is dropping legitimate rows. Check `fpd_run_summary.installment_drop_pct`; on the clean batch it should be `0.0`.
