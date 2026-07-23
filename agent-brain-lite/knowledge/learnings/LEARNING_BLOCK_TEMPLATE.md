---
title: LEARNING_BLOCK — predložak
category: reference
tags: [learning, template]
summary: Strukturirani blok za ingest u learning log.
---

# LEARNING_BLOCK predložak

Na kraju značajnog zadatka agent može emitirati:

```markdown
## LEARNING_BLOCK
{"task_type": "admin", "task_description": "Organizacija grant priloga", "approach": "01_work/inbox + checklista u log.md", "status": "success", "learnings": {"what_worked": ["jasna mapa inbox/output"], "what_failed": [], "insights": ["rokovi u tablici u log.md"]}}
## END_LEARNING_BLOCK
```

## Polja

| Polje | Obavezno | Vrijednosti |
|-------|----------|-------------|
| task_type | da | admin, writing, research, automation, legal, publishing |
| task_description | da | kratki opis |
| approach | da | što je napravljeno |
| status | da | success, partial, failure |
| learnings | ne | what_worked, what_failed, insights (liste) |

## Ingest

```powershell
python scripts/learning_log.py ingest-block --file draft.txt
# ili
python scripts/learning_log.py ingest-block --stdin
```

Nakon ingest-a ažuriraj [[log]] i po potrebi kreiraj stranicu u `knowledge/learnings/` ako je učenje trajno vrijedno.
