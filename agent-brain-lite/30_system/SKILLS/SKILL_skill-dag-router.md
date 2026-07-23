---
name: skill-dag-router
description: Route skills using registry depends_on and pipeline DAG before flat TF-IDF rerank. Use when loading pipeline sequences, resolving skill prerequisites, or avoiding conflicts_with pairs. NOT subunit decomposition (skill_decompose) or NotebookLM gate (notebooklm-research-gate).
version: 1.0
last_updated: 2026-06-05
domain: engineering
tokens: ~420
triggers:
  - skill dag router
  - skill DAG routing
  - depends_on skills
  - pipeline skill order
  - topological skill load
  - conflicts_with skills
requires_packages: []
reference_files:
  - 30_system/docs/SKILLDAG_MAP.md
  - 30_system/docs/skill_pipelines_dag.json
  - outputs/skillrae/skilldag_subunit_compare.md
pipeline_position:
  - grill-me
conflicts_with:
  - meta-analysis
disambiguation: Inter-skill DAG routing via registry depends_on and skill_pipelines_dag.json; for TF-IDF-only ranking use skill_rerank; for intra-skill steps use skill_decompose (SkillRAE).
---

# Skill: Skill DAG Router

## When to use

- User asks which skills to load for a **named pipeline** (engineering or scholarly)
- Orchestrator needs **prerequisite order** before loading a heavy skill
- Need to block **conflicts_with** or **tier3_pairing.forbidden_pairs** combinations
- After `skill_rerank` returns candidates, need **DAG filter** not replacement

## When NOT to use

- Decomposing steps inside one SKILL file → `skill_decompose` (SkillRAE)
- Flat keyword routing only → `skill_rerank.py`
- NotebookLM claim gating → `notebooklm-research-gate`

## Procedure

1. **Validate DAG**
   ```bash
   python 40_operations/scripts/skill_dag_validate.py
   ```
   Abort routing suggestions if cycles reported.

2. **Identify pipeline**
   - Match user intent to `30_system/docs/skill_pipelines_dag.json` (`agentic-engineering`, `scholarly-spec`, optional `notebooklm-before-prd`).
   - Read `depends_on` and `pipeline_group` from `30_system/SKILLS/registry.json`.

3. **Build load order**
   - Topological sort on `depends_on` edges for the matched pipeline.
   - Entry skill = pipeline `entry`; do not skip prerequisites unless user explicitly opts out.

4. **Conflict check**
   - If two skills share a `conflicts_with` edge or appear in `tier3_pairing.forbidden_pairs`, load **one** only; prefer pipeline order winner.

5. **Combine with rerank (preferred)**
   ```bash
   python 40_operations/scripts/skill_rerank.py --prompt "..." --top 10 --dag --json
   ```
   - `--dag` prepends `depends_on` prerequisites, applies pipeline edge bonuses, and returns `dag.bundle_order`.
   - `agent_auto_detection.py` uses `dag_mode=True` by default for `skill_suggestions`.

6. **Emit bundle**
   - List: `[prereq…] → [target skill]` with `dag_role` (`prerequisite` | `anchor` | `candidate`).

## Verification

- [ ] `skill_dag_validate.py` exit 0
- [ ] No `conflicts_with` pair loaded together
- [ ] Compare report consulted if SkillRAE vs DAG ambiguity: `outputs/skillrae/skilldag_subunit_compare.md`

## Reference

Canonical map: `30_system/docs/SKILLDAG_MAP.md`

## Semantic graph (auto)

- [[SkillDAG]]
- [[Skill gap pipeline]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
