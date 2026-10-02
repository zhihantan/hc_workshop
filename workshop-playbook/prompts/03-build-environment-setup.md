# Prompt 03 — Build the environment setup and admin instructions

**Use when:** the dataset generator works. Rerun whenever a section adds a shared asset or permission.
**Produces:** schema setup notebook, shared-asset setup SQL, optional setup Jobs, and a short admin instruction document (Markdown and PDF) you can send to the customer's workspace administrator.
**Next:** `04-plan-section.md`.

On the first run, before any section is planned, build the base setup: schemas, dataset, and read access to the source. Rerun after each section plan or notebook adds a shared asset, grant, or required feature.

## Prompt

````text
Build the workshop environment setup and the administrator instructions.

Read first:
1. workshop-playbook/workshop-standards.md
2. workshop-authoring/workshop-facts.md
3. workshop-setup/dataset-generator/README.md
4. Every section plan under workshop-authoring/sections/ (the "Reuses / depends on" line lists shared assets, grants, and features), and any workshop-setup/section-<NN>-facilitator-setup.sql

## Inputs

REPOSITORY_ROOT: [absolute path]
ADMIN_AUDIENCE: [who runs setup, for example the customer's workspace admin]
FACILITATOR_HAS_PARTICIPANT_WORKSPACE_ACCESS: [yes | no — from the facts file]
DEV_WORKSPACE_PROFILE: [profile for testing, or NONE]

## Task

1. Create workshop-setup/setup_workshop_schemas.py: creates <SOURCE_SCHEMA>, <SHARED_SCHEMA>, and <LABS_SCHEMA> in an existing <CATALOG> and reports READY for each. It must not create the catalog.
2. Create one setup SQL file per section that needs shared assets (for example the shared analysis view and Metric View), named workshop-setup/section-<NN>-facilitator-setup.sql. Make each idempotent.
3. If several setup steps must run in order, add a Job definition (JSON) and a single setup notebook that runs them, so the admin presses one button.
4. Write the minimum Unity Catalog grants per section for <PARTICIPANT_GROUP>. Never grant catalog-wide ALL PRIVILEGES or MANAGE to participants. Explain in one line what each grant allows.
5. List workspace prerequisites: entitlements (for example Databricks SQL access), CAN USE on warehouses, serverless notebook compute, AI features at account and workspace level, private user folders left at default permissions.
6. Write workshop-setup/WORKSHOP_ADMIN_INSTRUCTIONS.md as numbered steps an administrator who has never seen the repository can follow:
   1. Upload or clone the setup folder.
   2. Create the catalog manually in Catalog Explorer (state the storage choice from the facts file).
   3. Run schema setup and confirm READY.
   4. Run the generator and stop unless it reports success.
   5. Run validation.
   6. Run shared-asset setup.
   7. Apply grants.
   8. Confirm workspace prerequisites.
   9. Report back the values the facilitator needs (warehouse name, group names, dashboard URL).
   Keep it short. Remove anything that is optional or facilitator-only.
7. Render the admin instructions to PDF.
8. Create workshop-setup/README.md listing every setup file, the order to run them, and a per-section table of the participant and facilitator permissions each section needs.

## Rules

- Setup is never part of the participant flow. If the facilitator cannot access the participant workspace, every shared asset must be creatable by the admin from these files alone.
- Do not hard-code storage locations, workspace URLs, cluster IDs, or tokens.
- Every setup file is safe to rerun and states what rerunning does.
- Keep all setup in workshop-setup/. Do not split facilitator setup into another folder.

## Validation

If DEV_WORKSPACE_PROFILE is available, run the full sequence from an empty catalog with an identity that has only the documented admin privileges, then confirm participant-equivalent access with an identity that has only the documented participant grants. Record what was run. Otherwise say clearly that nothing was executed.

## Final response

List setup files and run order, grants per section, workspace prerequisites, values the admin must report back, and what was executed.
````
