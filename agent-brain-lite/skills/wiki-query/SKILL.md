---
name: wiki-query
description: Pretraži lokalni wiki (RAG-lite)
category: skill
tags: [skill, rag, query]
triggers: [što znamo o, pretraži wiki, wiki query]
node: 04_research
---

# Skill: wiki-query (RAG-lite)

**Kada:** Pitanje o domenskom znanju prije vanjskog lookupa.

## Procedura

1. Pretraži `knowledge/` i `nodes/` po ključnim riječima
2. Čitaj `summary` u YAML frontmatter i naslove (`#` / `title`)
3. Otvori samo relevantne `.md` stranice
4. Sintetiziraj odgovor s `[[wikilink]]` citatima
5. Ako nema pokrivenosti → čvor 04 Research ili parent brain
