# Multi-PC workspace (agent-rules)

**Purpose:** One git repo, many machines. Git is the source of truth for code, rules, and skills. Machine-local paths and junctions are recreated after every clone or pull.

---

## What lives in git vs on disk

| In git (shared) | Local per machine (not in git) |
|-----------------|--------------------------------|
| `30_system/SKILLS/` — canonical agent skills | `.env` — paths for this PC |
| `90_archive/imports/obsidian-wiki_2026-05/obsidian-wiki/.skills/` — wiki vendor skills | `.cursor/skills/*` junctions → upstream `.skills` |
| Rules, scripts, docs, wiki markdown | `C:\books_rag` — Chroma index (see `BOOKS_RAG_DATA_DIR`) |
| PDF metadata / README only | PDF binaries under `20_knowledge/wiki/sources/pdf/files/` |

Large binaries (PDF, zip, epub) are **gitignored**. They stay on each machine's disk; git never tracks them.

---

## Workflow on every PC

### First time (new machine)

```powershell
cd "C:\Users\<YOU>\Documents\agent rules"
git clone https://github.com/ivsitum1/agent-rules.git .
git checkout master

python 40_operations/scripts/workspace_bootstrap.py --seed-env
python 40_operations/scripts/brain_health.py
```

Copy PDFs and the books RAG index separately (USB stick, LAN share, or Explorer). See **Books RAG** below — **no rebuild** on weak-GPU PCs if you copy `C:\books_rag` from the GPU machine.

### After every `git pull`

```powershell
git pull
python 40_operations/scripts/workspace_bootstrap.py
python 40_operations/scripts/brain_health.py
```

Bootstrap recreates `.cursor/skills` junctions with **repo-relative** targets. Broken junctions are replaced automatically.

---

## Clone path does not matter

Junctions use paths inside the repo:

```
.cursor/skills/wiki-ingest  →  90_archive/imports/obsidian-wiki_2026-05/obsidian-wiki/.skills/wiki-ingest
```

Each machine can clone to `Documents`, `D:\dev\`, etc. Run bootstrap after pull; do not copy junctions between PCs.

---

## Environment file (`.env`)

- Template: `.env.example` uses `<REPO_ROOT>` placeholders.
- `workspace_bootstrap.py --seed-env` writes `.env` with the resolved path on this machine.
- `.env` is gitignored — never commit it.

---

## Books RAG

Index directory defaults to `C:\books_rag` (override with `BOOKS_RAG_DATA_DIR`). Keep it **outside** the git repo. See `30_system/docs/BOOKS_RAG_PATHS.md`.

**Multi-PC rule:** build once on the GPU machine, then **copy the folder** to other PCs. No second embed/rebuild required if the same `embedding_model` is in `manifest.json`.

```powershell
# On GPU PC after build: copy entire C:\books_rag to USB or share
# On this PC (weak GPU):
.\40_operations\scripts\books_rag_sync_from_peer.ps1 -SourcePath "D:\books_rag_export"
python 40_operations/scripts/books_rag_repair_manifest.py --root .
python 40_operations/scripts/books_rag_verify.py --json --cpu-ok
```

Explorer copy of `C:\books_rag` works the same way; close Cursor first and avoid copying while a build lock exists.

---

## Health checks

| Command | When |
|---------|------|
| `python 40_operations/scripts/workspace_bootstrap.py --check-only` | Junctions only |
| `python 40_operations/scripts/brain_health.py` | Full brain check (includes junctions) |
| `python 40_operations/scripts/brain_audit.py` | Audit + errors |

**PASS** requires `cursor_skills: ok (N junctions)` — no broken or OneDrive-stale links.

---

## Do not commit

- Hostname conflict copies (`*-DESKTOP-*`, multi-segment hostname suffixes, etc.)
- PDF/epub binaries
- `.env`, `.cursor/skills/*` junction targets
- OneDrive placeholder files

These patterns are in root `.gitignore`.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Git shows 61 deleted under `.cursor/skills` | Run `workspace_bootstrap.py` (junctions were broken) |
| Junction target contains `OneDrive` | `workspace_bootstrap.py` (auto re-links) |
| `brain_health` fails on `cursor_skills` | Run `python 40_operations/scripts/workspace_bootstrap.py` — auto-clones upstream if `.skills` missing, then installs junctions. `brain_health` retries bootstrap once before failing. |
| Empty `obsidian-wiki` gitlink after clone | `git submodule update --init` or bootstrap (see `IMPORT_MANIFEST.md`) |
| PDFs missing after clone | Expected — copy from backup; git does not ship PDFs |
| Wrong Obsidian paths in tools | `workspace_bootstrap.py --seed-env --overwrite-env` |

---

## Related

- [BRAIN_AND_PROJECT.md](BRAIN_AND_PROJECT.md)
- [CANONICAL_PATHS.md](CANONICAL_PATHS.md)
- `40_operations/scripts/install_obsidian_wiki_skills.ps1`

**Version:** 1.0 | **2026-06-18**
