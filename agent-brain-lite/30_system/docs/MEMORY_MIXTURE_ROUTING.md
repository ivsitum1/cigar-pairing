# Memory mixture routing

Extends [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) with explicit substore routing (Beyond Intelligence / MemFail slice).

## Substores

| Substore | Path / service | Query types | Write policy |
|----------|----------------|-------------|--------------|
| **Episodic trajectory** | `90_archive/artifacts/*/trajectory.jsonl`, `.agent/memory/trajectory_session.json` | Tool failures, routing gaps, session replay | Append-only; primary evidence |
| **SQLite observations** | `.agent/memory/memory.db` via `memory_engine` | Session recall, lifecycle events | Ingest hook; dedup by event hash |
| **Wiki distilled** | `20_knowledge/wiki/` | Concepts, procedures, cross-session knowledge | Wiki skills; human-gated promote |
| **Books RAG** | MCP `books_rag`, `20_knowledge/wiki/sources/books_md/` | Textbook/guideline lookup | Index rebuild only via `books_rag_verify.py` |
| **Verifier ledger** | `.agent/memory/verifier_usage_ledger.jsonl` | Skill routing corrections, relation tags | Hook append; PHI sanitize |

## Routing table

| User / agent need | Primary | Fallback |
|-------------------|---------|----------|
| "What did I do last session on X?" | trajectory | memory.db timeline |
| "What does the textbook say about Y?" | books_rag | research-lookup MCP |
| "What is our procedure for Z?" | wiki + SKILL registry | memory.db search |
| "Why did verifier SKIP skill S?" | verifier ledger | skill-verifier-gate evals |
| Clinical dosing / PHI | **Do not route to wiki** | User protocol only |

## Failure mode tags

Ingest tags observations with `failure_mode:{summary|storage|retrieval|unknown}` per MemFail decomposition (`memory_engine/compression.py`).

## Episodic-first policy

See [TRAJECTORY_RL_POLICY.md](TRAJECTORY_RL_POLICY.md#episodic-first-policy): do not force abstract consolidation into `.agent/MEMORY.md` without milestone or eval gate.

## MemFail adapter

`40_operations/python/memory/memfail_adapter.py` exposes `store_conversation`, `retrieve_memories`, `get_all_memories` for benchmark smoke — not production replacement of `memory_engine`.
