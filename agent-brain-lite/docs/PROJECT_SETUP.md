---
title: Upute — koloniranje u projekt
category: doc
tags: [setup, project, windows]
---

# Kako kolonirati mozak u projekt

**Nije** dovoljno samo „Add Folder" u Cursoru ako želite punu funkcionalnost. Trebate strukturu + vezu na `.cursor` pravila.

## Što se događa

1. Kopija mozga u podmapu projekta
2. Projektne mape za rad (`01_work/`)
3. `.cursor` pokazuje na pravila mozga
4. `.agent/` na razini projekta za memoriju tog projekta

## Korak 1 — Kreiraj mapu projekta

```powershell
mkdir D:\projekti\moj-ured-projekt
cd D:\projekti\moj-ured-projekt
```

## Korak 1b — Poveži parent (master mozak, jednom)

```powershell
cd "C:\Users\Ivan\OneDrive\Dokumenti\agent brain lite"
copy .env.example .env
python scripts/link_parent.py
```

## Korak 2 — Pokreni project_init

Iz master kopije mozga (ovaj repo):

```powershell
python "C:\Users\Ivan\OneDrive\Dokumenti\agent brain lite\scripts\project_init.py" --root "D:\projekti\moj-ured-projekt"
```

Na Windowsu bez symlink prava:

```powershell
python "...\scripts\project_init.py" --root "D:\projekti\moj-ured-projekt" --no-symlink
```

## Korak 3 — Otvori u Cursoru

**File → Open Folder** → odaberi `D:\projekti\moj-ured-projekt` (korijen projekta), ne samo `agent-brain-lite` unutra.

## Struktura nakon inita

```
moj-ured-projekt/
├── agent-brain-lite/     ← kopija mozga
├── .cursor/              ← symlink ili kopija iz mozga
├── .agent/               ← MEMORY projekta
├── 01_work/
│   ├── inbox/
│   ├── output/
│   └── correspondence/
└── README.md
```

## Ručna alternativa (bez skripte)

1. Kopiraj cijeli folder `agent brain lite` u projekt kao `agent-brain-lite`
2. Kopiraj `agent-brain-lite\.cursor` u korijen projekta kao `.cursor`
3. Kreiraj `01_work/inbox`, `output`, `correspondence`
4. Kreiraj `.agent/MEMORY.md`

## Ažuriranje mozga

Dok nema gita: ručno kopiraj novu verziju `agent-brain-lite` ili samo `.cursor` + `nodes` + `skills`. Kasnije: `git pull` unutar `agent-brain-lite`.

## Add Folder vs Open Folder

- **Open Folder** — jedan workspace root; orchestrator vidi cijeli projekt. *Preporučeno.*
- **Add Folder to Workspace** — multi-root; radi, ali putanje u pravilima pretpostavljaju jedan korijen.
