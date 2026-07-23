---
cluster_id: scholarly-lifecycle
domain: methodology
parent_layer: scaffold
related_skills:
  - research-grill-me
  - write-research-spec
  - research-spec-to-milestones
  - scholarly-iteration-loop
last_updated: 2026-06-16
---

# Intent: Scholarly research lifecycle

## Legislative intent

Support manuscript, thesis chapter, and protocol work from ambiguous research intent through a written spec, milestones, and gated iteration loops. This cluster is the scholarly analogue of agentic-engineering PRD/Ralph, but for evidence and methods rather than software features.

## In scope

- PICO / study design clarification (research-grill-me)
- Durable research-spec.json and milestone breakdown
- LOOP ON/OFF scholarly iteration with Swiss gate before writing claims

## Out of scope

- Software PRD/Ralph (see agentic-engineering cluster)
- One-off chat answers without spec artifact
- Autonomous rule or skill rewrites

## Dependencies (SkillDAG)

- depends_on: [research-grill-me]
- conflicts_with: [write-prd]

## Success signals

- Eval pass rate target: ≥ 80% on scholarly eval seed
- Swiss gate required: yes (before Results/Discussion prose)

## Provenance

- Source: internal pipeline (SCHOLARLY_WORKFLOW.md)
- Notes: Skill tree grouping only; routing remains SkillDAG + skill_rerank

## Semantic graph (auto)

- [[Scholarly skill loop]]
- [[Engineering skill loop]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../../../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../../../docs/FOLDER_INDEX.md)
