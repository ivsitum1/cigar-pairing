# Rule Maintenance Protocol

## Purpose

Defines how behavior_rules files are updated, versioned, and deprecated.
Without this, the rules system cannot officially evolve.

## Update Authority

- **Propose**: any agent or user can propose a change
- **Review**: proposed changes must be tested in at least 2 eval scenarios before merging
- **Approve**: changes to files 00–05 require explicit user confirmation
- **Merge**: append change summary to `CHANGELOG.md` and bump `VERSION.md`

## Process

1. **Propose**: describe the change and which file(s) it affects
2. **Justify**: cite the specific failure, gap, or contradiction that motivates the change
3. **Test**: run the affected workflow/eval with and without the proposed change
4. **Document**: write a 1-2 sentence CHANGELOG entry
5. **Merge**: apply the change; bump VERSION.md (patch for content edits, minor for new files,
   major for structural overhaul)
6. **Recurring-error eval**: if the change was prompted by a recurring error, also append an eval case via `python 40_operations/scripts/skill_gap_ingest.py append-eval`

When changing `.cursor/rules/*.mdc` or `30_system/behavior_rules/*.md` files, stage `VERSION.md` and `CHANGELOG.md` together (pre-commit hook `version-bump-check` warns if VERSION is missing).

## Adding a New File

- Number sequentially (next after current highest)
- Add to README.md file list with one-sentence description
- Cross-reference from any existing files that overlap in topic
- Rate at 9/10 or document explicitly why it cannot reach 9/10 yet

## Deprecation Protocol

1. Add `[DEPRECATED]` to the file's H1 title
2. Add a note: "Replaced by [filename]. Will be removed in next major version."
3. Keep for one full version cycle
4. Remove in next major version bump; update CHANGELOG.md and README.md

## Version Bumping Rules (VERSION.md)

- **Patch** (e.g., 1.0.0 → 1.0.1): content edits within existing files
- **Minor** (e.g., 1.0.0 → 1.1.0): new file added or file deprecated
- **Major** (e.g., 1.0.0 → 2.0.0): structural changes (numbering, architecture overhaul)

---

**Version:** 1.0  
**Last updated:** 2026-04-10

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
