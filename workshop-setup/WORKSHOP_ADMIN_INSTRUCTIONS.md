# Workshop administrator setup instructions

Use these instructions to prepare the Databricks workspace before the workshop.

## 1. Upload the zipped file

Upload the zipped workshop setup file into your workspace directory.

## 2. Create the catalog manually

1. Open **Catalog** in the Databricks sidebar.
2. Select **Create catalog**.
3. Enter `hc_workshop`.
4. Use the managed storage location of your preference, and add a sub path for this catalog
5. Create the catalog.

## 3. Create the workshop schemas

Open and run:

`workshop-setup/setup_workshop_schemas.py`

Confirm that these schemas report `READY`:

- `hc_workshop.core_lending`
- `hc_workshop.workshop_shared`
- `hc_workshop.workshop_labs`

## 4. Generate the workshop dataset

Open:

`workshop-setup/dataset-generator/generate_workshop_dataset.py`

Keep the standard workshop configuration:

- Catalog: `hc_workshop`
- Schema: `core_lending`
- Scale: `standard`
- As-of date: `2026-09-01`

Run all cells. Do not continue unless the final cell reports:

`SUCCESS: generated, validated, and published`

## 5. Run the additional dataset checks

Open and run:

`workshop-setup/dataset-generator/validate_workshop_dataset.sql`

The structural and integrity checks should report zero failures.

## 6. Create the shared data-analysis assets

Attach a Serverless SQL warehouse and run:

`workshop-setup/section-01-facilitator-setup.sql`

This creates:

- `hc_workshop.workshop_shared.fpd_analysis`
- `hc_workshop.workshop_shared.fpd_metrics`

## 7. Grant participant catalog access

Replace `<participant-group>` with the account group assigned to participants:

```sql
GRANT USE CATALOG
ON CATALOG hc_workshop
TO `<participant-group>`;

GRANT USE SCHEMA, SELECT
ON SCHEMA hc_workshop.core_lending
TO `<participant-group>`;

GRANT USE SCHEMA
ON SCHEMA hc_workshop.workshop_shared
TO `<participant-group>`;

GRANT SELECT
ON VIEW hc_workshop.workshop_shared.fpd_analysis
TO `<participant-group>`;

GRANT SELECT
ON VIEW hc_workshop.workshop_shared.fpd_metrics
TO `<participant-group>`;

GRANT USE SCHEMA, CREATE TABLE
ON SCHEMA hc_workshop.workshop_labs
TO `<participant-group>`;
```

These are the minimum Unity Catalog grants for Sections 01 and 02. Add only the section-specific privileges documented for other sections. Do not grant catalog-wide `ALL PRIVILEGES` or `MANAGE`.

Participants can read protected workshop sources and shared FPD5 assets, then create participant-owned lab tables. They cannot modify `core_lending` or facilitator-managed objects in `workshop_shared`.

## 8. Configure participant workspace access

Participants already have workspace access. Also confirm:

- The **Databricks SQL access** entitlement is enabled.
- Participants have `CAN USE` on each workshop SQL warehouse they will use.
- Serverless interactive notebook compute is enabled for the workspace.
- Partner-powered AI features are enabled at both the account and workspace levels.
- Each participant can create a Genie Agent in their own `/Workspace/Users/<workspace-username>` folder.
- Participant user folders retain their default private permissions. Do not grant the participant group access to `/Workspace/Users` or place participant Agents in `/Workspace/Shared`.

Serverless notebooks normally require no separate compute ACL. Section 02 uses the assigned Serverless notebook compute. If an approved classic cluster is used only as the documented Section 01 fallback, grant participants `CAN ATTACH TO` on that cluster.
