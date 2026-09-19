# Workshop content

This directory is the participant entry point for runnable labs and facilitator-led participant materials. Each topic exposes one primary participant entry point so participants do not need to switch between instructions, exercises, and expected-results files.

Start the workshop with [`../participant-materials/unicorn-finance-workshop-scenario.md`](../participant-materials/unicorn-finance-workshop-scenario.md). It defines the participant role, shared FPD5 question, and the Unicorn Finance delivery produced by each workshop topic.

## Section identifiers and delivery modes

The numeric folder prefixes are internal content identifiers, not a promise that participants will see a consecutive sequence of numbered sessions. The current agenda contains one two-hour **Data Engineering in Databricks** block. The unimplemented `03` and `04` identifiers do not mean that participants attend two separate Data Engineering sections.

Use workshop titles and scheduled times in participant communication. The Governance and Access Control content remains under `05-governance-and-access-control/` for repository-path stability.

Most authored topics use a participant notebook. Governance and Access Control is different: participants use only [`05-governance-and-access-control/participant-guide.md`](05-governance-and-access-control/participant-guide.md) while the facilitator runs a restricted-identity demonstration from a private facilitator folder. Participants do not run code or change permissions in that section.

## Status

The section content is being prepared and is **not yet ready for participant use**.

### Section readiness

- **01 — Data Analysis in Databricks:** Draft. The complete participant journey is in `01-data-analysis-in-databricks/participant-lab.py`; workspace validation, shared data asset creation, access grants, dashboard setup, participant private-Agent creation, and facilitator rehearsal remain.
- **02 — Generative AI in Databricks:** Draft. The complete participant journey is in `02-generative-ai-in-databricks/participant-lab.py`; dashboard showcase setup, optional private participant-Agent editing, workspace validation, and facilitator rehearsal remain.
- **03 — Data Engineering in Databricks:** Draft. The Lakeflow medallion pipeline (bronze → silver + Expectations → gold), the orchestrating Job with a data-quality gate and failure alert, and the WARN/DROP/FAIL demo passed an end-to-end serverless validation run against `sean_development_catalog` (gold = 25,440, matching Sections 01 and 06); facilitator rehearsal, access grants, and TBD confirmations remain.
- **05 — Governance and Access Control in Databricks:** Draft. The participant journey is consolidated in `05-governance-and-access-control/participant-guide.md`; final slides, restricted-identity validation, optional Discover preview setup, lineage verification, and facilitator rehearsal remain.
- **06 — Introduction to Machine Learning in Databricks:** Draft. The runnable lab passed an end-to-end workspace validation run (train → register → batch-score, retargeted to `sean_development_catalog`); facilitator rehearsal, access grants, and TBD confirmations remain.
- **04, 07:** No content directories have been authored. This status does not define the number of Data Engineering sessions in the agenda.

Open the [Section 01 maintainer README](../workshop-authoring/sections/01-data-analysis-in-databricks/README.md), [Section 02 maintainer README](../workshop-authoring/sections/02-generative-ai-in-databricks/README.md), [03-data-engineering-in-databricks/README.md](03-data-engineering-in-databricks/README.md), [Governance maintainer README](../workshop-authoring/sections/05-governance-and-access-control/README.md), or [06-machine-learning-in-databricks/README.md](06-machine-learning-in-databricks/README.md) for section prerequisites and definition of done.

Status meanings:

- **Not started** — required files do not exist.
- **Draft** — files exist but setup, permissions, workspace execution, or rehearsal is incomplete.
- **Ready** — runnable assets passed workspace validation and the facilitator completed a timed rehearsal.

Each completed section contains one participant entry point appropriate to its delivery format. Participant exercises, validation criteria, and reflection belong in that entry point. Facilitator-only design and delivery sources belong in `../workshop-authoring/`.
