# PubMed search syntax (patterns)

## Field tags (examples)

- `[ti]` title
- `[tiab]` title/abstract
- `[mh]` MeSH term
- `[au]` author
- `[pt]` publication type

## Building blocks

```
("extracorporeal membrane oxygenation"[mh] OR ECMO[tiab])
AND (sedation[tiab] OR analgesia[tiab])
AND (adult[tiab] OR adult[mh])
```

## Filters

- Apply in query or interface: dates, species, language, article types
- Record exact filter string in search log

## E-utilities (when no MCP)

- Use NCBI E-utilities with polite rate limits and `email` parameter per NCBI policy.
- Store PMIDs and query version in project logs.

## Verification

Never cite a paper from title alone if PubMed has no abstract; verify full text for substantive claims.

## Parent skills (auto)

- [[SKILL_literature-synthesis]]
- [[SKILL_meta-analysis]]
- [[SKILL_research-lookup]]
