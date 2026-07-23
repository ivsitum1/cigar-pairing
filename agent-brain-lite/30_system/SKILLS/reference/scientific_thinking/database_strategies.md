# Database search strategies

## Core databases (biomedical)

- PubMed / MEDLINE
- Embase (if available)
- Cochrane CENTRAL (for interventions)
- Trial registries when gaps suspected

## Query construction

- PICO blocks: population, intervention/exposure, comparator, outcome
- Combine with AND; synonyms with OR inside blocks
- MeSH + free text where appropriate
- Document date limits and language filters

## Efficiency

- Prefer **PubMed MCP** in this workspace when configured.
- Otherwise E-utilities patterns in `pubmed/search_syntax.md` (no embedded API keys).

## Updates

- Rerun search before submission if protocol allows; record update date and new hits.

## Not in scope here

Full trial registry API scripts may live under project `40_operations/`; cite only verified hits.

## Parent skills (auto)

- [[SKILL_literature-synthesis]]
- [[SKILL_meta-analysis]]

## Related playbooks (auto)

- [[literature_review_phases]]
- [[citation_styles]]
- [[peer_review_checklist]]
- [[hypothesis_generation_workflow]]
- [[evaluation_framework]]
