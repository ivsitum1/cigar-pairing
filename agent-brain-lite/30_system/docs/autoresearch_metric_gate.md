# Autoresearch Metric Gate

## Goal

Define deterministic keep/discard policy for autonomous learning iterations.

## Score Components

`composite_score` is normalized to `[0, 100]`:

`composite_score = w_traj * trajectory_score_100 + w_eval * eval_score + w_tests * tests_score + w_lint * lint_score + w_stability * stability_score`

Default weights **without** trajectory trace:
- `w_eval = 0.55`
- `w_tests = 0.25`
- `w_lint = 0.10`
- `w_stability = 0.10`
- `w_traj = 0` (omitted from sum; remaining weights unchanged)

When a trajectory JSONL is linked (`trajectory_trace` on candidate or benchmark manifest), defaults in `self_eval_learning_loop.py`:
- `w_traj = 0.30`
- remaining weights scaled to sum to `0.70` (same relative ratios as above)

CLI: `--trajectory-weight` on `40_operations/scripts/self_eval_learning_loop.py`.

If `trajectory_score` is missing, do **not** apply `w_traj`; record `trajectory_score_missing` in manifest.

See [TRAJECTORY_RL_POLICY.md](TRAJECTORY_RL_POLICY.md).

## Skill-first Baseline

When only skill eval is available:
- `eval_score = pass_rate_pct`
- `tests_score = 100` if command success else `0`
- `lint_score = 100` when not evaluated (neutral default)
- `stability_score = 100` when not evaluated (neutral default)

This keeps backward compatibility while enabling richer gates later.

## Decision Thresholds

Let `delta = candidate_score - baseline_score`.

- `accept_threshold` default: `+0.10`
- `rollback_threshold` default: `0.00`
- `tie_breaker` default: `revert`

Decision:
1. if evaluation failed -> `revert`
2. if `delta >= accept_threshold` -> `accept`
3. if `delta <= rollback_threshold` -> `revert`
4. otherwise -> apply `tie_breaker` (`accept` or `revert`)

## Determinism Rules

- Use explicit numeric thresholds from CLI/runtime state.
- Persist all decision inputs in manifest and metrics artifacts.
- Never infer missing metrics silently; fill known neutral defaults and record them.

## Output Contract

Each iteration must emit:
- `baseline_score`
- `candidate_score`
- `delta`
- `decision`
- `decision_reason`

Schema: `30_system/docs/schemas/experiment_result.schema.json`.

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[SKILL_write-prd]]
- [[Skill optimization safety gates]]
- [[SKILL_create-skill]]
- [[SKILL_write-research-spec]]
- [[SKILL_ralph-loop]]
