# Exercise — Apply the Genie Code productivity loop

**Core timebox:** 30 minutes  
**Optional Genie Agent extension:** 10 minutes

Work in your personal clone of `participant-lab.py`.

## 1. Understand

Attach the inherited cohort query and its output with `@cell`. Ask Genie Code to explain its grain, measures, denominator, grouping, and percentage conversion without editing code.

Check the explanation against the query and record one useful point and one point you verified yourself.

## 2. Generate and iterate

Use the regional-extension prompt in the notebook. Review the plan, allow the required notebook actions, and give a targeted correction if one detail is wrong.

The completed result must contain:

- one row per promotion region;
- eligible contracts, FPD5 contracts, and FPD5 rate;
- only regions with at least 20 eligible contracts;
- a sorted, readable chart;
- a comparison with the overall promotion rate.

## 3. Diagnose and repair inherited PySpark

Run the inherited PySpark validation helper. Its output is suspicious: both cohorts report a 100% FPD5 rate because the function removes non-FPD5 contracts before calculating the denominator.

Attach the function and output with `@cell`. Ask Genie Code to:

- explain the semantic bug;
- preserve the full eligible population;
- count `fpd5_flag` only in the numerator;
- keep the function read-only and DataFrame-based;
- add lightweight assertions for the result shape, count relationship, and reference rates.

Review the proposed diff before accepting it. Rerun the function and its checks.

## 4. Improve and document

Use `/optimize` on the generated regional query. Do not force or accept a change without a material reason. If you accept a change, rerun the query and confirm that its results are unchanged.

Use `/doc` to add a concise explanation of the query's grain, denominator, and threshold.

## Optional extension — Improve your private Genie Agent

Open **Unicorn FPD5 Investigator — `<your_workspace_username>`**, the private Agent you created in Section 01.

In your Agent:

1. Run the baseline store-associate question from the notebook.
2. Open Genie Code from the response.
3. Supply the new risk-team response requirements.
4. Review and accept only the smallest relevant context changes.
5. Start a fresh conversation and rerun the target question.
6. Rerun the cohort-comparison question as a regression check.

Keep the Agent private. Do not share it with another participant or duplicate the governed FPD5 formula in Agent instructions.

## Validation

Your core workflow is complete when:

- generated SQL uses only `hc_workshop.workshop_shared.fpd_metrics`, and the PySpark validation helper reads only `hc_workshop.workshop_shared.fpd_analysis`;
- generated SQL uses governed `MEASURE(...)` expressions;
- the regional result reconciles to the expected values;
- the PySpark helper no longer filters out non-FPD5 contracts before aggregation;
- the repaired helper reports approximately 42.26% and 21.03% and passes its lightweight assertions;
- accepted improvements preserve the result;
- there are no data write operations or unsupported causal claims;
- you can name one step Genie Code made faster and one check that remained your responsibility.

If you complete the optional extension:

- the participant's private Agent meets the new response requirements;
- the cohort regression still returns approximately 42.26% versus 21.03%;
- the Agent remains in the participant's user folder and unshared.
