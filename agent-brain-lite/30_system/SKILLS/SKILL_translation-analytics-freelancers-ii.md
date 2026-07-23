---
name: translation-analytics-freelancers-ii
description: Benchmark local/offline LLMs for confidential translation workflows (freelancer/LSP). Use when evaluating on-prem translation models, privacy-sensitive translation QA, translation workflow benchmarks. Source arXiv 2605.31452 (non-peer-reviewed).
version: 1.0
last_updated: 2026-06-01
domain: engineering
tokens: ~650
triggers:
  - local LLM translation benchmark
  - confidential translation workflow
  - offline translation evaluation
  - translation analytics freelancers
  - privacy sensitive translation LLM
requires_packages: []
reference_files: []
conflicts_with: ["document-conversion"]
disambiguation: Offline/local LLM translation benchmarking; for file format conversion only use document-conversion; for academic manuscript translation quality use avoid-ai-formulations + writing skills.
pipeline_position: []
---

# Skill: Local LLM translation workflow benchmark

**Source (preprint):** [arXiv:2605.31452](https://arxiv.org/abs/2605.31452) — Translation Analytics for Freelancers II. Low-barrier analytic methods for translators/LSPs; not peer-reviewed clinical guidance.

## When to use

- User must keep text **on-prem / offline** (no cloud API) for translation or post-editing
- Comparing **local LLMs** for domain-specific translation (legal, medical marketing copy, etc.) with reproducible metrics
- Building a **repeatable evaluation sheet** for freelancer or small LSP tool choice

## When NOT to use

- Clinical trial reporting or journal manuscript methods → METHODOLOGY / WRITING skills
- Simple docx/md conversion → `document-conversion`

## Procedure

1. **Constraints:** Confirm confidentiality requirement, language pair, domain register, and hardware (GPU/RAM).
2. **Corpus:** Fix a small held-out set (50–200 segments) with reference translations or LQA rubric; no patient identifiers in samples.
3. **Models:** List candidate local models/quantizations; record prompt template and decoding params.
4. **Metrics (accessible):** BLEU/chrF optional; add **human LQA** or error taxonomy (adequacy, terminology, confidentiality leak check).
5. **Run matrix:** Model × prompt variant; log latency and failures.
6. **Report:** Table of winners per metric; note trade-offs (speed vs quality); **do not** recommend cloud APIs if user forbade them.
7. **Limitation:** State preprint/source date; recommend expert human review for publishable or regulated text.

## Verification

- [ ] Confidentiality constraint explicit in report
- [ ] No fabricated benchmark numbers
- [ ] No clinical dosing or treatment claims

## Related

- `SKILL_arxiv-skill-scout.md`, `SKILL_document-conversion.md`

## Semantic graph (auto)

- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
