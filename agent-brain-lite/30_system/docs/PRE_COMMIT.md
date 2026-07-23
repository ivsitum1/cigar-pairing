# Pre-commit hook

The hook is **installed** in `.git/hooks/pre-commit` (same content as `40_operations/scripts/pre-commit-hook.sh`). If you clone the repo or replace hooks, reinstall using the steps below.

The hook:

1. **Cursor rules** – Ensures every `.cursor/rules/*.mdc` file starts with `---` (frontmatter).
2. **R code** – Warns on `subset()` (prefer `dplyr::filter()`); **fails** on `setwd()` (use `here::here()`); warns on bare `T`/`F` (use `TRUE`/`FALSE`). **Exception:** `40_operations/tests/*` is skipped. Python rubrics in `40_operations/python/quality_validation/rubrics.py` are not scanned by this R-only block.
3. **Manuscript** – Reminds to run an AI detection check when manuscript/paper/draft files are staged.

## Reinstall (Linux / macOS / Git Bash)

From repo root:

```bash
cp 40_operations/scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Install (Windows PowerShell)

Git on Windows often uses bash for hooks. If your `.git/hooks` runs bash:

```powershell
Copy-Item 40_operations/scripts/pre-commit-hook.sh .git/hooks/pre-commit
```

To run the checks manually without installing (PowerShell):

```powershell
.\40_operations/scripts\pre-commit-hook.ps1
```

## Bypass (one-time)

To commit despite a failing hook (use sparingly):

```bash
git commit --no-verify -m "message"
```

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
