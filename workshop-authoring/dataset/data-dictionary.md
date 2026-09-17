# Unicorn Finance workshop data dictionary

**Updated at:** 2026-09-16

*Authoritative column-level reference for the eight synthetic Unicorn Finance Delta tables in the default namespace `hc_workshop.core_lending`. Types use Databricks SQL notation.*

<style>
@page { size: A4 landscape; margin: 1.2cm; }
html, body { font-size: 9.5pt; }
table { font-size: 8pt; }
th, td { padding: 0.35em 0.5em; }
code { font-size: 8pt; }
th:nth-child(1), td:nth-child(1) { width: 22%; }
th:nth-child(2), td:nth-child(2) { width: 15%; }
th:nth-child(3), td:nth-child(3) { width: 8%; }
th:nth-child(4), td:nth-child(4) { width: 12%; }
th:nth-child(5), td:nth-child(5) { width: 43%; }
</style>

## Schema overview

| Table | Grain | Purpose | Primary relationship |
|---|---|---|---|
| `customer` | One borrower or prospect | Customer identity, contact, employment, income, and geography | Parent of `loan_application` |
| `retail_location` | One physical partner store | Merchant and location context for in-store originations | Optional parent of `loan_application` |
| `loan_product` | One product version | Commercial rules, limits, tenors, rates, and interest method | Parent of `loan_application` |
| `loan_application` | One credit request | Origination, promotion, item, associate, and underwriting decision | Child of reference tables; optional parent of `credit_contract` |
| `credit_contract` | One approved application converted to a contract | Accepted financial terms and contract lifecycle | Parent of `installment` and `collection_action` |
| `installment` | One scheduled fixed-term obligation | Due amounts and servicing state at the configured as-of date | Parent of `payment` and `collection_action` |
| `payment` | One payment attempt | Posted receipts and failed attempts | Child of `credit_contract` and `installment` |
| `collection_action` | One action against one delinquent installment | Collection activity, outcome, promise, and attributed payment | Child of `credit_contract` and `installment` |

## Conventions

- **PK** — Primary key.
- **UK** — Unique business key.
- **FK** — Foreign key relationship; Delta does not enforce it automatically.
- **Required** — `Yes` means the generator always supplies a value.
- **Money** — `DECIMAL(18,2)`, denominated in PHP unless stated otherwise.
- **Rates** — `DECIMAL(7,4)` percentage points; `5.9900` means 5.99%.
- **Timestamps** — UTC.
- **PII / sensitive** — Synthetic but suitable for masking, tagging, and access-control exercises.

## `customer`

One row per borrower or prospect.

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `customer_id` | `BIGINT` | Yes | PK | Surrogate customer identifier |
| `customer_no` | `STRING` | Yes | UK | Human-readable core-system customer number |
| `national_id_no` | `STRING` | Yes | PII | Synthetic government ID |
| `first_name` | `STRING` | Yes | PII | Synthetic given name |
| `last_name` | `STRING` | Yes | PII | Synthetic family name |
| `birth_date` | `DATE` | Yes | PII | Date of birth |
| `sex_code` | `STRING` | No | PII | Source demographic code |
| `mobile_number` | `STRING` | Yes | PII | Synthetic Philippine mobile number |
| `email_address` | `STRING` | No | PII | Synthetic email address |
| `employment_type_code` | `STRING` | Yes |  | Employment classification |
| `monthly_income_amount` | `DECIMAL(18,2)` | Yes | Sensitive | Declared monthly income |
| `province` | `STRING` | Yes | PII | Current province |
| `city_municipality` | `STRING` | Yes | PII | Current city or municipality |
| `customer_since_date` | `DATE` | Yes |  | Relationship start date |
| `created_at` | `TIMESTAMP` | Yes |  | Source creation timestamp |
| `updated_at` | `TIMESTAMP` | Yes |  | Last source update timestamp |

Typical `employment_type_code` values: `SALARIED`, `SELF_EMPLOYED`, `INFORMAL`, `UNEMPLOYED`, `RETIRED`.

## `retail_location`

One row per physical store. Merchant fields are denormalized onto the location for the workshop.

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `store_id` | `BIGINT` | Yes | PK | Store identifier |
| `store_code` | `STRING` | Yes | UK | Source store code |
| `store_name` | `STRING` | Yes |  | Store display name |
| `merchant_code` | `STRING` | Yes |  | Parent merchant or chain code |
| `merchant_name` | `STRING` | Yes |  | Retail partner name |
| `merchant_type_code` | `STRING` | Yes |  | Merchant classification |
| `city_municipality` | `STRING` | Yes |  | Store city or municipality |
| `province` | `STRING` | Yes |  | Store province |
| `region_code` | `STRING` | Yes |  | Philippine administrative region |
| `opened_date` | `DATE` | Yes |  | Origination-location start date |
| `active_flag` | `BOOLEAN` | Yes |  | Whether the location is active |
| `updated_at` | `TIMESTAMP` | Yes |  | Last source update timestamp |

Generated `merchant_type_code` values: `LARGE_CHAIN`, `INDEPENDENT`.

## `loan_product`

One row per product version and commercial rule set.

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `product_id` | `BIGINT` | Yes | PK | Product-version identifier |
| `product_code` | `STRING` | Yes | UK | Product-version business code |
| `product_name` | `STRING` | Yes |  | Product display name |
| `product_type_code` | `STRING` | Yes |  | Product family |
| `interest_method_code` | `STRING` | Yes |  | Interest calculation method |
| `min_principal_amount` | `DECIMAL(18,2)` | Yes |  | Minimum allowed principal or limit |
| `max_principal_amount` | `DECIMAL(18,2)` | Yes |  | Maximum allowed principal or limit |
| `min_tenor_months` | `INT` | No |  | Minimum fixed-term tenor |
| `max_tenor_months` | `INT` | No |  | Maximum fixed-term tenor |
| `min_monthly_rate_pct` | `DECIMAL(7,4)` | Yes |  | Minimum monthly percentage |
| `max_monthly_rate_pct` | `DECIMAL(7,4)` | Yes |  | Maximum monthly percentage |
| `effective_from` | `DATE` | Yes |  | Product-version start date |
| `effective_to` | `DATE` | No |  | Product-version end date |
| `active_flag` | `BOOLEAN` | Yes |  | Whether the product is currently sellable |

`product_type_code` values:

- `POS_INSTALLMENT`
- `CASH_LOAN`
- `REVOLVING_LINE`
- `CREDIT_CARD`

`interest_method_code` values: `ADD_ON`, `DECLINING_BALANCE`.

Generated `product_code` values: `UNICORN_EASY_4M`, `UNICORN_POS_A`, `UNICORN_POS_B`, `UNICORN_ZERO_PROMO`, `UNICORN_CASH`, `UNICORN_CASH_PLUS`, `UNICORN_FLEX`, `UNICORN_VISA`.

## `loan_application`

One row per credit request and underwriting outcome. Promotion, associate, and financed-item fields are intentionally embedded to keep the workshop at eight tables.

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `application_id` | `BIGINT` | Yes | PK | Application identifier |
| `application_no` | `STRING` | Yes | UK | Human-readable core-system application number |
| `customer_id` | `BIGINT` | Yes | FK → `customer` | Applicant |
| `product_id` | `BIGINT` | Yes | FK → `loan_product` | Requested product version |
| `store_id` | `BIGINT` | No | FK → `retail_location` | Physical origin; null for digital/direct |
| `sales_associate_id` | `STRING` | No | Sensitive | Synthetic assisting associate number |
| `application_channel_code` | `STRING` | Yes |  | Origination channel |
| `requested_amount` | `DECIMAL(18,2)` | Yes |  | Requested principal or credit limit |
| `requested_tenor_months` | `INT` | No |  | Requested fixed tenor; null for revolving |
| `declared_income_amount` | `DECIMAL(18,2)` | Yes | Sensitive | Income captured at application |
| `underwriting_score` | `DECIMAL(7,2)` | Yes | Sensitive | Point-in-time decision score |
| `decision_code` | `STRING` | Yes |  | Underwriting outcome |
| `decision_reason_code` | `STRING` | No | Sensitive | Primary decision reason |
| `promotion_code` | `STRING` | No |  | Embedded promotion identifier |
| `promotion_sponsor_type_code` | `STRING` | No |  | Promotion funder |
| `item_category_code` | `STRING` | No |  | POS item category |
| `item_brand_name` | `STRING` | No |  | POS item brand |
| `financed_amount` | `DECIMAL(18,2)` | No |  | POS amount financed |
| `submitted_at` | `TIMESTAMP` | Yes |  | Submission timestamp |
| `decided_at` | `TIMESTAMP` | Yes |  | Decision timestamp |
| `created_at` | `TIMESTAMP` | Yes |  | Source creation timestamp |
| `updated_at` | `TIMESTAMP` | Yes |  | Last source update timestamp |

Typical codes:

- `application_channel_code`: `IN_STORE`, `MOBILE_APP`, `WEB`, `CALL_CENTER`
- `decision_code`: `APPROVED`, `DECLINED`, `CANCELLED`
- `promotion_sponsor_type_code`: `BRAND`
- `item_category_code`: `SMARTPHONE`, `APPLIANCE`, `LAPTOP`

## `credit_contract`

One row per accepted contract. Contractual values are retained as snapshots even when they repeat product defaults.

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `contract_id` | `BIGINT` | Yes | PK | Contract identifier |
| `contract_no` | `STRING` | Yes | UK | Human-readable core-system contract number |
| `application_id` | `BIGINT` | Yes | FK/UK → `loan_application` | Approved source application |
| `contract_status_code` | `STRING` | Yes |  | Contract lifecycle status |
| `currency_code` | `STRING` | Yes |  | ISO currency code; `PHP` in this dataset |
| `principal_amount` | `DECIMAL(18,2)` | No |  | Fixed-term financed principal |
| `credit_limit_amount` | `DECIMAL(18,2)` | No |  | Revolving limit; null for fixed-term |
| `tenor_months` | `INT` | No |  | Fixed-term tenor |
| `monthly_interest_rate_pct` | `DECIMAL(7,4)` | Yes |  | Contractual monthly percentage |
| `interest_method_code` | `STRING` | Yes |  | `ADD_ON` or `DECLINING_BALANCE` |
| `processing_fee_amount` | `DECIMAL(18,2)` | Yes |  | Upfront customer processing fee |
| `subsidy_amount` | `DECIMAL(18,2)` | Yes |  | Merchant or brand subsidy |
| `origination_date` | `DATE` | Yes |  | Contract start date |
| `maturity_date` | `DATE` | No |  | Scheduled maturity for fixed-term products |
| `disbursed_at` | `TIMESTAMP` | Yes |  | Merchant/customer funding timestamp |
| `closed_at` | `TIMESTAMP` | No |  | Contract closure timestamp |
| `created_at` | `TIMESTAMP` | Yes |  | Source creation timestamp |
| `updated_at` | `TIMESTAMP` | Yes |  | Last source update timestamp |

Generated `contract_status_code` values: `ACTIVE`, `CLOSED`, `DEFAULTED`.

Exactly one of `principal_amount` and `credit_limit_amount` is normally populated:

- Fixed-term POS/cash: `principal_amount`
- Revolving Unicorn Flex/card: `credit_limit_amount`

## `installment`

One row per scheduled fixed-term obligation. The pair `(contract_id, installment_no)` is unique.

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `installment_id` | `BIGINT` | Yes | PK | Installment identifier |
| `contract_id` | `BIGINT` | Yes | FK → `credit_contract` | Parent contract |
| `installment_no` | `INT` | Yes | UK within contract | Installment sequence |
| `due_date` | `DATE` | Yes |  | Contractual due date |
| `principal_due_amount` | `DECIMAL(18,2)` | Yes |  | Principal component |
| `interest_due_amount` | `DECIMAL(18,2)` | Yes |  | Interest component |
| `fee_due_amount` | `DECIMAL(18,2)` | Yes |  | Scheduled fee component |
| `total_due_amount` | `DECIMAL(18,2)` | Yes |  | Total scheduled amount |
| `outstanding_amount` | `DECIMAL(18,2)` | Yes |  | Current unpaid amount |
| `installment_status_code` | `STRING` | Yes |  | Servicing status |
| `settled_date` | `DATE` | No |  | Fully settled date |
| `created_at` | `TIMESTAMP` | Yes |  | Source creation timestamp |
| `updated_at` | `TIMESTAMP` | Yes |  | Last source update timestamp |

Generated `installment_status_code` values: `SCHEDULED`, `PARTIAL`, `PAID`, `OVERDUE`.

Current DPD is not stored because it changes with the reporting date. Calculate it from `due_date`, `settled_date`, `outstanding_amount`, and a declared as-of date.

## `payment`

One row per payment attempt or receipt. Failed attempts remain visible as events.

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `payment_id` | `BIGINT` | Yes | PK | Payment-event identifier |
| `payment_reference` | `STRING` | Yes | UK | External or source reference |
| `contract_id` | `BIGINT` | Yes | FK → `credit_contract` | Receiving contract |
| `installment_id` | `BIGINT` | Yes | FK → `installment` | Applied fixed-term installment |
| `payment_at` | `TIMESTAMP` | Yes |  | Attempt or receipt timestamp |
| `payment_amount` | `DECIMAL(18,2)` | Yes |  | Payment amount |
| `payment_channel_code` | `STRING` | Yes |  | Payment channel |
| `payment_status_code` | `STRING` | Yes |  | Event status |
| `failure_reason_code` | `STRING` | No |  | Failure reason when applicable |
| `posted_at` | `TIMESTAMP` | No |  | Ledger posting timestamp |
| `created_at` | `TIMESTAMP` | Yes |  | Source creation timestamp |

Typical codes:

- `payment_channel_code`: `APP`, `BANK_TRANSFER`, `PAYMENT_CENTER`, `STORE`
- `payment_status_code`: `POSTED`, `FAILED`

Only `POSTED` payments should reduce an outstanding balance. A posted payment should have `posted_at`; a failed payment should have `failure_reason_code`.

## `collection_action`

One row per collection attempt or outcome against a delinquent contract.

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `collection_action_id` | `BIGINT` | Yes | PK | Collection-action identifier |
| `contract_id` | `BIGINT` | Yes | FK → `credit_contract` | Contract worked |
| `installment_id` | `BIGINT` | Yes | FK → `installment` | Specific overdue installment |
| `action_at` | `TIMESTAMP` | Yes |  | Action timestamp |
| `days_past_due_at_action` | `INT` | Yes | Snapshot | DPD when the action occurred |
| `action_type_code` | `STRING` | Yes |  | Collection method |
| `outcome_code` | `STRING` | Yes |  | Action outcome |
| `promise_to_pay_date` | `DATE` | No |  | Promised payment date |
| `promise_amount` | `DECIMAL(18,2)` | No |  | Promised amount |
| `amount_collected` | `DECIMAL(18,2)` | Yes |  | Amount directly attributed to the action |
| `agent_id` | `STRING` | No | Sensitive | Synthetic collection-agent identifier |
| `created_at` | `TIMESTAMP` | Yes |  | Source creation timestamp |

Typical codes:

- `action_type_code`: `SMS`, `CALL`, `FIELD_VISIT`, `NOTICE`
- `outcome_code`: `NO_CONTACT`, `CONTACTED`, `PROMISE_TO_PAY`, `PAYMENT_RECEIVED`

`promise_to_pay_date` and `promise_amount` are populated when `outcome_code = 'PROMISE_TO_PAY'`. `PAYMENT_RECEIVED` records reconcile to one `POSTED` payment with the same installment, timestamp, and amount.

## Relationship summary

- `loan_application.customer_id` → `customer.customer_id`
- `loan_application.store_id` → `retail_location.store_id`
- `loan_application.product_id` → `loan_product.product_id`
- `credit_contract.application_id` → `loan_application.application_id`
- `installment.contract_id` → `credit_contract.contract_id`
- `payment.contract_id` → `credit_contract.contract_id`
- `payment.installment_id` → `installment.installment_id`
- `collection_action.contract_id` → `credit_contract.contract_id`
- `collection_action.installment_id` → `installment.installment_id`

## Generator metadata

The generator records its version, deterministic seed, as-of date, scale, and shared `workshop.run_id` as Delta table properties rather than adding columns to every business table. Data values are derived from a stable row identifier, field namespace, master seed, and generator version so the same configuration produces the same logical rows across workspaces.
