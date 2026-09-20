# Content-first slide brief — Governance and Access Control in Databricks

Use this document as the complete content input for an LLM creating presentation support for the 30-minute facilitator-led Governance and Access Control workshop.

This is not a slide outline. Decide the smallest effective slide count, titles, order, layouts, and visuals. Do not display the internal `05` repository identifier.

## Source authority

Resolve conflicts in this order:

1. `../../../workshop-content/05-governance-and-access-control/participant-guide.md`
2. `facilitator-demo.py`
3. `../../../workshop-setup/section-05-governance-demo-setup.sql`
4. `facilitator-guide.md`
5. `../../../participant-materials/unicorn-finance-workshop-scenario.md`
6. `../../agenda/workshop-agenda.md`

Treat target-workspace setup as intended and draft until successfully rehearsed.

## Audience and role

- The audience is Home Credit Philippines developers and technical owners.
- Participants act as Unicorn Finance's internal team taking over an inherited Databricks platform.
- They need a reusable operating method, not a comprehensive security-product tour.
- Unicorn Finance, Atlas Ridge, all identities, records, and results are fictional or synthetic.

## Participant assignment

A risk analyst can find:

```text
hc_workshop.workshop_shared.fpd_analysis
```

under **Consumer Lending > Origination Risk**, but cannot query it.

Participants must complete one incident handover covering:

1. runtime principal;
2. failed authorization layer;
3. supporting evidence;
4. narrowest approved repair;
5. verification from the unchanged request;
6. downstream assets requiring retesting;
7. what Domain placement proves and does not prove;
8. one owner, risk, and recovery action.

The same `fpd_analysis` asset must anchor discovery, the failed query, repair, verification, lineage, and handover.

## Business and data boundary

`fpd_analysis` is the trusted one-row-per-eligible-contract view created earlier in the workshop. Governance does not recalculate FPD5.

If the FPD5 definition is mentioned, preserve:

- first installment only;
- five-day observation point reached by 2026-09-01;
- eligible contracts as the denominator;
- unsettled or settled on/after day five counts as FPD5.

A ten-row result is an access smoke test. It does not prove data completeness, unrestricted row visibility, or business-definition correctness.

## Mandatory messages

- “Can access” is a chain of gates, not one permission.
- Users, service principals, and groups can hold permissions.
- The runtime identity executes the request; group membership can contribute effective access.
- Notebook `CAN RUN`, SQL warehouse `CAN USE`, runtime identity, and Unity Catalog privileges are separate gates.
- For this view read: `USE CATALOG → USE SCHEMA → SELECT`.
- `BROWSE` supports discovery without granting row access.
- Direct, inherited, and group-derived grants all matter.
- Preserve the request and change one authorization variable at a time.
- An unchanged rerun provides stronger evidence than changing the SQL, identity, or compute.
- A successful query can still be affected by row filters, column masks, ABAC, or a shared asset's data-permission mode.
- Lineage supports dependency and impact analysis; it does not authorize access or prove correctness.
- Discover Domains organize assets by business purpose using governed tags; they are not authorization boundaries.
- Domain placement does not grant `USE CATALOG`, `USE SCHEMA`, or `SELECT`.
- The final output is an operational handover, not merely a successful query.

## Demonstration evidence

The restricted identity can:

- sign in;
- run the demonstration notebook;
- use the SQL warehouse;
- discover `fpd_analysis`;
- pass `USE CATALOG`;
- hold `SELECT` on `fpd_analysis`.

It initially lacks:

```text
USE SCHEMA ON SCHEMA hc_workshop.workshop_shared
```

The facilitator:

1. shows `current_user()`;
2. asks participants to predict the outcome;
3. runs the `fpd_analysis` query;
4. stops at the insufficient-privilege error;
5. distinguishes direct grants, parent-securable inheritance, and group-derived access;
6. grants only `USE SCHEMA`;
7. reruns the unchanged query;
8. confirms ten synthetic rows appear.

The temporary privilege is revoked after rehearsal or delivery.

## Required live flow

```text
participant assignment
→ minimum authorization model
→ restricted-user identity and failed request
→ administrator permission evidence and narrow repair
→ restricted-user unchanged rerun
→ lineage for fpd_analysis
→ Consumer Lending > Origination Risk
→ participant incident handover
```

Lineage should show:

```text
core_lending source tables
→ workshop_shared.fpd_analysis
→ workshop_shared.fpd_metrics
→ verified downstream dashboard or analysis
```

Do not switch to an unrelated table for lineage or discovery.

## Definitions to introduce before use

- **Principal:** user, service principal, or group that can hold permissions.
- **Runtime identity:** user or service principal for the session or workload that executes the request.
- **Group-derived access:** effective access supplied through group membership.
- **Workspace permission:** access to a notebook, Job, warehouse, dashboard, or Genie Agent.
- **Unity Catalog privilege:** permission to act on governed data or AI assets.
- **Inherited grant:** privilege received from a parent securable.
- **`BROWSE`:** metadata discovery without data access.
- **Lineage:** dependency evidence.
- **Domain:** business-aligned discovery grouping implemented with governed tags.

Avoid unexplained acronyms. If “ACL” appears, first define it as an access control list for a workspace asset.

## Participant and facilitator boundaries

Participants:

- use one integrated participant guide;
- predict, record, and interpret evidence;
- complete the incident handover;
- do not run code or change permissions.

The facilitator:

- operates separate restricted and administrator sessions;
- runs the notebook and temporary grant;
- uses Catalog Explorer, lineage, and Discover;
- keeps setup, answer keys, fallbacks, and cleanup out of participant materials.

## Optional transfer examples

Mention only if time remains; do not create additional UI demonstrations:

- interactive notebook succeeds but scheduled Job fails → inspect the Job's **Run as** identity;
- authorized users receive different rows or values → inspect policies and runtime context;
- dashboard behavior differs by **Share data permissions** versus **Individual data permissions**.

## Scope exclusions

Do not expand the core presentation to cover:

- complete securable or privilege inventories;
- live row-filter, column-mask, or ABAC configuration;
- Data Classification or PII tagging;
- storage credentials or external locations;
- Delta Sharing;
- live Domain creation;
- separate Job or dashboard-permissions walkthroughs;
- participant coding.

## Claims to avoid

Do not:

- imply notebook access proves data access;
- imply `SELECT` alone is sufficient;
- imply `BROWSE`, Domain placement, or lineage grants query access;
- claim a group executes a request;
- recommend `ALL PRIVILEGES` as a diagnostic shortcut;
- claim ten returned rows validate the FPD5 population;
- imply different authorized results are automatically failures;
- claim Domains or workspace evidence are ready before rehearsal;
- use “viewer or publisher data permissions”; use the current dashboard terms;
- imply the synthetic incident represents Home Credit production controls.

## Product and readiness facts

- Domains and the Discover page are Public Preview.
- Account- and workspace-level preview enablement must be confirmed.
- Curators require `MANAGE DISCOVERY` at the appropriate scope and permission to apply the Domain's governed tag.
- Consumers still need `BROWSE` or the relevant workspace-object viewing permission to see assigned assets.
- Underlying Unity Catalog or workspace permissions continue to govern use.

## Output request

Design effective 16:9 presentation support for this 30-minute section.

Return:

1. a short explanation of the chosen narrative and information architecture;
2. concise slide content with detailed presenter notes;
3. explicit transitions between presentation and live workspace;
4. visual or collateral recommendations;
5. Essential/Optional and Create/Curate/Hybrid labels;
6. a coverage check against the mandatory messages;
7. human-supplied screenshots or workspace evidence required;
8. a rehearsal and claim-verification checklist;
9. clear marking of every intended but unverified statement.

Use the smallest presentation that establishes the assignment and diagnostic model. Do not preserve old slide headings mechanically, fabricate workspace evidence, or broaden the scope to fill time.
