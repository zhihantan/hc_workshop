# Workshop facts — <CUSTOMER> <WORKSHOP_NAME>

**Updated at:** <YYYY-MM-DD>

*The single source of customer-specific facts for this workshop. Every playbook prompt reads this file. Copy it to `workshop-authoring/workshop-facts.md` in the new repository and keep it current.*

Mark unknown values `TBD`. Prompts must not invent them. See `examples/home-credit-unicorn-finance-facts.md` for a completed version.

## 1. Engagement

| Field | Value |
|---|---|
| `CUSTOMER` | Real audience organization |
| `WORKSHOP_DATE` | |
| `FORMAT` | Full day / half day; in person / remote; venue |
| `FACILITATORS` | Names and roles |
| `PARTICIPANT_BACKGROUND` | What they already know; what will be new |
| `LANGUAGE_NOTES` | For example, English is a second language for many participants |
| `CUSTOMER_REQUESTS` | Topics the customer explicitly asked for |
| `PREREQUISITES` | Pre-work participants must complete |
| `FACILITATOR_HAS_PARTICIPANT_WORKSPACE_ACCESS` | Yes / No. If no, demos run in the facilitator's own workspace and the customer's admin runs setup |

## 2. Fictional story

| Field | Value |
|---|---|
| `FICTIONAL_COMPANY` | Name and tagline |
| `HANDOVER_PARTNER` | Fictional partner handing the platform over (optional) |
| `PARTICIPANT_ROLE` | For example, the internal data team taking ownership |
| `BUSINESS_EVENT` | One event that every section investigates |
| `OTHER_FICTIONAL_ENTITIES` | Brands, merchants, and so on |

### Business event in plain steps

1. <step a customer or employee takes>
2. <step>
3. <step>

### What the event is not

- <misreading to prevent, for example "the phone is not free">

### Canonical identifiers and labels

| Identifier | Value |
|---|---|
| Event code in data | |
| Product or campaign label | |
| Analysis label | |
| Comparison label | |

### Interpretation boundary

The pattern is a reason to investigate. It is not proof of: <causation, fraud, misconduct, ...>. Fictional names and synthetic data do not represent <CUSTOMER> products, systems, controls, or results.

## 3. Core metric

| Field | Value |
|---|---|
| `CORE_METRIC` | Short name |
| Plain-language meaning | One sentence |
| Population | What one row represents (grain) |
| Eligibility rule | When a row can be counted, relative to `AS_OF_DATE` |
| Numerator | |
| Denominator | |
| Edge cases | Boundary days, nulls, ties |
| Never calculate from | Wrong populations to block |
| Uniqueness check | Key that must be unique before aggregation |

Add more rows or a second table if the workshop has more than one canonical metric.

## 4. Dataset

| Field | Value |
|---|---|
| `GENERATOR_VERSION` | |
| `MASTER_SEED` | |
| `SCALE` | small / standard / large |
| `AS_OF_DATE` | |
| Total records at standard scale | |

### Tables

| Table | One row represents | Purpose |
|---|---|---|
| | | |

### Story signals that must be visible after aggregation

- <signal, for example "80/20 store concentration">

### Out of scope

- <concepts deliberately not modelled, for example "no offer-response events, so no cross-sell analysis">

### Reference values (fill after the dataset is generated and validated)

| Measure | Value | Reveal after |
|---|---:|---|
| | | Section and step |

## 5. Unity Catalog and workspace

| Field | Value |
|---|---|
| `CATALOG` | |
| `CATALOG_STORAGE` | For example, Default Storage, created manually in Catalog Explorer |
| `SOURCE_SCHEMA` | Read-only source |
| `SHARED_SCHEMA` | Facilitator-owned shared views and Metric Views |
| `LABS_SCHEMA` | Participant outputs and models |
| `SHARED_METRIC_VIEW` | Fully qualified name |
| `WORKSPACE_ROOT` | Shared workshop folder, for example `/Workspace/Shared/<repo>` |
| `ASSET_PREFIX` | Prefix for participant assets, used as `<ASSET_PREFIX>_<runner_id>_<asset>` |
| `PRIVATE_ASSET_LOCATION` | `/Workspace/Users/<workspace-username>` |

## 6. Environment values

| Field | Development | Delivery |
|---|---|---|
| Workspace URL | | |
| Databricks CLI profile | | |
| Notebook compute / runtime | | |
| `SQL_WAREHOUSE` | | |
| `PARTICIPANT_GROUP` | | |
| `FACILITATOR_GROUP` | | |
| Prepared dashboard URL | | |
| Features that must be enabled | | |

## 7. Agenda and sections

| No. | Section | Time | Minutes | Delivery mode | Depends on |
|---|---|---|---:|---|---|
| 00 | Opening and introduction | | | Slides | |
| 01 | | | | NOTEBOOK_LED / FACILITATOR_LED | |
| — | Closing | | | Slides | All |

Numbering decision: <for example, "Section 04 dropped; later numbers kept unchanged">

For each section, keep this summary short. The detailed plan lives in `workshop-authoring/sections/<NN>-<section>/section-plan.md`.

### Section <NN> — <name>

- **Assignment:** <the question participants answer for the fictional company>
- **Final deliverable:** <saved result, decision, asset, or handover note>
- **Topics that must be covered:** <list>
- **Optional topics:** <list>
- **Reuses from earlier sections:** <tables, definitions, Agents>

## 8. Glossary

| Term | Plain-language definition |
|---|---|
| | |
