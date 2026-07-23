# Cursor Workspace Index (Router)

**Purpose:** This file is the layout index for the agent-rules workspace. Tier 0 rules in `.cursor/rules/` act as the router; stable autonomous behavior is also summarized in **`30_system/claude.md`** (see root `CLAUDE.md` bridge). Use this index to find where rules, skills, and project state live.

---

## Router

- **Tier 0 (always loaded):** `.cursor/rules/` – orchestrator, core principles, general-rules (conversational mode), skills auto-detect, error memory.
- **Tier 1 (by glob):** One of Statistics | Writing | Reporting from `.cursor/rules/`.
- **Tier 2 (on demand):** Domain rules (50_ml, 51_llm, 52_causal, 53_bayesian).
- **Tier 3 (on demand):** Up to **two** paired skills from `30_system/SKILLS/` when `registry.json` `tier3_pairing` allows; otherwise one; load via progressive disclosure (see context-optimization.mdc).

---

## Rules

| Purpose | Location |
|--------|----------|
| Orchestrator, classification, pipelines | `.cursor/rules/00_orchestrator_agent.mdc` |
| Core principles, safety, self-assessment | `.cursor/rules/core-principles.mdc` |
| Conversational mode (answer-first, no phantom denial) | `.cursor/rules/general-rules.mdc` |
| Extended conversational examples (on demand) | `.cursor/rules/55_conversational_cognition.mdc` |
| Agentic workflow guardrails (task/plan globs) | `.cursor/rules/agentic-workflow-guardrails.mdc` |
| Claude Tier 0 (non-Cursor) | `30_system/claude.md` |
| Claude extended protocols (on demand) | `30_system/claude_extended.md` |
| Tier system, token budget, overload | `.cursor/rules/context-optimization.mdc` |
| Skill selection, triggers, registry | `.cursor/rules/skills-auto-detect.mdc` |
| Swiss Cheese verification | `.cursor/rules/verification.mdc` |
| Error memory (do not / avoid) | `.cursor/rules/99_error_memory.mdc` |
| Learning loop emit triggers | `.cursor/rules/learning-loop-triggers.mdc` |
| Domain rules (reporting, writing, stats) | `.cursor/rules/reporting-*.mdc`, `writing-*.mdc`, etc. |
| Agentic engineering (PRD, Ralph; glob when editing PRD/progress) | `.cursor/rules/agentic_engineering_workflow.mdc` |
| Scholarly workflow (research spec, scholarly progress; glob) | `.cursor/rules/scholarly_workflow.mdc` |

---

## Skills

- **Location:** `30_system/SKILLS/` at repo root (not under `.cursor/skills/` except for the meta-skill below).
- **Registry:** `30_system/SKILLS/registry.json` – single source of truth for skill id, file, domain, triggers, disambiguation.
- **Meta-skill (skill builder):** `.cursor/skills/skill-builder.md` – create, eval, optimize, benchmark skills; invoked by name or trigger.

---

## Documentation

| Topic | Location |
|-------|----------|
| This index | `.cursor/docs/INDEX.md` |
| Context isolation, 50–60% rule, GSD | `.cursor/docs/CONTEXT_ISOLATION.md` |
| Session reset, when to /clear | `.cursor/docs/STATUS_AND_SESSION.md` |
| MCP vs Skills (data vs logic) | `.cursor/docs/MCP_AND_SKILLS_LAYERS.md` |
| Agentic Re-Act OS (TAOR, CoT/ToT, caps) | `.cursor/docs/AGENTIC_REACT_OS.md` |
| CLI vs MCP (agent-native tooling) | `.cursor/docs/CLI_VS_MCP_AGENT_NATIVE.md` |
| Evidence consistency, pivot, Data Void | `.cursor/docs/EVIDENCE_CONSISTENCY_PROTOCOL.md` |
| AI Semantic Gate (CORE/BACKGROUND/REJECTED) | `.cursor/docs/AI_SEMANTIC_GATE.md` |
| Discovery engine (pipelines, agents, awakening) | `.cursor/docs/DISCOVERY_ENGINE.md` |
| Awakening Ritual (Discovery session start) | `.cursor/docs/AWAKENING_RITUAL.md` |
| Discovery capability registry, super-pipeline | `30_system/behavior_rules/25_capability_registry.md`, `30_system/behavior_rules/26_discovery_superpipeline.md` |
| Brain vs project layout | `30_system/docs/BRAIN_AND_PROJECT.md` |
| Cursor rules setup (no duplicate stacks) | `30_system/docs/CURSOR_RULES_SETUP.md` |
| Brain health PASS criteria | `30_system/docs/BRAIN_HEALTH_CRITERIA.md` |
| Books RAG (reference library) | `30_system/docs/BOOKS_RAG.md` |
| Books RAG paths (local index) | `30_system/docs/BOOKS_RAG_PATHS.md` |
| Study data codebooks (not RAG) | `30_system/docs/study_data/README.md` |
| RAG vs codebooks disambiguation | `30_system/docs/RAG_VS_STUDY_DATA.md` |
| Karpathy wiki (`knowledge_system/`, Cursor IDE workflow) | `30_system/docs/KARPATHY_WIKI.md` |
| Skill optimization loop | `30_system/docs/SKILL_OPTIMIZATION_AGENT.md` |
| Agentic workflow (Grill-me, PRD, vertical slices, Ralph loop) | `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md` |
| Scholarly workflow (research spec, milestones, LOOP ON/OFF) | `30_system/docs/SCHOLARLY_WORKFLOW.md` |
| Autonomy, TRIGGER handoffs, parallel fan-out / fan-in, token economics | `.cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md` |
| Chat komande, skillovi, Ralph/LOOP/autonomous (cheat sheet) | `.cursor/docs/COMMANDS_CHEAT_SHEET.md` |
| Graph connectivity map | `30_system/docs/GRAPH_CONNECTIVITY_MAP.md` |
| Automation linking index | `30_system/docs/AUTOMATION_INDEX.md` |
| Folder index hub | `30_system/docs/FOLDER_INDEX.md` |
| Non-markdown bridge notes | `30_system/docs/bridges/non_markdown_bridges.md` |
| Wiki hub | `20_knowledge/wiki/index.md` |
| Context nodes | `30_system/context/user.md`, `30_system/context/memory.md`, `30_system/context/soul.md` |

---

## Project state (when used inside a project)

- **Context index:** `.agent/README.md` – read first before planning.
- **Task, system, SOPs:** `.agent/task/`, `.agent/system/`, `.agent/SOPs/`.
- **Memory, handoff:** `.agent/MEMORY.md`, `.agent/handoff_log.jsonl`.
- **Phase context:** `30_system/04_documentation/context/main.md`, `commit.md`, `log.md` (when project contains brain).
- **Project wiki (optional):** `knowledge_system/` – see `30_system/docs/KARPATHY_WIKI.md`.

---

## Execution

- For architectural or multi-file changes, use **Plan Mode** (e.g. Shift+Tab) to propose changes before editing.
- For complex tasks, use sub-agents or Agent Teams (if enabled) to parallelize and avoid context contamination.
- For **long pipelines without unnecessary stops**, **subagent-triggered routing**, **parallel tracks with file-based merge**, and **when to parallelize to save context**, see `.cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md` (and token table in `context-optimization.mdc`).

## Semantic graph (auto)

- [[Orchestrator - agent roles]]
- [[Behavior rules hub]]
- [[20_knowledge/wiki/index]]
- [[Graph connectivity map]]
- [FOLDER INDEX](../../30_system/docs/FOLDER_INDEX.md)
- [GRAPH CONNECTIVITY MAP](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [FOLDER INDEX](../../30_system/docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[SKILL_agentic-react-os]]
- [[Engineering skill loop]]
- [[SKILL_scholarly-iteration-loop]]
- [[25_capability_registry]]
- [[Scholarly skill loop]]
