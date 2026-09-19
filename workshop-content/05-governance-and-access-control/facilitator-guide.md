# Facilitator guide — Governance and Access Control in Databricks

**Facilitator-only:** Participants receive `access-diagnostic-checklist.md`. The notebook is a prepared demonstration, not a participant lab.

## Delivery intent

Teach a reusable authorization model, not a list of security features. Participants should leave able to identify which control system is involved and collect the evidence an administrator needs.

Use three surfaces deliberately:

- **Slides** for the layered mental model and diagnostic sequence.
- **Notebook and SQL editor** for runtime identity, the actual failure, and the narrow repair.
- **Workspace UI** for resource ACLs, inherited Unity Catalog grants, lineage, and Domains.

Do not add Data Classification, quality checks, storage credentials, external locations, Delta Sharing, or a complete privilege inventory. Those topics dilute the diagnostic objective and belong in separate sessions.

## Before participants enter

### Prepare the restricted scenario

1. Create a dedicated account group, for example `hc-workshop-governance-demo-restricted`.
2. Add one non-admin demo user to that group.
3. Confirm that the user is not in:
   - the workshop participant group;
   - a group with inherited access to the `hc_workshop` catalog;
   - a workspace-admin or metastore-admin role.
4. Replace `<governance-demo-group>` in `../../workshop-setup/section-05-governance-demo-setup.sql`.
5. Run only the **Prepare before the session** statements.
6. Grant the demo user permission to open and run `facilitator-demo.py`.
7. Grant the demo user `CAN USE` on the workshop SQL warehouse.
8. Attach the notebook to that SQL warehouse and run it through the intentional query failure.
9. From an administrator session, confirm:
   - `BROWSE` and `USE CATALOG` are present on `hc_workshop`;
   - `SELECT` is present on `hc_workshop.core_lending.customer`;
   - `USE SCHEMA` is absent on `hc_workshop.core_lending`.
10. Revoke `USE SCHEMA` after every rehearsal.

The normal participant group has broad access to the dedicated synthetic workshop catalog. Do not use it for this scenario; the query would succeed and undermine the lesson.

### Prepare the workspace UI

Keep these tabs open before the session:

1. Restricted-user browser profile: `facilitator-demo.py`, attached to the workshop SQL warehouse.
2. Administrator browser profile: **Catalog > hc_workshop > core_lending > Permissions**.
3. Administrator browser profile: **Catalog > hc_workshop > workshop_shared > fpd_analysis > Lineage**.
4. Administrator browser profile: the demonstration notebook's **Permissions** dialog.
5. Administrator browser profile: the workshop SQL warehouse's **Permissions** dialog.
6. **Discover > Consumer Lending** domain.

Use separate browser profiles or a private session so changing identities does not require signing out during the demonstration.

### Prepare the Discover domain

Create the following discovery structure if Domains are available:

```text
Consumer Lending
├── Origination Risk
└── Collections
```

Use a short domain description:

> Trusted data and analytical assets for Unicorn Finance's synthetic lending lifecycle. Domain placement aids discovery and does not replace asset permissions.

Assign a small representative set:

- `hc_workshop.core_lending.customer`
- `hc_workshop.core_lending.loan_application`
- `hc_workshop.core_lending.credit_contract`
- `hc_workshop.workshop_shared.fpd_analysis`
- **Unicorn FPD5 Overview** dashboard
- **Unicorn FPD5 Investigator** Genie Agent

Place the FPD assets under **Origination Risk**. Use the parent domain page to show that a business domain can surface both Unity Catalog and workspace assets.

Do not build the domain live. Open the prepared page, show its organization, and open one asset. Confirm the exact Domain UI and required discovery-management permission in the target workspace during rehearsal because availability and labels can differ.

### Prepare lineage

Open a lineage graph that already contains evidence from the earlier sections. Prefer:

```text
core_lending tables
        ↓
workshop_shared.fpd_analysis
        ↓
workshop_shared.fpd_metrics
        ↓
dashboard or downstream analysis
```

Verify at least one column-level path before the session. Do not generate lineage live or imply that the graph is an access-control mechanism.

## Minute-by-minute run of show

### 0:00–0:04 — One request, several authorization layers

Use slides 1–2.

Talking points:

- Databricks does not have one universal `Can access` switch.
- Identity and groups are evaluated first.
- Workspace ACLs govern resources such as notebooks, Jobs, pipelines, warehouses, dashboards, and Genie Agents.
- Unity Catalog governs data and AI securables such as tables, views, volumes, functions, and registered models.
- The executing principal might differ from the human clicking **Run**.

Ask:

> If a user can open a notebook, does that prove they can read its tables?

Expected answer: no. Notebook access, compute access, and data access are separate gates.

### 0:04–0:08 — Unity Catalog hierarchy and diagnostic sequence

Use slides 3–4.

Write or reveal:

```text
USE CATALOG → USE SCHEMA → SELECT
```

Explain:

- `BROWSE` enables discovery but not data access.
- Parent grants can be inherited.
- Ownership and `MANAGE` determine who can administer access.
- A row filter or mask can change a successful result without causing a permission error.

Transition:

> We will now diagnose a request that has two of the three required Unity Catalog privileges.

### 0:08–0:17 — Controlled runtime diagnosis

Open `facilitator-demo.py` as the restricted identity.

1. Run the identity cell. Read the active identity aloud.
2. Review the three Unity Catalog gates shown in the notebook.
3. Before running the table query, ask participants to predict the outcome.
4. Run the query and stop on the `USE SCHEMA` or insufficient-privilege error.
5. In the administrator browser, open the schema **Permissions** tab.
6. Show direct and inherited permissions for the dedicated demo group.
7. From the prepared administrator SQL editor, run only:

   ```sql
   GRANT USE SCHEMA
   ON SCHEMA hc_workshop.core_lending
   TO `<governance-demo-group>`;
   ```

8. Return to the restricted session and rerun the unchanged query.
9. Confirm that ten rows appear.

Narrate the reasoning:

- The user could sign in, open the notebook, and use the SQL warehouse.
- `USE CATALOG` and `SELECT` did not compensate for missing `USE SCHEMA`.
- The repair added the one missing privilege rather than `ALL PRIVILEGES`.

Do not demonstrate a revoke against the participant group or modify production-like permissions.

### 0:17–0:21 — Compare workspace ACLs with data privileges

Open the notebook permission dialog and the SQL warehouse permission dialog.

Show only:

- the notebook permission that lets the user open or run the asset;
- `CAN USE` on the SQL warehouse;
- the separate Unity Catalog permissions just diagnosed.

Then point to, but do not configure, a Job's **Run as** setting from the Data Engineering portion.

Ask:

> The interactive notebook works, but its scheduled Job fails. Which identity should we inspect?

Expected answer: the Job's **Run as** identity.

Avoid reading every resource's ACL vocabulary. The reusable concept is that a workspace asset and its governed data have separate permissions.

### 0:21–0:25 — Lineage as impact evidence

Use slide 6, then open the prepared lineage graph.

Show:

1. an upstream `core_lending` source;
2. `fpd_analysis` or `fpd_metrics`;
3. a downstream asset;
4. one column-level lineage path.

Ask:

> If this source column changes or access is removed, which downstream assets should the owner test?

Clarify:

- Lineage explains dependencies and supports impact analysis.
- It does not itself grant or deny access.
- Audit evidence answers a different question: which identity performed which action.

Do not introduce data-quality rules; those remain in the Data Engineering section.

### 0:25–0:29 — Domains for business discovery

Use slide 5 and open **Discover > Consumer Lending**.

Show:

- the parent domain and two subdomains;
- one Unity Catalog table;
- one dashboard or Genie Agent;
- how the same business area crosses technical asset types.

State explicitly:

> A Domain is a curated discovery layer. It does not replace the catalog hierarchy and it does not grant access to its assets.

Contrast the surfaces:

- Use **Discover** when a consumer wants trusted assets organized by business purpose.
- Use **Catalog Explorer** when an operator needs complete object details, permissions, properties, and lineage.

Do not create a Domain or assign assets live.

### 0:29–0:30 — Close

Use the first scenario in `exercises.md` or ask:

> A user finds a table in Discover but cannot query it. What does Domain membership prove?

Expected answer: it proves that the asset was curated for discovery, not that the user has `USE CATALOG`, `USE SCHEMA`, and `SELECT`.

Close with:

> Identify the principal, locate the failed layer, inspect inherited access, and apply the narrowest repair.

## Fallbacks

- **Restricted user unavailable:** show saved output from a rehearsed failure, then use the administrator Permissions tab to walk the same diagnosis. Do not manufacture an error against a participant.
- **The query unexpectedly succeeds:** stop. Check group nesting, catalog ownership, admin roles, and inherited grants. Do not claim the scenario worked.
- **Grant propagation is delayed:** refresh the notebook session and rerun once. Use saved successful output if necessary.
- **Domains unavailable:** show the Domain slide and explain the distinction, then spend the saved time in Catalog Explorer. Do not relabel catalogs as domains.
- **Lineage graph is empty:** use the previously captured lineage screenshot or a table with known notebook lineage. Do not create disposable transformations during the session.
- **Cannot inspect all grants:** switch to an owner, metastore-admin, or identity with `MANAGE` or `READ METADATA`. A normal user may only see their own grants.
- **No SQL warehouse access:** fix `CAN USE` before the session. Do not confuse the compute ACL failure with the planned Unity Catalog failure.

## After the session

1. Run the reset statement in `section-05-governance-demo-setup.sql`.
2. Confirm the restricted query fails again.
3. Leave participant access unchanged.
4. Record any UI labels or permission behavior that differed from rehearsal.

## Facilitator references

- [Access control lists](https://docs.databricks.com/aws/en/security/auth/access-control/)
- [Unity Catalog privileges and securable objects](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/)
- [Manage privileges in Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/)
- [Unity Catalog lineage](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-lineage/)
- [Discover page](https://docs.databricks.com/aws/en/discover/discover-page)
- [Data discovery in Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-discovery)
