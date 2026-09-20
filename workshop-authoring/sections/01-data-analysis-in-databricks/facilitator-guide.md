# Facilitator cue card — Data Analysis in Databricks

**90 minutes · Participant source of truth:** [`participant-lab.py`](../../../workshop-content/01-data-analysis-in-databricks/participant-lab.py)

## Goal

Help participants answer two simple questions:

> Did promotion loans have more late first payments? If yes, which places need a closer look?

The promotion is a point-of-sale installment loan for selected smartphones. Approved customers repay the amount borrowed over 6, 9, or 12 months. Nova Mobile pays Unicorn Finance so the customer pays 0% monthly interest. The phone is not free, and a processing fee or down payment may still apply.

A high FPD5 rate is a reason to investigate. It is not proof of fraud.

## Use plain language

Assume participants are new to both lending and Databricks.

- Use short sentences and one idea at a time.
- Say **loan application**, not **origination context**.
- Say **group of loans**, then introduce a code field such as `promotion_cohort`.
- Say **what one row represents**, not **grain**.
- Say **the total used to calculate the rate**, then introduce **denominator**.
- Say **check that the answers match**, not **reconcile**.
- Explain a business term before a Databricks product term.
- Ask the simple business question before showing code.
- Repeat the same clear words instead of switching to synonyms.

## Before participants enter

- Run [`section-01-facilitator-setup.sql`](../../../workshop-setup/section-01-facilitator-setup.sql); verify 8 source tables and approximately **42.26%** versus **21.03%**.
- Test the notebook with a participant-equivalent identity on the assigned notebook compute.
- Confirm participants can read `core_lending`, read `fpd_analysis` and `fpd_metrics`, create their lab table in `workshop_labs`, and use the SQL warehouse.
- Prepare **Unicorn FPD5 Overview** from `fpd_metrics`: three KPIs, monthly context, promotion-store ranking with at least 10 eligible contracts, cohort/month/region filters, and detail table. Reconcile it, publish with **Individual data permissions**, and grant participants `CAN VIEW`.
- Confirm participants can create an unshared **Unicorn FPD5 Investigator — `<workspace_username>`** in their user folder using only `fpd_metrics`.
- Save one healthy Query Profile and optional queue/spill evidence for fallback.

## Run of show

| Time | Cue | Checkpoint |
|---|---|---|
| 9:45–9:50 | Explain the phone loan, FPD5, and five-day wait | Participants can explain which loans can be checked |
| 9:50–9:57 | Choose compute by workload | Notebook compute versus SQL warehouse is clear |
| 9:57–10:15 | Check where customers applied and when volume increased | Participants understand the promotion before checking payments |
| 10:15–10:27 | Find loans old enough to check and compare FPD5 rates | Counts, percentages, and the five-day rule are correct |
| 10:27–10:39 | Participant groups the loans in a different way | A plain-language summary and follow-up question are recorded |
| 10:39–10:49 | Save the result and view Delta history | Same rows; later version adds `review_note` |
| 10:49–10:56 | Check the Metric View and dashboard | Notebook and dashboard answers match |
| 10:56–11:06 | Create and verify private Genie Agent | Source, SQL, result, date, and sharing verified |
| 11:06–11:11 | Inspect Query History and Query Profile | Queueing and spill distinguished |
| 11:11–11:15 | Complete notebook reflection | One owner, possible problem, and check or fix |

## Keep these messages consistent

- An application tells us that someone asked for a loan. It does not tell us whether they paid.
- A loan can be checked when its first payment reaches day five after the due date. It is FPD5 when still unpaid at that point or paid on or after day five.
- A busy store may have more FPD5 loans because it handles more applications. Always compare percentages as well as counts.
- Do not announce the reference rates before participants run the initial cohort comparison.
- Notebook SQL and PySpark use notebook compute; dashboard and Genie queries use the SQL warehouse.
- `fpd_metrics` stores the shared FPD5 calculation. If it is missing, stop and restore it. Do not create a different formula.
- Delta history shows table changes. Old versions depend on retained files and are not a backup.
- Check the SQL created by Genie before trusting its written answer.

## Fast checks

- **Dashboard:** prepared, participant-visible, matches the notebook, correct filter behavior, Individual data permissions.
- **Agent:** private folder, only `fpd_metrics`, unshared, answer is approximately 42.26% versus 21.03%.
- **Workload:** use participant-owned Query History where possible; do not imply participants administer warehouse-wide activity.
- **Close:** protect the participant grouping exercise, Agent answer, and final reflection. Skip optional UI detail if time slips.

## Fallbacks

- **Metric View missing:** restore with the setup SQL; participants stop.
- **Dashboard unavailable:** reconcile the notebook and Metric View, then use a verified capture.
- **Genie unavailable:** use the facilitator demonstration and inspect its generated SQL; never share or clone the demo Agent. Record affected participants for follow-up—the optional Section 02 extension remains unavailable until they own a private Agent.
- **No queue/spill:** say the live query is healthy and use saved evidence.
- **Lab-table write denied:** verify `USE SCHEMA` and `CREATE TABLE` on `workshop_labs`.
