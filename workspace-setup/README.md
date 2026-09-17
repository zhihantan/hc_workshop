# Workshop workspace setup

**Updated at:** 2026-09-16

*Administrator runbook for creating the workshop namespaces and publishing the synthetic core-lending dataset.*

## Namespace plan

The workshop uses one configurable catalog and three schemas:

- `core_lending` — generated source tables; read-only for participants.
- `workshop_shared` — facilitator-managed trusted views and metrics for dashboards and Genie.
- `workshop_labs` — team-prefixed participant tables, views, and registered models.

No participant-specific or model-only schema is required for this workshop.

## Run order

1. Open `setup_workshop_schemas.py`.
2. Edit the catalog and schema names in its top configuration cell.
3. Attach Unity Catalog-enabled compute and select **Run all**.
4. Confirm that the notebook reports all three schemas as `READY`.
5. Open `dataset-generator/generate_workshop_dataset.py`.
6. Set its top configuration cell to the same catalog and `core_lending` schema.
7. Follow `dataset-generator/README.md` to generate and validate the tables.

Both Python notebooks keep their configuration visibly at the top of the source. They do not require a first run to initialize widgets.

The administrator needs permission to create the catalog when it does not exist and to create schemas within it. Grant participant and facilitator access separately after the identities and groups are confirmed.
