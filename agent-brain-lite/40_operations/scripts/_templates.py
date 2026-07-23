"""Shared templates for context files used by brain_init, project_init, and context_sync."""

MAIN_TEMPLATE = """# main.md – Global Project Context

**Purpose:** Study type, PICO, main outputs. Single source of truth for project scope.

---

## Template

- **Study type:** [RCT | observational | systematic review | meta-analysis | …]
- **PICO (if applicable):** [Population, Intervention, Comparison, Outcome]
- **Primary outcome:** [variable, metric]
- **Main deliverables:** [list]

## Data contracts (codebooks)

- **Extraction codebook (SR/MA):** `01_input/data_extraction/codebook.md`
- **Dataset codebook (own CSV):** `01_input/codebook/dataset_codebook.md`

Agents read the relevant codebook before extraction, EDA, or inferential analysis. Column names in sheets must match `variable_name` in the codebook.

---
"""

COMMIT_TEMPLATE = """# commit.md – Milestones (per branch/phase)

**Purpose:** What is "done" in this phase. Updated at milestone boundaries.

---

- **Phase:** (not set)
- **Completed:** (none)
- **Next:** (none)

---
"""

LOG_TEMPLATE = """# log.md – OTA History (Observation, Thought, Action)

**Purpose:** Agent logs what it noticed, thought, and did. Supports continuity in long sessions.

---

## Format

`[YYYY-MM-DD HH:MM] [O|T|A] Brief entry.`

---
"""

MEMORY_TEMPLATE = """# MEMORY.md – Agent Auto-Progress

**Max:** ~200 lines. Agent appends progress here; trim when exceeded.

---

## Format

`[YYYY-MM-DD] [task] Brief description of progress.`

---
"""

README_TEMPLATE = """# Project

Created with `project_init.py` from agent-rules. See `agent-rules/30_system/docs/BRAIN_AND_PROJECT.md` for layout.
"""

CHANGELOG_TEMPLATE = """# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

**Git timeline (auto):** each commit is also logged to `CHANGELOG_AUTO.md` and
`CHANGELOG_AUTO.jsonl` in this folder when the post-commit hook is installed
(`project_init.py`).

## [Unreleased]

### Added
- Project initialized via `project_init.py`

### Notes
- Update this file for milestone-level changes (new analysis, SAP revision, manuscript freeze).
- Commit-level detail lives in `CHANGELOG_AUTO.md`.
"""

PROJECT_CHANGELOG_AUTO_README = """# Project auto changelog

Git commits at the **project root** append to:

- `05_version_control/CHANGELOG_AUTO.md` — human-readable timeline
- `05_version_control/CHANGELOG_AUTO.jsonl` — machine-readable log

## Hook

Installed by `project_init.py` when `.git` exists at project root.
Source: `agent-rules/40_operations/scripts/project-post-commit-hook.sh`

Skip one amend: `SKIP_CHANGELOG=1 git commit --amend --no-edit`

## Manual

```bash
python agent-rules/40_operations/scripts/project_changelog_auto.py --root .
python agent-rules/40_operations/scripts/project_changelog_auto.py --root . --backfill
```

See also `agent-rules/30_system/docs/CHANGELOG_AUTO_README.md` (brain repo pattern).
"""

KARPATHY_INDEX_TEMPLATE = """# Wiki index

**Purpose:** Entry map for the project knowledge wiki (`knowledge_system/20_knowledge/wiki/`). Update when you add or rename topic pages. Navigate here in **Cursor** (Explorer or Quick Open); use **`@knowledge_system/20_knowledge/wiki/index.md`** in chat when you want the agent to sync structure.

---

## Topics

(Add sections or bullet lists. Prefer relative links so the IDE can open targets: `[Short label](topic-slug.md)`. Optional compact refs: `[[Page Title]]` for see-also — not tied to any external app.)

- (none yet)

---
"""

KARPATHY_WIKI_LOG_TEMPLATE = """# Wiki maintenance log

**Purpose:** Record ingest runs and structural changes to the wiki. **Not** the same as `30_system/04_documentation/context/log.md` (OTA) or `.agent/MEMORY.md`.

---

## Format

`[YYYY-MM-DD] action – brief note (e.g. ingested 00_inbox/raw/foo.md → 20_knowledge/wiki/bar.md)`

---

"""

KARPATHY_AGENT_SPEC_TEMPLATE = """# Knowledge wiki agent spec

**Purpose:** Instructions for the Cursor agent when maintaining this project's Karpathy-style wiki (`knowledge_system/`).

**Human:** Include this file with `@knowledge_system/AGENT_SPEC.md` when asking for ingest or wiki edits.

---

## Role

You maintain a **second brain** layer: structured markdown in `20_knowledge/wiki/` derived from `00_inbox/raw/`, with cross-links. You do **not** replace `.agent/MEMORY.md` or `30_system/04_documentation/context/log.md`; those stay for session and OTA logging.

---

## Environment (Cursor)

The user works in **Cursor**, not a separate knowledge app. Files under `knowledge_system/` are normal project files: Explorer, Quick Open, workspace search, and **`@folder` / `@file`** in Chat/Composer for context. Do not assume a vault or external graph viewer.

---

## Paths

| Path | Role |
|------|------|
| `knowledge_system/00_inbox/raw/` | Incoming unstructured material (notes, transcripts, exports). |
| `knowledge_system/20_knowledge/wiki/` | Curated topic pages and `index.md`. |
| `knowledge_system/20_knowledge/wiki/log.md` | Append-only log of wiki ingest and maintenance. |

---

## Ingest procedure

**When** the user adds a file under `00_inbox/raw/` and asks to ingest (or update the 20_knowledge/wiki):

1. Read the new or updated raw file(s).
2. Identify concepts, entities, people, and recurring themes.
3. For each significant topic: create or update a **single** markdown file under `20_knowledge/wiki/` using short, stable filenames (e.g. `topic-slug.md`). Prefer updating existing pages over duplicating.
4. **Link related pages** with **relative markdown links**: `[label](other-topic.md)` from same directory (or correct relative path). That keeps navigation natural in the IDE. Optional: `[[Other Title]]` as a short see-also if the user likes that convention; still keep `index.md` authoritative.
5. Update **`20_knowledge/wiki/index.md`** so every important page is reachable from the index.
6. Append one line to **`20_knowledge/wiki/log.md`** describing what you ingested and which pages changed.

---

## Conventions

- **Tone:** Clear, factual; separate quoted sources from your synthesis when relevant.
- **Duplicates:** Merge overlapping pages; leave one canonical note and redirect or delete stubs.
- **Sensitive data:** Do not copy secrets or personal identifiers from `00_inbox/raw/` into `20_knowledge/wiki/` unless the user explicitly wants them stored.

---

## Health check (when asked)

- Find broken **relative** links `( ... )` pointing to missing `.md` files.
- Flag orphan pages not linked from `index.md`.
- List orphan `[[...]]` tokens if used and no matching note title/file.
- Suggest index updates for stale structure.

---
"""
