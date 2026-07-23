# SkillDAG Map (agent-rules)

**Version:** 1.0 | **Last updated:** 2026-06-05  
**Source:** NotebookLM *SkillDAG* notebook (`48a6afa2-97d8-44f4-8a41-c87d2ea0b650`); gate GO in [`outputs/notebooklm/skilldag_gate_report.json`](../../outputs/notebooklm/skilldag_gate_report.json).  
**External ledger:** [`notebooklm_skilldag_external_verification.json`](notebooklm_skilldag_external_verification.json)

Treat scale claims (10k+ skills), benchmark percentages, and GPT-5.x leaderboard numbers as **UNVERIFIED** in operational docs until locally reproduced or arXiv-verified.

---

## Disambiguation (read first)

| Concept | Scope | Repo artifact |
|---------|--------|---------------|
| **SkillRAE** | Subunit decomposition inside one skill (macro + micro compile) | `skill_decompose.py` → `outputs/skillrae/<id>_graph.json` |
| **SkillDAG** | Inter-skill typed DAG (routing between skills) | `registry.json` optional `depends_on`, `skill_pipelines_dag.json`, `skill_dag_validate.py` |
| **SkillOpt** | Content optimization of a single skill document | Geometry `model-native-skill-transform`; **no new skill** until arXiv 2605.23904 verified |

---

## Typed edge vocabulary (notebook → repo)

| Edge (notebook) | Meaning | Repo mapping |
|-----------------|---------|--------------|
| `depends_on` | B requires A loaded or completed first | `depends_on[]` on registry skill entry |
| `specializes` | Narrower variant of a parent skill | Document only (P2); not in registry v1 |
| `composes_with` | Complementary skills load together | `tier3_pairing.allowed_pairs` (runtime pair, not DAG edge) |
| `conflicts_with` | Must not load simultaneously | `conflicts_with[]` per skill + `tier3_pairing.forbidden_pairs` |

**Routing goal (notebook):** topological projection — select pipeline macros, graft micro-dependencies, avoid context bloat from flat cosine retrieval.

**Current repo routing:** `skill_rerank.py --dag` (TF-IDF + `depends_on` prerequisite injection + pipeline edge bonus). Flat-only: omit `--dag`. Procedural fallback: `SKILL_skill-dag-router.md`.

---

## Named pipeline DAGs (declarative)

Canonical file: [`skill_pipelines_dag.json`](skill_pipelines_dag.json)

| Pipeline ID | Entry → exit | skills-auto-detect row |
|-------------|--------------|------------------------|
| `agentic-engineering` | grill-me → write-prd → prd-to-issues → ralph-loop | Agentic PRD + Ralph |
| `scholarly-spec` | research-grill-me → write-research-spec → research-spec-to-milestones → scholarly-iteration-loop | Scholarly research spec |
| `notebooklm-before-prd` | notebooklm-research-gate → write-prd | Optional; gate before PRD from notebook synthesis |

Validate: `python 40_operations/scripts/skill_dag_validate.py`

---

## Repo touchpoints by layer

### L2 — Procedural skills (LifeHarness)

| Concern | Path |
|---------|------|
| Skill registry | `30_system/SKILLS/registry.json` |
| Pipeline table (human) | `.cursor/rules/skills-auto-detect.mdc` |
| Pipeline DAG (machine) | `30_system/docs/skill_pipelines_dag.json` |
| Flat rerank | `40_operations/scripts/skill_rerank.py` |
| DAG router (procedural) | `30_system/SKILLS/SKILL_skill-dag-router.md` |
| Subunit graph (SkillRAE) | `40_operations/scripts/skill_decompose.py` |
| Subunit vs inter-skill compare | `outputs/skillrae/skilldag_subunit_compare.md` |
| DAG validator | `40_operations/scripts/skill_dag_validate.py` |
| Registry validator | `40_operations/scripts/skill_registry.py` |

### L4 — Trajectory / gates

| Gate type (notebook) | Repo analog |
|---------------------|-------------|
| Validation gating (SkillOpt) | `skill_gap_optimize_gate.py`, eval `passes` in PRD JSON |
| Qualification (SkillAdaptor) | `skill_eval_runner.py`, append-eval on correction |
| Research gate | `SKILL_notebooklm-research-gate.md`, `notebooklm_bridge.py gate-report` |
| Swiss Cheese | `verification.mdc`, `SKILL_swiss-cheese.md` |
| HITL stage pause | Pipeline handoff in `00_orchestrator_agent.mdc` |

---

## Related notebooks (dedup — do not reopen PRDs)

| Notebook | ID | Owns |
|----------|-----|------|
| Geometry of Intelligence | `7c31671a-37df-4227-ac76-3ef2f5346d84` | SkillRAE-lite, model-native, phase memory, MCP prescreen |
| RAG Anatomy | `33feafbc-a75e-4e05-9eff-ae5394a08f05` | Corpus/query RAG, books_rag, harness four levers |
| **SkillDAG** | `48a6afa2-97d8-44f4-8a41-c87d2ea0b650` | Inter-skill DAG, registry dependency metadata, pipeline DAG JSON |

---

## Already covered (no duplicate work)

- `notebooklm-research-gate` + bridge scripts
- `tier3_pairing` (partial `conflicts_with` analog)
- LifeHarness map: `LIFEHARNESS_4_LAYER.md`
- Geometry + RAG Anatomy PRDs (`execution_chain.status: complete`)

---

## True gaps (remaining P2)

1. ~~Edge-weighted `skill_rerank --dag`~~ shipped 2026-06-05 (`brain_assist/skill_dag_rerank.py`)
2. `specializes` / `composes_with` as first-class registry edges
3. Execution-backed dynamic edge mutation from trajectories (with eval gates)
4. ~~`skill-dag-router` skill~~ done (SD-7); `--dag` rerank still open

---

## Extraction artifacts

| File | Role |
|------|------|
| [`outputs/notebooklm/skilldag_executive.md`](../../outputs/notebooklm/skilldag_executive.md) | One-page thesis |
| [`outputs/notebooklm/skilldag_vs_agent_rules_delta.md`](../../outputs/notebooklm/skilldag_vs_agent_rules_delta.md) | Delta vs repo |
| [`outputs/notebooklm/skilldag_skill_fit_assessment.md`](../../outputs/notebooklm/skilldag_skill_fit_assessment.md) | Skill coverage matrix |
| [`30_system/docs/reference/notebooklm_skilldag_grill_prompts.md`](reference/notebooklm_skilldag_grill_prompts.md) | 14 grill questions |

Re-grill: `python 40_operations/scripts/notebooklm_skilldag_grill_playwright.py`

---

## Related

- [[SkillDAG]] (wiki concept)
- [[SkillRAE retrieval augmented execution]]
- [[NotebookLM research gate]]
- [[LifeHarness four-layer model]]
- [[Skill gap pipeline]]
