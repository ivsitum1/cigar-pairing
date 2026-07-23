# Hypothesis generation workflow

Use when research questions are still exploratory (before locking `research-spec.json`).

## Steps

1. **State competing hypotheses** (at least two plausible mechanisms).
2. **Operationalize:** what data would distinguish H1 vs H2?
3. **Falsifiability:** specify what result would weaken each hypothesis.
4. **Map to design:** RCT vs cohort vs descriptive; label causal claims accordingly.
5. **Pre-register** primary outcome and analysis in spec/SAP before unblinded looks.

## PICO alignment

| Element | Question |
|---------|----------|
| P | Who is studied? |
| I/E | Exposure or intervention? |
| C | Comparator? |
| O | Primary outcome at what time? |

## Handoff

When hypotheses and design are stable → `SKILL_write-research-spec` or methodology subagent.

Do not substitute example drugs/doses from rules for user protocol facts.

## Parent skills (auto)

- [[SKILL_research-grill-me]]
- [[SKILL_write-research-spec]]

## Related playbooks (auto)

- [[literature_review_phases]]
- [[database_strategies]]
- [[citation_styles]]
- [[peer_review_checklist]]
- [[evaluation_framework]]
