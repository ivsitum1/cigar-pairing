---
name: grill-me
description: Use for structured interview and design-tree alignment before coding or PRD; NOT for statistical grill-down of data Triggers include: Grill-me, grill me, shared understanding, interview before coding, design tree, clarify requirements.
version: 1.1
last_updated: 2026-03-30
domain: engineering
tokens: ~550
triggers:
  - Grill-me
  - grill me
  - shared understanding
  - interview before coding
  - design tree
  - clarify requirements
requires_packages: []
reference_files: []
pipeline_position: []
---

# Skill: Grill-me (Shared Understanding)

## When to use

Use before any non-trivial implementation or before writing a PRD when the problem is underspecified. Trigger phrases: "Grill-me", "interview me", "clarify the plan", "design tree".

## Scope

- **Application projects:** Run in the active repo where code will change.
- **Brain-only workspace:** If `agent rules` is referenced read-only from another project, perform Grill-me in the **application project** context or defer until that workspace is open.

## Objective

Interview the user until there is **shared understanding** of what to build, why, and what constraints apply. Do not start coding or lock a PRD until ambiguity is resolved.

## Method

1. **Design tree:** Walk branches of the design space (data model, APIs, UX, deployment, failure modes). Resolve dependencies between decisions in order (one decision at a time when they depend on each other).
2. **Codebase first:** If a question can be answered by reading the repository (e.g. "How is auth implemented?"), **explore the codebase** and cite findings. Ask the user only for what cannot be inferred from code or docs.
3. **Surface unknowns:** Explicitly list remaining assumptions and risks before closing the phase.

## Outcome

- Either a short written summary of agreed scope and constraints, or readiness to run **SKILL_write-prd** in the same session.
- Do not proceed to PRD if critical product or safety constraints are still open without user acknowledgment.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Hoću feature X; nisam siguran oko auth-a, sheme i migracija."  
**Output:** "Design tree: grananje odluka; što je u kodu `[EXTRACTED]`; što korisnik mora potvrditi ostaje `[BLANK]` prije PRD-a."

## Verification

- [ ] Major branches of the design tree addressed or explicitly deferred with rationale
- [ ] No redundant questions that code exploration could answer
- [ ] User and agent align on what "done" looks like

---

**Reference:** `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md`, `30_system/SKILLS/SKILL_write-prd.md`

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
