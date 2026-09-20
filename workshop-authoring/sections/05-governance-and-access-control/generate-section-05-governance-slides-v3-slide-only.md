# Final slide-only generation prompt — Governance and Access Control

Create the visible presentation slides for the two slide windows in the 30-minute facilitator-led Governance and Access Control workshop.

This prompt intentionally covers only the portions marked **Slides** or **Slides and discussion** in the facilitator delivery map. The controlled access failure, administrator repair, lineage, Discover walkthrough, and participant handover are delivered outside the deck.

## Source authority

Resolve conflicts in this order:

1. `facilitator-guide.md`
2. `../../../workshop-content/05-governance-and-access-control/05-participant-guide.md`
3. `facilitator-demo.py`
4. `../../../workshop-setup/section-05-governance-demo-setup.sql`
5. `generate-section-05-governance-slides-v2-content-first.md`
6. `README.md`
7. `../../../participant-materials/unicorn-finance-workshop-scenario.md`
8. `../../agenda/workshop-agenda.md`

## Delivery contract

Generate the smallest useful deck for these two slide windows:

| Time | Duration | Visible slide purpose |
|---|---:|---|
| 0:00–0:03 | 3 minutes | Access incident, assignment, and smoke-test boundary |
| 0:03–0:07 | 4 minutes | Authorization chain and evidence to collect |
| 0:16–0:20 | 4 minutes | What the successful repair proves and does not prove |

The deck pauses from 0:07–0:16 while the facilitator runs the restricted-user failure and administrator repair. It closes again at 0:20 for the lineage, Discover, and participant-handover activities.

Aim for approximately **3–5 concise slides** across the two windows. Choose the exact count and titles yourself.

## Audience and incident

- The real audience is Home Credit Philippines.
- Participants act as Unicorn Finance's internal team operating an inherited Databricks platform.
- A risk analyst can discover `hc_workshop.workshop_shared.fpd_analysis` under **Consumer Lending > Origination Risk**, but cannot query it.
- Participants diagnose the request while the facilitator operates the restricted identity and separate administrator session.
- All identities and data are fictional or synthetic.

## Opening slide window: 0:00–0:07

### Incident and assignment

The opening must establish:

- the asset is discoverable but not queryable;
- the goal is to identify the executing identity and first failed authorization gate;
- the repair must be the narrowest approved change;
- the same request must be rerun unchanged to verify the diagnosis.

The ten-row query is an access smoke test. It does not recalculate or validate FPD5.

### Authorization chain

Show this request path:

```text
Notebook CAN RUN
→ SQL warehouse CAN USE
→ runtime identity
→ USE CATALOG
→ USE SCHEMA
→ SELECT
→ authorized result
```

Explain:

- workspace permissions and Unity Catalog privileges are separate;
- a user or service principal executes the request;
- groups contribute effective access through membership;
- `BROWSE` supports discovery but does not grant row access;
- passing one gate does not prove the next gate will pass.

### Evidence to collect

Before changing access, collect:

- runtime identity;
- workspace asset and compute resource;
- fully qualified object and requested action;
- exact error and request ID;
- direct grants, parent-securable inheritance, and group-derived access;
- timestamp and time zone.

End the opening window by asking participants to predict whether the query will succeed.

Then close the deck and transition to `facilitator-demo.py`.

## Post-repair slide window: 0:16–0:20

Return to the deck only after:

- the restricted query failed because `USE SCHEMA` was missing;
- the administrator granted only `USE SCHEMA` on `hc_workshop.workshop_shared`;
- the restricted user reran the unchanged query successfully.

### What the result proves

The unchanged rerun supports the conclusion that this request now passes:

- notebook access;
- SQL warehouse access;
- the observed runtime identity;
- catalog traversal;
- schema traversal;
- view `SELECT`.

### What the result does not prove

Ten returned rows do not prove:

- that the full FPD5 dataset or business definition is correct;
- that every row is visible;
- that no row filter, column mask, dynamic view, or other policy applies;
- that unrelated objects or execution identities have access;
- that a broader grant was required.

Reinforce:

> Preserve the failing request, change one authorization variable, and verify the unchanged request.

At 0:20, close the deck and transition to Catalog Explorer lineage.

## Recommended visual ideas

Use simple visuals such as:

- a discoverable-but-blocked asset;
- a gated authorization path;
- an evidence packet;
- before/after states showing only `USE SCHEMA` changing;
- a two-column “proves / does not prove” debrief.

Do not fabricate workspace screenshots, permission evidence, errors, identities, lineage, or Domain pages.

## Excluded from visible slides

Do not create slides for:

- the live `current_user()` output;
- the intentional error text;
- administrator permission inspection;
- the actual `GRANT` statement execution;
- the unchanged successful query output;
- table- or column-level lineage;
- Discover Domains;
- the final participant incident handover.

Those belong to the live workspace or participant guide. Presenter notes may provide transition cues only.

## Output request

Return:

1. the proposed slide count and narrative;
2. concise visible slide content;
3. presenter notes for each slide;
4. recommended visuals;
5. exact timing across both slide windows;
6. explicit transitions into the restricted demo, back to the post-repair debrief, and onward to lineage;
7. a coverage check confirming that no excluded live-workspace topic became a visible slide.

Use a clean 16:9 workshop style. Keep the deck focused on the diagnostic mental model and the meaning of the evidence.
