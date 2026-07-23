# Scholarly evaluation framework

## Milestone pass criteria (`research-spec.json`)

Each item should have `"passes": true|false` only when:

- Deliverable exists at agreed path
- Methods match prespecified analysis
- Critical numbers reconciled with source scripts
- Swiss Cheese completed when mandatory (`verification.mdc`)

## Evidence strength (narrative chapters)

Label claims before upgrading prose:

| Label | Meaning |
|-------|---------|
| supported | Direct evidence in cited sources |
| partial | Indirect or heterogeneous evidence |
| unsupported | No adequate source; do not state as fact |

## Iteration loop (`scholarly-iteration-loop`)

1. Pick one milestone with `passes: false`
2. Execute → validate → update spec
3. Append `scholarly-progress.txt`
4. Stop on blocker or user `LOOP OFF`

## Quality dimensions (self-assessment ≥9/10)

Accuracy, Completeness, Methodology, Clarity, Naturalness, Security.

## Parent skills (auto)

- [[SKILL_scholarly-iteration-loop]]
- [[SKILL_write-research-spec]]

## Related playbooks (auto)

- [[literature_review_phases]]
- [[database_strategies]]
- [[citation_styles]]
- [[peer_review_checklist]]
- [[hypothesis_generation_workflow]]
