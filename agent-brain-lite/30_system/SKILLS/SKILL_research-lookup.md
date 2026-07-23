---
name: research-lookup
description: Current research facts with cited sources via Consensus MCP (OAuth), PubMed MCP, and web. Use for lookup evidence, recent studies, fact check literature. NOT arXiv skill scout (arxiv-skill-scout), NOT full SR (meta-analysis) or synthesis grid (literature-synthesis).
version: 1.1
last_updated: 2026-06-01
domain: tools
tokens: ~600
triggers:
  - research lookup
  - current evidence
  - recent studies on
  - what does literature say now
  - fact check study claim
requires_packages: []
reference_files:
  - reference/scientific_thinking/pubmed/search_syntax.md
conflicts_with:
  - meta-analysis
  - literature-synthesis
disambiguation: Quick cited lookup via Consensus MCP then PubMed; for formal SR/MA use meta-analysis; for synthesis grid use literature-synthesis (internal evidence agreement table is NOT Consensus.app). For arXiv agent-skill scouting use arxiv-skill-scout. For local reference library (textbooks, clinical handbooks, guidelines already indexed in books_md): use books_rag MCP (search_fused_rag / search_books_answer) as COMPLEMENT — books_rag gives local indexed knowledge, research-lookup gives live web/PubMed; pair them when currency + depth both matter.
pipeline_position: []
---

# Skill: Research lookup

## When to use

- Need **current** evidence on a focused question with citations
- Verify whether a claim is supported by recent literature

## Procedure

1. Clarify PICO or question scope in one sentence.
2. **Consensus MCP** (if enabled in Cursor): broad peer-reviewed search; note relevance metadata and filters (year, human studies, etc.) when useful. If MCP unavailable or returns empty, say so explicitly.
3. **PubMed MCP**: PMIDs, MeSH, known identifiers, and gaps Consensus did not cover; use patterns in `reference/scientific_thinking/pubmed/search_syntax.md`.
4. **Retrieval phase:** gather 3–8 key sources with PMID/DOI/year from MCP results only.
5. **Derivation phase:** for multi-step claims, trace logic across sources explicitly; flag gaps.
6. **Calibration phase:** resolve conflicts between Consensus and PubMed hits; state when evidence is sparse or contradictory.
7. Return one-paragraph synthesis with per-finding tags `[EXTRACTED]` vs `[INFERRED]`.
8. State **search date** and limits (language, date range).

## Verification

- [ ] No fabricated PMIDs/DOIs (especially when Consensus or PubMed returns no hits)
- [ ] Distinguish guidelines vs single studies
- [ ] Say when evidence is sparse or conflicting
- [ ] Do not confuse Consensus.app with literature-synthesis “consensus meter”

## Related

- `SKILL_literature-synthesis.md`, `SKILL_meta-analysis.md`
- Setup: `30_system/docs/CONSENSUS_MCP_SETUP.md`
- Wiki: `20_knowledge/wiki/concepts/Consensus MCP.md`

## Related Hubs

- [[Research lookup skill]]
- [[Skills audit 2026-05]]

## Skill reference graph (auto)

- [[search_syntax]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
