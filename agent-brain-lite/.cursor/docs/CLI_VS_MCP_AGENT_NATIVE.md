# CLI vs MCP for agent-native workflows

**Purpose:** Complement `MCP_AND_SKILLS_LAYERS.md` with when to **keep MCP**, when to add a **thin CLI** (typically Python in this repo), and how to reduce tool-schema and raw-JSON pressure on context.  
**Audience:** Maintainers designing integrations for Cursor agents in this workspace.

---

## 1. Roles recap

- **MCP:** Long-lived tools exposed to the IDE; good for ad hoc discovery and capabilities that must stay inside the agent tool surface.
- **CLI:** One-shot or scriptable commands; good for **shaping** output before it reaches the model, caching, pagination, and auth held locally.

Neither replaces the other; they solve different parts of the stack.

---

## 2. When MCP tends to win

- Low-frequency calls where loading tool descriptions is acceptable.
- Tight IDE integration (filesystem, git, PDF text, PubMed) already configured in `.cursor/mcp.json`.
- Operations where the agent benefits from **enumerated tools** and standardized invoke semantics.

---

## 3. When to prefer or add a CLI (`40_operations/scripts/`)

Consider a dedicated CLI (or extending an existing script) when:

1. **Large JSON payloads** — APIs return nested blobs; the agent only needs summaries, counts, or filtered rows.
2. **Pagination and rate limits** — Stable loops belong in code, not in repeated chat turns.
3. **OAuth / token refresh / session quirks** — Secrets stay out of prompts; the CLI holds configuration.
4. **Repeated identical fetches** — Local cache or **SQLite mirror** avoids duplicate network work and duplicate context.
5. **Deterministic transforms** — Normalize fields, validate schemas, produce stable Markdown or tables for the model.

**Lazy discovery:** Design CLIs with subcommands and `--help` so the agent loads **only** the usage fragment for the command in play, instead of imagining an entire MCP tool catalog in prose.

**Language:** `.cursorrules` defaults non-statistical tooling to **Python**; this repo has no Go baseline. Other languages are fine if policy is explicitly updated.

---

## 4. MCP “overhead” and benchmarks

Public commentary sometimes claims large token ratios (e.g. CLI vs MCP) or reliability percentages. Treat such figures as **non-verified** unless you attach a reproducible benchmark in this repo (fixture + script + measured token counts). Use local profiling when decisions hinge on cost.

---

## 5. Workspace audit checklist (repeatable)

Run when adding integrations or debugging context bloat:

1. **Inventory MCP servers** — Read `.cursor/mcp.json` keys under `mcpServers`.
2. **Find HTTP clients** — Search `40_operations/scripts/**/*.py` for `requests`, `httpx`, `urllib`, `aiohttp`.
3. **Find JSON hotspots** — Search for `json.load`, `json.loads`, `.json()` on responses; flag scripts that print huge unstructured JSON to stdout.
4. **Skills / rules** — Ensure skills describe **process**, not pasted API payloads (`MCP_AND_SKILLS_LAYERS.md`).
5. **Decision** — For each hotspot: narrow MCP tool output, add CLI post-processing, or move bulk work to a script the agent runs once.

Suggested searches (from repo root):

```bash
rg "requests\.|httpx\.|urllib\.|aiohttp" 40_operations/scripts --glob "*.py"
rg "json\.loads?\\(|\\.json\\(\\)" 40_operations/scripts --glob "*.py"
```

---

## 6. Related

- [MCP and Skills layers](MCP_AND_SKILLS_LAYERS.md) (data vs logic split)
- [Agentic Re-Act OS](AGENTIC_REACT_OS.md) (TAOR, iteration caps, when to script vs delegate)
- [Workspace router (INDEX)](INDEX.md) (rules, skills, and docs hooks)
- CLI ergonomics for agents: external Cursor skill `cli-for-agents` (layered `--help`, non-interactive flags, dry-run)

---

## Appendix A: Current workspace snapshot (factual)

_Snapshot generated 2026-05-10 during Agentic OS integration; re-run §5 searches to refresh._

### A.1 MCP servers configured

Keys under `mcpServers` in `.cursor/mcp.json`:

| Server key | Transport / entry (summary) |
|------------|-------------------------------|
| filesystem | `npx` → `@anthropic/mcp-filesystem` |
| git | `npx` → `@anthropic/mcp-git` |
| pubmed | `python` → `.cursor/mcp_servers/pubmed_server.py` (optional `NCBI_API_KEY`, `NCBI_EMAIL`) |
| handoff | `python` → `.cursor/mcp_servers/handoff_server.py` |
| memory | `python` → `.cursor/mcp_servers/memory_server.py` |
| pdf | `npx` → `@sylphx/pdf-reader-mcp` |

### A.2 HTTP client patterns in `40_operations/scripts` (\*.py)

- Search for `requests.`, `httpx.`, `urllib.`, `aiohttp` usage strings: **no matches** in that folder.
- Broader `urllib|requests|httpx|aiohttp` file scan under `40_operations/scripts`: only **`brain_health.py`**, and only as a **warnings filter** comment referencing transitive `urllib3` (not an outbound HTTP client implementation in this file).

### A.3 `json.load` / `json.loads` / `.json()` occurrences

These indicate structured parsing (often local artifacts, registry, or eval JSON), not necessarily external API bulk:

- `memory_hook.py`, `brain_health.py`, `generate_evals_from_skill.py`, `self_eval_learning_loop.py`, `run_agent_benchmark.py`, `reliability_eval_runner.py`, `rag_eval_runner.py`, `trajectory_eval_runner.py`, `changelog_auto.py`, `skill_gap_ingest.py`, `build_knowledge_population_reports.py`, `brain_status.py`, `generate_experiment_report.py`, `memory_admin.py`, `run_all_skill_evals.py`, `run_autoresearch.py`, `run_optimization_round.py`, `skill_registry.py`, `validate_experiment_artifacts.py`, `skill_examples_tailor.py`

### A.4 Go toolchain

- No `*.go` files under workspace root at snapshot time; agent-native CLIs here align with **Python** per `.cursorrules` unless policy is extended.
