# Auto changelog

Changelog is **automatically** updated on each `git commit` so changes can always be reconstructed.

## What happens

- **Post-commit hook** (`.git/hooks/post-commit`; source: `40_operations/scripts/post-commit-hook.sh`) runs `40_operations/scripts/changelog_auto.py` after each commit. It does **not** run `git commit --amend` inside the hook (that would re-invoke the hook and can recurse indefinitely).
- **Skip the hook** when amending so CHANGELOG does not get a second entry for the amended hash (avoids extra commits or force-push fixes):
  - Git Bash / macOS / Linux:  
    `git add 30_system/docs/CHANGELOG_AUTO.md 30_system/docs/CHANGELOG_AUTO.jsonl`  
    `SKIP_CHANGELOG=1 git commit --amend --no-edit`
  - PowerShell:  
    `git add 30_system/docs/CHANGELOG_AUTO.md 30_system/docs/CHANGELOG_AUTO.jsonl`  
    `$env:SKIP_CHANGELOG = '1'; git commit --amend --no-edit; Remove-Item Env:SKIP_CHANGELOG -ErrorAction SilentlyContinue`
  Set `SKIP_CHANGELOG` to any non-empty value. Then ensure `HEAD` appears in the changelog (run `python 40_operations/scripts/changelog_auto.py` once if needed) before a normal commit, or fold again with the same skip pattern.
- **Pre-commit** does **not** update the changelog (avoids duplicate lines and extra noise).
- Script writes to:
  - **`30_system/docs/CHANGELOG_AUTO.md`** — human-readable log (date, hash, message, files).
  - **`30_system/docs/CHANGELOG_AUTO.jsonl`** — one JSON line per commit (for scripts and search).

## Usage

- **Review changes:** Open `30_system/docs/CHANGELOG_AUTO.md`.
- **Reconstruct:** By date or hash you can see which files changed and the commit message; details with `git show <hash>`.
- **Backfill (first time or after cloning):** Populate changelog for all existing commits:
  ```bash
  python 40_operations/scripts/changelog_auto.py --backfill
  ```
- **Manually log one commit:**
  ```bash
  python 40_operations/scripts/changelog_auto.py           # HEAD
  python 40_operations/scripts/changelog_auto.py HEAD~2    # specific commit
  ```
- **Rebuild markdown order from JSONL** (chronological, dedupe by hash):  
  `python 40_operations/scripts/changelog_auto.py --rewrite-md-from-jsonl`

## Reinstalling the hook

If you clone the repo or lose the hook, copy from the repo scripts:

```bash
cp 40_operations/scripts/post-commit-hook.sh .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

On Windows, Git often uses the same `post-commit` shell script. You can run manually after a commit: `python 40_operations/scripts/changelog_auto.py` (then stage + amend if you need the same fold behavior).

## JSONL format

Each line in `CHANGELOG_AUTO.jsonl`:

```json
{"date": "2026-02-15T12:00:00+01:00", "hash": "abc123...", "short": "abc123", "message": "Message", "files": ["path/a", "path/b"]}
```

Parsing (e.g. Python): `for line in open("30_system/docs/CHANGELOG_AUTO.jsonl"): entry = json.loads(line)`.

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
