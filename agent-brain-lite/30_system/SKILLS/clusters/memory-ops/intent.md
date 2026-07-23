---
cluster_id: memory-ops
domain: agentic
parent_layer: harness
related_skills:
  - agentic-react-os
  - notebooklm-research-gate
  - swiss-cheese
last_updated: 2026-07-04
---

# Intent: Memory operations (AutoMem-aligned)

## Legislative intent

Promote **memory operations** to first-class harness actions, separate from domain **task ops**. Inspired by AutoMem ([arXiv:2607.01224](https://arxiv.org/abs/2607.01224)): the agent decides what to encode, when to retrieve, and how to organize — via explicit log/read/write/plan steps — not implicit context stuffing.

**Not to be confused with:** task skills (meta-analysis, manuscript-writing), vector RAG pipelines, or LoRA memory co-processors (rejected in brain repo).

## Memory op vocabulary

| Op | Purpose | Primary artifacts / tools |
|----|---------|---------------------------|
| **log** | Append episodic event without folding | `context_sync --append-log`, `trajectory_lifecycle`, `.cursor/errors/error_log.jsonl`, `handoff_log.jsonl` |
| **read** | Retrieve compact or raw memory for current step | `.agent/MEMORY.md`, `memory_hierarchy/index.json`, `solved_lemmas.jsonl`, MCP filesystem, wiki-query |
| **write** | Persist durable memory with provenance | `context_sync --fold-lemma`, `memory_hierarchy` summaries, wiki-ingest (gated), `MEMORY.md` milestone append |
| **plan** | Set sub-goal / phase before task ops | `.agent/solved_lemmas.jsonl` (pending subgoals), `commit.md`, orchestrator HANDOFF brief |

## In scope

- Memory-as-filesystem layout under `.agent/memory_hierarchy/`
- `--sync-memory-hierarchy` after batch lemma import
- Pairing memory **write** with Swiss gate before global brain promotion
- Trajectory review → memory schema proposals (via gated `self_harness_propose`, not auto-apply)

## Out of scope

- LoRA / fine-tuning memory proficiency (AutoMem loop 2 at weight level)
- Replacing SkillDAG routing with memory ops
- Auto-promote notebook synthesis to CORE memory without research gate
- Clinical memory claims extrapolated from game benchmarks

## Dependencies (SkillDAG)

- depends_on: [agentic-react-os]
- conflicts_with: []

## Success signals

- Every folded lemma has ≥1 provenance pointer in `memory_hierarchy/index.json`
- Memory ops invoked explicitly in long autonomous chains (log before retry, fold after sub-goal)
- Eval: memory-hierarchy tests pass; no UNVERIFIED benchmark in rules prose

## Provenance

- Source: notebooklm (`91614142-…` AutoMemory / AutoMem)
- External ledger: `30_system/docs/notebooklm_user_notebook_91614142_external_verification.json`
- Paper: AutoMem arXiv:2607.01224

## Semantic graph (auto)

- [[AutoMem metamemory skill]]
- [[HORMA hierarchical memory]]
- [[Agent harness memory and skill tree]]
- [[LifeHarness four-layer model]]
- [SKILLS INDEX](../../../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../../../docs/FOLDER_INDEX.md)
