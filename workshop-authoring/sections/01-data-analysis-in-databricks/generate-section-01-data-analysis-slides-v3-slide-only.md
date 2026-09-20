# Final slide-only generation prompt — Data Analysis in Databricks

Create the visible presentation slides for the opening **12 minutes** of the 90-minute Data Analysis in Databricks workshop.

This prompt intentionally covers only the portions marked **Slides** in the facilitator delivery map. The remaining 78 minutes are delivered in the notebook, participant workspace, or live demonstrations.

## Source authority

Resolve conflicts in this order:

1. `facilitator-guide.md`
2. `../../../workshop-content/01-data-analysis-in-databricks/01-lab.py`
3. `drafts/generate-section-01-data-analysis-slides-v2-content-first.md`
4. `README.md`
5. `../../../participant-materials/unicorn-finance-workshop-scenario.md`
6. `../../agenda/workshop-agenda.md`

## Delivery contract

Generate the smallest useful deck for these two slide windows:

| Time | Duration | Visible slide purpose |
|---|---:|---|
| 9:45–9:50 | 5 minutes | Business question, promotion, FPD5, eligibility, and investigation boundary |
| 9:50–9:57 | 7 minutes | Notebook compute, Jobs compute, and SQL warehouse distinctions |

At 9:57, the presentation must transition to `01-lab.py`. Do not create later slides for the notebook exercises, Delta workflow, Metric View, dashboard, Genie Agent, Query History, Query Profile, or closing reflection.

Aim for approximately **3–5 concise slides**. Choose the exact count and titles yourself.

## Audience and role

- The real audience is Home Credit Philippines.
- Participants act as Unicorn Finance's internal data team taking ownership of an inherited Databricks platform.
- The audience may include analysts, developers, engineers, and technical owners.
- Unicorn Finance, Atlas Ridge Consulting, Nova Mobile, and all workshop records are fictional or synthetic.

## Visible-slide content

### Business assignment

Participants need to answer:

> Does Nova Mobile's 0%-interest smartphone financing campaign show elevated FPD5, and where should the business investigate?

The slide content must establish:

- Nova Mobile subsidizes selected smartphone financing;
- approved customers repay principal over 6, 9, or 12 months at 0% monthly interest;
- a processing fee or down payment may still apply;
- application and contract volume increased during the campaign;
- apparent FPD5 concentration is an investigation signal, not proof of fraud, misconduct, or causality.

### FPD5 and eligibility

Explain the minimum definition participants need before opening the notebook:

- only the first installment is considered;
- the installment must reach day five past due by the as-of date `2026-09-01`;
- an unsettled installment, or settlement on or after day five, counts as FPD5;
- settlement before day five does not count;
- the denominator is eligible contracts, not applications, approvals, or only defaulted contracts.

Make the distinction between **count** and **rate** visible. A high count may reflect volume; a high rate still requires a meaningful denominator and further investigation.

Do not show the seeded reference rates on these opening slides.

### Compute by workload

Show a compact workload-to-compute mental model:

- interactive Python, PySpark, `spark.sql(...)`, and `%sql` in this lab run on the notebook's attached Serverless compute;
- `%sql` changes the notebook cell language but does not move execution to a SQL warehouse;
- Databricks supplies the `spark` session;
- scheduled Python or notebook work belongs on Jobs compute;
- AI/BI Dashboards and Genie Agent analytical queries run on a SQL warehouse;
- SQL Query History contains warehouse statements, not this lab's notebook `%sql` cells.

Focus on the execution distinction rather than infrastructure administration or a complete compute-product taxonomy.

## Recommended visual ideas

Use simple visuals such as:

- a partner-to-internal-team handover with the unresolved business question;
- a first-installment timeline showing eligibility and day-five classification;
- a count-versus-rate comparison;
- a three-column workload map for notebook, Jobs, and SQL warehouse compute.

Do not fabricate product screenshots or workspace evidence.

## Presenter notes

Presenter notes may include:

- brief definitions;
- the exact FPD5 edge cases;
- the non-causality reminder;
- the explanation that Databricks already provides the Spark session;
- the transition into the participant notebook.

End with a direct transition:

> We have the business question, the population rule, and the compute model. Now we will test the inherited data in the notebook.

## Excluded from visible slides

Do not create slides for:

- source-table verification or application queries;
- cohort results or seeded percentages;
- the participant grouping exercise;
- Delta table creation, history, or time travel;
- Metric View or dashboard reconciliation;
- private Genie Agent creation;
- Query History or Query Profile;
- final ownership reflection.

Those topics belong to the live delivery and may appear only as brief transition notes when necessary.

## Output request

Return:

1. the proposed slide count and narrative;
2. concise visible slide content;
3. presenter notes for each slide;
4. recommended visuals;
5. exact timing across the 12-minute slide window;
6. the final transition into `01-lab.py`;
7. a coverage check confirming that no excluded live-workspace topic became a visible slide.

Use a clean 16:9 workshop style. Keep slides readable, business-led, and technically accurate.
