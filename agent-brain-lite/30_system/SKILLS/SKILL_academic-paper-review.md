---
name: academic-paper-review
description: Structured peer-review-style critique of papers, preprints, or PDFs. Use for review, analyze, critique, summarize research article, arXiv, peer review prep. NOT for IMRaD structure-only check (manuscript-structure) or narrative lit synthesis (literature-synthesis).
version: 1.0
last_updated: 2026-05-18
domain: writing
tokens: ~900
triggers:
  - review this paper
  - peer review
  - critique paper
  - analyze research article
  - academic paper review
  - arXiv review
requires_packages: []
reference_files:
  - reference/scientific_critical_thinking/validity_framework.md
  - reference/medical_research/claim-strength-calibrator/hard-rules.md
conflicts_with:
  - manuscript-structure
  - literature-synthesis
disambiguation: Use for external paper critique or peer-review draft; for own manuscript section check use manuscript-structure; for synthesizing multiple papers use literature-synthesis.
pipeline_position: []
---

# Skill: Academic paper review

## When to use

- User provides a paper (PDF, URL, preprint) and wants structured critique
- Preparing referee report or internal journal club review
- Assessing methodology, novelty, and limitations of **one** paper

## Prerequisites

- Full text or sufficient excerpt; if only abstract, state limits explicitly
- Domain context from user when clinical (doses, population) — do not invent

## Procedure

1. **Metadata:** title, authors, venue, year, design type.
2. **Claims table:** list main claims with evidence strength (strong/moderate/weak) per `reference/medical_research/claim-strength-calibrator/hard-rules.md`.
3. **Methodology:** apply `reference/scientific_critical_thinking/validity_framework.md` (design fit, biases, statistics).
4. **Strengths / weaknesses:** evidence-based bullets; no ad hominem.
5. **Literature position:** only cite verifiable prior work; use MCP/web search when needed.
6. **Recommendations:** actionable revisions; distinguish major vs minor.

## Output format

- Executive summary (≤150 words)
- Detailed sections: Summary | Strengths | Weaknesses | Methodology | Significance | Recommendations
- Tag claims `[EXTRACTED]` from paper vs `[INFERRED]` critique

## Verification

- [ ] No fabricated citations or results
- [ ] Causal language matched to design
- [ ] Limitations acknowledged for reviewer uncertainty

## Related

- `SKILL_manuscript-structure.md`, `SKILL_literature-synthesis.md`, `SKILL_swiss-cheese.md`

## Related Hubs

- [[Academic paper review skill]]
- [[Skills audit 2026-05]]
- [[Skill registry]]
- [[skills-auto-detect]]

## Skill reference graph (auto)

- [[validity_framework]]
- [[hard-rules]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
