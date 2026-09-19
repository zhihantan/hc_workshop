# Exercises — Extend the investigation and create a Genie Agent

**Total timebox:** 22 minutes

## 1. Change the analytical grain

**Timebox:** 12 minutes

Use the cohort results and the **Try it: change the analytical grain** cell in `participant-lab.py`.

1. Record the promotion and other-originations FPD5 rates.
2. Change `ANALYSIS_DIMENSION` from `region_code` to either `store_province` or `merchant_name`.
3. Rerun the cell and record:
   - the dimension you selected;
   - the highest-rate segment;
   - its eligible-contract count, FPD5 count, and FPD5 rate.
4. Compare the result with the store-associate ranking. Explain whether the new grain reveals a broad concentration or a more localized hotspot.
5. Write a two-sentence handover note using this structure:

> Among contracts whose first installment had reached the five-day observation point by 2026-09-01, the 0% smartphone promotion had an FPD5 rate of ___% versus ___% for other eligible originations. When analyzed by `<dimension>`, `<segment>` had ___ FPD5 contracts from ___ eligible contracts (___%); this is a synthetic investigation signal that requires control, customer-mix, campaign, and operational evidence before any fraud conclusion.

6. Add one operational question for Atlas Ridge Consulting. Choose the question that would most reduce uncertainty, such as:
   - Who owns the FPD5 definition and approves changes?
   - What data-quality control verifies first-installment settlement dates?
   - Which dashboard or Genie Agent depends on this logic?
   - What alert or review process follows a material increase?

### Validation

Your answer is complete when it:

- reflects a dimension change you made in the notebook;
- Uses the eligible-contract denominator.
- Treats settlement exactly five days after due date as FPD5.
- Includes both rate and count evidence.
- Does not present the pattern as confirmed fraud.
- Names one concrete ownership, dependency, monitoring, or recovery question.

## 2. Create your private Genie Agent

**Timebox:** 10 minutes

Follow the facilitator in your workshop workspace:

1. Open **Genie Agents** from the sidebar and select **New**.
2. Add only `hc_workshop.workshop_shared.fpd_metrics` as the data source, then create the Agent. Do not add `fpd_analysis` or any raw `core_lending` tables.
3. Name it **Unicorn FPD5 Investigator — `<your_workspace_username>`**.
4. Select the workshop SQL warehouse.
5. Set the description to:

   > Answers governed questions about eligible fixed-term contracts and FPD5 for the synthetic Unicorn Finance workshop. It compares promotion, product, channel, store, region, and sales-associate cohorts through the `fpd_metrics` Metric View and must describe hotspots as investigation signals rather than confirmed fraud.

6. Do not tune the Agent context yet. Section 02 will use Genie Code to improve this same Agent after its baseline is recorded.
7. Add these common questions:
   - How does FPD5 for the 0% smartphone promotion compare with other eligible originations?
   - Which promotion stores have the highest FPD5 rate, with at least 10 eligible contracts?
   - Which promotion store-associate pairs have the highest FPD5 rate, with at least 10 eligible contracts?
8. In the Workspace browser, confirm that the Agent is in your user folder. Then open **Share** and confirm it is not shared with **All account users**, the workshop participant group, or another participant. Inherited workspace-administrator access can remain.
9. Ask:

   > As of 2026-09-01, how does FPD5 for the 0% smartphone promotion compare with other eligible originations?

10. Inspect the generated SQL before accepting the prose answer as correct.
11. Save the baseline response and generated SQL for Section 02.

### Validation

Your Agent is ready for Section 02 when:

- it is in your own user folder and is not shared with other participants;
- `fpd_metrics` is its only data source;
- it uses the workshop SQL warehouse;
- generated SQL queries `hc_workshop.workshop_shared.fpd_metrics` and invokes governed measures with `MEASURE(...)`;
- the answer reconciles to approximately **42.26%** for the promotion and **21.03%** for other eligible originations;
- the answer states the observation date and does not claim that the hotspot proves fraud.

