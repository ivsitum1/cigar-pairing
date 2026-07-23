# Obsidian wiki upgrade (ar9av/obsidian-wiki)

**Date:** 2026-05-22 | **Completed pass:** 2026-05-30  
**Upstream:** [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki) @ `6f20faaa` (import: `90_archive/imports/obsidian-wiki_2026-05/`)

## What was integrated

| Component | Location |
|-----------|----------|
| Upstream skills (36) | `.cursor/skills/<name>/` → junctions to import `.skills/` |
| Installer | `40_operations/scripts/install_obsidian_wiki_skills.ps1` |
| Env (local) | `.env` (gitignored), template `.env.example` |
| Global portable config | `%USERPROFILE%/.obsidian-wiki/config` |
| Manifest | `20_knowledge/wiki/.manifest.json` |
| Staging | `20_knowledge/wiki/_raw/` |
| Taxonomy stub | `20_knowledge/wiki/_meta/taxonomy.md` |
| Cursor routing | `.cursor/rules/obsidian-wiki-upstream.mdc` (scoped) |

## Vault path adapter

| Setting | Value | Why |
|---------|-------|-----|
| `OBSIDIAN_VAULT_PATH` | `.../20_knowledge/wiki` | Matches existing `entities/`, `concepts/`, `sources/`, `analysis/` |
| Obsidian UI | Repo root (`.obsidian/` at root) | Whole repo remains the desktop vault |
| `AGENT_RULES_REPO_ROOT` | Repo root | In `~/.obsidian-wiki/config` for scripts spanning wiki + system |

Do **not** run `wiki-rebuild` without explicit approval.

## Native vs upstream skills

| Task | Use |
|------|-----|
| `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-status`, history ingest | Upstream `.cursor/skills/` |
| Obsidian syntax, Canvas, Bases, callouts | `SKILL_obsidian-wiki-agent` + `OBSIDIAN_AGENT_PLAYBOOK` |
| Literature claim / gap gates | `reference/obsidian_literature/` |
| Graph connectivity (Python) | `obsidian_connectivity_check.py`, `wiki_semantic_link.py` |

## Re-install upstream skills

```powershell
powershell -ExecutionPolicy Bypass -File 40_operations/scripts/install_obsidian_wiki_skills.ps1
```

## QMD semantic search

### Install

1. Install [QMD](https://github.com/tobi/qmd) and ensure `qmd` is on PATH.
2. Repo `.env` already sets:
   - `QMD_WIKI_COLLECTION=agent-rules-wiki`
   - `QMD_PAPERS_COLLECTION=agent-rules-sources`
   - `QMD_TRANSPORT=cli`
   - `QMD_CLI_SEARCH_MODE=balanced`

### Index (run after install)

```powershell
qmd index --name agent-rules-wiki "$env:USERPROFILE\Documents\agent rules\20_knowledge\wiki"
qmd index --name agent-rules-sources "$env:USERPROFILE\Documents\agent rules\20_knowledge\reference_library"
```

Re-index after large ingests.

**Status (2026-05-22):** Node.js LTS + QMD 2.5.1 installed. Collections indexed: `agent-rules-wiki` (3298 md), `agent-rules-sources` (2073 md in `books_md`). BM25 search works; run `qmd embed` for full semantic vectors (downloads models, slow on CPU).

**Windows wrapper** (npm `qmd` launcher broken without Git Bash):

```powershell
powershell -File 40_operations/scripts/qmd.ps1 search "your topic" -c agent-rules-wiki -n 5
powershell -File 40_operations/scripts/qmd.ps1 query "your topic" -c agent-rules-wiki --no-rerank
```

Re-index: `powershell -ExecutionPolicy Bypass -File 40_operations/scripts/install_qmd.ps1`  
Optional vectors: add `-RunEmbed` (long-running).

### MCP mode (optional)

Set `QMD_TRANSPORT=mcp` in `.env` and add a QMD MCP server to `.cursor/mcp.json` per the QMD project docs. Default is **CLI** (no extra MCP).

Without QMD, `wiki-query` and `wiki-ingest` use Grep/Glob automatically.

## First commands in Cursor

1. `set up my wiki` or `/wiki-setup` (respects existing `index.md` / `log.md`)
2. `/wiki-status`
3. `/wiki-query <topic>`
4. Drop a note in `20_knowledge/wiki/_raw/` then `/wiki-ingest`

## Optional pass 2

```bash
npx skills add kepano/obsidian-skills
```

Then re-run the junction installer or symlink into `.cursor/skills/`.

## Completion status (2026-05-30)

| Check | Result |
|-------|--------|
| Upstream skills (36 junctions) | Installed via `install_obsidian_wiki_skills.ps1` |
| `.cursor/rules/obsidian-wiki-upstream.mdc` | Active |
| Wiki graph (`obsidian_connectivity_check.py`) | Connected 3756 / Weak 0 / Orphan 0 (after `wiki_semantic_link.py --apply --fix-zero-outbound --embeddings`) |
| QMD collections | See `.manifest.json` (re-index after large ingests) |
| Native gates | `SKILL_obsidian-wiki-agent` + `obsidian_literature/` unchanged |

Orphan remediation (2026-05-30): `wiki_semantic_link.py --root . --apply --fix-zero-outbound --embeddings` updated 63 files; graph orphan count 0.

## Related

- [[20_knowledge/wiki/index]]
- [[Claude agent Obsidian wiki workflow]]
- [IMPORT_MANIFEST](../../90_archive/imports/obsidian-wiki_2026-05/IMPORT_MANIFEST.md)
- [KARPATHY_WIKI.md](KARPATHY_WIKI.md)
