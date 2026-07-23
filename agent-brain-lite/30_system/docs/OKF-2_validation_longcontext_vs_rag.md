# OKF-2 validation: long-context vs RAG (production week 1)

**Policy:** `context-optimization.mdc` § Academic corpus  
**Gate:** okf-knowledge GO | **Issue:** OKF-2

## Decision tree

```
Task needs evidence from literature?
├─ Single PDF/paper, ≤~80k tokens after compress → pdf MCP read_pdf (full twin) + thread
├─ Textbook/handbook corpus, multi-hop → books_rag search_fused_rag
├─ Wiki concepts + graph → wiki-query / context pack (20_knowledge/wiki/)
└─ Meta-analysis PDF set + PRISMA → hybrid (see meta_analysis_pdf_trace.md)
```

## Smoke test A — single PDF (long-context path)

**When:** One primary paper for Methods citation or full-text claim check.

1. `read_pdf` with `auto=true` on project PDF under `01_input/` or `20_knowledge/`
2. Optional: `AGENT_CONTEXT_COMPRESS=1` if tool output >8k tokens prose equivalent
3. **Pass:** Agent cites page/section from twin without chunk-boundary hallucination
4. **Fail signal:** Claim spans two distant sections and twin excerpt is truncated → fall back to `pdf_evidence` crop or smaller scope question

## Smoke test B — books_rag (chunk path)

**When:** Statistics textbook lookup, guideline comparison across chapters.

1. MCP `books_rag` → `search_fused_rag` with narrow query
2. **Pass:** Retrieved span answers question; wikilink to concept note if recurring
3. **Fail signal:** Multi-hop synthesis needed across 3+ books → wiki synthesis or serial long-context loads, not bigger k

## Smoke test C — contrast (same question, both paths)

Pick one clinical stats question (e.g. "Welch vs Student t-test default").

| Path | Tool | Record |
|------|------|--------|
| Long-context | Load one chapter PDF via pdf MCP | Answer + token estimate |
| RAG | books_rag fused search | Answer + chunk IDs |

**Expected:** Answers align on facts; RAG uses less context, long-context preserves cross-paragraph nuance.

## Log template

```markdown
## OKF-2 smoke YYYY-MM-DD
- Question:
- Path used:
- Tokens (approx):
- Verdict: pass | fail | hybrid_needed
- Notes:
```

Append results to `.agent/task/OKF-2_smoke_log.md` (create on first run).

## Do not

- Remove books_rag index because OKF notebook suggests anti-RAG for coding
- Load entire textbook library into one thread without compress hook
