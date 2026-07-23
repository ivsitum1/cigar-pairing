# NotebookLM grill prompts — Strategic RAG Chunking

**Notebook ID:** `cea806f1-982c-4666-b760-a8237d615eb5`  
**URL:** https://notebooklm.google.com/notebook/cea806f1-982c-4666-b760-a8237d615eb5

## Extraction

```bash
python 40_operations/scripts/assemble_rag_chunking_batch.py
python 40_operations/scripts/notebooklm_bridge.py export-normalize \
  --input outputs/notebooklm/rag_chunking_query_batch.json \
  --output outputs/notebooklm/rag_chunking_normalized.json
python 40_operations/scripts/notebooklm_bridge.py gate-report \
  --input outputs/notebooklm/rag_chunking_normalized.json \
  --output outputs/notebooklm/rag_chunking_gate_report.json
```

## Grill questions (14)

1. List every source: title, type, one-line topic; total count.
2. Central thesis in 3 sentences; actionable vs background-only for RAG ingest.
3. Define: parent-child chunking, contextual retrieval, layout-aware splitting, metadata filtering, late chunking.
4. Step-by-step corpus ingest workflow with chunk sizes, parent resolution, and embed framing.
5. Boundaries and anti-patterns (fixed char splits, orphan chunks, version collision, token bloat).
6. Integration seams: books_rag, wiki ingest, TGS, fused_rag; file-level artifacts.
7. Metrics and eval: recall@k, parent resolve rate, metadata coverage, ingest cost.
8. Experimental vs production-ready recommendations.
9. Cross-check vs RAG Anatomy, Geometry, Harness notebooks.
10. P0/P1/P2 ranked changes for agent-rules workspace.
11. Risks: token budget, stale metadata, wrong parent context.
12. MVP vs full rollout; test plan and eval seeds.
13. Open questions for user confirmation.
14. Final delta table: concept | covered/partial/gap/reject | action | risk.

## Gate

External ledger: `30_system/docs/notebooklm_rag_chunking_external_verification.json`  
Gate report: `outputs/notebooklm/rag_chunking_gate_report.json`

## Related notebooks (dedup)

| Notebook | Dedup |
|----------|-------|
| RAG Anatomy (`33feafbc`) | Pipeline stages; chunking extends corpus half |
| Geometry | TGS/fused — no duplicate chunk PRD |
| Harness SkillTree | HORMA memory ≠ chunking |
