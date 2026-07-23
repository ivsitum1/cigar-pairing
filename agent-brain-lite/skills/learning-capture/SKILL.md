---
name: learning-capture
description: Zabilježi učenje nakon zadatka (LEARNING_BLOCK + wiki)
category: skill
tags: [skill, learning]
triggers: [learning block, zabilježi učenje, što smo naučili, learning capture]
node: 01_admin
layer: lite
---

# Skill: learning-capture (sloj 1)

**Kada:** Zadatak završen; korisnik traži bilježenje ili agent procijeni da je učenje vrijedno spremiti.

## Procedura

1. Sažmi: što je radilo, što nije, što ponoviti
2. Emitiraj LEARNING_BLOCK ([[knowledge/learnings/LEARNING_BLOCK_TEMPLATE]])
3. Pokreni: `python scripts/learning_log.py ingest-block --stdin` (ili ručno append)
4. Ažuriraj [[log]], [[hot]], `.agent/MEMORY.md` za milestone
5. Ako je trajno znanje → nova stranica u `knowledge/learnings/<slug>.md` s frontmatter

Ne dupliciraj — proširi postojeću learning stranicu ako tema postoji.
