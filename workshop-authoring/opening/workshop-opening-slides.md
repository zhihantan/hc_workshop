# Workshop opening — introductory slides

**Recommended duration:** 5–7 minutes
**Slides:** 3
**Audience:** Home Credit Philippines
**Scenario:** Fictional company and synthetic data

Use these slides at the start of the 9:00 AM Introduction to Databricks session.

---

## Slide 1 — Today's workshop journey

### Visible content

**Databricks Enablement — 22 September 2026**

```text
9:00–9:30      Introduction to Databricks
9:45–11:15     Data Analysis in Databricks
11:15–12:15    Generative AI in Databricks
12:15–1:15     Lunch
1:20–3:20      Data Engineering in Databricks
3:20–3:50      Governance and Access Control
4:00–5:00      Introduction to Machine Learning
```

**One continuous outcome:** understand, validate, operate, govern, and improve an inherited Databricks platform.

### Recommended visual

Use a horizontal timeline with six workshop topics. Visually separate the morning investigation, afternoon operationalization, and final model lifecycle while keeping them connected as one journey.

### Presenter notes

- This is one connected workshop rather than a collection of unrelated product demonstrations.
- Each topic produces or validates something that Unicorn Finance must operate after the handover.
- The same business event, data, and FPD5 definition connect the sessions.

### Transition

> To make that journey concrete, today we will work as one fictional company's internal data team.

---

## Slide 2 — The platform was delivered. Ownership starts today.

### Visible content

**Today, you are the internal data team at Unicorn Finance Philippines.**

Atlas Ridge Consulting has handed over a Databricks platform containing data, notebooks, dashboards, metrics, pipelines, models, and AI assets.

Nova Mobile's 0%-interest smartphone financing campaign increased volume, while FPD5 appears concentrated in a small number of stores and sales associates.

> What happened, which evidence can we trust, and what must Unicorn Finance operate after the handover?

**The pattern is an investigation signal—not proof of fraud, misconduct, or causality.**

### Recommended visual

Create one horizontal handover:

```text
Atlas Ridge Consulting
        ↓ handover
Data · Notebooks · Dashboards · Metrics · Pipelines · Models · AI assets
        ↓ ownership
Unicorn Finance internal team
```

Place the campaign question beside the inherited assets and make it the focal point.

### Presenter notes

- Unicorn Finance, Atlas Ridge Consulting, Nova Mobile, all identities, and all records are fictional or synthetic.
- “0%” means 0% monthly interest. Customers still repay financed principal and may pay a processing fee.
- FPD5 means the first installment reached five days past due before full settlement.
- The workshop is about ownership: purpose, governed definitions, compute, permissions, validation, monitoring, recovery, and the next responsible owner.

### Transition

> We will investigate that question using one connected synthetic lending dataset.

---

## Slide 3 — The data we will explore

### Visible content

**Unity Catalog structure**

```text
hc_workshop
├── core_lending       protected synthetic source tables
├── workshop_shared    trusted views, metrics, and facilitator assets
└── workshop_labs      participant-created tables and models
```

**Connected lending lifecycle**

```text
customer → loan_application → credit_contract → installment → payment
                    │                            └──→ collection_action
                    ├→ loan_product
                    └→ retail_location
```

**Eight source tables**

- `customer`
- `loan_application`
- `loan_product`
- `retail_location`
- `credit_contract`
- `installment`
- `payment`
- `collection_action`

### Recommended visual

Use a simple lifecycle diagram. Emphasize the path from application to contract, first installment, and payment because it supports the shared FPD5 investigation. Show product and retail location as business context and collection action as the downstream delinquency response.

### Presenter notes

- All data is synthetic and contains no Home Credit production records.
- `core_lending` represents the protected inherited source.
- `workshop_shared` contains governed definitions reused by dashboards and AI assets.
- `workshop_labs` is where participants create their own governed outputs.
- The sections reuse the same data but ask different operational questions: analysis, development, pipelines, access, lineage, and modeling.

### Transition

> Before we run the investigation, we need a shared map of the Databricks platform that contains these assets.

These slides intentionally establish the same starting point revisited in `../closing/workshop-closing-slides.md`.
