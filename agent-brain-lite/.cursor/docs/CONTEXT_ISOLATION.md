# Context Isolation (GSD Strategy)

**Purpose:** Keep the active context window below 50–60% to avoid context rot. Use phase-specific files instead of stuffing the prompt. Prefer scalpel over sledgehammer: load only the context needed for the current sub-task.

---

## 50–60% rule

Efficiency drops when context exceeds roughly 50–60% of the window. To maintain output quality:

- Do not load all rules and skills at once.
- Keep project state, roadmaps, and phase-specific details in **separate markdown files** that are read only when needed.
- Use the Tier system (context-optimization.mdc): Tier 0 kernel + at most one Tier 1 + on-demand Tier 2/3.

---

## Where state lives

| Content | Location |
|--------|----------|
| Project state, task plans, research output | `.agent/task/` |
| Architecture, schemas, API | `.agent/system/` |
| SOPs, error memory, procedures | `.agent/SOPs/` |
| Auto-progress log (max ~200 lines) | `.agent/MEMORY.md` |
| Handoff history | `.agent/handoff_log.jsonl` |
| Phase context (when project contains brain) | `30_system/04_documentation/context/main.md`, `commit.md`, `log.md` |

Reference: `30_system/docs/BRAIN_AND_PROJECT.md` for full layout when agent-rules is used inside a project.

---

## Scalpel loading

- Load only the **specific context** needed for the current sub-task.
- Avoid loading full pipelines or all rules at once.
- For skills: use progressive disclosure (scan YAML → load full skill → load reference files only when executing the step that needs them).
- For pipelines: reference `30_system/behavior_rules/22_pipeline_and_refinement.md` and `30_system/behavior_rules/23_figure_visualization_pipeline.md` for stages; do not inline entire pipeline content into the prompt.

---

## Sub-agents and parallelization

For complex tasks, use sub-agents or Agent Teams (if enabled) to parallelize work and avoid context contamination. Hand off with brief context (e.g. ≤30 tokens); see orchestrator handoff format in `00_orchestrator_agent.mdc`.

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
