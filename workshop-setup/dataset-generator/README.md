# Unicorn Finance workshop dataset generator

**Updated at:** 2026-09-16

*Administrator runbook for provisioning the synthetic eight-table Unicorn Finance dataset used in the Home Credit Databricks workshop.*

## What this creates

The generator creates or reuses the configured dataset schema:

```text
Catalog: hc_workshop
Schema:  core_lending
```

Create the catalog manually in Catalog Explorer with **Use default storage**, then run `../setup_workshop_schemas.py` to create the complete three-schema workshop layout. The generator can create its configured dataset schema when needed, but it deliberately does not create the catalog.

It builds, validates, and publishes these managed Delta tables:

1. `customer` — one borrower or prospect.
2. `retail_location` — one physical partner store.
3. `loan_product` — one product version and commercial rule set.
4. `loan_application` — one credit request and underwriting outcome.
5. `credit_contract` — one approved application converted to a contract.
6. `installment` — one scheduled fixed-term obligation.
7. `payment` — one posted or failed payment attempt.
8. `collection_action` — one action against one delinquent installment.

All records are synthetic. The dataset is general core-lending data; Nova Mobile's campaign is one intentionally visible cohort for analysis, not the scope of the entire dataset. For that campaign, approved customers finance selected smartphones over 6, 9, or 12 months at 0% monthly interest, Nova Mobile supplies a brand subsidy, and a processing fee may still apply. “0%” does not mean a free phone, zero down payment, zero fees, or guaranteed approval.

## Files

- `generate_workshop_dataset.py` — Databricks source notebook; provisions and generates everything.
- `validate_workshop_dataset.sql` — Optional SQL notebook with additional validation and story checks.

Participant references are distributed separately from the generator ZIP. In the source repository they are under `participant-materials/`:

- `../../participant-materials/dataset-guide.pdf`
- `../../participant-materials/data-dictionary.pdf`

## Administrator prerequisites

Run on Databricks compute that:

- Has Unity Catalog enabled.
- Supports Python and Spark.
- Can create managed Delta tables.

The run identity requires:

- Permission to create the catalog manually in Catalog Explorer before running setup.
- `USE CATALOG` and `CREATE SCHEMA` on the configured catalog if the schema does not exist.
- `USE SCHEMA` and `CREATE TABLE` on the configured dataset schema and permission to create a temporary run-scoped build schema.
- `SELECT`, `MODIFY`, and ownership or equivalent management rights on existing generated tables when rerunning with `write_mode = overwrite`.
- Permission to `COMMENT ON TABLE` and set table properties.

Workspace catalog bindings must allow the workspace to access `hc_workshop`.

## Install in a workspace

### Option 1: Git folder

1. In Databricks, create a Git folder and clone this repository.
2. Open `workshop-setup/dataset-generator/generate_workshop_dataset.py`.

### Option 2: Upload an archive

1. Upload `workshop-setup/workshop-setup.zip`.
2. Extract it into a Databricks workspace folder.
3. Follow `workshop-setup/README.md`, beginning with manual catalog creation.
4. Run `workshop-setup/setup_workshop_schemas.py`.
5. Open `workshop-setup/dataset-generator/generate_workshop_dataset.py`.

The generator uses only built-in PySpark functions. No `%pip install`, wheel build, external storage path, workspace URL, cluster ID, or Databricks CLI profile is required.

## Run

1. Open `generate_workshop_dataset.py`.
2. Attach Unity Catalog-compatible workspace compute.
3. Edit and review the configuration values in the first Python cell.
4. Select **Run all**.
5. Review the displayed row counts, checksums, structural checks, and promotion-cohort comparison.
6. Confirm that the final cell prints `SUCCESS: generated, validated, and published`.

Do not release the dataset to participants when the notebook ends before the final `SUCCESS` message.

Default configuration:

| Parameter | Default | Meaning |
|---|---|---|
| `catalog` | `hc_workshop` | Unity Catalog catalog to create/use |
| `schema` | `core_lending` | Schema to create/use |
| `master_seed` | `20260922` | Deterministic master seed |
| `as_of_date` | `2026-09-01` | Fixed reporting date used for servicing state |
| `scale` | `standard` | Dataset size |
| `write_mode` | `overwrite` | Replace the eight generated tables |

## Scale options

| Scale | Customers | Locations | Applications | Use |
|---|---:|---:|---:|---|
| `small` | 1,500 | 100 | 4,000 | Permission and smoke testing |
| `standard` | 15,000 | 1,000 | 40,000 | Workshop default |
| `large` | 75,000 | 5,000 | 200,000 | Performance demonstration |

Contract, installment, payment, and collection row counts are derived from applications, approvals, tenors, and repayment behavior.

Use `small` first when validating a new workspace. Rerun with `standard` after permissions and compute are confirmed.

## Reproducibility

The generator does not depend on Python’s global random state, Faker, Spark partition placement, or execution order.

Each pseudo-random value is derived from:

```text
SHA-256(master_seed | generator_version | field_namespace | stable_row_id)
```

For identical:

- generator code/version,
- master seed,
- as-of date,
- scale,
- static lookup lists,

the logical table rows are identical across workspaces. Delta transaction versions, file names, partition layout, and physical file bytes can differ.

Each table records these properties:

- `workshop.generator`
- `workshop.generator_version`
- `workshop.master_seed`
- `workshop.as_of_date`
- `workshop.scale`
- `workshop.run_id`
- `workshop.synthetic`

The notebook displays an order-independent logical checksum for comparing runs.

## Rerunning safely

The notebook first verifies that every existing target or build table is Delta and carries `workshop.generator = unicorn_finance_workshop`. It also accepts the legacy `home_credit_workshop` marker so previously generated workshop tables can be upgraded safely. It refuses to overwrite unrelated objects even when the run identity has permission.

Generation happens in a run-unique `<schema>__build_<suffix>` schema, so concurrent runs cannot overwrite each other. Structural and story gates run there before any target table is published. A target-schema lock serializes publishers. Target tables are then deep-cloned sequentially; if any publish step or final run-ID check fails, completed replacements are restored to their prior Delta versions (or dropped on a first release). Participants should wait for the final `SUCCESS` message.

`write_mode = overwrite` replaces only the eight known generator-owned table names in the selected namespace. It does not drop the target catalog or schema. The temporary build schema is removed after a successful publication and retained for diagnosis after a failed publication.

Use a dedicated catalog/schema. Do not point the notebook at a production schema.

`write_mode = error` checks all eight target names before generation and stops if any exists.

## Additional validation

Open `validate_workshop_dataset.sql`, attach a SQL-capable compute resource, edit the three SQL variables at the top to match the generator, and select **Run all**. The defaults remain `hc_workshop`, `core_lending`, and `2026-09-01`.

Expected results:

- Eight tables are present.
- Primary-key duplicate counts are zero.
- Foreign-key orphan counts are zero.
- Contract and payment consistency failures are zero.
- Collection outcomes reconcile to posted payment events.
- POS installment is the largest product cohort.
- The 0% smartphone promotion has elevated first-payment default.
- First-payment default is concentrated in a minority of stores/associates.
- The top 20% of stores account for at least 75% of in-store applications.
- Collection actions appear at 5, 30, 60, and 90 DPD.

## Troubleshooting

### Catalog does not exist

Open Catalog Explorer, create the configured catalog with **Use default storage**, then rerun `setup_workshop_schemas.py`. Do not add a guessed managed-storage location to the generator.

### Catalog exists but is not visible

Check workspace catalog bindings and `USE CATALOG` privileges.

### Cannot overwrite a table

Use the table owner or grant the run identity `SELECT` and `MODIFY`. If the table is not marked as owned by this generator, use a new dedicated schema; the safety check deliberately refuses to replace it.

### Publication lock already exists

Another generator may be publishing. If no run is active, inspect `<catalog>.<schema>._generator_publication_lock`; its `run_id` and `acquired_at` identify the interrupted publisher. After confirming the lock is stale, an owner can drop that lock table and rerun. Do not remove it while another publication is active.

### Serverless is unavailable

Attach any running Unity Catalog-compatible all-purpose compute. The notebook does not depend on serverless-specific APIs.

### Checksums differ between workspaces

Confirm the generator version, seed, as-of date, scale, and code are identical. Physical Delta files are not expected to match; compare the logical checksum displayed by the notebook.
