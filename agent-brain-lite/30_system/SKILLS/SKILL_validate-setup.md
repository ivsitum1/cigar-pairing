---
name: validate-setup
description: Use to verify existing project structure is correct; for creating new structure use setup-project Triggers include: validate setup, check project structure, verify setup.
version: 1.1
last_updated: 2026-03-30
domain: setup
tokens: ~750
triggers:
  - validate setup
  - check project structure
  - verify setup
requires_packages: []
reference_files: []
pipeline_position: [2]
---

# Skill: Validate Project Setup

## When to use

Use this skill when:
- User requests "validate setup", "check project structure", "verify setup"
- After running setup or when checking if project structure is correct
- Before starting analysis (ensure folders and paths exist)

## Prerequisites

- `.ai` folder present with `validate_setup.R` or `validate_setup.py`
- Project root = folder containing `.ai/`, `30_system/behavior_rules/`, `40_operations/R/` (in RStudio: set project to this folder)

## Step-by-step procedure

1. **Run validation script:**
   ```r
   # R (from project root)
   source(".ai/validate_setup.R")
   result <- validate_setup(".")   # or validate_project_structure(".")
   ```
   OR
   ```bash
   python .ai/validate_setup.py
   ```

2. **Check result:**
   - `passed` / success: all required folders and templates present
   - If failed: report `missing` folders/files and `fixes` (create missing dirs, add templates)
   - **Codebook soft warnings** (non-blocking): report `codebook_warnings` if present:
     - Raw data in `01_input/data/00_inbox/raw/` (`.csv`/`.xlsx`) but no `01_input/codebook/dataset_codebook.md`
     - Data files under `01_input/data_extraction/` but no `01_input/data_extraction/codebook.md`
   - Fix codebook gaps: `python agent-rules/40_operations/scripts/codebook_seed.py --root .` from project root
   - Always mention specific missing elements by name: **README** (index.md), **.gitignore**, **session_info** (reproducibilnost). Use wording "nedostaje", "missing", "dodaj", "preporuča" when listing gaps. Never state "struktura je ispravna" or "sve je prisutno" if any required item is missing.

3. **Report to user:**
   - List what passed (existing folders)
   - List what is missing (if any); name 01_input, 02_analysis, 03_output when these are missing (kritične mape)
   - For flat structure (all files in one folder): identify lack of **podstruktura** / **organizacije** / **mapa**; recommend **reorganizacija**, creating 01_input etc., "odvojiti", "preporučiti"
   - Suggest commands or steps to fix (reorganiz, kreirati, missing)

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Je li ovaj workspace ispravno spojen na agent-rules i foldere projekta?"  
**Output:** "Provjera mapa i skripti `[VERIFIED]` ako čitam FS; read-only pravilo za referencirani agent-rules `[EXTRACTED]`; drugačiji root `[ASSUMPTION]`."

## Verification

- [ ] All required folders exist (01_input, 02_analysis, 03_output, etc.)
- [ ] Template files present where expected
- [ ] Paths in scripts are valid for current project root

## Related

- Setup: `SKILL_setup-project.md`
- Paths: `40_operations/R/00_paths.R` (project root, path_raw_data for statistics)

## Learning integration

- **task_type:** validation
- **log_fields:** passed, missing_items, fixes_applied
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
