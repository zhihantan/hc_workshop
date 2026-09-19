# Expected results — Governance and Access Control

## Live demonstration

### Before the repair

The restricted demo identity can:

- sign in;
- open and run the demonstration notebook;
- use the workshop SQL warehouse;
- discover `hc_workshop`;
- hold `SELECT` on `hc_workshop.core_lending.customer`.

The table query still fails because the identity lacks:

```text
USE SCHEMA ON SCHEMA hc_workshop.core_lending
```

If the query succeeds before the live grant, the demo identity has broader access through ownership, an administrator role, nested group membership, or an inherited grant. Stop and correct the setup instead of continuing.

### After the repair

After the administrator grants only `USE SCHEMA`, the unchanged query returns ten rows containing:

- `customer_id`
- `customer_no`
- `employment_type_code`
- `customer_since_date`

The demonstration does not query the synthetic PII columns.

### Reset

After the facilitator revokes `USE SCHEMA` from the dedicated group, the query fails again. Participant privileges remain unchanged.

## UI evidence

The completed walkthrough should visibly establish:

- notebook and SQL warehouse ACLs are separate from Unity Catalog privileges;
- the runtime principal is the dedicated demo user;
- the catalog, schema, and table privileges form one authorization chain;
- the lineage graph shows upstream and downstream dependencies;
- the Consumer Lending Domain includes both data and workspace assets;
- Domain placement does not grant access to those assets.

## Team checkpoint answers

### Scenario 1 — Discoverable but not queryable

- **Likely layer:** Unity Catalog traversal or action privilege.
- **Inspect first:** active identity and the effective `USE CATALOG`, `USE SCHEMA`, and `SELECT` grants.
- **Premature change:** granting access to the Domain or granting `ALL PRIVILEGES`.

Finding an asset proves discoverability, not query authorization.

### Scenario 2 — Interactive success, scheduled failure

- **Likely layer:** the Job's runtime identity.
- **Inspect first:** the Job's **Run as** principal, then that principal's compute and Unity Catalog access.
- **Premature change:** adding more privileges to the engineer who can already run the query.

The interactive user and the scheduled workload can be different principals.

### Scenario 3 — Same query, different result

- **Likely layer:** row filter, column mask, dynamic view, or credential mode.
- **Inspect first:** whether the query succeeded, active group membership, attached policies, and the data-permission mode of any shared asset.
- **Premature change:** removing the policy or granting broad object ownership.

Different authorized results can be correct policy enforcement rather than an access failure.
