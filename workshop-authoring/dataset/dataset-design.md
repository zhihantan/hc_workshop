# Unicorn Finance workshop dataset

**Updated at:** 2026-09-16

*Synthetic lending data for the 22 September 2026 Home Credit enablement workshop. The fictional Unicorn Finance story follows a 0% smartphone promotion that lifts volume, followed by concentrated first-payment default and collections.*

Unicorn Finance and all records are fictional. This is **not** Home Credit production HOSEL/DWH data and does not reproduce Home Credit product names or a physical source schema. The complete narrative is in `../story/unicorn-finance-story.md`.

## Recommendation

Keep one shared dataset across analysis, Genie, engineering, governance, and ML. Do **not** use a generic payment-channel outage plot. The workshop story is POS origination at partner stores, add-on lending economics, and credit losses—not a digital-wallet incident.

## Story

A smartphone-brand-subsidised **0% POS promotion** runs for several weeks across large partner chains and independent retailers. Origination volume spikes. First-payment defaults then concentrate in a small number of stores and field associates, creating a plausible origination-control or fraud-investigation signal. The dataset does not assert the root cause; participants must investigate the pattern.

Databricks value in the workshop: vintage/DPD analysis, Genie Q&A over the same metrics, bronze→silver quality rules on origination, mask sensitive customer and associate identifiers, and predict first-payment default.

**Detailed source schema and ER model:** `source-schema.md`

## What changed vs the first sketch

| Original | Change |
|---|---|
| Generic “loan” contracts | Four product families: POS installment, cash loan, Unicorn Flex, and Unicorn Visa |
| Digital payment outage as the incident | 0% POS promo + first-payment default / fraud concentration |
| `digital_events` as the plot driver | Drop — attendee analysis stays on core lending and in-store origination |
| `system_incidents` | Drop — not an IT-ops story |
| Missing merchant / associate | Add store and associate on applications (fraud and concentration) |
| Missing collections | Add collection actions at 5 / 30 / 60 / 90 DPD; derive current DPD during analysis |
| Missing fee economics | Processing fee at origination; late fees by DPD; 0% = merchant/brand subsidy |

Do **not** model bank borrowings, cost of funds, BSP caps, or the full merchant P&L. Those are real but too much for a one-day lab.

## Tables

📍 Default output location: **`hc_workshop.core_lending`**

The catalog name is configurable during workspace setup. The `core_lending` schema is named after the lending system of record, not the HOSEL acronym.

| Table | Rows (approx) | Grain | Purpose |
|---|---:|---|---|
| `customer` | 15,000 | One borrower or prospect | Identity, contact, employment, income, and geography for origination and governance |
| `retail_location` | 1,000 | One physical partner store | Merchant, store, and geographic context for in-store volume and concentration |
| `loan_product` | 8 | One product version | Commercial limits, tenors, rates, and interest methods |
| `loan_application` | 40,000 | One credit request | Product, amount, channel, store, associate, promotion, item, score, and decision |
| `credit_contract` | Derived | One approved application converted to a contract | Accepted terms, product structure, dates, and lifecycle status |
| `installment` | Derived | One scheduled fixed-term obligation | Due amounts, settlement state, and as-of outstanding amount |
| `payment` | Derived | One payment attempt | Posted receipts and failed attempts |
| `collection_action` | Derived | One action against one delinquent installment | Action, DPD milestone, outcome, promise, and attributed payment |

**Selected workshop scope:** eight tables. Promotion and financed-item attributes stay on `loan_application`; merchant and store are combined as `retail_location`; `preapproved_offer` is not part of the attendee dataset.

**Product rules to encode (skewed, not uniform):**

- **POS installment** (~70% of contracts): 6–24 months (some 4-month Easy Plan); 0–5.99%/month add-on; ~3% processing fee; 0% rows are subsidised promos.
- **Cash loan** (~15%): 6–60 months; higher add-on (1.49–8.99%); existing-customer target; higher default.
- **Unicorn Flex** (~10%): revolving limit up to ₱50,000 with declining-balance interest.
- **Unicorn Visa** (~5%): selected best payers; declining-balance 3%/month.

**Distributions that must be visible after aggregation:**

- POS dominates volume; cash loans dominate loss rate.
- 80/20 store concentration; a few stores/associates drive the promo fraud spike.
- First-payment default cluster in the promo vintage, not a flat delinquency rate.
- Late fees escalate at 5 / 30 / 60 / 90 DPD.

## How each workshop block uses the same data

- **Analysis:** product mix, vintage curves, DPD waterfall, store league table, interest vs fee vs loss.
- **Genie:** same questions in natural language after the SQL/dashboard hour.
- **Engineering:** raw applications/installments → silver contracts with expectations (invalid tenor, missing store, duplicate application).
- **Governance:** mask `national_id_no`, `monthly_income_amount`, `mobile_number`, and `sales_associate_id`; row filter by province.
- **ML:** first-payment default or 30+ DPD on POS originations.

## Generator

The clone-and-run Databricks source notebook is available at `../../workspace-setup/dataset-generator/generate_workshop_dataset.py`. It builds the eight deterministic Delta tables in an isolated staging schema, validates structural and business-story gates, and only then publishes to the configured catalog’s `core_lending` schema.

An administrator still needs catalog-creation and table-write privileges in each destination workspace. See `../../workspace-setup/dataset-generator/README.md`.
