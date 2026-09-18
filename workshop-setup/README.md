# Workshop environment setup

**Updated at:** 2026-09-16

*Administrator and facilitator runbook for preparing the workshop environment.*

## Namespace plan

The workshop uses one configurable catalog and three schemas:

- `core_lending` — generated source tables; read-only for participants.
- `workshop_shared` — facilitator-managed trusted views and metrics for dashboards and Genie.
- `workshop_labs` — team-prefixed participant tables, views, and registered models.

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
11. Follow `../workshop-content/01-data-analysis-in-databricks/facilitator-guide.md` to prepare and share the dashboard and Genie Agent.
12. Rehearse `../workshop-content/01-data-analysis-in-databricks/participant-lab.py` with a non-admin participant identity.

Both Python notebooks keep their configuration visibly at the top of the source. They do not require a first run to initialize widgets.

The administrator needs permission to create the catalog through Catalog Explorer and to create schemas within it. The facilitator needs permission to create views in `workshop_shared`, author the dashboard and Genie Agent, and use the workshop SQL warehouse.

Grant participant and facilitator access separately after the identities and groups are confirmed. Unity Catalog grants do not replace workspace-resource permissions on SQL warehouses, dashboards, Genie Agents, Jobs, pipelines, or serving endpoints.
