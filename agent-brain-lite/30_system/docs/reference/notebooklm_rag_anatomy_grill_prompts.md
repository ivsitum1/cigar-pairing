# NotebookLM grill prompts — RAG Anatomy, Harness, Workflow

**Notebook ID:** `33feafbc-a75e-4e05-9eff-ae5394a08f05`  
**URL:** https://notebooklm.google.com/notebook/33feafbc-a75e-4e05-9eff-ae5394a08f05

## Extraction (canonical)

```bash
python 40_operations/scripts/notebooklm_grill_playwright.py \
  --notebook-url "https://notebooklm.google.com/notebook/33feafbc-a75e-4e05-9eff-ae5394a08f05"
```

Output: `outputs/notebooklm/rag_anatomy_query_batch.json`  
Then: `notebooklm_bridge.py export-normalize` → `gate-report`.

Requires Chrome profile: `%USERPROFILE%\.notebooklm\profiles\default\browser_profile`.

## Grill questions (14)

Use in order; reuse chat session when using MCP `ask_question`.

1. List every source in this notebook. For each YouTube source give: exact title, URL if present, and a one-line topic label.
2. For each YouTube video, extract 5-8 main claims as bullets. After each claim add a short quote from the transcript and tag FACT, OPINION, DEMO, or BENCHMARK.
3. Across all sources, describe the full RAG pipeline stages mentioned: ingest, chunking, embedding, indexing, retrieval, reranking, fusion, and citation grounding. Separate operational steps from marketing language.
4. What hybrid retrieval patterns are discussed (sparse+dense, graph RAG, multi-hop)? For each, what problem does it solve and what are the stated limitations?
5. What token or context cost claims appear about RAG? List each number with the video/source it came from.
6. How do sources define runtime harness vs the language model core? Map to environment contract, procedural skill, action realization, trajectory regulation if possible.
7. What tool-contract or MCP failure modes and deterministic prescreen fixes are recommended?
8. What is said about skills as operators (SkillRAE), self-evolving skills (SkillOpt), and edit budgets?
9. What multi-agent debate, HITL, or deep-research calibration workflows are described?
10. Where do sources disagree? What claims lack code, paper, or reproducible benchmarks?
11. List the top 10 changes an agent-rules workspace should make, ranked P0 (rules/MCP/skills), P1 (scripts), P2 (research only). For each: target artifact, acceptance test, dependencies.
12. Build a table of papers, GitHub repos, benchmarks cited: claim, source video title, external ref, reproducible Y/N.
13. Summarize harness-specific recommendations that differ from generic prompt engineering.
14. What wiki or knowledge-graph RAG patterns (wikilinks, orphans, multi-hop) are recommended for long-running agent memory?

## Gate

External ledger: `30_system/docs/notebooklm_rag_anatomy_external_verification.json`  
Do not cite Opus 4.8 leaderboard numbers or demo token totals (3.1M) in rules/skills without primary sources.

## Semantic graph (auto)

- [[RAG anatomy harness workflow]]
- [[SkillDAG]]
- [[Behavior rules hub]]
- [30 system INDEX](../indexes/30_system_INDEX.md)
- [FOLDER INDEX](../FOLDER_INDEX.md)
