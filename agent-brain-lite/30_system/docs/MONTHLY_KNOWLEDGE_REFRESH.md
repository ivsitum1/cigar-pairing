# Monthly Knowledge Refresh Policy

This policy ensures periodic updates from external knowledge sources relevant to this workspace.

## Cadence

- Frequency: once per month
- Recommended day: first working Monday of each month

## Scope

- Science
- Medicine
- Statistics
- AI / agentic workflows / tooling

## Runner

- Script: `40_operations/scripts/monthly_knowledge_refresh.py`
- Example:
  - `python 40_operations/scripts/monthly_knowledge_refresh.py --month 2026-05`

This creates:

- `30_system/docs/knowledge_refresh/YYYY-MM.md`
- `30_system/docs/knowledge_refresh/RUN_LOG.md`

## Operational Loop

1. Generate monthly template.
2. Fill reviewed papers/guidelines/tools.
3. Mark accepted rule/skill/doc updates.
4. Apply updates through normal changelog and validation process.

## Scheduling Options

### Windows Task Scheduler

- Create monthly task running:
  - `python C:\path\to\agent rules\40_operations/scripts\monthly_knowledge_refresh.py`

### Linux cron

- Example (first day, monthly at 09:00):
  - `0 9 1 * * cd /path/to/agent\ rules && python3 40_operations/scripts/monthly_knowledge_refresh.py`

## Related Nodes

- [Automation index](AUTOMATION_INDEX.md)
- [Task optimization check](TASK_OPTIMIZATION_CHECK.md)
- [Scripts README](../40_operations/scripts/index.md)
