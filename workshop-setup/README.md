# Workshop environment setup

**Updated at:** 2026-09-16

*Administrator and facilitator runbook for preparing the workshop environment.*

For a standalone checklist that can be sent to the workspace administrator, use [WORKSHOP_ADMIN_INSTRUCTIONS.md](WORKSHOP_ADMIN_INSTRUCTIONS.md).

## Namespace plan

The workshop uses one configurable catalog and three schemas:

- `core_lending` — generated source tables; read-only for participants.
- `workshop_shared` — facilitator-managed trusted views and metrics for dashboards and Genie.
- `workshop_labs` — participant-owned tables, views, and registered models with per-user prefixes.

No participant-specific or model-only schema is required for this workshop.

## Run order

1. In the Databricks workspace, open **Catalog** and select **Create catalog**.
2. Name the catalog `hc_workshop`, select **Use default storage**, and create it.
3. Open `setup_workshop_schemas.py`.
4. Confirm its catalog and schema names, attach Unity Catalog-enabled compute, and select **Run all**.
5. Confirm that the notebook reports all three schemas as `READY`.
6. Open `dataset-generator/generate_workshop_dataset.py`.
7. Confirm it uses the same catalog and the `core_lending` schema.
8. Follow `dataset-generator/README.md` to generate and validate the tables.
9. Open `section-01-facilitator-setup.sql` on the workshop SQL warehouse.
10. Run all cells to create `workshop_shared.fpd_analysis` and the `workshop_shared.fpd_metrics` Metric View.
11. Follow `../workshop-authoring/sections/01-data-analysis-in-databricks/facilitator-guide.md` to prepare and share the dashboard.
12. With a non-admin participant identity, rehearse `../workshop-content/01-data-analysis-in-databricks/participant-lab.py` and create one private Genie Agent in that user's folder using only `workshop_shared.fpd_metrics`.
13. Create the dedicated restricted group and non-admin user described in `../workshop-authoring/sections/05-governance-and-access-control/facilitator-guide.md`.
14. Configure `section-05-governance-demo-setup.sql` with that group and run only its preparation statements; do not select **Run all**.
15. Import `../workshop-authoring/sections/05-governance-and-access-control/facilitator-demo.py` into a private facilitator workspace folder and rehearse it from the restricted identity. Participants do not run or clone it.
16. If the Public Preview is approved for the target environment, enable **Domains and Discover Page** for the account and **Discover Page** for the workshop workspace.
17. Give the curator `MANAGE DISCOVERY` at the required scope, prepare **Consumer Lending > Origination Risk**, and assign `workshop_shared.fpd_analysis` using the Domain's governed tag.
18. Verify the lineage path from `workshop_shared.fpd_analysis` to `fpd_metrics` and the prepared FPD5 dashboard.

Both Python notebooks keep their configuration visibly at the top of the source. They do not require a first run to initialize widgets.

The administrator needs permission to create the catalog through Catalog Explorer and to create schemas within it. For Sections 01 and 02, participants need `USE CATALOG`; read access to `core_lending`, `workshop_shared.fpd_analysis`, and `workshop_shared.fpd_metrics`; and `USE SCHEMA` plus `CREATE TABLE` on `workshop_labs`. They also need Databricks SQL access, `CAN USE` on the workshop SQL warehouse, and permission to create a Genie Agent in their private user folder. The facilitator needs permission to create views in `workshop_shared`, author and share the dashboard, use the workshop SQL warehouse, inspect and manage the demonstration grants, and—when the preview is used—curate the Discover domain and apply its governed tag.

Grant participant and facilitator access separately after the identities and groups are confirmed. Do not use catalog-wide `ALL PRIVILEGES` as a shortcut. Unity Catalog grants do not replace workspace-resource permissions on SQL warehouses, dashboards, Genie Agents, Jobs, pipelines, or serving endpoints.
