# Section 02 — Generative AI in Databricks

**Status:** Draft — notebooks are authored; workspace validation and facilitator rehearsal remain
**Time:** 11:15 AM–12:15 PM (60 minutes)

This section continues the FPD5 investigation from Section 01. Participants use Genie Code to understand, extend, repair, and improve inherited SQL and PySpark with less manual effort. A facilitator showcase applies the same workflow to dashboard authoring. If time and workspace readiness allow, participants can also use Genie Code to implement a new stakeholder requirement in the private Genie Agent they created in Section 01.

The central message is:

> Genie Code makes technical work faster, but governed definitions, permissions, and human validation still make it trustworthy.

## Outcomes

By the end of the section, participants can:

1. Use notebook, cell, and data context to understand inherited analysis faster.
2. Generate and refine SQL analysis and visualizations with targeted prompts.
3. Diagnose a realistic PySpark denominator bug, review the proposed repair, and add lightweight validation checks.
4. Improve and document existing code without forcing unnecessary changes.
5. Explain how Genie Code creates and refines an AI/BI Dashboard.
6. Apply the same context → outcome → review → validation loop to their own work.

Optional extension:

- Use Genie Code to make and regression-test a focused context change in the private Section 01 Genie Agent.

## Workshop flow

- **Understand:** explain an inherited Section 01 query using notebook, cell, and Metric View context.
- **Build and iterate:** extend the FPD5 analysis by region with a structured prompt and targeted follow-ups.
- **Diagnose and improve:** repair an inherited PySpark validation helper with a denominator bug, add assertions, document the query, and review optimization suggestions.
- **Deliver:** watch Genie Code build a simple, unpublished AI/BI Dashboard from the same Metric View.
- **Optional extension:** improve the participant's private Section 01 Genie Agent with Genie Code and run a regression check.

## Prerequisites

- The administrator has completed `../../workshop-setup/README.md`.
- `hc_workshop.workshop_shared.fpd_metrics` exists and passed the Section 01 validation.
- `hc_workshop.workshop_shared.fpd_analysis` exists and contains one row per eligible contract.
- The Section 01 participant lab has been completed or demonstrated.
- Participants can use Serverless notebook compute.
- Partner-powered AI features are enabled at both account and workspace level, and the workspace is in a region supported by Genie Code.
- Genie Code and its agentic notebook actions are available to participants.
- Each participant has a writable user workspace folder in which to clone `participant-lab.py`.
- A Serverless or Pro SQL warehouse is available for dashboard authoring and the optional participant Agent extension.

For the optional Agent extension, each participant must also have completed Section 01 with one private **Unicorn FPD5 Investigator — `<workspace_username>`** Agent using only `fpd_metrics`.

Before delivery, the facilitator must confirm:

- Genie Code appears in the notebook sidebar for a participant-equivalent user.
- The `@` resource picker can attach `hc_workshop.workshop_shared.fpd_metrics`.
- The participant can approve generated notebook edits and query execution.
- Genie Code for dashboard authoring is available in a new AI/BI Dashboard.
- Completed fallback notebook and dashboard states are ready in case a live agentic action stalls.
- For the optional extension, a participant-equivalent user can open and edit their private Section 01 Agent with Genie Code.
- For the optional extension, the facilitator has rehearsed the improvement flow in the demonstration account.

## Required permissions

Participants need:

- Workspace access and permission to create or clone notebooks in their own user folder.
- Permission to use the assigned Serverless notebook compute.
- `USE CATALOG` on `hc_workshop`.
- `USE SCHEMA` on `hc_workshop.workshop_shared`.
- `SELECT` on `hc_workshop.workshop_shared.fpd_metrics` and `hc_workshop.workshop_shared.fpd_analysis`.
- Access to Genie Code.

For the optional Agent extension, participants also need Databricks SQL access, `CAN USE` on the Agent's Pro or Serverless SQL warehouse, and `CAN MANAGE` on the private Agent they created in Section 01.

The participant SQL and PySpark operations are read-only and do not require `CREATE`, `MODIFY`, or `MANAGE` on workshop data. In the optional extension, every participant edits only the private Agent they created in Section 01. The Agent remains unshared with other participants.

For the facilitator showcases, the facilitator additionally needs:

- Databricks SQL access.
- `CAN USE` on the selected SQL warehouse.
- Permission to create and edit draft AI/BI Dashboards.
- `SELECT` on the Metric View through the credentials used by those assets.
- For the optional extension, `CAN MANAGE` on the facilitator's private demonstration Agent.

Recommended product references:

- [Get coding help from Genie Code](https://docs.databricks.com/aws/en/notebooks/code-assistant)
- [Use Genie Code for data science](https://docs.databricks.com/aws/en/notebooks/ds-agent)
- [Use Genie Code for dashboard authoring](https://docs.databricks.com/aws/en/dashboards/manage/dashboard-agent)
- [Create, clone, and manage a Genie Agent](https://docs.databricks.com/aws/en/genie-agents/set-up)

## Assets

Participant entry point:

- `participant-lab.py` — a Databricks source notebook that participants clone before Genie Code edits it.
- `exercises.md` — the required notebook productivity loop and optional Agent-iteration checklist.
- `expected-results.md` — invariant results, acceptable variation, and recovery paths.

Facilitator-only delivery files:

- `facilitator-demo.py` — a resettable live-demo notebook, including the intentional diagnosis example.
- `facilitator-guide.md` — the minute-by-minute required flow, optional extension, talking points, UI paths, and fallbacks.

Generated cells and dashboard layouts can vary between runs. Correctness is judged by governed sources, measures, filters, safety constraints, and reference outputs—not by exact generated content.

## Definition of done

- Every participant works in a personal clone rather than modifying the shared workshop notebook.
- Participants use Genie Code to explain an inherited query before modifying it.
- Genie Code uses only `hc_workshop.workshop_shared.fpd_metrics` for generated analytical SQL and `hc_workshop.workshop_shared.fpd_analysis` for the PySpark validation helper.
- The cohort comparison agrees with the Section 01 reference rates: approximately **42.26%** for the promotion and **21.03%** for other eligible originations.
- The participant extension groups by region and applies a minimum of 20 eligible contracts.
- Participants diagnose and repair the PySpark helper that filters to FPD5 rows before calculating its denominator.
- The repaired helper keeps the full eligible population, uses `fpd5_flag` only as the numerator, and passes lightweight validation checks.
- Any accepted optimization preserves the validated result.
- No generated cell writes or replaces data.
- Interpretations describe elevated FPD5 as an investigation signal and do not claim causality or fraud.
- The facilitator's draft dashboard reconciles to the notebook and remains unpublished.
- Participants can identify where they would incorporate the same workflow into their own work.

Optional Agent-extension checkpoint:

- Each participant continues with the single private Agent created in Section 01; no shared Agent or clone is introduced.
- The participant Agent explicitly includes counts, observation date, investigation language, and minimum-denominator behavior for FPD5 ranking answers.
- The target store-associate question and the cohort regression question both pass after the context change.
