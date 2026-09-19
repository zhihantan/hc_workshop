# Governance and Access Control in Databricks

**Participant entry point · 30 minutes · Facilitator-led**

## Your assignment

You are part of the Unicorn Finance team taking ownership of the inherited Databricks platform. A risk analyst can find the trusted FPD5 analysis under **Consumer Lending > Origination Risk**, but cannot query it.

Your task is to diagnose the request without broadening access unnecessarily and complete an incident handover that answers:

1. Which identity is executing the request?
2. Which authorization layer failed?
3. What evidence supports that conclusion?
4. What is the narrowest repair?
5. How was the repair verified?
6. Which downstream assets could be affected by a future change?
7. What does Domain placement prove, and what does it not prove?

The facilitator runs the restricted-identity demonstration. You do not run code or change permissions in this section. Use this guide to record the evidence and complete your handover.

All workshop identities and records are fictional or synthetic. This exercise does not represent Home Credit production permissions or controls.

## Business and data boundary

The governed asset in this incident is:

```text
hc_workshop.workshop_shared.fpd_analysis
```

It contains one row per eligible fixed-term contract used by the workshop's First Payment Default at five days, or **FPD5**, investigation. Eligibility and FPD5 are already defined and validated in the earlier analysis:

- only the first installment is considered;
- the installment must have reached five days past due by **2026-09-01**;
- the denominator is eligible contracts, not applications, approvals, or only defaulted contracts;
- an unsettled installment, or settlement on or after day five, counts as FPD5.

This section does not recalculate that population. A ten-row query is only an access smoke test. It does not prove that the complete dataset or its business definition is correct.

## Terms used in the investigation

- **Principal:** the user, service principal, or group whose permissions are evaluated.
- **Runtime identity:** the principal that actually executes a request. It may differ from the person who opened an asset.
- **Workspace permission:** access to a workspace asset such as a notebook, Job, SQL warehouse, dashboard, or Genie Agent.
- **Unity Catalog privilege:** permission to perform an action on governed data or AI assets.
- **Inherited grant:** a privilege received from a parent object or group rather than granted directly.
- **`BROWSE`:** permission to discover an asset and view metadata without reading its data.
- **Lineage:** evidence showing where data came from and which assets depend on it. Lineage does not grant access.
- **Domain:** a business-aligned discovery grouping built with governed tags. Domain membership does not grant access to the underlying asset.

## The request path

A successful read of a governed view requires several independent gates:

```text
Open the notebook
        ↓
Use the SQL warehouse
        ↓
Identify the runtime principal
        ↓
USE CATALOG → USE SCHEMA → SELECT
        ↓
Return the authorized result
```

Passing one gate does not prove that the next gate will pass. Diagnose the first failed gate before proposing a change.

## Investigation record

### 1. Record the request

- Business request: ________________________________________________
- Runtime principal: _______________________________________________
- Workspace asset: ________________________________________________
- Compute resource: _______________________________________________
- Governed object: `hc_workshop.workshop_shared.fpd_analysis`
- Requested action: _______________________________________________
- Timestamp and time zone: _________________________________________

### 2. Predict, then observe

Before the query runs, identify which facts are already proven:

- [ ] The identity can sign in.
- [ ] The identity can run the notebook.
- [ ] The identity can use the SQL warehouse.
- [ ] The identity can discover the governed asset.
- [ ] The identity can traverse the catalog.
- [ ] The identity can traverse the schema.
- [ ] The identity can select from the view.

After the query runs, record:

- Exact error: _____________________________________________________
- Request ID, if shown: ____________________________________________
- First failed gate: _______________________________________________
- Direct or inherited evidence: ____________________________________

### 3. Propose the narrowest repair

- Missing permission or privilege: _________________________________
- Scope of the change: _____________________________________________
- Principal receiving the change: _________________________________
- Broader change that should be avoided: ___________________________
- Approver or access owner: ________________________________________

Do not use `ALL PRIVILEGES` as a troubleshooting shortcut. Do not add access to the person reporting the error until the runtime principal is confirmed.

### 4. Verify the same request

After the administrator applies the approved change, the facilitator reruns the unchanged query.

- Result after the repair: _________________________________________
- Evidence that the failed gate is now passing: ____________________
- What this result does **not** prove: ______________________________

## Assess downstream impact

Use the prepared lineage graph for `fpd_analysis` to identify what must be retested if its definition, schema, or availability changes.

- Upstream source or transformation observed: ______________________
- Downstream Metric View: __________________________________________
- Downstream dashboard, notebook, or other consumer: _______________
- Owner who should be notified: ____________________________________

Remember: lineage is dependency evidence. It does not authorize access and it does not prove that a downstream result is correct.

## Explain discovery versus authorization

The same asset appears under **Consumer Lending > Origination Risk** in Discover.

- What Domain placement proves: ____________________________________
- Which underlying privileges still control reading the data: ______
- When to use Discover: ____________________________________________
- When to use Catalog Explorer: ____________________________________

## Complete the handover

Timebox: **3 minutes**

Write a concise handover:

> The request ran as ____________________. It failed at ____________________, supported by ____________________. The narrow repair was ____________________. We verified it by ____________________. Downstream assets to retest include ____________________. Domain placement proves ____________________, but does not prove ____________________. The owner is ____________________, the main risk is ____________________, and the recovery action is ____________________.

## Before finishing, make sure you can explain

- why opening a notebook does not prove that its data can be read;
- why the runtime principal must be identified before grants change;
- why `USE CATALOG`, `USE SCHEMA`, and `SELECT` are separate requirements;
- how direct and inherited grants affect diagnosis;
- why an unchanged rerun is stronger evidence than changing the query;
- how lineage supports impact analysis;
- why Domain membership supports discovery but not authorization;
- one owner, risk, and recovery action for this incident.

Your handover is complete when every blank above has evidence and you can explain the diagnostic sequence without proposing a broader permission than the request requires.
