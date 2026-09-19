# Workshop content

This directory is the participant entry point for runnable labs and facilitator-led participant materials.

## Section identifiers and delivery modes

The numeric folder prefixes are internal content identifiers, not a promise that participants will see a consecutive sequence of numbered sessions. The current agenda contains one two-hour **Data Engineering in Databricks** block. The unimplemented `03` and `04` identifiers do not mean that participants attend two separate Data Engineering sections.

Use workshop titles and scheduled times in participant communication. The Governance and Access Control content remains under `05-governance-and-access-control/` for repository-path stability.

Most authored topics use a participant notebook. Governance and Access Control is different: the facilitator runs `05-governance-and-access-control/facilitator-demo.py` under a dedicated restricted identity while participants follow the diagnostic checklist and complete the team checkpoint. Participants do not run or clone that demonstration notebook.

## Status

The section content is being prepared and is **not yet ready for participant use**.

### Section readiness

- **01 — Data Analysis in Databricks:** Draft. Content is authored; workspace validation, shared data asset creation, access grants, dashboard setup, participant private-Agent creation, and facilitator rehearsal remain.
- **02 — Generative AI in Databricks:** Draft. Genie Code SQL and PySpark notebooks are authored; dashboard showcase setup, optional private participant-Agent editing, workspace validation, and facilitator rehearsal remain.
- **03 — Data Engineering in Databricks:** Draft. The Lakeflow medallion pipeline (bronze → silver + Expectations → gold), the orchestrating Job with a data-quality gate and failure alert, and the WARN/DROP/FAIL demo passed an end-to-end serverless validation run against `sean_development_catalog` (gold = 25,440, matching Sections 01 and 06); facilitator rehearsal, access grants, and TBD confirmations remain.
- **05 — Governance and Access Control in Databricks:** Draft. Slides, a facilitator-run controlled diagnostic notebook, UI walkthrough, Domain design, and participant checklist are authored; restricted-identity setup, workspace validation, Domain curation, and facilitator rehearsal remain.
- **06 — Introduction to Machine Learning in Databricks:** Draft. The runnable lab passed an end-to-end workspace validation run (train → register → batch-score, retargeted to `sean_development_catalog`); facilitator rehearsal, access grants, and TBD confirmations remain.
- **04, 07:** No content directories have been authored. This status does not define the number of Data Engineering sessions in the agenda.

Open [01-data-analysis-in-databricks/README.md](01-data-analysis-in-databricks/README.md), [02-generative-ai-in-databricks/README.md](02-generative-ai-in-databricks/README.md), [03-data-engineering-in-databricks/README.md](03-data-engineering-in-databricks/README.md), [05-governance-and-access-control/README.md](05-governance-and-access-control/README.md), or [06-machine-learning-in-databricks/README.md](06-machine-learning-in-databricks/README.md) for section prerequisites and definition of done.

Status meanings:

- **Not started** — required files do not exist.
- **Draft** — files exist but setup, permissions, workspace execution, or rehearsal is incomplete.
- **Ready** — runnable assets passed workspace validation and the facilitator completed a timed rehearsal.

Each completed section contains the participant or facilitator assets appropriate to its delivery format, exercises, expected results, and concise setup requirements. Facilitator-only design sources belong in `../workshop-authoring/`; section-specific delivery guidance can remain beside the runnable lab.
