# Unicorn Finance Philippines — workshop story

**Updated at:** 2026-09-16

*Canonical fictional narrative for the Home Credit Databricks workshop. It defines the company, business event, inherited platform, dataset, and investigation that every workshop section should use.*

The concise participant-facing opening narrative and section-delivery map is published at [`../../participant-materials/unicorn-finance-workshop-scenario.md`](../../participant-materials/unicorn-finance-workshop-scenario.md).

<style>
@page { size: A4 portrait; margin: 1.5cm; }
table { font-size: 8.5pt; }
</style>

## The company

**Unicorn Finance Philippines — Credit with a little magic**

Unicorn Finance is a fictional consumer lender serving customers through retail partners and digital channels. Its portfolio includes fixed-term point-of-sale (POS) installment loans, cash loans, a revolving product called **Unicorn Flex**, and **Unicorn Visa**.

Atlas Ridge Consulting has delivered Unicorn Finance’s Databricks lakehouse and is now handing operations to the internal data team. Atlas Ridge is the fictional stand-in for Tiger Analytics. Participants take the role of Unicorn Finance employees learning to find, understand, run, govern, troubleshoot, and improve the inherited assets.

## The business event

A smartphone brand funds a limited 0% POS promotion. Applications and approved contracts increase, but first-payment default becomes concentrated in a small number of stores and sales associates.

The pattern is an investigation signal, not proof of fraud. Participants must determine whether it could reflect campaign design, customer mix, weak origination controls, operational behavior, or another explanation.

## The inherited data platform

Synthetic operational records have been loaded as managed Delta tables in the default namespace:

```text
hc_workshop.core_lending
```

The catalog name can be changed during workspace setup. The workshop uses three schemas:

- `core_lending` — protected source data shared by all participants.
- `workshop_shared` — facilitator-managed trusted views and metrics for dashboards and Genie.
- `workshop_labs` — participant-owned tables, views, and registered models with per-user prefixes.

Notebooks, Lakeflow Jobs and pipelines, dashboards, MLflow experiments, and Genie Agents are workspace assets rather than objects inside these schemas.

## Core-lending schema

The eight tables represent one connected lending lifecycle:

```text
customer → loan_application → credit_contract → installment → payment
                    │                            └──→ collection_action
                    ├→ loan_product
                    └→ retail_location
```

| Domain | Table | One row represents | Purpose |
|---|---|---|---|
| Reference | `customer` | One borrower or prospect | Customer identity, contact, employment, income, and geography for origination and governance exercises |
| Reference | `retail_location` | One physical partner store | Merchant, store, and geographic context for application-volume and concentration analysis |
| Reference | `loan_product` | One product version | Commercial limits, tenor ranges, rates, and interest methods used to interpret applications and contracts |
| Origination | `loan_application` | One credit request | Requested product and amount, channel, store, associate, promotion, underwriting decision, and financed item |
| Origination | `credit_contract` | One approved application converted to a contract | Accepted financial terms, product structure, origination date, maturity, and lifecycle status |
| Servicing | `installment` | One scheduled fixed-term obligation | Due amounts, due date, settlement state, and as-of outstanding amount |
| Servicing | `payment` | One payment attempt | Posted receipts and failed attempts applied to an installment and contract |
| Collections | `collection_action` | One action against one delinquent installment | Collection method, DPD at action, outcome, promise to pay, and directly attributed payment |

`loan_application` is the origination hub. Declined or cancelled applications do not produce contracts. Only fixed-term POS and cash contracts produce installments in this dataset. One installment can have multiple payment attempts. Collection actions identify both the overdue installment and its parent contract.

## Workshop investigation

Across the day, participants:

1. Locate the inherited data and workspace assets.
2. Explore product mix, approval conversion, and store concentration.
3. Calculate first-payment default consistently and investigate the 0% promotion.
4. Ask governed natural-language questions and verify the answers against trusted SQL.
5. Productionise selected logic as a monitored data pipeline and job.
6. Apply access controls and inspect lineage.
7. Train, register, and batch-score an interpretable first-payment-default model.
8. Finish with the ownership, monitoring, recovery, and change practices needed after partner handover.

For this workshop, first-payment default (FPD5) means the first installment reached five days past due before full settlement. Include only contracts whose first installment has reached that observation point by the declared as-of date. A null settlement or settlement on or after day five counts as FPD5.

## Fiction boundary

Unicorn Finance, Atlas Ridge Consulting, all people, IDs, applications, stores, contracts, payments, and collection events in the dataset are fictional or synthetic. The scenario is designed for the Home Credit Philippines enablement workshop but does not describe Home Credit production data, product names, systems, controls, or confirmed business outcomes.
