# NotebookLM grill prompts — Relation-Conditioned slice

**Notebook:** Relation-Conditioned Multimodal Learning for Semantic Representations  
**ID:** `b4be6608-180d-4619-862e-9ddbefa92314`  
**URL:** https://notebooklm.google.com/notebook/b4be6608-180d-4619-862e-9ddbefa92314

Use with Playwright (`outputs/notebooklm/_query_user_notebook.py` pattern) or MCP `ask_question` after auth.

---

## Grill questions (14)

1. List every source with title, type (paper/YouTube/web), URL or arXiv id, and one-line topic.
2. For each paper, extract 5–8 main claims. Tag each FACT, OPINION, DEMO, or BENCHMARK.
3. **SkillLens:** Define the four layers (Policy, Strategy, Procedure, Primitive) with paper quotes. How do they differ from flat skill libraries?
4. **SkillLens:** Describe verifier actions (ACCEPT, DECOMPOSE, REWRITE, SKIP). When does each fire?
5. **SkillLens:** Explain degree-corrected random walk retrieval. What graph edges exist between skill units?
6. **SkillLens:** What is dual-registry evolution? What updates on failure — agent registry, verifier registry, or both?
7. **LARGER:** Define Lexically Anchored Structural Localization. What is the agent loop integration point?
8. **LARGER:** How are sidecar JSON files structured? What edge types and confidence weights are used?
9. **LARGER:** Describe commit-aware incremental graph update. What speedup is claimed and under what conditions?
10. **Rcml:** What requires model weights vs what could be approximated with prompt-level relation conditioning?
11. Map SkillLens and LARGER to harness layers: environment contract, procedural skill, action realization, trajectory regulation.
12. Where do the three papers disagree? Which claims lack code or reproducible benchmarks?
13. Top 10 changes for a Cursor agent-rules repo: P0 (rules/MCP/skills), P1 (scripts), P2 (research). Target artifact + acceptance test each.
14. Build a table: claim, paper, arXiv id, reproducible Y/N, overlaps with SkillRAE/SkillDAG/Graphify.

---

## Playwright command

```bash
python outputs/notebooklm/_query_user_notebook.py
# Or extend notebooklm_grill_playwright.py:
python 40_operations/scripts/notebooklm_grill_playwright.py \
  --notebook-url "https://notebooklm.google.com/notebook/b4be6608-180d-4619-862e-9ddbefa92314" \
  --needle "Relation-Conditioned" \
  --output outputs/notebooklm/relation_conditioned_query_batch.json
```

---

## Gate pipeline

```bash
python 40_operations/scripts/notebooklm_bridge.py export-normalize \
  --input outputs/notebooklm/user_notebook_query.json \
  --output outputs/notebooklm/relation_conditioned_normalized.json \
  --notebook-id b4be6608-180d-4619-862e-9ddbefa92314

python 40_operations/scripts/notebooklm_bridge.py gate-report \
  --input outputs/notebooklm/user_notebook_query.json \
  --output outputs/notebooklm/relation_conditioned_gate_report.json
```

Cross-check: `30_system/docs/notebooklm_relation_conditioned_external_verification.json`

---

## Dedup notebooks

| Notebook | ID | PRD |
|----------|-----|-----|
| Geometry of Intelligence | `7c31671a-37df-4227-ac76-3ef2f5346d84` | `prd_geometry_incorporation.json` |
| SkillDAG | `48a6afa2-97d8-44f4-8a41-c87d2ea0b650` | `prd_skilldag_incorporation.json` |
| **This notebook** | `b4be6608-180d-4619-862e-9ddbefa92314` | `prd_relation_conditioned_incorporation.json` |

## Semantic graph (auto)

- [[Relation-conditioned harness]]
- [[SkillDAG]]
- [[Behavior rules hub]]
- [30 system INDEX](../indexes/30_system_INDEX.md)
- [FOLDER INDEX](../FOLDER_INDEX.md)
