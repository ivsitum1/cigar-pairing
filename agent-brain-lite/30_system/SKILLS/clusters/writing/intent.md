---
cluster_id: writing
domain: writing
parent_layer: scaffold
related_skills:
  - manuscript-writing
  - manuscript-structure
  - avoid-ai-formulations
  - ai-detection
  - literature-synthesis
  - prisma-checklist
last_updated: 2026-06-28
---

# Intent: Academic writing and reporting

## Legislative intent

Produce journal-ready prose with methodology checklists, anti-AI pattern compliance, and verified citations. Done means submission-quality draft with detector score target under 20%.

## In scope

- Manuscript structure, SR reporting, checklist skills
- Full manuscript protocol (`manuscript-writing`): file hygiene, style QC, pre-output gate
- avoid-ai-formulations + ai-detection pairing when allowed

## Out of scope

- Blog/newsletter (nonacademic-writer cluster)
- Autonomous rule rewrites

## Dependencies (SkillDAG)

- depends_on: []
- conflicts_with: [nonacademic-writer]

## Success signals

- Pattern scan score < 0.20
- Swiss gate required: yes (pre-submission)

## Provenance

- Source: registry tier3_pairing + humanize notebook
