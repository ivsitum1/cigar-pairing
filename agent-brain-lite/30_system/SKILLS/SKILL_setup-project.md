---
name: setup-project
description: Use to create new project directory structure; for checking existing structure use validate-setup Triggers include: setup project, create project, initialize project.
version: 1.1
last_updated: 2026-03-30
domain: setup
tokens: ~950
triggers:
  - setup project
  - create project
  - initialize project
requires_packages: []
reference_files: []
pipeline_position: [2]
---

# Skill: Setup New Project

## When to use

Use this skill when:
- User requests "setup project", "create project", "initialize project"
- Starting a new research project
- Need to create standardized project structure

## Prerequisites

- `.ai` folder present in project root
- R or Python installed
- Write permissions in project directory

## Step-by-step procedure

1. **Detect project type:**
   - Analyze project name for study type patterns (meta-analysis, RCT, cohort, etc.)
   - Check existing files if any
   - Calculate confidence score
   - Use default if confidence < 0.7

2. **Run setup script:**
   ```r
   # R version
   source(".ai/setup_project.R")
   setup_project()  # Uses current folder
   ```
   OR
   ```bash
   # Python version
   python .ai/setup_project.py
   ```

3. **Verify structure:**
   - Check that all folders created (01_input, 02_analysis, 03_output, etc.)
   - Verify template files exist
   - Check study-specific folders (PRISMA, CONSORT, STROBE) if applicable

4. **Confirm completion:**
   - Report created structure
   - List key folders and their purposes
   - Note any study-specific additions

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Inicijaliziraj novi projekt s brain/agent-rules strukturom."  
**Output:** "Koristim `project_init` ili ekvivalent; struktura mapa `[VERIFIED]` nakon provjere; pogrešan workspace root `[BLANK]`."

## Verification

- [ ] All required folders exist
- [ ] Codebook templates seeded: `01_input/data_extraction/codebook.md`, `01_input/codebook/dataset_codebook.md` (via `codebook_seed` / `project_init`)
- [ ] Template files created (README, changelog, search_strings)
- [ ] Study-specific folders added (if applicable)
- [ ] R/Python scripts have correct paths
- [ ] Git initialized (if requested)

## Related rules

- `.cursor/rules/project-structure.mdc` (when migrated)
- `30_system/behavior_rules/07_project_structure.md`
- `30_system/behavior_rules/09_workflow_optimization.md` (Workflow 1)

## Learning integration

- **task_type:** setup
- **log_fields:** project_type, study_type, validation_passed, errors
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion via `python 30_system/behavior_rules/tools/ingest_learning_block.py`. If `setup_project.py`/`.R` runs, it logs automatically.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
