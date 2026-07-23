# Task Optimization Check

Use this check for any new task context (statistics, study design, manuscript writing) before execution.

## Command

- Windows:
  - `python 40_operations/scripts\task_optimization_check.py --task-file ".agent\task\templates\task_context_template.md" --task-type general`
- Linux/Mac:
  - `python3 40_operations/scripts/task_optimization_check.py --task-file ".agent/task/templates/task_context_template.md" --task-type general`

## Target

- `TASK_OPTIMIZATION_SCORE >= 98/100`

## Task types

- `statistics`
- `methodology`
- `writing`
- `general`

## Expected workflow

1. Copy template: `.agent/task/templates/task_context_template.md`
2. Fill task-specific content and links.
3. Run checker.
4. Improve missing sections/gates until score is >= 98/100.

## Example (98+ ready)

- Example file: `.agent/task/examples/new_statistics_task_example.md`
- Example run:
  - `python 40_operations/scripts/task_optimization_check.py --task-file .agent/task/examples/new_statistics_task_example.md --task-type statistics`

## Related nodes

- [Scripts README](../40_operations/scripts/index.md)
- [Workspace optimization check](../40_operations/scripts/workspace_optimization_check.py)
- [Folder index hub](FOLDER_INDEX.md)
