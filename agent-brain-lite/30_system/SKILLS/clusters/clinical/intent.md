---
cluster_id: clinical
domain: clinical
parent_layer: scaffold
related_skills:
  - clinical-cdss
  - books_rag
  - research-lookup
last_updated: 2026-06-24
---

# Intent: Clinical decision support and evidence

## Legislative intent

Bedside and literature-grounded clinical reasoning with explicit uncertainty, guideline alignment, and no hallucinated dosing. Project-specific doctrine lives in `10_projects/`, not global brain.

## In scope

- SBAR-style CDSS via clinical-cdss skill
- books_rag + research-lookup for evidence depth

## Out of scope

- Global encoding of project-specific ECMO/sedation protocols in brain rules
- K1 pipeline until paper verified (see K1 spike)

## Dependencies (SkillDAG)

- depends_on: [research-lookup]
- conflicts_with: []

## Success signals

- Every dose/claim has verifiable source or [BLANK]
- Swiss gate required: yes (patient-facing outputs)

## Provenance

- Source: orchestrator clinical routing + K1 spike doc
