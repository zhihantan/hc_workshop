# Team checkpoint — Locate the failed layer

For each scenario, name:

1. the likely authorization layer;
2. the first evidence to inspect;
3. one change that would be premature.

## Scenario 1 — Discoverable but not queryable

An analyst finds `hc_workshop.core_lending.customer` in the **Consumer Lending** Domain. The table page opens, but a SQL query fails with an insufficient-privilege error.

## Scenario 2 — Interactive success, scheduled failure

An engineer can run a notebook interactively and read `hc_workshop.core_lending.loan_application`. The scheduled Job that runs the same notebook fails with `PERMISSION_DENIED`.

## Scenario 3 — Same query, different result

Two analysts can run the same table query. One analyst sees all provinces and unmasked values; the other sees only an assigned province and masked values. Neither receives an error.

Use `access-diagnostic-checklist.md` before proposing a repair.
