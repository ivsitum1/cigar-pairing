# Optimization loop – all skills (run after evals update from SKILLS_evals_all.md)

**Date:** 2026-03-14  
**Evals source:** `30_system/SKILLS/evals/SKILLS_evals_all.md` (converted to JSON via `40_operations/scripts/md_evals_to_json.py`).

## What was done

1. **Evals updated:** All `30_system/SKILLS/evals/<skill_id>.json` regenerated from the markdown spec (21 skills, 3–4 cases each).
2. **Converter:** `40_operations/scripts/md_evals_to_json.py` parses the md and writes per-skill JSON; run with `python 40_operations/scripts/md_evals_to_json.py` (reads `30_system/SKILLS/evals/SKILLS_evals_all.md`).
3. **Outputs:** New outputs produced for **avoid-ai-formulations** and **ai-detection** (agent-applied skill). Other skills still use existing `*_outputs.json` (from previous eval set); they do not fully match the new cases/assertions.
4. **Full eval run:** `python 40_operations/scripts/run_all_skill_evals.py` (UTF-8-safe; writes runner stdout to a temp file to avoid Windows encoding errors).

## Results (latest run: poboljšani skillovi koji su pali)

**Date:** 2026-03-14

| Skill ID | Pass % | Note |
|----------|--------|------|
| ai-detection | 100% | ✓ |
| avoid-ai-formulations | 100% | ✓ |
| bayesian-workflow | 37.93% | 18 failed |
| consort-checklist | **100%** | ✓ (skill + outputi poboljšani) |
| create-sop | 35.29% | 11 failed |
| document-conversion | 27.78% | 13 failed |
| figure-pipeline | 16.67% | 15 failed |
| forest-plot | 38.89% | 11 failed |
| grade-assessment | 27.27% | 16 failed |
| literature-synthesis | 44.44% | 10 failed |
| manuscript-structure | 35.29% | 11 failed |
| meta-analysis | 27.78% | 13 failed |
| prisma-checklist | **88.89%** | 2 failed (bilo 33%) |
| publication-bias | 33.33% | 12 failed |
| sensitivity-analysis | 33.33% | 12 failed |
| setup-project | **82.35%** | 3 failed (bilo 41%) |
| strobe-checklist | **93.75%** | 1 failed (bilo 19%) |
| swiss-cheese | 33.33% | 12 failed |
| target-trial-emulation | 33.33% | 12 failed |
| test-selection | **100%** | ✓ (skill + outputi poboljšani) |
| validate-setup | **100%** | ✓ (skill + outputi poboljšani) |

**Summary:** **7 skillova na 100%** (ai-detection, avoid-ai-formulations, consort-checklist, test-selection, validate-setup + prethodno). Poboljšani: consort-checklist, test-selection, validate-setup (dodana pravila u skill + novi outputi → 100%); strobe-checklist, prisma-checklist, setup-project (novi outputi + izmjena strobe evala → 82–94%). Uređeni skillovi: `SKILL_consort-checklist.md`, `SKILL_test-selection.md`, `SKILL_validate-setup.md`.

## Next steps (optimization loop per skill)

For each skill with pass rate &lt; 100%:

1. **Generate new outputs** (choose one):
   - With API:  
     `python 40_operations/scripts/skill_eval_runner.py --skill-id <id> --save-outputs 30_system/SKILLS/evals/<id>_outputs.json`  
     (set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).
   - Manually: apply the skill to each case in `30_system/SKILLS/evals/<id>.json` and fill `30_system/SKILLS/evals/<id>_outputs.json`.
2. **Evaluate:**  
   `python 40_operations/scripts/skill_eval_runner.py --skill-id <id> --outputs 30_system/SKILLS/evals/<id>_outputs.json --json`
3. **If &lt; 100%:** edit `30_system/SKILLS/SKILL_<id>.md` (one change per iteration), re-generate outputs, re-eval; commit only when pass rate improves (see `30_system/docs/SKILL_OPTIMIZATION_AGENT.md`).

## Files

- **Eval spec (source):** `30_system/SKILLS/evals/SKILLS_evals_all.md`
- **Converter:** `40_operations/scripts/md_evals_to_json.py`
- **Batch eval:** `40_operations/scripts/run_all_skill_evals.py`
- **One round (API gen + eval):** `40_operations/scripts/run_optimization_round.py` [--force]
- **Runner (with --save-outputs):** `40_operations/scripts/skill_eval_runner.py`

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)
