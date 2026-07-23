# Ubiquitous language

Shared glossary for **this repository** (agent rules, orchestration, research tooling). Extend when introducing new domain concepts in code, rules, or user-facing docs.

**Rule:** Prefer defining or updating terms **here before** proliferating synonyms in implementation (`54_strategic_engineering.mdc`).

## Related Nodes

- [[README]]
- [[30_system/docs/README]]
- [[30_system/docs/GRAPH_CONNECTIVITY_MAP]]
- [[.cursor/docs/INDEX]]
- [[WORKSPACE_RECONSTRUCTION_GUIDE]] (file `30_system/WORKSPACE_RECONSTRUCTION_GUIDE.md`)

---

## How to maintain

1. Add **Term** → short definition → optional contrast (“Not to be confused with…”).
2. When renaming concepts, update this file and grep for old names.
3. For **application projects** copied alongside these rules, either symlink/project-specific `UBIQUITOUS_LANGUAGE.md` or maintain a separate glossary in that repo.

---

## Core tooling & workflow

| Term | Definition |
|------|------------|
| Orchestrator | Single routing role for tasks/subagents (`00_orchestrator_agent.mdc`). |
| Skill | Tiered procedural bundle (`SKILL.md`), loaded per context (`skills-auto-detect.mdc`). |
| Grill-me | Alignment questioning **before** locking PRD/spec (`SKILL_grill-me.md`). |
| PRD | Product/requirements artifact (`30_system/docs/prd.json`, `30_system/docs/prd.md`) — not PRISMA. |
| Scaffold | Procedural knowledge layer: how a problem class should be decomposed, what evidence counts, workflow order. Implemented as `SKILL_*.md`, pipelines, checklists. **Not** tool execution. |
| Harness | Runtime layer that instantiates scaffold as action: MCP/tools, hooks, memory trim, loop control (ReAct/TAOR), handoff log. Maps to LifeHarness L3–L4. |
| Skill tree | Domain grouping of related skills with shared `intent` (business/OS layer). **Not** routing — use SkillDAG for load order. |
| SkillDAG | Typed DAG over registry skills (`depends_on`, pipeline groups); routing via `skill_rerank --dag`. |
| Self-Harness | Iterative harness improvement from failure traces (Weakness Mining → Proposal → Validation). **Policy:** gated experiments only; no autonomous `.cursorrules` / `behavior_rules` rewrite without human approval. See arXiv:2606.09498. |
| Information folding | After sub-goal success, replace micro-history with a compact solved-lemma summary; prevents context pollution (HIP-If pattern). |
| HORMA | Hierarchical Organize-and-Retrieve Memory Agent; file-system-like memory with provenance pointers. See arXiv:2606.11680. |
| HIPIF | Hierarchical Planning and Information Folding; fold completed subgoal history into compact lemmas. See arXiv:2606.10507. Maps to `context_sync --fold-lemma`. |
| Agents-K1 | Agent-native knowledge orchestration pipeline (4B extractor + multimodal graph). See arXiv:2606.13669. |
| Metamemory | Knowing what to encode, when to retrieve, and how to organize knowledge — the *skill* of managing memory, not the stored content. Cognitive-science term adopted by AutoMem. |
| AutoMem | Stanford framework treating memory management as a trainable skill via dual loops: (1) structure revision from trajectory review, (2) proficiency from successful memory decisions. See arXiv:2607.01224. **Not** weight fine-tuning in this repo — adapt as harness patterns only. |
| Memory-as-filesystem | Memory exposed as addressable file operations (paths, schemas, append/read) rather than opaque vector stores. Maps to `.agent/memory_hierarchy/`, `solved_lemmas.jsonl`, MCP filesystem. |
| Memory op | First-class harness action for memory: **log**, **read**, **write**, or **plan**. Mechanically separable from domain task actions (analysis, coding, writing). See `memory-ops` skill cluster. |
| Task op | Domain action toward user deliverable (run analysis, edit manuscript, implement script). **Not** a memory op — though it may trigger memory ops as side effects. |

---

## Research / reporting (high level)

| Term | Definition |
|------|------------|
| PICO | Population, Intervention, Comparator, Outcomes — study question scaffold. |
| Swiss Cheese validation | Layered verification before high-stakes conclusions (`verification.mdc`). |

---

## Reserved — fill per subdomain

_Add rows as needed (e.g. specific pipelines, statistical estimands, deployment environments)._

| Term | Definition |
|------|------------|
| | |
