---
name: dreaming-daemon
description: Idle grounded creativity — build hypothesis frameworks from run logs with source_ref on every premise. Triggers include dreaming daemon, run dreaming, knowledge frameworks, dream daemon, idle frameworks.
version: 1.0
last_updated: 2026-06-29
domain: meta
tokens: ~350
triggers:
  - dreaming daemon
  - run dreaming
  - knowledge frameworks
  - dream daemon
  - idle frameworks
requires_packages: []
reference_files:
  - .agent/dreaming/README.md
  - .agent/dreaming/config.md
pipeline_position: []
---

# Skill: Dreaming Daemon

## When to use

After pipeline runs or weekly digest when you want **creative recombination** grounded in project evidence.

## Rules

- Every premise must cite `source_ref` from run logs or loaded files.
- Frameworks are **hypotheses** until verified (Swiss Cheese or human review).
- Never use dreaming output as manuscript fact.

## Procedure

1. Append run summaries to `.agent/dreaming/run_logs/*.jsonl`.
2. `python 40_operations/scripts/dreaming_daemon.py`
3. Review `.agent/dreaming/frameworks/*.md`.

## Related

- `30_system/docs/THE_MACHINE.md`
- `.cursor/docs/EVIDENCE_CONSISTENCY_PROTOCOL.md`
