---
name: create-skill
description: Meta-skill for authoring SKILL files, registry entries, eval JSON, optional optimization loop, and benchmark reports.
version: 1.0
last_updated: 2026-05-10
domain: meta
tokens: ~450
triggers:
  - create skill
  - new skill
  - add skill
  - skill gap
  - skill builder
  - auto research skill
requires_packages: []
reference_files: []
pipeline_position: []
---

# Meta-Skill: Skill Builder (Create skill)

**Purpose:** Create new skills, define eval suites, run the autonomous optimization loop, and produce benchmark reports. This meta-skill references existing automation; it does not replace it.

---

## Triggers

- "skill builder", "create skill", "skill-builder", "@skill-builder"
- "auto research skill", "evaluate and optimize skill"
- User asks to draft a new skill or to run optimization + benchmarking for an existing skill

---

## Scope

- **New skill:** Phase 1 (Creation) + Phase 2 (Eval suite); optionally Phase 3 + 4 if evals exist.
- **Existing skill:** Phase 3 (Iterative optimization) + Phase 4 (Benchmarking); optionally Phase 2 if evals are missing or need expansion.
- **Full cycle:** 1 -> 2 -> 3 -> 4 for a new skill with evals.

---

## Phase 1 - Creation

1. **Define the skill:**
   - Clear description (when to use, prerequisites).
   - Allowed tools (e.g. read file, MCP PubMed, write file).
   - Triggers (keywords/phrases that should load this skill).

2. **Draft YAML front matter and steps:**
   - `name`, `domain`, `tokens` (estimate), `triggers`, `reference_files` (if any).
   - Step-by-step procedure; each step actionable and tied to the skill goal.

3. **Output:**
   - Write to `30_system/SKILLS/SKILL_<id>.md` (use kebab-case id, e.g. `my-new-skill`).
   - Add or update entry in `30_system/SKILLS/registry.json`: `id`, `file`, `domain`, `triggers`, `conflicts_with` (if any), `disambiguation` (short hint for when to choose this over others).

4. **Reference:** Use existing skills (e.g. `30_system/SKILLS/SKILL_avoid-ai-formulations.md`) as structure templates.

---

## Phase 1b - Search before create (ECC skill-scout pattern)

Before authoring a new skill ID:

1. Scan `30_system/SKILLS/registry.json` triggers and `skill_task_mapping.md`.
2. Check `90_archive/imports/ecc-index/SKILL_MAP.yaml` for enrich-only mappings.
3. If an existing skill covers >80% of the workflow, **enrich** that skill and reference files instead of adding a duplicate registry entry.

## Phase 2 - Eval suite

1. **Create or update** `30_system/SKILLS/evals/<id>.json` (eval-first; binary assertions only).

2. **Schema (see `30_system/SKILLS/evals/README.md`):**
   - `skill_id`, `version: "1.0"`, `cases[]`.
   - Each case: `id`, `input` (e.g. `{ "text": "..." }`), `assertions[]`.
   - Each assertion: `type`, `value`, optional `description`. Use binary types only: `contains`, `not_contains`, `regex_match`, `regex_not_match`, `word_count_below`, `word_count_above`, `word_count_between`, `last_sentence_not_question`.

3. **Optional:** Use `40_operations/scripts/generate_evals_from_skill.py` to bootstrap an initial evals file from the skill, then refine.

---

## Phase 3 - Iterative optimization

1. **Follow** `30_system/docs/SKILL_OPTIMIZATION_AGENT.md` exactly.

2. **Summary of loop:**
   - Read `30_system/SKILLS/SKILL_<id>.md` and `30_system/SKILLS/evals/<id>.json`.
   - For each case, apply the skill and write output to `30_system/SKILLS/evals/<id>_outputs.json` (format: `{"case_1": "text", ...}`).
   - Run: `python 40_operations/scripts/skill_eval_runner.py --skill-id <id> --outputs 30_system/SKILLS/evals/<id>_outputs.json --json`.
   - Parse pass rate and `failed_assertions`. If pass rate < 100%, edit the skill (one change per iteration), re-run outputs and eval; if score improves, commit; else revert and try a different edit.
   - Log each iteration to `30_system/SKILLS/evals/<id>_optimization_log.md`.
   - Do not stop for permission until 100% pass or user interrupt.

3. **No API:** Use `--outputs` so the runner only evaluates; no external LLM calls from the script.

---

## Phase 4 - Benchmarking

1. **Produce a short report** comparing baseline (or old version) vs final (or new version):
   - Pass rate before / after.
   - Number of assertions passed and failed (before / after).
   - List of assertions that were failing and are now fixed (or still failing).

2. **Save to** `30_system/SKILLS/evals/<id>_benchmark_report.md` (or append to the optimization log if preferred). Include date and skill id.

---

## File reference

| Item | Path |
|------|------|
| Optimization procedure | `30_system/docs/SKILL_OPTIMIZATION_AGENT.md` |
| Eval schema and assertion types | `30_system/SKILLS/evals/README.md` |
| Eval runner | `40_operations/scripts/skill_eval_runner.py` |
| Optional evals generator | `40_operations/scripts/generate_evals_from_skill.py` |
| Skill registry | `30_system/SKILLS/registry.json` |

## Semantic graph (auto)

- [[Skill gap pipeline]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[Skill gap pipeline]]
- [[Skill evals binary assertions]]
- [[SKILL_skill-discovery]]
- [[Skill optimization safety gates]]
- [[SKILL_ralph-loop]]
