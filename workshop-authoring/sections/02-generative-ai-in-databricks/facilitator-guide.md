# Facilitator cue card — Generative AI in Databricks

**60 minutes · Participant source of truth:** [`participant-lab.py`](../../../workshop-content/02-generative-ai-in-databricks/participant-lab.py)

## Goal

Participants use Genie Code to understand, extend, repair, and document inherited FPD5 work while retaining responsibility for review and validation.

> Context → outcome → review → execute → governed reconciliation

## Before participants enter

- Import only `participant-lab.py`; keep `facilitator-demo.py`, expected results, and fallback assets private.
- Test cloning, Serverless notebook compute, Genie Code approval prompts, `@fpd_metrics`, and `@cell` with a participant-equivalent identity.
- Confirm read access to `fpd_metrics` and `fpd_analysis`.
- Verify the baseline, six-region checkpoint, repaired helper, and assertions in [`expected-results.md`](expected-results.md).
- Prepare a reconciled, unpublished **Genie Code Demo — FPD5 Overview** dashboard and a completed notebook fallback.
- Confirm private Section 01 Agents remain editable only if the optional extension may run.

## Run of show

| Time | Cue | Checkpoint |
|---|---|---|
| 11:15–11:20 | Assign the handover; refresh FPD5 and campaign meaning | Population, denominator, date, and caveat stated |
| 11:20–11:27 | Ask Genie Code to explain inherited analysis | Grain and governed measures understood |
| 11:27–11:39 | Participant extends analysis to region | Read-only result uses 20-contract threshold |
| 11:39–11:44 | Reconcile every region | Six rows match; `REGION_VI` is 53.95%, 11.69 points above baseline |
| 11:44–11:54 | Run and repair the PySpark helper | 100% bug diagnosed; live checks pass |
| 11:54–11:59 | Review `/optimize` and `/doc` | Only justified, result-preserving changes accepted |
| 11:59–12:08 | Build the facilitator dashboard draft | Participant observation checklist completed |
| 12:08–12:12 | Optional Agent extension or buffer | Run only if participants are already ready |
| 12:12–12:15 | Complete notebook reflection | Owner, risk, recovery, and next use recorded |

## Keep these messages consistent

- Participants work in personal clones of `participant-lab.py`, never in the facilitator notebook.
- Genie Code output is a draft. Source, grain, denominator, thresholds, permissions, and results still require human validation.
- Regional analysis uses **20 eligible contracts**; dashboard and Agent rankings use **10**. Neither threshold defines FPD5 or statistical significance.
- Let participants see both cohorts at 100% before naming the bug. The repair keeps the full eligible population and uses `fpd5_flag` only as numerator.
- Assertions require two cohorts, positive eligible counts, FPD5 counts not exceeding eligible counts, and live Metric View agreement within 0.05 percentage points.
- Notebook work uses notebook compute. Dashboard and Agent work use a SQL warehouse.
- Elevated FPD5 is an investigation signal, not proof of fraud, causality, or a regional effect.

## Dashboard watch list

Participants should confirm:

- only `fpd_metrics` is used;
- cohort values reconcile;
- store ranking shows eligible and FPD5 counts plus rate;
- the 10-contract minimum is retained;
- the promotion filter affects the cohort comparison and store ranking but leaves all-cohort KPI counters unchanged;
- the draft remains unpublished.

## Optional Agent

- Use only the participant's private Section 01 Agent.
- Skip if the owner cannot edit it or the core checkpoints are incomplete.
- Test the target store-associate question in a fresh conversation.
- After the smallest context change, test the target again in a new conversation and run the original cohort comparison in another fresh conversation.
- Keep `fpd_metrics` as the only source and keep the Agent unshared.

## Fallbacks

- **Genie Code unavailable:** review the completed facilitator clone and validate the same invariants.
- **Metric View unavailable:** verify privileges, then stop; never rebuild FPD5 from raw tables.
- **Regional mismatch:** check source, promotion filter, grain, measures, `HAVING`, denominator, and percentage conversion.
- **Dashboard stalls:** use the completed unpublished draft.
- **Agent unavailable:** skip the optional extension; do not provide a shared Agent.

After the section, delete the disposable facilitator dashboard and personal demo artifacts.
