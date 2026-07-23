# MCP and Skills Layers (Data vs Logic)

**Purpose:** Define the hierarchy between MCP (data) and Skills (logic). Skills provide the process; MCP provides the capability. Skills must not hardcode data that can be fetched via MCP.

---

## MCP (Data Layer)

- **Role:** Bridge to external data. MCP servers expose tools to read, search, or modify external systems (filesystem, git, PubMed, PDFs, handoff log, etc.).
- **Configuration:** `.cursor/mcp.json` (filesystem, git, pubmed, consensus, handoff, memory, pdf, notebooklm in this workspace).
- **Rule:** When a process needs external data (e.g. literature, repo state, 40_operations/logs), the agent **invokes MCP tools** (or read/write file tools). Data is not embedded in skills or rules.

---

## Skills (Logic Layer)

- **Role:** Provide the "how" – process steps, triggers, allowed tools, and when to use them. Skills define *when* and *how* to use capabilities; MCP provides the *what* (e.g. "search PubMed", "read file").
- **Location:** `30_system/SKILLS/SKILL_*.md`; **meta / skill-maker bridge** at `.cursor/skills/skill-builder.md` (routes to `SKILL_create-skill.md` + registry); Obsidian vault + syntax at `SKILL_obsidian-wiki-agent.md` with deep reference `30_system/SKILLS/reference/OBSIDIAN_AGENT_PLAYBOOK.md`.
- **Rule:** A skill describes the process. When that process needs external data, the agent uses MCP or read/write tools rather than embedding that data in the skill file.

---

## Hierarchy

- **Skills trigger MCP:** A skill step may say "search PubMed for X" or "load handoff log"; the agent then calls the appropriate MCP tool. The skill does not contain the search results.
- **No hardcoded data:** Do not paste API responses, database dumps, or fetched content into skills. Reference the source (e.g. "use PubMed MCP") and fetch at execution time.
- **Future connectors:** ChEMBL, UniProt, AutoDock Vina, or other data sources would be added as MCP servers (or 40_operations/scripts) in the data layer and invoked by skills when the process requires them.

---

## Agent-native CLI complement

MCP covers discovery and IDE-facing tools; **thin CLIs** under `40_operations/scripts/` (often Python here) remain appropriate when responses are bulky JSON, pagination/rate limits dominate, or auth should stay local. That split reduces raw payloads reaching the model and supports lazy discovery via subcommands. See [CLI vs MCP for agent-native workflows](CLI_VS_MCP_AGENT_NATIVE.md) (same folder) for decision criteria and audit checks.

---

## Discovery data layer (Pipeline 7B)

Used by the Discovery Super-pipeline (`30_system/behavior_rules/26_discovery_superpipeline.md`) and capability registry (`30_system/behavior_rules/25_capability_registry.md`). Agents must never hardcode results; all data is fetched at execution time via MCP or documented scripts.

**Status:** **Current** = configured in `.cursor/mcp.json` and available today. **Planned** = not yet configured; Pipeline 7B uses only Current connectors until they are added.

| Connector | Purpose | Status | Used by |
|-----------|---------|--------|---------|
| PubMed | Literature search, disease/therapy evidence | Current (`.cursor/mcp.json`) | DiseaseDeepDive, EvidenceMiner |
| Consensus | Peer-reviewed quick search (OAuth MCP) | Current (`.cursor/mcp.json`) | research-lookup, WRITING/METHODOLOGY |
| arXiv (CLI) | Monthly stat/CS preprint skill scout | Current (`arxiv_monthly_scan.py`) | arxiv-skill-scout |
| Filesystem / Git | Project context, MEMORY, log, handoff | Current | ContextLoader, AwakeningAgent |
| ClinicalTrials.gov | Trial registry search | Planned (MCP or HTTP script) | EvidenceMiner |
| Crossref | Publication metadata, DOIs | Planned | EvidenceMiner |
| ChEMBL | Molecule targets, activities | Planned (MCP or script) | ChemAgent |
| PubChem | Structures, SMILES, compounds | Planned | ChemAgent |
| UniProt | Protein targets, sequences | Planned | ChemAgent, DisruptiveReasoning |
| STRING / KEGG | Pathways, interactions | Planned | CausalReasoner, EvidenceMiner |
| IntAct | Molecular interactions | Planned | EvidenceMiner |
| RDKit | SMILES validation, basic chemistry | Planned (local script) | ChemAgent |
| AutoDock Vina | Docking stub (scores only) | Planned (local or Docker) | ChemAgent |

Outputs of computational chemistry (docking, candidates) are **starting points only**; they do not replace expert medicinal chemistry or regulatory assessment.

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
