---
title: Learning Loop — tri sloja
category: meta
tags: [learning, loop, harness]
summary: Minimal (ručno), medium (parent hooks), lite auto (JSONL).
---

# Learning Loop (brain-lite)

Tri sloja rade **zajedno**, od lakšeg prema težem.

## Sloj 1 — Minimal (ručno, bez Pythona)

Agent na kraju značajnog zadatka:

1. Ažurira [[log]] i [[hot]]
2. Piše milestone u `.agent/MEMORY.md` ako je trajno važno
3. Opcionalno emitira **LEARNING_BLOCK** (vidi [[knowledge/learnings/LEARNING_BLOCK_TEMPLATE]])
4. Ingest: `python scripts/learning_log.py ingest-block --stdin`

Parent protokol: `30_system/behavior_rules/14_learning_loop.md` (nakon `link_parent.py`).

## Sloj 2 — Medium (parent automacija)

`link_parent.py` povezuje:

- `40_operations/` — `self_eval_learning_loop.py`, memory admin, …
- `memory_engine/` — SQLite memorija
- `.cursor/hooks/` — parent hookovi (memory, trajectory, verifier)
- Spojeni `.cursor/hooks.json`

Tjedno (opcionalno):

```powershell
powershell -File 40_operations/scripts/memory_weekly_maintenance.ps1
```

## Sloj 3 — Lite auto (JSONL)

- Hook: `.cursor/hooks/learning_lifecycle.py` (sessionEnd/stop)
- Log: `.agent/learning.jsonl`
- CLI: `scripts/learning_log.py`

```powershell
python scripts/learning_log.py list --recent 10
python scripts/learning_log.py summary
```

## Prioritet

1. Lite JSONL + ručni LEARNING_BLOCK za uredske zadatke
2. Parent hooks kad je workspace brain-lite s `link_parent.py`
3. `self_eval_learning_loop.py` za prijedloge skills/rules (parent)
