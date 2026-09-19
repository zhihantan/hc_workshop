# Facilitator guide — Governance and Access Control in Databricks

**Facilitator-only · 30 minutes**

Participants use only `../../../workshop-content/05-governance-and-access-control/participant-guide.md`. The facilitator screen-shares `facilitator-demo.py` from a private facilitator folder and runs it as the dedicated restricted identity.

## Delivery intent

Teach one repeatable operating method through one business incident:

> A risk analyst can discover `hc_workshop.workshop_shared.fpd_analysis` under Consumer Lending > Origination Risk, but cannot query it.

The same governed view anchors discovery, the failed request, the narrow repair, verification, lineage, and the final handover. Do not turn the session into a privilege inventory or a tour of unrelated governance features.

## Authoritative participant outcome

By the close, every participant should have one incident handover containing:

- runtime principal;
- exact failed gate and supporting evidence;
- narrowest approved repair;
- verification from the unchanged request;
- at least one downstream asset to retest;
- the Domain discovery-versus-authorization boundary;
- one owner, risk, and recovery action.

## Before participants enter

### Prepare the restricted scenario

1. Create a dedicated account group, for example `hc-workshop-governance-demo-restricted`.
2. Add one non-admin demo user to that group.
3. Confirm that the user is not a workspace admin, metastore admin, catalog owner, member of the workshop participant group, or member of any group with broader access to `hc_workshop`.
4. Replace `<governance-demo-group>` in `../../../workshop-setup/section-05-governance-demo-setup.sql`.
5. Run only the **Prepare before the session** statements.
6. Import `facilitator-demo.py` into a private facilitator workspace folder.
7. Grant the demo user `CAN RUN` on the notebook and `CAN USE` on the workshop SQL warehouse.
8. Attach the notebook to the SQL warehouse.
9. Confirm the dedicated group has:
   - `BROWSE` and `USE CATALOG` on `hc_workshop`;
   - `SELECT` on `hc_workshop.workshop_shared.fpd_analysis`;
   - no direct or inherited `USE SCHEMA` on `hc_workshop.workshop_shared`.
10. Run through the intentional failure, apply the live grant, verify success, and reset.

The normal participant group has broad workshop access. Do not use a participant identity for this scenario.

### Prepare the workspace surfaces

Keep these tabs open:

1. Restricted-user profile: the demonstration notebook attached to the SQL warehouse.
2. Administrator profile: **Catalog > hc_workshop > workshop_shared > Permissions**.
3. Administrator SQL editor: the prepared live `GRANT USE SCHEMA` statement.
4. Administrator profile: **Catalog > hc_workshop > workshop_shared > fpd_analysis > Lineage**.
5. **Discover > Consumer Lending > Origination Risk**.

Use separate browser profiles so the live sequence does not require signing out.

### Prepare lineage

Verify this path before delivery:

```text
core_lending source tables
        ↓
workshop_shared.fpd_analysis
        ↓
workshop_shared.fpd_metrics
        ↓
Unicorn FPD5 Overview or another verified consumer
```

Confirm at least one table-level path and one column-level path. Do not generate lineage live. Lineage is dependency evidence, not authorization or result validation.

### Prepare Discover Domains

Domains and the Discover page are Public Preview. Confirm that the target account has enabled:

- **Domains and Discover Page** at account level;
- **Discover Page** for the workshop workspace.

Confirm the curator has `MANAGE DISCOVERY` at the appropriate scope and permission to apply the Domain's governed tag to each assigned asset.

Prepare and publish:

```text
Consumer Lending
├── Origination Risk
└── Collections
```

Use this description:

> Trusted data and analytical assets for Unicorn Finance's synthetic lending lifecycle. Domain placement supports discovery and does not replace asset permissions.

Assign `hc_workshop.workshop_shared.fpd_analysis` and `fpd_metrics` to **Origination Risk**. Add **Unicorn FPD5 Overview** only if its permissions and visibility have been verified.

The walkthrough must use `fpd_analysis`, the same asset as the access incident. Do not create a Domain or assign tags live.

## Minute-by-minute run of show

### 0:00–0:03 — Give the assignment

Use the slide titled **Restore access without overgranting**.

Ask participants to open the participant guide. State their role, the incident, the seven questions they must answer, and the final handover they will produce.

Establish two boundaries:

- the data and identities are synthetic;
- the ten-row query is an access smoke test, not a recalculation or validation of FPD5.

### 0:03–0:07 — Explain only the request path needed now

Use **Why finding an asset does not mean you can query it** and **Collect evidence before changing access**.

Define in plain language:

- principal and runtime identity;
- workspace permission;
- Unity Catalog privilege;
- inherited grant;
- `BROWSE`;
- lineage;
- Domain.

Show:

```text
Notebook CAN RUN
        ↓
SQL warehouse CAN USE
        ↓
Runtime principal
        ↓
USE CATALOG → USE SCHEMA → SELECT
```

Ask:

> If the analyst can open the notebook and find the view in Discover, which gates are proven—and which remain unknown?

Do not reveal the missing privilege yet.

### 0:07–0:16 — Diagnose and repair the same request

Open `facilitator-demo.py` as the restricted identity.

1. Run the identity cell and have participants record the runtime principal.
2. Review the read path and ask for a prediction.
3. Run the `fpd_analysis` query.
4. Stop at the insufficient-privilege error.
5. Have participants record the exact error and request ID.
6. Open the `workshop_shared` Permissions tab as the administrator.
7. Show direct and inherited evidence for the dedicated group.
8. Ask participants to name the first failed gate and propose the narrowest repair.
9. Run only:

   ```sql
   GRANT USE SCHEMA
   ON SCHEMA hc_workshop.workshop_shared
   TO `<governance-demo-group>`;
   ```

10. Return to the restricted session and run the unchanged query.
11. Confirm that ten synthetic rows appear.

Narrate why changing only one variable creates stronger diagnostic evidence. Do not grant `ALL PRIVILEGES`, change the query, or modify participant access.

### 0:16–0:20 — Explain what the result proves

Use **Prove the repair and assess the impact**.

Connect the observed evidence:

- notebook `CAN RUN` let the identity execute cells;
- warehouse `CAN USE` let it submit SQL;
- `current_user()` established the runtime principal;
- the original error isolated the missing schema traversal privilege;
- the unchanged rerun verified the narrow repair.

Clarify that the result does not prove unrestricted row visibility or validate the business definition. If discussing dashboards, use the current terms **Share data permissions** and **Individual data permissions**. Do not open another dashboard-permissions demonstration.

### 0:20–0:24 — Assess downstream impact

Open lineage for `fpd_analysis`.

Show:

1. an upstream `core_lending` source;
2. `fpd_analysis`;
3. `fpd_metrics`;
4. the verified dashboard or other downstream consumer;
5. one column-level path.

Ask participants to record which assets require retesting if `fpd_analysis` changes. State that lineage supports impact analysis but does not grant access or prove correctness.

### 0:24–0:27 — Return to the business discovery surface

Open **Consumer Lending > Origination Risk** and select `fpd_analysis`.

Explain:

- Domains group assets by business purpose using governed tags;
- `BROWSE` or the appropriate workspace-object view permission determines whether a consumer can see an assigned asset;
- underlying Unity Catalog privileges still control data access;
- Catalog Explorer is the operator surface for complete technical metadata, permissions, properties, and lineage.

State explicitly:

> Domain placement proves curation for discovery. It does not grant `USE CATALOG`, `USE SCHEMA`, or `SELECT`.

### 0:27–0:30 — Complete the incident handover

Give participants three minutes to complete the handover template in their guide.

Ask one participant to state:

- the runtime principal;
- the failed gate and evidence;
- the narrow repair and verification;
- one downstream asset;
- the Domain boundary;
- one owner, risk, and recovery action.

Close with:

> Identify the principal, locate the first failed gate, preserve the request, and apply the narrowest approved repair.

## Expected evidence and answer key

Before the repair, the restricted identity can:

- sign in;
- run the notebook;
- use the SQL warehouse;
- discover the catalog and view metadata;
- pass `USE CATALOG`;
- hold `SELECT` on `fpd_analysis`.

The query fails because the identity lacks:

```text
USE SCHEMA ON SCHEMA hc_workshop.workshop_shared
```

After the administrator grants only `USE SCHEMA`, the unchanged query returns ten rows with:

- `application_id`;
- `contract_id`;
- `origination_date`;
- `promotion_cohort`;
- `fpd5_flag`.

Expected participant handover:

- **Principal:** dedicated restricted demo user.
- **Failed layer:** Unity Catalog schema traversal.
- **Evidence:** exact error plus the direct and inherited grants on `workshop_shared`.
- **Repair:** `USE SCHEMA` on `hc_workshop.workshop_shared` for the dedicated group.
- **Premature changes:** `ALL PRIVILEGES`, object ownership, or grants to the human reporter without confirming runtime identity.
- **Verification:** the same SQL under the same identity and warehouse succeeds.
- **Impact:** `fpd_metrics` and the verified downstream dashboard or analysis require retesting after a definition or schema change.
- **Discovery boundary:** Domain placement curates the asset but does not authorize reading it.

If the query succeeds before the live grant, stop. The demo identity has broader access through ownership, an administrative role, nested group membership, or an inherited grant.

## Optional transfer examples

Use only if time remains:

- An interactive notebook succeeds but a scheduled Job fails: inspect the Job's configured **Run as** identity before changing the interactive user's grants.
- Two authorized users receive different rows or masked values: inspect row filters, column masks, ABAC policies, dynamic views, and—when a dashboard is involved—its selected data-permission mode.

Do not turn either example into another UI walkthrough.

## Fallbacks

- **Restricted identity unavailable:** use captured output from a rehearsed failure and walk the same permission evidence. Do not manufacture an error against a participant.
- **Query unexpectedly succeeds:** inspect ownership, admin roles, nested groups, and inherited access. Do not continue as though the scenario worked.
- **Grant propagation is delayed:** refresh once and rerun the unchanged query. Use captured successful output if necessary.
- **Domains unavailable:** explain the incident from the assignment slide and use a captured Domain image if approved. Spend the saved time in Catalog Explorer. Do not relabel catalogs as Domains.
- **Lineage is incomplete:** use a verified capture of the same `fpd_analysis` path. Do not switch to an unrelated asset.
- **Cannot inspect all grants:** use an owner, metastore admin, or principal with sufficient `READ METADATA` or `MANAGE` and required parent usage privileges.
- **No SQL warehouse access:** correct `CAN USE` before delivery. Do not confuse that failure with the planned Unity Catalog failure.

## After rehearsal or delivery

1. Run the reset statement in `../../../workshop-setup/section-05-governance-demo-setup.sql`.
2. Confirm the restricted query fails again.
3. Leave participant access unchanged.
4. Record changed UI labels, errors, preview behavior, or grant propagation.

## References

- [Workspace object access control](https://docs.databricks.com/security/auth/access-control/)
- [Unity Catalog permissions concepts](https://docs.databricks.com/data-governance/unity-catalog/access-control/permissions-concepts)
- [Manage Unity Catalog privileges](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/)
- [Unity Catalog lineage](https://docs.databricks.com/data-governance/unity-catalog/data-lineage/)
- [Discover page](https://docs.databricks.com/discover/discover-page)
- [Domains and subdomains](https://docs.databricks.com/uc-semantics/domains)
- [AI/BI dashboard data permissions](https://docs.databricks.com/dashboards/share/share)
