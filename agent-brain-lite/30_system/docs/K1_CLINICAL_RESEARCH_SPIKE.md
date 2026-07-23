# K1 clinical knowledge extraction — research spike (P2)

**Status:** spike only — primary paper VERIFIED 2026-07-04  
**User decision (2026-06-16):** clinical priority over generic K1 rollout  
**Notebook source:** Harness Memory v2 (`f9554fae-…`); prior v1 `86aaaf0e-…`

## Primary source [VERIFIED]

- **Paper:** [Agents-K1: Towards Agent-native Knowledge Orchestration](https://arxiv.org/abs/2606.13669) (arXiv:2606.13669)
- **Model:** [InternScience/Agents-K1](https://huggingface.co/InternScience/Agents-K1) (4B, Qwen3-4B-Instruct + GRPO)
- **Scope:** Scientific document → agent-native knowledge graph (entities, relations, multimodal evidence, citation lineage)

## Question

Should agent-rules add a **K1-style structured extractor** for clinical sources (guidelines, SR papers, trial reports) beyond existing `books_rag` + wiki ingest?

## Current coverage

| Capability | Path | Gap |
|------------|------|-----|
| Textbook/handbook RAG | `books_rag` MCP, `20_knowledge/wiki/sources/books_md/` | Indexed prose, not causal graph |
| Wiki ingest | `notebooklm_bridge.py wiki-ingest`, wiki-ingest skills | Narrative pages, manual wikilinks |
| Live literature | `research-lookup`, PubMed MCP | Currency, not local graph |
| Clinical writing QA | medical_research skill references | Manuscript, not knowledge graph |

## K1 claims from notebook [VERIFIED primary paper]

- Agents-K1: 4B GRPO-trained extractor + multimodal parser + graphanything CLI ([arXiv:2606.13669](https://arxiv.org/abs/2606.13669))
- Agent-native knowledge orchestration vs flat GraphRAG triplets
- Scholar-KG scale (2.46M papers); clinical subset TBD with PHI review

## Spike tasks

1. **Primary source** — [VERIFIED] arXiv:2606.13669; add to `notebooklm_user_notebook_91614142_external_verification.json`
2. **Corpus sample** — 3 clinical PDFs already in reference library (guideline + SR + trial abstract)
3. **Compare** — manual claim extraction vs `books_rag` answer vs K1 (if tool available)
4. **Decision matrix**

| Criterion | books_rag | K1 pipeline |
|-----------|-----------|-------------|
| Guideline dose tables | ? | ? |
| Citation lineage | weak | claimed strong |
| Setup cost | low (exists) | high |
| PHI risk | local | depends on deployment |

## Acceptance for GO to implementation

- [x] Primary paper URL VERIFIED (arXiv:2606.13669)
- [ ] Sample extraction beats books_rag on **citation lineage** or **conditional claims** on ≥2/3 docs
- [ ] Privacy review: no cloud upload of PHI without BAA
- [ ] Wiki schema for structured claims (`CLAIM-EXTRACTION.md` alignment)

## Reject if

- K1 only improves generic triplets without clinical conditional structure
- `books_rag` + obsidian literature gates sufficient for user's SR workflow

## Outputs (this spike)

- This document
- Wiki concept: [[Agent-native clinical knowledge]]
- Backlog item HS-9 in `.agent/task/harness_skilltree_incorporation_backlog.md`
