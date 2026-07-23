---
name: ai-detection
description: Use when checking/reducing AI detection score on existing text; for writing strategy guidance use avoid-ai-formulations instead Triggers include: check AI score, AI detection, reduce AI phrasing, natural writing.
version: 1.3
last_updated: 2026-06-16
domain: writing
tokens: ~700
triggers:
  - check AI score
  - AI detection
  - reduce AI phrasing
  - natural writing
requires_packages: []
reference_files:
  - reference/ai_detection_patterns.md
pipeline_position: [1, 4]
---

# Skill: AI Writing Detection and Revision

## When to use

Use this skill when:
- User requests "check AI score", "AI detection", "reduce AI phrasing", "natural writing"
- Revising text to avoid AI-detectable formulations
- Integrating with writing workflow (write → check → revise)

## Prerequisites

- Writing tools present: `30_system/behavior_rules/tools/check_ai_score_fast.R`, `30_system/behavior_rules/tools/writing/writing_workflow.R`
- Python environment for AI detection script if using full pipeline (check_ai_plagiarism.py)

## Step-by-step procedure

1. **Quick AI score (40_operations/R):**
   ```r
   source("30_system/behavior_rules/tools/check_ai_score_fast.R")
   result <- check_ai_score_fast(text = "Your text here", fast_mode = TRUE)
   # or: check_ai_score_fast(file_path = "path/to/file.txt")
   ```
   Use `result$score` (0–1) and `result$recommendations`.

2. **Full writing workflow (iterate until AI score < 20%):**
   ```r
   source("30_system/behavior_rules/tools/writing/writing_workflow.R")
   result <- write_with_ai_check(initial_text, target_ai_score = 0.20, max_iterations = 5)
   ```

3. **Pattern scan (local, preferred):**
   ```bash
   python 30_system/behavior_rules/tools/ai_pattern_scan.py path/to/file.txt --json
   ```
   Integrated in `check_ai_score_only()` as `pattern_scan` component (weight 45–65%).

4. **Pattern checklist:** Use `reference/ai_detection_patterns.md` — 15-step phased revision; academic Methods exception for passive/hedging.

5. **Rules:** Apply `writing-avoid-ai.mdc`. Goal is natural accurate prose, not bypassing detection tools. Target **< 0.20** combined score; keep draft trail (detectors are probabilistic; ESL false positives occur).

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Pokreni AI score na Discussion sekciji i reci što popraviti."  
**Output:** "Pokrećem `check_ai_score_fast` ili pipeline; score `[VERIFIED]` iz R outputa; prijedloge reformulacija `[INFERRED]` uz `writing-avoid-ai` reference."

## Verification

- [ ] AI score checked before finalizing manuscript text
- [ ] Banned words and AI phrases removed (see writing_realtime_check)
- [ ] Final prose sounds natural and not template-like

## Related

- `SKILL_avoid-ai-formulations.md` – natural writing strategies
- `.cursor/rules/writing-avoid-ai.mdc` – phrases to avoid

## Learning integration

- **task_type:** writing
- **log_fields:** ai_score_before, ai_score_after, strategies_used
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion. If `writing_workflow.R`/`.py` runs, it calls `log_writing_check()`.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[ai_detection_patterns]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
