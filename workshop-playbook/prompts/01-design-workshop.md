# Prompt 01 — Design the workshop

**Use when:** starting a new workshop from a customer brief.
**Produces:** the facts file, agenda, canonical story, participant opening scenario, and repository skeleton.
**Next:** `02-build-dataset.md`.

Run this in plan or review mode first. Approve the story and section plan before any files are written.

## Prompt

````text
Design a full-day Databricks enablement workshop for a customer.

Read first:
1. workshop-playbook/workshop-standards.md
2. workshop-playbook/workshop-facts-template.md
3. workshop-playbook/examples/home-credit-unicorn-finance-facts.md (a completed example; do not copy its story)

## Inputs

CUSTOMER: [real audience organization]
INDUSTRY_AND_BUSINESS_MODEL: [how the customer makes money; main products]
WORKSHOP_DATE_AND_FORMAT: [date, duration, in person or remote]
PARTICIPANT_BACKGROUND: [roles, current platform (for example Cloudera, Snowflake), SQL/Python level]
LANGUAGE_NOTES: [for example, English is a second language]
REQUESTED_TOPICS: [topics the customer asked for, in their words]
REQUIRED_DATABRICKS_TOPICS: [for example analysis, Genie and Genie Code, data engineering, governance, ML]
TIME_BUDGET: [start and end time, breaks, fixed slots]
FACILITATOR_HAS_PARTICIPANT_WORKSPACE_ACCESS: [yes | no]
CONSTRAINTS: [anything the content must avoid, such as real product names or regulators]

## Task

1. Propose one fictional company that mirrors the customer's business without copying its real products, systems, or names. Include a fictional partner that is handing the platform over, so participants play the internal team taking ownership.
2. Propose one business event that can carry the whole day. It must:
   - be explainable in five plain numbered steps;
   - produce a visible pattern in data that is a reason to investigate, not proof;
   - need one core metric with a precise population, eligibility rule, numerator, and denominator;
   - be investigable with analysis, AI assistance, pipelines, governance, and ML in turn.
   List the misreadings participants are likely to make and how to prevent each one.
3. Define the core metric with every edge case.
4. Propose the workshop-level section list. For each section give number, name, time, minutes, delivery mode (NOTEBOOK_LED or FACILITATOR_LED), assignment, final deliverable, required and optional topics, and what it reuses from earlier sections. Keep this high level; the detailed plan of what to present and what to go through in the notebook comes later, per section, from prompt 04. Each section must deliver something for the fictional company; do not plan feature tours. Keep section numbers aligned with the agenda.
5. Flag topics that do not fit the time or story, and recommend whether to cut, shorten, demo, or make optional.
6. Draft a plain-language glossary of every domain and Databricks term participants will meet.

Stop and present 1–6 for approval. Do not write files yet.

After approval:

7. Create workshop-authoring/workshop-facts.md from the template. Mark every unknown value TBD.
8. Create workshop-authoring/story/<company>-story.md: company, partner handover, business event, inherited platform, dataset overview, investigation across the day, fiction boundary.
9. Create workshop-authoring/agenda/workshop-agenda.md: time slots, three to seven topic bullets per section, pre-requisites, pre-reading links. Bullets describe what participants do for the company, not product names alone.
10. Create participant-materials/<company>-workshop-scenario.md: a one-page opening story for participants, with the section-to-deliverable map.
11. Create the repository skeleton from workshop-standards.md section 4 with README files that say what belongs where.

## Rules

- Apply workshop-standards.md throughout, especially plain English and the interpretation boundary.
- Do not invent customer facts. Ask when a business detail matters to the story.
- Every fictional entity must be clearly fictional, and the fiction boundary must be stated in the story.
- Prefer fewer, deeper sections over broad product coverage.

## Final response

List the approved story, the section plan, files created, open TBD values, and the questions the customer or account team must answer before dataset design.
````
