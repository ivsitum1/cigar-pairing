# Workflow: Cursor Migration and Enhancement

**Version:** 1.0  
**Created:** 2026-01-27  
**Status:** Active

---

## Overview

This workflow documents the complete migration from `30_system/behavior_rules/` to Cursor's native `.cursor/rules/` structure, addition of Skills, and implementation of learning loop integration.

---

## Phase 1: Core Structure ✅ COMPLETED

### 1.1 Directory Creation
- [x] Create `.cursor/rules/` directory
- [x] Create `30_system/SKILLS/` directory
- [x] Create documentation files

### 1.2 Core Rules Migration
- [x] `core-principles.mdc` ← `00_core_principles.md`
- [x] `context-optimization.mdc` ← `17_context_optimization.md` (source file later removed; .mdc is canonical)
- [x] Both set to `alwaysApply: true`

---

## Phase 2: Critical New Rules ✅ COMPLETED

### 2.1 Test Selection Framework
- [x] `statistics-test-selection.mdc` - Modern test selection hierarchy
  - PRIMARY: Welch, Permutation, Yuen-Welch
  - SECONDARY: Non-parametric (sensitivity only)
  - Clear rationale and decision tree

### 2.2 Writing Rules
- [x] `writing-avoid-ai.mdc` - AI formulation avoidance
  - Specific formulations to avoid
  - Natural writing strategies
  - AI checker integration

---

## Phase 3: Reporting Guidelines ✅ COMPLETED

### 3.1 Core Guidelines
- [x] `reporting-strobe.mdc` - STROBE Statement (observational studies)
- [x] `reporting-consort.mdc` - CONSORT 2010 (RCTs)
- [x] `reporting-prisma.mdc` - PRISMA 2020 (systematic reviews)
- [x] `reporting-tripod-ai.mdc` - TRIPOD+AI (prediction models)

### 3.2 Additional Guidelines
- [x] `reporting-stard.mdc` - STARD 2015 (diagnostic accuracy)
- [x] `reporting-care.mdc` - CARE Statement (case reports)
- [x] `reporting-spirit.mdc` - SPIRIT 2013 (trial protocols)
- [x] `reporting-squire.mdc` - SQUIRE 2.0 (quality improvement)
- [x] `reporting-cheers.mdc` - CHEERS 2022 (economic evaluations)

### 3.3 Auto-Detection System
- [x] `reporting-auto-detect.mdc` - Automatic guideline selection
  - File pattern detection
  - Keyword detection
  - Folder structure detection
  - Multiple guideline support

---

## Phase 4: Skills Creation ✅ COMPLETED

### 4.1 Setup Skills
- [x] `SKILL_setup-project.md` - Project initialization
- [x] `SKILL_validate-setup.md` - Setup validation (to be created)

### 4.2 Analysis Skills
- [x] `SKILL_meta-analysis.md` - Meta-analysis workflow
- [x] `SKILL_test-selection.md` - Statistical test selection

### 4.3 Writing Skills
- [x] `SKILL_avoid-ai-formulations.md` - Natural writing strategies

### 4.4 Additional Skills (To Be Created)
- [ ] `SKILL_forest-plot.md` - Forest plot creation
- [ ] `SKILL_sensitivity-analysis.md` - Sensitivity analyses
- [ ] `SKILL_publication-bias.md` - Publication bias assessment
- [ ] `SKILL_bayesian-analysis.md` - Bayesian analysis
- [ ] `SKILL_prisma-checklist.md` - PRISMA compliance check
- [ ] `SKILL_strobe-checklist.md` - STROBE compliance check
- [ ] `SKILL_consort-checklist.md` - CONSORT compliance check
- [ ] `SKILL_grade-assessment.md` - GRADE assessment
- [ ] `SKILL_manuscript-structure.md` - Manuscript structuring
- [ ] `SKILL_swiss-cheese.md` - Verification protocol
- [ ] `SKILL_ai-detection.md` - AI writing detection
- [ ] `SKILL_analysis-pipeline.md` - Complete analysis pipeline
- [ ] `SKILL_data-cleaning.md` - Data cleaning workflow

---

## Phase 5: Learning Loop Integration ✅ COMPLETED

### 5.1 Core Integration
- [x] `learning_integration.py` - Learning logger module
  - Task logging
  - Pattern detection
  - Success/failure tracking
  - User feedback integration

### 5.2 Integration Points
- [x] Setup tools integration (ready for implementation)
- [x] Statistical tools integration (ready for implementation)
- [x] Writing tools integration (ready for implementation)
- [x] Skills integration (ready for implementation)

### 5.3 Positive Reinforcement
- [x] Success pattern tracking
- [x] Error pattern tracking
- [x] User preference learning
- [x] Automatic adaptation mechanism

---

## Phase 6: Documentation ✅ COMPLETED

### 6.1 Migration Documentation
- [x] `MIGRATION_GUIDE.md` - Complete migration guide (in `30_system/docs/`)
- [x] `.cursor/rules/README.md` - Rules directory overview
- [x] Updated `README.md` - Project overview with new structure
- [x] Updated `.ai/rules.md` - Quick reference with new structure

### 6.2 Workflow Documentation
- [x] `WORKFLOW_CURSOR_MIGRATION.md` - This document (in `30_system/docs/`)

---

## Phase 7: Remaining Domain Rules Migration 🔄 IN PROGRESS

### 7.1 Statistics Rules
- [ ] `statistics.mdc` ← `02_statistics.md`
  - Comprehensive statistical rules
  - Meta-analysis rules
  - Hypothesis testing rules
  - Error types (Type 1, 2, M, S)

### 7.2 Writing Rules
- [ ] `scientific-writing.mdc` ← `03_scientific_writing.md`
  - PRISMA compliance
  - GRADE assessment
  - Statistical reporting standards

### 7.3 Visualization Rules
- [x] `visualization.mdc` ← `04_visualization.md`

### 7.4 Verification Rules
- [x] `verification.mdc` ← `05_verification.md`

### 7.5 Study Types Rules
- [x] `study-types.mdc` ← `06_study_types.md`

### 7.6 Project Structure Rules
- [ ] `project-structure.mdc` ← `07_project_structure.md`
  - Folder structure standards
  - File naming conventions

### 7.7 R Programming Rules
- [x] `coding-standards-r.mdc` ← `01_general_rules.md` + `11_r_programming.md` (summary)
- [x] `SKILL_r-statistics.md` — full 11-step workflow (procedural)

### 7.8 Machine Learning Rules
- [ ] `machine-learning.mdc` ← `12_machine_learning.md`
  - Data leakage prevention
  - Model validation
  - TRIPOD+AI compliance

### 7.9 Workflow Rules
- [ ] `workflow-optimization.mdc` ← `09_workflow_optimization.md` (reference only)
- [x] `agentic-workflow-guardrails.mdc` ← `13_agentic_workflow.md` (partial)
- [x] `context-optimization.mdc` ← `16_cursor_optimization.md`
- [x] `learning-loop.mdc` + `learning-loop-triggers.mdc` ← `14_learning_loop.md`
- [x] `output-format-standards.mdc` ← `01_general_rules.md` § Output Format

---

## Phase 8: Additional Statistical Rules 📋 PLANNED

### 8.1 Advanced Methods
- [ ] `statistics-network-meta.mdc` - Network Meta-Analysis
- [ ] `statistics-ipd-meta.mdc` - Individual Patient Data Meta-Analysis
- [ ] `statistics-multiplicity.mdc` - Multiple Testing and Multiplicity
- [ ] `statistics-causal-inference.mdc` - Causal Inference Methods
- [ ] `statistics-bayesian.mdc` - Bayesian Analysis (detailed)

### 8.2 Methodology Rules
- [ ] `methodology-sample-size.mdc` - Sample Size Calculation
- [ ] `methodology-missing-data.mdc` - Missing Data Strategies
- [ ] `methodology-sensitivity.mdc` - Sensitivity Analysis Framework

---

## Phase 9: Testing and Validation 📋 PLANNED

### 9.1 Rules Testing
- [ ] Test glob pattern activation
- [ ] Test `alwaysApply: true` rules
- [ ] Test context management
- [ ] Verify no context overload

### 9.2 Skills Testing
- [ ] Test skill invocation (`@skill-name`)
- [ ] Test skill context loading
- [ ] Test skill chaining
- [ ] Verify skill effectiveness

### 9.3 Learning Loop Testing
- [ ] Test logging functionality
- [ ] Test pattern detection
- [ ] Test adaptation mechanism
- [ ] Verify positive reinforcement

---

## Usage Instructions

### For New Projects

1. **Rules activate automatically** based on file patterns
2. **Invoke Skills** when needed: `@setup-project`, `@meta-analysis`, etc.
3. **Reference 30_system/behavior_rules/** for detailed documentation

### For Existing Projects

1. **No changes required** - backward compatible
2. **Gradually adopt** new `.cursor/rules/` structure
3. **Use Skills** for new workflows

### For Development

1. **Follow this workflow** for adding new rules or skills
2. **Update documentation** when adding new components
3. **Test thoroughly** before marking as completed

---

## Status Summary

### ✅ Completed (Phases 1-6)
- Core structure
- Critical new rules
- All reporting guidelines
- Basic Skills
- Learning loop integration
- Documentation

### 🔄 In Progress (Phase 7)
- Domain rules migration

### 📋 Planned (Phases 8-9)
- Additional statistical rules
- Testing and validation

---

## Next Steps

1. **Continue Phase 7** - Migrate remaining domain rules
2. **Expand Skills** - Add more procedural instructions
3. **Implement Learning** - Integrate learning loop into actual tools
4. **Test Everything** - Comprehensive testing of all components

---

**Last Updated:** 2026-06-28  
**Maintained By:** Project maintainer

---

## Hygiene validation checklist (2026-06)

Run after major `.mdc` changes:

```powershell
python 40_operations/scripts/brain_health.py
python 40_operations/scripts/check_version_sync.py
python -m pytest 40_operations/tests/scripts/test_brain_health.py -q
```

Grep gates:

- [x] No `cursor.com/30_system` in active docs (archive exempt)
- [x] No stale `17 rule files` without context (use **58 `.mdc`**)
- [x] `writing-avoid-ai.mdc` core ≤ ~100 lines; extended in `writing-avoid-ai-extended.mdc`
- [x] `skills-auto-detect.mdc` core ≤ ~50 lines; extended in `skills-auto-detect-extended.mdc`
- [x] Files exist: `study-types.mdc`, `coding-standards-r.mdc`, `output-format-standards.mdc`, `learning-loop.mdc`, `LICENSE`
- [x] `target-trial-emulation` in skills-auto-detect shortcut table
- [x] Tier 0 token budget consistent (`~3000–3800` in `context-optimization.mdc`)
- [x] `skill_rerank` smoke logged (`.agent/task/skill_rerank_smoke_2026-06-28.md`)
- [x] No machine-brand names in active docs (hostname-conflict generic tooling)
- [ ] GitHub branch protection per `GITHUB_BRANCH_PROTECTION.md` (manual — repo Settings)

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[README]]
- [[22_pipeline_and_refinement]]
- [[09_workflow_optimization]]
- [[SKILL_strobe-checklist]]
- [[SKILL_ai-detection]]
