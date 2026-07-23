# Brain health check criteria

**Script:** `python 40_operations/scripts/brain_health.py`  
**Exit code:** `0` = PASS, `1` = FAIL

---

## What PASS means

| Check | PASS condition |
|-------|----------------|
| **structure** | `.agent/`, `30_system/context/`, `40_operations/scripts/` exist |
| **30_system/context** | `user.md`, `soul.md`, `memory.md` non-empty (identity context; required) |
| **04_documentation/context (project, warn-only)** | `main.md`, `commit.md`, `log.md` reported as ok or absent; does not fail health check |
| **memory** | `.agent/MEMORY.md` exists; warn if &gt;250 non-empty lines (does not fail) |
| **handoff** | `handoff_log.jsonl` valid JSON per line if present |
| **errors** | No **unpromoted** `critical` or `high` entries in `.cursor/errors/error_log.jsonl`. Promoted learning events (`promoted: true`) do not fail the check. Use `--strict` to fail on any critical/high regardless of promotion. |
| **40_operations/scripts** | `context_sync --summary`, `brain_status`, `memory_trim` exit 0 |
| **error_ops** | `.cursor/scripts/error_ops.py audit` exit 0 |
| **git** | `git status` works in project root |
| **python** | 3.8+ |
| **cursor_skills** | Obsidian wiki junctions under `.cursor/skills/` valid and repo-relative (not OneDrive); via `workspace_bootstrap.py --check-only` |
| **mcp_deps** | warn-only if `fastmcp` missing |

---

## What FAIL does *not* mean

- **Promoted high/critical errors** in `error_log.jsonl` are intentional long-term memory feeding `99_error_memory.mdc`. They are reported as `ok (N entries, M promoted learning events)` in default mode.

---

## Related commands

```powershell
python 40_operations/scripts/brain_status.py    # quick status
python 40_operations/scripts/brain_audit.py     # errors + bridge + status
python 40_operations/scripts/workspace_inventory_audit.py
python 40_operations/scripts/skill_registry.py validate
python -m pytest 40_operations/tests
```

**Strict error mode:**

```powershell
python 40_operations/scripts/brain_health.py --strict
```

---

## Definition of done (brain QA 10/10)

All of:

1. Single effective Tier-0 rule source per session ([CURSOR_RULES_SETUP.md](CURSOR_RULES_SETUP.md))
2. `brain_health.py` → PASS (default, non-strict)
3. `pytest 40_operations/tests` → green (optional markers excluded as documented)
4. `workspace_inventory_audit.py` → PASS
5. `skill_registry.py validate` → no errors
6. Canonical docs agree on tier budgets ([context-optimization.mdc](../../.cursor/rules/context-optimization.mdc))
