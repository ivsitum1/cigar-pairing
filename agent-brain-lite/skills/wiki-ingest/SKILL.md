---
name: wiki-ingest
description: Dodaj sadržaj u lokalni Markdown wiki
category: skill
tags: [skill, ingest, wiki]
triggers: [ingest, dodaj u wiki, spremi u znanje]
node: 01_admin
---

# Skill: wiki-ingest

**Kada:** Korisnik želi spremiti bilješku, sažetak ili izvor u lokalni wiki.

## Procedura

1. Odredi kategoriju: `concepts` | `entities` | `references` | `projects`
2. Kreiraj `.md` s YAML frontmatter (`title`, `category`, `tags`, `summary`, `created`, `updated`)
3. Poveži s postojećim stranicama (`[[wikilinks]]`)
4. Ažuriraj [[index]], `.manifest.json`, [[log]], [[hot]]

Ne dupliciraj sadržaj — ažuriraj postojeću stranicu ako tema već postoji.
