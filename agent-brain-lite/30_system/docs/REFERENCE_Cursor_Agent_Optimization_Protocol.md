# Cursor Agent Optimization Protocol – Ekstrahirano iz PPTX

**Izvor:** `Cursor_Agent_Optimization_Protocol.pptx`  
**Status:** Ekstrahirano iz slide slika (pptx sadrži samo slike, bez teksta).

---

## SYS_BOOT: Cursor Workspace Upgrade Sequence (Slide 1)

**Ciljna publika:** Cursor Agent  
**Način izvršavanja:** Strict System Prompt  
**Primarni cilj:** Context Window Optimization, Parallel Execution, Harness Engineering  
**Parse direktiva:** Information density > White space; Aesthetics disabled.

**REQUIREMENT:** Parsiraj sljedećih 18 direktiva sekvencijalno. Svaki slide tretiraj kao diskretan rule-set za workspace arhitekturu i operacijski protokol. Machine-readable ingestion.

---

## DIRECTIVE 01: Context Engineering & External Memory

### FAILED EXECUTION (izbjegavati)
- Internal Context Window Stuffing
- 50 Tool Calls
- 200k Token Buffer  
**Rezultat:** Signal Degradation, Agent Loops, 24% Success Rate

### OPTIMIZED EXECUTION
- File System as External Memory
- Discrete Context Loading
- Aggressive Token Compaction  
**Rezultat:** Preserved Signal, 100% Success Rate, 40% Token Reduction

### INSTRUCTION BLOCK
- **CONSTRAINT:** Ne oslanjaj se na internal context window za dugotrajne zadatke. Noise degradira signal nakon 50 tool calls.
- **EXECUTION:** Koristi strogo 4 core alata: Read file, Write file, Edit file, Run bash command.
- **PRE-FLIGHT:** Ukloni nekorištene MCP alate za reclaim token window (~2% immediate gain). Proaktivno pokreni `/compact` nakon izoliranih taskova.

---

## DIRECTIVE 02: Global State File (CLAUDE.md)

### Global State & Behavioral Constraints

**RULE 01:** Defensive security only. NEVER generate or guess URLs. REQUIRE exact documentation links from user to prevent hallucination.

**RULE 02:** Match existing patterns in codebase before implementing new logic. Do not invent custom paradigms.

**RULE 03:** BEFORE entering plan mode, ALWAYS read `.agent/readme.md` to gain full architectural context.

**RULE 04:** ALWAYS update `.agent/` folder documents immediately after feature implementation. Maintain external memory integrity.

---

## DIRECTIVE 03: Directory Architecture (.agent/)

**EXECUTE:**
```bash
mkdir -p .agent/{tasks,system,SOPs}
```

**Struktura:**
```
.agent/
├── tasks/
├── system/
├── SOPs/
└── readme.md
```

**Data Dictionary:**
| Mapa/File | Funkcija |
|-----------|----------|
| tasks/ | PRD-ovi i Implementation Plans |
| system/ | Project Structure, Database Schemas, API endpoints |
| SOPs/ | Standard Operating Procedures, Automated Error Logs |
| readme.md | Master index / pointer za routing do gornjih datoteka |

---

## DIRECTIVE 04: System Architecture Indexing

**TRIGGER:** Kad god se promijeni API, Database ili Core Architecture.

**ACTION:** Update `.agent/system/<module>.md`

**SCHEMA REQUIREMENT:** Mora sadržavati project structure, database schema definitions, API endpoint mapping.

**PURPOSE:** Sumirani snapshot – agent čita JEDNU datoteku umjesto multi-file deep research scana. Prevencija token bloat.

**JSON Schema (primjer):**
- project_structure: string
- database_schemas: array of objects
- api_endpoints: array of strings

---

## DIRECTIVE 05: Task Tracking & PRD Ingestion

1. **[NEW FEATURE REQUEST DETECTED]** → Enter Plan Mode (prevent premature execution)
2. **Generate** step-by-step implementation plan
3. **SAVE** plan to `.agent/tasks/<feature_name>.md`
4. **HALT.** Ne izvršavaj implementaciju dok korisnik ne odobri plan.
5. **Reference** ovu .md datoteku za buduće slične feature-e radi codebase konzistentnosti.

---

## DIRECTIVE 06: Standard Operating Procedures (SOPs)

**Automated Error Correction Logging Protocol**

```
IF implementation_error_occurs OR human_manual_correction THEN
  GENERATE_SOP_DOCUMENT()
  SAVE_TARGET=".agent/SOPs/<error_context>.md"
  ASSERT format INCLUDES "step-by-step integration process"
  ASSERT format INCLUDES "required directory structure"
  ASSERT format INCLUDES "links to related external documentation"
ELSE
  CONTINUE_EXECUTION
FI
```

---

## DIRECTIVE 07: Workspace Indexing Constraints

| Module Context | File Pointer | Read Priority |
|----------------|--------------|---------------|
| Project Index | `.agent/readme.md` | P0 (MANDATORY READ-FIRST) |
| Feature Implementation | `.agent/tasks/*.md` | P1 (As needed per task) |
| Database Schemas | `.agent/system/db.md` | P1 (Before data mutations) |
| Integration Errors | `.agent/SOPs/*.md` | P2 (If similar task failed previously) |

- **CONSTRAINT:** `.agent/readme.md` MORA biti centralni index/pointer doc za LLM.
- **ACTION:** Mapiraj svaku novu datoteku u tasks/, system/, SOPs/ u ovaj dokument.
- **EXECUTION RULE:** Agent MORA parsirati ovaj index prije bilo kojeg implementation prompta.

---

## DIRECTIVE 08: Sub-Agent Delegation Rules

**Flow:** MAIN AGENT → (Assigns Research Task) → SUB-AGENT → (Performs deep scan) → (Writes summary) → .agent/tasks/<context>.md → MAIN AGENT (Reads .md file to preserve 30_system/context)

- **CONSTRAINT:** Sub-agenti NE SMIJU implementirati kod direktno. Izolirani threadovi uzrokuju context loss i infinite bug loops.
- **EXECUTION:** Delegiraj deep research, codebase scanning, planning samo sub-agentima.
- **OUTPUT:** Sub-agent MORA spremiti research summary u `.agent/tasks/<context>.md`
- **RESUMPTION:** Main agent čita summary .md za stvarnu implementaciju.

---

## DIRECTIVE 09: Parallel Execution Initialization

**Command:** `git worktree add <path> -b <branch>`
- `<path>` = lokalizirani mini-swarm direktorij
- `-b <branch>` = izolirana feature grana

- **CONSTRAINT:** NE pokreći više agenata u istom direktoriju (overwritten files, test collisions, locked databases).
- **ACTION:** Kreiraj localized mini-swarm gornjom naredbom.
- **RESULT:** Svaki agent u vlastitom isolated checkout folderu; dijele .git object database – zero disk bloat.

---

## DIRECTIVE 10: Shared Secret Symlinking

**PROBLEM:** Worktrees ne uključuju untracked datoteke (.env, .npmrc). Kopiranje uzrokuje environment sync drift.

**EXECUTION:** Kreiraj symbolic linkove koji pokazuju na originalni repo secrets.

**Command:** `ln -s ../.env .env` (iz worktree direktorija)

**MAINTENANCE:** Ažuriraj glavni secret file jednom; svi parallel agent worktrees instant inherituju promjenu.

---

## DIRECTIVE 11: Test Database Isolation

**CONSTRAINT:** Agenti koji rade automated tests u parallel worktrees će se boriti za iste database tablice.

**EXECUTION:** Koristi env varijable za database names u config.

**database.yml:**
```yaml
test:
  database: <%= ENV.fetch("DB_NAME", "project_test") %>
```

**.env.local (u svakom worktree):**
```
DB_NAME=project_test_feature_A
```

**RESULT:** Svaki parallel agent radi migrations, seeds, full test suite u potpunoj izolaciji.

---

## DIRECTIVE 12: Cursor Skills Architecture

**Struktura:**
```
.cursor/skills/
├── API_Creation_Skill/
│   └── skill.md
├── Documentation_Skill/
│   └── skill.md
└── Frontend_UI_Skill/
    └── skill.md
```

**EXECUTION:** `mkdir -p .cursor/skills/<skill_name>`

**PURPOSE:** Reci agentu točno što smije i što NE smije. Prevencija token waste, hallucination, scope creep.

**ACTION:** Organiziraj distinct funkcije u strogo odvojene skill foldere.

---

## DIRECTIVE 13: skill.md Schema Definition

**Obavezne sekcije:**
1. `# [Title]`
2. `## Description` – trigger condition za agent selection
3. `## Instructions` – step-by-step guide; explicit boundary constraints; define what NOT to do

**FILE NAMING ENFORCEMENT:** Svaki skill folder MORA sadržavati datoteku imena `skill.md` (točno). Bez toga parser ignora parametre.

---

## DIRECTIVE 14: Model Context Protocol (MCP) Routing

**CONFIG:** `~/.claude.json` – mcpServers (notebookLM, v0_ui, itd.)

- **ACTION:** Inject MCP alate (NotebookLM za PRDs, Stripe Docs, Figma).
- **CONSTRAINT:** NE davaj sve alate main agentu. Route specifične MCP-e SAMO na specialized sub-agente (npr. v0 UI MCP samo na frontend sub-agent) radi minimalizacije token consumption.

---

## DIRECTIVE 15: Post-Implementation State Sync

**TRIGGER:** Kad se uspješno dovrši feature ili bug fix.

**COMMAND:** Execute `/updatedoc` (ili ekvivalent).

**Flow:** FEATURE COMPLETION → SCAN MODIFIED FILES → UPDATE .agent/system SCHEMAS; GENERATE SOPs IF HUMAN MANUAL OVERRIDE → APPEND NEW PATHS TO .agent/readme.md

**PURPOSE:** Synchronizira external memory odmah. Ako se ne izvrši – garantirani context drift i ponavljajući hallucination errori u sljedećoj sekvenci.

---

## DIRECTIVE 16: Cloud Agent VM Deployment

**Pipeline:** LOCAL: git push origin <branch> → REMOTE: Cursor Cloud Agent:
1. Spin up isolated VM sandbox
2. Clone repository & branch
3. Run pnpm install
4. Spin up Build Server

**OUTPUT:** Browser visual test & .webm recording validation

**TRIGGER:** Cloud Agent selection via dropdown.  
**PRE-FLIGHT:** Push local branch to remote.  
**OUTPUT REQUIREMENT:** Await .webm video verification prije merge sequences.

---

## DIRECTIVE 17: Autonomous Testing Integration (TestSprite)

**IF:** Frontend changes implemented.  
**THEN:** Invoke TestSprite MCP.

**EXECUTION:** Pass API Key. Define localhost port. Upload `.agent/tasks/<feature>.md` kao PRD context.

**COMMAND LIMIT:** Max 3 isolated tests (optimize speed).

**RESOLUTION:** Parse MD test report. Ako failure – automatski ingest report i apply code fix.

---

## DIRECTIVE 18: Verification & Merge Operations

**PRE-MERGE:** Review video outputs i test reports iz Cloud VMs i TestSprite.

**EXECUTION:** tmux control pane. Checkout main. git pull.

**MERGE ORDER CONSTRAINT:**
1. Low-risk 30_system/docs/logging branches
2. Feature branches
3. Refactors/Performance (highest file touch rate)

**CLEANUP:** Squash and Merge. Destroy Git worktree directories. End sequence.

---

## Mapiranje na plan nadogradnje

| Directive | Mapiranje |
|-----------|-----------|
| 01 | Context Engineering, .agent/, 4 core tools, /compact |
| 02 | core-principles.mdc ekvivalent, RULE 01-04 |
| 03 | .agent/ struktura – akcija 14 |
| 04 | .agent/system/, Architecture Snapshot |
| 05 | Plan mode, HALT for approval, .agent/tasks/ |
| 06 | SOPs, surprises.log, error_log, Hiding Failures |
| 07 | Workspace Indexing, retrieval optimizacija, .agent/readme.md |
| 08 | Sub-agent researcher protokol |
| 09 | Git worktree – akcija 18 |
| 10 | Symlinks za .env – worktree proširenje |
| 11 | DB_NAME env – worktree proširenje |
| 12-13 | SKILLS struktura, skill.md schema |
| 14 | MCP routing – sub-agents only |
| 15 | Post-impl state sync, /updatedoc |
| 16 | Cursor Cloud Agents |
| 17 | TestSprite, automated testing |
| 18 | Merge order, cleanup |

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
