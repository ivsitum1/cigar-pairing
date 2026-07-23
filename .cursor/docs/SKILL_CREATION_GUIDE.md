# Skill Creation Guide

How to add a new procedural skill to this system.
**Reference:** `30_system/behavior_rules/27_rule_maintenance.md` (rule maintenance); `skills-auto-detect.mdc` (loading protocol); `30_system/SKILLS/registry.json` (single source of truth for skill metadata).

---

## Concepts: Skill vs. Cursor Rule vs. MCP

| Type | File location | Who loads it | When to create |
|---|---|---|---|
| **Skill** (`SKILL_*.md`) | `30_system/SKILLS/` | On-demand via trigger or `@skill-name` | Multi-step procedural workflow with clear entry/exit |
| **Cursor rule** (`.mdc`) | `.cursor/rules/` | Always or via glob | Behavioral guidance active across many tasks |
| **MCP server** | `.cursor/mcp_servers/` + `.cursor/mcp.json` | Persistent process | External API integration, new tool capability |

Create a **Skill** when the task is a named, reusable, multi-step procedure (e.g., "run meta-analysis", "check PRISMA", "write a case report"). Create a **Cursor rule** when the behavior should color ALL work in a domain (e.g., "always avoid em dashes").

---

## Part A — Creating a New Skill

### Step 1: Choose a name and verify no conflict

Check `30_system/SKILLS/registry.json` — `disambiguation` fields tell you what each existing skill covers. If your new skill overlaps with an existing one, extend that skill rather than creating a duplicate.

Naming convention: `SKILL_<kebab-case-name>.md`

### Step 2: Write `SKILL_<name>.md`

Save to `30_system/SKILLS/`. Use this frontmatter:

```markdown
---
name: skill-name
description: One sentence: what this skill does. Second sentence: when to trigger it (user phrases, contexts).
version: 1.0
last_updated: YYYY-MM-DD
domain: writing | statistics | methodology | setup | validation | figures | tools | engineering
tokens: ~NNN              # approximate token count of this file; used for budget checks
triggers:
  - trigger phrase 1
  - trigger phrase 2 (in English and Croatian if relevant)
requires_packages: []     # R/Python packages needed; [] if none
reference_files: []       # relative paths to files loaded on demand; [] if none
pipeline_position: []     # pipeline numbers where this skill is used; [] if standalone
conflicts_with: []        # skill IDs that cannot be active at the same time
---

# Skill: <Human-Readable Title>

## When to use

- Bullet list of situations that trigger this skill
- Include what it does NOT cover (disambiguation)

## Prerequisites

- What the user must provide or have ready before running this skill

## Step-by-step procedure

### 1. [First step]
...

### 2. [Second step]
...

## Output

What the skill produces and where it saves output.

## Quality check

How to verify the output is correct.
```

**Body length:** Keep under 400 lines. If you exceed this, move reference material to `20_knowledge/reference_library/` and list files in the `reference_files` frontmatter field with a note about when to load each.

**Why precise triggers matter:** The auto-detect system (`skills-auto-detect.mdc`) matches user intent against the `triggers` field. Vague triggers cause false positives or misses. Include both English and Croatian phrasings for any trigger a Croatian-speaking user might type.

### Step 3: Register in `30_system/SKILLS/registry.json`

Add an entry to the `"skills"` array (maintain alphabetical order by `id`):

```json
{
  "id": "skill-name",
  "file": "SKILL_skill-name.md",
  "domain": "writing",
  "triggers": ["trigger phrase 1", "trigger phrase 2"],
  "conflicts_with": [],
  "disambiguation": "Use when X; NOT when Y; prefer Z if the user wants W."
}
```

The `disambiguation` field is critical — it is read when two skills have overlapping triggers to decide which one to load.

### Step 4: Add to `skills-auto-detect.mdc`

Add the skill ID to the relevant group in the `## Task → Skill (grouped)` table. If the skill participates in a named pipeline, add it to the `## Pipeline Skill Sequence` table as well.

### Step 5: Add to `30_system/behavior_rules/22_pipeline_and_refinement.md` (if pipeline-relevant)

If the skill fits into an existing pipeline (1–7B), add a row or note to the pipeline table there. If it defines a new pipeline, document it under a new named pipeline entry.

### Step 6: Verify

1. Open Cursor. Type a trigger phrase in chat.
2. The skill should be detected and loaded (you'll see it referenced in the agent's reasoning).
3. If not detected: tighten the `triggers` list and update both `registry.json` and `skills-auto-detect.mdc`.
4. Run `40_operations/scripts/skill_registry.py` to validate registry consistency.

---

## Part B — Creating a Companion Cursor Rule

Create a `.cursor/rules/*.mdc` when you need the skill's key principles to be **always active** (not only when the skill is explicitly triggered). This is optional but useful for behavioral guidelines.

```markdown
---
description: "One sentence description for Cursor's rule selector."
globs: ["**/*.py", "**/*.R"]   # omit if rule should apply everywhere
alwaysApply: false             # true only for global behavioral rules
---

# Rule Title

... concise version of the key principles from the SKILL ...

**Full procedure:** `30_system/SKILLS/SKILL_skill-name.md`
```

Keep `.mdc` files under 80 lines — they are loaded into every matched context. Use them for principles and warnings; put the full step-by-step procedure in the SKILL file.

---

## Part C — Adding an MCP Server

For new tool capabilities (external API, persistent process):

1. **Implement** the server in `.cursor/mcp_servers/` using the MCP SDK (see `handoff_server.py` as an example).
2. **Register** in `.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "server-name": {
         "command": "python",
         "args": [".cursor/mcp_servers/my_server.py"]
       }
     }
   }
   ```
3. **Write a companion Skill** (Part A above) that explains when to call the MCP's tools and in what order.
4. **Document** the distinction between skill logic and MCP data in `.cursor/docs/MCP_AND_SKILLS_LAYERS.md`.

---

## Maintenance Checklist

```
[ ] 30_system/SKILLS/SKILL_<name>.md          — frontmatter + procedure
[ ] 30_system/SKILLS/registry.json            — new entry added, alphabetical order
[ ] .cursor/rules/skills-auto-detect.mdc  — skill added to task→skill table
[ ] 30_system/behavior_rules/22_pipeline_and_refinement.md  — pipeline updated (if relevant)
[ ] .cursor/rules/<name>.mdc        — created (optional, for always-on principles)
[ ] 40_operations/scripts/skill_registry.py       — run to validate registry
```

**When updating an existing skill:** bump `version` and `last_updated` in frontmatter; add an entry to `30_system/behavior_rules/CHANGELOG.md` following the existing format.

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
