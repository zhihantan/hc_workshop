# Exercise — Hand over the FPD5 model

**Timebox:** 8 minutes

## Task

Use the training metrics, the coefficient risk drivers, and the batch-score cohort table in `participant-lab.py`.

1. Record the validation ROC-AUC and PR-AUC, and the base FPD5 rate on the validation vintage.
2. Record the average **predicted** risk versus the **actual** FPD5 rate for the 0% smartphone promotion cohort and for other originations.
3. Name the two features that most raise predicted FPD5 risk, from the coefficient table.
4. Write a three-sentence model-handover note using this structure:

> The FPD5 model is an interpretable logistic-regression scorer trained only on origination-time features, split by `origination_date`, reaching ROC-AUC ___ on the most recent vintage. At the review threshold it flags ___ eligible contracts (___% of the book), with predicted risk of ___% for the 0% smartphone promotion versus ___% for other originations. Because it is trained only on application-time inputs, a high score is a synthetic investigation signal for origination review, not a confirmed-fraud label.

5. Add one operational question the internal team must answer to own this model, such as:
   - Who approves promoting a new `champion`, and what is the rollback step?
   - What retraining cadence or trigger keeps it current as new vintages mature?
   - Which drift or performance signal is monitored, and where?
   - Which downstream process consumes the batch-scores table?

## Validation

Your answer is complete when it:

- Uses only origination-time features and names at least one forbidden leakage source (installments, payments, collections, contract status, or settlement).
- Reports both a ranking metric (ROC-AUC or PR-AUC) and the calibrated cohort comparison.
- States the review threshold and the flagged share.
- Does not present the pattern or a high score as confirmed fraud.
- Names one concrete ownership, retraining, monitoring, or consumption question for the handover.
