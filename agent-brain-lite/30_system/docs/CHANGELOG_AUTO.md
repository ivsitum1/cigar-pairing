# Auto Changelog (Git commits)

Updated automatically on each commit. For reconstructing changes use this file and `30_system/docs/CHANGELOG_AUTO.jsonl`.

---

## 2026-07-04 — feat(harness): NotebookLM Harness Memory v2 full cycle

- **NotebookLM v2:** Registered `f9554fae-…` as `harness-memory-v2`; 20-turn grill batch (seeded pending live MCP auth); gate GO; source expansion with arXiv VERIFIED (Self-Harness 2606.09498, HORMA 2606.11680, HIPIF 2606.10507, Agents-K1 2606.13669).
- **Docs:** `notebooklm_harness_v2_grill_prompts.md`, external ledger, executive + delta, `.agent/task/harness_v2_incorporation_backlog.md`.
- **Implementation:** UBIQUITOUS_LANGUAGE HIPIF/Agents-K1; `clusters/harness/intent.md`; SKILL_notebooklm-research-gate v1.3 refs; evals `self-harness-gate`, `memory-hierarchy`; K1 spike primary paper verified.
- **Runtime:** memory_hierarchy populated via fold-lemma; self_harness proposal_0003 (human gate iteration 3).

---

## 2026-07-01 — feat(machine): Machine v3 + NotebookLM follow-on

- **Faza 0:** brain_health PASS; pytest context_compress + ai_pattern_scan; NotebookLM auth OK; OKF-2 smoke log.
- **NotebookLM follow-on:** LOOP-4 `wiki_nested_loop.py`; MILE-3 `LAST_MILE_INTEGRATION_CHECKLIST.md`; OKF-1 `okf_wiki_export.py`; OKF-4 in SKILL_meta-analysis v1.4.
- **Machine v3 (US-30..40):** W28 GitHub scopes A/B; wiki concepts (Dify, awesome-claude-code); Agent-Reach matrix; headroom rollout in context-optimization; harness omo patterns.
- **Ledger:** `machine_digest_decisions_2026-W29.json`; `prd_machine_v3.json`. HUM-3 remains deferred_human.

---

## 2026-06-30 — feat(notebooklm): batch 2026-06 grill gate GO + Machine v2

- **NotebookLM:** pass1 (14×4) + pass2 (6×4) via CLI; all slugs GO; MAP docs, merged delta, source expansion JSON.
- **Machine v2:** spike docs (headroom, agent-reach, cowagent, oh-my-openagent, dify, crabbox); context_compress MVP; W27/W28 digest ledger.
- **Incorporation:** LOOP-1 in AGENT_AUTONOMY; OKF-2 long-context vs RAG in context-optimization; HUM-2 structural signals in ai_pattern_scan; HUM-3 paragraph rules in writing-avoid-ai v1.4; OKF-4 PDF trace; LOOP-3 wiki pipeline doc.

---

- **Files:** 


## 2026-01-16 `995d552` — Update writing_realtime_check.py and add STYLE_RULES_IMPLEMENTATION.md

- **Files:** .ai/STYLE_RULES_IMPLEMENTATION.md, .ai/writing_realtime_check.py


## 2026-01-16 `2feb268` — Initial commit: Optimized agent rules project

- **Files:** .gitignore, PYTEST_SETUP.md, index.md, WATCH_MODE_GUIDE.md, 30_system/behavior_rules/15_agent_roles-DESKTOP-8FP2N9R.md, 30_system/behavior_rules/CHANGELOG-DESKTOP-8FP2N9R.md, 30_system/behavior_rules/VERSION-DESKTOP-8FP2N9R.md, 30_system/behavior_rules/agents/08_academic_writing_specialist-DESKTOP-8FP2N9R.md, vim_angry_reviewer_integration_analysis.md


## 2026-01-16 `0fa9aa1` — Optimize project: Remove duplicates, add root .gitignore and README

- **Files:** GIT_SETUP.md, setup_git_and_push.ps1, setup_git_and_push.sh

```
Optimize project: Remove duplicates, add root .gitignore and README

- Removed duplicate files (DESKTOP-8FP2N9R versions)
- Removed temporary/analysis files
- Added root .gitignore
- Added comprehensive root index.md
- Verified portability
- Added Git setup 40_operations/scripts
```


## 2026-01-22 `8ccea58` — Version 3.2: Integrated Writing Workflow with AI Score Check and enhanced modules

- **Files:** 30_system/behavior_rules/11_r_programming.md, 30_system/behavior_rules/agents/03_code_quality_assurance.md, 30_system/behavior_rules/agents/04_medical_data_science/01_r_ecosystem.md, 30_system/behavior_rules/agents/04_medical_data_science/02_python_ecosystem.md, 30_system/behavior_rules/agents/04_medical_data_science/03_analysis_templates.md, 30_system/behavior_rules/agents/04_medical_data_science/04_visualization_standards.md, 30_system/behavior_rules/agents/04_medical_data_science/05_reproducibility_setup.md, 30_system/behavior_rules/agents/04_medical_data_science/06_research_gap_finder.md, 30_system/behavior_rules/agents/04_medical_data_science/07_code_quality_checklist.md, 30_system/behavior_rules/agents/04_medical_data_science_coder.md


## 2026-01-27 `fdf2e1a` — Migrate to Cursor rules structure and add Skills

- **Files:** .ai/rules.md, .cursor/rules/index.md, .cursor/rules/context-optimization.mdc, .cursor/rules/core-principles.mdc, .cursor/rules/reporting-auto-detect.mdc, .cursor/rules/reporting-care.mdc, .cursor/rules/reporting-cheers.mdc, .cursor/rules/reporting-consort.mdc, .cursor/rules/reporting-prisma.mdc, .cursor/rules/reporting-spirit.mdc, .cursor/rules/reporting-squire.mdc, .cursor/rules/reporting-stard.mdc, .cursor/rules/reporting-strobe.mdc, .cursor/rules/reporting-tripod-ai.mdc, .cursor/rules/statistics-test-selection.mdc, .cursor/rules/writing-avoid-ai.mdc, MIGRATION_GUIDE.md, index.md, 30_system/SKILLS/SKILL_avoid-ai-formulations.md, 30_system/SKILLS/SKILL_consort-checklist.md, 30_system/SKILLS/SKILL_forest-plot.md, 30_system/SKILLS/SKILL_meta-analysis.md, 30_system/SKILLS/SKILL_prisma-checklist.md, 30_system/SKILLS/SKILL_publication-bias.md, 30_system/SKILLS/SKILL_sensitivity-analysis.md, 30_system/SKILLS/SKILL_setup-project.md, 30_system/SKILLS/SKILL_strobe-checklist.md, 30_system/SKILLS/SKILL_test-selection.md, WORKFLOW_CURSOR_MIGRATION.md, 30_system/behavior_rules/tools/learning_integration.py

```
Migrate to Cursor rules structure and add Skills

- Add .cursor/rules/ directory with Cursor-native rules (.mdc files)
- Migrate core rules (core-principles, context-optimization)
- Add modern test selection framework (Welch/Permutation hierarchy)
- Add writing rules for avoiding AI formulations
- Add all reporting guidelines (STROBE, CONSORT, PRISMA, TRIPOD+AI, STARD, CARE, SPIRIT, SQUIRE, CHEERS)
- Add auto-detection system for reporting guidelines
- Create 30_system/SKILLS/ directory with procedural instructions
- Add 10 Skills for common workflows (setup, meta-analysis, test selection, checklists, etc.)
- Add learning loop integration module
- Update documentation (MIGRATION_GUIDE.md, WORKFLOW_CURSOR_MIGRATION.md)
- Update README files to reflect new structure
- Maintain backward compatibility with 30_system/behavior_rules/
```


## 2026-01-27 `b649e68` — Cleanup project structure (Opcija 1 - Konzervativna)

- **Files:** .ai/CONSOLIDATION_NOTES.md, .ai/FOLDER_STRUCTURE.md, .ai/INSTALLATION.md, .ai/LEGACY_NOTES.md, .ai/PROJECT_TEMPLATE.md, .ai/QUICK_START.md, .ai/index.md, .ai/STYLE_RULES_IMPLEMENTATION.md, .ai/SUMMARY.md, .ai/agent_activation_middleware.R, .ai/agent_auto_detection.R, .ai/agent_auto_detection.py, .ai/ai_detection_advanced.py, .ai/check_ai_score_fast.R, .ai/check_ai_score_fast.py, .ai/context.md, .ai/preferences.md, .ai/writing_auto_revise.R, .ai/writing_auto_revise.py, .ai/writing_feedback.R, .ai/writing_feedback.py, .ai/writing_realtime_check.R, .ai/writing_realtime_check.py, .ai/writing_workflow.R, .ai/writing_workflow.py, 90_archive/ARCHIVE/index.md, 90_archive/ARCHIVE/legacy_docs/CONSOLIDATION_NOTES.md, 90_archive/ARCHIVE/legacy_docs/FOLDER_STRUCTURE.md, 90_archive/ARCHIVE/legacy_docs/INSTALLATION.md, 90_archive/ARCHIVE/legacy_docs/LEGACY_NOTES.md (+28 more)

```
Cleanup project structure (Opcija 1 - Konzervativna)

- Create 90_archive/ARCHIVE/legacy_docs/ for legacy documentation
- Move legacy docs from .ai/ to 90_archive/ARCHIVE/ (10 files)
- Move writing tools to 30_system/behavior_rules/tools/writing/ (8 files)
- Move agent tools to 30_system/behavior_rules/tools/agents/ (3 files)
- Move AI detection tools to 30_system/behavior_rules/tools/ (3 files)
- Update all file paths in moved tools
- Mark migrated rules in 30_system/behavior_rules/ with migration notices
- Update documentation to reflect new structure
- Reduce .ai/ folder from 34 to 12 files (65% reduction)
- Maintain backward compatibility - no files deleted, only moved
- All tools now organized in 30_system/behavior_rules/tools/
```


## 2026-01-30 `6eba3c6` — Workflow upgrades: statistics alignment, publishing workflow, deduplication, re-evaluation

- **Files:** .cursor/rules/50_ml_mlops_standards.mdc, .cursor/rules/51_llm_agent_patterns.mdc, .cursor/rules/52_causal_inference.mdc, .cursor/rules/53_bayesian_workflow.mdc, .cursor/rules/60_windows_file_types.mdc, .cursor/rules/index.md, .cursor/rules/context-optimization.mdc, .cursor/rules/writing-avoid-ai.mdc, 30_system/SKILLS/SKILL_bayesian-workflow.md, 30_system/SKILLS/SKILL_target-trial-emulation.md, 30_system/behavior_rules/02_statistics.md, 30_system/behavior_rules/03_scientific_writing.md, 30_system/behavior_rules/05_verification.md, 30_system/behavior_rules/07_project_structure.md, 30_system/behavior_rules/09_workflow_optimization.md, 30_system/behavior_rules/12_machine_learning.md, 30_system/behavior_rules/18_ml_production.md, 30_system/behavior_rules/19_llm_development.md, 30_system/behavior_rules/20_modern_causal_methods.md, 30_system/behavior_rules/21_publishing_workflow.md, 30_system/behavior_rules/README-DESKTOP-8FP2N9R.md, 30_system/behavior_rules/index.md, 30_system/behavior_rules/agents/02_clinical_research_methodologist.md, 30_system/behavior_rules/agents/04_medical_data_science/03_analysis_templates.md, 30_system/behavior_rules/agents/04_medical_data_science/05_reproducibility_setup.md, 30_system/behavior_rules/agents/05_prompt_engineering_specialist.md, 30_system/behavior_rules/agents/07_statistical_analysis_expert.md, push_to_github.ps1, push_to_github.sh, 20_knowledge/reference_library/statistics/Global_Medical_Statistics_Discovery_Report.md (+3 more)

```
Workflow upgrades: statistics alignment, publishing workflow, deduplication, re-evaluation

- Statistics: check_descriptive (no Shapiro-based test choice); Welch/permutation/Yuen hierarchy in 02, agents, templates, Workflow 2
- References: writing-avoid-ai -> 03_scientific_writing, 10_ai_writing_plagiarism; .cursor README
- Publishing: Workflow 8 + 21_publishing_workflow.md, journal_guidelines placeholder, 07 structure
- Dedup: Workflow 6 (Search String) content under its own header; 02 vs statistics-test-selection clarified
- Evaluation: Workflow Evaluation (Post-Upgrade) in 09; scores 8/8/7, overall 7.5/10
- Git: installed via winget for agent terminal access
```


## 2026-01-30 `1c18876` — Remove temporary push 40_operations/scripts

- **Files:** push_to_github.ps1, push_to_github.sh


## 2026-02-01 `e22146e` — Add manuscript structure rules, skill, and reference (IMRaD/CARS)

- **Files:** .ai/rules_reference.md, .cursor/rules/index.md, .cursor/rules/writing-avoid-ai.mdc, .cursor/rules/writing-manuscript-structure.mdc, 30_system/SKILLS/SKILL_manuscript-structure.md, 20_knowledge/reference_library/writing/manuscript_tips_checklist.md


## 2026-02-01 `5071f24` — Update bayesian workflow, target-trial emulation, ML production, LLM development

- **Files:** 30_system/SKILLS/SKILL_bayesian-workflow.md, 30_system/SKILLS/SKILL_target-trial-emulation.md, 30_system/behavior_rules/18_ml_production.md, 30_system/behavior_rules/19_llm_development.md


## 2026-02-05 `b6a1546` — Agent-subagent system, token budget, Vancouver citations

- **Files:** .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/index.md, .cursor/rules/context-optimization.mdc, .cursor/rules/core-principles.mdc, .cursor/rules/writing-avoid-ai.mdc, .cursor/rules/writing-manuscript-structure.mdc, 30_system/behavior_rules/15_agent_roles.md, 30_system/behavior_rules/15b_agent_subagent_system.md, 30_system/behavior_rules/agents/08_academic_writing_specialist.md

```
Agent-subagent system, token budget, Vancouver citations

- Add Orchestrator rule (00_orchestrator_agent.mdc): classify, delegate, output hints
- Add 15b_agent_subagent_system.md (architecture)
- Trim core-principles and context-optimization; single Tier 2 list, token budget
- Tighten writing globs (drop **/*.md), add 15_agent_roles 'do not load' note
- Vancouver style in Writer: [n] order, before period, reference list; 08 + writing-manuscript-structure
```


## 2026-02-05 `196b6fb` — Update CHANGELOG.md with version tracking and assistant learning enhancements

- **Files:** 30_system/behavior_rules/CHANGELOG.md

```
Update CHANGELOG.md with version tracking and assistant learning enhancements

- Added version tracking and changelog system
- Introduced assistant learning log for AI self-improvement
- Added scripts for version tracking and assistant learning
- Enhanced documentation to include version tracking details
- Updated ML production and LLM development rules in documentation
```


## 2026-02-08 `61676e0` — Enhance rules for manuscript writing and project initiation

- **Files:** .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/core-principles.mdc, .cursor/rules/writing-manuscript-structure.mdc, 30_system/behavior_rules/01_general_rules.md, 30_system/behavior_rules/agents/01_clinical_decision_support.md, 30_system/behavior_rules/agents/08_academic_writing_specialist.md

```
Enhance rules for manuscript writing and project initiation

- Added guidelines for creating a roadmap when starting new projects with freshly copied agent rules.
- Emphasized the importance of using user-specific study details in manuscript writing, prohibiting the substitution of example content.
- Introduced explicit instructions on stating uncertainty and avoiding hallucinations in factual claims.
```


## 2026-02-08 `d9d49cc` — Remove obsolete documentation and 40_operations/scripts

- **Files:** .ai/index.md, .ai/rules.md, .ai/setup_learning.py, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/index.md, .cursor/rules/context-optimization.mdc, .cursor/rules/core-principles.mdc, .cursor/rules/reporting-auto-detect.mdc, .cursor/rules/skills-auto-detect.mdc, .cursor/rules/statistics-test-selection.mdc, CLEANUP_SUMMARY.md, GIT_SETUP.md, MIGRATION_GUIDE.md, 40_operations/R/00_paths.R, 40_operations/R/index.md, 40_operations/R/validation/self_assessment.R, 40_operations/R/validation/swiss_cheese_validation.R, index.md, 30_system/SKILLS/SKILL_ai-detection.md, 30_system/SKILLS/SKILL_avoid-ai-formulations.md, 30_system/SKILLS/SKILL_bayesian-workflow.md, 30_system/SKILLS/SKILL_consort-checklist.md, 30_system/SKILLS/SKILL_forest-plot.md, 30_system/SKILLS/SKILL_grade-assessment.md, 30_system/SKILLS/SKILL_manuscript-structure.md, 30_system/SKILLS/SKILL_meta-analysis.md, 30_system/SKILLS/SKILL_prisma-checklist.md, 30_system/SKILLS/SKILL_publication-bias.md, 30_system/SKILLS/SKILL_sensitivity-analysis.md, 30_system/SKILLS/SKILL_setup-project.md (+37 more)

```
Remove obsolete documentation and 40_operations/scripts

- Deleted CLEANUP_SUMMARY.md, GIT_SETUP.md, and MIGRATION_GUIDE.md as part of project restructuring.
- Removed setup scripts for Git initialization (setup_git_and_push.ps1 and setup_git_and_push.sh) and test watch scripts (run_tests_watch.bat and run_tests_watch.sh).
- Updated README.md to reflect changes in documentation structure and removed references to deleted files.
- Ensured all documentation is now centralized in the 30_system/docs/ directory for better organization.
```


## 2026-02-09 `d12ddb7` — Refine R and Python usage documentation for clarity and organization

- **Files:** 40_operations/R/index.md, index.md, 30_system/behavior_rules/01_general_rules.md, 30_system/behavior_rules/tools/README_tools.md, 30_system/behavior_rules/tools/project_check_page.py, 30_system/docs/EXISTING_ARCHITECTURE.md, 30_system/docs/PROJECT_CHECK.md

```
Refine R and Python usage documentation for clarity and organization

- Updated README.md and 40_operations/R/README.md to clarify the scope of R scripts, emphasizing their use for statistics, hypothesis testing, simulation, modeling, and validation.
- Specified that Python is used for writing tools and automation, with all relevant R scripts organized under the 40_operations/R/ directory.
- Enhanced documentation in 30_system/behavior_rules/01_general_rules.md to differentiate R and Python roles in the project.
- Added details about the new project_check_page.py tool in 30_system/behavior_rules/tools/README_tools.md, including usage instructions and Slack integration.
- Revised EXISTING_ARCHITECTURE.md to accurately reflect the current structure and purpose of R and Python scripts.
```


## 2026-02-10 `ad02166` — Add document conversion: Word/Excel <-> txt/md scripts and SKILL_document-conversion

- **Files:** .cursor/rules/skills-auto-detect.mdc, 30_system/SKILLS/SKILL_document-conversion.md, 40_operations/scripts/document_conversion/index.md, 40_operations/scripts/document_conversion/convert_documents.py, 40_operations/scripts/document_conversion/requirements.txt

```
Add document conversion: Word/Excel <-> txt/md scripts and SKILL_document-conversion

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-02-12 `d11d314` — Enhance behavior rules and documentation for AI agents

- **Files:** .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/index.md, .cursor/rules/context-optimization.mdc, .cursor/rules/skills-auto-detect.mdc, 90_archive/ARCHIVE/legacy_docs/README-DESKTOP-8FP2N9R.md, index.md, 30_system/SKILLS/SKILL_figure-pipeline.md, 30_system/behavior_rules/05_verification.md, 30_system/behavior_rules/09_workflow_optimization.md, 30_system/behavior_rules/15_agent_roles.md, 30_system/behavior_rules/15b_agent_subagent_system.md, 30_system/behavior_rules/16_cursor_optimization.md, 30_system/behavior_rules/17_context_optimization.md, 30_system/behavior_rules/22_pipeline_and_refinement.md, 30_system/behavior_rules/23_figure_visualization_pipeline.md, 30_system/behavior_rules/CHANGELOG.md, 30_system/behavior_rules/README-DESKTOP-8FP2N9R.md, 30_system/behavior_rules/index.md, 30_system/behavior_rules/VERSION.md, 30_system/behavior_rules/agents/05_prompt_engineering_specialist.md, 30_system/docs/CLEANUP_SUMMARY.md, 30_system/docs/EXISTING_ARCHITECTURE.md, 30_system/docs/MIGRATION_GUIDE.md, 30_system/docs/WORKFLOW_CURSOR_MIGRATION.md

```
Enhance behavior rules and documentation for AI agents

- Updated README.md to reflect the addition of 19+ behavior rule files and clarified the organization of procedural instructions in 30_system/SKILLS/.
- Enhanced the Orchestrator agent's documentation to include predefined pipelines for full workflows, referencing new files `22_pipeline_and_refinement.md` and `23_figure_visualization_pipeline.md`.
- Added sections on predefined pipelines and the REFINE phase in multiple rule files, ensuring clarity on workflow execution and critical output validation.
- Removed the obsolete `17_context_optimization.md`, consolidating its content into `.cursor/rules/context-optimization.mdc` for improved organization and accessibility.
- Updated CHANGELOG.md to document the addition of new pipelines and the removal of outdated files.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-02-15 `b0f2d5b` — fix: pre-commit skip 40_operations/tests/ for setwd/subset; exclude Pr(>F) from T/F check

- **Files:** .ai/templates.R, .cursor/errors/error_log.jsonl, .cursor/mcp.json, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/99_error_memory.mdc, .cursor/rules/context-optimization.mdc, .cursor/rules/reporting-auto-detect.mdc, .cursor/rules/visualization.mdc, .cursor/40_operations/scripts/error_ops.py, 90_archive/ARCHIVE/index.md, 90_archive/ARCHIVE/30_system/behavior_rules/index.md, 40_operations/R/shared/check_assumptions.R, 40_operations/R/shared/reproducibility.R, 40_operations/R/shared/theme_publication.R, 40_operations/R/validation/rubrics/code_rubric.R, 40_operations/R/validation/rubrics/load_rubrics.R, 40_operations/R/validation/rubrics/methodology_rubric.R, 40_operations/R/validation/rubrics/statistics_rubric.R, 40_operations/R/validation/rubrics/writing_rubric.R, 40_operations/R/validation/self_assessment.R, 30_system/behavior_rules/index.md, 30_system/behavior_rules/agents/05_prompt_engineering_specialist.md, 30_system/behavior_rules/tools/learning_integration.py, 30_system/behavior_rules/tools/learning_loop.py, 30_system/docs/AGENT_RULES_V2_INIT.md, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 30_system/docs/CHANGELOG_AUTO_README.md, 30_system/docs/MCP_INSTALL.md, 30_system/docs/MIGRATION_ARCHIVE.md (+8 more)

```
fix: pre-commit skip 40_operations/tests/ for setwd/subset; exclude Pr(>F) from T/F check

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-01 `63fb00c` — Enhance agent functionality and documentation

- **Files:** .agent/MEMORY.md, .agent/README.md, .agent/SOPs/README.md, .agent/handoff_log.jsonl, .agent/system/.gitkeep, .agent/system/README.md, .agent/task/.gitkeep, .cursor/mcp.json, .cursor/mcp_servers/handoff_server.py, .cursor/mcp_servers/requirements.txt, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/context-optimization.mdc, .cursor/rules/core-principles.mdc, .cursor/rules/harness_tdd.mdc, .cursor/rules/pipelines-summary.mdc, .cursor/rules/reporting-auto-detect.mdc, .cursor/rules/skills-auto-detect.mdc, .cursor/rules/writing-avoid-ai.mdc, .cursor/rules/writing-manuscript-structure.mdc, .cursor/scripts/error_to_learning_bridge.py, .cursor/scripts/handoff_log.py, 04_documentation/context/commit.md, 04_documentation/context/log.md, 04_documentation/context/main.md, SKILLS/SKILL_swiss-cheese.md, behavior_rules/reference/classification_hints.md, behavior_rules/reference/skill_task_mapping.md, behavior_rules/tools/agents/agent_auto_detection.py, docs/AUDIT_REPORT.md, docs/BRAIN_AND_PROJECT.md (+46 more)

```
Enhance agent functionality and documentation

- Updated `.cursor/mcp.json` to introduce a new "handoff" command for logging handoffs between subagents and refined the "pdf" command for text extraction from PDFs.
- Revised `.cursor/rules/00_orchestrator_agent.mdc` to clarify delegation instructions and added a new section on pipeline triggers for improved workflow management.
- Improved context optimization rules in `.cursor/rules/context-optimization.mdc`, including updates to the tier system and overload protocols.
- Enhanced various writing rules to specify file globs for manuscript structure and AI avoidance, ensuring better adherence to guidelines.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-01 `84bf44b` — Enhance agent functionality and documentation

- **Files:** .agent/README.md, .cursor/mcp.json, .cursor/mcp_servers/handoff_server.py, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/50_ml_mlops_standards.mdc, .cursor/rules/51_llm_agent_patterns.mdc, .cursor/rules/60_windows_file_types.mdc, .cursor/rules/context-optimization.mdc, .cursor/rules/core-principles.mdc, .cursor/rules/discovery-pipeline.mdc, .cursor/rules/general-rules.mdc, .cursor/rules/harness_tdd.mdc, .cursor/rules/pipelines-summary.mdc, .cursor/rules/statistics-test-selection.mdc, .cursor/rules/verification.mdc, .cursor/rules/visualization.mdc, SKILLS/SKILL_figure-pipeline.md, SKILLS/SKILL_manuscript-structure.md, SKILLS/SKILL_swiss-cheese.md, behavior_rules/15b_agent_subagent_system.md, behavior_rules/22_pipeline_and_refinement.md, behavior_rules/23_figure_visualization_pipeline.md, behavior_rules/agents/04_medical_data_science/06_research_gap_finder.md, behavior_rules/reference/classification_hints.md, behavior_rules/reference/skill_task_mapping.md, behavior_rules/tools/AI_PLAGIARISM_CHECKER_ANALYSIS.md, behavior_rules/tools/IMPROVEMENTS_EXAMPLES.md, behavior_rules/tools/agents/agent_auto_detection.py, docs/AGENT_RULES_V2_INIT.md, docs/AUDIT_REPORT.md (+20 more)

```
Enhance agent functionality and documentation

- Updated `.agent/README.md` to clarify project structure and context for agent-rules.
- Refined `.cursor/mcp.json` to improve the description of the "handoff" command, adding details for low-confidence classification detection.
- Enhanced `.cursor/mcp_servers/handoff_server.py` to include a new `detect_agent` tool for identifying subagents based on user prompts and context files.
- Revised `.cursor/rules/00_orchestrator_agent.mdc` and other rule files to improve clarity on task classification and pipeline execution, including updates to keywords and conflict resolution strategies.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-01 `81a161e` — Update documentation and refine agent rules

- **Files:** .agent/README.md, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/51_llm_agent_patterns.mdc, .cursor/rules/52_causal_inference.mdc

```
Update documentation and refine agent rules

- Revised `.agent/README.md` to enhance clarity on Swiss Cheese references and project structure.
- Updated `.cursor/rules/00_orchestrator_agent.mdc` to streamline references to verification processes.
- Adjusted globs in `.cursor/rules/51_llm_agent_patterns.mdc` and `.cursor/rules/52_causal_inference.mdc` for consistency and improved file matching.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-04 `e3a07b0` — Refine agent rules and documentation for improved clarity

- **Files:** .cursor/rules/index.md, .cursor/rules/agent-rules-readonly-when-referenced.mdc, 30_system/WORKSPACE_RECONSTRUCTION_GUIDE.md, workspace_reconstruction.json

```
Refine agent rules and documentation for improved clarity

- Updated `.agent/README.md` to enhance explanations of project structure and agent rules.
- Streamlined references in `.cursor/rules/00_orchestrator_agent.mdc` to improve understanding of verification processes.
- Adjusted file globs in `.cursor/rules/51_llm_agent_patterns.mdc` and `.cursor/rules/52_causal_inference.mdc` for better consistency and matching.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-09 `4b48b61` — Refine agent rules and documentation for improved clarity

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
Refine agent rules and documentation for improved clarity

- Updated `.agent/README.md` to enhance explanations of project structure and agent rules.
- Streamlined references in `.cursor/rules/00_orchestrator_agent.mdc` to improve understanding of verification processes.
- Adjusted file globs in `.cursor/rules/51_llm_agent_patterns.mdc` and `.cursor/rules/52_causal_inference.mdc` for better consistency and matching.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-09 `192f05c` — Comprehensive workspace quality improvement (score 78 -> 95/100)

- **Files:** .agent/SOPs/index.md, .agent/SOPs/TEMPLATE.md, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/50_ml_mlops_standards.mdc, .cursor/rules/51_llm_agent_patterns.mdc, .cursor/rules/52_causal_inference.mdc, .cursor/rules/53_bayesian_workflow.mdc, .cursor/rules/60_windows_file_types.mdc, .cursor/rules/99_error_memory.mdc, .cursor/rules/agent-rules-readonly-when-referenced.mdc, .cursor/rules/context-optimization.mdc, .cursor/rules/core-principles.mdc, .cursor/rules/discovery-pipeline.mdc, .cursor/rules/general-rules.mdc, .cursor/rules/harness_tdd.mdc, .cursor/rules/pipelines-summary.mdc, .cursor/rules/reporting-auto-detect.mdc, .cursor/rules/reporting-care.mdc, .cursor/rules/reporting-cheers.mdc, .cursor/rules/reporting-consort.mdc, .cursor/rules/reporting-prisma.mdc, .cursor/rules/reporting-spirit.mdc, .cursor/rules/reporting-squire.mdc, .cursor/rules/reporting-stard.mdc, .cursor/rules/reporting-strobe.mdc, .cursor/rules/reporting-tripod-ai.mdc, .cursor/rules/skills-auto-detect.mdc, .cursor/rules/statistics-test-selection.mdc, .cursor/rules/verification.mdc, .cursor/rules/visualization.mdc (+56 more)

```
Comprehensive workspace quality improvement (score 78 -> 95/100)

Phase 1: Fix broken cross-references, unify self-assessment dimensions,
correct CHEERS checklist items 20-22, add Pipeline 6, update Tier 0 kernel.

Phase 2: Add token budgets to all 27 .mdc files, standardize YAML metadata,
add CLINICAL/CODE error categories, fix ambiguous script paths.

Phase 3: Add requires_packages to SKILL_create-sop YAML front matter.

Phase 4: Extract shared templates (_templates.py), refactor brain_init and
memory_trim to eliminate duplication, add MCP dependency check to
brain_health, improve agent_auto_detection confidence scoring.

Phase 5: Create pytest test suite (37 tests across 6 modules) with
conftest fixtures and requirements-dev.txt.

Phase 6: Wire pre-commit hooks to run changelog + registry validation,
update run_all_checks to include pytest, add surprises.log support.

Made-with: Cursor
```


## 2026-03-11 `e8baae1` — Update writing and communication guidelines to enhance clarity and consistency

- **Files:** .cursor/rules/99_error_memory.mdc, .cursor/rules/general-rules.mdc, .cursor/rules/writing-avoid-ai.mdc, "Naj\304\215e\305\241\304\207i uzroci akutnog respiratornog zatajenja-1.md", 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
Update writing and communication guidelines to enhance clarity and consistency

- Added rules to avoid using em dashes, excessive parentheses, and semicolons in writing.
- Emphasized the importance of varying sentence length for all text produced.
- Revised structure guidelines to clarify the order of summary and detail in communication.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-14 `0ec2799` — Update requirements and enhance documentation for skill optimization

- **Files:** .cursor/rules/README.md, .cursor/rules/skill-optimization.mdc, .cursor/rules/skills-auto-detect.mdc, .cursor/rules/statistics-test-selection.mdc, R/exploratory/eda_flexplot.R, SKILLS/SKILL_case-report-series.md, SKILLS/SKILL_consort-checklist.md, SKILLS/SKILL_eda-flexplot.md, SKILLS/SKILL_literature-synthesis.md, SKILLS/SKILL_meta-analysis.md, SKILLS/SKILL_observational-studies.md, SKILLS/SKILL_prisma-checklist.md, SKILLS/SKILL_prospective-cohort.md, SKILLS/SKILL_rct-manuscript.md, SKILLS/SKILL_retrospective-cohort.md, SKILLS/SKILL_test-selection.md, SKILLS/SKILL_validate-setup.md, SKILLS/evals/OPTIMIZATION_RUN_ALL_SKILLS.md, SKILLS/evals/OPTIMIZATION_RUN_SUMMARY.md, SKILLS/evals/README.md, SKILLS/evals/RUN_ALL_RESULTS.txt, SKILLS/evals/SKILLS_evals_all.md, SKILLS/evals/ai-detection.json, SKILLS/evals/ai-detection_outputs.json, SKILLS/evals/avoid-ai-formulations.json, SKILLS/evals/avoid-ai-formulations_optimization_log.md, SKILLS/evals/avoid-ai-formulations_outputs.json, SKILLS/evals/bayesian-workflow.json, SKILLS/evals/bayesian-workflow_outputs.json, SKILLS/evals/consort-checklist.json (+66 more)

```
Update requirements and enhance documentation for skill optimization

- Added `openai` dependency to `requirements.txt` for skill evaluation runner.
- Introduced new section in `.cursor/rules/README.md` detailing the skill optimization process.
- Updated `.cursor/rules/skills-auto-detect.mdc` and `.cursor/rules/statistics-test-selection.mdc` to include new skills and clarify task mappings.
- Enhanced `SKILLS/registry.json` with new skills for exploratory data analysis and various cohort study types.
- Revised `SKILLS/SKILL_meta-analysis.md` to clarify the workflow for systematic reviews and meta-analyses.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-16 `bcf06f3` — Discovery Engine full product: Pipeline 7/7B, learning log discovery fields, classification, awakening script

- **Files:** .agent/MEMORY.md, .agent/index.md, .agent/dreaming/index.md, .agent/dreaming/config.md, .agent/dreaming/frameworks/.gitkeep, .agent/dreaming/run_logs/.gitkeep, .agent/dreaming/success_scores.json, .cursor/docs/AI_SEMANTIC_GATE.md, .cursor/docs/AWAKENING_RITUAL.md, .cursor/docs/CONTEXT_ISOLATION.md, .cursor/docs/DISCOVERY_ENGINE.md, .cursor/docs/EVIDENCE_CONSISTENCY_PROTOCOL.md, .cursor/docs/INDEX.md, .cursor/docs/MCP_AND_SKILLS_LAYERS.md, .cursor/docs/STATUS_AND_SESSION.md, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/context-optimization.mdc, .cursor/rules/skills-auto-detect.mdc, .cursor/skills/skill-builder.md, index.md, 30_system/behavior_rules/14_learning_loop.md, 30_system/behavior_rules/15_agent_roles.md, 30_system/behavior_rules/22_pipeline_and_refinement.md, 30_system/behavior_rules/23_figure_visualization_pipeline.md, 30_system/behavior_rules/24_discovery_pipeline.md, 30_system/behavior_rules/25_capability_registry.md, 30_system/behavior_rules/26_discovery_superpipeline.md, 30_system/behavior_rules/CHANGELOG.md, 30_system/behavior_rules/VERSION.md, 30_system/behavior_rules/reference/classification_hints.md (+10 more)

```
Discovery Engine full product: Pipeline 7/7B, learning log discovery fields, classification, awakening script

- run_pipeline: Pipeline 7 and 7B with orchestrator hints (24_ and 26_+25_)
- classification_hints: DISCOVERY_DRUG row and discovery triggers
- 22_pipeline_and_refinement: Pipeline 7 (7A/7B) subsection
- learning_integration: discovery_metadata in log_task and task_entry
- ingest_learning_block: pass pipeline_variant, hypothesis_pivots, etc. for drug_discovery
- learning_loop: task_type filter (drug_discovery), discovery_metrics, --task-type in CLI
- agent_auto_detection: discovery_engine triggers and DISCOVERY_DRUG mapping
- MCP_AND_SKILLS_LAYERS: Current vs Planned clarification for Discovery data layer
- DISCOVERY_ENGINE + 26_: .agent/dreams/ path and naming (dream_*, framework_*)
- 40_operations/scripts/awakening.py + AWAKENING_RITUAL.md + 40_operations/scripts/README
- .cursor/docs: INDEX, AWAKENING_RITUAL, DISCOVERY_ENGINE, MCP_AND_SKILLS_LAYERS

Made-with: Cursor
```


## 2026-03-18 `a5e1854` — Update core principles documentation for R/Python coding practices

- **Files:** .cursor/rules/core-principles.mdc, .cursor/rules/python_r_code_always.mdc, docs/CHANGELOG_AUTO.jsonl, docs/CHANGELOG_AUTO.md

```
Update core principles documentation for R/Python coding practices

- Translated the section on harness and TDD to Croatian, emphasizing reproducibility, paths, and explicitness in R/Python code.
- Adjusted references to related documentation for clarity.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-24 `7aa548c` — Enhance documentation and skills registry for agentic and scholarly workflows

- **Files:** .cursor/docs/INDEX.md, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/agentic_engineering_workflow.mdc, .cursor/rules/scholarly_workflow.mdc, .cursor/rules/skills-auto-detect.mdc, 30_system/SKILLS/SKILL_grill-me.md, 30_system/SKILLS/SKILL_prd-to-issues.md, 30_system/SKILLS/SKILL_ralph-loop.md, 30_system/SKILLS/SKILL_research-grill-me.md, 30_system/SKILLS/SKILL_research-spec-to-milestones.md, 30_system/SKILLS/SKILL_scholarly-iteration-loop.md, 30_system/SKILLS/SKILL_write-prd.md, 30_system/SKILLS/SKILL_write-research-spec.md, 30_system/SKILLS/registry.json, 30_system/behavior_rules/reference/skill_task_mapping.md, 30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md, 30_system/docs/SCHOLARLY_WORKFLOW.md, 30_system/docs/templates/prd.example.json, 30_system/docs/templates/prd.schema.json, 30_system/docs/templates/progress.template.txt, 30_system/docs/templates/research-spec.example.json, 30_system/docs/templates/research-spec.schema.json, 30_system/docs/templates/scholarly-progress.template.txt

```
Enhance documentation and skills registry for agentic and scholarly workflows

- Added new entries to `.cursor/docs/INDEX.md` for agentic engineering and scholarly workflow.
- Updated `.cursor/rules/00_orchestrator_agent.mdc` to include keywords and references for agentic and scholarly tasks.
- Enhanced `.cursor/rules/skills-auto-detect.mdc` with new skills related to engineering and scholarly processes.
- Expanded `30_system/SKILLS/registry.json` to incorporate new skills for PRD management and research specification.
- Revised `30_system/behavior_rules/reference/skill_task_mapping.md` to reflect updates in skill mappings for engineering and scholarly tasks.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-03-24 `5b80360` — docs: update auto changelog for recent workflow changes

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs: update auto changelog for recent workflow changes

Made-with: Cursor
```


## 2026-03-24 `7df02ee` — docs: sync auto changelog after commit hook

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs: sync auto changelog after commit hook

Made-with: Cursor
```


## 2026-03-24 `c467387` — docs: auto changelog follow-up entry

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs: auto changelog follow-up entry

Made-with: Cursor
```


## 2026-03-24 `f3b148d` — docs: include auto-changelog entries from pre-commit hook

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs: include auto-changelog entries from pre-commit hook

Made-with: Cursor
```


## 2026-03-24 `a4d4c34` — docs: changelog entry for f3b148d

- **Files:** docs/CHANGELOG_AUTO.jsonl, docs/CHANGELOG_AUTO.md

```
docs: changelog entry for f3b148d

Made-with: Cursor
```


## 2026-03-24 `7b92397` — chore: fold auto-changelog via post-commit amend; dedupe and amend-aware log

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 30_system/docs/CHANGELOG_AUTO_README.md, 40_operations/scripts/index.md, 40_operations/scripts/changelog_auto.py, 40_operations/scripts/post-commit-hook.ps1, 40_operations/scripts/post-commit-hook.sh, 40_operations/scripts/pre-commit-hook.ps1, 40_operations/scripts/pre-commit-hook.sh

```
chore: fold auto-changelog via post-commit amend; dedupe and amend-aware log

Made-with: Cursor
```


## 2026-03-24 `63a3c96` — chore: fold auto-changelog via post-commit amend; dedupe and amend-aware log

- **Files:** docs/CHANGELOG_AUTO.jsonl, docs/CHANGELOG_AUTO.md, docs/CHANGELOG_AUTO_README.md, scripts/README.md, scripts/changelog_auto.py, scripts/post-commit-hook.ps1, scripts/post-commit-hook.sh, scripts/pre-commit-hook.ps1, scripts/pre-commit-hook.sh

```
chore: fold auto-changelog via post-commit amend; dedupe and amend-aware log

Made-with: Cursor
```


## 2026-03-24 `2ecdf50` — fix: post-commit hook scripts — no git amend (avoids recursive hook loop)

- **Files:** 30_system/docs/CHANGELOG_AUTO_README.md, 40_operations/scripts/index.md, 40_operations/scripts/post-commit-hook.ps1, 40_operations/scripts/post-commit-hook.sh

```
fix: post-commit hook scripts — no git amend (avoids recursive hook loop)

Made-with: Cursor
```


## 2026-03-24 `1153f2e` — docs: auto changelog for hook fix commit

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs: auto changelog for hook fix commit

Made-with: Cursor
```


## 2026-03-24 `34f7bfc` — docs: auto changelog follow-up

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs: auto changelog follow-up

Made-with: Cursor
```


## 2026-03-24 `40ff8a1` — docs: auto changelog for 34f7bfc

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs: auto changelog for 34f7bfc

Made-with: Cursor
```


## 2026-03-30 `67a54a5` — chore: skills, changelog, scripts, honesty rules and .cursorrules

- **Files:** .cursor/rules/98_honesty_grounding_protocol.mdc, .cursor/rules/99_error_memory.mdc, .cursorrules, 30_system/04_documentation/context/log.md, 30_system/SKILLS/SKILL_ai-detection.md, 30_system/SKILLS/SKILL_avoid-ai-formulations.md, 30_system/SKILLS/SKILL_bayesian-workflow.md, 30_system/SKILLS/SKILL_case-report-series.md, 30_system/SKILLS/SKILL_consort-checklist.md, 30_system/SKILLS/SKILL_create-sop.md, 30_system/SKILLS/SKILL_document-conversion.md, 30_system/SKILLS/SKILL_eda-flexplot.md, 30_system/SKILLS/SKILL_figure-pipeline.md, 30_system/SKILLS/SKILL_forest-plot.md, 30_system/SKILLS/SKILL_grade-assessment.md, 30_system/SKILLS/SKILL_grill-me.md, 30_system/SKILLS/SKILL_literature-synthesis.md, 30_system/SKILLS/SKILL_manuscript-structure.md, 30_system/SKILLS/SKILL_meta-analysis.md, 30_system/SKILLS/SKILL_observational-studies.md, 30_system/SKILLS/SKILL_prd-to-issues.md, 30_system/SKILLS/SKILL_prisma-checklist.md, 30_system/SKILLS/SKILL_prospective-cohort.md, 30_system/SKILLS/SKILL_publication-bias.md, 30_system/SKILLS/SKILL_ralph-loop.md, 30_system/SKILLS/SKILL_rct-manuscript.md, 30_system/SKILLS/SKILL_research-grill-me.md, 30_system/SKILLS/SKILL_research-spec-to-milestones.md, 30_system/SKILLS/SKILL_retrospective-cohort.md, 30_system/SKILLS/SKILL_scholarly-iteration-loop.md (+13 more)

```
chore: skills, changelog, scripts, honesty rules and .cursorrules

- Update SKILLS front matter and tooling; changelog auto; pre-commit hooks

- Add 98_honesty_grounding_protocol, root .cursorrules, learning doc, skill_examples_tailor

- 99_error_memory and context log updates

Made-with: Cursor
```


## 2026-03-30 `9680fc6` — chore: skills, changelog, scripts, honesty rules and .cursorrules

- **Files:** .cursor/rules/98_honesty_grounding_protocol.mdc, .cursor/rules/99_error_memory.mdc, .cursorrules, 04_documentation/context/log.md, SKILLS/SKILL_ai-detection.md, SKILLS/SKILL_avoid-ai-formulations.md, SKILLS/SKILL_bayesian-workflow.md, SKILLS/SKILL_case-report-series.md, SKILLS/SKILL_consort-checklist.md, SKILLS/SKILL_create-sop.md, SKILLS/SKILL_document-conversion.md, SKILLS/SKILL_eda-flexplot.md, SKILLS/SKILL_figure-pipeline.md, SKILLS/SKILL_forest-plot.md, SKILLS/SKILL_grade-assessment.md, SKILLS/SKILL_grill-me.md, SKILLS/SKILL_literature-synthesis.md, SKILLS/SKILL_manuscript-structure.md, SKILLS/SKILL_meta-analysis.md, SKILLS/SKILL_observational-studies.md, SKILLS/SKILL_prd-to-issues.md, SKILLS/SKILL_prisma-checklist.md, SKILLS/SKILL_prospective-cohort.md, SKILLS/SKILL_publication-bias.md, SKILLS/SKILL_ralph-loop.md, SKILLS/SKILL_rct-manuscript.md, SKILLS/SKILL_research-grill-me.md, SKILLS/SKILL_research-spec-to-milestones.md, SKILLS/SKILL_retrospective-cohort.md, SKILLS/SKILL_scholarly-iteration-loop.md (+13 more)

```
chore: skills, changelog, scripts, honesty rules and .cursorrules

- Update SKILLS front matter and tooling; changelog auto; pre-commit hooks

- Add 98_honesty_grounding_protocol, root .cursorrules, learning doc, skill_examples_tailor

- 99_error_memory and context log updates

Made-with: Cursor
```


## 2026-03-31 `96e1c9d` — rules: manuscript output without internal repo paths or SKILL references

- **Files:** .cursor/rules/general-rules.mdc, .cursorrules, 30_system/behavior_rules/01_general_rules.md

```
rules: manuscript output without internal repo paths or SKILL references

Made-with: Cursor
```


## 2026-04-19 `091d06c` — Integrations: coding-discipline, writing meta-principles, SKILL guide; rules and docs sync

- **Files:** .Rprofile, .agent/MEMORY-hostname-conflict.md, .agent/README-hostname-conflict.md, .agent/SOPs/README-hostname-conflict.md, .cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md, .cursor/docs/COMMANDS_CHEAT_SHEET.md, .cursor/docs/INDEX.md, .cursor/docs/SKILL_CREATION_GUIDE.md, .cursor/rules/00_orchestrator_agent-hostname-conflict.mdc, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/50_ml_mlops_standards-hostname-conflict.mdc, .cursor/rules/51_llm_agent_patterns-hostname-conflict.mdc, .cursor/rules/52_causal_inference-hostname-conflict.mdc, .cursor/rules/53_bayesian_workflow-hostname-conflict.mdc, .cursor/rules/60_windows_file_types-hostname-conflict.mdc, .cursor/rules/99_error_memory-hostname-conflict.mdc, .cursor/rules/README-hostname-conflict.md, .cursor/rules/agent-rules-readonly-when-referenced-hostname-conflict.mdc, .cursor/rules/coding-discipline.mdc, .cursor/rules/context-optimization-hostname-conflict.mdc, .cursor/rules/core-principles-hostname-conflict.mdc, .cursor/rules/core-principles.mdc, .cursor/rules/discovery-pipeline-hostname-conflict.mdc, .cursor/rules/general-rules-hostname-conflict.mdc, .cursor/rules/general-rules.mdc, .cursor/rules/harness_tdd-hostname-conflict.mdc, .cursor/rules/pipelines-summary-hostname-conflict.mdc, .cursor/rules/reporting-auto-detect-hostname-conflict.mdc, .cursor/rules/reporting-care-hostname-conflict.mdc, .cursor/rules/reporting-cheers-hostname-conflict.mdc (+117 more)

```
Integrations: coding-discipline, writing meta-principles, SKILL guide; rules and docs sync

- Add .cursor/rules/coding-discipline.mdc (Karpathy principles layer)
- Extend writing-avoid-ai.mdc with Writing Meta-Principles section
- Add .cursor/docs/SKILL_CREATION_GUIDE.md (30_system/SKILLS/registry pipeline)
- Record updates in 30_system/behavior_rules/CHANGELOG.md [Unreleased]
- Sync behavior_rules, agents, orchestrator, core-principles, docs INDEX
- Add hostname-conflict rule/skill clones, analysis scaffolding, 40_operations/scripts
- Add rule maintenance and external integration behavior 30_system/docs
- Update CHANGELOG_AUTO, log.md, README, .gitignore; remove stray md file

Made-with: Cursor
```


## 2026-04-19 `c768aa8` — chore: sync CHANGELOG_AUTO after post-commit amend

- **Files:** docs/CHANGELOG_AUTO.jsonl, docs/CHANGELOG_AUTO.md

```
chore: sync CHANGELOG_AUTO after post-commit amend

Made-with: Cursor
```


## 2026-04-28 `dd37011` — Introduce strategic engineering intent scoring and shared language scaffold.

- **Files:** .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/54_strategic_engineering.mdc, .cursor/rules/agentic_engineering_workflow.mdc, .cursor/rules/coding-discipline.mdc, .cursor/rules/core-principles.mdc, .cursorrules, 30_system/UBIQUITOUS_LANGUAGE.md, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
Introduce strategic engineering intent scoring and shared language scaffold.

This adds a dedicated strategic engineering rule set, links it into orchestrator/workflow guidance, and switches routing from brittle keyword matching to score-based intent detection so Grill-me activates on natural user phrasing.

Made-with: Cursor
```


## 2026-04-30 `708db56` — feat: add autonomous memory learning loop and hook integration

- **Files:** .cursor/hooks.json, .cursor/hooks/memory_lifecycle.py, .cursor/mcp.json, .cursor/mcp_servers/memory_server.py, SKILLS/SKILL_ai-detection-hostname-conflict.md, SKILLS/SKILL_avoid-ai-formulations-hostname-conflict.md, SKILLS/SKILL_bayesian-workflow-hostname-conflict.md, SKILLS/SKILL_consort-checklist-hostname-conflict.md, SKILLS/SKILL_document-conversion-hostname-conflict.md, SKILLS/SKILL_figure-pipeline-hostname-conflict.md, SKILLS/SKILL_forest-plot-hostname-conflict.md, SKILLS/SKILL_grade-assessment-hostname-conflict.md, SKILLS/SKILL_manuscript-structure-hostname-conflict.md, SKILLS/SKILL_meta-analysis-hostname-conflict.md, SKILLS/SKILL_prisma-checklist-hostname-conflict.md, SKILLS/SKILL_publication-bias-hostname-conflict.md, SKILLS/SKILL_sensitivity-analysis-hostname-conflict.md, SKILLS/SKILL_setup-project-hostname-conflict.md, SKILLS/SKILL_strobe-checklist-hostname-conflict.md, SKILLS/SKILL_swiss-cheese-hostname-conflict.md, SKILLS/SKILL_target-trial-emulation-hostname-conflict.md, SKILLS/SKILL_test-selection-hostname-conflict.md, SKILLS/SKILL_validate-setup-hostname-conflict.md, docs/MCP_INSTALL.md, docs/MEMORY_SYSTEM.md, docs/SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md, memory_engine/__init__.py, memory_engine/compression.py, memory_engine/config.py, memory_engine/hooks.py (+20 more)

```
feat: add autonomous memory learning loop and hook integration

Implement always-on memory capture with lifecycle hooks, persistent retrieval APIs, self-evaluation telemetry, and a guarded learning loop that proposes/applies skill and rule improvements with audit trails.

Also remove legacy hostname-suffix skill duplicates and keep active canonical skills only.

Made-with: Cursor
```


## 2026-04-30 `89ab87e` — chore: sync pending rule and changelog updates

- **Files:** docs/CHANGELOG_AUTO.jsonl, docs/CHANGELOG_AUTO.md

```
chore: sync pending rule and changelog updates

Commit remaining tracked documentation and rule updates that were left unstaged after the memory-system integration commit, and include updated auto changelog entries.

Made-with: Cursor
```


## 2026-04-30 `manual` — autoresearch hybrid hardening: centralized memory signal, memory-first loop, and changelog enforcement

- **Files:** 40_operations/scripts/self_eval_learning_loop.py, 40_operations/scripts/changelog_auto.py, 30_system/docs/SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md, 40_operations/scripts/index.md, 30_system/docs/autoresearch_hybrid_spec.md
- **Source:** `agent_implementation`


## 2026-04-30 `3b5c28d` — feat: add memory-first autoresearch integration loop

- **Files:** .agent/task/templates/auditor_template.md, .agent/task/templates/critic_template.md, .agent/task/templates/executor_template.md, .agent/task/templates/proposer_template.md, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 30_system/docs/SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md, 30_system/docs/artifact_policy.md, 30_system/docs/autoresearch_hybrid_spec.md, 30_system/docs/autoresearch_metric_gate.md, 30_system/docs/autoresearch_orchestration_contract.md, 30_system/docs/report_template.md, 30_system/docs/run_manifest.md, 30_system/docs/schemas/experiment_result.schema.json, 40_operations/scripts/index.md, 40_operations/scripts/changelog_auto.py, 40_operations/scripts/generate_experiment_report.py, 40_operations/scripts/self_eval_learning_loop.py, 40_operations/scripts/validate_experiment_artifacts.py

```
feat: add memory-first autoresearch integration loop

Implement the hybrid autoresearch workflow with a centralized memory signal, deterministic accept/revert gates, resumable run artifacts, role handoff templates, and automatic changelog logging for agent-rules mutations.

Made-with: Cursor
```


## 2026-04-30 `56b53e3` — chore: sync auto changelog after integration commit

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
chore: sync auto changelog after integration commit

Capture the latest integration commit in the auto changelog so agent-rules changes remain fully traceable.

Made-with: Cursor
```


## 2026-05-04 `72ec29c` — feat: Karpathy-style knowledge_system (project_init, AGENT_SPEC, docs)

- **Files:** docs/BRAIN_AND_PROJECT.md, docs/KARPATHY_WIKI.md, scripts/_templates.py, scripts/project_init.py

```
feat: Karpathy-style knowledge_system (project_init, AGENT_SPEC, docs)

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-05 `129ffb6` — feat: scaffold agentic OS with Re-Act and wiki workflow

- **Files:** .cursorrules, 30_system/SKILLS/_template/SKILL_TEMPLATE.md, 30_system/claude.md, 30_system/context/memory.md, 30_system/context/soul.md, 30_system/context/user.md, 40_operations/logs/index.md, 10_projects/projects/index.md, 00_inbox/raw/index.md, 30_system/shared-brand/index.md, 20_knowledge/wiki/index.md, 20_knowledge/wiki/log.md

```
feat: scaffold agentic OS with Re-Act and wiki workflow

Add a practical Agentic OS foundation with context files, deterministic output structure, Re-Act execution rules, and a Karpathy-style markdown wiki ingestion system to improve continuity and reduce context rot.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-05 `d821a66` — feat: consolidate layout (30_system, 40_operations), rules sync, archive hostname-suffix variants

- **Files:** .agent/MEMORY-hostname-conflict.md, .agent/MEMORY.md, .agent/README-hostname-conflict.md, .agent/README.md, .agent/SOPs/README-hostname-conflict.md, .agent/SOPs/README.md, .agent/dreaming/README.md, .agent/handoff_log.jsonl, .agent/memory/hook_session.json, .agent/memory/memory.db, .agent/memory/raw_events.jsonl, .agent/memory/self_eval.jsonl, .agent/system/README.md, .agent/task/examples/new_statistics_task_example.md, .agent/task/learning_run_20260505_092704.json, .agent/task/templates/task_context_template.md, .ai/README.md, .ai/detect_study_type.py, .ai/rules.md, .ai/rules_reference.md, .ai/setup_learning.py, .ai/setup_project.py, .ai/setup_recovery.py, .ai/validate_setup.py, .claude/worktrees/strange-borg-b3266e, .cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md, .cursor/docs/AI_SEMANTIC_GATE.md, .cursor/docs/AWAKENING_RITUAL.md, .cursor/docs/COMMANDS_CHEAT_SHEET.md, .cursor/docs/CONTEXT_ISOLATION.md (+4493 more)

```
feat: consolidate layout (30_system, 40_operations), rules sync, archive hostname-suffix variants

Replaces prior local scaffold commit with full workspace state: migrated SKILLS/scripts/docs, memory hooks, wiki paths, and removal of duplicated *-hostname-conflict artifacts.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-05 `fa5d3bf` — docs(rules): canonical token budgets, parallel context policy, .cursor/docs path fix

- **Files:** .agent/dreaming/README.md, .agent/memory/raw_events.jsonl, .cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md, .cursor/docs/AI_SEMANTIC_GATE.md, .cursor/docs/COMMANDS_CHEAT_SHEET.md, .cursor/docs/DISCOVERY_ENGINE.md, .cursor/docs/EVIDENCE_CONSISTENCY_PROTOCOL.md, .cursor/docs/INDEX.md, .cursor/docs/SKILL_CREATION_GUIDE.md, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/agentic_engineering_workflow.mdc, .cursor/rules/context-optimization.mdc, .cursor/rules/skills-auto-detect.mdc, .obsidian/graph.json, 30_system/UBIQUITOUS_LANGUAGE.md, 30_system/WORKSPACE_RECONSTRUCTION_GUIDE.md, 30_system/behavior_rules/15b_agent_subagent_system.md, 30_system/behavior_rules/24_discovery_pipeline.md, 30_system/behavior_rules/25_capability_registry.md, 30_system/behavior_rules/26_discovery_superpipeline.md, 30_system/behavior_rules/CHANGELOG.md, 30_system/claude.md, 30_system/context/soul.md, 30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md, 30_system/docs/ALL_NOTES_INDEX.md, 30_system/docs/AUTOMATION_INDEX.md, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 30_system/docs/GRAPH_CONNECTIVITY_MAP.md, 30_system/docs/README.md (+2 more)

```
docs(rules): canonical token budgets, parallel context policy, .cursor/docs path fix

- context-optimization: Tier 0 table, warn threshold, parallelism for token savings

- orchestrator 1.5: remove duplicate token line; point to canonical budget; parallel default

- AGENT_AUTONOMY + cross-links: token economics, fixed .cursor/docs/* references repo-wide

- bulk replace .cursor/30_system/docs -> .cursor/docs (incl. indexes, behavior_rules, changelogs)

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-06 `dae977a` — chore(changelog): backfill JSONL, rewrite MD chronologically, --rewrite-md-from-jsonl

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 40_operations/scripts/changelog_auto.py

```
chore(changelog): backfill JSONL, rewrite MD chronologically, --rewrite-md-from-jsonl

- Fix post-commit path usage reflected in prior session; JSONL backfill + sorted CHANGELOG_AUTO.md

- changelog_auto.py: rebuild .md from JSONL with dedupe by commit hash

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-06 `bb371a5` — docs(changelog): record commit dae977a in CHANGELOG_AUTO

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs(changelog): record commit dae977a in CHANGELOG_AUTO

Co-authored-by: Cursor <cursoragent@cursor.com>
```

## 2026-05-06 `18dce28` — docs(changelog): SKIP_CHANGELOG env to skip post-commit hook

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 30_system/docs/CHANGELOG_AUTO_README.md, 40_operations/scripts/post-commit-hook.ps1, 40_operations/scripts/post-commit-hook.sh

```
docs(changelog): SKIP_CHANGELOG env to skip post-commit hook

Templates: post-commit-hook.sh/.ps1 and CHANGELOG_AUTO_README; local .git/hooks/post-commit synced.
Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-06 `3e8f935` — docs(changelog): tidy AUTO md/jsonl after tip log

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs(changelog): tidy AUTO md/jsonl after tip log

Co-authored-by: Cursor <cursoragent@cursor.com>
```

## 2026-05-06 `90904c0` — feat(ops): workspace QA, brain_audit paths, pytest suite, benchmarks

- **Files:** .agent/MEMORY.md, .cursor/hooks/memory_lifecycle.py, .cursor/mcp_servers/memory_server.py, .cursor/rules/00_orchestrator_agent.mdc, 20_knowledge/reference_library/tools/catalog_pdfs.py, 30_system/WORKSPACE_RECONSTRUCTION_GUIDE.md, 30_system/behavior_rules/tools/track_versions.py, 30_system/docs/AGENT_BENCHMARK_MANIFEST_EXAMPLE.json, 30_system/docs/AGENT_BENCHMARK_SCHEMA.md, 30_system/docs/AUTOMATION_INDEX.md, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 30_system/docs/GRILL_ME_INJECTION_HEURISTIC.md, 30_system/docs/MEMORY_SYSTEM.md, 30_system/docs/TRAJECTORY_EVAL_SPEC.md, 40_operations/scripts/brain_audit.py, 40_operations/scripts/brain_health.py, 40_operations/scripts/cursor_paths.py, 40_operations/scripts/generate_evals_from_skill.py, 40_operations/scripts/memory_hook.py, 40_operations/scripts/rag_eval_runner.py, 40_operations/scripts/reliability_eval_runner.py, 40_operations/scripts/run_agent_benchmark.py, 40_operations/scripts/self_eval_learning_loop.py, 40_operations/scripts/task_optimization_check.py, 40_operations/scripts/trajectory_eval_runner.py, 40_operations/scripts/workspace_inventory_audit.py, 40_operations/tests/behavior_rules/tools/test_check_ai_plagiarism.py, 40_operations/tests/behavior_rules/tools/test_track_versions.py, 40_operations/tests/conftest.py (+14 more)

```
feat(ops): workspace QA, brain_audit paths, pytest suite, benchmarks

- Add cursor_paths resolver and workspace_inventory_audit; fix brain_audit for .cursor/scripts
- Fix pytest REPO_ROOT conftest, pytest.ini testpaths, requirements-dev pins
- Fix memory_hook sys.path, memory hooks MCP/lifecycle, grill-me injection and tests
- track_versions and catalog_pdfs classification fixes; task_optimization_check wiki bug
- Agent benchmark runners and trajectory/RAG/reliability eval docs and scripts
- Orchestrator and reconstruction guide canonical .cursor/scripts paths

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-08 `7a1ef43` — feat(rules): migrate behavior-rule operations into active Cursor rules

- **Files:** .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/50_ml_mlops_standards.mdc, .cursor/rules/agentic-workflow-guardrails.mdc, .cursor/rules/pipeline-refinement.mdc, .cursor/rules/python_r_code_always.mdc, .cursor/rules/visualization.mdc, .cursor/rules/writing-avoid-ai.mdc, .cursor/skills/README.md, .cursor/skills/skill-builder.md, 30_system/SKILLS/SKILL_create-skill.md, 30_system/SKILLS/registry.json, 30_system/behavior_rules/04_visualization.md, 30_system/behavior_rules/11_r_programming.md, 30_system/behavior_rules/12_machine_learning.md, 30_system/behavior_rules/13_agentic_workflow.md, 30_system/behavior_rules/15_agent_roles.md, 30_system/behavior_rules/22_pipeline_and_refinement.md, 30_system/behavior_rules/23_figure_visualization_pipeline.md, 30_system/context/user.md, ARCHIVE/README.md, UBIQUITOUS_LANGUAGE.md

```
feat(rules): migrate behavior-rule operations into active Cursor rules

Promote operational guidance from behavior_rules into active .cursor/rules, align skills and registry, and complete context/glossary bridges so runtime behavior reflects the canonical workflow.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-08 `18a0b96` — docs: normalize Related Hubs and complete Obsidian graph links

- **Files:** .agent/README.md, .agent/SOPs/TEMPLATE.md, .agent/dreaming/README.md, .agent/dreaming/config.md, .agent/system/README.md, .agent/task/templates/auditor_template.md, .agent/task/templates/critic_template.md, .agent/task/templates/executor_template.md, .agent/task/templates/proposer_template.md, .ai/rules.md, .ai/rules_reference.md, .cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md, .cursor/docs/AI_SEMANTIC_GATE.md, .cursor/docs/AWAKENING_RITUAL.md, .cursor/docs/COMMANDS_CHEAT_SHEET.md, .cursor/docs/CONTEXT_ISOLATION.md, .cursor/docs/DISCOVERY_ENGINE.md, .cursor/docs/EVIDENCE_CONSISTENCY_PROTOCOL.md, .cursor/docs/MCP_AND_SKILLS_LAYERS.md, .cursor/docs/SKILL_CREATION_GUIDE.md, .cursor/docs/STATUS_AND_SESSION.md, .cursor/skills/README.md, 04_documentation/README.md, 10_projects/projects/README.md, 20_knowledge/reference_library/KNOWLEDGE_CATALOG.md, 20_knowledge/reference_library/README.md, 20_knowledge/reference_library/medicine/README.md, 20_knowledge/reference_library/medicine/textbooks/README.md, 20_knowledge/reference_library/opinions/README.md, 20_knowledge/reference_library/opinions/editorials_commentaries/README.md (+570 more)

```
docs: normalize Related Hubs and complete Obsidian graph links

- Add normalize_related_hubs.py for consistent Folder / All notes / Graph links

- Preserve context-specific Related Hubs bullets (e.g. SOPs, skill cluster indexes)

- Skip Graph map self-link; update GRAPH_CONNECTIVITY_MAP workflow and snapshot

- SKILLS_INDEX: functional units + pipeline bridges; blank line before main body

Connectivity (obsidian_connectivity_check): 3604 md files, 3546 connected, weak 0, orphan 0.

Co-authored-by: Cursor <cursoragent@cursor.com>
```

## Semantic graph (auto)

- [[Behavior rules hub]]
- [[Orchestrator - agent roles]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[VERSION]]
- [[README]]
- [[SKILL_ai-detection]]
- [[SKILL_setup-project]]
- [[09_workflow_optimization]]

## 2026-05-22 `5227a01` — feat(ocr): integrate PaddleOCR as priority PDF extraction path

- **Files:** .cursor/rules/skills-auto-detect.mdc, .gitignore, 30_system/SKILLS/SKILL_paddle-ocr.md, 30_system/SKILLS/registry.json, 30_system/docs/AUTOMATION_INDEX.md, 30_system/docs/BOOKS_RAG.md, 30_system/docs/REFERENCE_LIBRARY_AGENT_ACCESS.md, 40_operations/python/pdf_extraction/__init__.py, 40_operations/python/pdf_extraction/device.py, 40_operations/python/pdf_extraction/heuristics.py, 40_operations/python/pdf_extraction/paddle_ppstructure.py, 40_operations/requirements-ocr.txt, 40_operations/scripts/bootstrap_paddleocr_vendor.py, 40_operations/scripts/extract_pdf_library_to_md.py, 40_operations/scripts/extract_pdf_ocr.ps1, 40_operations/scripts/install_books_rag.py, 40_operations/scripts/install_paddle_ocr.ps1, 40_operations/scripts/install_paddle_ocr.py, 40_operations/scripts/link_ocr_venv_path.py, 40_operations/tests/pdf_extraction/test_heuristics.py, 40_operations/tests/pdf_extraction/test_paddle_smoke.py, pytest.ini

```
feat(ocr): integrate PaddleOCR as priority PDF extraction path

Add PP-StructureV3 wrapper, auto OCR fallback in extract_pdf_library_to_md,
vendor bootstrap from zip, Python 3.12 install scripts, paddle-ocr skill, and tests.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-22 `67eb357` — feat(books-rag): MCP server, index pipeline, hooks, and study-data docs

- **Files:** .cursor/docs/INDEX.md, .cursor/hooks.json, .cursor/hooks/books_rag_lifecycle.py, .cursor/mcp.json, .cursor/mcp_servers/books_rag_server.py, .cursor/mcp_servers/requirements.txt, .cursor/rules/books-rag.mdc, 30_system/behavior_rules/reference/skill_task_mapping.md, 30_system/docs/BOOKS_RAG_LOCAL_LLM.md, 30_system/docs/FOLDER_INDEX.md, 30_system/docs/MCP_INSTALL.md, 30_system/docs/RAG_VS_STUDY_DATA.md, 30_system/docs/indexes/40_operations_INDEX.md, 30_system/docs/indexes/_agent_INDEX.md, 30_system/docs/indexes/study_data_INDEX.md, 30_system/docs/study_data/CODEBOOK_MIGRATION.md, 30_system/docs/study_data/README.md, 30_system/docs/study_data/examples/METAANALIZA_CODEBOOK_MIGRATION.md, 40_operations/docs/CODEBOOK_MIGRATION.md, 40_operations/scripts/books_rag_eval.py, 40_operations/scripts/books_rag_index_batch.ps1, 40_operations/scripts/books_rag_index_until_complete.py, 40_operations/scripts/build_books_rag_index.py, 40_operations/scripts/link_books_md_hubs.py, 40_operations/scripts/prepare_study_codebook.py, 40_operations/templates/codebooks/README.md, 40_operations/tests/books_rag/test_chunker.py, 40_operations/tests/books_rag/test_context_policy.py, 40_operations/tests/books_rag/test_hook.py, 40_operations/tests/books_rag/test_hybrid.py (+21 more)

```
feat(books-rag): MCP server, index pipeline, hooks, and study-data docs

Add books_rag package, build/index scripts, lifecycle hook, and RAG vs codebook separation docs.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-22 `d007806` — chore(wiki): refresh books_md corpus and add LaTeX journal skills

- **Files:** .agent/MEMORY.md, .agent/task/METAANALIZA_CODEBOOK_MIGRATION.md, .cursor/mcp_servers/latex/latex_server.py, .cursor/mcp_servers/latex/pyproject.toml, .cursor/mcp_servers/latex/templates/article_template.tex, .cursor/mcp_servers/latex/templates/beamer_template.tex, .cursor/mcp_servers/latex/templates/report_template.tex, 20_knowledge/wiki/concepts/Journal cover design skill.md, 20_knowledge/wiki/concepts/Journal production skill.md, 20_knowledge/wiki/concepts/LaTeX and journal production stack.md, 20_knowledge/wiki/concepts/LaTeX compile skill.md, 20_knowledge/wiki/concepts/LaTeX document skill.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part01.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part02.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part03.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part04.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part05.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part06.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part07.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part08.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part09.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part10.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part11.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part12.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part13.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part14.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part15.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part16.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part17.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part18.md (+2067 more)

```
chore(wiki): refresh books_md corpus and add LaTeX journal skills

Update extracted reference-library markdown parts, journal/LaTeX skills and evals, LaTeX MCP server, and related wiki concepts. Excludes agent memory, Obsidian UI state, vendor PaddleOCR tree, and paths blocked by Windows MAX_PATH.

Co-authored-by: Cursor <cursoragent@cursor.com>
```

## 2026-05-26 `6c6796af` — feat(brain): remediation, Obsidian wiki pack, books corpus, and PDF/OCR tooling

- **Files:** .agent/MEMORY.md, .agents/skills/defuddle/SKILL.md, .agents/skills/json-canvas/SKILL.md, .agents/skills/json-canvas/references/EXAMPLES.md, .agents/skills/obsidian-bases/SKILL.md, .agents/skills/obsidian-bases/references/FUNCTIONS_REFERENCE.md, .agents/skills/obsidian-cli/SKILL.md, .agents/skills/obsidian-markdown/SKILL.md, .agents/skills/obsidian-markdown/references/CALLOUTS.md, .agents/skills/obsidian-markdown/references/EMBEDS.md, .agents/skills/obsidian-markdown/references/PROPERTIES.md, .cursor/docs/INDEX.md, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/50_ml_mlops_standards.mdc, .cursor/rules/README.md, .cursor/rules/books-rag.mdc, .cursor/rules/obsidian-wiki-upstream.mdc, .cursor/rules/statistics-test-selection.mdc, .env.example, .gitignore, .markdownlint.json, .obsidian/graph.json, .obsidian/graph.json.bak-2026-05-22, .obsidian/workspace.json, .pre-commit-config.yaml, 20_knowledge/reference_library/README.md, 20_knowledge/reference_library/coding/books/.gitkeep, 20_knowledge/wiki/.manifest.json, 20_knowledge/wiki/_meta/taxonomy.md, 20_knowledge/wiki/_raw/README.md (+12863 more)

```
feat(brain): remediation, Obsidian wiki pack, books corpus, and PDF/OCR tooling

Brain health strict mode, QA scripts, pre-commit, and skill eval seeds. Add Obsidian
upstream skills, wiki concepts, and gitignore for secrets and local memory shards.
Refresh books_md/pdf sources, Paddle migration tooling, and brain_assist rerank helpers.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-27 `a971eb3a` — feat(trajectory-rl): instrument traces, composite reward, and skill learning bridge

- **Files:** .cursor/hooks.json, .cursor/hooks/trajectory_lifecycle.py, 20_knowledge/wiki/concepts/Skill gap pipeline.md, 20_knowledge/wiki/concepts/Trajectory reinforcement learning.md, 30_system/behavior_rules/14_learning_loop.md, 30_system/docs/AGENT_BENCHMARK_RL_DEMO.json, 30_system/docs/AUTOMATION_INDEX.md, 30_system/docs/DEEP_LEARNING_POLICY.md, 30_system/docs/SKILL_GAP_PIPELINE.md, 30_system/docs/TRAJECTORY_EMIT_PROTOCOL.md, 30_system/docs/TRAJECTORY_RL_POLICY.md, 30_system/docs/autoresearch_metric_gate.md, 40_operations/python/trajectory_rl/__init__.py, 40_operations/python/trajectory_rl/candidates.py, 40_operations/python/trajectory_rl/emit.py, 40_operations/scripts/run_agent_benchmark.py, 40_operations/scripts/self_eval_learning_loop.py, 40_operations/scripts/trajectory_emit.py, 40_operations/scripts/trajectory_rl_bridge.py, 90_archive/artifacts/bench_rl_demo/latest.json, 90_archive/artifacts/bench_rl_demo/latest.md, 90_archive/artifacts/bench_rl_demo/run_20260527_lit_bad_tool/trajectory.jsonl, 90_archive/artifacts/bench_rl_demo/run_20260527_lit_good/trajectory.jsonl

```
feat(trajectory-rl): instrument traces, composite reward, and skill learning bridge

Add JSONL emit protocol, Cursor hooks, benchmark demo, and self-eval composite scoring with trajectory_weight so skills improve from measurable run paths without LLM fine-tuning.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-27 `33db867b` — docs: changelog entry for trajectory-rl commit a971eb3a

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
docs: changelog entry for trajectory-rl commit a971eb3a

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-28 `e344df64` — chore(data): sync corpus, memory logs, and extraction progress

- **Files:** .agent/memory/eval_events.jsonl, .agent/memory/memory.db, .agent/memory/raw_events.jsonl, .agent/memory/self_eval.jsonl, .agent/task/learning_run_20260527_190119.json, 20_knowledge/wiki/sources/books_md/INDEX.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part01.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part02.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part03.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part04.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part05.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part06.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part07.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part08.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part09.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part10.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part11.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part12.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part13.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part14.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part15.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part16.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part17.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part18.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part19.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part20.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part21.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part22.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part23.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part24.md (+529 more)

```
chore(data): sync corpus, memory logs, and extraction progress

Record the remaining workspace updates after trajectory RL integration, including books corpus refreshes, memory telemetry growth, and PDF/books_rag progress artifacts.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-28 `97b748ec` — chore(data): sync corpus and extraction progress artifacts

- **Files:** .agent/task/learning_run_20260527_190119.json, 20_knowledge/wiki/sources/books_md/INDEX.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part01.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part02.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part03.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part04.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part05.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part06.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part07.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part08.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part09.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part10.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part11.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part12.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part13.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part14.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part15.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part16.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part17.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part18.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part19.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part20.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part21.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part22.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part23.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part24.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part25.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part26.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part27.md, 20_knowledge/wiki/sources/books_md/inbox_raw/andrew_d_bersten_jonathan_handy_oh_s_intensive_care_manual_2018_elsevier_libge__f863c297a1_part28.md (+525 more)

```
chore(data): sync corpus and extraction progress artifacts

Record remaining workspace updates after trajectory RL integration, including books corpus refreshes, PDF/books_rag progress artifacts, and related changelog updates (excluding local memory DB/event logs).

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-28 `f548cec3` — feat(notebooklm): add consumer extraction workflow and docs

- **Files:** .agent/memory/eval_events.jsonl, .agent/memory/memory.db, .agent/memory/raw_events.jsonl, .agent/memory/self_eval.jsonl, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 40_operations/scripts/notebooklm_consumer_extract.py, docs/NOTEBOOKLM_CONSUMER_INTEGRATION.md, outputs/notebooklm/notebooklm_skill_fit_assessment.md, outputs/notebooklm/skill_system_transition_assessment.md, requirements.txt

```
feat(notebooklm): add consumer extraction workflow and docs

Introduce NotebookLM consumer extraction script and supporting documentation, while syncing generated outputs and changelog artifacts for the transition assessment workflow.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-28 `181e3025` — merge: integrate origin/master into remediation branch

- **Files:** 

```
merge: integrate origin/master into remediation branch

Resolve diverged histories after local history cleanup and prefer current branch versions for conflicted operational files.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-05-28 `68cb0455` — feat(skills): implement model-native transition workflow with verification guardrails

- **Files:** 30_system/04_documentation/context/log.md, 30_system/SKILLS/SKILL_model-native-skill-transform.md, 30_system/SKILLS/SKILL_write-prd.md, 30_system/SKILLS/evals/model-native-skill-transform.json, 30_system/SKILLS/registry.json, 30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md, 30_system/docs/templates/prd.example.json, 30_system/docs/templates/prd.schema.json

```
feat(skills): implement model-native transition workflow with verification guardrails

Add P1+P2+P3 transition artifacts by standardizing the engineering chain in PRD guidance, introducing reproducibility and baseline-vs-steered verification controls, and registering a new model-native-skill-transform skill with eval seed for repeatable execution.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-06-01 `6e20f945` — feat(harness): LifeHarness RAG, NotebookLM gate, wiki skills, books_rag paths

- **Files:** .agent/MEMORY.md, .agent/memory/self_eval.jsonl, .agent/task/METAANALIZA_CODEBOOK_MIGRATION.md, .agent/task/_templates/arxiv_digest_template.md, .agent/task/arxiv_digest_2026-05.md, .agent/task/arxiv_scan_2026-05.json, .agent/task/brain_health_audit_2026-05-30.md, .agent/task/skill_auto_detect_verify_2026-05-18.md, .agents/skills/defuddle/SKILL.md, .agents/skills/json-canvas/SKILL.md, .agents/skills/json-canvas/references/EXAMPLES.md, .agents/skills/obsidian-bases/references/FUNCTIONS_REFERENCE.md, .agents/skills/obsidian-cli/SKILL.md, .agents/skills/obsidian-markdown/references/CALLOUTS.md, .agents/skills/obsidian-markdown/references/EMBEDS.md, .agents/skills/obsidian-markdown/references/PROPERTIES.md, .cursor/docs/INDEX.md, .cursor/docs/MCP_AND_SKILLS_LAYERS.md, .cursor/hooks/trajectory_lifecycle.py, .cursor/mcp.json, .cursor/mcp_servers/books_rag_server.py, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/books-rag.mdc, .cursor/rules/gpu-compute.mdc, .cursor/rules/skills-auto-detect.mdc, .cursor/skills/claude-history-ingest/SKILL.md, .cursor/skills/claude-history-ingest/references/claude-data-format.md, .cursor/skills/codex-history-ingest/SKILL.md, .cursor/skills/codex-history-ingest/references/codex-data-format.md, .cursor/skills/copilot-history-ingest/SKILL.md (+258 more)

```
feat(harness): LifeHarness RAG, NotebookLM gate, wiki skills, books_rag paths

Add NotebookLM research gate, arXiv skill scout, fused/TGS RAG, GPU policy,
and Cursor wiki skill pack; externalize books_rag index data; extend registry,
orchestrator routing, tests, and wiki knowledge nodes.

Co-authored-by: Cursor <cursoragent@cursor.com>
```

## 2026-06-01 `79e1efc8` — fix(hygiene): sync Cowork path cleanup, brain_health context split, test fix

- **Files:** .agent/MEMORY.md, .agent/system/README.md, .agent/task/examples/new_statistics_task_example.md, .cursor/docs/SKILL_CREATION_GUIDE.md, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/agent-rules-readonly-when-referenced.mdc, .cursor/rules/books-rag.mdc, .cursor/rules/coding-discipline.mdc, .cursor/rules/context-optimization.mdc, .cursor/rules/core-principles.mdc, .cursor/rules/discovery-pipeline.mdc, .cursor/rules/skills-auto-detect.mdc, 20_knowledge/reference_library/statistics/Global_Medical_Statistics_Discovery_Report.md, 20_knowledge/reference_library/statistics/discovery/README.md, 20_knowledge/reference_library/statistics/index.md, 20_knowledge/reference_library/statistics/knowledge_bases/README.md, 30_system/SKILLS/SKILL_figure-pipeline.md, 30_system/SKILLS/SKILL_research-lookup.md, 30_system/SKILLS/SKILL_setup-project.md, 30_system/SKILLS/evals/setup-project_outputs.json, 30_system/behavior_rules/07_project_structure.md, 30_system/behavior_rules/09_workflow_optimization.md, 30_system/behavior_rules/23_figure_visualization_pipeline.md, 30_system/behavior_rules/agents/04_medical_data_science/05_reproducibility_setup.md, 30_system/behavior_rules/agents/04_medical_data_science_coder.md, 30_system/behavior_rules/agents/07_statistical_analysis_expert.md, 30_system/claude.md, 30_system/docs/AUDIT_REPORT.md, 30_system/docs/BRAIN_AND_PROJECT.md, 30_system/docs/BRAIN_HEALTH_CRITERIA.md (+11 more)

```
fix(hygiene): sync Cowork path cleanup, brain_health context split, test fix

Align canonical paths across rules, skills, and docs after Claude Cowork
hygiene pass. Split brain_health identity (30_system/context) from project
context (04_documentation, warn-only). Slim root claude.md to bridge only.
Fix pytest regression and update BRAIN_HEALTH_CRITERIA. 152 tests green.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-06-05 `d4987c95` — feat(skilldag): SkillDAG pack, --dag rerank, and PRD/Ralph auto-pipeline

- **Files:** .agent/task/SKILLDAG_FIRST_RUN_PACK.md, .agent/task/skilldag_incorporation_backlog.md, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/skills-auto-detect.mdc, 20_knowledge/wiki/concepts/NotebookLM research gate.md, 20_knowledge/wiki/concepts/SkillDAG.md, 20_knowledge/wiki/concepts/SkillRAE retrieval augmented execution.md, 30_system/SKILLS/SKILL_notebooklm-research-gate.md, 30_system/SKILLS/SKILL_skill-dag-router.md, 30_system/SKILLS/evals/skill-dag-router.json, 30_system/SKILLS/registry.json, 30_system/behavior_rules/reference/classification_hints.md, 30_system/behavior_rules/tools/agents/agent_auto_detection.py, 30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md, 30_system/docs/DEEP_LEARNING_POLICY.md, 30_system/docs/SKILLDAG_MAP.md, 30_system/docs/notebooklm_skilldag_external_verification.json, 30_system/docs/prd_skilldag_incorporation.json, 30_system/docs/reference/notebooklm_skilldag_grill_prompts.md, 30_system/docs/skill_pipelines_dag.json, 40_operations/python/brain_assist/skill_dag_rerank.py, 40_operations/python/brain_assist/skill_pipeline_detect.py, 40_operations/python/brain_assist/skill_rerank.py, 40_operations/scripts/notebooklm_skilldag_grill.py, 40_operations/scripts/notebooklm_skilldag_grill_playwright.py, 40_operations/scripts/skill_dag_subunit_compare.py, 40_operations/scripts/skill_dag_validate.py, 40_operations/scripts/skill_rerank.py, 40_operations/tests/brain_assist/test_skill_dag_rerank.py, 40_operations/tests/brain_assist/test_skill_pipeline_detect.py (+13 more)

```
feat(skilldag): SkillDAG pack, --dag rerank, and PRD/Ralph auto-pipeline

Incorporate SkillDAG notebook extraction (map, validator, registry depends_on, external arXiv ledger). Add skill_rerank --dag prerequisite injection and --auto-pipeline semantic bundle for agentic PRD/Ralph (and scholarly spec). Wire pipeline_auto_load into agent_auto_detection and orchestrator routing.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-06-09 `514f1e97` — feat(relation-conditioned): SkillLens dual registry, REWRITE, and Rcml export

- **Files:** .cursor/hooks/trajectory_lifecycle.py, .cursor/mcp.json, .cursor/mcp_servers/graphify_server.py, .cursor/rules/00_orchestrator_agent.mdc, .cursor/rules/graphify-brain.mdc, .cursor/rules/skills-auto-detect.mdc, .gitignore, .graphifyignore, .graphifyignore.full, 20_knowledge/wiki/concepts/Relation-conditioned harness.md, 20_knowledge/wiki/log.md, 20_knowledge/wiki/sources/notebooklm/relation_conditioned_export.md, 30_system/SKILLS/SKILL_graphify-brain-map.md, 30_system/SKILLS/SKILL_notebooklm-research-gate.md, 30_system/SKILLS/evals/graphify-brain-map.json, 30_system/SKILLS/evals/skill-verifier-gate.json, 30_system/SKILLS/registry.json, 30_system/behavior_rules/reference/classification_hints.md, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 30_system/docs/GRAPHIFY_BRAIN_INTEGRATION.md, 30_system/docs/RELATION_CONDITIONED_MAP.md, 30_system/docs/SKILL_LAYER_TAXONOMY.md, 30_system/docs/notebooklm_relation_conditioned_external_verification.json, 30_system/docs/prd_relation_conditioned_incorporation.json, 30_system/docs/progress.txt, 30_system/docs/rcml_relation_registry.json, 30_system/docs/reference/notebooklm_relation_conditioned_grill_prompts.md, 30_system/docs/verifier_registry.json, 40_operations/python/brain_assist/dual_registry_evolve.py (+35 more)

```
feat(relation-conditioned): SkillLens dual registry, REWRITE, and Rcml export

Incorporate the Relation-Conditioned notebook slice: verifier gate, LARGER-Graphify expansion, trajectory gap bridge, dual verifier registry with human-gated REWRITE proposals, and training-ready Rcml relation catalog with 12 contrastive examples.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-06-16 `91e165ea` — feat(harness): incorporate NotebookLM SkillTree and author-claims gate

- **Files:** .agent/self_harness_state.json, .agent/task/harness_skilltree_incorporation_backlog.md, .agent/task/self_harness_proposals/proposal_0001.json, .agent/task/self_harness_proposals/proposal_0001_applied.json, 20_knowledge/wiki/concepts/Agent harness memory and skill tree.md, 20_knowledge/wiki/concepts/Agent-native clinical knowledge.md, 20_knowledge/wiki/concepts/Failure patterns registry.md, 20_knowledge/wiki/concepts/LifeHarness four-layer model.md, 20_knowledge/wiki/concepts/NotebookLM research gate.md, 20_knowledge/wiki/concepts/SkillDAG.md, 20_knowledge/wiki/log.md, 30_system/SKILLS/SKILL_notebooklm-research-gate.md, 30_system/SKILLS/clusters/notebooklm-gate/intent.md, 30_system/SKILLS/clusters/scholarly-lifecycle/intent.md, 30_system/SKILLS/reference/intent_template.md, 30_system/UBIQUITOUS_LANGUAGE.md, 30_system/docs/K1_CLINICAL_RESEARCH_SPIKE.md, 30_system/docs/LIFEHARNESS_4_LAYER.md, 30_system/docs/notebooklm_harness_skilltree_external_verification.json, 30_system/docs/reference/notebooklm_harness_skilltree_grill_prompts.md, 30_system/docs/verifier_registry.json, 40_operations/python/brain_assist/author_claims_gate.py, 40_operations/python/brain_assist/reward_decay.py, 40_operations/python/brain_assist/skill_rerank.py, 40_operations/python/brain_assist/skill_verifier.py, 40_operations/scripts/assemble_harness_skilltree_batch.py, 40_operations/scripts/author_claims_check.py, 40_operations/scripts/context_sync.py, 40_operations/scripts/failure_patterns_bridge.py, 40_operations/scripts/record_skill_hint.py (+14 more)

```
feat(harness): incorporate NotebookLM SkillTree and author-claims gate

Add gated self-harness workflow, reward decay routing, HIP-If lemma folding,
failure-pattern mining, and deterministic ECMO author-claims check from approved proposal_0001.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-06-16 `ab263b8c` — refactor(harness): scope ECMO author-claims to project packs

- **Files:** .agent/task/harness_skilltree_incorporation_backlog.md, .cursor/rules/99_error_memory.mdc, 10_projects/projects/sedacija-ecmo/author_claims/README.md, 10_projects/projects/sedacija-ecmo/author_claims/rules.json, 30_system/docs/BRAIN_AND_PROJECT.md, 40_operations/python/brain_assist/author_claims_gate.py, 40_operations/scripts/author_claims_check.py, 40_operations/scripts/failure_patterns_bridge.py, 40_operations/tests/brain_assist/test_author_claims_gate.py

```
refactor(harness): scope ECMO author-claims to project packs

Keep generic epistemic fences in brain author_claims_gate and 99_error_memory.
Move ECMO-specific phrasing rules to 10_projects/projects/sedacija-ecmo/author_claims.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-06-16 `b8f42819` — fix(memory): harden episodic engine and brain health on Windows

- **Files:** .agent/MEMORY.md, .cursor/hooks/books_rag_lifecycle.py, .cursor/hooks/memory_lifecycle.py, .cursor/mcp_servers/books_rag_server.py, .cursor/mcp_servers/memory_server.py, 40_operations/scripts/brain_status.py, 40_operations/scripts/context_sync.py, memory_engine/store.py

```
fix(memory): harden episodic engine and brain health on Windows

Add SQLite WAL/busy_timeout for concurrent hook access, UTF-8-safe brain_status/context_sync, and fail-soft memory/books_rag hooks plus MCP servers so sessions keep working when optional layers are unavailable.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-06-18 `29afde5b` — feat(ops): multi-PC workspace bootstrap after OneDrive migration

- **Files:** .cursor/skills/README.md, .cursor/skills/claude-history-ingest/SKILL.md, .cursor/skills/claude-history-ingest/references/claude-data-format.md, .cursor/skills/codex-history-ingest/SKILL.md, .cursor/skills/codex-history-ingest/references/codex-data-format.md, .cursor/skills/copilot-history-ingest/SKILL.md, .cursor/skills/copilot-history-ingest/references/copilot-data-format.md, .cursor/skills/cross-linker/SKILL.md, .cursor/skills/daily-update/SKILL.md, .cursor/skills/data-ingest/SKILL.md, .cursor/skills/graph-colorize/SKILL.md, .cursor/skills/hermes-history-ingest/SKILL.md, .cursor/skills/hermes-history-ingest/references/hermes-data-format.md, .cursor/skills/impl-validator/SKILL.md, .cursor/skills/ingest-url/SKILL.md, .cursor/skills/llm-wiki/SKILL.md, .cursor/skills/obsidian-wiki-ingest/scripts/ingest-wiki.sh, .cursor/skills/openclaw-history-ingest/SKILL.md, .cursor/skills/openclaw-history-ingest/references/openclaw-data-format.md, .cursor/skills/pi-history-ingest/SKILL.md, .cursor/skills/skill-creator/LICENSE.txt, .cursor/skills/skill-creator/SKILL.md, .cursor/skills/skill-creator/agents/analyzer.md, .cursor/skills/skill-creator/agents/comparator.md, .cursor/skills/skill-creator/agents/grader.md, .cursor/skills/skill-creator/assets/eval_review.html, .cursor/skills/skill-creator/eval-viewer/generate_review.py, .cursor/skills/skill-creator/eval-viewer/viewer.html, .cursor/skills/skill-creator/references/schemas.md, .cursor/skills/skill-creator/scripts/__init__.py (+227 more)

```
feat(ops): multi-PC workspace bootstrap after OneDrive migration

Add workspace_bootstrap.py to recreate repo-relative skill junctions on each
machine. Stop tracking .cursor/skills vendor links and large PDF/zips in git;
gitignore junctions and OneDrive hostname conflict copies. Portable Cursor
project path resolution; brain_health checks junction health.

Co-authored-by: Cursor <cursoragent@cursor.com>
```

## 2026-06-18 `b88472cf` — chore(hygiene): canonical paths, wiki hub links, stop tracking runtime logs

- **Files:** .agent/MEMORY.md, .agent/memory/self_eval.jsonl, .agent/task/REMINDER_VERIFIER_NEURAL_PHASE4_2026-07-08.md, .agent/task/_templates/arxiv_digest_template.md, .agent/task/arxiv_digest_2026-05.md, .agent/task/brain_health_audit_2026-06-17.md, .agent/task/harness_skilltree_incorporation_backlog.md, .cursor/skills/llm-wiki/references/karpathy-pattern.md, .cursor/skills/memory-bridge/SKILL.md, .cursor/skills/obsidian-wiki-ingest/SKILL.md, .gitignore, 10_projects/projects/sedacija-ecmo/author_claims/README.md, 20_knowledge/reference_library/opinions/README.md, 20_knowledge/reference_library/opinions/editorials_commentaries/README.md, 20_knowledge/reference_library/opinions/guidelines_consensus/README.md, 20_knowledge/reference_library/statistics/Global_Medical_Statistics_Discovery_Report.md, 20_knowledge/reference_library/statistics/books/README.md, 20_knowledge/reference_library/statistics/discovery/README.md, 20_knowledge/reference_library/statistics/index.md, 20_knowledge/reference_library/statistics/knowledge_bases/README.md, 20_knowledge/reference_library/statistics/knowledge_bases/digital_twin_blueprint.md, 20_knowledge/reference_library/statistics/knowledge_bases/medical_data_science_laboratory.md, 20_knowledge/reference_library/statistics/knowledge_bases/modern_statistical_literature_2024_2025.md, 20_knowledge/reference_library/statistics/papers/README.md, 20_knowledge/reference_library/tools/CLEANUP_GUIDE.md, 20_knowledge/reference_library/tools/README.md, 20_knowledge/reference_library/writing/manuscript_tips_checklist.md, 20_knowledge/wiki/sources/notebooklm/geometry_export.md, 30_system/SKILLS/SKILL_autosci-memory-centric-lifecycle.md, 30_system/SKILLS/SKILL_graphify-brain-map.md (+51 more)

```
chore(hygiene): canonical paths, wiki hub links, stop tracking runtime logs

Align README and docs to 30_system/ canonical paths; add semantic graph hub
footers across skills and reference_library. Add brain health audit task and
NotebookLM geometry export. Untrack self_eval.jsonl and remaining .cursor/skills
vendor paths; ignore last_injected_context.md.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-07-02 `565da232` — fix(books-rag): multi-PC index copy workflow and verify fixes

- **Files:** .gitignore, 30_system/docs/BOOKS_RAG_GPU_RUNBOOK.md, 30_system/docs/MULTI_PC_WORKSPACE.md, 40_operations/scripts/books_rag_repair_manifest.py, 40_operations/scripts/books_rag_sync_from_peer.ps1, 40_operations/scripts/books_rag_verify.py

```
fix(books-rag): multi-PC index copy workflow and verify fixes

Add sync/repair scripts for copying C:\books_rag from GPU build machine.
Verify supports parent-child domains and --cpu-ok on weak-GPU PCs.
Update MULTI_PC and GPU runbook; gitignore cleanup audit logs.

Co-authored-by: Cursor <cursoragent@cursor.com>
```


## 2026-07-02 `5dcb46ec` — feat(ci): GitHub Actions pytest workflow + salvage arxiv digest 2026-06 from stale OneDrive copy

- **Files:** .agent/task/arxiv_digest_2026-06.md, .agent/task/arxiv_scan_2026-06.json, .github/workflows/tests.yml, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
feat(ci): GitHub Actions pytest workflow + salvage arxiv digest 2026-06 from stale OneDrive copy

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```


## 2026-07-02 `543d0c36` — refactor(repo): extract 90_archive (991MB, 11k files) to standalone local repo

- **Files:** .gitignore, .gitmodules, 30_system/docs/ARCHIVE_EXTRACTION_2026-07-02.md, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 90_archive/ARCHIVE/README.md, 90_archive/ARCHIVE/behavior_rules/README.md, 90_archive/ARCHIVE/legacy_docs/CONSOLIDATION_NOTES.md, 90_archive/ARCHIVE/legacy_docs/FOLDER_STRUCTURE.md, 90_archive/ARCHIVE/legacy_docs/INSTALLATION.md, 90_archive/ARCHIVE/legacy_docs/LEGACY_NOTES.md, 90_archive/ARCHIVE/legacy_docs/PROJECT_TEMPLATE.md, 90_archive/ARCHIVE/legacy_docs/QUICK_START.md, 90_archive/ARCHIVE/legacy_docs/README-DESKTOP-8FP2N9R.md, 90_archive/ARCHIVE/legacy_docs/STYLE_RULES_IMPLEMENTATION.md, 90_archive/ARCHIVE/legacy_docs/SUMMARY.md, 90_archive/ARCHIVE/legacy_docs/context.md, 90_archive/ARCHIVE/legacy_docs/preferences.md, 90_archive/ARCHIVE/pdf_duplicates_2026-05-05/MOVE_MANIFEST.json, 90_archive/ARCHIVE/planning_history/DISCOVERY_FINDINGS.md, 90_archive/ARCHIVE/planning_history/MIGRATION_ARCHIVE.md, 90_archive/ARCHIVE/planning_history/README.md, 90_archive/ARCHIVE/planning_history/UPGRADE_PLAN.md, 90_archive/ARCHIVE/planning_history/UPGRADE_PRIORITIES.md, 90_archive/ARCHIVE/planning_history/UPGRADE_SELF_ASSESSMENT_PLAN.md, 90_archive/ARCHIVE/planning_history/UPGRADE_SWISS_CHEESE_PLAN.md, 90_archive/artifacts/bench/trend.jsonl, 90_archive/artifacts/bench_rl_demo/latest.json, 90_archive/artifacts/bench_rl_demo/latest.md, 90_archive/artifacts/bench_rl_demo/run_20260527_lit_bad_tool/trajectory.jsonl (+11113 more)

```
refactor(repo): extract 90_archive (991MB, 11k files) to standalone local repo

Tree shrinks ~70%; archive lives at Documents/agent-rules-archive with its own git history.
Submodule obsidian-wiki removed with the archive.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```


## 2026-07-02 `dc939a86` — feat(ops): session-start sync guard + ADR memory consolidation

- **Files:** .cursor/hooks.json, 30_system/docs/ADR_2026-07-02_memory_canonical.md, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, scripts/check_sync.py

```
feat(ops): session-start sync guard + ADR memory consolidation

check_sync.py warns when HEAD is behind origin/master (multi-PC drift guard).
ADR declares memory_engine canonical over claude-mem/ECC/MEMORY.md layers.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```


## 2026-07-02 `e90f095a` — chore(docs): sync CHANGELOG_AUTO after weekly learning activation

- **Files:** 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md

```
chore(docs): sync CHANGELOG_AUTO after weekly learning activation

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```


## 2026-07-02 `b7349c38` — feat(learning): weekly rules update 2026-W27

- **Files:** .agent/MEMORY.md, .agent/task/learning_run_20260702_133917.json

```
feat(learning): weekly rules update 2026-W27

NO-OP run â€” nema novih prijedloga ni obrazaca ovaj tjedan.

Prihvaceni prijedlozi: (nijedan)
Odbijeni prijedlozi: (nijedan)
Odgodeni prijedlozi: (nijedan)

Razlog: Tjedni digest za W29 jos nije generiran (generira se
nedjeljom). Proposals iz W28 i W29 su vec ingested i implemented u
digest_proposal_ledger.jsonl (approved_at: 2026-07-01). HUM-3
(writing-avoid-ai.mdc v1.5) potvrden kao implementiran. self_eval
failure_mode=unknown (ingest score=0.95) je poznati artefakt â€” nema
regresije ni novog obrasca >=2 pojave.

Pytest: 268 passed, 5 skipped.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```


## 2026-07-02 `17d6bf4d` — feat(brain): process-leak guard + memory typing/pruning + dreaming playbooks

- **Files:** 30_system/docs/BRAIN_AUDIT_2026-07-02.md, 40_operations/scripts/machine_digest_learning.py, 40_operations/scripts/memory_prune.py, 40_operations/scripts/workspace_bootstrap.py, 40_operations/tests/memory_engine/test_memory_upgrades.py, 40_operations/tests/scripts/test_digest_playbooks.py, README.md, index.md, memory_engine/compression.py, memory_engine/config.py, memory_engine/ingest.py, memory_engine/models.py, memory_engine/store.py, scripts/check_sync.py

```
feat(brain): process-leak guard + memory typing/pruning + dreaming playbooks

Track A: session-start CWD guard (scripts/check_sync.py) + session_cwd check
in workspace_bootstrap.py â€” catches sessions launched from the stale OneDrive
copy (the real 2026-07 drift cause; junction check only validated symlink
targets). Docs: .mdc count 58->60; README link CLAUDE.md->claude.md.

Track B: brain-inspired memory upgrades on canonical memory_engine (per ADR):
typed memory (mem_type explicit/implicit/associative), staleness pruning
(store.prune_stale + memory_prune.py), and an ingest poisoning guard that
quarantines memory-injection payloads (ref arXiv 2606.28270, our W28 digest).

Track C: Dreaming-style playbooks (machine_digest_learning.py --emit-playbooks)
per accepted proposal. Skill-reference validation already covered by
skill_registry.py validate (PASS).

Audit: 30_system/docs/BRAIN_AUDIT_2026-07-02.md. pytest 274 pass / 5 skip.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```


## 2026-07-05 `03d600d7` — feat(harness): NotebookLM Harness Memory v2 cycle + memory_hierarchy QA

- **Files:** .agent/MEMORY.md, .agent/memory_hierarchy/index.json, .agent/memory_hierarchy/summaries/lemma-001-hv2-bootstrap-lemma.md, .agent/self_harness_state.json, .agent/solved_lemmas.jsonl, .agent/task/harness_v2_incorporation_backlog.md, .agent/task/self_harness_proposals/proposal_0002.json, .agent/task/self_harness_proposals/proposal_0003.json, .agent/task/user_notebook_91614142_incorporation_backlog.md, 20_knowledge/wiki/concepts/Agent harness memory and skill tree.md, 20_knowledge/wiki/concepts/AutoMem metamemory skill.md, 20_knowledge/wiki/concepts/HORMA hierarchical memory.md, 20_knowledge/wiki/log.md, 20_knowledge/wiki/sources/notebooklm/harness_v2.md, 30_system/04_documentation/context/log.md, 30_system/SKILLS/SKILL_notebooklm-research-gate.md, 30_system/SKILLS/clusters/harness/intent.md, 30_system/SKILLS/clusters/memory-ops/intent.md, 30_system/SKILLS/evals/memory-hierarchy.json, 30_system/SKILLS/evals/self-harness-gate.json, 30_system/SKILLS/reference/intent_template.md, 30_system/UBIQUITOUS_LANGUAGE.md, 30_system/docs/CHANGELOG_AUTO.jsonl, 30_system/docs/CHANGELOG_AUTO.md, 30_system/docs/K1_CLINICAL_RESEARCH_SPIKE.md, 30_system/docs/LIFEHARNESS_4_LAYER.md, 30_system/docs/MEMORY_HIERARCHY_SPEC.md, 30_system/docs/notebooklm_harness_skilltree_external_verification.json, 30_system/docs/notebooklm_harness_v2_external_verification.json, 30_system/docs/notebooklm_user_notebook_91614142_external_verification.json (+34 more)

```
feat(harness): NotebookLM Harness Memory v2 cycle + memory_hierarchy QA

Land harness v2 grill gate (seeded + partial live), HORMA memory_hierarchy module,
cluster intents, eval seeds, and brain_health UTF-8 fix. Clean test lemma pollution;
277 pytest OK, brain_health PASS.

Co-authored-by: Cursor <cursoragent@cursor.com>
```

