# AI Agent Behavior Rules - Overview

**REFERENCE ONLY.** This folder is **human-readable documentation**. The agent does **not** read `30_system/behavior_rules/` for execution. **Authority:** `.cursor/rules/*.mdc` (active rules) and `30_system/SKILLS/*.md` (on-demand). See context-optimization.mdc (Authority Model).

## Purpose

This folder contains all behavior rules and guidelines for AI agents working on scientific paper writing projects in the field of medicine. Rules are organized into logical categories for easier navigation and maintenance.

> **⚠️ MIGRATION STATUS:** Many rules have been migrated to `.cursor/rules/` for Cursor IDE integration.
> See `.cursor/rules/README.md` for active Cursor-native rules.
> This folder is **REFERENCE ONLY** — agent interacts only with `.cursor/rules/` and `30_system/SKILLS/`.

**Related resources:**
- `.cursor/rules/` - **ACTIVE** Cursor-native rules (automatically activated)
- `30_system/SKILLS/` - **ACTIVE** Procedural instructions (invoke with `@skill-name`); includes e.g. `SKILL_figure-pipeline.md` for the figure/visualization pipeline
- `20_knowledge/reference_library/` - Centralized library of reference materials (books, key papers, guidelines)
- `20_knowledge/reference_library/statistics/knowledge_bases/` - Comprehensive knowledge bases:
  - `modern_statistical_literature_2024_2025.md` - Latest methodological advances (25 critical resources)
  - `medical_data_science_laboratory.md` - Complete 17-layer methodological framework
- `.ai/` - Setup scripts and configurations for new projects

---

## Migration Status

### ✅ Fully Migrated
- `00_core_principles.md` → `.cursor/rules/core-principles.mdc` (⚠️ marked as migrated)
- ~~17_context_optimization.md~~ → removed; use `.cursor/rules/context-optimization.mdc`

### ⚠️ Partially Migrated
- `02_statistics.md` → Test selection framework migrated to `.cursor/rules/statistics-test-selection.mdc`
- `10_ai_writing_plagiarism.md` → AI formulation avoidance migrated to `.cursor/rules/writing-avoid-ai.mdc`
- `03_scientific_writing.md` → Reporting guidelines migrated to `.cursor/rules/reporting-*.mdc`

### 📋 Still Active (Not Migrated Yet)
- `01_general_rules.md` - General communication rules
- `04_visualization.md` - Visualization standards
- `05_verification.md` - Verification protocol
- `06_study_types.md` - Study type rules
- `07_project_structure.md` - Project structure
- `08_swiss_cheese_solution.md` - Swiss Cheese solution
- `09_workflow_optimization.md` - Workflow optimization
- `11_r_programming.md` - R programming rules
- `12_machine_learning.md` - ML rules
- `13_agentic_workflow.md` - Agentic workflow
- `14_learning_loop.md` - Learning loop
- `15_agent_roles.md` - Agent roles
- `16_cursor_optimization.md` - Cursor optimization
- `22_pipeline_and_refinement.md` - Named pipelines (PaperBanana-style), REFINE phase, skill sequencing
- `23_figure_visualization_pipeline.md` - Figure/visualization pipeline (Pipeline 5)

---

## Folder Structure

```
30_system/behavior_rules/
├── README.md                    # This document - structure overview
├── 01_general_rules.md          # General communication rules, style, self-assessment
├── 02_statistics.md             # Statistical rules and guidelines (⚠️ partially migrated)
├── 03_scientific_writing.md     # PRISMA, GRADE, reporting standards (⚠️ partially migrated)
├── 04_visualization.md          # Standards for publication-quality figures
├── 05_verification.md           # Swiss Cheese protocol - verification and checking
├── 06_study_types.md            # Rules for different study types
├── 07_project_structure.md      # Standardized project structure
├── 08_swiss_cheese_solution.md  # Detailed solution for Swiss Cheese Problem
├── 09_workflow_optimization.md  # Optimized workflows for different tasks
├── 21_publishing_workflow.md    # Publishing workflow; journal guidelines placeholder
├── 22_pipeline_and_refinement.md # Named pipelines (PaperBanana-style), REFINE phase, skill sequencing
├── 23_figure_visualization_pipeline.md # Figure/visualization pipeline (Pipeline 5)
├── 27_rule_maintenance.md       # How to propose, review, version, and deprecate behavior_rules
├── 28_external_integration.md   # MCP failures, retries, fallbacks for discovery pipelines
├── 10_ai_writing_plagiarism.md  # AI writing detection and plagiarism (⚠️ partially migrated)
├── 11_r_programming.md          # Detailed R-specific rules and best practices
├── 12_machine_learning.md       # ML workflow protection - data leakage prevention
├── 13_agentic_workflow.md       # Agentic workflow controls - task decomposition, checkpoints
├── 14_learning_loop.md           # Learning loop protocol for adaptive behavior
├── 15_agent_roles.md            # Overview of eight specialized agent roles and collaboration
├── 16_cursor_optimization.md    # Cursor IDE-specific optimizations for speed and efficiency
├── 00_core_principles.md        # ⚠️ MIGRATED to .cursor/rules/core-principles.mdc
├── agents/                      # Detailed role definitions for each agent
│   ├── 01_clinical_decision_support.md
│   ├── 02_clinical_research_methodologist.md
│   ├── 03_code_quality_assurance.md
│   ├── 04_medical_data_science/
│   ├── 04_medical_data_science_coder.md
│   ├── 05_prompt_engineering_specialist.md
│   ├── 06_rules_roles_maintainer.md
│   ├── 07_statistical_analysis_expert.md
│   └── 08_academic_writing_specialist.md
├── tools/                       # Tools and utilities
│   ├── writing/                 # Writing tools (moved from .ai/)
│   ├── agents/                  # Agent tools (moved from .ai/)
│   ├── check_ai_plagiarism.py
│   ├── learning_loop.py
│   ├── learning_integration.py
│   └── [other tools]
├── CHANGELOG.md
└── VERSION.md
```

---

## How to Use

### For New Projects

1. **Use `.cursor/rules/`** - Active Cursor-native rules (automatically activated)
2. **Use `30_system/SKILLS/`** - Procedural instructions (invoke with `@skill-name`)
3. **Reference `30_system/behavior_rules/`** - For detailed documentation when needed

### For AI Agents

1. **Do NOT read `30_system/behavior_rules/` for execution.** Active rules are in `.cursor/rules/` and `30_system/SKILLS/`.
2. **Load active rules** from `.cursor/rules/` (Cursor automatically does this)
3. **Use Skills** from `30_system/SKILLS/` when needed
4. **Reference `30_system/behavior_rules/`** only when a human or explicit prompt points to a specific file for detail

---

## Key Principles

### Accuracy and Reliability of References (EXTREMELY IMPORTANT)

- **Reference Verification**: Always verify that references exist and are accurate
- **Formatting**: Use consistent format throughout the document
- **Source Quality**: Prefer peer-reviewed and authoritative sources
- **Cross-Reference Check**: Verify that references match the text
- **Content Verification**: Verify that cited works actually support the claim
- **Online Verification**: Check availability of DOIs and URLs
- **Documentation**: Record all verifications in verification log

### Academic and Scientific Standards
- Always maintain scientific rigor and statistical accuracy
- Use academic language that sounds natural and human, not artificial
- Never fabricate or lie - all claims must be verifiable
- All statistical claims must be accurate and supported by evidence
- Cite sources appropriately using established academic formats
- Maintain objectivity and avoid overemphasizing findings

### Statistical Best Practices
- Follow R best practices for meta-analysis
- Preserve analysis reproducibility
- Clearly document all statistical decisions
- Always report exact p-values (not just p < 0.05)
- Always report effect estimates with 95% confidence intervals
- Distinguish between statistical and clinical significance
- Follow PRISMA 2020 and GRADE standards

### Medical Research Standards
- Follow CONSORT, STROBE, and PRISMA reporting guidelines
- Consider Minimal Clinically Important Difference (MCID) when available
- Report Number Needed to Treat (NNT) for binary outcomes when appropriate
- Assess evidence quality using GRADE approach
- Always consider both absolute and relative risks

### Communication
- Direct, accurate, concise, academic language
- Use standard medical and statistical terminology
- Honesty - do not sugarcoat results or interpretations
- Think outside the box; prioritize innovation and practical solutions

### Self-Assessment
- Mandatory self-assessment before delivering any output
- Quality rating of response (scale 1-10)
- Iteration and improvement until 10/10 is achieved
- Consider: accuracy, completeness, clarity, practical utility, code correctness

---

## Version Tracking and Changelog

The Behavior Rules System includes comprehensive version tracking and changelog management.

### CHANGELOG.md

**Location:** `30_system/behavior_rules/CHANGELOG.md`

Centralized changelog following [Keep a Changelog](https://keepachangelog.com/) format. Tracks:
- **Added**: New rules, features, agents
- **Changed**: Modifications to existing rules
- **Deprecated**: Rules marked for removal
- **Fixed**: Bug fixes and corrections
- **Security**: Security-related changes

### VERSION.md

**Location:** `30_system/behavior_rules/VERSION.md`

Version registry tracking all module versions in one place. Includes:
- System version (semantic versioning)
- Individual module versions
- Last updated dates
- Module status

---

## References to Original Files

These rules were consolidated from the following sources:

- `.ai/rules.md` → `01_general_rules.md` (now also in `.cursor/rules/`)
- `.ai/context.md` → Integrated into `01_general_rules.md` (archived)
- `.ai/preferences.md` → Integrated into `01_general_rules.md` and `02_statistics.md` (archived)
- All duplicates consolidated into appropriate files
- No need for duplicates - all rules are in one place

**Note:** Original files are retained in their original locations or archived. This consolidated version serves for easier agent navigation.

---

## Contact and Support

For questions or suggestions about rules, contact the project owner.

---

**Version:** 3.3  
**Created:** 2024-12-31  
**Last updated:** 2026-04-10  
**Status:** Partially Migrated to `.cursor/rules/`

## Semantic graph (auto)

- [[Behavior rules hub]]
- [[Orchestrator - agent roles]]
- [behavior rules INDEX](../docs/indexes/behavior_rules_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[Behavior rules hub]]
- [[VERSION]]
- [[15_agent_roles]]
- [[23_figure_visualization_pipeline]]
- [[00_core_principles]]
