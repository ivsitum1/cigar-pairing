---
name: machine-weekly-digest
description: Weekly Machine digest for agent-rules brain — arXiv, GitHub AI repos, AI news RSS, upgrade proposals. Triggers include machine weekly digest, machine digest, weekly machine upgrade, sensor digest, the machine digest.
version: 1.0
last_updated: 2026-06-29
domain: meta
tokens: ~400
triggers:
  - machine weekly digest
  - machine digest
  - weekly machine upgrade
  - sensor digest
  - the machine digest
requires_packages: []
reference_files:
  - 30_system/docs/THE_MACHINE.md
  - .agent/task/_templates/machine_digest_template.md
pipeline_position: []
---

# Skill: Machine Weekly Digest

## When to use

Brain repo (`agent-rules`) maintenance: aggregate weekly sensor outputs and produce upgrade proposals for the Machine architecture.

## Procedure

1. Run `python 40_operations/scripts/machine_weekly_digest.py` (or `--dry-run`).
2. Open `.agent/task/machine_digest_YYYY-WW.md`.
3. Human gate: approve proposals in chat before registry or rule changes.

## Honesty

- Sensor outputs are pointers, not verified claims.
- Do not auto-register skills from proposals.

## Related

- `SKILL_arxiv-skill-scout.md`
- `30_system/docs/THE_MACHINE.md`
