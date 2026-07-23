# Brain and project – separation and layout

**Purpose:** agent-rules is the "brain" (rules, scripts, MCP). The project (input, output, manuscript) lives outside the brain.

**Cursor rules (avoid duplicate stacks):** [CURSOR_RULES_SETUP.md](CURSOR_RULES_SETUP.md)  
**Health check PASS criteria:** [BRAIN_HEALTH_CRITERIA.md](BRAIN_HEALTH_CRITERIA.md)  
**GitHub branch protection:** [GITHUB_BRANCH_PROTECTION.md](GITHUB_BRANCH_PROTECTION.md)

---

## Brain vs project

| Brain (agent-rules) | Project |
|---------------------|---------|
| `.cursor/` – rules, MCP config | `01_input/` – literature, data, search strings |
| `40_operations/scripts/` – brain scripts | `02_analysis/` – R/Python scripts, working data |
| `30_system/behavior_rules/`, `30_system/SKILLS/` | `03_output/` – figures, tables, manuscript |
| Git: `git pull` to update brain | `30_system/04_documentation/` – protocol, SAP, context |
| Does not touch project content | `.agent/` – MEMORY, handoff, task output |

**Karpathy-style wiki (optional, project root):** `knowledge_system/` – durable markdown wiki edited and navigated **in Cursor** (`00_inbox/raw/` → `20_knowledge/wiki/` ingestion by the agent). Separate from MEMORY and from `30_system/04_documentation/context/log.md`. See [KARPATHY_WIKI.md](KARPATHY_WIKI.md). Created when you run `project_init.py`.

---

## Layout (project contains brain)

```
my-study/                     ← workspace root (Cursor opens here)
├── agent-rules/              ← brain (git clone/pull)
│   ├── .cursor/
│   ├── 40_operations/scripts/
│   ├── 30_system/behavior_rules/
│   └── 30_system/SKILLS/
├── .cursor → agent-rules/.cursor  (symlink)
├── .agent/
├── 01_input/
├── 02_analysis/
├── 03_output/
├── 30_system/04_documentation/
│   ├── context/                        ← main.md, commit.md, log.md
│   ├── protocol/
│   └── ...
├── 05_version_control/       ← changelog.md (milestones) + CHANGELOG_AUTO.* (git timeline)
├── knowledge_system/         ← optional: 00_inbox/raw/ → 20_knowledge/wiki/ (see KARPATHY_WIKI.md)
└── README.md
```

---

## Steps for new project

1. **Create project folder** and clone agent-rules inside:
   ```bash
   mkdir my-study
   cd my-study
   git clone https://github.com/.../agent-rules.git agent-rules
   ```

2. **Run project_init** (from agent-rules):
   ```powershell
   python agent-rules/40_operations/scripts/project_init.py
   ```
   Or with `--no-symlink` if symlink does not work (e.g. Windows without Admin/Developer Mode):
   ```powershell
   python agent-rules/40_operations/scripts/project_init.py --no-symlink
   ```

3. **Open project root in Cursor** – `my-study`, not `agent-rules`.

4. **Changelog (project)** — `project_init` seeds `05_version_control/changelog.md` and, if `.git` exists, installs a post-commit hook that updates `CHANGELOG_AUTO.md` / `.jsonl` via `project_changelog_auto.py`. Milestone edits go in `changelog.md`; commit timeline is automatic. Rule: `.cursor/rules/project-changelog.mdc`.

---

## Self-assessment i Swiss Cheese (Python)

Izvršavaju se iz **Pythona** (`40_operations/python/quality_validation/`), ne iz R-a. R ispod `40_operations/R/` ostaje za statistiku.

- Iz korijena repozitorija (standalone brain):  
  `python 40_operations/scripts/run_quality_validation.py assess --text "..." --domain statistics`
- Kad je `agent-rules/` podfolder: pokreni istu naredbu s radnim direktorijem koji sadrži `agent-rules/`, ili prilagodi relativne putanje.

Puna konvencija putanja: [CANONICAL_PATHS.md](CANONICAL_PATHS.md).

---

## Author-claims scope (brain vs project)

| Layer | What belongs | Tool |
|-------|----------------|------|
| **Brain** | Generic epistemic fences: population extrapolation, animal PK→human, protocol vs results, title-only claims, writing hygiene | `author_claims_check.py` (no `--project`); `output_controller_gate.py` Layer 1 |
| **Project** | Domain-specific phrasing from **your** corrections on one manuscript/study | `author_claims_check.py --project <id>`; `output_controller_gate.py --project <id>` |

Project packs live at `10_projects/projects/<id>/author_claims/rules.json`. Example: `sedacija-ecmo` (ECMO sedation chapter). The brain must **not** encode ultra-specific clinical doctrine globally.

---

## When to run git pull in agent-rules

- **Brain:** `cd agent-rules && git pull` – updates rules and scripts. Project data (01_input, 02_output, .agent) remains untouched.
- **Project:** If project has its own git repo at root, commit only project files; agent-rules is a separate submodule or subfolder.

---

## Backward compatibility

When agent-rules is **standalone** (workspace root = agent-rules, no 01_input in parent), scripts use agent-rules as project root. `01_input/` at brain root is optional; `.agent/` and `30_system/04_documentation/context/` may exist for brain maintenance and dogfooding. Existing behavior remains the same.
