# Recommended slide outline — Section 05

Use six concise slides. Slides establish the mental model; the workspace supplies the evidence.

## Slide 1 — One request, several authorization layers

**Title:** "Can I access it?" is not one permission

Show:

```text
Identity and groups
        ↓
Workspace entitlement and resource ACL
        ↓
Runtime identity / credential mode
        ↓
Unity Catalog privileges and policies
        ↓
Data result
```

Examples:

- Notebook, Job, pipeline, dashboard, Genie Agent, and SQL warehouse access use workspace-resource permissions.
- Tables, views, volumes, functions, and registered models use Unity Catalog privileges.
- A workflow can pass one layer and fail the next.

Key message: locate the failed layer before changing permissions.

## Slide 2 — Start with identity, not the error text

Ask four questions:

1. Who is the active user, service principal, or group?
2. Is the request interactive or automated?
3. Which identity runs the workload?
4. Is a dashboard or other asset using viewer or publisher data permissions?

Examples to name:

- A user runs an interactive notebook as themselves.
- A scheduled Job uses its configured **Run as** identity.
- A dashboard's credential mode can change whose data permissions apply.

Key message: granting a human user more access does not repair a Job running as a different principal.

## Slide 3 — Unity Catalog evaluates a hierarchy

Show only the hierarchy used in this workshop:

```text
Metastore
└── Catalog: hc_workshop
    ├── Schema: core_lending
    │   └── Tables
    ├── Schema: workshop_shared
    │   ├── Views and Metric Views
    │   └── Functions
    └── Schema: workshop_labs
        ├── Participant tables
        └── Registered models
```

For a table read:

```text
USE CATALOG + USE SCHEMA + SELECT
```

Call out:

- Grants can be direct or inherited from a parent.
- Ownership and `MANAGE` are administrative capabilities, not reasons to grant everyone `ALL PRIVILEGES`.
- `BROWSE` enables discovery without granting data access.
- Row filters and column masks refine successful access; they do not replace `SELECT`.

Transition: "Let us diagnose one deliberately incomplete privilege chain."

## Slide 4 — Diagnose from the outside in

Use this sequence:

```text
Can the user sign in?
        ↓
Can they open the workspace asset?
        ↓
Can they use its compute?
        ↓
Which principal executes the request?
        ↓
Can it traverse catalog and schema?
        ↓
Does it have the required object action?
        ↓
Is a policy changing rows or values?
```

Evidence to capture before changing anything:

- active identity and group;
- asset URL/name and fully qualified data object;
- action attempted and exact error;
- runtime or credential identity;
- compute and access mode;
- direct and inherited grants;
- timestamp and request ID.

Transition to `facilitator-demo.py`.

## Slide 5 — Catalogs secure; Domains curate

**Catalog hierarchy**

- Technical organization and privilege inheritance.
- Contains Unity Catalog securables.
- Used in fully qualified names such as `hc_workshop.core_lending.customer`.

**Discover Domains**

- Business-oriented navigation across tables, dashboards, Genie Agents, Pages, and other assets.
- Can use domains and subdomains such as **Consumer Lending > Origination Risk**.
- Helps consumers find trusted assets without learning the technical hierarchy first.

Boundary:

> Assigning an asset to a Domain does not grant access to it. The underlying Unity Catalog privileges or workspace ACLs still apply.

Transition to the prepared Discover domain.

## Slide 6 — Governance includes evidence and accountability

Show:

```text
Permissions → who may act
Runtime identity → who actually acts
Lineage → what depends on what
Audit evidence → what happened
Domains and metadata → how people find and understand assets
```

Use the live lineage graph rather than placing a screenshot on the slide.

Close with the diagnostic rule:

> Identify the principal, locate the failed layer, inspect inherited access, and apply the narrowest repair.

## Keep off the slides

Use the live workspace or participant checklist for:

- Complete securable and privilege inventories.
- Exact `GRANT` and `REVOKE` syntax.
- Full permission matrices for every workspace asset.
- Domain creation steps.
- Long troubleshooting decision trees.
- Data Classification and automated PII tagging.
