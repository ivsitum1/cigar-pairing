# Run Manifest

## Purpose

`manifest.json` is the canonical run descriptor for autonomous learning cycles.

## Location

`90_archive/artifacts/<run_id>/manifest.json`

## Required Fields

- `run_id`
- `started_at`
- `mode`
- `seed`
- `window_days`
- `max_candidates`
- `allow_rule_apply`
- `dry_run`
- `thresholds`
- `weights`
- `proposal_file`

## Optional Fields

- `resumed_from`
- `ended_at`
- `status`
- `error`

## Example

```json
{
  "run_id": "run_20260430_153000",
  "started_at": "2026-04-30T13:30:00+00:00",
  "mode": "apply",
  "seed": 42,
  "window_days": 7,
  "max_candidates": 3,
  "allow_rule_apply": false,
  "dry_run": false,
  "thresholds": {
    "accept_threshold": 0.1,
    "rollback_threshold": 0.0,
    "tie_breaker": "revert"
  },
  "weights": {
    "eval_weight": 0.55,
    "tests_weight": 0.25,
    "lint_weight": 0.1,
    "stability_weight": 0.1
  },
  "proposal_file": ".agent/task/learning_run_20260430_153000.json"
}
```

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[SKILL_write-prd]]
- [[SKILL_write-research-spec]]
- [[14_learning_loop]]
- [[Autonomous Skill Optimization Agent]]
- [[SKILL_ralph-loop]]
