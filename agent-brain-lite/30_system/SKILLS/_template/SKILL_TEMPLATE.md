---
name: SKILL_NAME
description: >
  Triggered for [domain/problem]. Use when user asks for [keywords/synonyms].
  Produces deterministic outputs in `/10_projects/projects/[client]/[SKILL_NAME]/[YYYY-MM-DD]/`.
version: 0.1.0
last_updated: 2026-05-05
---

# SKILL_NAME

## Metadata

- Owner: [TO_CONFIRM]
- Inputs required:
  - client_name
  - task_brief
  - output_format
- Outputs:
  - main artifact
  - execution log
  - feedback append to `learnings.md`

## Quick Start Checklist

1. Validate required inputs.
2. Load only minimal context files required for this task.
3. Confirm output path before generation.
4. Execute.
5. Verify against acceptance criteria.
6. Save artifacts and append learning.

## Full Procedure (Load when needed)

### 1) Intake

- Parse task objective and constraints.
- Mark missing critical data as `[TO_CONFIRM]`.

### 2) Context Injection

- Load only:
  - `/30_system/context/user.md`
  - `/30_system/context/soul.md`
  - relevant files under `/shared-brand` (if needed)
- Do not load unrelated project data.

### 3) Execution

- Produce output in the requested format.
- Keep assumptions explicit.
- Use deterministic naming:
  - `/10_projects/projects/[client_name]/[SKILL_NAME]/[YYYY-MM-DD]/artifact.ext`

### 4) Verification Gate

- Check output against:
  - task brief
  - constraints
  - quality criteria
- If failed, run one repair pass and re-check.

### 5) Closure

- Ask exactly 3 feedback questions:
  1. What was most useful?
  2. What was missing or unclear?
  3. What should be improved next time?
- Append summarized learning to `learnings.md`.

## Output Contract

- All outputs must be written under:
  - `/10_projects/projects/[client_name]/[SKILL_NAME]/[YYYY-MM-DD]/`
- No final artifacts should remain chat-only.

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)
