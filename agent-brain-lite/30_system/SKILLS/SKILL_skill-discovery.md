---
name: skill-discovery
description: >-
  Finds procedural skills for the agent-rules brain: scans local registry first,
  then SkillsMP/GitHub via API. Use when no integrated skill matches, external skill,
  SkillsMP, find skill, nedostaje skill, koji skill, pretraži skillove, skill marketplace.
  Run before create-skill unless user wants immediate authoring.
version: 1.0
last_updated: 2026-05-16
domain: meta
tokens: ~900
triggers:
  - find skill
  - skill discovery
  - external skill
  - SkillsMP
  - skills marketplace
  - nedostaje skill
  - nema skilla
  - koji skill
  - pretraži skill
  - skill nije integriran
  - agent skills marketplace
requires_packages: []
reference_files: []
pipeline_position: []
---

# Skill: Skill discovery (local brain + SkillsMP)

Locates skills **already in** `30_system/SKILLS/` or **candidates on** [SkillsMP](https://skillsmp.com/) for optional import. Does not install skills automatically.

## When to use

- User needs a workflow that is **not** loading via `skills-auto-detect.mdc`.
- User asks to search SkillsMP, GitHub agent skills, or „što imamo u mozgu za X”.
- Before creating a new skill (`SKILL_create-skill.md`), unless user says „odmah napravi skill”.

## When NOT to use

- Task already maps to a registry skill → load that skill instead.
- One-off question with no repeatable procedure.

## Step-by-step procedure

### 1) Define search intent (one line)

Extract: **domain** (legal, clinical, stats, writing, marketing, engineering), **verbs** (review, search, grant, meta-analysis), **stack** (R, Python), **language** (hr/en).

### 2) Local scan (always first)

From repo root (`agent rules` workspace):

```bash
py -3 40_operations/scripts/skill_discovery_scan.py "<keywords>" --top 10
```

Optional JSON:

```bash
py -3 40_operations/scripts/skill_discovery_scan.py "<keywords>" --json
```

Also read manually:

- `30_system/SKILLS/registry.json` — `triggers`, `disambiguation`, `conflicts_with`
- `30_system/behavior_rules/reference/skill_task_mapping.md`

**Decision:**

| Local result | Action |
|--------------|--------|
| Clear match, `file_exists: true` | Tell user to invoke `@<id>` or rely on auto-detect; load `SKILL_<id>.md` |
| Match in registry but **missing** `SKILL_*.md` | Report tech debt; offer to implement file or use closest skill |
| Weak / no match | Continue to step 3 |

### 3) Cached research (optional, fast)

If present, skim:

- `.agent/task/skillsmp_detailed_report.md` — curated shortlist by domain
- `.agent/task/skillsmp_search_results.json` — last API batch
- `.agent/task/zip_skill_inventory.json` — unpacked zip skill previews

Refresh cache only if stale or query is novel (step 4).

### 4) SkillsMP live search (external)

Single query:

```bash
py -3 40_operations/scripts/skillsmp_search.py "<english keywords>" --limit 12
```

Full domain batch (16 queries, ~1 min):

```bash
py -3 40_operations/scripts/skillsmp_search_batch.py
```

Writes `.agent/task/skillsmp_search_results.json`.

**Evaluate candidates:**

1. Open `githubUrl` and read `SKILL.md` (not only description).
2. Prefer: [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins), [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills), [beita6969/ScienceClaw](https://github.com/beita6969/ScienceClaw) — then others by relevance.
3. Check: disclaimer for legal/clinical, no PHI exfiltration, no destructive bash, license.
4. Compare to local skills — **do not recommend import** if `meta-analysis`, `test-selection`, `grill-me`, etc. already cover it.

### 5) Deliverable to user

Structured report (summary first):

```markdown
## Skill discovery: [intent]

### Already integrated (use these)
- `id` — why it fits — disambiguation note

### Registry gap (listed but no file)
- ...

### External candidates (review before import)
| Rank | name | author | stars | github | fit | risk |
|------|------|--------|-------|--------|-----|------|

### Recommendation
- **Use now:** ...
- **Adapt into brain:** ... (→ create-skill + registry + eval)
- **Cursor-only / one-off:** clone to ~/.cursor/skills without registry
```

Save long runs to `.agent/task/skill_discovery_<YYYYMMDD>_<slug>.md` when >15 lines of candidates.

### 6) Handoff

| Outcome | Next step |
|---------|-----------|
| Good local skill | Load it; stop discovery |
| Good external + repeatable | `SKILL_create-skill.md` + wiki log (`skill_gap_ingest.py wiki-log`) |
| Good external + one-off | User installs in Claude/Cursor skills folder; no registry |
| Nothing fit | Skill gap branch or improvise with orchestrator only |

## Programmatic rules

- **>2 SkillsMP queries:** use `skillsmp_search_batch.py` or a small Python loop, not manual repeated tool churn.
- **Rate limit:** SkillsMP anonymous ~50 req/day; batch thoughtfully.

## Honesty checkpoints

- Stars on SkillsMP often reflect **parent repo**, not skill quality.
- Never claim a skill was audited unless `SKILL.md` was read.
- Do not fabricate GitHub URLs; only report API/script output.

## Verification

- [ ] Local scan run or registry read
- [ ] At least one of: cache read, SkillsMP search, or explicit „no network” note
- [ ] Clear recommendation: use local / import / create / one-off
- [ ] No duplicate of existing registry skill without disambiguation

## Scripts

| Script | Purpose |
|--------|---------|
| `40_operations/scripts/skill_discovery_scan.py` | Local registry + file existence |
| `40_operations/scripts/skillsmp_search.py` | Single SkillsMP query |
| `40_operations/scripts/skillsmp_search_batch.py` | 16-query batch → `.agent/task/skillsmp_search_results.json` |

## Related (wiki)

- [[Skill discovery skill]]
- [[Skill gap pipeline]]
- [[Skill registry]]
- [[Clinical CDSS skill]]
- [[Legal contract review skill]]

## Related (repo)

- `SKILL_create-skill.md`, `30_system/docs/SKILL_GAP_PIPELINE.md`
- Report: `.agent/task/skillsmp_detailed_report.md`
