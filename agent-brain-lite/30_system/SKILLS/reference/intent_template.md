# Skill cluster intent template

Use one `intent.md` per **skill tree cluster** (domain grouping). SkillDAG handles routing order; intent captures *why* the cluster exists.

## File location

`30_system/SKILLS/clusters/<cluster-id>/intent.md`

## Template

```markdown
---
cluster_id: <kebab-case-id>
domain: <statistics|writing|clinical|engineering|tools|methodology>
parent_layer: scaffold
related_skills:
  - <skill-id-1>
  - <skill-id-2>
last_updated: YYYY-MM-DD
---

# Intent: <Human-readable cluster name>

## Legislative intent

One paragraph: what problems this cluster solves, for whom, and what "done" looks like.

## In scope

- 
- 

## Out of scope

- 
- 

## Dependencies (SkillDAG)

- depends_on: [<skill-id>]
- conflicts_with: [<skill-id>]

## Success signals

- Eval pass rate target: 
- Swiss gate required: yes/no

## Provenance

- Source: [user | notebooklm | prd]
- Notes:
```

## Example clusters (starter)

| cluster_id | related_skills |
|------------|----------------|
| `scholarly-lifecycle` | research-grill-me, write-research-spec, scholarly-iteration-loop |
| `agentic-engineering` | grill-me, write-prd, prd-to-issues, ralph-loop |
| `notebooklm-gate` | notebooklm-research-gate, research-lookup |
| `memory-ops` | agentic-react-os, context_sync fold-lemma, memory_hierarchy (see clusters/memory-ops/intent.md) |

Do not duplicate full SKILL bodies here; link only.

## Semantic graph (auto)

- [[Scholarly skill loop]]
- [[Engineering skill loop]]
- [[Skill registry]]
- [[Statistics skill stack]]
- [SKILLS INDEX](../../docs/indexes/SKILLS_INDEX.md)
- [REFERENCE INDEX](REFERENCE_INDEX.md)
- [FOLDER INDEX](../../docs/FOLDER_INDEX.md)
