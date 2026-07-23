---
name: drug-discovery-workbench
description: Lightweight discovery pipeline pointers for target ID, docking, pathology tools. Use for drug discovery, diffdock, pathml, discovery pipeline 7B. NOT bedside clinical CDSS.
version: 1.0
last_updated: 2026-05-18
domain: discovery
tokens: ~550
triggers:
  - drug discovery
  - diffdock
  - pathml
  - molecular docking
  - discovery workbench
requires_packages: []
reference_files: []
conflicts_with:
  - clinical-cdss
  - meta-analysis
disambiguation: Use for computational discovery workflows; for Pipeline 7B see behavior_rules discovery docs; for clinical scenarios use clinical-cdss.
pipeline_position: [7]
---

# Skill: Drug discovery workbench (light)

## When to use

- Computational drug discovery, docking, or pathology ML exploration
- User references Pipeline 7 or MedDiscovery-style tasks

## Procedure

1. Confirm objective: target ID, hit finding, ADME, or pathology WSI.
2. Route: full discovery → `30_system/behavior_rules/26_discovery_superpipeline.md` and Pipeline 7B triggers.
3. For docking/pathology: use staged external tools only when user provides environment; do not fabricate binding affinities.
4. Document data provenance and model limits.

## Verification

- [ ] No human PK claims from in silico only
- [ ] Staging references in `90_archive/imports/skills_audit_2026-05/` for full vendor skills

## Related

- `25_capability_registry.md`, DISCOVERY_DRUG subagent

## Related Hubs

- [[Drug discovery workbench skill]]
- [[Skills audit 2026-05]]
