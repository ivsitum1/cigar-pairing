---
name: longtracerl-long-context-reason
description: Long-context agent evaluation with tiered distractors and rubric-style process rewards. Use when designing or reviewing long-context RL/benchmarks for search agents. Source arXiv 2605.31584 (non-peer-reviewed). NOT clinical evidence.
version: 1.0
last_updated: 2026-06-01
domain: engineering
tokens: ~700
triggers:
  - long context reasoning agent
  - longtracerl
  - rubric reward agent trajectory
  - tiered distractors benchmark
  - long context RL agent evaluation
requires_packages: []
reference_files: []
conflicts_with: []
disambiguation: Engineering pattern from LongTraceRL preprint; for quick literature on a clinical question use research-lookup; for general Re-Act discipline use agentic-react-os.
pipeline_position: []
---

# Skill: Long-context agent reasoning (LongTraceRL-inspired)

**Source (preprint):** [arXiv:2605.31584](https://arxiv.org/abs/2605.31584) — LongTraceRL (THU-KEG). Methods are illustrative; verify against paper/repo before production use.

## When to use

- Designing or critiquing **long-context** benchmarks for **search agents**
- User wants **process-level** supervision (entity/rubric checks), not outcome-only scoring
- Building training/eval contexts with **hard distractors** (read-but-not-cited vs never-opened docs)

## When NOT to use

- Clinical or biomedical evidence synthesis → `research-lookup`
- General agent OS checkpoints → `agentic-react-os`

## Procedure

1. **Scope:** Define task (multi-hop QA, retrieval, tool-use trace) and max context length.
2. **Context construction (tiered distractors):**
   - Gold evidence documents (cited in correct trace).
   - **High confusability:** documents the agent opened but did not cite.
   - **Low confusability:** documents only in search results, never opened.
3. **Gold reasoning chain:** List entities/steps per hop (knowledge-graph walk or manual spec).
4. **Rubric reward design:**
   - Final answer correctness gate.
   - Entity-level alignment to gold chain on **correct-answer** trajectories only (positive-only to reduce reward hacking).
5. **Eval:** Run on held-out long-context suites; report per-tier distractor ablation.
6. **Honesty:** Label outputs as design/review notes; cite arXiv + GitHub if implementing: `https://github.com/THU-KEG/LongTraceRL`.

## Verification

- [ ] Distractor tiers explicitly documented
- [ ] No clinical treatment claims from this workflow
- [ ] Process rubric separate from final-answer-only scoring

## Related

- `SKILL_arxiv-skill-scout.md`, `SKILL_agentic-react-os.md`

## Semantic graph (auto)

- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
