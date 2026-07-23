# Python utilities (40_operations/python)

## quality_validation

Self-assessment and Swiss Cheese pipeline (moved from R so `40_operations/R/` stays statistics-only).

**Import** (from repo root, after adding this folder to `PYTHONPATH`):

```bash
set PYTHONPATH=40_operations/python
python -c "from quality_validation import mandatory_self_assess; print(mandatory_self_assess('hello', domain='writing', max_iterations=1))"
```

Or use the helper script (no `PYTHONPATH`):

```bash
python 40_operations/scripts/run_quality_validation.py assess --text "..." --domain statistics
python 40_operations/scripts/run_quality_validation.py swiss --dry-run
```

See `30_system/docs/CANONICAL_PATHS.md`.

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
