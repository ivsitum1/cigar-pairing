---
name: swiss-cheese
description: Runs multi-layer validation for critical analyses before reporting or publication, including pre-checks, monitored execution, post-validation, meta-review, and self-assessment. Use for high-stakes outputs or when users request Swiss Cheese verification.
version: 1.2
last_updated: 2026-05-18
domain: validation
tokens: ~1300
triggers:
  - swiss cheese
  - validation protocol
  - validate task
  - verification protocol
requires_packages: []
reference_files:
  - reference/scientific_thinking/peer_review_checklist.md
  - reference/scientific_critical_thinking/validity_framework.md
pipeline_position: [1, 3]
---

# Skill: Swiss Cheese Verification Protocol

## Description

Multi-layer validation for critical analyses. Load when: validation/verification/swiss cheese requested, or when executing primary outcome analysis, meta-analysis pooled estimate, end of analysis before writing, or pre-publication.

## Problem

Ensure critical outputs pass pre-execution checks, monitored execution, post-validation, meta-review, and self-assessment before delivery. Prevent undetected errors in high-stakes analyses.

## Acceptance Criteria

- [ ] Task has task_type and inputs
- [ ] Executor runs without error in isolation
- [ ] All 5 layers completed (or documented skip with reason)
- [ ] Self-assessment ≥9/10
- [ ] For statistics: path_raw_data set when loading data

## Constraints

- **Must:** Use Python `quality_validation.validate_with_swiss_cheese` (see `40_operations/python/quality_validation/`); require `path_raw_data` when R loads raw data (`40_operations/R/00_paths.R`)
- **Must not:** Skip layers without justification; deliver with self-assessment <9
- **Escalate:** If validation fails repeatedly or layer unclear
- **Optional gate (ECC):** for high-risk edits during validation fixes, state importers/data schema evidence before changing analysis code (gateguard-style discipline; no separate skill load required).

## When to use

**MANDATORY in these scenarios:**
1. **Critical analyses:** primary outcome analysis, meta-analysis pooled estimate, survival primary analysis, diagnostic accuracy primary, propensity-score matching result.
2. **End of analysis:** before transitioning to Methods/Results text (before WRITING subagent).
3. **Preparation for publication:** before submission, journal revision, final manuscript versions.

**Also use when:**
- User requests "validate task", "swiss cheese", "run through validation", "verification protocol"
- Running critical analysis or output through multi-layer checks
- Ensuring pre-exec, execution, post-validation, meta-review, and self-assessment

## Prerequisites

- Repo / project root known; `40_operations/python/quality_validation/` present
- For statistical analysis inside executor: R project / `path_raw_data` set as usual in `40_operations/R/`

## Honesty and grounding checkpoints

- For each layer outcome, classify as `[VERIFIED]` (passed with evidence), `[ASSUMPTION]` (not executed), or `[BLANK]` (blocked).
- Do not claim validation success if any mandatory layer is skipped without explicit rationale.
- If raw data path or executor is missing, stop and return `[BLANK]` with required inputs.
- Final delivery requires documented evidence for layer status and self-assessment threshold.

## Step-by-step procedure

1. **Define task:** Dict with `task_type`, `inputs`, and optionally `expect_output`.

2. **Define executor:** Python callable `executor(task)` that returns output (may call R subprocess or `rpy2` if needed).

3. **Run validation** (add `40_operations/python` to `PYTHONPATH` or run from repo with path as in `run_quality_validation.py`):
   ```python
   from quality_validation import validate_with_swiss_cheese
   result = validate_with_swiss_cheese(task, executor, existing_validators=None)
   ```

4. **Interpret result:**
   - `result["success"] is True`: output in `result["output"]`, assessment in `result["assessment"]`
   - `result["success"] is False`: check `result["layer"]` and `result["issues"]`; fix and re-run

5. **Optional – wrap existing function:**
   ```python
   from quality_validation import validate_with_swiss_cheese_fn
   result = validate_with_swiss_cheese_fn(my_fn, arg1, kwarg=2)
   ```

## Layers (reference)

1. Pre-execution (inputs, task_type)
2. Monitored execution (run executor, capture log)
3. Post-execution validation (optional validators)
4. Meta-review (summary, duration, errors)
5. Self-assessment (iteration toward threshold via `quality_validation.self_assessment`)

## Verification

- [ ] Task has task_type and inputs
- [ ] Executor runs without error in isolation if needed
- [ ] For statistics: path to raw data set via `path_raw_data` (see `40_operations/R/00_paths.R`) when loading data

## Examples

**Input:** "Validiraj ovaj primary endpoint rezultat prije prelaska na Results sekciju."  
**Output:** "Pokrećem svih 5 slojeva i prijavljujem status po sloju `[VERIFIED]`; ako layer 3 padne, rezultat ostaje `[BLANK]` dok se validatori i executor ne usklade."

## Related

- Self-assessment only: `mandatory_self_assess()` in `40_operations/python/quality_validation/` or CLI `run_quality_validation.py assess`
- Rules: `30_system/behavior_rules/05_verification.md`, `30_system/behavior_rules/08_swiss_cheese_solution.md`

## Learning integration

- **task_type:** validation
- **log_fields:** task_type, layers_passed, issues_found
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[validity_framework]]
- [[peer_review_checklist]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
