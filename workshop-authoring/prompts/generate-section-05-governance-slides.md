# Slide-generation brief — Section 05: Governance and Access Control in Databricks

Use this document either as a complete prompt for an LLM that can generate presentation slides or as a curation guide for selecting and adapting existing Databricks slides.

## Instructions for the slide-generating LLM

Create a 16:9 deck for a 30-minute facilitator-led workshop section.

For every slide:

- provide a concise title;
- keep visible text to one message, three to five short bullets, or one simple comparison;
- recommend a visual, diagram, or verified product screenshot;
- write detailed presenter notes;
- include the live-demo transition when applicable;
- label the slide as `Essential` or `Optional`;
- label the content strategy as `Create new`, `Curate existing collateral`, or `Hybrid`.

Use clean Databricks-style enterprise visuals, restrained orange/red accents, and diagrams over dense prose. Do not use decorative stock photography, full code listings, unsupported claims, or unverified workspace screenshots.

Treat the implemented section assets and timed facilitator guide as more authoritative than the high-level agenda. Concepts and decision frameworks belong on slides. The prepared notebook and workspace UI supply execution evidence.

## Authoritative scope decision

This is a facilitator-led diagnostic session, not a participant coding lab or a broad security-feature tour.

The high-level agenda mentions fine-grained policies broadly. The implemented section:

- teaches how to distinguish a permission failure from successful row-filter or column-mask enforcement;
- does not configure row filters or column masks live;
- does not cover Data Classification, storage credentials, external locations, Delta Sharing, or a complete privilege inventory;
- uses one controlled missing-`USE SCHEMA` failure to teach a reusable diagnostic method.

Domains are presented as a discovery and curation layer, not an authorization boundary. Lineage is presented as impact evidence, not an access-control mechanism.

## Workshop scenario

- Unicorn Finance Philippines is a fictional consumer lender.
- Atlas Ridge Consulting has handed over an inherited Databricks lakehouse.
- Participants act as the new owners of the inherited analytical assets.
- All workshop data is synthetic.
- A dedicated restricted demo identity can open the notebook and use the SQL warehouse.
- The identity has `BROWSE`, `USE CATALOG`, and table `SELECT`, but initially lacks `USE SCHEMA`.
- The unchanged query succeeds only after an administrator grants the one missing privilege.
- The closing discovery example uses **Consumer Lending** with **Origination Risk** and **Collections** subdomains.

## Section analysis

### Outcomes

Participants should be able to:

1. distinguish workspace-resource ACLs from Unity Catalog privileges;
2. identify the executing principal;
3. trace a table read through `USE CATALOG → USE SCHEMA → SELECT`;
4. reason about direct and inherited grants;
5. separate a permission failure from successful row-filter or column-mask enforcement;
6. use Catalog Explorer and the exact error as diagnostic evidence;
7. distinguish a technical catalog hierarchy from a business-oriented Discover domain;
8. use lineage as impact evidence, not as an authorization mechanism.

### Timing and instructional arc

- 0:00–0:04 — layered authorization model and identity
- 0:04–0:08 — Unity Catalog hierarchy and outside-in diagnosis
- 0:08–0:17 — restricted-identity notebook failure and narrow repair
- 0:17–0:21 — workspace ACLs versus data privileges
- 0:21–0:25 — lineage as impact evidence
- 0:25–0:29 — Discover Domains
- 0:29–0:30 — verbal checkpoint and close

Use six core slides. Present the evidence/lineage slide before the Domains slide so the deck matches the live-demo order.

## Slide specifications

### Slide 1 — “Can I access it?” is not one permission

**Priority:** Essential  
**Strategy:** Hybrid

**Visible content**

`Identity and groups → workspace entitlement and resource ACL → runtime identity or credential mode → Unity Catalog privileges and policies → data result`

Examples:

- workspace resources: notebooks, Jobs, pipelines, warehouses, dashboards, Genie Agents;
- Unity Catalog securables: tables, views, volumes, functions, registered models.

Key message:

> Passing one layer does not prove that the next layer will pass.

**Recommended visual**

A vertical gate diagram. Curate generic identity and authorization iconography if useful, but use this exact layer sequence.

**Presenter notes**

Ask:

> If a user can open a notebook, does that prove they can read its tables?

Expected answer: no. Opening the notebook, using compute, and accessing data are separate gates.

**Transition**

“Before changing a permission, identify the principal that actually executes the request.”

---

### Slide 2 — Start with identity, not the error text

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

Ask four questions:

1. Who is active: user, service principal, or group?
2. Is the request interactive or automated?
3. Which identity runs the workload?
4. Does the asset use viewer or publisher data permissions?

Examples:

- interactive notebook → user;
- scheduled Job → configured Run as identity;
- dashboard → credential/data-permission mode matters.

**Recommended visual**

A three-column comparison: Interactive, Job Run as, Dashboard credential mode.

**Presenter notes**

Granting the person who reported an error does not fix a Job running as a different identity. This concept returns after the live failure when the facilitator compares notebook and warehouse permissions.

**Transition**

“Once the principal is known, trace the Unity Catalog path.”

---

### Slide 3 — Unity Catalog evaluates a hierarchy

**Priority:** Essential  
**Strategy:** Hybrid

**Curate from existing collateral**

Use a current Unity Catalog hierarchy diagram, simplified to the workshop namespace.

**Visible content**

`Metastore → Catalog hc_workshop → schemas core_lending, workshop_shared, workshop_labs → objects`

For a table read:

> `USE CATALOG + USE SCHEMA + SELECT`

Callouts:

- grants may be direct or inherited;
- `BROWSE` enables discovery, not data access;
- ownership and `MANAGE` are administrative capabilities;
- row filters and column masks refine successful access; they do not replace `SELECT`.

**Recommended visual**

A tree rooted at `hc_workshop`, with a three-gate read path highlighted.

**Presenter notes**

The controlled demo identity has `USE CATALOG` and `SELECT` but lacks `USE SCHEMA`. Ask participants to predict whether the query succeeds.

Do not show a complete privilege inventory.

**Transition**

“Let us diagnose the incomplete chain from the outside in.”

---

### Slide 4 — Diagnose from the outside in

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

`Sign in? → open asset? → use compute? → executing principal? → traverse catalog/schema? → required object action? → policy changing rows or values?`

Evidence to capture:

- identity and relevant group;
- asset and fully qualified object;
- requested action and exact error;
- runtime identity and compute;
- direct and inherited grants;
- timestamp and request ID.

**Recommended visual**

An outside-in funnel or seven-gate diagnostic path with a compact evidence packet beside it.

**Presenter notes**

This is the participant’s reusable diagnostic sequence. The narrowest repair comes only after the failed layer is located.

**Live transition**

Open `facilitator-demo.py` as the restricted identity:

1. show `current_user()`;
2. ask participants to predict the query outcome;
3. run the table query;
4. stop at the missing-`USE SCHEMA` error;
5. inspect direct and inherited grants;
6. grant only `USE SCHEMA`;
7. rerun the unchanged query and confirm ten rows appear.

After the repair, compare the notebook permission, SQL warehouse `CAN USE`, and Unity Catalog privileges. Point to a Job’s Run as setting without configuring it.

---

### Slide 5 — Governance includes evidence and accountability

**Priority:** Essential  
**Strategy:** Create new

**Visible content**

- Permissions → who may act
- Runtime identity → who actually acts
- Lineage → what depends on what
- Audit evidence → what happened
- Domains and metadata → how people find and understand assets

Key boundary:

> Lineage supports impact analysis. It does not grant or deny access.

**Recommended visual**

A five-box strip. Do not use a static lineage screenshot on the slide; use the live graph.

**Presenter notes**

Open the prepared lineage path from `core_lending` through `fpd_analysis` or `fpd_metrics` to a downstream asset. Show one column-level path.

Ask:

> If this source column changes or access is removed, which downstream assets should the owner test?

Do not introduce data-quality rules here; they belong in Data Engineering.

**Live transition**

Open the prepared lineage graph.

---

### Slide 6 — Catalogs secure; Domains curate

**Priority:** Essential  
**Strategy:** Hybrid

**Visible comparison**

Catalog hierarchy:

- technical organization;
- fully qualified names;
- privilege inheritance;
- complete object details in Catalog Explorer.

Discover Domains:

- business-oriented navigation;
- domains and subdomains;
- tables, dashboards, Genie Agents, Pages, and other trusted assets;
- consumer-oriented discovery.

Prominent boundary:

> Assigning an asset to a Domain does not grant access to it.

**Recommended visual**

A two-column comparison plus a small business tree:

`Consumer Lending → Origination Risk / Collections`

**Presenter notes**

Open the prepared **Consumer Lending** domain. Show one table and one dashboard or Genie Agent. Do not create a Domain or assign assets live.

Contrast:

- Discover for consumers seeking trusted assets by business purpose.
- Catalog Explorer for operators inspecting object details, permissions, properties, and lineage.

Close verbally:

> Identify the principal, locate the failed layer, inspect inherited access, and apply the narrowest repair.

Checkpoint question:

> A user finds a table in Discover but cannot query it. What does Domain membership prove?

Expected answer: curation for discovery only, not `USE CATALOG`, `USE SCHEMA`, or `SELECT`.

## Keep off the slides

- Exact `GRANT` and `REVOKE` syntax
- Full securable and privilege inventories
- Every workspace-resource ACL vocabulary
- Domain creation steps
- Browser-profile setup
- Restricted group name and user
- Long troubleshooting trees
- Data Classification and automated PII tagging
- Storage credentials, external locations, or Delta Sharing
- Live row-filter or column-mask configuration

## Collateral-curation search terms

- Databricks authorization layers
- Unity Catalog three-level namespace
- Unity Catalog privilege inheritance
- workspace ACL versus data permission
- Job Run as identity
- Unity Catalog lineage
- Discover Domains
- Catalog Explorer versus Discover

Curate high-level diagrams only. The controlled `USE SCHEMA` failure, outside-in diagnostic sequence, and Catalog-versus-Domains comparison are workshop-specific and should be newly created.

## Verify before final slide export

1. Exact missing-`USE SCHEMA` error text in the target workspace.
2. `BROWSE` and discovery behavior for the restricted identity.
3. Dashboard viewer/publisher data-permission terminology.
4. Current ownership and `MANAGE` language.
5. Grant propagation delay and required refresh behavior.
6. Prepared lineage path and column-level lineage visibility.
7. Discover Domains availability, labels, and required permissions.
8. Warehouse, restricted user/group, and Domain values still marked `TBD`.

Until rehearsal confirms these details, use conceptual diagrams rather than unverified screenshots and do not hardcode URLs or identity names.

## Final output request

Return:

1. the final slide order;
2. slide title and concise on-slide copy;
3. recommended visual or source collateral;
4. detailed speaker notes;
5. live-demo transition;
6. Essential/Optional label;
7. Create/Curate/Hybrid label;
8. a list of screenshots, diagrams, or existing slides the human author must supply;
9. a final claim-verification checklist.

Do not generate implementation details that belong in notebooks, facilitator guides, or workspace setup. Do not expand the section scope merely to fill slides. If an agenda item is unsupported by the authored workshop assets, identify the gap instead of fabricating content.
