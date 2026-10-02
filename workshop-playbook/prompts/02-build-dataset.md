# Prompt 02 — Design and generate the synthetic dataset

**Use when:** the story and section plan are approved.
**Produces:** dataset design, source schema and ER diagram, data dictionary, participant dataset guide, a deterministic generator notebook, validation SQL, and reference values in the facts file.
**Next:** `03-build-environment-setup.md`.

## Prompt

````text
Design and build the synthetic dataset for this workshop.

Read first:
1. workshop-playbook/workshop-standards.md
2. workshop-authoring/workshop-facts.md
3. workshop-authoring/story/<company>-story.md
4. workshop-authoring/agenda/workshop-agenda.md
5. For reference only: the Home Credit generator design in workshop-playbook/examples/home-credit-unicorn-finance-facts.md (section 4)

## Inputs

REPOSITORY_ROOT: [absolute path]
DEV_WORKSPACE_PROFILE: [Databricks CLI profile for testing, or NONE]
TARGET_SCALE_ROWS: [approximate total rows at standard scale]

## Phase 1 — Design (stop for approval)

1. Propose the smallest set of tables (aim for six to ten) that supports every section's assignment. For each table: grain, primary key, foreign keys, purpose, and which sections use it.
2. List the story signals that must appear after aggregation (concentrations, cohort differences, time patterns) and the expected size of each effect. The signal must be visible but not absurd.
3. List the columns needed for governance exercises (personal identifiers to mask, a column for row filtering) and for ML (origination-time features versus outcome columns that would leak).
4. List what is deliberately out of scope and why.
5. Draw the ER model in Mermaid.

## Phase 2 — Build (after approval)

Create:

- workshop-authoring/dataset/dataset-design.md — story, tables, distributions, how each section uses the data.
- workshop-authoring/dataset/source-schema.md and diagrams/<name>-er.mmd (plus PNG and SVG exports).
- workshop-authoring/dataset/data-dictionary.md — every column, type, meaning in plain English, allowed values.
- workshop-authoring/dataset/dataset-guide.md — participant-facing guide; render it and the data dictionary to PDF in participant-materials/.
- workshop-setup/dataset-generator/generate_workshop_dataset.py — Databricks source notebook.
- workshop-setup/dataset-generator/validate_workshop_dataset.sql — structural and story checks.
- workshop-setup/dataset-generator/README.md — administrator runbook.

Generator requirements:

- Configuration in the first cell: catalog, schema, master_seed, as_of_date, scale (small, standard, large), write_mode (overwrite, error).
- Deterministic: derive each random value from SHA-256(master_seed | generator_version | field_namespace | stable_row_id). Do not use Python global random state, Faker, partition order, or execution order.
- Built-in PySpark only. No %pip, external paths, workspace URLs, or cluster IDs.
- Build in a run-unique staging schema, validate structural and story gates there, then publish. Refuse to overwrite tables that are not marked as generator-owned. Roll back on a failed publish. End with a single unambiguous success message.
- Do not create the catalog. Expect it to exist (it is created manually in Catalog Explorer).
- Tag every table with generator, version, seed, as-of date, scale, run ID, and a synthetic flag. Display an order-independent logical checksum.

Validation requirements:

- Zero primary-key duplicates, zero orphan foreign keys, consistent amounts and dates.
- Every story signal from Phase 1 is present at the expected size.

## Phase 3 — Verify and record

1. If DEV_WORKSPACE_PROFILE is available, run the generator at small scale, then standard scale, then the validation SQL. Otherwise state clearly that nothing was executed.
2. Calculate the core metric and every reference value the sections will reveal, using the exact definition in the facts file.
3. Write the reference values, generator version, seed, scale, as-of date, and total row count into workshop-facts.md, with the section and step where each value may be revealed.

## Rules

- The dataset must not resemble the customer's real physical schema or production data.
- Only add events and relationships the story needs. Every column must be used by at least one section or governance exercise.
- Plain-language descriptions in the data dictionary follow workshop-standards.md section 3.

## Final response

List tables and row counts, story signals with measured sizes, reference values, files created, and what was and was not executed.
````
