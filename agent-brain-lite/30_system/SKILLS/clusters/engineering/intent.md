---
cluster_id: engineering
domain: engineering
parent_layer: scaffold
related_skills:
  - grill-me
  - write-prd
  - prd-to-issues
  - ralph-loop
  - agentic-react-os
last_updated: 2026-06-24
---

# Intent: Agentic software engineering

## Legislative intent

Turn feature intent into verified PRD, issues, and iterative implementation with harness TDD. Done means passing tests and documented interfaces per strategic engineering rules.

## In scope

- grill-me → write-prd → prd-to-issues → ralph-loop
- ReAct/TAOR discipline for multi-step code tasks

## Out of scope

- Scholarly research-spec loop (scholarly-lifecycle cluster)
- Autonomous `.cursorrules` rewrite

## Dependencies (SkillDAG)

- depends_on: [grill-me]
- conflicts_with: [write-research-spec]

## Success signals

- PRD stories `passes: true` before merge
- Harness tests green

## Provenance

- Source: AGENTIC_ENGINEERING_WORKFLOW.md
