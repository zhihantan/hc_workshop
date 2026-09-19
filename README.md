# Home Credit Databricks workshop

Updated on 17 September 2026

Participant and facilitator materials for the Home Credit Philippines enablement workshop on 22 September 2026.

## Start here

Participants should use only:

1. `participant-materials/`
   - [Workshop agenda](participant-materials/workshop-agenda.pdf)
   - [Unicorn Finance story](participant-materials/unicorn-finance-story.pdf)
   - [Unicorn Finance dataset guide](participant-materials/dataset-guide.pdf)
   - [Unicorn Finance data dictionary](participant-materials/data-dictionary.pdf)
2. `workshop-content/` — section-by-section labs, facilitator-led participant materials, exercises, and instructions.

The runnable section content is still being prepared. The repository will be ready for participant use when `workshop-content/README.md` marks every required section as **Ready**.

## Repository layout

```text
participant-materials/   PDFs distributed to workshop participants
workshop-content/        Participant labs and facilitator-led section materials
workshop-setup/          Administrator and facilitator environment setup
workshop-authoring/      Facilitator design sources, diagrams, and prompts
```

Participants do not need `workshop-setup/` or `workshop-authoring/`.

Not every workshop topic has a participant-run notebook. Governance and Access Control is a facilitator-led demonstration: participants use its diagnostic checklist and team exercise while the facilitator runs the prepared restricted-identity notebook.

## Workshop scenario

The hands-on exercises follow **Unicorn Finance Philippines**, a fictional consumer lender taking over a Databricks lakehouse delivered by an implementation partner. The canonical narrative is in `workshop-authoring/story/unicorn-finance-story.md`.

Home Credit Philippines is the real workshop audience. Unicorn Finance is the company represented by the synthetic data.

## Workshop environment setup

Before the workshop, follow `workshop-setup/README.md`. The administrator first creates `hc_workshop` manually in Catalog Explorer using **Default Storage**, then runs the setup notebooks to create:

```text
hc_workshop.core_lending
hc_workshop.workshop_shared
hc_workshop.workshop_labs
```

The catalog name is configurable. The default standard-scale dataset run deterministically produces 700,150 records across eight managed Delta tables in `core_lending`. The generator builds in a run-isolated schema, validates structural and business-story gates, then publishes with a serialized release lock and compensating rollback.

Use `workshop-setup/workshop-setup.zip` only when Git folder access is unavailable.

## Facilitator authoring

Editable Markdown, the dataset design, ER sources, and the reusable content-generation prompt live under `workshop-authoring/`. Generated participant labs belong under `workshop-content/`, not in the authoring directory.

The development and workspace-validation approach is documented in [TESTING.md](TESTING.md).

## Disclaimer

Unicorn Finance and all dataset records are fictional. This repository does not contain Home Credit production data or claim to reproduce Home Credit products or its physical core-system schema.
