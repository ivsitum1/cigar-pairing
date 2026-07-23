# Agentic engineering workflow (Grill-me, PRD, Ralph)

**Purpose:** External memory for software feature work: PRD and progress logs survive context limits; the agent follows procedural SKILLS instead of improvising.

**Scope:** Application repositories where you write code. If you only attach the **agent rules** folder as a read-only brain to another repo, create `30_system/docs/prd.json` and `30_system/docs/progress.txt` in the **application** project, not inside the brain.

**Related (not software):** For manuscripts, statistics, and book chapters with the same “spec + passes + iteration” discipline, see `30_system/docs/SCHOLARLY_WORKFLOW.md` and domain `scholarly` skills in `30_system/SKILLS/registry.json`.

---

## Artifacts

| Artifact | Typical path | Role |
|----------|----------------|------|
| PRD | `30_system/docs/prd.json` (preferred) or `30_system/docs/prd.md` | Source of truth; each item can have `"passes": false/true` |
| Progress log | `30_system/docs/progress.txt` | Append-only; long-term memory between chats |
| Templates | `30_system/docs/templates/prd.schema.json`, `prd.example.json`, `progress.template.txt` | Copy or reference when bootstrapping |

---

## Skill sequence

1. **SKILL_grill-me** — Shared understanding; explore codebase before asking redundant questions.
2. **SKILL_write-prd** — Lock problem, solution, user stories, technical decisions; Ralph flags.
3. **SKILL_prd-to-issues** — Vertical slices, tracer bullets, `blocked_by`.
4. **SKILL_ralph-loop** — Only after explicit **Ralph ON**: select task → TDD (`harness_tdd.mdc`) → update PRD → append progress → git commit → suggest fresh chat when needed.

Operational default chain for new software tasks: `grill-me -> write-prd -> prd-to-issues -> ralph-loop`.

**Semantic auto-load:** `python 40_operations/scripts/skill_rerank.py --prompt "..." --auto-pipeline --dag --json` detects PRD/Ralph intent and returns the full pipeline bundle (`pipeline_auto_load`). `agent_auto_detection.py` uses the same path for `skill_suggestions` / `pipeline_auto_load`.

---

## Verification guardrails in PRD

- Add a `verification_protocol` block to `30_system/docs/prd.json` when tasks rely on factual or model-behavior claims.
- Use claim statuses consistently:
  - `VERIFIED`: backed by execution output, source documents, or reproducible tooling evidence.
  - `INFERRED`: reasonable synthesis derived from verified facts.
  - `UNVERIFIED`: not yet supported, must not be treated as final evidence.
- Require baseline-vs-steered comparison whenever steering or representation methods are introduced.
- Require reproducibility metadata (seed, runtime environment, package versions) before setting related PRD items to `passes: true`.

---

## Modes

| Mode | Trigger |
|------|---------|
| Ralph OFF | Default; interactive pair programming |
| Ralph ON | User says "Ralph ON" or "Run Ralph loop [N iterations]" |
| Exploration Mode | Spikes and MVPs; still log to `progress.txt` |

---

## MCP and tools

- **Skills** encode *process*; **MCP** supplies *data and tools*. See `.cursor/docs/MCP_AND_SKILLS_LAYERS.md`.
- This workspace’s `.cursor/mcp.json` may include **filesystem** and **git** for PRD and commits.
- Optional additions (configure in your **application** project if needed): **Playwright** (UI verification), **GitHub** (issues and Kanban). They are not required for the core loop.

---

## Risks

- Long threads and huge PRDs increase token use; keep PRD and progress entries concise.
- Stop and ask for human help if tests stay red after two focused iterations or the plan drifts from the PRD.
- Tests must assert real behavior (anti-poisoning); see `SKILL_ralph-loop.md`.

---

## Parallel workflows and token budget guards

When running **parallel sub-agents** or NotebookLM-style deep-research workflows (see `outputs/notebooklm/rag_anatomy_executive.md`), set explicit limits **before** starting:

| Guard | Recommended default | Rationale |
|-------|---------------------|-----------|
| Max concurrent sub-agents | 16 (tool cap) or lower per subscription | Avoid runaway parallel fan-out |
| Max steps per agent loop | 25–50 (align with `TRAJECTORY_CONSOLIDATE_THRESHOLD`) | Prevent infinite Re-Act |
| Max hops (multi-hop RAG) | 3 | Notebook: cost explodes without stop criteria |
| Human approval | Destructive file/git/network actions | Governance lever |
| Token budget | User-defined cap per run; log usage | Do **not** treat anecdotal demo totals (e.g. multi-million tokens in one workflow) as SLA |

Orchestrator: prefer **deterministic workflow scripts** for width-heavy work; keep LLM as worker, not manager (`30_system/docs/RAG_ANATOMY_MAP.md`).

---

## Registry

Skills are registered in `30_system/SKILLS/registry.json` (domain `engineering`). Invoke by name or trigger phrase; see `30_system/behavior_rules/reference/skill_task_mapping.md`.

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
