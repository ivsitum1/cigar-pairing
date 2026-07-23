---
name: autosci-memory-centric-lifecycle
description: Memory-centric agent layout for full scientific research lifecycle (literature, ideas, experiments, manuscript, review). Use when structuring multi-phase research agents with persistent project memory. Source arXiv 2605.31468 (non-peer-reviewed).
version: 1.0
last_updated: 2026-06-01
domain: engineering
tokens: ~750
triggers:
  - scientific research lifecycle agent
  - autosci memory agent
  - memory centric research agent
  - full research lifecycle orchestration
  - persistent memory scientific agent
requires_packages: []
reference_files:
  - .agent/README.md
conflicts_with: ["agentic-react-os"]
disambiguation: Project memory layout for long research runs; for TAOR/Re-Act OS discipline use agentic-react-os; for clinical SR use meta-analysis; pairs with this repo's .agent/ and context/ folders.
pipeline_position: []
---

# Skill: Memory-centric scientific research lifecycle agent

**Source (preprint):** [arXiv:2605.31468](https://arxiv.org/abs/2605.31468) — AutoSci. Pattern for orchestrating phases with structured persistent memory; not a substitute for human PI oversight or registered protocols.

## When to use

- Multi-month **research project** with agents touching literature, hypotheses, analysis, and manuscript
- Need **structured memory** across phases (not one flat chat log)
- Aligning agent folders with lifecycle stages in this brain repo

## When NOT to use

- Single quick literature lookup → `research-lookup`
- Formal PRISMA/meta-analysis protocol → `meta-analysis`
- Software feature PRD only → grill-me / write-prd chain

## Procedure

1. **Map phases:** Literature → ideation → experiments/analysis → manuscript → revision (adjust to project).
2. **Memory layers (this repo):**
   - Scope/PICO: `30_system/04_documentation/context/main.md`
   - Phase/milestones: `commit.md`; session log: `log.md`
   - Task artifacts: `.agent/task/`
   - Handoffs: `handoff_log.jsonl` + MCP `log_handoff`
3. **Per phase:** Write entry summary to `log.md` before switching subagent (STATISTICS → WRITING, etc.).
4. **Structured stores:** Prefer typed notes (hypothesis, dataset version, figure list) over dumping raw tool output into MEMORY.md.
5. **Retrieval:** On resume, read `.agent/README.md`, `main.md`, last 10 `log.md` lines, active `research_*.md` if any.
6. **Governance:** Human approves phase transitions; agents do not change registered primary outcomes or SAP without explicit user sign-off.
7. **Honesty:** Label AutoSci-inspired layout as architectural pattern; verify claims against user protocol, not the preprint alone.

## Verification

- [ ] Phase boundaries and memory paths documented
- [ ] No post-hoc outcome changes without user approval
- [ ] Swiss Cheese / REFINE still run for critical analyses per pipeline rules

## Related

- `SKILL_arxiv-skill-scout.md`, `30_system/behavior_rules/22_pipeline_and_refinement.md`, `.cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md`

## Semantic graph (auto)

- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
