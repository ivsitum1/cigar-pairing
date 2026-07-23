# Contrastive reflection pipeline

EvoSC-style comparison of success vs failure trajectories for rule/wiki updates.

## CLI

```bash
python 40_operations/scripts/contrastive_reflection.py \
  --success 90_archive/artifacts/<run_ok>/trajectory.jsonl \
  --failure 90_archive/artifacts/<run_fail>/trajectory.jsonl \
  --task-domain statistics \
  --write-error-log --write-wiki --json
```

Auto-pick latest pair:

```bash
python 40_operations/scripts/contrastive_reflection.py --auto-latest --task-domain code --json
```

## Outputs

- **error_log:** `.cursor/errors/error_log.jsonl` (pitfall + success pattern)
- **wiki:** `20_knowledge/wiki/concepts/Contrastive reflection patterns.md`

## Requires

ATDP-lite events in trajectories (`atdp_step` or `tool_selected`). See `TRAJECTORY_EMIT_PROTOCOL.md`.

## Related

- `40_operations/scripts/skill_gap_ingest.py`
- [[Skill trust tiers]]
- arXiv EvoSC [2602.01966](https://arxiv.org/abs/2602.01966) — contrastive reflection + consolidation
- `30_system/docs/SELF_EVOLVING_AGENTS_LANDSCAPE.md`
