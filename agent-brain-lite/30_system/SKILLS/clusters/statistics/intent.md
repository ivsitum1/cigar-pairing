---
cluster_id: statistics
domain: statistics
parent_layer: scaffold
related_skills:
  - eda-flexplot
  - test-selection
  - r-statistics
  - meta-analysis
  - bayesian-workflow
  - swiss-cheese
last_updated: 2026-06-24
---

# Intent: Statistics and inference

## Legislative intent

Standardize exploratory analysis, test selection, inferential workflows, and validation gates for clinical research pipelines. Done means reproducible estimates with assumptions checked and Swiss gate before manuscript claims.

## In scope

- EDA → user pause → inferential skill
- Meta-analysis, Bayesian, forest plots, publication bias
- Swiss Cheese before Results text

## Out of scope

- Software PRD/Ralph
- Non-statistical automation scripts

## Dependencies (SkillDAG)

- depends_on: [eda-flexplot]
- conflicts_with: []

## Success signals

- Eval pass rate target: ≥ 85% on stats eval seeds
- Swiss gate required: yes (primary analyses)

## Provenance

- Source: skills-auto-detect pipeline table
- Notes: Skill tree grouping; routing via SkillDAG
