# ADR: memory_engine je kanonski memorijski sustav

**Datum:** 2026-07-02 · **Status:** prihvaćeno

## Kontekst

U okruženju postoje 4 paralelna memorijska sloja: `memory_engine/` (vlastiti,
ingest→retrieval→injection→self_eval), claude-mem plugin, ECC
continuous-learning, i `.agent/MEMORY.md`. Svaki uči zasebno — znanje se
fragmentira po slojevima i računalima.

## Odluka

1. **`memory_engine/` je jedini kanonski store** (piše u `.agent/memory/`).
   Ožičen je u `.cursor/hooks.json` na svim lifecycle točkama.
2. `.agent/MEMORY.md` ostaje ljudski čitljiv **sažetak/izlog**, ne primarni zapis;
   generira se iz memory_enginea, ne uređuje ručno mimo njega.
3. claude-mem i ECC learning slojevi smiju čitati, ali se njihovi zapisi
   smatraju lokalnim keševima — ništa trajno ne smije živjeti samo tamo.
   Ako se pokažu redundantnima, isključiti ih u `~/.claude/settings.json`.

## Posljedice

- Novi memorijski feature = proširenje memory_enginea, ne novi sloj.
- Migracije/konsolidacije zapisa idu kroz `memory_engine/ingest.py`.
- Runtime artefakti (`memory.db`, `raw_events.jsonl`, `self_eval.jsonl`)
  ostaju izvan gita (.gitignore).
