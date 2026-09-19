# Databricks access diagnostic checklist

Use this sequence before requesting broader permissions.

## 1. Record the request

- Who received the error?
- What exact action were they attempting?
- Which workspace asset and fully qualified data object were involved?
- When did it happen?
- What was the exact error and request ID?

Prefer evidence over “it does not work.”

## 2. Identify the executing principal

Check whether the request runs as:

- the interactive user;
- a service principal;
- a Job's configured **Run as** identity;
- a pipeline owner or configured execution identity;
- a dashboard viewer or publishing identity.

For SQL, confirm the interactive identity with:

```sql
SELECT current_user();
```

Do not add privileges to the person reporting the error until you know that person is the executing principal.

## 3. Check the workspace-resource gate

Can the principal:

- sign in and use the required workspace entitlement?
- open or run the notebook, query, Job, pipeline, dashboard, or Genie Agent?
- use or attach to the selected compute?

Typical evidence:

- resource **Permissions** dialog;
- SQL warehouse `CAN USE`;
- classic compute `CAN ATTACH TO`;
- Job or pipeline **Run as** identity.

Passing this gate does not imply access to the underlying data.

## 4. Check the Unity Catalog path

For a table read, verify:

```text
USE CATALOG → USE SCHEMA → SELECT
```

For a write, model, function, or volume action, replace `SELECT` with the privilege required by that action.

Inspect:

- direct grants;
- inherited grants from the catalog or schema;
- object ownership;
- group membership;
- the fully qualified object name.

`BROWSE` allows discovery. It does not grant data access.

## 5. Decide whether access failed or policy succeeded

An authorization error usually means a required gate failed.

A query that succeeds but returns fewer rows or masked values may be governed by:

- a row filter;
- a column mask;
- a dynamic view;
- the dashboard's selected data-permission mode.

Do not remove a policy merely because two users see different results.

## 6. Use the narrowest repair

- Add only the missing resource permission or Unity Catalog privilege.
- Prefer account groups over individual grants.
- Grant at the narrowest practical scope.
- Preserve separation between readers, creators, operators, and access administrators.
- Avoid `ALL PRIVILEGES` as a troubleshooting shortcut.
- Rerun the identical request after the change.
- Record and review the change.

## 7. Know what discovery proves

- **Discover Domains** curate assets by business purpose.
- **Catalog Explorer** exposes technical object details, permissions, and lineage.
- Domain placement does not grant access to an asset.
- Lineage describes dependencies; it does not authorize access.

## Escalation packet

Send the administrator:

- user or runtime principal;
- group memberships relevant to the request;
- workspace asset URL/name;
- compute resource;
- fully qualified data object;
- requested action;
- exact error and request ID;
- timestamp and time zone;
- direct and inherited grants already checked;
- whether the same action succeeds interactively or under another runtime identity.
