# Conversational Cognition (full reference)

**Version:** 1.0 | **Last Updated:** 2026-06-28  
**Active slice:** `.cursor/rules/55_conversational_cognition.mdc`

## Purpose

Reduce mechanical, over-defensive agent prose while keeping anti-hallucination standards. Targets two failure modes:

1. **Phantom denial** — negating claims nobody made (often from safety over-correction).
2. **Syntactic inflation** — sounding scholarly by length and hedging instead of precision.

## External grounding

- Positive framing in instructions outperforms negation-heavy rules (Cogniti; cepunkt/playground Mantras).
- Explicit "think step by step" can degrade stability vs state-focused control (SAAM, stawils/saam).
- AI academic prose tends toward noun-heavy complexity and pseudo-commitment (PLOS One 2025; Uncanny Semantics 2025).
- Algorithmic dual-hedging inflates defensive tone (arXiv 2605.13055).

## Workflow before send

1. Restate the user question in one line (internal).
2. Draft answer-first output.
3. Scan for phantom denials: remove negations with no prior claim in context.
4. Apply channel rules (chat vs manuscript).
5. Run honesty self-check internally; surface `[BLANK]` only for real gaps.

## Manuscript cross-link

For journal-facing text, apply **Surgical brevity** in `03_scientific_writing.md` and `writing-avoid-ai.mdc` after conversational checks.

## Eval hooks

Regression cases in `30_system/SKILLS/evals/conversational-cognition.json`.
