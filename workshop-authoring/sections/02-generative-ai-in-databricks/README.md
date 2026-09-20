# Section 02 — Generative AI in Databricks

**Status:** Draft — workspace validation and facilitator rehearsal required
**Time:** 11:15 AM–12:15 PM (60 minutes)

This directory contains maintainer and facilitator material. Participants use only [`02-lab.py`](../../../workshop-content/02-generative-ai-in-databricks/02-lab.py), which contains the complete assignment, exercises, UI activities, validation criteria, dashboard observation checklist, optional Agent extension, and final reflection.

## Delivery authority

- Participant flow and outcomes: [`02-lab.py`](../../../workshop-content/02-generative-ai-in-databricks/02-lab.py)
- Timing, delivery surfaces, and facilitator talking points: [`facilitator-guide.md`](facilitator-guide.md)
- Facilitator dashboard sequence: [`facilitator-demo.py`](facilitator-demo.py)
- Final visible-slide generation: [`generate-section-02-generative-ai-slides-v3-slide-only.md`](generate-section-02-generative-ai-slides-v3-slide-only.md)

This README tracks release prerequisites, permissions, file ownership, and definition of done rather than repeating the delivery narrative.

## Prerequisites

- The administrator completed [`workshop-setup/README.md`](../../../workshop-setup/README.md).
- `hc_workshop.workshop_shared.fpd_metrics` passed the Section 01 validation.
- `hc_workshop.workshop_shared.fpd_analysis` contains one row per eligible contract.
- Section 01 was completed or demonstrated.
- Participants can use Serverless notebook compute and access Genie Code.
- Each participant has a writable user workspace folder.
- A Pro or Serverless SQL warehouse is available for the facilitator dashboard and optional Genie Agent extension.
- Partner-powered AI features and required regional availability are confirmed.

For the optional extension, each participant must still own the private **Unicorn FPD5 Investigator — `<workspace_username>`** Agent created in Section 01.

## Required permissions

Participants need:

- workspace access and permission to clone notebooks into their user folder;
- permission to use the assigned notebook compute;
- `USE CATALOG` on `hc_workshop`;
- `USE SCHEMA` on `hc_workshop.workshop_shared`;
- `SELECT` on `fpd_metrics` and `fpd_analysis`; and
- access to Genie Code.

For the optional Agent extension, participants also need the Databricks SQL entitlement, access to the Agent's configured Pro or Serverless SQL warehouse, and at least `CAN EDIT` on the Agent. Creators normally retain `CAN MANAGE`.

The facilitator additionally needs permission to create and edit draft AI/BI dashboards, `CAN USE` on the selected SQL warehouse, and access to a private demonstration Agent.

## Participant-visible asset

Only this file should be distributed or imported into the participant-facing workshop folder:

- [`02-lab.py`](../../../workshop-content/02-generative-ai-in-databricks/02-lab.py)

Participants do not need a separate exercise sheet or expected-results file.

## Facilitator and authoring assets

- [`facilitator-guide.md`](facilitator-guide.md) — timed delivery map plus concise talking points organized in participant-notebook order.
- [`facilitator-demo.py`](facilitator-demo.py) — resettable demonstration notebook and dashboard prompt.
- [`expected-results.md`](expected-results.md) — governed reference outputs and troubleshooting.
- [`generate-section-02-generative-ai-slides-v3-slide-only.md`](generate-section-02-generative-ai-slides-v3-slide-only.md) — final generation prompt limited to the facilitator guide's visible slide window.
- [`drafts/`](drafts/README.md) — archived content-first and prescriptive slide sources.

## Definition of done

- Participants begin from one personal notebook clone.
- The assignment and FPD5 definitions appear before calculation.
- The regional result uses only `fpd_metrics`, applies the 20-contract rule at regional grain, and reconciles with the governed checkpoint.
- The repaired helper keeps the full eligible population and reconciles dynamically with `fpd_metrics`.
- No generated participant cell writes or replaces workshop data.
- Interpretations use investigation language and retain counts beside rates.
- The facilitator dashboard reconciles and remains unpublished.
- Participants record an owner, operating risk, recovery action, next-week use case, and retained validation.
- The optional Agent remains private and passes both target and regression questions.
