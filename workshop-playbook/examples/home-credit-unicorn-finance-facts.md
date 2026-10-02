# Workshop facts — Home Credit Philippines Databricks Enablement

**Updated at:** 2026-10-01

*Completed facts file for the workshop delivered on 22 September 2026. Use it as a worked example of `../workshop-facts-template.md`. Sources: `workshop-authoring/story/`, `agenda/`, `dataset/`, `workshop-setup/`, and the section folders in this repository.*

## 1. Engagement

| Field | Value |
|---|---|
| `CUSTOMER` | Home Credit Philippines |
| `WORKSHOP_DATE` | Tuesday 22 September 2026 |
| `FORMAT` | Full day, face to face, Ore 14F |
| `FACILITATORS` | Sean Chang (Sections 01, 02, 05), Zhi Han Tan (Sections 03, 06) |
| `PARTICIPANT_BACKGROUND` | Basic SQL and Python. Many are developers moving from Cloudera Spark. New to Databricks, Unity Catalog, and Genie |
| `LANGUAGE_NOTES` | English is a second language for many participants. Lending jargon must be explained |
| `CUSTOMER_REQUESTS` | SQL warehouse troubleshooting: compute choices, Serverless versus Classic versus Pro, and how to monitor a warehouse |
| `PREREQUISITES` | Databricks Free Edition sign-up; Databricks Academy account with corporate email; "Databricks Fundamentals" path (~1 hour) |
| `FACILITATOR_HAS_PARTICIPANT_WORKSPACE_ACCESS` | No. The customer admin ran setup in the participant sandbox. Facilitator demos ran in the facilitator's own workspace |

## 2. Fictional story

| Field | Value |
|---|---|
| `FICTIONAL_COMPANY` | Unicorn Finance Philippines — "Credit with a little magic" |
| `HANDOVER_PARTNER` | Atlas Ridge Consulting (fictional stand-in for the customer's real implementation partner) |
| `PARTICIPANT_ROLE` | Unicorn Finance's internal data team taking ownership of the inherited Databricks platform |
| `BUSINESS_EVENT` | Nova Mobile's 0% smartphone promotion |
| `OTHER_FICTIONAL_ENTITIES` | Nova Mobile (smartphone brand) |

### Business event in plain steps

1. A customer chooses a selected Nova phone at a participating store.
2. The customer applies for a Unicorn Finance point-of-sale installment loan.
3. If approved, the customer repays the amount borrowed over 6, 9, or 12 monthly payments.
4. The customer pays 0% monthly interest.
5. Nova Mobile pays Unicorn Finance a subsidy to support the 0% offer.

### What the event is not

- The phone is not free; the customer repays the amount borrowed.
- A processing fee or down payment can still apply.
- Approval is not guaranteed.

### Canonical identifiers and labels

| Identifier | Value |
|---|---|
| Event code in data | `ZERO_SMARTPHONE_2026` |
| Product label | `Unicorn 0% Brand Promotion` |
| Analysis label | `0% smartphone promotion` |
| Comparison label | `Other eligible originations` (origination = a loan that was created) |

### Interpretation boundary

Applications rose during the promotion, and some stores and salespeople had more first-payment problems. This is a reason to investigate. It is not proof that the promotion caused the increase, that a store or salesperson caused a late payment, or that fraud occurred. The synthetic data does not represent Home Credit production data, product names, systems, or results.

## 3. Core metric

| Field | Value |
|---|---|
| `CORE_METRIC` | FPD5 — First Payment Default at five days past due |
| Plain-language meaning | The first monthly payment was still unpaid, or paid late, five days after its due date |
| Population | One row per eligible fixed-term credit contract |
| Eligibility rule | `installment_no = 1` and `date_add(due_date, 5) <= AS_OF_DATE` |
| Numerator | Eligible contracts where settlement is null or on or after `due_date + 5` |
| Denominator | All eligible contracts in the group |
| Edge cases | Payment on day five counts as FPD5. Settlement before day five does not |
| Never calculate from | All applications, all approvals, all contracts regardless of age, or only defaulted contracts |
| Uniqueness check | `contract_id` unique before counting. Do not join first installments to multiple payment rows |

"Default" here describes only the first payment at day five. It does not mean the loan was never repaid.

## 4. Dataset

| Field | Value |
|---|---|
| `GENERATOR_VERSION` | 1.1.0 |
| `MASTER_SEED` | 20260922 |
| `SCALE` | standard |
| `AS_OF_DATE` | 2026-09-01 |
| Total records at standard scale | 700,150 across eight managed Delta tables |

### Tables

| Table | One row represents | Approx. rows |
|---|---|---:|
| `customer` | One borrower or prospect | 15,000 |
| `retail_location` | One partner store | 1,000 |
| `loan_product` | One product version | 8 |
| `loan_application` | One credit request (origination hub) | 40,000 |
| `credit_contract` | One approved application converted to a contract | Derived |
| `installment` | One scheduled monthly payment | Derived |
| `payment` | One payment attempt | Derived |
| `collection_action` | One action against one late installment | Derived |

### Story signals that must be visible after aggregation

- Point-of-sale installment loans dominate volume; cash loans dominate loss rate.
- The busiest 20% of stores take most applications.
- FPD5 clusters in the promotion and in a few stores and sales associates.
- Collection actions appear at 5, 30, 60, and 90 days past due.

### Out of scope

- No offer-response events, so no cross-sell analysis. `preapproved_offer` is excluded.
- No bank borrowings, cost of funds, regulatory caps, or merchant profit and loss.
- No digital-event or IT-incident storyline.

### Reference values

| Measure | Value | Reveal after |
|---|---:|---|
| Top-20% store share of applications (non-null `store_id`) | ≈ 81.13% | Section 01 application exploration |
| Eligible contracts | 25,440 | Section 01 population step; Section 03 gold check |
| Overall FPD5 rate | 25.14% | Section 01 |
| Promotion FPD5 rate | ≈ 42.26% (4,927 contracts) | Section 01 cohort comparison |
| Other eligible originations FPD5 rate | ≈ 21.03% (20,513 contracts) | Section 01 cohort comparison |
| Worst promotion region | `REGION_VI` ≈ 53.95% (6 regions, ≥ 20 eligible) | Section 02 regional checkpoint |
| Interpretable model ROC-AUC | ≈ 0.63 (0.9 would signal leakage) | Section 06 evaluation |

## 5. Unity Catalog and workspace

| Field | Value |
|---|---|
| `CATALOG` | `hc_workshop` |
| `CATALOG_STORAGE` | Created manually in Catalog Explorer. `CREATE CATALOG` from code failed with "Metastore storage root URL does not exist" because the account uses Default Storage |
| `SOURCE_SCHEMA` | `core_lending` |
| `SHARED_SCHEMA` | `workshop_shared` (`fpd_analysis` view, `fpd_metrics` Metric View) |
| `LABS_SCHEMA` | `workshop_labs` |
| `SHARED_METRIC_VIEW` | `hc_workshop.workshop_shared.fpd_metrics` |
| `WORKSPACE_ROOT` | `/Workspace/Shared/hc_workshop` |
| `ASSET_PREFIX` | `unicorn` (for example `unicorn_<runner_id>_fpd_investigation`, model `unicorn_<user_id>_fpd`) |
| `PRIVATE_ASSET_LOCATION` | `/Workspace/Users/<workspace-username>` for each participant's private Genie Agent |
| Per-participant schema exception | Section 03 pipeline targets `de_<user_id>` |

## 6. Environment values

| Field | Development | Delivery |
|---|---|---|
| Workspace URL | `https://fevm-sean-development.cloud.databricks.com` | Customer sandbox (not recorded) |
| Databricks CLI profile | `DEFAULT` | — |
| Notebook compute | Serverless | Serverless |
| `SQL_WAREHOUSE` | Serverless SQL warehouse | TBD (never recorded) |
| `PARTICIPANT_GROUP` | — | TBD (never recorded) |
| `FACILITATOR_GROUP` | — | TBD (never recorded) |
| Features that must be enabled | Serverless notebooks, Databricks SQL entitlement, partner-powered AI features at account and workspace level, Genie Code | Same |

## 7. Agenda and sections

| No. | Section | Time | Minutes | Delivery mode | Depends on |
|---|---|---|---:|---|---|
| 00 | Introduction to Databricks (with opening slides) | 9:00–9:30 | 30 | Slides and guided UI | — |
| 01 | Data Analysis in Databricks | 9:45–11:15 | 90 | NOTEBOOK_LED | Dataset, `fpd_metrics` |
| 02 | Generative AI in Databricks (Genie Code) | 11:15–12:15 | 60 | NOTEBOOK_LED | 01 Agent and `fpd_metrics` |
| — | Lunch | 12:15–1:15 | 60 | — | — |
| 03 | Data Engineering in Databricks | 1:20–3:20 | 120 | NOTEBOOK_LED (pipeline + Job) | 01 FPD5 logic |
| 05 | Governance and Access Control | 3:20–3:50 | 30 | FACILITATOR_LED | `fpd_analysis`, `fpd_metrics`, dashboard |
| 06 | Introduction to Machine Learning | 4:00–5:00 | 60 | NOTEBOOK_LED | Dataset, FPD5 definition |
| — | Closing | end of day | 8–10 | Slides | All |

Numbering decision: the original Section 04 was dropped and later numbers were kept, so Governance stayed Section 05. Section 07 was never built.

### Section 01 — Data Analysis

- **Assignment:** Does the 0% smartphone promotion show higher FPD5, and where should the business look more closely?
- **Final deliverable:** a participant Delta table with a handover note, reconciled to `fpd_metrics`, plus a private Genie Agent with verified SQL.
- **Topics:** notebook versus Jobs versus SQL warehouse compute; Python and SQL exploration; FPD5 population; cohort and concentration comparison; Delta history; Metric View; AI/BI dashboard; private Genie Agent; Query History and Query Profile.

### Section 02 — Generative AI

- **Assignment:** use Genie Code to understand, extend, repair, and document inherited analysis while the developer owns validation.
- **Final deliverable:** one validated personal notebook: explained query, regional extension, independent reconciliation, repaired PySpark denominator bug, short handover documentation.
- **Topics:** Genie Code explain, extend, debug; `/optimize` and `/doc` review; dashboard draft (demo). **Optional:** improving the Section 01 Genie Agent with regression checks.

### Section 03 — Data Engineering

- **Assignment:** turn the one-off FPD5 query into a quality-gated, scheduled pipeline whose gold layer every consumer trusts.
- **Final deliverable:** a serverless Lakeflow pipeline (bronze, silver, gold) and a Job (`run_pipeline → quality_gate`) with a failure alert, plus a handover checkpoint.
- **Topics:** medallion layers; Streaming Tables versus Materialized Views; Expectations (WARN, DROP ROW, FAIL UPDATE); pipeline versus Job; event log, lineage, recovery by full refresh; Lakeflow Designer (optional demo).

### Section 05 — Governance and Access Control

- **Assignment:** a risk analyst can discover `fpd_analysis` but cannot query it. Find the identity and the first failed gate, apply the narrowest fix, and verify with an unchanged rerun.
- **Final deliverable:** a completed incident handover in `05-participant-guide.md`.
- **Topics:** authorization chain (notebook, warehouse, identity, `USE CATALOG`, `USE SCHEMA`, `SELECT`); evidence; lineage for retest decisions; Discover Domains (curation is not authorization).

### Section 06 — Machine Learning

- **Assignment:** train an interpretable FPD5 model, track it, register it in Unity Catalog, batch-score the eligible book, and hand it over.
- **Final deliverable:** an MLflow run, a registered model with a `@champion` alias, and a governed scores table (25,440 rows).
- **Topics:** leakage-safe features; time split; logistic regression and reason codes; MLflow; Unity Catalog model registry; batch scoring. **Optional or future:** Model Serving, online features, monitoring.

## 8. Glossary

| Term | Plain-language definition |
|---|---|
| Point of sale (POS) | The loan is offered when the customer buys the item |
| Installment | One scheduled monthly payment |
| Origination | A loan that was created |
| FPD5 | The first payment was still unpaid, or paid late, five days after the due date |
| Cohort | A group |
| Grain | What one row represents |
| Denominator | The total used to calculate a rate |
| Metric View | A shared business calculation stored in one place |
| Queue | A query is waiting because compute is busy |
| Spill | A query needed more memory and temporarily used disk |
| Lineage | Where data came from and what uses it |
