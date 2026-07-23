# Skill optimization run summary

**Date:** 2026-03-14  
**Run:** Optimization loop for **all 21 skills** (agent-only evaluation, no API).  
**Method:** For each skill: agent applied skill to each case → saved to `<id>_outputs.json` → ran `skill_eval_runner.py --outputs 30_system/SKILLS/evals/<id>_outputs.json --json` → pass rate.

---

## Results – all skills

| Skill | Pass rate | Iterations | Skill changed? |
|-------|------------|------------|----------------|
| avoid-ai-formulations | 100% | 0 (baseline) | No |
| manuscript-structure | 100% | 0 (baseline) | No |
| validate-setup | 100% | 0 (baseline) | No |
| ai-detection | 100% | 0 (baseline) | No |
| bayesian-workflow | 100% | 0 (baseline) | No |
| consort-checklist | 100% | 0 (baseline) | No |
| document-conversion | 100% | 0 (baseline) | No |
| figure-pipeline | 100% | 0 (baseline) | No |
| forest-plot | 100% | 0 (baseline) | No |
| grade-assessment | 100% | 0 (baseline) | No |
| meta-analysis | 100% | 0 (baseline) | No |
| prisma-checklist | 100% | 0 (baseline) | No |
| publication-bias | 100% | 0 (baseline) | No |
| sensitivity-analysis | 100% | 0 (baseline) | No |
| setup-project | 100% | 0 (baseline) | No |
| strobe-checklist | 100% | 0 (baseline) | No |
| swiss-cheese | 100% | 0 (baseline) | No |
| target-trial-emulation | 100% | 0 (baseline) | No |
| test-selection | 100% | 0 (baseline) | No |
| create-sop | 100% | 0 (baseline) | No |
| literature-synthesis | 100% | 0 (baseline) | No |

All 21 skills reached 100% at baseline; no modifications to skill files were needed.

**Fix during run:** In `setup-project.json`, one assertion was changed from `regex_match` (invalid JSON escape `\.`) to two `contains` assertions (python, setup_project) so the runner parses the file correctly.

---

## How to re-run

- **One skill:** "Pokreni optimization loop za \<skill_id>"
- **All skills:** Agent produces outputs for each, runs evaluator for each; see `30_system/docs/SKILL_OPTIMIZATION_AGENT.md`.

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)
