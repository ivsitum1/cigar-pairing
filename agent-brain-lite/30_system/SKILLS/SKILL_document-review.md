---
name: document-review
description: Structured review of PDF, DOCX, PPTX, XLSX for spelling, logic, confidentiality, public facts, and internal math. Use for fact-check document, audit report, proofread deck. NOT legal contract redlines (legal-contract-review) or journal IMRaD (manuscript-structure).
version: 1.0
last_updated: 2026-05-18
domain: tools
tokens: ~850
triggers:
  - document review
  - fact-check document
  - audit this PDF
  - proofread report
  - review deck
requires_packages: []
reference_files:
  - reference/document_review/issue_schema.md
conflicts_with:
  - legal-contract-review
  - manuscript-structure
disambiguation: Use for factual/structural audit of business or technical documents; for HR/EU contracts use legal-contract-review; for scientific manuscript structure use manuscript-structure.
pipeline_position: []
---

# Skill: Document review

## When to use

- User attaches or points to a document needing structured QA
- Fact-checking numbers and public claims in reports or slides
- Not for clinical manuscript peer review (use `academic-paper-review`)

## Procedure

1. **Scope:** confirm issue types requested (default: all five in `reference/document_review/issue_schema.md`).
2. **Sections:** divide document into page/sheet ranges; no gaps.
3. **Claims:** extract verifiable claims; mark status after search/calculation.
4. **Issues:** each with type, severity, verbatim `original_text`, fix suggestion.
5. **Deliver:** summary table + issue list; tell user to download annotated copy if tooling produced one.

## Honesty

- `verify_public_data`: only URLs from actual search results
- `numerical_consistency`: show calculation for refuted math
- Tag `[BLANK]` when source unavailable

## Verification

- [ ] No fabricated URLs
- [ ] Cascade errors linked via `root_issue_id` when applicable
- [ ] Clinical/regulatory claims flagged for human expert if high stakes

## Related

- `SKILL_legal-contract-review.md`, `SKILL_academic-paper-review.md`

## Related Hubs

- [[Document review skill]]
- [[Skills audit 2026-05]]
- [[Skill registry]]

## Skill reference graph (auto)

- [[issue_schema]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
