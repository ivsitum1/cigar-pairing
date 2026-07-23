# Cursor rules setup (brain vs user-global)

**Purpose:** Avoid duplicate orchestrator and conflicting token budgets when using agent-rules as the shared brain.

**Canonical tier budgets:** `.cursor/rules/context-optimization.mdc` v3.2 (Tier 0 ~3000–3800 tok; composite aim below ~8500 with one skill, ~9500 with two paired skills).

---

## Problem

Cursor can load **two** rule stacks in one session:

| Source | Path | Risk |
|--------|------|------|
| **Workspace** | `agent-rules/.cursor/rules/` (or project symlink) | Intended brain rules (v1.5 orchestrator, context v3.2) |
| **User-global** | `%USERPROFILE%\.cursor\rules\` | Older copies (e.g. context v2.0, total &lt;4700, Tier 3 “one skill”) |

Both may have `alwaysApply: true` on orchestrator, `skills-auto-detect`, `core-principles`, and `context-optimization`. That doubles Tier 0 and creates ambiguous authority.

---

## Recommended setup

### A. Standalone brain (workspace root = agent-rules)

1. Open **`agent rules`** (this repo) as the Cursor workspace root.
2. In **Cursor Settings → Rules**, disable or remove user-global rules that duplicate:
   - `00_orchestrator_agent.mdc`
   - `context-optimization.mdc`
   - `skills-auto-detect.mdc`
   - `core-principles.mdc`
   - `99_error_memory.mdc`
   - `general-rules.mdc`
3. Keep user-global rules only for **personal** preferences that do not overlap the brain (or move them into this repo if they should be versioned).

### B. Project contains brain (recommended for studies)

1. Clone agent-rules into `my-study/agent-rules/`.
2. Run `python agent-rules/40_operations/scripts/project_init.py` (use `--no-symlink` on Windows if needed).
3. Open **`my-study`** as workspace root (not `agent-rules`).
4. Ensure project uses brain rules via symlink or copy:
   - `my-study/.cursor` → `agent-rules/.cursor`
5. Same as (A): disable duplicate user-global rules in Cursor Settings.

### C. Brain as referenced folder only

When another workspace references agent-rules as an extra folder:

- Rules from the **workspace root** apply; brain rules apply only if `.cursor` is symlinked or the folder is the root.
- Do **not** edit files inside agent-rules from that workspace (`agent-rules-readonly-when-referenced.mdc`).
- Put project-specific rules in the **consumer** `.cursor/rules/`.

---

## Verify single effective stack

After setup, a new chat should reflect **one** orchestrator version and context-optimization v3.2 token table. Optional checks:

```powershell
Set-Location "path\to\agent-rules"
python 40_operations/scripts/brain_health.py
python 40_operations/scripts/skill_registry.py validate
```

See [BRAIN_HEALTH_CRITERIA.md](BRAIN_HEALTH_CRITERIA.md) for PASS criteria.

---

## Archiving outdated user-global rules

If you previously copied brain rules to `%USERPROFILE%\.cursor\rules\`:

1. Rename that folder to `.cursor\rules_archive_YYYYMMDD` (backup), **or**
2. Delete only the duplicate `.mdc` files listed above and keep non-brain personal rules.

**Applied on this machine (2026-05-26):** all user-global `.mdc` files moved to `%USERPROFILE%\.cursor\rules_archive_2026-05-26\`; active folder contains only `README.md` pointing to agent-rules.

Template supersession note (optional): `90_archive/imports/user_global_rules_superseded.md`.

---

## Hostname conflict duplicates (OneDrive sync)

OneDrive and multi-PC sync can create conflict copies with hostname suffixes (e.g. `-DESKTOP-ABC123`, or `file-HOST-SEGMENT.ext`). Policy:

- **Never commit** hostname-suffixed files (see root `.gitignore` and `hostname_conflict_files.py`).
- **Active rules** live only in `.cursor/rules/*.mdc` without conflict suffixes.
- **Cleanup:** `python 40_operations/scripts/cleanup_machine_variants.py --dry-run` then `--delete --yes` when hash matches canonical.

---

## Related

- [BRAIN_AND_PROJECT.md](BRAIN_AND_PROJECT.md) – layout and `project_init.py`
- [BRAIN_HEALTH_CRITERIA.md](BRAIN_HEALTH_CRITERIA.md) – health PASS definition
- [.cursor/docs/INDEX.md](../../.cursor/docs/INDEX.md) – router index
