---
name: create-sop
description: Use to document multi-step fixes or complex integrations as reusable SOPs; NOT for simple error logging Triggers include: create SOP, standard operating procedure, document procedure, record fix.
version: 1.1
last_updated: 2026-03-30
domain: methodology
tokens: ~600
triggers:
  - create SOP
  - standard operating procedure
  - document procedure
  - record fix
requires_packages: []
reference_files: []
pipeline_position: []
---

# Skill: Create Standard Operating Procedure

## When to use

Use this skill when:
- A complex error required multiple steps to fix
- An error is promoted to `99_error_memory.mdc` and the fix involved non-trivial steps
- A complex integration or workflow was successfully completed and should be documented
- User requests "create SOP", "document this procedure", "record this fix"

## Prerequisites

- Clear understanding of the problem and its resolution
- `.agent/SOPs/TEMPLATE.md` available as template

## Step-by-step procedure

1. **Determine SOP necessity:**
   - Was the fix multi-step (>2 steps)?
   - Is it likely to recur?
   - Would another agent or future session benefit from this?
   - If YES to any: proceed. If NO to all: skip (a simple error_log entry suffices).

2. **Gather context:**
   - Error ID(s) from `.cursor/errors/error_log.jsonl`
   - Related entries in `99_error_memory.mdc`
   - Steps that were taken to resolve
   - How the fix was verified

3. **Write SOP from template:**
   - Copy `.agent/SOPs/TEMPLATE.md` structure
   - Fill in Title, Date, Category, Trigger, Problem, Resolution Steps, Verification
   - Save as `.agent/SOPs/SOP_[descriptive-name].md`

4. **Update SOP index:**
   - Add one-line entry to `.agent/SOPs/README.md` under the index table

5. **Cross-reference:**
   - If the error was promoted, link the SOP from `99_error_memory.mdc` entry
   - If relevant to a pipeline, note in the SOP's Notes section

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Dokumentiraj ovaj višekorakni fix (npr. pre-commit) da ga tim može ponoviti."  
**Output:** "SOP: koraci, preduvjeti, rollback `[INFERRED]`; verzije alata i putanje `[EXTRACTED]` iz repozitorija; netestirani korak `[ASSUMPTION]`."

## Verification

- [ ] SOP follows TEMPLATE.md structure
- [ ] Trigger section clearly describes when to use
- [ ] Resolution steps are specific and reproducible
- [ ] Verification checks are actionable
- [ ] README.md index updated

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
