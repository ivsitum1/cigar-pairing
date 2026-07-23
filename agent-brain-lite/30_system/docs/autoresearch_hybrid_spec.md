# Autoresearch Hybrid Spec

## Purpose

This document defines how to adopt the `autoresearch` operating style in this workspace without vendoring external source code. The integration is concept-level and must remain compatible with current guardrails, logging, and reproducibility requirements.

## Scope

We adopt:
- iterative single-change experimentation;
- objective keep/discard decisions from measured outcomes;
- deterministic rollback on regression or failed validation;
- end-to-end traceability of decisions and artifacts.

We do not adopt:
- direct code import from upstream `karpathy/autoresearch`;
- uncontrolled self-modifying behavior across unrelated files;
- bypassing high-risk rule protections.

## Operating Model

Each cycle follows:
1. Propose one bounded change for one target file.
2. Apply patch in a guarded execution context.
3. Run mandatory evaluation for that target class.
4. Decide using metric gates and tie-break policy.
5. Keep or rollback deterministically.
6. Persist ledger, manifest, and human-readable summary.

Signal policy:
- candidate ranking must use one centralized `memory_signal`;
- signal inputs must come from memory artifacts only.

## Policy Boundaries

### Allowed targets
- `30_system/SKILLS/SKILL_*.md`
- `.cursor/rules/*.mdc` except high-risk rule files protected from auto-apply

### High-risk policy
High-risk rules are proposal-only and must not be automatically applied:
- `.cursor/rules/core-principles.mdc`
- `.cursor/rules/00_orchestrator_agent.mdc`

### Patch discipline
- Single-file, single-intent patches only.
- No hidden side effects across unrelated paths.
- No acceptance without a recorded decision object.

## Acceptance Logic

A change can be kept only if:
- evaluation command succeeds;
- decision gate returns `accept`;
- all required artifacts for that iteration are written.

If any condition fails, rollback is mandatory and logged.

## Required Artifacts

For every run:
- `90_archive/artifacts/<run_id>/manifest.json`
- `90_archive/artifacts/<run_id>/metrics.json`
- `90_archive/artifacts/<run_id>/decision.md`

For every cycle:
- append machine ledger in `30_system/docs/LEARNING_UPDATES.jsonl`
- append human ledger in `30_system/docs/LEARNING_UPDATES.md`
- append changelog entry in `30_system/docs/CHANGELOG_AUTO.jsonl` and `30_system/docs/CHANGELOG_AUTO.md` for each auto-learn file mutation

## Quality Goals

- Deterministic decisions for identical inputs and thresholds.
- Re-runnable workflow with resumable state.
- Audit-friendly trail from candidate proposal to final decision.

## Reference

- `30_system/docs/SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md`
- `40_operations/scripts/self_eval_learning_loop.py`
- `30_system/docs/autoresearch_metric_gate.md`

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[27_rule_maintenance]]
- [[00_core_principles]]
- [[SKILL_ralph-loop]]
- [[Orchestrator - agent roles]]
- [[SKILL_write-prd]]
