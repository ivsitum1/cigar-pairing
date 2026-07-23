# Discovery Engine – Components and References

**Purpose:** Index of Discovery Engine components (MedDiscovery-inspired). Pipeline 7A (MVP) and 7B (full) are implemented; this doc points to where each piece lives and adds Dreaming and safety.

---

## 45-step scientific pipeline (implemented)

- **Where:** `30_system/behavior_rules/26_discovery_superpipeline.md` – clusters for Understanding, Disease Deep Dive, Evidence Mining, Ideation + Self-correction, Cross-Domain, Computational Chemistry, Protocol + Red Team + Council, Learning + Dreaming.
- **MVP (5 phases):** `30_system/behavior_rules/24_discovery_pipeline.md`. Orchestrator: `.cursor/rules/00_orchestrator_agent.mdc` (Pipeline 7A vs 7B).

---

## Multi-agent capability registry (implemented)

- **Where:** `30_system/behavior_rules/25_capability_registry.md` – agents include SafetyGuardian, ContextLoader, QueryClassifier, DiseaseDeepDive, EvidenceMiner, SemanticGate, CausalReasoner, IdeationAgent, CriticAgent, EvidenceConsistencyCheck, DisruptiveReasoningEngine, ChemAgent, ProtocolEngine, RedTeamAgent, AgentCouncil, AwakeningAgent, DreamingDaemon, LearningRecorder.

---

## Awakening Ritual (implemented)

- **Where:** `.cursor/docs/AWAKENING_RITUAL.md` – inputs (MEMORY, handoff log, log.md, commit.md), output (state summary). Optional Step 1 of Pipeline 7B.

---

## Dreaming Daemon (concept)

- **Idea:** During or after a Discovery run, optionally create **new knowledge frameworks** (e.g. cross-domain heuristics, failure-pattern summaries) and store them for future runs. Not a separate process; the DreamingDaemon is a logical role (RULES_MAINT or WRITING) that writes to a store.
- **Where:** Triggered optionally at Step 45b in `26_discovery_superpipeline.md`. Output: short framework docs with a score or tag; these can be loaded in a later run (e.g. Cluster 1, Step 6) to bias or enrich context.
- **Storage (canonical):** `.agent/dreams/`. One file per dream/framework. **Naming:** `dream_YYYYMMDD_HHMM.md` (timestamp-based) or `framework_<short_slug>.md` (e.g. `framework_cross_domain_cavitation.md`). Do not overwrite user data; create new files only.

---

## Tool connectors (data layer)

- **Current:** PubMed, filesystem, git, handoff, PDF in `.cursor/mcp.json`.
- **Discovery layer:** `.cursor/docs/MCP_AND_SKILLS_LAYERS.md` (section "Discovery data layer") – ClinicalTrials, Crossref, ChEMBL, PubChem, UniProt, STRING, KEGG, IntAct, RDKit, AutoDock Vina as planned MCP or scripts.

---

## Safety and limits

- The Discovery Engine **does not make clinical or regulatory decisions**. It proposes research concepts, protocol drafts, and computational starting points for **expert and regulatory review**.
- **Computational chemistry** (docking, candidate lists) is for hypothesis generation and starting points only; no claim that results are development-ready.
- **Red Team and Council** outputs are advisory; final approval and risk acceptance rest with the user and relevant authorities.
- See also: `30_system/behavior_rules/26_discovery_superpipeline.md` (Safety and limits), `.cursor/rules/core-principles.mdc`, `.cursor/rules/verification.mdc`.

---

## Index

- This doc: `.cursor/docs/DISCOVERY_ENGINE.md`
- Main layout: `.cursor/docs/INDEX.md`
- Super-pipeline: `30_system/behavior_rules/26_discovery_superpipeline.md`
- Registry: `30_system/behavior_rules/25_capability_registry.md`
- Awakening: `.cursor/docs/AWAKENING_RITUAL.md`

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
