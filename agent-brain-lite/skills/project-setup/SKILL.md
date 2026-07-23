---
name: project-setup
description: Koloniraj mozak u novi projekt
category: skill
tags: [skill, project, setup]
triggers: [postavi projekt, koloniraj mozak, project init]
node: 03_automation
---

# Skill: project-setup

**Kada:** Novi admin projekt treba mozak.

## Procedura

1. Korisnik odredi mapu projekta (npr. `D:\projekti\ured-grant-2026`)
2. Pokreni: `python scripts/project_init.py --root "PUTANJA"`
3. Na Windowsu ako symlink ne radi: `--no-symlink`
4. U master mozgu jednom: `python scripts/link_parent.py` (poveže agent rules)
5. Otvori **korijen projekta** u Cursoru (ne samo `agent-brain-lite` podmapu)

Detalji: [[docs/PROJECT_SETUP]]
