# NotebookLM grill prompts — SkillDAG

**Notebook ID:** `48a6afa2-97d8-44f4-8a41-c87d2ea0b650`  
**URL:** https://notebooklm.google.com/notebook/48a6afa2-97d8-44f4-8a41-c87d2ea0b650

## Extraction (canonical)

**MCP (preferirano):** `ask_question` s `notebook_url` iznad; reuse `session_id` za sva 14 pitanja; `source_format: json` za citate.

**CLI chat export (dopuna, ne zamjena za grill):**

```bash
python 40_operations/scripts/notebooklm_consumer_extract.py export-chat \
  --notebook "48a6afa2-97d8-44f4-8a41-c87d2ea0b650" \
  --output "outputs/notebooklm/skilldag_chat_history.json"
```

**Normalizacija + gate:**

```bash
python 40_operations/scripts/notebooklm_bridge.py export-normalize \
  --input outputs/notebooklm/skilldag_query_batch.json \
  --output outputs/notebooklm/skilldag_normalized.json

python 40_operations/scripts/notebooklm_bridge.py gate-report \
  --input outputs/notebooklm/skilldag_normalized.json \
  --output outputs/notebooklm/skilldag_gate_report.json
```

Output batch: `outputs/notebooklm/skilldag_query_batch.json`

Requires NotebookLM auth: MCP `setup_auth` or `python -m notebooklm.notebooklm_cli auth login`.  
Playwright profile (if used): `%USERPROFILE%\.notebooklm\profiles\default\browser_profile`.

## Grill questions (14)

Use in order; reuse chat session when using MCP `ask_question`.

1. List every source in this notebook. For each source give: exact title, URL if present, source type (YouTube, PDF, web, pasted text), and a one-line topic label.
2. For each source, extract 5–8 main claims as bullets. After each claim add a short quote and tag FACT, OPINION, DEMO, or BENCHMARK.
3. How do the sources define SkillDAG (or skill dependency graph)? What is a node, edge, cycle, and valid topological order? Give definitions used in the notebook.
4. How does SkillDAG differ from a flat skill list, from SkillRAE subunit decomposition, and from MUSE/SkillOpt if mentioned?
5. What routing rules are described: when must skill A load before skill B; which branches can run in parallel vs serial; how are conflicts resolved?
6. What evaluation or gate nodes appear in a skill DAG (pass/fail, Swiss Cheese, research gate, human-in-the-loop)? Where must execution stop?
7. Map SkillDAG concepts to harness layers if possible: environment contract, procedural skill, action realization, trajectory regulation (LifeHarness or equivalent).
8. Are named pipeline sequences (e.g. grill-me → write-prd → prd-to-issues → ralph-loop) represented as DAGs in the sources? How should they be encoded?
9. What token or context budget rules apply per DAG branch or per parallel fan-out? List each number with its source.
10. Where do sources disagree? Which claims lack code, papers, or reproducible benchmarks?
11. List the top 10 changes an agent-rules workspace should make, ranked P0 (rules/MCP/skills), P1 (scripts), P2 (research only). For each: target artifact, acceptance test, dependencies.
12. Build a table of papers, GitHub repos, and benchmarks cited: claim, source title, external reference, reproducible Y/N.
13. What recommendations are specific to Cursor, MCP, or file-based agent harnesses (not generic prompt engineering)?
14. What wiki or knowledge-graph patterns (wikilinks, orphans, multi-hop, cross-linking) are recommended for skill or pipeline memory?

## Gate

External ledger: `30_system/docs/notebooklm_skilldag_external_verification.json`  
Gate report: `outputs/notebooklm/skilldag_gate_report.json`

Do not cite benchmark percentages or token savings in rules/skills without primary sources and local eval.  
Do not reopen completed Geometry or RAG Anatomy PRD issues unless SkillDAG introduces a genuine conflict.

## Related notebooks (dedup)

| Notebook | ID | Dedup note |
|----------|-----|------------|
| Geometry of Intelligence | `7c31671a-37df-4227-ac76-3ef2f5346d84` | SkillRAE, model-native — map overlap in delta doc |
| RAG Anatomy | `33feafbc-a75e-4e05-9eff-ae5394a08f05` | RAG/harness — map overlap in delta doc |

## Semantic graph (auto)

- [[SkillDAG]]
- [[Behavior rules hub]]
- [30 system INDEX](../indexes/30_system_INDEX.md)
- [FOLDER INDEX](../FOLDER_INDEX.md)
