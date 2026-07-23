---
name: write-prd
description: Use for software Product Requirements Document with passes flags; NOT for PRISMA systematic review checklist (use prisma-checklist) Triggers include: Write PRD, product requirements, prd.json, PRD, requirements document, passes flag.
version: 1.1
last_updated: 2026-03-30
domain: engineering
tokens: ~650
triggers:
  - Write PRD
  - product requirements
  - prd.json
  - PRD
  - requirements document
  - passes flag
requires_packages: []
reference_files:
  - 30_system/docs/templates/prd.schema.json
  - 30_system/docs/templates/prd.example.json
pipeline_position: []
---

# Skill: Write-PRD (Source of Truth)

## When to use

After Grill-me (or equivalent alignment). Produces a durable **Product Requirements Document** as external memory for agents. Not for PRISMA systematic-review checklists; for that use `prisma-checklist`.

## Scope

- Default paths (application repo root): `30_system/docs/prd.json` **or** `30_system/docs/prd.md`.
- JSON is preferred for machine-readable `passes` flags and automation; Markdown is acceptable if the team does not use JSON.

## Structure (required content)

1. **Problem:** What problem exists and for whom.
2. **Solution:** What you are building at a high level (durable; avoid implementation trivia that will churn).
3. **User stories / requirements:** Each item describes desired behavior; must be testable or verifiable in principle.
4. **Technical decisions:** Architectural choices that must stay stable so implementation does not drift (interfaces, stores, auth model, etc.).
5. **Execution chain (recommended):** Record intended flow `grill-me -> write-prd -> prd-to-issues -> ralph-loop`.
6. **Verification protocol (recommended):** Include claim status labels (`VERIFIED/INFERRED/UNVERIFIED`), baseline-vs-steered checks, and reproducibility metadata.

## Ralph compatibility

- In JSON form, **every** trackable requirement or user story MUST include `"passes": false` until verified done.
- Optional: nested `issues` or tasks with `passes` and `priority` (see `30_system/docs/templates/prd.schema.json`).
- For model-behavior work, keep `verification_protocol.baseline_vs_steered.passes` and `verification_protocol.reproducibility.passes` as `false` until objective checks are complete.

## Procedure

1. Read `30_system/docs/templates/prd.example.json` and `30_system/docs/templates/prd.schema.json`.
2. Create or update `30_system/docs/prd.json` (or `30_system/docs/prd.md` with an equivalent checklist) at the **application** project root.
3. Keep the PRD concise to limit token bleed in later Ralph iterations.
4. If migrating from ad hoc notes, map them into stories with `passes: false`.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Napiši PRD za bulk export s `passes` flagovima."  
**Output:** "Polja PRD-a i passes `[EXTRACTED]` iz dogovora; edge caseovi `[INFERRED]`; nepotvrđeni API ugovori `[BLANK]`."

## Verification

- [ ] Problem, solution, and stories are present
- [ ] Each story/requirement can be tied to a test or observable outcome
- [ ] `passes` fields exist for Ralph tracking (JSON) or equivalent checklist (Markdown)

---

**Reference:** `30_system/SKILLS/SKILL_prd-to-issues.md`, `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md`

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[prd.schema]]
- [[prd.example]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
