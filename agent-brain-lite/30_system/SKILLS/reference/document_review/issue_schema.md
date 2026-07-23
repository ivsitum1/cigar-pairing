# Document review issue schema (condensed)

Adapted from external `document-review` skill. For grants, reports, PDF/DOCX/PPTX/XLSX.

## Issue types

- `spelling_grammar` — spell-checker catchable
- `narrative_logic` — contradictions, timeline, tautology (needs meaning)
- `non_public_info` — confidential leaks
- `verify_public_data` — external fact check (URLs only from search, never fabricate)
- `numerical_consistency` — internal math (verify with calculation)

## Severity

- `high` — wrong decisions, legal/PII, material false facts
- `medium` — credibility (contradictions, math errors)
- `low` — professionalism (typos)

## Claims workflow

Extract `claim:N` with status `unverified|verified|refuted|inconclusive` before writing issues.

## Ground rules

- No repo paths in user-facing deliverables
- Never fabricate URLs for verification

## Parent skills (auto)

- [[SKILL_document-review]]
