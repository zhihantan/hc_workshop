# Section 02 — Generative AI in Databricks

**Status:** Draft — workspace validation and facilitator rehearsal required
**Time:** 11:15 AM–12:15 PM (60 minutes)

This directory contains maintainer and facilitator material. Participants use only [`participant-lab.py`](../../../workshop-content/02-generative-ai-in-databricks/participant-lab.py), which contains the complete assignment, exercises, UI activities, validation criteria, dashboard observation checklist, optional Agent extension, and final reflection.

## Delivery

Participants act as developers supporting Unicorn Finance's risk analytics team after the Atlas Ridge handover. They extend the governed FPD5 investigation to regional grain, repair an inherited PySpark denominator bug, and prepare a validated notebook for its next owner.

The investigation continues Nova Mobile's brand-subsidized offer for selected smartphones: approved customers repay principal over 6, 9, or 12 months at 0% monthly interest. “0%” describes interest only; it does not mean a free phone, zero down payment, zero fees, or guaranteed approval.

The section delivers:

- a governed promotion-region analysis with counts, rates, and a minimum denominator;
- reconciliation against a pre-authored Metric View checkpoint;
- a repaired read-only PySpark validation helper with executable checks;
- concise handover documentation;
- a facilitator-built, reconciled, unpublished AI/BI dashboard draft; and
- optionally, a focused and regression-tested change to the participant's existing private Genie Agent.

The central message is:

> Genie Code makes technical work faster, but governed definitions, permissions, and human validation still make it trustworthy.

## Outcomes

By the end of the section, participants can:

1. Use notebook, cell, and data context to understand inherited analysis.
2. Extend a governed investigation with a structured prompt and targeted correction.
3. Interpret counts, rates, denominators, and uncertainty at regional grain.
4. Diagnose a semantic PySpark denominator bug and protect the repair with checks.
5. Distinguish notebook compute from the SQL warehouse used by dashboards and Genie Agents.
6. Explain which generated actions remain subject to human review, validation, and publication decisions.

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

- [`participant-lab.py`](../../../workshop-content/02-generative-ai-in-databricks/participant-lab.py)

Participants do not need a separate exercise sheet or expected-results file.

## Facilitator and authoring assets

- [`facilitator-guide.md`](facilitator-guide.md) — preparation, timed delivery, answers, recovery, and dashboard flow.
- [`facilitator-demo.py`](facilitator-demo.py) — resettable demonstration notebook and dashboard prompt.
- [`expected-results.md`](expected-results.md) — governed reference outputs and troubleshooting.
- [`generate-section-02-generative-ai-slides-v2-content-first.md`](generate-section-02-generative-ai-slides-v2-content-first.md) — recommended content-first slide-generation source.
- [`generate-section-02-generative-ai-slides.md`](generate-section-02-generative-ai-slides.md) — prescriptive editorial reference.

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
