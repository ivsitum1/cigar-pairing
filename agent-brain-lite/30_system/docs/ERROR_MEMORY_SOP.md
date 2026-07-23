# Error Memory Maintenance SOP

## When

Once per month (last day of month) or when a category exceeds 10 entries.

## Steps

1. Open `.cursor/rules/99_error_memory.mdc`
2. Each category max **10** entries. If more:
   - Identify oldest or least relevant entries
   - Move them to `90_archive/error_memory_archive.md` with date and category header
3. Update `Last updated` in `99_error_memory.mdc` frontmatter
4. Commit: `chore(rules): monthly error memory rotation`

## Archive format

```markdown
## [YYYY-MM-DD] STATISTICS
- [entry text]
```

## Related

- `.cursor/errors/error_log.jsonl` — full error history (not rotated by this SOP)
- `40_operations/scripts/error_ops.py` — audit and promotion to `99_error_memory`

**Last updated:** 2026-06-28
