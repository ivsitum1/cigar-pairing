# Discovery Super-Pipeline (MedDiscovery-Style, ~45 Steps)

## Purpose

This document defines the **full Discovery Super-pipeline**: a fine-grained, multi-cluster workflow for drug/therapeutic discovery and research-direction generation. It extends the 5-phase Discovery Pipeline (`24_discovery_pipeline.md`) into explicit step-by-step stages that map to the **Capability Registry** (`25_capability_registry.md`). Used when the user requests a full "MedDiscovery-like" run (Pipeline 7B).

**Pipeline 7A** (MVP): use `24_discovery_pipeline.md` (5 phases).  
**Pipeline 7B** (full): use this super-pipeline and the capability registry.

---

## Overview: Clusters and Step Counts

| Cluster | Steps (approx) | Main agents | Output |
|---------|----------------|-------------|--------|
| 1. Understanding Before Thinking | 1–8 | SafetyGuardian, ContextLoader, QueryClassifier | Context brief, query type, go/no-go |
| 2. Disease Deep Dive | 9–15 | DiseaseDeepDive | Mechanisms, targets, failure patterns, paper set |
| 3. Evidence Mining | 16–24 | EvidenceMiner, SemanticGate | Deduplicated sources; CORE/BACKGROUND/REJECTED |
| 4. Ideation and Self-Correction | 25–32 | IdeationAgent, CriticAgent, EvidenceConsistencyCheck | Hypotheses; pivot if needed; chosen direction(s) |
| 5. Cross-Domain Reasoning | 33–36 | DisruptiveReasoningEngine | Layer-3 hypotheses, validation paths |
| 6. Computational Chemistry (optional) | 37–41 | ChemAgent | Candidate list; docking stub results |
| 7. Protocol, Red Team, Council | 42–44 | ProtocolEngine, RedTeamAgent, AgentCouncil | Protocol draft; flaw list; council score |
| 8. Learning and Dreaming | 45 | LearningRecorder; optional DreamingDaemon | LEARNING_BLOCK; optional new frameworks |

---

## Cluster 1: Understanding Before Thinking (Steps 1–8)

| Step | Name | Agent | Input | Tools | Output | On success | On failure |
|------|------|-------|-------|-------|--------|------------|-----------|
| 1 | Awakening (optional) | AwakeningAgent | — | Read MEMORY, log, handoff | State summary | → 2 | → 2 |
| 2 | Load context | ContextLoader | User prompt; project paths | Filesystem MCP, `.agent/README.md`, `30_system/04_documentation/context/*` | Context brief, discovery goal | → 3 | → 3 |
| 3 | Safety and scope | SafetyGuardian | Context brief, goal | — | Go / no-go, scope limits | → 4 if go | Stop; report |
| 4 | Classify query | QueryClassifier | Goal, context | — | Query type (e.g. drug_discovery), confidence | → 5 | → 5 |
| 5 | Select pipeline variant | Orchestrator | Query type, user intent | — | 7A vs 7B; cluster path | → 6 | → 6 |
| 6 | Load knowledge frameworks (if any) | ContextLoader | Registry of frameworks | Read from `.agent/dreams/` (see DISCOVERY_ENGINE.md: naming `dream_*.md` or `framework_*.md`) | Loaded set (optional) | → 7 | → 7 |
| 7 | Consciousness dialogue (optional) | WRITING/METHODOLOGY | Context, goal | Internal debate / multi-view | Consensus thoughts (optional) | → 8 | → 8 |
| 8 | Handoff to Disease Deep Dive | — | Context + query type | — | — | → Cluster 2 | — |

---

## Cluster 2: Disease Deep Dive (Steps 9–15)

| Step | Name | Agent | Input | Tools | Output | On success | On failure |
|------|------|-------|-------|-------|--------|------------|-----------|
| 9 | Build PubMed queries | DiseaseDeepDive | Disease/therapy keywords from context | — | 5–7 query strings | → 10 | → 10 |
| 10 | Execute PubMed searches | DiseaseDeepDive | Queries | PubMed MCP | Raw result set | → 11 | → 11 (degrade) |
| 11 | Deduplicate papers | DiseaseDeepDive | Raw set | — | Unique paper list (e.g. up to ~100) | → 12 | → 12 |
| 12 | Extract mechanisms | DiseaseDeepDive | Papers (abstracts/titles) | SKILL_literature-synthesis if applicable | 8–12 molecular/pathway mechanisms | → 13 | → 13 |
| 13 | Extract targets | DiseaseDeepDive | Papers, mechanisms | — | 3–6 molecular targets | → 14 | → 14 |
| 14 | Map failure patterns | DiseaseDeepDive | Papers, mechanisms | — | 2–4 treatment-failure patterns | → 15 | → 15 |
| 15 | Handoff to Evidence Mining | — | Mechanisms, targets, failures, paper set | — | — | → Cluster 3 | — |

---

## Cluster 3: Evidence Mining (Steps 16–24)

| Step | Name | Agent | Input | Tools | Output | On success | On failure |
|------|------|-------|-------|-------|--------|------------|-----------|
| 16 | Build multi-DB query plan | EvidenceMiner | Disease/targets, question | — | Query plan (PubMed, ClinicalTrials, Crossref, etc.) | → 17 | → 17 |
| 17 | Execute PubMed batch | EvidenceMiner | Plan | PubMed MCP | PubMed hits | → 18 | → 18 |
| 18 | Execute other DBs (if available) | EvidenceMiner | Plan | ClinicalTrials, Crossref MCP or scripts | Additional hits | → 19 | → 19 |
| 19 | Merge and deduplicate | EvidenceMiner | All hits | — | Deduplicated source list (e.g. 300–600) | → 20 | → 20 |
| 20 | AI Semantic Gate – batch 1 | SemanticGate | Subset, research question | — | CORE/BACKGROUND/REJECTED per item | → 21 | → 21 |
| 21 | AI Semantic Gate – remaining batches | SemanticGate | Rest in batches | — | Full classification | → 22 | → 22 |
| 22 | Summarise gate | SemanticGate | Classifications | — | Counts: CORE, BACKGROUND, REJECTED | → 23 | → 23 |
| 23 | Causal graph sketch | CausalReasoner | Mechanisms, targets, evidence | — | Entities, relationships, failure modes | → 24 | → 24 |
| 24 | Handoff to Ideation | — | Evidence set, causal graph, disease summary | — | — | → Cluster 4 | — |

---

## Cluster 4: Ideation and Self-Correction (Steps 25–32)

| Step | Name | Agent | Input | Tools | Output | On success | On failure |
|------|------|-------|-------|-------|--------|------------|-----------|
| 25 | Generate initial hypotheses | IdeationAgent | Gaps, evidence, causal graph | — | 5–15 candidate hypotheses | → 26 | → 26 |
| 26 | Score hypotheses (Critic) | CriticAgent | Hypotheses | — | Score per hypothesis (e.g. 0–1); issues | → 27 | → 27 |
| 27 | Select top hypothesis | IdeationAgent | Scores | — | Top 1 (or 2) for consistency check | → 28 | → 28 |
| 28 | Evidence Consistency Check | EvidenceConsistencyCheck | Top hypothesis, CORE evidence | — | Support ratio; safety/concern count | → 29 if pass | → 30 if fail |
| 29 | Lock direction; optional second hypothesis | — | — | — | Chosen direction(s) | → 31 | — |
| 30 | Pivot: re-ideate with new query | IdeationAgent + CausalReasoner | Pivot query, evidence | — | New hypothesis set | → 26 | → 26 (retry or degrade) |
| 31 | Document pivot count (if any) | LearningRecorder | Run history | — | hypothesis_pivots | → 32 | → 32 |
| 32 | Handoff to Cross-Domain or Protocol | — | Chosen hypothesis(es) | — | — | → Cluster 5 or 7 | — |

---

## Cluster 5: Cross-Domain Reasoning (Steps 33–36)

| Step | Name | Agent | Input | Tools | Output | On success | On failure |
|------|------|-------|-------|-------|--------|------------|-----------|
| 33 | Identify fundamental weaknesses | DisruptiveReasoningEngine | Disease, mechanisms, failures | First-principles (physics, materials, info theory) | 4–6 fundamental weaknesses | → 34 | → 36 |
| 34 | Generate Layer-3 hypotheses | DisruptiveReasoningEngine | Weaknesses | Cross-domain transfer | 3–5 hypotheses with validation path | → 35 | → 35 |
| 35 | Paradigm-shift statements | DisruptiveReasoningEngine | Layer-3 hypotheses | — | Short statements per hypothesis | → 36 | → 36 |
| 36 | Handoff to Chem or Protocol | — | Layer-3 + main direction | — | — | → Cluster 6 or 7 | → Cluster 7 |

---

## Cluster 6: Computational Chemistry (Optional, Steps 37–41)

| Step | Name | Agent | Input | Tools | Output | On success | On failure |
|------|------|-------|-------|-------|--------|------------|-----------|
| 37 | Target selection for chemistry | ChemAgent | Hypothesis, targets | — | 1–2 targets to search | → 38 | Skip to 42 |
| 38 | ChEMBL/PubChem search | ChemAgent | Targets | ChEMBL, PubChem MCP or script | Candidate molecules | → 39 | → 41 |
| 39 | Enrich structures | ChemAgent | Candidates | RDKit or script | SMILES, basic props | → 40 | → 41 |
| 40 | Docking stub (if available) | ChemAgent | Protein + ligands | AutoDock Vina or script | Docking scores; "starting points only" note | → 41 | → 41 |
| 41 | Handoff to Protocol | — | Candidates, docking note | — | — | → Cluster 7 | → Cluster 7 |

---

## Cluster 7: Protocol, Red Team, Council (Steps 42–44)

| Step | Name | Agent | Input | Tools | Output | On success | On failure |
|------|------|-------|-------|-------|--------|------------|-----------|
| 42 | Generate protocol draft | ProtocolEngine | Hypothesis, design type | reporting-spirit.mdc, CONSORT refs | SPIRIT-aligned draft (sections, design) | → 43 | → 43 |
| 43 | Red Team review | RedTeamAgent | Protocol draft | — | CRITICAL / MAJOR (and optional MINOR) flaws | → 44 | → 44 |
| 44 | Agent Council | AgentCouncil | Protocol, Red Team list | — | Council score (e.g. /100); approve / conditional / reject | → Cluster 8 | → Cluster 8 |

### Red Team Tie-Breaking

If Red Team voting ends in a tie (equal votes for and against proceeding):

1. The RedTeamAgent's vote counts double (weighted vote)
2. If still tied after weighted vote: proceed with modification
   - Document the unresolved objection explicitly
   - Carry it forward as an open caveat in the protocol output
   - Flag in the LEARNING_BLOCK for post-study review

Rationale: a tied Red Team signals genuine uncertainty — proceeding with a documented caveat
is more useful than a full stop, but the objection must be visible.

---

## Cluster 8: Learning and Dreaming (Step 45)

| Step | Name | Agent | Input | Tools | Output | On success | On failure |
|------|------|-------|-------|-------|--------|------------|-----------|
| 45 | Emit LEARNING_BLOCK and record | LearningRecorder | Full run summary, pivots, scores | `30_system/behavior_rules/tools/ingest_learning_block.py` | LEARNING_BLOCK (drug_discovery); log entry | End | End |
| 45b | Dreaming (optional, async) | DreamingDaemon | Run summary, open questions | Write to `.agent/dreams/`; one file per output: `dream_YYYYMMDD_HHMM.md` or `framework_<slug>.md` | New knowledge framework docs | — | — |

---

## When to Use Pipeline 7A vs 7B

- **7A (MVP):** User asks for "research directions", "gap identification", "explore options" without explicitly requesting full drug-discovery or multi-DB evidence + protocol + Red Team. Use `24_discovery_pipeline.md` (5 phases).
- **7B (Full):** User says "novel therapeutic strategy", "drug discovery", "run full discovery", "MedDiscovery-style", or requests protocol + adversarial review + multi-source evidence. Use this super-pipeline and `25_capability_registry.md`.

Orchestrator decides 7A vs 7B from classification and keywords (see `00_orchestrator_agent.mdc`).

---

## Safety and Limits

- The Discovery Engine **does not make clinical decisions**. It proposes research concepts and protocol drafts for expert review.
- Computational chemistry outputs are **starting points only**; no claim that docking results are development-ready.
- All high-impact or clinical-use outputs require **expert and regulatory review** before use.
- See also core principles (`.cursor/rules/core-principles.mdc`) and verification (`.cursor/rules/verification.mdc`).

---

## References

- Capability registry: `30_system/behavior_rules/25_capability_registry.md`
- MVP Discovery pipeline: `30_system/behavior_rules/24_discovery_pipeline.md`
- Orchestrator and Pipeline 7: `.cursor/rules/00_orchestrator_agent.mdc`
- Learning Loop: `30_system/behavior_rules/14_learning_loop.md`
- Awakening: `.cursor/docs/AWAKENING_RITUAL.md`

**Version:** 1.0  
**Last updated:** 2026-04-10  
**Status:** Active for Pipeline 7B.

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
