---
cluster_id: notebooklm-gate
domain: tools
parent_layer: scaffold
related_skills:
  - notebooklm-research-gate
  - research-lookup
last_updated: 2026-06-16
---

# Intent: NotebookLM research gate

## Legislative intent

Block implementation of NotebookLM-grounded ideas until claims are normalized, externally verified where needed, and passed through a grill gate (GO/NO-GO). Prevents UNVERIFIED YouTube synthesis from becoming production rules.

## In scope

- MCP NotebookLM Q&A with session reuse
- Export normalize + gate-report via notebooklm_bridge
- Harness SkillTree and SkillDAG grill prompt packs

## Out of scope

- Replacing PubMed/live evidence (pair with research-lookup)
- Auto wiki promotion without gate GO

## Dependencies (SkillDAG)

- depends_on: []
- conflicts_with: []

## Success signals

- Eval pass rate target: gate blocks UNVERIFIED primary claims
- Swiss gate required: no (methodology gate is upstream)

## Provenance

- Source: notebooklm (harness skilltree + skilldag notebooks)
- Notes: External ledger at `30_system/docs/notebooklm_harness_skilltree_external_verification.json`

## Semantic graph (auto)

- [[NotebookLM research gate]]
- [[SkillDAG]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../../../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../../../docs/FOLDER_INDEX.md)
