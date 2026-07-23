---
name: artifact-audit-bundle
description: Produces a reproducibility bundle for a scientific deliverable (exact code, environment freeze, plain-language methodology, session reference) so the work can be validated and reproduced months later. Use after producing an analysis, figure, or manuscript result that must be auditable.
version: 1.0
last_updated: 2026-07-03
domain: validation
tokens: ~600
triggers:
  - artifact bundle
  - audit bundle
  - reproducibility bundle
  - make this auditable
  - reproducible artifact
  - "@artifact-audit"
requires_packages: []
reference_files:
  - ../docs/CLAUDE_SCIENCE_ADOPTION.md
pipeline_position: [3]
---

# Skill: Artifact Audit Bundle

**Origin:** Claude Science "auditable artifacts" concept (`30_system/docs/CLAUDE_SCIENCE_ADOPTION.md`).
**Goal:** any scientific deliverable can be validated and reproduced later from a self-contained bundle. Reuses the existing `90_archive/artifacts/<run_id>/` convention (same tree as trajectory logs) — do not invent a new location.

## When to use

After producing an auditable deliverable: a statistical analysis, a figure, a pooled estimate, a manuscript Results paragraph derived from computation.

## Bundle contents (write to `90_archive/artifacts/<run_id>/`)

1. **`code.<ext>`** — the exact code that produced the result (R or Python), runnable as-is. No paraphrase, no "representative" snippet.
2. **`env.txt`** — environment freeze:
   - R: output of `sessionInfo()` (or `sessioninfo::session_info()`).
   - Python: `pip freeze` (or `uv pip freeze`) for the active environment.
3. **`methodology.md`** — plain-language description: what was done and why, in prose a reviewer can follow without reading the code. Distinct from code comments.
4. **`provenance.json`** — `{run_id, deliverable, timestamp, session_ref, inputs: [paths/DOIs], outputs: [paths]}`. `session_ref` links back to the chat/session; `inputs` list source data paths or citations.

## Steps

1. Resolve `<run_id>` (reuse the trajectory run_id if one exists for this session; else `date +%Y%m%d_%H%M%S`).
2. Create `90_archive/artifacts/<run_id>/` if absent.
3. Write the four items above. For `env.txt`, run the freeze command in the deliverable's actual environment — do not fabricate versions (`30_system/claude.md`: never fabricate).
4. If a number or figure in the deliverable cannot be traced to `code.<ext>`, stop — that is a reviewer-agent failure (`reviewer-agent.mdc`), fix before bundling.
5. Report the bundle path in chat. The bundle is the artifact; the deliverable prose stays clean.

## Guarantees

- **Reproducible:** code + env are sufficient to re-run.
- **Auditable:** methodology + provenance let a reviewer validate inputs and logic.
- **Located canonically:** under `90_archive/artifacts/`, so it is git-tracked with metadata (large binaries follow `.gitignore` policy).

## Related

- `.cursor/rules/reviewer-agent.mdc` (gate that must pass before bundling)
- `.cursor/rules/learning-loop.mdc` (`trajectory.jsonl` shares the run_id tree)
- `30_system/docs/CLAUDE_SCIENCE_ADOPTION.md`
