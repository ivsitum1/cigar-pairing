# Self-Eval Driven Rules and Skills Learning Spec

## Purpose

Implement a closed-loop learning system that uses memory/self-evaluation telemetry to propose, validate, and optionally apply targeted improvements to:

- `30_system/SKILLS/SKILL_*.md`
- `.cursor/rules/*.mdc`

All decisions must be logged for auditability and reconstruction.

## Goals

- Reduce repeated failures by learning from recurring error patterns.
- Keep changes deterministic and reviewable.
- Apply automatic edits only when measurable quality improves.
- Record every proposal, decision, and outcome in changelog-compatible artifacts.

## Non-goals

- No model fine-tuning.
- No fully autonomous edits of high-risk core rules (unless explicitly forced).
- No destructive operations on unrelated files.

## Inputs

Primary signal (centralized, memory-first):

- `memory_signal = frequency_in_memory_events * (1 - avg_self_eval_score)`

Primary memory sources:

- `.agent/memory/raw_events.jsonl`
- `.agent/memory/self_eval.jsonl`
- `.agent/memory/memory.db` (`self_evaluations` table)

Optional signals:

- `30_system/docs/CHANGELOG_AUTO.jsonl`
- `30_system/SKILLS/evals/*.json`

## Data model

### Learning candidate

```json
{
  "candidate_id": "cand_20260430_001",
  "target_type": "skill|rule",
  "target_path": "30_system/SKILLS/SKILL_test-selection.md",
  "signal_window_days": 7,
  "frequency": 5,
  "avg_score": 0.62,
  "impact_score": 1.9,
  "reasons": ["low_score_retrieval", "repeated_error_tag:test-selection"]
}
```

### Learning event ledger record

`30_system/docs/LEARNING_UPDATES.jsonl` line schema:

```json
{
  "ts": "2026-04-30T10:50:00Z",
  "run_id": "run_20260430_1050",
  "candidate_id": "cand_20260430_001",
  "target_path": "30_system/SKILLS/SKILL_test-selection.md",
  "action": "proposed|applied|reverted|skipped",
  "before_metric": 72.0,
  "after_metric": 79.0,
  "decision_reason": "improved_pass_rate",
  "40_operations/tests": {
    "command": "python 40_operations/scripts/skill_eval_runner.py --skill-id test-selection --outputs ... --json",
    "ok": true
  },
  "patch_summary": "Added explicit disambiguation rule for Welch default when assumptions unclear."
}
```

## Scoring and policy

### Impact score

For each grouped memory pattern:

`memory_signal = frequency * (1 - avg_self_eval_score)`

Where:

- `frequency`: number of occurrences in time window
- `avg_self_eval_score`: mean of relevant self-eval scores in `[0,1]`

### Thresholds

- Minimum frequency: `3`
- Maximum avg score to qualify: `0.80`
- Minimum memory signal to propose patch: `0.60`
- Cooldown per target file: `24h`

### Safety classes

- **High-risk rules** (no auto-apply):  
  `.cursor/rules/core-principles.mdc`, `.cursor/rules/00_orchestrator_agent.mdc`
- **Medium-risk rules** (proposal-only by default):  
  other `.cursor/rules/*.mdc`
- **Skills** (auto-apply allowed):  
  `30_system/SKILLS/SKILL_*.md` when eval improves

## Pipeline

1. **Collect**
   - Read self-eval and error logs.
   - Aggregate by candidate target.

2. **Select**
   - Compute `impact_score`.
   - Keep candidates above thresholds.

3. **Propose**
   - Build minimal patch plan (single-file, single-intent).
   - Save proposal artifact in `.agent/task/learning_<run_id>.json`.

4. **Apply (guarded)**
   - For skills: apply deterministic patch template.
   - For rules: default proposal-only unless `--allow-rule-apply`.

5. **Validate**
   - Skills: run `40_operations/scripts/skill_eval_runner.py --outputs ... --json` if eval file exists.
   - Rules: run targeted tests (`pytest` subset) when available.

6. **Decide**
   - Keep only if metric improves.
   - Otherwise revert and log as `reverted`.

7. **Record**
   - Append ledger line to `30_system/docs/LEARNING_UPDATES.jsonl`.
   - Optionally run `40_operations/scripts/changelog_auto.py` in commit workflows.

## Changelog integration

- Learning loop writes:
  - `30_system/docs/LEARNING_UPDATES.jsonl` (detailed machine log)
  - `30_system/docs/LEARNING_UPDATES.md` (human summary)
- Git commit hook remains source of truth for `30_system/docs/CHANGELOG_AUTO.*`.
- Recommended commit message:
  - `auto-learn: <target> improve <metric_before>-><metric_after>`

## CLI contract

New command:

```bash
python 40_operations/scripts/self_eval_learning_loop.py --mode propose
python 40_operations/scripts/self_eval_learning_loop.py --mode apply --max-candidates 3
```

Options:

- `--mode propose|apply`
- `--window-days N`
- `--max-candidates N`
- `--allow-rule-apply`
- `--dry-run`
- `--json`

## Rollout

1. **Phase 1 (observe)**: propose-only, no edits.
2. **Phase 2 (skills auto-apply)**: apply only to skills with eval improvement gate.
3. **Phase 3 (rules guarded)**: optional apply for medium-risk rules with explicit flag.

## Failure handling

- If logs missing: return no-op report.
- If eval command fails: mark candidate `skipped`.
- If patch does not improve metric: revert file and log `reverted`.

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[Skill gap pipeline]]
- [[SKILL_create-skill]]
- [[SKILL_skill-discovery]]
- [[SKILL_scholarly-iteration-loop]]
- [[Skill optimization safety gates]]
