# Slide-generation brief — Governance and Access Control in Databricks

Create a 16:9 deck for a 30-minute facilitator-led workshop section. Use the topic title and scheduled time, not the internal `05` repository identifier.

## Authoritative design

This is one access-incident story, not a security-feature tour.

> A Unicorn Finance risk analyst can find `hc_workshop.workshop_shared.fpd_analysis` under Consumer Lending > Origination Risk, but cannot query it after the partner handover.

Participants act as the new platform owners. They diagnose the request, record evidence, identify the narrowest repair, verify the unchanged query, assess downstream impact, and complete an incident handover.

The facilitator runs `facilitator-demo.py` as a dedicated restricted identity. Participants use only `../../../workshop-content/05-governance-and-access-control/participant-guide.md`; they do not run code or change permissions.

All data and identities are fictional or synthetic.

## Design rules

Create four concise core slides. For each slide:

- use one message, one simple diagram, or at most five short bullets;
- define unfamiliar terms before using them;
- state the operational question the slide answers;
- include detailed presenter notes and the transition to the next action;
- label the slide `Essential` or `Optional`;
- label the strategy `Create new`, `Curate existing collateral`, or `Hybrid`.

Use clean Databricks-style enterprise visuals with restrained orange or red accents. Prefer diagrams to prose. Do not include code listings, complete privilege inventories, decorative stock imagery, or unverified product screenshots.

The slides establish the assignment and mental model. The notebook, Catalog Explorer, lineage graph, and Discover page provide the evidence.

## Technical boundaries

- A view read requires `USE CATALOG`, `USE SCHEMA`, and `SELECT`.
- `BROWSE` supports discovery without data access.
- Notebook `CAN RUN`, SQL warehouse `CAN USE`, runtime identity, and Unity Catalog privileges are separate gates.
- Direct and inherited grants both matter.
- Row filters, column masks, and ABAC can change an authorized result; they are not configured live.
- Lineage supports impact analysis; it does not authorize access or prove correctness.
- Discover Domains are Public Preview, business-aligned groupings implemented with governed tags.
- Domain placement does not grant access to an asset.
- If dashboard behavior is mentioned, use **Share data permissions** and **Individual data permissions**.
- The ten-row query is an access smoke test, not a validation of the FPD5 population or denominator.

Do not add Data Classification, storage credentials, external locations, Delta Sharing, live policy creation, Domain creation, or separate Job and dashboard demonstrations.

## Timed instructional arc

- 0:00–0:03 — participant assignment and handover deliverable
- 0:03–0:07 — minimum authorization model and evidence packet
- 0:07–0:16 — restricted-identity failure, permission inspection, narrow repair, unchanged rerun
- 0:16–0:20 — interpret what the result proves and does not prove
- 0:20–0:24 — lineage for the same `fpd_analysis` asset
- 0:24–0:27 — return to Consumer Lending > Origination Risk
- 0:27–0:30 — participant incident handover and reflection

## Slide 1 — Restore access without overgranting

**Priority:** Essential
**Strategy:** Create new

### Visible content

Role:

> You own the inherited Unicorn Finance platform.

Incident:

> A risk analyst can find the trusted FPD5 analysis, but cannot query it.

Deliverable:

> Principal → failed gate → evidence → narrow repair → verification → downstream impact → owner and recovery

### Recommended visual

An incident card connected to **Consumer Lending > Origination Risk > fpd_analysis**. Mark the asset as “discoverable” and the query as “blocked,” without revealing the missing privilege.

### Presenter notes

State that participants will complete one incident handover in their guide. The data is synthetic. The FPD5 definition was established earlier and is not recalculated here.

### Transition

“Finding the asset proves discovery. We now need to determine which independent gate blocks the read.”

---

## Slide 2 — Why finding an asset does not mean you can query it

**Priority:** Essential
**Strategy:** Hybrid

### Visible content

```text
Notebook CAN RUN
        ↓
SQL warehouse CAN USE
        ↓
Runtime principal
        ↓
USE CATALOG → USE SCHEMA → SELECT
        ↓
Authorized result
```

Definitions:

- principal = user, service principal, or group that can hold permissions;
- runtime identity = user or service principal for the session or workload;
- inherited grant = permission received from a parent securable;
- group-derived access = effective access supplied through group membership;
- `BROWSE` = discover metadata, not read rows.

### Recommended visual

A five-gate vertical path with the current evidence unknown at each stage. Curate generic Databricks iconography only if it matches the exact sequence.

### Presenter notes

Ask which gates are proven when a user can open the notebook and find the view in Discover. Do not reveal the missing `USE SCHEMA`.

### Transition

“Before changing access, collect evidence that identifies the first failed gate.”

---

## Slide 3 — Collect evidence before changing access

**Priority:** Essential
**Strategy:** Create new

### Visible content

Capture:

- runtime principal;
- workspace asset, data object, action, and compute;
- exact error and request ID;
- direct grants, parent-securable inheritance, and group-derived access;
- timestamp and time zone.

Rule:

> Preserve the request. Change one authorization variable at a time.

### Recommended visual

An evidence packet beside the request path. Highlight “first failed gate” and “narrowest approved repair.”

### Presenter notes

Open `facilitator-demo.py`:

1. show `current_user()`;
2. run the `fpd_analysis` query;
3. stop at the error;
4. inspect the `workshop_shared` permissions;
5. ask participants to identify the missing privilege;
6. grant only `USE SCHEMA`;
7. rerun the unchanged query.

Explain that an unchanged rerun is stronger evidence than altering the SQL, identity, or compute.

### Live transition

Move to the restricted notebook and administrator permission view.

---

## Slide 4 — Prove the repair and assess the impact

**Priority:** Essential
**Strategy:** Create new

### Visible content

```text
Unchanged request succeeds
        ↓
Lineage identifies downstream retesting
        ↓
Domain supports business discovery
        ↓
Incident handover records owner, risk, and recovery
```

Boundaries:

- ten rows prove access, not data completeness;
- lineage shows dependencies, not authorization;
- Domain placement shows curation, not permission.

### Recommended visual

A compact path from `fpd_analysis` to `fpd_metrics` to the verified FPD5 dashboard, beside **Consumer Lending > Origination Risk**.

### Presenter notes

Open lineage for the same `fpd_analysis` view and show one column-level path. Then return to its Domain page. Explain that Domains use governed tags and that underlying Unity Catalog or workspace permissions still apply.

Give participants three minutes to complete the handover in their guide.

Close with:

> Identify the principal, locate the first failed gate, preserve the request, and apply the narrowest approved repair.

## Optional transfer note

If time remains, mention without another UI demonstration:

- a scheduled Job can fail under a different **Run as** identity even when the interactive notebook succeeds;
- an authorized query can return different rows or masked values because of policies;
- a dashboard can use **Share data permissions** or **Individual data permissions**.

## Verify before final slide export

1. Exact insufficient-privilege error in the target workspace.
2. Restricted identity's notebook `CAN RUN` and warehouse `CAN USE`.
3. Direct and inherited permission display for `workshop_shared`.
4. Successful `fpd_analysis` query after only `USE SCHEMA` is granted.
5. Table- and column-level lineage from `fpd_analysis` to verified consumers.
6. Discover preview availability and current labels.
7. `MANAGE DISCOVERY` and governed-tag behavior.
8. Current dashboard data-permission terminology.
9. Final warehouse, user, group, and Domain values.

Use conceptual diagrams rather than screenshots until the target workspace has been rehearsed.

## Final output request

Return:

1. final slide order;
2. concise visible copy;
3. recommended visual;
4. detailed speaker notes;
5. live-demo transition;
6. Essential/Optional label;
7. Create/Curate/Hybrid label;
8. required screenshots or supplied collateral;
9. final claim-verification checklist.

Do not expand the scope to fill slides. Identify unsupported workspace evidence rather than fabricating it.
