# Section 06 — Introduction to Machine Learning in Databricks

**Status:** Draft — runnable lab passed workspace validation; facilitator rehearsal, access grants, and TBD confirmations remain
**Time:** 4:00 PM–5:00 PM (60 minutes)

Participants turn the first-payment-default (FPD5) investigation from Sections 01–05 into an operable model: they train an interpretable FPD5 classifier, track it with MLflow, register it in Unity Catalog, and batch-score the eligible population — then decide how the internal team operates it after the Atlas Ridge Consulting handover.

> **Deployment note:** The canonical design catalog is `hc_workshop`. This workshop instance is retargeted to **`sean_development_catalog`**, where the dataset was published. Every other rule (FPD5 definition, schema layout, naming, leakage control) is unchanged. A facilitator repoints the lab by updating the `WORKSHOP_CATALOG` constant and revalidating.

## Outcomes

By the end of the section, participants can:

1. State which features are legitimate for an origination-time model and which tables are forbidden as target leakage.
2. Split by time (origination vintage) so evaluation mirrors scoring future originations.
3. Track parameters, metrics, and the model with MLflow autologging.
4. Register a model in the Unity Catalog Model Registry with a signature, a `champion` alias, and lineage.
5. Run the required **batch-scoring** path and write governed, team-owned predictions.
6. Read an interpretable model's coefficient reason codes and a calibrated risk distribution.
7. Name what the internal team must own, monitor, promote, and roll back after the handover.

## Workshop flow

- **Slide-led decisions:** leakage vs. legitimate features, time-based vs. random splits, batch scoring vs. real-time serving, when to promote a new champion.
- **Live and hands-on:** build the leakage-safe feature set, train with MLflow, register to UC, batch score, and reconcile predicted risk to the promotion cohort.
- **Focused exercise:** write a model handover note (owner, retrain trigger, drift signal, operating threshold) without claiming confirmed fraud.

This split keeps the section inside 60 minutes. Batch scoring is the required inference path; Model Serving, an online Feature Store, and Lakehouse Monitoring are shown or discussed as optional extensions, not built.

## Prerequisites

- The administrator has completed `../../workshop-setup/README.md` and the standard dataset passed its final generator `SUCCESS` gate.
- The `workshop_labs` and `workshop_shared` schemas exist in the workshop catalog.
- Participants have compute that can run MLflow and scikit-learn: **serverless notebook compute** (the notebook installs the two libraries in its first cell) or a **Databricks ML Runtime** all-purpose resource (libraries preinstalled).

Environment values that must be confirmed before release:

- `WORKSHOP_CATALOG`: **`sean_development_catalog`** for this instance (canonical design value is `hc_workshop`)
- `WORKSHOP_RUNTIME`: **TBD — facilitator confirmation required**
- `FACILITATOR_GROUP`: **TBD — facilitator confirmation required**
- `TEAM_ID`: **TBD — assigned lowercase team ID per team**
- MLflow experiment location: **TBD — defaults to the participant notebook's own experiment**
- Optional Model Serving endpoint: **TBD — only if the serving extension is demonstrated**

## Required permissions

Participants need:

- `USE CATALOG` on the workshop catalog.
- `USE SCHEMA` and `SELECT` on `core_lending`.
- `USE SCHEMA`, `CREATE TABLE`, and `CREATE MODEL` in `workshop_labs`, plus permission to modify their own team- and runner-prefixed model and table.
- Permission to run the imported notebook and use its assigned compute.
- Permission to create MLflow experiment runs.

The facilitator additionally needs `CAN MANAGE` on the workshop catalog's `workshop_labs` schema for cleanup, and (only if the optional serving extension runs) permission to create a Model Serving endpoint.

## Assets

Participant entry point:

- `participant-lab.py` — imported Databricks Python source notebook (installs ML libraries, builds features, trains, registers, batch-scores).
- `exercises.md` — the focused model-handover exercise.
- `expected-results.md` — open after the exercise for observable results and recovery paths.

Facilitator-only delivery file:

- `facilitator-guide.md` — minute-by-minute delivery, UI paths, talking points, and fallbacks.

Each participant's lab creates only, in `workshop_labs`:

```text
unicorn_<team_id>_<runner_id>_fpd            (registered model, alias @champion)
unicorn_<team_id>_<runner_id>_fpd_scores     (Delta table of batch predictions)
```

plus the session-scoped temporary view `unicorn_<team_id>_fpd_features`. It never modifies `core_lending`.

## Definition of done

- The participant notebook reaches its final checkpoint without an unexpected error.
- The eligible FPD5 population is at one-row-per-contract grain and reproduces the cohort rates (promotion higher than other originations).
- A model version is registered in Unity Catalog with a signature, the `champion` alias, and visible lineage to its run and the `core_lending` tables.
- The batch-scores table is written at one row per eligible contract and carries `model_name`/`model_version`.
- Predicted risk is higher for the 0% smartphone promotion cohort than for other originations, reconciling with the analysis sections.
- The participant can explain the leakage rule, why the split is by time, how to promote and roll back a champion by alias, why batch scoring is the required path, and why a high predicted risk is still only an investigation signal.
