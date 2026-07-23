# Cleanup audit — 2026-05-05 (hostname conflict variants)

Historical note: OneDrive sync had created hostname-suffixed duplicate files across the workspace.

## Actions taken (2026-05-05)

- Archived hostname-suffixed variants under `90_archive/` (later removed in 2026-06 hygiene pass)
- Added cleanup tooling: `cleanup_machine_variants.py`, `hostname_conflict_files.py`
- Policy: canonical files only in active paths; conflict copies deleted when hash matches

## Detection

- `python 40_operations/scripts/cleanup_machine_variants.py --dry-run`
- `python 40_operations/scripts/workspace_optimization_check.py` — `hostname_conflict_cleanup` score

## Related

- [CURSOR_RULES_SETUP.md](CURSOR_RULES_SETUP.md)
- [MULTI_PC_WORKSPACE.md](MULTI_PC_WORKSPACE.md)
