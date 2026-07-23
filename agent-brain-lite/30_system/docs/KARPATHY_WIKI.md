# Karpathy-style project wiki (second brain)

**Purpose:** Long-lived, interlinked markdown knowledge at the **project root**, separate from the agent-rules brain. The workflow is **native to Cursor**: the wiki lives in the project tree, you navigate and edit in the IDE, and the **agent** (Chat/Composer) ingests from `00_inbox/raw/` and maintains `20_knowledge/wiki/`.

**Canonical layout:** `knowledge_system/00_inbox/raw/`, `knowledge_system/20_knowledge/wiki/`, plus `knowledge_system/AGENT_SPEC.md`. Created by [`40_operations/scripts/project_init.py`](../40_operations/scripts/project_init.py).

---

## How this differs from other logs

| Location | Role |
|----------|------|
| `.agent/MEMORY.md` | Short auto-progress log for agent continuity (~200 lines max). |
| `30_system/04_documentation/context/log.md` | OTA (Observation, Thought, Action) session history. |
| `knowledge_system/20_knowledge/wiki/` | Curated, growing **topic pages** and navigation. |
| `knowledge_system/20_knowledge/wiki/log.md` | **Wiki-only** history: what was ingested, merged, or reorganized (not OTA). |

Do not merge these roles. The wiki is for durable concepts and links; MEMORY and OTA logs are for process and session state.

---

## Directory structure

```
knowledge_system/
├── AGENT_SPEC.md    # Rules for the wiki agent (ingest, naming, linking)
├── 00_inbox/raw/             # Drop zone: transcripts, exports, text extractions, draft notes
└── 20_knowledge/wiki/
    ├── index.md     # Map of topics / entry point for you and the agent
    ├── log.md       # Ingest and maintenance log
    └── ...          # One .md per topic (created by the agent)
```

---

## Ingestion workflow

1. Add a file under `knowledge_system/00_inbox/raw/` (e.g. a transcript or cleaned export).
2. In Cursor, open Chat or Composer, attach context with **`@knowledge_system/AGENT_SPEC.md`** (and `@knowledge_system/00_inbox/raw/...` if needed), then ask for example: *I added `00_inbox/raw/lecture_2026-01.md`. Ingest it into the wiki.*
3. The agent should: read the raw file; extract entities and concepts; create or update pages in `20_knowledge/wiki/`; add **cross-links** between notes (see linking conventions below); update `20_knowledge/wiki/index.md`; append a line to `20_knowledge/wiki/log.md`.

---

## Working in Cursor (not a separate notes app)

Everything stays inside the **same workspace** where you already code and write.

| Practice | Why |
|----------|-----|
| **Explorer** | Expand `knowledge_system/20_knowledge/wiki/` and open `.md` files like any source file. |
| **Quick Open** (`Ctrl+P` / `Cmd+P`) | Jump to `topic-slug.md` by filename. |
| **`@` in chat** | Attach `@knowledge_system/wiki`, a single page, or `AGENT_SPEC.md` so the agent sees the right subset without pasting long text. |
| **Search** | Workspace search (`Ctrl+Shift+F` / `Cmd+Shift+F`) across `knowledge_system/` for phrases or titles. |
| **Relative markdown links** | Prefer `[Label](other-topic.md)` between pages so links resolve in-repo and work with normal editor navigation where supported. |

Optional **`[[Page Title]]`**-style tokens may still appear as a compact human/agent convention for “see also” mentions. Consistency matters more than syntax.

---

## Cursor usage (agent + tokens)

- For ingest or large edits, include **`@knowledge_system/AGENT_SPEC.md`** (and optionally `@knowledge_system/20_knowledge/wiki/index.md`).
- To limit context cost on big 20_knowledge/wikis, the agent should read **`20_knowledge/wiki/index.md` first**, then open only the pages relevant to the task.
- You can add a short pointer in **project `.cursor/rules`** or **Cursor Settings → Rules** if you want the wiki spec emphasized whenever `knowledge_system/**` is in scope; keep it thin to avoid rule overload (see `context-optimization.mdc` in the brain).

---

## Relationship to `01_input/`

- Literature and lab inputs stay in `01_input/` per [BRAIN_AND_PROJECT.md](BRAIN_AND_PROJECT.md).
- Put in `knowledge_system/raw` only material you **intend to process into the wiki** (copies, exports, or short notes). Use copy vs. symlink as you prefer on your OS.

---

## Health check (periodic)

- Ask the agent to run a **wiki health check**: broken relative links, orphan pages not listed in `index.md`, duplicate topics, stale `index.md` structure. Optional: a small script later for automation.

---

## Further reading

- Project vs brain: [BRAIN_AND_PROJECT.md](BRAIN_AND_PROJECT.md)

## Parent skills (auto)

- [[SKILL_obsidian-wiki-agent]]
