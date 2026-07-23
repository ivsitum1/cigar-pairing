# Discovery Capability Registry (MedDiscovery-Inspired)

## Purpose

This document defines the **capability registry** for the Autonomous Discovery Engine: a declarative list of agents, their roles, triggers, tools, and outputs. Agents are logical roles executed by the Orchestrator adopting the appropriate subagent (WRITING, METHODOLOGY, STATISTICS, CODE_QA, etc.); they do not require separate processes. The registry is the single source of truth for which "agent" runs which step in the Discovery Super-pipeline.

**Reference:** Orchestrator: `.cursor/rules/00_orchestrator_agent.mdc`; Discovery pipelines: `30_system/behavior_rules/24_discovery_pipeline.md`, `30_system/behavior_rules/26_discovery_superpipeline.md`; subagent roles: `30_system/behavior_rules/15_agent_roles.md`.

---

## Registry Table

| Agent ID | Role | Subagent | Trigger / When | Tools (MCP / 40_operations/scripts) | Output |
|----------|------|----------|----------------|------------------------|--------|
| **SafetyGuardian** | Scope and safety check; block off-topic or high-risk intents | METHODOLOGY or RULES_MAINT | Start of Discovery run | — | Go / no-go; optional confidence |
| **ContextLoader** | Load project and user context before any reasoning | WRITING | RETRIEVE phase | Filesystem MCP, read `.agent/README.md`, `30_system/04_documentation/context/*` | Context brief, clarified discovery goal |
| **QueryClassifier** | Classify query (e.g. drug_discovery, disease_mechanism, trial_design) | METHODOLOGY | After context load | — | Query type, confidence |
| **DiseaseDeepDive** | PubMed disease search; extract mechanisms, targets, failure patterns | WRITING | DISCOVER phase when domain is disease/therapy | PubMed MCP, SKILL_literature-synthesis | Mechanisms, targets, failure patterns, paper set |
| **EvidenceMiner** | Multi-source evidence gathering; deduplicate; apply semantic gate | WRITING + METHODOLOGY | Evidence Mining cluster | PubMed, ClinicalTrials, Crossref MCP (when available); local scripts | Deduplicated source list; CORE/BACKGROUND/REJECTED tags |
| **SemanticGate** | Classify each source as CORE / BACKGROUND / REJECTED vs research question | WRITING | After Evidence Miner raw fetch | — | Per-source classification; batch summary |
| **CausalReasoner** | Build causal graph sketch (entities, relationships, failure modes) | METHODOLOGY | After evidence structured | — | Causal graph (nodes, edges), failure patterns |
| **IdeationAgent** | Generate initial hypotheses from gaps and evidence | METHODOLOGY | Ideation cluster | — | Ranked hypothesis list with scores |
| **CriticAgent** | Score hypothesis (e.g. 0–1); flag weaknesses | CODE_QA or METHODOLOGY | After each hypothesis batch | — | Score, critical/major/minor issues |
| **EvidenceConsistencyCheck** | Compare hypothesis to evidence; compute support ratio; decide pivot | METHODOLOGY | After first hypothesis | Evidence set, semantic gate output | Pass/fail; pivot query if fail |
| **DisruptiveReasoningEngine** | First-principles (physics, materials, info theory) to find biological weaknesses; cross-domain transfer | METHODOLOGY | Cross-Domain cluster | — | Layer-3 hypotheses, validation paths, paradigm-shift statements |
| **ChemAgent** | Find molecules (ChEMBL/PubChem); structural data; run docking stub | CODE_IMPL (or script) | Computational Chemistry cluster | ChEMBL, PubChem, RDKit, AutoDock Vina (MCP or 40_operations/scripts) | Candidate list; docking scores; "starting points" disclaimer |
| **ProtocolEngine** | Generate SPIRIT-aligned protocol draft | METHODOLOGY | Protocol cluster | reporting-spirit.mdc, CONSORT/PRISMA/STROBE refs | Protocol draft (sections, key design choices) |
| **RedTeamAgent** | Adversarial review: critical and major flaws | CODE_QA | After Protocol Engine | — | CRITICAL / MAJOR flaw list; optional MINOR |
| **AgentCouncil** | Aggregate scores; conditional approval / reject | METHODOLOGY | After Red Team | — | Council score (e.g. /100); approve / conditional / reject |
| **AwakeningAgent** | On Discovery session start: read MEMORY, log, handoff; output state summary | WRITING | Optional start of Pipeline 7B | Filesystem MCP, read `.agent/MEMORY.md`, handoff log, `log.md` | State summary (recent domains, prior directions, open gaps) |
| **DreamingDaemon** | Offline / idle: create new knowledge frameworks; store for future runs | RULES_MAINT or WRITING | Optional; async or end-of-run | Write to `dreams/` or knowledge store | New framework docs; scores |
| **LearningRecorder** | Emit LEARNING_BLOCK and update learning log for Discovery runs | WRITING | End of REFINE / Learning cluster | `30_system/behavior_rules/tools/ingest_learning_block.py` | LEARNING_BLOCK; log entry |

---

## Agent → Subagent Mapping (Summary)

- **WRITING:** ContextLoader, DiseaseDeepDive, EvidenceMiner (narrative), SemanticGate, AwakeningAgent, LearningRecorder.
- **METHODOLOGY:** SafetyGuardian, QueryClassifier, CausalReasoner, IdeationAgent, EvidenceConsistencyCheck, DisruptiveReasoningEngine, ProtocolEngine, AgentCouncil.
- **CODE_QA:** CriticAgent, RedTeamAgent.
- **CODE_IMPL:** ChemAgent (or external script invoked by Orchestrator).
- **RULES_MAINT:** SafetyGuardian (optional), DreamingDaemon.

---

## Tool Connectors (Data Layer)

Agents depend on the data layer. Current and planned connectors are documented in `.cursor/docs/MCP_AND_SKILLS_LAYERS.md` (Discovery data layer). No agent must hardcode data; all external data is fetched via MCP or documented scripts at execution time.

---

## Version

**Version:** 1.0  
**Last updated:** 2026-04-10  
**Status:** Active. Referenced by `26_discovery_superpipeline.md` and Orchestrator for Pipeline 7B.

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
