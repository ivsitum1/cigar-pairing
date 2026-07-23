# Literature review phases (SR and narrative)

## Phase log (reproducible)

For each database record:

| Field | Content |
|-------|---------|
| Database | e.g. PubMed, Embase |
| Date | YYYY-MM-DD |
| Query | Full string |
| Filters | Applied limits |
| Hits | Count before dedup |

## Systematic review (full MA skill)

1. Protocol / PICO frozen
2. Search (multiple databases + grey if prespecified)
3. Deduplication
4. Title/abstract screening (dual when possible)
5. Full-text screening
6. Extraction + risk of bias
7. Synthesis (narrative and/or quantitative)
8. Reporting (PRISMA flow)

Use `SKILL_meta-analysis` for execution; PRISMA checklist for compliance audit.

## Narrative / grid synthesis

Use `SKILL_literature-synthesis` when pooling is not mandatory: analysis grid, consensus meter, gap statement.

## Screening discipline

- Document exclusions per stage with counts.
- Do not upgrade screening corpus language to "review article" in manuscript prose without editorial intent.

## Parent skills (auto)

- [[SKILL_literature-synthesis]]
- [[SKILL_meta-analysis]]
- [[SKILL_prisma-checklist]]

## Related playbooks (auto)

- [[database_strategies]]
- [[citation_styles]]
- [[peer_review_checklist]]
- [[hypothesis_generation_workflow]]
- [[evaluation_framework]]
