---
cluster_id: harness
domain: agentic
parent_layer: harness
related_skills:
  - notebooklm-research-gate
  - agentic-react-os
  - swiss-cheese
last_updated: 2026-07-04
---

# Intent: Agent harness (runtime)

## Legislative intent

Define the **runtime layer** that executes procedural scaffolds: MCP tools, hooks, memory trim/fold, ReAct loops, handoff logging, and gated self-improvement. Distinct from scaffold (SKILL_*.md workflows) and SkillDAG (routing).

## In scope

- MCP execution inside ReAct/TAOR loop
- `context_sync --fold-lemma` and `.agent/memory_hierarchy/`
- `memory-ops` cluster (log/read/write/plan as first-class harness actions)
- `failure_patterns_bridge` → self_harness_propose (human gate every 3rd iteration)
- LifeHarness L3–L4 mapping

## Out of scope

- Autonomous `.cursorrules` / `behavior_rules` rewrite
- Flat import of hundreds of external skills
- Replacing SkillDAG routing with skill tree flat hierarchy

## Dependencies (SkillDAG)

- depends_on: [notebooklm-research-gate]
- conflicts_with: []

## Success signals

- memory_hierarchy index has provenance-linked nodes after fold-lemma
- self_harness proposals require human approval on iterations 3, 6, 9…
- Eval: `self-harness-gate`, `memory-hierarchy`

## Provenance

- Source: NotebookLM Harness Memory v2 (`f9554fae-…`)
- External ledger: `30_system/docs/notebooklm_harness_v2_external_verification.json`
- Papers: Self-Harness 2606.09498, HORMA 2606.11680, HIPIF 2606.10507, Agents-K1 2606.13669

## Semantic graph (auto)

- [[Agent harness memory and skill tree]]
- [[LifeHarness four-layer model]]
- [[Failure patterns registry]]
- [[NotebookLM research gate]]
