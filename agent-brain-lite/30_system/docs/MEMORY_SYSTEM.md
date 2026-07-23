# Memory System (full parity baseline)

This document describes the new persistent memory system for `agent rules`.

## Components

- `memory_engine/`:
  - `config.py`: runtime paths and feature flags
  - `store.py`: SQLite + FTS index
  - `ingest.py`: lifecycle event ingest with dedup
  - `compression.py`: sanitized observation composer
  - `retrieval.py`: `search`, `timeline`, `get_observations`
  - `injection.py`: budget-aware session context injection
  - `worker.py`: local HTTP service
- MCP server: `.cursor/mcp_servers/memory_server.py`
- Auto hooks wiring:
  - `.cursor/hooks.json`
  - `.cursor/hooks/memory_lifecycle.py`
- CLI wrappers:
  - `40_operations/scripts/memory_hook.py`
  - `40_operations/scripts/memory_worker.py`

## Data layout

- DB: `.agent/memory/memory.db`
- Raw ingest audit: `.agent/memory/raw_events.jsonl`
- Last injected context cache: `.agent/memory/last_injected_context.md`
- Self-evaluation log: `.agent/memory/self_eval.jsonl`
- Verifier usage ledger: `.agent/memory/verifier_usage_ledger.jsonl` (SkillLens hook; see [VERIFIER_LEARNING_LOOP.md](VERIFIER_LEARNING_LOOP.md))

## Mixture routing and failure modes

Multi-substore routing (wiki, trajectory, SQLite, books_rag, verifier ledger) and `failure_mode` tags (`summary` | `storage` | `retrieval` | `unknown`) are documented in **[MEMORY_MIXTURE_ROUTING.md](MEMORY_MIXTURE_ROUTING.md)**.

- Ingest: `memory_engine/ingest.py` + `compression.py` tag observations.
- Hook: `.cursor/hooks/memory_lifecycle.py` infers `failure_mode` on payload before ingest when not explicitly set.
- Episodic-first consolidation into `.agent/MEMORY.md`: [TRAJECTORY_RL_POLICY.md](TRAJECTORY_RL_POLICY.md#episodic-first-policy) and `trajectory_rl/emit.py` (`request_milestone_consolidate`, `approve_consolidate_eval`).

## Feature flag

By default memory is enabled for auto-capture and auto-injection.

- `AGENT_MEMORY_ENABLED=1` (default)
- Set `AGENT_MEMORY_ENABLED=0` only if you explicitly want to disable memory

## Hook visibility and conditional injection (Cursor)

These variables apply to `.cursor/hooks/memory_lifecycle.py` (when Cursor runs the hook with environment inheritance).

**Spec (what this is and is not):** [GRILL_ME_INJECTION_HEURISTIC.md](GRILL_ME_INJECTION_HEURISTIC.md) — memory **prefetch cues** from the skill registry; this is not the conversational SKILL “grill me” interview in chat.

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `AGENT_MEMORY_SHOW_MESSAGES` | `1` | If set, hook JSON may include `agent_message` (lifecycle + optional `memory_prefetch=alignment-cues`). Set to `0` for silent hooks. |
| `AGENT_MEMORY_INJECT_CONTEXT_ON_START` | `0` | If `1`, on `sessionStart` injects retrieval context (same as legacy “always on start”). |
| `AGENT_MEMORY_INJECT_ON_GRILL_ME` | `1` | If `1`, on `beforeSubmitPrompt` prefetches memory **once per conversation** when the user text matches **registry + supplemental injection cues** (see linked doc). |
| `AGENT_MEMORY_FALLBACK_INJECT` | `0` | If `1` and memory_engine unavailable, inject tail of workspace `.agent/MEMORY.md` (scoped label only). Default off. |

**Project scope:** Resolved by `40_operations/python/common/workspace_scope.py` — per workspace root, not brain folder name when `.cursor` is symlinked. Override: `.agent/project_scope.json`. Cross-project recall: MCP `search_cross_project` only (never hooks). Federated mode queries the active workspace DB plus embedded `agent-rules` brain and optional `AGENT_MEMORY_FEDERATED_ROOTS` (comma-separated project roots). Use MCP `list_memory_sources` to inspect discovered DBs.

Injection uses `session_start_injection` with a query built from the user prompt plus retrieval anchors. Conversation identity is taken from `conversation_id` (or aliases) in the hook payload when present; otherwise at most one inject is allowed until `hook_session.json` is reset.

## Automatic lifecycle capture

When enabled, Cursor hooks automatically capture:

- `sessionStart`
- `beforeSubmitPrompt`
- `postToolUse`
- `stop`
- `sessionEnd`

No manual trigger is required.

## Hook workflow

1. Lifecycle emits event.
2. Hook auto-captures event (or `40_operations/scripts/memory_hook.py ingest ...` manually).
3. On session start, call `40_operations/scripts/memory_hook.py inject ...`.
4. Context is cached and can be inserted into prompt bootstrap.

## Self-evaluation (all layers)

Self-evaluation is run across:

- Ingest quality checks (summary presence, privacy scrubbing)
- Retrieval quality checks (query validity, hit ratio)
- Injection checks (budget fit, source references)
- Runtime health checks (endpoint status)

Scores are stored in:

- `.agent/memory/self_eval.jsonl`
- SQLite table `self_evaluations`

## MCP workflow (3-layer retrieval)

1. `search(query, project_scope)` returns compact index.
2. `timeline(project_scope)` returns chronological context.
3. `get_observations(ids)` returns detailed entries.

Additional tools:

- `ingest_event(...)`
- `inject_context(...)`
- `search_cross_project(query, limit)` — **explicit opt-in only**; hooks never call this

## Cross-project search (conscious)

Automatic injection is always scoped to the current `project_scope`. To recall across studies:

1. User asks: e.g. "što smo radili na THERACRAB i PSIOS?"
2. Agent calls MCP **memory** → `search_cross_project(query="THERACRAB OR PSIOS meta-analysis", limit=15)`
3. Optional: `get_observations(ids)` for detail on hit IDs

**Chat example (orchestrator):**

```
User: Pretraži memoriju za meta-analizu na svim projektima.
Agent: [calls search_cross_project] → summarizes with project_scope labels per hit.
```

Never use `search_cross_project` in hooks or sessionStart inject. See [THE_MACHINE.md](THE_MACHINE.md).

## Worker service

Run:

`python 40_operations/scripts/memory_worker.py`

Endpoints:

- `GET /health`
- `GET /api/search?query=...&project_scope=...`
- `GET /api/timeline?project_scope=...`
- `GET /api/get_observations?ids=id1,id2`
- `GET /api/inject?project_scope=...&query=...`
- `POST /api/ingest`
