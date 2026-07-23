# The Machine — agent-rules architecture

**Version:** 1.0.0  
**PRD:** [prd_machine.json](prd_machine.json)  
**Scope decisions:** `.agent/task/machine_prd_scope_decisions.md`

## Concept

The Machine (Person of Interest metaphor) is a **single-user** orchestration layer that:

1. **Observes** via MCP sensors and scheduled brain digests (arXiv, GitHub AI, AI news).
2. **Classifies** requests and routes to specialized subagents (orchestrator).
3. **Remembers** per-project episodic memory without cross-project auto-injection.
4. **Learns** from errors, verifier corrections, and weekly maintenance.
5. **Dreams** grounded creative recombination from run logs (hypotheses only).

It does **not** run a background Cursor agent while the IDE is closed. Scheduled tasks write digest files only.

## Component map

| Layer | Components | Location |
|-------|------------|----------|
| Perception | MCP sensors, weekly digest scripts | `.cursor/mcp.json`, `40_operations/scripts/` |
| Scope | Workspace + project scope resolver | `40_operations/python/common/workspace_scope.py` |
| Memory | SQLite + FTS, hooks, MCP memory | `memory_engine/`, `.cursor/hooks/` |
| Cognition | Orchestrator, skills, subagents | `.cursor/rules/00_orchestrator_agent.mdc` |
| Relevance | Primary / Secondary routing | `MACHINE_PRIMARY_SECONDARY.md` |
| Identity | soul.md, user.md | `30_system/context/` |
| Idle | Dreaming Daemon | `.agent/dreaming/`, `dreaming_daemon.py` |
| Policy | Autonomy boundaries | `.cursor/rules/machine-autonomy.mdc` |

## Project vs brain

| Mode | Workspace | `project_scope` | Memory DB |
|------|-----------|-----------------|-----------|
| Brain maintenance | `agent-rules` repo root | `agent-rules` | `.agent/memory/memory.db` (brain) |
| Clinical/research project | Project root (with `01_input/`, `agent-rules/`) | Folder name slug | `.agent/memory/memory.db` (project) |

**Rule:** Automatic injection is always scoped. Cross-project recall requires explicit `search_cross_project` MCP call or user request.

## Sensor catalog

### On-demand (MCP)

filesystem, git, pubmed, consensus, pdf, books_rag, graphify, notebooklm, latex, overleaf, handoff, memory.

### Scheduled (brain repo only)

| Script | Output | Schedule |
|--------|--------|----------|
| `arxiv_monthly_scan.py --period weekly` | `arxiv_scan_YYYY-WW.json` | Weekly digest |
| `github_ai_watch.py` | `github_ai_watch_YYYY-WW.json` | Weekly digest |
| `ai_news_feed.py` | `ai_news_YYYY-WW.json` | Weekly digest |
| `machine_weekly_digest.py` | `machine_digest_YYYY-WW.md` | Weekly (Task Scheduler) |
| `dreaming_daemon.py` | `frameworks/*.md` | After digest or manual |

## Memory workflow

```
sessionStart → resolve scope → ingest (scoped)
beforeSubmitPrompt → optional grill-me prefetch (scoped)
postToolUse → ingest (scoped)
sessionEnd → ingest (scoped)

Explicit: MCP search(query, project_scope)
Explicit: MCP search_cross_project(query)  # never from hooks
```

## Primary vs Secondary

See [MACHINE_PRIMARY_SECONDARY.md](MACHINE_PRIMARY_SECONDARY.md). Secondary items surface as a **count** at session start when digest exists; full list in weekly digest only.

## Honesty and autonomy

See [machine-autonomy.mdc](../../.cursor/rules/machine-autonomy.mdc) and [soul.md](../context/soul.md).

- Never fabricate citations, statistics, or clinical facts.
- Tell the user the truth even when manuscript prose needs diplomatic framing.
- When uncertain: stop, propose action with rationale, ask.

## GitHub API token (weekly digest)

Public GitHub search is limited (~60 req/h). For scheduled digest:

1. Create `.env.local` at repo root (gitignored): `GITHUB_TOKEN=ghp_...`
2. `run_machine_weekly_digest.ps1` loads `.env.local` automatically
3. Task Scheduler: `install_machine_weekly_task.ps1 -EnvFile "C:\path\to\.env.local"` optional

## Related

- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)
- [BRAIN_AND_PROJECT.md](BRAIN_AND_PROJECT.md)
- [MONTHLY_ARXIV_SKILL_SCOUT.md](MONTHLY_ARXIV_SKILL_SCOUT.md)
- `.agent/dreaming/README.md`
