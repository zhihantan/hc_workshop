# Exercise — Investigate the promotion hotspot

**Timebox:** 7 minutes

## Task

Use the cohort, store-concentration, and store-associate results in `participant-lab.py`.

1. Record the promotion and other-originations FPD5 rates.
2. Record the share of in-store applications produced by the top 20% of stores.
3. Select the highest-ranked promotion store-associate pair with at least 10 eligible contracts.
4. Write a two-sentence handover note using this structure:

> Among contracts whose first installment had reached the five-day observation point by 2026-09-01, the 0% smartphone promotion had an FPD5 rate of ___% versus ___% for other eligible originations. The highest-ranked store-associate pair had ___ FPD5 contracts from ___ eligible contracts (___%); this is a synthetic investigation signal that requires control, customer-mix, campaign, and operational evidence before any fraud conclusion.

5. Add one operational question for Atlas Ridge Consulting. Choose the question that would most reduce uncertainty, such as:
   - Who owns the FPD5 definition and approves changes?
   - What data-quality control verifies first-installment settlement dates?
   - Which dashboard or Genie Agent depends on this logic?
   - What alert or review process follows a material increase?

## Validation

Your answer is complete when it:

- Uses the eligible-contract denominator.
- Treats settlement exactly five days after due date as FPD5.
- Includes both rate and count evidence.
- Does not present the pattern as confirmed fraud.
- Names one concrete ownership, dependency, monitoring, or recovery question.

