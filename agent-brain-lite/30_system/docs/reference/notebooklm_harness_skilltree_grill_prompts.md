# NotebookLM grill prompts — Agent Harness Memory SkillTree

**Notebook ID:** `86aaaf0e-eeeb-4735-be0f-9019ff0ba075`  
**Library ID:** `agent-harness-memory-skilltree`  
**URL:** https://notebooklm.google.com/notebook/86aaaf0e-eeeb-4735-be0f-9019ff0ba075

## Extraction

**MCP (preferirano):** `ask_question` s `notebook_url`; reuse `session_id`; prefer `source_format: none` if citation overlay blocks UI.

```bash
python 40_operations/scripts/assemble_harness_skilltree_batch.py
python 40_operations/scripts/notebooklm_bridge.py export-normalize \
  --input outputs/notebooklm/harness_skilltree_query_batch.json \
  --output outputs/notebooklm/harness_skilltree_normalized.json
python 40_operations/scripts/notebooklm_bridge.py gate-report \
  --input outputs/notebooklm/harness_skilltree_normalized.json \
  --output outputs/notebooklm/harness_skilltree_gate_report.json
```

Output batch: `outputs/notebooklm/harness_skilltree_query_batch.json`

## Grill questions (14)

1. List every source: title, URL, type, one-line topic; total count.
2. Central thesis in 3 sentences; actionable vs background-only for harness work.
3. Define: scaffold, harness, skill tree, HORMA, HIP-If, Socratic PO, self-harness, K1; hierarchical relations.
4. Step-by-step operational workflows (memory, planning, tool loops, self-correction) with triggers and stop conditions.
5. Boundaries and anti-patterns (self-evolve without gate, flat skills, context pollution, LLM-as-judge).
6. Integration seams: MCP, procedural skills, hooks, wiki/graph; file-level artifacts.
7. Metrics, eval protocols, pass/fail gates (TerminalBench, token savings, planning, skill-tree routing).
8. Experimental vs production-ready recommendations.
9. Cross-check vs SkillDAG, LifeHarness, Geometry, Humanize notebooks.
10. P0/P1/P2 ranked changes for agent-rules workspace.
11. Risks: token budget, hallucination, ethics, AI bubble.
12. MVP vs full rollout; test plan and eval seeds.
13. Open questions for user confirmation.
14. Final delta table: concept | covered/partial/gap/reject | action | risk.

## Gate

External ledger: `30_system/docs/notebooklm_harness_skilltree_external_verification.json`  
Gate report: `outputs/notebooklm/harness_skilltree_gate_report.json`

**Policy (user-confirmed 2026-06-16):**
- Self-harness proposals: human gate every **3rd** iteration
- K1: clinical priority research spike before implementation
- Reward decay: implement in skill_rerank / verifier eval

## Related notebooks (dedup)

| Notebook | Dedup |
|----------|-------|
| SkillDAG | Tree = grouping; DAG = routing |
| Geometry of Intelligence | Model-native / LifeHarness L1–L4 |
| Humanize AI | No substantive overlap |

## Semantic graph (auto)

- [[Agent harness memory and skill tree]]
- [[SkillDAG]]
- [[Behavior rules hub]]
- [30 system INDEX](../indexes/30_system_INDEX.md)
- [FOLDER INDEX](../FOLDER_INDEX.md)
